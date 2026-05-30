"""Logger structure JSON minimaliste (pas de dependance externe).

Format : {"ts": ISO8601, "level": LEVEL, "logger": NAME, "msg": EVENT, ...kwargs}
Niveau via env LOG_LEVEL (defaut INFO).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import MutableMapping
from datetime import UTC, datetime
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Serialise chaque LogRecord en une ligne JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # extras passes via logger.info("evt", extra={"key": "value"}) OU kwargs
        if hasattr(record, "_extras") and isinstance(record._extras, dict):
            payload.update(record._extras)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


class _StructuredAdapter(logging.LoggerAdapter[logging.Logger]):
    """Adapter qui accepte des kwargs structures et les passe via 'extra._extras'."""

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        reserved = {"exc_info", "stack_info", "stacklevel"}
        extras = {k: v for k, v in kwargs.items() if k not in reserved}
        passthrough: dict[str, Any] = {k: kwargs[k] for k in reserved if k in kwargs}
        passthrough["extra"] = {"_extras": extras}
        return msg, passthrough


_configured = False


def _ensure_root_handler() -> None:
    global _configured
    if _configured:
        return
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    _configured = True


def get_logger(name: str) -> _StructuredAdapter:
    """Retourne un adapter qui accepte des kwargs structures.

    Usage :
        logger = get_logger(__name__)
        logger.info("event_name", asset="DAX", score=7.4)
    """
    _ensure_root_handler()
    return _StructuredAdapter(logging.getLogger(name), {})
