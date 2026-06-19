# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-19T08:11:24.159406+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 259
- Proba prédite moyenne : 0.7328
- Taux observé global : 0.5405
- **ECE = 0.2311** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 81 | 0.5430 | 0.6049 | -0.0619 | 0.0194 |
| 2 | [0.60, 0.70] | 50 | 0.6475 | 0.5200 | +0.1275 | 0.0246 |
| 3 | [0.70, 0.80] | 45 | 0.7464 | 0.4000 | +0.3464 | 0.0602 |
| 4 | [0.80, 0.90] | 17 | 0.8597 | 0.6471 | +0.2126 | 0.0140 |
| 5 | [0.90, 1.00] | 66 | 0.9885 | 0.5455 | +0.4430 | 0.1129 |

**ECE total = 0.2311**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
