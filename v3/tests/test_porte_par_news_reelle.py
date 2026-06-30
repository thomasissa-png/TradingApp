"""Transparence du porteur NET news (décision fondateur 23/06).

CONTEXTE DU BUG : quand une cellule est portée par le critère qui PORTE le NET
news (synthèse DeepSeek du corpus, source_track ia_synthese), le rendu affichait
le libellé OPAQUE « Synthèse news (net, IA) » — sans dire QUELLE news ni POURQUOI
(ex. « Cacao LONG — Synthèse news (net, IA) »). Aucun learning possible.

CORRECTIF (PUR RENDU) : partout où une ligne est portée par le NET news, on
remplace ce libellé par le SENS net + le TITRE réel de la news dominante de
l'actif (ex. « news net haussière : El Niño menace les récoltes du cacao »).
Source UNIQUE : briefing.filter_recent_impactful (le même feed que « Top
actualités à impact »). Zéro invention : sans titre exploitable → « news net
haussière/baissière » ; sans sens → libellé d'origine (dégradation sûre).

Ce que ce fichier prouve :
  (1) cellule portée par le net news haussier + news « El Niño… » dans le corpus
      → la raison contient le sens (« haussière ») ET le titre, PAS le libellé
      opaque ;
  (2) fallback sans titre exploitable → « news net haussière/baissière » ;
  (3) cellule portée par un critère NON-news (taux réels US) → INCHANGÉE.

PUR RENDU : zéro LLM, zéro réseau (events-log monkeypatché).
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import briefing as B  # noqa: E402
import scoring_analyste as sa  # noqa: E402


NOW = datetime(2026, 6, 23, 7, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helpers de construction (alignés sur test_raison_cellule)
# ---------------------------------------------------------------------------

def _crit(
    nom: str,
    cle: str,
    contribs: Dict[str, float],
    *,
    signe: int = 1,
    source_track: str = "",
) -> sa.CritereResult:
    c = sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="lineaire",
        valeur_brute=1.0,
        valeur_norm=1.0,
        poids=5.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions=dict(contribs),
        cle_courante=cle,
    )
    c.source_track = source_track
    return c


def _actif(
    nom: str,
    criteres: List[sa.CritereResult],
    scores: Dict[str, float],
    conclusions: Dict[str, str],
) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=nom.lower(),
        criteres=criteres,
        scores=dict(scores),
        conclusions=dict(conclusions),
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


def _patch_events(monkeypatch, events: List[Dict[str, str]]) -> None:
    """Monkeypatch la SEULE source de news (briefing.parse_events) + vide le cache.

    On ne réécrit aucun parseur : on injecte des events bruts que le pipeline
    réel (filter_recent_impactful → _primary_actif_from_event → _direction_arrow_for)
    consomme tel quel. Garantit qu'on teste la VRAIE chaîne de vérité news.
    """
    monkeypatch.setattr(B, "parse_events", lambda _p: list(events))
    sa._DOMINANT_NEWS_CACHE.clear()


def _ev(date_s: str, cat: str, trigger: str, impacts: str, mat: str) -> Dict[str, str]:
    return {
        "date": date_s,
        "cat": cat,
        "trigger": trigger,
        "impacts": impacts,
        "materiality": mat,
        "cours": "",
    }


# ---------------------------------------------------------------------------
# (1) Cas Cacao : net news haussier + titre réel « El Niño… »
# ---------------------------------------------------------------------------

def test_cacao_net_news_haussier_affiche_titre_reel(monkeypatch):
    """Cacao 24h LONG porté par le NET news (ia_synthese). Corpus : news high
    haussière « El Niño menace les récoltes du cacao » → la raison du pari du
    jour contient le sens (« haussière ») ET le titre, PAS le libellé opaque."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity",
            "El Niño menace les récoltes du cacao en Afrique de l'Ouest",
            "COCOA:LONG:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Maladies cabosses", "maladies_cabosses_cacao", {h: +6.0},
              source_track="ia_synthese"),
    ]
    r = _actif("Cacao", crit, {h: +6.0}, {h: "LONG"})

    picks = sa.select_paris_du_jour([r], NOW)
    assert len(picks) == 1
    raison = picks[0]["raison"]
    assert sa.SYNTHESE_NET_LABEL not in raison
    assert "haussière" in raison
    assert "El Niño menace les récoltes du cacao" in raison
    assert raison.startswith("news net haussière :")


def test_cacao_porte_par_dans_a_jouer(monkeypatch):
    """Même cas, colonne « Porté par » du bloc « À jouer aujourd'hui (24h) » :
    la cellule contient le titre réel, pas « Synthèse news (net, IA) »."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity",
            "El Niño menace les récoltes du cacao en Afrique de l'Ouest",
            "COCOA:LONG:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Maladies cabosses", "maladies_cabosses_cacao", {h: +6.0},
              source_track="ia_synthese"),
    ]
    r = _actif("Cacao", crit, {h: +6.0}, {h: "LONG"})

    lines = sa.build_a_jouer_block([r], NOW)
    joined = "\n".join(lines)
    assert sa.SYNTHESE_NET_LABEL not in joined
    assert "news net haussière : El Niño menace les récoltes du cacao" in joined


def test_titre_long_tronque_proprement(monkeypatch):
    """Un titre > 70 car est tronqué à la frontière de mot avec « … »."""
    long_titre = (
        "El Niño menace très sérieusement les récoltes du cacao en Afrique "
        "de l'Ouest et fait flamber les cours mondiaux du chocolat"
    )
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity", long_titre, "COCOA:LONG:high", "high"),
    ])
    sens, titre = sa._dominant_news_for_actif(NOW).get("Cacao", ("", ""))
    assert sens == "haussière"
    assert titre.endswith("…")
    assert len(titre) <= sa.DOMINANT_NEWS_TITLE_MAX_LEN + 1
    assert titre.startswith("El Niño menace")


# ---------------------------------------------------------------------------
# (2) Fallback sans titre exploitable → « news net haussière/baissière »
# ---------------------------------------------------------------------------

def test_fallback_sans_titre_sens_haussier(monkeypatch):
    """Titre vide MAIS contribution news +6 → le sens vient de la CONTRIBUTION
    (haussière), pas d'un titre ni du call (fix 30/06). Suffixe « pas de titre
    représentatif » plutôt que d'afficher un titre vide ou inventer le sens."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity", "   ", "COCOA:LONG:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Maladies cabosses", "maladies_cabosses_cacao", {h: +6.0},
              source_track="ia_synthese"),
    ]
    r = _actif("Cacao", crit, {h: +6.0}, {h: "LONG"})
    raison = sa.select_paris_du_jour([r], NOW)[0]["raison"]
    assert "news net haussière" in raison
    assert sa.SYNTHESE_NET_LABEL not in raison


def test_cacao_3006_titre_baissier_isole_ne_contredit_pas_le_net(monkeypatch):
    """RÉGRESSION (fondateur 30/06) : cacao LONG, news NETTE haussière (+3.2), mais le
    titre dominant du corpus est BAISSIER (« offre abondante »). Le label doit dire
    « haussière » (le NET, source de vérité) et NE PAS afficher le titre baissier
    (sinon « news net baissière » sur un LONG → l'incohérence signalée)."""
    _patch_events(monkeypatch, [
        _ev("2026-06-29", "commodity",
            "Offre mondiale de cacao plus abondante, pression sur les prix",
            "COCOA:SHORT:high", "medium"),
    ])
    h = "24h"
    crit = [
        _crit("Maladies cabosses", "maladies_cabosses_cacao", {h: +3.2},
              source_track="ia_synthese"),
    ]
    r = _actif("Cacao", crit, {h: +3.2}, {h: "LONG"})
    raison = sa.select_paris_du_jour([r], NOW)[0]["raison"]
    assert "haussière" in raison                       # le NET haussier mène
    assert "baissière" not in raison                   # plus jamais l'inverse
    assert "abondante" not in raison                   # le titre baissier n'est PAS cité


def test_fallback_sens_baissier(monkeypatch):
    """Direction IA SHORT → « news net baissière » (avec titre si présent)."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity",
            "Demande chinoise de cuivre en net repli", "COPPER:SHORT:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Mining strikes", "mining_strikes_chili_perou", {h: -6.0},
              signe=-1, source_track="ia_synthese"),
    ]
    r = _actif("Cuivre", crit, {h: -6.0}, {h: "SHORT"})
    raison = sa.select_paris_du_jour([r], NOW)[0]["raison"]
    assert "news net baissière" in raison
    assert "Demande chinoise de cuivre en net repli" in raison


def test_fallback_corpus_vide_sens_vient_de_la_contribution(monkeypatch):
    """Corpus de news vide (aucun titre) MAIS la contribution news vaut +6 : le sens
    vient de la CONTRIBUTION réelle (haussière), il n'est PAS perdu (fix 30/06). On
    n'affiche plus le jargon « Synthèse news (net, IA) » ni un sens inventé du call."""
    _patch_events(monkeypatch, [])  # corpus vide
    h = "24h"
    crit = [
        _crit("Maladies cabosses", "maladies_cabosses_cacao", {h: +6.0},
              source_track="ia_synthese"),
    ]
    r = _actif("Cacao", crit, {h: +6.0}, {h: "LONG"})
    raison = sa.select_paris_du_jour([r], NOW)[0]["raison"]
    assert "news net haussière" in raison
    assert sa.SYNTHESE_NET_LABEL not in raison


def test_news_neutre_ne_porte_pas_de_sens(monkeypatch):
    """Une news à direction NEUTRAL ne fournit pas de sens net exploitable →
    pas dans la carte dominante → libellé d'origine conservé."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity", "Marché du cacao stable", "COCOA:NEUTRAL:high", "high"),
    ])
    assert "Cacao" not in sa._dominant_news_for_actif(NOW)


# ---------------------------------------------------------------------------
# (3) Critère NON-news (taux réels US) → libellé INCHANGÉ
# ---------------------------------------------------------------------------

def test_critere_quant_non_news_inchange(monkeypatch):
    """Or 24h SHORT porté par « Taux réels US » (critère quant, pas de source_track
    net news). Même avec une news Or dans le corpus, le libellé du driver reste
    le critère quant : on n'enrichit QUE le porteur net news."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "macro",
            "Bond du dollar après la Fed", "GOLD:SHORT:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.0}, signe=-1),
    ]
    r = _actif("Or", crit, {h: -6.0}, {h: "SHORT"})

    raison = sa.select_paris_du_jour([r], NOW)[0]["raison"]
    assert "Taux réels US" in raison
    assert "news net" not in raison
    assert sa.SYNTHESE_NET_LABEL not in raison


def test_a_jouer_critere_quant_inchange(monkeypatch):
    """Même non-régression sur la colonne « Porté par » : un critère quant garde
    son format legacy (val / sens / contribue)."""
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "macro",
            "Bond du dollar après la Fed", "GOLD:SHORT:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.0}, signe=-1),
    ]
    r = _actif("Or", crit, {h: -6.0}, {h: "SHORT"})
    joined = "\n".join(sa.build_a_jouer_block([r], NOW))
    assert "Taux réels US" in joined
    assert "contribue" in joined
    assert "news net" not in joined


# ---------------------------------------------------------------------------
# Verrou PUR RENDU : aucune mutation du scoring / conclusion / source_track
# ---------------------------------------------------------------------------

def test_pur_rendu_aucune_mutation(monkeypatch):
    _patch_events(monkeypatch, [
        _ev("2026-06-22", "commodity",
            "El Niño menace les récoltes du cacao", "COCOA:LONG:high", "high"),
    ])
    h = "24h"
    crit = [
        _crit("Maladies cabosses", "maladies_cabosses_cacao", {h: +6.0},
              source_track="ia_synthese"),
    ]
    r = _actif("Cacao", crit, {h: +6.0}, {h: "LONG"})
    score_avant = dict(r.scores)
    conc_avant = dict(r.conclusions)
    track_avant = r.criteres[0].source_track
    cle_avant = r.criteres[0].cle_courante
    _ = sa.select_paris_du_jour([r], NOW)
    _ = sa.build_a_jouer_block([r], NOW)
    assert r.scores == score_avant
    assert r.conclusions == conc_avant
    assert r.criteres[0].source_track == track_avant
    assert r.criteres[0].cle_courante == cle_avant
