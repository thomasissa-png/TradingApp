# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-08T07:05:58.329589+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 20 | 95.0% | 0.1277 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 2 | 50.0% | 0.2431 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 18 | 33.3% | 0.2341 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 2 | 100.0% | 0.0286 | 2 | 100.0% | 0.0667 |
| CAC 40 | 24h | 7 | 42.9% | 0.2937 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 17 | 0.0% | 0.3717 | 14 | 0.0% | 0.3996 |
| Cacao | 7j | 2 | 0.0% | 0.4218 | 2 | 0.0% | 0.4457 |
| Café (Arabica) | 24h | 11 | 81.8% | 0.2257 | 11 | 81.8% | 0.2372 |
| Café (Arabica) | 7j | 2 | 0.0% | 0.4410 | 2 | 0.0% | 0.4476 |
| Cuivre | 24h | 18 | 5.6% | 0.5475 | 18 | 5.6% | 0.4074 |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 15 | 100.0% | 0.0360 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 2 | 50.0% | 0.2559 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 20 | 90.0% | 0.1912 | 9 | 77.8% | 0.1671 |
| Nasdaq | 7j | 2 | 50.0% | 0.5025 | 2 | 50.0% | 0.4991 |
| Or | 24h | 19 | 100.0% | 0.1411 | 15 | 100.0% | 0.1233 |
| Or | 7j | 2 | 100.0% | 0.0308 | 2 | 100.0% | 0.0286 |
| Pétrole (Brent) | 24h | 14 | 92.9% | 0.1271 | 9 | 88.9% | 0.1294 |
| Pétrole (Brent) | 7j | 2 | 100.0% | 0.0005 | 2 | 100.0% | 0.0133 |
| S&P 500 | 24h | 20 | 5.0% | 0.4269 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 2 | 0.0% | 0.6115 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 17 | 64.7% | 0.1687 | 2 | 50.0% | 0.1869 |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-0.71 pts** sur 20 cellules
