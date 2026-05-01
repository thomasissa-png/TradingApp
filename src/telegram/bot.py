"""Wrapper minimal Telegram — envoi de messages texte.

Synchrone via API HTTP directe (pas de boucle asyncio pour le mini-jalon J+7).
Cohere avec docs/infra/infra-audit.md §5 (envoi simple).
"""

from __future__ import annotations

from typing import Any

import requests

from src.lib.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_API_BASE = "https://api.telegram.org"
SEND_TIMEOUT_S = 10.0


def send_message(
    bot_token: str,
    chat_id: str,
    text: str,
    parse_mode: str | None = None,
) -> dict[str, Any] | None:
    """Envoie un message Telegram via Bot API (sendMessage).

    Args:
        bot_token: token du bot (TELEGRAM_BOT_TOKEN).
        chat_id: chat_id Thomas (THOMAS_CHAT_ID).
        text: corps du message (UTF-8 natif — pas d'echappement unicode).
        parse_mode: 'Markdown' | 'MarkdownV2' | 'HTML' | None.

    Returns:
        dict (response.json() de Telegram) si HTTP 200 ET ok=true, None sinon.
        N'eleve PAS d'exception : la couche appelante decide quoi faire en cas d'echec.
    """
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
