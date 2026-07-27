# Calibration probabiliste — Reliability Diagram

- Généré : 27 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 367
- Proba prédite moyenne : 0.7912
- Taux observé global : 0.4659
- **ECE = 0.3253** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 72 | 0.5512 | 0.3889 | +0.1623 | 0.0319 |
| 2 | [0.60, 0.70] | 74 | 0.6457 | 0.4595 | +0.1862 | 0.0375 |
| 3 | [0.70, 0.80] | 43 | 0.7431 | 0.6744 | +0.0687 | 0.0081 |
| 4 | [0.80, 0.90] | 38 | 0.8463 | 0.4211 | +0.4252 | 0.0440 |
| 5 | [0.90, 1.00] | 140 | 0.9913 | 0.4571 | +0.5342 | 0.2038 |

**ECE total = 0.3253**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
