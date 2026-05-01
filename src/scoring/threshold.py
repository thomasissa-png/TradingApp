"""Selection runtime du CONFIDENCE_THRESHOLD selon STRATEGY_ACTIVE.

Source : docs/ia/edge-scoring-model.md v1.2 §4.1 (split paper 7.0 / live 6.5).

Lookup SQLite via src/journal/db.py (table strategy_state) — fallback sur la valeur
de Config.strategy_active si la DB n'est pas accessible.
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Literal

from src.config import Config

logger = logging.getLogger(__name__)


def select_threshold(
    config: Config,
    db_conn: sqlite3.Connection | None = None,
) -> tuple[float, Literal["live", "paper"]]:
    """Retourne (threshold, mode) selon STRATEGY_ACTIVE.

    Ordre de priorite :
    1. Si db_conn fournie ET table strategy_state contient une ligne avec un mode -> SQLite
    2. Sinon -> config.strategy_active (env var)

    Note : la table strategy_state actuelle (cf src/journal/schema.py) ne contient PAS
    de colonne `mode` explicite (elle traque rnd_start_date + stop_loss_rnd). La selection
    runtime se fait donc via Config.strategy_active jusqu'a ce que cette colonne soit
    ajoutee Phase 2c-2 (US-11 /stop avec ALTER TABLE ADD COLUMN mode).
    """
    mode: Literal["live", "paper"] = "paper"

    if db_conn is not None:
        try:
            cursor = db_conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_state'"
            )
            if cursor.fetchone():
                # Verifier si la colonne `mode` existe (futur ALTER TABLE)
                cursor = db_conn.execute("PRAGMA table_info(strategy_state)")
                cols = [row[1] for row in cursor.fetchall()]
                if "mode" in cols:
                    cursor = db_conn.execute("SELECT mode FROM strategy_state WHERE id = 1")
                    row = cursor.fetchone()
                    mode = (
                        row[0] if row and row[0] in ("live", "paper") else _from_config(config)
                    )
                else:
                    mode = _from_config(config)
            else:
                mode = _from_config(config)
        except sqlite3.Error as exc:
            logger.warning("strategy_state lookup failed: %s — fallback Config", exc)
            mode = _from_config(config)
    else:
        mode = _from_config(config)

    threshold = (
        config.confidence_threshold_live if mode == "live" else config.confidence_threshold_paper
    )
    return threshold, mode


def _from_config(config: Config) -> Literal["live", "paper"]:
    """Lecture safe de Config.strategy_active avec fallback paper."""
    val = config.strategy_active
    if val == "live":
        return "live"
    return "paper"
