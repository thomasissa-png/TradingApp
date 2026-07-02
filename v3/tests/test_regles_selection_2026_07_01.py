"""Règles de sélection validées fondateur (GO explicite 01/07).

Rejoue les cas de référence du bulletin du 01/07 avec des données MOCKÉES :

  1. Véto « news contre la tendance courte » (sélection uniquement) — cas Cacao.
  2. Plancher d'intensité (note normalisée) — garde les nets, écarte les mous.
  3. Conviction plafonnée « fragile (capteurs éteints) » — cas Blé (USDA poids 11 n/a).
  4. Cutover pertinence 24h EUR/USD (usd_jpy_proxy_risk 0.7 -> 0.1, flip SHORT->LONG).

Le point 5 (mention météo cacao « à valider » retirée) est couvert par
`test_raison_cellule.py::test_meteo_cacao_convention_validee_01_07`.

PUR : zéro réseau, zéro LLM. Isolé de l'events-log LIVE via monkeypatch.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 7, 1, 7, 0, tzinfo=timezone.utc)
SEUIL = 0.6


@pytest.fixture(autouse=True)
def _isole_news_flux(monkeypatch):
    """Aucune news adverse par défaut (le ↯ feed lit sinon l'events-log live)."""
    import bilan_jour as bj

    monkeypatch.setattr(bj, "cause_news_high_dir", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", lambda now: {}, raising=False)


# ---------------------------------------------------------------------------
# Helpers de construction
# ---------------------------------------------------------------------------
def _crit(
    cle: str,
    poids: float,
    eff_24h: float,
    *,
    source_track: str = "",
    is_na: bool = False,
    valeur_norm: Optional[float] = 1.0,
) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle,
        nom=cle,
        type_norm="lineaire",
        valeur_brute=1.0,
        valeur_norm=valeur_norm,
        poids=poids,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions={h: (eff_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        cle_courante=cle,
        source_track=source_track,
        is_na=is_na,
    )


def _actif(
    nom: str,
    fiche_key: str,
    criteres: List[sa.CritereResult],
    *,
    score_24h: float,
    direction: str,
    coverage: float = 1.0,
) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=fiche_key,
        criteres=criteres,
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={
            h: (direction if h == "24h" else sa.CONCLUSION_INSUFFISANT)
            for h in sa.HORIZONS
        },
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=coverage,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


# ===========================================================================
# Point 1 — Véto « news contre la tendance courte » (cas Cacao 01/07)
# ===========================================================================
def _cacao_news_contre_tendance() -> sa.ActifResult:
    """Cacao LONG : driver dominant = news El Niño (+3.2, source ia) ET tendance
    3j à contre-sens (momentum_prix_3j négatif). Reproduit le cas 01/07."""
    crits = [
        _crit("maladies_cabosses", 5.0, 3.20, source_track="ia_synthese"),  # news dom.
        _crit("hf_positioning_flux_options", 5.0, 1.20),                    # 2e (quant)
        _crit("momentum_prix_3j_cacao", 6.0, -1.03),                        # tendance 3j ⊥
        _crit("momentum_prix_20j_cacao", 6.0, 0.50),
    ]
    return _actif("Cacao", "cacao", crits, score_24h=3.87, direction="LONG")


def _cafe_tendance_alignee() -> sa.ActifResult:
    """Café LONG : driver dominant NON news (momentum) → pas de véto → sélectionné."""
    crits = [
        _crit("momentum_prix_3j_cafe", 6.0, 3.00),   # tendance ALIGNÉE (positive)
        _crit("usd_brl_cafe", 6.0, 1.50),
    ]
    return _actif("Café", "cafe", crits, score_24h=4.50, direction="LONG")


def _sucre_driver_quant() -> sa.ActifResult:
    """Sucre LONG : driver dominant quant (météo), tendance 3j alignée → sélectionné."""
    crits = [
        _crit("meteo_bresil_sucre", 7.0, 3.20),
        _crit("momentum_prix_3j_sucre", 6.0, 1.00),  # alignée
    ]
    return _actif("Sucre", "sucre", crits, score_24h=4.20, direction="LONG")


def test_p1_veto_predicat_cacao():
    cacao = _cacao_news_contre_tendance()
    # driver dominant est bien la news, et la tendance 3j est à contre-sens.
    assert sa._driver_dominant_est_news(cacao, "24h") is True
    assert sa._tendance_courte_3j_contre_call(cacao, "24h") is True
    assert sa._cell_news_contre_tendance_courte(cacao, "24h") is True


def test_p1_cacao_ecarte_cafe_et_sucre_restent():
    res = [
        _cacao_news_contre_tendance(),
        _cafe_tendance_alignee(),
        _sucre_driver_quant(),
    ]
    ecartes_tend: list = []
    picks = sa.select_paris_du_jour(
        res, NOW, seuil_conviction=SEUIL, ecartes_tendance=ecartes_tend
    )
    noms = [p["actif"] for p in picks]
    # Cacao écarté par le véto ; Café et Sucre restent sélectionnés.
    assert "Cacao" not in noms
    assert "Café" in noms and "Sucre" in noms
    # Transparence : Cacao apparaît dans les écartés « tendance courte ».
    assert {e["actif"] for e in ecartes_tend} == {"Cacao"}


def test_p1_motif_hors_top_et_ligne_ecartes():
    res = [
        _cacao_news_contre_tendance(),
        _cafe_tendance_alignee(),
        _sucre_driver_quant(),
    ]
    hors: list = []
    sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL, hors_top=hors)
    motifs = {e["fiche_key"]: e["motif"] for e in hors}
    assert motifs["cacao"] == "écarté : news contre la tendance courte"
    # Le bloc « 🎯 Aujourd'hui » mentionne l'écart.
    block = "\n".join(sa.build_paris_du_jour_block(res, NOW, seuil_conviction=SEUIL))
    assert "news contre la tendance courte" in block and "Cacao" in block


def test_p1_pas_de_veto_si_driver_non_news():
    """Même tendance 3j à contre-sens, mais driver dominant QUANT → pas de véto."""
    crits = [
        _crit("driver_quant", 8.0, 3.20),            # dominant NON news
        _crit("momentum_prix_3j_x", 6.0, -1.00),     # 3j à contre-sens
    ]
    r = _actif("X", "x", crits, score_24h=2.20, direction="LONG")
    assert sa._cell_news_contre_tendance_courte(r, "24h") is False


# ===========================================================================
# Point 2 — Plancher d'intensité (note normalisée), calibration 01/07
# ===========================================================================
def _cell_intensite(nom: str, fk: str, note_norm_cible: float, direction: str):
    """1 critère poids 10, pertinence 1.0 → denom d'intensité = 10 ; score brut
    imposé = note_norm_cible × 10 → note normalisée = note_norm_cible. Score brut
    >= NEUTRAL_BAND (jouable) : la SEULE cause d'écart possible est l'intensité."""
    brute = note_norm_cible * 10.0
    signed = brute if direction == "LONG" else -brute
    crits = [_crit("q", 10.0, signed)]
    return _actif(nom, fk, crits, score_24h=signed, direction=direction)


def test_p2_seuil_constant_dans_le_gap():
    # Gap empirique 01/07 entre le plus faible NET (Or 0.48) et le plus fort MOU
    # (EUR/USD 0.23). Le seuil doit être dans ]0.23 ; 0.48].
    assert 0.23 < sa.SELECTION_INTENSITE_MIN <= 0.48
    assert sa.SELECTION_INTENSITE_MIN == 0.30


def test_p2_garde_or_ecarte_eurusd_et_cac():
    res = [
        _cell_intensite("Or", "or", 0.48, "SHORT"),        # net → gardé
        _cell_intensite("EUR/USD", "eurusd", 0.23, "SHORT"),  # mou → écarté
        _cell_intensite("CAC 40", "cac40", 0.16, "SHORT"),    # mou → écarté
    ]
    hors: list = []
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL, hors_top=hors)
    noms = [p["actif"] for p in picks]
    assert noms == ["Or"]
    motifs = {e["fiche_key"]: e["motif"] for e in hors}
    assert motifs["eurusd"] == "écarté : intensité sous le plancher"
    assert motifs["cac40"] == "écarté : intensité sous le plancher"


def test_p2_predicat_intensite():
    faible = _cell_intensite("Mou", "mou", 0.23, "SHORT")
    net = _cell_intensite("Net", "net", 0.48, "SHORT")
    assert sa._intensite_sous_plancher(faible, "24h") is True
    assert sa._intensite_sous_plancher(net, "24h") is False


# ===========================================================================
# Point 3 — Conviction plafonnée « fragile (capteurs éteints) » (cas Blé)
# ===========================================================================
def _ble_capteur_max_na(coverage: float = 0.75) -> sa.ActifResult:
    """Blé LONG : stocks USDA (poids 11, le PLUS LOURD) n/a → capteur max éteint.
    Couverture VOLONTAIREMENT haute (>= CONVICTION_COVERAGE_MIN) pour isoler le
    plafond « capteurs éteints » du plafond « couverture insuffisante »."""
    # Contributions équilibrées (aucune > 50 % du total) pour éviter le drapeau
    # ◧ mono-critère : on isole bien le plafond « capteurs éteints ».
    crits = [
        _crit("usda_wasde_stocks_to_use", 11.0, 0.0, is_na=True, valeur_norm=None),
        _crit("geopolitique_mer_noire", 8.0, 2.00, source_track="ia"),
        _crit("cftc_cot_wheat", 5.0, 1.60),
        _crit("momentum_prix_3j_ble", 6.0, 1.70),
    ]
    return _actif("Blé", "ble", crits, score_24h=5.30, direction="LONG",
                  coverage=coverage)


def test_p3_predicat_capteurs_eteints_max_na():
    ble = _ble_capteur_max_na()
    assert sa._capteurs_lourds_eteints(ble) is True


def test_p3_conviction_plafonnee():
    ble = _ble_capteur_max_na()
    # Sans le garde-fou, |score| 5.30 >= seuil → « forte ». Avec : plafonnée.
    assert sa._conviction_cell(ble, "24h", SEUIL) == "fragile (capteurs éteints)"


def test_p3_inéligible_selection():
    ble = _ble_capteur_max_na()
    # Un actif net à côté pour vérifier que la sélection fonctionne mais exclut le blé.
    autre = _actif(
        "Or", "or", [_crit("q", 5.0, -3.0)], score_24h=-3.0, direction="SHORT"
    )
    picks = sa.select_paris_du_jour([ble, autre], NOW, seuil_conviction=SEUIL)
    assert "Blé" not in [p["actif"] for p in picks]
    assert "Or" in [p["actif"] for p in picks]


def test_p3_condition_b_deux_capteurs_lourds_na():
    """Condition (b) : >= 2 critères de poids >= 8 n/a (le max n'est PAS forcément na)."""
    crits = [
        _crit("gros_a", 10.0, 2.0),                     # poids MAX, vivant
        _crit("gros_b", 9.0, 0.0, is_na=True, valeur_norm=None),   # lourd na
        _crit("gros_c", 8.0, 0.0, is_na=True, valeur_norm=None),   # lourd na
        _crit("petit", 4.0, 1.0),
    ]
    r = _actif("Z", "z", crits, score_24h=3.0, direction="LONG", coverage=0.8)
    assert sa._max_weight_critere_is_na(r) is False   # le max (10) est vivant
    assert sa._capteurs_lourds_eteints(r) is True     # mais 2 lourds (9, 8) na


# ===========================================================================
# Point 4 — Cutover pertinence 24h EUR/USD (usd_jpy_proxy_risk 0.7 -> 0.1)
# ===========================================================================
def test_p4_fiche_eurusd_pertinence_usd_jpy():
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "eurusd.yml").read_text())
    crit = next(
        c for c in fiche["criteres"]
        if c.get("cle_courante") == "usd_jpy_proxy_risk"
    )
    pert = crit["pertinence"]
    assert pert["24h"] == 0.1          # réduit (était 0.7)
    assert pert["7j"] == 0.8           # INCHANGÉ
    assert pert["1m"] == 0.5           # INCHANGÉ


def test_p4_flip_short_vers_long_replay_01_07():
    """Replay numérique du 01/07 : effets 24h réels d'EUR/USD. Avec usd_jpy à
    pertinence 0.7 le score est SHORT (-1.35) ; réduit à 0.1 il devient LONG."""
    # Effets 24h réels (decision-log 2026-07-01), usd_jpy à pertinence 0.7.
    effets_hors_usdjpy = {
        "momentum_prix_3j": +1.473,
        "momentum_prix_7j": +1.458,
        "differentiel_taux_2y": -0.942,
        "dxy_trend_20j": -0.879,
        "momentum_prix_20j": -0.305,
        "cftc_cot_eur": +0.296,
        "differentiel_taux_10y": +0.222,
    }
    usdjpy_eff_07 = -2.676  # à pertinence 0.7
    score_old = sum(effets_hors_usdjpy.values()) + usdjpy_eff_07
    assert score_old < 0  # SHORT (≈ -1.35)
    # L'effet est linéaire en pertinence → à 0.1 : × (0.1 / 0.7).
    usdjpy_eff_new = usdjpy_eff_07 * (0.1 / 0.7)
    score_new = sum(effets_hors_usdjpy.values()) + usdjpy_eff_new
    assert score_new > 0  # LONG (≈ +0.94) : dominé par les tendances courtes
