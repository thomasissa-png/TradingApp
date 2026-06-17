"""TradingApp v3 — News Collector (Phase 2.1 v3)

Différences vs vps-news-collector :
- Blacklist forte appliquée AVANT la whitelist finance (vire lifestyle/sport/people
  AVANT de tester les mots-clés finance) → évite les faux positifs type
  "Football club owner buys shares of...".
- Cache dédup SQLite déplacé sous v3/data/ (pas /opt/tradingapp).
- as_event_log_line_extracted() compatible schéma 7 champs (sans duree/fin/consequence).
"""

import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests  # noqa: F401 — exposé pour les tests (patch nc.requests.get) ; http_retry partage le même module

from config import (
    BROWSER_HEADERS,
    DEDUP_CACHE_SIZE,
    DEDUP_JACCARD_THRESHOLD,
    EARLY_SIGNAL_FEEDS,
    HTTP_TIMEOUT,
    RSS_FEEDS,
    STRUCTURED_QUERIES,
    STRUCTURED_SOURCES,
    TITLES_CACHE_DB,
    USER_AGENT,
)
from http_retry import http_get_retry, RETRY_STATUS_WITH_403
from source_monitor import SourceMonitor

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GATE C9 — Normalisation UTC des timestamps à l'ingestion (garde-fou P0)
# ---------------------------------------------------------------------------
# Tout timestamp d'event (`published_at`) DOIT être :
#   - tz-aware (jamais naïf) → UTC explicite si la source n'a pas de TZ
#   - rejeté/corrigé s'il est dans le futur > NOW_UTC + FUTURE_TOLERANCE_MIN
#     (horloge source décalée — ex : RSS d'un serveur mal réglé)
# La fraîcheur (canonical_event_date) et le filtre de premier-vu sont faussés
# si on mélange des TZ ou si on accepte un timestamp futur. NE casse PAS la
# logique existante (check_freshness en aval) : on garantit juste l'invariant.
FUTURE_TOLERANCE_MIN: int = 10  # tolérance d'horloge source (minutes)

# ---------------------------------------------------------------------------
# Filtre de fraîcheur À L'INGESTION (garde-fou anti-pollution archive)
# ---------------------------------------------------------------------------
# Google News RSS (queries larges type café) renvoie des articles à `pubDate`
# ANCIEN (jusqu'à 2022) → 1016 lignes pré-2026-04 polluaient events-log et le
# compteur Café (cf. v3/audit/news-coverage-diagnostic.md). Le scoring les écarte
# DÉJÀ via STALE_DAYS=30 (triggers_classifier), mais on évite de les ÉCRIRE.
# Aligné sur STALE_DAYS=30 par défaut. 0 ou négatif → filtre désactivé (zéro
# régression sur les tests / callers qui ne veulent pas filtrer).
INGEST_MAX_AGE_DAYS: int = int(os.environ.get("INGEST_MAX_AGE_DAYS", "30"))


def _is_too_old(item: "NewsItem", now=None) -> bool:
    """True si l'article est plus vieux que INGEST_MAX_AGE_DAYS (publié).

    Zéro invention : `published` est déjà UTC tz-aware (GATE C9). Si le filtre
    est désactivé (≤0) → jamais trop vieux.
    """
    if INGEST_MAX_AGE_DAYS <= 0:
        return False
    pub = getattr(item, "published", None)
    if not isinstance(pub, datetime):
        return False
    now = now or datetime.now(timezone.utc)
    age_days = (now - pub).total_seconds() / 86400.0
    return age_days > INGEST_MAX_AGE_DAYS


def _normalize_to_utc(dt, *, source: str = "") -> datetime:
    """Garantit qu'un datetime est UTC tz-aware et pas dans le futur.

    - dt None / illisible → now(UTC).
    - dt naïf             → UTC (replace tzinfo=UTC).
    - dt aware            → converti en UTC (astimezone).
    - dt > now + FUTURE_TOLERANCE_MIN → ramené à now (log WARNING, horloge source KO).
    """
    if dt is None:
        return datetime.now(timezone.utc)
    if not isinstance(dt, datetime):
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)
    if dt > now_utc + timedelta(minutes=FUTURE_TOLERANCE_MIN):
        logger.warning(
            "C9 timestamp futur rejeté source=%s dt=%s now=%s → ramené à now (horloge décalée)",
            source, dt.isoformat(), now_utc.isoformat(),
        )
        return now_utc
    return dt


# ============================================================
# Modèle
# ============================================================

@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    published: datetime
    summary: str = ""

    def as_event_log_line_raw(self) -> str:
        """Ligne markdown brute (sans extraction) — schéma v2.2 directionnel.

        Colonnes (19) :
        date | L1 | L2 | trigger | cours | latence | R | source | news_zone |
        category | pattern_id | impacts | materiality | reliability |
        event_id | event_date | nature | dedup_status | stale
        """
        # Lazy import (évite cycle si module utilisé en pure-data tests)
        from triggers_classifier import compute_event_id  # noqa
        date = self.published.strftime("%Y-%m-%d")
        safe_title = self.title.replace("|", "/").strip()[:250]
        # En mode brut on ne connaît pas encore d'actif → event_id sur trigger seul.
        event_id = compute_event_id(safe_title, "")
        # event_date = pubDate RSS (déjà strftime), source=rss si self.published existe
        event_date = date
        # 19 colonnes (v2.2 Phase 2) — toutes vides sauf date, trigger, R, source,
        # event_id, event_date.
        cols = [
            date,           # 1 date
            "",             # 2 L1
            "",             # 3 L2
            safe_title,     # 4 trigger
            "",             # 5 cours
            "",             # 6 latence
            "1",            # 7 R
            self.source,    # 8 source
            "",             # 9 news_zone
            "",             # 10 category
            "",             # 11 pattern_id
            "",             # 12 impacts
            "",             # 13 materiality
            "",             # 14 reliability
            event_id,       # 15 event_id
            event_date,     # 16 event_date
            "",             # 17 nature
            "",             # 18 dedup_status
            "",             # 19 stale
        ]
        return "| " + " | ".join(cols) + " |"

    def as_event_log_line_extracted(self, e) -> str:
        """Ligne markdown enrichie — schéma v2.2 directionnel.

        Colonnes (19) : date | L1 | L2 | trigger | cours | latence | R | source |
        news_zone | category | pattern_id | impacts | materiality | reliability |
        event_id | event_date | nature | dedup_status | stale

        - event_id : SHA-256 tronqué 12 hex sur normalise(trigger)+"|"+actif (Phase 2).
        - event_date : pubDate RSS (premier-vu fait foi calculé en aval par classifier).
        - nature : axe persistance DeepSeek (structurel/ponctuel/deja_cote/verbal).
        - dedup_status, stale : laissés vides ici → calculés à la volée par classifier
          (ne pas geler à l'ingest : la canonisation premier-vu nécessite tout l'historique).
        """
        # Lazy import pour éviter le coût si non utilisé
        from extractor import encode_impacts
        from triggers_classifier import compute_event_id

        date = self.published.strftime("%Y-%m-%d")

        def safe(v):
            return (str(v) if v is not None else "").replace("|", "/").strip()

        impacts_str = encode_impacts(getattr(e, "impacts", []) or [])
        # cours = libellé lisible (premier actif) pour rétro-compat parsers historiques
        first_asset = ""
        impacts = getattr(e, "impacts", []) or []
        if impacts:
            first_asset = impacts[0].asset

        trigger_safe = safe(getattr(e, "trigger", "") or self.title)[:250]
        # event_id : hash stable trigger+actif. Si impacts vides → "" en actif
        # (pas d'invention) ; les events sans actif ne participent pas au scoring
        # mais conservent un id traçable.
        event_id = compute_event_id(trigger_safe, first_asset)
        event_date = date  # pubDate RSS ; le canonical_event_date sera dérivé en aval
        nature = safe(getattr(e, "nature", "")) or "ponctuel"

        cols = [
            date,
            "",  # L1 (legacy, vide)
            safe(getattr(e, "subcat", "")),  # L2 = subcat (libre)
            trigger_safe,
            first_asset,  # cours = id actif des 12 (ex: BRENT)
            safe(getattr(e, "latence", "")),
            "1",
            self.source,
            safe(getattr(e, "news_zone", "")),
            safe(getattr(e, "category", "other")),
            "",  # pattern_id Phase 2.3
            impacts_str,
            safe(getattr(e, "materiality", "")),
            safe(getattr(e, "reliability", "")),
            # --- Phase 2 (5 nouvelles colonnes) ---
            event_id,
            event_date,
            nature,
            "",  # dedup_status : calculé à la lecture (canonisation premier-vu)
            "",  # stale : calculé à la lecture (canonical_event_date vs cutoff)
        ]
        return "| " + " | ".join(cols) + " |"


# ============================================================
# Blacklist forte — appliquée AVANT la whitelist
# ============================================================

# Vire les news lifestyle/people/sport AVANT le test finance.
# Évite qu'un titre type "Football star buys Tesla stake" matche `tesla` alors
# qu'on veut filtrer le bruit sport.
BLACKLIST_KEYWORDS = [
    # Royals / celebrity
    r"\broyal\b", r"\bking\s+charles\b", r"\bqueen\b", r"\bprince\b", r"\bprincess\b",
    r"\bbuckingham\b", r"\bcelebrity\b", r"\bcelebrities\b", r"\bkardashian\b",
    r"\binfluencer\b", r"\bredcarpet\b", r"\bred\s+carpet\b",
    # Sport
    r"\bfootball\b", r"\bsoccer\b", r"\bnba\b", r"\bnfl\b", r"\bnhl\b",
    r"\bpremier\s+league\b", r"\bchampions\s+league\b", r"\bfifa\b", r"\buefa\b",
    r"\bolympics?\b", r"\btennis\b", r"\bgolf\b", r"\bformula\s+1\b", r"\bf1\b",
    r"\bcricket\b", r"\brugby\b",
    # Lifestyle
    r"\brecipe\b", r"\brecipes\b", r"\bcooking\b", r"\brestaurant\s+review\b",
    r"\bhoroscope\b", r"\bzodiac\b", r"\bastrology\b",
    r"\bfashion\b", r"\bcouture\b", r"\bcatwalk\b", r"\brunway\s+show\b",
    r"\bgossip\b", r"\bdating\b", r"\bromance\b", r"\bwedding\b",
    r"\btravel\s+guide\b", r"\btourism\b", r"\bcruise\s+ship\b",
    # Entertainment
    r"\bmovie\s+review\b", r"\bbox\s+office\b", r"\bnetflix\s+show\b",
    r"\btv\s+show\b", r"\bgrammys?\b", r"\boscars?\b", r"\bemmys?\b",
    # Misc bruit
    r"\bobituary\b", r"\bobituaries\b", r"\bfuneral\b",
]

_BLACKLIST_PATTERN = re.compile("|".join(BLACKLIST_KEYWORDS), re.IGNORECASE)


def is_blacklisted(title: str, summary: str = "") -> bool:
    text = f"{title} {summary}"
    return bool(_BLACKLIST_PATTERN.search(text))


# ============================================================
# Whitelist finance
# ============================================================

FINANCE_KEYWORDS = [
    # Indices / actions
    r"\bs&?p\s*5?0?0\b", r"\bnasdaq\b", r"\bdow\b", r"\bcac\s?40\b",
    r"\bdax\b", r"\bnikkei\b", r"\bftse\b", r"\bstoxx\b", r"\bvix\b",
    r"\bequity\b", r"\bequities\b", r"\bstock(s)?\b", r"\bshares?\b",
    r"\bearnings\b", r"\bguidance\b", r"\bipo\b", r"\bbuyback\b",
    # FX
    r"\beur(o|/usd|/gbp|/jpy)\b", r"\busd\b", r"\bdollar\b", r"\byen\b",
    r"\bsterling\b", r"\bfx\b", r"\bforeign\s+exchange\b",
    # Énergie
    r"\boil\b", r"\bcrude\b", r"\bbrent\b", r"\bwti\b", r"\bopec\b",
    r"\bgas\b", r"\bnatural\s+gas\b", r"\blng\b", r"\beia\b",
    r"\bgasoline\b", r"\bdiesel\b",
    # Métaux
    r"\bgold\b", r"\bsilver\b", r"\bcopper\b", r"\bplatinum\b",
    r"\baluminum\b", r"\baluminium\b", r"\blme\b", r"\bbullion\b",
    # Agri
    r"\bwheat\b", r"\bcorn\b", r"\bsoy(bean)?s?\b", r"\bcoffee\b",
    r"\bcocoa\b", r"\bcotton\b", r"\bsugar\b", r"\bharvest\b",
    r"\busda\b", r"\bwasde\b", r"\bdrought\b",
    # Offre prospective cacao (ajout 16/06) : choc d'offre météo/récolte/maladie.
    r"\bel\s+ni(ñ|n)o\b", r"\bblack\s+pod\b", r"\bswollen\s+shoot\b",
    r"\bcherelles?\b", r"\bicco\b",
    # Banques centrales
    r"\bfed(eral)?\s+reserve\b", r"\bfed\b", r"\bfomc\b", r"\bpowell\b",
    r"\becb\b", r"\blagarde\b", r"\bboj\b", r"\bbank\s+of\s+japan\b",
    r"\bboe\b", r"\bbank\s+of\s+england\b", r"\bpboc\b",
    r"\brate\s+(hike|cut|decision|hold)\b", r"\binterest\s+rate(s)?\b",
    r"\bbasis\s+point(s)?\b", r"\bbps\b",
    # Macro
    r"\bcpi\b", r"\binflation\b", r"\bgdp\b", r"\brecession\b",
    r"\bnfp\b", r"\bnon-?farm\s+payroll\b", r"\bunemployment\b",
    r"\bpmi\b", r"\bism\b", r"\bretail\s+sales\b", r"\bjobless\s+claims\b",
    r"\btreasury\b", r"\byield\b", r"\bbond(s)?\b", r"\bcurve\b",
    r"\bsovereign\b", r"\brating\b", r"\bdowngrade\b", r"\bupgrade\b",
    # Géopolitique / Commerce
    r"\biran\b", r"\bisrael\b", r"\bukraine\b", r"\brussia\b", r"\bchina\b",
    r"\btaiwan\b", r"\bnorth\s+korea\b", r"\bopec\+?\b",
    r"\btariff(s)?\b", r"\btrade\s+war\b", r"\bsanction(s)?\b",
    r"\bembargo\b", r"\bairstrike(s)?\b", r"\bstrike\b", r"\bwar\b",
    r"\bcease.?fire\b",
    # Maritime / supply chain
    r"\bsuez\b", r"\bpanama\s+canal\b", r"\bormuz\b", r"\bhormuz\b",
    r"\bport\b", r"\btanker\b", r"\bshipping\b", r"\bfreight\b",
    r"\bsupply\s+chain\b",
    # Méga-caps tech
    r"\bnvidia\b", r"\bnvda\b", r"\bmicrosoft\b", r"\bmsft\b",
    r"\bapple\b", r"\baapl\b", r"\bgoogle\b", r"\bgoogl\b",
    r"\bamazon\b", r"\bamzn\b", r"\bmeta\b", r"\btesla\b", r"\btsla\b",
    r"\bai\b", r"\bartificial\s+intelligence\b", r"\bchip(s)?\b",
    r"\bsemiconductor(s)?\b",
    # Crypto
    r"\bbitcoin\b", r"\bbtc\b", r"\bethereum\b", r"\beth\b", r"\bcrypto\b",
    # Météo
    r"\bhurricane\b", r"\btyphoon\b", r"\bnoaa\b", r"\bel\s+niño\b",
    r"\bla\s+niña\b", r"\bfrost\b",
    # --- Finance FR (fix 31/05 : gnews_cac40 muet car titres FR non whitelistés) ---
    # Marchés / actions
    r"\bbourse\b", r"\bcotation\b", r"\bcours\s+action\b", r"\baction(s)?\s+(en|de|du|à)\b",
    r"\beuronext\b", r"\bcac\s?40\b", r"\bsbf\s?120\b", r"\bindice(s)?\b",
    # Économie / monnaie / banques centrales
    r"\bbanque\s+centrale\b", r"\btaux\s+(directeur|d'intérêt)\b",
    r"\bpolitique\s+monétaire\b", r"\bbcf\b", r"\bbce\b",
    r"\bobligation(s)?\b", r"\brendement\b", r"\bdette\s+publique\b",
    r"\bdéficit\b", r"\bcroissance\b", r"\brécession\b", r"\binflation\b",
    # Macro FR (acronymes courants)
    r"\bpib\b", r"\bchômage\b", r"\bemploi\b",
    # Méga-caps FR
    r"\blvmh\b", r"\btotalenergies\b", r"\bsanofi\b", r"\bairbus\b",
    r"\bschneider\b", r"\bsaint-gobain\b", r"\bcrédit\s+agricole\b",
    r"\bbnp\s+paribas\b", r"\bsociété\s+générale\b",
    # Trading verbes / signaux FR
    r"\bbénéfices?\b", r"\brésultats?\s+(annuels|trimestriels|semestriels)\b",
    r"\bdividende(s)?\b", r"\bipo\b", r"\boffre\s+publique\b", r"\bopa\b",
    r"\brachat\s+d'actions\b", r"\bémission\s+obligataire\b",
]

_FINANCE_PATTERN = re.compile("|".join(FINANCE_KEYWORDS), re.IGNORECASE)


def is_finance_relevant(title: str, summary: str = "") -> bool:
    """v3 : BLACKLIST d'abord, whitelist ensuite.
    Si match blacklist → out (même si match finance ensuite).
    """
    if is_blacklisted(title, summary):
        return False
    text = f"{title} {summary}"
    return bool(_FINANCE_PATTERN.search(text))


# ============================================================
# Cache dédup SQLite (sous v3/data/)
# ============================================================

DB_PATH = Path(os.environ.get("DEDUP_DB_PATH", str(TITLES_CACHE_DB)))


def _ensure_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT,
            seen_at TIMESTAMP NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_seen_at ON titles(seen_at)")
    conn.commit()
    conn.close()


def _get_recent_titles() -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT title FROM titles ORDER BY seen_at DESC LIMIT ?",
        (DEDUP_CACHE_SIZE,),
    )
    titles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return titles


def _add_title(item: "NewsItem"):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO titles (title, source, url, seen_at) VALUES (?, ?, ?, ?)",
        (item.title, item.source, item.url, datetime.now(timezone.utc)),
    )
    conn.execute("""
        DELETE FROM titles
        WHERE id NOT IN (SELECT id FROM titles ORDER BY seen_at DESC LIMIT ?)
    """, (DEDUP_CACHE_SIZE * 2,))
    conn.commit()
    conn.close()


def mark_title_seen(item: "NewsItem") -> None:
    """API publique : marque définitivement un titre comme vu (dédup committée).

    À appeler par les callers (ex: agent_news) UNIQUEMENT après traitement réussi.
    Sur erreur d'extraction LLM → NE PAS appeler → le titre reste candidat au
    prochain cycle (idempotence, cf. audit-ia §1).
    """
    _ensure_db()
    _add_title(item)


# ============================================================
# Dédup Jaccard
# ============================================================

_STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "à", "au", "aux",
    "en", "sur", "par", "pour", "avec", "sans", "dans", "qui", "que", "ce", "ces",
    "the", "a", "an", "is", "are", "was", "were", "of", "in", "on", "at", "to",
    "and", "or", "for", "with", "as", "by", "from", "this", "that",
}


def _tokenize(title: str) -> set:
    tokens = title.lower().split()
    return {t.strip(".,;:!?\"'()[]") for t in tokens
            if t.lower() not in _STOPWORDS and len(t) > 1}


def _jaccard_similarity(a: str, b: str) -> float:
    set_a, set_b = _tokenize(a), _tokenize(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _is_dup(title: str, recent_titles: list) -> bool:
    return any(_jaccard_similarity(title, prev) >= DEDUP_JACCARD_THRESHOLD for prev in recent_titles)


# ============================================================
# Fetch RSS
# ============================================================

def _fetch_rss(name: str, url: str, monitor: "SourceMonitor | None" = None) -> list:
    """Fetch RSS et enregistre la santé du flux dans `monitor` (si fourni).

    Retour : liste de NewsItem (peut être vide). Les détails d'erreur sont
    persistés dans le monitor (HTTP status, type d'erreur, items_fetched bruts).
    """
    # Headers d'un vrai navigateur (UA + Accept + Accept-Language), pas seulement
    # l'UA : certains WAF (type Cloudflare) inspectent aussi Accept* et 403 un
    # client UA-only. Gratuit, standard, aucun scraping.
    headers = dict(BROWSER_HEADERS)
    # Fetch résilient : retry backoff sur 429/5xx + Retry-After (helper partagé).
    # On INCLUT 403 dans les statuts retriables POUR LES RSS uniquement : un 403 de
    # WAF peut être un challenge INTERMITTENT — le feed répond 200 la plupart du
    # temps — donc un 403 ponctuel est récupérable au retry suivant (contraire d'un
    # 403 d'API à clé invalide). Si le 403 PERSISTE après tous les retries,
    # source_monitor signale le flux en échec → dégradation propre, zéro
    # acharnement. (mining_com a été RETIRÉ le 06/06 : son 403 Cloudflare était
    # permanent par IP runner, donc non récupérable au retry — cf. config.py.)
    status_out: dict = {}
    response = http_get_retry(
        url, headers=headers, timeout=HTTP_TIMEOUT, bucket="rss",
        label=f"rss:{name}", status_out=status_out,
        retry_status=RETRY_STATUS_WITH_403,
    )
    if response is None:
        # Échec APRÈS épuisement des retries (429/5xx) ou statut non-retriable
        # (403/404) ou erreur réseau persistante → on compte l'échec une seule fois.
        # On conserve le dernier statut HTTP observé pour la visibilité monitoring.
        status = status_out.get("status", "error")
        logger.warning("RSS fetch failed for %s (status=%s, après retries)", name, status)
        if monitor is not None:
            monitor.record_call(name, ok=False, http_status=status,
                                items_fetched=0, reason=f"HTTP {status}")
        return []

    http_status: str = str(response.status_code)
    parsed = feedparser.parse(response.content)
    items = []
    for entry in parsed.entries:
        try:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_dt = (datetime(*published[:6], tzinfo=timezone.utc) if published
                      else datetime.now(timezone.utc))
            # GATE C9 — normalisation UTC + rejet futur (horloge source décalée)
            pub_dt = _normalize_to_utc(pub_dt, source=f"rss:{name}")
            items.append(NewsItem(
                title=entry.get("title", "").strip(),
                url=entry.get("link", ""),
                source=name,
                published=pub_dt,
                summary=entry.get("summary", ""),
            ))
        except Exception as e:
            logger.warning("Failed to parse entry from %s: %s", name, e)

    logger.info("RSS %s: %d items fetched", name, len(items))
    if monitor is not None:
        # ok = HTTP OK + parse OK. items_fetched = items bruts (avant dédup/filtre).
        reason = "0 reçus (RSS vide ou parse-friendly mais 0 entries)" if len(items) == 0 else ""
        monitor.record_call(name, ok=True, http_status=http_status,
                            items_fetched=len(items), reason=reason)
    return items


def collect_rss_light(monitor: "SourceMonitor | None" = None) -> list:
    """Récolte RSS LÉGÈRE pour les suivis 12h/18h : titres finance frais, SANS état.

    Réutilise EXACTEMENT le chemin `_fetch_rss` (mêmes flux RSS_FEEDS + early-signal,
    même résilience http_retry) que la collecte principale, mais :
    - ZÉRO écriture dans la DB de dédup SQLite (pas de `_add_title`) → aucun effet
      de bord sur le pipeline 7h (le suivi est pure lecture/présentation).
    - ZÉRO appel DeepSeek / extraction (Q9 — suivi léger) : on ne renvoie que des
      `NewsItem` bruts (title/published/source) déjà filtrés finance (blacklist
      puis whitelist), à charge de l'appelant de filtrer par date / dédupliquer
      contre ce qui a déjà été montré.

    Best-effort : un flux KO log WARNING + skip (jamais de crash). Retour : liste
    de NewsItem finance-pertinents (peut être vide). L'appelant gère la dégradation
    propre si la liste est vide ET qu'aucun flux n'a répondu.
    """
    raw: list = []
    for name, url, _interval in RSS_FEEDS:
        if name.startswith("reuters_"):
            continue
        try:
            raw.extend(_fetch_rss(name, url, monitor=monitor))
        except Exception as e:  # noqa: BLE001 — un flux KO ne bloque pas le suivi
            logger.warning("collect_rss_light: RSS %s KO: %s — skip", name, e)
    for name, url, _interval in EARLY_SIGNAL_FEEDS:
        try:
            raw.extend(_fetch_rss(name, url, monitor=monitor))
        except Exception as e:  # noqa: BLE001
            logger.warning("collect_rss_light: early-signal %s KO: %s — skip", name, e)
    # Filtre finance (blacklist d'abord, whitelist ensuite) — pas de dédup DB.
    filtered = [it for it in raw if it.title and is_finance_relevant(it.title, it.summary)]
    logger.info("collect_rss_light: raw=%d → finance=%d", len(raw), len(filtered))
    return filtered


def collect_rss_phase21(commit_seen: bool = True) -> dict:
    """Poll RSS_FEEDS (sauf Reuters mort), dédup, blacklist+whitelist finance.

    commit_seen=True (défaut) : un titre dédupliqué est immédiatement marqué vu en DB
    (comportement historique, ne casse pas les anciens callers / tests).
    commit_seen=False : la dédup utilise les titres déjà vus pour filtrer, mais
    NE marque PAS les nouveaux comme vus — le caller doit appeler `mark_title_seen()`
    après traitement réussi (idempotence sur erreur d'extraction LLM, cf. audit-ia §1).
    """
    _ensure_db()
    recent_titles = _get_recent_titles()

    raw = []
    for name, url, _interval in RSS_FEEDS:
        if name.startswith("reuters_"):
            continue
        raw.extend(_fetch_rss(name, url))  # pas de monitor sur cette voie legacy

    deduped = []
    for item in raw:
        if _is_dup(item.title, recent_titles):
            continue
        deduped.append(item)
        if commit_seen:
            _add_title(item)
        recent_titles.insert(0, item.title)
        recent_titles = recent_titles[:DEDUP_CACHE_SIZE]

    # Blacklist d'abord, whitelist ensuite
    filtered = [it for it in deduped if is_finance_relevant(it.title, it.summary)]
    skipped = len(deduped) - len(filtered)

    logger.info(
        "collect_rss_phase21: raw=%d → deduped=%d → finance_relevant=%d (skipped %d)",
        len(raw), len(deduped), len(filtered), skipped,
    )

    return {
        "raw": raw,
        "deduped": deduped,
        "filtered": filtered,
        "skipped_non_finance": skipped,
    }


# ============================================================
# Fetch JSON (GNews + NewsAPI) — Phase 2.2
# ============================================================

def _fetch_gnews(query: str, api_key: str, base_url: str,
                 monitor: "SourceMonitor | None" = None) -> list:
    """GNews API : https://gnews.io/docs/v4
    Réponse : {"articles": [{"title", "description", "url", "publishedAt", "source": {"name"}}, ...]}
    """
    params = {
        "q": query,
        "lang": "en",
        "max": 25,
        "apikey": api_key,
    }
    headers = {"User-Agent": USER_AGENT}
    # Fetch résilient : retry backoff sur 429/5xx + Retry-After (helper partagé).
    status_out: dict = {}
    r = http_get_retry(
        base_url, params=params, headers=headers, timeout=HTTP_TIMEOUT,
        bucket="gnews", label="gnews", status_out=status_out,
    )
    if r is None:
        status = status_out.get("status", "error")
        logger.warning("GNews fetch failed for query '%s' (status=%s, après retries)", query, status)
        if monitor is not None:
            monitor.record_call("gnews", ok=False, http_status=status,
                                items_fetched=0, reason=f"HTTP {status}",
                                query=query)
        return []
    http_status = str(r.status_code)
    try:
        data = r.json()
    except ValueError as e:
        logger.warning("GNews JSON invalide (HTTP %s) pour '%s': %s", http_status, query, e)
        if monitor is not None:
            monitor.record_call("gnews", ok=False, http_status=http_status,
                                items_fetched=0, reason="JSON invalide",
                                query=query)
        return []

    items = []
    for art in data.get("articles", []) or []:
        try:
            pub_raw = art.get("publishedAt") or ""
            try:
                pub_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except ValueError:
                pub_dt = datetime.now(timezone.utc)
            # GATE C9 — normalisation UTC + rejet futur
            pub_dt = _normalize_to_utc(pub_dt, source="gnews")
            items.append(NewsItem(
                title=(art.get("title") or "").strip(),
                url=art.get("url", ""),
                source="gnews",
                published=pub_dt,
                summary=(art.get("description") or "").strip(),
            ))
        except Exception as e:
            logger.warning("GNews entry parse failed: %s", e)
    logger.info("GNews query='%s': %d items", query[:40], len(items))
    if monitor is not None:
        monitor.record_call("gnews", ok=True, http_status=http_status,
                            items_fetched=len(items),
                            reason="" if items else "0 reçus")
    return items


def _fetch_newsapi(query: str, api_key: str, base_url: str,
                   monitor: "SourceMonitor | None" = None) -> list:
    """NewsAPI.org : https://newsapi.org/docs/endpoints/everything
    Réponse : {"articles": [{"title", "description", "url", "publishedAt", "source": {"name"}}, ...]}
    """
    params = {
        "q": query,
        "language": "en",
        "pageSize": 25,
        "sortBy": "publishedAt",
        "apiKey": api_key,
    }
    headers = {"User-Agent": USER_AGENT}
    # Fetch résilient : retry backoff sur 429/5xx + Retry-After (helper partagé).
    status_out: dict = {}
    r = http_get_retry(
        base_url, params=params, headers=headers, timeout=HTTP_TIMEOUT,
        bucket="newsapi", label="newsapi", status_out=status_out,
    )
    if r is None:
        status = status_out.get("status", "error")
        logger.warning("NewsAPI fetch failed for query '%s' (status=%s, après retries)", query, status)
        if monitor is not None:
            monitor.record_call("newsapi", ok=False, http_status=status,
                                items_fetched=0, reason=f"HTTP {status}",
                                query=query)
        return []
    http_status = str(r.status_code)
    try:
        data = r.json()
    except ValueError as e:
        logger.warning("NewsAPI JSON invalide (HTTP %s) pour '%s': %s", http_status, query, e)
        if monitor is not None:
            monitor.record_call("newsapi", ok=False, http_status=http_status,
                                items_fetched=0, reason="JSON invalide",
                                query=query)
        return []

    if data.get("status") and data.get("status") != "ok":
        logger.warning("NewsAPI returned status=%s message=%s",
                       data.get("status"), data.get("message"))
        if monitor is not None:
            monitor.record_call("newsapi", ok=False, http_status=http_status,
                                items_fetched=0,
                                reason=f"API status={data.get('status')}",
                                query=query)
        return []

    items = []
    for art in data.get("articles", []) or []:
        try:
            pub_raw = art.get("publishedAt") or ""
            try:
                pub_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except ValueError:
                pub_dt = datetime.now(timezone.utc)
            # GATE C9 — normalisation UTC + rejet futur
            pub_dt = _normalize_to_utc(pub_dt, source="newsapi")
            items.append(NewsItem(
                title=(art.get("title") or "").strip(),
                url=art.get("url", ""),
                source="newsapi",
                published=pub_dt,
                summary=(art.get("description") or "").strip(),
            ))
        except Exception as e:
            logger.warning("NewsAPI entry parse failed: %s", e)
    logger.info("NewsAPI query='%s': %d items", query[:40], len(items))
    if monitor is not None:
        monitor.record_call("newsapi", ok=True, http_status=http_status,
                            items_fetched=len(items),
                            reason="" if items else "0 reçus")
    return items


def _collect_structured(monitor: "SourceMonitor | None" = None) -> list:
    """Poll GNews + NewsAPI sur toutes les STRUCTURED_QUERIES.
    Clé absente → skip propre (log + 0 item, zéro invention) + record_skip.
    """
    raw = []
    for name, kind, env_key, base_url in STRUCTURED_SOURCES:
        api_key = os.environ.get(env_key, "").strip()
        if not api_key:
            logger.info("Structured source %s: no API key (%s) → skip", name, env_key)
            if monitor is not None:
                monitor.record_skip(name, reason=f"pas de clé API ({env_key} absent)")
            continue
        for query in STRUCTURED_QUERIES:
            if kind == "gnews":
                raw.extend(_fetch_gnews(query, api_key, base_url, monitor=monitor))
            elif kind == "newsapi":
                raw.extend(_fetch_newsapi(query, api_key, base_url, monitor=monitor))
            else:
                logger.warning("Unknown structured kind: %s", kind)
    return raw


# ============================================================
# Collecte unifiée — Phase 2.2
# ============================================================

def collect_all(commit_seen: bool = True, monitor: "SourceMonitor | None" = None) -> dict:
    """Poll mainstream + early-signal + structured (GNews/NewsAPI).
    Dédup cross-source via cache SQLite + Jaccard.
    Pré-filtre finance (blacklist puis whitelist).
    Dégradation gracieuse : un feed KO log WARNING + skip, ne casse pas la run.

    commit_seen=True (défaut, rétro-compat) : un titre dédupliqué est immédiatement
    marqué vu en DB SQLite.
    commit_seen=False : la dédup filtre contre les titres déjà vus mais NE marque
    PAS les nouveaux comme vus. Le caller (ex: agent_news.run_one_cycle) doit
    appeler `mark_title_seen(item)` après extraction réussie pour fermer la boucle.
    Sur erreur LLM → ne pas marquer → l'item revient au prochain cycle (idempotence,
    cf. audit-ia §1 "Idempotence non garantie sur erreur LLM").
    """
    _ensure_db()
    recent_titles = _get_recent_titles()

    # Crée un monitor par défaut si non fourni — chaque appel est tracé.
    if monitor is None:
        monitor = SourceMonitor()

    raw = []

    # 1) RSS mainstream (hors Reuters mort)
    for name, url, _interval in RSS_FEEDS:
        if name.startswith("reuters_"):
            continue
        try:
            raw.extend(_fetch_rss(name, url, monitor=monitor))
        except Exception as e:
            logger.warning("RSS mainstream %s crashed: %s — skip", name, e)
            monitor.record_call(name, ok=False, http_status="crash",
                                items_fetched=0, reason=f"exception: {type(e).__name__}")

    # 2) RSS early-signal (sources officielles)
    for name, url, _interval in EARLY_SIGNAL_FEEDS:
        try:
            raw.extend(_fetch_rss(name, url, monitor=monitor))
        except Exception as e:
            logger.warning("RSS early-signal %s crashed: %s — skip", name, e)
            monitor.record_call(name, ok=False, http_status="crash",
                                items_fetched=0, reason=f"exception: {type(e).__name__}")

    # 3) Sources structurées (GNews + NewsAPI)
    try:
        raw.extend(_collect_structured(monitor=monitor))
    except Exception as e:
        logger.warning("Structured collect crashed: %s — skip", e)

    # Dédup cross-source
    deduped = []
    for item in raw:
        if not item.title:
            continue
        if _is_dup(item.title, recent_titles):
            continue
        deduped.append(item)
        if commit_seen:
            _add_title(item)
        # Mémoire locale recent_titles : on bloque les doublons INTRA-cycle même
        # si commit_seen=False (sinon 2 dépêches identiques dans le même batch
        # passeraient toutes les deux).
        recent_titles.insert(0, item.title)
        recent_titles = recent_titles[:DEDUP_CACHE_SIZE]

    # Blacklist d'abord, whitelist ensuite, PUIS fraîcheur à l'ingestion.
    # _is_too_old écarte les articles à pubDate ancien (archive Google News RSS)
    # pour ne pas polluer events-log (cf. news-coverage-diagnostic.md §fraîcheur).
    now_utc = datetime.now(timezone.utc)
    finance_ok = [it for it in deduped if is_finance_relevant(it.title, it.summary)]
    filtered = [it for it in finance_ok if not _is_too_old(it, now_utc)]
    skipped_stale = len(finance_ok) - len(filtered)
    skipped = len(deduped) - len(finance_ok)
    if skipped_stale:
        logger.info(
            "collect_all: %d articles finance écartés car trop vieux (>%dj à l'ingestion)",
            skipped_stale, INGEST_MAX_AGE_DAYS,
        )

    # Renseigne items_kept (post-dédup + filtre finance) par source dans le monitor.
    # ⚠️ items_fetched (déjà enregistré) = bruts reçus.
    #    items_kept (ici) = survivants après dédup + blacklist + whitelist finance.
    # Le delta dit si c'est le FILTRE qui jette tout (vs flux qui ne reçoit rien).
    kept_by_source: dict = {}
    for it in filtered:
        kept_by_source[it.source] = kept_by_source.get(it.source, 0) + 1
    # S'assure que les flux appelés mais avec 0 kept apparaissent quand même
    for h_name in list(monitor.by_name.keys()):
        kept_by_source.setdefault(h_name, 0)
    monitor.set_items_kept(kept_by_source)

    logger.info(
        "collect_all: raw=%d → deduped=%d → finance=%d → frais=%d "
        "(skip_non_finance=%d skip_stale=%d) | monitor: %s",
        len(raw), len(deduped), len(finance_ok), len(filtered),
        skipped, skipped_stale, monitor.summary(),
    )

    return {
        "raw": raw,
        "deduped": deduped,
        "filtered": filtered,
        "skipped_non_finance": skipped,
        "skipped_stale": skipped_stale,
        "monitor": monitor,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = collect_all()
    print(f"\n=== {len(result['raw'])} raw → {len(result['deduped'])} deduped → "
          f"{len(result['filtered'])} finance ({result['skipped_non_finance']} skipped) ===\n")
    for item in result["filtered"][:10]:
        print(f"  [{item.source}] {item.title[:100]}")
