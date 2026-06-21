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


def test_phase_un_jour_non_finale_perf_non_nulle(tmp_path):
    """Bug S9 corrigé : une phase d'UN jour suivie d'une bascule mesure désormais
    du prix de début au prix du JOUR DE BASCULE (et non début==fin → 0 %)."""
    dlog = tmp_path / "decision-log"
    pe = tmp_path / "prix-emission"
    po = tmp_path / "prix-ouverture"
    _write_decision_log(dlog, date(2026, 6, 15), {"Or": "LONG"})   # phase 1 jour
    _write_decision_log(dlog, date(2026, 6, 16), {"Or": "SHORT"})  # bascule
    _write_decision_log(dlog, date(2026, 6, 17), {"Or": "SHORT"})
    _write_prix_emission(pe, date(2026, 6, 15), {"GC=F": 100.0})  # début phase LONG
    _write_prix_emission(pe, date(2026, 6, 16), {"GC=F": 110.0})  # jour de bascule
    _write_prix_emission(pe, date(2026, 6, 17), {"GC=F": 99.0})
    res = rw.tendances_par_actif(
        NOW, fiches=_fiches_or(),
        decision_log_dir=dlog, prix_emission_dir=pe, prix_ouverture_dir=po,
    )
    segs = res[0].segments
    assert len(segs) == 2
    # Phase LONG d'un seul jour : 100 → 110 (jour de bascule) = +10 %, PAS 0 %.
    assert segs[0].direction == "LONG"
    assert segs[0].perf_pct == 10.0


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

def _write_measures_log(path: Path, records: list) -> None:
    """Écrit un measures-log.jsonl (journal persisté des verdicts)."""
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def _mrec(actif, conclusion, outcome, realized_pct, echeance, bulletin_date):
    return {
        "actif": actif, "horizon": "24h", "conclusion": conclusion,
        "outcome": outcome, "realized_pct": realized_pct,
        "echeance": echeance, "bulletin_date": bulletin_date,
    }


def test_selection_semaine_winrate_et_ampleur(tmp_path, monkeypatch):
    """Win rate sélection + ampleur gagnantes/perdantes, LU DEPUIS LE JOURNAL
    PERSISTÉ (measures-log.jsonl) — plus de re-mesure live (bug « Aucune
    sélection »). Ampleur directionnelle = signe(call) × realized_pct."""
    import bilan_jour as bj
    # Or et Pétrole sélectionnés le jour de décision (15/06), échéance 16/06.
    monkeypatch.setattr(
        bj, "load_selection_map",
        lambda d, dl=None: {("Or", "24h"): True, ("Pétrole", "24h"): True},
    )
    log = tmp_path / "measures-log.jsonl"
    _write_measures_log(log, [
        # Or LONG VRAI, prix +2 % brut → directionnel +2 % (gagnante).
        _mrec("Or", "LONG", "VRAI", 2.0, "2026-06-16", "2026-06-15"),
        # Pétrole SHORT FAUSSE, prix +2,5 % brut → directionnel −2,5 % (perdante).
        _mrec("Pétrole", "SHORT", "FAUSSE", 2.5, "2026-06-16", "2026-06-15"),
        # Cacao non sélectionné → ignoré.
        _mrec("Cacao", "LONG", "VRAI", 10.0, "2026-06-16", "2026-06-15"),
    ])
    res = rw.selection_semaine(NOW, measures_log=log, decision_log_dir=tmp_path)
    assert res.n_select == 2
    assert res.n_vrai == 1
    assert res.win_rate == 50.0
    assert res.ampleur_moy_gagnantes == 2.0
    assert res.ampleur_moy_perdantes == -2.5


def test_selection_prix_manquant_exclu_ampleur(tmp_path, monkeypatch):
    """realized_pct absent : compté au win rate, exclu de l'ampleur (zéro invention)."""
    import bilan_jour as bj
    monkeypatch.setattr(
        bj, "load_selection_map", lambda d, dl=None: {("Or", "24h"): True},
    )
    log = tmp_path / "measures-log.jsonl"
    _write_measures_log(log, [
        _mrec("Or", "LONG", "VRAI", None, "2026-06-16", "2026-06-15"),
    ])
    res = rw.selection_semaine(NOW, measures_log=log, decision_log_dir=tmp_path)
    assert res.n_select == 1 and res.n_vrai == 1
    assert res.ampleur_moy_gagnantes is None
    assert res.ampleur_moy_perdantes is None


def test_selection_semaine_ignore_non_conclusif_et_hors_semaine(tmp_path, monkeypatch):
    """Non-conclusif exclu ; échéance hors semaine ISO exclue ; dédup dernier record."""
    import bilan_jour as bj
    monkeypatch.setattr(bj, "load_selection_map", lambda d, dl=None: {("Or", "24h"): True})
    log = tmp_path / "measures-log.jsonl"
    _write_measures_log(log, [
        _mrec("Or", "LONG", "non-conclusive", None, "2026-06-16", "2026-06-15"),
        _mrec("Or", "LONG", "VRAI", 1.0, "2026-06-08", "2026-06-05"),  # semaine précédente
        # Dédup : deux records même (actif, échéance) → le dernier (VRAI) gagne.
        _mrec("Or", "LONG", "FAUSSE", -1.0, "2026-06-17", "2026-06-16"),
        _mrec("Or", "LONG", "VRAI", 1.5, "2026-06-17", "2026-06-16"),
    ])
    res = rw.selection_semaine(NOW, measures_log=log, decision_log_dir=tmp_path)
    assert res.n_select == 1 and res.n_vrai == 1  # seul le 17/06 conclusif, dédup VRAI


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


# ---------------------------------------------------------------------------
# Refonte S9 vague 5 — section 2 en TABLEAU visuel + POURQUOI + annexe repliée
# ---------------------------------------------------------------------------

def test_verdict_segment_glyphes():
    assert rw._verdict_segment(None) == "—"      # prix manquant
    assert rw._verdict_segment(0.2) == "⚪"        # sous le seuil = négligeable
    assert rw._verdict_segment(1.5) == "✅"        # gagnant
    assert rw._verdict_segment(-1.5) == "❌"       # perdant


def test_cause_segment_pourquoi_tracable():
    s = rw.SegmentTendance(direction="SHORT", jours=[date(2026, 6, 15)])
    # Direction stable gagnante (1 seul segment) = continuation.
    assert "stable" in rw._cause_segment(s, 0, 1, gagnant=True)
    # Phase perdante suivie d'une bascule = tendance retournée.
    assert "retourn" in rw._cause_segment(s, 0, 2, gagnant=False)
    # Phase gagnante issue d'une bascule = bascule captée.
    assert "captée" in rw._cause_segment(s, 1, 2, gagnant=True)


def test_section2_est_un_tableau_avec_verdicts():
    seg1 = rw.SegmentTendance(direction="LONG", jours=[date(2026, 6, 15)],
                              prix_debut=100.0, prix_fin=102.0)              # +2 % ✅
    seg2 = rw.SegmentTendance(direction="SHORT", jours=[date(2026, 6, 16)],
                              prix_debut=102.0, prix_fin=102.05, en_cours=True)  # ~0 % ⚪
    t = rw.TendanceActif(actif="Or", ticker="GC=F", segments=[seg1, seg2])
    L: list = []
    rw._render_section2_tendances(SimpleNamespace(tendances=[t]), L)
    md = "\n".join(L)
    # En-tête de tableau (plus de liste à puces).
    assert "| Actif | Tendance | Période | Perf (sens tendance) | Résultat |" in md
    assert "**Or**" in md
    assert "✅" in md and "⚪" in md            # gagne/perd visibles d'un coup d'œil
    assert "(en cours)" in md                   # phase en cours marquée


def test_points_forts_incluent_le_pourquoi():
    # Or SHORT stable gagnant → un point fort avec sa cause (continuation).
    seg = rw.SegmentTendance(direction="SHORT", jours=[date(2026, 6, 15)],
                             prix_debut=100.0, prix_fin=95.0)  # +5 % dans le sens SHORT
    t = rw.TendanceActif(actif="Or", ticker="GC=F", segments=[seg])
    forts = rw._points_forts(SimpleNamespace(
        tendances=[t], selection=None, cellules=[],
        n_forte=0, taux_forte=None,
    ))
    blob = " ".join(forts)
    assert "Or SHORT" in blob
    assert "stable" in blob or "tenue" in blob   # le POURQUOI est présent


def test_annexe_technique_repliee_hors_sections_analyse(monkeypatch, tmp_path):
    _patch_full(monkeypatch, tmp_path)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    md = bilan.markdown
    assert '<details class="weekly-annex">' in md
    assert "</details>" in md
    idx_annex = md.index('<details class="weekly-annex">')
    # Les tableaux denses descendent DANS l'annexe (après le <details>).
    for bloc in ("### Win rate par conviction", "### Cellules à surveiller",
                 "### Sortie de warm-up par horizon", "### Justesse des news vs quant"):
        assert bloc in md and md.index(bloc) > idx_annex, f"{bloc} doit être dans l'annexe"
    # Les sections 3/4 (avant l'annexe) restent de l'ANALYSE : pas ces tables.
    section34 = md[md.index("## 3."):idx_annex]
    assert "### Win rate par conviction" not in section34
    assert "### Cellules à surveiller" not in section34
    # Mais les propositions actionnables restent en section 4.
    assert "### Propositions d'ajustement" in section34


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
