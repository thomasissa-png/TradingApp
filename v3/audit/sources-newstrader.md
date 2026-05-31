# Audit couverture informationnelle — News Trader (12 actifs)

> Recul desk : on vise la JUSTESSE DIRECTIONNELLE de tendance (24h/7j/1m), pas la vitesse.
> Les drivers de tendance sont presque tous des FLUX/POSITIONNEMENT/POLITIQUE, pas des titres mainstream.
> Légende type : `RSS`=flux news · `Q`=requête GNews/NewsAPI ciblée · `API`=donnée chiffrée.

## Audit par actif

| Actif | A déjà (utile) | Manque critique (driver de tendance) | Type | Prio |
|---|---|---|---|---|
| **Pétrole/Brent** | EIA RSS+API, oilprice, COT, géopol via events-log | Décisions **OPEC+** (quota/JMMC), rapports mensuels **IEA + OPEC MOMR** (demande/offre), spread term-structure | RSS+Q / API | P1 |
| **Or** | COT, DXY, VIX, géopol | **Taux réels 10Y (FRED DFII10)** = driver #1, **achats CB / WGC**, flux ETF | API / Q | P1 |
| **Argent** | COT, ratio G/S, PMI | Taux réels (FRED), **inventaires COMEX/SLV**, demande PV/industrielle (proxy via cuivre+solar) | API / Q | P2 |
| **Cuivre** | gnews_copper, mining.com, COT | **Inventaires LME+SHFE** (trend), **PMI Caixin Chine**, grèves mines Chili/Pérou (events-log alimenté ?) | API / RSS | P1 |
| **Blé** | gnews_wheat, COT, géopol mer Noire | **USDA WASDE/NASS** (stocks-to-use, crop progress), **NOAA drought**, GASC tenders | API / RSS | P1 |
| **Café** | gnews_coffee, COT | **Météo Brésil (gel Minas) + Vietnam**, **stocks ICE certifiés**, USD/BRL (Twelve Data ✓) | API / RSS | P1 |
| **Cacao** | gnews_cocoa, COT | **Météo + arrivées ports CI/Ghana**, **grindings trimestriels**, statut **EUDR** | API / Q | P1 |
| **S&P 500** | CNBC, COT, VIX, 10Y | **HY credit spread (FRED ICE BofA OAS)**, breadth, AAII sentiment, flux ETF SPY | API / Q | P2 |
| **Nasdaq** | CNBC, SOX, news Tech-IA | Taux réels (FRED), **sentiment méga-caps/IA structuré** (events-log L1 alimenté ?), VXN | API / Q | P2 |
| **CAC 40** | gnews_cac40, ECB RSS | **Spread OAT-Bund** (Twelve Data ✓), **politique FR (budget/dissolution)** ciblée, news LVMH/Total/banques | Q / API | P1 |
| **EUR/USD** | Fed/ECB/BoE RSS, COT, DXY | **Différentiel taux 2Y/10Y US-DE (FRED)**, **CME FedWatch probas**, Eurostat | API / Q | P2 |
| **VIX** | mainstream, géopol, COT | **CBOE Put/Call + SKEW + VVIX**, term-structure VIX/VIX3M (Twelve Data ✓), calendrier macro (GATE) | API | P1 |

## Diagnostic des 4 sous-couverts (crédibilité minimale)

- **Agri (café/cacao/blé)** : aujourd'hui = uniquement Google News RSS = bruit narratif sans driver. Pour être crédible il FAUT :
  (1) **météo zones-clés** (Open-Meteo déjà câblé → ajouter points Minas/Vietnam/CI-Ghana/Midwest), (2) **USDA WASDE/NASS** (blé) en RSS ou parsing, (3) **stocks certifiés ICE** (café/cacao), (4) **grindings/arrivées ports** via requête ciblée. Sans météo+stocks, on ne capte PAS la tendance agri.
- **Cuivre** : ajouter **inventaires LME/SHFE** (proxy possible via mining.com + requête dédiée) et **PMI Caixin** = les 2 vrais drivers ; le reste est bruit macro.
- **CAC 40** : driver = **OAT-Bund (risque politique FR)** + **poids sectoriel luxe/banques**. Requête FR ciblée "budget/déficit/dissolution/Moody's France" >> news génériques Paris.
- **VIX** : c'est un actif de DÉRIVÉS — sans **CBOE (Put/Call, SKEW, VVIX)** et le **calendrier macro** (FOMC/CPI/NFP), on ne fait que suivre le spot. Données chiffrées >> news.

## Optimisation (recul) : MIEUX cibler > PLUS de sources

- **Retirer le bruit** : `investing_stocks` duplique `investing_econ` (même URL news_25.rss) → doublon mort. `bbc_world` (0.7) apporte peu d'edge directionnel.
- **Edge disproportionné** : les **données officielles** (EIA 1.5, Fed/ECB 1.5, COT, FRED) portent 80% du signal directionnel de tendance. Le mainstream sert au CONTEXTE et au GATE géopol, pas au signal fin.
- **Le vrai trou n'est pas le volume de news mais les APIs chiffrées manquantes** : FRED (taux réels, HY OAS, différentiels), CBOE, USDA, inventaires (LME/COMEX/ICE), CME FedWatch. C'est là que se joue la tendance.
- **events-log** : vérifier qu'il est réellement ALIMENTÉ pour L1=Géopolitique, L2=OPEC/France-politique/Iran, L1=Tech-IA — plusieurs fiches en dépendent et la table ne montre que 3 hits CAC / 3 Copper.

## Top 5 ajouts à plus fort impact (priorisés)

1. **FRED API** (gratuit, illimité) → DFII10 (taux réels = driver Or/Argent/Nasdaq), ICE BofA HY OAS (S&P), différentiels 2Y/10Y US-DE (EUR/USD). `API`. Touche 5 actifs. **Impact #1.**
2. **Open-Meteo sur points agri précis** (déjà câblé, juste ajouter coords) → Minas Gerais, Vietnam Central Highlands, Côte d'Ivoire/Ghana, US Plains/Midwest. `API`. Débloque café/cacao/blé (~0 aujourd'hui).
3. **CBOE data** (Put/Call, SKEW, VVIX) + **term-structure VIX/VIX3M**. `API`. Rend le VIX crédible (20→signal réel).
4. **USDA WASDE/NASS** (RSS ou scrape mensuel) + **stocks certifiés ICE café/cacao**. `RSS/API`. Cœur de la tendance agri.
5. **Requêtes ciblées affinées** : OPEC+/IEA/MOMR (pétrole), LME+SHFE inventories+Caixin (cuivre), OAT-Bund/budget FR (CAC). `Q`. Remplacer les requêtes larges par des requêtes drivers.

## Synthèse (4 puces)

- **Mainstream = saturé, données chiffrées = le trou réel.** Ajouter des APIs (FRED, CBOE, USDA, inventaires, Open-Meteo agri) ferait plus pour la justesse directionnelle que 50 flux RSS de plus.
- **Pareto des sources** : EIA, Fed/ECB, COT, FRED portent l'essentiel du signal de tendance ; le reste est contexte/GATE. Pondérer en conséquence et élaguer les doublons (investing_stocks).
- **Les 4 sous-couverts ne deviendront crédibles que par la DONNÉE** (météo + stocks + inventaires + spreads), pas par plus de Google News.
- **Vérifier l'alimentation d'events-log** : plusieurs critères de fiches (OPEC, géopol, France-politique, Tech-IA) en dépendent ; s'il est vide, ces critères sont morts quelle que soit la qualité des flux.
