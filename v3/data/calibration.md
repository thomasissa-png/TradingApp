# Calibration probabiliste — Reliability Diagram

- Généré : 10 août 2026, 07h32
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 859
- Proba prédite moyenne : 0.7863
- Taux observé global : 0.4331
- **ECE = 0.3532** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 173 | 0.5493 | 0.4624 | +0.0869 | 0.0175 |
| 2 | [0.60, 0.70] | 158 | 0.6486 | 0.4430 | +0.2056 | 0.0378 |
| 3 | [0.70, 0.80] | 117 | 0.7493 | 0.5214 | +0.2279 | 0.0310 |
| 4 | [0.80, 0.90] | 111 | 0.8462 | 0.4414 | +0.4048 | 0.0523 |
| 5 | [0.90, 1.00] | 300 | 0.9878 | 0.3733 | +0.6145 | 0.2146 |

**ECE total = 0.3532**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
