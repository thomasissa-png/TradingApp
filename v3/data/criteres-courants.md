# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T14:25:32.723008+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T14:25:32.723008+00:00'
  mouvement_or_5j:
    valeur: -0.0010759346159484595
    valeur_normalisee: -0.04307429828782588
    valeur_ponderee: -0.04307429828782588
    ts: '2026-06-02T14:25:32.723008+00:00'
  ratio_gold_silver:
    valeur: 59.634140607098566
    ts: '2026-06-02T14:25:32.723008+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.003554854481668257
    valeur_normalisee: -0.12401729367810031
    valeur_ponderee: -0.12401729367810031
    ts: '2026-06-02T14:25:32.723008+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T14:25:32.723008+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.02266207687894428
    valeur_normalisee: -0.07999548948171145
    valeur_ponderee: -0.07999548948171145
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T14:25:32.723008+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T14:25:32.723008+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T14:25:32.723008+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Les news LONG (Chine lève interdictions Brésil, baisse production
      australienne) sont contredites par des news SHORT récentes (Euronext à 3 semaines
      bas, chute des prix due au pétrole et prises de bénéfices). Le prix a baissé
      de 10% sur 20j, suggérant que le marché a déjà intégré les facteurs baissie
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T14:25:32.723008+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.008274920998681434
    valeur_normalisee: 0.042716875230174124
    valeur_ponderee: 0.042716875230174124
    ts: '2026-06-02T14:25:32.723008+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.0015243902439023849
    valeur_normalisee: 0.06792308036174904
    valeur_ponderee: 0.06792308036174904
    ts: '2026-06-02T14:25:32.723008+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T14:25:32.723008+00:00'
  rsi_14j_fchi:
    valeur: 55.14414327341266
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.1718737046270795
    valeur_normalisee: 0.08593685231353974
    valeur_ponderee: 0.08593685231353974
    ts: '2026-06-02T14:25:32.723008+00:00'
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T14:25:32.723008+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T14:25:32.723008+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T14:25:32.723008+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Majorité de news SHORT (dollar fort, stocks abondants) dominent,
      malgré une news LONG récente (Chine lève interdictions Brésil) de matérialité
      high mais non confirmée. Le prix a baissé de 6.86% sur 20j, confirmant le biais
      baissier.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.60'
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
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Majorité de news SHORT (dollar fort, stocks abondants) dominent,
      malgré une news LONG récente (Chine lève interdictions Brésil) de matérialité
      high mais non confirmée. Le prix a baissé de 6.86% sur 20j, confirmant le biais
      baissier.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.60'
    p2_shadow_contrib_exclu:
      24h: -10.433333333333332
      7j: -10.433333333333332
      1m: -10.433333333333332
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T14:25:32.723008+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Deux news high du 2 juin s'opposent (tarifs US vs levée interdiction
      Chine), tandis que les news LONG plus anciennes sont contredites par la baisse
      récente de -7.11% sur 20j. Signal trop dispersé et prix déjà baissier.
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
    ts: '2026-06-02T14:25:32.723008+00:00'
  meteo_vietnam_robusta:
    valeur: -0.21638148650563183
    valeur_normalisee: -0.10819074325281591
    valeur_ponderee: -0.10819074325281591
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Les news LONG dominent en nombre et matérialité, notamment
      les PMI chinois solides et les profits industriels, mais la proposition de tarif
      US sur le Brésil et les tensions géopolitiques créent un contre-courant. Le
      prix a déjà monté de +3.89% sur 5j, ce qui limite la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.60'
    p2_shadow_contrib_exclu:
      24h: -1.3666666666666667
      7j: -1.3666666666666667
      1m: -1.3666666666666667
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T14:25:32.723008+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Les news LONG dominent en nombre et matérialité, notamment
      les PMI chinois solides et les profits industriels, mais la proposition de tarif
      US sur le Brésil et les tensions géopolitiques créent un contre-courant. Le
      prix a déjà monté de +3.89% sur 5j, ce qui limite la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.60'
    p2_shadow_contrib_exclu:
      24h: 4.433333333333334
      7j: 4.433333333333334
      1m: 4.433333333333334
  ratio_cuivre_or:
    valeur: 0.0014785690629555298
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
eurusd:
  differentiel_taux_10y_us_bund:
    valeur: 1.4536842105
    valeur_normalisee: 0.3001881730442448
    valeur_ponderee: 0.3001881730442448
    ts: '2026-06-02T14:25:32.723008+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.87375
    valeur_normalisee: 0.5736785498522486
    valeur_ponderee: 0.5736785498522486
    ts: '2026-06-02T14:25:32.723008+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T14:25:32.723008+00:00'
  sox_trend_5j:
    valeur: 589.695
    valeur_normalisee: 0.9499900788434846
    valeur_ponderee: 0.9499900788434846
    ts: '2026-06-02T14:25:32.723008+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16290342125459464
    valeur_normalisee: -0.29630467992236387
    valeur_ponderee: -0.29630467992236387
    ts: '2026-06-02T14:25:32.723008+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Nvidia PC chip,
      HPE, Alphabet/Berkshire) et fraîcheur du 2 juin. Le prix +10.41% sur 20j confirme
      le momentum, sans contradiction majeure.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 3.8666666666666663
      7j: 3.8666666666666663
      1m: 3.8666666666666663
  flux_etf_qqq_5j:
    valeur: 0.017020826928541455
    valeur_normalisee: 0.030604879158831262
    valeur_ponderee: 0.030604879158831262
    ts: '2026-06-02T14:25:32.723008+00:00'
  spread_nasdaq_russell2000:
    valeur: 452.81000000000006
    valeur_normalisee: 0.887477715953824
    valeur_ponderee: 0.887477715953824
    ts: '2026-06-02T14:25:32.723008+00:00'
  rsi_14j_ixic:
    valeur: 78.42843053404386
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T14:25:32.723008+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T14:25:32.723008+00:00'
  flux_etf_or_5j:
    valeur: -0.003043478260869592
    valeur_normalisee: 0.09681953110045616
    valeur_ponderee: 0.09681953110045616
    ts: '2026-06-02T14:25:32.723008+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Majorité de news LONG (escalade Iran-USA, Liban, Ukraine)
      avec matérialité high, mais le prix a baissé de 4.2% sur 20j, suggérant que
      le marché a déjà intégré une partie des tensions. La fraîcheur des news (2 juin)
      et la persistance des conflits limitent le biais baissier, mais la conviction
      est aba
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 25.166666666666664
      7j: 25.166666666666664
      1m: 25.166666666666664
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T14:25:32.723008+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T14:25:32.723008+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T14:25:32.723008+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Malgré un recul de -9.83% sur 20j, les news du jour montrent
      un net biais LONG avec des tensions persistantes au Liban, des risques sur le
      détroit d'Ormuz, et une inflation énergétique élevée en zone euro. Les signaux
      SHORT (discussions Iran, cessez-le-feu Liban) sont contredits par les faits
      de ter
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 28.166666666666668
      7j: 28.166666666666668
      1m: 28.166666666666668
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T14:25:32.723008+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Malgré un recul de -9.83% sur 20j, les news du jour montrent
      un net biais LONG avec des tensions persistantes au Liban, des risques sur le
      détroit d'Ormuz, et une inflation énergétique élevée en zone euro. Les signaux
      SHORT (discussions Iran, cessez-le-feu Liban) sont contredits par les faits
      de ter
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 26.03333333333334
      7j: 26.03333333333334
      1m: 26.03333333333334
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
    ts: '2026-06-02T14:25:32.723008+00:00'
  spread_brent_wti:
    valeur: 2.970339999999993
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
sp500:
  vix_regime:
    valeur: 23.57
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T14:25:32.723008+00:00'
  hy_credit_spread:
    valeur: 2.72
    valeur_normalisee: -0.5532705134158924
    valeur_ponderee: -0.5532705134158924
    ts: '2026-06-02T14:25:32.723008+00:00'
  breadth_sp_ma50:
    valeur: 0.2757296669657466
    valeur_normalisee: -0.615135314894268
    valeur_ponderee: -0.615135314894268
    ts: '2026-06-02T14:25:32.723008+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.009712319253694313
    valeur_normalisee: 0.0535379492068654
    valeur_ponderee: 0.0535379492068654
    ts: '2026-06-02T14:25:32.723008+00:00'
  rsi_14j_gspc:
    valeur: 74.59639486537142
    ts: '2026-06-02T14:25:32.723008+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T14:25:32.723008+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T14:25:32.723008+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T14:25:32.723008+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T14:25:32.723008+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T14:25:32.723008+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T14:25:32.723008+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T14:25:32.723008+00:00'
    synthese_rationale: Majorité de news LONG (escalades Iran/US, Israël/Hezbollah)
      mais le VIX a baissé de 15% sur 20j, indiquant que le marché a déjà pricé ces
      tensions. Une seule news SHORT (cessez-le-feu Liban) ne suffit pas à inverser
      le biais, mais la baisse du prix réduit la conviction.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 24.266666666666666
      7j: 24.266666666666666
      1m: 24.266666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T14:25:32.723008+00:00'
```
