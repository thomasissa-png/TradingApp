"""H-C — Opening Range Breakout (ORB) 5/15 min.

Logique : les N premières minutes après l'ouverture définissent un range
d'ancrage. Une cassure au-dessus du high (BUY) ou en dessous du low (SELL)
initie un mouvement directionnel.

Spec : docs/analytics/edge-rnd-report.md §3 H-C.

Sous-jacents wave 1 : DAX, CAC40, EuroStoxx50.
Heure ouverture EU : 8h00 CET / 7h00 UTC (heure de mesure du range).
Signal envoyé à 8h45 CET au plus tard (contrainte persona Thomas).
"""

from __future__ import annotations

from datetime import time

import pandas as pd


class H_C_ORB:
    """Opening Range Breakout strategy.

    Paramètres :
        orb_minutes : 5 ou 15 (durée fenêtre de range)
        tp_multiple : multiplicateur du range pour TP (défaut 1.5)
        volume_filter : ratio volume vs moyenne mobile (1.0 = pas de filtre)
        open_hour_utc : heure ouverture marché en UTC (défaut 7 = 8h CET hiver,
                        9h CET été — à ajuster pour DST en runner)
    """

    edge_id: str = "H-C-ORB"

    def __init__(self) -> None:
        self.signal_cutoff_utc = time(7, 45)  # 8h45 CET (contrainte Thomas)

    def generate_signals(
        self,
        df: pd.DataFrame,
        params: dict[str, float | int],
    ) -> pd.DataFrame:
        """Génère 1 signal par jour de trading (BUY/SELL/NONE).

        Stratégie :
        1. Pour chaque jour, identifier la fenêtre ORB (open .. open+orb_minutes).
        2. Calculer range_high = max(high) et range_low = min(low) sur la fenêtre.
        3. Identifier la 1ère bougie après ORB qui casse range_high → BUY,
           ou casse range_low → SELL. Cassure doit avoir lieu avant signal_cutoff.
        4. Si pas de cassure avant cutoff → NONE.
        """
        orb_minutes = int(params.get("orb_minutes", 15))
        tp_multiple = float(params.get("tp_multiple", 1.5))
        open_hour_utc = int(params.get("open_hour_utc", 7))

        if df.empty:
            return _empty_signals_df()

        signals: list[dict[str, object]] = []

        # Group par date
        df_local = df.copy()
        df_local["date"] = df_local.index.date
        for trade_date, day_df in df_local.groupby("date"):
            signal = _process_orb_day(
                day_df=day_df,
                orb_minutes=orb_minutes,
                tp_multiple=tp_multiple,
                open_hour_utc=open_hour_utc,
                signal_cutoff_utc=self.signal_cutoff_utc,
            )
            signal["timestamp"] = pd.Timestamp(trade_date)
            signals.append(signal)

        if not signals:
            return _empty_signals_df()
        result = pd.DataFrame(signals).set_index("timestamp")
        return result


def _process_orb_day(
    day_df: pd.DataFrame,
    orb_minutes: int,
    tp_multiple: float,
    open_hour_utc: int,
    signal_cutoff_utc: time,
) -> dict[str, object]:
    """Traite un jour de données et retourne un signal."""
    # Filtrer les bougies à partir de l'ouverture marché
    day_df = day_df[day_df.index.time >= time(open_hour_utc, 0)]
    if day_df.empty:
        return _no_signal("Pas de données après ouverture marché")

    open_ts = day_df.index[0]
    orb_end_ts = open_ts + pd.Timedelta(minutes=orb_minutes)
    orb_window = day_df[day_df.index < orb_end_ts]
    if len(orb_window) < 2:
        return _no_signal(f"Fenêtre ORB {orb_minutes}min vide")

    range_high = float(orb_window["high"].max())
    range_low = float(orb_window["low"].min())
    range_width = range_high - range_low
    if range_width <= 0:
        return _no_signal("Range ORB nul (marché plat)")

    # Bougies post-ORB jusqu'au cutoff
    post_orb = day_df[
        (day_df.index >= orb_end_ts) & (day_df.index.time <= signal_cutoff_utc)
    ]
    if post_orb.empty:
        return _no_signal("Pas de bougie post-ORB avant cutoff 8h45")

    # 1ère bougie qui casse range_high (BUY) ou range_low (SELL)
    for ts, candle in post_orb.iterrows():
        close_price = float(candle["close"])
        if close_price > range_high:
            entry = close_price
            sl = range_low
            tp = entry + (entry - sl) * tp_multiple
            return {
                "direction": "BUY",
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "raison": f"ORB break UP @ {ts.time()} > {range_high:.2f}",
            }
        if close_price < range_low:
            entry = close_price
            sl = range_high
            tp = entry - (sl - entry) * tp_multiple
            return {
                "direction": "SELL",
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "raison": f"ORB break DOWN @ {ts.time()} < {range_low:.2f}",
            }
    return _no_signal("Pas de cassure ORB avant cutoff")


def _no_signal(reason: str) -> dict[str, object]:
    return {
        "direction": "NONE",
        "entry": float("nan"),
        "sl": float("nan"),
        "tp": float("nan"),
        "raison": reason,
    }


def _empty_signals_df() -> pd.DataFrame:
    return pd.DataFrame(
        columns=["direction", "entry", "sl", "tp", "raison"],
        index=pd.DatetimeIndex([], name="timestamp"),
    )
