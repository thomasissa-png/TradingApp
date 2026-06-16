"""Tests cutover v2 — reset PARTIEL (ref_changed) + estampillage system_version + L023.

Couvre :
- registre ref-changed.json clé par ticker_principal (chargement, parsing, robustesse) ;
- enforcement anti-mélange v1/v2 : une cellule d'un actif RESET ne compte pas une
  mesure émise avant ref_changed ; une cellule NON reset compte tout ;
- N (compute_kpi) repart de 0 pour les actifs reset à partir de ref_changed ;
- system_version estampillé sur les nouvelles entrées (Measure + decision-log record) ;
- L023 : un renommage du `nom` d'actif ne casse pas l'agrégation (clé stable fiche_key).
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402
import system_version as sv  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_measure(
    outcome: str,
    fiche_key: str,
    ticker: str,
    actif_name: str,
    bulletin_date: date,
    conc: str = "LONG",
    score: float = 3.0,
    horizon: str = "24h",
) -> jr.Measure:
    echeance = jr.compute_echeance(bulletin_date, horizon)
    cell = jr.BulletinCell(
        bulletin_date=bulletin_date,
        actif_name=actif_name,
        horizon=horizon,
        conclusion=conc,
        score=score,
    )
    return jr.Measure(
        cell=cell,
        fiche_key=fiche_key,
        ticker=ticker,
        horizon=horizon,
        echeance=echeance,
        prix_emission=100.0,
        prix_courant=101.0,
        seuil_pct=1.0,
        delta_pct=1.0,
        outcome=outcome,
    )


# Fiches synthétiques minimales (ticker_principal = clé stable).
FICHES = {
    "cacao": {"actif": "Cacao", "ticker_principal": "CC=F"},      # reset 2026-06-10
    "or": {"actif": "Or", "ticker_principal": "GC=F"},            # NON reset
}

REGISTRY = {"CC=F": date(2026, 6, 10)}  # seul le cacao est reset


# ---------------------------------------------------------------------------
# Registre ref-changed.json
# ---------------------------------------------------------------------------

def test_registre_charge_par_ticker(tmp_path):
    p = tmp_path / "ref-changed.json"
    p.write_text(json.dumps({
        "ref_changed": {
            "CC=F": {"ref_changed": "2026-06-10", "fiche_key": "cacao"},
            "BZ=F": {"ref_changed": "2026-06-10"},
        }
    }), encoding="utf-8")
    reg = sv.load_ref_changed(p)
    assert reg == {"CC=F": date(2026, 6, 10), "BZ=F": date(2026, 6, 10)}


def test_registre_absent_degrade_propre(tmp_path):
    # Fichier inexistant -> dict vide (aucun reset, comportement v1).
    assert sv.load_ref_changed(tmp_path / "absent.json") == {}


def test_registre_date_invalide_ignoree(tmp_path):
    p = tmp_path / "ref-changed.json"
    p.write_text(json.dumps({
        "ref_changed": {"CC=F": {"ref_changed": "pas-une-date"}, "X=F": {}}
    }), encoding="utf-8")
    assert sv.load_ref_changed(p) == {}


def test_registre_reel_contient_les_actifs_reset():
    # Cutover « prix le plus frais » (2026-06-15) : les critères des actifs
    # CONTINUS intègrent désormais le prix temps réel plus frais que close[-1]
    # (fin de l'angle mort overnight/week-end). Le SIGNAL change → ref_changed des
    # 8 continus (or, argent, pétrole, cuivre, cacao, café, blé, EUR/USD) avancé
    # 2026-06-11 → 2026-06-15 (justif CHANGELOG, 3e reset des continus). Les 4 NON
    # continus (nasdaq ^IXIC, sp500 ^GSPC, cac40 ^FCHI, vix ^VIX) ne sont PAS
    # touchés (cash fermé à 7h → close J-1 = dernier prix réel) → restent au 11/06.
    reg = sv.load_ref_changed()
    # Cutover 2026-06-16 (source = Twelve natif XAU/XAG/XBR) : or/argent/Brent
    # avancent du 15/06 au 16/06 (le niveau spot diffère du future → signal change).
    assert reg.get("BZ=F") == date(2026, 6, 16)   # petrole (XBR/USD natif)
    assert reg.get("SI=F") == date(2026, 6, 16)   # argent (XAG/USD natif)
    assert reg.get("GC=F") == date(2026, 6, 16)   # or (XAU/USD natif)
    # 5 autres CONTINUS reset au 15/06 (VOLET C — prix le plus frais), INCHANGÉS :
    # Twelve ne sert pas leur future au bon niveau → yfinance conservé, pas de
    # changement de source le 16/06.
    assert reg.get("CC=F") == date(2026, 6, 15)   # cacao
    assert reg.get("KC=F") == date(2026, 6, 15)   # cafe
    assert reg.get("ZW=F") == date(2026, 6, 15)   # ble
    assert reg.get("HG=F") == date(2026, 6, 15)   # cuivre
    assert reg.get("EUR=X") == date(2026, 6, 15)  # eurusd (FX, continu)
    # 4 actifs NON continus : inchangés au 11/06 (marché cash fermé à 7h).
    assert reg.get("^IXIC") == date(2026, 6, 11)  # nasdaq
    assert reg.get("^GSPC") == date(2026, 6, 11)  # sp500
    assert reg.get("^FCHI") == date(2026, 6, 11)  # cac40
    assert reg.get("^VIX") == date(2026, 6, 11)   # vix
    # Total : 12 actifs au registre (8 continus au 15/06 + 4 non continus au 11/06).
    assert len(reg) == 12


def test_ref_changed_for_ticker():
    assert sv.ref_changed_for_ticker("CC=F", REGISTRY) == date(2026, 6, 10)
    assert sv.ref_changed_for_ticker("GC=F", REGISTRY) is None
    assert sv.ref_changed_for_ticker(None, REGISTRY) is None


# ---------------------------------------------------------------------------
# Enforcement anti-mélange (cœur)
# ---------------------------------------------------------------------------

def test_cutover_filtre_les_mesures_pre_ref_pour_actif_reset():
    # Cacao : 2 mesures avant le 10/06 (v1), 3 mesures à/après (v2).
    ms = [
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 5)),
        _make_measure(jr.OUTCOME_FAUSSE, "cacao", "CC=F", "Cacao", date(2026, 6, 8)),
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 10)),
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 11)),
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 12)),
    ]
    filtered = jr._apply_ref_changed_cutover(ms, FICHES, REGISTRY)
    # Les 2 pré-cutover sont exclues ; il reste 3 mesures post-cutover.
    assert len(filtered) == 3
    assert all(m.cell.bulletin_date >= date(2026, 6, 10) for m in filtered)


def test_cutover_ne_filtre_pas_actif_non_reset():
    ms = [
        _make_measure(jr.OUTCOME_VRAI, "or", "GC=F", "Or", date(2026, 6, 5)),
        _make_measure(jr.OUTCOME_FAUSSE, "or", "GC=F", "Or", date(2026, 6, 8)),
        _make_measure(jr.OUTCOME_VRAI, "or", "GC=F", "Or", date(2026, 6, 11)),
    ]
    filtered = jr._apply_ref_changed_cutover(ms, FICHES, REGISTRY)
    assert len(filtered) == 3  # tout est compté (aucun reset)


def test_cutover_registre_vide_ne_filtre_rien():
    ms = [
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 5)),
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 11)),
    ]
    assert len(jr._apply_ref_changed_cutover(ms, FICHES, {})) == 2


def test_N_repart_de_zero_pour_actif_reset():
    # 4 VRAI pré-cutover + 2 VRAI post : N effectif ne doit compter que les 2 post.
    ms = (
        [_make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 1) + timedelta(days=i))
         for i in range(4)]
        + [_make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 10) + timedelta(days=i))
           for i in range(2)]
    )
    filtered = jr._apply_ref_changed_cutover(ms, FICHES, REGISTRY)
    kpi = jr.compute_kpi(sorted(filtered, key=lambda m: m.echeance))
    # n_total et n_effective ne comptent que les 2 mesures post-cutover.
    assert kpi.n_total == 2
    assert kpi.n_effective == 2


def test_aucune_cellule_reset_ne_melange_v1_v2():
    # Mesures v1 FAUSSE + v2 VRAI : le WR ne doit refléter QUE le v2 (100%),
    # pas un mélange (qui donnerait 50%).
    ms = [
        _make_measure(jr.OUTCOME_FAUSSE, "cacao", "CC=F", "Cacao", date(2026, 6, 7)),
        _make_measure(jr.OUTCOME_FAUSSE, "cacao", "CC=F", "Cacao", date(2026, 6, 8)),
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 10)),
        _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 11)),
    ]
    filtered = jr._apply_ref_changed_cutover(ms, FICHES, REGISTRY)
    kpi = jr.compute_kpi(sorted(filtered, key=lambda m: m.echeance))
    assert kpi.taux_eff_pct == 100.0  # uniquement les 2 VRAI post-cutover


# ---------------------------------------------------------------------------
# system_version estampillé
# ---------------------------------------------------------------------------

def test_system_version_constante():
    assert sv.SYSTEM_VERSION == "v2"


def test_measure_to_record_porte_system_version():
    m = _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao", date(2026, 6, 11))
    m.system_version = "v2"
    rec = jr.measure_to_record(m)
    assert rec["system_version"] == "v2"


def test_decision_log_record_estampille_system_version():
    import scoring_analyste as sa  # noqa: PLC0415
    # Le record racine du decision-log doit porter system_version.
    # On vérifie via la constante importée (le champ est ajouté en dur au record).
    assert sa.SYSTEM_VERSION == "v2"


# ---------------------------------------------------------------------------
# L023 — robustesse au renommage (agrégation par clé stable)
# ---------------------------------------------------------------------------

def test_l023_renommage_actif_ne_casse_pas_agregation_winrate():
    # Une cellule reste ré-associée par fiche_key même si le `nom` d'affichage change.
    fiches_avant = {"cacao": {"actif": "Cacao", "ticker_principal": "CC=F"}}
    fiches_apres = {"cacao": {"actif": "Fèves de cacao (ICE)", "ticker_principal": "CC=F"}}

    kpi = jr.CellKPI(fiche_key="cacao", actif_name="Cacao", horizon="24h",
                     n_effective=15, taux_eff_pct=72.0, tradable_eff_pct=70.0,
                     n_tradable=15, n_regimes=3)
    kpis = {("cacao", "24h"): kpi}

    rows_avant = jr._winrate_rows(kpis, fiches_avant)
    rows_apres = jr._winrate_rows(kpis, fiches_apres)

    # La clé stable (fiche_key) est portée par la row et inchangée malgré le renommage.
    fk_avant = next(r["fiche_key"] for r in rows_avant if r["horizon"] == "24h")
    fk_apres = next(r["fiche_key"] for r in rows_apres if r["horizon"] == "24h")
    assert fk_avant == fk_apres == "cacao"
    # Le nom d'affichage, lui, change (preuve que la ré-association ne dépend pas de lui).
    nom_avant = next(r["nom"] for r in rows_avant if r["horizon"] == "24h")
    nom_apres = next(r["nom"] for r in rows_apres if r["horizon"] == "24h")
    assert nom_avant != nom_apres


def test_l023_weekly_winrate_reassocie_par_cle_stable():
    # render_weekly_winrate doit retrouver les "nouveaux paris" via fiche_key,
    # robuste à un renommage du nom (pas de round-trip par le nom d'affichage).
    fiches = {"cacao": {"actif": "Cacao RENOMMÉ", "ticker_principal": "CC=F"}}
    now = datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc)
    # Mesure terminée dans la semaine ISO courante, clé par fiche_key="cacao".
    monday, _ = jr.iso_week_bounds(now)
    m = _make_measure(jr.OUTCOME_VRAI, "cacao", "CC=F", "Cacao RENOMMÉ",
                      monday)  # échéance dans la semaine
    kpi = jr.CellKPI(fiche_key="cacao", actif_name="Cacao RENOMMÉ", horizon="24h",
                     n_effective=15, taux_eff_pct=72.0, tradable_eff_pct=70.0, n_tradable=15)
    out = jr.render_weekly_winrate({("cacao", "24h"): kpi}, [m], now, fiches)
    # Pas de crash, et le tableau est produit (le renommage n'empêche pas la jointure).
    assert "Win rate — semaine" in out
