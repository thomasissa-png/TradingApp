# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-09-01T05:22:16.765894+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.5167003188142474
    valeur_ponderee: 0.5167003188142474
    ts: '2026-09-01T05:22:16.765894+00:00'
  mouvement_or_5j:
    valeur: -0.0379826431954412
    valeur_normalisee: -0.8276521594259978
    valeur_ponderee: -0.8276521594259978
    ts: '2026-09-01T05:22:16.765894+00:00'
  ratio_gold_silver:
    valeur: 66.7596551226597
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_silver:
    valeur: 23255.0
    valeur_normalisee: -0.2251627248122002
    valeur_ponderee: -0.2251627248122002
    ts: '2026-09-01T05:22:16.765894+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.033279742765273346
    valeur_normalisee: -0.20954600238028853
    valeur_ponderee: -0.20954600238028853
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_argent:
    valeur: 0.014962712228653308
    valeur_normalisee: -0.05982416305690977
    valeur_ponderee: -0.05982416305690977
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_argent:
    valeur: -0.03409902012367749
    valeur_normalisee: -0.5007618159535352
    valeur_ponderee: -0.5007618159535352
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_argent:
    valeur: -0.0011145994755551447
    valeur_normalisee: -0.0942442034743625
    valeur_ponderee: -0.0942442034743625
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.033080090357248126
    valeur_normalisee: 0.016540045178624063
    valeur_ponderee: 0.016540045178624063
    ts: '2026-09-01T05:22:16.765894+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (frappes
      russes, problèmes d'exportation mer Noire, hausse des prix à plus hauts de 3
      ans) cohérente avec le prix +15.7%/20j. Aucune news SHORT significative ne contrebalance.
    nature: structurel
    event_id: 813be5de8bfe
    event_date: '2026-08-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 174.06666666666652
      7j: 174.06666666666652
      1m: 174.06666666666652
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -11740.0
    valeur_normalisee: 0.4475969488007501
    valeur_ponderee: 0.4475969488007501
    ts: '2026-09-01T05:22:16.765894+00:00'
  meteo_australie_dryland:
    valeur: -0.11999695298570341
    valeur_normalisee: -0.059998476492851706
    valeur_ponderee: -0.059998476492851706
    ts: '2026-09-01T05:22:16.765894+00:00'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_ble:
    valeur: 0.15628480088359198
    valeur_normalisee: 0.5437588457323078
    valeur_ponderee: 0.5437588457323078
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_ble:
    valeur: 0.09927182229849918
    valeur_normalisee: 0.6830035974983095
    valeur_ponderee: 0.6830035974983095
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_ble:
    valeur: -0.014302231929434694
    valeur_normalisee: -0.4147067529467704
    valeur_ponderee: -0.4147067529467704
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-09-01T05:22:16.765894+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.018708971230577465
    valeur_normalisee: -0.6134093988720841
    valeur_ponderee: -0.6134093988720841
    ts: '2026-09-01T05:22:16.765894+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.023008095440988474
    valeur_normalisee: -0.7036518532837641
    valeur_ponderee: -0.7036518532837641
    ts: '2026-09-01T05:22:16.765894+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (coûts d'emprunt
      français, guerre commerciale US-Canada, tensions Moyen-Orient, blocage gaz qatari)
      et cohérentes avec la baisse récente du CAC40. La seule news LONG (PMI chinois)
      est faible et isolée.
    nature: structurel
    event_id: 9e729fce990b
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -219.99999999999963
      7j: -219.99999999999963
      1m: -219.99999999999963
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  rsi_14j_fchi:
    valeur: 38.350775118452944
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_cac40:
    valeur: -0.0324269952178744
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.014029171130148899
    valeur_normalisee: -0.48453517003910995
    valeur_ponderee: -0.48453517003910995
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.015112711100463083
    valeur_normalisee: -0.6648904309914861
    valeur_ponderee: -0.6648904309914861
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.04367855770917875
    valeur_normalisee: 0.021839278854589375
    valeur_ponderee: 0.021839278854589375
    ts: '2026-09-01T05:22:16.765894+00:00'
  hf_positioning_flux_options:
    valeur: -18386.0
    valeur_normalisee: -0.6253210381718236
    valeur_ponderee: -0.6253210381718236
    ts: '2026-09-01T05:22:16.765894+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: structurel
    event_id: aa90a870f402
    event_date: '2026-08-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 161.53333333333316
      7j: 161.53333333333316
      1m: 161.53333333333316
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  maladies_cabosses:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Les news récentes (28-31 août) sont majoritairement LONG avec
      matérialité high (risques de récolte en Afrique de l'Ouest, prix de ferme réduit
      en Côte d'Ivoire) et le prix a déjà monté de +18% sur 20j, confirmant le biais
      haussier. Les news SHORT plus anciennes (21-26 août) sont moins fraîches et
      de
    nature: structurel
    event_id: aa90a870f402
    event_date: '2026-08-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 166.09999999999982
      7j: 166.09999999999982
      1m: 166.09999999999982
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.18321799198713018
    valeur_normalisee: 0.27072312283040934
    valeur_ponderee: 0.27072312283040934
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.1579348961002356
    valeur_normalisee: 0.6951031097329372
    valeur_ponderee: 0.6951031097329372
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.020681248817525866
    valeur_normalisee: 0.03833780109060404
    valeur_ponderee: 0.03833780109060404
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
cafe:
  meteo_bresil_minas_gerais:
    ts: '2026-09-01T05:22:16.765894+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-31'
    valeur: -0.3774764309805664
    valeur_normalisee: 0.1887382154902832
    valeur_ponderee: 0.1887382154902832
    reporte_cause: source réseau indisponible
  usd_brl:
    valeur: 5.18337
    valeur_normalisee: 0.548258555764715
    valeur_ponderee: 0.548258555764715
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_coffee:
    valeur: 30746.0
    valeur_normalisee: -0.09318554391505972
    valeur_ponderee: -0.09318554391505972
    ts: '2026-09-01T05:22:16.765894+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: 'Signaux mitigés : news LONG récentes (stocks ICE en baisse,
      El Niño) contrebalancées par des news SHORT (baisse des prix, surproduction
      Robusta). Le prix a baissé de 1.81% sur 20j, suggérant que le marché a déjà
      intégré les facteurs baissiers, et les news LONG récentes ne sont pas assez
      fortes pour '
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 236.86666666666673
      7j: 236.86666666666673
      1m: 236.86666666666673
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-09-01T05:22:16.765894+00:00'
  meteo_vietnam_robusta:
    valeur: 0.5555521185531158
    valeur_normalisee: 0.2777760592765579
    valeur_ponderee: 0.2777760592765579
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.01766045900931912
    valeur_normalisee: -0.3706761429257497
    valeur_ponderee: -0.3706761429257497
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.0697375072533829
    valeur_normalisee: -0.6617487631486237
    valeur_ponderee: -0.6617487631486237
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.0029897944203560733
    valeur_normalisee: -0.0625301081295879
    valeur_ponderee: -0.0625301081295879
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: -0.01915887482309612
    valeur_normalisee: 0.00957943741154806
    valeur_ponderee: 0.00957943741154806
    ts: '2026-09-01T05:22:16.765894+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.7938263436272224
    valeur_normalisee: 0.3969131718136112
    valeur_ponderee: 0.3969131718136112
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_cotton:
    valeur: 127183.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_coton:
    valeur: 0.13076311605723379
    valeur_normalisee: 0.8074429907178463
    valeur_ponderee: 0.8074429907178463
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_coton:
    valeur: 0.043270993766043375
    valeur_normalisee: 0.4288992427189524
    valeur_ponderee: 0.4288992427189524
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_coton:
    valeur: 0.040219378427788
    valeur_normalisee: 0.7219050744395582
    valeur_ponderee: 0.7219050744395582
    ts: '2026-09-01T05:22:16.765894+00:00'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: structurel
    event_id: 2374791f65df
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 102.56666666666692
      7j: 102.56666666666692
      1m: 102.56666666666692
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Les nouvelles récentes (PMI chinois et sud-coréen en hausse,
      tarifs US-Canada, demande électrique) dominent les signaux short plus anciens
      (offre chilienne, contraction PMI). Le prix est en légère hausse, cohérent avec
      un biais long modéré.
    nature: structurel
    event_id: 025c6f115260
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 58.06666666666672
      7j: 58.06666666666672
      1m: 58.06666666666672
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_copper_nets:
    valeur: 84321.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-09-01T05:22:16.765894+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: ponctuel
    event_id: 61d32360b04b
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 62.96666666666659
      7j: 62.96666666666659
      1m: 62.96666666666659
  ratio_cuivre_or:
    valeur: 0.0014957742615092362
    valeur_normalisee: -0.2113576896814708
    valeur_ponderee: -0.2113576896814708
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.00556741799979954
    valeur_normalisee: -0.21633757165781017
    valeur_ponderee: -0.21633757165781017
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.01272156881456199
    valeur_normalisee: -0.5800749643789163
    valeur_ponderee: -0.5800749643789163
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.011976084511175156
    valeur_normalisee: 0.25245928692274694
    valeur_ponderee: 0.25245928692274694
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5346215697
    valeur_normalisee: -0.017394369061321625
    valeur_ponderee: -0.017394369061321625
    ts: '2026-09-01T05:22:16.765894+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7600000000000002
    valeur_normalisee: 0.6970191910477733
    valeur_ponderee: 0.6970191910477733
    ts: '2026-09-01T05:22:16.765894+00:00'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.88253
    valeur_normalisee: -0.15500250398776763
    valeur_ponderee: -0.15500250398776763
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_eur_nets:
    valeur: -53872.0
    valeur_normalisee: -0.7461352509219135
    valeur_ponderee: -0.7461352509219135
    ts: '2026-09-01T05:22:16.765894+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.007115152672086955
    valeur_normalisee: 0.1298190410100676
    valeur_ponderee: 0.1298190410100676
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.005824560802418888
    valeur_normalisee: -0.6518094511108637
    valeur_ponderee: -0.6518094511108637
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.001994198694706295
    valeur_normalisee: 0.14301555210221947
    valeur_ponderee: 0.14301555210221947
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.5167003188142474
    valeur_ponderee: 0.5167003188142474
    ts: '2026-09-01T05:22:16.765894+00:00'
  sox_trend_5j:
    valeur: 511.040009
    valeur_normalisee: -0.5332811690413203
    valeur_ponderee: -0.5332811690413203
    ts: '2026-09-01T05:22:16.765894+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17012667880285343
    valeur_normalisee: 0.3714239886972414
    valeur_ponderee: 0.3714239886972414
    ts: '2026-09-01T05:22:16.765894+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG sur IA (Nvidia, data
      centers) contre SHORT hawkish Fed et escalade Moyen-Orient. Prix +2.38%/20j
      suggère que le positif IA est déjà pricé, et les risques géopolitiques/taux
      dominent sans direction claire.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 183.9999999999999
      7j: 183.9999999999999
      1m: 183.9999999999999
  flux_etf_qqq_5j:
    valeur: 0.014780835672487891
    valeur_normalisee: 0.2457004533782938
    valeur_ponderee: 0.2457004533782938
    ts: '2026-09-01T05:22:16.765894+00:00'
  spread_nasdaq_russell2000:
    valeur: 422.83002
    valeur_normalisee: 0.205323004063738
    valeur_ponderee: 0.205323004063738
    ts: '2026-09-01T05:22:16.765894+00:00'
  rsi_14j_ixic:
    valeur: 51.177096787071854
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.0238404771424523
    valeur_normalisee: 0.34526925201787617
    valeur_ponderee: 0.34526925201787617
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.008200554318998465
    valeur_normalisee: 0.18398179638136444
    valeur_ponderee: 0.18398179638136444
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.007576943081659238
    valeur_normalisee: 0.1798452192325235
    valeur_ponderee: 0.1798452192325235
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.5167003188142474
    valeur_ponderee: 0.5167003188142474
    ts: '2026-09-01T05:22:16.765894+00:00'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_nets:
    valeur: 242212.0
    valeur_normalisee: 0.38662879828456004
    valeur_ponderee: 0.38662879828456004
    ts: '2026-09-01T05:22:16.765894+00:00'
  flux_etf_or_5j:
    valeur: -0.04281794745599854
    valeur_normalisee: -0.6236524878141191
    valeur_ponderee: -0.6236524878141191
    ts: '2026-09-01T05:22:16.765894+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Escalade majeure au Moyen-Orient (frappes US sur l'Iran, menaces
      sur Hormuz) domine, avec matérialité high et fraîcheur immédiate, malgré des
      signaux hawkish Fed. Le prix récent (-3.8% sur 5j) est contredit, mais la news
      du jour (attaque sur Hormuz) change le régime.
    nature: structurel
    event_id: e701c2150f84
    event_date: '2026-09-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 570.3333333333318
      7j: 570.3333333333318
      1m: 570.3333333333318
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-09-01T05:22:16.765894+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_or:
    valeur: 0.004012197627663694
    valeur_normalisee: -0.23929096527632987
    valeur_ponderee: -0.23929096527632987
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_or:
    valeur: -0.04977847030646598
    valeur_normalisee: -0.9551516776292021
    valeur_ponderee: -0.9551516776292021
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_or:
    valeur: -0.007208835854893181
    valeur_normalisee: -0.2718676856383344
    valeur_ponderee: -0.2718676856383344
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-09-01T05:22:16.765894+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-28'
    valeur: 428910.0
    valeur_normalisee: -0.010699044988311703
    valeur_ponderee: -0.010699044988311703
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Escalade militaire US-Iran avec frappes sur Larak et menace
      sur Kharg Island, risque de perturbation du détroit d'Ormuz, dominent largement
      malgré quelques news SHORT (accord Trump-Venezuela, PMI chinois faible). Le
      prix a déjà monté de +15.84% sur 20j, mais les news fraîches (≤48h) à matérialité
      hi
    nature: structurel
    event_id: e701c2150f84
    event_date: '2026-09-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 531.3333333333308
      7j: 531.3333333333308
      1m: 531.3333333333308
  cftc_cot_crude_nets:
    valeur: 17068.0
    valeur_normalisee: -0.1877382283014539
    valeur_ponderee: -0.1877382283014539
    ts: '2026-09-01T05:22:16.765894+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: structurel
    event_id: e701c2150f84
    event_date: '2026-09-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 497.36666666666383
      7j: 497.36666666666383
      1m: 497.36666666666383
    sign_conflict: true
    sign_conflict_details:
    - event_id: cf4a9dfc777b
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: hausse
      surprise_polarity: up
      title: Hausse des stocks de pétrole brut inférieure aux attentes
    - event_id: 01ee9ad8d686
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: stocks de brut
      matched_surprise: hausse
      surprise_polarity: up
      title: Les EAU suspendent leurs liens économiques avec l'Iran, tensions militaires,
        hausse des stocks de brut US
    - event_id: c891330a80ef
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de petrole
      matched_surprise: chute
      surprise_polarity: down
      title: Accord de navigation Iran-Oman sur Hormuz et rebond des stocks US, le
        pétrole chute
    - event_id: fef734e1aa7e
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: 'Inventaires pétroliers US: brut +2,5M barils, produits en baisse'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  cushing_stocks:
    valeur: 22428.0
    valeur_normalisee: -0.18311536903012807
    valeur_ponderee: -0.18311536903012807
    ts: '2026-09-01T05:22:16.765894+00:00'
  spread_brent_wti:
    valeur: 3.9031999999999982
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.15836280938375813
    valeur_normalisee: 0.5637947159801595
    valeur_ponderee: 0.5637947159801595
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.016637099584537962
    valeur_normalisee: -0.07075740637658445
    valeur_ponderee: -0.07075740637658445
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.027691010259026427
    valeur_normalisee: 0.22339588614672684
    valeur_ponderee: 0.22339588614672684
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-09-01T05:22:16.765894+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.009999999999999787
    valeur_normalisee: -0.20748901492957164
    valeur_ponderee: -0.20748901492957164
    ts: '2026-09-01T05:22:16.765894+00:00'
  hy_credit_spread:
    valeur: 2.6
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-09-01T05:22:16.765894+00:00'
  breadth_sp_ma50:
    valeur: 0.28601786510946403
    valeur_normalisee: -0.0388019039511548
    valeur_ponderee: -0.0388019039511548
    ts: '2026-09-01T05:22:16.765894+00:00'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.004689140556504157
    valeur_normalisee: 0.07099586474888385
    valeur_ponderee: 0.07099586474888385
    ts: '2026-09-01T05:22:16.765894+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.04
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-09-01T05:22:16.765894+00:00'
  rsi_14j_gspc:
    valeur: 53.980446760805556
    ts: '2026-09-01T05:22:16.765894+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.5167003188142474
    valeur_ponderee: 0.5167003188142474
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.012380070806025545
    valeur_normalisee: 0.04243639147647292
    valeur_ponderee: 0.04243639147647292
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.005835310931951554
    valeur_normalisee: 0.09736582429553935
    valeur_ponderee: 0.09736582429553935
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.0012661484159297576
    valeur_normalisee: 0.012895603335832732
    valeur_ponderee: 0.012895603335832732
    ts: '2026-09-01T05:22:16.765894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-09-01T05:22:16.765894+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-31'
    valeur: -0.3965019427682916
    valeur_normalisee: 0.1982509713841458
    valeur_ponderee: 0.1982509713841458
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 90.83507
    valeur_normalisee: 0.5631809665373052
    valeur_ponderee: 0.5631809665373052
    ts: '2026-09-01T05:22:16.765894+00:00'
  usd_brl_sucre:
    valeur: 5.18337
    valeur_normalisee: 0.548258555764715
    valeur_ponderee: 0.548258555764715
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_sugar:
    valeur: 180943.0
    valeur_normalisee: 0.4810257086697616
    valeur_ponderee: 0.4810257086697616
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.15040650406504064
    valeur_normalisee: 0.7510384652689408
    valeur_ponderee: 0.7510384652689408
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.011617515638963516
    valeur_normalisee: -0.08847410626180396
    valeur_ponderee: -0.08847410626180396
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.00801424755120217
    valeur_normalisee: 0.0003896948455795316
    valeur_ponderee: 0.0003896948455795316
    ts: '2026-09-01T05:22:16.765894+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: structurel
    event_id: 37c6aee4d0b2
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 76.10000000000014
      7j: 76.10000000000014
      1m: 76.10000000000014
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
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: structurel
    event_id: 37c6aee4d0b2
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 76.10000000000014
      7j: 76.10000000000014
      1m: 76.10000000000014
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-09-01T05:22:16.765894+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.67
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-09-01T05:22:16.765894+00:00'
  dxy_trend_20j:
    valeur: 118.7479
    valeur_normalisee: -0.6371210138643244
    valeur_ponderee: -0.6371210138643244
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.004260536856661723
    valeur_normalisee: 0.2090588282143182
    valeur_ponderee: 0.2090588282143182
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.0013170393385396606
    valeur_normalisee: -0.045186999034174995
    valeur_ponderee: -0.045186999034174995
    ts: '2026-09-01T05:22:16.765894+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.002879731325432733
    valeur_normalisee: 0.2137447609350419
    valeur_ponderee: 0.2137447609350419
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_jpy_nets:
    valeur: -62792.0
    valeur_normalisee: -0.11127193802612544
    valeur_ponderee: -0.11127193802612544
    ts: '2026-09-01T05:22:16.765894+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0600000000000005
    valeur_normalisee: 0.6970191910477733
    valeur_ponderee: 0.6970191910477733
    ts: '2026-09-01T05:22:16.765894+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-09-01T05:22:16.765894+00:00'
    nature: structurel
    event_id: 2a2c3c4c07a3
    event_date: '2026-09-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -1.8999999999999542
      7j: -1.8999999999999542
      1m: -1.8999999999999542
  gate_regime_extreme:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-09-01T05:22:16.765894+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-09-01T05:22:16.765894+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-09-01T05:22:16.765894+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-09-01T05:22:16.765894+00:00'
  gap_rv_iv:
    valeur: -5.790943105161714
    ts: '2026-09-01T05:22:16.765894+00:00'
  cftc_cot_vix_nets:
    valeur: -78164.0
    valeur_normalisee: -0.5083978702949855
    valeur_ponderee: -0.5083978702949855
    ts: '2026-09-01T05:22:16.765894+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-09-01T05:22:16.765894+00:00'
    synthese_rationale: Escalade majeure Iran/États-Unis avec frappes sur Larak et
      menaces sur Kharg Island, risque de perturbation d'Ormuz, toutes les news récentes
      sont LONG et à matérialité élevée. Malgré la baisse récente du VIX, la fraîcheur
      et la cohérence des signaux dominent.
    nature: structurel
    event_id: e701c2150f84
    event_date: '2026-09-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 551.8999999999972
      7j: 551.8999999999972
      1m: 551.8999999999972
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-09-01T05:22:16.765894+00:00'
```
