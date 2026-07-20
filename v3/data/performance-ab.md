# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 20 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 16 | 62.5% | 0.3099 | 0 | — | — |
| Argent | 7j | 10 | 60.0% | 0.3610 | 0 | — | — |
| Blé | 24h | 18 | 61.1% | 0.1817 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 14 | 78.6% | 0.1072 | 6 | 100.0% | 0.0699 |
| CAC 40 | 24h | 10 | 80.0% | 0.2336 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 2 | 50.0% | 0.2169 | 0 | — | — |
| Cacao | 24h | 18 | 61.1% | 0.3575 | 16 | 62.5% | 0.3388 |
| Cacao | 7j | 12 | 75.0% | 0.2500 | 12 | 75.0% | 0.2501 |
| Café (Arabica) | 24h | 17 | 70.6% | 0.2948 | 17 | 70.6% | 0.2823 |
| Café (Arabica) | 7j | 13 | 69.2% | 0.2508 | 13 | 69.2% | 0.2272 |
| Coton | 24h | 12 | 16.7% | 0.4606 | 5 | 0.0% | 0.4941 |
| Coton | 7j | 1 | 0.0% | 0.6735 | 1 | 0.0% | 0.8823 |
| Cuivre | 24h | 15 | 33.3% | 0.4816 | 6 | 33.3% | 0.5106 |
| Cuivre | 7j | 5 | 0.0% | 0.6213 | 3 | 0.0% | 0.5649 |
| EUR/USD | 24h | 9 | 0.0% | 0.7360 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 17 | 70.6% | 0.2179 | 7 | 57.1% | 0.2450 |
| Nasdaq | 7j | 11 | 90.9% | 0.1426 | 9 | 88.9% | 0.1422 |
| Or | 24h | 13 | 38.5% | 0.4270 | 4 | 75.0% | 0.1529 |
| Or | 7j | 7 | 57.1% | 0.3140 | 7 | 57.1% | 0.2655 |
| Pétrole (Brent) | 24h | 18 | 55.6% | 0.3263 | 12 | 75.0% | 0.2838 |
| Pétrole (Brent) | 7j | 14 | 28.6% | 0.5084 | 6 | 33.3% | 0.5701 |
| S&P 500 | 24h | 13 | 38.5% | 0.5634 | 0 | — | — |
| S&P 500 | 7j | 5 | 20.0% | 0.6346 | 0 | — | — |
| Sucre | 24h | 5 | 40.0% | 0.5114 | 2 | 0.0% | 0.7575 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 4 | 25.0% | 0.3213 | 1 | 0.0% | 0.4147 |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 11 | 100.0% | 0.1424 | 1 | 100.0% | 0.2278 |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-1.90 pts** sur 20 cellules
