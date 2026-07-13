# Calibration probabiliste — Reliability Diagram

- Généré : 13 juillet 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 204
- Proba prédite moyenne : 0.7878
- Taux observé global : 0.5098
- **ECE = 0.2779** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 44 | 0.5449 | 0.5227 | +0.0222 | 0.0048 |
| 2 | [0.60, 0.70] | 37 | 0.6432 | 0.4324 | +0.2108 | 0.0382 |
| 3 | [0.70, 0.80] | 26 | 0.7473 | 0.7308 | +0.0165 | 0.0021 |
| 4 | [0.80, 0.90] | 17 | 0.8369 | 0.4706 | +0.3663 | 0.0305 |
| 5 | [0.90, 1.00] | 80 | 0.9909 | 0.4750 | +0.5159 | 0.2023 |

**ECE total = 0.2779**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
