# Infra Audit — TradingApp

> Auteur : @infrastructure — Date : 2026-05-01
> Mission : valider hypothèses H1, H2, H4 du `project-context.md` et proposer une architecture cible compatible cron jours ouvrés 8h40 CET, signal 8h45-8h55, push Telegram, R&D edge sur 5 ans Twelve Data, scoring Claude.
>
> **Lecture obligatoire amont** : `CLAUDE.md`, `_base-agent-protocol.md`, `_gates.md`, `project-context.md`.
>
> **Sources tarifs** :
> - Replit pricing : [replit.com/pricing](https://replit.com/pricing), [blog Replit Pro plan](https://blog.replit.com/pro-plan), [WeAreFounders 2026](https://www.wearefounders.uk/replit-pricing-what-you-actually-pay-to-build-apps/)
> - Twelve Data : [twelvedata.com/pricing](https://twelvedata.com/pricing), [docs](https://twelvedata.com/docs)
> - Anthropic : [platform.claude.com/docs/en/about-claude/pricing](https://platform.claude.com/docs/en/about-claude/pricing), [BenchLM April 2026](https://benchlm.ai/blog/posts/claude-api-pricing)

---

## 0. Résumé exécutif

| # | Hypothèse | Verdict | Justification courte |
|---|-----------|---------|----------------------|
| H1 | Replit Hacker ~7 €/mois suffit | **NEEDS-DECISION** | Le plan Hacker n'existe plus en 2026. Remplacé par **Core 20 $/mois annuel + crédits 25 $/mois** + **Always-On Deployment 5-20 $/mois en sus**. Budget cible 7 € → impossible sur Replit en 2026. Alternatives à arbitrer (Railway, Fly.io, Hetzner). |
| H2 | Twelve Data plan actuel couvre EU+FR+FX+commodities 1m sur 5 ans | **NEEDS-DECISION** (vérification compte requise) | L'intraday 1m est réservé au plan **Pro 79 $/mois (Individual)** ou supérieur. Couverture EU/FR/FX/commodities nécessite plan global (pas free). Volume R&D estimé OK avec rate limit 55-610 req/min selon plan + cache SQLite. |
| H4 | 1 appel Claude/signal × 22j tient < 10 €/mois | **PASS** | Sonnet 4.6 (3 $/15 $ par M tokens) en live 22 appels = **0,16 $/mois**. Haiku 4.5 R&D 500 appels/jour × 30 jours = **22,5 $** (au-dessus si gros prompt). Recommandation : Sonnet en live, Haiku en R&D batch (-50 %) avec cache prompt (-90 % cached input). |

**Coût total mensuel estimé (live 22 jours)** : **42-50 €/mois** (Replit Core + Always-On Deployment + Twelve Data Pro Individual + Claude Sonnet + buffer). Au-dessus du budget cible 17-35 €/mois mais en-dessous si on bascule hébergement vers Hetzner CX11 (~5 €/mois) ou Fly.io shared-cpu-1x (~2-5 €/mois).

**Verdict global** : H1 nécessite un arbitrage explicite (Replit Core 25 $/mois ou migration). H2 nécessite vérification du plan Twelve Data déjà payé par le persona (interface twelvedata.com/account). H4 PASS confortable.

---

## 1. H1 — Plan Replit suffisant ?

### 1.1 Plans Replit en mai 2026

| Plan | Prix | Crédits inclus | Always-On | Cron |
|------|------|----------------|-----------|------|
| Starter (free) | 0 $ | 0 $ | non | non |
| **Core** | **20 $/mois annuel** (25 $/mois mensuel) | **25 $/mois** | non, à payer en sus via Deployment | oui via Deployment Cron Jobs |
| Pro | 35 $/mois (équipe) | 35 $/mois | idem | oui |
| Enterprise | sur devis | n/a | idem | oui |

**Always-On Deployment** : facturation séparée 5-20 $+/mois selon ressources (RAM/CPU).
**Cron Jobs Deployment** : facturation à l'exécution via crédits.

> **Source primaire** : [WeAreFounders — Replit Pricing 2026](https://www.wearefounders.uk/replit-pricing-what-you-actually-pay-to-build-apps/) + [blog officiel Replit Pro](https://blog.replit.com/pro-plan).

### 1.2 Adéquation au besoin TradingApp

Le besoin réel est un **cron jours ouvrés à 8h40 CET, fenêtre d'exécution 5-10 min, total ~22 exécutions/mois × 10 min = ~220 min/mois CPU**.

- **Always-On 24/7 NON nécessaire** — l'app tourne 10 min/jour ouvré. Cron Job Deployment à l'exécution suffit.
- Si on choisit le **Cron Job Deployment**, la consommation crédits est marginale (quelques cents par exécution × 22 = quelques dollars/mois).
- Le plan **Core 20 $/mois annuel inclut 25 $ de crédits** → couvre largement le cron + R&D ponctuelle si on ne laisse pas tourner l'app en background.

### 1.3 Verdict H1

- **Hypothèse "Hacker ~7 €/mois" : FAIL** — ce plan n'existe plus en 2026.
- **Replit Core 20 $/mois annuel + Cron Job Deployment** : **PASS technique**, ~20-25 €/mois TTC effectif, **au-dessus du budget cible 7 € mais sous le plafond 25 €**.
- **Always-On 24/7 inutile** : ne pas le payer. Choisir Deployment "Cron Jobs" (paiement à l'exécution).

### 1.4 Alternatives si Replit Core 20 $/mois jugé trop cher

| Option | Prix | Pour | Contre |
|--------|------|------|--------|
| **Hetzner CX11** | 4,5 €/mois | Always-on 24/7, contrôle total, latence EU | Setup manuel (cron, systemd, monitoring), pas de PaaS |
| **Fly.io shared-cpu-1x** | 2-5 $/mois (free tier 256 MB possible) | Déploiement simple, scale-to-zero compatible cron via `fly machine run` | Cold start, machine config |
| **Railway** | ~5 $/mois minimum (usage-based) | Cron jobs natifs, GitHub deploy | Coût croissant si R&D longue, moins de free tier qu'avant |
| **GitHub Actions cron** | gratuit (2000 min/mois free tier private repo) | 0 € infra, planification cron native | Pas idéal pour signal time-critical (cron GitHub a 5-15 min de drift) — **incompatible G4 fenêtre 8h45 CET stricte** |

**Recommandation infra** :
1. **Court terme (MVP)** : Replit Core 20 $/mois annuel + Cron Job Deployment. Continuité avec habitude utilisateur, tooling intégré.
2. **Si budget < 10 €/mois absolu** : Hetzner CX11 + cron Linux + monitoring custom — surcoût en setup mais coût mensuel divisé par 4.
3. **NE PAS utiliser GitHub Actions cron** : drift incompatible fenêtre 8h45-8h55 (G4 BLOQUANT).

> **NEEDS-DECISION par @orchestrator + persona** : accepter le passage de 7 € à 20-25 €/mois sur Replit, OU migrer vers Hetzner/Fly.io.

---

## 2. H2 — Twelve Data couvre-t-il les besoins ?

### 2.1 Sous-jacents requis (issus du contexte persona)

**Indices EU** : CAC40, DAX, EuroStoxx50.
**Blue chips FR** : LVMH (MC.PA), TotalEnergies (TTE.PA), Sanofi (SAN.PA), Air Liquide (AI.PA), Schneider (SU.PA).
**FX** : EUR/USD, GBP/USD.
**Commodities** : XAU/USD (or), Brent (BRN), gaz naturel (TTF ou Henry Hub).

**Total : ~10 sous-jacents** (5 FR + 3 indices EU + 2 FX + 3 commodities = 13, on garde 10 prioritaires pour la R&D).

### 2.2 Couverture Twelve Data

D'après [twelvedata.com/market-data](https://twelvedata.com/market-data) et [twelvedata.com/commodities](https://twelvedata.com/commodities) :
- **Stocks EU/FR (Euronext Paris, Xetra)** : couvert (vérifier accès exchange dans le plan).
- **Indices CAC40/DAX/EuroStoxx50** : couvert via tickers `^FCHI`, `^GDAXI`, `^STOXX50E`.
- **FX EUR/USD, GBP/USD** : couvert (forex inclus dans tous plans payants).
- **Commodities XAU/USD, Brent, gaz** : couvert (catégorie commodities).

**Point critique** : l'**intraday 1m** n'est disponible qu'à partir du plan **Pro Individual (~79 $/mois) ou Venture Business**. Les plans inférieurs (Grow ~29 $/mois) limitent l'intraday à 5m+ ou exigent le module 1m en option.

> **Source** : [Twelve Data Pricing — Individual](https://twelvedata.com/pricing).

### 2.3 Volume requêtes R&D

Calcul brut **R&D edge sur 5 ans, 1m, 10 sous-jacents** :
- 1 jour ouvré ~8h de session × 60 min = **480 bougies 1m / sous-jacent / jour**
- 5 ans × ~252 jours ouvrés = **1260 jours**
- 480 × 1260 = **604 800 bougies / sous-jacent**
- × 10 sous-jacents = **~6 M bougies au total**

L'API Twelve Data renvoie jusqu'à **5000 bougies par requête** (`outputsize=5000`).
- **6 M / 5000 = ~1200 requêtes** pour télécharger l'historique complet R&D **une seule fois**.

**Rate limits** :
- Pro Individual : 55 req/min, 8 API credits/req pour timeseries 1m.
- 1200 req / 55 = **~22 min** pour rapatrier toute l'histoire à pleine cadence (avec backoff).

**En live** :
- 22 jours/mois × 10 sous-jacents × 1 requête (50-200 bougies) = **220 req/mois** = négligeable.

### 2.4 Stratégie cache local SQLite (BLOQUANT G15 rate limit)

> Règle d'or : **on télécharge UNE fois, on cache TOUT, on ne re-télécharge que l'incrément quotidien**.

```
data/
  market_cache.sqlite
    table candles_1m (symbol TEXT, ts TIMESTAMP, open, high, low, close, volume, PK(symbol, ts))
    table fetch_log (symbol, last_ts_fetched, fetched_at)
```

- Premier run R&D : full backfill 5 ans → ~22 min (one-shot).
- Run quotidien : delta `last_ts_fetched` → maintenant = ~480 bougies × 10 = 4800 bougies → 1 req/symbole = 10 req/jour.
- **Backup SQLite** : `cp market_cache.sqlite market_cache.$(date).sqlite.bak` quotidien sur volume persistant (et copie hors Replit hebdo via S3/R2 ou Drive — voir section 5.3).

### 2.5 Verdict H2

- **Couverture sous-jacents** : PASS (toutes les classes d'actifs sont supportées).
- **Intraday 1m sur 5 ans** : **NEEDS-DECISION** — dépend du plan déjà payé. Action persona : se connecter à twelvedata.com/account et confirmer "1-minute intraday + Europe stocks (Euronext, Xetra)" inclus.
- Si plan actuel < Pro Individual : **upgrade obligatoire à 79 $/mois Pro Individual** OU stratégie de fallback (intraday 5m → moins granulaire mais 5 ans accessible sur Grow 29 $/mois).
- **Volume R&D : PASS** avec stratégie cache SQLite (G15 BLOQUANT respecté).

---

## 3. H4 — Budget IA Claude < 10 €/mois ?

### 3.1 Tarifs Anthropic mai 2026

| Modèle | Input ($/M tokens) | Output ($/M tokens) | Batch (-50%) | Prompt cache (input -90%) |
|--------|--------------------|---------------------|---------------|---------------------------|
| **Claude Sonnet 4.6** | 3,00 | 15,00 | 1,50 / 7,50 | 0,30 input cached |
| **Claude Haiku 4.5** | 1,00 | 5,00 | 0,50 / 2,50 | 0,10 input cached |
| Claude Opus 4.7 | 5,00 | 25,00 | 2,50 / 12,50 | hors budget |

> **Source** : [Anthropic pricing officielle](https://platform.claude.com/docs/en/about-claude/pricing) + [BenchLM avril 2026](https://benchlm.ai/blog/posts/claude-api-pricing).

### 3.2 Estimation tokens / appel signal

Hypothèse signal :
- **Input** : 3-5 k tokens (contexte marché veille + bougies M1 condensées + indicateurs RSI/MACD/Bollinger + résumé news pré-marché). On retient **5 k input** (worst case).
- **Output** : 500-1000 tokens (justification structurée Telegram + score). On retient **1 k output**.

### 3.3 Calculs

**Live mensuel (22 jours, 1 appel/jour, Sonnet 4.6)** :
- Input : 22 × 5000 = 110 k tokens × 3 $/M = **0,33 $**
- Output : 22 × 1000 = 22 k tokens × 15 $/M = **0,33 $**
- **Total live = 0,66 $/mois ≈ 0,60 €/mois** ← très large marge sous 10 €.

**Live mensuel sur Haiku 4.5** :
- 22 × 5000 × 1 $/M + 22 × 1000 × 5 $/M = 0,11 + 0,11 = **0,22 $/mois** ← marginal.

**R&D 30 jours, 500 appels/jour, Haiku 4.5** :
- 500 × 30 = 15 000 appels
- Input : 15000 × 5000 = 75 M tokens × 1 $/M = **75 $**
- Output : 15000 × 1000 = 15 M tokens × 5 $/M = **75 $**
- **Total R&D Haiku full price = 150 $/mois** ← **HORS BUDGET**.

**R&D 30 jours, 500 appels/jour, Haiku 4.5 + batch -50% + prompt cache -90% input** :
- Si 80 % de l'input est cacheable (prompt système + contexte marché stable) :
  - Input cacheable : 75 M × 0,8 × 0,10 $/M = **6 $**
  - Input non cacheable : 75 M × 0,2 × 1 $/M = **15 $** (avec batch -50% → **7,5 $**)
  - Output : 75 $ × 50 % batch = **37,5 $**
  - **Total = ~51 $/mois** ← **encore au-dessus**, à arbitrer avec @ia.

**R&D 30 jours, 100 appels/jour, Haiku 4.5 batch + cache** :
- 100 × 30 = 3000 appels
- ~10 $/mois ← **PASS budget R&D modéré**.

### 3.4 Verdict H4 + recommandations

- **Live 22 appels/mois Sonnet 4.6** : PASS, < 1 $/mois. Sonnet recommandé pour **scoring final + génération message Telegram** (qualité justification = levier critique persona "pas confiance").
- **R&D 100 appels/jour Haiku 4.5 batch + cache prompt** : PASS, ~10 $/mois.
- **R&D 500 appels/jour** : NEEDS-DECISION — batch + cache obligatoires, sinon dépasse 50 $/mois. Coordination @ia + @data-analyst pour limiter le volume R&D ou itérer en plus petits batchs.

**Recommandation modèle** :
- **Live** : Claude Sonnet 4.6 (qualité > coût marginal).
- **R&D** : Claude Haiku 4.5 + **prompt caching obligatoire** + **batch API** quand workflow le permet.

---

## 4. Architecture cible

### 4.1 Schéma ASCII

```
                        ┌─────────────────────────────┐
                        │   Replit Cron Deployment    │
                        │   8h40 CET jours ouvrés     │
                        │   (Mon-Fri, hors fériés FR) │
                        └──────────────┬──────────────┘
                                       │ trigger
                                       ▼
              ┌────────────────────────────────────────────┐
              │   TradingApp Worker (Python ou Node TS)    │
              │   1) load .env via Replit Secrets          │
              │   2) check holiday calendar FR             │
              └─────┬──────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐         ┌──────────────────────────┐
        │  SQLite local cache      │◄────────┤  Twelve Data API         │
        │  market_cache.sqlite     │ delta   │  intraday 1m (10 ssj)    │
        │  - candles_1m            │ fetch   │  cap rate-limit + retry  │
        │  - fetch_log             │         └──────────────────────────┘
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  Backtester / Signal Engine      │
        │  - RSI, MACD, Bollinger, EMA     │
        │  - Edge logic (ORB / gap / etc)  │
        │  - Confidence score 1-10         │
        │  - Output : signal | no-trade    │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  Claude Sonnet 4.6 (Anthropic)   │
        │  - Justification structurée      │
        │  - Format Telegram concis        │
        │  - Timeout 30 s, fallback msg    │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  Telegram Bot API                │
        │  - sendMessage to TELEGRAM_CHAT  │
        │  - signal OU "pas de trade"      │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  SQLite journal trades           │
        │  - signal_log (id, ts, payload)  │
        │  - trade_journal (P&L, MAE/MFE)  │
        └──────────────────────────────────┘
```

### 4.2 Variables d'environnement (Replit Secrets — JAMAIS dans .env committé)

| Clé | Description | Source |
|-----|-------------|--------|
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram (BotFather) | t.me/BotFather |
| `TELEGRAM_CHAT_ID` | chat_id du persona (numérique) | `@userinfobot` |
| `TWELVEDATA_API_KEY` | Clé API Twelve Data | dashboard twelvedata |
| `ANTHROPIC_API_KEY` | Clé API Claude | console.anthropic.com |
| `LOG_LEVEL` | INFO en prod, DEBUG en R&D | défaut INFO |
| `TZ` | `Europe/Paris` (cron CET) | constante |
| `BACKUP_BUCKET_URL` | S3/R2 endpoint pour backup SQLite hebdo (optionnel) | provider externe |

> **`.env.example`** committé sans valeurs ; **`.env`** ignoré via `.gitignore`. Replit Secrets = source de vérité pour le runtime.

### 4.3 Persistance & cache

- **SQLite local** : `data/market_cache.sqlite` + `data/journal.sqlite`. Stockés dans un volume persistant (Replit Deployment supporte `/home/runner/<repl>/data` persistant ; sinon backup S3 obligatoire).
- **Backup automatisé** : `pg_dump` non applicable (SQLite). À la place : `sqlite3 .backup` quotidien + upload vers Cloudflare R2 (free tier 10 GB) ou Drive perso. RPO 24h, RTO 30 min.
- **Reconnexion SQLite** : ouvrir/fermer la connexion par run (pas de pool — cron court).

### 4.4 Logs structurés

Format JSON ligne par ligne (compatible `jq` + Replit log viewer) :
```json
{"ts":"2026-05-04T08:45:12+02:00","level":"INFO","stage":"twelvedata.fetch","symbol":"^FCHI","candles":480,"latency_ms":312}
{"ts":"2026-05-04T08:45:18+02:00","level":"INFO","stage":"signal.compute","decision":"BUY","symbol":"LVMH","entry":712.5,"sl":708.0,"tp":721.0,"confidence":7}
{"ts":"2026-05-04T08:45:22+02:00","level":"INFO","stage":"claude.call","model":"claude-sonnet-4-6","input_tokens":4827,"output_tokens":612,"cost_usd":0.0237}
{"ts":"2026-05-04T08:45:23+02:00","level":"INFO","stage":"telegram.send","status":200,"duration_ms":180}
```

Champs obligatoires : `ts` (ISO 8601 + offset), `level`, `stage`, `latency_ms`, `error` (si applicable).

---

## 5. Monitoring & alerting

### 5.1 Healthcheck cron (G4 BLOQUANT)

**Risque** : le cron Replit ne s'exécute pas à 8h40 CET → pas de signal → persona perd la fenêtre.

**Mitigation** :
1. À la fin de chaque run, le worker écrit un fichier `data/last_run.timestamp` ET fait un POST vers un **dead man's switch** ([healthchecks.io](https://healthchecks.io) free tier 20 checks).
2. Healthchecks.io configuré : alerte Telegram (canal personnel) si pas de ping reçu entre 8h41 et 9h00 CET un jour ouvré.
3. **Calendar des jours fériés FR** : librairie `holidays` (Python) ou `date-holidays` (Node) — vérifier avant d'exécuter (sinon faux positifs sur jours fériés).

### 5.2 Twelve Data fail (G15 BLOQUANT)

**Règle absolue** : **PAS DE SIGNAL FORCÉ** si données indisponibles ou incomplètes.

```python
try:
    candles = fetch_twelvedata(symbol, retries=3, backoff=2)
except (RateLimitError, NetworkError, IncompleteDataError) as e:
    log.error("twelvedata.fail", symbol=symbol, error=str(e))
    send_telegram("⚠️ Données indisponibles — pas de signal aujourd'hui.")
    raise SystemExit(0)  # exit clean, pas de retry forcé
```

### 5.3 Claude timeout / indispo

```python
try:
    justification = call_claude(prompt, model="claude-sonnet-4-6", timeout=30)
except (TimeoutError, AnthropicError) as e:
    log.error("claude.fail", error=str(e))
    send_telegram("⚠️ Système IA indisponible — signal brut envoyé sans justification narrative.\n" + raw_signal_text())
```

Le persona reçoit toujours quelque chose **si le signal a été calculé**. Pas de silence.

### 5.4 Backup SQLite

- **Quotidien (cron 23h CET)** : `sqlite3 data/journal.sqlite ".backup data/journal.$(date +%F).bak"` + rotation 14 jours.
- **Hebdomadaire (dimanche)** : upload `tar.gz` vers Cloudflare R2 (clé `BACKUP_BUCKET_URL`).
- **Restauration documentée dans `runbook.md`** (à produire par @fullstack).

### 5.5 Alerting (Telegram = canal opérationnel)

| Événement | Canal | Sévérité |
|-----------|-------|----------|
| Cron pas exécuté à 8h45 jour ouvré | Telegram persona via healthchecks.io | P0 |
| Twelve Data 3 retries échoués | Telegram persona (msg "données indispo") | P1 |
| Claude timeout | Telegram persona (signal brut envoyé) | P2 |
| Backup SQLite échoué 2 jours consécutifs | Telegram persona | P1 |
| Coût Claude > 5 $ sur 7 jours glissants | Telegram persona | P1 |

---

## 6. Sécurité

### 6.1 Repo privé GitHub (BLOQUANT)

- **Repo `private`** sur GitHub. Vérification : `gh repo view --json visibility`.
- **Aucun collaborateur** sauf le persona. Pas de team org.
- **Branch protection** sur `main` : require PR review uniquement si workflow multi-machines (optionnel solo).

### 6.2 Replit Secrets

- TOUTES les clés API dans Replit Secrets. **Aucune** dans le code, dans `.env` committé, dans les logs.
- `.gitignore` :
  ```
  .env
  .env.local
  data/*.sqlite
  data/*.bak
  *.log
  __pycache__/
  node_modules/
  .DS_Store
  ```

### 6.3 Rotation des clés

| Clé | Rotation | Procédure |
|-----|----------|-----------|
| `TELEGRAM_BOT_TOKEN` | Tous les 6 mois ou si exposé | BotFather → `/revoke` + `/token` + update Replit Secret |
| `TWELVEDATA_API_KEY` | Tous les 12 mois ou si exposé | dashboard twelvedata → regenerate + update Replit Secret |
| `ANTHROPIC_API_KEY` | Tous les 6 mois ou si suspicion | console.anthropic.com → revoke + new key + update Replit Secret |

### 6.4 Disclaimer README

À ajouter par @copywriter dans `README.md` :
> ⚠️ **Outil personnel non commercialisé**. Aucune des informations produites ne constitue un conseil en investissement. Pas de redistribution. Repo privé. Données financières personnelles incluses (`project-context.md` mentionne capital + P&L) — **ne jamais rendre ce repo public**.

### 6.5 Audit dépendances

- **Python** : `pip-audit` mensuel.
- **Node** : `npm audit --audit-level=high` à chaque PR + `dependabot.yml` activé sur GitHub.
- **Pas de package** non maintenu depuis > 2 ans dans le critical path.

---

## 7. Coût total mensuel estimé

| Poste | Live (22 j/mois) | R&D edge (1 mois) | Notes |
|-------|------------------|-------------------|-------|
| Replit Core (annuel) | 20 $ | 20 $ | inclut 25 $ crédits |
| Replit Cron Deployment | ~1-3 $ | ~5 $ | usage cron uniquement, pas always-on |
| Twelve Data Pro Individual | 79 $ | 79 $ | **nécessaire si 1m intraday confirmé requis** |
| Claude Sonnet 4.6 (live) | < 1 $ | n/a | 22 appels |
| Claude Haiku 4.5 (R&D) | n/a | 10-50 $ | 100-500 appels/jour, batch + cache |
| Cloudflare R2 backup | 0 $ | 0 $ | free tier |
| Healthchecks.io | 0 $ | 0 $ | free tier 20 checks |
| **Total live** | **~100 $/mois ≈ 90 €/mois** | — | dominé par Twelve Data Pro |
| **Total R&D (mois actif)** | — | **~115-160 $/mois ≈ 105-145 €/mois** | pic temporaire |

> **Dépassement budget cible 7-25 €/mois** : oui, principalement à cause de Twelve Data Pro Individual (79 $/mois) requis pour intraday 1m sur stocks EU.
>
> **Optimisations possibles** :
> 1. **Confirmer le plan Twelve Data déjà payé** — si Pro déjà actif, ce coût est sunk et hors budget mensuel marginal.
> 2. **Migrer Replit → Hetzner CX11 (4,5 €/mois)** : -15 €/mois.
> 3. **Limiter R&D à 100 appels/jour Haiku batch** : -40 $/mois pic R&D.
> 4. **Évaluer Twelve Data Grow (29 $/mois) avec intraday 5m** : -50 $/mois mais perte granularité — à arbitrer avec @data-analyst.

---

## 8. Synthèse verdicts vs gates BLOQUANTS

| Gate | Description | Statut |
|------|-------------|--------|
| **G4** | Cron 8h40 CET fiable jours ouvrés FR | **PASS** sous Replit Cron Deployment + healthchecks.io + holiday calendar FR |
| **G7** | Pas de signal forcé en cas de fail data | **PASS** par design (section 5.2) |
| **G12** | Bot Telegram envoi fiable + fallback | **PASS** (timeout + retry + msg fallback Claude) |
| **G13** | Repo privé + secrets sécurisés | **PASS** (section 6.1-6.3) |
| **G15** | Twelve Data rate limit & cache | **PASS** stratégie SQLite cache (section 2.4) |
| **G17** | Sous-jacents EU spécifiques (CAC40, blue chips FR, Brent, gaz) | **PASS** côté Twelve Data (couverture confirmée) ; **NEEDS-CHECK** côté Bourse Direct turbos (H3, hors scope @infrastructure) |

---

## 9. Décisions à arbitrer (NEEDS-DECISION)

| Décision | Owner | Délai |
|----------|-------|-------|
| Accepter Replit Core 20 $/mois OU migrer Hetzner/Fly.io | persona + @orchestrator | T0+2 |
| Confirmer plan Twelve Data actuel couvre 1m EU stocks 5 ans | persona | T0+1 (action persona simple) |
| Volume R&D acceptable : 100/j ou 500/j Claude Haiku | @ia + @data-analyst | T0+3 (avant phase R&D) |
| Stack Python vs Node TS (impacte libs cache + backtester) | @fullstack | T0+1 |

---

## Handoff

---
**Handoff → @orchestrator** (verdicts H1/H2/H4)

- Fichiers produits : `docs/infra/infra-audit.md`
- Décisions prises :
  - Architecture cible Cron Replit → SQLite cache → Twelve Data (delta) → Backtester → Claude Sonnet 4.6 → Telegram
  - Stratégie cache SQLite obligatoire pour respecter rate limits (G15)
  - Modèle Claude : Sonnet 4.6 en live (qualité justification = levier persona), Haiku 4.5 + batch + prompt cache en R&D
  - Monitoring : healthchecks.io (free) + alertes Telegram persona
- Points d'attention :
  - **H1 NEEDS-DECISION** : plan Hacker n'existe plus en 2026, Replit Core 20 $/mois OU migration. Décision persona requise.
  - **H2 NEEDS-DECISION** : confirmer plan Twelve Data inclut intraday 1m + Europe stocks (action persona dans dashboard twelvedata).
  - **H4 PASS** confortable.
  - Coût mensuel estimé 90-145 €/mois (vs cible 17-35 €/mois) — dominé par Twelve Data Pro Individual.
- **Actions Replit requises** :
  1. Créer un Replit Cron Deployment (pas Always-On).
  2. Configurer Replit Secrets : `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TWELVEDATA_API_KEY`, `ANTHROPIC_API_KEY`, `TZ=Europe/Paris`, `LOG_LEVEL=INFO`.
  3. Cron schedule : `40 8 * * 1-5` (Mon-Fri 8h40 CET — vérifier que Replit utilise bien `TZ=Europe/Paris` ou ajuster en UTC = `40 7` hiver / `40 6` été).
  4. Activer le volume persistant pour `data/` (SQLite cache + journal).

**Handoff secondaire :**
- @fullstack : implémenter le worker (Python ou Node TS — arbitrage stack), schéma SQLite, intégration Telegram + Claude + Twelve Data, gestion erreurs (sections 4-5).
- @data-analyst : valider stratégie cache + volume R&D acceptable (section 2.3-2.4 et 3.3).
- @ia : valider choix Sonnet live + Haiku R&D, configurer prompt caching (section 3.4).
---
