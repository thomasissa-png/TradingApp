<!-- Version: 2026-05-01T00:00 — @data-analyst — Création initiale edge-rnd-brief.md TradingApp -->
# Edge R&D Brief — Phase 1 TradingApp

> **Résumé exécutif**
> - **Objectif** : définir le cadre de recherche de l'edge robuste (Phase 1) avant tout code de production.
> - **Décisions clés** : 7 hypothèses d'edge à tester ; méthodologie IS 2021-2024 / OOS 2025 / walk-forward ; critères GO/NO-GO stricts (Sharpe OOS > 1, PF > 1,5, DD < 20 %) ; cache SQLite Twelve Data obligatoire.
> - **Dépendances** : @fullstack (choix stack Python vs Node, libs backtester) ; @ia (Haiku batch + cache pour scoring R&D) ; infra-audit.md (rate limits, volume 6 M bougies, H2 NEEDS-DECISION) ; project-context.md décision structurante n°4.

---

## 1. Objectif Phase 1 R&D

**Mission** : identifier au moins 1 edge robuste sur 5 ans d'historique Twelve Data (2021-2025) sur les sous-jacents EU compatibles avec la fenêtre d'ouverture 8h40-9h00 CET de Thomas, exécutable manuellement chez Bourse Direct sur turbos.

**Livrable attendu Phase 1** : un rapport de backtest par hypothèse testée, avec statistiques complètes (voir section 4), verdict GO/NO-GO par hypothèse, et au moins 1 edge qualifié pour Phase 2 Build. Si zéro edge qualifié → no-go assumé (décision structurante n°4 project-context.md).

**Prérequis bloquant avant lancement** : confirmer H2 (plan Twelve Data Pro Individual couvre intraday 1m + Europe stocks — infra-audit.md section 2.5). Action persona requise : se connecter à twelvedata.com/account et vérifier "1-minute intraday + Euronext Paris + Xetra" inclus dans le plan actuel.

---

## 2. Hypothèses d'edge à tester (7)

### H-EDGE-A — Gap Follow EU Open

**Logique** : si le sous-jacent ouvre en gap haussier (> X %) par rapport à la clôture J-1, la dynamique continue dans les premières minutes. Achat sur turbo Call dès l'ouverture (8h01 Xetra / 9h01 Euronext).

**Sous-jacents prioritaires** : ^GDAXI (DAX), ^FCHI (CAC40).
**Paramètres à optimiser** : seuil gap minimum (0,3 %, 0,5 %, 0,8 %), fenêtre de continuité (5-30 min), SL ATR-based.
**Référence héritage Finance** : piste gap follow déjà mentionnée dans project-context.md décision structurante n°4.

### H-EDGE-B — Gap Fade EU Open

**Logique** : inverse de H-A. Si gap haussier dépasse un seuil de sur-extension (> Y %), le prix revient combler partiellement le gap dans l'heure. Achat turbo Put.

**Sous-jacents prioritaires** : ^FCHI, ^STOXX50E.
**Paramètres à optimiser** : seuil de sur-extension (1,0 %, 1,5 %, 2,0 %), ratio fade partiel (33 %, 50 %, 61,8 % Fibonacci).
**Note** : H-A et H-B sont mutuellement exclusifs sur le même signal. La R&D devra identifier quel régime domine selon l'amplitude du gap.

### H-EDGE-C — Opening Range Breakout (ORB) 5/15 min

**Logique** : délimiter le range des 5 ou 15 premières minutes après l'ouverture (8h00-8h05 ou 8h00-8h15 Xetra). Entrée si le prix casse au-dessus ou en dessous de ce range avec volume confirmatoire. Signal envoyé à 8h45 après confirmation.

**Sous-jacents prioritaires** : ^GDAXI, MC.PA (LVMH), TTE.PA (TotalEnergies), SAN.PA (Sanofi).
**Paramètres à optimiser** : fenêtre ORB (5 ou 15 min), filtre volume (> moyenne 20 j), SL = borne opposée du range.
**Référence héritage Finance** : RSI/MACD/Bollinger présents dans les libs Finance — à réutiliser comme filtres secondaires sur ORB.

### H-EDGE-D — Momentum Overnight US → EU (S&P Futures → CAC/DAX)

**Logique** : la clôture de la session US (S&P 500 futures) prédit statistiquement le sens d'ouverture EU. Si S&P futures à 2h00-7h00 CET en hausse > Z %, signal d'achat sur CAC40/DAX à l'ouverture.

**Données requises** : S&P 500 E-mini futures (`ES=F` ou équivalent Twelve Data) en overnight. Vérifier couverture Twelve Data.
**Paramètres à optimiser** : seuil overnight S&P (0,5 %, 1,0 %), fenêtre de mesure (2h00-7h00 vs 22h00-7h00 CET), délai de corrélation.

### H-EDGE-E — News Pré-marché (continuité scoring Finance)

**Logique** : les news publiées entre 5h00 et 8h30 CET sur les grands médias financiers (Reuters, Bloomberg, Les Échos) ont un impact mesurable sur le sens d'ouverture. Scoring sentiment Claude sur les titres/résumés = signal directionnel.

**Référence héritage Finance** : project-context.md section "Garde" — "Scoring news Claude + catégorisation (piste edge news pré-marché)". Module existant dans Finance à adapter.
**Données requises** : API news Twelve Data ou source alternative. Vérifier couverture news EU dans le plan Pro Individual.
**Paramètres à optimiser** : seuil de sentiment (positif/négatif > X %), filtre sur mots-clés (PIB, BCE, NFP, earnings), combinaison avec signal technique (H-EDGE-C ou H-EDGE-A).
**Note** : cet edge dépend de Claude (Haiku R&D) pour le scoring — coordonner volume avec @ia (infra-audit.md section 3.3, 100 appels/j recommandés).

### H-EDGE-F — Écart Spot/Futures à l'Ouverture (basis trading)

**Logique** : l'écart entre le prix spot du sous-jacent (ex : actions LVMH) et ses futures (contrats à terme sur Euronext) se réduit mécaniquement à l'ouverture. Si l'écart dépasse un niveau statistique (> 2 écarts-types historiques), arbitrage directionnel.

**Données requises** : prix futures EU sur Twelve Data — vérifier disponibilité (futures sur indices EU couverts, futures sur actions individuelles moins certain).
**Paramètres à optimiser** : seuil d'écart (1,5 σ, 2 σ, 2,5 σ), fenêtre de réversion (5-30 min), filtre volume.
**Note** : edge plus technique, pertinence dépend de la disponibilité des futures dans le plan Twelve Data [HYPOTHÈSE : à vérifier dans twelvedata.com/market-data section Futures].

### H-EDGE-G — Sentiment Overnight Asie (Nikkei → CAC Corrélation)

**Logique** : la performance du Nikkei 225 (clôture Tokyo, ~8h30 CET) et du Hang Seng est corrélée statistiquement avec l'ouverture du CAC40. Si Nikkei clôt en hausse > W %, signal d'achat sur CAC40 turbo Call.

**Données requises** : Nikkei 225 (`^N225`) et Hang Seng (`^HSI`) daily close via Twelve Data.
**Paramètres à optimiser** : seuil Nikkei (0,5 %, 1,0 %, 1,5 %), corrélation conditionnelle (seulement quand S&P corrèle aussi ?), décalage horaire.
**Note** : cet edge est macro, moins granulaire en intraday 1m. À tester en complément d'un signal technique (ORB ou gap).

---

## 3. Méthodologie

### 3.1 Découpage temporel

| Période | Usage | Données Twelve Data |
|---------|-------|---------------------|
| **2021-2024 (4 ans)** | **In-sample (IS)** — entraînement + optimisation paramètres | ~4 × 252 × 480 bougies/ssj = ~2,4 M bougies pour 5 sous-jacents |
| **2025 (1 an)** | **Out-of-sample (OOS)** — validation stricte, AUCUNE modification paramètres après IS | ~252 × 480 × 5 = ~600 k bougies |
| **Walk-forward annuel** | Re-split par fenêtre glissante (IS 3 ans / OOS 1 an) | Rotation annuelle sur 2021-2025 |

**Règle absolue** : les paramètres sont fixés sur IS 2021-2024. L'OOS 2025 est une validation black-box. Toute modification de paramètre après avoir regardé l'OOS = overfitting = invalidation de l'edge.

### 3.2 Coûts de transaction réalistes

**Obligatoire dans chaque simulation backtest** :

```python
frais_total_par_trade = (
    frais_bd_achat + frais_bd_vente  # 0,99 € × 2 = 1,98 €
    + spread_emetteur                 # estimé 0,03-0,10 € selon turbo
    + slippage                        # 0,1 % du prix d'exécution (Bourse Direct, order routing)
)
```

| Coût | Valeur | Source |
|------|--------|--------|
| Frais Bourse Direct | 0,99 € × 2 = 1,98 € aller-retour | Bourse Direct tarifs CTO |
| Spread émetteur | 0,03-0,10 € par trade | [HYPOTHÈSE : à mesurer sur trades réels ; utiliser 0,05 € comme estimation centrale] |
| Slippage | 0,1 % du montant exécuté | [HYPOTHÈSE : estimation conservatrice pour turbos Bourse Direct] |

**Taille de position de référence** : 1 500 € par trade (midpoint de la fourchette personas.md 1 000-2 000 €).

### 3.3 Walk-forward analysis

```
Fenêtre 1 : IS 2021-2023 / OOS 2024
Fenêtre 2 : IS 2022-2024 / OOS 2025
Fenêtre standard : IS 2021-2024 / OOS 2025

Critère de robustesse : Sharpe_OOS ≥ 50 % × Sharpe_IS sur CHAQUE fenêtre
```

Un edge dont le Sharpe OOS < 50 % du Sharpe IS sur 2 fenêtres sur 3 est **invalidé** même si les chiffres absolus semblent bons.

### 3.4 Cache SQLite Twelve Data (OBLIGATOIRE — infra-audit.md section 2.4)

**Volume total R&D** : 6 M bougies 1m pour 10 sous-jacents × 5 ans (infra-audit.md section 2.3 — confirmé).

**Stratégie** :
1. Premier run : backfill complet 5 ans → ~1 200 requêtes API en ~22 min à 55 req/min (Pro Individual).
2. Tous les backtests R&D lisent depuis `data/market_cache.sqlite` — AUCUN appel API supplémentaire.
3. Backup quotidien de la base cache (infra-audit.md section 5.4).

```sql
-- Table cache (déjà définie dans infra-audit.md section 2.4)
-- candles_1m (symbol TEXT, ts TIMESTAMP, open, high, low, close, volume, PK(symbol, ts))
-- fetch_log (symbol, last_ts_fetched, fetched_at)
```

**Économie** : sans cache, répéter 7 hypothèses × 3 paramétrisations = 21 backtests × 1 200 req = 25 200 requêtes API → rate limit explosé. Avec cache : 1 200 requêtes one-shot + 0 appel R&D.

---

## 4. Statistiques requises par hypothèse testée

**Format obligatoire de reporting par hypothèse** (input pour @testeur-backtest-edge et GO/NO-GO Phase 2) :

| Statistique | Formule | Seuil GO Phase 2 |
|-------------|---------|------------------|
| Nombre de trades | COUNT(*) trades exécutés IS | ≥ 100 (significativité statistique minimale) |
| Win rate IS | Trades gagnants / total IS × 100 | ≥ 50 % |
| Win rate OOS | idem sur 2025 | ≥ Win_rate_IS − 5 pts |
| Profit Factor IS | Σ gains / Σ pertes IS | ≥ 1,5 |
| Profit Factor OOS | idem sur 2025 | **≥ 1,5** |
| Sharpe ratio annualisé IS | Formule section 2.4 kpi-framework.md | > 1,5 |
| **Sharpe ratio annualisé OOS** | idem sur 2025 | **> 1,0** |
| Max drawdown IS | % du capital, période IS | < 25 % (tolérance légèrement plus haute IS) |
| **Max drawdown OOS** | % du capital, période OOS | **< 20 %** |
| Durée moyenne trade | Σ (exit_time − entry_time) / N | 5-45 min (compatibilité fenêtre Thomas) |
| **Robustesse IS→OOS** | Sharpe_OOS / Sharpe_IS | **≥ 50 %** |
| Robustesse walk-forward | Sharpe_OOS sur 2 fenêtres walk-forward | ≥ 50 % Sharpe_IS sur chaque fenêtre |

---

## 5. Critère GO/NO-GO Phase 2

### Condition GO Phase 2 (AND — toutes requises)

- Au moins 1 hypothèse avec Sharpe OOS > 1,0
- ET Profit Factor OOS > 1,5
- ET Max drawdown OOS < 20 %
- ET Robustesse ≥ 50 % (Sharpe_OOS / Sharpe_IS)
- ET ≥ 100 trades IS (significativité)

### Condition NO-GO (si aucun edge qualifié)

Si aucune des 7 hypothèses ne satisfait les 5 critères GO : **no-go Phase 2 assumé**. Accepter le résultat sans sur-fitter. Options :

1. Tester des sous-hypothèses (ex : H-EDGE-A uniquement sur DAX entre 8h01-8h10)
2. Affiner les coûts de transaction (si spread réel Bourse Direct plus faible que l'hypothèse)
3. Accepter le no-go et archiver les résultats pour référence future

**Source** : décision structurante n°4 et n°5 project-context.md, risque anti-pattern n°2 Notes libres ("si le backtest ne donne aucun edge robuste, accepter le no-go. Mieux vaut pas de bot qu'un bot qui fait perdre 2-3 k€/mois.").

---

## 6. Outils R&D

### Stack recommandé (à arbitrer par @fullstack Phase 2)

| Outil | Usage | Décision |
|-------|-------|----------|
| **Python** | Langage principal R&D | Continuité libs Finance (project-context.md "Garde") |
| **pandas** | Manipulation données bougies, calcul indicateurs | Héritage Finance confirmé |
| **vectorbt** | Backtesting vectorisé rapide | Préféré pour sa vitesse sur 6 M bougies — à évaluer vs backtesting.py |
| **backtesting.py** | Alternative backtesting | Plus lisible, moins rapide — backup si vectorbt ne couvre pas un cas |
| **SQLite** | Cache bougies + journal résultats backtest | Obligatoire (infra-audit.md section 2.4) |
| **Claude Haiku 4.5** | Scoring news pré-marché (H-EDGE-E uniquement) | Batch + cache prompt obligatoires (infra-audit.md H4) |

**Note** : l'arbitrage vectorbt vs backtesting.py est laissé à @fullstack lors du setup Phase 2. Critère de décision : vitesse sur 6 M bougies × 7 hypothèses × 3 paramétrisations ≈ 126 M bougies à parcourir.

---

## 7. Coût R&D estimé

### Volume données Twelve Data

| Poste | Calcul | Volume |
|-------|--------|--------|
| Bougies 1m, 10 sous-jacents, 5 ans | 10 × 252 × 5 × 480 | ~6,1 M bougies |
| Requêtes API (one-shot, 5000 bougies/req) | 6 100 000 / 5 000 | **~1 220 requêtes** |
| Durée backfill (55 req/min, Pro Individual) | 1 220 / 55 | ~22 min |
| Coût API (inclus dans abonnement mensuel) | Plan Pro Individual 79 $/mois | 0 $ marginal si abonné |

### Claude Haiku R&D (H-EDGE-E news scoring uniquement)

| Scénario | Calcul | Coût estimé |
|----------|--------|-------------|
| 100 appels/jour × 30 jours (recommandé) | Haiku + batch + cache prompt (infra-audit.md section 3.3) | ~10 $/mois |
| 500 appels/jour × 30 jours (scénario max) | Sans optimisation : 150 $/mois — HORS BUDGET | Batch + cache → ~51 $/mois |

**Recommandation** : limiter à 100 appels Claude/jour pendant R&D H-EDGE-E. Les 6 autres hypothèses (A à D, F, G) sont purement quantitatives, zéro appel Claude.

### Budget cumulé R&D 30-90 jours

| Durée R&D | Twelve Data Pro | Claude Haiku (100 ap/j) | Replit Core | Total estimé |
|-----------|-----------------|-------------------------|-------------|--------------|
| 30 jours | 79 $ | 10 $ | 20 $ | **~109 $/mois ≈ 100 €** |
| 60 jours | 158 $ | 20 $ | 40 $ | **~218 $ ≈ 200 €** |
| 90 jours | 237 $ | 30 $ | 60 $ | **~327 $ ≈ 300 €** |

**Note** : si le plan Twelve Data Pro est déjà actif et payé, le coût marginal R&D est uniquement Claude (~10 $/mois) + Replit (~20 $/mois) = **~30 $/mois** pendant la R&D. Confirmation H2 (action persona) est donc critique pour évaluer le vrai coût marginal.

---

## Hypothèses à valider

| # | Hypothèse | Owner | Criticité |
|---|-----------|-------|-----------|
| H2 | Plan Twelve Data actuel couvre intraday 1m + Euronext Paris + Xetra | Thomas | BLOQUANT avant lancement R&D |
| H-EDGE-F-DATA | Futures EU (indices + actions) disponibles dans Twelve Data Pro Individual | @fullstack | Vérifier avant d'investir temps sur H-EDGE-F |
| H-EDGE-E-NEWS | API news EU disponible dans Twelve Data ou source alternative à définir | @fullstack + @ia | Vérifier avant H-EDGE-E |
| H-SLIPPAGE | Slippage 0,1 % estimation conservatrice pour turbos Bourse Direct | Thomas | À mesurer sur premiers trades paper-trading |
| H-SPREAD | Spread émetteur 0,05 € estimation centrale pour turbos | Thomas | À mesurer sur premiers trades paper-trading |

---

**Handoff → @ia, @fullstack, @orchestrator (Phase 1)**

- Fichiers produits : `/home/user/TradingApp/docs/analytics/edge-rnd-brief.md`
- Décisions prises :
  - 7 hypothèses d'edge documentées (A à G) avec logique, sous-jacents, paramètres
  - Méthodologie IS 2021-2024 / OOS 2025 / walk-forward — règle OOS black-box absolue
  - Coûts de transaction réalistes : 1,98 € frais BD + spread 0,05 € + slippage 0,1 %
  - Cache SQLite obligatoire — one-shot 1 220 requêtes → zéro appel R&D supplémentaire
  - Seuils GO Phase 2 stricts : Sharpe OOS > 1, PF > 1,5, DD < 20 %, robustesse ≥ 50 %
  - Budget R&D ~30 $/mois marginal si Twelve Data déjà actif (H2 à confirmer)
- Points d'attention :
  - **BLOQUANT** : H2 (plan Twelve Data 1m EU stocks) doit être confirmé par Thomas AVANT tout lancement R&D — action simple : vérifier twelvedata.com/account
  - **@fullstack** : arbitrer vectorbt vs backtesting.py selon perf sur 126 M bougies (~6 M × 7 hypothèses × 3 params)
  - **@ia** : H-EDGE-E news scoring = 100 appels Haiku/jour max — batch + cache prompt obligatoires pour rester dans budget
  - **@testeur-backtest-edge** (recommandé dans brand-platform.md) : créer cet agent (specs dans brand-platform.md section 9) avant de valider Phase 1 — il challengera chaque résultat backtest contre overfitting
  - **Zéro code de production** avant qu'au moins 1 edge passe tous les critères GO Phase 2
- Actions Replit requises : aucune (livrable documentation uniquement)
- Gates BLOQUANT vérifiées : G1 PASS, G3 PASS, G5 PASS (Thomas mentionné), G6 PASS (P&L net = North Star cohérent), G7 PASS (cohérent infra-audit.md, legal-audit.md, personas.md, project-context.md), G12 PASS, G13 PASS (zéro chiffre inventé, hypothèses marquées), G15 PASS, G17 PASS, G23 PASS (seuils GO/NO-GO explicites par statistique)
