"""Sonde 3 « KO virtuel » (panel 11/07) + lecture hebdo des 3 sondes SHADOW.

WIN RATE ONLY : on ne teste QUE des taux, des ordres temporels et des comptes —
aucun euro. Zéro invention : série insuffisante → None, champ shadow absent →
sonde « en attente ».
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

import mesure_bilan as mb  # noqa: E402
import bilan_jour as bj  # noqa: E402
import run_weekly as rw  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


def _bars(prices):
    """Série 1h ordonnée (dt croissants) à partir d'une liste de close."""
    base = datetime(2026, 6, 10, 8, 0, tzinfo=PARIS)
    return [(base.replace(hour=8 + i), p) for i, p in enumerate(prices)]


# ---------------------------------------------------------------------------
# ko_virtuel_du_jour : ordre temporel adverse -3 % vs favorable +1 %
# ---------------------------------------------------------------------------

def test_ko_atteint_avant_cible_long():
    # LONG, réf 100 : -3 % (97) touché AVANT +1 % (101) → KO virtuel True.
    bars = _bars([100.0, 96.5, 102.0])
    assert mb.ko_virtuel_du_jour(bars, 100.0, "LONG") is True


def test_ko_atteint_avant_cible_short():
    # SHORT, réf 100 : adverse = hausse. 103.5 (+3.5 % adverse) avant baisse à 99.
    bars = _bars([100.0, 103.5, 98.0])
    assert mb.ko_virtuel_du_jour(bars, 100.0, "SHORT") is True


def test_cible_atteinte_avant_ko():
    # LONG : +1 % (101) touché AVANT -3 % → pas de KO (False).
    bars = _bars([100.0, 101.5, 96.0])
    assert mb.ko_virtuel_du_jour(bars, 100.0, "LONG") is False


def test_ko_jamais_touche():
    # LONG : ni -3 % ni rien d'adverse fort → pas de KO (False).
    bars = _bars([100.0, 100.5, 99.0, 98.5])  # -1.5 % max adverse, jamais -3 %
    assert mb.ko_virtuel_du_jour(bars, 100.0, "LONG") is False


def test_serie_insuffisante_renvoie_none():
    assert mb.ko_virtuel_du_jour([], 100.0, "LONG") is None
    assert mb.ko_virtuel_du_jour(_bars([100.0]), None, "LONG") is None
    assert mb.ko_virtuel_du_jour(_bars([100.0]), 100.0, "NEUTRAL") is None


def test_constante_seuil():
    assert mb.KO_VIRTUEL_PCT == 3.0
    assert mb.KO_CIBLE_PCT == 1.0


# ---------------------------------------------------------------------------
# compute_perf_top3 : propage ko_virtuel (mesure) + pari_mur (decision-log)
# ---------------------------------------------------------------------------

def _mesure(actif, call, delta, ko):
    return SimpleNamespace(
        cell=SimpleNamespace(actif_name=actif, conclusion=call),
        horizon="24h", delta_pct=delta, max_gain_pct=None, ko_virtuel=ko,
    )


def test_compute_perf_top3_porte_ko_et_mur():
    measures = [_mesure("Or", "SHORT", 0.5, True)]
    sel = {("Or", "24h"): True}
    conv = {("Or", "24h"): {"p2_M5_nature_composition": {"deja_cote": 1}}}
    perf = bj.compute_perf_top3(measures, sel, tracking={}, date_j=None,
                                conviction_records=conv)
    assert len(perf) == 1
    assert perf[0].ko_virtuel is True
    assert perf[0].pari_mur is True


def test_compute_perf_top3_mur_false_si_pas_deja_cote():
    measures = [_mesure("Blé", "LONG", 0.2, False)]
    sel = {("Blé", "24h"): True}
    conv = {("Blé", "24h"): {"p2_M5_nature_composition": {"structurel": 1}}}
    perf = bj.compute_perf_top3(measures, sel, tracking={}, date_j=None,
                                conviction_records=conv)
    assert perf[0].ko_virtuel is False
    assert perf[0].pari_mur is False


# ---------------------------------------------------------------------------
# Persistance sortie-timing-log : ko_virtuel + pari_mur (append au record)
# ---------------------------------------------------------------------------

def test_persist_sortie_timing_ecrit_ko_et_mur(tmp_path):
    p = tmp_path / "sortie-timing-log.jsonl"
    ligne = bj.PerfTop3Ligne(
        actif="Or", call="SHORT", fav_12h=None, fav_18h=None, fav_cloture=-0.2,
        pic_valeur=None, pic_heure=None, points_manquants=[], verdict="",
        vendre_reco=None, ko_virtuel=True, pari_mur=True,
    )
    bj.persist_sortie_timing(date(2026, 6, 10), [ligne], path=p)
    rec = json.loads(p.read_text(encoding="utf-8").strip())
    assert rec["ko_virtuel"] is True
    assert rec["pari_mur"] is True


# ---------------------------------------------------------------------------
# Annexe bilan du soir : une ligne 🧨 par pari KO virtuel
# ---------------------------------------------------------------------------

def test_annexe_affiche_ligne_ko_virtuel():
    p_ko = bj.PerfTop3Ligne(
        actif="Or", call="SHORT", fav_12h=None, fav_18h=None, fav_cloture=-0.2,
        pic_valeur=None, pic_heure=None, points_manquants=[], verdict="",
        vendre_reco=None, ko_virtuel=True, pari_mur=True,
    )
    p_sain = bj.PerfTop3Ligne(
        actif="Blé", call="LONG", fav_12h=None, fav_18h=None, fav_cloture=0.5,
        pic_valeur=0.5, pic_heure="clôture", points_manquants=[], verdict="",
        vendre_reco=None, ko_virtuel=False, pari_mur=False,
    )
    bilan = SimpleNamespace(perf_top3=[p_ko, p_sain])
    lignes = bj._render_intraday_table(bilan)
    txt = "\n".join(lignes)
    assert "🧨 KO virtuel : le pari Or SHORT a touché -3 % avant +1 %" in txt
    assert "⌛ (pari déjà coté)" in txt
    assert "le pari Blé" not in txt  # pari sain → aucune ligne KO


# ---------------------------------------------------------------------------
# Sonde 3 hebdo : _sonde_ko_virtuel (segmentation ⌛ mûrs vs frais)
# ---------------------------------------------------------------------------

NOW = datetime(2026, 6, 12, 22, 30, tzinfo=PARIS)  # jeu. de la semaine ISO 08→14/06


def _write_sortie_log(tmp_path, rows):
    p = tmp_path / "sortie-timing-log.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                 encoding="utf-8")
    return p


def test_sonde_ko_virtuel_segmente_mur_vs_frais(tmp_path):
    rows = [
        {"date": "2026-06-10", "actif": "Or", "ko_virtuel": True, "pari_mur": True},
        {"date": "2026-06-11", "actif": "Blé", "ko_virtuel": False, "pari_mur": True},
        {"date": "2026-06-11", "actif": "Cacao", "ko_virtuel": True, "pari_mur": False},
        {"date": "2026-06-12", "actif": "Café", "ko_virtuel": None, "pari_mur": False},
        {"date": "2026-05-30", "actif": "Sucre", "ko_virtuel": True, "pari_mur": False},
    ]
    p = _write_sortie_log(tmp_path, rows)
    ko = rw._sonde_ko_virtuel(NOW, path=p)
    assert ko.n_mesurable == 3       # None exclu, hors-semaine exclu
    assert ko.n_ko == 2
    assert ko.n_mur_mesurable == 2 and ko.n_mur_ko == 1
    assert ko.n_frais_mesurable == 1 and ko.n_frais_ko == 1


def test_sonde_ko_virtuel_vide(tmp_path):
    ko = rw._sonde_ko_virtuel(NOW, path=tmp_path / "absent.jsonl")
    assert ko.n_mesurable == 0


# ---------------------------------------------------------------------------
# Sondes 1 & 2 hebdo : _sondes_flip_catalyseur (join measures × decision-log)
# ---------------------------------------------------------------------------

def _write_measures(tmp_path, rows):
    p = tmp_path / "measures-log.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                 encoding="utf-8")
    return p


def _write_decision(dldir, bdate, records):
    dldir.mkdir(parents=True, exist_ok=True)
    p = dldir / f"{bdate}-0700.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                 encoding="utf-8")


def test_sondes_flip_catalyseur(tmp_path):
    measures = _write_measures(tmp_path, [
        {"bulletin_date": "2026-06-10", "actif": "Or", "horizon": "24h",
         "conclusion": "SHORT", "outcome": "VRAI"},
        {"bulletin_date": "2026-06-11", "actif": "Blé", "horizon": "24h",
         "conclusion": "LONG", "outcome": "FAUSSE"},
    ])
    dldir = tmp_path / "decision-log"
    _write_decision(dldir, "2026-06-10", [
        {"bulletin_date": "2026-06-10", "actif": "Or", "horizon": "24h",
         "shadow_flip_j0": True, "shadow_flip_conf": True},
    ])
    _write_decision(dldir, "2026-06-11", [
        {"bulletin_date": "2026-06-11", "actif": "Blé", "horizon": "24h",
         "shadow_cat_epuise": True, "shadow_sens_fond": "SHORT"},  # fond ≠ call LONG
    ])
    flip, cat = rw._sondes_flip_catalyseur(NOW, measures_log=measures,
                                           decision_log_dir=dldir)
    assert flip.n_flips_j0 == 1 and flip.n_vrai_j0 == 1
    assert flip.n_flips_conf == 1 and flip.n_vrai_conf == 1
    assert cat.n_divergence == 1
    # call live LONG FAUSSE → le fond (SHORT) avait raison.
    assert cat.n_fond_raison == 1 and cat.n_live_raison == 0


def test_sondes_flip_catalyseur_vide(tmp_path):
    flip, cat = rw._sondes_flip_catalyseur(
        NOW, measures_log=tmp_path / "absent.jsonl", decision_log_dir=tmp_path / "dl")
    assert flip.n_flips_j0 == 0 and cat.n_divergence == 0


# ---------------------------------------------------------------------------
# Rendu hebdo : les 3 lignes (d)(e)(f) — données mockées + cas vide « en attente »
# ---------------------------------------------------------------------------

def _bilan_min():
    return rw.BilanSemaine(iso="2026-W24", lundi=date(2026, 6, 8),
                           dimanche=date(2026, 6, 14), now=NOW, picks=[])


def test_render_3_lignes_avec_donnees(monkeypatch, tmp_path):
    monkeypatch.setattr(rw, "_sondes_flip_catalyseur", lambda now: (
        rw.SondeConfirmationFlip(n_flips_j0=4, n_vrai_j0=3, n_flips_conf=2, n_vrai_conf=2),
        rw.SondeCatalyseurEpuise(n_divergence=3, n_live_raison=1, n_fond_raison=2),
    ))
    monkeypatch.setattr(rw, "_sonde_ko_virtuel", lambda now: rw.SondeKoVirtuel(
        n_mesurable=5, n_ko=2, n_mur_mesurable=2, n_mur_ko=2,
        n_frais_mesurable=3, n_frais_ko=0))
    L: list = []
    rw._render_mesures_shadow(_bilan_min(), L, selection_wr_path=tmp_path / "swr.jsonl")
    txt = "\n".join(L)
    assert "(d) Confirmation post-flip** : flips J0 3/4 VRAI vs flips confirmés 2/2" in txt
    assert "En chauffe (N=4/15 flips)" in txt
    assert "(e) Catalyseur épuisé** : 3 divergence(s)" in txt
    assert "le call live avait raison 1, le sens de fond 2" in txt
    assert "(f) KO virtuel** (risque « tendance mûre ») : 2/5 pari(s) ont touché -3 % avant +1 % (40%)" in txt
    assert "⌛ mûrs 2/2, frais 0/3" in txt
    assert "En chauffe (N=5/15)" in txt


def test_render_3_lignes_vides_en_attente(monkeypatch, tmp_path):
    monkeypatch.setattr(rw, "_sondes_flip_catalyseur", lambda now: (
        rw.SondeConfirmationFlip(), rw.SondeCatalyseurEpuise()))
    monkeypatch.setattr(rw, "_sonde_ko_virtuel", lambda now: rw.SondeKoVirtuel())
    L: list = []
    rw._render_mesures_shadow(_bilan_min(), L, selection_wr_path=tmp_path / "swr.jsonl")
    txt = "\n".join(L)
    assert "(d) Confirmation post-flip** : aucun flip tracé cette semaine" in txt
    assert "(e) Catalyseur épuisé** : aucune divergence" in txt
    assert "(f) KO virtuel** : aucun pari mesurable cette semaine" in txt
    assert "sonde en attente" in txt
