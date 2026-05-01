"""Templates Telegram (stubs Phase 2a — remplis Phase 2c par @copywriter).

Source de verite future : docs/copy/message-templates.md (14 templates ACHAT/VENTE,
4 NO-TRADE, 3 ERREUR/DEGRADED). Format strict 6L+1 (cf brand-platform.md).

Phase 2a : on n'a besoin que du template hello-world. Les autres sont des stubs
qui leveront NotImplementedError pour empecher tout usage avant @copywriter.
"""

from __future__ import annotations

from typing import Final

# ---- Mini-jalon J+7 : message hello-world ----

HELLO_WORLD_TEMPLATE: Final[str] = (
    "TradingApp cron OK — {ts}\n"
    "Mode: {mode}\n"
    "Mini-jalon J+7 actif. Le bot est en place, R&D edge a venir (30-90j)."
)


def render_hello_world(ts: str, mode: str) -> str:
    """Rendu du message du mini-jalon J+7."""
    return HELLO_WORLD_TEMPLATE.format(ts=ts, mode=mode)


# ---- Stubs Phase 2c ----


def render_buy_signal(*args: object, **kwargs: object) -> str:
    raise NotImplementedError(
        "Template ACHAT a remplir Phase 2c — cf docs/copy/message-templates.md"
    )


def render_sell_signal(*args: object, **kwargs: object) -> str:
    raise NotImplementedError(
        "Template VENTE a remplir Phase 2c — cf docs/copy/message-templates.md"
    )


def render_no_trade(*args: object, **kwargs: object) -> str:
    raise NotImplementedError(
        "Template NO-TRADE a remplir Phase 2c — cf docs/copy/message-templates.md"
    )


def render_error_data(*args: object, **kwargs: object) -> str:
    raise NotImplementedError(
        "Template ERREUR DATA a remplir Phase 2c — cf docs/copy/message-templates.md"
    )


def render_degraded_mode(*args: object, **kwargs: object) -> str:
    raise NotImplementedError(
        "Template DEGRADED a remplir Phase 2c — cf docs/copy/message-templates.md"
    )
