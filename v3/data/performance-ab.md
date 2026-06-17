# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-17T07:26:05.570460+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 12 | 41.7% | 0.5664 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 10 | 40.0% | 0.5196 | 2 | 50.0% | 0.2431 |
| Blé | 24h | 13 | 61.5% | 0.2673 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 5 | 100.0% | 0.1716 | 0 | — | — |
| CAC 40 | 24h | 14 | 42.9% | 0.2574 | 2 | 100.0% | 0.2457 |
| CAC 40 | 7j | 10 | 80.0% | 0.2438 | 2 | 100.0% | 0.2206 |
| Cacao | 24h | 13 | 76.9% | 0.2137 | 11 | 72.7% | 0.1939 |
| Cacao | 7j | 7 | 100.0% | 0.0866 | 7 | 100.0% | 0.0440 |
| Café (Arabica) | 24h | 13 | 15.4% | 0.4262 | 13 | 15.4% | 0.3751 |
| Café (Arabica) | 7j | 7 | 0.0% | 0.4975 | 7 | 0.0% | 0.3302 |
| Cuivre | 24h | 11 | 45.5% | 0.2304 | 7 | 71.4% | 0.1795 |
| Cuivre | 7j | 6 | 0.0% | 0.3023 | 2 | 0.0% | 0.3419 |
| EUR/USD | 24h | 9 | 22.2% | 0.7672 | 2 | 100.0% | 0.2081 |
| EUR/USD | 7j | 1 | 0.0% | 1.0000 | 0 | — | — |
| Nasdaq | 24h | 14 | 35.7% | 0.5926 | 10 | 20.0% | 0.6175 |
| Nasdaq | 7j | 7 | 42.9% | 0.6261 | 5 | 40.0% | 0.6443 |
| Or | 24h | 9 | 66.7% | 0.4020 | 6 | 66.7% | 0.3920 |
| Or | 7j | 7 | 85.7% | 0.1885 | 5 | 80.0% | 0.2330 |
| Pétrole (Brent) | 24h | 14 | 35.7% | 0.5308 | 9 | 22.2% | 0.5029 |
| Pétrole (Brent) | 7j | 10 | 20.0% | 0.6512 | 5 | 0.0% | 0.8305 |
| S&P 500 | 24h | 14 | 28.6% | 0.3129 | 2 | 0.0% | 0.3577 |
| S&P 500 | 7j | 6 | 33.3% | 0.5788 | 0 | — | — |
| VIX | 24h | 13 | 23.1% | 0.4066 | 3 | 66.7% | 0.2865 |
| VIX | 7j | 3 | 0.0% | 0.4370 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+9.54 pts** sur 20 cellules
