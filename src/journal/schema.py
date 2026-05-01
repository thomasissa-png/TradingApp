"""DDL des 6 tables SQLite (idempotent — CREATE TABLE IF NOT EXISTS).

Source de verite :
- `signals`, `trades`, index : docs/analytics/kpi-framework.md §4
- `journal_weeks` : functional-specs.md US-09
- `strategy_decisions` : functional-specs.md US-10/US-11
- `strategy_pauses` : functional-specs.md US-12
- `strategy_state` + `rnd_results` : kpi-framework.md §7 signal n°6 (J+45 stop-loss)

Toute migration future DOIT respecter le pattern ALTER TABLE ADD COLUMN IF NOT EXISTS
(cf agent fullstack — section "Migrations SQL idempotentes").
"""

from __future__ import annotations

# ---------- Tables principales (signals / trades) ----------

DDL_SIGNALS = """
CREATE TABLE IF NOT EXISTS signals (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    date                    DATE NOT NULL,
    hour_calc               TIME NOT NULL,
    asset                   TEXT NOT NULL,
    direction               TEXT NOT NULL CHECK (direction IN ('BUY','SELL','NO_TRADE')),
    entry                   REAL,
    sl                      REAL,
    tp                      REAL,
    score                   REAL,
    scoring_model_version   TEXT NOT NULL,
    prompt_version          TEXT NOT NULL,
    model_used              TEXT NOT NULL,
    sanity_check_failed     TEXT NULL,
    backtest_ref            TEXT,
    no_trade_reason         TEXT,
    raison                  TEXT NULL,
    ALERT_flag              TEXT NULL,
    sent_to_telegram        INTEGER NOT NULL DEFAULT 0,
    telegram_msg_id         INTEGER,
    hour_sent               TIME,
    latency_total_ms        INTEGER,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DDL_TRADES = """
CREATE TABLE IF NOT EXISTS trades (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id               INTEGER NOT NULL REFERENCES signals(id),
    executed                INTEGER NOT NULL DEFAULT 0,
    entry_real              REAL,
    exit_real               REAL,
    quantity                INTEGER,
    exit_reason             TEXT CHECK (exit_reason IN ('TP','SL','TIMEOUT','MANUAL','KNOCKOUT')),
    exit_date               TIMESTAMP,
    pnl_brut                REAL,
    frais_bd                REAL DEFAULT 0.99,
    frais_bd_vente          REAL DEFAULT 0.99,
    spread_emetteur         REAL,
    pnl_net_avant_pfu       REAL,
    pfu_year_estimate       REAL,
    mae                     REAL,
    mfe                     REAL,
    notes                   TEXT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ---------- Tables de gouvernance strategie ----------

DDL_JOURNAL_WEEKS = """
CREATE TABLE IF NOT EXISTS journal_weeks (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start              DATE NOT NULL,
    week_end                DATE NOT NULL,
    journal_week_sent_at    DATETIME,
    statut                  TEXT,
    UNIQUE(week_start, week_end)
);
"""

DDL_STRATEGY_DECISIONS = """
CREATE TABLE IF NOT EXISTS strategy_decisions (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    month                   TEXT NOT NULL,
    decision                TEXT NOT NULL CHECK (decision IN ('continue','stop')),
    decided_at              DATETIME NOT NULL,
    nb_criteres_ko          INTEGER NOT NULL DEFAULT 0,
    confirmation_step       INTEGER NOT NULL DEFAULT 1,
    is_active               INTEGER NOT NULL DEFAULT 1,
    UNIQUE(month, decision)
);
"""

DDL_STRATEGY_PAUSES = """
CREATE TABLE IF NOT EXISTS strategy_pauses (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date              TEXT NOT NULL,
    end_date                TEXT NOT NULL,
    requested_at            DATETIME NOT NULL,
    status                  TEXT NOT NULL CHECK (status IN ('active','expired','cancelled')),
    reminder_sent           DATETIME NULL
);
"""

DDL_STRATEGY_STATE = """
CREATE TABLE IF NOT EXISTS strategy_state (
    id                              INTEGER PRIMARY KEY CHECK (id = 1),
    rnd_start_date                  DATE,
    stop_loss_rnd_triggered         INTEGER NOT NULL DEFAULT 0,
    stop_loss_rnd_triggered_at      TIMESTAMP,
    last_updated_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DDL_RND_RESULTS = """
CREATE TABLE IF NOT EXISTS rnd_results (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_id                 TEXT NOT NULL,
    pre_backtest_passed     INTEGER NOT NULL DEFAULT 0,
    tested_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes                   TEXT
);
"""

# ---------- Index ----------

DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(date);",
    "CREATE INDEX IF NOT EXISTS idx_signals_asset ON signals(asset);",
    "CREATE INDEX IF NOT EXISTS idx_trades_signal_id ON trades(signal_id);",
    "CREATE INDEX IF NOT EXISTS idx_trades_exit_date ON trades(exit_date);",
    "CREATE INDEX IF NOT EXISTS idx_strategy_pauses_status ON strategy_pauses(status);",
    "CREATE INDEX IF NOT EXISTS idx_strategy_decisions_month ON strategy_decisions(month);",
    "CREATE INDEX IF NOT EXISTS idx_journal_weeks_week_start ON journal_weeks(week_start);",
    "CREATE INDEX IF NOT EXISTS idx_rnd_results_edge_id ON rnd_results(edge_id);",
]


# Liste des tables critiques attendues apres init_database (utilise par les tests).
EXPECTED_TABLES: tuple[str, ...] = (
    "signals",
    "trades",
    "journal_weeks",
    "strategy_decisions",
    "strategy_pauses",
    "strategy_state",
    "rnd_results",
)


def get_all_ddls() -> list[str]:
    """Retourne tous les statements DDL dans l'ordre d'execution.

    Idempotent : peut etre rejoue sur une DB existante sans erreur.
    """
    return [
        DDL_SIGNALS,
        DDL_TRADES,
        DDL_JOURNAL_WEEKS,
        DDL_STRATEGY_DECISIONS,
        DDL_STRATEGY_PAUSES,
        DDL_STRATEGY_STATE,
        DDL_RND_RESULTS,
        *DDL_INDEXES,
    ]
