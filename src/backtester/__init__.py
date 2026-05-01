"""Backtester R&D Phase 2b — implémentation Wave 1 (H-C ORB + H-A Gap Follow).

Stack : Python 3.12 + pandas + numpy + arch (Hansen SPA) + twelvedata + SQLite cache.

Spec : docs/qa/backtest-audit-phase1.md (verdict RETRAVAILLER, 11 corrections,
6 conditions GO C1-C6 v1.1) + docs/analytics/edge-rnd-report.md v1.1.

Usage CLI :
    python -m src.backtester.runner --edge=H-C --assets=DAX,CAC,ESTX50 \\
        --is-start=2021-01-01 --is-end=2024-12-31 \\
        --oos-start=2025-01-01 --oos-end=2025-12-31 \\
        --output-json=docs/analytics/results/edge-H-C-results.json
"""

from src.backtester.data import MarketDataLoader
from src.backtester.edges import H_C_ORB, EdgeStrategy, H_A_GapFollow
from src.backtester.methodology import (
    BacktestConfig,
    TestResult,
    compute_pvalue_hansen_spa,
    run_all_pre_backtest_tests,
)
from src.backtester.runner import run_backtest
from src.backtester.verdict import Verdict, evaluate_go_phase2

__all__ = [
    "H_C_ORB",
    "BacktestConfig",
    "EdgeStrategy",
    "H_A_GapFollow",
    "MarketDataLoader",
    "TestResult",
    "Verdict",
    "compute_pvalue_hansen_spa",
    "evaluate_go_phase2",
    "run_all_pre_backtest_tests",
    "run_backtest",
]
