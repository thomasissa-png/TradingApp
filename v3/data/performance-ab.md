# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 21 juillet 2026, 07h29
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 13 | 23.1% | 0.5340 | 0 | — | — |
| Argent | 7j | 8 | 37.5% | 0.5508 | 0 | — | — |
| Blé | 24h | 18 | 55.6% | 0.2049 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 15 | 80.0% | 0.1000 | 6 | 100.0% | 0.0699 |
| CAC 40 | 24h | 10 | 80.0% | 0.2336 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 2 | 50.0% | 0.2169 | 0 | — | — |
| Cacao | 24h | 18 | 61.1% | 0.3575 | 16 | 62.5% | 0.3388 |
| Cacao | 7j | 14 | 64.3% | 0.3278 | 14 | 64.3% | 0.3198 |
| Café (Arabica) | 24h | 17 | 70.6% | 0.2834 | 17 | 70.6% | 0.2821 |
| Café (Arabica) | 7j | 12 | 75.0% | 0.2392 | 12 | 75.0% | 0.2176 |
| Coton | 24h | 12 | 16.7% | 0.4606 | 5 | 0.0% | 0.4941 |
| Coton | 7j | 2 | 0.0% | 0.6145 | 1 | 0.0% | 0.8823 |
| Cuivre | 24h | 18 | 50.0% | 0.3416 | 8 | 50.0% | 0.3874 |
| Cuivre | 7j | 14 | 7.1% | 0.5552 | 9 | 11.1% | 0.6337 |
| EUR/USD | 24h | 8 | 0.0% | 0.8498 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 17 | 70.6% | 0.2179 | 7 | 57.1% | 0.2450 |
| Nasdaq | 7j | 12 | 91.7% | 0.1307 | 10 | 90.0% | 0.1283 |
| Or | 24h | 14 | 21.4% | 0.5824 | 5 | 40.0% | 0.3587 |
| Or | 7j | 8 | 25.0% | 0.6424 | 5 | 40.0% | 0.3647 |
| Pétrole (Brent) | 24h | 19 | 52.6% | 0.3618 | 13 | 69.2% | 0.3293 |
| Pétrole (Brent) | 7j | 15 | 33.3% | 0.4745 | 7 | 42.9% | 0.4887 |
| S&P 500 | 24h | 15 | 26.7% | 0.6541 | 0 | — | — |
| S&P 500 | 7j | 7 | 28.6% | 0.5059 | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 10 | 90.0% | 0.1734 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+2.02 pts** sur 17 cellules
