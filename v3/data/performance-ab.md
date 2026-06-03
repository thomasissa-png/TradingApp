# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-03T07:05:43.296187+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 2 | 100.0% | 0.1976 | 1 | 100.0% | 0.1464 |
| Blé | 24h | 3 | 100.0% | 0.0911 | 2 | 100.0% | 0.0643 |
| CAC 40 | 24h | 0 | — | — | 0 | — | — |
| Cacao | 24h | 2 | 100.0% | 0.2156 | 2 | 100.0% | 0.2156 |
| Café (Arabica) | 24h | 2 | 0.0% | 0.3128 | 2 | 0.0% | 0.3122 |
| Cuivre | 24h | 2 | 50.0% | 0.1662 | 2 | 50.0% | 0.2094 |
| EUR/USD | 24h | 1 | 100.0% | 0.2203 | 1 | 100.0% | 0.2203 |
| Nasdaq | 24h | 2 | 100.0% | 0.0324 | 2 | 100.0% | 0.0622 |
| Or | 24h | 3 | 100.0% | 0.1123 | 3 | 100.0% | 0.0855 |
| Pétrole (Brent) | 24h | 3 | 100.0% | 0.0666 | 2 | 100.0% | 0.0390 |
| S&P 500 | 24h | 2 | 100.0% | 0.1650 | 2 | 100.0% | 0.1650 |
| VIX | 24h | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+0.00 pts** sur 10 cellules
