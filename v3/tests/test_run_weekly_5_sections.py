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
# Brief S9 — GARDE-FOU HONNÊTETÉ : 0 mesure → « mesure indisponible », jamais RAS.
# Aligné sur bilan_jour._MSG_MESURE_INDISPO (même esprit, libellé semaine).
# ---------------------------------------------------------------------------

def test_mesure_indisponible_helper_vrai_sur_bilan_vide():
    bilan = rw.BilanSemaine(
        iso="2026-W25", lundi=date(2026, 6, 15), dimanche=date(2026, 6, 21), now=NOW,
    )
    assert rw._mesure_indisponible_semaine(bilan) is True


def test_mesure_indisponible_helper_faux_si_picks():
    bilan = rw.BilanSemaine(
        iso="2026-W25", lundi=date(2026, 6, 15), dimanche=date(2026, 6, 21), now=NOW,
        picks=[rw.PickSemaine(actif="Or", call="LONG", outcome="VRAI",
                              realized_pct=1.0, mouvement_dir=1.0,
                              bulletin_date=date(2026, 6, 16), ratio_news=None)],
    )
    assert rw._mesure_indisponible_semaine(bilan) is False


def test_render_affiche_mesure_indisponible_sur_0_mesure(monkeypatch, tmp_path):
    """Une semaine SANS aucune mesure (0 KPI, 0 pick, 0 tendance) doit afficher
    « mesure indisponible » dans les sections 3/4/5, JAMAIS « Aucun point faible »
    ni « Rien à améliorer » (trompeur). Garde-fou honnêteté."""
    _patch_full(monkeypatch, tmp_path)  # aucun KPI, aucune mesure, aucune tendance
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    md = bilan.markdown
    assert rw._mesure_indisponible_semaine(bilan) is True
    # Le message d'honnêteté apparaît (≥ 1 fois, sections 3/4/5).
    assert "Mesure indisponible cette semaine" in md
    assert md.count(rw._MSG_MESURE_INDISPO_SEMAINE) >= 3
    # Et les fallbacks rassurants trompeurs ne sont PAS affichés.
    assert "Aucun point faible confirmé cette semaine" not in md
    assert "Rien de statistiquement notable" not in md


def test_render_pas_de_message_indispo_si_mesure_presente(monkeypatch, tmp_path):
    """Avec au moins une cellule mesurée, le message « indisponible » n'apparaît PAS."""
    _patch_full(monkeypatch, tmp_path, kpis_list=[
        jl.CellKPI(fiche_key="or", actif_name="Or", horizon="24h",
                   n_effective=8, taux_eff_pct=90.0, wilson_low=0.60),
    ])
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    assert rw._mesure_indisponible_semaine(bilan) is False
    assert rw._MSG_MESURE_INDISPO_SEMAINE not in bilan.markdown


def test_weekly_agrege_le_measures_log_peuple_par_persist_mesures_jour(tmp_path, monkeypatch):
    """Part B point 2 : ce que persist_mesures_jour (bilan du jour) ÉCRIT est bien
    LU par l'agrégation weekly (selection_semaine). Round-trip de bout en bout :
    on persiste une mesure 24h via le module partagé, puis on l'agrège côté weekly."""
    import bilan_jour as bj
    import mesure_bilan as mb
    import journaliste as J

    # Une cellule 24h LONG VRAI, échéance dans la semaine ISO de NOW (16/06).
    cell = J.BulletinCell(actif_name="Or", conclusion="LONG", horizon="24h",
                          score=0.8, bulletin_date=date(2026, 6, 15))
    m = J.Measure(cell=cell, fiche_key="or", ticker="GC=F", horizon="24h",
                  echeance=date(2026, 6, 16), prix_emission=100.0, prix_courant=102.0,
                  seuil_pct=0.5, delta_pct=2.0, outcome=J.OUTCOME_VRAI)
    log = tmp_path / "measures-log.jsonl"
    n = mb.persist_mesures_jour([m], date(2026, 6, 15), log)
    assert n == 1 and log.exists()

    # Or sélectionné le jour de décision → l'agrégation weekly doit le voir.
    monkeypatch.setattr(bj, "load_selection_map", lambda d, dl=None: {("Or", "24h"): True})
    res = rw.selection_semaine(NOW, measures_log=log, decision_log_dir=tmp_path)
    assert res.n_select == 1
    assert res.n_vrai == 1
    assert res.win_rate == 100.0
    assert res.ampleur_moy_gagnantes == 2.0  # signe(LONG) × realized_pct 2.0


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
    # En-tête de tableau (plus de liste à puces) — avec colonne Raison.
    assert "| Actif | Tendance | Période | Perf (sens tendance) | Résultat | Raison |" in md
    assert "**Or**" in md
    assert "✅" in md and "⚪" in md            # gagne/perd visibles d'un coup d'œil
    assert "(en cours)" in md                   # phase en cours marquée


def test_points_forts_tendance_plus_de_1pct():
    # Tendance Or SHORT +5 % (> 1 % dans le bon sens) → comptée comme « bien fait ».
    seg = rw.SegmentTendance(direction="SHORT", jours=[date(2026, 6, 15)],
                             prix_debut=100.0, prix_fin=95.0)  # +5 % dans le sens SHORT
    t = rw.TendanceActif(actif="Or", ticker="GC=F", segments=[seg])
    forts = rw._points_forts(_bilan_stub([], tendances=[t]))
    blob = " ".join(forts)
    assert "Tendance Or SHORT" in blob
    assert "dans le bon sens" in blob and "+5,0 %" in blob


def test_points_forts_exclut_mouvement_sous_1pct():
    # Pick gagnant mais < 1 % → PAS « bien fait » (sous le seuil).
    forts = rw._points_forts(_bilan_stub([_pick("Or", "SHORT", "VRAI", 0.0, mv=0.6)]))
    assert all("Or" not in f for f in forts)
    assert any("Rien de net" in f for f in forts)


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
    for bloc in ("### Win rate par conviction", "### Cellules : ce qui marche / ce qui décroche",
                 "### Justesse des news vs quant"):
        assert bloc in md and md.index(bloc) > idx_annex, f"{bloc} doit être dans l'annexe"
    # Blocs retirés au tri de l'annexe : doublon page Performance + tableau statique.
    assert "### Win rate de la semaine" not in md
    assert "### Sortie de warm-up par horizon" not in md
    # Les sections 3/4 (avant l'annexe) restent de l'ANALYSE : pas ces tables.
    section34 = md[md.index("## 3."):idx_annex]
    assert "### Win rate par conviction" not in section34
    assert "### Cellules : ce qui marche" not in section34
    # Les ajustements actionnables sont en section 6 (APRÈS les learnings), avant l'annexe.
    assert "## 6. Ajustements proposés (à valider Thomas)" in section34
    assert md.index("## 5. Les learnings") < md.index("## 6. Ajustements proposés")


# ---------------------------------------------------------------------------
# Post-mortem CAUSAL (spec data-analyst S9) — sections 3/4/5 pick par pick
# ---------------------------------------------------------------------------

def _pick(actif, call, outcome, ratio_news, *, mono=False, mono_nom=None,
          coin_flip=False, quasi=False, cause_pro=None, cause_contra=None,
          raison_call=None, mv=1.0, evt=None, score=None, bdate=date(2026, 6, 16)):
    return rw.PickSemaine(
        actif=actif, call=call, outcome=outcome, realized_pct=mv, mouvement_dir=mv,
        bulletin_date=bdate, ratio_news=ratio_news, score=score,
        mono_critere=mono, mono_critere_nom=mono_nom, coin_flip=coin_flip,
        quasi_neutre=quasi, cause_pro=cause_pro, cause_contra=cause_contra,
        raison_call=raison_call, evenement_programme=evt,
    )


def test_drivers_reels_liste_tous_les_moteurs_du_sens():
    """La vraie raison = TOUS les critères matériels qui poussent dans le sens du
    call (decision-log contrib_pond), pas une news lambda ; bruit négligeable écarté."""
    rec = {"criteres": [
        {"nom": "Taux réels US", "contrib_pond": -4.66},   # SHORT, driver dominant
        {"nom": "VIX", "contrib_pond": -1.60},              # SHORT, co-moteur matériel
        {"nom": "Momentum 5j", "contrib_pond": 3.20},       # LONG → à contre-sens, exclu
        {"nom": "Bruit", "contrib_pond": -0.10},            # < 20 % du top → négligeable
    ]}
    assert rw._drivers_reels(rec, "SHORT") == ["Taux réels US", "VIX"]
    assert rw._raison_reelle(rec, "SHORT") == "Taux réels US + VIX"
    assert rw._drivers_reels(rec, "LONG") == ["Momentum 5j"]   # seul driver LONG
    assert rw._raison_reelle({"criteres": []}, "SHORT") is None  # zéro invention


def test_raison_pick_prime_le_driver_reel_sur_la_news():
    """Top 1/Top 3 : le DRIVER réel prime — jamais une news contradictoire/lambda."""
    p = _pick("Or", "SHORT", "VRAI", 0.10, mv=4.4,
              raison_call="Taux d'intérêt réels US (10 ans)",
              cause_pro="WGC: les banques centrales achètent l'or")  # haussière, ignorée
    assert rw._raison_pick(p) == "Taux d'intérêt réels US (10 ans)"


def test_raison_orientation_utilise_les_drivers_decision_log():
    """Section 2 : la raison d'une bascule = les drivers du score (decision-log)."""
    s = rw.SegmentTendance(direction="SHORT", jours=[date(2026, 6, 17)])
    cache = {date(2026, 6, 17): {("Or", "7j"): {"criteres": [
        {"nom": "Taux réels US", "contrib_pond": -5.2},
        {"nom": "Ratio or/argent", "contrib_pond": -4.9},
    ]}}}
    r = rw._raison_orientation("Or", s, flip=True, conv_cache=cache)
    assert r == "bascule SHORT : Taux réels US + Ratio or/argent"
    assert rw._raison_orientation("Or", s, flip=False,
                                  conv_cache={date(2026, 6, 17): {}}) == "—"


def test_top1_picks_un_par_jour_meilleur_score():
    lun, mar = date(2026, 6, 15), date(2026, 6, 16)
    p_or = _pick("Or", "SHORT", "VRAI", 0.0, mv=4.4, score=-5.0, bdate=lun)     # |5|
    p_ble = _pick("Blé", "SHORT", "FAUSSE", 0.0, mv=-1.0, score=-1.0, bdate=lun)  # |1|
    p_sp = _pick("S&P 500", "LONG", "FAUSSE", 0.0, mv=-1.1, score=2.0, bdate=mar)
    top1 = rw._top1_picks([p_or, p_ble, p_sp])
    assert sorted(p.actif for p in top1) == ["Or", "S&P 500"]  # 1/jour, meilleur score


def test_agg_picks_winrate_et_ampleur():
    ps = [_pick("Or", "SHORT", "VRAI", 0.0, mv=4.0),
          _pick("Blé", "SHORT", "FAUSSE", 0.0, mv=-2.0)]
    nv, nt, amp = rw._agg_picks(ps)
    assert nv == 1 and nt == 2 and amp == 1.0   # (4 + -2)/2 = 1.0


# --- Priorisation par famille + alerte événement programmé (S9 vague experts) ---

def test_macro_famille_par_cle_mappe_3_classes():
    fiches = {
        "or": {"actif": "Or", "famille": "métaux-précieux"},
        "petrole": {"actif": "Pétrole (Brent)", "famille": "énergie"},
        "eurusd": {"actif": "EUR/USD", "famille": "fx"},
        "sp500": {"actif": "S&P 500", "famille": "indices"},
        "vix": {"actif": "VIX", "famille": "volatilité"},
        "x": {"actif": "X"},  # famille absente → Autres
    }
    m = rw._macro_famille_par_cle(fiches)
    assert m["or"] == "Matières premières"
    assert m["petrole"] == "Matières premières"
    assert m["eurusd"] == "Devises"
    assert m["sp500"] == "Indices actions"
    assert m["vix"] == "Indices actions"
    assert m["x"] == "Autres"


def test_edge_par_famille_winrate_par_classe(tmp_path, monkeypatch):
    import bilan_jour as bj
    monkeypatch.setattr(bj, "load_selection_map",
                        lambda d, dl=None: {("Or", "24h"): True, ("S&P 500", "24h"): True})
    fiches = {"or": {"actif": "Or", "famille": "métaux-précieux"},
              "sp500": {"actif": "S&P 500", "famille": "indices"}}
    log = tmp_path / "measures-log.jsonl"
    _write_measures_log(log, [
        {"actif": "Or", "fiche_key": "or", "horizon": "24h", "conclusion": "SHORT",
         "outcome": "VRAI", "realized_pct": -2.0, "echeance": "2026-06-16", "bulletin_date": "2026-06-15"},
        {"actif": "S&P 500", "fiche_key": "sp500", "horizon": "24h", "conclusion": "LONG",
         "outcome": "FAUSSE", "realized_pct": -1.0, "echeance": "2026-06-16", "bulletin_date": "2026-06-15"},
    ])
    edges = rw.edge_par_famille(measures_log=log, decision_log_dir=tmp_path, fiches=fiches)
    by = {e.famille: e for e in edges}
    assert by["Matières premières"].win_rate == 100.0 and by["Matières premières"].n_total == 1
    assert by["Indices actions"].win_rate == 0.0 and by["Indices actions"].n_total == 1


def test_detail_24h_par_actif_grille(tmp_path):
    """Grille 24h par actif (équivalent 24h du tableau 7j) : call rangé au jour de
    l'échéance, week-end exclu, bilan = VRAI/(VRAI+FAUSSE)."""
    log = tmp_path / "measures-log.jsonl"
    _write_measures_log(log, [
        {"actif": "Or", "horizon": "24h", "conclusion": "SHORT", "outcome": "VRAI",
         "realized_pct": -2.0, "echeance": "2026-06-16", "bulletin_date": "2026-06-15"},   # mardi
        {"actif": "Or", "horizon": "24h", "conclusion": "SHORT", "outcome": "FAUSSE",
         "realized_pct": 1.5, "echeance": "2026-06-17", "bulletin_date": "2026-06-16"},     # mercredi
        {"actif": "Or", "horizon": "24h", "conclusion": "LONG", "outcome": "non-conclusive",
         "realized_pct": None, "echeance": "2026-06-18", "bulletin_date": "2026-06-17"},    # jeudi
        {"actif": "Or", "horizon": "24h", "conclusion": "SHORT", "outcome": "VRAI",
         "realized_pct": -1.0, "echeance": "2026-06-20", "bulletin_date": "2026-06-19"},    # samedi → exclu
    ])
    res = rw.detail_24h_par_actif(NOW, measures_log=log)
    assert len(res) == 1
    d = res[0]
    assert d.actif == "Or"
    # (direction, outcome, perf_dir) ; perf_dir = signe(call) × realized_pct.
    # 3e élément = variation BRUTE de l'actif (pas le sens du call).
    assert d.par_jour[1] == ("SHORT", "VRAI", -2.0)     # mardi : l'actif a baissé de 2 % (SHORT gagne)
    assert d.par_jour[2] == ("SHORT", "FAUSSE", 1.5)    # mercredi : l'actif a monté de 1,5 % (SHORT perd)
    assert d.par_jour[3][1] == "non-conclusive" and d.par_jour[3][2] is None  # jeudi, prix absent
    assert 5 not in d.par_jour                           # samedi exclu
    assert d.n_vrai == 1 and d.n_concl == 2             # non-conclusive hors bilan
    assert d.bilan == "1/2"


def test_section4_alerte_evenement_programme():
    faibles = rw._points_faibles(_bilan_stub([
        _pick("S&P 500", "LONG", "FAUSSE", 0.10, evt="Décision de taux Fed (FOMC)"),
    ]))
    blob = " ".join(faibles)
    assert "PRÉVISIBLE" in blob and "FOMC" in blob


def test_section4_pick_perdant_affiche_variation_brute():
    """Section 4 : chaque pick raté chiffre la variation BRUTE de l'actif (monte +, baisse −)."""
    faibles = rw._points_faibles(_bilan_stub([
        _pick("S&P 500", "LONG", "FAUSSE", 0.10, mv=-2.3),
    ]))
    blob = " ".join(faibles)
    assert "S&P 500 LONG (-2,3 %)" in blob


def test_section4_opportunite_ratee_affiche_variation_brute():
    """Section 4 : les opportunités ratées affichent la variation BRUTE de l'actif."""
    mr = rw.MouvementRate(actif="Or", jour=date(2026, 6, 16), call="SHORT",
                          perf_dir=2.4, variation_brute=-2.4, raison="opportunité ratée")
    faibles = rw._points_faibles(_bilan_stub([], mouvements_rates=[mr]))
    blob = " ".join(faibles)
    assert "Or SHORT -2,4 %" in blob  # variation brute (l'actif a baissé), pas le sens du call


def test_priorite_familles_ferme_si_N_suffisant():
    edges = [rw.EdgeFamille("Matières premières", n_vrai=8, n_total=10),
             rw.EdgeFamille("Indices actions", n_vrai=2, n_total=12)]
    line = rw._priorite_familles(_bilan_stub([], edge_familles=edges))
    assert line and "concentrer" in line and "Matières premières" in line
    assert "se méfier" in line and "Indices actions" in line


def test_priorite_familles_douce_si_petit_N():
    edges = [rw.EdgeFamille("Matières premières", n_vrai=4, n_total=5),
             rw.EdgeFamille("Indices actions", n_vrai=0, n_total=3)]
    line = rw._priorite_familles(_bilan_stub([], edge_familles=edges))
    assert line and "CONFIRMER" in line


def _bilan_stub(picks, edge_familles=None, tendances=None, detail_24h=None,
                mouvements_rates=None):
    return SimpleNamespace(
        picks=picks, tendances=tendances or [], selection=None, cellules=[],
        n_forte=0, taux_forte=None, n_faible_conv=0, taux_faible_conv=None,
        edge_familles=edge_familles or [], detail_24h=detail_24h or [],
        mouvements_rates=mouvements_rates or [],
    )


def test_pick_semaine_proprietes():
    p = _pick("Or", "SHORT", "VRAI", 0.71, mono=True, mono_nom="Tendance 20j")
    assert p.vrai is True
    assert p.news_driven is True              # 0.71 > 0.50
    assert p.drapeau_faible == "mono-critère : Tendance 20j"
    # Priorité coin-flip > mono > quasi.
    p2 = _pick("Blé", "LONG", "FAUSSE", 0.0, mono=True, coin_flip=True)
    assert p2.news_driven is False
    assert p2.drapeau_faible == "coin-flip"


def test_section3_bien_fait_avec_pourquoi_et_catalyseur():
    # « Bien fait » = > 1 % dans le bon sens ; on dit le POURQUOI réel (driver) + le
    # catalyseur news confirmant s'il y en a un (symétrie avec la section 4).
    forts = rw._points_forts(_bilan_stub([
        _pick("Pétrole (Brent)", "SHORT", "VRAI", 0.71, mv=3.8,
              raison_call="Stocks de brut US : surprise hebdomadaire + Tendance du pétrole Brent (20 jours)",
              cause_pro="Stocks US en forte hausse"),
        _pick("Or", "SHORT", "VRAI", 0.18, mv=4.4),               # pas de driver tracé → fallback
        _pick("Argent", "SHORT", "VRAI", 0.0, mv=0.6),            # < 1 % → exclu
    ]))
    blob = " ".join(forts)
    # Le POURQUOI réel (drivers du score) est affiché, pas une news lambda.
    assert ("Pétrole (Brent) SHORT (24h) : +3,8 % dans le bon sens. Pris sur : "
            "Stocks de brut US : surprise hebdomadaire + Tendance du pétrole Brent (20 jours)") in blob
    assert "Catalyseur confirmant : Stocks US en forte hausse" in blob
    # Sans driver tracé : fallback type de signal (jamais vide).
    assert "Or SHORT (24h) : +4,4 % dans le bon sens. Pris sur : quant-pur" in blob
    assert all("Argent" not in f for f in forts)   # mouvement sous 1 % écarté


def test_section4_causal_news_ratee_et_signal_faible():
    faibles = rw._points_faibles(_bilan_stub([
        # CAS A : news ratée (news-driven + cause adverse).
        _pick("S&P 500", "LONG", "FAUSSE", 0.62, cause_contra="Ventes au détail chinoises en baisse"),
        # CAS B : signal faible suivi à tort (quant + drapeau).
        _pick("Blé", "SHORT", "FAUSSE", 0.0, mono=True, mono_nom="Tendance du blé (20 jours)"),
        # CAS C : quant solide raté, cause non identifiée.
        _pick("Café (Arabica)", "SHORT", "FAUSSE", 0.10),
    ]))
    blob = " ".join(faibles)
    assert "CONTRE-SENS" in blob and "Ventes au détail chinoises en baisse" in blob
    assert "signal classé FAIBLE" in blob and "Tendance du blé (20 jours)" in blob
    assert "cause non identifiée" in blob


def test_section5_learning_news_vs_quant():
    learnings = rw._learnings_semaine(_bilan_stub([
        _pick("Pétrole (Brent)", "SHORT", "VRAI", 0.71),
        _pick("S&P 500", "LONG", "VRAI", 0.62),
        _pick("Or", "SHORT", "VRAI", 0.18),
        _pick("Café (Arabica)", "SHORT", "FAUSSE", 0.10),
    ]))
    blob = " ".join(learnings)
    assert "news-driven" in blob and "quant-pur" in blob


def test_section5_cadre_de_lecture_ouvre_la_section():
    """Le garde-fou statistique (Analyst) OUVRE TOUJOURS la section 5 (cadre avant chiffres)."""
    learnings = rw._learnings_semaine(_bilan_stub([]))
    assert learnings[0].startswith("Cadre de lecture")
    assert "50 paris cumulés" in learnings[0]
    assert len(learnings) <= 5


def test_section5_learning_rang_top1_vs_top3():
    """S-RANG : si le Top 1 gagne nettement plus que le Top 3, le dire (levier 70 %)."""
    lun, mar, mer = date(2026, 6, 15), date(2026, 6, 16), date(2026, 6, 17)
    picks = [
        _pick("Or", "SHORT", "VRAI", 0.0, score=5.0, bdate=lun),   # top1 lun
        _pick("Blé", "SHORT", "FAUSSE", 0.0, score=1.0, bdate=lun),
        _pick("Cuivre", "LONG", "VRAI", 0.0, score=5.0, bdate=mar),  # top1 mar
        _pick("VIX", "SHORT", "FAUSSE", 0.0, score=1.0, bdate=mar),
        _pick("Pétrole (Brent)", "SHORT", "VRAI", 0.0, score=5.0, bdate=mer),  # top1 mer
        _pick("S&P 500", "LONG", "FAUSSE", 0.0, score=1.0, bdate=mer),
    ]
    blob = " ".join(rw._learnings_semaine(_bilan_stub(picks)))
    assert "Top 1" in blob and "concentrer sur le Top 1" in blob
    assert "DÉCLENCHEUR" in blob and "20 paris" in blob   # seuil de bascule chiffré


def test_section5_learning_biais_long_metaux():
    """S-MÉTAUX (News Trader) : ≥ 2 LONG métaux perdus → alerte contre-pied haussier."""
    p1 = _pick("Argent", "LONG", "FAUSSE", 0.10, mv=-8.7)
    p1.famille = "métaux-précieux"
    p2 = _pick("Cuivre", "LONG", "FAUSSE", 0.10, mv=-3.0)
    p2.famille = "métaux-industriels"
    blob = " ".join(rw._learnings_semaine(_bilan_stub([p1, p2])))
    assert "Biais LONG métaux" in blob and "repricing Fed" in blob
    assert "dollar" in blob   # directive de vérification macro


def test_section5_regle_no_trade_jour_blanc():
    """S-NOTRADE : jour de verdict programmé OU Top 1 sans signal solide → jour blanc.
    Règle de précaution explicite (sans déclencheur chiffré, assumé)."""
    blob = " ".join(rw._learnings_semaine(_bilan_stub([
        _pick("S&P 500", "LONG", "FAUSSE", 0.10, evt="Décision de taux Fed (FOMC)"),
    ])))
    assert "NO-TRADE" in blob and "jour blanc" in blob
    assert "FOMC" in blob and "SANS attendre de confirmation" in blob


def test_section5_no_trade_top1_signal_faible():
    """S-NOTRADE se déclenche aussi quand le Top 1 ne tient que sur un signal faible."""
    blob = " ".join(rw._learnings_semaine(_bilan_stub([
        _pick("Cacao", "LONG", "FAUSSE", 0.10, coin_flip=True),
    ])))
    assert "NO-TRADE" in blob and "signal faible" in blob


def test_section5_opportunites_ratees_caveat_mono_critere():
    """S-B : ne remonter que les signaux solides, jamais les mono-critère."""
    mr = rw.MouvementRate(actif="Pétrole (Brent)", jour=date(2026, 6, 15), call="SHORT",
                          perf_dir=10.5, variation_brute=-10.5,
                          raison="bon call NON classé dans le top 3 ... opportunité ratée")
    blob = " ".join(rw._learnings_semaine(_bilan_stub([], mouvements_rates=[mr])))
    assert "signaux SOLIDES" in blob and "mono-critère" in blob


def test_section5_quant_pur_pile_ou_face():
    """5.2 : un quant-pur qui plafonne ≤ 40 % est pointé comme un pile-ou-face à écarter."""
    blob = " ".join(rw._learnings_semaine(_bilan_stub([
        _pick("Café (Arabica)", "SHORT", "FAUSSE", 0.10),
        _pick("Blé", "SHORT", "FAUSSE", 0.05),
    ])))
    assert "pile-ou-face" in blob


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


# --- Sortie « trop tôt / trop tard » agrégée à la semaine (vs 12h/18h) ---

def test_sortie_timing_semaine_agrege(tmp_path):
    import json as _j
    log = tmp_path / "sortie-timing-log.jsonl"
    rows = [
        {"date": "2026-06-15", "actif": "Or", "categorie": "bien_tenu",
         "pic_pct": 4.0, "pic_heure": "clôture", "cloture_pct": 4.0},
        {"date": "2026-06-16", "actif": "Argent", "categorie": "trop_tard",
         "pic_pct": 2.5, "pic_heure": "12h", "cloture_pct": 1.2},
        {"date": "2026-06-17", "actif": "VIX", "categorie": "trop_tot",
         "pic_pct": 3.0, "pic_heure": "clôture", "cloture_pct": 3.0},
        {"date": "2026-06-01", "actif": "Blé", "categorie": "trop_tard",   # hors semaine ISO
         "pic_pct": 2.0, "pic_heure": "12h", "cloture_pct": 1.0},
    ]
    log.write_text("\n".join(_j.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    agg = rw.sortie_timing_semaine(NOW, path=log)
    assert agg is not None
    assert (agg.n_bien_tenu, agg.n_trop_tard, agg.n_trop_tot) == (1, 1, 1)
    assert agg.n_juge == 3   # le 2026-06-01 (hors semaine) est exclu
    assert any("Argent" in c and "trop tard" in c for c in agg.cas)


def test_render_sortie_timing_semaine_dans_section1():
    agg = rw.SortieTimingSemaine(
        n_bien_tenu=2, n_trop_tard=1, n_trop_tot=0,
        cas=["Argent (mar) clôturé trop tard : pic +2,5 % à 12h, rendu à +1,2 %"],
    )
    L: list = []
    rw._render_sortie_timing_semaine(SimpleNamespace(sortie_timing=agg), L)
    md = "\n".join(L)
    assert "Sortie : a-t-on clôturé au bon moment" in md
    assert "1 clôturée(s) trop tard" in md and "2 bien tenue(s)" in md
    assert "Argent" in md
