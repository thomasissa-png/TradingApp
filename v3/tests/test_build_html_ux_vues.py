"""Tests build_html — extension UX aux vues hors-Briefing (Session 7).

Présentation pure. On vérifie que le HTML généré embarque bien les nouveaux
éléments d'aide à la lecture pour les vues Performance / Bilan semaine :
  - Vue Performance (fusion Résultats + Historique) : intro contextuelle (WR
    tradable, « trop peu N/15 »), encart « chauffe » avec les dates/règles RÉELLES
    (reset 11/06, jalon 08/08, 12 actifs), grisage des lignes sans données,
    explication « Flip vs continuation », colonne créneau, dates humaines,
    regroupement par jour, distinction du jour courant ;
  - Vue Bilan semaine : titre humain « Semaine ISO … du lundi … au vendredi … » ;
  - Transverse : bandeau MODE TEST hors du <main> (visible sur toutes les vues).

Zéro logique métier testée — uniquement le rendu / la présence des hooks JS+CSS.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_html as bh  # noqa: E402


SAMPLE_WINRATE_MD = """# Win rate du bulletin — Journaliste

**0 / 36 cellules fiables** (15 paris requis/cellule). Tout est en chauffe.

### 24 heures

| Actif | Win rate | WR tradable | Paris (réels) | Non notés | Statut |
|---|---|---|---|---|---|
| Or | 100.0% | 100.0% | 6 | 4 | ⏳ trop peu (6/15) |
| Argent | — | — | 0 | 0 | ⏳ en attente |

### Flip vs continuation

| Type | Win rate | N |
|---|---|---|
| Flip | — | 0 |
| Continuation | — | 0 |
"""

SAMPLE_WEEKLY_MD = """# Win rate — semaine 2026-S24 (2026-06-08 → 2026-06-14)

- Win rate CUMULÉ depuis le début

### 24 heures

| Actif | Win rate | WR tradable | Paris (réels) | Nouveaux paris (semaine) | Non notés | Statut |
|---|---|---|---|---|---|---|
| Or | — | — | 0 | 5 | 0 | ⏳ en attente |
"""


# --- Vue Performance (fusion Résultats + Historique, refonte S9) ------------

def test_performance_intro_contextuelle():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    section = html.split('id="history-view"')[1].split("</section>")[0]
    # Explique les deux métriques + le « trop peu N/15 ».
    assert "WR tradable" in section
    assert "trop peu" in section
    assert "15 paris" in section


def test_performance_encart_chauffe_dates_reelles():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    section = html.split('id="history-view"')[1].split("</section>")[0]
    assert "winrate-warmup" in section
    # Dates/règles RÉELLES (SELECTION-RULE / cutover momentum), zéro invention.
    assert "11 juin 2026" in section      # reset 12 actifs (ère v2)
    assert "8 août 2026" in section        # J+60 = point de contrôle
    assert "12 actifs" in section
    assert "70" in section and "15" in section  # WR tradable ≥ 70% / N ≥ 15


def test_performance_grisage_lignes_sans_donnees():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    assert "function dimEmptyRows" in html
    assert "row-no-data" in html
    # Appelé dans la construction de la vue Performance (sur #history-winrate).
    view = html.split("function showHistory")[1][:700]
    assert "dimEmptyRows(hwr)" in view


def test_performance_explication_flip_continuation():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    assert "function annotateFlipContinuation" in html
    # L'explication relie au bug momentum (cacao) et est appelée dans la vue.
    assert "momentum" in html.lower()
    assert "cacao" in html.lower()
    assert "annotateFlipContinuation(hwr)" in html


def test_performance_winrate_only_aucun_argent():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    section = html.split('id="history-view"')[1].split("</section>")[0]
    for banned in ["P&L", "€", "$", "gain", "expectancy", "equity"]:
        assert banned not in section, f"Terme argent dans la vue Performance : {banned}"


# --- Vue Bilan semaine -----------------------------------------------------

def test_semaine_titre_humain_present():
    html = bh.render_html([], 0, weekly={
        "id": "weekly-x", "label": "Semaine 2026-S24", "filename": "win-rate-2026-S24.md",
        "markdown": SAMPLE_WEEKLY_MD,
    })
    assert "function weekHumanTitle" in html
    assert 'id="week-human-title"' in html
    # Le libellé attendu : « du lundi … au vendredi … » (lundi-vendredi de bourse).
    assert "du lundi " in html
    assert "au vendredi " in html


def test_semaine_degradation_propre_si_absent():
    html = bh.render_html([], 0, weekly=None)
    assert "const WEEKLY = null" in html
    # Le titre humain est masqué proprement.
    assert "titleEl.hidden = true" in html


# --- Vue Historique --------------------------------------------------------

def test_historique_colonne_creneau_et_dates_humaines():
    html = bh.render_html([], 0, measures=[
        {"actif": "Or", "horizon": "24h", "outcome": "VRAI",
         "bulletin_date": "2026-06-03", "bulletin_id": "2026-06-03-05h", "conclusion": "LONG"},
    ])
    # Colonne créneau dans l'en-tête + helper de slot + date humaine.
    assert "<th>Créneau</th>" in html
    assert "function measureSlot" in html
    assert "function historyDateHuman" in html
    # Mapping UTC→Paris des créneaux (seul le 7h est noté, suffixes possibles).
    assert "SLOT_UTC_TO_PARIS" in html


def test_historique_regroupement_par_jour_et_jour_courant():
    html = bh.render_html([], 0, measures=[])
    assert "history-day-row" in html
    assert "history-day-today" in html
    assert "row-today" in html
    assert "function todayIso" in html
    assert "today-pill" in html


# --- Transverse ------------------------------------------------------------

def test_bandeau_mode_test_hors_du_main():
    """Refonte S10 (identité Issa Capital) : le statut de validation doit rester
    hors <main> pour être visible sur TOUTES les vues. Il vit dans le header
    (badge .validation-badge « Validation · 08/08 »), qui précède <main> :
    intention conservée (statut toujours visible)."""
    html = bh.render_html([], 0)
    assert "header-status" in html
    assert "validation-badge" in html
    # Le badge statut précède l'ouverture du <main> (donc commun à toutes les vues).
    idx_status = html.index("header-status")
    idx_main = html.index("<main")
    assert idx_status < idx_main, "Le statut de validation doit précéder <main>"


def test_pas_de_placeholder_non_substitue():
    """Aucun trou de template ne doit subsister dans le HTML généré."""
    html = bh.render_html(
        [], 0, performance_md=SAMPLE_WINRATE_MD, weekly={
            "id": "w", "label": "Semaine 2026-S24", "filename": "f.md",
            "markdown": SAMPLE_WEEKLY_MD,
        },
        measures=[{"actif": "Or", "horizon": "24h", "outcome": "VRAI",
                   "bulletin_date": "2026-06-03", "bulletin_id": "2026-06-03-05h",
                   "conclusion": "LONG"}],
    )
    assert html.startswith("<!DOCTYPE html>")
    for tok in ["{winrate_js}", "{weekly_js}", "{measures_js}", "{generated_at}",
                "{bulletins_js}", "{reports_js}"]:
        assert tok not in html, f"Placeholder non substitué : {tok}"
