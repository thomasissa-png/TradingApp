<!-- Version: 2026-05-01T00:00 — @orchestrator — Création squelette v2 (projet neuf TradingApp) -->
# Lessons learned — TradingApp

> Format v2 obligatoire (11 colonnes). Cap dur : 80 lignes max (commandement n°8 CLAUDE.md).
> TTL : 5 sessions OU 90 jours (le plus court). Au-delà : promote en règle ou archive vers `lessons-archive.md`.
> P0 jamais archivés automatiquement (garde-fous silencieux).
> GATE BLOQUANTE en reprise : tout learning P0/P1 avec propagation = `non-propagé` doit être propagé AVANT tout nouveau travail.

| ID | Date | Phase | Agent | Sévérité | Description | Cible propagation | Fichiers impactés | Statut correction | Statut propagation | Notes |
|----|------|-------|-------|----------|-------------|-------------------|-------------------|-------------------|---------------------|-------|
| L001 | 2026-05-01 | 0 | @legal | P0 | PFU = 31,4 % depuis 01/01/2025 (12,8 % IR + 18,6 % PS), pas 30 %. Hausse effective des prélèvements sociaux. | Tout livrable mentionnant la fiscalité turbos / PFU / scénarios P&L net | project-context.md L45, docs/strategy/personas.md L191, docs/orchestration-plan.md L235 + L317 | ✅ corrigé | ✅ propagé (4 fichiers, vérifié grep "PFU 30") | Réf. Service-public.fr fiche F21618. À garder en référence pour @data-analyst kpi-framework + @product-manager specs (rapport mensuel net). |

## Agents fragiles (circuit breaker)

| Agent | Type d'échec | Fréquence | Dernière occurrence | Contournement |
|-------|--------------|-----------|---------------------|---------------|

## Notes

- Projet TradingApp démarré le 2026-05-01.
- Aucun learning hérité au démarrage. Tableau vide attendu jusqu'à fin de Phase 0.
- Les learnings cross-projets de référence (zéro fausse promesse copy, anti-témoignage fictif, conviction-first, anti-placeholder galerie, backoffice = même DS, self-fetch Next.js 127.0.0.1:PORT, hooks AVANT return conditionnel, stale-while-revalidate fetch >3s, seuil réécriture 10 edits, migrations SQL idempotentes, flux progressifs IA, protocole migration modèle IA, parcours d'achat e2e, bugs corrigés immédiats, agents testeurs calibrés VALEUR, @sales-enablement obligatoire en Phase 4, earned media Phase 4 @growth, pre-commit build check, Actions Replit, favicons/icônes) sont assumés intégrés dans CLAUDE.md / `_base-agent-protocol.md` / les agents — pas re-listés ici pour respecter le cap 80L.
