# Calibration probabiliste — Reliability Diagram

- Généré : 28 août 2026, 06h34
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 1270
- Proba prédite moyenne : 0.7923
- Taux observé global : 0.5189
- **ECE = 0.2733** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 233 | 0.5463 | 0.4936 | +0.0527 | 0.0097 |
| 2 | [0.60, 0.70] | 234 | 0.6484 | 0.4957 | +0.1527 | 0.0281 |
| 3 | [0.70, 0.80] | 181 | 0.7472 | 0.5470 | +0.2002 | 0.0285 |
| 4 | [0.80, 0.90] | 159 | 0.8454 | 0.5660 | +0.2794 | 0.0350 |
| 5 | [0.90, 1.00] | 463 | 0.9881 | 0.5162 | +0.4719 | 0.1720 |

**ECE total = 0.2733**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
