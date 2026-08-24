# Calibration probabiliste — Reliability Diagram

- Généré : 24 août 2026, 08h05
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1140
- Proba prédite moyenne : 0.7948
- Taux observé global : 0.4860
- **ECE = 0.3089** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 210 | 0.5469 | 0.4952 | +0.0517 | 0.0095 |
| 2 | [0.60, 0.70] | 199 | 0.6472 | 0.4422 | +0.2050 | 0.0358 |
| 3 | [0.70, 0.80] | 163 | 0.7474 | 0.4908 | +0.2566 | 0.0367 |
| 4 | [0.80, 0.90] | 146 | 0.8449 | 0.4932 | +0.3517 | 0.0451 |
| 5 | [0.90, 1.00] | 422 | 0.9888 | 0.4976 | +0.4912 | 0.1818 |

**ECE total = 0.3089**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
