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

# Regex pour extraire l'identité du bulletin du nom de fichier :
#   - nouveau : bulletin-YYYY-MM-DD-HHh.md  (3 runs/jour, créneau = heure UTC)
#   - ancien  : bulletin-YYYY-MM-DD.md      (rétro-compat)
# group(1) = date ISO ; group(2) = heure UTC du créneau ("HH") ou None.
RE_BULLETIN = re.compile(r"^bulletin-(\d{4}-\d{2}-\d{2})(?:-(\d{2})h)?\.md$")

# Libellé lisible du créneau (heure UTC du run). Cron UTC 5/10/16.
SLOT_LABELS = {"05": "matin", "10": "midi", "16": "soir"}


def slot_label(hour_utc: str) -> str:
    """UTC 05→matin, 10→midi, 16→soir, sinon "{HH}h"."""
    return SLOT_LABELS.get(hour_utc, f"{hour_utc}h")


def list_bulletins() -> List[Tuple[str, Path]]:
    """Retourne [(stem, path)] triés par date PUIS créneau décroissants.

    Plus récent d'abord. Pour un même jour, le soir (16h) précède le midi (10h)
    qui précède le matin (05h). Les bulletins sans créneau (ancien nommage) sont
    classés comme "fin de journée" pour ce jour (clé "99").
    """
    if not BULLETINS_DIR.exists():
        return []
    items: List[Tuple[str, Path]] = []
    for p in BULLETINS_DIR.glob("bulletin-*.md"):
        m = RE_BULLETIN.match(p.name)
        if not m:
            continue
        items.append((p.stem[len("bulletin-"):], p))

    def _sort_key(item: Tuple[str, Path]) -> Tuple[str, str]:
        m = RE_BULLETIN.match(item[1].name)
        date_iso = m.group(1) if m else item[0]
        hour = m.group(2) if (m and m.group(2)) else "99"
        return (date_iso, hour)

    items.sort(key=_sort_key, reverse=True)
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
        m = RE_BULLETIN.match(path.name)
        # Créneau lisible (matin/midi/soir/{HH}h) — vide pour l'ancien nommage.
        slot = slot_label(m.group(2)) if (m and m.group(2)) else ""
        payload.append({
            "id": label,
            "label": label,
            "slot": slot,
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
        meta = json.dumps(
            {
                "id": b["id"],
                "label": b["label"],
                "slot": b.get("slot", ""),
                "filename": b["filename"],
            },
            ensure_ascii=False,
        )
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
    --bg: #f8fafc;
    --bg-panel: #ffffff;
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --text: #0f172a;
    --text-muted: #64748b;
    --accent: #2563eb;
    --accent-bg: #eff6ff;
    --code-bg: #f1f5f9;
    --row-alt: #f8fafc;
    --badge-bg: #16a34a;
    --badge-text: #ffffff;
    --th-bg: #f1f5f9;
    --dir-long-color: #15803d;
    --dir-short-color: #b91c1c;
  }}
  /* Dark mode automatique selon le réglage système — zéro toggle.
     Surcharge des variables CSS uniquement, aucune logique JS impactée.
     Vert/rouge LONG/SHORT éclaircis pour rester lisibles sur fond sombre. */
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #0f172a;
      --bg-panel: #1e293b;
      --border: #334155;
      --border-strong: #475569;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent: #60a5fa;
      --accent-bg: #1e3a5f;
      --code-bg: #1e293b;
      --row-alt: #172033;
      --badge-bg: #15803d;
      --badge-text: #ffffff;
      --th-bg: #243044;
      --dir-long-color: #4ade80;
      --dir-short-color: #f87171;
    }}
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; height: 100%; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
  }}
  header {{
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    position: sticky; top: 0; z-index: 20;
  }}
  header .header-row {{ display: flex; align-items: center; gap: 12px; }}
  header h1 {{ margin: 0; font-size: 17px; font-weight: 600; flex: 1; }}
  header .meta {{ font-size: 12px; color: var(--text-muted); margin-top: 4px; }}
  header .meta-note {{ margin-left: 8px; }}
  header .legend {{ font-size: 12px; color: var(--text-muted); margin-top: 6px; }}
  header .legend code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 11px; }}
  /* Hamburger (mobile uniquement) */
  .hamburger {{
    display: none;
    background: var(--bg-panel);
    border: 1px solid var(--border-strong);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 16px;
    cursor: pointer;
    color: var(--text);
  }}
  .hamburger:hover {{ background: var(--accent-bg); }}
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
    display: flex; align-items: center; gap: 8px;
    padding: 10px 16px; color: var(--text);
    text-decoration: none; font-size: 13.5px; border-left: 3px solid transparent;
    line-height: 1.35;
  }}
  aside a:hover {{ background: var(--accent-bg); }}
  aside a.active {{ background: var(--accent-bg); border-left-color: var(--accent); font-weight: 600; }}
  aside a.latest {{ font-weight: 600; }}
  aside .badge-latest {{
    background: var(--badge-bg); color: var(--badge-text);
    font-size: 10px; font-weight: 700;
    padding: 2px 6px; border-radius: 10px;
    text-transform: uppercase; letter-spacing: 0.3px;
    flex-shrink: 0;
  }}
  aside .item-date {{ flex: 1; }}
  main {{
    flex: 1;
    overflow-y: auto;
    padding: 0;
    max-width: 100%;
    position: relative;
  }}
  .content-inner {{
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 32px 48px 32px;
  }}
  /* Barre de légende sticky (toujours visible au-dessus du bulletin) */
  .legend-bar {{
    position: sticky; top: 0; z-index: 5;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    padding: 10px 20px;
    font-size: 13px;
    line-height: 1.5;
    color: var(--text);
  }}
  .legend-bar .legend-inner {{
    max-width: 900px; margin: 0 auto;
    display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center;
  }}
  .legend-bar code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 12px; }}
  /* Sous-navigation d'ancres intra-bulletin */
  .subnav {{
    position: sticky; top: 41px; z-index: 4;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    padding: 8px 20px;
    font-size: 13px;
  }}
  .subnav .subnav-inner {{
    max-width: 900px; margin: 0 auto;
    display: flex; flex-wrap: wrap; gap: 4px 4px; align-items: center;
  }}
  .subnav a {{
    color: var(--accent);
    text-decoration: none;
    padding: 4px 10px;
    border-radius: 999px;
    background: var(--accent-bg);
    font-size: 12.5px;
    border: 1px solid transparent;
    white-space: nowrap;
  }}
  .subnav a:hover {{ border-color: var(--accent); }}
  .subnav .subnav-label {{ color: var(--text-muted); font-size: 12px; margin-right: 4px; }}
  main h1, main h2, main h3 {{ color: var(--text); }}
  main h1 {{ font-size: 26px; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-top: 8px; }}
  main h2 {{ font-size: 20px; margin-top: 36px; padding-bottom: 6px; border-bottom: 1px solid var(--border); scroll-margin-top: 100px; }}
  main h3 {{ font-size: 16px; margin-top: 24px; scroll-margin-top: 100px; }}
  main p {{ margin: 10px 0; }}
  /* Wrapper de table pour scroll horizontal mobile propre */
  .table-wrap {{
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin: 14px 0;
    border: 1px solid var(--border);
    border-radius: 6px;
  }}
  main table {{ border-collapse: collapse; margin: 0; font-size: 13.5px; width: 100%; }}
  main table th, main table td {{
    border-bottom: 1px solid var(--border);
    padding: 9px 12px; text-align: left;
    vertical-align: top;
  }}
  main table th {{
    background: var(--th-bg); font-weight: 600;
    border-bottom: 2px solid var(--border-strong);
    white-space: nowrap;
  }}
  main table tbody tr:nth-child(even) {{ background: var(--row-alt); }}
  main table tbody tr:hover {{ background: var(--accent-bg); }}
  main code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 13px; }}
  main pre {{ background: var(--code-bg); padding: 12px; border-radius: 6px; overflow-x: auto; }}
  main pre code {{ background: none; padding: 0; }}
  main blockquote {{
    border-left: 4px solid var(--border-strong); margin: 12px 0; padding: 4px 16px;
    color: var(--text-muted);
  }}
  main ul, main ol {{ padding-left: 24px; }}
  main li {{ margin: 4px 0; }}
  /* Colorisation directionnelle LONG/SHORT et scores signés */
  .dir-long {{ color: var(--dir-long-color); font-weight: 600; }}
  .dir-short {{ color: var(--dir-short-color); font-weight: 600; }}
  /* Encart "Comment lire les scores" (détaillé, replié par défaut) */
  .help-box {{
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    margin: 20px 0 0 0;
    padding: 0;
    font-size: 13.5px;
  }}
  .help-box > summary {{
    cursor: pointer;
    padding: 10px 14px;
    font-weight: 600;
    color: var(--text);
    list-style: none;
    user-select: none;
  }}
  .help-box > summary::-webkit-details-marker {{ display: none; }}
  .help-box > summary::before {{
    content: "▸"; display: inline-block; margin-right: 8px;
    transition: transform 0.15s ease;
    color: var(--text-muted);
  }}
  .help-box[open] > summary::before {{ transform: rotate(90deg); }}
  .help-box .help-body {{
    padding: 4px 18px 14px 18px;
    color: var(--text);
    line-height: 1.6;
  }}
  .help-box .help-body p {{ margin: 8px 0; }}
  .help-box .help-body ul {{ margin: 6px 0 6px 18px; padding: 0; }}
  .help-box .help-body li {{ margin: 3px 0; }}
  .help-box .help-body code {{
    background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 12px;
  }}
  /* Section repliée « Cellules à surveiller » (monitoring dense) */
  .fold-section {{
    border: 1px solid var(--border);
    border-radius: 6px;
    margin: 20px 0;
    background: var(--bg-panel);
  }}
  .fold-section > summary {{
    cursor: pointer;
    padding: 10px 14px;
    font-weight: 600;
    color: var(--text);
    list-style: none;
    user-select: none;
  }}
  .fold-section > summary::-webkit-details-marker {{ display: none; }}
  .fold-section > summary::before {{
    content: "▸"; display: inline-block; margin-right: 8px;
    transition: transform 0.15s ease;
    color: var(--text-muted);
  }}
  .fold-section[open] > summary::before {{ transform: rotate(90deg); }}
  .fold-section > *:not(summary) {{ padding-left: 14px; padding-right: 14px; }}
  .fold-section > .table-wrap {{ margin-left: 14px; margin-right: 14px; }}
  /* Overlay mobile pour fermer la sidebar */
  .sidebar-overlay {{
    display: none;
    position: fixed; inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: 15;
  }}
  .sidebar-overlay.open {{ display: block; }}
  /* MOBILE */
  @media (max-width: 768px) {{
    body {{ font-size: 15.5px; }}
    .hamburger {{ display: inline-block; }}
    header h1 {{ font-size: 15.5px; }}
    .layout {{ height: calc(100vh - 86px); }}
    aside {{
      position: fixed;
      top: 0; left: 0; bottom: 0;
      width: 82%; max-width: 320px;
      transform: translateX(-100%);
      transition: transform 0.2s ease;
      z-index: 25;
      box-shadow: 2px 0 8px rgba(0,0,0,0.1);
      max-height: none;
      border-right: 1px solid var(--border);
    }}
    aside.open {{ transform: translateX(0); }}
    main {{ width: 100%; }}
    .content-inner {{ padding: 12px 14px 32px 14px; }}
    .legend-bar {{ padding: 8px 12px; font-size: 12px; }}
    .subnav {{ padding: 6px 12px; top: 39px; }}
    .subnav a {{ font-size: 12px; padding: 3px 8px; }}
    main h1 {{ font-size: 22px; }}
    main h2 {{ font-size: 18px; margin-top: 28px; scroll-margin-top: 130px; }}
    main h3 {{ font-size: 15.5px; scroll-margin-top: 130px; }}
    .help-box {{ font-size: 13px; }}
    /* Tables denses (Détail par actif, ≥8 colonnes) : on masque sur mobile la
       3e colonne (« Valeur brute », 15 décimales) et la 10e (« Note », redondante).
       La classe .dense-table est posée en JS UNIQUEMENT sur les tables à ≥8
       colonnes — la table Synthèse (4 colonnes) n'est PAS ciblée. */
    .dense-table td:nth-child(3),
    .dense-table th:nth-child(3),
    .dense-table td:nth-child(10),
    .dense-table th:nth-child(10) {{ display: none; }}
  }}
</style>
</head>
<body>
<header>
  <div class="header-row">
    <button class="hamburger" id="hamburger" aria-label="Ouvrir la liste des bulletins" aria-expanded="false">☰</button>
    <h1>TradingApp v3 — Bulletins</h1>
  </div>
  <div class="meta">Généré : {generated_at}{truncated_note}</div>
  <div class="legend">
    Légende symboles :
    <code>⚑</code> flip ·
    <code>📰</code> news&gt;50% (abs/abs) ·
    <code>⚪</code> coin-flip (|score|&lt;0.05, non-actionnable) ·
    <code>⚠</code> divergence pm1/pondéré
  </div>
</header>
<div class="sidebar-overlay" id="sidebar-overlay"></div>
<div class="layout">
  <aside id="sidebar">
    <ul id="bulletin-list"></ul>
  </aside>
  <main id="bulletin-main">
    <div class="legend-bar" id="legend-bar">
      <div class="legend-inner">
        <span><span class="dir-long">🟢 LONG</span> = hausse</span>
        <span>·</span>
        <span><span class="dir-short">🔴 SHORT</span> = baisse</span>
        <span>·</span>
        <span><code>|score|</code> = force de conviction (≈ 50% + |score|/15, max à 7,5)</span>
        <span>·</span>
        <span>⚪ &lt;0.05 = non-actionnable</span>
        <span>·</span>
        <span>📰 news&gt;50%</span>
        <span>·</span>
        <span>⚑ gate</span>
        <span>·</span>
        <span>⚠ divergence pm1/pondéré</span>
      </div>
    </div>
    <nav class="subnav" id="subnav" aria-label="Sections du bulletin">
      <div class="subnav-inner">
        <span class="subnav-label">Sauter à :</span>
        <span id="subnav-links"></span>
      </div>
    </nav>
    <div class="content-inner">
      <details class="help-box">
        <summary>❓ Comment lire les scores (détails complets)</summary>
        <div class="help-body">
          <p><strong>Signe = direction</strong> : <span class="dir-long">vert = LONG (hausse)</span>, <span class="dir-short">rouge = SHORT (baisse)</span>.</p>
          <p><strong>Grandeur = force de conviction</strong> (et non un % de mouvement attendu). Probabilité ≈ <code>50% + |score|/15</code>, plafonnée à 100%.</p>
          <p>Repères :</p>
          <ul>
            <li><code>|score| ~0</code> (&lt;0.05, ⚪) → ~50%, pile ou face, <strong>non-actionnable</strong></li>
            <li><code>|score| ≈ 1,5</code> → ~60% de conviction</li>
            <li><code>|score| ≈ 3,75</code> → ~75% de conviction</li>
            <li><code>|score| ≥ 7,5</code> → 100%, conviction maximale</li>
          </ul>
          <p><strong>Synthèse des décisions</strong> (en haut du bulletin) = vue d'oiseau : direction + note (le score signé, ex. <code>SHORT -3.82</code> ; plus <code>|note|</code> est élevé, plus la conviction est forte) ou <code>🚫</code>. Le détail chiffré complet est dans la <strong>Matrice</strong> plus bas.</p>
          <p><code>[pond: …]</code> = score en version <strong>pondérée</strong> (news × matérialité × fiabilité), affiché <strong>seulement s'il diffère</strong> du primaire. Sur les cellules <code>📰</code> (news&gt;50%), le pondéré (tempéré, plus fiable) passe <strong>en tête</strong> et le brut est entre parenthèses : <code>LONG +3.77 (brut +5.69) 📰</code>.</p>
          <p><strong>Symboles</strong> : <code>🚫</code> données insuffisantes · <code>⚑</code> gate · <code>📰</code> news&gt;50% du quant · <code>⚪</code> quasi coin-flip non-actionnable · <code>⚠</code> divergence primaire/pondéré. La légende complète du bulletin ne liste que les symboles réellement présents.</p>
        </div>
      </details>
      <div id="bulletin-content">
        <p>Chargement...</p>
      </div>
    </div>
  </main>
</div>
<script>
const BULLETINS = {bulletins_js};

// Colorisation idempotente des cellules de tableau :
// - "LONG" / "SHORT" enveloppés dans <span class="dir-long|dir-short">
// - Nombres signés +x.xx / -x.xx envloppés de même
// On opère sur l'HTML interne de chaque <td> mais en évitant de re-traiter
// du contenu déjà enveloppé (idempotent) et sans toucher aux attributs des
// balises (regex anti-attribut via lookbehind sur '>').
function colorizeDirections(root) {{
  if (!root) return;
  const tds = root.querySelectorAll('td');
  tds.forEach(td => {{
    // Skip si déjà colorisé (idempotent)
    if (td.dataset.colorized === '1') return;
    let html = td.innerHTML;
    // Découpe sur les balises pour n'opérer que sur les segments de texte.
    // Cela évite d'altérer href="..." ou autres attributs.
    const parts = html.split(/(<[^>]+>)/g);
    for (let i = 0; i < parts.length; i++) {{
      const seg = parts[i];
      if (!seg || seg.startsWith('<')) continue;  // balise → inchangée
      let s = seg;
      // 1) Mots LONG / SHORT — lookarounds robustes : on ne casse PAS sur un
      //    emoji ou caractère spécial collé (ex. "SHORT 📰", "🚫 LONG").
      //    \\b ne fonctionne que sur [A-Za-z0-9_] et échoue dès qu'un emoji
      //    Unicode est adjacent ; les lookarounds (?<![A-Za-z])/(?![A-Za-z])
      //    ne se basent que sur les lettres latines et restent corrects.
      s = s.replace(/(?<![A-Za-z])LONG(?![A-Za-z])/g, '<span class="dir-long">LONG</span>');
      s = s.replace(/(?<![A-Za-z])SHORT(?![A-Za-z])/g, '<span class="dir-short">SHORT</span>');
      // 2) Scores signés explicites : +1.23 / -0.45 / +12 / -7.5
      //    Borné à gauche par début, espace, parenthèse, deux-points ou crochet
      //    pour éviter d'attraper "x+1" dans une formule éventuelle.
      s = s.replace(/(^|[\\s(\\[:])\\+(\\d+(?:[.,]\\d+)?)/g, '$1<span class="dir-long">+$2</span>');
      s = s.replace(/(^|[\\s(\\[:])-(\\d+(?:[.,]\\d+)?)/g, '$1<span class="dir-short">-$2</span>');
      parts[i] = s;
    }}
    td.innerHTML = parts.join('');
    td.dataset.colorized = '1';
  }});
}}

// Formate une date lisible depuis l'ID du bulletin (ex "2026-06-01" ou "2026-06-01T18h00").
// Retourne {{ short: "dim. 1 juin", time: "18h" | "" }}.
function formatBulletinDate(id) {{
  const DAYS = ['dim.', 'lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.'];
  const MONTHS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
                  'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
  const m = id.match(/^(\\d{{4}})-(\\d{{2}})-(\\d{{2}})(?:[Tt_-]?(\\d{{1,2}})[hH:]?(\\d{{0,2}}))?/);
  if (!m) return {{ short: id, time: '' }};
  const y = parseInt(m[1], 10), mo = parseInt(m[2], 10), d = parseInt(m[3], 10);
  const dt = new Date(Date.UTC(y, mo - 1, d));
  const dayName = DAYS[dt.getUTCDay()];
  const monthName = MONTHS[mo - 1] || '';
  const short = `${{dayName}} ${{d}} ${{monthName}}`;
  let time = '';
  if (m[4]) {{
    const hh = m[4].padStart(2, '0');
    const mm = (m[5] || '').padStart(2, '0');
    time = mm && mm !== '00' ? `${{hh}}h${{mm}}` : `${{hh}}h`;
  }}
  return {{ short, time }};
}}

function renderList(activeId) {{
  const ul = document.getElementById('bulletin-list');
  ul.innerHTML = '';
  // Le plus récent = index 0 (BULLETINS déjà triés décroissant par build_payload).
  const latestId = BULLETINS.length > 0 ? BULLETINS[0].id : null;
  BULLETINS.forEach(b => {{
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = '#' + encodeURIComponent(b.id);
    const dt = formatBulletinDate(b.id);
    const dateSpan = document.createElement('span');
    dateSpan.className = 'item-date';
    // Créneau lisible : "matin/midi/soir" (b.slot) prioritaire, sinon l'heure
    // brute extraite de l'id (rétro-compat), sinon rien.
    const slotTxt = (b.slot && b.slot.length) ? b.slot : dt.time;
    dateSpan.textContent = slotTxt ? `${{dt.short}} — ${{slotTxt}}` : dt.short;
    a.appendChild(dateSpan);
    if (b.id === latestId) {{
      a.classList.add('latest');
      const badge = document.createElement('span');
      badge.className = 'badge-latest';
      badge.textContent = 'dernier';
      a.appendChild(badge);
    }}
    if (b.id === activeId) a.classList.add('active');
    a.onclick = (e) => {{
      e.preventDefault();
      selectBulletin(b.id);
      closeSidebarMobile();
    }};
    li.appendChild(a);
    ul.appendChild(li);
  }});
}}

// Enveloppe chaque <table> dans une <div class="table-wrap"> pour scroll horizontal mobile propre.
// Idempotent : skip si déjà enveloppé.
function wrapTables(root) {{
  if (!root) return;
  root.querySelectorAll('table').forEach(t => {{
    if (t.parentElement && t.parentElement.classList.contains('table-wrap')) return;
    const wrap = document.createElement('div');
    wrap.className = 'table-wrap';
    t.parentNode.insertBefore(wrap, t);
    wrap.appendChild(t);
  }});
}}

// Marque d'une classe .dense-table les tables ayant beaucoup de colonnes (≥8),
// pour le masquage CSS de colonnes sur mobile. marked.js rend TOUTES les tables
// en <table> sans classe : on cible donc par nombre d'en-têtes pour ne PAS
// toucher la table « Synthèse » (4 colonnes) ni les autres petites tables.
const DENSE_TABLE_MIN_COLS = 8;
function markDenseTables(root) {{
  if (!root) return;
  root.querySelectorAll('table').forEach(t => {{
    const headRow = t.querySelector('thead tr') || t.querySelector('tr');
    if (!headRow) return;
    const cols = headRow.querySelectorAll('th, td').length;
    if (cols >= DENSE_TABLE_MIN_COLS) t.classList.add('dense-table');
  }});
}}

// Tooltips natifs (attribut title) sur les symboles d'info de la matrice/synthèse.
// Reprend les définitions de la légende du bulletin. Zéro CSS, zéro espace.
const SYMBOL_TOOLTIPS = {{
  '🚫': 'Données insuffisantes — actif non scoré',
  '⏸': 'En pause — pas de décision actionnable',
  '📰': 'News > 50% du score quant — pondéré en tête',
  '⚑': 'Gate régime extrême actif',
  '⚪': 'Quasi coin-flip (|score| < 0.05) — non-actionnable',
  '⚠️': 'Divergence primaire/pondéré ou confiance faible',
  '⚠': 'Divergence primaire/pondéré ou confiance faible',
  '↯': 'Divergence quant ↔ news (signes opposés)',
  '⇄': 'Contre-momentum (conclusion vs RSI opposés)',
  '⇆': 'Contre-momentum (conclusion vs RSI opposés)',
  '⌛': 'Données périmées (stale)',
  '⊘': 'News démentie ou déjà cotée',
}};
function addSymbolTooltips(root) {{
  if (!root) return;
  // Regex couvrant tous les symboles de la map (échappés). On enveloppe chaque
  // occurrence dans un <span title="…"> sans toucher au contenu des balises.
  const keys = Object.keys(SYMBOL_TOOLTIPS);
  const escaped = keys.map(k => k.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&'));
  const re = new RegExp('(' + escaped.join('|') + ')', 'g');
  root.querySelectorAll('td, th').forEach(cell => {{
    if (cell.dataset.tooltipped === '1') return;
    const parts = cell.innerHTML.split(/(<[^>]+>)/g);
    let changed = false;
    for (let i = 0; i < parts.length; i++) {{
      const seg = parts[i];
      if (!seg || seg.startsWith('<')) continue;
      const next = seg.replace(re, (m) => {{
        const title = SYMBOL_TOOLTIPS[m] || '';
        return `<span title="${{title}}">${{m}}</span>`;
      }});
      if (next !== seg) {{ parts[i] = next; changed = true; }}
    }}
    if (changed) cell.innerHTML = parts.join('');
    cell.dataset.tooltipped = '1';
  }});
}}

// Replie la section « Cellules à surveiller » (monitoring dense) dans un
// <details> fermé par défaut : reste accessible en un clic sans polluer la
// lecture rapide. On cible le <h2> dont le texte contient « Cellules à surveiller »
// et on enveloppe ce h2 + tous les noeuds suivants jusqu'au prochain <h2>.
function foldCellsToWatch(root) {{
  if (!root) return;
  const h2s = Array.from(root.querySelectorAll('h2'));
  const target = h2s.find(h => /cellules\\s+à\\s+surveiller/i.test(h.textContent || ''));
  if (!target) return;
  if (target.dataset.folded === '1') return;
  const details = document.createElement('details');
  details.className = 'fold-section';
  const summary = document.createElement('summary');
  summary.textContent = (target.textContent || 'Cellules à surveiller').trim();
  details.appendChild(summary);
  // Déplace tout jusqu'au prochain h2 dans le <details>.
  const collected = [];
  let node = target.nextSibling;
  while (node && !(node.nodeType === 1 && node.tagName === 'H2')) {{
    collected.push(node);
    node = node.nextSibling;
  }}
  target.parentNode.insertBefore(details, target);
  collected.forEach(n => details.appendChild(n));
  target.dataset.folded = '1';
  target.remove();
}}

// Slugify simple pour ancres (cohérent avec le rendu marked par défaut, mais on
// génère nos propres ids pour ne pas dépendre du slugger interne).
function slugify(s) {{
  return s.toLowerCase()
    .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}}

// Construit la sous-navigation d'ancres à partir des <h2> du bulletin.
// Réécrit les ids des <h2> pour des ancres prévisibles et stables.
function buildSubnav(root) {{
  const links = document.getElementById('subnav-links');
  const subnav = document.getElementById('subnav');
  if (!links || !subnav) return;
  links.innerHTML = '';
  const h2s = root.querySelectorAll('h2');
  if (h2s.length === 0) {{
    subnav.style.display = 'none';
    return;
  }}
  subnav.style.display = '';
  h2s.forEach((h, i) => {{
    const raw = (h.textContent || '').trim();
    // Label court : premier mot significatif (Briefing / Matrice / Flips / Détail / Limites…)
    let label = raw.split(/[ —–\\-:(]/)[0] || raw;
    if (label.length > 22) label = label.slice(0, 22) + '…';
    const id = `sec-${{i}}-${{slugify(raw).slice(0, 40)}}`;
    h.id = id;
    const a = document.createElement('a');
    a.href = '#' + id;
    a.textContent = label;
    a.onclick = (e) => {{
      e.preventDefault();
      const target = document.getElementById(id);
      if (target) target.scrollIntoView({{behavior: 'smooth', block: 'start'}});
    }};
    if (i > 0) links.appendChild(document.createTextNode(' '));
    links.appendChild(a);
  }});
}}

function selectBulletin(id) {{
  const b = BULLETINS.find(x => x.id === id);
  const content = document.getElementById('bulletin-content');
  const mainEl = document.getElementById('bulletin-main');
  if (!b) {{
    content.innerHTML = '<p>Bulletin introuvable.</p>';
    return;
  }}
  if (typeof marked !== 'undefined') {{
    marked.setOptions({{gfm: true, breaks: false}});
    content.innerHTML = marked.parse(b.markdown);
    colorizeDirections(content);
    addSymbolTooltips(content);
    markDenseTables(content);
    wrapTables(content);
    foldCellsToWatch(content);
    buildSubnav(content);
  }} else {{
    // Fallback : affichage brut si marked n'a pas chargé (offline)
    const pre = document.createElement('pre');
    pre.textContent = b.markdown;
    content.innerHTML = '';
    content.appendChild(pre);
    // Pas de sous-nav en mode fallback
    const subnav = document.getElementById('subnav');
    if (subnav) subnav.style.display = 'none';
  }}
  history.replaceState(null, '', '#' + encodeURIComponent(id));
  renderList(id);
  if (mainEl) mainEl.scrollTop = 0;
}}

// --- Sidebar mobile (hamburger + overlay) ---
function openSidebarMobile() {{
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebar-overlay').classList.add('open');
  const h = document.getElementById('hamburger');
  if (h) h.setAttribute('aria-expanded', 'true');
}}
function closeSidebarMobile() {{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
  const h = document.getElementById('hamburger');
  if (h) h.setAttribute('aria-expanded', 'false');
}}

// Init : hash ou plus récent
(function init() {{
  // Bind hamburger + overlay
  const hb = document.getElementById('hamburger');
  if (hb) hb.addEventListener('click', () => {{
    const isOpen = document.getElementById('sidebar').classList.contains('open');
    if (isOpen) closeSidebarMobile(); else openSidebarMobile();
  }});
  const ov = document.getElementById('sidebar-overlay');
  if (ov) ov.addEventListener('click', closeSidebarMobile);
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') closeSidebarMobile();
  }});

  if (BULLETINS.length === 0) {{
    document.getElementById('bulletin-content').innerHTML = '<p>Aucun bulletin disponible.</p>';
    const subnav = document.getElementById('subnav');
    if (subnav) subnav.style.display = 'none';
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
