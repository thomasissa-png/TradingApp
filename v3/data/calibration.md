# Calibration probabiliste — Reliability Diagram

- Généré : 3 septembre 2026, 07h27
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1236
- Proba prédite moyenne : 0.7878
- Taux observé global : 0.5065
- **ECE = 0.2813** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 242 | 0.5464 | 0.4959 | +0.0505 | 0.0099 |
| 2 | [0.60, 0.70] | 225 | 0.6478 | 0.4756 | +0.1722 | 0.0314 |
| 3 | [0.70, 0.80] | 175 | 0.7474 | 0.5029 | +0.2445 | 0.0346 |
| 4 | [0.80, 0.90] | 155 | 0.8452 | 0.5677 | +0.2775 | 0.0348 |
| 5 | [0.90, 1.00] | 439 | 0.9884 | 0.5080 | +0.4804 | 0.1706 |

**ECE total = 0.2813**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
