"""Tests — le « POURQUOI » causal dans le Bilan du jour (brief B).

La cause d'un repli (Bloc 1) ou d'un gros move (Bloc 2) n'est citée QUE si elle
est tracée : une news HIGH sur l'actif horodatée (ingestion) après l'heure de
référence. Aucune news high tracée → « cause non identifiée » / « cause non
tracée » (zéro invention, JAMAIS d'explication fabriquée).
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bilan_jour as bj  # noqa: E402

DJ = date(2026, 6, 18)

HEADER = (
    "# log\n"
    "| date | L1 | L2 | trigger | cours | latence | R | source | zone | cat | "
    "pat | impacts | materiality | reliability | event_id | canonical_date | nature |\n"
    "|---|---|\n"
)


def _row(date_s, trigger, asset, mat, eid):
    impacts = f"{asset}:SHORT:{mat}" if asset else ""
    return (
        f"| {date_s} |  | {trigger[:15]} | {trigger} | {asset} |  | 1 | src | G | "
        f"macro |  | {impacts} | {mat} | confirmed | {eid} | {date_s} | structurel |\n"
    )


def _measure(actif, call, delta, seuil, horizon="24h"):
    return NS(
        cell=NS(actif_name=actif, conclusion=call),
        horizon=horizon, delta_pct=delta, seuil_pct=seuil,
    )


@pytest.fixture
def log_or_news_apres_pic(tmp_path: Path) -> Path:
    """events-log : une news HIGH sur l'Or ingérée à 13h UTC (après le pic 12h)."""
    p = tmp_path / "events-log.md"
    content = HEADER
    content += "<!-- batch 2026-06-18T07:00:00Z : 1 events -->\n"
    content += _row("2026-06-18", "Gold morning context", "GOLD", "medium", "m1")
    content += "<!-- batch 2026-06-18T13:00:00Z : 1 events -->\n"
    content += _row(
        "2026-06-18", "Fed hawkish surprise sinks gold", "GOLD", "high", "a1"
    )
    p.write_text(content, encoding="utf-8")
    return p


# ===========================================================================
# Bloc 1 — cause du repli après le pic
# ===========================================================================

def test_cause_repli_citee_quand_news_high_apres_pic(log_or_news_apres_pic: Path):
    # Or LONG : pic +1,0 % à 12h, clôture +0,3 % (repli). Une news high sur l'Or
    # est ingérée à 13h UTC (15h Paris > 12h) → citée comme cause probable.
    meas = [_measure("Or", "LONG", 0.3, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}},
        "18h": {"Or": {"call": "LONG", "fav_pct": 0.5, "heure": "18h05"}},
    }
    p = bj.compute_perf_top3(
        meas, selmap, tracking, date_j=DJ, events_path=log_or_news_apres_pic
    )[0]
    assert p.pic_heure == "12h"
    assert p.cause_repli is not None
    assert "Fed hawkish surprise sinks gold" in p.cause_repli


def test_cause_repli_non_identifiee_si_aucune_news_high(tmp_path: Path):
    # Aucune news high sur l'Or après le pic → cause_repli None (zéro invention).
    p = tmp_path / "events-log.md"
    p.write_text(
        HEADER
        + "<!-- batch 2026-06-18T13:00:00Z : 1 events -->\n"
        + _row("2026-06-18", "Gold minor note", "GOLD", "low", "x1"),
        encoding="utf-8",
    )
    meas = [_measure("Or", "LONG", 0.3, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}},
        "18h": {"Or": {"call": "LONG", "fav_pct": 0.5, "heure": "18h05"}},
    }
    line = bj.compute_perf_top3(meas, selmap, tracking, date_j=DJ, events_path=p)[0]
    assert line.cause_repli is None


def test_pas_de_cause_si_pas_de_repli(log_or_news_apres_pic: Path):
    # Pic à la clôture (pas de repli) → on ne cherche aucune cause (cause_repli None).
    meas = [_measure("Or", "LONG", 1.2, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "LONG", "fav_pct": 0.4, "heure": "12h05"}},
        "18h": {"Or": {"call": "LONG", "fav_pct": 0.8, "heure": "18h05"}},
    }
    p = bj.compute_perf_top3(
        meas, selmap, tracking, date_j=DJ, events_path=log_or_news_apres_pic
    )[0]
    assert p.pic_heure == "clôture"
    assert p.cause_repli is None


def test_rendu_bloc1_affiche_la_cause(log_or_news_apres_pic: Path):
    meas = [_measure("Or", "LONG", 0.3, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}},
        "18h": {"Or": {"call": "LONG", "fav_pct": 0.5, "heure": "18h05"}},
    }
    bilan = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 18, 22, 15))
    bilan.perf_top3 = bj.compute_perf_top3(
        meas, selmap, tracking, date_j=DJ, events_path=log_or_news_apres_pic
    )
    md = "\n".join(bj._render_bloc1_perf_top3(bilan))
    assert "coïncide avec : Fed hawkish surprise sinks gold" in md


def test_rendu_bloc1_cause_non_identifiee(tmp_path: Path):
    p = tmp_path / "events-log.md"
    p.write_text(HEADER + "<!-- batch 2026-06-18T13:00:00Z : 0 events -->\n", encoding="utf-8")
    meas = [_measure("Or", "LONG", 0.3, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}},
        "18h": {"Or": {"call": "LONG", "fav_pct": 0.5, "heure": "18h05"}},
    }
    bilan = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 18, 22, 15))
    bilan.perf_top3 = bj.compute_perf_top3(meas, selmap, tracking, date_j=DJ, events_path=p)
    md = "\n".join(bj._render_bloc1_perf_top3(bilan))
    assert "non identifiée (pas de catalyseur tracé)" in md


# ===========================================================================
# Bloc 2 — pourquoi le gros move (news high sur l'actif ce jour)
# ===========================================================================

def test_gros_move_cause_tracee(log_or_news_apres_pic: Path):
    # Cuivre hors top 3 : gros move ; news high sur GOLD seulement → pas de cause
    # pour le Cuivre (mapping par actif). On vérifie qu'un actif SANS news high
    # ce jour rend cause_move None.
    meas = [_measure("Cuivre", "LONG", 2.0, 0.5)]
    selmap = {}  # non sélectionné
    g = bj.compute_gros_moves_autres(
        meas, selmap, {}, 0.6, date_j=DJ, events_path=log_or_news_apres_pic
    )[0]
    assert g.cause_move is None


def test_gros_move_cause_matchee_sur_le_bon_actif(log_or_news_apres_pic: Path):
    # Or hors top 3 avec gros move → la news high GOLD du jour est citée.
    meas = [_measure("Or", "SHORT", 2.0, 0.5)]
    selmap = {}
    g = bj.compute_gros_moves_autres(
        meas, selmap, {}, 0.6, date_j=DJ, events_path=log_or_news_apres_pic
    )[0]
    assert g.cause_move is not None
    assert "Fed hawkish surprise sinks gold" in g.cause_move


def test_rendu_bloc2_cause_non_tracee(log_or_news_apres_pic: Path):
    meas = [_measure("Cuivre", "LONG", 2.0, 0.5)]
    bilan = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 18, 22, 15))
    bilan.gros_moves_autres = bj.compute_gros_moves_autres(
        meas, {}, {}, 0.6, date_j=DJ, events_path=log_or_news_apres_pic
    )
    md = "\n".join(bj._render_bloc2_gros_moves(bilan))
    assert "cause non tracée" in md


# ===========================================================================
# Bloc 3 — apprentissage avec le POURQUOI causal
# ===========================================================================

def test_apprentissage_inclut_pourquoi_repli():
    # Construit une PerfTop3Ligne en repli avec cause tracée → l'apprentissage la cite.
    perf = [
        bj.PerfTop3Ligne(
            actif="Or", call="LONG", fav_12h=1.0, fav_18h=0.5, fav_cloture=0.3,
            pic_valeur=1.0, pic_heure="12h", points_manquants=[],
            verdict="x", vendre_reco=None,
            cause_repli="Fed hawkish surprise sinks gold",
        )
    ]
    lignes = bj.compute_apprentissage_jour(perf, [])
    joined = "\n".join(lignes)
    assert "Sortie tardive sur **Or**" in joined
    assert "car : Fed hawkish surprise sinks gold" in joined


def test_apprentissage_repli_cause_non_identifiee():
    perf = [
        bj.PerfTop3Ligne(
            actif="Or", call="LONG", fav_12h=1.0, fav_18h=0.5, fav_cloture=0.3,
            pic_valeur=1.0, pic_heure="12h", points_manquants=[],
            verdict="x", vendre_reco=None, cause_repli=None,
        )
    ]
    lignes = bj.compute_apprentissage_jour(perf, [])
    joined = "\n".join(lignes)
    assert "cause non identifiée (pas de catalyseur tracé)" in joined


def test_apprentissage_gros_move_avec_cause():
    gm = [
        bj.GrosMoveAutre(
            actif="Cuivre", call="LONG", mouvement_pct=2.0, direction_juste=True,
            raison_non_select="hors top 3", apprentissage="x",
            cause_move="China stimulus boosts copper",
        )
    ]
    lignes = bj.compute_apprentissage_jour([], gm)
    joined = "\n".join(lignes)
    assert "porté par : China stimulus boosts copper" in joined
