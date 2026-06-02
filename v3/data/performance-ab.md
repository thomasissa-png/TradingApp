# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-02T12:31:00.184533+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 2 | 50.0% | 0.2912 | 2 | 50.0% | 0.2912 |
| Blé | 24h | 2 | 100.0% | 0.0146 | 2 | 100.0% | 0.0643 |
| CAC 40 | 24h | 0 | — | — | 0 | — | — |
| Cacao | 24h | 0 | — | — | 0 | — | — |
| Café (Arabica) | 24h | 2 | 0.0% | 0.3128 | 2 | 0.0% | 0.3122 |
| Cuivre | 24h | 2 | 50.0% | 0.1662 | 2 | 50.0% | 0.2094 |
| EUR/USD | 24h | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 0 | — | — | 0 | — | — |
| Or | 24h | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 24h | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0364 |
| S&P 500 | 24h | 0 | — | — | 0 | — | — |
| VIX | 24h | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+0.00 pts** sur 5 cellules
