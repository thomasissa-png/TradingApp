"""Tests — fetch des futures US (ES=F / NQ=F) via yfinance.

Zéro réseau : le fetcher yfinance est INJECTÉ. Couvre :
- fetch OK → écrit le JSON attendu (dernier prix par ticker + snapshots) ;
- append : 2 fetchs successifs → 2 snapshots, dernier prix mis à jour ;
- fetcher KO/vide → n'écrit RIEN (pas de fichier vide, zéro invention) ;
- main() → exit 0 même quand le fetch est vide (best-effort total).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import fetch_us_futures as fuf  # noqa: E402


def _now(h=5, m=31):
    return datetime(2026, 6, 23, h, m, tzinfo=timezone.utc)


def test_fetch_futures_ok_filtre_les_ko():
    prices = {"ES=F": 5512.25, "NQ=F": 0.0}  # NQ=F à 0 = vide
    fetcher = lambda t: prices.get(t)  # noqa: E731
    out = fuf.fetch_futures(fetcher=fetcher)
    assert out == {"ES=F": 5512.25}  # NQ=F (0) filtré : zéro invention


def test_write_snapshot_ecrit_le_json_attendu(tmp_path):
    path = fuf.write_snapshot(
        {"ES=F": 5500.0, "NQ=F": 19800.0}, now=_now(5, 1), base_dir=tmp_path
    )
    assert path is not None and path.name == "2026-06-23.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["date"] == "2026-06-23"
    assert data["ES=F"]["price"] == 5500.0
    assert data["NQ=F"]["price"] == 19800.0
    assert data["ES=F"]["ts"].endswith("+00:00")
    assert len(data["snapshots"]) == 1
    assert data["snapshots"][0]["ES=F"] == 5500.0


def test_write_snapshot_append_met_a_jour_le_dernier_prix(tmp_path):
    fuf.write_snapshot({"ES=F": 5500.0, "NQ=F": 19800.0}, now=_now(5, 1), base_dir=tmp_path)
    path = fuf.write_snapshot({"ES=F": 5512.25, "NQ=F": 19840.5}, now=_now(5, 31), base_dir=tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    # Dernier prix = le plus récent.
    assert data["ES=F"]["price"] == 5512.25
    assert data["NQ=F"]["price"] == 19840.5
    # 2 snapshots, ordonnés (ancien → récent).
    assert len(data["snapshots"]) == 2
    assert data["snapshots"][0]["ES=F"] == 5500.0
    assert data["snapshots"][1]["ES=F"] == 5512.25


def test_write_snapshot_vide_n_ecrit_rien(tmp_path):
    path = fuf.write_snapshot({}, now=_now(), base_dir=tmp_path)
    assert path is None
    # Aucun fichier créé (pas de fichier vide).
    assert list(tmp_path.glob("*.json")) == []


def test_fetch_futures_tout_ko_renvoie_dict_vide():
    out = fuf.fetch_futures(fetcher=lambda t: None)
    assert out == {}


def test_main_exit_0_meme_si_fetch_vide(tmp_path, monkeypatch):
    # Force fetch_futures à renvoyer vide → write_snapshot n'écrit rien → exit 0.
    monkeypatch.setattr(fuf, "fetch_futures", lambda *a, **k: {})
    rc = fuf.main(["--out-dir", str(tmp_path)])
    assert rc == 0
    assert list(tmp_path.glob("*.json")) == []
