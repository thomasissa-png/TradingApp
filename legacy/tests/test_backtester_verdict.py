"""Tests verdict GO/NO-GO Phase 2 (src/backtester/verdict.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.backtester.verdict import Verdict, evaluate_go_phase2

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "backtest_results"


def _load_fixture(name: str) -> dict:
    """Charge un fixture JSON."""
    with open(FIXTURE_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def test_verdict_go_phase2_when_all_6_pass() -> None:
    """Stats fictives PASS 6/6 → GO_PHASE_2, raisons vides."""
    stats = _load_fixture("h_c_orb_passing.json")
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.GO_PHASE_2
    assert reasons == []


def test_verdict_retravailler_when_only_sharpe_fails() -> None:
    """Stats FAIL C1 (Sharpe 1.10) mais PASS 5/6 autres → RETRAVAILLER."""
    stats = _load_fixture("h_c_orb_failing_sharpe.json")
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.RETRAVAILLER
    assert len(reasons) == 1
    assert "C1 FAIL" in reasons[0]
    assert "1.10" in reasons[0]


def test_verdict_no_go_when_multiple_fail() -> None:
    """Stats fixture failing_drawdown FAIL plusieurs conditions → NO_GO_EDGE."""
    stats = _load_fixture("h_c_orb_failing_drawdown.json")
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.NO_GO_EDGE
    # Au moins C3 (drawdown) doit être cité
    assert any("C3" in r for r in reasons)
    # 25% >= 20% donc DD fail
    assert any("25" in r or "0.25" in r for r in reasons)


def test_verdict_no_go_when_drawdown_25pct() -> None:
    """Drawdown 25% > 20% → C3 FAIL spécifiquement."""
    stats = {
        "sharpe_oos": 1.5,
        "profit_factor_oos": 1.8,
        "drawdown_monthly_oos": 0.25,
        "sharpe_is": 1.6,
        "walk_forward_pass_count": 3,
        "nb_trades_oos": 100,
    }
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.RETRAVAILLER
    assert len(reasons) == 1
    assert "C3 FAIL" in reasons[0]


def test_verdict_with_typed_dict() -> None:
    """Test avec dict standard (interface BacktestStats TypedDict)."""
    stats = {
        "sharpe_oos": 1.30,
        "profit_factor_oos": 1.60,
        "drawdown_monthly_oos": 0.18,
        "sharpe_is": 1.80,
        "walk_forward_pass_count": 3,
        "nb_trades_oos": 60,
    }
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.GO_PHASE_2


def test_verdict_walk_forward_partial_fails() -> None:
    """WF 2/3 < 3/3 requis → C5 FAIL."""
    stats = {
        "sharpe_oos": 1.30,
        "profit_factor_oos": 1.60,
        "drawdown_monthly_oos": 0.15,
        "sharpe_is": 1.80,
        "walk_forward_pass_count": 2,
        "nb_trades_oos": 60,
    }
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.RETRAVAILLER
    assert any("C5" in r for r in reasons)


def test_verdict_robustness_below_threshold() -> None:
    """Sharpe_OOS / Sharpe_IS = 0.55 < 0.6 → C4 FAIL."""
    stats = {
        "sharpe_oos": 1.30,
        "profit_factor_oos": 1.60,
        "drawdown_monthly_oos": 0.15,
        "sharpe_is": 2.50,  # 1.30/2.50 = 0.52 → fail
        "walk_forward_pass_count": 3,
        "nb_trades_oos": 60,
    }
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.RETRAVAILLER
    assert any("C4" in r for r in reasons)


def test_verdict_nb_trades_oos_below_50() -> None:
    """nb_trades_OOS = 40 < 50 → C6 FAIL."""
    stats = {
        "sharpe_oos": 1.30,
        "profit_factor_oos": 1.60,
        "drawdown_monthly_oos": 0.15,
        "sharpe_is": 1.80,
        "walk_forward_pass_count": 3,
        "nb_trades_oos": 40,
    }
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.RETRAVAILLER
    assert any("C6" in r for r in reasons)


def test_verdict_no_go_when_4_or_more_fail() -> None:
    """4 conditions fail → NO_GO_EDGE."""
    stats = {
        "sharpe_oos": 0.5,  # C1 fail
        "profit_factor_oos": 0.8,  # C2 fail
        "drawdown_monthly_oos": 0.30,  # C3 fail
        "sharpe_is": 1.80,  # robustness 0.5/1.8 = 0.27 → C4 fail
        "walk_forward_pass_count": 3,
        "nb_trades_oos": 100,
    }
    verdict, reasons = evaluate_go_phase2(stats)
    assert verdict == Verdict.NO_GO_EDGE
    assert len(reasons) >= 4
