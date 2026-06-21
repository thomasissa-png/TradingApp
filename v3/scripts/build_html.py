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
# Rapport hebdo du Manager (5 sections) : v3/data/bilan-semaine/YYYY-S##.md.
# C'est CE rapport qui doit s'afficher dans la vue « Bilan semaine » (et non
# l'archive win-rate ci-dessus). La plage (lundi → dimanche) est dans le markdown.
BILAN_SEMAINE_DIR = ROOT / "data" / "bilan-semaine"
RE_BILAN_SEMAINE = re.compile(r"^(\d{4})-S(\d{2})\.md$")
RE_WEEK_RANGE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*→\s*(\d{4}-\d{2}-\d{2})")


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


def build_weeklies_payload(weekly_dir: Path = BILAN_SEMAINE_DIR) -> List[Dict[str, str]]:
    """Tous les bilans de semaine du Manager (rapport 5 sections), récents d'abord.

    Lit `v3/data/bilan-semaine/YYYY-S##.md` (et NON l'archive win-rate). Chaque
    entrée : id, label (« Semaine AAAA-S## »), sunday (date ISO = fin de plage du
    markdown, pour ranger dans le menu au dimanche), filename, markdown. Dossier
    absent/vide → [] (la vue « Bilan semaine » est alors masquée, dégradation propre).
    """
    if not weekly_dir.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for p in weekly_dir.glob("*.md"):
        m = RE_BILAN_SEMAINE.match(p.name)
        if not m:
            continue
        md = _read_md(p)
        rng = RE_WEEK_RANGE.search(md)
        rows.append({
            "_key": (int(m.group(1)), int(m.group(2))),
            "id": f"weekly-{p.stem}",
            "label": f"Semaine {m.group(1)}-S{m.group(2)}",
            "sunday": rng.group(2) if rng else "",
            "filename": p.name,
            "markdown": md,
        })
    rows.sort(key=lambda r: r["_key"], reverse=True)
    for r in rows:
        r.pop("_key", None)
    return rows


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
    weeklies: Optional[List[Dict[str, str]]] = None,
    performance_md: Optional[str] = None,
) -> str:
    """Génère le HTML autonome."""
    # Timestamp de génération en libellé FR lisible (refonte S9 : plus de format
    # machine « 2026-06-20 14:30 UTC » dans l'interface ; il vit en pied de page).
    _now = datetime.now(timezone.utc)
    _MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
                "août", "septembre", "octobre", "novembre", "décembre"]
    generated_at_iso = _now.strftime("%Y-%m-%dT%H:%M:%SZ")
    generated_at = f"{_now.day} {_MOIS_FR[_now.month - 1]} {_now.year} · {_now:%Hh%M} (UTC)"
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
    # Tous les bilans de semaine (pour le menu historique : datés au dimanche).
    weeklies_js = _entries_to_js(weeklies or [], ["id", "label", "sunday", "filename"])

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
            f"<span class=\"meta-note\">({embedded} sur {total_count} bulletins embarqués, "
            f"les {embedded} plus récents)</span>"
        )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TradingApp v3 · Bulletins</title>
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
    --accent-strong: #1d4ed8;
    --accent-bg: #eff6ff;
    --accent-tint: #f5f8ff;
    --code-bg: #f1f5f9;
    --row-alt: #f8fafc;
    --badge-bg: #16a34a;
    --badge-text: #ffffff;
    --th-bg: #f1f5f9;
    --dir-long-color: #15803d;
    --dir-short-color: #b91c1c;
    /* Badge statut « mode test » — discret (refonte header S9). */
    --status-bg: #0f1c2e;
    --status-border: #1d3045;
    --status-text: #64748b;
    --status-dot: #f59e0b;
    --header-divider: #253348;
    /* Ombres douces (refonte design S9 vague 4) — donnent du relief aux cartes
       sans alourdir : la page « respire » au lieu d'empiler des filets 1px. */
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04), 0 1px 3px rgba(15, 23, 42, 0.06);
    --shadow-md: 0 2px 4px rgba(15, 23, 42, 0.05), 0 4px 12px rgba(15, 23, 42, 0.07);
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
      --accent-strong: #93c5fd;
      --accent-tint: #16243c;
      --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2), 0 1px 3px rgba(0, 0, 0, 0.28);
      --shadow-md: 0 2px 4px rgba(0, 0, 0, 0.24), 0 4px 12px rgba(0, 0, 0, 0.32);
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
  /* HEADER — ligne unique, sticky, 48px (refonte design S9 vague 4). Marque
     produit avec pastille accent (identité visuelle) + statut « mode test »
     discret, le tout sur une seule ligne. Ombre douce sous le header pour le
     détacher du contenu au scroll. */
  header {{
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    padding: 0 22px;
    position: sticky; top: 0; z-index: 20;
    height: 48px;
    display: flex; align-items: center;
  }}
  header .header-row {{ display: flex; align-items: center; gap: 10px; width: 100%; }}
  /* Marque : pastille accent + nom. Cliquable → retour « Aujourd'hui ». */
  .brand {{
    display: flex; align-items: center; gap: 9px; flex: 1; min-width: 0;
    text-decoration: none; color: var(--text);
  }}
  .brand-mark {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 7px; flex-shrink: 0;
    background: linear-gradient(135deg, var(--accent), var(--accent-strong));
    color: #fff; font-size: 14px; font-weight: 800; line-height: 1;
    box-shadow: var(--shadow-sm);
  }}
  .brand-name {{
    font-size: 15px; font-weight: 700; letter-spacing: -0.01em; color: var(--text);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1;
  }}
  .brand-name .brand-v {{ color: var(--text-muted); font-weight: 600; }}
  .brand-name .brand-sub {{
    color: var(--text-muted); font-weight: 500; font-size: 13px; margin-left: 2px;
  }}
  header .meta-note {{ font-size: 11px; color: var(--text-muted); margin-left: 6px; }}
  /* Badge statut « mode test » — inline, côté droit, point ambre + texte discret. */
  .header-status {{ display: flex; align-items: center; gap: 6px; flex-shrink: 0; }}
  .header-status-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--status-dot); flex-shrink: 0;
  }}
  .header-status-text {{
    font-size: 11px; font-weight: 500; color: var(--status-text); white-space: nowrap;
  }}
  @media (max-width: 380px) {{ .header-status-date {{ display: none; }} }}
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
  .hamburger:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .layout {{
    display: flex;
    height: calc(100vh - 48px);
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
  /* [Refonte S9 — point #6] La barre de légende redondante (« 🟢 LONG = hausse …
     ❓ Symboles ») a été supprimée : LONG/SHORT est évident à la lecture et les
     symboles vivent désormais UNIQUEMENT dans le help-box « ❓ Comment lire ».
     Plus de chrome permanent sous le header → la page respire. */
  /* Date de génération — discrète, en pied de contenu (refonte S9). */
  .gen-meta {{ margin-top: 40px; font-size: 11px; color: var(--text-muted); text-align: right; }}
  /* Sous-navigation d'ancres intra-bulletin (seule barre sticky sous le header) */
  .subnav {{
    position: static;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    padding: 6px 20px;
    font-size: 13px;
  }}
  /* [Refonte S9 — (C)] La subnav WRAPPE proprement (PC et mobile) plutôt que de
     scroller horizontalement : l'ensemble des pastilles (≤ ~10) tient sur 1-2
     lignes, toujours visibles, sans geste de scroll caché. */
  .subnav .subnav-inner {{
    max-width: 900px; margin: 0 auto;
    display: flex; flex-wrap: wrap; gap: 5px 4px; align-items: center;
  }}
  .subnav a {{
    color: var(--accent);
    text-decoration: none;
    padding: 3px 10px;
    border-radius: 999px;
    background: var(--accent-bg);
    font-size: 12px;
    border: 1px solid transparent;
    white-space: nowrap;
    flex-shrink: 0;
  }}
  .subnav a:hover {{ border-color: var(--accent); }}
  .subnav a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .subnav .subnav-label {{ color: var(--text-muted); font-size: 11px; margin-right: 4px; flex-shrink: 0; }}
  main h1, main h2, main h3 {{ color: var(--text); }}
  main h1 {{
    font-size: 28px; font-weight: 800; letter-spacing: -0.02em;
    border-bottom: 2px solid var(--border); padding-bottom: 12px; margin-top: 8px;
    line-height: 1.25;
  }}
  /* H2 : repère d'accent à gauche (barre verticale) qui donne une identité à
     chaque section sans alourdir — l'œil retrouve les sections d'un coup. */
  main h2 {{
    font-size: 21px; font-weight: 700; letter-spacing: -0.01em;
    margin-top: 42px; padding: 2px 0 8px 14px; position: relative;
    border-bottom: 1px solid var(--border); scroll-margin-top: 104px;
  }}
  main h2::before {{
    content: ""; position: absolute; left: 0; top: 4px; bottom: 10px;
    width: 4px; border-radius: 3px;
    background: linear-gradient(var(--accent), var(--accent-strong));
  }}
  main h3 {{ font-size: 16.5px; font-weight: 700; margin-top: 26px; scroll-margin-top: 104px; }}
  main p {{ margin: 11px 0; }}
  /* Paragraphe d'accroche (premier paragraphe d'une vue, sous le H1) : un peu
     plus grand, posé, pour inviter à la lecture. */
  main .lead {{ font-size: 16px; color: var(--text-muted); margin: 10px 0 22px 0; line-height: 1.55; }}
  /* [Refonte S9 vague 3 — encart Sélection] Carte distincte et discrète qui
     détache l'encart « Sélection (max 3) » en tête de « Décision du jour ».
     Cohérente avec les tokens dark-mode (bg-panel + accent). Épurée : un filet
     accent à gauche, un fond panneau, un padding raisonnable. Ne déborde pas
     (overflow géré par .table-wrap interne) et reste lisible sur mobile. */
  .decision-selection {{
    background: var(--bg-panel);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 18px 0 8px;
    box-shadow: var(--shadow-sm);
  }}
  .decision-selection > h3:first-child {{ margin-top: 0; }}
  .decision-selection .table-wrap {{ margin-bottom: 0; }}
  @media (max-width: 640px) {{
    .decision-selection {{ padding: 12px 12px; border-radius: 6px; }}
  }}
  /* Wrapper de table pour scroll horizontal mobile propre. [Point #2] Indice de
     scroll : une ombre dégradée sur le bord droit signale qu'on peut faire
     défiler horizontalement (CSS pur, via background-attachment local + radial).
     Disparaît une fois arrivé au bout du scroll. */
  .table-wrap {{
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin: 16px 0;
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
    background:
      linear-gradient(to right, var(--bg-panel) 30%, rgba(255,255,255,0)),
      linear-gradient(to left, var(--bg-panel) 30%, rgba(255,255,255,0)) 100% 0,
      radial-gradient(farthest-side at 0 50%, rgba(15,23,42,0.18), rgba(0,0,0,0)),
      radial-gradient(farthest-side at 100% 50%, rgba(15,23,42,0.18), rgba(0,0,0,0)) 100% 0;
    background-repeat: no-repeat;
    background-size: 28px 100%, 28px 100%, 14px 100%, 14px 100%;
    background-attachment: local, local, scroll, scroll;
  }}
  main table {{ border-collapse: collapse; margin: 0; font-size: 13.5px; width: 100%; }}
  main table th, main table td {{
    border-bottom: 1px solid var(--border);
    padding: 10px 13px; text-align: left;
    vertical-align: top;
  }}
  main table th {{
    background: var(--th-bg); font-weight: 700;
    font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--text-muted);
    border-bottom: 2px solid var(--border-strong);
    white-space: nowrap;
  }}
  main table tbody tr:nth-child(even) {{ background: var(--row-alt); }}
  main table tbody tr:hover {{ background: var(--accent-bg); }}
  /* [Point #3] Raison explicative (2e ligne d'une cellule de Synthèse) : la
     LOGIQUE, pas un nom. S'enroule proprement (jamais coupée en plein mot), même
     là où les cellules passent en nowrap sur mobile. Grisée, plus petite. */
  main table td .cell-reason {{
    display: block; margin-top: 3px;
    font-size: 11.5px; font-weight: 400; color: var(--text-muted);
    white-space: normal; overflow-wrap: normal; word-break: normal; line-height: 1.3;
  }}
  /* En-têtes à double libellé (tableau Sélection) : complet par défaut (desktop),
     court sur mobile. La version courte est masquée hors mobile. */
  .c-short {{ display: none; }}
  /* ── MARQUEUR « CHANGEMENT DE TENDANCE » (vs la veille) ───────────────────
     Une cellule (actif × horizon) dont la direction LONG/SHORT DIFFÈRE de la
     veille reçoit, EN TÊTE de cellule, le glyphe ⇌ (U+21CC) + un liseré gauche
     ambre. Le liseré est posé via :has() sur le <td> contenant le glyphe — pas
     de classe à injecter dans le markdown→td. Token : --status-dot (#f59e0b).
     Double-codage forme (⇌) + couleur (ambre) → OK daltonien. */
  .trend-flip {{ color: var(--status-dot); font-weight: 700; margin-right: 3px; }}
  main table td:has(.trend-flip) {{
    border-left: 3px solid var(--status-dot); padding-left: 9px;
  }}
  main code {{ background: var(--code-bg); padding: 1px 5px; border-radius: 3px; font-size: 13px; }}
  main pre {{ background: var(--code-bg); padding: 12px; border-radius: 6px; overflow-x: auto; }}
  main pre code {{ background: none; padding: 0; }}
  /* Citations = notes explicatives (omniprésentes dans les bilans). Fond teinté
     accent + filet accent : on les lit comme des « aides de lecture », pas comme
     du texte mort. Coins arrondis, italique léger retiré pour la lisibilité. */
  main blockquote {{
    border-left: 3px solid var(--accent); margin: 14px 0; padding: 10px 16px;
    background: var(--accent-tint); border-radius: 0 8px 8px 0;
    color: var(--text-muted); font-size: 14px; line-height: 1.55;
  }}
  main blockquote p {{ margin: 4px 0; }}
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
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
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
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
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
  /* Annexe technique du bilan semaine — repliée, même langage visuel que les
     folds. Sort les tableaux denses des sections d'analyse (3/4). */
  .weekly-annex {{
    border: 1px solid var(--border); border-radius: 8px; box-shadow: var(--shadow-sm);
    margin: 28px 0 0 0; background: var(--bg-panel); padding: 0 16px;
  }}
  .weekly-annex > summary {{
    cursor: pointer; padding: 12px 0; font-weight: 700; color: var(--text);
    list-style: none; user-select: none;
  }}
  .weekly-annex > summary::-webkit-details-marker {{ display: none; }}
  .weekly-annex > summary::before {{
    content: "▸"; display: inline-block; margin-right: 8px;
    transition: transform 0.15s ease; color: var(--text-muted);
  }}
  .weekly-annex[open] > summary::before {{ transform: rotate(90deg); }}
  .weekly-annex h3 {{ font-size: 14.5px; }}
  /* Navigation des vues (Historique) en tête de sidebar */
  #nav-views {{ list-style: none; margin: 0; padding: 0; border-bottom: 1px solid var(--border); }}
  .nav-view-link {{
    display: block; text-decoration: none;
    padding: 12px 16px; color: var(--text);
    border-left: 3px solid transparent; font-weight: 600; font-size: 13.5px;
  }}
  .nav-view-link:hover {{ background: var(--accent-bg); }}
  .nav-view-link.active {{ background: var(--accent-bg); border-left-color: var(--accent); color: var(--accent-strong); }}
  .nav-section-label {{
    padding: 8px 16px 4px 16px; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.04em; color: var(--text-muted); font-weight: 600;
  }}
  /* Vues Aujourd'hui / Bilan semaine / Historique */
  .history-intro {{ color: var(--text-muted); margin: 4px 0 18px 0; }}
  /* Vue jour : menu d'onglets (Briefing par défaut + Suivi/Bilan), 1 rapport à la fois. */
  .day-tabs {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0 16px 0; }}
  .day-tab {{
    font: inherit; font-size: 12.5px; padding: 5px 12px;
    border: 1px solid var(--border); border-radius: 999px;
    background: var(--bg-panel); color: var(--text-muted); cursor: pointer;
  }}
  .day-tab:hover {{ border-color: var(--accent); }}
  .day-tab.active {{ background: var(--accent-bg); border-color: var(--accent); color: var(--text); font-weight: 600; }}
  .day-tab:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  /* Titre humain de la semaine (lundi → vendredi) — sous le H1 « Bilan semaine ». */
  .week-human-title {{
    font-size: 15px; font-weight: 600; color: var(--text);
    margin: 2px 0 4px 0;
  }}
  /* Vue Aujourd'hui : un groupe replié par jour, chaque rapport en sous-bloc */
  .today-day {{
    border: 1px solid var(--border); border-radius: 10px; margin: 0 0 18px 0;
    background: var(--bg-panel); overflow: hidden; box-shadow: var(--shadow-sm);
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
    header {{ height: 44px; padding: 0 12px; }}
    .brand-name {{ font-size: 14px; }}
    .brand-name .brand-sub {{ display: none; }}  /* gain de place : « · Bulletins » masqué sur mobile */
    .brand-mark {{ width: 23px; height: 23px; font-size: 12px; }}
    .header-status-text {{ font-size: 10px; }}
    .layout {{ height: calc(100vh - 44px); }}
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
    .subnav {{ padding: 5px 12px; }}
    .subnav a {{ font-size: 11.5px; padding: 3px 8px; }}
    .subnav .subnav-label {{ width: 100%; margin-bottom: 2px; }}
    /* La subnav wrappe désormais sur ~2 lignes sous un header de 40px : on
       décale l'ancrage des titres pour qu'ils ne passent pas sous le chrome. */
    main h1 {{ font-size: 22px; }}
    main h2 {{ font-size: 18px; margin-top: 28px; scroll-margin-top: 110px; }}
    main h3 {{ font-size: 15.5px; scroll-margin-top: 110px; }}
    /* [Point #2] Anti-débordement horizontal du TEXTE EN PROSE uniquement (URL,
       hash) : on casse les mots longs dans les paragraphes/listes/résumés. Les
       CELLULES DE TABLEAU sont volontairement EXCLUES : casser « Arabica » en
       « Arabi/ca » ou « -13.19 » en « -13./19 » est illisible. Les tables gèrent
       leur largeur par scroll horizontal (.table-wrap) + nowrap par cellule. */
    main p, main li, main summary {{ overflow-wrap: anywhere; }}
    /* [Point #2] Cellules de tableau : aucun mot/nombre coupé. Les tables larges
       débordent dans .table-wrap (scroll horizontal propre, indice ci-dessous).
       Les libellés d'actif multi-mots (« S&P 500 », « Café (Arabica) ») peuvent
       passer à la ligne entre MOTS (normal) mais jamais à l'intérieur d'un mot. */
    main table td, main table th {{ white-space: nowrap; overflow-wrap: normal; word-break: keep-all; }}
    /* [Point #3] Sur mobile, la phrase de raison s'enroule en 2-3 lignes dans une
       largeur bornée (sinon elle étire la colonne et force un long scroll). */
    main table td .cell-reason {{ max-width: 58vw; white-space: normal; }}
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
    /* [Refonte suivi S9] Tableau « Sélection du jour — progression » (6 col.,
       vue rapide en tête du suivi). Sur mobile, les 6 colonnes ne tiennent pas
       à 390px → on resserre police + padding pour cette table UNIQUEMENT, afin
       que la colonne « Vendre / Pas vendre » (la reco, la plus importante) reste
       visible sans scroll horizontal. Classe posée en JS sur l'en-tête signature
       « % vs ouv. 12h ». */
    .selection-progression, .bilan-perf-table {{ font-size: 12px; }}
    .selection-progression th, .selection-progression td,
    .bilan-perf-table th, .bilan-perf-table td {{ padding: 7px 6px; }}
    /* À 390px les colonnes ne tiennent pas toutes. On masque UNE colonne par table,
       jamais une colonne « résultat ». SUIVI : masque « Tendance » (col 5) ; la
       progression 12h/18h + la reco « Vendre ? » restent. BILAN : masque
       l'intermédiaire « 18h » (col 4) ; la CLÔTURE (col 5, résultat final) et le
       Pic (col 6) restent TOUJOURS visibles. */
    .selection-progression td:nth-child(6),
    .selection-progression th:nth-child(6) {{ display: none; }}
    .bilan-perf-table td:nth-child(4),
    .bilan-perf-table th:nth-child(4) {{ display: none; }}
    /* En-têtes : version courte sur mobile (la complète prend trop de largeur) —
       pour les DEUX tables (suivi + bilan). */
    .selection-progression .c-full, .bilan-perf-table .c-full {{ display: none; }}
    .selection-progression .c-short, .bilan-perf-table .c-short {{ display: inline; }}
  }}
</style>
</head>
<body>
<header>
  <div class="header-row">
    <button class="hamburger" id="hamburger" aria-label="Ouvrir la liste des bulletins" aria-expanded="false">☰</button>
    <a class="brand" href="#vue=aujourdhui" aria-label="TradingApp v3 — accueil">
      <span class="brand-mark" aria-hidden="true">▲</span>
      <span class="brand-name">TradingApp <span class="brand-v">v3</span><span class="brand-sub">· Bulletins</span></span>
    </a>
    <div class="header-status" role="status" aria-label="Statut : mode test, go-live le 08/08">
      <span class="header-status-dot" aria-hidden="true"></span>
      <span class="header-status-text">Mode test<span class="header-status-date"> · go-live 08/08</span></span>
    </div>
  </div>
</header>
<div class="sidebar-overlay" id="sidebar-overlay"></div>
<div class="layout">
  <aside id="sidebar">
    <ul id="nav-views">
      <li><a href="#vue=aujourdhui" id="nav-today" class="nav-view-link">📅 Aujourd'hui</a></li>
      <li><a href="#vue=semaine" id="nav-week" class="nav-view-link">🗓️ Bilan semaine</a></li>
      <li><a href="#vue=performance" id="nav-history" class="nav-view-link">📊 Performance</a></li>
    </ul>
    <div class="nav-section-label">Bulletins</div>
    <ul id="bulletin-list"></ul>
  </aside>
  <main id="bulletin-main">
    <nav class="subnav" id="subnav" aria-label="Sections du bulletin">
      <div class="subnav-inner">
        <span class="subnav-label">Sauter à :</span>
        <span id="subnav-links"></span>
      </div>
    </nav>
    <div class="content-inner">
      <details class="help-box" id="help-box">
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
          <p><strong>Symboles</strong> (la légende du bulletin ne liste que ceux réellement présents) :</p>
          <ul>
            <li><code>🚫</code> données insuffisantes · <code>⚑</code> gate régime · <code>📰</code> news&gt;50% du quant</li>
            <li><code>⚪</code> quasi coin-flip, non-actionnable · <code>≈</code> quasi-neutre (sous la bande de décision)</li>
            <li><code>⚠</code> divergence primaire/pondéré · <code>↯</code> divergence quant/news · <code>◧</code> mono-critère (une seule donnée porte la décision)</li>
            <li><code>⇄</code> contre-momentum (bouge à contre-sens depuis la dernière clôture vue) · <code>⇆</code> zigzag (direction instable) · <code>⌛</code> déjà coté (la news est dans le prix)</li>
            <li><code>⚭</code> driver macro partagé (plusieurs cellules portées par le même pari) · <code>🔴</code> alerte · <code>🟡</code> vigilance</li>
          </ul>
        </div>
      </details>
      <div id="bulletin-content">
        <p>Chargement...</p>
      </div>
      <section id="today-view" hidden aria-label="Rapports d'aujourd'hui">
        <h1>📅 Aujourd'hui</h1>
        <p class="lead">Le briefing du matin et les suivis de la journée, regroupés par jour. Le plus récent en premier.</p>
        <div id="today-list"></div>
        <p id="today-empty" hidden></p>
      </section>
      <section id="week-view" hidden aria-label="Bilan de la semaine">
        <h1>🗓️ Bilan semaine</h1>
        <p id="week-human-title" class="week-human-title" hidden></p>
        <p class="history-intro">WIN RATE ONLY · jamais d'euros. Le Manager propose, Thomas valide.</p>
        <div id="week-content"></div>
        <p id="week-empty" hidden></p>
      </section>
      <section id="history-view" hidden aria-label="Performance : win rate et historique des décisions">
        <h1>📊 Performance</h1>
        <p class="lead">Ce qui marche : le win rate par actif et par horizon (le taux de bonnes directions), puis le détail décision par décision.</p>
        <p class="history-intro">Deux mesures : le <strong>Win rate</strong> (sur les paris conclus) et le <strong>WR tradable</strong> (VRAI / VRAI+FAUSSE+non-conclusif, qui inclut les jours sous seuil où une position aurait quand même été prise, donc toujours ≤ Win rate). <strong>⏳ trop peu (N/15)</strong> = il faut au moins 15 paris indépendants par cellule pour qu'un chiffre soit fiable ; en dessous, le taux affiché ne veut encore rien dire.</p>
        <div class="winrate-warmup" role="note">
          <strong>Tout est en chauffe.</strong> Les 12 actifs ont été remis à zéro le <strong>11 juin 2026</strong> (passage en ère v2 du moteur). La mesure ouverture→clôture, 1 décision notée par jour, tourne depuis le 9 juin. Premier point de contrôle : le <strong>8 août 2026</strong>, une cellule 24h se trade alors uniquement si son WR tradable ≥&nbsp;70&nbsp;% sur ≥&nbsp;15 paris (règle de sélection gravée, mode test jusque-là).
        </div>
        <div id="history-winrate"></div>
        <details class="fold-section" id="history-ab-fold">
          <summary>Détail technique par cellule (calibration ±1)</summary>
          <p class="history-intro" style="margin-top:8px;">Taux et calibration internes par cellule (secondaire, conservé pour le suivi technique).</p>
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
      <p class="gen-meta" aria-label="Date de génération de la page">
        Page générée le <time datetime="{generated_at_iso}">{generated_at}</time>{truncated_note}
      </p>
    </div>
  </main>
</div>
<script>
const BULLETINS = {bulletins_js};
const REPORTS = {reports_js};   // suivis 12h/18h + bilans du jour (22h), plus récent d'abord
const WEEKLY = {weekly_js};     // bilan de semaine le plus récent (ou null)
const WEEKLIES = {weeklies_js}; // tous les bilans de semaine (datés au dimanche, pour le menu)
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

// --- [Point #5] formate une date ISO8601 en libellé FR lisible --------------
// "2026-06-19T08:08:09.816553+02:00" → "19 juin 2026, 08h08".
// Robuste : accepte AUSSI le format FR déjà lisible émis par les scripts Python
// (« 19 juin 2026, 08h08 ») → renvoyé tel quel. Si rien ne matche, renvoie la
// chaîne d'origine (zéro crash, zéro invention).
const MONTHS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                   'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
function formatIsoHuman(iso) {{
  const s = (iso || '').trim();
  // Déjà au format FR lisible (émis par les scripts Python) → inchangé.
  if (/^\\d{{1,2}}\\s+[a-zéûôî]+\\s+\\d{{4}},\\s+\\d{{2}}h\\d{{2}}$/i.test(s)) return s;
  const m = s.match(/(\\d{{4}})-(\\d{{2}})-(\\d{{2}})T(\\d{{2}}):(\\d{{2}})/);
  if (!m) return s;
  const d = parseInt(m[3], 10);
  const mois = MONTHS_FR[parseInt(m[2], 10) - 1] || m[2];
  return `${{d}} ${{mois}} ${{m[1]}}, ${{m[4]}}h${{m[5]}}`;
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

// Liste des JOURS de l'historique : une seule entrée par date (déduplication),
// sans heure/créneau dans le libellé (« ven. 19 juin »). Un jour = un clic qui
// ouvre TOUS ses rapports groupés et dépliables (cf. selectDay), comme la vue
// « Aujourd'hui ». On garde, par date, le bulletin le plus récent comme ancre
// (BULLETINS est déjà trié décroissant par build_payload). Les jours qui n'ont
// que des suivis/bilans (REPORTS) mais aucun briefing apparaissent aussi.
function listDays() {{
  const byDay = {{}};  // date ISO -> {{ date, briefingId }}
  BULLETINS.forEach(b => {{
    const d = (b.id || '').slice(0, 10);
    if (!/^\\d{{4}}-\\d{{2}}-\\d{{2}}$/.test(d)) return;
    if (!byDay[d]) byDay[d] = {{ date: d, briefingId: b.id }};  // 1er = plus récent du jour
  }});
  REPORTS.forEach(r => {{
    if (r.date && !byDay[r.date]) byDay[r.date] = {{ date: r.date, briefingId: null }};
  }});
  return Object.values(byDay).sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
}}

function renderList(activeDate) {{
  const ul = document.getElementById('bulletin-list');
  ul.innerHTML = '';
  const days = listDays();
  const latestDate = days.length > 0 ? days[0].date : null;
  // Entrées combinées, triées par date décroissante : les JOURS (briefing +
  // suivis + bilan) et les BILANS DE SEMAINE (datés à leur dimanche, marqués
  // « (bilan) ») pour les retrouver facilement, en ligne avec les jours.
  const entries = [];
  days.forEach(d => entries.push({{ kind: 'day', date: d.date }}));
  (WEEKLIES || []).forEach(w => {{ if (w.sunday) entries.push({{ kind: 'week', date: w.sunday, weekly: w }}); }});
  entries.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : (a.kind === 'week' ? -1 : 1)));
  entries.forEach(en => {{
    const li = document.createElement('li');
    const a = document.createElement('a');
    const dt = formatBulletinDate(en.date);
    const dateSpan = document.createElement('span');
    dateSpan.className = 'item-date';
    if (en.kind === 'week') {{
      // Bilan de semaine : « dim. JJ mois (bilan) » → ouvre la vue Bilan semaine.
      a.href = '#vue=semaine';
      a.classList.add('week-entry');
      dateSpan.textContent = dt.short + ' (bilan)';
      a.appendChild(dateSpan);
      a.onclick = (e) => {{ e.preventDefault(); showWeek(en.weekly); closeSidebarMobile(); }};
    }} else {{
      // Pas d'heure : un jour = une entrée. Ex. « ven. 19 juin ».
      a.href = '#jour=' + encodeURIComponent(en.date);
      dateSpan.textContent = dt.short;
      a.appendChild(dateSpan);
      // Repère « jour le plus récent » : un léger gras suffit. La pastille verte
      // « DERNIER » a été retirée (refonte S9) — redondante avec le tri (le plus
      // récent est toujours en tête) et avec l'entrée « 📅 Aujourd'hui ».
      if (en.date === latestDate) a.classList.add('latest');
      if (en.date === activeDate) a.classList.add('active');
      a.onclick = (e) => {{
        e.preventDefault();
        selectDay(en.date);
        closeSidebarMobile();
      }};
    }}
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

// [Refonte suivi S9] Tague le tableau « Sélection du jour — progression » des
// suivis (6 col.) par sa signature d'en-tête « % vs ouv. 12h », pour le resserrer
// sur mobile (CSS .selection-progression) sans masquer aucune colonne — la reco
// « Vendre / Pas vendre » reste visible. marked rend les tables sans classe → on
// cible par texte d'en-tête (zéro faux positif : libellé unique au suivi).
function markSelectionTables(root) {{
  if (!root) return;
  root.querySelectorAll('table').forEach(t => {{
    const headRow = t.querySelector('thead tr') || t.querySelector('tr');
    if (!headRow) return;
    const heads = Array.from(headRow.querySelectorAll('th, td')).map(c => (c.textContent || '').trim());
    // Suivi : tableau « Sélection du jour — progression » (en-tête « % vs ouv. 12h »).
    if (heads.some(h => h.indexOf('% vs ouv. 12h') !== -1)) t.classList.add('selection-progression');
    // Bilan : tableau « Performance 24h du Top 3 » (en-tête « % fav. 12h »). Classe
    // DISTINCTE : libellés courts actifs sur mobile, mais on masque un INTERMÉDIAIRE
    // (18h), JAMAIS la clôture (résultat final) ni le Pic.
    if (heads.some(h => h.indexOf('% fav. 12h') !== -1)) t.classList.add('bilan-perf-table');
  }});
}}

// [Refonte S9 vague 3 — encart Sélection] Enveloppe le sous-bloc « Sélection
// (max 3) » de « Décision du jour » dans une carte .decision-selection pour le
// détacher visuellement. On repère le <h3> dont le texte commence par
// « Sélection » et on déplace ce h3 + tous les nœuds frères suivants JUSQU'AU
// prochain titre (h2/h3) dans la carte. Idempotent (skip si déjà enveloppé).
// Robuste : no-op si le h3 est absent (jour d'abstention rend quand même un h3).
function wrapDecisionSelection(root) {{
  if (!root) return;
  const h3s = root.querySelectorAll('h3');
  let target = null;
  for (const h of h3s) {{
    const txt = (h.textContent || '').trim().toLowerCase();
    if (txt.indexOf('sélection') === 0 || txt.indexOf('selection') === 0) {{ target = h; break; }}
  }}
  if (!target) return;
  if (target.parentElement && target.parentElement.classList.contains('decision-selection')) return;
  const card = document.createElement('div');
  card.className = 'decision-selection';
  target.parentNode.insertBefore(card, target);
  let node = target;
  while (node) {{
    const next = node.nextSibling;
    // On s'arrête au prochain titre de section (le tableau « À jouer » en h3, ou
    // un h2). Le h3 « Sélection » lui-même est inclus (premier tour de boucle).
    if (node !== target && node.nodeType === 1 && /^H[123]$/.test(node.tagName)) break;
    card.appendChild(node);
    node = next;
  }}
}}

// Tooltips natifs (attribut title) sur les symboles d'info de la matrice/synthèse.
// Reprend les définitions de la légende du bulletin. Zéro CSS, zéro espace.
const SYMBOL_TOOLTIPS = {{
  '🚫': 'Données insuffisantes : actif non scoré',
  '⏸': 'En pause : pas de décision actionnable',
  '📰': 'News > 50% du score quant : pondéré en tête',
  '⚑': 'Gate régime extrême actif',
  '⚪': 'Quasi coin-flip (|score| < 0.05) : non-actionnable',
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
  /fausses\\s+aux\\s+retournements/i, // [C-BD2] métrique technique du moteur (bilan jour)
  // [Refonte S9 — I7/I9] sections informatives non décisionnelles, repliées :
  /intensité\\s+comparable/i,    // I7 — note normalisée, informatif
  /^flips\\s+vs\\s+veille/i,      // I9 — retournements, consultés en 2e lecture
];

// Détecte la section H2 dont le titre matche `re` ; renvoie le <h2> ou null.
function findH2(root, re) {{
  return Array.from(root.querySelectorAll('h2')).find(h => re.test(h.textContent || '')) || null;
}}

// Renvoie le texte agrégé d'une section H2 (du h2 jusqu'au prochain h2).
function sectionText(h2) {{
  let txt = '';
  let node = h2.nextSibling;
  while (node && !(node.nodeType === 1 && node.tagName === 'H2')) {{
    txt += (node.textContent || '');
    node = node.nextSibling;
  }}
  return txt;
}}

function foldSections(root) {{
  if (!root) return;

  // [I12] « Comment lire les scores » : doublon EXACT de la help-box (qui contient
  // désormais tous les symboles). On la RETIRE du flux du bulletin (pas repliée :
  // supprimée), zéro perte d'info. Idempotent.
  const cl = findH2(root, /comment\\s+lire\\s+les\\s+scores/i);
  if (cl) {{
    let node = cl.nextSibling;
    while (node && !(node.nodeType === 1 && node.tagName === 'H2')) {{
      const next = node.nextSibling; node.remove(); node = next;
    }}
    cl.remove();
  }}

  // [Point #4] « Santé des sources » : TOUJOURS repliée par défaut (même en cas
  // d'anomalie — c'est du monitoring, pas une alerte de décision). Si une
  // anomalie est détectée, on l'INDIQUE dans le summary (« ⚠️ anomalie ») mais on
  // garde la section FERMÉE : le trader l'ouvre s'il veut le détail.
  const sante = findH2(root, /santé\\s+des\\s+sources/i);
  if (sante) {{
    const t = sectionText(sante);
    const anomalie = /[1-9]\\d*\\s+en\\s+échec/i.test(t) || /muet/i.test(t);
    const sm = foldOneSection(sante);
    if (sm) {{
      const d = sm.closest('details.fold-section');
      if (d) d.open = false;  // toujours fermé, anomalie ou pas
      sm.textContent = anomalie ? 'Santé des sources ⚠️ anomalie'
                                : 'Santé des sources ✓';
    }}
  }}

  // [I8] « News par actif » : repliée seulement si AUCUN actif n'a d'actualité
  // (matin calme = bruit total). Si ≥ 1 news → reste dépliée.
  const news = findH2(root, /news\\s+par\\s+actif/i);
  if (news) {{
    const t = sectionText(news);
    // Vide si chaque entrée dit « aucune actualité » et aucun contenu d'actu.
    const aucune = /aucune\\s+actualité/i.test(t) && !/\\b(LONG|SHORT|impact|haussier|baissier)\\b/i.test(t);
    if (aucune) {{
      const sm = foldOneSection(news);
      if (sm) sm.textContent = 'News par actif (aucune ce matin)';
    }}
  }}

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

// [Point #1] Libellé court MAIS COMPLET pour la sous-nav : table de
// correspondance par motif sur le titre du <h2>. Chaque titre `## ` connu du
// bulletin a une entrée — des libellés courts, jamais coupés en plein mot ni en
// plein milieu d'une phrase (l'ancien repli « 2 premiers mots » donnait
// « Sélection du » — corrigé). L'ORDRE compte : les motifs les plus spécifiques
// d'abord (« sélection du jour » avant un éventuel « décision du jour »).
const SUBNAV_LABELS = [
  [/décor\\s+du\\s+jour/i,              'Décor'],
  [/briefing\\s+du\\s+jour/i,           'Briefing'],
  [/santé\\s+des\\s+sources/i,          'Santé sources'],
  [/sélection\\s+du\\s+jour/i,          'Sélection du jour'],
  [/à\\s+jouer\\s+aujourd/i,            'À jouer'],
  [/décision\\s+du\\s+jour/i,           'Décision du jour'],
  [/top\\s+convictions\\s+multi/i,      'Top convictions'],
  [/top\\s+3\\s+convictions/i,          'Top convictions'],
  [/top\\s+convictions/i,               'Top convictions'],
  [/top\\s+swing/i,                     'Top swing'],
  [/synthèse\\s+des\\s+décisions/i,     'Synthèse'],
  [/matrice/i,                         'Matrice'],
  [/intensité/i,                       'Intensité'],
  [/cellules\\s+à\\s+surveiller/i,      'À surveiller'],
  [/drivers\\s+macro/i,                 'Drivers macro'],
  [/flips/i,                           'Flips'],
  [/comment\\s+lire/i,                  null],   // section supprimée du flux (→ help-box)
  [/détail\\s+par\\s+actif/i,           'Détail par actif'],
  [/limites\\s+du\\s+jour/i,            'Limites'],
  [/calls\\s+24h\\s+jug/i,              'Calls jugés'],
  [/audit\\s+de\\s+la\\s+veille/i,      'Calls jugés'],
  [/bilan\\s+des\\s+news/i,             'Bilan news'],
  [/news\\s+par\\s+actif/i,             'News par actif'],
];
function subnavLabelFor(raw) {{
  for (const [re, lab] of SUBNAV_LABELS) {{
    if (re.test(raw)) return lab; // null → exclu (filtré en amont par buildSubnav)
  }}
  // [Point #1] Repli SANS troncature : on retire seulement les émojis/symboles
  // de tête et le suffixe entre parenthèses (« (fenêtre récente) ») ou après un
  // tiret long. On garde le titre COMPLET — jamais coupé en plein mot/phrase.
  let cleaned = raw.replace(/^[^\\p{{L}}\\p{{N}}]+/u, '').trim();
  cleaned = cleaned.replace(/\\s*[–—-]\\s+.*$/u, '');  // retire « — max 3 », « — fenêtre… »
  cleaned = cleaned.replace(/\\s*\\([^)]*\\)\\s*$/u, '').trim();  // retire « (…) » final
  return cleaned || raw;
}}

// Pose un id stable et prévisible sur CHAQUE <h2> du bulletin. Appelé AVANT
// foldSections : ainsi un h2 replié transfère son id à son <summary> (l'ancre
// reste valide même une fois la section repliée).
function assignH2Ids(root) {{
  if (!root) return;
  root.querySelectorAll('h2').forEach((h, i) => {{
    const raw = (h.textContent || '').trim();
    h.id = `sec-${{i}}-${{slugify(raw).slice(0, 40)}}`;
  }});
}}

// Construit la sous-navigation d'ancres. [Refonte S9 — (B)1] N'affiche QUE les
// sections VISIBLES : on appelle buildSubnav APRÈS foldSections, qui remplace
// chaque h2 replié par un <details><summary> (l'h2 disparaît du DOM). Du coup
// `querySelectorAll('h2')` ne renvoie plus que les sections dépliées → la
// subnav ne pointe jamais vers une section masquée. Solution la plus simple et
// robuste : zéro test d'état de repli, on s'appuie sur le DOM déjà transformé.
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
  let lastLabel = null;
  let emitted = 0;
  h2s.forEach((h) => {{
    const raw = (h.textContent || '').trim();
    const id = h.id || `sec-${{slugify(raw).slice(0, 40)}}`;
    h.id = id; // garantit une ancre même si assignH2Ids n'a pas tourné.
    // Label court et LISIBLE. Table de correspondance (mots, jamais d'émoji nu) :
    // on reconnaît la section par un motif sur son titre, sinon repli générique.
    let label = subnavLabelFor(raw);
    if (label === null) return;            // section exclue de la nav (ex. Comment lire)
    if (label === lastLabel) return;       // dédoublonne (ex. ancienne fusion 24h)
    lastLabel = label;
    if (label.length > 22) label = label.slice(0, 22) + '…';
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
    if (emitted > 0) links.appendChild(document.createTextNode(' '));
    links.appendChild(a);
    emitted += 1;
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
    if (empty) {{ empty.hidden = false; empty.textContent = 'Historique en cours de constitution : les résultats par prédiction apparaîtront ici dès la première mesure d\\'échéance.'; }}
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
const AUX_NAV_IDS = ['nav-today', 'nav-week', 'nav-history'];
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
  ['today-view', 'week-view', 'history-view'].forEach(s => {{
    const el = document.getElementById(s);
    if (el) el.hidden = (s !== sectionId);
  }});
  const bc = document.getElementById('bulletin-content');
  const subnav = document.getElementById('subnav');
  const help = document.querySelector('.help-box');
  if (bc) bc.hidden = true;
  if (subnav) subnav.style.display = 'none';
  if (help) help.style.display = 'none';
  clearAuxNavActive();
  const nav = document.getElementById(navId);
  if (nav) nav.classList.add('active');
  // [CH-4] titre d'onglet par vue auxiliaire.
  const AUX_TITLES = {{
    'nav-today': 'Aujourd\\'hui',
    'nav-week': 'Bilan semaine', 'nav-history': 'Performance',
  }};
  document.title = `${{AUX_TITLES[navId] || 'Vue'}} · TradingApp v3`;
  renderList(null);
  const mainEl = document.getElementById('bulletin-main');
  if (mainEl) mainEl.scrollTop = 0;
}}

// Quitte toute vue auxiliaire et restaure la vue bulletin (légende, aide…).
function hideAuxViews() {{
  ['today-view', 'week-view', 'history-view'].forEach(s => {{
    const el = document.getElementById(s);
    if (el) el.hidden = true;
  }});
  const bc = document.getElementById('bulletin-content');
  const help = document.querySelector('.help-box');
  if (bc) bc.hidden = false;
  if (help) help.style.display = '';
  clearAuxNavActive();
}}

function showToday() {{
  buildTodayView();
  showAuxView('today-view', 'nav-today');
  history.replaceState(null, '', '#vue=aujourdhui');
}}
function showWeek(weekly) {{
  buildWeekView(weekly || WEEKLY);
  showAuxView('week-view', 'nav-week');
  history.replaceState(null, '', '#vue=semaine');
}}
function showHistory() {{
  if (!HISTORY_BUILT) {{
    // Vue « Performance » fusionnée : win rate par actif en tête (résultats
    // principaux + séquence des verdicts), puis le détail A/B replié, puis la
    // table décision par décision. (Fusion S9 : l'ancienne vue « Résultats /
    // Win rate » faisait doublon avec celle-ci — une seule vue désormais.)
    const hwr = document.getElementById('history-winrate');
    if (renderWinrateInto(hwr)) {{
      dimEmptyRows(hwr);
      enhanceWinrateRows(hwr);
      annotateFlipContinuation(hwr);
      buildVerdictSequences(hwr);
    }} else if (hwr) {{
      hwr.innerHTML = '<p class="history-intro">Aucun résultat de win rate disponible pour le moment : les chiffres apparaîtront ici dès les premières mesures.</p>';
    }}
    buildHistoryFilters();
    buildHistorySummary();
    HISTORY_BUILT = true;
  }}
  renderHistoryTable();
  showAuxView('history-view', 'nav-history');
  history.replaceState(null, '', '#vue=performance');
}}

// --- Rendu markdown mutualisé (suivis, bilans, semaine) -------------------
// Rend `md` dans `target` avec le même pipeline d'enrichissement que les
// bulletins (colorisation LONG/SHORT, tooltips symboles, wrap tables). Fallback
// <pre> si marked.js n'a pas chargé (offline). Réutilisé par toutes les vues.
// Normalisation typographique : le tiret cadratin « — » « fait très IA »
// (préférence fondateur). On le remplace AU RENDU par le point médian « · »
// (style maison déjà utilisé dans les titres), en absorbant les espaces autour.
// Couvre d'un coup les archives (markdown figé) ET les futurs rapports, sans
// toucher aux fichiers data/. On épargne les blocs de code (``` … ```) pour ne
// rien casser dans d'éventuels exemples techniques.
function normalizeDashes(md) {{
  if (!md) return md;
  const parts = md.split(/(```[\\s\\S]*?```)/g);
  for (let i = 0; i < parts.length; i++) {{
    if (i % 2 === 1) continue;  // bloc de code → inchangé
    parts[i] = parts[i].replace(/\\s*—\\s*/g, ' · ');
  }}
  return parts.join('');
}}

function renderMarkdownInto(target, md) {{
  if (!target) return;
  if (typeof marked !== 'undefined') {{
    marked.setOptions({{gfm: true, breaks: false}});
    target.innerHTML = marked.parse(normalizeDashes(md) || '');
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
    markSelectionTables(target);
    wrapTables(target);
    wrapDecisionSelection(target);
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
// « Aujourd'hui » (buildTodayView) et le clic sur un jour de l'historique
// (selectDay, via buildDayGroup) — un seul ordre canonique, pas de duplication.
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

// Briefings (BULLETINS) d'une date ISO, plus récent d'abord — un jour peut en
// avoir plusieurs (run du matin + run du soir). Helper partagé.
function sameDayBriefings(dateIso) {{
  return BULLETINS.filter(b => (b.id || '').slice(0, 10) === dateIso);
}}

// Construit le groupe repliable d'UN jour : un <details class="today-day"> dont
// le summary porte la date, contenant le briefing 7h + suivis 12h/18h + bilan du
// soir, chacun dans un <details class="today-report"> à rendu paresseux. C'est
// LE bloc partagé entre la vue « Aujourd'hui » (buildTodayView) et le clic sur
// un jour de l'historique (selectDay) — un seul système de regroupement.
// Dégradation propre : un jour sans bilan (ou sans briefing) n'affiche que ce
// qui existe (zéro section vide trompeuse). openDay/openLastReport pilotent les
// états ouverts par défaut.
function buildDayGroup(dateIso, opts) {{
  opts = opts || {{}};
  const dt = formatBulletinDate(dateIso);
  const briefings = sameDayBriefings(dateIso);
  const dayReports = sameDayReports(dateIso);

  const details = document.createElement('details');
  details.className = 'today-day';
  if (opts.openDay) details.open = true;
  const summary = document.createElement('summary');
  summary.innerHTML = '<span>' + dt.short + '</span>';
  details.appendChild(summary);

  // Ordre de lecture du jour : briefing 7h → suivi 12h → suivi 18h → bilan 22h.
  const ordered = [];
  briefings.forEach(b => ordered.push({{ tag: 'Briefing', slot: b.slot || '7h', md: b.markdown }}));
  dayReports.forEach(r => {{
    const isBilan = r.kind === 'bilan-jour';
    ordered.push({{ tag: isBilan ? 'Bilan' : 'Suivi', slot: isBilan ? '22h' : r.slot, md: r.markdown }});
  }});
  if (ordered.length === 0) return details;

  // Vue jour : le BRIEFING est visible PAR DÉFAUT ; un MENU (onglets) donne accès
  // aux autres rapports (Suivi 12h / Suivi 18h / Bilan 22h) DEPUIS le briefing.
  // Un seul rapport affiché à la fois — pas 4 rapports empilés.
  const tabs = document.createElement('div');
  tabs.className = 'day-tabs';
  const panel = document.createElement('div');
  panel.className = 'day-panel';
  const showItem = (item, btn) => {{
    tabs.querySelectorAll('.day-tab').forEach(x => x.classList.remove('active'));
    if (btn) btn.classList.add('active');
    panel.innerHTML = '';
    renderMarkdownInto(panel, item.md);
  }};
  ordered.forEach((item, ii) => {{
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'day-tab' + (ii === 0 ? ' active' : '');
    const lab = (item.tag === 'Briefing') ? ('Briefing ' + (item.slot || '7h'))
              : (item.tag === 'Bilan') ? ('Bilan ' + (item.slot || '22h'))
              : ('Suivi ' + (item.slot || ''));
    btn.textContent = lab;
    btn.onclick = () => showItem(item, btn);
    tabs.appendChild(btn);
  }});
  details.appendChild(tabs);
  details.appendChild(panel);
  showItem(ordered[0], tabs.querySelector('.day-tab'));  // Briefing visible par défaut
  return details;
}}

// Construit la vue « Aujourd'hui » : pour chaque jour (récent d'abord), un
// groupe repliable (buildDayGroup). Réutilise BULLETINS + REPORTS.
function buildTodayView() {{
  const wrap = document.getElementById('today-list');
  const empty = document.getElementById('today-empty');
  if (!wrap) return;
  wrap.innerHTML = '';

  const days = listDays().map(d => d.date);  // déjà trié récent d'abord
  if (days.length === 0) {{
    if (empty) {{ empty.hidden = false; empty.textContent = "Aucun rapport pour l'instant : les briefings et suivis apparaîtront ici."; }}
    return;
  }}
  if (empty) empty.hidden = true;

  days.forEach((d, di) => {{
    const grp = buildDayGroup(d, {{ openDay: di === 0, openLastReport: di === 0 }});
    wrap.appendChild(grp);
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
  const sem = iso ? ('Semaine ISO ' + iso[1] + ' · ') : '';
  return sem + 'du lundi ' + fmt(lundi) + ' au vendredi ' + fmt(vendredi);
}}

function buildWeekView(weekly) {{
  weekly = weekly || WEEKLY;
  const content = document.getElementById('week-content');
  const empty = document.getElementById('week-empty');
  const titleEl = document.getElementById('week-human-title');
  if (!content) return;
  if (!weekly) {{
    content.innerHTML = '';
    if (titleEl) titleEl.hidden = true;
    if (empty) {{ empty.hidden = false; empty.textContent = 'Aucun bilan de semaine pour le moment : le premier est généré le dimanche suivant (18h), puis chaque dimanche.'; }}
    return;
  }}
  if (empty) empty.hidden = true;
  const human = weekHumanTitle(weekly);
  if (titleEl) {{
    if (human) {{ titleEl.textContent = human; titleEl.hidden = false; }}
    else titleEl.hidden = true;
  }}
  // Anti-doublon : le H1 du markdown (« Bilan semaine · 2026-S## (range) ») et
  // ses 3 puces méta (Généré / WIN RATE ONLY / WR tradable) répètent le chrome de
  // la vue (titre + sous-titre humain + intro). On rend à partir de la 1re section
  // « ## 1. … » seulement. weekHumanTitle lit le markdown BRUT (range intact).
  const md = weekly.markdown || '';
  const idx = md.search(/^## /m);
  renderMarkdownInto(content, idx > 0 ? md.slice(idx) : md);
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


// Clic sur un JOUR de l'historique : on présente la journée COMME la vue
// « Aujourd'hui » — un groupe dépliable (buildDayGroup) avec briefing 7h +
// suivis 12h/18h + bilan du soir, au lieu de n'ouvrir que le bulletin 7h. Le
// briefing (premier rapport) est ouvert par défaut (lecture primaire), les
// autres repliés. Dégradation propre : un jour sans bilan n'affiche que ce qui
// existe. Réutilise EXACTEMENT le système de regroupement de today-view.
function selectDay(dateIso) {{
  hideAuxViews();
  const content = document.getElementById('bulletin-content');
  const mainEl = document.getElementById('bulletin-main');
  const subnav = document.getElementById('subnav');
  // La journée par jour n'a pas de sous-nav globale (chaque rapport est replié).
  if (subnav) subnav.style.display = 'none';
  content.innerHTML = '';

  const briefings = sameDayBriefings(dateIso);
  const dayReports = sameDayReports(dateIso);
  if (briefings.length === 0 && dayReports.length === 0) {{
    content.innerHTML = '<p>Aucun rapport pour ce jour.</p>';
    renderList(dateIso);
    return;
  }}

  const grp = buildDayGroup(dateIso, {{ openDay: true, openFirstReport: true }});
  content.appendChild(grp);

  history.replaceState(null, '', '#jour=' + encodeURIComponent(dateIso));
  renderList(dateIso);
  const dt = formatBulletinDate(dateIso);
  document.title = `${{dt.short}} · TradingApp v3`;
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

  // [Point #6] La barre de légende redondante (et son lien « ❓ Symboles ») a été
  // supprimée : la help-box « ❓ Comment lire » reste accessible par son propre
  // <summary> (cliquable, en tête de bulletin). Aucun handler à rebrancher.
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') closeSidebarMobile();
  }});

  // Liens de vues auxiliaires de la sidebar (Aujourd'hui / Bilan semaine / Historique).
  const bindNav = (id, fn) => {{
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', (e) => {{ e.preventDefault(); fn(); closeSidebarMobile(); }});
  }};
  bindNav('nav-today', showToday);
  bindNav('nav-week', showWeek);
  bindNav('nav-history', showHistory);

  const rawHash = (location.hash || '').replace(/^#/, '');
  // Routage des vues auxiliaires (avant la résolution d'un jour). #vue=performance
  // est le hash canonique de la vue fusionnée ; #vue=resultats et #vue=historique
  // y retombent (rétro-compat des liens partagés avant la fusion S9).
  if (rawHash === 'vue=aujourdhui') {{ showToday(); return; }}
  if (rawHash === 'vue=semaine') {{ showWeek(); return; }}
  if (rawHash === 'vue=performance' || rawHash === 'vue=historique' || rawHash === 'vue=resultats') {{ showHistory(); return; }}

  const days = listDays();
  if (days.length === 0) {{
    // Aucun jour : ni briefing ni suivi/bilan → message neutre.
    document.getElementById('bulletin-content').innerHTML = '<p>Aucun bulletin disponible.</p>';
    const subnav = document.getElementById('subnav');
    if (subnav) subnav.style.display = 'none';
    return;
  }}
  // Hash « jour=YYYY-MM-DD » → ce jour ; rétro-compat : un hash d'id de bulletin
  // (ex. ancien lien « 2026-06-16T05... ») retombe sur sa date (10 prem. car.).
  let target = null;
  const hash = decodeURIComponent(rawHash);
  const jm = hash.match(/^jour=(\\d{{4}}-\\d{{2}}-\\d{{2}})$/);
  if (jm) target = jm[1];
  else if (/^\\d{{4}}-\\d{{2}}-\\d{{2}}/.test(hash)) target = hash.slice(0, 10);
  const known = days.some(d => d.date === target);
  selectDay(known ? target : days[0].date);
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
    weeklies = build_weeklies_payload()
    weekly = weeklies[0] if weeklies else None
    performance_md = load_performance_md()
    html = render_html(
        payload, total, measures=measures, perf_ab=perf_ab,
        reports=reports, weekly=weekly, weeklies=weeklies, performance_md=performance_md,
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
