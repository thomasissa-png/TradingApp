# Santé des sources news

_Cycle : 2026-06-02 19:53 UTC_

**Synthèse** : 34 flux configurés, 34 appelés, 33 OK, 1 partiels, 0 en échec, 5 muets (0 gardé), 0 skip (pas de clé API). Items : 1663 reçus → 1156 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ⚠️ | partiel (13/14) | gnews | 400 | 23 | 23 | 1/14 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default |
| ⚪ | muet | cnbc_economy | 200 | 30 | 0 | 30 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | eia_press_releases | 200 | 7 | 0 | 7 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | eia_today_in_energy | 200 | 13 | 0 | 13 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_metals | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_stocks | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 55 | 2 |  |
| ✅ | OK | bbc_world | 200 | 34 | 3 |  |
| ✅ | OK | boe_news | 200 | 50 | 20 |  |
| ✅ | OK | boj_news | 200 | 50 | 20 |  |
| ✅ | OK | cnbc_finance | 200 | 30 | 2 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 8 |  |
| ✅ | OK | ecb_press | 200 | 15 | 5 |  |
| ✅ | OK | fed_monetary | 200 | 15 | 1 |  |
| ✅ | OK | fed_press_all | 200 | 20 | 13 |  |
| ✅ | OK | gnews_cac40 | 200 | 100 | 98 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 97 |  |
| ✅ | OK | gnews_coffee | 200 | 56 | 55 |  |
| ✅ | OK | gnews_copper | 200 | 81 | 81 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 97 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 95 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 95 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 99 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 97 |  |
| ✅ | OK | gnews_wheat | 200 | 55 | 53 |  |
| ✅ | OK | investing_commod | 200 | 10 | 6 |  |
| ✅ | OK | investing_commodities | 200 | 10 | 2 |  |
| ✅ | OK | investing_econ | 200 | 10 | 7 |  |
| ✅ | OK | investing_economy | 200 | 10 | 6 |  |
| ✅ | OK | investing_forex | 200 | 10 | 2 |  |
| ✅ | OK | investing_news | 200 | 10 | 7 |  |
| ✅ | OK | mining_com | 200 | 36 | 2 |  |
| ✅ | OK | newsapi | 200 | 268 | 155 |  |
| ✅ | OK | oilprice | 200 | 15 | 5 |  |
