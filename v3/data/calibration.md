# Calibration probabiliste — Reliability Diagram

- Généré : 31 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 541
- Proba prédite moyenne : 0.7899
- Taux observé global : 0.4011
- **ECE = 0.3889** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 109 | 0.5508 | 0.4495 | +0.1013 | 0.0204 |
| 2 | [0.60, 0.70] | 108 | 0.6484 | 0.4167 | +0.2317 | 0.0463 |
| 3 | [0.70, 0.80] | 59 | 0.7465 | 0.6102 | +0.1363 | 0.0149 |
| 4 | [0.80, 0.90] | 63 | 0.8493 | 0.3651 | +0.4842 | 0.0564 |
| 5 | [0.90, 1.00] | 202 | 0.9889 | 0.3168 | +0.6721 | 0.2509 |

**ECE total = 0.3889**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
