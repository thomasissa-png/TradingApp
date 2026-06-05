# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 2026-06-05T12:06:25.161422+02:00
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 14 | 92.9% | 0.1586 | 2 | 50.0% | 0.2252 |
| Argent | 7j | 0 | — | — | 0 | — | — |
| Blé | 24h | 7 | 85.7% | 0.1812 | 2 | 100.0% | 0.0643 |
| Blé | 7j | 0 | — | — | 0 | — | — |
| CAC 40 | 24h | 12 | 16.7% | 0.3148 | 2 | 100.0% | 0.2457 |
| CAC 40 | 7j | 0 | — | — | 0 | — | — |
| Cacao | 24h | 9 | 0.0% | 0.3911 | 6 | 0.0% | 0.4148 |
| Cacao | 7j | 0 | — | — | 0 | — | — |
| Café (Arabica) | 24h | 11 | 81.8% | 0.2257 | 11 | 81.8% | 0.2372 |
| Café (Arabica) | 7j | 0 | — | — | 0 | — | — |
| Cuivre | 24h | 11 | 0.0% | 0.5699 | 11 | 0.0% | 0.4155 |
| Cuivre | 7j | 0 | — | — | 0 | — | — |
| EUR/USD | 24h | 4 | 0.0% | 0.7990 | 0 | — | — |
| EUR/USD | 7j | 0 | — | — | 0 | — | — |
| Nasdaq | 24h | 3 | 100.0% | 0.2347 | 0 | — | — |
| Nasdaq | 7j | 0 | — | — | 0 | — | — |
| Or | 24h | 5 | 100.0% | 0.1327 | 5 | 100.0% | 0.1007 |
| Or | 7j | 0 | — | — | 0 | — | — |
| Pétrole (Brent) | 24h | 12 | 33.3% | 0.5681 | 8 | 25.0% | 0.6059 |
| Pétrole (Brent) | 7j | 0 | — | — | 0 | — | — |
| S&P 500 | 24h | 0 | — | — | 0 | — | — |
| S&P 500 | 7j | 0 | — | — | 0 | — | — |
| VIX | 24h | 11 | 18.2% | 0.3945 | 0 | — | — |
| VIX | 7j | 0 | — | — | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **+5.80 pts** sur 8 cellules
