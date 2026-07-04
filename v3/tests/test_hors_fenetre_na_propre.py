"""Fix 03/07 — hors fenêtre d'activation → n/a PROPRE (critère ABSENT), jamais un
placeholder pseudo-présent {valeur_normalisee: 0.0, note: "hors fenêtre"}.

Régression prouvée sur logs réels (Blé pari n°3, 03/07) : hors fenêtre, le
placeholder faisait voir le critère « présent » (is_na=False) → son poids comptait
dans la couverture → le plafond « fragile (capteurs éteints) » du scoring ne se
déclenchait JAMAIS. Le fix rend le critère absent (poids exclu) pour réarmer le
garde-fou. Aucun appel réseau : le retour None précède tout fetch.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import criteres_calculator as cc  # noqa: E402


def _crit(cle: str, norm: str = "zscore") -> dict:
    return {"cle_courante": cle, "normalisation": norm, "source": "usda",
            "zscore_window": 12, "zscore_div": 2, "cap": 1.0}


def test_wasde_hors_fenetre_na_propre_pas_de_placeholder():
    """usda_wasde_stocks_to_use (zscore, poids 11) hors fenêtre (jour 20, fenêtre
    8-17) → None (n/a propre), pas de {valeur_normalisee: 0.0}."""
    cc.SKIP_COUNTER.clear()
    # jour 20 → hors fenêtre 8-17 ; pas de clé USDA → aucun fetch réel de toute façon.
    now = datetime(2026, 6, 20, 14, 0, tzinfo=timezone.utc)
    out = cc.build_critere_value("ble", _crit("usda_wasde_stocks_to_use"), {}, {}, [], now)
    assert out is None  # critère ABSENT → poids exclu de la couverture
    assert cc.SKIP_COUNTER.get("hors_fenetre:usda_wasde_stocks_to_use") == 1


def test_eia_surprise_hors_fenetre_na_propre():
    """eia_crude_surprise (zscore) hors fenêtre (lundi) → None, motif tracé."""
    cc.SKIP_COUNTER.clear()
    now = datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc)  # lundi → hors fenêtre EIA
    crit = {"cle_courante": "eia_crude_surprise", "normalisation": "zscore",
            "source": "eia api", "zscore_window": 52, "zscore_div": 2, "cap": 1.0}
    out = cc.build_critere_value("petrole", crit, {}, {}, [], now)
    assert out is None
    assert cc.SKIP_COUNTER.get("hors_fenetre:eia_crude_surprise") == 1


def test_wasde_dans_fenetre_sans_cle_na_propre():
    """Dans la fenêtre (jour 10) mais SANS USDA_API_KEY → n/a propre via le handler
    NASS (motif nass_no_key), pas de placeholder hors-fenêtre."""
    cc.SKIP_COUNTER.clear()
    now = datetime(2026, 6, 10, 14, 0, tzinfo=timezone.utc)  # jour 10 → dans fenêtre
    out = cc.build_critere_value("ble", _crit("usda_wasde_stocks_to_use"), {}, {}, [], now)
    assert out is None
    assert cc.SKIP_COUNTER.get("nass_no_key") == 1
    assert "hors_fenetre:usda_wasde_stocks_to_use" not in cc.SKIP_COUNTER


def test_critere_sans_fenetre_intact():
    """Un critère SANS fenêtre définie (is_in_activation_window → None) n'est pas
    affecté par le fix : il poursuit le dispatch normal (ici zscore Twelve absent
    → None mais SANS motif hors_fenetre)."""
    cc.SKIP_COUNTER.clear()
    now = datetime(2026, 6, 20, 14, 0, tzinfo=timezone.utc)
    crit = {"cle_courante": "momentum_prix_20j_ble", "normalisation": "zscore",
            "source": "twelve", "zscore_window": 20, "zscore_div": 2, "cap": 1.0}
    cc.build_critere_value("ble", crit, {}, {}, [], now)
    assert "hors_fenetre:momentum_prix_20j_ble" not in cc.SKIP_COUNTER
