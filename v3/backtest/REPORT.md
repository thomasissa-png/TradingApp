# Backtest QUANT historique — Rapport v1 (2026-06-01)

> Backtest du moteur **quant-only** (features price-derived) sur historique réel yfinance.
> But : prouver/réfuter l'edge directionnel du moteur SANS la partie news (irreproductible).
> Méthode : no-look-ahead strict (`series_asof` filtre `index < as_of`), échantillonnage non-chevauchant, walk-forward IS 2022-2024 / OOS 2025-01→2026-05.

## Résultats OOS (4 actifs × 24h)

| Cellule | N concl. | Accuracy | Wilson_low | p-value | Verdict |
|---|---|---|---|---|---|
| S&P 500 (^GSPC) | 212 | 46.2% | 39.6% | 0.703 | NO-GO |
| Nasdaq (^IXIC) | 177 | 51.4% | 44.1% | 0.529 | NO-GO |
| Or (GC=F) | 234 | 48.3% | 42.0% | 0.680 | NO-GO |
| Pétrole (CL=F) | 217 | **57.6%** | **51.0%** | **0.019** | BORDERLINE |
| **POOLED** | **840** | **50.8%** | 47.5% | — | **NO-GO** |

**Critères GO** (audit-reel-et-backtest-scope.md) : accuracy OOS ≥60% ET Wilson_low ≥55% ET p-bootstrap <0.05. Aucune cellule ne les remplit. Pétrole est significatif (p=0.019) mais sous 60%.

## Verdict v1 : NO-GO (PARTIEL)

Sur le sous-ensemble câblé (price-derived), le moteur est **indistinguable du pile ou face** à 24h (50.8%).

## Limites (pourquoi c'est PARTIEL, pas définitif)
1. **Couverture ~30-50% des critères** : seuls les price-derived sont câblés. **CFTC COT, FRED (TIPS, HY spread), EIA, météo** = absents (n/a, poids 0). Or l'audit estime que COT+FRED = ~50% du poids effectif → c'est peut-être là qu'est l'edge.
2. **Bug trouvé** : proxy ETF `TIP` pour les taux réels est INVERSÉ (TIP monte quand les taux réels baissent) → à corriger via FRED `DFII10` direct en v2.
3. **24h seulement** : l'horizon le plus dur (direction journalière ≈ marché efficient). La thèse trend-following vise surtout 7j/1m — non testés en v1.
4. CL=F (WTI) utilisé comme proxy Brent (historique yfinance plus propre).

## Plan v2 (obligatoire pour conclure sur le moteur LIVE complet)
1. **CFTC COT historique** (CSV Socrata, filtrage `report_date < as_of`) — débloque ~6 actifs, poids 6-8. [TRÈS ÉLEVÉ]
2. **FRED historique** (`fred_series_asof` filtré par date — fonction live existe) — TIPS, HY spread. [ÉLEVÉ]
3. Horizons **7j + 1m** (le moteur les supporte déjà). [MOYEN]
4. 12 actifs + étude d'ablation par critère (quels critères portent l'edge ?). [ÉLEVÉ]
Effort v2 ~7-8j. Verdict complet ~J+10/J+14.

## Reproductibilité
`python3 v3/backtest/backtest_quant.py` (~15s, cache yfinance). Tests : `pytest v3/tests/test_backtest.py` (17, dont 2 no-look-ahead).
