# Calibration probabiliste — Reliability Diagram

- Généré : 30 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 475
- Proba prédite moyenne : 0.7903
- Taux observé global : 0.4400
- **ECE = 0.3504** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 96 | 0.5521 | 0.4062 | +0.1459 | 0.0295 |
| 2 | [0.60, 0.70] | 89 | 0.6480 | 0.4494 | +0.1986 | 0.0372 |
| 3 | [0.70, 0.80] | 62 | 0.7468 | 0.5968 | +0.1500 | 0.0196 |
| 4 | [0.80, 0.90] | 52 | 0.8501 | 0.4038 | +0.4463 | 0.0489 |
| 5 | [0.90, 1.00] | 176 | 0.9898 | 0.4091 | +0.5807 | 0.2152 |

**ECE total = 0.3504**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
