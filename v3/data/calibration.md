# Calibration probabiliste — Reliability Diagram

- Généré : 24 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 373
- Proba prédite moyenne : 0.7799
- Taux observé global : 0.5576
- **ECE = 0.2222** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 76 | 0.5492 | 0.5000 | +0.0492 | 0.0100 |
| 2 | [0.60, 0.70] | 81 | 0.6437 | 0.5679 | +0.0758 | 0.0165 |
| 3 | [0.70, 0.80] | 46 | 0.7452 | 0.7174 | +0.0278 | 0.0034 |
| 4 | [0.80, 0.90] | 39 | 0.8469 | 0.5128 | +0.3341 | 0.0349 |
| 5 | [0.90, 1.00] | 131 | 0.9902 | 0.5420 | +0.4482 | 0.1574 |

**ECE total = 0.2222**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
