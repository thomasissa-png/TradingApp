# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 1 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 4 | 75.0% | 0.2994 | 0 | — | — |
| Argent | 7j | 2 | 100.0% | 0.0000 | 0 | — | — |
| Blé | 24h | 3 | 33.3% | 0.2176 | 1 | 100.0% | 0.0397 |
| Blé | 7j | 0 | — | — | 0 | — | — |
| CAC 40 | 24h | 1 | 0.0% | 0.3505 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 5 | 80.0% | 0.2000 | 5 | 80.0% | 0.2027 |
| Cacao | 7j | 2 | 100.0% | 0.0000 | 2 | 100.0% | 0.0000 |
| Café (Arabica) | 24h | 6 | 100.0% | 0.0996 | 6 | 100.0% | 0.0978 |
| Café (Arabica) | 7j | 2 | 100.0% | 0.1483 | 2 | 100.0% | 0.0796 |
| Coton | 24h | 0 | — | — | 0 | — | — |
| Cuivre | 24h | 3 | 33.3% | 0.3746 | 2 | 50.0% | 0.1918 |
| Cuivre | 7j | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0000 |
| EUR/USD | 24h | 3 | 0.0% | 1.0000 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 5 | 0.0% | 0.6229 | 3 | 0.0% | 0.6314 |
| Nasdaq | 7j | 1 | 0.0% | 1.0000 | 1 | 0.0% | 1.0000 |
| Or | 24h | 5 | 100.0% | 0.0014 | 3 | 100.0% | 0.0000 |
| Or | 7j | 2 | 100.0% | 0.0000 | 2 | 100.0% | 0.0000 |
| Pétrole (Brent) | 24h | 3 | 100.0% | 0.0962 | 0 | — | — |
| Pétrole (Brent) | 7j | 2 | 100.0% | 0.0167 | 1 | 100.0% | 0.0171 |
| S&P 500 | 24h | 5 | 100.0% | 0.1178 | 0 | — | — |
| S&P 500 | 7j | 1 | 0.0% | 1.0000 | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| VIX | 24h | 4 | 100.0% | 0.2234 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+6.95 pts** sur 12 cellules
