# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-01T08:17:49.964712+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 0 | — | — | 0 | — | — |
| Blé | 24h | 1 | 0.0% | 1.0000 | 1 | 0.0% | 0.5535 |
| CAC 40 | 24h | 0 | — | — | 0 | — | — |
| Cacao | 24h | 0 | — | — | 0 | — | — |
| Café (Arabica) | 24h | 0 | — | — | 0 | — | — |
| Cuivre | 24h | 1 | 0.0% | 0.2746 | 1 | 0.0% | 0.2746 |
| EUR/USD | 24h | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 0 | — | — | 0 | — | — |
| Or | 24h | 1 | 100.0% | 0.0040 | 1 | 100.0% | 0.0064 |
| Pétrole (Brent) | 24h | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0013 |
| S&P 500 | 24h | 0 | — | — | 0 | — | — |
| VIX | 24h | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+0.00 pts** sur 4 cellules
