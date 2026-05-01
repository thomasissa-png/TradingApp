"""Tests handlers commandes Telegram (Phase 2c-2 — US-08 à US-12).

Couverture :
- /trade : valide format, INSERT, refuse signal périmé, refuse args invalides
- /pause : dates valides → INSERT ; start > end → erreur ; durée > 30j → erreur
- /cancel-pause : annule pause active
- /continue : nb_criteres_ko < 2 → live ; ≥ 2 → demande confirmation
- /stop : insert decision + mode paper
- /journal-week : INSERT idempotent
- Auth : commande de chat_id différent → ignore (None)
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from src.ai.tools import ScoringSignalOutput
from src.journal.db import (
    get_strategy_mode,
    init_database,
    insert_signal,
    insert_strategy_decision,
)
from src.telegram.bot import (
    CommandError,
    dispatch_command,
    handle_cancel_pause,
    handle_continue,
    handle_journal_week,
    handle_pause,
    handle_stop,
    handle_trade,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_conn(tmp_path: Path) -> sqlite3.Connection:
    """SQLite in-memory style : crée DB tmp, retourne connection avec migration."""
    init_database(tmp_path)
    db_path = tmp_path / "journal.sqlite"
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _signal_buy(date_iso: str) -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000001",
        date=date_iso,
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
        model_used="claude-sonnet-4-5-20250929",
    )


# ---------------------------------------------------------------------------
# /trade — US-08
# ---------------------------------------------------------------------------


def test_trade_inserts_with_valid_args(db_conn: sqlite3.Connection) -> None:
    today = date.today()
    insert_signal(db_conn, _signal_buy(today.isoformat()))
    msg = handle_trade(db_conn, ["42.50", "-18.00", "65.30"], today=today)
    assert "Trade #" in msg
    assert "+42.50" in msg or "42.50" in msg
    cursor = db_conn.execute("SELECT COUNT(*) FROM trades")
    assert cursor.fetchone()[0] == 1


def test_trade_accepts_french_decimal_comma(db_conn: sqlite3.Connection) -> None:
    today = date.today()
    insert_signal(db_conn, _signal_buy(today.isoformat()))
    msg = handle_trade(db_conn, ["42,50", "-18,00", "65,30"], today=today)
    assert "Trade #" in msg


def test_trade_refuses_wrong_arg_count(db_conn: sqlite3.Connection) -> None:
    with pytest.raises(CommandError, match="Usage"):
        handle_trade(db_conn, ["42.50", "-18.00"], today=date.today())


def test_trade_refuses_non_numeric_args(db_conn: sqlite3.Connection) -> None:
    today = date.today()
    insert_signal(db_conn, _signal_buy(today.isoformat()))
    with pytest.raises(CommandError, match="numériques"):
        handle_trade(db_conn, ["abc", "def", "ghi"], today=today)


def test_trade_refuses_when_no_signal_today(db_conn: sqlite3.Connection) -> None:
    # Aucun signal inséré
    with pytest.raises(CommandError, match="Aucun signal"):
        handle_trade(db_conn, ["42.50", "-18.00", "65.30"], today=date.today())


def test_trade_confirmation_shows_paper_mode_by_default(
    db_conn: sqlite3.Connection,
) -> None:
    """Phase 2f (A2) : confirmation /trade affiche [PAPER 📝] par defaut.

    Le mode par defaut de strategy_state est 'paper' (cf migration B2). Sans
    feedback visuel explicite dans la confirmation, Thomas peut shooter a cote
    en pensant etre en live (cf §2.2 audit @testeur-persona-thomas Phase 2e).
    """
    today = date.today()
    insert_signal(db_conn, _signal_buy(today.isoformat()))
    msg = handle_trade(db_conn, ["42.50", "-18.00", "65.30"], today=today)
    assert "[PAPER" in msg
    assert "📝" in msg
    assert "(simulé)" in msg


def test_trade_confirmation_shows_live_mode_when_active(
    db_conn: sqlite3.Connection,
) -> None:
    """Phase 2f (A2) : confirmation /trade affiche [LIVE 💰] apres /continue.

    Verifie que la confirmation reflete bien strategy_state.mode courant
    (snapshot DB au moment du INSERT trade + lecture pour affichage).
    """
    from src.journal.db import set_strategy_mode

    today = date.today()
    insert_signal(db_conn, _signal_buy(today.isoformat()))
    set_strategy_mode(db_conn, "live")
    msg = handle_trade(db_conn, ["42.50", "-18.00", "65.30"], today=today)
    assert "[LIVE" in msg
    assert "💰" in msg
    assert "PFU" in msg


# ---------------------------------------------------------------------------
# /pause — US-12
# ---------------------------------------------------------------------------


def test_pause_valid_dates(db_conn: sqlite3.Connection) -> None:
    msg = handle_pause(db_conn, ["2026-07-15", "2026-07-29"])
    assert "Pause #" in msg
    assert "2026-07-15" in msg
    assert "2026-07-29" in msg


def test_pause_refuses_start_after_end(db_conn: sqlite3.Connection) -> None:
    with pytest.raises(CommandError, match="start_date"):
        handle_pause(db_conn, ["2026-07-29", "2026-07-15"])


def test_pause_refuses_more_than_30_days(db_conn: sqlite3.Connection) -> None:
    with pytest.raises(CommandError, match="30j"):
        handle_pause(db_conn, ["2026-07-01", "2026-08-15"])


def test_pause_refuses_invalid_date_format(db_conn: sqlite3.Connection) -> None:
    with pytest.raises(CommandError, match="Format date"):
        handle_pause(db_conn, ["2026/07/15", "2026/07/29"])


def test_pause_refuses_wrong_arg_count(db_conn: sqlite3.Connection) -> None:
    with pytest.raises(CommandError, match="Usage"):
        handle_pause(db_conn, ["2026-07-15"])


def test_pause_refuses_overlap_with_active(db_conn: sqlite3.Connection) -> None:
    """Phase 2d-bis (B1) : 2e /pause chevauchant la 1re est REJETEE explicitement.

    Le handler doit transformer le ValueError de db.py en CommandError lisible
    pour Thomas (avec mention `/cancel-pause`).
    """
    handle_pause(db_conn, ["2026-07-15", "2026-07-29"])
    with pytest.raises(CommandError, match=r"overlap|cancel-pause"):
        handle_pause(db_conn, ["2026-07-20", "2026-08-05"])


# ---------------------------------------------------------------------------
# /cancel-pause — US-12 edge
# ---------------------------------------------------------------------------


def test_cancel_pause_when_active(db_conn: sqlite3.Connection) -> None:
    handle_pause(db_conn, ["2026-07-15", "2026-07-29"])
    msg = handle_cancel_pause(db_conn)
    assert "annulée" in msg


def test_cancel_pause_when_none(db_conn: sqlite3.Connection) -> None:
    msg = handle_cancel_pause(db_conn)
    assert "Aucune pause" in msg


# ---------------------------------------------------------------------------
# /continue — US-10
# ---------------------------------------------------------------------------


def test_continue_below_2_criteria_goes_live(db_conn: sqlite3.Connection) -> None:
    msg = handle_continue(db_conn, current_month="2026-05")
    assert "Continuation" in msg
    assert "live" in msg
    assert get_strategy_mode(db_conn) == "live"


def test_continue_with_2_or_more_criteria_asks_confirmation(
    db_conn: sqlite3.Connection,
) -> None:
    # Pré-remplir une décision avec nb_criteres_ko=3
    insert_strategy_decision(
        db_conn, month="2026-04", decision="continue", nb_criteres_ko=3
    )
    msg = handle_continue(db_conn, current_month="2026-05")
    assert "Attention" in msg
    assert "3 critères KO" in msg
    # Pas de transition immédiate
    assert get_strategy_mode(db_conn) == "paper"


def test_continue_idempotent_same_month(db_conn: sqlite3.Connection) -> None:
    handle_continue(db_conn, current_month="2026-05")
    handle_continue(db_conn, current_month="2026-05")
    cursor = db_conn.execute(
        "SELECT COUNT(*) FROM strategy_decisions WHERE month = '2026-05' AND decision = 'continue'"
    )
    assert cursor.fetchone()[0] == 1


# ---------------------------------------------------------------------------
# /stop — US-11
# ---------------------------------------------------------------------------


def test_stop_sets_paper_mode(db_conn: sqlite3.Connection) -> None:
    # D'abord passer en live
    handle_continue(db_conn, current_month="2026-05")
    assert get_strategy_mode(db_conn) == "live"
    # Puis stop
    msg = handle_stop(db_conn, current_month="2026-05")
    assert "paper trading" in msg
    assert get_strategy_mode(db_conn) == "paper"


def test_stop_idempotent_same_month(db_conn: sqlite3.Connection) -> None:
    handle_stop(db_conn, current_month="2026-05")
    handle_stop(db_conn, current_month="2026-05")
    cursor = db_conn.execute(
        "SELECT COUNT(*) FROM strategy_decisions WHERE month = '2026-05' AND decision = 'stop'"
    )
    assert cursor.fetchone()[0] == 1


# ---------------------------------------------------------------------------
# /journal-week — US-09
# ---------------------------------------------------------------------------


def test_journal_week_renders_summary_and_inserts(db_conn: sqlite3.Connection) -> None:
    stats = {
        "week_n": 18,
        "week_start": "2026-04-27",
        "week_end": "2026-05-01",
        "signaux": 5,
        "trades": 3,
        "no_trades": 2,
        "pnl_brut": 124.50,
        "pnl_net": 118.54,
        "win_rate": 66,
        "gagnants": 2,
        "perdants": 1,
        "drawdown": 8,
        "meilleur_signal": "DAX",
        "meilleur_pct": 4.2,
        "meilleur_ref": "#B-031",
        "pire_signal": "CAC40",
        "pire_pct": -1.8,
        "pire_ref": "#B-018",
        "pertes_consecutives": 1,
    }
    msg = handle_journal_week(
        db_conn,
        stats=stats,
        week_start=date(2026, 4, 27),
        week_end=date(2026, 5, 1),
    )
    assert "Résumé semaine 18" in msg
    cursor = db_conn.execute("SELECT COUNT(*) FROM journal_weeks")
    assert cursor.fetchone()[0] == 1


def test_journal_week_idempotent(db_conn: sqlite3.Connection) -> None:
    stats = {"week_n": 18, "week_start": "2026-04-27", "week_end": "2026-05-01"}
    handle_journal_week(
        db_conn, stats=stats,
        week_start=date(2026, 4, 27), week_end=date(2026, 5, 1),
    )
    handle_journal_week(
        db_conn, stats=stats,
        week_start=date(2026, 4, 27), week_end=date(2026, 5, 1),
    )
    cursor = db_conn.execute("SELECT COUNT(*) FROM journal_weeks")
    assert cursor.fetchone()[0] == 1


# ---------------------------------------------------------------------------
# Auth — dispatch_command
# ---------------------------------------------------------------------------


def test_dispatch_unauthorized_chat_id_returns_none(db_conn: sqlite3.Connection) -> None:
    """Un sender_chat_id différent de allowed_chat_id → silencieux."""
    result = dispatch_command(
        db_conn,
        sender_chat_id="999999",
        allowed_chat_id="123456",
        command="/continue",
        args=[],
    )
    assert result is None
    # Aucune décision insérée
    cursor = db_conn.execute("SELECT COUNT(*) FROM strategy_decisions")
    assert cursor.fetchone()[0] == 0


def test_dispatch_authorized_routes_to_handler(db_conn: sqlite3.Connection) -> None:
    result = dispatch_command(
        db_conn,
        sender_chat_id="123456",
        allowed_chat_id="123456",
        command="/stop",
        args=[],
    )
    assert result is not None
    assert "paper" in result.lower()


def test_dispatch_unknown_command_returns_none(db_conn: sqlite3.Connection) -> None:
    result = dispatch_command(
        db_conn,
        sender_chat_id="123456",
        allowed_chat_id="123456",
        command="/unknown",
        args=[],
    )
    assert result is None


def test_dispatch_command_error_returns_message(db_conn: sqlite3.Connection) -> None:
    """CommandError → message d'erreur formaté avec ❌."""
    result = dispatch_command(
        db_conn,
        sender_chat_id="123456",
        allowed_chat_id="123456",
        command="/pause",
        args=["2026/01/01"],
    )
    assert result is not None
    assert result.startswith("❌")
