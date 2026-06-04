# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-04T12:07:50.304774+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 55
- Proba prédite moyenne : 0.6630
- Taux observé global : 0.5273
- **ECE = 0.1858** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 27 | 0.5415 | 0.5926 | -0.0511 | 0.0251 |
| 2 | [0.60, 0.70] | 10 | 0.6219 | 0.4000 | +0.2219 | 0.0403 |
| 3 | [0.70, 0.80] | 7 | 0.7581 | 0.4286 | +0.3295 | 0.0419 |
| 4 | [0.80, 0.90] | 5 | 0.8856 | 0.8000 | +0.0856 | 0.0078 |
| 5 | [0.90, 1.00] | 6 | 0.9816 | 0.3333 | +0.6483 | 0.0707 |

**ECE total = 0.1858**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
