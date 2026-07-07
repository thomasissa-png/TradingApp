# Calibration probabiliste — Reliability Diagram

- Généré : 7 juillet 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 140
- Proba prédite moyenne : 0.8057
- Taux observé global : 0.5143
- **ECE = 0.2974** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 25 | 0.5431 | 0.5600 | -0.0169 | 0.0030 |
| 2 | [0.60, 0.70] | 24 | 0.6487 | 0.5000 | +0.1487 | 0.0255 |
| 3 | [0.70, 0.80] | 19 | 0.7493 | 0.7368 | +0.0125 | 0.0017 |
| 4 | [0.80, 0.90] | 13 | 0.8359 | 0.5385 | +0.2974 | 0.0276 |
| 5 | [0.90, 1.00] | 59 | 0.9923 | 0.4237 | +0.5686 | 0.2396 |

**ECE total = 0.2974**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
