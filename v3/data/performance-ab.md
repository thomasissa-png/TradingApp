# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2 juillet 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 7 | 28.6% | 0.4574 | 0 | — | — |
| Argent | 7j | 3 | 66.7% | 0.3333 | 0 | — | — |
| Blé | 24h | 6 | 16.7% | 0.2771 | 0 | — | — |
| Blé | 7j | 0 | — | — | 0 | — | — |
| CAC 40 | 24h | 5 | 100.0% | 0.1188 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 5 | 80.0% | 0.2000 | 5 | 80.0% | 0.2027 |
| Cacao | 7j | 2 | 100.0% | 0.0000 | 2 | 100.0% | 0.0000 |
| Café (Arabica) | 24h | 7 | 100.0% | 0.0854 | 7 | 100.0% | 0.0838 |
| Café (Arabica) | 7j | 3 | 100.0% | 0.1082 | 3 | 100.0% | 0.0615 |
| Coton | 24h | 3 | 0.0% | 0.3852 | 3 | 0.0% | 0.4353 |
| Cuivre | 24h | 3 | 33.3% | 0.3746 | 2 | 50.0% | 0.1918 |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 1 | 100.0% | 0.0000 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 6 | 0.0% | 0.6746 | 3 | 0.0% | 0.7874 |
| Nasdaq | 7j | 3 | 33.3% | 0.6744 | 3 | 33.3% | 0.6817 |
| Or | 24h | 5 | 20.0% | 0.7627 | 1 | 100.0% | 0.0000 |
| Or | 7j | 1 | 0.0% | 1.0000 | 0 | — | — |
| Pétrole (Brent) | 24h | 7 | 71.4% | 0.1765 | 2 | 50.0% | 0.1376 |
| Pétrole (Brent) | 7j | 2 | 100.0% | 0.0167 | 1 | 100.0% | 0.0171 |
| S&P 500 | 24h | 5 | 100.0% | 0.1178 | 0 | — | — |
| S&P 500 | 7j | 2 | 0.0% | 1.0000 | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| VIX | 24h | 4 | 100.0% | 0.2234 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+6.84 pts** sur 11 cellules
