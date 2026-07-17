# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 17 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 17 | 70.6% | 0.2475 | 0 | — | — |
| Argent | 7j | 13 | 69.2% | 0.2710 | 0 | — | — |
| Blé | 24h | 17 | 52.9% | 0.2512 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 13 | 76.9% | 0.1154 | 6 | 100.0% | 0.0699 |
| CAC 40 | 24h | 6 | 50.0% | 0.4315 | 3 | 33.3% | 0.6035 |
| CAC 40 | 7j | 2 | 50.0% | 0.5760 | 1 | 0.0% | 1.0000 |
| Cacao | 24h | 17 | 64.7% | 0.3272 | 16 | 62.5% | 0.3388 |
| Cacao | 7j | 12 | 66.7% | 0.3333 | 12 | 66.7% | 0.3335 |
| Café (Arabica) | 24h | 15 | 73.3% | 0.3007 | 15 | 73.3% | 0.2872 |
| Café (Arabica) | 7j | 10 | 80.0% | 0.2518 | 10 | 80.0% | 0.2268 |
| Coton | 24h | 12 | 16.7% | 0.4606 | 5 | 0.0% | 0.4941 |
| Coton | 7j | 1 | 0.0% | 0.6735 | 1 | 0.0% | 0.8823 |
| Cuivre | 24h | 11 | 18.2% | 0.6118 | 7 | 28.6% | 0.5433 |
| Cuivre | 7j | 2 | 0.0% | 0.8511 | 1 | 0.0% | 0.9370 |
| EUR/USD | 24h | 9 | 0.0% | 0.7846 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 12 | 58.3% | 0.2730 | 6 | 50.0% | 0.2826 |
| Nasdaq | 7j | 6 | 83.3% | 0.1750 | 5 | 80.0% | 0.1808 |
| Or | 24h | 14 | 57.1% | 0.2676 | 5 | 100.0% | 0.0353 |
| Or | 7j | 9 | 66.7% | 0.2660 | 8 | 62.5% | 0.2324 |
| Pétrole (Brent) | 24h | 14 | 42.9% | 0.4141 | 8 | 62.5% | 0.3964 |
| Pétrole (Brent) | 7j | 13 | 23.1% | 0.5455 | 6 | 33.3% | 0.5701 |
| S&P 500 | 24h | 11 | 100.0% | 0.0656 | 0 | — | — |
| S&P 500 | 7j | 5 | 20.0% | 0.6979 | 0 | — | — |
| Sucre | 24h | 11 | 18.2% | 0.5522 | 7 | 0.0% | 0.6140 |
| Sucre | 7j | 3 | 0.0% | 0.8592 | 2 | 0.0% | 1.0000 |
| USD/JPY | 24h | 4 | 25.0% | 0.3213 | 1 | 0.0% | 0.4147 |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 10 | 90.0% | 0.2456 | 1 | 100.0% | 0.2215 |
| VIX | 7j | 1 | 100.0% | 0.1924 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-0.66 pts** sur 22 cellules
