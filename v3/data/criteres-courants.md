# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-09T05:23:35.502017+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.3
    valeur_normalisee: 0.8835232067017706
    valeur_ponderee: 0.8835232067017706
    ts: '2026-07-09T05:23:35.502017+00:00'
  mouvement_or_5j:
    valeur: -0.025372978255015388
    valeur_normalisee: -0.3533725973483267
    valeur_ponderee: -0.3533725973483267
    ts: '2026-07-09T05:23:35.502017+00:00'
  ratio_gold_silver:
    valeur: 70.1460901143399
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_silver:
    valeur: 25012.0
    valeur_normalisee: -0.1738925972915221
    valeur_ponderee: -0.1738925972915221
    ts: '2026-07-09T05:23:35.502017+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.01196932859547406
    valeur_normalisee: -0.0027171917969932517
    valeur_ponderee: -0.0027171917969932517
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_argent:
    valeur: -0.10777026860734695
    valeur_normalisee: -0.2365548329087031
    valeur_ponderee: -0.2365548329087031
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_argent:
    valeur: -0.048610319488823106
    valeur_normalisee: -0.15654059016090635
    valeur_ponderee: -0.15654059016090635
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_argent:
    valeur: -0.0651535829796781
    valeur_normalisee: -0.504902057716374
    valeur_ponderee: -0.504902057716374
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur: 920112000.0
    valeur_normalisee: -0.5367988110081852
    valeur_ponderee: -0.5367988110081852
    ts: '2026-07-09T05:23:35.502017+00:00'
  noaa_drought_midwest_plains:
    valeur: 0.32453611091757173
    valeur_normalisee: 0.16226805545878586
    valeur_ponderee: 0.16226805545878586
    ts: '2026-07-09T05:23:35.502017+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: 'Signal LONG dominant avec matérialité élevée : USDA record-low
      planted acres (30 juin) et menaces météo récentes (typhon Chine, conditions
      extrêmes US/Europe) malgré une baisse de prix de -1.73% sur 20j. La fraîcheur
      des news (8 juillet) et la cohérence des signaux LONG surclassent la seule news
      SHO'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: -10.500000000000014
      7j: -10.500000000000014
      1m: -10.500000000000014
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -62992.0
    valeur_normalisee: -0.2609471487988438
    valeur_ponderee: -0.2609471487988438
    ts: '2026-07-09T05:23:35.502017+00:00'
  meteo_australie_dryland:
    valeur: 0.1124713410438114
    valeur_normalisee: 0.0562356705219057
    valeur_ponderee: 0.0562356705219057
    ts: '2026-07-09T05:23:35.502017+00:00'
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_ble:
    valeur: -0.017344138410646637
    valeur_normalisee: -0.049013721233152244
    valeur_ponderee: -0.049013721233152244
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_ble:
    valeur: 0.006318359394977158
    valeur_normalisee: 0.09675372003351682
    valeur_ponderee: 0.09675372003351682
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_ble:
    valeur: -0.013881879637516636
    valeur_normalisee: -0.23948595808982157
    valeur_ponderee: -0.23948595808982157
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-09T05:23:35.502017+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-07-09T05:23:35.502017+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.01617236325026683
    valeur_normalisee: -0.24765869587370937
    valeur_ponderee: -0.24765869587370937
    ts: '2026-07-09T05:23:35.502017+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.011005943209333013
    valeur_normalisee: -0.33322309757058
    valeur_ponderee: -0.33322309757058
    ts: '2026-07-09T05:23:35.502017+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: Escalade géopolitique majeure US-Iran avec frappes mutuelles
      et menaces sur le détroit d'Ormuz, matérialité élevée et fraîcheur immédiate
      (7-9 juillet). Le contexte de prix (+1.11% sur 20j) est contredit par ce choc
      géopolitique récent, justifiant une conviction haute malgré le mouvement haussier
      an
    nature: structurel
    event_id: cd06d1a40215
    event_date: '2026-07-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -103.3333333333334
      7j: -103.3333333333334
      1m: -103.3333333333334
  rsi_14j_fchi:
    valeur: 44.31974265829486
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.011128641384310578
    valeur_normalisee: -0.13701680954926948
    valeur_ponderee: -0.13701680954926948
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.013704481465848906
    valeur_normalisee: -0.46800826238013377
    valeur_ponderee: -0.46800826238013377
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.0300197509698249
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-07-09T05:23:35.502017+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-07'
    valeur: 0.9698239638123765
    valeur_normalisee: 0.4849119819061882
    valeur_ponderee: 0.4849119819061882
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -21877.0
    valeur_normalisee: -0.7211506343761804
    valeur_ponderee: -0.7211506343761804
    ts: '2026-07-09T05:23:35.502017+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 36.43333333333335
      7j: 36.43333333333335
      1m: 36.43333333333335
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  maladies_cabosses:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (El Niño, hausse
      des prix) du 6 au 8 juillet, fraîches et cohérentes avec le rallye de +42% sur
      20j. Les quelques news SHORT du 2 juillet sont anciennes et surclassées.
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 36.43333333333335
      7j: 36.43333333333335
      1m: 36.43333333333335
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.4217823840120152
    valeur_normalisee: 0.876843513493135
    valeur_ponderee: 0.876843513493135
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.20618754649817062
    valeur_normalisee: 0.830309276837419
    valeur_ponderee: 0.830309276837419
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.05697198847130003
    valeur_normalisee: 0.27520629841281946
    valeur_ponderee: 0.27520629841281946
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-09T05:23:35.502017+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.33911835698588594
    valeur_normalisee: 0.16955917849294297
    valeur_ponderee: 0.16955917849294297
    ts: '2026-07-09T05:23:35.502017+00:00'
  usd_brl:
    valeur: 5.16174
    valeur_normalisee: 0.40083242778811756
    valeur_ponderee: 0.40083242778811756
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_coffee:
    valeur: 18605.0
    valeur_normalisee: -0.34422431403586484
    valeur_ponderee: -0.34422431403586484
    ts: '2026-07-09T05:23:35.502017+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: Multiples news à matérialité high et medium sur le risque
      El Niño et les retards de récolte au Brésil dominent, toutes LONG et récentes
      (≤ 48h). Le prix a déjà monté de +16.62% sur 20j, mais la fraîcheur et la cohérence
      des signaux maintiennent une conviction élevée.
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 59.16666666666666
      7j: 59.16666666666666
      1m: 59.16666666666666
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-09T05:23:35.502017+00:00'
  meteo_vietnam_robusta:
    valeur: 0.22131817737296158
    valeur_normalisee: 0.11065908868648079
    valeur_ponderee: 0.11065908868648079
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.16618141394917885
    valeur_normalisee: 0.7478217656678589
    valeur_ponderee: 0.7478217656678589
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.02571532097956486
    valeur_normalisee: 0.09119628978266422
    valeur_ponderee: 0.09119628978266422
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.10797203049205273
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.38139892852595486
    valeur_normalisee: 0.19069946426297743
    valeur_ponderee: 0.19069946426297743
    ts: '2026-07-09T05:23:35.502017+00:00'
  meteo_inde_gujarat_coton:
    valeur: -0.05826163816023121
    valeur_normalisee: 0.029130819080115604
    valeur_ponderee: 0.029130819080115604
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_cotton:
    valeur: 78511.0
    valeur_normalisee: 0.5572122663344853
    valeur_ponderee: 0.5572122663344853
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_coton:
    valeur: 0.0683430045132174
    valeur_normalisee: 0.25506419587172385
    valeur_ponderee: 0.25506419587172385
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_coton:
    valeur: 0.047849915682967925
    valeur_normalisee: 0.45219077183725753
    valeur_ponderee: 0.45219077183725753
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_coton:
    valeur: 0.04608585858585856
    valeur_normalisee: 0.7030103829064197
    valeur_ponderee: 0.7030103829064197
    ts: '2026-07-09T05:23:35.502017+00:00'
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 5.366666666666667
      7j: 5.366666666666667
      1m: 5.366666666666667
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-09T05:23:35.502017+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: 'Les news récentes sont mitigées : l''inflation chinoise et
      la demande IA soutiennent le LONG, mais l''IPC faible et la substitution vers
      l''aluminium pèsent en SHORT. Le prix a baissé de 4% sur 20j, suggérant que
      le marché a déjà intégré ces signaux contradictoires.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 13.46666666666667
      7j: 13.46666666666667
      1m: 13.46666666666667
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_copper_nets:
    valeur: 66140.0
    valeur_normalisee: 0.8735975127573763
    valeur_ponderee: 0.8735975127573763
    ts: '2026-07-09T05:23:35.502017+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: ponctuel
    event_id: 59b2bd143389
    event_date: '2026-07-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 26.0
      7j: 26.0
      1m: 26.0
  ratio_cuivre_or:
    valeur: 0.001492423064377407
    valeur_normalisee: 0.32915467575953133
    valeur_ponderee: 0.32915467575953133
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.04004347138792286
    valeur_normalisee: -0.5701938477456926
    valeur_ponderee: -0.5701938477456926
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.008463520406497227
    valeur_normalisee: -0.14992025143465348
    valeur_ponderee: -0.14992025143465348
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.020060513151524906
    valeur_normalisee: -0.39067498366294084
    valeur_ponderee: -0.39067498366294084
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6608596952000005
    valeur_normalisee: 0.7517709874807109
    valeur_ponderee: 0.7517709874807109
    ts: '2026-07-09T05:23:35.502017+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.5034999999999998
    valeur_normalisee: 0.6269358883790062
    valeur_ponderee: 0.6269358883790062
    ts: '2026-07-09T05:23:35.502017+00:00'
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  usd_jpy_proxy_risk:
    valeur: 162.40535
    valeur_normalisee: 0.7908072799628436
    valeur_ponderee: 0.7908072799628436
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_eur_nets:
    valeur: -50281.0
    valeur_normalisee: -0.7633541132054062
    valeur_ponderee: -0.7633541132054062
    ts: '2026-07-09T05:23:35.502017+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.003600383575974142
    valeur_normalisee: 0.507841522049659
    valeur_ponderee: 0.507841522049659
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.00039355617358460826
    valeur_normalisee: 0.2095131801226557
    valeur_ponderee: 0.2095131801226557
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0010051393210501747
    valeur_normalisee: 0.06458381732233409
    valeur_ponderee: 0.06458381732233409
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.3
    valeur_normalisee: 0.8835232067017706
    valeur_ponderee: 0.8835232067017706
    ts: '2026-07-09T05:23:35.502017+00:00'
  sox_trend_5j:
    valeur: 562.030029
    valeur_normalisee: 0.22134992587954253
    valeur_ponderee: 0.22134992587954253
    ts: '2026-07-09T05:23:35.502017+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1673366735072529
    valeur_normalisee: 0.7002552616635969
    valeur_ponderee: 0.7002552616635969
    ts: '2026-07-09T05:23:35.502017+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée et fraîcheur
      récente : frappes US-Iran (7-9 juillet), vente massive des semi-conducteurs
      (DeepSeek, Samsung, Intel), et hausse du pétrole. Les quelques news LONG (Fed
      accommodante, autorisation Chine H200) sont minoritaires et ne compensent pas
      le biais b'
    nature: structurel
    event_id: eba4ec9b5ec4
    event_date: '2026-07-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 57.700000000000024
      7j: 57.700000000000024
      1m: 57.700000000000024
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  flux_etf_qqq_5j:
    valeur: -0.03389464872638104
    valeur_normalisee: -0.8271625289821887
    valeur_ponderee: -0.8271625289821887
    ts: '2026-07-09T05:23:35.502017+00:00'
  spread_nasdaq_russell2000:
    valeur: 417.95999000000006
    valeur_normalisee: 0.04146139522393057
    valeur_ponderee: 0.04146139522393057
    ts: '2026-07-09T05:23:35.502017+00:00'
  rsi_14j_ixic:
    valeur: 47.975985787239296
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.006465858023292359
    valeur_normalisee: -0.6121798963738113
    valeur_ponderee: -0.6121798963738113
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.006963680944242823
    valeur_normalisee: -0.22631120868292412
    valeur_ponderee: -0.22631120868292412
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.0016278136858772774
    valeur_normalisee: -0.21518283178657047
    valeur_ponderee: -0.21518283178657047
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.3
    valeur_normalisee: 0.8835232067017706
    valeur_ponderee: 0.8835232067017706
    ts: '2026-07-09T05:23:35.502017+00:00'
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_nets:
    valeur: 182210.0
    valeur_normalisee: -0.14086870631385312
    valeur_ponderee: -0.14086870631385312
    ts: '2026-07-09T05:23:35.502017+00:00'
  flux_etf_or_5j:
    valeur: 0.016477577501493146
    valeur_normalisee: 0.4309143378514745
    valeur_ponderee: 0.4309143378514745
    ts: '2026-07-09T05:23:35.502017+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: Escalade géopolitique majeure US-Iran avec frappes mutuelles
      et menaces sur le détroit d'Ormuz, matérialité élevée et fraîcheur immédiate
      (09/07/2026). Malgré le récent recul du prix de l'or (-2.11% sur 20j), la vague
      de news LONG très récentes et de haute matérialité domine, justifiant une convicti
    nature: structurel
    event_id: cd06d1a40215
    event_date: '2026-07-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 174.89999999999998
      7j: 174.89999999999998
      1m: 174.89999999999998
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-09T05:23:35.502017+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_or:
    valeur: -0.02107504786591541
    valeur_normalisee: 0.39531761771567575
    valeur_ponderee: 0.39531761771567575
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_or:
    valeur: -0.013305099268866916
    valeur_normalisee: 0.0021426276427869754
    valeur_ponderee: 0.0021426276427869754
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_or:
    valeur: -0.023074984209760507
    valeur_normalisee: -0.3900120230271239
    valeur_ponderee: -0.3900120230271239
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
petrole:
  eia_crude_surprise:
    valeur: 411357.0
    valeur_normalisee: -0.6144876248362549
    valeur_ponderee: -0.6144876248362549
    ts: '2026-07-09T05:23:35.502017+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et très fraîches
      (09/07) sur l'escalade US-Iran et les perturbations d'approvisionnement, malgré
      une baisse de prix de -9% sur 20j. Le rebond de +10% sur 5j et la hausse de
      6% du pétrole le 09/07 confirment que le marché intègre ce choc géopolitique
      majeur
    nature: structurel
    event_id: cd06d1a40215
    event_date: '2026-07-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 158.3666666666669
      7j: 158.3666666666669
      1m: 158.3666666666669
  cftc_cot_crude_nets:
    valeur: 32995.0
    valeur_normalisee: 0.156717837728965
    valeur_ponderee: 0.156717837728965
    ts: '2026-07-09T05:23:35.502017+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: structurel
    event_id: cd06d1a40215
    event_date: '2026-07-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 158.66666666666697
      7j: 158.66666666666697
      1m: 158.66666666666697
    sign_conflict: true
    sign_conflict_details:
    - event_id: 56c74dc537b8
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: crude oil inventories
      matched_surprise: rising
      surprise_polarity: up
      title: Crude oil jumps 6% with US wholesale inventories rising 0.1% in May,
        energy shares surging, and stocks falling
    - event_id: 19e031d6354c
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins que prévu, signalant
        une demande plus faible
    - event_id: acd93c29c552
      asset: BRENT
      rule_name: opec_production
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: opec
      matched_surprise: baisse de production
      surprise_polarity: down
      title: Arabie saoudite baisse ses prix pétroliers et OPEC+ relève ses objectifs
        de production
    - event_id: 93f789bff896
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: higher
      surprise_polarity: up
      title: US crude stocks fell 6.1M barrels in week ending June 19 despite higher
        imports and refinery runs
    - event_id: 20a6d1bce9f5
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: higher
      surprise_polarity: up
      title: US crude stocks -6.1M barrels (week ending June 19) despite higher imports
    - event_id: 8d8d4a34f31c
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: crude inventories
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins forte que prévu
    - event_id: ddfe1eafaac5
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins forte que prévu, signal
        de demande plus faible
    - event_id: e4081bee17c1
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de brut
      matched_surprise: baisse
      surprise_polarity: down
      title: Optimisme sur la réouverture du détroit d'Ormuz, baisse des prix du brut
        et de l'essence, mais stocks bas et contraintes logistiques
    - event_id: d680e22bc9c3
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: chute
      surprise_polarity: down
      title: Les prix des biens de grande consommation ne devraient pas baisser malgré
        la chute du brut sous 80 $, en raison de stocks achetés lors du conflit au-dessus
        de 1
    - event_id: bae1728ca145
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: baisse
      surprise_polarity: down
      title: Les stocks de pétrole restent élevés malgré la baisse des prix, suggérant
        un décalage entre prix et fondamentaux
    - event_id: 5aa3a2e9d5a3
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse des stocks de brut inférieure aux prévisions, signaux de demande
        mitigés
    - event_id: 34a7e1cc4307
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: oil stocks
      matched_surprise: hausse
      surprise_polarity: up
      title: Avertissement des dirigeants pétroliers sur des stocks bas et une hausse
        des prix de l'essence cet été
    - event_id: 3d89aa578c9d
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut US en baisse, mais moins que prévu
    - event_id: 0c1807e7a1bb
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: increased
      surprise_polarity: up
      title: U.S. crude oil inventories fell for the seventh consecutive week, refineries
        increased capacity use
    - event_id: a2dbe0286308
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stockpiles
      matched_surprise: draws
      surprise_polarity: down
      title: China draws crude oil stockpiles to offset Middle East supply disruption
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  cushing_stocks:
    valeur: 19614.0
    valeur_normalisee: -0.7089363198780467
    valeur_ponderee: -0.7089363198780467
    ts: '2026-07-09T05:23:35.502017+00:00'
  spread_brent_wti:
    valeur: 4.589728999999991
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.09229964585220773
    valeur_normalisee: -0.03559223187514095
    valeur_ponderee: -0.03559223187514095
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.0727065303811465
    valeur_normalisee: 0.5700655056238484
    valeur_ponderee: 0.5700655056238484
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.09187914778102302
    valeur_normalisee: 0.8287824129502656
    valeur_ponderee: 0.8287824129502656
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-09T05:23:35.502017+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.16999999999999993
    valeur_normalisee: 0.897243485102919
    valeur_ponderee: 0.897243485102919
    ts: '2026-07-09T05:23:35.502017+00:00'
  hy_credit_spread:
    valeur: 2.67
    valeur_normalisee: -0.8210495990837218
    valeur_ponderee: -0.8210495990837218
    ts: '2026-07-09T05:23:35.502017+00:00'
  breadth_sp_ma50:
    valeur: 0.2846793591446375
    valeur_normalisee: 0.32855720079663825
    valeur_ponderee: 0.32855720079663825
    ts: '2026-07-09T05:23:35.502017+00:00'
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.0018345674883949448
    valeur_normalisee: -0.33485043359341865
    valeur_ponderee: -0.33485043359341865
    ts: '2026-07-09T05:23:35.502017+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.64
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-09T05:23:35.502017+00:00'
  rsi_14j_gspc:
    valeur: 52.93866709853423
    ts: '2026-07-09T05:23:35.502017+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.3
    valeur_normalisee: 0.8835232067017706
    valeur_ponderee: 0.8835232067017706
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.008360231393640616
    valeur_normalisee: -0.3972176777001189
    valeur_ponderee: -0.3972176777001189
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.02251063831480038
    valeur_normalisee: 0.19900034166089012
    valeur_ponderee: 0.19900034166089012
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.0008324471320746429
    valeur_normalisee: -0.15628683139295915
    valeur_ponderee: -0.15628683139295915
    ts: '2026-07-09T05:23:35.502017+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-07-09T05:23:35.502017+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-07'
    valeur: -0.17744248658840586
    valeur_normalisee: 0.08872124329420293
    valeur_ponderee: 0.08872124329420293
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 78.73962
    valeur_normalisee: -0.5281242761284288
    valeur_ponderee: -0.5281242761284288
    ts: '2026-07-09T05:23:35.502017+00:00'
  usd_brl_sucre:
    valeur: 5.16174
    valeur_normalisee: 0.40083242778811756
    valeur_ponderee: 0.40083242778811756
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_sugar:
    valeur: -87164.0
    valeur_normalisee: -0.5949213325200434
    valeur_ponderee: -0.5949213325200434
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.03112033195020736
    valeur_normalisee: 0.37207569730256035
    valeur_ponderee: 0.37207569730256035
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.033264033264033266
    valeur_normalisee: 0.3606347449127402
    valeur_ponderee: 0.3606347449127402
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.017400204708290623
    valeur_normalisee: 0.276622947322508
    valeur_ponderee: 0.276622947322508
    ts: '2026-07-09T05:23:35.502017+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 7.433333333333332
      7j: 7.433333333333332
      1m: 7.433333333333332
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  exports_bresil_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 7.433333333333332
      7j: 7.433333333333332
      1m: 7.433333333333332
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-09T05:23:35.502017+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5400000000000005
    valeur_normalisee: 0.7921407018727081
    valeur_ponderee: 0.7921407018727081
    ts: '2026-07-09T05:23:35.502017+00:00'
  dxy_trend_20j:
    valeur: 120.6902
    valeur_normalisee: 0.7954255003641996
    valeur_ponderee: 0.7954255003641996
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.00790713814068611
    valeur_normalisee: 0.5226716038375914
    valeur_ponderee: 0.5226716038375914
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.0018402392273981771
    valeur_normalisee: 0.006322125146644251
    valeur_ponderee: 0.006322125146644251
    ts: '2026-07-09T05:23:35.502017+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.0067145592895927475
    valeur_normalisee: -0.07006552823708612
    valeur_ponderee: -0.07006552823708612
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_jpy_nets:
    valeur: -165445.0
    valeur_normalisee: -0.752937561284528
    valeur_ponderee: -0.752937561284528
    ts: '2026-07-09T05:23:35.502017+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.9
    valeur_normalisee: 0.6140225544157301
    valeur_ponderee: 0.6140225544157301
    ts: '2026-07-09T05:23:35.502017+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-09T05:23:35.502017+00:00'
    nature: structurel
    event_id: c67a818aa26e
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 7.200000000000003
      7j: 7.200000000000003
      1m: 7.200000000000003
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-09T05:23:35.502017+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-09T05:23:35.502017+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-09T05:23:35.502017+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-09T05:23:35.502017+00:00'
  gap_rv_iv:
    valeur: 0.3325370776873733
    ts: '2026-07-09T05:23:35.502017+00:00'
  cftc_cot_vix_nets:
    valeur: -58486.0
    valeur_normalisee: -0.12165161736552672
    valeur_ponderee: -0.12165161736552672
    ts: '2026-07-09T05:23:35.502017+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-09T05:23:35.502017+00:00'
    synthese_rationale: Escalade géopolitique majeure US-Iran avec frappes mutuelles
      et menaces sur le détroit d'Ormuz, toutes les news récentes (8-9 juillet) sont
      LONG et de matérialité élevée, dominant le contexte de baisse du VIX sur 20j
      qui est probablement déjà intégré mais la fraîcheur et l'intensité des événements
      j
    nature: structurel
    event_id: cd06d1a40215
    event_date: '2026-07-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 171.0
      7j: 171.0
      1m: 171.0
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-09T05:23:35.502017+00:00'
```
