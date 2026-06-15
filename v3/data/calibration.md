# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-15T07:26:47.877867+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 175
- Proba prédite moyenne : 0.7157
- Taux observé global : 0.4000
- **ECE = 0.3157** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 62 | 0.5384 | 0.4839 | +0.0545 | 0.0193 |
| 2 | [0.60, 0.70] | 32 | 0.6401 | 0.4375 | +0.2026 | 0.0370 |
| 3 | [0.70, 0.80] | 29 | 0.7487 | 0.5862 | +0.1625 | 0.0269 |
| 4 | [0.80, 0.90] | 14 | 0.8694 | 0.3571 | +0.5123 | 0.0410 |
| 5 | [0.90, 1.00] | 38 | 0.9870 | 0.1053 | +0.8817 | 0.1915 |

**ECE total = 0.3157**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
