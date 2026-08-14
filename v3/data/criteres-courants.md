# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-14T05:22:48.784641+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.6372633155914107
    valeur_ponderee: 0.6372633155914107
    ts: '2026-08-14T05:22:48.784641+00:00'
  mouvement_or_5j:
    valeur: -0.005275061223359523
    valeur_normalisee: -0.13952011479423024
    valeur_ponderee: -0.13952011479423024
    ts: '2026-08-14T05:22:48.784641+00:00'
  ratio_gold_silver:
    valeur: 67.65556758955218
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_silver:
    valeur: 20058.0
    valeur_normalisee: -0.3206731163551768
    valeur_ponderee: -0.3206731163551768
    ts: '2026-08-14T05:22:48.784641+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.0413607878245299
    valeur_normalisee: 0.36717513425245246
    valeur_ponderee: 0.36717513425245246
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_argent:
    valeur: 0.09723957903709213
    valeur_normalisee: 0.8250623369098048
    valeur_ponderee: 0.8250623369098048
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_argent:
    valeur: 0.004348272001142517
    valeur_normalisee: 0.055218023387127
    valeur_ponderee: 0.055218023387127
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_argent:
    valeur: -0.012883158436983733
    valeur_normalisee: -0.13245867617391696
    valeur_ponderee: -0.13245867617391696
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur: 920112000.0
    valeur_normalisee: -0.5367988110081852
    valeur_ponderee: -0.5367988110081852
    ts: '2026-08-14T05:22:48.784641+00:00'
  noaa_drought_midwest_plains:
    valeur: 0.18168016879883958
    valeur_normalisee: 0.09084008439941979
    valeur_ponderee: 0.09084008439941979
    ts: '2026-08-14T05:22:48.784641+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: Attaques récentes sur terminaux russes en mer Noire et frappes
      sur Novorossiysk (12-13 août) dominent, avec matérialité high et fraîcheur ≤48h.
      USDA prévoit baisse de 11% de production des exportateurs, renforçant le biais
      haussier malgré -2.74% sur 20j.
    nature: structurel
    event_id: cd16f8309faf
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 120.40000000000005
      7j: 120.40000000000005
      1m: 120.40000000000005
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -19165.0
    valeur_normalisee: 0.34324298726925345
    valeur_ponderee: 0.34324298726925345
    ts: '2026-08-14T05:22:48.784641+00:00'
  meteo_australie_dryland:
    valeur: -0.03129589983393959
    valeur_normalisee: -0.015647949916969797
    valeur_ponderee: -0.015647949916969797
    ts: '2026-08-14T05:22:48.784641+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_ble:
    valeur: -0.02744209911398532
    valeur_normalisee: -0.36787338612202475
    valeur_ponderee: -0.36787338612202475
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_ble:
    valeur: 0.03470263467548218
    valeur_normalisee: 0.24781604788229636
    valeur_ponderee: 0.24781604788229636
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_ble:
    valeur: 0.04784606106467426
    valeur_normalisee: 0.7617168542938453
    valeur_ponderee: 0.7617168542938453
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-14T05:22:48.784641+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.01777623283571994
    valeur_normalisee: -0.7099107955924036
    valeur_ponderee: -0.7099107955924036
    ts: '2026-08-14T05:22:48.784641+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.0048319327731093376
    valeur_normalisee: -0.22066524253892703
    valeur_ponderee: -0.22066524253892703
    ts: '2026-08-14T05:22:48.784641+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: 'Signaux mitigés : news LONG (PMI, emploi US) contrebalancées
      par SHORT (sécheresse, géopolitique, Fed). Prix +3.25%/20j suggère que le positif
      est déjà intégré, et la fraîcheur des news SHORT (13/08) limite la conviction.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: -324.26666666666665
      7j: -324.26666666666665
      1m: -324.26666666666665
  rsi_14j_fchi:
    valeur: 61.936592150788385
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.03254998395861275
    valeur_normalisee: 0.38881212001846943
    valeur_ponderee: 0.38881212001846943
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.0018542744091433194
    valeur_normalisee: -0.3831598776212238
    valeur_ponderee: -0.3831598776212238
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.00864891601780493
    valeur_normalisee: -0.5538548425265911
    valeur_ponderee: -0.5538548425265911
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-14T05:22:48.784641+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-12'
    valeur: 0.031046256409448445
    valeur_normalisee: 0.015523128204724223
    valeur_ponderee: 0.015523128204724223
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -13320.0
    valeur_normalisee: -0.5520070944399957
    valeur_ponderee: -0.5520070944399957
    ts: '2026-08-14T05:22:48.784641+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: structurel
    event_id: 5ae5acf78f87
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 119.89999999999996
      7j: 119.89999999999996
      1m: 119.89999999999996
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
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: 'Les news LONG dominent, notamment les menaces El Niño et
      les récoltes (matérialité high, répétées), malgré quelques signaux SHORT récents
      sur l''amélioration de l''offre. Le prix a déjà monté de +7.30% sur 20j, ce
      qui suggère que l''info est partiellement pricée, mais la fraîcheur des news
      LONG (10-13 '
    nature: structurel
    event_id: 5ae5acf78f87
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 121.99999999999986
      7j: 121.99999999999986
      1m: 121.99999999999986
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.07295595669212762
    valeur_normalisee: -0.19553355335987804
    valeur_ponderee: -0.19553355335987804
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.0008063668382053413
    valeur_normalisee: -0.26441212729107677
    valeur_ponderee: -0.26441212729107677
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.03427701408152717
    valeur_normalisee: 0.10558591504131402
    valeur_ponderee: 0.10558591504131402
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.40754739096499126
    valeur_normalisee: 0.20377369548249563
    valeur_ponderee: 0.20377369548249563
    ts: '2026-08-14T05:22:48.784641+00:00'
  usd_brl:
    valeur: 5.19397
    valeur_normalisee: 0.7723077833791
    valeur_ponderee: 0.7723077833791
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_coffee:
    valeur: 26014.0
    valeur_normalisee: -0.19165598000827952
    valeur_ponderee: -0.19165598000827952
    ts: '2026-08-14T05:22:48.784641+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: 'Signaux mitigés : El Niño (LONG) et récolte brésilienne en
      accélération (SHORT) se compensent, avec des news récentes mixtes. Le prix a
      baissé de 0.43% sur 20j, suggérant que le marché a déjà intégré ces informations.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 225.20000000000024
      7j: 225.20000000000024
      1m: 225.20000000000024
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-14T05:22:48.784641+00:00'
  meteo_vietnam_robusta:
    valeur: 0.37634245498084634
    valeur_normalisee: 0.18817122749042317
    valeur_ponderee: 0.18817122749042317
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.004312334736708778
    valeur_normalisee: -0.4316556175564462
    valeur_ponderee: -0.4316556175564462
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.0028475439236161915
    valeur_normalisee: -0.2528414432004729
    valeur_ponderee: -0.2528414432004729
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_cafe:
    valeur: -7.299738485189167e-05
    valeur_normalisee: -0.13048939116218017
    valeur_ponderee: -0.13048939116218017
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.12407292877279504
    valeur_normalisee: 0.06203646438639752
    valeur_ponderee: 0.06203646438639752
    ts: '2026-08-14T05:22:48.784641+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.803061324177372
    valeur_normalisee: 0.401530662088686
    valeur_ponderee: 0.401530662088686
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_cotton:
    valeur: 102492.0
    valeur_normalisee: 0.7964676176052232
    valeur_ponderee: 0.7964676176052232
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_coton:
    valeur: 0.05213849287169037
    valeur_normalisee: 0.5160921582075657
    valeur_ponderee: 0.5160921582075657
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_coton:
    valeur: 0.021554281194384073
    valeur_normalisee: 0.30339657813897764
    valeur_ponderee: 0.30339657813897764
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_coton:
    valeur: -0.010344827586206806
    valeur_normalisee: -0.18593614345457837
    valeur_ponderee: -0.18593614345457837
    ts: '2026-08-14T05:22:48.784641+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 66.90000000000012
      7j: 66.90000000000012
      1m: 66.90000000000012
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: Les nouvelles récentes montrent un biais haussier dominant,
      avec des signaux forts comme les importations chinoises record et la demande
      IA, malgré des nouvelles récurrentes sur l'offre chilienne. Le prix a déjà monté
      de 3.88% sur 20j, mais la fraîcheur des nouvelles et la matérialité élevée de
      cert
    nature: structurel
    event_id: 33d84a40551b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 39.03333333333334
      7j: 39.03333333333334
      1m: 39.03333333333334
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_copper_nets:
    valeur: 77422.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-14T05:22:48.784641+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: structurel
    event_id: 33d84a40551b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 55.20000000000002
      7j: 55.20000000000002
      1m: 55.20000000000002
  ratio_cuivre_or:
    valeur: 0.0015160971445603493
    valeur_normalisee: -0.22193985387373583
    valeur_ponderee: -0.22193985387373583
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.03882310762533869
    valeur_normalisee: 0.4194874396950661
    valeur_ponderee: 0.4194874396950661
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.0019173818744921967
    valeur_normalisee: -0.1275524773385937
    valeur_ponderee: -0.1275524773385937
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.00966073986023086
    valeur_normalisee: -0.2801632472183577
    valeur_ponderee: -0.2801632472183577
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4994925350000003
    valeur_normalisee: -0.2901501276575075
    valeur_ponderee: -0.2901501276575075
    ts: '2026-08-14T05:22:48.784641+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7099999999999995
    valeur_normalisee: 0.6767252866284205
    valeur_ponderee: 0.6767252866284205
    ts: '2026-08-14T05:22:48.784641+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.32423
    valeur_normalisee: -0.4795202172347653
    valeur_ponderee: -0.4795202172347653
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_eur_nets:
    valeur: -78631.0
    valeur_normalisee: -0.9272135456966083
    valeur_ponderee: -0.9272135456966083
    ts: '2026-08-14T05:22:48.784641+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.014576849360834032
    valeur_normalisee: 0.8201404725118258
    valeur_ponderee: 0.8201404725118258
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.0016955604000139513
    valeur_normalisee: -0.110675210600644
    valeur_ponderee: -0.110675210600644
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0002772194885301005
    valeur_normalisee: -0.01220928853770569
    valeur_ponderee: -0.01220928853770569
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.6372633155914107
    valeur_ponderee: 0.6372633155914107
    ts: '2026-08-14T05:22:48.784641+00:00'
  sox_trend_5j:
    valeur: 550.73999
    valeur_normalisee: -0.1368467092235197
    valeur_ponderee: -0.1368467092235197
    ts: '2026-08-14T05:22:48.784641+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17032524049301748
    valeur_normalisee: 0.6581985146082514
    valeur_ponderee: 0.6581985146082514
    ts: '2026-08-14T05:22:48.784641+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: Dominance de nouvelles positives sur l'IA et la tech (Nvidia,
      SK Hynix, CoreWeave) et inflation US modérée, malgré quelques signaux négatifs
      (tensions Iran, carry trade). Le prix a déjà monté de 3.7% sur 20j, mais la
      fraîcheur et la matérialité des nouvelles soutiennent encore le biais haussier.
    nature: ponctuel
    event_id: c8f1e8b0443c
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 79.3666666666667
      7j: 79.3666666666667
      1m: 79.3666666666667
  flux_etf_qqq_5j:
    valeur: 0.024375549587195122
    valeur_normalisee: 0.33005255200043593
    valeur_ponderee: 0.33005255200043593
    ts: '2026-08-14T05:22:48.784641+00:00'
  spread_nasdaq_russell2000:
    valeur: 428.57000700000003
    valeur_normalisee: 0.18275747605509218
    valeur_ponderee: 0.18275747605509218
    ts: '2026-08-14T05:22:48.784641+00:00'
  rsi_14j_ixic:
    valeur: 58.98875641611183
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.03701448706688959
    valeur_normalisee: 0.2581762208659379
    valeur_ponderee: 0.2581762208659379
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.011355981525343228
    valeur_normalisee: 0.13461238431803915
    valeur_ponderee: 0.13461238431803915
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.015536791654528592
    valeur_normalisee: 0.28118549252294617
    valeur_ponderee: 0.28118549252294617
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.6372633155914107
    valeur_ponderee: 0.6372633155914107
    ts: '2026-08-14T05:22:48.784641+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_nets:
    valeur: 190648.0
    valeur_normalisee: -0.0635299654081457
    valeur_ponderee: -0.0635299654081457
    ts: '2026-08-14T05:22:48.784641+00:00'
  flux_etf_or_5j:
    valeur: 0.023840633771123443
    valeur_normalisee: 0.42931527645964385
    valeur_ponderee: 0.42931527645964385
    ts: '2026-08-14T05:22:48.784641+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: Dominance de news géopolitiques LONG (blocus Ormuz, attaques
      navires, sanctions US) avec matérialité high et fraîcheur immédiate, malgré
      quelques news SHORT dispersées. Le prix +6.48%/20j confirme le biais haussier,
      et les news récentes renforcent le scénario de tensions prolongées.
    nature: verbal
    event_id: 66fa1ba401c6
    event_date: '2026-08-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 357.4999999999987
      7j: 357.4999999999987
      1m: 357.4999999999987
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-14T05:22:48.784641+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_or:
    valeur: 0.06490859413980732
    valeur_normalisee: 0.8282538846392618
    valeur_ponderee: 0.8282538846392618
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_or:
    valeur: -0.005377428272803186
    valeur_normalisee: -0.1567904944167053
    valeur_ponderee: -0.1567904944167053
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_or:
    valeur: -0.01108928299829448
    valeur_normalisee: -0.2964941731048409
    valeur_ponderee: -0.2964941731048409
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
petrole:
  eia_crude_surprise:
    valeur: 424410.0
    valeur_normalisee: -0.13812033584105132
    valeur_ponderee: -0.13812033584105132
    ts: '2026-08-14T05:22:48.784641+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: Menaces de sanctions et blocus du détroit d'Ormuz, avec attaques
      de navires et trafic au plus bas, dominent nettement malgré des prévisions de
      demande réduites. Le prix a rebondi de +5.49% sur 5j, confirmant le biais haussier.
    nature: verbal
    event_id: 66fa1ba401c6
    event_date: '2026-08-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 336.7666666666651
      7j: 336.7666666666651
      1m: 336.7666666666651
  cftc_cot_crude_nets:
    valeur: 26587.0
    valeur_normalisee: 0.013076899911430795
    valeur_ponderee: 0.013076899911430795
    ts: '2026-08-14T05:22:48.784641+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: verbal
    event_id: 66fa1ba401c6
    event_date: '2026-08-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 307.19999999999783
      7j: 307.19999999999783
      1m: 307.19999999999783
    sign_conflict: true
    sign_conflict_details:
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
    - event_id: c4566eff9e81
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de petrole
      matched_surprise: baisse
      surprise_polarity: down
      title: Pétrole en baisse après avoir bondi de 8% suite à des hostilités iraniennes
        et une baisse des stocks
    - event_id: 8aa5c20f7194
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: draw
      surprise_polarity: down
      title: La Chine a puisé 41 millions de barils dans ses stocks de brut en juin,
        réduisant la pression sur l'offre mondiale pendant le conflit iranien.
    - event_id: 46c8cbf2b438
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: draw
      surprise_polarity: down
      title: La Chine a puisé 41 millions de barils dans ses stocks de brut en juin,
        l'un des plus gros prélèvements mensuels jamais enregistrés, selon l'AIE.
    - event_id: a802379cbc43
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: stocks petroliers
      matched_surprise: hausse
      surprise_polarity: up
      title: Disparition des buffers pétroliers mondiaux (faibles stocks, détroit
        d'Ormuz perturbé, excédents réduits) augmentant le risque de hausse des prix
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  cushing_stocks:
    valeur: 22566.0
    valeur_normalisee: -0.15882864718542616
    valeur_ponderee: -0.15882864718542616
    ts: '2026-08-14T05:22:48.784641+00:00'
  spread_brent_wti:
    valeur: 4.605949999999993
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.024581915412171806
    valeur_normalisee: 0.08840347364850339
    valeur_ponderee: 0.08840347364850339
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.08953400504257303
    valeur_normalisee: 0.5540539782385991
    valeur_ponderee: 0.5540539782385991
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.021444341228111452
    valeur_normalisee: -0.11800784117448385
    valeur_ponderee: -0.11800784117448385
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-14T05:22:48.784641+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.04999999999999982
    valeur_normalisee: 0.18945060867161656
    valeur_ponderee: 0.18945060867161656
    ts: '2026-08-14T05:22:48.784641+00:00'
  hy_credit_spread:
    valeur: 2.71
    valeur_normalisee: -0.24500879635002007
    valeur_ponderee: -0.24500879635002007
    ts: '2026-08-14T05:22:48.784641+00:00'
  breadth_sp_ma50:
    valeur: 0.2863295109785571
    valeur_normalisee: 0.2617152115352926
    valeur_ponderee: 0.2617152115352926
    ts: '2026-08-14T05:22:48.784641+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.012126574372853138
    valeur_normalisee: 0.2130899017556278
    valeur_ponderee: 0.2130899017556278
    ts: '2026-08-14T05:22:48.784641+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.65
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-14T05:22:48.784641+00:00'
  rsi_14j_gspc:
    valeur: 66.17974265856284
    ts: '2026-08-14T05:22:48.784641+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.42
    valeur_normalisee: 0.6372633155914107
    valeur_ponderee: 0.6372633155914107
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.036178643282927414
    valeur_normalisee: 0.4805482518648253
    valeur_ponderee: 0.4805482518648253
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.008491799657946775
    valeur_normalisee: 0.08250357237935209
    valeur_ponderee: 0.08250357237935209
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.006273974901432888
    valeur_normalisee: 0.14139943816099526
    valeur_ponderee: 0.14139943816099526
    ts: '2026-08-14T05:22:48.784641+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-14T05:22:48.784641+00:00'
    reporte: true
    reporte_age_j: 4
    reporte_date: '2026-08-10'
    valeur: -0.1786140319430498
    valeur_normalisee: 0.0893070159715249
    valeur_ponderee: 0.0893070159715249
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 85.94716
    valeur_normalisee: 0.10347402086759773
    valeur_ponderee: 0.10347402086759773
    ts: '2026-08-14T05:22:48.784641+00:00'
  usd_brl_sucre:
    valeur: 5.19397
    valeur_normalisee: 0.7723077833791
    valeur_ponderee: 0.7723077833791
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_sugar:
    valeur: -54728.0
    valeur_normalisee: -0.4516842533419668
    valeur_ponderee: -0.4516842533419668
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.13746065057712498
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.09384460141271433
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.013084112149532867
    valeur_normalisee: 0.1723608040249252
    valeur_ponderee: 0.1723608040249252
    ts: '2026-08-14T05:22:48.784641+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 53.56666666666667
      7j: 53.56666666666667
      1m: 53.56666666666667
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
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 53.56666666666667
      7j: 53.56666666666667
      1m: 53.56666666666667
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-14T05:22:48.784641+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5300000000000002
    valeur_normalisee: 0.2347199393846966
    valeur_ponderee: 0.2347199393846966
    ts: '2026-08-14T05:22:48.784641+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.009691602987255576
    valeur_normalisee: 0.39032134996812523
    valeur_ponderee: 0.39032134996812523
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.00013220127361424083
    valeur_normalisee: 0.020405831950329766
    valeur_ponderee: 0.020405831950329766
    ts: '2026-08-14T05:22:48.784641+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.027644196146306532
    valeur_normalisee: -0.8378123785918896
    valeur_ponderee: -0.8378123785918896
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_jpy_nets:
    valeur: -46951.0
    valeur_normalisee: -0.009726152296552546
    valeur_ponderee: -0.009726152296552546
    ts: '2026-08-14T05:22:48.784641+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.01
    valeur_normalisee: 0.6421683810527447
    valeur_ponderee: 0.6421683810527447
    ts: '2026-08-14T05:22:48.784641+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-14T05:22:48.784641+00:00'
    nature: ponctuel
    event_id: 267712266c81
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 5.100000000000002
      7j: 5.100000000000002
      1m: 5.100000000000002
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-14T05:22:48.784641+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-14T05:22:48.784641+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-14T05:22:48.784641+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-14T05:22:48.784641+00:00'
  gap_rv_iv:
    valeur: -1.3325365244295053
    ts: '2026-08-14T05:22:48.784641+00:00'
  cftc_cot_vix_nets:
    valeur: -61109.0
    valeur_normalisee: -0.17603530735988018
    valeur_ponderee: -0.17603530735988018
    ts: '2026-08-14T05:22:48.784641+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-14T05:22:48.784641+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîches (blocus
      Ormuz, attaques navires, escalade US-Iran) malgré le repli récent du VIX, signal
      directionnel net. Le marché n'a pas encore intégré pleinement ces risques géopolitiques.
    nature: verbal
    event_id: 66fa1ba401c6
    event_date: '2026-08-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 373.63333333333185
      7j: 373.63333333333185
      1m: 373.63333333333185
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-14T05:22:48.784641+00:00'
```
