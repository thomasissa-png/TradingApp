# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-04T07:07:54.683799+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 48
- Proba prédite moyenne : 0.6470
- Taux observé global : 0.6250
- **ECE = 0.1847** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 28 | 0.5382 | 0.6429 | -0.1047 | 0.0610 |
| 2 | [0.60, 0.70] | 4 | 0.6232 | 0.7500 | -0.1268 | 0.0106 |
| 3 | [0.70, 0.80] | 8 | 0.7589 | 0.3750 | +0.3839 | 0.0640 |
| 4 | [0.80, 0.90] | 4 | 0.8830 | 1.0000 | -0.1170 | 0.0097 |
| 5 | [0.90, 1.00] | 4 | 0.9723 | 0.5000 | +0.4723 | 0.0394 |

**ECE total = 0.1847**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
