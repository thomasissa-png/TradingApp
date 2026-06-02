# Gates — ANALYST round 2 (convergence)
**2026-06-02 | Position méthodo finale**

> Lecture de : `gates-CONSOLIDE.md`, `gates-newstrader.md`, `gates-speculateur.md`, `gates-analyst.md` (round 1).
> Objectif : valider/contester les 9 gates consensus, défendre ou lâcher les gates solo, fixer l'ordre de build.

---

## 1. Validation des 9 gates consensus (C1–C9) et contestation des priorités

### C1 — Cohérence de signe DeepSeek + table macro : VALIDÉ, priorité REVUE

Consensus NT+Sp, P0. Je valide le fond — c'est bien l'erreur la plus chère. Un point de méthodo cependant : la table de référence macro (CPI haut → SHORT actions) doit être **figée dans le code, non dans le prompt**. Si elle est dans le prompt, elle est invisible au CI et peut dériver silencieusement. Gate valide, implémentation à contraindre.

Priorité relative : C1 est P0 mais il est plus difficile à tester automatiquement que C2 (jugement sémantique). Il appartient au Lot D, pas au Lot A. La consolidation le place bien. Pas de contestation sur l'ordre.

### C2 — Intégrité quant (bornage z-score, std=0, prix>0, NaN/Inf, anti-spike) : VALIDÉ, priorité CONFIRMÉE

Consensus NT+Sp+An. P0 absolu. C'est mon gate #1 et #2 du round 1. Cinq sous-gates déterministes, tous automatisables en assertions pytest. Le Lot A doit commencer ici — c'est le rapport effort/impact le plus élevé du pipeline. Aucune contestation.

### C3 — Arbitrage divergence quant↔news (au lieu d'additionner) : VALIDÉ avec réserve méthodo

Consensus Sp+NT. Je valide l'objectif. Réserve technique : "arbitrer" ne doit pas signifier "trend-price gagne toujours". La règle trend-first est un bon défaut, mais elle doit être **paramétrée et loggée** — sinon on crée un biais systématique invisible dans le decision-log. Gate valide, mais la spec d'implémentation doit inclure : (a) règle explicite et nommée, (b) log de chaque arbitrage, (c) test CI avec fixture contradictoire. Sans ces trois points, le gate devient une boîte noire.

### C4 — Anti-bascule mono-news + quorum de sources indépendantes : VALIDÉ, priorité DISCUTABLE

Consensus NT+Sp. Je valide le gate. Contestation sur le périmètre : le "quorum de sources indépendantes" est difficile à mesurer rigoureusement — deux sources distinctes peuvent reproduire exactement la même dépêche Reuters sans être indépendantes (cascade de reposts détectée en T1 mais non comptée par source). La spécification doit distinguer "sources distinctes" (nom du flux) et "événements dédup indépendants" (event_id différents post-T1). Sans cette précision, le gate est flou et son CI est impossible à écrire.

**Ma version préférée** : gate = "≥2 event_id non-relatifs (distance T1 > seuil) pour autoriser un flip". C'est déterministe et testable.

### C5 — Intégrité mesure (verrou prix d'émission, échéance figée, zéro look-ahead) : VALIDÉ, PRIORITÉ MAXIMALE

Consensus NT+An+Sp. C'est mon gate #4 du round 1. P0 absolu. Aucune contestation. Précision méthodo que j'ajoute : le verrou doit être **write-once** — le fichier `prix-emission/YYYY-MM-DD.json` ne doit pas être réécrit si le ticker existe déjà. Une assertion CI doit vérifier l'idempotence de ce fichier (écriture × 2 sur même date → aucun changement).

### C6 — Cohérence inter-horizons (LONG 24h / SHORT 7j sans cause datée) : VALIDÉ, périmètre à préciser

Consensus Sp+NT+An. Je valide. Point méthodo : "cohérence" ne signifie pas "interdit d'avoir des horizons contradictoires". Un retournement attendu entre 24h et 7j est légitime et doit être **explicité**, pas bloqué. Le gate doit être un drapeau + explication obligatoire, pas un rejet dur. Si le gate rejette toute séquence contradictoire, il force des conclusions artificiellement monotones. Garder la règle souple : drapeau + event_id de cause ou note texte.

### C7 — Publication : cohérence biais agrégé↔détail + affichage conviction/contre-tendance/flip : VALIDÉ

Consensus NT+Sp+An. Je valide sans réserve. C'est le dernier rempart humain avant exécution. La checklist d'affichage minimum doit contenir : (1) biais global agrégé recalculé depuis les cellules, (2) drapeau `contre_tendance` visible, (3) drapeau `flip` avec delta vs cycle précédent, (4) drapeau `faible_conviction` si score < seuil. Ces quatre éléments doivent être testés en CI sur le template HTML.

### C8 — Détection "déjà cotée" (already priced) + démenti/correction chaînés : VALIDÉ, mais déclassé à P1 sur l'aspect "démenti"

Consensus NT+(Sp partiel). Je valide la détection "déjà cotée" — c'est le piège n°1 du news trading. En revanche, le chaînage des **démentis/corrections** est une fonctionnalité significativement plus complexe à implémenter correctement (il faut identifier la news d'origine, chaîner les event_id, gérer l'annulation de score). Je propose de **séparer ce gate en deux** :

- C8a — détection already priced via movement price check : P0, automatisable.
- C8b — chaînage démenti/correction : P1, revue humaine, post-shadow.

Fusionner les deux dans C8 P0 crée un gate non-automatable dans le Lot D, ce qui ralentit le build.

### C9 — Intégrité horodatage/TZ à l'ingestion : VALIDÉ, priorité MONTÉE

Consensus NT+An+Sp. Unanimité méthodo. C9 devrait monter à Lot A (avec C2), pas rester en Lot E. La raison : une corruption TZ fausse la fraîcheur en S3 ET le prix d'émission en S8 — c'est un gate transverse qui corrompt deux autres gates C5 et C4 si mal ordonné. Corriger C9 après avoir construit C5 = construire C5 sur des fondations instables.

**Ma correction à la roadmap** : C9 passe en Lot A, en parallèle de C2. Effort : 2h (normalisation systématique à l'ingestion via `dateutil.parser` + assert UTC).

---

## 2. Contestation de gates solo des autres experts

### [NT] Latence d'ingestion (lag horodatage source → ingestion) — P0 NT

Je conteste la priorité P0. Ce gate mesure le délai entre la pubDate du flux et le moment d'ingestion. C'est utile mais il n'est **pas déterministe** — le lag dépend du réseau, du créneau d'exécution du workflow GitHub Actions, du délai éditorial de la source. Un assert CI ne peut pas tester ça de manière stable. De plus, le contenu informatif est déjà couvert par C9 (TZ) et S3 (fraîcheur T2). Je propose : **P2, monitoring dashboard** (log du lag moyen par source), pas gate bloquant.

### [NT] Couverture par classe d'actif (flux FX morts → conclure quand même sur EURUSD) — P1 NT

Je conteste la formulation. C'est un cas particulier de source_monitor (S1 déjà implémenté) étendu au niveau "actif". La vraie question méthodo est : le système doit-il publier une conclusion sur un actif quand 0 flux vivant le couvre ? Oui, ce gate a de la valeur. Mais il est recouvert par S5 (suffisance données, en build). Je propose de ne pas créer un nouveau gate — plutôt enrichir le périmètre de S5 pour intégrer la couverture par actif. **Pas de gate supplémentaire, enrichissement S5.**

### [NT] Anti-hallucination de citation (chiffre absent du texte source) — P0 NT

Je valide l'intuition mais conteste la faisabilité en tant que gate bloquant. Pour détecter qu'un chiffre cité dans la synthèse est absent du texte source, il faut soit un second appel LLM (coût), soit une extraction regex + comparaison (fragile). Ce gate est **non-déterministe et coûteux**. Ma position : le couvrir via la règle d'abstention (S2-G6 / confiance LLM seuillée) plutôt que par un gate indépendant. **Déclasser à P2, traité via le gate de confiance extraction.**

### [Sp] Score vs momentum prix récent — P0 Sp

Je valide complètement. Ce gate est méthodologiquement central : si le score dit LONG et le prix baisse depuis 5 séances consécutives, la conclusion est structurellement à contre-tendance sans que personne ne le voie. Automatisable : `assert direction_score == sign(price_change_horizon)` ou drapeau `contre_momentum`. **Je maintiens ce gate en P0**, il était dans ma liste solo et je regrette qu'il ne soit pas en consensus C. Je le défends ici.

### [Sp] Cohérence inter-actifs corrélés (LONG S&P + LONG VIX simultanément) — P1 Sp

Je conteste la priorité P1 et propose P2. La corrélation VIX/S&P est structurelle mais pas toujours absolue (VIX peut monter légèrement en bull market sur incertitude sectorielle). Un gate trop strict sur les corrélations inter-actifs risque de bloquer des conclusions légitimes. De plus, ce gate nécessite une matrice de corrélation maintenue — complexité de maintenance élevée. **P2, revue humaine trimestrielle.**

---

## 3. Gates méthodo sous-représentés dans la consolidation

### Multiple-testing (36 cellules) — actuellement P2 "solo An"

Je maintiens que ce gate doit rester P2 mais je veux **fixer la date de son activation** : il doit être obligatoire AVANT toute décision de passage en émission réelle basée sur un KPI statistique. Actuellement il est dans le Lot E sans date. Ma position : le multiple-testing n'est pas urgent en shadow (les KPI ne servent qu'à décider si on sort du shadow), mais si Thomas lit "taux de réussite 68%, p=0.03" sans correction Bonferroni sur 36 cellules, la décision de passage en émission est statistiquement invalide. **Gate P2 mais avec trigger clair : avant activation émission réelle.**

### Idempotence bout-en-bout — P1/P2 "solo An"

Je lâche l'idempotence comme gate bloquant P0. Je la maintiens comme test CI P2 pour les composants déterministes (dédup, scoring). La raison : l'idempotence parfaite est impossible avec des appels LLM (température=0 réduit mais n'élimine pas la variabilité selon la charge API). Tester l'idempotence sur les couches purement déterministes (S3, S4, S6) est précieux et automatisable. **P2 CI pour S3/S4/S6 uniquement.**

### Distribution dégénérée des scores — P1 "solo An"

Je maintiens P1. Un signal d'alarme simple : si 80% des scores sur 30 runs tombent dans [-0.05, +0.05], le scoring est pathologique indépendamment de la direction. Ce n'est pas une contrainte de build, c'est une alerte monitoring. Automatisable : calcul de la variance empirique des scores en fin de chaque run, log dans `performance.md`. **P1 monitoring, pas gate bloquant.**

---

## 4. Ordre de build final — Top 5 par ratio impact/effort

| Rang | Gate(s) | Ratio impact/effort | Type | Lot |
|---|---|---|---|---|
| **#1** | **C2 + C9** : bornage z-score + NaN/Inf + prix>0 + std=0→n/a + normalisation TZ UTC | Très élevé — 5 assertions pytest, 0 jugement sémantique, corrige 2 vecteurs de corruption silencieuse en même temps. | **CI automatisable** | A |
| **#2** | **C5** : verrou prix d'émission write-once + assertion `échéance ≥ émission` + `prix_courant_date ≥ bulletin_date` | Très élevé — 3 assertions déterministes, protège l'intégrité de TOUS les KPI. Sans ce gate le reste du scoring est anecdotique. | **CI automatisable** | B |
| **#3** | **C3 + [Sp] score-vs-momentum + hystérésis** : règle trend-first avec log de l'arbitrage + drapeau contre_momentum + marge minimale pour flip | Élevé — coeur métier, mais complexité accrue : la règle trend-first doit être spécifiée précisément avant le code. Effort ~1,5j. | **Revue humaine (spec) + CI (résultat)** | C |
| **#4** | **C4 + [Sp] hystérésis** : anti-bascule mono-news avec quorum event_id non-relatifs + marging anti-flip marginal | Élevé — réduit directement les faux retournements. Automatisable si on définit "event_id non-relatif" rigoureusement (distance T1 > seuil). | **CI automatisable** | C |
| **#5** | **C7** : checklist affichage bulletin (biais recalculé depuis cellules + drapeaux contre_tendance/flip/faible_conviction) + test CI template HTML | Moyen-élevé — effort faible (template), impact fort (dernier rempart humain). | **CI automatisable (template)** | E |

**Hors top 5 mais à débloquer en parallèle** : C6 (drapeau inter-horizons, Lot C, effort faible une fois C3 spécifié) + [An] réconciliation Σ contributions (assertion 1 ligne, Lot A, effort < 30 min).

---

## 5. Points de convergence et divergences maintenues

### Je me range sur :

- **Ordre Lot A → B → C → D → E** : logique, je valide. Seul ajustement : C9 monte en Lot A.
- **12 gates automatisables CI avant sortie shadow** : critère de sortie solide, je le valide sans réserve.
- **C8 priorité P0** : je valide le fond (already priced), je demande seulement la scission C8a/C8b pour rendre le Lot D faisable.
- **[Sp] hystérésis anti-flip marginal** : j'accepte l'intégration en consensus implicite, c'est méthodo pur.

### Je maintiens (divergences réelles) :

1. **C9 doit monter au Lot A** — construire C5 (verrou prix d'émission) sans C9 (normalisation TZ) revient à verrouiller un prix avec un timestamp potentiellement incorrect. C'est une dépendance de build, pas une question de priorité relative.

2. **[Sp] score-vs-momentum (confrontation direction vs prix récent) mérite le consensus C** — c'est le gate qui détecte le résultat final d'une erreur dans C3 (arbitrage quant↔news mal paramétré). Sans ce gate, C3 peut être contourné en production sans que personne ne le voie.

3. **Multiple-testing P2 doit avoir un trigger de date explicite** — l'activer comme condition de passage en émission réelle, pas comme "à faire un jour". La décision d'émission est une décision financière ; les KPI qui la fondent doivent être statistiquement valides (correction BH sur 36 cellules).

4. **[NT] Anti-hallucination de citation : P2, pas P0** — non-déterministe, coûteux, recouvert par le gate de confiance extraction. Sa présence en P0 dans le document NT gonflera le Lot D sans valeur additionnelle claire.

---

## MA LISTE FINALE PRIORISÉE (méthodo)

Classée par urgence de build. Marquage **CI** = automatisable pytest | **H** = revue humaine requise.

| # | Gate | Étape | Priorité méthodo | Type |
|---|---|---|---|---|
| 1 | **C2 — Bornage z-score** `clip(-3,3)`, `std=0→n/a`, `prix>0`, `NaN/Inf` | S4/S6 | P0 — build immédiat | **CI** |
| 2 | **C9 — Normalisation TZ UTC** à l'ingestion (dateutil + assert UTC) | S1 | P0 — build immédiat (parallèle C2) | **CI** |
| 3 | **C5 — Verrou prix d'émission** write-once + `échéance ≥ émission` + `prix_courant_date ≥ bulletin_date` | S8 | P0 — intégrité KPI | **CI** |
| 4 | **[An] Réconciliation Σ contributions = score** — `assert abs(Σ - score) < 1e-9` | S6 | P0 — decision-log rejouable | **CI** |
| 5 | **C3 — Arbitrage quant↔news** : règle trend-first paramétrée + log arbitrage + fixture CI contradiction | S6 | P0 — cœur métier | **H (spec) + CI (résultat)** |
| 6 | **[Sp] Score vs momentum prix récent** — drapeau `contre_momentum` si direction ≠ sign(price_change) | S6 | P0 — détecteur de résidu C3 | **CI** |
| 7 | **C4 — Anti-bascule mono-news** : quorum event_id non-relatifs, plafond contribution par news | S3/S6 | P0 | **CI** |
| 8 | **[Sp] Hystérésis anti-flip marginal** — marge minimale pour changer de sens vs cycle précédent | S6 | P0 tendance | **CI** |
| 9 | **C6 — Cohérence inter-horizons** — drapeau si séquence contradictoire sans event_id de cause | S7 | P0 (drapeau, pas rejet dur) | **CI** |
| 10 | **C1 — Cohérence de signe DeepSeek** + table macro figée dans le code | S2 | P0 sémantique | **H (table) + CI (test fixture)** |
| 11 | **C8a — Détection already priced** (movement check) | S3 | P0 | **CI** |
| 12 | **C7 — Affichage bulletin** (biais recalculé + drapeaux contre_tendance/flip/faible_conviction) | S9 | P1 | **CI (template)** |
| 13 | **[An] Distribution dégénérée** — variance empirique scores sur 30 runs, log dans performance.md | S6 | P1 monitoring | **CI (log)** |
| 14 | **[An] Enum nature → exclusion scoring effective** | S2/S3 | P0 Phase 2 | **CI** |
| 15 | **C8b — Chaînage démenti/correction** | S3 | P1 post-shadow | **H** |
| 16 | **[An] Multiple-testing 36 cellules** (correction BH) | S8 | P2 — trigger : avant émission réelle | **H** |
| 17 | **[An] Idempotence S3/S4/S6** | S3/S4/S6 | P2 CI | **CI** |

**Règle de sortie shadow (12 gates CI obligatoires)** : rangs 1, 2, 3, 4, 6, 7, 8, 9, 11, 12 (template), 14 + réconciliation Σ.
**Condition émission réelle** : + rangs 5 (spec arbitrage validée), 10 (table macro codée), 16 (multiple-testing appliqué).
