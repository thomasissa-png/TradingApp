"""Tests integration TC-01 a TC-08 sur ScoringEngine (LLM mocke + pipeline reel).

Chaque TC reproduit le scenario decrit dans prompt-library.md v1.1 §5 et
edge-scoring-model.md v1.2 §5.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from anthropic import APITimeoutError

from src.ai.client import AnthropicClient, AnthropicClientError
from src.ai.tools import ScoringSignalOutput
from src.config import Config
from src.journal.db import (
    migrate_rnd_results_add_stats,
    migrate_strategy_state_add_mode,
    migrate_trades_add_mode,
)
from src.journal.schema import get_all_ddls
from src.scoring.engine import ScoringEngine

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ai"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _make_tool_use_response(input_data: dict[str, Any], model: str = "claude-sonnet-4-5-20250929") -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.name = "emit_signal_scoring"
    # Strip _note key (fixture metadata, pas dans le tool input reel)
    cleaned = {k: v for k, v in input_data.items() if not k.startswith("_")}
    block.input = cleaned

    resp = MagicMock()
    resp.content = [block]
    resp.model = model
    usage = MagicMock(
        input_tokens=4500, output_tokens=200,
        cache_read_input_tokens=0, cache_creation_input_tokens=0,
    )
    resp.usage = usage
    return resp


@pytest.fixture
def config(env_minimal: dict[str, str]) -> Config:  # noqa: ARG001
    return Config.from_env()


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    for ddl in get_all_ddls():
        conn.execute(ddl)
    # Phase 2d-bis : migrations idempotentes (R1 rnd_results stats, B2 trades.mode)
    migrate_strategy_state_add_mode(conn)
    migrate_trades_add_mode(conn)
    migrate_rnd_results_add_stats(conn)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# TC-01 — ACHAT DAX gap+ORB -> emit signal score 8.0
# ---------------------------------------------------------------------------


def test_tc01_achat_dax_gap_orb(config: Config, db_conn: sqlite3.Connection) -> None:
    inp = _load_fixture("inputs/TC-01-input.json")
    expected = _load_fixture("outputs/TC-01-expected.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config, db_conn=db_conn)
        signal, meta = engine.score(inp, mode="live")

    # Threshold paper = 7.0, score 8.0 >= 7.0 -> BUY confirme
    assert signal.direction == "BUY"
    assert signal.score == 8.0
    assert signal.ALERT_flag == "SAFE"
    assert meta["scoring_model_version"] == "scoring-model-v1.2"
    assert meta["prompt_version"] == "signal-scoring-v1.1"

    # Verifier INSERT SQLite
    row = db_conn.execute("SELECT direction, score, model_used FROM signals").fetchone()
    assert row[0] == "BUY"
    assert row[1] == 8.0


# ---------------------------------------------------------------------------
# TC-02 — VENTE CAC gap+news -> emit signal score 7.0
# ---------------------------------------------------------------------------


def test_tc02_vente_cac_news(config: Config) -> None:
    inp = _load_fixture("inputs/TC-02-input.json")
    expected = _load_fixture("outputs/TC-02-expected.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        signal, meta = engine.score(inp, mode="live")

    # Score 7.0 = threshold paper (limite stricte) -> SELL emis
    assert signal.direction == "SELL"
    assert signal.score == 7.0
    assert signal.entry > signal.tp  # SELL : entry > tp
    assert signal.entry < signal.sl  # SELL : sl > entry


# ---------------------------------------------------------------------------
# TC-03 — NO-TRADE flat -> seuil
# ---------------------------------------------------------------------------


def test_tc03_no_trade_flat(config: Config) -> None:
    inp = _load_fixture("inputs/TC-03-input.json")
    expected = _load_fixture("outputs/TC-03-expected.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        signal, meta = engine.score(inp, mode="live")

    assert signal.direction == "NO_TRADE"
    assert signal.entry is None
    assert signal.no_trade_reason is not None
    assert signal.score < meta["threshold_used"]


# ---------------------------------------------------------------------------
# TC-04 — Conflit news/technique -> SC plafond
# ---------------------------------------------------------------------------


def test_tc04_no_trade_conflict(config: Config) -> None:
    inp = _load_fixture("inputs/TC-04-input.json")
    expected = _load_fixture("outputs/TC-04-expected.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        signal, _ = engine.score(inp, mode="live")

    # Score 5.8 < threshold 7.0 -> NO_TRADE force par THRESHOLD
    assert signal.direction == "NO_TRADE"
    assert signal.ALERT_flag in ("NO_TRADE", "ALERT")


# ---------------------------------------------------------------------------
# TC-05 — Timeout total -> AnthropicClientError -> degraded mode
# ---------------------------------------------------------------------------


def test_tc05_timeout_degraded_mode(config: Config) -> None:
    inp = _load_fixture("inputs/TC-05-input.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        timeout_err = APITimeoutError(request=MagicMock())
        # Sonnet timeout + Haiku fallback timeout = AnthropicClientError
        mock_client.messages.create.side_effect = [timeout_err, timeout_err]
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        with pytest.raises(AnthropicClientError):
            engine.score(inp, mode="live")

        # Verifier que degraded_mode_signal produit un signal NO_TRADE valide
        degraded = engine.degraded_mode_signal(inp, "Anthropic timeout total")
        assert degraded.direction == "NO_TRADE"
        assert degraded.model_used == "degraded-mode"
        assert "DEGRADED MODE" in (degraded.no_trade_reason or "")


# ---------------------------------------------------------------------------
# TC-06 — Score LLM 8.0 vs deterministe ~5.2 -> SC7 plafond 7.0 ALERT
# ---------------------------------------------------------------------------


def test_tc06_sc7_plausibility_catch(config: Config) -> None:
    inp = _load_fixture("inputs/TC-06-input.json")
    expected = _load_fixture("outputs/TC-06-expected.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        signal, meta = engine.score(inp, mode="live")

    # Le LLM voulait 8.0 mais le deterministe est ~5.2 -> SC7 plafonne 7.0
    # Threshold paper = 7.0, score 7.0 >= 7.0 -> BUY mais avec ALERT
    # Note : la logique exacte depend de la valeur deterministe calculee runtime
    assert "SC7" in meta["sanity_checks_triggered"]
    assert signal.score <= 7.0
    # Score == threshold = passe (>= strict), mais ALERT doit etre visible
    if signal.direction == "BUY":
        assert signal.ALERT_flag == "ALERT"


# ---------------------------------------------------------------------------
# TC-07 — Prompt injection news -> sanitize OK, scoring normal
# ---------------------------------------------------------------------------


def test_tc07_prompt_injection_sanitized(config: Config) -> None:
    inp = _load_fixture("inputs/TC-07-input.json")
    expected = _load_fixture("outputs/TC-07-expected.json")

    captured_payloads: list[str] = []

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()

        def _capture_and_respond(**kwargs: Any) -> MagicMock:
            captured_payloads.append(str(kwargs["messages"]))
            return _make_tool_use_response(expected)

        mock_client.messages.create.side_effect = _capture_and_respond
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        signal, _ = engine.score(inp, mode="live")

    # Le payload envoye a Claude doit avoir l'injection STRIPPED
    assert len(captured_payloads) == 1
    assert "Ignore previous instructions" not in captured_payloads[0]
    assert "[INJECTION ATTEMPT REMOVED]" in captured_payloads[0]
    # Scoring normal
    assert signal.direction == "NO_TRADE"  # Score 5.5 < seuil 7.0


# ---------------------------------------------------------------------------
# TC-08 — OHLC partiel degrade -> ALERT, score plafond 7.0
# ---------------------------------------------------------------------------


def test_tc08_ohlc_partial_degraded(config: Config) -> None:
    inp = _load_fixture("inputs/TC-08-input.json")
    expected = _load_fixture("outputs/TC-08-expected.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        signal, _ = engine.score(inp, mode="live")

    # Score 7.0 = threshold paper -> BUY emis avec ALERT (degradation Twelve Data)
    assert signal.score == 7.0
    assert signal.ALERT_flag == "ALERT"


# ---------------------------------------------------------------------------
# Integration : threshold runtime selection
# ---------------------------------------------------------------------------


def test_threshold_paper_default(config: Config) -> None:
    """Paper mode : threshold = 7.0."""
    expected = _load_fixture("outputs/TC-01-expected.json")
    inp = _load_fixture("inputs/TC-01-input.json")

    with patch("src.ai.client.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_tool_use_response(expected)
        mock_anthropic_cls.return_value = mock_client

        engine = ScoringEngine(config)
        _, meta = engine.score(inp, mode="live")

    assert meta["threshold_used"] == 7.0
    assert meta["mode_used"] == "paper"
