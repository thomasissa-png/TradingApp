"""VOLET C — cutover : ref-changed.json contient les actifs continus au 15/06.

Vérifie que les 8 actifs continus touchés par VOLET A (or, argent, pétrole,
cuivre, cacao, café, blé, EUR/USD) ont leur `ref_changed` avancé au 2026-06-15
avec le motif « prix le plus frais », et que les NON continus (S&P/Nasdaq/CAC/
VIX) gardent leur référence 2026-06-11 (inchangée).
"""

from __future__ import annotations

import json
from pathlib import Path

REF_CHANGED = Path(__file__).resolve().parents[1] / "data" / "ref-changed.json"

_CONTINUS = ["GC=F", "SI=F", "BZ=F", "HG=F", "CC=F", "KC=F", "ZW=F", "EUR=X"]
_NON_CONTINUS = ["^GSPC", "^IXIC", "^FCHI", "^VIX"]


def _load():
    return json.loads(REF_CHANGED.read_text(encoding="utf-8"))["ref_changed"]


def test_continus_resets_au_15_06():
    rc = _load()
    for ticker in _CONTINUS:
        assert ticker in rc, f"{ticker} absent du registre"
        assert rc[ticker]["ref_changed"] == "2026-06-15", (
            f"{ticker} devrait être reset au 15/06"
        )


def test_continus_motif_prix_frais():
    rc = _load()
    for ticker in _CONTINUS:
        motif = rc[ticker]["motif"].lower()
        assert "prix le plus frais" in motif or "angle mort" in motif, (
            f"{ticker} : motif 15/06 manquant"
        )


def test_non_continus_inchanges():
    rc = _load()
    for ticker in _NON_CONTINUS:
        assert rc[ticker]["ref_changed"] == "2026-06-11", (
            f"{ticker} (non continu) ne doit PAS être reset au 15/06"
        )


def test_json_valide_et_append_only():
    """Le registre reste un JSON valide et chaque entrée garde fiche_key/actif."""
    rc = _load()
    for ticker in _CONTINUS:
        assert rc[ticker].get("fiche_key")
        assert rc[ticker].get("actif")
