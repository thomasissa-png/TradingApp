# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-16T07:27:36.128037+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 176
- Proba prédite moyenne : 0.7177
- Taux observé global : 0.4318
- **ECE = 0.2859** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 56 | 0.5370 | 0.5357 | +0.0013 | 0.0004 |
| 2 | [0.60, 0.70] | 36 | 0.6406 | 0.4167 | +0.2239 | 0.0458 |
| 3 | [0.70, 0.80] | 34 | 0.7476 | 0.5882 | +0.1594 | 0.0308 |
| 4 | [0.80, 0.90] | 12 | 0.8709 | 0.4167 | +0.4542 | 0.0310 |
| 5 | [0.90, 1.00] | 38 | 0.9819 | 0.1579 | +0.8240 | 0.1779 |

**ECE total = 0.2859**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
