"""Cutover des actifs continus dans ref-changed.json.

Historique des resets continus :
  - 15/06 : prix le plus frais (angle mort overnight/week-end) — 3e reset
  - 16/06 : source Twelve natif XAU/XAG/XBR (or/argent/Brent)
  - 17/06 : fix L027 — référence de mesure 24h = ÉMISSION 7h (point d'exécution
            réel) au lieu de l'OUVERTURE 8h Paris. 4e reset des continus.

Ce module vérifie l'ÉTAT COURANT du registre après le fix L027 : les 8 continus
(or, argent, pétrole, cuivre, cacao, café, blé, EUR/USD) sont tous reset au
2026-06-17, et les NON continus (S&P/Nasdaq/CAC/VIX) gardent leur 2026-06-11.
"""

from __future__ import annotations

import json
from pathlib import Path

REF_CHANGED = Path(__file__).resolve().parents[1] / "data" / "ref-changed.json"

_CONTINUS = ["GC=F", "SI=F", "BZ=F", "HG=F", "CC=F", "KC=F", "ZW=F", "EUR=X"]
_NON_CONTINUS = ["^GSPC", "^IXIC", "^FCHI", "^VIX"]
# Fix L027 (16/06, GO mesure Thomas) : les 8 continus sont reset au 1er bulletin
# sous la nouvelle sémantique = 2026-06-17.
_CUTOVER_L027 = "2026-06-17"


def _load():
    return json.loads(REF_CHANGED.read_text(encoding="utf-8"))["ref_changed"]


def test_continus_resets_au_17_06_fix_l027():
    # Les dates du registre AVANCENT avec les cutovers ultérieurs (re-découpage
    # 30/06, ticket C 01/07) ; on vérifie le PLANCHER L027, pas l'égalité.
    rc = _load()
    for ticker in _CONTINUS:
        assert ticker in rc, f"{ticker} absent du registre"
        assert rc[ticker]["ref_changed"] >= _CUTOVER_L027, (
            f"{ticker} devrait être reset au moins au {_CUTOVER_L027} (fix L027)"
        )


def test_continus_motif_l027():
    rc = _load()
    for ticker in _CONTINUS:
        motif = rc[ticker]["motif"].lower()
        assert "l027" in motif, f"{ticker} : motif fix L027 manquant"
        assert "emission 7h" in motif, (
            f"{ticker} : la nouvelle référence (émission 7h) doit être documentée"
        )


def test_non_continus_inchanges():
    # Le fix L027 (17/06) n'a pas touché les non-continus : leur plancher reste
    # le cutover momentum v3 du 11/06 (dates avancées ensuite par des cutovers
    # DISTINCTS et légitimes, ex. re-découpage horizons du 30/06).
    rc = _load()
    for ticker in _NON_CONTINUS:
        assert rc[ticker]["ref_changed"] >= "2026-06-11", (
            f"{ticker} (non continu) doit porter au moins le cutover du 11/06"
        )


def test_json_valide_et_append_only():
    """Le registre reste un JSON valide et chaque entrée garde fiche_key/actif."""
    rc = _load()
    for ticker in _CONTINUS:
        assert rc[ticker].get("fiche_key")
        assert rc[ticker].get("actif")
