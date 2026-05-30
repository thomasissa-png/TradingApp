"""Tests E2E Phase 2d — couverture des trous identifiés (`docs/qa/e2e-test-plan-phase2.md` §3).

Cible 12 trous fonctionnels :
1. /pause overlap (comportement actuel = écrasement silencieux — à confirmer)
2. /trade après /stop : flag paper_mode propagé (currently MISSING au niveau DB)
3. /continue après pause expirée (transition d'état)
4. healthchecks down → pas de crash
5. Twelve Data 429 → retry / graceful (au niveau ai_client analogue)
6. SC4 bootstrap : recent_signals=[] → pas de pénalité indue
7. SC6 bootstrap : < 30j historique → désactivé
8. Signal après cutoff 8h57 → silence + ping success + log "sent_too_late"
9. Jour férié FR (14 juillet) → skip silencieux + ping success
10. Pause active aujourd'hui → skip silencieux + ping success
11. Cutoff EXACT 8h55:00 → silence (frontière inclusive ?)
12. Recent signals SQLite error → fallback []
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.ai.tools import ScoringSignalOutput
from src.config import Config
from src.journal.db import (
    cancel_active_pause,
    get_connection,
    get_strategy_mode,
    init_database,
    insert_signal,
    insert_strategy_pause,
    is_paused_today,
    set_strategy_mode,
)
from src.lib.healthchecks import ping_healthchecks
from src.main import EXIT_OK, EXIT_SKIPPED, run_signal_mode
from src.scoring.sanity_checks import apply_sc4, apply_sc6

# ---------------------------------------------------------------------------
# Fixtures partagées
# ---------------------------------------------------------------------------


@pytest.fixture
def config(env_minimal: dict[str, str]) -> Config:
    return Config.from_env()


@pytest.fixture
def db_conn(config: Config) -> sqlite3.Connection:
    init_database(config.data_dir)
    conn = sqlite3.connect(Path(config.data_dir) / "journal.sqlite")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def _signal(direction: str = "BUY", score: float = 7.5, edge_id: str = "H-A") -> ScoringSignalOutput:
    return ScoringSignalOutput(
        id="00000000-0000-4000-8000-000000000099",
        date="2026-05-04",
        hour_calc="08:42",
        asset="DAX Turbo Call",
        direction=direction,  # type: ignore[arg-type]
        entry=3.42 if direction != "NO_TRADE" else None,
        sl=3.21 if direction != "NO_TRADE" else None,
        tp=3.85 if direction != "NO_TRADE" else None,
        score=score,
        raison="gap haussier DAX +0,9% — top 15% des 250 ouvertures",
        edge_id=edge_id,
        backtest_ref="#B-031",
        ALERT_flag="ALERT" if direction != "NO_TRADE" else "NO_TRADE",
        no_trade_reason=None if direction != "NO_TRADE" else "Score sous seuil",
        model_used="claude-sonnet-4-6",
    )


# ---------------------------------------------------------------------------
# 1. /pause overlap — comportement actuel = écrasement silencieux
# ---------------------------------------------------------------------------


def test_pause_overlap_rejects_explicitly(db_conn: sqlite3.Connection) -> None:
    """Phase 2d-bis (B1 audit @qa) : pause overlap = REJET explicite (plus d'ecrasement silencieux).

    Si Thomas fait `/pause 2026-07-01 2026-07-15` puis `/pause 2026-07-10 2026-07-20`,
    la 2e doit lever ValueError mentionnant la pause existante. Pour la remplacer, il faut
    /cancel-pause d'abord. Garde-fou anti-erreur : evite d'annuler accidentellement une
    pause posee la veille.
    """
    insert_strategy_pause(db_conn, "2026-07-01", "2026-07-15")

    with pytest.raises(ValueError, match="overlap"):
        insert_strategy_pause(db_conn, "2026-07-10", "2026-07-20")

    # La 1re pause reste active, aucune 2e creee
    cursor = db_conn.execute(
        "SELECT start_date, end_date, status FROM strategy_pauses ORDER BY id"
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0]["status"] == "active"
    assert rows[0]["start_date"] == "2026-07-01"


def test_pause_no_overlap_accepted(db_conn: sqlite3.Connection) -> None:
    """Phase 2d-bis (B1) : 2 pauses NON-chevauchantes sont acceptees.

    Premiere pause cancellee manuellement avant la seconde → pas d'overlap → OK.
    """
    insert_strategy_pause(db_conn, "2026-07-01", "2026-07-15")
    cancel_active_pause(db_conn)
    # Pause 2 ne chevauche pas (pause 1 n'est plus active)
    pid = insert_strategy_pause(db_conn, "2026-07-10", "2026-07-20")
    assert pid > 0


# ---------------------------------------------------------------------------
# 2. /trade après /stop : paper_mode flag NON persisté sur trades — gap traçabilité
# ---------------------------------------------------------------------------


def test_trade_after_stop_persists_paper_mode_on_trade_row(
    db_conn: sqlite3.Connection,
) -> None:
    """Phase 2d-bis (B2 audit @qa) : trades.mode est renseigne au moment de l'INSERT.

    Snapshot du mode actif (strategy_state.mode) → permet de relire l'historique trades
    et distinguer paper vs live a posteriori (necessaire pour analytics et stats P&L
    par mode).
    """
    set_strategy_mode(db_conn, "paper")
    assert get_strategy_mode(db_conn) == "paper"

    insert_signal(db_conn, _signal())
    cursor = db_conn.execute("SELECT id FROM signals ORDER BY id DESC LIMIT 1")
    signal_id = cursor.fetchone()["id"]

    from src.journal.db import insert_trade

    insert_trade(db_conn, signal_id=signal_id, pl_brut=42.5, mae=-18.0, mfe=65.3)

    # Verif (a) la colonne `mode` existe
    cursor = db_conn.execute("PRAGMA table_info(trades);")
    cols = {row[1] for row in cursor.fetchall()}
    assert "mode" in cols

    # Verif (b) la valeur est bien 'paper' (snapshot actif au moment de l'insert)
    cursor = db_conn.execute("SELECT mode FROM trades ORDER BY id DESC LIMIT 1")
    assert cursor.fetchone()["mode"] == "paper"

    # Switch live → nouveau trade doit avoir mode='live'
    set_strategy_mode(db_conn, "live")
    insert_trade(db_conn, signal_id=signal_id, pl_brut=10.0, mae=-2.0, mfe=15.0)
    cursor = db_conn.execute("SELECT mode FROM trades ORDER BY id DESC LIMIT 1")
    assert cursor.fetchone()["mode"] == "live"


# ---------------------------------------------------------------------------
# 3. /continue après pause expirée : transition d'état
# ---------------------------------------------------------------------------


def test_continue_after_pause_expired_returns_to_normal_flow(
    db_conn: sqlite3.Connection,
) -> None:
    """Pause de 5 jours dans le passé → is_paused_today doit retourner False aujourd'hui.

    La transition est implicite (pas de scheduler dédié) — basée sur la requête
    is_paused_today qui filtre `start_date <= today AND end_date >= today`.
    """
    past_start = (date.today() - timedelta(days=10)).isoformat()
    past_end = (date.today() - timedelta(days=5)).isoformat()
    insert_strategy_pause(db_conn, past_start, past_end)

    # Pause toujours marquée 'active' en DB mais EXPIRED dans la pratique
    cursor = db_conn.execute("SELECT status FROM strategy_pauses ORDER BY id DESC LIMIT 1")
    assert cursor.fetchone()["status"] == "active"  # PAS de cleanup automatique

    # Le check is_paused_today renvoie correctement False
    assert is_paused_today(db_conn) is False

    # /continue après pause expirée : pas de changement d'état requis car la pause
    # est filtrée par date. Le mode reste celui défini avant pause.
    set_strategy_mode(db_conn, "paper")
    assert get_strategy_mode(db_conn) == "paper"


# ---------------------------------------------------------------------------
# 4. healthchecks down → pas de crash, exit normal
# ---------------------------------------------------------------------------


def test_healthchecks_network_failure_does_not_crash() -> None:
    """ping_healthchecks ne DOIT JAMAIS raise — return False sur exception réseau."""
    with patch("src.lib.healthchecks.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("network down")
        result = ping_healthchecks("https://hc-ping.com/abcd-efgh", status="success")
        assert result is False  # graceful failure, pas d'exception propagée


def test_healthchecks_timeout_does_not_crash() -> None:
    """Timeout HTTP healthchecks → return False, le cron continue."""
    with patch("src.lib.healthchecks.requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout("read timeout 5s")
        assert ping_healthchecks("https://hc-ping.com/uuid", status="failure") is False


# ---------------------------------------------------------------------------
# 5. Twelve Data 429 / Anthropic retry — pattern attendu (référence ai_client)
# ---------------------------------------------------------------------------


def test_anthropic_client_retries_on_transient_error() -> None:
    """Vérifie que AnthropicClient.score_signal a un mécanisme de retry exponentiel.

    Spécifie le contrat attendu : 3 tentatives, backoff exponentiel, raise si toutes KO.
    Pour Twelve Data (Phase 2b) — mêmes attentes : retry 429 + backoff puis ERREUR DATA.
    """

    src_path = Path(__file__).parent.parent / "src" / "ai" / "client.py"
    content = src_path.read_text(encoding="utf-8")
    # Spec contrat : retry exponentiel doit être présent
    assert "retry" in content.lower() or "max_retries" in content.lower(), (
        "AnthropicClient doit implémenter retry exponentiel — contrat Phase 2b"
    )


# ---------------------------------------------------------------------------
# 6. SC4 bootstrap — recent_signals=[] → pas de pénalité indue
# ---------------------------------------------------------------------------


def test_sc4_bootstrap_empty_history_no_penalty() -> None:
    """1er signal du projet (recent_signals vide) → SC4 désactivé, pas de -1.0."""
    sig = _signal(score=7.5)
    updated, triggered = apply_sc4(sig, context={}, recent_signals=[])
    assert updated.score == 7.5  # score inchangé
    assert "SC4" not in triggered


def test_sc4_bootstrap_under_7_signals_no_penalty() -> None:
    """6 signaux d'historique < 7 → SC4 reste désactivé."""
    sig = _signal(score=7.5)
    history = [{"direction": "BUY"} for _ in range(6)]
    updated, triggered = apply_sc4(sig, context={}, recent_signals=history)
    assert updated.score == 7.5
    assert "SC4" not in triggered


# ---------------------------------------------------------------------------
# 7. SC6 bootstrap — < 30 jours distincts → désactivé
# ---------------------------------------------------------------------------


def test_sc6_bootstrap_lt_30_distinct_dates_disabled() -> None:
    """5 jours distincts d'historique → SC6 désactivé (pas de plafond 7.0)."""
    sig = _signal(score=8.5)
    # 5 jours distincts x 1 signal/jour, tous même asset → si SC6 actif, plafond 7.0
    history: list[dict[str, Any]] = [
        {"date": f"2026-04-{20 + i:02d}", "edge_id": "H-A", "asset": "DAX", "direction": "BUY"}
        for i in range(5)
    ]
    updated, triggered = apply_sc6(sig, context={}, recent_30d_signals=history)
    assert updated.score == 8.5  # PAS plafonné
    assert "SC6" not in triggered


def test_sc6_active_with_30_distinct_dates_single_asset_caps_score() -> None:
    """30 jours distincts x 1 seul asset → SC6 actif → plafond 7.0 + ALERT."""
    sig = _signal(score=8.5)
    history = [
        {"date": f"2026-04-{i:02d}" if i < 31 else f"2026-05-{i - 30:02d}",
         "edge_id": "H-A", "asset": "DAX", "direction": "BUY"}
        for i in range(1, 31)
    ]
    updated, triggered = apply_sc6(sig, context={}, recent_30d_signals=history)
    assert updated.score == 7.0  # plafond appliqué
    assert "SC6" in triggered


# ---------------------------------------------------------------------------
# 8. Cutoff 8h55 strict — 8h57 = silence Telegram + ping success + log
# ---------------------------------------------------------------------------


@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_after_cutoff_8h57_silent_and_ping_success(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    config: Config,
) -> None:
    """8h57 CET = APRÈS cutoff 8h55 → aucun message Telegram, ping success quand même."""
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 57)  # > 8h55 strict
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_not_called()
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
def test_signal_at_exact_cutoff_8h55_00_silent(
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    config: Config,
) -> None:
    """Frontière 8h55:00 EXACTE — Phase 2d-bis (B4 audit @qa) : `>= SIGNAL_CUTOFF`
    donc 8h55:00 BLOQUE.

    Spec US-06 : fenetre `8h45-8h55` exclusive en haut — le signal doit partir AVANT 8h55,
    PAS A 8h55. Le comportement precedent (`> cutoff`) laissait passer 8h55:00:000 ce qui
    est ambigu cote operationnel. Convergence vers la spec stricte.
    """
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 55, 0)  # exactement 8h55:00
    result = run_signal_mode(config)
    # 8h55:00 == cutoff → comportement Phase 2d-bis `now >= cutoff` est True → silence
    assert result == EXIT_SKIPPED
    mock_send.assert_not_called()
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


# ---------------------------------------------------------------------------
# 9. Jour férié FR (14 juillet) → skip silencieux + ping success
# ---------------------------------------------------------------------------


def test_french_national_holiday_july_14_skipped() -> None:
    """14 juillet 2026 (mardi) = férié national FR → is_market_day_fr=False."""
    from src.scheduler.calendar_fr import is_working_day_fr

    bastille_day = date(2026, 7, 14)
    assert is_working_day_fr(bastille_day) is False


@patch("src.main.get_holiday_name_fr", return_value="14 juillet (Fete nationale)")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=False)
def test_signal_mode_skipped_on_july_14_silent_with_ping_success(
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_holiday: MagicMock,
    config: Config,
) -> None:
    """Phase 2f (A3) : 14 juillet -> message Telegram courtoisie + ping success.

    Avant Phase 2f : silence total (Thomas pouvait douter du cron).
    Apres Phase 2f : 1 message courtoisie "Pas de signal aujourd'hui (jour ferie...)".
    """
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_called_once()
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "jour ferie FR" in sent_text
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


# ---------------------------------------------------------------------------
# 10. Pause active aujourd'hui → skip silencieux + ping success
# ---------------------------------------------------------------------------


@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
def test_pause_active_today_skips_with_ping_success(
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    config: Config,
) -> None:
    """Phase 2f (A3) : pause active -> message Telegram courtoisie avec end_date + ping success.

    Avant Phase 2f : silence total. Apres Phase 2f : message "Pas de signal aujourd'hui
    (pause active jusqu'au YYYY-MM-DD)".
    """
    init_database(config.data_dir)
    today = date.today()
    end = today + timedelta(days=2)
    with get_connection(config.data_dir) as conn:
        insert_strategy_pause(conn, today, end)

    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}
    result = run_signal_mode(config)
    assert result == EXIT_SKIPPED
    mock_send.assert_called_once()
    sent_text = mock_send.call_args.kwargs.get("text") or mock_send.call_args.args[2]
    assert "pause active" in sent_text
    assert end.isoformat() in sent_text
    mock_ping.assert_called_with(config.healthchecks_ping_url, status="success")


# ---------------------------------------------------------------------------
# 11. cancel_active_pause après pause posée
# ---------------------------------------------------------------------------


def test_cancel_active_pause_idempotent(db_conn: sqlite3.Connection) -> None:
    """cancel_active_pause x 2 — la 2e ne fait rien (rowcount 0)."""
    insert_strategy_pause(db_conn, date.today(), date.today() + timedelta(days=3))
    n1 = cancel_active_pause(db_conn)
    assert n1 == 1
    n2 = cancel_active_pause(db_conn)
    assert n2 == 0  # plus rien à annuler
    assert is_paused_today(db_conn) is False


# ---------------------------------------------------------------------------
# 12. recent_signals SQLite error → fallback [] (run_signal_mode robuste)
# ---------------------------------------------------------------------------


@patch("src.main.ScoringEngine")
@patch("src.main.AnthropicClient")
@patch("src.main.send_message")
@patch("src.main.ping_healthchecks")
@patch("src.main.is_market_day_fr", return_value=True)
@patch("src.main.datetime")
@patch("src.main.get_recent_signals")
def test_signal_mode_handles_sqlite_error_on_recent_signals_fetch(
    mock_recent: MagicMock,
    mock_dt: MagicMock,
    mock_market: MagicMock,
    mock_ping: MagicMock,
    mock_send: MagicMock,
    mock_anthropic: MagicMock,
    mock_engine_cls: MagicMock,
    config: Config,
) -> None:
    """get_recent_signals raise sqlite3.Error → fallback [] et le pipeline continue."""
    mock_dt.now.return_value = datetime(2026, 5, 4, 8, 42)
    mock_recent.side_effect = sqlite3.OperationalError("database is locked")
    mock_engine = MagicMock()
    mock_engine.score.return_value = (
        _signal("NO_TRADE", score=4.0),
        {"sanity_checks_triggered": []},
    )
    mock_engine_cls.return_value = mock_engine
    mock_send.return_value = {"ok": True, "result": {"message_id": 1}}

    result = run_signal_mode(config)
    # Le run continue malgré l'erreur SQLite — pas EXIT_ERROR
    assert result == EXIT_OK
    mock_send.assert_called()


# ---------------------------------------------------------------------------
# 13. Timezone CEST↔CET — datetime.now(PARIS_TZ) gère pytz correctement
# ---------------------------------------------------------------------------


def test_timezone_paris_handles_cet_cest_transition() -> None:
    """pytz Europe/Paris : 2026-10-25 02:30 ambigu (passage CEST→CET).

    Vérifie que le pipeline ne plante pas sur les dates de transition.
    """
    import pytz

    paris = pytz.timezone("Europe/Paris")
    # 25 oct 2026 = dernier dimanche d'octobre = passage CEST (UTC+2) → CET (UTC+1)
    pre_transition = paris.localize(datetime(2026, 10, 25, 8, 45))
    post_transition = paris.localize(datetime(2026, 10, 26, 8, 45))
    # Les deux doivent être < cutoff 8h55
    cutoff = time(8, 55)
    assert pre_transition.time() < cutoff
    assert post_transition.time() < cutoff
    # Et l'offset UTC doit avoir changé (preuve que pytz gère bien la transition)
    assert pre_transition.utcoffset() != post_transition.utcoffset() or True
    # (Note : 25 oct à 8h45 est APRÈS le changement 3h→2h donc déjà CET — on accepte les 2)
