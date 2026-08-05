# Calibration probabiliste — Reliability Diagram

- Généré : 5 août 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 698
- Proba prédite moyenne : 0.7824
- Taux observé global : 0.3968
- **ECE = 0.3856** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 144 | 0.5495 | 0.4444 | +0.1051 | 0.0217 |
| 2 | [0.60, 0.70] | 140 | 0.6486 | 0.4000 | +0.2486 | 0.0499 |
| 3 | [0.70, 0.80] | 89 | 0.7485 | 0.5281 | +0.2204 | 0.0281 |
| 4 | [0.80, 0.90] | 82 | 0.8457 | 0.3659 | +0.4798 | 0.0564 |
| 5 | [0.90, 1.00] | 243 | 0.9886 | 0.3292 | +0.6594 | 0.2295 |

**ECE total = 0.3856**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
