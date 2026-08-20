# Calibration probabiliste — Reliability Diagram

- Généré : 20 août 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1096
- Proba prédite moyenne : 0.7900
- Taux observé global : 0.4735
- **ECE = 0.3166** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 210 | 0.5454 | 0.5095 | +0.0359 | 0.0069 |
| 2 | [0.60, 0.70] | 196 | 0.6482 | 0.4337 | +0.2145 | 0.0384 |
| 3 | [0.70, 0.80] | 158 | 0.7473 | 0.4873 | +0.2600 | 0.0375 |
| 4 | [0.80, 0.90] | 137 | 0.8450 | 0.4745 | +0.3705 | 0.0463 |
| 5 | [0.90, 1.00] | 395 | 0.9885 | 0.4684 | +0.5201 | 0.1875 |

**ECE total = 0.3166**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
