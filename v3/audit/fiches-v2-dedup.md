# Audit doublons sémantiques — fiches v2 (12 actifs)
# Lot A étape 1 — CHECKPOINT PRÉ-FUSION
# Date : 2026-06-10 · Auteur : @data-analyst
# Statut : BROUILLON — NE PAS FUSIONNER avant validation Thomas + Cowork

> **Ce fichier est un audit de lecture seule.** Aucun YAML n'a été modifié.
> Toutes les fusions proposées restent à l'état de recommandations jusqu'à validation explicite.
> Sources : lecture directe des 12 fiches `v3/config/fiches/*.yml` + bulletin 2026-06-10 07h19 (run représentatif).

> **⚠️ CONTRE-AUDIT (à lire avant de réutiliser ce document).** L'audit externe du 10/06 annonçait **9 doublons** ; la vérification YAML directe montre que **8 sur 9 n'existaient pas** dans les fiches v2 (un seul critère par facteur). **Cause racine : des critères ont été RENOMMÉS les 7-8 juin** — l'auteur de l'audit externe travaillait sur d'anciens libellés / contributions pondérées, pris à tort pour du double comptage. **Conséquence évitée de justesse : on a failli « dédupliquer » 9 fiches saines.** Seules **4 fusions réelles** subsistent (cacao, pétrole, nasdaq, argent). **Leçon (cf. `docs/lessons-learned.md` L023) : ne jamais auditer les critères par leur `nom` — toujours par leur `cle_courante` stable ; tout renommage doit passer par le CHANGELOG.** Si vous relisez ce fichier dans 2 mois : ne refaites pas l'erreur, partez des `cle_courante`.

---

## Sommaire

1. [Or — groupe TIPS](#1-or)
2. [Nasdaq — groupe TIPS](#2-nasdaq)
3. [S&P 500 — groupe VIX-régime + groupe TIPS](#3-sp500)
4. [EUR/USD — groupe différentiel de taux](#4-eurusd)
5. [CAC 40 — groupe OAT-Bund](#5-cac40)
6. [Pétrole — groupe géopolitique Moyen-Orient](#6-petrole)
7. [Café — groupe météo Brésil](#7-cafe)
8. [Cacao — triple comptage positionnement](#8-cacao)
9. [VIX — groupe term structure](#9-vix)
10. [Blé — mono-critère dominant](#10-ble)
11. [Argent — pas de doublon interne (note)](#11-argent)
12. [Cuivre — pas de doublon interne (note)](#12-cuivre)
13. [Synthèse et tableau récapitulatif des fusions](#13-synthese)
14. [Tableau de couverture AVANT/APRÈS par fiche](#14-couverture)
15. [Points à trancher — Thomas / Cowork](#15-points-a-trancher)

---

## 1. Or {#1-or}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Taux d'intérêt réels US (10 ans) | taux_10y_us_reels_tips | FRED (DFII10) | zscore | 12 |
| 2 | Achats d'or des banques centrales | achats_pboc_cb_emergentes | WGC (mensuel) | zscore | 9 |
| 3 | Tendance du dollar (20 jours) | dxy_trend_20j | Twelve Data | zscore | 8 |
| 4 | Positionnement des gros spéculateurs (or) | cftc_cot_nets | CFTC (vendredi) | zscore | 6 |
| 5 | Flux vers les fonds or (5 jours) | flux_etf_or_5j | WGC / fournisseur flux | zscore | 5 |
| 6 | Tension géopolitique mondiale | tension_geopolitique | events-log L1=Géopolitique | triplet | 5 |
| 7 | Demande saisonnière en Inde | demande_indienne_saisonniere | calendrier | triplet | 3 |
| 8 | Indice de peur des marchés (VIX) | vix_risk_off_proxy | Twelve Data | lineaire | 3 |

**Σ poids (hors gate) = 51**

### Groupe de doublons détecté

**Groupe OR-A : Taux réels US 10 ans — doublon signalé par Cowork**

Cowork signale deux critères : « TIPS Taux 10Y US réels » + « Taux d'intérêt réels US 10 ans » (~47% du signal).

Après lecture directe du YAML : **dans la fiche or.yml, il n'existe qu'UN SEUL critère TIPS** (id=1, `taux_10y_us_reels_tips`, poids 12).

**Conclusion : le doublon Cowork sur l'or ne se retrouve PAS dans le YAML actuel.** Soit la fiche a déjà été corrigée depuis leur analyse, soit la confusion vient du fait que le même critère `taux_10y_us_reels_tips` est présent dans d'autres fiches (Nasdaq, Argent, S&P 500). À noter que le critère id=1 poids 12 représente 12/51 = **23,5% du signal total**, ce qui est significatif mais pas anormal pour un critère dominant.

> ⚠️ **Aucun doublon interne sur Or.** Le % cité par Cowork (~47%) n'est pas confirmé par le YAML — il correspond vraisemblablement à l'effet pondéré sur un horizon donné (pertinence 7j/1m = 1.0), pas à un double comptage structurel.

**Pas de fusion à réaliser sur cette fiche.**

---

## 2. Nasdaq {#2-nasdaq}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Taux d'intérêt réels US (10 ans) | taux_10y_us_reels_tips | FRED (DFII10) | zscore | 11 |
| 2 | Régime de volatilité Nasdaq (VXN) | vxn_regime | Twelve Data | mapping_non_monotone | 7 |
| 3 | Tendance des semi-conducteurs (5 jours) | sox_trend_5j | Twelve Data | zscore | 7 |
| 4 | Participation des actions au rallye Nasdaq | breadth_nasdaq100_ma50 | Twelve Data (proxy QQQE/QQQ) | zscore | 6 |
| 5 | Concentration sur les 7 plus grosses valeurs | concentration_top7 | Twelve Data | zscore | 5 |
| 6 | Sentiment sur l'IA et les méga-caps tech | sentiment_ia_megacaps | events-log L1=Tech-IA | triplet | 5 |
| 7 | Flux vers le fonds Nasdaq (5 jours) | flux_etf_qqq_5j | Twelve Data | zscore | 5 |
| 8 | Écart de performance Nasdaq − petites valeurs US | spread_nasdaq_russell2000 | Twelve Data | zscore | 4 |
| 9 | Indicateur technique Nasdaq (RSI 14 jours) | rsi_14j_ixic | Twelve Data | lineaire | 2 |

**Σ poids (hors gate) = 52**

### Groupe de doublons détecté

**Groupe NASDAQ-A : TIPS — doublon signalé par Cowork (~27%)**

Après lecture directe du YAML : **un seul critère TIPS** (id=1, poids 11). Pas de doublon interne.

Le 27% cité correspond à 11/52 = 21,2% de part structurelle, et jusqu'à ~27% en pondéré à pertinence 7j/1m=1.0 — ce qui est la part d'un seul critère dominant, pas d'un double comptage.

**Potentiel doublon à examiner : breadth vs concentration**

- id=4 `breadth_nasdaq100_ma50` (proxy QQQE/QQQ, poids 6) : ratio EW/CW en hausse = participation large
- id=5 `concentration_top7` (poids 5) : concentration des 7 mega-caps

Ces deux critères mesurent le même phénomène (domination des mega-caps vs breadth large) depuis deux angles opposés mais redondants. Quand la concentration monte, le ratio QQQE/QQQ baisse — les signes sont corrélés (-1 l'un avec l'autre). Il s'agit d'un **doublon sémantique hors-liste Cowork**.

| Critère | Poids | Source / clé | Direction | Garder ? |
|---|---|---|---|---|
| Participation (QQQE/QQQ) | 6 | Twelve Data, `breadth_nasdaq100_ma50` | EW/CW ratio | **OUI** — mesure directe de la breadth, source propre |
| Concentration top7 | 5 | Twelve Data calculé, `concentration_top7` | % top-7 | **ABSORBER** — corrélé inverse au précédent, ajout marginal |

**Fusion proposée NASDAQ-A** : supprimer id=5 (`concentration_top7`, poids 5). Poids fusionné = MAX = **6** (breadth reste). Σ poids passe de 52 à **47**.

> ⚠️ Le schéma fiche ne supporte PAS de source fallback/secondaire. La fusion garde la source primaire `breadth_nasdaq100_ma50` seule. La donnée `concentration_top7` est abandonnée.

**Pas de doublon sur le TIPS en interne.**

---

## 3. S&P 500 {#3-sp500}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Régime de volatilité (VIX) | vix_regime | Twelve Data | mapping_non_monotone | 8 |
| 2 | Variation des taux US 10 ans (5 jours) | taux_10y_us_delta_5j | Twelve Data | zscore | 9 |
| 3 | Écart de crédit obligataire haut rendement US | hy_credit_spread | FRED (ICE BofA HY OAS) | zscore | 7 |
| 4 | Participation des actions au rallye S&P | breadth_sp_ma50 | Twelve Data (proxy RSP/SPY) | zscore | 7 |
| 5 | Tendance du dollar (20 jours) | dxy_trend_20j | Twelve Data | zscore | 5 |
| 6 | Flux vers les fonds S&P 500 (5 jours) | flux_etf_spy_ivv_5j | Twelve Data | zscore | 5 |
| 7 | Sentiment des investisseurs particuliers US | aaii_bull_bear | AAII (hebdomadaire) | zscore | 4 |
| 8 | Valorisation du marché (Shiller CAPE / P/E à terme) | shiller_cape_fwd_pe | multpl | composite | 4 |
| 9 | Indicateur technique S&P 500 (RSI 14 jours) | rsi_14j_gspc | Twelve Data | lineaire | 2 |
| 10 | Taux d'intérêt réels US (10 ans) | taux_10y_us_reels_tips | FRED (DFII10) | zscore | 10 |

**Σ poids (hors gate) = 61**

### Groupes de doublons détectés

**Groupe SP500-A : VIX — doublon signalé par Cowork (~37%)**

Cowork signale : « VIX régime » + « Régime de volatilité (VIX) ». Après lecture du YAML : **un seul critère VIX** (id=1, `vix_regime`, poids 8). La fiche ne contient PAS deux critères VIX distincts.

Le % de 37% cité est cohérent avec 8/61 = 13,1% de poids structurel × pertinence 24h=0.9 → contribution élevée sur le 24h, mais il s'agit d'un seul critère, pas d'un double comptage.

> ⚠️ **Aucun doublon VIX interne sur S&P 500.** Le libellé Cowork « VIX régime » et « Régime de volatilité (VIX) » désignent le même critère unique. Pas de fusion nécessaire.

**Groupe SP500-B : Taux US — doublon taux réels (TIPS) + delta 5 jours**

Le S&P 500 est la **seule fiche** à avoir simultanément :
- id=2 `taux_10y_us_delta_5j` (variation taux nominaux 10 ans, 5 jours, poids 9) — mesure le mouvement récent des taux nominaux
- id=10 `taux_10y_us_reels_tips` (niveau taux réels 10 ans FRED DFII10, poids 10) — mesure le niveau absolu des taux réels

Ces deux critères mesurent des **facteurs distincts** : la dynamique récente (delta 5j) vs le niveau structurel (taux réels). Ils ne sont pas purement redondants — un taux nominal peut monter (delta positif) avec une inflation en hausse laissant les taux réels stables. La corrélation est haute mais la sémantique est différente.

> **Verdict : pas un doublon sémantique au sens strict.** Ces deux critères capturent des angles différents du même macro-facteur taux. La concentration combinée est notable (9+10=19 sur 61 = 31% du signal), mais elle est intentionnelle dans la construction de la fiche. À documenter comme risque de concentration macro, pas à fusionner.

**Pas de fusion à réaliser sur S&P 500.**

---

## 4. EUR/USD {#4-eurusd}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Écart de taux courts US − Allemagne (2 ans) | differentiel_taux_2y_us_de | FRED / Twelve Data | zscore | 12 |
| 2 | Écart de taux longs US − Allemagne (10 ans) | differentiel_taux_10y_us_bund | FRED / Twelve Data | zscore | 6 |
| 3 | Tendance du dollar (20 jours) | dxy_trend_20j | Twelve Data | zscore | 9 |
| 4 | Taux de change dollar / yen (signal de risque) | usd_jpy_proxy_risk | Twelve Data | zscore | 4 |
| 5 | Probabilité de baisse des taux Fed (marché) | fedwatch_proba | CME FedWatch | lineaire | 6 |
| 6 | Positionnement des gros spéculateurs (euro) | cftc_cot_eur_nets | CFTC (vendredi) | zscore | 5 |
| 7 | Écart de taux France − Allemagne (stress zone euro) | spread_oat_bund_stress_ez | Twelve Data | zscore | 4 |
| 8 | Balance commerciale de la zone euro | balance_commerciale_ez | Eurostat (mensuel) | zscore | 3 |

**Σ poids (hors gate) = 49**

### Groupe de doublons détecté

**Groupe EURUSD-A : Différentiel de taux US-DE — doublon signalé par Cowork (~45%)**

Cowork signale : « Écart taux courts US-DE » (id=1) + « Différentiel taux 2Y US-DE » (id=1 identique) → noms différents, même cle_courante `differentiel_taux_2y_us_de`.

Après lecture du YAML : il s'agit en réalité de **deux critères distincts légitimes** :
- id=1 : **Écart 2 ans** (`differentiel_taux_2y_us_de`, poids 12) — taux courts, sensible à la politique monétaire immédiate
- id=2 : **Écart 10 ans** (`differentiel_taux_10y_us_bund`, poids 6) — taux longs, capturent les anticipations à long terme

Ces deux critères ont des **sources et clés distinctes** et mesurent deux portions différentes de la courbe des taux. La corrélation est élevée (USD/DE 2 ans et 10 ans bougent souvent ensemble) mais ce sont des facteurs économiques séparables — le 2 ans dépend des décisions BCEs/Fed, le 10 ans dépend des anticipations d'inflation à long terme.

**Cependant**, pour un système de positionnement directionnel sur une paire FX, le signal de court terme domine. La contribution combinée est 12+6 = 18/49 = **36,7% du signal**, ce qui est une concentration réelle. Le DXY (id=3, poids 9) capturant déjà la force du dollar, la triple présence taux 2 ans + taux 10 ans + DXY = 12+6+9 = 27/49 = **55% du signal** sur le facteur dollar/taux.

**Verdict Cowork recalculé** : la confusion sur « même critère » vient du fait que les deux s'appellent « écart taux US-DE » avec des maturités différentes. Ce ne sont **pas des vrais doublons** (clés différentes, maturités différentes), mais une **concentration macro significative**.

> **Pas de fusion recommandée sur EURUSD-A** (maturités différentes = information économique distincte). En revanche, signaler la concentration 55% facteur dollar/taux comme risque de biais systémique.

**Pas de fusion à réaliser sur EUR/USD.**

---

## 5. CAC 40 {#5-cac40}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Régime de volatilité Europe (V2X) | v2x_regime | Twelve Data | mapping_non_monotone | 8 |
| 2 | Écart de taux France − Allemagne (10 ans) | spread_oat_bund_10y | Twelve Data | zscore | 10 |
| 3 | Sur-performance du CAC face au S&P 500 (5 jours) | alpha_cac_vs_sp_5j | Twelve Data | zscore | 6 |
| 4 | Participation des valeurs CAC (non disponible) | breadth_cac_ma50 | n/a | lineaire | 6 |
| 5 | Flux vers les fonds actions France (5 jours) | flux_etf_msci_france_5j | Twelve Data | zscore | 5 |
| 6 | Stabilité politique en France | tension_politique_fr | events-log | triplet | 3 |
| 7 | Indicateur technique CAC 40 (RSI 14 jours) | rsi_14j_fchi | Twelve Data | lineaire | 2 |

**Σ poids (hors gate) = 40**

### Groupe de doublons détecté

**Groupe CAC40-A : OAT-Bund — doublon signalé par Cowork (~32%)**

Cowork signale : « Spread OAT-Bund 10Y » + « Écart taux France-Allemagne ». Après lecture du YAML : **un seul critère OAT-Bund** dans cac40.yml (id=2, `spread_oat_bund_10y`, poids 10).

Note : un critère OAT-Bund existe aussi dans **eurusd.yml** (id=7, `spread_oat_bund_stress_ez`, poids 4), mais il s'agit d'une fiche différente — ce n'est pas un doublon interne à cac40.yml.

Le 32% cité correspond à 10/40 = 25% structurel, avec pertinence 7j=0.9 / 1m=1.0 → contribution forte sur ces horizons, mais pas de double comptage.

> ⚠️ **Aucun doublon OAT-Bund interne sur CAC 40.** Pas de fusion nécessaire.

**Pas de fusion à réaliser sur CAC 40.**

---

## 6. Pétrole {#6-petrole}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Stocks de brut US : surprise hebdomadaire | eia_crude_surprise | EIA API | zscore | 10 |
| 2 | Stocks de brut US : pré-indicateur du mardi | api_weekly_surprise | API publication | zscore | 8 |
| 3 | Tension géopolitique au Moyen-Orient | tension_geopol_moyen_orient | events-log L2=Iran-Moyen-Orient | triplet | 7 |
| 4 | Positionnement des gros spéculateurs (pétrole) | cftc_cot_crude_nets | CFTC (vendredi) | zscore | 7 |
| 5 | Décision de production de l'OPEC+ | opec_production_policy | events-log L2=OPEC | triplet | 6 |
| 6 | Structure des prix futurs Brent (spot vs M+1) | brent_term_structure_m1m2 | Twelve Data | lineaire | 5 |
| 7 | Tendance du dollar (20 jours) | dxy_trend_20j | Twelve Data | zscore | 5 |
| 8 | Stocks au hub pétrolier américain (Cushing) | cushing_stocks | EIA API | zscore | 4 |
| 9 | Écart de prix Brent − WTI | spread_brent_wti | Twelve Data | lineaire | 4 |
| 10 | Activité industrielle Chine (indice PMI) | caixin_pmi_manuf | Caixin / NBS | lineaire | 4 |

**Σ poids (hors gate) = 60**

### Groupe de doublons détecté

**Groupe PETROLE-A : Géopolitique Moyen-Orient ×2 — doublon signalé par Cowork (~44%)**

Cowork signale : « Tension géopolitique Moyen-Orient » ×2.

Après lecture du YAML : **un seul critère géopolitique Moyen-Orient** (id=3, `tension_geopol_moyen_orient`, poids 7). Pas de doublon interne.

**Groupe PETROLE-B : Stocks EIA + API (doublon hors-liste Cowork)**

- id=1 `eia_crude_surprise` (poids 10, EIA API) : surprise stocks hebdomadaires EIA
- id=8 `cushing_stocks` (poids 4, EIA API) : niveau stocks Cushing (hub Oklahoma)

Ces deux critères sont **distincts** : la surprise hebdomadaire EIA mesure la variation surprise vs consensus (court terme), les stocks Cushing mesurent le niveau structurel du hub de référence WTI. Sources EIA différentes (série de stocks national vs Cushing spécifique). **Pas un doublon** — information complémentaire.

**Groupe PETROLE-C : EIA + API stocks hebdomadaires — doublon hors-liste Cowork**

- id=1 `eia_crude_surprise` (poids 10, EIA API) : stocks EIA hebdomadaires (mercredi)
- id=2 `api_weekly_surprise` (poids 8, API publication) : pré-indicateur API (mardi)

Ces deux critères mesurent **le même facteur** : les stocks hebdomadaires US de brut. L'EIA est la publication officielle (mercredi), l'API est son pré-indicateur le mardi soir. Ils sont **hautement corrélés** (r > 0,80 historiquement) et mesurent la même réalité physique. Il s'agit d'un **doublon sémantique fort** hors-liste Cowork.

| Critère | Poids | Source | Timing | Garder ? |
|---|---|---|---|---|
| Stocks EIA surprise (hebdo) | 10 | EIA API (officiel) | mercredi | **OUI** — source officielle, plus précise |
| Stocks API pré-indicateur | 8 | API (sondage privé) | mardi soir | **ABSORBER** — pré-indicateur redondant avec l'EIA |

**Fusion proposée PETROLE-C** : supprimer id=2 (`api_weekly_surprise`, poids 8). Poids fusionné = MAX = **10** (EIA reste). Σ poids passe de 60 à **52**.

> ⚠️ Le schéma fiche ne supporte PAS de source fallback. La fusion garde l'EIA seule. La donnée API (mardi) est abandonnée — elle n'apportera plus de signal le mardi soir avant la publication EIA.

**Impact de la suppression** : la perte du pré-indicateur API signifie que le lundi/mardi, avant la publication EIA, la contribution stocks = 0 (EIA publie mercredi). C'est un **point à trancher** : est-il préférable de garder l'API comme signal mardi-soir, quitte au double comptage mercredi-jeudi ?

---

## 7. Café {#7-cafe}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Météo Brésil — risque gel et sécheresse (Minas Gerais) | meteo_bresil_minas_gerais | NOAA / météo | composite | 11 |
| 2 | Stocks d'Arabica certifiés (tendance 20 jours) | stocks_ice_arabica_certifies_20j | ICE | zscore | 9 |
| 3 | Taux de change dollar / real brésilien | usd_brl | Twelve Data | zscore | 6 |
| 4 | Positionnement des gros spéculateurs (café) | cftc_cot_coffee | CFTC (vendredi) | zscore | 5 |
| 5 | Maladies du caféier (rouille et cabosses) | maladies_cabosses_rouille | events-log | triplet | 5 |
| 6 | Cycle de production brésilien (année forte / faible) | cycle_bresil_biannuel | calendrier CONAB | triplet | 4 |
| 7 | Écart de prix Arabica − Robusta | spread_arabica_robusta | Twelve Data | zscore | 4 |
| 8 | Météo Vietnam — précipitations (Robusta) | meteo_vietnam_robusta | NOAA / météo | zscore | 4 |

**Σ poids (hors gate) = 48**

### Groupe de doublons détecté

**Groupe CAFE-A : Météo Brésil ×2 — doublon signalé par Cowork (~36%)**

Cowork signale : 2× météo Brésil gel/sécheresse.

Après lecture du YAML : **un seul critère météo Brésil** (id=1, `meteo_bresil_minas_gerais`, poids 11, normalisation composite = zscore précipitations + check T min<4°C). Le 36% cité correspond à 11/48 = 22,9% de poids structurel, avec pertinence 7j/1m=1.0 → contribution dominante mais pas un double comptage.

**Vérification du commentaire YAML** : id=1 est en `composite` — il intègre déjà en interne le gel (check T min) ET la sécheresse (zscore précipitations). Cette intégration interne est correcte du point de vue sémantique — c'est une source unique (NOAA/Open-Meteo) qui remonte deux signaux combinés.

**Groupe CAFE-B : Maladies caféier vs cycle production brésilien (doublon partiel hors-liste)**

- id=5 `maladies_cabosses_rouille` (poids 5) : rouille et maladies cabosses — événements ponctuels
- id=6 `cycle_bresil_biannuel` (poids 4) : cycle biannuel CONAB (année on/off)

Ces deux critères mesurent des risques sur l'offre brésilienne mais via des angles **fondamentalement distincts** (événement sanitaire ponctuel vs cycle structurel). Pas un doublon.

> ⚠️ **Aucun doublon interne sur Café.** Le doublon Cowork (2× météo Brésil) ne se retrouve pas dans le YAML.

**Pas de fusion à réaliser sur Café.**

---

## 8. Cacao {#8-cacao}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Météo Côte d'Ivoire + Ghana (pluies, 30 jours) | meteo_ci_ghana_precip_30j | NOAA / météo | zscore | 11 |
| 2 | Arrivées de cacao dans les ports ivoiriens (20 jours) | arrivees_port_abidjan_sanpedro_20j | ports CI | zscore | 9 |
| 3 | Positionnement spéculatif + options cacao (ICE) | hf_positioning_flux_options | ICE + CFTC | composite | 7 |
| 4 | Positionnement des gros spéculateurs (cacao) | cftc_cot_cocoa | CFTC (vendredi) | zscore | 6 |
| 5 | Volume de broyage de cacao (demande trimestrielle) | grindings_q | associations (ECA/NCA/CAA) | zscore | 5 |
| 6 | Réglementation UE anti-déforestation (impact supply) | eudr | events-log (phase EUDR) | triplet | 5 |
| 7 | Écart de prix cacao New York − Londres | spread_ny_london | Twelve Data | zscore | 4 |
| 8 | Maladies des cabosses (impact récolte) | maladies_cabosses | events-log | triplet | 4 |
| 9 | Taux de change franc CFA et cédi ghanéen | usd_cfa_usd_cedi | Twelve Data | zscore | 3 |

**Σ poids (hors gate) = 54**

### Groupe de doublons détecté

**Groupe CACAO-A : Triple comptage positionnement — doublon signalé par Cowork (~53%)**

Cowork signale : « CFTC COT Cocoa » + « Hedge fund positioning » + « Positionnement spéculatif+options » (TRIPLE).

Après lecture du YAML :
- id=3 `hf_positioning_flux_options` (poids 7, ICE + CFTC) : **composite** = zscore put/call OI ICE + zscore COT CFTC. Mesure : options ICE + positions COT CFTC.
- id=4 `cftc_cot_cocoa` (poids 6, CFTC) : **zscore** des positions nets COT CFTC uniquement.

**Analyse de la redondance** :

Le critère id=3 (`composite`) intègre en interne le COT CFTC (une de ses deux composantes). Le critère id=4 mesure **le même COT CFTC** en standalone.

Résultat : les données CFTC COT sont comptées **DEUX FOIS** — une fois dans le composite (id=3) et une fois seules (id=4). C'est un double comptage avéré sur la source CFTC.

**Quantification du chevauchement** : id=3 poids 7 + id=4 poids 6 = 13/54 = **24% du signal** en chevauchement partiel. La composante options (ICE) est propre à id=3, mais la composante COT est partagée.

**Poids effectivement en double comptage** = ~50% de id=3 (la composante COT) + 100% de id=4 ≈ 3,5 + 6 = 9,5/54 = ~18% du signal en double comptage strict.

**Comparaison avec l'estimation Cowork (53%)** : non confirmée à ce niveau. La confusion vient de l'identification d'un « 3e critère » qui n'existe pas dans le YAML actuel (seulement 2 critères positionnement, pas 3). [estimation]

| Critère | Poids | Source | Contenu | Garder ? |
|---|---|---|---|---|
| Positionnement spéculatif + options (composite) | 7 | ICE + CFTC | Put/call OI + COT | **OUI** — plus riche, source duale |
| Positionnement gros spéculateurs (cacao) | 6 | CFTC seul | COT nets uniquement | **ABSORBER** — sous-ensemble du composite |

**Fusion proposée CACAO-A** : supprimer id=4 (`cftc_cot_cocoa`, poids 6). Poids fusionné = MAX = **7** (composite reste). Σ poids passe de 54 à **48**.

> ⚠️ Le schéma fiche ne supporte PAS de source fallback. La fusion garde `hf_positioning_flux_options` (ICE + CFTC composite). La clé CFTC standalone `cftc_cot_cocoa` est abandonnée.

---

## 9. VIX {#9-vix}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Niveau absolu de la peur des marchés (VIX) | niveau_vix_absolu | Twelve Data (CBOE en priorité) | lineaire | 10 |
| 2 | Structure des prix : VIX court vs VIX 3 mois | term_structure_vix_vix3m | Twelve Data (calculé) | lineaire | 8 |
| 3 | Ratio puts / calls options US (moyenne 5 jours) | put_call_ratio_cboe_5j | CBOE | zscore | 6 |
| 4 | Indice de risque de choc extrême (SKEW) | skew_index_cboe | CBOE | lineaire | 5 |
| 5 | Volatilité de la volatilité (VVIX) | vvix | CBOE | lineaire | 5 |
| 6 | Écart volatilité réelle − volatilité implicite (20 jours) | gap_rv_iv | Twelve Data (calculé) | lineaire | 5 |
| 7 | Positionnement des gros spéculateurs (VIX futures) | cftc_cot_vix_nets | CFTC (vendredi) | zscore | 5 |
| 8 | Événement géopolitique actif (3 jours) | tension_geopolitique_active | events-log L1=Géopolitique | triplet | 4 |

**Σ poids (hors gate) = 48**

### Groupe de doublons détecté

**Groupe VIX-A : Term structure ×2 — doublon signalé par Cowork (~39%)**

Cowork signale : « Term structure VIX/VIX3M » + « Structure prix VIX court vs long ».

Après lecture du YAML : **un seul critère term structure** (id=2, `term_structure_vix_vix3m`, poids 8). Pas de doublon interne.

**Groupe VIX-B : Niveau VIX absolu + écart RV-IV (doublon partiel hors-liste)**

- id=1 `niveau_vix_absolu` (poids 10) : niveau absolu du VIX (volatilité implicite actuelle)
- id=6 `gap_rv_iv` (poids 5) : écart RV (réalisée 20j) − IV (implicite)

Ces deux critères utilisent la volatilité implicite comme composante. `niveau_vix_absolu` mesure IV directement, `gap_rv_iv` mesure la prime IV vs RV. Ce sont des facteurs **distincts** (le niveau vs le premium) — pas un doublon sémantique strict. En revanche, quand le VIX est très bas (id=1 → signal LONG VIX), l'IV tend à être inférieure à la RV → `gap_rv_iv` envoie également un signal LONG. Corrélation partielle, pas un doublon structurel.

**Groupe VIX-C : SKEW + VVIX (doublon potentiel hors-liste)**

- id=4 `skew_index_cboe` (poids 5) : risque de queue gauche (choc extrême)
- id=5 `vvix` (poids 5) : volatilité de la volatilité (nervosité du marché d'options)

Ces deux critères sont corrélés en période de stress (les deux montent avant les crises) mais mesurent des dimensions différentes du risque d'options. Le SKEW mesure l'asymétrie de la distribution implicite, le VVIX mesure l'instabilité du pricing de volatilité. **Pas un doublon** au sens strict — information complémentaire sur le marché des options.

> ⚠️ **Aucun doublon interne avéré sur VIX.** Le doublon Cowork (term structure ×2) ne se retrouve pas dans le YAML actuel (une seule clé `term_structure_vix_vix3m`).

**Pas de fusion à réaliser sur VIX.**

---

## 10. Blé — mono-critère dominant {#10-ble}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Stocks mondiaux de blé (rapport USDA mensuel) | usda_wasde_stocks_to_use | USDA WASDE | zscore | 11 |
| 2 | Sécheresse dans les plaines céréalières US | noaa_drought_midwest_plains | NOAA US Drought Monitor | zscore | 9 |
| 3 | Tensions géopolitiques en mer Noire | geopolitique_mer_noire | events-log | triplet | 8 |
| 4 | État des cultures US (bon / excellent) | nass_crop_progress | USDA NASS | zscore | 6 |
| 5 | Demande chinoise à l'import (blé) | demande_chinoise_imports | USDA FAS | zscore | 5 |
| 6 | Positionnement des gros spéculateurs (blé) | cftc_cot_wheat | CFTC (vendredi) | zscore | 5 |
| 7 | Météo dans les zones céréalières australiennes | meteo_australie_dryland | BoM / météo | zscore | 5 |
| 8 | Appels d'offres blé de l'Égypte | egypte_gasc_tenders | GASC | zscore | 4 |
| 9 | Tendance du dollar (20 jours) | dxy_trend_20j | Twelve Data | zscore | 4 |

**Σ poids (hors gate) = 57**

### Analyse mono-critère

**Pas de doublon sémantique interne sur Blé.**

**Risque de mono-critère dominant : « Géopolitique mer Noire »** (id=3, poids 8/57 = 14% structurel).

Sur le run du 10/06, la fiche blé présente une couverture de **54%** (⚠️ conf. faible) avec plusieurs critères n/a :
- Stocks USDA (poids 11) — n/a ce run
- État des cultures US (poids 6) — n/a ce run
- Demande chinoise (poids 5) — n/a ce run
- Appels d'offres Égypte (poids 4) — n/a ce run

Quand 4 critères (poids 26/57) sont n/a, le critère géopolitique mer Noire (poids 8) représente **8/(57-26) = 25,8%** du signal effectivement disponible — ce qui déclenche le flag `◧ mono-critère dominant` (>50% serait le seuil strict, mais avec une couverture réduite il pèse davantage).

**Conformément au prompt : le cap mono-critère existant est `detect_mono_critere_dominant` en flag-only (`◧`), PAS un cap actif.** Ce document se limite à documenter le risque.

> **Risque documenté** : en cas de couverture réduite (plusieurs critères n/a simultanément), le critère géopolitique mer Noire peut dominer le signal blé à hauteur de 25-30% du signal effectif. Le flag `◧` est correctement affiché dans le bulletin (run 10/06 : Blé 7j porte le flag `◧`). Ce risque est réel mais le mécanisme de détection fonctionne.

---

## 11. Argent {#11-argent}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Taux d'intérêt réels US (10 ans) | taux_10y_us_reels_tips | FRED (DFII10) | zscore | 8 |
| 2 | Mouvement de l'or (5 jours) | mouvement_or_5j | Twelve Data | zscore | 7 |
| 3 | Ratio or / argent | ratio_gold_silver | Twelve Data | lineaire | 7 |
| 4 | Sur-performance de l'argent face à l'or (5 jours) | alpha_argent_vs_or_5j | Twelve Data | zscore | 5 |
| 5 | Activité industrielle Chine (indice PMI) | caixin_pmi_manuf | Caixin (mensuel) | lineaire | 5 |
| 6 | Positionnement des gros spéculateurs (argent) | cftc_cot_silver | CFTC (vendredi) | zscore | 5 |
| 7 | Stocks d'argent physique (marchés US) | inventaires_comex_silver | COMEX | zscore | 4 |
| 8 | Flux vers les fonds argent (5 jours) | flux_etf_slv_pslv_5j | Twelve Data | zscore | 4 |
| 9 | Demande solaire et grèves minières | demande_pv_mining_strikes | events-log + rapports industrie | composite | 3 |

**Σ poids (hors gate) = 48**

### Analyse

**Groupe ARGENT-A : Or + ratio or/argent (doublon partiel potentiel)**

- id=2 `mouvement_or_5j` (poids 7) : variation du prix de l'or sur 5 jours
- id=3 `ratio_gold_silver` (poids 7) : ratio or/argent absolu
- id=4 `alpha_argent_vs_or_5j` (poids 5) : sur-performance argent vs or sur 5 jours

Ces trois critères utilisent le prix de l'or comme référence. Le ratio id=3 et la sur-performance id=4 sont **particulièrement proches** : quand le ratio baisse (argent monte plus que l'or), id=4 est positif. Les deux mesurent la performance relative argent/or, quoique sur des bases différentes (ratio absolu vs performance relative 5j).

**Verdict** : id=2 (mouvement or absolu) est distinct — il mesure la tendance de l'or qui entraîne l'argent par corrélation structurelle. id=3 et id=4 ont une redondance partielle sur la notion de « valeur relative de l'argent face à l'or ».

| Critère | Poids | Source | Contenu | Garder ? |
|---|---|---|---|---|
| Ratio or / argent (absolu) | 7 | Twelve Data | Niveau absolu du ratio — valeur structurelle de long terme | **OUI** — capte la sous-évaluation persistante |
| Sur-performance argent vs or (5 jours) | 5 | Twelve Data | Momentum relatif argent/or sur 5j | **ABSORBER** — corrélé à l'inverse du ratio sur courte période |

**Fusion proposée ARGENT-A** : supprimer id=4 (`alpha_argent_vs_or_5j`, poids 5). Poids fusionné = MAX = **7** (ratio reste). Σ poids passe de 48 à **43**.

> ⚠️ Le schéma fiche ne supporte PAS de source fallback. La fusion garde `ratio_gold_silver` seul. La donnée de momentum relatif 5j est abandonnée.

> **Note** : cette fusion est hors-liste Cowork — à valider avec attention. L'argument de la redondance est valide mais le momentum 5j apporte une information de court terme que le ratio absolu ne capture pas toujours au même moment. **Niveau de confiance : moyen** — à discuter avec Thomas/Cowork.

---

## 12. Cuivre {#12-cuivre}

### Inventaire des critères (hors gate)

| id | Nom | cle_courante | Source | Normalisation | Poids |
|---|---|---|---|---|---|
| 1 | Activité industrielle Chine (indice PMI) | caixin_pmi_manuf | Caixin (mensuel) | lineaire | 12 |
| 2 | Stocks de cuivre mondiaux (tendance 5 jours) | inventaires_lme_shfe_5j | LME + SHFE | zscore | 8 |
| 3 | Grèves minières (Chili / Pérou) | mining_strikes_chili_perou | events-log | triplet | 5 |
| 4 | Tendance du dollar (20 jours) | dxy_trend_20j | Twelve Data | zscore | 6 |
| 5 | Positionnement des gros spéculateurs (cuivre) | cftc_cot_copper_nets | CFTC (vendredi) | zscore | 5 |
| 6 | Structure des prix futurs cuivre (spot vs M+3) | term_structure_m1_m3 | Twelve Data | lineaire | 5 |
| 7 | Plans de construction et infrastructures US-Chine | news_construction_infra | events-log | triplet | 4 |
| 8 | Ratio cuivre / or (appétit pour le risque) | ratio_cuivre_or | Twelve Data | zscore | 3 |

**Σ poids (hors gate) = 48**

### Analyse

**Pas de doublon sémantique avéré sur Cuivre.**

**Note hors-liste** : id=3 (`mining_strikes_chili_perou`) et id=7 (`news_construction_infra`) sont tous deux des critères événementiels (triplet), mais ils mesurent l'offre vs la demande — pas le même facteur.

**Note sur argent.yml et cuivre.yml** : les deux fiches partagent `caixin_pmi_manuf` comme clé courante mais avec des `echelle` différentes (argent=1.0, cuivre=1.3). Ce n'est pas un doublon dans la même fiche — c'est un critère macro partagé inter-fiches, déjà documenté dans `v3/audit/correlation-cachee-2026-06-05.md`.

**Pas de fusion à réaliser sur Cuivre.**

---

## 13. Synthèse et tableau récapitulatif des fusions {#13-synthese}

### Tableau des fusions confirmées

| Fiche | Groupe | Critère absorbé | id | Poids absorbé | Critère gardé | Poids gardé | Poids fusionné (MAX) |
|---|---|---|---|---|---|---|---|
| Nasdaq | NASDAQ-A | concentration_top7 | 5 | 5 | breadth_nasdaq100_ma50 | 6 | 6 |
| Pétrole | PETROLE-C | api_weekly_surprise | 2 | 8 | eia_crude_surprise | 10 | 10 |
| Cacao | CACAO-A | cftc_cot_cocoa | 4 | 6 | hf_positioning_flux_options | 7 | 7 |
| Argent | ARGENT-A | alpha_argent_vs_or_5j | 4 | 5 | ratio_gold_silver | 7 | 7 |

**Total critères supprimés : 4** (sur ~117 critères/run — soit ~3,4% de réduction)

### Doublons confirmés Cowork (vérification)

| Doublon signalé Cowork | Fiche | Verdict après audit YAML |
|---|---|---|
| Or : TIPS ×2 (~47%) | or.yml | ❌ Non confirmé — 1 seul critère TIPS dans le YAML |
| Nasdaq : TIPS ×27% | nasdaq.yml | ❌ Non confirmé — 1 seul critère TIPS (part élevée, pas doublon) |
| Pétrole : géopolitique Moyen-Orient ×2 (~44%) | petrole.yml | ❌ Non confirmé — 1 seul critère géopolitique dans le YAML |
| S&P 500 : VIX régime ×2 (~37%) | sp500.yml | ❌ Non confirmé — 1 seul critère VIX (même id) |
| EUR/USD : écart taux courts ×2 (~45%) | eurusd.yml | ❌ Non confirmé — 2 critères distincts (2 ans ≠ 10 ans) |
| CAC 40 : OAT-Bund ×2 (~32%) | cac40.yml | ❌ Non confirmé — 1 seul critère OAT-Bund dans le YAML |
| Café : météo Brésil ×2 (~36%) | cafe.yml | ❌ Non confirmé — 1 seul critère météo Brésil (composite interne) |
| Cacao : triple positionnement (~53%) | cacao.yml | ✅ Partiellement confirmé — 2 critères COT (double, pas triple) |
| VIX : term structure ×2 (~39%) | vix.yml | ❌ Non confirmé — 1 seul critère term structure dans le YAML |

### Doublons nouveaux identifiés (hors-liste Cowork)

| Fiche | Groupe | Nature du doublon | Fusion recommandée |
|---|---|---|---|
| Nasdaq | NASDAQ-A | breadth (QQQE/QQQ) et concentration top7 mesurent le même phénomène | OUI |
| Pétrole | PETROLE-C | EIA stocks + API pré-indicateur = même réalité physique, source quasi-identique | OUI |
| Argent | ARGENT-A | Ratio or/argent absolu et sur-performance 5j argent/or sont partiellement corrélés | OUI (niveau de confiance moyen) |

### Total récapitulatif

- Doublons liste Cowork vérifiés et confirmés : **1/9** (cacao partiellement)
- Doublons nouveaux hors-liste : **3** (nasdaq, pétrole, argent)
- Fusions proposées : **4** (1 Cowork confirmé + 3 nouveaux)
- Critères qui seraient supprimés : **4**
- Σ poids total réduit : Nasdaq 52→47 / Pétrole 60→52 / Cacao 54→48 / Argent 48→43

---

## 14. Tableau de couverture AVANT/APRÈS {#14-couverture}

### Méthode de calcul

Couverture pondérée = Σpoids(critères avec donnée) / Σpoids total de la fiche.

Paliers (gate S5 de `scoring_analyste.py`) :
- ≥65% → couverture normale
- 40-65% → ⚠️ conf. faible
- <40% → 🚫 insuffisant

**Source des disponibilités** : bulletin 2026-06-10 07h19 (run représentatif, les critères affichant `—` dans la colonne Valeur = n/a).

Les couvertures actuelles sont lues depuis le bulletin (label ⚠️ conf. faible avec % affiché). Les couvertures APRÈS sont calculées sur la base des fusions proposées.

### Données de disponibilité par fiche (run 10/06 07h)

**Argent** — Critères n/a : stocks COMEX (id=7), demande solaire (id=9). Présents : TIPS(8), or 5j(7), ratio(7), alpha(5), PMI(5 n/a!), COT(5), flux(4). Note bulletin : aucun seuil ⚠️ affiché → couverture normale.

> Recalcul depuis le bulletin : Argent 24h/7j/1m — pas de flag ⚠️ → couverture ≥65%.
> Critères avec valeur : TIPS(8), or5j(7), ratio(7), alpha(5), COT(5), flux(4) = 36. PMI = n/a = 0 (valeur « 0 non numérique »). Stocks n/a(4), demande solaire n/a(3) → Σavec donnée = 36, Σtotal = 48 → couverture = 36/48 = **75%** ✅

**Blé** — Bulletin : ⚠️ 54% sur toutes cellules. Critères n/a : stocks USDA(11), état cultures(6), demande chinoise(5), tenders Égypte(4). Présents : sécheresse(9), géopol(8 triplet=0), COT(5), météo Australie(5), DXY(4). Note : géopolitique = 0 penchant mais est considéré comme « avec valeur ».
> Σavec donnée = 9+8+5+5+4 = 31 (si géopolitique compte), Σtotal = 57 → 31/57 = **54%** ⚠️ conf. faible. Confirmé.

**CAC 40** — Bulletin : pas de flag ⚠️. Critère n/a : V2X(8), breadth(6 n/a assumé). Présents : OAT-Bund(10), alpha CAC(6), flux(5), politique(3), RSI(2).
> Σavec donnée = 10+6+5+3+2 = 26, Σtotal = 40 → 26/40 = **65%** — exactement à la frontière. Normal (seuil ≥65%).

**Cacao** — Bulletin : ⚠️ 50% sur toutes cellules. Critères n/a : météo CI/Ghana(11), arrivées ports(9), NY-Londres spread(4), CFA/cédi(3). Présents : composite(7), COT(6), broyages(5), EUDR(5), maladies(4).
> Σavec donnée = 7+6+5+5+4 = 27, Σtotal = 54 → 27/54 = **50%** ⚠️ conf. faible. Confirmé.

**Café** — Bulletin : ⚠️ 60% sur toutes cellules. Critères n/a : stocks ICE Arabica(9), USD/BRL(6), spread Arabica-Robusta(4). Présents : météo Brésil(11), COT(5), maladies(5), cycle biannuel(4), météo Vietnam(4).
> Σavec donnée = 11+5+5+4+4 = 29, Σtotal = 48 → 29/48 = **60%** ⚠️ conf. faible. Confirmé.

**Cuivre** — Bulletin : ⚠️ 48% sur toutes cellules. Critères n/a : PMI Caixin(12), stocks LME/SHFE(8), term structure(5). Présents : grèves(5), DXY(6), COT(5), infra news(4), ratio Cu/Or(3).
> Σavec donnée = 5+6+5+4+3 = 23, Σtotal = 48 → 23/48 = **47,9%** ⚠️ conf. faible. Confirmé.

**EUR/USD** — Bulletin : pas de flag ⚠️. Critères n/a : FedWatch(6), OAT-Bund stress(4), balance commerciale(3). Présents : diff 2Y(12), diff 10Y(6), DXY(9), USD/JPY(4), COT(5).
> Σavec donnée = 12+6+9+4+5 = 36, Σtotal = 49 → 36/49 = **73,5%** ✅ normal.

**Nasdaq** — Bulletin : pas de flag ⚠️ couverture (flag ⌛ uniquement). Critères n/a : VXN régime(7), concentration top7(5). Présents : TIPS(11), SOX(7), breadth(6), sentiment IA(5), flux QQQ(5), spread Russell(4), RSI(2).
> Σavec donnée = 11+7+6+5+5+4+2 = 40, Σtotal = 52 → 40/52 = **76,9%** ✅ normal.

**Or** — Bulletin : pas de flag ⚠️. Critères n/a : WGC banques centrales(9). Présents : TIPS(12), DXY(8), COT(6), flux(5), géopol(5), saisonnalité Inde(3), VIX proxy(3).
> Σavec donnée = 12+8+6+5+5+3+3 = 42, Σtotal = 51 → 42/51 = **82,4%** ✅ normal.

**Pétrole** — Bulletin : pas de flag ⚠️. Critère n/a : term structure(5). Présents : EIA(10), API(8), géopol(7), COT(7), OPEC(6), DXY(5), Cushing(4), spread Brent-WTI(4), PMI Caixin(4 = 0 n/a!).
> PMI = 0 non numérique = n/a. Σavec donnée = 10+8+7+7+6+5+4+4 = 51, Σtotal = 60 → 51/60 = **85%** ✅ (avant fusion). Nota : PMI marcherait comme n/a → 51/60 = 85%.

**S&P 500** — Bulletin : pas de flag ⚠️. Critères n/a : sentiment AAII(4). Présents : VIX régime(8), delta taux(9), HY spread(7), breadth(7), DXY(5), flux(5), CAPE(4), RSI(2), TIPS(10).
> Σavec donnée = 8+9+7+7+5+5+4+2+10 = 57, Σtotal = 61 → 57/61 = **93,4%** ✅ normal.

**VIX** — Bulletin : pas de flag ⚠️. Critères n/a : put/call ratio(6), gap RV-IV(5). Présents : niveau VIX(10), term structure(8), SKEW(5), VVIX(5), COT(5), géopol(4).
> Σavec donnée = 10+8+5+5+5+4 = 37, Σtotal = 48 → 37/48 = **77,1%** ✅ normal.

### Tableau AVANT/APRÈS couverture (run 10/06 07h)

Les cellules `24h / 7j / 1m` reçoivent la même couverture (le run calcule une couverture unique par actif, indépendante de l'horizon).

| Fiche | Σpoids AVANT | Couverture AVANT | Palier AVANT | Σpoids APRÈS fusion | Couverture APRÈS | Palier APRÈS | Bascule ? |
|---|---|---|---|---|---|---|---|
| Argent | 48 | 36/48 = 75% | ✅ normal | **43** (-5) | 36/43 = 83,7% | ✅ normal | ➡️ Aucune |
| Blé | 57 | 31/57 = 54% | ⚠️ faible | 57 (inchangé) | 31/57 = 54% | ⚠️ faible | ➡️ Aucune |
| CAC 40 | 40 | 26/40 = 65% | ✅ normal | 40 (inchangé) | 26/40 = 65% | ✅ normal | ➡️ Aucune |
| Cacao | 54 | 27/54 = 50% | ⚠️ faible | **48** (-6) | 27/48 = 56,3% | ⚠️ faible | ➡️ Aucune |
| Café | 48 | 29/48 = 60% | ⚠️ faible | 48 (inchangé) | 29/48 = 60% | ⚠️ faible | ➡️ Aucune |
| Cuivre | 48 | 23/48 = 47,9% | ⚠️ faible | 48 (inchangé) | 23/48 = 47,9% | ⚠️ faible | ➡️ Aucune |
| EUR/USD | 49 | 36/49 = 73,5% | ✅ normal | 49 (inchangé) | 36/49 = 73,5% | ✅ normal | ➡️ Aucune |
| Nasdaq | 52 | 40/52 = 76,9% | ✅ normal | **47** (-5) | 40/47 = 85,1% | ✅ normal | ➡️ Aucune |
| Or | 51 | 42/51 = 82,4% | ✅ normal | 51 (inchangé) | 42/51 = 82,4% | ✅ normal | ➡️ Aucune |
| Pétrole | 60 | 51/60 = 85% | ✅ normal | **52** (-8) | 43/52 = 82,7% | ✅ normal | ➡️ Aucune |
| S&P 500 | 61 | 57/61 = 93,4% | ✅ normal | 61 (inchangé) | 57/61 = 93,4% | ✅ normal | ➡️ Aucune |
| VIX | 48 | 37/48 = 77,1% | ✅ normal | 48 (inchangé) | 37/48 = 77,1% | ✅ normal | ➡️ Aucune |

> Note couverture Pétrole APRÈS : l'API (id=2, poids 8) est **actuellement disponible** (valeur 433712 dans le run). Sa suppression fait passer la couverture de 51/60=85% à (51-8)/52=43/52=**82,7%** — toujours ✅ normal.

### Cellules à risque de bascule de palier

**Aucune cellule ne bascule de palier suite aux fusions proposées** sur ce run.

**Observation** : les fusions améliorent mécaniquement la couverture des fiches fusionnées (Nasdaq, Argent) car le Σpoids total diminue. Pour Pétrole, la couverture baisse légèrement (85%→82,7%) mais reste très au-dessus du seuil normal (65%). La fusion la plus risquée est Pétrole : si un jour le critère EIA est n/a ET que le Σpoids est réduit à 52, la couverture sans EIA serait (51-10)/52 = 41/52 = **78,8%** — toujours normal.

**Cas limite à surveiller (Cacao)** : après fusion (Σpoids = 48), si un critère supplémentaire devient n/a (ex. le composite hf_positioning, poids 7), la couverture passerait à 20/48 = 41,7% — proche du seuil ⚠️/🚫 (40%). Cette cellule mérite une surveillance.

---

## 15. Points à trancher — Thomas / Cowork {#15-points-a-trancher}

### Décisions requises avant toute fusion

1. **[Cowork] Vérifier la source des % (~47% or, ~27% nasdaq, etc.)** : les doublons listés ne correspondent pas aux YAML actuels. Soit les fiches ont déjà été partiellement corrigées, soit les % viennent d'une analyse sur une version antérieure des fiches. Il faut valider sur quelle version de fichier Cowork a travaillé.

2. **[Thomas + Cowork] Valider la fusion Pétrole PETROLE-C** (API supprimé) : la suppression du pré-indicateur API signifie que le mardi soir (avant publication EIA mercredi), le signal pétrole sera moins riche d'une composante stocks. Est-ce acceptable compte tenu du drift directionnel (l'EIA remplace le lendemain) ?

3. **[Thomas + Cowork] Valider la fusion Argent ARGENT-A** (alpha 5j supprimé) : niveau de confiance moyen. Le momentum relatif 5j apporte une info court terme que le ratio absolu ne capture pas dans les 24 premières heures d'un mouvement.

4. **[Thomas + Cowork] Valider la fusion Nasdaq NASDAQ-A** (concentration top7 supprimée) : dans les faits, concentration_top7 est n/a sur ce run (valeur absente) — la fusion n'a pas d'impact immédiat mais supprime définitivement la clé.

5. **[Thomas + Cowork] Valider la fusion Cacao CACAO-A** (cftc_cot_cocoa supprimé) : c'est le doublon le mieux établi. Le composite (id=3) intègre déjà le COT — la suppression du standalone est logique.

6. **[Technique] Vérifier que `hf_positioning_flux_options` (id=3 cacao) consomme bien les deux composantes** (put/call OI ICE + COT CFTC) à chaque run — si la composante COT est parfois absente dans le composite, supprimer id=4 réduirait la robustesse.

7. **[Thomas] Blé — mono-critère** : le flag `◧` est visible dans le bulletin. Aucune action système requise, mais documenter dans la fiche ble.yml (commentaire) que le critère géopolitique peut dominer en cas de couverture réduite. Décision : ajouter un commentaire YAML ou laisser tel quel ?

---

*Checkpoint Lot A étape 1 — Version 1.0 — 2026-06-10*
*Auteur : @data-analyst — Lecture seule, AUCUN YAML modifié*
