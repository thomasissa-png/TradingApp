"""Module AI — client Anthropic + tool definitions + sanitization (Phase 2c-1).

Architecture : cf docs/ia/ai-architecture.md v1.1 + docs/ia/prompt-library.md v1.1.
Modeles : Sonnet 4.5 live + Haiku 4.5 R&D + Haiku fallback live (timeout 25s -> 10s).
"""

from __future__ import annotations

from src.ai.client import AnthropicClient
from src.ai.tools import (
    SCORING_TOOL_DEFINITION,
    ScoringSignalOutput,
    parse_tool_response,
    sanitize_news_titles,
)

__all__ = [
    "SCORING_TOOL_DEFINITION",
    "AnthropicClient",
    "ScoringSignalOutput",
    "parse_tool_response",
    "sanitize_news_titles",
]
