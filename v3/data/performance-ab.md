# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-11T07:25:58.766058+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 10 | 90.0% | 0.1048 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 5 | 60.0% | 0.2309 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 5 | 100.0% | 0.1429 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 4 | 100.0% | 0.1281 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 6 | 100.0% | 0.2370 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 7 | 0.0% | 0.3541 | 6 | 0.0% | 0.3725 |
| Cacao | 7j | 4 | 0.0% | 0.6123 | 3 | 0.0% | 0.5904 |
| Café (Arabica) | 24h | 5 | 60.0% | 0.2487 | 5 | 60.0% | 0.2570 |
| Café (Arabica) | 7j | 4 | 50.0% | 0.3131 | 4 | 50.0% | 0.3376 |
| Cuivre | 24h | 8 | 37.5% | 0.4381 | 6 | 16.7% | 0.3800 |
| Cuivre | 7j | 4 | 100.0% | 0.2069 | 2 | 100.0% | 0.1792 |
| EUR/USD | 24h | 4 | 100.0% | 0.1087 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 50.0% | 0.2559 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 10 | 80.0% | 0.2085 | 6 | 66.7% | 0.2152 |
| Nasdaq | 7j | 5 | 80.0% | 0.2775 | 4 | 75.0% | 0.3049 |
| Or | 24h | 10 | 100.0% | 0.0732 | 7 | 100.0% | 0.0586 |
| Or | 7j | 5 | 100.0% | 0.0614 | 4 | 100.0% | 0.0413 |
| Pétrole (Brent) | 24h | 6 | 50.0% | 0.4337 | 4 | 50.0% | 0.3898 |
| Pétrole (Brent) | 7j | 3 | 33.3% | 0.4221 | 2 | 50.0% | 0.5007 |
| S&P 500 | 24h | 10 | 30.0% | 0.3124 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 5 | 40.0% | 0.3895 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 10 | 80.0% | 0.1347 | 2 | 50.0% | 0.1869 |
| VIX | 7j | 2 | 50.0% | 0.2536 | 2 | 50.0% | 0.2536 |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-7.84 pts** sur 22 cellules
