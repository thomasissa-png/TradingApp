# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-15T07:26:47.877867+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 12 | 41.7% | 0.5664 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 8 | 50.0% | 0.3995 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 6 | 83.3% | 0.1437 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 4 | 100.0% | 0.1281 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 12 | 41.7% | 0.2595 | 2 | 100.0% | 0.2457 |
| CAC 40 | 7j | 8 | 75.0% | 0.2611 | 2 | 100.0% | 0.2206 |
| Cacao | 24h | 10 | 30.0% | 0.2903 | 9 | 33.3% | 0.2669 |
| Cacao | 7j | 2 | 0.0% | 0.8028 | 1 | 0.0% | 0.8798 |
| Café (Arabica) | 24h | 10 | 10.0% | 0.4455 | 10 | 10.0% | 0.3947 |
| Café (Arabica) | 7j | 2 | 0.0% | 0.4410 | 2 | 0.0% | 0.4476 |
| Cuivre | 24h | 11 | 45.5% | 0.2304 | 7 | 71.4% | 0.1795 |
| Cuivre | 7j | 4 | 0.0% | 0.3025 | 2 | 0.0% | 0.3419 |
| EUR/USD | 24h | 8 | 25.0% | 0.7381 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 0.0% | 1.0000 | 0 | — | — |
| Nasdaq | 24h | 11 | 36.4% | 0.6036 | 7 | 14.3% | 0.6736 |
| Nasdaq | 7j | 8 | 62.5% | 0.4235 | 7 | 57.1% | 0.4599 |
| Or | 24h | 9 | 66.7% | 0.4020 | 6 | 66.7% | 0.3920 |
| Or | 7j | 6 | 100.0% | 0.0532 | 4 | 100.0% | 0.0413 |
| Pétrole (Brent) | 24h | 12 | 25.0% | 0.6168 | 7 | 0.0% | 0.6316 |
| Pétrole (Brent) | 7j | 8 | 0.0% | 0.7520 | 5 | 0.0% | 0.8305 |
| S&P 500 | 24h | 11 | 27.3% | 0.2889 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 6 | 50.0% | 0.3438 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 5 | 0.0% | 0.4838 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+3.95 pts** sur 21 cellules
