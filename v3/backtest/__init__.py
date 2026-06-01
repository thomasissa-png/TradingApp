"""TradingApp v3 — Backtest quant historique (itération 1).

Objectif : mesurer l'edge directionnel du moteur QUANT-only (prix/z-scores/RSI/
ratios/momentum) sur l'historique, sans la composante news (irreproductible).

Modules :
- historical_data : couche fetch yfinance avec garantie no look-ahead (`series_asof`)
- backtest_quant : moteur de backtest non-chevauchant + métriques walk-forward
"""
