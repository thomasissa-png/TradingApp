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
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
BULLETINS_DIR = ROOT / "data" / "bulletins"
SUIVI_DIR = ROOT / "data" / "suivi"
BILAN_JOUR_DIR = ROOT / "data" / "bilan-jour"
WEEKLY_DIR = ROOT / "data" / "performance" / "weekly"
OUT_PATH = ROOT / "data" / "index.html"
MEASURES_LOG_FILE = ROOT / "data" / "measures-log.jsonl"
PERFORMANCE_AB_FILE = ROOT / "data" / "performance-ab.md"
# Notre tableau win-rate-only propre (généré par journaliste.render_performance) :
# c'est LA vue de résultats principale (win rate par actif × horizon). Win-rate-only,
# zéro argent, zéro Brier. Affiché en tête de l'onglet « Résultats » + Historique.
PERFORMANCE_MD_FILE = ROOT / "data" / "performance.md"
MAX_BULLETINS = 90
# Combien de jours récents on embarque pour les suivis + bilans du jour.
MAX_REPORT_DAYS = 30

# Ligne de la Matrice A/B de performance-ab.md :
# | Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
RE_AB_ROW = re.compile(
    r"^\|\s*(?P<actif>[^|]+?)\s*\|\s*(?P<horizon>[^|]+?)\s*\|"
    r"\s*(?P<n>[^|]+?)\s*\|\s*(?P<taux>[^|]+?)\s*\|\s*(?P<brier>[^|]+?)\s*\|"
)

# Regex pour extraire l'identité du bulletin du nom de fichier :
#   - nouveau : bulletin-YYYY-MM-DD-HHh.md  (3 runs/jour, créneau = heure UTC)
#   - ancien  : bulletin-YYYY-MM-DD.md      (rétro-compat)
# group(1) = date ISO ; group(2) = heure UTC du créneau ("HH") ou None.
RE_BULLETIN = re.compile(r"^bulletin-(\d{4}-\d{2}-\d{2})(?:-(\d{2})h)?\.md$")

# Libellé lisible du créneau (heure UTC du run). Cron UTC 5/10/16.
SLOT_LABELS = {"05": "matin", "10": "midi", "16": "soir"}

# Suivis intra-journée : v3/data/suivi/YYYY-MM-DD-HHh.md (HH = heure Paris du run, 12h/18h).
RE_SUIVI = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{2})h\.md$")
# Bilan du jour 22h : v3/data/bilan-jour/YYYY-MM-DD.md
RE_BILAN_JOUR = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
# Bilan de semaine : v3/data/performance/weekly/win-rate-YYYY-S##.md
RE_WEEKLY = re.compile(r"^win-rate-(\d{4})-S(\d{2})\.md$")


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


def _read_md(path: Path) -> str:
    """Lit un fichier markdown ; renvoie un message lisible en cas d'erreur (jamais de crash)."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — robustesse build, on ne plante jamais la page
        return f"_Erreur lecture {path.name} : {exc}_"


def build_reports_payload(
    suivi_dir: Path = SUIVI_DIR,
    bilan_jour_dir: Path = BILAN_JOUR_DIR,
    max_days: int = MAX_REPORT_DAYS,
) -> List[Dict[str, str]]:
    """Collecte suivis (12h/18h) + bilans du jour (22h), du plus récent au plus ancien.

    Chaque entrée : {id, kind, date, slot, label, filename, markdown}.
    - kind = "suivi" | "bilan-jour"
    - slot = "12h"/"18h" pour un suivi, "22h" pour un bilan du jour (heure Paris).
    Dossier absent ou vide → simplement aucune entrée (dégradation propre, zéro erreur).
    On limite aux `max_days` jours les plus récents (par date) pour ne pas gonfler la page.
    """
    items: List[Tuple[str, str, str, str, Path]] = []  # (date, sort_hour, kind, slot, path)

    if suivi_dir.exists():
        for p in suivi_dir.glob("*.md"):
            m = RE_SUIVI.match(p.name)
            if not m:
                continue
            items.append((m.group(1), m.group(2), "suivi", f"{m.group(2)}h", p))

    if bilan_jour_dir.exists():
        for p in bilan_jour_dir.glob("*.md"):
            m = RE_BILAN_JOUR.match(p.name)
            if not m:
                continue
            # Le bilan du jour clôt la journée (22h) → trié après les suivis du même jour.
            items.append((m.group(1), "22", "bilan-jour", "22h", p))

    # Tri date puis heure décroissants (le plus récent en tête).
    items.sort(key=lambda it: (it[0], it[1]), reverse=True)

    # Limite aux N jours les plus récents (par date distincte).
    if max_days > 0:
        kept_dates: List[str] = []
        seen = set()
        for date_iso, *_ in items:
            if date_iso not in seen:
                seen.add(date_iso)
                kept_dates.append(date_iso)
            if len(kept_dates) >= max_days:
                break
        allowed = set(kept_dates)
        items = [it for it in items if it[0] in allowed]

    payload: List[Dict[str, str]] = []
    for date_iso, _sort_hour, kind, slot, path in items:
        label = "Bilan du jour" if kind == "bilan-jour" else f"Suivi {slot}"
        payload.append({
            "id": f"{kind}-{path.stem}",
            "kind": kind,
            "date": date_iso,
            "slot": slot,
            "label": label,
            "filename": path.name,
            "markdown": _read_md(path),
        })
    return payload


def build_weekly_payload(weekly_dir: Path = WEEKLY_DIR) -> Optional[Dict[str, str]]:
    """Renvoie le bilan de semaine le plus récent, ou None si aucun.

    Tri par (année, numéro de semaine ISO) décroissant. Dossier absent/vide → None
    (la section « Bilan semaine » sera alors masquée — dégradation propre).
    """
    if not weekly_dir.exists():
        return None
    best: Optional[Tuple[Tuple[int, int], Path, str]] = None
    for p in weekly_dir.glob("win-rate-*.md"):
        m = RE_WEEKLY.match(p.name)
        if not m:
            continue
        key = (int(m.group(1)), int(m.group(2)))
        label = f"Semaine {m.group(1)}-S{m.group(2)}"
        if best is None or key > best[0]:
            best = (key, p, label)
    if best is None:
        return None
    _key, path, label = best
    return {
        "id": f"weekly-{path.stem}",
        "label": label,
        "filename": path.name,
        "markdown": _read_md(path),
    }


def load_measures(path: Path = MEASURES_LOG_FILE) -> List[Dict]:
    """Charge measures-log.jsonl (1 mesure JSON par ligne).

    Retourne une liste de dicts (ordre du fichier). Si le fichier est absent
    (1er run, mesures pas encore persistées) → liste vide (l'onglet Historique
    affichera « Historique en cours de constitution »). Lignes illisibles ignorées.
    """
    if not path.exists():
        return []
    out: List[Dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict):
            out.append(rec)
    return out


def parse_perf_ab_summary(path: Path = PERFORMANCE_AB_FILE) -> Dict[str, Dict[str, str]]:
    """Extrait un résumé (Taux/Brier ±1) par cellule depuis performance-ab.md.

    Clé = "{actif}|{horizon}" ; valeur = {"taux": str, "brier": str}. On ne lit
    QUE la Matrice A/B existante (colonnes Taux_pm1 / Brier_pm1). Aucune cellule
    inventée : si le fichier est absent ou la table introuvable → dict vide.
    """
    summary: Dict[str, Dict[str, str]] = {}
    if not path.exists():
        return summary
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return summary
    for line in text.splitlines():
        m = RE_AB_ROW.match(line)
        if not m:
            continue
        actif = m.group("actif").strip()
        horizon = m.group("horizon").strip()
        # Saute la ligne d'en-tête et le séparateur markdown.
        if actif.lower() in ("actif", "") or horizon.lower() in ("horizon", ""):
            continue
        if set(actif) <= set("-: "):
            continue
        summary[f"{actif}|{horizon}"] = {
            "taux": m.group("taux").strip(),
            "brier": m.group("brier").strip(),
        }
    return summary


def load_performance_md(path: Path = PERFORMANCE_MD_FILE) -> Optional[str]:
    """Lit notre tableau win-rate-only (performance.md) en markdown brut.

    Renvoie le contenu markdown tel quel, ou None si le fichier est absent
    (dégradation propre : la vue « Résultats » sera masquée et l'onglet
    Historique retombera sur l'historique des mesures unitaires). Aucune
    transformation : on réutilise tel quel le markdown produit par le
    journaliste (zéro invention).
    """
    if not path.exists():
        return None
    return _read_md(path)


def _entries_to_js(entries: List[Dict[str, str]], meta_keys: List[str]) -> str:
    """Sérialise une liste d'entrées {meta..., markdown} en tableau JS.

    Les `meta_keys` sont sérialisés en JSON ; `markdown` est inséré dans un
    template literal JS échappé (robuste guillemets/backslashes/Unicode).
    """
    js_entries: List[str] = []
    for e in entries:
        meta = json.dumps({k: e.get(k, "") for k in meta_keys}, ensure_ascii=False)
        md_escaped = escape_for_js_template_literal(e["markdown"])
        js_entries.append(f"{{...{meta}, markdown: `{md_escaped}`}}")
    return "[\n" + ",\n".join(js_entries) + "\n]"


def render_html(
    payload: List[Dict[str, str]],
    total_count: int,
    measures: Optional[List[Dict]] = None,
    perf_ab: Optional[Dict[str, Dict[str, str]]] = None,
    reports: Optional[List[Dict[str, str]]] = None,
    weekly: Optional[Dict[str, str]] = None,
    performance_md: Optional[str] = None,
) -> str:
    """Génère le HTML autonome."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # On sérialise séparément id/label/filename en JSON (simple), et le markdown
    # est inséré dans des template literals JS échappés (plus robuste pour
    # les guillemets, backslashes, et caractères Unicode).
    bulletins_js = _entries_to_js(payload, ["id", "label", "slot", "filename"])

    # Suivis 12h/18h + bilans du jour (section « Aujourd'hui »).
    reports = reports or []
    reports_js = _entries_to_js(reports, ["id", "kind", "date", "slot", "label", "filename"])

    # Bilan de semaine le plus récent (peut être absent → null).
    if weekly:
        weekly_js = _entries_to_js([weekly], ["id", "label", "filename"]) + "[0]"
    else:
        weekly_js = "null"

    # Historique : mesures unitaires + résumé Taux/Brier par cellule (page
    # autonome → tout est sérialisé en JS, aucun fetch au runtime).
    measures = measures or []
    perf_ab = perf_ab or {}
    measures_js = json.dumps(measures, ensure_ascii=False)
    perf_ab_js = json.dumps(perf_ab, ensure_ascii=False)

    # Notre tableau win-rate-only (performance.md) : markdown brut embarqué dans
    # un template literal JS échappé, rendu via le même pipeline marked.js que
    # les autres vues. Absent → null (la vue « Résultats » est masquée).
    if performance_md:
        winrate_js = "`" + escape_for_js_template_literal(performance_md) + "`"
    else:
        winrate_js = "null"

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
<link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHZpZXdCb3g9JzAgMCAzMiAzMic+PHJlY3QgeD0nOCcgeT0nNicgd2lkdGg9JzQnIGhlaWdodD0nMjAnIHJ4PScxJyBmaWxsPSdjcmltc29uJy8+PGxpbmUgeDE9JzEwJyB5MT0nMicgeDI9JzEwJyB5Mj0nNicgc3Ryb2tlPSdjcmltc29uJyBzdHJva2Utd2lkdGg9JzInLz48bGluZSB4MT0nMTAnIHkxPScyNicgeDI9JzEwJyB5Mj0nMzAnIHN0cm9rZT0nY3JpbXNvbicgc3Ryb2tlLXdpZHRoPScyJy8+PHJlY3QgeD0nMjAnIHk9JzEyJyB3aWR0aD0nNCcgaGVpZ2h0PScxNCcgcng9JzEnIGZpbGw9J2xpbWVncmVlbicvPjxsaW5lIHgxPScyMicgeTE9JzQnIHgyPScyMicgeTI9JzEyJyBzdHJva2U9J2xpbWVncmVlbicgc3Ryb2tlLXdpZHRoPScyJy8+PGxpbmUgeDE9JzIyJyB5MT0nMjYnIHgyPScyMicgeTI9JzI4JyBzdHJva2U9J2xpbWVncmVlbicgc3Ryb2tlLXdpZHRoPScyJy8+PC9zdmc+">
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
  /* Bandeau contexte permanent (casquette COMPRENDRE) — discret mais toujours là. */
  .context-banner {{
    background: var(--accent-bg);
    border-bottom: 1px solid var(--border);
    padding: 8px 20px;
    font-size: 12px;
    color: var(--text-muted);
  }}
  .context-inner {{
    max-width: 900px; margin: 0 auto;
    display: flex; flex-direction: column; gap: 2px;
  }}
  .context-inner strong {{ color: var(--text); font-weight: 600; }}
  .context-inner .ctx-shadow strong {{ color: var(--dir-short-color); }}
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
  /* [CH-5 audit visuel 12/06] : la légende n'est PLUS une barre sticky (elle
     occupait ~40px permanents pour une info rarement consultée). Elle défile
     avec le contenu après le premier coup d'œil ; la légende complète reste
     dans le help-box repliable. Seule la subnav reste collante sous le header
     → ~40px de chrome permanent récupérés. */
  .legend-bar {{
    position: static;
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
  /* Sous-navigation d'ancres intra-bulletin (seule barre sticky sous le header) */
  .subnav {{
    position: sticky; top: 0; z-index: 4;
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
  /* Badge de niveau par cellule (P1-C) — discret, dérivé des drapeaux existants. */
  .lvl-badge {{ font-size: 11px; cursor: help; }}
  /* Métadonnées techniques (P1-D) — repliées en pied de bulletin, discrètes. */
  .debug-meta {{
    margin: 32px 0 0 0; border-top: 1px solid var(--border);
    padding-top: 12px; font-size: 12px; color: var(--text-muted);
  }}
  .debug-meta > summary {{ cursor: pointer; user-select: none; }}
  .debug-meta ul {{ margin: 8px 0 0 0; }}
  /* Encart « chauffe » de la vue Résultats — repère doux, pas une alerte. */
  .winrate-warmup {{
    background: var(--accent-bg);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 10px 14px;
    margin: 4px 0 18px 0;
    font-size: 13px;
    color: var(--text);
    line-height: 1.5;
  }}
  /* Lignes sans données (N=0) dans les tables de résultats : grisées pour que
     l'œil saute aux lignes qui ont du contenu. Posé en JS (data-no-data). */
  .row-no-data {{ opacity: 0.5; }}
  /* Mini-légende des verdicts (vue Résultats), au-dessus de la séquence. */
  .verdict-flip-note {{
    font-size: 12.5px; color: var(--text-muted);
    margin: 8px 0 0 0; line-height: 1.5;
  }}
  /* Séquence des verdicts par cellule (vue Résultats) — compact ✅❌⚪. */
  .verdict-seq .verdict-line {{
    display: flex; align-items: center; gap: 12px;
    padding: 5px 0; border-bottom: 1px solid var(--border); font-size: 13.5px;
  }}
  .verdict-seq .verdict-cell {{ min-width: 150px; color: var(--text-muted); }}
  .verdict-seq .verdict-glyphs {{ letter-spacing: 2px; font-size: 14px; }}
  .verdict-seq .vg {{ letter-spacing: 0; }}
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
  /* Navigation des vues (Historique) en tête de sidebar */
  #nav-views {{ list-style: none; margin: 0; padding: 0; border-bottom: 1px solid var(--border); }}
  .nav-view-link {{
    display: block; text-decoration: none;
    padding: 12px 16px; color: var(--text);
    border-left: 3px solid transparent; font-weight: 600; font-size: 13.5px;
  }}
  .nav-view-link:hover {{ background: var(--accent-bg); }}
  .nav-view-link.active {{ background: var(--accent-bg); border-left-color: var(--accent); }}
  .nav-section-label {{
    padding: 8px 16px 4px 16px; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.04em; color: var(--text-muted); font-weight: 600;
  }}
  /* Vues Aujourd'hui / Bilan semaine / Historique */
  .history-intro {{ color: var(--text-muted); margin: 4px 0 18px 0; }}
  /* Titre humain de la semaine (lundi → vendredi) — sous le H1 « Bilan semaine ». */
  .week-human-title {{
    font-size: 15px; font-weight: 600; color: var(--text);
    margin: 2px 0 4px 0;
  }}
  /* Vue Aujourd'hui : un groupe replié par jour, chaque rapport en sous-bloc */
  .today-day {{
    border: 1px solid var(--border); border-radius: 8px; margin: 0 0 18px 0;
    background: var(--bg-panel); overflow: hidden;
  }}
  .today-day > summary {{
    cursor: pointer; padding: 12px 16px; font-weight: 600; font-size: 15px;
    color: var(--text); list-style: none; user-select: none;
    display: flex; align-items: center; gap: 10px;
  }}
  .today-day > summary::-webkit-details-marker {{ display: none; }}
  .today-day > summary::before {{
    content: "▸"; display: inline-block; transition: transform 0.15s ease;
    color: var(--text-muted);
  }}
  .today-day[open] > summary::before {{ transform: rotate(90deg); }}
  .today-day .day-count {{
    margin-left: auto; font-size: 12px; font-weight: 500; color: var(--text-muted);
  }}
  .today-report {{ border-top: 1px solid var(--border); }}
  .today-report > summary {{
    cursor: pointer; padding: 10px 16px 10px 32px; font-weight: 600; font-size: 13.5px;
    color: var(--accent); list-style: none; user-select: none;
    display: flex; align-items: center; gap: 8px;
  }}
  .today-report > summary::-webkit-details-marker {{ display: none; }}
  .today-report > summary::before {{
    content: "▸"; display: inline-block; transition: transform 0.15s ease;
    color: var(--text-muted);
  }}
  .today-report[open] > summary::before {{ transform: rotate(90deg); }}
  .today-report .report-body {{ padding: 4px 18px 16px 32px; }}
  .today-report .report-tag {{
    font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;
    padding: 2px 7px; border-radius: 10px; background: var(--accent-bg); color: var(--accent);
    flex-shrink: 0;
  }}
  /* Fil de la journée sous le briefing 7h (vue Historique/bulletin) : séparateur
     léger + rapports repliés. Cohérent avec .today-report / .fold-section. */
  .day-fil-sep {{
    display: flex; align-items: center; gap: 12px;
    margin: 28px 0 14px 0; font-size: 12px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-muted);
  }}
  .day-fil-sep::before, .day-fil-sep::after {{
    content: ""; flex: 1; height: 1px; background: var(--border);
  }}
  .day-fil-report {{
    border: 1px solid var(--border); border-radius: 8px; margin: 0 0 12px 0;
    background: var(--bg-panel); overflow: hidden;
  }}
  .day-fil-report > summary {{
    cursor: pointer; padding: 11px 16px; font-weight: 600; font-size: 14px;
    color: var(--accent); list-style: none; user-select: none;
    display: flex; align-items: center; gap: 8px;
  }}
  .day-fil-report > summary::-webkit-details-marker {{ display: none; }}
  .day-fil-report > summary::before {{
    content: "▸"; display: inline-block; transition: transform 0.15s ease;
    color: var(--text-muted);
  }}
  .day-fil-report[open] > summary::before {{ transform: rotate(90deg); }}
  .day-fil-body {{ padding: 4px 18px 16px 18px; }}
  /* Vue Historique */
  #history-view .history-intro {{ color: var(--text-muted); margin: 4px 0 18px 0; }}
  .history-filters {{
    display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-end;
    margin: 16px 0; padding: 12px; background: var(--bg-panel);
    border: 1px solid var(--border); border-radius: 6px;
  }}
  .history-filters label {{
    display: flex; flex-direction: column; gap: 4px;
    font-size: 12px; color: var(--text-muted); font-weight: 600;
  }}
  .history-filters select {{
    padding: 6px 10px; border: 1px solid var(--border-strong); border-radius: 4px;
    background: var(--bg); color: var(--text); font-size: 13.5px; min-width: 120px;
  }}
  .history-count {{ font-size: 12.5px; color: var(--text-muted); align-self: center; }}
  #history-table {{ border-collapse: collapse; width: 100%; font-size: 13.5px; }}
  #history-table th, #history-table td {{
    border-bottom: 1px solid var(--border); padding: 9px 12px; text-align: left;
    white-space: nowrap;
  }}
  #history-table th {{
    background: var(--th-bg); font-weight: 600;
    border-bottom: 2px solid var(--border-strong);
    position: sticky; top: 0; z-index: 1;
  }}
  #history-table tbody tr:nth-child(even) {{ background: var(--row-alt); }}
  #history-table tbody tr:hover {{ background: var(--accent-bg); }}
  .outcome-vrai {{ color: var(--dir-long-color); font-weight: 600; }}
  .outcome-faux {{ color: var(--dir-short-color); font-weight: 600; }}
  .outcome-neutre {{ color: var(--text-muted); }}
  /* Regroupement par jour de l'historique : ligne d'en-tête de date + jour courant. */
  #history-table tr.history-day-row td {{
    background: var(--th-bg); font-weight: 600; color: var(--text-muted);
    font-size: 12.5px; text-transform: capitalize;
    border-top: 2px solid var(--border-strong);
  }}
  #history-table tr.history-day-today td {{ color: var(--accent); }}
  #history-table tr.row-today td {{ background: var(--accent-bg); }}
  .today-pill {{
    display: inline-block; margin-left: 8px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.3px; padding: 1px 7px;
    border-radius: 10px; background: var(--accent); color: #fff;
  }}
  #history-summary {{
    display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 8px 0;
  }}
  #history-summary .summary-card {{
    border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px;
    background: var(--bg-panel); font-size: 12.5px; min-width: 120px;
  }}
  #history-summary .summary-card .sc-cell {{ color: var(--text-muted); }}
  #history-summary .summary-card .sc-val {{ font-weight: 600; color: var(--text); }}
  #history-empty {{ color: var(--text-muted); font-style: italic; padding: 20px 0; }}
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
    .subnav {{ padding: 6px 12px; top: 0; }}
    .subnav a {{ font-size: 12px; padding: 3px 8px; }}
    main h1 {{ font-size: 22px; }}
    main h2 {{ font-size: 18px; margin-top: 28px; scroll-margin-top: 130px; }}
    main h3 {{ font-size: 15.5px; scroll-margin-top: 130px; }}
    .help-box {{ font-size: 13px; }}
    /* Tables denses (Détail par actif, 9 colonnes) : on masque sur mobile la
       3e (« Valeur actuelle »), la 4e (« Penchant ») et — [CH-6 audit visuel
       12/06] — la 6e (« Sens », déjà expliquée dans l'encart « Comment lire »)
       pour tomber à 6 colonnes lisibles à 375px : Critère · Comment c'est lu ·
       Importance · Effet 24h/7j/1m. La classe .dense-table est posée en JS
       UNIQUEMENT sur les tables à ≥8 colonnes — la Synthèse (4 col.) n'est PAS
       ciblée. */
    .dense-table td:nth-child(3),
    .dense-table th:nth-child(3),
    .dense-table td:nth-child(4),
    .dense-table th:nth-child(4),
    .dense-table td:nth-child(6),
    .dense-table th:nth-child(6) {{ display: none; }}
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
    <code>⚑</code> gate régime ·
    <code>📰</code> news&gt;50% ·
    <code>⚪</code> coin-flip (non-actionnable) ·
    <code>⚠</code> calcul contesté ·
    <code>🔴</code> alerte ·
    <code>🟡</code> vigilance
  </div>
</header>
<div class="context-banner" role="note" aria-label="Contexte du système">
  <div class="context-inner">
    <span class="ctx-line ctx-shadow">⚠️ <strong>Mode test</strong> — non validé pour le réel · go-live 08/08 (WR&nbsp;≥&nbsp;70&nbsp;%, N&nbsp;≥&nbsp;15)</span>
  </div>
</div>
<div class="sidebar-overlay" id="sidebar-overlay"></div>
<div class="layout">
  <aside id="sidebar">
    <ul id="nav-views">
      <li><a href="#vue=aujourdhui" id="nav-today" class="nav-view-link">📅 Aujourd'hui</a></li>
      <li><a href="#vue=resultats" id="nav-winrate" class="nav-view-link">📈 Résultats / Win rate</a></li>
      <li><a href="#vue=semaine" id="nav-week" class="nav-view-link">🗓️ Bilan semaine</a></li>
      <li><a href="#vue=historique" id="nav-history" class="nav-view-link">📊 Historique / Performance</a></li>
    </ul>
    <div class="nav-section-label">Bulletins</div>
    <ul id="bulletin-list"></ul>
  </aside>
  <main id="bulletin-main">
    <div class="legend-bar" id="legend-bar">
      <div class="legend-inner">
        <span><span class="dir-long">🟢 LONG</span> = hausse</span>
        <span>·</span>
        <span><span class="dir-short">🔴 SHORT</span> = baisse</span>
        <span>·</span>
        <span><code>note</code> = force de conviction (plus elle est haute, plus la conviction est forte)</span>
        <span>·</span>
        <span>⚪ = non-actionnable</span>
        <span>·</span>
        <span>📰 news&gt;50%</span>
        <span>·</span>
        <span>⚑ gate</span>
        <span>·</span>
        <span>⚠ calcul contesté</span>
        <span>·</span>
        <span>🔴 alerte · 🟡 vigilance</span>
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
      <section id="winrate-view" hidden aria-label="Résultats — win rate par actif">
        <h1>📈 Résultats / Win rate</h1>
        <p class="history-intro">Le taux de bonnes directions par actif et par horizon — réécrit à chaque run. Deux mesures : le <strong>Win rate</strong> (sur les paris conclus) et le <strong>WR tradable</strong> (VRAI / VRAI+FAUSSE+non-conclusif — inclut les jours sous seuil où une position aurait quand même été prise, donc toujours ≤ Win rate).</p>
        <p class="history-intro"><strong>⏳ trop peu (N/15)</strong> = il faut au moins 15 paris indépendants par cellule pour qu'un chiffre soit fiable ; en dessous, le taux affiché ne veut encore rien dire.</p>
        <div class="winrate-warmup" role="note">
          <strong>Tout est en chauffe.</strong> Les 12 actifs ont été remis à zéro le <strong>11 juin 2026</strong> (passage en ère v2 du moteur). La mesure ouverture→clôture, 1 décision notée par jour, tourne depuis le 9 juin. Premier point de contrôle : le <strong>8 août 2026</strong> — une cellule 24h se trade alors uniquement si son WR tradable ≥&nbsp;70&nbsp;% sur ≥&nbsp;15 paris (règle de sélection gravée, mode test jusque-là).
        </div>
        <div id="winrate-content"></div>
        <p id="winrate-empty" hidden></p>
      </section>
      <section id="today-view" hidden aria-label="Rapports d'aujourd'hui">
        <h1>📅 Aujourd'hui</h1>
        <p class="history-intro">Le briefing du matin et les suivis de la journée, regroupés par jour. Le plus récent en premier.</p>
        <div id="today-list"></div>
        <p id="today-empty" hidden></p>
      </section>
      <section id="week-view" hidden aria-label="Bilan de la semaine">
        <h1>🗓️ Bilan semaine</h1>
        <p id="week-human-title" class="week-human-title" hidden></p>
        <p class="history-intro">Win rate cumulé de la semaine en cours (réécrit à chaque run, figé en fin de semaine).</p>
        <div id="week-content"></div>
        <p id="week-empty" hidden></p>
      </section>
      <section id="history-view" hidden aria-label="Historique des décisions et performance">
        <h1>Historique / Performance</h1>
        <p class="history-intro">Le win rate par actif en tête (résultats), puis le détail décision par décision.</p>
        <div id="history-winrate"></div>
        <details class="fold-section" id="history-ab-fold">
          <summary>Détail technique par cellule (calibration ±1)</summary>
          <p class="history-intro" style="margin-top:8px;">Taux et calibration internes par cellule — secondaire, conservé pour le suivi technique.</p>
          <div id="history-summary"></div>
        </details>
        <h2>Décision par décision</h2>
        <div class="history-filters" role="group" aria-label="Filtres de l'historique">
          <label>Actif
            <select id="filter-actif" aria-label="Filtrer par actif"><option value="">Tous</option></select>
          </label>
          <label>Horizon
            <select id="filter-horizon" aria-label="Filtrer par horizon"><option value="">Tous</option></select>
          </label>
          <label>Résultat
            <select id="filter-outcome" aria-label="Filtrer par résultat">
              <option value="">Tous</option>
              <option value="vrai">✅ VRAI</option>
              <option value="faux">❌ FAUX</option>
              <option value="encours">⏳ En cours</option>
            </select>
          </label>
          <span id="history-count" class="history-count"></span>
        </div>
        <div class="table-wrap">
          <table id="history-table">
            <thead>
              <tr>
                <th>Date</th><th>Créneau</th><th>Actif</th><th>Horizon</th><th>Direction</th><th>Résultat</th><th>Réalisé %</th>
              </tr>
            </thead>
            <tbody id="history-tbody"></tbody>
          </table>
        </div>
        <p id="history-empty" hidden></p>
      </section>
    </div>
  </main>
</div>
<script>
const BULLETINS = {bulletins_js};
const REPORTS = {reports_js};   // suivis 12h/18h + bilans du jour (22h), plus récent d'abord
const WEEKLY = {weekly_js};     // bilan de semaine le plus récent (ou null)
const MEASURES = {measures_js};
const PERF_AB = {perf_ab_js};
const WINRATE_MD = {winrate_js};   // tableau win-rate-only (performance.md) ou null

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

// --- P2-A : formate une date ISO8601 en libellé FR lisible ------------------
// "2026-06-10T07:19:06.037270+02:00" → "10 juin 2026 · 07h19 (Paris)".
// Si la chaîne n'est pas une date ISO reconnue, renvoie la chaîne d'origine.
const MONTHS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                   'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
function formatIsoHuman(iso) {{
  const m = (iso || '').match(/(\\d{{4}})-(\\d{{2}})-(\\d{{2}})T(\\d{{2}}):(\\d{{2}})/);
  if (!m) return iso;
  const d = parseInt(m[3], 10);
  const mois = MONTHS_FR[parseInt(m[2], 10) - 1] || m[2];
  return `${{d}} ${{mois}} ${{m[1]}} · ${{m[4]}}h${{m[5]}} (Paris)`;
}}

// --- P1-D : déplace les métadonnées de debug vers un pied de page replié -----
// Les lignes « Généré / Analyste version / Fiches hash » en tête du bulletin
// sont du suivi interne : on les sort du flux de décision vers un <details>
// en bas. « Fraîcheur » reste en place (info de décision). La date « Généré »
// est reformatée lisible (P2-A) au passage. HTML only, idempotent.
const DEBUG_META_RE = /^\\s*(généré|analyste version|fiches hash)\\s*:/i;
function relocateDebugMeta(root) {{
  if (!root || root.dataset.metaRelocated === '1') return;
  root.dataset.metaRelocated = '1';
  // Premier <ul> du document (la liste de méta est juste sous le H1).
  const ul = root.querySelector('ul');
  if (!ul) return;
  // Ne traite que si ce <ul> précède le premier <h2> (= bloc d'en-tête).
  const firstH2 = root.querySelector('h2');
  if (firstH2 && firstH2.compareDocumentPosition(ul) & Node.DOCUMENT_POSITION_FOLLOWING) return;
  const moved = [];
  Array.from(ul.querySelectorAll('li')).forEach(li => {{
    const txt = li.textContent || '';
    if (!DEBUG_META_RE.test(txt)) return;
    if (/^\\s*généré\\s*:/i.test(txt)) {{
      const iso = txt.replace(/^[^:]*:\\s*/, '').trim();
      li.textContent = 'Généré : ' + formatIsoHuman(iso);
    }}
    moved.push(li);
  }});
  if (moved.length === 0) return;
  const details = document.createElement('details');
  details.className = 'debug-meta';
  const summary = document.createElement('summary');
  summary.textContent = 'Métadonnées techniques (génération, version, hash)';
  details.appendChild(summary);
  const list = document.createElement('ul');
  moved.forEach(li => list.appendChild(li));
  details.appendChild(list);
  // Si le <ul> d'origine est désormais vide, on le retire.
  if (!ul.querySelector('li')) ul.remove();
  root.appendChild(details);
}}

// --- P1-A / P1-C : lecture rapide de la matrice (grisage + badge niveau) ----
// Drapeaux dérivés UNIQUEMENT des symboles déjà présents dans la cellule.
// Aucun seuil inventé, aucun recalcul : on lit le texte rendu.
// Rouge « ne pas jouer » : ⚪ (coin-flip) · ≈ (quasi-neutre) · 🚫 (données insuffisantes).
const LEVEL_RED = ['⚪', '≈', '🚫'];
// Jaune « prudence » : ◧ (semi-fiable) · ⚠️/⚠ (divergence/conf. faible) · ↯ (divergence quant↔news).
const LEVEL_YELLOW = ['◧', '⚠️', '⚠', '↯'];

// Vrai si une cellule de DIRECTION (1re ou 2e colonne hors actif) — on ne badge/grise
// que les <td> contenant une direction LONG/SHORT ou un score signé, pas les libellés.
function tdLooksLikeDecision(text) {{
  return /\\b(LONG|SHORT)\\b/.test(text) || /[+-]\\d/.test(text) || /🚫/.test(text);
}}

// P1-A — grise les cellules faibles (⚪ ou ≈) de la matrice Synthèse. Aucune info
// supprimée : opacité réduite + texte muted. Idempotent (data-dimmed).
function dimWeakCells(root) {{
  if (!root) return;
  root.querySelectorAll('td').forEach(td => {{
    if (td.dataset.dimmed === '1') return;
    const text = td.textContent || '';
    if (!tdLooksLikeDecision(text)) return;
    if (text.includes('⚪') || text.includes('≈')) {{
      td.style.opacity = '0.45';
      td.dataset.dimmed = '1';
    }}
  }});
}}

// Vue Résultats — grise les lignes SANS données (win rate « — » ET paris = 0)
// dans les tables de win rate, pour que l'œil aille aux lignes qui ont du contenu.
// Pur visuel (classe .row-no-data), aucune ligne supprimée, aucun chiffre touché.
// Idempotent (data-rowscanned sur la table). On repère par en-têtes : la 2e
// colonne est « Win rate », l'avant-dernière paire contient « Paris (réels) ».
function dimEmptyRows(root) {{
  if (!root) return;
  root.querySelectorAll('table').forEach(table => {{
    if (table.dataset.rowscanned === '1') return;
    const headRow = table.querySelector('thead tr') || table.querySelector('tr');
    if (!headRow) return;
    const heads = Array.from(headRow.querySelectorAll('th, td')).map(h => (h.textContent || '').toLowerCase());
    const wrIdx = heads.findIndex(h => h.includes('win rate'));
    const parisIdx = heads.findIndex(h => h.includes('paris'));
    if (wrIdx < 0) {{ table.dataset.rowscanned = '1'; return; }}
    table.querySelectorAll('tbody tr').forEach(tr => {{
      const cells = tr.querySelectorAll('td');
      if (cells.length <= wrIdx) return;
      const wr = (cells[wrIdx].textContent || '').trim();
      const paris = parisIdx >= 0 && cells.length > parisIdx
        ? (cells[parisIdx].textContent || '').trim() : '';
      const wrEmpty = (wr === '' || wr === '—' || wr === '-');
      const noParis = (parisIdx < 0) || (paris === '' || paris === '0' || paris === '—');
      if (wrEmpty && noParis) tr.classList.add('row-no-data');
    }});
    table.dataset.rowscanned = '1';
  }});
}}

// [P-R1 + C-R1 audit visuel 12/06] — Vue Résultats :
//  P-R1 : grise (row-no-data) toute ligne dont N < WINRATE_MIN_N (trop peu de
//         paris pour être significatif — le tableau est sinon noyé de zéros).
//  C-R1 : pour les sections 7j et 1m, MASQUE les lignes vides (N=0 ET Non
//         notés=0) et insère UN message unique « en attente de données ».
// Pur visuel : aucune ligne supprimée du markdown source, aucun chiffre touché.
const WINRATE_MIN_N = 5;
function _leadingInt(s) {{
  const m = (s || '').match(/-?\\d+/);
  return m ? parseInt(m[0], 10) : 0;
}}
function enhanceWinrateRows(root) {{
  if (!root) return;
  // Repère la section (h3) de chaque table : 24 heures / 7 jours / 1 mois.
  root.querySelectorAll('table').forEach(table => {{
    if (table.dataset.wrEnhanced === '1') return;
    const headRow = table.querySelector('thead tr') || table.querySelector('tr');
    if (!headRow) return;
    const heads = Array.from(headRow.querySelectorAll('th, td')).map(h => (h.textContent || '').toLowerCase());
    const wrIdx = heads.findIndex(h => h.includes('win rate'));
    const parisIdx = heads.findIndex(h => h.includes('paris'));
    if (wrIdx < 0 || parisIdx < 0) {{ table.dataset.wrEnhanced = '1'; return; }}
    // Section = texte du h3 précédent la table.
    let prev = table.previousElementSibling;
    while (prev && prev.tagName !== 'H3') prev = prev.previousElementSibling;
    const sectionTxt = prev ? (prev.textContent || '').toLowerCase() : '';
    const isLongHorizon = sectionTxt.includes('7 jour') || sectionTxt.includes('1 mois');
    const nonNotesIdx = heads.findIndex(h => h.includes('non not'));
    let hidden = 0;
    table.querySelectorAll('tbody tr').forEach(tr => {{
      const cells = tr.querySelectorAll('td');
      if (cells.length <= parisIdx) return;
      const n = _leadingInt(cells[parisIdx].textContent);
      const nonNotes = (nonNotesIdx >= 0 && cells.length > nonNotesIdx)
        ? _leadingInt(cells[nonNotesIdx].textContent) : 0;
      // C-R1 : 7j/1m sans aucune donnée → masquer.
      if (isLongHorizon && n === 0 && nonNotes === 0) {{
        tr.style.display = 'none';
        hidden++;
        return;
      }}
      // P-R1 : N < seuil → grisé (significativité nulle).
      if (n < WINRATE_MIN_N) tr.classList.add('row-no-data');
    }});
    if (isLongHorizon && hidden > 0) {{
      const tb = table.querySelector('tbody');
      if (tb) {{
        const msg = document.createElement('tr');
        msg.className = 'wr-empty-horizon';
        const td = document.createElement('td');
        td.colSpan = heads.length;
        td.innerHTML = '<em>Horizon long en attente de données (premiers résultats à partir de juillet).</em>';
        msg.appendChild(td);
        tb.appendChild(msg);
      }}
    }}
    table.dataset.wrEnhanced = '1';
  }});
}}

// P1-C — préfixe un badge de niveau (🔴/🟡) en début de cellule de décision, dérivé
// des drapeaux existants. 🔴 prime sur 🟡. Idempotent (data-badged). HTML only.
function addLevelBadges(root) {{
  if (!root) return;
  root.querySelectorAll('td').forEach(td => {{
    if (td.dataset.badged === '1') return;
    const text = td.textContent || '';
    if (!tdLooksLikeDecision(text)) {{ td.dataset.badged = '1'; return; }}
    let badge = '';
    if (LEVEL_RED.some(s => text.includes(s))) {{
      badge = '<span class="lvl-badge lvl-red" title="Ne pas jouer (coin-flip / quasi-neutre / données insuffisantes)">🔴</span> ';
    }} else if (LEVEL_YELLOW.some(s => text.includes(s))) {{
      badge = '<span class="lvl-badge lvl-yellow" title="Prudence (semi-fiable / divergence / confiance faible)">🟡</span> ';
    }}
    if (badge) td.innerHTML = badge + td.innerHTML;
    td.dataset.badged = '1';
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
// Replie une section <h2> (et tous ses noeuds jusqu'au prochain <h2>) dans un
// <details class="fold-section"> fermé. Conserve l'id du h2 d'origine sur le
// <summary> pour que la sous-nav puisse cibler et ouvrir la section repliée.
// Idempotent (data-folded). Renvoie l'élément <summary> créé (ou null).
function foldOneSection(target) {{
  if (!target || target.dataset.folded === '1') return null;
  const details = document.createElement('details');
  details.className = 'fold-section';
  const summary = document.createElement('summary');
  summary.textContent = (target.textContent || '').trim();
  // L'id (posé par buildSubnav) est repris sur le summary pour l'ancrage.
  if (target.id) {{ summary.id = target.id; target.removeAttribute('id'); }}
  details.appendChild(summary);
  const collected = [];
  let node = target.nextSibling;
  while (node && !(node.nodeType === 1 && node.tagName === 'H2')) {{
    collected.push(node);
    node = node.nextSibling;
  }}
  target.parentNode.insertBefore(details, target);
  collected.forEach(n => details.appendChild(n));
  target.dataset.folded = '1';
  details.dataset.foldedSection = '1';
  target.remove();
  return summary;
}}

// Titres de h2 à replier par défaut (P1-E + Reco 1). On gère AUSSI l'ancien
// titre « Audit de la veille » (bulletins archivés) en plus du nouveau
// « Calls 24h jugés ». Comparaison insensible casse/accents/espaces.
const FOLD_SECTION_PATTERNS = [
  /cellules\\s+à\\s+surveiller/i,
  /limites\\s+du\\s+jour/i,
  /calls\\s+24h\\s+jug/i,        // « 🔎 Calls 24h jugés (fenêtre récente) » (nouveau titre)
  /audit\\s+de\\s+la\\s+veille/i, // ancien titre (bulletins archivés)
  /détail\\s+par\\s+actif/i,
  // [P8] « Synthèse des décisions » : DÉPLIÉE par défaut (demande Thomas). On la
  // RETIRE de la liste de repli → elle reste une section ouverte normale.
  /comment\\s+lire\\s+les\\s+scores/i, // pédagogie consolidée → repliée (lecture rapide)
  /fausses\\s+aux\\s+retournements/i, // [C-BD2] métrique technique du moteur (bilan jour)
];

function foldSections(root) {{
  if (!root) return;
  const h2s = Array.from(root.querySelectorAll('h2'));
  h2s.forEach(h => {{
    const txt = h.textContent || '';
    if (FOLD_SECTION_PATTERNS.some(re => re.test(txt))) foldOneSection(h);
  }});
  // [C-B1 audit visuel 12/06] : à l'intérieur de « Détail par actif » (replié),
  // chaque actif (### = h3) devient un <details> individuel → on n'ouvre que
  // l'actif voulu sans dérouler les 12. Idempotent (data-folded sur le h3).
  foldPerActifDetail(root);
}}

// Replie chaque sous-section actif (### h3) du Détail par actif dans un
// <details> propre. Le contenu d'un actif court jusqu'au prochain h3 OU jusqu'à
// la fin du conteneur (fin du fold parent). Le glossaire / encart « Comment
// lire » (paragraphes hors h3) restent visibles en tête, non repliés.
function foldPerActifDetail(root) {{
  if (!root) return;
  // On cible les h3 situés DANS la section repliée « Détail par actif » : son
  // summary porte un id sec-… ; le contenu est dans le <details> parent.
  const summaries = Array.from(root.querySelectorAll('details.fold-section > summary'));
  const detailSummary = summaries.find(s => /détail\\s+par\\s+actif/i.test(s.textContent || ''));
  if (!detailSummary) return;
  const container = detailSummary.parentNode; // le <details> du Détail par actif
  const h3s = Array.from(container.querySelectorAll(':scope > h3'));
  h3s.forEach(h3 => {{
    if (h3.dataset.folded === '1') return;
    const d = document.createElement('details');
    d.className = 'fold-actif';
    const sm = document.createElement('summary');
    sm.textContent = (h3.textContent || '').trim();
    d.appendChild(sm);
    const collected = [];
    let node = h3.nextSibling;
    while (node && !(node.nodeType === 1 && node.tagName === 'H3')) {{
      collected.push(node);
      node = node.nextSibling;
    }}
    container.insertBefore(d, h3);
    collected.forEach(n => d.appendChild(n));
    h3.dataset.folded = '1';
    h3.remove();
  }});
}}

// Ouvre la <details class="fold-section"> contenant l'élément ciblé par `id`
// (h2 replié → son summary porte cet id). Permet à un clic de sous-nav d'ouvrir
// une section repliée avant de scroller dessus.
function openFoldedSectionFor(id) {{
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  const details = el.closest('details.fold-section');
  if (details && !details.open) details.open = true;
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
      // Si la section a été repliée (foldSections), l'ouvrir avant de scroller.
      openFoldedSectionFor(id);
      const target = document.getElementById(id);
      if (target) target.scrollIntoView({{behavior: 'smooth', block: 'start'}});
    }};
    if (i > 0) links.appendChild(document.createTextNode(' '));
    links.appendChild(a);
  }});
}}

// --- Vue Historique / Performance -----------------------------------------
// Classe un outcome brut (VRAI / FAUSSE / en-cours / interrompu / non-conclusive…)
// en 3 familles d'affichage : vrai (✅), faux (❌), neutre (⏳/—).
function outcomeClass(outcome) {{
  const o = (outcome || '').toString().toUpperCase();
  if (o === 'VRAI' || o.startsWith('VRAI')) return 'vrai';
  if (o === 'FAUSSE' || o === 'FAUX' || o.startsWith('FAUS')) return 'faux';
  // en-cours / interrompu / non-conclusive / inconnu → neutre
  return 'neutre';
}}
function outcomeBadge(cls, outcome) {{
  // [I-2 audit visuel 12/06] : verdict standardisé « ✅ VRAI » / « ❌ FAUSSE »
  // partout (le Bilan du jour utilise déjà FAUSSE ; la vue Historique disait
  // FAUX → incohérence inter-rapports corrigée).
  if (cls === 'vrai') return '✅ VRAI';
  if (cls === 'faux') return '❌ FAUSSE';
  // affiche l'outcome brut tel quel (en-cours, interrompu, non-conclusive…)
  return '⏳ ' + (outcome || '—');
}}
function fmtPct(v) {{
  if (v === null || v === undefined || v === '') return '—';
  const n = Number(v);
  if (!isFinite(n)) return '—';
  return (n >= 0 ? '+' : '') + n.toFixed(2) + ' %';
}}
function uniqueSorted(values) {{
  return Array.from(new Set(values.filter(v => v !== null && v !== undefined && v !== ''))).sort();
}}

let HISTORY_BUILT = false;
function buildHistoryFilters() {{
  const selA = document.getElementById('filter-actif');
  const selH = document.getElementById('filter-horizon');
  if (!selA || !selH) return;
  uniqueSorted(MEASURES.map(m => m.actif)).forEach(a => {{
    const o = document.createElement('option'); o.value = a; o.textContent = a; selA.appendChild(o);
  }});
  uniqueSorted(MEASURES.map(m => m.horizon)).forEach(h => {{
    const o = document.createElement('option'); o.value = h; o.textContent = h; selH.appendChild(o);
  }});
  selA.addEventListener('change', renderHistoryTable);
  selH.addEventListener('change', renderHistoryTable);
  const selO = document.getElementById('filter-outcome');
  if (selO) selO.addEventListener('change', renderHistoryTable);
}}
function buildHistorySummary() {{
  const wrap = document.getElementById('history-summary');
  if (!wrap) return;
  const keys = Object.keys(PERF_AB);
  const fold = document.getElementById('history-ab-fold');
  if (keys.length === 0) {{
    wrap.innerHTML = '';
    if (fold) fold.hidden = true;  // pas de détail A/B → on masque tout le bloc
    return;
  }}
  if (fold) fold.hidden = false;
  wrap.innerHTML = '';
  keys.forEach(k => {{
    const [actif, horizon] = k.split('|');
    const v = PERF_AB[k] || {{}};
    const card = document.createElement('div');
    card.className = 'summary-card';
    card.innerHTML = '<div class="sc-cell">' + actif + ' · ' + horizon + '</div>'
      + '<div><span class="sc-val">Taux ' + (v.taux || '—') + '</span>'
      + ' · Brier ' + (v.brier || '—') + '</div>';
    wrap.appendChild(card);
  }});
}}
// Créneau lisible d'une mesure : l'heure UTC suffixée à l'id (« …-05h ») mappée
// matin/midi/soir, sinon « 7h » (seul le Briefing 7h est noté — CA-M6b). Renvoie
// un libellé heure-Paris parlant. Zéro invention : si pas de suffixe, c'est le 7h.
const SLOT_UTC_TO_PARIS = {{ '05': '7h', '10': '12h', '16': '18h', '19': '18h' }};
function measureSlot(m) {{
  const id = (m.bulletin_id || '');
  const mm = id.match(/-(\\d{{2}})h$/);
  if (mm) return SLOT_UTC_TO_PARIS[mm[1]] || (mm[1] + 'h UTC');
  return '7h';
}}
// Date courte humaine pour l'historique (« lun. 9 juin »). Réutilise formatBulletinDate.
function historyDateHuman(iso) {{
  const d = (iso || '').slice(0, 10);
  const dt = formatBulletinDate(d);
  return dt.short || (iso || '—');
}}
// Date ISO du jour courant (Europe/Paris approx via locale du navigateur) pour
// distinguer la journée en cours dans l'historique.
function todayIso() {{
  const n = new Date();
  const p = (x) => String(x).padStart(2, '0');
  return n.getFullYear() + '-' + p(n.getMonth() + 1) + '-' + p(n.getDate());
}}

function renderHistoryTable() {{
  const tbody = document.getElementById('history-tbody');
  const empty = document.getElementById('history-empty');
  const countEl = document.getElementById('history-count');
  const table = document.getElementById('history-table');
  if (!tbody) return;
  // 1er run : aucune mesure persistée → message de constitution.
  if (!MEASURES || MEASURES.length === 0) {{
    tbody.innerHTML = '';
    if (table) table.hidden = true;
    if (empty) {{ empty.hidden = false; empty.textContent = 'Historique en cours de constitution — les résultats par prédiction apparaîtront ici dès la première mesure d\\'échéance.'; }}
    if (countEl) countEl.textContent = '';
    return;
  }}
  if (table) table.hidden = false;
  const fActif = (document.getElementById('filter-actif') || {{}}).value || '';
  const fHorizon = (document.getElementById('filter-horizon') || {{}}).value || '';
  const fOutcome = (document.getElementById('filter-outcome') || {{}}).value || '';
  let rows = MEASURES.slice();
  if (fActif) rows = rows.filter(m => m.actif === fActif);
  if (fHorizon) rows = rows.filter(m => m.horizon === fHorizon);
  if (fOutcome) rows = rows.filter(m => outcomeClass(m.outcome) === fOutcome);
  // Tri par date décroissante (puis actif/horizon stable).
  rows.sort((a, b) => {{
    const da = (a.bulletin_date || '') + (a.bulletin_id || '');
    const db = (b.bulletin_date || '') + (b.bulletin_id || '');
    if (da < db) return 1;
    if (da > db) return -1;
    return (a.actif || '').localeCompare(b.actif || '');
  }});
  tbody.innerHTML = '';
  const frag = document.createDocumentFragment();
  // Regroupement visuel par jour : on insère une ligne d'en-tête « date » quand
  // le jour change (liste triée par date desc). Au-delà de 12 lignes on active
  // les en-têtes ; en dessous la table reste plate (inutile d'alourdir).
  const useGroups = rows.length > 12;
  const TODAY = todayIso();
  let lastDay = null;
  rows.forEach(m => {{
    const day = (m.bulletin_date || m.bulletin_id || '').slice(0, 10);
    if (useGroups && day && day !== lastDay) {{
      lastDay = day;
      const isToday = (day === TODAY);
      const gtr = document.createElement('tr');
      gtr.className = 'history-day-row' + (isToday ? ' history-day-today' : '');
      gtr.innerHTML = '<td colspan="7">' + historyDateHuman(day)
        + (isToday ? ' <span class="today-pill">aujourd\\'hui</span>' : '') + '</td>';
      frag.appendChild(gtr);
    }}
    const tr = document.createElement('tr');
    if (day === TODAY) tr.classList.add('row-today');
    const cls = outcomeClass(m.outcome);
    const dir = (m.conclusion || '—');
    const dirCls = dir === 'LONG' ? 'dir-long' : (dir === 'SHORT' ? 'dir-short' : '');
    tr.innerHTML =
      '<td>' + historyDateHuman(m.bulletin_date || m.bulletin_id) + '</td>'
      + '<td>' + measureSlot(m) + '</td>'
      + '<td>' + (m.actif || '—') + '</td>'
      + '<td>' + (m.horizon || '—') + '</td>'
      + '<td class="' + dirCls + '">' + dir + '</td>'
      + '<td class="outcome-' + cls + '">' + outcomeBadge(cls, m.outcome) + '</td>'
      + '<td>' + fmtPct(m.realized_pct) + '</td>';
    frag.appendChild(tr);
  }});
  tbody.appendChild(frag);
  if (empty) empty.hidden = true;
  if (countEl) countEl.textContent = rows.length + ' / ' + MEASURES.length + ' décisions';
}}
// Liste des liens de nav de vue auxiliaire (pour gérer l'état .active).
const AUX_NAV_IDS = ['nav-today', 'nav-winrate', 'nav-week', 'nav-history'];
function clearAuxNavActive() {{
  AUX_NAV_IDS.forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.classList.remove('active');
  }});
}}

// Bascule l'UI en mode « vue auxiliaire » (today/week/history) : masque le
// bulletin + sa chrome (légende, sous-nav, aide) et n'affiche QUE la section
// demandée. `sectionId` = id de la <section> à afficher.
function showAuxView(sectionId, navId) {{
  ['today-view', 'winrate-view', 'week-view', 'history-view'].forEach(s => {{
    const el = document.getElementById(s);
    if (el) el.hidden = (s !== sectionId);
  }});
  const bc = document.getElementById('bulletin-content');
  const subnav = document.getElementById('subnav');
  const legend = document.getElementById('legend-bar');
  const help = document.querySelector('.help-box');
  if (bc) bc.hidden = true;
  if (subnav) subnav.style.display = 'none';
  if (legend) legend.style.display = 'none';
  if (help) help.style.display = 'none';
  clearAuxNavActive();
  const nav = document.getElementById(navId);
  if (nav) nav.classList.add('active');
  // [CH-4] titre d'onglet par vue auxiliaire.
  const AUX_TITLES = {{
    'nav-today': 'Aujourd\\'hui', 'nav-winrate': 'Résultats / Win rate',
    'nav-week': 'Bilan semaine', 'nav-history': 'Historique',
  }};
  document.title = `${{AUX_TITLES[navId] || 'Vue'}} · TradingApp v3`;
  renderList(null);
  const mainEl = document.getElementById('bulletin-main');
  if (mainEl) mainEl.scrollTop = 0;
}}

// Quitte toute vue auxiliaire et restaure la vue bulletin (légende, aide…).
function hideAuxViews() {{
  ['today-view', 'winrate-view', 'week-view', 'history-view'].forEach(s => {{
    const el = document.getElementById(s);
    if (el) el.hidden = true;
  }});
  const bc = document.getElementById('bulletin-content');
  const legend = document.getElementById('legend-bar');
  const help = document.querySelector('.help-box');
  if (bc) bc.hidden = false;
  if (legend) legend.style.display = '';
  if (help) help.style.display = '';
  clearAuxNavActive();
}}

function showToday() {{
  buildTodayView();
  showAuxView('today-view', 'nav-today');
  history.replaceState(null, '', '#vue=aujourdhui');
}}
function showWinrate() {{
  buildWinrateView();
  showAuxView('winrate-view', 'nav-winrate');
  history.replaceState(null, '', '#vue=resultats');
}}
function showWeek() {{
  buildWeekView();
  showAuxView('week-view', 'nav-week');
  history.replaceState(null, '', '#vue=semaine');
}}
function showHistory() {{
  if (!HISTORY_BUILT) {{
    // Win rate en tête de l'onglet (résultats principaux), puis A/B replié.
    const hwr = document.getElementById('history-winrate');
    renderWinrateInto(hwr);
    dimEmptyRows(hwr);
    enhanceWinrateRows(hwr);
    buildHistoryFilters();
    buildHistorySummary();
    HISTORY_BUILT = true;
  }}
  renderHistoryTable();
  showAuxView('history-view', 'nav-history');
  history.replaceState(null, '', '#vue=historique');
}}

// --- Rendu markdown mutualisé (suivis, bilans, semaine) -------------------
// Rend `md` dans `target` avec le même pipeline d'enrichissement que les
// bulletins (colorisation LONG/SHORT, tooltips symboles, wrap tables). Fallback
// <pre> si marked.js n'a pas chargé (offline). Réutilisé par toutes les vues.
function renderMarkdownInto(target, md) {{
  if (!target) return;
  if (typeof marked !== 'undefined') {{
    marked.setOptions({{gfm: true, breaks: false}});
    target.innerHTML = marked.parse(md || '');
    // Même pipeline de transformations que la vue bulletin principale : sans
    // ça, le briefing affiché dans « Aujourd'hui » semblait être un AUTRE
    // rapport (mur de texte non replié, hash en tête — incident 11/06). Seule
    // la sous-navigation reste propre à la vue principale (pas de subnav
    // multiple dans l'accordéon par jour).
    relocateDebugMeta(target);
    addLevelBadges(target);
    dimWeakCells(target);
    colorizeDirections(target);
    addSymbolTooltips(target);
    markDenseTables(target);
    wrapTables(target);
    foldSections(target);
  }} else {{
    const pre = document.createElement('pre');
    pre.textContent = md || '';
    target.innerHTML = '';
    target.appendChild(pre);
  }}
}}

// Rapports REPORTS d'une date ISO (YYYY-MM-DD), triés dans l'ordre de lecture
// de la journée : suivi 12h → suivi 18h → bilan du jour (22h). Renvoie [] si
// rien (dégradation propre côté appelants). Helper partagé entre la vue
// « Aujourd'hui » (buildTodayView) et le fil de la vue « Historique »
// (selectBulletin) — un seul ordre canonique, pas de duplication.
function sameDayReports(dateIso) {{
  if (!dateIso) return [];
  const suivis = [];
  let bilan = null;
  REPORTS.forEach(r => {{
    if (r.date !== dateIso) return;
    if (r.kind === 'bilan-jour') bilan = r;
    else suivis.push(r);
  }});
  suivis.sort((a, b) => (a.slot || '').localeCompare(b.slot || ''));
  return bilan ? suivis.concat([bilan]) : suivis;
}}

// Construit la vue « Aujourd'hui » : pour chaque jour (récent d'abord), un
// groupe repliable contenant le briefing 7h + les suivis 12h/18h + le bilan du
// jour. Réutilise BULLETINS (briefings) + REPORTS (suivis/bilans).
function buildTodayView() {{
  const wrap = document.getElementById('today-list');
  const empty = document.getElementById('today-empty');
  if (!wrap) return;
  wrap.innerHTML = '';

  // Regroupe par date ISO (YYYY-MM-DD). Un briefing 7h = un bulletin dont l'id
  // commence par la date ; on extrait juste les 10 premiers caractères.
  const byDay = {{}};  // date -> groupe (briefings)
  const ensure = (d) => (byDay[d] = byDay[d] || {{ briefings: [] }});
  BULLETINS.forEach(b => {{
    const d = (b.id || '').slice(0, 10);
    if (/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(d)) ensure(d).briefings.push(b);
  }});
  REPORTS.forEach(r => {{
    if (r.date) ensure(r.date);  // un jour sans briefing mais avec suivi/bilan reste listé
  }});

  const days = Object.keys(byDay).sort().reverse();
  if (days.length === 0) {{
    if (empty) {{ empty.hidden = false; empty.textContent = "Aucun rapport pour l'instant — les briefings et suivis apparaîtront ici."; }}
    return;
  }}
  if (empty) empty.hidden = true;

  days.forEach((d, di) => {{
    const grp = byDay[d];
    const dt = formatBulletinDate(d);
    const details = document.createElement('details');
    details.className = 'today-day';
    if (di === 0) details.open = true;  // le jour le plus récent ouvert par défaut
    const dayReports = sameDayReports(d);
    const summary = document.createElement('summary');
    const n = grp.briefings.length + dayReports.length;
    summary.innerHTML = '<span>' + dt.short + '</span>'
      + '<span class="day-count">' + n + ' rapport' + (n > 1 ? 's' : '') + '</span>';
    details.appendChild(summary);

    // Ordre de lecture du jour : briefing 7h → suivi 12h → suivi 18h → bilan 22h.
    const ordered = [];
    grp.briefings.forEach(b => ordered.push({{ tag: 'Briefing', slot: b.slot || '7h', md: b.markdown, key: '07' }}));
    dayReports.forEach(r => {{
      const isBilan = r.kind === 'bilan-jour';
      ordered.push({{ tag: isBilan ? 'Bilan' : 'Suivi', slot: isBilan ? '22h' : r.slot, md: r.markdown, key: isBilan ? '22' : r.slot }});
    }});

    ordered.forEach((item, ii) => {{
      const rd = document.createElement('details');
      rd.className = 'today-report';
      if (di === 0 && ii === ordered.length - 1) rd.open = true;  // dernier rapport du jour le + récent ouvert
      const rs = document.createElement('summary');
      rs.innerHTML = '<span class="report-tag">' + item.tag + '</span><span>' + (item.slot || '') + '</span>';
      rd.appendChild(rs);
      const body = document.createElement('div');
      body.className = 'report-body';
      rd.appendChild(body);
      // Rendu paresseux : on ne parse le markdown qu'à la première ouverture.
      let rendered = false;
      const doRender = () => {{ if (!rendered) {{ renderMarkdownInto(body, item.md); rendered = true; }} }};
      rd.addEventListener('toggle', () => {{ if (rd.open) doRender(); }});
      if (rd.open) doRender();
      details.appendChild(rd);
    }});
    wrap.appendChild(details);
  }});
}}

// Titre humain de la semaine ISO depuis l'identité du bilan (label « Semaine
// AAAA-S## » + bornes du markdown « (AAAA-MM-JJ → AAAA-MM-JJ) »). La borne haute
// du fichier est dimanche ; on affiche du lundi au vendredi (jours de bourse).
// Renvoie '' si on ne peut pas reconstituer proprement (zéro invention).
function weekHumanTitle(weekly) {{
  if (!weekly) return '';
  const md = weekly.markdown || '';
  const iso = (weekly.label || '').match(/S(\\d{{2}})/);
  const range = md.match(/(\\d{{4}})-(\\d{{2}})-(\\d{{2}})\\s*→\\s*(\\d{{4}})-(\\d{{2}})-(\\d{{2}})/);
  if (!range) return iso ? ('Semaine ISO ' + iso[1]) : '';
  // Lundi = borne basse ; vendredi = borne basse + 4 jours.
  const lundi = new Date(Date.UTC(+range[1], +range[2] - 1, +range[3]));
  const vendredi = new Date(lundi.getTime() + 4 * 86400000);
  const fmt = (dt) => {{
    const MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
                  'août', 'septembre', 'octobre', 'novembre', 'décembre'];
    return dt.getUTCDate() + ' ' + MOIS[dt.getUTCMonth()];
  }};
  const sem = iso ? ('Semaine ISO ' + iso[1] + ' — ') : '';
  return sem + 'du lundi ' + fmt(lundi) + ' au vendredi ' + fmt(vendredi);
}}

function buildWeekView() {{
  const content = document.getElementById('week-content');
  const empty = document.getElementById('week-empty');
  const titleEl = document.getElementById('week-human-title');
  if (!content) return;
  if (!WEEKLY) {{
    content.innerHTML = '';
    if (titleEl) titleEl.hidden = true;
    if (empty) {{ empty.hidden = false; empty.textContent = 'Aucun bilan de semaine pour le moment — le premier est généré le dimanche suivant (18h), puis chaque dimanche.'; }}
    return;
  }}
  if (empty) empty.hidden = true;
  const human = weekHumanTitle(WEEKLY);
  if (titleEl) {{
    if (human) {{ titleEl.textContent = human; titleEl.hidden = false; }}
    else titleEl.hidden = true;
  }}
  renderMarkdownInto(content, WEEKLY.markdown);
}}

// Rend notre tableau win-rate-only (performance.md) dans `target`. Renvoie true
// si du contenu a été rendu, false si WINRATE_MD est absent (dégradation propre).
function renderWinrateInto(target) {{
  if (!target) return false;
  if (!WINRATE_MD) {{ target.innerHTML = ''; return false; }}
  renderMarkdownInto(target, WINRATE_MD);
  return true;
}}

// Symbole compact d'un verdict (rendu pur, AUCUN recalcul de KPI) :
// VRAI → ✅ · FAUSSE → ❌ · non-conclusive → ⚪. Les autres états
// (non-notee, suivi-interrompu, en-cours…) renvoient '' (ignorés).
function verdictGlyph(outcome) {{
  const o = (outcome || '').toString().trim().toLowerCase();
  if (o === 'vrai' || o.startsWith('vrai')) return '✅';
  if (o === 'fausse' || o === 'faux' || o.startsWith('faus')) return '❌';
  if (o === 'non-conclusive' || o.startsWith('non-concl')) return '⚪';
  return '';  // non-notee / suivi-interrompu / en-cours / inconnu → ignoré
}}

// Construit la séquence des ~10 derniers verdicts chronologiques par cellule
// (actif × horizon), à partir de MEASURES déjà chargé. Affichage compact
// ✅❌⚪ à côté du win rate. Zéro recalcul : on lit seulement `outcome`.
const VERDICT_MAX = 10;
function buildVerdictSequences(host) {{
  if (!host || !MEASURES || MEASURES.length === 0) return;
  // Regroupe par cellule.
  const byCell = {{}};
  MEASURES.forEach(m => {{
    const key = (m.actif || '?') + ' · ' + (m.horizon || '?');
    (byCell[key] = byCell[key] || []).push(m);
  }});
  const cells = Object.keys(byCell).sort();
  if (cells.length === 0) return;

  const section = document.createElement('section');
  section.className = 'verdict-seq';
  const h2 = document.createElement('h2');
  h2.textContent = 'Séquence des verdicts par cellule';
  section.appendChild(h2);
  const intro = document.createElement('p');
  intro.className = 'history-intro';
  intro.innerHTML = "Les ~10 derniers verdicts, du plus ancien au plus récent (à droite) : "
    + '<span class="vg">✅</span> direction juste · <span class="vg">❌</span> fausse · '
    + '<span class="vg">⚪</span> non-conclusive.';
  section.appendChild(intro);

  cells.forEach(key => {{
    // Tri chronologique (ancien → récent) par date puis id de bulletin.
    const rows = byCell[key].slice().sort((a, b) => {{
      const da = (a.bulletin_date || '') + (a.bulletin_id || '');
      const db = (b.bulletin_date || '') + (b.bulletin_id || '');
      return da < db ? -1 : (da > db ? 1 : 0);
    }});
    const glyphs = rows.map(r => verdictGlyph(r.outcome)).filter(g => g);
    if (glyphs.length === 0) return;  // cellule sans verdict conclu → omise
    const tail = glyphs.slice(-VERDICT_MAX);
    const line = document.createElement('div');
    line.className = 'verdict-line';
    const label = document.createElement('span');
    label.className = 'verdict-cell';
    label.textContent = key;
    const seq = document.createElement('span');
    seq.className = 'verdict-glyphs';
    seq.textContent = tail.join(' ');
    line.appendChild(label);
    line.appendChild(seq);
    section.appendChild(line);
  }});

  // N'ajoute la section que si au moins une cellule a un verdict.
  if (section.querySelector('.verdict-line')) host.appendChild(section);
}}

// Explication d'une ligne du bloc « Flip vs continuation » présent dans
// performance.md (ce que ça mesure + pourquoi c'est lié au momentum). On
// l'insère juste AVANT le titre concerné s'il existe — sinon on ne fait rien
// (dégradation propre, zéro invention). Idempotent (classe déjà posée).
function annotateFlipContinuation(root) {{
  if (!root) return;
  const heads = Array.from(root.querySelectorAll('h2, h3'));
  const target = heads.find(h => /flip\\s+vs\\s+continuation/i.test(h.textContent || ''));
  if (!target || target.dataset.flipAnnotated === '1') return;
  target.dataset.flipAnnotated = '1';
  const note = document.createElement('p');
  note.className = 'verdict-flip-note';
  note.innerHTML = "Mesure si les <strong>retournements</strong> de direction (flip) "
    + "réussissent mieux ou moins bien que les <strong>continuations</strong> (même "
    + "direction que la veille). Sentinelle du bug momentum (type cacao) : un système "
    + "qui se trompe surtout sur les flips suit la tendance avec retard.";
  target.parentNode.insertBefore(note, target.nextSibling);
}}

function buildWinrateView() {{
  const content = document.getElementById('winrate-content');
  const empty = document.getElementById('winrate-empty');
  if (!content) return;
  if (renderWinrateInto(content)) {{
    if (empty) empty.hidden = true;
    dimEmptyRows(content);
    enhanceWinrateRows(content);
    annotateFlipContinuation(content);
    buildVerdictSequences(content);
  }} else if (empty) {{
    empty.hidden = false;
    empty.textContent = 'Aucun résultat de win rate disponible pour le moment — les chiffres apparaîtront ici dès les premières mesures.';
  }}
}}

// Ajoute, à la suite du briefing 7h rendu dans `container`, le fil des rapports
// du même jour (suivi 12h → suivi 18h → bilan 22h). Chaque rapport est un
// <details class="day-fil-report"> REPLIÉ, rendu paresseusement via le pipeline
// unifié. Si aucun rapport ce jour-là → n'ajoute rien (zéro séparateur, zéro
// message). Présentation pure : aucune logique métier, aucun scoring.
function appendDayFil(container, id) {{
  if (!container) return;
  const dateIso = (id || '').slice(0, 10);
  const reports = sameDayReports(dateIso);
  if (reports.length === 0) return;  // dégradation propre

  // Séparateur léger « ── La journée ── », uniquement s'il y a ≥1 rapport.
  const sep = document.createElement('div');
  sep.className = 'day-fil-sep';
  sep.textContent = 'La journée';
  container.appendChild(sep);

  const LABELS = {{ '12h': '🕛 Suivi 12h', '18h': '🕕 Suivi 18h' }};
  reports.forEach(r => {{
    const isBilan = r.kind === 'bilan-jour';
    const label = isBilan ? '🌙 Bilan du jour — 22h15' : (LABELS[r.slot] || ('Suivi ' + (r.slot || '')));
    const rd = document.createElement('details');
    rd.className = 'day-fil-report';  // replié par défaut (pas d'attribut open)
    const rs = document.createElement('summary');
    rs.textContent = label;
    rd.appendChild(rs);
    const body = document.createElement('div');
    body.className = 'day-fil-body';
    rd.appendChild(body);
    // Rendu paresseux : on ne parse le markdown qu'à la première ouverture.
    let rendered = false;
    rd.addEventListener('toggle', () => {{
      if (rd.open && !rendered) {{ renderMarkdownInto(body, r.markdown); rendered = true; }}
    }});
    container.appendChild(rd);
  }});
}}

function selectBulletin(id) {{
  hideAuxViews();
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
    relocateDebugMeta(content);
    addLevelBadges(content);
    dimWeakCells(content);
    colorizeDirections(content);
    addSymbolTooltips(content);
    markDenseTables(content);
    wrapTables(content);
    // buildSubnav AVANT foldSections : il pose les ids sur tous les <h2> ;
    // foldSections les reprend sur le <summary> pour garder l'ancrage. Un clic
    // sous-nav vers une section repliée l'ouvre alors (openFoldedSectionFor).
    buildSubnav(content);
    foldSections(content);
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
  // Le fil complet de la journée sous le briefing 7h : suivi 12h → suivi 18h →
  // bilan 22h (REPORTS, 30 derniers jours). Chaque rapport en <details> REPLIÉ —
  // le briefing reste la lecture primaire. Dégradation propre : aucun rapport du
  // jour (bulletin pré-refonte ou > 30 jours) → on n'ajoute RIEN.
  appendDayFil(content, b.id);
  history.replaceState(null, '', '#' + encodeURIComponent(id));
  renderList(id);
  // [CH-4 audit visuel 12/06] : le titre d'onglet reflète le bulletin actif
  // (utile quand l'onglet reste ouvert toute la journée). Ex. « Briefing — mer.
  // 12 juin · 7h ».
  const dt = formatBulletinDate(b.id);
  const tt = dt.time ? ` · ${{dt.time}}` : '';
  document.title = `Briefing — ${{dt.short}}${{tt}} · TradingApp v3`;
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

  // Liens de vues auxiliaires de la sidebar (Aujourd'hui / Bilan semaine / Historique).
  const bindNav = (id, fn) => {{
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', (e) => {{ e.preventDefault(); fn(); closeSidebarMobile(); }});
  }};
  bindNav('nav-today', showToday);
  bindNav('nav-winrate', showWinrate);
  bindNav('nav-week', showWeek);
  bindNav('nav-history', showHistory);

  const rawHash = (location.hash || '').replace(/^#/, '');
  // Routage des vues auxiliaires (avant la résolution d'un bulletin par id).
  if (rawHash === 'vue=aujourdhui') {{ showToday(); return; }}
  if (rawHash === 'vue=resultats') {{ showWinrate(); return; }}
  if (rawHash === 'vue=semaine') {{ showWeek(); return; }}
  if (rawHash === 'vue=historique') {{ showHistory(); return; }}

  if (BULLETINS.length === 0) {{
    // Pas de bulletin mais peut-être des suivis/bilans → on ouvre « Aujourd'hui »
    // si disponible, sinon un message neutre.
    if (REPORTS.length > 0) {{ showToday(); return; }}
    document.getElementById('bulletin-content').innerHTML = '<p>Aucun bulletin disponible.</p>';
    const subnav = document.getElementById('subnav');
    if (subnav) subnav.style.display = 'none';
    return;
  }}
  const hash = decodeURIComponent(rawHash);
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
    measures = load_measures()
    perf_ab = parse_perf_ab_summary()
    reports = build_reports_payload()
    weekly = build_weekly_payload()
    performance_md = load_performance_md()
    html = render_html(
        payload, total, measures=measures, perf_ab=perf_ab,
        reports=reports, weekly=weekly, performance_md=performance_md,
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    n_suivi = sum(1 for r in reports if r["kind"] == "suivi")
    n_bilan = sum(1 for r in reports if r["kind"] == "bilan-jour")
    print(
        f"[build_html] {len(payload)}/{total} bulletins + {n_suivi} suivis + "
        f"{n_bilan} bilans-jour + {'1' if weekly else '0'} bilan-semaine + "
        f"{'1' if performance_md else '0'} win-rate + "
        f"{len(measures)} mesures embarqués → {OUT_PATH} ({OUT_PATH.stat().st_size} octets)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
