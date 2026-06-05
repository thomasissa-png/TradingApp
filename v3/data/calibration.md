# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-05T07:05:58.416135+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 99
- Proba prédite moyenne : 0.6337
- Taux observé global : 0.5253
- **ECE = 0.2715** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 47 | 0.5356 | 0.7021 | -0.1665 | 0.0791 |
| 2 | [0.60, 0.70] | 32 | 0.6437 | 0.4062 | +0.2375 | 0.0767 |
| 3 | [0.70, 0.80] | 11 | 0.7565 | 0.1818 | +0.5747 | 0.0639 |
| 4 | [0.80, 0.90] | 2 | 0.8790 | 1.0000 | -0.1210 | 0.0024 |
| 5 | [0.90, 1.00] | 7 | 0.9842 | 0.2857 | +0.6985 | 0.0494 |

**ECE total = 0.2715**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
