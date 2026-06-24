"""Tests CA-M7 (compteur jours de bourse exclus) + CA-B2 (clôture CAC 17h30).

Dérivés des critères d'acceptation de `v3/docs/reco/spec-refonte-5-rapports.md`
§7 :
- CA-M7 : compteur `jours_bourse_exclus` (férié partiel : un marché ouvert,
  l'autre fermé → la garde globale `is_trading_day` saute le run) visible dans
  performance.md.
- CA-B2 : pour le CAC 40 (actif EU), la clôture de référence du 24h est le close
  officiel 17h30, pas le prix spot à 22h. Fallback robuste marqué `[close approx]`
  si le close officiel n'est pas récupérable (Q5 non validé en shadow).

WIN RATE ONLY — aucune valeur monétaire, aucune modification de poids/seuils.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import journaliste as jr  # noqa: E402
import bilan_jour as bj  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


# ===========================================================================
# CA-M7 — Compteur de jours de bourse exclus (férié partiel)
# ===========================================================================

def test_is_partial_holiday_memorial_day():
    # 2026-05-25 = Memorial Day (NYSE fermé) mais Euronext ouvert → partiel.
    d = date(2026, 5, 25)
    assert d.weekday() == 0  # lundi
    assert jr.is_trading_day(d) is False  # garde globale saute le run
    assert jr.is_partial_holiday(d) is True


def test_is_partial_holiday_premier_mai():
    # 2026-05-01 = Fête du Travail (Euronext fermé) mais NYSE ouvert → partiel.
    d = date(2026, 5, 1)
    assert d.weekday() == 4  # vendredi
    assert jr.is_trading_day(d) is False
    assert jr.is_partial_holiday(d) is True


def test_noel_n_est_pas_partiel():
    # 2026-12-25 = Noël : les DEUX marchés fermés → exclu mais PAS partiel.
    d = date(2026, 12, 25)
    assert jr.is_trading_day(d) is False
    assert jr.is_partial_holiday(d) is False


def test_jour_normal_n_est_pas_partiel():
    d = date(2026, 6, 9)  # mardi ordinaire, bourse ouverte
    assert jr.is_trading_day(d) is True
    assert jr.is_partial_holiday(d) is False


def test_weekend_n_est_pas_partiel():
    # Un week-end est exclu mais n'est jamais un « jour de bourse partiel ».
    assert jr.is_partial_holiday(date(2026, 6, 6)) is False  # samedi
    assert jr.is_partial_holiday(date(2026, 6, 7)) is False  # dimanche


def test_compter_jours_bourse_exclus_sur_fenetre():
    # Fenêtre couvrant le 1er Mai (Euronext fermé) ET le Memorial Day (NYSE
    # fermé) : 2 jours de bourse exclus par férié partiel.
    n = jr.compter_jours_bourse_exclus(date(2026, 5, 1), date(2026, 5, 31))
    assert n == 2


def test_compter_jours_bourse_exclus_fenetre_vide():
    # Une semaine ordinaire sans férié partiel → 0.
    n = jr.compter_jours_bourse_exclus(date(2026, 6, 8), date(2026, 6, 12))
    assert n == 0
    # Bornes inversées → 0 (zéro invention).
    assert jr.compter_jours_bourse_exclus(date(2026, 6, 12), date(2026, 6, 8)) == 0


def test_render_performance_affiche_compteur(monkeypatch):
    # Le rendu performance.md affiche le compteur CA-M7 sur la fenêtre observée.
    # On fabrique une mesure dont la date d'émission ouvre la fenêtre sur mai
    # (contient le 1er Mai + Memorial Day = 2 jours partiels).
    cell = jr.BulletinCell(
        actif_name="CAC 40", conclusion="LONG", horizon="24h",
        score=0.5, bulletin_date=date(2026, 5, 1),
    )
    m = jr.Measure(
        cell=cell, fiche_key="cac40", ticker="^FCHI", horizon="24h",
        echeance=date(2026, 5, 4), prix_emission=8000.0, prix_courant=8040.0,
        seuil_pct=0.4, delta_pct=0.5, outcome=jr.OUTCOME_VRAI,
    )
    now = datetime(2026, 6, 1, 8, 0, tzinfo=PARIS)
    md = jr.render_performance({}, [m], now, fiches={})
    assert "Jours de bourse exclus" in md
    # 1er Mai (EU fermé) + Memorial Day 25/05 (US fermé) = 2 dans [2026-05-01, 2026-06-01].
    assert "**2**" in md


# ===========================================================================
# CA-B2 — Clôture CAC officielle 17h30 (fallback marqué si indisponible)
# ===========================================================================

BULLETIN_7H = """# Bulletin 2026-06-08 07h

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| CAC 40 | LONG (+0.40) | LONG (+0.20) | LONG (+0.10) |
"""

DATE_J = date(2026, 6, 8)


def _fiche(actif, ticker, famille, seuil_24h):
    return {
        "actif": actif,
        "ticker_principal": ticker,
        "famille": famille,
        "seuils_reussite_pct": {"24h": seuil_24h, "7j": 1.3, "1m": 3.0},
    }


FICHES = {"cac40": _fiche("CAC 40", "^FCHI", "indices", 0.4)}


@pytest.fixture
def env(tmp_path):
    bdir = tmp_path / "bulletins"
    bdir.mkdir()
    (bdir / "bulletin-2026-06-08-07h.md").write_text(BULLETIN_7H, encoding="utf-8")
    odir = tmp_path / "prix-ouverture"
    odir.mkdir()
    # Ouverture CAC 09h00 = 8000.
    (odir / "2026-06-08.json").write_text(json.dumps({"^FCHI": 8000.0}), encoding="utf-8")
    edir = tmp_path / "prix-emission"
    edir.mkdir()
    dlog = tmp_path / "decision-log"
    dlog.mkdir()
    return {"bdir": bdir, "odir": odir, "edir": edir, "dlog": dlog}


def _ligne_close(bilan, actif):
    return next(m for m in bilan.measures_24h if m.cell.actif_name == actif)


def test_cac_utilise_close_1day_du_jour(env):
    # Refonte « jour de bourse même » (2026-06) : la cascade de clôture prend
    # d'abord la bougie 1day du jour J (close officiel) — pas le spot 22h.
    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    close_1day = 8080.0    # +1.0% vs ouverture 8000
    spot_22h = 9999.0      # spot 22h : NE DOIT PAS être utilisé si 1day dispo

    def fetch_price(t):
        return spot_22h

    def fetch_series(t, *, interval="1day", outputsize=60):
        if interval == "1day":
            return [
                (datetime(2026, 6, 5, 17, 30, tzinfo=PARIS), 7950.0),
                (datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), close_1day),
            ]
        return None  # pas de 1h dans ce test

    bilan = bj.build_bilan_jour(
        now=now, date_j=DATE_J,
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"],
        fiches=FICHES, fetch_price=fetch_price, fetch_series=fetch_series,
        prix_ouverture_dir=env["odir"], prix_emission_dir=env["edir"],
    )
    m = _ligne_close(bilan, "CAC 40")
    # Le close utilisé = bougie 1day du jour J (pas le spot 22h).
    assert m.prix_courant == pytest.approx(close_1day)
    assert m.prix_cloture_source == "1day"
    # delta = (8080 - 8000) / 8000 * 100 = +1.0%
    assert m.delta_pct == pytest.approx(1.0, abs=0.01)


def test_cac_fallback_spot_si_1day_et_1h_indispo(env):
    # Cascade : ni 1day ni 1h pour le jour J → fallback spot (source "spot").
    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    spot_22h = 8050.0  # +0.625% vs ouverture 8000

    def fetch_price(t):
        return spot_22h

    def fetch_series(t, *, interval="1day", outputsize=60):
        # Aucune barre datée du jour J (que des barres d'un autre jour).
        return [(datetime(2026, 6, 5, 17, 30, tzinfo=PARIS), 7950.0)]

    bilan = bj.build_bilan_jour(
        now=now, date_j=DATE_J,
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"],
        fiches=FICHES, fetch_price=fetch_price, fetch_series=fetch_series,
        prix_ouverture_dir=env["odir"], prix_emission_dir=env["edir"],
    )
    m = _ligne_close(bilan, "CAC 40")
    # Fallback spot (zéro invention d'un close fabriqué).
    assert m.prix_courant == pytest.approx(spot_22h)
    assert m.prix_cloture_source == "spot"


def test_bilan_aucune_mention_monetaire(env):
    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    bilan = bj.build_bilan_jour(
        now=now, date_j=DATE_J,
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"],
        fiches=FICHES, fetch_price=lambda t: 8080.0,
        fetch_series=lambda t, *, interval="1day", outputsize=60: [
            (datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), 8080.0)],
        prix_ouverture_dir=env["odir"], prix_emission_dir=env["edir"],
    )
    md = bilan.markdown.lower()
    # « gain » n'est PLUS interdit : depuis la décision fondateur 24/06, le win rate
    # se mesure sur le MAX GAIN du jour (% d'amplitude, jamais un montant). Seules
    # les mentions MONÉTAIRES restent proscrites (symboles, rendement, p&l).
    for token in ("€", "$", "rendement", "p&l"):
        assert token not in md, f"mention monétaire interdite : {token!r}"
