# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-03T22:04:03.969767+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 4 | 75.0% | 0.2277 | 2 | 50.0% | 0.2252 |
| Blé | 24h | 4 | 100.0% | 0.1293 | 2 | 100.0% | 0.0643 |
| CAC 40 | 24h | 2 | 100.0% | 0.2401 | 0 | — | — |
| Cacao | 24h | 2 | 100.0% | 0.2156 | 2 | 100.0% | 0.2156 |
| Café (Arabica) | 24h | 3 | 33.3% | 0.2780 | 3 | 33.3% | 0.2824 |
| Cuivre | 24h | 3 | 33.3% | 0.2947 | 3 | 33.3% | 0.2634 |
| EUR/USD | 24h | 2 | 100.0% | 0.2081 | 2 | 100.0% | 0.2081 |
| Nasdaq | 24h | 2 | 100.0% | 0.0324 | 2 | 100.0% | 0.0622 |
| Or | 24h | 4 | 100.0% | 0.1160 | 4 | 100.0% | 0.0872 |
| Pétrole (Brent) | 24h | 4 | 100.0% | 0.0547 | 3 | 100.0% | 0.0496 |
| S&P 500 | 24h | 2 | 50.0% | 0.1784 | 0 | — | — |
| VIX | 24h | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-2.78 pts** sur 9 cellules
