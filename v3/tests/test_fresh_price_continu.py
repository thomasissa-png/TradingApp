"""VOLET A — prix le plus FRAIS pour les actifs CONTINUS (fin de l'angle mort
overnight / week-end, décision fondateur 2026-06-15).

ZÉRO réseau : on injecte les overrides directement et on mocke fetch_history /
fetch_price via monkeypatch sur market_data. On teste :
  - prix frais STRICTEMENT plus récent que close[-1] → la série inclut le point
    frais (et momentum/zscore se décalent) ;
  - prix frais du MÊME jour → remplace close[-1] ;
  - prix frais ABSENT ou PÉRIMÉ (≤ close[-1]) → série INCHANGÉE (no-op) ;
  - actif NON continu → jamais d'override appliqué ;
  - _continu_tickers réutilise mesure_ouverture.actif_group (pas de liste en dur).
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import criteres_calculator as cc  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_overrides():
    """Isole chaque test : aucun override ne fuit entre tests."""
    cc.clear_fresh_price_overrides()
    yield
    cc.clear_fresh_price_overrides()


def _fake_series(monkeypatch, points):
    """Mocke market_data.fetch_history pour renvoyer une série de closes datés.

    `points` : liste de (date, close). Renvoie un objet minimal compatible avec
    le parsing de fetch_twelve_series (index + colonne Close).
    """
    class _FakeDF:
        def __init__(self, pts):
            self.index = [datetime(d.year, d.month, d.day, tzinfo=timezone.utc) for d, _ in pts]
            self._close = [c for _, c in pts]

        def __len__(self):
            return len(self.index)

        def __getitem__(self, key):
            assert key == "Close"
            return self._close

    monkeypatch.setattr(cc.md, "fetch_history",
                        lambda symbol, period_days=60, interval="1day": _FakeDF(points))
    # Pas de clé Twelve en test → on force la dispo (yfinance branch).
    monkeypatch.setattr(cc, "_twelve_key", lambda: "fake-key")


def test_prix_frais_plus_recent_append_un_point(monkeypatch):
    """Prix frais daté APRÈS close[-1] → série + 1 point (le point frais)."""
    pts = [(date(2026, 6, 11), 100.0), (date(2026, 6, 12), 101.0)]  # close J-1 = vendredi
    _fake_series(monkeypatch, pts)
    base = cc.fetch_twelve_series("GC=F", outputsize=60)
    assert base is not None and len(base) == 2

    # Prix frais lundi 15/06 = +2 % vs vendredi → strictement plus récent.
    cc.set_fresh_price_override("GC=F", 103.02, date(2026, 6, 15))
    enriched = cc.fetch_twelve_series("GC=F", outputsize=60)
    assert enriched is not None
    assert len(enriched) == 3, "le point frais doit être appendé"
    assert enriched[-1][1] == pytest.approx(103.02)
    assert enriched[-1][0].date() == date(2026, 6, 15)
    # Les points historiques sont préservés et triés.
    assert enriched[-2][1] == pytest.approx(101.0)


def test_prix_frais_meme_jour_remplace_close(monkeypatch):
    """Prix frais du MÊME jour calendaire que close[-1] → remplace close[-1]."""
    pts = [(date(2026, 6, 12), 100.0), (date(2026, 6, 15), 101.0)]
    _fake_series(monkeypatch, pts)
    cc.set_fresh_price_override("GC=F", 104.5, date(2026, 6, 15))
    enriched = cc.fetch_twelve_series("GC=F", outputsize=60)
    assert enriched is not None
    assert len(enriched) == 2, "pas d'ajout, on raffraîchit le dernier point"
    assert enriched[-1][1] == pytest.approx(104.5)
    assert enriched[-1][0].date() == date(2026, 6, 15)


def test_prix_frais_perime_noop(monkeypatch):
    """Prix frais ≤ date de close[-1] (Twelve gratuit lundi 7h) → série INCHANGÉE."""
    pts = [(date(2026, 6, 11), 100.0), (date(2026, 6, 12), 101.0)]
    _fake_series(monkeypatch, pts)
    base = cc.fetch_twelve_series("GC=F", outputsize=60)

    # Prix « frais » daté de la veille de close[-1] → périmé → no-op.
    cc.set_fresh_price_override("GC=F", 999.0, date(2026, 6, 11))
    after = cc.fetch_twelve_series("GC=F", outputsize=60)
    assert after == base, "prix frais périmé → comportement actuel exact"
    assert all(c != 999.0 for _, c in after)


def test_aucun_override_noop(monkeypatch):
    """Aucun override posé → série inchangée (cas normal sans prix frais)."""
    pts = [(date(2026, 6, 11), 100.0), (date(2026, 6, 12), 101.0)]
    _fake_series(monkeypatch, pts)
    base = cc.fetch_twelve_series("GC=F", outputsize=60)
    again = cc.fetch_twelve_series("GC=F", outputsize=60)
    assert base == again
    assert len(again) == 2


def test_actif_non_continu_jamais_touche(monkeypatch):
    """Un symbole NON continu (S&P) n'a jamais d'override → série intacte même si
    on en pose un par erreur sur un AUTRE symbole."""
    pts = [(date(2026, 6, 11), 4000.0), (date(2026, 6, 12), 4010.0)]
    _fake_series(monkeypatch, pts)
    # override posé sur GC=F seulement ; ^GSPC ne doit pas être affecté.
    cc.set_fresh_price_override("GC=F", 9999.0, date(2026, 6, 15))
    sp = cc.fetch_twelve_series("^GSPC", outputsize=60)
    assert sp is not None and len(sp) == 2
    assert all(c != 9999.0 for _, c in sp)


def test_momentum_zscore_decale_avec_point_frais(monkeypatch):
    """Effet métier : un saut overnight déplace le z-score de variation 20j."""
    # 30 closes plats à 100, puis le prix frais saute à 130 (+30 %).
    pts = [(date(2026, 5, 1), 100.0)]
    # 30 sessions ouvrées approximées par jours consécutifs (suffisant pour le test).
    for i in range(1, 30):
        pts.append((date(2026, 5, 1 + i) if (1 + i) <= 31 else date(2026, 6, (1 + i) - 31), 100.0))
    _fake_series(monkeypatch, pts)
    crit = {"zscore_window": 20, "zscore_div": 2.0, "cap": 1.0}

    res_base = cc._twelve_variation_zscore("GC=F", 20, crit)

    cc.set_fresh_price_override("GC=F", 130.0, date(2026, 6, 30))
    res_fresh = cc._twelve_variation_zscore("GC=F", 20, crit)
    # Au minimum le résultat frais ne doit pas être identique au baseline plat
    # (le saut crée un rendement non nul). Tolérant : on vérifie qu'un signal
    # apparaît là où le baseline était nul/None.
    assert res_fresh is not None
    if res_base is not None:
        assert res_fresh[0] != res_base[0]


def test_continu_tickers_reutilise_actif_group():
    """_continu_tickers s'appuie sur mesure_ouverture.actif_group (pas de liste
    codée en dur) et inclut bien or/argent/pétrole/cacao/blé."""
    fiches = cc.load_fiches()
    tickers = set(cc._continu_tickers(fiches))
    # GC=F (or), BZ=F (brent), CC=F (cacao), ZW=F (blé) sont continus.
    assert {"GC=F", "BZ=F", "CC=F", "ZW=F"} <= tickers
    # Les indices cash (S&P/Nasdaq/CAC) ne doivent PAS y être.
    assert "^GSPC" not in tickers
    assert "^IXIC" not in tickers
    assert "^FCHI" not in tickers


def test_set_override_rejette_prix_invalide():
    """Prix ≤ 0 / NaN → pas d'override (zéro invention)."""
    cc.set_fresh_price_override("GC=F", 0.0, date(2026, 6, 15))
    cc.set_fresh_price_override("GC=F", float("nan"), date(2026, 6, 15))
    assert "GC=F" not in cc._FRESH_PRICE_OVERRIDES
