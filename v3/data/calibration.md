# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-08T12:02:24.289959+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 214
- Proba prédite moyenne : 0.6850
- Taux observé global : 0.6168
- **ECE = 0.1243** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 80 | 0.5487 | 0.6000 | -0.0513 | 0.0192 |
| 2 | [0.60, 0.70] | 50 | 0.6420 | 0.6800 | -0.0380 | 0.0089 |
| 3 | [0.70, 0.80] | 39 | 0.7524 | 0.2821 | +0.4703 | 0.0857 |
| 4 | [0.80, 0.90] | 16 | 0.8690 | 0.8125 | +0.0565 | 0.0042 |
| 5 | [0.90, 1.00] | 29 | 0.9434 | 0.8966 | +0.0468 | 0.0063 |

**ECE total = 0.1243**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
