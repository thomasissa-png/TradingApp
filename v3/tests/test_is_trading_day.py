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


# ---------------------------------------------------------------------------
# PREUVE de l'automatisme multi-années : fériés 2027/2028 calculés par la lib
# `holidays` (XNYS + XECB), ABSENTS du set statique MARKET_HOLIDAYS (qui ne
# couvre que 2026). Si ces tests passent, la maintenance annuelle manuelle est
# bien terminée. Skip propre si la lib n'est pas installée localement.
# ---------------------------------------------------------------------------

import pytest  # noqa: E402

_HAS_HOLIDAYS = False
try:  # pragma: no cover - dépend de l'environnement
    import holidays as _holidays_probe  # noqa: F401

    _HAS_HOLIDAYS = True
except ImportError:  # pragma: no cover
    _HAS_HOLIDAYS = False

requires_lib = pytest.mark.skipif(
    not _HAS_HOLIDAYS, reason="lib `holidays` absente (testée en CI via requirements)"
)


@requires_lib
def test_feries_2027_calcules_par_la_lib_pas_dans_le_statique() -> None:
    # Aucune date 2027 dans le socle statique → la lib est la SEULE source.
    assert all(d.year != 2027 for d in jr.MARKET_HOLIDAYS), "le statique ne doit couvrir que 2026"
    # Noël 2027 : XNYS ferme le vendredi 24/12 (25 = samedi), XECB ferme 27/12.
    noel_xnys = date(2027, 12, 24)  # vendredi, NYSE fermé
    assert noel_xnys.weekday() < 5
    assert jr._is_market_holiday(noel_xnys) is True
    assert jr.is_trading_day(noel_xnys) is False
    # Thanksgiving 2027 = jeudi 25/11 (XNYS), absent du statique.
    thanksgiving = date(2027, 11, 25)
    assert thanksgiving.weekday() == 3  # jeudi
    assert jr.is_trading_day(thanksgiving) is False
    # Lundi de Pâques 2027 = 29/03 (Euronext XECB), absent du statique.
    paques = date(2027, 3, 29)
    assert paques.weekday() == 0  # lundi
    assert jr.is_trading_day(paques) is False


@requires_lib
def test_feries_2028_calcules_par_la_lib() -> None:
    assert all(d.year != 2028 for d in jr.MARKET_HOLIDAYS), "le statique ne doit couvrir que 2026"
    # Vendredi saint 2028 = 14/04 (commun XNYS + XECB).
    vendredi_saint = date(2028, 4, 14)
    assert vendredi_saint.weekday() == 4  # vendredi
    assert jr._is_market_holiday(vendredi_saint) is True
    assert jr.is_trading_day(vendredi_saint) is False
    # Thanksgiving 2028 = jeudi 23/11 (XNYS).
    thanksgiving = date(2028, 11, 23)
    assert thanksgiving.weekday() == 3
    assert jr.is_trading_day(thanksgiving) is False
    # 1er Mai 2028 = lundi (Euronext XECB).
    fete_travail = date(2028, 5, 1)
    assert fete_travail.weekday() == 0
    assert jr.is_trading_day(fete_travail) is False


@requires_lib
def test_un_mardi_ordinaire_2028_reste_jour_de_bourse() -> None:
    # Garde-fou anti-faux-positif : la lib ne doit PAS bloquer un jour ouvré
    # normal d'une année future (sinon la garde NO-OP à tort).
    d = date(2028, 6, 6)  # mardi ordinaire 2028
    assert d.weekday() == 1
    assert jr._is_market_holiday(d) is False
    assert jr.is_trading_day(d) is True


@requires_lib
def test_coherence_croisee_lib_vs_statique_2026() -> None:
    # Validation croisée : l'union (XNYS ∪ XECB) calculée par la lib pour 2026
    # doit donner EXACTEMENT le même verdict que le socle statique pour chaque
    # date 2026 du set. Garantit que le fallback statique 2026 est fidèle à la
    # lib (aucune divergence cachée le jour où la lib serait indisponible).
    import holidays as hol

    xnys = set(hol.financial_holidays("XNYS", years=2026).keys())
    xecb = set(hol.financial_holidays("XECB", years=2026).keys())
    union_lib_2026 = {d for d in (xnys | xecb)}
    static_2026 = {d for d in jr.MARKET_HOLIDAYS if d.year == 2026}
    assert union_lib_2026 == static_2026, (
        f"divergence lib/statique 2026 — "
        f"lib seule: {sorted(union_lib_2026 - static_2026)}, "
        f"statique seul: {sorted(static_2026 - union_lib_2026)}"
    )


def test_fallback_statique_si_lib_absente(monkeypatch: pytest.MonkeyPatch) -> None:
    # ROBUSTESSE CRITIQUE : si `import holidays` lève ImportError (lib non
    # installée / pip raté en CI), _is_market_holiday NE DOIT PAS planter et
    # doit retomber sur le socle statique MARKET_HOLIDAYS.
    import builtins

    _real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "holidays":
            raise ImportError("simulé : lib holidays indisponible")
        return _real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    # Un férié 2026 PRÉSENT dans le statique → toujours détecté (socle seul).
    ferie_2026 = date(2026, 12, 25)  # Christmas, ∈ MARKET_HOLIDAYS
    assert ferie_2026 in jr.MARKET_HOLIDAYS
    assert jr._is_market_holiday(ferie_2026) is True  # ne plante pas

    # Un jour ouvré ordinaire → False, sans crash (la garde ne bloque pas à tort).
    mardi = date(2026, 6, 9)
    assert jr._is_market_holiday(mardi) is False
    assert jr.is_trading_day(mardi) is True

    # Un férié 2027 ABSENT du statique → faute de lib, retombe à False sans
    # crash (le filet anti-mesure dégénérée prend le relais en aval). La PREUVE
    # ici = pas d'exception levée, pas que 2027 soit couvert sans lib.
    noel_2027 = date(2027, 12, 24)
    assert jr._is_market_holiday(noel_2027) is False  # pas de lib → fallback, no crash
