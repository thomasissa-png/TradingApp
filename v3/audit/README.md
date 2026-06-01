# Trio d'audit experts — TradingApp v3

> **Mémoire projet.** Ce trio est notre panel de relecture officiel des cycles décisionnels.
> À réutiliser à chaque audit de run. Audit **fichier par fichier, dans l'ordre d'édition du pipeline**.

## Les 3 experts

| # | Expert | Posture | Ce qu'il juge |
|---|--------|---------|---------------|
| 1 | **Analyst** (`@data-analyst`) | Rigueur statistique / décision data-driven | Validité de la mesure : taille d'échantillon, indépendance (chevauchement des fenêtres 7j/1m), Wilson, Brier, multiple-testing, intégrité des normalisations [-1,1]. |
| 2 | **News Trader** senior | 15 ans desk macro/commodities | Justesse **directionnelle** de tendance, défendabilité desk de chaque cellule (pas la perf). Cohérence triplet news → critère → score. |
| 3 | **Spéculateur** trend-follower | « Est-ce que je mets du cash dessus ? » (vagues 24h/7j/1m) | Conviction réelle par cellule : signal large vs mono-critère trompeur, coin-flips déguisés, bruit sur-coté, edge exploitable. |

## Ordre d'édition du pipeline (= ordre d'audit)

1. `v3/data/events-log.md` — INGEST (news + triplets directionnels)
2. `v3/data/criteres-courants.md` — CRITÈRES (normalisation, scoring)
3. `v3/data/bulletins/bulletin-AAAA-MM-JJ.md` — BULLETIN (matrice 12×3 + briefing)
4. `v3/data/decision-log/*.jsonl` — DECISION-LOG (traçabilité)
5. `v3/data/performance.md` + `performance-ab.md` — MESURE (KPIs shadow, A/B)

## Convention de nommage des rendus

`v3/audit/<étape>-<expert>.md` — ex. `chaine-speculateur.md`, `bulletin-newstrader.md`, `sources-analyst.md`.
- `chaine-*` = audit bout-en-bout dans l'ordre d'édition (le format complet attendu)
- `bulletin-*`, `sources-*`, `deepseek-*` = audits ciblés d'une étape.
