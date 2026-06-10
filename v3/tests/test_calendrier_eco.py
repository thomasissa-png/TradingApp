"""Tests du calendrier économique statique (`calendrier_eco.py`).

Couvre :
- Règles de récurrence : NFP = 1er vendredi, EIA/COT = jour de semaine hebdo,
  CPI/BCE = n-ième jour ouvré, WASDE = jour du mois (recalé hors week-end).
- Tri (date, impact) + fenêtre J+1 / horizon.
- YAML absent → fallback liste vide (zéro exception).
- precision affichée (`date` vs `regle`).
- ZÉRO date inventée : toute entrée `precision: date` du YAML réel porte une date
  ISO valide.
- Gate déterministe `evenement_majeur_imminent` (FOMC J0/J-1).

WIN RATE ONLY — purement informatif, aucun impact scoring/mesure.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import calendrier_eco as ce  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
CONFIG_REEL = Path(__file__).resolve().parents[1] / "config" / "calendrier-eco.yml"


# ---------------------------------------------------------------------------
# Helpers de fixtures YAML temporaires
# ---------------------------------------------------------------------------

def _write_yaml(tmp_path: Path, contenu: str) -> Path:
    p = tmp_path / "calendrier-eco.yml"
    p.write_text(contenu, encoding="utf-8")
    return p


def _now(annee, mois, jour, h=10) -> datetime:
    return datetime(annee, mois, jour, h, 0, tzinfo=PARIS)


# ---------------------------------------------------------------------------
# Règles de récurrence pures
# ---------------------------------------------------------------------------

def test_nfp_premier_vendredi_du_mois():
    # 1er vendredi de juillet 2026 = 2026-07-03.
    assert ce._premier_jour_semaine_mois(2026, 7, 4).isoformat() == "2026-07-03"
    # 1er vendredi de février 2026 = 2026-02-06.
    assert ce._premier_jour_semaine_mois(2026, 2, 4).isoformat() == "2026-02-06"


def test_eia_mercredis_hebdo():
    from datetime import date
    # Mercredis entre le 2026-06-08 (lundi) et 2026-06-21 (dimanche).
    mercs = ce._occurrences_hebdo(2, date(2026, 6, 8), date(2026, 6, 21))
    assert [d.isoformat() for d in mercs] == ["2026-06-10", "2026-06-17"]


def test_cot_vendredi_unique_dans_fenetre_courte():
    from datetime import date
    # Du jeudi 2026-06-11 au samedi 2026-06-13 : un seul vendredi.
    vens = ce._occurrences_hebdo(4, date(2026, 6, 11), date(2026, 6, 13))
    assert [d.isoformat() for d in vens] == ["2026-06-12"]


def test_nieme_jour_ouvre_saute_weekend():
    # 10e jour ouvré de juin 2026 (1er = lundi 1er juin) → 2026-06-12 (vendredi).
    assert ce._nieme_jour_ouvre_mois(2026, 6, 10).isoformat() == "2026-06-12"


def test_jour_du_mois_recale_si_weekend():
    # Le 11 juillet 2026 est un samedi → recalé au lundi 13.
    assert ce._jour_du_mois(2026, 7, 11).isoformat() == "2026-07-13"
    # Le 11 juin 2026 est un jeudi → inchangé.
    assert ce._jour_du_mois(2026, 6, 11).isoformat() == "2026-06-11"


# ---------------------------------------------------------------------------
# evenements_a_venir — fenêtre, tri, precision
# ---------------------------------------------------------------------------

def test_fenetre_j1_exclut_aujourdhui_inclut_demain(tmp_path):
    yml = _write_yaml(tmp_path, """
evenements:
  - nom: "Fed aujourd'hui"
    type: FOMC
    precision: date
    dates: ["2026-06-10"]
    impact: high
    actifs: [or]
  - nom: "Fed demain"
    type: FOMC
    precision: date
    dates: ["2026-06-11"]
    impact: high
    actifs: [or]
""")
    evts = ce.evenements_a_venir(_now(2026, 6, 10), horizon_jours=1, path=yml)
    noms = [e["nom"] for e in evts]
    assert noms == ["Fed demain"]  # J0 exclu, J+1 inclus


def test_tri_par_date_puis_impact(tmp_path):
    yml = _write_yaml(tmp_path, """
evenements:
  - nom: "Medium J+2"
    type: EIA
    precision: date
    dates: ["2026-06-12"]
    impact: medium
    actifs: [petrole]
  - nom: "High J+1"
    type: FOMC
    precision: date
    dates: ["2026-06-11"]
    impact: high
    actifs: [or]
  - nom: "Medium J+1"
    type: COT
    precision: date
    dates: ["2026-06-11"]
    impact: medium
    actifs: [or]
""")
    evts = ce.evenements_a_venir(_now(2026, 6, 10), horizon_jours=3, path=yml)
    assert [e["nom"] for e in evts] == ["High J+1", "Medium J+1", "Medium J+2"]


def test_precision_regle_calculee_dans_fenetre(tmp_path):
    yml = _write_yaml(tmp_path, """
evenements:
  - nom: "Emploi US (NFP)"
    type: NFP
    precision: regle
    regle: premier_jour_semaine_mois
    regle_params: { weekday: 4 }
    impact: high
    actifs: [or, sp500]
""")
    # Au 2026-07-02 (jeudi), J+1 = 2026-07-03 = 1er vendredi → NFP attendu.
    evts = ce.evenements_a_venir(_now(2026, 7, 2), horizon_jours=1, path=yml)
    assert len(evts) == 1
    assert evts[0]["date"] == "2026-07-03"
    assert evts[0]["precision"] == "regle"


# ---------------------------------------------------------------------------
# Fallback : YAML absent / invalide
# ---------------------------------------------------------------------------

def test_yaml_absent_renvoie_vide(tmp_path):
    inexistant = tmp_path / "nope.yml"
    assert ce.evenements_a_venir(_now(2026, 6, 10), path=inexistant) == []
    assert ce.charger_evenements(inexistant) == []


def test_date_invalide_ignoree_pas_exception(tmp_path):
    yml = _write_yaml(tmp_path, """
evenements:
  - nom: "Date pourrie"
    type: FOMC
    precision: date
    dates: ["pas-une-date", "2026-06-11"]
    impact: high
    actifs: [or]
""")
    evts = ce.evenements_a_venir(_now(2026, 6, 10), horizon_jours=1, path=yml)
    assert [e["date"] for e in evts] == ["2026-06-11"]  # invalide ignorée


# ---------------------------------------------------------------------------
# Garde-fou ZÉRO date inventée sur le YAML RÉEL
# ---------------------------------------------------------------------------

def test_yaml_reel_chaque_date_est_iso_valide():
    from datetime import date as _date
    for ev in ce.charger_evenements(CONFIG_REEL):
        if (ev.get("precision") or "").lower() == "date":
            for s in ev.get("dates") or []:
                _date.fromisoformat(str(s))  # lève ValueError si inventée/mal formée


def test_yaml_reel_entrees_regle_ont_une_regle_connue():
    regles_connues = {
        "premier_jour_semaine_mois", "nieme_jour_ouvre_mois",
        "jour_du_mois", "jour_semaine_hebdo",
    }
    for ev in ce.charger_evenements(CONFIG_REEL):
        if (ev.get("precision") or "").lower() == "regle":
            assert ev.get("regle") in regles_connues


# ---------------------------------------------------------------------------
# Gate déterministe : evenement_majeur_imminent (FOMC J0/J-1)
# ---------------------------------------------------------------------------

def test_gate_fomc_imminent_j0_et_jmoins1(tmp_path):
    yml = _write_yaml(tmp_path, """
evenements:
  - nom: "Fed"
    type: FOMC
    precision: date
    dates: ["2026-06-17"]
    impact: high
    actifs: [or]
""")
    # J0 (le jour même) → imminent.
    assert ce.evenement_majeur_imminent(_now(2026, 6, 17), path=yml) is True
    # J-1 (la veille) → imminent.
    assert ce.evenement_majeur_imminent(_now(2026, 6, 16), path=yml) is True
    # J-2 → pas imminent (horizon défaut 1).
    assert ce.evenement_majeur_imminent(_now(2026, 6, 15), path=yml) is False


def test_gate_ignore_les_types_non_majeurs(tmp_path):
    yml = _write_yaml(tmp_path, """
evenements:
  - nom: "Stocks pétrole"
    type: EIA
    precision: date
    dates: ["2026-06-17"]
    impact: medium
    actifs: [petrole]
""")
    # EIA n'est pas un type majeur → gate False même le jour J.
    assert ce.evenement_majeur_imminent(_now(2026, 6, 17), path=yml) is False
