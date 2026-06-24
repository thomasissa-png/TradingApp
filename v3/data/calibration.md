# Calibration probabiliste — Reliability Diagram

- Généré : 24 juin 2026, 07h27
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 10
- Proba prédite moyenne : 0.7861
- Taux observé global : 0.7000
- **ECE = 0.1263** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 2 | 0.5310 | 0.0000 | +0.5310 | 0.1062 |
| 2 | [0.60, 0.70] | 3 | 0.6407 | 0.6667 | -0.0260 | 0.0078 |
| 3 | [0.70, 0.80] | 0 | — | — | — | — |
| 4 | [0.80, 0.90] | 0 | — | — | — | — |
| 5 | [0.90, 1.00] | 5 | 0.9755 | 1.0000 | -0.0245 | 0.0123 |

**ECE total = 0.1263**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
