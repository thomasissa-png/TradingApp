"""Tests des 6 dimensions D1-D6 + agregat compute_deterministic_score.

Chaque dimension est testable isolement (fonction pure).
"""

from __future__ import annotations

from typing import Any

import pytest

from src.scoring.dimensions import (
    WEIGHTS,
    compute_d1_force_signal,
    compute_d2_confluence_indicators,
    compute_d3_news_context,
    compute_d4_volatility,
    compute_d5_regime_vix,
    compute_d6_backtest_freshness,
    compute_deterministic_score,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_context(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "edge_id": "H-A",
        "asset": {"name": "DAX"},
        "indicators": {
            "rsi_14": 58,
            "macd_signal": 12.0,
            "macd_histogram": 0.3,
            "bollinger_upper": 18450,
            "bollinger_lower": 18200,
            "bollinger_middle": 18325,
            "atr_14": 85,
        },
        "edge_features": {
            "gap_pct": 0.82,
            "sigma_gap_30d": 0.45,
            "orb_breakout": True,
            "volume_premarket_ratio": 1.4,
        },
        "ohlc_today_premarket": [
            {"ts": "2026-05-04T08:30", "open": 18400, "high": 18420, "low": 18395, "close": 18415, "volume": 25000},
        ],
        "backtest_stats": {"sharpe_ratio": 1.3, "win_rate": 61, "nb_trades": 87, "age_days": 30},
        "vix": 14.0,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# D1 — Force du signal
# ---------------------------------------------------------------------------


def test_d1_h_a_gap_normalise() -> None:
    """H-A : gap 0.82 / sigma 0.45 * 5 = ~9.1 -> clip 9.1."""
    ctx = _base_context()
    score, reason = compute_d1_force_signal(ctx)
    assert 9.0 <= score <= 9.2
    assert "H-A" in reason


def test_d1_h_e_sentiment() -> None:
    ctx = _base_context(
        edge_id="H-E",
        edge_features={"sentiment_score": -0.72, "news_titles": ["a", "b"]},
    )
    score, reason = compute_d1_force_signal(ctx)
    assert score == pytest.approx(7.2, abs=0.01)
    assert "H-E" in reason


def test_d1_unknown_edge() -> None:
    ctx = _base_context(edge_id="H-Z")
    score, reason = compute_d1_force_signal(ctx)
    assert score == 0.0
    assert "inconnu" in reason


# ---------------------------------------------------------------------------
# D2 — Confluence indicateurs
# ---------------------------------------------------------------------------


def test_d2_three_aligned_buy() -> None:
    """RSI>50, MACD>0, prix>middle -> 3/3 = 10."""
    ctx = _base_context()  # RSI 58, MACD_h 0.3, last_close 18415 > middle 18325
    score, reason = compute_d2_confluence_indicators(ctx)
    assert score == 10.0
    assert "3/3" in reason


def test_d2_zero_aligned_sell() -> None:
    """SELL avec indicateurs tous bullish -> 0/3 = 0."""
    ctx = _base_context(edge_id="H-B")  # H-B fade, gap positif -> direction SELL
    score, _ = compute_d2_confluence_indicators(ctx)
    # Avec rsi 58, macd_h 0.3, last_close > middle, et direction SELL -> 0/3
    assert score == 0.0


# ---------------------------------------------------------------------------
# D3 — News context
# ---------------------------------------------------------------------------


def test_d3_news_aligned_with_direction() -> None:
    """sentiment +0.7 aligne BUY -> 7.0."""
    ctx = _base_context(
        edge_id="H-A",
        edge_features={
            "gap_pct": 0.82,
            "sigma_gap_30d": 0.45,
            "sentiment_score": 0.7,
            "news_titles": ["bullish news 1", "bullish news 2"],
        },
    )
    score, _ = compute_d3_news_context(ctx)
    assert 6.9 <= score <= 7.1


def test_d3_news_indispo_plafond_7() -> None:
    """news_titles vide -> plafond 7.0."""
    ctx = _base_context(
        edge_features={
            "gap_pct": 0.82,
            "sigma_gap_30d": 0.45,
            "sentiment_score": 0.9,  # sentiment fort mais pas de titres
            "news_titles": [],
        },
    )
    score, reason = compute_d3_news_context(ctx)
    assert score <= 7.0
    assert "indispo" in reason or "plafond" in reason


def test_d3_no_news_at_all() -> None:
    """Pas de news_titles ni sentiment -> fallback 5.0."""
    ctx = _base_context(edge_features={"gap_pct": 0.82, "sigma_gap_30d": 0.45})
    score, _ = compute_d3_news_context(ctx)
    assert score == 5.0


# ---------------------------------------------------------------------------
# D4 — Volatilite
# ---------------------------------------------------------------------------


def test_d4_sur_volatilite() -> None:
    ctx = _base_context()
    ctx["indicators"]["sigma_realized"] = 1.5
    ctx["indicators"]["sigma_implied"] = 1.0
    score, _ = compute_d4_volatility(ctx)
    assert score == 8.0


def test_d4_indispo() -> None:
    ctx = _base_context()
    score, _ = compute_d4_volatility(ctx)
    # sigma_implied absent -> neutre 5.0
    assert score == 5.0


# ---------------------------------------------------------------------------
# D5 — Regime VIX
# ---------------------------------------------------------------------------


def test_d5_trend_regime() -> None:
    ctx = _base_context(vix=12.0)
    score, _ = compute_d5_regime_vix(ctx)
    assert score == 8.0


def test_d5_panic_regime() -> None:
    ctx = _base_context(vix=30.0)
    score, _ = compute_d5_regime_vix(ctx)
    assert score == 3.0


def test_d5_indispo() -> None:
    ctx = _base_context()
    ctx.pop("vix")
    score, _ = compute_d5_regime_vix(ctx)
    assert score == 5.0


# ---------------------------------------------------------------------------
# D6 — Backtest freshness
# ---------------------------------------------------------------------------


def test_d6_quality_backtest() -> None:
    """Sharpe 1.3*3 + WR 61/10 + min(87/20,5) = 3.9 + 6.1 + 5.0 = 15 -> clip 10."""
    ctx = _base_context()
    score, _ = compute_d6_backtest_freshness(ctx)
    assert score == 10.0


def test_d6_penalite_age_90j() -> None:
    """Age > 90j -> -1.5."""
    ctx = _base_context()
    ctx["backtest_stats"]["age_days"] = 120
    score, reason = compute_d6_backtest_freshness(ctx)
    assert score < 10.0  # penalite appliquee
    assert "age>90j" in reason


def test_d6_penalite_nb_trades_insuffisant() -> None:
    """nb_trades < 30 -> -2.0."""
    ctx = _base_context()
    ctx["backtest_stats"]["nb_trades"] = 20
    ctx["backtest_stats"]["sharpe_ratio"] = 0.5
    ctx["backtest_stats"]["win_rate"] = 50
    score, reason = compute_d6_backtest_freshness(ctx)
    # Sharpe 0.5*3 + WR 5 + min(1, 5) = 1.5 + 5 + 1 = 7.5, -2.0 = 5.5
    assert 5.0 <= score <= 6.0
    assert "nb_trades<30" in reason


# ---------------------------------------------------------------------------
# Agregat compute_deterministic_score
# ---------------------------------------------------------------------------


def test_weights_sum_to_one() -> None:
    """Verification ponderation v1.2 = 35+15+15+15+10+10 = 100%."""
    assert sum(WEIGHTS.values()) == pytest.approx(1.0, abs=1e-9)
    assert WEIGHTS["D1"] == 0.35
    assert WEIGHTS["D6"] == 0.10


def test_deterministic_score_in_bounds() -> None:
    """Score agrege dans [1.0, 10.0]."""
    ctx = _base_context()
    score, breakdown = compute_deterministic_score(ctx)
    assert 1.0 <= score <= 10.0
    assert set(breakdown.keys()) == {"D1", "D2", "D3", "D4", "D5", "D6"}


def test_deterministic_score_strong_signal() -> None:
    """Inputs forts (gap 0.82, RSI 58, news bullish, VIX bas, backtest solide) -> score elevé."""
    ctx = _base_context(
        edge_features={
            "gap_pct": 0.82,
            "sigma_gap_30d": 0.45,
            "sentiment_score": 0.7,
            "news_titles": ["news1", "news2"],
        },
        vix=12.0,
    )
    score, _ = compute_deterministic_score(ctx)
    # D1 9.1*0.35 + D2 10*0.15 + D3 7*0.15 + D4 5*0.15 + D5 8*0.10 + D6 10*0.10 = 8.34
    assert score >= 7.5


def test_deterministic_score_weak_signal_tc06() -> None:
    """TC-06 inputs faibles : gap 0.10, RSI 51, no news, no ORB -> score ~5.x."""
    ctx = {
        "edge_id": "H-A",
        "asset": {"name": "DAX"},
        "indicators": {
            "rsi_14": 51,
            "macd_signal": 8.0,
            "macd_histogram": 0.02,
            "bollinger_upper": 18450,
            "bollinger_lower": 18200,
            "bollinger_middle": 18325,
            "atr_14": 75,
        },
        "edge_features": {
            "gap_pct": 0.10,
            "sigma_gap_30d": 0.45,
            "orb_breakout": False,
            "volume_premarket_ratio": 0.9,
            "news_titles": [],
        },
        "ohlc_today_premarket": [
            {"ts": "2026-05-18T08:30", "open": 18415, "high": 18420, "low": 18410, "close": 18418, "volume": 8000},
        ],
        "backtest_stats": {"sharpe_ratio": 1.3, "win_rate": 61, "nb_trades": 87, "age_days": 30},
        "vix": 16.0,
    }
    score, breakdown = compute_deterministic_score(ctx)
    # D1 ~1.1, D2 ~6 (RSI 51 limite, MACD positif, prix > middle), D3 ~5, D4 ~5, D5 ~6, D6 ~10
    # Sigma : 1.1*0.35 + 6*0.15 + 5*0.15 + 5*0.15 + 6*0.10 + 10*0.10 = ~5.0-5.5
    assert 4.5 <= score <= 6.0
    assert breakdown["D1"] < 2.0  # gap faible
