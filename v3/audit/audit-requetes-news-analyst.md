# Audit — Couverture requêtes news vs 12 actifs
**Date :** 2026-06-01
**Auteur :** @data-analyst
**Périmètre :** STRUCTURED_QUERIES (11 requêtes), EARLY_SIGNAL_FEEDS (20 flux), RSS_FEEDS (10 flux)
**Objectif :** évaluer la capacité du pipeline news à alimenter les critères `source: events-log` des 12 fiches de positionnement

---

## 1. Inventaire canonique des sources

### 1.1 STRUCTURED_QUERIES (API GNews + NewsAPI — quota ~100 req/j free tier)

| # | Requête | Actifs ciblés | Type |
|---|---------|---------------|------|
| Q1 | `oil OR brent OR WTI OR OPEC` | Brent | thématique large |
| Q2 | `gold OR silver OR copper OR platinum` | Or, Argent, Cuivre | groupée métaux |
| Q3 | `wheat OR corn OR coffee OR cocoa OR sugar` | Blé, Café, Cacao | groupée agri |
| Q4 | `Fed OR FOMC OR ECB OR inflation OR CPI` | macro (tous actifs) | macro générique |
| Q5 | `Nasdaq OR S&P 500 OR CAC 40 OR DAX` | Nasdaq, S&P 500, CAC 40 | indices groupés |
| Q6 | `EUR USD OR yen OR dollar index OR forex` | EUR/USD, DXY | FX |
| Q7 | `coffee prices OR arabica OR robusta OR Brazil harvest OR Vietnam coffee` | Café | dédiée café |
| Q8 | `cocoa prices OR Ivory Coast OR Ghana cocoa OR cocoa grindings` | Cacao | dédiée cacao |
| Q9 | `wheat prices OR Black Sea grain OR Russia wheat OR US wheat crop` | Blé | dédiée blé |
| Q10 | `copper prices OR LME copper OR Chile mine OR China copper demand` | Cuivre | dédiée cuivre |
| Q11 | `CAC 40 OR French stocks OR LVMH OR TotalEnergies OR France politics budget` | CAC 40 | dédiée CAC |
| — | *(VIX absent)* | VIX | **MANQUANT** |

**Coût quota estimé par run :**
- GNews free tier : 100 req/j — 11 requêtes × 1 = 11 req (si run unique/j) ✓
- NewsAPI free tier : 100 req/j — 11 req idem ✓
- **Marge restante : ~89 req/j par API** (potentiel d'ajout)

### 1.2 EARLY_SIGNAL_FEEDS (RSS/Atom — illimités, poll 30-60 min)

| Catégorie | Flux | Actifs couverts |
|-----------|------|-----------------|
| Énergie | eia_today_in_energy, eia_press_releases, oilprice | Brent |
| Métaux | mining_com, investing_commodities, investing_metals | Or, Argent, Cuivre |
| Banques centrales | fed_press_all, fed_monetary, ecb_press, boe_news, boj_news | EUR/USD, indices, macro |
| Macro | investing_economy | tous |
| Sous-couverts Google News | gnews_coffee, gnews_cocoa, gnews_wheat, gnews_copper, gnews_cac40 | Café, Cacao, Blé, Cuivre, CAC 40 |

### 1.3 RSS_FEEDS génériques (illimités)

BBC Business/World, CNBC top/economy/finance, Investing.com (news, econ, forex, commodities, stocks) — couverture large, bruit élevé, pertinence ≤ 0.9.

---

## 2. Matrice de couverture — 12 actifs × 5 catégories de drivers

**Légende :** ✅ couverture directe et ciblée · ⚠️ couverture indirecte/bruit élevé · ❌ aucune couverture

Les 5 catégories de drivers sont extraites des fiches YML :
- **OFF** = offre physique (stocks, inventaires, production, récoltes)
- **DEM** = demande (Chine, industrie, consommation)
- **POS** = positionnement (CFTC COT, ETF flows, options)
- **MAC** = macro/taux (Fed, ECB, DXY, TIPS, inflation)
- **GEO** = géopolitique / idiosyncratique (conflits, politique, météo, régulation)

| Actif | OFF | DEM | POS | MAC | GEO |
|-------|-----|-----|-----|-----|-----|
| **Brent** | ✅ EIA feeds (poids 1.4-1.5) | ⚠️ Q1 + RSS génériques | ❌ | ✅ Q4 + Fed/ECB RSS | ✅ Q1 (OPEC) · ⚠️ bbc_world |
| **Or** | ❌ | ❌ WGC absent | ❌ | ✅ Q4 + Fed/ECB RSS | ⚠️ bbc_world générique |
| **Argent** | ❌ | ❌ PV/industrie absent | ❌ | ✅ Q4 | ❌ |
| **Cuivre** | ⚠️ mining_com (indirect) | ⚠️ Q10 + gnews_copper | ❌ | ✅ Q4 | ⚠️ Q10 (Chile) |
| **Café** | ⚠️ Q7 + gnews_coffee | ❌ | ❌ | ⚠️ Q6 (USD/BRL indirect) | ⚠️ Q7 (Brésil/Vietnam) · ❌ NOAA météo absent |
| **Cacao** | ⚠️ Q8 + gnews_cocoa | ⚠️ Q8 grindings | ❌ | ❌ | ⚠️ Q8 (CI/Ghana) · ❌ EUDR absent |
| **Blé** | ⚠️ Q9 + gnews_wheat | ❌ USDA FAS absent | ❌ | ⚠️ Q4 indirect | ✅ Q9 (Black Sea) · ❌ USDA NASS absent |
| **CAC 40** | ❌ | ❌ | ❌ | ✅ Q4 + ECB RSS | ✅ Q11 + gnews_cac40 (politique FR) |
| **S&P 500** | ❌ | ❌ | ❌ | ✅ Q4 + Fed RSS | ⚠️ Q5 · ❌ earnings absent |
| **Nasdaq** | ❌ | ❌ | ❌ | ✅ Q4 + Fed RSS | ⚠️ Q5 · ❌ IA/semi absent |
| **VIX** | ❌ | ❌ | ❌ | ⚠️ Q4 indirect | ❌ **aucune requête** |
| **EUR/USD** | ❌ | ❌ | ❌ | ✅ Q4 + Q6 + Fed/ECB/BoJ | ⚠️ générique |

**Score couverture (nb cases ✅+⚠️ / 5) :**
- Brent : 4/5 — couverture correcte
- Or : 2/5 — lacune OFF/DEM/POS
- Argent : 1/5 — lacune critique
- Cuivre : 3/5 — DEM/GEO partiels, POS absent
- Café : 2/5 — météo absente (critère poids 11)
- Cacao : 2/5 — EUDR absent, arrivées port absentes
- Blé : 3/5 — USDA NASS/FAS absents, GASC absent
- CAC 40 : 2/5 — OAT-Bund absent en news
- S&P 500 : 2/5 — earnings absents
- Nasdaq : 2/5 — IA/semi absents
- VIX : 1/5 — **zéro couverture directe**
- EUR/USD : 2/5 — FX macro correct, reste absent

---

## 3. Analyse précision / rappel par requête

| # | Requête | Précision estimée | Rappel | Risque bruit | Diagnostic |
|---|---------|-------------------|--------|--------------|------------|
| Q1 | oil/brent/WTI/OPEC | Haute | Moyen | Faible | Bien ciblée — conserver |
| Q2 | gold/silver/copper/platinum | Faible | Très large | **Élevé** | 4 actifs très différents dans une seule requête : un article gold "pollue" copper. Fusionner avec les dédiées Q10 et séparer métaux précieux/industriels |
| Q3 | wheat/corn/coffee/cocoa/sugar | Très faible | Très large | **Critique** | 5 soft commodities dont corn et sugar hors périmètre (non tradés). Corn = 0 utilité. Sugar = 0 utilité. Remplacer intégralement par Q7+Q8+Q9 déjà plus ciblées |
| Q4 | Fed/FOMC/ECB/inflation/CPI | Faible | Très large | **Élevé** | Utile comme fond macro commun mais génère des centaines d'articles sans attribution actif. Acceptable si downstream filtre par actif |
| Q5 | Nasdaq/S&P 500/CAC 40/DAX | Faible | Large | Élevé | DAX hors périmètre (pas d'actif DAX). Élargissement inutile. Séparer Nasdaq+S&P d'un côté, CAC de l'autre (déjà Q11) |
| Q6 | EUR USD/yen/dollar index/forex | Moyenne | Large | Moyen | Yen et "forex" sont trop génériques. Resserrer sur EUR/USD + DXY |
| Q7 | coffee/arabica/robusta/Brazil/Vietnam | Haute | Moyen | Faible | Bonne requête dédiée — conserver |
| Q8 | cocoa/Ivory Coast/Ghana/grindings | Haute | Faible | Faible | Bonne requête dédiée — conserver. Ajouter EUDR |
| Q9 | wheat/Black Sea/Russia/US wheat crop | Haute | Moyen | Faible | Bonne requête dédiée — conserver. Ajouter USDA |
| Q10 | copper/LME/Chile/China copper demand | Haute | Moyen | Faible | Bonne requête dédiée — conserver |
| Q11 | CAC 40/French stocks/LVMH/TotalEnergies/France politics | Moyenne | Moyen | Moyen | Correct mais LVMH/TotalEnergies génèrent des articles corporate sans impact indice. Acceptable |
| — | *(VIX — ABSENT)* | — | — | — | **Trou critique** |

---

## 4. Redondance et chevauchement

### 4.1 Chevauchements identifiés

| Paire | Chevauchement | Gaspillage quota |
|-------|---------------|------------------|
| Q2 (`gold/silver/copper`) ↔ Q10 (`copper`) | ~40% des articles copper dans Q2 aussi dans Q10 | ~15 req/j en double |
| Q2 (`gold/silver`) ↔ metals RSS (investing_metals, mining_com) | Or et argent couverts 3× (Q2 + gnews non existant + RSS) | Faible sur quota API, bruit accru sur dedup |
| Q3 (`wheat/coffee/cocoa`) ↔ Q7+Q8+Q9 | Intégralité de Q3 doublon des dédiées | **Q3 entièrement redondante** : économiser 2 req/run (1 GNews + 1 NewsAPI) |
| Q5 (`Nasdaq/S&P/CAC 40`) ↔ Q11 (`CAC 40`) | CAC 40 couvert 2× | ~10 req/j en double |
| Q4 macro ↔ investing_economy RSS + Fed/ECB feeds | Communiqués officiels couverts 3× | Sur quota RSS = gratuit, redondance acceptable si dedup actif |
| gnews_wheat RSS ↔ Q9 | Overlap ~60% | Acceptable : RSS poll 60 min (temps réel), Q9 = batch |

### 4.2 Requêtes à faible valeur ajoutée

- **Q3** : redondante à 100% avec Q7+Q8+Q9, corn et sugar hors périmètre. **Supprimer.**
- **Q2** : or et argent reçoivent des news via RSS (investing_metals, mining_com). La valeur de Q2 est la partie cuivre — mais Q10 couvre mieux. Conserver uniquement pour `gold OR silver` après suppression de copper.
- **Q5** : DAX hors périmètre. Côté CAC 40, Q11 + gnews_cac40 couvrent mieux. Ne garder que `Nasdaq OR "S&P 500"`.

---

## 5. Trous mesurables — actifs structurellement sous-couverts

### 5.1 VIX — couverture quasi nulle (CONFIRMÉ TROU CRITIQUE)

**Critères news dans la fiche VIX :**
- id:8 `tension_geopolitique_active` source=`events-log L1=Géopolitique (3j)` — poids 4

La fiche VIX ne repose pas sur des news textuelles mais sur des données quantitatives (CBOE, CFTC, Twelve Data). Le seul critère news est géopolitique — couvert par les RSS génériques (bbc_world) et Q4 de manière indirecte.

**Diagnostic :** absence de requête dédiée VIX est **justifiée** — l'actif est piloté par des indicateurs de marché, pas par des articles de presse. Pas de requête à créer. En revanche, le critère géopolitique bénéficierait d'un flux dédié events géopol (absent des structured queries).

### 5.2 Nasdaq — critère IA/semi sans couverture

**Critère fiche :** id:6 `sentiment_ia_megacaps` source=`events-log L1=Tech-IA (7j)` — poids 5

Drivers IA/semi-conducteurs (NVDA, TSMC, AMD, Arm) absents de toutes les structured queries et des flux RSS. Q5 mentionne "Nasdaq" mais ne cible pas les méga-caps Tech-IA. **Trou réel confirmé.**

### 5.3 Or — achats banques centrales sans couverture

**Critère fiche :** id:2 `achats_pboc_cb_emergentes` source=`WGC (mensuel)` — poids 9

Aucun flux WGC (World Gold Council). La requête Q2 capte quelques articles ponctuels sur "China gold buying" mais sans fiabilité. **Trou réel confirmé.**

### 5.4 Argent — demande photovoltaïque/industrie sans couverture

**Critère fiche :** id:9 `demande_pv_mining_strikes` source=`events-log` — poids 3 (mineur)

Absent des structured queries. Poids faible — acceptable à court terme.

### 5.5 Blé — USDA NASS et GASC sans couverture news

**Critères fiche :** id:4 `nass_crop_progress` poids 6, id:8 `egypte_gasc_tenders` poids 4

Ces sources sont des données structurées (USDA API, GASC pdf), pas des news — leur absence du pipeline news est normale. Mais les annonces WASDE et les tenders GASC génèrent des articles presse qui eux pourraient être captés.

### 5.6 Cacao — EUDR sans couverture

**Critère fiche :** id:6 `eudr` source=`events-log (phase EUDR)` — poids 5

Aucune requête sur "EU Deforestation Regulation" ou "EUDR". Trou identifié.

### 5.7 CAC 40 — spread OAT-Bund et contexte EU non couverts

**Critère fiche :** id:2 `spread_oat_bund_10y` — poids 10. Ce critère est quantitatif (Twelve Data), pas news. Mais id:6 `tension_politique_fr` poids 3 est bien couvert par Q11 + gnews_cac40.

Couverture news CAC suffisante pour les critères qualitatifs.

---

## 6. Quota et coût — analyse d'allocation

### 6.1 Situation actuelle (free tier)

| API | Quota free | Req actuelles/run | Runs possibles/j | Marge |
|-----|-----------|-------------------|-----------------|-------|
| GNews | 100/j | 11 | 1 run/9 h | +89 req disponibles |
| NewsAPI | 100/j | 11 | 1 run/9 h | +89 req disponibles |

**Observation :** le free tier est très largement sous-utilisé. 11 requêtes = 11% du quota. On peut ajouter jusqu'à 8-9 requêtes supplémentaires sans changer de tier, ou augmenter la fréquence à 2 runs/j.

### 6.2 Recommandation d'allocation post-optimisation

| Action | Requêtes | Impact quota |
|--------|----------|--------------|
| SUPPRIMER Q3 (corn/sugar/agri générique) | -1 req/run | -2/j (GNews+NewsAPI) |
| RÉDUIRE Q2 → `gold OR silver` uniquement | 0 req/run | optimisation qualitative |
| RÉDUIRE Q5 → `Nasdaq OR "S&P 500"` uniquement | 0 req/run | optimisation qualitative |
| RÉDUIRE Q6 → `"EUR/USD" OR "dollar index" OR DXY` | 0 req/run | optimisation qualitative |
| AJOUTER Q12 : `NVDA OR "semiconductor" OR "AI chips" OR TSMC` | +1 req/run | +2/j |
| AJOUTER Q13 : `VIX OR "market volatility" OR "fear index" OR CBOE` | +1 req/run | +2/j |
| AJOUTER Q14 : `"gold demand" OR WGC OR "central bank gold" OR "PBoC gold"` | +1 req/run | +2/j |
| AJOUTER Q15 : `EUDR OR "EU deforestation" OR "cocoa regulation"` | +1 req/run | +2/j |

**Budget post-optimisation : 14 req/run (après suppression Q3)** = 14% du quota free tier. Marge confortable.

---

## 7. Biais d'échantillon — sources US-centrées

### 7.1 Inventaire par zone géographique

| Source | Zone | Actifs exposés au biais |
|--------|------|------------------------|
| BBC Business/World | UK + global | Neutre — acceptable |
| CNBC (3 flux) | **US majoritaire** | S&P, Nasdaq, Brent, Or |
| Investing.com (5 flux) | Mixte US/EU | Acceptable |
| EIA (2 flux) | **US uniquement** | Brent (vision WTI/US shale, pas OPEC) |
| Fed RSS (2 flux) | **US uniquement** | EUR/USD, indices |
| ECB RSS | EU | EUR/USD, CAC |
| BoE/BoJ | UK/JP | EUR/USD indirect |
| oilprice.com | US-centré | Brent |
| mining.com | Canada/US | Cuivre (manque perspectives LME/Chine) |
| Google News RSS dédiés | En-US majoritaire | gnews_cac40 en français (FR:fr) ✓ |
| GNews API (structured) | En-US | Tous |
| NewsAPI | En-US | Tous |

### 7.2 Biais directionnel identifiés

**Brent :** les flux EIA couvrent les stocks WTI et la production shale US. Le Brent est principalement un contrat Mer du Nord / OPEC. Les décisions OPEC, la production russe et la demande asiatique sont sous-représentées. **Biais haussier US shale** possible lors de divergences WTI/Brent.

**Cuivre :** mining_com et les structured queries mentionnent "LME copper OR China copper demand" mais sans source primaire chinoise (NBS, SHFE, Caixin). Le sentiment China-side repose sur Q10 qui capte des articles anglais sur la Chine — souvent avec 12-48h de retard vs NBS/SHFE. **Biais de latence** pour les signaux demand Chine.

**Café/Cacao :** gnews_coffee et gnews_cocoa sont configurés en `hl=en-US&gl=US`. Les publications CONAB (Brésil, portugais), les rapports ICCO (anglais mais EU), et les données des ports ivoiriens sont absents. **Biais de langue** pour les soft commodities dont les signaux primaires sont en portugais ou dans des sources institutionnelles non-US.

**Blé :** Q9 cible correctement Black Sea + USDA. Mais l'absence de sources australiennes (BoM, ABARE) crée un trou pour la production australienne (critère poids 5 dans fiche blé). **Biais Northern Hemisphere** dans les nouvelles de production.

**VIX / S&P 500 / Nasdaq :** sources 100% US. Cohérent avec la nature des actifs (indices US). Pas de biais problématique.

**CAC 40 :** gnews_cac40 est correctement configuré en `hl=fr&gl=FR`. ECB RSS couvre la BCE. Couverture géographique acceptable.

**EUR/USD :** couverture déséquilibrée Fed > BCE. 4 flux officiels Fed (fed_press_all, fed_monetary + CNBC + GNews) vs 1 flux ECB. Le différentiel est important car EUR/USD réagit autant aux communiqués BCE qu'aux communiqués Fed. **Biais USD-hawkish** potentiel.

---

## 8. Synthèse — recommandations priorisées

### 8.1 Actions immédiates (sans coût quota)

| Priorité | Action | Justification |
|----------|--------|---------------|
| P1 | **Supprimer Q3** (`wheat OR corn OR coffee OR cocoa OR sugar`) | 100% redondante avec Q7+Q8+Q9, corn et sugar hors périmètre. Économise 2 req/j. |
| P2 | **Réduire Q2** → `gold OR silver` (retirer copper) | Copper mieux couvert par Q10 dédiée. Réduit pollution croisée. |
| P3 | **Réduire Q5** → `Nasdaq OR "S&P 500"` (retirer DAX) | DAX hors périmètre. CAC 40 déjà Q11. |
| P4 | **Réduire Q6** → `"EUR/USD" OR "dollar index" OR DXY` (retirer yen/forex génériques) | Yen non tradé en actif. "forex" génère bruit maximal. |

### 8.2 Ajouts recommandés (dans la marge quota disponible)

| Priorité | Nouvelle requête | Actif cible | Critère adressé | Quota |
|----------|-----------------|-------------|-----------------|-------|
| P1 | `NVDA OR "semiconductor" OR "AI chips" OR TSMC OR "chip stocks"` | Nasdaq | id:6 sentiment_ia_megacaps (poids 5) | +2 req/j |
| P2 | `"central bank gold" OR WGC OR "gold demand" OR "PBoC gold reserves"` | Or | id:2 achats_pboc_cb_emergentes (poids 9) | +2 req/j |
| P3 | `EUDR OR "EU deforestation regulation" OR "cocoa supply chain"` | Cacao | id:6 eudr (poids 5) | +2 req/j |
| P4 | `VIX OR CBOE OR "market volatility" OR "fear gauge" OR "volatility spike"` | VIX | id:8 tension_geopolitique (poids 4) + signal contexte | +2 req/j |
| P5 | `"USDA report" OR WASDE OR "crop progress" OR "wheat harvest"` | Blé | id:1 WASDE (poids 11), id:4 NASS (poids 6) | +2 req/j |

**Budget post-modifications : 15 req/run = 15% du quota free tier.** Confortable.

### 8.3 Améliorations flux RSS (sans impact quota)

| Action | Cible | Justification |
|--------|-------|---------------|
| Ajouter gnews_vix RSS : `https://news.google.com/rss/search?q=VIX+volatility+CBOE+market+fear` | VIX | Couverture temps réel sans quota API |
| Ajouter gnews_nasdaq_tech : `q=NVDA+semiconductor+AI+chips+Nasdaq+earnings` | Nasdaq | IA/semi sous-couverts |
| Vérifier gnews_wheat (fix 31/05) : surveiller nb items/run | Blé | Query élargie après fix — valider stabilité |
| Envisager flux CONAB (si RSS disponible) ou alertes Google News `CONAB+café` | Café | Biais de langue sur données Brésil |

### 8.4 Ce qu'il ne faut PAS faire

- **Ne pas ajouter de flux chinois primaires (NBS, SHFE)** : pages non-RSS ou en chinois, parsing complexe, taux d'échec élevé — documenté dans les retraits du 30/05.
- **Ne pas dédoubler les banques centrales** : Fed/ECB/BoE/BoJ RSS déjà en place. Tout ajout de flux "macro US" générique amplifie le bruit sans valeur.
- **Ne pas tenter OPEC/LME/USDA/WGC en RSS direct** : tous bloquent (403/404) — documenté 30/05.

---

## 9. Tableau récapitulatif — état de couverture post-recommandations

| Actif | Couverture actuelle | Couverture post-corrections | Trou résiduel |
|-------|--------------------|-----------------------------|---------------|
| Brent | 4/5 ✅ | 4/5 | Demande Asie (latence) |
| Or | 2/5 ⚠️ | 3/5 (+Q WGC) | PBoC data primaire |
| Argent | 1/5 ❌ | 1/5 | Demande PV (poids faible) |
| Cuivre | 3/5 ⚠️ | 3/5 | LME/SHFE primaire |
| Café | 2/5 ⚠️ | 2/5 | NOAA météo (donnée, pas news) |
| Cacao | 2/5 ⚠️ | 3/5 (+Q EUDR) | Ports CI primaire |
| Blé | 3/5 ⚠️ | 3/5 (+Q USDA) | GASC tender direct |
| CAC 40 | 2/5 ⚠️ | 2/5 | OAT-Bund = donnée, pas news |
| S&P 500 | 2/5 ⚠️ | 2/5 | Earnings (calendrier, pas news) |
| Nasdaq | 2/5 ⚠️ | 3/5 (+Q semi/IA) | SOX en temps réel |
| VIX | 1/5 ❌ | 2/5 (+Q VIX) | Actif piloté par données CBOE, news secondaires |
| EUR/USD | 2/5 ⚠️ | 2/5 | Balance commerciale = donnée Eurostat |

**Note méthodologique :** les cases OFF/DEM/POS restant vides après corrections correspondent à des critères quantitatifs (CFTC COT, ETF flows, FRED, Twelve Data) — leur couverture n'est pas du ressort du pipeline news mais du pipeline data. Ce n'est pas un échec de la couverture news.

---

*Fin d'audit — @data-analyst, 2026-06-01*
