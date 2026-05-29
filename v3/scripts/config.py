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

# ============================================================
# Early-signal feeds — Phase 2.2
# Sources « en avance de phase » : data officielles, banques centrales,
# régulateurs, organismes sectoriels. RSS / Atom uniquement ici.
# Couvre les 12 actifs : énergie, métaux, agri, indices, FX, macro.
# Format : (name, url, poll_interval_sec_legacy)
# ============================================================

EARLY_SIGNAL_FEEDS = [
    # Énergie (pétrole, gaz, OPEP)
    ("eia_today_in_energy",    "https://www.eia.gov/rss/todayinenergy.xml",                  1800),
    ("eia_press_releases",     "https://www.eia.gov/rss/press_rss.xml",                      1800),
    ("opec_press",             "https://www.opec.org/opec_web/en/press_room/rss.xml",        1800),
    # Métaux / commodités
    ("lme_news",               "https://www.lme.com/api/rss/news",                           1800),
    ("kitco_metals",           "https://www.kitco.com/rss/KitcoNews.xml",                    1800),
    # Agri (USDA / météo)
    ("usda_newsroom",          "https://www.usda.gov/rss/latest-releases.xml",               1800),
    ("noaa_news",              "https://www.noaa.gov/news/rss.xml",                          1800),
    # Banques centrales — communiqués
    ("fed_press_all",          "https://www.federalreserve.gov/feeds/press_all.xml",         1800),
    ("fed_monetary",           "https://www.federalreserve.gov/feeds/press_monetary.xml",    1800),
    ("ecb_press",              "https://www.ecb.europa.eu/rss/press.html",                   1800),
    ("boe_news",               "https://www.bankofengland.co.uk/rss/news",                   1800),
    ("boj_news",               "https://www.boj.or.jp/en/rss/whatsnew.xml",                  1800),
    # Macro / institutionnel
    ("imf_news",               "https://www.imf.org/en/News/RSS?Language=ENG",               1800),
    ("worldbank_news",         "https://www.worldbank.org/en/news/all.rss",                  1800),
    ("bis_press",              "https://www.bis.org/list/press_releases/index.rss",          1800),
    ("bls_news",               "https://www.bls.gov/feed/news_release.rss",                  1800),
]

# ============================================================
# Sources structurées (JSON APIs) — Phase 2.2
# GNews + NewsAPI : requêtes par thématique actif.
# Clés via env : GNEWS_API_KEY, NEWSAPI_KEY. Absent → skip propre.
# ============================================================

# Requêtes finance ciblées sur les 12 actifs (énergie / métaux / agri / indices / FX / macro)
STRUCTURED_QUERIES = [
    "oil OR brent OR WTI OR OPEC",
    "gold OR silver OR copper OR platinum",
    "wheat OR corn OR coffee OR cocoa OR sugar",
    "Fed OR FOMC OR ECB OR inflation OR CPI",
    "Nasdaq OR S&P 500 OR CAC 40 OR DAX",
    "EUR USD OR yen OR dollar index OR forex",
]

STRUCTURED_SOURCES = [
    # (name, kind, env_key, base_url)
    ("gnews",   "gnews",   "GNEWS_API_KEY",   "https://gnews.io/api/v4/search"),
    ("newsapi", "newsapi", "NEWSAPI_KEY",     "https://newsapi.org/v2/everything"),
]

# ============================================================
# Source weights — Phase 2.2
# Pondération qualitative pour priorisation downstream (scoring).
# DEFAULT_SOURCE_WEIGHT pour tout feed non listé.
# Échelle 0.5 (bruit toléré) → 1.5 (signal primaire officiel).
# ============================================================

DEFAULT_SOURCE_WEIGHT = 1.0

SOURCE_WEIGHTS = {
    # Mainstream — bruit modéré, latence faible
    "bbc_business": 0.8, "bbc_world": 0.7,
    "cnbc_top": 0.9, "cnbc_economy": 1.0, "cnbc_finance": 1.0,
    "investing_news": 0.8, "investing_econ": 0.9, "investing_forex": 0.9,
    "investing_commod": 0.9, "investing_stocks": 0.8,
    # Early-signal — sources primaires officielles
    "eia_today_in_energy": 1.5, "eia_press_releases": 1.4,
    "opec_press": 1.5,
    "lme_news": 1.3, "kitco_metals": 1.1,
    "usda_newsroom": 1.4, "noaa_news": 1.2,
    "fed_press_all": 1.5, "fed_monetary": 1.5,
    "ecb_press": 1.5, "boe_news": 1.3, "boj_news": 1.3,
    "imf_news": 1.2, "worldbank_news": 1.1,
    "bis_press": 1.2, "bls_news": 1.4,
    # Sources structurées (agrégateurs) — bruit élevé mais couverture large
    "gnews": 0.7, "newsapi": 0.7,
}


def source_weight(name: str) -> float:
    """Retourne le poids d'une source (DEFAULT si inconnue)."""
    return SOURCE_WEIGHTS.get(name, DEFAULT_SOURCE_WEIGHT)
