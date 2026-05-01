<!-- Version: 2026-05-01T00:00 — @orchestrator — Création squelette v2 (projet neuf TradingApp) -->
# Lessons learned — TradingApp

> Format v2 obligatoire (11 colonnes). Cap dur : 80 lignes max (commandement n°8 CLAUDE.md).
> TTL : 5 sessions OU 90 jours (le plus court). Au-delà : promote en règle ou archive vers `lessons-archive.md`.
> P0 jamais archivés automatiquement (garde-fous silencieux).
> GATE BLOQUANTE en reprise : tout learning P0/P1 avec propagation = `non-propagé` doit être propagé AVANT tout nouveau travail.

| ID | Date | Phase | Agent | Sévérité | Description | Cible propagation | Fichiers impactés | Statut correction | Statut propagation | Notes |
|----|------|-------|-------|----------|-------------|-------------------|-------------------|-------------------|---------------------|-------|
| L001 | 2026-05-01 | 0 | @legal | P0 | PFU = 31,4 % depuis 01/01/2025 (12,8 % IR + 18,6 % PS), pas 30 %. Hausse effective des prélèvements sociaux. | Tout livrable mentionnant la fiscalité turbos / PFU / scénarios P&L net | project-context.md L45, docs/strategy/personas.md L191, docs/orchestration-plan.md L235 + L317 | ✅ corrigé | ✅ propagé (4 fichiers, vérifié grep "PFU 30") | Réf. Service-public.fr fiche F21618. |
| L002 | 2026-05-01 | 0 | @ia | P1 | Tag modèle Anthropic exact obligatoire (`claude-sonnet-4-5-20250929`), pas d'alias `-latest` cross-family. Évite la régression silencieuse en prod sur un signal qui engage du capital réel. | Tout code/livrable invoquant l'API Anthropic | docs/ia/ai-architecture.md §1.2, docs/ia/prompt-library.md §6 | ✅ corrigé (tag exact retenu) | ✅ propagé (2 fichiers @ia) | À renforcer en Phase 2 par @fullstack : variable env `ANTHROPIC_MODEL_LIVE` + assertion runtime que la valeur n'est pas `latest`. Couplé au champ `prompt_version` SQLite + au champ `model_used` JSON output. |
| L003 | 2026-05-01 | 0 | @infrastructure | P1 | Replit Hacker plan (~7 €/mois) discontinué en 2026 — remplacé par Replit Core 20 $/mois minimum. | Tout livrable mentionnant un budget infra / Replit Hacker | project-context.md, docs/orchestration-plan.md | ✅ corrigé | ✅ propagé (Replit Core retenu par persona 2026-05-01, project-context.md L56 + table hypothèses mis à jour) | Coût infra net : ~20 $/mois en croisière. Cron Deployment validé (pas Always-On). |
| L004 | 2026-05-01 | 0 | @infrastructure | P1 | Twelve Data 1m intraday EU stocks = plan Pro Individual 79 $/mois minimum (et non plan « payant » générique). | Toute Phase utilisant Twelve Data en intraday 1m | project-context.md, docs/analytics/edge-rnd-brief.md | ✅ corrigé | ✅ propagé (persona confirme plan Pro 2026-05-01, table hypothèses H2 → PASS) | Phase 1 R&D peut démarrer. Cache SQLite obligatoire pour limiter le rate. |
| L005 | 2026-05-01 | 0 | @data-analyst → persona | P2 | Heure cutoff turbo Bourse Direct = 18h00 CET (et non 17h30 CET initialement présumé). | Signal d'arrêt n°5 "position overnight" partout | docs/analytics/kpi-framework.md L306 + L335 | ✅ corrigé | ✅ propagé (persona 2026-05-01) | Trigger SQLite à régler sur 18h00 CET en Phase 2. |
| L006 | 2026-05-01 | 1 | @data-analyst (escalade @ia) | P2 | Schéma SQLite table `signals` enrichi de 4 colonnes traçabilité scoring : `scoring_model_version`, `prompt_version`, `model_used`, `sanity_check_failed`. Escalade Phase 1 @ia → @data-analyst. | @fullstack pour implémentation SQLite Phase 2 | docs/analytics/kpi-framework.md §4 (DDL signals) | ✅ corrigé | ✅ propagé | Colonnes NOT NULL pour les 3 versions (défaut obligatoire à l'INSERT), NULL autorisé pour `sanity_check_failed` (NULL = tous SC PASS). Cohérent edge-scoring-model.md §7 + L002. |

## Agents fragiles (circuit breaker)

| Agent | Type d'échec | Fréquence | Dernière occurrence | Contournement |
|-------|--------------|-----------|---------------------|---------------|

## Notes

- Projet TradingApp démarré le 2026-05-01.
- Aucun learning hérité au démarrage. Tableau vide attendu jusqu'à fin de Phase 0.
- Les learnings cross-projets de référence (zéro fausse promesse copy, anti-témoignage fictif, conviction-first, anti-placeholder galerie, backoffice = même DS, self-fetch Next.js 127.0.0.1:PORT, hooks AVANT return conditionnel, stale-while-revalidate fetch >3s, seuil réécriture 10 edits, migrations SQL idempotentes, flux progressifs IA, protocole migration modèle IA, parcours d'achat e2e, bugs corrigés immédiats, agents testeurs calibrés VALEUR, @sales-enablement obligatoire en Phase 4, earned media Phase 4 @growth, pre-commit build check, Actions Replit, favicons/icônes) sont assumés intégrés dans CLAUDE.md / `_base-agent-protocol.md` / les agents — pas re-listés ici pour respecter le cap 80L.
