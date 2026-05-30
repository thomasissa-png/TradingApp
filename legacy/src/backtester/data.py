"""MarketDataLoader — wrapper Twelve Data SDK + cache SQLite.

Source de vérité : docs/analytics/edge-rnd-report.md §4 + infra-audit.md.

Cache : data/market_cache.sqlite, table candles_1m.
Rate limits Twelve Data Pro Individual : 8 req/sec, 800/min (gérés par retry).

NB : pas d'appel réel API dans cette session — le code est testé via fixtures
parquet/CSV dans tests/fixtures/market/.
"""

from __future__ import annotations

import sqlite3
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

DDL_CANDLES = """
CREATE TABLE IF NOT EXISTS candles_1m (
    symbol     TEXT NOT NULL,
    timestamp  TIMESTAMP NOT NULL,
    open       REAL NOT NULL,
    high       REAL NOT NULL,
    low        REAL NOT NULL,
    close      REAL NOT NULL,
    volume     REAL NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);
"""

DDL_INDEX = (
    "CREATE INDEX IF NOT EXISTS idx_candles_symbol_ts ON candles_1m(symbol, timestamp);"
)

# Mapping interne → symbole Twelve Data (à enrichir wave 2)
SYMBOL_MAP: dict[str, str] = {
    "DAX": "DAX",
    "CAC": "CAC",
    "CAC40": "CAC",
    "ESTX50": "ESTX50",
    "EUROSTOXX50": "ESTX50",
}


class MarketDataLoader:
    """Loader OHLC 1min avec cache SQLite + retry exponentiel.

    Usage :
        loader = MarketDataLoader(cache_path=Path("data/market_cache.sqlite"))
        df = loader.load_ohlc("DAX", start=date(2024,1,1), end=date(2024,1,10))
    """

    def __init__(
        self,
        cache_path: Path,
        api_key: str | None = None,
        max_retries: int = 3,
        request_delay_ms: int = 130,  # ~7.7 req/sec, dans la limite 8/sec
    ) -> None:
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key
        self.max_retries = max_retries
        self.request_delay_ms = request_delay_ms
        self._init_cache()

    def _init_cache(self) -> None:
        """Crée table cache si absente (idempotent)."""
        with sqlite3.connect(self.cache_path) as conn:
            conn.execute(DDL_CANDLES)
            conn.execute(DDL_INDEX)
            conn.commit()

    def load_ohlc(
        self,
        symbol: str,
        start: date,
        end: date,
        timeframe: str = "1min",
    ) -> pd.DataFrame:
        """Charge OHLC pour la période. Cache hit → SELECT, cache miss → API.

        Args:
            symbol : symbole interne (ex 'DAX', 'CAC', 'ESTX50').
            start : date début (incluse).
            end : date fin (incluse).
            timeframe : intervalle Twelve Data ('1min', '5min', etc.).

        Returns:
            DataFrame indexé par DatetimeIndex UTC, colonnes
            [open, high, low, close, volume].
        """
        # 1. Tentative cache
        cached = self._load_from_cache(symbol, start, end)
        if not cached.empty and self._is_cache_complete(cached, start, end):
            return cached

        # 2. Cache incomplet : appel API + persist
        if self.api_key is None:
            # Mode test : pas de fallback API, retourne ce qui est en cache
            return cached

        api_data = self._fetch_from_api(symbol, start, end, timeframe)
        if not api_data.empty:
            self._persist_to_cache(symbol, api_data)
        return api_data

    def _load_from_cache(
        self, symbol: str, start: date, end: date
    ) -> pd.DataFrame:
        """SELECT depuis cache pour (symbol, période)."""
        query = """
            SELECT timestamp, open, high, low, close, volume
            FROM candles_1m
            WHERE symbol = ? AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        """
        start_ts = datetime.combine(start, datetime.min.time())
        end_ts = datetime.combine(end, datetime.max.time())
        with sqlite3.connect(self.cache_path) as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params=(symbol, start_ts.isoformat(), end_ts.isoformat()),
                parse_dates=["timestamp"],
            )
        if df.empty:
            return df
        df = df.set_index("timestamp")
        # Force UTC tz-aware
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        return df

    @staticmethod
    def _is_cache_complete(
        df: pd.DataFrame, start: date, end: date, min_coverage_pct: float = 0.5
    ) -> bool:
        """Heuristique : considère le cache complet si > min_coverage_pct des
        jours ouvrés ont des données.

        Pour l'usage backtester (paper R&D), 50% de couverture est suffisant
        pour ne pas refaire des appels API à chaque load. Le runner remontera
        le flag DEGRADED si trop de trous.
        """
        if df.empty:
            return False
        # Nb jours ouvrés attendus (approximation : 5/7 du calendrier)
        total_days = (end - start).days + 1
        expected_business_days = max(1, int(total_days * 5 / 7))
        actual_days = int(df.index.normalize().nunique())
        return bool(actual_days >= expected_business_days * min_coverage_pct)

    def _fetch_from_api(
        self, symbol: str, start: date, end: date, timeframe: str
    ) -> pd.DataFrame:
        """Appel Twelve Data API avec retry exponentiel.

        Note : implémentation paresseuse — instancie le client à la demande
        pour éviter import-time crash si twelvedata SDK absent.
        """
        try:
            from twelvedata import TDClient
        except ImportError as e:
            raise RuntimeError(
                "twelvedata package required for live API calls. "
                "Use cache-only mode for tests."
            ) from e

        td_symbol = SYMBOL_MAP.get(symbol.upper(), symbol)
        client = TDClient(apikey=self.api_key)
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                ts = client.time_series(
                    symbol=td_symbol,
                    interval=timeframe,
                    start_date=start.isoformat(),
                    end_date=end.isoformat(),
                    outputsize=5000,
                    timezone="UTC",
                )
                df = ts.as_pandas()
                if df is None or df.empty:
                    return _empty_ohlc()
                df = df.rename(
                    columns={
                        "open": "open",
                        "high": "high",
                        "low": "low",
                        "close": "close",
                        "volume": "volume",
                    }
                )
                df.index = pd.to_datetime(df.index, utc=True)
                # Throttle pour respecter rate limit
                time.sleep(self.request_delay_ms / 1000)
                return df[["open", "high", "low", "close", "volume"]].sort_index()
            except Exception as e:
                last_error = e
                # Backoff exponentiel : 1s, 2s, 4s
                time.sleep(2**attempt)
        raise RuntimeError(
            f"Twelve Data API failed after {self.max_retries} retries: {last_error}"
        )

    def _persist_to_cache(self, symbol: str, df: pd.DataFrame) -> None:
        """INSERT OR REPLACE en batch."""
        if df.empty:
            return
        rows: list[tuple[Any, ...]] = []
        for ts, row in df.iterrows():
            rows.append(
                (
                    symbol,
                    ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    float(row["volume"]),
                )
            )
        with sqlite3.connect(self.cache_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO candles_1m "
                "(symbol, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()


def _empty_ohlc() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["open", "high", "low", "close", "volume"],
        index=pd.DatetimeIndex([], tz="UTC", name="timestamp"),
    )


def load_fixture(fixture_path: Path) -> pd.DataFrame:
    """Helper test : charge un fixture OHLC (CSV ou Parquet selon extension).

    Format attendu : index DatetimeIndex UTC + colonnes open/high/low/close/volume.
    """
    suffix = fixture_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(fixture_path, index_col=0, parse_dates=True)
    elif suffix == ".parquet":
        df = pd.read_parquet(fixture_path)
    else:
        raise ValueError(f"Extension inconnue : {suffix} (attendu .csv ou .parquet)")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    return df
