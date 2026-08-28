# Calibration probabiliste — Reliability Diagram

- Généré : 28 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1273
- Proba prédite moyenne : 0.7919
- Taux observé global : 0.5185
- **ECE = 0.2734** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 234 | 0.5464 | 0.4915 | +0.0549 | 0.0101 |
| 2 | [0.60, 0.70] | 234 | 0.6484 | 0.4957 | +0.1527 | 0.0281 |
| 3 | [0.70, 0.80] | 183 | 0.7470 | 0.5410 | +0.2060 | 0.0296 |
| 4 | [0.80, 0.90] | 160 | 0.8455 | 0.5625 | +0.2830 | 0.0356 |
| 5 | [0.90, 1.00] | 462 | 0.9880 | 0.5195 | +0.4685 | 0.1700 |

**ECE total = 0.2734**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
