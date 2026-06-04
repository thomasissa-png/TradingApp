# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-04T20:35:19.961135+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 59
- Proba prédite moyenne : 0.6554
- Taux observé global : 0.4746
- **ECE = 0.2093** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 30 | 0.5387 | 0.5667 | -0.0280 | 0.0142 |
| 2 | [0.60, 0.70] | 11 | 0.6265 | 0.2727 | +0.3538 | 0.0660 |
| 3 | [0.70, 0.80] | 7 | 0.7563 | 0.4286 | +0.3277 | 0.0389 |
| 4 | [0.80, 0.90] | 4 | 0.8578 | 0.7500 | +0.1078 | 0.0073 |
| 5 | [0.90, 1.00] | 7 | 0.9842 | 0.2857 | +0.6985 | 0.0829 |

**ECE total = 0.2093**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
