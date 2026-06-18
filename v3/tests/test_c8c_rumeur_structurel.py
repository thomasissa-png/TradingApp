"""Tests C8c — détecteur « rumeur / non-confirmé » sur news structurelle.

Reco Newstrader n°2 : une news classée `nature == "structurel"` mais en réalité
non confirmée (reliability rumor/reported, OU marqueur de rumeur dans le texte)
DEVRAIT être rétrogradée en `verbal` (coef 0.3/0.2/0.1, s'éteint vite) au lieu
de tenir jusqu'à 1m (coef structurel 0.8/1.0/1.0).

MODE SHADOW STRICT (comme is_denial / already_priced) :
- Le flag `nature_shadow_downgrade` NE change PAS la nature, le coef, le score
  ni la conclusion. Pur ajout observationnel pour mesure.
- Verrou test « conclusions inchangées ».

Cas couverts :
- structurel + rumor → flag downgrade=True
- structurel + reported → flag downgrade=True
- structurel + confirmed (sans marqueur) → PAS de downgrade
- structurel + confirmed + marqueur texte → downgrade=True (texte fait foi)
- ponctuel / verbal → JAMAIS de downgrade (règle ne vise que structurel)
- le flag NE change PAS la note (verrou shadow)
- marqueurs de rumeur détectés (FR + EN, word-bounded, multi-token)
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import triggers_classifier as tc  # noqa: E402
import scoring_analyste as sa  # noqa: E402


def _ev(nature="structurel", reliability="confirmed", trigger="Accord commercial signé"):
    """Forge un event minimal (les clés lues par detect_rumor_downgrade)."""
    return {
        "nature": nature,
        "reliability": reliability,
        "trigger": trigger,
        "l2": "",
        "l1": "",
        "source": "",
        "news_zone": "",
    }


# ---------------------------------------------------------------------------
# Constantes documentées
# ---------------------------------------------------------------------------

def test_constants_documented():
    assert tc.RUMOR_NATURE_TARGET == "structurel"
    assert tc.RUMOR_NATURE_PROPOSED == "verbal"
    # La nature proposée existe bien dans COEF_NATURE et est « plus faible »
    # que structurel sur 7j/1m (l'objectif de la rétrogradation).
    struct = tc.COEF_NATURE["structurel"]
    verbal = tc.COEF_NATURE["verbal"]
    assert verbal["7j"] < struct["7j"]
    assert verbal["1m"] < struct["1m"]
    assert tc.RUMOR_UNCONFIRMED_RELIABILITY == {"rumor", "reported"}


# ---------------------------------------------------------------------------
# Règle reliability sur structurel
# ---------------------------------------------------------------------------

def test_structurel_rumor_downgrades():
    """structurel + reliability=rumor → downgrade=True (reason reliability)."""
    dg, reason = tc.detect_rumor_downgrade(_ev(reliability="rumor"))
    assert dg is True
    assert "reliability:rumor" in reason


def test_structurel_reported_downgrades():
    """structurel + reliability=reported → downgrade=True."""
    dg, reason = tc.detect_rumor_downgrade(_ev(reliability="reported"))
    assert dg is True
    assert "reliability:reported" in reason


def test_structurel_confirmed_no_downgrade():
    """structurel + confirmed + texte neutre → PAS de downgrade (verrou faux+)."""
    dg, reason = tc.detect_rumor_downgrade(
        _ev(reliability="confirmed", trigger="Accord commercial signé officiellement")
    )
    assert dg is False
    assert reason == ""


# ---------------------------------------------------------------------------
# Règle marqueurs texte (le texte fait foi même si reliability=confirmed)
# ---------------------------------------------------------------------------

def test_structurel_confirmed_but_rumor_keyword_downgrades():
    """structurel + confirmed MAIS texte « in talks » → downgrade=True."""
    dg, reason = tc.detect_rumor_downgrade(
        _ev(reliability="confirmed", trigger="US and Iran reportedly in talks for ceasefire")
    )
    assert dg is True
    assert "keyword:" in reason


def test_marker_fr_pourparlers():
    dg, reason = tc.detect_rumor_downgrade(
        _ev(reliability="confirmed", trigger="Les deux pays seraient en pourparlers")
    )
    assert dg is True
    assert "keyword:en pourparlers" in reason


def test_marker_en_could():
    dg, _ = tc.detect_rumor_downgrade(
        _ev(reliability="confirmed", trigger="OPEC could cut output next month")
    )
    assert dg is True


def test_marker_fr_pourrait():
    dg, _ = tc.detect_rumor_downgrade(
        _ev(reliability="confirmed", trigger="La Fed pourrait baisser ses taux")
    )
    assert dg is True


def test_marker_word_boundary_no_false_positive():
    """« maybe » ne doit PAS matcher le marqueur « may » (token distinct)."""
    dg, _ = tc.detect_rumor_downgrade(
        _ev(reliability="confirmed", trigger="Maybe Industries signs deal")
    )
    assert dg is False


# ---------------------------------------------------------------------------
# La règle ne vise QUE structurel
# ---------------------------------------------------------------------------

def test_ponctuel_never_downgrades():
    """ponctuel + rumor → PAS de downgrade (la règle ne vise que structurel)."""
    dg, _ = tc.detect_rumor_downgrade(_ev(nature="ponctuel", reliability="rumor"))
    assert dg is False


def test_verbal_never_downgrades():
    """verbal est déjà la cible — rien à rétrograder."""
    dg, _ = tc.detect_rumor_downgrade(
        _ev(nature="verbal", reliability="rumor", trigger="rumeur de hausse")
    )
    assert dg is False


def test_deja_cote_never_downgrades():
    dg, _ = tc.detect_rumor_downgrade(_ev(nature="deja_cote", reliability="rumor"))
    assert dg is False


# ---------------------------------------------------------------------------
# Propagation : parse_events_log pose le flag SANS muter la nature
# ---------------------------------------------------------------------------

def test_parse_events_log_marks_flag_without_mutating_nature(tmp_path):
    """parse_events_log pose nature_shadow_downgrade=True + nature_proposee
    mais NE change PAS ev['nature'] (reste 'structurel')."""
    log = tmp_path / "events-log.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = ("| date | l1 | l2 | trigger | cours | latence | r | source | "
              "news_zone | category | pattern_id | impacts | materiality | "
              "reliability | event_id | event_date | nature | dedup_status | stale |\n")
    sep = "|" + "---|" * 19 + "\n"
    # 1 structurel+reported (downgrade) ; 1 structurel+confirmed neutre (non)
    row_dg = (f"| {today} |  | Iran | US and Iran reportedly in talks for a peace deal "
              f"| BRENT |  | 1 | bbc | ME | geopolitical |  | BRENT:SHORT:high | high "
              f"| reported | aaa111 | {today} | structurel |  |  |\n")
    row_ok = (f"| {today} |  | Tech | Nvidia signe un contrat ferme avec Dell "
              f"| NASDAQ |  | 1 | cnbc | US | earnings |  | NASDAQ:LONG:high | high "
              f"| confirmed | bbb222 | {today} | structurel |  |  |\n")
    log.write_text(header + sep + row_dg + row_ok, encoding="utf-8")

    events = tc.parse_events_log(log)
    assert len(events) == 2
    by_trig = {e["trigger"]: e for e in events}
    dg_ev = [e for e in events if e.get("nature_shadow_downgrade")]
    assert len(dg_ev) == 1
    flagged = dg_ev[0]
    # SHADOW STRICT : la nature réelle n'est PAS modifiée.
    assert flagged["nature"] == "structurel"
    assert flagged["nature_proposee"] == "verbal"
    assert "reliability:reported" in flagged["rumor_reason"]
    # L'event confirmé neutre n'est PAS flaggé.
    ok_ev = [e for e in events if not e.get("nature_shadow_downgrade")]
    assert len(ok_ev) == 1
    assert ok_ev[0]["nature"] == "structurel"


# ---------------------------------------------------------------------------
# VERROU SHADOW : le flag NE change PAS la note (decision-log)
# ---------------------------------------------------------------------------

def _make_actif_with_rumor_flag(
    *, nature_shadow_downgrade: bool, conclusion: str = "LONG",
) -> sa.ActifResult:
    crit = sa.CritereResult(
        id="news_test",
        nom="news_test",
        type_norm="signal_directionnel",
        valeur_brute={"valeur": 1},
        valeur_norm=1.0,
        poids=5.0,
        signe=1,
        pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0},
        note="",
        contributions={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        contributions_pond={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        materiality="high",
        reliability="reported",
        source_track="ia",
        cle_courante="news_test",
        nature="structurel",
        event_id="ABC123",
        event_date=datetime.now(timezone.utc).isoformat(),
        event_date_source="rss",
        freshness_days=0.5,
        nature_shadow_downgrade=nature_shadow_downgrade,
        nature_proposee="verbal" if nature_shadow_downgrade else "",
        rumor_reason="reliability:reported" if nature_shadow_downgrade else "",
    )
    return sa.ActifResult(
        nom="TestActif",
        fiche_key="test",
        criteres=[crit],
        scores={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        conclusions={"24h": conclusion, "7j": conclusion, "1m": conclusion},
        tie_break_notes={},
        scores_pond={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        conclusions_pond={"24h": conclusion, "7j": conclusion, "1m": conclusion},
        tie_break_notes_pond={},
        diverge={},
        news_cap_info={
            "24h": {"news_total_pm1": 5.0, "quant_total_pm1": 0.0},
            "7j":  {"news_total_pm1": 5.0, "quant_total_pm1": 0.0},
            "1m":  {"news_total_pm1": 5.0, "quant_total_pm1": 0.0},
        },
        coverage=1.0,
        confidence={"24h": "normale", "7j": "normale", "1m": "normale"},
    )


def test_decision_log_emits_flag_only_when_true():
    """nature_shadow_downgrade=True → champ tracé ; False → champ ABSENT."""
    now = datetime.now(timezone.utc)

    actif_dg = _make_actif_with_rumor_flag(nature_shadow_downgrade=True)
    for r in sa.build_decision_log_records([actif_dg], now):
        crit = r["criteres"][0]
        assert crit.get("nature_shadow_downgrade") is True
        assert crit.get("nature_proposee") == "verbal"
        assert crit.get("rumor_reason")

    actif_ok = _make_actif_with_rumor_flag(nature_shadow_downgrade=False)
    for r in sa.build_decision_log_records([actif_ok], now):
        crit = r["criteres"][0]
        assert "nature_shadow_downgrade" not in crit  # zéro bruit
        assert "nature_proposee" not in crit


def test_conclusions_unchanged_when_rumor_flag():
    """VERROU SHADOW : un flag rumeur NE doit PAS inverser/modifier la note."""
    actif = _make_actif_with_rumor_flag(nature_shadow_downgrade=True, conclusion="LONG")
    records = sa.build_decision_log_records([actif], datetime.now(timezone.utc))
    for r in records:
        assert r["conclusion_pm1"] == "LONG"
        assert r["score_pm1"] == 5.0
        assert r["criteres"][0].get("nature_shadow_downgrade") is True
