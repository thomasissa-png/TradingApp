"""Tests — or/argent/Brent servis par le symbole Twelve natif + provenance.

Mission 2026-06-16 (présentation/source, pas de scoring) :
- Twelve devient la source UNIQUE de l'or/argent/Brent via leurs symboles spot
  natifs XAU/USD, XAG/USD, XBR/USD (les futures Yahoo GC=F/SI=F/BZ=F renvoient
  404 sur Twelve /time_series → fallback yfinance silencieux jusqu'ici).
- Le mapping s'applique au PRIX (fetch_price) ET à l'HISTORIQUE (fetch_history).
- Le ticker_principal des fiches reste GC=F/SI=F/BZ=F (identifiant interne stable, L023).
- La provenance réellement utilisée est loggée par symbole (twelve_native /
  yfinance_fallback / stooq_fallback).
- Cuivre/cacao/café/blé NE sont PAS remappés (Twelve ne sert pas ces futures au
  bon niveau → yfinance conservé, zéro invention).
- Cutover : ref-changed.json contient GC=F/SI=F/BZ=F au 2026-06-16.

ZÉRO réseau : tous les appels Twelve/yfinance sont mockés.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import market_data as md  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Mapping : GC=F→XAU/USD, SI=F→XAG/USD, BZ=F→XBR/USD (table de vérité)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "yf_ticker,expected_symbol",
    [
        ("GC=F", "XAU/USD"),
        ("SI=F", "XAG/USD"),
        ("BZ=F", "XBR/USD"),
    ],
)
def test_map_ticker_native_spot(yf_ticker, expected_symbol):
    mapping = md._map_ticker(yf_ticker)
    assert mapping is not None, f"{yf_ticker} doit être mappé (pas de fallback yfinance)"
    td_sym, extra = mapping
    assert td_sym == expected_symbol
    # Symbole spot forex-style : aucun type=commodities (sinon collision/404).
    assert "type" not in extra


def test_brent_no_longer_commodity_future():
    """BZ=F ne doit plus pointer vers CO1 type=commodities (qui renvoyait 404)."""
    td_sym, extra = md._map_ticker("BZ=F")
    assert td_sym != "CO1"
    assert extra.get("type") != "commodities"


# ---------------------------------------------------------------------------
# 2. Le symbole NATIF est bien celui INTERROGÉ chez Twelve (price ET history)
# ---------------------------------------------------------------------------

@pytest.fixture
def captured_symbols(monkeypatch):
    """Capture le `symbol` envoyé à Twelve via _td_request, sans réseau."""
    seen = []

    def fake_td_request(endpoint, params, yf_ticker=None):
        seen.append((endpoint, params.get("symbol")))
        return None  # force le retour à None (pas de df), on ne teste que le symbole

    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    monkeypatch.setattr(md, "_td_request", fake_td_request)
    # Coupe le fallback yfinance pour ne pas appeler le réseau.
    monkeypatch.setattr(md, "_yf_history", lambda *a, **k: None)
    md._cache.clear()
    return seen


@pytest.mark.parametrize(
    "yf_ticker,expected_symbol",
    [("GC=F", "XAU/USD"), ("SI=F", "XAG/USD"), ("BZ=F", "XBR/USD")],
)
def test_fetch_history_queries_native_symbol(captured_symbols, yf_ticker, expected_symbol):
    md.fetch_history(yf_ticker, period_days=25, interval="1day")
    assert ("time_series", expected_symbol) in captured_symbols


@pytest.mark.parametrize(
    "yf_ticker,expected_symbol",
    [("GC=F", "XAU/USD"), ("SI=F", "XAG/USD"), ("BZ=F", "XBR/USD")],
)
def test_fetch_price_queries_native_symbol(monkeypatch, yf_ticker, expected_symbol):
    seen = []

    def fake_td_request(endpoint, params, yf_ticker=None):
        seen.append((endpoint, params.get("symbol")))
        return None

    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    monkeypatch.setattr(md, "_td_request", fake_td_request)
    # Empêche les fallbacks (yfinance + fetch_quote) d'appeler le réseau.
    monkeypatch.setattr(md, "fetch_quote", lambda *a, **k: None)
    import builtins
    real_import = builtins.__import__

    def no_yf(name, *a, **k):
        if name == "yfinance":
            raise ImportError("yfinance désactivé en test")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", no_yf)
    md._cache.clear()
    md.fetch_price(yf_ticker, bypass_cache=True)
    assert ("price", expected_symbol) in seen


# ---------------------------------------------------------------------------
# 3. ticker_principal des fiches INCHANGÉ (L023) — reste GC=F/SI=F/BZ=F
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "fiche_file,expected_ticker",
    [("or.yml", "GC=F"), ("argent.yml", "SI=F"), ("petrole.yml", "BZ=F")],
)
def test_ticker_principal_unchanged(fiche_file, expected_ticker):
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load((ROOT / "config" / "fiches" / fiche_file).read_text(encoding="utf-8"))
    assert data["ticker_principal"] == expected_ticker


# ---------------------------------------------------------------------------
# 4. Provenance loggée : twelve_native quand Twelve répond, yfinance sinon
# ---------------------------------------------------------------------------

def test_provenance_twelve_native_on_price(monkeypatch):
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    monkeypatch.setattr(md, "_td_request", lambda e, p, yf_ticker=None: {"price": "4326.0"})
    md._cache.clear()
    md.clear_provenance()
    price = md.fetch_price("GC=F", bypass_cache=True)
    assert price == 4326.0
    assert md.get_provenance().get("GC=F") == "twelve_native"


def test_provenance_yfinance_fallback_on_price(monkeypatch):
    """Si Twelve ne répond pas (None) mais yfinance oui → yfinance_fallback."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    monkeypatch.setattr(md, "_td_request", lambda e, p, yf_ticker=None: None)

    class _FastInfo:
        def get(self, k, default=None):
            return {"lastPrice": 50.0}.get(k, default)

    class _FakeYfTicker:
        fast_info = _FastInfo()

    fake_yf_module = type("yf", (), {"Ticker": staticmethod(lambda t: _FakeYfTicker())})

    import builtins
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "yfinance":
            return fake_yf_module
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    md._cache.clear()
    md.clear_provenance()
    price = md.fetch_price("HG=F", bypass_cache=True)
    assert price == 50.0
    assert md.get_provenance().get("HG=F") == "yfinance_fallback"


def test_clear_provenance_resets():
    md.record_provenance("GC=F", "twelve_native")
    assert md.get_provenance().get("GC=F") == "twelve_native"
    md.clear_provenance()
    assert md.get_provenance() == {}


def test_stooq_fallback_provenance_recorded(monkeypatch):
    """criteres_calculator enregistre stooq_fallback quand Stooq sert la série."""
    import criteres_calculator as cc

    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    # Twelve/market_data KO → série vide.
    monkeypatch.setattr(md, "fetch_history", lambda ticker, **k: None)
    # Stooq renvoie une série exploitable.
    fake_series = [
        (__import__("datetime").datetime(2026, 6, 1, tzinfo=__import__("datetime").timezone.utc), 100.0),
        (__import__("datetime").datetime(2026, 6, 2, tzinfo=__import__("datetime").timezone.utc), 101.0),
    ]
    monkeypatch.setattr(cc, "fetch_stooq_series", lambda symbol, outputsize=60: fake_series)
    md.clear_provenance()
    out = cc.fetch_twelve_series("HG=F", interval="1day", outputsize=60)
    assert out is not None
    assert md.get_provenance().get("HG=F") == "stooq_fallback"


# ---------------------------------------------------------------------------
# 5. Cuivre/cacao/café/blé : NON remappés (futures conservés, yfinance documenté)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "yf_ticker,not_native",
    [
        ("HG=F", "XCU/USD"),
        ("CC=F", "COCOA"),
        ("KC=F", "COFFEE"),
        ("ZW=F", "WHEAT"),
    ],
)
def test_commodities_not_remapped_to_spot(yf_ticker, not_native):
    """Pas de symbole spot natif fabriqué pour les futures non servis par Twelve."""
    mapping = md._map_ticker(yf_ticker)
    assert mapping is not None
    td_sym, _ = mapping
    assert td_sym != not_native, f"{yf_ticker} ne doit PAS être mappé vers {not_native} (zéro invention)"


# ---------------------------------------------------------------------------
# 6. Cutover : ref-changed.json contient GC=F/SI=F/BZ=F au 2026-06-16
# ---------------------------------------------------------------------------

def _ref_changed():
    return json.loads((ROOT / "data" / "ref-changed.json").read_text(encoding="utf-8"))["ref_changed"]


@pytest.mark.parametrize("ticker", ["GC=F", "SI=F", "BZ=F"])
def test_cutover_native_tickers_2026_06_16(ticker):
    entry = _ref_changed()[ticker]
    assert entry["ref_changed"] == "2026-06-16"
    motif = entry["motif"].lower()
    assert "twelve natif" in motif or "twelve nativ" in motif


@pytest.mark.parametrize("ticker", ["CC=F", "KC=F", "ZW=F", "HG=F"])
def test_cutover_commodities_unchanged(ticker):
    """Cuivre/cacao/café/blé gardent leur date de reset précédente (2026-06-15)."""
    assert _ref_changed()[ticker]["ref_changed"] == "2026-06-15"
