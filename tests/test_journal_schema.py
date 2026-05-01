"""Tests schema SQLite — creation idempotente des 6 tables."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.journal.db import init_database
from src.journal.schema import EXPECTED_TABLES


def _existing_tables(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return {row[0] for row in cur.fetchall()}


def test_init_creates_all_expected_tables(tmp_path: Path) -> None:
    """Toutes les tables attendues (signals, trades, journal_weeks, ...) sont creees."""
    db_path = init_database(tmp_path)
    assert db_path.exists()
    tables = _existing_tables(db_path)
    for expected in EXPECTED_TABLES:
        assert expected in tables, f"Table manquante: {expected}"


def test_init_database_idempotent(tmp_path: Path) -> None:
    """Deux appels successifs ne doivent pas lever d'exception."""
    init_database(tmp_path)
    init_database(tmp_path)  # ne doit pas crash
    tables = _existing_tables(tmp_path / "journal.sqlite")
    for expected in EXPECTED_TABLES:
        assert expected in tables


def test_signals_table_has_traceability_columns(tmp_path: Path) -> None:
    """Les 4 colonnes de tracabilite scoring sont presentes (kpi-framework §4)."""
    init_database(tmp_path)
    with sqlite3.connect(tmp_path / "journal.sqlite") as conn:
        cur = conn.execute("PRAGMA table_info(signals);")
        cols = {row[1] for row in cur.fetchall()}
    for required in (
        "scoring_model_version",
        "prompt_version",
        "model_used",
        "sanity_check_failed",
    ):
        assert required in cols, f"Colonne tracabilite manquante: {required}"


def test_strategy_decisions_unique_constraint(tmp_path: Path) -> None:
    """UNIQUE(month, decision) — empeche doublon de decision pour un meme mois."""
    init_database(tmp_path)
    with sqlite3.connect(tmp_path / "journal.sqlite") as conn:
        conn.execute(
            "INSERT INTO strategy_decisions (month, decision, decided_at, nb_criteres_ko, "
            "confirmation_step, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            ("2026-05", "continue", "2026-05-01T08:05:00Z", 0, 1, 1),
        )
        conn.commit()
        try:
            conn.execute(
                "INSERT INTO strategy_decisions (month, decision, decided_at, nb_criteres_ko, "
                "confirmation_step, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                ("2026-05", "continue", "2026-05-01T09:00:00Z", 0, 1, 1),
            )
            conn.commit()
            raised = False
        except sqlite3.IntegrityError:
            raised = True
    assert raised, "UNIQUE(month, decision) doit empecher le doublon"
