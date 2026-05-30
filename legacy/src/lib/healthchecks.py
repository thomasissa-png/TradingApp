"""Wrapper healthchecks.io — ping G4 reliability."""

from __future__ import annotations

from typing import Literal

import requests

from src.lib.logger import get_logger

logger = get_logger(__name__)

PingStatus = Literal["success", "failure", "start"]


def ping_healthchecks(
    base_url: str,
    status: PingStatus = "success",
    timeout: float = 5.0,
) -> bool:
    """Envoie un ping a healthchecks.io.

    Args:
        base_url: URL fournie par healthchecks.io (ex: https://hc-ping.com/<uuid>)
        status: 'success' | 'failure' | 'start' (suffixe d'URL en API healthchecks)
        timeout: timeout HTTP en secondes (defaut 5s — ne pas bloquer le cron)

    Returns:
        True si HTTP 200, False sinon (jamais raise — un fail healthchecks NE DOIT PAS
        casser l'envoi du signal Telegram qui est l'output critique du cron).
    """
    if not base_url:
        logger.warning("healthchecks_skipped", reason="empty_url")
        return False

    suffix = "" if status == "success" else f"/{status}"
    url = base_url.rstrip("/") + suffix

    try:
        resp = requests.get(url, timeout=timeout)
        ok = resp.status_code == 200
        logger.info("healthchecks_ping", url=url, status=status, http_status=resp.status_code)
        return ok
    except requests.RequestException as e:
        logger.warning("healthchecks_failed", url=url, error=str(e))
        return False
