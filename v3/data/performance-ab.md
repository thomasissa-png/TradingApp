# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 8 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 33.3% | 0.4723 | 0 | — | — |
| Argent | 7j | 6 | 16.7% | 0.6651 | 0 | — | — |
| Blé | 24h | 10 | 40.0% | 0.2704 | 2 | 50.0% | 0.3206 |
| Blé | 7j | 7 | 57.1% | 0.1847 | 3 | 100.0% | 0.1365 |
| CAC 40 | 24h | 6 | 16.7% | 0.4974 | 1 | 0.0% | 0.6475 |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 10 | 100.0% | 0.0183 | 10 | 100.0% | 0.0442 |
| Cacao | 7j | 7 | 100.0% | 0.0000 | 7 | 100.0% | 0.0000 |
| Café (Arabica) | 24h | 10 | 90.0% | 0.1598 | 10 | 90.0% | 0.1587 |
| Café (Arabica) | 7j | 7 | 100.0% | 0.0740 | 7 | 100.0% | 0.0383 |
| Coton | 24h | 5 | 40.0% | 0.3159 | 3 | 0.0% | 0.4353 |
| Coton | 7j | 3 | 0.0% | 0.5528 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 5 | 60.0% | 0.2554 | 4 | 75.0% | 0.1891 |
| Cuivre | 7j | 2 | 0.0% | 0.8511 | 1 | 0.0% | 0.9370 |
| EUR/USD | 24h | 5 | 0.0% | 0.8027 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 5 | 40.0% | 0.3721 | 3 | 33.3% | 0.4340 |
| Nasdaq | 7j | 3 | 66.7% | 0.2675 | 3 | 66.7% | 0.2259 |
| Or | 24h | 8 | 12.5% | 0.8507 | 2 | 0.0% | 1.0000 |
| Or | 7j | 5 | 0.0% | 1.0000 | 1 | 0.0% | 1.0000 |
| Pétrole (Brent) | 24h | 8 | 25.0% | 0.5782 | 4 | 25.0% | 0.6636 |
| Pétrole (Brent) | 7j | 5 | 0.0% | 0.7090 | 1 | 0.0% | 1.0000 |
| S&P 500 | 24h | 6 | 100.0% | 0.1202 | 0 | — | — |
| S&P 500 | 7j | 3 | 0.0% | 0.9045 | 0 | — | — |
| Sucre | 24h | 4 | 100.0% | 0.0835 | 3 | 100.0% | 0.0681 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 2 | 50.0% | 0.1497 | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 6 | 100.0% | 0.2212 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-0.44 pts** sur 18 cellules
