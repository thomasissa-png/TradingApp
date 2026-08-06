# Calibration probabiliste — Reliability Diagram

- Généré : 6 août 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 769
- Proba prédite moyenne : 0.7792
- Taux observé global : 0.4148
- **ECE = 0.3644** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 161 | 0.5499 | 0.4596 | +0.0903 | 0.0189 |
| 2 | [0.60, 0.70] | 150 | 0.6496 | 0.4267 | +0.2229 | 0.0435 |
| 3 | [0.70, 0.80] | 106 | 0.7470 | 0.5000 | +0.2470 | 0.0340 |
| 4 | [0.80, 0.90] | 96 | 0.8468 | 0.4479 | +0.3989 | 0.0498 |
| 5 | [0.90, 1.00] | 256 | 0.9874 | 0.3320 | +0.6554 | 0.2182 |

**ECE total = 0.3644**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
