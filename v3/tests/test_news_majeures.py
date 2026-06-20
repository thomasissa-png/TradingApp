"""Tests — News majeures (high) dans les suivis 12h/18h (brief A).

Couvre :
- parsing de l'horodatage d'INGESTION (batch-comment) par event ;
- filtre matérialité high + cutoff heure ;
- event sans horodatage d'ingestion → ignoré (zéro invention) ;
- cas vide ;
- rendu des lignes côté run_suivi (cutoff Paris → UTC, libellé).
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import briefing as B  # noqa: E402
import run_suivi as RS  # noqa: E402


HEADER = (
    "# log\n"
    "| date | L1 | L2 | trigger | cours | latence | R | source | zone | cat | "
    "pat | impacts | materiality | reliability | event_id | canonical_date | nature |\n"
    "|---|---|\n"
)


def _row(date_s, trigger, asset, mat, eid):
    impacts = f"{asset}:LONG:{mat}" if asset else ""
    return (
        f"| {date_s} |  | {trigger[:15]} | {trigger} | {asset} |  | 1 | src | G | "
        f"macro |  | {impacts} | {mat} | confirmed | {eid} | {date_s} | structurel |\n"
    )


@pytest.fixture
def log_multi_batch(tmp_path: Path) -> Path:
    """events-log : un batch à 07h UTC (matin) + un batch à 13h UTC (intraday)."""
    p = tmp_path / "events-log.md"
    content = HEADER
    content += "<!-- batch 2026-06-18T07:00:00Z : 2 events -->\n"
    content += _row("2026-06-18", "Gold morning high move", "GOLD", "high", "m1")
    content += _row("2026-06-18", "Silver morning low", "SILVER", "low", "m2")
    content += "<!-- batch 2026-06-18T13:00:00Z : 2 events -->\n"
    content += _row("2026-06-18", "Brent afternoon high crash", "BRENT", "high", "a1")
    content += _row("2026-06-18", "Copper afternoon medium", "COPPER", "medium", "a2")
    p.write_text(content, encoding="utf-8")
    return p


def test_ingest_ts_assigned_from_batch(log_multi_batch: Path):
    evs = B.parse_events_with_ingest_ts(log_multi_batch)
    assert len(evs) == 4
    by_trigger = {e["trigger"]: e for e in evs}
    assert by_trigger["Gold morning high move"]["ingest_ts"] == datetime(
        2026, 6, 18, 7, 0, tzinfo=timezone.utc
    )
    assert by_trigger["Brent afternoon high crash"]["ingest_ts"] == datetime(
        2026, 6, 18, 13, 0, tzinfo=timezone.utc
    )


def test_filtre_high_et_cutoff(log_multi_batch: Path):
    evs = B.parse_events_with_ingest_ts(log_multi_batch)
    # Depuis 12h UTC : seul le batch 13h compte → Brent (high). Copper est medium.
    cut = datetime(2026, 6, 18, 12, 0, tzinfo=timezone.utc)
    nm = B.news_majeures_depuis(evs, cut, date(2026, 6, 18))
    assert [e["trigger"] for e in nm] == ["Brent afternoon high crash"]


def test_filtre_depuis_matin_inclut_les_deux_high(log_multi_batch: Path):
    evs = B.parse_events_with_ingest_ts(log_multi_batch)
    # Depuis 06h UTC : les deux batchs → 2 high (Gold matin + Brent aprem),
    # triés par fraîcheur (le plus récent d'abord).
    cut = datetime(2026, 6, 18, 6, 0, tzinfo=timezone.utc)
    nm = B.news_majeures_depuis(evs, cut, date(2026, 6, 18))
    assert [e["trigger"] for e in nm] == [
        "Brent afternoon high crash",
        "Gold morning high move",
    ]


def test_event_sans_horodatage_ignore(tmp_path: Path):
    """Un event AVANT tout batch-comment → ingest_ts None → exclu (zéro invention)."""
    p = tmp_path / "events-log.md"
    content = HEADER
    content += _row("2026-06-18", "Orphan high no batch", "GOLD", "high", "o1")
    content += "<!-- batch 2026-06-18T13:00:00Z : 1 events -->\n"
    content += _row("2026-06-18", "Brent with batch", "BRENT", "high", "b1")
    p.write_text(content, encoding="utf-8")
    evs = B.parse_events_with_ingest_ts(p)
    orphan = next(e for e in evs if e["trigger"] == "Orphan high no batch")
    assert orphan["ingest_ts"] is None
    # Cutoff large : l'orphelin (sans horodatage) reste EXCLU, seul Brent passe.
    cut = datetime(2026, 6, 18, 0, 0, tzinfo=timezone.utc)
    nm = B.news_majeures_depuis(evs, cut, date(2026, 6, 18))
    assert [e["trigger"] for e in nm] == ["Brent with batch"]


def test_cas_vide_aucune_high(tmp_path: Path):
    p = tmp_path / "events-log.md"
    content = HEADER
    content += "<!-- batch 2026-06-18T13:00:00Z : 1 events -->\n"
    content += _row("2026-06-18", "Only medium", "GOLD", "medium", "x1")
    p.write_text(content, encoding="utf-8")
    evs = B.parse_events_with_ingest_ts(p)
    cut = datetime(2026, 6, 18, 0, 0, tzinfo=timezone.utc)
    assert B.news_majeures_depuis(evs, cut, date(2026, 6, 18)) == []


def test_batch_autre_jour_exclu(tmp_path: Path):
    """Un batch high de la veille (17/06) n'apparaît PAS pour le suivi du 18/06."""
    p = tmp_path / "events-log.md"
    content = HEADER
    content += "<!-- batch 2026-06-17T13:00:00Z : 1 events -->\n"
    content += _row("2026-06-17", "Yesterday high", "GOLD", "high", "y1")
    p.write_text(content, encoding="utf-8")
    evs = B.parse_events_with_ingest_ts(p)
    cut = datetime(2026, 6, 18, 6, 0, tzinfo=timezone.utc)
    assert B.news_majeures_depuis(evs, cut, date(2026, 6, 18)) == []


def test_run_suivi_news_majeures_lignes(log_multi_batch: Path):
    """run_suivi.news_majeures_lignes : cutoff 18h (depuis 12h Paris=10h UTC)."""
    now = datetime(2026, 6, 18, 18, 5, tzinfo=RS.PARIS_TZ)
    lignes = RS.news_majeures_lignes("18h", now, events_path=log_multi_batch)
    # Depuis 12h Paris (=10h UTC) → batch 13h UTC compte → Brent high.
    assert len(lignes) == 1
    assert "Pétrole" in lignes[0]
    assert "Brent afternoon high crash" in lignes[0]


def test_run_suivi_news_majeures_vide(tmp_path: Path):
    """Aucune high intraday → liste vide (le rendu affichera « Aucune news majeure »)."""
    p = tmp_path / "events-log.md"
    p.write_text(
        HEADER + "<!-- batch 2026-06-18T13:00:00Z : 0 events -->\n", encoding="utf-8"
    )
    now = datetime(2026, 6, 18, 18, 5, tzinfo=RS.PARIS_TZ)
    assert RS.news_majeures_lignes("18h", now, events_path=p) == []
