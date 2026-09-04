# Calibration probabiliste — Reliability Diagram

- Généré : 4 septembre 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1474
- Proba prédite moyenne : 0.7936
- Taux observé global : 0.5136
- **ECE = 0.2800** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 278 | 0.5470 | 0.4964 | +0.0506 | 0.0095 |
| 2 | [0.60, 0.70] | 260 | 0.6493 | 0.4731 | +0.1762 | 0.0311 |
| 3 | [0.70, 0.80] | 205 | 0.7481 | 0.5171 | +0.2310 | 0.0321 |
| 4 | [0.80, 0.90] | 190 | 0.8467 | 0.5526 | +0.2941 | 0.0379 |
| 5 | [0.90, 1.00] | 541 | 0.9883 | 0.5268 | +0.4615 | 0.1694 |

**ECE total = 0.2800**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
