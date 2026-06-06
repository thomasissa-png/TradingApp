"""#4 / #5 — Refonte du rendu du bulletin (forme uniquement, zéro changement
de calcul) :

  #4.1  Bloc « 🎯 Top 3 convictions du jour » en tête (cellules à confidence
        "normale" + |note| forte, jamais de remplissage avec du faible).
  #4.2  Fusion des deux tables de synthèse en UNE seule « ## Synthèse des
        décisions » (format riche), suppression de l'ancienne « ## Matrice ».
  #5.1  Drapeau ⚑ régime extrême annoncé UNE fois en tête quand quasi-global,
        plus répété sur chaque cellule de la table fusionnée.
  #5.2  « ## ⚠️ Cellules à surveiller » resserré (exclut INSUFFISANT + flags de
        couverture isolés ⚠️/⏸/📰).

Tous ces tests vérifient le RENDU : aucune conclusion / score n'est modifié.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


NOW = datetime(2026, 6, 2, 9, 0, tzinfo=timezone.utc)


def _fiche(quant_signe: int = 1, quant_poids: int = 10) -> dict:
    """Fiche minimale à 1 critère quant (couverture 100% → confidence normale)."""
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


def _vals(quant_val: float) -> dict:
    return {"quant": {"valeur": quant_val, "source_track": "twelvedata"}}


def _fiche_equilibree() -> dict:
    """Fiche à 2 critères de poids égaux → PAS de mono-critère dominant (◧).
    Utile pour isoler les autres flags de surveillance sans déclencher A1."""
    return {
        "actif": "TestActif",
        "criteres": [
            {"id": 1, "nom": "QuantA", "cle_courante": "qa", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": 1, "poids": 10,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 2, "nom": "QuantB", "cle_courante": "qb", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": 1, "poids": 10,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
        ],
    }


def _vals2(va: float, vb: float) -> dict:
    return {"qa": {"valeur": va, "source_track": "twelvedata"},
            "qb": {"valeur": vb, "source_track": "twelvedata"}}


# ===========================================================================
# #4.2 — Une seule table de synthèse (fusion)
# ===========================================================================

def test_une_seule_table_de_synthese():
    """Une SEULE table de décisions : '## Synthèse des décisions' présente,
    l'ancienne '## Matrice' supprimée."""
    res = sa.score_actif("test", _fiche(), _vals(1.0))
    b = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert b.count("## Synthèse des décisions") == 1
    assert "## Matrice" not in b
    # Format riche conservé dans la table fusionnée (note signée entre parenthèses)
    synth = b.split("## Synthèse des décisions")[1].split("## ⚠️")[0]
    line = next(l for l in synth.splitlines() if l.startswith("| TestActif"))
    assert "LONG" in line and "(" in line and ")" in line


def test_synthese_garde_sous_table_insuffisant_separee():
    """Les actifs INSUFFISANT restent regroupés dans une sous-table dédiée."""
    res = sa.score_actif("test", _fiche(), _vals(1.0))
    res.conclusions = {h: sa.CONCLUSION_INSUFFISANT for h in sa.HORIZONS}
    res.confidence = {h: "insuffisant" for h in sa.HORIZONS}
    b = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "Données insuffisantes (🚫" in b


# ===========================================================================
# #4.1 — Top 3 convictions : uniquement des cellules "normale"
# ===========================================================================

def test_top3_present_en_tete():
    """Le bloc Top 3 est présent et placé avant la table de synthèse."""
    res = sa.score_actif("test", _fiche(quant_poids=10), _vals(1.0))
    b = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "## 🎯 Top 3 convictions du jour" in b
    assert b.index("## 🎯 Top 3 convictions du jour") < b.index("## Synthèse des décisions")


def test_top3_ne_contient_que_des_cellules_normales():
    """Une cellule à confidence 'faible' (ou carry/news_regime/insuffisant) ne
    doit JAMAIS apparaître dans le Top 3 — même si sa |note| est énorme."""
    # Actif A : forte note, confidence normale → éligible
    a = sa.score_actif("a", _fiche(quant_poids=10), _vals(1.0))
    a.nom = "ForteNormale"
    a.confidence = {h: "normale" for h in sa.HORIZONS}
    # Actif B : note ÉNORME mais confidence faible → DOIT être exclu
    b_res = sa.score_actif("b", _fiche(quant_poids=10), _vals(1.0))
    b_res.nom = "FaibleMaisGrosse"
    b_res.scores = {h: 999.0 for h in sa.HORIZONS}
    b_res.confidence = {h: "faible" for h in sa.HORIZONS}

    block = sa.build_top3_block([a, b_res])
    txt = "\n".join(block)
    assert "ForteNormale" in txt
    assert "FaibleMaisGrosse" not in txt


def test_top3_exclut_carry_et_regime_news():
    """Carry-forward (⏸) et régime news (📰) sont exclus du Top 3."""
    carry = sa.score_actif("c", _fiche(quant_poids=10), _vals(1.0))
    carry.nom = "Carry"
    carry.confidence = {h: "faible" for h in sa.HORIZONS}
    carry.is_carry = {h: True for h in sa.HORIZONS}
    news = sa.score_actif("n", _fiche(quant_poids=10), _vals(1.0))
    news.nom = "RegimeNews"
    news.confidence = {h: "faible" for h in sa.HORIZONS}
    news.is_news_regime = {h: True for h in sa.HORIZONS}
    block = "\n".join(sa.build_top3_block([carry, news]))
    assert "Carry" not in block
    assert "RegimeNews" not in block


def test_top3_montre_moins_de_3_si_moins_de_3_normales():
    """Si une seule cellule 'normale' existe, le Top 3 n'en montre qu'une (pas
    de remplissage avec du faible)."""
    a = sa.score_actif("a", _fiche(quant_poids=10), _vals(1.0))
    a.nom = "SeuleNormale"
    a.confidence = {"24h": "normale", "7j": "faible", "1m": "faible"}
    block = sa.build_top3_block([a])
    # 1 seule ligne de conviction (préfixée '- **')
    convictions = [l for l in block if l.startswith("- **")]
    assert len(convictions) == 1
    assert "SeuleNormale 24h" in convictions[0]


def test_top3_placeholder_si_aucune_normale():
    """Aucune cellule 'normale' → message explicite, jamais de fausse conviction."""
    a = sa.score_actif("a", _fiche(quant_poids=10), _vals(1.0))
    a.confidence = {h: "faible" for h in sa.HORIZONS}
    block = "\n".join(sa.build_top3_block([a]))
    assert "Aucune conviction à couverture suffisante" in block
    assert "- **" not in block


def test_top3_un_seul_actif_garde_meilleur_horizon():
    """Q1 — max 1 cellule par actif : un actif seul ne sort QU'UNE fois (son
    meilleur horizon par |note|), pas 3 fois pour ses 3 horizons."""
    a = sa.score_actif("a", _fiche(quant_poids=10), _vals(1.0))
    a.nom = "A"
    a.scores = {"24h": 1.0, "7j": 8.0, "1m": 3.0}
    a.confidence = {h: "normale" for h in sa.HORIZONS}
    block = [l for l in sa.build_top3_block([a]) if l.startswith("- **")]
    # Un seul actif distinct → une seule ligne, et c'est son meilleur horizon (7j).
    assert len(block) == 1
    assert "A 7j" in block[0]
    assert "A 1m" not in "\n".join(block)
    assert "A 24h" not in "\n".join(block)


def test_top3_trois_actifs_distincts():
    """Q1 (audit trio 03/06) — le Top 3 contient 3 actifs DISTINCTS, jamais le
    même actif sur plusieurs horizons (« Pétrole, Pétrole, Pétrole » corrigé)."""
    actifs = []
    # Pétrole : 3 horizons à fort |note| (aurait monopolisé l'ancien Top 3).
    petrole = sa.score_actif("petrole", _fiche(quant_poids=10), _vals(1.0))
    petrole.nom = "Petrole"
    petrole.scores = {"24h": 9.0, "7j": 8.0, "1m": 7.0}
    petrole.confidence = {h: "normale" for h in sa.HORIZONS}
    actifs.append(petrole)
    # Or et Cuivre : un horizon fort chacun.
    for nom, sc in (("Or", 6.0), ("Cuivre", 5.0)):
        r = sa.score_actif(nom.lower(), _fiche(quant_poids=10), _vals(1.0))
        r.nom = nom
        r.scores = {"24h": sc, "7j": sc / 2, "1m": sc / 3}
        r.confidence = {h: "normale" for h in sa.HORIZONS}
        actifs.append(r)
    block = [l for l in sa.build_top3_block(actifs) if l.startswith("- **")]
    assert len(block) == 3
    # 3 actifs DISTINCTS présents, et Pétrole n'apparaît qu'UNE fois.
    joined = "\n".join(block)
    assert "Petrole" in joined and "Or" in joined and "Cuivre" in joined
    assert sum(1 for ln in block if "Petrole" in ln) == 1
    assert "Petrole 24h" in block[0]  # meilleur horizon du pétrole (|9.0|)


# ===========================================================================
# #5.1 — Régime extrême annoncé UNE fois (plus 12×)
# ===========================================================================

def _fiche_avec_gate(gate_active: bool) -> dict:
    return {
        "actif": "TestGate",
        "criteres": [
            {
                "id": 1, "nom": "Quant",
                "cle_courante": "quant", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 5.0,
                "signe": 1, "poids": 10,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
            {
                "id": 2, "nom": "GATE régime extrême",
                "cle_courante": "gate_regime", "normalisation": "gate",
                "signe": 1, "poids": 0,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _vals_gate(gate_active: bool) -> dict:
    return {
        "quant": {"valeur": 1.0, "source_track": "twelvedata"},
        "gate_regime": {"valeur": bool(gate_active)},
    }


def test_regime_extreme_annonce_une_fois_quand_global():
    """Gate actif sur tous les actifs → annonce UNE fois en tête, ⚑ retiré des
    cellules de la table de synthèse (plus de répétition 12×)."""
    actifs = []
    for i in range(3):
        r = sa.score_actif("g", _fiche_avec_gate(True), _vals_gate(True))
        r.nom = f"Actif{i}"
        actifs.append(r)
    assert sa.regime_extreme_global(actifs) is True
    b = sa.render_bulletin(actifs, {}, NOW, "h", "ok")
    # Annonce globale présente exactement 1×
    assert b.count("Régime extrême actif sur l'ensemble du tableau") == 1
    # ⚑ retiré de la table de synthèse (cellules)
    synth = b.split("## Synthèse des décisions")[1].split("## ⚠️")[0]
    assert "⚑" not in synth
    # ⚑ conservé dans le détail par critère (où il discrimine) — le gate actif
    # est marqué « Drapeau régime ⚑ actif » dans la colonne « Comment c'est lu »
    # (info de risque préservée après suppression de la colonne « Note »).
    detail = b.split("## Détail par actif")[1]
    assert "⚑ actif" in detail
    assert "Drapeau régime ⚑ actif" in detail


def test_regime_extreme_garde_le_drapeau_par_cellule_si_partiel():
    """Si le gate n'est PAS quasi-global, le ⚑ reste sur les cellules (info
    discriminante) et il n'y a pas d'annonce globale."""
    actif_gate = sa.score_actif("g", _fiche_avec_gate(True), _vals_gate(True))
    actif_gate.nom = "AvecGate"
    actif_sans = sa.score_actif("s", _fiche_avec_gate(False), _vals_gate(False))
    actif_sans.nom = "SansGate"
    actifs = [actif_gate, actif_sans]
    # 1/2 actifs avec gate = 50% < 90% → pas global
    assert sa.regime_extreme_global(actifs) is False
    b = sa.render_bulletin(actifs, {}, NOW, "h", "ok")
    assert "Régime extrême actif sur l'ensemble du tableau" not in b
    synth = b.split("## Synthèse des décisions")[1].split("## ⚠️")[0]
    assert "⚑" in synth  # conservé sur la cellule de AvecGate


# ===========================================================================
# #5.2 — Surveillance resserrée
# ===========================================================================

def test_surveillance_exclut_flag_couverture_isole():
    """Une cellule dont le SEUL flag est ⚠️ conf. faible (qualificatif de
    couverture, pas une alerte directionnelle) n'est PAS dans la surveillance."""
    # Fiche équilibrée (2 critères) → pas de ◧ mono-critère pour isoler le cas
    # « seul flag = qualificatif de couverture » (A1 n'interfère pas).
    r = sa.score_actif("a", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.nom = "ConfFaible"
    r.confidence = {h: "faible" for h in sa.HORIZONS}
    r.divergence_quant_news = {h: False for h in sa.HORIZONS}
    r.contre_momentum = {h: False for h in sa.HORIZONS}
    r.incoherence_inter_horizons = False
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    section = b.split("## ⚠️ Cellules à surveiller", 1)[1].split("##", 1)[0]
    assert "_Aucune cellule à risque directionnel ce cycle._" in section
    assert "ConfFaible" not in section


def test_surveillance_garde_alerte_directionnelle_sur_direction_actee():
    """Une direction ACTÉE (LONG/SHORT) avec divergence ↯ est bien surveillée."""
    # Fiche équilibrée (2 critères) : seul le ↯ du 24h doit faire remonter la
    # cellule (sans ◧ mono-critère qui remonterait aussi 7j/1m).
    r = sa.score_actif("a", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.nom = "AvecDivergence"
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    r.divergence_quant_news = {"24h": True, "7j": False, "1m": False}
    r.contre_momentum = {h: False for h in sa.HORIZONS}
    r.incoherence_inter_horizons = False
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    section = b.split("## ⚠️ Cellules à surveiller", 1)[1].split("##", 1)[0]
    assert "AvecDivergence 24h" in section
    assert "↯" in section
    # Les horizons sans alerte ne remontent pas
    assert "AvecDivergence 7j" not in section


# ===========================================================================
# Reformulation tableau « Détail par actif » (reco-wording-detail-bulletin.md)
# ===========================================================================

def test_detail_table_wording_humain():
    """Les nouveaux en-têtes, la traduction des types, la colonne Sens humaine
    et l'encart « Comment lire ce tableau » (1×) sont rendus ; les anciens
    libellés techniques ont disparu de la section Détail."""
    r = sa.score_actif("a", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.nom = "ActifWording"
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    detail = b.split("## Détail par actif")[1]

    # Nouveaux en-têtes (9 colonnes, plus de « Note »)
    assert "| Critère | Comment c'est lu | Valeur actuelle | Penchant | Importance | Sens | Effet 24h | Effet 7j | Effet 1m |" in detail
    # Séparateur à 9 colonnes (9 cellules → 10 pipes)
    assert "|---|---|---|---|---|---|---|---|---|\n" in detail

    # Anciens libellés techniques retirés de la vue
    assert "| Type |" not in detail
    assert "Valeur brute" not in detail
    assert "| Norm. |" not in detail

    # Traduction de type : la fiche équilibrée utilise des critères « lineaire »
    assert "Échelle graduée" in detail
    # Sens humain (signe +1 → « normal »), plus de « +1 » brut en colonne Sens
    assert "| normal |" in detail

    # Encart inséré exactement une fois, avant le 1er actif
    assert b.count("**Comment lire ce tableau**") == 1
    assert b.index("**Comment lire ce tableau**") < b.index("### ActifWording")


def test_detail_table_sens_inverse():
    """Un critère de signe -1 affiche « inversé » dans la colonne Sens."""
    r = sa.score_actif("a", _fiche(quant_signe=-1), _vals(1.0))
    r.nom = "ActifInverse"
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    detail = b.split("## Détail par actif")[1]
    assert "| inversé |" in detail
