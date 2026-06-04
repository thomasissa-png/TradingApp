# Calibration probabiliste — Reliability Diagram

- Généré : 2026-06-04T18:07:19.095411+02:00
- Méthode : ECE (Expected Calibration Error) simple, 5 bins sur proba ∈ [0.5, 1.0]
- proba = 0.5 + clip(|score| / 15.0, 0, 0.5)  [mapping déterministe — non calibré empiriquement]

## Interprétation

- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0
- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)
- **Sous-confiant** : proba_prédite < taux_observé
- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée

- Observations conclusives totales : 65
- Proba prédite moyenne : 0.6443
- Taux observé global : 0.4462
- **ECE = 0.1981** ⚠️ RECALIBRER (> 0.10)

## Reliability Diagram (textuel)

| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |
|---|---|---|---|---|---|---|
| 1 | [0.50, 0.60] | 37 | 0.5418 | 0.5405 | +0.0013 | 0.0007 |
| 2 | [0.60, 0.70] | 11 | 0.6265 | 0.2727 | +0.3538 | 0.0599 |
| 3 | [0.70, 0.80] | 6 | 0.7554 | 0.3333 | +0.4221 | 0.0390 |
| 4 | [0.80, 0.90] | 4 | 0.8790 | 0.5000 | +0.3790 | 0.0233 |
| 5 | [0.90, 1.00] | 7 | 0.9842 | 0.2857 | +0.6985 | 0.0752 |

**ECE total = 0.1981**

## Note méthodologique

L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.
Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.
Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba
est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.
