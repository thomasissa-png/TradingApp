"""Tests du branchement « Catalyseurs J+1 » du Bilan du jour sur le calendrier éco.

Vérifie que `bilan_jour._catalyseurs_j1` :
- consomme le calendrier statique (plus le message « non disponibles »),
- préfixe « ~ » les entrées `precision: regle`,
- étend la fenêtre à J+2 quand J+1 est un week-end,
- retombe sur un fallback propre si le YAML est absent.

WIN RATE ONLY — section purement informative, aucun impact scoring/mesure.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bilan_jour as bj  # noqa: E402
import calendrier_eco as ce  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


def _now(annee, mois, jour, h=22) -> datetime:
    return datetime(annee, mois, jour, h, 15, tzinfo=PARIS)


def _patch_yaml(monkeypatch, tmp_path, contenu: str) -> None:
    p = tmp_path / "calendrier-eco.yml"
    p.write_text(contenu, encoding="utf-8")
    monkeypatch.setattr(ce, "CALENDRIER_FILE", p, raising=False)


def test_catalyseurs_affiche_evenement_date(monkeypatch, tmp_path):
    _patch_yaml(monkeypatch, tmp_path, """
evenements:
  - nom: "Décision de taux Fed (FOMC)"
    type: FOMC
    precision: date
    dates: ["2026-06-11"]
    impact: high
    actifs: [or, sp500]
""")
    # Mercredi soir 2026-06-10 → J+1 = jeudi 11 (jour ouvré, horizon 1).
    lignes = bj._catalyseurs_j1(_now(2026, 6, 10))
    txt = "\n".join(lignes)
    assert "non disponibles" not in txt
    assert "2026-06-11" in txt
    assert "Fed" in txt
    assert "🔴" in txt  # impact high
    # precision: date → PAS de préfixe « ~ » sur la ligne d'événement.
    ligne_ev = next(l for l in lignes if "2026-06-11" in l)
    assert not ligne_ev.lstrip("- ").startswith("~")


def test_catalyseurs_prefixe_tilde_pour_regle(monkeypatch, tmp_path):
    _patch_yaml(monkeypatch, tmp_path, """
evenements:
  - nom: "Emploi US (NFP)"
    type: NFP
    precision: regle
    regle: premier_jour_semaine_mois
    regle_params: { weekday: 4 }
    impact: high
    actifs: [or]
""")
    # 2026-07-02 (jeudi) soir → J+1 = vendredi 3 = 1er vendredi → NFP.
    lignes = bj._catalyseurs_j1(_now(2026, 7, 2))
    ligne_ev = next(l for l in lignes if "2026-07-03" in l)
    assert "~ " in ligne_ev  # honnêteté : date approximative


def test_catalyseurs_etend_a_j2_le_weekend(monkeypatch, tmp_path):
    _patch_yaml(monkeypatch, tmp_path, """
evenements:
  - nom: "Positionnement (COT)"
    type: COT
    precision: date
    dates: ["2026-06-15"]
    impact: medium
    actifs: [or]
""")
    # Vendredi 2026-06-12 soir → J+1 = samedi (week-end) → horizon étendu à J+3,
    # capte un événement du lundi 2026-06-15.
    lignes = bj._catalyseurs_j1(_now(2026, 6, 12))
    assert any("2026-06-15" in l for l in lignes)


def test_catalyseurs_fallback_yaml_absent(monkeypatch, tmp_path):
    inexistant = tmp_path / "absent.yml"
    monkeypatch.setattr(ce, "CALENDRIER_FILE", inexistant, raising=False)
    lignes = bj._catalyseurs_j1(_now(2026, 6, 10))
    txt = "\n".join(lignes)
    assert "Aucun catalyseur" in txt
    # Pas d'ancien message technique trompeur.
    assert "non ingéré" not in txt
