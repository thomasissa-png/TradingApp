# Audit requêtes news — œil « News Trader senior » (desk macro/commodities)

> **Mission** : auditer la PERTINENCE des requêtes/mots-clés news (`STRUCTURED_QUERIES` GNews/NewsAPI + `EARLY_SIGNAL_FEEDS` + `RSS_FEEDS`) vs l'objectif unique du système : **justesse de la TENDANCE directionnelle** sur 12 actifs × 3 horizons. **La vitesse de capture est hors-sujet** (un retard de 4h sur une news n'est pas un problème — cf. `project-context.md`). On juge donc : est-ce que les mots-clés ramènent le **bon driver de tendance** par actif, ni trop étroit, ni noyé dans le bruit ?
>
> Auteur : audit desk. Date : 2026-06-01. Périmètre : `v3/scripts/config.py`, 12 fiches `v3/config/fiches/*.yml`.

## TL;DR (verdict desk)

- Couverture **commodities** (pétrole, café, cacao, blé, cuivre) = solide, requêtes dédiées + RSS spécialisés alignés sur les vrais drivers (météo, stocks, géopol producteur). Bon travail de desk soft-commodities.
- **Trou structurel sur le bloc « equities/vol US »** : Nasdaq (driver = Nvidia/IA/semi/SOX/export chips) et VIX (driver = risk-off/volatilité) **ne sont captés par AUCUNE requête dédiée**. S&P 500 idem partiel (seulement noyé dans la requête #5). Ce sont les 3 actifs où le système est le plus aveugle au **catalyseur de tendance**.
- **Partiels notables** : Or (achats banques centrales / PBoC = driver de tendance long terme non requêté en mots-clés), Argent (demande solaire/PV + industrielle), EUR/USD (différentiel de taux / BCE-Fed capté seulement via macro générique).
- **Bruit** : `DAX` (requête #5) n'est pas un de nos 12 actifs → pollue ; requêtes #1-#6 trop larges (« forex », « dollar », « inflation ») ramènent du tout-venant qui dilue le signal directionnel par actif.

**Top 3 corrections prioritaires** (détaillées en fin de doc) :
1. **Créer une requête Nasdaq/semi/IA** (Nvidia, semiconductors, SOX, AI capex, chip export) + RSS dédié — actif aujourd'hui sans capteur de driver.
2. **Créer une requête VIX/risk-off** (volatility, VIX, risk-off, market selloff, safe haven) — la vol n'a aucun mot-clé.
3. **Nettoyer / scinder les requêtes fourre-tout** : retirer `DAX`, sortir une requête S&P dédiée, resserrer Or (ajouter « central bank gold buying / PBoC »).

---

## Tableau d'audit par actif

Note = pertinence des mots-clés news vs **driver de tendance** de l'actif. `news_zone` rappelle que la news n'est qu'un critère événementiel (le cœur numérique = prix/COT/météo/EIA, déjà couvert hors news).

| # | Actif | Vrai(s) driver(s) de tendance desk | Requête(s)/feed(s) qui le captent | Note |
|---|---|---|---|---|
| 1 | **Pétrole (Brent)** | OPEC+ quotas, stocks EIA/API, géopol Moyen-Orient, demande Chine, DXY | #1 `oil OR brent OR WTI OR OPEC` + EIA feeds + oilprice | **OK** |
| 2 | **Or** | Taux réels US, **achats banques centrales (PBoC)**, DXY, risk-off, flux ETF | #2 `gold...` + #4 (Fed/inflation) ; mais achats CB **non requêtés** | **PARTIEL** |
| 3 | **Argent** | Or (corrélation), **demande PV/solaire + industrielle**, ratio Gold/Silver, COMEX | #2 `gold OR silver...` + mining_com ; demande solaire/PV **non requêtée** | **PARTIEL** |
| 4 | **Cuivre** | PMI Chine, stocks LME/SHFE, grèves mines Chili/Pérou, infra/constru | #10 dédié (`LME / Chile mine / China demand`) + mining_com | **OK** |
| 5 | **Café** | Météo Brésil (gel/sécheresse), stocks ICE, USD/BRL, Vietnam robusta | #7 dédié + gnews_coffee | **OK** |
| 6 | **Cacao** | Météo + arrivées port CI/Ghana, broyages (grindings), EUDR | #8 dédié + gnews_cocoa | **OK** |
| 7 | **Blé** | WASDE stocks-to-use, sécheresse Midwest/Plaines, géopol mer Noire, tenders Égypte | #9 dédié + gnews_wheat | **OK** (manque Égypte/GASC, Australie) |
| 8 | **CAC 40** | Politique FR/budget, spread OAT-Bund, LVMH/luxe, TotalEnergies | #11 dédié + gnews_cac40 | **OK** |
| 9 | **S&P 500** | Fed/taux, VIX/risk-off, crédit HY, breadth, méga-caps | #5 (noyé avec Nasdaq/CAC/**DAX**) + #4 macro | **PARTIEL** |
| 10 | **Nasdaq** | **Nvidia/IA/semi (SOX), capex IA, export chips Chine**, taux réels, méga-caps | **AUCUNE requête dédiée** — seulement « Nasdaq » dans #5 | **TROU** |
| 11 | **VIX** | **Volatilité / risk-off / selloff / safe-haven / stress crédit** | **AUCUNE requête** — aucun mot-clé volatilité | **TROU** |
| 12 | **EUR/USD** | **Différentiel taux Fed-BCE**, DXY, USD/JPY, stress EZ (OAT-Bund) | #6 (`EUR USD OR forex...` trop large) + #4 (Fed/ECB) | **PARTIEL** |

**Bilan** : 5 OK nets (commodities dédiées) · 4 PARTIELS (Or, Argent, S&P, EUR/USD) · **2 TROUS (Nasdaq, VIX)**.

---

## 1. Driver de tendance par actif & captation (détail desk)

**Pétrole (Brent) — OK.** Les vrais moteurs de tendance d'un desk énergie (décisions OPEC+, surprises stocks EIA hebdo, escalade/détente Moyen-Orient, demande chinoise via PMI, DXY) sont couverts par la requête #1 *et* surtout par les feeds officiels EIA + oilprice (poids 1.5/1.0). C'est le seul actif avec une source primaire de données fondamentales en flux. Rien à corriger.

**Or — PARTIEL.** La fiche identifie clairement le driver de tendance structurel : **achats des banques centrales (PBoC + CB émergentes, 12m cumulés)**. Or aucune requête ne cherche « central bank gold buying / PBoC gold reserves / gold demand WGC ». Le seul capteur news est `gold` (#2) + le bloc Fed/taux (#4) pour les taux réels. On capte donc la jambe « taux réels » mais on rate la jambe « demande officielle » — qui est précisément le moteur de la tendance pluri-mensuelle sur l'or 2024-2026. À combler.

**Argent — PARTIEL.** Capté en ricochet de l'or (`silver` dans #2) et via mining_com pour l'offre. Mais le driver différenciant argent vs or — **demande photovoltaïque/solaire + demande industrielle + grèves mines** (explicite dans la fiche, critère « Demande photovoltaïque + mining strikes ») — n'a aucun mot-clé. Un desk métaux suivrait « silver solar demand / photovoltaic silver / silver industrial deficit ». À combler.

**Cuivre — OK.** Requête dédiée #10 bien ciblée sur les 3 vrais moteurs : stocks LME, grèves mines Chili, demande Chine. Complétée par mining_com. Aligné fiche (PMI Chine, inventaires, strikes, infra). RAS, amélioration mineure possible (Pérou, « China stimulus / property »).

**Café — OK.** Requête #7 + gnews_coffee couvrent le driver n°1 absolu : **météo Brésil (gel/sécheresse Minas Gerais)** + robusta Vietnam + récolte. Aligné fiche. Le seul affinage utile : « frost Brazil / drought Minas Gerais » explicite (le gel est LE catalyseur de tendance violente sur l'arabica).

**Cacao — OK.** Requête #8 + gnews_cocoa : Côte d'Ivoire, Ghana, broyages (grindings). Aligné fiche. Manque mineur : EUDR (régulation déforestation EU) et maladies (Black Pod, Swollen Shoot) — drivers structurels d'offre suivis par le desk.

**Blé — OK (avec angles morts).** Requête #9 couvre mer Noire / Russie / récolte US. Mais la fiche liste 2 drivers non requêtés : **tenders GASC Égypte** (premier importateur mondial — signal de demande directionnel) et **météo Australie (dryland)** + WASDE. À enrichir.

**CAC 40 — OK.** Requête #11 + gnews_cac40 : politique FR/budget (driver dominant 2024-2026 via spread OAT-Bund), LVMH (luxe = poids lourd indice), TotalEnergies. Bien pensé pour un indice à forte sensibilité politique domestique. RAS.

**S&P 500 — PARTIEL.** Le driver de tendance (Fed/taux, régime VIX, spreads crédit HY, breadth) est capté indirectement par #4 (Fed/CPI) mais **l'actif n'a pas de requête propre** : il partage #5 avec Nasdaq, CAC et DAX, ce qui dilue. Aucun mot-clé sur « earnings / credit spreads / risk-off » spécifiquement actions US. À sortir en requête dédiée.

**Nasdaq — TROU.** C'est l'angle mort le plus coûteux. Le driver de tendance du Nasdaq 100 en 2024-2026 est **massivement idiosyncratique tech/IA** : Nvidia, semi-conducteurs (SOX), capex IA des hyperscalers, restrictions d'export de puces vers la Chine, sentiment méga-caps (la fiche liste explicitement « Sentiment IA / méga-caps », « SOX trend », « Concentration top 7 »). Or **aucun de ces termes n'est requêté** : seul le mot « Nasdaq » apparaît, noyé dans #5. Un mouvement Nvidia/export-ban — principal catalyseur de tendance de l'indice — passe sous le radar news. **Requête dédiée indispensable.**

**VIX — TROU.** Le VIX n'a **aucun mot-clé news**, alors que son driver est par nature événementiel/sentiment : pics de volatilité, épisodes risk-off, sell-offs, fuite vers les valeurs refuges, chocs macro/géopol. La fiche s'appuie sur des critères numériques (term structure, put/call, SKEW) mais le contexte news (« market selloff / volatility spike / risk-off / safe haven ») renforcerait la justesse directionnelle, surtout sur 24h. **Requête dédiée à créer.**

**EUR/USD — PARTIEL.** Driver de tendance = **différentiel de politique monétaire Fed vs BCE** + DXY + stress zone euro. Capté par #4 (Fed/ECB/inflation) et #6, mais #6 (`EUR USD OR yen OR dollar index OR forex`) est trop générique et ramène du bruit FX multi-paires. Manque les mots-clés directionnels précis : « ECB rate decision / Fed rate path / rate differential / Lagarde / Powell ». À resserrer.

---

## 2. Bruit / hors-objectif

- **`DAX` (requête #5)** : l'Allemagne (DAX) **n'est pas un de nos 12 actifs**. Chaque article DAX consomme du quota GNews/NewsAPI et entre dans le pool de dédup/scoring sans cible. À retirer. (Le S&P et le CAC, eux, sont des actifs — DAX est le seul intrus.)
- **Requête #6 `EUR USD OR yen OR dollar index OR forex`** : `yen` et `forex` sont des aimants à bruit. Nous tradons EUR/USD, pas USD/JPY ni le FX en général. Le `yen` n'est utile que comme *proxy risk* (déjà un critère numérique). « forex » ramène tout le tout-venant cambiste. Resserrer sur EUR/USD + drivers de taux.
- **Requêtes #1-#3 OR-larges** : `gold OR silver OR copper OR platinum` et `wheat OR corn OR coffee OR cocoa OR sugar` incluent `platinum`, `corn`, `sugar` — **non tradés**. Pas critique (proches thématiquement, peuvent co-citer un actif suivi) mais elles font doublon avec les requêtes dédiées #7-#10 plus fines. Elles servent de filet large ; acceptable, mais ne pas s'y fier comme capteur de tendance par actif.
- **Requête #4 `Fed OR FOMC OR ECB OR inflation OR CPI`** : très large mais **légitime** — c'est le macro-driver transverse (or, S&P, Nasdaq, EUR/USD, blé/DXY en dépendent tous). À garder, c'est un capteur multi-actifs, pas du bruit.
- **Risque de dilution global** : les requêtes #1-#6 sont des « buckets » thématiques larges ; le signal directionnel *par actif* repose surtout sur les requêtes dédiées #7-#11 et les RSS spécialisés. Les actifs **sans requête dédiée (Nasdaq, VIX, S&P, EUR/USD, Or-volet-CB, Argent-volet-PV)** sont donc structurellement sous-captés : leur seule chance d'apparaître est de surnager dans un bucket large. C'est la cause racine des PARTIEL/TROU.

---

## 3. Mots-clés manquants critiques (par actif)

Mots-clés que suivrait un desk macro/commodities et que la config rate aujourd'hui :

- **Nasdaq** : `Nvidia`, `semiconductor` / `chip`, `SOX` / `Philadelphia semiconductor`, `AI capex` / `AI spending`, `chip export` / `export controls China`, `TSMC`, `mega-cap tech earnings`, `hyperscaler`. → AUCUN présent.
- **VIX** : `volatility` / `VIX`, `risk-off`, `market selloff` / `stock rout`, `safe haven`, `flight to quality`, `circuit breaker`, `credit stress`. → AUCUN présent.
- **S&P 500** : `S&P 500 earnings`, `Wall Street`, `US stocks` (en propre), `credit spreads` / `high yield`, `recession` / `soft landing`. → seulement « S&P 500 » noyé dans #5.
- **Or** : `central bank gold buying`, `PBoC gold reserves`, `WGC gold demand`, `gold ETF flows`, `real yields`. → volet banques centrales absent.
- **Argent** : `silver solar demand` / `photovoltaic silver`, `silver industrial demand`, `silver deficit`, `gold-silver ratio`. → volet demande PV absent.
- **EUR/USD** : `ECB rate decision`, `Fed rate path` / `Powell`, `Lagarde`, `rate differential`, `eurozone PMI`. → captés seulement via macro générique.
- **Blé** : `GASC tender` / `Egypt wheat import`, `Australia wheat drought`, `WASDE`, `Argentina wheat`. → demande/Australie absentes.
- **Cacao** : `EUDR` / `EU deforestation`, `Black Pod` / `Swollen Shoot`, `cocoa grindings` (présent dans #8 ✓). → volets maladie/régulation absents.
- **Café** : `frost Brazil` / `Brazil frost`, `drought Minas Gerais`. → utile pour le catalyseur de tendance violent (gel).
- **Cuivre** : `Peru copper`, `China stimulus` / `China property`, `copper smelter`. → enrichissements mineurs.
- **Pétrole / Cuivre / Or / Blé / EUR/USD** partagent le driver **DXY** : bien câblé en numérique (critère `DXY trend 20j`), pas besoin de mot-clé news dédié.

---

## 4. Requêtes à reformuler — formulations exactes proposées

### A. `STRUCTURED_QUERIES` (GNews/NewsAPI) — diff proposé

**Retirer / modifier :**

```python
# AVANT (#5) : DAX hors-périmètre + S&P/Nasdaq noyés
"Nasdaq OR S&P 500 OR CAC 40 OR DAX",
# APRÈS : scinder, retirer DAX, donner une requête propre à chaque indice US
"S&P 500 OR Wall Street OR US stocks OR high yield credit spread OR recession",
```

```python
# AVANT (#6) : trop large (yen, forex)
"EUR USD OR yen OR dollar index OR forex",
# APRÈS : resserré sur EUR/USD + différentiel de politique monétaire
"EUR USD OR euro dollar OR ECB rate OR Fed rate path OR Lagarde OR Powell OR rate differential",
```

```python
# AVANT (#2) : volet banques centrales de l'or absent
"gold OR silver OR copper OR platinum",
# APRÈS : ajouter le driver de tendance structurel or + demande PV argent
"gold OR silver OR copper OR central bank gold buying OR PBoC gold OR silver solar demand",
```

**Ajouter (nouvelles requêtes dédiées — comble les 2 TROUS) :**

```python
# NOUVEAU — Nasdaq / semi / IA (driver de tendance n°1 de l'indice)
"Nvidia OR semiconductor OR chip export OR SOX index OR AI capex OR TSMC OR mega-cap tech",
# NOUVEAU — VIX / risk-off / volatilité
"VIX OR market volatility OR risk-off OR stock market selloff OR safe haven OR flight to quality",
# NOUVEAU (optionnel) — enrichissement blé demande/Australie
"Egypt GASC wheat tender OR Australia wheat OR WASDE OR Argentina wheat crop",
```

### B. `EARLY_SIGNAL_FEEDS` (RSS) — ajouts proposés

```python
# Semi/tech pour Nasdaq (Google News dédié)
("gnews_semi",   "https://news.google.com/rss/search?q=Nvidia+OR+semiconductor+OR+%22chip+export%22+OR+%22AI+capex%22&hl=en-US&gl=US&ceid=US:en", 3600),
# Volatilité / risk-off pour VIX
("gnews_vix",    "https://news.google.com/rss/search?q=VIX+OR+%22market+volatility%22+OR+%22risk-off%22+OR+selloff&hl=en-US&gl=US&ceid=US:en", 3600),
# Or — achats banques centrales
("gnews_gold_cb","https://news.google.com/rss/search?q=%22central+bank+gold%22+OR+%22PBoC+gold%22+OR+%22gold+demand%22&hl=en-US&gl=US&ceid=US:en", 3600),
```

> Pondérer ces nouvelles sources dans `SOURCE_WEIGHTS` au niveau des autres gnews dédiés (0.8). Penser à incrémenter `PROMPT_VERSION` si l'ajout de catégories change le mapping article→actif côté DeepSeek.

---

## 5. Verdict & priorisation

**La couverture mots-clés est-elle alignée sur l'objectif « justesse de la tendance » ? → NON, partiellement.**

Alignée et même excellente sur les **soft commodities et l'énergie** (pétrole, café, cacao, blé, cuivre) : requêtes dédiées + RSS spécialisés + feeds officiels (EIA) qui captent les vrais drivers de tendance (météo producteur, stocks, géopol, OPEC, PMI Chine). C'est un travail de desk commodities de bon niveau.

**Désalignée sur le bloc actions/vol US** : Nasdaq et VIX — 2 des 12 actifs — n'ont **aucun capteur news de leur driver de tendance**. Pour le Nasdaq, dont la tendance 2024-2026 est dictée par Nvidia/IA/semi/export-chips, c'est un angle mort majeur : le système peut manquer le contexte directionnel du catalyseur dominant. Le VIX, par nature piloté par le sentiment/risk-off, n'a aucun mot-clé. S&P, Or (volet CB), Argent (volet PV), EUR/USD (volet politique monétaire) sont partiels. Et un intrus (`DAX`) consomme du quota pour rien.

Comme l'objectif est la **justesse directionnelle** (pas la vitesse), un mot-clé manquant n'est pas un retard rattrapable : c'est un driver **structurellement absent** du faisceau de critères événementiels — donc un risque d'erreur de direction sur l'actif concerné, exactement ce que le système cherche à éviter.

### Top 3 corrections prioritaires

1. **[P0] Requête + RSS Nasdaq/semi/IA** — `Nvidia OR semiconductor OR chip export OR SOX OR AI capex OR TSMC` + `gnews_semi`. Comble le trou le plus coûteux (driver dominant de l'indice non capté).
2. **[P0] Requête + RSS VIX/risk-off** — `VIX OR market volatility OR risk-off OR selloff OR safe haven` + `gnews_vix`. La volatilité n'a aujourd'hui aucun mot-clé.
3. **[P1] Nettoyer & scinder les buckets larges** — retirer `DAX`, sortir une requête S&P dédiée, resserrer #6 (EUR/USD vs Fed-BCE), enrichir #2 (achats CB or + demande PV argent).

> Conforme à l'objectif `project-context.md` : ces corrections renforcent la **justesse de la tendance** (couverture du driver), pas la vitesse. À valider par Thomas avant modif de `config.py` (commandement « pas de modif silencieuse des prompts/poids » + bump `PROMPT_VERSION`).

---

## Handoff

- **Livrable** : `v3/audit/audit-requetes-news-newstrader.md` (ce fichier).
- **Constat** : couverture commodities OK ; **2 TROUS** (Nasdaq, VIX) + **4 PARTIELS** (Or, Argent, S&P 500, EUR/USD) ; 1 intrus (`DAX`).
- **Action attendue** : si Thomas valide, appliquer le diff section 4 à `v3/scripts/config.py` (`STRUCTURED_QUERIES`, `EARLY_SIGNAL_FEEDS`, `SOURCE_WEIGHTS`) → @fullstack, avec bump `PROMPT_VERSION` et tests verts (360+).
- **Hors périmètre** : ce audit ne touche PAS la vitesse de capture (hors-sujet par `project-context.md`) ni le scoring numérique (déjà couvert par les fiches). Il porte uniquement sur la pertinence des mots-clés news comme capteurs de driver de tendance.
- **Lien Phase 2 news** : cohérent avec le flag `nature` (structurel/ponctuel) prévu — capter le bon driver est prérequis à bien le classer.
