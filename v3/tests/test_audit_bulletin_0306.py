"""Audit trio du bulletin 03/06 — 4 modifs d'AFFICHAGE / SHADOW sur scoring_analyste.

Garantie testée ici : ZÉRO impact sur les CONCLUSIONS (LONG/SHORT/INSUFFISANT).
Ces modifs sont purement de l'affichage (Q1 Top 3 distinct, Q2 régime news non
ambigu, K2 drapeau ≈) ou des drapeaux shadow decision-log (K1 mono-critère).

  Q1 — Top 3 = actifs DISTINCTS (testé dans test_bulletin_top3_fusion.py)
  Q2 — Régime news : la direction vient du biais news, le chiffre quant étiqueté
  K2 — Bande quasi-neutre (≈) sur cellule actionnée 0.05 ≤ |note| < 0.30, conclusion inchangée
  K1 — Mono-critère dominant loggé dans le decision-log (pas affiché en matrice)
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


NOW = datetime(2026, 6, 3, 9, 0, tzinfo=timezone.utc)


def _fiche(quant_signe: int = 1, quant_poids: int = 10) -> dict:
    """Fiche minimale à 1 critère quant (couverture 100%)."""
    return {
        "actif": "TestActif",
        "criteres": [
            {
                "id": 1, "nom": "Quant",
                "cle_courante": "quant", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 5.0,
                "signe": quant_signe, "poids": quant_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _fiche_deux_criteres() -> dict:
    """Fiche 2 critères de poids très différents (pour mono-critère dominant)."""
    return {
        "actif": "TestMono",
        "criteres": [
            {
                "id": 1, "nom": "VIX régime",
                "cle_courante": "vix", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 10.0,
                "signe": 1, "poids": 20,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
            {
                "id": 2, "nom": "Momentum mineur",
                "cle_courante": "mom", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 10.0,
                "signe": 1, "poids": 1,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _vals(quant_val: float) -> dict:
    return {"quant": {"valeur": quant_val, "source_track": "twelvedata"}}


# ===========================================================================
# Q2 — Régime news : direction du biais news, chiffre quant étiqueté
# ===========================================================================

def test_regime_news_affichage_sans_contradiction_de_signe():
    """Cellule en régime news avec un score quant de signe OPPOSÉ à la direction :
    l'affichage ne doit JAMAIS montrer la direction collée au chiffre contradictoire.
    Cas réel : Cuivre 1m « LONG (-0.64) » → doit devenir « LONG ... [quant -0.64] »."""
    r = sa.score_actif("test", _fiche(), _vals(1.0))
    r.nom = "Cuivre"
    # Force un régime news LONG avec un quant NÉGATIF (contradiction de signe).
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.scores = {h: -0.64 for h in sa.HORIZONS}
    r.confidence = {h: "faible" for h in sa.HORIZONS}
    r.is_news_regime = {h: True for h in sa.HORIZONS}
    r.coverage = 0.35

    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    synth = b.split("## Synthèse des décisions")[1].split("## Détail")[0]
    # La direction LONG apparaît, le chiffre quant est étiqueté explicitement.
    assert "[quant -0.64]" in synth
    assert "📰 régime news" in synth
    # ANTI-CONTRADICTION : on ne doit JAMAIS trouver "LONG (-0.64)" collé,
    # ni "LONG -0.64" en tête de cellule (le chiffre ne contredit plus la direction).
    assert "LONG (-0.64)" not in synth
    assert "LONG -0.64" not in synth
    # La conclusion (LONG) n'a pas changé.
    assert all(r.conclusions[h] == "LONG" for h in sa.HORIZONS)


# ===========================================================================
# K2 — Bande quasi-neutre (≈), conclusion inchangée
# ===========================================================================

def test_bande_quasi_neutre_drapeau_mais_conclusion_inchangee():
    """|note| = 0.2 (0.05 ≤ |note| < 0.30) → drapeau ≈ MAIS la conclusion
    reste SHORT (shadow). Cas réel : Cuivre 7j -0.28 « habillé en SHORT ferme »."""
    r = sa.score_actif("test", _fiche(quant_signe=-1), _vals(0.2))
    r.nom = "Cuivre"
    r.scores = {h: -0.2 for h in sa.HORIZONS}
    r.conclusions = {h: "SHORT" for h in sa.HORIZONS}
    r.confidence = {h: "normale" for h in sa.HORIZONS}

    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    synth = b.split("## Synthèse des décisions")[1].split("## Détail")[0]
    assert "≈" in synth  # drapeau quasi-neutre présent
    # Conclusion INCHANGÉE : la cellule reste SHORT avec sa note.
    assert "SHORT (-0.20)" in synth
    assert all(r.conclusions[h] == "SHORT" for h in sa.HORIZONS)


def test_bande_quasi_neutre_exclut_coin_flip():
    """|note| < 0.05 → ⚪ (coin-flip), PAS ≈ (les deux sont exclusifs ; ⚪ prime)."""
    r = sa.score_actif("test", _fiche(), _vals(0.02))
    r.nom = "SP"
    r.scores = {h: 0.02 for h in sa.HORIZONS}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.confidence = {h: "normale" for h in sa.HORIZONS}

    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    synth = b.split("## Synthèse des décisions")[1].split("## Détail")[0]
    assert "⚪" in synth
    assert "≈" not in synth


def test_bande_quasi_neutre_exclut_note_forte():
    """|note| ≥ 0.30 → ni ⚪ ni ≈ (conviction normale)."""
    r = sa.score_actif("test", _fiche(), _vals(5.0))
    r.nom = "Or"
    r.scores = {h: 1.5 for h in sa.HORIZONS}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.confidence = {h: "normale" for h in sa.HORIZONS}

    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    synth = b.split("## Synthèse des décisions")[1].split("## Détail")[0]
    assert "≈" not in synth


# ===========================================================================
# K1 — Mono-critère dominant (decision-log only)
# ===========================================================================

def test_mono_critere_dominant_detecte_et_logue():
    """Un critère poids 20 vs un poids 1 → mono-critère dominant True + nom loggé."""
    r = sa.score_actif(
        "mono", _fiche_deux_criteres(),
        {"vix": {"valeur": 5.0, "source_track": "cboe"},
         "mom": {"valeur": 0.1, "source_track": "twelvedata"}},
    )
    r.nom = "SP"
    records = sa.build_decision_log_records([r], NOW)
    assert records, "decision-log non vide attendu"
    for rec in records:
        assert rec["mono_critere_dominant"] is True
        assert rec["mono_critere_nom"] == "VIX régime"


def test_mono_critere_helper_direct():
    """detect_mono_critere_dominant : True si un critère > 50% du |score|."""
    r = sa.score_actif(
        "mono", _fiche_deux_criteres(),
        {"vix": {"valeur": 5.0, "source_track": "cboe"},
         "mom": {"valeur": 0.1, "source_track": "twelvedata"}},
    )
    is_mono, nom = sa.detect_mono_critere_dominant(r, "24h")
    assert is_mono is True
    assert nom == "VIX régime"


def test_mono_critere_absent_quand_equilibre():
    """Deux critères de contribution égale → pas de mono-dominant."""
    r = sa.score_actif(
        "equi",
        {
            "actif": "Equi",
            "criteres": [
                {"id": 1, "nom": "A", "cle_courante": "a", "normalisation": "lineaire",
                 "centre": 0.0, "echelle": 1.0, "cap": 10.0, "signe": 1, "poids": 10,
                 "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
                {"id": 2, "nom": "B", "cle_courante": "b", "normalisation": "lineaire",
                 "centre": 0.0, "echelle": 1.0, "cap": 10.0, "signe": 1, "poids": 10,
                 "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            ],
        },
        {"a": {"valeur": 1.0, "source_track": "x"},
         "b": {"valeur": 1.0, "source_track": "x"}},
    )
    is_mono, nom = sa.detect_mono_critere_dominant(r, "24h")
    assert is_mono is False
    assert nom is None


def test_mono_critere_affiche_en_matrice():
    """A1 (audit trio 05/06) — REVERSAL du choix K1 : le mono-critère dominant
    est désormais rendu VISIBLE dans la matrice via le drapeau ◧ (flag-only).
    Les 3 experts ont jugé le mono-critère trop fragile pour rester invisible."""
    r = sa.score_actif(
        "mono", _fiche_deux_criteres(),
        {"vix": {"valeur": 5.0, "source_track": "cboe"},
         "mom": {"valeur": 0.1, "source_track": "twelvedata"}},
    )
    r.nom = "SP"
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    synth = b.split("## Synthèse des décisions")[1].split("## Détail")[0]
    # Le drapeau ◧ apparaît dans la matrice ET dans la légende.
    assert "◧" in synth
    assert "mono-critère dominant" in b  # légende


def test_mono_critere_flag_only_conclusion_inchangee():
    """A1 — le drapeau ◧ est FLAG-ONLY : la conclusion LONG/SHORT n'est jamais
    mutée par l'ajout du drapeau."""
    r = sa.score_actif(
        "mono", _fiche_deux_criteres(),
        {"vix": {"valeur": 5.0, "source_track": "cboe"},
         "mom": {"valeur": 0.1, "source_track": "twelvedata"}},
    )
    r.nom = "SP"
    avant = dict(r.conclusions)
    sa.render_bulletin([r], {}, NOW, "h", "ok")
    assert dict(r.conclusions) == avant


def test_mono_critere_dans_cellules_a_surveiller():
    """A1 — une cellule mono-critère (direction actée) doit apparaître dans la
    section 'Cellules à surveiller' (alerte de fragilité)."""
    r = sa.score_actif(
        "mono", _fiche_deux_criteres(),
        {"vix": {"valeur": 5.0, "source_track": "cboe"},
         "mom": {"valeur": 0.1, "source_track": "twelvedata"}},
    )
    r.nom = "SP"
    flags = sa._compute_cell_risk_flags(r, "24h", NOW)
    assert "◧" in flags
    assert sa._cellule_a_surveiller(r, "24h", flags) is True


def test_mono_critere_pas_de_surveillance_si_insuffisant():
    """A1 — pas de ◧ sur une cellule INSUFFISANT (pas de direction à fragiliser)."""
    r = sa.score_actif(
        "mono", _fiche_deux_criteres(),
        {"vix": {"valeur": 5.0, "source_track": "cboe"},
         "mom": {"valeur": 0.1, "source_track": "twelvedata"}},
    )
    r.nom = "SP"
    r.conclusions = {h: sa.CONCLUSION_INSUFFISANT for h in sa.HORIZONS}
    flags = sa._compute_cell_risk_flags(r, "24h", NOW)
    assert "◧" not in flags


def test_quasi_neutre_champ_decision_log():
    """A2 (audit trio 05/06) — le champ shadow quasi_neutre marque les notes
    |score|<0.30 (NEUTRAL_BAND), englobant coin_flip strict ET bande ≈.
    Cas réel : Cuivre 7j (-0.22) → coin_flip=False mais quasi_neutre=True.
    Le seuil coin_flip (0.05) NE bouge PAS (couplé à EPSILON_CARRY)."""
    r = sa.score_actif("a", _fiche(), _vals(5.0))
    r.nom = "Cuivre"
    # 7j à -0.22 (bande ≈, pas coin-flip strict) ; 1m à -0.53 (au-delà de la bande).
    r.scores = {"24h": -0.02, "7j": -0.22, "1m": -0.53}
    r.conclusions = {h: "SHORT" for h in sa.HORIZONS}
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    records = {rec["horizon"]: rec for rec in sa.build_decision_log_records([r], NOW)}
    # 24h : coin_flip ET quasi_neutre.
    assert records["24h"]["coin_flip"] is True
    assert records["24h"]["quasi_neutre"] is True
    # 7j (-0.22) : PAS coin_flip (>0.05) MAIS quasi_neutre (<0.30) — le cas raté.
    assert records["7j"]["coin_flip"] is False
    assert records["7j"]["quasi_neutre"] is True
    # 1m (-0.53) : ni l'un ni l'autre (au-delà de la bande).
    assert records["1m"]["coin_flip"] is False
    assert records["1m"]["quasi_neutre"] is False


def test_coin_flip_seuil_inchange():
    """A2 — garde-fou : le seuil coin_flip reste à 0.05 (EPSILON_CARRY), il N'a
    PAS été déplacé à 0.30. -0.10 = au-dessus du seuil coin_flip."""
    r = sa.score_actif("a", _fiche(), _vals(5.0))
    r.scores = {h: -0.10 for h in sa.HORIZONS}
    r.conclusions = {h: "SHORT" for h in sa.HORIZONS}
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    rec = sa.build_decision_log_records([r], NOW)[0]
    assert rec["coin_flip"] is False  # 0.10 > 0.05 → pas coin_flip
    assert rec["quasi_neutre"] is True  # 0.10 < 0.30 → quasi_neutre


# ===========================================================================
# NON-RÉGRESSION DES CONCLUSIONS — preuve que l'affichage ne change rien
# ===========================================================================

def _make_jeu_de_cellules() -> list:
    """Jeu de cellules couvrant tous les cas (normale, quasi-neutre, news-regime,
    coin-flip, conviction forte)."""
    cellules = []

    a = sa.score_actif("a", _fiche(), _vals(5.0))
    a.nom = "Or"
    a.scores = {"24h": 1.5, "7j": 0.20, "1m": -0.09}  # forte, quasi-neutre, coin-flip
    a.conclusions = {"24h": "LONG", "7j": "LONG", "1m": "SHORT"}
    a.confidence = {h: "normale" for h in sa.HORIZONS}
    cellules.append(a)

    b = sa.score_actif("b", _fiche(), _vals(1.0))
    b.nom = "Cuivre"
    b.scores = {h: -0.64 for h in sa.HORIZONS}
    b.conclusions = {h: "LONG" for h in sa.HORIZONS}  # régime news (signe opposé)
    b.confidence = {h: "faible" for h in sa.HORIZONS}
    b.is_news_regime = {h: True for h in sa.HORIZONS}
    b.coverage = 0.35
    cellules.append(b)
    return cellules


def test_non_regression_conclusions_identiques_apres_affichage():
    """Test de non-régression : les directions (conclusions) d'un jeu de cellules
    sont STRICTEMENT identiques avant et après le rendu (les nouveaux affichages
    Q1/Q2/K2 et le log K1 ne mutent JAMAIS r.conclusions)."""
    cellules = _make_jeu_de_cellules()
    # Snapshot des directions AVANT rendu.
    avant = {r.nom: dict(r.conclusions) for r in cellules}

    # Rendu complet (déclenche tout le pipeline d'affichage) + decision-log K1.
    sa.render_bulletin(cellules, {}, NOW, "h", "ok")
    sa.build_decision_log_records(cellules, NOW)

    # Snapshot APRÈS.
    apres = {r.nom: dict(r.conclusions) for r in cellules}
    assert avant == apres, (
        "RÉGRESSION : une direction a changé entre avant et après affichage — "
        f"avant={avant} après={apres}"
    )


def test_non_regression_scores_inchanges():
    """Les scores numériques ne sont pas non plus altérés par l'affichage."""
    cellules = _make_jeu_de_cellules()
    avant = {r.nom: dict(r.scores) for r in cellules}
    sa.render_bulletin(cellules, {}, NOW, "h", "ok")
    apres = {r.nom: dict(r.scores) for r in cellules}
    assert avant == apres
