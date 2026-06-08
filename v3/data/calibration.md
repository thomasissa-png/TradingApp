# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-08T16:28:24.152030+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 190
- Proba prédite moyenne : 0.6861
- Taux observé global : 0.5737
- **ECE = 0.1809** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 72 | 0.5485 | 0.6389 | -0.0904 | 0.0343 |
| 2 | [0.60, 0.70] | 40 | 0.6385 | 0.5250 | +0.1135 | 0.0239 |
| 3 | [0.70, 0.80] | 38 | 0.7538 | 0.3158 | +0.4380 | 0.0876 |
| 4 | [0.80, 0.90] | 15 | 0.8706 | 0.7333 | +0.1373 | 0.0108 |
| 5 | [0.90, 1.00] | 25 | 0.9450 | 0.7600 | +0.1850 | 0.0243 |

**ECE total = 0.1809**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
