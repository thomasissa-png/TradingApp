# Synthèse de cohérence : audit complet fond + forme vs objectifs de gains 24h/7j/1m

> Date : 2026-07-01 (S11). Panel : Analyst (fond mesure, 4/10) · News Trader (fond signal, 6,5/10) · Spéculateur (forme, 6,5 / 3,5 / 5 sur 10). Synthèse : orchestration, contradictions vérifiées sur pièces.
> Objectif de référence : directions justes sur 24h/7j/1m, WR tradable ≥ 70 % avec N ≥ 15 par cellule au jalon 08/08 (v3/SELECTION-RULE.md). WIN RATE ONLY.

## Verdict consolidé par horizon

| Horizon | N atteignable au 08/08 | WR mesuré (23-30/06, measures-log) | Verdict |
|---|---|---|---|
| 24h | 26-28 si ZÉRO nouveau reset (base : reset 30/06) | conclusif 72 % (43/60 avec 7j) · tradable ~43 % | Seul horizon en course, mais la règle gravée (tradable ≥ 70 %) est inatteignable tant que ~37 % des mesures sont non-conclusives |
| 7j | max ~5 obs indépendantes (non-chevauchant) | 11 VRAI / 2 FAUSSE / 11 NC (N faible) | Impossible au 08/08. Jalon honnête : ~13/10/2026 |
| 1m | 1 (première mesure comptée ~30/07) | zéro mesure (structurel : échéance +30 j) | Impossible au 08/08. Validation non-chevauchante : pas avant l'automne 2027 |

Note : la règle gravée SELECTION-RULE est déjà 24h-only ; l'objectif « gains sur 3 horizons » n'a aujourd'hui AUCUNE règle de validation pour 7j et 1m. Décision fondateur requise (acter les jalons par horizon).

## Contradictions inter-audits, tranchées sur pièces

1. « WR 72 % » (News Trader) vs « WR 43 % » (Analyst) : PAS une contradiction, deux métriques. 72 % = conclusif (VRAI/(VRAI+FAUSSE)) ; 43 % = tradable (NC au dénominateur), et c'est le tradable que la règle gravée juge. Le plafond de non-conclusives (37 %) est LE problème de fond du 24h.
2. « N=1 affiché » : pas un bug d'affichage. 6e reset au 30/06 (commit bac8ccb, re-découpage horizons + tendance 2-3j, addendum en règle) : 87/102 mesures écartées par discipline anti-mélange. Légitime, mais session du 30/06 absente de l'historique project-context (à consigner) et chaque reset repousse le jalon.
3. « US illisible à midi » (Spéculateur) : cause racine vérifiée, `v3/data/futures-us/` N'EXISTE PAS. Le fetch OANDA (décision 23/06) n'a jamais écrit : secret `OANDA_API_TOKEN` jamais posé (blocker fondateur toujours ouvert). Le repli best-effort masque le manque en silence.

## P0 consolidés (ordre de priorité)

1. [Décision Thomas] Acter les jalons par horizon : 08/08 = 24h-only (déjà le cas en règle), 7j ~13/10, 1m à définir (mesure chevauchante ou horizon reporté). Sans ça, « objectif 3 horizons au 08/08 » restera structurellement raté.
2. [Décision Thomas + @fullstack] Traiter le plafond non-conclusives MAINTENANT puis geler : resserrer les seuils VRAI/FAUX par actif (précédent du 02/06 : avant accumulation, pour éviter le biais rétrospectif), PUIS moratoire écrit sur tout reset/changement de mesure jusqu'au 08/08. Un 7e reset après ~17/07 tue le jalon même en 24h.
3. [Signal, @fullstack + Analyst] Nasdaq : 5 FAUSSE news-driven SHORT consécutives (ratio_news 1,6 à 10,4) : la couche news a renversé la tendance une semaine, violation de la doctrine quant-patron. Reco News Trader : replay contrefactuel (news plafonnées à 1× le quant) AVANT toute retouche, verdict présenté à Thomas. Hors Nasdaq la couche news AIDE (20/22 = 91 %) : ne pas sur-corriger.
4. [Action Thomas] Poser le secret OANDA, puis brancher le prix future sur les lignes 12h/18h (reco Spéculateur P0-3) : sans ça la revente de midi sur les indices US reste aveugle.
5. [@fullstack] Sucre et USD/JPY : 4/4 mesures en suivi-interrompu (cellules mortes-nées depuis le cutover 26/06) : investiguer la source du prix d'échéance.

## Cutovers news (décision attendue depuis le 18/06) : verdict panel

- Persistance news : NO-GO, données insuffisantes (`persist_shadow_blocks_flip` 0/309, âge max 9,2 j < 30 j : l'événement discriminant n'a pas encore eu lieu). Laisser accumuler.
- Rumeur→verbal : NO-GO en l'état (98 % des déclenchements = simple reliability:reported ; aucun contrefactuel loggé). Reco : logger score/conclusion contrefactuels puis replay.
- Garde-fou démenti textuel : NO-GO DÉFINITIF (0 déclenchement textuel vs 158 démentis quantitatifs : le quant EST le démenti, L028 confirmée). Chantier clos.

## Forme (Spéculateur) : P0/P1 retenus, tous rendu pur

- P0 : « Pourquoi » de la Sélection contradictoire avec le pari (source unique = driver « Porté par ») · aucun suivi des positions 7j/1m ouvertes (bloc « Positions ouvertes » avec prix d'entrée, jour n/N, échéance) · US à midi (cf. P0-4 ci-dessus).
- P1 : pas de niveau de sortie affiché à 7h ; « Suggestions de sortie : aucune » vs 4 « 🔴 Coupe » sur le même écran ; « Cellules à surveiller » = 36/45 (bruit) ; 61 tirets cadratins résiduels dans le bulletin affiché ; heure d'émission instable (08h04 le 30/06).
- Points forts : mode test/08/08 clair et honnête, tableau Sélection lisible en 30 s.

## Références

- `v3/audit/audit-fond-analyst-2026-07-01.md` · `v3/audit/audit-fond-newstrader-2026-07-01.md` · `v3/audit/audit-forme-speculateur-2026-07-01.md`
