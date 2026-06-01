# Revue de plan — Horizon weighting & news dominance
**Analyst | 2026-06-01 | Référence : run midi 99023fe**

---

## 1. Diagnostic chiffré (problème posé)

| Cellule | Part news dans score brut | Effet observé |
|---|---|---|
| Or 24h | 43 % | Flip SHORT→LONG, démenti 2× |
| VIX 1m | ~480 % du score quant | Force LONG contre quant SHORT |
| Pétrole | 72–88 % (3 horizons) | Mono-signal IA |

Cause racine : la news injecte ±1 **flat** sur les 3 horizons, pendant que les critères
numériques portent des poids × pertinence déjà réduits sur les horizons courts.
Le déséquilibre est donc **structurel dans les poids relatifs**, pas dans la valeur brute du triplet.

---

## 2. Mécanique actuelle — ce que fait déjà `pertinence`

Le scoring pondéré calcule, pour chaque critère triplet :

```
contribution = direction(±1) × materiality × reliability × poids × pertinence[horizon]
```

La `pertinence` est **déjà un decay par horizon**, défini critère par critère dans les fiches YAML.
Exemples lus dans les fiches :

| Actif | Critère (triplet) | pertinence 24h | pertinence 7j | pertinence 1m |
|---|---|---|---|---|
| Pétrole | geopol_iran | 0.9 | 0.7 | 0.2 |
| Pétrole | opec_politique | 0.4 | 0.9 | 1.0 |
| Or | tension_geopolitique | 0.8 | 0.5 | 0.3 |
| Or | demande_indienne | 0.1 | 0.3 | 0.9 |

Le **`decay_factor` proposé** (24h:1.0, 7j:0.7, 1m:0.3) s'appliquerait **sur toute la famille
news**, en plus de la pertinence. Le score deviendrait :

```
contribution = direction × materiality × reliability × poids × pertinence[h] × decay[h]
```

Pour `geopol_iran` à 1m : `pertinence[1m]=0.2` × `decay[1m]=0.3` = **coefficient effectif 0.06**.
Pour `opec_politique` à 1m : `pertinence[1m]=1.0` × `decay[1m]=0.3` = **coefficient effectif 0.3**.

C'est une double décroissance. Elle crée deux effets négatifs :
1. **Écrasement aveugle** : OPEC politique à 1m était *voulu* à pertinence 1.0 par design
   (un cut annoncé 30j à l'avance est fondamentalement un signal 1m). Le decay ramènerait
   son influence à 30 % de ce qui était calibré.
2. **Perte de lisibilité** : deux curseurs tirent dans le même sens ; la pertinence par critère
   perd son sens si un facteur global vient tout écraser. Le calibrage devient non-traçable.

**Conclusion section 2** : le `decay_factor` global **ferait doublon** avec la pertinence
existante ET sur-corrigerait les triplets légitimement forts à 1m (OPEC, EUDR, mining strikes).

---

## 3. Verdict : a, b ou c ?

**Verdict : (a) + (c) combinés. Rejeter (b) seul.**

### Pourquoi rejeter (b) seul — decay_factor global

Démontré en §2 : doublon + sur-correction des critères 1m légitimes. Un paramètre global
sur une architecture conçue critère-par-critère est une régression de design.

### Pourquoi (a) seul est insuffisant

Le bug Or-24h vient d'une `pertinence[24h]=0.8` sur `tension_geopolitique` **trop haute**
face à des critères numériques qui portent de faibles poids à 24h (TIPS pertinence 0.5,
COT 0.2, flux ETF 0.4). Régler la pertinence corrige le ratio. Mais cela ne protège pas
contre le cas pathologique où le quant est faible **en valeur absolue** (score quant ≈ 0,
news = ±1 → flip automatique). Le réglage (a) réduit la fréquence du problème, il ne
l'annule pas structurellement.

### Pourquoi (a) + (c) est la bonne combinaison

- **(a)** : recalibre les pertinences sur les cas documentés (Or 24h, Pétrole horizons courts).
  Intervention ciblée, traçable, réversible.
- **(c) cap anti-inversion** : garde-fou structurel indépendant des valeurs numériques.
  Si `score_quant` et `direction_news` sont opposés en signe, la news est plafonnée à
  `abs(score_quant) × alpha` (voir §4 pour valeur de α). Elle ne peut pas renverser le signe.

Cette combinaison est **additive sans doublon** : (a) règle les poids normaux,
(c) protège les cas limites indépendamment des poids.

**Formulation du cap (c) recommandée :**
```
Si signe(contribution_news_totale) ≠ signe(score_quant) :
    contribution_news_totale = min(abs(contribution_news_totale), abs(score_quant) × 0.8)
    × signe(contribution_news_totale)
```
α = 0.8 : la news peut peser jusqu'à 80 % du score quant en opposition, mais pas l'inverser.
Choix de 0.8 plutôt que 1.0 pour éviter l'égalité parfaite qui produirait un score nul → SHORT
par défaut (règle du seuil >0).

---

## 4. Valeurs de pertinence recommandées — réglages exacts (a)

Principe de calibrage : la contribution news sur un horizon ne doit pas dépasser
**30 % du score quant maximal théorique** sur ce même horizon, hors événement extrême.
Calcul : `poids_news × pertinence[h]` doit rester ≤ 0.3 × `somme(poids_num × pertinence_max[h])`.

### Or — `tension_geopolitique` (id 6, poids 5)

Somme poids numériques Or = 12+9+8+6+5+3+3 = 46. Score quant max 24h (pertinences actuelles) :
TIPS(12×0.5) + DXY(8×0.6) + flux_ETF(5×0.4) + VIX(3×0.7) = 6+4.8+2+2.1 = **14.9 pts**.
Plafond 30 % → news max 24h = 4.5 pts. Avec poids 5 → `pertinence[24h]` max = 4.5/5 = **0.90**.

Valeur actuelle 0.8 → la news peut contribuer 4.0 pts sur 14.9 = 27 %. Techniquement dans
les clous, MAIS sur un run où les critères numériques sont partiellement n/a (WGC mensuel
absent, COT vendredi seul → score quant réel ~6-8 pts), la news représente 50-67 %.
Le problème est donc la **fragilité aux données manquantes**, pas un mauvais poids nominal.

**Recommandation Or `tension_geopolitique` :**

| Horizon | Actuel | Recommandé | Justification |
|---|---|---|---|
| 24h | 0.8 | **0.5** | Géopolitique n'est pas prédictif Or à 24h (réaction spot déjà absorbée) |
| 7j | 0.5 | **0.4** | Léger ajustement, valeur actuelle déjà prudente |
| 1m | 0.3 | **0.3** | Inchangé, correct |

### Pétrole — `tension_geopol_moyen_orient` (id 3, poids 7)

| Horizon | Actuel | Recommandé | Justification |
|---|---|---|---|
| 24h | 0.9 | **0.6** | Géopolitique à 24h est principalement du bruit vs EIA/API |
| 7j | 0.7 | **0.6** | Léger recul, EIA (poids 10) doit dominer |
| 1m | 0.2 | **0.2** | Inchangé, cohérent avec la logique fondamentale |

### Pétrole — `opec_production_policy` (id 5, poids 6)

| Horizon | Actuel | Recommandé | Justification |
|---|---|---|---|
| 24h | 0.4 | **0.3** | Annonce OPEC : impact immédiat mais incertain, COT et EIA valident |
| 7j | 0.9 | **0.8** | Légèrement réduit — signal fort mais pas monopolistique |
| 1m | 1.0 | **1.0** | Inchangé — décision OPEC structure le mois, légitimement à 1.0 |

### VIX — `tension_geopolitique_active` (à vérifier dans fiche VIX)

[HYPOTHÈSE : pertinence actuelle non lue — basé sur la logique de la fiche Or et le symptôme 480 %]
La contribution news de 480 % du score quant à 1m signifie que le score quant VIX 1m est
quasi-nul (VIX mean-reverting à 1m, critères numériques pertinence ≈ 0.1-0.2) pendant
que la news garde une pertinence élevée. Recommandation :

| Horizon | Recommandé | Justification |
|---|---|---|
| 24h | 0.8 | VIX réagit fort aux chocs immédiats — maintien |
| 7j | 0.5 | Réduction vs ce qui semble être ~0.7-0.8 actuel |
| **1m** | **0.1** | VIX est mean-reverting à 1m, géopolitique ne structure pas le niveau mensuel |

⚠️ Vérifier la valeur actuelle dans `v3/config/fiches/vix.yml` avant d'appliquer.

---

## 5. Testabilité shadow

### Ce qui est mesurable immédiatement (sans données historiques)

**Test de sanité structurel** (peut s'exécuter dès demain) :
Pour chaque cellule, calculer et logguer dans le `decision-log` :
```
ratio_news = abs(contribution_news_totale) / (abs(score_quant) + ε)
```
Seuil d'alerte : `ratio_news > 0.5` sur n'importe quelle cellule → drapeau dans le bulletin.
Ce ratio n'existe pas aujourd'hui dans les logs — l'ajouter est une ligne de code.

### Shadow comparatif (30 cycles ~10 jours de run 3×/jour)

Faire tourner en parallèle :
- **Branche A** : pertinences actuelles, sans cap
- **Branche B** : pertinences réglées (§4) + cap α=0.8

Métriques à comparer :
1. Distribution de `ratio_news` par cellule : la branche B doit réduire la variance
2. Taux de flip (signe B ≠ signe A) : attendu 5-15 % des cellules — si >25 % → sur-correction
3. Sur les cellules où B ≠ A, comparer avec réalité prix à J+1, J+7, J+30

### Risque de sur-correction (quantifié)

Le plus grand risque est sur OPEC 1m (pertinence 1.0 maintenu, légitime) et les triplets
commodités agricoles à 1m (EUDR cacao, mining strikes cuivre/argent). Ces critères sont
conçus pour être dominants à 1m — ils ne doivent PAS être écrasés. Le cap (c) seul
les protège si le quant est fort dans le même sens ; il les neutralise si le quant
est faible — ce qui est précisément le bon comportement (pas de signal fort sur signal quant faible).

---

## 6. Conclusion opérationnelle

| Décision | Action | Priorité |
|---|---|---|
| **Rejeter Réglage 1** (decay_factor global) | Ne pas implémenter | Immédiat |
| **Appliquer Réglage (a)** : recalibrer 4 pertinences | Éditer 2 fiches YAML (or.yml, petrole.yml) + vix.yml après vérification | Sprint 1 |
| **Appliquer Réglage (c)** : cap anti-inversion | Ajouter ~10 lignes dans le moteur de scoring | Sprint 1 |
| **Ajouter `ratio_news` dans decision-log** | Observabilité sans coût — logguer dès maintenant | Immédiat |

**Ordre d'implémentation** : (1) logguer `ratio_news` → (2) recalibrer les pertinences →
(3) ajouter le cap → (4) lancer 30 cycles shadow avant d'activer le score pondéré en production.

**Impact attendu sur le taux de réussite** : indéterminable sans backtest (données historiques
insuffisantes), mais le ratio signal/bruit par cellule sera mécaniquement plus stable.
L'objectif n'est pas d'augmenter le taux de réussite brut — c'est de réduire la variance
due à une source unique non vérifiée. Un score stable et modeste est plus exploitable
pour du trend-following qu'un score volatile et fort.

---
*Revue produite sans code. Implémenter via @fullstack après validation Thomas.*
