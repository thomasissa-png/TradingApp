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
        poids=5.0,
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
    assert "| Or | LONG | +0.90 | Fed (val 1, sens normal) → contribue +0.40 | 2400 |" in texte
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
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["selection_du_jour"] is True
    assert "selection_motif_exclusion" not in rec_24h
    # Hors 24h : champ absent (la sélection est définie sur le pari 24h).
    rec_7j = next(r for r in records if r["horizon"] == "7j")
    assert "selection_du_jour" not in rec_7j


def test_decision_log_selection_motif_exclusion():
    fort = _actif("Or", "or", score_24h=0.9, driver_cle="drv_macro", driver_nom="Fed")
    faible = _actif("Argent", "argent", score_24h=0.7, driver_cle="drv_macro", driver_nom="Fed")
    records = sa.build_decision_log_records([fort, faible], _NOW)
    rec_or = next(r for r in records if r["actif"] == "Or" and r["horizon"] == "24h")
    rec_ag = next(r for r in records if r["actif"] == "Argent" and r["horizon"] == "24h")
    assert rec_or["selection_du_jour"] is True
    assert rec_ag["selection_du_jour"] is False
    assert rec_ag["selection_motif_exclusion"] == "même pari (drv_macro) que Or"


def test_decision_log_selection_false_quand_non_selectionnee():
    a = _actif("Or", "or", score_24h=0.4)  # molle → non sélectionnée
    records = sa.build_decision_log_records([a], _NOW)
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["selection_du_jour"] is False


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
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["shadow_retour_j1"] == pytest.approx(0.05)
    assert rec_24h["shadow_gap_overnight"] == pytest.approx(-0.02)


def test_decision_log_shadow_none_si_absent():
    a = _actif("Or", "or", score_24h=0.9, driver_cle="drv_a")
    records = sa.build_decision_log_records([a], _NOW)  # pas de shadow_capteurs
    rec_24h = next(r for r in records if r["horizon"] == "24h")
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

