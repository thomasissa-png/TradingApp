# Calibration probabiliste — Reliability Diagram

- Généré : 23 juillet 2026, 07h27
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 334
- Proba prédite moyenne : 0.7935
- Taux observé global : 0.4581
- **ECE = 0.3354** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 67 | 0.5500 | 0.4328 | +0.1172 | 0.0235 |
| 2 | [0.60, 0.70] | 63 | 0.6470 | 0.4127 | +0.2343 | 0.0442 |
| 3 | [0.70, 0.80] | 38 | 0.7452 | 0.6579 | +0.0873 | 0.0099 |
| 4 | [0.80, 0.90] | 39 | 0.8479 | 0.3590 | +0.4889 | 0.0571 |
| 5 | [0.90, 1.00] | 127 | 0.9924 | 0.4646 | +0.5278 | 0.2007 |

**ECE total = 0.3354**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
