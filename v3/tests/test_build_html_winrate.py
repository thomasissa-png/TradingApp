"""Tests build_html — vue « Résultats / Win rate » (performance.md).

Vérifie :
  - load_performance_md lit notre tableau win-rate-only en markdown brut ;
  - absent → None (dégradation propre) ;
  - render_html embarque le markdown win-rate en JS + la nav/section dédiée ;
  - l'onglet Historique met le win rate en tête et rétrograde le bloc A/B Brier ;
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
# render_html — embarquement + vue dédiée
# ---------------------------------------------------------------------------

def test_render_html_embarque_le_tableau_winrate():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # Le markdown win-rate est embarqué dans la constante JS dédiée.
    assert "const WINRATE_MD =" in html
    assert "WINRATE_MD = null" not in html
    # Grep : le tableau win-rate de performance.md est bien dans le HTML.
    assert "| Actif | Win rate | Paris (réels) | Non notés | Statut |" in html
    assert "Win rate du bulletin" in html


def test_render_html_vue_winrate_nav_et_section():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # Entrée de nav sidebar + section dédiée + fonctions de rendu.
    assert 'id="nav-winrate"' in html
    assert "Résultats / Win rate" in html
    assert 'id="winrate-view"' in html
    assert 'id="winrate-content"' in html
    assert "function showWinrate" in html
    assert "function buildWinrateView" in html
    assert "vue=resultats" in html


def test_render_html_winrate_en_tete_onglet_historique():
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # Le win rate est rendu en tête de l'onglet Historique.
    assert 'id="history-winrate"' in html
    assert "renderWinrateInto(document.getElementById('history-winrate'))" in html
    # Le bloc A/B Brier est rétrogradé dans un <details> replié et secondaire.
    assert 'id="history-ab-fold"' in html
    assert "Détail technique par cellule" in html


def test_render_html_winrate_absent_degradation_propre():
    html = bh.render_html([], 0, performance_md=None)
    # Page bien formée, constante à null, pas de placeholder non substitué.
    assert html.startswith("<!DOCTYPE html>")
    assert "const WINRATE_MD = null" in html
    assert "{winrate_js}" not in html
    # La section + le message de dégradation existent dans la page (masqués via JS).
    assert 'id="winrate-view"' in html
    assert "Aucun résultat de win rate disponible" in html


def test_render_html_winrate_only_aucun_argent_injecte():
    """Le builder n'ajoute aucune notion d'argent autour du tableau win-rate."""
    html = bh.render_html([], 0, performance_md=SAMPLE_WINRATE_MD)
    # On vérifie que le chrome de la vue (titres, intro) est win-rate-only.
    section = html.split('id="winrate-view"')[1].split("</section>")[0]
    for banned in ["P&L", "€", "$", "gain", "expectancy", "equity"]:
        assert banned not in section, f"Terme argent dans la vue Résultats : {banned}"
