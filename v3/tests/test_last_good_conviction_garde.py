"""Test — garde-fou conviction sur valeur reportée (panel 3 experts 2026-06-25).

Règle : si le DRIVER DOMINANT d'une cellule est une valeur REPORTÉE depuis le
cache last-good (source réseau KO), la conviction est plafonnée à « contestée »
(une valeur reportée ne peut pas porter une conviction « forte » à elle seule).
Si le critère reporté n'est PAS le driver dominant (cas cacao : driver = news
El Niño vivante), la conviction « forte » est conservée.

On pilote le scoring réel (`score_actif`) avec des `valeurs_actif` synthétiques :
un critère porte un drapeau `reporte: True` (comme le poserait le fallback du
chokepoint build_critere_value), l'autre est une valeur vivante.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 6, 25, 5, 0, tzinfo=timezone.utc)
PERT = {"24h": 1.0, "7j": 1.0, "1m": 1.0}


def _fiche(poids_meteo: float, poids_news: float) -> dict:
    """Fiche cacao : météo (reportable) + news + un 3e critère, pour qu'AUCUN seul
    critère ne porte >50% du score (sinon le flag mono-critère ◧ préempte, ce qui
    n'est pas l'objet du test). Les poids déterminent le driver DOMINANT.
    """
    return {
        "nom": "Cacao",
        "criteres": [
            {"id": 1, "nom": "Météo CI/Ghana", "cle_courante": "meteo_ci_ghana_precip_30j",
             "normalisation": "zscore_abs", "poids": poids_meteo, "signe": 1,
             "pertinence": PERT, "cap": 1.0},
            {"id": 2, "nom": "Offre El Niño", "cle_courante": "offre_el_nino",
             "normalisation": "zscore", "poids": poids_news, "signe": 1,
             "pertinence": PERT, "cap": 1.0},
            {"id": 3, "nom": "Positionnement HF", "cle_courante": "hf_positioning_cacao",
             "normalisation": "zscore", "poids": 6, "signe": 1,
             "pertinence": PERT, "cap": 1.0},
        ],
    }


def _valeurs(meteo_reporte: bool) -> dict:
    """Valeurs résolues : météo (reportée ou vivante) + 2 critères vivants, toutes
    LONG (valeur_normalisee > 0) pour un score franc, sans mono-dominance."""
    meteo = {"valeur": 0.357, "valeur_normalisee": 0.9, "valeur_ponderee": 0.9,
             "ts": NOW.isoformat()}
    if meteo_reporte:
        meteo.update({"reporte": True, "reporte_age_j": 3,
                      "reporte_cause": "Open-Meteo injoignable (récents)"})
    return {
        "meteo_ci_ghana_precip_30j": meteo,
        "offre_el_nino": {"valeur": 0.8, "valeur_normalisee": 0.9,
                          "valeur_ponderee": 0.9, "ts": NOW.isoformat()},
        "hf_positioning_cacao": {"valeur": 0.7, "valeur_normalisee": 0.8,
                                 "valeur_ponderee": 0.8, "ts": NOW.isoformat()},
    }


def test_driver_dominant_reporte_plafonne_a_contestee():
    """Météo reportée + météo = driver dominant (poids fort) → conviction plafonnée."""
    fiche = _fiche(poids_meteo=11, poids_news=6)
    r = sa.score_actif("cacao", fiche, _valeurs(meteo_reporte=True), now=NOW)
    # Sanity : direction franche + couverture pleine (les 2 critères présents).
    assert r.conclusions["24h"] == "LONG"
    assert r.coverage >= sa.CONVICTION_COVERAGE_MIN
    conv = sa._conviction_cell(r, "24h", seuil=0.6)
    assert conv == "contestée (donnée reportée)", conv


def test_driver_dominant_vivant_garde_forte():
    """Météo reportée MAIS news (vivante) = driver dominant (poids fort) → la
    conviction « forte » est conservée (cas cacao réel : driver = news El Niño)."""
    fiche = _fiche(poids_meteo=6, poids_news=11)
    r = sa.score_actif("cacao", fiche, _valeurs(meteo_reporte=True), now=NOW)
    assert r.conclusions["24h"] == "LONG"
    conv = sa._conviction_cell(r, "24h", seuil=0.6)
    assert conv == "forte", conv


def test_meteo_reportee_compte_dans_couverture():
    """Une valeur reportée n'est PAS n/a : elle compte à plein poids dans la
    couverture (le but du fallback : débloquer la sélection)."""
    fiche = _fiche(poids_meteo=11, poids_news=3)
    # Avec report : couverture pleine.
    r_rep = sa.score_actif("cacao", fiche, _valeurs(meteo_reporte=True), now=NOW)
    # Sans la météo du tout (n/a) : couverture amputée du poids 11.
    val_na = {"offre_el_nino": {"valeur": 0.8, "valeur_normalisee": 0.8,
                                "valeur_ponderee": 0.8, "ts": NOW.isoformat()}}
    r_na = sa.score_actif("cacao", fiche, val_na, now=NOW)
    assert r_rep.coverage > r_na.coverage
    # Le critère reporté est bien marqué (échec visible) et non n/a.
    crit_meteo = next(c for c in r_rep.criteres if c.cle_courante == "meteo_ci_ghana_precip_30j")
    assert crit_meteo.reporte is True
    assert crit_meteo.is_na is False


def test_drapeau_reportee_dans_les_flags():
    """Le drapeau ⚠️♻ apparaît dans les flags de surveillance de la cellule."""
    fiche = _fiche(poids_meteo=11, poids_news=3)
    r = sa.score_actif("cacao", fiche, _valeurs(meteo_reporte=True), now=NOW)
    flags = sa._compute_cell_risk_flags(r, "24h", NOW)
    assert sa.SURVEILLANCE_FLAGS["reportee"] in flags
