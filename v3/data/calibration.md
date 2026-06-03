# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-03T18:06:54.132560+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 32
- Proba prédite moyenne : 0.6562
- Taux observé global : 0.8125
- **ECE = 0.1595** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 17 | 0.5345 | 0.7647 | -0.2302 | 0.1223 |
| 2 | [0.60, 0.70] | 4 | 0.6275 | 0.7500 | -0.1225 | 0.0153 |
| 3 | [0.70, 0.80] | 4 | 0.7627 | 0.7500 | +0.0127 | 0.0016 |
| 4 | [0.80, 0.90] | 5 | 0.8788 | 1.0000 | -0.1212 | 0.0189 |
| 5 | [0.90, 1.00] | 2 | 0.9780 | 1.0000 | -0.0220 | 0.0014 |

**ECE total = 0.1595**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
