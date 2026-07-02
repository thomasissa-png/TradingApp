"""Vague RENDU 01/07 — 17 corrections de PRÉSENTATION du bulletin analyste.

Tests MOCKÉS (aucun run du pipeline, `v3/data/` intact). Chaque test cible UN
point des 17 corrections validées fondateur (références = bulletin 2026-07-01).
Zéro changement de direction/note/seuil : PRÉSENTATION uniquement.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 7, 1, 7, 0, tzinfo=timezone.utc)
SEUIL = 0.6


# ---------------------------------------------------------------------------
# Fakes légers pour les fonctions de rendu pures (driver / raison / news)
# ---------------------------------------------------------------------------
class _C:
    def __init__(self, nom, cle, ctr24, *, source_track="twelvedata",
                 signe=1, valeur_brute=0.0, is_gate=False, is_na=False):
        self.nom = nom
        self.cle_courante = cle
        self.contributions = {"24h": ctr24, "7j": ctr24, "1m": ctr24}
        self.source_track = source_track
        self.signe = signe
        self.valeur_brute = valeur_brute
        self.is_gate = is_gate
        self.is_na = is_na


class _R:
    def __init__(self, nom, criteres, conc="LONG", score=5.0):
        self.nom = nom
        self.fiche_key = nom.lower()
        self.criteres = criteres
        self.conclusions = {h: conc for h in sa.HORIZONS}
        self.scores = {h: score for h in sa.HORIZONS}
        self.divergence_quant_news = {h: False for h in sa.HORIZONS}
        self.contre_momentum = {h: False for h in sa.HORIZONS}
        self.incoherence_inter_horizons = False
        self.news_cap_info = {}
        self.scores_pond = dict(self.scores)
        self.conclusions_pond = dict(self.conclusions)


def _news_c(ctr24, valeur_brute=1.0):
    """Critère porteur du NET news (source_track ia_synthese → SYNTHESE_NET_LABEL)."""
    return _C("Synthèse news (net, IA)", "news_net", ctr24,
              source_track="ia_synthese", valeur_brute=valeur_brute)


# ===========================================================================
# Point 1 — « news net … (pas de titre représentatif aujourd'hui) » INTERDITE
# ===========================================================================
def test_p1_phrase_pas_de_titre_interdite_et_bascule_driver(monkeypatch):
    # Aucun titre montrable dans l'events-log.
    monkeypatch.setattr(sa, "_dominant_news_for_actif", lambda now: {})
    r = _R("Cacao", [
        _news_c(+3.20),                                   # driver net news dominant
        _C("Tendance du cacao (20 jours)", "trend20", +0.50,
           source_track="twelvedata", valeur_brute=0.357),  # driver concret non-news
    ])
    # _enrich seul : plus jamais la phrase interdite (sentinelle « news net … »).
    label = sa._enrich_net_news_label(sa.SYNTHESE_NET_LABEL, r, NOW)
    assert "pas de titre représentatif" not in label
    assert sa._est_news_sans_titre(label)
    # La raison AFFICHÉE bascule sur le driver concret non-news (zéro invention).
    detail = sa._driver_detail(r, "24h", NOW)
    assert "Tendance du cacao" in detail
    assert "pas de titre représentatif" not in detail
    raison = sa._raison_pari_affichee(r, "24h", NOW)
    assert "Tendance du cacao" in raison
    assert "pas de titre représentatif" not in raison


# ===========================================================================
# Point 2 — cohérence : news baissière ne peut pas afficher une raison haussière
# ===========================================================================
def test_p2_news_baissiere_jamais_raison_haussiere(monkeypatch):
    monkeypatch.setattr(
        sa, "_dominant_news_for_actif",
        lambda now: {"Petrole": ("baissière", "Cessez-le-feu lève le blocus")},
    )
    r = _R("Petrole", [_news_c(-5.60)], conc="SHORT", score=-5.60)
    label = sa._enrich_net_news_label(sa.SYNTHESE_NET_LABEL, r, NOW)
    assert "baissière" in label and "haussière" not in label


# ===========================================================================
# Point 3 — « Porté par » jamais à contre-sens de la direction
# ===========================================================================
def test_p3_porte_par_jamais_contresens(monkeypatch):
    monkeypatch.setattr(sa, "_dominant_news_for_actif", lambda now: {})
    # LONG : la news (-5.60, plus forte en |contrib|) est à CONTRE-SENS → on cite
    # le driver positif (quant +2.0), pas la news négative.
    r = _R("Petrole", [
        _news_c(-5.60),
        _C("Stocks Cushing", "cushing", +2.10, valeur_brute=18957),
    ], conc="LONG", score=0.13)
    detail = sa._driver_detail(r, "24h", NOW)
    assert "Cushing" in detail
    assert "contribue +2.10" in detail
    assert "-5.60" not in detail


# ===========================================================================
# Point 4 + 9 — colonne « Note » (chiffre) + colonne « Objectif » (seuil)
# ===========================================================================
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


def _make(nom, score24, conc=None):
    r = sa.score_actif(nom.lower(), _fiche(), _vals(1.0))
    r.nom = nom
    r.fiche_key = nom.lower()
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    r.coverage = 1.0
    if conc is None:
        conc = "LONG" if score24 >= 0 else "SHORT"
    r.conclusions = dict(r.conclusions); r.conclusions["24h"] = conc
    r.scores = dict(r.scores); r.scores["24h"] = score24
    return r


def test_p4_p9_paris_colonnes_note_et_objectif():
    res = [_make("Cafe", 8.77)]
    fiches = {"cafe": {"seuils_reussite_pct": {"24h": 1.0, "7j": 3.0, "1m": 7.0}}}
    block = "\n".join(sa.build_paris_du_jour_block(
        res, NOW, seuil_conviction=SEUIL, fiches=fiches))
    # Point 4 : la colonne chiffrée s'appelle « Note » ; plus « Conviction » chiffrée.
    assert "| Actif | Sens | Prix d'entrée | Objectif | Note | Pourquoi |" in block
    # Point 9 : objectif = seuil 24h signé par le sens (LONG → +1.0 %).
    assert "+1.0 %" in block


# ===========================================================================
# Point 5 — « forte » exige |intensité| >= 0.30, sinon « modérée (signal peu net) »
# ===========================================================================
def test_p5_forte_exige_intensite_nette(monkeypatch):
    r = _make("Argent", -1.92, conc="SHORT")  # note franche mais intensité faible
    monkeypatch.setattr(sa, "_intensite_sous_plancher", lambda rr, h, **k: True)
    assert sa._conviction_cell(r, "24h", SEUIL) == "modérée (signal peu net)"
    monkeypatch.setattr(sa, "_intensite_sous_plancher", lambda rr, h, **k: False)
    assert sa._conviction_cell(r, "24h", SEUIL) == "forte"


def test_p5_seuil_aligne_sur_selection():
    assert sa.SELECTION_INTENSITE_MIN == 0.30


# ===========================================================================
# Point 6 — « Cellules à surveiller » réduite à Sélection + flips
# ===========================================================================
def test_p6_surveillance_reduite_selection_et_flips(monkeypatch):
    r = sa.score_actif("or", _fiche(), _vals(1.0))
    r.nom = "Or"; r.fiche_key = "or"
    r.confidence = {h: "normale" for h in sa.HORIZONS}
    r.divergence_quant_news = {"24h": True, "7j": False, "1m": False}  # ↯ 24h
    r.contre_momentum = {h: False for h in sa.HORIZONS}
    r.incoherence_inter_horizons = False
    # Ni Sélection ni flip → la cellule à alerte est FILTRÉE (point 6).
    hors = sa.build_surveillance_block([r], NOW, selection_keys=set(), flip_cells=set())
    assert "Or 24h" not in "\n".join(hors)
    # Flip du jour sur 24h → la cellule REMONTE.
    dans = sa.build_surveillance_block(
        [r], NOW, selection_keys=set(), flip_cells={("or", "24h")})
    assert "Or 24h" in "\n".join(dans)
    # Ligne d'intro renvoyant au decision-log présente en mode filtré.
    assert "decision-log" in "\n".join(dans)


# ===========================================================================
# Point 7 — tout symbole rendu figure dans la légende (dont ⚠️♻)
# ===========================================================================
def test_p7_legende_contient_reportee():
    leg = sa._build_legende({"⚠️♻"})
    assert "⚠️♻" in leg
    assert "valeur reportée" in leg


def test_p7_tout_symbole_de_surveillance_est_dans_la_legende():
    # Chaque symbole émis par _compute_cell_risk_flags DOIT avoir une entrée légende.
    defs = {sym for sym, _ in sa._LEGENDE_DEFS}
    for sym in sa.SURVEILLANCE_FLAGS.values():
        assert sym in defs, f"symbole {sym!r} rendu mais absent de la légende"


# ===========================================================================
# Point 8 — note de bas de tableau pour le drapeau ⌛ sur un pari
# ===========================================================================
def test_p8_note_bas_tableau_deja_cote(monkeypatch):
    res = [_make("Cafe", 8.77)]
    monkeypatch.setattr(sa, "_synthese_cell_risk_flags",
                        lambda r, h, now: ["⌛"])
    block = "\n".join(sa.build_paris_du_jour_block(res, NOW, seuil_conviction=SEUIL))
    assert "**Cafe** ⌛" in block
    assert "déjà dans les prix" in block


# ===========================================================================
# Point 10 — « (écarté des paris) » sur une cellule jouable écartée de la Sélection
# ===========================================================================
def test_p10_mention_ecarte_des_paris(monkeypatch):
    res = [_make("Or", -16.69, conc="SHORT")]  # forte mais news high à contre-sens
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", lambda now: {"Or": {"LONG"}})
    block = "\n".join(sa.build_a_jouer_block(res, NOW, seuil_conviction=SEUIL))
    assert "(écarté des paris)" in block


# ===========================================================================
# Point 11 — paradoxe net vs top-titre expliqué en une parenthèse
# ===========================================================================
def test_p11_paradoxe_net_vs_titre(monkeypatch):
    monkeypatch.setattr(
        sa, "_dominant_news_for_actif",
        lambda now: {"Cuivre": ("baissière", "Chine ralentit")},
    )
    r = _R("Cuivre", [_news_c(+4.00)], conc="LONG", score=4.00)  # net haussier
    label = sa._enrich_net_news_label(sa.SYNTHESE_NET_LABEL, r, NOW)
    assert "news globalement haussières mais un titre majeur baissier" in label
    assert "pas de titre représentatif" not in label


# ===========================================================================
# Point 12 — aucune mention « à valider » dans les chaînes affichées
# ===========================================================================
def test_p12_aucune_mention_a_valider():
    res = [_make("Cafe", 8.77), _make("Or", -6.03, conc="SHORT")]
    bulletin = sa.render_bulletin(res, {}, NOW, "07h", "ok")
    assert "à valider" not in bulletin


# ===========================================================================
# Point 13 — jargon « val …, sens normal » → forme humaine + zscore_abs traduit
# ===========================================================================
def test_p13_valeur_humaine_et_zscore_abs():
    assert sa._fmt_val_humaine(0.08568) == "0.086"
    assert sa._fmt_val_humaine(162.7) == "162.7"
    assert sa._label_type_norm("zscore_abs") == "Écart à la normale (dans les deux sens)"


# ===========================================================================
# Point 14 — tirets cadratins retirés des NOMS de critères affichés
# ===========================================================================
def test_p14_noms_criteres_sans_tiret_cadratin():
    assert sa._clean_nom_critere("Météo Brésil — écart à la normale") == \
        "Météo Brésil : écart à la normale"
    # Passe aussi par le funnel d'affichage.
    assert sa._nom_affiche("Météo Brésil — écart à la normale", "twelvedata") == \
        "Météo Brésil : écart à la normale"


# ===========================================================================
# Point 15 — « référence dégradée … » → « (prix de référence approximatif) »
# ===========================================================================
def test_p15_label_prix_reference_approximatif():
    src = ROOT / "scripts" / "scoring_analyste.py"
    txt = src.read_text(encoding="utf-8")
    assert "(prix de référence approximatif)" in txt
    assert "référence dégradée : source non canonique" not in txt


# ===========================================================================
# Point 17a — la table « Intensité comparable entre actifs » est supprimée
# ===========================================================================
def test_p17a_table_intensite_supprimee():
    res = [_make("Cafe", 8.77), _make("Or", -6.03, conc="SHORT")]
    bulletin = sa.render_bulletin(res, {}, NOW, "07h", "ok")
    assert "## Intensité comparable entre actifs" not in bulletin
    # La Synthèse reste la table centrale.
    assert "## Synthèse des décisions" in bulletin


# ===========================================================================
# Point 17b — « Détail par actif » replié par défaut (build_html)
# ===========================================================================
def test_p17b_detail_par_actif_replie_par_defaut():
    txt = (ROOT / "scripts" / "build_html.py").read_text(encoding="utf-8")
    # Le pattern de repli par défaut (FOLD_SECTION_PATTERNS) référence « détail …
    # actif » → la section « Détail par actif » est repliée par défaut sur la page.
    assert "FOLD_SECTION_PATTERNS" in txt
    i = txt.index("FOLD_SECTION_PATTERNS")
    fold_block = txt[i:i + 800]
    assert "détail" in fold_block and "actif" in fold_block
