# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-08T18:07:34.538770+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 197
- Proba prédite moyenne : 0.6828
- Taux observé global : 0.5990
- **ECE = 0.1928** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 79 | 0.5478 | 0.6835 | -0.1357 | 0.0544 |
| 2 | [0.60, 0.70] | 38 | 0.6386 | 0.5789 | +0.0597 | 0.0115 |
| 3 | [0.70, 0.80] | 39 | 0.7536 | 0.3077 | +0.4459 | 0.0883 |
| 4 | [0.80, 0.90] | 15 | 0.8706 | 0.7333 | +0.1373 | 0.0105 |
| 5 | [0.90, 1.00] | 26 | 0.9435 | 0.7308 | +0.2127 | 0.0281 |

**ECE total = 0.1928**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
