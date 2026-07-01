# Calibration probabiliste — Reliability Diagram

- Généré : 1 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 60
- Proba prédite moyenne : 0.8209
- Taux observé global : 0.7167
- **ECE = 0.2188** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 13 | 0.5501 | 0.6154 | -0.0653 | 0.0142 |
| 2 | [0.60, 0.70] | 9 | 0.6534 | 0.7778 | -0.1244 | 0.0187 |
| 3 | [0.70, 0.80] | 4 | 0.7268 | 1.0000 | -0.2732 | 0.0182 |
| 4 | [0.80, 0.90] | 2 | 0.8130 | 1.0000 | -0.1870 | 0.0062 |
| 5 | [0.90, 1.00] | 32 | 0.9903 | 0.6875 | +0.3028 | 0.1615 |

**ECE total = 0.2188**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
