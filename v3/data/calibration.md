# Calibration probabiliste — Reliability Diagram

- Généré : 21 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 298
- Proba prédite moyenne : 0.7937
- Taux observé global : 0.4966
- **ECE = 0.2970** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 56 | 0.5496 | 0.4643 | +0.0853 | 0.0160 |
| 2 | [0.60, 0.70] | 59 | 0.6439 | 0.5424 | +0.1015 | 0.0201 |
| 3 | [0.70, 0.80] | 36 | 0.7423 | 0.7222 | +0.0201 | 0.0024 |
| 4 | [0.80, 0.90] | 34 | 0.8490 | 0.3529 | +0.4961 | 0.0566 |
| 5 | [0.90, 1.00] | 113 | 0.9926 | 0.4602 | +0.5324 | 0.2019 |

**ECE total = 0.2970**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
