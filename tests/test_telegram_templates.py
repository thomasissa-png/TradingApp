"""Tests templates Telegram (Phase 2c-2 — formats stricts).

Couverture :
- format_buy_signal (5 tests : 6 lignes max, 🟢, "Cible potentielle", expiration, paper_mode)
- format_sell_signal (5 tests : idem 🔴)
- format_no_trade (4 tests : 3L strict — score, conflit, VIX, férié)
- format_data_error (1 test)
- format_degraded_mode (3 tests : claude_timeout, twelvedata_partial, cron_late)
- format_weekly_summary (1 test)
- format_monthly_report (1 test)
- vocabulaire proscrit (1 test grep transverse)
"""

from __future__ import annotations

import pytest

from src.ai.tools import ScoringSignalOutput
from src.telegram.templates import (
    format_buy_signal,
    format_data_error,
    format_degraded_mode,
    format_monthly_report,
    format_no_trade,
    format_sell_signal,
    format_weekly_summary,
)


# ---------------------------------------------------------------------------
# Fixtures signaux
# ---------------------------------------------------------------------------


def _signal_buy(asset: str = "DAX Turbo Call", edge: str = "H-A") -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000001",
        date="2026-05-04",
        hour_calc="08:42",
        asset=asset,
        direction="BUY",
        entry=3.42,
        sl=3.21,
        tp=3.85,
        score=7.4,
        raison="gap haussier DAX +0,9% vs clôture US — amplitude top 15% sur 250 ouvertures",
        edge_id=edge,
        backtest_ref="#B-031",
        ALERT_flag="ALERT",
        no_trade_reason=None,
        model_used="claude-sonnet-4-5-20250929",
    )


def _signal_sell(asset: str = "CAC40 Turbo Put", edge: str = "H-A") -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000002",
        date="2026-05-04",
        hour_calc="08:42",
        asset=asset,
        direction="SELL",
        entry=4.17,
        sl=4.38,
        tp=3.71,
        score=7.2,
        raison="gap baissier CAC40 -1,1% — futures US -0,7% pré-session",
        edge_id=edge,
        backtest_ref="#B-018",
        ALERT_flag="ALERT",
        no_trade_reason=None,
        model_used="claude-sonnet-4-5-20250929",
    )


def _signal_no_trade(reason: str = "Score 5,1 sous seuil 6,5") -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000003",
        date="2026-05-04",
        hour_calc="08:42",
        asset="CAC40",
        direction="NO_TRADE",
        entry=None,
        sl=None,
        tp=None,
        score=5.1,
        raison=reason,
        edge_id="H-A",
        backtest_ref="#B-031",
        ALERT_flag="NO_TRADE",
        no_trade_reason=reason,
        model_used="claude-sonnet-4-5-20250929",
    )


# ---------------------------------------------------------------------------
# format_buy_signal — 5 tests
# ---------------------------------------------------------------------------


def test_buy_signal_six_lines_max() -> None:
    msg = format_buy_signal(_signal_buy())
    lines = msg.split("\n")
    assert len(lines) == 6, f"BUY doit avoir 6 lignes (signal+score), reçu: {len(lines)}\n{msg}"


def test_buy_signal_contains_green_emoji_and_label() -> None:
    msg = format_buy_signal(_signal_buy())
    assert msg.startswith("🟢 ACHAT") or msg.startswith("[PAPER TRADING] 🟢 ACHAT")
    assert "ACHAT" in msg


def test_buy_signal_contains_cible_potentielle() -> None:
    msg = format_buy_signal(_signal_buy())
    assert "Cible potentielle" in msg, "TP doit être nommé 'Cible potentielle' (conditionnel obligatoire)"


def test_buy_signal_expiration_line_h_a() -> None:
    msg = format_buy_signal(_signal_buy(edge="H-A"))
    assert "Avant 8h55 CET" in msg
    assert "ne pas exécuter" in msg


def test_buy_signal_expiration_line_h_c_orb_at_9h00() -> None:
    msg = format_buy_signal(_signal_buy(edge="H-C"))
    assert "Avant 9h00 CET" in msg, "H-C ORB doit avoir cutoff 9h00 (breakout 8h-8h15)"


def test_buy_signal_paper_mode_prefix() -> None:
    msg = format_buy_signal(_signal_buy(), paper_mode=True)
    assert msg.startswith("[PAPER TRADING] "), f"Préfixe paper_mode manquant: {msg[:50]}"


def test_buy_signal_score_visible() -> None:
    msg = format_buy_signal(_signal_buy())
    assert "Score : 7,4/10" in msg or "Score : 7.4/10" in msg


# ---------------------------------------------------------------------------
# format_sell_signal — 5 tests
# ---------------------------------------------------------------------------


def test_sell_signal_six_lines_max() -> None:
    msg = format_sell_signal(_signal_sell())
    lines = msg.split("\n")
    assert len(lines) == 6


def test_sell_signal_contains_red_emoji_and_label() -> None:
    msg = format_sell_signal(_signal_sell())
    assert "🔴 VENTE" in msg


def test_sell_signal_contains_cible_potentielle() -> None:
    msg = format_sell_signal(_signal_sell())
    assert "Cible potentielle" in msg


def test_sell_signal_expiration_line_default() -> None:
    msg = format_sell_signal(_signal_sell())
    assert "Avant 8h55 CET" in msg


def test_sell_signal_paper_mode_prefix() -> None:
    msg = format_sell_signal(_signal_sell(), paper_mode=True)
    assert msg.startswith("[PAPER TRADING] ")


def test_sell_signal_score_visible() -> None:
    msg = format_sell_signal(_signal_sell())
    assert "/10" in msg
    assert "7,2" in msg or "7.2" in msg


def test_sell_signal_raises_on_wrong_direction() -> None:
    with pytest.raises(ValueError):
        format_sell_signal(_signal_buy())


def test_buy_signal_raises_on_wrong_direction() -> None:
    with pytest.raises(ValueError):
        format_buy_signal(_signal_sell())


# ---------------------------------------------------------------------------
# format_no_trade — 4 tests (NT-01 score / NT-02 conflit / NT-03 VIX / NT-04 férié)
# ---------------------------------------------------------------------------


def test_no_trade_three_lines_strict_score_under_threshold() -> None:
    sig = _signal_no_trade("Volume Xetra insuffisant (+8% vs requis +20%)")
    msg = format_no_trade(sig, max_score=5.1)
    lines = msg.split("\n")
    assert len(lines) == 3, f"NO-TRADE doit faire 3 lignes strict, reçu: {len(lines)}"
    assert "⚪️ NO-TRADE" in lines[0]
    assert "Score 5,1/10" in lines[0] or "Score 5.1/10" in lines[0]


def test_no_trade_conflict_news_technique() -> None:
    sig = _signal_no_trade("Conflit news/technique : BCE allocution 8h30 — biais bloqué")
    msg = format_no_trade(sig)
    assert "⚪️ NO-TRADE" in msg
    assert "BCE" in msg or "Conflit" in msg


def test_no_trade_vix_panique() -> None:
    sig = _signal_no_trade("VIX 28,4 > seuil 27,0 (régime panique — backtests non représentatifs)")
    msg = format_no_trade(sig)
    assert "VIX" in msg
    assert "panique" in msg


def test_no_trade_jour_ferie_partiel() -> None:
    sig = _signal_no_trade("Configuration absente : pont férié partiel — volume Euronext -47%")
    msg = format_no_trade(sig)
    assert "férié" in msg or "Configuration" in msg


# ---------------------------------------------------------------------------
# format_data_error / format_degraded_mode — 4 tests
# ---------------------------------------------------------------------------


def test_data_error_includes_missing_field() -> None:
    msg = format_data_error(
        {"asset": "DAX", "missing_field": "volume 1m Xetra", "hour": "8h44"}
    )
    assert "ERREUR DATA" in msg
    assert "volume 1m Xetra" in msg
    assert "8h44" in msg
    assert "status.twelvedata.com" in msg


def test_degraded_mode_claude_timeout() -> None:
    msg = format_degraded_mode("claude_timeout")
    assert "DEGRADED MODE" in msg
    assert "Claude" in msg
    assert "timeout" in msg
    assert "demain 8h40 CET" in msg


def test_degraded_mode_twelvedata_partial() -> None:
    msg = format_degraded_mode(
        "twelvedata_partial",
        context={"missing_field": "volume Xetra", "hour": "8h44"},
    )
    assert "DEGRADED MODE" in msg
    assert "Twelve Data" in msg


def test_degraded_mode_cron_late() -> None:
    msg = format_degraded_mode("cron_late", context={"date": "2026-05-04"})
    assert "CRON MANQUÉ" in msg
    assert "healthchecks.io" in msg
    assert "2026-05-04" in msg


# ---------------------------------------------------------------------------
# format_weekly_summary + format_monthly_report
# ---------------------------------------------------------------------------


def test_weekly_summary_renders_all_kpis() -> None:
    stats = {
        "week_n": 18,
        "week_start": "2026-04-27",
        "week_end": "2026-05-01",
        "signaux": 5,
        "trades": 3,
        "no_trades": 2,
        "pnl_brut": 124.50,
        "pnl_net": 118.54,
        "win_rate": 66.0,
        "gagnants": 2,
        "perdants": 1,
        "drawdown": 8,
        "meilleur_signal": "DAX",
        "meilleur_pct": 4.2,
        "meilleur_ref": "#B-031",
        "pire_signal": "CAC40",
        "pire_pct": -1.8,
        "pire_ref": "#B-018",
        "pertes_consecutives": 1,
    }
    msg = format_weekly_summary(stats, paper_mode=False)
    assert "Résumé semaine 18" in msg
    # Phase 2d-bis (R2) : passage parse_mode HTML — & escape en &amp;
    assert "P&amp;L brut semaine" in msg
    assert "Win rate semaine : 66%" in msg
    assert "DAX" in msg
    # Drawdown < 15 → pas d'alerte affichée
    assert "Drawdown hebdo" not in msg or "> 15%" not in msg


def test_weekly_summary_alerts_on_high_drawdown() -> None:
    stats = {
        "week_n": 18,
        "week_start": "2026-04-27",
        "week_end": "2026-05-01",
        "signaux": 5,
        "trades": 5,
        "no_trades": 0,
        "pnl_brut": -200,
        "pnl_net": -210,
        "win_rate": 20,
        "gagnants": 1,
        "perdants": 4,
        "drawdown": 18,
        "meilleur_signal": "DAX",
        "meilleur_pct": 1,
        "meilleur_ref": "#B-031",
        "pire_signal": "CAC40",
        "pire_pct": -5,
        "pire_ref": "#B-018",
        "pertes_consecutives": 4,
    }
    msg = format_weekly_summary(stats, paper_mode=True)
    assert "[PAPER TRADING]" in msg
    assert "Drawdown hebdo" in msg
    assert "pertes consécutives" in msg


def test_monthly_report_includes_pfu_and_prompt() -> None:
    stats = {
        "mois": "Avril 2026",
        "pnl_brut": 350.0,
        "frais": -19.80,
        "pnl_net": 330.20,
        "pfu": -103.68,
        "pnl_net_pfu": 226.52,
        "win_rate": 62,
        "backtest_win_rate": 60,
        "nb_trades": 18,
        "no_trades": 4,
        "no_trade_pct": 18,
        "drawdown_max": 12,
        "hypotheses_actives": ["H-A", "H-C"],
        "meilleure_hypothese": "H-C",
        "meilleure_wr": 70,
        "meilleure_n": 10,
        "hypothese_a_surveiller": "H-A",
        "surveiller_wr": 55,
        "surveiller_backtest": 63,
    }
    msg = format_monthly_report(stats, prompt_continue=True)
    assert "Rapport mensuel Avril 2026" in msg
    assert "Fiscalité PFU" in msg
    # Phase 2d-bis (R2) : passage parse_mode HTML — & escape en &amp;
    assert "P&amp;L net après PFU" in msg
    assert "/continue" in msg
    assert "/stop" in msg


def test_monthly_report_no_prompt_when_disabled() -> None:
    stats = {
        "mois": "Avril 2026",
        "pnl_brut": 0,
        "frais": 0,
        "pnl_net": 0,
        "pfu": 0,
        "pnl_net_pfu": 0,
        "win_rate": 0,
        "backtest_win_rate": 0,
        "nb_trades": 0,
        "no_trades": 0,
        "no_trade_pct": 0,
        "drawdown_max": 0,
        "hypotheses_actives": [],
        "meilleure_hypothese": "—",
        "meilleure_wr": 0,
        "meilleure_n": 0,
        "hypothese_a_surveiller": "—",
        "surveiller_wr": 0,
        "surveiller_backtest": 0,
    }
    msg = format_monthly_report(stats, prompt_continue=False)
    assert "/continue" not in msg
    assert "/stop" not in msg


# ---------------------------------------------------------------------------
# Vocabulaire proscrit — grep transverse
# ---------------------------------------------------------------------------


PROSCRIT = [
    "signal fort",
    "buy now",
    "guaranteed",
    "garanti",
    "perfect entry",
    "opportunity",
    "ne pas manquer",
]


def test_no_proscribed_vocabulary_in_any_template() -> None:
    """Aucun template ne doit contenir un mot proscrit (case-insensitive)."""
    outputs: list[str] = [
        format_buy_signal(_signal_buy()),
        format_buy_signal(_signal_buy(), paper_mode=True),
        format_sell_signal(_signal_sell()),
        format_sell_signal(_signal_sell(), paper_mode=True),
        format_no_trade(_signal_no_trade(), max_score=5.1),
        format_data_error({"asset": "DAX", "missing_field": "volume", "hour": "8h44"}),
        format_degraded_mode("claude_timeout"),
        format_degraded_mode("twelvedata_partial"),
        format_degraded_mode("cron_late"),
    ]
    for output in outputs:
        lower = output.lower()
        for word in PROSCRIT:
            assert word.lower() not in lower, (
                f"Mot proscrit '{word}' trouvé dans output:\n{output}"
            )


# ---------------------------------------------------------------------------
# G24 boucle visuelle adaptée — snapshot mockup texte
# ---------------------------------------------------------------------------


def test_generate_telegram_mockups(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Génère snapshots Markdown bruts pour audit visuel @design.

    Cf prompt mission Phase 2c-2 — G24 adapté Telegram (rendu desktop = brut Markdown).
    """
    import os

    out_dir = "tests/screenshots/telegram-mockup"
    os.makedirs(out_dir, exist_ok=True)

    snapshots = {
        "TC-01-BUY-H-A.txt": format_buy_signal(_signal_buy()),
        "TC-02-BUY-H-C.txt": format_buy_signal(_signal_buy(edge="H-C")),
        "TC-03-BUY-paper.txt": format_buy_signal(_signal_buy(), paper_mode=True),
        "TC-04-SELL.txt": format_sell_signal(_signal_sell()),
        "TC-05-NO-TRADE-score.txt": format_no_trade(_signal_no_trade(), max_score=5.1),
        "TC-06-NO-TRADE-VIX.txt": format_no_trade(
            _signal_no_trade("VIX 28,4 > seuil 27,0 (régime panique)")
        ),
        "TC-07-DATA-ERROR.txt": format_data_error(
            {"asset": "DAX", "missing_field": "volume 1m Xetra", "hour": "8h44"}
        ),
        "TC-08-DEGRADED-CLAUDE.txt": format_degraded_mode("claude_timeout"),
        "TC-09-DEGRADED-CRON.txt": format_degraded_mode(
            "cron_late", context={"date": "2026-05-04"}
        ),
    }

    for filename, content in snapshots.items():
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        assert os.path.exists(path)
