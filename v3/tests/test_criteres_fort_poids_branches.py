"""Tests des critères à fort poids nouvellement branchés (Session 3).

Branche 5 critères dont la source (Twelve Data / FRED) était intégrée mais pas
câblée dans le dispatch de criteres_calculator :

  - dxy_trend_20j          → FRED DTWEXBGS (USD Index broad)         [BRANCHÉ]
  - taux_10y_us_delta_5j   → FRED DGS10, z-score du delta 5j          [BRANCHÉ]
  - spread_oat_bund_10y    → FRED FR(IRLTLT01FRM156N) − DE(...DEM)    [BRANCHÉ]
  - differentiel_taux_2y_us_de → DGS2 (FRED) − Bund 2Y (ECB Data Portal) [BRANCHÉ S?]
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
# 4) differentiel_taux_2y_us_de — BRANCHÉ : DGS2 (FRED) − Bund 2Y (ECB Data Portal)
# ---------------------------------------------------------------------------

def _diff2y_crit() -> dict:
    return {"cle_courante": "differentiel_taux_2y_us_de", "normalisation": "zscore",
            "source": "FRED / Twelve Data (calculé)", "zscore_window": 60,
            "zscore_div": 2, "cap": 1.0, "signe": -1}


def _dgs2_dated(start: str = "2026-01-01", n: int = 70, base: float = 4.0,
                step: float = 0.0):
    """Série DGS2 datée [(date, val)] oldest→newest, dates ISO quotidiennes."""
    from datetime import date as _date, timedelta as _td
    d0 = _date.fromisoformat(start)
    return [((d0 + _td(days=i)).isoformat(), base + i * step) for i in range(n)]


def _ecb_dated(start: str = "2026-01-01", n: int = 70, base: float = 2.0,
               step: float = 0.0):
    from datetime import date as _date, timedelta as _td
    d0 = _date.fromisoformat(start)
    return [((d0 + _td(days=i)).isoformat(), base + i * step) for i in range(n)]


def test_differentiel_2y_us_de_branche(monkeypatch, now_fixed):
    """(a) US + DE dispo → différentiel = DGS2 − Bund2Y, z-score correct (signe vérifié).

    Différentiel qui S'ÉLARGIT (US monte plus vite que DE) → dernier point > moyenne
    → valeur_normalisee > 0. La fiche applique le signe -1 en aval (pas ici).
    """
    monkeypatch.setattr(cc, "fetch_fred_series_dated",
                        lambda sid, n=252: _dgs2_dated(base=4.0, step=0.02) if sid == "DGS2" else None)
    monkeypatch.setattr(cc, "fetch_ecb_yield_series",
                        lambda key, n=300: _ecb_dated(base=2.0, step=0.0))
    val = cc.build_critere_value("eurusd", _diff2y_crit(), {}, {}, [], now_fixed)
    assert val is not None, "le 2Y doit être branché (FRED DGS2 + ECB)"
    assert "valeur_normalisee" in val
    # différentiel courant ≈ (4.0 + 69*0.02) − 2.0 = 3.38 ; série de différentiels
    # croissante → dernier > moyenne → z>0.
    assert val["valeur_normalisee"] > 0
    assert val["valeur"] == pytest.approx(4.0 + 69 * 0.02 - 2.0, abs=1e-6)


def test_differentiel_2y_us_de_resserrement_signe_negatif(monkeypatch, now_fixed):
    """Différentiel qui SE RESSERRE → dernier point < moyenne → normalisee < 0 (signe inverse)."""
    monkeypatch.setattr(cc, "fetch_fred_series_dated",
                        lambda sid, n=252: _dgs2_dated(base=5.0, step=-0.02) if sid == "DGS2" else None)
    monkeypatch.setattr(cc, "fetch_ecb_yield_series",
                        lambda key, n=300: _ecb_dated(base=2.0, step=0.0))
    val = cc.build_critere_value("eurusd", _diff2y_crit(), {}, {}, [], now_fixed)
    assert val is not None
    assert val["valeur_normalisee"] < 0


def test_differentiel_2y_us_de_ecb_ko_na(monkeypatch, now_fixed):
    """(b) ECB KO → n/a propre (pas de différentiel partiel inventé)."""
    monkeypatch.setattr(cc, "fetch_fred_series_dated",
                        lambda sid, n=252: _dgs2_dated(base=4.0, step=0.01))
    monkeypatch.setattr(cc, "fetch_ecb_yield_series", lambda key, n=300: None)
    val = cc.build_critere_value("eurusd", _diff2y_crit(), {}, {}, [], now_fixed)
    assert val is None


def test_differentiel_2y_us_de_fred_ko_na(monkeypatch, now_fixed):
    """(c) FRED KO (DGS2 indispo) → n/a propre."""
    monkeypatch.setattr(cc, "fetch_fred_series_dated", lambda sid, n=252: None)
    monkeypatch.setattr(cc, "fetch_ecb_yield_series",
                        lambda key, n=300: _ecb_dated(base=2.0, step=0.0))
    val = cc.build_critere_value("eurusd", _diff2y_crit(), {}, {}, [], now_fixed)
    assert val is None


def test_ecb_yield_hors_plage_rejete(monkeypatch):
    """(d) Rendement hors plage [-2, 10] % → série filtrée → None (n/a)."""
    # CSV ECB avec une seule observation absurde (999 %) → hors plage → rejet total.
    csv_text = "KEY,TIME_PERIOD,OBS_VALUE\nYC...,2026-05-29,999.0\n"
    monkeypatch.setattr(cc, "http_get_text", lambda url, timeout=cc.DEFAULT_TIMEOUT: csv_text)
    assert cc.fetch_ecb_yield(cc.ECB_BUND_2Y_SERIES_KEY) is None
    series = cc.fetch_ecb_yield_series(cc.ECB_BUND_2Y_SERIES_KEY, n=5)
    assert series is None


def test_ecb_csv_parsing_echantillon_realiste(monkeypatch):
    """(e) Parsing CSV ECB d'un échantillon réaliste → valeur extraite, bornée à la plage."""
    # En-tête SDMX-CSV ECB typique (ordre des colonnes volontairement non trivial :
    # OBS_VALUE après TIME_PERIOD, plus une colonne KEY en tête).
    csv_text = (
        "KEY,FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE,OBS_STATUS\n"
        "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y,B,U2,2026-05-27,2.10,A\n"
        "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y,B,U2,2026-05-28,2.15,A\n"
        "YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y,B,U2,2026-05-29,2.23,A\n"
    )
    monkeypatch.setattr(cc, "http_get_text", lambda url, timeout=cc.DEFAULT_TIMEOUT: csv_text)
    series = cc.fetch_ecb_yield_series(cc.ECB_BUND_2Y_SERIES_KEY, n=300)
    assert series is not None
    assert [d for d, _ in series] == ["2026-05-27", "2026-05-28", "2026-05-29"]
    assert cc.fetch_ecb_yield(cc.ECB_BUND_2Y_SERIES_KEY) == pytest.approx(2.23)


def test_ecb_json_fallback_parsing(monkeypatch):
    """Fallback JSON (jsondata) : CSV vide → bascule JSON SDMX → valeur extraite."""
    import json as _json
    sdmx = {
        "dataSets": [{"series": {"0:0:0:0:0:0:0": {"observations": {
            "0": [2.05], "1": [2.18]}}}}],
        "structure": {"dimensions": {"observation": [{"values": [
            {"id": "2026-05-28"}, {"id": "2026-05-29"}]}]}},
    }
    json_text = _json.dumps(sdmx)

    def _http(url, timeout=cc.DEFAULT_TIMEOUT):
        # csvdata → vide (force le fallback) ; jsondata → SDMX-JSON.
        return "" if "csvdata" in url else json_text

    monkeypatch.setattr(cc, "http_get_text", _http)
    series = cc.fetch_ecb_yield_series(cc.ECB_BUND_2Y_SERIES_KEY, n=300)
    assert series is not None
    assert series[-1] == ("2026-05-29", pytest.approx(2.18))


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
