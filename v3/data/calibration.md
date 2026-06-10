# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-10T07:21:29.166735+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 101
- Proba prédite moyenne : 0.6838
- Taux observé global : 0.6139
- **ECE = 0.1585** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 40 | 0.5382 | 0.6500 | -0.1118 | 0.0443 |
| 2 | [0.60, 0.70] | 19 | 0.6364 | 0.6316 | +0.0048 | 0.0009 |
| 3 | [0.70, 0.80] | 19 | 0.7534 | 0.4737 | +0.2797 | 0.0526 |
| 4 | [0.80, 0.90] | 10 | 0.8667 | 0.7000 | +0.1667 | 0.0165 |
| 5 | [0.90, 1.00] | 13 | 0.9587 | 0.6154 | +0.3433 | 0.0442 |

**ECE total = 0.1585**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
