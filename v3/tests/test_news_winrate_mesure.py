"""Mesure de justesse des news (news-driven vs quant-pures), PAR HORIZON.

Couvre les 3 briques de la mesure-only :
  (1) FORWARD — `journaliste.measure_to_record` persiste news_driven + ratio_news ;
      `load_ratio_news_map` joint correctement le decision-log d'émission.
  (2) Calcul des 2 win-rates par horizon (run_weekly._news_vs_quant_winrate).
  (3) Garde-fou honnêteté N<15 → « en chauffe », jamais significatif.

Zéro impact signal : on ne teste QUE des champs additifs et des agrégats de
lecture. Aucune assertion ne dépend d'un score/direction.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402
import run_weekly as rw  # noqa: E402


# ---------------------------------------------------------------------------
# (1) FORWARD — persistance des champs news_driven / ratio_news
# ---------------------------------------------------------------------------
def _mk_cell(bdate: date, actif: str, horizon: str):
    return jr.BulletinCell(
        bulletin_date=bdate,
        bulletin_id=bdate.isoformat(),
        actif_name=actif,
        horizon=horizon,
        conclusion="LONG",
        score=1.0,
    )


def test_measure_to_record_persiste_news_driven_et_ratio_news():
    """Les 2 champs additifs DOIVENT apparaître dans le dict sérialisé."""
    cell = _mk_cell(date(2026, 6, 10), "Or", "24h")
    m = jr.Measure(
        cell=cell, fiche_key="or", ticker="GC=F", horizon="24h",
        echeance=date(2026, 6, 11), prix_emission=100.0, prix_courant=101.0,
        seuil_pct=0.5, delta_pct=1.0, outcome=jr.OUTCOME_VRAI,
    )
    m.news_driven = True
    m.ratio_news = 142.0
    rec = jr.measure_to_record(m)
    assert rec["news_driven"] is True
    assert rec["ratio_news"] == 142.0
    # round-trip JSON (pas de type non sérialisable)
    json.loads(json.dumps(rec, ensure_ascii=False))


def test_measure_to_record_news_champs_none_par_defaut():
    """Aucune jointure ⇒ champs présents mais None (zéro invention)."""
    cell = _mk_cell(date(2026, 6, 10), "Argent", "7j")
    m = jr.Measure(
        cell=cell, fiche_key="argent", ticker="SI=F", horizon="7j",
        echeance=date(2026, 6, 17), prix_emission=None, prix_courant=None,
        seuil_pct=None, delta_pct=None, outcome=jr.OUTCOME_INTERROMPU,
    )
    rec = jr.measure_to_record(m)
    assert rec["news_driven"] is None
    assert rec["ratio_news"] is None


def _write_decision_log(dl_dir: Path, fname: str, records: list) -> None:
    dl_dir.mkdir(parents=True, exist_ok=True)
    (dl_dir / fname).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def test_load_ratio_news_map_joint_le_ratio(tmp_path):
    dl = tmp_path / "decision-log"
    _write_decision_log(dl, "2026-06-10-0723.jsonl", [
        {"bulletin_date": "2026-06-10", "actif": "Or", "horizon": "24h", "ratio_news": 80.0},
        {"bulletin_date": "2026-06-10", "actif": "Argent", "horizon": "7j", "ratio_news": 12.5},
    ])
    mp = jr.load_ratio_news_map(date(2026, 6, 10), decision_log_dir=dl)
    assert mp[("Or", "24h")] == 80.0
    assert mp[("Argent", "7j")] == 12.5


def test_load_ratio_news_map_dernier_run_gagne(tmp_path):
    dl = tmp_path / "decision-log"
    _write_decision_log(dl, "2026-06-10-0723.jsonl", [
        {"bulletin_date": "2026-06-10", "actif": "Or", "horizon": "24h", "ratio_news": 10.0},
    ])
    _write_decision_log(dl, "2026-06-10-1800.jsonl", [
        {"bulletin_date": "2026-06-10", "actif": "Or", "horizon": "24h", "ratio_news": 90.0},
    ])
    mp = jr.load_ratio_news_map(date(2026, 6, 10), decision_log_dir=dl)
    assert mp[("Or", "24h")] == 90.0  # 18h > 07h


def test_load_ratio_news_map_absent_best_effort(tmp_path):
    """Champ absent / decision-log vide ⇒ map vide, jamais de crash."""
    dl = tmp_path / "decision-log"
    _write_decision_log(dl, "2026-06-10-0723.jsonl", [
        {"bulletin_date": "2026-06-10", "actif": "Or", "horizon": "24h"},  # pas de ratio_news
    ])
    mp = jr.load_ratio_news_map(date(2026, 6, 10), decision_log_dir=dl)
    assert mp == {}
    # dossier inexistant
    assert jr.load_ratio_news_map(date(2026, 6, 10), decision_log_dir=tmp_path / "nope") == {}


# ---------------------------------------------------------------------------
# (2) + (3) Win-rate par horizon news vs quant + garde-fou N<15
# ---------------------------------------------------------------------------
def _build_measures_log(path: Path, rows: list) -> None:
    """rows = liste de (actif, horizon, ratio_news_pct_or_None, outcome)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for actif, h, rn, outcome in rows:
        rec = {
            "bulletin_date": "2026-06-10", "bulletin_id": "2026-06-10",
            "fiche_key": actif.lower(), "actif": actif, "horizon": h,
            "conclusion": "LONG", "score": 1.0, "outcome": outcome,
            "realized_pct": 1.0, "is_flip": None, "echeance": "2026-06-11",
            "ratio_news": rn, "news_driven": (rn > 50.0 if rn is not None else None),
        }
        lines.append(json.dumps(rec, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_news_vs_quant_winrate_par_horizon(tmp_path, monkeypatch):
    """News (ratio>50) et quant (ratio<=50) comptés SÉPARÉMENT, par horizon."""
    rows = []
    # 24h news : 3 VRAI / 1 FAUX (ratio 80)
    rows += [("Or", "24h", 80.0, o) for o in ["VRAI", "VRAI", "VRAI", "FAUSSE"]]
    # 24h quant : 1 VRAI / 1 FAUX (ratio 10)
    rows += [("Cuivre", "24h", 10.0, o) for o in ["VRAI", "FAUSSE"]]
    # 7j quant : 2 VRAI (ratio 5)
    rows += [("Ble", "7j", 5.0, o) for o in ["VRAI", "VRAI"]]
    measures = tmp_path / "data" / "measures-log.jsonl"
    _build_measures_log(measures, rows)
    monkeypatch.setattr(rw, "ROOT", tmp_path)

    out = rw._news_vs_quant_winrate()
    assert out["24h"]["news"] == (3, 1)   # 3 VRAI, 1 FAUX
    assert out["24h"]["quant"] == (1, 1)
    assert out["7j"]["quant"] == (2, 0)
    assert out["7j"]["news"] == (0, 0)
    assert out["1m"]["news"] == (0, 0) and out["1m"]["quant"] == (0, 0)


def test_news_vs_quant_exclut_nc(tmp_path, monkeypatch):
    """NC / non-noté NE comptent PAS dans les buckets (VRAI+FAUX seulement)."""
    rows = [
        ("Or", "24h", 80.0, "VRAI"),
        ("Or", "24h", 80.0, "non-conclusif"),
        ("Or", "24h", 80.0, "non-notee"),
        ("Or", "24h", 80.0, "suivi-interrompu"),
    ]
    measures = tmp_path / "data" / "measures-log.jsonl"
    _build_measures_log(measures, rows)
    monkeypatch.setattr(rw, "ROOT", tmp_path)
    out = rw._news_vs_quant_winrate()
    assert out["24h"]["news"] == (1, 0)  # seul le VRAI compte


def test_news_vs_quant_inconnu_exclu(tmp_path, monkeypatch):
    """ratio_news None (pré-instrumentation, decision-log absent) ⇒ exclu."""
    rows = [("Or", "24h", None, "VRAI"), ("Or", "24h", 80.0, "VRAI")]
    measures = tmp_path / "data" / "measures-log.jsonl"
    _build_measures_log(measures, rows)
    monkeypatch.setattr(rw, "ROOT", tmp_path)
    # pas de decision-log ⇒ la ligne None reste inconnue
    monkeypatch.setattr(jr, "DECISION_LOG_DIR", tmp_path / "no-dl")
    out = rw._news_vs_quant_winrate()
    assert out["24h"]["news"] == (1, 0)  # seule la ligne ratio=80 comptée


def test_garde_fou_n_inferieur_15_marque_en_chauffe():
    """Sous N=15 ⇒ mention « en chauffe » ; jamais affiché comme significatif."""
    assert "en chauffe" in rw._fmt_news_cell((10, 4))  # N=14 < 15
    assert "en chauffe" not in rw._fmt_news_cell((10, 5))  # N=15 ⇒ significatif
    assert rw._fmt_news_cell((0, 0)) == "— (0 jugé)"


def test_garde_fou_seuil_exact_15_significatif():
    cell = rw._fmt_news_cell((9, 6))  # N=15
    assert "en chauffe" not in cell
    assert "[N=15]" in cell
