"""Tests des 7 tests PRE-backtest (src/backtester/methodology.py).

Note : les fonctions du module sont préfixées 'check_' pour éviter la
collection automatique pytest (qui sinon les invoque comme des tests sans
fixture 'config'/'stats').
"""

from __future__ import annotations

from datetime import date

import pytest

from src.backtester.methodology import (
    BacktestConfig,
    check_costs_realistic,
    check_minimum_trades_is,
    check_minimum_trades_oos,
    check_no_data_leakage,
    check_pvalue_calculated,
    check_split_temporal_correct,
    check_walk_forward_3_windows,
    compute_pvalue_hansen_spa,
    run_all_pre_backtest_tests,
)


def _valid_config() -> BacktestConfig:
    """Config qui PASS T1-T3."""
    return BacktestConfig(
        is_start=date(2021, 1, 1),
        is_end=date(2024, 12, 31),
        oos_start=date(2025, 1, 1),
        oos_end=date(2025, 12, 31),
        wf_windows=[
            (date(2021, 1, 1), date(2023, 12, 31), date(2024, 1, 1), date(2024, 6, 30)),
            (date(2021, 7, 1), date(2024, 6, 30), date(2024, 7, 1), date(2024, 12, 31)),
            (date(2022, 1, 1), date(2024, 12, 31), date(2025, 1, 1), date(2025, 6, 30)),
        ],
    )


def _valid_stats() -> dict:
    """Stats fictives qui PASS T4-T7."""
    return {
        "nb_trades_is": 250,
        "nb_trades_oos": 78,
        "pvalue": 0.012,
        "pvalue_method": "hansen_spa",
        "best_params_is": {"orb_minutes": 15, "tp_multiple": 1.5},
        "params_used_oos": {"orb_minutes": 15, "tp_multiple": 1.5},
    }


# ---------- T1 ----------

def test_t1_pass_on_valid_split() -> None:
    result = check_split_temporal_correct(_valid_config())
    assert result.passed
    assert result.test_id == "T1"


def test_t1_fail_on_overlap() -> None:
    config = BacktestConfig(
        is_start=date(2021, 1, 1),
        is_end=date(2025, 6, 30),  # overlap avec OOS
        oos_start=date(2025, 1, 1),
        oos_end=date(2025, 12, 31),
    )
    result = check_split_temporal_correct(config)
    assert not result.passed
    assert "Chevauchement" in result.reason


def test_t1_fail_on_short_oos() -> None:
    config = BacktestConfig(
        is_start=date(2021, 1, 1),
        is_end=date(2024, 12, 31),
        oos_start=date(2025, 1, 1),
        oos_end=date(2025, 6, 30),  # 6 mois seulement
    )
    result = check_split_temporal_correct(config)
    assert not result.passed
    assert "364" in result.reason


# ---------- T2 ----------

def test_t2_pass_on_3_windows() -> None:
    result = check_walk_forward_3_windows(_valid_config())
    assert result.passed


def test_t2_fail_on_2_windows() -> None:
    config = _valid_config()
    config.wf_windows = config.wf_windows[:2]
    result = check_walk_forward_3_windows(config)
    assert not result.passed
    assert "2 fenêtres" in result.reason


# ---------- T3 ----------

def test_t3_pass_on_correct_costs() -> None:
    result = check_costs_realistic(_valid_config())
    assert result.passed


def test_t3_fail_on_wrong_bd_cost() -> None:
    config = _valid_config()
    config.costs_bd_round_trip = 0.99  # spec exige 1.98
    result = check_costs_realistic(config)
    assert not result.passed
    assert "Frais BD" in result.reason


# ---------- T4 ----------

def test_t4_pass_on_sufficient_trades_is() -> None:
    result = check_minimum_trades_is(_valid_stats())
    assert result.passed


def test_t4_fail_on_insufficient_trades_is() -> None:
    stats = _valid_stats()
    stats["nb_trades_is"] = 50
    result = check_minimum_trades_is(stats)
    assert not result.passed
    assert "100" in result.reason


# ---------- T5 ----------

def test_t5_pass_on_sufficient_trades_oos() -> None:
    result = check_minimum_trades_oos(_valid_stats())
    assert result.passed


def test_t5_fail_on_insufficient_trades_oos() -> None:
    stats = _valid_stats()
    stats["nb_trades_oos"] = 30
    result = check_minimum_trades_oos(stats)
    assert not result.passed
    assert "C6" in result.reason


# ---------- T6 ----------

def test_t6_pass_on_valid_pvalue_spa() -> None:
    result = check_pvalue_calculated(_valid_stats())
    assert result.passed


def test_t6_fail_on_pvalue_too_high_spa() -> None:
    stats = _valid_stats()
    stats["pvalue"] = 0.10
    result = check_pvalue_calculated(stats)
    assert not result.passed


def test_t6_pass_on_bonferroni_method() -> None:
    stats = _valid_stats()
    stats["pvalue"] = 0.005
    stats["pvalue_method"] = "bonferroni"
    result = check_pvalue_calculated(stats)
    assert result.passed


def test_t6_fail_on_missing_pvalue() -> None:
    stats = _valid_stats()
    del stats["pvalue"]
    result = check_pvalue_calculated(stats)
    assert not result.passed


# ---------- T7 ----------

def test_t7_pass_on_frozen_params() -> None:
    result = check_no_data_leakage(_valid_stats())
    assert result.passed


def test_t7_fail_on_data_leakage() -> None:
    stats = _valid_stats()
    stats["params_used_oos"] = {"orb_minutes": 5, "tp_multiple": 2.0}  # ≠ IS
    result = check_no_data_leakage(stats)
    assert not result.passed
    assert "DATA LEAKAGE" in result.reason


# ---------- Run all ----------

def test_run_all_pre_backtest_returns_7_results() -> None:
    results = run_all_pre_backtest_tests(_valid_config(), _valid_stats())
    assert len(results) == 7
    assert all(r.passed for r in results), [
        f"{r.test_id}: {r.reason}" for r in results if not r.passed
    ]
    assert [r.test_id for r in results] == ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]


# ---------- p-value Hansen SPA fallback ----------

def test_pvalue_hansen_spa_returns_value_and_method() -> None:
    """compute_pvalue_hansen_spa retourne (pvalue, method) sans crash."""
    returns = [10.0, -5.0, 15.0, -3.0, 8.0, 12.0, -2.0, 6.0, 9.0, -4.0]
    pvalue, method = compute_pvalue_hansen_spa(returns, n_bootstrap=100)
    assert 0.0 <= pvalue <= 1.0
    assert method in {"hansen_spa", "bonferroni_fallback"}
