# Audit de forme · Le Spéculateur · 2026-07-01

_Panel d'audit TradingApp v3 (Analyst / News Trader / Spéculateur). Angle : est-ce que MOI, trader turbo chez Bourse Direct, je peux exécuter des positions rentables en lisant uniquement ce que la page affiche ?_

## Notes

| Axe | Note /10 | Verdict en une ligne |
|---|---|---|
| Décider 24h | **6.5/10** | Le tableau « paris du jour » est bon, mais pas de sortie ni de stop à 7h, et le « Pourquoi » est parfois faux ou vide de sens |
| Décider 7j / 1m | **3.5/10** | On peut ENTRER (blocs Swing 7j et Positions 1 mois existent), on ne peut pas SUIVRE : zéro rappel des positions ouvertes, zéro échéance, zéro suivi multi-jours |
| Confiance / lisibilité | **5/10** | Honnêteté réelle sur la chauffe, mais incohérences visibles (justifications divergentes, cotation US absente à 12h, valeur suspecte sans ⚠️) et décodeur nécessaire |

## Q1. Décision 24h exécutable en moins de 2 minutes ?

**Oui pour le quoi/sens/prix, non pour la sortie.** Le bulletin du 01/07 à 07h23 donne d'entrée un tableau propre : « Café (Arabica) LONG 296.566 +8.77 », « Sucre LONG 9.79 +7.23 », « Cacao LONG 5079.97 +3.84 ». En 30 secondes je sais quoi jouer et dans quel sens. Ce qui manque ou parasite :

- **Aucune sortie à l'entrée.** Pas de stop, pas d'objectif, pas d'heure de revente sur la Sélection 24h. La règle réelle (« GAGNÉ si son max gain du jour dépasse 1 % ») n'apparaît que dans le suivi 12h et le bilan. Un turbo sans niveau d'invalidation affiché, je ne l'exécute pas proprement. Les blocs 7j/1m ont une colonne « Objectif » ; le 24h n'a rien.
- **La colonne « Pourquoi » peut être vide de sens ou fausse.** 01/07, Cacao LONG : « news net haussière (pas de titre représentatif aujourd'hui) ». Une raison qui dit « pas de titre » ne me dit rien. Pire, le 30/06, Cacao LONG +8.25 était justifié par « news net baissière : Offre mondiale de cacao plus abondante, pression sur les prix » : un pari LONG « expliqué » par une news baissière. Ça détruit la confiance en 5 secondes.
- **Conviction non bornée et confiance % fantôme.** La légende dit « à lire avec la confiance % », mais la confiance n'est affichée nulle part sauf pour Cuivre (« conf. faible (48%) »). +8.77, c'est fort par rapport à quoi ? Le tableau « Intensité comparable » (Café +1.35, Sucre +1.19) répond à la question mais il est enterré et étiqueté « informatif ».
- **Comparaison 30/06 (08h04) vs 01/07 (07h23) : l'heure d'émission flotte.** Le 30/06, un bulletin à 08h04 arrive APRÈS ma fenêtre d'entrée 7h-8h : prix de référence stampés à 08h04, entrée réelle décalée. Le 01/07 à 07h23 est bon. Sans heure garantie avant 7h30, la routine « j'entre entre 7h et 8h » n'est pas fiable un jour sur deux.

## Q2. Horizons 7j et 1m exécutables ?

**Prendre : oui. Suivre : non. L'affichage est 24h-centré, je le dis franchement.**

- Les blocs existent et sont bien formés : « Swing 7j (max 3) » (Sucre LONG +4.0 % @9.79, Café LONG +3.0 %, Or SHORT) et « Positions 1 mois (max 3) » (EUR/USD SHORT objectif 1.8 %, Café LONG +7.0 %) avec Sens / Objectif / Entrée / Porté par. C'est exécutable à l'entrée.
- **Mais aucun suivi multi-jours n'existe.** Le 30/06 le bulletin proposait EUR/USD SHORT 1m @1.13867. Le 01/07, le bulletin réémet EUR/USD SHORT 1m @1.14102 comme si de rien n'était : aucun « position ouverte hier, jour 2, entrée 1.13867, +0.2 % dans notre sens, échéance ~30/07 ». Si j'ai pris la position, la page ne me dit ni où j'en suis ni quand je dois rendre des comptes.
- Le suivi 12h/18h ne couvre QUE les positions 24h (titre explicite : « Suivi détaillé : toutes les positions 24h »). Le consigne de sortie 7j/1m (« sortie si la tendance de fond se retourne ») n'est vérifiable nulle part : aucun bloc ne dit si la tendance de fond d'hier s'est retournée.
- Cohérent avec performance.md : les tableaux 7 jours et 1 mois sont 15 lignes de « ⏳ en attente », 0 pari mesuré. Le système ne se juge même pas encore sur ces horizons.

## Q3. Suivi intra-day actionnable ?

**À moitié.** Le bon : la Sélection en tête avec Action tranchée (« 🟢 Laisse courir » Café +2.64 % à 12h, « 🟡 Sécurise » à 18h après reflux de +3.07 % à +0.65 %, avec la règle du demi-pic écrite). Lecture en 2 minutes : tenue. Le mauvais :

- **US via future : promesse non tenue.** La page annonce « on suit l'indice US en continu dès 8h (« 🔵 via future ») ». Or le suivi 12h affiche Nasdaq / S&P 500 / VIX : « ⏳ future : cotation en attente ». Je suis entré à 7h30 sur le future via OANDA, à midi je dois décider de revendre, et la ligne est vide. À 18h, « ⏳ données manquantes » alors qu'un Prix 18h est affiché (728.6, 749) : il manque juste l'ouverture, et rien ne l'explique.
- **« Suggestions de sortie : Aucune alerte » à 12h alors que le tableau au-dessus affiche 4 « 🔴 Coupe »** (Argent, Blé, Or, Coton). Si le bloc synthèse ne couvre que la Sélection, il doit le dire ; là, deux messages contradictoires cohabitent sur le même écran.
- **Valeur suspecte sans ⚠️ :** Blé « Max gain du jour +7.93 % » à 12h15 pour une position ouverte à 7h (ouverture 586.9, prix 12h 580.7). +7.93 % de max en une matinée sur le blé, personne n'y croit ; ça ressemble à un résidu de la veille (le bilan 30/06 montre un max adverse Blé de 7.39 %). Une valeur aberrante affichée sans avertissement contamine toutes les autres.
- Bon point : les statuts « ✅ gagne / ⚠️ perd », la colonne Tendance 18h (« ↑ s'accélère », « ↓ s'essouffle ») et « 🚨 Grosses actualités depuis 7h » sont exactement le format 2 minutes qu'il faut.

## Q4. Confiance et honnêteté

- **Le mode test est clair et bien affiché** : badge header « validation · 08/08 », footer « En validation, mise en service prévue le 08/08/2026 », encart « Tout est en chauffe » avec la règle gravée (WR tradable ≥ 70 % sur ≥ 15 paris). Performance.md est honnête : « 0 / 45 cellules fiables », « N faible, non concluant » sur le Top 1 à 50 %. Comme lecteur qui doit se construire une confiance avant le 08/08, je sais où j'en suis : nulle part encore, et on me le dit. C'est la bonne posture.
- **Mais deux affichages minent cette honnêteté** : (1) des lignes « Win rate 100.0 % » sur N=1 (Cacao, Café, S&P 500) restent visuellement des 100 % même avec le statut « ⏳ trop peu » à côté ; (2) « WR tradable 0.0 % » affiché pour des actifs à 0 pari (Argent, CAC 40...) : 0 % calculé sur rien, ça se lit comme un échec.
- **Symboles sans décodeur** : « ⚠️♻ » apparaît sur Cacao et Coton dans les tableaux ET dans « Cellules à surveiller », mais n'est défini nulle part dans la légende (qui couvre ◧ ↯ ⚠️ ⇄ ⌛). « pond: », « brut », « already-priced », « N_eff », « régimes=Y » exigent un décodeur.
- **« ⚠️ Cellules à surveiller » : 36 cellules listées sur 45.** Quand 80 % de l'univers est « à surveiller », plus rien n'est saillant : c'est du bruit, pas un avertissement.
- Les avertissements qui marchent : « conf. faible (48%) » sur Cuivre, « Écartés des paris pour news à contre-sens (↯) : Nasdaq (LONG), S&P 500 (LONG) » (excellent : ça explique pourquoi le n°1 au score n'est pas dans la Sélection), « fragile (1 seul critère) », « ⏳ pas encore (+0.48%) ».

## Q5. Forme pure

- **Tirets cadratins : préférence gravée violée.** 61 occurrences dans le bulletin du 01/07, 10 dans le suivi 12h, dans du texte affiché : « Flux muets (normal (tiret) tout dédupliqué/filtré...) », « Les paris du jour (max 3) (tiret) les plus fortes convictions », « Sélection du jour (tiret) progression », plus les légendes. `build_html.py` en produit aussi dans des libellés rendus (titres de tableaux, placeholders de cellules « (tiret) »). Le placeholder de cellule vide est défendable, le texte courant non.
- **Incohérence de justification entre briefing et suivi pour la MÊME position** : bulletin 7h, Café porté par « Tendance du café Arabica (3 jours) » ; suivi 12h, « Pourquoi ces positions » : « Tendance 3 jours + Tendance 7 jours + Maladies du caféier (rouille et cabosses) ». Cacao : bulletin « news net haussière » vs suivi « Maladies des cabosses + Positionnement + Tendance 20j + Réglementation UE ». Deux récits pour un même pari = je ne sais plus lequel croire.
- **Densité** : bulletin de 643 lignes dont ~280 de « Détail par actif » et 37 lignes de « Cellules à surveiller ». La page replie les sections, mais le pavé légende (« Comment lire les scores ») est répété intégralement dans CHAQUE bulletin, donc dans chaque vue jour de l'historique.
- **Jargon non traduit résiduel** : « zscore_abs » brut dans la colonne « Comment c'est lu » (Météo cacao, coton, café), « [pond:LONG +8.82] », « (val 0.08568, sens normal) », « n/a (lineaire : valeur non numérique) » (en plus sans accent).
- Bon point : le glossaire PMI/RSI/VIX/SKEW en une ligne, et les raisons en français des cellules (« taux réels US élevés : l'or/les sans-rendement coûtent à porter ») sont exactement le bon niveau.

## Top findings

### P0 (bloquants confiance/exécution)

1. **P0-1 · Le « Pourquoi » de la Sélection peut contredire le sens du pari** (Cacao LONG justifié par « news net baissière » le 30/06 ; « pas de titre représentatif » le 01/07) et diverge du « Pourquoi ces positions » du suivi. **Reco (rendu pur, zéro scoring)** : afficher dans « Pourquoi » le driver dominant déjà calculé (champ « Porté par », ex. « Positionnement cacao vendeur extrême ») au lieu du titre news, et faire lire au suivi la même source que le bulletin.
2. **P0-2 · Aucun suivi des positions 7j / 1m.** Prendre une position 1m est proposé, la suivre est impossible (pas de rappel entrée/date/échéance, pas de % courant, réémission chaque matin comme si c'était nouveau). **Reco (rendu pur)** : bloc « Positions 7j/1m ouvertes » dans le bulletin et le suivi : actif, sens, entrée stampée, jour n/N, % courant vs entrée, condition de sortie ; toutes les données existent déjà (prix stampés + prix du jour).
3. **P0-3 · Indices US illisibles à 12h malgré la promesse « via future dès 8h »** (« ⏳ future : cotation en attente » sur Nasdaq/S&P/VIX à 12h15 ; « données manquantes » à 18h avec un prix 18h pourtant affiché). **Reco (rendu + fetch d'affichage, zéro scoring)** : brancher le prix future OANDA déjà utilisé le matin sur les lignes 12h/18h, et à défaut afficher un ⚠️ explicite « future OANDA indisponible depuis 8h » plutôt qu'un ⏳ ambigu.

### P1

4. **P1-1 · Pas de sortie affichée à 7h sur le 24h** (ni stop ni objectif ; la cible +1 % n'apparaît qu'au suivi). Reco (rendu pur) : ajouter une colonne « Sortie » à la Sélection : « objectif +1 % / coupe si le pari casse / revente midi possible ».
5. **P1-2 · « Suggestions de sortie : Aucune alerte » contredit 4 « 🔴 Coupe » du même écran** (suivi 12h). Reco (rendu pur) : renommer « Suggestions de sortie (Sélection) » ou y remonter les 🔴 du tableau détaillé.
6. **P1-3 · Blé « Max gain +7.93 % » à 12h, valeur invraisemblable affichée sans ⚠️.** Reco (rendu) : flag ⚠️ automatique quand max gain > 3 × l'amplitude du jour, avec mention « valeur à vérifier ».
7. **P1-4 · « ⚠️ Cellules à surveiller » liste 36/45 cellules : du bruit, pas une alerte.** Reco (rendu pur) : ne lister que les cellules de la Sélection et des Jouables « forte », le reste est déjà flaggé dans les tableaux.
8. **P1-5 · Symbole « ⚠️♻ » affiché mais absent de la légende ; « confiance % » annoncée mais presque jamais affichée.** Reco (rendu pur) : compléter la légende et afficher la confiance % sur chaque ligne Jouables, ou retirer la mention.
9. **P1-6 · Heure d'émission instable (08h04 le 30/06 vs 07h23 le 01/07)** : un bulletin après 8h rate la fenêtre d'entrée. Reco (process, pas scoring) : engagement d'heure limite 07h15 affiché dans le header du bulletin, avec ⚠️ si dépassée.
10. **P1-7 · Tirets cadratins : 61 au bulletin, 10 au suivi, plus les libellés de build_html.py.** Reco (rendu pur) : passe de remplacement (deux-points, parenthèses, point) sur les chaînes affichées ; garder au plus le placeholder de cellule vide.

### P2

11. **P2-1 · « WR tradable 0.0 % » et « Win rate 100.0 % » sur 0-1 pari** se lisent comme des verdicts. Reco (rendu pur) : afficher « ⏳ » à la place de tout % tant que N < 5.
12. **P2-2 · Légende « Comment lire les scores » répétée dans chaque bulletin.** Reco (rendu pur) : la sortir dans un bloc replié unique de la page, hors du markdown du bulletin.
13. **P2-3 · Jargon résiduel** (« zscore_abs », « [pond: ] », « lineaire : valeur non numérique »). Reco (rendu pur) : table de traduction des libellés au moment du rendu.

## Handoff

- Livrable : ce fichier (`v3/audit/audit-forme-speculateur-2026-07-01.md`). Aucun autre fichier modifié.
- Pièces lues : bulletin 01/07 07h, bulletin 30/06 08h, suivi 01/07 12h et 18h, bilan 30/06, performance.md, structure `v3/data/index.html` (grep), chaînes de `v3/scripts/build_html.py`.
- Toutes les recos P0/P1/P2 sont du rendu ou du process d'affichage : aucune ne touche le scoring.
