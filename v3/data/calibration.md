# Calibration probabiliste — Reliability Diagram

- Généré : 19 août 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 996
- Proba prédite moyenne : 0.7849
- Taux observé global : 0.4458
- **ECE = 0.3391** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 206 | 0.5458 | 0.5000 | +0.0458 | 0.0095 |
| 2 | [0.60, 0.70] | 185 | 0.6490 | 0.4162 | +0.2328 | 0.0432 |
| 3 | [0.70, 0.80] | 129 | 0.7475 | 0.4884 | +0.2591 | 0.0336 |
| 4 | [0.80, 0.90] | 122 | 0.8457 | 0.4344 | +0.4113 | 0.0504 |
| 5 | [0.90, 1.00] | 354 | 0.9877 | 0.4181 | +0.5696 | 0.2024 |

**ECE total = 0.3391**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
