"""Runner backtest CLI principal.

Usage :
    python -m src.backtester.runner --edge=H-C --assets=DAX,CAC,ESTX50 \\
        --is-start=2021-01-01 --is-end=2024-12-31 \\
        --oos-start=2025-01-01 --oos-end=2025-12-31 \\
        --output-json=docs/analytics/results/edge-H-C-results.json

Pipeline :
    1. Charge data via MarketDataLoader (cache SQLite)
    2. Grid search paramètres en IS (3-5 combos)
    3. Sélectionne meilleur paramset (Sharpe IS)
    4. Backtest OOS black-box avec params gelés
    5. Walk-forward 3 fenêtres
    6. Calcule métriques + verdict 6 conditions AND v1.1
    7. Persist résultats JSON + INSERT rnd_results SQLite
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.backtester.data import MarketDataLoader
from src.backtester.edges import H_C_ORB, EdgeStrategy, H_A_GapFollow
from src.backtester.methodology import compute_pvalue_hansen_spa
from src.backtester.metrics import (
    equity_curve_from_returns,
    max_drawdown_monthly,
    profit_factor,
    robustness_ratio,
    sharpe_ratio,
    win_rate,
)
from src.backtester.verdict import Verdict, evaluate_go_phase2

# Coûts standard (edge-rnd-report.md §2.2)
COST_BD_ROUND_TRIP = 1.98
COST_SPREAD = 0.05
COST_SLIPPAGE_PCT = 0.001
DEFAULT_POSITION_EUR = 1500.0
DEFAULT_LEVERAGE = 10.0


@dataclass
class TradeResult:
    """Résultat d'un trade simulé."""

    timestamp: pd.Timestamp
    asset: str
    direction: str
    entry: float
    sl: float
    tp: float
    exit_price: float
    exit_reason: str  # 'TP' / 'SL' / 'TIMEOUT'
    pnl_brut: float
    costs: float
    pnl_net: float


@dataclass
class BacktestStats:
    """Stats agrégées d'un backtest."""

    edge_id: str
    period_label: str  # 'IS', 'OOS', 'WF1', 'WF2', 'WF3'
    nb_trades: int
    win_rate_pct: float
    profit_factor: float
    sharpe: float
    drawdown_monthly: float
    pnl_total: float
    params: dict[str, float | int] = field(default_factory=dict)


def simulate_trades(
    signals: pd.DataFrame,
    ohlc: pd.DataFrame,
    asset: str,
    position_eur: float = DEFAULT_POSITION_EUR,
    leverage: float = DEFAULT_LEVERAGE,
    timeout_minutes: int = 60,
) -> list[TradeResult]:
    """Simule les trades depuis les signaux + OHLC suivant.

    Pour chaque signal BUY/SELL :
    - Suit OHLC à partir de l'entrée jusqu'à TP/SL/TIMEOUT
    - Calcule P&L net après coûts

    Args:
        signals : DataFrame des signaux (sortie generate_signals).
        ohlc : OHLC source (1min).
        asset : nom du sous-jacent.
        position_eur : taille position en € (défaut 1500).
        leverage : levier turbo (défaut x10).
        timeout_minutes : durée max trade en min (défaut 60).

    Returns:
        Liste TradeResult.
    """
    trades: list[TradeResult] = []
    exposure = position_eur * leverage

    for ts, signal in signals.iterrows():
        direction = str(signal["direction"])
        if direction == "NONE":
            continue
        entry = float(signal["entry"])
        sl = float(signal["sl"])
        tp = float(signal["tp"])
        if pd.isna(entry):
            continue

        # Cherche bougie d'entrée (1ère bougie >= ts dans OHLC)
        # ts dans signals = date du jour, on cherche dans ohlc le timestamp
        # qui correspond à l'entrée réelle (pour ORB c'est >= 8h45 UTC, pour
        # gap c'est open + 5min). On utilise le close de la bougie de signal.
        day_mask = ohlc.index.date == ts.date()
        day_ohlc = ohlc[day_mask]
        if day_ohlc.empty:
            continue
        # Cherche la bougie où close == entry (signal d'entrée)
        # Sinon prend la 1ère bougie après 8h45 UTC
        entry_candle_mask = day_ohlc["close"] == entry
        if entry_candle_mask.any():
            entry_idx = day_ohlc[entry_candle_mask].index[0]
        else:
            continue

        # Suit les bougies à partir d'entry_idx
        exit_window = day_ohlc[
            (day_ohlc.index > entry_idx)
            & (day_ohlc.index <= entry_idx + pd.Timedelta(minutes=timeout_minutes))
        ]
        exit_price = entry
        exit_reason = "TIMEOUT"
        for _, candle in exit_window.iterrows():
            high = float(candle["high"])
            low = float(candle["low"])
            if direction == "BUY":
                if low <= sl:
                    exit_price = sl
                    exit_reason = "SL"
                    break
                if high >= tp:
                    exit_price = tp
                    exit_reason = "TP"
                    break
            else:  # SELL
                if high >= sl:
                    exit_price = sl
                    exit_reason = "SL"
                    break
                if low <= tp:
                    exit_price = tp
                    exit_reason = "TP"
                    break
        else:
            # Boucle terminée sans break : exit au close de la dernière bougie
            if not exit_window.empty:
                exit_price = float(exit_window["close"].iloc[-1])

        # P&L brut en euros (basé sur exposition turbo)
        if direction == "BUY":
            pnl_brut = (exit_price - entry) / entry * exposure
        else:
            pnl_brut = (entry - exit_price) / entry * exposure

        costs = COST_BD_ROUND_TRIP + COST_SPREAD + position_eur * COST_SLIPPAGE_PCT
        pnl_net = pnl_brut - costs

        trades.append(
            TradeResult(
                timestamp=entry_idx,
                asset=asset,
                direction=direction,
                entry=entry,
                sl=sl,
                tp=tp,
                exit_price=exit_price,
                exit_reason=exit_reason,
                pnl_brut=pnl_brut,
                costs=costs,
                pnl_net=pnl_net,
            )
        )
    return trades


def trades_to_df(trades: list[TradeResult]) -> pd.DataFrame:
    """Convertit liste TradeResult → DataFrame avec colonne pnl_net."""
    if not trades:
        return pd.DataFrame(columns=["pnl_net", "pnl_brut", "exit_reason"])
    rows = [asdict(t) for t in trades]
    return pd.DataFrame(rows)


def compute_stats(
    trades: list[TradeResult],
    edge_id: str,
    period_label: str,
    params: dict[str, float | int],
) -> BacktestStats:
    """Agrège les stats d'un backtest."""
    df = trades_to_df(trades)
    if df.empty:
        return BacktestStats(
            edge_id=edge_id,
            period_label=period_label,
            nb_trades=0,
            win_rate_pct=0.0,
            profit_factor=0.0,
            sharpe=0.0,
            drawdown_monthly=0.0,
            pnl_total=0.0,
            params=params,
        )
    pnl_series = df["pnl_net"]
    # Equity indexée par timestamp pour drawdown mensuel
    timestamps = pd.DatetimeIndex(df["timestamp"])
    pnl_indexed = pd.Series(pnl_series.to_numpy(), index=timestamps)
    equity = equity_curve_from_returns(pnl_indexed, initial_capital=15_000.0)
    # Convertir P&L en rendement par trade (vs exposition)
    returns_pct = pnl_series / (DEFAULT_POSITION_EUR * DEFAULT_LEVERAGE)

    return BacktestStats(
        edge_id=edge_id,
        period_label=period_label,
        nb_trades=len(df),
        win_rate_pct=win_rate(df),
        profit_factor=profit_factor(pnl_series),
        sharpe=sharpe_ratio(returns_pct),
        drawdown_monthly=max_drawdown_monthly(equity),
        pnl_total=float(pnl_series.sum()),
        params=params,
    )


def _get_edge(edge_arg: str) -> EdgeStrategy:
    if edge_arg.upper() in {"H-C", "H-C-ORB", "ORB"}:
        return H_C_ORB()
    if edge_arg.upper() in {"H-A", "H-A-GAPFOLLOW", "GAP"}:
        return H_A_GapFollow()
    raise ValueError(f"Edge inconnu : {edge_arg} (attendu : H-C ou H-A)")


def _param_grid(edge_id: str) -> list[dict[str, float | int]]:
    """Grille de recherche par edge."""
    if edge_id == "H-C-ORB":
        return [
            {"orb_minutes": 5, "tp_multiple": 1.5},
            {"orb_minutes": 15, "tp_multiple": 1.5},
            {"orb_minutes": 15, "tp_multiple": 2.0},
        ]
    if edge_id == "H-A-GapFollow":
        return [
            {"gap_min_pct": 0.003, "tp_multiple": 1.5, "entry_delay_minutes": 5},
            {"gap_min_pct": 0.005, "tp_multiple": 1.5, "entry_delay_minutes": 5},
            {"gap_min_pct": 0.008, "tp_multiple": 2.0, "entry_delay_minutes": 5},
        ]
    return [{}]


def run_backtest(
    edge: EdgeStrategy,
    assets: list[str],
    is_start: date,
    is_end: date,
    oos_start: date,
    oos_end: date,
    cache_path: Path,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Pipeline complet : grid search IS → params gelés → OOS → walk-forward.

    Returns:
        Dict prêt pour sérialisation JSON.
    """
    loader = MarketDataLoader(cache_path=cache_path, api_key=api_key)

    # 1. Charge data IS et OOS pour tous les assets
    is_data: dict[str, pd.DataFrame] = {}
    oos_data: dict[str, pd.DataFrame] = {}
    for asset in assets:
        is_data[asset] = loader.load_ohlc(asset, is_start, is_end)
        oos_data[asset] = loader.load_ohlc(asset, oos_start, oos_end)

    # 2. Grid search IS
    grid = _param_grid(edge.edge_id)
    best_params: dict[str, float | int] = {}
    best_sharpe = -float("inf")
    best_is_stats: BacktestStats | None = None

    for params in grid:
        all_trades: list[TradeResult] = []
        for asset, df in is_data.items():
            if df.empty:
                continue
            signals = edge.generate_signals(df, params)
            all_trades.extend(simulate_trades(signals, df, asset))
        stats = compute_stats(all_trades, edge.edge_id, "IS", params)
        if stats.sharpe > best_sharpe and stats.nb_trades >= 10:
            best_sharpe = stats.sharpe
            best_params = params
            best_is_stats = stats

    if best_is_stats is None:
        # Aucun paramset n'a généré assez de trades — retourne stub
        best_is_stats = compute_stats([], edge.edge_id, "IS", {})

    # 3. OOS black-box avec params gelés
    oos_trades: list[TradeResult] = []
    for asset, df in oos_data.items():
        if df.empty:
            continue
        signals = edge.generate_signals(df, best_params)
        oos_trades.extend(simulate_trades(signals, df, asset))
    oos_stats = compute_stats(oos_trades, edge.edge_id, "OOS", best_params)

    # 4. Walk-forward 3 fenêtres
    wf_results: list[BacktestStats] = []
    wf_windows = _walk_forward_windows()
    for label, (_wf_is_s, _wf_is_e, wf_oos_s, wf_oos_e) in wf_windows:
        wf_oos_trades: list[TradeResult] = []
        for asset in assets:
            wf_df = loader.load_ohlc(asset, wf_oos_s, wf_oos_e)
            if wf_df.empty:
                continue
            wf_signals = edge.generate_signals(wf_df, best_params)
            wf_oos_trades.extend(simulate_trades(wf_signals, wf_df, asset))
        wf_stats = compute_stats(wf_oos_trades, edge.edge_id, label, best_params)
        wf_results.append(wf_stats)

    # 5. Verdict 6 conditions AND v1.1
    pnl_returns = [t.pnl_net for t in oos_trades]
    pvalue, pvalue_method = compute_pvalue_hansen_spa(pnl_returns)
    wf_pass_count = sum(
        1
        for wf in wf_results
        if wf.sharpe >= 0.6 * best_is_stats.sharpe and best_is_stats.sharpe > 0
    )
    stats_for_verdict = {
        "sharpe_oos": oos_stats.sharpe,
        "profit_factor_oos": oos_stats.profit_factor,
        "drawdown_monthly_oos": oos_stats.drawdown_monthly,
        "sharpe_is": best_is_stats.sharpe,
        "walk_forward_pass_count": wf_pass_count,
        "nb_trades_oos": oos_stats.nb_trades,
    }
    verdict, reasons = evaluate_go_phase2(stats_for_verdict)

    return {
        "edge_id": edge.edge_id,
        "assets": assets,
        "is_period": [is_start.isoformat(), is_end.isoformat()],
        "oos_period": [oos_start.isoformat(), oos_end.isoformat()],
        "best_params_is": best_params,
        "params_used_oos": best_params,
        "is_stats": asdict(best_is_stats),
        "oos_stats": asdict(oos_stats),
        "walk_forward": [asdict(w) for w in wf_results],
        "walk_forward_pass_count": wf_pass_count,
        "robustness_ratio": robustness_ratio(oos_stats.sharpe, best_is_stats.sharpe),
        "pvalue": pvalue,
        "pvalue_method": pvalue_method,
        "verdict": verdict.value,
        "verdict_reasons": reasons,
        "computed_at": datetime.utcnow().isoformat(),
    }


def _walk_forward_windows() -> list[tuple[str, tuple[date, date, date, date]]]:
    """3 fenêtres glissantes (edge-rnd-report.md §2.1)."""
    return [
        (
            "WF1",
            (date(2021, 1, 1), date(2023, 12, 31), date(2024, 1, 1), date(2024, 6, 30)),
        ),
        (
            "WF2",
            (date(2021, 7, 1), date(2024, 6, 30), date(2024, 7, 1), date(2024, 12, 31)),
        ),
        (
            "WF3",
            (date(2022, 1, 1), date(2024, 12, 31), date(2025, 1, 1), date(2025, 6, 30)),
        ),
    ]


def _persist_rnd_result(
    journal_path: Path, edge_id: str, verdict: Verdict, notes: str
) -> None:
    """INSERT dans rnd_results table (kpi-framework.md §7 signal n°6)."""
    if not journal_path.exists():
        return
    pre_pass = 1 if verdict == Verdict.GO_PHASE_2 else 0
    with sqlite3.connect(journal_path) as conn:
        conn.execute(
            "INSERT INTO rnd_results (edge_id, pre_backtest_passed, notes) "
            "VALUES (?, ?, ?)",
            (edge_id, pre_pass, notes),
        )
        conn.commit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backtester R&D Phase 2b")
    parser.add_argument("--edge", required=True, help="H-C ou H-A")
    parser.add_argument("--assets", required=True, help="Liste séparée virgules")
    parser.add_argument("--is-start", required=True, type=date.fromisoformat)
    parser.add_argument("--is-end", required=True, type=date.fromisoformat)
    parser.add_argument("--oos-start", required=True, type=date.fromisoformat)
    parser.add_argument("--oos-end", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--cache-path", default="data/market_cache.sqlite", type=Path
    )
    parser.add_argument(
        "--journal-path", default="data/journal.sqlite", type=Path
    )
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--api-key", default=None)
    args = parser.parse_args(argv)

    edge = _get_edge(args.edge)
    assets = [a.strip() for a in args.assets.split(",") if a.strip()]

    result = run_backtest(
        edge=edge,
        assets=assets,
        is_start=args.is_start,
        is_end=args.is_end,
        oos_start=args.oos_start,
        oos_end=args.oos_end,
        cache_path=args.cache_path,
        api_key=args.api_key,
    )

    # Persist JSON
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str, ensure_ascii=False)

    # Persist rnd_results SQLite
    _persist_rnd_result(
        journal_path=args.journal_path,
        edge_id=edge.edge_id,
        verdict=Verdict(result["verdict"]),
        notes=f"Phase 2b run — verdict {result['verdict']}",
    )

    print(f"[OK] Backtest {edge.edge_id} → {result['verdict']}")
    print(f"     Output : {args.output_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
