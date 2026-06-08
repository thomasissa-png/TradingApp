# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-08T07:05:58.329589+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 214
- Proba prédite moyenne : 0.6762
- Taux observé global : 0.5794
- **ECE = 0.1099** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 85 | 0.5440 | 0.5294 | +0.0146 | 0.0058 |
| 2 | [0.60, 0.70] | 47 | 0.6420 | 0.6596 | -0.0176 | 0.0039 |
| 3 | [0.70, 0.80] | 41 | 0.7512 | 0.2683 | +0.4829 | 0.0925 |
| 4 | [0.80, 0.90] | 15 | 0.8706 | 0.8000 | +0.0706 | 0.0050 |
| 5 | [0.90, 1.00] | 26 | 0.9396 | 0.9615 | -0.0219 | 0.0027 |

**ECE total = 0.1099**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
