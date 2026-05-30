"""Tests mode signal main.py (Phase 2c-2 — pipeline complet).

Couverture (mocks ScoringEngine + Telegram + cron) :
- happy path BUY → format BUY + send
- no-trade : tous edges < threshold → format NO-TRADE + send
- férié FR : silence + ping success
- pause active : silence + ping success
- cutoff > 8h55 : silence + ping success
- Twelve Data fail : ERREUR DATA template
- Claude timeout : DEGRADED MODE template
- Idempotence INSERT signals
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, time
from pathlib import Path
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from src.ai.client import AnthropicClientError
from src.ai.tools import ScoringSignalOutput
from src.config import Config
from src.journal.db import (
    get_connection,
    init_database,
    insert_strategy_pause,
)
from src.main import (
    EXIT_ERROR,
    EXIT_OK,
    EXIT_SKIPPED,
    _select_best_signal,
    _select_top_signals,
    run_signal_mode,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def config(env_minimal: dict[str, str]) -> Config:
    return Config.from_env()


def _build_signal(direction: str, score: float = 7.5) -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000001",
        date="2026-05-04",
        hour_calc="08:42",
        asset="DAX Turbo Call",
        direction=direction,  # type: ignore[arg-type]
        entry=3.42 if direction != "NO_TRADE" else None,
        sl=3.21 if direction != "NO_TRADE" else None,
        tp=3.85 if direction != "NO_TRADE" else None,
        score=score,
        raison="gap haussier DAX +0,9%",
        edge_id="H-A",
        backtest_ref="#B-031",
        ALERT_flag="ALERT" if direction != "NO_TRADE" else "NO_TRADE",
        no_trade_reason=None if direction != "NO_TRADE" else "Score sous seuil",
        model_used="claude-sonnet-4-6",
    )


# ---------------------------------------------------------------------------
# _select_top_signals — unit (multi-signaux décision persona 2026-05-01)
# ---------------------------------------------------------------------------


def test_select_top_signals_returns_top_2_by_score() -> None:
    """2 signaux éligibles → top 2 triés par score DESC."""
    sig1 = _build_signal("BUY", score=7.0)
    sig2 = _build_signal("BUY", score=8.5)
    sig3 = _build_signal("SELL", score=7.8)
    top, max_score = _select_top_signals([sig1, sig2, sig3], threshold=7.0)
    assert len(top) == 2
    assert top[0].score == 8.5
    assert top[1].score == 7.8
    assert max_score == 8.5


def test_select_top_signals_caps_at_2_when_3_eligible() -> None:
    """3 signaux éligibles → seuls top 2 retournés (3e exclu)."""
    sig1 = _build_signal("BUY", score=9.0)
    sig2 = _build_signal("BUY", score=8.0)
    sig3 = _build_signal("SELL", score=7.2)
    top, _ = _select_top_signals([sig1, sig2, sig3], threshold=7.0)
    assert len(top) == 2
    scores = [s.score for s in top]
    assert 9.0 in scores
    assert 8.0 in scores
    assert 7.2 not in scores


def test_select_top_signals_returns_empty_when_all_below_threshold() -> None:
    sig1 = _build_signal("BUY", score=5.0)
    sig2 = _build_signal("SELL", score=5.5)
    top, max_score = _select_top_signals([sig1, sig2], threshold=7.0)
    assert top == []
    assert max_score == 5.5


def test_select_top_signals_excludes_no_trade() -> None:
    sig = _build_signal("NO_TRADE", score=8.0)
    top, max_score = _select_top_signals([sig], threshold=7.0)
    assert top == []
    assert max_score == 8.0


# ---------------------------------------------------------------------------
# _select_best_signal — unit (conservé pour compatibilité)
# ---------------------------------------------------------------------------


def test_select_best_signal_picks_highest_eligible() -> None:
    sig1 = _build_signal("BUY", score=7.0)
    sig2 = _build_signal("BUY", score=8.5)
    sig3 = _build_signal("SELL", score=7.8)
    best, max_score = _select_best_signal([sig1, sig2, sig3], threshold=7.0)
    assert best is not None
    assert best.score == 8.5
    assert max_score == 8.5


def test_select_best_signal_returns_none_when_all_below_threshold() -> None:
    sig1 = _build_signal("BUY", score=5.0)
    sig2 = _build_signal("SELL", score=5.5)
    best, max_score = _select_best_signal([sig1, sig2], threshold=7.0)
    assert best is None
    assert max_score == 5.5


def test_select_best_signal_returns_none_when_only_no_trade() -> None:
    sig = _build_signal("NO_TRADE", score=8.0)
    best, max_score = _select_best_signal([sig], threshold=7.0)
    assert best is None
    assert max_score == 8.0


def test_select_best_signal_empty_list() -> None:
    best, max_score = _select_best_signal([], threshold=7.0)
    assert best is None
    assert max_score == 0.0


# ---------------------------------------------------------------------------
# run_signal_mode — happy path BUY
# ---------------------------------------------------------------------------


@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_happy_path_buy(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    config: Config,
) -> None:
    # Mock now = 8h42 CET
    fake_now = datetime(2026, 5, 4, 8, 42)
    mock_dt.now.return_value = fake_now

    # Mock ScoringEngine.score → BUY signal score 7.5
    mock_engine = MagicMock()
    mock_engine.score.return_value = (_build_signal("BUY", score=7.5), {"sanity_checks_triggered": []})
    mock_engine_cls.return_value = mock_engine

    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)

    assert result == EXIT_OK
    mock_send.assert_called()
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "🟢 ACHAT" in sent_text or "ACHAT" in sent_text
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_no_trade_when_all_below_threshold(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    config: Config,
) -> None:
    fake_now = datetime(2026, 5, 4, 8, 42)
    mock_dt.now.return_value = fake_now

    mock_engine = MagicMock()
    # NO_TRADE returned (score < threshold paper 7.0)
    mock_engine.score.return_value = (
        _build_signal("NO_TRADE", score=5.5),
        {"sanity_checks_triggered": ["THRESHOLD"]},
    )
    mock_engine_cls.return_value = mock_engine

    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)

    assert result == EXIT_OK
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "NO-TRADE" in sent_text


# ---------------------------------------------------------------------------
# run_signal_mode — skip cases
# ---------------------------------------------------------------------------


@patch("src.main.get_holiday_name_fr", return_value=None)
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=False)
def test_signal_mode_skipped_silent_on_weekend(
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_holiday: MagicMock,
    config: Config,
) -> None:
    """Weekend : silence Telegram (Thomas sait que le marche est ferme)."""
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_not_called()
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


@patch("src.main.get_holiday_name_fr", return_value="14 juillet (Fete nationale)")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=False)
def test_signal_mode_sends_courtesy_message_on_french_holiday(
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_holiday: MagicMock,
    config: Config,
) -> None:
    """Phase 2f (A3) : jour ferie FR -> message Telegram courtoisie + ping success.

    Sans ce message, Thomas peut douter "le bot a-t-il plante ?" en silence legitime
    (cf §3.2 audit @testeur-persona-thomas Phase 2e).
    """
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_called_once()
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "⚪️" in sent_text
    assert "jour ferie FR" in sent_text
    assert "14 juillet" in sent_text
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
def test_signal_mode_sends_courtesy_message_when_paused(
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    config: Config,
) -> None:
    """Phase 2f (A3) : pause active -> message Telegram courtoisie avec end_date."""
    # Pré-insère pause active couvrant aujourd'hui
    init_database(config.data_dir)
    today = date.today()
    end = today
    with get_connection(config.data_dir) as conn:
        insert_strategy_pause(conn, today, end)

    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_called_once()
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "⚪️" in sent_text
    assert "pause active" in sent_text
    assert end.isoformat() in sent_text
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_skipped_when_after_cutoff(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    config: Config,
) -> None:
    # 9h05 CET — au-delà du cutoff 8h55
    mock_dt.now.return_value = datetime(2026, 5, 4, 9, 5)
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_not_called()
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


# ---------------------------------------------------------------------------
# run_signal_mode — Claude timeout / Twelve Data fail
# ---------------------------------------------------------------------------


@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_claude_timeout_sends_degraded(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    config: Config,
) -> None:
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 42)
    mock_engine = MagicMock()
    mock_engine.score.side_effect = AnthropicClientError("timeout > 45s")
    mock_engine_cls.return_value = mock_engine
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)
    assert result == EXIT_ERROR
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "DEGRADED MODE" in sent_text
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="failure")


@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_market_data_error_sends_data_error(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    config: Config,
) -> None:
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 42)
    mock_engine = MagicMock()
    mock_engine.score.side_effect = KeyError("volume_xetra_1m")
    mock_engine_cls.return_value = mock_engine
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)
    assert result == EXIT_ERROR
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "ERREUR DATA" in sent_text


# ---------------------------------------------------------------------------
# Idempotence INSERT signals
# ---------------------------------------------------------------------------


@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_inserts_signals_in_db(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    config: Config,
) -> None:
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 42)
    mock_engine = MagicMock()
    mock_engine.score.return_value = (
        _build_signal("BUY", score=7.5),
        {"sanity_checks_triggered": []},
    )
    mock_engine_cls.return_value = mock_engine
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)
    assert result == EXIT_OK

    # Vérifie qu'au moins 1 signal a été inséré (2 edges wave 1 = potentiellement 2 inserts)
    with get_connection(config.data_dir) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM signals")
        count = cursor.fetchone()[0]
    assert count >= 1


# ---------------------------------------------------------------------------
# Multi-signaux — décision persona 2026-05-01
# ---------------------------------------------------------------------------


def _build_signal_with_edge(
    direction: str, score: float, edge_id: str
) -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id=f"00000000-0000-4000-8000-{abs(hash(edge_id + str(score))) % (10**12):012d}",
        date="2026-05-04",
        hour_calc="08:42",
        asset="DAX Turbo Call" if edge_id == "H-C" else "CAC40 Turbo Call",
        direction=direction,  # type: ignore[arg-type]
        entry=4.05 if edge_id == "H-C" else 3.77,
        sl=3.84 if edge_id == "H-C" else 3.56,
        tp=4.56 if edge_id == "H-C" else 4.21,
        score=score,
        raison="breakout ORB" if edge_id == "H-C" else "gap haussier",
        edge_id=edge_id,
        backtest_ref="#B-009" if edge_id == "H-C" else "#B-031",
        ALERT_flag="ALERT",
        no_trade_reason=None,
        model_used="claude-sonnet-4-6",
    )


@patch("src.main.time_module.sleep")
@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_multi_two_signals_30s_apart(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    mock_sleep: MagicMock,
    config: Config,
) -> None:
    """2 edges ≥ seuil → 2 send_message + time.sleep(30) entre les 2 (décision persona 2026-05-01)."""
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 42)

    # Edge H-C (score 7.8) et H-A (score 7.4) — tous deux ≥ seuil paper 7.0
    mock_engine = MagicMock()
    mock_engine.score.side_effect = [
        (_build_signal_with_edge("BUY", score=7.8, edge_id="H-C"), {"sanity_checks_triggered": []}),
        (_build_signal_with_edge("BUY", score=7.4, edge_id="H-A"), {"sanity_checks_triggered": []}),
    ]
    mock_engine_cls.return_value = mock_engine
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)

    assert result == EXIT_OK
    # Exactement 2 appels send_message
    assert mock_send.call_count == 2
    # sleep(30) appelé exactement 1 fois entre les 2 envois
    mock_sleep.assert_called_once_with(30)
    # ping success
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


@patch("src.main.time_module.sleep")
@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_mode_multi_caps_at_2_max(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    mock_sleep: MagicMock,
    config: Config,
) -> None:
    """3 signaux ≥ seuil (wave 2 future) → seulement 2 messages envoyés (top 2 par score)."""
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 42)

    # Simuler 3 edges en injectant 3 retours score.side_effect
    # On override ACTIVE_EDGES_WAVE_1 temporairement via patch
    mock_engine = MagicMock()
    mock_engine.score.side_effect = [
        (_build_signal_with_edge("BUY", score=9.0, edge_id="H-C"), {"sanity_checks_triggered": []}),
        (_build_signal_with_edge("BUY", score=8.0, edge_id="H-A"), {"sanity_checks_triggered": []}),
        (_build_signal_with_edge("SELL", score=7.2, edge_id="H-B"), {"sanity_checks_triggered": []}),
    ]
    mock_engine_cls.return_value = mock_engine
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    with patch("src.main.ACTIVE_EDGES_WAVE_1", ["H-C", "H-A", "H-B"]):
        result = run_signal_mode(config)

    assert result == EXIT_OK
    # Cap à 2 : seuls les 2 meilleurs scores sont envoyés (9.0 + 8.0, pas 7.2)
    assert mock_send.call_count == 2
    # sleep(30) appelé 1 fois
    mock_sleep.assert_called_once_with(30)
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")
