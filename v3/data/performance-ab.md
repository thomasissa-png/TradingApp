# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 13 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 11 | 18.2% | 0.5401 | 0 | — | — |
| Argent | 7j | 5 | 40.0% | 0.5382 | 0 | — | — |
| Blé | 24h | 13 | 46.1% | 0.2441 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 9 | 66.7% | 0.1572 | 3 | 100.0% | 0.1365 |
| CAC 40 | 24h | 9 | 77.8% | 0.2419 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 1 | 0.0% | 0.2816 | 0 | — | — |
| Cacao | 24h | 12 | 91.7% | 0.0986 | 12 | 91.7% | 0.1202 |
| Cacao | 7j | 9 | 100.0% | 0.0000 | 9 | 100.0% | 0.0002 |
| Café (Arabica) | 24h | 13 | 76.9% | 0.2565 | 13 | 76.9% | 0.2552 |
| Café (Arabica) | 7j | 9 | 100.0% | 0.0576 | 9 | 100.0% | 0.0298 |
| Coton | 24h | 5 | 40.0% | 0.3159 | 3 | 0.0% | 0.4353 |
| Coton | 7j | 5 | 0.0% | 0.4595 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 7 | 42.9% | 0.3933 | 5 | 60.0% | 0.2992 |
| Cuivre | 7j | 2 | 0.0% | 0.8511 | 1 | 0.0% | 0.9370 |
| EUR/USD | 24h | 6 | 33.3% | 0.5249 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 9 | 11.1% | 0.5661 | 4 | 25.0% | 0.6398 |
| Nasdaq | 7j | 5 | 20.0% | 0.6610 | 5 | 20.0% | 0.6710 |
| Or | 24h | 9 | 11.1% | 0.7085 | 1 | 100.0% | 0.0000 |
| Or | 7j | 4 | 0.0% | 0.9454 | 1 | 0.0% | 0.6900 |
| Pétrole (Brent) | 24h | 12 | 33.3% | 0.4720 | 6 | 50.0% | 0.5031 |
| Pétrole (Brent) | 7j | 9 | 0.0% | 0.7307 | 3 | 0.0% | 0.9186 |
| S&P 500 | 24h | 12 | 100.0% | 0.0619 | 0 | — | — |
| S&P 500 | 7j | 8 | 37.5% | 0.5282 | 0 | — | — |
| Sucre | 24h | 4 | 25.0% | 0.6120 | 2 | 0.0% | 0.7575 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 2 | 0.0% | 0.3994 | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 11 | 81.8% | 0.2546 | 2 | 50.0% | 0.2474 |
| VIX | 7j | 3 | 100.0% | 0.2242 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+3.47 pts** sur 19 cellules
