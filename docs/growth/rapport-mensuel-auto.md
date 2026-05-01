<!-- Version: 2026-05-01 — @growth Phase 4 — Rapport mensuel auto-généré TradingApp -->
# Rapport mensuel auto-généré — Spec @growth Phase 4

> **Résumé exécutif**
> - Spec du rapport mensuel envoyé automatiquement par le bot le 1er de chaque mois à 9h00 CET.
> - Format Telegram (cohérent avec le reste du bot). Trigger : cron Replit `--mode=monthly-report`.
> - Pas de "earned media" externe — outil 100 % perso. L'enjeu @growth est interne : communiquer
>   la performance au persona Thomas de façon lisible, actionnelle, sans bullshit.
> - KPI North Star : P&L net mensuel après frais et PFU 31,4 %.
> - Dépendances : kpi-framework.md (formules, 6 signaux d'arrêt, schéma SQLite), message-templates.md
>   §5 AUDIT-MENSUEL (template existant étendu), functional-specs.md US-10/11.

---

## 1. Contexte

### Pourquoi un rapport mensuel pour un outil perso ?

TradingApp n'a ni utilisateurs externes, ni budget marketing, ni canaux d'acquisition à piloter.
Les leviers @growth classiques (SEO, paid, earned media, referral) sont hors-scope.

Le seul "canal" qui compte ici est la **rétention de Thomas vis-à-vis de son propre outil** :
un Thomas qui ne comprend pas sa performance mensuelle abandonnera le bot ou, pire, continuera
à l'utiliser sans détecter un edge en train de se dégrader.

Le rapport mensuel remplit trois fonctions growth internes :

| Fonction | Mécanique |
|---|---|
| **Rétention** | Thomas reste engagé si la perf est visible et actionnelle |
| **Décision GO/NO-GO** | /continue ou /stop — contrôle explicite mensuel (user-flows.md F20) |
| **Audit edge** | Détection précoce dégradation win rate live vs backtest |

### Format et canal

Format **Telegram** — cohérent avec le reste du bot (push, pas de dashboard à ouvrir).
Ton : factuel, sans bullshit, conditionnel sur l'incertitude (brand-platform.md piliers 1-3).
Longueur cible : lisible en 60 secondes max (rapport mensuel ≠ signal quotidien).

### Trigger

Cron Replit `--mode=monthly-report`, schedule UTC `0 7 1 * *` (= 1er du mois à 9h00 CET
en CEST / 8h00 en CET — voir note §5 sur l'ambiguïté CET/CEST).

Thomas lit le rapport le matin du 1er, décide de `/continue` ou `/stop`, et la stratégie
du mois suivant est définie. Autonomie totale, sans relancer le bot manuellement.

### Signaux d'arrêt — rappel (source : kpi-framework.md §7)

Le rapport mensuel affiche le **statut des 6 signaux d'arrêt** définis dans kpi-framework.md :

| # | Condition | Source SQLite |
|---|---|---|
| 1 | Drawdown mensuel > 20 % capital dédié | `trades.pnl_net_avant_pfu` cumulé |
| 2 | 15 jours ouvrés consécutifs sans signal GO | `signals.direction = 'NO_TRADE'` streak |
| 3 | Win rate live < win rate backtest − 15 pts sur 3 mois | JOIN `signals` × `rnd_results` |
| 4 | Score confiance moyen live > score moyen backtest (euphorie) | `AVG(signals.score)` vs `backtest_avg_score` |
| 5 | Position overnight non clôturée après 18h00 CET | `trades.exit_date` NULL après cutoff |
| 6 | J+45 R&D sans hypothèse wave 1 validée | `strategy_state.stop_loss_rnd_triggered` |

---

## 2. Template du rapport mensuel — Telegram

Le template étend AUDIT-MENSUEL de `message-templates.md` §5 en ajoutant :
- Les 6 signaux d'arrêt (kpi-framework.md §7)
- Le top 3 / bottom 3 trades du mois
- Les critères GO/NO-GO continue chiffrés (kpi-framework.md §6)
- La mention `[MODE PAPER]` en en-tête si `strategy_state.mode = 'paper'`
- Un bloc d'alerte P0 si un signal d'arrêt est actif

### Template complet

```
📊 Rapport mensuel TradingApp — {MOIS} {YYYY}
{MODE_PAPER_LINE}
────────────────────────────────
💰 P&L NET MENSUEL : {pl_net} €
   (frais BD : −{frais_bd_total} € | spread : −{spread_total} € | PFU 31,4 % estimé YTD : −{pfu_ytd_estimate} €)

📈 MÉTRIQUES DU MOIS
Signaux envoyés : {nb_signaux}  |  NO-TRADE : {nb_no_trade} ({pct_no_trade} % — vertu)
Trades exécutés : {nb_trades}  |  Win rate : {win_rate} %
Drawdown max mensuel : {drawdown_max} %  (seuil BLOQUANT : 20 %)
Profit Factor : {profit_factor}
Score confiance moyen : {avg_score}/10
Sharpe glissant 3 mois : {sharpe_3m}

🔁 COHÉRENCE BACKTEST
Win rate live : {win_rate} %  |  Backtest réf. : {win_rate_backtest} %
Écart : {ecart_wr} pts  {ALERTE_ECART_WR}

────────────────────────────────
🚦 SIGNAUX D'ARRÊT
{SIGNAL_1_STATUS}  n°1 — Drawdown mensuel > 20 %
{SIGNAL_2_STATUS}  n°2 — 15 jours ouvrés sans signal GO
{SIGNAL_3_STATUS}  n°3 — Win rate live < backtest − 15 pts (3 mois)
{SIGNAL_4_STATUS}  n°4 — Euphorie (score live > score backtest)
{SIGNAL_5_STATUS}  n°5 — Position overnight non clôturée
{SIGNAL_6_STATUS}  n°6 — J+45 R&D sans hypothèse validée

────────────────────────────────
🏆 TOP 3 TRADES DU MOIS
1. {trade1_asset} — P&L net : {trade1_pnl} €  |  Réf. {trade1_ref}  |  {trade1_raison}
2. {trade2_asset} — P&L net : {trade2_pnl} €  |  Réf. {trade2_ref}  |  {trade2_raison}
3. {trade3_asset} — P&L net : {trade3_pnl} €  |  Réf. {trade3_ref}  |  {trade3_raison}

📉 BOTTOM 3 TRADES DU MOIS
1. {loss1_asset} — P&L net : {loss1_pnl} €  |  Réf. {loss1_ref}  |  Cause : {loss1_cause}
2. {loss2_asset} — P&L net : {loss2_pnl} €  |  Réf. {loss2_ref}  |  Cause : {loss2_cause}
3. {loss3_asset} — P&L net : {loss3_pnl} €  |  Réf. {loss3_ref}  |  Cause : {loss3_cause}

────────────────────────────────
✅ CRITÈRES GO/NO-GO CONTINUE
{C1_STATUS}  P&L net > 0 € sur le mois
{C2_STATUS}  Drawdown max < 20 % du capital
{C3_STATUS}  Écart win rate live vs backtest < 15 pts
{C4_STATUS}  Profit Factor ≥ 1,5 sur le mois
{C5_STATUS}  P&L net > 0 € sur ≥ 3 mois consécutifs (cible 12 mois)

Score GO/NO-GO : {nb_pass}/5 critères PASS

────────────────────────────────
📋 DÉCISION REQUISE
→ /continue  pour valider le mois suivant
→ /stop      pour suspendre les signaux (retour paper-trading)

{ALERTE_P0_BLOCK}
```

### Légende des variables conditionnelles

| Variable | Valeur PASS | Valeur FAIL |
|---|---|---|
| `{MODE_PAPER_LINE}` | *(vide)* | `[MODE PAPER]` |
| `{SIGNAL_X_STATUS}` | `✅ OK` | `🔴 ACTIF` |
| `{C1_STATUS}` à `{C5_STATUS}` | `✅ PASS` | `❌ FAIL` |
| `{ALERTE_ECART_WR}` | *(vide si écart < 15 pts)* | `⚠️ ALERTE — écart > 15 pts` |
| `{ALERTE_P0_BLOCK}` | *(vide si aucun signal actif)* | voir bloc ci-dessous |

### Bloc alerte P0 (inséré si au moins 1 signal d'arrêt actif)

```
⚠️ ATTENTION — Signal d'arrêt n°{X} actif depuis {date_declenchement}.
Intervention requise avant de taper /continue.
```

### Règles de formatage Telegram

- Parse mode : HTML (cohérent Phase 2d-bis décision @fullstack — Markdown trop fragile)
- `&` → `&amp;` dans les champs free-form (asset, raison, cause)
- Longueur totale : ≤ 4096 caractères (limite Telegram message)
- 1 emoji par section max (📊 en-tête, 💰 P&L, 📈 métriques, 🚦 signaux, 🏆 top, 📉 bottom, ✅ critères)
- Si top 3 / bottom 3 contient moins de 3 trades (mois avec peu de trades) : afficher seulement
  les trades disponibles. Si 0 trades : `Aucun trade exécuté ce mois.`

---

## 3. Logique de calcul — SQL

Toutes les requêtes s'exécutent sur `data/journal.sqlite` (schéma kpi-framework.md §4).
Le paramètre `:month` est au format `'YYYY-MM'` (ex : `'2026-04'`).

### 3.1 P&L net mensuel (North Star)

```sql
-- P&L brut, frais BD, spread, P&L net avant PFU
SELECT
    SUM(t.pnl_brut)                                   AS pl_brut,
    SUM(t.frais_bd + t.frais_bd_vente)                AS frais_bd_total,
    SUM(COALESCE(t.spread_emetteur, 0))               AS spread_total,
    SUM(t.pnl_net_avant_pfu)                          AS pl_net_avant_pfu
FROM trades t
JOIN signals s ON t.signal_id = s.id
WHERE t.executed = 1
  AND strftime('%Y-%m', t.exit_date) = :month;

-- PFU YTD estimé (cumulatif depuis début d'année — charge fiscale provisionnée)
SELECT SUM(t.pfu_year_estimate) AS pfu_ytd_estimate
FROM trades t
WHERE t.executed = 1
  AND strftime('%Y', t.exit_date) = :year;

-- P&L net après PFU mensuel estimé (approximation pilotage)
-- Formule : pl_net_avant_pfu - (pfu_ytd_estimate / 12)
-- Note : le PFU réel est annuel (formulaire 2074), ceci est une estimation mensuelle de pilotage
--        conformément à kpi-framework.md §1 Note fiscale critique (L001 @legal)
```

### 3.2 Drawdown mensuel max

```sql
-- Vue equity curve mensuelle (créer si inexistante)
-- Equity = cumul pnl_net_avant_pfu dans l'ordre chronologique des exits
CREATE VIEW IF NOT EXISTS equity_curve_monthly AS
SELECT
    t.exit_date,
    strftime('%Y-%m', t.exit_date) AS month,
    SUM(t.pnl_net_avant_pfu) OVER (
        ORDER BY t.exit_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS equity_cumul
FROM trades t
WHERE t.executed = 1;

-- Drawdown max du mois (pic → creux)
SELECT
    MAX(equity_cumul) - MIN(equity_cumul) AS drawdown_abs,
    CASE WHEN MAX(equity_cumul) > 0
         THEN (MAX(equity_cumul) - MIN(equity_cumul)) / MAX(equity_cumul) * 100
         ELSE 0 END                        AS drawdown_pct
FROM equity_curve_monthly
WHERE month = :month;
```

### 3.3 Métriques mensuelles (vue trades_stats_monthly)

```sql
-- Créer la vue si inexistante
CREATE VIEW IF NOT EXISTS trades_stats_monthly AS
SELECT
    strftime('%Y-%m', t.exit_date)              AS month,
    COUNT(*)                                    AS nb_trades,
    SUM(CASE WHEN t.pnl_net_avant_pfu > 0 THEN 1 ELSE 0 END) AS nb_gagnants,
    ROUND(
        100.0 * SUM(CASE WHEN t.pnl_net_avant_pfu > 0 THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                           AS win_rate,
    ROUND(
        SUM(CASE WHEN t.pnl_net_avant_pfu > 0 THEN t.pnl_net_avant_pfu ELSE 0 END)
        / NULLIF(ABS(SUM(CASE WHEN t.pnl_net_avant_pfu <= 0 THEN t.pnl_net_avant_pfu ELSE 0 END)), 0),
        2
    )                                           AS profit_factor
FROM trades t
WHERE t.executed = 1
GROUP BY month;

-- Requête mensuelle
SELECT win_rate, profit_factor, nb_trades
FROM trades_stats_monthly
WHERE month = :month;
```

### 3.4 Signaux du mois (no-trade, score moyen)

```sql
SELECT
    COUNT(*)                                              AS nb_signaux,
    SUM(CASE WHEN direction = 'NO_TRADE' THEN 1 ELSE 0 END) AS nb_no_trade,
    ROUND(100.0 * SUM(CASE WHEN direction = 'NO_TRADE' THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                          AS pct_no_trade,
    ROUND(AVG(CASE WHEN direction != 'NO_TRADE' THEN score ELSE NULL END), 2)
                                                          AS avg_score
FROM signals
WHERE strftime('%Y-%m', date) = :month;
```

### 3.5 Cohérence backtest — win rate live vs backtest

```sql
-- Win rate backtest de référence (depuis rnd_results, edge retenu)
-- rnd_results.win_rate = win rate OOS de l'edge (alimenté par backtester Phase 2b)
SELECT win_rate AS win_rate_backtest
FROM rnd_results
WHERE pre_backtest_passed = 1
ORDER BY tested_at DESC
LIMIT 1;

-- Calcul de l'écart
-- ecart_wr = win_rate_live - win_rate_backtest
-- Signal d'arrêt n°3 : ABS(ecart_wr) > 15 pts sur 3 mois glissants
SELECT
    ROUND(AVG(tsm.win_rate), 1) AS win_rate_live_3m,
    rr.win_rate                  AS win_rate_backtest
FROM trades_stats_monthly tsm, (
    SELECT win_rate FROM rnd_results WHERE pre_backtest_passed = 1 ORDER BY tested_at DESC LIMIT 1
) rr
WHERE tsm.month IN (
    strftime('%Y-%m', date('now', 'start of month', '-1 month')),
    strftime('%Y-%m', date('now', 'start of month', '-2 month')),
    strftime('%Y-%m', date('now', 'start of month', '-3 month'))
);
```

### 3.6 Top 3 / Bottom 3 trades

```sql
-- Top 3 — meilleurs trades du mois
SELECT
    s.asset,
    t.pnl_net_avant_pfu AS pnl_net,
    s.backtest_ref       AS ref,
    s.direction,
    t.exit_reason
FROM trades t
JOIN signals s ON t.signal_id = s.id
WHERE t.executed = 1
  AND strftime('%Y-%m', t.exit_date) = :month
ORDER BY t.pnl_net_avant_pfu DESC
LIMIT 3;

-- Bottom 3 — pires trades du mois
SELECT
    s.asset,
    t.pnl_net_avant_pfu AS pnl_net,
    s.backtest_ref       AS ref,
    t.exit_reason        AS cause
FROM trades t
JOIN signals s ON t.signal_id = s.id
WHERE t.executed = 1
  AND strftime('%Y-%m', t.exit_date) = :month
ORDER BY t.pnl_net_avant_pfu ASC
LIMIT 3;
```

### 3.7 Sharpe glissant 3 mois

```sql
-- Rendement moyen et écart-type sur 3 mois glissants
-- Sharpe = (rendement_moyen - taux_sans_risque_journalier) / ecart_type * sqrt(252)
-- Taux sans risque : [HYPOTHÈSE : OAT 10 ans France ~3,0 % — kpi-framework.md §2.4]
-- Le calcul Python est recommandé pour sqrt(252) — la requête SQL fournit les inputs

SELECT
    AVG(t.pnl_net_avant_pfu)                          AS rendement_moyen,
    -- SQLite n'a pas STDDEV natif — calculé côté Python depuis cette liste
    GROUP_CONCAT(t.pnl_net_avant_pfu, ',')            AS pnl_serie
FROM trades t
WHERE t.executed = 1
  AND t.exit_date >= date('now', 'start of month', '-3 month');
```

### 3.8 Statut signaux d'arrêt (batch mensuel)

```sql
-- Signal n°1 : drawdown > 20 %  → calculé depuis drawdown_pct (§3.2)

-- Signal n°2 : streak NO_TRADE ≥ 15 jours ouvrés
-- (calculé en Python : requête la série direction + date, compte le streak max)
SELECT date, direction FROM signals
WHERE strftime('%Y-%m', date) = :month
ORDER BY date ASC;

-- Signal n°3 : win rate live vs backtest sur 3 mois (§3.5)

-- Signal n°4 : euphorie — score live > score backtest
SELECT AVG(score) AS avg_score_live
FROM signals
WHERE direction != 'NO_TRADE'
  AND strftime('%Y-%m', date) = :month;
-- Comparer à backtest_avg_score depuis rnd_results (colonne à ajouter si absente)

-- Signal n°5 : position overnight
SELECT COUNT(*) AS overnight_count
FROM trades t
JOIN signals s ON t.signal_id = s.id
WHERE t.executed = 1
  AND t.exit_date IS NULL
  AND time(s.hour_sent) >= '18:00:00'
  AND DATE(s.date) = :check_date;

-- Signal n°6 : J+45 R&D
SELECT stop_loss_rnd_triggered, rnd_start_date
FROM strategy_state
LIMIT 1;
```

---

## 4. Déclenchement et idempotence

### 4.1 Trigger

- **Cron Replit** : schedule UTC `0 7 1 * *` = 1er du mois à 07h00 UTC.
- En CEST (été, avril-octobre) : 07h00 UTC = 09h00 CEST. Correct.
- En CET (hiver, novembre-mars) : 07h00 UTC = 08h00 CET. Envoi à 8h00 au lieu de 9h00.
- **Décision** : accepter ce delta 1h en hiver (Thomas est déjà levé, rapport mensuel ≠ signal
  temps-réel). Cohérent avec le cron signal existant (`40 6,7 * * 1-5`) qui applique la même
  logique TZ-aware via `src/cron.py` wrapper `TZ=Europe/Paris`.
- Si le 1er du mois tombe un week-end ou un jour férié FR (ex : 1er janvier, 1er mai),
  `calendar_fr.py` détecte le cas → le rapport est envoyé le **premier jour ouvré suivant**.

### 4.2 Idempotence — table `monthly_reports`

Créer la table SQLite dans `data/journal.sqlite` (via `src/journal/schema.py`) :

```sql
CREATE TABLE IF NOT EXISTS monthly_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    month           TEXT NOT NULL UNIQUE,       -- format YYYY-MM
    sent_at         TIMESTAMP NOT NULL,         -- heure d'envoi effective CET
    telegram_msg_id INTEGER,                    -- message_id retourné par Telegram
    pl_net          REAL,                       -- P&L net snapshot au moment de l'envoi
    nb_criteres_ko  INTEGER DEFAULT 0,          -- nb critères GO/NO-GO en FAIL
    signal_arret_actif INTEGER DEFAULT 0,       -- 1 si au moins 1 signal actif
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_monthly_reports_month ON monthly_reports(month);
```

**Logique idempotence** : au démarrage du mode `monthly-report`, vérifier :

```python
existing = conn.execute(
    "SELECT id FROM monthly_reports WHERE month = ?", (month_str,)
).fetchone()
if existing:
    logger.info("Rapport mensuel déjà envoyé pour %s — skip", month_str)
    return  # sortie silencieuse
```

Cela garantit qu'un retry Replit ou un re-déclenchement manuel ne génère pas un doublon.

### 4.3 Alerte P0 si signal d'arrêt actif

Si au moins un signal d'arrêt est actif (signaux n°1 à n°6), le rapport inclut un bloc
d'alerte P0 **en plus** du rapport standard (pas à la place). Thomas voit toujours la
performance complète + l'alerte en contexte.

```python
# Pseudo-code Python
active_signals = [i for i, active in enumerate(signal_statuses, 1) if active]
if active_signals:
    alert_block = "\n".join([
        f"⚠️ ATTENTION — Signal d'arrêt n°{i} actif depuis {signal_dates[i]}."
        for i in active_signals
    ])
    alert_block += "\nIntervention requise avant de taper /continue."
else:
    alert_block = ""
```

### 4.4 Mode paper

Si `strategy_state.mode = 'paper'` au moment de l'envoi, la 2e ligne du rapport affiche :
`[MODE PAPER] — Tous les trades de ce mois sont simulés.`

Les calculs P&L restent les mêmes (journal en paper inclut les trades simulés avec les
mêmes colonnes que le live — `trades.mode = 'paper'` colonne ajoutée en Phase 2d-bis).

### 4.5 Mois sans trades

Si aucun trade exécuté dans le mois (phase R&D pure, paper-trading bloqué, ou mois
complet en NO-TRADE) :
- Les métriques affichent `—` ou `0` selon le cas
- Le bloc top 3 / bottom 3 affiche : `Aucun trade exécuté ce mois.`
- Les critères GO/NO-GO : C1 FAIL (P&L net = 0 € non positif), C4 FAIL (PF non calculable)
- La décision `/continue` reste disponible (Thomas peut choisir de continuer malgré 0 trade)

---

## 5. Implémentation — @fullstack Phase 5

### 5.1 Nouveau mode CLI

Ajouter dans `src/main.py` :

```python
# Entrée CLI — cohérent avec les modes existants (hello / live / paper)
if args.mode == "monthly-report":
    run_monthly_report_mode()
```

Signature du helper principal :

```python
def generate_monthly_report(month: str) -> str:
    """
    Génère le texte Telegram du rapport mensuel pour le mois donné.

    Args:
        month: format 'YYYY-MM' (ex : '2026-04')

    Returns:
        Texte HTML Telegram prêt à envoyer via send_message(parse_mode='HTML').

    Raises:
        ValueError: si month n'est pas au format YYYY-MM.
    """
    ...

def run_monthly_report_mode() -> None:
    """
    Point d'entrée du mode --mode=monthly-report.
    1. Calcule le mois précédent (date('now') - 1 mois).
    2. Vérifie idempotence (table monthly_reports).
    3. Génère le rapport via generate_monthly_report().
    4. Envoie sur Telegram.
    5. INSERT dans monthly_reports.
    6. Ping healthchecks.io (URL dédiée monthly-report).
    """
    ...
```

### 5.2 Nouveau cron Replit

Ajouter dans `REPLIT_ACTIONS.md` (section C — Cron Deployments) :

```
Cron 3 : tradingapp-cron-monthly
  Schedule : 0 7 1 * *   (UTC — 1er du mois 09h00 CEST / 08h00 CET)
  Command  : python -m src.main --mode=monthly-report
  Note     : si le 1er est férié FR → calendar_fr.py renvoie is_trading_day=False
             → run_monthly_report_mode() envoie quand même le rapport (rapport ≠ signal).
             Pas de skip sur jours fériés pour le rapport mensuel.
```

**Rappel des 3 crons Replit après Phase 5 :**

| Cron | Schedule UTC | Mode | Condition d'exécution |
|---|---|---|---|
| `tradingapp-cron-signal` | `40 6,7 * * 1-5` | `live` ou `paper` | Jours ouvrés FR uniquement |
| `tradingapp-cron-weekly` | `0 16 * * 5` | `journal-week` | Vendredi 18h00 CET |
| `tradingapp-cron-monthly` | `0 7 1 * *` | `monthly-report` | 1er du mois, **toujours** |

### 5.3 Healthchecks.io — URL dédiée

Créer un check séparé sur healthchecks.io pour le cron mensuel (différent du check signal
quotidien). Ajouter la variable d'environnement dans Replit Secrets :

```
HEALTHCHECKS_MONTHLY_URL=https://hc-ping.com/{uuid-monthly}
```

Timeout healthchecks : 48h (le check est mensuel, une fenêtre large est appropriée).

### 5.4 Vues SQLite à créer

Les vues suivantes doivent être créées dans `src/journal/schema.py` (idempotentes) :

```python
VIEWS_DDL = [
    """
    CREATE VIEW IF NOT EXISTS equity_curve_monthly AS
    SELECT t.exit_date, strftime('%Y-%m', t.exit_date) AS month,
           SUM(t.pnl_net_avant_pfu) OVER (ORDER BY t.exit_date
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS equity_cumul
    FROM trades t WHERE t.executed = 1
    """,
    """
    CREATE VIEW IF NOT EXISTS trades_stats_monthly AS
    SELECT strftime('%Y-%m', t.exit_date) AS month,
           COUNT(*) AS nb_trades,
           SUM(CASE WHEN t.pnl_net_avant_pfu > 0 THEN 1 ELSE 0 END) AS nb_gagnants,
           ROUND(100.0 * SUM(CASE WHEN t.pnl_net_avant_pfu > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_rate,
           ROUND(SUM(CASE WHEN t.pnl_net_avant_pfu > 0 THEN t.pnl_net_avant_pfu ELSE 0 END) /
                 NULLIF(ABS(SUM(CASE WHEN t.pnl_net_avant_pfu <= 0 THEN t.pnl_net_avant_pfu ELSE 0 END)), 0), 2)
                 AS profit_factor
    FROM trades t WHERE t.executed = 1
    GROUP BY month
    """,
]
```

### 5.5 Modules à créer ou étendre

| Fichier | Action | Contenu |
|---|---|---|
| `src/journal/schema.py` | **Étendre** | Ajouter table `monthly_reports` + 2 vues DDL |
| `src/journal/db.py` | **Étendre** | Helpers : `get_monthly_stats()`, `get_top_bottom_trades()`, `get_signal_arret_statuses()`, `insert_monthly_report()`, `get_monthly_report_sent()` |
| `src/reports/monthly.py` | **Créer** | `generate_monthly_report(month, conn) -> str` + logique calcul Sharpe Python |
| `src/telegram/templates.py` | **Étendre** | `format_monthly_report(data: MonthlyReportData) -> str` (HTML) |
| `src/main.py` | **Étendre** | `run_monthly_report_mode()` + branche `monthly-report` dans dispatch |
| `tests/test_monthly_report.py` | **Créer** | ≥ 15 tests : rapport standard, mode paper, 0 trades, signal P0 actif, idempotence, top/bottom 3 avec N < 3 trades |

---

## Auto-évaluation gates

| Gate | Intitulé | Statut | Justification |
|---|---|---|---|
| G1 | Cohérence avec project-context.md | PASS | Persona Thomas, canal Telegram, capital 20-30k€, Replit Cron, Python pur — tous alignés sur project-context.md §Identité et §Stack |
| G3 | Zéro invention de données | PASS | Aucun chiffre de performance inventé. Les exemples de valeurs dans le template sont des placeholders `{variable}`. Le taux PFU 31,4 % est sourcé kpi-framework.md §1 (L001 @legal). |
| G6 | KPI North Star explicite + PFU 31,4 % cité | PASS | §2 template : `P&L NET MENSUEL : {pl_net} €` en tête, avec décomposition frais BD + spread + `PFU 31,4 % estimé YTD`. §3.1 formule SQL complète avec note fiscale. |
| G7 | Cohérent kpi-framework.md + functional-specs US-10/11 | PASS | Les 6 signaux d'arrêt de §1 sont copiés depuis kpi-framework.md §7. Les commandes /continue et /stop renvoient explicitement aux US-10/11 functional-specs et à user-flows.md F20. Les vues SQLite sont cohérentes avec le schéma kpi-framework.md §4 (tables `signals`, `trades`, `rnd_results`, `strategy_state`). |
| G12 | Implémentable @fullstack sans ambiguïté | PASS | §5 spécifie les 5 fichiers à créer/étendre, les signatures de fonctions Python, la DDL SQL complète, le schedule UTC du cron, et la liste des ≥ 15 tests attendus. Zéro décision ouverte sur le code. |
| G15 | Zéro placeholder non résolu | PASS | Tous les `{variable}` sont documentés dans la légende §2 et les requêtes SQL §3. Aucun placeholder typé sans définition. |
| G17 | Zéro témoignage fictif | PASS | Pas de témoignage. Le rapport est un template bot, pas une citation de Thomas. |

**Questions auto-évaluation @growth spécifiques :**

- Chaque canal recommandé a-t-il une projection CAC/LTV ? N/A — outil perso, 0 € acquisition.
- La stratégie fonctionne-t-elle avec le budget réel ? OUI — 0 € additionnel. Le cron mensuel
  est inclus dans le budget Replit Core existant (~20 $/mois). Coût additionnel = 0.
- Le premier levier est-il activable en < 24h avec les agents IA ? OUI — @fullstack peut
  implémenter `run_monthly_report_mode()` en 1 session (Phase 5).
- La rétention est-elle traitée avec autant de rigueur que l'acquisition ? OUI — c'est
  l'unique canal : rétention de Thomas vis-à-vis de son outil.
- Le plan earned media inclut-il 2 pipelines ? N/A — outil non commercialisé, earned media
  externe hors-scope (justifié en §1 Contexte).

---

**Handoff → @fullstack**

- Fichiers produits :
  - `/home/user/TradingApp/docs/growth/rapport-mensuel-auto.md`
- Décisions prises :
  - Format Telegram HTML (cohérent Phase 2d-bis — pas de Markdown)
  - Cron UTC `0 7 1 * *` — delta 1h CET/CEST accepté (rapport mensuel, pas signal temps-réel)
  - Idempotence via table `monthly_reports` UNIQUE(month)
  - Rapport envoyé même sur jours fériés FR (différent du signal quotidien qui skip)
  - Sharpe 3 mois calculé côté Python (SQLite sans STDDEV natif)
  - Top 3 / bottom 3 dégradés si < 3 trades (pas d'erreur, affichage partiel)
  - Alerte P0 incluse dans le rapport si signal d'arrêt actif (pas à la place)
- Points d'attention :
  - Ajouter `monthly_reports` DDL dans `src/journal/schema.py` (idempotent)
  - Créer les 2 vues `equity_curve_monthly` et `trades_stats_monthly` dans schema.py
  - Créer `src/reports/monthly.py` (nouveau module) + étendre `src/telegram/templates.py`
  - Ajouter 3e cron `tradingapp-cron-monthly` dans `REPLIT_ACTIONS.md` section C
  - Ajouter `HEALTHCHECKS_MONTHLY_URL` dans les secrets Replit (section B de REPLIT_ACTIONS.md)
  - `rnd_results.backtest_avg_score` : si la colonne n'existe pas encore, le signal n°4
    (euphorie) doit dégrader gracieusement (`PASS par défaut — données backtest insuffisantes`)
  - `calendar_fr.py` : ne PAS skipper le rapport sur jours fériés (contrairement au signal)
  - Tests : ≥ 15 tests dont idempotence, mode paper, 0 trades, signal P0 actif
