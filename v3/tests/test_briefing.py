"""Tests briefing — filtrage, groupement, mapping ticker, insertion bulletin."""

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
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_LOG = """# TradingApp v3 — Events log

| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-29 | Énergie | Pétrole | Iran ceasefire optimism drives Brent lower | Brent (BZ=F) | intraday | 1 | cnbc_top | Moyen-Orient | geopolitical |  |
| 2026-05-29 | Macro | PCE | Core PCE 3.3% in line with expectations | S&P 500 (^GSPC), DXY (DX-Y.NYB) | intraday | 1 | cnbc_economy | US | macro |  |
| 2026-05-29 | Banques-centrales | BCE | BCE fera ce qui est nécessaire | EUR/USD (EUR=X) | intraday | 1 | cnbc_economy | EU | central_bank_subtle |  |
| 2026-05-28 | Énergie | Café | Mauvaises récoltes Brésil font grimper café | Café (KC=F) | jours | 1 | bbc_business | Global | commodity |  |
| 2026-05-28 | Earnings | Dell | Dell AI server revenue +757% YoY | Dell (DELL) | intraday | 1 | cnbc_top | US | earnings |  |
| 2026-05-15 | Énergie | Pétrole | Vieux event hors fenêtre | Brent (BZ=F) | intraday | 1 | cnbc_top | Global | geopolitical |  |
| 2026-05-29 | Tech-IA | Smart glasses | Meta smart glasses selling well |  | intraday | 1 | bbc_business | US | sector |  |
| 2026-05-29 |  |  | Filler news sans cours sans catégorie impactante |  |  | 1 | bbc_business |  | other |  |
"""


@pytest.fixture
def events_log(tmp_path: Path) -> Path:
    p = tmp_path / "events-log.md"
    p.write_text(FIXTURE_LOG, encoding="utf-8")
    return p


@pytest.fixture
def today() -> date:
    return date(2026, 5, 29)


# ---------------------------------------------------------------------------
# parse_events
# ---------------------------------------------------------------------------

def test_parse_events_reads_rows(events_log: Path):
    evs = briefing.parse_events(events_log)
    # 8 lignes data (header + sep ignorés)
    assert len(evs) == 8
    # premier event = Brent
    assert "Brent" in evs[0]["cours"]
    assert evs[0]["cat"] == "geopolitical"


def test_parse_events_missing_file(tmp_path: Path):
    assert briefing.parse_events(tmp_path / "nope.md") == []


# ---------------------------------------------------------------------------
# match_actif (mapping ticker → actif)
# ---------------------------------------------------------------------------

def test_match_actif_ticker_paren():
    assert briefing.match_actif("Brent (BZ=F)") == "Pétrole"
    assert briefing.match_actif("WTI (CL=F)") == "Pétrole"
    assert briefing.match_actif("Café (KC=F)") == "Café"
    assert briefing.match_actif("EUR/USD (EUR=X)") == "EUR/USD"
    assert briefing.match_actif("S&P 500 (^GSPC), DXY (DX-Y.NYB)") == "S&P 500"


def test_match_actif_par_nom():
    assert briefing.match_actif("Brent crude oil") == "Pétrole"
    assert briefing.match_actif("gold spot") == "Or"
    assert briefing.match_actif("Nasdaq composite") == "Nasdaq"


def test_match_actif_hors_univers():
    assert briefing.match_actif("Dell (DELL)") is None
    assert briefing.match_actif("Tesla (TSLA)") is None
    assert briefing.match_actif("") is None


# ---------------------------------------------------------------------------
# filter_recent_impactful
# ---------------------------------------------------------------------------

def test_filter_recent_impactful(events_log: Path, today: date):
    evs = briefing.parse_events(events_log)
    kept = briefing.filter_recent_impactful(evs, today)
    # On garde : Brent, S&P (macro), EUR/USD, Café, Dell (=5)
    # On exclut : vieux Brent (2026-05-15), Meta sans cours, filler other
    assert len(kept) == 5
    triggers = [e["trigger"] for e in kept]
    assert any("Iran ceasefire" in t for t in triggers)
    assert any("PCE" in t for t in triggers)
    assert not any("Vieux event" in t for t in triggers)


# ---------------------------------------------------------------------------
# group_by_actif
# ---------------------------------------------------------------------------

def test_group_by_actif(events_log: Path, today: date):
    evs = briefing.parse_events(events_log)
    kept = briefing.filter_recent_impactful(evs, today)
    groups = briefing.group_by_actif(kept)
    assert "Pétrole" in groups
    assert "S&P 500" in groups
    assert "EUR/USD" in groups
    assert "Café" in groups
    # Dell → Autres (hors univers)
    assert "Autres" in groups
    assert any("Dell" in e["cours"] for e in groups["Autres"])


# ---------------------------------------------------------------------------
# build_briefing
# ---------------------------------------------------------------------------

def test_build_briefing_contient_sections(events_log: Path, today: date):
    md = briefing.build_briefing(events_log, today=today)
    # PARTIE A (16/06) : le briefing s'ouvre désormais sur l'intro « ## Décor du
    # jour » (décor factuel + top news), puis la section « ## Briefing du jour ».
    assert md.startswith("## Décor du jour")
    assert "## Briefing du jour" in md
    assert "events analysés" in md
    assert "### Pétrole" in md
    assert "### S&P 500" in md
    assert "### EUR/USD" in md
    assert "### Café" in md
    # Format puce : [zone] trigger (source)
    assert "[Moyen-Orient]" in md
    assert "(cnbc_top)" in md
    # Mention de la fenêtre 48h
    assert "48h" in md or "fenêtre" in md.lower()


def test_build_briefing_aucun_event(tmp_path: Path, today: date):
    log = tmp_path / "events-log.md"
    log.write_text(
        "| date | L1 | L2 | trigger | cours | latence | R | source | "
        "news_zone | category | pattern_id |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| 2026-05-29 |  |  | Filler |  |  | 1 | s |  | other |  |\n",
        encoding="utf-8",
    )
    md = briefing.build_briefing(log, today=today)
    assert "Aucun event marquant" in md
    assert "## Briefing du jour" in md


def test_build_briefing_pas_de_fichier(tmp_path: Path, today: date):
    md = briefing.build_briefing(tmp_path / "absent.md", today=today)
    assert "## Briefing du jour" in md
    assert "Aucun event marquant" in md


# ---------------------------------------------------------------------------
# prepend_to_bulletin
# ---------------------------------------------------------------------------

BULLETIN_FIXTURE = """# Bulletin Analyste — 2026-05-29

- Généré : 2026-05-29T10:00:00+02:00
- Analyste version : v3.0.0

## Matrice (12 actifs × 3 horizons)

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| Pétrole | LONG (+0.42) | LONG (+0.30) | SHORT (-0.10) |

## Détail par actif
### Pétrole
ligne détail
"""


def test_prepend_to_bulletin_apres_titre(tmp_path: Path, events_log: Path, today: date):
    bull = tmp_path / "bulletin-2026-05-29.md"
    bull.write_text(BULLETIN_FIXTURE, encoding="utf-8")
    md = briefing.build_briefing(events_log, today=today)
    ok = briefing.prepend_to_bulletin(bull, md)
    assert ok is True
    new_content = bull.read_text(encoding="utf-8")
    # Le briefing doit apparaître APRÈS le titre H1 et AVANT la matrice
    idx_titre = new_content.index("# Bulletin Analyste")
    idx_briefing = new_content.index("## Briefing du jour")
    idx_matrice = new_content.index("## Matrice")
    assert idx_titre < idx_briefing < idx_matrice
    # Le détail par actif reste intact (en fin)
    assert "## Détail par actif" in new_content
    assert "### Pétrole\nligne détail" in new_content


def test_prepend_to_bulletin_idempotent(tmp_path: Path, events_log: Path, today: date):
    bull = tmp_path / "bulletin-2026-05-29.md"
    bull.write_text(BULLETIN_FIXTURE, encoding="utf-8")
    md = briefing.build_briefing(events_log, today=today)
    briefing.prepend_to_bulletin(bull, md)
    briefing.prepend_to_bulletin(bull, md)  # re-run
    content = bull.read_text(encoding="utf-8")
    # Un seul bloc Briefing (le 2e remplace le 1er)
    assert content.count("## Briefing du jour") == 1
    # La matrice n'est pas dupliquée
    assert content.count("## Matrice") == 1


def test_prepend_to_bulletin_fichier_absent(tmp_path: Path):
    ok = briefing.prepend_to_bulletin(tmp_path / "absent.md", "## Briefing du jour\n")
    assert ok is False
