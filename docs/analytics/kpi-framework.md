<!-- Version: 2026-05-01T00:00 — @data-analyst — Création initiale kpi-framework.md TradingApp -->
# KPI Framework — TradingApp

> **Résumé exécutif**
> - **Objectif** : définir les métriques de pilotage du bot signal turbo de Thomas, de la R&D edge au live.
> - **Décisions clés** : North Star = P&L net mensuel (PFU 31,4 % sur résultat annuel) ; drawdown 20 % bloquant ; % no-trade = vertu stratégique ; 5 signaux d'arrêt automatiques codifiés ; schéma SQLite prêt pour @fullstack.
> - **Dépendances** : @fullstack (schema SQLite) ; @ia (scoring Claude) ; @legal (PFU 31,4 % — L001 lessons-learned) ; personas.md (signaux d'arrêt, journée type 8h40-9h05) ; infra-audit.md (cache SQLite, rate limits Twelve Data).

---

## 1. Métrique North Star

### Définition

**P&L net mensuel après frais et fiscalité PFU.**

### Formule de calcul

```
P&L_net_mensuel =
  Σ_trades_du_mois (
    (prix_sortie − prix_entrée) × quantité          -- gain_brut_trade
    − frais_BD                                       -- 0,99 € × 2 (achat + vente)
    − spread_émetteur                                -- estimé 0,03-0,10 € selon turbo
  )
  − PFU_annuel_estimé_mensuel                        -- voir note fiscale ci-dessous
```

### Note fiscale critique (L001 — source @legal)

Le PFU s'applique au **résultat net annuel**, pas trade par trade. Taux : **31,4 %** depuis le 1er janvier 2025 (12,8 % IR + 18,6 % prélèvements sociaux + 0,6 % CSHR intégrés).

**Calcul du PFU mensuel estimé** (pour le suivi de performance mensuel uniquement) :
```
PFU_annuel_estimé = MAX(0, Σ_gains_bruts_annuels − Σ_pertes_brutes_annuelles) × 31,4 %
PFU_mensuel_estimé = PFU_annuel_estimé / 12  [APPROXIMATION pour pilotage mensuel]
```

Le scénario daté de personas.md L191 (~176 € net sur un trade à +258 € brut) est une **simplification illustrative**. La réalité fiscale est : le PFU se calcule en N+1 sur le bilan annuel via formulaire 2074. Le journal SQLite doit stocker `pfu_year_estimate` cumulé pour anticiper la charge fiscale.

### Seuil d'alerte

| Niveau | Valeur | Action requise |
|--------|--------|----------------|
| Alerte précoce | P&L net < 0 sur le mois | Revue du journal, identifier les patterns de pertes |
| **Seuil bloquant** | P&L net < −10 % du capital dédié mensuel (soit −2 000 à −3 000 € sur 20-30 k€) | Arrêt du live, audit complet du journal, passage en paper-trading |
| GO continue | P&L net positif ≥ 3 mois consécutifs + drawdown < 20 % | Critère de validation edge viable (voir section 6) |

---

## 2. Métriques secondaires

### 2.1 Drawdown mensuel max (BLOQUANT)

```
Drawdown_mensuel_max = MAX( (capital_peak_du_mois − capital_creux_du_mois) / capital_peak_du_mois )
```

| Seuil | Action |
|-------|--------|
| > 15 % | Alerte — Thomas devient plus sélectif (personas.md : critère pull-the-trigger) |
| **> 20 %** | **Arrêt du live immédiat** — retour en paper-trading + audit journal (signal d'arrêt n°1) |

### 2.2 Win Rate

```
Win_rate = (nombre de trades gagnants / nombre total de trades) × 100
```

| Phase | Valeur cible | Seuil alerte |
|-------|-------------|--------------|
| Backtest in-sample (2021-2024) | [HYPOTHÈSE : ≥ 55 % — à calibrer en R&D Phase 1] | < 50 % → edge non rentable sans PF élevé |
| Out-of-sample 2025 | ≥ 50 % (dégradation max −5 pts vs IS) | < 45 % → overfitting probable |
| Live | Win_rate_live ≥ Win_rate_backtest − 15 pts | Écart > 15 pts sur 3 mois → signal d'arrêt n°3 |

### 2.3 Profit Factor

```
Profit_Factor = Σ gains bruts / Σ pertes brutes (valeur absolue)
```

| Seuil | Interprétation | Action |
|-------|----------------|--------|
| < 1,0 | Edge perdant | Revoir edge, no-go Phase 2 |
| 1,0 − 1,5 | Marginal, insuffisant pour frais + fiscalité | Optimisation requise avant Phase 2 |
| **≥ 1,5** | **Seuil minimum GO Phase 2** | Critère de qualification edge |
| ≥ 2,0 | Edge robuste | GO Phase 2 confiant |

### 2.4 Sharpe Ratio annualisé

```
Sharpe_annualisé = (Rendement_moyen_trades − Taux_sans_risque) / Écart_type_rendements × √252
```

Taux sans risque : [HYPOTHÈSE : OAT 10 ans France ~3,0 % — à actualiser au moment du calcul].

| Phase | Seuil |
|-------|-------|
| In-sample | > 1,5 (Sharpe élevé attendu en IS) |
| **Out-of-sample** | **> 1,0 (seuil GO Phase 2)** |
| Dégradation admissible | OOS Sharpe ≥ 50 % du Sharpe IS |

### 2.5 MAE / MFE moyens (héritage Finance — conservé)

Source : `project-context.md` section "Héritage Finance — Garde".

```
MAE_moyen = Σ (prix_entrée − prix_min_trade) / nombre_trades   [pour trades achat]
MFE_moyen = Σ (prix_max_trade − prix_entrée) / nombre_trades   [pour trades achat]
```

| Indicateur | Usage | Seuil d'alerte |
|------------|-------|----------------|
| MAE / SL | Ratio d'utilisation du stop-loss. Si MAE_moyen ≈ SL → les stops sont trop serrés | > 0,8 → réviser SL |
| MFE / TP | Ratio de capture du profit. Si MFE_moyen >> TP → les TP sont trop courts | < 0,5 → réviser TP |
| MAE / MFE | Ratio risque/opportunité intrinsèque | < 0,3 → edge favorable |

---

## 3. Métriques de qualité signal

### 3.1 Score de confiance moyen

```
Score_confiance_moyen = Σ scores_signaux_GO / nombre_signaux_GO  [échelle 1-10]
```

| Seuil | Interprétation | Action |
|-------|----------------|--------|
| Score moyen en live > Score moyen backtest | Euphorie — signaux cherry-pickés | Signal d'arrêt n°4 — forcer walk-forward OOS |
| Score moyen < seuil de déclenchement × 1,1 | Signaux marginaux retenus | Revoir seuil à la hausse |

### 3.2 % No-trade jours — VERTU STRATÉGIQUE

```
Pct_no_trade = (nombre de jours "pas de trade" / nombre de jours ouvrés) × 100
```

**Principe** (brand-platform.md section 3, pilier "Backtesté") : un % no-trade élevé est la preuve que le bot respecte son seuil de confiance. Ce KPI est positif, pas négatif.

| Valeur | Interprétation | Action |
|--------|----------------|--------|
| 30-60 % | Normal — bot sélectif, cohérent | RAS |
| < 20 % | Alerte — le bot force des signaux | Vérifier seuil de confiance, signal d'arrêt n°2 si 3 semaines consécutives sans no-trade |
| > 80 % | Alerte — edge peut-être trop sur-paramétré | Revoir les paramètres, revue du seuil de confiance |

### 3.3 Latence push Telegram

```
Latence_telegram = heure_envoi_message_telegram − heure_déclenchement_cron
```

| Seuil | Action |
|-------|--------|
| ≤ 8h55 CET | OK — dans la fenêtre d'exécution Thomas |
| **> 8h55 CET** | **BLOQUANT** — Thomas ne peut plus exécuter (contrainte absolue personas.md L51) |
| > 9h00 CET | Signal inutilisable — journaliser comme "sent_too_late", ne pas compter dans P&L |

Composantes mesurées séparément : `latence_twelve_data_ms`, `latence_claude_ms`, `latence_telegram_ms`.

### 3.4 Taux d'erreur Twelve Data

```
Taux_erreur_TD = (appels Twelve Data en échec / appels totaux) × 100  [sur 30 jours glissants]
```

| Seuil | Action |
|-------|--------|
| < 5 % | Normal |
| 5-15 % | Monitoring renforcé, vérifier rate limits (infra-audit.md section 2.3) |
| > 15 % | Alerte Telegram P1 — risque de signaux incomplets |

### 3.5 Taux d'erreur Claude

```
Taux_erreur_Claude = (appels Claude en timeout ou erreur / appels totaux) × 100  [30 jours glissants]
```

| Seuil | Action |
|-------|--------|
| < 2 % | Normal (fallback signal brut activé selon infra-audit.md section 5.3) |
| > 5 % | Alerte P1 — qualité justification dégradée |

---

## 4. Plan d'instrumentation — Schéma SQLite

Deux bases distinctes (infra-audit.md section 4.3) : `data/market_cache.sqlite` (données marché) et `data/journal.sqlite` (trading + performance).

### Table `signals`

```sql
CREATE TABLE signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE NOT NULL,                          -- date du signal (YYYY-MM-DD)
    hour_calc       TIME NOT NULL,                          -- heure calcul signal (HH:MM:SS CET)
    asset           TEXT NOT NULL,                          -- ex : "^FCHI", "MC.PA", "EURUSD"
    direction       TEXT NOT NULL CHECK (direction IN ('BUY','SELL','NO_TRADE')),
    entry           REAL,                                   -- prix d'entrée turbo (NULL si NO_TRADE)
    sl              REAL,                                   -- stop-loss turbo (NULL si NO_TRADE)
    tp              REAL,                                   -- take-profit turbo (NULL si NO_TRADE)
    score           REAL,                                   -- score de confiance Claude (1.0-10.0)
    backtest_ref    TEXT,                                   -- ex : "B-031"
    no_trade_reason TEXT,                                   -- raison si NO_TRADE (ex : "score 5.1 < seuil 6.5")
    sent_to_telegram BOOLEAN NOT NULL DEFAULT 0,
    telegram_msg_id  INTEGER,                               -- message_id retourné par Telegram API
    hour_sent        TIME,                                  -- heure d'envoi effectif Telegram (CET)
    latency_total_ms INTEGER,                               -- latence totale cron→Telegram en ms
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table `trades`

```sql
CREATE TABLE trades (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id           INTEGER NOT NULL REFERENCES signals(id),
    executed            BOOLEAN NOT NULL DEFAULT 0,         -- Thomas a-t-il exécuté ?
    entry_real          REAL,                               -- prix d'entrée réel (peut différer du signal)
    exit_real           REAL,                               -- prix de sortie réel
    quantity            INTEGER,                            -- nombre de turbos
    exit_reason         TEXT CHECK (exit_reason IN ('TP','SL','TIMEOUT','MANUAL','KNOCKOUT')),
    exit_date           TIMESTAMP,
    pnl_brut            REAL,                               -- (exit_real − entry_real) × quantity
    frais_bd            REAL DEFAULT 0.99,                  -- frais Bourse Direct achat (€)
    frais_bd_vente      REAL DEFAULT 0.99,                  -- frais Bourse Direct vente (€)
    spread_emetteur     REAL,                               -- spread estimé à l'exécution (€)
    pnl_net_avant_pfu   REAL,                               -- pnl_brut − frais_bd − frais_bd_vente − spread_emetteur
    pfu_year_estimate   REAL,                               -- contribution estimée au PFU annuel (31,4 % × MAX(0, gain))
    mae                 REAL,                               -- Maximum Adverse Excursion (€)
    mfe                 REAL,                               -- Maximum Favorable Excursion (€)
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Rétention** : 10 ans minimum (legal-audit.md section 7.4 — délai report moins-values + prescription fiscale).

### Index recommandés

```sql
CREATE INDEX idx_signals_date ON signals(date);
CREATE INDEX idx_trades_signal_id ON trades(signal_id);
CREATE INDEX idx_trades_exit_date ON trades(exit_date);
```

---

## 5. Dashboard de suivi mensuel

### Rapport auto-généré (Phase 4 — à implémenter par @growth transposé)

**Fréquence** : généré automatiquement le 1er jour ouvré du mois suivant, envoyé sur Telegram.

**Contenu obligatoire** (format Telegram — cohérent brand-platform.md Tone of Voice) :

```
--- Rapport mensuel [MOIS ANNEE] ---
Signaux envoyés : [N]  | No-trade : [N] ([%] — vertu)
Trades exécutés : [N]  | Win rate : [%]

P&L brut : +[X] €
Frais Bourse Direct : −[X] €
Spread émetteur estimé : −[X] €
PFU estimé (31,4 % cumulé YTD) : −[X] €
P&L net estimé : [X] €

Drawdown max du mois : [%] (seuil 20 %)
Profit Factor : [X]
Score confiance moyen : [X]/10

MAE moyen : [X] € | MFE moyen : [X] €
Latence moyenne Telegram : [X]h[X]m[X]s

Statut edge : [OK / ALERTE / ARRÊT]
```

---

## 6. Critère GO/NO-GO continuer la stratégie

**Critère de succès à 12 mois** (project-context.md — objectif "ce que ressemble le succès") :

| Condition | Valeur cible | Durée |
|-----------|-------------|-------|
| P&L net positif | > 0 € (net PFU) | ≥ 3 mois consécutifs |
| Drawdown mensuel | < 20 % capital dédié | Chaque mois |
| Win rate live vs backtest | Écart < 15 pts | Sur 3 mois glissants |
| Profit Factor live | ≥ 1,5 | Sur 3 mois |

**NO-GO continuer** : si l'une des conditions ci-dessus n'est pas respectée sur 3 mois consécutifs → revoir l'edge complet. Cohérent avec décision structurante n°4 et n°5 du project-context.md.

---

## 7. Signaux d'arrêt automatiques (5 conditions de personas.md)

Implémenter en **triggers SQLite + alerte Telegram P0** (infra-audit.md section 5.5).

| # | Condition | Trigger SQLite | Alerte Telegram |
|---|-----------|----------------|-----------------|
| 1 | Drawdown mensuel > 20 % capital dédié | `pnl_net_avant_pfu` cumulé mensuel < −capital_dédié × 0,20 | P0 — "ARRÊT LIVE — drawdown mensuel dépasse 20 %. Retour paper-trading." |
| 2 | 3 semaines consécutives sans signal GO | 15 jours ouvrés consécutifs avec `direction = 'NO_TRADE'` | "Revue seuil de confiance — 15 j ouvrés sans signal GO. Edge peut-être sur-paramétré." |
| 3 | Win rate live < win rate backtest − 15 pts sur 3 mois | Calculé en batch mensuel (comparaison journal vs `backtest_ref`) | "ALERTE — win rate live [X%] vs backtest [Y%]. Écart > 15 pts sur 3 mois. Revue edge." |
| 4 | Score confiance moyen en live > score moyen backtest (euphorie) | `AVG(score) WHERE direction='BUY'` dernier mois > `backtest_avg_score` | "ALERTE euphorie — scores signaux récents supérieurs backtest. Forcer walk-forward OOS." |
| 5 | Position turbo non clôturée en fin de journée (overnight) | Trade sans `exit_date` après 17h30 CET le jour J | P0 — "INCIDENT — position ouverte non clôturée. Vérifier immédiatement sur Bourse Direct." |

---

## Hypothèses à valider

| # | Hypothèse | Owner | Action |
|---|-----------|-------|--------|
| H-KPI-1 | Seuil de confiance GO = 6,5/10 | @fullstack + Thomas | À calibrer en Phase 1 R&D — valeur exemple dans personas.md |
| H-KPI-2 | Win rate cible ≥ 55 % in-sample | @data-analyst Phase 1 | Dépend de l'edge retenu |
| H-KPI-3 | Taux sans risque OAT 10 ans ~3,0 % pour Sharpe | Thomas | À actualiser au moment du calcul Sharpe |
| H-KPI-4 | Spread émetteur estimé 0,03-0,10 € | Thomas | À mesurer sur trades réels Bourse Direct |
| H-KPI-5 | backtest_avg_score = score moyen IS backtest retenu | @data-analyst Phase 1 | À alimenter dans `signals` table après Phase 1 |

---

**Handoff → @ia, @fullstack, @orchestrator**

- Fichiers produits : `/home/user/TradingApp/docs/analytics/kpi-framework.md`
- Décisions prises :
  - North Star = P&L net mensuel après frais (0,99 € × 2 BD + spread) et PFU 31,4 % (annuel, pas trade par trade)
  - Drawdown > 20 % = seuil BLOQUANT (signal d'arrêt n°1, trigger SQLite implémenté)
  - % no-trade = vertu (alerte si < 20 % — bot force des signaux)
  - Schéma SQLite tables `signals` + `trades` complet et prêt à implémenter
  - 5 signaux d'arrêt codifiés en triggers SQLite + alertes Telegram P0
- Points d'attention :
  - **@fullstack** : implémenter le schéma SQLite `journal.sqlite` (tables `signals` + `trades` + index) — prêt à copier tel quel
  - **@ia** : le champ `score` dans `signals` est la sortie directe du scoring Claude (1.0-10.0) — aligner avec le prompt de scoring
  - **@fullstack** : calculer `pfu_year_estimate` dans `trades` = MAX(0, pnl_net_avant_pfu) × 31,4 % en Python/SQL
  - **Signal d'arrêt n°5** (position overnight) : vérifier l'heure avec `TZ=Europe/Paris` — 17h30 CET = cutoff turbo Bourse Direct [HYPOTHÈSE H3 non validée — confirmer l'heure exacte de clôture des turbos sur Bourse Direct]
  - Rétention journal SQLite 10 ans obligatoire (legal-audit.md section 7.4)
- Actions Replit requises : aucune (livrable documentation uniquement — le schéma SQL sera implémenté par @fullstack Phase 2)
- Gates BLOQUANT vérifiées : G1 PASS, G3 PASS, G5 PASS (Thomas mentionné), G6 PASS (P&L net mensuel = North Star identique project-context.md), G7 PASS (PFU 31,4 % aligné legal-audit.md L001), G12 PASS, G13 PASS (zéro chiffre inventé — seuils sourcés, hypothèses marquées), G15 PASS, G17 PASS, G23 PASS (chaque KPI a formule + seuil d'alerte)
