# Calibration probabiliste — Reliability Diagram

- Généré : 8 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 147
- Proba prédite moyenne : 0.8001
- Taux observé global : 0.5102
- **ECE = 0.2900** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 29 | 0.5430 | 0.5172 | +0.0258 | 0.0051 |
| 2 | [0.60, 0.70] | 23 | 0.6486 | 0.5217 | +0.1269 | 0.0199 |
| 3 | [0.70, 0.80] | 19 | 0.7492 | 0.7368 | +0.0124 | 0.0016 |
| 4 | [0.80, 0.90] | 17 | 0.8403 | 0.4118 | +0.4285 | 0.0496 |
| 5 | [0.90, 1.00] | 59 | 0.9904 | 0.4576 | +0.5328 | 0.2138 |

**ECE total = 0.2900**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
