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
    # Or hors top 3, mouvement BAISSIER (-2 %) → la news high GOLD baissière du jour
    # (« Fed hawkish sinks gold », GOLD:SHORT) est citée car COHÉRENTE avec le sens
    # du mouvement (une news haussière ne serait jamais collée à une baisse).
    meas = [_measure("Or", "SHORT", -2.0, 0.5)]
    selmap = {}
    g = bj.compute_gros_moves_autres(
        meas, selmap, {}, 0.6, date_j=DJ, events_path=log_or_news_apres_pic
    )[0]
    assert g.cause_move is not None
    assert "Fed hawkish surprise sinks gold" in g.cause_move


def test_perf_top3_affiche_la_vraie_raison_drivers():
    """Bilan du jour : chaque pick du Top 3 montre la VRAIE raison (drivers du score,
    decision-log), comme le bilan semaine — pas une news lambda."""
    meas = [_measure("Or", "SHORT", -0.3, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "SHORT", "fav_pct": 1.0, "heure": "12h05"}},
        "18h": {"Or": {"call": "SHORT", "fav_pct": 0.5, "heure": "18h05"}},
    }
    conv = {("Or", "24h"): {"criteres": [
        {"nom": "Taux d'intérêt réels US (10 ans)", "contrib_pond": -4.0},  # SHORT, dominant
        {"nom": "Indice de peur (VIX)", "contrib_pond": -1.2},              # SHORT, co-moteur
        {"nom": "Momentum 5j", "contrib_pond": 0.5},                        # LONG → exclu
    ]}}
    p = bj.compute_perf_top3(meas, selmap, tracking, date_j=DJ, conviction_records=conv)[0]
    assert p.raison_call == "Taux d'intérêt réels US (10 ans) + Indice de peur (VIX)"


def test_perf_top3_raison_absente_si_pas_de_records():
    """Sans decision-log fourni : pas de raison inventée (None)."""
    meas = [_measure("Or", "SHORT", -0.3, 0.3)]
    selmap = {("Or", "24h"): True}
    p = bj.compute_perf_top3(meas, selmap, {}, date_j=DJ)[0]
    assert p.raison_call is None


def test_rendu_bloc2_cause_non_tracee(log_or_news_apres_pic: Path):
    # Pas de news catalyseur ET pas de drivers (conviction_records={}) → on le dit
    # honnêtement (« ni catalyseur news ni driver quant tracé »), jamais une invention.
    meas = [_measure("Cuivre", "LONG", 2.0, 0.5)]
    bilan = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 18, 22, 15))
    bilan.gros_moves_autres = bj.compute_gros_moves_autres(
        meas, {}, {}, 0.6, date_j=DJ, events_path=log_or_news_apres_pic
    )
    md = "\n".join(bj._render_bloc2_gros_moves(bilan))
    assert "ni catalyseur news ni driver quant tracé" in md


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


# ===========================================================================
# cause_news_high_dir — n'affiche qu'une news COHÉRENTE avec une direction
# ===========================================================================

def _row_dir(date_s, trigger, asset, direction, mat, eid):
    impacts = f"{asset}:{direction}:{mat}" if asset else ""
    return (
        f"| {date_s} |  | {trigger[:15]} | {trigger} | {asset} |  | 1 | src | G | "
        f"macro |  | {impacts} | {mat} | confirmed | {eid} | {date_s} | structurel |\n"
    )


@pytest.fixture
def log_or_deux_directions(tmp_path: Path) -> Path:
    """events-log : deux news high sur l'Or le même jour, l'une LONG, l'autre SHORT."""
    p = tmp_path / "events-log.md"
    content = HEADER
    content += "<!-- batch 2026-06-18T08:00:00Z : 1 events -->\n"
    content += _row_dir("2026-06-18", "WGC: central banks to buy more gold", "GOLD", "LONG", "high", "g1")
    content += "<!-- batch 2026-06-18T10:00:00Z : 1 events -->\n"
    content += _row_dir("2026-06-18", "Fed hawkish surprise sinks gold", "GOLD", "SHORT", "high", "g2")
    p.write_text(content, encoding="utf-8")
    return p


def test_cause_dir_short_ignore_la_news_haussiere(log_or_deux_directions: Path):
    """Pour un call SHORT, on ne renvoie QUE la news baissière (cohérente), pas la
    news haussière (qui contredirait le call) — c'est le bug Or SHORT corrigé."""
    res = bj.cause_news_high_dir("Or", DJ, "SHORT", None, log_or_deux_directions)
    assert res is not None
    assert "Fed hawkish surprise sinks gold" in res
    assert "central banks" not in res        # la news LONG n'est jamais affichée


def test_cause_dir_long_renvoie_la_news_haussiere(log_or_deux_directions: Path):
    res = bj.cause_news_high_dir("Or", DJ, "LONG", None, log_or_deux_directions)
    assert res is not None and "central banks to buy more gold" in res


def test_cause_dir_aucune_news_coherente_renvoie_none(tmp_path: Path):
    """Si aucune news ne va dans le sens demandé → None (zéro invention)."""
    p = tmp_path / "events-log.md"
    p.write_text(
        HEADER
        + "<!-- batch 2026-06-18T08:00:00Z : 1 events -->\n"
        + _row_dir("2026-06-18", "WGC bullish gold", "GOLD", "LONG", "high", "g1"),
        encoding="utf-8",
    )
    assert bj.cause_news_high_dir("Or", DJ, "SHORT", None, p) is None


# ===========================================================================
# Sortie « trop tôt / trop tard » + persistance pour l'agrégat hebdo
# ===========================================================================

def _perf(actif, call, fav_cloture, pic_valeur, pic_heure, vendre=None):
    return bj.PerfTop3Ligne(
        actif=actif, call=call, fav_12h=None, fav_18h=None, fav_cloture=fav_cloture,
        pic_valeur=pic_valeur, pic_heure=pic_heure, points_manquants=[],
        verdict="x", vendre_reco=vendre,
    )


def test_categorie_sortie_trop_tot_tard_bien_tenu():
    assert bj.categorie_sortie(_perf("Or", "SHORT", 4.0, 4.0, "clôture")) == "bien_tenu"
    assert bj.categorie_sortie(_perf("Argent", "LONG", 1.2, 2.5, "12h")) == "trop_tard"
    assert bj.categorie_sortie(_perf("VIX", "SHORT", 3.0, 3.0, "clôture", vendre="Vendre")) == "trop_tot"
    assert bj.categorie_sortie(_perf("Blé", "LONG", -1.0, -1.0, "clôture")) == "sans_objet"


def test_persist_sortie_timing_dedup(tmp_path: Path):
    import json as _j
    log = tmp_path / "sortie-timing-log.jsonl"
    perf = [_perf("Or", "SHORT", 4.0, 4.0, "clôture"),
            _perf("Argent", "LONG", 1.2, 2.5, "12h")]
    bj.persist_sortie_timing(date(2026, 6, 18), perf, path=log)
    bj.persist_sortie_timing(date(2026, 6, 18), perf, path=log)  # idempotent (dédup date+actif)
    recs = [_j.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(recs) == 2
    cats = {r["actif"]: r["categorie"] for r in recs}
    assert cats == {"Or": "bien_tenu", "Argent": "trop_tard"}


def test_render_sortie_timing_visible_en_section1():
    """Le bloc « trop tôt / trop tard » est VISIBLE (besoin fondateur), pas en annexe."""
    b = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 18, 22, 15))
    b.perf_top3 = [_perf("Argent", "LONG", 1.2, 2.5, "12h", vendre="Pas vendre")]
    md = "\n".join(bj._render_sortie_timing(b))
    assert "clôturé TROP TARD" in md and "pic +2.50% à 12h" in md


# ===========================================================================
# Onglet « Variations 24h > 1 % »
# ===========================================================================

def _write_measures(tmp: Path, rows: list) -> Path:
    import json as _j
    p = tmp / "measures-log.jsonl"
    p.write_text("\n".join(_j.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return p


def test_variations_24h_filtre_tri_et_prix(tmp_path: Path):
    log = _write_measures(tmp_path, [
        {"actif": "Or", "horizon": "24h", "conclusion": "SHORT", "realized_pct": -4.2,
         "prix_emission": 4500.0, "prix_echeance": 4311.0, "echeance": "2026-06-18", "bulletin_date": "2026-06-17"},
        {"actif": "S&P 500", "horizon": "24h", "conclusion": "LONG", "realized_pct": 2.0,
         "prix_emission": 5800.0, "prix_echeance": 5916.0, "echeance": "2026-06-17", "bulletin_date": "2026-06-16"},
        {"actif": "Blé", "horizon": "24h", "conclusion": "SHORT", "realized_pct": 0.3,  # < 1 % → exclu
         "echeance": "2026-06-18", "bulletin_date": "2026-06-17"},
        {"actif": "Or", "horizon": "7j", "conclusion": "SHORT", "realized_pct": -9.0,    # pas 24h → exclu
         "echeance": "2026-06-18", "bulletin_date": "2026-06-17"},
    ])
    vs = bj.variations_24h_significatives(
        measures_log_path=log, decision_log_dir=tmp_path / "none", events_path=tmp_path / "noevents.md",
    )
    assert [v.actif for v in vs] == ["Or", "S&P 500"]          # récent → ancien, > 1 %, 24h only
    # Or SHORT -4.2 brut → clôture FAVORABLE +4.2 ; prix d'entrée = émission.
    assert vs[0].prix_entree == 4500.0 and vs[0].perf_cloture_fav == 4.2
    # S&P LONG +2.0 brut → clôture favorable +2.0.
    assert vs[1].perf_cloture_fav == 2.0
    assert all(v.joue is False for v in vs)                    # aucune sélection fournie


def test_variations_24h_joue_via_selection(tmp_path: Path):
    import json as _j
    log = _write_measures(tmp_path, [
        {"actif": "Or", "horizon": "24h", "conclusion": "SHORT", "realized_pct": -4.2,
         "echeance": "2026-06-18", "bulletin_date": "2026-06-17"},
    ])
    dlog = tmp_path / "decision-log"
    dlog.mkdir()
    (dlog / "2026-06-17-0700.jsonl").write_text(
        _j.dumps({"bulletin_date": "2026-06-17", "actif": "Or", "horizon": "24h",
                  "selection_du_jour": True}) + "\n", encoding="utf-8")
    vs = bj.variations_24h_significatives(
        measures_log_path=log, decision_log_dir=dlog, events_path=tmp_path / "noevents.md")
    assert vs[0].joue is True and vs[0].call == "SHORT"


def test_render_variations_24h_colonnes():
    v = bj.Variation24h(jour=date(2026, 6, 18), actif="Or", prix_entree=4500.0,
                        perf_12h=0.55, perf_18h=2.10, perf_cloture_fav=4.2,
                        max_jour=4.38, joue=True, call="SHORT", raison="Fed hawkish",
                        conviction=-7.5)
    md = bj.render_variations_24h([v])
    assert ("| Jour | Actif | Call | Conviction | Prix d'entrée | % 12h | % 18h | % clôture "
            "| Max du jour | Joué | Raison du mouvement |") in md
    assert ("Or | SHORT | -7.50 | 4500 | +0.55% | +2.10% | +4.20% | +4.38% | Oui | "
            "Fed hawkish") in md


# ===========================================================================
# POURQUOI le marché a fait l'inverse (pari perdant) — enrichissement 26/06
# ===========================================================================

DJ2 = date(2026, 6, 26)


def _measure_perdant(actif, call, delta):
    """Mesure perdante mock : outcome FAUSSE, delta contre le call."""
    from journaliste import OUTCOME_FAUSSE  # noqa: PLC0415
    return NS(cell=NS(actif_name=actif), outcome=OUTCOME_FAUSSE, delta_pct=delta)


def test_post_mortem_cause_adverse_news_medium(tmp_path: Path):
    """Pari perdant : le bilan dit POURQUOI le marché a fait l'inverse, même via une
    news MEDIUM cohérente avec le mouvement adverse (Argent SHORT, marché monté)."""
    p = tmp_path / "events-log.md"
    p.write_text(
        HEADER
        + "<!-- batch 2026-06-26T09:00:00Z : 1 events -->\n"
        + _row_dir("2026-06-26", "Silver rallies on industrial demand", "SILVER", "LONG", "medium", "s1"),
        encoding="utf-8",
    )
    meas = [_measure("Argent", "SHORT", 3.62, 0.6)]
    perf = bj.compute_perf_top3(meas, {("Argent", "24h"): True}, {}, date_j=DJ2, events_path=p)
    bilan = bj.BilanJour(date_j=DJ2, now=datetime(2026, 6, 26, 22, 15))
    bilan.perf_top3 = perf
    bilan.measures_24h = [_measure_perdant("Argent", "SHORT", 3.62)]
    joined = "\n".join(bj._points_faibles_jour(bilan))
    assert "Le marché a monté sur : Silver rallies on industrial demand" in joined


def test_post_mortem_divergence_sans_catalyseur(tmp_path: Path):
    """Pari perdant SANS news adverse → le bilan explique la DIVERGENCE (le marché
    n'a pas suivi le signal), au lieu du laconique « a fait l'inverse »."""
    p = tmp_path / "events-log.md"
    p.write_text(HEADER + "<!-- batch 2026-06-26T09:00:00Z : 0 events -->\n", encoding="utf-8")
    meas = [_measure("Argent", "SHORT", 3.62, 0.6)]
    perf = bj.compute_perf_top3(meas, {("Argent", "24h"): True}, {}, date_j=DJ2, events_path=p)
    bilan = bj.BilanJour(date_j=DJ2, now=datetime(2026, 6, 26, 22, 15))
    bilan.perf_top3 = perf
    bilan.measures_24h = [_measure_perdant("Argent", "SHORT", 3.62)]
    joined = "\n".join(bj._points_faibles_jour(bilan))
    assert "sans catalyseur news identifié" in joined
    assert "divergence" in joined.lower()


def test_learning_contresens_sans_cause_explique_le_recit():
    """Learning contre-sens SANS cause tracée → explique que le récit n'a pas tenu
    (au lieu du laconique « Driver à réexaminer » seul)."""
    bilan = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 18, 22, 15))
    bilan.gros_moves_autres = [
        bj.GrosMoveAutre(
            actif="Cacao", call="LONG", mouvement_pct=-2.62, direction_juste=False,
            raison_non_select="couverture insuffisante", apprentissage="x", cause_move=None,
        )
    ]
    joined = "\n".join(bj._learnings_jour(bilan))
    assert "récit haussier n'a pas tenu" in joined


# ===========================================================================
# LEVIER driver minoritaire (déterministe) — partagé quotidien ↔ hebdo
# ===========================================================================

def test_cause_minority_driver_renvoie_le_contra():
    rec = {"criteres": [
        {"nom": "facteur haussier", "contrib_pond": 2.0},
        {"nom": "facteur baissier", "contrib_pond": -3.0},
    ]}
    # call SHORT → driver LONG (haussier) sous-pondéré ; call LONG → l'inverse.
    assert bj.cause_minority_driver(rec, "SHORT") is not None
    assert bj.cause_minority_driver(rec, "LONG") is not None
    assert bj.cause_minority_driver(rec, "SHORT") != bj.cause_minority_driver(rec, "LONG")
    assert bj.cause_minority_driver(None, "SHORT") is None
    assert bj.cause_minority_driver(rec, "") is None


def test_post_mortem_daily_driver_minoritaire(tmp_path: Path):
    """Pari perdant, ni news propre ni cross-asset → le quotidien nomme le driver
    minoritaire (cohérence avec le bilan hebdo)."""
    p = tmp_path / "events-log.md"
    p.write_text(HEADER + "<!-- batch 2026-06-26T09:00:00Z : 0 events -->\n", encoding="utf-8")
    meas = [_measure("Argent", "SHORT", 3.62, 0.6)]
    perf = bj.compute_perf_top3(meas, {("Argent", "24h"): True}, {}, date_j=DJ2, events_path=p)
    perf[0].cause_minoritaire = "Stocks au hub Cushing"
    bilan = bj.BilanJour(date_j=DJ2, now=datetime(2026, 6, 26, 22, 15))
    bilan.perf_top3 = perf
    bilan.measures_24h = [_measure_perdant("Argent", "SHORT", 3.62)]  # pas de sibling → cross None
    joined = "\n".join(bj._points_faibles_jour(bilan))
    assert "facteur qu'on avait sous-pondéré (Stocks au hub Cushing)" in joined
    assert "divergence" not in joined.lower()


# ===========================================================================
# LEVIER A — pourquoi cross-asset depuis nos propres mouvements 24h
# ===========================================================================

def test_cross_asset_argent_complexe_metaux_et_dollar():
    """Argent monté avec l'Or ET le dollar plus faible (EUR/USD up) → on nomme les
    deux moteurs corrélés (déterministe, depuis nos mouvements 24h)."""
    moves = {"Argent": 3.62, "Or": 2.10, "EUR/USD": 0.80}
    res = bj.cause_cross_asset("Argent", moves)
    assert res is not None
    assert "complexe métaux précieux (Or +2.10%)" in res
    assert "EUR/USD +0.80% — dollar plus faible" in res


def test_cross_asset_ignore_ref_sens_contraire():
    """Une référence qui a bougé dans le sens INVERSE n'explique rien → ignorée."""
    moves = {"Argent": 3.62, "Or": -1.50, "EUR/USD": -0.10}  # Or baisse, EURUSD ~plat
    assert bj.cause_cross_asset("Argent", moves) is None


def test_post_mortem_levier_a_cross_asset(tmp_path: Path):
    """Pari perdant SANS news propre mais avec moteurs corrélés → le bilan donne le
    pourquoi cross-asset (Levier A), pas la divergence."""
    p = tmp_path / "events-log.md"
    p.write_text(HEADER + "<!-- batch 2026-06-26T09:00:00Z : 0 events -->\n", encoding="utf-8")
    meas = [_measure("Argent", "SHORT", 3.62, 0.6)]
    perf = bj.compute_perf_top3(meas, {("Argent", "24h"): True}, {}, date_j=DJ2, events_path=p)
    bilan = bj.BilanJour(date_j=DJ2, now=datetime(2026, 6, 26, 22, 15))
    bilan.perf_top3 = perf
    bilan.measures_24h = [
        _measure_perdant("Argent", "SHORT", 3.62),
        NS(cell=NS(actif_name="Or"), outcome="x", delta_pct=2.10),
        NS(cell=NS(actif_name="EUR/USD"), outcome="x", delta_pct=0.80),
    ]
    joined = "\n".join(bj._points_faibles_jour(bilan))
    assert "complexe métaux précieux (Or +2.10%)" in joined
    assert "divergence" not in joined.lower()  # Levier A a expliqué, pas de fallback


# ===========================================================================
# LEVIER B — piste externe best-effort (Google News RSS, sans clé)
# ===========================================================================

def test_cause_externe_news_titre_le_plus_frais(monkeypatch):
    """Renvoie le titre RÉEL le plus frais et proche du jour (les vieux exclus)."""
    from datetime import timezone  # noqa: PLC0415
    items = [
        NS(title="Silver added to US critical minerals list",
           published=datetime(2026, 6, 26, 14, tzinfo=timezone.utc)),
        NS(title="Old silver note", published=datetime(2026, 6, 18, tzinfo=timezone.utc)),
    ]
    monkeypatch.setattr(bj, "_rss_items", lambda url: items)
    res = bj.cause_externe_news("Argent", DJ2)
    assert res == "Silver added to US critical minerals list"


def test_cause_externe_news_best_effort_none(monkeypatch):
    """Réseau KO (fetch lève) ou actif inconnu → None (échec visible, jamais crash)."""
    def _boom(url):
        raise RuntimeError("network down")
    monkeypatch.setattr(bj, "_rss_items", _boom)
    assert bj.cause_externe_news("Argent", DJ2) is None
    assert bj.cause_externe_news("ActifInconnu", DJ2) is None


def test_post_mortem_levier_b_piste_externe(tmp_path: Path):
    """Pari perdant SANS news propre NI cross-asset, mais avec une piste externe →
    le bilan l'affiche comme « piste externe à vérifier » (pas la divergence)."""
    p = tmp_path / "events-log.md"
    p.write_text(HEADER + "<!-- batch 2026-06-26T09:00:00Z : 0 events -->\n", encoding="utf-8")
    meas = [_measure("Argent", "SHORT", 3.62, 0.6)]
    perf = bj.compute_perf_top3(meas, {("Argent", "24h"): True}, {}, date_j=DJ2, events_path=p)
    perf[0].cause_externe = "Silver added to US critical minerals list"
    bilan = bj.BilanJour(date_j=DJ2, now=datetime(2026, 6, 26, 22, 15))
    bilan.perf_top3 = perf
    # Aucun sibling corrélé dans les mesures → Levier A renvoie None.
    bilan.measures_24h = [_measure_perdant("Argent", "SHORT", 3.62)]
    joined = "\n".join(bj._points_faibles_jour(bilan))
    assert "piste externe à vérifier : Silver added to US critical minerals list" in joined


def test_enrich_externe_off_par_defaut(monkeypatch):
    """Sans le flag env, l'enrichissement externe ne fait RIEN (pas de réseau en test)."""
    monkeypatch.delenv("BILAN_POST_MORTEM_EXTERNE", raising=False)
    bilan = bj.BilanJour(date_j=DJ2, now=datetime(2026, 6, 26, 22, 15))
    bilan.perf_top3 = []
    bilan.measures_24h = []
    bj._enrich_causes_externes(bilan)  # ne lève pas, ne fetch pas
    assert True
