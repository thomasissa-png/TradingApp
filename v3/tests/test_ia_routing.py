"""Tests routage IA-first dans triggers_classifier (prompt v2.1).

Couvre :
- IA-first : un event avec impacts[BRENT:LONG] prime sur le keyword matching.
- IA NEUTRAL (rétro-compat ancien schéma) ne bloque PAS le fallback keyword :
  un actif marqué NEUTRAL = "pas de signal IA" → les keywords du même event
  peuvent matcher (fix bug v2 → v2.1).
- IA sans impact pour cet actif → fallback keyword non bloqué.
- Fallback keyword : événement SANS impacts (ancien schéma) → matching texte.
- Cohabitation : un event IA récent + un event keyword plus ancien → IA gagne.
- Conflit LONG/SHORT IA : matérialité d'abord, date ensuite.
- Rétro-compat events-log : parser supporte 11 ET 14 colonnes.
- Asset hors-énum dans encoded impacts → ignoré.
- Confidence bucket (v2.1) ET legacy entier (v2.0) supportés au décodage.
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
        impacts="BRENT:LONG:high",
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
        impacts="BRENT:SHORT:medium",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_neutral_legacy_does_not_block_fallback_keyword(triggers_cfg, now_fixed):
    """FIX v2.1 — bug NEUTRAL : un event IA NEUTRAL (rétro-compat ancien schéma)
    ne doit PAS empêcher le fallback keyword de s'activer sur le même event.

    Ici : trigger contient "Iran ceasefire" (keyword SHORT du pétrole), IA legacy
    a marqué NEUTRAL. En v2.0 (bug) : 0 (NEUTRAL bloquait). En v2.1 (fix) : -1.
    """
    ev = _ev(
        "2026-05-28",
        trigger="Iran ceasefire holding, brent stable",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:NEUTRAL:medium",
        materiality="low",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # FIX : le keyword "Iran ceasefire" doit pouvoir trancher → SHORT (-1)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_impact_absent_does_not_block_fallback(triggers_cfg, now_fixed):
    """FIX v2.1 — un event IA dont impacts[] ne mentionne PAS l'actif visé
    (ici BRENT absent) ne doit pas bloquer le fallback keyword pour le pétrole.

    Le scope catégorie reste vérifié, donc l'event doit rester candidat via le
    `cours` ou via les domain_hints. Ici on s'appuie sur le cours=BRENT pour
    rester candidat tout en n'ayant aucun impact IA sur BRENT.
    """
    ev = _ev(
        "2026-05-28",
        trigger="frappes Iran sur infrastructure pétrolière",  # keyword LONG
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        # Impact uniquement sur l'OR, pas sur BRENT — le pétrole doit pouvoir
        # tomber sur le fallback keyword.
        impacts="GOLD:LONG:high",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Fallback keyword "frappes Iran" → LONG pétrole
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
    # En passant, l'or reste piloté par l'IA
    assert res["or"]["tension_geopolitique"] == 1


def test_ia_multi_assets_independants(triggers_cfg, now_fixed):
    """Un event escalade Iran touche BRENT + GOLD + VIX + SP500. Chaque actif
    reçoit la bonne direction depuis ses propres impacts."""
    ev = _ev(
        "2026-05-29",
        trigger="Iran airstrikes escalate, brent and gold surge",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:LONG:high;GOLD:LONG:high;VIX:LONG:medium;SP500:SHORT:medium",
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
        impacts="BRENT:LONG:high",
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
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    short_ev = _ev(
        "2026-05-29",
        trigger="Iran talks",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:medium",
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
        impacts="BRENT:LONG:medium",
        materiality="medium",
    )
    recent_ev = _ev(
        "2026-05-29",
        trigger="Iran ceasefire framework",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:medium",
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
| 2026-05-28 |  | Iran | Iran escalation, brent surges | BRENT |  | 1 | bbc | Moyen-Orient | geopolitical |  | BRENT:LONG:high;GOLD:LONG:high | high | confirmed |
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
    assert ev.get("impacts") == "BRENT:LONG:high;GOLD:LONG:high"
    decoded = ev.get("_impacts")
    assert len(decoded) == 2
    assert decoded[0]["asset"] == "BRENT"
    assert decoded[0]["direction"] == "LONG"
    assert decoded[0]["confidence"] == "high"


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
    out = tc._decode_impacts_str("DOGECOIN:LONG:high;BRENT:LONG:high")
    assert len(out) == 1
    assert out[0]["asset"] == "BRENT"


def test_decode_ignores_unknown_direction():
    out = tc._decode_impacts_str("BRENT:WHATEVER:high")
    assert out == []


def test_decode_empty_string():
    assert tc._decode_impacts_str("") == []
    assert tc._decode_impacts_str(None) == []  # type: ignore[arg-type]


def test_decode_legacy_integer_confidence():
    """Rétro-compat : ancien schéma 'BRENT:LONG:85' → bucket 'high'."""
    out = tc._decode_impacts_str("BRENT:LONG:85;GOLD:LONG:50;VIX:LONG:10")
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"
    assert out[2]["confidence"] == "low"


def test_decode_bucket_confidence():
    """v2.1 : confidence directement en bucket."""
    out = tc._decode_impacts_str("BRENT:LONG:high;GOLD:LONG:medium;VIX:LONG:low")
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"
    assert out[2]["confidence"] == "low"


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
        impacts="BRENT:LONG:high",
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
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0
