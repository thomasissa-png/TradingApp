# ruff: noqa: RUF001
"""Wrapper Telegram — envoi de messages + handlers commandes Phase 2c-2.

Synchrone via API HTTP directe (cohérent avec mini-jalon J+7).

Commandes implémentées (US-08 à US-12) :
- /trade <pl_brut> <mae> <mfe> : enregistre P&L réel (US-08)
- /pause YYYY-MM-DD YYYY-MM-DD : suspend signaux période (US-12)
- /cancel-pause : annule pause active
- /continue : valide mois suivant ⇒ mode live (US-10)
- /stop : suspend stratégie ⇒ mode paper (US-11)
- /journal-week : génère résumé hebdo (US-09)

Authentification : refuse toute commande hors THOMAS_CHAT_ID.
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from typing import Any

import pytz
import requests

from src.journal.db import (
    cancel_active_pause,
    get_last_journal_week_criteria_ko,
    get_latest_signal_today,
    get_strategy_mode,
    insert_journal_week,
    insert_strategy_decision,
    insert_strategy_pause,
    insert_trade,
    set_strategy_mode,
)
from src.lib.logger import get_logger
from src.telegram.templates import format_weekly_summary

logger = get_logger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"
SEND_TIMEOUT_S = 10.0
PARIS_TZ = pytz.timezone("Europe/Paris")

# Cutoff /trade : signal périmé après 9h00 (cron 8h40 du jour)
TRADE_CUTOFF_HOUR = 9


# ---------------------------------------------------------------------------
# send_message (existant — conservé strict)
# ---------------------------------------------------------------------------


def send_message(
    bot_token: str,
    chat_id: str,
    text: str,
    parse_mode: str | None = None,
) -> dict[str, Any] | None:
    """Envoie un message Telegram via Bot API (sendMessage)."""
    if not bot_token or not chat_id:
        logger.error("telegram_send_skipped", reason="missing_token_or_chat_id")
        return None

    url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        resp = requests.post(url, json=payload, timeout=SEND_TIMEOUT_S)
        data = resp.json() if resp.content else {}
        if resp.status_code == 200 and data.get("ok") is True:
            logger.info(
                "telegram_send_ok",
                chat_id=chat_id,
                message_id=data.get("result", {}).get("message_id"),
            )
            return data
        logger.error(
            "telegram_send_failed",
            chat_id=chat_id,
            http_status=resp.status_code,
            response=data,
        )
        return None
    except requests.RequestException as e:
        logger.error("telegram_send_exception", chat_id=chat_id, error=str(e))
        return None


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------


def _is_authorized(sender_chat_id: str | int, allowed_chat_id: str) -> bool:
    """True si sender == allowed (Thomas uniquement)."""
    return str(sender_chat_id) == str(allowed_chat_id)


# ---------------------------------------------------------------------------
# Handlers commandes (entrées : args str, conn sqlite, retour : str message)
# ---------------------------------------------------------------------------


class CommandError(ValueError):
    """Erreur applicative côté commande (validation / business rule)."""


def handle_trade(
    conn: sqlite3.Connection,
    args: list[str],
    today: date | None = None,
) -> str:
    """/trade <pl_brut_eur> <mae_eur> <mfe_eur>.

    Valide format, INSERT trades, message confirmation.
    Refuse si aucun signal du jour (BUY/SELL).
    """
    if len(args) != 3:
        raise CommandError(
            "Usage : /trade <pl_brut_eur> <mae_eur> <mfe_eur>\n"
            "Ex : /trade 42.50 -18.00 65.30"
        )

    try:
        pl_brut = float(args[0].replace(",", "."))
        mae = float(args[1].replace(",", "."))
        mfe = float(args[2].replace(",", "."))
    except ValueError as exc:
        raise CommandError(f"Valeurs numériques invalides : {exc}") from None

    today_iso = (today or date.today()).isoformat()
    signal = get_latest_signal_today(conn, today_iso)
    if signal is None:
        raise CommandError(
            f"Aucun signal BUY/SELL trouvé pour le {today_iso}. "
            "Le /trade doit être passé le jour du signal (cutoff 9h00 CET)."
        )

    # Cutoff 9h00 : si maintenant > 9h00 et signal date < today, refuser
    now_paris = datetime.now(PARIS_TZ)
    if now_paris.hour >= TRADE_CUTOFF_HOUR and signal["date"] != today_iso:
        raise CommandError(
            f"Signal périmé (signal du {signal['date']}, cutoff dépassé). "
            "Seul le signal du jour est éligible /trade."
        )

    trade_id = insert_trade(
        conn,
        signal_id=int(signal["id"]),
        pl_brut=pl_brut,
        mae=mae,
        mfe=mfe,
    )
    pl_net = pl_brut - 0.99 - 0.99

    # Phase 2f (A2 audit @testeur-persona-thomas) : afficher mode PAPER/LIVE
    # dans la confirmation pour eviter le shoot a cote (verbatim Thomas RER 8h48 :
    # "je peux taper /trade apres /stop sans m'en rendre compte"). Cf §2.2 et §6.3
    # docs/qa/persona-final-review-phase2.md.
    current_mode = get_strategy_mode(conn)
    mode_tag = "[PAPER 📝]" if current_mode == "paper" else "[LIVE 💰]"
    pfu_note = "(simulé)" if current_mode == "paper" else "(PFU 31,4 % a appliquer)"

    return (
        f"✅ Trade #{trade_id} enregistré {mode_tag} (signal #{signal['id']} {signal['asset']}).\n"
        f"P&amp;L brut : {pl_brut:+.2f} € | P&amp;L net (frais BD A/R) : {pl_net:+.2f} € {pfu_note}\n"
        f"MAE : {mae:+.2f} € | MFE : {mfe:+.2f} €"
    )


def handle_pause(conn: sqlite3.Connection, args: list[str]) -> str:
    """/pause YYYY-MM-DD YYYY-MM-DD — suspend signaux période (max 30j)."""
    if len(args) != 2:
        raise CommandError(
            "Usage : /pause YYYY-MM-DD YYYY-MM-DD\n"
            "Ex : /pause 2026-07-15 2026-07-29"
        )

    try:
        start = date.fromisoformat(args[0])
        end = date.fromisoformat(args[1])
    except ValueError as exc:
        raise CommandError(f"Format date invalide (attendu YYYY-MM-DD) : {exc}") from None

    try:
        pause_id = insert_strategy_pause(conn, start, end)
    except ValueError as exc:
        raise CommandError(str(exc)) from None

    delta = (end - start).days + 1
    return (
        f"⏸️ Pause #{pause_id} enregistrée : du {start.isoformat()} au {end.isoformat()} "
        f"({delta}j). Aucun signal envoyé pendant cette période."
    )


def handle_cancel_pause(conn: sqlite3.Connection) -> str:
    """/cancel-pause — annule la pause active (US-12 edge case)."""
    n = cancel_active_pause(conn)
    if n == 0:
        return "ℹ️ Aucune pause active à annuler."
    return f"✅ Pause active annulée (n={n}). Signaux repris immédiatement."


def handle_continue(conn: sqlite3.Connection, current_month: str | None = None) -> str:
    """/continue — valide mois suivant, passe mode live (US-10).

    Si nb_criteres_ko >= 2 (depuis dernière strategy_decision) : demande confirmation
    explicite (message d'avertissement, pas de transition immédiate).
    Sinon : insert decision 'continue' + set_strategy_mode('live').

    Idempotent : 2x /continue le même mois → 1 seule décision.
    """
    month = current_month or datetime.now(PARIS_TZ).strftime("%Y-%m")
    nb_ko = get_last_journal_week_criteria_ko(conn)

    if nb_ko >= 2:
        return (
            f"⚠️ Attention : {nb_ko} critères KO détectés ce mois.\n"
            "Reformuler /continue dans les 24h pour confirmer la continuation en mode live, "
            "ou /stop pour rester en paper trading."
        )

    decision_id = insert_strategy_decision(
        conn, month=month, decision="continue", nb_criteres_ko=nb_ko
    )
    set_strategy_mode(conn, "live")
    return (
        f"✅ Continuation mois {month} validée (decision #{decision_id}). "
        "Mode : **live**. Les signaux sont à exécuter réellement."
    )


def handle_stop(conn: sqlite3.Connection, current_month: str | None = None) -> str:
    """/stop — suspend stratégie, passe mode paper (US-11).

    Le bot continue d'envoyer les signaux mais préfixés [PAPER TRADING].
    Idempotent même mois.
    """
    month = current_month or datetime.now(PARIS_TZ).strftime("%Y-%m")
    decision_id = insert_strategy_decision(
        conn, month=month, decision="stop", nb_criteres_ko=0
    )
    set_strategy_mode(conn, "paper")
    return (
        f"🛑 Stratégie passée en paper trading (decision #{decision_id}, mois {month}).\n"
        "Les signaux continuent d'arriver mais préfixés [PAPER TRADING] — "
        "ne pas les exécuter en réel. Reformuler /continue pour repasser en live."
    )


def handle_journal_week(
    conn: sqlite3.Connection,
    stats: dict[str, Any],
    week_start: date,
    week_end: date,
    paper_mode: bool = False,
) -> str:
    """/journal-week — compute stats + format_weekly_summary + INSERT idempotent (US-09)."""
    insert_journal_week(conn, week_start=week_start, week_end=week_end)
    return format_weekly_summary(stats, paper_mode=paper_mode)


# ---------------------------------------------------------------------------
# Dispatcher (utilisé par un éventuel poller / webhook Telegram)
# ---------------------------------------------------------------------------


def dispatch_command(
    conn: sqlite3.Connection,
    sender_chat_id: str | int,
    allowed_chat_id: str,
    command: str,
    args: list[str],
    journal_week_stats: dict[str, Any] | None = None,
    journal_week_dates: tuple[date, date] | None = None,
    paper_mode: bool = False,
) -> str | None:
    """Dispatch une commande Telegram vers son handler.

    Returns:
        - str : message à renvoyer à l'utilisateur
        - None : commande refusée (auth) ou inconnue (silencieux)
    """
    if not _is_authorized(sender_chat_id, allowed_chat_id):
        logger.warning(
            "telegram_command_unauthorized",
            sender=str(sender_chat_id),
            command=command,
        )
        return None  # silencieux, pas de feedback à un attaquant

    try:
        if command == "/trade":
            return handle_trade(conn, args)
        if command == "/pause":
            return handle_pause(conn, args)
        if command == "/cancel-pause":
            return handle_cancel_pause(conn)
        if command == "/continue":
            return handle_continue(conn)
        if command == "/stop":
            return handle_stop(conn)
        if command == "/journal-week":
            if journal_week_stats is None or journal_week_dates is None:
                return (
                    "ℹ️ /journal-week : pas de stats disponibles. "
                    "Le résumé est envoyé automatiquement vendredi 18h00 CET."
                )
            return handle_journal_week(
                conn,
                stats=journal_week_stats,
                week_start=journal_week_dates[0],
                week_end=journal_week_dates[1],
                paper_mode=paper_mode,
            )
    except CommandError as exc:
        return f"❌ {exc}"

    logger.info("telegram_command_unknown", command=command)
    return None


__all__ = [
    "CommandError",
    "dispatch_command",
    "handle_cancel_pause",
    "handle_continue",
    "handle_journal_week",
    "handle_pause",
    "handle_stop",
    "handle_trade",
    "send_message",
]
