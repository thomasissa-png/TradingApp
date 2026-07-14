# Calibration probabiliste — Reliability Diagram

- Généré : 14 juillet 2026, 07h28
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 216
- Proba prédite moyenne : 0.7847
- Taux observé global : 0.5139
- **ECE = 0.2708** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 45 | 0.5455 | 0.4444 | +0.1011 | 0.0211 |
| 2 | [0.60, 0.70] | 45 | 0.6422 | 0.4444 | +0.1978 | 0.0412 |
| 3 | [0.70, 0.80] | 22 | 0.7463 | 0.7273 | +0.0190 | 0.0019 |
| 4 | [0.80, 0.90] | 22 | 0.8432 | 0.4091 | +0.4341 | 0.0442 |
| 5 | [0.90, 1.00] | 82 | 0.9888 | 0.5610 | +0.4278 | 0.1624 |

**ECE total = 0.2708**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
