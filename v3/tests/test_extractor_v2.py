"""Tests Extractor v2 (chantier prompt directionnel).

Couvre :
- Parsing défensif du nouveau schéma (impacts[], énums normalisées).
- Rejet des asset hors-liste (zéro invention).
- Tolérance bullish/bearish vs LONG/SHORT.
- Encode/decode impacts compact 'ASSET:DIR:CONF;...'.
- Format de ligne events-log v2 (14 colonnes).
- Rétro-compat decode (entrées vides / partielles).

Pas d'appel réseau : on teste les fonctions pures + mock du SDK.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Stub feedparser si absent en environnement de test (sandbox sans sgmllib3k).
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    fp_stub = types.ModuleType("feedparser")
    fp_stub.parse = lambda *_a, **_kw: type("R", (), {"entries": []})()  # type: ignore
    sys.modules["feedparser"] = fp_stub

import extractor as ex  # noqa: E402
import news_collector as nc  # noqa: E402


# ---------------------------------------------------------------------------
# Parsing défensif
# ---------------------------------------------------------------------------

def test_parse_impacts_valid():
    raw = [
        {"asset": "BRENT", "direction": "LONG", "confidence": 85},
        {"asset": "GOLD", "direction": "LONG", "confidence": 70},
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 2
    assert out[0].asset == "BRENT"
    assert out[0].direction == "LONG"
    assert out[0].confidence == 85


def test_parse_impacts_rejects_unknown_asset():
    """Zéro invention : asset hors-liste -> rejeté silencieusement."""
    raw = [
        {"asset": "DOGECOIN", "direction": "LONG", "confidence": 90},  # rejeté
        {"asset": "BRENT", "direction": "LONG", "confidence": 80},     # OK
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 1
    assert out[0].asset == "BRENT"


def test_parse_impacts_tolerates_bullish_bearish():
    """Rétro-compat : si DeepSeek glisse vers bullish/bearish historique."""
    raw = [
        {"asset": "BRENT", "direction": "bullish", "confidence": 80},
        {"asset": "SP500", "direction": "bearish", "confidence": 70},
        {"asset": "VIX", "direction": "neutral", "confidence": 50},
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 3
    assert out[0].direction == "LONG"
    assert out[1].direction == "SHORT"
    assert out[2].direction == "NEUTRAL"


def test_parse_impacts_confidence_high_medium_low():
    """Confidence en string énumération -> mappé numériquement."""
    raw = [
        {"asset": "BRENT", "direction": "LONG", "confidence": "high"},
        {"asset": "GOLD", "direction": "LONG", "confidence": "medium"},
        {"asset": "VIX", "direction": "LONG", "confidence": "low"},
    ]
    out = ex._parse_impacts(raw)
    assert out[0].confidence == 80
    assert out[1].confidence == 50
    assert out[2].confidence == 25


def test_parse_impacts_garbage_input():
    """Entrées corrompues : ne crash pas, retourne []."""
    assert ex._parse_impacts(None) == []
    assert ex._parse_impacts("not a list") == []
    assert ex._parse_impacts([{"asset": "BRENT"}]) == []  # pas de direction
    assert ex._parse_impacts([{"direction": "LONG"}]) == []  # pas d'asset


def test_norm_enum_strict():
    assert ex._norm_enum("LONG", {"LONG", "SHORT"}) == "LONG"
    assert ex._norm_enum("long", {"LONG", "SHORT"}) == "LONG"
    assert ex._norm_enum("INVALID", {"LONG", "SHORT"}, default="X") == "X"
    assert ex._norm_enum(None, {"LONG"}, default="") == ""


# ---------------------------------------------------------------------------
# Encode / decode impacts
# ---------------------------------------------------------------------------

def test_encode_impacts_roundtrip():
    impacts = [
        ex.Impact(asset="BRENT", direction="LONG", confidence=85),
        ex.Impact(asset="GOLD", direction="LONG", confidence=70),
        ex.Impact(asset="SP500", direction="SHORT", confidence=60),
    ]
    encoded = ex.encode_impacts(impacts)
    assert encoded == "BRENT:LONG:85;GOLD:LONG:70;SP500:SHORT:60"

    decoded = ex.decode_impacts(encoded)
    assert len(decoded) == 3
    assert decoded[0]["asset"] == "BRENT"
    assert decoded[0]["direction"] == "LONG"
    assert decoded[0]["confidence"] == 85


def test_encode_impacts_empty():
    assert ex.encode_impacts([]) == ""
    assert ex.decode_impacts("") == []
    assert ex.decode_impacts(None) == []  # type: ignore[arg-type]


def test_decode_impacts_skips_bad_entries():
    """Rétro-compat : ligne ancien schéma 'cours' classique => decode renvoie []."""
    # Format 'Brent (BZ=F)' n'est pas un encodage impacts → 0 résultats
    assert ex.decode_impacts("Brent (BZ=F)") == []
    # Mix valide + corrompu : on garde le valide
    out = ex.decode_impacts("BRENT:LONG:80;GARBAGE;GOLD:SHORT:30")
    assert len(out) == 2
    assert out[0]["asset"] == "BRENT"
    assert out[1]["asset"] == "GOLD"
    assert out[1]["direction"] == "SHORT"


def test_decode_impacts_default_confidence():
    out = ex.decode_impacts("BRENT:LONG")
    assert out == [{"asset": "BRENT", "direction": "LONG", "confidence": 0}]


# ---------------------------------------------------------------------------
# Mock du SDK : test du flow complet extract()
# ---------------------------------------------------------------------------

def _mock_response(payload: dict) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))],
        usage=SimpleNamespace(prompt_tokens=300, completion_tokens=150),
    )


def test_extract_full_flow(monkeypatch, tmp_path):
    """End-to-end : mock du SDK, vérifie dataclass renvoyée."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")
    monkeypatch.setattr(ex, "COST_LEDGER_PATH", tmp_path / "cost-ledger.json")

    # On instancie avec un client mock
    e = ex.Extractor.__new__(ex.Extractor)
    e.client = MagicMock()
    e.client.chat.completions.create.return_value = _mock_response({
        "category": "geopolitical",
        "subcat": "Iran-Moyen-Orient",
        "trigger": "Frappes iraniennes",
        "news_zone": "Moyen-Orient",
        "latence": "intraday",
        "reliability": "confirmed",
        "materiality": "high",
        "already_priced": False,
        "impacts": [
            {"asset": "BRENT", "direction": "LONG", "confidence": 85},
            {"asset": "GOLD", "direction": "LONG", "confidence": 70},
        ],
    })
    e.model = "deepseek-chat"
    e.total_calls = 0
    e.total_tokens_in = 0
    e.total_tokens_out = 0
    e.total_errors = 0
    e.hard_capped = False
    e.ledger = {}
    e.day_key = "2026-05-29"
    e.day_cost_usd = 0.0

    out = e.extract("Iran retaliates", "Tehran launched drones")
    assert out.error == ""
    assert out.category == "geopolitical"
    assert out.materiality == "high"
    assert out.reliability == "confirmed"
    assert len(out.impacts) == 2
    assert out.impacts[0].asset == "BRENT"
    assert out.impacts[0].direction == "LONG"


def test_extract_normalizes_bad_enums(monkeypatch, tmp_path):
    """Si DeepSeek renvoie une catégorie hors-énum → default 'other'."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-key")
    monkeypatch.setattr(ex, "COST_LEDGER_PATH", tmp_path / "cost-ledger.json")

    e = ex.Extractor.__new__(ex.Extractor)
    e.client = MagicMock()
    e.client.chat.completions.create.return_value = _mock_response({
        "category": "INVENTED_CATEGORY",
        "materiality": "ULTRA_HIGH",
        "reliability": "MAYBE",
        "impacts": [],
    })
    e.model = "deepseek-chat"
    e.total_calls = e.total_tokens_in = e.total_tokens_out = e.total_errors = 0
    e.hard_capped = False
    e.ledger = {}
    e.day_key = "2026-05-29"
    e.day_cost_usd = 0.0

    out = e.extract("Random news")
    assert out.category == "other"
    assert out.materiality == "low"
    assert out.reliability == ""


# ---------------------------------------------------------------------------
# news_collector : ligne events-log v2 (14 colonnes)
# ---------------------------------------------------------------------------

def test_event_log_line_extracted_v2():
    """La ligne markdown produite par news_collector doit avoir 14 colonnes
    et encoder impacts en compact."""
    item = nc.NewsItem(
        title="Iran retaliates",
        url="https://example.com",
        source="bbc",
        published=datetime(2026, 5, 29, 10, 0, tzinfo=timezone.utc),
        summary="",
    )
    e = ex.ExtractedEvent(
        impacts=[
            ex.Impact(asset="BRENT", direction="LONG", confidence=85),
            ex.Impact(asset="GOLD", direction="LONG", confidence=70),
        ],
        category="geopolitical",
        subcat="Iran-Moyen-Orient",
        trigger="Frappes iraniennes",
        news_zone="Moyen-Orient",
        latence="intraday",
        reliability="confirmed",
        materiality="high",
    )
    line = item.as_event_log_line_extracted(e)
    # 14 colonnes (pipes externes inclus = 15 pipes)
    assert line.count("|") == 15
    assert "BRENT:LONG:85;GOLD:LONG:70" in line
    assert "geopolitical" in line
    assert "high" in line
    assert "confirmed" in line
    assert "Iran-Moyen-Orient" in line  # subcat dans L2


def test_event_log_line_raw_v2():
    """La ligne brute (sans extraction) doit avoir 14 colonnes vides."""
    item = nc.NewsItem(
        title="Some news",
        url="x",
        source="src",
        published=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    line = item.as_event_log_line_raw()
    assert line.count("|") == 15


# ---------------------------------------------------------------------------
# Garde-fou : extractor désactivé sans clé
# ---------------------------------------------------------------------------

def test_extractor_disabled_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    e = ex.Extractor()
    assert e.client is None
    out = e.extract("Some news")
    assert "disabled" in out.error or "hard-capped" in out.error
