# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-02T12:48:18.551815+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 11
- Proba prédite moyenne : 0.6701
- Taux observé global : 0.6364
- **ECE = 0.1895** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 5 | 0.5285 | 0.6000 | -0.0715 | 0.0325 |
| 2 | [0.60, 0.70] | 2 | 0.6140 | 0.0000 | +0.6140 | 0.1116 |
| 3 | [0.70, 0.80] | 1 | 0.7427 | 1.0000 | -0.2573 | 0.0234 |
| 4 | [0.80, 0.90] | 2 | 0.8790 | 1.0000 | -0.1210 | 0.0220 |
| 5 | [0.90, 1.00] | 1 | 1.0000 | 1.0000 | +0.0000 | 0.0000 |

**ECE total = 0.1895**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
