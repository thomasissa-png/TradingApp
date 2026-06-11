# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-11T07:25:58.766058+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 134
- Proba prédite moyenne : 0.6842
- Taux observé global : 0.6642
- **ECE = 0.1547** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 54 | 0.5366 | 0.7037 | -0.1671 | 0.0673 |
| 2 | [0.60, 0.70] | 26 | 0.6463 | 0.5769 | +0.0694 | 0.0135 |
| 3 | [0.70, 0.80] | 25 | 0.7467 | 0.5200 | +0.2267 | 0.0423 |
| 4 | [0.80, 0.90] | 10 | 0.8671 | 0.8000 | +0.0671 | 0.0050 |
| 5 | [0.90, 1.00] | 19 | 0.9769 | 0.7895 | +0.1874 | 0.0266 |

**ECE total = 0.1547**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
