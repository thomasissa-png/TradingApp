# Calibration probabiliste — Reliability Diagram

- Généré : 28 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 409
- Proba prédite moyenne : 0.7778
- Taux observé global : 0.4792
- **ECE = 0.2985** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 89 | 0.5514 | 0.5393 | +0.0121 | 0.0026 |
| 2 | [0.60, 0.70] | 88 | 0.6484 | 0.4318 | +0.2166 | 0.0466 |
| 3 | [0.70, 0.80] | 44 | 0.7421 | 0.6591 | +0.0830 | 0.0089 |
| 4 | [0.80, 0.90] | 48 | 0.8508 | 0.4167 | +0.4341 | 0.0510 |
| 5 | [0.90, 1.00] | 140 | 0.9892 | 0.4357 | +0.5535 | 0.1894 |

**ECE total = 0.2985**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
