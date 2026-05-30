# Audit rigueur de mesure — TradingApp v3
> Angle : validité statistique / décision data-driven. Date : 2026-05-30.

## 1. Taille d'échantillon et indépendance

**Fenêtre KPI : 30 conclusions terminées par cellule (hors non-conclusives et suivi-interrompu).**

À 1 bulletin/jour, les 30 observations couvrent ~30 jours calendaires. Or l'horizon 1m utilise un delta de prix sur 30 j : les conclusions émises en J et J+1 sont mesurées sur des fenêtres de prix qui se chevauchent à 96 %. Cela crée une **autocorrélation forte** — les 30 observations ne sont pas i.i.d. La variance estimée du taux de réussite est sous-estimée ; l'intervalle de confiance réel est bien plus large que ce que laisse penser N=30.

Pour l'horizon 7j, le chevauchement est de ~86 % entre deux jours consécutifs. Seul l'horizon 24h produit des observations quasi-indépendantes (chevauchement nul si mesuré à date fixe).

**Conséquence pratique** : un taux de 70 % calculé sur 30 observations chevauchantes pour 1m ne suffit pas à établir la significativité statistique. Avec chevauchement, la puissance effective est équivalente à ~4-6 observations indépendantes pour 1m.

## 2. Multiple testing sur 36 cellules

Le dispositif évalue 36 cellules (12 actifs × 3 horizons) contre le même seuil de 70 %. Avec α=0,05 et 36 tests indépendants, l'espérance de faux positifs est **~1,8 cellules** si le système est sans valeur prédictive. Avec des cellules corrélées entre actifs (les marchés bougent ensemble), ce chiffre est moindre mais le risque de data dredging demeure réel.

Aucune correction de Bonferroni ni FDR (Benjamini-Hochberg) n'est implémentée. La bascule vers le mode actif sur la base du taux brut par cellule expose à valider des cellules gagnantes **par chance**.

## 3. Validité de l'A/B ±1 vs pondéré

Le design A/B compare deux règles de décision sur les **mêmes observations** (même prix d'émission, même prix de sortie). Ce n'est pas un vrai test contrôlé (pas d'allocation aléatoire de l'utilisateur à un groupe). C'est une **comparaison rétrospective de règles**.

Ce design est valide pour sélectionner la règle dominante ex-post, **mais pas pour inférer que la règle pondérée "bat" la baseline en production** : les deux règles partagent le même bruit de marché ; les différences de taux peuvent s'inverser sur un nouveau segment temporel. Le risque est de sur-optimiser les facteurs materiality/reliability sur la période de shadow, puis de voir la performance régresser à la moyenne en mode actif.

Point positif : le skip propre (bulletins sans annotation pondérée exclus du dénominateur pondéré) est correctement implémenté, ce qui évite un biais de sélection temporelle dans le calcul du taux pondéré.

## 4. Calibration de la probabilité et validité du Brier

La proba est dérivée de façon déterministe : `proba = 0.5 + clip(|score| / 10, 0, 0.5)`. Elle n'a jamais été calibrée empiriquement. Si le score moyen en shadow est de ±3, la proba affichée sera 0.80 — mais si le taux réel est 0.60, la proba est **systématiquement sur-confiante** et le Brier score pénalisera la sur-confiance sans que cela soit visible dans le taux de réussite.

Le Brier score peut donc être dégradé non pas parce que les conclusions sont fausses, mais parce que le mapping score→proba est mal étalonné. Sans courbe de calibration (reliability diagram), on ne peut pas distinguer les deux causes.

De plus, les non-conclusives (mouvement < seuil) sont exclues du Brier, ce qui est cohérent, mais réduit encore la taille d'échantillon effective. Si le seuil de réussite est trop élevé (beaucoup de non-conclusives), le Brier est calculé sur trop peu de points pour être significatif.

## 5. Ce que le decision-log capture — et ce qu'il manque

**Bien capturé** : score ±1 et pondéré, toutes les contributions critère × horizon, materiality, reliability, source_track, diverge. Suffisant pour reconstituer le calcul et attribuer un flip à un critère.

**Manquant pour un post-mortem honnête** :
- L'outcome (VRAI/FAUSSE) n'est PAS dans le decision-log. Il est dans `performance.md` (régénéré) mais le lien entre une ligne JSONL et son outcome n'est pas formalisé (pas de `bulletin_date + actif + horizon` comme clé de jointure explicite dans le rendu de performance).
- Le prix d'émission réellement utilisé pour la mesure n'est pas dupliqué dans le log (il est dans `prix-emission/YYYY-MM-DD.json`, séparé). Un fichier de prix manquant rend le post-mortem impossible pour ce jour.
- Les critères en `n/a` ce jour-là ne sont pas logués (exclure gates et n/a du JSONL, lignes 578-579). On ne peut pas reconstruire quels critères étaient muets et leur impact théorique.

## 6. Métriques et garde-fous manquants

- **Intervalle de confiance sur le taux** : afficher 70,0 % sans IC à 95 % est trompeur. Avec N=30 et chevauchement, l'IC réel peut englober 50 %.
- **Taux de non-conclusives** : si > 40 % des conclusions sont non-conclusives, le taux de réussite est calculé sur < 18 observations — ce cas n'est pas alerté.
- **Correction multiple testing** : aucune. Implémenter au minimum un seuil ajusté (≈ 82-83 % par cellule pour Bonferroni sur 36 tests à α=0,05) ou adopter un p-value global avant bascule.
- **Courbe de calibration** : tracer proba prédite vs taux observé par décile de score, pour valider ou recalibrer le mapping score→proba.
- **Kill criterion formalisé** : le README mentionne "Brier > X à J+60" à définir ; sans valeur seuil fixée avant le shadow, le kill criterion peut être rétroactivement ajusté (hypothèse post-hoc).
- **Stabilité temporelle** : pas de test de rupture (Chow test ou simple comparaison de taux semaine 1-4 vs semaine 5-8) pour détecter une dérive du système en cours de shadow.
