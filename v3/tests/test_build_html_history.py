"""Tests build_html — onglet « Historique / Performance ».

Vérifie :
  - load_measures lit correctement measures-log.jsonl (champs, lignes invalides ignorées) ;
  - parse_perf_ab_summary extrait Taux/Brier ±1 par cellule depuis performance-ab.md ;
  - render_html embarque les mesures + le résumé en JS (page autonome, zéro fetch) ;
  - la page contient le tableau, les filtres (actif/horizon/résultat) et l'entrée de nav ;
  - measures-log absent → page bien formée + message « en cours de constitution ».
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_html as bh  # noqa: E402


def _write_jsonl(path: Path, records: list) -> None:
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


SAMPLE_MEASURES = [
    {
        "bulletin_date": "2026-06-01", "bulletin_id": "2026-06-01-16h",
        "fiche_key": "or", "actif": "Or", "horizon": "24h",
        "conclusion": "LONG", "score": 3.2, "outcome": "VRAI",
        "realized_pct": 1.42, "is_flip": False, "echeance": "2026-06-02",
    },
    {
        "bulletin_date": "2026-06-02", "bulletin_id": "2026-06-02-05h",
        "fiche_key": "nasdaq", "actif": "Nasdaq", "horizon": "7j",
        "conclusion": "SHORT", "score": -2.1, "outcome": "FAUSSE",
        "realized_pct": 0.8, "is_flip": True, "echeance": "2026-06-09",
    },
    {
        "bulletin_date": "2026-06-03", "bulletin_id": "2026-06-03-10h",
        "fiche_key": "argent", "actif": "Argent", "horizon": "24h",
        "conclusion": "LONG", "score": 0.5, "outcome": "suivi-interrompu",
        "realized_pct": None, "is_flip": None, "echeance": "2026-06-04",
    },
]


# ---------------------------------------------------------------------------
# load_measures
# ---------------------------------------------------------------------------

def test_load_measures_lit_les_champs(tmp_path):
    log = tmp_path / "measures-log.jsonl"
    _write_jsonl(log, SAMPLE_MEASURES)
    out = bh.load_measures(log)
    assert len(out) == 3
    assert out[0]["actif"] == "Or"
    assert out[0]["outcome"] == "VRAI"
    assert out[0]["realized_pct"] == 1.42
    assert out[2]["realized_pct"] is None  # None préservé (zéro invention)


def test_load_measures_absent_retourne_liste_vide(tmp_path):
    assert bh.load_measures(tmp_path / "absent.jsonl") == []


def test_load_measures_ignore_lignes_invalides(tmp_path):
    log = tmp_path / "measures-log.jsonl"
    log.write_text(
        json.dumps(SAMPLE_MEASURES[0], ensure_ascii=False) + "\n"
        + "ceci n'est pas du json\n"
        + "\n"  # ligne vide
        + json.dumps(SAMPLE_MEASURES[1], ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    out = bh.load_measures(log)
    assert len(out) == 2


# ---------------------------------------------------------------------------
# parse_perf_ab_summary
# ---------------------------------------------------------------------------

def test_parse_perf_ab_summary(tmp_path):
    ab = tmp_path / "performance-ab.md"
    ab.write_text(
        "## Matrice A/B\n\n"
        "| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| Or | 24h | 3 | 100.0% | 0.1123 | 3 | 100.0% | 0.0855 |\n"
        "| Cuivre | 24h | 2 | 50.0% | 0.1662 | 2 | 50.0% | 0.2094 |\n",
        encoding="utf-8",
    )
    summary = bh.parse_perf_ab_summary(ab)
    assert summary["Or|24h"] == {"taux": "100.0%", "brier": "0.1123"}
    assert summary["Cuivre|24h"]["taux"] == "50.0%"
    # En-tête et séparateur markdown ne polluent pas le résumé.
    assert "Actif|Horizon" not in summary
    assert len(summary) == 2


def test_parse_perf_ab_summary_absent(tmp_path):
    assert bh.parse_perf_ab_summary(tmp_path / "absent.md") == {}


# ---------------------------------------------------------------------------
# render_html — embarquement + structure de l'onglet
# ---------------------------------------------------------------------------

def test_render_html_embarque_mesures_et_resume():
    perf_ab = {"Or|24h": {"taux": "100.0%", "brier": "0.1123"}}
    html = bh.render_html([], 0, measures=SAMPLE_MEASURES, perf_ab=perf_ab)
    # Données embarquées en JS (page autonome).
    assert "const MEASURES =" in html
    assert "const PERF_AB =" in html
    assert '"actif": "Or"' in html or '"actif":"Or"' in html
    assert "100.0%" in html


def test_render_html_genere_tableau_et_filtres():
    html = bh.render_html([], 0, measures=SAMPLE_MEASURES, perf_ab={})
    # Tableau historique + colonnes.
    assert 'id="history-table"' in html
    for col in ("Date", "Actif", "Horizon", "Direction", "Résultat", "Réalisé %"):
        assert col in html
    # Filtres actif / horizon / résultat.
    assert 'id="filter-actif"' in html
    assert 'id="filter-horizon"' in html
    assert 'id="filter-outcome"' in html
    # Logique de rendu + tri date décroissant présente.
    assert "function renderHistoryTable" in html
    assert "function outcomeClass" in html


def test_render_html_entree_de_nav():
    html = bh.render_html([], 0, measures=SAMPLE_MEASURES, perf_ab={})
    assert 'id="nav-history"' in html
    assert "Historique" in html
    assert "function showHistory" in html


def test_render_html_colorisation_outcome():
    html = bh.render_html([], 0, measures=SAMPLE_MEASURES, perf_ab={})
    # Classes CSS branchées sur les variables dir-long/dir-short (dark mode).
    assert ".outcome-vrai" in html
    assert ".outcome-faux" in html
    assert "var(--dir-long-color)" in html
    assert "var(--dir-short-color)" in html


def test_render_html_sans_mesures_message_constitution():
    html = bh.render_html([], 0, measures=[], perf_ab={})
    # Page bien formée + message de constitution (1er run).
    assert "<!DOCTYPE html>" in html
    assert "en cours de constitution" in html
    assert "const MEASURES = []" in html


def test_render_html_page_bien_formee():
    html = bh.render_html([], 0, measures=SAMPLE_MEASURES, perf_ab={})
    assert html.startswith("<!DOCTYPE html>")
    assert html.rstrip().endswith("</html>")
    # Aucun placeholder de format non substitué.
    assert "{measures_js}" not in html
    assert "{perf_ab_js}" not in html
