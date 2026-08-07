# Calibration probabiliste — Reliability Diagram

- Généré : 7 août 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 825
- Proba prédite moyenne : 0.7810
- Taux observé global : 0.4255
- **ECE = 0.3556** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 175 | 0.5492 | 0.4686 | +0.0806 | 0.0171 |
| 2 | [0.60, 0.70] | 153 | 0.6494 | 0.4248 | +0.2246 | 0.0417 |
| 3 | [0.70, 0.80] | 112 | 0.7476 | 0.5268 | +0.2208 | 0.0300 |
| 4 | [0.80, 0.90] | 107 | 0.8474 | 0.4673 | +0.3801 | 0.0493 |
| 5 | [0.90, 1.00] | 278 | 0.9872 | 0.3417 | +0.6455 | 0.2175 |

**ECE total = 0.3556**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
