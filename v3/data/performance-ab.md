# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-08T16:28:24.152030+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 20 | 95.0% | 0.1277 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 2 | 50.0% | 0.2431 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 8 | 75.0% | 0.1916 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 2 | 100.0% | 0.0286 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 6 | 50.0% | 0.2817 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 19 | 10.5% | 0.3495 | 16 | 12.5% | 0.3677 |
| Cacao | 7j | 0 | — | — | 0 | — | — |
| Café (Arabica) | 24h | 12 | 75.0% | 0.2396 | 12 | 75.0% | 0.2440 |
| Café (Arabica) | 7j | 2 | 0.0% | 0.4410 | 2 | 0.0% | 0.4476 |
| Cuivre | 24h | 16 | 12.5% | 0.5047 | 16 | 12.5% | 0.3812 |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 15 | 100.0% | 0.0360 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 50.0% | 0.2559 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 20 | 85.0% | 0.2399 | 9 | 66.7% | 0.2516 |
| Nasdaq | 7j | 2 | 50.0% | 0.5025 | 2 | 50.0% | 0.4991 |
| Or | 24h | 19 | 100.0% | 0.1411 | 15 | 100.0% | 0.1233 |
| Or | 7j | 2 | 100.0% | 0.0308 | 2 | 100.0% | 0.0286 |
| Pétrole (Brent) | 24h | 14 | 35.7% | 0.5181 | 9 | 33.3% | 0.5460 |
| Pétrole (Brent) | 7j | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0013 |
| S&P 500 | 24h | 21 | 9.5% | 0.4120 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 2 | 0.0% | 0.6115 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 5 | 40.0% | 0.2016 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-2.68 pts** sur 18 cellules
