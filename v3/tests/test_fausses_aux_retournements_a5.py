"""Tests A5 — métrique shadow « FAUSSES aux retournements » (bilan_jour).

Audit momentum-family 10/06, amendement A5 : métrique d'OBSERVABILITÉ distincte
du win rate qui compte les conclusions FAUSSES sur les cellules « en situation de
retournement » (cap anti-inversion déclenché OU news opposées au quant
hors-momentum). WIN RATE ONLY, mode shadow : aucun impact scoring/conclusions.

Synthétiques purs : aucun fichier decision-log réel n'est lu.
"""

from __future__ import annotations

from types import SimpleNamespace

import bilan_jour as B
import journaliste as J


# --------------------------------------------------------------------------
# is_reversal_context — R1 (cap déclenché) / R2 (signes opposés) / indéterminé
# --------------------------------------------------------------------------

def test_r1_cap_applied_true_est_retournement():
    """R1 : le cap anti-inversion a mordu → retournement avéré."""
    rec = {"news_cap_applied": True, "news_total": 0.0, "cap_quant_ex_momentum": 0.0}
    assert B.is_reversal_context(rec) is True


def test_r2_news_positives_quant_negatif_est_retournement():
    """R2 : news > 0 et quant (hors momentum) < 0 → désaccord directionnel."""
    rec = {"news_cap_applied": False, "news_total": 2.5, "cap_quant_ex_momentum": -1.8}
    assert B.is_reversal_context(rec) is True


def test_r2_news_negatives_quant_positif_est_retournement():
    rec = {"news_cap_applied": False, "news_total": -3.0, "cap_quant_ex_momentum": 1.2}
    assert B.is_reversal_context(rec) is True


def test_signes_concordants_pas_retournement():
    """News et quant dans le MÊME sens → pas de retournement."""
    rec = {"news_cap_applied": False, "news_total": 2.0, "cap_quant_ex_momentum": 1.5}
    assert B.is_reversal_context(rec) is False


def test_un_signe_nul_pas_retournement():
    """Si l'un est nul (pas de désaccord strict) → pas de retournement."""
    rec = {"news_cap_applied": False, "news_total": 0.0, "cap_quant_ex_momentum": 1.5}
    assert B.is_reversal_context(rec) is False


def test_champs_absents_indetermine():
    """Champs R2 absents et cap inconnu → None (exclu de la métrique, zéro invention)."""
    assert B.is_reversal_context({}) is None
    assert B.is_reversal_context({"news_total": 1.0}) is None  # quant manquant


def test_cap_false_sans_donnees_r2_est_non_retournement():
    """cap explicitement False mais R2 inexploitable → False (pas de retournement)."""
    rec = {"news_cap_applied": False}
    assert B.is_reversal_context(rec) is False


# --------------------------------------------------------------------------
# fausses_aux_retournements — agrégation sur mesures + reversal_map
# --------------------------------------------------------------------------

def _measure(actif, horizon, outcome):
    cell = SimpleNamespace(actif_name=actif, horizon=horizon)
    return SimpleNamespace(cell=cell, horizon=horizon, outcome=outcome)


def test_fausse_en_retournement_comptee():
    """Une cellule FAUSSE taguée retournement est comptée au numérateur ET dénominateur."""
    measures = [_measure("Cacao", "24h", J.OUTCOME_FAUSSE)]
    rmap = {("Cacao", "24h"): True}
    agg = B.fausses_aux_retournements(measures, rmap)
    assert agg.n_retournement == 1
    assert agg.n_fausse_retournement == 1
    assert agg.taux_fausses == 100.0


def test_vrai_en_retournement_compte_au_denominateur_seulement():
    """VRAI en retournement : dénominateur +1, numérateur inchangé."""
    measures = [_measure("Or", "24h", J.OUTCOME_VRAI)]
    rmap = {("Or", "24h"): True}
    agg = B.fausses_aux_retournements(measures, rmap)
    assert agg.n_retournement == 1
    assert agg.n_fausse_retournement == 0
    assert agg.taux_fausses == 0.0


def test_fausse_hors_retournement_non_comptee():
    """Une FAUSSE NON taguée retournement n'entre PAS dans la métrique."""
    measures = [_measure("Petrole", "24h", J.OUTCOME_FAUSSE)]
    rmap = {("Petrole", "24h"): False}   # tag = pas en retournement
    agg = B.fausses_aux_retournements(measures, rmap)
    assert agg.n_retournement == 0
    assert agg.n_fausse_retournement == 0
    assert agg.taux_fausses is None


def test_cellule_indeterminee_absente_du_map_exclue():
    """Cellule absente du reversal_map (indéterminée) → exclue (zéro invention)."""
    measures = [_measure("Cuivre", "24h", J.OUTCOME_FAUSSE)]
    agg = B.fausses_aux_retournements(measures, {})  # rien dans le map
    assert agg.n_retournement == 0
    assert agg.taux_fausses is None


def test_non_conclusif_jamais_compte():
    """Une cellule NC (non conclusive) en retournement n'est pas comptée."""
    measures = [_measure("Argent", "24h", J.OUTCOME_NC)]
    rmap = {("Argent", "24h"): True}
    agg = B.fausses_aux_retournements(measures, rmap)
    assert agg.n_retournement == 0
    assert agg.taux_fausses is None


def test_mix_realiste():
    """3 retournements (2 FAUSSES, 1 VRAI) + bruit hors-périmètre → 2/3 = 66.7%."""
    measures = [
        _measure("Cacao", "24h", J.OUTCOME_FAUSSE),    # retournement, FAUSSE
        _measure("Petrole", "24h", J.OUTCOME_FAUSSE),  # retournement, FAUSSE
        _measure("Or", "24h", J.OUTCOME_VRAI),         # retournement, VRAI
        _measure("Nasdaq", "24h", J.OUTCOME_FAUSSE),   # hors retournement (False)
        _measure("Cuivre", "24h", J.OUTCOME_VRAI),     # indéterminé (absent du map)
    ]
    rmap = {
        ("Cacao", "24h"): True,
        ("Petrole", "24h"): True,
        ("Or", "24h"): True,
        ("Nasdaq", "24h"): False,
    }
    agg = B.fausses_aux_retournements(measures, rmap)
    assert agg.n_retournement == 3
    assert agg.n_fausse_retournement == 2
    assert agg.taux_fausses == 66.7
