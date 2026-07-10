# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 10 juillet 2026, 07h31
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 10 | 20.0% | 0.5256 | 0 | — | — |
| Argent | 7j | 8 | 25.0% | 0.6239 | 0 | — | — |
| Blé | 24h | 11 | 36.4% | 0.2764 | 2 | 50.0% | 0.3206 |
| Blé | 7j | 9 | 66.7% | 0.1572 | 3 | 100.0% | 0.1365 |
| CAC 40 | 24h | 9 | 77.8% | 0.2419 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 2 | 50.0% | 0.1750 | 0 | — | — |
| Cacao | 24h | 12 | 100.0% | 0.0153 | 12 | 100.0% | 0.0369 |
| Cacao | 7j | 9 | 100.0% | 0.0000 | 9 | 100.0% | 0.0002 |
| Café (Arabica) | 24h | 11 | 90.9% | 0.1213 | 11 | 90.9% | 0.1198 |
| Café (Arabica) | 7j | 9 | 100.0% | 0.0576 | 9 | 100.0% | 0.0298 |
| Coton | 24h | 5 | 40.0% | 0.3159 | 3 | 0.0% | 0.4353 |
| Coton | 7j | 4 | 0.0% | 0.5016 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 11 | 36.4% | 0.3903 | 5 | 40.0% | 0.4159 |
| Cuivre | 7j | 7 | 0.0% | 0.6375 | 6 | 0.0% | 0.6980 |
| EUR/USD | 24h | 6 | 0.0% | 0.9409 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 9 | 11.1% | 0.5661 | 4 | 25.0% | 0.6398 |
| Nasdaq | 7j | 4 | 25.0% | 0.7006 | 4 | 25.0% | 0.6694 |
| Or | 24h | 9 | 11.1% | 0.8058 | 2 | 0.0% | 1.0000 |
| Or | 7j | 7 | 0.0% | 0.8702 | 2 | 0.0% | 0.8450 |
| Pétrole (Brent) | 24h | 9 | 22.2% | 0.6251 | 5 | 20.0% | 0.7134 |
| Pétrole (Brent) | 7j | 7 | 0.0% | 0.7011 | 2 | 0.0% | 1.0000 |
| S&P 500 | 24h | 11 | 100.0% | 0.0656 | 0 | — | — |
| S&P 500 | 7j | 4 | 0.0% | 0.8302 | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 8 | 87.5% | 0.2502 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-0.98 pts** sur 17 cellules
