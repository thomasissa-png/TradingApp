"""Tests Config — validation env vars + L002 (no alias modele)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.config import Config


def test_config_loads_with_minimal_env(env_minimal: dict[str, str]) -> None:
    """Config se charge sans erreur si toutes les vars critiques sont presentes."""
    config = Config.from_env()
    assert config.telegram_bot_token == "test-bot-token"
    assert config.thomas_chat_id == "123456"
    assert config.strategy_active == "paper"
    assert config.confidence_threshold == 7.0  # paper threshold


def test_config_raises_when_telegram_token_missing(
    monkeypatch: pytest.MonkeyPatch, env_minimal: dict[str, str]
) -> None:
    """Si TELEGRAM_BOT_TOKEN manque, ValidationError leve."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN")
    with pytest.raises(ValidationError):
        Config.from_env()


def test_config_rejects_alias_latest(
    monkeypatch: pytest.MonkeyPatch, env_minimal: dict[str, str]
) -> None:
    """L002 : ANTHROPIC_MODEL_LIVE='*-latest' doit etre rejete."""
    monkeypatch.setenv("ANTHROPIC_MODEL_LIVE", "claude-sonnet-latest")
    with pytest.raises(ValidationError) as exc_info:
        Config.from_env()
    assert "tag exact" in str(exc_info.value) or "L002" in str(exc_info.value)


def test_config_rejects_alias_newest(
    monkeypatch: pytest.MonkeyPatch, env_minimal: dict[str, str]
) -> None:
    """L002 etendu : '*-newest' doit aussi etre rejete."""
    monkeypatch.setenv("ANTHROPIC_MODEL_RND", "claude-haiku-newest")
    with pytest.raises(ValidationError):
        Config.from_env()


def test_confidence_threshold_switches_with_strategy_active(
    monkeypatch: pytest.MonkeyPatch, env_minimal: dict[str, str]
) -> None:
    """STRATEGY_ACTIVE=live -> threshold 6.5, paper -> 7.0 (cf scoring-model v1.1)."""
    monkeypatch.setenv("STRATEGY_ACTIVE", "live")
    config = Config.from_env()
    assert config.confidence_threshold == 6.5

    monkeypatch.setenv("STRATEGY_ACTIVE", "paper")
    config = Config.from_env()
    assert config.confidence_threshold == 7.0


def test_strategy_active_invalid_value_rejected(
    monkeypatch: pytest.MonkeyPatch, env_minimal: dict[str, str]
) -> None:
    """STRATEGY_ACTIVE en dehors de {live, paper} -> rejete."""
    monkeypatch.setenv("STRATEGY_ACTIVE", "production")
    with pytest.raises(ValidationError):
        Config.from_env()
