# Calibration probabiliste — Reliability Diagram

- Généré : 29 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 435
- Proba prédite moyenne : 0.7800
- Taux observé global : 0.4506
- **ECE = 0.3294** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 91 | 0.5512 | 0.5165 | +0.0347 | 0.0073 |
| 2 | [0.60, 0.70] | 92 | 0.6473 | 0.4022 | +0.2451 | 0.0518 |
| 3 | [0.70, 0.80] | 53 | 0.7445 | 0.5472 | +0.1973 | 0.0240 |
| 4 | [0.80, 0.90] | 49 | 0.8513 | 0.3673 | +0.4840 | 0.0545 |
| 5 | [0.90, 1.00] | 150 | 0.9895 | 0.4333 | +0.5562 | 0.1918 |

**ECE total = 0.3294**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
