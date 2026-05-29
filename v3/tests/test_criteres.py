"""Tests criteres_calculator + triggers_classifier.

Mock 100% des appels HTTP — aucun appel réseau réel.
Vérifie :
- parsing events-log (avec/sans header, ligne invalide ignorée)
- triggers_classifier : match long/short/aucun/fenêtre lookback/calendrier
- fenêtre d'activation (dans/hors → comportement attendu)
- dégradation gracieuse : clé absente → critère omis, pas d'exception
- format de sortie compatible avec scoring_analyste.normalise
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402
import criteres_calculator as cc  # noqa: E402
import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _no_real_http(monkeypatch):
    """Bloque tout appel HTTP réel : si un test oublie de mocker, il échoue clean."""
    def _fail(*a, **kw):
        raise RuntimeError("HTTP réseau interdit dans les tests — mocker http_get_json")
    monkeypatch.setattr(cc, "http_get_json", _fail)


@pytest.fixture
def triggers_cfg():
    return tc.load_triggers_config()


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Parsing events-log
# ---------------------------------------------------------------------------

EVENTS_SAMPLE = """# events-log

| date | l1 | l2 | trigger | cours | source | news_zone |
|---|---|---|---|---|---|---|
| 2026-05-28 | Géopolitique | Iran-Moyen-Orient | frappes Iran sur Ormuz | 85 | Reuters | Global |
| 2026-05-25 | Banques centrales | FOMC | FOMC hawkish | 100 | Reuters | US |
| 2026-05-20 | Politique-FR | France | motion de censure | 7400 | AFP | EU-FR |
| 2026-05-15 | Commodities | OPEC | OPEC cut annoncé | 90 | Bloomberg | Global |
| bad-date | x | x | x | x | x | x |
"""


def test_parse_events_log(tmp_path):
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_SAMPLE, encoding="utf-8")
    events = tc.parse_events_log(p)
    # 4 valides, la ligne bad-date ignorée
    assert len(events) == 4
    # Triés desc
    assert events[0]["_dt"] > events[-1]["_dt"]
    # Champs présents
    assert events[0]["trigger"]


def test_parse_events_log_absent(tmp_path):
    events = tc.parse_events_log(tmp_path / "nope.md")
    assert events == []


# ---------------------------------------------------------------------------
# Classifier triplets
# ---------------------------------------------------------------------------

def _make_event(date_str: str, trigger: str, l2: str = "") -> dict:
    return {
        "date": date_str,
        "l1": "",
        "l2": l2,
        "trigger": trigger,
        "source": "test",
        "news_zone": "Global",
        "_dt": datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc),
    }


def test_classify_long_match(triggers_cfg, now_fixed):
    events = [_make_event("2026-05-28", "frappes Iran sur Ormuz", "Iran")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res.get("petrole", {}).get("geopol_iran") == 1


def test_classify_short_match(triggers_cfg, now_fixed):
    events = [_make_event("2026-05-28", "cessez-le-feu Iran annoncé", "Iran")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res.get("petrole", {}).get("geopol_iran") == -1


def test_classify_no_match(triggers_cfg, now_fixed):
    events = [_make_event("2026-05-28", "marché calme, rien de neuf", "")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    # Tous les triplets doivent valoir 0
    assert res.get("petrole", {}).get("geopol_iran") == 0
    assert res.get("vix", {}).get("tension_geopolitique_active") == 0


def test_classify_lookback_window(triggers_cfg, now_fixed):
    # Event vieux de 60 jours → hors fenêtre 7j de geopol_iran
    old_dt = (now_fixed - timedelta(days=60)).date().isoformat()
    events = [_make_event(old_dt, "frappes Iran", "Iran")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["geopol_iran"] == 0


def test_classify_long_and_short_keeps_most_recent(triggers_cfg, now_fixed):
    events = [
        _make_event("2026-05-28", "cessez-le-feu Iran", "Iran"),   # plus récent: SHORT
        _make_event("2026-05-20", "frappes Iran", "Iran"),         # plus ancien: LONG
    ]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["geopol_iran"] == -1


def test_classify_calendrier_or_diwali():
    # Octobre → LONG (Diwali)
    now = datetime(2026, 10, 15, tzinfo=timezone.utc)
    res = tc.classify_all(events=[], today=now)
    assert res["or"]["demande_indienne_saisonniere"] == 1


def test_classify_calendrier_or_off_season():
    # Mars → SHORT (off-season)
    now = datetime(2026, 3, 15, tzinfo=timezone.utc)
    res = tc.classify_all(events=[], today=now)
    assert res["or"]["demande_indienne_saisonniere"] == -1


def test_classify_calendrier_cafe_cycle():
    # 2025 (impaire) → off cycle → LONG
    now = datetime(2025, 6, 1, tzinfo=timezone.utc)
    res = tc.classify_all(events=[], today=now)
    assert res["cafe"]["cycle_bresil_biannuel"] == 1
    # 2026 (paire) → on cycle → SHORT
    now2 = datetime(2026, 6, 1, tzinfo=timezone.utc)
    res2 = tc.classify_all(events=[], today=now2)
    assert res2["cafe"]["cycle_bresil_biannuel"] == -1


def test_classify_word_boundary(triggers_cfg, now_fixed):
    # "war" en sub-string (warm) ne doit PAS matcher tension_geopolitique de l'or
    events = [_make_event("2026-05-28", "warm weather in Iowa", "")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["or"]["tension_geopolitique"] == 0


def test_classify_empty_events(triggers_cfg, now_fixed):
    res = tc.classify_all(events=[], today=now_fixed, triggers_cfg=triggers_cfg)
    # Tous les triplets = 0 ; calendrier résolu
    for actif, crits in res.items():
        for cle, val in crits.items():
            assert val in (-1, 0, 1)


# ---------------------------------------------------------------------------
# Fenêtres d'activation
# ---------------------------------------------------------------------------

def test_window_eia_in(triggers_cfg):
    # Jeudi 2026-05-28 14h CET → dans fenêtre EIA (mer 16h30 → ven 16h30)
    now = datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc)  # 14h CET (UTC+2 en mai)
    assert cc.is_in_activation_window("eia_crude_surprise", now, triggers_cfg, "petrole") is True


def test_window_eia_out(triggers_cfg):
    # Lundi → hors fenêtre
    now = datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("eia_crude_surprise", now, triggers_cfg, "petrole") is False


def test_window_wasde_in(triggers_cfg):
    # 10 du mois
    now = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("wasde", now, triggers_cfg, "ble") is True


def test_window_wasde_out(triggers_cfg):
    now = datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("wasde", now, triggers_cfg, "ble") is False


def test_window_unknown_returns_none(triggers_cfg):
    now = datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("inexistant_cle", now, triggers_cfg, "x") is None


def test_window_out_emits_zero_normalisee(triggers_cfg, now_fixed):
    """Critère numerique hors fenêtre → valeur_normalisee=0 (contribution 0)."""
    # On simule un critère EIA un lundi (hors fenêtre)
    monday = datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc)
    crit = {"cle_courante": "eia_crude_surprise", "normalisation": "zscore",
            "source": "EIA API", "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, triggers_cfg, [], monday)
    assert val is not None
    assert val["valeur_normalisee"] == 0.0


# ---------------------------------------------------------------------------
# Dégradation gracieuse
# ---------------------------------------------------------------------------

def test_twelve_no_key_skips_gracefully(monkeypatch, triggers_cfg, now_fixed):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    crit = {"cle_courante": "dxy_trend_20j", "normalisation": "zscore",
            "source": "Twelve Data", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, triggers_cfg, [], now_fixed)
    assert val is None  # omis


def test_eia_no_key_skips_gracefully(monkeypatch, triggers_cfg, now_fixed):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    # Mercredi 17h CET → dans fenêtre EIA → on tente le fetch → no key → omis
    wed = datetime(2026, 5, 27, 15, 30, tzinfo=timezone.utc)  # 17h30 CET
    crit = {"cle_courante": "eia_crude_surprise", "normalisation": "zscore",
            "source": "EIA API", "zscore_window": 52, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, triggers_cfg, [], wed)
    assert val is None


def test_unmapped_source_skips(triggers_cfg, now_fixed):
    crit = {"cle_courante": "wgc_demand_index", "normalisation": "zscore",
            "source": "WGC monthly", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("or", crit, {}, triggers_cfg, [], now_fixed)
    assert val is None  # OMIS, pas d'exception


def test_collect_for_fiche_handles_all_missing(triggers_cfg, now_fixed, monkeypatch):
    """Aucune clé API + events-log vide → fiche petrole ne crash pas, retourne au moins triplets+gate."""
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    fiches = cc.load_fiches()
    fiche = fiches["petrole"]
    triplets = tc.classify_all(events=[], today=now_fixed, triggers_cfg=triggers_cfg).get("petrole", {})
    out = cc.collect_for_fiche("petrole", fiche, triplets, triggers_cfg, [], now_fixed)
    # Triplets (geopol + opec) + gate → présents avec valeur=0/false
    assert "tension_geopol_moyen_orient" in out
    assert out["tension_geopol_moyen_orient"]["valeur"] == 0
    assert "opec_production_policy" in out
    assert "gate_evenement_extreme" in out
    # Les critères Twelve/EIA/CFTC sont OMIS (pas dans le dict)
    assert "dxy_trend_20j" not in out


# ---------------------------------------------------------------------------
# Compatibilité avec scoring_analyste.normalise
# ---------------------------------------------------------------------------

def test_output_compatible_scoring_triplet():
    """Une valeur triplet {valeur: -1/0/+1} doit être normalisée correctement par sa."""
    crit = {"normalisation": "triplet", "cap": 1.0}
    v, _ = sa.normalise(crit, {"valeur": 1, "ts": "x"})
    assert v == 1.0
    v, _ = sa.normalise(crit, {"valeur": -1, "ts": "x"})
    assert v == -1.0
    v, _ = sa.normalise(crit, {"valeur": 0, "ts": "x"})
    assert v == 0.0


def test_output_compatible_scoring_zscore_precalc():
    """valeur_normalisee pré-calculée doit passer telle quelle (capée)."""
    crit = {"normalisation": "zscore", "cap": 1.0, "zscore_div": 2}
    v, note = sa.normalise(crit, {"valeur": 100, "valeur_normalisee": 0.5, "ts": "x"})
    assert v == 0.5
    # Cap doit s'appliquer
    v2, _ = sa.normalise(crit, {"valeur": 999, "valeur_normalisee": 5.0, "ts": "x"})
    assert v2 == 1.0


def test_output_compatible_scoring_lineaire():
    """valeur brute lineaire → scoring applique centre/echelle."""
    crit = {"normalisation": "lineaire", "centre": 50.0, "echelle": 1.0, "cap": 1.0}
    v, _ = sa.normalise(crit, {"valeur": 51.0, "ts": "x"})
    assert v == 1.0  # (51-50)/1 = 1, capé


def test_output_compatible_scoring_gate():
    """gate avec valeur:bool → ne contribue pas (None) mais ne lève pas."""
    crit = {"normalisation": "gate", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": True, "ts": "x"})
    assert v is None
    assert "GATE" in note


# ---------------------------------------------------------------------------
# Fetch helpers mockés (sanity)
# ---------------------------------------------------------------------------

def test_fetch_twelve_series_no_key(monkeypatch):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    assert cc.fetch_twelve_series("DXY") is None


def test_fetch_twelve_series_with_mock(monkeypatch):
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    fake = {
        "status": "ok",
        "values": [
            {"datetime": "2026-05-25", "close": "100.0"},
            {"datetime": "2026-05-26", "close": "101.0"},
            {"datetime": "2026-05-27", "close": "102.0"},
        ],
    }
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, timeout=15: fake)
    series = cc.fetch_twelve_series("DXY", outputsize=3)
    assert series is not None
    assert len(series) == 3
    assert series[-1][1] == 102.0


def test_fetch_cftc_with_mock(monkeypatch):
    fake = [
        {"report_date_as_yyyy_mm_dd": "2026-05-21T00:00:00", "m_money_positions_long_all": "100", "m_money_positions_short_all": "50"},
        {"report_date_as_yyyy_mm_dd": "2026-05-14T00:00:00", "m_money_positions_long_all": "120", "m_money_positions_short_all": "60"},
    ]
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, timeout=15: fake)
    nets = cc.fetch_cftc_managed_money_nets("CRUDE OIL, LIGHT SWEET-WTI - NEW YORK MERCANTILE EXCHANGE")
    assert nets == [60.0, 50.0]  # oldest→newest


def test_compute_zscore_cap():
    # Historique constant → std=0 → None
    assert cc.compute_zscore_normalisee(10, [5, 5, 5, 5], zscore_div=2, cap=1) is None
    # Valeur extrême → cap appliqué
    hist = [0.0, 1.0, 2.0, 3.0, 4.0]
    z = cc.compute_zscore_normalisee(100, hist, zscore_div=2, cap=1.0)
    assert z == 1.0


# ---------------------------------------------------------------------------
# Intégration : run complet sans clés
# ---------------------------------------------------------------------------

def test_run_complete_no_keys_no_crash(monkeypatch, tmp_path):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    # Rediriger l'output vers tmp_path
    monkeypatch.setattr(cc, "CRITERES_OUT", tmp_path / "criteres-courants.md")
    out = cc.run(now=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc))
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "last_update" in text
    # Au moins les gates + triplets sont présents pour chaque fiche
    assert "petrole" in text or "petrole:" in text
