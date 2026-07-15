# Calibration probabiliste — Reliability Diagram

- Généré : 15 juillet 2026, 07h29
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 234
- Proba prédite moyenne : 0.7877
- Taux observé global : 0.4744
- **ECE = 0.3135** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 48 | 0.5472 | 0.4167 | +0.1305 | 0.0268 |
| 2 | [0.60, 0.70] | 47 | 0.6444 | 0.4255 | +0.2189 | 0.0440 |
| 3 | [0.70, 0.80] | 27 | 0.7460 | 0.6667 | +0.0793 | 0.0092 |
| 4 | [0.80, 0.90] | 22 | 0.8412 | 0.3636 | +0.4776 | 0.0449 |
| 5 | [0.90, 1.00] | 90 | 0.9903 | 0.5000 | +0.4903 | 0.1886 |

**ECE total = 0.3135**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
