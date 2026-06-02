"""TradingApp v3 — Tests LOT 1 garde-fous P0 (concertation 3-experts).

Couvre :
- GATE C2  : intégrité des critères quant (clip z, std=0, prix invalide, spike).
- GATE Réconciliation : Σ contributions individuelles = score final par horizon.
- GATE C9  : normalisation UTC tz-aware + rejet futur des timestamps event.

Aucun de ces gates ne change le résultat tant que la donnée est valide — ils ne
se déclenchent QUE sur donnée corrompue/incohérente (→ n/a, log, correction).
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Path setup
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

# Stub feedparser si absent (sandbox CI sans sgmllib3k). Cohérent avec test_ingestion.
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    fp_stub = types.ModuleType("feedparser")
    fp_stub.parse = lambda content: types.SimpleNamespace(entries=[])
    sys.modules["feedparser"] = fp_stub

import criteres_calculator as cc  # noqa: E402
import scoring_analyste as sa  # noqa: E402
import news_collector as nc  # noqa: E402
import triggers_classifier as tc  # noqa: E402


# ============================================================
# GATE C2 — Intégrité des critères quant
# ============================================================

def test_c2_zscore_extreme_is_clipped_to_3_sigma(caplog):
    """z-score brut > 3 → clippé à +3 (puis divisé par zscore_div, capé)."""
    # Série uniform 0..99 (mean=49.5, std~28.86). value=15 * std + mean ≈ 482.4
    # → z = +15, doit être clippé à +3.
    history = list(range(100))
    # zscore_div=1 (pas de réduction supplémentaire), cap=10 (>3, pas de re-clip)
    with caplog.at_level(logging.WARNING):
        norm = cc.compute_zscore_normalisee(
            value=49.5 + 15 * 28.866, history=history,
            zscore_div=1.0, cap=10.0, label="test_clip"
        )
    assert norm is not None
    # Doit être exactement Z_CLIP_MAX (3.0) / 1.0 = 3.0
    assert norm == pytest.approx(cc.Z_CLIP_MAX, abs=1e-6)
    # WARNING émis (z brut ~15 > Z_WARN_THRESHOLD=2.5)
    assert any("z-score extrême" in r.message for r in caplog.records)


def test_c2_zscore_negatif_extreme_is_clipped(caplog):
    """z-score brut < -3 → clippé à -3."""
    history = list(range(100))
    with caplog.at_level(logging.WARNING):
        norm = cc.compute_zscore_normalisee(
            value=49.5 - 15 * 28.866, history=history,
            zscore_div=1.0, cap=10.0, label="test_clip_neg"
        )
    assert norm == pytest.approx(-cc.Z_CLIP_MAX, abs=1e-6)


def test_c2_constant_series_returns_na_no_zero_division():
    """Série constante (std=0) → None (pas de ZeroDivisionError)."""
    history = [42.0] * 50
    norm = cc.compute_zscore_normalisee(
        value=42.0, history=history,
        zscore_div=1.0, cap=1.0, label="test_const"
    )
    assert norm is None


def test_c2_value_nan_returns_na():
    """value = NaN → None (n/a)."""
    norm = cc.compute_zscore_normalisee(
        value=float("nan"), history=list(range(50)),
        zscore_div=1.0, cap=1.0, label="test_nan"
    )
    assert norm is None


def test_c2_value_inf_returns_na():
    """value = Inf → None (n/a)."""
    norm = cc.compute_zscore_normalisee(
        value=float("inf"), history=list(range(50)),
        zscore_div=1.0, cap=1.0, label="test_inf"
    )
    assert norm is None


def test_c2_invalid_price_helpers():
    """Helpers _is_finite_number / _is_valid_price : prix ≤0/NaN/Inf rejetés."""
    assert not cc._is_valid_price(0)
    assert not cc._is_valid_price(-1.5)
    assert not cc._is_valid_price(float("nan"))
    assert not cc._is_valid_price(float("inf"))
    assert not cc._is_valid_price(None)
    assert cc._is_valid_price(0.0001)
    assert cc._is_valid_price(100.0)


def test_c2_spike_filter_drops_implausible_variation(caplog):
    """Variation journalière > seuil de la classe d'actif → point ignoré + log."""
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    # Série avec un spike au milieu : +60% en 1 jour sur un indice → > 20% → out.
    series = [
        (base + timedelta(days=i), p) for i, p in enumerate([100, 101, 102, 163, 102, 103])
    ]
    with caplog.at_level(logging.WARNING):
        out = cc._filter_spikes(series, threshold=cc.SPIKE_THRESHOLD_INDEX, label="^TEST")
    closes = [c for _, c in out]
    # 163 doit être absent. 102 (jour 5) revient car prev (102, j2) est conservé.
    assert 163 not in closes
    assert any("spike" in r.message.lower() for r in caplog.records)


def test_c2_spike_thresholds_per_class():
    """Seuils différenciés par classe d'actif (indices/commodités/FX/défaut)."""
    assert cc._spike_threshold_for_symbol("^GSPC") == cc.SPIKE_THRESHOLD_INDEX
    assert cc._spike_threshold_for_symbol("BZ=F") == cc.SPIKE_THRESHOLD_COMMODITY
    assert cc._spike_threshold_for_symbol("EURUSD=X") == cc.SPIKE_THRESHOLD_FX
    assert cc._spike_threshold_for_symbol("AAPL") == cc.SPIKE_THRESHOLD_DEFAULT


# ============================================================
# Synergie C2 ↔ S5 (compute_coverage)
# ============================================================

def test_c2_na_critere_lowers_coverage_via_s5():
    """Un critère passé n/a par C2 baisse la coverage S5 (synergie attendue).

    Garantit que C2 (n/a) alimente bien le gate de couverture S5 :
    compute_coverage compte les critères AVEC valeur_norm non-None ;
    quand C2 force None, la couverture chute → confidence dégradée en aval.
    """
    # 3 critères, poids 5 chacun. 1 passe en n/a (C2 a forcé None).
    crits = [
        sa.CritereResult(
            id="c1", nom="ok1", type_norm="zscore", valeur_brute=0.5,
            valeur_norm=0.5, poids=5.0, signe=1,
            pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0}, note="",
            is_na=False, is_gate=False,
        ),
        sa.CritereResult(
            id="c2", nom="ok2", type_norm="zscore", valeur_brute=-0.3,
            valeur_norm=-0.3, poids=5.0, signe=1,
            pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0}, note="",
            is_na=False, is_gate=False,
        ),
        sa.CritereResult(
            id="c3", nom="na_via_c2", type_norm="zscore", valeur_brute=None,
            valeur_norm=None, poids=5.0, signe=1,
            pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0},
            note="n/a (C2 std=0)", is_na=True, is_gate=False,
        ),
    ]
    cov = sa.compute_coverage(crits)
    # 2 / 3 critères couverts (poids égaux) → ~0.666
    assert cov == pytest.approx(2.0 / 3.0, abs=1e-6)
    # Doit déclencher palier "faible" (entre COVERAGE_MIN=0.40 et COVERAGE_OK=0.65)
    # Note : 0.666 > 0.65 donc "normale" ici. Test plus strict avec un 4ème NA :
    crits.append(sa.CritereResult(
        id="c4", nom="na2", type_norm="zscore", valeur_brute=None,
        valeur_norm=None, poids=5.0, signe=1,
        pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0},
        note="n/a", is_na=True, is_gate=False,
    ))
    cov2 = sa.compute_coverage(crits)
    assert cov2 == pytest.approx(0.5, abs=1e-6)
    assert sa.derive_confidence(cov2) == "faible"  # 0.40 ≤ 0.5 < 0.65


# ============================================================
# GATE Réconciliation Σ contributions = score
# ============================================================

def test_reconcile_score_nominal_match():
    """Cas nominal : Σ contributions == score → True, aucune erreur loggée."""
    contribs = {"c1": 0.3, "c2": -0.1, "c3": 0.2}
    ok = sa.reconcile_score(0.4, contribs, actif="TEST", horizon="24h")
    assert ok is True


def test_reconcile_score_detects_mismatch_logs_error(caplog):
    """Écart Σ != score → False + ERROR loggée (mais pas de crash)."""
    contribs = {"c1": 0.3, "c2": 0.5}
    with caplog.at_level(logging.ERROR):
        ok = sa.reconcile_score(0.4, contribs, actif="TEST", horizon="7j")
    assert ok is False
    assert any("RECONCILE ERROR" in r.message for r in caplog.records)
    # Le message contient les valeurs : actif, horizon, Σ, score
    err_msg = next(r.message for r in caplog.records if "RECONCILE ERROR" in r.message)
    assert "TEST" in err_msg
    assert "7j" in err_msg


def test_reconcile_score_with_cap_extra():
    """cap_extra (delta news_capped - news_total) compense correctement."""
    # Σ contribs brutes = 1.0, mais le cap retire 0.3 (news_capped < news_total).
    contribs = {"news": 0.7, "quant": 0.3}
    # score_final = 0.7 (après cap qui ramène news 0.7→0.4) → 0.4 + 0.3 = 0.7
    ok = sa.reconcile_score(0.7, contribs, actif="TEST", horizon="1m", cap_extra=-0.3)
    assert ok is True


def test_score_actif_reconciliation_passes_on_real_compute(caplog):
    """score_actif : la réconciliation doit passer sans ERROR sur calcul nominal."""
    fiche = {
        "actif": "TEST",
        "criteres": [
            {
                "id": 1, "nom": "k1", "cle_courante": "k1",
                "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0,
                "poids": 3.0, "signe": 1,
                "pertinence": {"24h": 1.0, "7j": 0.8, "1m": 0.5},
            },
            {
                "id": 2, "nom": "k2", "cle_courante": "k2",
                "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0,
                "poids": 2.0, "signe": -1,
                "pertinence": {"24h": 0.5, "7j": 1.0, "1m": 1.0},
            },
        ],
    }
    valeurs = {"k1": 0.4, "k2": 0.2}
    with caplog.at_level(logging.ERROR, logger="scoring_analyste"):
        result = sa.score_actif("test", fiche, valeurs)
    # Aucune erreur de réconciliation
    assert not any("RECONCILE ERROR" in r.message for r in caplog.records)
    # Scores cohérents par horizon
    # 24h : 0.4*3*1*1 + 0.2*2*0.5*-1 = 1.2 - 0.2 = 1.0
    assert result.scores["24h"] == pytest.approx(1.0, abs=1e-6)


# ============================================================
# GATE C9 — Normalisation UTC des timestamps à l'ingestion
# ============================================================

def test_c9_normalize_naive_datetime_becomes_utc_aware():
    """Datetime naïf → UTC tz-aware (replace tzinfo)."""
    naive = datetime(2026, 1, 15, 12, 30, 0)
    assert naive.tzinfo is None
    out = nc._normalize_to_utc(naive, source="test")
    assert out.tzinfo is timezone.utc
    assert out.year == 2026 and out.month == 1 and out.day == 15


def test_c9_normalize_aware_other_tz_converted_to_utc():
    """Datetime tz-aware non-UTC → converti en UTC."""
    from zoneinfo import ZoneInfo
    paris = datetime(2026, 1, 15, 14, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
    out = nc._normalize_to_utc(paris, source="test")
    assert out.tzinfo is timezone.utc
    # Paris hiver = UTC+1 → 14h Paris = 13h UTC
    assert out.hour == 13


def test_c9_normalize_future_timestamp_clamped_to_now(caplog):
    """Timestamp futur > now + 10min → ramené à now + log WARNING."""
    future = datetime.now(timezone.utc) + timedelta(hours=2)
    with caplog.at_level(logging.WARNING):
        out = nc._normalize_to_utc(future, source="rss:test_source")
    # Doit être ≈ now (à <1s près)
    delta = abs((out - datetime.now(timezone.utc)).total_seconds())
    assert delta < 1.0
    assert any("timestamp futur" in r.message for r in caplog.records)


def test_c9_normalize_near_future_within_tolerance_kept():
    """Timestamp futur < 10 min de tolérance → conservé (horloge légèrement décalée)."""
    near_future = datetime.now(timezone.utc) + timedelta(minutes=5)
    out = nc._normalize_to_utc(near_future, source="test")
    # Conservé tel quel (pas de clamp)
    assert abs((out - near_future).total_seconds()) < 1.0


def test_c9_normalize_none_returns_now_utc():
    """dt=None → now(UTC) tz-aware (jamais naïf)."""
    out = nc._normalize_to_utc(None, source="test")
    assert out.tzinfo is timezone.utc


def test_c9_normalize_non_datetime_returns_now_utc():
    """Input invalide (str, int) → now(UTC) (zéro crash)."""
    out = nc._normalize_to_utc("not a datetime", source="test")
    assert out.tzinfo is timezone.utc


def test_c9_triggers_classifier_parse_date_returns_utc_aware():
    """tc._parse_date : date naïve ISO → UTC tz-aware (mode ingestion default)."""
    dt = tc._parse_date("2026-03-15T10:00:00")
    assert dt is not None
    assert dt.tzinfo is not None
    # astimezone(UTC) → tz est UTC (peut être timezone.utc ou équivalent)
    assert dt.utcoffset() == timedelta(0)


def test_c9_triggers_classifier_parse_date_clamps_future(caplog):
    """tc._parse_date(clamp_future=True, défaut) : futur lointain → ramené à NOW + WARNING."""
    with caplog.at_level(logging.WARNING):
        dt = tc._parse_date("2099-01-01T00:00:00")
    assert dt is not None
    now = datetime.now(timezone.utc)
    assert abs((dt - now).total_seconds()) < 5.0
    assert any("timestamp futur" in r.message for r in caplog.records)


def test_c9_triggers_classifier_parse_date_no_clamp_preserves_future():
    """tc._parse_date(clamp_future=False) : utilisé par _parse_event_date_safe pour valider."""
    dt = tc._parse_date("2099-01-01T00:00:00", clamp_future=False)
    assert dt is not None
    assert dt.year == 2099
    # Et _parse_event_date_safe doit rejeter cette date (None)
    assert tc._parse_event_date_safe("2099-01-01") is None


def test_c9_triggers_classifier_event_date_safe_still_rejects_past_and_future():
    """Rétro-compat : _parse_event_date_safe rejette toujours <2020 et futurs."""
    assert tc._parse_event_date_safe("2019-12-31") is None
    assert tc._parse_event_date_safe("2030-01-01") is None
    # Date valide passe
    valid = tc._parse_event_date_safe("2026-03-15")
    assert valid is not None
    assert valid.tzinfo is not None
