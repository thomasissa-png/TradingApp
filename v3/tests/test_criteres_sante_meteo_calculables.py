"""Tests — santé des critères persistée, durcissement météo, USD/BRL, gap RV/IV.

Couvre le lot « santé des critères + météo cacao + 2 critères calculables » :
  1. write_criteres_health : raisons exactes (HTTP code, vide, unmapped) persistées.
  2. fetch_open_meteo_anomaly : la cause HTTP (status_out) enrichit le SKIP_COUNTER.
  3. _retry_meteo_once : 1 retry global, récupère un critère météo n/a au 2e essai.
  4. usd_brl : mappé vers USD/BRL côté market_data (café id=3).
  5. gap_rv_iv : spread RV(S&P) − IV(VIX) calculé sur séries synthétiques + n/a propre.

Aucun appel réseau réel — tout mocké. v3/data/ jamais pollué (tmp_path).
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


NOW = datetime(2026, 6, 10, 5, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _clean_skip():
    cc.SKIP_COUNTER.clear()
    yield
    cc.SKIP_COUNTER.clear()


# ---------------------------------------------------------------------------
# 1. Santé persistée
# ---------------------------------------------------------------------------

def test_write_criteres_health_persiste_raisons(tmp_path):
    skips = {
        "meteo_dead:6.8,-5.3:429": 2,
        "twelve_no_key": 1,
        "cboe_unmapped:put_call_ratio_cboe_5j": 1,
    }
    out = tmp_path / "criteres-health.md"
    cc.write_criteres_health(skips, NOW, path=out)
    text = out.read_text(encoding="utf-8")
    # Raison lisible + détail HTTP code conservé pour traçabilité
    assert "Open-Meteo injoignable (récents)" in text
    assert "6.8,-5.3:429" in text
    assert "Pas de clé TWELVE_DATA_API_KEY" in text
    assert "Put/Call sans CSV public" in text
    # Synthèse + tri par occurrences décroissantes (meteo 2 en tête)
    assert "Santé des critères" in text
    assert "3 motifs de skip distincts" in text


def test_write_criteres_health_aucun_skip(tmp_path):
    out = tmp_path / "criteres-health.md"
    cc.write_criteres_health({}, NOW, path=out)
    text = out.read_text(encoding="utf-8")
    assert "Aucun critère skippé" in text


def test_skip_reason_decode_prefixe():
    assert "Open-Meteo injoignable (récents)" in cc._skip_reason("meteo_dead:6.8,-5.3:429")
    # Préfixe inconnu → renvoyé tel quel (pas de crash)
    assert cc._skip_reason("motif_inedit:detail").startswith("motif_inedit")


# ---------------------------------------------------------------------------
# 2. Cause HTTP capturée dans le SKIP_COUNTER météo
# ---------------------------------------------------------------------------

def test_meteo_skip_capture_code_http(monkeypatch):
    """http_get_json renvoie None + remplit status_out['status']=429 → la cause
    apparaît dans la clé SKIP_COUNTER (échec visible)."""
    def fake_get(url, params=None, timeout=15, *, status_out=None):
        if status_out is not None:
            status_out["status"] = "429"
        return None
    monkeypatch.setattr(cc, "http_get_json", fake_get)
    z = cc.fetch_open_meteo_anomaly(6.8, -5.3, days=30)
    assert z is None
    keys = list(cc.SKIP_COUNTER.keys())
    assert any(k.startswith("meteo_dead:6.8,-5.3:429") for k in keys), keys


def test_meteo_get_json_tolere_mock_sans_status_out(monkeypatch):
    """Un mock legacy sans kwarg status_out ne casse pas (fallback positionnel)."""
    calls = {"n": 0}

    def legacy_get(url, params=None, timeout=15):  # pas de status_out
        calls["n"] += 1
        return {"daily": {"precipitation_sum": [1.0, 2.0, 3.0] * 20}}
    monkeypatch.setattr(cc, "http_get_json", legacy_get)
    # Ne lève pas malgré l'appel avec status_out en interne
    cc.fetch_open_meteo_anomaly(6.8, -5.3, days=30)
    assert calls["n"] >= 1


# ---------------------------------------------------------------------------
# 3. Retry météo global (1 essai)
# ---------------------------------------------------------------------------

def test_retry_meteo_once_recupere_critere(monkeypatch):
    """Un critère météo absent du payload est ré-tenté UNE fois ; succès → ajouté."""
    monkeypatch.setattr(cc, "METEO_RETRY_DELAY_S", 0.0)
    fiches = {
        "cacao": {"criteres": [
            {"cle_courante": "meteo_ci_ghana_precip_30j", "normalisation": "zscore",
             "zscore_div": 2, "cap": 1.0},
        ]},
    }
    payload = {"last_update": NOW.isoformat(), "cacao": {}}  # critère n/a

    def fake_meteo(cle, crit, ts):
        return {"valeur": 0.357, "valeur_normalisee": 0.18,
                "valeur_ponderee": 0.18, "ts": ts}
    monkeypatch.setattr(cc, "_handle_meteo", fake_meteo)
    cc._retry_meteo_once(fiches, payload, NOW)
    assert "meteo_ci_ghana_precip_30j" in payload["cacao"]
    assert payload["cacao"]["meteo_ci_ghana_precip_30j"]["valeur"] == 0.357


def test_retry_meteo_once_echec_reste_na(monkeypatch):
    """Si le retry échoue aussi → critère reste n/a (pas de boucle, pas de crash)."""
    monkeypatch.setattr(cc, "METEO_RETRY_DELAY_S", 0.0)
    fiches = {"cacao": {"criteres": [
        {"cle_courante": "meteo_ci_ghana_precip_30j", "normalisation": "zscore"},
    ]}}
    payload = {"last_update": NOW.isoformat(), "cacao": {}}
    monkeypatch.setattr(cc, "_handle_meteo", lambda c, cr, ts: None)
    cc._retry_meteo_once(fiches, payload, NOW)
    assert "meteo_ci_ghana_precip_30j" not in payload["cacao"]


def test_retry_meteo_skip_si_deja_present(monkeypatch):
    """Un critère météo déjà alimenté n'est PAS ré-tenté."""
    monkeypatch.setattr(cc, "METEO_RETRY_DELAY_S", 0.0)
    fiches = {"cacao": {"criteres": [
        {"cle_courante": "meteo_ci_ghana_precip_30j", "normalisation": "zscore"},
    ]}}
    payload = {"cacao": {"meteo_ci_ghana_precip_30j": {"valeur": 1.0}}}
    called = {"n": 0}

    def spy(c, cr, ts):
        called["n"] += 1
        return None
    monkeypatch.setattr(cc, "_handle_meteo", spy)
    cc._retry_meteo_once(fiches, payload, NOW)
    assert called["n"] == 0


# ---------------------------------------------------------------------------
# 4. USD/BRL câblé (café id=3)
# ---------------------------------------------------------------------------

def test_usd_brl_mappe_vers_twelve():
    # Le critère café est mappé vers le symbole Yahoo USDBRL=X...
    assert cc.TWELVE_SYMBOLS["usd_brl"] == "USDBRL=X"
    # ...que market_data sait traduire en paire Twelve USD/BRL (comme EUR=X→EUR/USD).
    mapped = md._map_ticker("USDBRL=X")
    assert mapped == ("USD/BRL", {})


def test_usd_brl_zscore_sur_serie_synthetique(monkeypatch):
    """build_critere_value('cafe', usd_brl) → z-score calculé si la série existe."""
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    # série croissante puis dernier point haut → z>0
    series = [(base.replace(day=1) , 5.0 + i * 0.01) for i in range(70)]
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda sym, **k: series if sym == "USDBRL=X" else None)
    crit = {"cle_courante": "usd_brl", "normalisation": "zscore", "source": "Twelve Data",
            "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    res = cc.build_critere_value("cafe", crit, {}, {}, [], NOW)
    assert res is not None
    assert "valeur_normalisee" in res


def test_usd_brl_serie_manquante_na_propre(monkeypatch):
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda sym, **k: None)
    crit = {"cle_courante": "usd_brl", "normalisation": "zscore", "source": "Twelve Data",
            "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    res = cc.build_critere_value("cafe", crit, {}, {}, [], NOW)
    assert res is None  # n/a propre, zéro invention


# ---------------------------------------------------------------------------
# 5. gap_rv_iv (VIX id=6) — spread RV(S&P) − IV(VIX)
# ---------------------------------------------------------------------------

def _spy_series(n=30, vol=0.01):
    """Série SPY synthétique avec rendements alternés ±vol (stdev ≈ vol)."""
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    closes = [500.0]
    for i in range(1, n):
        closes.append(closes[-1] * (1.0 + (vol if i % 2 else -vol)))
    return [(base, c) for c in closes]


def test_gap_rv_iv_calcule_spread(monkeypatch):
    """RV annualisée − niveau VIX, branché sur la sortie lineaire."""
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda sym, **k: _spy_series(30, 0.01))
    monkeypatch.setattr(cc, "fetch_cboe_history", lambda idx: [("2026-06-09", 15.0)])
    crit = {"cle_courante": "gap_rv_iv", "normalisation": "lineaire",
            "centre": 0.0, "echelle": 5.0, "cap": 1.0, "signe": -1}
    res = cc.build_critere_value("vix", crit, {}, {}, [], NOW)
    assert res is not None
    # RV ≈ 1% daily ×√252 ×100 ≈ 15.87 ; IV=15 → spread ≈ +0.87 (RV légèrement > IV)
    assert res["valeur"] == pytest.approx(0.87, abs=0.6)


def test_gap_rv_iv_na_si_vix_manque(monkeypatch):
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda sym, **k: _spy_series(30, 0.01))
    monkeypatch.setattr(cc, "fetch_cboe_history", lambda idx: None)  # CBOE down
    crit = {"cle_courante": "gap_rv_iv", "normalisation": "lineaire",
            "centre": 0.0, "echelle": 5.0, "cap": 1.0}
    res = cc.build_critere_value("vix", crit, {}, {}, [], NOW)
    assert res is None
    assert cc.SKIP_COUNTER.get("gap_rv_iv_iv_missing", 0) == 1


def test_gap_rv_iv_na_si_spy_manque(monkeypatch):
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda sym, **k: None)
    monkeypatch.setattr(cc, "fetch_cboe_history", lambda idx: [("2026-06-09", 15.0)])
    crit = {"cle_courante": "gap_rv_iv", "normalisation": "lineaire",
            "centre": 0.0, "echelle": 5.0, "cap": 1.0}
    res = cc.build_critere_value("vix", crit, {}, {}, [], NOW)
    assert res is None


def test_gap_rv_iv_realized_vol_annualisation(monkeypatch):
    """RV = stdev rendements ×√252 ×100. Avec ±1% alterné, RV ≈ 15.87."""
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda sym, **k: _spy_series(30, 0.01))
    rv = cc._realized_vol_sp500(20)
    assert rv == pytest.approx(15.87, abs=0.3)
