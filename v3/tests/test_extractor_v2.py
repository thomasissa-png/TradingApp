"""Tests Extractor v2.1 (prompt directionnel nettoyé).

Couvre :
- Parsing défensif du nouveau schéma (impacts[], énums normalisées).
- Rejet des asset hors-liste (zéro invention).
- Tolérance bullish/bearish vs LONG/SHORT, REJET de NEUTRAL (impact non listé).
- Confidence en bucket {high, medium, low} avec rétro-compat entier 0-100.
- Encode/decode impacts compact 'ASSET:DIR:BUCKET;...'.
- Format de ligne events-log v2 (14 colonnes — `latence` toujours vide).
- Rétro-compat decode (entrées vides / partielles / ancien schéma numérique).

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
        {"asset": "BRENT", "direction": "LONG", "confidence": "high"},
        {"asset": "GOLD", "direction": "LONG", "confidence": "medium"},
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 2
    assert out[0].asset == "BRENT"
    assert out[0].direction == "LONG"
    assert out[0].confidence == "high"
    assert out[1].confidence == "medium"


def test_parse_impacts_rejects_unknown_asset():
    """Zéro invention : asset hors-liste -> rejeté silencieusement."""
    raw = [
        {"asset": "DOGECOIN", "direction": "LONG", "confidence": "high"},  # rejeté
        {"asset": "BRENT", "direction": "LONG", "confidence": "high"},     # OK
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 1
    assert out[0].asset == "BRENT"


def test_parse_impacts_tolerates_bullish_bearish():
    """Rétro-compat : si DeepSeek glisse vers bullish/bearish historique.

    v2.1 : 'neutral' n'est plus une direction valide → impact rejeté
    (un actif sans direction tradable ne doit pas figurer dans impacts[]).
    """
    raw = [
        {"asset": "BRENT", "direction": "bullish", "confidence": "high"},
        {"asset": "SP500", "direction": "bearish", "confidence": "medium"},
        {"asset": "VIX", "direction": "neutral", "confidence": "low"},  # rejeté
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 2
    assert out[0].direction == "LONG"
    assert out[1].direction == "SHORT"


def test_parse_impacts_rejects_neutral_direction():
    """v2.1 : NEUTRAL retiré du prompt → impact rejeté à la parse."""
    raw = [
        {"asset": "BRENT", "direction": "NEUTRAL", "confidence": "high"},
        {"asset": "GOLD", "direction": "LONG", "confidence": "high"},
    ]
    out = ex._parse_impacts(raw)
    assert len(out) == 1
    assert out[0].asset == "GOLD"


def test_parse_impacts_confidence_buckets():
    """Confidence en bucket string : renvoyée telle quelle (lowercase)."""
    raw = [
        {"asset": "BRENT", "direction": "LONG", "confidence": "high"},
        {"asset": "GOLD", "direction": "LONG", "confidence": "MEDIUM"},
        {"asset": "VIX", "direction": "LONG", "confidence": "low"},
    ]
    out = ex._parse_impacts(raw)
    assert out[0].confidence == "high"
    assert out[1].confidence == "medium"
    assert out[2].confidence == "low"


def test_parse_impacts_confidence_legacy_integer():
    """Rétro-compat : confidence entier 0-100 → mappé en bucket."""
    raw = [
        {"asset": "BRENT", "direction": "LONG", "confidence": 85},   # high
        {"asset": "GOLD", "direction": "LONG", "confidence": 50},    # medium
        {"asset": "VIX", "direction": "LONG", "confidence": 20},     # low
        {"asset": "SP500", "direction": "SHORT", "confidence": 66},  # high (borne)
        {"asset": "EURUSD", "direction": "LONG", "confidence": 33},  # medium (borne)
    ]
    out = ex._parse_impacts(raw)
    assert out[0].confidence == "high"
    assert out[1].confidence == "medium"
    assert out[2].confidence == "low"
    assert out[3].confidence == "high"
    assert out[4].confidence == "medium"


def test_parse_impacts_confidence_garbage_defaults_low():
    """Confidence inintelligible → bucket 'low' (degradation gracieuse)."""
    raw = [
        {"asset": "BRENT", "direction": "LONG", "confidence": "yolo"},
        {"asset": "GOLD", "direction": "LONG", "confidence": None},
        {"asset": "VIX", "direction": "LONG"},  # absent
    ]
    out = ex._parse_impacts(raw)
    assert all(imp.confidence == "low" for imp in out)


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
        ex.Impact(asset="BRENT", direction="LONG", confidence="high"),
        ex.Impact(asset="GOLD", direction="LONG", confidence="medium"),
        ex.Impact(asset="SP500", direction="SHORT", confidence="low"),
    ]
    encoded = ex.encode_impacts(impacts)
    assert encoded == "BRENT:LONG:high;GOLD:LONG:medium;SP500:SHORT:low"

    decoded = ex.decode_impacts(encoded)
    assert len(decoded) == 3
    assert decoded[0]["asset"] == "BRENT"
    assert decoded[0]["direction"] == "LONG"
    assert decoded[0]["confidence"] == "high"


def test_encode_impacts_empty():
    assert ex.encode_impacts([]) == ""
    assert ex.decode_impacts("") == []
    assert ex.decode_impacts(None) == []  # type: ignore[arg-type]


def test_decode_impacts_skips_bad_entries():
    """Rétro-compat : ligne ancien schéma 'cours' classique => decode renvoie []."""
    # Format 'Brent (BZ=F)' n'est pas un encodage impacts → 0 résultats
    assert ex.decode_impacts("Brent (BZ=F)") == []
    # Mix valide + corrompu : on garde le valide
    out = ex.decode_impacts("BRENT:LONG:high;GARBAGE;GOLD:SHORT:low")
    assert len(out) == 2
    assert out[0]["asset"] == "BRENT"
    assert out[1]["asset"] == "GOLD"
    assert out[1]["direction"] == "SHORT"


def test_decode_impacts_default_confidence():
    out = ex.decode_impacts("BRENT:LONG")
    assert out == [{"asset": "BRENT", "direction": "LONG", "confidence": "low"}]


def test_decode_impacts_legacy_numeric_confidence():
    """Rétro-compat décodage : entier 0-100 dans la ligne events-log v2.0."""
    out = ex.decode_impacts("BRENT:LONG:85;GOLD:LONG:50;VIX:LONG:10")
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"
    assert out[2]["confidence"] == "low"


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
        "reliability": "confirmed",
        "materiality": "high",
        "impacts": [
            {"asset": "BRENT", "direction": "LONG", "confidence": "high"},
            {"asset": "GOLD", "direction": "LONG", "confidence": "medium"},
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
    assert out.impacts[0].confidence == "high"
    # Garde-fou : les champs morts ne sont plus exposés
    assert not hasattr(out, "latence")
    assert not hasattr(out, "already_priced")


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
    """La ligne markdown produite par news_collector doit avoir 19 colonnes
    (v2.2 Phase 2 : +event_id, +event_date, +nature, +dedup_status, +stale)
    et encoder impacts en compact avec buckets confidence."""
    item = nc.NewsItem(
        title="Iran retaliates",
        url="https://example.com",
        source="bbc",
        published=datetime(2026, 5, 29, 10, 0, tzinfo=timezone.utc),
        summary="",
    )
    e = ex.ExtractedEvent(
        impacts=[
            ex.Impact(asset="BRENT", direction="LONG", confidence="high"),
            ex.Impact(asset="GOLD", direction="LONG", confidence="medium"),
        ],
        category="geopolitical",
        subcat="Iran-Moyen-Orient",
        trigger="Frappes iraniennes",
        news_zone="Moyen-Orient",
        reliability="confirmed",
        materiality="high",
        nature="structurel",
    )
    line = item.as_event_log_line_extracted(e)
    # 19 colonnes (pipes externes inclus = 20 pipes) — v2.2 Phase 2
    assert line.count("|") == 20
    assert "BRENT:LONG:high;GOLD:LONG:medium" in line
    assert "geopolitical" in line
    assert "confirmed" in line
    assert "Iran-Moyen-Orient" in line  # subcat dans L2
    assert "structurel" in line  # nature présente
    # Colonne latence présente mais vide (pos 6 dans la ligne)
    parts = [p.strip() for p in line.strip("|").split("|")]
    assert len(parts) == 19
    assert parts[5] == ""  # latence vide
    # event_id (pos 14) : 12 hex
    assert len(parts[14]) == 12


def test_event_log_line_raw_v2():
    """La ligne brute (sans extraction) doit avoir 19 colonnes v2.2."""
    item = nc.NewsItem(
        title="Some news",
        url="x",
        source="src",
        published=datetime(2026, 5, 29, tzinfo=timezone.utc),
    )
    line = item.as_event_log_line_raw()
    # 19 colonnes (20 pipes externes inclus)
    assert line.count("|") == 20
    parts = [p.strip() for p in line.strip("|").split("|")]
    assert len(parts) == 19
    # event_id calculé même en mode brut (sur trigger seul)
    assert len(parts[14]) == 12


# ---------------------------------------------------------------------------
# Garde-fou : extractor désactivé sans clé
# ---------------------------------------------------------------------------

def test_extractor_disabled_without_api_key(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    e = ex.Extractor()
    assert e.client is None
    out = e.extract("Some news")
    assert "disabled" in out.error or "hard-capped" in out.error


# ---------------------------------------------------------------------------
# v2.4 — DATE DU JOUR + stabilité du préfixe de cache
# ---------------------------------------------------------------------------

def _new_extractor_stub() -> "ex.Extractor":
    """Instance Extractor sans réseau pour tester _build_messages (méthode pure)."""
    e = ex.Extractor.__new__(ex.Extractor)
    e.model = "deepseek-chat"
    return e


def test_build_messages_date_only_in_last_user_message():
    """La DATE DU JOUR n'apparaît QUE dans le dernier message user (le variable).
    Le préfixe [system + few-shots] ne doit JAMAIS contenir 'DATE DU JOUR'."""
    e = _new_extractor_stub()
    msgs = e._build_messages("Iran retaliates", "Tehran launched drones")
    # Dernier message = user variable, contient la date + le titre
    last = msgs[-1]
    assert last["role"] == "user"
    assert last["content"].startswith("DATE DU JOUR : ")
    assert "TITRE : Iran retaliates" in last["content"]
    # Aucun message du préfixe ne contient la LIGNE DATÉE injectée (la mention
    # 'DATE DU JOUR' dans la règle 10 du system est attendue, mais jamais la date réelle).
    import re
    for m in msgs[:-1]:
        assert not re.search(r"DATE DU JOUR : \d{4}-\d{2}-\d{2}", m["content"]), (
            "la date réelle ne doit jamais figurer dans le préfixe de cache"
        )


def test_build_messages_prefix_strictly_stable():
    """Le préfixe [system + few-shots] (tous les messages SAUF le dernier) est
    STRICTEMENT identique entre 2 builds → cache DeepSeek préservé. Seule la
    queue (dernier message user) varie."""
    e = _new_extractor_stub()
    m1 = e._build_messages("News A", "snippet A")
    m2 = e._build_messages("News B totalement différente", "snippet B")
    assert len(m1) == len(m2)
    # Tous les messages N-1 identiques (préfixe figé)
    assert m1[:-1] == m2[:-1]
    # Seul le dernier diffère (queue variable)
    assert m1[-1] != m2[-1]


def test_build_messages_date_format_iso():
    """La date injectée est au format ISO YYYY-MM-DD (Europe/Paris, pas d'offset dur)."""
    import re
    e = _new_extractor_stub()
    msgs = e._build_messages("X", "")
    m = re.match(r"^DATE DU JOUR : (\d{4}-\d{2}-\d{2})\n", msgs[-1]["content"])
    assert m is not None, "préfixe DATE DU JOUR : YYYY-MM-DD attendu"


# ---------------------------------------------------------------------------
# v2.4 — few-shots : plus de single-name M&A → indice ; nouvel exemple verbal
# ---------------------------------------------------------------------------

def test_fewshots_no_single_name_ma_to_index():
    """L'ancien few-shot 'Microsoft acquire Anthropic → NASDAQ' est retiré
    (contredisait l'anti-piège single-name)."""
    for user_msg, assistant_json in ex.FEW_SHOTS:
        assert "Anthropic" not in user_msg
        assert "Microsoft" not in user_msg
        # plus aucun few-shot category m_a (le seul restant single-name était (c))
        data = json.loads(assistant_json)
        if data.get("category") == "m_a":
            pytest.fail("un few-shot m_a single-name subsiste")


def test_fewshots_new_verbal_central_bank_example():
    """Le few-shot (c) de remplacement est verbal + central_bank, sans single-name."""
    found = False
    for user_msg, assistant_json in ex.FEW_SHOTS:
        if "rate cuts" in user_msg and "Fed official" in user_msg:
            found = True
            data = json.loads(assistant_json)
            assert data["category"] == "central_bank"
            assert data["nature"] == "verbal"
            assert data["reliability"] == "reported"
            # impacts indice-large + or, confidence low (déclaration conditionnelle)
            assets = {imp["asset"] for imp in data["impacts"]}
            assert {"SP500", "NASDAQ", "GOLD"} <= assets
            assert all(imp["confidence"] == "low" for imp in data["impacts"])
    assert found, "nouveau few-shot verbal central_bank introuvable"


# ---------------------------------------------------------------------------
# v2.4 — RÈGLES renumérotées : séquence strictement croissante 1,2,3,…
# ---------------------------------------------------------------------------

def test_system_prompt_rules_sequence_strictly_increasing():
    """Les RÈGLES sont numérotées 1,2,3,… sans saut ni doublon (ex-bug 1,9,2,3)."""
    import re
    # Section RÈGLES : entre 'RÈGLES :' et 'Réponds avec UNIQUEMENT le JSON.'
    body = ex.SYSTEM_PROMPT.split("RÈGLES :", 1)[1]
    # Numéros en début de ligne (les sous-puces commencent par '-' ou espaces).
    nums = [int(n) for n in re.findall(r"^(\d+)\.", body, flags=re.MULTILINE)]
    assert nums, "aucune règle numérotée détectée"
    assert nums == list(range(1, len(nums) + 1)), f"séquence non croissante : {nums}"


def test_system_prompt_mentions_date_rule():
    """Le SYSTEM_PROMPT contient la règle d'usage de la DATE DU JOUR."""
    assert "DATE DU JOUR" in ex.SYSTEM_PROMPT


def test_prompt_version_is_v24():
    assert ex.PROMPT_VERSION == "v2.4"
