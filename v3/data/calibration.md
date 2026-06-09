# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-09T07:21:37.531784+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 78
- Proba prédite moyenne : 0.6877
- Taux observé global : 0.5769
- **ECE = 0.1463** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 29 | 0.5385 | 0.5862 | -0.0477 | 0.0177 |
| 2 | [0.60, 0.70] | 16 | 0.6304 | 0.5625 | +0.0679 | 0.0139 |
| 3 | [0.70, 0.80] | 16 | 0.7574 | 0.5000 | +0.2574 | 0.0528 |
| 4 | [0.80, 0.90] | 6 | 0.8754 | 0.6667 | +0.2087 | 0.0161 |
| 5 | [0.90, 1.00] | 11 | 0.9609 | 0.6364 | +0.3245 | 0.0458 |

**ECE total = 0.1463**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
