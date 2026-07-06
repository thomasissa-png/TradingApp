# Calibration probabiliste — Reliability Diagram

- Généré : 6 juillet 2026, 20h17
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 136
- Proba prédite moyenne : 0.8002
- Taux observé global : 0.5000
- **ECE = 0.3002** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 25 | 0.5442 | 0.4800 | +0.0642 | 0.0118 |
| 2 | [0.60, 0.70] | 24 | 0.6492 | 0.5000 | +0.1492 | 0.0263 |
| 3 | [0.70, 0.80] | 19 | 0.7472 | 0.7368 | +0.0104 | 0.0015 |
| 4 | [0.80, 0.90] | 13 | 0.8364 | 0.6154 | +0.2210 | 0.0211 |
| 5 | [0.90, 1.00] | 55 | 0.9923 | 0.4000 | +0.5923 | 0.2395 |

**ECE total = 0.3002**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
