# Santé des sources news

_Cycle : 2026-06-08 14:23 UTC_

**Synthèse** : 33 flux configurés, 33 appelés, 32 OK, 1 partiels, 0 en échec, 9 muets (0 gardé), 0 skip (pas de clé API). Items : 1620 reçus → 1086 gardés.

_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · ⏭ skip (pas de clé API)._

| | Statut | Flux | HTTP | Reçus | Gardés | Raison |
|---|---|---|---|---:|---:|---|
| ⚠️ | partiel (13/14) | gnews | 400 | 22 | 18 | 1/14 requêtes en échec : stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default |
| ⚪ | muet | boe_news | 200 | 50 | 0 | 50 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | boj_news | 200 | 52 | 0 | 52 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | cnbc_economy | 200 | 30 | 0 | 30 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | cnbc_finance | 200 | 30 | 0 | 30 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | ecb_press | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | eia_press_releases | 200 | 7 | 0 | 7 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | fed_monetary | 200 | 15 | 0 | 15 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | fed_press_all | 200 | 20 | 0 | 20 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ⚪ | muet | investing_stocks | 200 | 10 | 0 | 10 reçus / 0 gardés (dédup + blacklist + filtre finance) |
| ✅ | OK | bbc_business | 200 | 58 | 3 |  |
| ✅ | OK | bbc_world | 200 | 26 | 2 |  |
| ✅ | OK | cnbc_top | 200 | 30 | 6 |  |
| ✅ | OK | eia_today_in_energy | 200 | 16 | 1 |  |
| ✅ | OK | gnews_cac40 | 200 | 75 | 75 |  |
| ✅ | OK | gnews_cocoa | 200 | 100 | 91 |  |
| ✅ | OK | gnews_coffee | 200 | 78 | 65 |  |
| ✅ | OK | gnews_copper | 200 | 73 | 73 |  |
| ✅ | OK | gnews_ecb_policy | 200 | 100 | 97 |  |
| ✅ | OK | gnews_gold_cb | 200 | 100 | 97 |  |
| ✅ | OK | gnews_nasdaq | 200 | 100 | 97 |  |
| ✅ | OK | gnews_silver_industrial | 200 | 100 | 100 |  |
| ✅ | OK | gnews_vix | 200 | 100 | 97 |  |
| ✅ | OK | gnews_wheat | 200 | 60 | 57 |  |
| ✅ | OK | investing_commod | 200 | 10 | 10 |  |
| ✅ | OK | investing_commodities | 200 | 10 | 1 |  |
| ✅ | OK | investing_econ | 200 | 10 | 6 |  |
| ✅ | OK | investing_economy | 200 | 10 | 1 |  |
| ✅ | OK | investing_forex | 200 | 10 | 3 |  |
| ✅ | OK | investing_metals | 200 | 10 | 1 |  |
| ✅ | OK | investing_news | 200 | 10 | 5 |  |
| ✅ | OK | newsapi | 200 | 268 | 175 |  |
| ✅ | OK | oilprice | 200 | 15 | 5 |  |
