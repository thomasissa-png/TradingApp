"""Calendrier France — wrapper holidays.

Note : `holidays.France()` inclut les 11 jours feries legaux
(1er janvier, lundi de Paques, 1er mai, 8 mai, Ascension, lundi de Pentecote,
14 juillet, 15 aout, 1er novembre, 11 novembre, 25 decembre).

Phase 5c bis : migration workalendar -> holidays. workalendar tire pymeeus
en dependance transitive (via convertdate) qui ne build pas sur Replit.
holidays>=0.45 n'a pas cette dependance et couvre les memes jours feries FR
y compris les mobiles (Paques, Pentecote, Ascension).
"""

from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache

import holidays


@lru_cache(maxsize=1)
def _calendar() -> holidays.HolidayBase:
    return holidays.France()


def is_working_day_fr(d: date | datetime | None = None) -> bool:
    """Lundi-vendredi ET pas un jour ferie FR."""
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    # weekday() : 0=lundi, 4=vendredi, 5=samedi, 6=dimanche
    if d.weekday() >= 5:
        return False
    return d not in _calendar()


# Mapping noms jours feries FR (holidays.France() retourne les libelles en francais natifs).
# Phase 2f (A3 audit @testeur-persona-thomas) : message courtoisie skip jour ferie.
# On normalise vers des libelles courts standardises (sans accents pour compat Telegram).
_HOLIDAY_FR_NAMES: dict[str, str] = {
    "Jour de l'an": "1er janvier",
    "Lundi de Pâques": "Lundi de Paques",
    "Fête du Travail": "1er mai (Fete du travail)",
    "Fête de la Victoire": "8 mai (Victoire 1945)",
    "Ascension": "Ascension",
    "Lundi de Pentecôte": "Lundi de Pentecote",
    "Fête nationale": "14 juillet (Fete nationale)",
    "Assomption": "15 aout (Assomption)",
    "Toussaint": "Toussaint",
    "Armistice": "11 novembre (Armistice 1918)",
    "Noël": "Noel",
}


def get_holiday_name_fr(d: date | datetime | None = None) -> str | None:
    """Nom du jour ferie FR si la date en est un, sinon None.

    Returns:
        Libelle francais court (ex "14 juillet (Fete nationale)") ou None.
        Weekend renvoie None (ce n'est pas un ferie au sens calendrier legal).
    """
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    name = _calendar().get(d)
    if name is None:
        return None
    name_str = str(name)
    return _HOLIDAY_FR_NAMES.get(name_str, name_str)
