"""TradingApp entry point — Phase 2a mini-jalon J+7.

Modes :
  --mode=hello : pousse un message hello-world Telegram + ping healthchecks (jour ouvre FR uniquement)
  --mode=live  : Phase 2c (fallback hello-world tant que pipeline scoring pas implemente)
  --mode=paper : alias de --mode=live (STRATEGY_ACTIVE=paper definit le seuil)

Usage Replit (Cron Deployment) : commande `python -m src.main --mode=hello` declenchee
par cron Replit lundi-vendredi a 8h40 CET (cf docs/infra/infra-audit.md §2 + REPLIT_ACTIONS.md).
"""

from __future__ import annotations

import sys

from src.config import Config
from src.journal.db import init_database
from src.lib.healthchecks import ping_healthchecks
from src.lib.logger import get_logger
from src.scheduler.cron import is_market_day_fr
from src.telegram.bot import send_message
from src.telegram.templates import render_hello_world

logger = get_logger(__name__)

EXIT_OK = 0
EXIT_SKIPPED = 0  # pas un echec : jour ferie / week-end
EXIT_ERROR = 1


def run_hello_world(config: Config) -> int:
    """Mini-jalon J+7 : push hello-world Telegram + ping healthchecks.

    Sequence :
      1. Init DB SQLite (idempotent — cree journal.sqlite + 6 tables si absent)
      2. Verifie que c'est un jour ouvre FR (sinon EXIT_SKIPPED, pas une erreur)
      3. Envoie le message Telegram
      4. Ping healthchecks.io 'success' si Telegram OK, 'failure' sinon
    """
    # Init DB en premier — assure que la persistence est prete meme avant
    # le 1er signal reel (Phase 2c). Idempotent : pas d'erreur si deja cree.
    init_database(config.data_dir)

    if not is_market_day_fr():
        logger.info("market_closed", reason="not_a_market_day_fr")
        # Ping start mais pas success — healthchecks attend un ping quotidien,
        # un skip silencieux fait croire a une panne.
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


def main() -> int:
    """CLI entry point. Retourne un exit code Unix-style."""
    try:
        config = Config.from_env()
    except Exception as e:  # ValidationError ou autre — log explicite
        # Logger bas niveau (logging racine) — config peut avoir echoue avant init logger
        print(f'{{"level":"FATAL","msg":"config_load_failed","error":"{e}"}}', file=sys.stderr)
        return EXIT_ERROR

    mode = "--mode=hello"
    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode = arg
            break

    if mode == "--mode=hello":
        return run_hello_world(config)
    if mode in ("--mode=live", "--mode=paper"):
        # Phase 2c pas implementee — fallback hello-world pour ne pas casser le cron.
        logger.warning("live_mode_not_implemented_yet", phase="2c", fallback="hello")
        return run_hello_world(config)

    logger.error("unknown_mode", mode=mode)
    return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
