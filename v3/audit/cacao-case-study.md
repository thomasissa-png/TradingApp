# Cacao Case Study — Lot F · Audit Cowork 10/06/2026
**Auteur** : @data-analyst  
**Date** : 2026-06-10  
**Statut** : Analyse pure — AUCUN code/YAML modifié

---

## Résumé exécutif

La fiche cacao a conclu **LONG 11 jours de suite** (du 29/05 au 10/06) dans un marché structurellement baissier, avec un hit rate live de **1/6 sur les 24h notées** (1 VRAI, 4 FAUSSES, 1 non-conclusive). Pendant la même période, les **news cacao** produisaient des signaux SHORT à **68-80%**.

Cause racine identifiée : le **double comptage COT** (critères `hf_positioning_flux_options` poids 7 + `cftc_cot_cocoa` poids 6, tous deux alimentés par la même valeur brute CFTC) verrouille un signal LONG spéculatif suffisamment fort pour **annuler systématiquement les news SHORT** et les rares critères fondamentaux disponibles. Le Lot A (suppression de `cftc_cot_cocoa`) corrige partiellement ce biais, mais ne suffit pas : même après dédup, la fiche manque d'un critère de tendance prix qui aurait signalé le retournement baissier.

**Verdict : Lot A nécessaire mais insuffisant.** Problème de fond identifié. Recommandation fiche v3 documentée en section 4.

---

## 1. Analyse jour par jour — décision-log shadow v1

### Données de référence : convention de lecture

Le système produit 3 runs par jour. Seul le bulletin 7h (ou premier bulletin du jour) est **noté** en mesure (filtre CA-M6b). Les scores ci-dessous sont ceux du run 7h du matin (ou bulletin validé de la journée) sur l'horizon 24h et 7j, qui sont les deux horizons pertinents pour le suivi live.

Le champ `p2_shadow_contrib_exclu` indique la contribution cumulée exclue en mode shadow (la somme de ce que `cftc_cot_cocoa` aurait apportée si le critère avait été retiré — c'est le signal du double comptage).

Le champ `p2_shadow_flip_potential = true` signale que le retrait de `cftc_cot_cocoa` **aurait pu inverser la conclusion** dans une version v2 dédupliquée.

### Tableau jour par jour (horizon 24h, runs 7h)

| Date | Valeur COT brute | hf_positioning contrib 24h | cftc_cot_cocoa contrib 24h | Part doublon / score total | Score total 24h (v1) | News direction | Conclusion v1 | Outcome mesuré |
|---|---|---|---|---|---|---|---|---|
| 29/05 | [données log manquantes — run pré-disponibilité] | — | — | — | 0.72 | SHORT majoritaire | LONG | suivi-interrompu |
| 30/05 | [données log manquantes] | — | — | — | 1.51 | SHORT majoritaire | LONG | suivi-interrompu |
| 31/05 | [données log manquantes] | — | — | — | 0.91 | SHORT majoritaire | LONG | **FAUSSE** (−3.02%) |
| 01/06 | [données log manquantes] | — | — | — | 0.18 | SHORT majoritaire | LONG | **FAUSSE** (−3.02%) |
| 02/06 | [couverture INSUFFISANT — run FRED 429] | — | — | — | 0.00 | — | INSUFFISANT | non-notée |
| **03/06** | **-22 106** | +1.593 | +0.911 | **2.504 / 2.776 = 90%** | 1.736 | SHORT (medium) | **LONG** | **FAUSSE** (−7.39%) |
| **04/06** | **-22 106** | +1.593 | +0.911 | **2.504 / 2.504 = 100%** | 2.504 | absent (ia_faible) | **LONG** | **FAUSSE** (−6.57%) |
| **05/06** | **-22 106** | +1.593 | +0.911 | **2.504 / 2.067 = [>100%]** | 1.464 | SHORT (medium) | **LONG** | **FAUSSE** (−4.01%) |
| **06/06** | **-23 189** | +1.623 | +0.928 | **2.551 / 1.823 = 140%** | 1.823 | SHORT (high) | **LONG** | **VRAI** (+1.14%) |
| **08/06** | **-23 189** | +1.623 | +0.928 | **2.551 / 2.114 = 121%** | 2.114 | SHORT (medium) | **LONG** | **VRAI** (+1.18%) |
| **09/06** | **-23 189** | +1.623 | +0.928 | **2.551 / 2.114 = 121%** | 2.114 | SHORT (medium) | **LONG** | non-conclusive (−0.33%) |
| **10/06** | **-23 189** | +1.623 | +0.928 | **2.551 / 2.114 = 121%** | 2.114 | SHORT (medium) | **LONG** | en cours |

**Nota sur ">100%"** : quand les news envoient un signal négatif (news_total = -1.04 sur 05/06), le score total est score_quant + news_total. Le score_quant = 2.504, news = -1.04, total = 1.464. La contribution du doublon (2.551) représente alors 174% du score total — la partie double-comptée est plus grosse que le score final.

### Analyse détaillée des jours avec decision-log complet

#### 03/06/2026 — premier jour avec critères lisibles

**Critères présents** :
- `meteo_ci_ghana_precip_30j` (poids 11, pertinence 0.3) : valeur +0.164, normalisée +0.082 → contrib 24h = **+0.272** (LONG météo = pluies normales, pas de stress)
- `hf_positioning_flux_options` (poids 7, pertinence 0.3) : valeur COT -22 106, normalisée -0.759, signe -1 → contrib = **+1.593** (LONG : spéculateurs nets vendeurs = contrarian)
- `cftc_cot_cocoa` (poids 6, pertinence 0.2) : **même valeur -22 106**, même normalisation -0.759, signe -1 → contrib = **+0.911** (LONG : doublon du critère précédent)
- `grindings_q` (poids 5) : n/a → 0.000
- `eudr` (poids 5, pertinence 0.1) : triplet -1, facteur 0.42 → contrib = **-0.400** (SHORT news)
- `maladies_cabosses` (poids 4, pertinence 0.2) : triplet -1, facteur 0.42 → contrib = **-0.640** (SHORT news)

**Quant total** = +0.272 + 1.593 + 0.911 = **+2.776**  
**News total** = -0.400 + (-0.640) = **-1.040**  
**Score final** = +1.736 → LONG

**Ce que disaient les news** : synthèse DeepSeek = "Majorité de news SHORT (dollar fort, stocks ICE, offre abondante) dominent malgré une news LONG récente (Chine lève interdiction Brésil)". Conviction = medium. **Les news tiraient SHORT.**

**Part du double comptage** : contribution combinée des deux critères COT = 1.593 + 0.911 = **2.504 / score quant 2.776 = 90%** du signal quantitatif provient de la même donnée CFTC, lue deux fois. Sans le doublon, score quant = 0.272 (seule météo) → score total = 0.272 − 1.040 = **-0.768 → SHORT**. La conclusion aurait été inversée.

---

#### 04/06/2026

**Critères présents** :
- `meteo_ci_ghana_precip_30j` : **n/a** ce jour (météo absente — couverture 50%)
- `hf_positioning_flux_options` : COT -22 106 → contrib 24h = **+1.593**
- `cftc_cot_cocoa` : COT -22 106 → contrib 24h = **+0.911** (doublon)
- `grindings_q` : n/a → 0.000
- `eudr` : valeur 0 (ia_synthese_faible, pas de conviction) → **0.000**
- `maladies_cabosses` : valeur 0 (ia_synthese_faible) → **0.000**

**Score total** = 1.593 + 0.911 = **+2.504 → LONG**

**Part du double comptage** : **100% du score total** = les deux critères COT sont les seuls porteurs de la décision. Les news étaient inactives (ia_synthese_faible : "Signal trop dispersé"). La météo était n/a.

**Constat critique** : sur ce run, le signal entier = le double comptage. Sans `cftc_cot_cocoa`, score = +1.593 → toujours LONG (1.593 > 0). **Mais la COT est interprétée à contresens** (voir section 3).

---

#### 05/06/2026

- `hf_positioning_flux_options` : COT -22 106 → contrib 24h = **+1.593**
- `cftc_cot_cocoa` : COT -22 106 → contrib 24h = **+0.911** (doublon)
- `eudr` : triplet -1, facteur 0.42 → **-0.400** (SHORT)
- `maladies_cabosses` : triplet -1, facteur 0.42 → **-0.640** (SHORT)

**Score** = 1.593 + 0.911 - 0.400 - 0.640 = **+1.464 → LONG**

**News ce jour** : synthèse "offre abondante, demande faible, dollar fort" — biais SHORT maintenu, conviction medium. Le prix avait baissé de 2.80% sur 5j (bulletin 09/06).

**Part doublon** : 2.504 / 1.464 = 171% du score final. Sans le doublon : 1.593 − 1.040 = **+0.553 → toujours LONG** (mais très proche du seuil, et le signal météo absent ce jour). **Important** : même sans le doublon, le signal reste positif car hf_positioning seul (1.593) dépasse les news SHORT (-1.040).

---

#### 06/06/2026

Changement de valeur COT : de -22 106 à **-23 189** (spéculateurs encore plus nets vendeurs).

- `hf_positioning_flux_options` : COT -23 189 → contrib 24h = **+1.623**
- `cftc_cot_cocoa` : COT -23 189 → contrib 24h = **+0.928** (doublon)
- `eudr` : facteur 0.70 (conviction = high, freshness 2.21j) → **-0.280** (SHORT)
- `maladies_cabosses` : facteur 0.70 → **-0.448** (SHORT)

**Score** = 1.623 + 0.928 - 0.280 - 0.448 = **+1.823 → LONG**

**Outcome réel** : VRAI (+1.14%) — la seule journée où le marché a effectivement monté légèrement. Coïncidence plutôt que signal juste : la baisse de 4 jours précédents a produit un rebond technique.

---

#### 08/06 et 09/06 — mêmes données figées

La valeur COT reste **-23 189** (les données CFTC ne sont publiées qu'une fois par semaine, le vendredi). Les scores sont identiques depuis le 06/06 : score_pond 24h = **2.114**, score_pond 7j = **5.896**. Les news restent SHORT (freshness 4-5 jours sur event_id d1aea367dde8 — le même event).

Les deux jours VRAI/non-conclusive du 08-09/06 correspondent à une petite hausse technique (+1.18% / -0.33%) dans une tendance toujours baissière — non représentatifs d'un signal valide.

---

### Récapitulatif live (bulletins 7h notés uniquement)

| Jour | Conclusion 24h | Outcome | Mouvement |
|---|---|---|---|
| 31/05 | LONG | FAUSSE | −3.02% |
| 01/06 | LONG | FAUSSE | −3.02% |
| 03/06 | LONG | FAUSSE | −7.39% |
| 04/06 | LONG | FAUSSE | −6.57% |
| 05/06 | LONG | FAUSSE | −4.01% |
| 06/06 | LONG | VRAI | +1.14% |
| 08/06 | LONG | VRAI | +1.18% |
| 09/06 | LONG | non-conclusive | −0.33% |

**Win rate sur 24h notés** : 2 VRAI / 6 notables (7 notés, 2 VRAI, 4 FAUSSES, 1 NC) = **2/6 = 33% sur conclues** — WR tradable 2/(2+4+1) = 29%. Objectif minimal requis : 70%.

---

## 2. Rejeu v2 (sans `cftc_cot_cocoa`) — calcul statique documenté

### Méthode

Le script `v3/scripts/_replay_plan_horizon.py` est dédié au rejeu Or/VIX sur le log `2026-06-01-1337.jsonl` avec modifications de pertinences. **Il ne couvre pas le cas cacao** (aucun paramètre cacao dans `PERTINENCE_NEW`, aucun champ `fiche_key=cacao` dans le log ciblé). Un rejeu via ce script n'est pas possible sans modification du code — ce qui est hors-périmètre Lot F.

**Calcul statique retenu** : pour chaque jour avec données decision-log, on retire la contribution de `cftc_cot_cocoa` (valeur lue directement dans le log) et on recalcule le score.

### Formule

```
score_v2(horizon) = score_v1(horizon) - contrib_cftc_cot_cocoa(horizon)
conclusion_v2 = "LONG" si score_v2 > 0, sinon "SHORT"
```

La contribution de `cftc_cot_cocoa` dépend de l'horizon via la `pertinence` :
- 24h : pertinence = 0.2 → contrib = valeur_normalisee × poids × pertinence × signe = -0.773 × 6 × 0.2 × (-1) = **+0.928** (ou +0.911 pour COT -22106)
- 7j : pertinence = 0.7 → contrib = -0.773 × 6 × 0.7 × (-1) = **+3.247** (ou +3.187 pour -22106)

### Résultats du rejeu statique

#### Horizon 24h

| Date | Score v1 (24h) | Contrib cftc_cot_cocoa retirée | Score v2 (24h) | Conclusion v2 | Concl. v1 | Inversion ? |
|---|---|---|---|---|---|---|
| 03/06 | +1.736 | −0.911 | **+0.825** | LONG | LONG | **NON** |
| 04/06 | +2.504 | −0.911 | **+1.593** | LONG | LONG | **NON** |
| 05/06 | +1.464 | −0.911 | **+0.553** | LONG | LONG | **NON** |
| 06/06 | +1.823 | −0.928 | **+0.895** | LONG | LONG | **NON** |
| 08/06 | +2.114 | −0.928 | **+1.186** | LONG | LONG | **NON** |
| 09/06 | +2.114 | −0.928 | **+1.186** | LONG | LONG | **NON** |
| 10/06 | +2.114 | −0.928 | **+1.186** | LONG | LONG | **NON** |

**Résultat : la suppression de `cftc_cot_cocoa` ne suffit pas à inverser la conclusion 24h sur aucun des jours.**

**Raison** : `hf_positioning_flux_options` (poids 7, pertinence 0.3 sur 24h) porte seul +1.593 à +1.623 de contribution LONG. Les news SHORT ne totalisent que -1.04 sur les jours où elles sont actives. Le signal net reste LONG même après dédup.

#### Horizon 7j

| Date | Score v1 (7j) | Contrib cftc_cot_cocoa retirée | Score v2 (7j) | Conclusion v2 | Concl. v1 | Inversion ? |
|---|---|---|---|---|---|---|
| 03/06 | +4.252 | −3.187 | **+1.065** | LONG | LONG | **NON** |
| 04/06 | +7.436 | −3.187 | **+4.249** | LONG | LONG | **NON** |
| 05/06 | +5.756 | −3.187 | **+2.569** | LONG | LONG | **NON** |
| 06/06 | +4.776 | −3.247 | **+1.529** | LONG | LONG | **NON** |
| 08/06 | +5.896 | −3.247 | **+2.649** | LONG | LONG | **NON** |
| 09/06 | +5.896 | −3.247 | **+2.649** | LONG | LONG | **NON** |
| 10/06 | +5.896 | −3.247 | **+2.649** | LONG | LONG | **NON** |

**Résultat : même constat sur l'horizon 7j.** Le retrait de `cftc_cot_cocoa` réduit le score de 7.4 à 1.0 minimum, mais le signal reste positif. Sur le 7j, le composite `hf_positioning` (pertinence 0.7-0.8, poids 7) produit +4.25 à +4.33, et les news SHORT n'atteignent que -4.00 au maximum.

### Vérification : à quel niveau les news auraient-elles pu renverser v2 ?

Sur 24h avec score v2 = +0.553 (05/06) : il aurait fallu news_total ≤ -0.554 pour inverser. Or news_total = -1.040. **Mais le cap anti-inversion α=0.8 est actif.** Avec le cap :

```
cap_abs = |quant_total| × 0.8 = 0.553 × 0.8 = 0.442
news_total_après_cap = min(|news_total|, cap_abs) × signe = -0.442
score_capé = 0.553 - 0.442 = +0.111 → LONG
```

Le cap anti-inversion protège le signal quant même quand les news sont plus fortes. Ce mécanisme est correct (il évite les faux flips news haute volatilité), mais dans ce cas il aggrave le problème : il empêche les news SHORT valides de renverser un signal quant LONG erroné.

**Conclusion du rejeu v2** : le Lot A ne corrige pas la direction sur ces 7 jours. Le composite `hf_positioning_flux_options` seul est suffisamment fort pour maintenir LONG.

---

## 3. Diagnostic : pourquoi le signal COT est-il interprété à contresens ?

### La logique de contrarian positionnement

Le signe -1 attribué aux critères `hf_positioning_flux_options` et `cftc_cot_cocoa` implique la logique suivante : **quand les grands spéculateurs sont nets VENDEURS (position nette négative = -22 000 à -23 000 contrats), le système conclut LONG**.

Cette logique est celle du **contrarian** : les hedges fonds très vendeurs = le marché est "over-short" → rebond probable. C'est une hypothèse valide en régime de pic de position (short squeeze), mais elle suppose que les positions spéculatives sont à un extrême qui va se corriger.

### Le problème : en marché baissier structurel, le "contrarian" est faux

Entre mai et juin 2026, le cacao est en tendance baissière persistante (-7.39% en une journée le 03/06, -6.57% le 04/06, -4.01% le 05/06). **Dans ce contexte, les spéculateurs nets vendeurs ont raison.** Ils ne sont pas "over-short" à contre-courant — ils sont positionnés dans le sens de la tendance.

La valeur normalisée du COT est calculée via un z-score sur historique. Si les positions nettes à -23 000 contrats sont rares historiquement (z-score = -0.773 = peu fréquent d'être aussi net vendeur), le système les interprète comme un signal de retournement imminent (contrarian). Mais si la tendance baissière est nouvelle ou en phase d'accélération, la position short peut continuer à s'installer bien au-delà des niveaux "historiquement extrêmes".

**En résumé** : le critère de positionnement est un signal contrarian qui fonctionne sur les retournements de position, pas sur les tendances naissantes.

### Ce que disaient les news pendant ce temps

Les synthèses DeepSeek enregistrées dans le decision-log signalent de manière cohérente :
- **03/06** : "dollar fort, stocks ICE, offre abondante — biais SHORT persistant"
- **04/06** : "news trop dispersées pour une conviction" (signal quant pur)
- **05/06** : "offre abondante, demande faible, dollar fort — biais SHORT persistant"
- **06/06** : "demande faible et offre abondante (8 news sur 9) — conviction high"
- **08-09/06** : "8 sur 9 news signalent pression baissière — biais baissier"

Les news capturent la réalité fondamentale (offre mondiale abondante post-cycle météo favorable, demande atone) et étaient directionnellement correctes. Le hit rate news de 68-80% annoncé est cohérent avec les synthèses lues dans le log.

---

## 4. Conclusion tranchée et recommandation v3

### Le Lot A suffit-il à corriger le biais LONG du cacao ?

**NON.** Le Lot A (suppression de `cftc_cot_cocoa`) est nécessaire et doit être appliqué — il élimine un double comptage avéré. Mais le rejeu statique montre que la conclusion reste LONG sur 100% des jours analysés même après dédup. Le problème est plus profond.

### Le problème de fond

**La fiche cacao est dominée par un signal de positionnement contrarian (`hf_positioning_flux_options`, poids 7) sur une structure de couverture de 50%.** Quand les 4 critères fondamentaux de prix/tendance sont n/a (météo, arrivées ports, broyages, spread NY-Londres — les 4 absents correspondent à 27/54 = 50% du poids), le seul signal actif après le doublon est le positionnement spéculatif interprété en contrarian.

Ce critère contrarian :
1. **Interprète systématiquement les positions nets vendeurs comme un signal de rebond.** C'est approprié aux extrêmes ponctuels de marché, pas aux tendances baissières installées.
2. **N'est contrebalancé par aucun critère de tendance prix** : il n'y a pas de momentum prix, pas de tendance 20j, pas de RSI dans la fiche cacao. Pourtant ces critères auraient clairement signalé la direction baissière (le cours avait baissé de 7-8% sur 20j).
3. **Résiste au cap anti-inversion** α=0.8 : même les news SHORT high conviction passent par le cap qui réduit leur influence à 80% du quant total — insuffisant pour renverser un quant positif fort.

**Facteur aggravant** : la couverture à 50% (`⚠️ conf. faible`) active bien le flag visuellement mais n'empêche pas le signal de conclure. Le critère `hf_positioning_flux_options` pèse 7/(7+6+5+5+4) = **7/27 = 26% du signal effectivement disponible** une fois les critères n/a retirés, et 100% du signal LONG actif.

### Recommandation pour fiche cacao v3

[HYPOTHESE : ces recommandations sont architecturales — elles requièrent validation Thomas avant toute implémentation]

**Critère manquant prioritaire : tendance momentum prix cacao**

Exemple de critère à ajouter :
```yaml
- cle: "momentum_prix_20j_cacao"
  nom: "Tendance du cacao (20 jours)"
  source: "Twelve Data (CC1! ou CACAO)"
  type_norm: zscore
  signe: 1
  poids: 9
  pertinences: {24h: 0.8, 7j: 1.0, 1m: 0.8}
  description: "Z-score de la variation de prix sur 20 jours glissants. Signe +1 = 
    une hausse est haussière. Capture la tendance installée, contrebalance le 
    contrarian COT en régime de tendance."
```

**Pourquoi ce critère changerait le résultat** : sur la période étudiée, le cacao avait baissé de -5.95% (20j au 06/06) à -7% (20j au début de la période). Un z-score calculé sur cette variation, avec poids 9 et pertinence 0.8 sur 24h, aurait produit une contribution ~-4 à -6 LONG-négatif (selon le z-score historique de la baisse). Score v2+momentum estimé = 1.186 + (-4) = **-2.8 → SHORT**.

**Ajustement de poids secondaire recommandé** : baisser le poids de `hf_positioning_flux_options` de 7 à 5 une fois le critère momentum ajouté, pour que le positionnement contrarian ne représente plus >25% du signal effectif à couverture faible. [HYPOTHESE : calibration à valider sur données réelles]

**À ne pas modifier dans ce lot** : le signe -1 du critère de positionnement reste valide en théorie — le contrarian COT fonctionne sur les retournements. Il faut simplement le rééquilibrer par un critère de tendance.

**Signalement à @product-manager** : envisager un gate de conviction minimale sur la fiche cacao quand `coverage < 55%` ET `hf_positioning` est le seul critère actif LONG → forcer `⚠️ conf. faible` avec drapeau `◧` visible (le drapeau mono-critère n'est aujourd'hui déclenché qu'au seuil >50% du score, mais sur couverture 50% le critère pèse 26% du signal effectif = sous le seuil).

---

## Annexe — Vérification du script replay

Le script `v3/scripts/_replay_plan_horizon.py` :
- Cible le log `2026-06-01-1337.jsonl` — il n'existe pas de données cacao dans ce log avec données 7h exploitables
- Paramètre `PERTINENCE_NEW` ne contient que des clés `petrole` et `or/vix`
- Aucune modification du script n'a été effectuée (contrainte Lot F)

**Conclusion** : replay via le script non réalisable sur le cas cacao sans modification de code. Calcul statique documenté ci-dessus utilisé à la place (formule transparente, données issues directement du decision-log).

---

*Lot F — Analyse pure, aucun code/YAML modifié. Auteur : @data-analyst. 2026-06-10*
