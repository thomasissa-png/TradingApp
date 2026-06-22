"""VOLET B — drapeau ⚠️ « bouge à contre-sens depuis la dernière clôture vue »
pour les actifs CONTINUS de la sélection (décision fondateur 2026-06-15).

ZÉRO réseau : on teste `_build_gap_contresens_flags` directement avec une
sélection et un dict shadow_capteurs in-memory + des fiches minimales.
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

# Fiches minimales : un continu (or) + un non-continu (S&P) — `actif_group` les
# classe via la famille (métaux-précieux=continu, indices=us). On fournit `actif`
# pour ne pas dépendre d'un override par nom.
_FICHES = {
    "or": {"actif": "Or", "famille": "métaux-précieux", "ticker_principal": "GC=F"},
    "sp500": {"actif": "S&P 500", "famille": "indices", "ticker_principal": "^GSPC"},
}


def _sel(fiche_key, actif, direction):
    return {"fiche_key": fiche_key, "actif": actif, "direction": direction}


def test_short_contre_hausse_continu_leve_drapeau():
    """SHORT sur l'or alors que le prix monte de +1.2 % depuis close J-1 → ⚠️."""
    selection = [_sel("or", "Or", "SHORT")]
    shadow = {"or": {"shadow_gap_overnight": 0.012, "shadow_retour_j1": None}}
    flags = sa._build_gap_contresens_flags(selection, shadow, _FICHES)
    assert any("Or" in f and "contre-sens" in f for f in flags)
    assert any("+1.2%" in f for f in flags)


def test_long_contre_baisse_continu_leve_drapeau():
    """LONG alors que ça baisse de -1 % → ⚠️."""
    selection = [_sel("or", "Or", "LONG")]
    shadow = {"or": {"shadow_gap_overnight": -0.010}}
    flags = sa._build_gap_contresens_flags(selection, shadow, _FICHES)
    assert any("Or" in f and "LONG" in f for f in flags)


def test_gap_aligne_aucun_drapeau():
    """LONG ET ça monte → le système voit déjà dans le bon sens → RIEN."""
    selection = [_sel("or", "Or", "LONG")]
    shadow = {"or": {"shadow_gap_overnight": 0.015}}
    flags = sa._build_gap_contresens_flags(selection, shadow, _FICHES)
    assert flags == []


def test_gap_sous_seuil_aucun_drapeau():
    """Mouvement ~0.3 % (< 0.8 %) → anti-bruit → RIEN même si contre-sens."""
    selection = [_sel("or", "Or", "SHORT")]
    shadow = {"or": {"shadow_gap_overnight": 0.003}}
    flags = sa._build_gap_contresens_flags(selection, shadow, _FICHES)
    assert flags == []


def test_actif_non_continu_jamais_de_drapeau():
    """S&P (marché cash fermé à 7h) : close J-1 = dernier prix réel → jamais ⚠️
    même avec un gap énorme à contre-sens."""
    selection = [_sel("sp500", "S&P 500", "SHORT")]
    shadow = {"sp500": {"shadow_gap_overnight": 0.05}}
    flags = sa._build_gap_contresens_flags(selection, shadow, _FICHES)
    assert flags == []


def test_gap_none_aucun_drapeau():
    """gap indisponible (None) → RIEN (zéro invention)."""
    selection = [_sel("or", "Or", "SHORT")]
    shadow = {"or": {"shadow_gap_overnight": None}}
    flags = sa._build_gap_contresens_flags(selection, shadow, _FICHES)
    assert flags == []


def test_pas_de_shadow_capteurs_aucun_drapeau():
    """shadow_capteurs absent → no-op."""
    selection = [_sel("or", "Or", "SHORT")]
    assert sa._build_gap_contresens_flags(selection, None, _FICHES) == []
    assert sa._build_gap_contresens_flags(selection, {}, _FICHES) == []


def test_drapeau_present_dans_le_bloc_complet():
    """Intégration : le drapeau apparaît bien dans build_selection_du_jour_block."""
    # On fabrique un ActifResult minimal sélectionnable (conviction forte simulée
    # via monkeypatch de compute_selection_du_jour pour rester pur/ZÉRO réseau).
    selection = [_sel("or", "Or", "SHORT")]
    shadow = {"or": {"shadow_gap_overnight": 0.012}}

    _orig = sa.compute_selection_du_jour
    sa.compute_selection_du_jour = lambda results, seuil=None, now=None, events_path=None: (
        [{"fiche_key": "or", "actif": "Or", "direction": "SHORT", "note": -0.9,
          "driver_cle": "", "driver_nom": "", "coverage": 0.9}], [])
    try:
        import datetime as _dt
        block = sa.build_selection_du_jour_block(
            [], _dt.datetime(2026, 6, 15, 7, 0),
            shadow_capteurs=shadow, fiches=_FICHES,
        )
    finally:
        sa.compute_selection_du_jour = _orig
    txt = "\n".join(block)
    assert "contre-sens" in txt and "Or" in txt
