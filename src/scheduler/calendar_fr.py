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


# Mapping noms jours feries FR (workalendar retourne les libelles en anglais).
# Phase 2f (A3 audit @testeur-persona-thomas) : message courtoisie skip jour ferie.
_HOLIDAY_FR_NAMES: dict[str, str] = {
    "New year": "1er janvier",
    "Easter Monday": "Lundi de Paques",
    "Labour Day": "1er mai (Fete du travail)",
    "Victory in Europe Day": "8 mai (Victoire 1945)",
    "Ascension Day": "Ascension",
    "Whit Monday": "Lundi de Pentecote",
    "Bastille Day": "14 juillet (Fete nationale)",
    "Assumption of Mary to Heaven": "15 aout (Assomption)",
    "All Saints Day": "Toussaint",
    "Armistice Day": "11 novembre (Armistice 1918)",
    "Christmas Day": "Noel",
}


def get_holiday_name_fr(d: date | datetime | None = None) -> str | None:
    """Nom du jour ferie FR si la date en est un, sinon None.

    Returns:
        Libelle francais court (ex "14 juillet (Fete nationale)") ou None.
        Weekend renvoie None (ce n'est pas un ferie au sens workalendar).
    """
    if d is None:
        d = date.today()
    if isinstance(d, datetime):
        d = d.date()
    for h_date, h_name in _calendar().holidays(d.year):
        if h_date == d:
            name_str = str(h_name)
            return _HOLIDAY_FR_NAMES.get(name_str, name_str)
    return None
