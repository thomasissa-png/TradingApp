"""7 sanity checks deterministes ex-post (SC1-SC7) v1.2.

Source : docs/ia/edge-scoring-model.md v1.2 §3.

SC1 BLOQUANT : coherence direction/SL/TP -> NO_TRADE force si incoherent
SC2 BLOQUANT : R/R >= 1.5 (plafond 6.0 si <1.5, NO_TRADE force si <1.0)
SC3 ALERT    : score brut > 9.0 -> ALERT_flag
SC4 PENALITE : %no-trade 7j < 20% -> score -1.0 (BOOTSTRAP off si <7 signaux historiques)
SC5 PLAFOND  : raison speculatif (pourrait/devrait/...) sans chiffre -> plafond 6.0
SC6 ALERT    : edge sur 1 seul sous-jacent / 13 sur 30j -> plafond 7.0 + ALERT
                (BOOTSTRAP off si < 30j historiques)
SC7 ALERT    : |score_LLM - score_deterministe| > 1.5 -> plafond 7.0 + ALERT
                                                  > 3.0 -> NO_TRADE force
"""

from __future__ import annotations

import re
from typing import Any

from src.ai.tools import ScoringSignalOutput

# Universe Bourse Direct (3 indices EU + 10 actions FR) — cf project-context Thomas
UNIVERSE_SIZE = 13

# Patterns langage speculatif (SC5) — cf edge-scoring-model §3.5
_SPECULATIVE_PATTERNS = re.compile(
    r"\b(pourrait|pourraient|devrait|devraient|probablement|peut[- ]etre|"
    r"peut etre|possible que|va peut[- ]etre|semble|paraitrait?)\b",
    re.IGNORECASE,
)
# Detection chiffre (nombre brut, pourcentage, prix, indicateur)
_NUMBER_PATTERN = re.compile(r"\d+[.,]?\d*")


# ---------------------------------------------------------------------------
# SC1 — Coherence direction/SL/TP
# ---------------------------------------------------------------------------

def apply_sc1(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC1 : direction coherente avec placement SL/TP.

    BUY  : sl < entry < tp (turbo call)
    SELL : tp < entry < sl (turbo put)
    NO_TRADE : entry/sl/tp tous null
    """
    triggered: list[str] = []

    if signal.direction == "NO_TRADE":
        if signal.entry is not None or signal.sl is not None or signal.tp is not None:
            triggered.append("SC1")
            updated = signal.model_copy(
                update={
                    "entry": None,
                    "sl": None,
                    "tp": None,
                    "score": 1.0,
                    "ALERT_flag": "NO_TRADE",
                    "no_trade_reason": "SC1 incoherence: NO_TRADE doit avoir entry/sl/tp=null",
                }
            )
            return updated, triggered
        return signal, triggered

    # BUY ou SELL : verifier que les 3 valeurs sont presentes
    if signal.entry is None or signal.sl is None or signal.tp is None:
        triggered.append("SC1")
        updated = signal.model_copy(
            update={
                "direction": "NO_TRADE",
                "entry": None,
                "sl": None,
                "tp": None,
                "score": 1.0,
                "ALERT_flag": "NO_TRADE",
                "no_trade_reason": f"SC1 incoherence: direction {signal.direction} sans entry/sl/tp",
            }
        )
        return updated, triggered

    if signal.direction == "BUY":
        if not (signal.sl < signal.entry < signal.tp):
            triggered.append("SC1")
            updated = signal.model_copy(
                update={
                    "direction": "NO_TRADE",
                    "entry": None,
                    "sl": None,
                    "tp": None,
                    "score": 1.0,
                    "ALERT_flag": "NO_TRADE",
                    "no_trade_reason": (
                        f"SC1 incoherence BUY: sl={signal.sl} entry={signal.entry} tp={signal.tp}"
                    ),
                }
            )
            return updated, triggered
    elif signal.direction == "SELL" and not (signal.tp < signal.entry < signal.sl):
        triggered.append("SC1")
        updated = signal.model_copy(
            update={
                "direction": "NO_TRADE",
                "entry": None,
                "sl": None,
                "tp": None,
                "score": 1.0,
                "ALERT_flag": "NO_TRADE",
                "no_trade_reason": (
                    f"SC1 incoherence SELL: sl={signal.sl} entry={signal.entry} tp={signal.tp}"
                ),
            }
        )
        return updated, triggered

    return signal, triggered


# ---------------------------------------------------------------------------
# SC2 — R/R minimum 1.5
# ---------------------------------------------------------------------------

def apply_sc2(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC2 : R/R >= 1.5 sinon plafond 6.0 ; < 1.0 -> NO_TRADE force."""
    triggered: list[str] = []

    if signal.direction == "NO_TRADE" or signal.entry is None or signal.sl is None or signal.tp is None:
        return signal, triggered

    if signal.direction == "BUY":
        risk = signal.entry - signal.sl
        reward = signal.tp - signal.entry
    else:  # SELL
        risk = signal.sl - signal.entry
        reward = signal.entry - signal.tp

    if risk <= 0:
        # SC1 aurait du catch ; defense en profondeur
        triggered.append("SC2")
        updated = signal.model_copy(
            update={
                "direction": "NO_TRADE",
                "entry": None,
                "sl": None,
                "tp": None,
                "score": 1.0,
                "ALERT_flag": "NO_TRADE",
                "no_trade_reason": "SC2 risk<=0 (SL invalide)",
            }
        )
        return updated, triggered

    rr = reward / risk

    if rr < 1.0:
        triggered.append("SC2")
        updated = signal.model_copy(
            update={
                "direction": "NO_TRADE",
                "entry": None,
                "sl": None,
                "tp": None,
                "score": min(signal.score, 1.0),
                "ALERT_flag": "NO_TRADE",
                "no_trade_reason": (
                    f"SC2 R/R {rr:.2f} < 1.0 — gain potentiel insuffisant vs risque"
                ),
            }
        )
        return updated, triggered

    if rr < 1.5:
        triggered.append("SC2")
        updated = signal.model_copy(update={"score": min(signal.score, 6.0)})
        return updated, triggered

    return signal, triggered


# ---------------------------------------------------------------------------
# SC3 — Score brut > 9.0 -> ALERT
# ---------------------------------------------------------------------------

def apply_sc3(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC3 : score > 9.0 -> ALERT_flag (revue manuelle)."""
    triggered: list[str] = []
    if signal.score > 9.0 and signal.direction != "NO_TRADE":
        triggered.append("SC3")
        updated = signal.model_copy(update={"ALERT_flag": "ALERT"})
        return updated, triggered
    return signal, triggered


# ---------------------------------------------------------------------------
# SC4 — % no-trade 7j < 20% -> score -1.0 (BOOTSTRAP off si < 7 signaux)
# ---------------------------------------------------------------------------

def apply_sc4(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
    recent_signals: list[dict[str, Any]] | None = None,
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC4 : si %no-trade 7j < 20%, penalite -1.0.

    Bootstrap : desactive si recent_signals < 7 (besoin d'historique fiable).
    recent_signals format : [{"direction": "BUY|SELL|NO_TRADE", ...}, ...]
    """
    triggered: list[str] = []
    if recent_signals is None or len(recent_signals) < 7:
        return signal, triggered

    no_trade_count = sum(1 for s in recent_signals if s.get("direction") == "NO_TRADE")
    ratio = no_trade_count / len(recent_signals)

    if ratio < 0.20:
        triggered.append("SC4")
        new_score = max(1.0, signal.score - 1.0)
        updated = signal.model_copy(update={"score": new_score})
        return updated, triggered

    return signal, triggered


# ---------------------------------------------------------------------------
# SC5 — Langage speculatif sans chiffre -> plafond 6.0
# ---------------------------------------------------------------------------

def apply_sc5(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC5 : si raison contient mots speculatifs sans chiffre, plafond 6.0."""
    triggered: list[str] = []
    raison = signal.raison

    speculative_match = _SPECULATIVE_PATTERNS.search(raison)
    if not speculative_match:
        return signal, triggered

    # Verifier presence d'un chiffre dans la phrase qui contient le mot speculatif
    # (heuristique : couper aux points/virgules autour du match)
    start, end = speculative_match.span()
    # Etend le contexte : phrase = du dernier '.' avant 'start' au prochain '.' apres 'end'
    sentence_start = max(raison.rfind(".", 0, start), raison.rfind(";", 0, start)) + 1
    next_dot = raison.find(".", end)
    next_semicolon = raison.find(";", end)
    candidates = [c for c in (next_dot, next_semicolon) if c >= 0]
    sentence_end = min(candidates) if candidates else len(raison)
    sentence = raison[sentence_start:sentence_end]

    if not _NUMBER_PATTERN.search(sentence):
        triggered.append("SC5")
        updated = signal.model_copy(update={"score": min(signal.score, 6.0)})
        return updated, triggered

    return signal, triggered


# ---------------------------------------------------------------------------
# SC6 — Diversite sous-jacents 30j (1/13) -> plafond 7.0 + ALERT
# ---------------------------------------------------------------------------

def apply_sc6(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
    recent_30d_signals: list[dict[str, Any]] | None = None,
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC6 : si l'edge n'a triggé que sur 1 sous-jacent / 13 sur 30j -> plafond 7.0 + ALERT.

    Bootstrap : desactive si recent_30d_signals couvrent < 30 jours (lookup `date` field).
    recent_30d_signals format : [{"edge_id": ..., "asset": ..., "date": "YYYY-MM-DD", "direction": ...}]
    """
    triggered: list[str] = []
    if recent_30d_signals is None or len(recent_30d_signals) == 0:
        return signal, triggered

    # Bootstrap : besoin d'au moins 30 jours d'historique distincts
    distinct_dates = {s.get("date") for s in recent_30d_signals if s.get("date")}
    if len(distinct_dates) < 30:
        return signal, triggered

    # Compter les sous-jacents distincts pour cet edge_id (hors NO_TRADE)
    same_edge = [
        s
        for s in recent_30d_signals
        if s.get("edge_id") == signal.edge_id and s.get("direction") != "NO_TRADE"
    ]
    distinct_assets = {s.get("asset") for s in same_edge if s.get("asset")}

    if len(distinct_assets) <= 1:
        triggered.append("SC6")
        updated = signal.model_copy(
            update={
                "score": min(signal.score, 7.0),
                "ALERT_flag": "ALERT" if signal.direction != "NO_TRADE" else signal.ALERT_flag,
            }
        )
        return updated, triggered

    return signal, triggered


# ---------------------------------------------------------------------------
# SC7 — Plausibilite LLM vs deterministe (v1.2)
# ---------------------------------------------------------------------------

def apply_sc7(
    signal: ScoringSignalOutput,
    deterministic_score: float | None,
) -> tuple[ScoringSignalOutput, list[str]]:
    """SC7 : si |score_LLM - score_deterministe| > 1.5 -> plafond 7.0 + ALERT.

    Si > 3.0 -> NO_TRADE force (divergence inacceptable, audit prompt requis).
    """
    triggered: list[str] = []
    if deterministic_score is None:
        return signal, triggered

    delta = abs(signal.score - deterministic_score)

    if delta > 3.0:
        triggered.append("SC7")
        updated = signal.model_copy(
            update={
                "direction": "NO_TRADE",
                "entry": None,
                "sl": None,
                "tp": None,
                "score": deterministic_score,
                "ALERT_flag": "NO_TRADE",
                "no_trade_reason": (
                    f"SC7 ecart LLM {signal.score:.1f} vs deterministe "
                    f"{deterministic_score:.1f} > 3.0 — audit prompt requis"
                ),
            }
        )
        return updated, triggered

    if delta > 1.5:
        triggered.append("SC7")
        updated = signal.model_copy(
            update={
                "score": min(signal.score, 7.0),
                "ALERT_flag": "ALERT" if signal.direction != "NO_TRADE" else signal.ALERT_flag,
            }
        )
        return updated, triggered

    return signal, triggered


# ---------------------------------------------------------------------------
# Agregat — apply_all_sanity_checks
# ---------------------------------------------------------------------------

def apply_all_sanity_checks(
    signal: ScoringSignalOutput,
    context: dict[str, Any],
    recent_signals: list[dict[str, Any]] | None = None,
    recent_30d_signals: list[dict[str, Any]] | None = None,
    deterministic_score: float | None = None,
) -> tuple[ScoringSignalOutput, list[str]]:
    """Applique SC1-SC7 dans l'ordre. SC1 prioritaire (NO_TRADE bloque les autres).

    Returns (signal_modifie, liste_SC_declenches).
    """
    all_triggered: list[str] = []

    # SC1 prioritaire — si NO_TRADE force, court-circuit les autres
    signal, triggered = apply_sc1(signal, context)
    all_triggered.extend(triggered)
    if signal.direction == "NO_TRADE" and "SC1" in triggered:
        return signal, all_triggered

    # SC2 (peut aussi forcer NO_TRADE)
    signal, triggered = apply_sc2(signal, context)
    all_triggered.extend(triggered)
    if signal.direction == "NO_TRADE" and "SC2" in triggered:
        return signal, all_triggered

    # SC3 — flag ALERT seulement
    signal, triggered = apply_sc3(signal, context)
    all_triggered.extend(triggered)

    # SC4 — penalite (peut faire passer sous threshold mais pas force NO_TRADE)
    signal, triggered = apply_sc4(signal, context, recent_signals)
    all_triggered.extend(triggered)

    # SC5 — plafond 6.0
    signal, triggered = apply_sc5(signal, context)
    all_triggered.extend(triggered)

    # SC6 — plafond 7.0 + ALERT
    signal, triggered = apply_sc6(signal, context, recent_30d_signals)
    all_triggered.extend(triggered)

    # SC7 — plausibilite LLM vs deterministe (peut force NO_TRADE)
    signal, triggered = apply_sc7(signal, deterministic_score)
    all_triggered.extend(triggered)

    return signal, all_triggered
