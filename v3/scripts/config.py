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

# NB (30/05) : tous les flux ci-dessous ont été testés en réel (HTTP 200 + items RSS).
# Les flux institutionnels qui bloquaient (OPEC/LME/Kitco/USDA/NOAA/IMF/WB/BIS/BLS,
# 403/404 même avec UA navigateur) ont été RETIRÉS. Pour les actifs sous-couverts
# (agri/cuivre/CAC), on utilise Google News RSS ciblé (robuste, ~100 items/requête).
EARLY_SIGNAL_FEEDS = [
    # Énergie (pétrole, gaz)
    ("eia_today_in_energy",    "https://www.eia.gov/rss/todayinenergy.xml",                  1800),
    ("eia_press_releases",     "https://www.eia.gov/rss/press_rss.xml",                      1800),
    ("oilprice",               "https://oilprice.com/rss/main",                              1800),
    # Métaux / commodités
    ("mining_com",             "https://www.mining.com/feed/",                               1800),
    ("investing_commodities",  "https://www.investing.com/rss/commodities.rss",              1800),
    ("investing_metals",       "https://www.investing.com/rss/commodities_Metals.rss",       1800),
    # Banques centrales — communiqués
    ("fed_press_all",          "https://www.federalreserve.gov/feeds/press_all.xml",         1800),
    ("fed_monetary",           "https://www.federalreserve.gov/feeds/press_monetary.xml",    1800),
    ("ecb_press",              "https://www.ecb.europa.eu/rss/press.html",                   1800),
    ("boe_news",               "https://www.bankofengland.co.uk/rss/news",                   1800),
    ("boj_news",               "https://www.boj.or.jp/en/rss/whatsnew.xml",                  1800),
    # Macro
    ("investing_economy",      "https://www.investing.com/rss/news_95.rss",                  1800),
    # Actifs sous-couverts — Google News RSS ciblé (testé : ~100 items/requête)
    ("gnews_coffee",  "https://news.google.com/rss/search?q=coffee+prices+arabica+robusta&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_cocoa",   "https://news.google.com/rss/search?q=cocoa+prices+Ivory+Coast+Ghana&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_wheat",   "https://news.google.com/rss/search?q=wheat+grain+prices+harvest&hl=en-US&gl=US&ceid=US:en",     3600),
    ("gnews_copper",  "https://news.google.com/rss/search?q=copper+prices+LME+China+demand&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_cac40",   "https://news.google.com/rss/search?q=CAC+40+bourse+Paris+France&hl=fr&gl=FR&ceid=FR:fr",        3600),
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
    # Requêtes dédiées aux actifs sous-couverts (audit 30/05) — agri / cuivre / CAC
    "coffee prices OR arabica OR robusta OR Brazil harvest OR Vietnam coffee",
    "cocoa prices OR Ivory Coast OR Ghana cocoa OR cocoa grindings",
    "wheat prices OR Black Sea grain OR Russia wheat OR US wheat crop",
    "copper prices OR LME copper OR Chile mine OR China copper demand",
    "CAC 40 OR French stocks OR LVMH OR TotalEnergies OR France politics budget",
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
    # Early-signal — flux testés fonctionnels (30/05)
    "eia_today_in_energy": 1.5, "eia_press_releases": 1.4,
    "oilprice": 1.0,
    "mining_com": 1.1, "investing_commodities": 0.9, "investing_metals": 0.9,
    "fed_press_all": 1.5, "fed_monetary": 1.5,
    "ecb_press": 1.5, "boe_news": 1.3, "boj_news": 1.3,
    "investing_economy": 0.9,
    # Actifs sous-couverts — Google News RSS ciblé (agrégateur, bruit modéré)
    "gnews_coffee": 0.8, "gnews_cocoa": 0.8, "gnews_wheat": 0.8,
    "gnews_copper": 0.8, "gnews_cac40": 0.8,
    # Sources structurées (agrégateurs API) — bruit élevé mais couverture large
    "gnews": 0.7, "newsapi": 0.7,
}


def source_weight(name: str) -> float:
    """Retourne le poids d'une source (DEFAULT si inconnue)."""
    return SOURCE_WEIGHTS.get(name, DEFAULT_SOURCE_WEIGHT)
