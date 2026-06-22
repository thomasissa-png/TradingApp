"""Moteur de sélection « top 3 du jour » (selection_jour) — logique implacable.

Tests purs (zéro réseau) : on construit des AssetDay/NewsItem à la main et on
vérifie chaque règle de la reco validée 10/10 (catalyseur, momentum, anti-faux-
négatif, anti-piège Café, ordre total déterministe, pas de remplissage).
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import selection_jour as sj  # noqa: E402

NOW = datetime(2026, 6, 22, 7, 0, tzinfo=timezone.utc)
ORDRE = ["or", "petrole", "sp500", "nasdaq", "cuivre", "cafe", "eurusd"]


def _news(direction="LONG", materiality="high", reliability="confirmed",
          nature="ponctuel", age_h=1.0, resume="news X", post_news_move=None):
    return sj.NewsItem(
        direction=direction, materiality=materiality, reliability=reliability,
        nature=nature, ingest_ts=NOW - timedelta(hours=age_h), resume=resume,
        post_news_move=post_news_move,
    )


def _asset(actif="Or", key="or", news=None, session_move=None, closes=None,
           fond_dir="", groupe=""):
    a = sj.AssetDay(
        actif=actif, fiche_key=key, news=news or [],
        session_move=session_move, closes=closes or [], fond_dir=fond_dir,
    )
    a.groupe = groupe
    return a


# ── Matérialité / palier ────────────────────────────────────────────────────
def test_materiality_high_confirmed_est_P1():
    assert sj._palier_news(sj._materiality_score(_news("LONG", "high", "confirmed"))) == sj.PALIER_P1


def test_materiality_medium_ou_reported_est_P2():
    assert sj._palier_news(sj._materiality_score(_news("LONG", "high", "reported"))) == sj.PALIER_P2
    assert sj._palier_news(sj._materiality_score(_news("LONG", "medium", "confirmed"))) == sj.PALIER_P2


def test_rumeur_ou_low_ou_deja_cote_ne_declenche_pas():
    assert sj._materiality_score(_news(reliability="rumor")) == 0
    assert sj._materiality_score(_news(materiality="low")) == 0
    assert sj._materiality_score(_news(nature="deja_cote")) == 0


# ── Anti-faux-négatif : grosse news fraîche, move pas encore fait → on PREND ──
def test_grosse_news_move_pas_fait_est_prise():
    # P1, fraîche, prix neutre (move pas commencé) → DOIT être sélectionnée.
    a = _asset(news=[_news("LONG", "high", "confirmed", post_news_move=0.0)], session_move=0.0)
    top = sj.select_top3([a], NOW, ORDRE)
    assert [p.actif for p in top] == ["Or"]
    assert top[0].porte == "news" and top[0].direction == "LONG"


def test_hesitation_legere_ne_veto_pas_un_P1():
    # P1 : un petit contre-mouvement (-0,2 %) sous le seuil 0,4 % ne veto PAS.
    a = _asset(news=[_news("LONG", "high", "confirmed")], session_move=-0.002)
    assert sj.select_top3([a], NOW, ORDRE)


def test_contradiction_soutenue_veto_proportionnel():
    # P1 : contre-mouvement -0,5 % (> 0,4 %) → veto. P2 aurait été veto dès 0,15 %.
    a = _asset(news=[_news("LONG", "high", "confirmed")], session_move=-0.005)
    assert sj.select_top3([a], NOW, ORDRE) == []


# ── Déjà coté / consommé ─────────────────────────────────────────────────────
def test_deja_cote_ecarte():
    # 80 % du move déjà fait ET ne prolonge plus (séance retombée à plat/contre).
    n = _news("LONG", "high", "confirmed", post_news_move=0.004)  # 0.4%/0.5% = 80%
    a = _asset(news=[n], session_move=-0.0005)  # ne prolonge plus
    assert sj.select_top3([a], NOW, ORDRE) == []


def test_move_avance_encore_meme_tres_consomme_est_garde():
    # 80 % consommé MAIS le prix prolonge encore (jambe 2) → on garde.
    n = _news("LONG", "high", "confirmed", post_news_move=0.004)
    a = _asset(news=[n], session_move=0.001)  # prolonge
    assert sj.select_top3([a], NOW, ORDRE)


def test_fraicheur_morte_au_dela_12h():
    a = _asset(news=[_news("LONG", "high", "confirmed", age_h=13)])
    assert sj.select_top3([a], NOW, ORDRE) == []


# ── Porte momentum + anti-piège Café ─────────────────────────────────────────
def test_momentum_accel_et_cassure_haussiere():
    closes = [10, 10, 10, 10, 10.1, 10.2, 10.3, 10.5]  # accélère + nouveau plus-haut
    a = _asset(actif="Cuivre", key="cuivre", closes=closes, session_move=0.002)
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].porte == "momentum" and top[0].direction == "LONG"


def test_cafe_long_tendance_mais_seance_contre_est_rejete():
    # Pas de news, momentum LONG faible MAIS séance -2 % → alignement violé → rejeté.
    closes = [10, 10, 10, 10, 10.1, 10.2, 10.3, 10.4]
    a = _asset(actif="Café", key="cafe", closes=closes, session_move=-0.02)
    assert sj.select_top3([a], NOW, ORDRE) == []


def test_momentum_rejete_si_fond_contredit():
    closes = [10, 10, 10, 10, 10.1, 10.2, 10.3, 10.5]  # momentum LONG
    a = _asset(key="cuivre", closes=closes, session_move=0.002, fond_dir="SHORT")
    assert sj.select_top3([a], NOW, ORDRE) == []


# ── Catalyseur > momentum ────────────────────────────────────────────────────
def test_catalyseur_prime_sur_momentum_oppose():
    closes = [10, 10, 10, 10, 10.1, 10.2, 10.3, 10.5]  # momentum LONG
    n = _news("SHORT", "high", "confirmed")             # news SHORT P1
    a = _asset(key="cuivre", news=[n], closes=closes, session_move=0.0)
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].porte == "news" and top[0].direction == "SHORT"


# ── Ordre total déterministe + dédup + pas de remplissage ────────────────────
def test_ordre_P1_avant_P2_avant_momentum():
    a1 = _asset("Pétrole", "petrole", news=[_news("LONG", "high", "reported")])  # P2 news
    a2 = _asset("Or", "or", news=[_news("LONG", "high", "confirmed")])           # P1 news
    a3 = _asset("Cuivre", "cuivre",
                closes=[10, 10, 10, 10, 10.1, 10.2, 10.3, 10.5], session_move=0.002)  # momentum
    top = sj.select_top3([a1, a2, a3], NOW, ORDRE)
    assert [p.actif for p in top] == ["Or", "Pétrole", "Cuivre"]


def test_max_3_et_dedup_par_groupe():
    base = dict(materiality="high", reliability="confirmed")
    assets = [
        _asset("Or", "or", news=[_news("SHORT", **base)], groupe="metaux"),
        _asset("Argent", "argent", news=[_news("SHORT", **base)], groupe="metaux"),
        _asset("Pétrole", "petrole", news=[_news("LONG", **base)], groupe="energie"),
        _asset("S&P 500", "sp500", news=[_news("LONG", **base)], groupe="actions"),
    ]
    top = sj.select_top3(assets, NOW, ["or", "argent", "petrole", "sp500"])
    # Or et Argent = même groupe → un seul gardé ; max 3.
    assert len(top) == 3
    assert sum(1 for p in top if p.fiche_key in ("or", "argent")) == 1


def test_pas_de_remplissage_zero_possible():
    # Rien d'éligible → top 3 vide (jamais de repli sur du faible).
    a = _asset(news=[_news(reliability="rumor")])
    assert sj.select_top3([a], NOW, ORDRE) == []


def test_meilleure_news_gardee_par_actif():
    # Deux news sur l'actif : la P1 confirmed l'emporte sur la P2 reported.
    a = _asset(news=[_news("LONG", "high", "reported"), _news("SHORT", "high", "confirmed")])
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].direction == "SHORT" and top[0].palier == sj.PALIER_P1
