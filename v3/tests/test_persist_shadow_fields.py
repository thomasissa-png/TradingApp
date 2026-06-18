"""Tests SHADOW persistance — champs observationnels persist_shadow_* (Partie B).

Mesure « news vit tant que le quant ne la dément pas » vs le filet d'âge 30j.
Garde-fou ABSOLU : ces champs sont PUREMENT ADDITIFS. Ils n'altèrent NI la
direction, NI le score, NI la conclusion, NI les champs existants du decision-log.
Posés UNIQUEMENT sur les critères news (source_track ia*/keyword).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

SHADOW_FIELDS = (
    "persist_shadow_age_days",
    "quant_disconfirms",
    "persist_shadow_alive",
    "persist_shadow_blocks_flip",
)


def _news_crit(
    *,
    freshness_days: float,
    signe: int,
    contrib: float,
    source_track: str = "ia_synthese",
) -> sa.CritereResult:
    """Critère news minimal avec fraîcheur + contribution contrôlées."""
    return sa.CritereResult(
        id=1,
        nom="news_test",
        type_norm="lineaire",
        valeur_brute=None,
        valeur_norm=contrib,
        poids=1.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: contrib for h in sa.HORIZONS},
        contributions_pond={h: contrib for h in sa.HORIZONS},
        source_track=source_track,
        cle_courante="news_test",
        nature="structurel",
        event_id="EV-TEST-1",
        freshness_days=freshness_days,
    )


def _quant_crit(*, signe: int, contrib: float) -> sa.CritereResult:
    """Critère quant pur (pas de source_track news)."""
    return sa.CritereResult(
        id=2,
        nom="quant_test",
        type_norm="lineaire",
        valeur_brute=None,
        valeur_norm=contrib,
        poids=1.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: contrib for h in sa.HORIZONS},
        contributions_pond={h: contrib for h in sa.HORIZONS},
        source_track="",
        cle_courante="quant_test",
    )


def _actif(news_crit, quant_total: float, *, conclusion: str = "LONG") -> sa.ActifResult:
    base_cap = {
        "news_total_pm1": news_crit.contributions["24h"],
        "quant_total_pm1": quant_total,
        "news_total_pm1_capped": news_crit.contributions["24h"],
        "news_total_pond": 0.0, "quant_total_pond": quant_total,
        "news_total_pond_capped": 0.0, "cap_applied": False,
        "override_high_confirmed": False, "alpha": 0.8,
    }
    return sa.ActifResult(
        nom="TestActif",
        fiche_key="testactif",
        criteres=[news_crit, _quant_crit(signe=1 if quant_total >= 0 else -1,
                                          contrib=quant_total)],
        scores={h: quant_total for h in sa.HORIZONS},
        conclusions={h: conclusion for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: quant_total for h in sa.HORIZONS},
        conclusions_pond={h: conclusion for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        news_cap_info={h: dict(base_cap) for h in sa.HORIZONS},
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


def _rec24(records):
    return next(r for r in records if r["horizon"] == "24h")


def _news_entry(rec):
    return next(c for c in rec["criteres"] if c["cle"] == "news_test")


def _quant_entry(rec):
    return next(c for c in rec["criteres"] if c["cle"] == "quant_test")


# ---------------------------------------------------------------------------
# Présence et additivité
# ---------------------------------------------------------------------------

def test_shadow_fields_present_on_news_crit():
    """Les 4 champs shadow sont posés sur le critère news."""
    nc = _news_crit(freshness_days=10.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=0.5)
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    entry = _news_entry(rec)
    for f in SHADOW_FIELDS:
        assert f in entry, f"champ shadow manquant : {f}"


def test_shadow_fields_absent_on_quant_crit():
    """Aucun champ shadow sur un critère quant pur (zéro bruit)."""
    nc = _news_crit(freshness_days=10.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=0.5)
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    entry = _quant_entry(rec)
    for f in SHADOW_FIELDS:
        assert f not in entry


def test_shadow_fields_additive_existing_unchanged():
    """L'ajout des champs shadow n'altère ni score, ni conclusion, ni les
    champs existants du critère news (contrib_pm1, signe, source_track)."""
    nc = _news_crit(freshness_days=10.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=0.5, conclusion="LONG")
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    assert rec["conclusion_pm1"] == "LONG"
    assert rec["score_pm1"] == pytest.approx(0.5)
    entry = _news_entry(rec)
    assert entry["contrib_pm1"] == pytest.approx(0.4)
    assert entry["signe"] == 1
    assert entry["source_track"] == "ia_synthese"


# ---------------------------------------------------------------------------
# Sémantique des flags
# ---------------------------------------------------------------------------

def test_quant_disconfirms_true_when_opposite_sign():
    """News LONG (contrib>0) + quant SHORT (<0) → quant_disconfirms=True."""
    nc = _news_crit(freshness_days=5.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=-0.6)
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    assert _news_entry(rec)["quant_disconfirms"] is True


def test_quant_disconfirms_false_when_same_sign():
    """News LONG + quant LONG → quant_disconfirms=False (quant confirme)."""
    nc = _news_crit(freshness_days=5.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=0.6)
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    assert _news_entry(rec)["quant_disconfirms"] is False


def test_alive_true_when_young_regardless_of_quant():
    """Âge < 30j → vivant dans les deux régimes même si quant dément."""
    nc = _news_crit(freshness_days=12.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=-0.6)  # quant dément
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    entry = _news_entry(rec)
    assert entry["quant_disconfirms"] is True
    assert entry["persist_shadow_alive"] is True  # < 30j → vivant


def test_alive_false_when_old_and_quant_disconfirms():
    """Âge ≥ 30j ET quant dément → mort sous persist-until-quant-confirms."""
    nc = _news_crit(freshness_days=40.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=-0.6)
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    entry = _news_entry(rec)
    assert entry["persist_shadow_age_days"] == pytest.approx(40.0)
    assert entry["persist_shadow_alive"] is False


def test_alive_true_when_old_but_quant_confirms():
    """Âge ≥ 30j MAIS quant confirme → survit sous persistance (≠ régime 30j)."""
    nc = _news_crit(freshness_days=45.0, signe=1, contrib=0.4)
    r = _actif(nc, quant_total=0.6)  # quant confirme
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    entry = _news_entry(rec)
    assert entry["persist_shadow_alive"] is True


def test_blocks_flip_true_when_old_alive_and_decisive():
    """Âge ≥ 30j + vivant (quant confirme) + news décisive (|news|≥|quant|)
    → persist_shadow_blocks_flip=True (la persistance figerait la cellule là où
    le régime 30j l'aurait DROP)."""
    nc = _news_crit(freshness_days=35.0, signe=1, contrib=0.7)
    r = _actif(nc, quant_total=0.5)  # quant confirme, news plus forte
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    assert _news_entry(rec)["persist_shadow_blocks_flip"] is True


def test_blocks_flip_false_when_young():
    """Âge < 30j → le régime 30j n'aurait rien DROP → pas de blocage."""
    nc = _news_crit(freshness_days=10.0, signe=1, contrib=0.7)
    r = _actif(nc, quant_total=0.5)
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    assert _news_entry(rec)["persist_shadow_blocks_flip"] is False


def test_age_days_matches_freshness():
    """persist_shadow_age_days reflète freshness_days du critère porteur."""
    nc = _news_crit(freshness_days=23.5, signe=-1, contrib=-0.3)
    r = _actif(nc, quant_total=-0.4, conclusion="SHORT")
    rec = _rec24(sa.build_decision_log_records([r], datetime.now(timezone.utc)))
    assert _news_entry(rec)["persist_shadow_age_days"] == pytest.approx(23.5)
