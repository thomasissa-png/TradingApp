"""Logique cron — verification jour ouvre + fenetre 8h40-8h55 CET.

Le cron Replit se declenche a 8h40 CET (cf docs/infra/infra-audit.md). Cette
couche logique repete la verification cote code pour ne JAMAIS pousser un
signal en dehors de la fenetre (ex : retry manuel sur jour ferie).
"""

from __future__ import annotations

from datetime import datetime, time

import pytz

from src.scheduler.calendar_fr import is_working_day_fr

PARIS_TZ = pytz.timezone("Europe/Paris")

# Fenetre signal 8h40-8h55 CET (cf functional-specs.md US-06 cutoff 8h55).
SIGNAL_WINDOW_START = time(8, 40)
SIGNAL_WINDOW_END = time(8, 55)


def _now_paris() -> datetime:
    return datetime.now(PARIS_TZ)


def is_market_day_fr(d: datetime | None = None) -> bool:
    """True si jour ouvre FR (lundi-vendredi, hors feries)."""
    target = d if d is not None else _now_paris()
    return is_working_day_fr(target)


def is_in_signal_window(now: datetime | None = None) -> bool:
    """True si l'heure courante est dans [8h40, 8h55] CET (bornes incluses)."""
    target = now if now is not None else _now_paris()
    if target.tzinfo is None:
        target = PARIS_TZ.localize(target)
    else:
        target = target.astimezone(PARIS_TZ)
    t = target.time()
    return SIGNAL_WINDOW_START <= t <= SIGNAL_WINDOW_END
