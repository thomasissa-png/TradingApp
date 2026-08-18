# Calibration probabiliste — Reliability Diagram

- Généré : 18 août 2026, 07h33
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1001
- Proba prédite moyenne : 0.7844
- Taux observé global : 0.4625
- **ECE = 0.3218** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 207 | 0.5471 | 0.4831 | +0.0640 | 0.0132 |
| 2 | [0.60, 0.70] | 186 | 0.6471 | 0.4301 | +0.2170 | 0.0403 |
| 3 | [0.70, 0.80] | 135 | 0.7476 | 0.5037 | +0.2439 | 0.0329 |
| 4 | [0.80, 0.90] | 118 | 0.8453 | 0.4492 | +0.3961 | 0.0467 |
| 5 | [0.90, 1.00] | 355 | 0.9883 | 0.4563 | +0.5320 | 0.1887 |

**ECE total = 0.3218**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
