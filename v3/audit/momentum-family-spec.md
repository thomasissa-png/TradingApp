# Momentum-prix v2 — Critique contradictoire (Le Spéculateur)
**Angle** : first-principles, anti-bullshit. **Date** : 2026-06-10. **Aucun code/YAML modifié.**

---

## Verdict : 6/10 — GO-MODIFIÉ. Plafond de poids : **6** tant que non prouvé en shadow.

---

## Le débat en 5 points

### 1. Edge ou chasing ? — C'est du chasing, et il faut l'assumer.
« Suivre la tendance 20j » est la stratégie la plus crowdée de la planète. Sur des turbos à frais
fixes, un trend-follower retardé achète haut et vend bas avec du slippage structurel. Le backtest
OOS à **46%** dit la vérité : le quant ne **prédit** rien d'exploitable. Ajouter du momentum ne crée
PAS d'edge prédictif — il faut arrêter de se raconter que si. Quand on a conçu le Raptor chez SpaceX,
on n'a pas ajouté une pièce en espérant qu'elle marche : on a mesuré. Ici, mesure = shadow, point.

### 2. Le piège du retournement — réel, et le momentum +1 l'institutionnalise.
Par construction, un trend-follower est TOUJOURS faux au point de cassure : il est encore LONG quand
ça retourne. Le cacao était exactement ça (11 jours LONG dans une chute). Mettre momentum +1 partout
= acheter le biais « late on reversals » sur 11 fiches. Argument POUR : aujourd'hui les fiches sont
faussses AVANT le retournement aussi (LONG fondamental pendant toute la baisse) — donc le momentum
réduit la fenêtre d'erreur de « toute la tendance » à « juste le point de cassure ». Net : moins pire,
pas bon.

### 3. Cohérence vs performance — on corrige la COHÉRENCE, pas la perf. Soyons honnêtes.
C'est le point le plus important. La vraie justification du momentum n'est pas « ça gagne ». C'est :
**une fiche qui se déclare trend-following et qui ne voit pas le prix bouger est incohérente.** On
répare un bug logique (le système concluait LONG en regardant ailleurs), pas on n'invente un alpha.
Donc : on mesure le WIN RATE en shadow, et la barre est « est-ce que ça réduit les FAUSSES aux
retournements », PAS « est-ce que le PnL grimpe ». Ne jamais confondre les deux.

### 4. Poids cacao 9 — NON tant que non prouvé. Le plus gros poids d'une fiche = la plus forte conviction.
Mettre le momentum en poids 9 (le plus lourd de la fiche cacao) = déclarer que la tendance prix est le
signal #1 du cacao. C'est un pari fort sur un critère à edge prédictif nul (cf. point 1). Le case-study
lui-même calibre l'impact sur un seul épisode baissier (~-7% sur 20j → SHORT) : c'est de
l'overfitting sur 7 jours. Tu ne donnes pas le plus gros poids à ce que tu n'as jamais vu performer.

### 5. Verdict brutal.
GO-MODIFIÉ : ajouter le critère est justifié (cohérence trend-following), MAIS plafonné. Tu valides
l'idée que la fiche doit VOIR le prix — pas que le momentum doit DOMINER la fiche.

---

## Plafond de poids recommandé

| Phase | Plafond momentum | Condition |
|---|---|---|
| **Shadow (maintenant)** | **6** | jamais le plus gros poids de la fiche. Doit pouvoir corriger un signal, pas le dicter |
| **Promotion** | jusqu'à 9 | SEULEMENT si shadow ≥ N=30 décisions notées montre une **baisse mesurable des FAUSSES aux retournements** sans dégrader le WR hors-retournement |

**Cacao** : 9 → ramener à **6**. Le `hf_positioning` est déjà passé de 7 à 5 (correctif appliqué dans
la fiche) — bien. Mais on ne remplace pas un sur-poids contrarian par un sur-poids momentum. Deux
poids 5-6 qui s'équilibrent > un poids 9 qui re-verrouille la fiche dans l'autre sens.

---

## La question qui dérange
Si le quant fait 46% OOS, pourquoi ajouter un critère quant de plus AVANT d'avoir prouvé que les NEWS
(68-80% sur le cacao) ne suffisent pas mieux à elles seules ? Le momentum corrige une incohérence
visible — mais le vrai edge mesuré dans ce projet, ce sont les news. Mon avis : plafonne le momentum à
6, et fais le shadow en posant explicitement la question « momentum aide-t-il le WR, ou est-ce que
laisser les news parler aurait suffi ? ». Kill criteria : si à N=30 le momentum n'améliore pas le WR
aux retournements, on le gèle à 3 (rôle de garde-fou anti-incohérence pur), on ne le promeut pas.

---

## Kill criteria (non-négociables)
- N≥30 décisions notées en shadow avant toute promotion de poids.
- Momentum ne devient le plus gros poids d'AUCUNE fiche tant qu'il n'a pas battu sa propre fiche sans lui.
- Si WR shadow avec momentum < WR shadow sans → retour à poids 3 (garde-fou), pas suppression.

---

## Prochaine action
Lundi : geler tous les poids momentum proposés à **6 max** (cacao 9→6), lancer le shadow, et instrumenter
la métrique « FAUSSES aux points de retournement » séparément du WR global. C'est la seule mesure qui
tranche entre « on a corrigé un bug » et « on s'est raconté une histoire ».

---
**Handoff → réponse directe (conseil consultatif)**
- Fichier produit : `/home/user/TradingApp/v3/audit/momentum-family-spec.md`
- Verdict : 6/10, GO-MODIFIÉ, plafond poids 6 en shadow.
- Points d'attention : calibration de poids → à valider par Thomas / @data-analyst ; ne PAS implémenter le poids 9 cacao. Métrique « FAUSSES aux retournements » à ajouter au shadow.
- Rappel : AVIS, pas directive. Thomas décide.
---
