"""Initialisation et accès SQLite (journal.sqlite) + helpers Phase 2c-2.

Helpers ajoutés Phase 2c-2 (US-08 à US-12) :
- insert_signal, get_recent_signals
- insert_trade
- insert_strategy_decision, set_strategy_mode
- insert_strategy_pause, is_paused_today, cancel_active_pause
- insert_journal_week
- migrate_strategy_state_add_mode (ALTER TABLE idempotent)
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal

from src.ai.tools import ScoringSignalOutput
from src.journal.schema import get_all_ddls
from src.lib.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Init + connexion
# ---------------------------------------------------------------------------


def init_database(data_dir: Path | str) -> Path:
    """Crée journal.sqlite + 6 tables si elles n'existent pas. Idempotent.

    Inclut les migrations ALTER TABLE :
    - strategy_state.mode (Phase 2c-2)
    - trades.mode (Phase 2d-bis — B2 audit @qa)
    """
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    db_path = data_path / "journal.sqlite"

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for ddl in get_all_ddls():
            conn.execute(ddl)
        # Migrations idempotentes
        migrate_strategy_state_add_mode(conn)
        migrate_trades_add_mode(conn)
        migrate_rnd_results_add_stats(conn)
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


# ---------------------------------------------------------------------------
# Migration idempotente (cf agent fullstack — Migrations SQL idempotentes)
# ---------------------------------------------------------------------------


def migrate_strategy_state_add_mode(conn: sqlite3.Connection) -> None:
    """ALTER TABLE strategy_state ADD COLUMN mode (idempotent).

    Vérifie via PRAGMA table_info que la colonne n'existe pas déjà.
    Mode par défaut : 'paper' (US-11 — décision /stop = paper, /continue + critères = live).
    """
    cursor = conn.execute("PRAGMA table_info(strategy_state);")
    cols = {row[1] for row in cursor.fetchall()}
    if "mode" not in cols:
        conn.execute(
            "ALTER TABLE strategy_state ADD COLUMN mode TEXT NOT NULL DEFAULT 'paper';"
        )
        logger.info("migration_applied", change="strategy_state.mode")


def migrate_trades_add_mode(conn: sqlite3.Connection) -> None:
    """ALTER TABLE trades ADD COLUMN mode (Phase 2d-bis — B2 audit @qa).

    Trace si chaque trade a été passé en paper ou live. Sans cette colonne, on ne sait
    pas relire l'historique trades pour distinguer paper/live a posteriori
    (strategy_state.mode est l'état COURANT, pas historique).

    Idempotent via PRAGMA table_info.
    """
    cursor = conn.execute("PRAGMA table_info(trades);")
    cols = {row[1] for row in cursor.fetchall()}
    if "mode" not in cols:
        conn.execute(
            "ALTER TABLE trades ADD COLUMN mode TEXT NOT NULL DEFAULT 'paper';"
        )
        logger.info("migration_applied", change="trades.mode")


def migrate_rnd_results_add_stats(conn: sqlite3.Connection) -> None:
    """ALTER TABLE rnd_results ADD COLUMNS backtest_ref/win_rate/nb_trades/drawdown_max.

    Phase 2d-bis (R1 audit @design) : ajoute les colonnes nécessaires pour qu'un signal
    puisse afficher les stats du backtest référencé (`win_rate`, `nb_trades`, `drawdown_max`)
    via lookup `get_backtest_stats(backtest_ref)`.

    Idempotent via PRAGMA table_info — chaque colonne ajoutée individuellement.
    """
    cursor = conn.execute("PRAGMA table_info(rnd_results);")
    cols = {row[1] for row in cursor.fetchall()}
    if "backtest_ref" not in cols:
        conn.execute("ALTER TABLE rnd_results ADD COLUMN backtest_ref TEXT;")
        logger.info("migration_applied", change="rnd_results.backtest_ref")
    if "win_rate" not in cols:
        conn.execute("ALTER TABLE rnd_results ADD COLUMN win_rate REAL;")
        logger.info("migration_applied", change="rnd_results.win_rate")
    if "nb_trades" not in cols:
        conn.execute("ALTER TABLE rnd_results ADD COLUMN nb_trades INTEGER;")
        logger.info("migration_applied", change="rnd_results.nb_trades")
    if "drawdown_max" not in cols:
        conn.execute("ALTER TABLE rnd_results ADD COLUMN drawdown_max REAL;")
        logger.info("migration_applied", change="rnd_results.drawdown_max")


# ---------------------------------------------------------------------------
# Helpers signals (US-04 + US-08 + SC4/SC6)
# ---------------------------------------------------------------------------


def insert_signal(
    conn: sqlite3.Connection,
    signal: ScoringSignalOutput,
    metadata: dict[str, Any] | None = None,
    sanity_check_failed: list[str] | None = None,
) -> int:
    """INSERT signals avec 4 colonnes traçabilité.

    Returns: rowid (int) du signal inséré.
    """
    meta = metadata or {}
    sanity_failed_str = (
        ",".join(sanity_check_failed) if sanity_check_failed else None
    )

    cursor = conn.execute(
        """
        INSERT INTO signals (
            date, hour_calc, asset, direction, entry, sl, tp, score,
            scoring_model_version, prompt_version, model_used, sanity_check_failed,
            backtest_ref, no_trade_reason, latency_total_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            signal.date,
            signal.hour_calc,
            signal.asset,
            signal.direction,
            signal.entry,
            signal.sl,
            signal.tp,
            signal.score,
            meta.get("scoring_model_version", "v1.2"),
            meta.get("prompt_version", "v1.1"),
            meta.get("model_used", signal.model_used),
            sanity_failed_str,
            signal.backtest_ref,
            signal.no_trade_reason,
            meta.get("latency_ms"),
        ),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def get_recent_signals(conn: sqlite3.Connection, days: int) -> list[dict[str, Any]]:
    """SELECT signals des N derniers jours (pour SC4/SC6 anti-spam streak)."""
    cursor = conn.execute(
        """
        SELECT id, date, hour_calc, asset, direction, entry, sl, tp, score,
               scoring_model_version, prompt_version, model_used, sanity_check_failed,
               backtest_ref, no_trade_reason
        FROM signals
        WHERE date >= date('now', ?)
        ORDER BY date DESC, hour_calc DESC
        """,
        (f"-{int(days)} days",),
    )
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row, strict=False)) for row in cursor.fetchall()]


def get_signal_by_id(conn: sqlite3.Connection, signal_id: int) -> dict[str, Any] | None:
    """Récupère un signal par son ID (pour /trade — vérifier date du signal)."""
    cursor = conn.execute(
        "SELECT id, date, hour_calc, asset, direction FROM signals WHERE id = ?",
        (signal_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    cols = [c[0] for c in cursor.description]
    return dict(zip(cols, row, strict=False))


def get_latest_signal_today(
    conn: sqlite3.Connection, today_iso: str
) -> dict[str, Any] | None:
    """Dernier signal envoyé aujourd'hui (pour /trade — associer trade au signal du jour)."""
    cursor = conn.execute(
        """
        SELECT id, date, hour_calc, asset, direction
        FROM signals
        WHERE date = ? AND direction IN ('BUY','SELL')
        ORDER BY hour_calc DESC
        LIMIT 1
        """,
        (today_iso,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    cols = [c[0] for c in cursor.description]
    return dict(zip(cols, row, strict=False))


# ---------------------------------------------------------------------------
# Helpers trades (US-08 /trade)
# ---------------------------------------------------------------------------


def insert_trade(
    conn: sqlite3.Connection,
    signal_id: int,
    pl_brut: float,
    mae: float,
    mfe: float,
    pl_net: float | None = None,
) -> int:
    """INSERT trades — US-08 /trade <pl_brut> <mae> <mfe>.

    pl_net calculé automatiquement si non fourni : pl_brut - 0.99 (entrée) - 0.99 (sortie).
    Phase 2d-bis (B2) : la colonne `mode` est renseignée depuis strategy_state.mode au moment
    de l'INSERT (snapshot historique du mode actif quand le trade a été enregistré).
    """
    if pl_net is None:
        pl_net = pl_brut - 0.99 - 0.99  # frais Bourse Direct standard A/R

    # Snapshot mode actif (paper par défaut si non initialisé)
    current_mode = get_strategy_mode(conn)

    cursor = conn.execute(
        """
        INSERT INTO trades (
            signal_id, executed, pnl_brut, frais_bd, frais_bd_vente,
            pnl_net_avant_pfu, mae, mfe, exit_date, mode
        ) VALUES (?, 1, ?, 0.99, 0.99, ?, ?, ?, ?, ?)
        """,
        (
            signal_id,
            pl_brut,
            pl_net,
            mae,
            mfe,
            datetime.now(UTC).isoformat(timespec="seconds"),
            current_mode,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


# ---------------------------------------------------------------------------
# Helpers strategy_decisions + strategy_state (US-10 /continue, US-11 /stop)
# ---------------------------------------------------------------------------


def insert_strategy_decision(
    conn: sqlite3.Connection,
    month: str,
    decision: Literal["continue", "stop"],
    nb_criteres_ko: int = 0,
    confirmation_step: int = 1,
) -> int:
    """INSERT strategy_decisions (UNIQUE(month, decision)).

    Idempotent : si décision identique déjà présente pour le mois, retourne l'id existant.
    """
    cursor = conn.execute(
        "SELECT id FROM strategy_decisions WHERE month = ? AND decision = ?",
        (month, decision),
    )
    existing = cursor.fetchone()
    if existing:
        return int(existing[0])

    cursor = conn.execute(
        """
        INSERT INTO strategy_decisions (
            month, decision, decided_at, nb_criteres_ko, confirmation_step, is_active
        ) VALUES (?, ?, ?, ?, ?, 1)
        """,
        (
            month,
            decision,
            datetime.now(UTC).isoformat(timespec="seconds"),
            nb_criteres_ko,
            confirmation_step,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def set_strategy_mode(
    conn: sqlite3.Connection,
    mode: Literal["paper", "live"],
) -> None:
    """UPSERT strategy_state.mode (US-10 /continue ⇒ live, US-11 /stop ⇒ paper).

    Une seule ligne dans strategy_state (id=1).
    """
    conn.execute(
        """
        INSERT INTO strategy_state (id, mode, last_updated_at)
        VALUES (1, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            mode = excluded.mode,
            last_updated_at = CURRENT_TIMESTAMP
        """,
        (mode,),
    )
    conn.commit()


def get_strategy_mode(conn: sqlite3.Connection) -> Literal["paper", "live"]:
    """Lecture du mode actif (paper par défaut si absent)."""
    cursor = conn.execute("SELECT mode FROM strategy_state WHERE id = 1")
    row = cursor.fetchone()
    if row is None or not row[0]:
        return "paper"
    mode = str(row[0])
    return "live" if mode == "live" else "paper"


# ---------------------------------------------------------------------------
# Helpers strategy_pauses (US-12 /pause + /cancel-pause)
# ---------------------------------------------------------------------------


def insert_strategy_pause(
    conn: sqlite3.Connection,
    start: date | str,
    end: date | str,
) -> int:
    """INSERT strategy_pauses (US-12 — max 30 jours).

    Validation amont :
    - start <= end
    - durée <= 30 jours
    - Phase 2d-bis (B1 audit @qa) : overlap avec une pause active existante = REJET explicite
      (plus d'écrasement silencieux). Thomas doit /cancel-pause avant de poser une nouvelle pause.
    """
    start_str = start if isinstance(start, str) else start.isoformat()
    end_str = end if isinstance(end, str) else end.isoformat()

    # Validation
    s_date = date.fromisoformat(start_str)
    e_date = date.fromisoformat(end_str)
    if s_date > e_date:
        raise ValueError(f"start_date {start_str} > end_date {end_str}")
    delta_days = (e_date - s_date).days
    if delta_days > 30:
        raise ValueError(f"Durée pause {delta_days}j > 30j max (US-12)")

    # B1 — Détection overlap : test deux pauses se chevauchent ssi
    # (existing.start_date <= new.end_date) AND (existing.end_date >= new.start_date)
    cursor = conn.execute(
        """
        SELECT id, start_date, end_date FROM strategy_pauses
        WHERE status = 'active'
          AND start_date <= ?
          AND end_date >= ?
        LIMIT 1
        """,
        (end_str, start_str),
    )
    existing = cursor.fetchone()
    if existing is not None:
        raise ValueError(
            f"Pause overlap detected: une pause active existe sur la période "
            f"({existing[1]} → {existing[2]}). Utilisez /cancel-pause d'abord."
        )

    cursor = conn.execute(
        """
        INSERT INTO strategy_pauses (start_date, end_date, requested_at, status)
        VALUES (?, ?, ?, 'active')
        """,
        (start_str, end_str, datetime.now(UTC).isoformat(timespec="seconds")),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def cleanup_expired_pauses(conn: sqlite3.Connection) -> int:
    """Marque comme 'expired' les pauses actives dont end_date < aujourd'hui.

    Phase 2d-bis (B3 audit @qa) : nettoyage juste-à-temps appelé en début de
    is_paused_today. Sans ce cleanup, les pauses passées restent 'active' en DB
    (incohérent pour analytics et /cancel-pause peut annuler une pause déjà finie).

    Returns: nombre de pauses passées en 'expired'.
    """
    cursor = conn.execute(
        "UPDATE strategy_pauses SET status = 'expired' "
        "WHERE status = 'active' AND end_date < date('now')"
    )
    conn.commit()
    return cursor.rowcount


def is_paused_today(conn: sqlite3.Connection, today: date | str | None = None) -> bool:
    """True si une pause active couvre la date du jour.

    Phase 2d-bis (B3) : cleanup juste-à-temps des pauses expirées avant le check.
    """
    cleanup_expired_pauses(conn)
    today_str = (
        today
        if isinstance(today, str)
        else (today or date.today()).isoformat()
    )
    cursor = conn.execute(
        """
        SELECT id FROM strategy_pauses
        WHERE status = 'active'
          AND start_date <= ?
          AND end_date >= ?
        LIMIT 1
        """,
        (today_str, today_str),
    )
    return cursor.fetchone() is not None


def cancel_active_pause(conn: sqlite3.Connection) -> int:
    """Annule la pause active (US-12 edge /cancel-pause).

    Returns: nombre de pauses annulées (0 ou 1 normalement).
    """
    cursor = conn.execute(
        "UPDATE strategy_pauses SET status = 'cancelled' WHERE status = 'active'"
    )
    conn.commit()
    return cursor.rowcount


# ---------------------------------------------------------------------------
# Helpers journal_weeks (US-09 /journal-week)
# ---------------------------------------------------------------------------


def insert_journal_week(
    conn: sqlite3.Connection,
    week_start: date | str,
    week_end: date | str,
) -> int:
    """INSERT journal_weeks (US-09 — UNIQUE(week_start, week_end), idempotent).

    Returns: rowid existant ou nouveau.
    """
    start_str = week_start if isinstance(week_start, str) else week_start.isoformat()
    end_str = week_end if isinstance(week_end, str) else week_end.isoformat()

    cursor = conn.execute(
        "SELECT id FROM journal_weeks WHERE week_start = ? AND week_end = ?",
        (start_str, end_str),
    )
    existing = cursor.fetchone()
    if existing:
        return int(existing[0])

    cursor = conn.execute(
        """
        INSERT INTO journal_weeks (week_start, week_end, journal_week_sent_at, statut)
        VALUES (?, ?, ?, 'sent')
        """,
        (start_str, end_str, datetime.now(UTC).isoformat(timespec="seconds")),
    )
    conn.commit()
    return int(cursor.lastrowid or 0)


def get_backtest_stats(
    conn: sqlite3.Connection, backtest_ref: str
) -> dict[str, Any] | None:
    """Lookup stats backtest depuis rnd_results par backtest_ref.

    Phase 2d-bis (R1 audit @design) : alimente les 3 champs `win_rate_backtest`,
    `nb_trades_backtest`, `drawdown_max_backtest` du signal pour la ligne 5 du
    template ACHAT/VENTE (cf docs/copy/message-templates.md v1.2 §2).

    Returns:
        dict avec clés `win_rate`, `nb_trades`, `drawdown_max` (drawdown POSITIF en %),
        ou None si backtest_ref non trouvé. Convention : drawdown_max stocké en valeur
        positive (ex 17.0 pour DD -17%) — le template applique le signe.
    """
    cursor = conn.execute(
        """
        SELECT win_rate, nb_trades, drawdown_max
        FROM rnd_results
        WHERE backtest_ref = ?
        ORDER BY tested_at DESC
        LIMIT 1
        """,
        (backtest_ref,),
    )
    row = cursor.fetchone()
    if row is None or row[0] is None:
        return None
    return {
        "win_rate": float(row[0]),
        "nb_trades": int(row[1]) if row[1] is not None else 0,
        "drawdown_max": float(row[2]) if row[2] is not None else 0.0,
    }


def get_last_journal_week_criteria_ko(conn: sqlite3.Connection) -> int:
    """Retourne nb_criteres_ko de la dernière journal_week (pour /continue US-10).

    MVP : on lit depuis la dernière strategy_decision si présente, sinon 0.
    Heuristique : si la dernière décision a nb_criteres_ko >= 2, demander confirmation.
    """
    cursor = conn.execute(
        """
        SELECT nb_criteres_ko FROM strategy_decisions
        ORDER BY decided_at DESC LIMIT 1
        """
    )
    row = cursor.fetchone()
    return int(row[0]) if row else 0


__all__ = [
    "cancel_active_pause",
    "cleanup_expired_pauses",
    "get_backtest_stats",
    "get_connection",
    "get_last_journal_week_criteria_ko",
    "get_latest_signal_today",
    "get_recent_signals",
    "get_signal_by_id",
    "get_strategy_mode",
    "init_database",
    "insert_journal_week",
    "insert_signal",
    "insert_strategy_decision",
    "insert_strategy_pause",
    "insert_trade",
    "is_paused_today",
    "migrate_rnd_results_add_stats",
    "migrate_strategy_state_add_mode",
    "migrate_trades_add_mode",
    "set_strategy_mode",
]
