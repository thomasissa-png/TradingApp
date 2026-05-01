"""Fixtures pytest partagees."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def env_minimal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, str]]:
    """Variables d'environnement minimales pour instancier Config en test."""
    env = {
        "TELEGRAM_BOT_TOKEN": "test-bot-token",
        "THOMAS_CHAT_ID": "123456",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "ANTHROPIC_MODEL_LIVE": "claude-sonnet-4-5-20250929",
        "ANTHROPIC_MODEL_RND": "claude-haiku-4-5",
        "TWELVEDATA_API_KEY": "td-test-key",
        "HEALTHCHECKS_PING_URL": "https://hc-ping.com/test-uuid",
        "STRATEGY_ACTIVE": "paper",
        "DATA_DIR": str(tmp_path / "data"),
        "LOG_LEVEL": "WARNING",
    }
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    yield env
