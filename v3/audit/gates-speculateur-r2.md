# Gates pipeline — SPÉCULATEUR trend-follower (round 2, convergence)

> Débat réel, brutal. Mon seul juge : combien de positions à CONTRE-TENDANCE chaque gate élimine.
> Tout le reste (schéma JSON, XSS, disclaimer, atomicité git) est de la plomberie. Utile, mais ça ne fait pas perdre une jambe de trade.

---

## 0. Cadrage : ce qui me fait perdre de l'argent

Un trend-follower perd sur exactement 4 erreurs de DIRECTION :
1. **Mauvais côté dès le départ** (signe news inversé) → C1.
2. **Le quant dit tendance haussière, la news me retourne SHORT** (additionner au lieu d'arbitrer) → C3.
3. **Je flippe sur du bruit** (marginal + mono-news) → hystérésis + C4.
4. **Je conclus contre le prix qui bouge déjà** (score qui ignore le momentum) → score-vs-momentum + C6.

Tout gate qui ne touche PAS l'une de ces 4 erreurs est, pour moi, du polish. Je le dis sans détour plus bas.

---

## 1. Validation des 9 gates consensus (C1-C9)

| Gate | Mon verdict | Commentaire trend |
|---|---|---|
| **C1** signe DeepSeek + table macro | **VALIDÉ — P0 absolu** | Si le signe est faux, hystérésis/quorum/momentum corrigent un signal déjà mort-né. Racine #1, point. |
| **C2** intégrité quant (clip z, std=0, NaN) | **VALIDÉ — P0 mais préalable, pas finalité** | Un z=15 non borné fabrique une fausse méga-tendance. MAIS attention : C2 protège le CALCUL, pas le JUGEMENT. Le ranger en Lot A est correct (rapide, déterministe), à condition de ne pas croire qu'il suffit. C2 vert + C3 absent = on calcule proprement une position à contre-tendance. |
| **C3** arbitrage quant↔news | **VALIDÉ — MON P0 #1 de jugement. Je défends son rang (voir §3).** | C'est LE gate qui décide qui gagne quand le fondamental court terme (news) contredit la tendance établie (quant/prix). Sans règle de défaut, on additionne et le bruit news gagne. |
| **C4** anti-bascule mono-news + quorum | **VALIDÉ — P0** | Indissociable de l'hystérésis. Une dépêche fraîche ne doit JAMAIS retourner une tendance à elle seule. |
| **C5** intégrité mesure (verrou émission) | **VALIDÉ — P0 mais c'est de la MESURE, pas de la DIRECTION** | Crédibilise le KPI. Je le soutiens, mais soyons honnêtes : un verrou de prix d'émission ne corrige aucune position à contre-tendance en temps réel. Il dit a posteriori si j'avais raison. Important pour la confiance, neutre pour la justesse de tendance live. Rang OK car bon marché et bloquant pour sortir du shadow. |
| **C6** cohérence inter-horizons | **VALIDÉ — MON P0 #2. Je défends son rang (voir §3).** | LONG 24h / SHORT 7j sans cause datée = le lecteur prend la mauvaise jambe. Une séquence d'horizons DOIT raconter continuation ou retournement daté. |
| **C7** publication conviction/contre-tendance/flip | **VALIDÉ — P0 d'affichage** | Dernier rempart : Thomas doit VOIR « SHORT contre-tendance / flip » et ne pas l'exécuter comme un LONG solide. Capital. Mais il dépend des gates amont qui PRODUISENT ces drapeaux (C3, hystérésis, momentum). Sans eux, C7 affiche un drapeau qui n'existe pas. C7 est l'aboutissement, pas le départ. |
| **C8** déjà cotée + démenti | **VALIDÉ — P1 pour moi, pas P0** | Entrer sur un move déjà fait : c'est de l'exécution/timing, pas de la direction. Le SENS reste juste (la tendance est bien là), c'est juste tard. Pour un news trader pur c'est P0 ; pour un trend-follower qui tient la position, entrer tard sur la bonne tendance reste gagnant. **Je conteste son P0 implicite** (voir §2). |
| **C9** horodatage/TZ | **VALIDÉ — P0 d'infrastructure** | Empoisonne fraîcheur (C4) ET prix d'émission (C5) en cascade. Transverse, donc à blinder tôt. Pas glamour mais pré-requis. |

**Conclusion §1 : je valide les 9.** Mais je refuse leur mise à plat. Trois ont un impact DIRECTION fort (C1, C3, C6 + le couple C4/hystérésis), trois sont des pré-requis/mesure (C2, C5, C9), deux sont affichage/timing (C7, C8). La priorité doit refléter ça, pas l'ordre des lots.

---

## 2. Ce que je conteste chez les autres

### Contre l'Analyst — trop de gates « calcul propre » sur-priorisés P0
- **S4-G1/G2/G5 (prix>0, NaN, std=0)** : tous P0 chez l'Analyst. Or ce sont des sous-cas de C2. Les empiler en P0 distincts gonfle artificiellement la liste P0 et noie mes vrais P0 de jugement. **Un seul gate C2 consolidé suffit. Ne pas compter 4 P0 là où il y en a 1.**
- **S6-G1 réconciliation Σ = score (P0)** : l'Analyst en fait un P0. Je le rétrograde **P1 pour la direction**. Un score irréproductible est un problème d'AUDIT, pas de tendance. Si Σcontrib ≠ score de 0,3 %, ma direction ne change pas. C'est important pour le decision-log, ça ne sauve aucune jambe. **P0 d'observabilité, P1 de tendance.**
- **S2-G5 enum nature → exclusion scoring (P0)** : d'accord que c'est structurant, mais l'impact tendance dépend de C3. Si un discours verbal « déjà coté » contribue, c'est exactement le cas que C3 (arbitrage) + C8 (déjà coté) doivent attraper. **Le ranger derrière C3, pas devant.**
- **S8-G8 multiple-testing Bonferroni (P2)** : OK P2, aucun impact direction. Bien classé.

### Contre le News Trader — il sur-priorise le TIMING d'entrée
- **C8 « déjà cotée » en P0 #2 de son top 5** : pour un desk news, oui. Pour la JUSTESSE DE TENDANCE, non. Entrer tard ≠ entrer du mauvais côté. **Je conteste frontalement : C8 ne mérite pas de passer devant C3/C6/hystérésis.** Une position prise tard sur la bonne tendance est récupérable ; une position à contre-tendance est une perte sèche.
- **S1 latence d'ingestion (P0)** : surtout un enjeu intraday news. Pour le swing/trend, une news de 40 min reste exploitable. **P1 trend, pas P0.**
- **S2 anti-hallucination de citation (P0)** : c'est de la conformité/qualité de synthèse, pas de la direction. Une citation hallucinée n'inverse pas forcément le signe (C1 attrape l'inversion). **P1.**

### Ce que je NE conteste PAS (et je le dis pour être honnête)
- C1, C2, C5, C9 des autres : solides, je m'aligne sans réserve.
- Le découpage en lots automatisables (12 gates pytest avant sortie shadow) : excellent, je le garde.

---

## 3. Gates critiques dilués par la consolidation — je défends leur rang

La consolidation a relégué **3 de mes gates en « SOLO P0 trend »** alors que ce sont eux qui réduisent le PLUS les positions à contre-tendance. Je les remonte :

1. **Hystérésis anti-flip marginal (S6)** — relégué « solo ». **INACCEPTABLE en solo.**
   Un score +0,05 → −0,05 flippe la position chaque cycle sur du bruit pur. C'est la machine à fabriquer des positions à contre-tendance la plus prolifique du pipeline : elle produit du flip à HAUTE FRÉQUENCE. C4 (quorum) traite le flip mono-news ; l'hystérésis traite le flip marginal multi-cycles. **Les deux sont nécessaires, l'hystérésis doit être au même rang que C4.** Je demande sa fusion dans le Lot C en tant que co-P0, pas en annexe.

2. **Score-vs-momentum prix récent (S6)** — relégué « solo P0 ». **À remonter en P0 de plein droit.**
   C'est le seul gate qui confronte directement la conclusion au PRIX qui bouge. Si je conclus SHORT alors que le prix fait +4 % sur l'horizon, drapeau obligatoire. C'est la définition même du contrôle trend-follower : ne jamais être du côté opposé au mouvement sans le savoir. **Sans lui, aucun gate ne regarde le prix réel de l'horizon.** C3 arbitre quant interne vs news ; le momentum arbitre conclusion vs réalité du marché. Complémentaires, pas redondants.

3. **Mesure flip vs continuation séparée (S8)** — relégué « solo P0 ». **J'accepte un rang plus bas (P1), MAIS pas la suppression.**
   C'est LE chiffre qui prouve que le moteur suit vraiment la tendance (taux de continuation correcte vs taux de flip correct). C'est de la MESURE, pas de la direction live — donc je concède qu'il vient après les gates de jugement. Mais sans lui, on ne saura jamais si le système est trend-follower ou contrarian par accident. **P1, dans le Lot E, non négociable sur l'existence.**

**Point dur : hystérésis et score-vs-momentum NE SONT PAS des solos. Ce sont mes C-niveau. La consolidation les a sous-évalués parce qu'un seul expert (moi) les a cités — mais c'est précisément mon domaine. Argument d'autorité assumé : sur la justesse de tendance, je suis l'expert de référence ici.**

---

## 4. Mon ordre de build final — les 5 gates qui tuent le plus de contre-tendance

Classés par nombre de positions à contre-tendance éliminées, du plus au moins :

1. **C1 — Cohérence de signe DeepSeek + table macro.**
   Élimine les positions du MAUVAIS CÔTÉ dès l'origine. Aucun gate aval ne rattrape un signe inversé. Volume d'erreurs le plus élevé sur le contre-intuitif (jours macro = gros volumes). **#1 incontestable.**

2. **C3 — Arbitrage divergence quant↔news (défaut : la tendance-prix gagne).**
   Élimine le SHORT 51 % news contre une vague haussière quant. Transforme « on additionne et le bruit gagne » en « la tendance établie a priorité, la news doit la battre franchement ». Cœur du métier trend.

3. **Hystérésis + C4 (quorum mono-news) — couple anti-flip.**
   Élimine le flip marginal multi-cycles (hystérésis) ET le flip mono-news (quorum). La plus grosse source de contre-tendance EN VOLUME de transactions. Je les fusionne car ils traitent deux faces du même bug : retourner une tendance sans raison suffisante.

4. **Score-vs-momentum prix récent.**
   Élimine la conclusion qui contredit le prix réel de l'horizon. Dernier filtre face à la RÉALITÉ du marché, pas aux données internes. Drapeau contre-tendance automatique.

5. **C6 — Cohérence inter-horizons.**
   Élimine la séquence d'horizons incohérente (LONG 24h / SHORT 7j sans cause datée) qui fait prendre la mauvaise jambe. Garantit que la position raconte continuation ou retournement DATÉ.

> Note : C2 et C9 sont des PRÉ-REQUIS de ces 5 (un calcul corrompu ou un TZ faux les sabote tous). Ils passent AVANT en ordre chronologique de build (Lot A), mais ils ne « tuent » pas de contre-tendance par eux-mêmes — ils empêchent juste mes 5 de travailler sur des données pourries. Donc : build C2+C9 d'abord (plomberie), puis mes 5 dans l'ordre ci-dessus.

---

## 5. Point de convergence

**Où je me range :**
- Je valide les 9 gates consensus C1-C9. Pas de gate consensus à supprimer.
- Je m'aligne sur C1 en #1 absolu : le signe avant tout, c'est incontestable même pour un trend-follower.
- J'accepte que C2/C5/C9 soient buildés tôt (Lot A/B) pour leur faible coût et leur statut bloquant-shadow, même s'ils ne sont pas des gates de direction.
- J'accepte de rétrograder « flip vs continuation » en P1 (mesure, pas direction live).
- J'accepte le découpage automatisable/revue humaine de l'Analyst tel quel.

**Où je MAINTIENS (lignes rouges) :**
- **Hystérésis et score-vs-momentum ne sont PAS des solos** : ce sont des P0 de jugement, à mettre au même rang que C3/C4 dans le Lot C. Refus de les voir traités en annexe.
- **C8 (déjà cotée) reste P1, pas P0** pour la tendance : entrer tard ≠ entrer à l'envers. Je conteste son rang dans le top 5 du News Trader.
- **Ne pas compter 4 P0 quant (S4-G1/2/4/5) là où C2 en couvre 1** : ça gonfle la liste P0 et dilue mes vrais P0 de direction.
- **S6-G1 réconciliation = P0 d'observabilité, P1 de tendance.** Un score irréproductible ne crée pas une position à contre-tendance.

**Synthèse de la convergence :** le consensus a raison sur QUI sont les gates, il a tort sur l'ORDRE pour la justesse de tendance. La hiérarchie correcte n'est pas « calcul → mesure → jugement » mais « pré-requis minimal (C2/C9) → JUGEMENT directionnel (C1/C3/hystérésis+C4/momentum/C6) → mesure & affichage (C5/flip-continuation/C7) ». Le jugement directionnel est le cœur ; le reste le sert.

---

## MA LISTE FINALE PRIORISÉE (tendance)

| Rang | Gate | Pourquoi (impact contre-tendance) | Priorité |
|---|---|---|---|
| **0a** | **C2** intégrité quant (clip z, std=0, NaN, anti-spike) | Pré-requis : sans calcul sain, tout le reste juge du bruit | P0 (plomberie, Lot A) |
| **0b** | **C9** horodatage/TZ | Pré-requis : empoisonne fraîcheur + prix d'émission | P0 (plomberie, Lot A) |
| **1** | **C1** signe DeepSeek + table macro | Mauvais côté dès l'origine — racine #1 | **P0 direction** |
| **2** | **C3** arbitrage quant↔news (défaut tendance-prix gagne) | SHORT 51 % news contre vague haussière | **P0 direction** |
| **3** | **Hystérésis + C4** (anti-flip marginal + quorum mono-news) | Flip sur bruit, plus gros volume de contre-tendance | **P0 direction** |
| **4** | **Score-vs-momentum** prix récent | Conclusion qui contredit le prix réel de l'horizon | **P0 direction** |
| **5** | **C6** cohérence inter-horizons | Mauvaise jambe prise par le lecteur | **P0 direction** |
| 6 | **C5** verrou prix émission + échéance figée | Crédibilité KPI (mesure, pas direction live) | P0 mesure |
| 7 | **C7** affichage conviction/contre-tendance/flip | Dernier rempart visuel — dépend des amont | P0 affichage |
| 8 | **Flip vs continuation** mesuré | Prouve que le moteur est trend-follower | P1 mesure |
| 9 | **C8** déjà cotée + démenti | Timing d'entrée, pas direction (entrer tard ≠ à l'envers) | P1 timing |
| 10 | **S6-G1** réconciliation Σ=score | Observabilité, pas direction | P1 audit |

**Ligne finale du spéculateur : le signe d'abord (C1), l'arbitrage de tendance ensuite (C3), l'anti-flip et le momentum pour ne jamais lutter contre le prix, la cohérence d'horizons pour raconter la bonne histoire. Le reste sert ces cinq. Tout ce qui ne touche pas la DIRECTION peut attendre.**
