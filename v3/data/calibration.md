# Calibration probabiliste — Reliability Diagram

- Généré : 30 juin 2026, 08h09
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 49
- Proba prédite moyenne : 0.7756
- Taux observé global : 0.7551
- **ECE = 0.2546** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 15 | 0.5390 | 0.8667 | -0.3277 | 0.1003 |
| 2 | [0.60, 0.70] | 8 | 0.6353 | 0.6250 | +0.0103 | 0.0017 |
| 3 | [0.70, 0.80] | 1 | 0.7040 | 1.0000 | -0.2960 | 0.0060 |
| 4 | [0.80, 0.90] | 3 | 0.8244 | 1.0000 | -0.1756 | 0.0107 |
| 5 | [0.90, 1.00] | 22 | 0.9844 | 0.6818 | +0.3026 | 0.1359 |

**ECE total = 0.2546**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
