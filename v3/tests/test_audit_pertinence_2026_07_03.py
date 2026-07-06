"""Audit de pertinence 03/07 — corrections de RENDU (zéro impact signal/mesure).

Tests MOCKÉS (aucun run du pipeline, `v3/data/` intact). Points couverts ici :
  - Point 1 : alerte catalyseur J0 (🔴/🟡) sous les paris quand le scope touche un
              pari (présente/absente), verbe accordé, heure « non confirmée ».
  - Point 4 : flips qualifiés — flip sous le seuil de conviction forte suffixé
              « (bruit : signal proche de zéro) » ET trié en fin de liste.
  - Point 5 : biblio raisons — entrée dédiée USD/JPY (dollar fort = LONG) au lieu
              de la phrase générique « matières premières » (sens inversé, absurde).

PUR RENDU : zéro LLM, zéro réseau.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 7, 3, 7, 0, tzinfo=timezone.utc)
SEUIL = 0.6


# ---------------------------------------------------------------------------
# Fabriques légères (ActifResult réel via score_actif, comme test_rendu 01/07).
# ---------------------------------------------------------------------------
def _fiche(poids=1):
    return {
        "actif": "X",
        "criteres": [
            {"id": i, "nom": f"Quant{i}", "cle_courante": f"quant{i}",
             "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0,
             "cap": 5.0, "signe": 1, "poids": poids,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}}
            for i in (1, 2, 3)
        ],
    }


def _vals(v):
    return {f"quant{i}": {"valeur": v, "source_track": "twelvedata"}
            for i in (1, 2, 3)}


def _make(nom, fiche_key, score24, conc=None):
    r = sa.score_actif(fiche_key, _fiche(), _vals(1.0))
    r.nom = nom
    r.fiche_key = fiche_key
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    r.coverage = 1.0
    if conc is None:
        conc = "LONG" if score24 >= 0 else "SHORT"
    r.conclusions = dict(r.conclusions); r.conclusions["24h"] = conc
    r.scores = dict(r.scores); r.scores["24h"] = score24
    return r


def _crit_dxy(ctr, signe):
    return sa.CritereResult(
        id="dxy",
        nom="Tendance du dollar (20 jours)",
        type_norm="zscore",
        valeur_brute=120.9,
        valeur_norm=0.98,
        poids=9.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: ctr for h in sa.HORIZONS},
        cle_courante="dxy_trend_20j",
    )


def _actif_dxy(nom, fiche_key, ctr, signe, conc, score):
    return sa.ActifResult(
        nom=nom,
        fiche_key=fiche_key,
        criteres=[_crit_dxy(ctr, signe)],
        scores={h: score for h in sa.HORIZONS},
        conclusions={h: conc for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: score for h in sa.HORIZONS},
        conclusions_pond={h: conc for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


# ===========================================================================
# Point 5 — biblio raisons : entrée dédiée USD/JPY
# ===========================================================================
def test_p5_resolver_usdjpy_override_dedie():
    """La cle partagée `dxy_trend_20j` résolue POUR usdjpy → entrée dédiée
    (dollar/yen), PAS la phrase générique « matières premières »."""
    ph = sa._raison_phrases_for_cle("dxy_trend_20j", "usdjpy")
    assert ph is not None
    assert ph["phrase_long"] == "dollar fort : le billet vert paie mieux que le yen"
    assert "yen" in ph["phrase_short"]
    # Sans fiche_key (ou autre actif) → phrase générique matières premières inchangée.
    gen = sa._raison_phrases_for_cle("dxy_trend_20j", "coton")
    assert "matières premières" in gen["phrase_short"]
    gen0 = sa._raison_phrases_for_cle("dxy_trend_20j")
    assert "matières premières" in gen0["phrase_short"]


def test_p5_usdjpy_long_dollar_fort_pas_matieres_premieres():
    """LONG USD/JPY porté par un dollar FORT (effet dxy > 0) : la raison de cellule
    dit « dollar fort … yen », JAMAIS « dollar en repli … matières premières »
    (double faux du 03/07 : sens inversé + « matières premières » sur une paire FX)."""
    r = _actif_dxy("USD/JPY", "usdjpy", ctr=+3.38, signe=1, conc="LONG", score=+3.38)
    phrase = sa.raison_cellule_phrase(r, "7j", NOW)
    assert phrase == "dollar fort : le billet vert paie mieux que le yen"
    assert "matières premières" not in phrase
    assert "repli" not in phrase


def test_p5_matiere_premiere_dollar_fort_short_inchangee():
    """Verrou non-régression : sur une matière première (signe inversé), un dollar
    fort pousse SHORT (effet < 0) → phrase générique « dollar fort : frein sur les
    matières premières » CONSERVÉE (l'override ne s'applique qu'à usdjpy)."""
    r = _actif_dxy("Coton", "coton", ctr=-0.59, signe=-1, conc="SHORT", score=-1.35)
    phrase = sa.raison_cellule_phrase(r, "7j", NOW)
    assert phrase == "dollar fort : frein sur les matières premières en USD"


# ===========================================================================
# Point 1 — alerte catalyseur J0 sous les paris
# ===========================================================================
def _nfp_event(actifs, impact="high", heure=None):
    return [{"nom": "Emploi US (NFP / rapport mensuel)",
             "actifs": actifs, "impact": impact, "heure": heure}]


def test_p1_alerte_j0_scope_touche_un_pari(monkeypatch):
    """Cas de réf. 03/07 : NFP J0 (scope or/argent/…) + pari Argent → ligne
    « 🔴 … : Argent traverse l'annonce. » (verbe singulier, heure non confirmée)."""
    monkeypatch.setattr(
        sa, "_catalyseurs_j0_scope",
        lambda now: _nfp_event(["or", "argent", "sp500", "nasdaq",
                                "cac40", "eurusd", "vix"]),
    )
    res = [_make("Argent", "argent", 8.76)]
    fiches = {"argent": {"seuils_reussite_pct": {"24h": 0.8}}}
    block = "\n".join(sa.build_paris_du_jour_block(
        res, NOW, seuil_conviction=SEUIL, fiches=fiches))
    assert "🔴 Emploi US (NFP / rapport mensuel) à heure non confirmée : " in block
    assert "Argent traverse l'annonce." in block
    assert "traversent" not in block  # un seul pari → singulier


def test_p1_alerte_j0_verbe_pluriel_et_heure(monkeypatch):
    """Deux paris dans le scope + heure connue → verbe pluriel et heure affichée."""
    monkeypatch.setattr(
        sa, "_catalyseurs_j0_scope",
        lambda now: _nfp_event(["argent", "or"], heure="14h30"),
    )
    res = [_make("Argent", "argent", 8.76), _make("Or", "or", 7.88)]
    fiches = {"argent": {"seuils_reussite_pct": {"24h": 0.8}},
              "or": {"seuils_reussite_pct": {"24h": 1.0}}}
    block = "\n".join(sa.build_paris_du_jour_block(
        res, NOW, seuil_conviction=SEUIL, fiches=fiches))
    assert "à 14h30 :" in block
    assert "traversent l'annonce." in block


def test_p1_pas_d_alerte_si_scope_hors_paris(monkeypatch):
    """Event J0 dont le scope ne touche AUCUN pari → aucune ligne (zéro bruit)."""
    monkeypatch.setattr(
        sa, "_catalyseurs_j0_scope", lambda now: _nfp_event(["petrole"]))
    res = [_make("Argent", "argent", 8.76)]
    fiches = {"argent": {"seuils_reussite_pct": {"24h": 0.8}}}
    block = "\n".join(sa.build_paris_du_jour_block(
        res, NOW, seuil_conviction=SEUIL, fiches=fiches))
    assert "traverse" not in block


def test_p1_pas_d_alerte_si_aucun_event_j0(monkeypatch):
    monkeypatch.setattr(sa, "_catalyseurs_j0_scope", lambda now: [])
    res = [_make("Argent", "argent", 8.76)]
    fiches = {"argent": {"seuils_reussite_pct": {"24h": 0.8}}}
    block = "\n".join(sa.build_paris_du_jour_block(
        res, NOW, seuil_conviction=SEUIL, fiches=fiches))
    assert "traverse" not in block


# ===========================================================================
# Point 4 — flips qualifiés (bruit suffixé + trié en fin)
# ===========================================================================
def test_p4_flip_bruit_suffixe_et_trie_en_fin(monkeypatch):
    """Seuil de conviction forte fixé à 2.0. Flip franc (score 9.0) AVANT le flip
    de bruit (score 0.5) qui porte « (bruit : signal proche de zéro) »."""
    monkeypatch.setattr(sa, "_raison_force_seuil", lambda: 2.0)
    franc = _make("Cafe", "cafe", 9.0, conc="LONG")
    bruit = _make("Ble", "ble", 0.5, conc="LONG")
    res = [bruit, franc]  # ordre d'entrée : bruit d'abord → le tri doit l'envoyer en fin
    veille = {"cafe": {"24h": "SHORT"}, "ble": {"24h": "SHORT"}}
    bulletin = sa.render_bulletin(res, veille, NOW, "07h", "ok")
    lignes = [l for l in bulletin.splitlines() if l.startswith("- Cafe [24h]")
              or l.startswith("- Ble [24h]")]
    assert len(lignes) == 2
    # Franc en premier, bruit en dernier.
    assert lignes[0].startswith("- Cafe [24h]")
    assert lignes[1].startswith("- Ble [24h]")
    assert "(bruit : signal proche de zéro)" in lignes[1]
    assert "(bruit : signal proche de zéro)" not in lignes[0]


def test_p4_flip_franc_pas_de_suffixe_bruit(monkeypatch):
    """Un flip dont la nouvelle note dépasse le seuil fort n'est jamais « bruit »."""
    monkeypatch.setattr(sa, "_raison_force_seuil", lambda: 2.0)
    res = [_make("Cafe", "cafe", 9.0, conc="LONG")]
    veille = {"cafe": {"24h": "SHORT"}}
    bulletin = sa.render_bulletin(res, veille, NOW, "07h", "ok")
    assert "Cafe [24h] : SHORT → LONG" in bulletin
    assert "bruit : signal proche de zéro" not in bulletin
