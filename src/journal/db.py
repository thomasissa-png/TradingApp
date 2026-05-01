"""Initialisation et acces SQLite (journal.sqlite)."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path

from src.journal.schema import get_all_ddls
from src.lib.logger import get_logger

logger = get_logger(__name__)


def init_database(data_dir: Path | str) -> Path:
    """Cree journal.sqlite + 6 tables si elles n'existent pas. Idempotent.

    Args:
        data_dir: repertoire racine ou stocker journal.sqlite.

    Returns:
        Path du fichier SQLite cree/existant.
    """
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    db_path = data_path / "journal.sqlite"

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for ddl in get_all_ddls():
            conn.execute(ddl)
        conn.commit()

    logger.info("database_initialized", db_path=str(db_path))
    return db_path


@contextmanager
def get_connection(data_dir: Path | str) -> Iterator[sqlite3.Connection]:
    """Context manager pour une connexion sqlite3 (auto-close)."""
    db_path = Path(data_dir) / "journal.sqlite"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()
