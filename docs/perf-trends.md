# Perf-trends — TradingApp

> Suivi de la santé du framework (commandement n°8). Idéalement alimenté par `scripts/perf-trend.sh`.
> ⚠️ **`scripts/perf-trend.sh` est ABSENT de ce projet** (gap framework — à créer/importer depuis Agent-Team). En attendant : mesure MANUELLE en fin de session.

| Session | Date | M1 context (core) | M4 learnings actifs | CLAUDE.md | lessons-learned | M7 sur-invocation | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | 2026-06-02 | 54 / cap≈250 | 17 (L001-L017) | 110/125 | 39/80 | @fullstack ×~8 (lots distincts) | **WARNING isolé** (M7) |
| 2 | 2026-06-09 (proj. S4) | 125 / cap 250 | 22 (L001-L022) | 110/125 | 44/80 | agents ×~25 (autopilote refonte, livrables distincts) | **WARNING M7** (2e conséc., non bloquant) |
| 8 | 2026-06-19 | 144 / cap 250 | 31 (L001-L031) | 110/125 | 49/80 | agents ×~15 (autopilote multi-mandats, livrables distincts) | **WARNING M7** (justifié) |

**Détail Session 1** :
- Caps : tous respectés (CLAUDE 110<125, lessons 39<80, context core 54<250). Net-zero prompts : 0 fichier de prompt (CLAUDE/agents/gates/index.html) modifié.
- **M7 WARNING (isolé, non bloquant)** : @fullstack invoqué ~8× — mais pour des **livrables DISTINCTS** (S5 + 6 lots de gates + source_monitor + backtest), pas des retries sur un même échec. Cause = **grosse session** (beaucoup empilé en une fois, piloté par Thomas). Plan correctif : si récurrent, découper en sessions plus courtes (1-2 lots/session). Pas une dérive de scope d'agent.
- **Gap framework noté** : `scripts/perf-trend.sh` absent + `docs/founder-preferences.md` était absent (créé cette session). À importer depuis le repo framework de référence.
- Verdict global : **PASS** sur les caps/net-zero ; **WARNING isolé** sur M7 (1ère occurrence, surveiller session 2).

**Détail Session 2 (projet S4, 2026-06-09)** :
- Caps : tous OK (CLAUDE 110<125, lessons 44<80, context 125<250, founder-prefs 26). Net-zero prompts : 0 fichier de prompt (CLAUDE/agents/gates/index.html) modifié → ✅.
- **M7 WARNING (2e consécutif, NON bloquant)** : ~25 invocations d'agents sur la session — MAIS **mandat explicite « prépare en autopilote, itère jusqu'à 10/10 »** de Thomas + **livrables tous DISTINCTS** (refonte 5 rapports : spec, 3 audits trio, 3 phases build, infra, revue finale, 2× page, mining_com, micro-bugs). Pas de retry sur un même échec, pas de dérive de scope. C'est une **mega-session pilotée**.
- ⚠️ **Seuil CRITICAL à 3 WARNING consécutifs** : la prochaine session (S5) doit revenir à un volume normal (sessions plus courtes) pour éviter le 3e WARNING → audit profond forcé. Plan : S5 = observation live + petits chantiers (pas de nouveau mega-chantier).
- **Gap framework persistant** : `scripts/perf-trend.sh` toujours absent (mesure manuelle). À importer depuis Agent-Team.
- Verdict global : **PASS** caps/net-zero ; **WARNING M7** (volume, justifié par le mandat autopilote — surveiller que S5 ne soit pas un 3e WARNING).

**Détail Session 7 (2026-06-16)** :
- Caps : tous OK (CLAUDE 110<125, lessons 45<80, context 142<250, founder-prefs 30). Net-zero prompts : 0 fichier de prompt (CLAUDE/agents/gates) modifié → ✅. Archivé 5 P2 (>5 sessions) → lessons-learned-archive.md.
- **M7 WARNING (volume agents élevé, ~18 invocations sur 5 jours live 11→16/06)** — JUSTIFIÉ : mandats explicites répétés de Thomas (« implémente tout / GO / en autopilote »), livrables tous DISTINCTS (momentum live, UX ×2 audits+fixes, DeepSeek v2.4, sources/calendrier, continu, Twelve-natif, gate, sélection), zéro retry-sur-même-échec, zéro dérive de scope. Multi-jour compté comme 1 session.
- **Script `scripts/perf-trend.sh` toujours ABSENT** (gap framework persistant depuis S2) — mesure manuelle. À importer depuis Agent-Team (reco P1).
- Note : clôture demandée « ne lance aucun agent » → pas d'audit profond délégué malgré le volume ; recommandation = **S8 = session LÉGÈRE** (fix mesure ciblé + nettoyage), pas de nouveau méga-chantier.
- Verdict global : **PASS caps/net-zero ; WARNING M7 volume (justifié mandat, à surveiller).**

**Détail Session 8 (2026-06-16→19)** :
- Caps : tous OK (CLAUDE 110<125, lessons 49<80, context 144<250, founder-prefs 32). Net-zero prompts : **0 fichier de prompt (CLAUDE/agents/gates) modifié** → ✅. Mémo S7 archivé → `docs/project-context-archive.md` (créé).
- **M7 WARNING (~15 invocations d'agents sur 4 jours)** — JUSTIFIÉ : mandats EXPLICITES répétés de Thomas (« termine tout en autopilote », « corrige tout », « force et corrige », « audite jusqu'à 10/10 », « applique la reco des experts »). Livrables tous DISTINCTS (L027, refonte briefing, raison 10/10, 3 instrumentations shadow, 5 météo, garde-fou férié, parser news, bandeau), **zéro retry-sur-même-échec, zéro dérive de scope**. Multi-jour = 1 session.
- ⚠️ **Tendance M7 récurrente (S1/S2/S7/S8)** : le seuil M7>3 flagge le **STYLE de travail de Thomas** (mega-sessions autopilote à livrables distincts), pas une dérive. **Audit profond NON déclenché** : Thomas a explicitement demandé « **ne lance aucun agent** » pour cette clôture → consigne prioritaire. **Reco framework (P1)** : affiner M7 pour distinguer « retries / dérive de scope » (mauvais) de « volume mandaté à livrables distincts » (sain) — sinon le WARNING est structurel et perd sa valeur d'alarme.
- **Script `scripts/perf-trend.sh` toujours ABSENT** (gap framework depuis S2, 4e session) — mesure manuelle. Reco : créer/importer.
- Verdict global : **PASS caps/net-zero ; WARNING M7 (volume mandaté, audit non lançable par consigne — affiner le métrique).**
