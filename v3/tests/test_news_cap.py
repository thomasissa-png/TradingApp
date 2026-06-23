"""Tests Point 3 (cap anti-inversion news/quant) + Point 4 (ratio_news).

Plan horizon — référence : v3/audit/revue-plan-horizon-*.md.
Garde-fous :
- la news ne flippe pas le quant en cas de désaccord (sauf override high+confirmed)
- la pertinence recalibrée est bien chargée
- ratio_news + news_dominant sont calculés et exposés
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers — fabrique de fiches minimales pour isoler le cap
# ---------------------------------------------------------------------------

def _fiche(quant_signe: int = 1, news_signe: int = 1) -> dict:
    """Fiche minimale : 1 critère quant (lineaire) + 1 critère news (triplet).
    Poids égaux pour que le cap soit clairement testable."""
    return {
        "actif": "TestActif",
        "criteres": [
            {
                "id": 1, "nom": "Quant",
                "cle_courante": "quant", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 1.0,
                "signe": quant_signe, "poids": 10,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
            {
                "id": 2, "nom": "News",
                "cle_courante": "news", "normalisation": "triplet",
                "cap": 1.0, "signe": news_signe, "poids": 10,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _valeurs(quant_val: float, news_val: float, mat: str = "medium",
             rel: str = "confirmed", nature: str = "ponctuel",
             freshness_days: float = 1.0) -> dict:
    """Helper Phase 2 : `nature` et `freshness_days` ajoutés pour permettre l'override
    raffiné. Défaut : ponctuel (coef 24h=1.0, neutre pour les tests legacy) + frais (1j).
    Les tests qui veulent l'override passent explicitement nature="structurel"."""
    return {
        "quant": {"valeur": quant_val, "source_track": "twelvedata"},
        "news": {
            "valeur": news_val, "source_track": "ia_synthese",
            "materiality": mat, "reliability": rel,
            "nature": nature,
            "freshness_days": freshness_days,
            "event_id": "TEST", "event_date_source": "rss",
        },
    }


# ---------------------------------------------------------------------------
# Point 3 — cap anti-inversion
# ---------------------------------------------------------------------------

def test_cap_news_short_vs_quant_long_no_flip():
    """News SHORT (-1) face à un quant LONG (+1) ne doit PAS flipper le score
    en SHORT quand la news n'est pas high+confirmed.
    Quant_total = +1*10*1*1 = +10. News_total = -1*10*1*1 = -10.
    Sans cap : score = 0 (ou négatif). Avec cap α=0.8 : news capped = -8,
    score = +10 - 8 = +2 → LONG préservé."""
    fiche = _fiche()
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    assert res.conclusions["24h"] == "LONG"
    assert res.scores["24h"] == pytest.approx(2.0)
    info = res.news_cap_info["24h"]
    assert info["cap_applied"] is True
    assert info["override_high_confirmed"] is False
    assert info["news_total_pm1_capped"] == pytest.approx(-8.0)


def test_cap_news_long_vs_quant_short_no_flip():
    """Symétrique : news LONG face à quant SHORT ne flippe pas en LONG."""
    fiche = _fiche()
    vals = _valeurs(quant_val=-1.0, news_val=1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    assert res.conclusions["24h"] == "SHORT"
    assert res.scores["24h"] == pytest.approx(-2.0)
    assert res.news_cap_info["24h"]["cap_applied"] is True


def test_cap_override_high_confirmed_flips():
    """Override Phase 2 : news high+confirmed+structurel+frais ≤72h → pas de cap.
    Le quant peut flipper."""
    fiche = _fiche()
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="high", rel="confirmed",
                    nature="structurel", freshness_days=1.0)
    res = sa.score_actif("test", fiche, vals)
    info = res.news_cap_info["24h"]
    assert info["override_high_confirmed"] is True
    assert info["cap_applied"] is False
    # structurel × pertinence 1.0 × 24h coef 0.8 → news_contrib = -1*10*0.8 = -8
    # quant +10 + news -8 → score = +2 (au lieu de 0 sans coef_nature).
    # Le but de ce test : vérifier que le CAP n'est pas appliqué.
    # Score exact dépend du coef_nature 24h = 0.8 pour structurel.
    assert res.scores["24h"] == pytest.approx(2.0)


def test_cap_override_only_medium_confirmed_does_not_apply():
    """Override exige high+confirmed. medium+confirmed ⇒ cap appliqué."""
    fiche = _fiche()
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="medium", rel="confirmed")
    res = sa.score_actif("test", fiche, vals)
    assert res.news_cap_info["24h"]["override_high_confirmed"] is False
    assert res.news_cap_info["24h"]["cap_applied"] is True


def test_cap_override_high_unconfirmed_does_not_apply():
    """Override exige reliability ≠ rumor (spec Phase 2). high+rumor ⇒ cap appliqué."""
    fiche = _fiche()
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="high", rel="rumor")
    res = sa.score_actif("test", fiche, vals)
    assert res.news_cap_info["24h"]["override_high_confirmed"] is False
    assert res.news_cap_info["24h"]["cap_applied"] is True


def test_cap_override_blocked_by_nature_verbal_phase2():
    """Phase 2 : même high+confirmed, si nature=verbal → override BLOQUÉ.
    Note : verbal a déjà coef 24h=0.3 → contribution news fortement amortie
    en amont. L'override n'est pas nécessaire pour bloquer le flip — le coef
    suffit. Le test vérifie le drapeau override (jamais autorisé)."""
    fiche = _fiche()
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="high", rel="confirmed",
                    nature="verbal")
    res = sa.score_actif("test", fiche, vals)
    assert res.news_cap_info["24h"]["override_high_confirmed"] is False


def test_cap_override_blocked_by_staleness_phase2():
    """Phase 2 : même high+confirmed+structurel, si event > 72h → override BLOQUÉ.
    On vérifie le drapeau override (le cap peut ne pas s'appliquer si les
    contributions sont équilibrées ; ce qui compte est qu'override=False)."""
    fiche = _fiche()
    # 5j = 120h > 72h
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="high", rel="confirmed",
                    nature="structurel", freshness_days=5.0)
    res = sa.score_actif("test", fiche, vals)
    assert res.news_cap_info["24h"]["override_high_confirmed"] is False
    # Cap appliqué car structurel à 24h coef=0.8 → news=-8, quant=+10. abs(news)=8
    # est <= quant_alpha = 8. Égalité limite : cap_applied dépend de strict ">".
    # Ce qu'on garantit : pas d'override (vieille news → pas de flip autorisé).


def test_cap_no_op_when_signs_aligned():
    """News et quant dans le même sens : pas de cap (pas d'inversion à prévenir)."""
    fiche = _fiche()
    vals = _valeurs(quant_val=1.0, news_val=1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    assert res.scores["24h"] == pytest.approx(20.0)
    assert res.news_cap_info["24h"]["cap_applied"] is False


def test_cap_no_op_when_news_smaller_than_alpha_quant():
    """News opposée mais |news| ≤ 0.8 * |quant| → cap n'a aucun effet."""
    fiche = _fiche()
    # Force un quant plus puissant : poids quant=10, news=5.
    fiche["criteres"][1]["poids"] = 5
    vals = _valeurs(quant_val=1.0, news_val=-1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    # quant_total=+10, news_total=-5, |news|=5 ≤ 0.8*10=8 → pas de cap.
    assert res.news_cap_info["24h"]["cap_applied"] is False
    assert res.scores["24h"] == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Point 2 — pertinence recalibrée (chargement)
# ---------------------------------------------------------------------------

def test_pertinence_recalibree_petrole_geopol():
    """petrole.yml : tension_geopol_moyen_orient 24h=1.0 (boost news 24h refonte
    23/06, porteur net IA ; était 0.6), 7j=0.6, 1m=0.2 préservés."""
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    crits = {c["cle_courante"]: c for c in fiches["petrole"]["criteres"]
             if c.get("cle_courante")}
    p = crits["tension_geopol_moyen_orient"]["pertinence"]
    assert p["24h"] == 1.0
    assert p["7j"] == 0.6
    assert p["1m"] == 0.2


def test_pertinence_recalibree_petrole_opec_preserve_7j_1m():
    """petrole.yml : opec_production_policy 24h=0.3 ; 7j=0.9, 1m=1.0 PRESERVÉS."""
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    crits = {c["cle_courante"]: c for c in fiches["petrole"]["criteres"]
             if c.get("cle_courante")}
    p = crits["opec_production_policy"]["pertinence"]
    assert p["24h"] == 0.3
    assert p["7j"] == 0.9, "Signal structurel OPEC 7j doit rester 0.9"
    assert p["1m"] == 1.0, "Signal structurel OPEC 1m doit rester 1.0"


def test_pertinence_recalibree_or_geopol():
    """or.yml : tension_geopolitique 24h=1.0 (boost news 24h refonte 23/06, porteur
    net IA ; était 0.5), 7j=0.4, 1m=0.3 préservés."""
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    crits = {c["cle_courante"]: c for c in fiches["or"]["criteres"]
             if c.get("cle_courante")}
    p = crits["tension_geopolitique"]["pertinence"]
    assert p["24h"] == 1.0
    assert p["7j"] == 0.4
    assert p["1m"] == 0.3


def test_pertinence_recalibree_vix_geopol_1m():
    """vix.yml : tension_geopolitique_active 24h=1.0 (boost news 24h refonte 23/06,
    porteur net IA ; était 0.9), 7j=0.6, 1m=0.1 préservés."""
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    crits = {c["cle_courante"]: c for c in fiches["vix"]["criteres"]
             if c.get("cle_courante")}
    p = crits["tension_geopolitique_active"]["pertinence"]
    assert p["24h"] == 1.0
    assert p["7j"] == 0.6
    assert p["1m"] == 0.1


# ---------------------------------------------------------------------------
# Point 4 — ratio_news + news_dominant dans le decision-log
# ---------------------------------------------------------------------------

def test_ratio_news_computed_in_decision_log():
    from datetime import datetime, timezone
    fiche = _fiche()
    vals = _valeurs(quant_val=0.5, news_val=1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    records = sa.build_decision_log_records([res], datetime(2026, 6, 1, tzinfo=timezone.utc))
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert "ratio_news" in rec_24h
    assert "news_dominant" in rec_24h
    # quant=+5, news=+10 → ratio = 10/5 = 2.0 → dominant.
    assert rec_24h["ratio_news"] == pytest.approx(2.0, rel=1e-6)
    assert rec_24h["news_dominant"] is True


def test_news_dominant_false_when_quant_bigger():
    from datetime import datetime, timezone
    fiche = _fiche()
    fiche["criteres"][1]["poids"] = 2  # news plus faible
    vals = _valeurs(quant_val=1.0, news_val=1.0, mat="medium")
    res = sa.score_actif("test", fiche, vals)
    records = sa.build_decision_log_records([res], datetime(2026, 6, 1, tzinfo=timezone.utc))
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    # quant=+10, news=+2 → ratio = 0.2 → pas dominant.
    assert rec_24h["ratio_news"] == pytest.approx(0.2, rel=1e-6)
    assert rec_24h["news_dominant"] is False
