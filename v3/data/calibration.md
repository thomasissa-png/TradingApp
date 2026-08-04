# Calibration probabiliste — Reliability Diagram

- Généré : 4 août 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 620
- Proba prédite moyenne : 0.7812
- Taux observé global : 0.4194
- **ECE = 0.3618** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 133 | 0.5511 | 0.4361 | +0.1150 | 0.0247 |
| 2 | [0.60, 0.70] | 125 | 0.6474 | 0.4400 | +0.2074 | 0.0418 |
| 3 | [0.70, 0.80] | 75 | 0.7485 | 0.5467 | +0.2018 | 0.0244 |
| 4 | [0.80, 0.90] | 70 | 0.8489 | 0.4000 | +0.4489 | 0.0507 |
| 5 | [0.90, 1.00] | 217 | 0.9887 | 0.3594 | +0.6293 | 0.2202 |

**ECE total = 0.3618**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
