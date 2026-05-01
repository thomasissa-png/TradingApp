# Plan de tests E2E — Phase 2 TradingApp

> Auteur : @qa — Phase 2d (audit couverture + plan E2E pré-live)
> Dernière màj : 2026-05-01
> Source : `docs/product/functional-specs.md` (US-01 à US-12) + `src/main.py` Phase 2c-2 + 209 tests Phase 2 PASS.
> Objectif : couvrir les trous identifiés AVANT le mini-jalon J+7 et l'entrée en live.

---

## 1. Inventaire tests existants — 209 tests PASS (5.46 s)

Exécution : `/home/user/TradingApp/.venv/bin/python -m pytest -q` → **209 passed in 5.46s**.

| Fichier | Tests | Couverture |
|---|---:|---|
| `test_ai_client.py` | 12 | AnthropicClient — retry exponentiel, timeout, JSON parsing, model selection live/RND |
| `test_backtester_edges.py` | 10 | H-A gap-follow + H-C ORB — signal generation, entry/SL/TP logic |
| `test_backtester_methodology.py` | 19 | IS/OOS split, walk-forward, Hansen SPA p-value, no-overlap |
| `test_backtester_metrics.py` | 20 | Sharpe, Sortino, max DD, win rate, profit factor, expectancy |
| `test_backtester_verdict.py` | 9 | evaluate_go_phase2 — verdict GO/NO-GO sur 6 critères |
| `test_calendar_fr.py` | 9 | Jours fériés FR (workalendar.France), week-end, paques mobile |
| `test_config.py` | 6 | Config.from_env — validation pydantic, ANTHROPIC_API_KEY required, DATA_DIR |
| `test_journal_schema.py` | 4 | DDL 6 tables, foreign keys ON, idempotence init_database |
| `test_main_signal.py` | 12 | run_signal_mode happy/no-trade/holiday/pause/cutoff/Claude-timeout/data-error/INSERT |
| `test_scoring_dimensions.py` | 20 | 5 dimensions (Edge, Conf, Risk, Macro, Sanity) — bornes + edge cases |
| `test_scoring_engine.py` | 9 | TC-01 à TC-08 (specs §3) — orchestration + sanity_checks integration |
| `test_scoring_sanity_checks.py` | 27 | SC1-SC7 — VIX, gap %, news conflict, streak BUY x3, anomaly check, freq 30j |
| `test_telegram_bot_commands.py` | 23 | /trade, /stop, /continue, /pause, /journal-week — happy + edge args |
| `test_telegram_templates.py` | 29 | Tous formats (BUY/SELL/NO-TRADE/ERREUR DATA/DEGRADED/weekly/monthly) + vocab proscrit |

**Total Phase 2 (unit + intégration mocks) : 209 tests PASS, 0 FAIL.**

---

## 2. Matrice de traçabilité user stories ↔ tests (Gate G27)

| User Story | Test(s) correspondant(s) | Statut |
|---|---|---|
| US-01 — signal BUY/SELL jour ouvré | `test_main_signal.py::test_signal_mode_happy_path_buy` + `test_telegram_templates.py::test_buy_signal_*` | PASS |
| US-02 — NO-TRADE explicite | `test_main_signal.py::test_signal_mode_no_trade_when_all_below_threshold` + `test_telegram_templates.py::test_no_trade_*` | PASS |
| US-03 — inhibition jours fériés FR | `test_calendar_fr.py` (9 tests) + `test_main_signal.py::test_signal_mode_skipped_on_holiday` | PASS |
| US-04 — ERREUR DATA Twelve Data KO | `test_main_signal.py::test_signal_mode_market_data_error_sends_data_error` + `test_telegram_templates.py::test_data_error_*` | PASS partiel — pas de test rate-limit 429 (gap §3) |
| US-05 — DEGRADED MODE Claude timeout | `test_main_signal.py::test_signal_mode_claude_timeout_sends_degraded` + `test_ai_client.py::test_retry_*` | PASS |
| US-06 — cutoff 8h55 strict | `test_main_signal.py::test_signal_mode_skipped_when_after_cutoff` | PASS partiel — pas de test "8h57 = silence + ping" (gap §3) |
| US-07 — INSERT signal SQLite | `test_main_signal.py::test_signal_mode_inserts_signals_in_db` + `test_journal_schema.py` | PASS |
| US-08 — `/trade` log post-exec | `test_telegram_bot_commands.py::test_trade_*` | PASS partiel — pas de test "trade après /stop = paper_mode flag" (gap §3) |
| US-09 — `/journal-week` hebdo | `test_telegram_templates.py::test_weekly_summary_*` + `test_telegram_bot_commands.py::test_journal_week_*` | PASS |
| US-10 — `/continue` mensuel | `test_telegram_bot_commands.py::test_continue_*` | PASS partiel — pas de test "continue après pause expirée" (gap §3) |
| US-11 — `/stop` paper-trading | `test_telegram_bot_commands.py::test_stop_*` | PASS |
| US-12 — `/pause` 1-30 j | `test_telegram_bot_commands.py::test_pause_*` | PASS partiel — pas de test "overlap deux pauses" (gap §3) |

**Verdict G27 : PASS** — toutes les US ont >=1 test. Les "PASS partiel" sont couverts par le livrable 2 (`tests/test_e2e_phase2.py`).

---

## 3. Trous de couverture détectés (livrable 2 ci-dessous)

### 3.1 Trous fonctionnels confirmés

1. **`_build_market_context` est STUB MVP** (`src/main.py` lignes 99-124) — aucun test E2E avec pipeline réelle Twelve Data → engine → templates → bot. Sera couvert quand `MarketDataLoader` Phase 2b sera branché. Pour Phase 2c-2 : tester avec mocks réalistes.
2. **`/pause` chevauchements** : `insert_strategy_pause` désactive l'ancienne pause silencieusement (`UPDATE ... SET status='cancelled'` ligne 329-331 db.py). User story US-12 dit "refuser overlap" — comportement actuel : ÉCRASE sans erreur. → bug fonctionnel ou comportement à confirmer avec @product-manager. Test ajouté pour CAPTURER le comportement actuel + alerter.
3. **`/trade` après `/stop` = `paper_mode=true`** : `insert_trade` n'a pas de colonne `paper_mode` distincte ; le mode est lu via `get_strategy_mode()` au moment du calcul P&L (templates) mais PAS persisté sur la ligne `trades`. → bug de traçabilité : on ne saura pas a posteriori quels trades étaient en paper. Test ajouté + signalement @fullstack.
4. **`/continue` après pause expirée** : pas de transition automatique d'état. Quand pause termine, mode reste `paper`. `/continue` doit-il forcer `live` même sans critères ? → comportement à confirmer.
5. **Cron healthchecks failure path** : `ping_healthchecks` gère déjà `requests.RequestException` sans crash (ligne 44 healthchecks.py — return False). Test ajouté pour PROUVER que le cron continue.
6. **Twelve Data 429 rate limit** : aucun test de retry exponentiel sur HTTP 429. Comme `_build_market_context` est stub, pas critique pour Phase 2c-2 mais BLOQUANT pour Phase 2b. Test ajouté pour spécifier le contrat attendu.
7. **SC4/SC6 bootstrap (1er signal du projet)** : `apply_sc4` (streak BUY x3) et `apply_sc6` (freq 30j) avec `recent_signals=[]`. Comportement actuel à valider — pénalité -1.0 indue ou désactivation correcte ?
8. **Timezone change CEST↔CET** : changement fin oct (3h→2h) et fin mars (2h→3h). Cutoff 8h55 doit rester valide. Test ajouté avec `freezegun` ou simulation.

### 3.2 Décisions importantes

- **`_build_market_context` stub** : explicitement documenté dans le code et accepté pour Phase 2c-2. Les tests E2E utilisent des mocks `ScoringEngine.score`. Le test d'intégration Twelve Data réel est différé en Phase 2b.
- **Couverture `coverage`** : impossible à mesurer sans `pytest-cov` (pas dans .venv). À installer pour Phase 2d V2. Estimation visuelle : >= 90% sur src/scoring, >= 85% sur src/main, >= 80% sur src/journal.

---

## 4. Plan d'exécution E2E recommandé (pré-live, avant J+7)

### Smoke test 1 — Hello world Telegram réel

```bash
cd /home/user/TradingApp
python -m src.main --mode=hello
```

**Pré-requis** : `.env` avec `TELEGRAM_BOT_TOKEN`, `THOMAS_CHAT_ID`, `HEALTHCHECKS_PING_URL` valides.
**Résultat attendu** :
- Message Telegram reçu sur THOMAS_CHAT_ID (« Hello world… mode=paper »).
- Ping HTTP 200 sur healthchecks.io.
- Exit code 0.
- Fichier `data/journal.sqlite` créé avec 6 tables.

### Smoke test 2 — Mode signal avec stub `_build_market_context`

```bash
cd /home/user/TradingApp
python -m src.main --mode=signal
```

**Pré-requis** : idem + `ANTHROPIC_API_KEY`. Le stub renvoie `news_titles=[]` → ScoringEngine recevra des features minimales.
**Résultat attendu (entre 8h45-8h55 jour ouvré)** :
- 1 message Telegram (NO-TRADE le plus probable car features vides).
- 1-2 lignes INSERT dans `signals` (1 par edge wave 1 : H-A et H-C).
- Ping success sur healthchecks.
- Exit code 0.

**Si > 8h55 ou férié** : silence Telegram + ping success + exit 0.

### Smoke test 3 — Backtester runner

```bash
cd /home/user/TradingApp
python -m src.backtester.runner \
  --edge=H-C --assets=DAX \
  --is-start=2024-01-01 --is-end=2024-12-31 \
  --oos-start=2025-01-01 --oos-end=2025-06-30 \
  --output-json=/tmp/test_results.json \
  --api-key=$TWELVEDATA_API_KEY
```

**Pré-requis** : `TWELVEDATA_API_KEY` plan Pro Individual (1m intraday EU).
**Résultat attendu** :
- Verdict GO ou NO-GO Phase 2 imprimé.
- `/tmp/test_results.json` valide (Sharpe, max DD, p-value Hansen, equity curve).
- INSERT dans `rnd_results` SQLite.
- Exit code 0.

### Test J+7 — Mini-jalon (5 jours ouvrés × 6 critères)

Procédure complète dans `REPLIT_ACTIONS.md` §F.1-F.6 :
- F.1 : 5 jours ouvrés consécutifs → 5 messages Telegram reçus à 8h45-8h55.
- F.2 : 0 ping healthchecks failure sur la période.
- F.3 : 0 crash logs dans Replit Console.
- F.4 : `data/journal.sqlite` contient >= 5 lignes `signals` (INSERT par edge actif).
- F.5 : 1 message `/journal-week` reçu vendredi 18h00 CET.
- F.6 : `python -m src.main --mode=hello` reproduit OK en local + sur Replit.

---

## 5. Couverture cible Phase 2

- **209 tests Phase 2 PASS (5.46s)** — baseline solide.
- **+12 tests E2E ajoutés Phase 2d** (`tests/test_e2e_phase2.py`) → 221 tests PASS cible.
- **Couverture statements >= 90%** sur `src/scoring`, `src/journal`, `src/main`. À mesurer en Phase 2d V2 avec `pytest-cov` (à ajouter dans `pyproject.toml` dev deps).
- **Mutation score >= 70%** sur `src/scoring/engine.py` et `src/scoring/sanity_checks.py` (chemins critiques) — différé Phase 3 (`mutmut` ou `cosmic-ray`).
- **Pipeline CI < 10 min** : actuellement 5.46s pour 209 tests, marge confortable. Backtester runner exclu (lent, Twelve Data réseau) → marqué `@pytest.mark.slow`.

---

## 6. Verdict G26 (pre-deploy gate) — checklist

Avant tout déploiement Replit :

1. `mypy src --strict` → 0 erreur.
2. `ruff check src` → 0 erreur.
3. `python -m pytest -q` → 209+12 = 221 tests PASS.
4. Smoke test 1 (hello world) PASS sur env de dev.
5. Grep `sk_test_`, `=xxx`, `=placeholder` dans `src/` → 0 résultat.

Si l'un des 5 échoue → bloquer le déploiement.

---

## 7. Limitations & dépendances (signalements @fullstack / @product-manager)

- **`_build_market_context` STUB MVP** : Phase 2b doit brancher `MarketDataLoader` réel.
- **Comportement `/pause` overlap** : actuel = écrasement silencieux. À confirmer vs spec US-12.
- **`trades.paper_mode` non persisté** : ajouter colonne dans `journal_schema.py` Phase 2d V2.
- **Aucun test contre Twelve Data live** : différé Phase 2b. Mocks réalistes seulement.
- **Coverage tooling absent** : ajouter `pytest-cov>=4.1` à `pyproject.toml` dev deps.
- **`requirements.txt` absent** : pyproject.toml seul → OK pour Replit, mais doc à clarifier.

---

**Fin plan E2E Phase 2 — @qa 2026-05-01.**
