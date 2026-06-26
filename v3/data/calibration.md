# Calibration probabiliste — Reliability Diagram

- Généré : 26 juin 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 23
- Proba prédite moyenne : 0.8556
- Taux observé global : 0.6522
- **ECE = 0.2034** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 3 | 0.5513 | 0.0000 | +0.5513 | 0.0719 |
| 2 | [0.60, 0.70] | 5 | 0.6303 | 0.6000 | +0.0303 | 0.0066 |
| 3 | [0.70, 0.80] | 0 | — | — | — | — |
| 4 | [0.80, 0.90] | 0 | — | — | — | — |
| 5 | [0.90, 1.00] | 15 | 0.9915 | 0.8000 | +0.1915 | 0.1249 |

**ECE total = 0.2034**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
