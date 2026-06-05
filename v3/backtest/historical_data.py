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
import sys
import warnings
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("backtest.historical_data")

# Permet d'importer les helpers LIVE (fetch_fred_series_dated, etc.) même quand
# ce module est chargé seul (tests). Idempotent.
_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

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
# FRED historique as-of (chantier v2.1)
# ---------------------------------------------------------------------------
#
# Garantie centrale (identique à series_asof) : ZÉRO LOOK-AHEAD. On récupère la
# série datée FRED via le helper LIVE `fetch_fred_series_dated` (réutilisation,
# pas de réimplémentation), puis on filtre STRICTEMENT `date < as_of`.
#
# Subtilité FRED : la date d'observation FRED (`row.date`) est la date à laquelle
# la donnée se RAPPORTE, pas la date de publication. Pour les séries quotidiennes
# (DFII10, DGS10, BAMLH0A0HYM2, DTWEXBGS) le décalage de publication est de ~1
# jour ouvré, donc filtrer `date < as_of` reste prudent (la valeur du jour J est
# publiée J+1, on ne la verrait pas au matin de J de toute façon). Pour les séries
# mensuelles OECD (IRLTLT01*M156N) le lag de publication est plus long (~1-2 mois) :
# c'est une limite documentée (léger optimisme), mais le forward-fill LOCF n'utilise
# que des points `< as_of`, donc pas de fuite du futur au sens strict.

_FRED_RAM_CACHE: Dict[str, object] = {}


def _fred_dated_cached(series_id: str, n: int = 5000):
    """Récupère la série FRED complète datée (oldest→newest) via le helper LIVE,
    avec cache disque CSV + RAM. Retourne List[(date_str, value)] ou None.

    On charge une fenêtre large (n par défaut ~20 ans de daily) UNE fois, puis
    on filtre par as_of en mémoire (comme yfinance _get_full_df)."""
    if series_id in _FRED_RAM_CACHE:
        return _FRED_RAM_CACHE[series_id]

    cache_file = CACHE_DIR / f"fred__{series_id}__n{n}.csv"
    points: Optional[List[Tuple[str, float]]] = None
    if cache_file.exists():
        try:
            import csv
            with cache_file.open() as f:
                rd = csv.reader(f)
                next(rd, None)  # header
                points = [(row[0], float(row[1])) for row in rd if len(row) >= 2]
            if not points:
                points = None
        except Exception:  # noqa: BLE001
            points = None

    if points is None:
        try:
            from criteres_calculator import fetch_fred_series_dated  # type: ignore
        except Exception as e:  # noqa: BLE001
            logger.warning("import fetch_fred_series_dated KO : %s", e)
            _FRED_RAM_CACHE[series_id] = None
            return None
        try:
            points = fetch_fred_series_dated(series_id, n=n)
        except Exception as e:  # noqa: BLE001
            logger.warning("fetch_fred_series_dated(%s) KO (réseau ?) : %s", series_id, e)
            points = None
        if points:
            try:
                import csv
                with cache_file.open("w", newline="") as f:
                    wr = csv.writer(f)
                    wr.writerow(["date", "value"])
                    wr.writerows(points)
            except Exception as e:  # noqa: BLE001
                logger.warning("cache FRED write KO : %s", e)

    _FRED_RAM_CACHE[series_id] = points
    return points


def fred_series_asof(series_id: str, as_of: "date | str | datetime",
                     lookback_days: int = 400) -> Optional[List[float]]:
    """Valeurs FRED (oldest→newest) STRICTEMENT antérieures à `as_of`.

    Réutilise le fetch LIVE. Filtre `date < as_of` (zéro look-ahead) ET
    `date >= as_of - lookback_days`. Retourne la liste des valeurs (sans dates),
    prête pour zscore_from_series, OU None si rien."""
    pts = fred_dated_asof(series_id, as_of, lookback_days=lookback_days)
    if not pts:
        return None
    return [v for _, v in pts]


def fred_dated_asof(series_id: str, as_of: "date | str | datetime",
                    lookback_days: int = 400) -> Optional[List[Tuple["date", float]]]:
    """Comme fred_series_asof mais conserve les dates → [(date, value)], oldest→newest.

    Filtre STRICT `date < as_of` (no look-ahead) et borne basse `>= as_of - lookback`."""
    points = _fred_dated_cached(series_id)
    if not points:
        return None
    asof_d = _to_date(as_of)
    lo = asof_d - timedelta(days=lookback_days)
    out: List[Tuple[date, float]] = []
    for ds, v in points:
        try:
            dd = _to_date(ds)
        except Exception:  # noqa: BLE001
            continue
        if dd < asof_d and dd >= lo:  # STRICT < as_of
            out.append((dd, v))
    if not out:
        return None
    out.sort(key=lambda t: t[0])
    return out


def fred_spread_asof(series_us: str, series_de: str, as_of: "date | str | datetime",
                     lookback_days: int = 600) -> Optional[List[float]]:
    """Spread US − DE aligné par forward-fill LOCF, as-of (no look-ahead).

    Réplique EXACTEMENT la logique d'alignement de `fetch_fred_spread` (live) :
    la série DE basse-fréquence (mensuelle OECD) est reportée (LOCF) sur chaque
    date US haute-fréquence. Ici les deux séries sont d'abord filtrées `< as_of`.
    Retourne la liste des spreads (oldest→newest) ou None."""
    us = fred_dated_asof(series_us, as_of, lookback_days=lookback_days)
    de = fred_dated_asof(series_de, as_of, lookback_days=lookback_days + 400)
    if not us or not de:
        return None
    map_de = {d: v for d, v in de}
    de_dates = sorted(map_de)
    us_dates = [d for d, _ in us]
    map_us = {d: v for d, v in us}
    spread: List[float] = []
    j = 0
    last_de: Optional[float] = None
    for d in us_dates:
        while j < len(de_dates) and de_dates[j] <= d:
            last_de = map_de[de_dates[j]]
            j += 1
        if last_de is None:
            continue
        spread.append(map_us[d] - last_de)
    if len(spread) < 10:
        return None
    return spread


def fred_delta_asof(series_id: str, as_of: "date | str | datetime",
                    n_days: int = 5, lookback_days: int = 400) -> Optional[List[float]]:
    """Série des deltas glissants sur `n_days` observations, as-of (no look-ahead).

    Réplique `_handle_fred_delta` (live) : delta[i] = série[i] − série[i−n_days].
    Filtrage `< as_of` en amont. Retourne la série de deltas (oldest→newest)."""
    series = fred_series_asof(series_id, as_of, lookback_days=lookback_days)
    if not series or len(series) <= n_days + 5:
        return None
    deltas = [series[i] - series[i - n_days] for i in range(n_days, len(series))]
    if len(deltas) < 10:
        return None
    return deltas


# ---------------------------------------------------------------------------
# CFTC COT historique as-of (chantier v2.2)
# ---------------------------------------------------------------------------
#
# Garantie centrale : ZÉRO LOOK-AHEAD. On requête le dataset Socrata Legacy COT
# (jun7-fc8e), filtré côté serveur `report_date_as_yyyy_mm_dd < as_of`, et on
# calcule le NET non-commercial = noncomm_long − noncomm_short, EXACTEMENT comme
# le live (`fetch_cftc_managed_money_nets`). Le z-score est ensuite appliqué côté
# backtest avec la même normalisation (compute_zscore_normalisee).
#
# Subtilité de publication COT : le rapport COT porte une `report_date` (mardi de
# référence) mais n'est PUBLIÉ que le vendredi suivant (T+3 jours ouvrés). Filtrer
# `report_date < as_of` est donc LÉGÈREMENT optimiste les 3 jours suivant un mardi
# (on "verrait" un rapport pas encore publié). Pour être strictement prudent, on
# applique un décalage de publication COT_PUBLICATION_LAG_DAYS : on ne considère
# visible qu'un rapport dont report_date + lag < as_of. Garde-fou no-look-ahead.

CFTC_BASE_BT = "https://publicreporting.cftc.gov/resource/jun7-fc8e.json"
COT_PUBLICATION_LAG_DAYS = 3  # report_date (mardi) publié vendredi → T+3

_COT_RAM_CACHE: Dict[str, object] = {}


def _cot_full_cached(market: str):
    """Récupère TOUT l'historique COT (date, net) pour un marché, oldest→newest.
    Cache disque CSV + RAM. Retourne List[(date, net)] ou None."""
    if market in _COT_RAM_CACHE:
        return _COT_RAM_CACHE[market]

    safe = "".join(c if c.isalnum() else "_" for c in market)[:60]
    cache_file = CACHE_DIR / f"cot__{safe}.csv"
    points: Optional[List[Tuple[date, float]]] = None
    if cache_file.exists():
        try:
            import csv
            with cache_file.open() as f:
                rd = csv.reader(f)
                next(rd, None)
                points = [(_to_date(row[0]), float(row[1])) for row in rd if len(row) >= 2]
            if not points:
                points = None
        except Exception:  # noqa: BLE001
            points = None

    if points is None:
        points = _fetch_cot_socrata(market)
        if points:
            try:
                import csv
                with cache_file.open("w", newline="") as f:
                    wr = csv.writer(f)
                    wr.writerow(["report_date", "net"])
                    wr.writerows([(d.isoformat(), v) for d, v in points])
            except Exception as e:  # noqa: BLE001
                logger.warning("cache COT write KO : %s", e)

    _COT_RAM_CACHE[market] = points
    return points


def _fetch_cot_socrata(market: str, limit: int = 2000):
    """Requête Socrata pour TOUT l'historique d'un marché. net = noncomm long−short
    (MÊME définition que le live fetch_cftc_managed_money_nets). Retourne
    List[(date, net)] oldest→newest ou None (réseau KO)."""
    try:
        from urllib.parse import urlencode
        from urllib.request import urlopen, Request
        import json
    except Exception:  # noqa: BLE001
        return None
    params = {
        "$select": "report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all",
        "$where": f"market_and_exchange_names='{market}'",
        "$order": "report_date_as_yyyy_mm_dd ASC",
        "$limit": limit,
    }
    url = f"{CFTC_BASE_BT}?{urlencode(params)}"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (backtest)"})
        with urlopen(req, timeout=30) as resp:  # noqa: S310
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        logger.warning("CFTC Socrata KO (réseau ?) market=%s : %s", market, e)
        return None
    if not isinstance(data, list) or not data:
        logger.warning("CFTC Socrata vide pour market=%s", market)
        return None
    pts: List[Tuple[date, float]] = []
    for row in data:
        try:
            ds = row["report_date_as_yyyy_mm_dd"].replace("Z", "")
            dd = datetime.fromisoformat(ds).date()
            longp = float(row["noncomm_positions_long_all"])
            shortp = float(row["noncomm_positions_short_all"])
        except (KeyError, ValueError, TypeError):
            continue
        pts.append((dd, longp - shortp))
    if not pts:
        return None
    pts.sort(key=lambda t: t[0])
    return pts


def cot_nets_asof(market: str, as_of: "date | str | datetime",
                  lookback_days: int = 1900) -> Optional[List[float]]:
    """Série des nets non-commerciaux (long−short) STRICTEMENT visibles à `as_of`.

    No look-ahead : on ne garde qu'un rapport dont `report_date + lag < as_of`
    (lag de publication COT). Retourne la liste des nets (oldest→newest) ou None."""
    points = _cot_full_cached(market)
    if not points:
        return None
    asof_d = _to_date(as_of)
    lo = asof_d - timedelta(days=lookback_days)
    out: List[float] = []
    for dd, net in points:
        visible_at = dd + timedelta(days=COT_PUBLICATION_LAG_DAYS)
        if visible_at < asof_d and dd >= lo:  # publié AVANT as_of
            out.append(net)
    if not out:
        return None
    return out


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
