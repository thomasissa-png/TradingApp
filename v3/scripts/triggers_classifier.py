"""TradingApp v3 — Classifieur d'events vers triplets binaires.

Lit `v3/data/events-log.md` (tableau markdown : date|L1|L2|trigger|cours|latence|R|source|news_zone|category|pattern_id)
et `v3/config/triggers-and-windows.yml`. Pour chaque critère `type: triplet`,
applique un routage HYBRIDE :

1. **Routage par DeepSeek** (champs déjà extraits) :
   - `cours` mappé via TICKER_TO_ACTIF → quel actif est impacté
   - `category` filtré par CRITERION_CATEGORY_SCOPE → quelle famille de critère
   - À défaut de mapping `cours`, on garde l'event si le `l2`/`trigger` matche
     le scope textuel du critère (DOMAIN_HINTS) — borné pour éviter les faux positifs.
2. **Direction par mots-clés robustes** :
   - Match exact de la phrase (word-boundary, accents OK)
   - OU match "tokens AND" : tous les tokens du mot-clé apparaissent
     comme tokens word-bounded (« Iran ceasefire » matche « extended ceasefire »
     dès lors que l'event est déjà rattaché à l'Iran/Brent via cours+category).
3. Si LONG et SHORT matchent → garder le plus récent.
4. Si l'event est bien rattaché à l'actif+catégorie mais sans cue directionnel
   clair → rester 0 (ne pas inventer de direction).

Pour `type: calendrier`, résout selon la date du jour (Diwali, cycle Brésil).

Règles (cf. triggers-and-windows.yml) :
- Listes fermées : aucun match → 0 (neutre, pas n/a)
- Mots-clés FR + EN
- Case-insensitive, word-boundary, accents gérés
- Si LONG et SHORT matchent dans la même fenêtre → garder le plus récent

Zéro invention : events-log absent/vide → tous triplets = 0.

Interface stable (consommée par criteres_calculator.py) :
- `parse_events_log()` → List[dict]
- `load_triggers_config()` → dict
- `classify_all(events, today, triggers_cfg)` → Dict[actif_key, Dict[cle_courante, int]]
- `_event_text(ev)` → str (utilisé par criteres_calculator pour la gate événement extrême)
"""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger("triggers_classifier")

ROOT = Path(__file__).resolve().parents[1]
EVENTS_LOG = ROOT / "data" / "events-log.md"
TRIGGERS_YML = ROOT / "config" / "triggers-and-windows.yml"


# ---------------------------------------------------------------------------
# Table ticker → actif (cle YAML triggers-and-windows.yml)
# ---------------------------------------------------------------------------
# Format : { actif_key_yml: (set_de_tickers, set_d_alias_textuels) }
# Les tickers sont matchés exactement (entre parenthèses ou délimiteurs).
# Les alias matchent en substring case/accent-insensible sur le champ `cours`.
TICKER_TO_ACTIF: Dict[str, Tuple[Set[str], Set[str]]] = {
    "cac_40": (
        {"^FCHI", "CAC40"},
        {"cac 40", "cac40"},
    ),
    "nasdaq": (
        {"^IXIC", "NASDAQ", "NVDA", "MSFT", "GOOGL", "AAPL", "AMZN", "META", "TSLA"},
        {"nasdaq", "nvidia", "microsoft", "alphabet", "google", "apple",
         "amazon", "meta", "tesla"},
    ),
    "sp500": (
        {"^GSPC", "SP500", "SPX"},
        {"s&p 500", "sp500", "s&p500"},
    ),
    "vix": (
        {"^VIX", "VIX"},
        {"vix"},
    ),
    "eurusd": (
        {"EUR=X", "EURUSD"},
        {"eur/usd", "eurusd", "eur usd"},
    ),
    "petrole": (
        {"BZ=F", "CL=F", "BRENT"},
        {"brent", "petrole", "wti", "crude", "oil"},
    ),
    "or": (
        {"GC=F", "XAU/USD", "GOLD"},
        {"gold", " or "},  # " or " avec espaces pour éviter de matcher "for", "more", etc.
    ),
    "argent": (
        {"SI=F", "XAG/USD", "SILVER"},
        {"silver", "argent"},
    ),
    "cuivre": (
        {"HG=F", "COPPER"},
        {"copper", "cuivre"},
    ),
    "cafe": (
        {"KC=F", "COFFEE"},
        {"coffee", "cafe"},
    ),
    "cacao": (
        {"CC=F", "COCOA"},
        {"cocoa", "cacao"},
    ),
    "ble": (
        {"ZW=F", "WHEAT"},
        {"wheat", "ble"},
    ),
}


# ---------------------------------------------------------------------------
# Mapping ASSET (id IA fermé) → actif_key YAML
# ---------------------------------------------------------------------------
# Utilisé par le routage IA-first : pour un event qui a un `impacts[]` contenant
# {asset:"BRENT",...}, on sait que c'est l'actif `petrole` du YAML.
IA_ASSET_TO_ACTIF: Dict[str, str] = {
    "CAC40":   "cac_40",
    "SP500":   "sp500",
    "NASDAQ":  "nasdaq",
    "EURUSD":  "eurusd",
    "BRENT":   "petrole",
    "VIX":     "vix",
    "GOLD":    "or",
    "SILVER":  "argent",
    "COPPER":  "cuivre",
    "COFFEE":  "cafe",
    "COCOA":   "cacao",
    "WHEAT":   "ble",
}


# Matérialité IA → poids (pour départager LONG/SHORT de même date)
_MAT_WEIGHT = {"high": 3, "medium": 2, "low": 1, "": 1}


# ---------------------------------------------------------------------------
# Scope catégorie + indices de domaine textuel par critère YAML
# ---------------------------------------------------------------------------
# Permet de filtrer les events candidats à un critère donné :
# - `categories` : ensemble des `category` DeepSeek acceptés (None = pas de filtre).
# - `domain_hints` : tokens (lowercase, sans accents) qui, présents dans l2/trigger,
#   permettent de rattacher un event au critère MEME SI le `cours` ne matche pas
#   l'actif. Liste fermée et stricte pour éviter les faux positifs.
# - `strict_actif` : si True, l'event DOIT cibler l'actif via `cours` ou alias ;
#   les domain_hints seuls ne suffisent pas.
CRITERION_SCOPE: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("cac_40", "tension_politique_fr"): {
        "categories": {"geopolitical", "central_bank_subtle", "regulatory", "macro"},
        "domain_hints": {"france", "lecornu", "matignon", "assemblee", "elysee",
                         "gouvernement francais", "loi de finances", "budget france"},
        "strict_actif": False,
    },
    ("nasdaq", "sentiment_ia_megacaps"): {
        "categories": {"earnings", "sector"},
        "domain_hints": {"nvda", "nvidia", "msft", "microsoft", "googl",
                         "alphabet", "aapl", "apple", "amzn", "amazon",
                         "meta", "tsla", "tesla", "guidance", "earnings"},
        "strict_actif": False,
    },
    ("vix", "tension_geopolitique_active"): {
        "categories": {"geopolitical"},
        "domain_hints": {"war", "guerre", "conflict", "conflit", "strike",
                         "frappe", "escalation", "escalade", "ceasefire",
                         "cessez-le-feu", "invasion"},
        "strict_actif": False,
    },
    ("petrole", "geopol_iran"): {
        "categories": {"geopolitical"},
        "domain_hints": {"iran", "ormuz", "hormuz", "tehran", "teheran",
                         "moyen-orient", "middle east", "israel", "gaza",
                         "hezbollah", "houthi", "oman"},
        "strict_actif": False,
    },
    ("petrole", "opec_politique"): {
        "categories": {"commodity", "geopolitical"},
        "domain_hints": {"opec", "opep"},
        "strict_actif": False,
    },
    ("or", "tension_geopolitique"): {
        "categories": {"geopolitical"},
        "domain_hints": {"war", "guerre", "conflict", "conflit", "escalation",
                         "escalade", "sanctions", "terrorism", "terrorisme",
                         "invasion", "ceasefire", "cessez-le-feu"},
        # Pour l'or, on n'exige PAS que `cours` mappe l'or : la tension géopol
        # impacte l'or indirectement via fly-to-safety.
        "strict_actif": False,
    },
    ("argent", "demande_photovoltaique_et_mining_strikes"): {
        "categories": {"commodity", "sector"},
        "domain_hints": {"silver", "argent", "photovoltaic", "photovoltaique",
                         "solar", "mining", "mine"},
        "strict_actif": False,
    },
    ("cuivre", "mining_strikes_chili_perou"): {
        "categories": {"commodity", "geopolitical", "sector"},
        "domain_hints": {"copper", "cuivre", "codelco", "las bambas",
                         "antofagasta", "chile mining", "peru mining",
                         "chili mine", "perou mine"},
        "strict_actif": False,
    },
    ("cuivre", "news_construction_infrastructure"): {
        "categories": {"macro", "sector", "commodity"},
        "domain_hints": {"china stimulus", "stimulus chine", "infrastructure",
                         "belt and road", "real estate china",
                         "immobilier chine", "construction"},
        "strict_actif": False,
    },
    ("cafe", "maladies_cabosses"): {
        "categories": {"commodity"},
        "domain_hints": {"coffee", "cafe", "rust", "rouille", "hemileia",
                         "broca", "outbreak"},
        "strict_actif": False,
    },
    ("cacao", "eudr_impact"): {
        "categories": {"regulatory", "commodity"},
        "domain_hints": {"eudr", "deforestation regulation", "traceability"},
        "strict_actif": False,
    },
    ("cacao", "maladies_cabosses_cacao"): {
        "categories": {"commodity"},
        "domain_hints": {"cocoa", "cacao", "black pod", "swollen shoot",
                         "pod borer", "outbreak"},
        "strict_actif": False,
    },
    ("ble", "geopol_mer_noire"): {
        "categories": {"geopolitical", "commodity"},
        "domain_hints": {"wheat", "ble", "ukraine", "russia wheat", "russie ble",
                         "black sea", "mer noire", "odessa", "corridor"},
        "strict_actif": False,
    },
}


# ---------------------------------------------------------------------------
# Mapping clé YAML → cle_courante des fiches
# ---------------------------------------------------------------------------
# Les fiches (config/fiches/*.yml) utilisent `cle_courante` qui peut différer
# de la clé du critère dans triggers-and-windows.yml. On émet TOUJOURS la clé
# attendue par les fiches (le criteres_calculator fait `triplets[cle_courante]`).
YML_KEY_TO_CLE_COURANTE: Dict[Tuple[str, str], str] = {
    ("petrole", "geopol_iran"): "tension_geopol_moyen_orient",
    ("petrole", "opec_politique"): "opec_production_policy",
    ("ble", "geopol_mer_noire"): "geopolitique_mer_noire",
    ("cacao", "eudr_impact"): "eudr",
    ("cacao", "maladies_cabosses_cacao"): "maladies_cabosses",
    ("cafe", "maladies_cabosses"): "maladies_cabosses_rouille",
    ("argent", "demande_photovoltaique_et_mining_strikes"): "demande_pv_mining_strikes",
    ("cuivre", "news_construction_infrastructure"): "news_construction_infra",
}


# ---------------------------------------------------------------------------
# Parsing events-log.md
# ---------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
_SEPARATOR_RE = re.compile(r"^\s*\|?[\s\-:|]+\|?\s*$")


def _parse_date(s: str) -> Optional[datetime]:
    s = s.strip()
    if not s:
        return None
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
    """Parse le tableau markdown. Retourne une liste de dicts triée par date desc.

    Rétro-compat : supporte 2 formats de header
    - Legacy (11 cols) : date|L1|L2|trigger|cours|latence|R|source|news_zone|category|pattern_id
    - v2 directionnel (14 cols) : + impacts|materiality|reliability

    Une ligne sans colonnes v2 -> impacts décodés=[], materiality="", reliability="".
    """
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

    header = rows[0]
    first_is_date = _parse_date(header[0]) is not None
    # Header par défaut v2 (14 col). Si la ligne a moins de colonnes, on tronque.
    DEFAULT_HEADERS = [
        "date", "l1", "l2", "trigger", "cours", "latence", "r",
        "source", "news_zone", "category", "pattern_id",
        "impacts", "materiality", "reliability",
    ]
    if first_is_date:
        headers_l = DEFAULT_HEADERS
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
        # Décode `impacts` compacts en liste de dicts (rétro-compat : vide si absent)
        ev["_impacts"] = _decode_impacts_str(ev.get("impacts", ""))
        events.append(ev)
    events.sort(key=lambda e: e["_dt"], reverse=True)
    return events


# ---------------------------------------------------------------------------
# Décodage impacts (sans dépendance dure à extractor.py pour la rétro-compat)
# ---------------------------------------------------------------------------

_VALID_DIRECTIONS_TC = {"LONG", "SHORT", "NEUTRAL"}
_VALID_ASSETS_TC = set(IA_ASSET_TO_ACTIF.keys())


def _decode_impacts_str(encoded: str) -> List[Dict[str, Any]]:
    """Décodage tolérant 'ASSET:DIR:CONF;...' → [{asset,direction,confidence}].
    Entrées hors-énum silencieusement ignorées."""
    if not encoded or not isinstance(encoded, str):
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
        if asset not in _VALID_ASSETS_TC or direction not in _VALID_DIRECTIONS_TC:
            continue
        try:
            confidence = int(parts[2].strip()) if len(parts) >= 3 and parts[2].strip() else 0
        except ValueError:
            confidence = 0
        out.append({"asset": asset, "direction": direction, "confidence": confidence})
    return out


# ---------------------------------------------------------------------------
# Helpers texte (normalisation, accents, tokens)
# ---------------------------------------------------------------------------

def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _norm(s: str) -> str:
    """Lowercase + accents retirés (pour comparaisons souples)."""
    return _strip_accents(s or "").lower()


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(s: str) -> List[str]:
    return _TOKEN_RE.findall(_norm(s))


def _event_text(ev: dict) -> str:
    """Concaténation utilisée pour le match mots-clés ET pour la gate événement extrême."""
    parts = []
    for k in ("trigger", "l2", "l1", "source", "news_zone"):
        v = ev.get(k)
        if v:
            parts.append(str(v))
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Routage event → (actif, critère)
# ---------------------------------------------------------------------------

def _event_targets_actif(ev: dict, actif_key: str) -> bool:
    """L'event cible-t-il cet actif via son champ `cours` (ticker ou alias) ?"""
    cours = ev.get("cours") or ""
    if not cours:
        return False
    tickers, aliases = TICKER_TO_ACTIF.get(actif_key, (set(), set()))
    # 1) tickers : match exact entre délimiteurs (parenthèses, virgules, espaces)
    cours_padded = f" {cours} "
    for tk in tickers:
        pattern = r"[\(\s,/]" + re.escape(tk) + r"[\)\s,/]"
        if re.search(pattern, cours_padded, re.IGNORECASE):
            return True
    # 2) alias : substring case/accent-insensible
    cours_norm = f" {_norm(cours)} "
    for alias in aliases:
        if _norm(alias) in cours_norm:
            return True
    return False


def _event_matches_domain(ev: dict, scope: Dict[str, Any]) -> bool:
    """L'event relève-t-il du domaine textuel du critère (via l2/trigger) ?

    Borné par `domain_hints` pour éviter les faux positifs. Chaque hint est
    matché en word-boundary (tokens AND si multi-mot) — ainsi « war » ne match
    pas « warm ».
    """
    hints = scope.get("domain_hints") or set()
    if not hints:
        return False
    text_norm = _norm((ev.get("l2") or "") + " | " + (ev.get("trigger") or ""))
    return any(_phrase_matches(text_norm, h) for h in hints)


def _event_category_ok(ev: dict, scope: Dict[str, Any]) -> bool:
    """L'event a-t-il une `category` acceptée par le scope du critère ?

    Si scope.categories est None/vide → pas de filtre catégorie.
    Si l'event n'a PAS de category → on accepte (degradation gracieuse).
    """
    cats = scope.get("categories")
    if not cats:
        return True
    ev_cat = (ev.get("category") or "").strip().lower()
    if not ev_cat:
        return True  # event sans category → on laisse passer (ne pas pénaliser)
    return ev_cat in cats


def _event_ia_targets_actif(ev: dict, actif_key: str) -> bool:
    """L'event a-t-il un impact IA ciblant cet actif (asset IA mappé via
    IA_ASSET_TO_ACTIF) ?"""
    impacts = ev.get("_impacts") or []
    for imp in impacts:
        asset = imp.get("asset")
        if asset and IA_ASSET_TO_ACTIF.get(asset) == actif_key:
            return True
    return False


def _candidates_for(events: List[dict], actif_key: str, cle: str) -> List[dict]:
    """Filtre les events candidats pour un critère donné (avant matching directionnel).

    Routage IA-first : un event dont `impacts[]` cible cet actif est candidat
    SANS exiger que `cours` ou `domain_hints` matchent (l'IA a déjà inféré
    l'impact réel). Le filtre catégorie reste appliqué pour éviter qu'un event
    earnings pollue un critère géopolitique.
    """
    scope = CRITERION_SCOPE.get((actif_key, cle), {})
    strict = bool(scope.get("strict_actif", False))
    out: List[dict] = []
    for ev in events:
        # Filtre catégorie en premier (peu coûteux, s'applique aussi à l'IA)
        if not _event_category_ok(ev, scope):
            continue
        # Routage : (a) impacts IA ciblent l'actif, (b) `cours` cible l'actif,
        # ou (c) domain_hints matchent (legacy fallback).
        ia_targets = _event_ia_targets_actif(ev, actif_key)
        targets = _event_targets_actif(ev, actif_key)
        domain = _event_matches_domain(ev, scope) if not strict else False
        if not (ia_targets or targets or domain):
            continue
        out.append(ev)
    return out


# ---------------------------------------------------------------------------
# Matching mots-clés robuste (exact phrase OU tokens AND)
# ---------------------------------------------------------------------------

def _phrase_matches(text_norm: str, keyword: str) -> bool:
    """Match d'un mot-clé sur un texte (déjà normalisé).

    Stratégie :
    1. Phrase exacte avec word-boundary (lookaround non-mot).
    2. Sinon, "tokens AND" : tous les tokens du mot-clé apparaissent comme
       tokens word-bounded dans le texte. Permet « Iran ceasefire » de matcher
       « extended ceasefire ... Iran ... » même si non adjacents.
    """
    kw_norm = _norm(keyword).strip()
    if not kw_norm:
        return False
    # 1) Phrase exacte
    escaped = re.escape(kw_norm)
    phrase_re = re.compile(
        rf"(?<![a-z0-9_]){escaped}(?![a-z0-9_])"
    )
    if phrase_re.search(text_norm):
        return True
    # 2) Tokens AND (uniquement si mot-clé multi-token)
    kw_tokens = _tokens(kw_norm)
    if len(kw_tokens) < 2:
        return False
    text_tokens = set(_tokens(text_norm))
    return all(tk in text_tokens for tk in kw_tokens)


def _any_keyword_matches(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return False
    text_norm = _norm(text)
    for kw in keywords:
        if _phrase_matches(text_norm, kw):
            return True
    return False


# ---------------------------------------------------------------------------
# Résolution triplet : routage + direction
# ---------------------------------------------------------------------------

def _ia_direction_for(ev: dict, actif_key: str) -> Optional[str]:
    """Retourne 'LONG' / 'SHORT' / 'NEUTRAL' si l'IA a marqué cet actif dans
    `impacts[]`, sinon None.

    Si plusieurs impacts ciblent le même actif (rare), on garde celui de
    confidence max. NEUTRAL est traité comme un vrai signal "0", pas comme None.
    """
    impacts = ev.get("_impacts") or []
    if not impacts:
        return None
    best_dir: Optional[str] = None
    best_conf = -1
    for imp in impacts:
        asset = imp.get("asset")
        if not asset:
            continue
        if IA_ASSET_TO_ACTIF.get(asset) != actif_key:
            continue
        conf = int(imp.get("confidence") or 0)
        if conf > best_conf:
            best_conf = conf
            best_dir = imp.get("direction")
    return best_dir


def _resolve_triplet(
    events: List[dict],
    actif_key: str,
    cle: str,
    long_keywords: List[str],
    short_keywords: List[str],
    lookback_days: int,
    now: datetime,
) -> int:
    """Résout un triplet en mode HYBRIDE :

    1. **IA-first** : si un event récent dans la fenêtre a un `impacts[]` qui
       cible cet actif, on prend sa direction (LONG=+1, SHORT=-1, NEUTRAL=0).
       Le scope catégorie + domaine reste vérifié pour éviter qu'un event
       Brent off-topic (ex: earnings) pollue un critère géopolitique.
       Départage : matérialité descendante puis date descendante.

    2. **Fallback keyword** (rétro-compat ancien schéma sans impacts, ou IA off) :
       pour les events SANS `_impacts`, on applique l'ancien matching mots-clés
       (LONG/SHORT) avec le même routage scope.

    Règles communes :
    - Fenêtre [now - lookback, now]
    - Long et Short conflictuels (même event ou même date) : matérialité puis
      récence
    """
    if not long_keywords and not short_keywords and not _criterion_has_ia_route(actif_key, cle):
        # Critère sans keywords ni route IA possible : 0 neutre.
        return 0

    cutoff = now - timedelta(days=lookback_days)
    candidates = _candidates_for(events, actif_key, cle)

    # -------- 1) IA-first : un event avec direction IA pour cet actif --------
    ia_long: Optional[Tuple[datetime, int]] = None  # (dt, materiality_weight)
    ia_short: Optional[Tuple[datetime, int]] = None
    ia_seen_any = False
    for ev in candidates:
        dt = ev.get("_dt")
        if not isinstance(dt, datetime):
            continue
        if dt < cutoff or dt > now:
            continue
        direction = _ia_direction_for(ev, actif_key)
        if direction is None:
            continue
        ia_seen_any = True
        mat = (ev.get("materiality") or "").strip().lower()
        weight = _MAT_WEIGHT.get(mat, 1)
        if direction == "LONG":
            if ia_long is None or (weight, dt) > (ia_long[1], ia_long[0]):
                ia_long = (dt, weight)
        elif direction == "SHORT":
            if ia_short is None or (weight, dt) > (ia_short[1], ia_short[0]):
                ia_short = (dt, weight)
        # NEUTRAL : ne touche ni long ni short (mais contribue à ia_seen_any=True)
    if ia_seen_any:
        # Au moins un event IA cible cet actif dans la fenêtre → on tranche en IA-only.
        if ia_long and not ia_short:
            return 1
        if ia_short and not ia_long:
            return -1
        if ia_long and ia_short:
            # Matérialité d'abord, date ensuite
            if (ia_long[1], ia_long[0]) >= (ia_short[1], ia_short[0]):
                return 1
            return -1
        # Que des NEUTRAL → 0
        return 0

    # -------- 2) Fallback keyword (ancien schéma, ou IA n'a rien marqué) -----
    if not long_keywords and not short_keywords:
        return 0
    last_long: Optional[datetime] = None
    last_short: Optional[datetime] = None
    for ev in candidates:
        # On évite de re-traiter les events ayant déjà des impacts IA (cohérence)
        if ev.get("_impacts"):
            continue
        dt = ev.get("_dt")
        if not isinstance(dt, datetime):
            continue
        if dt < cutoff or dt > now:
            continue
        text = _event_text(ev)
        if _any_keyword_matches(text, long_keywords):
            if last_long is None or dt > last_long:
                last_long = dt
        if _any_keyword_matches(text, short_keywords):
            if last_short is None or dt > last_short:
                last_short = dt
    if last_long is None and last_short is None:
        return 0
    if last_long is not None and last_short is None:
        return 1
    if last_short is not None and last_long is None:
        return -1
    if last_long >= last_short:  # type: ignore[operator]
        return 1
    return -1


def _criterion_has_ia_route(actif_key: str, cle: str) -> bool:
    """Un critère est IA-routable si son scope catégorie est défini (sinon
    aucun event IA ne sera retenu — autant le savoir tôt)."""
    scope = CRITERION_SCOPE.get((actif_key, cle))
    return bool(scope)


# ---------------------------------------------------------------------------
# Calendrier (cycle annuel / saisonnier)
# ---------------------------------------------------------------------------

def _resolve_calendrier(cle: str, today: date) -> Optional[int]:
    """Résout les critères calendrier connus. Retourne -1/0/+1 ou None si non géré."""
    m = today.month
    y = today.year
    if cle == "demande_indienne_saisonniere":
        if m in (10, 11, 12):
            return 1
        if m in (1, 2, 3, 4, 5):
            return -1
        return 0
    if cle == "cycle_bresil_biannuel":
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

def _emit_key(actif_key: str, yml_cle: str) -> str:
    """Retourne la clé sous laquelle émettre le triplet (cle_courante des fiches
    si un alias est défini, sinon la clé YAML directe)."""
    return YML_KEY_TO_CLE_COURANTE.get((actif_key, yml_cle), yml_cle)


def classify_all(
    events: Optional[List[dict]] = None,
    today: Optional[datetime] = None,
    triggers_cfg: Optional[dict] = None,
) -> Dict[str, Dict[str, int]]:
    """Pour chaque actif × critère triplet/calendrier, retourne la valeur ∈ {-1,0,+1}.

    Sortie : {actif_key: {cle_courante: valeur_triplet}}
    Les clés émises sont les `cle_courante` attendues par les fiches.
    Les critères `numerique` (fenêtres d'activation) ne sont PAS traités ici
    (le calculator s'en occupe).
    """
    if triggers_cfg is None:
        triggers_cfg = load_triggers_config()
    if events is None:
        events = parse_events_log()
    if today is None:
        today = datetime.now(timezone.utc)
    # Accepte un date OU un datetime (naïf ou aware). On dérive :
    #  - today_dt : datetime aware UTC (fin de journée) pour comparer aux _dt des events
    #  - today_date : date pure pour les critères calendrier
    if isinstance(today, datetime):
        today_dt = today if today.tzinfo else today.replace(tzinfo=timezone.utc)
        today_date = today.date()
    else:
        today_dt = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)
        today_date = today

    out: Dict[str, Dict[str, int]] = {}
    for actif_key, criteres in triggers_cfg.items():
        if not isinstance(criteres, dict):
            continue
        actif_out: Dict[str, int] = {}
        for cle, spec in criteres.items():
            if not isinstance(spec, dict):
                continue
            t = spec.get("type")
            emit_cle = _emit_key(actif_key, cle)
            if t == "triplet" or t == "triplet_composite":
                lookback = int(spec.get("horizon_lookback_jours", 7))
                val = _resolve_triplet(
                    events,
                    actif_key,
                    cle,
                    spec.get("long_keywords", []) or [],
                    spec.get("short_keywords", []) or [],
                    lookback,
                    today_dt,
                )
                actif_out[emit_cle] = val
            elif t == "calendrier":
                val = _resolve_calendrier(cle, today_date)
                if val is not None:
                    actif_out[emit_cle] = val
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
