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
    """Le bloc « À jouer aujourd'hui (24h) » + le mini « Top convictions
    multi-horizons » sont présents et placés avant la table de synthèse
    (remplacent l'ancien « Top 3 convictions du jour »)."""
    res = sa.score_actif("test", _fiche(quant_poids=10), _vals(1.0))
    b = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "## 🎯 À jouer aujourd'hui (24h)" in b
    assert "## 🎯 Top convictions multi-horizons" in b
    assert b.index("## 🎯 À jouer aujourd'hui (24h)") < b.index("## Synthèse des décisions")
    assert b.index("## 🎯 À jouer aujourd'hui (24h)") < b.index("## 🎯 Top convictions multi-horizons")
    # L'ancien titre exact a disparu (absorbé).
    assert "## 🎯 Top 3 convictions du jour" not in b


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


def test_detail_synthese_avant_tableau():
    """La synthèse directionnelle 24h/7j/1m est rendue EN TÊTE de chaque actif :
    après « ### {nom} » et AVANT la 1ʳᵉ ligne de tableau. L'ancienne ligne
    « - Scores : » placée après le tableau (redondante) a été retirée."""
    r = sa.score_actif("a", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.nom = "ActifSynth"
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    detail = b.split("## Détail par actif")[1]

    # Ordre : ### nom  <  synthèse (24h : … · 7j : … · 1m : …)  <  en-tête tableau
    idx_titre = detail.index("### ActifSynth")
    idx_synth = detail.index("**24h : ", idx_titre)
    idx_table = detail.index("| Critère | Comment c'est lu |", idx_titre)
    assert idx_titre < idx_synth < idx_table, "synthèse doit être entre titre et tableau"

    # La synthèse reprend les 3 horizons avec direction + note signée 2 décimales.
    synth_line = next(l for l in detail.splitlines() if l.startswith("**24h : "))
    for h in ("24h", "7j", "1m"):
        assert f"{h} : " in synth_line
        assert f"{r.scores[h]:+.2f}" in synth_line
    assert " · " in synth_line  # séparateurs cohérents avec le style du bulletin

    # Ancienne ligne « - Scores : » (après tableau) supprimée → plus de doublon.
    assert "- Scores : 24h=" not in detail


# ===========================================================================
# Bloc 1 — « 🎯 À jouer aujourd'hui (24h) » (audit UX 10/06)
# ===========================================================================

def _actif_24h(nom: str, score_24h: float, confidence: str = "normale") -> "sa.ActifResult":
    """ActifResult minimal avec un score 24h imposé (présentation pure)."""
    r = sa.score_actif(nom.lower(), _fiche(quant_poids=10), _vals(1.0))
    r.nom = nom
    r.scores = {"24h": score_24h, "7j": score_24h, "1m": score_24h}
    direction = "LONG" if score_24h >= 0 else "SHORT"
    r.conclusions = {h: direction for h in sa.HORIZONS}
    r.confidence = {h: confidence for h in sa.HORIZONS}
    return r


def test_a_jouer_present_et_24h_seulement():
    """Le bloc « À jouer aujourd'hui (24h) » est en tête, avant Top multi-horizons
    et Synthèse, et porte les colonnes attendues."""
    r = _actif_24h("Fort", 8.0)
    b = sa.render_bulletin([r], {}, NOW, "h", "ok")
    assert "## 🎯 À jouer aujourd'hui (24h)" in b
    assert "| Actif | Direction | Note | Conviction | Drapeaux | Prix de réf. |" in b
    assert "**Jouables**" in b and "**À éviter**" in b
    assert b.index("## 🎯 À jouer aujourd'hui (24h)") < b.index("## 🎯 Top convictions multi-horizons")


def test_a_jouer_tri_note_decroissante():
    """Les cellules jouables sont triées par |note| décroissante."""
    faible = _actif_24h("Faible", 1.0)
    fort = _actif_24h("Fort", 9.0)
    moyen = _actif_24h("Moyen", 4.0)
    block = sa.build_a_jouer_block([faible, fort, moyen], NOW)
    txt = "\n".join(block)
    jouables = txt.split("**Jouables**")[1].split("**À éviter**")[0]
    i_fort = jouables.index("| Fort |")
    i_moyen = jouables.index("| Moyen |")
    i_faible = jouables.index("| Faible |")
    assert i_fort < i_moyen < i_faible


def test_a_jouer_scinde_jouables_vs_a_eviter():
    """⚪ (coin-flip <0.05), ≈ (quasi-neutre <0.30) et 🚫 (insuffisant) vont dans
    « À éviter » ; une note franche reste dans « Jouables » même avec un ◧."""
    jouable = _actif_24h("Franche", 8.0)
    coinflip = _actif_24h("CoinFlip", 0.01)     # ⚪
    neutre = _actif_24h("QuasiNeutre", 0.20)    # ≈
    insuff = _actif_24h("Insuff", 0.0)
    insuff.conclusions = {h: sa.CONCLUSION_INSUFFISANT for h in sa.HORIZONS}
    block = sa.build_a_jouer_block([jouable, coinflip, neutre, insuff], NOW)
    txt = "\n".join(block)
    jouables = txt.split("**Jouables**")[1].split("**À éviter**")[0]
    a_eviter = txt.split("**À éviter**")[1]
    assert "| Franche |" in jouables
    assert "| CoinFlip |" in a_eviter and "⚪" in a_eviter
    assert "| QuasiNeutre |" in a_eviter and "≈" in a_eviter
    assert "| Insuff |" in a_eviter


def test_a_jouer_prix_absent_tiret():
    """Sans prix de référence stampé → « — » (zéro invention)."""
    r = _actif_24h("Fort", 8.0)
    block = sa.build_a_jouer_block([r], NOW, prix_reference=None)
    ligne = next(l for l in block if l.startswith("| Fort |"))
    assert ligne.rstrip().endswith("| — |")


def test_a_jouer_prix_present_affiche():
    """Avec un prix stampé (clé = fiche_key) → la valeur s'affiche."""
    r = _actif_24h("Fort", 8.0)
    block = sa.build_a_jouer_block([r], NOW, prix_reference={r.fiche_key: 123.45})
    ligne = next(l for l in block if l.startswith("| Fort |"))
    assert "123.45" in ligne


# ===========================================================================
# Bloc 1b — Top convictions multi-horizons AVEC drapeaux
# ===========================================================================

def test_top_multi_horizons_affiche_drapeaux():
    """Une cellule mono-critère dominante (◧) du top affiche son drapeau (le bug
    EUR/USD 7j ◧ affiché sans avertissement — corrigé)."""
    # Fiche 1 seul critère → mono-critère dominant garanti → ◧.
    r = sa.score_actif("eurusd", _fiche(quant_poids=12), _vals(1.0))
    r.nom = "EUR/USD"
    r.scores = {"24h": 11.0, "7j": 20.0, "1m": 19.0}
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    block = sa.build_top_multi_horizons_block([r])
    txt = "\n".join(block)
    assert "EUR/USD 7j" in txt
    assert "drapeaux :" in txt and "◧" in txt


def test_top_multi_horizons_ligne_driver_partage():
    """Si ≥ 2 convictions du top partagent le même driver dominant → ligne ⚭."""
    actifs = []
    # 3 actifs distincts, tous portés par le MÊME critère (même cle_courante).
    for nom in ("ActifA", "ActifB", "ActifC"):
        r = sa.score_actif(nom.lower(), _fiche(quant_poids=10), _vals(1.0))
        r.nom = nom
        r.scores = {"24h": 8.0, "7j": 6.0, "1m": 4.0}
        r.confidence = {h: "normale" for h in sa.HORIZONS}
        actifs.append(r)
    block = sa.build_top_multi_horizons_block(actifs, shared_summary=[{"x": 1}])
    txt = "\n".join(block)
    assert "⚭" in txt
    assert "reposent sur le même driver" in txt


# ===========================================================================
# Bloc 3 — Flips de bruit drapeautés ⚪/≈
# ===========================================================================

def test_flips_bruit_drapeau():
    """Un flip à note quasi-nulle est drapeauté ⚪ (coin-flip) ou ≈ (quasi-neutre)."""
    r = sa.score_actif("test", _fiche(quant_poids=10), _vals(1.0))
    r.nom = "TestActif"
    r.scores = {"24h": 0.01, "7j": 0.01, "1m": 0.01}   # ⚪ quasi coin-flip
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    veille = {"testactif": {"24h": "SHORT", "7j": "SHORT", "1m": "SHORT"}}
    b = sa.render_bulletin([r], veille, NOW, "h", "ok")
    flips = b.split("## Flips vs veille")[1].split("##")[0]
    assert "SHORT → LONG" in flips
    assert "⚪" in flips


# ===========================================================================
# Bloc 4 — métadonnées techniques déplacées en pied
# ===========================================================================

def test_metadata_en_pied_pas_en_tete():
    """Version Analyste + hash en PIED (après ---), plus en tête ; Fraîcheur en tête."""
    r = _actif_24h("Fort", 8.0)
    b = sa.render_bulletin([r], {}, NOW, "abcd1234", "fraîcheur OK")
    # En-tête : Généré + Fraîcheur, PAS de « Analyste version » / « Fiches hash ».
    tete = b.split("## 🎯 À jouer aujourd'hui (24h)")[0]
    assert "- Fraîcheur" in tete
    assert "Analyste version" not in tete
    assert "Fiches hash" not in tete
    # Pied : section --- + métadonnées techniques.
    assert "_Analyste version : v3.0.0 · Fiches hash : abcd1234_" in b
    assert b.index("_Analyste version") > b.index("## 🎯 À jouer aujourd'hui (24h)")


# ===========================================================================
# Bloc 5 — Conviction EXPLICITE (audit UX 2026-06-11)
#   Renommage d'affichage SEUL : mêmes conditions, mêmes seuils que l'ancien
#   « forte »/« faible ». On vérifie chaque libellé + l'ordre de priorité.
# ===========================================================================

SEUIL = 0.6  # seuil par défaut (bilan_jour KO → 0.6, cf. build_a_jouer_block)


def test_conviction_forte():
    """|score| ≥ seuil + aucun drapeau → « forte »."""
    # Fiche 2 critères équilibrés → pas de mono (◧) ; score franc, pas de divergence.
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.scores = {"24h": 8.0, "7j": 8.0, "1m": 8.0}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    assert sa._conviction_cell(r, "24h", SEUIL) == "forte"


def test_conviction_molle_score_faible():
    """|score| < NEUTRAL_BAND → « molle (score faible) »."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.scores = {"24h": 0.20, "7j": 0.20, "1m": 0.20}  # < 0.30
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    assert sa._conviction_cell(r, "24h", SEUIL) == "molle (score faible)"


def test_conviction_molle_entre_neutral_et_seuil():
    """NEUTRAL_BAND ≤ |score| < seuil, sans drapeau → « molle (score faible) »
    (ancien « faible » non dégradé)."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.scores = {"24h": 0.45, "7j": 0.45, "1m": 0.45}  # 0.30 ≤ 0.45 < 0.6
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    assert sa._conviction_cell(r, "24h", SEUIL) == "molle (score faible)"


def test_conviction_contestee_divergence():
    """Divergence quant↔news (↯) → « contestée (news à contre-sens) »."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.scores = {"24h": 8.0, "7j": 8.0, "1m": 8.0}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.divergence_quant_news = {"24h": True, "7j": False, "1m": False}
    assert sa._conviction_cell(r, "24h", SEUIL) == "contestée (news à contre-sens)"


def test_conviction_fragile_mono_critere():
    """Mono-critère dominant (◧) → « fragile (1 seul critère) »."""
    # Fiche à 1 seul critère → mono-dominant garanti.
    r = sa.score_actif("test", _fiche(quant_poids=12), _vals(1.0))
    r.scores = {"24h": 8.0, "7j": 8.0, "1m": 8.0}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    assert sa._conviction_cell(r, "24h", SEUIL) == "fragile (1 seul critère)"


def test_conviction_zigzag_horizons():
    """Incohérence inter-horizons (⇆) → « zigzag horizons »."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.scores = {"24h": 8.0, "7j": 8.0, "1m": 8.0}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.incoherence_inter_horizons = True
    assert sa._conviction_cell(r, "24h", SEUIL) == "zigzag horizons"


def test_conviction_insuffisant():
    """INSUFFISANT → « — »."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.conclusions = {h: sa.CONCLUSION_INSUFFISANT for h in sa.HORIZONS}
    assert sa._conviction_cell(r, "24h", SEUIL) == "—"


def test_conviction_priorite_molle_avant_contestee():
    """Priorité : molle > contestée. Si |score| < NEUTRAL_BAND ET divergence,
    on affiche « molle » (la plus disqualifiante)."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(1.0, 1.0))
    r.scores = {"24h": 0.20, "7j": 0.20, "1m": 0.20}  # < 0.30
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.divergence_quant_news = {"24h": True, "7j": True, "1m": True}
    assert sa._conviction_cell(r, "24h", SEUIL) == "molle (score faible)"


def test_conviction_priorite_contestee_avant_fragile():
    """Priorité : contestée > fragile. Fiche mono-critère (◧) + divergence (↯)
    → on affiche « contestée » (plus disqualifiante que la fragilité)."""
    r = sa.score_actif("test", _fiche(quant_poids=12), _vals(1.0))  # mono garanti
    r.scores = {"24h": 8.0, "7j": 8.0, "1m": 8.0}
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.divergence_quant_news = {"24h": True, "7j": True, "1m": True}
    assert sa._conviction_cell(r, "24h", SEUIL) == "contestée (news à contre-sens)"


def test_a_jouer_libelle_explicite_dans_table():
    """Le tableau « À jouer » affiche le libellé explicite, pas « faible »."""
    fort = _actif_24h("Fort", 8.0)
    block = sa.build_a_jouer_block([fort], NOW, seuil_conviction=SEUIL)
    txt = "\n".join(block)
    assert "forte" in txt
    assert "| faible |" not in txt  # plus de libellé binaire « faible »


# ===========================================================================
# Bloc 6 — Phrase d'explication déterministe sous chaque top conviction
# ===========================================================================

def test_top_explication_top2_criteres():
    """La phrase cite les 2 critères à plus forte |contribution| (nom + valeur
    signée), du plus fort au moins fort."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(3.0, 1.0))
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    phrase = sa._top_explication(r, "24h")
    assert phrase.startswith("_Porté par QuantA (") and "QuantB (" in phrase
    # QuantA (val 3) cité avant QuantB (val 1).
    assert phrase.index("QuantA") < phrase.index("QuantB")
    assert phrase.endswith("._")


def test_top_explication_news_contre_sens():
    """Divergence quant↔news → mention « news en sens inverse (↯) »."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(2.0, 1.0))
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.divergence_quant_news = {"24h": True, "7j": False, "1m": False}
    phrase = sa._top_explication(r, "24h")
    assert "news en sens inverse (↯)" in phrase
    assert "📰" not in phrase  # exclusif avec ↯


def test_top_explication_porte_par_news():
    """News dominantes et alignées avec la conclusion → « porté par les news 📰 »."""
    fiche = {
        "actif": "TestActif",
        "criteres": [
            {"id": 1, "nom": "Quant", "cle_courante": "q", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": 1, "poids": 3,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 2, "nom": "NewsGeo", "cle_courante": "ng", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": 1, "poids": 12,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
        ],
    }
    vals = {
        "q": {"valeur": 1.0, "source_track": "twelvedata"},
        "ng": {"valeur": 1.0, "source_track": "ia_synthese"},
    }
    r = sa.score_actif("test", fiche, vals)
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    r.divergence_quant_news = {h: False for h in sa.HORIZONS}
    phrase = sa._top_explication(r, "24h")
    assert "porté par les news 📰" in phrase
    assert "↯" not in phrase


def test_top_explication_vide_si_aucun_contributeur():
    """Aucune contribution réelle → phrase vide (zéro invention)."""
    r = sa.score_actif("test", _fiche_equilibree(), _vals2(0.0, 0.0))
    r.conclusions = {h: "LONG" for h in sa.HORIZONS}
    assert sa._top_explication(r, "24h") == ""
