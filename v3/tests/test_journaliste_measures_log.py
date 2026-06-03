"""Tests journaliste — persistance des mesures unitaires (measures-log.jsonl).

Vérifie :
  - measure_to_record sérialise les bons champs (et omet ce qui n'existe pas
    sur Measure — zéro invention) ;
  - write_measures_log réécrit le fichier complet (1 ligne JSON par mesure) ;
  - run() branche la persistance dans le cycle (à côté de performance.md) sans
    altérer le calcul des mesures/KPI.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers (autonomes — mêmes conventions que test_journaliste.py)
# ---------------------------------------------------------------------------

@pytest.fixture
def fiches_dict():
    return {
        "petrole": {
            "actif": "Pétrole (Brent)",
            "ticker_principal": "BZ=F",
            "seuils_reussite_pct": {"24h": 1.0, "7j": 2.5, "1m": 6.0},
        },
        "or": {
            "actif": "Or",
            "ticker_principal": "XAU/USD",
            "seuils_reussite_pct": {"24h": 0.8, "7j": 2.0, "1m": 5.0},
        },
    }


def _make_measure(outcome: str, conc: str = "LONG", score: float = 1.0,
                  echeance: date = date(2026, 6, 2)) -> jr.Measure:
    cell = jr.BulletinCell(
        bulletin_date=echeance - timedelta(days=1),
        actif_name="Pétrole (Brent)",
        horizon="24h",
        conclusion=conc,
        score=score,
    )
    return jr.Measure(
        cell=cell,
        fiche_key="petrole",
        ticker="BZ=F",
        horizon="24h",
        echeance=echeance,
        prix_emission=100.0,
        prix_courant=101.0,
        seuil_pct=1.0,
        delta_pct=1.0,
        outcome=outcome,
    )


def _write_bulletin(dir_: Path, d: date, rows: List[tuple]) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Bulletin Analyste — {d.isoformat()}",
        "",
        "## Matrice (12 actifs × 3 horizons)",
        "",
        "| Actif | 24h | 7j | 1m |",
        "|---|---|---|---|",
    ]
    for actif, (c24, s24), (c7, s7), (c1, s1) in rows:
        lines.append(
            f"| {actif} | {c24} ({s24:+.2f}) | {c7} ({s7:+.2f}) | {c1} ({s1:+.2f}) |"
        )
    path = dir_ / f"bulletin-{d.isoformat()}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_prix_emission(dir_: Path, d: date, prix: Dict[str, float]) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    path = dir_ / f"{d.isoformat()}.json"
    path.write_text(json.dumps(prix), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# measure_to_record
# ---------------------------------------------------------------------------

def test_measure_to_record_champs():
    m = _make_measure(jr.OUTCOME_VRAI, conc="LONG", score=2.5, echeance=date(2026, 6, 2))
    rec = jr.measure_to_record(m)
    assert rec["bulletin_date"] == "2026-06-01"
    assert rec["actif"] == "Pétrole (Brent)"
    assert rec["fiche_key"] == "petrole"
    assert rec["horizon"] == "24h"
    assert rec["conclusion"] == "LONG"
    assert rec["score"] == 2.5
    assert rec["outcome"] == jr.OUTCOME_VRAI
    assert rec["realized_pct"] == 1.0  # = delta_pct
    assert rec["echeance"] == "2026-06-02"
    # bulletin_id résolu via __post_init__ (rétro-compat = isoformat de la date).
    assert rec["bulletin_id"] == "2026-06-01"
    # is_flip présent (None par défaut), pas inventé.
    assert "is_flip" in rec and rec["is_flip"] is None


def test_measure_to_record_realized_pct_none():
    m = _make_measure(jr.OUTCOME_INTERROMPU)
    m.delta_pct = None
    rec = jr.measure_to_record(m)
    assert rec["realized_pct"] is None  # None préservé (zéro invention)


# ---------------------------------------------------------------------------
# write_measures_log
# ---------------------------------------------------------------------------

def test_write_measures_log_une_ligne_par_mesure(tmp_path):
    ms = [
        _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 6, 2)),
        _make_measure(jr.OUTCOME_FAUSSE, conc="SHORT", echeance=date(2026, 6, 3)),
    ]
    log = tmp_path / "measures-log.jsonl"
    out = jr.write_measures_log(ms, log)
    assert out == log
    lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    rec0 = json.loads(lines[0])
    assert rec0["outcome"] == jr.OUTCOME_VRAI
    assert json.loads(lines[1])["conclusion"] == "SHORT"


def test_write_measures_log_reecriture_complete(tmp_path):
    log = tmp_path / "measures-log.jsonl"
    # 1er run : 2 mesures
    jr.write_measures_log([_make_measure(jr.OUTCOME_VRAI)] * 2, log)
    # 2e run : la sortie de measure() est exhaustive → réécriture complète (1 ligne)
    jr.write_measures_log([_make_measure(jr.OUTCOME_FAUSSE)], log)
    lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["outcome"] == jr.OUTCOME_FAUSSE


def test_write_measures_log_vide(tmp_path):
    log = tmp_path / "measures-log.jsonl"
    jr.write_measures_log([], log)
    assert log.exists()
    assert log.read_text(encoding="utf-8").strip() == ""


# ---------------------------------------------------------------------------
# run() — la persistance est branchée dans le cycle
# ---------------------------------------------------------------------------

def test_run_ecrit_measures_log(tmp_path, fiches_dict):
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    perf = tmp_path / "performance.md"
    d_em = date(2026, 5, 28)
    today = date(2026, 5, 29)
    _write_bulletin(bulletins, d_em, [("Pétrole (Brent)", ("LONG", 0.5), ("SHORT", -0.5), ("LONG", 0.3))])
    _write_prix_emission(prix, d_em, {"BZ=F": 100.0})
    now = datetime(2026, 5, 29, 19, 0, tzinfo=timezone.utc)

    out, measures, kpis = jr.run(
        today=today,
        now=now,
        bulletins_dir=bulletins,
        prix_emission_dir=prix,
        performance_path=perf,
        fiches=fiches_dict,
        fetch_price=lambda t: 105.0,
        stamp_today=True,
    )
    # measures-log.jsonl écrit À CÔTÉ de performance.md (même dossier).
    log = perf.parent / "measures-log.jsonl"
    assert log.exists()
    lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    # autant de lignes que de mesures retournées par measure() (zéro double appel).
    assert len(lines) == len(measures)
    # chaque ligne a les champs attendus.
    if lines:
        rec = json.loads(lines[0])
        for key in ("bulletin_date", "bulletin_id", "fiche_key", "actif",
                    "horizon", "conclusion", "score", "outcome",
                    "realized_pct", "is_flip", "echeance"):
            assert key in rec
        assert rec["actif"] == "Pétrole (Brent)"
