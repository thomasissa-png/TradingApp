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
| L003 | 2026-05-01 | 0 | @infrastructure | P1 | Replit Hacker plan (~7 €/mois) discontinué en 2026 — remplacé par Replit Core 20 $/mois minimum. Hypothèse H1 du project-context invalidée → NEEDS-DECISION (Replit Core OU Hetzner CX11 4,5 €/mois). | Tout livrable mentionnant un budget infra / Replit Hacker | project-context.md (hypothèse H1 à mettre à jour après décision persona), docs/orchestration-plan.md | ✅ documenté (alternatives chiffrées section 1 infra-audit.md) | ⏳ partiel (project-context.md H1 reste tel quel jusqu'à décision persona checkpoint) | Décision persona requise au checkpoint Phase 0 — impact coût total mensuel 90→145 €/mois ou ~50-90 €/mois selon arbitrage. |
| L004 | 2026-05-01 | 0 | @infrastructure | P1 | Twelve Data plan « payant » est un terme ambigu : 1m intraday EU stocks réservé au plan Pro Individual 79 $/mois minimum. Hypothèse H2 NEEDS-DECISION → action persona obligatoire avant R&D. | Toute Phase utilisant Twelve Data en intraday 1m | project-context.md (hypothèse H2), docs/analytics/edge-rnd-brief.md (prérequis Phase 1) | ✅ documenté | ⏳ partiel (action persona pending — vérifier twelvedata.com/account) | Si plan persona ne couvre pas, choix entre upgrade Pro Individual 79 $/mois OU repli Twelve Data Grow 5m -50 $/mois (perte granularité ORB 5 min). |

## Agents fragiles (circuit breaker)

| Agent | Type d'échec | Fréquence | Dernière occurrence | Contournement |
|-------|--------------|-----------|---------------------|---------------|

## Notes

- Projet TradingApp démarré le 2026-05-01.
- Aucun learning hérité au démarrage. Tableau vide attendu jusqu'à fin de Phase 0.
- Les learnings cross-projets de référence (zéro fausse promesse copy, anti-témoignage fictif, conviction-first, anti-placeholder galerie, backoffice = même DS, self-fetch Next.js 127.0.0.1:PORT, hooks AVANT return conditionnel, stale-while-revalidate fetch >3s, seuil réécriture 10 edits, migrations SQL idempotentes, flux progressifs IA, protocole migration modèle IA, parcours d'achat e2e, bugs corrigés immédiats, agents testeurs calibrés VALEUR, @sales-enablement obligatoire en Phase 4, earned media Phase 4 @growth, pre-commit build check, Actions Replit, favicons/icônes) sont assumés intégrés dans CLAUDE.md / `_base-agent-protocol.md` / les agents — pas re-listés ici pour respecter le cap 80L.
