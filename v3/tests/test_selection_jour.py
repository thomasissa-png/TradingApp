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


# ── R2 : garde-fou fond sur la porte news ────────────────────────────────────
def test_R2_catalyseur_P2_contre_fond_est_rejete():
    # News LONG P2 (medium×confirmed) vs fond SHORT → catalyseur faible ne prime pas.
    n = _news("LONG", "medium", "confirmed", age_h=1.0)
    a = _asset(news=[n], fond_dir="SHORT")
    assert sj.select_top3([a], NOW, ORDRE) == []


def test_R2_catalyseur_P1_frais_contre_fond_est_retenu():
    # News LONG P1 (high×confirmed) ET fraîche (1h) vs fond SHORT → la grosse news
    # casse l'habitude et prime.
    n = _news("LONG", "high", "confirmed", age_h=1.0)
    a = _asset(news=[n], fond_dir="SHORT")
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].porte == "news" and top[0].direction == "LONG"


def test_R2_catalyseur_P1_moins_frais_contre_fond_est_rejete():
    # P1 mais age 8h (> FRESH_OK_H=6h) à contre-fond → ne casse plus l'habitude → rejet.
    n = _news("LONG", "high", "confirmed", age_h=8.0)
    a = _asset(news=[n], fond_dir="SHORT")
    assert sj.select_top3([a], NOW, ORDRE) == []


def test_R2_catalyseur_P2_sans_fond_oppose_est_retenu():
    # P2 LONG sans fond opposé (fond vide) → retenu (le garde-fou R2 ne s'applique pas).
    n = _news("LONG", "medium", "confirmed", age_h=1.0)
    a = _asset(news=[n], fond_dir="")
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].porte == "news" and top[0].direction == "LONG"


def test_R2_catalyseur_P2_fond_concordant_est_retenu():
    # P2 LONG avec fond LONG (concordant) → retenu.
    n = _news("LONG", "medium", "confirmed", age_h=1.0)
    a = _asset(news=[n], fond_dir="LONG")
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].direction == "LONG"


# ── R3 : alignement sur le net des news fraîches ─────────────────────────────
def test_R3_news_minoritaire_contre_net_frais_est_rejetee():
    # Net frais nettement SHORT (deux SHORT P1) ; une news LONG minoritaire P1 ne
    # doit PAS commander → seule la SHORT est retenue.
    a = _asset(news=[
        _news("SHORT", "high", "confirmed", age_h=1.0),
        _news("SHORT", "high", "confirmed", age_h=2.0),
        _news("LONG", "high", "confirmed", age_h=1.0),
    ])
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].direction == "SHORT"


def test_R3_net_nul_ne_bloque_pas():
    # Vrai 50/50 (un LONG P1 et un SHORT P1, scores égaux) → net == 0 → R3 ne bloque
    # pas ; la news la mieux classée (départage interne) est retenue.
    a = _asset(news=[
        _news("LONG", "high", "confirmed", age_h=1.0),
        _news("SHORT", "high", "confirmed", age_h=2.0),
    ])
    top = sj.select_top3([a], NOW, ORDRE)
    assert top and top[0].porte == "news"


# ── Cas réel Or du 23/06 : aucun pari Or LONG ne doit sortir ──────────────────
def test_cas_or_23_06_aucun_pari_long():
    # Reproduction : fond SHORT fort ; news catalyseur Or LONG « avril » (structurel,
    # high/confirmed = P1) mais VIEILLE (1ʳᵉ apparition ~20j → R1 la date à 20j) ;
    # net des news FRAÎCHES baissier (Fed + paix dominent en SHORT). Triple garde-fou.
    age_avril_h = 20 * 24.0  # 1ʳᵉ apparition il y a ~20 jours (R1 applique ce min)
    news = [
        # Catalyseur récurrent « avril » : haussier mais vieux.
        _news("LONG", "high", "confirmed", nature="structurel",
              age_h=age_avril_h, resume="Banques centrales achats nets d'or en avril"),
        # Contexte frais baissier qui domine (Fed hawkish + désescalade géopolitique).
        _news("SHORT", "high", "confirmed", age_h=2.0, resume="Fed hawkish"),
        _news("SHORT", "medium", "confirmed", age_h=3.0, resume="désescalade"),
    ]
    a = _asset(actif="Or", key="or", news=news, fond_dir="SHORT")
    top = sj.select_top3([a], NOW, ORDRE)
    # Aucun pari Or LONG. (Le SHORT, lui, reste cohérent fond + net frais.)
    assert all(not (p.fiche_key == "or" and p.direction == "LONG") for p in top)


def test_cas_or_23_06_r1_seule_tue_le_long():
    # Même news « avril » SEULE (sans contexte) : R1 (1ʳᵉ apparition 20j > 12h) suffit
    # à la tuer, indépendamment de R2/R3.
    n = _news("LONG", "high", "confirmed", nature="structurel", age_h=20 * 24.0)
    a = _asset(actif="Or", key="or", news=[n], fond_dir="")
    assert sj.select_top3([a], NOW, ORDRE) == []
