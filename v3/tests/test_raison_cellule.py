"""Tests ciblés — « raison principale » par cellule (Synthèse des décisions).

Couvre les garanties de l'audit `/tmp/audit-marche-raisons.md` :
  (a) la raison va TOUJOURS dans le sens de la conclusion (jamais à contre-sens,
      cas S&P 7j net-carrier) ;
  (b) quasi-neutre (|note| < NEUTRAL_BAND) → libellé neutre, pas de direction ;
  (c) gate (⚑ FOMC) jamais cité ;
  (d) fallback nom canonique si driver hors config ;
  (e) meteo_cacao → phrase neutre (signe douteux) ;
  (f) verrou PUR RENDU : aucune mutation de conclusion/score.

PUR RENDU : zéro LLM, zéro réseau.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import scoring_analyste as sa  # noqa: E402


def _crit(
    nom: str,
    cle: str,
    contribs: Dict[str, float],
    *,
    signe: int = 1,
    is_gate: bool = False,
    is_na: bool = False,
) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="lineaire",
        valeur_brute=1.0,
        valeur_norm=1.0,
        poids=5.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions=dict(contribs),
        cle_courante=cle,
        is_gate=is_gate,
        gate_active=is_gate,
        is_na=is_na,
    )


def _actif(
    nom: str,
    criteres: List[sa.CritereResult],
    scores: Dict[str, float],
    conclusions: Dict[str, str],
) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=nom.lower(),
        criteres=criteres,
        scores=dict(scores),
        conclusions=dict(conclusions),
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


# ---------------------------------------------------------------------------
# (a) net-carrier : jamais à contre-sens (cas S&P 7j)
# ---------------------------------------------------------------------------

def test_sp500_7j_net_carrier_jamais_contre_sens():
    """S&P 7j LONG (+5.52) alors que le plus fort |effet| est `taux_10y_us_reels_tips`
    (−6.51, pousse SHORT). La raison DOIT venir d'un porteur LONG (taux 10a / crédit),
    JAMAIS du driver baissier dominant en |effet|."""
    h = "7j"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.51}),
        _crit("Variation taux 10a", "variation_taux_10y_5j", {h: +5.07}),
        _crit("Spread crédit HY", "credit_spread_hy_us", {h: +4.18}),
        _crit("Régime VIX", "vix_regime_seuils", {h: +4.68}),
    ]
    r = _actif("S&P 500", crit, {h: +5.52}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    # Le porteur NET dominant côté LONG est variation_taux_10y_5j (+5.07).
    assert "taux longs US qui refluent" in raison
    assert "(+5.1)" in raison
    # Garantie dure : aucune phrase baissière de taux réels (driver à contre-sens).
    assert "coûtent à porter" not in raison
    assert "taux réels US élevés" not in raison


def test_or_24h_short_driver_taux_reels():
    """Or 24h SHORT (−7.82) : driver porteur SHORT = taux réels élevés."""
    h = "24h"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91}),
        _crit("Géopolitique", "tension_geopolitique", {h: -1.20}),
    ]
    r = _actif("Or", crit, {h: -7.82}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "taux réels US élevés" in raison
    assert "(-3.9)" in raison


# ---------------------------------------------------------------------------
# (b) quasi-neutre → libellé neutre, pas de direction
# ---------------------------------------------------------------------------

def test_vix_7j_quasi_neutre_pas_de_direction():
    """VIX 7j LONG (+0.07) mais |note| < NEUTRAL_BAND → quasi-neutre.
    Driver dominant en |effet| est baissier (term structure −8.00) : on ne doit
    NI raconter une direction LONG, NI citer le driver baissier."""
    h = "7j"
    crit = [
        _crit("Structure de vol", "vix_term_structure", {h: -8.00}),
        _crit("Niveau VIX", "vix_niveau_absolu", {h: +4.04}),
    ]
    r = _actif("VIX", crit, {h: +0.07}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    assert raison == sa._RAISON_QUASI_NEUTRE
    assert "(" not in raison  # aucune contribution chiffrée


def test_cac_1m_quasi_neutre():
    h = "1m"
    crit = [_crit("Spread OAT-Bund", "ecart_taux_fr_de_10a", {h: -3.40})]
    r = _actif("CAC 40", crit, {h: -0.10}, {h: "SHORT"})
    assert sa._raison_cellule(r, h) == sa._RAISON_QUASI_NEUTRE


# ---------------------------------------------------------------------------
# (c) gate FOMC jamais cité
# ---------------------------------------------------------------------------

def test_gate_fomc_jamais_cite():
    """Un gate ⚑ actif (même avec un gros effet apparent) n'est JAMAIS le driver
    de la raison — il est exclu par `is_gate`."""
    h = "24h"
    crit = [
        _crit("Drapeau régime FOMC", "gate_fomc", {h: -99.0}, is_gate=True),
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91}),
    ]
    r = _actif("Or", crit, {h: -7.82}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "FOMC" not in raison
    assert "régime" not in raison.lower()
    assert "taux réels US élevés" in raison


# ---------------------------------------------------------------------------
# (d) fallback nom canonique si driver hors config
# ---------------------------------------------------------------------------

def test_fallback_nom_canonique_hors_config():
    h = "24h"
    crit = [_crit("Critère exotique XYZ", "driver_inconnu_hors_biblio", {h: +2.50})]
    r = _actif("Actif X", crit, {h: +2.50}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    assert raison == "Critère exotique XYZ (+2.5)"


def test_donnee_absente_tiret():
    """Aucun contributeur dans le sens de la conclusion → « — » (jamais de crash)."""
    h = "24h"
    # Conclusion LONG mais le seul critère pousse SHORT → aucun porteur LONG.
    crit = [_crit("Critère contraire", "driver_inconnu_hors_biblio", {h: -2.50})]
    r = _actif("Actif Y", crit, {h: +0.50}, {h: "LONG"})
    assert sa._raison_cellule(r, h) == "—"


# ---------------------------------------------------------------------------
# (e) meteo_cacao → phrase neutre (signe douteux)
# ---------------------------------------------------------------------------

def test_meteo_cacao_phrase_neutre():
    h = "24h"
    crit = [_crit("Météo cacao", "meteo_cacao_cote_ivoire_ghana", {h: +1.37})]
    r = _actif("Cacao", crit, {h: +1.75}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    assert "convention de signe à valider" in raison
    # Pas d'assertion directionnelle bullish/bearish assénée.
    assert "bonne récolte" not in raison


# ---------------------------------------------------------------------------
# matching par préfixe (familles à suffixe d'actif)
# ---------------------------------------------------------------------------

def test_prefixe_momentum_prix():
    h = "24h"
    crit = [_crit("Tendance Brent 20j", "momentum_prix_20j_petrole", {h: -3.38})]
    r = _actif("Pétrole (Brent)", crit, {h: -3.30}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "tendance 20 jours baissière" in raison
    assert "(-3.4)" in raison


# ---------------------------------------------------------------------------
# (f) verrou PUR RENDU : aucune mutation de conclusion/score
# ---------------------------------------------------------------------------

def test_pur_rendu_aucune_mutation():
    h = "7j"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.51}),
        _crit("Régime VIX", "vix_regime_seuils", {h: +4.68}),
    ]
    r = _actif("S&P 500", crit, {h: +5.52}, {h: "LONG"})
    score_avant = dict(r.scores)
    conc_avant = dict(r.conclusions)
    contribs_avant = [dict(c.contributions) for c in r.criteres]
    _ = sa._raison_cellule(r, h)
    _ = sa.build_raisons_block([r])
    assert r.scores == score_avant
    assert r.conclusions == conc_avant
    assert [dict(c.contributions) for c in r.criteres] == contribs_avant


def test_build_block_structure():
    """Le bloc compact contient une ligne par actif, format scannable."""
    h = "24h"
    crit = [_crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91})]
    scores = {hz: (-7.82 if hz == "24h" else 0.0) for hz in sa.HORIZONS}
    conc = {hz: ("SHORT" if hz == "24h" else sa.CONCLUSION_INSUFFISANT) for hz in sa.HORIZONS}
    r = _actif("Or", crit, scores, conc)
    lines = sa.build_raisons_block([r])
    joined = "\n".join(lines)
    assert "**Or**" in joined
    assert "24h :" in joined and "7j :" in joined and "1m :" in joined
    assert "_(SHORT)_" in joined  # direction rappelée sur la cellule franche
