"""TradingApp v3 — Critères courants (incrément 5 — mapping étendu).

Produit `v3/data/criteres-courants.md` à partir de :
- Twelve Data (prix, séries → z-scores, RSI, spreads, ratios, alphas, mapping non-monotone)
- CFTC COT Legacy (Socrata jun7-fc8e, sans clé) → noncomm nets z-score 252w
- EIA API (clé requise) → crude stocks (WCESTUS1), Cushing (W_EPC0_SAX_YCUOK_MBBL)
- Open-Meteo (public) → anomalies précipitations 30/90j zones agri
- triggers_classifier (events-log + triggers-and-windows.yml) → triplets + calendrier

Red line : zéro invention. Source injoignable / clé absente / valeur non
disponible → critère OMIS (le scoring le marquera n/a, poids 0). Log WARNING
par source ratée + compteur de skip global.

Format de sortie pour scoring_analyste.normalise :
- zscore  → `valeur_normalisee` pré-calculée (z/zscore_div, capé)
- lineaire → `valeur` brute (le scoring applique centre/echelle/cap)
- triplet  → `valeur` ∈ {-1, 0, +1}
- gate     → `valeur: bool`
- mapping_non_monotone / composite → `valeur_normalisee` pré-calculée
"""

from __future__ import annotations

import json
import logging
import math
import os
import random
import statistics
import sys
import time
import threading
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import yaml

logger = logging.getLogger("criteres_calculator")

ROOT = Path(__file__).resolve().parents[1]
FICHES_DIR = ROOT / "config" / "fiches"
TRIGGERS_YML = ROOT / "config" / "triggers-and-windows.yml"
EVENTS_LOG = ROOT / "data" / "events-log.md"
CRITERES_OUT = ROOT / "data" / "criteres-courants.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import triggers_classifier as tc  # noqa: E402
import weighting as wg  # noqa: E402
import market_data as md  # noqa: E402 — module validé (symboles testés 2026-03)
import http_retry as _http_retry  # noqa: E402 — helper HTTP partagé (retry/backoff)

SKIP_COUNTER: Counter = Counter()
DEFAULT_TIMEOUT = 15  # seconds

# ---------------------------------------------------------------------------
# GATE C2 — Intégrité des critères quant (garde-fous P0, déterministes)
# ---------------------------------------------------------------------------
# Bornage des z-scores : tout |z| > Z_CLIP_MAX est clippé à ±Z_CLIP_MAX (3σ).
# Au-delà de Z_WARN_THRESHOLD on logge un WARNING AVANT clip (signal de donnée
# extrême — peut révéler une corruption en amont).
# Sortie n/a (None) sur : std=0, prix≤0, NaN/Inf, spike implausible.
# Ces critères passent en n/a → consommés par le gate de couverture S5 dans
# scoring_analyste (compute_coverage), qui rétrograde l'actif vers
# "⚠️ conf. faible" voire "🚫 insuffisant" si trop de critères tombent.
Z_CLIP_MAX: float = 3.0          # |z| max après bornage (3 sigmas)
Z_WARN_THRESHOLD: float = 2.5    # |z| déclenchant WARNING avant clip

# Anti-spike : variation journalière implausible (close_t / close_{t-1} - 1).
# Seuils par classe d'actif (constantes documentées) :
#   indices boursiers : un mouvement > 20% en une journée est invraisemblable
#     (vrais cas historiques : Black Monday 1987 = -22.6% ; sinon < 15%)
#   commodités (futures pétrole/métaux/agri) : > 50% = spike (rolls, données
#     corrompues) ; les vrais shocks (avril 2020 WTI négatif) sortent du modèle
#     z-score de toute façon.
#   FX majeurs : > 15% = spike (le SNB-CHF de 2015 a fait ~30% mais c'est un
#     cygne noir ; on coupe à 15% par défaut).
#   défaut : 30% pour les actifs non classés.
SPIKE_THRESHOLD_INDEX: float = 0.20
SPIKE_THRESHOLD_COMMODITY: float = 0.50
SPIKE_THRESHOLD_FX: float = 0.15
SPIKE_THRESHOLD_DEFAULT: float = 0.30


def _is_finite_number(x: Any) -> bool:
    """True si x est un nombre fini (pas None, NaN ni Inf)."""
    if x is None:
        return False
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v)


def _is_valid_price(x: Any) -> bool:
    """Prix valide = nombre fini strictement positif."""
    return _is_finite_number(x) and float(x) > 0.0


def _spike_threshold_for_symbol(symbol: str) -> float:
    """Seuil de variation journalière au-delà duquel on considère le point comme
    spike. Heuristique par classe d'actif (formats Yahoo)."""
    if not symbol:
        return SPIKE_THRESHOLD_DEFAULT
    s = symbol.upper()
    # Indices : préfixe ^ Yahoo
    if s.startswith("^"):
        return SPIKE_THRESHOLD_INDEX
    # Forex : suffixe =X
    if s.endswith("=X"):
        return SPIKE_THRESHOLD_FX
    # Commodities : suffixe =F (futures)
    if s.endswith("=F"):
        return SPIKE_THRESHOLD_COMMODITY
    return SPIKE_THRESHOLD_DEFAULT


def _filter_spikes(series: List[Tuple[datetime, float]], threshold: float,
                   *, label: str = "") -> List[Tuple[datetime, float]]:
    """Filtre les points dont la variation absolue vs la précédente dépasse `threshold`.

    Conserve le premier point. Logge un WARNING par spike détecté. Retourne la
    série filtrée (peut être plus courte). N'altère pas la liste d'origine.
    """
    if not series or len(series) < 2:
        return list(series) if series else []
    out: List[Tuple[datetime, float]] = [series[0]]
    prev = series[0][1]
    for dt, c in series[1:]:
        if not _is_valid_price(prev) or not _is_valid_price(c):
            # Donnée invalide → on saute le point + log (alimente Z_warn pas spike)
            SKIP_COUNTER[f"c2_invalid_price:{label or 'unknown'}"] += 1
            logger.warning("C2 prix invalide ignoré symbol=%s prev=%r curr=%r",
                           label, prev, c)
            continue
        if prev == 0:
            continue
        var = abs(c / prev - 1.0)
        if var > threshold:
            SKIP_COUNTER[f"c2_spike:{label or 'unknown'}"] += 1
            logger.warning("C2 donnée suspecte (spike %.1f%%) symbol=%s "
                           "prev=%.4f curr=%.4f seuil=%.1f%% — point ignoré",
                           var * 100.0, label, prev, c, threshold * 100.0)
            # On ignore le point spike (ne devient pas la nouvelle référence non plus)
            continue
        out.append((dt, c))
        prev = c
    return out


# ---------------------------------------------------------------------------
# HTTP helper (mockable en tests)
# ---------------------------------------------------------------------------

def _bucket_for_url(url: str) -> str:
    """Déduit le bucket de throttle/retry à partir de l'host de l'URL.

    Bucket distinct par source pour que CFTC, EIA et Open-Meteo aient des cadences
    indépendantes (une source rate-limitée n'en pénalise pas une autre). Dérivé de
    l'URL plutôt qu'en argument explicite → le contrat positionnel de
    `http_get_json` reste strictement inchangé (les mocks existants restent valides).
    """
    if "cftc.gov" in url:
        return "cftc"
    if "eia.gov" in url:
        return "eia"
    if "open-meteo.com" in url:
        return "openmeteo"
    return "http"


def http_get_json(url: str, params: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> Optional[Any]:
    """GET JSON résilient avec timeout. Retourne le JSON parsé, ou None si erreur.

    Wrapper mince autour de `http_retry.http_get_retry` (helper partagé) : route le
    GET via la logique retry/backoff (429/5xx + Retry-After + throttle par bucket)
    puis parse `.json()`. Le contrat historique est PRÉSERVÉ (même signature
    positionnelle, même type de retour JSON-ou-None) : les tests qui mockent
    `http_get_json` en entier restent valides, et CFTC/EIA/Open-Meteo encaissent
    désormais un 429/5xx avec retry au lieu de tomber n/a au 1er coup.

    Le bucket de throttle est déduit de l'URL (cftc/eia/openmeteo) pour que les
    sources ne se pénalisent pas mutuellement.
    """
    bucket = _bucket_for_url(url)
    resp = _http_retry.http_get_retry(
        url, params=params, timeout=timeout, bucket=bucket, label=bucket,
    )
    if resp is None:
        # Échec réseau / statut non-retriable / retries épuisés : déjà loggé par
        # le helper. Le caller (CFTC/EIA/Meteo) incrémente son SKIP_COUNTER sur None.
        return None
    try:
        return resp.json()
    except ValueError as e:
        logger.warning("HTTP GET %s : JSON invalide (HTTP 200) : %s", url, e)
        return None


# ---------------------------------------------------------------------------
# Twelve Data
# ---------------------------------------------------------------------------

TWELVE_BASE = "https://api.twelvedata.com"


def _twelve_key() -> Optional[str]:
    k = os.environ.get("TWELVE_DATA_API_KEY")
    return k or None


# NOTE refacto : YAHOO_TO_TWELVE supprimé. Le mapping Yahoo→Twelve est désormais
# géré par `market_data._TICKER_MAP` (table de vérité validée 2026-03 contre l'API
# réelle). Les fetchers ci-dessous (`fetch_twelve_series`, `fetch_twelve_price`,
# `fetch_twelve_rsi`) acceptent maintenant des tickers FORMAT YAHOO (BZ=F, ^GSPC,
# EURUSD=X, MC.PA, ...) et délèguent à `market_data`, qui fait :
#   - la traduction Yahoo → Twelve via _TICKER_MAP (BZ=F → CO1+type=commodities,
#     ^GSPC → blacklist → yfinance, EUR=X → EUR/USD, ...)
#   - le fallback yfinance pour les indices et tout ticker blacklisté
#   - rate limiting + cache + validation de prix
# Alias backward-compat : un dict vide pass-through pour les tests legacy qui
# référencent `cc.YAHOO_TO_TWELVE` — toute lookup retourne la clé inchangée.

class _PassthroughMap(dict):
    """Dict qui retourne la clé elle-même si absente (pour compat tests legacy)."""
    def get(self, key, default=None):  # type: ignore[override]
        if key in self:
            return self[key]
        return key if default is None else default

    def __contains__(self, key) -> bool:  # type: ignore[override]
        # Les tests legacy font `assert "BZ=F" in YAHOO_TO_TWELVE` → on accepte
        # tout ticker Yahoo connu de market_data (présent dans _TICKER_MAP ou
        # blacklisté = géré).
        try:
            return (
                key in md._TICKER_MAP
                or key in md._td_blacklist
                or key.endswith(".PA")
            )
        except Exception:  # noqa: BLE001
            return False


YAHOO_TO_TWELVE = _PassthroughMap()


def fetch_twelve_series(symbol: str, *, interval: str = "1day", outputsize: int = 60) -> Optional[List[Tuple[datetime, float]]]:
    """Retourne [(datetime_utc, close)] triée oldest→newest. None si indisponible.

    `symbol` est un ticker FORMAT YAHOO (BZ=F, ^GSPC, EURUSD=X, MC.PA, ...).
    Délègue à market_data.fetch_history qui gère la traduction Twelve + fallback yfinance.
    """
    if not _twelve_key() and not _yfinance_available():
        SKIP_COUNTER["twelve_no_key"] += 1
        logger.warning("TWELVE_DATA_API_KEY manquante ET yfinance indispo — symbol=%s skip", symbol)
        return None
    try:
        df = md.fetch_history(symbol, period_days=outputsize, interval=interval)
    except Exception as e:  # noqa: BLE001
        SKIP_COUNTER[f"twelve_dead:{symbol}"] += 1
        logger.warning("market_data.fetch_history KO symbol=%s : %s", symbol, e)
        return None
    if df is None or len(df) == 0:
        SKIP_COUNTER[f"twelve_empty:{symbol}"] += 1
        return None
    out: List[Tuple[datetime, float]] = []
    for ts_idx, close_val in zip(df.index, df["Close"]):
        try:
            # Index peut être Timestamp (avec ou sans tz) ou datetime
            dt_py = ts_idx.to_pydatetime() if hasattr(ts_idx, "to_pydatetime") else ts_idx
            if dt_py.tzinfo is None:
                dt_py = dt_py.replace(tzinfo=timezone.utc)
            close = float(close_val)
        except (AttributeError, ValueError, TypeError):
            continue
        # GATE C2 — rejette prix ≤0 / NaN / Inf au point de capture (filet ultime
        # avant l'usage). Les prix de marché valides sont > 0.
        if not _is_valid_price(close):
            SKIP_COUNTER[f"c2_invalid_price:{symbol}"] += 1
            logger.warning("C2 prix invalide ignoré symbol=%s ts=%s value=%r",
                           symbol, dt_py, close_val)
            continue
        out.append((dt_py, close))
    if not out:
        SKIP_COUNTER[f"twelve_parse:{symbol}"] += 1
        return None
    out.sort(key=lambda t: t[0])
    # GATE C2 — filtre les spikes (variations journalières implausibles) selon la
    # classe d'actif. Ne casse pas la chaîne : le critère dérivé sera n/a si
    # trop de points sautent (compute_zscore_normalisee → std=0 ou len<2 → None).
    out = _filter_spikes(out, _spike_threshold_for_symbol(symbol), label=symbol)
    if not out:
        return None
    return out


def _yfinance_available() -> bool:
    """True si yfinance est importable (fallback pour les indices)."""
    try:
        import yfinance  # noqa: F401
        return True
    except ImportError:
        return False


def fetch_twelve_price(symbol: str) -> Optional[float]:
    """Dernier prix pour un ticker FORMAT YAHOO (BZ=F, ^GSPC, EURUSD=X, ...).

    Délègue à market_data.fetch_price qui :
      - traduit Yahoo → Twelve via _TICKER_MAP (ex: BZ=F → CO1+type=commodities)
      - bascule en fallback yfinance pour les tickers blacklistés (indices ^...)
      - applique cache + rate limit
    """
    if not _twelve_key() and not _yfinance_available():
        SKIP_COUNTER["twelve_no_key"] += 1
        return None
    try:
        price = md.fetch_price(symbol)
    except Exception as e:  # noqa: BLE001
        SKIP_COUNTER[f"twelve_dead:{symbol}"] += 1
        logger.warning("market_data.fetch_price KO symbol=%s : %s", symbol, e)
        return None
    if price is None:
        SKIP_COUNTER[f"twelve_empty:{symbol}"] += 1
    return price


def _compute_rsi(closes: List[float], period: int = 14) -> Optional[float]:
    """RSI 14 standard (Wilder) calculé localement à partir des closes oldest→newest.

    Évite l'endpoint Twelve /rsi (1 crédit par appel) qui n'est plus nécessaire
    puisqu'on récupère déjà les séries OHLCV via market_data."""
    if len(closes) < period + 1:
        return None
    gains: List[float] = []
    losses: List[float] = []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    # Wilder smoothing initial = SMA(period)
    avg_gain = statistics.fmean(gains[:period])
    avg_loss = statistics.fmean(losses[:period])
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def fetch_twelve_rsi(symbol: str, *, period: int = 14, outputsize: int = 5) -> Optional[float]:
    """Dernier RSI calculé localement à partir d'une série market_data (yahoo ticker)."""
    series = fetch_twelve_series(symbol, outputsize=max(period * 3 + outputsize, 50))
    if not series:
        SKIP_COUNTER[f"twelve_rsi_empty:{symbol}"] += 1
        return None
    closes = [c for _, c in series]
    rsi = _compute_rsi(closes, period=period)
    if rsi is None:
        SKIP_COUNTER[f"twelve_rsi_short:{symbol}"] += 1
    return rsi


# ---------------------------------------------------------------------------
# CFTC COT Legacy (Socrata jun7-fc8e) — noncomm_positions_*
# ---------------------------------------------------------------------------

CFTC_BASE = "https://publicreporting.cftc.gov/resource/jun7-fc8e.json"

# Mapping cle_courante → market_and_exchange_names (validé contre dataset live)
CFTC_MARKETS = {
    "cftc_cot_crude_nets":  "CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE",
    "cftc_cot_nets":        "GOLD - COMMODITY EXCHANGE INC.",          # or
    "cftc_cot_copper_nets": "COPPER- #1 - COMMODITY EXCHANGE INC.",
    "cftc_cot_silver":      "SILVER - COMMODITY EXCHANGE INC.",
    "cftc_cot_wheat":       "WHEAT-SRW - CHICAGO BOARD OF TRADE",
    "cftc_cot_cocoa":       "COCOA - ICE FUTURES U.S.",
    "cftc_cot_coffee":      "COFFEE C - ICE FUTURES U.S.",
    "cftc_cot_eur_nets":    "EURO FX - CHICAGO MERCANTILE EXCHANGE",
    "cftc_cot_vix_nets":    "VIX FUTURES - CBOE FUTURES EXCHANGE",
}


def fetch_cftc_managed_money_nets(market: str, *, weeks: int = 260) -> Optional[List[float]]:
    """Retourne la série des nets non-commercial (long - short) sur N semaines (oldest→newest).

    Note : le dataset Socrata jun7-fc8e est le Legacy COT — il expose noncomm_positions_*
    et non m_money_positions_*. On utilise donc le noncomm net comme proxy "spéculateurs".
    """
    params = {
        "$select": "report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all",
        "$where": f"market_and_exchange_names='{market}'",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": weeks,
    }
    data = http_get_json(CFTC_BASE, params=params)
    if not isinstance(data, list) or not data:
        SKIP_COUNTER[f"cftc_dead:{market}"] += 1
        return None
    nets: List[Tuple[datetime, float]] = []
    for row in data:
        try:
            dt_str = row["report_date_as_yyyy_mm_dd"].replace("Z", "")
            dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
            longp = float(row["noncomm_positions_long_all"])
            shortp = float(row["noncomm_positions_short_all"])
        except (KeyError, ValueError, TypeError):
            continue
        nets.append((dt, longp - shortp))
    if not nets:
        SKIP_COUNTER[f"cftc_parse:{market}"] += 1
        return None
    nets.sort(key=lambda t: t[0])
    return [n for _, n in nets]


# ---------------------------------------------------------------------------
# EIA
# ---------------------------------------------------------------------------

EIA_BASE = "https://api.eia.gov/v2"

# Mapping critère → série EIA (path v2, frequency, series ID si applicable)
EIA_SERIES = {
    # Crude oil stocks excl SPR (weekly, M-barils)
    "eia_crude_surprise":  ("petroleum/stoc/wstk/data/", "weekly", "WCESTUS1"),
    "api_weekly_surprise": ("petroleum/stoc/wstk/data/", "weekly", "WCESTUS1"),  # proxy : pas d'API officielle gratuite
    # Cushing OK ending stocks (weekly)
    "cushing_stocks":      ("petroleum/stoc/wstk/data/", "weekly", "W_EPC0_SAX_YCUOK_MBBL"),
}


def _eia_key() -> Optional[str]:
    k = os.environ.get("EIA_API_KEY")
    return k or None


def fetch_eia_series(path: str, *, frequency: str = "weekly", series_id: Optional[str] = None,
                     length: int = 60) -> Optional[List[float]]:
    """Récupère N derniers points d'une série EIA. Path = endpoint v2 data (ex: 'petroleum/stoc/wstk/data/').
    Retourne valeurs oldest→newest. None si KO ou clé manquante."""
    key = _eia_key()
    if not key:
        SKIP_COUNTER["eia_no_key"] += 1
        logger.warning("EIA_API_KEY manquante — path=%s skip", path)
        return None
    params: Dict[str, Any] = {
        "api_key": key,
        "frequency": frequency,
        "data[0]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": length,
    }
    if series_id:
        params["facets[series][]"] = series_id
    data = http_get_json(f"{EIA_BASE}/{path}", params=params)
    if not isinstance(data, dict):
        SKIP_COUNTER[f"eia_dead:{path}:{series_id}"] += 1
        return None
    resp = data.get("response", {})
    rows = resp.get("data") if isinstance(resp, dict) else None
    if not isinstance(rows, list) or not rows:
        SKIP_COUNTER[f"eia_empty:{path}:{series_id}"] += 1
        return None
    vals: List[Tuple[str, float]] = []
    for row in rows:
        try:
            period = row.get("period")
            val = float(row.get("value"))
        except (TypeError, ValueError):
            continue
        if period is None:
            continue
        vals.append((period, val))
    if not vals:
        return None
    vals.sort(key=lambda t: t[0])
    return [v for _, v in vals]


# ---------------------------------------------------------------------------
# FRED (Federal Reserve Economic Data — St. Louis Fed)
# ---------------------------------------------------------------------------

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# Mapping cle_courante → (series_id, mode) où mode ∈ {"zscore", "linear", "spread"}
# Pour les spreads US-DE : tuple (series_us, series_de). Si une série DE n'existe pas
# côté FRED → on n'inclut PAS le critère ici (skip propre dans le dispatch).
#
# Séries validées :
#   DFII10        : 10-Year Treasury Inflation-Indexed (TIPS) — taux réel 10a US — daily
#   BAMLH0A0HYM2  : ICE BofA US High Yield Index Option-Adjusted Spread — daily
#   DGS10         : 10-Year Treasury Constant Maturity Rate — daily
#   DGS2          : 2-Year Treasury Constant Maturity Rate — daily
#   IRLTLT01DEM156N : Germany Long-Term Gov Bond Yield (mensuel)
#   DTWEXBGS      : Trade-Weighted USD Index — Broad — daily (fallback DXY)
FRED_SERIES_SIMPLE = {
    "taux_10y_us_reels_tips": "DFII10",       # Or, Argent, Nasdaq — z-score
    "hy_credit_spread":       "BAMLH0A0HYM2", # S&P 500 — z-score
}
# Différentiels US - DE (spread = série_US - série_DE alignée)
FRED_SPREADS = {
    "differentiel_taux_10y_us_bund": ("DGS10", "IRLTLT01DEM156N"),
    # 2Y DE n'est pas dispo en série quotidienne fiable côté FRED gratuit → skip propre
    # ("differentiel_taux_2y_us_de" est laissé volontairement non mappé)
}


def _fred_key() -> Optional[str]:
    k = os.environ.get("FRED_API_KEY")
    return k or None


# ── Résilience FRED : retry backoff + throttle inter-requêtes ──────────────
#
# Contexte (run 2026-06-02) : les séries FRED sont appelées en rafale dans un
# même run de cycle-decision. Sans espacement, l'API FRED renvoie 429 Too Many
# Requests → DFII10 + le spread DGS10-IRLTLT01DEM156N tombaient en n/a, faisant
# basculer 42 % du bulletin en INSUFFISANT (gate de couverture S5).
#
# Philosophie alignée sur le rate-limiter Twelve Data (cf. market_data.py
# `_acquire_rate_limit` : « attend au lieu de rejeter ») : on étale les requêtes
# au lieu de les perdre. FRED gratuit tolère ~120 req/min ; un espacement de
# ~0.6 s/req est une marge sûre tout en restant rapide sur la dizaine de séries
# d'un run.
#
# NOTE refacto (2026-06-02) : la logique backoff + Retry-After est désormais
# factorisée dans `http_retry.py` (helper partagé), réutilisée par les fetchers
# news (RSS/GNews/NewsAPI) qui subissent le même 429. _fred_get_json conserve son
# throttle global dédié (cadence FRED spécifique) mais délègue backoff/Retry-After
# au helper partagé via _fred_backoff_delay / _parse_retry_after.

FRED_MIN_INTERVAL = float(os.environ.get("FRED_MIN_INTERVAL", "0.6"))  # secondes entre requêtes
FRED_MAX_RETRIES = int(os.environ.get("FRED_MAX_RETRIES", "3"))
FRED_BACKOFF_BASE = float(os.environ.get("FRED_BACKOFF_BASE", "2.0"))  # 2s → 4s → 8s
FRED_RETRY_STATUS = {429, 500, 502, 503, 504}

_fred_throttle_lock = threading.Lock()
_fred_last_request_ts = 0.0


def _fred_throttle() -> None:
    """Espacement minimal entre deux requêtes FRED dans un même run.

    Bloque (sleep) le temps nécessaire pour respecter FRED_MIN_INTERVAL depuis
    la dernière requête. Thread-safe ; le sleep est fait sous lock (les requêtes
    FRED sont séquentielles dans le run, pas de contention significative).
    """
    global _fred_last_request_ts
    with _fred_throttle_lock:
        now = time.monotonic()
        wait = FRED_MIN_INTERVAL - (now - _fred_last_request_ts)
        if wait > 0:
            time.sleep(wait)
        _fred_last_request_ts = time.monotonic()


def _fred_get_json(series_id: str, params: dict, *, timeout: int = DEFAULT_TIMEOUT) -> Optional[Any]:
    """GET JSON FRED résilient : throttle + retry backoff sur 429/5xx.

    - Espacement minimal entre requêtes (anti-rafale) via _fred_throttle().
    - Retry exponentiel (2s/4s/8s + jitter) sur HTTP 429 et 5xx, en respectant
      l'en-tête Retry-After si présent.
    - Retourne le JSON parsé (200) ou None après épuisement des retries / erreur.
      Le caller incrémente fred_dead UNIQUEMENT sur None (donc après les retries).
    - Zéro régression sur 200 : succès au 1er essai → comportement identique.
    """
    try:
        import requests  # lazy import (testable)
    except ImportError:
        logger.warning("requests non installé — HTTP FRED désactivé")
        return None

    last_err: Optional[str] = None
    for attempt in range(1, FRED_MAX_RETRIES + 1):
        _fred_throttle()
        try:
            r = requests.get(FRED_BASE, params=params, timeout=timeout)
        except Exception as e:  # noqa: BLE001 — erreur réseau/timeout
            last_err = str(e)
            logger.warning(
                "FRED %s : erreur réseau (tentative %d/%d) : %s",
                series_id, attempt, FRED_MAX_RETRIES, e,
            )
            if attempt < FRED_MAX_RETRIES:
                time.sleep(_fred_backoff_delay(attempt, None))
            continue

        if r.status_code == 200:
            try:
                return r.json()
            except ValueError as e:
                logger.warning("FRED %s : JSON invalide (HTTP 200) : %s", series_id, e)
                return None

        if r.status_code in FRED_RETRY_STATUS and attempt < FRED_MAX_RETRIES:
            retry_after = _parse_retry_after(r.headers.get("Retry-After"))
            delay = _fred_backoff_delay(attempt, retry_after)
            logger.warning(
                "FRED %s : HTTP %d (tentative %d/%d) → retry dans %.1fs",
                series_id, r.status_code, attempt, FRED_MAX_RETRIES, delay,
            )
            time.sleep(delay)
            last_err = f"HTTP {r.status_code}"
            continue

        # Statut non-retriable (4xx ≠ 429) OU dernier essai épuisé
        last_err = f"HTTP {r.status_code}"
        break

    logger.error(
        "FRED %s : échec après %d tentative(s) — %s",
        series_id, FRED_MAX_RETRIES, last_err or "raison inconnue",
    )
    return None


def _fred_backoff_delay(attempt: int, retry_after: Optional[float]) -> float:
    """Délai avant retry FRED : délègue au helper partagé (backoff_base FRED).

    Conserve la signature historique (utilisée par les tests FRED) ; la logique
    est désormais factorisée dans http_retry.backoff_delay.
    """
    return _http_retry.backoff_delay(attempt, retry_after, backoff_base=FRED_BACKOFF_BASE)


def _parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Parse l'en-tête Retry-After (secondes uniquement). Délègue au helper partagé."""
    return _http_retry.parse_retry_after(value)


def fetch_fred_series(series_id: str, *, n: int = 252) -> Optional[List[float]]:
    """Retourne les N dernières observations valides d'une série FRED, oldest→newest.

    Filtre les valeurs manquantes ('.' chez FRED). None si clé absente ou erreur HTTP.
    """
    key = _fred_key()
    if not key:
        SKIP_COUNTER["fred_no_key"] += 1
        logger.warning("FRED_API_KEY manquante — series_id=%s skip", series_id)
        return None
    params = {
        "series_id": series_id,
        "file_type": "json",
        "sort_order": "desc",
        "limit": n,
        "api_key": key,
    }
    data = _fred_get_json(series_id, params)
    if not isinstance(data, dict):
        SKIP_COUNTER[f"fred_dead:{series_id}"] += 1
        return None
    obs = data.get("observations")
    if not isinstance(obs, list) or not obs:
        SKIP_COUNTER[f"fred_empty:{series_id}"] += 1
        return None
    parsed: List[Tuple[str, float]] = []
    for row in obs:
        try:
            d = row.get("date")
            v = row.get("value")
        except AttributeError:
            continue
        if not d or v in (None, "", "."):
            continue
        try:
            parsed.append((d, float(v)))
        except (TypeError, ValueError):
            continue
    if not parsed:
        SKIP_COUNTER[f"fred_parse:{series_id}"] += 1
        return None
    parsed.sort(key=lambda t: t[0])  # oldest → newest
    return [v for _, v in parsed]


def fetch_fred_spread(series_us: str, series_de: str, *, n: int = 252) -> Optional[List[float]]:
    """Spread US - DE aligné par date d'observation (intersection). oldest→newest."""
    key = _fred_key()
    if not key:
        SKIP_COUNTER["fred_no_key"] += 1
        return None
    params_base = {"file_type": "json", "sort_order": "desc", "limit": n, "api_key": key}
    a = _fred_get_json(series_us, dict(params_base, series_id=series_us))
    b = _fred_get_json(series_de, dict(params_base, series_id=series_de))
    if not isinstance(a, dict) or not isinstance(b, dict):
        SKIP_COUNTER[f"fred_spread_dead:{series_us}-{series_de}"] += 1
        return None
    def _parse(obj: dict) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for r in obj.get("observations", []) or []:
            v = r.get("value")
            d = r.get("date")
            if not d or v in (None, "", "."):
                continue
            try:
                out[d] = float(v)
            except (TypeError, ValueError):
                continue
        return out
    map_a = _parse(a)
    map_b = _parse(b)

    # Alignement par forward-fill : la série DE (ex IRLTLT01DEM156N) est MENSUELLE
    # (un point en début de mois), la série US (DGS10) est QUOTIDIENNE. Une simple
    # intersection de dates ne garde qu'une poignée de points (les jours où les
    # deux séries coïncident) → spread "thin" → critère perdu. On reporte donc la
    # dernière valeur DE connue sur chaque date US (last-observation-carried-forward),
    # ce qui est la convention standard pour mélanger une série basse fréquence et
    # une série haute fréquence.
    if not map_a or not map_b:
        SKIP_COUNTER[f"fred_spread_thin:{series_us}-{series_de}"] += 1
        return None

    de_dates = sorted(map_b)  # dates DE croissantes (oldest→newest)
    us_dates = sorted(map_a)  # dates US croissantes
    spread: List[float] = []
    j = 0  # curseur sur de_dates : dernière valeur DE connue ≤ date US courante
    last_de: Optional[float] = None
    for d in us_dates:
        while j < len(de_dates) and de_dates[j] <= d:
            last_de = map_b[de_dates[j]]
            j += 1
        if last_de is None:
            # Date US antérieure au 1er point DE disponible → pas de valeur à
            # reporter, on ignore ce point (pas de bruit).
            continue
        spread.append(map_a[d] - last_de)

    # Garde-fou : si même après forward-fill on n'a pas assez de points (séries
    # quasi vides ou totalement désynchronisées), n/a propre.
    if len(spread) < 10:
        SKIP_COUNTER[f"fred_spread_thin:{series_us}-{series_de}"] += 1
        return None
    return spread


# ---------------------------------------------------------------------------
# CBOE (CSV public — sans clé)
# ---------------------------------------------------------------------------

CBOE_BASE = "https://cdn.cboe.com/api/global/us_indices/daily_prices"

# Mapping cle_courante → identifiant CBOE (utilisé pour <IDX>_History.csv)
# VIX, VIX3M, SKEW, VVIX exposés publiquement en CSV daily sans authentification.
CBOE_HISTORY_INDEX = {
    "niveau_vix_absolu":          "VIX",
    "vix_risk_off_proxy":         "VIX",
    "skew_index_cboe":            "SKEW",
    "vvix":                       "VVIX",
}
# Term structure : ratio VIX / VIX3M (centré autour de ~0.95 en marché normal,
# > 1 = backwardation = stress)
CBOE_TERM_STRUCTURE = ("VIX", "VIX3M")


def http_get_text(url: str, *, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """GET texte (CSV CBOE). None si erreur."""
    try:
        import requests  # lazy
    except ImportError:
        return None
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:  # noqa: BLE001
        logger.warning("HTTP GET %s : %s", url, e)
        return None


def _parse_cboe_csv(text: str) -> List[Tuple[str, float]]:
    """Parse CSV CBOE. Deux formats existent :
    - VIX/VIX3M : 'DATE,OPEN,HIGH,LOW,CLOSE' → on prend CLOSE.
    - SKEW/VVIX : 'DATE,<INDEX>' (valeur unique) → on prend la dernière colonne numérique.
    Retourne [(date, valeur)] oldest→newest."""
    out: List[Tuple[str, float]] = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return out
    # Trouver le header (ligne contenant 'date'). CBOE met parfois un préambule.
    header_idx = None
    for i, ln in enumerate(lines[:20]):
        if "date" in ln.lower():
            header_idx = i
            break
    if header_idx is None:
        return out
    header = [h.strip().lower() for h in lines[header_idx].split(",")]
    try:
        i_date = header.index("date")
    except ValueError:
        return out
    # Colonne valeur : 'close' si présente (VIX/VIX3M), sinon dernière colonne (SKEW/VVIX).
    i_val = header.index("close") if "close" in header else len(header) - 1
    for ln in lines[header_idx + 1:]:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) <= max(i_date, i_val):
            continue
        d = parts[i_date]
        try:
            c = float(parts[i_val])
        except (TypeError, ValueError):
            continue
        if not d:
            continue
        out.append((d, c))
    out.sort(key=lambda t: t[0])
    return out


def fetch_cboe_history(index: str) -> Optional[List[Tuple[str, float]]]:
    """Retourne [(date_str, close)] oldest→newest depuis le CSV public CBOE.
    None si HTTP KO ou parse vide."""
    url = f"{CBOE_BASE}/{index}_History.csv"
    text = http_get_text(url)
    if not text:
        SKIP_COUNTER[f"cboe_dead:{index}"] += 1
        return None
    parsed = _parse_cboe_csv(text)
    if not parsed:
        SKIP_COUNTER[f"cboe_parse:{index}"] += 1
        return None
    return parsed


# ---------------------------------------------------------------------------
# Open-Meteo (anomalies météo)
# ---------------------------------------------------------------------------

OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"

# Mapping cle_courante → (lat, lon, days_window)
# Coordonnées validées contre brief P3 : Minas Gerais (-19.9/-43.9 — Belo Horizonte),
# Vietnam Central Highlands (12.7/108.1 — Buon Ma Thuot), Côte d'Ivoire/Ghana barycentre
# bassin cacao (~6.8/-5.3 entre Daloa CI et Kumasi GH), US Plains (39/-98 — center Kansas),
# Australie wheatbelt (-33/147 — NSW/VIC bordure).
METEO_CRITERIA = {
    "meteo_ci_ghana_precip_30j":    (6.8, -5.3, 30),    # CI/Ghana — cacao
    "meteo_vietnam_robusta":        (12.7, 108.1, 60),   # Central Highlands — café robusta
    "meteo_australie_dryland":      (-33.0, 147.0, 60),  # NSW/VIC wheatbelt — blé
    "meteo_bresil_minas_gerais":    (-19.9, -43.9, 60),  # Minas Gerais — café arabica
    "noaa_drought_midwest_plains":  (39.0, -98.0, 60),   # US Plains (KS) — blé HRW/SRW
}


def fetch_open_meteo_anomaly(lat: float, lon: float, *, days: int = 90) -> Optional[float]:
    """Anomalie z-score précipitations sur `days` derniers jours vs climato 5 ans.
    Retourne le z brut (avant cap)."""
    today = date.today()
    end = today - timedelta(days=1)
    start = end - timedelta(days=days)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "precipitation_sum",
        "timezone": "UTC",
    }
    data = http_get_json(OPEN_METEO_ARCHIVE, params=params)
    if not isinstance(data, dict):
        SKIP_COUNTER[f"meteo_dead:{lat},{lon}"] += 1
        return None
    daily = data.get("daily", {})
    series = daily.get("precipitation_sum") if isinstance(daily, dict) else None
    if not isinstance(series, list) or len(series) < 10:
        SKIP_COUNTER[f"meteo_empty:{lat},{lon}"] += 1
        return None
    try:
        clean = [float(x) for x in series if x is not None]
    except (TypeError, ValueError):
        return None
    if len(clean) < 10:
        return None
    clim_start = end - timedelta(days=365 * 5)
    clim_end = end - timedelta(days=days)
    params2 = dict(params)
    params2["start_date"] = clim_start.isoformat()
    params2["end_date"] = clim_end.isoformat()
    data2 = http_get_json(OPEN_METEO_ARCHIVE, params=params2)
    if not isinstance(data2, dict):
        SKIP_COUNTER[f"meteo_clim_dead:{lat},{lon}"] += 1
        return None
    clim_series = data2.get("daily", {}).get("precipitation_sum") if isinstance(data2.get("daily"), dict) else None
    if not isinstance(clim_series, list) or len(clim_series) < 30:
        return None
    try:
        clim_clean = [float(x) for x in clim_series if x is not None]
    except (TypeError, ValueError):
        return None
    if len(clim_clean) < 30:
        return None
    recent_mean = statistics.fmean(clean)
    clim_mean = statistics.fmean(clim_clean)
    clim_std = statistics.pstdev(clim_clean)
    if clim_std == 0:
        return None
    return (recent_mean - clim_mean) / clim_std


# ---------------------------------------------------------------------------
# Z-score utility
# ---------------------------------------------------------------------------

def compute_zscore_normalisee(value: float, history: List[float], *, zscore_div: float,
                              cap: float, label: str = "") -> Optional[float]:
    """Calcule (z / zscore_div) capé. history = série de référence (incluant ou non value).

    GATE C2 (garde-fous) :
    - NaN/Inf/None dans value ou history → None (n/a).
    - std == 0 (série constante) → None (n/a, pas de division par zéro).
    - |z| > Z_WARN_THRESHOLD → WARNING avant clip.
    - z clippé à ±Z_CLIP_MAX (bornage hard 3σ) AVANT la division par zscore_div.
    """
    if not history or len(history) < 2:
        return None
    if not _is_finite_number(value):
        SKIP_COUNTER[f"c2_value_not_finite:{label or 'unknown'}"] += 1
        logger.warning("C2 value non-finie ignorée label=%s value=%r", label, value)
        return None
    # Filtre history : tous doivent être finis. Sinon n/a (rejette série corrompue).
    try:
        clean_hist = [float(x) for x in history if _is_finite_number(x)]
    except (TypeError, ValueError):
        return None
    if len(clean_hist) < 2:
        return None
    mean = statistics.fmean(clean_hist)
    std = statistics.pstdev(clean_hist)
    if std == 0:
        SKIP_COUNTER[f"c2_std_zero:{label or 'unknown'}"] += 1
        logger.warning("C2 série constante (std=0) label=%s n=%d → n/a", label, len(clean_hist))
        return None
    z = (float(value) - mean) / std
    if not math.isfinite(z):
        # Sécurité ceinture-bretelle (std très petit + grande valeur → overflow rare)
        SKIP_COUNTER[f"c2_z_not_finite:{label or 'unknown'}"] += 1
        return None
    if abs(z) > Z_WARN_THRESHOLD:
        logger.warning("C2 z-score extrême label=%s z=%.3f (clip à ±%.1f)",
                       label, z, Z_CLIP_MAX)
    # Clip dur 3σ AVANT division par zscore_div (séparation des préoccupations :
    # le clip C2 borne le z brut, le cap fiche borne la normalisée finale).
    z_clipped = max(-Z_CLIP_MAX, min(Z_CLIP_MAX, z))
    norm = z_clipped / zscore_div
    return max(-cap, min(cap, norm))


def zscore_from_series(series: List[float], *, zscore_div: float, cap: float,
                       label: str = "") -> Optional[Tuple[float, float]]:
    """Helper : retourne (valeur=dernier point, valeur_normalisee) à partir d'une série brute.

    GATE C2 : si le dernier point n'est pas un nombre fini → None (n/a).
    """
    if not series or len(series) < 2:
        return None
    value = series[-1]
    if not _is_finite_number(value):
        SKIP_COUNTER[f"c2_last_not_finite:{label or 'unknown'}"] += 1
        return None
    norm = compute_zscore_normalisee(value, series, zscore_div=zscore_div, cap=cap, label=label)
    if norm is None:
        return None
    return float(value), norm


# ---------------------------------------------------------------------------
# Mappings cle_courante → fetcher Twelve Data
# ---------------------------------------------------------------------------

# Symboles FORMAT YAHOO par cle_courante (post-refacto market_data).
#
# La traduction Yahoo → Twelve / yfinance se fait dans market_data._TICKER_MAP
# (validé 2026-03 contre l'API réelle). Avantages :
#   - Indices ^GSPC, ^IXIC, ^FCHI, ^VIX, ^RUT : blacklist Twelve → fallback
#     yfinance automatique (plus de "n/a" dû au format faux SPX/IXIC).
#   - Commodities futures BZ=F, CL=F, HG=F, ZW=F, KC=F, CC=F : symbole Twelve
#     correct (CO1, CL1, HG1, W_1, KC1, CC1) + type=commodities pour éviter
#     les collisions avec stocks (HG1=Homag, SB1=Smartbroker, etc.).
#   - Métaux GC=F, SI=F : forex spot XAU/USD, XAG/USD.
#   - Forex EURUSD=X / EUR=X : EUR/USD.
#   - DXY : DX-Y.NYB (Yahoo) → blacklist Twelve → yfinance.
#
# Si market_data renvoie None (clé absente, ticker inconnu, fallback yf KO),
# le critère est OMIS proprement (n/a).
TWELVE_SYMBOLS = {
    # --- Trend / risk-off ---
    "dxy_trend_20j":         "DX-Y.NYB",     # DXY US Dollar Index (yfinance natif)
    "vix_risk_off_proxy":    "^VIX",
    "niveau_vix_absolu":     "^VIX",
    "vix_regime":            "^VIX",         # mapping non-monotone
    "vxn_regime":            "^VXN",         # yfinance (Nasdaq vol index)
    "v2x_regime":            "^STOXX50EVOL", # placeholder — peut nécessiter ETF proxy
    "vvix":                  "^VVIX",
    "skew_index_cboe":       "^SKEW",
    "sox_trend_5j":          "SOXX",         # ETF iShares Semicond
    # --- Term structure VIX ---
    "term_structure_vix_vix3m": ("^VIX3M", "^VIX"),
    # --- Taux ---
    "taux_10y_us_reels_tips":   "TIP",       # ETF proxy (TIPS bonds)
    "taux_10y_us_delta_5j":     "^TNX",      # 10Y Treasury yield (yfinance)
    "differentiel_taux_2y_us_de":   ("^IRX", "^IRX"),   # placeholder (DE 2Y indispo)
    "differentiel_taux_10y_us_bund": ("^TNX", "^TNX"),  # placeholder (DE 10Y indispo)
    # --- Credit / stress ---
    "hy_credit_spread":      "HYG",          # ETF HY proxy
    "spread_oat_bund_10y":   ("HYG", "HYG"), # placeholder (souverains non dispo)
    "spread_oat_bund_stress_ez": ("HYG", "HYG"),
    # --- FX (spot format Yahoo) ---
    "usd_brl":               "USDBRL=X",
    "usd_jpy_proxy_risk":    "USDJPY=X",
    "usd_cfa_usd_cedi":      ("USDXOF=X", "USDGHS=X"),
    # --- Spreads commodities (futures Yahoo natifs) ---
    "spread_brent_wti":      ("BZ=F", "CL=F"),
    "spread_arabica_robusta":("KC=F", "KC=F"),   # robusta non listé → même symbole (placeholder)
    "spread_ny_london":      ("CC=F", "CC=F"),   # cacao Londres non listé
    "spread_nasdaq_russell2000": ("^IXIC", "^RUT"),
    # --- Ratios ---
    "ratio_gold_silver":     ("GC=F", "SI=F"),
    "ratio_cuivre_or":       ("HG=F", "GC=F"),
    # --- Alpha (perf relative 5j) ---
    "alpha_argent_vs_or_5j": ("SI=F", "GC=F"),
    "alpha_cac_vs_sp_5j":    ("^FCHI", "^GSPC"),
    # --- RSI (calculé localement via market_data + _compute_rsi) ---
    "rsi_14j_gspc":          ("RSI", "^GSPC"),
    "rsi_14j_ixic":          ("RSI", "^IXIC"),
    "rsi_14j_fchi":          ("RSI", "^FCHI"),
    # --- Trend perf 5j ---
    "mouvement_or_5j":       "GC=F",
    # --- Term structure brent (front + M2 indispo plan Grow → n/a explicite) ---
    "brent_term_structure_m1m2": ("BZ=F", "BZ=F"),
    # --- Flux ETF (proxy : variation de prix 5j) ---
    "flux_etf_or_5j":        "GLD",
    "flux_etf_qqq_5j":       "QQQ",
    "flux_etf_spy_ivv_5j":   "SPY",
    "flux_etf_slv_pslv_5j":  "SLV",
    "flux_etf_msci_france_5j": "EWQ",
    # --- Breadth (proxy participation interne : ratio equal-weight / cap-weight) ---
    # PROXY, pas le vrai % >MA50. Ratio EW/CW en hausse = rallye large
    # (participation saine) = haussier ; en baisse = rallye méga-caps = baissier.
    # Tuple (num, den) → routé vers _twelve_ratio_zscore dans le dispatch zscore.
    "breadth_sp_ma50":        ("RSP", "SPY"),    # S&P 500 equal-weight / cap-weight
    "breadth_nasdaq100_ma50": ("QQQE", "QQQ"),   # Nasdaq-100 equal-weight / cap-weight
    # CAC : pas d'ETF equal-weight gratuit évident → reste n/a (handler dédié).
    "breadth_cac_ma50":       "^FCHI",
}


def _twelve_perf_5j(symbol: str) -> Optional[float]:
    """Performance relative sur 5 jours (close / close-5j - 1). None si indispo."""
    series = fetch_twelve_series(symbol, outputsize=10)
    if not series or len(series) < 6:
        return None
    last = series[-1][1]
    ref = series[-6][1]
    if ref == 0:
        return None
    return last / ref - 1.0


def _twelve_zscore_from_symbol(symbol: str, crit: dict) -> Optional[Tuple[float, float]]:
    """Récupère séries Twelve + calcule (value, normalisee)."""
    window = int(crit.get("zscore_window", 60))
    series = fetch_twelve_series(symbol, outputsize=max(window + 5, 20))
    if not series or len(series) < max(10, window // 4):
        return None
    closes = [c for _, c in series]
    hist = closes[-window:] if len(closes) >= window else closes
    return zscore_from_series(hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                              cap=float(crit.get("cap", 1.0)))


def _twelve_spread_zscore(sym_a: str, sym_b: str, crit: dict) -> Optional[Tuple[float, float]]:
    """Spread A - B → z-score sur la fenêtre. None si une série manque."""
    window = int(crit.get("zscore_window", 60))
    sa = fetch_twelve_series(sym_a, outputsize=max(window + 5, 20))
    sb = fetch_twelve_series(sym_b, outputsize=max(window + 5, 20))
    if not sa or not sb:
        return None
    # Aligne par date (intersection)
    dict_b = {d.date(): c for d, c in sb}
    pairs = [(d.date(), c - dict_b[d.date()]) for d, c in sa if d.date() in dict_b]
    if len(pairs) < max(10, window // 4):
        return None
    spreads = [v for _, v in pairs]
    hist = spreads[-window:] if len(spreads) >= window else spreads
    return zscore_from_series(hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                              cap=float(crit.get("cap", 1.0)))


def _twelve_spread_lineaire(sym_a: str, sym_b: str) -> Optional[float]:
    """Spread A - B (dernière valeur)."""
    pa = fetch_twelve_price(sym_a)
    pb = fetch_twelve_price(sym_b)
    if pa is None or pb is None:
        return None
    return pa - pb


def _twelve_ratio_zscore(sym_num: str, sym_den: str, crit: dict) -> Optional[Tuple[float, float]]:
    """Ratio A/B → z-score sur fenêtre."""
    window = int(crit.get("zscore_window", 60))
    sa = fetch_twelve_series(sym_num, outputsize=max(window + 5, 20))
    sb = fetch_twelve_series(sym_den, outputsize=max(window + 5, 20))
    if not sa or not sb:
        return None
    dict_b = {d.date(): c for d, c in sb}
    pairs = []
    for d, c in sa:
        b = dict_b.get(d.date())
        if b is None or b == 0:
            continue
        pairs.append((d.date(), c / b))
    if len(pairs) < max(10, window // 4):
        return None
    ratios = [v for _, v in pairs]
    hist = ratios[-window:] if len(ratios) >= window else ratios
    return zscore_from_series(hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                              cap=float(crit.get("cap", 1.0)))


def _twelve_ratio_lineaire(sym_num: str, sym_den: str) -> Optional[float]:
    pa = fetch_twelve_price(sym_num)
    pb = fetch_twelve_price(sym_den)
    if pa is None or pb is None or pb == 0:
        return None
    return pa / pb


def _twelve_alpha_5j(sym_a: str, sym_b: str, crit: dict) -> Optional[Tuple[float, float]]:
    """Alpha 5j = perf(A,5j) - perf(B,5j). Z-score sur fenêtre des alphas glissants."""
    window = int(crit.get("zscore_window", 60))
    sa = fetch_twelve_series(sym_a, outputsize=max(window + 10, 25))
    sb = fetch_twelve_series(sym_b, outputsize=max(window + 10, 25))
    if not sa or not sb or len(sa) < 10 or len(sb) < 10:
        return None
    dict_b = {d.date(): c for d, c in sb}
    aligned = [(d.date(), c, dict_b[d.date()]) for d, c in sa if d.date() in dict_b]
    if len(aligned) < 10:
        return None
    alphas: List[float] = []
    for i in range(5, len(aligned)):
        ca0 = aligned[i - 5][1]
        ca1 = aligned[i][1]
        cb0 = aligned[i - 5][2]
        cb1 = aligned[i][2]
        if ca0 == 0 or cb0 == 0:
            continue
        alphas.append((ca1 / ca0 - 1.0) - (cb1 / cb0 - 1.0))
    if len(alphas) < 5:
        return None
    hist = alphas[-window:] if len(alphas) >= window else alphas
    return zscore_from_series(hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                              cap=float(crit.get("cap", 1.0)))


def _twelve_rsi_lineaire(symbol: str) -> Optional[float]:
    """RSI 14j brut (valeur 0-100). Le scoring fiche utilise centre=50 echelle ~20."""
    return fetch_twelve_rsi(symbol, period=14)


# ---------------------------------------------------------------------------
# Mapping non-monotone (VIX/V2X/VXN regime : +1 zone centre, -1 extrêmes)
# ---------------------------------------------------------------------------

def _mapping_non_monotone_vix(value: float, *, centre: float = 15.0,
                              low_zero: float = 11.0, high_zero: float = 28.0,
                              cap: float = 1.0,
                              low: Optional[float] = None,
                              high: Optional[float] = None) -> float:
    """Mapping triangulaire asymétrique pour un index de volatilité (VIX/VXN/V2X).

    +cap exactement au centre_optimal (régime sain), décroissance linéaire vers
    -cap aux deux bornes extrêmes (complacence basse `low_zero`, stress haut
    `high_zero`), puis capé à -cap au-delà.

    Calibrage (cf. fiches *.yml, champs centre_optimal + effet_short) :
      - sp500  : centre=15, low_zero=11, high_zero=28
      - nasdaq : centre=20, low_zero=14, high_zero=35
      - cac40  : centre=16, low_zero=11, high_zero=30

    Exemples (sp500) :
      VIX=15   → +1.0   (centre, régime sain)
      VIX=23.9 → ≈-0.37 (proche du stress)
      VIX=28   → -1.0   (borne stress)
      VIX=11   → -1.0   (borne complacence)
      VIX=40   → -1.0   (capé)

    NB : l'ancienne implémentation était un *plateau* [14,25]→+1, qui classait à
    tort VIX≈24 comme "sain". Remplacé par ce triangle conforme aux fiches.

    Rétrocompat : `low`/`high` (ancienne API plateau) sont acceptés comme alias
    dépréciés et réinterprétés en bornes -cap (low→low_zero, high→high_zero),
    afin de ne pas casser les appelants existants (ex: backtest_quant).
    """
    if low is not None:
        low_zero = low
    if high is not None:
        high_zero = high
    if value >= centre:
        span = max(high_zero - centre, 1e-6)
        score = cap - 2.0 * cap * (value - centre) / span
    else:
        span = max(centre - low_zero, 1e-6)
        score = cap - 2.0 * cap * (centre - value) / span
    return max(-cap, min(cap, score))


# ---------------------------------------------------------------------------
# Fenêtres d'activation
# ---------------------------------------------------------------------------

def is_in_activation_window(cle: str, now: datetime, triggers_cfg: dict, fiche_key: str) -> Optional[bool]:
    """Retourne True/False si une fenêtre est définie pour ce critère, None sinon.

    Règles connues (cf. triggers-and-windows.yml) :
    - eia_crude_surprise : mercredi 16h30 CET → vendredi 16h30 CET
    - api_weekly_surprise : mardi 22h30 → mercredi 16h30 CET
    - caixin_pmi_manuf : 1er-9 du mois
    - wasde : 8-17 du mois
    - nass_crop_progress : lundi 22h → vendredi 22h CET (avril-novembre)
    - grindings_q : mi-jan/avril/juil/oct → +14j
    Inconnu → None (pas de fenêtre à appliquer).
    """
    try:
        cet = now.astimezone(ZoneInfo("Europe/Paris"))
    except Exception:  # noqa: BLE001
        cet = now
    wd = cet.weekday()
    h = cet.hour + cet.minute / 60.0
    m = cet.month
    d = cet.day

    if cle == "eia_crude_surprise":
        if wd == 2 and h >= 16.5:
            return True
        if wd == 3:
            return True
        if wd == 4 and h < 16.5:
            return True
        return False
    if cle in ("api_weekly_surprise", "api_bulletin_surprise"):
        if wd == 1 and h >= 22.5:
            return True
        if wd == 2 and h < 16.5:
            return True
        return False
    if cle == "caixin_pmi_manuf":
        return d <= 9
    if cle == "wasde" or cle == "usda_wasde_stocks_to_use":
        return 8 <= d <= 17
    if cle == "nass_crop_progress":
        if m < 4 or m > 11:
            return False
        if wd == 0 and h >= 22:
            return True
        if 1 <= wd <= 3:
            return True
        if wd == 4 and h < 22:
            return True
        return False
    if cle == "grindings_q":
        if m in (1, 4, 7, 10) and 15 <= d <= 29:
            return True
        return False
    return None


# ---------------------------------------------------------------------------
# Heuristique GATE
# ---------------------------------------------------------------------------

# Mots-clés d'événement extrême PAR actif (fallback legacy, sans impacts IA)
_GATE_KEYWORDS = {
    "petrole": ("opec", "iran", "ormuz", "hormuz", "strait of hormuz", "fomc"),
    "or": ("fomc", "cpi", "nfp", "guerre", "war", "escalad"),
    "argent": ("fomc", "cpi", "nfp"),
    "cac40": ("fomc", "bce", "ecb", "cpi", "nfp", "censure", "dissolution"),
    "sp500": ("fomc", "cpi", "nfp"),
    "nasdaq": ("fomc", "cpi", "nvidia", "nvda", "earnings"),
    "eurusd": ("fomc", "ecb", "bce", "nfp", "cpi"),
    "cuivre": ("caixin", "pmi", "fomc", "stimulus", "chine", "china"),
    "cafe": ("gel", "frost", "conab", "drought", "sécheresse"),
    "cacao": ("harmattan", "icco", "eudr"),
    "ble": ("wasde", "mer noire", "black sea", "corridor"),
    "vix": ("fomc", "cpi", "nfp", "ecb"),
}
# id actif IA (extractor) → clé de fiche
_IA_TO_FICHE = {
    "BRENT": "petrole", "GOLD": "or", "SILVER": "argent", "CAC40": "cac40",
    "SP500": "sp500", "NASDAQ": "nasdaq", "EURUSD": "eurusd", "COPPER": "cuivre",
    "COFFEE": "cafe", "COCOA": "cacao", "WHEAT": "ble", "VIX": "vix",
}


def _resolve_gate(fiche_key: str, cle: str, now: datetime, events: List[dict]) -> bool:
    """GATE spécifique à l'actif = un événement EXTRÊME imminent le concernant.

    Vrai si : (a) fenêtre EIA active (pétrole uniquement), OU
              (b) un event de matérialité HIGH cible cet actif (impacts IA) < 24h, OU
              (c) fallback legacy : mot-clé extrême SPÉCIFIQUE à l'actif < 24h.
    Ne s'allume donc plus pour tous les actifs dès qu'une news macro tombe.
    """
    # (a) fenêtre EIA Crude (mercredi 16-17h CET) → seulement pétrole
    if fiche_key == "petrole":
        try:
            cet = now.astimezone(ZoneInfo("Europe/Paris"))
        except Exception:  # noqa: BLE001
            cet = now
        if cet.weekday() == 2 and 16 <= cet.hour <= 17:
            return True

    kws = _GATE_KEYWORDS.get(fiche_key, ())
    cutoff = now - timedelta(hours=24)
    for ev in events:
        dt = ev.get("_dt")
        if not (isinstance(dt, datetime) and dt >= cutoff):
            continue
        impacts = ev.get("_impacts") or []
        # (b) v2 : event high-materiality ciblant CET actif
        if (ev.get("materiality") or "").strip().lower() == "high" and impacts:
            for imp in impacts:
                if _IA_TO_FICHE.get((imp.get("asset") or "").upper()) == fiche_key:
                    return True
        # (c) fallback legacy : seulement si pas d'impacts IA + mot-clé spécifique actif
        if not impacts and kws:
            text = tc._event_text(ev).lower()
            if any(k in text for k in kws):
                return True
    return False


# ---------------------------------------------------------------------------
# Construction des critères par fiche
# ---------------------------------------------------------------------------

def _emit_zscore(value: float, normalisee: float, ts: str) -> dict:
    # Pour les critères numériques (z-scores), la valeur normalisée EST déjà
    # graduée → valeur_ponderee = valeur_normalisee. (Identité entre les deux chemins.)
    return {"valeur": value, "valeur_normalisee": normalisee,
            "valeur_ponderee": normalisee, "ts": ts}


def _handle_twelve_zscore_dispatch(cle: str, crit: dict, ts: str) -> Optional[dict]:
    """Dispatcher pour les zscores Twelve Data — gère symbole simple, spread, ratio, alpha."""
    spec = TWELVE_SYMBOLS.get(cle)
    if spec is None:
        return None
    # RSI exception : (RSI, SYMBOL) → on sort en lineaire même si la fiche dit zscore
    # (RSI est par construction borné 0-100, le scoring fiche fait centre/echelle).
    if isinstance(spec, tuple) and spec[0] == "RSI":
        rsi = _twelve_rsi_lineaire(spec[1])
        if rsi is None:
            return None
        return {"valeur": rsi, "ts": ts}
    # Spread / ratio / alpha
    if isinstance(spec, tuple):
        sym_a, sym_b = spec
        if cle.startswith("spread_"):
            res = _twelve_spread_zscore(sym_a, sym_b, crit)
        elif cle.startswith("ratio_"):
            res = _twelve_ratio_zscore(sym_a, sym_b, crit)
        elif cle.startswith("breadth_"):
            # Proxy participation : ratio equal-weight / cap-weight (RSP/SPY,
            # QQQE/QQQ) → z-score. Pas le vrai % >MA50. Si une des deux séries
            # manque → None (n/a propre, absorbé par le gate S5).
            res = _twelve_ratio_zscore(sym_a, sym_b, crit)
        elif cle.startswith("alpha_"):
            res = _twelve_alpha_5j(sym_a, sym_b, crit)
        elif cle.startswith("differentiel_") or cle.startswith("spread_oat"):
            res = _twelve_spread_zscore(sym_a, sym_b, crit)
        elif cle == "term_structure_vix_vix3m":
            # cas particulier : ratio mais sortie lineaire
            ratio = _twelve_ratio_lineaire(sym_a, sym_b)
            if ratio is None:
                return None
            return {"valeur": ratio, "ts": ts}
        elif cle == "brent_term_structure_m1m2":
            # Pas de M2 distinct via Twelve gratuit → on retourne n/a explicite
            SKIP_COUNTER[f"twelve_no_m2:{cle}"] += 1
            return None
        elif cle == "usd_cfa_usd_cedi":
            res = _twelve_spread_zscore(sym_a, sym_b, crit)
        else:
            res = None
        if res is None:
            return None
        return _emit_zscore(res[0], res[1], ts)
    # Symbole simple
    if cle == "mouvement_or_5j" or cle.startswith("flux_etf_"):
        # perf 5j → z-score sur fenêtre des perfs 5j glissantes
        perf = _twelve_perf_5j(spec)
        if perf is None:
            return None
        # On utilise une approximation : série de perfs glissantes
        series = fetch_twelve_series(spec, outputsize=int(crit.get("zscore_window", 60)) + 10)
        if not series or len(series) < 10:
            return None
        closes = [c for _, c in series]
        perfs = [closes[i] / closes[i - 5] - 1.0 for i in range(5, len(closes)) if closes[i - 5] != 0]
        if len(perfs) < 5:
            return None
        res = zscore_from_series(perfs, zscore_div=float(crit.get("zscore_div", 2.0)),
                                 cap=float(crit.get("cap", 1.0)))
        if res is None:
            return None
        return _emit_zscore(res[0], res[1], ts)
    # Cas par défaut : z-score sur les closes
    res = _twelve_zscore_from_symbol(spec, crit)
    if res is None:
        return None
    return _emit_zscore(res[0], res[1], ts)


def _handle_twelve_lineaire_dispatch(cle: str, crit: dict, ts: str) -> Optional[dict]:
    """Dispatcher pour les lineaires Twelve Data."""
    spec = TWELVE_SYMBOLS.get(cle)
    if spec is None:
        return None
    if isinstance(spec, tuple) and spec[0] == "RSI":
        rsi = _twelve_rsi_lineaire(spec[1])
        if rsi is None:
            return None
        return {"valeur": rsi, "ts": ts}
    if isinstance(spec, tuple):
        sym_a, sym_b = spec
        if cle.startswith("spread_"):
            val = _twelve_spread_lineaire(sym_a, sym_b)
        elif cle.startswith("ratio_") or cle == "term_structure_vix_vix3m":
            val = _twelve_ratio_lineaire(sym_a, sym_b)
        elif cle == "term_structure_m1_m3":
            SKIP_COUNTER[f"twelve_no_m3:{cle}"] += 1
            return None
        elif cle == "brent_term_structure_m1m2":
            SKIP_COUNTER[f"twelve_no_m2:{cle}"] += 1
            return None
        else:
            return None
        if val is None:
            return None
        return {"valeur": val, "ts": ts}
    # Symbole simple : on récupère le prix brut
    if cle in ("niveau_vix_absolu", "vvix", "skew_index_cboe"):
        price = fetch_twelve_price(spec)
        if price is None:
            return None
        return {"valeur": price, "ts": ts}
    if cle.startswith("rsi_14j_"):
        # ne devrait pas arriver ici (déjà géré ci-dessus), garde-fou
        return None
    if cle.startswith("breadth_"):
        # Pas de vrai breadth → n/a explicite
        SKIP_COUNTER[f"no_breadth_data:{cle}"] += 1
        return None
    price = fetch_twelve_price(spec)
    if price is None:
        return None
    return {"valeur": price, "ts": ts}


# Régimes de volatilité indexés sur un indice exposé en CSV CBOE (source fraîche
# et faisant autorité, identique à niveau_vix_absolu). Pour ces clés on lit CBOE
# en PRIORITÉ afin que vix_regime utilise EXACTEMENT la même valeur VIX que
# niveau_vix_absolu / vix_risk_off_proxy (qui passent déjà par _handle_cboe).
# Sans ça, vix_regime lisait ^VIX via Twelve (valeur périmée/désynchronisée :
# 23.6 alors que CBOE donnait 14.95 le même jour → faux régime "stress").
# VXN (^VXN) et V2X (^STOXX50EVOL) ne sont PAS exposés en CSV CBOE public →
# fallback Twelve/yfinance conservé pour eux.
MAPPING_REGIME_CBOE_INDEX = {
    "vix_regime": "VIX",
}


def _handle_mapping_non_monotone(cle: str, crit: dict, ts: str) -> Optional[dict]:
    """Récupère le niveau de l'indice + applique mapping_non_monotone_vix.

    Source : CBOE CSV en priorité pour les régimes VIX (cohérence avec
    niveau_vix_absolu), fallback Twelve/yfinance pour VXN/V2X.
    """
    price: Optional[float] = None
    # 1) Source CBOE (fraîche, faisant autorité) pour les régimes basés VIX.
    cboe_idx = MAPPING_REGIME_CBOE_INDEX.get(cle)
    if cboe_idx:
        series = fetch_cboe_history(cboe_idx)
        if series:
            price = series[-1][1]
    # 2) Fallback Twelve/yfinance (VXN/V2X, ou CBOE indisponible).
    if price is None:
        spec = TWELVE_SYMBOLS.get(cle)
        if not spec or isinstance(spec, tuple):
            return None
        price = fetch_twelve_price(spec)
    if price is None:
        return None
    cap = float(crit.get("cap", 1.0))
    # Calibrage configurable via fiche ; defaults orientés VIX (sp500).
    # `centre` = centre_optimal de la fiche (+cap). `low_zero`/`high_zero` =
    # bornes extrêmes (-cap), dérivables de effet_short (ex: "VIX>28 OU <11").
    centre = float(crit.get("centre_optimal", crit.get("centre", 15.0)))
    low_zero = float(crit.get("low_zero", crit.get("low", 11.0)))
    high_zero = float(crit.get("high_zero", crit.get("high", 28.0)))
    norm = _mapping_non_monotone_vix(price, centre=centre, low_zero=low_zero,
                                     high_zero=high_zero, cap=cap)
    return {"valeur": price, "valeur_normalisee": norm,
            "valeur_ponderee": norm, "ts": ts}


def _handle_composite(cle: str, crit: dict, ts: str) -> Optional[dict]:
    """Composites : on tente de reconstituer via sous-séries Twelve si possible.

    Politique P4 (composites silencieux) :
    - Si une sous-source est alimentable → on l'utilise (proxy honnête).
    - Si AUCUNE sous-source n'est dispo → on RETOURNE None (skip propre, poids
      effectif 0, le critère n'apparaît pas dans criteres-courants.md) ET on
      émet un WARNING explicite via SKIP_COUNTER pour traçabilité.
    Ne JAMAIS retourner 0.0 silencieusement (faisait apparaître le critère
    comme "actif mais nul" — distortion du score).
    """
    # meteo_bresil_minas_gerais : composite (précipitations + check Tmin<4°C). On utilise
    # juste l'anomalie pluie (proxy) — la composante T° n'est pas critique en routine.
    if cle == "meteo_bresil_minas_gerais":
        # Coords alignées sur METEO_CRITERIA (brief P3 : Belo Horizonte -19.9/-43.9)
        lat, lon, days = METEO_CRITERIA.get(cle, (-19.9, -43.9, 60))
        z = fetch_open_meteo_anomaly(lat, lon, days=days)
        if z is None:
            SKIP_COUNTER[f"composite_meteo_dead:{cle}"] += 1
            logger.warning("composite %s : Open-Meteo KO → n/a", cle)
            return None
        cap = float(crit.get("cap", 1.0))
        div = float(crit.get("zscore_div", 2.0))
        norm = max(-cap, min(cap, z / div))
        return {"valeur": z, "valeur_normalisee": norm,
                "valeur_ponderee": norm, "ts": ts}
    # hf_positioning_flux_options (cacao) : composite put/call OI + COT.
    # Put/call options non câblé (pas de source publique fiable) → on utilise
    # le COT noncomm cacao seul comme proxy. WARNING explicite : sous-source
    # options manquante.
    if cle == "hf_positioning_flux_options":
        market = "COCOA - ICE FUTURES U.S."
        nets = fetch_cftc_managed_money_nets(market, weeks=260)
        if not nets or len(nets) < 20:
            SKIP_COUNTER[f"composite_cftc_thin:{cle}"] += 1
            logger.warning("composite %s : CFTC cacao thin/dead → n/a", cle)
            return None
        cap = float(crit.get("cap", 1.0))
        div = float(crit.get("zscore_div", 2.0))
        res = zscore_from_series(nets[-252:], zscore_div=div, cap=cap)
        if res is None:
            SKIP_COUNTER[f"composite_cftc_zscore:{cle}"] += 1
            return None
        # signe inversé déjà géré par la fiche (signe: -1)
        SKIP_COUNTER[f"composite_partial:{cle}"] += 1  # WARNING : 1 sous-source sur 2
        logger.warning("composite %s : sous-source put/call options manquante "
                       "(COT seul utilisé) — résultat partiel", cle)
        return _emit_zscore(res[0], res[1], ts)
    # demande_pv_mining_strikes (argent) : composite triplet+triplet.
    # Aucune sous-source alimentable automatiquement → SKIP propre (n/a, pas
    # 0.0). Le scoring traitera comme poids effectif 0.
    if cle == "demande_pv_mining_strikes":
        SKIP_COUNTER[f"composite_no_subsource:{cle}"] += 1
        logger.warning("composite %s : aucune sous-source alimentable "
                       "(PV demand + mining strikes) → n/a (pas de neutre 0)", cle)
        return None
    SKIP_COUNTER[f"composite_unmapped:{cle}"] += 1
    logger.warning("composite %s : non mappé dans _handle_composite → n/a", cle)
    return None


def _handle_cftc(cle: str, crit: dict, ts: str) -> Optional[dict]:
    market = CFTC_MARKETS.get(cle)
    if not market:
        return None
    window = int(crit.get("zscore_window", 252))
    nets = fetch_cftc_managed_money_nets(market, weeks=max(window + 10, 260))
    if not nets or len(nets) < 20:
        return None
    value = nets[-1]
    hist = nets[-window:] if len(nets) >= window else nets
    norm = compute_zscore_normalisee(value, hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                                     cap=float(crit.get("cap", 1.0)))
    if norm is None:
        return None
    return _emit_zscore(value, norm, ts)


def _handle_eia(cle: str, crit: dict, ts: str) -> Optional[dict]:
    spec = EIA_SERIES.get(cle)
    if not spec:
        return None
    path, frequency, series_id = spec
    window = int(crit.get("zscore_window", 52))
    series = fetch_eia_series(path, frequency=frequency, series_id=series_id, length=window + 10)
    if not series or len(series) < 10:
        return None
    value = series[-1]
    hist = series[-window:] if len(series) >= window else series
    norm = compute_zscore_normalisee(value, hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                                     cap=float(crit.get("cap", 1.0)))
    if norm is None:
        return None
    return _emit_zscore(value, norm, ts)


def _handle_fred(cle: str, crit: dict, ts: str) -> Optional[dict]:
    """Calcule un z-score à partir d'une série FRED (simple ou spread US-DE)."""
    window = int(crit.get("zscore_window", 252))
    # Spread US-DE
    if cle in FRED_SPREADS:
        sus, sde = FRED_SPREADS[cle]
        series = fetch_fred_spread(sus, sde, n=max(window + 10, 260))
    elif cle in FRED_SERIES_SIMPLE:
        sid = FRED_SERIES_SIMPLE[cle]
        series = fetch_fred_series(sid, n=max(window + 10, 260))
    else:
        return None
    if not series or len(series) < 10:
        return None
    value = series[-1]
    hist = series[-window:] if len(series) >= window else series
    norm = compute_zscore_normalisee(value, hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                                     cap=float(crit.get("cap", 1.0)))
    if norm is None:
        return None
    return _emit_zscore(value, norm, ts)


def _handle_cboe(cle: str, crit: dict, ts: str, type_norm: str) -> Optional[dict]:
    """Récupère VIX/VIX3M/SKEW/VVIX via CSV CBOE et émet le bon format.

    - term_structure_vix_vix3m : ratio VIX/VIX3M (lineaire) — sortie {valeur}
    - niveau_vix_absolu, skew_index_cboe, vvix : lineaire — sortie {valeur}
    - vix_risk_off_proxy (zscore) : z-score des closes VIX sur la fenêtre
    """
    if cle == "term_structure_vix_vix3m":
        sa = fetch_cboe_history("VIX")
        sb = fetch_cboe_history("VIX3M")
        if not sa or not sb:
            return None
        # Aligne par date d'observation, prend la dernière intersection
        db = dict(sb)
        last_date = None
        last_a = last_b = None
        for d, a in sa:
            if d in db:
                last_date = d
                last_a = a
                last_b = db[d]
        if last_a is None or last_b is None or last_b == 0:
            return None
        return {"valeur": last_a / last_b, "ts": ts}
    idx = CBOE_HISTORY_INDEX.get(cle)
    if not idx:
        return None
    series = fetch_cboe_history(idx)
    if not series:
        return None
    if type_norm == "zscore":
        if len(series) < 2:
            return None
        closes = [c for _, c in series]
        window = int(crit.get("zscore_window", 60))
        hist = closes[-window:] if len(closes) >= window else closes
        res = zscore_from_series(hist, zscore_div=float(crit.get("zscore_div", 2.0)),
                                 cap=float(crit.get("cap", 1.0)))
        if res is None:
            return None
        return _emit_zscore(res[0], res[1], ts)
    # lineaire : on retourne le dernier close
    return {"valeur": series[-1][1], "ts": ts}


def _handle_meteo(cle: str, crit: dict, ts: str) -> Optional[dict]:
    spec = METEO_CRITERIA.get(cle)
    if not spec:
        return None
    lat, lon, days = spec
    z = fetch_open_meteo_anomaly(lat, lon, days=days)
    if z is None:
        return None
    cap = float(crit.get("cap", 1.0))
    div = float(crit.get("zscore_div", 2.0))
    norm = max(-cap, min(cap, z / div))
    return {"valeur": z, "valeur_normalisee": norm,
            "valeur_ponderee": norm, "ts": ts}


def build_critere_value(
    fiche_key: str,
    crit: dict,
    triplets: Dict[str, int],
    triggers_cfg: dict,
    events: List[dict],
    now: datetime,
) -> Optional[dict]:
    """Retourne le dict {valeur, [valeur_normalisee], ts} ou None si critère à omettre."""
    cle = crit.get("cle_courante")
    if not cle:
        return None
    type_norm = crit.get("normalisation")
    source = (crit.get("source") or "").lower()
    ts = now.isoformat()

    # GATE
    if type_norm == "gate":
        return {"valeur": _resolve_gate(fiche_key, cle, now, events), "ts": ts}

    # Triplet (résolu par triggers_classifier)
    if type_norm == "triplet":
        weighting = wg.load_weighting()
        if cle in triplets:
            entry = triplets[cle]
            synth_rationale = ""
            # Phase 2 — meta propagée par triggers_classifier (nature, event_id, ...)
            p2_meta: Dict[str, Any] = {}
            if isinstance(entry, dict):
                val = int(entry.get("valeur", 0))
                mat = entry.get("materiality", "")
                rel = entry.get("reliability", "")
                source_track = entry.get("source_track", "")
                # Persistance "pourquoi" DeepSeek (demande Thomas 2026-06-01) :
                # le rationale de la synthèse directionnelle, posé par
                # triggers_classifier.classify_all_with_meta. Vide si critère non-IA.
                synth_rationale = str(entry.get("synthese_rationale", "") or "")
                # Phase 2 — propage nature + meta event source pour le scoring
                # (scoring_analyste lit raw.get("nature") → CritereResult.nature
                # → coef_nature appliqué + métriques M5/T1/T2 + decision-log).
                for k in ("nature", "event_id", "event_date",
                          "event_date_source", "freshness_days"):
                    if k in entry and entry[k] not in (None, ""):
                        p2_meta[k] = entry[k]
                # A1 — shadow_contrib_exclu : dict {horizon: float} agrégé par
                # triggers_classifier sur les events deja_cote/stale/repost.
                # Propagé tel quel au raw (consommé par scoring pour T1).
                if "p2_shadow_contrib_exclu" in entry and entry["p2_shadow_contrib_exclu"]:
                    p2_meta["p2_shadow_contrib_exclu"] = entry["p2_shadow_contrib_exclu"]
                # Gate C1 — sign_conflict (cohérence de signe DeepSeek) :
                # propagation au raw pour traçabilité decision-log + affichage.
                if entry.get("sign_conflict"):
                    p2_meta["sign_conflict"] = True
                    p2_meta["sign_conflict_details"] = entry.get(
                        "sign_conflict_details", []
                    )
            else:
                val = int(entry)
                mat = ""
                rel = ""
                source_track = "legacy"
            valeur_ponderee = weighting.weight_direction(val, mat, rel)
            out: Dict[str, Any] = {
                "valeur": val,
                "valeur_normalisee": float(val),
                "valeur_ponderee": valeur_ponderee,
                "materiality": mat,
                "reliability": rel,
                "source_track": source_track,
                "ts": ts,
            }
            if synth_rationale:
                out["synthese_rationale"] = synth_rationale
            # Phase 2 — nature & meta event (clés ajoutées seulement si présentes,
            # zéro invention : un critère sans event source ne porte pas de nature).
            out.update(p2_meta)
            return out
        SKIP_COUNTER[f"triplet_no_cfg:{cle}"] += 1
        return {
            "valeur": 0,
            "valeur_normalisee": 0.0,
            "valeur_ponderee": 0.0,
            "materiality": "",
            "reliability": "",
            "source_track": "none",
            "ts": ts,
        }

    # Mapping non-monotone (VIX/V2X/VXN regime)
    if type_norm == "mapping_non_monotone":
        return _handle_mapping_non_monotone(cle, crit, ts)

    # Composite (résolu par helper dédié)
    if type_norm == "composite":
        return _handle_composite(cle, crit, ts)

    # Fenêtre d'activation
    in_window = is_in_activation_window(cle, now, triggers_cfg, fiche_key)
    if in_window is False:
        return {"valeur_normalisee": 0.0, "ts": ts, "note": "hors fenêtre"}

    # Numérique (zscore / lineaire)
    if type_norm == "zscore":
        # CFTC d'abord (peut être détecté par préfixe)
        if cle.startswith("cftc_") or "cftc" in source:
            res = _handle_cftc(cle, crit, ts)
            if res is not None:
                return res
            return None
        # EIA
        if cle in EIA_SERIES or "eia" in source:
            res = _handle_eia(cle, crit, ts)
            if res is not None:
                return res
            return None
        # FRED (taux réels TIPS, HY OAS, différentiels US-DE)
        if cle in FRED_SERIES_SIMPLE or cle in FRED_SPREADS or "fred" in source:
            res = _handle_fred(cle, crit, ts)
            if res is not None:
                return res
            return None
        # CBOE (Put/Call : non câblé sans auth → skip ; SKEW/VVIX/VIX en zscore : si demandé)
        if cle in CBOE_HISTORY_INDEX or "cboe" in source:
            res = _handle_cboe(cle, crit, ts, "zscore")
            if res is not None:
                return res
            # Sinon : Put/Call sans CSV public fiable → skip propre
            SKIP_COUNTER[f"cboe_unmapped:{cle}"] += 1
            return None
        # Open-Meteo
        if cle in METEO_CRITERIA:
            return _handle_meteo(cle, crit, ts)
        # Twelve Data (catch-all : symbole, spread, ratio, alpha)
        if cle in TWELVE_SYMBOLS or "twelve" in source:
            res = _handle_twelve_zscore_dispatch(cle, crit, ts)
            if res is not None:
                return res
        # Sources non programmatiques (AAII, USDA WASDE, CFTC inexistants, etc.)
        SKIP_COUNTER[f"zscore_unmapped:{cle}"] += 1
        return None

    if type_norm == "lineaire":
        # CBOE en priorité pour les critères vol (term structure, SKEW, VVIX, niveau VIX)
        if cle == "term_structure_vix_vix3m" or cle in CBOE_HISTORY_INDEX or "cboe" in source:
            res = _handle_cboe(cle, crit, ts, "lineaire")
            if res is not None:
                return res
            # Fallback Twelve Data si CBOE indispo (ex: VIX via Twelve)
        if cle in TWELVE_SYMBOLS or "twelve" in source:
            res = _handle_twelve_lineaire_dispatch(cle, crit, ts)
            if res is not None:
                return res
        SKIP_COUNTER[f"lineaire_unmapped:{cle}"] += 1
        return None

    SKIP_COUNTER[f"unknown_norm:{type_norm}"] += 1
    return None


def collect_for_fiche(
    fiche_key: str,
    fiche: dict,
    triplets: Dict[str, int],
    triggers_cfg: dict,
    events: List[dict],
    now: datetime,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for crit in fiche.get("criteres", []):
        cle = crit.get("cle_courante")
        if not cle:
            continue
        try:
            val = build_critere_value(fiche_key, crit, triplets, triggers_cfg, events, now)
        except Exception as e:  # noqa: BLE001
            logger.warning("Critère %s/%s : exception %s — omis", fiche_key, cle, e)
            SKIP_COUNTER[f"exception:{cle}"] += 1
            continue
        if val is None:
            continue
        out[cle] = val
    return out


# ---------------------------------------------------------------------------
# Écriture criteres-courants.md
# ---------------------------------------------------------------------------

def write_criteres(payload: dict, path: Path = CRITERES_OUT) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    yml = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    content = (
        "# Critères courants — généré par criteres_calculator.py\n"
        "# Source de vérité du moteur de scoring (Analyste).\n\n"
        "```yaml\n" + yml + "```\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def load_fiches(fiches_dir: Path = FICHES_DIR) -> Dict[str, dict]:
    fiches: Dict[str, dict] = {}
    for f in sorted(fiches_dir.glob("*.yml")):
        with f.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and "criteres" in data:
            fiches[f.stem] = data
    return fiches


def run(now: Optional[datetime] = None) -> Path:
    SKIP_COUNTER.clear()
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    fiches = load_fiches()
    triggers_cfg = tc.load_triggers_config()
    events = tc.parse_events_log()

    # Synthèse directionnelle par actif (niveau 1 — DeepSeek). Si la clé
    # DEEPSEEK_API_KEY est absente OU si le hard-cap coût est atteint,
    # l'extractor est désactivé → classify_all_with_meta retombe sur
    # l'agrégation mécanique legacy (rétro-compat 100%).
    extractor_for_synthese: Any = None
    try:
        from extractor import Extractor  # import local : pas de cycle, pas de coût si non utilisé
        ext = Extractor()
        if ext.is_enabled():
            extractor_for_synthese = ext
            logger.info("synthese-directionnelle: extractor activé")
        else:
            logger.info("synthese-directionnelle: extractor désactivé (no key / hard-cap) -> fallback legacy")
    except Exception as e:  # noqa: BLE001
        logger.warning("synthese-directionnelle: init extractor KO (%s) -> fallback legacy", e)

    # On utilise la variante "with_meta" pour propager materiality/reliability
    # jusqu'aux critères (nécessaire au calcul de valeur_ponderee).
    triplets_by_actif = tc.classify_all_with_meta(
        events=events, today=now, triggers_cfg=triggers_cfg,
        extractor=extractor_for_synthese,
    )

    payload: Dict[str, Any] = {"last_update": now.isoformat()}
    total_crit = 0
    total_filled = 0
    for key, fiche in fiches.items():
        actif_triplets = triplets_by_actif.get(key, {})
        crits = collect_for_fiche(key, fiche, actif_triplets, triggers_cfg, events, now)
        payload[key] = crits
        total_crit += len(fiche.get("criteres", []))
        total_filled += len(crits)

    out = write_criteres(payload)
    logger.info("Critères : %d/%d alimentés (%.0f%%)", total_filled, total_crit,
                100.0 * total_filled / max(total_crit, 1))
    if SKIP_COUNTER:
        logger.info("Skips : %s", dict(SKIP_COUNTER))
    return out


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    path = run()
    print(f"OK : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
