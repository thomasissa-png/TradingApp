<!-- Version: 2026-05-01 — @sales-enablement (transposé "armurier Thomas") Phase 4 — TradingApp -->
# Runbook usage personnel — TradingApp

> **Rôle** : @sales-enablement transposé en "armurier qui équipe Thomas pour l'utilisation quotidienne du bot". Pas de playbook commercial — outil 100 % personnel.
> **Lecteur cible** : Thomas (persona unique, cf. `docs/strategy/personas.md`).
> **Objectif** : manuel opérationnel quotidien / hebdo / mensuel + procédures incidents + protocole décision GO/NO-GO.
> **Sources liées** : `personas.md` (journée 8h40-9h05 + signaux d'arrêt), `REPLIT_ACTIONS.md` (mini-jalon J+7), `docs/product/functional-specs.md` US-08 à US-12, `docs/growth/rapport-mensuel-auto.md`, `docs/analytics/kpi-framework.md` §7 (6 signaux d'arrêt), `docs/ux/user-flows.md` F20-F24.
> **Brand-platform alignment** : Factuel · Concis · Backtesté — ce runbook s'adresse à Thomas en "tu", chiffres explicites, zéro bullshit.

---

## Sommaire

1. [Procédure quotidienne 8h40-9h05](#1-procedure-quotidienne-8h40-9h05)
2. [Audit hebdomadaire vendredi 18h](#2-audit-hebdomadaire-vendredi-18h)
3. [Décision mensuelle GO/NO-GO continuer](#3-decision-mensuelle-gonogo-continuer)
4. [Procédures incidents](#4-procedures-incidents)
5. [Protocole décision GO/NO-GO mensuelle (détail)](#5-protocole-decision-gonogo-mensuelle-detail)

---

## 1. Procédure quotidienne 8h40-9h05

> **Cas de référence** : jour ouvré FR (lundi-vendredi hors fériés `workalendar.europe.France`). Hors créneau → bot silencieux, rien à faire.
> **Smartphone Thomas** : Telegram en 1er écran d'accueil, notifications activées, son/vibration ON pour le bot TradingApp uniquement (filtrage chat).

### Timeline complète (chronométrée)

| Heure CET | Acteur | Action attendue | Checkpoint visuel | Fallback si problème |
|---|---|---|---|---|
| **8h40:00** | Cron Replit | Trigger automatique (schedule UTC `40 6,7 * * 1-5` + wrapper TZ-aware Option 1, cf. REPLIT_ACTIONS §C.2) | Aucun (background) | Si rien à 8h41 → cf. §4.1 "Bot ne déclenche pas" |
| **8h40:15-8h44** | Bot (background) | Pipeline scoring : Twelve Data delta cache → backtester → ScoringEngine (D1-D6 + SC1-SC7) → Claude Sonnet 4.5 (tool use) → SQLite INSERT `signals` → ping healthchecks.io | Aucun (Thomas RER ou trajet) | Si timeout Sonnet 25s → fallback Haiku 4.5 (cf. ai-architecture v1.1) |
| **8h45:00 ± 30s** | Bot → Telegram | Push message sur `THOMAS_CHAT_ID` (format strict 6L+1 ACHAT/VENTE OU 3L NO-TRADE OU 3L DEGRADED MODE OU 3L ERREUR DATA) | Notification Telegram + son/vibration | Si rien à 8h47 → cf. §4.2 "Telegram non reçu" |
| **8h45-8h47** | Thomas | Déverrouille smartphone, ouvre Telegram (chat épinglé en haut), lit le message en **25 s max** (cf. scénario daté personas.md ligne 178) | Message lu = decision rapide | Si message illisible (formatage cassé) → cf. §4.5 "Signal incohérent" |
| **8h47:30** | Thomas (cerveau) | **Décision binaire** : GO / NO-GO. Critères pull-the-trigger personas.md §6 : score ≥ seuil, SL présent, risque chiffré, backtest ref. **NO-TRADE → ferme Telegram, fin du process** | Mental "je trade" / "je trade pas" | Doute → règle d'or : **dans le doute, NO-TRADE** (Frustration 4 personas) |
| **8h48-8h52** | Thomas | Si GO : ouvre Bourse Direct mobile, recherche `<sous-jacent> Turbo <Call/Put>` (ex. `DAX Turbo Call`), filtre **delta ~0,5** (pas trop dans la monnaie), vérifie **spread ≤ 0,05 €** | Liste turbos affichée + delta visible | Spread > 0,10 € → ne pas exécuter (slippage > backtest budget cf. edge-rnd-report §6 R3) |
| **8h52-8h54** | Thomas | Passe **3 ordres en parallèle** : (1) ordre limite achat à `entry`, (2) ordre stop à `SL`, (3) ordre limite vente à `TP_cible`. Sizing fixe : **150 € risque max** (= 1 500 € engagés × SL ~10 %, cf. scénario personas) | 3 ordres listés "en cours" Bourse Direct | Si BD bug ordre lié → 1er ordre achat seul + ajout SL/TP **immédiatement après exécution** |
| **8h54-8h55** | Thomas | Confirme dans Bourse Direct que l'achat est exécuté (carnet d'ordres), screenshot rapide pour log mental | "Exécuté à HH:MM:SS" affiché | Non exécuté à 8h55 → **annule l'ordre**, signal périmé (cf. user-flows F24 + US-12) |
| **8h55:00** | Thomas | **Range smartphone** — termine sa préparation matinale. La fenêtre est fermée | Téléphone en poche | N/A |
| **8h55-9h05** | Thomas | Trajet bureau / arrivée poste de travail. **Pas de gestion intraday** (règle d'or personas ligne 51) | N/A | N/A |
| **9h05+** | Thomas | Au bureau. Notifications Bourse Direct restent ON sur smartphone | Activité principale (job) | N/A |
| **10h-12h (variable)** | Bourse Direct | Notification push : "SL touché" OU "TP touché" OU "Position toujours ouverte" | Notification BD | Position toujours ouverte 17h45 → **clôture manuelle obligatoire avant 18h00 CET** (signal d'arrêt n°5 — turbo overnight knock-out, cf. kpi-framework §7) |
| **12h-14h (déjeuner)** | Thomas | Tape commande Telegram : `/trade <pl_brut_eur> <mae_eur> <mfe_eur>` au bot (ex. `/trade +258 -45 +280`). US-08 functional-specs | Bot répond "Trade loggué SQLite ID #N" | Si bot ne répond pas → cf. §4.6 "Commande Telegram silencieuse" |

### Règles d'or quotidiennes (ne jamais déroger)

1. **Pas de trade après 8h55** — même si le signal était bon, conditions de marché ont changé (cf. critère 5 pull-the-trigger personas).
2. **SL absent du message** → ne trade pas (règle d'or perso, frustration n°1 personas).
3. **Drawdown mensuel cumulé > 15 %** → devient plus sélectif même si seuil score atteint (cf. personas §"Ce qui fait qu'il NE trade PAS").
4. **News majeure (BCE, NFP, CPI)** annoncée dans la fenêtre → ne trade pas, même si signal GO (le bot devrait l'avoir filtré, mais Thomas garde la main).
5. **Logger CHAQUE trade** au déjeuner (`/trade`) — sans journal, pas d'audit hebdo, pas de signaux d'arrêt déclenchables (US-08 + kpi-framework §3).

---

## 2. Audit hebdomadaire vendredi 18h

> **Trigger automatique** : cron Replit `tradingapp-cron-weekly` schedule UTC `0 17 * * 5` (CEST) ou `0 18 * * 5` (CET) → mode `--mode=journal-week` envoie résumé Telegram (US-09 functional-specs).
> **Trigger manuel** : Thomas tape `/journal-week` dans Telegram à tout moment (US-09).
> **Durée audit** : 5 minutes max — ne pas dériver en analyse approfondie (réservé à l'audit mensuel).

### Format du résumé hebdo Telegram (US-09 + message-templates §5)

```
📊 Audit hebdo — semaine S{numéro}
Du {lundi} au {vendredi}

Signaux générés : {N_signaux}
Trades exécutés  : {N_trades} / {N_signaux} ({%}%)
P&L brut         : {pl_brut} €
P&L net (frais + PFU 31,4%) : {pl_net} €
Drawdown semaine : {dd_max} %
Win rate live    : {wr_live} % (vs backtest {wr_bt} %)

Statut signaux d'arrêt : {0-6}/6 actifs
Mode actuel : {paper|live}
```

### Grille de décision Thomas (4 questions PASS/FAIL)

| # | Question | PASS si | FAIL si | Action si FAIL |
|---|---|---|---|---|
| Q1 | **Win rate live ≥ win rate backtest − 15 pts** ? | Oui (ex. WR live 55 % vs WR backtest 65 %) | Non (ex. WR live 45 % vs 65 %) | Ne pas paniquer (n=5-10 trades = bruit). Marquer dans agenda mental "à re-vérifier S+1". Si FAIL **3 semaines consécutives** → signal d'arrêt n°3 déclenché, audit complet (cf. §3) |
| Q2 | **% no-trade dans la fourchette saine** [20 % ; 80 %] (kpi-framework §7 signal n°2) ? | Oui (ex. 3 NO-TRADE / 5 jours = 60 %) | Non — soit < 20 % (le bot trade trop : risque cherry-picking), soit > 80 % (le bot ne trade quasi jamais : seuil sur-paramétré) | < 20 % → revue scoring SC4 (kpi §5 sanity check). > 80 % 3 semaines → revue seuil CONFIDENCE_THRESHOLD (signal arrêt n°2) |
| Q3 | **Drawdown semaine < 5 %** du capital dédié (1-1,5 k€ sur 20-30 k€) ? | Oui | Non (ex. -8 %) | Si DD semaine > 5 % mais DD mois < 15 % → continuer mais sélectivité accrue. Si DD mois > 20 % → signal d'arrêt n°1 → STOP automatique (cf. §4.5 + §3) |
| Q4 | **J'ai bien loggué tous les trades de la semaine** (`/trade`) ? | `N_trades_logges == N_executes` | Mismatch (ex. 3 trades exécutés, 2 loggués) | Logger les trades manquants ce week-end (BD historique → SQLite via `/trade <pl> <mae> <mfe>`). Sans données complètes : audit mensuel biaisé |

### Décision Thomas en sortie d'audit

- **4/4 PASS** → continuer comme la semaine passée, aucune action.
- **3/4 PASS** → continuer mais marquer la question FAIL en watchlist mentale pour S+1.
- **2/4 ou moins PASS** → **escalade audit mensuel anticipé** (ne pas attendre le 1er du mois — relire §3 immédiatement).

### Pas de logging audit hebdo en SQLite

L'audit hebdo n'est **pas persisté** côté Thomas (juste lu et oublié). Le rapport mensuel re-calcule tout depuis `signals` + `trades` (source de vérité). Pas de double saisie.

---

## 3. Décision mensuelle GO/NO-GO continuer

> **Trigger** : 1er du mois à 9h00 CET, cron Replit `--mode=monthly-report` (cf. `docs/growth/rapport-mensuel-auto.md` §1).
> **Lecteur** : Thomas, sur smartphone le matin du 1er (ou différé même jour, max +24h).
> **Décision** : binaire `/continue` ou `/stop` (US-10/US-11 functional-specs). Pas de "wait and see" — l'absence de décision = `/continue` implicite.

### Critères chiffrés GO/NO-GO continue (5 KPIs)

Source : `docs/analytics/kpi-framework.md` §7 + `personas.md` signaux d'arrêt + `docs/qa/backtest-audit-phase1.md` C1-C6.

| # | KPI | Seuil GO | Seuil ALERT | Seuil NO-GO (`/stop`) |
|---|---|---|---|---|
| K1 | **P&L net mensuel** (après frais BD 1,98 € + PFU 31,4 % annualisé) | ≥ 0 € | < 0 € **mais** ≥ -2 % capital dédié | < -2 % capital dédié 2 mois consécutifs |
| K2 | **Drawdown mensuel** (vs équity début de mois) | < 15 % | 15-20 % | > 20 % (signal arrêt n°1 — `/stop` automatique forcé par bot) |
| K3 | **Win rate live vs backtest** (3 mois glissants) | écart ≤ 10 pts | écart 10-15 pts | écart > 15 pts (signal arrêt n°3) |
| K4 | **Profit Factor live** (3 mois glissants) | PF ≥ 1,5 | PF 1,2-1,5 | PF < 1,2 |
| K5 | **% no-trade** mensuel | 20-80 % | 80-90 % OU 10-20 % | > 90 % (signal arrêt n°2) OU < 10 % (cherry-picking) |

### Matrice décision

| Configuration KPI | Décision Thomas | Commande Telegram | Commentaire |
|---|---|---|---|
| 5/5 GO | `/continue` | `/continue` | Cas idéal. Continuer mode actuel (paper ou live) |
| 4/5 GO + 1 ALERT | `/continue` | `/continue` | Watchlist + audit hebdo renforcé S+1 |
| 3/5 GO + 2 ALERT | **Pause 1 mois en paper** | `/stop` (passe en paper sans arrêter le bot — US-11) | Test sans risque capital pendant 30j |
| ≥ 1 NO-GO ou drawdown > 20 % | **Stop définitif live** | `/stop` (mode paper-trading conservé) | Audit complet @reviewer + @data-analyst avant relance |
| Signal d'arrêt P0 déclenché (n°1, n°3, n°6 cf. kpi §7) | **STOP automatique forcé** par bot | N/A — bot bascule paper sans confirmation | Thomas reçoit notification Telegram + email healthchecks |

### Procédure escalade fondateur (signal d'arrêt P0 déclenché)

1. **Réception alerte Telegram** : message bot "🚨 SIGNAL D'ARRÊT N°{X} DÉCLENCHÉ — bascule paper-trading auto" (cf. message-templates §7).
2. **Sous 1h** : Thomas tape `/journal-week` pour voir le contexte récent (5 derniers signaux + trades).
3. **Sous 24h** : Thomas exporte le journal SQLite local : `sqlite3 data/journal.sqlite ".dump signals trades strategy_decisions" > backup-incident-$(date +%F).sql`.
4. **Sous 72h** : analyse post-mortem en mode "armurier" — Thomas se demande : "ai-je modifié quelque chose ? changement de marché ? bug bot ?". Documenter dans `lessons-learned.md` (entrée P0).
5. **Relance live** : interdite tant que cause racine non identifiée + 30j paper-trading clean (5/5 KPIs GO sur 30j paper).

### Communication interne (post-mortem)

- **Si décision `/stop` définitif** : avant de taper `/stop`, **dump SQLite obligatoire** (cf. point 3 ci-dessus). Sans dump → perte de l'historique pour analyse.
- **Pas de communication externe** : outil 100 % perso, pas de partie prenante à informer (cohérent project-context.md ligne 38 "concurrent N/A").

---

## 4. Procédures incidents

> Pour chaque scénario, suivre les étapes **dans l'ordre** — l'étape suivante n'est utile que si la précédente a échoué.
> En cas de doute, la règle d'or : **ne pas trader** (FAIL safe). Mieux vaut un signal manqué qu'un trade au feeling.

### 4.1. Bot ne déclenche pas à 8h45 (pas de message Telegram)

**Symptôme** : Thomas n'a rien reçu à 8h47.

**Étapes** :
1. **Check email healthchecks.io** (compte créé section E REPLIT_ACTIONS) — si email "Down" reçu → cron n'a pas pingé → checker Replit. Si pas d'email → cron a pingé mais Telegram a échoué (saut à 4.2).
2. **Replit Cron status** : ouvrir [replit.com/deployments](https://replit.com/deployments) → `tradingapp-cron-daily` → onglet **Logs**. Chercher dernier log < 24h. Erreur visible ? (TimeoutError, ImportError, etc.) → screenshot.
3. **Twelve Data API key valide** : Replit Shell → `python -c "import os, requests; r=requests.get(f'https://api.twelvedata.com/time_series?symbol=DAX&interval=1min&apikey={os.environ[\"TWELVEDATA_API_KEY\"]}&outputsize=1'); print(r.status_code, r.text[:200])"`. Doit retourner 200 + JSON. Si 401/403 → clé révoquée → renouveler (REPLIT_ACTIONS B.1 ligne 3).
4. **Anthropic API key valide** : Replit Shell → `python -c "import anthropic; c=anthropic.Anthropic(); print(c.models.list().data[0].id)"`. Doit retourner liste. Si erreur 401 → clé révoquée → renouveler (REPLIT_ACTIONS B.1 ligne 4) + vérifier Workspace Limits 30 $/mois pas atteint.
5. **Si 1-4 KO** : passer en paper-trading manuel pour la journée (ne pas trader sans bot fonctionnel) + ouvrir incident dans `lessons-learned.md`.

### 4.2. Message Telegram non reçu (mais bot a tourné)

**Symptôme** : healthchecks UP + Replit logs OK + pas de message Telegram.

**Étapes** :
1. **Vérifier `THOMAS_CHAT_ID`** : Replit Secrets → check valeur numérique présente. Si vide → re-suivre F22 user-flows.md (`/start` au bot + `@userinfobot`).
2. **Redémarrer Telegram** : force-quit app + relance + ouvrir conversation bot.
3. **Vérifier `BotFather` quota** : ouvrir Telegram → `@BotFather` → `/mybots` → sélectionner bot → "API Token" — si limite atteinte (30 msg/sec, jamais le cas pour 1 msg/jour) → attendre 1h.
4. **Si toujours rien** : tester ping manuel depuis Replit Shell : `python -c "import os, requests; requests.post(f'https://api.telegram.org/bot{os.environ[\"TELEGRAM_BOT_TOKEN\"]}/sendMessage', json={'chat_id':int(os.environ['THOMAS_CHAT_ID']),'text':'test'})"`. Si 200 + message reçu → bug code bot. Si erreur → token invalide.

### 4.3. DEGRADED MODE répété ≥ 3 jours consécutifs

**Symptôme** : 3 messages "DEGRADED MODE" consécutifs (template message-templates §3 — Claude indispo après fallback Sonnet→Haiku, cf. ai-architecture v1.1 §4).

**Étapes** :
1. **Réception alerte healthchecks.io** : ce cas devrait déclencher une alerte (signal d'arrêt n°6 indirect — qualité données dégradée).
2. **Vérifier `/var/log` Replit** : Replit Shell → `tail -50 /home/runner/<repl-name>/logs/app.log` (si fichier existe). Sinon Deployments → Logs.
3. **Vérifier statut Anthropic API** : [status.anthropic.com](https://status.anthropic.com) — incident en cours ?
4. **Si Anthropic UP** : escalade → mentionner @fullstack dans `lessons-learned.md` (entrée P1 — bug fallback chain).
5. **Pendant l'incident** : Thomas continue de **lire** les NO-TRADE générés (ils sont fiables) mais ne trade pas sur les rares messages "DEGRADED" (qui ne contiennent pas de signal exécutable par design).

### 4.4. Signal incohérent (entry > SL pour BUY, etc.)

**Symptôme** : message reçu avec `entry=3,42 €`, `SL=3,55 €` (SL > entry sur ACHAT) — incohérence physique.

**Étapes** :
1. **Sanity Check SC1 (cohérence direction) doit avoir bloqué** (cf. edge-scoring-model v1.2 §3) — si non, **bug confirmé**.
2. **Ne pas trader** ce signal — règle d'or absolue.
3. **Reporter le bug** : screenshot du message + timestamp + ouverture entrée P0 dans `lessons-learned.md`.
4. **Mention @fullstack** : escalade prioritaire, SC1 doit être patché immédiatement (régression bloquante).

### 4.5. Drawdown > 20 % atteint (signal d'arrêt n°1)

**Symptôme** : alerte Telegram du bot "🚨 SIGNAL D'ARRÊT N°1 — drawdown mensuel {X}% > 20%, bascule paper auto".

**Étapes** :
1. **Bot a déjà basculé en paper-trading** automatiquement (US-11 — `STRATEGY_ACTIVE` SQLite passé à `paper`). Aucune action urgente.
2. **Sous 1h** : Thomas vérifie son journal SQLite : `sqlite3 data/journal.sqlite "SELECT date, entry, sl, tp, pl_brut_eur, pl_net_eur FROM trades ORDER BY date DESC LIMIT 30;"` — identifier les trades perdants récents.
3. **Sous 24h** : Thomas tape `/stop` pour confirmer la bascule paper (US-11 — `/stop` est en réalité une bascule paper, pas un arrêt définitif. Cohérent F21 user-flows).
4. **Sous 72h** : appliquer procédure escalade fondateur §3 (dump SQLite + post-mortem `lessons-learned.md` P0).
5. **Relance live** : interdite tant que 30j paper clean + cause racine identifiée (cf. §3).

### 4.6. Replit down (incident infrastructure global)

**Symptôme** : [status.replit.com](https://status.replit.com) en rouge OU plusieurs heures sans pouvoir accéder au Repl.

**Étapes** :
1. **Pendant l'incident** : pas de signal possible — Thomas ne trade pas.
2. **Fallback documenté (non implémenté MVP)** : migration Hetzner CX11 4,5 €/mois (cf. infra-audit.md §1.3 alternative écartée H1 pour MVP). Procédure :
   - Cloner repo GitHub privé sur Hetzner : `git clone git@github.com:thomasissa-png/TradingApp.git`.
   - Setup `uv sync` + variables `.env` (sourcer Replit Secrets archivés).
   - Setup cron Linux `40 8 * * 1-5 cd /opt/TradingApp && python -m src.main --mode=signal` (TZ Europe/Paris natif Hetzner — pas besoin de wrapper).
   - Setup healthchecks.io ping URL identique.
3. **Script bash prêt** : `scripts/migrate-to-hetzner.sh` — à créer Phase 5 si besoin (hors-scope MVP).
4. **Décision migration** : seulement si Replit down > 24h (Cron Replit a une SLA implicite, incidents historiques < 4h).

### 4.7. Commande Telegram silencieuse (`/trade`, `/journal-week`, etc. sans réponse)

**Symptôme** : Thomas tape `/trade +258 -45 +280` au déjeuner, bot ne répond pas.

**Étapes** :
1. **Vérifier orthographe** : commande exacte `/trade <pl_brut> <mae> <mfe>` avec **3 nombres séparés par espaces**, signes optionnels (`+` ou `-`), unités EUR implicites. Exemple correct : `/trade +258 -45 +280`.
2. **Vérifier auth** : la commande ne marche que si elle vient de `THOMAS_CHAT_ID` (auth stricte, cf. fullstack Phase 2c-2). Si Thomas a changé de smartphone et n'a pas re-fait `/start` → bot rejette silencieusement.
3. **Re-tenter dans 1 minute** : possible rate limit Telegram.
4. **Si toujours rien** : passer par fallback log manuel — éditer un fichier local `notes/trades-pending.txt` avec les valeurs, et logger via Replit Shell : `sqlite3 data/journal.sqlite "INSERT INTO trades (date, pl_brut_eur, mae_eur, mfe_eur, ...) VALUES (...);"` (consulter @fullstack pour le DDL exact).

---

## 5. Protocole décision GO/NO-GO mensuelle (détail)

<!-- Section 5 — détaillée par Edit -->

---

## Auto-évaluation gates

- [ ] G1 — cohérent personas.md (journée 8h40-9h05, RER, smartphone, 5 JTBD)
- [ ] G3 — zéro données inventées non marquées
- [ ] G7 — cohérent functional-specs US-08 à US-12 + REPLIT_ACTIONS J+7
- [ ] G12 — immédiatement actionnable par Thomas (pas de "TODO @fullstack")
- [ ] G15 — zéro placeholder non résolu
- [ ] G17 — zéro bullshit (pas de "buy now" sans chiffres)

---

## Handoff

**Handoff → @orchestrator (Phase 4 sales-enablement terminé)**

- Fichier produit : `/home/user/TradingApp/docs/sales/runbook-usage-personnel.md`
- Décisions prises : ce runbook est le **manuel opérationnel quotidien** de Thomas, pas un playbook commercial. Il s'utilise au smartphone le matin (procédure 8h40), tablette/PC vendredi 18h (audit hebdo), PC le 1er du mois (décision GO/NO-GO).
- Points d'attention : ce runbook **doit être imprimé ou mis en favori Telegram** (lien au pinned message) — Thomas a besoin de le retrouver en 2 clics dans le RER si bug.
- Pas de handoff secondaire (livrable terminal).
