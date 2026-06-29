# Calibration probabiliste — Reliability Diagram

- Généré : 29 juin 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 36
- Proba prédite moyenne : 0.7936
- Taux observé global : 0.5556
- **ECE = 0.3075** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 9 | 0.5456 | 0.3333 | +0.2123 | 0.0531 |
| 2 | [0.60, 0.70] | 6 | 0.6252 | 0.8333 | -0.2081 | 0.0347 |
| 3 | [0.70, 0.80] | 3 | 0.7120 | 0.0000 | +0.7120 | 0.0593 |
| 4 | [0.80, 0.90] | 0 | — | — | — | — |
| 5 | [0.90, 1.00] | 18 | 0.9874 | 0.6667 | +0.3207 | 0.1604 |

**ECE total = 0.3075**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
