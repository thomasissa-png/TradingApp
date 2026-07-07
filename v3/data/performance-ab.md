# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 7 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 33.3% | 0.4723 | 0 | — | — |
| Argent | 7j | 5 | 20.0% | 0.6898 | 0 | — | — |
| Blé | 24h | 9 | 33.3% | 0.3004 | 1 | 0.0% | 0.6411 |
| Blé | 7j | 3 | 33.3% | 0.2780 | 1 | 100.0% | 0.2349 |
| CAC 40 | 24h | 8 | 0.0% | 0.4975 | 1 | 0.0% | 0.6475 |
| CAC 40 | 7j | 2 | 0.0% | 0.7415 | 0 | — | — |
| Cacao | 24h | 9 | 100.0% | 0.0204 | 9 | 100.0% | 0.0492 |
| Cacao | 7j | 6 | 100.0% | 0.0000 | 6 | 100.0% | 0.0000 |
| Café (Arabica) | 24h | 9 | 100.0% | 0.0664 | 9 | 100.0% | 0.0652 |
| Café (Arabica) | 7j | 6 | 100.0% | 0.0864 | 6 | 100.0% | 0.0447 |
| Coton | 24h | 3 | 0.0% | 0.3852 | 3 | 0.0% | 0.4353 |
| Coton | 7j | 0 | — | — | 0 | — | — |
| Cuivre | 24h | 6 | 66.7% | 0.2495 | 4 | 75.0% | 0.1891 |
| Cuivre | 7j | 2 | 0.0% | 0.8511 | 1 | 0.0% | 0.9370 |
| EUR/USD | 24h | 6 | 0.0% | 0.9409 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 7 | 14.3% | 0.5872 | 4 | 25.0% | 0.6398 |
| Nasdaq | 7j | 3 | 33.3% | 0.6744 | 3 | 33.3% | 0.6817 |
| Or | 24h | 8 | 12.5% | 0.8507 | 2 | 0.0% | 1.0000 |
| Or | 7j | 5 | 0.0% | 1.0000 | 2 | 0.0% | 1.0000 |
| Pétrole (Brent) | 24h | 4 | 75.0% | 0.3222 | 1 | 0.0% | 1.0000 |
| Pétrole (Brent) | 7j | 2 | 100.0% | 0.0167 | 1 | 100.0% | 0.0171 |
| S&P 500 | 24h | 9 | 100.0% | 0.0801 | 0 | — | — |
| S&P 500 | 7j | 4 | 0.0% | 0.8302 | 0 | — | — |
| Sucre | 24h | 4 | 100.0% | 0.0835 | 3 | 100.0% | 0.0681 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 3 | 33.3% | 0.3376 | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 7 | 100.0% | 0.2220 | 0 | — | — |
| VIX | 7j | 1 | 100.0% | 0.1924 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-2.07 pts** sur 17 cellules
