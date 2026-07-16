# Calibration probabiliste — Reliability Diagram

- Généré : 16 juillet 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 267
- Proba prédite moyenne : 0.7860
- Taux observé global : 0.5019
- **ECE = 0.2841** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 61 | 0.5496 | 0.4590 | +0.0906 | 0.0207 |
| 2 | [0.60, 0.70] | 48 | 0.6445 | 0.5208 | +0.1237 | 0.0222 |
| 3 | [0.70, 0.80] | 30 | 0.7457 | 0.7000 | +0.0457 | 0.0051 |
| 4 | [0.80, 0.90] | 27 | 0.8464 | 0.4074 | +0.4390 | 0.0444 |
| 5 | [0.90, 1.00] | 101 | 0.9918 | 0.4851 | +0.5067 | 0.1917 |

**ECE total = 0.2841**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
