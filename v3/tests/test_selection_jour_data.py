"""Couche d'assemblage du moteur top 3 (selection_jour_data) — tests purs."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import selection_jour as sj  # noqa: E402
import selection_jour_data as sjd  # noqa: E402

NOW = datetime(2026, 6, 22, 7, 0, tzinfo=timezone.utc)


@dataclass
class _R:
    nom: str
    fiche_key: str
    conclusions: Dict[str, str] = field(default_factory=dict)


def _ev(asset_code, direction, materiality="high", reliability="confirmed",
        nature="ponctuel", age_h=1.0, trigger="Choc majeur sur le marché"):
    return {
        "ingest_ts": NOW - timedelta(hours=age_h),
        "materiality": materiality,
        "reliability": reliability,
        "nature": nature,
        "trigger": trigger,
        "impacts": [{"asset": asset_code, "direction": direction}],
    }


def test_assemble_rattache_news_et_calcule_session_move(monkeypatch):
    # _CODE_TO_LABEL : SP500 → "S&P 500"
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"SP500": "S&P 500", "GOLD": "Or"})
    results = [
        _R("S&P 500", "sp500", {"24h": "LONG"}),
        _R("Or", "or", {"24h": "SHORT"}),
    ]
    events = [_ev("SP500", "SHORT"), _ev("GOLD", "SHORT")]
    closes = {"sp500": [100, 101, 102], "or": [50, 50.5, 51]}
    prix = {"sp500": 102.0, "or": 51.5}  # spot
    # prix à l'heure de la news (1h avant) : pour le post_news_move
    price_at = {"sp500": 101.0, "or": 51.0}
    assets = sjd.assemble_assets(
        results, events, NOW,
        prix_reference=prix,
        fiche_meta={"sp500": {"famille": "indices"}, "or": {"famille": "métaux-précieux"}},
        get_closes=lambda k: closes.get(k, []),
        get_price_at=lambda k, dt: price_at.get(k),
    )
    by = {a.fiche_key: a for a in assets}
    # S&P : news SHORT rattachée, fond LONG, groupe indices.
    sp = by["sp500"]
    assert len(sp.news) == 1 and sp.news[0].direction == "SHORT"
    assert sp.fond_dir == "LONG"
    assert sp.groupe == "indices"
    # session_move = spot/prev_close - 1 = 102/102 - 1 = 0
    assert abs(sp.session_move) < 1e-9
    # post_news_move SHORT : spot 102 vs news 101 → raw +0.99 % → favorable SHORT = -0.99 %
    assert sp.news[0].post_news_move < 0


def test_assemble_sans_prix_ne_crash_pas():
    results = [_R("Blé", "ble", {"24h": "LONG"})]
    assets = sjd.assemble_assets(
        results, [], NOW,
        prix_reference={},
        fiche_meta={},
        get_closes=lambda k: [],
        get_price_at=lambda k, dt: None,
    )
    a = assets[0]
    assert a.session_move is None and a.closes == [] and a.news == []
    assert a.groupe == "ble"  # pas de famille → fiche_key comme groupe


def test_assemble_bout_en_bout_selectionne(monkeypatch):
    # Une grosse news SHORT fraîche sur le S&P, prix non contredisant → top 3.
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"SP500": "S&P 500"})
    results = [_R("S&P 500", "sp500", {"24h": "LONG"})]
    events = [_ev("SP500", "SHORT", materiality="high", reliability="confirmed")]
    assets = sjd.assemble_assets(
        results, events, NOW,
        prix_reference={"sp500": 100.0},
        fiche_meta={"sp500": {"famille": "indices"}},
        get_closes=lambda k: [100, 100, 100],
        get_price_at=lambda k, dt: 100.0,  # pas de move post-news
    )
    top = sj.select_top3(assets, NOW, ["sp500"])
    assert [p.actif for p in top] == ["S&P 500"]
    assert top[0].direction == "SHORT" and top[0].porte == "news"


def test_load_fiche_meta_lit_les_vraies_fiches():
    meta = sjd.load_fiche_meta(ROOT / "config" / "fiches")
    assert meta.get("or", {}).get("ticker") == "GC=F"
    assert meta["or"]["famille"] == "métaux-précieux"
    assert meta["sp500"]["ticker"] == "^GSPC"


def test_build_top3_block_rendu():
    picks = [
        sj.Pick(actif="S&P 500", fiche_key="sp500", direction="SHORT",
                porte="news", palier=1, raison="Chine restreint les exports"),
        sj.Pick(actif="Cuivre", fiche_key="cuivre", direction="LONG",
                porte="momentum", palier=2, raison="momentum haussier (accélération + cassure 7j)"),
    ]
    txt = "\n".join(sjd.build_top3_block(picks, prix_reference={"sp500": 100.0}))
    assert "## 🎯 Aujourd'hui" in txt
    assert "**S&P 500** SHORT @ 100" in txt
    assert "catalyseur news" in txt and "momentum" in txt


def test_build_top3_block_vide():
    txt = "\n".join(sjd.build_top3_block([]))
    assert "Aucun pari qualifié" in txt
