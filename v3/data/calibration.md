# Calibration probabiliste — Reliability Diagram

- Généré : 21 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1125
- Proba prédite moyenne : 0.7933
- Taux observé global : 0.4853
- **ECE = 0.3079** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 215 | 0.5462 | 0.4837 | +0.0625 | 0.0119 |
| 2 | [0.60, 0.70] | 197 | 0.6477 | 0.4518 | +0.1959 | 0.0343 |
| 3 | [0.70, 0.80] | 153 | 0.7479 | 0.5033 | +0.2446 | 0.0333 |
| 4 | [0.80, 0.90] | 144 | 0.8450 | 0.4931 | +0.3519 | 0.0450 |
| 5 | [0.90, 1.00] | 416 | 0.9887 | 0.4928 | +0.4959 | 0.1834 |

**ECE total = 0.3079**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
