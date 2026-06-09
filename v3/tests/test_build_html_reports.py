"""Tests build_html — affichage des suivis 12h/18h, bilans du jour et bilan semaine.

Garantit que la page `index.html` embarque, en plus des bulletins :
- les suivis intra-journée (v3/data/suivi/YYYY-MM-DD-HHh.md),
- le bilan du jour 22h (v3/data/bilan-jour/YYYY-MM-DD.md),
- le bilan de semaine le plus récent (v3/data/performance/weekly/win-rate-YYYY-S##.md).

Et qu'en l'absence de ces fichiers la page se dégrade proprement (aucune erreur,
sections vides). WIN RATE ONLY — aucune mention monétaire dans ces rapports.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_html as bh  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures de contenu (markdown réaliste, win-rate-only)
# ---------------------------------------------------------------------------

SUIVI_12H = """## Suivi 12h — 2026-06-08 12h03

### Positions du matin vs ouverture

| Actif | Call 7h | Statut |
|---|---|---|
| Or | SHORT | ✅ gagne |
"""

SUIVI_18H = """## Suivi 18h — 2026-06-08 18h02

### Positions vs ouverture + dynamique intraday

| Actif | Call 7h | Statut |
|---|---|---|
| Or | SHORT | ⚠️ perd |
"""

BILAN_JOUR = """## Bilan du jour — 2026-06-08

### Win rate du jour

Win rate : 2/3 calls justes.
"""

WEEKLY = """# Win rate — semaine 2026-S24

**0 / 36 cellules fiables.**

| Actif | Win rate |
|---|---|
| Or | 100.0% |
"""


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Collecte : suivis + bilans du jour
# ---------------------------------------------------------------------------

def test_build_reports_payload_collecte_suivis_et_bilan(tmp_path):
    suivi = tmp_path / "suivi"
    bilan = tmp_path / "bilan-jour"
    _write(suivi / "2026-06-08-12h.md", SUIVI_12H)
    _write(suivi / "2026-06-08-18h.md", SUIVI_18H)
    _write(bilan / "2026-06-08.md", BILAN_JOUR)

    reports = bh.build_reports_payload(suivi_dir=suivi, bilan_jour_dir=bilan)
    kinds = [r["kind"] for r in reports]
    assert kinds.count("suivi") == 2
    assert kinds.count("bilan-jour") == 1
    # Le bilan du jour (22h) doit précéder les suivis du même jour (tri décroissant).
    assert reports[0]["kind"] == "bilan-jour"
    # Slots lisibles.
    slots = {r["slot"] for r in reports}
    assert {"12h", "18h", "22h"} <= slots


def test_build_reports_payload_tri_multi_jours(tmp_path):
    suivi = tmp_path / "suivi"
    _write(suivi / "2026-06-07-12h.md", SUIVI_12H)
    _write(suivi / "2026-06-08-12h.md", SUIVI_12H)
    reports = bh.build_reports_payload(suivi_dir=suivi, bilan_jour_dir=tmp_path / "vide")
    # Jour le plus récent en tête.
    assert reports[0]["date"] == "2026-06-08"
    assert reports[-1]["date"] == "2026-06-07"


def test_build_reports_payload_dossiers_absents(tmp_path):
    # Dégradation propre : dossiers inexistants → liste vide, aucune exception.
    reports = bh.build_reports_payload(
        suivi_dir=tmp_path / "nope", bilan_jour_dir=tmp_path / "nope2"
    )
    assert reports == []


def test_build_reports_payload_ignore_fichiers_hors_format(tmp_path):
    suivi = tmp_path / "suivi"
    _write(suivi / ".gitkeep", "")
    _write(suivi / "2026-06-08-12h.md", SUIVI_12H)
    _write(suivi / "notes.txt", "ignore")
    reports = bh.build_reports_payload(suivi_dir=suivi, bilan_jour_dir=tmp_path / "x")
    assert len(reports) == 1
    assert reports[0]["filename"] == "2026-06-08-12h.md"


# ---------------------------------------------------------------------------
# Collecte : bilan de semaine (le plus récent)
# ---------------------------------------------------------------------------

def test_build_weekly_payload_plus_recent(tmp_path):
    wdir = tmp_path / "weekly"
    _write(wdir / "win-rate-2026-S23.md", "# S23")
    _write(wdir / "win-rate-2026-S24.md", WEEKLY)
    weekly = bh.build_weekly_payload(weekly_dir=wdir)
    assert weekly is not None
    assert weekly["filename"] == "win-rate-2026-S24.md"
    assert "2026-S24" in weekly["label"]


def test_build_weekly_payload_absent(tmp_path):
    assert bh.build_weekly_payload(weekly_dir=tmp_path / "nope") is None
    # Dossier présent mais vide → None aussi.
    (tmp_path / "empty").mkdir()
    assert bh.build_weekly_payload(weekly_dir=tmp_path / "empty") is None


# ---------------------------------------------------------------------------
# Rendu HTML : les rapports sont bien inclus dans la page générée
# ---------------------------------------------------------------------------

def test_render_html_inclut_suivi_bilan_et_semaine(tmp_path):
    suivi = tmp_path / "suivi"
    bilan = tmp_path / "bilan-jour"
    wdir = tmp_path / "weekly"
    _write(suivi / "2026-06-08-12h.md", SUIVI_12H)
    _write(suivi / "2026-06-08-18h.md", SUIVI_18H)
    _write(bilan / "2026-06-08.md", BILAN_JOUR)
    _write(wdir / "win-rate-2026-S24.md", WEEKLY)

    reports = bh.build_reports_payload(suivi_dir=suivi, bilan_jour_dir=bilan)
    weekly = bh.build_weekly_payload(weekly_dir=wdir)
    html = bh.render_html([], 0, reports=reports, weekly=weekly)

    # Le HTML embarque le contenu de chaque rapport.
    assert "Suivi 12h" in html
    assert "Suivi 18h" in html
    assert "Bilan du jour" in html
    assert "Win rate — semaine 2026-S24" in html
    # Et les vues de navigation existent.
    assert "nav-today" in html
    assert "nav-week" in html
    assert 'id="today-view"' in html
    assert 'id="week-view"' in html


def test_render_html_degradation_propre_sans_rapports(tmp_path):
    # Aucun suivi/bilan/semaine → page valide, pas de crash, WEEKLY null.
    html = bh.render_html([], 0, reports=[], weekly=None)
    assert "const WEEKLY = null" in html
    # Les vues existent quand même (elles afficheront un message vide côté JS).
    assert 'id="today-view"' in html
    assert 'id="week-view"' in html
    # Tableau REPORTS vide mais syntaxiquement valide.
    assert "const REPORTS = [" in html


def test_aucune_mention_monetaire_dans_les_rapports():
    # Garde-fou WIN RATE ONLY sur les fixtures (cohérent avec les générateurs).
    for md in (SUIVI_12H, SUIVI_18H, BILAN_JOUR, WEEKLY):
        low = md.lower()
        for token in ("€", "$", "gain", "perte", "rendement", "p&l"):
            assert token not in low
