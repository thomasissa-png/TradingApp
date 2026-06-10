"""Tests A2 (cap aveugle au momentum) + A6 (couverture exclut le momentum).

Audit momentum-family 10/06 :
  A2 — le cap anti-inversion news/quant est calculé sur quant SANS le momentum
       (`cap_abs = |quant_total − contrib_momentum| × α`). Le momentum garde sa
       voix dans le score mais ne participe JAMAIS au plafonnement des news.
  A6 — le momentum-prix est exclu du calcul de couverture (gate S5) pour
       préserver le filet is_news_regime / drapeau 📰.

On isole le momentum via un critère `cle_courante` préfixé `momentum_prix_`,
normalisation `lineaire` (valeur contrôlée). Aucun appel HTTP réel.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


def _cr(cle, poids, valeur_norm, *, is_na):
    """CritereResult minimal pour tester compute_coverage (champs requis remplis)."""
    return sa.CritereResult(
        id=cle, nom=cle, type_norm="lineaire", valeur_brute=valeur_norm,
        valeur_norm=valeur_norm, poids=poids, signe=1,
        pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0}, note="",
        is_gate=False, is_na=is_na, source_track="twelvedata",
        cle_courante=cle,
    )


# ---------------------------------------------------------------------------
# Fabriques de fiches
# ---------------------------------------------------------------------------

def _critere(id_, nom, cle, *, signe=1, poids=10, norm="lineaire"):
    return {
        "id": id_, "nom": nom,
        "cle_courante": cle, "normalisation": norm,
        "centre": 0.0, "echelle": 1.0, "cap": 1.0,
        "signe": signe, "poids": poids,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }


def _fiche_qmn(actif="TestActif"):
    """Fiche : 1 quant 'classique' + 1 momentum-prix + 1 news. Poids égaux."""
    return {
        "actif": actif,
        "criteres": [
            _critere(1, "Quant", "quant_macro", poids=10),
            _critere(2, "Momentum", "momentum_prix_20j_test", poids=10),
            {
                "id": 3, "nom": "News",
                "cle_courante": "news", "normalisation": "triplet",
                "cap": 1.0, "signe": 1, "poids": 10,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _vals_qmn(quant_val, momentum_val, news_val,
              mat="medium", rel="confirmed", nature="ponctuel", freshness_days=1.0):
    return {
        "quant_macro": {"valeur": quant_val, "source_track": "twelvedata"},
        "momentum_prix_20j_test": {"valeur": momentum_val, "source_track": "twelvedata"},
        "news": {
            "valeur": news_val, "source_track": "ia_synthese",
            "materiality": mat, "reliability": rel, "nature": nature,
            "freshness_days": freshness_days,
            "event_id": "TEST", "event_date_source": "rss",
        },
    }


# ---------------------------------------------------------------------------
# A2 — cap aveugle au momentum
# ---------------------------------------------------------------------------

def test_cap_aveugle_momentum_alimente_pas_le_plafond():
    """Tendance finissante : momentum encore haussier (+1) gonfle quant_total,
    mais NE doit PAS gonfler le plafond laissé aux news SHORT.

    quant_macro = +1*10 = +10 ; momentum = +1*10 = +10 → quant_total = +20.
    news = -1*10 = -10.
    Cap AVEUGLE au momentum : base = quant_total − contrib_momentum = +10.
      cap_abs = 10 * 0.8 = 8 → news cappée à -8.
    Cap NAÏF (ancien, inclurait le momentum) : base = +20 → cap_abs = 16 → news
      non cappée (|−10| ≤ 16) → news garderait toute sa voix de -10.
    Donc : avec A2, news_capped = -8 (cap appliqué). Score = 20 - 8 = +12.
    """
    fiche = _fiche_qmn()
    vals = _vals_qmn(quant_val=1.0, momentum_val=1.0, news_val=-1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    info = res.news_cap_info["24h"]
    assert info["cap_applied"] is True, "le cap doit s'appliquer sur la base SANS momentum"
    assert info["contrib_momentum"] == pytest.approx(10.0)
    assert info["cap_quant_ex_momentum"] == pytest.approx(10.0)
    assert info["news_total_pm1_capped"] == pytest.approx(-8.0)
    assert res.scores["24h"] == pytest.approx(12.0)


def test_cap_naif_aurait_laisse_passer_la_news():
    """Contrôle : sans la correction A2 (cap sur quant_total entier=+20), la news
    -10 ne serait PAS cappée (|−10| ≤ 0.8*20=16). On prouve que A2 change le
    résultat en comparant à ce qu'aurait donné le cap naïf.
    """
    fiche = _fiche_qmn()
    vals = _vals_qmn(quant_val=1.0, momentum_val=1.0, news_val=-1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    # Avec A2 : cap appliqué → news = -8 ≠ -10 (le cap naïf aurait laissé -10).
    assert res.news_cap_info["24h"]["news_total_pm1"] == pytest.approx(-10.0)
    assert res.news_cap_info["24h"]["news_total_pm1_capped"] == pytest.approx(-8.0)


def test_cap_momentum_absent_comportement_inchange():
    """Sans critère momentum (n/a), contrib_momentum=0 → cap identique à l'ancien.

    Régression : le cap classique news vs quant doit donner exactement le même
    résultat qu'avant l'introduction de A2 quand il n'y a pas de momentum.
    """
    fiche = _fiche_qmn()
    # momentum n/a (valeur absente du dict de valeurs).
    vals = {
        "quant_macro": {"valeur": 1.0, "source_track": "twelvedata"},
        "news": {
            "valeur": -1.0, "source_track": "ia_synthese",
            "materiality": "medium", "reliability": "confirmed",
            "nature": "ponctuel", "freshness_days": 1.0,
            "event_id": "T", "event_date_source": "rss",
        },
    }
    res = sa.score_actif("test", fiche, vals)
    info = res.news_cap_info["24h"]
    assert info["contrib_momentum"] == pytest.approx(0.0)
    assert info["cap_quant_ex_momentum"] == pytest.approx(10.0)
    # quant=+10, news=-10 → cap 0.8*10=8 → news=-8 → score=+2 (comme test_news_cap).
    assert info["cap_applied"] is True
    assert res.scores["24h"] == pytest.approx(2.0)


def test_cap_momentum_meme_signe_que_news_pas_d_etouffement():
    """Momentum et news dans le MÊME sens (SHORT) contre un quant macro LONG.

    quant_macro=+10 ; momentum=-10 (baissier) → quant_total=0. news=-10.
    Base du cap = quant_total − contrib_momentum = 0 − (−10) = +10.
    Signes opposés (news<0 < base +10) → cap = 0.8*10 = 8 → news=-8.
    Score = 0 + (-8) = -8 → SHORT. Le momentum baissier a aidé la direction
    (via quant_total) sans servir à étouffer la news (qui va dans son sens).
    """
    fiche = _fiche_qmn()
    vals = _vals_qmn(quant_val=1.0, momentum_val=-1.0, news_val=-1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    info = res.news_cap_info["24h"]
    assert info["contrib_momentum"] == pytest.approx(-10.0)
    assert info["cap_quant_ex_momentum"] == pytest.approx(10.0)
    assert res.conclusions["24h"] == "SHORT"
    assert res.scores["24h"] == pytest.approx(-8.0)


def test_cap_decision_log_expose_champs_a2():
    """Les nouveaux champs A2 sont tracés au decision-log."""
    from datetime import datetime, timezone
    fiche = _fiche_qmn()
    vals = _vals_qmn(quant_val=1.0, momentum_val=1.0, news_val=-1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    records = sa.build_decision_log_records([res], datetime(2026, 6, 10, tzinfo=timezone.utc))
    rec = next(r for r in records if r["horizon"] == "24h")
    assert rec["contrib_momentum"] == pytest.approx(10.0)
    assert rec["cap_quant_ex_momentum"] == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# A6 — couverture exclut le momentum
# ---------------------------------------------------------------------------

def test_couverture_exclut_momentum_du_denominateur():
    """compute_coverage ignore le momentum (num ET dénom).

    Fiche : quant_macro (poids 10, présent) + momentum (poids 10, présent) +
    autre quant (poids 10, ABSENT). Sans A6 : couverture = 20/30 = 0.667.
    Avec A6 (momentum exclu des deux côtés) : couverture = 10/20 = 0.5.
    """
    crits = [
        _cr("quant_macro", 10, 0.5, is_na=False),
        _cr("momentum_prix_20j_test", 10, 0.5, is_na=False),
        _cr("autre_quant", 10, None, is_na=True),
    ]
    cov = sa.compute_coverage(crits)
    assert cov == pytest.approx(0.5), (
        "le momentum (toujours dispo) ne doit pas gonfler la couverture"
    )


def test_couverture_momentum_present_ne_remonte_pas_au_dessus_du_plancher():
    """Cœur de A6 : un momentum présent ne doit pas, à lui seul, faire repasser
    une cellule au-dessus de COVERAGE_MIN (sinon il éteindrait le filet 📰).

    quant_macro ABSENT (poids 30) + momentum présent (poids 10).
    Sans A6 : couverture = 10/40 = 0.25 (< 0.40 = INSUFFISANT, filet 📰 actif) —
      mais si le momentum avait un poids fort, il remonterait au-dessus.
    Avec A6 : le momentum est exclu → couverture = 0/30 = 0.0 (filet préservé).
    """
    crits = [
        _cr("quant_macro", 30, None, is_na=True),
        _cr("momentum_prix_20j_test", 10, 0.5, is_na=False),
    ]
    cov = sa.compute_coverage(crits)
    assert cov == pytest.approx(0.0)


def test_couverture_sans_momentum_inchangee():
    """Régression : sans momentum, compute_coverage est inchangée."""
    crits = [
        _cr("a", 10, 0.5, is_na=False),
        _cr("b", 10, None, is_na=True),
    ]
    assert sa.compute_coverage(crits) == pytest.approx(0.5)
