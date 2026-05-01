"""Scoring deterministe (sanity checks SC1-SC6) — stub Phase 2a, rempli Phase 2c.

Spec : docs/ia/edge-scoring-model.md scoring-model-v1.1.

SC1 : coherence direction (BLOQUANT)
SC2 : R/R >= 1.5 (NO-TRADE si <1.0)
SC3 : score > 9 -> ALERT (sur-confiance)
SC4 : %no-trade 7j <20% -> -1.0
SC5 : speculatif sans chiffre -> plafond 6.0
SC6 : diversite sous-jacents 30j (1/13) -> plafond 7.0 + ALERT
"""
