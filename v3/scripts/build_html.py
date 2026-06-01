#!/usr/bin/env python3
"""build_html.py — Génère v3/data/index.html, une page autonome de lecture des bulletins.

USAGE LOCAL :
    python3 v3/scripts/build_html.py
    # Ouvre v3/data/index.html dans le navigateur (file://)

ACCÈS POUR THOMAS :
    (1) Local : `git pull` puis ouvrir `v3/data/index.html` dans un navigateur.
        Marche partout, aucun setup. Aucun fetch (markdown embarqué).
    (2) GitHub Pages : optionnel, nécessite plan payant pour repo privé.
        Sinon → option (1).

DÉTAILS TECHNIQUES :
    - Fichier HTML unique, autonome (CSS embarqué, marked.js via CDN).
    - Embarque les 90 derniers bulletins (par date décroissante) comme données JS.
    - Markdown échappé pour insertion dans des template literals JS.
    - Légende des symboles : ⚑ flip · 📰 news>50% · ⚪ coin-flip · ⚠ divergence.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
BULLETINS_DIR = ROOT / "data" / "bulletins"
OUT_PATH = ROOT / "data" / "index.html"
MAX_BULLETINS = 90

# Regex pour extraire la date (YYYY-MM-DD ou YYYY-MM-DDTHHhMM) du nom de fichier
RE_BULLETIN = re.compile(r"^bulletin-(.+)\.md$")


def list_bulletins() -> List[Tuple[str, Path]]:
    """Retourne [(stem, path)] triés par date décroissante (plus récent d'abord)."""
    if not BULLETINS_DIR.exists():
        return []
    items: List[Tuple[str, Path]] = []
    for p in BULLETINS_DIR.glob("bulletin-*.md"):
        m = RE_BULLETIN.match(p.name)
        if not m:
            continue
        items.append((m.group(1), p))
    # Tri par le label (qui contient la date ISO) décroissant
    items.sort(key=lambda x: x[0], reverse=True)
    return items


def escape_for_js_template_literal(s: str) -> str:
    """Échappe une chaîne pour insertion dans un template literal JS (backticks).

    - antislash → doublé
    - backtick → échappé
    - ${ → échappé (pour éviter l'interpolation)
    - </script> → cassé pour éviter une sortie prématurée du <script>
    """
    s = s.replace("\\", "\\\\")
    s = s.replace("`", "\\`")
    s = s.replace("${", "\\${")
    s = s.replace("</script>", "<\\/script>")
    return s


def build_payload() -> List[Dict[str, str]]:
    """Construit la liste des bulletins embarqués (max MAX_BULLETINS, du + récent au + ancien)."""
    items = list_bulletins()[:MAX_BULLETINS]
    payload: List[Dict[str, str]] = []
    for label, path in items:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            content = f"_Erreur lecture {path.name} : {exc}_"
        payload.append({
            "id": label,
            "label": label,
            "filename": path.name,
            "markdown": content,
        })
    return payload


def render_html(payload: List[Dict[str, str]], total_count: int) -> str:
    """Génère le HTML autonome."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # On sérialise séparément id/label/filename en JSON (simple), et le markdown
    # est inséré dans des template literals JS échappés (plus robuste pour
    # les guillemets, backslashes, et caractères Unicode).
    js_entries: List[str] = []
    for b in payload:
        meta = json.dumps({"id": b["id"], "label": b["label"], "filename": b["filename"]}, ensure_ascii=False)
        md_escaped = escape_for_js_template_literal(b["markdown"])
        js_entries.append(f"{{...{meta}, markdown: `{md_escaped}`}}")
    bulletins_js = "[\n" + ",\n".join(js_entries) + "\n]"

    embedded = len(payload)
    truncated_note = ""
    if total_count > embedded:
        truncated_note = (
            f"<span class=\"meta-note\">({embedded} sur {total_count} bulletins embarqués — "
            f"les {embedded} plus récents)</span>"
        )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TradingApp v3 — Bulletins</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  :root {{
    --bg: #fafafa;
    --bg-panel: #ffffff;
    --border: #e2e8f0;
    --text: #1e293b;
    --text-muted: #64748b;
    --accent: #2563eb;
    --accent-bg: #eff6ff;
    --code-bg: #f1f5f9;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; height: 100%; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
  }}
  header {{
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    position: sticky; top: 0; z-index: 10;
  }}
  header h1 {{ margin: 0; font-size: 17px; font-weight: 600; }}
  header .meta {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
  header .meta-note {{ margin-left: 8px; }}
  header .legend {{ font-size: 12px; color: var(--text-muted); margin-top: 6px; }}
  header .legend code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 11px; }}
  .layout {{
    display: flex;
    height: calc(100vh - 86px);
  }}
  aside {{
    width: 280px;
    border-right: 1px solid var(--border);
    background: var(--bg-panel);
    overflow-y: auto;
    flex-shrink: 0;
  }}
  aside ul {{ list-style: none; margin: 0; padding: 8px 0; }}
  aside li {{ padding: 0; }}
  aside a {{
    display: block; padding: 8px 16px; color: var(--text);
    text-decoration: none; font-size: 13px; border-left: 3px solid transparent;
  }}
  aside a:hover {{ background: var(--accent-bg); }}
  aside a.active {{ background: var(--accent-bg); border-left-color: var(--accent); font-weight: 600; }}
  main {{
    flex: 1;
    overflow-y: auto;
    padding: 24px 36px;
    max-width: 100%;
  }}
  main h1, main h2, main h3 {{ color: var(--text); }}
  main h1 {{ font-size: 22px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  main h2 {{ font-size: 18px; margin-top: 24px; }}
  main h3 {{ font-size: 15px; }}
  main table {{ border-collapse: collapse; margin: 12px 0; font-size: 13px; width: 100%; }}
  main table th, main table td {{
    border: 1px solid var(--border); padding: 6px 10px; text-align: left;
  }}
  main table th {{ background: var(--code-bg); font-weight: 600; }}
  main code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 13px; }}
  main pre {{ background: var(--code-bg); padding: 12px; border-radius: 6px; overflow-x: auto; }}
  main pre code {{ background: none; padding: 0; }}
  main blockquote {{
    border-left: 4px solid var(--border); margin: 12px 0; padding: 4px 16px;
    color: var(--text-muted);
  }}
  @media (max-width: 768px) {{
    .layout {{ flex-direction: column; height: auto; }}
    aside {{ width: 100%; max-height: 200px; border-right: none; border-bottom: 1px solid var(--border); }}
    main {{ padding: 16px 18px; }}
  }}
</style>
</head>
<body>
<header>
  <h1>TradingApp v3 — Bulletins</h1>
  <div class="meta">Généré : {generated_at}{truncated_note}</div>
  <div class="legend">
    Légende :
    <code>⚑</code> flip ·
    <code>📰</code> news&gt;50% (abs/abs) ·
    <code>⚪</code> coin-flip (|score|&lt;0.05, non-actionnable) ·
    <code>⚠</code> divergence pm1/pondéré
  </div>
</header>
<div class="layout">
  <aside>
    <ul id="bulletin-list"></ul>
  </aside>
  <main id="bulletin-content">
    <p>Chargement...</p>
  </main>
</div>
<script>
const BULLETINS = {bulletins_js};

function renderList(activeId) {{
  const ul = document.getElementById('bulletin-list');
  ul.innerHTML = '';
  BULLETINS.forEach(b => {{
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#' + encodeURIComponent(b.id);
    a.textContent = b.label;
    if (b.id === activeId) a.classList.add('active');
    a.onclick = (e) => {{
      e.preventDefault();
      selectBulletin(b.id);
    }};
    li.appendChild(a);
    ul.appendChild(li);
  }});
}}

function selectBulletin(id) {{
  const b = BULLETINS.find(x => x.id === id);
  const main = document.getElementById('bulletin-content');
  if (!b) {{
    main.innerHTML = '<p>Bulletin introuvable.</p>';
    return;
  }}
  if (typeof marked !== 'undefined') {{
    marked.setOptions({{gfm: true, breaks: false}});
    main.innerHTML = marked.parse(b.markdown);
  }} else {{
    // Fallback : affichage brut si marked n'a pas chargé (offline)
    const pre = document.createElement('pre');
    pre.textContent = b.markdown;
    main.innerHTML = '';
    main.appendChild(pre);
  }}
  history.replaceState(null, '', '#' + encodeURIComponent(id));
  renderList(id);
  main.scrollTop = 0;
}}

// Init : hash ou plus récent
(function init() {{
  if (BULLETINS.length === 0) {{
    document.getElementById('bulletin-content').innerHTML = '<p>Aucun bulletin disponible.</p>';
    return;
  }}
  const hash = decodeURIComponent((location.hash || '').replace(/^#/, ''));
  const found = BULLETINS.find(b => b.id === hash);
  selectBulletin(found ? found.id : BULLETINS[0].id);
}})();
</script>
</body>
</html>
"""


def main() -> int:
    items = list_bulletins()
    total = len(items)
    payload = build_payload()
    html = render_html(payload, total)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"[build_html] {len(payload)}/{total} bulletins embarqués → {OUT_PATH} ({OUT_PATH.stat().st_size} octets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
