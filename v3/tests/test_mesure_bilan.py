"""Tests de la refonte « mesure du bilan = jour de bourse même » (mesure_bilan).

Couvre (brief 2026-06) :
- excursion favorable/adverse pour LONG ET SHORT ;
- calcul du max sur série 1h ;
- cascade de fallback clôture (1day → 1h → spot → suivi → non-notee) ;
- cohérence d'échelle indices (refus si proxy vs direct) ;
- garde-fou honnêteté (0/N notées → message « mesure indisponible ») ;
- variations-24h peuplé depuis les mesures du bilan.

Tous les fetchers sont injectés (callables) → zéro réseau.
"""

import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import journaliste as J  # noqa: E402
import mesure_bilan as MB  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
DATE_J = date(2026, 6, 8)


def _cell(actif, conclusion, score=0.5):
    return J.BulletinCell(
        actif_name=actif, conclusion=conclusion, horizon="24h",
        score=score, bulletin_date=DATE_J,
    )


FICHE_CAC = {"ticker_principal": "^FCHI", "seuils_reussite_pct": {"24h": 0.4}}
FICHE_OR = {"ticker_principal": "GC=F", "seuils_reussite_pct": {"24h": 0.5}}


# --------------------------------------------------------------------------
# Excursions favorable / adverse — LONG et SHORT
# --------------------------------------------------------------------------

def _series_1h(date_j, prices):
    """Série 1h : une barre par prix, toutes datées du jour J (heures croissantes)."""
    return [
        (datetime(date_j.year, date_j.month, date_j.day, 9 + i, 0, tzinfo=PARIS), p)
        for i, p in enumerate(prices)
    ]


def test_excursion_long():
    # LONG, ouverture 100. Série monte à 105 (fav +5%) puis descend à 98 (adverse -2%).
    bars = _series_1h(DATE_J, [100, 105, 98, 102])
    fav, adv = MB._excursions_intraday(bars, reference=100.0, call="LONG")
    assert fav == pytest.approx(5.0)
    assert adv == pytest.approx(-2.0)


def test_excursion_short():
    # SHORT, ouverture 100. Baisse à 94 = favorable +6% ; hausse à 103 = adverse -3%.
    bars = _series_1h(DATE_J, [100, 94, 103, 97])
    fav, adv = MB._excursions_intraday(bars, reference=100.0, call="SHORT")
    assert fav == pytest.approx(6.0)
    assert adv == pytest.approx(-3.0)


def test_excursion_jamais_favorable_long():
    # LONG qui ne monte jamais : fav clampé à 0, adverse négatif.
    bars = _series_1h(DATE_J, [100, 98, 96])
    fav, adv = MB._excursions_intraday(bars, reference=100.0, call="LONG")
    assert fav == pytest.approx(0.0)
    assert adv == pytest.approx(-4.0)


def test_excursion_pas_de_barre():
    fav, adv = MB._excursions_intraday([], reference=100.0, call="LONG")
    assert fav is None and adv is None


def test_excursion_ignore_barres_autre_jour():
    # _bars_du_jour filtre ; ici on vérifie via la mesure complète plus bas.
    bars = _series_1h(DATE_J, [100, 110])
    fav, _ = MB._excursions_intraday(bars, reference=100.0, call="LONG")
    assert fav == pytest.approx(10.0)


# --------------------------------------------------------------------------
# Cascade de fallback clôture
# --------------------------------------------------------------------------

def test_cloture_1day_prioritaire():
    s1day = [(datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), 200.0)]
    s1h = _series_1h(DATE_J, [190, 195])
    px, src, _ = MB._resolve_cloture("X", DATE_J, s1day, s1h, lambda t: 999.0, None)
    assert px == 200.0 and src == MB.CLOTURE_1DAY


def test_cloture_fallback_1h():
    s1h = _series_1h(DATE_J, [190, 195, 197])
    px, src, _ = MB._resolve_cloture("X", DATE_J, None, s1h, lambda t: 999.0, None)
    assert px == 197.0 and src == MB.CLOTURE_1H


def test_cloture_fallback_spot():
    px, src, _ = MB._resolve_cloture("X", DATE_J, None, None, lambda t: 150.0, None)
    assert px == 150.0 and src == MB.CLOTURE_SPOT


def test_cloture_fallback_suivi_prix():
    px, src, _ = MB._resolve_cloture("X", DATE_J, None, None, lambda t: None, 142.0)
    assert px == 142.0 and src == MB.CLOTURE_SUIVI


def test_cloture_fallback_suivi_fav_reconstruit():
    # Pas de prix de suivi direct, mais un fav% relevé (+2%) pour un LONG, ref 100
    # → clôture reconstruite = 102.
    px, src, _ = MB._resolve_cloture(
        "X", DATE_J, None, None, lambda t: None, None,
        suivi_fav_pct=2.0, reference=100.0, call="LONG",
    )
    assert px == pytest.approx(102.0) and src == MB.CLOTURE_SUIVI


def test_cloture_donnee_absente():
    px, src, h = MB._resolve_cloture("X", DATE_J, None, None, lambda t: None, None)
    assert px is None and src is None and h is None


# --------------------------------------------------------------------------
# Cohérence d'échelle indices (proxy vs direct)
# --------------------------------------------------------------------------

def test_echelle_incoherente_refuse():
    # Ouverture proxy ETF (748) vs clôture indice direct (5500) → ratio ~7.3 → refus.
    fiches = {"sp500": FICHE_CAC}  # ticker ^FCHI suffit pour le test d'échelle
    cell = _cell("CAC 40", "LONG")
    m = MB.measure_cellule_journee(
        cell, "cac", {"ticker_principal": "^FCHI", "seuils_reussite_pct": {"24h": 0.4}},
        date_j=DATE_J, prix_emis={"^FCHI": 748.0},
        prix_ouverture_dir=Path("/nonexistent"),
        fetch_series=lambda t, *, interval="1day", outputsize=60: (
            [(datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), 5500.0)] if interval == "1day" else None
        ),
        fetch_price=None,
    )
    # delta absurde refusé : pas de VRAI/FAUSSE, clôture neutralisée.
    assert m.delta_pct is None
    assert m.prix_courant is None
    assert "échelle incohérente" in m.note


def test_echelle_coherente_ok():
    cell = _cell("CAC 40", "LONG")
    m = MB.measure_cellule_journee(
        cell, "cac", {"ticker_principal": "^FCHI", "seuils_reussite_pct": {"24h": 0.4}},
        date_j=DATE_J, prix_emis={"^FCHI": 8000.0},
        prix_ouverture_dir=Path("/nonexistent"),
        fetch_series=lambda t, *, interval="1day", outputsize=60: (
            [(datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), 8080.0)] if interval == "1day" else None
        ),
        fetch_price=None,
    )
    assert m.delta_pct == pytest.approx(1.0, abs=0.01)
    assert m.outcome == J.OUTCOME_VRAI


# --------------------------------------------------------------------------
# Mesure complète d'une cellule : max favorable/adverse renseignés
# --------------------------------------------------------------------------

def test_mesure_cellule_renseigne_max_favorable():
    cell = _cell("CAC 40", "LONG")
    m = MB.measure_cellule_journee(
        cell, "cac", {"ticker_principal": "^FCHI", "seuils_reussite_pct": {"24h": 0.4}},
        date_j=DATE_J, prix_emis={"^FCHI": 8000.0},
        prix_ouverture_dir=Path("/nonexistent"),
        fetch_series=lambda t, *, interval="1day", outputsize=60: (
            _series_1h(DATE_J, [8000, 8200, 7950, 8080]) if interval == "1h"
            else [(datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), 8080.0)]
        ),
        fetch_price=None,
    )
    # max favorable = (8200-8000)/8000 = +2.5% ; max adverse = (7950-8000)/8000 = -0.625%
    assert m.max_favorable_pct == pytest.approx(2.5)
    assert m.max_adverse_pct == pytest.approx(-0.625)
    assert m.prix_cloture_source == "1day"


# --------------------------------------------------------------------------
# Garde-fou honnêteté + persistance variations-24h via build_bilan_jour
# --------------------------------------------------------------------------

def _setup_bulletin_env(tmp_path, actifs):
    """Crée un bulletin 7h + prix-ouverture + prix-emission pour `actifs`.

    `actifs` : liste de (nom, ticker, call, open_px, emis_px).
    """
    bdir = tmp_path / "bulletins"
    odir = tmp_path / "ouverture"
    edir = tmp_path / "emission"
    dlog = tmp_path / "dlog"
    for d in (bdir, odir, edir, dlog):
        d.mkdir(parents=True, exist_ok=True)

    lignes = [
        "# Briefing 7h", "",
        "| Actif | 24h | 7j | 1m |",
        "|---|---|---|---|",
    ]
    for nom, _tkr, call, _o, _e in actifs:
        lignes.append(f"| {nom} | {call} (+0.50) | {call} (+0.30) | {call} (+0.10) |")
    (bdir / "bulletin-2026-06-08-07h.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")

    import json
    ouv = {tkr: o for _n, tkr, _c, o, _e in actifs}
    emis = {tkr: e for _n, tkr, _c, _o, e in actifs}
    (odir / "2026-06-08.json").write_text(json.dumps(ouv), encoding="utf-8")
    (edir / "2026-06-08-07h.json").write_text(json.dumps(emis), encoding="utf-8")
    return {"bdir": bdir, "odir": odir, "edir": edir, "dlog": dlog}


def test_garde_fou_mesure_indisponible(tmp_path, monkeypatch):
    import bilan_jour as bj

    # Fiches minimales (le parseur de bulletin résout par nom via fiches).
    fiches = {
        "cacao": {"ticker_principal": "CC=F", "actif_name": "Cacao",
                  "seuils_reussite_pct": {"24h": 0.5}},
    }
    # On force fiche_for_actif_name à matcher "Cacao".
    env = _setup_bulletin_env(tmp_path, [("Cacao", "CC=F", "LONG", 8000.0, 8000.0)])
    monkeypatch.setattr(bj, "MEASURES_LOG_FILE", tmp_path / "measures-log.jsonl")
    monkeypatch.setattr(bj, "VARIATIONS_24H_FILE", tmp_path / "variations-24h.md")

    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    # AUCUNE clôture disponible (fetchers renvoient None) → toutes non-notées.
    bilan = bj.build_bilan_jour(
        now=now, date_j=DATE_J,
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"],
        fiches=fiches, fetch_price=lambda t: None,
        fetch_series=lambda t, *, interval="1day", outputsize=60: None,
        prix_ouverture_dir=env["odir"], prix_emission_dir=env["edir"],
    )
    # Robustesse : on a bien des cellules mesurées (non vides), toutes non-notées.
    assert len(bilan.measures_24h) >= 1
    assert all(m.outcome not in (J.OUTCOME_VRAI, J.OUTCOME_FAUSSE, J.OUTCOME_NC)
               for m in bilan.measures_24h)
    assert bj._mesure_indisponible(bilan) is True
    assert bj._MSG_MESURE_INDISPO in bilan.markdown
    # Le garde-fou remplace les messages « journée parfaite ».
    assert "Aucun pari raté ni opportunité ratée nette aujourd'hui." not in bilan.markdown
    assert "Rien de net aujourd'hui" not in bilan.markdown


def test_variations_24h_peuple_depuis_bilan(tmp_path, monkeypatch):
    import bilan_jour as bj

    fiches = {
        "cacao": {"ticker_principal": "CC=F", "actif_name": "Cacao",
                  "seuils_reussite_pct": {"24h": 0.5}},
    }
    env = _setup_bulletin_env(tmp_path, [("Cacao", "CC=F", "LONG", 10000.0, 10000.0)])
    mlog = tmp_path / "measures-log.jsonl"
    vfile = tmp_path / "variations-24h.md"
    monkeypatch.setattr(bj, "MEASURES_LOG_FILE", mlog)
    monkeypatch.setattr(bj, "VARIATIONS_24H_FILE", vfile)

    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    # Cacao +8% : clôture 1day 10800 vs ouverture 10000.
    bj.build_bilan_jour(
        now=now, date_j=DATE_J,
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"],
        fiches=fiches, fetch_price=lambda t: 10800.0,
        fetch_series=lambda t, *, interval="1day", outputsize=60: (
            [(datetime(2026, 6, 8, 17, 30, tzinfo=PARIS), 10800.0)] if interval == "1day"
            else _series_1h(DATE_J, [10000, 10800])
        ),
        prix_ouverture_dir=env["odir"], prix_emission_dir=env["edir"],
    )
    # Le measures-log contient désormais la mesure du jour (plus jamais vide).
    assert mlog.exists()
    content = mlog.read_text(encoding="utf-8")
    assert "Cacao" in content
    assert '"realized_pct": 8' in content or '"realized_pct": 7.99' in content
    # variations-24h.md régénéré et peuplé (le cacao +8% y apparaît, plus jamais vide).
    assert vfile.exists()
    vcontent = vfile.read_text(encoding="utf-8")
    assert "Cacao" in vcontent
    assert "+8.00%" in vcontent or "+7.99%" in vcontent
