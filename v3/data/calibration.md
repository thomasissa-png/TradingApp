# Calibration probabiliste — Reliability Diagram

- Généré : 11 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 873
- Proba prédite moyenne : 0.7873
- Taux observé global : 0.4399
- **ECE = 0.3475** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 175 | 0.5486 | 0.4514 | +0.0972 | 0.0195 |
| 2 | [0.60, 0.70] | 159 | 0.6485 | 0.4340 | +0.2145 | 0.0391 |
| 3 | [0.70, 0.80] | 118 | 0.7490 | 0.5508 | +0.1982 | 0.0268 |
| 4 | [0.80, 0.90] | 113 | 0.8455 | 0.4602 | +0.3853 | 0.0499 |
| 5 | [0.90, 1.00] | 308 | 0.9878 | 0.3864 | +0.6014 | 0.2122 |

**ECE total = 0.3475**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
