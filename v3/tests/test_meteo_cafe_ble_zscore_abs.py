"""Tests — FIX SIGNE/LABEL MÉTÉO CAFÉ & BLÉ : normalisation symétrique « écart à la normale ».

Même défaut que le cacao (corrigé par `zscore_abs`), appliqué à 2 critères :

(A) CAFÉ — `meteo_bresil_minas_gerais` (poids 11). Intention SYMÉTRIQUE déclarée
    (effet_long « Gel imminent OU sécheresse persistante ») mais ancienne impl.
    (`composite` → en réalité seule l'anomalie pluie via fetch_open_meteo_anomaly,
    puis `z/div` + signe:1) rendait la SÉCHERESSE (z<0) BAISSIÈRE — à contre-sens.
    Fix : `normalisation: zscore_abs` (|z|). La dimension GEL (Tmin<4°C) reste NON
    câblée (chantier data séparé — elle ne l'était déjà pas dans le composite).

(B) BLÉ — `noaa_drought_midwest_plains` (poids 9). La donnée injectée est une
    anomalie de PRÉCIPITATIONS signée (z>0 = plus de pluie), pas un indice de
    sécheresse → le label « drought, z>+1 = LONG » était faux. Lecture agronomique
    retenue = SYMÉTRIQUE (sécheresse z<0 OU excès de pluie z>0 = récolte menacée =
    haussier), implémentée en `zscore_abs`. cle_courante INCHANGÉE (L023).

Vérifie pour chaque actif :
- sécheresse (z<0) → contribution HAUSSIÈRE (bug réparé) ;
- excès de pluie (z>0) → contribution HAUSSIÈRE ;
- normal (z≈0) → neutre ;
- symétrie |z| ;
- ZÉRO cutover sur la valeur du jour (café z=-0.332, blé z=+0.299) documenté ;
- la fiche déclare bien zscore_abs / signe +1 / poids inchangé.
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


# Critères tels que dans les fiches (après fix) — utilisés pour piloter _handle_meteo.
CRIT_CAFE = {
    "id": 1,
    "cle_courante": "meteo_bresil_minas_gerais",
    "normalisation": "zscore_abs",
    "zscore_div": 2,
    "zscore_centre": 0.0,
    "cap": 1.0,
    "signe": 1,
    "poids": 11,
    "source": "NOAA / météo (précipitations ; T min non câblée)",
}

CRIT_BLE = {
    "id": 2,
    "cle_courante": "noaa_drought_midwest_plains",
    "normalisation": "zscore_abs",
    "zscore_div": 2,
    "zscore_centre": 0.0,
    "cap": 1.0,
    "signe": 1,
    "poids": 9,
    "source": "Open-Meteo (anomalie précipitations vs climato 5 ans)",
}


def _contribution(crit: dict, z: float) -> float:
    """norm pré-calculée par _handle_meteo → consommée par scoring → contribution signée."""
    with patch.object(cc, "fetch_open_meteo_anomaly", return_value=z):
        res = cc._handle_meteo(crit["cle_courante"], crit, "2026-06-18T00:00:00")
    assert res is not None
    norm, _note = sa.normalise(crit, res)
    assert norm is not None
    return norm * crit["signe"]


# --- (A) CAFÉ ---------------------------------------------------------------

def test_cafe_secheresse_devient_haussier():
    """Café : sécheresse (z<0) → contribution POSITIVE = HAUSSIER (bug réparé)."""
    assert _contribution(CRIT_CAFE, -1.5) > 0


def test_cafe_exces_pluie_reste_haussier():
    """Café : excès de pluie (z>0) → contribution POSITIVE = HAUSSIER (intention)."""
    assert _contribution(CRIT_CAFE, +1.5) > 0


def test_cafe_normal_neutre():
    """Café : pluies normales (z≈0) → contribution ≈ 0 (centre=0)."""
    assert abs(_contribution(CRIT_CAFE, 0.0)) < 1e-9


def test_cafe_symetrie():
    """Café : |z| égal des deux côtés → même intensité haussière."""
    assert _contribution(CRIT_CAFE, -2.0) == pytest.approx(_contribution(CRIT_CAFE, +2.0))


def test_cafe_valeur_du_jour_secheresse_haussiere():
    """Café : valeur réelle du 18/06 (z=-0.332, sécheresse légère) → désormais HAUSSIÈRE
    (avant le fix : -0.166 baissière). Le café est déjà LONG → le fix RENFORCE la
    conviction LONG, NE flippe AUCUN horizon (cutover de direction = NON)."""
    z_jour = -0.3319996216764765  # criteres-courants.md 18/06
    contrib = _contribution(CRIT_CAFE, z_jour)
    assert contrib == pytest.approx(0.16599981083823825)  # +|z|/div, haussier
    # Ancienne valeur (bug) : z/div = -0.166 (baissière). On vérifie l'inversion.
    ancienne = max(-1.0, min(1.0, z_jour / 2.0))
    assert ancienne < 0 < contrib


def test_fiche_cafe_meteo_est_zscore_abs():
    """La fiche cafe.yml critère id 1 doit être zscore_abs, signe +1, poids 11 inchangé."""
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "cafe.yml").read_text())
    meteo = next(c for c in fiche["criteres"] if c.get("cle_courante") == "meteo_bresil_minas_gerais")
    assert meteo["normalisation"] == "zscore_abs"
    assert meteo["signe"] == 1
    assert meteo["poids"] == 11  # L023 : poids inchangé


# --- (B) BLÉ ----------------------------------------------------------------

def test_ble_secheresse_devient_haussier():
    """Blé : sécheresse (z<0, précip < normale) → contribution POSITIVE = HAUSSIER."""
    assert _contribution(CRIT_BLE, -1.5) > 0


def test_ble_exces_pluie_haussier():
    """Blé : excès de pluie (z>0, inondation/qualité) → HAUSSIER (lecture symétrique)."""
    assert _contribution(CRIT_BLE, +1.5) > 0


def test_ble_normal_neutre():
    """Blé : précipitations normales (z≈0) → neutre."""
    assert abs(_contribution(CRIT_BLE, 0.0)) < 1e-9


def test_ble_symetrie():
    """Blé : |z| égal des deux côtés → même intensité (symétrique)."""
    assert _contribution(CRIT_BLE, -2.0) == pytest.approx(_contribution(CRIT_BLE, +2.0))


def test_ble_zero_cutover_sur_valeur_du_jour():
    """Blé : à z courant>0 (18/06 : z=+0.299, pluie au-dessus de la normale), la valeur
    normalisée zscore_abs est IDENTIQUE à l'ancienne z/div → direction blé du jour
    INCHANGÉE (le fix ne touche que le côté sécheresse z<0)."""
    z_jour = 0.29940886966561936  # criteres-courants.md 18/06
    div, cap = 2.0, 1.0
    ancienne = max(-cap, min(cap, z_jour / div))           # ancienne formule linéaire
    nouvelle = cc.zscore_abs_normalisee(z_jour, zscore_div=div, cap=cap, centre=0.0)
    assert nouvelle == pytest.approx(ancienne), "z>0 : zscore_abs ≡ z/div (zéro cutover)"
    assert _contribution(CRIT_BLE, z_jour) > 0


def test_fiche_ble_meteo_est_zscore_abs_cle_stable():
    """La fiche ble.yml critère id 2 : zscore_abs, signe +1, poids 9, cle_courante STABLE."""
    fiche = yaml.safe_load((ROOT / "config" / "fiches" / "ble.yml").read_text())
    meteo = next(c for c in fiche["criteres"] if c.get("cle_courante") == "noaa_drought_midwest_plains")
    assert meteo["normalisation"] == "zscore_abs"
    assert meteo["signe"] == 1
    assert meteo["poids"] == 9
    # L023 : la clé d'agrégation NE doit PAS être renommée (label honnête, clé stable).
    assert meteo["cle_courante"] == "noaa_drought_midwest_plains"


# --- Routage : zscore_abs atteint bien _handle_meteo pour café ET blé -------

@pytest.mark.parametrize("crit", [CRIT_CAFE, CRIT_BLE])
def test_routage_zscore_abs_vers_meteo(crit, now_fixed=None):
    """build_critere_value route un critère météo zscore_abs vers _handle_meteo."""
    import datetime as _dt
    with patch.object(cc, "fetch_open_meteo_anomaly", return_value=-1.0):
        fiche = "cafe" if crit is CRIT_CAFE else "ble"
        res = cc.build_critere_value(
            fiche, crit, {}, {}, [],
            _dt.datetime(2026, 6, 18, tzinfo=_dt.timezone.utc),
        )
    assert res is not None
    assert res["valeur_normalisee"] > 0  # sécheresse → haussier
