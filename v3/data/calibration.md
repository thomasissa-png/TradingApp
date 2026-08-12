# Calibration probabiliste — Reliability Diagram

- Généré : 12 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 885
- Proba prédite moyenne : 0.7865
- Taux observé global : 0.4384
- **ECE = 0.3481** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 182 | 0.5483 | 0.4560 | +0.0923 | 0.0190 |
| 2 | [0.60, 0.70] | 157 | 0.6480 | 0.4204 | +0.2276 | 0.0404 |
| 3 | [0.70, 0.80] | 119 | 0.7498 | 0.5462 | +0.2036 | 0.0274 |
| 4 | [0.80, 0.90] | 116 | 0.8451 | 0.4569 | +0.3882 | 0.0509 |
| 5 | [0.90, 1.00] | 311 | 0.9879 | 0.3891 | +0.5988 | 0.2104 |

**ECE total = 0.3481**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
