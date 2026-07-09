# Calibration probabiliste — Reliability Diagram

- Généré : 9 juillet 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 155
- Proba prédite moyenne : 0.8046
- Taux observé global : 0.5161
- **ECE = 0.2885** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 29 | 0.5428 | 0.4828 | +0.0600 | 0.0112 |
| 2 | [0.60, 0.70] | 28 | 0.6486 | 0.5357 | +0.1129 | 0.0204 |
| 3 | [0.70, 0.80] | 16 | 0.7497 | 0.7500 | -0.0003 | 0.0000 |
| 4 | [0.80, 0.90] | 16 | 0.8330 | 0.5000 | +0.3330 | 0.0344 |
| 5 | [0.90, 1.00] | 66 | 0.9922 | 0.4697 | +0.5225 | 0.2225 |

**ECE total = 0.2885**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
