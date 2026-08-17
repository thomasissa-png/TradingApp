# Calibration probabiliste — Reliability Diagram

- Généré : 17 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 874
- Proba prédite moyenne : 0.7836
- Taux observé global : 0.4359
- **ECE = 0.3476** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 185 | 0.5464 | 0.4865 | +0.0599 | 0.0127 |
| 2 | [0.60, 0.70] | 157 | 0.6465 | 0.4013 | +0.2452 | 0.0441 |
| 3 | [0.70, 0.80] | 120 | 0.7478 | 0.4750 | +0.2728 | 0.0374 |
| 4 | [0.80, 0.90] | 105 | 0.8454 | 0.4571 | +0.3883 | 0.0466 |
| 5 | [0.90, 1.00] | 307 | 0.9895 | 0.4007 | +0.5888 | 0.2068 |

**ECE total = 0.3476**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
