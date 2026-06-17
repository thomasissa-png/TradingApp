# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-17T07:26:05.570460+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 228
- Proba prédite moyenne : 0.7070
- Taux observé global : 0.4298
- **ECE = 0.2878** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 81 | 0.5407 | 0.5556 | -0.0149 | 0.0053 |
| 2 | [0.60, 0.70] | 45 | 0.6426 | 0.4444 | +0.1982 | 0.0391 |
| 3 | [0.70, 0.80] | 43 | 0.7458 | 0.5581 | +0.1877 | 0.0354 |
| 4 | [0.80, 0.90] | 15 | 0.8635 | 0.4000 | +0.4635 | 0.0305 |
| 5 | [0.90, 1.00] | 44 | 0.9878 | 0.0682 | +0.9196 | 0.1775 |

**ECE total = 0.2878**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
