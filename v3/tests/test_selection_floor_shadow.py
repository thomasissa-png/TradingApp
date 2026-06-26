"""Tests SHADOW — plancher de conviction sur la sélection réelle (panel 26/06).

Mesure PURE : on retire (en shadow) les paris de la sélection RÉELLE dont la
note NORMALISÉE (intensité comparable entre actifs) est sous le plancher — le cas
Café +0.21 du 26/06. Garde-fous : ne touche NI la sélection réelle, NI le score,
NI la conclusion ; n'écrit que des champs decision-log additifs.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


def _crit(cle: str, poids: float, val: Optional[float] = 1.0) -> sa.CritereResult:
    c = sa.CritereResult(
        id=cle,
        nom=cle,
        type_norm="lineaire",
        valeur_brute=val,
        valeur_norm=val,
        poids=poids,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: 0.0 for h in sa.HORIZONS},
        cle_courante=cle,
    )
    c.is_na = val is None
    return c


def _actif(nom, fiche_key, *, score_24h, direction, criteres) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=fiche_key,
        criteres=criteres,
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (direction if h == "24h" else "") for h in sa.HORIZONS},
        tie_break_notes={},
    )


def _denom15() -> List[sa.CritereResult]:
    # Σ|poids|×pertinence = 15 → note_norm = note_brute / 15.
    return [_crit("c1", 15.0, 1.0)]


def test_plancher_droppe_le_pari_faible():
    """Café +3.15/15 = +0.21 (< 0.30) → DROPPED ; Argent -10/15 = -0.67 → KEPT."""
    cafe = _actif("Café", "cafe", score_24h=3.15, direction="LONG", criteres=_denom15())
    argent = _actif("Argent", "argent", score_24h=-10.0, direction="SHORT", criteres=_denom15())
    petrole = _actif("Pétrole", "petrole", score_24h=-4.5, direction="SHORT", criteres=_denom15())
    res = [cafe, argent, petrole]
    sel = {"cafe", "argent", "petrole"}

    kept, dropped, notes = sa.selection_floor_shadow_map(res, sel)

    assert dropped == {"cafe"}
    assert kept == {"argent", "petrole"}        # -4.5/15 = -0.30 = plancher → gardé
    assert round(notes["cafe"], 2) == 0.21
    assert round(notes["argent"], 2) == -0.67
    assert round(notes["petrole"], 2) == -0.30


def test_pari_non_jugeable_jamais_droppe():
    """note_norm absente (aucun critère couvert → denom 0) → KEPT (zéro invention)."""
    vide = _actif("Vide", "vide", score_24h=0.10, direction="LONG", criteres=[_crit("na", 9.0, None)])
    kept, dropped, notes = sa.selection_floor_shadow_map([vide], {"vide"})
    assert kept == {"vide"}
    assert dropped == set()
    assert "vide" not in notes


def test_cle_absente_des_results_est_gardee():
    kept, dropped, _ = sa.selection_floor_shadow_map([], {"fantome"})
    assert kept == {"fantome"} and dropped == set()


def test_shadow_pur_ne_touche_pas_la_selection():
    """La fonction est lecture seule : scores/conclusions inchangés après appel."""
    cafe = _actif("Café", "cafe", score_24h=3.15, direction="LONG", criteres=_denom15())
    avant_score = dict(cafe.scores)
    avant_concl = dict(cafe.conclusions)
    sa.selection_floor_shadow_map([cafe], {"cafe"})
    assert cafe.scores == avant_score
    assert cafe.conclusions == avant_concl
