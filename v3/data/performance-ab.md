# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 29 juin 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 4 | 50.0% | 0.5022 | 0 | — | — |
| Blé | 24h | 4 | 100.0% | 0.1551 | 1 | 100.0% | 0.0397 |
| CAC 40 | 24h | 2 | 50.0% | 0.2500 | 0 | — | — |
| Cacao | 24h | 4 | 75.0% | 0.2500 | 4 | 75.0% | 0.2518 |
| Café (Arabica) | 24h | 3 | 33.3% | 0.3864 | 3 | 33.3% | 0.3882 |
| Cuivre | 24h | 3 | 33.3% | 0.3746 | 2 | 50.0% | 0.1918 |
| EUR/USD | 24h | 1 | 100.0% | 0.0000 | 0 | — | — |
| Nasdaq | 24h | 4 | 75.0% | 0.1007 | 2 | 100.0% | 0.0134 |
| Or | 24h | 3 | 33.3% | 0.6667 | 1 | 100.0% | 0.0000 |
| Pétrole (Brent) | 24h | 3 | 100.0% | 0.0962 | 0 | — | — |
| S&P 500 | 24h | 4 | 0.0% | 0.3743 | 0 | — | — |
| VIX | 24h | 1 | 0.0% | 0.3010 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+18.06 pts** sur 6 cellules
