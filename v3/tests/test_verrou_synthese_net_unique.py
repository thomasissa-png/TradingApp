"""Test-verrou — anti double-comptage de la synthèse nette news (L013).

CONTEXTE DU BUG (16/06) : la synthèse directionnelle DeepSeek est UNE direction
nette PAR ACTIF. Elle était appliquée à TOUT critère IA-routable
(`_criterion_has_ia_route`). Pour un actif à PLUSIEURS créneaux news IA, le même
signal net était donc compté 2-3 fois (poids cumulés) → conviction gonflée.

CORRECTIF : un seul critère par actif PORTE la synthèse nette
(`_is_synthese_carrier` / SYNTHESE_NET_CARRIER). Les autres créneaux news IA
retombent sur leur détection par mots-clés DÉDIÉS uniquement (0 si pas de news
propre — zéro invention).

Ce que ce fichier prouve :
- cacao / cuivre / petrole (2 créneaux news IA) : APRÈS fix, UN SEUL créneau
  porte le net (`source_track="ia_synthese"`, val signée) ; l'AUTRE est
  keyword-only et vaut 0 en l'absence de news dédiée.
- Non-régression : les actifs MONO-créneau news IA (or, argent, cafe, ble,
  cac_40, nasdaq, vix) portent toujours le net sur leur unique créneau.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402


NOW = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)

# Synthèse nette DeepSeek pour l'actif (1 direction / actif).
SYNTH_SHORT = {"direction": "SHORT", "conviction": "high",
               "rationale": "récit baissier net"}
SYNTH_LONG = {"direction": "LONG", "conviction": "high",
              "rationale": "récit haussier net"}


def _resolve(actif_key: str, cle: str, synth: dict):
    """Résout un créneau news IA SANS events dédiés (events=[]).

    En l'absence d'event keyword/IA, seul le mécanisme synthèse peut produire
    une valeur ≠ 0 → isole proprement « qui porte le net ».
    """
    spec = tc.load_triggers_config()[actif_key][cle]
    return tc._resolve_triplet_with_meta(
        [],  # aucun event → keyword-only = 0
        actif_key,
        cle,
        spec.get("long_keywords", []) or [],
        spec.get("short_keywords", []) or [],
        int(spec.get("horizon_lookback_jours", 7)),
        NOW,
        synthese=synth,
    )


# ---------------------------------------------------------------------------
# 1. cacao — porteur = maladies_cabosses_cacao (slot renommé « Synthèse net »)
# ---------------------------------------------------------------------------

def test_cacao_seul_le_porteur_porte_le_net():
    # Porteur : reçoit le net (-1, ia_synthese)
    val_carrier, meta_carrier = _resolve("cacao", "maladies_cabosses_cacao", SYNTH_SHORT)
    assert val_carrier == -1
    assert meta_carrier["source_track"] == "ia_synthese"

    # Non-porteur (eudr) : PAS de net → keyword-only = 0 (pas de news EUDR dédiée)
    val_eudr, meta_eudr = _resolve("cacao", "eudr_impact", SYNTH_SHORT)
    assert val_eudr == 0
    assert meta_eudr.get("source_track") != "ia_synthese"


# ---------------------------------------------------------------------------
# 2. cuivre — porteur = mining_strikes_chili_perou (poids 5 > 4)
# ---------------------------------------------------------------------------

def test_cuivre_seul_le_porteur_porte_le_net():
    val_carrier, meta_carrier = _resolve("cuivre", "mining_strikes_chili_perou", SYNTH_LONG)
    assert val_carrier == 1
    assert meta_carrier["source_track"] == "ia_synthese"

    val_infra, meta_infra = _resolve("cuivre", "news_construction_infrastructure", SYNTH_LONG)
    assert val_infra == 0
    assert meta_infra.get("source_track") != "ia_synthese"


# ---------------------------------------------------------------------------
# 3. petrole — porteur = geopol_iran (poids 7 > 6)
# ---------------------------------------------------------------------------

def test_petrole_seul_le_porteur_porte_le_net():
    val_carrier, meta_carrier = _resolve("petrole", "geopol_iran", SYNTH_SHORT)
    assert val_carrier == -1
    assert meta_carrier["source_track"] == "ia_synthese"

    val_opec, meta_opec = _resolve("petrole", "opec_politique", SYNTH_SHORT)
    assert val_opec == 0
    assert meta_opec.get("source_track") != "ia_synthese"


# ---------------------------------------------------------------------------
# 4. Non-régression — actifs MONO-créneau news IA : net porté normalement
# ---------------------------------------------------------------------------

MONO_CRENEAU = [
    ("or", "tension_geopolitique"),
    ("argent", "demande_photovoltaique_et_mining_strikes"),
    ("cafe", "maladies_cabosses"),
    ("ble", "geopol_mer_noire"),
    ("cac_40", "tension_politique_fr"),
    ("nasdaq", "sentiment_ia_megacaps"),
    ("vix", "tension_geopolitique_active"),
]


@pytest.mark.parametrize("actif_key,cle", MONO_CRENEAU)
def test_mono_creneau_porte_toujours_le_net(actif_key, cle):
    # Actif non listé dans SYNTHESE_NET_CARRIER → son unique créneau reste porteur.
    assert actif_key not in tc.SYNTHESE_NET_CARRIER
    val, meta = _resolve(actif_key, cle, SYNTH_LONG)
    assert val == 1
    assert meta["source_track"] == "ia_synthese"


# ---------------------------------------------------------------------------
# 5. Inventaire — chaque actif multi-créneau a EXACTEMENT 1 porteur
# ---------------------------------------------------------------------------

def test_un_seul_porteur_par_actif_multi_creneau():
    cfg = tc.load_triggers_config()
    for actif_key in tc.SYNTHESE_NET_CARRIER:
        creneaux_ia = [
            cle for cle in cfg.get(actif_key, {})
            if tc._criterion_has_ia_route(actif_key, cle)
        ]
        porteurs = [cle for cle in creneaux_ia if tc._is_synthese_carrier(actif_key, cle)]
        assert len(creneaux_ia) >= 2, f"{actif_key} attendu multi-créneau"
        assert len(porteurs) == 1, f"{actif_key} : {len(porteurs)} porteur(s), attendu 1"
        assert porteurs[0] == tc.SYNTHESE_NET_CARRIER[actif_key]


# ---------------------------------------------------------------------------
# 6. _is_synthese_carrier — contrat de la fonction
# ---------------------------------------------------------------------------

def test_is_synthese_carrier_contrat():
    # Actif listé : seul le carrier renvoie True
    assert tc._is_synthese_carrier("cacao", "maladies_cabosses_cacao") is True
    assert tc._is_synthese_carrier("cacao", "eudr_impact") is False
    # Actif non listé : tout critère reste porteur (legacy mono-créneau)
    assert tc._is_synthese_carrier("or", "tension_geopolitique") is True
    assert tc._is_synthese_carrier("nimporte", "nimporte") is True
