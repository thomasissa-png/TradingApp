"""Tests briefing v2 — tri par matérialité, flèches directionnelles, rétro-compat."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import briefing  # noqa: E402


# ---------------------------------------------------------------------------
# Fixture log v2 (14 cols) avec materiality variée
# ---------------------------------------------------------------------------

FIXTURE_V2 = """# events-log v2

| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-28 |  | Iran | Iran low-key signal | BRENT | intraday | 1 | bbc | Moyen-Orient | geopolitical |  | BRENT:LONG:50 | low | reported |
| 2026-05-29 |  | Iran | Iran airstrikes escalate | BRENT | intraday | 1 | reuters | Moyen-Orient | geopolitical |  | BRENT:LONG:85;GOLD:LONG:75 | high | confirmed |
| 2026-05-29 |  | OPEC | OPEC discusses cut | BRENT | intraday | 1 | bloomberg | Global | commodity |  | BRENT:LONG:70 | medium | reported |
| 2026-05-29 |  | FOMC | Fed minutes cautious | SP500 | intraday | 1 | cnbc | US | central_bank_subtle |  | SP500:SHORT:60 | medium | confirmed |
"""


# Fixture mixte v2 + legacy pour rétro-compat
FIXTURE_MIXED = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29 |  | v2 | v2 line with impacts | BRENT | intraday | 1 | s | Global | geopolitical |  | BRENT:LONG:80 | high | confirmed |
| 2026-05-29 |  | legacy | legacy line no impacts | Brent (BZ=F) | intraday | 1 | s | Global | geopolitical |  |
"""


@pytest.fixture
def log_v2(tmp_path):
    p = tmp_path / "events-log.md"
    p.write_text(FIXTURE_V2, encoding="utf-8")
    return p


@pytest.fixture
def log_mixed(tmp_path):
    p = tmp_path / "events-log.md"
    p.write_text(FIXTURE_MIXED, encoding="utf-8")
    return p


@pytest.fixture
def today():
    return date(2026, 5, 29)


# ---------------------------------------------------------------------------
# Tri par matérialité
# ---------------------------------------------------------------------------

def test_sort_by_materiality(log_v2, today):
    evs = briefing.parse_events(log_v2)
    kept = briefing.filter_recent_impactful(evs, today)
    # 3 events Brent + 1 SP500 = 4 events
    assert len(kept) == 4
    # Sur Brent : high doit passer avant medium et low
    brent_evs = [e for e in kept if "BRENT" in e.get("impacts", "")]
    sorted_evs = briefing._sort_by_materiality_then_date(brent_evs)
    materialities = [e.get("materiality") for e in sorted_evs]
    # high d'abord, puis medium, puis low
    assert materialities[0] == "high"
    assert materialities[-1] == "low"


def test_briefing_renders_high_first(log_v2, today):
    md = briefing.build_briefing(log_v2, today=today)
    # Le high "airstrikes" doit apparaître AVANT le low "low-key signal"
    idx_high = md.index("airstrikes")
    idx_low = md.index("low-key signal")
    assert idx_high < idx_low


def test_briefing_includes_arrow_long(log_v2, today):
    md = briefing.build_briefing(log_v2, today=today)
    # Flèche ↑ doit apparaître pour BRENT (LONG)
    assert "↑" in md


def test_briefing_includes_arrow_short(log_v2, today):
    md = briefing.build_briefing(log_v2, today=today)
    # Flèche ↓ doit apparaître pour SP500 (SHORT)
    assert "↓" in md


def test_briefing_marks_high_materiality(log_v2, today):
    md = briefing.build_briefing(log_v2, today=today)
    # Tag [high] doit apparaître sur les events high matérialité
    assert "[high]" in md


# ---------------------------------------------------------------------------
# Rétro-compat parser : ligne legacy + ligne v2 dans même fichier
# ---------------------------------------------------------------------------

def test_parse_supports_mixed_v2_and_legacy(log_mixed, today):
    evs = briefing.parse_events(log_mixed)
    assert len(evs) == 2
    # Trie par materiality desc
    sorted_evs = briefing._sort_by_materiality_then_date(evs)
    # v2 high d'abord
    assert sorted_evs[0]["materiality"] == "high"
    # legacy a materiality="" (rang 0)
    assert sorted_evs[1]["materiality"] == ""


def test_briefing_legacy_no_arrow(tmp_path, today):
    """Une ligne legacy (sans impacts) ne déclenche pas de flèche."""
    legacy_only = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29 |  | Iran | legacy event | Brent (BZ=F) | intraday | 1 | s | Global | geopolitical |  |
"""
    p = tmp_path / "log.md"
    p.write_text(legacy_only, encoding="utf-8")
    md = briefing.build_briefing(p, today=today)
    assert "### Pétrole" in md
    assert "legacy event" in md
    # Pas de flèche directionnelle
    assert "↑" not in md
    assert "↓" not in md


def test_briefing_v2_groups_via_ia_asset(log_v2, today):
    """Un event avec impacts BRENT:... mais cours='BRENT' doit être groupé sous 'Pétrole'."""
    md = briefing.build_briefing(log_v2, today=today)
    assert "### Pétrole" in md
    assert "### S&P 500" in md


# ---------------------------------------------------------------------------
# Helpers unitaires
# ---------------------------------------------------------------------------

def test_parse_impacts_compact_unitaire():
    out = briefing._parse_impacts_compact("BRENT:LONG:85;GOLD:LONG:70")
    assert len(out) == 2
    assert out[0]["asset"] == "BRENT"
    assert out[1]["confidence"] == 70


def test_direction_arrow_for_actif():
    ev = {"impacts": "BRENT:LONG:80;SP500:SHORT:60"}
    assert briefing._direction_arrow_for(ev, "Pétrole") == "↑"
    assert briefing._direction_arrow_for(ev, "S&P 500") == "↓"
    # Actif absent → flèche du 1er impact
    assert briefing._direction_arrow_for(ev, "Café") == "↑"
    # Pas d'impacts → vide
    assert briefing._direction_arrow_for({"impacts": ""}, "Pétrole") == ""


def test_filter_keeps_v2_without_cours(tmp_path, today):
    """Event v2 sans `cours` mais avec impacts → gardé."""
    log = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29 |  | x | v2 sans cours | | intraday | 1 | s | Global | geopolitical |  | BRENT:LONG:80 | high | confirmed |
"""
    p = tmp_path / "log.md"
    p.write_text(log, encoding="utf-8")
    evs = briefing.parse_events(p)
    kept = briefing.filter_recent_impactful(evs, today)
    assert len(kept) == 1
