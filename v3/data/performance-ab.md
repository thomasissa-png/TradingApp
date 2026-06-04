# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-04T20:35:19.961135+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 5 | 80.0% | 0.2442 | 1 | 100.0% | 0.1464 |
| Blé | 24h | 9 | 66.7% | 0.1993 | 2 | 100.0% | 0.0643 |
| CAC 40 | 24h | 6 | 33.3% | 0.3082 | 2 | 100.0% | 0.2457 |
| Cacao | 24h | 6 | 0.0% | 0.3644 | 6 | 0.0% | 0.4148 |
| Café (Arabica) | 24h | 7 | 71.4% | 0.2369 | 7 | 71.4% | 0.2469 |
| Cuivre | 24h | 6 | 33.3% | 0.3407 | 6 | 33.3% | 0.2737 |
| EUR/USD | 24h | 2 | 100.0% | 0.2081 | 2 | 100.0% | 0.2081 |
| Nasdaq | 24h | 0 | — | — | 0 | — | — |
| Or | 24h | 7 | 42.9% | 0.2660 | 6 | 50.0% | 0.2291 |
| Pétrole (Brent) | 24h | 9 | 33.3% | 0.6460 | 8 | 25.0% | 0.6059 |
| S&P 500 | 24h | 1 | 100.0% | 0.0356 | 0 | — | — |
| VIX | 24h | 1 | 0.0% | 0.4312 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+13.20 pts** sur 9 cellules
