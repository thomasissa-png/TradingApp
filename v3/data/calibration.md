# Calibration probabiliste — Reliability Diagram

- Généré : 26 août 2026, 08h01
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1181
- Proba prédite moyenne : 0.7925
- Taux observé global : 0.4691
- **ECE = 0.3234** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 223 | 0.5465 | 0.4888 | +0.0577 | 0.0109 |
| 2 | [0.60, 0.70] | 207 | 0.6479 | 0.4493 | +0.1986 | 0.0348 |
| 3 | [0.70, 0.80] | 168 | 0.7468 | 0.4821 | +0.2647 | 0.0376 |
| 4 | [0.80, 0.90] | 153 | 0.8453 | 0.4641 | +0.3812 | 0.0494 |
| 5 | [0.90, 1.00] | 430 | 0.9888 | 0.4651 | +0.5237 | 0.1907 |

**ECE total = 0.3234**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
