"""Backtester R&D — stub Phase 2a, rempli Phase 2b.

Stack cible : vectorbt (backtests vectorises) + arch (Hansen SPA p-value) +
stationary bootstrap Politis-Romano n=10 000.

Spec : docs/qa/backtest-audit-phase1.md (verdict RETRAVAILLER, 11 corrections,
6 conditions GO C1-C6 dont Sharpe OOS > 1.2 + IC95% > 0.5, DD mensuel < 20%,
walk-forward 3/3 PASS, robustesse >= 0.6).
"""
