"""Tests — chantiers cacao 16/06 (Thomas) : libellés honnêtes, garde-fou
conviction « confiant ET aveugle », détecteur choc d'offre SHADOW.

Couverture :
- ① rename slot maladies_cabosses (fiche YAML) + libellé suivi honnête.
- ③ détecteur choc d'offre cacao SHADOW : champ decision-log présent + bien
  formé + TEST-VERROU « conclusions inchangées » (poids 0 → score/conclusion
  identiques que le détecteur fire ou non).
- ④ garde-fou conviction : « fragile (couverture insuffisante) » quand
  coverage < 0.50 ET critère de poids max n/a ; « forte » sinon.

ZÉRO cutover, ZÉRO impact scoring : on vérifie l'affichage, le shadow et la
non-régression des conclusions.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytest
import yaml

import scoring_analyste as sa

ROOT = Path(__file__).resolve().parents[1]
_NOW = datetime(2026, 6, 16, 7, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fabriques minimales
# ---------------------------------------------------------------------------

def _crit(
    nom: str, cle: str, poids: float, contrib: float, *, is_na: bool = False
) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="lineaire",
        valeur_brute=None if is_na else 1.0,
        valeur_norm=None if is_na else 1.0,
        poids=poids,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: (0.0 if is_na else contrib) for h in sa.HORIZONS},
        cle_courante=cle,
        is_na=is_na,
    )


def _actif_cacao(
    *, score_24h: float, coverage: float, max_weight_na: bool
) -> sa.ActifResult:
    """Cacao 24h SHORT « forte »-éligible (|score| élevé, pas de drapeau).

    `max_weight_na` : le critère de poids max (« Arrivées ports », poids 9) est
    n/a (cas réel 16/06) ou présent.
    """
    # Critère de poids MAX = arrivées ports (poids 9).
    arrivees = _crit("Arrivées ports", "arrivees_port", 9.0, -0.4, is_na=max_weight_na)
    # 3 critères présents à contributions ÉGALES → aucun ne dépasse 50 % (pas mono).
    momentum = _crit("Tendance cacao", "momentum_prix_20j_cacao", 6.0, -0.4)
    autre = _crit("HF positioning", "hf_positioning_flux_options", 5.0, -0.4)
    autre2 = _crit("EUDR", "eudr", 5.0, -0.4)
    criteres = [arrivees, momentum, autre, autre2]
    return sa.ActifResult(
        nom="Cacao",
        fiche_key="cacao",
        criteres=criteres,
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: ("SHORT" if h == "24h" else sa.CONCLUSION_INSUFFISANT) for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=coverage,
        confidence={h: "faible" for h in sa.HORIZONS},
    )


# ---------------------------------------------------------------------------
# ① Libellés honnêtes
# ---------------------------------------------------------------------------

def test_fiche_cacao_slot_nom_thematique_reel():
    """RÉCONCILIATION 16/06 (libellé dynamique) : le slot maladies_cabosses est à
    DOUBLE CASQUETTE. Son NOM DE FICHE est désormais son VRAI thème keyword
    (« Maladies des cabosses », cohérent signe +1 = offre↓ = haussier) ; le
    libellé « Synthèse news (net, IA) » est appliqué DYNAMIQUEMENT au rendu quand
    le créneau porte le net (cf. test_libelle_dynamique_*). L'ancien nom statique
    « Synthèse news cacao (net, IA) » était FAUX en mode keyword → revert."""
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "cacao.yml").read_text("utf-8"))
    slot = next(c for c in fiche["criteres"] if c.get("cle_courante") == "maladies_cabosses")
    # cle_courante INCHANGÉE (L023), signe/poids INCHANGÉS (zéro modif silencieuse).
    assert slot["cle_courante"] == "maladies_cabosses"
    assert slot["signe"] == 1
    assert slot["poids"] == 4
    # Le nom de fiche = thème keyword réel (cohérent avec signe +1, mode keyword).
    assert "Maladies des cabosses" in slot["nom"]


def test_libelle_dynamique_porte_le_net():
    """Un critère news dont le source_track porte le net (ia_synthese /
    ia_synthese_faible) s'affiche « Synthèse news (net, IA) », quel que soit son
    nom de fiche — uniforme pour TOUS les actifs."""
    assert sa._nom_affiche("Maladies des cabosses (impact récolte)", "ia_synthese") == sa.SYNTHESE_NET_LABEL
    assert sa._nom_affiche("Grèves minières Chili/Pérou", "ia_synthese_faible") == sa.SYNTHESE_NET_LABEL
    assert sa._nom_affiche("Géopolitique Iran", "IA_SYNTHESE") == sa.SYNTHESE_NET_LABEL  # casse insensible
    assert "synth" in sa.SYNTHESE_NET_LABEL.lower()


def test_libelle_dynamique_mode_keyword_garde_le_theme():
    """En mode keyword (détection mots-clés thématique) le créneau garde son nom
    de fiche — pas de « Synthèse news »."""
    assert sa._nom_affiche("Maladies des cabosses (impact récolte)", "keyword") == "Maladies des cabosses (impact récolte)"
    assert sa._nom_affiche("Grèves minières Chili/Pérou", "keyword") == "Grèves minières Chili/Pérou"


def test_libelle_dynamique_degrade_proprement():
    """source_track absent / inconnu / non-news → nom de fiche (legacy), jamais
    de crash (vieux decision-logs, critères quant)."""
    assert sa._nom_affiche("Météo CI+Ghana", "") == "Météo CI+Ghana"
    assert sa._nom_affiche("Météo CI+Ghana", "none") == "Météo CI+Ghana"
    assert sa._nom_affiche("Météo CI+Ghana", "calendrier") == "Météo CI+Ghana"
    assert sa._nom_affiche("Météo CI+Ghana", "ia_conflict") == "Météo CI+Ghana"
    assert sa._nom_affiche("Météo CI+Ghana", None) == "Météo CI+Ghana"  # type: ignore[arg-type]


def test_cacao_16_06_net_short_plus_de_non_sens():
    """Cas cacao 16/06 (net SHORT) : le slot maladies_cabosses porté par le net
    ne s'affiche PLUS « Maladies des cabosses → baissier » (non-sens : maladie =
    haussier), mais « Synthèse news (net, IA) → baissier » (cohérent)."""
    affiche = sa._nom_affiche("Maladies des cabosses (impact récolte)", "ia_synthese")
    assert "Maladies des cabosses" not in affiche
    assert affiche == sa.SYNTHESE_NET_LABEL


def test_suivi_libelle_news_honnete():
    """run_suivi n'affiche plus « News à impact depuis 7h » (impliquait une
    réactualisation) mais un libellé honnête « non réactualisé »."""
    src = (ROOT / "scripts" / "run_suivi.py").read_text("utf-8")
    # Le titre rendu (string littérale du L.append) ne contient plus l'ancien libellé.
    assert 'L.append(f"### News à impact depuis' not in src
    assert "non réactualisé" in src


# ---------------------------------------------------------------------------
# ④ Garde-fou conviction « confiant ET aveugle »
# ---------------------------------------------------------------------------

def test_conviction_degradee_si_couverture_basse_et_max_weight_na():
    """coverage < 0.50 ET critère de poids max n/a → « fragile (couverture
    insuffisante) », jamais « forte ». Direction conservée (cellule reste SHORT)."""
    r = _actif_cacao(score_24h=-1.78, coverage=0.41, max_weight_na=True)
    conv = sa._conviction_cell(r, "24h", seuil=0.6)
    assert conv == "fragile (couverture insuffisante)"
    # La DIRECTION reste notée (jamais neutre).
    assert r.conclusions["24h"] == "SHORT"


def test_conviction_forte_si_couverture_basse_mais_max_weight_present():
    """Le garde-fou ne se déclenche QUE si le critère de poids max est n/a.
    S'il est présent, conviction « forte » normale (couverture basse seule ne
    suffit pas — c'est le rôle du palier confidence, pas de ce garde-fou)."""
    r = _actif_cacao(score_24h=-1.78, coverage=0.41, max_weight_na=False)
    assert sa._conviction_cell(r, "24h", seuil=0.6) == "forte"


def test_conviction_forte_si_couverture_suffisante_meme_max_weight_na():
    """coverage ≥ 0.50 → pas de dégradation même si le max-weight est n/a (le
    seuil garde-fou est 0.50, distinct de COVERAGE_OK)."""
    r = _actif_cacao(score_24h=-1.78, coverage=0.55, max_weight_na=True)
    assert sa._conviction_cell(r, "24h", seuil=0.6) == "forte"


def test_max_weight_critere_is_na_helper():
    r_na = _actif_cacao(score_24h=-1.0, coverage=0.41, max_weight_na=True)
    r_ok = _actif_cacao(score_24h=-1.0, coverage=0.41, max_weight_na=False)
    assert sa._max_weight_critere_is_na(r_na) is True
    assert sa._max_weight_critere_is_na(r_ok) is False


# ---------------------------------------------------------------------------
# ③ Détecteur choc d'offre SHADOW
# ---------------------------------------------------------------------------

def _ev(L1: str, *, zone: str = "CI", dt: Optional[datetime] = None) -> dict:
    return {
        "L1": L1, "L2": "", "trigger": "", "cours": "cocoa",
        "news_zone": zone, "_canonical_dt": dt or _NOW,
    }


def test_choc_offre_detecte_signal_offre_haussier():
    events = [_ev("El Nino threatens West Africa cocoa harvest, ICCO deficit looms")]
    res = sa.compute_shadow_choc_offre_cacao(events=events, now=_NOW)
    assert res["detected"] is True
    assert res["direction"] == 1
    assert res["n_events"] >= 1
    assert res["would_be_contrib"] == 0.0  # SHADOW poids 0
    assert any("el nino" in k or "deficit" in k for k in res["keywords"])


def test_choc_offre_negateur_annule():
    events = [_ev("Bumper crop expected, favorable weather, healthy cocoa harvest")]
    res = sa.compute_shadow_choc_offre_cacao(events=events, now=_NOW)
    assert res["detected"] is False
    assert res["direction"] == 0
    assert res["negators"] >= 1


def test_choc_offre_vide_si_aucun_event():
    res = sa.compute_shadow_choc_offre_cacao(events=[], now=_NOW)
    assert res == {
        "detected": False, "direction": 0, "n_events": 0,
        "negators": 0, "keywords": [], "would_be_contrib": 0.0,
    }


def test_choc_offre_ignore_event_hors_cacao():
    events = [_ev("El Nino hits Brazil coffee crop", zone="BR")]
    # cours/zone non-cacao → ignoré (pas de pollution café/sucre).
    res = sa.compute_shadow_choc_offre_cacao(
        events=[{**events[0], "cours": "coffee"}], now=_NOW,
    )
    assert res["detected"] is False


# ---------------------------------------------------------------------------
# TEST-VERROU ③ — conclusions INCHANGÉES (poids 0, L015)
# ---------------------------------------------------------------------------

def test_verrou_shadow_choc_offre_conclusions_inchangees(monkeypatch):
    """Le détecteur choc d'offre est SHADOW : que le scan retourne detected=True
    ou False, le score et la conclusion du record cacao 24h sont IDENTIQUES.

    On compare deux builds du decision-log avec le même ActifResult, en forçant
    le scan à fire puis à ne pas fire. Aucune divergence score/conclusion."""
    r = _actif_cacao(score_24h=-1.78, coverage=0.41, max_weight_na=True)

    def _fire(*a, **k):
        return {"detected": True, "direction": 1, "n_events": 3,
                "negators": 0, "keywords": ["el nino"], "would_be_contrib": 0.0}

    def _silent(*a, **k):
        return {"detected": False, "direction": 0, "n_events": 0,
                "negators": 0, "keywords": [], "would_be_contrib": 0.0}

    monkeypatch.setattr(sa, "compute_shadow_choc_offre_cacao", _fire)
    rec_fire = next(
        x for x in sa.build_decision_log_records([r], _NOW) if x["horizon"] == "24h"
    )
    monkeypatch.setattr(sa, "compute_shadow_choc_offre_cacao", _silent)
    rec_silent = next(
        x for x in sa.build_decision_log_records([r], _NOW) if x["horizon"] == "24h"
    )

    # Conclusion + score STRICTEMENT identiques (le shadow ne touche RIEN).
    assert rec_fire["conclusion_pm1"] == rec_silent["conclusion_pm1"] == "SHORT"
    assert rec_fire["score_pm1"] == rec_silent["score_pm1"]
    # Le champ shadow est bien présent et reflète l'état du détecteur (observabilité).
    assert rec_fire["shadow_choc_offre"]["detected"] is True
    assert rec_silent["shadow_choc_offre"]["detected"] is False
    # Le shadow ne porte JAMAIS de contribution (poids 0).
    assert rec_fire["shadow_choc_offre"]["would_be_contrib"] == 0.0


def test_shadow_choc_offre_present_seulement_pour_cacao():
    """Le champ shadow_choc_offre n'est posé que sur cacao (zéro bruit ailleurs)."""
    r_cacao = _actif_cacao(score_24h=-1.0, coverage=0.41, max_weight_na=True)
    r_autre = sa.ActifResult(
        nom="Or", fiche_key="or",
        criteres=[_crit("c", "c", 5.0, 0.5)],
        scores={h: (1.0 if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: ("LONG" if h == "24h" else sa.CONCLUSION_INSUFFISANT) for h in sa.HORIZONS},
        tie_break_notes={},
        coverage=0.8,
        confidence={h: "normale" for h in sa.HORIZONS},
    )
    records = sa.build_decision_log_records([r_cacao, r_autre], _NOW)
    cacao_24h = next(x for x in records if x["fiche_key"] == "cacao" and x["horizon"] == "24h")
    or_24h = next(x for x in records if x["fiche_key"] == "or" and x["horizon"] == "24h")
    assert "shadow_choc_offre" in cacao_24h
    assert "shadow_choc_offre" not in or_24h
