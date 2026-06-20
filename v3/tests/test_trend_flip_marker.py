"""Tests ciblés — marqueur « changement de tendance » (⇌) dans la grille « ## Synthèse des décisions ».

Sémantique (validée Thomas, session 9) : une cellule (actif × horizon) reçoit le
glyphe ⇌ en TÊTE de cellule si sa direction LONG/SHORT DIFFÈRE de la MÊME cellule
(actif + horizon) dans le bulletin de la VEILLE (`veille_conclusions`). C'est la
sémantique exacte de `is_flip` (decision-log, LOT 6).

Garanties couvertes :
  (a) direction différente de la veille → marqueur ⇌ présent ;
  (b) direction identique → aucun marqueur (continuation) ;
  (c) cellule quasi-neutre / non franche → aucun marqueur (pas de direction fiable) ;
  (d) pas de lecture de veille pour la cellule → aucun marqueur (zéro invention) ;
  (e) cellule 🚫 insuffisante → aucun marqueur ;
  (f) le glyphe est EN TÊTE de cellule (avant la direction), pas en queue avec les drapeaux ;
  (g) le marqueur cohabite avec la raison `.cell-reason` sans la casser.

PUR RENDU : zéro LLM, zéro réseau.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import scoring_analyste as sa  # noqa: E402

_NOW = datetime(2026, 6, 20, 7, 0, tzinfo=timezone.utc)
_FLIP_GLYPH = "⇌"
_FLIP_CLASS = 'class="trend-flip"'


def _crit(nom: str, cle: str, contribs: Dict[str, float]) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle, nom=nom, type_norm="lineaire", valeur_brute=1.0, valeur_norm=1.0,
        poids=5.0, signe=1, pertinence={h: 1.0 for h in sa.HORIZONS}, note="",
        contributions=dict(contribs), cle_courante=cle,
        is_gate=False, gate_active=False, is_na=False,
    )


def _actif(nom: str, criteres: List[sa.CritereResult],
           scores: Dict[str, float], conclusions: Dict[str, str]) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom, fiche_key=nom.lower(), criteres=criteres,
        scores=dict(scores), conclusions=dict(conclusions), tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS}, tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS}, coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


def _grid_cells(md: str, actif: str) -> Dict[str, str]:
    """Retourne {horizon: cellule_brute} pour `actif` dans la grille « ## Synthèse des décisions »."""
    in_synth = False
    for ln in md.splitlines():
        if ln.startswith("## Synthèse des décisions"):
            in_synth = True
            continue
        if in_synth and ln.startswith("## "):
            break
        if in_synth and ln.startswith("| ") and " | " in ln and not ln.startswith("| Actif"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) == 4 and cells[0] == actif:
                return dict(zip(sa.HORIZONS, cells[1:]))
    return {}


def _strong_actif(nom: str, conc_par_h: Dict[str, str]) -> sa.ActifResult:
    """Actif à direction FRANCHE sur chaque horizon (|note| largement > NEUTRAL_BAND),
    porté par un driver simple — pour que la cellule soit actionnable (pas quasi-neutre).
    Les horizons non précisés héritent de la direction LONG par défaut (toujours franche)."""
    full = {h: conc_par_h.get(h, "LONG") for h in sa.HORIZONS}
    scores = {}
    crit_contribs = {}
    for h, conc in full.items():
        s = 6.0 if conc == "LONG" else -6.0
        scores[h] = s
        crit_contribs[h] = s
    crit = [_crit("Taux réels US", "taux_10y_us_reels_tips", crit_contribs)]
    return _actif(nom, crit, scores, full)


# ---------------------------------------------------------------------------
# (a) direction différente de la veille → marqueur ⇌
# ---------------------------------------------------------------------------

def test_direction_differente_veille_recoit_marqueur():
    """Or 24h LONG aujourd'hui, SHORT la veille → la cellule 24h porte ⇌ en tête."""
    r = _strong_actif("Or", {"24h": "LONG", "7j": "LONG", "1m": "LONG"})
    veille = {"or": {"24h": "SHORT", "7j": "LONG", "1m": "LONG"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cells = _grid_cells(md, "Or")
    # 24h a flippé (SHORT → LONG) : marqueur présent, EN TÊTE.
    assert _FLIP_GLYPH in cells["24h"], cells["24h"]
    assert _FLIP_CLASS in cells["24h"]
    # 7j et 1m inchangés (LONG → LONG) : pas de marqueur.
    assert _FLIP_GLYPH not in cells["7j"], cells["7j"]
    assert _FLIP_GLYPH not in cells["1m"], cells["1m"]


def test_marqueur_sur_les_trois_colonnes():
    """Les 3 horizons peuvent flipper indépendamment vs la veille."""
    r = _strong_actif("CAC 40", {"24h": "LONG", "7j": "SHORT", "1m": "LONG"})
    veille = {"cac 40": {"24h": "SHORT", "7j": "LONG", "1m": "SHORT"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cells = _grid_cells(md, "CAC 40")
    for h in sa.HORIZONS:
        assert _FLIP_GLYPH in cells[h], f"{h} aurait dû flipper : {cells[h]}"


# ---------------------------------------------------------------------------
# (b) direction identique → aucun marqueur (continuation)
# ---------------------------------------------------------------------------

def test_direction_identique_pas_de_marqueur():
    r = _strong_actif("Or", {"24h": "LONG", "7j": "SHORT", "1m": "LONG"})
    veille = {"or": {"24h": "LONG", "7j": "SHORT", "1m": "LONG"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cells = _grid_cells(md, "Or")
    for h in sa.HORIZONS:
        assert _FLIP_GLYPH not in cells[h], f"{h} = continuation, aucun marqueur : {cells[h]}"


# ---------------------------------------------------------------------------
# (c) cellule quasi-neutre / non franche → aucun marqueur
# ---------------------------------------------------------------------------

def test_cellule_quasi_neutre_pas_de_marqueur():
    """Cellule « LONG » mais |note| sous NEUTRAL_BAND : direction non franche.
    La veille est SHORT (donc différente), MAIS la conclusion courante reste
    LONG/SHORT seulement nominalement — le garde-fou exige conc ∈ {LONG, SHORT}
    ; ici on vérifie qu'une note quasi-nulle (≈ coin-flip) ne déclenche pas un
    marqueur trompeur sur une cellule non actionnable."""
    h = "24h"
    crit = [_crit("Taux réels US", "taux_10y_us_reels_tips", {h: +0.02})]
    scores = {hz: (+0.02 if hz == h else 0.0) for hz in sa.HORIZONS}
    conc = {hz: ("LONG" if hz == h else sa.CONCLUSION_INSUFFISANT) for hz in sa.HORIZONS}
    r = _actif("Cuivre", crit, scores, conc)
    veille = {"cuivre": {"24h": "SHORT"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cells = _grid_cells(md, "Cuivre")
    # |note| < 0.05 → coin-flip (⚪), cellule non franche : pas de marqueur de bascule.
    assert _FLIP_GLYPH not in cells["24h"], cells["24h"]


# ---------------------------------------------------------------------------
# (d) pas de lecture de veille → aucun marqueur (zéro invention)
# ---------------------------------------------------------------------------

def test_pas_de_veille_pas_de_marqueur():
    r = _strong_actif("Or", {"24h": "LONG", "7j": "SHORT", "1m": "LONG"})
    # veille vide → aucune base de comparaison.
    md = sa.render_bulletin([r], {}, _NOW, "h", "ok")
    cells = _grid_cells(md, "Or")
    for h in sa.HORIZONS:
        assert _FLIP_GLYPH not in cells[h], cells[h]


def test_cellule_absente_de_la_veille_pas_de_marqueur():
    """Actif présent mais horizon 7j absent de la veille → pas de marqueur sur 7j."""
    r = _strong_actif("Or", {"24h": "LONG", "7j": "SHORT", "1m": "LONG"})
    veille = {"or": {"24h": "SHORT"}}  # 7j et 1m absents
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cells = _grid_cells(md, "Or")
    assert _FLIP_GLYPH in cells["24h"]       # présent + flip
    assert _FLIP_GLYPH not in cells["7j"]    # absent de la veille → rien
    assert _FLIP_GLYPH not in cells["1m"]    # absent de la veille → rien


def test_veille_neutre_pas_de_marqueur():
    """La veille était quasi-neutre (ni LONG ni SHORT) → pas de base de bascule."""
    r = _strong_actif("Or", {"24h": "LONG"})
    veille = {"or": {"24h": "≈"}}  # direction veille non franche
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cells = _grid_cells(md, "Or")
    assert _FLIP_GLYPH not in cells["24h"], cells["24h"]


# ---------------------------------------------------------------------------
# (e) cellule 🚫 insuffisante → aucun marqueur
# ---------------------------------------------------------------------------

def test_cellule_insuffisante_pas_de_marqueur():
    h = "24h"
    crit = [_crit("Taux réels US", "taux_10y_us_reels_tips", {h: 0.0})]
    conc = {hz: sa.CONCLUSION_INSUFFISANT for hz in sa.HORIZONS}
    r = _actif("Cacao", crit, {hz: 0.0 for hz in sa.HORIZONS}, conc)
    veille = {"cacao": {"24h": "SHORT"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    # Les 🚫 sont regroupés dans la sous-table « Données insuffisantes » — on
    # vérifie qu'AUCUNE cellule du bulletin n'a reçu un marqueur de bascule.
    assert _FLIP_GLYPH not in md


# ---------------------------------------------------------------------------
# (f) glyphe EN TÊTE de cellule (avant la direction)
# ---------------------------------------------------------------------------

def test_glyphe_en_tete_avant_direction():
    """Le ⇌ précède le texte directionnel LONG/SHORT (pas en queue avec les drapeaux)."""
    r = _strong_actif("Or", {"24h": "LONG"})
    veille = {"or": {"24h": "SHORT"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cell = _grid_cells(md, "Or")["24h"]
    pos_glyph = cell.index(_FLIP_GLYPH)
    pos_dir = cell.index("LONG")
    assert pos_glyph < pos_dir, f"⇌ doit précéder LONG : {cell}"
    # Le span porte bien le title d'accessibilité.
    assert "Tendance inversée vs la veille" in cell


# ---------------------------------------------------------------------------
# (g) cohabitation avec la raison .cell-reason
# ---------------------------------------------------------------------------

def test_cohabite_avec_cell_reason():
    """Quand la cellule porte une raison (.cell-reason), le marqueur ⇌ reste en
    tête et la raison reste en queue (sous la direction) — les deux coexistent."""
    h = "24h"
    crit = [_crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.0})]
    scores = {hz: (-6.0 if hz == h else 0.0) for hz in sa.HORIZONS}
    conc = {hz: ("SHORT" if hz == h else sa.CONCLUSION_INSUFFISANT) for hz in sa.HORIZONS}
    r = _actif("Or", crit, scores, conc)
    veille = {"or": {"24h": "LONG"}}
    md = sa.render_bulletin([r], veille, _NOW, "h", "ok")
    cell = _grid_cells(md, "Or")["24h"]
    assert _FLIP_GLYPH in cell                 # marqueur présent
    if "cell-reason" in cell:                  # raison émise pour cette cellule
        # ⇌ avant le span .cell-reason (en tête vs en queue).
        assert cell.index(_FLIP_GLYPH) < cell.index("cell-reason"), cell
