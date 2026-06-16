"""Tests Phase 3 — Bilan de la semaine dimanche 18h (R5) + le Manager.

Dérivés des critères d'acceptation CA-W1..CA-W6 + garde-fous de la mission.
Source : `v3/docs/reco/spec-refonte-5-rapports.md` §4 + §7.

WIN RATE ONLY (aucun montant). Le Manager PROPOSE, Thomas VALIDE.

Couvre :
- Seuil de proposition : N_eff >= 10 ET Wilson_low < 50% ET >= 2 semaines
  consécutives. N_eff 5-9 -> observation, PAS de proposition.
- CA-W4 : aucune écriture dans v3/config/ après un run (git diff vide) — testé.
- §4.6 : remonte aussi ce qui MARCHE (cellules porteuses).
- CA-W6 : win rate par conviction (forte/faible).
- CA-W3 : tous les champs obligatoires des propositions.
- WIN RATE ONLY : aucun symbole monétaire dans le markdown.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_weekly as rw  # noqa: E402
import journaliste as jl  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
# Un dimanche (weekday()==6) — 2026-06-14 est un dimanche.
NOW = datetime(2026, 6, 14, 18, 0, tzinfo=PARIS)


def _kpi(actif, horizon, taux, n_eff, wilson_low):
    """CellKPI minimal. wilson_low passé en PROPORTION [0,1] (comme le module)."""
    return jl.CellKPI(
        fiche_key=actif.lower().replace(" ", ""),
        actif_name=actif,
        horizon=horizon,
        n_effective=n_eff,
        taux_eff_pct=taux,
        wilson_low=wilson_low,
    )


def _patch_measure(monkeypatch, kpis_list, measures=None):
    """Mocke journaliste.measure -> (measures, kpis_dict)."""
    kpis = {(k.fiche_key, k.horizon): k for k in kpis_list}
    monkeypatch.setattr(jl, "measure", lambda **kw: (measures or [], kpis))
    # collect_cellules importe `measure` et `load_fiches` depuis journaliste.
    monkeypatch.setattr(jl, "load_fiches", lambda *a, **k: {})


def _patch_conviction_empty(monkeypatch):
    import bilan_jour as bj  # noqa: PLC0415
    monkeypatch.setattr(bj, "load_conviction_map", lambda *a, **k: {})


# ---------------------------------------------------------------------------
# Détection : seuil N_eff>=10 + Wilson_low<50% + 2 semaines (cœur du Manager)
# ---------------------------------------------------------------------------

def test_petit_N_aucune_proposition(monkeypatch, tmp_path):
    """N_eff 5-9 -> observation, JAMAIS de proposition (mesurer avant d'agir)."""
    _patch_measure(monkeypatch, [_kpi("Cuivre", "24h", 20.0, 7, 0.05)])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    assert bilan.propositions == []
    # Mais c'est bien en observation.
    assert any("Cuivre 24h" in o and "observation" in o for o in bilan.observations)


def test_premiere_semaine_aucune_proposition(monkeypatch, tmp_path):
    """N_eff>=10 + Wilson<50% mais 1ère semaine -> observation, PAS de proposition."""
    _patch_measure(monkeypatch, [_kpi("S&P 500", "24h", 30.0, 12, 0.10)])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    # state_dir vide -> aucune candidate la semaine précédente.
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=True
    )
    assert bilan.propositions == []
    assert any("S&P 500 24h" in o and "1ère semaine" in o for o in bilan.observations)


def test_deux_semaines_consecutives_genere_proposition(monkeypatch, tmp_path):
    """Faible confirmée sur 2 semaines -> proposition générée."""
    kpi = _kpi("S&P 500", "24h", 30.0, 12, 0.10)
    _patch_measure(monkeypatch, [kpi])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    # Semaine précédente : S&P déjà candidate (ISO = semaine de NOW - 7j).
    prev_iso = rw._prev_iso_label(NOW)
    rw.save_candidates_state(prev_iso, {("S&P 500", "24h")}, state_dir=tmp_path)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=True
    )
    assert len(bilan.propositions) == 1
    p = bilan.propositions[0]
    assert "S&P 500" in p["actifs"]
    # Constat chiffré sur données réelles (zéro invention).
    assert "30.0%" in p["constat"]
    assert "12" in p["constat"]


def test_proposition_champs_obligatoires(monkeypatch, tmp_path):
    """CA-W3 : tous les champs obligatoires présents et non vides."""
    kpi = _kpi("Cacao", "24h", 0.0, 11, 0.02)
    _patch_measure(monkeypatch, [kpi])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    prev_iso = rw._prev_iso_label(NOW)
    rw.save_candidates_state(prev_iso, {("Cacao", "24h")}, state_dir=tmp_path)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    assert bilan.propositions, "une proposition attendue"
    for p in bilan.propositions:
        assert rw.proposition_valide(p)
        for champ in rw.PROPOSITION_CHAMPS:
            assert p.get(champ), f"champ {champ} manquant/vide"


def test_proposition_invalide_rejetee():
    """Un champ vide rend la proposition invalide (rejet système)."""
    p = {c: "x" for c in rw.PROPOSITION_CHAMPS}
    assert rw.proposition_valide(p)
    p["risque"] = ""
    assert not rw.proposition_valide(p)


# ---------------------------------------------------------------------------
# §4.6 — remonte aussi ce qui MARCHE
# ---------------------------------------------------------------------------

def test_cellules_porteuses_remontees(monkeypatch, tmp_path):
    _patch_measure(monkeypatch, [
        _kpi("Or", "24h", 90.0, 8, 0.60),         # porteuse
        _kpi("Argent", "24h", 60.0, 6, 0.40),     # sous seuil 65% -> pas porteuse
        _kpi("EUR/USD", "24h", 70.0, 4, 0.50),    # N_eff < 5 -> pas porteuse
    ])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    porteuses = [c for c in bilan.cellules if c.porteuse]
    assert {c.actif for c in porteuses} == {"Or"}
    assert "Cellules porteuses" in bilan.markdown
    assert "Or" in bilan.markdown


# ---------------------------------------------------------------------------
# CA-W4 — AUCUNE écriture dans v3/config/ après un run (git diff vide)
# ---------------------------------------------------------------------------

def test_aucune_ecriture_config(monkeypatch, tmp_path):
    """CA-W4 : après build_bilan_semaine, git diff v3/config/ est vide."""
    _patch_measure(monkeypatch, [_kpi("S&P 500", "24h", 25.0, 11, 0.08)])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)

    before = subprocess.run(
        ["git", "diff", "--name-only", "--", "v3/config/"],
        cwd=ROOT.parent, capture_output=True, text=True,
    ).stdout
    # État porcelain AVANT (tolère une édition de config légitime non commitée
    # dans le working tree — l'invariant testé est « le Manager n'ajoute/modifie
    # RIEN », pas « v3/config/ est vierge dans l'absolu »).
    untracked_before = subprocess.run(
        ["git", "status", "--porcelain", "--", "v3/config/"],
        cwd=ROOT.parent, capture_output=True, text=True,
    ).stdout

    rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=True
    )

    after = subprocess.run(
        ["git", "diff", "--name-only", "--", "v3/config/"],
        cwd=ROOT.parent, capture_output=True, text=True,
    ).stdout
    assert before == after, f"v3/config/ modifié par le Manager : {after}"
    # Le Manager n'écrit RIEN sous config (before == after, robuste à un diff
    # config pré-existant non commité).
    untracked_after = subprocess.run(
        ["git", "status", "--porcelain", "--", "v3/config/"],
        cwd=ROOT.parent, capture_output=True, text=True,
    ).stdout
    assert untracked_after == untracked_before, (
        f"v3/config/ modifié par le Manager : {untracked_after}"
    )


# ---------------------------------------------------------------------------
# CA-W6 — win rate par conviction (forte/faible)
# ---------------------------------------------------------------------------

def test_win_rate_par_conviction(monkeypatch, tmp_path):
    """Le bilan contient un tableau conviction forte/faible (§4.7)."""
    _patch_measure(monkeypatch, [_kpi("Or", "24h", 80.0, 6, 0.55)])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    assert "Win rate par conviction" in bilan.markdown
    assert "Forte" in bilan.markdown and "Faible" in bilan.markdown


def test_conviction_n_insuffisant(monkeypatch, tmp_path):
    """N < 3 pour un niveau de conviction -> « N insuffisant » (CA-W6)."""
    _patch_measure(monkeypatch, [])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    assert "N insuffisant" in bilan.markdown


# ---------------------------------------------------------------------------
# WIN RATE ONLY — aucun montant dans le markdown
# ---------------------------------------------------------------------------

def test_win_rate_only_aucun_montant(monkeypatch, tmp_path):
    kpi = _kpi("Cacao", "24h", 0.0, 11, 0.02)
    _patch_measure(monkeypatch, [kpi, _kpi("Or", "24h", 90.0, 8, 0.60)])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(rw, "_read_weekly_archive", lambda iso: None)
    prev_iso = rw._prev_iso_label(NOW)
    rw.save_candidates_state(prev_iso, {("Cacao", "24h")}, state_dir=tmp_path)
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    md = bilan.markdown
    for token in ("€", "$", "P&L", "rendement", "gain en", "expectancy"):
        assert token not in md, f"métrique monétaire interdite trouvée : {token}"


# ---------------------------------------------------------------------------
# Persistance inter-semaines
# ---------------------------------------------------------------------------

def test_state_roundtrip(tmp_path):
    rw.save_candidates_state("2026-S23", {("Cuivre", "24h"), ("S&P 500", "7j")}, state_dir=tmp_path)
    loaded = rw.load_candidates_state("2026-S23", state_dir=tmp_path)
    assert loaded == {("Cuivre", "24h"), ("S&P 500", "7j")}


def test_state_absent_vide(tmp_path):
    assert rw.load_candidates_state("2099-S01", state_dir=tmp_path) == set()


def test_prev_iso_label():
    # NOW = 2026-06-14 (S24) -> semaine précédente = S23.
    assert rw._prev_iso_label(NOW) == "2026-S23"


# ---------------------------------------------------------------------------
# CA-W2 — win rate hebdo pris tel quel depuis l'archive
# ---------------------------------------------------------------------------

def test_archive_hebdo_reprise_telle_quelle(monkeypatch, tmp_path):
    _patch_measure(monkeypatch, [_kpi("Or", "24h", 90.0, 8, 0.60)])
    _patch_conviction_empty(monkeypatch)
    monkeypatch.setattr(
        rw, "_read_weekly_archive",
        lambda iso: "# Win rate — semaine X\n\nMARQUEUR_ARCHIVE_UNIQUE\n",
    )
    bilan = rw.build_bilan_semaine(
        now=NOW, fiches={}, fetch_price=None, state_dir=tmp_path, persist_state=False
    )
    assert "MARQUEUR_ARCHIVE_UNIQUE" in bilan.markdown
    # Le titre H1 de l'archive est retiré (on garde le corps).
    assert "# Win rate — semaine X" not in bilan.markdown
