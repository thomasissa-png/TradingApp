# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-04T11:05:55.979900+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 50
- Proba prédite moyenne : 0.6648
- Taux observé global : 0.5600
- **ECE = 0.1768** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 25 | 0.5467 | 0.6000 | -0.0533 | 0.0266 |
| 2 | [0.60, 0.70] | 9 | 0.6238 | 0.4444 | +0.1794 | 0.0323 |
| 3 | [0.70, 0.80] | 6 | 0.7560 | 0.5000 | +0.2560 | 0.0307 |
| 4 | [0.80, 0.90] | 4 | 0.8830 | 1.0000 | -0.1170 | 0.0094 |
| 5 | [0.90, 1.00] | 6 | 0.9816 | 0.3333 | +0.6483 | 0.0778 |

**ECE total = 0.1768**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
