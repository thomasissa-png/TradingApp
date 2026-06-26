# Performance A/B — ±1 (baseline) vs pondéré (secondaire)

- Généré : 26 juin 2026, 07h28
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- Cible : 70% (Bourse.md)

Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent
pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).

## Matrice A/B

| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |
|---|---|---|---|---|---|---|---|
| Argent | 24h | 3 | 100.0% | 0.0029 | 0 | — | — |
| Blé | 24h | 1 | 100.0% | 0.0008 | 1 | 100.0% | 0.0397 |
| CAC 40 | 24h | 2 | 0.0% | 0.3800 | 0 | — | — |
| Cacao | 24h | 3 | 100.0% | 0.0000 | 3 | 100.0% | 0.0024 |
| Café (Arabica) | 24h | 1 | 100.0% | 0.1340 | 1 | 100.0% | 0.1315 |
| Cuivre | 24h | 2 | 100.0% | 0.0000 | 2 | 100.0% | 0.0000 |
| EUR/USD | 24h | 1 | 100.0% | 0.0000 | 0 | — | — |
| Nasdaq | 24h | 2 | 0.0% | 0.6278 | 1 | 0.0% | 0.7442 |
| Or | 24h | 3 | 66.7% | 0.3333 | 2 | 100.0% | 0.0000 |
| Pétrole (Brent) | 24h | 3 | 66.7% | 0.4294 | 1 | 0.0% | 1.0000 |
| S&P 500 | 24h | 1 | 0.0% | 0.4053 | 0 | — | — |
| VIX | 24h | 1 | 0.0% | 0.3010 | 0 | — | — |

## Synthèse globale (cellules avec ≥1 mesure pondérée)
- Delta taux moyen (pondéré − ±1) : **-4.76 pts** sur 7 cellules
