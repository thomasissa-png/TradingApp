"""Chargement et validation des variables d'environnement (Pydantic Settings).

Conforme au split modele Sonnet live + Haiku R&D (cf docs/ia/ai-architecture.md)
et aux split-thresholds CONFIDENCE_THRESHOLD_PAPER/_LIVE (cf edge-scoring-model v1.1).
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytz
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration runtime — toutes les vars critiques sont validees au boot.

    Regles bloquantes :
    - L002 lessons-learned : ANTHROPIC_MODEL_LIVE doit etre un tag exact
      (ex `claude-sonnet-4-6` minor-family alias OK, ou `claude-sonnet-4-6-20250929`),
      JAMAIS un alias `*-latest` ou `*-newest` cross-family.
    - data_dir cree si absent (idempotent).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Telegram (mini-jalon J+7) ---
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    thomas_chat_id: str = Field(..., alias="THOMAS_CHAT_ID")

    # --- Anthropic (Phase 2c — preset des maintenant pour valider config) ---
    anthropic_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    anthropic_model_live: str = Field(
        default="claude-sonnet-4-6", alias="ANTHROPIC_MODEL_LIVE"
    )
    anthropic_model_rnd: str = Field(
        default="claude-haiku-4-5-20251001", alias="ANTHROPIC_MODEL_RND"
    )

    # --- Twelve Data ---
    twelvedata_api_key: str = Field(..., alias="TWELVEDATA_API_KEY")

    # --- Healthchecks.io (G4 reliability) ---
    healthchecks_ping_url: str = Field(..., alias="HEALTHCHECKS_PING_URL")

    # --- Strategie / scoring ---
    strategy_active: str = Field(default="paper", alias="STRATEGY_ACTIVE")  # 'live' | 'paper'
    confidence_threshold_paper: float = Field(default=7.0, alias="CONFIDENCE_THRESHOLD_PAPER")
    confidence_threshold_live: float = Field(default=6.5, alias="CONFIDENCE_THRESHOLD_LIVE")

    # --- Stockage / paths ---
    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- Timezone ---
    tz_name: str = Field(default="Europe/Paris", alias="TZ")

    # ----- Validators -----

    @field_validator("anthropic_model_live", "anthropic_model_rnd")
    @classmethod
    def _no_alias_in_model_tag(cls, v: str) -> str:
        """L002 : interdit `*-latest`, `*-newest`, `*-current` dans les tags modele.

        Un alias = regression silencieuse possible (cross-family swap Anthropic).
        Le tag exact est l'unique source de verite reproductible.
        """
        forbidden = ("-latest", "-newest", "-current")
        if any(tok in v for tok in forbidden):
            raise ValueError(
                f"ANTHROPIC_MODEL_* doit etre un tag exact, pas un alias. Recu: '{v}'. "
                "Reference : docs/lessons-learned.md L002."
            )
        return v

    @field_validator("strategy_active")
    @classmethod
    def _valid_strategy(cls, v: str) -> str:
        if v not in ("live", "paper"):
            raise ValueError(f"STRATEGY_ACTIVE doit etre 'live' ou 'paper', recu: '{v}'")
        return v

    @field_validator("data_dir")
    @classmethod
    def _ensure_data_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v

    # ----- Helpers -----

    def now_iso(self) -> str:
        """Timestamp ISO 8601 avec timezone Europe/Paris."""
        return datetime.now(pytz.timezone(self.tz_name)).isoformat(timespec="seconds")

    @property
    def confidence_threshold(self) -> float:
        """Threshold actif selon STRATEGY_ACTIVE (cf edge-scoring-model v1.1 §4)."""
        return (
            self.confidence_threshold_live
            if self.strategy_active == "live"
            else self.confidence_threshold_paper
        )

    @classmethod
    def from_env(cls) -> Config:
        """Chargement explicite — leve une erreur ValidationError si vars manquantes."""
        # pydantic-settings lit automatiquement .env + os.environ ; methode-helper pour
        # uniformiser l'API d'invocation (cf src/main.py).
        return cls()  # type: ignore[call-arg]


def load_config_from_dict(env: dict[str, str]) -> Config:
    """Helper test — charge Config depuis un dict (override os.environ ponctuel)."""
    saved = {k: os.environ.get(k) for k in env}
    try:
        os.environ.update(env)
        return Config.from_env()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
