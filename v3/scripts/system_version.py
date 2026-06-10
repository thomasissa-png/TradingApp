"""system_version — cutover v2 (reset PARTIEL) : version systeme + registre ref_changed.

Responsabilite unique : exposer la version du systeme (`SYSTEM_VERSION`) et lire le
registre de reset `v3/data/ref-changed.json` (mappant des cellules — clees par
`ticker_principal`, identifiant STABLE — vers une date `ref_changed`).

Le cutover v2 est une operation de MESURE / OBSERVABILITE uniquement :
- `SYSTEM_VERSION` est estampille sur les NOUVELLES entrees du decision-log et sur
  les nouvelles mesures du Journaliste. Les entrees passees sans le champ sont
  implicitement v1 (jamais reecrites — append-only).
- Pour les cellules presentes dans le registre, le comptage N et le win rate
  (conclusif ET tradable) ne comptent QUE les observations datees >= `ref_changed`.
  Les cellules ABSENTES du registre comptent tout (aucun reset).

Cle = `ticker_principal` (pas le nom d'affichage) pour rester robuste a un
renommage de l'actif (lecon L023 : agreger / clé par identifiant stable).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, Optional

# Version courante du systeme. Estampillee sur les nouvelles entrees de mesure /
# decision-log. NE JAMAIS reecrire les entrees passees (= implicitement v1).
SYSTEM_VERSION = "v2"

# Chemin par defaut du registre de reset (data, append-only).
ROOT = Path(__file__).resolve().parent.parent
REF_CHANGED_PATH = ROOT / "data" / "ref-changed.json"


def load_ref_changed(path: Optional[Path] = None) -> Dict[str, date]:
    """Charge le registre de reset : { ticker_principal -> date ref_changed }.

    Retourne un dict vide si le fichier est absent ou illisible (degradation
    propre : aucun reset applique => comportement v1 inchange). Zero invention.
    """
    p = path if path is not None else REF_CHANGED_PATH
    if not p.exists():
        return {}
    try:
        with p.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, ValueError):
        return {}
    entries = raw.get("ref_changed") if isinstance(raw, dict) else None
    if not isinstance(entries, dict):
        return {}
    out: Dict[str, date] = {}
    for ticker, meta in entries.items():
        if not isinstance(meta, dict):
            continue
        rc = meta.get("ref_changed")
        if not isinstance(rc, str):
            continue
        try:
            out[ticker] = date.fromisoformat(rc)
        except ValueError:
            continue
    return out


def ref_changed_for_ticker(
    ticker_principal: Optional[str],
    registry: Optional[Dict[str, date]] = None,
) -> Optional[date]:
    """Date de reset pour un `ticker_principal`, ou None si la cellule n'est pas reset.

    `registry` permet d'injecter un registre deja charge (evite de relire le
    fichier a chaque cellule). Si None, charge le registre par defaut.
    """
    if not ticker_principal:
        return None
    reg = registry if registry is not None else load_ref_changed()
    return reg.get(ticker_principal)
