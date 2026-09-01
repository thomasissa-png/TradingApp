# Calibration probabiliste — Reliability Diagram

- Généré : 1 septembre 2026, 07h27
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1302
- Proba prédite moyenne : 0.7924
- Taux observé global : 0.5177
- **ECE = 0.2746** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 250 | 0.5471 | 0.4960 | +0.0511 | 0.0098 |
| 2 | [0.60, 0.70] | 235 | 0.6474 | 0.4638 | +0.1836 | 0.0331 |
| 3 | [0.70, 0.80] | 174 | 0.7480 | 0.5172 | +0.2308 | 0.0308 |
| 4 | [0.80, 0.90] | 163 | 0.8472 | 0.5644 | +0.2828 | 0.0354 |
| 5 | [0.90, 1.00] | 480 | 0.9886 | 0.5396 | +0.4490 | 0.1655 |

**ECE total = 0.2746**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
