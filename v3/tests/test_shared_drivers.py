"""Reco A (audit corrélation cachée 05/06) — Drivers macro partagés.

FLAG-ONLY : ces tests vérifient la DÉTECTION et le RENDU du bloc « ⚭ Drivers
macro partagés », plus la présence du champ shadow `drivers_partages` dans le
decision-log. Aucun score / conclusion / mesure n'est modifié.

Cas synthétiques, zéro réseau, zéro YAML : on stube directement les objets
critère/actif (le module ne lit que .nom, .criteres, .contributions, .is_gate,
.is_na, .cle_courante).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import shared_drivers as sd  # noqa: E402

HORIZONS = ("24h", "7j", "1m")


@dataclass
class _Crit:
    cle_courante: str
    contributions: Dict[str, float]
    nom: str = ""
    is_gate: bool = False
    is_na: bool = False


@dataclass
class _Actif:
    nom: str
    criteres: List[_Crit] = field(default_factory=list)
    # compute_selection_shared_drivers lit la conclusion par horizon (sens du call)
    # et, optionnellement, fiche_key (tendance propre). Défauts inoffensifs pour les
    # tests de compute_shared_drivers_summary qui ne les lisent pas.
    conclusions: Dict[str, str] = field(default_factory=dict)
    fiche_key: str = ""


def _crit(cle, contrib_all, nom="", is_gate=False, is_na=False):
    """Critère dont la contribution est identique sur les 3 horizons."""
    return _Crit(
        cle_courante=cle,
        contributions={h: contrib_all for h in HORIZONS},
        nom=nom or cle,
        is_gate=is_gate,
        is_na=is_na,
    )


# ===========================================================================
# Détection : driver partagé (≥ 2 fiches) portant ≥ 2 cellules même direction
# ===========================================================================

def test_driver_partage_detecte_sur_deux_actifs_meme_direction():
    """TIPS porte SHORT (signe -) sur 2 actifs, dominant (>50%) → signalé."""
    a = _Actif("Or", [
        _crit("taux_10y_us_reels_tips", -8.0, "Taux réels US"),
        _crit("autre_or", -1.0, "Autre"),
    ])
    b = _Actif("Nasdaq", [
        _crit("taux_10y_us_reels_tips", -7.0, "Taux réels US"),
        _crit("autre_nasdaq", -1.0, "Autre"),
    ])
    summary = sd.compute_shared_drivers_summary([a, b], HORIZONS)
    assert len(summary) == 1
    d = summary[0]
    assert d["cle"] == "taux_10y_us_reels_tips"
    assert d["label"] == "Taux réels US (TIPS)"
    assert d["direction"] == "SHORT"
    assert d["actifs"] == ["Nasdaq", "Or"]
    # 2 actifs × 3 horizons (contrib identique par horizon) = 6 cellules portées.
    assert d["n_cellules"] == 6
    assert d["n_actifs"] == 2
    assert d["part_max"] > 0.5


def test_driver_sur_une_seule_fiche_non_signale():
    """HY spread présent sur 1 seul actif (audit : pas un doublon) → rien."""
    a = _Actif("SP500", [
        _crit("hy_credit_spread", -8.0),
        _crit("autre", -1.0),
    ])
    b = _Actif("Or", [
        _crit("taux_10y_us_reels_tips", -8.0),
        _crit("autre2", -1.0),
    ])
    summary = sd.compute_shared_drivers_summary([a, b], HORIZONS)
    # hy_credit_spread : 1 seule fiche → pas partagé. tips : 1 seule fiche → idem.
    assert summary == []


def test_driver_sous_le_seuil_de_part_non_signale():
    """Driver partagé mais NON dominant (< 50% du score) → pas de signalement."""
    # tips contribue -2 face à -10 d'un critère propre → part = 2/12 ≈ 0.17 < 0.5.
    a = _Actif("Or", [
        _crit("taux_10y_us_reels_tips", -2.0),
        _crit("propre_or", -10.0),
    ])
    b = _Actif("Nasdaq", [
        _crit("taux_10y_us_reels_tips", -2.0),
        _crit("propre_nasdaq", -10.0),
    ])
    summary = sd.compute_shared_drivers_summary([a, b], HORIZONS)
    assert summary == []


def test_na_et_gate_ignores():
    """Un critère n/a ou gate ne compte PAS comme présent (zéro invention)."""
    a = _Actif("Or", [
        _crit("taux_10y_us_reels_tips", -8.0),
        _crit("gate_regime_extreme", 0.0, is_gate=True),
    ])
    # Sur Nasdaq, tips est n/a → la fiche ne le « porte » pas → pas partagé.
    crit_na = _Crit("taux_10y_us_reels_tips", {h: None for h in HORIZONS}, is_na=True)
    b = _Actif("Nasdaq", [crit_na, _crit("propre", -5.0)])
    summary = sd.compute_shared_drivers_summary([a, b], HORIZONS)
    # tips présent (réel) sur 1 seule fiche (Or) → pas partagé → rien.
    assert summary == []


def test_directions_opposees_non_fusionnees():
    """Même driver SHORT sur 2 actifs et LONG sur 2 autres → 2 entrées distinctes,
    jamais fusionnées (sinon le message tromperait)."""
    shorts = [
        _Actif("Or", [_crit("dxy_trend_20j", -8.0), _crit("p1", -1.0)]),
        _Actif("Argent", [_crit("dxy_trend_20j", -8.0), _crit("p2", -1.0)]),
    ]
    longs = [
        _Actif("EURUSD", [_crit("dxy_trend_20j", 8.0), _crit("p3", 1.0)]),
        _Actif("Cuivre", [_crit("dxy_trend_20j", 8.0), _crit("p4", 1.0)]),
    ]
    summary = sd.compute_shared_drivers_summary(shorts + longs, HORIZONS)
    dirs = sorted(d["direction"] for d in summary)
    assert dirs == ["LONG", "SHORT"]
    for d in summary:
        assert d["cle"] == "dxy_trend_20j"
        assert d["label"] == "Dollar (DXY)"


# ===========================================================================
# Rendu du bloc bulletin
# ===========================================================================

def test_rendu_bloc_present_quand_driver_signale():
    a = _Actif("Or", [_crit("taux_10y_us_reels_tips", -8.0), _crit("x", -1.0)])
    b = _Actif("Nasdaq", [_crit("taux_10y_us_reels_tips", -7.0), _crit("y", -1.0)])
    summary = sd.compute_shared_drivers_summary([a, b], HORIZONS)
    block = sd.build_shared_drivers_block(summary)
    text = "\n".join(block)
    assert "## ⚭ Drivers macro partagés" in text
    assert "Taux réels US (TIPS)" in text
    assert "SHORT" in text
    assert "Or" in text and "Nasdaq" in text
    assert "fausserait ensemble" in text


def test_pas_de_bloc_si_aucun_driver():
    """Aucun driver signalé → bloc vide (anti-bruit, la section n'existe pas)."""
    assert sd.build_shared_drivers_block([]) == []


# ===========================================================================
# Recentrage Sélection (fondateur 25/06) — le bloc ⚭ ne porte plus sur les 36
# cellules mais UNIQUEMENT sur les paris réellement engagés (24h + 7j + 1m).
# ===========================================================================

def test_selection_shared_drivers_signale_si_deux_paris_meme_driver():
    """Deux paris DISTINCTS de la Sélection portés par la même FAMILLE, même sens
    → signalé (corrélation cachée entre nos propres positions)."""
    argent = _Actif("Argent", [
        _crit("taux_10y_us_reels_tips", -8.0, "Taux réels US"),
        _crit("propre_argent", -1.0),
    ], conclusions={"24h": "SHORT"})
    orr = _Actif("Or", [
        _crit("taux_10y_us_reels_tips", -8.0, "Taux réels US"),
        _crit("propre_or", -1.0),
    ], conclusions={"7j": "SHORT"})
    # Argent retenu en pari 24h, Or en swing 7j → 2 actifs distincts, même famille.
    summary = sd.compute_selection_shared_drivers([(argent, "24h"), (orr, "7j")])
    assert len(summary) == 1
    assert summary[0]["famille"] == "taux_dollar"
    assert summary[0]["actifs"] == ["Argent", "Or"]
    assert summary[0]["actifs_calls"] == {"Argent": "Short", "Or": "Short"}
    assert summary[0]["n_actifs"] == 2


def test_selection_shared_drivers_calls_opposes_meme_pari_dollar():
    """RÉGRESSION (fondateur 29/06) : EUR/USD SHORT et USD/JPY LONG ont des CALLS
    opposés mais parient le MÊME sens du dollar (famille taux_dollar) → doivent être
    signalés ENSEMBLE. L'ancienne version (group par signe de contribution) les ratait."""
    # Dollar en hausse : pousse EUR/USD vers le SHORT (contrib négative) et USD/JPY
    # vers le LONG (contrib positive). Familles : dxy_trend_20j ∈ taux_dollar.
    eurusd = _Actif("EUR/USD", [
        _crit("differentiel_taux_2y_us_de", -8.0, "Écart taux US-DE"),
        _crit("propre_eurusd", -1.0),
    ], conclusions={"24h": "SHORT"})
    usdjpy = _Actif("USD/JPY", [
        _crit("dxy_trend_20j", +8.0, "Tendance du dollar"),
        _crit("propre_usdjpy", +1.0),
    ], conclusions={"24h": "LONG"})
    summary = sd.compute_selection_shared_drivers([(eurusd, "24h"), (usdjpy, "24h")])
    assert len(summary) == 1
    assert summary[0]["famille"] == "taux_dollar"
    assert summary[0]["actifs"] == ["EUR/USD", "USD/JPY"]
    assert summary[0]["actifs_calls"] == {"EUR/USD": "Short", "USD/JPY": "Long"}


def test_selection_shared_drivers_ride_vs_fade_non_fusionnes():
    """Un actif qui RIDE le dollar et un autre qui le FADE = couverture, pas
    concentration → PAS fusionnés (sens opposés du pari sur le driver)."""
    # EUR/USD SHORT ride le dollar (dollar up, contrib SHORT alignée au call).
    eurusd = _Actif("EUR/USD", [_crit("dxy_trend_20j", -8.0), _crit("x", -1.0)],
                    conclusions={"24h": "SHORT"})
    # Or LONG mais le dollar pousse SHORT (contrib négative CONTRE le call LONG) →
    # Or parie que le dollar SE RETOURNE → fade. align opposé → groupe distinct.
    orr = _Actif("Or", [_crit("dxy_trend_20j", -8.0), _crit("y", +9.0)],
                 conclusions={"7j": "LONG"})
    summary = sd.compute_selection_shared_drivers([(eurusd, "24h"), (orr, "7j")])
    assert summary == []  # ride (EUR/USD) ≠ fade (Or) → aucun pari commun signalé


def test_selection_shared_drivers_silencieux_si_un_seul_actif():
    """Un même actif tenu sur 2 horizons (Or 7j + Or 1m) = 1 pari → AUCUN signalement."""
    orr = _Actif("Or", [
        _crit("taux_10y_us_reels_tips", -8.0, "Taux réels US"),
        _crit("propre_or", -1.0),
    ], conclusions={"7j": "SHORT", "1m": "SHORT"})
    assert sd.compute_selection_shared_drivers([(orr, "7j"), (orr, "1m")]) == []


def test_selection_shared_drivers_silencieux_si_drivers_differents():
    """Deux paris portés par des familles distinctes → pas de pari répété → silence."""
    petrole = _Actif("Pétrole", [_crit("stocks_brut_us", -8.0, "Stocks brut US")],
                     conclusions={"24h": "SHORT"})
    cafe = _Actif("Café", [_crit("tendance_cafe", 8.0, "Tendance café")],
                  conclusions={"7j": "LONG"})
    assert sd.compute_selection_shared_drivers([(petrole, "24h"), (cafe, "7j")]) == []


def test_selection_shared_drivers_bloc_rendu():
    argent = _Actif("Argent", [_crit("taux_10y_us_reels_tips", -8.0), _crit("x", -1.0)],
                    conclusions={"24h": "SHORT"})
    orr = _Actif("Or", [_crit("taux_10y_us_reels_tips", -8.0), _crit("y", -1.0)],
                 conclusions={"7j": "SHORT"})
    summary = sd.compute_selection_shared_drivers([(argent, "24h"), (orr, "7j")])
    text = "\n".join(sd.build_selection_shared_drivers_block(summary))
    assert "## ⚭ Drivers macro partagés" in text
    assert "Argent" in text and "Or" in text
    assert sd.build_selection_shared_drivers_block([]) == []


# ===========================================================================
# Champ shadow par cellule (decision-log requêtable)
# ===========================================================================

def test_cell_shared_drivers_liste_le_driver_dominant():
    a = _Actif("Or", [_crit("taux_10y_us_reels_tips", -8.0), _crit("x", -1.0)])
    b = _Actif("Nasdaq", [_crit("taux_10y_us_reels_tips", -7.0), _crit("y", -1.0)])
    cles = sd.compute_shared_cles([a, b], HORIZONS)
    assert "taux_10y_us_reels_tips" in cles
    cell = sd.compute_cell_shared_drivers(a, "7j", cles)
    assert len(cell) == 1
    assert cell[0]["cle"] == "taux_10y_us_reels_tips"
    assert cell[0]["part"] > 0.5
    assert cell[0]["signe"] == -1


def test_cell_shared_drivers_vide_si_non_partage():
    a = _Actif("Or", [_crit("propre_or", -8.0)])
    b = _Actif("Nasdaq", [_crit("propre_nasdaq", -7.0)])
    cles = sd.compute_shared_cles([a, b], HORIZONS)
    assert sd.compute_cell_shared_drivers(a, "7j", cles) == []


def test_driver_label_fallback_sur_nom():
    """Clé non mappée → on retombe sur le nom du critère (pas d'invention)."""
    assert sd.driver_label("dxy_trend_20j") == "Dollar (DXY)"
    assert sd.driver_label("cle_inconnue_xyz", "Mon Critère") == "Mon Critère"


# ===========================================================================
# Faux consensus élargi (audit fond 22/06) : seuil 0.30 pour le bloc ⚭, mais
# l'attribution « Porté par » (cell_shared_drivers) reste à 0.50.
# ===========================================================================

def test_faux_consensus_capte_driver_secondaire_30_a_50pct():
    """tips à 40% (entre 0.30 et 0.50) → signalé dans le bloc ⚭ (corrélation
    cachée), mais ABSENT de l'attribution « Porté par » de la cellule (0.50)."""
    # tips -4 vs propre -6 → part = 4/10 = 0.40 : ≥ consensus (0.30), < dominant (0.50).
    a = _Actif("Nasdaq", [
        _crit("taux_10y_us_reels_tips", -4.0, "Taux réels US"),
        _crit("propre_nasdaq", -6.0),
    ])
    b = _Actif("S&P 500", [
        _crit("taux_10y_us_reels_tips", -4.0, "Taux réels US"),
        _crit("propre_sp", -6.0),
    ])
    # Bloc faux consensus : tips capté (0.40 ≥ 0.30).
    summary = sd.compute_shared_drivers_summary([a, b], HORIZONS)
    assert len(summary) == 1
    assert summary[0]["cle"] == "taux_10y_us_reels_tips"
    assert summary[0]["actifs"] == ["Nasdaq", "S&P 500"]
    # Attribution « Porté par » de la cellule : tips NON listé (0.40 < 0.50).
    cles = sd.compute_shared_cles([a, b], HORIZONS)
    assert sd.compute_cell_shared_drivers(a, "24h", cles) == []


def test_faux_consensus_respecte_le_plancher_30pct():
    """Driver partagé sous 0.30 → toujours exclu du bloc ⚭ (pas de sur-signalement)."""
    # tips -2 vs propre -8 → part = 2/10 = 0.20 < 0.30.
    a = _Actif("Or", [_crit("taux_10y_us_reels_tips", -2.0), _crit("p_or", -8.0)])
    b = _Actif("Nasdaq", [_crit("taux_10y_us_reels_tips", -2.0), _crit("p_nq", -8.0)])
    assert sd.compute_shared_drivers_summary([a, b], HORIZONS) == []
    assert sd.driver_label("cle_inconnue_xyz") == "cle_inconnue_xyz"


# ===========================================================================
# Intégration via le scoring réel (score_actif + render_bulletin + decision-log)
# Pas de réseau : fiche + valeurs synthétiques (cf. test_bulletin_top3_fusion).
# ===========================================================================

from datetime import datetime, timezone  # noqa: E402

import scoring_analyste as sa  # noqa: E402

_NOW = datetime(2026, 6, 10, 9, 0, tzinfo=timezone.utc)


def _fiche_tips(nom: str = "TestActif", signe: int = -1) -> dict:
    """Fiche dont le critère DOMINANT (poids fort) est le driver macro partagé
    `taux_10y_us_reels_tips`, plus un critère propre faible. Le `nom` (champ
    `actif`) doit être distinct par fiche : le scoring dérive r.nom de ce champ
    et la détection compte les fiches DISTINCTES par nom."""
    return {
        "actif": nom,
        "criteres": [
            {"id": 1, "nom": "Taux d'intérêt réels US (10 ans)",
             "cle_courante": "taux_10y_us_reels_tips", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": signe, "poids": 12,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 2, "nom": "Critère propre", "cle_courante": "propre",
             "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0, "cap": 5.0,
             "signe": 1, "poids": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
        ],
    }


def _vals_tips(tips_val: float, propre_val: float = 0.1) -> dict:
    return {
        "taux_10y_us_reels_tips": {"valeur": tips_val, "source_track": "fred"},
        "propre": {"valeur": propre_val, "source_track": "twelvedata"},
    }


def test_integration_render_bulletin_affiche_le_bloc():
    """Deux actifs portés par TIPS (>50%, même direction) → bloc dans le bulletin."""
    a = sa.score_actif("Or", _fiche_tips("Or"), _vals_tips(0.7))
    b = sa.score_actif("Nasdaq", _fiche_tips("Nasdaq"), _vals_tips(0.7))
    bulletin = sa.render_bulletin([a, b], {}, _NOW, "h", "ok")
    assert "## ⚭ Drivers macro partagés" in bulletin
    assert "Taux réels US (TIPS)" in bulletin
    # Légende compacte : ⚭ présent car le bloc est émis.
    assert "⚭ driver macro partagé" in bulletin


def test_integration_pas_de_bloc_si_un_seul_actif_porteur():
    """Un seul actif porte TIPS → driver non partagé → pas de bloc ni de ⚭."""
    a = sa.score_actif("Or", _fiche_tips("Or"), _vals_tips(0.7))
    # Nasdaq sans le critère partagé.
    fiche_b = {"actif": "Nasdaq", "criteres": [
        {"id": 1, "nom": "Propre", "cle_courante": "propre_b", "normalisation": "lineaire",
         "centre": 0.0, "echelle": 1.0, "cap": 5.0, "signe": -1, "poids": 10,
         "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}}]}
    b = sa.score_actif("Nasdaq", fiche_b, {"propre_b": {"valeur": 0.7, "source_track": "twelvedata"}})
    bulletin = sa.render_bulletin([a, b], {}, _NOW, "h", "ok")
    assert "## ⚭ Drivers macro partagés" not in bulletin
    assert "⚭ driver macro partagé" not in bulletin


def test_integration_decision_log_contient_drivers_partages():
    """Le champ shadow `drivers_partages` est présent et requêtable par cellule."""
    a = sa.score_actif("Or", _fiche_tips("Or"), _vals_tips(0.7))
    b = sa.score_actif("Nasdaq", _fiche_tips("Nasdaq"), _vals_tips(0.7))
    records = sa.build_decision_log_records([a, b], _NOW)
    assert records, "au moins une cellule attendue"
    for rec in records:
        assert "drivers_partages" in rec
    # Au moins une cellule porte le driver partagé TIPS.
    porteuses = [r for r in records if r["drivers_partages"]]
    assert porteuses
    drv = porteuses[0]["drivers_partages"][0]
    assert drv["cle"] == "taux_10y_us_reels_tips"
    assert "part" in drv and "signe" in drv


def test_integration_zero_impact_sur_scores_et_conclusions():
    """Garde-fou : drivers_partages ne touche NI score NI conclusion (flag-only)."""
    a = sa.score_actif("Or", _fiche_tips("Or"), _vals_tips(0.7))
    scores_avant = dict(a.scores)
    concl_avant = dict(a.conclusions)
    _ = sa.build_decision_log_records([a], _NOW)
    _ = sa.render_bulletin([a], {}, _NOW, "h", "ok")
    assert a.scores == scores_avant
    assert a.conclusions == concl_avant
