"""Tests calendrier ouvre France + fenetre signal."""

from __future__ import annotations

from datetime import date, datetime

import pytz

from src.scheduler.calendar_fr import is_working_day_fr
from src.scheduler.cron import is_in_signal_window, is_market_day_fr

PARIS = pytz.timezone("Europe/Paris")


def test_14_juillet_2026_is_not_working_day() -> None:
    """14 juillet = fete nationale FR -> pas un jour ouvre."""
    assert is_working_day_fr(date(2026, 7, 14)) is False


def test_4_mai_2026_is_working_day() -> None:
    """Lundi 4 mai 2026 — pas ferie, jour ouvre."""
    assert is_working_day_fr(date(2026, 5, 4)) is True


def test_saturday_is_not_working_day() -> None:
    """Samedi 2 mai 2026 -> non ouvre."""
    assert is_working_day_fr(date(2026, 5, 2)) is False


def test_christmas_2026_is_not_working_day() -> None:
    """25 decembre — ferie."""
    assert is_working_day_fr(date(2026, 12, 25)) is False


def test_is_market_day_fr_on_weekday() -> None:
    """Wrapper market_day = working_day FR pour la session signal."""
    assert is_market_day_fr(datetime(2026, 5, 4, 8, 45, tzinfo=PARIS)) is True
    assert is_market_day_fr(datetime(2026, 7, 14, 8, 45, tzinfo=PARIS)) is False


def test_signal_window_inside() -> None:
    """8h45 CET dans la fenetre [8h40, 8h55]."""
    t = PARIS.localize(datetime(2026, 5, 4, 8, 45))
    assert is_in_signal_window(t) is True


def test_signal_window_before() -> None:
    """8h35 CET hors fenetre."""
    t = PARIS.localize(datetime(2026, 5, 4, 8, 35))
    assert is_in_signal_window(t) is False


def test_signal_window_after() -> None:
    """9h00 CET hors fenetre (cutoff 8h55 strict — US-06)."""
    t = PARIS.localize(datetime(2026, 5, 4, 9, 0))
    assert is_in_signal_window(t) is False


def test_signal_window_boundaries() -> None:
    """Bornes incluses : 8h40 et 8h55 sont dans la fenetre."""
    t1 = PARIS.localize(datetime(2026, 5, 4, 8, 40))
    t2 = PARIS.localize(datetime(2026, 5, 4, 8, 55))
    assert is_in_signal_window(t1) is True
    assert is_in_signal_window(t2) is True
