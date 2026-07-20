# Calibration probabiliste — Reliability Diagram

- Généré : 20 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 290
- Proba prédite moyenne : 0.7844
- Taux observé global : 0.5517
- **ECE = 0.2332** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 58 | 0.5521 | 0.5000 | +0.0521 | 0.0104 |
| 2 | [0.60, 0.70] | 60 | 0.6447 | 0.6333 | +0.0114 | 0.0024 |
| 3 | [0.70, 0.80] | 35 | 0.7413 | 0.7429 | -0.0016 | 0.0002 |
| 4 | [0.80, 0.90] | 33 | 0.8470 | 0.3939 | +0.4531 | 0.0516 |
| 5 | [0.90, 1.00] | 104 | 0.9893 | 0.5192 | +0.4701 | 0.1686 |

**ECE total = 0.2332**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
