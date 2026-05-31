"""TradingApp v3 — Synthèse directionnelle PAR ACTIF (DeepSeek).

OBJET
=====
Quand plusieurs news se contredisent sur un même actif (ex: 16 LONG vs 8 SHORT
sur 7 jours), l'agrégation mécanique (plus récent / matérialité brute) peut
sortir une direction à contresens du marché. La SYNTHÈSE DIRECTIONNELLE confie
à DeepSeek la résultante d'un actif : il reçoit TOUTES les news récentes d'un
actif d'un coup et rend :

    { "direction": "LONG|SHORT|NEUTRAL",
      "conviction": "high|medium|low",
      "rationale": "<courte explication factuelle>" }

NIVEAU 1 — synthèse IA : un appel par actif ayant des news (≤12/cycle).
NIVEAU 2 — fallback prix : si conviction = low OU direction = NEUTRAL OU
synthèse indisponible (clé absente / hard-cap / erreur), le critère news
passe à 0 dans triggers_classifier ; ce sont alors les critères numériques
(momentum, prix, RSI…) de la cellule qui portent la direction. Le prix ne ment
pas.

GARANTIES
=========
- Aucun crash si DEEPSEEK_API_KEY absente : retourne None proprement.
- Réutilise le cost-ledger de Extractor (pas de double-comptage : on appelle
  extractor._update_cost après chaque call).
- temperature=0, response_format JSON strict.
- Parsing défensif : tout champ hors-énum → conviction "low" + direction "NEUTRAL".
- Interface stable : synthesize_asset / synthesize_all (rien d'autre n'est public).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("synthese_directionnelle")


# Énumérations fermées (alignées avec les buckets de l'Extractor)
_DIRECTIONS = ("LONG", "SHORT", "NEUTRAL")
_DIR_SET = set(_DIRECTIONS)
_CONVICTIONS = ("high", "medium", "low")
_CONV_SET = set(_CONVICTIONS)

# Plafond dur de news par actif (anti-runaway tokens). On garde les N plus récentes.
MAX_EVENTS_PER_ASSET = 30

# Plafond de tokens en sortie (le JSON attendu est court).
MAX_OUTPUT_TOKENS = 350

# Prompt système : court, factuel, JSON strict.
SYSTEM_PROMPT = """Tu es un analyste senior d'un desk de news trading institutionnel.

On te fournit, pour UN actif donné, la liste des news récentes déjà étiquetées
par un premier passage IA (direction LONG/SHORT par news, matérialité, date).

Ta mission : produire la RESULTANTE directionnelle de l'actif sur la fenêtre.
Tu dois peser : matérialité, fraîcheur, cohérence des signaux, et NE PAS
simplement compter les news. Une seule news "high" récente peut surclasser
8 news "low" plus anciennes.

Tu réponds UNIQUEMENT avec un JSON strict :

{
  "direction": "LONG | SHORT | NEUTRAL",
  "conviction": "high | medium | low",
  "rationale": "<2 phrases max, factuelles>"
}

REGLES :
1. AUCUNE INVENTION. Si les news se contredisent sans signal dominant clair
   -> direction "NEUTRAL", conviction "low".
2. NEUTRAL est légitime : un marché sans biais net DOIT renvoyer NEUTRAL.
3. conviction "high" = signal dominant clair, matérialité élevée, fraîcheur OK.
   conviction "medium" = signal présent mais contesté ou matérialité moyenne.
   conviction "low" = signal faible, dispersé, ancien ou bruité.
4. rationale = factuel, court, cite les drivers (ex: "OPEC cut confirmé +
   tensions Ormuz dominent malgré 3 news demand-side faibles").
5. Ne mentionne aucun ticker hors de l'actif demandé.

Réponds avec UNIQUEMENT le JSON, rien d'autre."""


def _safe_get(d: Any, key: str, default: str = "") -> str:
    if not isinstance(d, dict):
        return default
    v = d.get(key)
    if v is None:
        return default
    return str(v)


def _format_events_for_prompt(asset_id: str, events: List[dict]) -> str:
    """Sérialise les events en un bloc texte compact, lisible par le LLM.

    Format d'une ligne :
      - 2026-05-28 | mat=high | impact=LONG (conf=high) | trigger…

    Ne contient QUE les events qui ont un impact IA ciblant `asset_id` (LONG/SHORT).
    NEUTRAL et événements sans impact pertinent sont filtrés en amont par
    l'appelant (triggers_classifier), mais on re-filtre ici par robustesse.
    """
    lines: List[str] = [f"ACTIF : {asset_id}", "NEWS RECENTES (les plus récentes en premier) :"]
    kept = 0
    for ev in events:
        if kept >= MAX_EVENTS_PER_ASSET:
            break
        # Date : on prend la string brute ou _dt.isoformat()
        dt = ev.get("_dt")
        if dt is not None and hasattr(dt, "strftime"):
            date_str = dt.strftime("%Y-%m-%d")
        else:
            date_str = _safe_get(ev, "date", "?")[:10]

        mat = (_safe_get(ev, "materiality") or "low").lower()
        rel = (_safe_get(ev, "reliability") or "").lower()
        trigger = (_safe_get(ev, "trigger") or _safe_get(ev, "l2") or "")[:180]

        # Cherche l'impact IA pour cet actif (si présent)
        impacts = ev.get("_impacts") or []
        impact_str = "n/a"
        for imp in impacts:
            if not isinstance(imp, dict):
                continue
            if str(imp.get("asset", "")).upper() != asset_id.upper():
                continue
            d = str(imp.get("direction", "")).upper()
            if d not in ("LONG", "SHORT"):
                continue
            c = str(imp.get("confidence", "low")).lower()
            impact_str = f"{d} (conf={c})"
            break

        line = f"- {date_str} | mat={mat}"
        if rel:
            line += f" | rel={rel}"
        line += f" | impact={impact_str} | {trigger}"
        lines.append(line)
        kept += 1

    if kept == 0:
        lines.append("(aucune news directionnelle exploitable)")

    lines.append("")
    lines.append("Réponds avec le JSON strict {direction, conviction, rationale}.")
    return "\n".join(lines)


def _parse_response(content: str) -> Optional[Dict[str, str]]:
    """Parse le JSON renvoyé par DeepSeek. Retourne None si invalide."""
    if not content or not isinstance(content, str):
        return None
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning("synthese: JSON invalide : %s", str(e)[:120])
        return None
    if not isinstance(data, dict):
        return None

    direction_raw = str(data.get("direction", "")).strip().upper()
    if direction_raw not in _DIR_SET:
        # Tolérance : bullish/bearish -> LONG/SHORT
        if direction_raw in ("BULLISH", "BUY"):
            direction_raw = "LONG"
        elif direction_raw in ("BEARISH", "SELL"):
            direction_raw = "SHORT"
        elif direction_raw in ("NEUTRE", "FLAT", ""):
            direction_raw = "NEUTRAL"
        else:
            direction_raw = "NEUTRAL"  # défaut sûr

    conviction_raw = str(data.get("conviction", "")).strip().lower()
    if conviction_raw not in _CONV_SET:
        conviction_raw = "low"

    rationale = str(data.get("rationale", "") or "")[:500]

    return {
        "direction": direction_raw,
        "conviction": conviction_raw,
        "rationale": rationale,
    }


def synthesize_asset(
    asset_id: str,
    events_recent: List[dict],
    extractor: Any,
) -> Optional[Dict[str, str]]:
    """Synthèse directionnelle pour UN actif (1 appel DeepSeek).

    Args:
        asset_id: id IA fermé ("BRENT", "GOLD", ...).
        events_recent: liste d'events DEJA FILTRES par fenêtre lookback,
            triés desc par date. Format = celui de parse_events_log() (dicts
            avec `_dt`, `_impacts`, `materiality`, `reliability`, `trigger`...).
        extractor: instance Extractor (réutilisée pour client + cost-ledger).
            Si extractor est None ou non-activé → retourne None.

    Returns:
        {"direction": "LONG|SHORT|NEUTRAL",
         "conviction": "high|medium|low",
         "rationale": "..."}
        ou None si la synthèse n'est pas exploitable (pas de clé, hard-cap,
        erreur LLM, parsing KO). Le caller (triggers_classifier) DOIT alors
        retomber sur l'ancienne logique (mécanique keyword/IA agrégée).
    """
    if extractor is None:
        return None
    # is_enabled() = client présent ET pas hard-capped
    is_enabled = getattr(extractor, "is_enabled", None)
    if not callable(is_enabled) or not is_enabled():
        return None
    client = getattr(extractor, "client", None)
    if client is None:
        return None
    if not events_recent:
        # Pas de news → rien à synthétiser. On retourne explicitement NEUTRAL/low
        # pour distinguer "pas de news" de "erreur LLM".
        return {"direction": "NEUTRAL", "conviction": "low", "rationale": "aucune news exploitable"}

    user_content = _format_events_for_prompt(asset_id, events_recent)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    start = time.monotonic()
    try:
        response = client.chat.completions.create(
            model=getattr(extractor, "model", "deepseek-chat"),
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
            max_tokens=MAX_OUTPUT_TOKENS,
            timeout=20,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
    except Exception as e:
        logger.warning("synthese[%s]: appel LLM KO : %s", asset_id, str(e)[:160])
        return None

    # Mise à jour cost-ledger (réutilise la mécanique Extractor)
    try:
        usage = getattr(response, "usage", None)
        tokens_in = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
        tokens_out = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0
        update_cost = getattr(extractor, "_update_cost", None)
        if callable(update_cost):
            update_cost(tokens_in, tokens_out)
    except Exception as e:  # noqa: BLE001
        logger.debug("synthese[%s]: maj cost-ledger KO : %s", asset_id, str(e)[:120])

    try:
        content = response.choices[0].message.content
    except Exception as e:
        logger.warning("synthese[%s]: réponse mal formée : %s", asset_id, str(e)[:120])
        return None

    parsed = _parse_response(content)
    if parsed is None:
        return None

    logger.info(
        "synthese[%s] dur=%dms -> direction=%s conviction=%s | %s",
        asset_id, duration_ms,
        parsed["direction"], parsed["conviction"], parsed["rationale"][:160],
    )
    return parsed


def synthesize_all(
    events_by_asset: Dict[str, List[dict]],
    extractor: Any,
) -> Dict[str, Dict[str, str]]:
    """Synthèse pour tous les actifs ayant des news.

    Args:
        events_by_asset: {asset_id: [events triés desc par date]} — déjà filtrés
            par fenêtre lookback par l'appelant.
        extractor: instance Extractor (peut être None → tous None).

    Returns:
        {asset_id: {direction, conviction, rationale}} — les actifs pour
        lesquels la synthèse a échoué sont OMIS (clé absente). Le caller
        traite "clé absente" = pas de signal IA exploitable.
    """
    out: Dict[str, Dict[str, str]] = {}
    if not events_by_asset:
        return out
    for asset_id, events in events_by_asset.items():
        if not asset_id:
            continue
        res = synthesize_asset(asset_id, events, extractor)
        if res is not None:
            out[asset_id] = res
    return out
