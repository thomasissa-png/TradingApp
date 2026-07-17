# Calibration probabiliste — Reliability Diagram

- Généré : 17 juillet 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 270
- Proba prédite moyenne : 0.7903
- Taux observé global : 0.5407
- **ECE = 0.2496** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 55 | 0.5506 | 0.5455 | +0.0051 | 0.0011 |
| 2 | [0.60, 0.70] | 53 | 0.6474 | 0.5849 | +0.0625 | 0.0123 |
| 3 | [0.70, 0.80] | 31 | 0.7427 | 0.6774 | +0.0653 | 0.0075 |
| 4 | [0.80, 0.90] | 28 | 0.8459 | 0.4286 | +0.4173 | 0.0433 |
| 5 | [0.90, 1.00] | 103 | 0.9909 | 0.5049 | +0.4860 | 0.1854 |

**ECE total = 0.2496**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
