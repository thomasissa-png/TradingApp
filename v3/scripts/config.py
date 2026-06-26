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

# User-Agent réaliste de navigateur. Un UA "bot" (ancien
# "TradingApp-v3-news-collector/1.0") était bloqué en 403 par certains flux RSS
# qui filtrent les UA non-navigateur. Un UA Chrome desktop standard passe ces
# filtres anti-scraping basiques sans rien forcer d'autre. Si un flux reste 403
# malgré ça, source_monitor le signale en échec (pas d'acharnement) — c'est ce
# qui a conduit au retrait de mining_com le 06/06 (403 Cloudflare CI persistant).
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Headers d'un vrai navigateur (au-delà du seul User-Agent). Certains WAF
# (type Cloudflare) inspectent aussi Accept / Accept-Language : un client qui
# n'envoie QUE le UA ressemble encore à un bot. Ces en-têtes sont gratuits et
# standards — aucun scraping, aucun contournement. Utilisés sur les flux RSS
# (fetch type page). NB : ces headers n'ont PAS suffi pour mining.com (blocage
# WAF par IP runner, pas par signature de requête) → flux retiré le 06/06.
BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
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
    # Fix 31/05 : avant pointait vers news_25.rss (= dup de investing_econ → muet par dédup).
    # news_287.rss = stock-market-news (testé HTTP 200 + items frais).
    ("investing_stocks", "https://www.investing.com/rss/news_287.rss",               900),
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
    # mining_com RETIRÉ 06/06 : 403 Cloudflare PERSISTANT sur les IP des runners
    # GitHub Actions (le feed répond 200 ailleurs, mais jamais depuis CI). Le retry
    # 403 borné posé le 05/06 (RETRY_STATUS_WITH_403) n'a rien changé — toute la
    # plage d'IP runner est bloquée par le WAF. Poids faible (1.1) et redondant avec
    # investing_commodities/metals + oilprice. Retiré net (décision Thomas).
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
    # Ajout 16/06 (chantier sources OFFRE prospective, Thomas) : le système a RATÉ
    # le récit de CHOC D'OFFRE cacao 2026-27 (El Niño / météo Afrique de l'Ouest /
    # récolte sous la normale / cherelles / maladies). gnews_cocoa ci-dessus est
    # demande+prix-centré → on AJOUTE un flux dédié OFFRE PROSPECTIVE (météo, surveys
    # de récolte, maladies, bilans ICCO/StoneX). Additif, zéro invention : si le flux
    # ne renvoie rien → critères offre restent n/a. Alimente le détecteur shadow ③.
    ("gnews_cocoa_supply", "https://news.google.com/rss/search?q=cocoa+%22El+Nino%22+OR+%22West+Africa+weather%22+OR+%22cocoa+harvest%22+OR+cherelles+OR+%22black+pod%22+OR+%22swollen+shoot%22+OR+%22ICCO+deficit%22+OR+%22cocoa+supply%22&hl=en-US&gl=US&ceid=US:en", 3600),
    # Fix 31/05 : query précédente (wheat+grain+prices+harvest) renvoyait ~0-2 titres
    # sur Google News RSS. Query élargie + opérateur OR pour fertilité.
    ("gnews_wheat",   "https://news.google.com/rss/search?q=wheat+OR+grain+OR+%22soft+commodities%22+harvest+USDA+Black+Sea&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_copper",  "https://news.google.com/rss/search?q=copper+prices+LME+China+demand&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_cac40",   "https://news.google.com/rss/search?q=CAC+40+bourse+Paris+France&hl=fr&gl=FR&ceid=FR:fr",        3600),
    # Ajout audit requêtes (round 2) : combler les 2 trous Nasdaq (tech/IA/semi) et VIX (volatilité/risk-off)
    ("gnews_nasdaq",  "https://news.google.com/rss/search?q=Nvidia+OR+semiconductor+OR+%22AI+chips%22+OR+TSMC+OR+%22chip+export%22+OR+%22earnings+guidance%22+OR+%22data+center+capex%22&hl=en-US&gl=US&ceid=US:en", 3600),
    # Round 3 : VIX aligné sur les CAUSES amont (war/escalation/sanctions/bank failure) pas seulement les symptômes
    ("gnews_vix",     "https://news.google.com/rss/search?q=%22market+selloff%22+OR+%22risk-off%22+OR+war+OR+escalation+OR+sanctions+OR+%22bank+failure%22+OR+%22sovereign+default%22&hl=en-US&gl=US&ceid=US:en", 3600),
    # Round 3 : équilibrage BCE (vs déséquilibre 4 flux Fed/US), demande Argent industrielle, achats or banques centrales
    ("gnews_ecb_policy",       "https://news.google.com/rss/search?q=%22ECB+minutes%22+OR+%22Lagarde+speech%22+OR+%22Eurozone+GDP%22+OR+%22EU+trade+balance%22&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_silver_industrial","https://news.google.com/rss/search?q=silver+demand+OR+%22solar+panels%22+OR+%22photovoltaic+silver%22+OR+%22silver+mining+strike%22&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_gold_cb",          "https://news.google.com/rss/search?q=%22central+bank+gold%22+OR+%22gold+reserves%22+OR+%22PBoC+gold%22+OR+WGC+gold&hl=en-US&gl=US&ceid=US:en", 3600),
    # Nouveaux actifs 2026-06-26 — flux dédiés (alignés sur les flux niche existants
    # gnews_copper/cocoa). boj_news (EARLY_SIGNAL ci-dessous) couvre déjà la politique
    # BoJ ; ces flux ajoutent le yen/USD-JPY, le coton et le sucre spécifiquement.
    ("gnews_usdjpy",  "https://news.google.com/rss/search?q=yen+OR+%22USD%2FJPY%22+OR+%22Bank+of+Japan%22+OR+BoJ+OR+%22yen+intervention%22+OR+%22Ministry+of+Finance+Japan%22+OR+%22carry+trade%22&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_sugar",   "https://news.google.com/rss/search?q=%22sugar+prices%22+OR+%22raw+sugar%22+OR+%22Brazil+ethanol%22+OR+UNICA+OR+%22India+sugar+export%22+OR+%22Centre-South+Brazil%22+OR+%22ICE+sugar%22&hl=en-US&gl=US&ceid=US:en", 3600),
    ("gnews_cotton",  "https://news.google.com/rss/search?q=%22cotton+prices%22+OR+%22USDA+cotton%22+OR+%22Texas+cotton+drought%22+OR+%22India+cotton%22+OR+%22China+cotton+imports%22+OR+%22ICE+cotton%22+OR+Cotlook&hl=en-US&gl=US&ceid=US:en", 3600),
]

# ============================================================
# Sources structurées (JSON APIs) — Phase 2.2
# GNews + NewsAPI : requêtes par thématique actif.
# Clés via env : GNEWS_API_KEY, NEWSAPI_KEY. Absent → skip propre.
# ============================================================

# Requêtes finance ciblées sur les 12 actifs (énergie / métaux / agri / indices / FX / macro)
STRUCTURED_QUERIES = [
    # Round 2 (audit requêtes 3 experts) : DAX retiré (hors périmètre), Q3 agri générique
    # redondante supprimée, gold/silver/copper dégroupés, + Nasdaq(IA/semi) + VIX(volatilité),
    # Or (achats banques centrales) et Argent (demande industrielle/solaire) enrichis,
    # Cacao (EUDR) et Blé (WASDE) complétés, EUR/USD resserré sur le différentiel Fed-BCE.
    "oil OR brent OR WTI OR OPEC OR crude inventories",
    "gold price OR central bank gold buying OR WGC OR PBoC gold OR real yields",          # Or
    "silver price OR silver industrial demand OR solar photovoltaic OR gold silver ratio",  # Argent
    # Round 3 : Fed et BCE DÉGROUPÉS (directions opposées sur EUR/USD, US vs EU)
    "Fed OR FOMC OR interest rate decision OR federal funds rate OR Powell speech",        # bloc US
    "ECB OR European Central Bank OR Eurozone inflation OR Lagarde speech OR ECB rate",    # bloc EU
    '"S&P 500" earnings OR corporate earnings beat OR EPS surprise OR earnings guidance OR market correction',  # S&P (driver-isé) — "S&P 500" quoté : le & non quoté cassait GNews (HTTP 400, doc gnews.io)
    "EUR USD OR ECB rate decision OR Fed ECB divergence OR dollar index",                  # EUR/USD resserré
    "coffee prices OR arabica OR robusta OR Brazil harvest OR frost Brazil OR drought Minas Gerais",  # Café + gel/sécheresse
    # Enrichi 16/06 (chantier sources OFFRE prospective) : ajout du récit d'offre
    # 2026-27 (El Niño, météo Afrique de l'Ouest, surveys de récolte/cherelles,
    # maladies black pod/swollen shoot, déficit ICCO). Capte le choc d'offre HAUSSIER
    # raté le 16/06. Additif : aucune source → critères offre n/a (zéro invention).
    'cocoa prices OR Ivory Coast OR Ghana cocoa OR cocoa grindings OR EUDR deforestation OR "cocoa harvest" OR "El Nino cocoa" OR "black pod" OR "swollen shoot" OR "ICCO deficit"',
    "wheat prices OR Black Sea grain OR Russia wheat OR US wheat crop OR WASDE OR Egypt GASC OR Australia wheat",  # Blé + demande importateur
    "copper prices OR LME copper OR Chile mine OR China copper demand",
    "CAC 40 OR SBF 120 OR LVMH OR TotalEnergies OR profit warning France OR résultats trimestriels OR France budget politics",  # + earnings mid-cap / profit warnings (dernier fix CAC, audit R3)
    "Nvidia OR semiconductor OR AI chips OR TSMC OR chip export controls OR earnings guidance OR data center capex",  # Nasdaq + pivot baissier
    # VIX : causes AMONT (war/escalation/...) en plus des symptômes → capter la peur AVANT le spike.
    # Fix 10/06 (audit DeepSeek) : la requête unique 9-termes renvoyait HTTP 400 sur GNews.
    # Fix 11/06 : la moitié « symptômes » restait en 400 malgré le split (la longueur n'était
    # donc pas la cause). Guillemets sur les expressions multi-mots et le terme à tiret
    # (« risk-off » : tiret nu ambigu pour le parseur GNews — syntaxe doc API). Non validable
    # en live sans GNEWS_API_KEY → vérifier source-health 15/15 au prochain run ; si encore
    # 400, retirer « risk-off » (le flux RSS dédié gnews_vix le couvre déjà, quoted).
    '"stock market volatility" OR VIX OR "risk-off" OR "market selloff"',  # VIX symptômes marché
    "war escalation OR sanctions OR bank failure OR sovereign default",  # VIX causes amont géopol/systémiques
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
    "investing_commodities": 0.9, "investing_metals": 0.9,
    "fed_press_all": 1.5, "fed_monetary": 1.5,
    "ecb_press": 1.5, "boe_news": 1.3, "boj_news": 1.3,
    "investing_economy": 0.9,
    # Actifs sous-couverts — Google News RSS ciblé (agrégateur, bruit modéré)
    "gnews_coffee": 0.8, "gnews_cocoa": 0.8, "gnews_cocoa_supply": 0.9, "gnews_wheat": 0.8,
    "gnews_copper": 0.8, "gnews_cac40": 0.8, "gnews_nasdaq": 0.8, "gnews_vix": 0.8,
    "gnews_ecb_policy": 0.8, "gnews_silver_industrial": 0.8, "gnews_gold_cb": 0.8,
    "gnews_usdjpy": 0.8, "gnews_sugar": 0.8, "gnews_cotton": 0.8,  # nouveaux actifs 2026-06-26
    # Sources structurées (agrégateurs API) — bruit élevé mais couverture large
    "gnews": 0.7, "newsapi": 0.7,
}


def source_weight(name: str) -> float:
    """Retourne le poids d'une source (DEFAULT si inconnue)."""
    return SOURCE_WEIGHTS.get(name, DEFAULT_SOURCE_WEIGHT)
