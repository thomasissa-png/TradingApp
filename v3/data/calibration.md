# Calibration probabiliste — Reliability Diagram

- Généré : 3 août 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 586
- Proba prédite moyenne : 0.7885
- Taux observé global : 0.3976
- **ECE = 0.3910** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 125 | 0.5492 | 0.4720 | +0.0772 | 0.0165 |
| 2 | [0.60, 0.70] | 109 | 0.6493 | 0.4128 | +0.2365 | 0.0440 |
| 3 | [0.70, 0.80] | 66 | 0.7498 | 0.5455 | +0.2043 | 0.0230 |
| 4 | [0.80, 0.90] | 71 | 0.8492 | 0.2958 | +0.5534 | 0.0671 |
| 5 | [0.90, 1.00] | 215 | 0.9900 | 0.3349 | +0.6551 | 0.2404 |

**ECE total = 0.3910**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
