# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-12T07:27:12.842749+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 138
- Proba prédite moyenne : 0.7145
- Taux observé global : 0.5072
- **ECE = 0.2295** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 47 | 0.5419 | 0.5745 | -0.0326 | 0.0111 |
| 2 | [0.60, 0.70] | 25 | 0.6388 | 0.4800 | +0.1588 | 0.0288 |
| 3 | [0.70, 0.80] | 26 | 0.7468 | 0.5385 | +0.2083 | 0.0393 |
| 4 | [0.80, 0.90] | 13 | 0.8730 | 0.5385 | +0.3345 | 0.0315 |
| 5 | [0.90, 1.00] | 27 | 0.9778 | 0.3704 | +0.6074 | 0.1188 |

**ECE total = 0.2295**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
