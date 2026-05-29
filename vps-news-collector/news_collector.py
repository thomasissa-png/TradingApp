"""TradingApp v3 — News Collector (Phase 2.1 : pré-filtre finance + extraction)

Phase 1 : Reuters seul, lignes events-log brutes (colonnes vides).
Phase 2.1 (cette version) :
- Élargi à BBC + CNBC + Investing (Reuters DEAD, on l'exclut).
- Pré-filtre `is_finance_relevant()` pour limiter les appels DeepSeek.
- Méthode `as_event_log_line_extracted()` pour formater avec les colonnes L1/L2/etc.
  remplies par l'extracteur.

Phase 2.2 (plus tard) : élargir à EARLY_SIGNAL_FEEDS + STRUCTURED_SOURCES.
"""

import logging
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests

from config import RSS_FEEDS, DEDUP_JACCARD_THRESHOLD, DEDUP_CACHE_SIZE, USER_AGENT, HTTP_TIMEOUT

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
        """Ligne markdown sans extraction (colonnes L1/L2/cours/etc. vides).
        Utilisée quand l'extracteur DeepSeek est désactivé ou en échec."""
        date = self.published.strftime("%Y-%m-%d")
        safe_title = self.title.replace("|", "/").strip()[:250]
        return f"| {date} |  |  | {safe_title} |  |  |  |  |  | 1 | {self.source} |  |  |"

    def as_event_log_line_extracted(self, e) -> str:
        """Ligne markdown enrichie avec l'ExtractedEvent du LLM.
        Colonnes : date | L1 | L2 | trigger | cours | conséquence | latence | durée | fin | R | source | news_zone | pattern_id"""
        date = self.published.strftime("%Y-%m-%d")
        def safe(v):
            return (v or "").replace("|", "/").strip()
        cols = [
            date,
            safe(e.L1),
            safe(e.L2),
            safe(e.trigger or self.title)[:250],
            safe(e.cours),
            safe(e.consequence),
            safe(e.latence),
            safe(e.duree),
            safe(e.fin),
            "1",
            self.source,
            safe(e.news_zone),
            "",  # pattern_id à venir en Phase 2.3
        ]
        return "| " + " | ".join(cols) + " |"


# ============================================================
# Pré-filtre finance — keywords ouverts
# ============================================================

# On veut filtrer LARGEMENT (ne pas rater une news pertinente) mais éviter
# les news lifestyle/sport/people. Les mots-clés couvrent les 12 actifs +
# les drivers macro habituels.
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
    # Maritime / supply chain (signal commodity)
    r"\bsuez\b", r"\bpanama\s+canal\b", r"\bormuz\b", r"\bhormuz\b",
    r"\bport\b", r"\btanker\b", r"\bshipping\b", r"\bfreight\b",
    r"\bsupply\s+chain\b",
    # Corp tech / IA (méga-caps)
    r"\bnvidia\b", r"\bnvda\b", r"\bmicrosoft\b", r"\bmsft\b",
    r"\bapple\b", r"\baapl\b", r"\bgoogle\b", r"\bgoogl\b",
    r"\bamazon\b", r"\bamzn\b", r"\bmeta\b", r"\btesla\b", r"\btsla\b",
    r"\bai\b", r"\bartificial\s+intelligence\b", r"\bchip(s)?\b",
    r"\bsemiconductor(s)?\b",
    # Crypto (faible weighting mais pas exclu)
    r"\bbitcoin\b", r"\bbtc\b", r"\bethereum\b", r"\beth\b", r"\bcrypto\b",
    # Météo (driver agri)
    r"\bhurricane\b", r"\btyphoon\b", r"\bnoaa\b", r"\bel\s+niño\b",
    r"\bla\s+niña\b", r"\bfrost\b", r"\bgel\b",
]

_FINANCE_PATTERN = re.compile("|".join(FINANCE_KEYWORDS), re.IGNORECASE)


def is_finance_relevant(title: str, summary: str = "") -> bool:
    """Retourne True si la news contient au moins 1 mot-clé financier.
    Filtrer côté collector pour éviter d'envoyer du bruit à DeepSeek.
    """
    text = f"{title} {summary}"
    return bool(_FINANCE_PATTERN.search(text))


# ============================================================
# Cache dédup — SQLite
# ============================================================

DB_PATH = Path("/opt/tradingapp/data/titles_cache.db")


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


def _add_title(item: NewsItem):
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
# Dédup Jaccard 0,65
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
# Collecte RSS
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
    """Phase 2.1 : poll tous les RSS_FEEDS sauf Reuters (mort), dédup, pré-filtre finance.

    Retourne un dict {
        "raw": [NewsItem],          # tous les items collectés
        "deduped": [NewsItem],       # après dédup Jaccard
        "filtered": [NewsItem],      # après pré-filtre finance (à envoyer à l'extracteur)
        "skipped_non_finance": int,  # combien on a écarté du filtre
    }
    """
    _ensure_db()
    recent_titles = _get_recent_titles()

    raw = []
    for name, url, _interval in RSS_FEEDS:
        if name.startswith("reuters_"):
            continue  # Reuters RSS mort depuis 2020
        raw.extend(_fetch_rss(name, url))

    # Dédup
    deduped = []
    for item in raw:
        if _is_dup(item.title, recent_titles):
            continue
        deduped.append(item)
        _add_title(item)
        recent_titles.insert(0, item.title)
        recent_titles = recent_titles[:DEDUP_CACHE_SIZE]

    # Pré-filtre finance
    filtered = [it for it in deduped if is_finance_relevant(it.title, it.summary)]
    skipped = len(deduped) - len(filtered)

    logger.info(
        "collect_rss_phase21: raw=%d → deduped=%d → finance_relevant=%d (skipped %d non-finance)",
        len(raw), len(deduped), len(filtered), skipped,
    )

    return {
        "raw": raw,
        "deduped": deduped,
        "filtered": filtered,
        "skipped_non_finance": skipped,
    }


# Alias rétrocompatibilité avec Phase 1
def collect_rss_phase1() -> list:
    """Retourne les items dédupliqués (compatibilité Phase 1)."""
    return collect_rss_phase21()["deduped"]


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = collect_rss_phase21()
    print(f"\n=== {len(result['raw'])} raw → {len(result['deduped'])} deduped → "
          f"{len(result['filtered'])} finance ({result['skipped_non_finance']} skipped) ===\n")
    for item in result["filtered"][:10]:
        print(f"  [{item.source}] {item.title[:100]}")
    print(f"\nSamples non-finance écartés :")
    non_fin = [it for it in result["deduped"] if not is_finance_relevant(it.title, it.summary)]
    for item in non_fin[:5]:
        print(f"  [{item.source}] {item.title[:100]}")
