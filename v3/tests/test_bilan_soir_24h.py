"""Tests — Refonte BILAN DU SOIR 24h (S9, demande fondateur, design validé).

3 blocs en tête du Bilan du jour :
  Bloc 1 — Performance 24h du Top 3 (Sélection) : fav 12h/18h/clôture, pic
           horodaté, verdict de sortie optimale relié aux heures + reco suivi.
  Bloc 2 — Gros mouvements hors Top 3 : direction juste/ratée + pourquoi pas
           sélectionné (déduit des logs, zéro invention) + apprentissage.
  Bloc 3 — Apprentissage du jour (synthèse déterministe sur les blocs 1-2).
+ persistance intraday 12h/18h (run_suivi.save/load_suivi_tracking, idempotente).

WIN RATE ONLY — aucune valeur monétaire (le % d'ampleur est OK, Thomas l'a
demandé). ZÉRO INVENTION : point manquant → « — » + trou signalé.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace as NS
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bilan_jour as bj  # noqa: E402
import mesure_bilan as mb  # noqa: E402
import run_suivi as rs  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


def _measure(actif, call, delta, seuil, horizon="24h"):
    """Stub minimal d'une Measure pour les blocs (champs lus uniquement)."""
    return NS(
        cell=NS(actif_name=actif, conclusion=call),
        horizon=horizon, delta_pct=delta, seuil_pct=seuil,
    )


# ===========================================================================
# Bloc 1 — Performance 24h du Top 3 : fav 12h/18h/clôture + pic + verdict
# ===========================================================================

def test_perf_top3_pic_a_12h_sortir_plus_tot():
    # S&P LONG : monte +1,0 % à 12h, reflue à +0,8 % puis +0,59 % à la clôture.
    # Pic = 12h ; clôture plus basse → « sortir à 12h aurait été mieux ».
    meas = [_measure("S&P 500", "LONG", 0.59, 0.3)]
    selmap = {("S&P 500", "24h"): True}
    tracking = {
        "12h": {"S&P 500": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}},
        "18h": {"S&P 500": {"call": "LONG", "fav_pct": 0.8, "heure": "18h05"}},
    }
    p = bj.compute_perf_top3(meas, selmap, tracking)[0]
    assert p.fav_12h == 1.0 and p.fav_18h == 0.8 and p.fav_cloture == 0.59
    assert p.pic_valeur == 1.0 and p.pic_heure == "12h"
    assert p.points_manquants == []
    assert "sortir à 12h aurait été mieux" in p.verdict


def test_perf_top3_monte_jusquau_bout_tenir():
    # Or SHORT : -0,5 % delta → fav clôture = +0,5 % ; pic à la clôture → tenir.
    meas = [_measure("Or", "SHORT", -0.5, 0.3)]
    selmap = {("Or", "24h"): True}
    tracking = {
        "12h": {"Or": {"call": "SHORT", "fav_pct": 0.2, "heure": "12h05"}},
        "18h": {"Or": {"call": "SHORT", "fav_pct": 0.35, "heure": "18h05"}},
    }
    p = bj.compute_perf_top3(meas, selmap, tracking)[0]
    assert p.fav_cloture == 0.5
    assert p.pic_heure == "clôture"
    assert "tenir était le bon choix" in p.verdict


def test_perf_top3_point_manquant_signale_pic_sur_dispo():
    # Pas de relevé 18h (trou) : pic calculé sur {12h, clôture} seulement.
    meas = [_measure("Cuivre", "LONG", 0.4, 0.3)]
    selmap = {("Cuivre", "24h"): True}
    tracking = {"12h": {"Cuivre": {"call": "LONG", "fav_pct": 0.9, "heure": "12h05"}}}
    p = bj.compute_perf_top3(meas, selmap, tracking)[0]
    assert p.fav_18h is None
    assert "18h" in p.points_manquants
    # Pic sur les points dispo (12h=0.9 vs clôture=0.4) → 12h.
    assert p.pic_valeur == 0.9 and p.pic_heure == "12h"


def test_perf_top3_jamais_dans_notre_sens():
    # SHORT mais le marché monte partout → fav négatif partout, rien à verrouiller.
    meas = [_measure("Blé", "SHORT", 1.0, 0.3)]
    selmap = {("Blé", "24h"): True}
    tracking = {
        "12h": {"Blé": {"call": "SHORT", "fav_pct": -0.5, "heure": "12h05"}},
        "18h": {"Blé": {"call": "SHORT", "fav_pct": -0.8, "heure": "18h05"}},
    }
    p = bj.compute_perf_top3(meas, selmap, tracking)[0]
    assert p.pic_valeur == -0.5  # le « moins pire »
    assert "jamais dans notre sens" in p.verdict


def test_perf_top3_call_discordant_ignore_le_releve():
    # Le tracking 12h porte un call opposé (bruit) → relevé ignoré (zéro invention).
    meas = [_measure("EUR/USD", "LONG", 0.3, 0.2)]
    selmap = {("EUR/USD", "24h"): True}
    tracking = {"12h": {"EUR/USD": {"call": "SHORT", "fav_pct": 1.2, "heure": "12h05"}}}
    p = bj.compute_perf_top3(meas, selmap, tracking)[0]
    assert p.fav_12h is None  # call discordant → non retenu
    assert "12h" in p.points_manquants


def test_perf_top3_non_selectionnes_exclus():
    meas = [_measure("S&P 500", "LONG", 0.5, 0.3), _measure("Or", "SHORT", -0.2, 0.3)]
    selmap = {("S&P 500", "24h"): True}  # Or non sélectionné
    res = bj.compute_perf_top3(meas, selmap, {})
    assert [p.actif for p in res] == ["S&P 500"]


# ===========================================================================
# Bloc 2 — Gros moves hors top 3 : direction + raison non-sélection + appr.
# ===========================================================================

def test_gros_move_bonne_direction_raison_tracee():
    # Cacao LONG, +3 % vs ouverture (≥ 2×seuil) → bonne direction, raison tracée.
    meas = [_measure("Cacao", "LONG", 3.0, 1.0)]
    recs = {("Cacao", "24h"): {"selection_motif_exclusion": "hors top 3"}}
    g = bj.compute_gros_moves_autres(meas, {}, recs, 0.6)[0]
    assert g.direction_juste is True
    assert g.raison_non_select == "hors top 3"
    assert "bonne direction" in g.apprentissage


def test_gros_move_mauvaise_direction():
    # Pétrole SHORT mais +4 % (monte fort) → mauvaise direction.
    meas = [_measure("Pétrole (Brent)", "SHORT", 4.0, 1.0)]
    recs = {("Pétrole (Brent)", "24h"): {"selection_motif_exclusion": "hors top 3"}}
    g = bj.compute_gros_moves_autres(meas, {}, recs, 0.6)[0]
    assert g.direction_juste is False
    assert "mauvaise direction" in g.apprentissage.lower()


def test_gros_move_sous_seuil_exclu():
    # Mouvement < 2×seuil → pas un gros move.
    meas = [_measure("Argent", "LONG", 1.5, 1.0)]  # 1.5 < 2.0
    assert bj.compute_gros_moves_autres(meas, {}, {}, 0.6) == []


def test_gros_move_tri_du_plus_gros():
    meas = [
        _measure("A", "LONG", 2.5, 1.0),
        _measure("B", "LONG", 5.0, 1.0),
        _measure("C", "LONG", -3.5, 1.0),
    ]
    res = bj.compute_gros_moves_autres(meas, {}, {}, 0.6)
    assert [g.actif for g in res] == ["B", "C", "A"]  # |5| > |3.5| > |2.5|


def test_gros_move_dans_top3_exclu_du_bloc2():
    meas = [_measure("S&P 500", "LONG", 3.0, 1.0)]
    selmap = {("S&P 500", "24h"): True}
    assert bj.compute_gros_moves_autres(meas, selmap, {}, 0.6) == []


# --- reason_non_selection : la logique « pourquoi pas sélectionné » -----------

def test_reason_motif_exact_prioritaire():
    rec = {"selection_motif_exclusion": "même pari (taux/dollar) que EUR/USD"}
    assert bj.reason_non_selection("Or", rec, 0.6, 0.7) == "même pari (taux/dollar) que EUR/USD"


def test_reason_conviction_sous_seuil_deduite():
    # Pas de motif tracé, score sous le seuil → conviction sous le seuil.
    rec = {"score_pm1": 0.2, "coverage": 0.9}
    assert bj.reason_non_selection("X", rec, 0.6, 0.7) == "conviction sous le seuil (pas assez tranchée)"


def test_reason_couverture_insuffisante_deduite():
    # Conviction forte (score haut, zéro drapeau) mais couverture < plancher.
    rec = {"score_pm1": 5.0, "coverage": 0.5}
    r = bj.reason_non_selection("X", rec, 0.6, 0.7)
    assert "couverture insuffisante" in r and "50%" in r


def test_reason_drapeau_mono_critere():
    rec = {"score_pm1": 5.0, "coverage": 0.9, "mono_critere_dominant": True}
    assert bj.reason_non_selection("X", rec, 0.6, 0.7) == "conviction non forte (mono-critère dominant)"


def test_reason_non_tracee_si_indeterminable():
    # Record absent → on le dit honnêtement (plus de « raison non tracée » vague).
    assert bj.reason_non_selection("X", None, 0.6, 0.7) == \
        "décision d'émission non retrouvée (decision-log)"
    # Conviction forte + couverture OK mais pas sélectionné = hors des 3 meilleures
    # convictions (la Sélection est capée à 3) — une VRAIE raison, fondateur 24/06.
    rec = {"score_pm1": 5.0, "coverage": 0.95}
    assert bj.reason_non_selection("X", rec, 0.6, 0.7) == \
        "hors des 3 meilleures convictions du jour (Sélection limitée à 3)"


# ===========================================================================
# Bloc 3 — Apprentissage du jour
# ===========================================================================

def test_apprentissage_sortie_ratee_et_prudence():
    perf = [bj.PerfTop3Ligne(
        actif="S&P 500", call="LONG", fav_12h=1.0, fav_18h=0.8, fav_cloture=0.59,
        pic_valeur=1.0, pic_heure="12h", points_manquants=[], verdict="x", vendre_reco=None,
    )]
    gros = [bj.GrosMoveAutre(
        actif="Cacao", call="LONG", mouvement_pct=3.0, direction_juste=True,
        raison_non_select="conviction sous le seuil (pas assez tranchée)", apprentissage="y",
    )]
    lignes = bj.compute_apprentissage_jour(perf, gros)
    txt = "\n".join(lignes)
    # Brief B : reformulé « Sortie tardive … PARCE QUE … » (le pourquoi causal).
    # Ici aucune news high tracée (events_path non injecté) → cause non identifiée.
    assert "Sortie tardive sur **S&P 500**" in txt
    assert "cause non identifiée (pas de catalyseur tracé)" in txt
    assert "Sélection trop prudente sur **Cacao**" in txt


def test_apprentissage_mauvaise_direction():
    gros = [bj.GrosMoveAutre(
        actif="Pétrole (Brent)", call="SHORT", mouvement_pct=4.0, direction_juste=False,
        raison_non_select="hors top 3", apprentissage="y",
    )]
    lignes = bj.compute_apprentissage_jour([], gros)
    assert any("Mauvaise direction sur **Pétrole (Brent)**" in li for li in lignes)


def test_apprentissage_trou_de_donnees_signale():
    perf = [bj.PerfTop3Ligne(
        actif="Cuivre", call="LONG", fav_12h=0.9, fav_18h=None, fav_cloture=0.4,
        pic_valeur=0.9, pic_heure="12h", points_manquants=["18h"], verdict="x", vendre_reco=None,
    )]
    lignes = bj.compute_apprentissage_jour(perf, [])
    assert any("Données intraday incomplètes" in li and "Cuivre" in li for li in lignes)


def test_apprentissage_rien_de_notable():
    lignes = bj.compute_apprentissage_jour([], [])
    assert len(lignes) == 1 and "Rien de notable" in lignes[0]


def test_section1_winrate_top1_top3_sur_max_gain():
    """SECTION 1 : win rate Top 1 / Top 3 sur le MAX GAIN du jour (> 1 %), perf =
    max gain (décision fondateur 24/06). Top 1 = conviction (|score|) max."""
    b = bj.BilanJour(date_j=date(2026, 6, 23),
                     now=datetime(2026, 6, 23, 22, 15, tzinfo=PARIS))
    b.perf_top3 = [
        # Or : conviction max (|score| 16.7) mais max gain 0.33% → Top 1 raté.
        bj.PerfTop3Ligne(actif="Or", call="SHORT", fav_12h=-0.10, fav_18h=-0.10,
                         fav_cloture=0.04, pic_valeur=0.33, pic_heure="18h",
                         points_manquants=[], verdict="x", vendre_reco=None,
                         raison_call="Taux réels", max_gain_pct=0.33,
                         score_conviction=16.7),
        # Cacao : max gain 1.40% > 1% → gagné.
        bj.PerfTop3Ligne(actif="Cacao", call="LONG", fav_12h=-0.52, fav_18h=-0.52,
                         fav_cloture=0.91, pic_valeur=0.91, pic_heure="clôture",
                         points_manquants=[], verdict="x", vendre_reco=None,
                         raison_call="Météo CI", max_gain_pct=1.40,
                         score_conviction=7.7),
        # EUR/USD : max gain 0.38% → raté.
        bj.PerfTop3Ligne(actif="EUR/USD", call="SHORT", fav_12h=0.35, fav_18h=0.35,
                         fav_cloture=0.38, pic_valeur=0.38, pic_heure="clôture",
                         points_manquants=[], verdict="x", vendre_reco=None,
                         raison_call="Écart taux", max_gain_pct=0.38,
                         score_conviction=16.0),
    ]
    md = "\n".join(bj._render_jour_selection(b))
    assert "| Actif | Call | 12h | 18h | 22h | Max gain jour | Gagné >1% | Raison |" in md
    # Top 1 = Or (conviction max) et il a RATÉ (max gain 0.33% < 1%).
    assert "**Top 1** (Or) : ❌ raté" in md
    # Top 3 : seul Cacao > 1% → 1/3.
    assert "**Top 3** : 1/3 = 33%" in md
    # Or affiché en tête (Top 1), max gain 0.33% → ❌.
    assert "| Or | SHORT | -0.10% | -0.10% | +0.04% | +0.33% | ❌ |" in md
    # Cacao gagné (1.40% > 1%).
    assert "| Cacao | LONG | -0.52% | -0.52% | +0.91% | +1.40% | ✅ |" in md


def test_win_rate_max_gain_exclut_non_mesurable():
    """Un pick sans max gain mesurable (high/low absent) est exclu (zéro invention)."""
    perf = [
        bj.PerfTop3Ligne(actif="A", call="LONG", fav_12h=None, fav_18h=None,
                         fav_cloture=None, pic_valeur=None, pic_heure=None,
                         points_manquants=[], verdict="x", vendre_reco=None,
                         max_gain_pct=2.0, score_conviction=5.0),
        bj.PerfTop3Ligne(actif="B", call="SHORT", fav_12h=None, fav_18h=None,
                         fav_cloture=None, pic_valeur=None, pic_heure=None,
                         points_manquants=[], verdict="x", vendre_reco=None,
                         max_gain_pct=None, score_conviction=9.0),
    ]
    wr = bj.win_rate_max_gain(perf)
    assert wr.n_top3 == 1 and wr.n_gagnants_top3 == 1  # B exclu (max gain None)
    assert wr.top1_actif == "A" and wr.top1_gagnant is True


def test_learnings_section_omise_si_rien_a_apprendre():
    """Section 4 OMISE quand il n'y a aucun learning (décision fondateur 24/06 :
    fini le cadre répété chaque jour). Top 1 gagné + aucun gros move → rien à dire."""
    b = bj.BilanJour(date_j=date(2026, 6, 23),
                     now=datetime(2026, 6, 23, 22, 15, tzinfo=PARIS))
    b.perf_top3 = [
        bj.PerfTop3Ligne(actif="Or", call="SHORT", fav_12h=None, fav_18h=None,
                         fav_cloture=1.5, pic_valeur=1.5, pic_heure="clôture",
                         points_manquants=[], verdict="x", vendre_reco=None,
                         max_gain_pct=1.5, score_conviction=10.0),
    ]
    b.gros_moves_autres = []
    assert bj._learnings_jour(b) == []          # rien à apprendre
    md = bj._render_markdown(b, {})
    assert "## 4. Les learnings du jour" not in md   # section omise


def test_learnings_top1_rate_emet_spec():
    """Top 1 (conviction max) qui rate le seuil → learning Spéculateur émis."""
    b = bj.BilanJour(date_j=date(2026, 6, 23),
                     now=datetime(2026, 6, 23, 22, 15, tzinfo=PARIS))
    b.perf_top3 = [
        bj.PerfTop3Ligne(actif="Or", call="SHORT", fav_12h=None, fav_18h=None,
                         fav_cloture=0.3, pic_valeur=0.3, pic_heure="clôture",
                         points_manquants=[], verdict="x", vendre_reco=None,
                         max_gain_pct=0.3, score_conviction=16.0),
    ]
    learnings = "\n".join(bj._learnings_jour(b))
    assert "Spéculateur" in learnings and "conviction n°1 (Or)" in learnings


def test_max_gain_du_jour_high_low():
    """max_gain_du_jour : LONG sur le high, SHORT sur le low ; 0 si jamais favorable."""
    assert mb.max_gain_du_jour(103.0, 99.0, 100.0, "LONG") == 3.0
    assert mb.max_gain_du_jour(101.0, 98.0, 100.0, "SHORT") == 2.0
    assert mb.max_gain_du_jour(100.0, 99.0, 100.0, "LONG") == 0.0  # n'est jamais monté
    assert mb.max_gain_du_jour(None, None, 100.0, "SHORT") is None  # donnée absente


# ===========================================================================
# Persistance intraday 12h/18h (run_suivi) — idempotente, zéro invention
# ===========================================================================

def _ligne(actif, call, fav_now, selection=True):
    return rs.SuiviLigne(
        actif=actif, call=call, ouverture=100.0, prix_courant=101.0, delta_pct=1.0,
        statut="✅ gagne", tendance="—", delta_vs_prec=None, suggestion="Hold",
        seuil_pct=0.3, vendre="Pas vendre", selection=selection, fav_now=fav_now,
        fav_prec=None,
    )


def test_tracking_save_load_12h_puis_18h(tmp_path):
    d = date(2026, 6, 22)
    now12 = datetime(2026, 6, 22, 12, 5, tzinfo=PARIS)
    now18 = datetime(2026, 6, 22, 18, 5, tzinfo=PARIS)
    rs.save_suivi_tracking(d, "12h", [_ligne("S&P 500", "LONG", 1.0)], now12, base_dir=tmp_path)
    rs.save_suivi_tracking(d, "18h", [_ligne("S&P 500", "LONG", 0.8)], now18, base_dir=tmp_path)
    data = rs.load_suivi_tracking(d, base_dir=tmp_path)
    assert data["12h"]["S&P 500"]["fav_pct"] == 1.0
    assert data["12h"]["S&P 500"]["heure"] == "12h05"
    assert data["18h"]["S&P 500"]["fav_pct"] == 0.8


def test_tracking_idempotent_ne_touche_pas_autre_creneau(tmp_path):
    # Rejouer le 12h ne doit PAS effacer le bloc 18h déjà écrit.
    d = date(2026, 6, 22)
    now12 = datetime(2026, 6, 22, 12, 5, tzinfo=PARIS)
    now18 = datetime(2026, 6, 22, 18, 5, tzinfo=PARIS)
    rs.save_suivi_tracking(d, "12h", [_ligne("Or", "SHORT", 0.5)], now12, base_dir=tmp_path)
    rs.save_suivi_tracking(d, "18h", [_ligne("Or", "SHORT", 0.6)], now18, base_dir=tmp_path)
    rs.save_suivi_tracking(d, "12h", [_ligne("Or", "SHORT", 0.55)], now12, base_dir=tmp_path)
    data = rs.load_suivi_tracking(d, base_dir=tmp_path)
    assert data["12h"]["Or"]["fav_pct"] == 0.55  # rejeu pris en compte
    assert data["18h"]["Or"]["fav_pct"] == 0.6   # 18h intact


def test_tracking_n_ecrit_que_la_selection_avec_fav(tmp_path):
    d = date(2026, 6, 22)
    now = datetime(2026, 6, 22, 12, 5, tzinfo=PARIS)
    lignes = [
        _ligne("S&P 500", "LONG", 1.0, selection=True),
        _ligne("Cacao", "LONG", 2.0, selection=False),   # non sélectionné → exclu
        _ligne("Or", "SHORT", None, selection=True),       # fav None → exclu
    ]
    rs.save_suivi_tracking(d, "12h", lignes, now, base_dir=tmp_path)
    data = rs.load_suivi_tracking(d, base_dir=tmp_path)
    assert list(data["12h"].keys()) == ["S&P 500"]


def test_tracking_rien_a_ecrire_n_efface_pas(tmp_path):
    # Aucun actif relevable → save retourne None et n'écrase pas un fichier existant.
    d = date(2026, 6, 22)
    now = datetime(2026, 6, 22, 12, 5, tzinfo=PARIS)
    rs.save_suivi_tracking(d, "12h", [_ligne("S&P 500", "LONG", 1.0)], now, base_dir=tmp_path)
    res = rs.save_suivi_tracking(d, "18h", [_ligne("X", "LONG", None, selection=True)], now, base_dir=tmp_path)
    assert res is None
    data = rs.load_suivi_tracking(d, base_dir=tmp_path)
    assert "12h" in data and "18h" not in data  # 12h préservé


def test_tracking_load_absent_renvoie_vide(tmp_path):
    assert rs.load_suivi_tracking(date(2026, 6, 22), base_dir=tmp_path) == {}


# ===========================================================================
# Reco « Vendre à 18h ? » recalculée depuis les relevés (source unique)
# ===========================================================================

def test_vendre_reco_18h_verrouille_gain_qui_reflue():
    # fav 12h=1.0, 18h=0.8 (le gain reflue) → Vendre (verrouiller près du pic).
    tracking = {
        "12h": {"S&P 500": {"call": "LONG", "fav_pct": 1.0}},
        "18h": {"S&P 500": {"call": "LONG", "fav_pct": 0.8}},
    }
    assert bj._vendre_reco_18h(tracking)["S&P 500"] == "Vendre"


def test_vendre_reco_18h_laisse_courir_gain_qui_grandit():
    tracking = {
        "12h": {"Or": {"call": "SHORT", "fav_pct": 0.3}},
        "18h": {"Or": {"call": "SHORT", "fav_pct": 0.6}},
    }
    assert bj._vendre_reco_18h(tracking)["Or"] == "Pas vendre"
