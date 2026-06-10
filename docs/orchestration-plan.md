<!-- Version: 2026-05-01T08:30 — @orchestrator — Plan initial Phases 0→5 TradingApp + note environnement sub-agent -->
# Plan d'orchestration — TradingApp

> ⚠️ **SUPERSEDED (2026-06-02) — CE PLAN DÉCRIT L'ARCHITECTURE LEGACY** (Phases 0-5 : Replit + `src/` Python + bot Telegram « 1 signal turbo/jour »).
> Le projet a **pivoté vers l'architecture v3** (GitHub Actions + git-as-storage, bulletin directionnel 12 actifs × 3 horizons, **mode shadow**). Le `legacy/` est **archivé**.
> **État réel et roadmap courante : voir `project-context.md`** (section État + Mémo de reprise). Ce fichier est conservé pour l'historique des Phases 0-2a (réellement livrées sur le legacy) mais n'est plus le plan actif.
> **Phase v3 en cours : mode shadow (état 2026-06-09, Session 4)** — **984 tests**. Backtest quant v1+v2 = **NO-GO, écarté comme jalon** (validation = shadow réel uniquement). **Refonte « 5 rapports/jour » LIVE** : mesure ouverture→clôture, 1 décision notée/jour, Briefing 7h / Suivis 12h-18h / Bilan 22h15 / Bilan semaine + **Manager** (4e agent), VPS déployé, page complète. **WIN RATE ONLY.** Prochaine étape : ~30 j shadow KPI>70% + calage ~23/06 (le Manager / ticket C : frein contre-momentum CAC) + Phase 2 news `nature`. Détail : `project-context.md` (source de vérité).

> Statut global : **PLAN PRODUIT LEGACY — superseded par v3 (cf. project-context.md)**
> Mode : **AUTOPILOT** phases 0→5, livraison complète, 100% gates PASS.
> Mise à jour : 2026-05-01

<!-- SESSION: phases=0 tasks_prod=0 tasks_consult=0 -->

> **NOTE ENVIRONNEMENT** : cette instance d'orchestrator a été invoquée comme sous-agent et n'a PAS accès au tool `Task` pour invoquer les sous-agents Phase 0. Le plan ci-dessous est produit, validé, prêt à exécuter — mais l'invocation des Tasks doit être faite par le top-level (utilisateur ou orchestrator parent) en relayant les prompts détaillés stockés dans la section "Prompts pré-rédigés Phase 0 — Batch 1" en fin de fichier.

## Résumé exécutif

- **Objectif projet** : Bot Telegram qui envoie 1 signal turbo justifié + backtesté par jour ouvré 8h45-8h55 CET, exécutable manuellement chez Bourse Direct par Thomas (capital 20-30 k€, levier 5-10 max x10 validé Thomas 2026-05-02).
- **Décisions clés (cadrage)** :
  1. R&D edge AVANT tout code de prod — la Phase 2 (build) ne démarre QUE si Phase 1 R&D edge a identifié ≥ 1 candidat avec backtest 5 ans positif.
  2. Pas de UI web (Telegram pur) → adaptations design/qa/seo.
  3. Usage 100% personnel, jamais redistribué → Phase 2d (testeur-client) marquée N/A justifié, mais Phase 1b/2c (testeur-persona Thomas) OBLIGATOIRES.
  4. Stack backend à arbitrer en Phase 0 : Python (continuité Finance) vs Node/Bun + TypeScript.
  5. 4 hypothèses H1-H4 à valider en Phase 0 (Replit plan, Twelve Data plan, catalogue Bourse Direct, budget IA).
- **Verdict GO/NO-GO final** : assumé possible — si R&D edge ne donne aucun candidat robuste sur 5 ans, no-go assumé (pas de live).

## Mode projet et calibration

- **Stade** : Idée → mode "nouveau projet"
- **Type** : API / produit technique sans UI → Phase 0 → 1 (R&D edge) → 2 (build) → 4 (procédures usage perso) → 5 (validation finale). Pas de Phase 3 contenu (pas de site public, mais @geo s'applique sur lisibilité messages Telegram).
- **Objectif** : Funnel ? Vitrine ? → **NI L'UN NI L'AUTRE** : outil interne, KPI = P&L net, pas conversion. Calibration = "outil personnel à valeur opérationnelle".
- **Budget** : 0 € marketing, ~7-25 €/mois Replit, ~10 €/mois IA, Twelve Data déjà payé.
- **Niveau technique persona** : Expert (trader expérimenté, code Finance déjà existant) → ton direct, technique, pas de vulgarisation.

## Phases — vue d'ensemble

| Phase | Statut | Agents | Livrables principaux | Gates clés |
|-------|--------|--------|----------------------|------------|
| 0 — Fondations | ✅ COMPLETE | @creative-strategy, @product-manager, @data-analyst, @ia, @infrastructure, @legal | brand-platform, personas, functional-specs, kpi-framework, ai-architecture, prompt-library, infra-audit (H1-H4), legal-audit, edge-rnd-brief | G1-G18 PASS |
| 0b — Agents testeurs | ✅ COMPLETE | @agent-factory | testeur-persona-thomas.md, testeur-backtest-edge.md (v1.1) | — |
| 1 — R&D edge + Expérience | ✅ COMPLETE | @data-analyst, @ia, @ux, @copywriter | edge-rnd-report v1.1 (6 conditions AND), edge-scoring-model v1.2 (7 SC, D1/D6 35/10), prompt-library v1.1 (TC-06/07/08 + H-D/H-G seuils), user-flows (5 flows, 24 frictions), message-templates v1.2 (14 exemples + expiration F24), score-distribution-simulation | G19, GP1-GP10 |
| 1b — Audits Phase 1 | ✅ COMPLETE | @reviewer (testeur-persona), @qa (testeur-backtest), @moi (proxy fondateur), @ia (auto-critical) | persona-test verdict AJUSTER, backtest-audit verdict RETRAVAILLER, audit @moi GO MODIFIÉ, audit @ia GO MODIFIÉ → 15 corrections appliquées | GP1-GP10 |
| 2a — Mini-jalon J+7 (R2 @moi) | ✅ COMPLETE | @infrastructure, @fullstack | REPLIT_ACTIONS.md, .replit, .gitignore, replit.nix, pyproject.toml, src/ (15 modules Python), tests/ (18 tests, 10 PASS local), README.md, .env.example | G20-G21, G31, pytest 10/10 |
| 2b — Backtester Wave 1 | À VENIR (priorité actuelle) | @fullstack, @data-analyst | src/backtester/ (data_loader, edges H-C+H-A, methodology.py, runner CLI, stats, report), tests E2E backtester | G22-G24 |
| 2c — Bot Telegram complet | À VENIR | @fullstack, @ia, @design | src/scoring/ (6 dim + 7 SC + tool use Anthropic), src/ai/ (anthropic SDK), 5 templates Telegram, fixtures TC-01 à TC-08, maquettes Telegram desktop+mobile | G25-G26 |
| 2d — Tests + boucle visuelle | À VENIR | @qa, @design | tests E2E 12 US, screenshots Telegram, methodology.py PRE-backtest | G27 |
| 2e — Revue testeur-persona-thomas | À VENIR | testeur-persona via @reviewer | persona-review-bot, verdict GO live | GP1-GP10 |
| 3 — Contenu / GEO Telegram | ADAPTÉ | @geo, @copywriter | geo-strategy Telegram lisibility, signal-copy enrichi | G16-G18 |
| 4 — Procédures usage perso | ADAPTÉ | @sales-enablement (runbook), @growth (rapport mensuel) | runbook-quotidien, decision-go-nogo-mensuelle, rapport-mensuel-auto | — |
| 5 — Conformité & Validation finale | À VENIR | @legal, @qa, @reviewer, testeur-persona | cross-review-report, final-audit, paper-trading 4-8 sem | G1-G32 + GP1-GP10 |

## Phase 0 — Fondations (en cours)

### Objectifs
1. Affiner le persona Thomas (frustrations, jobs-to-be-done, décision de trade).
2. Poser le positionnement et le ton de marque (Justifié · Concis · Backtesté).
3. Cadrer les specs fonctionnelles V1 (1 signal/jour, format message, no-trade autorisé, justification obligatoire).
4. Définir le KPI framework (P&L net, drawdown, win rate, MAE/MFE, win/loss ratio).
5. Architecture IA : Claude Sonnet vs Haiku, prompts scoring, garde-fous.
6. Audit infrastructure : H1 (Replit Hacker plan suffit), H4 (budget IA tient).
7. Audit légal : confirmer pas d'obligation AMF tant que perso, repo privé GitHub.

### Agents et batchs

**Batch 1 (parallèle)** :
- @creative-strategy → `docs/strategy/brand-platform.md` + `docs/strategy/personas.md`
- @legal → `docs/legal/legal-audit.md`
- @infrastructure → `docs/infra/infra-audit.md` (validation H1, H4)

**Batch 2 (séquentiel après batch 1)** :
- @product-manager → `docs/product/functional-specs.md` (lit brand-platform + personas)
- @data-analyst → `docs/analytics/kpi-framework.md` (lit brand-platform + personas)

**Batch 3 (parallèle après batch 2)** :
- @ia → `docs/ia/ai-architecture.md` (lit functional-specs + kpi-framework)

### Hypothèses Phase 0

H1 : Replit Hacker (~7 €/mois) suffit — @infrastructure tranche.
H2 : Twelve Data plan actuel couvre EU+FR+FX+commodities en 1m sur 5 ans — @infrastructure + @data-analyst croisent.
H3 : Bourse Direct catalogue turbos couvre tous les sous-jacents retenus — @product-manager liste + persona vérifie.
H4 : 1 appel Claude/signal × 22j/mois reste sous 10 € — @ia chiffre.

### Critère de done Phase 0

- 6 livrables produits, gates BLOQUANT G1, G3, G5, G7, G12, G13, G15, G17 PASS sur chacun.
- 11 critères de cohérence Étape 6 PASS.
- Hypothèses H1-H4 tranchées (PASS / FAIL / NEEDS-DECISION).
- Checkpoint persona OBLIGATOIRE : présenter au persona, attendre validation explicite avant Phase 0b/1.

## Phase 0b — Agents testeurs (conditionnelle, lancée après checkpoint)

- @agent-factory crée `testeur-persona-thomas.md` (incarne Thomas : trader exp, capital 20-30k€, allergie aux dashboards, exige justification structurée).
- Pas de testeur-client (usage 100% perso).

## Phase 1 — R&D edge + Expérience

### Sous-phase 1a : R&D edge (priorité absolue, structurante)

- @data-analyst → `docs/analytics/edge-rnd-report.md` : exploration ≥ 6 hypothèses (gap follow / fade, ORB, momentum overnight US→EU, news pré-marché, écart spot/futures, sentiment Asie). Backtest 5 ans Twelve Data. Statistiques : win rate, profit factor, Sharpe, drawdown, robustesse out-of-sample.
- @ia → `docs/ia/edge-scoring-model.md` : design du scoring multi-dimension (input edge + indicateurs + news → score 1-10).
- **Décision intermédiaire** : si aucun edge avec backtest 5y positif robuste → STOP, no-go assumé, mémo "no-go documenté" + Phase 2 annulée.

### Sous-phase 1b : Expérience (parallèle 1a si possible)

- @ux → `docs/ux/user-flows.md` : parcours quotidien Thomas 8h40-9h05 (réveil → check Telegram → décision trade → exécution Bourse Direct → log).
- @copywriter → `docs/copy/message-templates.md` : 3 formats messages Telegram (ACHAT, VENTE, NO-TRADE) tirés du ton brand "Justifié · Concis · Backtesté".

### Phase 1b — Revue testeur-persona stratégie

- testeur-persona-thomas évalue brand-platform + personas + functional-specs + edge-rnd-report + message-templates → gates GP1-GP10.

## Phase 2 — Build (après validation R&D edge)

### Préparation
- @infrastructure : setup Replit (cron 8h40 CET, env vars, secrets, monitoring), repo privé.
- @fullstack : arbitrage stack (Python vs Node/Bun) + skeleton.

### Build
- @ia → prompt-library.md AVANT @fullstack code la couche LLM.
- @fullstack → bot Telegram + backtester + journal SQLite (ordre strict : schema DB → API/cron → logique edge → intégration LLM → polish).
- @design → maquettes des messages Telegram (rendu Markdown sur Telegram desktop + mobile + favicon repo). Boucle visuelle adaptée : screenshots messages réels rendus.
- @qa → tests E2E (signal envoyé, no-trade, robustesse Twelve Data down, fail Telegram).

### Phase 2c — Revue testeur-persona bot
- testeur-persona-thomas teste le bot en simulation (paper-trading) → gates GP1-GP10.

### Phase 2d — Revue testeur-client : **N/A JUSTIFIÉ** (usage 100% personnel, jamais redistribué — confirmé project-context.md ligne 67-71).

## Phase 3 — Contenu (adaptée Telegram pur)

- @geo → `docs/geo/geo-strategy.md` : lisibilité messages Telegram, structure (titre, justification, score, backtest), accessibilité par Thomas en mobilité 8h45.
- @copywriter → enrichissement message-templates avec justifications types (gap fade vs follow vs ORB).
- SEO @seo : N/A justifié (pas de site web public).

## Phase 4 — Procédures usage personnel

- @sales-enablement → `docs/sales/runbook-quotidien.md` (procédure 8h40-9h05 Thomas) + `docs/sales/decision-go-nogo-mensuelle.md` (template audit fin de mois P&L vs drawdown).
- @growth → `docs/growth/rapport-mensuel-auto.md` : générateur de rapport mensuel auto (P&L net, drawdown, win rate, top trades, anomalies).
- @social : N/A (pas de communication externe).

## Phase 5 — Conformité & Validation finale

- @legal : revue finale (rappel : repo privé, perso, pas AMF).
- @qa → revue chirurgicale 21 dimensions (adaptée artefacts : code bot + messages Telegram + journal SQLite).
- @reviewer → cross-review report toutes phases.
- testeur-persona-thomas → revue finale GP1-GP10 sur bot final (paper-trading 1 semaine simulée).
- @fullstack → vérification screenshots messages Telegram + baselines.

### Critère GO final
- 100% gates BLOQUANT PASS (G1-G32 applicables + GP1-GP10).
- Persona Thomas validation ≥ 9/10.
- 4-8 semaines paper-trading concluant (HORS scope automatisé : Thomas exécute manuellement, on livre l'outil et le runbook).

## Suivi des hypothèses

| ID | Hypothèse | Owner | Statut | Verdict |
|----|-----------|-------|--------|---------|
| H1 | Replit Hacker (~7 €/mois) suffit always-on + cron | @infrastructure | À VALIDER (Phase 0) | — |
| H2 | Twelve Data plan couvre EU+FR+FX+commo en 1m sur 5 ans | @infrastructure + @data-analyst | À VALIDER (Phase 0) | — |
| H3 | Bourse Direct catalogue turbos sur tous sous-jacents retenus | @product-manager + persona | À VALIDER (Phase 0) | — |
| H4 | 1 appel Claude/signal × 22j tient < 10 €/mois | @ia | À VALIDER (Phase 0) | — |

## Adaptations spécifiques TradingApp

- **Pas de B2B** : Phase 2d (testeur-client) N/A justifié.
- **Pas de UI web** : @design produit maquettes messages Telegram + favicon repo. @seo N/A justifié, @geo s'applique sur lisibilité Telegram.
- **@sales-enablement** : transposé en playbook usage personnel (runbook quotidien + audit mensuel).
- **@growth earned media** : transposé en rapport mensuel auto-généré.
- **Boucle visuelle G24/G26** : adaptée — screenshots réels du rendu Markdown Telegram desktop + mobile (simulateur ou app réelle), comparés aux maquettes @design.
- **Phase 1 R&D edge structurante** : Phase 2 conditionnelle au verdict R&D edge. No-go assumé si edge non robuste.

## Suivi d'exécution (mis à jour après chaque batch)

| Batch | Phase | Agents | Lancé | Verdict | Gates | Décisions extraites |
|-------|-------|--------|-------|---------|-------|---------------------|
| 1 | 0 | @creative-strategy, @legal, @infrastructure | 2026-05-01 | EN COURS | — | — |

## Prochaine action

**Lancer Batch 1 Phase 0** : @creative-strategy + @legal + @infrastructure en parallèle (3 Task dans le même message).

## Mémo de reprise

Si session coupée : commande de reprise = `Lis project-context.md et docs/orchestration-plan.md, continue où on s'est arrêté.`

---

## Prompts pré-rédigés Phase 0 — Batch 1 (à invoquer par le top-level)

### Task 1 — @creative-strategy (parallèle)

**description** : `Phase 0 — Brand platform + persona Thomas`
**subagent_type** : `creative-strategy`
**prompt** :

```
Contexte projet (résumé pré-digéré) :
- Nom : TradingApp (provisoire)
- Secteur : Day-trading turbos personnel — fenêtre EU 8h45-9h CET
- Stade : Idée
- Persona : Thomas, trader particulier expérimenté, France, capital dédié 20-30 k€, levier 5-10 turbos (max x10 validé Thomas 2026-05-02), taille position 1000-2000 €, exécution manuelle Bourse Direct, dispo 8h45-9h chaque jour ouvré.
- Frustrations (verbatims) : « pas assez d'éléments pour engager 1500 € avec levier 10 », « pas envie d'ouvrir un dashboard tous les matins », « un seul signal clair par jour ouvré, pas dix indicateurs qui se contredisent », « préfère un no-trade honnête à une reco forcée ».
- Promesse : 1 signal turbo/jour ouvré 8h45-8h55 CET, justifié (entrée + SL + TP + raison + score + ref backtest) et backtesté 5 ans, sur Telegram, exécutable < 5 min Bourse Direct.
- 3 mots brand : Justifié · Concis · Backtesté
- 3 mots anti-brand : Generic · Hype · Boîte noire
- Modèle : 100% personnel, jamais redistribué.
- Stack : pas de UI web, bot Telegram, backend Python ou Node à arbitrer, Twelve Data, Anthropic Claude, Replit always-on.

Mission : produire 2 livrables stratégiques affinés à partir du project-context.md déjà rempli. Ne pas repartir de zéro.

1. docs/strategy/brand-platform.md : positionnement (1 phrase), promesse interne, tone of voice (5 do's + 5 don'ts copy), 3 piliers de marque, anti-personnalité, section "Agents spécialisés recommandés" (testeur-persona-thomas confirmé, pas de testeur-client).

2. docs/strategy/personas.md : Thomas affiné (profil, équipement, journée type 8h40-9h05, historique trading, drawdown signaux d'arrêt), Jobs-to-be-done (3-5), frustrations enrichies, critères de pull-the-trigger, persona client-de-client = N/A explicite.

Contraintes : ANTI-TIMEOUT (Write structure d'abord, Edit ensuite, max 150 lignes/Write). Zéro placeholder. Typographie FR. Pas de mention concurrent par nom.

Critères BLOQUANT : G1, G3, G5 (Thomas ≥ 5 fois), G7, G12, G15, G17, G18 (≥ 1 scénario daté concret).

Handoff vers @product-manager, @data-analyst, testeur-persona-thomas.

ANTI-TIMEOUT : écris le fichier IMMÉDIATEMENT après lecture. Write d'abord, Edit ensuite.
```

### Task 2 — @legal (parallèle)

**description** : `Phase 0 — Audit légal usage perso`
**subagent_type** : `legal`
**prompt** :

```
Contexte : TradingApp, bot trading 100% personnel France, persona Thomas, capital 20-30 k€, turbos Bourse Direct, Twelve Data + Anthropic Claude, repo GitHub privé, jamais redistribué.

Mission : produire docs/legal/legal-audit.md couvrant les 9 sections suivantes :
1. Statut AMF/MiFID II — confirmer non-conseil tant que perso (Code monétaire et financier, position AMF). Conditions si redistribution future (CIF).
2. RGPD — chat_id Telegram identifiant indirect, journal P&L = données personnelles. Bonnes pratiques.
3. Repo GitHub privé — règles secrets, .gitignore strict, risques fuite.
4. Twelve Data CGU — usage perso autorisé ? Restrictions redistribution.
5. Bourse Direct — exécution manuelle = aucun risque conformité broker.
6. Anthropic Claude — données envoyées (publiques marché + signaux), pas de PII. Politique rétention. Zero Data Retention si possible.
7. Fiscalité — PFU 31,4% (12,8% IR + 18,6% PS, taux 2025+) turbos CTO, formulaire 2074, recommandation journal trades.
8. Risques redistribution future — paliers vers CIF.
9. Limitation responsabilité — disclaimer README repo.

Contraintes : ANTI-TIMEOUT. Citer sources précises (articles Code monétaire et financier, AMF, RGPD). Si CGU inaccessibles → [HYPOTHÈSE — vérifier CGU à jour]. Pas d'invention juridique.

Critères BLOQUANT : G4 (sources), G5, G13 (0 invention), G15, G17 (spécifique turbos/Bourse Direct/Twelve Data).

Handoff vers @orchestrator, @fullstack (sécurité repo), @ia (politique Claude).

ANTI-TIMEOUT : écris le fichier IMMÉDIATEMENT après lecture. Write d'abord, Edit ensuite.
```

### Task 3 — @infrastructure (parallèle)

**description** : `Phase 0 — Audit infra H1+H2+H4`
**subagent_type** : `infrastructure`
**prompt** :

```
Contexte : TradingApp, bot Telegram, cron Replit jours ouvrés 8h40 CET, calcul signal 8h45-8h55, push Telegram immédiat. Données Twelve Data (compte payant déjà actif). LLM Anthropic Claude (Sonnet ou Haiku). Volume IA : 22 appels/mois live + 100-500/jour phase R&D edge. Budget Replit ~7-25 €/mois, IA < 10 €/mois live. Repo GitHub privé.

Mission : produire docs/infra/infra-audit.md qui valide H1, H2, H4 et propose architecture cible.

Sections :
1. H1 — Replit Hacker (~7 €/mois) suffit always-on + cron ? Comparer plans Replit 2026. Verdict PASS/FAIL/NEEDS-DECISION + alternatives (Railway, Fly.io, Hetzner) si FAIL.
2. H2 — Twelve Data plan couvre EU+FR+FX+commodities en 1m sur 5 ans ? Lister sous-jacents (CAC40, DAX, EuroStoxx50, blue chips FR LVMH/TotalEnergies/Sanofi/Air Liquide/Schneider, EUR/USD, GBP/USD, XAU/USD, Brent, gaz). Calculer volume requêtes R&D 5 ans × 10 sous-jacents × 1m. Verdict + plan recommandé. Stratégie cache local SQLite si rate limit.
3. H4 — 1 appel Claude/signal × 22j tient < 10 €/mois ? Estimer tokens (input 3-5k, output 500-1k). Coûts Sonnet vs Haiku 2026. Calcul mensuel live + R&D 30-90 jours. Recommandation modèle (Sonnet scoring final, Haiku R&D ?).
4. Architecture cible — schéma ASCII Cron→Twelve Data→backtester→Claude→Telegram. Variables env (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TWELVEDATA_API_KEY, ANTHROPIC_API_KEY). SQLite local. Logs structurés.
5. Monitoring — healthcheck cron (alerte si pas exécuté à 8h45), Twelve Data fail (pas de signal forcé), Claude timeout (message "système indispo"). Backup SQLite daily.
6. Sécurité — repo privé, Replit Secrets, .gitignore, disclaimer README, rotation keys.
7. Coût total mensuel estimé.

Contraintes : ANTI-TIMEOUT. Pas d'invention tarif (si 2026 inaccessible → [HYPOTHÈSE — tarif 2025 retenu, à vérifier]). Recommander Replit Hacker en premier sauf FAIL clair.

Critères BLOQUANT : G4, G7, G12, G13, G15, G17 (cron 8h40 CET, turbos, Twelve Data EU spécifiques).

Handoff vers @fullstack, @data-analyst (rate limit R&D), @ia (modèle Claude), @orchestrator (verdicts H1/H2/H4).

ANTI-TIMEOUT : écris le fichier IMMÉDIATEMENT après lecture. Write d'abord, Edit ensuite.
```

## Prompts pré-rédigés Phase 0 — Batch 2 (séquentiel après Batch 1)

### Task 4 — @product-manager

**description** : `Phase 0 — Functional specs V1`
**subagent_type** : `product-manager`
**prompt** :

```
Contexte : TradingApp, bot Telegram 1 signal/jour ouvré 8h45-8h55 CET, justification + backtest, exécution manuelle Bourse Direct, persona Thomas (capital 20-30 k€, turbos levier 5-10 max x10).

Lire AVANT : docs/strategy/brand-platform.md, docs/strategy/personas.md (produits par @creative-strategy), docs/infra/infra-audit.md (verdicts H1/H2/H4), project-context.md (héritage Finance, décisions structurantes).

Mission : produire docs/product/functional-specs.md V1.

Sections :
1. User stories V1 (max 8) avec format Given/When/Then + 5 états UI (mais ici "états du signal Telegram" : ACHAT, VENTE, NO-TRADE, ERREUR DATA, DEGRADED MODE), critères validation binaires, events analytics (signal_envoyé, no_trade, erreur_twelvedata, erreur_claude, signal_lu_par_thomas inferred).
2. Format message Telegram — détailler les 3 templates (ACHAT / VENTE / NO-TRADE) avec champs obligatoires : sous-jacent, sens, niveau d'entrée, SL, TP, raison (1-3 lignes), score confiance 1-10, ref backtest (lien ou ID), heure.
3. Liste sous-jacents V1 — basée sur infra-audit H3 et héritage Finance. Hypothèse H3 (Bourse Direct catalogue turbos) à VALIDER : lister CAC40, DAX, EuroStoxx50, top 5 blue chips FR, EUR/USD, XAU/USD, Brent. Marquer ceux qui ne sont pas couverts par Bourse Direct comme [À VÉRIFIER PAR PERSONA].
4. Règles métier — un seul signal/jour, no-trade autorisé explicite, justification obligatoire, pas de signal après 8h55 (cutoff), pas de signal hors jours ouvrés EU.
5. Hors scope V1 — exécution auto, multi-signaux, dashboard web, monitoring positions, alertes mid-day.
6. Roadmap — V1 (bot + backtester + journal) → V1.1 (auto-update bot post-trade : Thomas log son trade et bot affine) → V2 (peut-être notification mi-journée si edge "lunch fade" trouvé en R&D).
7. Section "Agents spécialisés recommandés" — confirmer testeur-persona-thomas, ajouter @ia (prompt-library obligatoire avant code LLM), pas de testeur-client.

Contraintes : ANTI-TIMEOUT. Spécifications implémentables sans ambiguïté. Chaque US a événement analytics. États du signal explicites.

Critères BLOQUANT : G1, G3, G5, G6 (KPI North Star = P&L net cité), G7 (cohérent brand-platform + personas + infra-audit), G12, G15, G17.

Handoff vers @ia (prompt-library), @fullstack (skeleton), @data-analyst (kpi-framework), @ux (user-flows).

ANTI-TIMEOUT : écris le fichier IMMÉDIATEMENT après lecture. Write d'abord, Edit ensuite.
```

### Task 5 — @data-analyst (parallèle de Task 4 si infra OK)

**description** : `Phase 0 — KPI framework + edge brief`
**subagent_type** : `data-analyst`
**prompt** :

```
Contexte : TradingApp, bot Telegram 1 signal/jour, persona Thomas trader perso. KPI North Star = P&L net mensuel après frais (turbos Bourse Direct ~0,99 € + spread émetteur) et fiscalité PFU 31,4% (taux 2025+, source @legal). Objectif secondaire : drawdown mensuel max < 20% capital dédié.

Lire AVANT : docs/strategy/brand-platform.md, docs/strategy/personas.md, project-context.md (verbatims persona, héritage Finance "garde MAE/MFE journal").

Mission : produire 2 livrables.

1. docs/analytics/kpi-framework.md :
   - Métrique North Star : P&L net mensuel (formule : Σ (gain_brut_trade - frais_BD - spread_émetteur) - PFU_30% sur résultat positif annuel; seuil alerte mensuel = -10% capital).
   - Métriques secondaires : drawdown mensuel max (seuil 20%), win rate (seuil minimum), profit factor (seuil 1.5+), Sharpe ratio annualisé, MAE/MFE moyens (héritage Finance, lib trackers à reprendre).
   - Métriques de qualité signal : score confiance moyen, % no-trade jours, latence push Telegram (seuil 8h55), taux d'erreur Twelve Data, taux d'erreur Claude.
   - Plan d'instrumentation (events à tracker dans SQLite journal) — schema table_signals + table_trades.
   - Dashboard de suivi : 1 rapport mensuel auto-généré (à produire par @growth en Phase 4).
   - Critère GO/NO-GO continuer la stratégie : 3 mois consécutifs P&L positif net + drawdown < 20%, sinon revoir edge.

2. docs/analytics/edge-rnd-brief.md (BRIEF — pas le rapport R&D complet, qui sera Phase 1) :
   - Objectif Phase 1 R&D : identifier ≥ 1 edge robuste sur 5 ans Twelve Data.
   - Hypothèses d'edge à tester (≥ 6) : (a) gap follow EU open, (b) gap fade EU open, (c) Opening Range Breakout 5/15 min, (d) momentum overnight US→EU (S&P futures → CAC), (e) news pré-marché (continuité scoring news Finance), (f) écart spot/futures à l'ouverture, (g) sentiment overnight Asie (Nikkei → CAC corrélation).
   - Méthodologie : in-sample 2021-2024, out-of-sample 2025, walk-forward analysis, transaction costs réalistes (frais BD + spread + slippage 0.1%).
   - Statistiques requises par hypothèse : nombre de trades, win rate, profit factor, Sharpe, max drawdown, avg trade duration, robustesse (Sharpe out-of-sample > 50% in-sample).
   - Décision : si aucun edge avec Sharpe out-of-sample > 1 ET profit factor > 1.5 ET drawdown < 20% → no-go assumé, pas de Phase 2.
   - Outils : pandas, vectorbt OU backtesting.py (héritage Finance) ; stack code à arbitrer @fullstack.

Contraintes : ANTI-TIMEOUT. Chaque KPI a formule + seuil d'alerte (G23). Pas d'invention de chiffre.

Critères BLOQUANT : G1, G3, G5, G6, G7, G12, G13, G15, G17, G23.

Handoff vers @ia (scoring model integré dans signal), @fullstack (schema SQLite), Phase 1 (R&D edge).

ANTI-TIMEOUT : écris le fichier IMMÉDIATEMENT après lecture. Write d'abord, Edit ensuite.
```

## Prompts pré-rédigés Phase 0 — Batch 3 (après Batch 2)

### Task 6 — @ia

**description** : `Phase 0 — AI architecture + scoring`
**subagent_type** : `ia`
**prompt** :

```
Contexte : TradingApp, signal turbo quotidien 8h45-8h55 CET, scoring multi-dimension via Claude (Sonnet ou Haiku), génération justification structurée Telegram. Volume : ~22 appels/mois live + 100-500/jour R&D. Budget < 10 €/mois live.

Lire AVANT : docs/strategy/brand-platform.md, docs/strategy/personas.md, docs/product/functional-specs.md, docs/analytics/kpi-framework.md, docs/analytics/edge-rnd-brief.md, docs/infra/infra-audit.md (verdict H4 + modèle recommandé), docs/legal/legal-audit.md (politique données envoyées Claude).

Mission : produire docs/ia/ai-architecture.md.

Sections :
1. Choix modèle — Sonnet 4.x vs Haiku 4 (coût, latence, qualité scoring). Justifier choix unique OU split (Haiku R&D itérations / Sonnet signal final). Citer infra-audit pour les chiffres.
2. Architecture prompts — schema input scoring (données marché : OHLC last 5 jours + indicateurs RSI/MACD/Bollinger + news titres pré-marché + edge signature : si edge "gap follow" alors features X, Y, Z), schema output (score 1-10 + raison 2-3 lignes + flag ALERT/SAFE/NO-TRADE).
3. Anti-hallucination — règles strictes : pas d'invention de chiffres marché, pas d'inférence sur news non-fournies, scoring déterministe (température basse), retry si JSON parse fail.
4. Garde-fous — circuit breaker si N erreurs consécutives, fallback "système indisponible" si Claude down (cohérent monitoring infra-audit), timeout 30s.
5. Politique données — confirmer (cf legal-audit) qu'aucune PII n'est envoyée. Activer Zero Data Retention Anthropic si plan le permet. Documenter le contenu type d'un appel.
6. Test cases — 5 inputs réalistes avec output attendu (1 ACHAT confiance 8, 1 VENTE confiance 7, 1 NO-TRADE faible signal, 1 NO-TRADE conflit news/technique, 1 erreur fallback).
7. Coût détaillé — tokens par appel × tarif × volume = budget mensuel live + R&D. Verdict H4 confirmé ou ajusté.
8. Section "Migration modèle IA" — protocole pour upgrade Sonnet quand nouvelle version sort (re-tester sur les 5 cases, comparer outputs, basculer si pas de régression).

Contraintes : ANTI-TIMEOUT. Test cases avec vrais inputs/outputs réalistes du persona Thomas. Pas d'invention prix tokens.

Critères BLOQUANT : G1, G3, G5, G6, G7, G12, G13, G15, G17. Vrais outputs : générer ≥ 1 exemple complet (input + prompt complet + output attendu).

Handoff vers @fullstack (intégration LLM Phase 2), @data-analyst (R&D edge Phase 1).

ANTI-TIMEOUT : écris le fichier IMMÉDIATEMENT après lecture. Write d'abord, Edit ensuite.
```

## Checkpoint Phase 0 — Validation persona OBLIGATOIRE

Après les 6 livrables Phase 0 (Batchs 1+2+3), AVANT toute Phase 0b/1, l'orchestrateur top-level DOIT :

1. Lire les 6 livrables produits.
2. Vérifier les 11 critères de cohérence (Étape 6) sur chacun.
3. Vérifier gates BLOQUANT (G1, G3, G5, G6, G7, G12, G13, G15, G17) via Grep.
4. Synthétiser pour Thomas :
   - Persona affiné (résumé 5 lignes)
   - Positionnement (1 phrase)
   - KPI North Star + seuils alerte
   - Verdicts H1/H2/H3/H4 (PASS/FAIL/NEEDS-DECISION + impacts)
   - Scope V1 confirmé
   - Brief R&D edge (les 6 hypothèses à tester en Phase 1)
   - Risques juridiques (synthèse 3 lignes)
5. Présenter à Thomas et **ATTENDRE validation explicite** avant de lancer Phase 0b (création testeur-persona-thomas) puis Phase 1 (R&D edge).
6. Si Thomas conteste un point → relance corrective sur l'agent concerné, re-vérification, re-checkpoint.

**STOP autopilot ici** : la R&D edge est structurante (Phase 2 dépend de son verdict). Le persona doit valider les fondations avant qu'on engage 30-90 jours de calculs Twelve Data + Claude.

## Suivi exécution Batch 1 (à mettre à jour par le top-level après réception)

| Task | Agent | Lancé | Reçu | Verdict gates | Décisions extraites |
|------|-------|-------|------|---------------|---------------------|
| 1 | @creative-strategy | À LANCER | — | — | — |
| 2 | @legal | À LANCER | — | — | — |
| 3 | @infrastructure | À LANCER | — | — | — |
