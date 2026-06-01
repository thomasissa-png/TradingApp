"""Tests Journaliste — stamp prix, mesure VRAI/FAUSSE/non-conclusive/suivi-interrompu,
KPI 30 dernières, Brier, distribution, target 70%. HTTP 100% mocké.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fiche_petrole():
    """Fiche minimale pour les tests (ticker + seuils)."""
    return {
        "actif": "Pétrole (Brent)",
        "ticker_principal": "BZ=F",
        "seuils_reussite_pct": {"24h": 1.0, "7j": 2.5, "1m": 6.0},
    }


@pytest.fixture
def fiche_or():
    return {
        "actif": "Or",
        "ticker_principal": "XAU/USD",
        "seuils_reussite_pct": {"24h": 0.8, "7j": 2.0, "1m": 5.0},
    }


@pytest.fixture
def fiches_dict(fiche_petrole, fiche_or):
    return {"petrole": fiche_petrole, "or": fiche_or}


def _write_bulletin(dir_: Path, d: date, rows: List[tuple]) -> Path:
    """Écrit un bulletin minimal compatible avec le parseur.

    rows = [(actif_name, (concl24, s24), (concl7, s7), (concl1, s1)), ...]
    """
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
# parse_bulletin
# ---------------------------------------------------------------------------

def test_parse_bulletin_extrait_3_horizons(tmp_path):
    d = date(2026, 5, 1)
    _write_bulletin(
        tmp_path,
        d,
        [("Pétrole (Brent)", ("LONG", 0.42), ("SHORT", -1.20), ("LONG", 3.0))],
    )
    cells = jr.parse_bulletin(tmp_path / f"bulletin-{d.isoformat()}.md")
    assert len(cells) == 3
    horizons = {c.horizon: c for c in cells}
    assert horizons["24h"].conclusion == "LONG"
    assert horizons["24h"].score == pytest.approx(0.42)
    assert horizons["7j"].conclusion == "SHORT"
    assert horizons["7j"].score == pytest.approx(-1.20)
    assert horizons["1m"].conclusion == "LONG"
    assert all(c.bulletin_date == d for c in cells)


def test_parse_bulletin_ignore_fichier_non_dated(tmp_path):
    (tmp_path / "autre.md").write_text("# autre\n", encoding="utf-8")
    assert jr.parse_bulletin(tmp_path / "autre.md") == []


# ---------------------------------------------------------------------------
# measure_cell — VRAI / FAUSSE / non-conclusive / suivi-interrompu
# ---------------------------------------------------------------------------

def _cell(conc: str, horizon: str, score: float = 0.5, bdate=date(2026, 5, 1), actif="Pétrole (Brent)"):
    return jr.BulletinCell(
        bulletin_date=bdate,
        actif_name=actif,
        horizon=horizon,
        conclusion=conc,
        score=score,
    )


def test_measure_cell_vrai_long(fiche_petrole):
    # seuil 24h = 1.0 % ; prix passe de 100 -> 102 (+2 %) ; LONG => VRAI
    c = _cell("LONG", "24h")
    m = jr.measure_cell(c, "petrole", fiche_petrole, prix_emission=100.0, prix_courant=102.0)
    assert m.outcome == jr.OUTCOME_VRAI
    assert m.delta_pct == pytest.approx(2.0)


def test_measure_cell_fausse_long(fiche_petrole):
    # LONG mais prix baisse de 2 % > seuil 1 % => FAUSSE
    c = _cell("LONG", "24h")
    m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 98.0)
    assert m.outcome == jr.OUTCOME_FAUSSE


def test_measure_cell_vrai_short(fiche_petrole):
    # SHORT et prix baisse de 3 % > seuil 2.5 % (7j) => VRAI
    c = _cell("SHORT", "7j")
    m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 97.0)
    assert m.outcome == jr.OUTCOME_VRAI


def test_measure_cell_fausse_short(fiche_petrole):
    # SHORT mais prix monte de 3 % > seuil 2.5 % => FAUSSE
    c = _cell("SHORT", "7j")
    m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 103.0)
    assert m.outcome == jr.OUTCOME_FAUSSE


def test_measure_cell_non_conclusive(fiche_petrole):
    # mouvement 0.5 % < seuil 1 % (24h) => non-conclusive, quel que soit le sens
    c_long = _cell("LONG", "24h")
    m = jr.measure_cell(c_long, "petrole", fiche_petrole, 100.0, 100.5)
    assert m.outcome == jr.OUTCOME_NC
    c_short = _cell("SHORT", "24h")
    m2 = jr.measure_cell(c_short, "petrole", fiche_petrole, 100.0, 99.5)
    assert m2.outcome == jr.OUTCOME_NC


def test_measure_cell_suivi_interrompu_prix_emission_absent(fiche_petrole):
    c = _cell("LONG", "24h")
    m = jr.measure_cell(c, "petrole", fiche_petrole, prix_emission=None, prix_courant=102.0)
    assert m.outcome == jr.OUTCOME_INTERROMPU
    assert "émission" in m.note.lower() or "emission" in m.note.lower()


def test_measure_cell_suivi_interrompu_prix_courant_absent(fiche_petrole):
    c = _cell("LONG", "24h")
    m = jr.measure_cell(c, "petrole", fiche_petrole, prix_emission=100.0, prix_courant=None)
    assert m.outcome == jr.OUTCOME_INTERROMPU


def test_measure_cell_seuil_pile_egal_compte_non_conclusive(fiche_petrole):
    # |delta| EXACTEMENT = seuil → non-conclusive (>, pas >=)
    c = _cell("LONG", "24h")
    m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 101.0)  # +1.0 % = seuil
    assert m.outcome == jr.OUTCOME_NC


# ---------------------------------------------------------------------------
# stamp_prix_emission
# ---------------------------------------------------------------------------

def test_stamp_prix_emission_ecrit_json(tmp_path, fiches_dict):
    base_dir = tmp_path / "prix-emission"
    prices = {"BZ=F": 82.5, "XAU/USD": 2400.0}
    out = jr.stamp_prix_emission(
        date(2026, 5, 29),
        fiches=fiches_dict,
        fetch_price=lambda ticker: prices.get(ticker),
        base_dir=base_dir,
    )
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == {"BZ=F": 82.5, "XAU/USD": 2400.0}


def test_stamp_prix_emission_idempotent_preserve_anciens(tmp_path, fiches_dict):
    base_dir = tmp_path / "prix-emission"
    d = date(2026, 5, 29)
    # 1er run : prix OK
    jr.stamp_prix_emission(d, fiches=fiches_dict, fetch_price=lambda t: 100.0, base_dir=base_dir)
    # 2e run : fetch retourne None → l'ancien doit être préservé
    jr.stamp_prix_emission(d, fiches=fiches_dict, fetch_price=lambda t: None, base_dir=base_dir)
    data = json.loads((base_dir / f"{d.isoformat()}.json").read_text(encoding="utf-8"))
    assert data == {"BZ=F": 100.0, "XAU/USD": 100.0}


def test_stamp_prix_emission_skip_si_fetch_none(tmp_path, fiches_dict):
    """Si Twelve Data injoignable, le ticker n'est PAS stampé (zéro invention)."""
    base_dir = tmp_path / "prix-emission"
    jr.stamp_prix_emission(
        date(2026, 5, 29),
        fiches=fiches_dict,
        fetch_price=lambda t: None,
        base_dir=base_dir,
    )
    data = json.loads((base_dir / "2026-05-29.json").read_text(encoding="utf-8"))
    assert data == {}


# ---------------------------------------------------------------------------
# proba_from_score
# ---------------------------------------------------------------------------

def test_proba_from_score_borne():
    assert jr.proba_from_score(0.0, "LONG") == pytest.approx(0.5)
    assert jr.proba_from_score(5.0, "LONG", scale=10.0) == pytest.approx(1.0)  # 0.5 + 0.5
    assert jr.proba_from_score(-5.0, "SHORT", scale=10.0) == pytest.approx(1.0)
    assert jr.proba_from_score(100.0, "LONG", scale=10.0) == pytest.approx(1.0)  # clip
    assert jr.proba_from_score(2.0, "LONG", scale=10.0) == pytest.approx(0.7)  # 0.5 + 0.2


def test_proba_scale_default_is_15():
    """Audit 2026-06-01 : PROBA_SCALE 10→15 pour réduire saturation Brier
    sur les scores ±5-14 observés en prod (Pétrole +9.99, Blé -5.68)."""
    assert jr.PROBA_SCALE == 15.0
    # Avec scale=15, |score|=5 → proba=0.5+5/15=0.833 (pas saturée à 1.0 comme avant)
    assert jr.proba_from_score(5.0, "LONG") == pytest.approx(0.5 + 5.0 / 15.0)
    # |score|=7.5 sature désormais (0.5 + 0.5 = 1.0)
    assert jr.proba_from_score(7.5, "LONG") == pytest.approx(1.0)
    # |score|=10 → toujours saturé
    assert jr.proba_from_score(10.0, "LONG") == pytest.approx(1.0)
    # |score|=3 → 0.5 + 0.2 = 0.7 (au lieu de 0.8 avec scale=10)
    assert jr.proba_from_score(3.0, "LONG") == pytest.approx(0.7)


# ---------------------------------------------------------------------------
# compute_kpi : taux 30 dernières, Brier, distribution, statut éligible vs shadow
# ---------------------------------------------------------------------------

def _make_measure(outcome: str, conc: str = "LONG", score: float = 1.0,
                  echeance: date = date(2026, 5, 2)) -> jr.Measure:
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


def test_compute_kpi_eligible_actif_70_pct():
    # 30 mesures terminées : 21 VRAI, 9 FAUSSE → 70 % ⇒ éligible
    ms = []
    for i in range(21):
        ms.append(_make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1) + timedelta(days=i)))
    for i in range(9):
        ms.append(_make_measure(jr.OUTCOME_FAUSSE, echeance=date(2026, 2, 1) + timedelta(days=i)))
    ms.sort(key=lambda m: m.echeance)
    k = jr.compute_kpi(ms)
    assert k.n_total == 30
    assert k.taux_pct == pytest.approx(70.0)
    assert k.statut == "éligible_actif"


def test_compute_kpi_shadow_sous_70_pct():
    ms = []
    for i in range(20):
        ms.append(_make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1) + timedelta(days=i)))
    for i in range(10):
        ms.append(_make_measure(jr.OUTCOME_FAUSSE, echeance=date(2026, 2, 1) + timedelta(days=i)))
    k = jr.compute_kpi(ms)
    assert k.taux_pct == pytest.approx(20 / 30 * 100, abs=0.01)
    assert k.statut == "shadow"


def test_compute_kpi_shadow_warmup_si_moins_de_30():
    ms = [_make_measure(jr.OUTCOME_VRAI) for _ in range(5)]
    for i, m in enumerate(ms):
        m.echeance = date(2026, 1, 1) + timedelta(days=i)
    k = jr.compute_kpi(ms)
    assert k.statut == "shadow"
    assert any("warm-up" in a for a in k.alertes)


def test_compute_kpi_non_conclusive_exclues_du_taux():
    """Non-conclusive : N total inclut, mais pas le taux ni le Brier."""
    ms = []
    for i in range(15):
        ms.append(_make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1) + timedelta(days=i)))
    for i in range(15):
        ms.append(_make_measure(jr.OUTCOME_NC, echeance=date(2026, 2, 1) + timedelta(days=i)))
    k = jr.compute_kpi(ms)
    assert k.n_total == 30
    assert k.n_vrai == 15
    assert k.n_nc == 15
    # taux = 15 / (15+0) = 100 %
    assert k.taux_pct == pytest.approx(100.0)
    # Brier ne porte que sur les 15 VRAI
    assert k.brier_n == 15


def test_compute_kpi_brier_parfait_si_proba_extrême_et_vrai():
    """proba=1, outcome=1 ⇒ contribution Brier = 0."""
    ms = [_make_measure(jr.OUTCOME_VRAI, score=100.0) for _ in range(10)]
    for i, m in enumerate(ms):
        m.echeance = date(2026, 1, 1) + timedelta(days=i)
    k = jr.compute_kpi(ms)
    assert k.brier == pytest.approx(0.0)


def test_compute_kpi_brier_pire_si_proba_extrême_et_faux():
    """proba=1, outcome=0 ⇒ contribution Brier = 1.0."""
    ms = [_make_measure(jr.OUTCOME_FAUSSE, score=100.0) for _ in range(10)]
    for i, m in enumerate(ms):
        m.echeance = date(2026, 1, 1) + timedelta(days=i)
    k = jr.compute_kpi(ms)
    assert k.brier == pytest.approx(1.0)


def test_compute_kpi_distribution_long_short_alerte():
    """Distribution 100% LONG ⇒ alerte biais."""
    ms = [_make_measure(jr.OUTCOME_VRAI, conc="LONG") for _ in range(30)]
    for i, m in enumerate(ms):
        m.echeance = date(2026, 1, 1) + timedelta(days=i)
    k = jr.compute_kpi(ms)
    assert k.distrib_long_pct == pytest.approx(100.0)
    assert any("biais" in a for a in k.alertes)


def test_compute_kpi_alerte_chevauchement_7j_1m():
    """Audit 2026-06-01 : pour 7j et 1m, une note explicite doit signaler
    que N_eff est déflaté par chevauchement tant que N_eff < N_EFFECTIVE_MIN.
    Pour 24h (pas non-chevauchant = 1j) → pas d'alerte chevauchement."""
    # Cas 7j : 10 mesures quotidiennes → N_eff faible (chevauchement)
    ms_7j = []
    for i in range(10):
        m = _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1) + timedelta(days=i))
        m.cell.horizon = "7j"
        m.horizon = "7j"
        ms_7j.append(m)
    k = jr.compute_kpi(ms_7j)
    assert k.horizon == "7j"
    assert k.n_effective < jr.N_EFFECTIVE_MIN
    assert any("chevauchement" in a and "÷9 pour 7j" in a for a in k.alertes), (
        f"Alerte chevauchement manquante pour 7j. Alertes: {k.alertes}"
    )

    # Cas 1m
    ms_1m = []
    for i in range(10):
        m = _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1) + timedelta(days=i))
        m.cell.horizon = "1m"
        m.horizon = "1m"
        ms_1m.append(m)
    k_1m = jr.compute_kpi(ms_1m)
    assert k_1m.horizon == "1m"
    assert any("chevauchement" in a and "÷60 pour 1m" in a for a in k_1m.alertes), (
        f"Alerte chevauchement manquante pour 1m. Alertes: {k_1m.alertes}"
    )

    # Cas 24h : pas d'alerte chevauchement (pas non-chevauchant = 1j → pas de déflation)
    ms_24h = []
    for i in range(10):
        m = _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1) + timedelta(days=i))
        ms_24h.append(m)
    k_24h = jr.compute_kpi(ms_24h)
    assert k_24h.horizon == "24h"
    assert not any("chevauchement" in a for a in k_24h.alertes), (
        f"Pas d'alerte chevauchement attendue pour 24h. Alertes: {k_24h.alertes}"
    )


def test_compute_kpi_garde_les_30_dernieres():
    """Si > 30 mesures, on garde les 30 plus récentes (par échéance)."""
    ms = []
    # 50 mesures FAUSSE anciennes
    for i in range(50):
        ms.append(_make_measure(jr.OUTCOME_FAUSSE, echeance=date(2026, 1, 1) + timedelta(days=i)))
    # 30 mesures VRAI récentes
    for i in range(30):
        ms.append(_make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 4, 1) + timedelta(days=i)))
    ms.sort(key=lambda m: m.echeance)
    k = jr.compute_kpi(ms)
    assert k.n_total == 30
    assert k.n_vrai == 30
    assert k.taux_pct == pytest.approx(100.0)


def test_compute_kpi_interrompus_exclus_de_la_fenetre():
    """Les suivi-interrompu n'entrent pas dans la fenêtre mais sont comptés à part."""
    ms = []
    for i in range(5):
        ms.append(_make_measure(jr.OUTCOME_INTERROMPU, echeance=date(2026, 1, 1) + timedelta(days=i)))
    for i in range(3):
        ms.append(_make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 2, 1) + timedelta(days=i)))
    k = jr.compute_kpi(ms)
    assert k.n_total == 3
    assert k.interrompus_recents == 5
    assert any("interrompu" in a for a in k.alertes)


# ---------------------------------------------------------------------------
# measure() — orchestration sur des bulletins fictifs
# ---------------------------------------------------------------------------

def test_measure_n_inclut_que_les_horizons_echus(tmp_path, fiches_dict):
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    # bulletin émis il y a 2 jours : 24h échu, 7j et 1m PAS échus
    d_em = date(2026, 5, 27)
    today = date(2026, 5, 29)
    _write_bulletin(
        bulletins, d_em,
        [("Pétrole (Brent)", ("LONG", 0.5), ("SHORT", -0.5), ("LONG", 0.3))],
    )
    _write_prix_emission(prix, d_em, {"BZ=F": 100.0})

    measures, kpis = jr.measure(
        today=today,
        bulletins_dir=bulletins,
        prix_emission_dir=prix,
        fiches=fiches_dict,
        fetch_price=lambda t: 102.0,
    )
    # Seul l'horizon 24h doit être mesuré
    horizons_mesurees = sorted({m.horizon for m in measures})
    assert horizons_mesurees == ["24h"]
    assert ("petrole", "24h") in kpis


def test_measure_suivi_interrompu_si_prix_emission_manquant(tmp_path, fiches_dict):
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    d_em = date(2026, 5, 27)
    today = date(2026, 5, 29)
    _write_bulletin(
        bulletins, d_em,
        [("Pétrole (Brent)", ("LONG", 0.5), ("SHORT", -0.5), ("LONG", 0.3))],
    )
    # prix d'émission absent (red line)
    measures, kpis = jr.measure(
        today=today,
        bulletins_dir=bulletins,
        prix_emission_dir=prix,
        fiches=fiches_dict,
        fetch_price=lambda t: 102.0,
    )
    assert all(m.outcome == jr.OUTCOME_INTERROMPU for m in measures)


def test_measure_suivi_interrompu_si_twelve_data_dead(tmp_path, fiches_dict):
    """Twelve Data injoignable → fetch_price retourne None → suivi-interrompu."""
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    d_em = date(2026, 5, 27)
    today = date(2026, 5, 29)
    _write_bulletin(bulletins, d_em, [("Pétrole (Brent)", ("LONG", 0.5), ("SHORT", -0.5), ("LONG", 0.3))])
    _write_prix_emission(prix, d_em, {"BZ=F": 100.0})
    measures, _ = jr.measure(
        today=today,
        bulletins_dir=bulletins,
        prix_emission_dir=prix,
        fiches=fiches_dict,
        fetch_price=lambda t: None,
    )
    assert all(m.outcome == jr.OUTCOME_INTERROMPU for m in measures)


def test_measure_vrai_long_apres_24h(tmp_path, fiches_dict):
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    d_em = date(2026, 5, 28)
    today = date(2026, 5, 29)  # 24h échu
    _write_bulletin(bulletins, d_em, [("Pétrole (Brent)", ("LONG", 0.5), ("SHORT", -0.5), ("LONG", 0.3))])
    _write_prix_emission(prix, d_em, {"BZ=F": 100.0})
    measures, kpis = jr.measure(
        today=today,
        bulletins_dir=bulletins,
        prix_emission_dir=prix,
        fiches=fiches_dict,
        fetch_price=lambda t: 105.0,  # +5 % > seuil 1 %
    )
    assert len(measures) == 1
    assert measures[0].outcome == jr.OUTCOME_VRAI
    assert kpis[("petrole", "24h")].n_vrai == 1


# ---------------------------------------------------------------------------
# run() — bout-en-bout (stamp + measure + write performance.md)
# ---------------------------------------------------------------------------

def test_run_ecrit_performance_md(tmp_path, fiches_dict):
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
    assert out == perf
    assert perf.exists()
    content = perf.read_text(encoding="utf-8")
    assert "Performance du bulletin" in content
    assert "Pétrole (Brent)" in content
    assert "Journaliste" in content
    # le run a aussi stampé le prix du jour
    assert (prix / f"{today.isoformat()}.json").exists()


def test_run_stamp_today_false_n_ecrase_pas(tmp_path, fiches_dict):
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    perf = tmp_path / "performance.md"
    today = date(2026, 5, 29)
    bulletins.mkdir(parents=True, exist_ok=True)
    now = datetime(2026, 5, 29, 19, 0, tzinfo=timezone.utc)
    jr.run(
        today=today, now=now,
        bulletins_dir=bulletins, prix_emission_dir=prix, performance_path=perf,
        fiches=fiches_dict, fetch_price=lambda t: 100.0, stamp_today=False,
    )
    # aucun fichier prix-emission du jour
    assert not (prix / f"{today.isoformat()}.json").exists()
