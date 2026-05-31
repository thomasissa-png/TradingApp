"""Tests synthese_directionnelle.py + branchement triggers_classifier.

100% mocké (HTTP/LLM) — aucun appel réseau réel.

Couvre :
- synthèse LONG conviction high → triplet = +1 (source_track="ia_synthese")
- conviction low → triplet = 0 (source_track="ia_synthese_faible", niveau 2)
- direction NEUTRAL → triplet = 0 (niveau 2 : le prix tranchera)
- extractor None → fallback complet sur ancienne logique (rétro-compat)
- extractor désactivé (is_enabled() False) → fallback
- parsing défensif : JSON invalide, énum hors-bornes → conviction "low"
- _format_events_for_prompt : sérialisation lisible des events
- _group_events_by_asset : multi-impacts, fenêtre lookback, dédup
- synthesize_all : multi-actifs, dégradation gracieuse
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import synthese_directionnelle as sd  # noqa: E402
import triggers_classifier as tc  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers : fake Extractor + fake LLM response
# ---------------------------------------------------------------------------

def _fake_response(payload: dict, tokens_in: int = 100, tokens_out: int = 40):
    """Construit une réponse OpenAI-like avec .choices[0].message.content + .usage."""
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))],
        usage=SimpleNamespace(prompt_tokens=tokens_in, completion_tokens=tokens_out),
    )


def _make_fake_extractor(response_payload: dict | None = None, raise_exc: Exception | None = None,
                        enabled: bool = True, raw_content: str | None = None):
    """Construit un Extractor mock contrôlable.

    - response_payload : dict retourné par DeepSeek (sérialisé JSON).
    - raise_exc : si défini, l'appel client.chat.completions.create lève cette exception.
    - enabled : valeur de is_enabled().
    - raw_content : si défini, on renvoie ce contenu brut (pour tester parsing défensif).
    """
    ext = MagicMock()
    ext.is_enabled = MagicMock(return_value=enabled)
    ext.model = "deepseek-chat"
    ext._update_cost = MagicMock()  # capté → vérif appel

    if not enabled:
        ext.client = None
        return ext

    client = MagicMock()
    create = MagicMock()
    if raise_exc is not None:
        create.side_effect = raise_exc
    elif raw_content is not None:
        create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=raw_content))],
            usage=SimpleNamespace(prompt_tokens=50, completion_tokens=10),
        )
    else:
        create.return_value = _fake_response(response_payload or {})
    client.chat.completions.create = create
    ext.client = client
    return ext


def _make_event(date_str: str, trigger: str, impacts: list[dict],
                materiality: str = "medium", reliability: str = "reported") -> dict:
    dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    return {
        "date": date_str,
        "trigger": trigger,
        "l1": "", "l2": "", "cours": "", "source": "test", "news_zone": "Global",
        "category": "geopolitical",
        "materiality": materiality,
        "reliability": reliability,
        "_dt": dt,
        "_impacts": impacts,
    }


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def triggers_cfg():
    return tc.load_triggers_config()


# ---------------------------------------------------------------------------
# 1. synthesize_asset — chemins nominaux
# ---------------------------------------------------------------------------

def test_synthesize_asset_long_high():
    ext = _make_fake_extractor({
        "direction": "LONG", "conviction": "high",
        "rationale": "OPEC cut + Ormuz dominent",
    })
    events = [_make_event("2026-05-28", "OPEC cut", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])]
    res = sd.synthesize_asset("BRENT", events, ext)
    assert res == {"direction": "LONG", "conviction": "high", "rationale": "OPEC cut + Ormuz dominent"}
    # Le cost-ledger a été mis à jour
    ext._update_cost.assert_called_once_with(100, 40)


def test_synthesize_asset_short_medium():
    ext = _make_fake_extractor({"direction": "SHORT", "conviction": "medium", "rationale": "demand-side weak"})
    events = [_make_event("2026-05-27", "demand weak", [{"asset": "BRENT", "direction": "SHORT", "confidence": "medium"}])]
    res = sd.synthesize_asset("BRENT", events, ext)
    assert res["direction"] == "SHORT"
    assert res["conviction"] == "medium"


def test_synthesize_asset_neutral_low():
    ext = _make_fake_extractor({"direction": "NEUTRAL", "conviction": "low", "rationale": "signaux contradictoires"})
    events = [_make_event("2026-05-28", "mixed", [{"asset": "GOLD", "direction": "LONG", "confidence": "low"}])]
    res = sd.synthesize_asset("GOLD", events, ext)
    assert res["direction"] == "NEUTRAL"
    assert res["conviction"] == "low"


# ---------------------------------------------------------------------------
# 2. synthesize_asset — dégradation gracieuse
# ---------------------------------------------------------------------------

def test_synthesize_asset_no_extractor():
    events = [_make_event("2026-05-28", "x", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])]
    assert sd.synthesize_asset("BRENT", events, None) is None


def test_synthesize_asset_extractor_disabled():
    ext = _make_fake_extractor(enabled=False)
    events = [_make_event("2026-05-28", "x", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])]
    assert sd.synthesize_asset("BRENT", events, ext) is None


def test_synthesize_asset_no_events():
    ext = _make_fake_extractor({"direction": "NEUTRAL", "conviction": "low", "rationale": "x"})
    res = sd.synthesize_asset("BRENT", [], ext)
    # Pas de news → NEUTRAL/low sans appel LLM
    assert res == {"direction": "NEUTRAL", "conviction": "low", "rationale": "aucune news exploitable"}
    ext.client.chat.completions.create.assert_not_called()


def test_synthesize_asset_llm_exception():
    ext = _make_fake_extractor(raise_exc=RuntimeError("API down"))
    events = [_make_event("2026-05-28", "x", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])]
    assert sd.synthesize_asset("BRENT", events, ext) is None


# ---------------------------------------------------------------------------
# 3. Parsing défensif
# ---------------------------------------------------------------------------

def test_parse_response_invalid_json():
    assert sd._parse_response("pas du json {") is None
    assert sd._parse_response("") is None
    assert sd._parse_response(None) is None  # type: ignore[arg-type]


def test_parse_response_enum_out_of_range():
    # Direction hors énum → NEUTRAL ; conviction hors énum → "low"
    res = sd._parse_response(json.dumps({"direction": "UP", "conviction": "very-high", "rationale": "x"}))
    assert res == {"direction": "NEUTRAL", "conviction": "low", "rationale": "x"}


def test_parse_response_bullish_bearish_tolerance():
    res = sd._parse_response(json.dumps({"direction": "bullish", "conviction": "high", "rationale": ""}))
    assert res["direction"] == "LONG"
    res = sd._parse_response(json.dumps({"direction": "BEARISH", "conviction": "medium", "rationale": ""}))
    assert res["direction"] == "SHORT"


def test_synthesize_asset_invalid_json_from_llm():
    ext = _make_fake_extractor(raw_content="not json at all")
    events = [_make_event("2026-05-28", "x", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])]
    assert sd.synthesize_asset("BRENT", events, ext) is None


# ---------------------------------------------------------------------------
# 4. Format prompt
# ---------------------------------------------------------------------------

def test_format_events_for_prompt_contains_asset_and_dates():
    events = [
        _make_event("2026-05-28", "OPEC cut", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}], materiality="high"),
        _make_event("2026-05-25", "demand weak", [{"asset": "BRENT", "direction": "SHORT", "confidence": "medium"}], materiality="medium"),
    ]
    txt = sd._format_events_for_prompt("BRENT", events)
    assert "ACTIF : BRENT" in txt
    assert "2026-05-28" in txt
    assert "OPEC cut" in txt
    assert "LONG (conf=high)" in txt
    assert "SHORT (conf=medium)" in txt
    assert "mat=high" in txt


def test_format_events_for_prompt_truncates_long_list():
    events = [
        _make_event(f"2026-05-{(i % 28) + 1:02d}", f"news {i}",
                    [{"asset": "BRENT", "direction": "LONG", "confidence": "low"}])
        for i in range(50)
    ]
    txt = sd._format_events_for_prompt("BRENT", events)
    # Cap à MAX_EVENTS_PER_ASSET = 30
    assert txt.count("- 2026-") <= sd.MAX_EVENTS_PER_ASSET


# ---------------------------------------------------------------------------
# 5. synthesize_all — multi-actifs
# ---------------------------------------------------------------------------

def test_synthesize_all_multi_assets():
    ext = _make_fake_extractor({"direction": "LONG", "conviction": "high", "rationale": "x"})
    events_by_asset = {
        "BRENT": [_make_event("2026-05-28", "OPEC", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])],
        "GOLD":  [_make_event("2026-05-27", "war",  [{"asset": "GOLD",  "direction": "LONG", "confidence": "high"}])],
    }
    res = sd.synthesize_all(events_by_asset, ext)
    assert set(res.keys()) == {"BRENT", "GOLD"}
    assert res["BRENT"]["direction"] == "LONG"
    # 2 appels LLM
    assert ext.client.chat.completions.create.call_count == 2


def test_synthesize_all_no_extractor():
    events_by_asset = {"BRENT": [_make_event("2026-05-28", "x", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])]}
    assert sd.synthesize_all(events_by_asset, None) == {}


# ---------------------------------------------------------------------------
# 6. Branchement triggers_classifier — niveau 1 prime
# ---------------------------------------------------------------------------

def test_classify_uses_synthese_long_high(triggers_cfg, now_fixed):
    """Si la synthèse dit LONG high → triplet = +1, source_track = ia_synthese."""
    # Event Brent géopol (sera rattaché à petrole/geopol_iran via IA_ASSET + scope)
    events = [_make_event(
        "2026-05-28", "frappes Iran sur Ormuz",
        [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
        materiality="high",
    )]
    ext = _make_fake_extractor({
        "direction": "LONG", "conviction": "high",
        "rationale": "OPEC cut + Ormuz",
    })
    res = tc.classify_all_with_meta(
        events=events, today=now_fixed, triggers_cfg=triggers_cfg, extractor=ext,
    )
    petrole_iran = res.get("petrole", {}).get("tension_geopol_moyen_orient")
    assert petrole_iran is not None
    assert petrole_iran["valeur"] == 1
    assert petrole_iran["source_track"] == "ia_synthese"
    assert "OPEC" in petrole_iran.get("synthese_rationale", "")


def test_classify_uses_synthese_short_medium(triggers_cfg, now_fixed):
    events = [_make_event(
        "2026-05-28", "demand weakness Brent",
        [{"asset": "BRENT", "direction": "SHORT", "confidence": "medium"}],
        materiality="medium",
    )]
    ext = _make_fake_extractor({
        "direction": "SHORT", "conviction": "medium",
        "rationale": "demand-side dominant",
    })
    res = tc.classify_all_with_meta(
        events=events, today=now_fixed, triggers_cfg=triggers_cfg, extractor=ext,
    )
    # Tous les critères Brent IA-routables sont à -1
    petrole = res.get("petrole", {})
    iran = petrole.get("tension_geopol_moyen_orient")
    assert iran is not None and iran["valeur"] == -1
    assert iran["source_track"] == "ia_synthese"


# ---------------------------------------------------------------------------
# 7. Niveau 2 : synthèse faible/neutral → critère = 0, le prix tranchera
# ---------------------------------------------------------------------------

def test_classify_synthese_low_returns_zero(triggers_cfg, now_fixed):
    """Conviction low → valeur=0, source_track=ia_synthese_faible (niveau 2)."""
    events = [_make_event(
        "2026-05-28", "mixed signals on Brent",
        [{"asset": "BRENT", "direction": "LONG", "confidence": "low"}],
    )]
    ext = _make_fake_extractor({
        "direction": "LONG", "conviction": "low",
        "rationale": "signaux faibles et dispersés",
    })
    res = tc.classify_all_with_meta(
        events=events, today=now_fixed, triggers_cfg=triggers_cfg, extractor=ext,
    )
    iran = res.get("petrole", {}).get("tension_geopol_moyen_orient")
    assert iran is not None
    assert iran["valeur"] == 0
    assert iran["source_track"] == "ia_synthese_faible"


def test_classify_synthese_neutral_returns_zero(triggers_cfg, now_fixed):
    events = [_make_event(
        "2026-05-28", "contradictory news",
        [{"asset": "BRENT", "direction": "LONG", "confidence": "medium"}],
    )]
    ext = _make_fake_extractor({
        "direction": "NEUTRAL", "conviction": "medium",
        "rationale": "16 long vs 8 short, pas de signal dominant",
    })
    res = tc.classify_all_with_meta(
        events=events, today=now_fixed, triggers_cfg=triggers_cfg, extractor=ext,
    )
    iran = res.get("petrole", {}).get("tension_geopol_moyen_orient")
    assert iran is not None
    assert iran["valeur"] == 0
    assert iran["source_track"] == "ia_synthese_faible"


# ---------------------------------------------------------------------------
# 8. Pas d'extractor → fallback complet (rétro-compat)
# ---------------------------------------------------------------------------

def test_classify_no_extractor_keeps_legacy_behavior(triggers_cfg, now_fixed):
    """Sans extractor, on retombe sur l'ancienne logique IA-first + keyword."""
    events = [_make_event(
        "2026-05-28", "frappes Iran sur Ormuz",
        [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
    )]
    res = tc.classify_all_with_meta(
        events=events, today=now_fixed, triggers_cfg=triggers_cfg, extractor=None,
    )
    iran = res.get("petrole", {}).get("tension_geopol_moyen_orient")
    assert iran is not None
    assert iran["valeur"] == 1
    # Source track = "ia" (impact direct), PAS "ia_synthese"
    assert iran["source_track"] == "ia"


def test_classify_extractor_disabled_falls_back(triggers_cfg, now_fixed):
    events = [_make_event(
        "2026-05-28", "frappes Iran sur Ormuz",
        [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
    )]
    ext = _make_fake_extractor(enabled=False)
    res = tc.classify_all_with_meta(
        events=events, today=now_fixed, triggers_cfg=triggers_cfg, extractor=ext,
    )
    iran = res.get("petrole", {}).get("tension_geopol_moyen_orient")
    # Fallback IA direct
    assert iran["valeur"] == 1
    assert iran["source_track"] == "ia"


# ---------------------------------------------------------------------------
# 9. _group_events_by_asset
# ---------------------------------------------------------------------------

def test_group_events_by_asset_multi_impacts(now_fixed):
    # Un event multi-actifs apparaît dans 2 buckets
    ev = _make_event("2026-05-28", "escalation", [
        {"asset": "BRENT", "direction": "LONG", "confidence": "high"},
        {"asset": "GOLD", "direction": "LONG", "confidence": "high"},
    ])
    grouped = tc._group_events_by_asset([ev], now_fixed, lookback_days=14)
    assert set(grouped.keys()) == {"BRENT", "GOLD"}
    assert len(grouped["BRENT"]) == 1
    assert len(grouped["GOLD"]) == 1


def test_group_events_by_asset_lookback_filter(now_fixed):
    old_ev = _make_event("2026-04-01", "old", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])
    new_ev = _make_event("2026-05-28", "new", [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}])
    grouped = tc._group_events_by_asset([old_ev, new_ev], now_fixed, lookback_days=7)
    assert len(grouped["BRENT"]) == 1
    assert grouped["BRENT"][0]["trigger"] == "new"


def test_group_events_by_asset_ignores_neutral(now_fixed):
    # NEUTRAL ou direction inconnue → ignoré
    ev = _make_event("2026-05-28", "x", [{"asset": "BRENT", "direction": "NEUTRAL", "confidence": "high"}])
    grouped = tc._group_events_by_asset([ev], now_fixed, lookback_days=14)
    assert grouped == {}
