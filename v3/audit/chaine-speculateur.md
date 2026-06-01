# Audit chaîne v3 — angle TRADER SPÉCULATEUR — DELTA run MIDI (01/06/2026 13h37, commit 99023fe)

Optique unique : « est-ce que je mets du cash sur cette cellule ? », vagues 24h/7j/1m.
Audit DELTA : comparé au run de 9h51 (`9e2ccc0`, verdict 5,5/10 — 1 trade franc S&P long, Pétrole long à fuir).
Le run de midi est PROCHE mais PAS identique : un changement structurel (câblage news) + 3 flips de matrice.
Ordre d'édition : où je mets du cash CE run → ce qui a changé → ce qui reste du bruit/mono-critère.

---

## 0. LE DELTA EN UNE PHRASE
Le tag directionnel de la news est ENFIN câblé au scoring (`facteur` 0.6 / 0.42 / null) — l'inversion ×0.42 dénoncée à 9h51 est **partiellement réparée** : la news ne s'inverse plus, elle est seulement atténuée. Mais le bug Pétrole survit (geopol M-O toujours lue LONG sur vague baissière, juste dégonflée). Côté trades : S&P reste la seule conviction propre, **Argent monte d'un cran** (flip SHORT→LONG sur 3 horizons), Pétrole reste le piège.

---

## 1. OÙ JE METS DU CASH SUR CE RUN

### Trade franc (une vraie ligne)
- **S&P 500 LONG 7j/1m (+4.88/+4.42)** — INCHANGÉ vs 9h51, et c'est toujours LA cellule du run. 3 critères, tous concordants : HY spread serré 2.72 (contrib +4.27 à 7j, le moteur), flux SPY +0.55/+1.37/+0.96, RSI 73.9 en léger frein (-0.76). Zéro divergence pm1/pond. Vague de fond haussière confirmée par le flux brut (PMI Corée 5 ans, optimisme Nvidia, futures US en hausse). Je trade, position modérée. Mince en nombre de critères (3) mais alignés et quanti-solides.

### Demi-lignes sous réserve
- **Argent LONG (+1.44/+2.77/+5.00)** — **NOUVEAU vs 9h51** : flip SHORT→LONG sur les 3 horizons. Tentant, mais le diagnostic de fond ne bouge pas : **51% du score 1m vient du ratio Gold/Silver saturé à -1.0** (contrib +7.0 sur +5.0 net — un plancher, pas un trend). Le driver news (« VC PMI bullish silver », trêve → argent en hausse) existe mais n'est PAS câblé (pas de critère news argent dans le scoring, juste mvt or 5j +1.26). Consensus apparent (6 critères) = monobloc déguisé. Demi-ligne max, stop serré : si le ratio G/S se dé-sature, le signal s'évapore.
- **Cuivre SHORT 7j/1m (-1.53/-3.31)** — quasi-inchangé. La macro Chine est baissière et ça colle (« factory activity stalls in May »). MAIS 79% du score sur COT saturé (+1.0 → contrib -5.0 à 1m), CONTREDIT par le ratio cuivre/or (+0.94 → +1.69 LONG). Petite ligne tactique, une révision COT hebdo la casse. NB : le driver news cuivre (mining strikes, news_construction) est passé `ia_synthese_faible` → contrib ZÉRO. Le signal repose à 100% sur le quanti positionnel.

### Ce que je ne touche PAS
- **Pétrole LONG (+9.84/+13.34/+10.35)** — **NO, toujours.** Score le plus fort du run sur l'actif dont le flux brut crie la détente (« biggest monthly loss in 6 years » côté mai). Le câblage a dégonflé le pondéré (+6.36/+9.22/+7.39 vs pm1) mais **n'a PAS inversé la direction** : geopol M-O et OPEC+ restent lues `+1` LONG. Le moteur a juste rendu son erreur moins violente, pas moins fausse. Si je tradais le pétrole, ce serait SHORT — l'inverse du signal. Piège à fort score, pas opportunité.
- **Coin-flips / divergences** : CAC (+0.21/+1.39/+1.03, faible), Or 24h (+0.17 pm1 / **-1.43 pond, divergence ⚠**), Café 1m (**-1.42 pm1 / +0.67 pond, diverge=true ⚠**), EUR/USD (mou, flip 24h SHORT → 7j/1m LONG). Le moteur « ne sait pas ». Rien.
- **Mono-critères** : Cacao (COT seul, 100%), Blé (geopol mer Noire). SHORT/LONG « propres » sur 1 donnée. Pas de cash. (détail §4)
- **Nasdaq** : se retourne dans la fenêtre (LONG 24h +4.25 → SHORT 1m -1.57). Diversifié mais pas directionnel. J'attends.
- **VIX LONG (+3.07/+1.77/+0.25)** — **flip SHORT→LONG sur les 3 horizons (nouveau)** mais c'est un LONG vol mécanique (niveau VIX bas 14.95 → contrib +4.5, term structure saturée -1.0 → -6.4 qui le mange). Pas un trade trend-follower, un artefact de mean-reversion sur niveau. Pass.

**Score cash CE run : 1 trade franc (S&P), 2 demi-lignes (Argent / Cuivre), 1 piège à fuir (Pétrole), reste = bruit/mono.** Identique en structure à 9h51, Argent en plus côté tentation (mais creux à l'analyse).

---

## 2. CE QUI A CHANGÉ vs 9h51 (le vrai DELTA)

### Changement STRUCTUREL — le câblage news (majeur)
À 9h51 j'écrivais : « le tag directionnel du fichier 1 n'est pas câblé au scoring, la news s'inverse ×0.42 ». **C'est maintenant câblé.** Le decision-log midi montre un champ `facteur` par critère news :
- `source_track: ia_synthese` → `facteur 0.6` (geopol mer Noire, sentiment IA, tension géopol, OPEC+, geopol M-O). La direction du tag est RESPECTÉE (mer Noire -1 → pond -0.6, baissier blé = correct), seule l'amplitude est réduite.
- `source_track: calendrier` → `facteur 0.42` (cycle Brésil café).
- `source_track: ia_synthese_faible` → `facteur null` → **contrib 0** (le prix a primé).
- Conséquence visible : sur le **Blé**, geopol mer Noire pousse maintenant -0.6 (baissier) = ALIGNÉ avec le flux brut. L'inversion dénoncée à 9h51 a disparu là où le tag est bien orienté.

### Ce que le câblage ne corrige PAS
- **Pétrole** : la news est bien câblée (facteur 0.6) MAIS le tag d'entrée est `+1` (LONG) alors que la vague de mai est baissière. Le moteur applique fidèlement une direction d'entrée fausse. **Le bug a migré de la transmission (réparée) vers le tagging (geopol M-O = haussier par défaut).** Score brut redescendu (+9.84 vs +9.99 à 9h51) — bruit, pas correction.

### Flips de matrice (3 mouvements de fond)
- **Argent** : SHORT → LONG (×3 horizons). Mouvement le plus net du run.
- **VIX** : SHORT → LONG (×3 horizons). Mécanique (niveau bas).
- **Café 1m** : LONG → SHORT (pm1), mais pond reste LONG → divergence. Bascule fragile.
- Mineurs : Cuivre 24h SHORT→LONG (+0.13, bruit), Or 24h SHORT→LONG (+0.17, divergent).

### Inchangé
S&P trade franc, Pétrole piège, couverture indices large (Nasdaq 6 critères), performance toujours en warm-up.

---

## 3. DeepSeek : MÊME direction news sur les 3 horizons — exploitable pour un trend-follower ?

C'est exact et visible partout : `geopolitique_mer_noire = -1`, `tension_geopol_moyen_orient = +1`, `sentiment_ia = +1` portent la **même valeur normalisée sur 24h, 7j et 1m**. Seule la `pertinence` (échelle d'horizon) module la contrib.

**Verdict trend-follower : ça NE m'aide PAS, et ça peut me piéger.**
- Un trend-follower lit le momentum PAR vague : un signal qui monte 24h→7j→1m est un trend qui s'accélère ; un signal qui se retourne dans la fenêtre est un piège. Or ici, la news est une CONSTANTE plate sur les 3 horizons. Elle n'apporte **aucune information de momentum** — c'est un biais de niveau, pas une pente.
- Pire : comme la contrib news croît mécaniquement avec la pertinence (montante vers 1m), une news constante FABRIQUE un faux « trend qui s'accélère ». C'est exactement l'artefact Pétrole (+9.84 → +13.34) et Cacao COT (+0.91 → +4.55) : le « +13 à 1m » n'est pas un momentum plus fort, c'est la même conviction × une échelle plus grande. **Un gros score 1m porté par une news plate n'est PAS un read de tendance — c'est de la dette de pondération.**
- Ce qu'un trend-follower veut, et qui manque : une news DATÉE avec une dérivée (« la détente s'accélère » vs « tension stable »). DeepSeek donne un état, pas une pente. Tant que la direction news ne se décline pas par horizon, je l'utilise comme **filtre de cohérence** (est-ce que ça contredit ma vague ?), jamais comme **signal de momentum**.

## 4. Les 5 critères passés `ia_synthese_faible` (le prix a primé) — bon ou mauvais ?

Les 5 : Cacao (EUDR, maladies_cabosses), Café (maladies_cabosses_rouille), Cuivre (mining_strikes, news_construction). Tous → `facteur null` → **contrib 0**.

**Pour moi, spéculateur : globalement BON signe, avec une nuance.**
- BON : le moteur refuse d'injecter une news faiblement sourcée comme conviction directionnelle. C'est exactement le garde-fou qui manquait quand le triplet news s'inversait à ×0.42. Mieux vaut un zéro honnête qu'un faux signal. Sur Cuivre, ça évite d'empiler une news « infra » bruitée par-dessus le COT.
- NUANCE / mauvais côté : ces 5 mises à zéro **vident encore plus des cellules déjà maigres**. Conséquence directe : Cacao tombe à **1 seul critère effectif** (COT, 100% du score), Café à 2 (COT + cycle Brésil calendrier ×0.42). Le « prix a primé » est vertueux SI le quanti prend le relais — mais sur Cacao/Café, il n'y a PAS de quanti de relais (météo, stocks, USD/BRL tous n/a). Donc « prix a primé » = en pratique « COT seul décide ». Le garde-fou est sain ; il révèle juste que ces cellules sont des coquilles.

**Net : bonne hygiène de signal, qui transforme des mono-critères déguisés en mono-critères assumés.** Je préfère — au moins je sais que je trade un COT, pas un consensus.

## 5. Mono-critères / bruit qui restent (la part non exploitable)

| Cellule | crit. effectifs | dominant | part | lecture spéculateur |
|---|---|---|---|---|
| Cacao 24/7j/1m | **1** | COT Cocoa | **100%** | mono-critère pur. LONG « propre », vide. Révision COT = retournement. |
| Blé 24/7j/1m | 3 (2 actifs réels) | geopol mer Noire | ~88% | quasi-mono, mais news ENFIN bien orientée (baissier). Cohérent ≠ tradeable. |
| Cuivre 1m | 2 | COT Copper (-5.0) | 79% | 2e critère (ratio cuivre/or) à CONTRE-SENS. Tension interne. |
| Café 1m | 2 | COT (+2.18) vs cycle (-1.5) | — | diverge=true. Signal nul. |
| EUR/USD | 2 | COT EUR / USD-JPY | — | 2 critères qui se battent. Mou. |
| Argent 1m | 6 | ratio G/S saturé -1.0 | 51% | « 6 critères » mais 1 saturé porte la moitié. |
| Nasdaq | 6 | TIPS -5.48 vs SOX +5.74 | — | **vraie diversité**, mais se retourne intra-fenêtre. Sain, pas directionnel. |

Trous noirs persistants (poids 8-12, contrib zéro) : Caixin PMI Chine (LE driver cuivre du jour, n/a partout), inventaires LME/SHFE, DXY trend 20j (absent sur 6 actifs), différentiels de taux EUR/USD, Breadth, météo café Minas Gerais, OAT-Bund (CAC). La news qualitative est désormais bien transmise ; les **gros drivers fondamentaux quanti restent des trous**.

---

## VERDICT GLOBAL — run MIDI

### Cash-or-not
Sur 36 cellules : **1 trade franc (S&P 500 LONG 7j/1m), 2 demi-lignes sous réserve (Argent LONG / Cuivre SHORT), 1 piège à fort score à fuir (Pétrole LONG), le reste = bruit, mono-critère ou divergence.** ~3 idées exploitables sur 12 actifs, comme à 9h51. La nouveauté Argent est tentante mais creuse à l'analyse (monobloc ratio G/S).

### Note : **6/10** (vs 5,5/10 à 9h51)
- Matière (events-log) : 9/10 — inchangé, drivers datés et taggés en direction.
- Transmission : **5,5/10** (vs 4,5) — **le +1 point du run**. Le câblage news (`facteur` 0.6/0.42/null) supprime l'inversion ×0.42 : c'est le correctif que je réclamais à 9h51. La news baissière mer Noire passe enfin baissière.
- Plafond : ce qui bloque la note plus haut →
  1. **Pétrole non corrigé** : le bug a migré de la transmission au tagging. Geopol M-O = LONG par défaut sur vague baissière. Tout score porté par un triplet news d'entrée mal orienté reste suspect.
  2. **News plate sur 3 horizons** : inexploitable en momentum, fabrique de faux « trends qui s'accélèrent » à 1m (artefact d'échelle, pas de pente).
  3. **Drivers quanti lourds toujours absents** (Caixin PMI, inventaires, DXY, différentiels taux) → cellules matières premières restent mono-critère.

### Pour le spéculateur, en une ligne
**Je trade S&P long sans réserve, demi-Argent / demi-Cuivre en sachant que ce sont des monoblocs, je shorte mentalement le Pétrole contre le signal, j'ignore le reste.** Le système a fait un vrai pas (news non inversée) mais ne sait toujours pas distinguer un trend qui accélère d'une news constante — exactement ce dont j'ai besoin pour décider de mettre du cash par vague.
