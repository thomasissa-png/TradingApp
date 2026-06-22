"""Garde STRUCTURELLE : la régénération de la page (Build HTML) doit tourner
APRÈS tous les runners qui produisent des données, sinon un rapport est écrit
sur disque mais absent de la page (bug récurrent — incidents 22/06 suivi 18h,
et antérieurs). Ce test échoue en CI si l'ordre des steps se re-casse.

Principe : `build_html.py` lit les .md du jour pour bâtir index.html. Tout step
qui ÉCRIT un .md (run_bulletin / run_stamp / run_suivi / run_bilan / run_journaliste)
doit donc s'exécuter AVANT Build HTML, et Build HTML AVANT le commit (sinon la
page n'est pas embarquée). On vérifie les deux workflows qui régénèrent la page.
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parents[2]  # racine repo (v3/tests → v3 → repo)
WORKFLOWS = ROOT / ".github" / "workflows"


def _steps(workflow: str) -> list[dict]:
    data = yaml.safe_load((WORKFLOWS / workflow).read_text(encoding="utf-8"))
    jobs = data["jobs"]
    # Un seul job par workflow ici → on prend le premier.
    return next(iter(jobs.values()))["steps"]


def _index_of(steps: list[dict], needle: str) -> int:
    """Index du 1ᵉʳ step dont le nom OU la commande `run` contient `needle`."""
    for i, s in enumerate(steps):
        blob = f"{s.get('name', '')}\n{s.get('run', '')}"
        if needle in blob:
            return i
    return -1


def test_cycle_build_html_apres_tous_les_runners():
    """cycle.yml : Build HTML APRÈS chaque runner de slot, et AVANT le commit."""
    steps = _steps("cycle.yml")
    build = _index_of(steps, "build_html.py")
    commit = _index_of(steps, "Commit and push")
    assert build != -1, "step Build HTML introuvable dans cycle.yml"
    assert commit != -1, "step Commit introuvable dans cycle.yml"

    # Tout runner qui écrit un .md du jour doit précéder Build HTML.
    runners = [
        "run_bulletin.py",
        "run_journaliste.py",
        "run_stamp.py",
        "run_suivi.py",
        "run_bilan.py",
    ]
    for r in runners:
        idx = _index_of(steps, r)
        assert idx != -1, f"runner {r} introuvable dans cycle.yml"
        assert idx < build, (
            f"{r} (#{idx}) doit s'exécuter AVANT Build HTML (#{build}) — sinon la "
            f"page est bâtie sur l'état précédent et le rapport du créneau est invisible."
        )
    assert build < commit, (
        f"Build HTML (#{build}) doit précéder le Commit (#{commit}) — sinon la "
        f"page régénérée n'est pas embarquée dans le snapshot."
    )


def test_weekly_build_html_apres_bilan_semaine():
    """weekly-summary.yml : régénération de la page APRÈS le bilan semaine, AVANT commit."""
    steps = _steps("weekly-summary.yml")
    build = _index_of(steps, "build_html.py")
    bilan = _index_of(steps, "run_weekly.py")
    commit = _index_of(steps, "Commit and push")
    assert build != -1, "step Build HTML introuvable dans weekly-summary.yml"
    assert bilan != -1, "step bilan semaine (run_weekly.py) introuvable"
    assert commit != -1, "step Commit introuvable dans weekly-summary.yml"
    assert bilan < build < commit, (
        f"Ordre attendu : bilan semaine (#{bilan}) < Build HTML (#{build}) < "
        f"Commit (#{commit})."
    )
