# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 23 juillet 2026, 07h27
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 18 | 22.2% | 0.4745 | 0 | — | — |
| Argent | 7j | 13 | 15.4% | 0.5773 | 0 | — | — |
| Argent | 1m | 0 | — | — | 0 | — | — |
| Blé | 24h | 21 | 66.7% | 0.1841 | 3 | 66.7% | 0.2137 |
| Blé | 7j | 17 | 82.3% | 0.0882 | 6 | 100.0% | 0.0699 |
| Blé | 1m | 1 | 0.0% | 0.3188 | 0 | — | — |
| CAC 40 | 24h | 15 | 0.0% | 0.5937 | 5 | 0.0% | 0.7136 |
| CAC 40 | 7j | 3 | 0.0% | 0.9929 | 3 | 0.0% | 0.9406 |
| CAC 40 | 1m | 0 | — | — | 0 | — | — |
| Cacao | 24h | 20 | 65.0% | 0.3179 | 19 | 63.2% | 0.3238 |
| Cacao | 7j | 16 | 56.2% | 0.3930 | 15 | 53.3% | 0.3890 |
| Cacao | 1m | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0000 |
| Café (Arabica) | 24h | 20 | 65.0% | 0.2874 | 20 | 65.0% | 0.2878 |
| Café (Arabica) | 7j | 13 | 61.5% | 0.2760 | 13 | 61.5% | 0.2690 |
| Café (Arabica) | 1m | 1 | 100.0% | 0.0196 | 1 | 100.0% | 0.0000 |
| Coton | 24h | 12 | 50.0% | 0.2737 | 6 | 33.3% | 0.3580 |
| Coton | 7j | 5 | 0.0% | 0.4595 | 3 | 0.0% | 0.7248 |
| Cuivre | 24h | 20 | 55.0% | 0.3098 | 8 | 50.0% | 0.3874 |
| Cuivre | 7j | 16 | 18.8% | 0.4871 | 10 | 20.0% | 0.5703 |
| Cuivre | 1m | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 8 | 0.0% | 0.8456 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 1m | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 15 | 53.3% | 0.3518 | 9 | 44.4% | 0.3856 |
| Nasdaq | 7j | 8 | 87.5% | 0.1424 | 6 | 83.3% | 0.1513 |
| Nasdaq | 1m | 1 | 100.0% | 0.0000 | 1 | 100.0% | 0.0000 |
| Or | 24h | 16 | 25.0% | 0.5935 | 6 | 16.7% | 0.6322 |
| Or | 7j | 10 | 0.0% | 0.8061 | 5 | 0.0% | 0.8174 |
| Or | 1m | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 24h | 21 | 61.9% | 0.2797 | 15 | 80.0% | 0.2302 |
| Pétrole (Brent) | 7j | 17 | 41.2% | 0.4187 | 8 | 50.0% | 0.4276 |
| Pétrole (Brent) | 1m | 1 | 0.0% | 1.0000 | 0 | — | — |
| S&P 500 | 24h | 12 | 50.0% | 0.4480 | 0 | — | — |
| S&P 500 | 7j | 4 | 25.0% | 0.7205 | 0 | — | — |
| S&P 500 | 1m | 0 | — | — | 0 | — | — |
| Sucre | 24h | 0 | — | — | 0 | — | — |
| Sucre | 7j | 0 | — | — | 0 | — | — |
| USD/JPY | 24h | 0 | — | — | 0 | — | — |
| USD/JPY | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 9 | 77.8% | 0.2903 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |
| VIX | 1m | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-0.10 pts** sur 21 cellules
