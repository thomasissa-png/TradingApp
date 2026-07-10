# Calibration probabiliste — Reliability Diagram

- Généré : 10 juillet 2026, 07h31
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 191
- Proba prédite moyenne : 0.8032
- Taux observé global : 0.4764
- **ECE = 0.3352** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 35 | 0.5426 | 0.4571 | +0.0855 | 0.0157 |
| 2 | [0.60, 0.70] | 34 | 0.6457 | 0.4118 | +0.2339 | 0.0416 |
| 3 | [0.70, 0.80] | 23 | 0.7471 | 0.7826 | -0.0355 | 0.0043 |
| 4 | [0.80, 0.90] | 20 | 0.8402 | 0.3500 | +0.4902 | 0.0513 |
| 5 | [0.90, 1.00] | 79 | 0.9933 | 0.4557 | +0.5376 | 0.2223 |

**ECE total = 0.3352**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
