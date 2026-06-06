"""Tests build_html — nommage multi-créneaux dans la liste des bulletins.

Vérifie :
  - le tri date PUIS créneau décroissant (soir avant midi avant matin) ;
  - le libellé lisible du créneau (UTC 05→matin, 10→midi, 16→soir, sinon {HH}h) ;
  - la rétro-compat de l'ancien nommage (sans créneau).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_html as bh  # noqa: E402


def test_slot_label():
    assert bh.slot_label("05") == "matin"
    assert bh.slot_label("10") == "midi"
    assert bh.slot_label("16") == "soir"
    assert bh.slot_label("08") == "08h"  # créneau inattendu → fallback {HH}h


def _touch(dir_: Path, name: str) -> None:
    (dir_ / name).write_text("# bulletin\n", encoding="utf-8")


def test_tri_date_puis_creneau_decroissant(tmp_path, monkeypatch):
    monkeypatch.setattr(bh, "BULLETINS_DIR", tmp_path)
    _touch(tmp_path, "bulletin-2026-06-01-16h.md")
    _touch(tmp_path, "bulletin-2026-06-02-05h.md")
    _touch(tmp_path, "bulletin-2026-06-02-10h.md")
    _touch(tmp_path, "bulletin-2026-06-02-16h.md")

    items = bh.list_bulletins()
    ids = [stem for stem, _ in items]
    # Plus récent d'abord : jour 02 soir → midi → matin, puis jour 01 soir.
    assert ids == [
        "2026-06-02-16h",
        "2026-06-02-10h",
        "2026-06-02-05h",
        "2026-06-01-16h",
    ]


def test_payload_slot_lisible(tmp_path, monkeypatch):
    monkeypatch.setattr(bh, "BULLETINS_DIR", tmp_path)
    _touch(tmp_path, "bulletin-2026-06-02-05h.md")
    _touch(tmp_path, "bulletin-2026-06-02-16h.md")
    _touch(tmp_path, "bulletin-2026-05-30.md")  # ancien nommage

    payload = bh.build_payload()
    by_id = {p["id"]: p for p in payload}
    assert by_id["2026-06-02-05h"]["slot"] == "matin"
    assert by_id["2026-06-02-16h"]["slot"] == "soir"
    # Ancien nommage : pas de créneau → slot vide (rétro-compat).
    assert by_id["2026-05-30"]["slot"] == ""


# --- Améliorations design (dark mode, colorisation, mobile, tooltips, repli) ---

def _render_sample_html() -> str:
    """Rend un HTML complet à partir d'un petit payload de test."""
    payload = [{
        "id": "2026-06-02-16h",
        "label": "2026-06-02-16h",
        "slot": "soir",
        "filename": "bulletin-2026-06-02-16h.md",
        "markdown": "# Test\n\n## Synthèse des décisions\n\n| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n| Or | SHORT 📰 | LONG | ⚪ |\n",
    }]
    return bh.render_html(payload, total_count=1)


def test_html_contient_dark_mode():
    html = _render_sample_html()
    # (a) bloc dark mode présent + au moins une variable sombre surchargée
    assert "@media (prefers-color-scheme: dark)" in html
    assert "--bg: #0f172a" in html
    # vert/rouge LONG/SHORT éclaircis pour le fond sombre
    assert "--dir-long-color: #4ade80" in html
    assert "--dir-short-color: #f87171" in html


def test_html_regex_colorisation_corrige():
    html = _render_sample_html()
    # (b) lookarounds robustes aux emojis, plus de \bLONG\b / \bSHORT\b
    assert "(?<![A-Za-z])LONG(?![A-Za-z])" in html
    assert "(?<![A-Za-z])SHORT(?![A-Za-z])" in html
    assert "\\\\bLONG\\\\b" not in html
    assert "\\\\bSHORT\\\\b" not in html


def test_html_dense_table_et_media_mobile():
    html = _render_sample_html()
    # (c) classe dense-table appliquée en JS + media query mobile sur les
    # colonnes secondaires du tableau « Détail par actif » (9 colonnes) :
    # 3e (« Valeur actuelle ») et 4e (« Penchant »).
    assert "markDenseTables" in html
    assert "dense-table" in html
    assert ".dense-table td:nth-child(3)" in html
    assert ".dense-table td:nth-child(4)" in html
    assert ".dense-table th:nth-child(3)" in html
    assert ".dense-table th:nth-child(4)" in html


def test_html_tooltips_symboles():
    html = _render_sample_html()
    # (d) tooltips natifs via attribut title sur les symboles d'info
    assert "addSymbolTooltips" in html
    assert "SYMBOL_TOOLTIPS" in html
    assert "<span title=" in html


def test_html_sticky_th_supprime():
    html = _render_sample_html()
    # bug #2 : plus de sticky sur les <th> (cassé dans overflow-x:auto).
    # On vérifie que le th utilise la variable --th-bg et non un sticky.
    assert "background: var(--th-bg)" in html


def test_html_repli_cellules_a_surveiller():
    html = _render_sample_html()
    # repli en <details> de la section monitoring dense
    assert "foldCellsToWatch" in html
    assert "fold-section" in html


def test_html_bien_forme_smoke():
    html = _render_sample_html()
    assert html.startswith("<!DOCTYPE html>")
    assert html.rstrip().endswith("</html>")
    # équilibre grossier des balises script
    assert html.count("<script") == html.count("</script>")
    assert html.count("<style>") == html.count("</style>")


def test_html_contient_favicon_data_uri():
    """(a) La page autonome embarque un favicon inline en data-URI SVG
    (pas de fichier externe) et reste bien formée."""
    html = _render_sample_html()
    # un seul <link rel="icon"> dans le <head>
    assert html.count('rel="icon"') == 1
    # data-URI encodée en BASE64 (robuste : les navigateurs refusent le SVG
    # en entités HTML / `<` bruts dans un favicon data:image/svg+xml).
    assert 'href="data:image/svg+xml;base64,' in html
    # le favicon est dans le <head>, avant le </head>
    head = html.split("</head>", 1)[0]
    assert 'rel="icon"' in head
    # aucun "<svg" brut dans le document (le SVG est en base64).
    assert "<svg" not in html
    # le favicon DÉCODÉ contient bien le SVG chandelier vert/rouge
    import base64 as _b64
    import re as _re
    _m = _re.search(r'href="data:image/svg\+xml;base64,([^"]+)"', html)
    assert _m, "favicon base64 introuvable"
    _svg = _b64.b64decode(_m.group(1)).decode("utf-8")
    assert "<svg" in _svg
    assert "limegreen" in _svg and "crimson" in _svg
    # page toujours bien formée
    assert html.startswith("<!DOCTYPE html>")
    assert html.rstrip().endswith("</html>")
