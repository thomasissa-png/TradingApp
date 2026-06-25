"""Tests build_html — vue « Performance » (fusion Résultats/Win rate + Historique).

Refonte design S9 : les deux entrées de menu « Résultats / Win rate » et
« Historique / Performance » faisaient doublon (même bloc win rate en tête, même
table 24h). Elles sont FUSIONNÉES en une seule vue « 📊 Performance » :
  - win rate par actif et par horizon en tête (le KPI, win-rate-only) ;
  - séquence des verdicts par cellule ;
  - détail technique A/B (calibration ±1) replié ;
  - table décision par décision en dessous.

Vérifie :
  - load_performance_md lit notre tableau win-rate-only en markdown brut ;
  - absent → None (dégradation propre) ;
  - render_html embarque le markdown win-rate en JS ;
  - la vue Performance unique (plus de winrate-view/showWinrate séparés) ;
  - win-rate-only : aucun montant d'argent injecté par le builder.

On NE teste PAS la logique de mesure (compute_kpi, render_performance) — couverte
par test_winrate_view_weekly. Ici : purement l'affichage côté build_html.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_html as bh  # noqa: E402


# Extrait représentatif de v3/data/performance.md (win-rate-only).
SAMPLE_WINRATE_MD = """# Win rate du bulletin — Journaliste

**0 / 36 cellules fiables** (15 paris requis/cellule). Tout est en chauffe.

### 24 heures

| Actif | Win rate | Paris (réels) | Non notés | Statut |
|---|---|---|---|---|
| Or | 100.0% | 6 | 4 | ⏳ trop peu (6/15) |
| Nasdaq | 66.7% | 6 | 3 | ⏳ trop peu (6/15) |
| S&P 500 | 16.7% | 6 | 3 | ⏳ trop peu (6/15) |
"""


# ---------------------------------------------------------------------------
# load_performance_md
# ---------------------------------------------------------------------------

def test_load_performance_md_lit_le_markdown(tmp_path):
    perf = tmp_path / "performance.md"
    perf.write_text(SAMPLE_WINRATE_MD, encoding="utf-8")
    out = bh.load_performance_md(perf)
    assert out is not None
    assert "Win rate du bulletin" in out
    assert "| Actif | Win rate | Paris (réels) | Non notés | Statut |" in out


def test_load_performance_md_absent_retourne_none(tmp_path):
    assert bh.load_performance_md(tmp_path / "absent.md") is None


# ---------------------------------------------------------------------------
# render_html — embarquement + vue Performance fusionnée
# ---------------------------------------------------------------------------

def test_render_html_embarque_le_tableau_winrate():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # Le markdown win-rate est embarqué dans la constante JS dédiée.
    assert "const WINRATE_MD =" in html
    assert "WINRATE_MD = null" not in html
    # Grep : le tableau win-rate de performance.md est bien dans le HTML.
    assert "| Actif | Win rate | Paris (réels) | Non notés | Statut |" in html
    assert "Win rate du bulletin" in html


def test_render_html_vue_performance_unique():
    # Une SEULE vue Résultats (fusion) : la nav et la section Historique portent
    # le libellé humain « Résultats · Win rate » (refonte S10, identité Issa
    # Capital), routée par #vue=performance (ancre inchangée).
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    assert 'id="nav-history"' in html
    assert "Résultats · Win rate" in html
    assert 'id="history-view"' in html
    assert 'id="history-winrate"' in html
    assert "vue=performance" in html
    # Rétro-compat des liens partagés d'avant la fusion (ne crée pas de vue).
    assert "vue=resultats" in html
    assert "vue=historique" in html


def test_render_html_ancienne_vue_resultats_supprimee():
    # La vue « Résultats / Win rate » séparée n'existe plus (doublon retiré).
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    assert 'id="nav-winrate"' not in html
    assert 'id="winrate-view"' not in html
    assert 'id="winrate-content"' not in html
    assert "function showWinrate" not in html
    assert "function buildWinrateView" not in html
    assert "Résultats / Win rate" not in html


def test_render_html_winrate_en_tete_vue_performance():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # Le win rate est rendu en tête de la vue Performance (#history-winrate),
    # avec la séquence des verdicts (annotateFlipContinuation + buildVerdictSequences).
    assert "getElementById('history-winrate')" in html
    assert "renderWinrateInto(hwr)" in html
    assert "buildVerdictSequences(hwr)" in html
    assert "annotateFlipContinuation(hwr)" in html
    # Le bloc A/B Brier est rétrogradé dans un <details> replié et secondaire.
    assert 'id="history-ab-fold"' in html
    assert "Détail technique par cellule" in html
    # L'encart de chauffe (ex-vue Résultats) vit désormais dans la vue Performance.
    assert "Tout est en chauffe." in html


def test_render_html_winrate_absent_degradation_propre():
    html = bh.render_html([], 0, performance_md=None)
    # Page bien formée, constante à null, pas de placeholder non substitué.
    assert html.startswith("<!DOCTYPE html>")
    assert "const WINRATE_MD = null" in html
    assert "{winrate_js}" not in html
    # La vue Performance + le message de dégradation existent (rendu via JS).
    assert 'id="history-view"' in html
    assert "Aucun résultat de win rate disponible" in html


def test_render_html_sequence_verdicts_par_cellule():
    """La vue Performance embarque la séquence compacte des verdicts par cellule,
    dérivée de MEASURES (rendu pur, zéro recalcul de KPI)."""
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD, measures=[
        {"actif": "Or", "horizon": "24h", "outcome": "VRAI", "bulletin_date": "2026-06-01"},
        {"actif": "Or", "horizon": "24h", "outcome": "FAUSSE", "bulletin_date": "2026-06-02"},
        {"actif": "Or", "horizon": "24h", "outcome": "non-conclusive", "bulletin_date": "2026-06-03"},
        {"actif": "Or", "horizon": "24h", "outcome": "suivi-interrompu", "bulletin_date": "2026-06-04"},
    ])
    assert "buildVerdictSequences" in html
    assert "verdict-seq" in html
    assert "verdictGlyph" in html
    # mapping documenté dans le code embarqué
    assert "✅" in html and "❌" in html and "⚪" in html
    # les états non conclus sont explicitement ignorés
    assert "non-conclusive" in html
    assert "suivi-interrompu" in html


def test_render_html_winrate_only_aucun_argent_injecte():
    """Le builder n'ajoute aucune notion d'argent autour de la vue Performance."""
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # On vérifie que le chrome de la vue (titres, intro, encart) est win-rate-only.
    section = html.split('id="history-view"')[1].split("</section>")[0]
    for banned in ["P&L", "€", "$", "gain", "expectancy", "equity"]:
        assert banned not in section, f"Terme argent dans la vue Performance : {banned}"
