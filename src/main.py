"""TradingApp entry point — Phase 2c-2 (mode signal complet).

Modes :
  --mode=hello       : pousse un hello-world Telegram + ping healthchecks (J+7)
  --mode=signal      : pipeline scoring complet — Twelve Data + ScoringEngine + Telegram
  --mode=journal-week: génère résumé hebdo (US-09 — vendredi 18h00 CET)
  --mode=live/paper  : alias de --mode=signal (STRATEGY_ACTIVE definit le seuil)

Usage Replit (Cron Deployment) : commande `python -m src.main --mode=signal` déclenchée
par cron Replit lundi-vendredi à 8h40 CET (cf docs/infra/infra-audit.md §2 + REPLIT_ACTIONS.md).
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, time, timedelta
from typing import Any

import pytz

from src.ai.client import AnthropicClient, AnthropicClientError
from src.ai.tools import ScoringSignalOutput
from src.config import Config
from src.journal.db import (
    get_connection,
    get_recent_signals,
    get_strategy_mode,
    init_database,
    insert_journal_week,
    insert_signal,
    is_paused_today,
)
from src.lib.healthchecks import ping_healthchecks
from src.lib.logger import get_logger
from src.scheduler.cron import is_market_day_fr
from src.scoring.engine import ScoringEngine
from src.telegram.bot import send_message
from src.telegram.templates import (
    format_buy_signal,
    format_data_error,
    format_degraded_mode,
    format_no_trade,
    format_sell_signal,
    format_weekly_summary,
    render_hello_world,
)

logger = get_logger(__name__)

EXIT_OK = 0
EXIT_SKIPPED = 0  # pas un échec : jour férié / week-end / pause
EXIT_ERROR = 1

PARIS_TZ = pytz.timezone("Europe/Paris")
SIGNAL_CUTOFF = time(8, 55)  # US-06 : silence Telegram au-delà

# Edges actifs en wave 1 (cf functional-specs §2 — H-A + H-C MVP)
ACTIVE_EDGES_WAVE_1 = ["H-A", "H-C"]


# ---------------------------------------------------------------------------
# Mode hello (mini-jalon J+7 — conservé strict)
# ---------------------------------------------------------------------------


def run_hello_world(config: Config) -> int:
    """Mini-jalon J+7 : push hello-world Telegram + ping healthchecks."""
    init_database(config.data_dir)

    if not is_market_day_fr():
        logger.info("market_closed", reason="not_a_market_day_fr")
        ping_healthchecks(config.healthchecks_ping_url, status="success")
        return EXIT_SKIPPED

    msg = render_hello_world(ts=config.now_iso(), mode=config.strategy_active)

    response = send_message(
        bot_token=config.telegram_bot_token,
        chat_id=config.thomas_chat_id,
        text=msg,
    )

    if response is None:
        logger.error("hello_world_failed", reason="telegram_send_failed")
        ping_healthchecks(config.healthchecks_ping_url, status="failure")
        return EXIT_ERROR

    ping_healthchecks(config.healthchecks_ping_url, status="success")
    logger.info("hello_world_sent", chat_id=config.thomas_chat_id, mode=config.strategy_active)
    return EXIT_OK


# ---------------------------------------------------------------------------
# Mode signal — pipeline complet
# ---------------------------------------------------------------------------


def _build_market_context(
    edge_id: str, today_iso: str, hour_calc: str
) -> dict[str, Any]:
    """Construit le market_context input pour ScoringEngine.score().

    MVP Phase 2c-2 : stub minimal si TWELVEDATA_API_KEY absent (les tests utilisent mocks).
    En prod : MarketDataLoader Phase 2b alimentera ce dict (US-04).
    """
    # Asset selon edge (mapping wave 1)
    asset_map = {
        "H-A": {"name": "DAX Turbo Call", "ticker": "DAX"},
        "H-C": {"name": "DAX Turbo Call", "ticker": "DAX"},
    }
    asset = asset_map.get(edge_id, {"name": "DAX", "ticker": "DAX"})

    return {
        "date": today_iso,
        "hour_calc": hour_calc,
        "asset": asset,
        "edge_id": edge_id,
        "backtest_ref": "#B-031" if edge_id == "H-A" else "#B-009",
        "edge_features": {
            "news_titles": [],
            # Stub : en prod, MarketDataLoader remplit les vraies features.
        },
    }


def _select_best_signal(
    signals: list[ScoringSignalOutput],
    threshold: float,
) -> tuple[ScoringSignalOutput | None, float]:
    """Sélectionne le meilleur signal éligible (BUY/SELL et score >= threshold).

    Returns:
        (best_signal_or_None, max_score_seen)
    """
    if not signals:
        return None, 0.0
    max_score = max(s.score for s in signals)
    eligible = [
        s for s in signals
        if s.direction in ("BUY", "SELL") and s.score >= threshold
    ]
    if not eligible:
        return None, max_score
    best = max(eligible, key=lambda s: s.score)
    return best, max_score


def _format_signal(signal: ScoringSignalOutput, paper_mode: bool) -> str:
    """Dispatch BUY → format_buy_signal, SELL → format_sell_signal, autre → format_no_trade."""
    if signal.direction == "BUY":
        return format_buy_signal(signal, paper_mode=paper_mode)
    if signal.direction == "SELL":
        return format_sell_signal(signal, paper_mode=paper_mode)
    return format_no_trade(signal, max_score=signal.score)


def run_signal_mode(config: Config) -> int:
    """Pipeline scoring complet — Twelve Data + ScoringEngine + Telegram (Phase 2c-2).

    Séquence (cf docstring module) :
      1. Init DB + check holiday FR + check pause + check cutoff 8h55
      2. Pour chaque edge actif wave 1 : ScoringEngine.score()
      3. Sélection best signal (BUY/SELL et score >= threshold)
      4. Format + envoi Telegram (paper_mode prefix selon strategy_state.mode)
      5. INSERT signals + ping healthchecks
    """
    init_database(config.data_dir)

    # 1. Holiday FR
    if not is_market_day_fr():
        logger.info("signal_skipped", reason="not_a_market_day_fr")
        ping_healthchecks(config.healthchecks_ping_url, status="success")
        return EXIT_SKIPPED

    # 2. Pause active (US-12)
    with get_connection(config.data_dir) as conn:
        if is_paused_today(conn):
            logger.info("signal_skipped", reason="pause_active")
            ping_healthchecks(config.healthchecks_ping_url, status="success")
            return EXIT_SKIPPED

    # 3. Cutoff 8h55 strict (US-06)
    now_paris = datetime.now(PARIS_TZ)
    if now_paris.time() > SIGNAL_CUTOFF:
        logger.warning(
            "signal_cutoff_exceeded",
            now=now_paris.isoformat(timespec="seconds"),
            cutoff=SIGNAL_CUTOFF.isoformat(),
        )
        # Silence Telegram (cf US-06) — mais ping success quand même (healthchecks attend ping/jour)
        ping_healthchecks(config.healthchecks_ping_url, status="success")
        return EXIT_SKIPPED

    today_iso = now_paris.date().isoformat()
    hour_calc = now_paris.strftime("%H:%M")

    # 4. ScoringEngine pour chaque edge wave 1
    anthropic_client = AnthropicClient(config)
    engine = ScoringEngine(config, anthropic_client=anthropic_client)
    signals: list[ScoringSignalOutput] = []
    sanity_failures: list[list[str]] = []

    with get_connection(config.data_dir) as conn:
        # bootstrap recent signals pour SC4/SC6
        try:
            recent_7d = get_recent_signals(conn, days=7)
            recent_30d = get_recent_signals(conn, days=30)
        except sqlite3.Error as exc:
            logger.warning("recent_signals_fetch_failed", error=str(exc))
            recent_7d = []
            recent_30d = []

        for edge_id in ACTIVE_EDGES_WAVE_1:
            ctx = _build_market_context(edge_id, today_iso, hour_calc)
            try:
                signal, metadata = engine.score(
                    ctx,
                    mode="live",
                    recent_signals=recent_7d,
                    recent_30d_signals=recent_30d,
                )
                signals.append(signal)
                sanity_failures.append(metadata.get("sanity_checks_triggered", []))
            except AnthropicClientError as exc:
                logger.error("claude_unavailable", edge=edge_id, error=str(exc))
                # Fallback DEGRADED MODE — envoyer 1 message + arrêter
                msg = format_degraded_mode(
                    "claude_timeout",
                    context={"asset": "Signal du jour"},
                )
                _send(config, msg)
                ping_healthchecks(config.healthchecks_ping_url, status="failure")
                return EXIT_ERROR
            except (KeyError, ValueError) as exc:
                # Twelve Data partiel — ERREUR DATA
                logger.error("market_data_error", edge=edge_id, error=str(exc))
                msg = format_data_error(
                    {
                        "asset": "Signal du jour",
                        "missing_field": str(exc)[:100],
                        "hour": hour_calc,
                    }
                )
                _send(config, msg)
                ping_healthchecks(config.healthchecks_ping_url, status="failure")
                return EXIT_ERROR

        # 5. Sélection best signal
        threshold = config.confidence_threshold
        best, max_score = _select_best_signal(signals, threshold)
        paper_mode = get_strategy_mode(conn) == "paper"

        # 6. Format + envoi
        if best is not None:
            formatted = _format_signal(best, paper_mode=paper_mode)
        elif signals:
            # Aucun éligible — NO-TRADE avec contexte du meilleur score vu
            best_no_trade = max(signals, key=lambda s: s.score)
            formatted = format_no_trade(best_no_trade, max_score=max_score)
        else:
            # Aucun signal du tout (pipeline vide)
            logger.error("no_signal_generated", reason="empty_engine_output")
            ping_healthchecks(config.healthchecks_ping_url, status="failure")
            return EXIT_ERROR

        sent = _send(config, formatted)

        # 7. INSERT signals (best ou tous — MVP : on insère tous pour traçabilité)
        for sig, sanity in zip(signals, sanity_failures, strict=False):
            try:
                insert_signal(conn, sig, sanity_check_failed=sanity)
            except sqlite3.Error as exc:
                logger.error("insert_signal_failed", error=str(exc))

        if not sent:
            ping_healthchecks(config.healthchecks_ping_url, status="failure")
            return EXIT_ERROR

    ping_healthchecks(config.healthchecks_ping_url, status="success")
    logger.info(
        "signal_mode_done",
        nb_signals=len(signals),
        best_direction=best.direction if best else "NO_TRADE",
        paper_mode=paper_mode,
    )
    return EXIT_OK


def _send(config: Config, text: str) -> bool:
    """Helper envoi Telegram avec parse_mode Markdown (cf format strict ** **)."""
    response = send_message(
        bot_token=config.telegram_bot_token,
        chat_id=config.thomas_chat_id,
        text=text,
        parse_mode="Markdown",
    )
    return response is not None


# ---------------------------------------------------------------------------
# Mode journal-week (US-09)
# ---------------------------------------------------------------------------


def run_journal_week_mode(config: Config) -> int:
    """Génère résumé hebdo (vendredi 18h00 CET — US-09).

    MVP : compute stats minimal (signaux + trades de la semaine) + send.
    """
    init_database(config.data_dir)

    now_paris = datetime.now(PARIS_TZ)
    today = now_paris.date()
    # Lundi de la semaine en cours
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=4)  # vendredi
    week_n = today.isocalendar()[1]

    with get_connection(config.data_dir) as conn:
        # Compte signaux + trades de la semaine
        cursor = conn.execute(
            """
            SELECT COUNT(*) as n,
                   SUM(CASE WHEN direction IN ('BUY','SELL') THEN 1 ELSE 0 END) as trades_signaled,
                   SUM(CASE WHEN direction = 'NO_TRADE' THEN 1 ELSE 0 END) as no_trades
            FROM signals
            WHERE date BETWEEN ? AND ?
            """,
            (week_start.isoformat(), week_end.isoformat()),
        )
        row = cursor.fetchone()
        n_signals = int(row[0] or 0) if row else 0
        n_signaled = int(row[1] or 0) if row else 0
        n_no_trade = int(row[2] or 0) if row else 0

        cursor = conn.execute(
            """
            SELECT COUNT(*) as n,
                   COALESCE(SUM(pnl_brut), 0) as pnl_brut,
                   COALESCE(SUM(pnl_net_avant_pfu), 0) as pnl_net,
                   SUM(CASE WHEN pnl_brut > 0 THEN 1 ELSE 0 END) as gagnants,
                   SUM(CASE WHEN pnl_brut <= 0 THEN 1 ELSE 0 END) as perdants
            FROM trades
            WHERE date(exit_date) BETWEEN ? AND ?
            """,
            (week_start.isoformat(), week_end.isoformat()),
        )
        trade_row = cursor.fetchone()
        nb_trades = int(trade_row[0] or 0) if trade_row else 0
        pnl_brut = float(trade_row[1] or 0) if trade_row else 0.0
        pnl_net = float(trade_row[2] or 0) if trade_row else 0.0
        gagnants = int(trade_row[3] or 0) if trade_row else 0
        perdants = int(trade_row[4] or 0) if trade_row else 0
        win_rate = (gagnants / nb_trades * 100) if nb_trades > 0 else 0.0

        paper_mode = get_strategy_mode(conn) == "paper"

        stats: dict[str, Any] = {
            "week_n": week_n,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "signaux": n_signals,
            "trades": n_signaled,
            "no_trades": n_no_trade,
            "pnl_brut": pnl_brut,
            "pnl_net": pnl_net,
            "win_rate": win_rate,
            "gagnants": gagnants,
            "perdants": perdants,
            "drawdown": 0,  # MVP : calculé Phase 2d
            "meilleur_signal": "—",
            "meilleur_pct": 0,
            "meilleur_ref": "—",
            "pire_signal": "—",
            "pire_pct": 0,
            "pire_ref": "—",
            "pertes_consecutives": 0,
        }

        msg = format_weekly_summary(stats, paper_mode=paper_mode)
        sent = _send(config, msg)

        if sent:
            insert_journal_week(conn, week_start=week_start, week_end=week_end)

    if not sent:
        ping_healthchecks(config.healthchecks_ping_url, status="failure")
        return EXIT_ERROR

    ping_healthchecks(config.healthchecks_ping_url, status="success")
    return EXIT_OK


# ---------------------------------------------------------------------------
# CLI dispatcher
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point. Retourne un exit code Unix-style."""
    try:
        config = Config.from_env()
    except Exception as e:
        print(f'{{"level":"FATAL","msg":"config_load_failed","error":"{e}"}}', file=sys.stderr)
        return EXIT_ERROR

    mode = "--mode=hello"
    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode = arg
            break

    if mode == "--mode=hello":
        return run_hello_world(config)
    if mode == "--mode=signal":
        return run_signal_mode(config)
    if mode == "--mode=journal-week":
        return run_journal_week_mode(config)
    if mode in ("--mode=live", "--mode=paper"):
        # Alias de --mode=signal — STRATEGY_ACTIVE détermine le seuil.
        return run_signal_mode(config)

    logger.error("unknown_mode", mode=mode)
    return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
