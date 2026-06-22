"""Fixtures partagées des tests v3.

Garde-fou anti-pollution : `run()`/`stamp_prix_ouverture()` écrivent par défaut
dans le VRAI dossier `v3/data/prix-ouverture/`. Les tests qui appellent
`journaliste.run(stamp_today=True)` sans isoler explicitement ce dossier
polluaient `v3/data/` (fichiers `{date}.json` parasites). Cette fixture autouse
redirige le défaut du module vers un tmp par test → zéro pollution, sans devoir
modifier chaque test individuellement.

Les tests qui passent explicitement `prix_ouverture_dir=...` ne sont pas affectés
(ils gardent leur isolation propre).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


@pytest.fixture(autouse=True)
def _isole_prix_ouverture(tmp_path, monkeypatch):
    """Redirige le dossier prix-ouverture par défaut vers un tmp par test."""
    try:
        import mesure_ouverture as mo  # noqa: PLC0415
    except Exception:  # noqa: BLE001 — module absent dans certains contextes
        return
    tmp_ouv = tmp_path / "_isolated_prix_ouverture"
    tmp_ouv.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mo, "PRIX_OUVERTURE_DIR", tmp_ouv, raising=False)


@pytest.fixture(autouse=True)
def _isole_news_flux(monkeypatch):
    """Isole les tests de l'events-log LIVE pour le veto news↯ et le drapeau ↯.

    `_fresh_high_feed_dirs` (scoring_analyste) lit la VRAIE events-log pour savoir
    quelles news high fraîches contredisent un call. Sans isolation, le rendu et
    la Sélection dépendraient des news du jour (tests non déterministes). Défaut :
    AUCUNE news de flux. Les tests qui exercent la fonctionnalité re-monkeypatchent
    `_fresh_high_feed_dirs` APRÈS ce fixture (l'override prime)."""
    try:
        import scoring_analyste as _sa  # noqa: PLC0415
    except Exception:  # noqa: BLE001 — module absent dans certains contextes
        return
    monkeypatch.setattr(_sa, "_fresh_high_feed_dirs", lambda now: {}, raising=False)
