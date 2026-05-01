"""Module scoring — pipeline complet (LLM + 6 dimensions deterministes + 7 sanity checks).

Architecture : cf docs/ia/edge-scoring-model.md v1.2 (6D 35/15/15/15/10/10 + SC1-SC7).
"""

from __future__ import annotations

from src.scoring.dimensions import (
    compute_d1_force_signal,
    compute_d2_confluence_indicators,
    compute_d3_news_context,
    compute_d4_volatility,
    compute_d5_regime_vix,
    compute_d6_backtest_freshness,
    compute_deterministic_score,
)
from src.scoring.engine import ScoringEngine
from src.scoring.sanity_checks import (
    apply_all_sanity_checks,
    apply_sc1,
    apply_sc2,
    apply_sc3,
    apply_sc4,
    apply_sc5,
    apply_sc6,
    apply_sc7,
)
from src.scoring.threshold import select_threshold

__all__ = [
    "ScoringEngine",
    "apply_all_sanity_checks",
    "apply_sc1",
    "apply_sc2",
    "apply_sc3",
    "apply_sc4",
    "apply_sc5",
    "apply_sc6",
    "apply_sc7",
    "compute_d1_force_signal",
    "compute_d2_confluence_indicators",
    "compute_d3_news_context",
    "compute_d4_volatility",
    "compute_d5_regime_vix",
    "compute_d6_backtest_freshness",
    "compute_deterministic_score",
    "select_threshold",
]
