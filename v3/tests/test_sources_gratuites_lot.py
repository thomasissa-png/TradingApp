"""Tests — lot « sources gratuites » + fallback Stooq + raccord gate FOMC.

Live-validés (2026-06-10) puis MOCKÉS ici : AUCUN appel réseau réel.

Couvre :
  1. Raccord gate ⚑ : calendrier_eco.evenement_majeur_imminent OR-é dans
     _resolve_gate (FOMC J0 → drapeau actif, déterministe, même sans news).
  2. Eurostat balance commerciale EZ (sans clé) : JSON-stat synthétique → valeur ;
     vide/erreur → None (n/a propre).
  3. Fallback Stooq (résilience SÉRIES) : Twelve None → série Stooq ; jamais pour
     les stamps de mesure (test négatif : md.fetch_price n'est pas touché) ;
     hors mapping → pas de fallback ; CSV HTML/404 → None.
  4. Sources écartées (USDA WASDE, Crop Progress, WGC, ICE arabica, AAII) :
     RIEN de câblé — ces clés restent n/a (pas de test fantôme, on vérifie
     juste qu'aucun handler dédié n'existe).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import calendrier_eco as cal  # noqa: E402
import criteres_calculator as cc  # noqa: E402
import market_data as md  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_http(monkeypatch):
    """Bloque tout réseau réel : un test qui oublie de mocker échoue clean."""
    def _fail(*a, **kw):  # noqa: ANN001
        raise RuntimeError("HTTP réseau interdit — mocker la fonction de fetch")

    monkeypatch.setattr(cc, "http_get_json", _fail)
    monkeypatch.setattr(cc, "http_get_text", _fail)
    monkeypatch.setattr(md, "fetch_history", _fail)
    monkeypatch.setattr(md, "fetch_price", _fail)


# ---------------------------------------------------------------------------
# 1) Raccord gate ⚑ FOMC déterministe
# ---------------------------------------------------------------------------

def test_fomc_imminent_deterministe_true(monkeypatch):
    """calendrier_eco signale un FOMC imminent concernant l'actif → helper True (asset-aware)."""
    monkeypatch.setattr(cal, "actifs_majeurs_imminents", lambda *a, **k: {"sp500", "or"})
    now = datetime(2026, 6, 17, 10, 0, tzinfo=timezone.utc)
    # Concerné par le FOMC → True ; non concerné (cacao) → False (spécificité actif).
    assert cc._fomc_imminent_deterministe(now, "sp500") is True
    assert cc._fomc_imminent_deterministe(now, "cacao") is False


def test_fomc_imminent_deterministe_tolere_module_ko(monkeypatch):
    """Si calendrier_eco lève une exception → helper retombe sur False (comportement actuel)."""
    def _boom(*a, **k):  # noqa: ANN001
        raise RuntimeError("module KO")
    monkeypatch.setattr(cal, "actifs_majeurs_imminents", _boom)
    now = datetime(2026, 6, 17, 10, 0, tzinfo=timezone.utc)
    assert cc._fomc_imminent_deterministe(now, "sp500") is False


def test_resolve_gate_active_par_fomc_sans_news(monkeypatch):
    """FOMC J0 (source déterministe) → gate True même avec events vide (zéro news)."""
    monkeypatch.setattr(cal, "evenement_majeur_imminent", lambda *a, **k: True)
    now = datetime(2026, 6, 17, 10, 0, tzinfo=timezone.utc)
    # Aucune news, n'importe quel actif → le gate s'allume par la source FOMC.
    assert cc._resolve_gate("sp500", "gate_regime_extreme", now, []) is True
    assert cc._resolve_gate("eurusd", "gate_regime_extreme", now, []) is True


def test_resolve_gate_inactif_hors_fomc_sans_news(monkeypatch):
    """Pas de FOMC + pas de news → gate False (comportement actuel préservé)."""
    monkeypatch.setattr(cal, "evenement_majeur_imminent", lambda *a, **k: False)
    now = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    assert cc._resolve_gate("sp500", "gate_regime_extreme", now, []) is False


def test_gate_est_flag_hors_score():
    """Garde-fou : le critère gate est bien un FLAG (normalisation 'gate'),
    pas un critère noté → l'OR FOMC n'injecte aucun poids dans le score."""
    import yaml
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "sp500.yml").read_text(encoding="utf-8"))
    gates = [c for c in fiche["criteres"] if c.get("normalisation") == "gate"]
    assert gates, "sp500 doit avoir un critère gate"
    assert gates[0]["cle_courante"] == "gate_regime_extreme"


# ---------------------------------------------------------------------------
# 2) Eurostat — balance commerciale zone euro
# ---------------------------------------------------------------------------

def _eurostat_jsonstat(values_by_period):
    """Construit un JSON-stat Eurostat mono-série minimal (comme la réponse live)."""
    periods = sorted(values_by_period)
    time_index = {p: i for i, p in enumerate(periods)}
    value = {str(i): values_by_period[p] for p, i in time_index.items()}
    return {
        "dimension": {"time": {"category": {"index": time_index}}},
        "value": value,
    }


def test_eurostat_parse_jsonstat():
    obj = _eurostat_jsonstat({"2026-01": -2407.1, "2026-02": 11123.6, "2026-03": 7820.6})
    parsed = cc._parse_eurostat_jsonstat(obj)
    assert parsed == [("2026-01", -2407.1), ("2026-02", 11123.6), ("2026-03", 7820.6)]


def test_eurostat_handler_synthetique_to_value(monkeypatch):
    # 18 points mensuels plausibles (calqués sur la série live EA21).
    series = [5843.0, 14202.7, 13009.2, -1822.3, 23127.6, 34118.3, 8815.6, 15434.1,
              5921.9, 11987.9, -31.6, 14944.9, 16570.4, 7011.8, 11363.8, -2407.1,
              11123.6, 7820.6]
    obj = _eurostat_jsonstat({f"2024-{i:02d}" if i <= 12 else f"2025-{i-12:02d}": v
                              for i, v in enumerate(series, start=1)})
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, **k: obj)
    crit = {"normalisation": "zscore", "zscore_window": 12, "zscore_div": 2, "cap": 1.0}
    res = cc._handle_eurostat_trade_balance("balance_commerciale_ez", crit, "2026-06-10T00:00:00")
    assert res is not None
    assert res["valeur"] == series[-1]
    assert "valeur_normalisee" in res and -1.0 <= res["valeur_normalisee"] <= 1.0


def test_eurostat_handler_vide_to_none(monkeypatch):
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, **k: {"value": {}})
    crit = {"normalisation": "zscore", "zscore_window": 12, "zscore_div": 2, "cap": 1.0}
    assert cc._handle_eurostat_trade_balance("balance_commerciale_ez", crit, "t") is None


def test_eurostat_handler_reseau_ko_to_none(monkeypatch):
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, **k: None)
    crit = {"normalisation": "zscore", "zscore_window": 12, "zscore_div": 2, "cap": 1.0}
    assert cc._handle_eurostat_trade_balance("balance_commerciale_ez", crit, "t") is None


def test_eurostat_cle_courante_existe_dans_fiche():
    """La cle_courante câblée doit correspondre EXACTEMENT à la fiche eurusd."""
    import yaml
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "eurusd.yml").read_text(encoding="utf-8"))
    cles = {c.get("cle_courante") for c in fiche["criteres"]}
    assert "balance_commerciale_ez" in cles


# ---------------------------------------------------------------------------
# 3) Fallback Stooq — SÉRIES uniquement
# ---------------------------------------------------------------------------

STOOQ_CSV_OK = (
    "Date,Open,High,Low,Close,Volume\n"
    "2026-06-01,500.0,502.0,498.0,501.5,1000000\n"
    "2026-06-02,501.5,505.0,500.0,504.0,1200000\n"
    "2026-06-03,504.0,506.0,503.0,505.5,900000\n"
)


def test_stooq_parse_csv_ok():
    series = cc._parse_stooq_csv(STOOQ_CSV_OK)
    assert series is not None and len(series) == 3
    assert series[0][1] == 501.5 and series[-1][1] == 505.5
    # oldest → newest
    assert series[0][0] < series[-1][0]


def test_stooq_parse_html_404_to_none():
    assert cc._parse_stooq_csv("<!DOCTYPE html><title>Stooq</title><p>404") is None


def test_stooq_parse_vide_to_none():
    assert cc._parse_stooq_csv("") is None
    assert cc._parse_stooq_csv("Date,Open,High,Low,Close,Volume\n") is None


def test_stooq_fetch_symbole_mappe(monkeypatch):
    monkeypatch.setattr(cc, "http_get_text", lambda url, **k: STOOQ_CSV_OK)
    series = cc.fetch_stooq_series("SPY", outputsize=60)
    assert series is not None and len(series) == 3


def test_stooq_fetch_hors_mapping_pas_de_fallback(monkeypatch):
    # Un ticker non mappé ne doit JAMAIS déclencher de requête HTTP (None direct).
    called = {"http": False}

    def _spy(url, **k):  # noqa: ANN001
        called["http"] = True
        return STOOQ_CSV_OK
    monkeypatch.setattr(cc, "http_get_text", _spy)
    assert cc.fetch_stooq_series("CL=F", outputsize=60) is None
    assert called["http"] is False


def test_stooq_fetch_csv_404_to_none(monkeypatch):
    monkeypatch.setattr(cc, "http_get_text", lambda url, **k: "<html>404</html>")
    assert cc.fetch_stooq_series("SPY") is None


def test_fetch_twelve_series_fallback_stooq_quand_twelve_vide(monkeypatch):
    """Twelve (market_data) None → fallback Stooq sert la série (mappé, daily)."""
    cc.SKIP_COUNTER.clear()
    monkeypatch.setattr(cc, "_twelve_key", lambda: "fake-key")
    monkeypatch.setattr(md, "fetch_history", lambda *a, **k: None)  # Twelve KO
    monkeypatch.setattr(cc, "http_get_text", lambda url, **k: STOOQ_CSV_OK)
    series = cc.fetch_twelve_series("SPY", interval="1day", outputsize=60)
    assert series is not None and len(series) == 3
    # Traçabilité : le fallback est marqué dans SKIP_COUNTER.
    assert cc.SKIP_COUNTER.get("twelve_fallback_stooq:SPY", 0) == 1


def test_fetch_twelve_series_pas_de_fallback_si_twelve_ok(monkeypatch):
    """Si Twelve répond, Stooq n'est JAMAIS appelé (pas de mélange de sources)."""
    cc.SKIP_COUNTER.clear()

    class _FakeDF:
        def __init__(self, closes):
            self.index = [datetime(2026, 6, d, tzinfo=timezone.utc) for d in range(1, len(closes) + 1)]
            self._closes = closes

        def __len__(self):
            return len(self._closes)

        def __getitem__(self, key):
            assert key == "Close"
            return self._closes

    monkeypatch.setattr(cc, "_twelve_key", lambda: "fake-key")
    monkeypatch.setattr(md, "fetch_history", lambda *a, **k: _FakeDF([500.0, 501.0, 502.0]))

    def _stooq_should_not_be_called(url, **k):  # noqa: ANN001
        raise AssertionError("Stooq ne doit PAS être appelé quand Twelve répond")
    monkeypatch.setattr(cc, "http_get_text", _stooq_should_not_be_called)

    series = cc.fetch_twelve_series("SPY", interval="1day", outputsize=60)
    assert series is not None and len(series) == 3
    assert cc.SKIP_COUNTER.get("twelve_fallback_stooq:SPY", 0) == 0


def test_fetch_twelve_series_pas_de_fallback_intraday(monkeypatch):
    """Stooq ne sert que du daily : un intervalle intraday ne déclenche pas le fallback."""
    cc.SKIP_COUNTER.clear()
    monkeypatch.setattr(cc, "_twelve_key", lambda: "fake-key")
    monkeypatch.setattr(md, "fetch_history", lambda *a, **k: None)

    def _stooq(url, **k):  # noqa: ANN001
        raise AssertionError("pas de fallback Stooq en intraday")
    monkeypatch.setattr(cc, "http_get_text", _stooq)
    assert cc.fetch_twelve_series("SPY", interval="1h", outputsize=60) is None


def test_stamps_de_mesure_ne_passent_pas_par_stooq(monkeypatch):
    """NÉGATIF (intégrité prédiction→mesure) : les stamps utilisent md.fetch_price,
    JAMAIS le fallback Stooq de criteres_calculator. On le prouve en vérifiant que
    mesure_ouverture appelle bien md.fetch_price (pas cc.fetch_twelve_series/Stooq)."""
    import inspect
    import mesure_ouverture as mo
    src = inspect.getsource(mo)
    # Le module de stamp s'appuie sur market_data.fetch_price (Twelve-only)...
    assert "fetch_price" in src
    # ...et ne référence ni le fallback Stooq ni fetch_twelve_series.
    assert "fetch_stooq_series" not in src
    assert "STOOQ" not in src.upper()


# ---------------------------------------------------------------------------
# 4) Sources ÉCARTÉES — aucun câblage (pas de test fantôme)
# ---------------------------------------------------------------------------

# [03/07] usda_wasde_stocks_to_use RETIRÉ de cette liste : handler NASS
# QuickStats câblé (clé USDA_API_KEY posée par le fondateur le 01/07, GO),
# cf. test_usda_nass_stocks.py. Les autres restent écartées (zéro invention).
@pytest.mark.parametrize("cle", [
    "nass_crop_progress",                # Blé — Crop Progress (clé)
    "achats_pboc_cb_emergentes",         # Or — WGC banques centrales (HTML only)
    "stocks_ice_arabica_certifies_20j",  # Café — ICE arabica (HTML/PDF)
    "aaii_bull_bear",                    # S&P — AAII (403)
])
def test_sources_ecartees_restent_unmapped(cle, monkeypatch):
    """Ces critères restent n/a : aucun handler dédié, le dispatch tombe en
    zscore_unmapped (None). On NE simule PAS de réseau (sources non câblées)."""
    cc.SKIP_COUNTER.clear()
    crit = {"cle_courante": cle, "normalisation": "zscore",
            "zscore_window": 12, "zscore_div": 2, "cap": 1.0,
            "source": "n/a"}
    # is_in_activation_window peut consulter la config triggers ; pas de réseau.
    res = cc.build_critere_value("test", crit, {}, {}, [], datetime(2026, 6, 10, tzinfo=timezone.utc))
    assert res is None
    assert any(k.startswith("zscore_unmapped") for k in cc.SKIP_COUNTER)


def test_pas_de_handler_dedie_pour_sources_ecartees():
    """Garde-fou anti-régression : aucun handler/constante n'a été câblé par erreur
    pour les sources écartées (WASDE, Crop Progress, WGC, ICE, AAII)."""
    assert not hasattr(cc, "fetch_usda_wasde")
    assert not hasattr(cc, "fetch_wgc_central_banks")
    assert not hasattr(cc, "fetch_ice_arabica")
    assert not hasattr(cc, "fetch_aaii_sentiment")
