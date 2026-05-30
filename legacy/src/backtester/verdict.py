"""Évaluation verdict GO/NO-GO Phase 2 sur les 6 conditions AND v1.1.

Source de vérité : docs/analytics/edge-rnd-report.md §5 (v1.1 — durci @qa Phase 1b).

6 conditions AND obligatoires :
- C1 : Sharpe annualisé OOS > 1.2
- C2 : Profit Factor OOS > 1.5
- C3 : Drawdown mensuel OOS < 20%
- C4 : Robustesse Sharpe_OOS / Sharpe_IS ≥ 0.6
- C5 : Walk-forward 3/3 fenêtres PASS
- C6 : nb_trades_OOS ≥ 50
"""

from __future__ import annotations

from enum import Enum
from typing import Any, TypedDict


class Verdict(str, Enum):  # noqa: UP042 — StrEnum pas dispo Python <3.11, str+Enum maintient sérialisation JSON propre
    """Verdicts possibles pour un edge candidat."""

    GO_PHASE_2 = "GO_PHASE_2"
    RETRAVAILLER = "RETRAVAILLER"
    NO_GO_EDGE = "NO_GO_EDGE"


class BacktestStats(TypedDict, total=False):
    """Stats minimales requises pour évaluer le verdict.

    Champs obligatoires : sharpe_oos, profit_factor_oos, drawdown_monthly_oos,
    sharpe_is, walk_forward_pass_count, nb_trades_oos.
    """

    sharpe_oos: float
    profit_factor_oos: float
    drawdown_monthly_oos: float
    sharpe_is: float
    walk_forward_pass_count: int  # 0..3
    nb_trades_oos: int


# Seuils v1.1 — source edge-rnd-report.md §5
THRESHOLD_SHARPE_OOS = 1.2
THRESHOLD_PROFIT_FACTOR_OOS = 1.5
THRESHOLD_DRAWDOWN_MONTHLY_OOS = 0.20
THRESHOLD_ROBUSTNESS = 0.6
THRESHOLD_WALK_FORWARD_PASS = 3
THRESHOLD_NB_TRADES_OOS = 50


def evaluate_go_phase2(
    stats: BacktestStats | dict[str, Any],
) -> tuple[Verdict, list[str]]:
    """Évalue les 6 conditions AND v1.1.

    Args:
        stats : dict avec les 6 champs requis.

    Returns:
        (Verdict, liste des raisons d'échec). Liste vide si GO_PHASE_2.

    Logique :
    - 6/6 PASS → GO_PHASE_2
    - 4-5 PASS → RETRAVAILLER (proche, ajustements possibles)
    - 0-3 PASS → NO_GO_EDGE (échec structurel, abandonner cet edge)
    """
    failures: list[str] = []

    sharpe_oos = float(stats.get("sharpe_oos", 0.0))
    if sharpe_oos <= THRESHOLD_SHARPE_OOS:
        failures.append(
            f"C1 FAIL : Sharpe OOS={sharpe_oos:.2f} ≤ {THRESHOLD_SHARPE_OOS} "
            f"(seuil v1.1 durci, Lo 2002 IC95%)"
        )

    pf_oos = float(stats.get("profit_factor_oos", 0.0))
    if pf_oos <= THRESHOLD_PROFIT_FACTOR_OOS:
        failures.append(
            f"C2 FAIL : Profit Factor OOS={pf_oos:.2f} ≤ {THRESHOLD_PROFIT_FACTOR_OOS}"
        )

    dd_monthly = float(stats.get("drawdown_monthly_oos", 1.0))
    if dd_monthly >= THRESHOLD_DRAWDOWN_MONTHLY_OOS:
        failures.append(
            f"C3 FAIL : Drawdown mensuel OOS={dd_monthly:.2%} ≥ "
            f"{THRESHOLD_DRAWDOWN_MONTHLY_OOS:.0%} (signal d'arrêt n°1 persona)"
        )

    sharpe_is = float(stats.get("sharpe_is", 0.0))
    ratio = 0.0 if sharpe_is == 0 else sharpe_oos / sharpe_is
    if ratio < THRESHOLD_ROBUSTNESS:
        failures.append(
            f"C4 FAIL : Robustesse Sharpe_OOS/Sharpe_IS={ratio:.2f} < "
            f"{THRESHOLD_ROBUSTNESS} (Pardo 2008)"
        )

    wf_pass = int(stats.get("walk_forward_pass_count", 0))
    if wf_pass < THRESHOLD_WALK_FORWARD_PASS:
        failures.append(
            f"C5 FAIL : Walk-forward {wf_pass}/3 fenêtres PASS < "
            f"{THRESHOLD_WALK_FORWARD_PASS}/3 requis"
        )

    nb_trades = int(stats.get("nb_trades_oos", 0))
    if nb_trades < THRESHOLD_NB_TRADES_OOS:
        failures.append(
            f"C6 FAIL : nb_trades_OOS={nb_trades} < {THRESHOLD_NB_TRADES_OOS} "
            f"(IC95% trop large, Lo 2002)"
        )

    n_pass = 6 - len(failures)
    if n_pass == 6:
        return Verdict.GO_PHASE_2, []
    if n_pass >= 4:
        return Verdict.RETRAVAILLER, failures
    return Verdict.NO_GO_EDGE, failures
