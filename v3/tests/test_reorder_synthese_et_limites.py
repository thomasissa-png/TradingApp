"""Audit design 2026-06-02 — deux améliorations de lecture validées par Thomas.

#5  La « Synthèse des décisions » (grille directionnelle) doit précéder le
    contexte news (Briefing). Le Top 3 reste tout en haut. L'ordre est contrôlé
    par run_bulletin.insert_briefing_after_synthese (le Briefing s'ancre juste
    avant « ## Flips vs veille » au lieu d'être préfixé après le H1).

#8  La section « ## Limites du jour » ne liste que les critères absents à poids
    >= LIMITES_POIDS_MIN (8) ; les critères mineurs sont résumés en une ligne de
    comptage par actif. Les GATES actifs restent toujours affichés.

Ces tests vérifient le RENDU + l'ordre des sections : aucune conclusion / score
n'est modifié. Ils garantissent aussi que le parser du Journaliste
(MATRIX_ROW_RE, par regex de section) mesure toujours après réordonnancement.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jo  # noqa: E402
import run_bulletin as rb  # noqa: E402
import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 6, 2, 9, 0, tzinfo=timezone.utc)


def _fiche_multi() -> dict:
    """Fiche à 3 critères : 1 quant présent (couverture OK), 1 gros n/a (poids 12),
    1 petit n/a (poids 3 < seuil)."""
    base_crit = lambda i, nom, cle, poids: {  # noqa: E731
        "id": i, "nom": nom, "cle_courante": cle, "normalisation": "lineaire",
        "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": 1, "poids": poids,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    return {
        "actif": "TestActif",
        "criteres": [
            base_crit(1, "Quant", "quant", 10),
            base_crit(2, "GrosManquant", "gm", 12),
            base_crit(3, "PetitManquant", "pm", 3),
        ],
    }


def _render() -> str:
    res = sa.score_actif("test", _fiche_multi(), {"quant": {"valeur": 1.0, "source_track": "twelvedata"}})
    return sa.render_bulletin([res], {}, NOW, "h", "ok")


def _write_bulletin(tmp_path: Path) -> Path:
    """Écrit un bulletin réel sur disque, nom au format reconnu par le parser."""
    p = tmp_path / "bulletin-2026-06-02-09h.md"
    p.write_text(_render(), encoding="utf-8")
    return p


_BRIEFING_MD = (
    "## Briefing du jour\n\n_2 events analysés, 1 à impact._\n\n"
    "### TestActif\n- News marquante du jour.\n\n"
    "## Santé des sources\n\n_OK._\n"
)


# ===========================================================================
# #5 — La Synthèse précède le Briefing ; le Top 3 reste en première position
# ===========================================================================

def test_synthese_apparait_avant_le_briefing(tmp_path: Path):
    """Après insertion, '## Synthèse des décisions' précède '## Briefing du jour'."""
    p = _write_bulletin(tmp_path)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    b = p.read_text(encoding="utf-8")
    assert "## Briefing du jour" in b
    assert b.index("## Synthèse des décisions") < b.index("## Briefing du jour")


def test_top3_reste_en_premiere_position(tmp_path: Path):
    """La tête « 🎯 Aujourd'hui » (paris du jour + tableau À jouer 24h) reste tout en
    haut, avant la Synthèse ET avant le Briefing. Même intention : l'actionnable du
    jour ouvre le bulletin."""
    p = _write_bulletin(tmp_path)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    b = p.read_text(encoding="utf-8")
    i_top = b.index("## 🎯 Aujourd'hui")
    # Le tableau « À jouer » est un sous-bloc ### de la tête « Aujourd'hui ».
    assert "### À jouer aujourd'hui (24h)" in b
    assert i_top < b.index("## Synthèse des décisions")
    assert i_top < b.index("## Briefing du jour")


def test_briefing_avant_flips(tmp_path: Path):
    """Le Briefing s'insère avant '## Flips vs veille' (contexte news avant le détail)."""
    p = _write_bulletin(tmp_path)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    b = p.read_text(encoding="utf-8")
    assert b.index("## Briefing du jour") < b.index("## Flips vs veille")


def test_insertion_idempotente(tmp_path: Path):
    """Un re-run ne duplique pas le bloc Briefing (un seul '## Briefing du jour')."""
    p = _write_bulletin(tmp_path)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    b = p.read_text(encoding="utf-8")
    assert b.count("## Briefing du jour") == 1
    # ordre toujours respecté après re-run
    assert b.index("## Synthèse des décisions") < b.index("## Briefing du jour")


def test_fallback_sans_ancre_flips(tmp_path: Path):
    """Si l'ancre '## Flips vs veille' est absente, on ne perd pas le Briefing
    (fallback : insertion après le H1)."""
    p = tmp_path / "bulletin-2026-06-02-09h.md"
    p.write_text("# Bulletin Analyste — 2026-06-02\n\n## Synthèse des décisions\n\n| A | B |\n", encoding="utf-8")
    ok = rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    assert ok
    assert "## Briefing du jour" in p.read_text(encoding="utf-8")


# ===========================================================================
# #5 (suite) — Le Bilan des news s'ancre toujours après le Briefing
# ===========================================================================

def test_bilan_news_sinsere_apres_briefing_reordonne(tmp_path: Path):
    """Le Bilan des news (journaliste, regex de section) reste correctement
    inséré APRÈS le Briefing, même quand le Briefing est désormais placé après
    la Synthèse."""
    p = _write_bulletin(tmp_path)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    bilan = "## Bilan des news (calls passés)\n\n_Aucun call mesuré._\n"
    assert jo.inject_bilan_news_into_bulletin(p, bilan)
    b = p.read_text(encoding="utf-8")
    assert b.index("## Briefing du jour") < b.index("## Bilan des news")
    # et la Synthèse reste avant tout le bloc news
    assert b.index("## Synthèse des décisions") < b.index("## Briefing du jour")


# ===========================================================================
# #5 (suite) — Le parser du Journaliste mesure toujours après réordonnancement
# ===========================================================================

def test_parser_journaliste_mesure_apres_reorder(tmp_path: Path):
    """MATRIX_ROW_RE lit la table Synthèse par regex de ligne, où qu'elle soit
    dans le fichier → le réordonnancement (Briefing déplacé) ne casse pas la
    mesure. On vérifie que parse_bulletin retrouve bien la cellule TestActif."""
    p = _write_bulletin(tmp_path)
    cells_avant = jo.parse_bulletin(p)
    rb.insert_briefing_after_synthese(p, _BRIEFING_MD)
    cells_apres = jo.parse_bulletin(p)
    # Même nombre de cellules LONG/SHORT mesurables avant et après réordonnancement
    keys = lambda cs: sorted((c.actif_name, c.horizon, c.conclusion) for c in cs)  # noqa: E731
    assert keys(cells_avant) == keys(cells_apres)
    assert any(c.actif_name == "TestActif" for c in cells_apres)


# ===========================================================================
# #8 — Limites du jour filtrées (poids >= 8 + compteur des mineurs)
# ===========================================================================

def test_limites_liste_uniquement_poids_eleve():
    """Seul le critère n/a de poids >= 8 est listé nominativement."""
    b = _render()
    lim = b.split("## Limites du jour")[1]
    assert "GrosManquant" in lim       # poids 12 → listé
    assert "PetitManquant" not in lim  # poids 3 → omis (résumé)


def test_limites_compte_les_mineurs():
    """Une ligne de synthèse compte les critères mineurs (poids < 8) omis."""
    b = _render()
    lim = b.split("## Limites du jour")[1]
    assert "+1 critère mineur de poids <8 omis" in lim


def test_limites_garde_gate_actif():
    """Un GATE actif reste affiché dans les Limites, quel que soit son poids."""
    res = sa.score_actif("test", _fiche_multi(), {"quant": {"valeur": 1.0, "source_track": "twelvedata"}})
    # On force un critère gate actif pour vérifier qu'il reste listé.
    gate = next((c for c in res.criteres if c.is_gate), None)
    if gate is None:
        # Pas de gate dans cette fiche minimale : on simule via un critère existant.
        res.criteres[0].is_gate = True
        res.criteres[0].gate_active = True
        gate = res.criteres[0]
    b = sa.render_bulletin([res], {}, NOW, "h", "ok")
    lim = b.split("## Limites du jour")[1]
    assert "GATE actif" in lim


def test_limites_seuil_constante_a_huit():
    """Le seuil de filtrage est bien fixé à 8 (centralisé, non hardcodé inline)."""
    assert sa.LIMITES_POIDS_MIN == 8.0
