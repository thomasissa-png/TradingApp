"""Métriques de performance backtest — fonctions pures testables isolément.

Source de vérité : docs/analytics/kpi-framework.md §2.

Toutes les fonctions sont pures (pas d'I/O, pas d'état) et opèrent sur des
pandas.Series ou DataFrames typés.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.03,
    periods_per_year: int = 252,
) -> float:
    """Sharpe ratio annualisé.

    Formule : (Rendement_moyen - Rf_par_periode) / sigma_returns * sqrt(periods_per_year).

    Args:
        returns : série de rendements par période (ex : par trade ou par jour).
        risk_free_rate : taux sans risque annualisé (défaut OAT 10 ans ~3 %).
        periods_per_year : nombre de périodes par an (252 jours ouvrés par défaut).

    Returns:
        Sharpe annualisé. 0.0 si série vide ou écart-type nul.
    """
    if len(returns) == 0:
        return 0.0
    rf_per_period = risk_free_rate / periods_per_year
    excess_returns = returns - rf_per_period
    # Calcule std sur la série originale (constance numérique = std de returns)
    std = returns.std(ddof=1)
    if std == 0 or math.isnan(std) or std < 1e-12:
        return 0.0
    mean_excess = excess_returns.mean()
    return float(mean_excess / std * math.sqrt(periods_per_year))


def profit_factor(returns: pd.Series) -> float:
    """Profit Factor = Σ gains / |Σ pertes|.

    Args:
        returns : série de P&L par trade (gains positifs, pertes négatives).

    Returns:
        Profit factor. inf si que des gains, 0.0 si que des pertes ou série vide.
    """
    if len(returns) == 0:
        return 0.0
    gains = returns[returns > 0].sum()
    losses_abs = abs(returns[returns < 0].sum())
    if losses_abs == 0:
        return float("inf") if gains > 0 else 0.0
    return float(gains / losses_abs)


def max_drawdown_monthly(equity_curve: pd.Series) -> float:
    """Max drawdown mensuel (pire mois calendaire).

    Pour respecter le critère C3 v1.1 (drawdown mensuel < 20%) — durci par
    @qa Phase 1b vs drawdown annuel v1.0.

    Args:
        equity_curve : courbe d'équité indexée par DatetimeIndex.

    Returns:
        Max drawdown mensuel en valeur absolue (0.20 = 20%). 0.0 si vide.
    """
    if len(equity_curve) == 0:
        return 0.0
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        raise TypeError("equity_curve must be indexed by DatetimeIndex")
    monthly_dd: list[float] = []
    for _, group in equity_curve.groupby(pd.Grouper(freq="ME")):
        if len(group) < 2:
            continue
        peak = group.cummax()
        # Évite division par zéro si peak == 0
        with np.errstate(divide="ignore", invalid="ignore"):
            drawdowns = (peak - group) / peak.replace(0, np.nan)
        max_dd = drawdowns.max()
        if pd.notna(max_dd):
            monthly_dd.append(float(max_dd))
    if not monthly_dd:
        return 0.0
    return max(monthly_dd)


def robustness_ratio(sharpe_oos: float, sharpe_is: float) -> float:
    """Ratio de robustesse OOS vs IS.

    Critère C4 v1.1 : Sharpe_OOS / Sharpe_IS ≥ 0.6 (Pardo 2008).

    Args:
        sharpe_oos : Sharpe out-of-sample.
        sharpe_is : Sharpe in-sample.

    Returns:
        Ratio. 0.0 si IS == 0 (garde-fou). Peut être négatif si OOS négatif.
    """
    if sharpe_is == 0 or math.isnan(sharpe_is):
        return 0.0
    return float(sharpe_oos / sharpe_is)


def mae_mfe(trades: pd.DataFrame) -> tuple[float, float]:
    """Maximum Adverse Excursion (MAE) et Maximum Favorable Excursion (MFE) moyens.

    Args:
        trades : DataFrame avec colonnes 'mae' et 'mfe' (en € absolus par trade).

    Returns:
        (MAE_moyen, MFE_moyen) en €. (0.0, 0.0) si vide.
    """
    if len(trades) == 0:
        return (0.0, 0.0)
    mae_col = trades["mae"] if "mae" in trades.columns else pd.Series([0.0])
    mfe_col = trades["mfe"] if "mfe" in trades.columns else pd.Series([0.0])
    return (float(mae_col.mean()), float(mfe_col.mean()))


def win_rate(trades: pd.DataFrame) -> float:
    """Win rate = pct trades gagnants.

    Args:
        trades : DataFrame avec colonne 'pnl_net' (P&L net par trade).

    Returns:
        Win rate en pourcentage (0.0-100.0). 0.0 si vide.
    """
    if len(trades) == 0 or "pnl_net" not in trades.columns:
        return 0.0
    n_wins = int((trades["pnl_net"] > 0).sum())
    return float(n_wins / len(trades) * 100.0)


def equity_curve_from_returns(
    returns: pd.Series,
    initial_capital: float = 15_000.0,
) -> pd.Series:
    """Reconstruit une courbe d'équité depuis une série de P&L par trade.

    Args:
        returns : série de P&L absolus en €, indexée par timestamp d'exit.
        initial_capital : capital initial (défaut 15 000 € = sizing référence).

    Returns:
        Série équité indexée par timestamp.
    """
    if len(returns) == 0:
        return pd.Series([initial_capital], dtype=float)
    cumulative = returns.cumsum()
    return cumulative + initial_capital
