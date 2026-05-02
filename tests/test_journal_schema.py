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


def test_signals_table_has_raison_and_alert_flag(tmp_path: Path) -> None:
    """Phase 2f (A1) : colonnes raison + ALERT_flag presentes pour audit hebdo/mensuel.

    Sans ces colonnes, Thomas ne peut pas reconstituer 6 mois plus tard pourquoi
    le bot lui a envoye un signal donne (raison narrative + sortie SC3).
    """
    init_database(tmp_path)
    with sqlite3.connect(tmp_path / "journal.sqlite") as conn:
        cur = conn.execute("PRAGMA table_info(signals);")
        cols = {row[1] for row in cur.fetchall()}
    assert "raison" in cols, "Colonne signals.raison manquante (A1 audit Phase 2e)"
    assert "ALERT_flag" in cols, "Colonne signals.ALERT_flag manquante (A1 audit Phase 2e)"


def test_insert_signal_persists_raison_and_alert_flag(tmp_path: Path) -> None:
    """Phase 2f (A1) : insert_signal ecrit bien raison + ALERT_flag en DB."""
    from src.ai.tools import ScoringSignalOutput
    from src.journal.db import get_connection, insert_signal

    init_database(tmp_path)
    sig = ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000001",
        date="2026-05-04",
        hour_calc="08:42",
        asset="DAX Turbo Call",
        direction="BUY",
        entry=3.42,
        sl=3.21,
        tp=3.85,
        score=7.4,
        raison="gap haussier DAX +0,9% — top 15% des 250 ouvertures",
        edge_id="H-A",
        backtest_ref="#B-031",
        ALERT_flag="ALERT",
        no_trade_reason=None,
        model_used="claude-sonnet-4-6",
    )
    with get_connection(tmp_path) as conn:
        rowid = insert_signal(conn, sig)
        cursor = conn.execute(
            "SELECT raison, ALERT_flag FROM signals WHERE id = ?", (rowid,)
        )
        row = cursor.fetchone()
    assert row is not None
    assert row[0] == "gap haussier DAX +0,9% — top 15% des 250 ouvertures"
    assert row[1] == "ALERT"


def test_migrate_signals_add_raison_alert_flag_idempotent(tmp_path: Path) -> None:
    """Phase 2f (A1) : la migration peut etre rejouee sans erreur (gate idempotence)."""
    from src.journal.db import migrate_signals_add_raison_alert_flag

    init_database(tmp_path)
    with sqlite3.connect(tmp_path / "journal.sqlite") as conn:
        # Premiere execution OK (deja appliquee dans init_database, mais on rejoue)
        migrate_signals_add_raison_alert_flag(conn)
        # Deuxieme execution ne doit pas crasher
        migrate_signals_add_raison_alert_flag(conn)
        cur = conn.execute("PRAGMA table_info(signals);")
        cols = {row[1] for row in cur.fetchall()}
    assert "raison" in cols
    assert "ALERT_flag" in cols


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
