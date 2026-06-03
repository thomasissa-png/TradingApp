# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-03T12:05:56.989715+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 26
- Proba prédite moyenne : 0.6763
- Taux observé global : 0.8462
- **ECE = 0.1736** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 11 | 0.5385 | 0.8182 | -0.2797 | 0.1183 |
| 2 | [0.60, 0.70] | 5 | 0.6304 | 0.8000 | -0.1696 | 0.0326 |
| 3 | [0.70, 0.80] | 4 | 0.7627 | 0.7500 | +0.0127 | 0.0019 |
| 4 | [0.80, 0.90] | 4 | 0.8757 | 1.0000 | -0.1243 | 0.0191 |
| 5 | [0.90, 1.00] | 2 | 0.9780 | 1.0000 | -0.0220 | 0.0017 |

**ECE total = 0.1736**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
