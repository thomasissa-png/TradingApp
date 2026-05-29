"""TradingApp v3 — Classifieur d'events vers triplets binaires.

Lit `v3/data/events-log.md` (tableau markdown : date|L1|L2|trigger|cours|...|source|news_zone)
et `v3/config/triggers-and-windows.yml`. Pour chaque critère `type: triplet`,
applique les listes de mots-clés (case-insensitive + word-boundary) sur la
fenêtre `horizon_lookback_jours`. Pour `type: calendrier`, résout selon la
date du jour.

Règles (cf. triggers-and-windows.yml) :
- Listes fermées : aucun match → 0 (neutre, pas n/a)
- Mots-clés FR + EN
- Case-insensitive, word-boundary
- Si LONG et SHORT matchent dans la même fenêtre → garder le plus récent

Zéro invention : events-log absent/vide → tous triplets = 0.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger("triggers_classifier")

ROOT = Path(__file__).resolve().parents[1]
EVENTS_LOG = ROOT / "data" / "events-log.md"
TRIGGERS_YML = ROOT / "config" / "triggers-and-windows.yml"


# ---------------------------------------------------------------------------
# Parsing events-log.md
# ---------------------------------------------------------------------------

# Lignes markdown table — on ignore le header et le separator (--- | ---).
_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
_SEPARATOR_RE = re.compile(r"^\s*\|?[\s\-:|]+\|?\s*$")


def _parse_date(s: str) -> Optional[datetime]:
    s = s.strip()
    if not s:
        return None
    # Try ISO with time, ISO date only, common french formats
    for fmt in (None,):  # fromisoformat first
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_events_log(path: Path = EVENTS_LOG) -> List[dict]:
    """Parse le tableau markdown. Colonnes minimales attendues :
    date | L1 | L2 | trigger | cours | source | news_zone (ordre flexible via header).

    Lignes invalides (date illisible, pas un row) → ignorées avec WARNING.
    Retourne une liste de dicts triée par date desc."""
    if not path.exists():
        logger.warning("events-log absent (%s) — 0 events", path)
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("Impossible de lire events-log : %s", e)
        return []

    rows: List[List[str]] = []
    for line in text.splitlines():
        m = _TABLE_ROW_RE.match(line)
        if not m:
            continue
        if _SEPARATOR_RE.match(line):
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        rows.append(cells)

    if not rows:
        return []

    # Premier row = header (sauf si la 1ere cellule ressemble à une date)
    header = rows[0]
    first_is_date = _parse_date(header[0]) is not None
    if first_is_date:
        # Pas de header — colonnes par défaut
        headers_l = ["date", "l1", "l2", "trigger", "cours", "source", "news_zone"]
        data_rows = rows
    else:
        headers_l = [h.lower().strip() for h in header]
        data_rows = rows[1:]

    events: List[dict] = []
    for r in data_rows:
        if len(r) < 2:
            continue
        ev: Dict[str, Any] = {}
        for i, val in enumerate(r):
            if i < len(headers_l):
                ev[headers_l[i]] = val
        dt = _parse_date(ev.get("date", ""))
        if dt is None:
            logger.warning("events-log : ligne ignorée (date illisible) : %r", r)
            continue
        ev["_dt"] = dt
        events.append(ev)
    events.sort(key=lambda e: e["_dt"], reverse=True)
    return events


# ---------------------------------------------------------------------------
# Matching mots-clés
# ---------------------------------------------------------------------------

def _compile_kw_pattern(keywords: List[str]) -> Optional[re.Pattern]:
    if not keywords:
        return None
    parts = []
    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        # Word boundary à gauche/droite, mais on doit autoriser ponctuation et
        # caractères non-ASCII (accents). On utilise des lookaround "non-word" custom.
        escaped = re.escape(kw_clean)
        # \b ne fonctionne pas bien avec accents → on encadre par non-lettre.
        parts.append(rf"(?<![A-Za-zÀ-ÖØ-öø-ÿ0-9_]){escaped}(?![A-Za-zÀ-ÖØ-öø-ÿ0-9_])")
    if not parts:
        return None
    return re.compile("|".join(parts), re.IGNORECASE)


def _event_text(ev: dict) -> str:
    parts = []
    for k in ("trigger", "l2", "l1", "source", "news_zone"):
        v = ev.get(k)
        if v:
            parts.append(str(v))
    return " | ".join(parts)


def _resolve_triplet(
    events: List[dict],
    long_keywords: List[str],
    short_keywords: List[str],
    lookback_days: int,
    now: datetime,
) -> int:
    """Cherche dans les events dans la fenêtre [now - lookback, now]. Retourne -1/0/+1.
    Si long ET short matchent → on garde le plus récent."""
    long_re = _compile_kw_pattern(long_keywords)
    short_re = _compile_kw_pattern(short_keywords)
    if long_re is None and short_re is None:
        return 0
    cutoff = now - timedelta(days=lookback_days)
    last_long: Optional[datetime] = None
    last_short: Optional[datetime] = None
    for ev in events:
        dt = ev.get("_dt")
        if not isinstance(dt, datetime):
            continue
        if dt < cutoff or dt > now:
            continue
        text = _event_text(ev)
        if long_re and long_re.search(text):
            if last_long is None or dt > last_long:
                last_long = dt
        if short_re and short_re.search(text):
            if last_short is None or dt > last_short:
                last_short = dt
    if last_long is None and last_short is None:
        return 0
    if last_long is not None and last_short is None:
        return 1
    if last_short is not None and last_long is None:
        return -1
    # Les deux : plus récent gagne
    if last_long >= last_short:  # type: ignore[operator]
        return 1
    return -1


# ---------------------------------------------------------------------------
# Calendrier (cycle annuel / saisonnier)
# ---------------------------------------------------------------------------

def _resolve_calendrier(cle: str, today: date) -> Optional[int]:
    """Résout les critères calendrier connus. Retourne -1/0/+1 ou None si non géré.

    Mapping documenté dans triggers-and-windows.yml (sections texte).
    """
    m = today.month
    y = today.year
    if cle == "demande_indienne_saisonniere":
        # long: oct-nov (Diwali) + oct-déc (mariages) → oct, nov, déc
        # short: jan-mai (off-season)
        # neutre: juin-sep
        if m in (10, 11, 12):
            return 1
        if m in (1, 2, 3, 4, 5):
            return -1
        return 0
    if cle == "cycle_bresil_biannuel":
        # long: années impaires (off) ; short: années paires (on)
        return 1 if (y % 2 == 1) else -1
    return None


# ---------------------------------------------------------------------------
# Chargement triggers-and-windows.yml
# ---------------------------------------------------------------------------

def load_triggers_config(path: Path = TRIGGERS_YML) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"triggers-and-windows.yml absent : {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError("triggers-and-windows.yml : racine YAML doit être un mapping")
    return data


# ---------------------------------------------------------------------------
# API principale
# ---------------------------------------------------------------------------

def classify_all(
    events: Optional[List[dict]] = None,
    today: Optional[datetime] = None,
    triggers_cfg: Optional[dict] = None,
) -> Dict[str, Dict[str, int]]:
    """Pour chaque actif × critère triplet/calendrier, retourne la valeur ∈ {-1,0,+1}.

    Sortie : {actif_key: {cle_courante: valeur_triplet}}
    Les critères `numerique` (fenêtres d'activation) ne sont PAS traités ici
    (le calculator s'en occupe).
    """
    if triggers_cfg is None:
        triggers_cfg = load_triggers_config()
    if events is None:
        events = parse_events_log()
    if today is None:
        today = datetime.now(timezone.utc)
    elif today.tzinfo is None:
        today = today.replace(tzinfo=timezone.utc)
    today_date = today.date()

    out: Dict[str, Dict[str, int]] = {}
    for actif_key, criteres in triggers_cfg.items():
        if not isinstance(criteres, dict):
            continue
        actif_out: Dict[str, int] = {}
        for cle, spec in criteres.items():
            if not isinstance(spec, dict):
                continue
            t = spec.get("type")
            if t == "triplet" or t == "triplet_composite":
                lookback = int(spec.get("horizon_lookback_jours", 7))
                val = _resolve_triplet(
                    events,
                    spec.get("long_keywords", []) or [],
                    spec.get("short_keywords", []) or [],
                    lookback,
                    today,
                )
                actif_out[cle] = val
            elif t == "calendrier":
                val = _resolve_calendrier(cle, today_date)
                if val is not None:
                    actif_out[cle] = val
                else:
                    logger.warning("Calendrier non géré : %s/%s", actif_key, cle)
            # numerique → ignoré (calculator)
        if actif_out:
            out[actif_key] = actif_out
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    res = classify_all()
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
