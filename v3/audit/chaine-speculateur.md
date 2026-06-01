# Audit chaîne de production v3 — angle TRADER SPÉCULATEUR (run 01/06/2026, commit 9e2ccc0)

Optique unique : « est-ce que je mets du cash sur cette cellule ? ». 1er run post-correctifs
(indices débloqués via ETF Twelve + rate-limiter, contexte-prix ajouté, prix d'émission réparés).
Question : en bout de chaîne, signal EXPLOITABLE par cellule, ou conviction diluée de fichier en fichier ?

---

## 1. `events-log.md` — la matière première (drivers)
918 events, 107 à impact (fenêtre 48h). La matière reste la meilleure étape de la chaîne, et les VRAIS drivers de tendance sont là, désormais **avec une direction explicite** (colonnes `impacts` type `BRENT:SHORT:high`) — progrès net vs 31/05.

**Pétrole — le signal est BIDIRECTIONNEL et la vague de mai est BAISSIÈRE.** Le fichier le dit noir sur blanc :
- baissier (détente) : « Brent posts biggest monthly loss in six years », « oil drops 20% from 2026 peak », « worst month since 2020 », « US-Iran ceasefire framework », fracture OPEC+ (départ EAU) → tags `BRENT:SHORT:high` répétés (lignes 182, 183, 193).
- haussier (escalade) : Netanyahu Gaza 70%, frappes Beyrouth, Exxon « $150-160 », Ormuz → tags `BRENT:LONG:high`.
La balance penche **baissier sur mai** (« biggest monthly loss in 6 years » est un fait, pas une opinion). Le flux brut PORTE les deux côtés correctement taggés.

**Indices — drivers haussiers riches et datés** : Nvidia chip PC, Dell +757%/+32%, SK Hynix/Micron $1tn, SoftBank 75 Mds€ data centers France (driver CAC explicite), software « best month since 2001 ». Contre-poids : Fed (Bowman/Goolsbee/Kashkari, inflation énergie persistante → taux hauts) et taux réels. Tension claire et exploitable.

**Argent** : « extension de trêve, ouverture en hausse de l'argent » (`SILVER:LONG:medium`, ligne 201). Driver direct présent, c'est nouveau.

**Cuivre** : driver baissier réel et daté — « China factory activity stalls in May » / PMI mitigé. Présent dans le bulletin mais quasi-absent du flux taggé (un seul `COPPER:LONG:low` ligne 187, contradictoire).

Constat : **à l'entrée, le signal directionnel est FORT, daté et désormais taggé en direction.** Rien ne manque ici. Pic de qualité de la chaîne — 9/10.

## 2. `criteres-courants.md` — dilution / critères effectifs par cellule
**45 critères en n/a (`note: hors fenêtre`/valeur absente), ~66 alimentés.** La couverture a remonté (les indices ont enfin du quanti : SOX, flux QQQ/SPY/MSCI-France, spread Russell), mais la dilution structurelle des correctifs de 31/05 **n'est PAS corrigée** :

**La news directionnelle reste écrasée en triplet booléen ×0.42, à contre-sens du flux brut.** Le fichier 1 tagge `BRENT:SHORT:high` en majorité (vague baissière), mais le critère sorti est `tension_geopol_moyen_orient: 1` valeur_pondérée **+0.42 HAUSSIER**, et `opec_production_policy: 1` **+0.42 HAUSSIER**. La fracture OPEC+ (baissière dans le flux) devient un signal LONG. **Le signal s'inverse exactement comme au run 31/05.** Le tagging directionnel ajouté au fichier 1 n'est pas câblé au scoring.

**Critères effectivement portants (valeur_pondérée ≠ 0) par cellule** — ce sur quoi repose réellement la conviction :
- Argent : 6 (TIPS, mvt or, ratio G/S figé à **-1.0** → contrib max, alpha, COT, flux ETF). Mais le ratio G/S normalisé -1.0 est un plancher saturé, pas un trend.
- Nasdaq : 6 (TIPS, SOX 0.91, sentiment IA, flux QQQ, spread Russell 0.91, RSI). **Couverture enfin large** — progrès réel.
- VIX : 6 (niveau, term structure -1.0, SKEW, VVIX, COT, géopol). Mais term structure saturée à -1.0.
- Or : 5 / S&P : 3 / Pétrole : 5 / EUR/USD : 2 / CAC : 3.
- **Cuivre : 2** (COT à +1.0 saturé → SHORT, ratio cuivre/or +0.76 → LONG : les deux se contredisent). Mono-driver de fait.
- **Cacao : 1** (COT seul). **Café : 2** (COT + cycle Brésil). **Blé : géopol mer Noire domine.**

Drivers à poids fort qui contribuent ZÉRO (signal jeté) : Caixin PMI Chine (poids 12 sur Cuivre, poids 5 sur Argent/Pétrole — **absent partout alors que c'est LE driver cuivre du bulletin**), inventaires LME/SHFE, DXY trend 20j (absent sur 6 actifs), breadth, Shiller CAPE. Café : météo Minas Gerais (poids 11) et stocks ICE (poids 9) = n/a → le driver récolte n°1 toujours sans canal.

Dilution réelle : **le quanti (TIPS/COT/HY/flux ETF) passe proprement ; la news qualitative survit mal ou s'inverse ; les drivers fondamentaux lourds (PMI, inventaires, DXY) sont des trous noirs à poids 8-12.**

## 3. `bulletin-2026-06-01.md` — verdict tradeable par cellule
Matrice 12×3, score primaire ±1 + pondéré en annotation. Tri spéculateur brut :

**Signal large + tranché (≥3 critères concordants, |score| franc) — tradeable :**
- **S&P 500 LONG 7j/1m (+4.88/+4.42)** : 3 critères tous LONG (HY serré 2.72 → +3.8, flux SPY +0.96, RSI léger frein). Concordant, pas de divergence pm1/pond, vague de fond haussière confirmée par le flux. **La meilleure cellule du run.**
- **Argent LONG 1m (+5.06)** : 6 critères, pond=pm1 (pas de divergence). MAIS dépend à 51% du ratio G/S saturé -1.0 (voir §4). Conviction large en apparence, monobloc en réalité.
- **Cuivre SHORT 7j/1m (-1.91/-3.63)** : tranché mais bâti sur COT saturé (+1.0) contredit par ratio cuivre/or (+0.76 LONG). Voir « mono-critère trompeur ».

**Coin-flips déguisés (|score|<0.5 OU divergence pm1/pond — NE RIEN FAIRE) :**
- **CAC 24h +0.27**, **Or 24h +0.17 (pond SHORT -2.15, divergence ⚠)**, **Cuivre 24h -0.09**, **VIX 1m +0.25 (pond SHORT -0.45, divergence ⚠)**, **Café 24h +0.04**, **EUR/USD 7j +0.12**. Le système « ne sait pas ». Le 24h reste globalement tassé (Argent excepté).

**Contre-sens vs vague réelle (DANGEREUX) :**
- **Pétrole LONG +9.99/+13.75/+10.70** : score le plus fort du run, sur un actif dont le fichier 1 dit « biggest monthly loss in 6 years » / « -20% du pic ». Le moteur est massivement LONG sur une vague baissière. **Inversion persistante du run 31/05, aggravée (score +13 vs +7).**
- **Nasdaq** : 24h LONG +4.25 mais **1m SHORT -1.57** (flip vs veille) → le momentum court haussier (SOX) est mangé par les taux réels à 1m. Cellule qui se retourne dans la fenêtre = pas un trend exploitable, un tiraillement.

Les ⚑ GATE régime extrême sont actifs quasi-partout (drapeau hors score) — bruit visuel, n'aide pas à trancher.

## 4. `decision-log/2026-06-01-0816.jsonl` — anatomie du score
36 cellules, contrib par critère traçable (`contrib_pm1`/`contrib_pond`). Part du critère dominant (% de la somme des |contrib|) :

| Cellule | crit. actifs | dominant | part dom. | lecture |
|---|---|---|---|---|
| Cacao 24/7j/1m | **1** | COT Cocoa | **100%** | mono-critère pur. SHORT propre en apparence, vide. |
| Blé 24h | 4 | Géopol mer Noire | **89%** | quasi-mono. |
| Cuivre 1m | 2 | COT Copper | **79%** | mono-driver de fait. |
| S&P 1m | 3 | HY spread | 74% | concentré mais les 3 vont dans le même sens. |
| EUR/USD 1m | 2 | COT EUR | 72% | mince. |
| Pétrole 24h | 5 | Géopol M-O (triplet) | 63% | dominé par la news inversée. |
| Or 24h | 5 | Tension géopol | 43% | divergence pm1/pond. |
| Argent 1m | 6 | Ratio G/S (saturé -1.0) | 51% | « 6 critères » mais 1 saturé porte la moitié. |
| Nasdaq 7j | 6 | SOX | 27% | **vraie diversité de drivers** — la cellule la plus saine. |

Lectures dures de spéculateur :
- **La conviction CROÎT mécaniquement avec l'horizon** (Cuivre -0.09→-3.63 ; Cacao +0.91→+4.55 ; Argent +1.56→+5.06). Cause = pertinence/échelle qui monte vers 1m, **pas un momentum plus fort**. Le « +5 à 1m » est un artefact de pondération, comme au 31/05. Un gros score long n'est PAS un read de tendance forte.
- **Mono-critère trompeur confirmé** : Cacao (COT seul, 100%), Blé (géopol mer Noire, 89%), Cuivre (COT, 79% — et le 2e critère, ratio cuivre/or, pousse à CONTRE-SENS du dominant). Ces SHORT/LONG « propres » reposent sur 1 donnée. Une révision COT hebdo les retourne.
- **Divergences pm1/pond = signal nul** : Or 24h (pm1 +0.17 / pond -2.15), VIX 1m (pm1 +0.25 / pond -0.45), Café 1m (pm1 -1.42 / pond +0.67). Le moteur se contredit lui-même selon la pondération → aucune conviction.
- **Nasdaq est la seule cellule à diversité réelle** (dominant à 27%, 6 drivers distincts), mais elle paie ça par un retournement intra-fenêtre (LONG 24h → SHORT 1m). Diversifié mais pas directionnel.

## 5. `performance.md` — edge naissant ou bruit ?
**Toujours VIDE de sens statistique, mais les prix d'émission sont enfin réparés** (progrès vs 31/05 où tout était `suivi-interrompu / prix indisponible`).

État : 12/12 cellules en `shadow`, N_eff=1 max, 0/12 éligibles (cible Wilson low > 50% sur N_eff ≥ 15). Premier batch de mesures terminées ce run :
- 4 cellules conclusives : **Or 24h SHORT = VRAI** (-0.627% vs seuil 0.5%), **Pétrole 24h LONG = VRAI** (+2.736% vs 1.0%), **Blé 24h SHORT = FAUX** (+0.885%), **Cuivre 24h SHORT = FAUX** (+0.894%).
- 8 cellules `non-conclusive` (|delta| < seuil — dont CAC/Nasdaq/S&P à +0.000%, prix figé : le contexte-prix indice est branché mais le mouvement intraday n'a pas bougé le curseur).

Lecture spéculateur : **2 VRAI / 2 FAUX sur 4 = pile ou face.** Aucun edge mesurable, c'est attendu au run 1 d'une fenêtre 30-obs. Notable et ironique : la seule cellule conclusive « gagnante » côté momentum est **Pétrole LONG = VRAI** (+2.7% sur 24h) — le marché a monté ce jour-là malgré la vague mensuelle baissière. Un point ne fait pas une tendance : ça ne valide pas le LONG structurel, ça reflète le rebond géopol du jour. **Le mapping score→proba (0.5 + |score|/10) reste déterministe, NON calibré.** On ne sait toujours pas si un +13 vaut mieux qu'un +1.

---

## VERDICT GLOBAL

### Où je mets du cash (long/short avec conviction)
- **S&P 500 LONG 7j/1m (+4.88/+4.42)** : la SEULE cellule où je trade sans réserve. 3 critères concordants (HY serré, flux SPY positifs, RSI non extrême), zéro divergence, vague de fond haussière confirmée par le flux brut (SoftBank, AI capex, software). Position modérée, c'est mince (3 critères) mais ils sont alignés et le quanti est solide.

### Où je mets une petite ligne, sous réserve
- **Cuivre SHORT 7j/1m** : la macro Chine est baissière (PMI stalls) et ça colle. MAIS le score tient à 79% sur le COT saturé, contredit par le ratio cuivre/or. Petite ligne tactique, stop serré — une révision COT la casse.
- **Argent LONG 1m** : 6 critères, mais 51% sur un ratio Gold/Silver saturé à -1.0 (plancher, pas trend). Le driver news (trêve → argent en hausse) existe enfin. Je prends une demi-ligne, conscient que c'est un signal monobloc déguisé en consensus.

### Où je NE touche À RIEN
- **Pétrole LONG +10/+13** : NO. Score le plus fort du run, à CONTRE-SENS de la vague (« pire perte mensuelle en 6 ans »). Le moteur lit la tension géopol comme haussière alors que le marché price la détente. Mettre du cash long ici = se battre contre la tendance que je suis censé suivre. **Si je devais trader le pétrole, ce serait SHORT — l'inverse du signal.** Bug directionnel, pas opportunité.
- **Coin-flips** : CAC 24h (+0.27), Or 24h (+0.17, divergent), Cuivre 24h (-0.09), VIX 1m (+0.25, divergent), Café (+0.04). Rien.
- **Mono-critères trompeurs** : Cacao (COT seul, 100%), Blé (géopol mer Noire, 89%). SHORT/LONG « propres » mais bâtis sur 1 donnée révisable. Pas de cash.
- **Nasdaq** : se retourne dans la fenêtre (LONG 24h → SHORT 1m). Diversifié mais pas directionnel — j'attends qu'il tranche.

### Le système a-t-il un edge exploitable ?
**Pas encore. DILUÉ, partiellement exploitable — note 5,5/10** (matière 9/10, transmission 4,5/10).

Ce qui a progressé depuis le 31/05 :
- **Couverture indices remontée** : Nasdaq passe à 6 critères alimentés (SOX, flux QQQ, spread Russell, sentiment IA), S&P/CAC ont enfin leur flux ETF. La « couverture catastrophique » de 31/05 est partiellement réparée pour les indices. **Réponse à la question posée : OUI, il y a enfin un signal large sur Nasdaq/S&P** — moins sur CAC (3 critères, OAT-Bund et breadth toujours n/a).
- Prix d'émission réparés → premières mesures conclusives (4/12). La boucle de feedback démarre.
- Direction de la news désormais taggée dans events-log (`BRENT:SHORT:high`).

Ce qui N'a PAS bougé (les 2 maladies de fond) :
1. **L'inversion news→triplet×0.42 persiste** : le tag directionnel du fichier 1 n'est pas câblé au scoring. Pétrole toujours LONG sur vague baissière, en pire (+13 vs +7). C'est LE bug qui rend une cellule à fort score non-fiable.
2. **La conviction reste un artefact d'horizon** : les gros scores 1m viennent de la pertinence montante, pas du momentum. Médiane des critères effectifs ~ 3-5/cellule (mieux que les 3 de 31/05, mais Cacao/Blé/Cuivre/Café restent mono- ou bi-driver).

**Conclusion cash-or-not** : sur 36 cellules, **1 trade franc (S&P long), 2 petites lignes sous réserve (Cuivre short / Argent long), 1 piège à fort score à fuir (Pétrole long), le reste = bruit ou mono-critère.** Le système produit ~3 idées exploitables par run sur 12 actifs — assez pour commencer à risquer du capital prudemment sur les indices, pas assez pour lui faire confiance en aggregate. Tant que le bug d'inversion géopol n'est pas corrigé, **tout score élevé porté par un triplet news doit être traité comme suspect, pas comme conviction.**
