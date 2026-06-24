"""Tests du fetch indices US via OANDA (source future, sans VPS).

Couvre : parsing du mid (bid/ask), best-effort (token absent / prix non coté),
contrat du fichier futures-us/{date}.json (1ère cotation = référence, dernier
prix par instrument, append des snapshots).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fetch_us_index as fx  # noqa: E402

UTC = timezone.utc


def test_mid_from_price_bid_ask():
    price = {"bids": [{"price": "5500.0"}], "asks": [{"price": "5502.0"}]}
    assert fx._mid_from_price(price) == 5501.0


def test_mid_from_price_closeout_fallback():
    price = {"bids": [], "asks": [], "closeoutBid": "100.0", "closeoutAsk": "102.0"}
    assert fx._mid_from_price(price) == 101.0


def test_mid_from_price_vide():
    assert fx._mid_from_price({"bids": [], "asks": []}) is None


def test_fetch_oanda_prices_token_absent(monkeypatch):
    monkeypatch.delenv("OANDA_API_TOKEN", raising=False)
    # Sans token → {} (best-effort, zéro invention, aucun réseau).
    assert fx.fetch_oanda_prices() == {}


def test_fetch_oanda_prices_fetcher_injecte():
    out = fx.fetch_oanda_prices(fetcher=lambda: {"SPX500_USD": 5500.0})
    assert out == {"SPX500_USD": 5500.0}


def test_write_snapshot_vide_n_ecrit_rien(tmp_path):
    assert fx.write_snapshot({}, base_dir=tmp_path) is None
    assert not list(tmp_path.glob("*.json"))


def test_write_snapshot_premiere_cotation_est_reference(tmp_path):
    now1 = datetime(2026, 6, 8, 6, 0, tzinfo=UTC)   # ~8h Paris (entrée)
    now2 = datetime(2026, 6, 8, 10, 0, tzinfo=UTC)  # ~12h Paris (suivi)
    fx.write_snapshot({"SPX500_USD": 5500.0}, now=now1, base_dir=tmp_path)
    p = fx.write_snapshot({"SPX500_USD": 5533.0}, now=now2, base_dir=tmp_path)
    data = json.loads(Path(p).read_text(encoding="utf-8"))
    # Dernier prix = 2e cotation ; 1ère cotation conservée comme référence.
    assert data["SPX500_USD"]["price"] == 5533.0
    assert data["snapshots"][0]["SPX500_USD"] == 5500.0
    assert len(data["snapshots"]) == 2
    assert data["date"] == "2026-06-08"


def test_write_snapshot_nom_fichier_jour_paris(tmp_path):
    # 23h30 UTC = 01h30 Paris le LENDEMAIN → le fichier doit porter le jour Paris.
    now = datetime(2026, 6, 7, 23, 30, tzinfo=UTC)
    p = fx.write_snapshot({"NAS100_USD": 19800.0}, now=now, base_dir=tmp_path)
    assert Path(p).name == "2026-06-08.json"
