# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 9 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 22.2% | 0.5828 | 0 | — | — |
| Argent | 7j | 4 | 50.0% | 0.4228 | 0 | — | — |
| Blé | 24h | 8 | 12.5% | 0.4578 | 2 | 0.0% | 0.9887 |
| Blé | 7j | 2 | 0.0% | 0.3957 | 0 | — | — |
| CAC 40 | 24h | 11 | 90.9% | 0.1274 | 2 | 100.0% | 0.0534 |
| CAC 40 | 7j | 6 | 100.0% | 0.0364 | 0 | — | — |
| Cacao | 24h | 11 | 100.0% | 0.0167 | 11 | 100.0% | 0.0402 |
| Cacao | 7j | 8 | 100.0% | 0.0000 | 8 | 100.0% | 0.0001 |
| Café (Arabica) | 24h | 10 | 80.0% | 0.2598 | 10 | 80.0% | 0.2587 |
| Café (Arabica) | 7j | 7 | 100.0% | 0.0740 | 7 | 100.0% | 0.0383 |
| Coton | 24h | 5 | 40.0% | 0.3159 | 3 | 0.0% | 0.4353 |
| Coton | 7j | 4 | 0.0% | 0.4873 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 8 | 50.0% | 0.2492 | 3 | 66.7% | 0.1279 |
| Cuivre | 7j | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0000 |
| EUR/USD | 24h | 6 | 0.0% | 0.9409 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 6 | 16.7% | 0.4442 | 3 | 33.3% | 0.4340 |
| Nasdaq | 7j | 4 | 75.0% | 0.2337 | 4 | 75.0% | 0.2248 |
| Or | 24h | 8 | 12.5% | 0.7543 | 1 | 100.0% | 0.0000 |
| Or | 7j | 4 | 0.0% | 1.0000 | 0 | — | — |
| Pétrole (Brent) | 24h | 11 | 27.3% | 0.5015 | 5 | 40.0% | 0.5701 |
| Pétrole (Brent) | 7j | 8 | 0.0% | 0.7766 | 3 | 0.0% | 0.9186 |
| S&P 500 | 24h | 6 | 100.0% | 0.0983 | 0 | — | — |
| S&P 500 | 7j | 3 | 0.0% | 0.9045 | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 5 | 80.0% | 0.2684 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+6.01 pts** sur 15 cellules
