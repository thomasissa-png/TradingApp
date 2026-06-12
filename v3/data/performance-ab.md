# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-12T07:27:12.842749+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 11 | 72.7% | 0.2771 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 6 | 66.7% | 0.1994 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 10 | 80.0% | 0.2133 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 3 | 100.0% | 0.0950 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 2 | 50.0% | 0.2834 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 7 | 14.3% | 0.3200 | 6 | 16.7% | 0.3037 |
| Cacao | 7j | 3 | 0.0% | 0.7125 | 2 | 0.0% | 0.8306 |
| Café (Arabica) | 24h | 10 | 20.0% | 0.3895 | 10 | 20.0% | 0.3506 |
| Café (Arabica) | 7j | 3 | 33.3% | 0.3558 | 3 | 33.3% | 0.3743 |
| Cuivre | 24h | 5 | 40.0% | 0.2862 | 3 | 66.7% | 0.2017 |
| Cuivre | 7j | 1 | 100.0% | 0.2317 | 0 | — | — |
| EUR/USD | 24h | 6 | 66.7% | 0.3206 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 50.0% | 0.2559 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 10 | 40.0% | 0.5990 | 7 | 14.3% | 0.6736 |
| Nasdaq | 7j | 6 | 83.3% | 0.2313 | 5 | 80.0% | 0.2439 |
| Or | 24h | 11 | 90.9% | 0.1575 | 8 | 87.5% | 0.1763 |
| Or | 7j | 6 | 100.0% | 0.0532 | 4 | 100.0% | 0.0413 |
| Pétrole (Brent) | 24h | 11 | 18.2% | 0.6662 | 7 | 0.0% | 0.6316 |
| Pétrole (Brent) | 7j | 6 | 0.0% | 0.6970 | 3 | 0.0% | 0.8786 |
| S&P 500 | 24h | 7 | 14.3% | 0.3270 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 6 | 50.0% | 0.3438 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 6 | 50.0% | 0.2309 | 2 | 50.0% | 0.1869 |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-3.60 pts** sur 20 cellules
