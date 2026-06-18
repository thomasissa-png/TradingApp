# Mesure SHADOW — Rumeur / non-confirmé sur news « structurel » (C8c)

> Reco Newstrader n°2 — détecteur déterministe, **mode SHADOW strict** : 
> le flag `nature_shadow_downgrade` est purement observationnel. **Aucune 
> note, direction, conclusion ou sélection live n'est modifiée.** On mesure 
> d'abord la fréquence et l'impact AVANT toute activation.

- Events-log rejoué : `v3/data/events-log.md`
- Total events : **5638**
- Events « structurel » : **1690**

## LE CHIFFRE

**59.9% des news « structurel » sont en réalité des rumeurs / non-confirmées** (1013 / 1690) et seraient rétrogradées en `verbal` si la règle était activée.

### Pourquoi c'est important (impact coefficient nature)

| Horizon | coef `structurel` (actuel) | coef `verbal` (proposé) | Effet |
|---|---|---|---|
| 24h | 0.8 | 0.3 | poids news fortement réduit |
| **7j** | **1.0** | **0.2** | **-80% de poids** |
| **1m** | **1.0** | **0.1** | **-90% de poids** |

C'est précisément sur **7j et 1m** que le coef structurel « mord » (1.0/1.0). Une rumeur y pèse aujourd'hui à plein régime ; rétrogradée en verbal elle tomberait à 0.2/0.1 → elle s'éteint vite et ne porte plus une fausse tendance durable (cause du flip-flop).

## Répartition des déclencheurs

| Déclencheur | Count |
|---|---|
| reliability seule | 993 |
| reliability+keyword | 17 |
| keyword seul | 3 |

### reliability des structurels rétrogradés

| reliability | structurels rétrogradés | tous structurels |
|---|---|---|
| rumor | 8 | 8 |
| reported | 1002 | 1002 |
| confirmed | 0 | 680 |

### Top marqueurs de rumeur détectés (texte)

| Marqueur | Count |
|---|---|
| `pourrait` | 11 |
| `envisage` | 7 |
| `weighing` | 1 |
| `could` | 1 |

## Exemples réels rétrogradés (échantillon)

| date | actif | titre | reliability | raison |
|---|---|---|---|---|
| 2026-06-18 | BRENT | Hausse des prix du carburant due à la guerre en Iran stimule les vent… | reported | reliability:reported |
| 2026-06-18 | GOLD | Accord de paix avec l'Iran, hausse de l'or malgré les inquiétudes sur… | reported | reliability:reported |
| 2026-06-18 | BRENT | Accord US-Iran sur le pétrole, offre perçue comme plus abondante | reported | reliability:reported |
| 2026-06-18 | SP500 | Prévisions de pénurie d'électricité pour alimenter la demande liée à … | reported | reliability:reported |
| 2026-06-18 | BRENT | Les marchés pétroliers anticipent un excès d'offre avant le retour ef… | reported | reliability:reported |
| 2026-06-18 |  | Afflux d'émetteurs étrangers sur le marché des panda bonds chinois, a… | reported | reliability:reported |
| 2026-06-18 | BRENT | Allies authorize Ukraine to reproduce their air-defense missiles | reported | reliability:reported |
| 2026-06-17 |  | Samsung anticipe des commandes accrues de puces de BYD, Google et AMD… | reported | reliability:reported |

**Cas accord Iran : 195 news structurelles liées à l'Iran rétrogradées** (rumeur/non-confirmé). C'est exactement le pattern du flip-flop Brent SHORT/LONG des 16-17/06 : une news non signée pesait jusqu'à 1m.

## Impact estimé si on activait (rétrogradation réelle)

- 1013 cellules news passeraient de coef 7j=1.0 → 0.2 et 1m=1.0 → 0.1.
- Effet : sur **7j/1m**, ces news cessent de porter une tendance durable. Les news confirmées/signées (structurel légitime) gardent tout leur poids.
- Le flip-flop quotidien (rumeur fraîche qui renverse la conclusion long terme du jour) disparaît mécaniquement : une rumeur en verbal ne suffit plus à renverser le quant à 7j/1m.
- 24h reste réactif (verbal=0.3 ≠ 0) : on ne perd pas la réaction court-terme à une rumeur, on l'empêche juste de durer.

## Recommandation

**Garder en SHADOW au moins 1 à 2 semaines** pour mesurer, sur le decision-log, combien de flips 7j/1m auraient été évités sans nouveau faux négatif (rumeur qui s'est avérée structurelle).

Conditions d'activation proposées :

1. Taux de flip-flop 7j/1m sur news flaggées mesuré et significatif (le flag corrèle bien avec les renversements observés).
2. Taux de faux positifs marqueurs acceptable (revue manuelle d'un échantillon `keyword seul` — vérifier qu'on ne rétrograde pas des structurels légitimes mal phrasés).
3. Activation **graduée** recommandée : commencer par `reliability ∈ {rumor}` seul (signal le plus net), puis étendre à `reported` + marqueurs après validation.

_Généré par `/tmp/mesure_rumeur_structurel.py` — lecture seule, zéro réseau, zéro écriture dans v3/data/._
