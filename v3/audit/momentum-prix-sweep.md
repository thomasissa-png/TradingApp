# Momentum-prix sweep — Balayage des 12 fiches v3
**Auteur** : @data-analyst
**Date** : 2026-06-10
**Statut** : Analyse pure — AUCUN code/YAML modifié

---

## 0. Méthode et périmètre

**Objet** : recenser, pour chaque fiche, les critères qui capturent la **tendance directionnelle du prix propre de l'actif** — ce que la thèse trend-following exige comme signal primaire.

**Ce qui compte** : un critère de tendance-PRIX doit mesurer le momentum ou la direction du **prix du sous-jacent lui-même** (ex. variation glissante, z-score des closes, RSI sur l'actif). Il doit avoir `signe: +1` (hausse = LONG) ou être un contrarian explicite sur l'extrême de prix (ex. RSI oversold = LONG).

**Ce qui ne compte pas** :
- `dxy_trend_20j` : tendance du dollar — critère MACRO partagé par 5 fiches, pas un critère de tendance-prix propre
- `sox_trend_5j` : tendance des semi-conducteurs — proxy sectoriel pour le Nasdaq, mais c'est le prix d'un **autre** actif (SOXX/SOXX ETF)
- `alpha_cac_vs_sp_5j` : performance RELATIVE du CAC vs S&P — c'est un alpha relatif, pas la tendance prix absolue du CAC lui-même
- `mouvement_or_5j` : variation de l'or sur 5j — utilisé dans la fiche ARGENT comme proxy, donc c'est le prix d'un **autre** actif
- critères COT/positionnement (signe -1, contrarian) : capturent le **positionnement des acteurs**, pas la tendance de prix
- spreads, structures de terme, régimes de vol : signaux dérivés, pas momentum directionnel du prix propre

**Cas limites documentés** :
- `sox_trend_5j` (Nasdaq) : semi-conducteurs ~80% corrélés au Nasdaq → classé PROXY PROCHE mais pas tendance-prix propre (c'est le prix du secteur, pas de l'indice)
- `ratio_gold_silver` (Argent) : mesure le prix relatif argent/or, pas la tendance absolue du prix de l'argent
- `spread_ny_london` (Cacao) : spread entre deux contrats du même sous-jacent sur deux marchés différents — capte une tension de marché mais pas la tendance directionnelle du prix cacao lui-même
- `rsi_14j_*` (S&P, Nasdaq, CAC) : RSI calculé sur le prix propre de l'actif, signe -1 contrarian (oversold = LONG) → **compté comme tendance-prix** car il mesure directement le niveau de prix propre même si logique contrarian (oversold signale une tendance baissière extrême)
- `breadth_*` (S&P, Nasdaq) : ratio equal-weight / cap-weight — mesure la participation interne, pas le momentum prix de l'indice lui-même → non compté

---

## 1. Recensement par fiche

### 1.1 Or (`or.yml`)

Critères présents (hors gate) :

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `taux_10y_us_reels_tips` | Taux réels US 10 ans | 12 | -1 | MACRO (TIPS) |
| 2 | `achats_pboc_cb_emergentes` | Achats banques centrales | 9 | +1 | FONDAMENTAL |
| 3 | `dxy_trend_20j` | Tendance dollar 20j | 8 | -1 | MACRO (autre actif) |
| 4 | `cftc_cot_nets` | Positionnement spéculateurs | 6 | -1 | COT contrarian |
| 5 | `flux_etf_or_5j` | Flux ETF or 5j | 5 | +1 | FLUX (proxy demande) |
| 6 | `tension_geopolitique` | Tension géopolitique | 5 | +1 | NEWS/EVENT |
| 7 | `demande_indienne_saisonniere` | Demande Inde | 3 | +1 | SAISONNIER |
| 8 | `vix_risk_off_proxy` | VIX | 3 | +1 | MACRO (autre actif) |

**Critères de tendance-prix propre** : **AUCUN**

`flux_etf_or_5j` est ambiguë : c'est la variation de prix de l'ETF or sur 5j, z-scorée, avec signe +1. Techniquement, si l'ETF suit GC=F, c'est proche d'un momentum-prix or 5j. Cependant dans le calculateur (`TWELVE_SYMBOLS`), `flux_etf_or_5j` est traité via la branche `mouvement_or_5j or cle.startswith("flux_etf_")` → perf 5j sur le ticker ETF. **Classé AMBIGÜ → PROXY mais non compté** : le critère est nommé "flux vers les fonds" (implication d'un signal de demande), le signe et la source sont identiques à un momentum-prix, mais l'intention déclarée est les flux, pas la tendance directionnelle. En cas de doute, la rigueur s'applique → ABSENT.

**Verdict Or : ABSENT**

---

### 1.2 Argent (`argent.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `taux_10y_us_reels_tips` | Taux réels US 10 ans | 8 | -1 | MACRO (TIPS) |
| 2 | `mouvement_or_5j` | Mouvement de l'or 5j | 7 | +1 | PRIX AUTRE ACTIF (or) |
| 3 | `ratio_gold_silver` | Ratio or/argent | 7 | -1 | RATIO RELATIF |
| 5 | `caixin_pmi_manuf` | PMI Caixin | 5 | +1 | MACRO (demande) |
| 6 | `cftc_cot_silver` | Positionnement spéculateurs | 5 | -1 | COT contrarian |
| 7 | `inventaires_comex_silver` | Stocks COMEX | 4 | -1 | OFFRE |
| 8 | `flux_etf_slv_pslv_5j` | Flux ETF argent 5j | 4 | +1 | FLUX (voir Or) |
| 9 | `demande_pv_mining_strikes` | Demande PV + grèves | 3 | +1 | NEWS/EVENT |

**Critères de tendance-prix propre** : **AUCUN**

Note : `mouvement_or_5j` (poids 7) capte le momentum du prix de l'**or**, utilisé comme proxy de l'argent. C'est un critère de tendance-prix d'un autre actif, pas du prix propre de l'argent. `ratio_gold_silver` mesure la valeur relative argent/or — signal de valeur relative, pas de tendance directionnelle.

**Verdict Argent : ABSENT**

---

### 1.3 Cuivre (`cuivre.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `caixin_pmi_manuf` | PMI Caixin Chine | 12 | +1 | MACRO (demande) |
| 2 | `inventaires_lme_shfe_5j` | Stocks LME+SHFE 5j | 8 | -1 | OFFRE |
| 3 | `mining_strikes_chili_perou` | Grèves minières | 5 | +1 | NEWS/EVENT |
| 4 | `dxy_trend_20j` | Tendance dollar 20j | 6 | -1 | MACRO (autre actif) |
| 5 | `cftc_cot_copper_nets` | Positionnement spéculateurs | 5 | -1 | COT contrarian |
| 6 | `term_structure_m1_m3` | Structure terme M1-M3 | 5 | +1 | STRUCTURE TERME |
| 7 | `news_construction_infra` | Plans infra US-Chine | 4 | +1 | NEWS/EVENT |
| 8 | `ratio_cuivre_or` | Ratio cuivre/or | 3 | +1 | RATIO RELATIF |

**Critères de tendance-prix propre** : **AUCUN**

Note : `ratio_cuivre_or` (poids 3) mesure le rapport cuivre/or comme baromètre de l'appétit pour le risque — signal de marché général, pas la tendance directionnelle du prix du cuivre propre. `inventaires_lme_shfe_5j` : variation de stock sur 5j (signe -1 = stock baisse = LONG) — c'est un signal d'offre, pas de prix.

**Verdict Cuivre : ABSENT**

---

### 1.4 Pétrole (`petrole.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `eia_crude_surprise` | Surprise stocks EIA | 10 | +1 | OFFRE (stocks) |
| 3 | `tension_geopol_moyen_orient` | Tension géopolitique MO | 7 | +1 | NEWS/EVENT |
| 4 | `cftc_cot_crude_nets` | Positionnement spéculateurs | 7 | -1 | COT contrarian |
| 5 | `opec_production_policy` | Décision OPEC+ | 6 | +1 | NEWS/EVENT |
| 6 | `brent_term_structure_m1m2` | Structure terme Brent | 5 | +1 | STRUCTURE TERME |
| 7 | `dxy_trend_20j` | Tendance dollar 20j | 5 | -1 | MACRO (autre actif) |
| 8 | `cushing_stocks` | Stocks Cushing | 4 | -1 | OFFRE (stocks) |
| 9 | `spread_brent_wti` | Spread Brent-WTI | 4 | +1 | SPREAD MARCHÉ |
| 10 | `caixin_pmi_manuf` | PMI Caixin | 4 | +1 | MACRO (demande) |

**Critères de tendance-prix propre** : **AUCUN**

Note : `eia_crude_surprise` est une surprise de stocks — c'est un signal d'offre/demande qui influence le prix mais ne mesure pas la tendance de prix elle-même. `brent_term_structure_m1m2` est actuellement n/a (pas de M2 distinct via Twelve gratuit — voir calculateur).

**Verdict Pétrole : ABSENT**

---

### 1.5 Blé (`ble.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `usda_wasde_stocks_to_use` | Stocks USDA WASDE | 11 | -1 | FONDAMENTAL |
| 2 | `noaa_drought_midwest_plains` | Sécheresse NOAA | 9 | +1 | MÉTÉO |
| 3 | `geopolitique_mer_noire` | Tension mer Noire | 8 | +1 | NEWS/EVENT |
| 4 | `nass_crop_progress` | État cultures USDA | 6 | -1 | FONDAMENTAL |
| 5 | `demande_chinoise_imports` | Demande Chine import | 5 | +1 | FONDAMENTAL |
| 6 | `cftc_cot_wheat` | Positionnement spéculateurs | 5 | -1 | COT contrarian |
| 7 | `meteo_australie_dryland` | Météo Australie | 5 | -1 | MÉTÉO |
| 8 | `egypte_gasc_tenders` | Tenders Égypte GASC | 4 | +1 | DEMANDE |
| 9 | `dxy_trend_20j` | Tendance dollar 20j | 4 | -1 | MACRO (autre actif) |

**Critères de tendance-prix propre** : **AUCUN**

**Verdict Blé : ABSENT**

---

### 1.6 Cacao (`cacao.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `meteo_ci_ghana_precip_30j` | Météo CI+Ghana 30j | 11 | +1 | MÉTÉO |
| 2 | `arrivees_port_abidjan_sanpedro_20j` | Arrivées ports ivoire 20j | 9 | -1 | OFFRE |
| 3 | `hf_positioning_flux_options` | Positionnement+options COT | 7 | -1 | COT contrarian |
| 5 | `grindings_q` | Broyages trimestriels | 5 | +1 | DEMANDE |
| 6 | `eudr` | Réglementation EUDR | 5 | +1 | NEWS/EVENT |
| 7 | `spread_ny_london` | Spread NY-Londres | 4 | +1 | SPREAD MARCHÉ |
| 8 | `maladies_cabosses` | Maladies des cabosses | 4 | +1 | NEWS/EVENT |
| 9 | `usd_cfa_usd_cedi` | Taux CFA+Cédi | 3 | -1 | MACRO (autre actif) |

**Critères de tendance-prix propre** : **AUCUN**

Note : `spread_ny_london` pourrait partiellement capter une tension de marché sur le cacao, mais c'est un écart entre deux marchés du même actif (tension géographique/arbitrage), pas la tendance directionnelle du prix cacao lui-même.

**Verdict Cacao : ABSENT** — cas documenté dans le case-study, confirmé ici.

---

### 1.7 Café (`cafe.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `meteo_bresil_minas_gerais` | Météo Brésil (gel/sécheresse) | 11 | +1 | MÉTÉO |
| 2 | `stocks_ice_arabica_certifies_20j` | Stocks ICE Arabica 20j | 9 | -1 | OFFRE |
| 3 | `usd_brl` | Taux USD/BRL | 6 | -1 | MACRO (autre actif) |
| 4 | `cftc_cot_coffee` | Positionnement spéculateurs | 5 | -1 | COT contrarian |
| 5 | `maladies_cabosses_rouille` | Maladies rouille | 5 | +1 | NEWS/EVENT |
| 6 | `cycle_bresil_biannuel` | Cycle biannuel Brésil | 4 | +1 | SAISONNIER |
| 7 | `spread_arabica_robusta` | Spread Arabica-Robusta | 4 | +1 | SPREAD MARCHÉ |
| 8 | `meteo_vietnam_robusta` | Météo Vietnam | 4 | -1 | MÉTÉO |

**Critères de tendance-prix propre** : **AUCUN**

Note : `spread_arabica_robusta` mesure le différentiel de prix entre deux types de café — signal de qualité/substitution relatif, pas la tendance directionnelle du prix de l'Arabica propre. `stocks_ice_arabica_certifies_20j` avec signe -1 sur la variation de stocks sur 20j — c'est un signal d'offre, pas le prix lui-même.

**Verdict Café : ABSENT**

---

### 1.8 S&P 500 (`sp500.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 10 | `taux_10y_us_reels_tips` | Taux réels US 10 ans | 10 | -1 | MACRO (TIPS) |
| 2 | `taux_10y_us_delta_5j` | Variation taux 10Y 5j | 9 | -1 | MACRO (taux) |
| 1 | `vix_regime` | Régime VIX | 8 | +1 | MACRO (autre actif, non-monotone) |
| 3 | `hy_credit_spread` | Spread crédit HY | 7 | -1 | MACRO (marché crédit) |
| 4 | `breadth_sp_ma50` | Breadth S&P (RSP/SPY) | 7 | +1 | PARTICIPATION (pas prix propre) |
| 5 | `dxy_trend_20j` | Tendance dollar 20j | 5 | -1 | MACRO (autre actif) |
| 6 | `flux_etf_spy_ivv_5j` | Flux ETF S&P 5j | 5 | +1 | FLUX (voir Or) |
| 7 | `aaii_bull_bear` | Sentiment AAII | 4 | -1 | SENTIMENT contrarian |
| 8 | `shiller_cape_fwd_pe` | CAPE/FwdPE | 4 | -1 | VALORISATION contrarian |
| 9 | `rsi_14j_gspc` | RSI 14j S&P | 2 | -1 | **TENDANCE-PRIX PROPRE** |

**Critères de tendance-prix propre** :
- `rsi_14j_gspc` — RSI 14 jours calculé sur ^GSPC (S&P 500 directement), **poids 2**, signe -1 (RSI=30 oversold = LONG). Capte la tendance de prix propre en mode contrarian : un RSI bas signale une tendance baissière extrême (rebond potentiel).

**Poids cumulé tendance-prix propre** : **2 / 61 total = 3,3 %**

**Verdict S&P 500 : FAIBLE** — le seul critère de tendance-prix propre pèse 2/61 du poids total. Le RSI est en logique contrarian et pertinence faible sur 24h (0.8) mais quasi nulle sur 1m (0.2).

---

### 1.9 Nasdaq (`nasdaq.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `taux_10y_us_reels_tips` | Taux réels US 10 ans | 11 | -1 | MACRO (TIPS) |
| 2 | `vxn_regime` | Régime VXN | 7 | +1 | MACRO (autre actif) |
| 3 | `sox_trend_5j` | Tendance semi-conducteurs 5j | 7 | +1 | PRIX AUTRE ACTIF (SOXX) |
| 4 | `breadth_nasdaq100_ma50` | Breadth Nasdaq (QQQE/QQQ) | 6 | +1 | PARTICIPATION |
| 6 | `sentiment_ia_megacaps` | Sentiment IA/méga-caps | 5 | +1 | NEWS/EVENT |
| 7 | `flux_etf_qqq_5j` | Flux ETF QQQ 5j | 5 | +1 | FLUX (voir Or) |
| 8 | `spread_nasdaq_russell2000` | Spread Nasdaq-Russell2000 | 4 | -1 | SPREAD RELATIF |
| 9 | `rsi_14j_ixic` | RSI 14j Nasdaq | 2 | -1 | **TENDANCE-PRIX PROPRE** |

**Critères de tendance-prix propre** :
- `rsi_14j_ixic` — RSI 14 jours calculé sur ^IXIC (Nasdaq Composite directement), **poids 2**, signe -1 (contrarian oversold). Même logique que S&P.

Note sur `sox_trend_5j` : les semi-conducteurs (SOXX) sont très corrélés au Nasdaq (~0.85), mais c'est le prix d'un autre actif (secteur), pas du Nasdaq directement. Le calculateur confirme : `"sox_trend_5j": "SOXX"` → c'est le ticker de l'ETF iShares Semiconductors, pas ^IXIC ou ^NDX. Classé PRIX AUTRE ACTIF.

**Poids cumulé tendance-prix propre** : **2 / 47 total = 4,3 %**

**Verdict Nasdaq : FAIBLE** — même situation que le S&P. `sox_trend_5j` est un proxy sectoriel fort mais techniquement pas la tendance-prix du Nasdaq lui-même.

---

### 1.10 CAC 40 (`cac40.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 2 | `spread_oat_bund_10y` | Spread OAT-Bund 10Y | 10 | -1 | MACRO (taux souverains) |
| 1 | `v2x_regime` | Régime V2X | 8 | +1 | MACRO (autre actif) |
| 3 | `alpha_cac_vs_sp_5j` | Sur-performance CAC vs S&P | 6 | +1 | ALPHA RELATIF |
| 4 | `breadth_cac_ma50` | Breadth CAC (n/a assumé) | 6 | +1 | PARTICIPATION (n/a) |
| 5 | `flux_etf_msci_france_5j` | Flux ETF France 5j | 5 | +1 | FLUX |
| 6 | `tension_politique_fr` | Stabilité politique FR | 3 | +1 | NEWS/EVENT |
| 7 | `rsi_14j_fchi` | RSI 14j CAC 40 | 2 | -1 | **TENDANCE-PRIX PROPRE** |

**Critères de tendance-prix propre** :
- `rsi_14j_fchi` — RSI 14 jours calculé sur ^FCHI (CAC 40 directement), **poids 2**, signe -1 (oversold = LONG).

Note sur `alpha_cac_vs_sp_5j` : la sur-performance relative du CAC face au S&P sur 5j (`alpha_cac_vs_sp_5j`, calculé via `_twelve_alpha_5j(^FCHI, ^GSPC, crit)`) intègre le prix propre du CAC, mais c'est une mesure RELATIVE (performance résiduelle après soustraction du S&P), pas la tendance absolue du CAC. Classé ALPHA RELATIF, non compté.

**Poids cumulé tendance-prix propre** : **2 / 40 total = 5 %** (hors breadth n/a)

**Verdict CAC 40 : FAIBLE** — même structure que S&P/Nasdaq, RSI seul poids 2. `breadth_cac_ma50` est n/a (pas d'ETF CAC equal-weight gratuit, confirmé dans la fiche).

---

### 1.11 EUR/USD (`eurusd.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `differentiel_taux_2y_us_de` | Différentiel taux 2Y US-DE | 12 | -1 | MACRO (différentiel de taux) |
| 3 | `dxy_trend_20j` | Tendance dollar 20j | 9 | -1 | MACRO (autre actif/dollar) |
| 2 | `differentiel_taux_10y_us_bund` | Différentiel taux 10Y US-Bund | 6 | -1 | MACRO (différentiel de taux) |
| 5 | `fedwatch_proba` | Proba coupe Fed | 6 | +1 | MACRO (anticipations taux) |
| 6 | `cftc_cot_eur_nets` | Positionnement spéculateurs EUR | 5 | -1 | COT contrarian |
| 4 | `usd_jpy_proxy_risk` | USD/JPY (signal risque) | 4 | -1 | PRIX AUTRE ACTIF (JPY) |
| 7 | `spread_oat_bund_stress_ez` | Spread OAT-Bund (stress EZ) | 4 | -1 | MACRO (stress zone euro) |
| 8 | `balance_commerciale_ez` | Balance commerciale EZ | 3 | +1 | FONDAMENTAL |

**Critères de tendance-prix propre** : **AUCUN**

Cas particulier : pour l'EUR/USD, la "tendance prix propre" serait un z-score de la variation du taux de change EUR/USD lui-même sur N jours. Aucun critère ne calcule directement le momentum du taux de change EUR/USD. `dxy_trend_20j` (poids 9) est inversé et concerne le dollar index, pas l'EUR/USD directement. `usd_jpy_proxy_risk` concerne une autre paire de change.

**Verdict EUR/USD : ABSENT**

---

### 1.12 VIX (`vix.yml`)

| id | cle_courante | nom | poids | signe | Nature |
|---|---|---|---|---|---|
| 1 | `niveau_vix_absolu` | Niveau absolu VIX | 10 | -1 | **NIVEAU-PRIX PROPRE (contrarian)** |
| 2 | `term_structure_vix_vix3m` | Structure terme VIX/VIX3M | 8 | +1 | STRUCTURE TERME (propre) |
| 3 | `put_call_ratio_cboe_5j` | P/C ratio CBOE 5j | 6 | -1 | DÉRIVÉS (signaux options) |
| 4 | `skew_index_cboe` | SKEW index | 5 | +1 | DÉRIVÉS |
| 5 | `vvix` | VVIX | 5 | +1 | **VOL DE LA VOL (propre)** |
| 6 | `gap_rv_iv` | Écart RV-IV 20j | 5 | -1 | DÉRIVÉS (propre) |
| 7 | `cftc_cot_vix_nets` | Positionnement futures VIX | 5 | -1 | COT contrarian |
| 8 | `tension_geopolitique_active` | Tension géopolitique 3j | 4 | +1 | NEWS/EVENT |

**Critères de tendance-prix propre** :

Le VIX est un actif particulier : LONG = VIX monte. La fiche vise à prédire la direction du VIX, donc "tendance-prix propre" s'entend comme tendance directionnelle du VIX lui-même.

- `niveau_vix_absolu` (poids 10, signe -1) : niveau actuel du VIX, logique contrarian (VIX<13 = trop bas = rebond attendu = LONG VIX). Capte bien la tendance de niveau du VIX propre, en logique de retour à la moyenne. **Compté** — c'est la mesure directe du prix propre du VIX.
- `term_structure_vix_vix3m` (poids 8, signe +1) : ratio VIX spot vs VIX 3 mois — mesure la structure propre de la vol (backwardation/contango). C'est une dérivée du VIX propre. **Compté** — les deux composantes sont du VIX.
- `vvix` (poids 5) : volatilité de la volatilité — c'est la vol implicite des options sur VIX futures. Très lié au VIX mais c'est un indice dérivé (options sur le VIX), pas le VIX lui-même. **Non compté** (actif dérivé).
- `gap_rv_iv` (poids 5) : écart entre volatilité réalisée et volatilité implicite 20j du S&P. Lié mais différent du VIX. **Non compté**.

**Poids cumulé tendance-prix propre** : **18 / 48 total = 37,5 %**

**Verdict VIX : COUVERT** — le VIX est le seul actif avec une couverture solide de son propre niveau de prix. C'est logique : le VIX se prédit bien par son niveau absolu (mean-reversion) et sa structure de terme (propres au VIX).

---

## 2. Tableau de synthèse — COUVERT / FAIBLE / ABSENT

| Fiche | Critères tendance-prix propre | Clé(s) | Poids | % poids total | Verdict |
|---|---|---|---|---|---|
| **Or** | 0 | — | 0 | 0% | **ABSENT** |
| **Argent** | 0 | — | 0 | 0% | **ABSENT** |
| **Cuivre** | 0 | — | 0 | 0% | **ABSENT** |
| **Pétrole** | 0 | — | 0 | 0% | **ABSENT** |
| **Blé** | 0 | — | 0 | 0% | **ABSENT** |
| **Cacao** | 0 | — | 0 | 0% | **ABSENT** |
| **Café** | 0 | — | 0 | 0% | **ABSENT** |
| **S&P 500** | 1 | `rsi_14j_gspc` | 2 | 3,3% | **FAIBLE** |
| **Nasdaq** | 1 | `rsi_14j_ixic` | 2 | 4,3% | **FAIBLE** |
| **CAC 40** | 1 | `rsi_14j_fchi` | 2 | 5% | **FAIBLE** |
| **EUR/USD** | 0 | — | 0 | 0% | **ABSENT** |
| **VIX** | 2 | `niveau_vix_absolu` + `term_structure_vix_vix3m` | 18 | 37,5% | **COUVERT** |

**Légende** :
- **COUVERT** : ≥1 critère tendance-prix propre avec poids significatif (>10% du total)
- **FAIBLE** : critère(s) présents mais poids marginal (<10% du total)
- **ABSENT** : aucun critère de tendance-prix propre

---

## 3. Verdict famille

### Décompte

- **ABSENT** : 8 fiches sur 12 (Or, Argent, Cuivre, Pétrole, Blé, Cacao, Café, EUR/USD)
- **FAIBLE** : 3 fiches sur 12 (S&P 500, Nasdaq, CAC 40 — RSI poids 2 chacun)
- **COUVERT** : 1 fiche sur 12 (VIX uniquement)

### Défaut systémique : OUI

Le cacao n'est pas un cas isolé. **8 fiches sur 12 n'ont aucun critère de tendance-prix propre.** Les 3 indices ont un RSI marginal (poids 2, <5% du total). Le VIX est l'exception structurellement justifiée (actif de vol, prédit par son niveau absolu par nature).

**Pourquoi ce pattern est systémique et non accidentel :**

1. **Architecture de la fiche type** : la fiche canonique est construite sur des fondamentaux (offre/demande/macro) + positionnement COT + news. Ce template ne prévoit pas de case "momentum directionnel du prix propre". Le pattern `dxy_trend_20j` (tendance d'un autre actif, le dollar) est réutilisé 5 fois comme proxy macro — jamais un z-score du sous-jacent lui-même.

2. **Origine des fiches** : les fiches viennent d'une analyse fondamentale (vault Drive Bourse.md). L'approche est : "quels facteurs structurels font bouger ce prix ?" (offre/demande, macro, positionnement). Cette approche est cohérente avec l'analyse fondamentale mais **orthogonale au trend-following directionnel** : un système trend-following doit mesurer que la tendance est en cours, pas seulement ses causes.

3. **Conséquence opérationnelle** : sans critère de tendance-prix, le système peut produire un signal directionnel (LONG/SHORT) cohérent avec les fondamentaux **même quand le prix évolue exactement à l'opposé**. Le cas cacao en est la démonstration : fondamentaux/positionnement LONG pendant 11 jours de chute.

4. **Le VIX est l'exception qui confirme la règle** : il est COUVERT parce que son propre niveau absolu est le meilleur prédicteur de sa future direction (mean-reversion), donc les auteurs de la fiche l'ont naturellement inclus. Pour tous les autres actifs, le niveau de prix propre n'a pas été inclus car il était perçu comme un signal technique ("on fait de l'analyse fondamentale, pas de l'analyse technique").

**Conclusion** : la thèse "trend-following directionnel" n'est pas instrumentée comme telle dans 11 fiches sur 12. C'est un défaut de famille, pas un bug cacao.

---

## 4. Faisabilité technique

### Question : le moteur sait-il déjà calculer un momentum/z-score sur le prix propre d'un actif ?

**Réponse : OUI, sans toucher au moteur.**

**Preuve dans le code** :

1. **Pattern `mouvement_or_5j`** (`criteres_calculator.py` ligne ~1745) :
   ```python
   if cle == "mouvement_or_5j" or cle.startswith("flux_etf_"):
       # perf 5j → z-score sur fenêtre des perfs 5j glissantes
   ```
   Ce pattern calcule exactement un **z-score de la performance sur 5 jours glissants** pour n'importe quel ticker Twelve. Il suffit d'ajouter une entrée dans `TWELVE_SYMBOLS` avec le ticker du sous-jacent et une `cle_courante` qui commence par `flux_etf_` ou égale la clé spéciale — ou, plus proprement, que la cle soit reconnue dans le dispatcher.

2. **Pattern `dxy_trend_20j`** via FRED (DTWEXBGS) : z-score sur une série de closes avec `zscore_window=60`. Ce pattern (`_handle_fred_zscore`) est exactement ce qu'il faudrait pour un `momentum_prix_20j_*` si le sous-jacent est disponible via Twelve ou FRED.

3. **Pattern `sox_trend_5j`** (`TWELVE_SYMBOLS["sox_trend_5j"] = "SOXX"`) : z-score d'une série de closes Twelve. Le dispatcher traite les symboles simples en "cas par défaut : z-score sur les closes" (ligne ~1763). **Ajouter `"momentum_prix_20j_cacao": "CC=F"` dans `TWELVE_SYMBOLS` suffirait** à calculer le z-score des closes cacao sur 60 jours sans aucune nouvelle logique.

4. **RSI sur actif propre** : le pattern `rsi_14j_fchi` / `rsi_14j_gspc` / `rsi_14j_ixic` est déjà généralisable — le calculateur reconnaît `(RSI, symbol)` dans `TWELVE_SYMBOLS` et calcule le RSI local via `_compute_rsi`.

**Ce qui est déjà disponible sans modification du moteur** :
- Z-score de closes sur N jours (pattern `sox_trend_5j` ou `flux_etf_*` / `mouvement_or_5j`)
- Z-score de performance glissante sur 5j (pattern `flux_etf_*`)
- RSI sur le prix propre (pattern `(RSI, ticker)`)

**Ce qui nécessiterait une légère modification du calculateur** :
- Un z-score de performance glissante sur **20 jours** (au lieu de 5j) : le code de la branche `mouvement_or_5j` est câblé sur une fenêtre de 5 (`closes[i] / closes[i-5] - 1.0`). Pour 20j, il faudrait soit (a) modifier cette constante pour la rendre paramétrable (trivial — 1 ligne dans le handler), soit (b) passer par le cas par défaut "z-score sur les closes" qui est déjà générique et n'a pas de fenêtre de perf fixée.

**Verdict faisabilité** : ajouter un `momentum_prix_20j_*` nécessite **au maximum 2 changements** :
1. Ajouter `"momentum_prix_20j_cacao": "CC=F"` dans `TWELVE_SYMBOLS` (mapping)
2. Ajouter une entrée dans le handler de dispatch (ou utiliser le cas par défaut z-score sur closes, qui est déjà générique)

**Le moteur n'a pas besoin d'être retouché en profondeur.** La mécanique de calcul existe déjà : z-score d'une série de closes Twelve sur une fenêtre configurée (`zscore_window`). Il suffit de brancher le bon ticker et la bonne cle.

---

## 5. Recommandations par fiche ABSENTE / FAIBLE

> Rappel : ces recommandations sont des **RECOS** — aucune implémentation. Décision Thomas requise avant toute modification de fiche.

### Méthodologie commune

Pour chaque fiche, le critère à ajouter suit ce patron :
- **Type** : `zscore` sur les closes du sous-jacent (fenêtre 60 jours)
- **Signe** : `+1` (hausse du prix propre = signal LONG, tendance suivie)
- **Pertinence** : forte sur 24h (la tendance récente est très pertinente pour 24h) et 7j, modérée sur 1m (les fondamentaux reprennent le dessus)
- **Poids** : calibré pour représenter ~15-20% du poids total de la fiche, suffisant pour inverser un signal quant erroné quand la tendance est claire (≥1,5σ)

### 5.1 Cacao — reco du case-study (reprendre telle quelle)

Reco documentée dans `cacao-case-study.md` :

```
cle_courante : momentum_prix_20j_cacao
nom          : Tendance du cacao (20 jours)
source       : Twelve Data (CC=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 9
pertinences  : {24h: 0.8, 7j: 1.0, 1m: 0.8}
```

Ajustement secondaire recommandé : réduire `hf_positioning_flux_options` de 7 → 5 une fois le critère momentum ajouté (pour que le COT contrarian ne représente pas >25% du signal effectif).

**Impact estimé** (repris du case-study) : sur la période 03-09/06, avec le prix du cacao en baisse de ~7% sur 20j, un z-score ~-1,5 σ avec poids 9 et pertinence 0,8 sur 24h aurait produit une contribution ~-4,3. Score net estimé : 1,186 + (-4,3) = -3,1 → **SHORT**.

---

### 5.2 Café — reco

```
cle_courante : momentum_prix_20j_cafe
nom          : Tendance du café Arabica (20 jours)
source       : Twelve Data (KC=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 8
pertinences  : {24h: 0.7, 7j: 1.0, 1m: 0.7}
```

**Justification** : poids total fiche = 44. Un poids 8 représente ~18% — suffisant pour contrebalancer une lecture contrarian erronée du COT (poids 5). Le café est très volatile (seuil 7% sur 1m), la tendance sur 20j est très informative pour les horizons 24h/7j.

**Ajustement secondaire** : pas nécessaire immédiatement — le critère le plus lourd est la météo Brésil (11), qui est fondamentale et justifiée. Le COT (5) est proportionné.

---

### 5.3 Blé — reco

```
cle_courante : momentum_prix_20j_ble
nom          : Tendance du blé (20 jours)
source       : Twelve Data (ZW=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 7
pertinences  : {24h: 0.6, 7j: 1.0, 1m: 0.6}
```

**Justification** : le blé est fortement piloté par les fondamentaux (WASDE poids 11, sécheresse poids 9, tension mer Noire poids 8). Un momentum-prix à poids 7 ne prendra pas le dessus sur les fondamentaux en régime normal, mais captera les tendances de prix persistantes que les fondamentaux mensuels ne voient pas toujours en temps réel (la pertinence 24h est volontairement modérée à 0.6 car les fondamentaux blé sont les vrais drivers). Pertinence 1m réduite (0.6) car sur 1m, WASDE/météo dominent légitimement.

---

### 5.4 Cuivre — reco

```
cle_courante : momentum_prix_20j_cuivre
nom          : Tendance du cuivre (20 jours)
source       : Twelve Data (HG=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 7
pertinences  : {24h: 0.7, 7j: 1.0, 1m: 0.7}
```

**Justification** : le cuivre est dominé par le PMI Caixin (poids 12) et les stocks LME (poids 8). Un momentum-prix à 7 représente ~14% du total (48) — suffisant pour signaler les tendances installées sans écraser les fondamentaux. Le cuivre est particulièrement sensible aux tendances macro chinoises, et le momentum-prix captera ces tendances même quand le PMI mensuel n'a pas encore bougé.

---

### 5.5 Pétrole — reco

```
cle_courante : momentum_prix_20j_petrole
nom          : Tendance du pétrole Brent (20 jours)
source       : Twelve Data (BZ=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 6
pertinences  : {24h: 0.6, 7j: 0.9, 1m: 0.7}
```

**Justification** : poids légèrement inférieur (6) car la fiche pétrole est déjà riche en fondamentaux opérationnels (EIA surprise poids 10, OPEC poids 6) et le COT (7) est proportionné. Un poids 6 = ~11% du total (52) — suffisant pour corriger un COT erroné sans écraser les signaux d'offre hebdomadaires. Pertinence 24h modérée (0.6) : l'EIA hebdomadaire est plus réactif sur ce court horizon.

---

### 5.6 Or — reco

```
cle_courante : momentum_prix_20j_or
nom          : Tendance de l'or (20 jours)
source       : Twelve Data (GC=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 7
pertinences  : {24h: 0.7, 7j: 0.9, 1m: 0.7}
```

**Justification** : l'or est dominé par les TIPS (poids 12) et les banques centrales (poids 9). Cependant l'audit trio du 05/06 a montré que l'or a monté en 2025 malgré des taux réels élevés (régime de découplage). Un momentum-prix à 7 permettrait de capter ces régimes atypiques où les fondamentaux classiques sont contredits par le trend. Pertinence 1m plus faible (0.7) car sur 1m les TIPS/CB restent les vrais drivers.

**Note** : `flux_etf_or_5j` (poids 5) est déjà proche d'un momentum-prix 5j. Le critère proposé ici est un horizon 20j plus stable — les deux peuvent coexister (horizon différent). Pas de dédup nécessaire.

---

### 5.7 Argent — reco

```
cle_courante : momentum_prix_20j_argent
nom          : Tendance de l'argent (20 jours)
source       : Twelve Data (SI=F)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 7
pertinences  : {24h: 0.7, 7j: 0.9, 1m: 0.7}
```

**Justification** : l'argent est actuellement piloté par le prix de l'or (`mouvement_or_5j` poids 7) et le ratio or/argent (poids 7). Ces deux critères capturent le momentum de l'**or** et la valeur relative, mais pas la tendance propre de l'argent. Un momentum-prix argent direct permettrait de capturer les mouvements idiosyncratiques de l'argent (demande industrielle, grèves mines) indépendamment de l'or.

**Ajustement secondaire** : on pourrait envisager de réduire `mouvement_or_5j` de 7 à 5 une fois le critère argent direct ajouté, pour équilibrer le poids entre momentum propre et proxy.

---

### 5.8 EUR/USD — reco

```
cle_courante : momentum_prix_20j_eurusd
nom          : Tendance EUR/USD (20 jours)
source       : Twelve Data (EURUSD=X ou EUR=X)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse EUR/USD = LONG)
poids        : 6
pertinences  : {24h: 0.7, 7j: 0.9, 1m: 0.6}
```

**Justification** : la fiche EUR/USD est fortement dominée par les différentiels de taux (différentiel 2Y poids 12, DXY poids 9, différentiel 10Y poids 6). Ces critères sont de bons prédicteurs structurels mais réagissent peu aux mouvements techniques intra-tendance. Un momentum-prix EUR/USD direct (poids 6 = ~12% du total 49) permettrait de capter les tendances de change installées que les différentiels de taux ne signalent pas toujours (carry-trade, risk-off flows). Pertinence 1m plus faible (0.6) car les différentiels de taux dominent sur le long terme.

---

### 5.9 S&P 500 — reco (amélioration du FAIBLE)

Le S&P a déjà un RSI (poids 2). Reco : **conserver le RSI et ajouter un momentum-prix directionnel explicite** (le RSI est contrarian/oversold, ce qui est différent d'un suivi de tendance).

```
cle_courante : momentum_prix_20j_sp500
nom          : Tendance du S&P 500 (20 jours)
source       : Twelve Data (^GSPC via ETF SPY=F ou proxy Twelve)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 5
pertinences  : {24h: 0.7, 7j: 0.8, 1m: 0.4}
```

**Justification** : poids modeste (5 = ~8% du total 61) car le S&P est déjà bien couvert par les taux, le VIX, le HY spread. Un momentum-prix directionnel (signe +1) complète le RSI contrarian (signe -1) en couvrant les deux régimes : tendance installée (momentum +1) et retournement potentiel (RSI -1). Pertinence 1m faible (0.4) : sur 1m, les TIPS et le HY spread dominent.

---

### 5.10 Nasdaq — reco (amélioration du FAIBLE)

Même logique que S&P.

```
cle_courante : momentum_prix_20j_nasdaq
nom          : Tendance du Nasdaq (20 jours)
source       : Twelve Data (^IXIC via proxy ETF QQQ ou Twelve)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 5
pertinences  : {24h: 0.7, 7j: 0.8, 1m: 0.4}
```

**Note** : `sox_trend_5j` (poids 7) est déjà un très bon proxy de la tendance technologique — un momentum Nasdaq direct à poids 5 est complémentaire (horizon 20j vs 5j SOX) et non redondant.

---

### 5.11 CAC 40 — reco (amélioration du FAIBLE)

```
cle_courante : momentum_prix_20j_cac
nom          : Tendance du CAC 40 (20 jours)
source       : Twelve Data (^FCHI via proxy ETF EWQ ou Twelve)
type_norm    : zscore (zscore_window: 60, zscore_div: 2, cap: 1.0)
signe        : +1  (hausse = LONG)
poids        : 5
pertinences  : {24h: 0.7, 7j: 0.8, 1m: 0.4}
```

**Note critique CAC** : le case-study du bulletin 05/06 a montré que le CAC a un biais "à l'envers" persistant (7/7 FAUX selon le ticket C). Ce biais pourrait être lié à l'absence de momentum-prix directionnel — le spread OAT-Bund (poids 10) et le V2X (poids 8) pilotent la direction, mais si le CAC baisse dans un contexte de spread stable (correction purement marché), rien ne le signale. Un momentum-prix 20j (poids 5) serait une première correction partielle, à évaluer dans le Ticket C.

---

## 6. Tableau de priorité d'implémentation

| Priorité | Fiche | Urgence | Raison |
|---|---|---|---|
| **P0** | Cacao | Critique | WR tradable 29%, biais LONG documenté, case-study complet. Reco prête. |
| **P1** | Café | Haute | Structure identique au cacao (même famille agri-softs, même absence). |
| **P1** | Blé | Haute | Fiche mono-critère documentée (◧ visible), fondamentaux mensuels lents. |
| **P1** | Cuivre | Haute | PMI Caixin mensuel + COT = risque de biais similaire cacao si tendance ≠ fondamentaux. |
| **P2** | Pétrole | Moyenne | EIA hebdomadaire + OPEC réagissent vite — risque moindre, mais COT poids 7 reste. |
| **P2** | Or | Moyenne | Découplage TIPS documenté (audit 05/06). Reco prête à intégrer. |
| **P2** | Argent | Moyenne | Piloté par l'or (proxy) — manque de signal propre sur mouvements idiosyncratiques. |
| **P3** | EUR/USD | Faible | Différentiels de taux sont de bons prédicteurs FX — risque plus faible. |
| **P3** | CAC 40 | Faible | Lié au Ticket C (~23/06) — mesurer avant d'agir sur le biais. |
| **P3** | S&P / Nasdaq | Faible | RSI existant + breadth + taux couvrent partiellement. |

---

## 7. Résumé des décisions requises (checkpoint Thomas)

1. **Valider la reco cacao v3** : `momentum_prix_20j_cacao` poids 9 + `hf_positioning` 7→5. (Déjà documentée dans Mémo S5 comme P1.)
2. **Étendre la reco aux autres ABSENTS** : valider le principe d'un critère momentum-prix sur les commodities (café, blé, cuivre, pétrole, or, argent) — les fiches individuelles pourront être écrites après validation du principe.
3. **Indices + EUR/USD** : valider si les RSI existants suffisent ou si un momentum directionnel complémentaire est souhaité (P3, peut attendre après le Ticket C).

---

*Balayage complet — 12 fiches analysées, aucun code/YAML modifié. Auteur : @data-analyst. 2026-06-10*
