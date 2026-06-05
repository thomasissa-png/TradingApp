# Santé des sources news

_Cycle : 2026-06-05 10:01 UTC_

**Synthèse** : 34 flux configurés, 34 appelés, 32 OK, 1 partiels, 1 en échec, 13 muets (0 gardé), 0 skip (pas de clé API). Items : 1674 reçus → 1098 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ❌ | échec | mining_com | 403 | 0 | 0 | HTTP 403 |
| ⚠️ | partiel (13/14) | gnews | 400 | 23 | 20 | 1/14 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default |
| ⚪ | muet | boj_news | 200 | 55 | 0 | 55 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | cnbc_economy | 200 | 30 | 0 | 30 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | cnbc_finance | 200 | 30 | 0 | 30 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | ecb_press | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | eia_press_releases | 200 | 7 | 0 | 7 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | eia_today_in_energy | 200 | 14 | 0 | 14 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | fed_monetary | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | fed_press_all | 200 | 20 | 0 | 20 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_commod | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_commodities | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_forex | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_metals | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_stocks | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 57 | 2 |  |
| ✅ | OK | bbc_world | 200 | 36 | 1 |  |
| ✅ | OK | boe_news | 200 | 50 | 2 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 2 |  |
| ✅ | OK | gnews_cac40 | 200 | 100 | 100 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 94 |  |
| ✅ | OK | gnews_coffee | 200 | 100 | 72 |  |
| ✅ | OK | gnews_copper | 200 | 73 | 73 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 97 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 96 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 96 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 100 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 98 |  |
| ✅ | OK | gnews_wheat | 200 | 56 | 54 |  |
| ✅ | OK | investing_econ | 200 | 10 | 6 |  |
| ✅ | OK | investing_economy | 200 | 10 | 3 |  |
| ✅ | OK | investing_news | 200 | 10 | 7 |  |
| ✅ | OK | newsapi | 200 | 268 | 174 |  |
| ✅ | OK | oilprice | 200 | 15 | 1 |  |
