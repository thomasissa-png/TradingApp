# Santé des sources news

_Cycle : 2026-06-09 05:16 UTC_

**Synthèse** : 33 flux configurés, 33 appelés, 32 OK, 1 partiels, 0 en échec, 2 muets (0 gardé), 0 skip (pas de clé API). Items : 1681 reçus → 1169 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ⚠️ | partiel (13/14) | gnews | 400 | 22 | 18 | 1/14 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default |
| ⚪ | muet | ecb_press | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_commodities | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 59 | 3 |  |
| ✅ | OK | bbc_world | 200 | 31 | 6 |  |
| ✅ | OK | boe_news | 200 | 50 | 12 |  |
| ✅ | OK | boj_news | 200 | 52 | 2 |  |
| ✅ | OK | cnbc_economy | 200 | 30 | 20 |  |
| ✅ | OK | cnbc_finance | 200 | 30 | 6 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 19 |  |
| ✅ | OK | eia_press_releases | 200 | 7 | 7 |  |
| ✅ | OK | eia_today_in_energy | 200 | 16 | 11 |  |
| ✅ | OK | fed_monetary | 200 | 15 | 1 |  |
| ✅ | OK | fed_press_all | 200 | 20 | 15 |  |
| ✅ | OK | gnews_cac40 | 200 | 100 | 97 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 72 |  |
| ✅ | OK | gnews_coffee | 200 | 100 | 39 |  |
| ✅ | OK | gnews_copper | 200 | 80 | 80 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 97 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 95 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 97 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 98 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 99 |  |
| ✅ | OK | gnews_wheat | 200 | 62 | 59 |  |
| ✅ | OK | investing_commod | 200 | 10 | 5 |  |
| ✅ | OK | investing_econ | 200 | 10 | 5 |  |
| ✅ | OK | investing_economy | 200 | 10 | 3 |  |
| ✅ | OK | investing_forex | 200 | 10 | 4 |  |
| ✅ | OK | investing_metals | 200 | 10 | 4 |  |
| ✅ | OK | investing_news | 200 | 10 | 5 |  |
| ✅ | OK | investing_stocks | 200 | 10 | 4 |  |
| ✅ | OK | newsapi | 200 | 267 | 174 |  |
| ✅ | OK | oilprice | 200 | 15 | 12 |  |
