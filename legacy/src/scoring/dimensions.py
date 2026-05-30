"""6 dimensions deterministes du scoring (D1-D6) — pondereations v1.2.

Source : docs/ia/edge-scoring-model.md v1.2 §2 (35/15/15/15/10/10 = 100%).

Chaque fonction est PURE : input dict context -> tuple (score 0-10, raison textuelle).
Aucun appel reseau, aucun side-effect, full testable isolement.

Le score deterministe agrege sert de reference pour SC7 (plausibilite LLM vs deterministe).
"""

from __future__ import annotations

from typing import Any

# Ponderations v1.2 (cf edge-scoring-model.md §2.1)
WEIGHTS = {
    "D1": 0.35,
    "D2": 0.15,
    "D3": 0.15,
    "D4": 0.15,
    "D5": 0.10,
    "D6": 0.10,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Ponderations doivent sommer a 1.0"


def _clip(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    """Borne value dans [lo, hi]."""
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# D1 — Force du signal d'edge (35 %, v1.2)
# Variable selon edge_id : H-A gap normalise, H-C ORB amplitude, H-E sentiment.
# ---------------------------------------------------------------------------

def compute_d1_force_signal(context: dict[str, Any]) -> tuple[float, str]:
    """D1 — Force du signal d'edge selon edge_id.

    H-A : |gap_pct| / sigma_gap_30d * 5 (gap normalise par ecart-type historique)
    H-B : meme formule que H-A (fade aussi base sur |gap|)
    H-C : (breakout_amplitude / atr_14) * 4
    H-D : |sp_overnight_pct| / sigma_overnight_30d * 5
    H-E : |sentiment_score| * 10
    H-F : |spread_sigma| * 3 (deviation statistique spot/futures)
    H-G : |nikkei_close_pct| * 4 (sentiment Asie)
    """
    edge_id = context.get("edge_id", "")
    features = context.get("edge_features", {}) or {}

    if edge_id in ("H-A", "H-B"):
        gap = abs(float(features.get("gap_pct", 0.0)))
        sigma = float(features.get("sigma_gap_30d") or 0.5)
        sigma = max(sigma, 0.1)  # eviter division par zero / micro-sigma
        score = _clip(gap / sigma * 5.0)
        return score, f"D1 H-A/B: gap {gap:.2f}% / sigma {sigma:.2f} = {score:.1f}"

    if edge_id == "H-C":
        amplitude = abs(float(features.get("breakout_amplitude", 0.0)))
        atr = float(context.get("indicators", {}).get("atr_14") or 1.0)
        atr = max(atr, 0.01)
        score = _clip((amplitude / atr) * 4.0)
        return score, f"D1 H-C: breakout {amplitude:.2f} / ATR {atr:.2f} = {score:.1f}"

    if edge_id == "H-D":
        sp = abs(float(features.get("sp_overnight_pct", 0.0)))
        sigma = float(features.get("sigma_overnight_30d") or 0.4)
        sigma = max(sigma, 0.1)
        score = _clip(sp / sigma * 5.0)
        return score, f"D1 H-D: SP overnight {sp:.2f}% / sigma {sigma:.2f} = {score:.1f}"

    if edge_id == "H-E":
        sentiment = abs(float(features.get("sentiment_score", 0.0)))
        score = _clip(sentiment * 10.0)
        return score, f"D1 H-E: |sentiment| {sentiment:.2f} * 10 = {score:.1f}"

    if edge_id == "H-F":
        spread_sigma = abs(float(features.get("spread_sigma", 0.0)))
        score = _clip(spread_sigma * 3.0)
        return score, f"D1 H-F: spread {spread_sigma:.2f} sigma * 3 = {score:.1f}"

    if edge_id == "H-G":
        nikkei = abs(float(features.get("nikkei_close_pct", 0.0)))
        score = _clip(nikkei * 4.0)
        return score, f"D1 H-G: |Nikkei close| {nikkei:.2f}% * 4 = {score:.1f}"

    return 0.0, f"D1 edge inconnu: {edge_id}"


# ---------------------------------------------------------------------------
# D2 — Confluence indicateurs techniques (15 %, v1.1)
# 3/3 alignes = 10, 2/3 = 6, 1/3 = 3, 0/3 = 0
# ---------------------------------------------------------------------------

def compute_d2_confluence_indicators(context: dict[str, Any]) -> tuple[float, str]:
    """D2 — Confluence RSI/MACD/Bollinger avec direction signal."""
    indicators = context.get("indicators", {}) or {}
    direction = (
        context.get("direction_hint")
        or context.get("edge_features", {}).get("direction_expected")
        or _infer_direction_from_edge(context)
    )

    rsi = float(indicators.get("rsi_14") or 50)
    macd_h = float(indicators.get("macd_histogram") or 0)
    bb_upper = float(indicators.get("bollinger_upper") or 0)
    bb_lower = float(indicators.get("bollinger_lower") or 0)
    bb_middle = float(indicators.get("bollinger_middle") or (bb_upper + bb_lower) / 2)

    # Prix de reference : derniere cloture premarket si dispo, sinon middle
    ohlc_pre = context.get("ohlc_today_premarket") or []
    last_close = float(ohlc_pre[-1]["close"]) if ohlc_pre else bb_middle

    aligned = 0
    if direction == "BUY":
        if rsi > 50:
            aligned += 1
        if macd_h > 0:
            aligned += 1
        if last_close > bb_middle:
            aligned += 1
    elif direction == "SELL":
        if rsi < 50:
            aligned += 1
        if macd_h < 0:
            aligned += 1
        if last_close < bb_middle:
            aligned += 1
    else:
        # NO_TRADE/inconnu -> neutre
        return 5.0, "D2: direction neutre/inconnue, fallback 5.0"

    score_map = {0: 0.0, 1: 3.0, 2: 6.0, 3: 10.0}
    score = score_map[aligned]
    return score, f"D2: {aligned}/3 indicateurs alignes ({direction}) = {score:.1f}"


def _infer_direction_from_edge(context: dict[str, Any]) -> str:
    """Heuristique direction par defaut a partir de edge_features."""
    features = context.get("edge_features", {}) or {}
    edge_id = context.get("edge_id", "")
    if edge_id == "H-B":  # fade -> direction opposee au gap
        gap = float(features.get("gap_pct", 0))
        return "SELL" if gap > 0 else "BUY"
    if edge_id == "H-A":
        gap = float(features.get("gap_pct", 0))
        return "BUY" if gap > 0 else "SELL"
    if edge_id == "H-C":
        return str(features.get("orb_direction", "BUY")).upper()
    if edge_id == "H-E":
        s = float(features.get("sentiment_score", 0))
        return "BUY" if s > 0 else "SELL"
    return "BUY"


# ---------------------------------------------------------------------------
# D3 — Contexte news pre-marche (15 %)
# Plafond 7.0 si news_titles absent / < 2 titres (cf prompt-library §4.2)
# ---------------------------------------------------------------------------

def compute_d3_news_context(context: dict[str, Any]) -> tuple[float, str]:
    """D3 — Sentiment news pre-marche, plafond 7.0 si news indispo."""
    features = context.get("edge_features", {}) or {}
    news_titles = features.get("news_titles") or []
    sentiment = float(features.get("sentiment_score") or 0.0)
    direction = (
        context.get("direction_hint")
        or features.get("direction_expected")
        or _infer_direction_from_edge(context)
    )

    if len(news_titles) < 2:
        # News indispo -> plafond 7.0 (pas de sur-confiance)
        score = min(7.0, abs(sentiment) * 10.0) if sentiment else 5.0
        return score, f"D3: news indispo ({len(news_titles)} titres) -> plafond 7.0 = {score:.1f}"

    # Aligne direction et signe(sentiment) -> bonus, sinon penalite
    sentiment_dir = "BUY" if sentiment > 0 else "SELL"
    if direction == sentiment_dir:
        score = _clip(abs(sentiment) * 10.0)
        return score, f"D3: sentiment {sentiment:+.2f} aligne {direction} = {score:.1f}"
    else:
        # Penalite signal contre-news
        score = _clip(abs(sentiment) * 5.0 * -1 + 5.0, 0.0, 10.0)
        return score, f"D3: sentiment {sentiment:+.2f} CONTRE direction {direction} = {score:.1f}"


# ---------------------------------------------------------------------------
# D4 — Volatilite realisee vs implicite (15 %)
# > 1.2 sur-vol = 8, 0.8-1.2 = 5, < 0.8 sous-vol = 3
# ---------------------------------------------------------------------------

def compute_d4_volatility(context: dict[str, Any]) -> tuple[float, str]:
    """D4 — Ratio sigma_realisee / sigma_implicite."""
    indicators = context.get("indicators", {}) or {}
    realized = float(indicators.get("sigma_realized") or indicators.get("atr_14") or 0)
    implied = float(indicators.get("sigma_implied") or 0)

    if implied <= 0:
        # Pas de vol implicite -> neutre
        return 5.0, "D4: sigma_implied indispo, neutre 5.0"

    ratio = realized / implied
    if ratio > 1.2:
        return 8.0, f"D4: sur-vol (ratio {ratio:.2f}) = 8.0"
    if ratio >= 0.8:
        return 5.0, f"D4: vol normale (ratio {ratio:.2f}) = 5.0"
    return 3.0, f"D4: sous-vol (ratio {ratio:.2f}) = 3.0"


# ---------------------------------------------------------------------------
# D5 — Regime de marche VIX/V2X (10 %)
# VIX < 15 trend = 8, 15-25 range = 6, > 25 panic = 3, indispo = 5
# ---------------------------------------------------------------------------

def compute_d5_regime_vix(context: dict[str, Any]) -> tuple[float, str]:
    """D5 — Classification regime VIX (ou V2X EU)."""
    vix = context.get("vix") or context.get("v2x")
    if vix is None:
        return 5.0, "D5: VIX/V2X indispo, neutre 5.0"

    vix_val = float(vix)
    if vix_val < 15:
        return 8.0, f"D5: VIX {vix_val:.1f} trend = 8.0"
    if vix_val <= 25:
        return 6.0, f"D5: VIX {vix_val:.1f} range = 6.0"
    return 3.0, f"D5: VIX {vix_val:.1f} panic = 3.0"


# ---------------------------------------------------------------------------
# D6 — Reference backtest (10 %, v1.2)
# Sharpe*3 + win_rate/10 + min(nb_trades/20, 5), penalite si > 90j ou nb_trades < 30
# ---------------------------------------------------------------------------

def compute_d6_backtest_freshness(context: dict[str, Any]) -> tuple[float, str]:
    """D6 — Qualite statistique du backtest reference."""
    stats = context.get("backtest_stats", {}) or {}
    sharpe = float(stats.get("sharpe_ratio") or 0)
    win_rate = float(stats.get("win_rate") or 0)
    nb_trades = int(stats.get("nb_trades") or 0)
    age_days = int(stats.get("age_days") or 0)

    raw = sharpe * 3.0 + win_rate / 10.0 + min(nb_trades / 20.0, 5.0)
    # Cap a 10.0 AVANT les penalites (sinon penalite invisible sur signaux forts)
    score = min(raw, 10.0)

    penalties: list[str] = []
    if age_days > 90:
        score -= 1.5
        penalties.append("age>90j -1.5")
    if nb_trades < 30:
        score -= 2.0
        penalties.append("nb_trades<30 -2.0")

    score = _clip(score)
    pen_str = f" [{', '.join(penalties)}]" if penalties else ""
    return (
        score,
        f"D6: Sharpe {sharpe:.1f}*3 + WR {win_rate:.0f}/10 + nb {nb_trades}/20 = {score:.1f}{pen_str}",
    )


# ---------------------------------------------------------------------------
# Agregat pondere (v1.2)
# ---------------------------------------------------------------------------

def compute_deterministic_score(
    context: dict[str, Any],
) -> tuple[float, dict[str, float]]:
    """Calcule le score deterministe pondere D1-D6 v1.2.

    Returns (score_pondere [1.0, 10.0], breakdown_par_dimension).
    Sert de reference SC7 (plausibilite LLM vs deterministe).
    """
    d1, _ = compute_d1_force_signal(context)
    d2, _ = compute_d2_confluence_indicators(context)
    d3, _ = compute_d3_news_context(context)
    d4, _ = compute_d4_volatility(context)
    d5, _ = compute_d5_regime_vix(context)
    d6, _ = compute_d6_backtest_freshness(context)

    breakdown = {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6}

    weighted = (
        d1 * WEIGHTS["D1"]
        + d2 * WEIGHTS["D2"]
        + d3 * WEIGHTS["D3"]
        + d4 * WEIGHTS["D4"]
        + d5 * WEIGHTS["D5"]
        + d6 * WEIGHTS["D6"]
    )
    # Borne stricte [1.0, 10.0] pour coherence avec ScoringSignalOutput
    score = max(1.0, min(10.0, weighted))
    return score, breakdown
