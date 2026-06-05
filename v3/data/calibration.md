# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-05T14:56:16.707129+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 119
- Proba prédite moyenne : 0.6434
- Taux observé global : 0.5210
- **ECE = 0.2890** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 52 | 0.5401 | 0.7308 | -0.1907 | 0.0833 |
| 2 | [0.60, 0.70] | 40 | 0.6411 | 0.3750 | +0.2661 | 0.0894 |
| 3 | [0.70, 0.80] | 14 | 0.7583 | 0.1429 | +0.6154 | 0.0724 |
| 4 | [0.80, 0.90] | 4 | 0.8798 | 0.7500 | +0.1298 | 0.0044 |
| 5 | [0.90, 1.00] | 9 | 0.9670 | 0.4444 | +0.5226 | 0.0395 |

**ECE total = 0.2890**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
