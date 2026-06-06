# Santé des sources news

_Cycle : 2026-06-06 05:01 UTC_

**Synthèse** : 34 flux configurés, 34 appelés, 32 OK, 1 partiels, 1 en échec, 3 muets (0 gardé), 0 skip (pas de clé API). Items : 1661 reçus → 1180 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ❌ | échec | mining_com | 403 | 0 | 0 | HTTP 403 |
| ⚠️ | partiel (13/14) | gnews | 400 | 23 | 19 | 1/14 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default |
| ⚪ | muet | cnbc_finance | 200 | 30 | 0 | 30 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | eia_today_in_energy | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_stocks | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 57 | 7 |  |
| ✅ | OK | bbc_world | 200 | 29 | 1 |  |
| ✅ | OK | boe_news | 200 | 50 | 18 |  |
| ✅ | OK | boj_news | 200 | 55 | 19 |  |
| ✅ | OK | cnbc_economy | 200 | 30 | 3 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 14 |  |
| ✅ | OK | ecb_press | 200 | 15 | 6 |  |
| ✅ | OK | eia_press_releases | 200 | 7 | 5 |  |
| ✅ | OK | fed_monetary | 200 | 15 | 1 |  |
| ✅ | OK | fed_press_all | 200 | 20 | 15 |  |
| ✅ | OK | gnews_cac40 | 200 | 81 | 81 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 75 |  |
| ✅ | OK | gnews_coffee | 200 | 100 | 84 |  |
| ✅ | OK | gnews_copper | 200 | 82 | 82 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 98 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 96 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 97 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 100 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 98 |  |
| ✅ | OK | gnews_wheat | 200 | 57 | 55 |  |
| ✅ | OK | investing_commod | 200 | 10 | 9 |  |
| ✅ | OK | investing_commodities | 200 | 10 | 2 |  |
| ✅ | OK | investing_econ | 200 | 10 | 3 |  |
| ✅ | OK | investing_economy | 200 | 10 | 3 |  |
| ✅ | OK | investing_forex | 200 | 10 | 1 |  |
| ✅ | OK | investing_metals | 200 | 10 | 6 |  |
| ✅ | OK | investing_news | 200 | 10 | 3 |  |
| ✅ | OK | newsapi | 200 | 270 | 169 |  |
| ✅ | OK | oilprice | 200 | 15 | 10 |  |
