# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 14 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 22.2% | 0.5631 | 0 | — | — |
| Argent | 7j | 6 | 33.3% | 0.5332 | 0 | — | — |
| Blé | 24h | 14 | 50.0% | 0.2267 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 10 | 70.0% | 0.1415 | 4 | 100.0% | 0.1024 |
| CAC 40 | 24h | 5 | 60.0% | 0.3466 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 2 | 50.0% | 0.2169 | 0 | — | — |
| Cacao | 24h | 14 | 78.6% | 0.2065 | 14 | 78.6% | 0.2092 |
| Cacao | 7j | 9 | 100.0% | 0.0000 | 9 | 100.0% | 0.0002 |
| Café (Arabica) | 24h | 14 | 78.6% | 0.2463 | 14 | 78.6% | 0.2453 |
| Café (Arabica) | 7j | 10 | 90.0% | 0.1518 | 10 | 90.0% | 0.1268 |
| Coton | 24h | 9 | 66.7% | 0.1990 | 5 | 40.0% | 0.2957 |
| Coton | 7j | 5 | 0.0% | 0.4595 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 14 | 35.7% | 0.4024 | 7 | 42.9% | 0.4427 |
| Cuivre | 7j | 9 | 0.0% | 0.5927 | 7 | 0.0% | 0.6569 |
| EUR/USD | 24h | 6 | 50.0% | 0.3582 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 8 | 37.5% | 0.3626 | 4 | 50.0% | 0.3447 |
| Nasdaq | 7j | 4 | 75.0% | 0.2337 | 4 | 75.0% | 0.2248 |
| Or | 24h | 13 | 38.5% | 0.4624 | 3 | 100.0% | 0.0000 |
| Or | 7j | 3 | 33.3% | 0.3834 | 3 | 33.3% | 0.3236 |
| Pétrole (Brent) | 24h | 14 | 42.9% | 0.4141 | 8 | 62.5% | 0.3964 |
| Pétrole (Brent) | 7j | 10 | 0.0% | 0.6891 | 4 | 0.0% | 0.8091 |
| S&P 500 | 24h | 10 | 90.0% | 0.1461 | 0 | — | — |
| S&P 500 | 7j | 4 | 0.0% | 0.8302 | 0 | — | — |
| Sucre | 24h | 4 | 25.0% | 0.6120 | 2 | 0.0% | 0.7575 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 3 | 33.3% | 0.2536 | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 7 | 85.7% | 0.2536 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+4.77 pts** sur 18 cellules
