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
    session = {"sp500": 0.0, "or": -0.001}            # mouvement overnight signé
    post = {"sp500": 0.0099, "or": 0.002}             # move BRUT depuis la news (+)
    assets = sjd.assemble_assets(
        results, events, NOW,
        fiche_meta={"sp500": {"famille": "indices"}, "or": {"famille": "métaux-précieux"}},
        get_closes=lambda k: closes.get(k, []),
        get_session_move=lambda k: session.get(k),
        get_post_news_move=lambda k, dt: post.get(k),
    )
    by = {a.fiche_key: a for a in assets}
    # S&P : news SHORT rattachée, fond LONG, groupe indices.
    sp = by["sp500"]
    assert len(sp.news) == 1 and sp.news[0].direction == "SHORT"
    assert sp.fond_dir == "LONG"
    assert sp.groupe == "indices"
    assert abs(sp.session_move) < 1e-9
    # post brut +0.99 % sur une news SHORT → favorable (signé) = -0.99 %
    assert sp.news[0].post_news_move < 0


def test_assemble_sans_prix_ne_crash_pas():
    results = [_R("Blé", "ble", {"24h": "LONG"})]
    assets = sjd.assemble_assets(
        results, [], NOW,
        fiche_meta={},
        get_closes=lambda k: [],
        get_session_move=lambda k: None,
        get_post_news_move=lambda k, dt: None,
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
        fiche_meta={"sp500": {"famille": "indices"}},
        get_closes=lambda k: [100, 100, 100],
        get_session_move=lambda k: 0.0,         # prix non contredisant
        get_post_news_move=lambda k, dt: 0.0,   # move pas encore fait
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


def test_per_impact_confidence_filtre_le_tag_faible(monkeypatch):
    # Cas réel : « Warsh hawkish » → EURUSD:LONG:low (tag douteux) ET EURUSD:SHORT:medium.
    # Le LONG:low ne doit PAS déclencher ; le SHORT:medium gagne → EUR/USD SHORT.
    # NB : fond 24h SHORT (concordant) pour isoler la propriété testée (filtrage du
    # tag par-impact) sans la coupler au garde-fou fond R2 — qui rejette à juste titre
    # une news P2 à contre-fond. R2 est couvert par les tests dédiés de selection_jour.
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"EURUSD": "EUR/USD"})
    results = [_R("EUR/USD", "eurusd", {"24h": "SHORT"})]
    events = [
        {"ingest_ts": NOW - timedelta(hours=1), "materiality": "high",
         "reliability": "confirmed", "nature": "ponctuel", "trigger": "Warsh hawkish A",
         "impacts": "EURUSD:LONG:low"},
        {"ingest_ts": NOW - timedelta(hours=1), "materiality": "high",
         "reliability": "confirmed", "nature": "ponctuel", "trigger": "Warsh hawkish B",
         "impacts": "EURUSD:SHORT:medium"},
    ]
    assets = sjd.assemble_assets(
        results, events, NOW,
        fiche_meta={"eurusd": {"famille": "fx"}},
        get_closes=lambda k: [1.14, 1.14, 1.14],
        get_session_move=lambda k: 0.0,
        get_post_news_move=lambda k, dt: 0.0,
    )
    top = sj.select_top3(assets, NOW, ["eurusd"])
    assert top and top[0].actif == "EUR/USD" and top[0].direction == "SHORT"


def test_impact_low_seul_ne_declenche_pas(monkeypatch):
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"EURUSD": "EUR/USD"})
    results = [_R("EUR/USD", "eurusd", {"24h": "LONG"})]
    events = [{"ingest_ts": NOW - timedelta(hours=1), "materiality": "high",
               "reliability": "confirmed", "nature": "ponctuel", "trigger": "x",
               "impacts": "EURUSD:LONG:low"}]
    assets = sjd.assemble_assets(
        results, events, NOW, fiche_meta={}, get_closes=lambda k: [],
        get_session_move=lambda k: None, get_post_news_move=lambda k, dt: None)
    assert sj.select_top3(assets, NOW, ["eurusd"]) == []


def test_pas_de_proxy_futures_inerte():
    # Vérifié sur pièces : Twelve ne sert aucun future CME + yfinance bloqué CI →
    # un proxy ES=F/NQ=F serait INERTE. On n'en met donc aucun (honnêteté data).
    assert sjd.PROXY_OVERNIGHT == {}


def test_R1_fraicheur_sur_premiere_apparition(monkeypatch):
    # Cas réel Or « avril » (hash 26051cf17f92) : RE-LOGGÉE ce matin (ingest_ts frais)
    # mais 1ʳᵉ apparition il y a ~20j. assemble_assets doit retenir l'ingest_ts MINIMAL
    # par event_id → la NewsItem a un âge de ~20j → tuée par FRESH_MAX_H. Sans cette
    # règle, la ligne re-loggée (1h) passerait le filtre et justifierait un Or LONG.
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"GOLD": "Or"})
    results = [_R("Or", "or", {"24h": "SHORT"})]
    vieux = NOW - timedelta(days=20)
    frais = NOW - timedelta(hours=1)
    base = {"materiality": "medium", "reliability": "confirmed", "nature": "structurel",
            "trigger": "Banques centrales achats nets d'or en avril",
            "impacts": "GOLD:LONG:high", "event_id": "26051cf17f92"}
    events = [
        {**base, "ingest_ts": vieux},   # 1ʳᵉ apparition
        {**base, "ingest_ts": frais},   # re-journalisation de ce matin
    ]
    assets = sjd.assemble_assets(
        results, events, NOW, fiche_meta={"or": {"famille": "métaux-précieux"}},
        get_closes=lambda k: [], get_session_move=lambda k: None,
        get_post_news_move=lambda k, dt: None)
    a = assets[0]
    # Les deux lignes sont rattachées, mais toutes deux datées de la 1ʳᵉ apparition.
    ages = sorted(sj._fresh_hours(n, NOW) for n in a.news)
    assert all(age > sj.FRESH_MAX_H for age in ages)
    # → aucun pari Or LONG (catalyseur trop vieux).
    assert sj.select_top3(assets, NOW, ["or"]) == []


def test_R1_sans_event_id_garde_ingest_ts_de_ligne(monkeypatch):
    # Pas de hash exploitable → comportement actuel conservé (zéro invention) :
    # la news garde l'ingest_ts de sa ligne (frais → reste éligible).
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"GOLD": "Or"})
    results = [_R("Or", "or", {"24h": "SHORT"})]
    events = [_ev("GOLD", "SHORT", age_h=1.0)]  # _ev ne pose pas d'event_id
    assets = sjd.assemble_assets(
        results, events, NOW, fiche_meta={"or": {"famille": "x"}},
        get_closes=lambda k: [], get_session_move=lambda k: None,
        get_post_news_move=lambda k, dt: None)
    assert abs(sj._fresh_hours(assets[0].news[0], NOW) - 1.0) < 1e-6


def test_garde_fou_contradiction_via_session_move(monkeypatch):
    # News SHORT P1 sur S&P, MAIS le future overnight monte +0,5 % (contredit le SHORT
    # de façon soutenue > 0,4 %) → la cellule est vétée. C'est le garde-fou rebranché.
    monkeypatch.setattr(sjd, "_CODE_TO_LABEL", {"SP500": "S&P 500"})
    results = [_R("S&P 500", "sp500", {"24h": "LONG"})]
    events = [_ev("SP500", "SHORT", materiality="high", reliability="confirmed")]
    assets = sjd.assemble_assets(
        results, events, NOW, fiche_meta={"sp500": {"famille": "indices"}},
        get_closes=lambda k: [100, 100, 100],
        get_session_move=lambda k: 0.005,        # future +0,5 % → contredit le SHORT
        get_post_news_move=lambda k, dt: 0.0)
    assert sj.select_top3(assets, NOW, ["sp500"]) == []
