"""H-A — Gap Follow EU Open.

Logique : si l'ouverture présente un gap > seuil % vs close veille, la
dynamique directionnelle se poursuit dans les premières minutes.

Spec : docs/analytics/edge-rnd-report.md §3 H-A.

Sous-jacents wave 1 : DAX, CAC40, EuroStoxx50.
Entrée : open + 5min (laisse retomber spread d'ouverture).
"""

from __future__ import annotations

from datetime import time

import pandas as pd


class H_A_GapFollow:
    """Gap Follow strategy.

    Paramètres :
        gap_min_pct : seuil minimum gap en pct (0.003 / 0.005 / 0.008)
        tp_multiple : multiplicateur ATR/range pour TP (défaut 1.5)
        entry_delay_minutes : minutes après open avant entrée (défaut 5)
        open_hour_utc : heure ouverture marché en UTC (défaut 7 = 8h CET)
        min_amplitude_pct : amplitude attendue minimale (tp-entry)/entry pour
            generer un signal (defaut 0.01 = 1 %). Decision Thomas 2026-05-02 :
            filtre frais turbo (spread + 1.98 € BD aller-retour + slippage).
    """

    edge_id: str = "H-A-GapFollow"

    def __init__(self) -> None:
        self.signal_cutoff_utc = time(7, 45)  # 8h45 CET

    def generate_signals(
        self,
        df: pd.DataFrame,
        params: dict[str, float | int],
    ) -> pd.DataFrame:
        """Génère 1 signal par jour.

        Stratégie :
        1. Pour chaque jour, identifier le close veille et l'open du jour.
        2. Calculer gap_pct = (open - close_prev) / close_prev.
        3. Si |gap_pct| > gap_min_pct → entrée à open + entry_delay minutes
           dans le sens du gap. SL = open précédent (close veille),
           TP = entry + sign(gap) * |entry - SL| * tp_multiple.
        4. Sinon → NONE.
        """
        gap_min_pct = float(params.get("gap_min_pct", 0.005))
        tp_multiple = float(params.get("tp_multiple", 1.5))
        entry_delay = int(params.get("entry_delay_minutes", 5))
        open_hour_utc = int(params.get("open_hour_utc", 7))
        min_amplitude_pct = float(params.get("min_amplitude_pct", 0.01))

        if df.empty:
            return _empty_signals_df()

        signals: list[dict[str, object]] = []
        df_local = df.copy()
        df_local["date"] = df_local.index.date
        prev_close: float | None = None

        # Itère par jour ordonné
        for trade_date, day_df in df_local.groupby("date"):
            signal = _process_gap_day(
                day_df=day_df,
                prev_close=prev_close,
                gap_min_pct=gap_min_pct,
                tp_multiple=tp_multiple,
                entry_delay=entry_delay,
                open_hour_utc=open_hour_utc,
                signal_cutoff_utc=self.signal_cutoff_utc,
                min_amplitude_pct=min_amplitude_pct,
            )
            signal["timestamp"] = pd.Timestamp(trade_date)
            signals.append(signal)
            # Update prev_close avec le dernier close du jour
            prev_close = float(day_df["close"].iloc[-1])

        if not signals:
            return _empty_signals_df()
        return pd.DataFrame(signals).set_index("timestamp")


def _process_gap_day(
    day_df: pd.DataFrame,
    prev_close: float | None,
    gap_min_pct: float,
    tp_multiple: float,
    entry_delay: int,
    open_hour_utc: int,
    signal_cutoff_utc: time,
    min_amplitude_pct: float = 0.01,
) -> dict[str, object]:
    """Traite un jour : check gap vs prev_close puis entrée delayed."""
    if prev_close is None or prev_close <= 0:
        return _no_signal("Pas de close veille (1er jour fixture)")

    market_open = day_df[day_df.index.time >= time(open_hour_utc, 0)]
    if market_open.empty:
        return _no_signal("Pas de données après ouverture marché")

    open_ts = market_open.index[0]
    today_open = float(market_open["open"].iloc[0])
    gap_pct = (today_open - prev_close) / prev_close

    if abs(gap_pct) < gap_min_pct:
        return _no_signal(f"Gap {gap_pct:.3%} < seuil {gap_min_pct:.3%}")

    # Trouver bougie d'entrée delayed
    entry_ts = open_ts + pd.Timedelta(minutes=entry_delay)
    entry_window = market_open[
        (market_open.index >= entry_ts)
        & (market_open.index.time <= signal_cutoff_utc)
    ]
    if entry_window.empty:
        return _no_signal("Pas de bougie d'entrée valide après delay")

    entry_candle = entry_window.iloc[0]
    entry = float(entry_candle["close"])
    if gap_pct > 0:
        # Gap haussier → BUY, SL au prev_close
        sl = prev_close
        if entry <= sl:
            return _no_signal("Gap haussier mais entry repassé sous SL")
        tp = entry + (entry - sl) * tp_multiple
        # Filtre amplitude attendue (decision Thomas 2026-05-02)
        amplitude_pct = (tp - entry) / entry if entry > 0 else 0.0
        if amplitude_pct < min_amplitude_pct:
            return _no_signal(
                f"Amplitude attendue {amplitude_pct:.2%} < seuil {min_amplitude_pct:.2%} "
                "(frais turbo non absorbes)"
            )
        return {
            "direction": "BUY",
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "raison": f"Gap UP {gap_pct:.2%} suivi (entrée +{entry_delay}min)",
        }
    # Gap baissier → SELL
    sl = prev_close
    if entry >= sl:
        return _no_signal("Gap baissier mais entry repassé au-dessus de SL")
    tp = entry - (sl - entry) * tp_multiple
    # Filtre amplitude attendue (decision Thomas 2026-05-02)
    amplitude_pct = (entry - tp) / entry if entry > 0 else 0.0
    if amplitude_pct < min_amplitude_pct:
        return _no_signal(
            f"Amplitude attendue {amplitude_pct:.2%} < seuil {min_amplitude_pct:.2%} "
            "(frais turbo non absorbes)"
        )
    return {
        "direction": "SELL",
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "raison": f"Gap DOWN {gap_pct:.2%} suivi (entrée +{entry_delay}min)",
    }


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
