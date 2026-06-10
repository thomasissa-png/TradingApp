# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-10T07:21:29.166735+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 88.9% | 0.1164 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 4 | 50.0% | 0.2464 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 8 | 100.0% | 0.1719 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 3 | 100.0% | 0.0950 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 1 | 0.0% | 0.3697 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 7 | 28.6% | 0.2966 | 6 | 33.3% | 0.2811 |
| Cacao | 7j | 1 | 0.0% | 0.6136 | 1 | 0.0% | 0.8798 |
| Café (Arabica) | 24h | 4 | 50.0% | 0.2595 | 4 | 50.0% | 0.2662 |
| Café (Arabica) | 7j | 3 | 33.3% | 0.3558 | 3 | 33.3% | 0.3743 |
| Cuivre | 24h | 6 | 33.3% | 0.4501 | 5 | 20.0% | 0.3691 |
| Cuivre | 7j | 1 | 100.0% | 0.2317 | 0 | — | — |
| EUR/USD | 24h | 4 | 100.0% | 0.1087 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 50.0% | 0.2559 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 7 | 71.4% | 0.2978 | 3 | 33.3% | 0.4200 |
| Nasdaq | 7j | 4 | 75.0% | 0.3283 | 4 | 75.0% | 0.3049 |
| Or | 24h | 9 | 100.0% | 0.0814 | 6 | 100.0% | 0.0684 |
| Or | 7j | 4 | 100.0% | 0.0562 | 4 | 100.0% | 0.0413 |
| Pétrole (Brent) | 24h | 8 | 12.5% | 0.6750 | 5 | 0.0% | 0.6420 |
| Pétrole (Brent) | 7j | 1 | 0.0% | 1.0000 | 1 | 0.0% | 1.0000 |
| S&P 500 | 24h | 6 | 16.7% | 0.3240 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 4 | 50.0% | 0.3733 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 5 | 60.0% | 0.1734 | 2 | 50.0% | 0.1869 |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-8.74 pts** sur 20 cellules
