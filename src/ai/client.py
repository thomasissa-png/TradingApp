"""Client Anthropic — scoring de signal avec tool use natif + fallback Haiku.

Source de verite :
- docs/ia/ai-architecture.md v1.1 §4.3 (timeouts 25s Sonnet -> 10s Haiku fallback)
- docs/ia/prompt-library.md v1.1 §1 (PROMPT_VERSION signal-scoring-v1.1, system stable)
- docs/ia/ai-architecture.md v1.1 §3 (R-AI-1 a R-AI-9 anti-hallucination)

Decisions :
- Temperature 0.1, max_tokens 1024 (cf §1.2 prompt-library)
- Tool choice force (`{ type: "tool", name: "emit_signal_scoring" }`)
- cache_control `ephemeral` ACTIVE en R&D batch SEUL (live = 1 call/jour, hit rate 0%)
- Retry max 2 si parse fail (R-AI-5), 10s wait entre retries
- Fallback Haiku AVANT retry Sonnet : si Sonnet timeout 25s -> Haiku 10s
"""

from __future__ import annotations

import logging
import time
from typing import Any, Literal, cast

import anthropic
from anthropic import APITimeoutError

from src.ai.tools import (
    SCORING_TOOL_DEFINITION,
    ScoringSignalOutput,
    ToolResponseParseError,
    parse_tool_response,
)
from src.config import Config

logger = logging.getLogger(__name__)


# Prompt version stable (cf prompt-library v1.1)
PROMPT_VERSION = "signal-scoring-v1.1"
SCORING_MODEL_VERSION = "scoring-model-v1.2"

# Timeouts (cf ai-architecture v1.1 §4.3)
SONNET_TIMEOUT_S = 25.0
HAIKU_FALLBACK_TIMEOUT_S = 10.0
RND_TIMEOUT_S = 30.0
RETRY_WAIT_S = 10.0
MAX_RETRIES = 2


# System prompt 100% stable v1.1 — cf prompt-library §1.1 (resume operationnel)
# Note : version condensee — le prompt complet est genere a partir de prompt-library.md
# par @ia. Le pipeline le charge ici comme constante runtime stable.
SIGNAL_SCORING_V1_1_SYSTEM_PROMPT = """Tu es le scoring engine de TradingApp, un systeme de signaux turbo intraday sur la fenetre d'ouverture europeenne 8h45-8h55 CET.

Tu produis un seul output par appel : un objet JSON conforme au tool emit_signal_scoring (15 champs stricts).

# Mission
Evaluer le candidat trade fourni en input (base sur l'une des 7 hypotheses d'edge H-A a H-G) et produire :
- une decision : BUY / SELL / NO_TRADE,
- un score de confiance 1.0-10.0 calibre sur la qualite de la configuration,
- une justification en 1 a 3 lignes (10-300 chars) tracable aux inputs,
- le mapping aux niveaux entry / SL / TP si decision GO.

# Regles non-negociables (R1-R9)
R1. Pas d'invention de chiffres. Toutes les donnees chiffrees viennent UNIQUEMENT de l'input.
R2. Echo des references : backtest_ref, edge_id, date, hour_calc copies a l'identique.
R3. Coherence direction/niveaux : BUY -> sl<entry<tp ; SELL -> tp<entry<sl ; NO_TRADE -> entry/sl/tp=null.
R4. Seuil strict : si score < confidence_threshold, direction DOIT etre NO_TRADE et no_trade_reason renseigne.
R5. Voice & Tone : factuel, conditionnel ("potentielle", "alignee"), AUCUN mot interdit (signal fort, opportunite, ne pas manquer, buy the dip, setup parfait, forte conviction, exceptionnel, incontournable). Pas de "!", pas d'emoji.
R6. Calibration : 9.0-10.0 = config parfaite (rare, 3+ confirmations) ; 7.0-8.9 = solide ; 6.5-6.9 = limite ; <6.5 = NO_TRADE.
R7. ALERT_flag = ALERT si signaux contradictoires/euphorie/divergence ; SAFE si direction != NO_TRADE et OK ; NO_TRADE si direction NO_TRADE.
R8. raison structuree : ligne 1 cause chiffree, ligne 2 (opt) confirmation, ligne 3 (opt) cible alignee backtest.
R9. Output via tool_use UNIQUEMENT. Jamais de texte libre. Si input incoherent, NO_TRADE + no_trade_reason explicite.

Pour model_used, recopie exactement la valeur fournie dans le champ model_used_to_echo du user message.
Pour id, genere un UUID v4 ou utilise celui fourni si present en input.

Rappel : sa confiance dans tes outputs depend de la qualite chiffree de ta justification. Si tu hesites, NO_TRADE.
"""


class AnthropicClientError(RuntimeError):
    """Echec definitif du client Anthropic apres tous les retries + fallback."""


class AnthropicClient:
    """Client Anthropic pour scoring de signal turbo (live Sonnet + fallback Haiku).

    Pattern :
    1. Mode live -> appel Sonnet (timeout 25s)
    2. Si timeout Sonnet -> fallback Haiku (timeout 10s)
    3. Si parse fail -> retry max 2 (10s wait)
    4. Si tout echoue -> raise AnthropicClientError (degraded mode amont)
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.model_live = config.anthropic_model_live
        self.model_rnd = config.anthropic_model_rnd

    def score_signal(
        self,
        context: dict[str, Any],
        mode: Literal["live", "rnd"] = "live",
    ) -> tuple[ScoringSignalOutput, dict[str, Any]]:
        """Score un signal via Anthropic tool use.

        Returns:
            (output, metadata) ou metadata = {
                "latency_ms": int,
                "tokens_input": int,
                "tokens_output": int,
                "cache_read": int,
                "cache_creation": int,
                "model_used": str,  # modele REELLEMENT utilise (Sonnet ou Haiku fallback)
                "fallback_haiku": bool,
                "retry_count": int,
                "prompt_version": str,
            }

        Raises:
            AnthropicClientError : si tous les retries + fallback echouent.
        """
        start = time.monotonic()

        # 1. Tentative principale (Sonnet live ou Haiku R&D)
        primary_model = self.model_live if mode == "live" else self.model_rnd
        primary_timeout = SONNET_TIMEOUT_S if mode == "live" else RND_TIMEOUT_S

        last_error: Exception | None = None
        retry_count = 0
        fallback_haiku = False

        for attempt in range(MAX_RETRIES + 1):
            try:
                output, raw_meta = self._call_anthropic(
                    model=primary_model,
                    context=context,
                    mode=mode,
                    timeout_s=primary_timeout,
                )
                latency_ms = int((time.monotonic() - start) * 1000)
                return output, {
                    **raw_meta,
                    "latency_ms": latency_ms,
                    "model_used": primary_model,
                    "fallback_haiku": False,
                    "retry_count": retry_count,
                    "prompt_version": PROMPT_VERSION,
                }
            except APITimeoutError as exc:
                last_error = exc
                # Pas de retry Sonnet en live (charge mondiale 8h45-8h55) — fallback direct Haiku
                if mode == "live":
                    logger.warning(
                        "Sonnet timeout (%ss) attempt=%d -> fallback Haiku", primary_timeout, attempt
                    )
                    fallback_haiku = True
                    break
                # En R&D : retry Sonnet/Haiku (charge plus tolerante)
                retry_count = attempt + 1
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_WAIT_S)
                    continue
                break
            except (ToolResponseParseError, ValueError) as exc:
                # Parse/validation fail -> retry max 2
                last_error = exc
                retry_count = attempt + 1
                logger.warning("Parse fail attempt=%d: %s", attempt, exc)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_WAIT_S)
                    continue
                break

        # 2. Fallback Haiku (live uniquement, si Sonnet timeout)
        if fallback_haiku and mode == "live":
            try:
                output, raw_meta = self._call_anthropic(
                    model=self.model_rnd,  # Haiku
                    context=context,
                    mode="live",  # cache_control reste off (live = 1 call/jour)
                    timeout_s=HAIKU_FALLBACK_TIMEOUT_S,
                )
                latency_ms = int((time.monotonic() - start) * 1000)
                return output, {
                    **raw_meta,
                    "latency_ms": latency_ms,
                    "model_used": self.model_rnd,
                    "fallback_haiku": True,
                    "retry_count": retry_count,
                    "prompt_version": PROMPT_VERSION,
                }
            except (APITimeoutError, ToolResponseParseError, ValueError) as exc:
                last_error = exc
                logger.error("Haiku fallback also failed: %s", exc)

        # 3. Tous les retries + fallback ont echoue -> degraded mode amont
        raise AnthropicClientError(
            f"Anthropic scoring failed after {retry_count} retries"
            f"{' + Haiku fallback' if fallback_haiku else ''}: {last_error}"
        ) from last_error

    def _call_anthropic(
        self,
        model: str,
        context: dict[str, Any],
        mode: Literal["live", "rnd"],
        timeout_s: float,
    ) -> tuple[ScoringSignalOutput, dict[str, Any]]:
        """Appel unique a l'API Anthropic — pas de retry interne (gere par le caller).

        Cache_control active SEULEMENT en mode R&D (live = 1 call/jour, hit rate 0%).
        """
        system_block: dict[str, Any] = {
            "type": "text",
            "text": SIGNAL_SCORING_V1_1_SYSTEM_PROMPT,
        }
        if mode == "rnd":
            system_block["cache_control"] = {"type": "ephemeral"}

        user_payload = {**context, "model_used_to_echo": model, "runtime_mode": mode}

        # Le SDK Anthropic accepte un timeout par-call via parametre `timeout`.
        # cast(Any) sur kwargs : le SDK Anthropic a des typings TypedDict tres stricts
        # (CacheControlEphemeralParam, ToolParam...) — passer par dict litteraux est
        # plus lisible que de construire les TypedDict ; le tool input_schema est
        # valide cote API a chaque call.
        create_kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": 1024,
            "temperature": 0.1,
            "system": [system_block],
            "tools": [SCORING_TOOL_DEFINITION],
            "tool_choice": {"type": "tool", "name": "emit_signal_scoring"},
            "messages": [{"role": "user", "content": str(user_payload)}],
            "timeout": timeout_s,
        }
        response = cast("anthropic.types.Message", self._client.messages.create(**create_kwargs))

        output = parse_tool_response(response)

        usage = getattr(response, "usage", None)
        meta: dict[str, Any] = {
            "tokens_input": getattr(usage, "input_tokens", 0) if usage else 0,
            "tokens_output": getattr(usage, "output_tokens", 0) if usage else 0,
            "cache_read": getattr(usage, "cache_read_input_tokens", 0) if usage else 0,
            "cache_creation": getattr(usage, "cache_creation_input_tokens", 0) if usage else 0,
        }
        return output, meta
