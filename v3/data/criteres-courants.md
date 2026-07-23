# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-23T05:22:52.322669+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.37
    valeur_normalisee: 0.8277699459470258
    valeur_ponderee: 0.8277699459470258
    ts: '2026-07-23T05:22:52.322669+00:00'
  mouvement_or_5j:
    valeur: 0.027861732057003596
    valeur_normalisee: 0.7903132982217176
    valeur_ponderee: 0.7903132982217176
    ts: '2026-07-23T05:22:52.322669+00:00'
  ratio_gold_silver:
    valeur: 69.13183534743835
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_silver:
    valeur: 22604.0
    valeur_normalisee: -0.24337735975094785
    valeur_ponderee: -0.24337735975094785
    ts: '2026-07-23T05:22:52.322669+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.03275234629381352
    valeur_normalisee: 0.3711650179389241
    valeur_ponderee: 0.3711650179389241
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_argent:
    valeur: -0.043784912785686525
    valeur_normalisee: 0.46355294147434944
    valeur_ponderee: 0.46355294147434944
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_argent:
    valeur: 0.07407535494478434
    valeur_normalisee: 0.9036354071129336
    valeur_ponderee: 0.9036354071129336
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_argent:
    valeur: 0.05680114601135289
    valeur_normalisee: 0.792274092159593
    valeur_ponderee: 0.792274092159593
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-23T05:22:52.322669+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.31454308236926903
    valeur_normalisee: 0.15727154118463452
    valeur_ponderee: 0.15727154118463452
    ts: '2026-07-23T05:22:52.322669+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée (Black Sea disruptions,
      USDA baisse production/stocks, conflit Russie-Ukraine) et fraîches (jusqu''au
      22 juillet). Le prix a déjà monté de 19% sur 20j, mais les news récentes (22
      juillet) confirment le biais haussier, justifiant une conviction haute malgré '
    nature: structurel
    event_id: 232c94c9f900
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 43.1999999999999
      7j: 43.1999999999999
      1m: 43.1999999999999
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -25958.0
    valeur_normalisee: 0.24746974397717958
    valeur_ponderee: 0.24746974397717958
    ts: '2026-07-23T05:22:52.322669+00:00'
  meteo_australie_dryland:
    valeur: 0.04417510964881471
    valeur_normalisee: 0.022087554824407354
    valeur_ponderee: 0.022087554824407354
    ts: '2026-07-23T05:22:52.322669+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_ble:
    valeur: 0.19214087602927177
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_ble:
    valeur: 0.04373681125630835
    valeur_normalisee: 0.37018898017237706
    valeur_ponderee: 0.37018898017237706
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_ble:
    valeur: 0.0459312318995595
    valeur_normalisee: 0.7636349013691759
    valeur_ponderee: 0.7636349013691759
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-23T05:22:52.322669+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-07-23T05:22:52.322669+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.016420046779533015
    valeur_normalisee: 0.5205948313148904
    valeur_ponderee: 0.5205948313148904
    ts: '2026-07-23T05:22:52.322669+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.0010996261271167818
    valeur_normalisee: 0.08219365353874265
    valeur_ponderee: 0.08219365353874265
    ts: '2026-07-23T05:22:52.322669+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée sur l'escalade
      Iran-USA (frappes nocturnes, menace nucléaire, détroit d'Ormuz) et tarifs US
      (Canada, Brésil), malgré une hausse récente du CAC40 de +0.62% sur 20j. La fraîcheur
      et la densité des signaux SHORT (30+ news en 4 jours) surclassent le mouvement
    nature: structurel
    event_id: 4ebd3fb6a165
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -116.36666666666679
      7j: -116.36666666666679
      1m: -116.36666666666679
    sign_conflict: true
    sign_conflict_details:
    - event_id: 351a6b7e7bc6
      asset: CAC40
      rule_name: cpi_actions
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: inflation
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse temporaire de l'inflation en juin, hausse attendue par la suite
  rsi_14j_fchi:
    valeur: 57.56579208037725
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.006248820112214171
    valeur_normalisee: -0.07060041994138962
    valeur_ponderee: -0.07060041994138962
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.008755806469515681
    valeur_normalisee: 0.1891915264053956
    valeur_ponderee: 0.1891915264053956
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.01188180149315965
    valeur_normalisee: 0.3940764331909495
    valeur_ponderee: 0.3940764331909495
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-07-23T05:22:52.322669+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-22'
    valeur: 0.3822598866442453
    valeur_normalisee: 0.19112994332212266
    valeur_ponderee: 0.19112994332212266
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -18516.0
    valeur_normalisee: -0.6527264467064956
    valeur_ponderee: -0.6527264467064956
    ts: '2026-07-23T05:22:52.322669+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 80.70000000000016
      7j: 80.70000000000016
      1m: 80.70000000000016
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  maladies_cabosses:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese_news_high
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: 'Signaux contradictoires : news récentes SHORT (demande faible,
      offre abondante) s''opposent aux news LONG plus anciennes (El Niño, demande
      nord-américaine). Le prix a monté de +6.23% sur 20j mais baissé de -3.68% sur
      5j, suggérant que le marché a déjà intégré les risques El Niño et se tourne
      vers les'
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 161.39999999999984
      7j: 161.39999999999984
      1m: 161.39999999999984
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.06227938208335515
    valeur_normalisee: -0.1902837226137217
    valeur_ponderee: -0.1902837226137217
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.02089189147360948
    valeur_normalisee: -0.34542620531091484
    valeur_ponderee: -0.34542620531091484
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.03266567156601774
    valeur_normalisee: -0.41689401700499634
    valeur_ponderee: -0.41689401700499634
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-23T05:22:52.322669+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.40165849517112373
    valeur_normalisee: 0.20082924758556187
    valeur_ponderee: 0.20082924758556187
    ts: '2026-07-23T05:22:52.322669+00:00'
  usd_brl:
    valeur: 5.06787
    valeur_normalisee: -0.47846785115412227
    valeur_ponderee: -0.47846785115412227
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_coffee:
    valeur: 26499.0
    valeur_normalisee: -0.18862009873184962
    valeur_ponderee: -0.18862009873184962
    ts: '2026-07-23T05:22:52.322669+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: 'Signal LONG dominant : tarifs US sur Brésil (16/07, high)
      + USDA haussier (15/07) + El Niño (17/07) pèsent plus que le tarif du 22/07
      (SHORT, même high) car ce dernier est contredit par le prix (+4.82%/20j) et
      la fraîcheur ne suffit pas à inverser le consensus LONG.'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '17.22'
    p2_shadow_contrib_exclu:
      24h: 84.43333333333342
      7j: 84.43333333333342
      1m: 84.43333333333342
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
    ts: '2026-07-23T05:22:52.322669+00:00'
  meteo_vietnam_robusta:
    valeur: 0.23208224035294764
    valeur_normalisee: 0.11604112017647382
    valeur_ponderee: 0.11604112017647382
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.04824302864763186
    valeur_normalisee: -0.059572746777850114
    valeur_ponderee: -0.059572746777850114
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.00911910422775808
    valeur_normalisee: -0.10019829094284394
    valeur_ponderee: -0.10019829094284394
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.020963363567532367
    valeur_normalisee: -0.3450160386375776
    valeur_ponderee: -0.3450160386375776
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-23T05:22:52.322669+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.49504609894741364
    valeur_normalisee: 0.24752304947370682
    valeur_ponderee: 0.24752304947370682
    ts: '2026-07-23T05:22:52.322669+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.05646156344348821
    valeur_normalisee: 0.028230781721744105
    valeur_ponderee: 0.028230781721744105
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_cotton:
    valeur: 101259.0
    valeur_normalisee: 0.7785042547190695
    valeur_ponderee: 0.7785042547190695
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_coton:
    valeur: 0.06210526315789466
    valeur_normalisee: 0.349271826999631
    valeur_ponderee: 0.349271826999631
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_coton:
    valeur: 0.002185141040921712
    valeur_normalisee: 0.05661322499174568
    valeur_ponderee: 0.05661322499174568
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_coton:
    valeur: 0.03190836571896094
    valeur_normalisee: 0.5225584263404396
    valeur_ponderee: 0.5225584263404396
    ts: '2026-07-23T05:22:52.322669+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  demande_chine_coton:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    event_id: f37165710bf1
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 27.63333333333332
      7j: 27.63333333333332
      1m: 27.63333333333332
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-23T05:22:52.322669+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: Les news LONG récentes (record de prix, demande chinoise forte,
      plan d'électrification UE) dominent les SHORT plus anciennes (PIB chinois faible,
      ventes auto en baisse). Le prix a déjà monté de 5%, ce qui limite la conviction.
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 6.766666666666664
      7j: 6.766666666666664
      1m: 6.766666666666664
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_copper_nets:
    valeur: 65629.0
    valeur_normalisee: 0.8500644003681505
    valeur_ponderee: 0.8500644003681505
    ts: '2026-07-23T05:22:52.322669+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 24.499999999999993
      7j: 24.499999999999993
      1m: 24.499999999999993
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.0015718019613073305
    valeur_normalisee: 0.7895215342073383
    valeur_ponderee: 0.7895215342073383
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.05028106825387568
    valeur_normalisee: 0.7110643742149663
    valeur_ponderee: 0.7110643742149663
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.039237322931636065
    valeur_normalisee: 0.7595676083081327
    valeur_ponderee: 0.7595676083081327
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.028429940956129718
    valeur_normalisee: 0.6351954242279919
    valeur_ponderee: 0.6351954242279919
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5226228744999997
    valeur_normalisee: 0.1518244580710941
    valeur_ponderee: 0.1518244580710941
    ts: '2026-07-23T05:22:52.322669+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6599999999999997
    valeur_normalisee: 0.9581208214163773
    valeur_ponderee: 0.9581208214163773
    ts: '2026-07-23T05:22:52.322669+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  usd_jpy_proxy_risk:
    valeur: 163.11037
    valeur_normalisee: 0.839148873456668
    valeur_ponderee: 0.839148873456668
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_eur_nets:
    valeur: -34257.0
    valeur_normalisee: -0.6453198959279014
    valeur_ponderee: -0.6453198959279014
    ts: '2026-07-23T05:22:52.322669+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.0005071570350551058
    valeur_normalisee: 0.526202906721736
    valeur_ponderee: 0.526202906721736
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.0011011002263372482
    valeur_normalisee: 0.0735569828873346
    valeur_ponderee: 0.0735569828873346
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.0013929528849017103
    valeur_normalisee: 0.27983355868277654
    valeur_ponderee: 0.27983355868277654
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.37
    valeur_normalisee: 0.8277699459470258
    valeur_ponderee: 0.8277699459470258
    ts: '2026-07-23T05:22:52.322669+00:00'
  sox_trend_5j:
    valeur: 555.52002
    valeur_normalisee: 0.026976009479368672
    valeur_ponderee: 0.026976009479368672
    ts: '2026-07-23T05:22:52.322669+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16630042294748487
    valeur_normalisee: 0.3956623066608616
    valeur_ponderee: 0.3956623066608616
    ts: '2026-07-23T05:22:52.322669+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée : escalade US-Iran
      (pétrole, inflation, craintes Fed) et résultats tech décevants (Alphabet/Tesla).
      Le contexte de baisse de prix (-1.16% sur 20j) confirme le biais baissier, renforcé
      par des news fraîches du jour.'
    nature: ponctuel
    event_id: 091bed95f9ba
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 69.66666666666673
      7j: 69.66666666666673
      1m: 69.66666666666673
  flux_etf_qqq_5j:
    valeur: -0.01726253263385824
    valeur_normalisee: -0.4349514000864304
    valeur_ponderee: -0.4349514000864304
    ts: '2026-07-23T05:22:52.322669+00:00'
  spread_nasdaq_russell2000:
    valeur: 411.55996999999996
    valeur_normalisee: -0.3444744800079253
    valeur_ponderee: -0.3444744800079253
    ts: '2026-07-23T05:22:52.322669+00:00'
  rsi_14j_ixic:
    valeur: 46.141318853076235
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.011630406736344079
    valeur_normalisee: -0.4666765539063424
    valeur_ponderee: -0.4666765539063424
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.008978011759603444
    valeur_normalisee: -0.3025087995168754
    valeur_ponderee: -0.3025087995168754
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.014410365886402987
    valeur_normalisee: 0.2348294539100384
    valeur_ponderee: 0.2348294539100384
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.37
    valeur_normalisee: 0.8277699459470258
    valeur_ponderee: 0.8277699459470258
    ts: '2026-07-23T05:22:52.322669+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_nets:
    valeur: 175931.0
    valeur_normalisee: -0.19336088557858558
    valeur_ponderee: -0.19336088557858558
    ts: '2026-07-23T05:22:52.322669+00:00'
  flux_etf_or_5j:
    valeur: 0.018181790837067613
    valeur_normalisee: 0.560813875923225
    valeur_ponderee: 0.560813875923225
    ts: '2026-07-23T05:22:52.322669+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: Escalade US-Iran avec frappes nocturnes continues et menaces
      Houthis sur le détroit d'Ormuz et la mer Rouge créent un choc d'offre pétrolier
      et une demande de safe haven, dominant largement la hausse des rendements US.
      Le récent rebond de +2.79% sur 5j confirme l'absorption du signal long, mais
      la f
    nature: structurel
    event_id: 9b18d9bf4c83
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 170.40000000000012
      7j: 170.40000000000012
      1m: 170.40000000000012
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-23T05:22:52.322669+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_or:
    valeur: -0.012595399118393358
    valeur_normalisee: 0.4760728355108806
    valeur_ponderee: 0.4760728355108806
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_or:
    valeur: 0.03660462207394999
    valeur_normalisee: 0.9344897943962484
    valeur_ponderee: 0.9344897943962484
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_or:
    valeur: 0.028452933478039677
    valeur_normalisee: 0.7767287285315512
    valeur_ponderee: 0.7767287285315512
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
petrole:
  eia_crude_surprise:
    valeur: 411675.0
    valeur_normalisee: -0.5782047119748305
    valeur_ponderee: -0.5782047119748305
    ts: '2026-07-23T05:22:52.322669+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: Escalade US-Iran avec frappes continues, attaques Houthis
      en mer Rouge et menace sur Ormuz dominent largement, avec matérialité high et
      fraîcheur immédiate. Les rares signaux SHORT (demande chinoise faible, excédent
      structurel) sont marginaux face au choc d'offre géopolitique.
    nature: structurel
    event_id: 9b18d9bf4c83
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 146.03333333333342
      7j: 146.03333333333342
      1m: 146.03333333333342
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 51028.0
    valeur_normalisee: 0.5358446521183773
    valeur_ponderee: 0.5358446521183773
    ts: '2026-07-23T05:22:52.322669+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    event_id: 9b18d9bf4c83
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 162.43333333333348
      7j: 162.43333333333348
      1m: 162.43333333333348
    sign_conflict: true
    sign_conflict_details:
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
    - event_id: 417f7c27cfee
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins que prévu
    - event_id: 1d1529ae2727
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse des stocks de brut inférieure aux attentes, signal de demande
        plus faible
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
    - event_id: 9eebdfb99c50
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: crude oil inventories
      matched_surprise: rise
      surprise_polarity: up
      title: Crude oil jumps 6% on supply concerns, US wholesale inventories rise
        0.1% in May
    - event_id: db8ce3bef4fa
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: crude oil inventories
      matched_surprise: rise
      surprise_polarity: up
      title: Crude oil jumps 6% amid broad market selloff; US wholesale inventories
        rise 0.1% in May
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  cushing_stocks:
    valeur: 19370.0
    valeur_normalisee: -0.7071724108334729
    valeur_ponderee: -0.7071724108334729
    ts: '2026-07-23T05:22:52.322669+00:00'
  spread_brent_wti:
    valeur: 7.888090000000005
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.31039592944993966
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.12712372745123646
    valeur_normalisee: 0.7278228628456686
    valeur_ponderee: 0.7278228628456686
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.08177805474502642
    valeur_normalisee: 0.755647574134361
    valeur_ponderee: 0.755647574134361
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-23T05:22:52.322669+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.04999999999999982
    valeur_normalisee: 0.14801425209390842
    valeur_ponderee: 0.14801425209390842
    ts: '2026-07-23T05:22:52.322669+00:00'
  hy_credit_spread:
    valeur: 2.69
    valeur_normalisee: -0.5281937770226375
    valeur_ponderee: -0.5281937770226375
    ts: '2026-07-23T05:22:52.322669+00:00'
  breadth_sp_ma50:
    valeur: 0.2845827705509467
    valeur_normalisee: 0.36289801858276893
    valeur_ponderee: 0.36289801858276893
    ts: '2026-07-23T05:22:52.322669+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.00980383142777641
    valeur_normalisee: -0.4661521013991411
    valeur_ponderee: -0.4661521013991411
    ts: '2026-07-23T05:22:52.322669+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.94
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-23T05:22:52.322669+00:00'
  rsi_14j_gspc:
    valeur: 51.26953671709346
    ts: '2026-07-23T05:22:52.322669+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.37
    valeur_normalisee: 0.8277699459470258
    valeur_ponderee: 0.8277699459470258
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.01885268085682057
    valeur_normalisee: -0.16073672815684684
    valeur_ponderee: -0.16073672815684684
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.0023492799324392744
    valeur_normalisee: -0.25710897871534066
    valeur_ponderee: -0.25710897871534066
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.005542910722407424
    valeur_normalisee: 0.12346000759891067
    valeur_ponderee: 0.12346000759891067
    ts: '2026-07-23T05:22:52.322669+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-07-23T05:22:52.322669+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-22'
    valeur: -0.2138384775982998
    valeur_normalisee: 0.1069192387991499
    valeur_ponderee: 0.1069192387991499
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 96.16942
    valeur_normalisee: 0.2523465357197371
    valeur_ponderee: 0.2523465357197371
    ts: '2026-07-23T05:22:52.322669+00:00'
  usd_brl_sucre:
    valeur: 5.06787
    valeur_normalisee: -0.47846785115412227
    valeur_ponderee: -0.47846785115412227
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_sugar:
    valeur: -45822.0
    valeur_normalisee: -0.4281576108153665
    valeur_ponderee: -0.4281576108153665
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.051948051948051965
    valeur_normalisee: 0.4181789047457517
    valeur_ponderee: 0.4181789047457517
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.003076923076922977
    valeur_normalisee: -0.13023530597914212
    valeur_ponderee: -0.13023530597914212
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.002053388090349051
    valeur_normalisee: -0.08801235921024532
    valeur_ponderee: -0.08801235921024532
    ts: '2026-07-23T05:22:52.322669+00:00'
  prod_inde_thai_sucre:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    event_id: 9b9416f709bd
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 21.599999999999987
      7j: 21.599999999999987
      1m: 21.599999999999987
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  exports_bresil_sucre:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    event_id: 9b9416f709bd
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 21.599999999999987
      7j: 21.599999999999987
      1m: 21.599999999999987
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-23T05:22:52.322669+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5899999999999999
    valeur_normalisee: 0.9378147519042628
    valeur_ponderee: 0.9378147519042628
    ts: '2026-07-23T05:22:52.322669+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.004488208499113355
    valeur_normalisee: 0.29193835403116364
    valeur_ponderee: 0.29193835403116364
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.0036884290338317083
    valeur_normalisee: 0.38711427487765465
    valeur_ponderee: 0.38711427487765465
    ts: '2026-07-23T05:22:52.322669+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.010759344161194395
    valeur_normalisee: 0.23285545432589905
    valeur_ponderee: 0.23285545432589905
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_jpy_nets:
    valeur: -127263.0
    valeur_normalisee: -0.5107367349427174
    valeur_ponderee: -0.5107367349427174
    ts: '2026-07-23T05:22:52.322669+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.96
    valeur_normalisee: 0.8990642062378184
    valeur_ponderee: 0.8990642062378184
    ts: '2026-07-23T05:22:52.322669+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-23T05:22:52.322669+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 2.399999999999999
      7j: 2.399999999999999
      1m: 2.399999999999999
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-23T05:22:52.322669+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-23T05:22:52.322669+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-23T05:22:52.322669+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-23T05:22:52.322669+00:00'
  gap_rv_iv:
    valeur: -4.550936192278327
    ts: '2026-07-23T05:22:52.322669+00:00'
  cftc_cot_vix_nets:
    valeur: -65783.0
    valeur_normalisee: -0.26642687690687433
    valeur_ponderee: -0.26642687690687433
    ts: '2026-07-23T05:22:52.322669+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-23T05:22:52.322669+00:00'
    synthese_rationale: 12 news de matérialité high toutes LONG ce jour, confirmant
      une escalade US-Iran avec menaces sur Ormuz et mer Rouge, dominant le contexte
      de prix baissier sur 20j. La fraîcheur et la cohérence des signaux justifient
      une conviction élevée.
    nature: structurel
    event_id: 9b18d9bf4c83
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 192.0333333333333
      7j: 192.0333333333333
      1m: 192.0333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-23T05:22:52.322669+00:00'
```
