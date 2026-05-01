"""7 tests PRE-backtest (gate méthodologique avant la R&D physique 30-90 j).

Source de vérité : docs/analytics/edge-rnd-report.md §2 + .claude/agents/testeur-backtest-edge.md.

Objectif : vérifier que la méthodologie de backtest est rigoureuse AVANT de
consommer le budget Twelve Data + 30-90 j de R&D physique. Si un test PRE
échoue → corriger AVANT de lancer le backtest physique.

Les 7 tests sont :
- T1 : split temporel correct (IS/OOS sans chevauchement, OOS ≥ 1 an)
- T2 : walk-forward 3 fenêtres définies
- T3 : coûts transaction réalistes (1.98 € + 0.05 € + 0.1%)
- T4 : nb_trades_IS ≥ 100 (significativité IS)
- T5 : nb_trades_OOS ≥ 50 (condition C6)
- T6 : p-value calculée (Hansen SPA ou Bonferroni)
- T7 : pas de data leakage (paramètres OOS = paramètres IS gelés)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

# Tentative import arch pour Hansen SPA — fallback Bonferroni si absent
try:
    from arch.bootstrap import StationaryBootstrap

    ARCH_AVAILABLE = True
except ImportError:
    ARCH_AVAILABLE = False


@dataclass
class TestResult:
    """Résultat d'un test PRE-backtest."""

    test_id: str
    passed: bool
    reason: str


class BacktestConfig:
    """Configuration backtest minimale (pour les tests PRE)."""

    def __init__(
        self,
        is_start: date,
        is_end: date,
        oos_start: date,
        oos_end: date,
        wf_windows: list[tuple[date, date, date, date]] | None = None,
        costs_bd_round_trip: float = 1.98,
        costs_spread: float = 0.05,
        costs_slippage_pct: float = 0.001,
    ) -> None:
        self.is_start = is_start
        self.is_end = is_end
        self.oos_start = oos_start
        self.oos_end = oos_end
        self.wf_windows = wf_windows or []
        self.costs_bd_round_trip = costs_bd_round_trip
        self.costs_spread = costs_spread
        self.costs_slippage_pct = costs_slippage_pct


def check_split_temporal_correct(config: BacktestConfig) -> TestResult:
    """T1 : IS/OOS sans chevauchement et OOS >= 1 an."""
    if config.is_end >= config.oos_start:
        return TestResult(
            "T1",
            False,
            f"Chevauchement IS/OOS : is_end={config.is_end} >= oos_start={config.oos_start}",
        )
    oos_days = (config.oos_end - config.oos_start).days
    if oos_days < 364:  # 1 an = 365 dates incluses → diff de 364 jours
        return TestResult(
            "T1",
            False,
            f"OOS trop court : {oos_days} jours < 364 (1 an requis)",
        )
    return TestResult("T1", True, f"Split OK ({oos_days}j OOS)")


def check_walk_forward_3_windows(config: BacktestConfig) -> TestResult:
    """T2 : 3 fenêtres glissantes définies (critère C5)."""
    if len(config.wf_windows) < 3:
        return TestResult(
            "T2",
            False,
            f"Walk-forward incomplet : {len(config.wf_windows)} fenêtres < 3 requis",
        )
    # Vérifier que chaque fenêtre a (is_start, is_end, oos_start, oos_end)
    for i, window in enumerate(config.wf_windows[:3]):
        if len(window) != 4:
            return TestResult(
                "T2", False, f"Fenêtre {i+1} mal formée (doit être 4-tuple)"
            )
        _is_s, is_e, oos_s, _oos_e = window
        if is_e >= oos_s:
            return TestResult(
                "T2",
                False,
                f"Fenêtre {i+1} : chevauchement IS/OOS (is_end={is_e} >= oos_start={oos_s})",
            )
    return TestResult("T2", True, "3 fenêtres walk-forward valides")


def check_costs_realistic(config: BacktestConfig) -> TestResult:
    """T3 : coûts intégrés conformes spec (1.98 € + 0.05 € + 0.1%)."""
    if abs(config.costs_bd_round_trip - 1.98) > 0.01:
        return TestResult(
            "T3",
            False,
            f"Frais BD aller-retour={config.costs_bd_round_trip}€ != 1.98€ spec",
        )
    if abs(config.costs_spread - 0.05) > 0.01:
        return TestResult(
            "T3",
            False,
            f"Spread={config.costs_spread}€ != 0.05€ spec",
        )
    if abs(config.costs_slippage_pct - 0.001) > 0.0001:
        return TestResult(
            "T3",
            False,
            f"Slippage={config.costs_slippage_pct} != 0.001 (0.1%) spec",
        )
    return TestResult("T3", True, "Coûts conformes spec edge-rnd-report.md §2.2")


def check_minimum_trades_is(stats: dict[str, Any]) -> TestResult:
    """T4 : nb_trades_IS >= 100 (significativité IS)."""
    nb = int(stats.get("nb_trades_is", 0))
    if nb < 100:
        return TestResult(
            "T4",
            False,
            f"nb_trades_IS={nb} < 100 (significativité minimale insuffisante)",
        )
    return TestResult("T4", True, f"nb_trades_IS={nb} >= 100")


def check_minimum_trades_oos(stats: dict[str, Any]) -> TestResult:
    """T5 : nb_trades_OOS >= 50 (condition C6 v1.1)."""
    nb = int(stats.get("nb_trades_oos", 0))
    if nb < 50:
        return TestResult(
            "T5",
            False,
            f"nb_trades_OOS={nb} < 50 (Lo 2002 IC95% — C6 FAIL)",
        )
    return TestResult("T5", True, f"nb_trades_OOS={nb} >= 50")


def check_pvalue_calculated(stats: dict[str, Any]) -> TestResult:
    """T6 : p-value présente et < seuil ajusté (Hansen SPA OU Bonferroni)."""
    pvalue = stats.get("pvalue")
    method = stats.get("pvalue_method", "")
    if pvalue is None:
        return TestResult("T6", False, "p-value manquante (champ 'pvalue' requis)")
    pvalue_f = float(pvalue)
    # Seuil : SPA → 0.05, Bonferroni → 0.05/7 ≈ 0.0071
    if "spa" in method.lower() or "hansen" in method.lower():
        threshold = 0.05
    elif "bonferroni" in method.lower():
        threshold = 0.05 / 7
    else:
        return TestResult(
            "T6",
            False,
            f"pvalue_method='{method}' inconnu (attendu : 'hansen_spa' ou 'bonferroni')",
        )
    if pvalue_f >= threshold:
        return TestResult(
            "T6",
            False,
            f"p-value={pvalue_f:.4f} >= seuil {threshold:.4f} ({method})",
        )
    return TestResult(
        "T6", True, f"p-value={pvalue_f:.4f} < {threshold:.4f} ({method})"
    )


def check_no_data_leakage(stats: dict[str, Any]) -> TestResult:
    """T7 : paramètres OOS = paramètres IS gelés (pas de re-fit OOS)."""
    params_is = stats.get("best_params_is")
    params_oos = stats.get("params_used_oos")
    if params_is is None or params_oos is None:
        return TestResult(
            "T7",
            False,
            "Champs 'best_params_is' et 'params_used_oos' requis pour audit leakage",
        )
    if params_is != params_oos:
        return TestResult(
            "T7",
            False,
            f"DATA LEAKAGE détecté : params_IS={params_is} != params_OOS={params_oos}",
        )
    return TestResult("T7", True, "Paramètres OOS = paramètres IS gelés")


def run_all_pre_backtest_tests(
    config: BacktestConfig, stats: dict[str, Any]
) -> list[TestResult]:
    """Exécute les 7 tests PRE-backtest dans l'ordre.

    Returns:
        Liste des 7 TestResult dans l'ordre T1-T7.
    """
    return [
        check_split_temporal_correct(config),
        check_walk_forward_3_windows(config),
        check_costs_realistic(config),
        check_minimum_trades_is(stats),
        check_minimum_trades_oos(stats),
        check_pvalue_calculated(stats),
        check_no_data_leakage(stats),
    ]


def compute_pvalue_hansen_spa(
    edge_returns: list[float],
    n_bootstrap: int = 10_000,
    block_size: int = 5,
) -> tuple[float, str]:
    """Calcule p-value via stationary bootstrap Politis-Romano + Hansen SPA.

    Fallback Bonferroni si arch package absent.

    Args:
        edge_returns : série des rendements de l'edge en OOS.
        n_bootstrap : itérations bootstrap (défaut 10 000).
        block_size : taille moyenne des blocs (défaut 5 — Politis-Romano).

    Returns:
        (pvalue, method) — method ∈ {'hansen_spa', 'bonferroni_fallback'}.
    """
    if not ARCH_AVAILABLE:
        # Fallback : test t-stat simple, ajusté Bonferroni 0.05/7
        import math

        if len(edge_returns) < 2:
            return (1.0, "bonferroni_fallback")
        mean = sum(edge_returns) / len(edge_returns)
        var = sum((x - mean) ** 2 for x in edge_returns) / (len(edge_returns) - 1)
        if var == 0:
            return (1.0, "bonferroni_fallback")
        t_stat = mean / math.sqrt(var / len(edge_returns))
        # Approximation : pvalue ≈ exp(-t^2/2) (queue normale très simplifiée)
        pvalue = math.exp(-(t_stat**2) / 2.0) if t_stat > 0 else 1.0
        return (min(pvalue, 1.0), "bonferroni_fallback")

    # Méthode A : Hansen SPA via stationary bootstrap
    import numpy as np

    arr = np.array(edge_returns, dtype=float)
    if len(arr) < 10:
        return (1.0, "hansen_spa")
    bs = StationaryBootstrap(block_size, arr)
    boot_means = []
    for data in bs.bootstrap(n_bootstrap):
        sample = data[0][0]
        boot_means.append(float(sample.mean()))
    observed_mean = float(arr.mean())
    # H0 : edge mean <= 0 → pvalue = P(boot_mean >= observed_mean | H0 centered)
    centered = np.array(boot_means) - observed_mean
    pvalue = float((centered >= 0).mean())
    return (pvalue, "hansen_spa")
