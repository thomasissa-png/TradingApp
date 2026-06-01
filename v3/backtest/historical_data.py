"""TradingApp v3 — Couche données historiques pour le backtest quant.

Garantie centrale : ZÉRO LOOK-AHEAD. La fonction `series_asof(ticker, date, lookback_days)`
renvoie UNIQUEMENT les barres OHLCV strictement antérieures à `date` (close du jour
`date - 1` inclus, close du jour `date` EXCLU). C'est le point critique du backtest.

Source : yfinance (gratuit, profondeur 5+ ans). En CI / prod, on basculerait sur
Twelve Data via `v3/scripts/market_data.fetch_history` — l'API de cette couche
reste la même.

Tickers couverts v1 (4 actifs liquides à historique propre) :
- ^GSPC (S&P 500), ^IXIC (Nasdaq), GC=F (Or), CL=F (Pétrole WTI)

Tickers v2 prévus : ^FCHI, ^VIX, EURUSD=X, BZ=F, SI=F, HG=F, ZW=F, KC=F, CC=F.

COT / FRED non câblés en v1 → critères correspondants marqués n/a (poids effectif 0)
côté backtest. Documenté dans REPORT.md.
"""

from __future__ import annotations

import logging
import warnings
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("backtest.historical_data")

# Cache disque optionnel pour éviter de spammer yfinance pendant le dev.
CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Tickers couverts
# ---------------------------------------------------------------------------

TICKERS_V1 = ["^GSPC", "^IXIC", "GC=F", "CL=F"]

# Tickers v2 (chargeables mais hors verdict v1 — pour extension future)
TICKERS_V2_EXTENSION = ["^FCHI", "^VIX", "EURUSD=X", "BZ=F", "SI=F", "HG=F", "ZW=F", "KC=F", "CC=F"]

# Mapping ticker → nom fiche v3 (utilisé par le moteur backtest pour charger la fiche)
TICKER_TO_FICHE = {
    "^GSPC": "sp500",
    "^IXIC": "nasdaq",
    "GC=F": "or",
    "CL=F": "petrole",   # fiche pétrole = ticker_principal BZ=F (Brent) côté live ;
                          # en backtest on utilise CL=F (WTI) qui a un historique
                          # plus propre sur yfinance gratuit. Documenté dans REPORT.md.
    "^FCHI": "cac40",
    "^VIX": "vix",
    "EURUSD=X": "eurusd",
    "BZ=F": "petrole",
    "SI=F": "argent",
    "HG=F": "cuivre",
    "ZW=F": "ble",
    "KC=F": "cafe",
    "CC=F": "cacao",
}


# ---------------------------------------------------------------------------
# Fetcher yfinance
# ---------------------------------------------------------------------------

def _fetch_yfinance_full(ticker: str, start: str = "2020-01-01", end: Optional[str] = None):
    """Récupère TOUT l'historique disponible entre start et end. Cache disque CSV.

    Retourne un DataFrame pandas indexé par date (tz-naive, normalisé à minuit UTC),
    avec colonnes ['Open', 'High', 'Low', 'Close', 'Volume'].
    """
    import pandas as pd  # lazy
    import yfinance as yf  # lazy

    end = end or (date.today() + timedelta(days=1)).isoformat()
    cache_file = CACHE_DIR / f"{ticker.replace('=', '_').replace('^', 'idx_')}__{start}__{end}.csv"
    if cache_file.exists():
        try:
            df = pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
            if len(df) > 10:
                return df
        except Exception:  # noqa: BLE001
            pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = yf.download(
            ticker, start=start, end=end, progress=False,
            auto_adjust=False, threads=False,
        )
    if df is None or len(df) == 0:
        logger.warning("yfinance vide pour ticker=%s start=%s end=%s", ticker, start, end)
        return None

    # yfinance renvoie un MultiIndex (Field, Ticker) → on aplatit
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = [c[0] for c in df.columns]

    # Garde uniquement les colonnes utiles, dans l'ordre
    cols_needed = ["Open", "High", "Low", "Close", "Volume"]
    for c in cols_needed:
        if c not in df.columns:
            logger.warning("colonne %s absente pour ticker=%s", c, ticker)
            return None
    df = df[cols_needed].copy()
    # Normalise l'index à minuit (tz-naive), enlève les NaN
    df.index = pd.to_datetime(df.index).normalize()
    df = df.dropna(subset=["Close"])

    try:
        df.to_csv(cache_file, index_label="Date")
    except Exception as e:  # noqa: BLE001
        logger.warning("cache write KO : %s", e)
    return df


# Mémoize en RAM par ticker (le DataFrame complet) — évite N relectures fichier
_RAM_CACHE: Dict[str, object] = {}


def _get_full_df(ticker: str, start: str = "2020-01-01", end: Optional[str] = None):
    key = f"{ticker}|{start}|{end}"
    if key not in _RAM_CACHE:
        _RAM_CACHE[key] = _fetch_yfinance_full(ticker, start=start, end=end)
    return _RAM_CACHE[key]


# ---------------------------------------------------------------------------
# API publique : series_asof + close_at + future_return
# ---------------------------------------------------------------------------

def _to_date(d) -> "date":
    """Convertit str/datetime/date → date (naïve)."""
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.fromisoformat(d).date()
    raise TypeError(f"date type non supporté : {type(d)}")


def series_asof(ticker: str, as_of: "date | str | datetime",
                lookback_days: int = 300,
                start: str = "2020-01-01"):
    """Retourne le DataFrame OHLCV pour `ticker` se terminant STRICTEMENT AVANT `as_of`.

    Garantie no look-ahead : le dernier point retourné est celui du dernier
    jour de trading strictement antérieur à `as_of`. La close du jour `as_of`
    n'est JAMAIS visible.

    Args:
        ticker : symbole yfinance (ex: "^GSPC", "GC=F")
        as_of : date "présent" du backtest. La fenêtre se termine AVANT.
        lookback_days : nombre de jours calendaires de fenêtre (≈ 252j de trading
            si lookback_days=365). Sert à fournir assez de données pour z-score,
            RSI, etc.

    Returns:
        DataFrame pandas avec colonnes [Open, High, Low, Close, Volume],
        index = dates strictement < as_of, OU None si données indisponibles.
    """
    asof_d = _to_date(as_of)
    df_full = _get_full_df(ticker, start=start)
    if df_full is None or len(df_full) == 0:
        return None

    # Filtre strict : index < as_of (la close du jour as_of n'est PAS visible)
    import pandas as pd  # lazy
    cutoff = pd.Timestamp(asof_d)
    window_start = pd.Timestamp(asof_d - timedelta(days=lookback_days))
    df = df_full[(df_full.index < cutoff) & (df_full.index >= window_start)]
    if len(df) == 0:
        return None
    return df.copy()


def close_at(ticker: str, day: "date | str | datetime",
             start: str = "2020-01-01") -> Optional[float]:
    """Retourne la close du jour `day` (utilisé pour mesurer l'outcome après prédiction).

    Diffère de series_asof : ici on accède délibérément à un point dans le futur
    par rapport à la date de prédiction. À utiliser UNIQUEMENT pour mesurer
    l'outcome, JAMAIS pour construire les features.

    Si le jour exact n'a pas de close (weekend, férié), retourne la close du
    PROCHAIN jour de trading disponible (la mesure d'outcome utilise le close
    forward le plus proche).
    """
    day_d = _to_date(day)
    df_full = _get_full_df(ticker, start=start)
    if df_full is None or len(df_full) == 0:
        return None
    import pandas as pd  # lazy
    target = pd.Timestamp(day_d)
    # On cherche la première date >= target
    df_after = df_full[df_full.index >= target]
    if len(df_after) == 0:
        return None
    return float(df_after["Close"].iloc[0])


def future_return(ticker: str, entry_day: "date | str | datetime",
                  horizon_days: int = 1,
                  start: str = "2020-01-01") -> Optional[float]:
    """Rendement forward (close_entry → close_entry+horizon_days) en fraction.

    Convention :
    - entry_day = jour de DÉCISION (on a vu les closes < entry_day via series_asof).
    - prix d'entrée = close du PREMIER jour de trading >= entry_day.
    - prix de sortie = close du PROCHAIN jour de trading STRICTEMENT APRÈS entry_jour
      pour horizon=1 (24h), ou jour de trading >= entry+horizon_days pour 7j/1m.

    Cela élimine l'artefact weekend (sinon entry et exit tombent sur la même
    close du lundi → rendement 0).
    """
    entry_d = _to_date(entry_day)
    df_full = _get_full_df(ticker, start=start)
    if df_full is None or len(df_full) == 0:
        return None
    import pandas as pd  # lazy
    target_entry = pd.Timestamp(entry_d)
    df_at_or_after = df_full[df_full.index >= target_entry]
    if len(df_at_or_after) < 2:
        return None
    # entry = close du premier jour de trading ≥ entry_day
    entry_idx = df_at_or_after.index[0]
    p_entry = float(df_at_or_after["Close"].iloc[0])
    if p_entry == 0:
        return None
    # exit = premier jour de trading dont la distance calendaire à entry_idx
    # est >= horizon_days. Pour horizon_days=1 : NEXT trading day.
    target_exit_min = entry_idx + pd.Timedelta(days=horizon_days)
    df_exit_pool = df_full[df_full.index >= target_exit_min]
    if len(df_exit_pool) == 0:
        return None
    p_exit = float(df_exit_pool["Close"].iloc[0])
    return (p_exit - p_entry) / p_entry


# ---------------------------------------------------------------------------
# Dates de trading non-chevauchantes
# ---------------------------------------------------------------------------

def non_overlapping_trading_dates(ticker: str, start_date: "date | str", end_date: "date | str",
                                  horizon_days: int = 1) -> List["date"]:
    """Retourne la liste des dates de trading entre start_date et end_date,
    espacées d'au moins `horizon_days` (pour garantir non-chevauchement).

    Pour horizon 24h (horizon_days=1) : quotidien.
    Pour 7j (horizon_days=7) : hebdomadaire.
    Pour 1m (horizon_days=30) : mensuel.
    """
    start = _to_date(start_date)
    end = _to_date(end_date)
    df = _get_full_df(ticker)
    if df is None or len(df) == 0:
        return []
    import pandas as pd  # lazy
    df = df[(df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))]
    if len(df) == 0:
        return []
    all_dates = [d.date() for d in df.index]
    if horizon_days <= 1:
        return all_dates
    selected: List[date] = []
    last_picked: Optional[date] = None
    for d in all_dates:
        if last_picked is None or (d - last_picked).days >= horizon_days:
            selected.append(d)
            last_picked = d
    return selected


# ---------------------------------------------------------------------------
# CLI smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    test_ticker = sys.argv[1] if len(sys.argv) > 1 else "GC=F"
    test_date = sys.argv[2] if len(sys.argv) > 2 else "2024-06-15"

    print(f"\n=== Smoke test : series_asof({test_ticker}, {test_date}) ===")
    df = series_asof(test_ticker, test_date, lookback_days=400)
    if df is None:
        print("KO : aucune donnée")
        sys.exit(1)
    print(f"OK : {len(df)} barres, dernière date = {df.index[-1].date()} (cutoff = {test_date})")
    print(f"Dernière close = {float(df['Close'].iloc[-1]):.2f}")
    assert df.index[-1].date() < _to_date(test_date), "VIOLATION look-ahead !"
    print("✓ no look-ahead confirmé")

    print(f"\n=== future_return 1j ===")
    r = future_return(test_ticker, test_date, horizon_days=1)
    print(f"Rendement 1j depuis {test_date} : {r*100:.3f}%" if r is not None else "n/a")

    print(f"\n=== non_overlapping_trading_dates 2024 ===")
    dates = non_overlapping_trading_dates(test_ticker, "2024-01-01", "2024-12-31", horizon_days=1)
    print(f"Nb dates 24h en 2024 : {len(dates)} (première={dates[0]}, dernière={dates[-1]})")
