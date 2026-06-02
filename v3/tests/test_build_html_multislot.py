"""Tests build_html — nommage multi-créneaux dans la liste des bulletins.

Vérifie :
  - le tri date PUIS créneau décroissant (soir avant midi avant matin) ;
  - le libellé lisible du créneau (UTC 05→matin, 10→midi, 16→soir, sinon {HH}h) ;
  - la rétro-compat de l'ancien nommage (sans créneau).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_html as bh  # noqa: E402


def test_slot_label():
    assert bh.slot_label("05") == "matin"
    assert bh.slot_label("10") == "midi"
    assert bh.slot_label("16") == "soir"
    assert bh.slot_label("08") == "08h"  # créneau inattendu → fallback {HH}h


def _touch(dir_: Path, name: str) -> None:
    (dir_ / name).write_text("# bulletin\n", encoding="utf-8")


def test_tri_date_puis_creneau_decroissant(tmp_path, monkeypatch):
    monkeypatch.setattr(bh, "BULLETINS_DIR", tmp_path)
    _touch(tmp_path, "bulletin-2026-06-01-16h.md")
    _touch(tmp_path, "bulletin-2026-06-02-05h.md")
    _touch(tmp_path, "bulletin-2026-06-02-10h.md")
    _touch(tmp_path, "bulletin-2026-06-02-16h.md")

    items = bh.list_bulletins()
    ids = [stem for stem, _ in items]
    # Plus récent d'abord : jour 02 soir → midi → matin, puis jour 01 soir.
    assert ids == [
        "2026-06-02-16h",
        "2026-06-02-10h",
        "2026-06-02-05h",
        "2026-06-01-16h",
    ]


def test_payload_slot_lisible(tmp_path, monkeypatch):
    monkeypatch.setattr(bh, "BULLETINS_DIR", tmp_path)
    _touch(tmp_path, "bulletin-2026-06-02-05h.md")
    _touch(tmp_path, "bulletin-2026-06-02-16h.md")
    _touch(tmp_path, "bulletin-2026-05-30.md")  # ancien nommage

    payload = bh.build_payload()
    by_id = {p["id"]: p for p in payload}
    assert by_id["2026-06-02-05h"]["slot"] == "matin"
    assert by_id["2026-06-02-16h"]["slot"] == "soir"
    # Ancien nommage : pas de créneau → slot vide (rétro-compat).
    assert by_id["2026-05-30"]["slot"] == ""
