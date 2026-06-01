# Contexte Projet — TradingApp v3

> Lu par tous les agents avant toute action.
> **Repo privé** (données financières personnelles). Dernière mise à jour : 2026-05-30.
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

## État (30/05/2026)

- ✅ Système v3 implémenté et testé (**217 tests**, dont intégration sur le vrai chemin).
- ✅ Audits croisés (`v3/audit/`) + corrections préopératoires (idempotence, kill criterion, pyproject réparé, repo nettoyé).
- ⬜ **À venir, dans l'ordre** : backtest du moteur de tendance (historique) → durcir la mesure (non-chevauchant, multiple-testing, calibration Brier) → mode shadow ~30 j → Manager + source_monitor → émission Argos (post-shadow).

## Garde-fous

- **Zéro invention** (source absente → critère n/a, poids 0). **Pas de modif silencieuse** des poids/prompts (changelog + validation Thomas). **Mode shadow obligatoire** avant toute émission. **Échec visible**.

## Repères repo

- `v3/scripts/` : le système. `v3/config/` : fiches actifs (YAML) + triggers + weighting. `v3/data/` : sorties (bulletins, events-log, decision-log, performance). `v3/audit/` : audits. `v3/docs/reco/` : décisions d'architecture.
- `legacy/` : ancienne app (bot « 1 signal turbo/jour ») — **archivée, ne pas utiliser**.
- `.claude/`, `CLAUDE.md`, `update.sh` : framework Gradient Agents (séparé du projet trading).

## Historique des interventions agents

| Date | Agent | Livrable | Décisions clés |
|---|---|---|---|
| 2026-06-01 | @data-analyst | `v3/audit/revue-plan-horizon-analyst.md` | Reject decay_factor global (doublon pertinence). Verdict : (a)+(c) — recalibrer 4 pertinences (or.yml, petrole.yml, vix.yml) + cap anti-inversion α=0.8. Ajouter ratio_news dans decision-log. |
