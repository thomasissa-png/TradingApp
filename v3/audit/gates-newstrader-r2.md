# GATES — Round 2 CONVERGENCE — NEWS TRADER senior (desk)

> Angle desk : ce qui me fait perdre du fric, c'est entrer du mauvais côté d'une news,
> entrer trop tard (déjà cotée), ou mesurer ma perf sur un KPI corrompu.
> Débat réel ci-dessous, pas de complaisance.

---

## 1. Validation des 9 gates consensus (C1-C9)

**Je valide les 9 sur le fond.** Tous touchent une erreur silencieuse à impact direction ou KPI. Mais je conteste la **priorité** sur 3 points.

| Gate | Mon verdict | Commentaire desk |
|---|---|---|
| **C1** Cohérence signe DeepSeek + table macro | **VALIDÉ — remonter en P0 #1** | C'est MA cause de perte n°1. Une news baissière classée LONG = j'achète le couteau qui tombe. La consolidation le met en Lot D (4e). Erreur : un bug de signe à la source contamine TOUT l'aval — C2/C3/C6 protègent un signal déjà inversé. Le re-check texte→sens doit précéder l'intégrité quant. |
| **C2** Intégrité quant (clip z, std=0, NaN, spike) | VALIDÉ P0 | Bon lot A. Déterministe, pas de débat. |
| **C3** Arbitrage divergence quant↔news | **VALIDÉ — co-P0 #2** | D'accord avec Spéculateur : l'addition aveugle est la racine des contre-tendances. Mais voir ma nuance §2 : la règle « tendance prix gagne par défaut » est dangereuse côté news. |
| **C4** Anti-bascule mono-news + quorum | **VALIDÉ mais DÉPRIORISER d'un cran** | Voir §2 — le quorum strict est un faux ami sur le desk news. |
| **C5** Intégrité mesure (verrou prix/échéance/look-ahead) | VALIDÉ P0 | Sans ça mon KPI est du flan. Lot B correct. |
| **C6** Cohérence inter-horizons | VALIDÉ P1 (pas P0) | Conteste la priorité : c'est un gate de LISIBILITÉ/observabilité, pas un gate qui empêche une perte. Une séquence LONG24h/SHORT7j incohérente est moche mais ne fait pas perdre si C1/C3/C7 sont là. À mettre en Lot E. |
| **C7** Publication cohérence + affichage flip/contre-tendance | **VALIDÉ — remonter P0** | Dernier rempart humain. Thomas DOIT voir un SHORT contre-tendance/flip avant d'armer un turbo. Aujourd'hui en Lot E (dernier) — trop tard. À monter dès qu'C1/C3 produisent les drapeaux. |
| **C8** Déjà cotée + démenti chaîné | **VALIDÉ — remonter P0** | Sous-estimé par les 2 autres (Sp le met entre parenthèses). Sur le desk news, entrer sur un move déjà fait est aussi cher qu'entrer du mauvais côté : « VRAI » non exécutable = faux positif qui pollue le KPI ET fait perdre Thomas en réel. C'est du métier news pur, pas du nice-to-have. |
| **C9** Intégrité horodatage/TZ | VALIDÉ P1 | Vrai problème en cascade (fraîcheur + prix émission). Mais c'est un fix d'hygiène localisé, pas un gate de jugement. P1 OK. |

---

## 2. Ce que je conteste chez les autres

**[Sp] « Tendance prix gagne par défaut » (règle trend-first de C3) — JE CONTESTE.**
Le Spéculateur veut que la tendance prix prime, et que la news ne renverse que si high+confirmed+quorum. Sur un desk news, **c'est exactement l'inverse du métier** : une vraie news fraîche (résultat trimestriel, sanction, défaut, décision banque centrale surprise) DOIT pouvoir casser une tendance prix instantanément — c'est le seul moment où on gagne vraiment. Sa règle me ferait rater tous les gaps. Convergence proposée : **C3 ne tranche pas un gagnant fixe, il DÉTECTE et DRAPEAUTE la divergence** (laisse l'arbitrage au cap α=0.8 existant + au flag 📰). La règle directionnelle dure appartient à C1 (cohérence de signe), pas à C3.

**[Sp] Quorum strict de N sources indépendantes (C4) — SUR-INGÉNIERIE côté news.**
Le scoop a UNE source par définition (Reuters casse une info en premier). Exiger un quorum me fait entrer 30 min après tout le monde = move déjà coté = perte. Le vrai garde-fou n'est pas « combien de sources » mais « est-ce une vraie news ou du bruit reposté » — et ça, T1/T2 + nature le font déjà. Convergence : C4 = **plafond mono-news + exiger nature=structurel/ponctuel high (pas verbal/rumor) pour autoriser un flip**, PAS un quorum numérique. Le quorum reste un drapeau d'observabilité, jamais un gate bloquant.

**[An] Multiple-testing 36 cellules (Bonferroni/BH) — FAUX PROBLÈME à ce stade.** P2 justifié, mais je l'enlèverais carrément de la roadmap court terme. On a N_eff=0/12, on est en warm-up. Corriger des p-values qu'on n'a pas encore = ingénierie prématurée. À ressortir uniquement quand N≥30 par cellule.

**[An] Idempotence extraction DeepSeek en CI (S2-G8) — bon mais pas prioritaire.** temperature=0 ne garantit pas la reproductibilité d'un LLM (drift serveur). Tester l'idempotence d'un appel réseau en CI = test flaky garanti. À reléguer en P2 hors chemin critique.

---

## 3. Gate critique que la consolidation a PERDU (mon angle desk)

**[NT-NEW] Cohérence `materiality` × `reliability` AVANT scoring (était S2-G7 chez Analyst, disparu du consensus).**
Une news `materiality=high` + `reliability=rumor` entre dans le score avec un poids fort sur une base fragile. Sur le desk c'est le piège classique : la rumeur qui bouge le marché 10 min puis se fait démentir. Aujourd'hui rien ne combine les deux champs. Ce gate doit **plafonner le poids d'un signal high-materiality si reliability est faible**, en amont du cap α. Il est complémentaire de C8 (démenti) : C8 attrape le démenti APRÈS, ce gate attrape la fragilité AVANT. P0 desk. **La consolidation l'a noyé — je le réclame.**

Second manque mineur : **[NT] flag `llm_empty_run`** (S2-G6 Analyst) — un run où DeepSeek sort `impacts:[]` partout n'est pas distinguable d'un run sans news réelle. Côté desk = je crois « marché calme » alors que mon extracteur est mort. P1, pas perdu de vue.

---

## 4. Si je ne câble que 5 gates ce mois — ordre desk

Critère unique : **probabilité × coût d'une perte réelle pour Thomas.**

1. **C1 — Cohérence de signe DeepSeek + table macro.** La perte la plus chère et la plus probable : tout part du mauvais côté. Rien en aval ne rattrape un signe inversé à la source. Priorité absolue.
2. **C2 — Intégrité quant (clip z / std=0 / NaN / spike).** Demi-journée, déterministe, supprime la conviction artificielle à 100% sur donnée corrompue. Quick win à fort levier.
3. **C8 + NT-NEW — Déjà cotée / démenti + materiality×reliability.** Le cœur du métier news : ne pas entrer sur un move fait, ne pas surpondérer une rumeur. C'est ce qui me distingue d'un quant pur.
4. **C3 — Détection (pas arbitrage forcé) divergence quant↔news.** Drapeau de contradiction. Pas de règle trend-first dure. Évite le SHORT 51%/49% silencieux.
5. **C7 — Publication : afficher flip / contre-tendance / 📰.** Dernier rempart humain. Si Thomas voit le drapeau, il ne mettra pas le même montant sur un signal fragile. Plus utile que C5 ce mois-ci car protège l'exécution réelle, pas juste le KPI.

> Sacrifiés ce mois (assumé) : C4 (quorum — voir mes réserves), C5 (intégrité KPI — important mais on est en shadow, le KPI n'arme rien encore), C6 (lisibilité), C9 (hygiène TZ).

---

## 5. Convergence — où je cède, où je tiens

**Je me range :**
- **Sur C2 (intégrité quant)** — l'Analyst a raison, c'est le socle déterministe, à faire en premier techniquement (Lot A). Je le mets #2 fonctionnel mais je ne conteste pas qu'il soit câblé en tête car c'est ½ journée.
- **Sur la mesure flip vs continuation (Sp, S8)** — bon point, je n'y avais pas pensé sous cet angle. Mesurable dès le decision-log, valide objectivement si nos retournements news gagnent. Je l'adopte en P1 (P0 pour le Spéculateur, P1 pour moi car ça mesure, ça n'empêche pas une perte immédiate).
- **Sur la réconciliation Σ=score (An, P0)** — d'accord, sans ça le decision-log est inrejouable. À grouper avec C2 dans le Lot A (assertion gratuite).

**Je tiens :**
- **C1 #1 absolu** contre la consolidation qui le met en 4e lot. Le signe à la source prime sur tout.
- **Contre la règle trend-first dure de C3** : sur un desk news, la news fraîche DOIT pouvoir casser la tendance — C3 détecte, le cap α arbitre, C1 garantit le sens.
- **Contre le quorum bloquant (C4)** : faux ami côté scoop. Plafond mono-news + seuil nature/reliability, oui ; comptage de sources bloquant, non.
- **C8 et NT-NEW (materiality×reliability) sont du métier news, pas du luxe** — je refuse leur déclassement.

---

## MA LISTE FINALE PRIORISÉE (desk)

1. **C1** — Cohérence de signe DeepSeek + table macro (CPI/NFP/taux). *P0 — n°1 absolu, le signe avant tout.*
2. **C2 + réconciliation Σ=score** — Intégrité quant (clip z / std=0 / NaN / spike) + assertion somme. *P0 — socle déterministe, ½ j.*
3. **C8 + NT-NEW** — Déjà cotée / démenti chaîné + plafond materiality×reliability. *P0 — cœur métier news.*
4. **C3** — Détection (drapeau) divergence quant↔news, sans règle trend-first dure. *P0 — l'arbitrage reste au cap α.*
5. **C7** — Publication : afficher flip / contre-tendance / 📰. *P0 — dernier rempart humain avant le turbo.*
6. **C5** — Intégrité mesure (verrou prix/échéance/look-ahead). *P0 différé — KPI n'arme rien en shadow.*
7. **C4** — Plafond mono-news + seuil nature/reliability (PAS quorum bloquant). *P1 — drapeau, pas blocage.*
8. **S8 flip vs continuation séparé** (Sp). *P1 — valide objectivement le moteur de retournement.*
9. **C6** — Cohérence inter-horizons. *P1 — lisibilité, pas perte directe.*
10. **C9** — Intégrité horodatage/TZ. *P1 — hygiène en cascade.*
11. **llm_empty_run** + multiple-testing. *P2 — quand N≥30, pas avant.*
