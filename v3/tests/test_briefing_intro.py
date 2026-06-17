"""Tests PARTIE A — Intro « Décor du jour » du Briefing 7h (déterministe, zéro LLM).

Couvre les helpers d'intro factuelle (build_intro_block + sous-helpers) :
- intro avec / sans catalyseur J0 (monkeypatch du calendrier éco)
- thèmes dominants avec / sans events
- top news avec events high/medium vs aucun (→ message « pas d'actualité »)
- non-régression : le briefing existant garde sa section « ## Briefing du jour »
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import briefing  # noqa: E402


# Réutilise un corpus v2 réaliste (high/medium/low) pour exercer le tri/filtre.
FIXTURE_V2 = """# events-log v2

| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29 |  | Iran | Iran airstrikes escalate | BRENT | intraday | 1 | bbc | Moyen-Orient | geopolitical |  | BRENT:LONG:85;GOLD:LONG:75 | high | confirmed |
| 2026-05-29 |  | OPEC | OPEC discusses cut | BRENT | intraday | 1 | bbc | Global | commodity |  | BRENT:LONG:70 | medium | reported |
| 2026-05-29 |  | FOMC | Fed minutes cautious | SP500 | intraday | 1 | cnbc | US | central_bank_subtle |  | SP500:SHORT:60 | low | confirmed |
"""

FIXTURE_LOW_ONLY = """# events-log low-only

| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29 |  | x | Minor wheat note | WHEAT | intraday | 1 | bbc | Global | commodity |  | WHEAT:LONG:30 | low | reported |
"""


@pytest.fixture
def today():
    return date(2026, 5, 29)


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 7, 0)


def _events(tmp_path, content):
    p = tmp_path / "events-log.md"
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Catalyseurs J0 dans l'intro (avec / sans)
# ---------------------------------------------------------------------------

def test_intro_avec_catalyseur(monkeypatch, today, now_fixed, tmp_path):
    monkeypatch.setattr(briefing, "_catalyseurs_j0_noms", lambda now: ["CPI US", "FOMC"])
    p = _events(tmp_path, FIXTURE_V2)
    impactful = briefing.filter_recent_impactful(briefing.parse_events(p), today)
    groups = briefing.group_by_actif(impactful)
    lines = briefing.build_intro_block(impactful, groups, today, now_fixed)
    txt = "\n".join(lines)
    assert "Décor du jour" in txt
    assert "Catalyseur(s) du jour : CPI US, FOMC." in txt


def test_intro_sans_catalyseur(monkeypatch, today, now_fixed, tmp_path):
    monkeypatch.setattr(briefing, "_catalyseurs_j0_noms", lambda now: [])
    p = _events(tmp_path, FIXTURE_V2)
    impactful = briefing.filter_recent_impactful(briefing.parse_events(p), today)
    groups = briefing.group_by_actif(impactful)
    txt = "\n".join(briefing.build_intro_block(impactful, groups, today, now_fixed))
    assert "Pas de catalyseur majeur identifié au calendrier." in txt


def test_catalyseurs_j0_noms_tolerant(monkeypatch):
    # Si le module calendrier lève → liste vide (zéro invention, jamais de crash).
    import builtins
    real_import = builtins.__import__

    def boom(name, *a, **k):
        if name == "scoring_analyste":
            raise RuntimeError("calendrier KO")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", boom)
    assert briefing._catalyseurs_j0_noms(datetime(2026, 5, 29, 7, 0)) == []


# ---------------------------------------------------------------------------
# Thèmes dominants (avec / sans)
# ---------------------------------------------------------------------------

def test_themes_dominants_pondere_materialite(today, tmp_path):
    p = _events(tmp_path, FIXTURE_V2)
    impactful = briefing.filter_recent_impactful(briefing.parse_events(p), today)
    groups = briefing.group_by_actif(impactful)
    themes = briefing._themes_dominants(groups)
    # Pétrole (2 events dont un high) doit dominer.
    assert "Pétrole" in themes
    assert len(themes) <= briefing.MAX_THEMES_INTRO


def test_themes_dominants_vide():
    assert briefing._themes_dominants({}) == []
    assert briefing._themes_dominants({"Autres": [{"materiality": "high"}]}) == []


def test_intro_sans_theme(monkeypatch, today, now_fixed):
    monkeypatch.setattr(briefing, "_catalyseurs_j0_noms", lambda now: [])
    txt = "\n".join(briefing.build_intro_block([], {}, today, now_fixed))
    assert "Aucun thème news dominant ce matin." in txt
    assert "Pas d'actualité à fort impact ce matin." in txt


# ---------------------------------------------------------------------------
# Top news : high/medium présents vs aucun
# ---------------------------------------------------------------------------

def test_top_news_high_medium(today, tmp_path):
    p = _events(tmp_path, FIXTURE_V2)
    impactful = briefing.filter_recent_impactful(briefing.parse_events(p), today)
    lignes = briefing._top_news_lignes(impactful)
    assert lignes, "des events high/medium doivent produire des lignes"
    # high d'abord (Iran), avec actif nommé.
    assert "Iran airstrikes escalate" in lignes[0]
    assert "Pétrole" in lignes[0]
    # le low (Fed minutes) est exclu du TOP.
    assert all("Fed minutes cautious" not in l for l in lignes)


def test_top_news_aucun_high_medium(today, tmp_path):
    # Corpus uniquement low → top news vide → message géré par build_intro_block.
    p = _events(tmp_path, FIXTURE_LOW_ONLY)
    impactful = briefing.filter_recent_impactful(briefing.parse_events(p), today)
    assert briefing._top_news_lignes(impactful) == []
    txt = "\n".join(briefing.build_intro_block(impactful, briefing.group_by_actif(impactful), today))
    assert "Pas d'actualité à fort impact ce matin." in txt


# ---------------------------------------------------------------------------
# Non-régression : le briefing complet contient intro + section legacy
# ---------------------------------------------------------------------------

def test_build_briefing_contient_intro_et_section(monkeypatch, today, tmp_path):
    monkeypatch.setattr(briefing, "_catalyseurs_j0_noms", lambda now: ["CPI US"])
    p = _events(tmp_path, FIXTURE_V2)
    md = briefing.build_briefing(events_path=p, today=today)
    assert "## Décor du jour" in md          # PARTIE A (intro)
    assert "## Briefing du jour" in md        # section legacy non régressée
    assert "Catalyseur(s) du jour : CPI US." in md


def test_intro_ne_casse_pas_si_helper_leve(monkeypatch, today, tmp_path):
    # build_intro_block qui lève → le briefing garde quand même sa section legacy.
    def boom(*a, **k):
        raise RuntimeError("intro KO")

    monkeypatch.setattr(briefing, "build_intro_block", boom)
    p = _events(tmp_path, FIXTURE_V2)
    md = briefing.build_briefing(events_path=p, today=today)
    assert "## Briefing du jour" in md
