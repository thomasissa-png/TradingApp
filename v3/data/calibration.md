# Calibration probabiliste — Reliability Diagram

- Généré : 22 juillet 2026, 07h30
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 331
- Proba prédite moyenne : 0.7838
- Taux observé global : 0.4743
- **ECE = 0.3095** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 69 | 0.5490 | 0.4783 | +0.0707 | 0.0148 |
| 2 | [0.60, 0.70] | 66 | 0.6439 | 0.3939 | +0.2500 | 0.0498 |
| 3 | [0.70, 0.80] | 41 | 0.7450 | 0.6585 | +0.0865 | 0.0107 |
| 4 | [0.80, 0.90] | 35 | 0.8479 | 0.3714 | +0.4765 | 0.0504 |
| 5 | [0.90, 1.00] | 120 | 0.9902 | 0.4833 | +0.5069 | 0.1838 |

**ECE total = 0.3095**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
