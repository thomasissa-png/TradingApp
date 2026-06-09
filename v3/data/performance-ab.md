# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-09T07:21:37.531784+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 6 | 83.3% | 0.1722 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 3 | 33.3% | 0.2671 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 5 | 100.0% | 0.1429 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 3 | 100.0% | 0.0950 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 2 | 50.0% | 0.2834 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 7 | 28.6% | 0.2966 | 6 | 33.3% | 0.2811 |
| Cacao | 7j | 0 | — | — | 0 | — | — |
| Café (Arabica) | 24h | 4 | 50.0% | 0.2595 | 4 | 50.0% | 0.2662 |
| Café (Arabica) | 7j | 2 | 0.0% | 0.4410 | 2 | 0.0% | 0.4476 |
| Cuivre | 24h | 4 | 25.0% | 0.4352 | 4 | 25.0% | 0.3394 |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 4 | 100.0% | 0.1087 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 50.0% | 0.2559 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 8 | 50.0% | 0.4987 | 5 | 20.0% | 0.5611 |
| Nasdaq | 7j | 3 | 66.7% | 0.3823 | 3 | 66.7% | 0.3661 |
| Or | 24h | 6 | 100.0% | 0.1029 | 4 | 100.0% | 0.0881 |
| Or | 7j | 3 | 100.0% | 0.0478 | 3 | 100.0% | 0.0371 |
| Pétrole (Brent) | 24h | 5 | 40.0% | 0.5173 | 3 | 33.3% | 0.4982 |
| Pétrole (Brent) | 7j | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0013 |
| S&P 500 | 24h | 6 | 16.7% | 0.3240 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 3 | 33.3% | 0.4164 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 1 | 0.0% | 0.2574 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-5.48 pts** sur 18 cellules
