# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-05T18:06:33.264982+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 141
- Proba prédite moyenne : 0.6627
- Taux observé global : 0.5248
- **ECE = 0.2499** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 59 | 0.5442 | 0.6780 | -0.1338 | 0.0560 |
| 2 | [0.60, 0.70] | 35 | 0.6382 | 0.4857 | +0.1525 | 0.0379 |
| 3 | [0.70, 0.80] | 24 | 0.7513 | 0.0833 | +0.6680 | 0.1137 |
| 4 | [0.80, 0.90] | 12 | 0.8747 | 0.7500 | +0.1247 | 0.0106 |
| 5 | [0.90, 1.00] | 11 | 0.9512 | 0.5455 | +0.4057 | 0.0317 |

**ECE total = 0.2499**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
