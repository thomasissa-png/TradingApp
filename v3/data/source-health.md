# Santé des sources news

_Cycle : 2026-06-11 05:16 UTC_

**Synthèse** : 33 flux configurés, 33 appelés, 32 OK, 1 partiels, 0 en échec, 3 muets (0 gardé), 0 skip (pas de clé API). Items : 1662 reçus → 691 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ⚠️ | partiel (14/15) | gnews | 400 | 22 | 20 | 1/15 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff |
| ⚪ | muet | eia_press_releases | 200 | 8 | 0 | 8 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | fed_monetary | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_stocks | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 57 | 5 |  |
| ✅ | OK | bbc_world | 200 | 51 | 9 |  |
| ✅ | OK | boe_news | 200 | 50 | 5 |  |
| ✅ | OK | boj_news | 200 | 55 | 19 |  |
| ✅ | OK | cnbc_economy | 200 | 30 | 4 |  |
| ✅ | OK | cnbc_finance | 200 | 30 | 9 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 23 |  |
| ✅ | OK | ecb_press | 200 | 15 | 7 |  |
| ✅ | OK | eia_today_in_energy | 200 | 17 | 1 |  |
| ✅ | OK | fed_press_all | 200 | 20 | 13 |  |
| ✅ | OK | gnews_cac40 | 200 | 100 | 1 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 10 |  |
| ✅ | OK | gnews_coffee | 200 | 33 | 2 |  |
| ✅ | OK | gnews_copper | 200 | 69 | 3 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 22 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 41 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 94 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 43 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 97 |  |
| ✅ | OK | gnews_wheat | 200 | 65 | 2 |  |
| ✅ | OK | investing_commod | 200 | 10 | 8 |  |
| ✅ | OK | investing_commodities | 200 | 10 | 9 |  |
| ✅ | OK | investing_econ | 200 | 10 | 6 |  |
| ✅ | OK | investing_economy | 200 | 10 | 6 |  |
| ✅ | OK | investing_forex | 200 | 10 | 5 |  |
| ✅ | OK | investing_metals | 200 | 10 | 8 |  |
| ✅ | OK | investing_news | 200 | 10 | 8 |  |
| ✅ | OK | newsapi | 200 | 300 | 196 |  |
| ✅ | OK | oilprice | 200 | 15 | 15 |  |
