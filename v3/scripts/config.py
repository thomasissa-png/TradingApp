"""TradingApp v3 — Configuration partagée (constantes RSS, dédup, HTTP).

Migré depuis vps-news-collector. Pas de chemins absolus VPS : les chemins
data/log sont relatifs au repo (v3/data/) et configurables via env vars.
"""

import os
from pathlib import Path

# ============================================================
# Chemins (relatifs au repo, surchargables par env)
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]  # /TradingApp
V3_ROOT = REPO_ROOT / "v3"
DATA_DIR = Path(os.environ.get("V3_DATA_DIR", str(V3_ROOT / "data")))
LOG_DIR = Path(os.environ.get("V3_LOG_DIR", str(V3_ROOT / "data" / "logs")))

EVENTS_LOG_PATH = DATA_DIR / "events-log.md"
TITLES_CACHE_DB = DATA_DIR / "titles_cache.db"
COST_LEDGER_PATH = DATA_DIR / "cost-ledger.json"

# ============================================================
# Dédup
# ============================================================

DEDUP_JACCARD_THRESHOLD = 0.65
DEDUP_CACHE_SIZE = 500

# ============================================================
# HTTP
# ============================================================

USER_AGENT = "TradingApp-v3-news-collector/1.0 (+github.com/thomasissa-png/TradingApp)"
HTTP_TIMEOUT = 15

# ============================================================
# RSS feeds — Phase 2.1
# Format : (name, url, poll_interval_sec_legacy)
# Reuters exclu (RSS mort depuis 2020).
# ============================================================

RSS_FEEDS = [
    ("bbc_business",     "http://feeds.bbci.co.uk/news/business/rss.xml",            900),
    ("bbc_world",        "http://feeds.bbci.co.uk/news/world/rss.xml",               900),
    ("cnbc_top",         "https://www.cnbc.com/id/100003114/device/rss/rss.html",    900),
    ("cnbc_economy",     "https://www.cnbc.com/id/20910258/device/rss/rss.html",     900),
    ("cnbc_finance",     "https://www.cnbc.com/id/10000664/device/rss/rss.html",     900),
    ("investing_news",   "https://www.investing.com/rss/news.rss",                   900),
    ("investing_econ",   "https://www.investing.com/rss/news_25.rss",                900),
    ("investing_forex",  "https://www.investing.com/rss/news_1.rss",                 900),
    ("investing_commod", "https://www.investing.com/rss/news_11.rss",                900),
    ("investing_stocks", "https://www.investing.com/rss/news_25.rss",                900),
]
