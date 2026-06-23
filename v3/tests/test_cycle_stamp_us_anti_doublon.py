"""Garde STRUCTURELLE : le stamp d'ouverture US doit pouvoir capter sa référence.

Incident 23/06/2026 : le suivi 18h affichait le prix US (SPY/QQQ proxies) mais
« Ouverture — » → « ⏳ données manquantes ». Cause racine : le cash US ouvre à
15h30 (+5 min délai = 15h35 stampable), or le créneau stamp tire à :12/:27/:42 ;
seul le tick :42 (15h42 Paris) tombe APRÈS l'ouverture. L'anti-doublon (2h)
suspendait ce tick parce qu'un « stamp ouverture » d'AVANT l'ouverture (15h12)
existait déjà → la référence d'ouverture US n'était JAMAIS captée.

Ces tests verrouillent les deux moitiés du correctif :
  1. les créneaux stamp (Paris 8h / 9h / 15h) sont EXEMPTÉS de l'anti-doublon ;
  2. « stamp ouverture » n'est plus compté par l'anti-doublon (qui ne protège
     que les runs lourds : snapshot / suivi / bilan).
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / ".github" / "workflows" / "cycle.yml"


def _guard_run() -> str:
    """Texte de la commande `run` du step garde (jour de bourse + anti-doublon)."""
    data = yaml.safe_load(CYCLE.read_text(encoding="utf-8"))
    steps = next(iter(data["jobs"].values()))["steps"]
    for s in steps:
        run = s.get("run", "")
        if "anti-doublon" in run or "tentative schedule redondante" in run:
            return run
    raise AssertionError("step garde anti-doublon introuvable dans cycle.yml")


def test_creneaux_stamp_exemptes_anti_doublon():
    """Paris 8h/9h/15h : run autorisé sur chaque tick (stamp idempotent)."""
    run = _guard_run()
    # La garde calcule l'heure de Paris et court-circuite l'anti-doublon pour
    # les 3 créneaux stamp (continus 8h, EU 9h, US 15h).
    assert 'ph_guard=$(TZ=\'Europe/Paris\' date +%H)' in run, (
        "la garde doit lire l'heure de Paris pour repérer les créneaux stamp"
    )
    for h in (8, 9, 15):
        assert f'"$ph_guard" -eq {h}' in run, (
            f"créneau stamp {h}h non exempté de l'anti-doublon — le stamp US "
            f"(15h) ne pourrait pas re-tirer à :42 après l'ouverture cash"
        )


def test_stamp_ouverture_hors_grep_anti_doublon():
    """L'anti-doublon ne compte QUE les runs lourds, pas les stamps prix-only."""
    run = _guard_run()
    # La ligne `last=$(git log ... --grep=...)` ne doit plus matcher les stamps.
    grep_line = next(
        (ln for ln in run.splitlines() if "--grep=" in ln and "format=%ct" in ln),
        "",
    )
    assert grep_line, "ligne anti-doublon `git log --grep` introuvable"
    assert "stamp ouverture" not in grep_line, (
        "« stamp ouverture » ne doit plus être compté par l'anti-doublon : un "
        "stamp prix-only ne doit ni se suspendre lui-même ni suspendre un "
        "suivi/bilan ultérieur"
    )
    for token in ("decision snapshot", "decision suivi", "decision bilan"):
        assert token in grep_line, (
            f"l'anti-doublon doit toujours protéger les runs lourds ({token})"
        )
