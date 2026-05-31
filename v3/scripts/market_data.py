"""Unified market data: Twelve Data (primary) + yfinance (fallback).

Adapté du module Finance validé (symboles testés 2026-03 contre l'API réelle).
Twelve Data fournit prix/OHLCV pour stocks, forex, commodities. Fallback yfinance
quand :
- TWELVE_DATA_API_KEY non défini / vide
- Ticker non supporté sur Twelve free (indices ^GSPC, ^FCHI, etc.)
- Rate limit atteint (8 req/min free tier)
- Erreur API ou timeout

Caching + rate limiting intégrés (free tier : 800 credits/jour, 8 req/min).

API publique (drop-in pour notre projet) :
- fetch_history(yahoo_ticker, period_days, interval) -> DataFrame OHLCV
- fetch_price(yahoo_ticker, bypass_cache=False) -> float
- fetch_quote(yahoo_ticker, bypass_cache=False) -> dict
- fetch_history_batch(yahoo_tickers, period_days, interval) -> {ticker: DataFrame}

Tous les tickers en entrée sont au FORMAT YAHOO (BZ=F, ^GSPC, EURUSD=X, MC.PA…).
La traduction vers Twelve Data se fait via `_TICKER_MAP` (table de vérité).
"""

from __future__ import annotations

import logging
import math
import os
import threading
import time
from collections import deque
from datetime import date, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

# pandas / requests sont lazy-importés pour permettre l'import du module
# même sans dépendances installées (tests qui mockent fetch_* directement).
try:
    import pandas as pd  # type: ignore
except ImportError:  # pragma: no cover
    pd = None  # type: ignore

try:
    import requests as http_req  # type: ignore
except ImportError:  # pragma: no cover
    http_req = None  # type: ignore


# ── Configuration ──────────────────────────────────────────────────
def _twelve_key() -> str:
    """Lit la clé en runtime (et non au boot) pour permettre les tests qui
    setenv/delenv après import."""
    return os.environ.get("TWELVE_DATA_API_KEY", "")


TD_BASE = "https://api.twelvedata.com"
TD_TIMEOUT = 15  # seconds per request

# ── Rate limiter (8 req/min free tier, use 7 for safety) ──────────
_rate_lock = threading.Lock()
_request_times: deque = deque()
_TD_RPM = 7

# ── TTL Cache ─────────────────────────────────────────────────────
_cache: dict[str, tuple[float, Any]] = {}
_cache_lock = threading.Lock()
CACHE_TTL_SHORT = 30     # 30s — quotes
CACHE_TTL_MEDIUM = 600   # 10 min — daily history
CACHE_TTL_LONG = 1800    # 30 min — intraday bars

_CACHE_PURGE_INTERVAL = 300  # 5 minutes
_last_purge: float = 0.0


def _maybe_purge_cache() -> None:
    """Periodically purge expired cache entries to prevent memory leak."""
    global _last_purge
    now = time.monotonic()
    if now - _last_purge < _CACHE_PURGE_INTERVAL:
        return
    _last_purge = now
    with _cache_lock:
        stale = [k for k, (expiry, _) in _cache.items() if time.monotonic() > expiry]
        for k in stale:
            del _cache[k]
        if stale:
            logger.debug("Cache purge: removed %d expired entries, %d remaining", len(stale), len(_cache))


def td_available() -> bool:
    """Check if Twelve Data API key is configured and non-empty."""
    return bool(_twelve_key())


# ── Ticker mapping: yfinance format → (td_symbol, extra_params) ──
# Verified against TD /indices, /forex_pairs, /commodities endpoints (2026-03).
_TICKER_MAP: dict[str, tuple[str, dict]] = {
    # Indices — all blacklisted (404 or ETF collision on TD free tier).
    # ^GSPC, ^DJI, ^IXIC, ^RUT, ^VIX, ^FCHI, ^GDAXI, ^FTSE, ^N225 → yfinance.
    # Forex — all verified correct via /forex_pairs endpoint
    "EURUSD=X": ("EUR/USD", {}),
    "USDJPY=X": ("USD/JPY", {}),
    "GBPUSD=X": ("GBP/USD", {}),
    "USDCHF=X": ("USD/CHF", {}),
    "EURJPY=X": ("EUR/JPY", {}),
    "AUDUSD=X": ("AUD/USD", {}),
    "USDCNH=X": ("USD/CNH", {}),
    # Alias raccourcis Yahoo "EUR=X" / "JPY=X" utilisés dans nos fiches
    "EUR=X": ("EUR/USD", {}),
    "JPY=X": ("USD/JPY", {}),
    # Paris stocks (Euronext) — use mic_code=XPAR
    "TTE.PA": ("TTE", {"mic_code": "XPAR"}),
    "MC.PA": ("MC", {"mic_code": "XPAR"}),
    "BNP.PA": ("BNP", {"mic_code": "XPAR"}),
    "SAN.PA": ("SAN", {"mic_code": "XPAR"}),
    "AI.PA": ("AI", {"mic_code": "XPAR"}),
    "OR.PA": ("OR", {"mic_code": "XPAR"}),
    "RMS.PA": ("RMS", {"mic_code": "XPAR"}),
    # Commodities / Futures — verified 2026-03 with actual API key.
    # IMPORTANT: Many commodity symbols collide with stock tickers on TD.
    # Without type=commodities, TD returns the stock price.
    "CL=F": ("CL1", {"type": "commodities"}),    # WTI Crude (front month)
    "BZ=F": ("CO1", {"type": "commodities"}),     # Brent Crude (front month)
    "NG=F": ("NG1", {"type": "commodities"}),  # Natural Gas
    # Precious metals — forex-style symbols, no collision
    "GC=F": ("XAU/USD", {}),    # Gold
    "SI=F": ("XAG/USD", {}),    # Silver
    "PL=F": ("XPT/USD", {}),    # Platinum
    "PA=F": ("XPD/USD", {}),    # Palladium
    # Base metals — HG1 collides with Homag Group AG → need type=commodities
    "HG=F": ("HG1", {"type": "commodities"}),   # Copper
    # Agriculture — type=commodities added to all for safety
    "ZW=F": ("W_1", {"type": "commodities"}),     # Wheat
    "ZC=F": ("C_1", {"type": "commodities"}),     # Corn
    "ZS=F": ("S_1", {"type": "commodities"}),     # Soybeans
    "CT=F": ("CT1", {"type": "commodities"}),     # Cotton
    "CC=F": ("CC1", {"type": "commodities"}),    # Cocoa
    "KC=F": ("KC1", {"type": "commodities"}),    # Coffee
    "SB=F": ("SB1", {"type": "commodities"}),    # Sugar
    "OJ=F": ("JO1", {"type": "commodities"}),    # Orange Juice
    # Livestock
    "LE=F": ("LC1", {"type": "commodities"}),    # Live Cattle
    "HE=F": ("LH1", {"type": "commodities"}),    # Lean Hogs
    # US Stocks — explicit mapping (same symbol on TD)
    "AAPL": ("AAPL", {}),
    "TSLA": ("TSLA", {}),
    "MSFT": ("MSFT", {}),
    "AMZN": ("AMZN", {}),
    # ETFs — standard US equity symbols, work as-is on TD
    "SPY": ("SPY", {}), "QQQ": ("QQQ", {}),
    "USO": ("USO", {}), "GLD": ("GLD", {}),
    "SLV": ("SLV", {}), "CORN": ("CORN", {}),
    "WEAT": ("WEAT", {}),
    "URA": ("URA", {}),
}

# Tickers known to not work on Twelve Data — skip to yfinance directly.
# Indices are not available on TD free tier (404 or resolve to ETFs).
# DXY : pas exposé par TD Grow → forcer yfinance via blacklist (DX-Y.NYB côté yf).
_td_blacklist: set[str] = {
    "^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX",   # US indices — not on TD free tier
    "^FCHI", "^GDAXI", "^N225",                  # EU/JP indices — 404 on TD
    "^FTSE",                                      # FTSE — resolves to ETF (~14$)
    "DX-Y.NYB",                                  # DXY US Dollar Index — TD KO, yf OK
}
_blacklist_lock = threading.Lock()


def _map_ticker(yf_ticker: str) -> Optional[tuple[str, dict]]:
    """Map yfinance ticker to Twelve Data (symbol, params). None if blacklisted."""
    with _blacklist_lock:
        if yf_ticker in _td_blacklist:
            return None
    if yf_ticker in _TICKER_MAP:
        return _TICKER_MAP[yf_ticker]
    # Dynamic mapping for unlisted Paris stocks
    if yf_ticker.endswith(".PA"):
        return (yf_ticker.replace(".PA", ""), {"mic_code": "XPAR"})
    # Futures not in _TICKER_MAP: don't guess — fall back to yfinance
    if yf_ticker.endswith("=F") or ".CBT" in yf_ticker:
        return None
    return (yf_ticker, {})


def _blacklist_ticker(yf_ticker: str) -> None:
    """Add ticker to blacklist after failure (unknown symbol on TD)."""
    with _blacklist_lock:
        _td_blacklist.add(yf_ticker)
    logger.info("TD blacklist: added %s (will use yfinance)", yf_ticker)


# ── Rate limiter ──────────────────────────────────────────────────

def _try_rate_limit() -> bool:
    """Try to acquire a rate limit slot. Returns True if allowed, False otherwise."""
    with _rate_lock:
        now = time.monotonic()
        while _request_times and now - _request_times[0] > 60:
            _request_times.popleft()
        if len(_request_times) >= _TD_RPM:
            return False
        _request_times.append(now)
        return True


# ── Cache ─────────────────────────────────────────────────────────

_CACHE_MISS = object()


def _cache_get_or_miss(key: str) -> Any:
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return _CACHE_MISS
        expiry, val = entry
        if time.monotonic() > expiry:
            del _cache[key]
            return _CACHE_MISS
        return val


def _cache_set(key: str, value: Any, ttl: float) -> None:
    with _cache_lock:
        _cache[key] = (time.monotonic() + ttl, value)


# ── Twelve Data API ───────────────────────────────────────────────

def _td_request(endpoint: str, params: dict, yf_ticker: Optional[str] = None) -> Optional[dict]:
    """Make a rate-limited request to Twelve Data API.

    Returns parsed JSON or None on failure.
    Pass yf_ticker to auto-blacklist on 'not found' errors.
    """
    if not td_available() or http_req is None:
        return None
    if not _try_rate_limit():
        logger.debug("TD rate limited, falling back to yfinance")
        return None

    params = dict(params)
    params["apikey"] = _twelve_key()
    try:
        resp = http_req.get(
            f"{TD_BASE}/{endpoint}",
            params=params,
            timeout=TD_TIMEOUT,
        )
        if resp.status_code == 429:
            logger.warning("Twelve Data 429 rate limit hit")
            return None
        if resp.status_code != 200:
            logger.debug("TD %s HTTP %d: %s", endpoint, resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        if isinstance(data, dict) and data.get("status") == "error":
            msg = data.get("message", "")
            if "not found" in msg.lower() or "not available" in msg.lower():
                if yf_ticker:
                    _blacklist_ticker(yf_ticker)
                logger.info("TD symbol not found (blacklisted=%s): %s", yf_ticker or "?", msg[:120])
                return None
            logger.debug("TD %s API error: %s", endpoint, msg[:200])
            return None
        return data
    except Exception as exc:
        logger.debug("TD %s request failed: %s", endpoint, exc)
        return None


def _td_values_to_dataframe(values: list[dict], tz: Optional[str] = None):
    """Convert Twelve Data 'values' array to yfinance-compatible DataFrame.

    TD returns newest-first; we reverse to oldest-first (yfinance convention).
    Columns: Open, High, Low, Close, Volume (capitalized, matching yfinance).
    """
    if pd is None or not values:
        return pd.DataFrame() if pd is not None else None

    rows = []
    for v in reversed(values):
        rows.append({
            "Open": float(v["open"]),
            "High": float(v["high"]),
            "Low": float(v["low"]),
            "Close": float(v["close"]),
            "Volume": int(v.get("volume", 0) or 0),
        })

    datetimes = [v["datetime"] for v in reversed(values)]
    try:
        idx = pd.to_datetime(datetimes)
    except Exception:
        idx = pd.to_datetime(datetimes, format="mixed")

    if tz:
        try:
            idx = idx.tz_localize(tz)
        except TypeError:
            try:
                idx = idx.tz_convert(tz)
            except Exception:
                pass
        except Exception:
            pass

    df = pd.DataFrame(rows, index=idx)
    df.index.name = "Date"
    return df


# ── yfinance fallback helpers ─────────────────────────────────────

def _yf_history(ticker: str, period: str = "25d", interval: str = "1d"):
    """Fetch history via yfinance (fallback)."""
    try:
        import yfinance as yf  # type: ignore
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        if df is not None and not df.empty:
            return df
    except Exception as exc:
        logger.debug("yfinance fallback failed for %s: %s", ticker, exc)
    return None


def _yf_history_range(ticker: str, start: str, end: str, interval: str = "1d"):
    try:
        import yfinance as yf  # type: ignore
        df = yf.Ticker(ticker).history(start=start, end=end, interval=interval)
        if df is not None and not df.empty:
            return df
    except Exception as exc:
        logger.debug("yfinance range fallback failed for %s: %s", ticker, exc)
    return None


# ── Interval mapping ──────────────────────────────────────────────

def _td_interval_to_yf(td_interval: str) -> str:
    mapping = {
        "1day": "1d", "1week": "1wk", "1month": "1mo",
        "1h": "1h", "4h": "1h",
        "30min": "30m", "15min": "15m", "5min": "5m", "1min": "1m",
    }
    return mapping.get(td_interval, "1d")


# ══════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════

def fetch_history(ticker: str, period_days: int = 25, interval: str = "1day"):
    """Fetch OHLCV history. Returns yfinance-compatible DataFrame or None.

    Primary: Twelve Data. Fallback: yfinance.
    Args:
        ticker: yfinance-format ticker (e.g., "^GSPC", "CL=F", "MC.PA")
        period_days: Number of data points to fetch
        interval: TD interval format — "1day", "1h", "4h", etc.
    """
    _maybe_purge_cache()
    cache_key = f"hist:{ticker}:{period_days}:{interval}"
    cached = _cache_get_or_miss(cache_key)
    if cached is not _CACHE_MISS:
        return cached

    df = None
    ttl = CACHE_TTL_SHORT if period_days <= 5 else CACHE_TTL_MEDIUM

    mapping = _map_ticker(ticker)
    if mapping and td_available():
        td_sym, extra_params = mapping
        params = {
            "symbol": td_sym,
            "interval": interval,
            "outputsize": period_days,
            **extra_params,
        }
        data = _td_request("time_series", params, yf_ticker=ticker)
        if data and "values" in data:
            tz = data.get("meta", {}).get("exchange_timezone")
            df = _td_values_to_dataframe(data["values"], tz)
            if df is not None and not df.empty:
                logger.debug("TD fetch OK: %s (%s) → %d bars", ticker, td_sym, len(df))
                _cache_set(cache_key, df, ttl)
                return df

    yf_period = f"{period_days}d" if period_days <= 59 else f"{(period_days // 30) + 1}mo"
    yf_interval = _td_interval_to_yf(interval)
    df = _yf_history(ticker, period=yf_period, interval=yf_interval)
    if df is not None:
        logger.debug("yfinance fetch OK: %s → %d bars (TD unavailable)", ticker, len(df))
    _cache_set(cache_key, df, ttl)
    return df


def fetch_history_range(ticker: str, start, end, interval: str = "1h"):
    """Fetch OHLCV for a date range. Returns yfinance-compatible DataFrame."""
    start_str = str(start)
    end_str = str(end)
    cache_key = f"range:{ticker}:{start_str}:{end_str}:{interval}"
    cached = _cache_get_or_miss(cache_key)
    if cached is not _CACHE_MISS:
        return cached

    df = None
    mapping = _map_ticker(ticker)
    if mapping and td_available():
        td_sym, extra_params = mapping
        params = {
            "symbol": td_sym,
            "interval": interval,
            "start_date": start_str,
            "end_date": end_str,
            **extra_params,
        }
        data = _td_request("time_series", params, yf_ticker=ticker)
        if data and "values" in data:
            tz = data.get("meta", {}).get("exchange_timezone")
            df = _td_values_to_dataframe(data["values"], tz)
            if df is not None and not df.empty:
                _cache_set(cache_key, df, CACHE_TTL_LONG)
                return df

    yf_interval = _td_interval_to_yf(interval)
    df = _yf_history_range(ticker, start=start_str, end=end_str, interval=yf_interval)
    _cache_set(cache_key, df, CACHE_TTL_LONG)
    return df


def fetch_history_batch(tickers: list[str], period_days: int = 2, interval: str = "1day") -> dict:
    """Fetch history for multiple tickers efficiently."""
    result: dict = {}
    uncached = []
    for t in tickers:
        cache_key = f"hist:{t}:{period_days}:{interval}"
        cached = _cache_get_or_miss(cache_key)
        if cached is not _CACHE_MISS:
            if cached is not None:
                result[t] = cached
        else:
            uncached.append(t)

    if not uncached:
        return result

    td_groups: dict[str, list[tuple[str, str]]] = {}
    yf_only: list[str] = []

    for t in uncached:
        mapping = _map_ticker(t)
        if mapping and td_available():
            td_sym, extra = mapping
            param_key = str(sorted(extra.items()))
            td_groups.setdefault(param_key, []).append((t, td_sym))
        else:
            yf_only.append(t)

    for param_key, ticker_pairs in td_groups.items():
        first_yf = ticker_pairs[0][0]
        mapping = _map_ticker(first_yf)
        extra = mapping[1] if mapping else {}
        td_syms = [td_sym for _, td_sym in ticker_pairs]
        td_to_yf = {td_sym: yf_t for yf_t, td_sym in ticker_pairs}
        params = {
            "symbol": ",".join(td_syms),
            "interval": interval,
            "outputsize": period_days,
            **extra,
        }
        data = _td_request("time_series", params)

        if data:
            if len(td_syms) == 1:
                td_sym = td_syms[0]
                yf_t = td_to_yf[td_sym]
                if "values" in data:
                    tz = data.get("meta", {}).get("exchange_timezone")
                    df = _td_values_to_dataframe(data["values"], tz)
                    if df is not None and not df.empty:
                        result[yf_t] = df
                        _cache_set(f"hist:{yf_t}:{period_days}:{interval}", df, CACHE_TTL_SHORT)
                    else:
                        yf_only.append(yf_t)
                else:
                    yf_only.append(yf_t)
            else:
                for td_sym in td_syms:
                    yf_t = td_to_yf[td_sym]
                    sym_data = data.get(td_sym, {})
                    if isinstance(sym_data, dict) and "values" in sym_data:
                        tz = sym_data.get("meta", {}).get("exchange_timezone")
                        df = _td_values_to_dataframe(sym_data["values"], tz)
                        if df is not None and not df.empty:
                            result[yf_t] = df
                            _cache_set(f"hist:{yf_t}:{period_days}:{interval}", df, CACHE_TTL_SHORT)
                        else:
                            yf_only.append(yf_t)
                    else:
                        yf_only.append(yf_t)
        else:
            for _, td_sym in ticker_pairs:
                yf_only.append(td_to_yf[td_sym])

    for t in yf_only:
        yf_period = f"{period_days}d"
        yf_interval = _td_interval_to_yf(interval)
        df = _yf_history(t, period=yf_period, interval=yf_interval)
        if df is not None:
            result[t] = df
            _cache_set(f"hist:{t}:{period_days}:{interval}", df, CACHE_TTL_SHORT)

    return result


def fetch_quote(ticker: str, bypass_cache: bool = False) -> Optional[dict]:
    """Fetch real-time quote (price + intraday range)."""
    cache_key = f"quote:{ticker}"
    if not bypass_cache:
        cached = _cache_get_or_miss(cache_key)
        if cached is not _CACHE_MISS:
            return cached

    result = None
    mapping = _map_ticker(ticker)
    if mapping and td_available():
        td_sym, extra_params = mapping
        params = {"symbol": td_sym, **extra_params}
        quote_data = _td_request("quote", params, yf_ticker=ticker)
        if quote_data and "close" in quote_data:
            try:
                price = float(quote_data.get("close", 0))
                high = float(quote_data.get("high", price))
                low = float(quote_data.get("low", price))
                rt_price = fetch_price(ticker, bypass_cache=bypass_cache)
                if rt_price and rt_price > 0:
                    price = rt_price
                if price > 0 and high > low:
                    intraday_range_pct = (high - low) / price * 100
                    result = {
                        "price": price,
                        "high": high,
                        "low": low,
                        "intraday_range_pct": round(intraday_range_pct, 4),
                    }
            except (ValueError, KeyError):
                pass

    if result is None:
        try:
            df = fetch_history(ticker, period_days=5, interval="1day")
            if df is not None and not df.empty:
                price = float(df["Close"].iloc[-1])
                if price > 0:
                    ranges = []
                    for _, row in df.iterrows():
                        h, l = float(row["High"]), float(row["Low"])
                        if h > 0 and l > 0:
                            ranges.append((h - l) / price * 100)
                    avg_range = sum(ranges) / len(ranges) if ranges else 0
                    result = {
                        "price": price,
                        "intraday_range_pct": round(avg_range, 4),
                    }
        except Exception:
            pass

    _cache_set(cache_key, result, CACHE_TTL_SHORT)
    return result


def fetch_price(ticker: str, bypass_cache: bool = False) -> Optional[float]:
    """Fetch current real-time price for a ticker.

    Uses Twelve Data /price endpoint (real-time last trade). Falls back to
    yfinance if TD unavailable.
    """
    cache_key = f"price:{ticker}"
    if not bypass_cache:
        cached = _cache_get_or_miss(cache_key)
        if cached is not _CACHE_MISS:
            return cached

    price = None
    mapping = _map_ticker(ticker)
    if mapping and td_available():
        td_sym, extra_params = mapping
        params = {"symbol": td_sym, **extra_params}
        data = _td_request("price", params, yf_ticker=ticker)
        if data and "price" in data:
            try:
                price = float(data["price"])
                if price <= 0:
                    price = None
            except (ValueError, TypeError):
                price = None

    if price is None:
        try:
            import yfinance as yf  # type: ignore
            t = yf.Ticker(ticker)
            info = t.fast_info if hasattr(t, "fast_info") else t.info
            price = float(info.get("lastPrice") or info.get("regularMarketPrice") or 0)
            if price <= 0:
                price = None
        except Exception:
            price = None

    if price is None:
        quote = fetch_quote(ticker, bypass_cache=bypass_cache)
        if quote and "price" in quote:
            price = quote["price"]
            if price is not None and price <= 0:
                price = None

    _cache_set(cache_key, price, CACHE_TTL_SHORT)
    return price


# ── Price validation (hardcoded ranges) ───────────────────────────
_price_reference: dict[str, float] = {}
_price_ref_lock = threading.Lock()
_MAX_PRICE_DEVIATION = 0.50

_PRICE_RANGES: dict[str, tuple[float, float]] = {
    # Commodities
    "CC=F": (500, 15000), "KC=F": (50, 1000),
    "ZW=F": (200, 2000), "ZC=F": (150, 1500), "ZS=F": (400, 3000),
    "HG=F": (1.0, 20.0),
    "CL=F": (20, 250), "BZ=F": (20, 250), "NG=F": (0.5, 20.0),
    "GC=F": (1000, 15000), "SI=F": (10, 250),
    "PL=F": (400, 5000), "PA=F": (300, 5000),
    "SB=F": (3, 50), "CT=F": (20, 200), "OJ=F": (50, 800),
    "LE=F": (80, 500), "HE=F": (30, 250),
    # Indices
    "^GSPC": (2000, 15000), "^DJI": (15000, 80000),
    "^IXIC": (5000, 40000), "^RUT": (800, 5000),
    "^FCHI": (3000, 15000), "^GDAXI": (8000, 40000),
    "^FTSE": (4000, 15000), "^N225": (15000, 80000),
    # Forex
    "EURUSD=X": (0.7, 1.6), "EUR=X": (0.7, 1.6),
    "USDJPY=X": (80, 200), "JPY=X": (80, 200),
    "GBPUSD=X": (0.9, 1.8), "USDCHF=X": (0.6, 1.4),
    "AUDUSD=X": (0.4, 1.1), "USDCNH=X": (5.0, 10.0),
    "EURJPY=X": (80, 250),
    # Paris stocks
    "MC.PA": (200, 2000), "OR.PA": (100, 1000), "AI.PA": (50, 500),
    "SAN.PA": (30, 300), "BNP.PA": (20, 200), "TTE.PA": (20, 200),
    "RMS.PA": (500, 5000),
    # US Stocks
    "AAPL": (50, 500), "MSFT": (100, 1000),
    "TSLA": (50, 1500), "AMZN": (50, 500),
    "URA": (5, 100),
    "^VIX": (5, 100),
    # DXY
    "DX-Y.NYB": (70, 130),
}


def validate_price(ticker: str, price: Optional[float]) -> tuple[bool, str]:
    """Validate a price against hardcoded ranges + reference."""
    if price is None or not math.isfinite(price) or price <= 0:
        return False, f"Invalid price: {price}"

    price_range = _PRICE_RANGES.get(ticker)
    if price_range:
        low, high = price_range
        if price < low or price > high:
            return False, (
                f"Price out of range: {ticker} price={price} expected [{low}, {high}]"
            )

    with _price_ref_lock:
        ref = _price_reference.get(ticker)

    if ref is None:
        _update_price_reference(ticker, price)
        return True, "first_price"

    deviation = abs(price - ref) / ref
    if deviation > _MAX_PRICE_DEVIATION:
        return False, (
            f"Price anomaly: {ticker} price={price} vs reference={ref} "
            f"(deviation={deviation:.1%} > {_MAX_PRICE_DEVIATION:.0%})"
        )

    _update_price_reference(ticker, price)
    return True, "ok"


def _update_price_reference(ticker: str, price: float) -> None:
    with _price_ref_lock:
        _price_reference[ticker] = price


def fetch_price_validated(ticker: str) -> Optional[float]:
    """Fetch current price with sanity-check + yfinance cross-check on anomaly."""
    price = fetch_price(ticker)
    if price is None:
        return None

    is_valid, reason = validate_price(ticker, price)
    if is_valid:
        return price

    logger.warning("Price validation failed: %s — cross-checking with yfinance", reason)
    try:
        import yfinance as yf  # type: ignore
        t = yf.Ticker(ticker)
        h = t.history(period="5d")
        if not h.empty:
            yf_price = float(h["Close"].iloc[-1])
            if yf_price > 0:
                yf_deviation = abs(price - yf_price) / yf_price
                if yf_deviation < 0.10:
                    _update_price_reference(ticker, price)
                    return price
                else:
                    _update_price_reference(ticker, yf_price)
                    return yf_price
    except Exception as exc:
        logger.warning("yfinance cross-check failed for %s: %s", ticker, exc)

    logger.error("REJECTED price for %s: %s — no valid cross-check available", ticker, reason)
    return None


def seed_price_references() -> None:
    """No-op pour notre projet : pas de liste ASSETS centralisée comme côté Finance.
    Les références se construisent au fil des fetch_price_validated()."""
    logger.debug("seed_price_references: no-op (pas de ASSETS dans ce projet)")


def fetch_intraday(ticker: str, period: str = "5d", interval: str = "1h"):
    """Fetch intraday OHLCV data — wrapper autour de fetch_history."""
    period_map = {"1d": 1, "2d": 2, "5d": 5, "7d": 7, "10d": 10, "30d": 30}
    period_days = period_map.get(period, 5)
    return fetch_history(ticker, period_days=period_days, interval=interval)


def get_provider_status() -> dict:
    """Return status info about the market data provider for health checks."""
    with _blacklist_lock:
        bl_count = len(_td_blacklist)
    with _rate_lock:
        now = time.monotonic()
        recent = sum(1 for t in _request_times if now - t <= 60)
    with _cache_lock:
        cache_size = len(_cache)

    return {
        "primary": "twelve_data" if td_available() else "yfinance",
        "twelve_data_configured": td_available(),
        "td_requests_last_minute": recent,
        "td_rate_limit": _TD_RPM,
        "td_blacklisted_tickers": bl_count,
        "cache_entries": cache_size,
    }
