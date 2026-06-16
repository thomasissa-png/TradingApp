# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-16T07:27:36.128037+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 12 | 41.7% | 0.5664 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 8 | 50.0% | 0.3995 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 6 | 100.0% | 0.1348 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 3 | 100.0% | 0.0950 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 12 | 41.7% | 0.2595 | 2 | 100.0% | 0.2457 |
| CAC 40 | 7j | 9 | 77.8% | 0.2498 | 2 | 100.0% | 0.2206 |
| Cacao | 24h | 11 | 63.6% | 0.2544 | 9 | 66.7% | 0.2198 |
| Cacao | 7j | 3 | 100.0% | 0.0683 | 3 | 100.0% | 0.0185 |
| Café (Arabica) | 24h | 11 | 0.0% | 0.4651 | 11 | 0.0% | 0.4081 |
| Café (Arabica) | 7j | 4 | 0.0% | 0.5490 | 4 | 0.0% | 0.3459 |
| Cuivre | 24h | 9 | 33.3% | 0.2678 | 5 | 60.0% | 0.2048 |
| Cuivre | 7j | 3 | 33.3% | 0.2527 | 0 | — | — |
| EUR/USD | 24h | 9 | 55.6% | 0.4361 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 9 | 33.3% | 0.6362 | 8 | 37.5% | 0.5754 |
| Nasdaq | 7j | 3 | 0.0% | 1.0000 | 2 | 0.0% | 1.0000 |
| Or | 24h | 9 | 66.7% | 0.4020 | 6 | 66.7% | 0.3920 |
| Or | 7j | 6 | 100.0% | 0.0532 | 4 | 100.0% | 0.0413 |
| Pétrole (Brent) | 24h | 13 | 30.8% | 0.5695 | 8 | 12.5% | 0.5566 |
| Pétrole (Brent) | 7j | 9 | 11.1% | 0.6960 | 5 | 0.0% | 0.8305 |
| S&P 500 | 24h | 9 | 44.4% | 0.2347 | 0 | — | — |
| S&P 500 | 7j | 3 | 0.0% | 0.7341 | 0 | — | — |
| VIX | 24h | 13 | 23.1% | 0.4066 | 3 | 66.7% | 0.2865 |
| VIX | 7j | 2 | 0.0% | 0.4198 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+9.55 pts** sur 19 cellules
