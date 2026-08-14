# Calibration probabiliste — Reliability Diagram

- Généré : 14 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 951
- Proba prédite moyenne : 0.7861
- Taux observé global : 0.4395
- **ECE = 0.3466** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 200 | 0.5473 | 0.4900 | +0.0573 | 0.0121 |
| 2 | [0.60, 0.70] | 172 | 0.6471 | 0.4128 | +0.2343 | 0.0424 |
| 3 | [0.70, 0.80] | 121 | 0.7470 | 0.5207 | +0.2263 | 0.0288 |
| 4 | [0.80, 0.90] | 115 | 0.8456 | 0.4435 | +0.4021 | 0.0486 |
| 5 | [0.90, 1.00] | 343 | 0.9888 | 0.3936 | +0.5952 | 0.2147 |

**ECE total = 0.3466**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
