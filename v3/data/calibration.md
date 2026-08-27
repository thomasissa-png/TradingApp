# Calibration probabiliste — Reliability Diagram

- Généré : 27 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1035
- Proba prédite moyenne : 0.7959
- Taux observé global : 0.4483
- **ECE = 0.3477** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 185 | 0.5465 | 0.4919 | +0.0546 | 0.0098 |
| 2 | [0.60, 0.70] | 181 | 0.6472 | 0.4199 | +0.2273 | 0.0398 |
| 3 | [0.70, 0.80] | 154 | 0.7471 | 0.4675 | +0.2796 | 0.0416 |
| 4 | [0.80, 0.90] | 134 | 0.8461 | 0.4701 | +0.3760 | 0.0487 |
| 5 | [0.90, 1.00] | 381 | 0.9898 | 0.4252 | +0.5646 | 0.2078 |

**ECE total = 0.3477**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
