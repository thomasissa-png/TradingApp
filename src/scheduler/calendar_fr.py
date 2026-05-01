"""Calendrier France — wrapper workalendar.

Note 14 juillet : `workalendar.europe.France` inclut les 11 jours feries legaux
(1er janvier, lundi de Paques, 1er mai, 8 mai, Ascension, lundi de Pentecote,
14 juillet, 15 aout, 1er novembre, 11 novembre, 25 decembre).
"""

from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache

from workalendar.europe import France


@lru_cache(maxsize=1)
def _calendar() -> France:
    return France()


def is_working_day_fr(d: date | datetime | None = None) -> bool:
    """Lundi-vendredi ET pas un jour ferie FR."""
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    return bool(_calendar().is_working_day(d))
