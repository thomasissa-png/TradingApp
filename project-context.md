# Contexte Projet — TradingApp v3

> Lu par tous les agents avant toute action.
> **Repo privé** (données financières personnelles). Dernière mise à jour : 2026-06-01.
> **Source de vérité produit complète : vault Drive `Bourse/Bourse.md`** (ce fichier en est le résumé technique).

## En une phrase

Système qui produit **3 fois par jour (7h/12h/18h CET)** un **bulletin de positionnement directionnel** sur **12 actifs × 3 horizons (24h/7j/1m)** : chaque cellule tranche **LONG ou SHORT**. Thomas (trader humain) lit le bulletin et exécute manuellement des turbos chez Bourse Direct. Le système ne place jamais d'ordre.

## Objectif (NON NÉGOCIABLE)

⚠️ **On ne cherche PAS l'edge à la minute.** Un retard de 4h sur une news n'est pas grave.
But = **être certain de la TENDANCE par actif**, pour **suivre les vagues de hausse/baisse dans le bon sens, sans erreur de direction**. C'est du **trend-following directionnel**, pas du front-running de news. Tout raisonnement qui critique la *vitesse de capture* est hors-sujet.

## Architecture (30/05/2026)

- **GitHub Actions + git-as-storage** — scripts Python, **sans VPS, sans Cowork, sans Drive**. Coût infra 0 €.
- Workflow unique `cycle-decision` (cron 3×/jour) enchaîne : **ingest** (26 sources + extraction DeepSeek) → **critères** (Twelve Data/CFTC/EIA/Open-Meteo + triplets news) → **bulletin** (scoring + Briefing) → **mesure** (Journaliste). Commit git atomique.
- Tout le système est dans **`v3/`**. Données et historiques commités dans `v3/data/`.

## Méthode

- Score pondéré de critères par actif × horizon → LONG si >0, SHORT sinon (jamais neutre).
- 2 types de critères : **numériques** (prix, z-scores, COT, météo — cœur de la tendance) + **événementiels** (news, direction donnée par DeepSeek = contexte).
- **A/B** : score **±1** (référence) + score **pondéré** (matérialité×fiabilité) calculés en parallèle, mesurés ; activation du pondéré sur preuve.
- **Observabilité** : `decision-log` JSONL par cycle (tout tracé, historique git requêtable).

## KPI

Taux de réussite > **70 %** + Brier < 0,25 par cellule (30 dernières conclusions). Mesure A/B dans `v3/data/performance-ab.md`. Kill criterion : `v3/KILL-CRITERION.md`.

## État (01/06/2026)

- ✅ Système v3 en **mode shadow** (cron 3×/jour, rien émis). **360 tests** verts.
- ✅ Pipeline complet sur vraies données : **indices via ETF Twelve** (SPY/QQQ/FCHI/VIXY… — yfinance bloqué sur les runners CI), métaux/commodities Twelve, taux FRED, vol CBOE, news DeepSeek. 0 tie-break, ~117 critères/run.
- ✅ **Boucle prédiction→mesure fermée** : prix d'émission stampés, conclusions VRAI/FAUX (Journaliste), KPI Wilson/Brier en warm-up.
- ✅ Session 01/06 (cf. Historique) : synthèse directionnelle 2 niveaux + contexte-prix, rate-limiter Twelve (attend, RPM=55), PROBA_SCALE=15, **plan horizon** (pertinence recalibrée + cap anti-inversion news α=0.8 + drapeau 📰 si news>50%).
- ⚠️ **GitHub `schedule` retardé de 1-3h** (comportement GitHub normal, PAS un bug — 6 runs schedule prouvés les 30-31/05). Parade : redondance ×3 par créneau (cron `:12/:27/:42`) + garde-fou anti-doublon (skip si snapshot <2h). Fallback fiables : push `v3/RUN-CYCLE.txt` ou `workflow_dispatch`. Pinger externe (cron-job.org) en option pour l'heure pile. **Ne plus churner le cron** (re-registration fait sauter l'occurrence suivante).
- ⬜ **À venir** : backtest moteur de tendance → durcir mesure (non-chevauchant, multiple-testing) → ~30 j shadow → **Phase 2 news** (tracer `event_id`/date + flag nature : structurel/ponctuel/déjà-price — cause racine du biais news) → émission post-shadow.

## Garde-fous

- **Zéro invention** (source absente → critère n/a, poids 0). **Pas de modif silencieuse** des poids/prompts (changelog + validation Thomas). **Mode shadow obligatoire** avant toute émission. **Échec visible**.

## Repères repo

- `v3/scripts/` : le système. `v3/config/` : fiches actifs (YAML) + triggers + weighting. `v3/data/` : sorties (bulletins, events-log, decision-log, performance). `v3/audit/` : audits. `v3/docs/reco/` : décisions d'architecture.
- `legacy/` : ancienne app (bot « 1 signal turbo/jour ») — **archivée, ne pas utiliser**.
- `.claude/`, `CLAUDE.md`, `update.sh` : framework Gradient Agents (séparé du projet trading).

## Historique des interventions agents

| Date | Agent | Livrable | Décisions clés |
|---|---|---|---|
| 2026-06-01 | orchestration + @fullstack | Correctifs pipeline run quotidien | Routing IA-first réparé, prix d'émission, symboles Twelve validés. Synthèse directionnelle 2 niveaux + contexte-prix. **Indices via ETF Twelve** (yfinance bloqué CI). **Rate-limiter Twelve** : attend au lieu de rejeter, `TWELVE_RPM=55` (plan Grow). PROBA_SCALE 10→15, propagation reliability, garde chevauchement 7j/1m. |
| 2026-06-01 | 3 experts (Analyst / News Trader / Spéculateur) | `v3/audit/chaine-*.md` + `coherence-3-experts.md` | Audit des runs dans l'ordre d'édition. Cohérence : 2 faux positifs écartés sur preuve (signe géopol déjà câblé `ia_synthese` ; contamination 2025 filtrée par cutoff lookback). **Trio = panel d'audit officiel** (`v3/audit/README.md`). |
| 2026-06-01 | @fullstack + 3 experts (validé Thomas) | **Plan horizon** (`revue-plan-horizon-*.md`) | Constat : DeepSeek = 1 direction/actif **horizon-agnostique** ; l'horizon est géré par `pertinence` par critère. **PAS de decay_factor global** (rejeté 3/3 : doublon + casserait l'OPEC structurel). Retenu : recalibrer pertinence (or/petrole/vix, OPEC 7j-1m préservé) + cap anti-inversion α=0.8 (override si high+confirmed) + `ratio_news`/drapeau 📰. Preuve : Or 24h & VIX 1m → SHORT, Pétrole/S&P inchangés. |
| 2026-06-01 | infrastructure (orch) | Workflow `cycle-decision` | Diagnostic : `schedule` GitHub retardé 1-3h (pas une panne). Redondance ×3 + garde-fou anti-doublon. Read/write permissions activées. |
