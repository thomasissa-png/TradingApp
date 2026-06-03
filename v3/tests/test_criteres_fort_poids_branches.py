"""Tests des critères à fort poids nouvellement branchés (Session 3).

Branche 5 critères dont la source (Twelve Data / FRED) était intégrée mais pas
câblée dans le dispatch de criteres_calculator :

  - dxy_trend_20j          → FRED DTWEXBGS (USD Index broad)         [BRANCHÉ]
  - taux_10y_us_delta_5j   → FRED DGS10, z-score du delta 5j          [BRANCHÉ]
  - spread_oat_bund_10y    → FRED FR(IRLTLT01FRM156N) − DE(...DEM)    [BRANCHÉ]
  - differentiel_taux_2y_us_de → n/a propre (pas de German 2Y gratuit) [TIER 2]
  - v2x_regime             → n/a propre (VSTOXX indispo Twelve free)   [TIER 2]

Règle : AUCUN appel réseau réel. Tout fetch est mocké. On vérifie pour chaque
critère branché : fetch simulé → valeur_normalisee correcte ; fetch absent → n/a
propre (None, jamais de valeur inventée).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import criteres_calculator as cc  # noqa: E402
import market_data as md  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_http(monkeypatch):
    """Bloque tout HTTP réel : un test qui oublie de mocker échoue proprement."""
    def _fail(*a, **kw):
        raise RuntimeError("HTTP réseau interdit dans les tests")

    monkeypatch.setattr(cc, "http_get_json", _fail)
    monkeypatch.setattr(cc, "_fred_get_json", _fail)
    monkeypatch.setattr(md, "fetch_history", _fail)
    monkeypatch.setattr(md, "fetch_price", _fail)


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# 1) dxy_trend_20j — FRED DTWEXBGS, z-score simple
# ---------------------------------------------------------------------------

def _dxy_crit() -> dict:
    return {"cle_courante": "dxy_trend_20j", "normalisation": "zscore",
            "source": "Twelve Data", "zscore_window": 60, "zscore_div": 2,
            "cap": 1.0, "signe": -1}


def test_dxy_trend_20j_branche_fred(monkeypatch, now_fixed):
    """Série DTWEXBGS croissante (dollar qui monte) → dernière valeur z>0."""
    serie = [100.0 + i * 0.2 for i in range(70)]
    monkeypatch.setattr(cc, "fetch_fred_series",
                        lambda sid, n=252: serie if sid == "DTWEXBGS" else None)
    val = cc.build_critere_value("sp500", _dxy_crit(), {}, {}, [], now_fixed)
    assert val is not None, "DXY doit être branché sur FRED DTWEXBGS"
    assert "valeur_normalisee" in val
    assert val["valeur_normalisee"] > 0  # série croissante → dernier point > moyenne
    assert val["valeur"] == pytest.approx(serie[-1])


def test_dxy_trend_20j_fetch_absent_na_propre(monkeypatch, now_fixed):
    """FRED indisponible (None) → critère n/a propre (pas de valeur inventée)."""
    monkeypatch.setattr(cc, "fetch_fred_series", lambda sid, n=252: None)
    val = cc.build_critere_value("sp500", _dxy_crit(), {}, {}, [], now_fixed)
    assert val is None


# ---------------------------------------------------------------------------
# 2) taux_10y_us_delta_5j — FRED DGS10, z-score du delta 5 jours
# ---------------------------------------------------------------------------

def _delta_crit() -> dict:
    return {"cle_courante": "taux_10y_us_delta_5j", "normalisation": "zscore",
            "source": "Twelve Data", "zscore_window": 60, "zscore_div": 2,
            "cap": 1.0, "signe": -1}


def test_taux_10y_delta_5j_branche_fred(monkeypatch, now_fixed):
    """DGS10 stable puis bond récent → delta 5j final élevé vs sa distribution → z>0."""
    serie = [4.00 + 0.001 * i for i in range(65)] + [4.10, 4.20, 4.32, 4.45, 4.60]
    monkeypatch.setattr(cc, "fetch_fred_series",
                        lambda sid, n=252: serie if sid == "DGS10" else None)
    val = cc.build_critere_value("sp500", _delta_crit(), {}, {}, [], now_fixed)
    assert val is not None, "taux_10y_us_delta_5j doit être branché sur FRED DGS10"
    assert "valeur_normalisee" in val
    assert val["valeur_normalisee"] > 0  # delta 5j final >> deltas historiques
    assert val["valeur"] == pytest.approx(serie[-1] - serie[-6])


def test_taux_10y_delta_5j_serie_courte_na(monkeypatch, now_fixed):
    """Série trop courte pour calculer la fenêtre de deltas → n/a propre."""
    monkeypatch.setattr(cc, "fetch_fred_series", lambda sid, n=252: [4.0, 4.1, 4.2])
    val = cc.build_critere_value("sp500", _delta_crit(), {}, {}, [], now_fixed)
    assert val is None


def test_taux_10y_delta_5j_fetch_absent_na(monkeypatch, now_fixed):
    monkeypatch.setattr(cc, "fetch_fred_series", lambda sid, n=252: None)
    val = cc.build_critere_value("sp500", _delta_crit(), {}, {}, [], now_fixed)
    assert val is None


# ---------------------------------------------------------------------------
# 3) spread_oat_bund_10y — FRED FR − DE (long-term), z-score du spread
# ---------------------------------------------------------------------------

def _oat_crit() -> dict:
    return {"cle_courante": "spread_oat_bund_10y", "normalisation": "zscore",
            "source": "Twelve Data (calculé)", "zscore_window": 60,
            "zscore_div": 2, "cap": 1.0, "signe": -1}


def test_spread_oat_bund_branche_fred(monkeypatch, now_fixed):
    """fetch_fred_spread renvoie une série de spreads qui s'élargit → z>0."""
    spreads = [0.40 + 0.005 * i for i in range(70)]  # spread FR-DE croissant

    def fake_spread(sus, sde, n=252):
        assert sus == "IRLTLT01FRM156N" and sde == "IRLTLT01DEM156N"
        return spreads

    monkeypatch.setattr(cc, "fetch_fred_spread", fake_spread)
    val = cc.build_critere_value("cac40", _oat_crit(), {}, {}, [], now_fixed)
    assert val is not None, "spread_oat_bund_10y doit être branché sur FRED FR-DE"
    assert "valeur_normalisee" in val
    assert val["valeur_normalisee"] > 0  # spread s'élargit → dernier > moyenne
    assert val["valeur"] == pytest.approx(spreads[-1])


def test_spread_oat_bund_fetch_absent_na(monkeypatch, now_fixed):
    monkeypatch.setattr(cc, "fetch_fred_spread", lambda sus, sde, n=252: None)
    val = cc.build_critere_value("cac40", _oat_crit(), {}, {}, [], now_fixed)
    assert val is None


# ---------------------------------------------------------------------------
# 4) differentiel_taux_2y_us_de — TIER 2 : reste n/a (pas de German 2Y gratuit)
# ---------------------------------------------------------------------------

def test_differentiel_2y_reste_na(monkeypatch, now_fixed):
    """Pas de série German 2Y FRED/Twelve gratuite → n/a propre, jamais inventé."""
    monkeypatch.setattr(cc, "fetch_fred_series", lambda sid, n=252: [1.0] * 70)
    monkeypatch.setattr(cc, "fetch_fred_spread", lambda sus, sde, n=252: [1.0] * 70)
    assert "differentiel_taux_2y_us_de" not in cc.FRED_SPREADS
    assert "differentiel_taux_2y_us_de" not in cc.FRED_SERIES_SIMPLE
    assert "differentiel_taux_2y_us_de" not in cc.FRED_DELTA
    crit = {"cle_courante": "differentiel_taux_2y_us_de", "normalisation": "zscore",
            "source": "FRED / Twelve Data (calculé)", "zscore_window": 60,
            "zscore_div": 2, "cap": 1.0, "signe": -1}
    val = cc.build_critere_value("eurusd", crit, {}, {}, [], now_fixed)
    assert val is None


# ---------------------------------------------------------------------------
# 5) v2x_regime — TIER 2 : VSTOXX indispo Twelve gratuit → n/a propre
# ---------------------------------------------------------------------------

def test_v2x_regime_na_si_indispo(monkeypatch, now_fixed):
    """^STOXX50EVOL yfinance-only (bloqué CI) → fetch_price None → n/a propre."""
    monkeypatch.setattr(cc, "fetch_cboe_history", lambda idx: None)
    monkeypatch.setattr(cc, "fetch_twelve_price", lambda sym: None)
    crit = {"cle_courante": "v2x_regime", "normalisation": "mapping_non_monotone",
            "source": "Twelve Data", "centre_optimal": 16, "cap": 1.0, "signe": 1}
    val = cc.build_critere_value("cac40", crit, {}, {}, [], now_fixed)
    assert val is None


def test_v2x_regime_branche_si_source_dispo(monkeypatch, now_fixed):
    """Si un jour V2X est dispo (price 16 = centre sain), le mapping émet +cap."""
    monkeypatch.setattr(cc, "fetch_cboe_history", lambda idx: None)
    monkeypatch.setattr(cc, "fetch_twelve_price", lambda sym: 16.0)
    crit = {"cle_courante": "v2x_regime", "normalisation": "mapping_non_monotone",
            "source": "Twelve Data", "centre_optimal": 16, "cap": 1.0, "signe": 1}
    val = cc.build_critere_value("cac40", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert val["valeur"] == pytest.approx(16.0)
    assert val["valeur_normalisee"] == pytest.approx(1.0)  # centre → +cap
