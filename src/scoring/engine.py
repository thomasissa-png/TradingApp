"""Pipeline orchestre — ScoringEngine (LLM + 6D + 7 SC + threshold + INSERT SQLite).

Pipeline (cf docs/ia/edge-scoring-model.md v1.2 §1.2) :
1. Sanitize news_titles (TC-07 prompt injection)
2. Compute deterministic score D1-D6 (sert reference SC7)
3. Build prompt context + appel AnthropicClient (tool use Sonnet/Haiku fallback)
4. Apply 7 sanity checks (SC1-SC7)
5. Select threshold (paper 7.0 / live 6.5 selon STRATEGY_ACTIVE)
6. Final decision : si score >= threshold AND direction != NO_TRADE -> emit, sinon NO_TRADE
7. INSERT SQLite avec 4 colonnes tracabilite (scoring_model_version, prompt_version,
   model_used, sanity_check_failed)
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any, Literal

from src.ai.client import (
    PROMPT_VERSION,
    SCORING_MODEL_VERSION,
    AnthropicClient,
    AnthropicClientError,
)
from src.ai.tools import ScoringSignalOutput, sanitize_news_titles
from src.config import Config
from src.scoring.dimensions import compute_deterministic_score
from src.scoring.sanity_checks import apply_all_sanity_checks
from src.scoring.threshold import select_threshold

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Orchestrateur scoring complet — interface publique consommee par src/main.py."""

    def __init__(
        self,
        config: Config,
        anthropic_client: AnthropicClient | None = None,
        db_conn: sqlite3.Connection | None = None,
    ) -> None:
        self.config = config
        self.anthropic_client = anthropic_client or AnthropicClient(config)
        self.db_conn = db_conn

    def score(
        self,
        market_context: dict[str, Any],
        mode: Literal["live", "rnd"] = "live",
        recent_signals: list[dict[str, Any]] | None = None,
        recent_30d_signals: list[dict[str, Any]] | None = None,
    ) -> tuple[ScoringSignalOutput, dict[str, Any]]:
        """Orchestrateur complet : sanitize -> deterministe -> LLM -> SC -> threshold.

        Args:
            market_context : input typé SignalScoringInput (cf prompt-library §1)
            mode : "live" (Sonnet) ou "rnd" (Haiku batch)
            recent_signals : 7 derniers jours pour SC4 (None = bootstrap off)
            recent_30d_signals : 30 derniers jours pour SC6 (None = bootstrap off)

        Returns:
            (signal_final, metadata) ou metadata contient :
              - latency_ms, tokens_*, model_used, fallback_haiku, retry_count
              - prompt_version, scoring_model_version
              - deterministic_score, deterministic_breakdown
              - sanity_checks_triggered : list[str]
              - threshold_used, mode_used (paper/live)

        Raises:
            AnthropicClientError : si LLM totalement indisponible (degraded mode amont).
        """
        # 1. Sanitize news titles (TC-07)
        ctx = self._sanitize_context(market_context)

        # 2. Score deterministe parallele (sert SC7)
        deterministic_score, breakdown = compute_deterministic_score(ctx)
        logger.debug("Deterministic score: %.2f, breakdown: %s", deterministic_score, breakdown)

        # 3. Appel LLM (tool use)
        llm_output, llm_meta = self.anthropic_client.score_signal(ctx, mode=mode)

        # 4. Apply 7 sanity checks
        signal, triggered = apply_all_sanity_checks(
            llm_output,
            ctx,
            recent_signals=recent_signals,
            recent_30d_signals=recent_30d_signals,
            deterministic_score=deterministic_score,
        )

        # 5. Select threshold runtime
        threshold, mode_used = select_threshold(self.config, db_conn=self.db_conn)

        # 6. Final decision : si score < threshold ET direction != NO_TRADE -> force NO_TRADE
        if signal.direction != "NO_TRADE" and signal.score < threshold:
            signal = signal.model_copy(
                update={
                    "direction": "NO_TRADE",
                    "entry": None,
                    "sl": None,
                    "tp": None,
                    "ALERT_flag": "NO_TRADE",
                    "no_trade_reason": (
                        f"Score {signal.score:.1f} < threshold {threshold} (mode {mode_used})"
                    ),
                }
            )
            triggered.append("THRESHOLD")

        metadata: dict[str, Any] = {
            **llm_meta,
            "scoring_model_version": SCORING_MODEL_VERSION,
            "prompt_version": PROMPT_VERSION,
            "deterministic_score": deterministic_score,
            "deterministic_breakdown": breakdown,
            "sanity_checks_triggered": triggered,
            "threshold_used": threshold,
            "mode_used": mode_used,
        }

        # 7. INSERT SQLite (si db_conn fournie)
        if self.db_conn is not None:
            self._insert_signal(signal, metadata)

        return signal, metadata

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Strip prompt injection patterns dans edge_features.news_titles."""
        ctx = dict(context)  # copie shallow
        features = dict(ctx.get("edge_features", {}) or {})
        if "news_titles" in features:
            titles = features["news_titles"]
            if isinstance(titles, list):
                features["news_titles"] = sanitize_news_titles(
                    [str(t) for t in titles]
                )
        ctx["edge_features"] = features
        return ctx

    def _insert_signal(
        self,
        signal: ScoringSignalOutput,
        metadata: dict[str, Any],
    ) -> None:
        """INSERT dans la table signals avec 4 colonnes tracabilite."""
        if self.db_conn is None:
            return

        sanity_failed = (
            ",".join(metadata.get("sanity_checks_triggered", []))
            if metadata.get("sanity_checks_triggered")
            else None
        )

        try:
            self.db_conn.execute(
                """
                INSERT INTO signals (
                    date, hour_calc, asset, direction, entry, sl, tp, score,
                    scoring_model_version, prompt_version, model_used, sanity_check_failed,
                    backtest_ref, no_trade_reason, latency_total_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.date,
                    signal.hour_calc,
                    signal.asset,
                    signal.direction,
                    signal.entry,
                    signal.sl,
                    signal.tp,
                    signal.score,
                    metadata["scoring_model_version"],
                    metadata["prompt_version"],
                    metadata["model_used"],
                    sanity_failed,
                    signal.backtest_ref,
                    signal.no_trade_reason,
                    metadata.get("latency_ms"),
                ),
            )
            self.db_conn.commit()
        except sqlite3.Error as exc:
            logger.error("INSERT signals failed: %s", exc)
            # Pas de re-raise : on ne veut pas perdre le signal Telegram pour un bug DB.

    def degraded_mode_signal(
        self,
        market_context: dict[str, Any],
        reason: str,
    ) -> ScoringSignalOutput:
        """Construit un signal NO_TRADE pour US-05 DEGRADED MODE (fallback total LLM).

        Utilise par src/main.py si AnthropicClientError leve.
        """
        date = market_context.get("date", "1970-01-01")
        hour_calc = market_context.get("hour_calc", "00:00")
        asset_obj = market_context.get("asset") or {}
        asset_name = (
            asset_obj.get("name") if isinstance(asset_obj, dict) else str(asset_obj)
        ) or "UNKNOWN"
        edge_id = market_context.get("edge_id", "H-A")
        backtest_ref = market_context.get("backtest_ref", "#B-000")

        return ScoringSignalOutput(
            id="00000000-0000-4000-8000-000000000000",
            date=date,
            hour_calc=hour_calc,
            asset=asset_name[:50],
            direction="NO_TRADE",
            entry=None,
            sl=None,
            tp=None,
            score=1.0,
            raison=f"DEGRADED MODE: {reason[:200]}",
            edge_id=edge_id,
            backtest_ref=backtest_ref,
            ALERT_flag="NO_TRADE",
            no_trade_reason=f"DEGRADED MODE: {reason[:200]}",
            model_used="degraded-mode",
        )


__all__ = ["AnthropicClientError", "ScoringEngine"]
