# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 22 juillet 2026, 07h30
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 19 | 21.1% | 0.4653 | 0 | — | — |
| Argent | 7j | 12 | 16.7% | 0.5907 | 0 | — | — |
| Blé | 24h | 19 | 63.2% | 0.1843 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 16 | 81.2% | 0.0938 | 6 | 100.0% | 0.0699 |
| CAC 40 | 24h | 5 | 60.0% | 0.3466 | 2 | 50.0% | 0.5343 |
| CAC 40 | 7j | 3 | 33.3% | 0.4779 | 1 | 0.0% | 1.0000 |
| Cacao | 24h | 20 | 55.0% | 0.3568 | 18 | 55.6% | 0.3330 |
| Cacao | 7j | 12 | 75.0% | 0.2500 | 12 | 75.0% | 0.2501 |
| Café (Arabica) | 24h | 18 | 72.2% | 0.2784 | 18 | 72.2% | 0.2666 |
| Café (Arabica) | 7j | 13 | 69.2% | 0.2508 | 13 | 69.2% | 0.2272 |
| Coton | 24h | 11 | 27.3% | 0.3520 | 3 | 0.0% | 0.4353 |
| Coton | 7j | 3 | 0.0% | 0.5528 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 20 | 55.0% | 0.3098 | 8 | 50.0% | 0.3874 |
| Cuivre | 7j | 16 | 18.8% | 0.4871 | 10 | 20.0% | 0.5703 |
| EUR/USD | 24h | 9 | 0.0% | 0.6373 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 13 | 46.1% | 0.4046 | 6 | 33.3% | 0.5224 |
| Nasdaq | 7j | 6 | 83.3% | 0.1750 | 5 | 80.0% | 0.1808 |
| Or | 24h | 16 | 25.0% | 0.5935 | 6 | 16.7% | 0.6322 |
| Or | 7j | 10 | 0.0% | 0.8163 | 5 | 0.0% | 0.8394 |
| Pétrole (Brent) | 24h | 20 | 60.0% | 0.2937 | 14 | 78.6% | 0.2446 |
| Pétrole (Brent) | 7j | 16 | 37.5% | 0.4449 | 7 | 42.9% | 0.4887 |
| S&P 500 | 24h | 15 | 66.7% | 0.3229 | 0 | — | — |
| S&P 500 | 7j | 5 | 20.0% | 0.6979 | 0 | — | — |
| Sucre | 24h | 6 | 33.3% | 0.4894 | 2 | 0.0% | 0.7575 |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 15 | 40.0% | 0.3165 | 2 | 50.0% | 0.3232 |
| USD/JPY | 7j | 1 | 100.0% | 0.0754 | 0 | — | — |
| VIX | 24h | 11 | 81.8% | 0.2788 | 1 | 100.0% | 0.2215 |
| VIX | 7j | 1 | 100.0% | 0.1924 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-2.73 pts** sur 21 cellules
