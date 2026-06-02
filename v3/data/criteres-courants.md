# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T12:15:08.927095+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T12:15:08.927095+00:00'
  mouvement_or_5j:
    valeur: 0.006883524004035024
    valeur_normalisee: 0.13101091401380544
    valeur_ponderee: 0.13101091401380544
    ts: '2026-06-02T12:15:08.927095+00:00'
  ratio_gold_silver:
    valeur: 59.386176929135885
    ts: '2026-06-02T12:15:08.927095+00:00'
  alpha_argent_vs_or_5j:
    valeur: 0.0006581110045666971
    valeur_normalisee: -0.0704077582445177
    valeur_ponderee: -0.0704077582445177
    ts: '2026-06-02T12:15:08.927095+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T12:15:08.927095+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.010093622001170255
    valeur_normalisee: -0.010882415223491364
    valeur_ponderee: -0.010882415223491364
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T12:15:08.927095+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T12:15:08.927095+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T12:15:08.927095+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: 'News mitigées : baisse production australienne (LONG) vs
      baisse Euronext et pression pétrole (SHORT). Prix en baisse de 9.48% sur 20j
      suggère que le marché a déjà intégré les éléments baissiers, sans signal frais
      dominant.'
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T12:15:08.927095+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.013500534769797179
    valeur_normalisee: -0.07679225980550873
    valeur_ponderee: -0.07679225980550873
    ts: '2026-06-02T12:15:08.927095+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.014390081912774022
    valeur_normalisee: 0.2762766481355668
    valeur_ponderee: 0.2762766481355668
    ts: '2026-06-02T12:15:08.927095+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T12:15:08.927095+00:00'
  rsi_14j_fchi:
    valeur: 55.972912686038896
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.1718737046270795
    valeur_normalisee: 0.08593685231353974
    valeur_ponderee: 0.08593685231353974
    ts: '2026-06-02T12:15:08.927095+00:00'
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T12:15:08.927095+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T12:15:08.927095+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T12:15:08.927095+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: Majoritarily SHORT news (dollar strength, abundant supplies,
      rising inventories) dominate, but a recent LONG high-mat news (China lifts Brazil
      import ban) and price stabilization over 5j (+0.78%) reduce conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.51'
    p2_shadow_contrib_exclu:
      24h: -10.433333333333332
      7j: -10.433333333333332
      1m: -10.433333333333332
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: Majoritarily SHORT news (dollar strength, abundant supplies,
      rising inventories) dominate, but a recent LONG high-mat news (China lifts Brazil
      import ban) and price stabilization over 5j (+0.78%) reduce conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.51'
    p2_shadow_contrib_exclu:
      24h: -10.433333333333332
      7j: -10.433333333333332
      1m: -10.433333333333332
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T12:15:08.927095+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: Une news SHORT high (tarif US sur Brésil) contredit les multiples
      news LONG sur les récoltes et prix, et le prix a baissé de 6.66% sur 20j, suggérant
      que le marché a déjà intégré le tarif. Aucun signal dominant clair.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 37.96666666666667
      7j: 37.96666666666667
      1m: 37.96666666666667
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T12:15:08.927095+00:00'
  meteo_vietnam_robusta:
    valeur: -0.21638148650563183
    valeur_normalisee: -0.10819074325281591
    valeur_ponderee: -0.10819074325281591
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: 'Les PMI manufacturiers chinois et sud-coréens solides, les
      bénéfices industriels chinois en forte hausse, et les risques d''offre (Cobre
      Panama, tensions géopolitiques) dominent les signaux short dispersés (tarifs,
      ralentissement officiel chinois). Le prix a déjà monté de 3.44% sur 5j, ce qui
      limite '
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.51'
    p2_shadow_contrib_exclu:
      24h: -1.3666666666666667
      7j: -1.3666666666666667
      1m: -1.3666666666666667
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T12:15:08.927095+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: 'Les PMI manufacturiers chinois et sud-coréens solides, les
      bénéfices industriels chinois en forte hausse, et les risques d''offre (Cobre
      Panama, tensions géopolitiques) dominent les signaux short dispersés (tarifs,
      ralentissement officiel chinois). Le prix a déjà monté de 3.44% sur 5j, ce qui
      limite '
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.51'
    p2_shadow_contrib_exclu:
      24h: 3.433333333333333
      7j: 3.433333333333333
      1m: 3.433333333333333
  ratio_cuivre_or:
    valeur: 0.0014618050398424105
    valeur_normalisee: 0.9768797451510751
    valeur_ponderee: 0.9768797451510751
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
eurusd:
  differentiel_taux_10y_us_bund:
    valeur: 1.4536842105
    valeur_normalisee: 0.3001881730442448
    valeur_ponderee: 0.3001881730442448
    ts: '2026-06-02T12:15:08.927095+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.75052
    valeur_normalisee: 0.5146191258724944
    valeur_ponderee: 0.5146191258724944
    ts: '2026-06-02T12:15:08.927095+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T12:15:08.927095+00:00'
  sox_trend_5j:
    valeur: 571.92999
    valeur_normalisee: 0.8877929217199515
    valeur_ponderee: 0.8877929217199515
    ts: '2026-06-02T12:15:08.927095+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1628968436181819
    valeur_normalisee: -0.3097042226397558
    valeur_ponderee: -0.3097042226397558
    ts: '2026-06-02T12:15:08.927095+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: Dominance de news LONG matérialité haute et fraîches (Nvidia
      chip reinvention, Alphabet IA funding, HPE AI demand) malgré quelques mises
      en garde SHORT. Le prix +10% sur 20j confirme le momentum haussier.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.51'
    p2_shadow_contrib_exclu:
      24h: 4.3999999999999995
      7j: 4.3999999999999995
      1m: 4.3999999999999995
  flux_etf_qqq_5j:
    valeur: 0.035120008225883126
    valeur_normalisee: 0.35922460073081663
    valeur_ponderee: 0.35922460073081663
    ts: '2026-06-02T12:15:08.927095+00:00'
  spread_nasdaq_russell2000:
    valeur: 453.75998000000004
    valeur_normalisee: 0.9414930191721986
    valeur_ponderee: 0.9414930191721986
    ts: '2026-06-02T12:15:08.927095+00:00'
  rsi_14j_ixic:
    valeur: 78.6749097386528
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T12:15:08.927095+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T12:15:08.927095+00:00'
  flux_etf_or_5j:
    valeur: -0.0061862644099786035
    valeur_normalisee: 0.04867063187236333
    valeur_ponderee: 0.04867063187236333
    ts: '2026-06-02T12:15:08.927095+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: Dominance de news géopolitiques LONG (frappes US-Iran, escalade
      Israël-Liban, tensions Ormuz) à matérialité high et fraîcheur ≤48h, malgré quelques
      signaux SHORT (ISM, hausse taux) et un recul de -3.44%/20j. Le marché n'a pas
      encore intégré ces risques, comme le montre le rebond récent de +0.69%/5j.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.51'
    p2_shadow_contrib_exclu:
      24h: 22.3
      7j: 22.3
      1m: 22.3
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T12:15:08.927095+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T12:15:08.927095+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T12:15:08.927095+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: 'Malgré le recul de -11.35% sur 20j, les news du 2 juin montrent
      un signal LONG dominant : tensions Iran/Ormuz (Goldman, trafic perturbé), inflation
      zone euro élevée, et reprise des hostilités au Liban. Les signaux SHORT (cessez-le-feu
      Liban, discussions US-Iran) sont nombreux mais contredits par les'
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.51'
    p2_shadow_contrib_exclu:
      24h: 26.7
      7j: 26.7
      1m: 26.7
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T12:15:08.927095+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: 'Malgré le recul de -11.35% sur 20j, les news du 2 juin montrent
      un signal LONG dominant : tensions Iran/Ormuz (Goldman, trafic perturbé), inflation
      zone euro élevée, et reprise des hostilités au Liban. Les signaux SHORT (cessez-le-feu
      Liban, discussions US-Iran) sont nombreux mais contredits par les'
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.51'
    p2_shadow_contrib_exclu:
      24h: 24.566666666666674
      7j: 24.566666666666674
      1m: 24.566666666666674
    sign_conflict: true
    sign_conflict_details:
    - event_id: a064c322c763
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: oil stocks
      matched_surprise: hausse
      surprise_polarity: up
      title: Avertissement des dirigeants pétroliers sur des stocks très bas et hausse
        imminente des prix
    - event_id: ef3e2bf5d814
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: hausse
      surprise_polarity: up
      title: EIA publie son STEO de mai avec révision à la hausse des prix pétrole
        due aux perturbations Moyen-Orient
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-02T12:15:08.927095+00:00'
  spread_brent_wti:
    valeur: 2.7862599999999986
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
sp500:
  vix_regime:
    valeur: 23.865
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T12:15:08.927095+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-02T12:15:08.927095+00:00'
  breadth_sp_ma50:
    valeur: 0.2758061743825289
    valeur_normalisee: -0.631119706411202
    valeur_ponderee: -0.631119706411202
    ts: '2026-06-02T12:15:08.927095+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.017300533537625062
    valeur_normalisee: 0.2411352806454264
    valeur_ponderee: 0.2411352806454264
    ts: '2026-06-02T12:15:08.927095+00:00'
  rsi_14j_gspc:
    valeur: 75.89804938696159
    ts: '2026-06-02T12:15:08.927095+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T12:15:08.927095+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T12:15:08.927095+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T12:15:08.927095+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T12:15:08.927095+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T12:15:08.927095+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T12:15:08.927095+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T12:15:08.927095+00:00'
    synthese_rationale: Majorité de news LONG (escalades Iran, Israël, Ukraine) mais
      le VIX a baissé de 13% sur 20j, indiquant que le marché a déjà pricé ces tensions.
      Une seule news SHORT (cessez-le-feu Liban) est contredite par d'autres escalades.
      Signal dominant mais prix en baisse réduit la conviction.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 22.566666666666666
      7j: 22.566666666666666
      1m: 22.566666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T12:15:08.927095+00:00'
```
