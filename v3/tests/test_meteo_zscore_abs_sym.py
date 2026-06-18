"""Tests (A) — FIX SIGNE MÉTÉO CACAO : normalisation symétrique « écart à la normale ».

Le critère météo cacao (meteo_ci_ghana_precip_30j) est SYMÉTRIQUE : sécheresse
harmattan (z<0) OU pluies excessives (z>0) = offre menacée = HAUSSIER ; pluies
normales (z≈0) = baissier. L'ancienne impl. (zscore linéaire + signe:1) poussait
le cacao SHORT en sécheresse — bug de signe. Le fix `zscore_abs` pénalise l'écart
à la normale (|z|), pas le sens.

Vérifie :
- sécheresse (z<0) → norm POSITIVE → contribution HAUSSIÈRE (signe +1) ;
- excès de pluie (z>0) → norm POSITIVE → HAUSSIER ;
- normal (z≈0) → norm ≈ 0 (neutre) ;
- ZÉRO cutover : à z_courant (>0), la valeur normalisée est INCHANGÉE vs l'ancienne
  formule z/div (donc la direction cacao 17/06 ne bouge pas) ;
- la fiche cacao déclare bien zscore_abs sur le critère id 1.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import criteres_calculator as cc  # noqa: E402
import scoring_analyste as sa  # noqa: E402


# Critère cacao météo tel que dans la fiche (id 1) après fix.
CRIT_CACAO_METEO = {
    "id": 1,
    "cle_courante": "meteo_ci_ghana_precip_30j",
    "normalisation": "zscore_abs",
    "zscore_div": 2,
    "zscore_centre": 0.0,
    "cap": 1.0,
    "signe": 1,
    "poids": 11,
    "source": "NOAA / météo",
}


def _handle(z: float) -> dict:
    """Exécute _handle_meteo avec une anomalie z mockée."""
    with patch.object(cc, "fetch_open_meteo_anomaly", return_value=z):
        res = cc._handle_meteo("meteo_ci_ghana_precip_30j", CRIT_CACAO_METEO, "2026-06-18T00:00:00")
    assert res is not None
    return res


def _contribution(z: float) -> float:
    """norm pré-calculée → consommée par scoring → contribution signée (signe +1)."""
    res = _handle(z)
    norm, _note = sa.normalise(CRIT_CACAO_METEO, res)
    assert norm is not None
    return norm * CRIT_CACAO_METEO["signe"]


# --- Cœur du fix : sécheresse ET excès → haussier ; normal → neutre ---------

def test_secheresse_devient_haussier():
    """z<0 (sécheresse) → contribution POSITIVE = HAUSSIER (bug réparé)."""
    contrib = _contribution(-1.5)
    assert contrib > 0, f"sécheresse devrait être haussière, got {contrib}"


def test_exces_pluie_reste_haussier():
    """z>0 (pluies excessives) → contribution POSITIVE = HAUSSIER (intention)."""
    contrib = _contribution(+1.5)
    assert contrib > 0, f"excès de pluie devrait être haussier, got {contrib}"


def test_normal_est_neutre():
    """z≈0 (pluies normales) → contribution ≈ 0 (neutre, centre=0)."""
    contrib = _contribution(0.0)
    assert abs(contrib) < 1e-9, f"normal devrait être neutre, got {contrib}"


def test_secheresse_et_exces_symetriques():
    """|z| égal des deux côtés → même intensité haussière (symétrie)."""
    assert _contribution(-2.0) == pytest.approx(_contribution(+2.0))


# --- VERROU anti-cutover : direction cacao 17/06 inchangée ------------------

def test_zero_cutover_sur_valeur_actuelle():
    """À z_courant>0 (17/06 : z=0.817, pluies au-dessus de la normale), la valeur
    normalisée zscore_abs est IDENTIQUE à l'ancienne formule z/div → la direction
    cacao du jour NE CHANGE PAS (le fix ne touche que le côté sécheresse)."""
    z_courant = 0.8169146333882531  # valeur réelle du 17/06 (criteres-courants.md)
    div = 2.0
    cap = 1.0
    ancienne_norm = max(-cap, min(cap, z_courant / div))  # ancienne formule linéaire
    nouvelle_norm = cc.zscore_abs_normalisee(z_courant, zscore_div=div, cap=cap, centre=0.0)
    assert nouvelle_norm == pytest.approx(ancienne_norm), (
        "z>0 : zscore_abs doit être identique à z/div (zéro cutover)"
    )
    # Et la contribution reste haussière (cacao restait LONG, météo y contribuait +).
    assert _contribution(z_courant) > 0


def test_centre_rend_normal_baissier():
    """zscore_centre>0 → normal (z=0) devient légèrement baissier (déviation jugée
    normale). Optionnel ; défaut 0 = neutre + zéro cutover."""
    norm0 = cc.zscore_abs_normalisee(0.0, zscore_div=2.0, cap=1.0, centre=0.5)
    assert norm0 < 0


def test_cap_borne_les_extremes():
    """|z| énorme → norm capée à ±cap (pas d'explosion)."""
    norm = cc.zscore_abs_normalisee(50.0, zscore_div=2.0, cap=1.0, centre=0.0)
    assert norm == pytest.approx(1.0)


def test_zscore_div_zero_degrade_proprement():
    """zscore_div=0 → 0.0 défensif (pas de ZeroDivisionError)."""
    assert cc.zscore_abs_normalisee(1.0, zscore_div=0.0, cap=1.0) == 0.0


# --- La fiche cacao déclare bien le fix -------------------------------------

def test_fiche_cacao_meteo_est_zscore_abs():
    """La fiche cacao.yml critère id 1 doit être en zscore_abs signe +1 poids 11."""
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "cacao.yml").read_text())
    meteo = next(c for c in fiche["criteres"] if c.get("cle_courante") == "meteo_ci_ghana_precip_30j")
    assert meteo["normalisation"] == "zscore_abs"
    assert meteo["signe"] == 1
    assert meteo["poids"] == 11


# --- Routage : zscore_abs atteint bien _handle_meteo ------------------------

def test_routage_zscore_abs_vers_meteo():
    """build_critere_value route un critère météo zscore_abs vers _handle_meteo."""
    with patch.object(cc, "fetch_open_meteo_anomaly", return_value=-1.0):
        import datetime as _dt
        res = cc.build_critere_value(
            "cacao", CRIT_CACAO_METEO, {}, {}, [],
            _dt.datetime(2026, 6, 18, tzinfo=_dt.timezone.utc),
        )
    assert res is not None
    assert res["valeur_normalisee"] > 0  # sécheresse → haussier
