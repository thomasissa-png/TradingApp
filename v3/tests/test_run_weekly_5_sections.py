"""Tests S9 — refonte du Bilan hebdomadaire en 5 sections (run_weekly).

Couvre :
- Les 5 sections présentes dans le markdown (ordre + titres).
- SECTION 2 — perf par tendance 7j : segmentation, bascule, perf SIGNÉE depuis
  le bon prix (émission du jour de prise), cas prix manquant -> « — ».
- SECTION 1 — agrégat de la Sélection 24h (win rate + ampleur gagnantes/perdantes).
- Le Manager n'applique RIEN (CA-W4 — git diff config vide, déjà couvert dans
  test_run_weekly.py, re-vérifié ici sur le chemin segmentation).
- WIN RATE ONLY : aucune valeur monétaire dans la sortie des nouvelles sections.

Source de spec : v3/docs/reco/bilan-hebdo-5-sections-s9.md.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_weekly as rw  # noqa: E402
import journaliste as jl  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
# Dimanche 2026-06-21 = fin de la semaine ISO contenant lun 15 -> dim 21 juin.
NOW = datetime(2026, 6, 21, 18, 0, tzinfo=PARIS)


# ---------------------------------------------------------------------------
# Fixtures bas niveau : écrit des decision-log + prix dans tmp_path.
# ---------------------------------------------------------------------------

def _write_decision_log(dlog_dir: Path, day: date, dirs_7j: dict, run="0723"):
    """Écrit un decision-log {day}-{run}.jsonl avec une direction 7j par actif."""
    dlog_dir.mkdir(parents=True, exist_ok=True)
    fp = dlog_dir / f"{day.isoformat()}-{run}.jsonl"
    lines = []
    for actif, direction in dirs_7j.items():
        lines.append(json.dumps({
            "bulletin_date": day.isoformat(),
            "actif": actif,
            "horizon": "7j",
            "conclusion_pm1": direction,
        }, ensure_ascii=False))
    fp.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_prix_emission(pe_dir: Path, day: date, prices: dict, suffix="-07h"):
    pe_dir.mkdir(parents=True, exist_ok=True)
    fp = pe_dir / f"{day.isoformat()}{suffix}.json"
    fp.write_text(json.dumps(prices, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# SECTION 2 — segmentation par tendance 7j + perf signée
# ---------------------------------------------------------------------------

def _fiches_or():
    return {"or": {"actif": "Or", "ticker_principal": "GC=F"}}


def test_segment_long_perf_signee(tmp_path):
    """Or LONG 3 jours, prix monte 100 -> 103 : perf = +3,0 % (sens du LONG)."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    for d in (date(2026, 6, 15), date(2026, 6, 16), date(2026, 6, 17)):
        _write_decision_log(dlog, d, {"Or": "LONG"})
    _write_prix_emission(pe, date(2026, 6, 15), {"GC=F": 100.0})
    _write_prix_emission(pe, date(2026, 6, 17), {"GC=F": 103.0})

    res = rw.tendances_par_actif(
        NOW, fiches=_fiches_or(),
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    assert len(res) == 1
    seg = res[0].segments
    assert len(seg) == 1
    assert seg[0].direction == "LONG"
    assert seg[0].perf_pct == 3.0
    assert seg[0].en_cours is True


def test_segment_short_perf_signee(tmp_path):
    """Or SHORT, prix baisse 100 -> 96 : perf = +4,0 % (le SHORT gagne)."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    for d in (date(2026, 6, 15), date(2026, 6, 16)):
        _write_decision_log(dlog, d, {"Or": "SHORT"})
    _write_prix_emission(pe, date(2026, 6, 15), {"GC=F": 100.0})
    _write_prix_emission(pe, date(2026, 6, 16), {"GC=F": 96.0})

    res = rw.tendances_par_actif(
        NOW, fiches=_fiches_or(),
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    seg = res[0].segments[0]
    assert seg.direction == "SHORT"
    assert seg.perf_pct == 4.0  # signe SHORT inverse la baisse en gain


def test_bascule_cree_nouveau_segment(tmp_path):
    """LONG (lun-mar) puis bascule SHORT (mer-jeu) : 2 segments, chacun son prix."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    _write_decision_log(dlog, date(2026, 6, 15), {"Or": "LONG"})
    _write_decision_log(dlog, date(2026, 6, 16), {"Or": "LONG"})
    _write_decision_log(dlog, date(2026, 6, 17), {"Or": "SHORT"})
    _write_decision_log(dlog, date(2026, 6, 18), {"Or": "SHORT"})
    _write_prix_emission(pe, date(2026, 6, 15), {"GC=F": 100.0})  # début seg1
    _write_prix_emission(pe, date(2026, 6, 16), {"GC=F": 102.0})  # fin seg1
    _write_prix_emission(pe, date(2026, 6, 17), {"GC=F": 102.0})  # début seg2
    _write_prix_emission(pe, date(2026, 6, 18), {"GC=F": 99.0})   # fin seg2

    res = rw.tendances_par_actif(
        NOW, fiches=_fiches_or(),
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    segs = res[0].segments
    assert len(segs) == 2
    # seg1 LONG 100->102 = +2,0 %
    assert segs[0].direction == "LONG" and segs[0].perf_pct == 2.0
    assert segs[0].en_cours is False
    # seg2 SHORT 102->99 = +2.94 % (baisse de 2,94 % dans le sens SHORT)
    assert segs[1].direction == "SHORT"
    assert round(segs[1].perf_pct, 2) == 2.94
    assert segs[1].en_cours is True


def test_prix_manquant_perf_none(tmp_path):
    """Prix d'émission absent pour le début de segment -> perf None (« — »)."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    _write_decision_log(dlog, date(2026, 6, 15), {"Or": "LONG"})
    _write_decision_log(dlog, date(2026, 6, 16), {"Or": "LONG"})
    # aucun prix écrit -> introuvable
    res = rw.tendances_par_actif(
        NOW, fiches=_fiches_or(),
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    seg = res[0].segments[0]
    assert seg.prix_debut is None
    assert seg.perf_pct is None  # zéro invention : pas de % fabriqué
    assert rw._fmt_signed_pct(seg.perf_pct) == "—"


def test_fallback_prix_ouverture(tmp_path):
    """Prix d'émission absent mais prix-ouverture présent : fallback utilisé."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    _write_decision_log(dlog, date(2026, 6, 15), {"Or": "LONG"})
    _write_decision_log(dlog, date(2026, 6, 16), {"Or": "LONG"})
    po.mkdir(parents=True, exist_ok=True)
    (po / "2026-06-15.json").write_text(json.dumps({"GC=F": 200.0}))
    (po / "2026-06-16.json").write_text(json.dumps({"GC=F": 210.0}))
    res = rw.tendances_par_actif(
        NOW, fiches=_fiches_or(),
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    seg = res[0].segments[0]
    assert seg.prix_debut == 200.0 and seg.prix_fin == 210.0
    assert seg.perf_pct == 5.0


def test_jour_sans_log_saute(tmp_path):
    """Un jour sans direction pour l'actif est sauté (zéro invention de direction)."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    _write_decision_log(dlog, date(2026, 6, 15), {"Or": "LONG"})
    # 16 : pas d'Or (autre actif)
    _write_decision_log(dlog, date(2026, 6, 16), {"Argent": "LONG"})
    _write_decision_log(dlog, date(2026, 6, 17), {"Or": "LONG"})
    _write_prix_emission(pe, date(2026, 6, 15), {"GC=F": 100.0})
    _write_prix_emission(pe, date(2026, 6, 17), {"GC=F": 105.0})
    res = rw.tendances_par_actif(
        NOW, fiches={"or": {"actif": "Or", "ticker_principal": "GC=F"},
                     "argent": {"actif": "Argent", "ticker_principal": "SI=F"}},
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    or_t = next(t for t in res if t.actif == "Or")
    # Un seul segment LONG (lun + mer, mardi sauté) : 100 -> 105 = +5,0 %
    assert len(or_t.segments) == 1
    assert or_t.segments[0].perf_pct == 5.0


# ---------------------------------------------------------------------------
# SECTION 1 — agrégat Sélection 24h (win rate + ampleur)
# ---------------------------------------------------------------------------

def _measure(actif, conclusion, outcome, prix_em, prix_cur, echeance):
    cell = SimpleNamespace(actif_name=actif, conclusion=conclusion)
    return SimpleNamespace(
        cell=cell, horizon="24h", outcome=outcome,
        prix_emission=prix_em, prix_courant=prix_cur, echeance=echeance,
    )


def test_selection_semaine_winrate_et_ampleur(tmp_path, monkeypatch):
    """Win rate sélection + ampleur gagnantes/perdantes (mouvement directionnel)."""
    # Sélection map : Or et Pétrole sélectionnés le jour de décision (15/06).
    import bilan_jour as bj
    monkeypatch.setattr(
        bj, "load_selection_map",
        lambda d, dl=None: {("Or", "24h"): True, ("Pétrole", "24h"): True},
    )
    ech = date(2026, 6, 16)  # échéance 24h dans la semaine ISO
    measures = [
        # Or LONG VRAI, prix 100 -> 102 : +2 % (gagnante)
        _measure("Or", "LONG", "VRAI", 100.0, 102.0, ech),
        # Pétrole SHORT FAUSSE, prix 80 -> 82 : -2,5 % (perdante)
        _measure("Pétrole", "SHORT", "FAUSSE", 80.0, 82.0, ech),
        # Non sélectionné : ignoré
        _measure("Cacao", "LONG", "VRAI", 10.0, 11.0, ech),
    ]
    res = rw.selection_semaine(measures, NOW, decision_log_dir=tmp_path)
    assert res.n_select == 2
    assert res.n_vrai == 1
    assert res.win_rate == 50.0
    assert res.ampleur_moy_gagnantes == 2.0
    assert res.ampleur_moy_perdantes == -2.5


def test_selection_prix_manquant_exclu_ampleur(tmp_path, monkeypatch):
    """Sélection sans prix : comptée au win rate, exclue de l'ampleur (zéro invention)."""
    import bilan_jour as bj
    monkeypatch.setattr(
        bj, "load_selection_map", lambda d, dl=None: {("Or", "24h"): True},
    )
    ech = date(2026, 6, 16)
    measures = [_measure("Or", "LONG", "VRAI", None, None, ech)]
    res = rw.selection_semaine(measures, NOW, decision_log_dir=tmp_path)
    assert res.n_select == 1 and res.n_vrai == 1
    assert res.ampleur_moy_gagnantes is None
    assert res.ampleur_moy_perdantes is None


# ---------------------------------------------------------------------------
# Les 5 sections présentes dans le markdown
# ---------------------------------------------------------------------------

def _patch_full(monkeypatch, tmp_path, kpis_list=None, measures=None):
    kpis = {(k.fiche_key, k.horizon): k for k in (kpis_list or [])}
    monkeypatch.setattr(jl, "measure", lambda **kw: (measures or [], kpis))
    monkeypatch.setattr(jl, "load_fiches", lambda *a, **k: {})
    import bilan_jour as bj
    monkeypatch.setattr(bj, "load_conviction_map", lambda *a, **k: {})
    monkeypatch.setattr(bj, "load_selection_map", lambda *a, **k: {})
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    # Pas de decision-log -> tendances vides (chemin dégradé propre).
    monkeypatch.setattr(rw, "DECISION_LOG_DIR", tmp_path / "nope")


def test_les_5_sections_presentes(monkeypatch, tmp_path):
    _patch_full(monkeypatch, tmp_path, kpis_list=[
        jl.CellKPI(fiche_key="or", actif_name="Or", horizon="24h",
                   n_effective=8, taux_eff_pct=90.0, wilson_low=0.60),
    ])
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    md = bilan.markdown
    assert "## 1. Performance des 24h sélectionnés" in md
    assert "## 2. Performance par tendance 7 jours, par actif" in md
    assert "## 3. Ce qu'on a bien fait cette semaine" in md
    assert "## 4. Ce qu'on doit améliorer" in md
    assert "## 5. Les learnings de la semaine" in md
    # Ordre strict 1 < 2 < 3 < 4 < 5.
    idx = [md.index(f"## {n}.") for n in range(1, 6)]
    assert idx == sorted(idx)


def test_5_sections_aucun_montant(monkeypatch, tmp_path):
    """WIN RATE ONLY : aucune valeur monétaire dans le markdown des 5 sections."""
    _patch_full(monkeypatch, tmp_path)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    md = bilan.markdown
    for token in ("€", "$", "P&L", "rendement", "gain en", "expectancy", "PnL"):
        assert token not in md, f"métrique monétaire interdite : {token}"


def test_manager_n_applique_rien_avec_segmentation(monkeypatch, tmp_path):
    """CA-W4 sur le chemin segmentation : aucune écriture v3/config/ (re-vérif)."""
    import subprocess
    _patch_full(monkeypatch, tmp_path)
    before = subprocess.run(
        ["git", "status", "--porcelain", "--", "v3/config/"],
        cwd=ROOT.parent, capture_output=True, text=True,
    ).stdout
    rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=True
    )
    after = subprocess.run(
        ["git", "status", "--porcelain", "--", "v3/config/"],
        cwd=ROOT.parent, capture_output=True, text=True,
    ).stdout
    assert before == after, f"v3/config/ modifié par le Manager : {after}"
