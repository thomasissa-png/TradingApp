# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 3 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 7 | 14.3% | 0.6057 | 0 | — | — |
| Argent | 7j | 2 | 0.0% | 1.0000 | 0 | — | — |
| Blé | 24h | 3 | 0.0% | 0.3269 | 0 | — | — |
| Blé | 7j | 0 | — | — | 0 | — | — |
| CAC 40 | 24h | 8 | 0.0% | 0.4975 | 1 | 0.0% | 0.6475 |
| CAC 40 | 7j | 1 | 0.0% | 0.5407 | 0 | — | — |
| Cacao | 24h | 7 | 57.1% | 0.3740 | 7 | 57.1% | 0.3489 |
| Cacao | 7j | 3 | 66.7% | 0.3333 | 3 | 66.7% | 0.3333 |
| Café (Arabica) | 24h | 8 | 87.5% | 0.1997 | 8 | 87.5% | 0.1984 |
| Café (Arabica) | 7j | 4 | 100.0% | 0.0886 | 4 | 100.0% | 0.0528 |
| Coton | 24h | 3 | 0.0% | 0.3852 | 3 | 0.0% | 0.4353 |
| Cuivre | 24h | 7 | 28.6% | 0.4397 | 5 | 40.0% | 0.4159 |
| Cuivre | 7j | 2 | 0.0% | 0.8511 | 1 | 0.0% | 0.9370 |
| EUR/USD | 24h | 8 | 0.0% | 0.8742 | 0 | — | — |
| EUR/USD | 7j | 2 | 0.0% | 1.0000 | 0 | — | — |
| Nasdaq | 24h | 4 | 25.0% | 0.4610 | 2 | 50.0% | 0.4881 |
| Nasdaq | 7j | 1 | 100.0% | 0.0233 | 1 | 100.0% | 0.0452 |
| Or | 24h | 8 | 12.5% | 0.8507 | 3 | 0.0% | 1.0000 |
| Or | 7j | 4 | 0.0% | 1.0000 | 2 | 0.0% | 1.0000 |
| Pétrole (Brent) | 24h | 5 | 60.0% | 0.3675 | 2 | 0.0% | 0.6376 |
| Pétrole (Brent) | 7j | 2 | 100.0% | 0.0167 | 1 | 100.0% | 0.0171 |
| S&P 500 | 24h | 5 | 100.0% | 0.1178 | 0 | — | — |
| S&P 500 | 7j | 2 | 0.0% | 1.0000 | 0 | — | — |
| Sucre | 24h | 1 | 100.0% | 0.2104 | 0 | — | — |
| USD/JPY | 24h | 4 | 25.0% | 0.5627 | 0 | — | — |
| VIX | 24h | 4 | 100.0% | 0.2234 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-2.58 pts** sur 14 cellules
