"""Tests — « 🎯 Sélection du jour — max 3 » + capteurs shadow 24h (décision
fondateur 12/06). ZÉRO cutover : on vérifie l'affichage + la mesure + le shadow,
JAMAIS un changement de score/conclusion.

Couverture :
- règles de sélection (forte + couverture ≥ 0.70 + dédup driver + max 3) ;
- cas « aucune sélection » ;
- champs decision-log (selection_du_jour / selection_motif_exclusion) ;
- shadow_retour_j1 / shadow_gap_overnight calculés et None propres ;
- WR Sélection au bilan (synthétique) ;
- avertissement catalyseur J0.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

import pytest

import scoring_analyste as sa


# ---------------------------------------------------------------------------
# Fabriques minimales (zéro dépendance réseau / YAML)
# ---------------------------------------------------------------------------

def _crit(nom: str, cle: str, contrib: float, h_contrib: Optional[Dict[str, float]] = None) -> sa.CritereResult:
    contributions = h_contrib or {h: contrib for h in sa.HORIZONS}
    return sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="lineaire",
        valeur_brute=1.0,
        valeur_norm=1.0,
        # poids=1/3 : `_actif` monte 3 critères → dénominateur d'intensité (note
        # normalisée) = 3 × (1/3) × pertinence 1.0 = 1.0 → intensité ≡ |score| pour
        # ces mocks. Le plancher d'intensité 24h (règle 01/07) coïncide alors avec
        # NEUTRAL_BAND (déjà exigé) → aucun sur-filtrage, scénarios inchangés.
        poids=1.0 / 3.0,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions=contributions,
        cle_courante=cle,
    )


def _actif(
    nom: str,
    fiche_key: str,
    *,
    score_24h: float,
    direction: str = "LONG",
    coverage: float = 1.0,
    driver_cle: str = "drv_a",
    driver_nom: str = "Critère A",
) -> sa.ActifResult:
    """ActifResult dont la cellule 24h est « forte ».

    Trois critères : le driver attendu est STRICTEMENT le plus contributeur (top
    déterministe) mais reste sous 50 % du total → ni mono-dominant (pas
    « fragile »), ni quasi-neutre si |score| ≥ seuil → conviction « forte »."""
    c_top = _crit(driver_nom, driver_cle, 0.40)
    c_b = _crit("autre b", "drv_b", 0.33)
    c_c = _crit("autre c", "drv_c", 0.33)
    return sa.ActifResult(
        nom=nom,
        fiche_key=fiche_key,
        criteres=[c_top, c_b, c_c],
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (direction if h == "24h" else sa.CONCLUSION_INSUFFISANT) for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=coverage,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


_NOW = datetime(2026, 6, 12, 7, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _isole_news_flux(monkeypatch):
    """Isole les tests de sélection de l'events-log LIVE : par défaut AUCUNE news
    adverse (le veto news↯ lit la vraie events-log via bilan_jour.cause_news_high_dir,
    sinon les tests dépendraient des données du jour). Les tests du veto
    re-monkeypatchent cette fonction APRÈS le fixture (l'override prime)."""
    import bilan_jour as bj
    monkeypatch.setattr(bj, "cause_news_high_dir", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", lambda now: {}, raising=False)


# ---------------------------------------------------------------------------
# Règles de sélection
# ---------------------------------------------------------------------------

def test_selection_garde_forte_couverture_ok():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    sel, ecart = sa.compute_selection_du_jour([a])
    assert [s["fiche_key"] for s in sel] == ["or"]
    assert ecart == []


def test_selection_exclut_couverture_insuffisante():
    # |note| forte mais couverture 0.69 < 0.70 → écartée (pas dans la sélection).
    a = _actif("Or", "or", score_24h=0.9, coverage=0.69)
    sel, _ = sa.compute_selection_du_jour([a])
    assert sel == []


def test_selection_exclut_conviction_non_forte():
    # |note| sous le seuil (0.6) → conviction « molle » → exclue.
    a = _actif("Or", "or", score_24h=0.4)
    assert sa._conviction_cell(a, "24h", 0.6) != "forte"
    sel, _ = sa.compute_selection_du_jour([a])
    assert sel == []


def test_selection_dedup_meme_driver_meme_direction():
    # Deux actifs LONG sur le même driver → on garde la plus forte, l'autre écartée.
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_macro", driver_nom="Fed")
    faible = _actif("Argent", "argent", score_24h=0.7, driver_cle="drv_macro", driver_nom="Fed")
    sel, ecart = sa.compute_selection_du_jour([fort, faible])
    assert [s["fiche_key"] for s in sel] == ["or"]
    assert len(ecart) == 1
    assert ecart[0]["fiche_key"] == "argent"
    # Famille SINGLETON (drv_macro inconnu de la table) : le label = la clé brute.
    assert ecart[0]["motif"] == "même pari (drv_macro) que Or"


def test_selection_pas_de_dedup_si_direction_opposee():
    # Même driver mais directions opposées → ce N'EST PAS le même pari.
    a = _actif("Or", "or", score_24h=0.9, direction="LONG", driver_cle="drv_macro")
    b = _actif("Argent", "argent", score_24h=-0.9, direction="SHORT", driver_cle="drv_macro")
    sel, ecart = sa.compute_selection_du_jour([a, b])
    assert {s["fiche_key"] for s in sel} == {"or", "argent"}
    assert ecart == []


def test_selection_max_3():
    actifs = [
        _actif(f"A{i}", f"a{i}", score_24h=0.9 - i * 0.01, driver_cle=f"drv_{i}")
        for i in range(5)
    ]
    sel, ecart = sa.compute_selection_du_jour(actifs)
    assert len(sel) == 3
    # Les 2 surnuméraires sont « hors top 3 ».
    assert all(e["motif"] == "hors top 3" for e in ecart)
    assert len(ecart) == 2


def test_selection_tri_note_decroissante():
    a = _actif("Faible", "f", score_24h=0.65, driver_cle="d1")
    b = _actif("Fort", "fo", score_24h=0.95, driver_cle="d2")
    sel, _ = sa.compute_selection_du_jour([a, b])
    assert [s["fiche_key"] for s in sel] == ["fo", "f"]


def test_selection_aucune_si_rien_ne_passe():
    a = _actif("Or", "or", score_24h=0.4)  # molle
    b = _actif("Argent", "argent", score_24h=0.9, coverage=0.5)  # couverture KO
    sel, _ = sa.compute_selection_du_jour([a, b])
    assert sel == []


# ---------------------------------------------------------------------------
# Bloc bulletin
# ---------------------------------------------------------------------------

def test_bloc_aucune_selection_message():
    a = _actif("Or", "or", score_24h=0.4)
    lignes = sa.build_selection_du_jour_block([a], _NOW)
    texte = "\n".join(lignes)
    # Refonte S9 vague 3 : la Sélection ouvre désormais « ## 🎯 Décision du jour »
    # comme encart « ### Sélection (max 3) » (fusion I11). Même intention : le bloc
    # porte bien le titre de section + le sous-titre Sélection.
    assert "## 🎯 Décision du jour" in texte
    assert "### Sélection (max 3)" in texte
    assert "Aucune sélection aujourd'hui" in texte
    assert "ne pas forcer" in texte


def test_bloc_tableau_et_ecartee(monkeypatch):
    # On neutralise le calendrier (J0) pour isoler le rendu du tableau/dédup.
    monkeypatch.setattr(sa, "_catalyseurs_j0_high", lambda now: [])
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_macro", driver_nom="Fed")
    faible = _actif("Argent", "argent", score_24h=0.7, driver_cle="drv_macro", driver_nom="Fed")
    lignes = sa.build_selection_du_jour_block(
        [fort, faible], _NOW, prix_reference={"or": 2400.0},
    )
    texte = "\n".join(lignes)
    # P3 — « Porté par » enrichi : nom complet + valeur + sens + contribution.
    # [Point 13 — 01/07] Forme humaine (« valeur X », phrase de sens).
    assert "| Or | LONG | +0.90 | Fed (valeur 1, la hausse pousse à la hausse) → contribue +0.40 | 2400 |" in texte
    assert "écartée : Argent, même pari (drv_macro) que Or" in texte
    # P2 — les 4 règles de sélection sont désormais dans « Comment lire les
    # scores » (consolidées une fois), plus dans le bloc « Sélection du jour ».
    assert "**signal fort**" not in texte
    pedago = "\n".join(sa.build_comment_lire_block(set()))
    assert "**signal fort**" in pedago
    assert "chaque type de marché représenté une seule fois" in pedago


def test_bloc_avertissement_catalyseur_j0(monkeypatch):
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")

    def _fake_cat(now):
        return [{"nom": "Inflation US (CPI)", "actifs": ["or"], "impact": "high"}]

    monkeypatch.setattr(sa, "_catalyseurs_j0_high", _fake_cat)
    lignes = sa.build_selection_du_jour_block([fort], _NOW)
    texte = "\n".join(lignes)
    assert "⚠️" in texte
    assert "Inflation US (CPI) aujourd'hui" in texte
    assert "peut retourner ce pari" in texte
    assert "Or" in texte


def test_bloc_catalyseur_ignore_si_actif_non_selectionne(monkeypatch):
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")

    def _fake_cat(now):
        # CPI concerne sp500, PAS l'or sélectionné → aucun avertissement.
        return [{"nom": "Inflation US (CPI)", "actifs": ["sp500"], "impact": "high"}]

    monkeypatch.setattr(sa, "_catalyseurs_j0_high", _fake_cat)
    texte = "\n".join(sa.build_selection_du_jour_block([fort], _NOW))
    assert "⚠️" not in texte


# ---------------------------------------------------------------------------
# Decision-log (Étage 1b)
# ---------------------------------------------------------------------------

def test_decision_log_selection_du_jour_true():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r.get("horizon") == "24h")
    assert rec_24h["selection_du_jour"] is True
    assert "selection_motif_exclusion" not in rec_24h
    # Hors 24h : champ absent (la sélection est définie sur le pari 24h).
    rec_7j = next(r for r in records if r.get("horizon") == "7j")
    assert "selection_du_jour" not in rec_7j


def test_decision_log_selection_motif_exclusion():
    """UNE SEULE sélection (refonte 23/06) : le decision-log dérive de
    `select_paris_du_jour` (Option C, top 3 par |note|, PAS de dédup famille).
    Avec 4 actifs jouables, les 3 plus forts sont sélectionnés et le 4e est
    écarté avec le motif « hors top 3 »."""
    a = _actif("Or", "or", score_24h=0.9)
    b = _actif("Argent", "argent", score_24h=0.8)
    c = _actif("Cacao", "cacao", score_24h=0.75)
    d = _actif("Café", "cafe", score_24h=0.65)  # 4e par |note| → hors top 3
    records = sa.build_decision_log_records([a, b, c, d], _NOW)

    def _rec(actif):
        return next(r for r in records if r["actif"] == actif and r.get("horizon") == "24h")

    assert _rec("Or")["selection_du_jour"] is True
    assert _rec("Argent")["selection_du_jour"] is True
    assert _rec("Cacao")["selection_du_jour"] is True
    assert _rec("Café")["selection_du_jour"] is False
    assert _rec("Café")["selection_motif_exclusion"] == "hors top 3"
    # Pas de dédup famille macro au decision-log : Or et Argent (même driver par
    # défaut) sont TOUS DEUX sélectionnés (cohérence avec la tête approuvée).


def test_decision_log_selection_false_quand_non_selectionnee():
    """Une cellule jouable surnuméraire (au-delà du top 3) → selection_du_jour
    False + motif « hors top 3 ». Source = `select_paris_du_jour`."""
    forts = [
        _actif("Or", "or", score_24h=0.9),
        _actif("Argent", "argent", score_24h=0.8),
        _actif("Cacao", "cacao", score_24h=0.7),
    ]
    surnumeraire = _actif("Café", "cafe", score_24h=0.4)  # 4e → hors top 3
    records = sa.build_decision_log_records(forts + [surnumeraire], _NOW)
    rec_24h = next(
        r for r in records if r["actif"] == "Café" and r.get("horizon") == "24h"
    )
    assert rec_24h["selection_du_jour"] is False
    assert rec_24h["selection_motif_exclusion"] == "hors top 3"


# ---------------------------------------------------------------------------
# Capteurs shadow 24h (Étage 2)
# ---------------------------------------------------------------------------

def test_shadow_capteurs_calcul():
    fiches = {"or": {"ticker_principal": "XAU"}}

    def _fake_series(symbol, outputsize=10):
        # oldest→newest : [-2]=close J-2=100, [-1]=close J-1=110.
        return [
            (datetime(2026, 6, 10, tzinfo=timezone.utc), 100.0),
            (datetime(2026, 6, 11, tzinfo=timezone.utc), 110.0),
        ]

    caps = sa.compute_shadow_capteurs(
        fiches, prix_emission={"XAU": 121.0}, fetch_series=_fake_series,
    )
    # retour_j1 = 110/100 - 1 = 0.10 ; gap = 121/110 - 1 = 0.10.
    assert caps["or"]["shadow_retour_j1"] == pytest.approx(0.10)
    assert caps["or"]["shadow_gap_overnight"] == pytest.approx(0.10)


def test_shadow_capteurs_none_propres():
    fiches = {"or": {"ticker_principal": "XAU"}}

    # Série indisponible → retour_j1 None ; pas de prix émission → gap None.
    caps = sa.compute_shadow_capteurs(
        fiches, prix_emission={}, fetch_series=lambda s, outputsize=10: None,
    )
    assert caps["or"]["shadow_retour_j1"] is None
    assert caps["or"]["shadow_gap_overnight"] is None


def test_shadow_capteurs_gap_none_si_close_manque():
    fiches = {"or": {"ticker_principal": "XAU"}}
    # Une seule bougie → pas de J-2 → retour_j1 None ; close J-1 connu → gap OK.
    caps = sa.compute_shadow_capteurs(
        fiches,
        prix_emission={"XAU": 121.0},
        fetch_series=lambda s, outputsize=10: [
            (datetime(2026, 6, 11, tzinfo=timezone.utc), 110.0)
        ],
    )
    assert caps["or"]["shadow_retour_j1"] is None
    assert caps["or"]["shadow_gap_overnight"] == pytest.approx(0.10)


def test_decision_log_shadow_injecte():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    shadow = {"or": {"shadow_retour_j1": 0.05, "shadow_gap_overnight": -0.02}}
    records = sa.build_decision_log_records([a], _NOW, shadow_capteurs=shadow)
    rec_24h = next(r for r in records if r.get("horizon") == "24h")
    assert rec_24h["shadow_retour_j1"] == pytest.approx(0.05)
    assert rec_24h["shadow_gap_overnight"] == pytest.approx(-0.02)


def test_decision_log_shadow_none_si_absent():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    records = sa.build_decision_log_records([a], _NOW)  # pas de shadow_capteurs
    rec_24h = next(r for r in records if r.get("horizon") == "24h")
    assert rec_24h["shadow_retour_j1"] is None
    assert rec_24h["shadow_gap_overnight"] is None


# ---------------------------------------------------------------------------
# WR Sélection au bilan (Étage 1c, synthétique)
# ---------------------------------------------------------------------------

class _FakeCell:
    def __init__(self, actif_name: str):
        self.actif_name = actif_name


class _FakeMeasure:
    def __init__(self, actif: str, horizon: str, outcome: str):
        self.cell = _FakeCell(actif)
        self.horizon = horizon
        self.outcome = outcome


def test_win_rate_selection_compte_vrai_fausse():
    import bilan_jour as bj
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE, OUTCOME_NC

    measures = [
        _FakeMeasure("Or", "24h", OUTCOME_VRAI),
        _FakeMeasure("Argent", "24h", OUTCOME_FAUSSE),
        _FakeMeasure("Cuivre", "24h", OUTCOME_VRAI),  # non sélectionné → ignoré
        _FakeMeasure("Or", "24h", OUTCOME_NC),         # NC → exclu du WR
    ]
    selection_map = {("Or", "24h"): True, ("Argent", "24h"): True, ("Cuivre", "24h"): False}
    wr = bj.win_rate_selection(measures, selection_map)
    assert wr.n_select == 2
    assert wr.n_vrai_select == 1
    assert wr.taux == pytest.approx(50.0)


def test_win_rate_selection_vide():
    import bilan_jour as bj
    wr = bj.win_rate_selection([], {})
    assert wr.n_select == 0
    assert wr.taux is None


# ---------------------------------------------------------------------------
# Dédup par FAMILLE macro (brief 12/06 — défaut 11/06)
# ---------------------------------------------------------------------------

import shared_drivers as sd  # noqa: E402  (après les fabriques, cf. style fichier)


@pytest.mark.parametrize(
    "cle_a, cle_b",
    [
        # TIPS et écart 2Y US-DE = LE MÊME complexe taux/dollar (cœur du défaut 11/06).
        ("taux_10y_us_reels_tips", "differentiel_taux_2y_us_de"),
        # Variation du 10Y US et dollar DXY = même famille taux/dollar.
        ("taux_10y_us_delta_5j", "dxy_trend_20j"),
        # USD/JPY et FedWatch = même famille taux/dollar.
        ("usd_jpy_proxy_risk", "fedwatch_proba"),
        # VIX régime et spread crédit HY = même famille risk_on_off.
        ("vix_regime", "hy_credit_spread"),
        # Mouvement de l'or et ratio or/argent = même famille metaux_croises.
        ("mouvement_or_5j", "ratio_gold_silver"),
        # OAT-Bund et tension politique FR = même famille stress_europe.
        ("spread_oat_bund_10y", "tension_politique_fr"),
    ],
)
def test_famille_macro_meme_famille(cle_a, cle_b):
    fa, _ = sd.famille_macro(cle_a)
    fb, _ = sd.famille_macro(cle_b)
    assert fa == fb, f"{cle_a} et {cle_b} devraient être la MÊME famille"


def test_famille_taux_dollar_label():
    famille, label = sd.famille_macro("taux_10y_us_reels_tips")
    assert famille == "taux_dollar"
    assert label == "taux/dollar"


def test_famille_oat_bund_est_europe_pas_dollar():
    # Garde-fou explicite du brief : l'OAT-Bund est un driver FRANCE, pas dollar.
    famille_oat, _ = sd.famille_macro("differentiel_taux_10y_us_bund")
    famille_eu, _ = sd.famille_macro("spread_oat_bund_10y")
    assert famille_oat == "taux_dollar"      # écart US-Bund = dollar
    assert famille_eu == "stress_europe"     # OAT-Bund (France) = stress euro
    assert famille_oat != famille_eu


def test_famille_tendance_propre_par_actif():
    # Momentum de l'or ≠ momentum du cacao : tendance de SON actif, pas le même
    # pari → la famille intègre la fiche/actif dans sa clé de regroupement.
    f_or, _ = sd.famille_macro("momentum_prix_20j_or", fiche_key="or")
    f_cacao, _ = sd.famille_macro("momentum_prix_20j_cacao", fiche_key="cacao")
    assert f_or != f_cacao
    assert f_or == "tendance_propre:or"
    assert f_cacao == "tendance_propre:cacao"
    # Même actif (deux signaux de tendance distincts) → MÊME famille.
    f_rsi_or, _ = sd.famille_macro("rsi_14j_gspc", fiche_key="sp500")
    f_breadth_sp, _ = sd.famille_macro("breadth_sp_ma50", fiche_key="sp500")
    assert f_rsi_or == f_breadth_sp == "tendance_propre:sp500"


def test_famille_fallback_singleton():
    # Clé absente de la table ET non-tendance → famille SINGLETON (= la clé).
    famille, label = sd.famille_macro("eia_crude_surprise")
    assert famille == "eia_crude_surprise"
    assert label == "eia_crude_surprise"


# ---------------------------------------------------------------------------
# RÈGLE DE SÉLECTION « HAUTE-CONVICTION » en SHADOW PUR (panel 3 experts 25/06).
# Garde-fous : SHADOW PUR (la sélection RÉELLE ne bouge JAMAIS), WIN RATE ONLY,
# pas d'override news, zéro invention. On prouve : (a) réel inchangé, (b) shadow
# calculée/loggée, (c) cas cacao 25/06 éligible en shadow.
# ---------------------------------------------------------------------------

def _crit_val(cle: str, poids: float, val, contrib: float = 0.0) -> sa.CritereResult:
    """Critère paramétrable : `val=None` → n/a (source morte) ; sinon vivant."""
    c = sa.CritereResult(
        id=cle,
        nom=cle,
        type_norm="lineaire",
        valeur_brute=val,
        valeur_norm=val,
        poids=poids,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: contrib for h in sa.HORIZONS},
        cle_courante=cle,
    )
    c.is_na = val is None
    return c


def _actif_criteres(
    nom: str,
    fiche_key: str,
    criteres: List[sa.CritereResult],
    *,
    score_24h: float,
    direction: str = "LONG",
    coverage: float = 1.0,
) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=fiche_key,
        criteres=criteres,
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (direction if h == "24h" else sa.CONCLUSION_INSUFFISANT) for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=coverage,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


def _cacao_2506() -> sa.ActifResult:
    """Reconstitue le cas cacao du 25/06 (audit fallback-source-cacao).

    Conditions reproduites pour que le RÉEL écarte ET que le SHADOW prenne :
      - 2 sources MORTES : météo CI+Ghana (poids 11, le PLUS LOURD, uniquement) +
        arrivées ports (poids 9) → n/a ; le critère de poids MAX est donc n/a ;
      - critères VIVANTS unanimes LONG : positionnement (5), spread (5), news
        offre El Niño (6) → poids vivant = 16 ;
      - couverture TOTALE = 16 / 36 ≈ 0.444 : sous CONVICTION_COVERAGE_MIN (0.50)
        ET poids-max n/a → la tête RÉELLE plafonne la conviction à « fragile
        (couverture insuffisante) » → cacao ÉCARTÉ du réel ;
      - couverture SUR VIVANTS = 1.0 ; part vivante = 16/36 ≈ 0.444 (≥ 0.40 garde-
        fou anti coquille vide) ;
      - |note| = 9.2 ≥ SHADOW_HC_NOTE_MIN (8.0) → quant hors-norme.
    → le SHADOW haute-conviction prend le cacao là où le réel l'écarte.
    momentum_prix_ exclu du calcul de couverture → on n'en met pas (cohérent).
    """
    criteres = [
        _crit_val("meteo_ci_ghana_precip_30j", 11.0, None),         # MORTE, poids MAX
        _crit_val("arrivees_port_abidjan_sanpedro_20j", 9.0, None),   # MORTE (structurel)
        _crit_val("hf_positioning_flux_options", 5.0, 1.0, contrib=0.5),   # vivant
        _crit_val("spread_ny_london", 5.0, 1.0, contrib=0.5),            # vivant
        _crit_val("synthese_offre_cacao", 6.0, 1.0, contrib=0.7),        # vivant (news offre)
    ]
    # coverage TOTAL (comme compute_coverage) = 16/36 ≈ 0.444 (< 0.50 → réel écarte).
    return _actif_criteres(
        "Cacao", "cacao", criteres,
        score_24h=9.2, direction="LONG", coverage=16.0 / 36.0,
    )


def test_shadow_couverture_vivants_exclut_les_na():
    a = _cacao_2506()
    # Couverture TOTALE plombée par les 2 sources mortes (16/36 ≈ 0.444 < 0.50).
    assert sa.compute_coverage(a.criteres) == pytest.approx(16.0 / 36.0)
    # Couverture SUR VIVANTS = 1.0 (n/a exclus du dénominateur).
    assert sa.compute_couverture_vivants(a.criteres) == pytest.approx(1.0)
    # Part du poids total portée par les vivants = 16/36 ≈ 0.444.
    assert sa.couverture_vivants_part(a.criteres) == pytest.approx(16.0 / 36.0)


def test_shadow_reporte_compte_comme_vivant():
    # Une valeur reportée (cache last-good) a une valeur_norm → compte VIVANTE.
    crit = _crit_val("meteo_ci_ghana_precip_30j", 11.0, 1.2)
    crit.reporte = True
    crit.reporte_age_j = 2
    assert crit.valeur_norm is not None
    a = _actif_criteres("X", "x", [crit], score_24h=9.0)
    assert sa.compute_couverture_vivants(a.criteres) == pytest.approx(1.0)
    assert sa.couverture_vivants_part(a.criteres) == pytest.approx(1.0)


def test_shadow_cacao_2506_eligible():
    """(c) Le cas cacao 25/06 serait PRIS par la règle shadow haute-conviction."""
    a = _cacao_2506()
    picks, motifs = sa.compute_selection_shadow_hc([a], now=_NOW)
    assert [p["fiche_key"] for p in picks] == ["cacao"]
    assert picks[0]["direction"] == "LONG"
    assert picks[0]["couverture_vivants"] == pytest.approx(1.0)
    assert picks[0]["coverage_totale"] == pytest.approx(16.0 / 36.0, abs=1e-3)


def test_shadow_cacao_2506_ecarte_du_reel():
    """(a) PREUVE garde-fou : la sélection RÉELLE écarte le cacao (couverture
    totale 0.375 < 0.70). La règle shadow ne change RIEN à ce verdict réel."""
    a = _cacao_2506()
    sel_reelle, _ = sa.compute_selection_du_jour([a], now=_NOW)
    assert sel_reelle == []  # réel : écarté (couverture insuffisante)


def test_shadow_rejette_note_faible():
    a = _cacao_2506()
    a.scores["24h"] = 3.0  # |note| < 8.0 → inéligible shadow
    picks, motifs = sa.compute_selection_shadow_hc([a], now=_NOW)
    assert picks == []
    assert motifs["cacao"] == "note < seuil shadow"


def test_shadow_rejette_couverture_vivants_faible():
    # |note| forte mais un vivant n/a partiel → couverture vivants < 0.70.
    criteres = [
        _crit_val("a", 7.0, 1.0, contrib=0.5),   # vivant
        _crit_val("b", 8.0, None),               # mort → exclu du dénominateur
        _crit_val("c", 3.0, None),               # mort → exclu
    ]
    # Pour forcer couverture vivants < 0.70 il faut un vivant « non couvert ».
    # Notre modèle : vivant == couvert. On teste donc la part vivante faible.
    a = _actif_criteres("Y", "y", criteres, score_24h=9.0, coverage=7.0 / 18.0)
    # part vivante = 7/18 ≈ 0.389 < 0.40 → rejet par garde-fou coquille vide.
    picks, motifs = sa.compute_selection_shadow_hc([a], now=_NOW)
    assert picks == []
    assert motifs["y"] == "poids vivant insuffisant"


def test_shadow_rejette_si_news_contre_sens(monkeypatch):
    # PAS d'override news : une news high à contre-sens DISQUALIFIE (↯).
    a = _cacao_2506()
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", lambda now: {"Cacao": {"SHORT"}})
    picks, motifs = sa.compute_selection_shadow_hc([a], now=_NOW)
    assert picks == []
    assert motifs["cacao"] == "news à contre-sens (↯)"


def test_shadow_cap_max_3():
    actifs = [
        _actif_criteres(
            f"A{i}", f"a{i}",
            [_crit_val("k", 5.0, 1.0, contrib=0.5)],
            score_24h=9.5 - i * 0.1,
        )
        for i in range(5)
    ]
    picks, motifs = sa.compute_selection_shadow_hc(actifs, now=_NOW)
    assert len(picks) == 3
    assert motifs["a3"] == "hors top 3 (shadow)"
    assert motifs["a4"] == "hors top 3 (shadow)"


# --- Decision-log : (b) shadow calculée ET loggée, réel inchangé -------------

def test_decision_log_selection_shadow_hc_loggee():
    """(b) Le champ `selection_shadow_hc` est écrit au decision-log (24h)."""
    a = _cacao_2506()
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r.get("horizon") == "24h")
    assert rec_24h["selection_shadow_hc"] is True
    # Hors 24h : champ absent (la sélection est définie sur le pari 24h).
    rec_7j = next(r for r in records if r.get("horizon") == "7j")
    assert "selection_shadow_hc" not in rec_7j


def test_decision_log_shadow_hc_nest_pas_le_reel():
    """(a)+(b) GARDE-FOU CENTRAL : sur le cacao 25/06, `selection_du_jour` RÉEL
    reste FALSE (écarté, couverture totale insuffisante) tandis que la mesure
    shadow `selection_shadow_hc` est TRUE. Les deux champs sont INDÉPENDANTS :
    le shadow ne contamine jamais le réel."""
    a = _cacao_2506()
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r.get("horizon") == "24h")
    assert rec_24h["selection_du_jour"] is False        # RÉEL : écarté (inchangé)
    assert rec_24h["selection_shadow_hc"] is True       # SHADOW : aurait été pris


def test_decision_log_shadow_hc_motif_si_ecarte():
    a = _cacao_2506()
    a.scores["24h"] = 3.0  # inéligible shadow (note faible)
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r.get("horizon") == "24h")
    assert rec_24h["selection_shadow_hc"] is False
    assert rec_24h["selection_shadow_hc_motif"] == "note < seuil shadow"


def test_mesure_branchement_shadow_field(tmp_path):
    """POINT DE BRANCHEMENT MESURE : `load_selection_map(field=...)` lit le champ
    shadow EN PARALLÈLE du réel, avec la MÊME mécanique → win_rate_selection
    réutilisable verbatim sur la sélection shadow."""
    import json
    import bilan_jour as bj
    from datetime import date

    d = date(2026, 6, 25)
    log = tmp_path / f"{d.isoformat()}-1200.jsonl"
    rows = [
        {"bulletin_date": d.isoformat(), "actif": "Cacao", "horizon": "24h",
         "selection_du_jour": False, "selection_shadow_hc": True},
        {"bulletin_date": d.isoformat(), "actif": "Or", "horizon": "24h",
         "selection_du_jour": True, "selection_shadow_hc": False},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    reel = bj.load_selection_map(d, decision_log_dir=tmp_path)
    shadow = bj.load_selection_map(d, decision_log_dir=tmp_path, field="selection_shadow_hc")
    # Les deux vues sont INDÉPENDANTES (réel ≠ shadow).
    assert reel[("Cacao", "24h")] is False
    assert reel[("Or", "24h")] is True
    assert shadow[("Cacao", "24h")] is True
    assert shadow[("Or", "24h")] is False
    # Deux clés singleton distinctes → familles distinctes (aucun regroupement).
    f1, _ = sd.famille_macro("egypte_gasc_tenders")
    f2, _ = sd.famille_macro("opec_production_policy")
    assert f1 != f2


def test_famille_cle_vide():
    assert sd.famille_macro("") == ("", "")


def test_selection_dedup_par_famille_taux_dollar():
    # Rejeu du 11/06 : Argent (TIPS) + EUR/USD (écart 2Y US-DE) = MÊME famille
    # taux/dollar, MÊME direction LONG → un seul retenu (la plus forte |note|).
    argent = _actif(
        "Argent", "argent", score_24h=0.92, direction="LONG",
        driver_cle="taux_10y_us_reels_tips", driver_nom="Taux réels US (TIPS)",
    )
    eurusd = _actif(
        "EUR/USD", "eurusd", score_24h=0.81, direction="LONG",
        driver_cle="differentiel_taux_2y_us_de", driver_nom="Écart 2Y US-DE",
    )
    cafe = _actif(
        "Café", "cafe", score_24h=0.75, direction="LONG",
        driver_cle="momentum_prix_20j_cafe", driver_nom="Momentum café",
    )
    sel, ecart = sa.compute_selection_du_jour([argent, eurusd, cafe])
    # Argent (le plus fort du complexe taux/dollar) + Café (famille propre) retenus.
    assert {s["fiche_key"] for s in sel} == {"argent", "cafe"}
    # EUR/USD écarté : même pari taux/dollar que Argent.
    motifs = {e["fiche_key"]: e["motif"] for e in ecart}
    assert motifs == {"eurusd": "même pari (taux/dollar) que Argent"}


def test_selection_famille_propre_ne_dedup_pas_entre_actifs():
    # Café (momentum café) et Cacao (momentum cacao) : tendance de LEUR actif →
    # familles DIFFÉRENTES → les deux retenus (pas de dédup abusive).
    cafe = _actif(
        "Café", "cafe", score_24h=0.9, direction="LONG",
        driver_cle="momentum_prix_20j_cafe", driver_nom="Momentum café",
    )
    cacao = _actif(
        "Cacao", "cacao", score_24h=0.85, direction="LONG",
        driver_cle="momentum_prix_20j_cacao", driver_nom="Momentum cacao",
    )
    sel, ecart = sa.compute_selection_du_jour([cafe, cacao])
    assert {s["fiche_key"] for s in sel} == {"cafe", "cacao"}
    assert ecart == []


def test_selection_motif_famille_affiche_dans_bloc(monkeypatch):
    monkeypatch.setattr(sa, "_catalyseurs_j0_high", lambda now: [])
    argent = _actif(
        "Argent", "argent", score_24h=0.92, direction="LONG",
        driver_cle="taux_10y_us_reels_tips", driver_nom="Taux réels US (TIPS)",
    )
    eurusd = _actif(
        "EUR/USD", "eurusd", score_24h=0.81, direction="LONG",
        driver_cle="differentiel_taux_2y_us_de", driver_nom="Écart 2Y US-DE",
    )
    texte = "\n".join(sa.build_selection_du_jour_block([argent, eurusd], _NOW))
    assert "écartée : EUR/USD, même pari (taux/dollar) que Argent" in texte
    # P2 — la règle « chaque type de marché représenté une seule fois » est
    # désormais expliquée dans « Comment lire les scores » (une seule fois).
    assert "chaque type de marché représenté une seule fois" not in texte
    pedago = "\n".join(sa.build_comment_lire_block(set()))
    assert "chaque type de marché représenté une seule fois" in pedago


# ---------------------------------------------------------------------------
# VETO NEWS↯ (décision fondateur 22/06) — NEWS SEULE : une news high adverse
# fraîche suffit à écarter une cellule de la VITRINE (top 3). Pas de condition
# tape. Garde-fou quant exceptionnel conservé. Cf. _veto_news_contre_call.
# ---------------------------------------------------------------------------

def _actif_veto(score_24h=2.0, direction="LONG"):
    """ActifResult 24h forte (candidate à la Sélection)."""
    return _actif("S&P 500", "sp500", score_24h=score_24h, direction=direction)


def _patch_news_short(monkeypatch):
    """News high SHORT sur S&P (contre un call LONG) dans le flux du jour."""
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        lambda now: {"S&P 500": {"SHORT"}})
    import bilan_jour as bj
    monkeypatch.setattr(
        bj, "cause_news_high_dir",
        lambda actif, date_j, sens, apres=None, events_path=None:
            "Chine impose des restrictions" if sens == "SHORT" else None,
    )


def test_veto_news_seule_exclut_la_cellule(monkeypatch):
    # Une news high SHORT contre un call LONG SUFFIT (pas besoin de tape).
    _patch_news_short(monkeypatch)
    a = _actif_veto()
    sel, ecart = sa.compute_selection_du_jour([a], now=_NOW)
    assert sel == []
    assert any(e["motif"].startswith("VETO news") for e in ecart)


def test_veto_news_alignee_pas_de_veto(monkeypatch):
    # News high SHORT mais call SHORT (alignée) → pas de contradiction → gardée.
    _patch_news_short(monkeypatch)
    a = _actif_veto(score_24h=-2.0, direction="SHORT")
    sel, _ = sa.compute_selection_du_jour([a], now=_NOW)
    assert [s["fiche_key"] for s in sel] == ["sp500"]


def test_veto_quant_exceptionnel_pas_de_veto(monkeypatch):
    # News adverse MAIS quant hors-norme (>= 8.0) → garde-fou Analyst conservé.
    _patch_news_short(monkeypatch)
    a = _actif_veto(score_24h=8.5)
    sel, _ = sa.compute_selection_du_jour([a], now=_NOW)
    assert [s["fiche_key"] for s in sel] == ["sp500"]


def test_veto_sans_now_ignore(monkeypatch):
    # now absent → veto inactif (zéro invention), cellule conservée.
    _patch_news_short(monkeypatch)
    a = _actif_veto()
    sel, _ = sa.compute_selection_du_jour([a])
    assert [s["fiche_key"] for s in sel] == ["sp500"]


def test_veto_sans_news_pas_de_veto(monkeypatch):
    # Aucune news adverse → cellule conservée.
    import bilan_jour as bj
    monkeypatch.setattr(
        bj, "cause_news_high_dir",
        lambda actif, date_j, sens, apres=None, events_path=None: None,
    )
    a = _actif_veto()
    sel, _ = sa.compute_selection_du_jour([a], now=_NOW)
    assert [s["fiche_key"] for s in sel] == ["sp500"]


def test_veto_affiche_dans_bloc(monkeypatch):
    monkeypatch.setattr(sa, "_catalyseurs_j0_high", lambda now: [])
    _patch_news_short(monkeypatch)
    a = _actif_veto()
    texte = "\n".join(sa.build_selection_du_jour_block([a], _NOW))
    # Format compact (retour Thomas 22/06) : ligne courte, news tronquée, pas de
    # boilerplate par ligne. On vérifie le motif compact + l'actif + la news.
    assert "écarté du top 3" in texte
    assert "S&P 500" in texte
    assert "Chine impose des restrictions" in texte
    # L'explication générique « jouable ailleurs » apparaît UNE seule fois.
    assert texte.count("jouables dans") == 1



# ---------------------------------------------------------------------------
# Conflit inter-horizons (⇅) — call 24h à contre-sens du fond 7j ET 1m
# (audit fond 22/06, cas S&P LONG 24h / SHORT 7j-1m).
# ---------------------------------------------------------------------------

def test_conflit_inter_horizons_flague():
    a = _actif("S&P 500", "sp500", score_24h=0.9, direction="LONG")
    a.conclusions = {"24h": "LONG", "7j": "SHORT", "1m": "SHORT"}
    sel, _ = sa.compute_selection_du_jour([a], now=_NOW)
    assert sel and sel[0]["conflit_horizons"] is True


def test_pas_de_conflit_si_un_seul_horizon_oppose():
    # 7j oppose mais 1m aligné → PAS un conflit de fond (il faut 7j ET 1m opposés).
    a = _actif("S&P 500", "sp500", score_24h=0.9, direction="LONG")
    a.conclusions = {"24h": "LONG", "7j": "SHORT", "1m": "LONG"}
    sel, _ = sa.compute_selection_du_jour([a], now=_NOW)
    assert sel and sel[0]["conflit_horizons"] is False


def test_conflit_inter_horizons_affiche_dans_bloc(monkeypatch):
    monkeypatch.setattr(sa, "_catalyseurs_j0_high", lambda now: [])
    a = _actif("S&P 500", "sp500", score_24h=0.9, direction="LONG")
    a.conclusions = {"24h": "LONG", "7j": "SHORT", "1m": "SHORT"}
    texte = "\n".join(sa.build_selection_du_jour_block([a], _NOW))
    assert "⇅" in texte
    assert "contre-sens du fond" in texte



# ---------------------------------------------------------------------------
# Swing 7j JOUABLE (audit 7j) : sélection tendance + objectif + dédup driver.
# ---------------------------------------------------------------------------

def test_swing_7j_selectionne_objectif_et_dedup(monkeypatch):
    import shared_drivers as sd
    # Deux actifs FORTS 7j sur le MÊME driver (taux réels) → 1 seul retenu ; +1 autre.
    monkeypatch.setattr(sd, "famille_macro",
                        lambda cle, fk="": ("taux_reels_us", "Taux réels US")
                        if cle == "taux" else (cle, cle))
    a = _actif("Or", "or", score_24h=0.0, direction="SHORT")
    a.conclusions = {"24h": "INSUFFISANT", "7j": "SHORT", "1m": "SHORT"}
    a.scores = {"24h": 0.0, "7j": -6.0, "1m": -3.0}
    a.coverage = 0.95
    a._top_driver_cle = "taux"
    b = _actif("Argent", "argent", score_24h=0.0, direction="SHORT")
    b.conclusions = {"24h": "INSUFFISANT", "7j": "SHORT", "1m": "SHORT"}
    b.scores = {"24h": 0.0, "7j": -5.0, "1m": -2.0}
    b.coverage = 0.95
    b._top_driver_cle = "taux"
    c = _actif("EUR/USD", "eurusd", score_24h=0.0, direction="LONG")
    c.conclusions = {"24h": "INSUFFISANT", "7j": "LONG", "1m": "LONG"}
    c.scores = {"24h": 0.0, "7j": 4.0, "1m": 2.0}
    c.coverage = 0.95
    c._top_driver_cle = "diff_taux"
    monkeypatch.setattr(sa, "_top_driver",
                        lambda r, h: (getattr(r, "_top_driver_cle", ""), "Driver X"))
    monkeypatch.setattr(sa, "_seuil_conviction_defaut", lambda: 0.6)
    fiches = {
        "or": {"seuils_reussite_pct": {"7j": 1.3}},
        "argent": {"seuils_reussite_pct": {"7j": 1.5}},
        "eurusd": {"seuils_reussite_pct": {"7j": 0.7}},
    }
    txt = "\n".join(sa.build_swing_7j_block([a, b, c], prix_reference={"or": 4200}, fiches=fiches))
    assert "## 📈 Swing 7j (max 3)" in txt
    # Or et Argent même driver → un seul des deux ; EUR/USD distinct présent.
    assert txt.count("**Or**") + txt.count("**Argent**") == 1
    assert "**EUR/USD**" in txt
    assert "objectif" in txt and "%" in txt


def test_swing_7j_vide_si_rien_de_fort(monkeypatch):
    monkeypatch.setattr(sa, "_seuil_conviction_defaut", lambda: 0.6)
    a = _actif("Or", "or", score_24h=0.0, direction="SHORT")
    a.conclusions = {"24h": "INSUFFISANT", "7j": "INSUFFISANT", "1m": "INSUFFISANT"}
    a.scores = {"24h": 0.0, "7j": 0.0, "1m": 0.0}
    txt = "\n".join(sa.build_swing_7j_block([a], fiches={}))
    assert "Aucune tendance 7j" in txt


def test_positions_1m_objectif_1m_et_dedup(monkeypatch):
    import shared_drivers as sd
    monkeypatch.setattr(sd, "famille_macro",
                        lambda cle, fk="": ("taux_reels_us", "Taux réels US")
                        if cle == "taux" else (cle, cle))
    monkeypatch.setattr(sa, "_top_driver",
                        lambda r, h: (getattr(r, "_d", ""), "Driver X"))
    monkeypatch.setattr(sa, "_seuil_conviction_defaut", lambda: 0.6)
    a = _actif("Or", "or", score_24h=0.0, direction="SHORT")
    a.conclusions = {"24h": "INSUFFISANT", "7j": "SHORT", "1m": "SHORT"}
    a.scores = {"24h": 0.0, "7j": -6.0, "1m": -7.0}; a.coverage = 0.95; a._d = "taux"
    b = _actif("Argent", "argent", score_24h=0.0, direction="SHORT")
    b.conclusions = {"24h": "INSUFFISANT", "7j": "SHORT", "1m": "SHORT"}
    b.scores = {"24h": 0.0, "7j": -5.0, "1m": -6.0}; b.coverage = 0.95; b._d = "taux"
    c = _actif("EUR/USD", "eurusd", score_24h=0.0, direction="LONG")
    c.conclusions = {"24h": "INSUFFISANT", "7j": "LONG", "1m": "LONG"}
    c.scores = {"24h": 0.0, "7j": 4.0, "1m": 5.0}; c.coverage = 0.95; c._d = "fx"
    fiches = {"or": {"seuils_reussite_pct": {"1m": 3.0}},
              "argent": {"seuils_reussite_pct": {"1m": 3.5}},
              "eurusd": {"seuils_reussite_pct": {"1m": 1.5}}}
    txt = "\n".join(sa.build_positions_1m_block([a, b, c], prix_reference={"or": 4200}, fiches=fiches))
    assert "## 🗓️ Positions 1 mois (max 3)" in txt
    assert txt.count("**Or**") + txt.count("**Argent**") == 1   # dédup driver
    assert "**EUR/USD**" in txt and "objectif" in txt


def test_carry_1m_allonge_a_96h():
    # Cohérence horizon (audit 1m) : le maintien 1m ne doit plus être < le 7j.
    assert sa.CARRY_MAX_AGE_H["1m"] >= sa.CARRY_MAX_AGE_H["7j"]


# ---------------------------------------------------------------------------
# UNE SEULE sélection du jour, partout (refonte 23/06, brief fondateur)
# La tête « 🎯 Aujourd'hui » (select_paris_du_jour) == le champ decision-log
# selection_du_jour == ce que le suivi/bilan traquent (load_selection_map).
# ---------------------------------------------------------------------------

def _actif_contresens(nom, fiche_key, *, score_24h, direction="LONG"):
    """ActifResult dont la cellule 24h porte un ↯ (news à contre-sens) via
    divergence_quant_news — même source de vérité que la colonne Drapeaux."""
    a = _actif(nom, fiche_key, score_24h=score_24h, direction=direction)
    a.divergence_quant_news = {"24h": True}
    return a


def test_selection_du_jour_map_egale_select_paris_du_jour():
    """Le set de fiche_key marqués selection_du_jour:true (via selection_du_jour_map,
    qui alimente le decision-log) == EXACTEMENT le set retourné par
    select_paris_du_jour (la tête). Aucune divergence possible."""
    actifs = [
        _actif("Or", "or", score_24h=0.9),
        _actif("Argent", "argent", score_24h=0.8),
        _actif("Cacao", "cacao", score_24h=0.7),
        _actif("Café", "cafe", score_24h=0.6),  # 4e → hors top 3
    ]
    tete = {p["fiche_key"] for p in sa.select_paris_du_jour(actifs, _NOW)}
    keys, _motifs = sa.selection_du_jour_map(actifs, _NOW)
    assert keys == tete
    assert keys == {"or", "argent", "cacao"}


def test_profil_23_06_contresens_exclu_tete_egale_decision_log():
    """Reproduit le profil 23/06 : Or et EUR portent un ↯ (news à contre-sens) et
    sont EXCLUS. La sélection écrite au decision-log = les non-↯ (Cacao/Argent/CAC),
    IDENTIQUE à la tête. C'est ce que load_selection_map renverrait → le suivi
    traque CES positions (plus de divergence tête ↔ suivi)."""
    actifs = [
        _actif_contresens("Or", "or", score_24h=0.95),       # ↯ → exclu
        _actif_contresens("EUR/USD", "eurusd", score_24h=0.90),  # ↯ → exclu
        _actif("Cacao", "cacao", score_24h=0.80),
        _actif("Argent", "argent", score_24h=0.75),
        _actif("CAC", "cac", score_24h=0.70),
    ]
    # 1) La tête affiche les non-↯ (top 3 par |note|).
    tete = {p["fiche_key"] for p in sa.select_paris_du_jour(actifs, _NOW)}
    assert tete == {"cacao", "argent", "cac"}

    # 2) Le decision-log marque selection_du_jour:true sur EXACTEMENT ces cellules.
    records = sa.build_decision_log_records(actifs, _NOW)
    # [03/07] .get() : le decision-log porte désormais aussi des records d'état
    # (record_type=positions_ouvertes) sans champ horizon/fiche_key : les
    # lecteurs (prod comme tests) doivent les ignorer sans crasher.
    selected = {
        r.get("fiche_key") for r in records
        if r.get("horizon") == "24h" and r.get("selection_du_jour") is True
    }
    assert selected == tete

    # 3) Les ↯ écartés portent le motif « écarté : news à contre-sens (↯) ».
    motifs = {
        r["fiche_key"]: r.get("selection_motif_exclusion")
        for r in records if r.get("horizon") == "24h"
    }
    assert motifs["or"] == "écarté : news à contre-sens (↯)"
    assert motifs["eurusd"] == "écarté : news à contre-sens (↯)"

    # 4) load_selection_map (ce que le suivi/bilan traquent) renvoie les MÊMES
    #    cellules sélectionnées que la tête (écriture → lecture round-trip).
    import json as _json
    import tempfile
    from datetime import date as _date
    from pathlib import Path as _Path

    import bilan_jour as _bj
    with tempfile.TemporaryDirectory() as d:
        log_dir = _Path(d)
        fp = log_dir / "2026-06-12-07h.jsonl"
        with fp.open("w", encoding="utf-8") as fh:
            for r in records:
                fh.write(_json.dumps(r, ensure_ascii=False) + "\n")
        sel_map = _bj.load_selection_map(_date(2026, 6, 12), decision_log_dir=log_dir)
    selected_via_map = {
        actif for (actif, h), v in sel_map.items() if h == "24h" and v is True
    }
    # load_selection_map indexe par NOM d'actif (pas fiche_key) → on convertit.
    noms_attendus = {"Cacao", "Argent", "CAC"}
    assert selected_via_map == noms_attendus
