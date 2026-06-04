# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-04T14:58:39.294048+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 59
- Proba prédite moyenne : 0.6844
- Taux observé global : 0.3898
- **ECE = 0.2947** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 26 | 0.5448 | 0.5000 | +0.0448 | 0.0198 |
| 2 | [0.60, 0.70] | 11 | 0.6319 | 0.0909 | +0.5410 | 0.1009 |
| 3 | [0.70, 0.80] | 7 | 0.7581 | 0.4286 | +0.3295 | 0.0391 |
| 4 | [0.80, 0.90] | 8 | 0.8835 | 0.5000 | +0.3835 | 0.0520 |
| 5 | [0.90, 1.00] | 7 | 0.9842 | 0.2857 | +0.6985 | 0.0829 |

**ECE total = 0.2947**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
