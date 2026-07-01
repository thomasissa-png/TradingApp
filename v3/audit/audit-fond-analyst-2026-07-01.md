# Audit de fond : chaîne prédiction / mesure vs objectif du 08/08/2026 (Analyst, panel officiel)

Date : 2026-07-01. Auditeur : l'Analyst (trio Analyst / News Trader / Spéculateur).
Objet : la chaîne prédiction, mesure, affichage tient-elle la promesse "directions justes sur 3 horizons (24h / 7j / 1m), win rate >= 70 % avec N >= 15 par cellule au 08/08/2026" ? WIN RATE ONLY : aucune considération de P&L.
Méthode : zéro invention, chaque affirmation est sourcée sur un fichier ou un chiffre réel du repo.

## Note globale : 4/10

- La mécanique de mesure fonctionne et est cohérente avec elle-même (log, page, registre de reset alignés). C'est le seul point fort.
- Mais l'objectif tel que formulé (3 horizons, N >= 15 chacun, au 08/08) est mathématiquement impossible pour 7j et 1m, et la propre règle gravée du projet le dit déjà (SELECTION-RULE.md lignes 94-99 : il faudrait 15 semaines pour le 7j, 15 mois pour le 1m). Le jalon à 3 horizons n'a jamais été réaliste.
- Le 24h, seul horizon jouable, vient de subir son 6e reset en 20 jours (ref-changed.json : les 15 cellules à ref_changed = 2026-06-30) : tout le capital statistique accumulé est reparti à zéro à 28 jours ouvrés du jalon.
- Le win rate réellement mesuré (log complet) est loin du seuil : WR tradable 24h = 43,2 %, borne basse Wilson 32,6 %.

---

## Q1. Déconnexion mesure / affichage : pourquoi N=1 par cellule et 7j vide alors que le log contient 78 mesures 24h et 24 mesures 7j ?

Cause racine trouvée dans le code : le filtre de cutover `ref_changed`, combiné au reset GLOBAL du 30/06.

1. `v3/data/ref-changed.json` : les 15 entrées (CC=F, BZ=F, ^IXIC, SI=F, KC=F, ZW=F, HG=F, GC=F, EUR=X, ^GSPC, ^FCHI, ^VIX, COTN, CANE, USD/JPY) portent toutes `"ref_changed": "2026-06-30"` (motif : re-découpage des horizons par familles de vitesse, addendum SELECTION-RULE du 30/06).
2. `v3/scripts/journaliste.py` ligne 2348, `_apply_ref_changed_cutover` (commentaire lignes 2333-2342) : pour les KPIs de la page, seules les observations dont `bulletin_date >= ref_changed` sont comptées. Les cellules absentes du registre garderaient tout, mais AUCUNE cellule n'est absente du registre.
3. Conséquence chiffrée : sur les 102 mesures du log, seules les 15 mesures du bulletin du 30/06 (mesurées le 01/07) survivent au filtre. Le champ `system_version` du log le confirme : 87 lignes "v1" (écartées), 15 lignes "v2" (comptées).
4. La colonne N de la page = `n_effective` = VRAI + FAUSSE non-chevauchants (journaliste.py lignes 1586-1588), NC exclus. Le 30/06 a donné 3 VRAI (Cacao, Café, S&P 500) et 2 FAUSSE (Blé, Nasdaq), 8 non-conclusives, 2 suivi-interrompu (log, entrées bulletin_date 2026-06-30). D'où exactement les 5 cellules à N=1 vues par Thomas, le reste à 0, et "0/45 cellules fiables" (15 actifs x 3 horizons, aucun N >= 15).
5. 7j vide : les 24 mesures 7j du log portent bulletin_date 23/06 et 24/06 (12+12), toutes antérieures au 30/06 donc filtrées. La première mesure 7j post-reset tombera le 07/07 (bulletin 30/06 + 7 jours, HORIZON_DAYS journaliste.py ligne 88).
6. Les pistes alternatives sont écartées sur pièces : le filtre "bulletin 7h only" n'a rien exclu (le bulletin du 30/06 émis à 08h04 a bien ses 15 mesures dans le log) ; `select_non_overlapping` ne réduit pas un historique de 6 jours 24h à 1 (pas de chevauchement en 24h, SELECTION-RULE.md lignes 87-92) ; le cutover 12 vers 15 actifs du 26/06 n'a rien resetté (addendum 26/06 : "zéro reset des actifs en place").

Verdict Q1 : ce n'est pas un bug d'affichage. La page applique fidèlement le registre de reset. Le vrai problème est en amont : le reset du 30/06 a volontairement jeté 87 mesures sur 102 à 39 jours calendaires du jalon.

## Q2. Pourquoi le measures-log ne commence-t-il qu'au 23/06 alors que le shadow tourne depuis fin mai ?

L'historique antérieur au 22/06 n'existe plus dans le repo. Preuves :

- Le repo git actuel ne contient que 50 commits et son commit racine est `d7ff14d` daté du 27/06/2026 (git log : le commit ajoute d'un bloc toute l'arborescence, dont `.claude/agents/`). Tout ce qui précède le 27/06 n'a pas d'historique git ici.
- `measures-log.jsonl` est "re-dérivé déterministe à chaque run depuis les bulletins" (CHANGELOG.md ligne 437). Or les bulletins les plus anciens présents sont `v3/data/bulletins/archive/bulletin-2026-06-22-*.md` : la re-dérivation ne peut donc pas remonter avant le 22/06, et la première journée complète mesurable est le 23/06.
- Même schéma sur toutes les données : `decision-log/archive/`, `prix-emission/archive/`, `suivi-tracking/archive/` commencent tous au 2026-06-22.
- À sa première apparition dans git (commit d7ff14d, 27/06), le log contenait déjà 48 lignes couvrant 23/06 à 26/06 : c'est un backfill depuis les bulletins présents, pas un log vivant depuis fin mai.

Verdict Q2 : historique pré-22/06 perdu pour ce repo (ou resté sur une machine hors repo, invérifiable ici). Impact décisionnel toutefois nul : le reset du 30/06 aurait de toute façon écarté ces observations. Impact réel : impossibilité d'auditer les cutovers 11/06, 15/06, 17/06 sur données brutes, on ne peut que croire les addendums.

## Q3. Horizon 1m : 0 mesure. Structurel ou bug ?

Structurel, pas un bug.

- L'échéance 1m = bulletin + 30 jours calendaires (`HORIZON_DAYS = {"24h": 1, "7j": 7, "1m": 30}`, journaliste.py ligne 88).
- Le plus ancien bulletin mesurable date du 23/06 (Q2) : la toute première échéance 1m possible est le 23/07/2026. Nous sommes le 01/07 : aucune échéance 1m n'est encore atteinte, donc zéro entrée 1m dans le log est le comportement attendu.
- Première mesure 1m dans le log : 23/07/2026 (bulletin 23/06), mais elle sera "v1" donc invisible sur la page. Première mesure 1m COMPTÉE par la page : 30/07/2026 (bulletin 30/06, premier bulletin post-reset).
- Au jalon du 08/08 : mesures 1m comptées = bulletins du 30/06 au 09/07, soit environ 8 mesures chevauchantes par cellule, et exactement 1 observation non-chevauchante (fenêtre de 30 jours, `NON_OVERLAP_STEP` journaliste.py ligne 101).

## Q4. Faisabilité du jalon 08/08 par horizon (rythme réel observé, paris non-chevauchants)

Rappel : le 08/08/2026 est un samedi ; le snapshot se fait à 00h00 (SELECTION-RULE.md ligne 127). Sont comptées les mesures dont l'échéance est atteinte avant cette date. Tous les compteurs partent du 30/06 (reset global, Q1).

| Horizon | Rythme réel | N max atteignable au 08/08 (par cellule) | N >= 15 ? |
|---|---|---|---|
| 24h | 1 pari/jour ouvré, mesuré à J+1 (66 mesures à delta 1 jour + 12 à delta 3 jours, vendredi vers lundi, dans le log) | bulletins du 30/06 au 06/08 = 28 jours ouvrés, moins le férié US du 03/07 et les incidents : environ 26-28 en N tradable | OUI, avec marge d'environ 11-13 paris, SI zéro nouveau reset |
| 7j | 1 obs non-chevauchante par fenêtre de 7 jours (KILL-CRITERION.md lignes 47-49) | fenêtres 30/06, 07/07, 14/07, 21/07, 28/07 (échéance <= 08/08) = 5 | NON. N=15 non-chevauchants exigerait des bulletins jusqu'au 06/10, dernière échéance vers le 13/10/2026 |
| 1m | 1 obs non-chevauchante par fenêtre de 30 jours | 1 (bulletin 30/06, échéance 30/07 ; la fenêtre suivante échoit le 29/08) | NON. N=15 non-chevauchants = environ 15 mois : automne 2027 |

Point d'honnêteté : même sans aucun reset, en comptant depuis le début du log (23/06), le 7j n'aurait que 6 fenêtres et le 1m 2 au 08/08. Les resets n'y changent rien : 7j et 1m à N >= 15 au 08/08 sont impossibles PAR CONSTRUCTION, et la règle gravée le reconnaît noir sur blanc (SELECTION-RULE.md lignes 94-99 et 144-145 : la sélection est "24h-only"). L'objectif "3 horizons au 08/08" contredit la propre règle signée par Thomas le 10/06.

Fragilité supplémentaire du 24h : 6 resets en 20 jours (10/06, 11/06, 15/06, 16/06, 17/06, 30/06, motifs cumulés dans ref-changed.json). Un 7e reset après le 17/07 environ (moins de 15 jours ouvrés restants) rendrait N >= 15 inatteignable aussi en 24h. Et 2 cellules sur 15 (Sucre, USD/JPY) ne produisent QUE des "suivi-interrompu" depuis leur introduction (Q6) : en l'état elles finiront à N=0.

UNE recommandation (pas un menu) : geler le moteur par écrit jusqu'au 08/08 (moratoire signé sur tout changement de signal, de source ou de sémantique de mesure, donc zéro nouveau ref_changed sauf bug de mesure prouvé de type L027), et re-périmétrer le jalon en conséquence : 08/08 = verdict 24h-only conformément à SELECTION-RULE.md ; le 7j reçoit son propre jalon N=15 vers le 13/10/2026 ; le gate 1m est abandonné en tant que critère daté (observabilité pure), car aucune date raisonnable n'existe avant l'automne 2027.

## Q5. Win rate réel actuel (depuis le log, 102 mesures, 23/06 au 30/06)

Définitions : WR conclusif = VRAI / (VRAI + FAUSSE) ; WR tradable = VRAI / (VRAI + FAUSSE + NC) (SELECTION-RULE.md lignes 54 et 66-67). Borne basse = Wilson 95 %.

| Horizon | VRAI | FAUSSE | NC | Suivi-interrompu | WR conclusif (Wilson bas) | WR tradable (Wilson bas) |
|---|---|---|---|---|---|---|
| 24h | 32 | 15 | 27 | 4 | 68,1 % (53,8 %) | 43,2 % (32,6 %) |
| 7j | 11 | 2 | 11 | 0 | 84,6 % (57,8 %) | 45,8 % (27,9 %) |
| 1m | 0 | 0 | 0 | 0 | n/a | n/a |

Lecture honnête :
- Le moteur, quand il conclut, est au-dessus du hasard (24h conclusif 68,1 %) mais PAS démontré >= 70 % : la borne Wilson à 53,8 % ne sépare même pas encore 70 % de 55 %.
- La métrique de décision du jalon, le WR tradable, est à 43,2 % en 24h : à 27 points du seuil. Aucun spin possible.
- Ces chiffres décrivent l'ANCIEN moteur (87 mesures "v1"). Le moteur du 30/06 n'a qu'un jour de données : 3 VRAI / 2 FAUSSE / 8 NC, WR tradable 3/13 = 23,1 % (Wilson bas 8,2 %). Trop tôt pour juger, mais le compteur qui compte pour le 08/08 part de là.
- Dispersion par cellule 24h (log complet, indicatif car pré-reset) : Café 6 VRAI / 0 FAUSSE / 0 NC, Or 5/0/1, S&P 500 5/0/1 d'un côté ; Nasdaq 0/5/1 (100 % faux sur les cas conclus) et EUR/USD 0/3/3 de l'autre. La sélection par cellule a du sens : certaines cellules portent un signal, d'autres détruisent.

Le taux de non-conclusives est-il un problème de seuils ? Oui, partiellement :
- 27 NC / 74 paris tradables en 24h = 36,5 %. Mécaniquement, une cellule avec 36 % de NC plafonne son WR tradable à 63,5 % MÊME avec 100 % de directions justes : le seuil de 70 % devient inatteignable. Par cellule : CAC 40 est à 5 NC / 6 mesures (plafond 17 %), Coton 2/2, Pétrole et EUR/USD 3/6.
- Les seuils sont fixés par fiche (`seuils_reussite_pct`, ex. cacao 24h = 1,0 %, sp500 24h = 0,4 %). 25 des 27 NC 24h ont un |delta| <= 0,87 % : ce sont bien des journées sans mouvement suffisant, pas des bugs. Les 2 NC restants sont le VIX (-2,45 % et -7,37 % absorbés par un seuil VIX élevé, cohérent avec sa volatilité).
- Ce n'est pas une raison de relâcher les seuils maintenant (interdit post-hoc, SELECTION-RULE.md lignes 146-147). C'est une raison d'accepter que les cellules lentes (CAC 40, indices calmes) ne se qualifieront JAMAIS sous cette métrique, et que la qualification se jouera sur 4-6 cellules volatiles au mieux.

## Q6. Intégrité de la mesure

1. Les 4 "suivi-interrompu" : ce sont exclusivement Sucre et USD/JPY, les 29/06 et 30/06, avec `prix_echeance: null` (log). Les 2 actifs introduits le 26/06 n'ont donc JAMAIS produit une mesure valide : 100 % d'échec de fetch du prix d'échéance depuis leur entrée. Cellules mortes-nées si rien n'est réparé (2 cellules sur 15 hors course pour le 08/08).
2. Mix prix_reference_source (94 emission / 8 ouverture) : NON conforme à la décision L027. L'addendum du 16/06 (SELECTION-RULE.md ligne 310) exige : continus = prix d'émission 7h, non-continus (CAC, S&P 500, Nasdaq, VIX) = ouverture de marché. Or dans le log : CAC 40 = 6/6 "ouverture" (conforme), mais S&P 500, Nasdaq et VIX = 6/6 chacun en "emission" (18 mesures non conformes). Cause vérifiée : les fichiers `v3/data/prix-ouverture/*.json` ne contiennent JAMAIS ^GSPC, ^IXIC ni ^VIX (ex. 2026-06-30.json : 12 symboles, dont ^FCHI, zéro indice US) ; le stamp d'ouverture US (15h30) ne se fait pas, et `_resolve_prix_reference` (journaliste.py ligne 1993) retombe sur le prix d'émission. Conséquence : les indices US sont mesurés depuis un prix de 7h, soit le close de la veille (marché fermé), exactement la sémantique "prix de nuit" que l'addendum L027 interdit pour les non-continus. Le WR de S&P 500 (5 VRAI / 0 FAUSSE) et du Nasdaq inclut des mouvements overnight que Thomas ne peut pas exécuter.
3. Bulletin du 30/06 émis à 08h au lieu de 07h (bulletin-2026-06-30-08h.md, decision-log/2026-06-30-0804.jsonl, prix-emission/2026-06-30-08h.json) : PAS de trou de mesure, les 15 mesures du 30/06 sont dans le log et sur la page (les 5 N=1). Impact résiduel : la référence des continus a été prise à 08h04 au lieu de 07h (une heure de mouvement escamotée), précisément le biais que L027 corrigeait, sur le jour 1 du nouveau moteur, celui dont chaque mesure compte pour le jalon. Ponctuel mais au pire moment.
4. Incohérence d'affichage secondaire : la page mélange des KPIs resettés au 30/06 (matrice N=1) et des KPIs cumulés depuis le 23/06 (Top 1 = 50 % soit 3/6, Top 3 = 71 % soit 10/14, calculés en cumul sur le decision-log, journaliste.py lignes 2778 et suivantes, fenêtre affichée 23/06 au 01/07). Deux périmètres temporels différents sur la même page, sans le dire : Thomas compare des chiffres incomparables.

---

## Verdict par horizon

- 24h : SEUL horizon jouable au 08/08. Atteignable en N (26-28 possibles contre 15 requis) SI moratoire sur les resets et SI Sucre/USD-JPY sont réparés. NON démontré en win rate : tradable observé 43,2 % (ancien moteur), 23,1 % sur l'unique jour du nouveau. Sur la voie du N, pas encore du WR.
- 7j : PAS sur la voie et ne peut pas l'être : maximum 5 observations non-chevauchantes au 08/08 contre 15 requises. Premier jalon honnête possible : mi-octobre 2026.
- 1m : PAS sur la voie, structurellement : 1 observation non-chevauchante au 08/08. N >= 15 indépendants = automne 2027. Aucune mesure n'existe encore (première le 23/07).

## Top findings

| Prio | Finding (preuve) | Recommandation (une seule) |
|---|---|---|
| P0 | Reset global des 15 cellules au 30/06, le 6e en 20 jours (ref-changed.json) : 87 mesures sur 102 écartées, N repart de 0 à 28 jours ouvrés du jalon ; un 7e reset après le 17/07 environ tue le 08/08 même en 24h | Moratoire écrit et signé sur tout changement générant un ref_changed jusqu'au 08/08 (seule exception : bug de MESURE prouvé type L027) |
| P0 | Le jalon "3 horizons N >= 15 au 08/08" est impossible par construction pour 7j (max 5 obs) et 1m (max 1 obs), en contradiction avec la règle gravée 24h-only (SELECTION-RULE.md lignes 94-99) | Acter par écrit avec Thomas : 08/08 = verdict 24h-only ; jalon 7j au 13/10/2026 ; gate 1m abandonné (observabilité pure) |
| P1 | S&P 500, Nasdaq, VIX mesurés depuis le prix d'émission 7h (prix de nuit) au lieu de l'ouverture de marché : 18/18 mesures non conformes à L027, car ^GSPC/^IXIC/^VIX absents de prix-ouverture/*.json | Réparer le stamp d'ouverture US (run 15h30/18h) et faire échouer bruyamment la mesure des non-continus si l'ouverture manque, au lieu du fallback silencieux vers l'émission |
| P1 | Sucre et USD/JPY : 4/4 mesures en "suivi-interrompu" (prix_echeance null) depuis leur introduction du 26/06 ; 2 cellules sur 15 mortes-nées | Corriger le fetch du prix d'échéance de CANE et USD/JPY avant le 03/07, sinon les retirer de l'univers du jalon |
| P1 | WR tradable 24h plafonné par les NC : 36,5 % de NC globaux, cellules lentes disqualifiées d'office (CAC 40 : 5 NC / 6, plafond 17 %) | Documenter AVANT le 08/08 (anti post-hoc) la liste des cellules dont le plafond NC rend 70 % inatteignable, pour que le verdict du 08/08 ne soit pas lu comme un échec du moteur sur ces cellules |
| P2 | Historique pré-22/06 absent du repo (commit racine d7ff14d du 27/06 ; plus ancien bulletin 22/06) : cutovers 11-17/06 invérifiables sur données brutes | Sauvegarder désormais bulletins et logs dans le repo au fil de l'eau (déjà le cas depuis le 27/06), et le noter comme limite d'audit dans le CHANGELOG |
| P2 | Page performance : matrice resettée au 30/06 mais Top 1 / Top 3 cumulés depuis le 23/06 sur la même page, deux périmètres non signalés | Afficher la date de départ du comptage sur chaque bloc de la page (colonne ou sous-titre "depuis le JJ/MM") |

Fin de l'audit. Signé : l'Analyst, 2026-07-01.
