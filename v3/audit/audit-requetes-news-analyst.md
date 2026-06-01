# Audit — Couverture requêtes news vs 12 actifs (Round 3)
**Date :** 2026-06-01
**Auteur :** @data-analyst
**Périmètre :** STRUCTURED_QUERIES (14 requêtes), EARLY_SIGNAL_FEEDS (22 flux), RSS_FEEDS (10 flux)
**Objectif :** évaluer la capacité du pipeline news à alimenter les critères `source: events-log` des 12 fiches de positionnement
**Changelog :** Round 3 — C1 Fed/ECB dégroupés, C2 gnews_silver_industrial ajouté, C3 Q5 S&P earnings-focused, C4 gnews_ecb_policy ajouté, C5 gnews_wheat monitoré + bonus café (gel/sécheresse Brésil), blé (GASC/Australie), VIX (causes amont), Nasdaq (guidance/capex), gnews_gold_cb.

---

## NOTE GLOBALE : **9/10**

### Justification du plafond — ce que le dernier point représente

Le plafond ~9,5/10 posé en round 2 reste pertinent. Le dernier 0,5-1 point est structurellement inatteignable via RSS/API news :
- **CFTC COT** (positionnement futures) — fichiers hebdo CFTC, pas de flux news
- **ETF flows** GLD/SLV — Bloomberg/FRED, pas de flux news
- **CBOE VIX index** — donnée marché temps réel Twelve Data
- **GASC tenders directs** — PDF institutionnel égyptien, hors RSS
- **NBS/SHFE cuivre Chine** — sources chinoises bloquées (403/404 constatés 30/05)
- **CONAB café Brésil** — publications en portugais, hors périmètre en-US

La note 9/10 signifie : **tout ce qui est couvrable par requêtes news l'est désormais, sans redondance sémantique critique ni biais d'attribution identifié**.

### Raison pour laquelle la note n'est pas 9,5

Un trou résiduel subsiste sur un actif — cf. section 5. Il est faible (poids driver bas) mais documenté.

---

## 1. Inventaire canonique — Round 3

### 1.1 STRUCTURED_QUERIES — 14 requêtes (~14% free tier)

| # | Requête (résumée) | Actifs ciblés | Delta R2→R3 |
|---|-------------------|---------------|-------------|
| Q1 | `oil OR brent OR WTI OR OPEC OR crude inventories` | Brent | inchangée |
| Q2 | `gold price OR central bank gold buying OR WGC OR PBoC gold OR real yields` | Or | inchangée |
| Q3 | `silver price OR silver industrial demand OR solar photovoltaic OR gold silver ratio` | Argent | inchangée |
| Q4a | `Fed OR FOMC OR interest rate decision OR federal funds rate OR Powell speech` | USD-macro | **DÉGROUPÉ ✅ C1** |
| Q4b | `ECB OR European Central Bank OR Eurozone inflation OR Lagarde speech OR ECB rate` | EUR-macro | **DÉGROUPÉ ✅ C1** |
| Q5 | `S&P 500 earnings OR corporate earnings beat OR EPS surprise OR earnings guidance OR market correction` | S&P 500 | **Resserrée ✅ C3** |
| Q6 | `EUR USD OR ECB rate decision OR Fed ECB divergence OR dollar index` | EUR/USD | inchangée |
| Q7 | `coffee prices OR arabica OR robusta OR Brazil harvest OR frost Brazil OR drought Minas Gerais` | Café | **+gel/sécheresse ✅ bonus** |
| Q8 | `cocoa prices OR Ivory Coast OR Ghana cocoa OR cocoa grindings OR EUDR deforestation` | Cacao | inchangée |
| Q9 | `wheat prices OR Black Sea grain OR Russia wheat OR US wheat crop OR WASDE OR Egypt GASC OR Australia wheat` | Blé | **+GASC/Australie ✅ bonus** |
| Q10 | `copper prices OR LME copper OR Chile mine OR China copper demand` | Cuivre | inchangée |
| Q11 | `CAC 40 OR French stocks OR LVMH OR TotalEnergies OR France politics budget` | CAC 40 | inchangée |
| Q12 | `Nvidia OR semiconductor OR AI chips OR TSMC OR chip export controls OR earnings guidance OR data center capex` | Nasdaq | **+guidance/capex ✅ bonus** |
| Q13 | `stock market volatility OR VIX OR risk-off OR market selloff OR war OR escalation OR sanctions OR bank failure OR sovereign default` | VIX | **+causes amont ✅ bonus** |

**Coût quota estimé :** 14 req × 2 (GNews + NewsAPI) = 28 req/run = **14% free tier** — marge 86 req/j.

### 1.2 EARLY_SIGNAL_FEEDS — 22 flux

| Catégorie | Flux | Actifs couverts | Delta R3 |
|-----------|------|-----------------|----------|
| Énergie | eia_today_in_energy, eia_press_releases, oilprice | Brent | inchangé |
| Métaux | mining_com, investing_commodities, investing_metals | Or, Argent, Cuivre | inchangé |
| Banques centrales | fed_press_all, fed_monetary, ecb_press, boe_news, boj_news | USD/EUR macro | inchangé |
| Macro | investing_economy | tous | inchangé |
| Google News RSS sous-couverts | gnews_coffee, gnews_cocoa, gnews_wheat, gnews_copper, gnews_cac40, gnews_nasdaq, gnews_vix | Café, Cacao, Blé, Cuivre, CAC 40, Nasdaq, VIX | inchangé |
| **Ajouts R3** | **gnews_ecb_policy, gnews_silver_industrial, gnews_gold_cb** | **EUR/USD biais, Argent OFF, Or CB** | **+3 flux ✅ C2+C4+bonus** |

---

## 2. Matrice de couverture — 12 actifs × 5 catégories de drivers

**Légende :** ✅ couverture directe et ciblée · ⚠️ couverture indirecte / bruit élevé · ❌ aucune couverture

Les 5 catégories de drivers :
- **OFF** = offre physique (stocks, inventaires, production, récoltes)
- **DEM** = demande (Chine, industrie, consommation)
- **POS** = positionnement (CFTC COT, ETF flows, options) — structurellement hors périmètre news
- **MAC** = macro/taux (Fed, ECB, DXY, TIPS, inflation)
- **GEO** = géopolitique / idiosyncratique (conflits, politique, météo, régulation)

| Actif | OFF | DEM | POS | MAC | GEO | Score /5 | Delta R2 |
|-------|-----|-----|-----|-----|-----|----------|----------|
| **Brent** | ✅ EIA (1.4-1.5) | ⚠️ Q1 générique | ❌ | ✅ Q4a Fed | ✅ Q1 OPEC | 4/5 | = |
| **Or** | ⚠️ mining_com | ✅ Q2 WGC/PBoC + gnews_gold_cb | ❌ | ✅ Q4a/Q4b | ⚠️ bbc_world | **4/5** | +0,5 ✅ |
| **Argent** | ✅ gnews_silver_industrial (temps réel) | ✅ Q3 PV/solaire | ❌ | ✅ Q4a/Q4b | ⚠️ Q3 grèves minières | **4/5** | **+1 ✅ C2** |
| **Cuivre** | ⚠️ mining_com | ✅ Q10 + gnews_copper | ❌ | ✅ Q4a/Q4b | ⚠️ Q10 Chile | 4/5 | = |
| **Café** | ✅ Q7 + gnews_coffee + gel Brésil | ⚠️ Q7 consommation indirect | ❌ | ⚠️ Q6 USD indirect | ✅ Q7 Brésil météo | **3/5** | **+1 ✅ bonus** |
| **Cacao** | ⚠️ Q8 + gnews_cocoa | ⚠️ Q8 grindings | ❌ | ❌ | ✅ Q8 EUDR + CI/Ghana | 3/5 | = |
| **Blé** | ✅ Q9 WASDE + gnews_wheat | ✅ Q9 GASC/Australie | ❌ | ⚠️ Q4a indirect | ✅ Q9 Black Sea | **4/5** | **+1 ✅ bonus** |
| **CAC 40** | ❌ | ❌ | ❌ | ✅ Q4b ECB + ecb_press | ✅ Q11 + gnews_cac40 | 2/5 | = |
| **S&P 500** | ❌ | ✅ Q5 earnings/EPS | ❌ | ✅ Q4a Fed + fed_monetary | ⚠️ Q5 market correction | **3/5** | **+1 ✅ C3** |
| **Nasdaq** | ❌ | ✅ Q12 IA/semi + capex | ❌ | ✅ Q4a Fed | ✅ Q12 + gnews_nasdaq | 3/5 | = |
| **VIX** | ❌ | ❌ | ❌ | ⚠️ Q4a/Q4b indirect | ✅ Q13 causes amont + gnews_vix | 2/5 | = |
| **EUR/USD** | ❌ | ❌ | ❌ | ✅ Q4a + Q4b + Q6 + 5 flux CB | ⚠️ Q6 géopolitique partiel | **3/5** | **+1 ✅ C1+C4** |

**Note :** les cases ❌ OFF/DEM/POS sur les actifs indices et FX correspondent à des critères quantitatifs (CFTC COT, ETF flows, Twelve Data, FRED) — hors périmètre news. Non imputables au pipeline.

---

## 3. Analyse précision / rappel — état Round 3

| # | Requête | Précision R3 | Rappel R3 | Risque bruit | Diagnostic |
|---|---------|-------------|-----------|--------------|------------|
| Q1 | oil/brent/WTI/OPEC | Haute | Moyen | Faible | Stable. Conserver. |
| Q2 | gold/WGC/PBoC/real yields | Haute | Bon | Faible | Stable. ✅ |
| Q3 | silver industrial/solar/ratio | Haute | Bon | Faible | Enrichie par gnews_silver_industrial RSS en parallèle. ✅ |
| Q4a | Fed/FOMC/federal funds/Powell | Haute | Bon | Faible | Dégroupage = gain attribution majeur. Driver USD-hawkish identifiable. ✅ |
| Q4b | ECB/European CB/Eurozone/Lagarde | Haute | Bon | Faible | Dégroupage = gain attribution majeur. Driver EUR-hawkish identifiable. ✅ |
| Q5 | S&P earnings/EPS surprise/guidance/correction | Haute | Bon | Faible | Resserrement efficace. "Wall Street" éliminé = -30% bruit estimé. ✅ |
| Q6 | EUR USD/ECB rate/Fed-ECB divergence | Haute | Bon | Faible | Q4a+Q4b apportent le macro ; Q6 gère le FX différentiel. Complémentaire, pas redondant. ✅ |
| Q7 | coffee/arabica/robusta/Brazil/gel/sécheresse | Haute | Bon | Faible | Ajout météo Minas Gerais = driver OFF manquant comblé. ✅ |
| Q8 | cocoa/Ivory Coast/Ghana/grindings/EUDR | Haute | Bon | Faible | Stable. ✅ |
| Q9 | wheat/Black Sea/WASDE/GASC/Australia | Haute | Bon | Faible | +GASC+Australie = demande importateur couverte. Score OFF+DEM blé à 4/5. ✅ |
| Q10 | copper/LME/Chile/China | Haute | Moyen | Faible | Stable. Trou NBS/SHFE insoluble accepté. |
| Q11 | CAC 40/LVMH/TotalEnergies/France | Moyenne | Moyen | Moyen | Corporate bruit modéré acceptable. Score 2/5 = actif sous-piloté par news. |
| Q12 | Nvidia/semi/AI chips/TSMC/guidance/capex | Haute | Bon | Faible | +guidance/capex = pivot baissier mid-cycle couvert. ✅ |
| Q13 | VIX/risk-off/selloff + war/escalation/sanctions/bank failure | Haute | Bon | Moyen | Causes amont ≠ symptômes : capter la peur AVANT le spike = gain analytique réel. Bruit potentiel sur "war" atténué par conjonction sémantique dans le scoring. ✅ |

---

## 4. Redondance résiduelle

| Paire | Chevauchement | Verdict |
|-------|---------------|---------|
| Q4a (Fed) ↔ fed_monetary RSS | Communiqués Fed couverts 2×, poids 1.5 vs 0.7 | Conserver — RSS = primary source (1.5), Q4a = contexte narratif (0.7). Dédup absorbe. |
| Q4b (ECB) ↔ ecb_press RSS + gnews_ecb_policy | ECB couvert 3× | Acceptable — ecb_press = communiqués officiels, gnews_ecb_policy = minutes/discours/macro EU, Q4b = narratif. Niveaux distincts. |
| Q13 (VIX causes) ↔ gnews_vix RSS | ~40% overlap thématique | Complémentaires (temporalités différentes). Conserver. |
| Q12 (Nasdaq) ↔ gnews_nasdaq RSS | ~40% overlap | Complémentaires. Conserver. |
| Q2 (gold) ↔ investing_metals + gnews_gold_cb | Or couvert 3× | investing_metals = métaux bulk, gnews_gold_cb = CB gold ciblé, Q2 = narratif macro-or. Niveaux distincts. Conserver. |
| Q3 (silver) ↔ gnews_silver_industrial + investing_metals | Argent couvert 3× | Même logique — complémentaires. |

**Conclusion :** aucune redondance sémantique critique. Tous les doublons identifiés sont soit des doublons temporels (RSS batch vs temps réel), soit des doublons de niveau (primaire officiel vs narratif vs ciblé). Le dédup Jaccard (seuil 0,65) absorbe les doublons de titre sans perte de signal.

---

## 5. Trou résiduel après Round 3

### 5.1 Trou actionnable résiduel (unique)

| Actif | Trou | Driver | Poids | Status |
|-------|------|--------|-------|--------|
| **CAC 40** | Earnings individuels (SBF 120 mid-cap) absents — Q11 cible LVMH + TotalEnergies mais pas les annonces bénéfices mid-cap | GEO | Faible | Acceptable — les two heavyweights couverts (LVMH 10% du CAC, TotalEnergies 8%). Un gnews_cac_earnings pourrait combler mais ROI faible. |

Ce trou est la raison pour laquelle la note est 9/10 et non 9,5/10 : le CAC reste à 2/5 sur la couverture drivers quand tous les autres actifs majeurs ont progressé.

### 5.2 Trous structurels — hors périmètre news (inchangés, documentés)

| Actif | Critère | Source primaire |
|-------|---------|----------------|
| Tous | CFTC COT (positionnement) | CFTC API |
| Or / ETF | ETF flows (GLD, SLV) | Bloomberg / FRED |
| VIX | CBOE VIX index | Twelve Data API |
| Blé | GASC tenders primaires (confirmation officielle) | GASC PDF — Q9 couvre l'écho news |
| Café | NOAA El Niño / météo Brésil granulaire | NOAA API — Q7 couvre l'écho news |
| EUR/USD | Balance commerciale EU primaire | Eurostat API |
| CAC 40 | Spread OAT-Bund | Twelve Data |
| Cuivre | NBS/SHFE données primaires | Bloqué 403/404 — latence 12-48h acceptée |

---

## 6. Biais d'échantillon — état Round 3

| Biais | R2 | R3 | Verdict |
|-------|----|----|---------|
| **USD-hawkish EUR/USD** : 4 flux Fed vs 1 ECB | Confirmé | **Corrigé ✅** — Q4b dédié + gnews_ecb_policy + ecb_press (poids 1.5) = 3 flux ECB actifs | Résolu C1+C4 |
| **WTI vs Brent** : EIA = vision shale US | Résiduel | Non corrigé | Acceptable — Q1 couvre OPEC, Brent reste l'actif de référence |
| **Café/Cacao en-US** : CONAB portugais absent | Structurel | Non corrigé | Structurel — pipeline data CONAB séparé à prévoir |
| **Cuivre Chine latence** : NBS/SHFE bloqués | Structurel | Non résolu | Insoluble RSS |
| **VIX piloté data** : news secondaires vs CBOE primaire | Documenté | Inchangé | Acceptable — Q13 causes amont améliore le prédictif |
| **CAC 40 mid-cap absent** | Non identifié R2 | Trou résiduel identifié | Acceptable poids faible — voir section 5.1 |

**Biais résiduels actifs : 1 (CAC 40 mid-cap, faible) + 2 structurels inactionnables (CONAB, SHFE).**

---

## 7. Score de couverture post-Round 3

| Actif | Score R1 | Score R2 | Score R3 | Delta R2→R3 | Trou résiduel principal |
|-------|----------|----------|----------|-------------|------------------------|
| Brent | 4/5 | 4/5 | 4/5 | = | Demande Asie (latence, insoluble) |
| Or | 2/5 | 4/5 | 4/5 | = (+gnews_gold_cb) | PBoC data primaire (pipeline data) |
| Argent | 1/5 | 3/5 | **4/5** | **+1 ✅** | POS CFTC (pipeline data) |
| Cuivre | 3/5 | 4/5 | 4/5 | = | LME/SHFE primaire (insoluble) |
| Café | 2/5 | 2/5 | **3/5** | **+1 ✅** | CONAB/météo granulaire (structurel) |
| Cacao | 2/5 | 3/5 | 3/5 | = | Ports CI primaire (insoluble) |
| Blé | 3/5 | 3/5 | **4/5** | **+1 ✅** | GASC confirmation (écho news couvert) |
| CAC 40 | 2/5 | 2/5 | 2/5 | = | OAT-Bund + mid-cap earnings |
| S&P 500 | 2/5 | 2/5 | **3/5** | **+1 ✅** | POS/ETF flows (pipeline data) |
| Nasdaq | 2/5 | 3/5 | 3/5 | = | SOX temps réel (acceptable) |
| VIX | 1/5 | 2/5 | 2/5 | = (causes amont = gain qualitatif) | Actif piloté CBOE, news secondaires |
| EUR/USD | 2/5 | 2/5 | **3/5** | **+1 ✅** | Balance EU primaire (Eurostat) |

**Score global couverture : 39/60 → 65% (R2 : 34/60 → 57% ; R1 : 26/60 → 43%). Progression cumulée +22 points.**

---

## 8. Synthèse — justification de la note 9/10

### Ce qui justifie 9 (et non 8 ou 9,5)

**Gains Round 3 (+1,5 pt vs R2 estimé à 7,5) :**

1. **C1 — Dégroupage Fed/ECB** : c'était le défaut méthodologique structurel le plus grave. Une requête Q4 unique rendait le scoring downstream aveugle à la direction macro. Q4a (USD-hawkish) et Q4b (EUR-hawkish) permettent désormais une attribution actif correcte pour EUR/USD, indices et métaux. Gain le plus impactant du round.

2. **C4 + C1 combinés** : le biais USD-hawkish documenté en round 1, non corrigé en round 2, est éliminé. La couverture BCE passe de 1 flux (ecb_press) à 3 niveaux : ecb_press (communiqués officiels, poids 1.5) + Q4b (narratif macro EU) + gnews_ecb_policy (minutes, discours, GDP EU). Symétrie Fed/ECB atteinte.

3. **C3 — Q5 S&P earnings** : retirer "Wall Street" et "US stocks" n'est pas cosmétique. Ces deux termes généraient du bruit de masse (toute mention d'un indice US) qui noyait le signal earnings (EPS surprise, guidance revision). La requête est désormais driver-isée, non actif-isée.

4. **C2 — gnews_silver_industrial** : l'Argent était l'actif le plus déséquilibré (1/5 en R1). Atteindre 4/5 en R3 avec une couverture OFF+DEM+MAC est le gain le plus rapide (3 min config.py, 0 quota API).

5. **Bonus Café, Blé, Nasdaq, VIX** : les ajouts spontanés (gel Brésil, GASC, data center capex, escalation/sanctions) comblent des drivers de second rang qui déclenchaient des faux négatifs — un choc climatique sur le café n'était pas détecté avant le spike prix. C'est précisément le cas d'usage du pipeline.

**Ce qui reste incomplet :**

- CAC 40 stagne à 2/5. Les drivers actionnables (news mid-cap, flux earnings SBF 120 intraday) existent mais le ROI d'ajout est faible comparé aux actifs liquides. Une Q14 dédiée `SBF 120 OR bénéfices OR résultats OR "profit warning" France` pourrait porter le CAC à 3/5 — effort 3 min, gain marginal.
- Trous structurels (CFTC, CBOE, SHFE, CONAB) : inchangés, hors périmètre, non imputables.

**Pourquoi pas 9,5 :** le CAC 40 = le seul actif du périmètre sans progression en 3 rounds. Un actif bloqué à 2/5 sur 3 rounds consécutifs empêche la note plafond, même si son poids dans le portefeuille est faible.

---

## 9. Seule correction résiduelle actionnable

| Priorité | Correction | Effort | Impact | Impact quota |
|----------|-----------|--------|--------|-------------|
| **P3** | Ajouter Q14 : `SBF 120 OR "profit warning" France OR "résultats trimestriels" CAC OR "chiffre d'affaires" LVMH OR Airbus OR Hermès` | 3 min | CAC 40 : 2/5 → 3/5 | +2 req/run → 16% free tier |
| ~~C5~~ | gnews_wheat monitoré (source_monitor actif) | En cours | Validation stabilité query | — |

Toutes les corrections P1 et P2 du round 2 ont été appliquées. Le pipeline est en état de production.

---

*Fin d'audit Round 3 — @data-analyst, 2026-06-01*
