"""Tests scoring_analyste.load_veille — exclusion de TOUS les créneaux du jour.

Avant : exclusion par nom exact `bulletin-{today}` → avec 3 runs/jour, les
créneaux du matin/midi du JOUR COURANT (bulletin-{today}-05h.md, etc.) étaient
pris pour la « veille » → un run du soir aurait lu son propre matin comme veille.
Après : exclusion par PRÉFIXE `bulletin-{today}` → tous les créneaux du jour
sont écartés, on remonte au vrai jour précédent.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


def _write(dir_: Path, name: str) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / name).write_text(
        "| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n", encoding="utf-8"
    )


def test_load_veille_exclut_tous_les_creneaux_du_jour(tmp_path):
    # « Maintenant » = 2026-06-02 16h UTC (run du soir).
    now = datetime(2026, 6, 2, 16, 0, tzinfo=timezone.utc)
    # Créneaux du JOUR COURANT : ne doivent JAMAIS être pris pour la veille.
    _write(tmp_path, "bulletin-2026-06-02-05h.md")
    _write(tmp_path, "bulletin-2026-06-02-10h.md")
    _write(tmp_path, "bulletin-2026-06-02-16h.md")
    # Vrai jour précédent.
    _write(tmp_path, "bulletin-2026-06-01-16h.md")

    veille_path, _conc = sa.load_veille(tmp_path, now)
    assert veille_path is not None
    assert veille_path.name == "bulletin-2026-06-01-16h.md"


def test_load_veille_exclut_ancien_nommage_du_jour(tmp_path):
    """Rétro-compat : bulletin-{today}.md (sans créneau) reste exclu du jour."""
    now = datetime(2026, 6, 2, 16, 0, tzinfo=timezone.utc)
    _write(tmp_path, "bulletin-2026-06-02.md")        # ancien nommage, jour courant
    _write(tmp_path, "bulletin-2026-06-01.md")        # veille
    veille_path, _conc = sa.load_veille(tmp_path, now)
    assert veille_path is not None
    assert veille_path.name == "bulletin-2026-06-01.md"
