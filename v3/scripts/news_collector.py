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
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

from config import (
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

logger = logging.getLogger(__name__)


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
        """Ligne markdown brute (sans extraction) — schéma v2 directionnel.

        Colonnes (14) :
        date | L1 | L2 | trigger | cours | latence | R | source | news_zone |
        category | pattern_id | impacts | materiality | reliability
        """
        date = self.published.strftime("%Y-%m-%d")
        safe_title = self.title.replace("|", "/").strip()[:250]
        return (
            f"| {date} |  |  | {safe_title} |  |  | 1 | "
            f"{self.source} |  |  |  |  |  |  |"
        )

    def as_event_log_line_extracted(self, e) -> str:
        """Ligne markdown enrichie — schéma v2 directionnel.

        Colonnes (14) : date | L1 | L2 | trigger | cours | latence | R | source |
        news_zone | category | pattern_id | impacts | materiality | reliability

        - L1/L2 conservés pour rétro-compat lecteurs anciens (laissés vides : on
          ne fait plus de double-taxonomie).
        - cours = libellé lisible reconstruit à partir des impacts (premier actif).
        - impacts = encodage compact 'ASSET:DIR:CONF;...' (voir extractor.encode_impacts).
        """
        date = self.published.strftime("%Y-%m-%d")

        def safe(v):
            return (str(v) if v is not None else "").replace("|", "/").strip()

        # Lazy import pour éviter le coût si non utilisé
        from extractor import encode_impacts

        impacts_str = encode_impacts(getattr(e, "impacts", []) or [])
        # cours = libellé lisible (premier actif) pour rétro-compat parsers historiques
        first_asset = ""
        impacts = getattr(e, "impacts", []) or []
        if impacts:
            first_asset = impacts[0].asset

        cols = [
            date,
            "",  # L1 (legacy, vide)
            safe(getattr(e, "subcat", "")),  # L2 = subcat (libre)
            safe(getattr(e, "trigger", "") or self.title)[:250],
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

def _fetch_rss(name: str, url: str) -> list:
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning("RSS fetch failed for %s: %s", name, e)
        return []

    parsed = feedparser.parse(response.content)
    items = []
    for entry in parsed.entries:
        try:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_dt = (datetime(*published[:6], tzinfo=timezone.utc) if published
                      else datetime.now(timezone.utc))
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
    return items


def collect_rss_phase21() -> dict:
    """Poll RSS_FEEDS (sauf Reuters mort), dédup, blacklist+whitelist finance."""
    _ensure_db()
    recent_titles = _get_recent_titles()

    raw = []
    for name, url, _interval in RSS_FEEDS:
        if name.startswith("reuters_"):
            continue
        raw.extend(_fetch_rss(name, url))

    deduped = []
    for item in raw:
        if _is_dup(item.title, recent_titles):
            continue
        deduped.append(item)
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

def _fetch_gnews(query: str, api_key: str, base_url: str) -> list:
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
    try:
        r = requests.get(base_url, params=params, headers=headers, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as e:
        logger.warning("GNews fetch failed for query '%s': %s", query, e)
        return []

    items = []
    for art in data.get("articles", []) or []:
        try:
            pub_raw = art.get("publishedAt") or ""
            try:
                pub_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except ValueError:
                pub_dt = datetime.now(timezone.utc)
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
    return items


def _fetch_newsapi(query: str, api_key: str, base_url: str) -> list:
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
    try:
        r = requests.get(base_url, params=params, headers=headers, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as e:
        logger.warning("NewsAPI fetch failed for query '%s': %s", query, e)
        return []

    if data.get("status") and data.get("status") != "ok":
        logger.warning("NewsAPI returned status=%s message=%s",
                       data.get("status"), data.get("message"))
        return []

    items = []
    for art in data.get("articles", []) or []:
        try:
            pub_raw = art.get("publishedAt") or ""
            try:
                pub_dt = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except ValueError:
                pub_dt = datetime.now(timezone.utc)
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
    return items


def _collect_structured() -> list:
    """Poll GNews + NewsAPI sur toutes les STRUCTURED_QUERIES.
    Clé absente → skip propre (log + 0 item, zéro invention).
    """
    raw = []
    for name, kind, env_key, base_url in STRUCTURED_SOURCES:
        api_key = os.environ.get(env_key, "").strip()
        if not api_key:
            logger.info("Structured source %s: no API key (%s) → skip", name, env_key)
            continue
        for query in STRUCTURED_QUERIES:
            if kind == "gnews":
                raw.extend(_fetch_gnews(query, api_key, base_url))
            elif kind == "newsapi":
                raw.extend(_fetch_newsapi(query, api_key, base_url))
            else:
                logger.warning("Unknown structured kind: %s", kind)
    return raw


# ============================================================
# Collecte unifiée — Phase 2.2
# ============================================================

def collect_all() -> dict:
    """Poll mainstream + early-signal + structured (GNews/NewsAPI).
    Dédup cross-source via cache SQLite + Jaccard.
    Pré-filtre finance (blacklist puis whitelist).
    Dégradation gracieuse : un feed KO log WARNING + skip, ne casse pas la run.
    """
    _ensure_db()
    recent_titles = _get_recent_titles()

    raw = []

    # 1) RSS mainstream (hors Reuters mort)
    for name, url, _interval in RSS_FEEDS:
        if name.startswith("reuters_"):
            continue
        try:
            raw.extend(_fetch_rss(name, url))
        except Exception as e:
            logger.warning("RSS mainstream %s crashed: %s — skip", name, e)

    # 2) RSS early-signal (sources officielles)
    for name, url, _interval in EARLY_SIGNAL_FEEDS:
        try:
            raw.extend(_fetch_rss(name, url))
        except Exception as e:
            logger.warning("RSS early-signal %s crashed: %s — skip", name, e)

    # 3) Sources structurées (GNews + NewsAPI)
    try:
        raw.extend(_collect_structured())
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
        _add_title(item)
        recent_titles.insert(0, item.title)
        recent_titles = recent_titles[:DEDUP_CACHE_SIZE]

    # Blacklist d'abord, whitelist ensuite
    filtered = [it for it in deduped if is_finance_relevant(it.title, it.summary)]
    skipped = len(deduped) - len(filtered)

    logger.info(
        "collect_all: raw=%d → deduped=%d → finance_relevant=%d (skipped %d)",
        len(raw), len(deduped), len(filtered), skipped,
    )

    return {
        "raw": raw,
        "deduped": deduped,
        "filtered": filtered,
        "skipped_non_finance": skipped,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = collect_all()
    print(f"\n=== {len(result['raw'])} raw → {len(result['deduped'])} deduped → "
          f"{len(result['filtered'])} finance ({result['skipped_non_finance']} skipped) ===\n")
    for item in result["filtered"][:10]:
        print(f"  [{item.source}] {item.title[:100]}")
