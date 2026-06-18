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
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("briefing")

ROOT = Path(__file__).resolve().parents[1]
EVENTS_LOG = ROOT / "data" / "events-log.md"
SOURCE_HEALTH = ROOT / "data" / "source-health.md"

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

# Ligne du tableau events-log (markdown) — schéma legacy 11 cols
ROW_RE = re.compile(
    r"^\|\s*(?P<date>[^|]*?)\s*\|\s*(?P<l1>[^|]*?)\s*\|\s*(?P<l2>[^|]*?)\s*\|"
    r"\s*(?P<trigger>[^|]*?)\s*\|\s*(?P<cours>[^|]*?)\s*\|\s*(?P<latence>[^|]*?)\s*\|"
    r"\s*(?P<r>[^|]*?)\s*\|\s*(?P<source>[^|]*?)\s*\|\s*(?P<zone>[^|]*?)\s*\|"
    r"\s*(?P<cat>[^|]*?)\s*\|\s*(?P<pat>[^|]*?)\s*\|\s*$"
)

# Ligne v2 directionnelle — 14 cols (legacy + impacts|materiality|reliability)
ROW_RE_V2 = re.compile(
    r"^\|\s*(?P<date>[^|]*?)\s*\|\s*(?P<l1>[^|]*?)\s*\|\s*(?P<l2>[^|]*?)\s*\|"
    r"\s*(?P<trigger>[^|]*?)\s*\|\s*(?P<cours>[^|]*?)\s*\|\s*(?P<latence>[^|]*?)\s*\|"
    r"\s*(?P<r>[^|]*?)\s*\|\s*(?P<source>[^|]*?)\s*\|\s*(?P<zone>[^|]*?)\s*\|"
    r"\s*(?P<cat>[^|]*?)\s*\|\s*(?P<pat>[^|]*?)\s*\|\s*(?P<impacts>[^|]*?)\s*\|"
    r"\s*(?P<materiality>[^|]*?)\s*\|\s*(?P<reliability>[^|]*?)\s*\|\s*$"
)

# Poids matérialité pour tri (high > medium > low > "")
_MAT_RANK = {"high": 3, "medium": 2, "low": 1, "": 0}

# Mapping ASSET (id IA) → libellé actif briefing
_IA_ASSET_TO_LABEL = {
    "CAC40": "CAC 40",
    "SP500": "S&P 500",
    "NASDAQ": "Nasdaq",
    "EURUSD": "EUR/USD",
    "BRENT": "Pétrole",
    "VIX": "VIX",
    "GOLD": "Or",
    "SILVER": "Argent",
    "COPPER": "Cuivre",
    "COFFEE": "Café",
    "COCOA": "Cacao",
    "WHEAT": "Blé",
}

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
    """Parse events-log.md. Retourne la liste des events bruts (dicts).

    Rétro-compat : essaie d'abord le format v2 (14 cols : + impacts|materiality|
    reliability). Si non-matching → fallback legacy 11 cols (impacts/materiality/
    reliability resteront vides).
    """
    if not events_path.exists():
        logger.warning("events-log introuvable : %s", events_path)
        return []
    # Parsing par split sur '|' (O(n), zéro backtracking regex). Les '|' internes
    # aux champs sont déjà échappés en '/' par le collector, donc le split est sûr.
    v2_cols = ["date", "l1", "l2", "trigger", "cours", "latence", "r",
               "source", "zone", "cat", "pat", "impacts", "materiality", "reliability"]
    legacy_cols = v2_cols[:11]
    events: List[Dict[str, str]] = []
    for raw_line in events_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) == 14:
            d = dict(zip(v2_cols, parts))
        elif len(parts) == 11:
            d = dict(zip(legacy_cols, parts))
        else:
            continue
        # skip header/separator rows
        first = d["date"].strip().lower()
        if first in HEADER_TOKENS or first.startswith(":---") or first.startswith("---"):
            continue
        ev = {k: (v or "").strip() for k, v in d.items()}
        # Garantir présence des champs v2 même sur format legacy
        ev.setdefault("impacts", "")
        ev.setdefault("materiality", "")
        ev.setdefault("reliability", "")
        events.append(ev)
    return events


def _parse_impacts_compact(encoded: str) -> List[Dict[str, Any]]:
    """Décode 'ASSET:DIR:CONF;...' → liste de dicts. Vide si encoded vide."""
    if not encoded:
        return []
    out: List[Dict[str, Any]] = []
    for chunk in encoded.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) < 2:
            continue
        asset = parts[0].strip().upper()
        direction = parts[1].strip().upper()
        if direction not in ("LONG", "SHORT", "NEUTRAL"):
            continue
        if asset not in _IA_ASSET_TO_LABEL:
            continue
        try:
            confidence = int(parts[2].strip()) if len(parts) >= 3 and parts[2].strip() else 0
        except ValueError:
            confidence = 0
        out.append({"asset": asset, "direction": direction, "confidence": confidence})
    return out


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
    """Garde les events récents (≤ window_hours) et à impact.

    Critère d'impact :
    - catégorie business (geopolitical/macro/commodity/...)
    - ET (cours non vide OU impacts IA non vide). Un event avec impacts IA mais
      sans cours legacy est tradable et doit passer le filtre.
    """
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
        has_cours = bool(ev.get("cours", "").strip())
        has_impacts = bool(ev.get("impacts", "").strip())
        if not (has_cours or has_impacts):
            continue
        kept.append(ev)
    return kept


def _primary_actif_from_event(ev: Dict[str, str]) -> Optional[str]:
    """Détermine le libellé actif principal d'un event.
    Priorité : 1) impacts IA (premier asset), 2) mapping legacy via `cours`.
    """
    impacts = _parse_impacts_compact(ev.get("impacts", ""))
    if impacts:
        label = _IA_ASSET_TO_LABEL.get(impacts[0]["asset"])
        if label:
            return label
    return match_actif(ev.get("cours", ""))


def group_by_actif(events: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Groupe les events par actif (libellé). Hors-univers → clé 'Autres'."""
    groups: Dict[str, List[Dict[str, str]]] = {}
    for ev in events:
        actif = _primary_actif_from_event(ev) or "Autres"
        groups.setdefault(actif, []).append(ev)
    return groups


def _sort_by_materiality_then_date(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Tri : materiality desc (high>medium>low>""), puis date desc."""
    def key(ev: Dict[str, str]):
        mat = (ev.get("materiality", "") or "").lower()
        rank = _MAT_RANK.get(mat, 0)
        d = _parse_date(ev.get("date", "")) or date.min
        return (-rank, -d.toordinal())
    return sorted(events, key=key)


def _news_dedup_key(ev: Dict[str, str]) -> str:
    """Clé de déduplication d'une news : titre normalisé + source.

    Normalise le `trigger` (titre) en minuscule avec espaces réduits, combiné à
    la `source` normalisée. Deux events partageant la même news (même titre,
    même source) collent sur la même clé. Robuste aux différences de casse et
    d'espacement multiple.
    """
    trigger = re.sub(r"\s+", " ", (ev.get("trigger", "") or "").strip().lower())
    source = (ev.get("source", "") or "").strip().lower()
    return trigger + " || " + source


def _dedup_news_in_actif(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Supprime les news identiques au sein d'un même actif.

    Le `seen` set de build_briefing dédoublonne les ACTIFS, pas les news AU SEIN
    d'un actif : une même news (même titre + source) peut apparaître deux fois.
    On garde la 1re occurrence et l'ordre d'entrée (l'appelant a déjà trié).
    """
    seen: set = set()
    out: List[Dict[str, str]] = []
    for ev in events:
        key = _news_dedup_key(ev)
        if key in seen:
            continue
        seen.add(key)
        out.append(ev)
    return out


def _direction_arrow_for(ev: Dict[str, str], actif_label: str) -> str:
    """Retourne ↑ / ↓ / → / '' selon la direction IA sur cet actif.

    Si pas d'impacts IA exploitables, retourne '' (pas de flèche).
    """
    impacts = _parse_impacts_compact(ev.get("impacts", ""))
    if not impacts:
        return ""
    # Cherche un impact correspondant au libellé actif
    for imp in impacts:
        if _IA_ASSET_TO_LABEL.get(imp["asset"]) == actif_label:
            d = imp["direction"]
            if d == "LONG":
                return "↑"
            if d == "SHORT":
                return "↓"
            if d == "NEUTRAL":
                return "→"
    # Sinon, prend la direction du premier impact (cas Autres)
    d = impacts[0]["direction"]
    if d == "LONG":
        return "↑"
    if d == "SHORT":
        return "↓"
    if d == "NEUTRAL":
        return "→"
    return ""


def _puce(ev: Dict[str, str], actif_label: str = "") -> str:
    zone = ev.get("zone", "").strip() or "—"
    trigger = ev.get("trigger", "").strip()
    source = ev.get("source", "").strip() or "—"
    mat = (ev.get("materiality", "") or "").strip().lower()
    arrow = _direction_arrow_for(ev, actif_label) if actif_label else ""
    # Tronque trigger si trop long pour rester lisible
    if len(trigger) > 220:
        trigger = trigger[:217].rstrip() + "..."
    mat_tag = f" [{mat}]" if mat in ("high", "medium") else ""
    arrow_str = f" {arrow}" if arrow else ""
    return f"- [{zone}]{mat_tag}{arrow_str} {trigger} ({source})"


# ---------------------------------------------------------------------------
# Intro « décor du jour » + Top news à impact (bloc A — 7h)
# ---------------------------------------------------------------------------
# DÉTERMINISTE, zéro LLM, zéro invention. Construit en TÊTE du Briefing 7h à
# partir des SEULES données déjà disponibles :
#   - catalyseurs J0 d'impact `high` du calendrier éco statique
#     (_catalyseurs_j0_high, ré-utilisé depuis scoring_analyste — aucune source
#      neuve) ;
#   - thèmes news DOMINANTS du corpus matin = actifs portant le plus d'events
#     à impact (materiality high>medium), dans l'ordre canonique des 12 actifs ;
#   - top 1-3 news = vrais titres de l'events-log triés par materiality puis
#     fraîcheur, avec actif + sens d'impact déjà qualifié par DeepSeek.
# Si pas de catalyseur / pas de news → on le DIT (« aucun », « pas d'actualité »).
# Style FACTUEL (décision Thomas 16/06) : pas d'avis, pas de prévision, aucune
# valeur monétaire. L'intro est du CONTEXTE, jamais une nouvelle prédiction.

# Nombre max de news dans le bloc « Top actualités à impact » (7h reste court).
MAX_TOP_NEWS = 3
# Nombre max de thèmes dominants cités dans la phrase d'intro.
MAX_THEMES_INTRO = 2


def _catalyseurs_j0_noms(now: datetime) -> List[str]:
    """Noms des catalyseurs J0 d'impact `high` du jour (liste, possiblement vide).

    Réutilise `scoring_analyste._catalyseurs_j0_high` (calendrier éco statique,
    même source, zéro invention). Import TOLÉRANT : module absent / KO → [].
    """
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from scoring_analyste import _catalyseurs_j0_high  # import paresseux/tolérant
    except Exception:  # noqa: BLE001 — calendrier indispo → pas de catalyseur cité
        return []
    try:
        cats = _catalyseurs_j0_high(now)
    except Exception:  # noqa: BLE001
        return []
    # Dédup en préservant l'ordre (un même event peut concerner plusieurs actifs).
    noms: List[str] = []
    for ev in cats:
        nom = str(ev.get("nom") or "").strip()
        if nom and nom not in noms:
            noms.append(nom)
    return noms


def _themes_dominants(groups: Dict[str, List[Dict[str, str]]]) -> List[str]:
    """Actifs dominants du corpus matin (le ou les 2 avec le plus d'events à impact).

    Le « thème » est l'actif le plus chargé en events à impact ce matin (proxy
    déterministe, zéro invention : on ne réécrit pas un récit). On pondère par la
    matérialité (high=3, medium=2, low=1) pour qu'un actif avec 1 event `high`
    prime sur un actif avec 3 events `low`. Exclut « Autres » (hors univers).
    Ordre de départage stable : score desc, puis ordre canonique des 12 actifs.
    """
    ordre = [a for a, _, _ in TICKER_TO_ACTIF]
    rang_canon = {a: i for i, a in enumerate(ordre)}
    scores: Dict[str, int] = {}
    for actif, evs in groups.items():
        if actif == "Autres":
            continue
        s = sum(_MAT_RANK.get((ev.get("materiality", "") or "").lower(), 0) + 1 for ev in evs)
        if s > 0:
            scores[actif] = s
    classes = sorted(scores.items(), key=lambda kv: (-kv[1], rang_canon.get(kv[0], 99)))
    return [a for a, _ in classes[:MAX_THEMES_INTRO]]


def _top_news_lignes(
    impactful: List[Dict[str, str]], max_news: int = MAX_TOP_NEWS
) -> List[str]:
    """Lignes « Top actualités à impact » : vrais titres triés materiality+fraîcheur.

    Ne garde QUE les events réellement à impact (high>medium ; les low/"" sont
    écartés du TOP — ils restent dans le détail par actif). Dédup par titre+source.
    Chaque ligne nomme l'actif + le sens d'impact déjà qualifié (↑/↓/→). Zéro
    invention : aucun event high/medium → liste vide (message géré par l'appelant).
    """
    forts = [
        ev for ev in impactful
        if (ev.get("materiality", "") or "").lower() in ("high", "medium")
    ]
    forts = _dedup_news_in_actif(_sort_by_materiality_then_date(forts))
    lignes: List[str] = []
    for ev in forts[:max_news]:
        actif = _primary_actif_from_event(ev) or "Marché"
        mat = (ev.get("materiality", "") or "").strip().lower()
        arrow = _direction_arrow_for(ev, actif) if actif != "Marché" else ""
        sens = {"↑": "haussier", "↓": "baissier", "→": "neutre"}.get(arrow, "")
        trigger = (ev.get("trigger", "") or "").strip()
        if len(trigger) > 180:
            trigger = trigger[:177].rstrip() + "..."
        sens_str = f" → {sens}" if sens else ""
        lignes.append(f"- **{actif}**{sens_str} ({mat}) : {trigger}")
    return lignes


def build_intro_block(
    impactful: List[Dict[str, str]],
    groups: Dict[str, List[Dict[str, str]]],
    today: date,
    now: Optional[datetime] = None,
    n_total: Optional[int] = None,
) -> List[str]:
    """Bloc « Décor du jour » : intro factuelle 1-2 phrases + top 1-3 news.

    DÉTERMINISTE (zéro LLM). Sources : catalyseurs J0 (calendrier statique) +
    thèmes dominants + top news (events réels). Retourne des lignes markdown.

    HONNÊTETÉ (P6) : à 7h le résultat d'un catalyseur (ex. FOMC) n'existe pas →
    l'intro l'ANNONCE comme « attendu aujourd'hui » (catalyseur), JAMAIS un
    résultat. `n_total` (optionnel) = nb d'events analysés, affiché en pied.
    """
    from datetime import datetime as _dt
    now = now or _dt.combine(today, _dt.min.time())

    cats = _catalyseurs_j0_noms(now)
    themes = _themes_dominants(groups)

    if cats:
        cat_str = ", ".join(cats)
        # P6 — HONNÊTETÉ : « attendu(s) aujourd'hui » = annonce d'un catalyseur,
        # jamais un résultat (à 7h le résultat FOMC n'existe pas encore).
        phrase_cat = f"Catalyseur(s) attendu(s) aujourd'hui : {cat_str}."
    else:
        phrase_cat = "Pas de catalyseur majeur attendu au calendrier."
    if themes:
        phrase_themes = f"Thèmes news dominants ce matin : {', '.join(themes)}."
    else:
        phrase_themes = "Aucun thème news dominant ce matin."

    lines: List[str] = []
    lines.append("## Décor du jour")
    lines.append("")
    lines.append(f"_Journée du {today:%Y-%m-%d}. {phrase_cat} {phrase_themes}_")
    lines.append("")
    lines.append("**Top actualités à impact**")
    top = _top_news_lignes(impactful)
    if top:
        lines.extend(top)
    else:
        lines.append("- Pas d'actualité à fort impact ce matin.")
    if n_total is not None:
        lines.append("")
        lines.append(
            f"_{n_total} events analysés, {len(impactful)} à impact "
            f"(fenêtre {FRESHNESS_HOURS}h jusqu'au {today:%Y-%m-%d})._"
        )
    lines.append("")
    return lines


def build_briefing(
    events_path: Path = EVENTS_LOG,
    today: Optional[date] = None,
    max_par_actif: int = 3,
    source_health_path: Path = SOURCE_HEALTH,
    now: Optional[datetime] = None,
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
    # P6 — « Décor du jour » : INTRO factuelle (catalyseur FOMC + thèmes + top
    # news), EN TÊTE du bulletin. Le bloc « ## Briefing du jour » per-actif (qui
    # affichait « 0 à impact / Aucun event marquant », redondant avec le détail
    # news) est SUPPRIMÉ : le détail par actif est désormais rendu UNE SEULE FOIS
    # en fin de bulletin via « ## News par actif » (build_news_par_actif).
    # Déterministe, best-effort — l'intro ne casse jamais le briefing.
    try:
        lines.extend(build_intro_block(
            impactful, groups, today, now, n_total=len(all_events)
        ))
    except Exception as e:  # noqa: BLE001 — l'intro ne doit jamais casser le briefing
        logger.warning("Intro « décor du jour » non rendue : %s", e)

    # --- Santé des sources (visible dans le briefing de base) ---
    # Best-effort : si source_monitor indispo ou source-health.md absent, on
    # affiche un bloc minimal. Ne fait jamais crasher le briefing.
    try:
        from source_monitor import render_briefing_block
        lines.append(render_briefing_block(source_health_path))
    except Exception as e:  # noqa: BLE001
        logger.warning("Santé des sources non rendue : %s", e)
        lines.append("## Santé des sources")
        lines.append("")
        lines.append("_Indisponible (erreur de rendu)._")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# « News par actif » (P7) — section EN FIN de bulletin
# ---------------------------------------------------------------------------
# Pour chacun des 12 actifs (ordre canonique), liste les events news du corpus
# matin qui le concernent : date / source / titre + sens d'impact déjà qualifié
# (↑/↓/→ via _direction_arrow_for). RÉUTILISE `group_by_actif` (events groupés
# par actif). Actif sans news → « — aucune actualité ». ZÉRO invention : seuls de
# vrais events de l'events-log sont rendus. Déterministe, best-effort.


def build_news_par_actif(
    events_path: Path = EVENTS_LOG,
    today: Optional[date] = None,
    max_par_actif: int = 3,
) -> str:
    """Construit le bloc markdown '## News par actif' (P7), placé EN FIN.

    Args:
        events_path: chemin vers events-log.md
        today: date du run (default = today)
        max_par_actif: nombre max de puces par actif

    Returns:
        Markdown du bloc (sans trailing newline superflu).
    """
    today = today or date.today()
    all_events = parse_events(events_path)
    impactful = filter_recent_impactful(all_events, today)
    groups = group_by_actif(impactful)

    lines: List[str] = ["## News par actif", ""]
    lines.append(
        f"_Actualités à impact des dernières {FRESHNESS_HOURS}h, groupées par "
        f"actif (la flèche en tête de puce donne le sens d'impact déjà qualifié : "
        f"haussier / baissier / neutre). Ordre canonique des 12 actifs._"
    )
    lines.append("")

    # Ordre canonique des 12 actifs (dédup en préservant l'ordre).
    ordre_actifs: List[str] = []
    seen: set = set()
    for actif, _, _ in TICKER_TO_ACTIF:
        if actif not in seen:
            ordre_actifs.append(actif)
            seen.add(actif)

    for actif in ordre_actifs:
        lines.append(f"### {actif}")
        evs = groups.get(actif)
        if not evs:
            lines.append("- — aucune actualité")
            lines.append("")
            continue
        evs_sorted = _dedup_news_in_actif(_sort_by_materiality_then_date(evs))
        for ev in evs_sorted[:max_par_actif]:
            lines.append(_puce(ev, actif_label=actif))
        if len(evs_sorted) > max_par_actif:
            lines.append(
                f"- _(+{len(evs_sorted) - max_par_actif} autres events sur cet actif)_"
            )
        lines.append("")

    # Events hors univers (Autres) — informatif, jamais rattaché à un actif suivi.
    autres = groups.get("Autres")
    if autres:
        autres_sorted = _dedup_news_in_actif(_sort_by_materiality_then_date(autres))
        lines.append("### Autres (hors univers suivi)")
        for ev in autres_sorted[:max_par_actif]:
            lines.append(_puce(ev, actif_label="Autres"))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Insertion dans le bulletin
# ---------------------------------------------------------------------------

# Titre de bulletin : '# Bulletin Analyste — YYYY-MM-DD'
TITRE_RE = re.compile(r"^(#\s+Bulletin[^\n]*\n)", re.MULTILINE)


def prepend_to_bulletin(bulletin_path: Path, briefing_md: str) -> bool:
    """Insère `briefing_md` (Décor du jour) après le H1 + la méta, AVANT la
    première section « ## … » (P6 — Décor en tête, après les lignes de méta).

    Si un bloc « ## Décor du jour » existe déjà (re-run), on le remplace. Si le
    titre H1 est introuvable, on préfixe en tête (best-effort).

    Retourne True si écrit, False si rien à faire (fichier absent).
    """
    if not bulletin_path.exists():
        logger.warning("bulletin introuvable : %s", bulletin_path)
        return False
    content = bulletin_path.read_text(encoding="utf-8")

    # Si un Décor existe déjà, le retirer pour le remplacer. Le bloc inclut
    # « ## Décor du jour » + (optionnel) « ## Santé des sources » accolée.
    existing_re = re.compile(
        r"## Décor du jour\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    if existing_re.search(content):
        content = existing_re.sub("", content, count=1)
        sante_re = re.compile(
            r"## Santé des sources\n.*?(?=\n## |\Z)",
            re.DOTALL,
        )
        content = sante_re.sub("", content, count=1)
        content = re.sub(r"\n{3,}", "\n\n", content)

    block = briefing_md.rstrip() + "\n\n"

    m = TITRE_RE.search(content)
    if m:
        # P6 — insérer APRÈS la méta : on cible le 1er « ## » qui suit le H1 et on
        # insère juste avant lui. Fallback : juste après le H1 si pas de « ## ».
        first_h2 = re.search(r"^## ", content[m.end():], re.MULTILINE)
        if first_h2:
            insert_at = m.end() + first_h2.start()
            new_content = (
                content[:insert_at].rstrip() + "\n\n" + block
                + content[insert_at:].lstrip("\n")
            )
        else:
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
