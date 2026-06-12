"""Tests — « 🎯 Sélection du jour — max 3 » + capteurs shadow 24h (décision
fondateur 12/06). ZÉRO cutover : on vérifie l'affichage + la mesure + le shadow,
JAMAIS un changement de score/conclusion.

Couverture :
- règles de sélection (forte + couverture ≥ 0.70 + dédup driver + max 3) ;
- cas « aucune sélection » ;
- champs decision-log (selection_du_jour / selection_motif_exclusion) ;
- shadow_retour_j1 / shadow_gap_overnight calculés et None propres ;
- WR Sélection au bilan (synthétique) ;
- avertissement catalyseur J0.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

import pytest

import scoring_analyste as sa


# ---------------------------------------------------------------------------
# Fabriques minimales (zéro dépendance réseau / YAML)
# ---------------------------------------------------------------------------

def _crit(nom: str, cle: str, contrib: float, h_contrib: Optional[Dict[str, float]] = None) -> sa.CritereResult:
    contributions = h_contrib or {h: contrib for h in sa.HORIZONS}
    return sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="lineaire",
        valeur_brute=1.0,
        valeur_norm=1.0,
        poids=5.0,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions=contributions,
        cle_courante=cle,
    )


def _actif(
    nom: str,
    fiche_key: str,
    *,
    score_24h: float,
    direction: str = "LONG",
    coverage: float = 1.0,
    driver_cle: str = "drv_a",
    driver_nom: str = "Critère A",
) -> sa.ActifResult:
    """ActifResult dont la cellule 24h est « forte ».

    Trois critères : le driver attendu est STRICTEMENT le plus contributeur (top
    déterministe) mais reste sous 50 % du total → ni mono-dominant (pas
    « fragile »), ni quasi-neutre si |score| ≥ seuil → conviction « forte »."""
    c_top = _crit(driver_nom, driver_cle, 0.40)
    c_b = _crit("autre b", "drv_b", 0.33)
    c_c = _crit("autre c", "drv_c", 0.33)
    return sa.ActifResult(
        nom=nom,
        fiche_key=fiche_key,
        criteres=[c_top, c_b, c_c],
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (direction if h == "24h" else sa.CONCLUSION_INSUFFISANT) for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=coverage,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


_NOW = datetime(2026, 6, 12, 7, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Règles de sélection
# ---------------------------------------------------------------------------

def test_selection_garde_forte_couverture_ok():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    sel, ecart = sa.compute_selection_du_jour([a])
    assert [s["fiche_key"] for s in sel] == ["or"]
    assert ecart == []


def test_selection_exclut_couverture_insuffisante():
    # |note| forte mais couverture 0.69 < 0.70 → écartée (pas dans la sélection).
    a = _actif("Or", "or", score_24h=0.9, coverage=0.69)
    sel, _ = sa.compute_selection_du_jour([a])
    assert sel == []


def test_selection_exclut_conviction_non_forte():
    # |note| sous le seuil (0.6) → conviction « molle » → exclue.
    a = _actif("Or", "or", score_24h=0.4)
    assert sa._conviction_cell(a, "24h", 0.6) != "forte"
    sel, _ = sa.compute_selection_du_jour([a])
    assert sel == []


def test_selection_dedup_meme_driver_meme_direction():
    # Deux actifs LONG sur le même driver → on garde la plus forte, l'autre écartée.
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_macro", driver_nom="Fed")
    faible = _actif("Argent", "argent", score_24h=0.7, driver_cle="drv_macro", driver_nom="Fed")
    sel, ecart = sa.compute_selection_du_jour([fort, faible])
    assert [s["fiche_key"] for s in sel] == ["or"]
    assert len(ecart) == 1
    assert ecart[0]["fiche_key"] == "argent"
    assert "même pari que Or" in ecart[0]["motif"]


def test_selection_pas_de_dedup_si_direction_opposee():
    # Même driver mais directions opposées → ce N'EST PAS le même pari.
    a = _actif("Or", "or", score_24h=0.9, direction="LONG", driver_cle="drv_macro")
    b = _actif("Argent", "argent", score_24h=-0.9, direction="SHORT", driver_cle="drv_macro")
    sel, ecart = sa.compute_selection_du_jour([a, b])
    assert {s["fiche_key"] for s in sel} == {"or", "argent"}
    assert ecart == []


def test_selection_max_3():
    actifs = [
        _actif(f"A{i}", f"a{i}", score_24h=0.9 - i * 0.01, driver_cle=f"drv_{i}")
        for i in range(5)
    ]
    sel, ecart = sa.compute_selection_du_jour(actifs)
    assert len(sel) == 3
    # Les 2 surnuméraires sont « hors top 3 ».
    assert all(e["motif"] == "hors top 3" for e in ecart)
    assert len(ecart) == 2


def test_selection_tri_note_decroissante():
    a = _actif("Faible", "f", score_24h=0.65, driver_cle="d1")
    b = _actif("Fort", "fo", score_24h=0.95, driver_cle="d2")
    sel, _ = sa.compute_selection_du_jour([a, b])
    assert [s["fiche_key"] for s in sel] == ["fo", "f"]


def test_selection_aucune_si_rien_ne_passe():
    a = _actif("Or", "or", score_24h=0.4)  # molle
    b = _actif("Argent", "argent", score_24h=0.9, coverage=0.5)  # couverture KO
    sel, _ = sa.compute_selection_du_jour([a, b])
    assert sel == []


# ---------------------------------------------------------------------------
# Bloc bulletin
# ---------------------------------------------------------------------------

def test_bloc_aucune_selection_message():
    a = _actif("Or", "or", score_24h=0.4)
    lignes = sa.build_selection_du_jour_block([a], _NOW)
    texte = "\n".join(lignes)
    assert "## 🎯 Sélection du jour — max 3" in texte
    assert "Aucune sélection aujourd'hui" in texte
    assert "ne pas forcer" in texte


def test_bloc_tableau_et_ecartee(monkeypatch):
    # On neutralise le calendrier (J0) pour isoler le rendu du tableau/dédup.
    monkeypatch.setattr(sa, "_catalyseurs_j0_high", lambda now: [])
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_macro", driver_nom="Fed")
    faible = _actif("Argent", "argent", score_24h=0.7, driver_cle="drv_macro", driver_nom="Fed")
    lignes = sa.build_selection_du_jour_block(
        [fort, faible], _NOW, prix_reference={"or": 2400.0},
    )
    texte = "\n".join(lignes)
    assert "| Or | LONG | +0.90 | Fed | 2400 |" in texte
    assert "écartée : Argent — même pari que Or" in texte
    # Intro : les 4 règles en clair.
    assert "conviction **forte**" in texte
    assert "un seul pari par driver" in texte


def test_bloc_avertissement_catalyseur_j0(monkeypatch):
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")

    def _fake_cat(now):
        return [{"nom": "Inflation US (CPI)", "actifs": ["or"], "impact": "high"}]

    monkeypatch.setattr(sa, "_catalyseurs_j0_high", _fake_cat)
    lignes = sa.build_selection_du_jour_block([fort], _NOW)
    texte = "\n".join(lignes)
    assert "⚠️" in texte
    assert "Inflation US (CPI) aujourd'hui" in texte
    assert "peut retourner ce pari" in texte
    assert "Or" in texte


def test_bloc_catalyseur_ignore_si_actif_non_selectionne(monkeypatch):
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")

    def _fake_cat(now):
        # CPI concerne sp500, PAS l'or sélectionné → aucun avertissement.
        return [{"nom": "Inflation US (CPI)", "actifs": ["sp500"], "impact": "high"}]

    monkeypatch.setattr(sa, "_catalyseurs_j0_high", _fake_cat)
    texte = "\n".join(sa.build_selection_du_jour_block([fort], _NOW))
    assert "⚠️" not in texte


# ---------------------------------------------------------------------------
# Decision-log (Étage 1b)
# ---------------------------------------------------------------------------

def test_decision_log_selection_du_jour_true():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["selection_du_jour"] is True
    assert "selection_motif_exclusion" not in rec_24h
    # Hors 24h : champ absent (la sélection est définie sur le pari 24h).
    rec_7j = next(r for r in records if r["horizon"] == "7j")
    assert "selection_du_jour" not in rec_7j


def test_decision_log_selection_motif_exclusion():
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_macro", driver_nom="Fed")
    faible = _actif("Argent", "argent", score_24h=0.7, driver_cle="drv_macro", driver_nom="Fed")
    records = sa.build_decision_log_records([fort, faible], _NOW)
    rec_or = next(r for r in records if r["actif"] == "Or" and r["horizon"] == "24h")
    rec_ag = next(r for r in records if r["actif"] == "Argent" and r["horizon"] == "24h")
    assert rec_or["selection_du_jour"] is True
    assert rec_ag["selection_du_jour"] is False
    assert "même pari que Or" in rec_ag["selection_motif_exclusion"]


def test_decision_log_selection_false_quand_non_selectionnee():
    a = _actif("Or", "or", score_24h=0.4)  # molle → non sélectionnée
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["selection_du_jour"] is False


# ---------------------------------------------------------------------------
# Capteurs shadow 24h (Étage 2)
# ---------------------------------------------------------------------------

def test_shadow_capteurs_calcul():
    fiches = {"or": {"ticker_principal": "XAU"}}

    def _fake_series(symbol, outputsize=10):
        # oldest→newest : [-2]=close J-2=100, [-1]=close J-1=110.
        return [
            (datetime(2026, 6, 10, tzinfo=timezone.utc), 100.0),
            (datetime(2026, 6, 11, tzinfo=timezone.utc), 110.0),
        ]

    caps = sa.compute_shadow_capteurs(
        fiches, prix_emission={"XAU": 121.0}, fetch_series=_fake_series,
    )
    # retour_j1 = 110/100 - 1 = 0.10 ; gap = 121/110 - 1 = 0.10.
    assert caps["or"]["shadow_retour_j1"] == pytest.approx(0.10)
    assert caps["or"]["shadow_gap_overnight"] == pytest.approx(0.10)


def test_shadow_capteurs_none_propres():
    fiches = {"or": {"ticker_principal": "XAU"}}

    # Série indisponible → retour_j1 None ; pas de prix émission → gap None.
    caps = sa.compute_shadow_capteurs(
        fiches, prix_emission={}, fetch_series=lambda s, outputsize=10: None,
    )
    assert caps["or"]["shadow_retour_j1"] is None
    assert caps["or"]["shadow_gap_overnight"] is None


def test_shadow_capteurs_gap_none_si_close_manque():
    fiches = {"or": {"ticker_principal": "XAU"}}
    # Une seule bougie → pas de J-2 → retour_j1 None ; close J-1 connu → gap OK.
    caps = sa.compute_shadow_capteurs(
        fiches,
        prix_emission={"XAU": 121.0},
        fetch_series=lambda s, outputsize=10: [
            (datetime(2026, 6, 11, tzinfo=timezone.utc), 110.0)
        ],
    )
    assert caps["or"]["shadow_retour_j1"] is None
    assert caps["or"]["shadow_gap_overnight"] == pytest.approx(0.10)


def test_decision_log_shadow_injecte():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    shadow = {"or": {"shadow_retour_j1": 0.05, "shadow_gap_overnight": -0.02}}
    records = sa.build_decision_log_records([a], _NOW, shadow_capteurs=shadow)
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["shadow_retour_j1"] == pytest.approx(0.05)
    assert rec_24h["shadow_gap_overnight"] == pytest.approx(-0.02)


def test_decision_log_shadow_none_si_absent():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    records = sa.build_decision_log_records([a], _NOW)  # pas de shadow_capteurs
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["shadow_retour_j1"] is None
    assert rec_24h["shadow_gap_overnight"] is None


# ---------------------------------------------------------------------------
# WR Sélection au bilan (Étage 1c, synthétique)
# ---------------------------------------------------------------------------

class _FakeCell:
    def __init__(self, actif_name: str):
        self.actif_name = actif_name


class _FakeMeasure:
    def __init__(self, actif: str, horizon: str, outcome: str):
        self.cell = _FakeCell(actif)
        self.horizon = horizon
        self.outcome = outcome


def test_win_rate_selection_compte_vrai_fausse():
    import bilan_jour as bj
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE, OUTCOME_NC

    measures = [
        _FakeMeasure("Or", "24h", OUTCOME_VRAI),
        _FakeMeasure("Argent", "24h", OUTCOME_FAUSSE),
        _FakeMeasure("Cuivre", "24h", OUTCOME_VRAI),  # non sélectionné → ignoré
        _FakeMeasure("Or", "24h", OUTCOME_NC),         # NC → exclu du WR
    ]
    selection_map = {("Or", "24h"): True, ("Argent", "24h"): True, ("Cuivre", "24h"): False}
    wr = bj.win_rate_selection(measures, selection_map)
    assert wr.n_select == 2
    assert wr.n_vrai_select == 1
    assert wr.taux == pytest.approx(50.0)


def test_win_rate_selection_vide():
    import bilan_jour as bj
    wr = bj.win_rate_selection([], {})
    assert wr.n_select == 0
    assert wr.taux is None
