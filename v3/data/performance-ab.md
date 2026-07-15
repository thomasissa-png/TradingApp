# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 15 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 11 | 18.2% | 0.5401 | 0 | — | — |
| Argent | 7j | 7 | 28.6% | 0.5999 | 0 | — | — |
| Blé | 24h | 15 | 53.3% | 0.2169 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 11 | 72.7% | 0.1286 | 5 | 100.0% | 0.0819 |
| CAC 40 | 24h | 5 | 60.0% | 0.3466 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 2 | 50.0% | 0.2169 | 0 | — | — |
| Cacao | 24h | 13 | 76.9% | 0.2224 | 13 | 76.9% | 0.2253 |
| Cacao | 7j | 9 | 100.0% | 0.0000 | 9 | 100.0% | 0.0002 |
| Café (Arabica) | 24h | 15 | 80.0% | 0.2427 | 15 | 80.0% | 0.2419 |
| Café (Arabica) | 7j | 10 | 90.0% | 0.1518 | 10 | 90.0% | 0.1268 |
| Coton | 24h | 9 | 66.7% | 0.1990 | 5 | 40.0% | 0.2957 |
| Coton | 7j | 5 | 0.0% | 0.4595 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 14 | 35.7% | 0.4024 | 7 | 42.9% | 0.4427 |
| Cuivre | 7j | 9 | 0.0% | 0.5821 | 6 | 0.0% | 0.6980 |
| EUR/USD | 24h | 8 | 0.0% | 0.7845 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 9 | 11.1% | 0.5532 | 5 | 20.0% | 0.5770 |
| Nasdaq | 7j | 5 | 20.0% | 0.5624 | 4 | 25.0% | 0.5026 |
| Or | 24h | 13 | 38.5% | 0.4624 | 3 | 100.0% | 0.0000 |
| Or | 7j | 5 | 20.0% | 0.5882 | 4 | 25.0% | 0.4175 |
| Pétrole (Brent) | 24h | 14 | 42.9% | 0.4141 | 8 | 62.5% | 0.3964 |
| Pétrole (Brent) | 7j | 11 | 9.1% | 0.6380 | 5 | 20.0% | 0.6842 |
| S&P 500 | 24h | 11 | 100.0% | 0.0656 | 0 | — | — |
| S&P 500 | 7j | 6 | 16.7% | 0.6811 | 0 | — | — |
| Sucre | 24h | 5 | 20.0% | 0.5655 | 2 | 0.0% | 0.7575 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 3 | 0.0% | 0.4201 | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 8 | 87.5% | 0.2502 | 0 | — | — |
| VIX | 7j | 1 | 100.0% | 0.1924 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+5.67 pts** sur 18 cellules
