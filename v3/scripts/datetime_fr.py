#!/usr/bin/env python3
"""datetime_fr.py — Horodatage FR lisible pour les en-têtes de rapports.

[Point #5] Les rapports (bulletin, briefing, suivi, bilan jour/semaine) datent
leur génération avec une ligne « Généré : … ». Historiquement c'était
`now.isoformat()` → « 2026-06-19T08:08:09.816553+02:00 » (ISO machine, illisible
pour un humain). On centralise ici le format FR lisible « 19 juin 2026, 08h08 ».

UNE seule fonction, réutilisée par tous les émetteurs (scoring_analyste,
journaliste, bilan_jour, run_weekly…). Le fuseau reste implicite (Paris) : les
`now` passés sont déjà en heure Paris dans le pipeline. Zéro dépendance externe.
"""
from __future__ import annotations

from datetime import datetime

_MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def horodatage_fr(dt: datetime) -> str:
    """Formate un datetime en libellé FR lisible : « 19 juin 2026, 08h08 ».

    Le fuseau est implicite (Paris) — on n'affiche pas l'offset machine. La
    minute est zéro-paddée (« 08h08 », « 14h05 »). Déterministe, jamais de crash.
    """
    mois = _MOIS_FR[dt.month - 1]
    return f"{dt.day} {mois} {dt.year}, {dt.hour:02d}h{dt.minute:02d}"
