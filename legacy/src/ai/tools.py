"""Tool definitions Anthropic + Pydantic validation pour le scoring de signal.

Source de verite :
- docs/ia/prompt-library.md v1.1 §3.1 (tool emit_signal_scoring)
- docs/ia/ai-architecture.md v1.1 §2.2 (schema output strict)
- src/journal/schema.py (DDL_SIGNALS — directions BUY/SELL/NO_TRADE)

Versioning du tool schema :
- v1.2 (Phase 2c) : 15 champs stricts emis par Claude
- v1.3 (Phase 2d-bis) : +3 champs OPTIONNELS `win_rate_backtest`, `nb_trades_backtest`,
  `drawdown_max_backtest` — calcules cote code (lookup rnd_results) AVANT format
  Telegram, JAMAIS emis par Claude (cf docs/ia/ai-architecture.md §2.2 note —
  anti-hallucination R-AI-1 : Claude ne doit pas inventer des stats backtest).
  Acceptes None pour les signaux sans backtest_ref retrouve dans rnd_results.

Note : la table SQLite signals utilise BUY/SELL/NO_TRADE (UPPER, underscore).
Les docs IA utilisent ACHAT/VENTE/NO-TRADE (FR, hyphen). Le tool Anthropic accepte
les 2 jeux de literals (`direction` enum) — la conversion est faite en aval (engine.py)
avant INSERT SQLite, JAMAIS dans le tool ou dans Claude (anti-hallucination R-AI-1).
"""

from __future__ import annotations

import re
from typing import Any, Literal

import anthropic
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Tool definition Anthropic — schema 15 champs strict (emis par Claude)
# +3 champs OPTIONNELS post-LLM (win_rate_backtest, nb_trades_backtest,
#  drawdown_max_backtest) — alimentes cote code via lookup rnd_results
# ---------------------------------------------------------------------------

SCORING_TOOL_DEFINITION: dict[str, Any] = {
    "name": "emit_signal_scoring",
    "description": (
        "Emet le scoring structure du signal turbo intraday EU pour TradingApp. "
        "A appeler une seule fois par requete. Les 15 premiers champs sont "
        "obligatoires (emis par Claude). Les 3 stats backtest sont alimentees "
        "cote code apres l'appel — ne PAS les inventer."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "UUID v4"},
            "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "hour_calc": {"type": "string", "pattern": r"^\d{2}:\d{2}$"},
            "asset": {"type": "string", "minLength": 1, "maxLength": 50},
            "direction": {"type": "string", "enum": ["BUY", "SELL", "NO_TRADE"]},
            "entry": {"type": ["number", "null"]},
            "sl": {"type": ["number", "null"]},
            "tp": {"type": ["number", "null"]},
            "score": {"type": "number", "minimum": 1.0, "maximum": 10.0},
            "raison": {"type": "string", "minLength": 10, "maxLength": 300},
            "edge_id": {
                "type": "string",
                "enum": ["H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G"],
            },
            "backtest_ref": {"type": "string", "pattern": r"^#B-\d{3}$"},
            "ALERT_flag": {"type": "string", "enum": ["ALERT", "SAFE", "NO_TRADE"]},
            "no_trade_reason": {"type": ["string", "null"]},
            "model_used": {"type": "string"},
            # v1.3 — champs OPTIONNELS calcules cote code (lookup rnd_results),
            # JAMAIS emis par Claude. Acceptes pour passage strict du schema si
            # un futur outil les renseignait, sinon laisses None par parse_tool_response.
            "win_rate_backtest": {
                "type": ["number", "null"],
                "minimum": 0.0,
                "maximum": 100.0,
                "description": (
                    "NE PAS REMPLIR — alimente cote code apres l'appel "
                    "depuis rnd_results.backtest_ref."
                ),
            },
            "nb_trades_backtest": {
                "type": ["integer", "null"],
                "minimum": 0,
                "description": "NE PAS REMPLIR — alimente cote code.",
            },
            "drawdown_max_backtest": {
                "type": ["number", "null"],
                "minimum": 0.0,
                "description": (
                    "NE PAS REMPLIR — alimente cote code. Stocke en valeur "
                    "POSITIVE (ex 17.0 pour drawdown -17%)."
                ),
            },
        },
        "required": [
            "id",
            "date",
            "hour_calc",
            "asset",
            "direction",
            "entry",
            "sl",
            "tp",
            "score",
            "raison",
            "edge_id",
            "backtest_ref",
            "ALERT_flag",
            "no_trade_reason",
            "model_used",
        ],
    },
}


# ---------------------------------------------------------------------------
# Pydantic validation post-reponse Anthropic
# ---------------------------------------------------------------------------


class ScoringSignalOutput(BaseModel):
    """Output du tool `emit_signal_scoring`.

    - 15 premiers champs : emis par Claude (strict, validation Pydantic + retry max 2 cf R-AI-5)
    - 3 champs backtest (v1.3) : OPTIONNELS, alimentes cote code via lookup rnd_results
      apres l'appel LLM (cf docs/ia/ai-architecture.md §2.2 — anti-hallucination R-AI-1).
      None si backtest_ref non trouve dans rnd_results (template affichera fallback).
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    hour_calc: str = Field(pattern=r"^\d{2}:\d{2}$")
    asset: str = Field(min_length=1, max_length=50)
    direction: Literal["BUY", "SELL", "NO_TRADE"]
    entry: float | None
    sl: float | None
    tp: float | None
    score: float = Field(ge=1.0, le=10.0)
    raison: str = Field(min_length=10, max_length=300)
    edge_id: Literal["H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G"]
    backtest_ref: str = Field(pattern=r"^#B-\d{3}$")
    ALERT_flag: Literal["ALERT", "SAFE", "NO_TRADE"]
    no_trade_reason: str | None
    model_used: str
    # v1.3 — stats backtest enrichies cote code (lookup rnd_results)
    win_rate_backtest: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Win rate du backtest reference en % (None si lookup KO).",
    )
    nb_trades_backtest: int | None = Field(
        default=None,
        ge=0,
        description="Nombre de trades du backtest reference (None si lookup KO).",
    )
    drawdown_max_backtest: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Drawdown max du backtest reference en % (POSITIF, ex 17.0 pour DD -17%). "
            "None si lookup KO."
        ),
    )


# ---------------------------------------------------------------------------
# Parsing reponse Anthropic
# ---------------------------------------------------------------------------


class ToolResponseParseError(ValueError):
    """Echec de parsing tool_use block dans la reponse Anthropic."""


def parse_tool_response(response: anthropic.types.Message) -> ScoringSignalOutput:
    """Extrait et valide le bloc tool_use `emit_signal_scoring` de la reponse Anthropic.

    Raises ToolResponseParseError si :
    - aucun bloc tool_use trouve
    - le bloc tool_use porte un nom different
    - les champs ne respectent pas le schema Pydantic
    """
    if not response.content:
        raise ToolResponseParseError("Reponse Anthropic vide (no content blocks)")

    for block in response.content:
        if getattr(block, "type", None) == "tool_use":
            block_name = getattr(block, "name", None)
            if block_name != "emit_signal_scoring":
                raise ToolResponseParseError(
                    f"Bloc tool_use porte le nom inattendu: {block_name!r}"
                )
            tool_input = getattr(block, "input", None)
            if not isinstance(tool_input, dict):
                raise ToolResponseParseError(
                    f"Bloc tool_use input doit etre un dict, recu: {type(tool_input)}"
                )
            return ScoringSignalOutput(**tool_input)

    raise ToolResponseParseError("Aucun bloc tool_use trouve dans la reponse Anthropic")


# ---------------------------------------------------------------------------
# Sanitization news_titles (TC-07 prompt injection — cf prompt-library §5.5)
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    # "Ignore previous/prior/all (previous) instructions..."
    re.compile(
        r"ignore\s+(?:all\s+)?(?:previous|prior|all)\s+instructions?[^.\n]*\.?",
        re.IGNORECASE,
    ),
    re.compile(r"\bscore\s*=\s*\d+(\.\d+)?", re.IGNORECASE),
    re.compile(r"\bdirection\s*=\s*(BUY|SELL|ACHAT|VENTE|NO[_-]?TRADE)", re.IGNORECASE),
    re.compile(r"\b(always|toujours)\s+(return|retourne)\b[^.\n]*", re.IGNORECASE),
    re.compile(r"<\s*/?\s*(system|user|assistant)[^>]*>", re.IGNORECASE),
)

_INJECTION_REPLACEMENT = "[INJECTION ATTEMPT REMOVED]"


def sanitize_news_titles(titles: list[str]) -> list[str]:
    """Strip prompt injection patterns sur une liste de titres news.

    Pattern detectes (cf prompt-library v1.1 §5.5 TC-07) :
    - "Ignore previous instructions..."
    - "score=10", "direction=BUY"
    - "always return..." / "toujours retourner..."
    - tags <system>...</system> tentatives d'echappement

    Garantit qu'aucun titre vide ne reste si toute la chaine etait injection
    (remplace par chaine "[INJECTION ATTEMPT REMOVED]").
    """
    sanitized: list[str] = []
    for title in titles:
        cleaned = title
        for pattern in _INJECTION_PATTERNS:
            cleaned = pattern.sub(_INJECTION_REPLACEMENT, cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned:
            cleaned = _INJECTION_REPLACEMENT
        sanitized.append(cleaned)
    return sanitized
