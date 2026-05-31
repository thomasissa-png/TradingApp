"""Tests validate_symbols + corrections P2 (stamp prix Yahoo→Twelve) +
P4 (composites silencieux).

100% HTTP mocké. Aucun appel réseau réel.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import criteres_calculator as cc  # noqa: E402
import journaliste as jr  # noqa: E402
import market_data as md  # noqa: E402
import validate_symbols as vs  # noqa: E402


# ---------------------------------------------------------------------------
# P3 — validate_symbols
# ---------------------------------------------------------------------------

class TestProbeSymbol:
    def test_no_key_returns_explicit_error(self, monkeypatch):
        monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
        r = vs.probe_symbol("SPY", sleep=0)
        assert r["ok"] is False
        assert "TWELVE_DATA_API_KEY" in (r["error"] or "")

    def test_close_numeric_ok(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")
        monkeypatch.setattr(vs, "http_get_json",
                            lambda *a, **k: {"symbol": "SPY", "close": "543.21"})
        r = vs.probe_symbol("SPY", sleep=0)
        assert r["ok"] is True
        assert r["value"] == pytest.approx(543.21)

    def test_status_error_ko(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")
        monkeypatch.setattr(vs, "http_get_json",
                            lambda *a, **k: {"status": "error", "message": "symbol not found"})
        r = vs.probe_symbol("FOOBAR", sleep=0)
        assert r["ok"] is False
        assert "symbol not found" in (r["error"] or "")

    def test_missing_close_ko(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")
        monkeypatch.setattr(vs, "http_get_json", lambda *a, **k: {"symbol": "FOO"})
        r = vs.probe_symbol("FOO", sleep=0)
        assert r["ok"] is False
        assert "close" in (r["error"] or "")

    def test_close_zero_ko(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")
        monkeypatch.setattr(vs, "http_get_json",
                            lambda *a, **k: {"close": "0"})
        r = vs.probe_symbol("FOO", sleep=0)
        assert r["ok"] is False

    def test_http_dead_ko(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")
        monkeypatch.setattr(vs, "http_get_json", lambda *a, **k: None)
        r = vs.probe_symbol("FOO", sleep=0)
        assert r["ok"] is False
        assert "HTTP" in (r["error"] or "")


class TestValidateAll:
    def test_picks_first_winner(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")

        # Premier candidat KO, second OK → winner = second.
        seq = [
            {"status": "error", "message": "nope"},
            {"close": "100.0"},
            {"close": "200.0"},
        ]
        calls = {"i": 0}

        def fake_http(*a, **k):
            r = seq[calls["i"]]
            calls["i"] += 1
            return r

        monkeypatch.setattr(vs, "http_get_json", fake_http)
        results = vs.validate_all([("G", "Test", ["A", "B", "C"])])
        assert results[0]["winner"] == "B"
        # Les 3 ont été testés (on n'arrête pas au winner)
        assert calls["i"] == 3

    def test_no_winner_when_all_fail(self, monkeypatch):
        monkeypatch.setenv("TWELVE_DATA_API_KEY", "x")
        monkeypatch.setattr(vs, "http_get_json",
                            lambda *a, **k: {"status": "error", "message": "x"})
        results = vs.validate_all([("G", "X", ["A", "B"])])
        assert results[0]["winner"] is None


class TestRender:
    def test_report_mentions_winner_and_failures(self):
        results = [{
            "group": "Indices", "label": "S&P 500", "winner": "SPX",
            "tests": [
                {"symbol": "SPX", "ok": True, "value": 5400.0, "error": None},
                {"symbol": "^GSPC", "ok": False, "value": None, "error": "status=error"},
            ],
        }, {
            "group": "Dollar", "label": "DXY", "winner": None,
            "tests": [
                {"symbol": "DXY", "ok": False, "value": None, "error": "status=error"},
                {"symbol": "UUP", "ok": False, "value": None, "error": "HTTP KO"},
            ],
        }]
        md = vs.render_report(results, now=datetime(2026, 5, 31, tzinfo=timezone.utc))
        assert "S&P 500" in md
        assert "`SPX`" in md
        assert "DXY" in md
        assert "Sans winner" in md
        # Le winner est mis en avant comme code inline
        assert "Indices" in md and "Dollar" in md

    def test_skip_when_no_key(self, monkeypatch, tmp_path):
        monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
        monkeypatch.setattr(vs, "REPORT_OUT", tmp_path / "symbol-validation.md")
        path = vs.run()
        content = path.read_text(encoding="utf-8")
        assert "SKIP" in content
        assert "TWELVE_DATA_API_KEY" in content


# ---------------------------------------------------------------------------
# Post-refacto market_data : la table de vérité Yahoo→Twelve vit maintenant
# dans market_data._TICKER_MAP. YAHOO_TO_TWELVE est un dict passthrough conservé
# pour compat. Les fetchers cc.fetch_twelve_* acceptent des tickers Yahoo.
# ---------------------------------------------------------------------------

class TestTickerMapMarketData:
    def test_market_data_map_contains_critical_tickers(self):
        """Tous les tickers Yahoo des fiches DOIVENT être routables par market_data
        (soit via _TICKER_MAP, soit via blacklist = fallback yfinance)."""
        critical_yahoo_tickers = [
            "GC=F", "SI=F", "HG=F",        # métaux futures
            "BZ=F", "CL=F",                # énergie futures
            "CC=F", "KC=F", "ZW=F",        # softs futures
            "^GSPC", "^IXIC", "^FCHI",     # indices ^prefix → yfinance
            "^VIX", "EUR=X",
        ]
        for t in critical_yahoo_tickers:
            in_map = t in md._TICKER_MAP
            in_blacklist = t in md._td_blacklist
            assert in_map or in_blacklist, (
                f"Ticker {t} absent de _TICKER_MAP ET de _td_blacklist : "
                f"market_data ne saura pas le router"
            )

    def test_map_ticker_translates_yahoo_to_twelve(self):
        """Sanity : _map_ticker fait bien la traduction documentée."""
        # Commodity future → symbole Twelve + type=commodities
        assert md._map_ticker("CL=F") == ("CL1", {"type": "commodities"})
        assert md._map_ticker("BZ=F") == ("CO1", {"type": "commodities"})
        # Forex → format A/B
        assert md._map_ticker("EURUSD=X") == ("EUR/USD", {})
        # Alias raccourci EUR=X (utilisé dans nos fiches)
        assert md._map_ticker("EUR=X") == ("EUR/USD", {})
        # Indices principaux → ETF proxies Twelve (CI compatible, GitHub
        # Actions où yfinance est bloqué par Yahoo). Cf. _TICKER_MAP.
        assert md._map_ticker("^GSPC") == ("SPY", {})
        assert md._map_ticker("^IXIC") == ("QQQ", {})
        assert md._map_ticker("^NDX") == ("QQQ", {})
        assert md._map_ticker("^RUT") == ("IWM", {})
        assert md._map_ticker("^VIX") == ("VIXY", {})
        # CAC 40 : symbole indice direct sur Twelve (FCHI=8183 validé)
        assert md._map_ticker("^FCHI") == ("FCHI", {})
        # Indices sans proxy validé → restent blacklistés (fallback yfinance)
        assert md._map_ticker("^DJI") is None
        assert md._map_ticker("^GDAXI") is None
        assert md._map_ticker("^N225") is None
        # DXY blacklisté → yfinance
        assert md._map_ticker("DX-Y.NYB") is None

    def test_fetch_twelve_price_delegates_to_market_data(self, monkeypatch):
        """fetch_twelve_price(yahoo_ticker) appelle md.fetch_price(yahoo_ticker)
        — qui fait la traduction en interne."""
        captured = {}

        def fake_fetch_price(ticker, **k):
            captured["ticker"] = ticker
            return 75.42

        monkeypatch.setattr(md, "fetch_price", fake_fetch_price)
        price = cc.fetch_twelve_price("BZ=F")
        # Le ticker Yahoo est passé tel quel à market_data (qui fait la
        # traduction Yahoo→Twelve via _TICKER_MAP en interne).
        assert captured["ticker"] == "BZ=F"
        assert price == pytest.approx(75.42)

    def test_stamp_prix_emission_with_yahoo_tickers(self, tmp_path, monkeypatch):
        """stamp_prix_emission alimenté par market_data via fetch_twelve_price :
        tickers Yahoo en entrée → prix réels en sortie (plus de suivi-interrompu
        dû au format)."""
        fiches = {
            "petrole": {"actif": "Brent", "ticker_principal": "BZ=F",
                        "seuils_reussite_pct": {"24h": 1.0}},
            "or": {"actif": "Or", "ticker_principal": "GC=F",
                   "seuils_reussite_pct": {"24h": 0.8}},
        }
        # Mock market_data.fetch_price : retourne un prix par ticker Yahoo
        fake_prices = {"BZ=F": 75.42, "GC=F": 2400.0}

        def fake_md_price(ticker, **k):
            return fake_prices.get(ticker)

        monkeypatch.setattr(md, "fetch_price", fake_md_price)
        # On utilise cc.fetch_twelve_price (par défaut dans stamp_prix_emission)
        # qui délègue à market_data.
        from datetime import date
        out = jr.stamp_prix_emission(
            date(2026, 5, 31), fiches=fiches,
            fetch_price=cc.fetch_twelve_price,
            base_dir=tmp_path,
        )
        import json
        data = json.loads(out.read_text())
        assert "BZ=F" in data
        assert "GC=F" in data
        assert data["BZ=F"] == pytest.approx(75.42)
        assert data["GC=F"] == pytest.approx(2400.0)


# ---------------------------------------------------------------------------
# P4 — composites silencieux
# ---------------------------------------------------------------------------

class TestCompositesP4:
    def test_demande_pv_mining_strikes_skips_propre(self):
        # Avant P4 : retournait {"valeur": 0.0, ...} → faux signal "actif mais nul"
        # Après P4 : retourne None + WARNING dans SKIP_COUNTER
        cc.SKIP_COUNTER.clear()
        res = cc._handle_composite("demande_pv_mining_strikes",
                                   {"cle_courante": "demande_pv_mining_strikes"},
                                   "2026-05-31T00:00:00+00:00")
        assert res is None  # plus de 0.0 silencieux
        # WARNING tracé
        assert any("demande_pv_mining_strikes" in k
                   for k in cc.SKIP_COUNTER) is True

    def test_hf_positioning_warns_partial_when_only_cot(self, monkeypatch):
        # hf_positioning_flux_options : composite COT + put/call. Put/call indispo.
        # On simule un fetch CFTC qui marche → warning "partial" doit être émis.
        cc.SKIP_COUNTER.clear()
        fake_nets = [float(i) for i in range(30)]
        monkeypatch.setattr(cc, "fetch_cftc_managed_money_nets",
                            lambda market, weeks=260: fake_nets)
        res = cc._handle_composite(
            "hf_positioning_flux_options",
            {"cle_courante": "hf_positioning_flux_options", "zscore_div": 2.0, "cap": 1.0},
            "2026-05-31T00:00:00+00:00",
        )
        assert res is not None  # on a quand même un résultat partiel
        assert "valeur_normalisee" in res
        # Mais le warning "partial" est tracé
        partial_keys = [k for k in cc.SKIP_COUNTER
                        if "composite_partial" in k and "hf_positioning" in k]
        assert partial_keys, f"WARNING composite_partial manquant : {dict(cc.SKIP_COUNTER)}"

    def test_hf_positioning_skip_when_cftc_dead(self, monkeypatch):
        cc.SKIP_COUNTER.clear()
        monkeypatch.setattr(cc, "fetch_cftc_managed_money_nets",
                            lambda market, weeks=260: None)
        res = cc._handle_composite(
            "hf_positioning_flux_options",
            {"cle_courante": "hf_positioning_flux_options"},
            "2026-05-31T00:00:00+00:00",
        )
        assert res is None  # skip propre
