# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-02T21:57:58.918928+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 15
- Proba prédite moyenne : 0.7170
- Taux observé global : 0.8000
- **ECE = 0.1644** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 6 | 0.5399 | 0.6667 | -0.1268 | 0.0507 |
| 2 | [0.60, 0.70] | 1 | 0.6107 | 0.0000 | +0.6107 | 0.0407 |
| 3 | [0.70, 0.80] | 3 | 0.7693 | 1.0000 | -0.2307 | 0.0461 |
| 4 | [0.80, 0.90] | 3 | 0.8802 | 1.0000 | -0.1198 | 0.0240 |
| 5 | [0.90, 1.00] | 2 | 0.9780 | 1.0000 | -0.0220 | 0.0029 |

**ECE total = 0.1644**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
