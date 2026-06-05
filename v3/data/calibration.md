# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-05T10:58:08.338027+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 100
- Proba prédite moyenne : 0.6514
- Taux observé global : 0.4700
- **ECE = 0.3331** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 40 | 0.5352 | 0.7250 | -0.1898 | 0.0759 |
| 2 | [0.60, 0.70] | 35 | 0.6416 | 0.3714 | +0.2702 | 0.0945 |
| 3 | [0.70, 0.80] | 12 | 0.7579 | 0.0833 | +0.6746 | 0.0809 |
| 4 | [0.80, 0.90] | 6 | 0.8823 | 0.3333 | +0.5490 | 0.0329 |
| 5 | [0.90, 1.00] | 7 | 0.9842 | 0.2857 | +0.6985 | 0.0489 |

**ECE total = 0.3331**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
