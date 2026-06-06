# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-06T07:06:52.489566+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 15 | 93.3% | 0.1545 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 0 | — | — | 0 | — | — |
| Blé | 24h | 12 | 50.0% | 0.2155 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 0 | — | — | 0 | — | — |
| CAC 40 | 24h | 4 | 0.0% | 0.3689 | 0 | — | — |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 14 | 0.0% | 0.3727 | 11 | 0.0% | 0.3947 |
| Cacao | 7j | 0 | — | — | 0 | — | — |
| Café (Arabica) | 24h | 11 | 81.8% | 0.2257 | 11 | 81.8% | 0.2372 |
| Café (Arabica) | 7j | 0 | — | — | 0 | — | — |
| Cuivre | 24h | 14 | 7.1% | 0.5441 | 14 | 7.1% | 0.4008 |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 11 | 100.0% | 0.0460 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 15 | 86.7% | 0.2532 | 4 | 50.0% | 0.3368 |
| Nasdaq | 7j | 0 | — | — | 0 | — | — |
| Or | 24h | 15 | 100.0% | 0.1547 | 13 | 100.0% | 0.1279 |
| Or | 7j | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 24h | 13 | 15.4% | 0.6015 | 7 | 14.3% | 0.6866 |
| Pétrole (Brent) | 7j | 0 | — | — | 0 | — | — |
| S&P 500 | 24h | 15 | 6.7% | 0.4527 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 13 | 76.9% | 0.1522 | 2 | 50.0% | 0.1869 |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-5.88 pts** sur 11 cellules
