# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 27 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 21 | 23.8% | 0.4555 | 0 | — | — |
| Argent | 7j | 13 | 23.1% | 0.6084 | 0 | — | — |
| Argent | 1m | 0 | — | — | 0 | — | — |
| Blé | 24h | 19 | 52.6% | 0.2774 | 5 | 40.0% | 0.5282 |
| Blé | 7j | 16 | 81.2% | 0.0938 | 6 | 100.0% | 0.0699 |
| Blé | 1m | 2 | 50.0% | 0.1724 | 1 | 100.0% | 0.1429 |
| CAC 40 | 24h | 8 | 37.5% | 0.4390 | 3 | 33.3% | 0.6035 |
| CAC 40 | 7j | 3 | 33.3% | 0.4779 | 1 | 0.0% | 1.0000 |
| CAC 40 | 1m | 0 | — | — | 0 | — | — |
| Cacao | 24h | 20 | 65.0% | 0.3179 | 19 | 63.2% | 0.3238 |
| Cacao | 7j | 16 | 56.2% | 0.3930 | 15 | 53.3% | 0.3890 |
| Cacao | 1m | 2 | 100.0% | 0.0000 | 2 | 100.0% | 0.0000 |
| Café (Arabica) | 24h | 21 | 61.9% | 0.3170 | 21 | 61.9% | 0.3043 |
| Café (Arabica) | 7j | 14 | 57.1% | 0.2795 | 14 | 57.1% | 0.2770 |
| Café (Arabica) | 1m | 2 | 100.0% | 0.0177 | 2 | 100.0% | 0.0049 |
| Coton | 24h | 12 | 25.0% | 0.3430 | 4 | 0.0% | 0.4585 |
| Coton | 7j | 4 | 0.0% | 0.5016 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 20 | 35.0% | 0.4829 | 8 | 37.5% | 0.5124 |
| Cuivre | 7j | 12 | 0.0% | 0.5498 | 6 | 0.0% | 0.6980 |
| Cuivre | 1m | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 8 | 0.0% | 0.5920 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 1m | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 22 | 77.3% | 0.1695 | 12 | 75.0% | 0.1541 |
| Nasdaq | 7j | 18 | 94.4% | 0.0948 | 14 | 92.9% | 0.0921 |
| Nasdaq | 1m | 2 | 100.0% | 0.0000 | 2 | 100.0% | 0.0000 |
| Or | 24h | 21 | 23.8% | 0.5602 | 6 | 33.3% | 0.4655 |
| Or | 7j | 10 | 0.0% | 0.8161 | 6 | 0.0% | 0.7295 |
| Or | 1m | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 24h | 22 | 45.5% | 0.4431 | 16 | 56.2% | 0.3957 |
| Pétrole (Brent) | 7j | 18 | 44.4% | 0.3954 | 9 | 55.6% | 0.3801 |
| Pétrole (Brent) | 1m | 2 | 0.0% | 1.0000 | 1 | 0.0% | 1.0000 |
| S&P 500 | 24h | 19 | 21.1% | 0.6511 | 0 | — | — |
| S&P 500 | 7j | 9 | 44.4% | 0.3114 | 0 | — | — |
| S&P 500 | 1m | 0 | — | — | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 11 | 100.0% | 0.1243 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |
| VIX | 1m | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+0.82 pts** sur 23 cellules
