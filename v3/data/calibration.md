# Calibration probabiliste — Reliability Diagram

- Généré : 31 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1241
- Proba prédite moyenne : 0.7934
- Taux observé global : 0.5068
- **ECE = 0.2867** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 242 | 0.5470 | 0.5041 | +0.0429 | 0.0084 |
| 2 | [0.60, 0.70] | 215 | 0.6478 | 0.4558 | +0.1920 | 0.0333 |
| 3 | [0.70, 0.80] | 168 | 0.7472 | 0.5119 | +0.2353 | 0.0319 |
| 4 | [0.80, 0.90] | 150 | 0.8461 | 0.5400 | +0.3061 | 0.0370 |
| 5 | [0.90, 1.00] | 466 | 0.9882 | 0.5193 | +0.4689 | 0.1761 |

**ECE total = 0.2867**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
