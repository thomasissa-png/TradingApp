# Calibration probabiliste — Reliability Diagram

- Généré : 13 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 927
- Proba prédite moyenne : 0.7870
- Taux observé global : 0.4315
- **ECE = 0.3556** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 190 | 0.5475 | 0.4789 | +0.0686 | 0.0141 |
| 2 | [0.60, 0.70] | 166 | 0.6476 | 0.4036 | +0.2440 | 0.0437 |
| 3 | [0.70, 0.80] | 123 | 0.7486 | 0.4878 | +0.2608 | 0.0346 |
| 4 | [0.80, 0.90] | 118 | 0.8449 | 0.4492 | +0.3957 | 0.0504 |
| 5 | [0.90, 1.00] | 330 | 0.9886 | 0.3909 | +0.5977 | 0.2128 |

**ECE total = 0.3556**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
