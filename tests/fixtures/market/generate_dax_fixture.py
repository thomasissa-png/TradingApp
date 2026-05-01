"""Génère le fixture DAX 10 jours synthétique pour les tests backtester.

Usage : python tests/fixtures/market/generate_dax_fixture.py

Génère 10 jours ouvrés DAX 1min synthétique :
- Jour 1 : flat (range étroit, pas de signal ORB ni gap)
- Jour 2 : gap haussier +0.6% suivi de continuation (signal H-A BUY attendu)
- Jour 3 : gap baissier -0.7% suivi de continuation (signal H-A SELL attendu)
- Jour 4 : range ORB explicite + breakout haussier post-15min (signal H-C BUY)
- Jour 5 : range ORB + breakout baissier (signal H-C SELL)
- Jours 6-10 : mixtes avec amplitude moyenne
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT_PATH = Path(__file__).parent / "dax_10days_synthetic.csv"


def _generate_minute_bars(
    start_dt: datetime,
    n_minutes: int,
    base_price: float,
    drift: float = 0.0,
    vol_pct: float = 0.0005,
    seed: int = 42,
) -> pd.DataFrame:
    """Génère n_minutes barres OHLC à partir de start_dt avec drift/volatilité."""
    rng = np.random.default_rng(seed)
    timestamps = [start_dt + timedelta(minutes=i) for i in range(n_minutes)]
    closes = []
    price = base_price
    for _ in range(n_minutes):
        ret = drift + rng.normal(0, vol_pct)
        price = price * (1 + ret)
        closes.append(price)
    closes_arr = np.array(closes)
    opens = np.concatenate([[base_price], closes_arr[:-1]])
    highs = np.maximum(opens, closes_arr) * (1 + np.abs(rng.normal(0, vol_pct / 2, n_minutes)))
    lows = np.minimum(opens, closes_arr) * (1 - np.abs(rng.normal(0, vol_pct / 2, n_minutes)))
    volumes = rng.integers(100, 1000, n_minutes).astype(float)
    return pd.DataFrame(
        {"open": opens, "high": highs, "low": lows, "close": closes_arr, "volume": volumes},
        index=pd.DatetimeIndex(timestamps, tz="UTC", name="timestamp"),
    )


def generate_fixture() -> pd.DataFrame:
    """Génère le fixture complet 10 jours."""
    base_date = datetime(2024, 6, 3, 7, 0, 0)  # lundi 3 juin 2024 7h UTC = 9h CET
    base_price = 18000.0
    days_dfs: list[pd.DataFrame] = []

    # Jour 1 : flat (range étroit)
    day1_start = base_date
    day1 = _generate_minute_bars(day1_start, 120, base_price, drift=0.0, vol_pct=0.0001, seed=1)
    days_dfs.append(day1)
    last_close = float(day1["close"].iloc[-1])

    # Jour 2 : gap UP +0.6% + continuation haussière
    day2_start = day1_start + timedelta(days=1)
    day2_open = last_close * 1.006  # gap +0.6%
    day2 = _generate_minute_bars(day2_start, 120, day2_open, drift=0.0008, vol_pct=0.0003, seed=2)
    days_dfs.append(day2)
    last_close = float(day2["close"].iloc[-1])

    # Jour 3 : gap DOWN -0.7% + continuation baissière
    day3_start = day2_start + timedelta(days=1)
    day3_open = last_close * 0.993  # gap -0.7%
    day3 = _generate_minute_bars(
        day3_start, 120, day3_open, drift=-0.0008, vol_pct=0.0003, seed=3
    )
    days_dfs.append(day3)
    last_close = float(day3["close"].iloc[-1])

    # Jour 4 : range ORB explicite (15min) + breakout UP
    day4_start = day3_start + timedelta(days=1)
    day4_open_price = last_close * 1.0001  # quasi pas de gap
    # 15 premières min : range étroit autour de open
    orb_part = _generate_minute_bars(
        day4_start, 15, day4_open_price, drift=0.0, vol_pct=0.0002, seed=4
    )
    # Force la 16e min à casser au-dessus du high
    orb_high = float(orb_part["high"].max())
    breakout_open = orb_high * 1.001
    breakout_part = _generate_minute_bars(
        day4_start + timedelta(minutes=15),
        45,
        breakout_open,
        drift=0.0006,
        vol_pct=0.0003,
        seed=14,
    )
    day4 = pd.concat([orb_part, breakout_part])
    days_dfs.append(day4)
    last_close = float(day4["close"].iloc[-1])

    # Jour 5 : range ORB + breakout DOWN
    day5_start = day4_start + timedelta(days=1)
    day5_open_price = last_close * 1.0001
    orb_part = _generate_minute_bars(
        day5_start, 15, day5_open_price, drift=0.0, vol_pct=0.0002, seed=5
    )
    orb_low = float(orb_part["low"].min())
    breakdown_open = orb_low * 0.999
    breakdown_part = _generate_minute_bars(
        day5_start + timedelta(minutes=15),
        45,
        breakdown_open,
        drift=-0.0006,
        vol_pct=0.0003,
        seed=15,
    )
    day5 = pd.concat([orb_part, breakdown_part])
    days_dfs.append(day5)
    last_close = float(day5["close"].iloc[-1])

    # Jours 6-10 : mixtes (saute samedi/dimanche)
    next_dt = day5_start + timedelta(days=3)  # passe au lundi suivant
    for day_idx in range(5):
        day_start = next_dt + timedelta(days=day_idx)
        # Petit gap aléatoire
        rng = np.random.default_rng(100 + day_idx)
        gap_pct = float(rng.uniform(-0.004, 0.004))
        day_open = last_close * (1 + gap_pct)
        drift = float(rng.uniform(-0.0004, 0.0004))
        df = _generate_minute_bars(
            day_start, 120, day_open, drift=drift, vol_pct=0.0003, seed=100 + day_idx
        )
        days_dfs.append(df)
        last_close = float(df["close"].iloc[-1])

    return pd.concat(days_dfs).sort_index()


if __name__ == "__main__":
    df = generate_fixture()
    df.to_csv(OUTPUT_PATH)
    print(f"[OK] Fixture créée : {OUTPUT_PATH}")
    print(f"     {len(df)} bougies, {df.index.normalize().nunique()} jours")
    print(f"     Période : {df.index.min()} → {df.index.max()}")
