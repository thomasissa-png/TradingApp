# Reco wording — Noms des critères (libellés affichés)

> Livrable @copywriter → @fullstack. Champ `nom:` uniquement — zéro modification de logique, poids, seuils, clés.
> Branche : claude/elegant-ramanujan-OIKms
> Style de référence : `reco-wording-detail-bulletin.md` (sobre, trader, zéro jargon dev).

**Note acronymes conservés** : PMI, RSI, VIX sont maintenus entre parenthèses car connus des traders et porteurs d'information utile. COT est traduit partout ("gros spéculateurs"). TIPS, COMEX, LME, SHFE sont expliqués ou supprimés selon le contexte.

---

## Reco glossaire (tranche finale : §8)

---

## 1. Or

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `taux_10y_us_reels_tips` | Taux 10Y US réels (TIPS) | Taux d'intérêt réels US (10 ans) |
| `achats_pboc_cb_emergentes` | Achats PBoC + CB émergentes (12m cumulés vs 24m précédents) | Achats d'or des banques centrales (12 derniers mois) |
| `dxy_trend_20j` | DXY trend 20j | Tendance du dollar (20 jours) |
| `cftc_cot_nets` | CFTC COT nets | Positionnement des gros spéculateurs (or) |
| `flux_etf_or_5j` | Flux ETF or agrégés 5j net | Flux vers les fonds or (5 jours) |
| `tension_geopolitique` | Tension géopolitique | Tension géopolitique mondiale |
| `demande_indienne_saisonniere` | Demande indienne saisonnière | Demande saisonnière en Inde |
| `vix_risk_off_proxy` | VIX (risk-off proxy) | Indice de peur des marchés (VIX) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 2. Argent

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `taux_10y_us_reels_tips` | Taux 10Y US réels (TIPS) | Taux d'intérêt réels US (10 ans) |
| `mouvement_or_5j` | Mouvement de l'or 5j | Mouvement de l'or (5 jours) |
| `ratio_gold_silver` | Ratio Gold/Silver | Ratio or / argent |
| `alpha_argent_vs_or_5j` | Alpha Argent-vs-Or 5j | Sur-performance de l'argent face à l'or (5 jours) |
| `caixin_pmi_manuf` | Caixin PMI Chine manuf | Activité industrielle Chine (indice PMI) |
| `cftc_cot_silver` | CFTC COT Silver | Positionnement des gros spéculateurs (argent) |
| `inventaires_comex_silver` | Inventaires COMEX Silver | Stocks d'argent physique (marchés US) |
| `flux_etf_slv_pslv_5j` | Flux ETF SLV+PSLV 5j net | Flux vers les fonds argent (5 jours) |
| `demande_pv_mining_strikes` | Demande photovoltaïque + mining strikes | Demande solaire et grèves minières |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 3. Pétrole (Brent)

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `eia_crude_surprise` | EIA Crude surprise (vs consensus) | Stocks de brut US : surprise hebdomadaire |
| `api_weekly_surprise` | API Weekly Statistical Bulletin surprise | Stocks de brut US : pré-indicateur du mardi |
| `tension_geopol_moyen_orient` | Tension géopolitique Moyen-Orient | Tension géopolitique au Moyen-Orient |
| `cftc_cot_crude_nets` | CFTC COT — managed money nets | Positionnement des gros spéculateurs (pétrole) |
| `opec_production_policy` | OPEC+ politique production | Décision de production de l'OPEC+ |
| `brent_term_structure_m1m2` | Term structure Brent (M1-M2) | Structure des prix futurs Brent (spot vs M+1) |
| `dxy_trend_20j` | DXY trend 20j | Tendance du dollar (20 jours) |
| `cushing_stocks` | Stocks Cushing (hub Brent-WTI) | Stocks au hub pétrolier américain (Cushing) |
| `spread_brent_wti` | Spread Brent-WTI | Écart de prix Brent − WTI |
| `caixin_pmi_manuf` | Caixin PMI Chine manuf. | Activité industrielle Chine (indice PMI) |
| `gate_evenement_extreme` | GATE — événement extrême | Drapeau : événement de marché majeur imminent |

---

## 4. Cuivre

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `caixin_pmi_manuf` | Caixin PMI Chine manuf | Activité industrielle Chine (indice PMI) |
| `inventaires_lme_shfe_5j` | Inventaires LME+SHFE (trend 5j) | Stocks de cuivre mondiaux (tendance 5 jours) |
| `mining_strikes_chili_perou` | Mining strikes Chili/Pérou | Grèves minières (Chili / Pérou) |
| `dxy_trend_20j` | DXY trend 20j | Tendance du dollar (20 jours) |
| `cftc_cot_copper_nets` | CFTC COT Copper nets | Positionnement des gros spéculateurs (cuivre) |
| `term_structure_m1_m3` | Term structure M1-M3 | Structure des prix futurs cuivre (spot vs M+3) |
| `news_construction_infra` | News construction/infra US-Chine | Plans de construction et infrastructures US-Chine |
| `ratio_cuivre_or` | Ratio Cuivre/Or | Ratio cuivre / or (appétit pour le risque) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 5. Blé

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `usda_wasde_stocks_to_use` | USDA WASDE stocks-to-use mondial (delta) | Stocks mondiaux de blé (rapport USDA mensuel) |
| `noaa_drought_midwest_plains` | NOAA drought % Midwest+Plains D2+ | Sécheresse dans les plaines céréalières US |
| `geopolitique_mer_noire` | Géopolitique mer Noire | Tensions géopolitiques en mer Noire |
| `nass_crop_progress` | NASS Crop Progress % good/excellent | État des cultures US (bon / excellent) |
| `demande_chinoise_imports` | Demande chinoise (imports USDA FAS) | Demande chinoise à l'import (blé) |
| `cftc_cot_wheat` | CFTC COT Wheat | Positionnement des gros spéculateurs (blé) |
| `meteo_australie_dryland` | Météo Australie (dryland) | Météo dans les zones céréalières australiennes |
| `egypte_gasc_tenders` | Égypte GASC tenders | Appels d'offres blé de l'Égypte |
| `dxy_trend_20j` | DXY trend 20j | Tendance du dollar (20 jours) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 6. Cacao

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `meteo_ci_ghana_precip_30j` | Météo CI + Ghana (anomalie précip 30j) | Météo Côte d'Ivoire + Ghana (pluies, 30 jours) |
| `arrivees_port_abidjan_sanpedro_20j` | Arrivées port Abidjan+San Pedro (trend 20j) | Arrivées de cacao dans les ports ivoiriens (20 jours) |
| `hf_positioning_flux_options` | Hedge fund positioning + flux options ICE | Positionnement spéculatif + options cacao (ICE) |
| `cftc_cot_cocoa` | CFTC COT Cocoa | Positionnement des gros spéculateurs (cacao) |
| `grindings_q` | Grindings Q (broyages) | Volume de broyage de cacao (demande trimestrielle) |
| `eudr` | EU Deforestation Regulation (EUDR) | Réglementation UE anti-déforestation (impact supply) |
| `spread_ny_london` | Spread NY-London (CC=F vs C-=F) | Écart de prix cacao New York − Londres |
| `maladies_cabosses` | Maladies cabosses (Black Pod, Swollen Shoot) | Maladies des cabosses (impact récolte) |
| `usd_cfa_usd_cedi` | USD/CFA + USD/Cedi | Taux de change franc CFA et cédi ghanéen |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 7. Café

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `meteo_bresil_minas_gerais` | Météo Brésil Minas Gerais (gel/sécheresse) | Météo Brésil — risque gel et sécheresse (Minas Gerais) |
| `stocks_ice_arabica_certifies_20j` | Stocks ICE Arabica certifiés (trend 20j) | Stocks d'Arabica certifiés (tendance 20 jours) |
| `usd_brl` | USD/BRL | Taux de change dollar / real brésilien |
| `cftc_cot_coffee` | CFTC COT Coffee | Positionnement des gros spéculateurs (café) |
| `maladies_cabosses_rouille` | Maladies cabosses/rouille | Maladies du caféier (rouille et cabosses) |
| `cycle_bresil_biannuel` | Cycle Brésil bi-annuel | Cycle de production brésilien (année forte / faible) |
| `spread_arabica_robusta` | Spread Arabica-Robusta | Écart de prix Arabica − Robusta |
| `meteo_vietnam_robusta` | Météo Vietnam (Robusta) | Météo Vietnam — précipitations (Robusta) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 8. S&P 500

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `vix_regime` | VIX régime | Régime de volatilité (VIX) |
| `taux_10y_us_delta_5j` | Taux 10Y US delta 5j | Variation des taux US 10 ans (5 jours) |
| `hy_credit_spread` | HY credit spread (ICE BofA HY OAS) | Écart de crédit obligataire haut rendement US |
| `breadth_sp_ma50` | Breadth S&P (proxy RSP/SPY) | Participation des actions au rallye S&P |
| `dxy_trend_20j` | DXY trend 20j | Tendance du dollar (20 jours) |
| `flux_etf_spy_ivv_5j` | Flux ETF SPY+IVV 5j net | Flux vers les fonds S&P 500 (5 jours) |
| `aaii_bull_bear` | AAII bull-bear | Sentiment des investisseurs particuliers US |
| `shiller_cape_fwd_pe` | Shiller CAPE / Forward P/E | Valorisation du marché (Shiller CAPE / P/E à terme) |
| `rsi_14j_gspc` | RSI 14j ^GSPC | Indicateur technique S&P 500 (RSI 14 jours) |
| `taux_10y_us_reels_tips` | Taux 10Y US réels (TIPS) | Taux d'intérêt réels US (10 ans) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 9. Nasdaq

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `taux_10y_us_reels_tips` | Taux 10Y US réels (TIPS) | Taux d'intérêt réels US (10 ans) |
| `vxn_regime` | VXN régime | Régime de volatilité Nasdaq (VXN) |
| `sox_trend_5j` | SOX trend 5j | Tendance des semi-conducteurs (5 jours) |
| `breadth_nasdaq100_ma50` | Breadth Nasdaq 100 (proxy QQQE/QQQ) | Participation des actions au rallye Nasdaq |
| `concentration_top7` | Concentration top 7 | Concentration sur les 7 plus grosses valeurs |
| `sentiment_ia_megacaps` | Sentiment IA / méga-caps | Sentiment sur l'IA et les méga-caps tech |
| `flux_etf_qqq_5j` | Flux ETF QQQ 5j net | Flux vers le fonds Nasdaq (5 jours) |
| `spread_nasdaq_russell2000` | Spread Nasdaq-Russell 2000 | Écart de performance Nasdaq − petites valeurs US |
| `rsi_14j_ixic` | RSI 14j ^IXIC | Indicateur technique Nasdaq (RSI 14 jours) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 10. CAC 40

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `v2x_regime` | V2X régime | Régime de volatilité Europe (V2X) |
| `spread_oat_bund_10y` | Spread OAT-Bund 10Y (bp) | Écart de taux France − Allemagne (10 ans) |
| `alpha_cac_vs_sp_5j` | Alpha CAC vs S&P 5j | Sur-performance du CAC face au S&P 500 (5 jours) |
| `breadth_cac_ma50` | Breadth CAC (%>MA50) | Participation des valeurs CAC au-dessus de leur moyenne (non disponible) |
| `flux_etf_msci_france_5j` | Flux ETF MSCI France 5j net | Flux vers les fonds actions France (5 jours) |
| `tension_politique_fr` | Tension politique FR | Stabilité politique en France |
| `rsi_14j_fchi` | RSI 14j ^FCHI | Indicateur technique CAC 40 (RSI 14 jours) |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 11. EUR/USD

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `differentiel_taux_2y_us_de` | Différentiel taux 2Y US-DE | Écart de taux courts US − Allemagne (2 ans) |
| `differentiel_taux_10y_us_bund` | Différentiel taux 10Y US-Bund | Écart de taux longs US − Allemagne (10 ans) |
| `dxy_trend_20j` | DXY trend 20j | Tendance du dollar (20 jours) |
| `usd_jpy_proxy_risk` | USD/JPY (proxy risk) | Taux de change dollar / yen (signal de risque) |
| `fedwatch_proba` | FedWatch proba | Probabilité de baisse des taux Fed (marché) |
| `cftc_cot_eur_nets` | CFTC COT EUR nets | Positionnement des gros spéculateurs (euro) |
| `spread_oat_bund_stress_ez` | Spread OAT-Bund (stress EZ) | Écart de taux France − Allemagne (stress zone euro) |
| `balance_commerciale_ez` | Balance commerciale EZ | Balance commerciale de la zone euro |
| `gate_regime_extreme` | GATE régime extrême | Drapeau : événement de marché majeur imminent |

---

## 12. VIX

| cle_courante | nom actuel | nom proposé |
|---|---|---|
| `niveau_vix_absolu` | Niveau VIX absolu | Niveau absolu de la peur des marchés (VIX) |
| `term_structure_vix_vix3m` | Term structure VIX/VIX3M | Structure des prix : VIX court vs VIX 3 mois |
| `put_call_ratio_cboe_5j` | Put/Call ratio CBOE 5j moy | Ratio puts / calls options US (moyenne 5 jours) |
| `skew_index_cboe` | SKEW Index CBOE | Indice de risque de choc extrême (SKEW) |
| `vvix` | VVIX | Volatilité de la volatilité (VVIX) |
| `gap_rv_iv` | Gap RV-IV (réalisée 20j vs implicite) | Écart volatilité réelle − volatilité implicite (20 jours) |
| `cftc_cot_vix_nets` | CFTC COT VIX nets | Positionnement des gros spéculateurs (VIX futures) |
| `tension_geopolitique_active` | Tension géopolitique active | Événement géopolitique actif (3 jours) |
| `gate_evenement_macro_imminent` | GATE événement macro imminent | Drapeau : événement macro majeur imminent |

---

## Reco glossaire

**Verdict : OUI — mini-glossaire recommandé**, limité aux 5 termes ci-dessous. Raison : PMI, RSI, VIX sont connus des traders actifs mais SKEW, VVIX et le principe COT méritent une ligne d'ancrage. Le glossaire n'est pas intégré dans le tableau dense — il s'affiche en note de bas de page ou dans un tooltip « ? » au survol du titre de colonne.

| Terme gardé | Définition en 1 ligne (style bulletin) |
|---|---|
| **PMI** | Indice d'activité des directeurs d'achat — au-dessus de 50 = expansion, en dessous = contraction |
| **RSI** | Indicateur technique de sur-achat / sur-vente sur une période donnée (30 = très vendu, 70+ = très acheté) |
| **VIX / VXN / V2X** | Indice de peur du marché : mesure la volatilité attendue sur 30 jours (US / Nasdaq / Europe) |
| **COT (gros spéculateurs)** | Rapport hebdomadaire CFTC : positions nettes des fonds sur les marchés dérivés — signal contrarian aux extrêmes |
| **SKEW / VVIX** | Mesures du risque de choc extrême et de la nervosité sur le VIX lui-même — montent avant les crises |
