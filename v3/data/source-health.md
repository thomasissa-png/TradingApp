# Santé des sources news

_Cycle : 2026-06-10 05:16 UTC_

**Synthèse** : 33 flux configurés, 33 appelés, 32 OK, 1 partiels, 0 en échec, 1 muets (0 gardé), 0 skip (pas de clé API). Items : 1642 reçus → 1228 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ⚠️ | partiel (13/14) | gnews | 400 | 22 | 18 | 1/14 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default |
| ⚪ | muet | investing_stocks | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 57 | 6 |  |
| ✅ | OK | bbc_world | 200 | 43 | 8 |  |
| ✅ | OK | boe_news | 200 | 50 | 20 |  |
| ✅ | OK | boj_news | 200 | 53 | 19 |  |
| ✅ | OK | cnbc_economy | 200 | 30 | 3 |  |
| ✅ | OK | cnbc_finance | 200 | 30 | 1 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 20 |  |
| ✅ | OK | ecb_press | 200 | 15 | 7 |  |
| ✅ | OK | eia_press_releases | 200 | 8 | 8 |  |
| ✅ | OK | eia_today_in_energy | 200 | 16 | 8 |  |
| ✅ | OK | fed_monetary | 200 | 15 | 1 |  |
| ✅ | OK | fed_press_all | 200 | 20 | 15 |  |
| ✅ | OK | gnews_cac40 | 200 | 72 | 72 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 92 |  |
| ✅ | OK | gnews_coffee | 200 | 78 | 74 |  |
| ✅ | OK | gnews_copper | 200 | 71 | 71 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 98 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 97 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 95 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 99 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 97 |  |
| ✅ | OK | gnews_wheat | 200 | 65 | 62 |  |
| ✅ | OK | investing_commod | 200 | 10 | 10 |  |
| ✅ | OK | investing_commodities | 200 | 10 | 7 |  |
| ✅ | OK | investing_econ | 200 | 10 | 4 |  |
| ✅ | OK | investing_economy | 200 | 10 | 6 |  |
| ✅ | OK | investing_forex | 200 | 10 | 5 |  |
| ✅ | OK | investing_metals | 200 | 10 | 6 |  |
| ✅ | OK | investing_news | 200 | 10 | 7 |  |
| ✅ | OK | newsapi | 200 | 272 | 180 |  |
| ✅ | OK | oilprice | 200 | 15 | 12 |  |
