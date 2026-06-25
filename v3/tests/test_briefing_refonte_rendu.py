"""Tests REFONTE RENDU du briefing 7h (P1/P2/P3/P4/P5/P6/P7/P8/P9).

PUR RENDU — ces tests vérifient l'AFFICHAGE, jamais un changement de score /
direction / conviction / mesure. Couvre :
- P1 : ligne « Fraîcheur » masquée quand OK, affichée quand problème.
- P9 : prix de réf. remplis depuis le live quand le stamp est absent (wiring).
- P6 : « Décor du jour » en tête + catalyseur ANNONCÉ (jamais un résultat).
- P2/P4/P5 : la pédagogie est consolidée dans « Comment lire les scores ».
- P3 : « Porté par » enrichi (nom complet + valeur + sens + contribution).
- P7 : « News par actif » rend les events réels par actif.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import briefing as bf  # noqa: E402
import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 6, 17, 7, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fabriques minimales (réutilise le style des autres tests)
# ---------------------------------------------------------------------------

def _crit(nom: str, cle: str, contrib: float, valeur=2.15, signe=-1) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="zscore",
        valeur_brute=valeur,
        valeur_norm=0.65,
        poids=8.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: contrib for h in sa.HORIZONS},
        cle_courante=cle,
    )


def _actif(nom: str, key: str, score: float, direction: str,
           driver_nom: str, driver_cle: str, valeur=2.15, signe=-1) -> sa.ActifResult:
    # Driver STRICTEMENT dominant mais < 50% du total (ni mono ◧, ni quasi-neutre)
    # → la cellule reste « forte » et entre dans la Sélection (cf. _actif des
    #   tests de sélection : 0.40 vs 0.33 + 0.33).
    c_top = _crit(driver_nom, driver_cle, score * 0.40, valeur=valeur, signe=signe)
    c_b = _crit("Critère secondaire", "drv_b", score * 0.33)
    c_c = _crit("Critère tertiaire", "drv_c", score * 0.33)
    return sa.ActifResult(
        nom=nom,
        fiche_key=key,
        criteres=[c_top, c_b, c_c],
        scores={h: (score if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (direction if h == "24h" else sa.CONCLUSION_INSUFFISANT)
                     for h in sa.HORIZONS},
        tie_break_notes={},
        confidence={h: "normale" for h in sa.HORIZONS},
        coverage=1.0,
    )


# ---------------------------------------------------------------------------
# P1 — Fraîcheur masquée si OK, visible si problème
# ---------------------------------------------------------------------------

def test_p1_fraicheur_masquee_si_ok():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    b = sa.render_bulletin([r], {}, NOW, "h", "fraîcheur OK — données du jour (< 1h)")
    tete = b.split("## ")[0]
    assert "- Généré" in tete
    assert "Fraîcheur" not in tete  # OK → masquée


def test_p1_fraicheur_visible_si_probleme():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    b = sa.render_bulletin([r], {}, NOW, "h",
                           "criteres-courants PÉRIMÉ : âge ≈ 5h")
    tete = b.split("## ")[0]
    assert "Fraîcheur" in tete
    assert "PÉRIMÉ" in tete


# ---------------------------------------------------------------------------
# P3 — « Porté par » enrichi (nom complet + valeur + sens + contribution)
# ---------------------------------------------------------------------------

def test_p3_driver_detail_format():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)",
               "taux_reels", valeur=2.15, signe=-1)
    detail = sa._driver_detail(r, "24h")
    # nom complet (non tronqué) + valeur + sens inversé + contribution signée.
    assert "Taux réels US (10 ans)" in detail
    assert "val 2.15" in detail
    assert "sens inversé" in detail
    assert "→ contribue -" in detail


def test_p3_driver_detail_sens_normal():
    r = _actif("S&P 500", "sp500", 6.63, "LONG", "Régime de volatilité (VIX)",
               "vix_regime", valeur=14.95, signe=1)
    detail = sa._driver_detail(r, "24h")
    assert "sens normal" in detail
    assert "→ contribue +" in detail


def test_p3_driver_detail_dans_selection_et_a_jouer():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    sel = "\n".join(sa.build_selection_du_jour_block([r], NOW))
    ajouer = "\n".join(sa.build_a_jouer_block([r], NOW))
    assert "val 2.15" in sel and "sens inversé" in sel
    assert "val 2.15" in ajouer and "sens inversé" in ajouer


# ---------------------------------------------------------------------------
# P2/P4/P5 — pédagogie consolidée dans « Comment lire les scores »
# ---------------------------------------------------------------------------

def test_p245_comment_lire_consolide():
    pedago = "\n".join(sa.build_comment_lire_block({"≈", "◧"}))
    assert "## Comment lire les scores" in pedago
    # Sélection (4 règles)
    assert "**signal fort**" in pedago
    assert "chaque type de marché représenté une seule fois" in pedago
    # À jouer (Conviction + Porté par + ⚭)
    assert "« Porté par »" in pedago
    assert "même driver" in pedago
    # Top convictions (◧ / ↯)
    assert "1 seul critère" in pedago
    # Légende des symboles + définition de Note
    assert "**Note**" in pedago


def test_p245_sections_du_jour_sans_blabla():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    sel = "\n".join(sa.build_selection_du_jour_block([r], NOW))
    ajouer = "\n".join(sa.build_a_jouer_block([r], NOW))
    # Le blabla méthodo n'est plus DANS les sections du jour.
    assert "**signal fort**" not in sel
    assert "« Porté par » = le critère" not in ajouer


# ---------------------------------------------------------------------------
# Couper le gras (fondateur 25/06) : « prend du recul... à quoi me sert ce
# paragraphe ». Suppression des blocs verbeux redondants avec la synthèse 12×3 :
# « Top swing (7j/1m) », « Top convictions multi-horizons », « Biais agrégé ».
# ---------------------------------------------------------------------------

def test_couper_le_gras_blocs_verbeux_supprimes():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    b = sa.render_bulletin([r], {}, NOW, "h", "fraîcheur OK")
    assert "## Top swing (7j / 1m)" not in b      # bloc verbeux multi-horizons
    assert "Top convictions multi-horizons" not in b  # légende du bloc supprimé
    assert "Biais agrégé" not in b                 # ligne non actionnable
    # Les sélections (24h / 7j / 1m) restent — recentrage, pas suppression.
    assert "## 🎯 Aujourd'hui" in b
    assert "## 📈 Swing 7j (max 3)" in b
    assert "## 🗓️ Positions 1 mois (max 3)" in b


def test_swing_rendu_en_tableau():
    """Swing 7j / Positions 1m affichés en TABLEAU aligné (fondateur 25/06) avec
    enrichissement du porteur news (plus de jargon « Synthèse news (net, IA) »)."""
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    r.conclusions = {h: "SHORT" for h in sa.HORIZONS}
    r.scores = {h: -7.82 for h in sa.HORIZONS}
    fiches = {"or": {"seuils_reussite_pct": {"7j": 1.3, "1m": 3.0}}}
    txt = "\n".join(sa.build_swing_7j_block([r], prix_reference={"or": 3993.45},
                                            fiches=fiches, now=NOW))
    assert "| Actif | Sens | Objectif | Entrée | Porté par |" in txt
    assert "| **Or** | SHORT |" in txt
    assert "Synthèse news (net, IA)" not in txt


def test_p245_comment_lire_present_une_fois_dans_bulletin():
    r = _actif("Or", "or", -7.82, "SHORT", "Taux réels US (10 ans)", "taux_reels")
    b = sa.render_bulletin([r], {}, NOW, "h", "fraîcheur OK — x")
    assert b.count("## Comment lire les scores") == 1
    # Placée avant le détail par actif.
    assert b.index("## Comment lire les scores") < b.index("## Détail par actif")


# ---------------------------------------------------------------------------
# P6 — Décor du jour en tête + catalyseur ANNONCÉ (jamais un résultat)
# ---------------------------------------------------------------------------

def test_p6_decor_catalyseur_annonce_pas_resultat(monkeypatch):
    monkeypatch.setattr(bf, "_catalyseurs_j0_noms", lambda now: ["Décision de taux Fed (FOMC)"])
    lines = bf.build_intro_block([], {}, date(2026, 6, 17),
                                 datetime(2026, 6, 17, 7, 0))
    txt = "\n".join(lines)
    assert "## Décor du jour" in txt
    # HONNÊTETÉ : « attendu(s) aujourd'hui » — annonce, pas un résultat.
    assert "attendu(s) aujourd'hui" in txt
    assert "Décision de taux Fed (FOMC)" in txt
    # Aucune affirmation de résultat (pas de « résultat », « a annoncé », etc.).
    assert "résultat" not in txt.lower()


def test_p6_build_briefing_pas_de_double_bloc_news():
    # build_briefing ne porte que le Décor (pas de « Briefing du jour » per-actif).
    md = bf.build_briefing(today=date(2026, 6, 17))
    assert md.startswith("## Décor du jour")
    assert "## Briefing du jour" not in md


# ---------------------------------------------------------------------------
# P7 — News par actif (events réels par actif, « — aucune actualité » sinon)
# ---------------------------------------------------------------------------

_LOG_P7 = """# events-log

| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-17 |  | OPEC | OPEC discusses output cut | BRENT | intraday | 1 | reuters | Global | commodity |  | BRENT:SHORT:75 | high | confirmed |
"""


def test_p7_news_par_actif_rend_events_reels(tmp_path):
    p = tmp_path / "events-log.md"
    p.write_text(_LOG_P7, encoding="utf-8")
    md = bf.build_news_par_actif(events_path=p, today=date(2026, 6, 17))
    assert md.startswith("## News par actif")
    assert "### Pétrole" in md
    assert "OPEC discusses output cut" in md
    assert "(reuters)" in md
    # Un actif sans news → « _aucune actualité_ ».
    assert "_aucune actualité_" in md


def test_p7_news_par_actif_zero_invention(tmp_path):
    # events-log vide → tous les actifs « _aucune actualité_ », aucun titre inventé.
    p = tmp_path / "events-log.md"
    p.write_text("# vide\n", encoding="utf-8")
    md = bf.build_news_par_actif(events_path=p, today=date(2026, 6, 17))
    assert md.count("_aucune actualité_") >= 12


# ---------------------------------------------------------------------------
# P9 — Prix de réf. remplis depuis le live quand le stamp est absent
# ---------------------------------------------------------------------------

def test_p9_prix_reference_rempli_depuis_live(monkeypatch, tmp_path):
    """Au run 7h le stamp n'existe pas → prix_reference doit être alimenté depuis
    le fetch live (même mapping ticker→fiche_key). Wiring testé via run()."""
    import journaliste as journ
    import criteres_calculator as cc

    # Fiches minimales : 1 actif avec ticker_principal.
    fiche = {"actif": "Or", "ticker_principal": "XAU/USD",
             "criteres": []}
    monkeypatch.setattr(sa, "load_fiches", lambda *a, **k: {"or": fiche})
    # criteres-courants frais (fraîcheur OK).
    monkeypatch.setattr(sa, "load_criteres_courants",
                        lambda *a, **k: {"last_update": NOW.isoformat()})
    monkeypatch.setattr(sa, "check_freshness", lambda *a, **k: (True, "fraîcheur OK — x"))
    monkeypatch.setattr(sa, "load_veille", lambda *a, **k: (None, {}))
    monkeypatch.setattr(sa, "score_actif",
                        lambda *a, **k: _actif("Or", "or", -7.0, "SHORT",
                                               "Taux réels US (10 ans)", "taux_reels"))
    monkeypatch.setattr(sa, "compute_shadow_capteurs", lambda *a, **k: {})
    # STAMP ABSENT (run 7h) → load_prix_emission vide ; LIVE renvoie le prix.
    monkeypatch.setattr(journ, "load_prix_emission", lambda *a, **k: {})
    monkeypatch.setattr(cc, "fetch_twelve_price", lambda tk: 4308.0 if tk == "XAU/USD" else None)

    captured = {}
    orig_render = sa.render_bulletin

    def _spy_render(results, veille, now, fhash, fresh, **kwargs):
        captured["prix_reference"] = kwargs.get("prix_reference")
        return orig_render(results, veille, now, fhash, fresh, **kwargs)

    monkeypatch.setattr(sa, "render_bulletin", _spy_render)

    sa.run(now=datetime(2026, 6, 17, 7, 0), write=False)
    # P9 — prix_reference doit être rempli depuis le live (stamp absent).
    assert captured["prix_reference"] == {"or": 4308.0}
