# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-18T07:26:43.869205+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 89
- Proba prédite moyenne : 0.6323
- Taux observé global : 0.5955
- **ECE = 0.1876** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 47 | 0.5377 | 0.6596 | -0.1219 | 0.0643 |
| 2 | [0.60, 0.70] | 19 | 0.6321 | 0.6842 | -0.0521 | 0.0111 |
| 3 | [0.70, 0.80] | 14 | 0.7358 | 0.6429 | +0.0929 | 0.0146 |
| 4 | [0.80, 0.90] | 2 | 0.8473 | 0.0000 | +0.8473 | 0.0190 |
| 5 | [0.90, 1.00] | 7 | 0.9993 | 0.0000 | +0.9993 | 0.0786 |

**ECE total = 0.1876**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
