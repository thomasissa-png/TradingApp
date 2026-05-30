"""Tests des fonctions de métriques pures (src/backtester/metrics.py)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from src.backtester.metrics import (
    equity_curve_from_returns,
    mae_mfe,
    max_drawdown_monthly,
    profit_factor,
    robustness_ratio,
    sharpe_ratio,
    win_rate,
)


# ---------- Sharpe ratio ----------

def test_sharpe_ratio_known_series() -> None:
    """Sharpe sur une série connue : rendements daily 0.001 ± 0.01."""
    returns = pd.Series([0.001, 0.002, -0.001, 0.003, -0.002, 0.001, 0.0005] * 10)
    sharpe = sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252)
    # Mean ≈ 0.000643, std ≈ 0.001779 → Sharpe daily 0.361 → annual ≈ 5.74
    assert sharpe > 4.0
    assert sharpe < 8.0


def test_sharpe_ratio_empty_series() -> None:
    """Série vide → Sharpe = 0."""
    assert sharpe_ratio(pd.Series([], dtype=float)) == 0.0


def test_sharpe_ratio_zero_variance() -> None:
    """Série constante → Sharpe = 0 (pas de division par zéro)."""
    assert sharpe_ratio(pd.Series([0.001] * 10)) == 0.0


def test_sharpe_ratio_negative_returns() -> None:
    """Rendements moyens négatifs → Sharpe négatif."""
    returns = pd.Series([-0.001, -0.002, -0.0015, -0.001, -0.0008] * 5)
    sharpe = sharpe_ratio(returns, risk_free_rate=0.0)
    assert sharpe < 0


# ---------- Profit factor ----------

def test_profit_factor_balanced() -> None:
    """Σ gains 100 / Σ pertes 50 → PF = 2.0."""
    returns = pd.Series([50.0, 50.0, -50.0])
    assert profit_factor(returns) == 2.0


def test_profit_factor_only_gains() -> None:
    """Que des gains → +inf."""
    returns = pd.Series([10.0, 20.0, 5.0])
    assert profit_factor(returns) == float("inf")


def test_profit_factor_only_losses() -> None:
    """Que des pertes → 0."""
    returns = pd.Series([-10.0, -20.0])
    assert profit_factor(returns) == 0.0


def test_profit_factor_empty() -> None:
    """Série vide → 0."""
    assert profit_factor(pd.Series([], dtype=float)) == 0.0


# ---------- Max drawdown mensuel ----------

def test_max_drawdown_monthly_synthetic() -> None:
    """Equity 100→120→90 sur 1 mois → DD 25%."""
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    equity = pd.Series([100, 110, 120, 115, 100, 95, 90, 95, 100, 105], index=idx, dtype=float)
    dd = max_drawdown_monthly(equity)
    assert dd == pytest.approx(0.25, abs=0.01)


def test_max_drawdown_monthly_no_drawdown() -> None:
    """Equity monotone croissante → DD = 0."""
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    equity = pd.Series(range(100, 110), index=idx, dtype=float)
    assert max_drawdown_monthly(equity) == 0.0


def test_max_drawdown_monthly_empty() -> None:
    """Série vide → 0."""
    assert max_drawdown_monthly(pd.Series([], dtype=float)) == 0.0


def test_max_drawdown_monthly_requires_datetime_index() -> None:
    """Index non-datetime → TypeError."""
    with pytest.raises(TypeError):
        max_drawdown_monthly(pd.Series([100, 90, 80], dtype=float))


# ---------- Robustness ratio ----------

def test_robustness_ratio_normal() -> None:
    """OOS 0.9 / IS 1.5 → 0.6."""
    assert robustness_ratio(0.9, 1.5) == pytest.approx(0.6)


def test_robustness_ratio_is_zero() -> None:
    """IS = 0 → 0 (garde-fou)."""
    assert robustness_ratio(0.5, 0.0) == 0.0


def test_robustness_ratio_negative_oos() -> None:
    """OOS négatif → ratio négatif."""
    assert robustness_ratio(-0.3, 1.0) == -0.3


# ---------- MAE / MFE ----------

def test_mae_mfe_basic() -> None:
    """MAE/MFE moyens sur DataFrame trades."""
    trades = pd.DataFrame({"mae": [10.0, 20.0, 15.0], "mfe": [50.0, 30.0, 40.0]})
    mae, mfe = mae_mfe(trades)
    assert mae == 15.0
    assert mfe == 40.0


def test_mae_mfe_empty() -> None:
    """DataFrame vide → (0, 0)."""
    mae, mfe = mae_mfe(pd.DataFrame(columns=["mae", "mfe"]))
    assert mae == 0.0
    assert mfe == 0.0


# ---------- Win rate ----------

def test_win_rate_basic() -> None:
    """3 wins sur 5 trades → 60%."""
    trades = pd.DataFrame({"pnl_net": [10.0, -5.0, 15.0, -3.0, 8.0]})
    assert win_rate(trades) == 60.0


def test_win_rate_empty() -> None:
    assert win_rate(pd.DataFrame()) == 0.0


# ---------- Equity curve ----------

def test_equity_curve_from_returns() -> None:
    """P&L cumul + capital initial."""
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    pnl = pd.Series([100.0, -50.0, 75.0], index=idx)
    equity = equity_curve_from_returns(pnl, initial_capital=15_000.0)
    assert equity.iloc[0] == 15_100.0
    assert equity.iloc[1] == 15_050.0
    assert equity.iloc[2] == 15_125.0
