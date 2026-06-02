# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-02T16:27:28.136614+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 13
- Proba prédite moyenne : 0.6998
- Taux observé global : 0.7692
- **ECE = 0.1633** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 6 | 0.5399 | 0.6667 | -0.1268 | 0.0585 |
| 2 | [0.60, 0.70] | 1 | 0.6107 | 0.0000 | +0.6107 | 0.0470 |
| 3 | [0.70, 0.80] | 2 | 0.7670 | 1.0000 | -0.2330 | 0.0358 |
| 4 | [0.80, 0.90] | 2 | 0.8790 | 1.0000 | -0.1210 | 0.0186 |
| 5 | [0.90, 1.00] | 2 | 0.9780 | 1.0000 | -0.0220 | 0.0034 |

**ECE total = 0.1633**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
