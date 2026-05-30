"""Tests routage IA-first dans triggers_classifier (chantier prompt v2).

Couvre :
- IA-first : un event avec impacts[BRENT:LONG] prime sur le keyword matching.
- IA NEUTRAL ne déclenche ni LONG ni SHORT (mais bloque le fallback keyword sur
  le même event car l'IA s'est exprimée).
- Fallback keyword : événement SANS impacts (ancien schéma) → matching texte.
- Cohabitation : un event IA récent + un event keyword plus ancien → IA gagne.
- Conflit LONG/SHORT IA : matérialité d'abord, date ensuite.
- Rétro-compat events-log : parser supporte 11 ET 14 colonnes.
- Asset hors-énum dans encoded impacts → ignoré.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402


@pytest.fixture
def triggers_cfg():
    return tc.load_triggers_config()


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


def _ev(date_str: str, *, trigger: str = "", cours: str = "", l2: str = "",
        category: str = "", impacts: str = "", materiality: str = "",
        reliability: str = "") -> dict:
    return {
        "date": date_str,
        "l1": "",
        "l2": l2,
        "trigger": trigger,
        "cours": cours,
        "source": "test",
        "news_zone": "Global",
        "category": category,
        "impacts": impacts,
        "materiality": materiality,
        "reliability": reliability,
        "_dt": datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc),
        "_impacts": tc._decode_impacts_str(impacts),
    }


# ---------------------------------------------------------------------------
# IA-first : direction prise depuis impacts[]
# ---------------------------------------------------------------------------

def test_ia_first_long_on_brent(triggers_cfg, now_fixed):
    """Event sans cue keyword mais avec impacts IA → IA décide."""
    ev = _ev(
        "2026-05-28",
        trigger="Oil markets monitor Middle East developments closely",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:LONG:75",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # IA-first : LONG malgré l'absence du keyword "frappes/airstrikes"
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_ia_first_short_on_brent(triggers_cfg, now_fixed):
    ev = _ev(
        "2026-05-28",
        trigger="Tehran signals talks continuing, prices ease",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:SHORT:70",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_neutral_does_not_long_nor_short(triggers_cfg, now_fixed):
    """IA NEUTRAL : event reste à 0 sans tomber dans le fallback."""
    ev = _ev(
        "2026-05-28",
        trigger="Iran ceasefire holding, brent stable",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:NEUTRAL:50",
        materiality="low",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Malgré "ceasefire" dans le texte (cue SHORT), IA NEUTRAL bloque le fallback
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_ia_multi_assets_independants(triggers_cfg, now_fixed):
    """Un event escalade Iran touche BRENT + GOLD + VIX + SP500. Chaque actif
    reçoit la bonne direction depuis ses propres impacts."""
    ev = _ev(
        "2026-05-29",
        trigger="Iran airstrikes escalate, brent and gold surge",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:LONG:85;GOLD:LONG:75;VIX:LONG:70;SP500:SHORT:60",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
    assert res["or"]["tension_geopolitique"] == 1
    assert res["vix"]["tension_geopolitique_active"] == 1


# ---------------------------------------------------------------------------
# Fallback keyword : ancien schéma sans impacts
# ---------------------------------------------------------------------------

def test_fallback_keyword_on_legacy_event(triggers_cfg, now_fixed):
    """Event sans `impacts` (ancien schéma) → fallback keyword."""
    ev = _ev(
        "2026-05-28",
        trigger="frappes Iran sur Ormuz",
        cours="Brent (BZ=F)",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="",  # legacy
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Le keyword "frappes Iran" matche le LONG
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_fallback_short_keyword_legacy(triggers_cfg, now_fixed):
    ev = _ev(
        "2026-05-28",
        trigger="cessez-le-feu Iran annoncé",
        cours="Brent (BZ=F)",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_prevails_over_legacy_keyword(triggers_cfg, now_fixed):
    """Si même fenêtre : event IA LONG + event legacy SHORT keyword → IA gagne."""
    ia_ev = _ev(
        "2026-05-29",
        trigger="Iran escalation noted by traders",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:80",
        materiality="high",
    )
    legacy_ev = _ev(
        "2026-05-29",
        trigger="cessez-le-feu Iran annoncé",
        cours="Brent (BZ=F)",
        l2="Iran",
        category="geopolitical",
        impacts="",
    )
    res = tc.classify_all(events=[ia_ev, legacy_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    # ia_seen_any=True (via ia_ev) → on tranche IA-only → LONG
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


# ---------------------------------------------------------------------------
# Conflit IA LONG vs IA SHORT : matérialité puis date
# ---------------------------------------------------------------------------

def test_ia_materiality_breaks_tie(triggers_cfg, now_fixed):
    """Deux events même date : LONG materiality=high vs SHORT materiality=low
    → LONG gagne (poids matérialité)."""
    long_ev = _ev(
        "2026-05-29",
        trigger="Iran tensions",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:80",
        materiality="high",
    )
    short_ev = _ev(
        "2026-05-29",
        trigger="Iran talks",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:40",
        materiality="low",
    )
    res = tc.classify_all(events=[long_ev, short_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_ia_date_breaks_tie_when_same_materiality(triggers_cfg, now_fixed):
    """Même matérialité : date plus récente gagne."""
    old_ev = _ev(
        "2026-05-25",
        trigger="Iran escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:75",
        materiality="medium",
    )
    recent_ev = _ev(
        "2026-05-29",
        trigger="Iran ceasefire framework",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:75",
        materiality="medium",
    )
    res = tc.classify_all(events=[old_ev, recent_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    # Plus récent et même weight → SHORT gagne
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


# ---------------------------------------------------------------------------
# Rétro-compat parsing events-log
# ---------------------------------------------------------------------------

EVENTS_LOG_LEGACY_11 = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-28 |  | Iran | frappes Iran sur Ormuz | Brent (BZ=F) | intraday | 1 | bbc | Moyen-Orient | geopolitical |  |
"""

EVENTS_LOG_V2_14 = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-28 |  | Iran | Iran escalation, brent surges | BRENT | intraday | 1 | bbc | Moyen-Orient | geopolitical |  | BRENT:LONG:80;GOLD:LONG:70 | high | confirmed |
"""


def test_parse_events_log_legacy_11_cols(tmp_path):
    """Format legacy : impacts/materiality/reliability vides."""
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_LOG_LEGACY_11, encoding="utf-8")
    events = tc.parse_events_log(p)
    assert len(events) == 1
    ev = events[0]
    assert ev.get("category") == "geopolitical"
    assert ev.get("impacts", "") == ""
    assert ev.get("materiality", "") == ""
    assert ev.get("_impacts") == []


def test_parse_events_log_v2_14_cols(tmp_path):
    """Format v2 : impacts décodés, materiality/reliability remplis."""
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_LOG_V2_14, encoding="utf-8")
    events = tc.parse_events_log(p)
    assert len(events) == 1
    ev = events[0]
    assert ev.get("materiality") == "high"
    assert ev.get("reliability") == "confirmed"
    assert ev.get("impacts") == "BRENT:LONG:80;GOLD:LONG:70"
    decoded = ev.get("_impacts")
    assert len(decoded) == 2
    assert decoded[0]["asset"] == "BRENT"
    assert decoded[0]["direction"] == "LONG"
    assert decoded[0]["confidence"] == 80


def test_parse_events_log_v2_routes_correctly(tmp_path, triggers_cfg, now_fixed):
    """Bout en bout : ligne v2 parsée → classify_all → triplet correct via IA."""
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_LOG_V2_14, encoding="utf-8")
    events = tc.parse_events_log(p)
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
    assert res["or"]["tension_geopolitique"] == 1


# ---------------------------------------------------------------------------
# Décodage robuste
# ---------------------------------------------------------------------------

def test_decode_ignores_unknown_asset():
    out = tc._decode_impacts_str("DOGECOIN:LONG:90;BRENT:LONG:80")
    assert len(out) == 1
    assert out[0]["asset"] == "BRENT"


def test_decode_ignores_unknown_direction():
    out = tc._decode_impacts_str("BRENT:WHATEVER:80")
    assert out == []


def test_decode_empty_string():
    assert tc._decode_impacts_str("") == []
    assert tc._decode_impacts_str(None) == []  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Lookback respecté en mode IA
# ---------------------------------------------------------------------------

def test_ia_lookback_respecte(triggers_cfg, now_fixed):
    old_dt = (now_fixed - timedelta(days=30)).date().isoformat()
    ev = _ev(
        old_dt,
        trigger="Iran escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:80",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Hors fenêtre 7j de geopol_iran → 0
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


# ---------------------------------------------------------------------------
# Scope catégorie s'applique aussi à l'IA
# ---------------------------------------------------------------------------

def test_ia_blocked_by_category_scope(triggers_cfg, now_fixed):
    """Event impacts[BRENT:LONG] mais category=earnings → bloqué par scope geopol."""
    ev = _ev(
        "2026-05-28",
        trigger="Some random earnings note mentioning oil",
        cours="BRENT",
        l2="Earnings",
        category="earnings",  # pas geopolitical
        impacts="BRENT:LONG:80",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0
