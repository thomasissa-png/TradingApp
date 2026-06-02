# Perf-trends — TradingApp

> Suivi de la santé du framework (commandement n°8). Idéalement alimenté par `scripts/perf-trend.sh`.
> ⚠️ **`scripts/perf-trend.sh` est ABSENT de ce projet** (gap framework — à créer/importer depuis Agent-Team). En attendant : mesure MANUELLE en fin de session.

| Session | Date | M1 context (core) | M4 learnings actifs | CLAUDE.md | lessons-learned | M7 sur-invocation | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | 2026-06-02 | 54 / cap≈250 | 17 (L001-L017) | 110/125 | 39/80 | @fullstack ×~8 (lots distincts) | **WARNING isolé** (M7) |

**Détail Session 1** :
- Caps : tous respectés (CLAUDE 110<125, lessons 39<80, context core 54<250). Net-zero prompts : 0 fichier de prompt (CLAUDE/agents/gates/index.html) modifié.
- **M7 WARNING (isolé, non bloquant)** : @fullstack invoqué ~8× — mais pour des **livrables DISTINCTS** (S5 + 6 lots de gates + source_monitor + backtest), pas des retries sur un même échec. Cause = **grosse session** (beaucoup empilé en une fois, piloté par Thomas). Plan correctif : si récurrent, découper en sessions plus courtes (1-2 lots/session). Pas une dérive de scope d'agent.
- **Gap framework noté** : `scripts/perf-trend.sh` absent + `docs/founder-preferences.md` était absent (créé cette session). À importer depuis le repo framework de référence.
- Verdict global : **PASS** sur les caps/net-zero ; **WARNING isolé** sur M7 (1ère occurrence, surveiller session 2).
