"""Tests d'INTÉGRATION sur le chemin réel (pas seulement des mocks).

Ces tests existent parce que la suite mockée a laissé passer 2 bugs réels :
  - crash date/datetime dans classify_all,
  - regex catastrophique qui faisait freezer le briefing sur les vraies lignes.
On exerce donc : le parsing du vrai events-log, des perfs (pas de hang),
le routing avec date ET datetime, et la spécificité du GATE par actif.
"""
import sys
import time
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402
import briefing as bf  # noqa: E402
import criteres_calculator as cc  # noqa: E402


@pytest.fixture(autouse=True)
def _neutralise_gate_calendrier(monkeypatch):
    """Les tests de gate isolent le path NEWS/EIA. Le gate calendrier déterministe
    (FOMC J-1/J0, asset-aware) dépend de `datetime.now()` → on le neutralise ici
    pour que ces tests restent déterministes même la veille d'un vrai FOMC. Sa
    logique propre est couverte par test_sources_gratuites_lot."""
    monkeypatch.setattr(cc, "_fomc_imminent_deterministe", lambda now, fiche_key: False)


# --- Garde-fou perf : aucun hang sur le vrai events-log -------------------

def test_parse_real_eventslog_is_fast():
    """parse_events_log sur le vrai fichier doit être quasi instantané."""
    t = time.time()
    events = tc.parse_events_log()
    dt = time.time() - t
    assert dt < 8.0, f"parse_events_log trop lent ({dt:.1f}s) — regex/boucle pathologique ?"
    assert isinstance(events, list)


def test_briefing_on_real_eventslog_is_fast():
    """build_briefing sur le vrai events-log : pas de hang (bug regex catastrophique)."""
    t = time.time()
    md = bf.build_briefing(today=date.today())
    dt = time.time() - t
    assert dt < 8.0, f"build_briefing trop lent ({dt:.1f}s) — regex catastrophique ?"
    # P6 — build_briefing produit désormais le « Décor du jour » (intro), plus
    # le bloc « Briefing du jour » per-actif (déplacé vers build_news_par_actif).
    assert "Décor du jour" in md


def test_long_malformed_line_does_not_hang(tmp_path):
    """Une ligne ~350 chars mal formée (mauvais nb de |) ne doit pas freezer le parser."""
    bad = "| " + " ".join(["motmotmot"] * 40) + " | a | b |"  # ~360 chars, 3 colonnes
    f = tmp_path / "events-log.md"
    f.write_text(bad + "\n", encoding="utf-8")
    t = time.time()
    bf.parse_events(f)        # parser briefing (ex-regex catastrophique)
    tc.parse_events_log(f)    # parser triggers
    assert time.time() - t < 2.0, "parsing d'une ligne longue mal formée a freezé"


# --- Régression date/datetime --------------------------------------------

@pytest.mark.parametrize("today", [
    date(2026, 5, 30),
    datetime(2026, 5, 30, 9, 0, tzinfo=timezone.utc),
    datetime(2026, 5, 30, 9, 0),  # naïf
])
def test_classify_accepts_date_and_datetime(today):
    """classify_all doit accepter un date OU un datetime (le bug corrigé)."""
    events = tc.parse_events_log()
    cfg = tc.load_triggers_config()
    res = tc.classify_all(events, today, cfg)
    assert isinstance(res, dict)  # ne lève pas


# --- GATE spécifique par actif -------------------------------------------

def _ev(text, hours_ago=2, materiality="", impacts=None):
    now = datetime.now(timezone.utc)
    return {
        "_dt": now - timedelta(hours=hours_ago),
        "trigger": text, "l1": "", "l2": "", "source": "", "news_zone": "",
        "category": "macro", "materiality": materiality, "_impacts": impacts or [],
    }


def test_gate_is_asset_specific_not_global():
    """Un event FOMC générique ne doit PAS allumer le gate de tous les actifs."""
    now = datetime.now(timezone.utc)
    events = [_ev("Fed FOMC decision expected, rate hold likely")]
    # sp500 a 'fomc' dans ses mots-clés gate -> True
    assert cc._resolve_gate("sp500", "gate_x", now, events) is True
    # cacao n'a rien à voir avec un FOMC -> False (avant le fix : True pour tous)
    assert cc._resolve_gate("cacao", "gate_x", now, events) is False
    assert cc._resolve_gate("cafe", "gate_x", now, events) is False


def test_gate_high_materiality_impact_fires_only_target():
    """Un event high-materiality ciblant BRENT allume le gate pétrole, pas le café."""
    now = datetime.now(timezone.utc)
    events = [_ev("Iran strikes tankers in Hormuz", materiality="high",
                  impacts=[{"asset": "BRENT", "direction": "LONG", "confidence": 90}])]
    assert cc._resolve_gate("petrole", "gate_x", now, events) is True
    assert cc._resolve_gate("cafe", "gate_x", now, events) is False


def test_gate_old_event_does_not_fire():
    """Un event trop vieux (> 24h) n'allume pas le gate."""
    now = datetime.now(timezone.utc)
    events = [_ev("Fed FOMC decision", hours_ago=72)]
    assert cc._resolve_gate("sp500", "gate_x", now, events) is False
