# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-04T14:58:39.294048+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 6 | 50.0% | 0.3306 | 1 | 100.0% | 0.1464 |
| Blé | 24h | 6 | 100.0% | 0.1676 | 2 | 100.0% | 0.0643 |
| CAC 40 | 24h | 6 | 33.3% | 0.3082 | 2 | 100.0% | 0.2457 |
| Cacao | 24h | 6 | 0.0% | 0.3644 | 6 | 0.0% | 0.4148 |
| Café (Arabica) | 24h | 6 | 66.7% | 0.2421 | 6 | 66.7% | 0.2513 |
| Cuivre | 24h | 5 | 20.0% | 0.3974 | 5 | 20.0% | 0.3065 |
| EUR/USD | 24h | 3 | 0.0% | 0.7945 | 0 | — | — |
| Nasdaq | 24h | 2 | 100.0% | 0.0324 | 2 | 100.0% | 0.0622 |
| Or | 24h | 6 | 16.7% | 0.3291 | 5 | 20.0% | 0.3287 |
| Pétrole (Brent) | 24h | 9 | 33.3% | 0.6460 | 8 | 25.0% | 0.6059 |
| S&P 500 | 24h | 4 | 25.0% | 0.2652 | 0 | — | — |
| VIX | 24h | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+12.41 pts** sur 9 cellules
