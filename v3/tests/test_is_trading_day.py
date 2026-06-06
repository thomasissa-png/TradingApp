"""Tests `is_trading_day` — garde de run « jours de bourse ouverts uniquement ».

`is_trading_day(d)` est la SOURCE DE VÉRITÉ UNIQUE de la garde de cycle.yml :
un run automatique (schedule / dispatch VPS sans force) ne s'exécute que les
jours où la bourse est ouverte = PAS week-end ET PAS férié de marché.

Elle réutilise EXACTEMENT le calendrier existant `_is_market_holiday`
(MARKET_HOLIDAYS, NYSE ∪ Euronext) — ces tests vérifient justement que la
fonction colle au calendrier réel (aucune liste recopiée).
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


def test_mardi_normal_est_jour_de_bourse() -> None:
    # 2026-06-09 = mardi ordinaire, hors MARKET_HOLIDAYS → bourse ouverte.
    d = date(2026, 6, 9)
    assert d.weekday() == 1  # mardi
    assert jr.is_trading_day(d) is True


def test_samedi_n_est_pas_jour_de_bourse() -> None:
    # 2026-06-06 = samedi (le jour du bug du briefing) → fermé.
    d = date(2026, 6, 6)
    assert d.weekday() == 5  # samedi
    assert jr.is_trading_day(d) is False


def test_dimanche_n_est_pas_jour_de_bourse() -> None:
    d = date(2026, 6, 7)
    assert d.weekday() == 6  # dimanche
    assert jr.is_trading_day(d) is False


def test_ferie_de_marche_n_est_pas_jour_de_bourse() -> None:
    # Date RÉELLE tirée de la frozenset MARKET_HOLIDAYS, et tombant un jour de
    # semaine (le cas dangereux : un lundi/jeudi férié sur prix figés).
    # Thanksgiving 2026-11-26 (jeudi) ∈ MARKET_HOLIDAYS.
    ferie = date(2026, 11, 26)
    assert ferie in jr.MARKET_HOLIDAYS
    assert ferie.weekday() < 5  # jour de semaine → le filtre week-end ne le couvre pas
    assert jr.is_trading_day(ferie) is False


def test_tous_les_feries_en_semaine_sont_exclus() -> None:
    # Cohérence forte : chaque férié de MARKET_HOLIDAYS doit donner is_trading_day=False
    # (qu'il tombe en semaine ou un week-end — dans les deux cas, fermé).
    for ferie in jr.MARKET_HOLIDAYS:
        assert jr.is_trading_day(ferie) is False, f"{ferie} devrait être fermé"


def test_is_trading_day_coherent_avec_is_market_holiday() -> None:
    # Un jour ouvré (lun-ven) non férié ⇔ is_trading_day True. Pas de divergence
    # possible : is_trading_day == (jour ouvré) and not _is_market_holiday.
    d = date(2026, 6, 9)  # mardi ordinaire
    assert jr._is_market_holiday(d) is False
    assert jr.is_trading_day(d) is True


def test_is_trading_day_ne_connait_pas_le_force() -> None:
    # La fonction ne juge QUE le jour : aucun paramètre force/bypass. Le bypass
    # « forçage explicite » est géré dans la garde cycle.yml, pas ici.
    import inspect

    sig = inspect.signature(jr.is_trading_day)
    params = list(sig.parameters)
    assert params == ["d"], f"is_trading_day ne doit prendre que `d`, vu : {params}"
