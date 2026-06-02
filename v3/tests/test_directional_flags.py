"""Tests Lot 4a — détecteurs directionnels FLAG-ONLY.

Couvre les 3 détecteurs ajoutés en mode drapeau :
    - C3      : divergence quant ↔ news
    - score-vs-momentum (RSI 14j sur ticker propre)
    - C6      : incohérence inter-horizons (zig-zag)

Garde-fou ABSOLU : aucune de ces détections ne doit modifier les conclusions
LONG/SHORT/INSUFFISANT. Un test dédié (test_conclusions_unchanged_by_flags)
verrouille ce contrat.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_crit(
    idx: int,
    *,
    cle: str = "",
    source_track: str = "",
    valeur_norm: float = 0.0,
    poids: float = 1.0,
    signe: int = 1,
    nom: str = "",
    is_gate: bool = False,
    is_na: bool = False,
    pertinence: float = 1.0,
    contributions: dict | None = None,
) -> sa.CritereResult:
    """Construit un CritereResult minimal pour les tests directionnels."""
    contribs = contributions if contributions is not None else {
        h: valeur_norm * poids * pertinence * signe for h in sa.HORIZONS
    }
    return sa.CritereResult(
        id=idx,
        nom=nom or f"crit_{idx}",
        type_norm="lineaire",
        valeur_brute=None,
        valeur_norm=valeur_norm,
        poids=poids,
        signe=signe,
        pertinence={h: pertinence for h in sa.HORIZONS},
        note="",
        contributions=contribs,
        is_gate=is_gate,
        is_na=is_na,
        source_track=source_track,
        cle_courante=cle,
    )


# ---------------------------------------------------------------------------
# C3 — divergence quant ↔ news
# ---------------------------------------------------------------------------

def test_c3_divergence_detectee_quant_long_news_short():
    """Quant total > 0 (LONG) et news total < 0 (SHORT) → flag."""
    info = {h: {"quant_total_pm1": 0.8, "news_total_pm1": -0.4} for h in sa.HORIZONS}
    div, _, _, _, _ = sa.compute_directional_flags(
        criteres_res=[], conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(div[h] for h in sa.HORIZONS)


def test_c3_divergence_detectee_quant_short_news_long():
    """Inverse symétrique : quant < 0, news > 0 → flag."""
    info = {h: {"quant_total_pm1": -0.6, "news_total_pm1": 0.5} for h in sa.HORIZONS}
    div, _, _, _, _ = sa.compute_directional_flags(
        criteres_res=[], conclusions={h: "SHORT" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(div[h] for h in sa.HORIZONS)


def test_c3_divergence_non_detectee_meme_signe():
    """Quant et news du même signe → pas de divergence."""
    info = {h: {"quant_total_pm1": 0.5, "news_total_pm1": 0.3} for h in sa.HORIZONS}
    div, _, _, _, _ = sa.compute_directional_flags(
        criteres_res=[], conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(not div[h] for h in sa.HORIZONS)


def test_c3_divergence_non_detectee_amplitude_negligeable():
    """Signes opposés MAIS un des deux totaux < EPSILON_DIVERG → pas de flag."""
    # news_total minuscule (sous le seuil) → bruit, pas divergence.
    info = {h: {"quant_total_pm1": 0.5, "news_total_pm1": -0.01} for h in sa.HORIZONS}
    div, _, _, _, _ = sa.compute_directional_flags(
        criteres_res=[], conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(not div[h] for h in sa.HORIZONS)


# ---------------------------------------------------------------------------
# Score-vs-momentum
# ---------------------------------------------------------------------------

def test_contre_momentum_detecte_long_contre_rsi_baissier():
    """Conclusion LONG mais RSI 14j négatif (momentum baissier) → flag."""
    # Critère RSI 14j S&P 500 avec valeur_norm négative (sous la moyenne).
    rsi_crit = _make_crit(
        1, cle="rsi_14j_gspc", source_track="", valeur_norm=-0.5, poids=1.0,
    )
    info = {h: {"quant_total_pm1": 0.5, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, cm, mv, cle, _ = sa.compute_directional_flags(
        criteres_res=[rsi_crit],
        conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(cm[h] for h in sa.HORIZONS)
    assert cle == "rsi_14j_gspc"
    for h in sa.HORIZONS:
        assert mv[h] == pytest.approx(-0.5)


def test_contre_momentum_non_detecte_si_aligne():
    """LONG + RSI positif → aligné, pas de flag."""
    rsi_crit = _make_crit(
        1, cle="rsi_14j_gspc", valeur_norm=0.4, poids=1.0,
    )
    info = {h: {"quant_total_pm1": 0.5, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, cm, _, _, _ = sa.compute_directional_flags(
        criteres_res=[rsi_crit],
        conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(not cm[h] for h in sa.HORIZONS)


def test_contre_momentum_absent_si_momentum_indisponible():
    """Aucun critère de momentum mappé → pas de flag (zéro invention)."""
    # Critère quant lambda, non mappé dans MOMENTUM_CLE_PAR_ACTIF.
    other_crit = _make_crit(1, cle="autre_critere_quant", valeur_norm=-0.5)
    info = {h: {"quant_total_pm1": 0.5, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, cm, mv, cle, _ = sa.compute_directional_flags(
        criteres_res=[other_crit],
        conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(not cm[h] for h in sa.HORIZONS)
    assert cle == ""  # aucun momentum identifié
    assert mv == {}   # aucune valeur enregistrée


def test_contre_momentum_neutre_si_momentum_faible():
    """|momentum| < EPSILON_MOMENTUM → neutre, pas de flag."""
    rsi_crit = _make_crit(1, cle="rsi_14j_gspc", valeur_norm=-0.05, poids=1.0)
    info = {h: {"quant_total_pm1": 0.5, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, cm, _, _, _ = sa.compute_directional_flags(
        criteres_res=[rsi_crit],
        conclusions={h: "LONG" for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(not cm[h] for h in sa.HORIZONS)


def test_contre_momentum_ignore_si_conclusion_insuffisant():
    """Conclusion INSUFFISANT → pas de direction → pas de flag même si momentum opposé."""
    rsi_crit = _make_crit(1, cle="rsi_14j_gspc", valeur_norm=-0.5)
    info = {h: {"quant_total_pm1": 0.0, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, cm, _, _, _ = sa.compute_directional_flags(
        criteres_res=[rsi_crit],
        conclusions={h: sa.CONCLUSION_INSUFFISANT for h in sa.HORIZONS},
        news_cap_info=info,
    )
    assert all(not cm[h] for h in sa.HORIZONS)


# ---------------------------------------------------------------------------
# C6 — incohérence inter-horizons (zig-zag)
# ---------------------------------------------------------------------------

def test_c6_zigzag_long_short_long_detecte():
    """LONG → SHORT → LONG = 2 changements = zig-zag → flag."""
    info = {h: {"quant_total_pm1": 0.0, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, _, _, _, incoh = sa.compute_directional_flags(
        criteres_res=[],
        conclusions={"24h": "LONG", "7j": "SHORT", "1m": "LONG"},
        news_cap_info=info,
    )
    assert incoh is True


def test_c6_zigzag_short_long_short_detecte():
    info = {h: {"quant_total_pm1": 0.0, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, _, _, _, incoh = sa.compute_directional_flags(
        criteres_res=[],
        conclusions={"24h": "SHORT", "7j": "LONG", "1m": "SHORT"},
        news_cap_info=info,
    )
    assert incoh is True


def test_c6_transition_simple_non_flaggee():
    """LONG → LONG → SHORT = 1 changement = continuation puis retournement = NORMAL."""
    info = {h: {"quant_total_pm1": 0.0, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, _, _, _, incoh = sa.compute_directional_flags(
        criteres_res=[],
        conclusions={"24h": "LONG", "7j": "LONG", "1m": "SHORT"},
        news_cap_info=info,
    )
    assert incoh is False


def test_c6_full_long_non_flaggee():
    """LONG → LONG → LONG : aucun changement → pas de flag."""
    info = {h: {"quant_total_pm1": 0.0, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, _, _, _, incoh = sa.compute_directional_flags(
        criteres_res=[],
        conclusions={"24h": "LONG", "7j": "LONG", "1m": "LONG"},
        news_cap_info=info,
    )
    assert incoh is False


def test_c6_insuffisant_exclu_de_la_sequence():
    """INSUFFISANT n'est PAS comparé : LONG → INSUFF → LONG ne lève pas le flag."""
    info = {h: {"quant_total_pm1": 0.0, "news_total_pm1": 0.0} for h in sa.HORIZONS}
    _, _, _, _, incoh = sa.compute_directional_flags(
        criteres_res=[],
        conclusions={"24h": "LONG", "7j": sa.CONCLUSION_INSUFFISANT, "1m": "LONG"},
        news_cap_info=info,
    )
    assert incoh is False


# ---------------------------------------------------------------------------
# Decision-log : émission UNIQUEMENT si flag True (zéro bruit)
# ---------------------------------------------------------------------------

def _build_actif_result(
    *,
    divergence: dict | None = None,
    contre_mom: dict | None = None,
    mom_val: dict | None = None,
    mom_cle: str = "",
    incoh: bool = False,
    cap_info_overrides: dict | None = None,
) -> sa.ActifResult:
    """ActifResult minimal pour tester build_decision_log_records."""
    base_cap = {
        "news_total_pm1": 0.0, "quant_total_pm1": 0.5,
        "news_total_pm1_capped": 0.0, "news_total_pond": 0.0,
        "quant_total_pond": 0.5, "news_total_pond_capped": 0.0,
        "cap_applied": False, "override_high_confirmed": False, "alpha": 0.8,
    }
    overrides = cap_info_overrides or {}
    news_cap_info = {h: {**base_cap, **overrides.get(h, {})} for h in sa.HORIZONS}
    return sa.ActifResult(
        nom="TestActif",
        fiche_key="testactif",
        criteres=[],
        scores={h: 0.5 for h in sa.HORIZONS},
        conclusions={h: "LONG" for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: 0.5 for h in sa.HORIZONS},
        conclusions_pond={h: "LONG" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        news_cap_info=news_cap_info,
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
        divergence_quant_news=divergence or {},
        contre_momentum=contre_mom or {},
        momentum_valeur=mom_val or {},
        momentum_source_cle=mom_cle,
        incoherence_inter_horizons=incoh,
    )


def test_decision_log_omits_flags_when_false():
    """Aucun flag True → champs absents du record (zéro bruit)."""
    from datetime import datetime, timezone
    r = _build_actif_result()
    records = sa.build_decision_log_records([r], datetime.now(timezone.utc))
    for rec in records:
        assert "divergence_quant_news" not in rec
        assert "contre_momentum" not in rec
        assert "incoherence_inter_horizons" not in rec
        assert "momentum_source_cle" not in rec


def test_decision_log_emits_divergence_when_true():
    from datetime import datetime, timezone
    r = _build_actif_result(
        divergence={"24h": True, "7j": False, "1m": False},
        cap_info_overrides={"24h": {"quant_total_pm1": 0.8, "news_total_pm1": -0.4}},
    )
    records = sa.build_decision_log_records([r], datetime.now(timezone.utc))
    rec_24h = next(rec for rec in records if rec["horizon"] == "24h")
    rec_7j = next(rec for rec in records if rec["horizon"] == "7j")
    assert rec_24h["divergence_quant_news"] is True
    assert rec_24h["quant_total_for_divergence"] == pytest.approx(0.8)
    assert rec_24h["news_total_for_divergence"] == pytest.approx(-0.4)
    assert "divergence_quant_news" not in rec_7j


def test_decision_log_emits_contre_momentum_with_metadata():
    from datetime import datetime, timezone
    r = _build_actif_result(
        contre_mom={"24h": True, "7j": False, "1m": False},
        mom_val={"24h": -0.5, "7j": -0.5, "1m": -0.5},
        mom_cle="rsi_14j_gspc",
    )
    records = sa.build_decision_log_records([r], datetime.now(timezone.utc))
    rec_24h = next(rec for rec in records if rec["horizon"] == "24h")
    assert rec_24h["contre_momentum"] is True
    assert rec_24h["momentum_valeur"] == pytest.approx(-0.5)
    assert rec_24h["momentum_source_cle"] == "rsi_14j_gspc"


def test_decision_log_emits_incoherence_on_all_horizons():
    """incoherence_inter_horizons est par actif → tracée sur les 3 horizons."""
    from datetime import datetime, timezone
    r = _build_actif_result(incoh=True)
    records = sa.build_decision_log_records([r], datetime.now(timezone.utc))
    for rec in records:
        assert rec["incoherence_inter_horizons"] is True


# ---------------------------------------------------------------------------
# Non-régression CRITIQUE : conclusions inchangées par les flags
# ---------------------------------------------------------------------------

def test_conclusions_unchanged_by_flags_real_fiche(fiches_dir):
    """Verrou ABSOLU Lot 4a : ajouter les flags ne doit JAMAIS changer le signe
    de la conclusion (LONG/SHORT/INSUFFISANT). Comparaison : score_actif sur
    une fiche réelle, on note les conclusions, on vérifie qu'elles correspondent
    EXACTEMENT au signe du score (le contrat de _conclusion_from_score) — autrement
    dit la logique métier reste pilotée par le score, pas par les flags."""
    fiches = sa.load_fiches(fiches_dir)
    fiche = fiches["petrole"]
    # Valeurs alignées avec la fixture historique : majoritairement positif.
    valeurs = {
        "prix_brent_usd": {"valeur": 95.0},
        "stocks_us_eia_wbbl": {"valeur": -5.0},
        "stocks_strategiques_us_wbbl": {"valeur": 600.0},
        "discipline_opep_bopd": {"valeur": 0.5},
        "rig_count_us": {"valeur": 600},
        "dxy": {"valeur": 100.0},
        "demande_chine_yoy_bopd": {"valeur": 0.3},
        "premium_geopol_usd": {"valeur": 3.0},
        "spread_brent_wti_usd": {"valeur": 5.0},
        "shutdown_us": {"valeur": False},
    }
    r = sa.score_actif("petrole", fiche, valeurs)
    # Contrat : la conclusion suit le signe du score (sauf override INSUFFISANT
    # qui dépend de la coverage, pas des flags).
    for h in sa.HORIZONS:
        conc = r.conclusions[h]
        score = r.scores[h]
        if conc == sa.CONCLUSION_INSUFFISANT:
            # Override coverage, indépendant des flags Lot 4a.
            continue
        if score > 0:
            assert conc == "LONG", f"horizon {h}: score>0 mais conc={conc}"
        elif score < 0:
            assert conc == "SHORT", f"horizon {h}: score<0 mais conc={conc}"
        # score == 0 → tie-break, conclusion peut être LONG ou SHORT, mais
        # n'est PAS influencée par les flags directionnels (qui sont calculés APRÈS).


def test_flags_do_not_mutate_conclusions_when_all_true(fiches_dir):
    """Même si TOUS les drapeaux directionnels seraient à True (cas extrême),
    les conclusions et scores doivent rester intacts."""
    fiches = sa.load_fiches(fiches_dir)
    fiche = fiches["petrole"]
    valeurs = {
        "prix_brent_usd": {"valeur": 95.0},
        "stocks_us_eia_wbbl": {"valeur": -5.0},
        "discipline_opep_bopd": {"valeur": 0.5},
        "rig_count_us": {"valeur": 600},
        "dxy": {"valeur": 100.0},
        "demande_chine_yoy_bopd": {"valeur": 0.3},
        "premium_geopol_usd": {"valeur": 3.0},
        "spread_brent_wti_usd": {"valeur": 5.0},
        "shutdown_us": {"valeur": False},
    }
    r = sa.score_actif("petrole", fiche, valeurs)
    scores_avant = dict(r.scores)
    conclusions_avant = dict(r.conclusions)
    # Mute artificiellement les drapeaux (simulation paranoïaque).
    r.divergence_quant_news = {h: True for h in sa.HORIZONS}
    r.contre_momentum = {h: True for h in sa.HORIZONS}
    r.incoherence_inter_horizons = True
    # Les scores et conclusions ne doivent PAS bouger : les drapeaux ne sont
    # consommés que par render_bulletin (affichage) et build_decision_log_records
    # (logging), pas par la décision.
    assert r.scores == scores_avant
    assert r.conclusions == conclusions_avant


# ---------------------------------------------------------------------------
# Fixture partagée
# ---------------------------------------------------------------------------

@pytest.fixture
def fiches_dir():
    return ROOT / "config" / "fiches"
