# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 16 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 15 | 60.0% | 0.3342 | 0 | — | — |
| Argent | 7j | 6 | 33.3% | 0.5332 | 0 | — | — |
| Blé | 24h | 16 | 56.2% | 0.2044 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 12 | 75.0% | 0.1179 | 6 | 100.0% | 0.0699 |
| CAC 40 | 24h | 9 | 33.3% | 0.5273 | 5 | 20.0% | 0.6703 |
| CAC 40 | 7j | 1 | 0.0% | 1.0000 | 1 | 0.0% | 1.0000 |
| Cacao | 24h | 15 | 73.3% | 0.2256 | 14 | 78.6% | 0.2092 |
| Cacao | 7j | 9 | 100.0% | 0.0000 | 9 | 100.0% | 0.0002 |
| Café (Arabica) | 24h | 14 | 78.6% | 0.2463 | 14 | 78.6% | 0.2453 |
| Café (Arabica) | 7j | 11 | 81.8% | 0.1701 | 11 | 81.8% | 0.1464 |
| Coton | 24h | 10 | 70.0% | 0.1866 | 5 | 40.0% | 0.2957 |
| Coton | 7j | 5 | 0.0% | 0.4595 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 15 | 40.0% | 0.3783 | 7 | 42.9% | 0.4427 |
| Cuivre | 7j | 12 | 0.0% | 0.6177 | 8 | 0.0% | 0.6998 |
| EUR/USD | 24h | 15 | 13.3% | 0.5859 | 0 | — | — |
| EUR/USD | 7j | 6 | 0.0% | 1.0000 | 0 | — | — |
| Nasdaq | 24h | 9 | 22.2% | 0.4798 | 4 | 25.0% | 0.5115 |
| Nasdaq | 7j | 4 | 25.0% | 0.6017 | 3 | 33.3% | 0.5593 |
| Or | 24h | 13 | 38.5% | 0.4624 | 3 | 100.0% | 0.0000 |
| Or | 7j | 5 | 20.0% | 0.5882 | 4 | 25.0% | 0.4175 |
| Pétrole (Brent) | 24h | 15 | 40.0% | 0.4531 | 9 | 55.6% | 0.4635 |
| Pétrole (Brent) | 7j | 12 | 16.7% | 0.5849 | 6 | 33.3% | 0.5701 |
| S&P 500 | 24h | 13 | 100.0% | 0.0572 | 0 | — | — |
| S&P 500 | 7j | 10 | 50.0% | 0.4504 | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 12 | 75.0% | 0.2706 | 2 | 50.0% | 0.2474 |
| VIX | 7j | 3 | 100.0% | 0.2242 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+4.48 pts** sur 19 cellules
