# Calibration probabiliste — Reliability Diagram

- Généré : 25 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1163
- Proba prédite moyenne : 0.7915
- Taux observé global : 0.4841
- **ECE = 0.3075** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 220 | 0.5471 | 0.4909 | +0.0562 | 0.0106 |
| 2 | [0.60, 0.70] | 206 | 0.6473 | 0.4466 | +0.2007 | 0.0356 |
| 3 | [0.70, 0.80] | 168 | 0.7465 | 0.4940 | +0.2525 | 0.0365 |
| 4 | [0.80, 0.90] | 148 | 0.8467 | 0.4662 | +0.3805 | 0.0484 |
| 5 | [0.90, 1.00] | 421 | 0.9884 | 0.5012 | +0.4872 | 0.1764 |

**ECE total = 0.3075**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
