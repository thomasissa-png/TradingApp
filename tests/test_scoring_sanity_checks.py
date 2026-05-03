"""Tests des 7 sanity checks SC1-SC7 + apply_all_sanity_checks (chainage)."""

from __future__ import annotations

from typing import Any

import pytest

from src.ai.tools import ScoringSignalOutput
from src.scoring.sanity_checks import (
    apply_all_sanity_checks,
    apply_sc1,
    apply_sc2,
    apply_sc3,
    apply_sc4,
    apply_sc5,
    apply_sc6,
    apply_sc7,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_signal(**overrides: Any) -> ScoringSignalOutput:
    base: dict[str, Any] = {
        "id": "11111111-2222-4333-8444-555555555555",
        "date": "2026-05-04",
        "hour_calc": "08:47",
        "asset": "DAX Turbo Call",
        "direction": "BUY",
        "entry": 3.42,
        "sl": 3.21,
        "tp": 3.85,
        "score": 8.0,
        "raison": "Gap haussier +0,82% sur cloture US, ORB casse a 18420.",
        "edge_id": "H-A",
        "backtest_ref": "#B-031",
        "ALERT_flag": "SAFE",
        "no_trade_reason": None,
        "model_used": "claude-sonnet-4-6",
    }
    base.update(overrides)
    return ScoringSignalOutput(**base)


# ---------------------------------------------------------------------------
# SC1 — Coherence direction/SL/TP
# ---------------------------------------------------------------------------


def test_sc1_buy_coherent_passes() -> None:
    sig = _make_signal()  # sl 3.21 < entry 3.42 < tp 3.85 OK
    result, triggered = apply_sc1(sig, {})
    assert triggered == []
    assert result.direction == "BUY"


def test_sc1_buy_incoherent_force_no_trade() -> None:
    """BUY avec sl > entry -> SC1 force NO_TRADE."""
    sig = _make_signal(sl=3.50)  # sl > entry incoherent
    result, triggered = apply_sc1(sig, {})
    assert triggered == ["SC1"]
    assert result.direction == "NO_TRADE"
    assert result.no_trade_reason is not None
    assert "SC1" in result.no_trade_reason


def test_sc1_sell_coherent() -> None:
    sig = _make_signal(direction="SELL", entry=2.50, sl=2.65, tp=2.20)  # tp<entry<sl
    result, triggered = apply_sc1(sig, {})
    assert triggered == []
    assert result.direction == "SELL"


def test_sc1_no_trade_with_non_null_fields_corrected() -> None:
    sig = _make_signal(direction="NO_TRADE", entry=3.42, sl=3.21, tp=3.85)
    result, triggered = apply_sc1(sig, {})
    assert triggered == ["SC1"]
    assert result.entry is None and result.sl is None and result.tp is None


# ---------------------------------------------------------------------------
# SC2 — R/R minimum 1.5
# ---------------------------------------------------------------------------


def test_sc2_rr_above_15_passes() -> None:
    """R/R = (3.85-3.42)/(3.42-3.21) = 0.43/0.21 = ~2.05 > 1.5."""
    sig = _make_signal()
    result, triggered = apply_sc2(sig, {})
    assert triggered == []
    assert result.score == 8.0


def test_sc2_rr_between_1_and_15_plafond_6() -> None:
    """R/R = 1.2 -> plafond 6.0."""
    sig = _make_signal(entry=3.42, sl=3.20, tp=3.68)  # R/R = 0.26/0.22 = ~1.18
    result, triggered = apply_sc2(sig, {})
    assert triggered == ["SC2"]
    assert result.score == 6.0


def test_sc2_rr_below_1_force_no_trade() -> None:
    sig = _make_signal(entry=3.42, sl=3.20, tp=3.55)  # R/R = 0.13/0.22 = ~0.59
    result, triggered = apply_sc2(sig, {})
    assert triggered == ["SC2"]
    assert result.direction == "NO_TRADE"


def test_sc2_no_trade_signal_skipped() -> None:
    """SC2 ne touche pas un signal NO_TRADE."""
    sig = _make_signal(direction="NO_TRADE", entry=None, sl=None, tp=None, score=4.0)
    result, triggered = apply_sc2(sig, {})
    assert triggered == []
    assert result.score == 4.0


def test_sc2_amplitude_below_1pct_plafond_6() -> None:
    """SC2 v1.3 : amplitude attendue (tp-entry)/entry < 1 % -> plafond 6.0.

    Decision Thomas 2026-05-02 : viser >= 1 % pour absorber frais turbo.
    Exemple : entry=100, sl=99.0 (risk 1), tp=100.7 (reward 0.7 = 0.70 %)
    R/R = 0.70 mais < 1.0 -> NO_TRADE force (cas 2 prevaut).
    On teste donc amplitude < 1 % MAIS R/R >= 1.5 : entry=100, sl=99.6, tp=100.7
    risk=0.4, reward=0.7, R/R=1.75, amplitude=0.7 % < 1 % -> plafond 6.0.
    """
    sig = _make_signal(entry=100.0, sl=99.6, tp=100.7, score=8.0)
    result, triggered = apply_sc2(sig, {})
    assert triggered == ["SC2"]
    assert result.direction == "BUY"  # Pas force NO_TRADE (amplitude > 0.5 %)
    assert result.score == 6.0


def test_sc2_amplitude_below_05pct_no_trade() -> None:
    """SC2 v1.3 : amplitude attendue < 0.5 % -> NO_TRADE force (frais non absorbes)."""
    # entry=100, sl=99.8, tp=100.4 -> amplitude = 0.4 % < 0.5 % -> NO_TRADE
    sig = _make_signal(entry=100.0, sl=99.8, tp=100.4, score=8.0)
    result, triggered = apply_sc2(sig, {})
    assert triggered == ["SC2"]
    assert result.direction == "NO_TRADE"
    assert result.no_trade_reason is not None
    assert "amplitude" in result.no_trade_reason.lower()


def test_sc2_amplitude_above_1pct_pass() -> None:
    """SC2 v1.3 : amplitude >= 1 % ET R/R >= 1.5 -> pass sans triggered."""
    # entry=100, sl=99.5, tp=101.5 -> risk=0.5, reward=1.5, R/R=3.0, amplitude=1.5 % -> PASS
    sig = _make_signal(entry=100.0, sl=99.5, tp=101.5, score=8.0)
    result, triggered = apply_sc2(sig, {})
    assert triggered == []
    assert result.direction == "BUY"
    assert result.score == 8.0


def test_sc2_amplitude_sell_below_1pct_plafond_6() -> None:
    """SC2 v1.3 : meme logique cote SELL — amplitude (entry-tp)/entry < 1 % -> plafond 6.0."""
    # SELL : entry=100, sl=100.4, tp=99.3 -> risk=0.4, reward=0.7, R/R=1.75, amplitude=0.7 %
    sig = _make_signal(direction="SELL", entry=100.0, sl=100.4, tp=99.3, score=8.0)
    result, triggered = apply_sc2(sig, {})
    assert triggered == ["SC2"]
    assert result.direction == "SELL"
    assert result.score == 6.0


# ---------------------------------------------------------------------------
# SC2 v1.4 — Amplitude STRICTEMENT sur sous-jacent (clarification Thomas 2026-05-03)
# ---------------------------------------------------------------------------


def test_sc2_amplitude_underlying_below_1pct_no_trade() -> None:
    """SC2 v1.4 : amplitude sous-jacent < 0.5 % -> NO_TRADE force.

    DAX : underlying_entry=17300, underlying_tp=17350
    -> amplitude = (17350-17300)/17300 = 0.289 % < 0.5 %
    Meme si R/R turbo >= 1.5 (entry=3.42, sl=3.21, tp=3.85, R/R~2.05),
    le filtre amplitude sur sous-jacent court-circuite -> NO_TRADE.
    """
    sig = _make_signal(entry=3.42, sl=3.21, tp=3.85, score=8.0)
    context = {"underlying_entry": 17300.0, "underlying_tp": 17350.0}
    result, triggered = apply_sc2(sig, context)
    assert triggered == ["SC2"]
    assert result.direction == "NO_TRADE"
    assert result.no_trade_reason is not None
    assert "amplitude" in result.no_trade_reason.lower()


def test_sc2_amplitude_underlying_above_1pct_pass() -> None:
    """SC2 v1.4 : amplitude sous-jacent >= 1 % ET R/R turbo >= 1.5 -> PASS sans triggered.

    DAX : underlying_entry=17300, underlying_tp=17500
    -> amplitude = 200/17300 = 1.156 % >= 1 %
    Turbo : entry=3.42, sl=3.21, tp=3.85 -> R/R = 0.43/0.21 ~ 2.05 >= 1.5
    -> Aucun plafond applique, score conserve.
    """
    sig = _make_signal(entry=3.42, sl=3.21, tp=3.85, score=8.0)
    context = {"underlying_entry": 17300.0, "underlying_tp": 17500.0}
    result, triggered = apply_sc2(sig, context)
    assert triggered == []
    assert result.direction == "BUY"
    assert result.score == 8.0


def test_sc2_amplitude_underlying_sell_below_05pct_no_trade() -> None:
    """SC2 v1.4 cote SELL : amplitude sous-jacent (valeur absolue) < 0.5 % -> NO_TRADE."""
    # CAC40 SELL : underlying_entry=8000, underlying_tp=7990
    # -> abs(7990-8000)/8000 = 0.125 % < 0.5 %
    sig = _make_signal(direction="SELL", entry=2.50, sl=2.65, tp=2.20, score=8.0)
    context = {"underlying_entry": 8000.0, "underlying_tp": 7990.0}
    result, triggered = apply_sc2(sig, context)
    assert triggered == ["SC2"]
    assert result.direction == "NO_TRADE"


def test_sc2_amplitude_underlying_between_05_and_1pct_plafond_6() -> None:
    """SC2 v1.4 : amplitude sous-jacent dans [0.5%, 1.0%[ ET R/R turbo >= 1.5 -> plafond 6.0."""
    # underlying_entry=17300, underlying_tp=17430 -> 130/17300 = 0.751 % dans [0.5%, 1.0%[
    sig = _make_signal(entry=3.42, sl=3.21, tp=3.85, score=8.0)  # R/R turbo ~2.05
    context = {"underlying_entry": 17300.0, "underlying_tp": 17430.0}
    result, triggered = apply_sc2(sig, context)
    assert triggered == ["SC2"]
    assert result.direction == "BUY"
    assert result.score == 6.0


def test_sc2_amplitude_fallback_turbo_when_underlying_absent() -> None:
    """SC2 v1.4 : si underlying_entry/underlying_tp absents -> fallback turbo (deprecie).

    Garantit retro-compatibilite : tests turbo existants (sans context underlying)
    continuent de fonctionner avec calcul amplitude sur prix turbo.
    """
    # Memes prix que test_sc2_amplitude_above_1pct_pass : amplitude turbo 1.5 % -> PASS
    sig = _make_signal(entry=100.0, sl=99.5, tp=101.5, score=8.0)
    result, triggered = apply_sc2(sig, {})  # context vide -> fallback
    assert triggered == []
    assert result.score == 8.0


# ---------------------------------------------------------------------------
# SC3 — Score brut > 9.0 -> ALERT
# ---------------------------------------------------------------------------


def test_sc3_score_above_9_alert() -> None:
    sig = _make_signal(score=9.5)
    result, triggered = apply_sc3(sig, {})
    assert triggered == ["SC3"]
    assert result.ALERT_flag == "ALERT"


def test_sc3_score_below_9_no_action() -> None:
    sig = _make_signal(score=8.0)
    result, triggered = apply_sc3(sig, {})
    assert triggered == []
    assert result.ALERT_flag == "SAFE"


# ---------------------------------------------------------------------------
# SC4 — % no-trade 7j < 20% -> -1.0 (BOOTSTRAP off si <7 signaux)
# ---------------------------------------------------------------------------


def test_sc4_bootstrap_disabled_under_7_signals() -> None:
    sig = _make_signal()
    recent = [{"direction": "BUY"} for _ in range(5)]
    result, triggered = apply_sc4(sig, {}, recent_signals=recent)
    assert triggered == []
    assert result.score == 8.0


def test_sc4_low_no_trade_ratio_penalty() -> None:
    """7 signaux dont 1 NO_TRADE = 14% -> penalite -1.0."""
    sig = _make_signal(score=7.5)
    recent = [{"direction": "BUY"} for _ in range(6)] + [{"direction": "NO_TRADE"}]
    result, triggered = apply_sc4(sig, {}, recent_signals=recent)
    assert triggered == ["SC4"]
    assert result.score == 6.5  # 7.5 - 1.0


def test_sc4_high_no_trade_ratio_no_penalty() -> None:
    """50% NO_TRADE -> pas de penalite."""
    sig = _make_signal()
    recent = [{"direction": "BUY"}, {"direction": "NO_TRADE"}, {"direction": "BUY"},
              {"direction": "NO_TRADE"}, {"direction": "SELL"}, {"direction": "NO_TRADE"},
              {"direction": "BUY"}]
    result, triggered = apply_sc4(sig, {}, recent_signals=recent)
    assert triggered == []


# ---------------------------------------------------------------------------
# SC5 — Speculatif sans chiffre -> plafond 6.0
# ---------------------------------------------------------------------------


def test_sc5_speculative_with_number_passes() -> None:
    """'Le DAX pourrait monter de 0.5%' = chiffre present, OK."""
    sig = _make_signal(raison="Le DAX pourrait monter de 0.5% sur la matinee.")
    result, triggered = apply_sc5(sig, {})
    assert triggered == []


def test_sc5_speculative_without_number_plafond() -> None:
    """'Le marche pourrait monter' sans chiffre -> plafond 6.0."""
    sig = _make_signal(score=8.0, raison="Le marche pourrait monter en milieu de seance.")
    result, triggered = apply_sc5(sig, {})
    assert triggered == ["SC5"]
    assert result.score == 6.0


def test_sc5_factual_no_speculative() -> None:
    """Raison purement factuelle = aucun trigger."""
    sig = _make_signal(raison="Gap haussier 0,82% sur cloture US, ORB casse a 18420.")
    result, triggered = apply_sc5(sig, {})
    assert triggered == []


# ---------------------------------------------------------------------------
# SC6 — Diversite sous-jacents 30j (BOOTSTRAP off si <30j)
# ---------------------------------------------------------------------------


def test_sc6_bootstrap_disabled_under_30_days() -> None:
    """recent_30d_signals couvrent <30 jours -> bootstrap, pas de SC6."""
    sig = _make_signal()
    recent = [
        {"edge_id": "H-A", "asset": "DAX", "date": f"2026-05-{i:02d}", "direction": "BUY"}
        for i in range(1, 11)  # 10 jours seulement
    ]
    result, triggered = apply_sc6(sig, {}, recent_30d_signals=recent)
    assert triggered == []


def test_sc6_one_asset_only_alert_plafond() -> None:
    """30j historique, edge n'a triggé que sur DAX -> plafond 7.0 + ALERT."""
    sig = _make_signal(score=8.5)
    recent = [
        {"edge_id": "H-A", "asset": "DAX", "date": f"2026-04-{i:02d}", "direction": "BUY"}
        for i in range(1, 31)
    ]
    result, triggered = apply_sc6(sig, {}, recent_30d_signals=recent)
    assert triggered == ["SC6"]
    assert result.score == 7.0
    assert result.ALERT_flag == "ALERT"


def test_sc6_diversity_ok_no_action() -> None:
    """3 sous-jacents distincts -> pas de SC6."""
    sig = _make_signal(score=8.5)
    assets = ["DAX", "CAC40", "EuroStoxx50"]
    recent = [
        {
            "edge_id": "H-A",
            "asset": assets[i % 3],
            "date": f"2026-04-{(i % 30) + 1:02d}",
            "direction": "BUY",
        }
        for i in range(60)
    ]
    result, triggered = apply_sc6(sig, {}, recent_30d_signals=recent)
    assert triggered == []
    assert result.score == 8.5


# ---------------------------------------------------------------------------
# SC7 — Plausibilite LLM vs deterministe
# ---------------------------------------------------------------------------


def test_sc7_delta_below_15_no_action() -> None:
    """|8.0 - 7.5| = 0.5 -> OK."""
    sig = _make_signal(score=8.0)
    result, triggered = apply_sc7(sig, deterministic_score=7.5)
    assert triggered == []
    assert result.score == 8.0


def test_sc7_delta_between_15_and_30_plafond_alert() -> None:
    """|8.0 - 5.2| = 2.8 -> plafond 7.0 + ALERT (TC-06)."""
    sig = _make_signal(score=8.0)
    result, triggered = apply_sc7(sig, deterministic_score=5.2)
    assert triggered == ["SC7"]
    assert result.score == 7.0
    assert result.ALERT_flag == "ALERT"


def test_sc7_delta_above_30_force_no_trade() -> None:
    """|9.0 - 4.0| = 5.0 -> NO_TRADE force."""
    sig = _make_signal(score=9.0)
    result, triggered = apply_sc7(sig, deterministic_score=4.0)
    assert triggered == ["SC7"]
    assert result.direction == "NO_TRADE"
    assert result.no_trade_reason is not None
    assert "SC7" in result.no_trade_reason


def test_sc7_no_deterministic_score_skipped() -> None:
    """deterministic_score=None -> SC7 desactive."""
    sig = _make_signal(score=8.0)
    result, triggered = apply_sc7(sig, deterministic_score=None)
    assert triggered == []


# ---------------------------------------------------------------------------
# apply_all_sanity_checks — chainage
# ---------------------------------------------------------------------------


def test_apply_all_sc1_priority_blocks_others() -> None:
    """SC1 declenche -> court-circuit SC2-SC7."""
    sig = _make_signal(sl=3.50)  # incoherent BUY
    result, triggered = apply_all_sanity_checks(sig, {}, deterministic_score=5.0)
    assert "SC1" in triggered
    assert result.direction == "NO_TRADE"


def test_apply_all_clean_signal_no_triggers() -> None:
    """Signal propre + deterministe coherent -> 0 trigger."""
    sig = _make_signal()
    result, triggered = apply_all_sanity_checks(sig, {}, deterministic_score=7.5)
    assert triggered == []
    assert result.direction == "BUY"


def test_apply_all_sc7_catches_llm_drift_tc06() -> None:
    """TC-06 reproduit : LLM 8.0, deterministe 5.2 -> SC7 catch."""
    sig = _make_signal(score=8.0)
    result, triggered = apply_all_sanity_checks(sig, {}, deterministic_score=5.2)
    assert "SC7" in triggered
    assert result.score == 7.0
    assert result.ALERT_flag == "ALERT"


def test_apply_all_sc3_alert_with_high_score() -> None:
    """Score 9.5 -> SC3 ALERT."""
    sig = _make_signal(score=9.5)
    result, triggered = apply_all_sanity_checks(sig, {}, deterministic_score=9.3)
    assert "SC3" in triggered
    assert result.ALERT_flag == "ALERT"
