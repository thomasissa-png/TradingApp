"""Régression T1 (audit news 25/06) — les news CAC 40 se routent sur la clé
`cac40` (celle de la fiche `cac40.yml`, via `f.stem`), pas sur l'ancienne clé
`cac_40` qui faisait perdre tout le contexte news de l'actif (« aucune
actualité » alors que 73-84 items/cycle entraient).

Le bug : `IA_ASSET_TO_ACTIF["CAC40"]` et `TICKER_TO_ACTIF["cac_40"]` pointaient
sur `cac_40`, mais la fiche/scoring/section « News par actif » utilisent `cac40`
(= nom de fichier `cac40.yml`). Les events routés IA→`cac_40` ne retombaient
jamais sur la fiche `cac40`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402


def test_cle_unique_cac40_partout():
    """La clé interne du CAC est `cac40` (= f.stem de la fiche), jamais `cac_40`."""
    assert "cac40" in tc.TICKER_TO_ACTIF
    assert "cac_40" not in tc.TICKER_TO_ACTIF
    assert tc.IA_ASSET_TO_ACTIF["CAC40"] == "cac40"
    assert "cac_40" not in set(tc.IA_ASSET_TO_ACTIF.values())
    # Le scope critère est référencé sur la même clé.
    assert ("cac40", "tension_politique_fr") in tc.CRITERION_SCOPE
    assert ("cac_40", "tension_politique_fr") not in tc.CRITERION_SCOPE


def test_fiche_cac40_existe_sous_cette_cle():
    """La fiche YAML existe et son nom de fichier == clé interne (anti-piège T1)."""
    fiche = ROOT / "config" / "fiches" / "cac40.yml"
    assert fiche.exists()
    assert fiche.stem == "cac40"
    assert not (ROOT / "config" / "fiches" / "cac_40.yml").exists()


def test_event_ia_cac40_route_sur_cac40():
    """Un event IA ciblant l'asset 'CAC40' retombe sur l'actif `cac40`."""
    ev = {"_impacts": [{"asset": "CAC40", "direction": "SHORT"}]}
    assert tc._event_ia_targets_actif(ev, "cac40") is True
    # Ne route PAS sur l'ancienne clé fantôme.
    assert tc._event_ia_targets_actif(ev, "cac_40") is False


def test_event_ticker_cac40_route_sur_cac40():
    """Un event dont `cours` mentionne le CAC retombe sur l'actif `cac40`."""
    ev_ticker = {"cours": "CAC 40 (^FCHI)"}
    assert tc._event_targets_actif(ev_ticker, "cac40") is True
    ev_alias = {"cours": "Indice CAC40 Paris"}
    assert tc._event_targets_actif(ev_alias, "cac40") is True
