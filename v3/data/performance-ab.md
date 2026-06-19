# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-19T08:11:24.159406+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 13 | 69.2% | 0.2025 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 10 | 80.0% | 0.1196 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 14 | 50.0% | 0.2695 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 8 | 75.0% | 0.2956 | 0 | — | — |
| CAC 40 | 24h | 14 | 42.9% | 0.2574 | 2 | 100.0% | 0.2457 |
| CAC 40 | 7j | 12 | 83.3% | 0.2271 | 2 | 100.0% | 0.2206 |
| Cacao | 24h | 13 | 76.9% | 0.2137 | 11 | 72.7% | 0.1939 |
| Cacao | 7j | 10 | 90.0% | 0.1130 | 9 | 88.9% | 0.0856 |
| Café (Arabica) | 24h | 12 | 0.0% | 0.4652 | 12 | 0.0% | 0.4119 |
| Café (Arabica) | 7j | 9 | 0.0% | 0.6092 | 9 | 0.0% | 0.4791 |
| Cuivre | 24h | 10 | 50.0% | 0.3637 | 5 | 20.0% | 0.3691 |
| Cuivre | 7j | 2 | 100.0% | 0.2346 | 0 | — | — |
| EUR/USD | 24h | 13 | 100.0% | 0.0365 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 11 | 90.9% | 0.0583 | 2 | 50.0% | 0.2559 |
| Nasdaq | 24h | 9 | 33.3% | 0.6657 | 7 | 28.6% | 0.6666 |
| Nasdaq | 7j | 6 | 0.0% | 1.0000 | 5 | 0.0% | 1.0000 |
| Or | 24h | 15 | 93.3% | 0.1155 | 11 | 90.9% | 0.1287 |
| Or | 7j | 10 | 90.0% | 0.1319 | 7 | 85.7% | 0.1664 |
| Pétrole (Brent) | 24h | 14 | 35.7% | 0.5308 | 9 | 22.2% | 0.5029 |
| Pétrole (Brent) | 7j | 12 | 33.3% | 0.5543 | 5 | 0.0% | 0.8305 |
| S&P 500 | 24h | 15 | 26.7% | 0.3512 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 11 | 27.3% | 0.5695 | 2 | 0.0% | 0.6115 |
| VIX | 24h | 13 | 23.1% | 0.4066 | 3 | 66.7% | 0.2865 |
| VIX | 7j | 3 | 0.0% | 0.5033 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-3.35 pts** sur 21 cellules
