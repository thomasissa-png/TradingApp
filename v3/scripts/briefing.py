"""TradingApp v3 — Briefing du jour (synthèse lisible des news à impact).

Lit `v3/data/events-log.md` (format : date|L1|L2|trigger|cours|latence|R|source|
news_zone|category|pattern_id), filtre les events récents (≤ 48h vs date du run)
et à impact (category business + cours non vide), groupe par actif des 12
suivis, et produit un bloc markdown « ## Briefing du jour » inséré juste après
le titre du bulletin.

Déterministe, zéro LLM, zéro invention. Si pas d'event marquant → message
explicite. Best-effort : utilisé en post-traitement du bulletin via
`run_bulletin.py`, doit être tolérant aux malformations.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("briefing")

ROOT = Path(__file__).resolve().parents[1]
EVENTS_LOG = ROOT / "data" / "events-log.md"

# Catégories considérées « à impact » pour le briefing
IMPACT_CATEGORIES = {
    "geopolitical",
    "macro",
    "commodity",
    "central_bank_subtle",
    "regulatory",
    "earnings",
}

# Fenêtre de fraîcheur : 48h
FRESHNESS_HOURS = 48

# Table ticker → actif (les 12 actifs suivis). Match souple :
# - ticker entre parenthèses dans le champ `cours`
# - OU nom de l'actif présent dans `cours` (insensible casse/accents)
TICKER_TO_ACTIF: List[Tuple[str, str, List[str]]] = [
    # (libellé actif, ticker canonique, alias noms)
    ("S&P 500", "^GSPC", ["s&p 500", "sp500", "s&p500"]),
    ("Nasdaq", "^IXIC", ["nasdaq"]),
    ("CAC 40", "^FCHI", ["cac 40", "cac40"]),
    ("VIX", "^VIX", ["vix"]),
    ("Pétrole", "BZ=F", ["brent", "pétrole", "petrole", "oil"]),
    ("Pétrole", "CL=F", ["wti", "pétrole brut", "petrole brut", "crude"]),
    ("Or", "GC=F", ["or", "gold"]),
    ("Argent", "SI=F", ["argent", "silver"]),
    ("Cuivre", "HG=F", ["cuivre", "copper"]),
    ("Café", "KC=F", ["café", "cafe", "coffee"]),
    ("Cacao", "CC=F", ["cacao", "cocoa"]),
    ("Blé", "ZW=F", ["blé", "ble", "wheat"]),
    ("EUR/USD", "EUR=X", ["eur/usd", "eurusd", "eur usd"]),
]

# Ligne du tableau events-log (markdown)
ROW_RE = re.compile(
    r"^\|\s*(?P<date>[^|]*?)\s*\|\s*(?P<l1>[^|]*?)\s*\|\s*(?P<l2>[^|]*?)\s*\|"
    r"\s*(?P<trigger>[^|]*?)\s*\|\s*(?P<cours>[^|]*?)\s*\|\s*(?P<latence>[^|]*?)\s*\|"
    r"\s*(?P<r>[^|]*?)\s*\|\s*(?P<source>[^|]*?)\s*\|\s*(?P<zone>[^|]*?)\s*\|"
    r"\s*(?P<cat>[^|]*?)\s*\|\s*(?P<pat>[^|]*?)\s*\|\s*$"
)

# Ligne d'en-tête / séparateur à ignorer
HEADER_TOKENS = {"date", "---"}


def _parse_date(s: str) -> Optional[date]:
    s = s.strip()
    if not s:
        return None
    # Accepte 'YYYY-MM-DD' ou 'YYYY-MM-DDTHH:MM:SS...'
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_events(events_path: Path) -> List[Dict[str, str]]:
    """Parse events-log.md. Retourne la liste des events bruts (dicts)."""
    if not events_path.exists():
        logger.warning("events-log introuvable : %s", events_path)
        return []
    events: List[Dict[str, str]] = []
    for raw_line in events_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        d = m.groupdict()
        # skip header/separator rows
        first = d["date"].strip().lower()
        if first in HEADER_TOKENS or first.startswith(":---") or first.startswith("---"):
            continue
        events.append({k: (v or "").strip() for k, v in d.items()})
    return events


def match_actif(cours: str) -> Optional[str]:
    """Mappe un champ `cours` vers un actif des 12 suivis.

    Stratégie :
    1. Cherche un ticker connu entre parenthèses (ex: 'Brent (BZ=F)' → 'Pétrole')
    2. Sinon, cherche un alias de nom (insensible casse)
    Retourne le libellé actif (ex: 'Pétrole') ou None si hors univers.
    """
    if not cours:
        return None
    low = cours.lower()
    # 1) tickers entre parenthèses
    for actif, ticker, _ in TICKER_TO_ACTIF:
        # match exact du ticker (avec délimiteurs courants)
        if re.search(r"[\(\s,]" + re.escape(ticker.lower()) + r"[\)\s,]?", " " + low + " "):
            return actif
    # 2) alias de nom (mot-clé)
    for actif, _, aliases in TICKER_TO_ACTIF:
        for alias in aliases:
            if alias in low:
                return actif
    return None


def filter_recent_impactful(
    events: List[Dict[str, str]],
    today: date,
    window_hours: int = FRESHNESS_HOURS,
) -> List[Dict[str, str]]:
    """Garde les events récents (≤ window_hours) et à impact (catégorie + cours)."""
    cutoff = today - timedelta(hours=window_hours)
    kept: List[Dict[str, str]] = []
    for ev in events:
        d = _parse_date(ev.get("date", ""))
        if d is None:
            continue
        if d < cutoff or d > today:
            continue
        cat = ev.get("cat", "").lower()
        if cat not in IMPACT_CATEGORIES:
            continue
        if not ev.get("cours", "").strip():
            continue
        kept.append(ev)
    return kept


def group_by_actif(events: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Groupe les events par actif (libellé). Hors-univers → clé 'Autres'."""
    groups: Dict[str, List[Dict[str, str]]] = {}
    for ev in events:
        actif = match_actif(ev.get("cours", "")) or "Autres"
        groups.setdefault(actif, []).append(ev)
    return groups


def _puce(ev: Dict[str, str]) -> str:
    zone = ev.get("zone", "").strip() or "—"
    trigger = ev.get("trigger", "").strip()
    source = ev.get("source", "").strip() or "—"
    # Tronque trigger si trop long pour rester lisible
    if len(trigger) > 220:
        trigger = trigger[:217].rstrip() + "..."
    return f"- [{zone}] {trigger} ({source})"


def build_briefing(
    events_path: Path = EVENTS_LOG,
    today: Optional[date] = None,
    max_par_actif: int = 3,
) -> str:
    """Construit le bloc markdown '## Briefing du jour'.

    Args:
        events_path: chemin vers events-log.md
        today: date du run (default = today)
        max_par_actif: nombre max de puces par actif (1 à 3)

    Returns:
        Markdown du bloc briefing (sans trailing newline).
    """
    today = today or date.today()
    all_events = parse_events(events_path)
    impactful = filter_recent_impactful(all_events, today)
    groups = group_by_actif(impactful)

    lines: List[str] = []
    lines.append("## Briefing du jour")
    lines.append("")
    lines.append(
        f"_{len(all_events)} events analysés, {len(impactful)} à impact "
        f"(fenêtre {FRESHNESS_HOURS}h jusqu'au {today:%Y-%m-%d})._"
    )
    lines.append("")

    if not impactful:
        lines.append("- Aucun event marquant sur la fenêtre.")
        lines.append("")
        return "\n".join(lines)

    # Ordre : les 12 actifs dans l'ordre canonique, puis 'Autres' à la fin
    ordre_actifs = []
    seen = set()
    for actif, _, _ in TICKER_TO_ACTIF:
        if actif not in seen:
            ordre_actifs.append(actif)
            seen.add(actif)
    ordre_actifs.append("Autres")

    for actif in ordre_actifs:
        evs = groups.get(actif)
        if not evs:
            continue
        lines.append(f"### {actif}")
        for ev in evs[:max_par_actif]:
            lines.append(_puce(ev))
        if len(evs) > max_par_actif:
            lines.append(f"- _(+{len(evs) - max_par_actif} autres events sur cet actif)_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Insertion dans le bulletin
# ---------------------------------------------------------------------------

# Titre de bulletin : '# Bulletin Analyste — YYYY-MM-DD'
TITRE_RE = re.compile(r"^(#\s+Bulletin[^\n]*\n)", re.MULTILINE)


def prepend_to_bulletin(bulletin_path: Path, briefing_md: str) -> bool:
    """Insère `briefing_md` juste après le titre H1 du bulletin.

    Si le bulletin contient déjà un bloc '## Briefing du jour' (re-run), on le
    remplace. Si le titre est introuvable, on préfixe le briefing en tête du
    fichier (best-effort).

    Retourne True si écrit, False si rien à faire (fichier absent).
    """
    if not bulletin_path.exists():
        logger.warning("bulletin introuvable : %s", bulletin_path)
        return False
    content = bulletin_path.read_text(encoding="utf-8")

    # Si un briefing existe déjà, le retirer pour le remplacer
    existing_re = re.compile(
        r"## Briefing du jour\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    if existing_re.search(content):
        content = existing_re.sub("", content, count=1)
        # nettoyage des doubles sauts résiduels après suppression
        content = re.sub(r"\n{3,}", "\n\n", content)

    block = briefing_md.rstrip() + "\n\n"

    m = TITRE_RE.search(content)
    if m:
        insert_at = m.end()
        new_content = content[:insert_at] + "\n" + block + content[insert_at:]
    else:
        new_content = block + content

    bulletin_path.write_text(new_content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# CLI (debug)
# ---------------------------------------------------------------------------

def main() -> int:
    import sys
    logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")
    md = build_briefing()
    sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
