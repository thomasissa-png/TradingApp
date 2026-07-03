# Calibration probabiliste — Reliability Diagram

- Généré : 3 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 105
- Proba prédite moyenne : 0.8051
- Taux observé global : 0.3714
- **ECE = 0.4337** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 20 | 0.5517 | 0.5000 | +0.0517 | 0.0098 |
| 2 | [0.60, 0.70] | 18 | 0.6496 | 0.4444 | +0.2052 | 0.0352 |
| 3 | [0.70, 0.80] | 14 | 0.7480 | 0.5000 | +0.2480 | 0.0331 |
| 4 | [0.80, 0.90] | 8 | 0.8340 | 0.6250 | +0.2090 | 0.0159 |
| 5 | [0.90, 1.00] | 45 | 0.9926 | 0.2000 | +0.7926 | 0.3397 |

**ECE total = 0.4337**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
