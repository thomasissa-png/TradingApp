# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-04T07:07:54.683799+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 5 | 80.0% | 0.2101 | 2 | 50.0% | 0.2252 |
| Blé | 24h | 7 | 85.7% | 0.1812 | 2 | 100.0% | 0.0643 |
| CAC 40 | 24h | 3 | 100.0% | 0.2403 | 0 | — | — |
| Cacao | 24h | 2 | 100.0% | 0.2156 | 2 | 100.0% | 0.2156 |
| Café (Arabica) | 24h | 5 | 60.0% | 0.2493 | 5 | 60.0% | 0.2575 |
| Cuivre | 24h | 6 | 16.7% | 0.4286 | 6 | 16.7% | 0.3219 |
| EUR/USD | 24h | 2 | 100.0% | 0.2081 | 2 | 100.0% | 0.2081 |
| Nasdaq | 24h | 2 | 100.0% | 0.0324 | 2 | 100.0% | 0.0622 |
| Or | 24h | 7 | 42.9% | 0.2660 | 6 | 50.0% | 0.2291 |
| Pétrole (Brent) | 24h | 5 | 60.0% | 0.4142 | 4 | 50.0% | 0.3838 |
| S&P 500 | 24h | 4 | 25.0% | 0.2652 | 0 | — | — |
| VIX | 24h | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-2.06 pts** sur 9 cellules
