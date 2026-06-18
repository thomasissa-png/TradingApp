# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-18T07:26:43.869205+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 15 | 33.3% | 0.5588 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 8 | 50.0% | 0.3995 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 13 | 38.5% | 0.3076 | 0 | — | — |
| Blé | 7j | 7 | 85.7% | 0.2476 | 0 | — | — |
| CAC 40 | 24h | 14 | 42.9% | 0.2574 | 2 | 100.0% | 0.2457 |
| CAC 40 | 7j | 11 | 81.8% | 0.2324 | 2 | 100.0% | 0.2206 |
| Cacao | 24h | 13 | 76.9% | 0.2137 | 11 | 72.7% | 0.1939 |
| Cacao | 7j | 8 | 100.0% | 0.0982 | 8 | 100.0% | 0.0607 |
| Café (Arabica) | 24h | 0 | — | — | 0 | — | — |
| Café (Arabica) | 7j | 0 | — | — | 0 | — | — |
| Cuivre | 24h | 0 | — | — | 0 | — | — |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 0 | — | — | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 0 | — | — | 0 | — | — |
| Nasdaq | 7j | 0 | — | — | 0 | — | — |
| Or | 24h | 0 | — | — | 0 | — | — |
| Or | 7j | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 24h | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 7j | 0 | — | — | 0 | — | — |
| S&P 500 | 24h | 0 | — | — | 0 | — | — |
| S&P 500 | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 0 | — | — | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+14.63 pts** sur 6 cellules
