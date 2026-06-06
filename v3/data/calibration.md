# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-06T07:06:52.489566+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 152
- Proba prédite moyenne : 0.6600
- Taux observé global : 0.5395
- **ECE = 0.2035** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 62 | 0.5433 | 0.6452 | -0.1019 | 0.0415 |
| 2 | [0.60, 0.70] | 42 | 0.6413 | 0.5714 | +0.0699 | 0.0193 |
| 3 | [0.70, 0.80] | 25 | 0.7494 | 0.1200 | +0.6294 | 0.1035 |
| 4 | [0.80, 0.90] | 12 | 0.8747 | 0.7500 | +0.1247 | 0.0098 |
| 5 | [0.90, 1.00] | 11 | 0.9512 | 0.5455 | +0.4057 | 0.0294 |

**ECE total = 0.2035**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
