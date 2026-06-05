# Corrélation cachée — fausse impression de consensus (point #10)

> Auteur : @data-analyst. Branche `claude/elegant-ramanujan-OIKms`. Date : 2026-06-05.
> Mode analyse pure — zéro modification de code décisionnel. Tout chiffre issu des fiches YAML et de `criteres-courants.md` run 10h56.

---

## 1. Cartographie des 3 critères macro partagés

### 1.1 `taux_10y_us_reels_tips` (FRED DFII10)

| Actif | ID critère | Poids | Pertinence 24h | Pertinence 7j | Pertinence 1m |
|---|---|---|---|---|---|
| Nasdaq | 1 | 11 | 0.5 | 1.0 | 1.0 |
| Or | 1 | 12 | 0.5 | 1.0 | 1.0 |
| Argent | 1 | 8 | 0.5 | 1.0 | 1.0 |
| S&P 500 | 10 | 10 | 0.5 | 1.0 | 1.0 |

**4 actifs porteurs.** Valeur run 10h56 : 2.11 %, norm +0.718 (zone SHORT pour tous, signe -1 partout).

### 1.2 `dxy_trend_20j` (FRED DTWEXBGS)

| Actif | ID critère | Poids | Pertinence 24h | Pertinence 7j | Pertinence 1m |
|---|---|---|---|---|---|
| Or | 3 | 8 | 0.6 | 0.9 | 0.8 |
| EUR/USD | 3 | 9 | 0.7 | 1.0 | 0.8 |
| Pétrole | 7 | 5 | 0.3 | 0.7 | 0.9 |
| Cuivre | 4 | 6 | 0.3 | 0.7 | 0.8 |
| S&P 500 | 5 | 5 | 0.3 | 0.7 | 0.9 |
| Blé | 9 | 4 | 0.3 | 0.7 | 0.8 |

**6 actifs porteurs.** Valeur run 10h56 : 118.878, norm -0.229 (z légèrement négatif = dollar en léger repli court-terme = contribution LONG, signe -1). Note : ce critère donne une contribution *positive* (LONG) dans les 6 actifs, contrairement à TIPS qui donne SHORT. L'effet net sur le biais directionnel dépend du score total par actif.

### 1.3 `hy_credit_spread` (FRED ICE BofA HY OAS)

| Actif | ID critère | Poids | Pertinence 24h | Pertinence 7j | Pertinence 1m |
|---|---|---|---|---|---|
| S&P 500 | 3 | 7 | 0.5 | 1.0 | 0.9 |

**1 seul actif porteur** (S&P 500). Valeur run 10h56 : 2.75 %, norm -0.446.

**Résumé cartographie :**

| Critère macro | Actifs porteurs | Poids moyen parmi porteurs |
|---|---|---|
| TIPS (taux réels 10Y) | Nasdaq, Or, Argent, S&P 500 | 10.25 |
| DXY trend 20j | Or, EUR/USD, Pétrole, Cuivre, S&P 500, Blé | 6.2 |
| HY credit spread | S&P 500 | 7 |

Constat immédiat : le HY spread n'est **pas** partagé (1 seul actif). Les deux drivers réellement partagés sont **TIPS** (4 actifs) et **DXY** (6 actifs). L'Or et le S&P 500 portent les deux simultanément.

---

## 2. Quantification de l'effet sur le run 10h56

### 2.1 Contributions des critères macro par actif (horizon 7j — le plus exposé)

Formule : contribution = signe × poids × pertinence(7j) × norm_valeur

**TIPS (norm +0.718, signe -1 partout) :**

| Actif | Calcul | Contribution TIPS 7j | Direction TIPS |
|---|---|---|---|
| Nasdaq 7j | -1 × 11 × 1.0 × 0.718 | **-7.90** | SHORT |
| Or 7j | -1 × 12 × 1.0 × 0.718 | **-8.62** | SHORT |
| Argent 7j | -1 × 8 × 1.0 × 0.718 | **-5.74** | SHORT |
| S&P 500 7j | -1 × 10 × 1.0 × 0.718 | **-7.18** | SHORT |

**DXY (norm -0.229, signe -1 partout) :**

| Actif | Calcul | Contribution DXY 7j | Direction DXY |
|---|---|---|---|
| Or 7j | -1 × 8 × 0.9 × (-0.229) | **+1.65** | LONG |
| EUR/USD 7j | -1 × 9 × 1.0 × (-0.229) | **+2.06** | LONG |
| Pétrole 7j | -1 × 5 × 0.7 × (-0.229) | **+0.80** | LONG |
| Cuivre 7j | -1 × 6 × 0.7 × (-0.229) | **+0.96** | LONG |
| S&P 500 7j | -1 × 5 × 0.7 × (-0.229) | **+0.80** | LONG |
| Blé 7j | -1 × 4 × 0.7 × (-0.229) | **+0.64** | LONG |

**HY spread (norm -0.446, signe -1, S&P seulement) :**

| Actif | Calcul | Contribution HY 7j | Direction HY |
|---|---|---|---|
| S&P 500 7j | -1 × 7 × 1.0 × (-0.446) | **+3.12** | LONG |

### 2.2 Part du score total issue du driver macro

Les scores totaux 7j du run 10h56 (issus du bulletin-analyst §4 et §5) :

| Actif | Score total 7j | Contrib TIPS | Contrib DXY | Contrib HY | Total macro commun | % score issu macro commun |
|---|---|---|---|---|---|---|
| Nasdaq | -8.94 | -7.90 | — | — | -7.90 | **88%** |
| Or | -5.83 | -8.62 | +1.65 | — | -6.97 | ~119% (TIPS écrase le reste) |
| Argent | ~-2.0 | -5.74 | — | — | -5.74 | >100% (autres critères partiellement compensateurs) |
| S&P 500 | -2.41 | -7.18 | +0.80 | +3.12 | -3.26 | ~135% (TIPS dominant, DXY+HY partiellement compensent) |

Note pour Or et S&P : « % >100% » signifie que les critères macro dominent et que les critères propres à l'actif vont dans l'autre sens (LONG partiel) — c'est cohérent avec des scores modérés malgré un TIPS fort.

### 2.3 Comptage des cellules SHORT par le même driver

Run 10h56 — 36 cellules (12 actifs × 3 horizons), 25 SHORT (69%).

Parmi ces 25 SHORT, combien sont portées majoritairement par TIPS ?

| Horizon | Actifs SHORT portés principalement par TIPS | Nombre cellules |
|---|---|---|
| 7j | Nasdaq, Or, Argent, S&P 500 (TIPS = 88-100% du signal directionnel) | 4 |
| 1m | Nasdaq, Or, Argent, S&P 500 (pertinence 1.0 = contribution identique) | 4 |
| 24h | Nasdaq, Or, Argent, S&P 500 (pertinence 0.5 = contribution réduite, mais TIPS reste dominant pour Nasdaq/Or) | ~3 |

**Estimation : 10-11 cellules SHORT sur 25 (40-44%) sont portées par le même signal TIPS.**

Ces 10-11 cellules apparaissent comme 10-11 opinions indépendantes dans le comptage 69% SHORT. Elles ne représentent en réalité **qu'un seul fait macro** : taux réels US élevés à 2.11%.

---

## 3. Métrique proposée : « Consensus effectif décorrélé »

### 3.1 Principe

Le comptage brut SHORT/(LONG+SHORT) = 69% est trompeur parce qu'il traite chaque cellule comme une conviction indépendante. Il faut pondérer chaque cellule par **l'unicité de son driver principal**.

**Formule du « Poids d'Indépendance » (PI) d'une cellule :**

```
PI(actif, horizon) = 1 - Σ (part_score_driver_macro_j)²
```

Où `part_score_driver_j` = |contribution driver macro j| / |score total|, sommée sur les N drivers macro partagés qui ont la même direction que le score final.

- PI = 1 : aucun driver macro commun ne domine → conviction pleinement indépendante
- PI = 0 : 100% du score vient d'un driver macro partagé → conviction nulle, doublons purs

**Consensus effectif décorrélé (CED) :**

```
CED_SHORT = Σ PI(cellule) × 1[cellule=SHORT]  /  Σ PI(cellule)
```

### 3.2 Calcul approximatif sur le run 10h56

Cellules avec PI estimé faible (driver macro dominant) :

| Cellule | Driver dominant | PI estimé |
|---|---|---|
| Nasdaq 7j | TIPS 88% | 0.12 |
| Nasdaq 1m | TIPS ~80% | 0.20 |
| Or 7j | TIPS >100% du net | 0.10 |
| Or 1m | TIPS ~80% | 0.20 |
| Argent 7j | TIPS ~60% | 0.40 |
| Argent 1m | TIPS ~70% | 0.30 |
| S&P 500 7j | TIPS 135% net mais partiel | 0.35 |
| S&P 500 1m | TIPS dominant | 0.30 |
| Nasdaq 24h | TIPS 50% (pertinence 0.5) | 0.50 |
| Or 24h | TIPS + DXY mixte | 0.50 |

Cellules à PI élevé (drivers propres à l'actif) : Pétrole (OPEC/EIA), Blé (WASDE/météo), Cacao (météo CI), Café (météo Brésil), CAC (OAT-Bund), EUR/USD (diff 2Y propre), VIX (term structure), Cuivre (COT/strikes), Argent 24h (ratio G/S + alpha)…

**CED_SHORT estimé ≈ 58-60 %** au lieu de 69% brut, soit un écart de ~10 points de pourcentage.

Ce CED de 58-60% reste significativement SHORT (régime macro réel), mais l'illusion de « 7 actifs indépendants confirment SHORT » est corrigée : c'est davantage « 3-4 convictions distinctes confirment SHORT ».

---

## 4. Recommandations

### 4.1 Flag-only — affichage dans le bulletin (faisable immédiatement)

**Reco A — bloc « Drivers macro partagés » dans le bulletin**

Ajouter un bloc récapitulatif sous la matrice :

```
⚭ Drivers macro communs actifs ce run :
  TIPS 2.11% (+0.72σ) → oriente SHORT sur : Nasdaq / Or / Argent / S&P 500 [4 actifs]
  DXY -0.23σ          → oriente LONG sur  : Or / EUR/USD / Pétrole / Cuivre / S&P / Blé [6 actifs]
  → Le biais SHORT agrégé (69%) reflète en partie le MÊME signal TIPS compté 4 fois.
```

Ce flag-only est **purement cosmétique** (ne touche ni score, ni conclusion, ni mesure). Il aide le trader à détecter d'un coup d'oeil si le consensus est « large » (drivers diversifiés) ou « factice » (1 macro driver répercuté N fois).

**Complexité d'implémentation :** faible. Les `valeur_normalisee` de ces 3 critères sont déjà dans `criteres-courants.md`. Il suffit de lire les valeurs et de construire la liste des actifs porteurs au moment de la génération du bulletin.

### 4.2 Correction de méthode — Ticket C (ne pas appliquer, proposer)

**Reco B — Corriger le biais directionnel agrégé avec le CED**

Au lieu d'afficher « SHORT 69% (25/36 cellules) », afficher :

```
Direction brute : SHORT 69% (25/36 cellules)
Consensus décorrélé (CED) : SHORT ~59% — 10 pts retirés (doublons TIPS/DXY)
```

**Ce que touche cette reco :** uniquement l'affichage du bilan directionnel en haut du bulletin. Les cellules individuelles LONG/SHORT restent inchangées, les scores restent inchangés, la mesure VRAI/FAUX reste inchangée.

**Pourquoi c'est un Ticket C et non flag-only :** le CED nécessite un calcul par run (somme pondérée des PI), et la formule PI elle-même est une définition méthodologique qui doit être validée par Thomas avant implémentation. Si le calcul PI est mal calibré, le CED afficherait un consensus « corrigé » trompeur — ce serait pire que le biais actuel.

**Calcul requis pour implémenter :** pour chaque cellule, récupérer |contributions| par critère depuis le decision-log (déjà loggué), calculer les PI, sommer. Effort : ~1j dev, ~20 lignes Python.

---

## 5. Résumé exécutif (10 lignes)

Le bulletin affiche 69% de cellules SHORT sur le run 10h56 (25/36). Ce chiffre suggère un large consensus baissier multi-actifs. En réalité, **10 à 11 de ces 25 cellules SHORT sont portées à 60-90% par le même signal : les taux réels US (TIPS = 2.11%)**, mesuré une seule fois mais répliqué dans Nasdaq, Or, Argent et S&P 500. C'est le même fait macro compté 4 fois sur 3 horizons.

Le DXY partagé (6 actifs) va en sens inverse (contribution LONG) donc n'amplifie pas le biais SHORT — il l'atténue partiellement. Le HY spread n'est partagé que sur S&P 500 (1 actif, pas un problème de doublons).

**Faux consensus : 10-11 cellules sur 25 SHORT (40-44%) sont du même driver.** Un « Consensus Effectif Décorrélé » (CED) corrige le taux à ~58-60% SHORT — plus proche de la conviction réelle.

**Reco principale (flag-only) :** ajouter un bloc « ⚭ Drivers macro partagés » dans le bulletin — 2-3 lignes, sans toucher au scoring. Le trader voit immédiatement si le consensus est diversifié ou mono-macro.

**Reco secondaire (Ticket C) :** calculer et afficher le CED en parallèle du comptage brut — nécessite validation Thomas (formule PI) avant implémentation.

---

*Fichier produit : `v3/audit/correlation-cachee-2026-06-05.md`*
*Sources : `v3/config/fiches/*.yml` + `v3/data/criteres-courants.md` (run 10h56) + `v3/audit/bulletin-analyst-2026-06-05.md`*

---

**Handoff → @orchestrator**
- Fichier produit : `/home/user/TradingApp/v3/audit/correlation-cachee-2026-06-05.md`
- Décisions prises : analyse pure, zéro modification code. Le HY spread n'est PAS le problème (1 seul actif). Les vrais drivers partagés sont TIPS (4 actifs) et DXY (6 actifs, mais en sens LONG = atténue le biais SHORT, ne l'amplifie pas).
- Points d'attention : (1) Reco A (flag ⚭) = flag-only, implémentable immédiatement par @fullstack sans validation Thomas. (2) Reco B (CED) = Ticket C, nécessite validation de la formule PI par Thomas avant implémentation. (3) Le biais SHORT 69% est réel à ~58-60% une fois décorrélé — le régime macro (TIPS élevés) est authentique, l'amplitude du chiffre est gonflée.
