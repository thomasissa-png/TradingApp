# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-18T05:26:32.672472+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5600369033629314
    valeur_ponderee: 0.5600369033629314
    ts: '2026-08-18T05:26:32.672472+00:00'
  mouvement_or_5j:
    valeur: 0.010255252372944001
    valeur_normalisee: 0.1208559331931513
    valeur_ponderee: 0.1208559331931513
    ts: '2026-08-18T05:26:32.672472+00:00'
  ratio_gold_silver:
    valeur: 67.41538423785846
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_silver:
    valeur: 21465.0
    valeur_normalisee: -0.2803992279605361
    valeur_ponderee: -0.2803992279605361
    ts: '2026-08-18T05:26:32.672472+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.0026931493014643593
    valeur_normalisee: 0.15013202340533494
    valeur_ponderee: 0.15013202340533494
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_argent:
    valeur: 0.13141200644525397
    valeur_normalisee: 0.8524901950247672
    valeur_ponderee: 0.8524901950247672
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_argent:
    valeur: 0.008165780589751925
    valeur_normalisee: 0.08968825212589375
    valeur_ponderee: 0.08968825212589375
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_argent:
    valeur: 0.007879071141932092
    valeur_normalisee: 0.10325211262875876
    valeur_ponderee: 0.10325211262875876
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.1962005168266471
    valeur_normalisee: 0.09810025841332355
    valeur_ponderee: 0.09810025841332355
    ts: '2026-08-18T05:26:32.672472+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (fermeture
      d'Ormuz, tensions mer Noire, frappes sur Novorossiysk) malgré une prise de bénéfices
      isolée. Le prix a déjà monté (+2.11% sur 20j), mais les drivers géopolitiques
      récents confirment le biais haussier.
    nature: structurel
    event_id: 2b47e84d9080
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.23'
    p2_shadow_contrib_exclu:
      24h: 126.70000000000002
      7j: 126.70000000000002
      1m: 126.70000000000002
  cftc_cot_wheat:
    valeur: -31179.0
    valeur_normalisee: 0.1801460824733161
    valeur_ponderee: 0.1801460824733161
    ts: '2026-08-18T05:26:32.672472+00:00'
  meteo_australie_dryland:
    valeur: -0.0352967287910984
    valeur_normalisee: -0.0176483643955492
    valeur_ponderee: -0.0176483643955492
    ts: '2026-08-18T05:26:32.672472+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_ble:
    valeur: 0.021050111752225487
    valeur_normalisee: -0.08403054207492855
    valeur_ponderee: -0.08403054207492855
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_ble:
    valeur: 0.06866009578151666
    valeur_normalisee: 0.583739985617046
    valeur_ponderee: 0.583739985617046
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_ble:
    valeur: -0.0018702791595325285
    valeur_normalisee: -0.13362313777274085
    valeur_ponderee: -0.13362313777274085
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-18T05:26:32.672472+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-18T05:26:32.672472+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.01631513919680183
    valeur_normalisee: -0.621639409686021
    valeur_ponderee: -0.621639409686021
    ts: '2026-08-18T05:26:32.672472+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.012774869109947629
    valeur_normalisee: -0.45027749345953416
    valeur_ponderee: -0.45027749345953416
    ts: '2026-08-18T05:26:32.672472+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: 'Signaux mitigés : PIB zone euro solide et emploi US faible
      (LONG) contre pressions géopolitiques, sécheresse et inflation (SHORT). Prix
      en hausse sur 20j mais repli récent, aucune dominante claire.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: -347.6666666666667
      7j: -347.6666666666667
      1m: -347.6666666666667
  rsi_14j_fchi:
    valeur: 54.33343715926863
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.02871535866428898
    valeur_normalisee: 0.2611679894510616
    valeur_ponderee: 0.2611679894510616
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.013806247628053159
    valeur_normalisee: -0.7461391391627017
    valeur_ponderee: -0.7461391391627017
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.010990371722933157
    valeur_normalisee: -0.6190355616478631
    valeur_ponderee: -0.6190355616478631
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: -0.03261425247044984
    valeur_normalisee: 0.01630712623522492
    valeur_ponderee: 0.01630712623522492
    ts: '2026-08-18T05:26:32.672472+00:00'
  hf_positioning_flux_options:
    valeur: -15606.0
    valeur_normalisee: -0.5862223435839012
    valeur_ponderee: -0.5862223435839012
    ts: '2026-08-18T05:26:32.672472+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 7f3f7e335e72
    event_date: '2026-08-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.23'
    p2_shadow_contrib_exclu:
      24h: 123.86666666666657
      7j: 123.86666666666657
      1m: 123.86666666666657
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
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: Multiples news high matérialité récentes (17/08, 15/08, 11/08)
      confirment la menace El Niño sur l'offre, dominant les quelques signaux SHORT
      plus anciens. Le prix est déjà en hausse (+17% sur 20j), cohérent avec le biais
      LONG.
    nature: structurel
    event_id: 7f3f7e335e72
    event_date: '2026-08-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.23'
    p2_shadow_contrib_exclu:
      24h: 126.43333333333327
      7j: 126.43333333333327
      1m: 126.43333333333327
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.17326763114474097
    valeur_normalisee: 0.08833065713252881
    valeur_ponderee: 0.08833065713252881
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.09734251264627947
    valeur_normalisee: 0.25030731170396947
    valeur_ponderee: 0.25030731170396947
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.051135996850082854
    valeur_normalisee: 0.2584685944689848
    valeur_ponderee: 0.2584685944689848
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-18T05:26:32.672472+00:00'
cafe:
  meteo_bresil_minas_gerais:
    ts: '2026-08-18T05:26:32.672472+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-14'
    valeur: -0.40754739096499126
    valeur_normalisee: 0.20377369548249563
    valeur_ponderee: 0.20377369548249563
    reporte_cause: source réseau indisponible
  usd_brl:
    valeur: 5.20408
    valeur_normalisee: 0.7509413258761375
    valeur_ponderee: 0.7509413258761375
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_coffee:
    valeur: 27282.0
    valeur_normalisee: -0.16470293830600344
    valeur_ponderee: -0.16470293830600344
    ts: '2026-08-18T05:26:32.672472+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: Les news LONG dominent, notamment les alertes El Niño (mat=high)
      du 7 août et la hausse de l'arabica le 10 août, malgré des pressions baissières
      sur la récolte brésilienne. Le prix a baissé sur 20j mais rebondi sur 5j, suggérant
      que le marché intègre déjà un biais haussier récent.
    nature: ponctuel
    event_id: 8491e889170b
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.23'
    p2_shadow_contrib_exclu:
      24h: 113.73333333333356
      7j: 113.73333333333356
      1m: 113.73333333333356
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-18T05:26:32.672472+00:00'
  meteo_vietnam_robusta:
    valeur: 0.4552059956530745
    valeur_normalisee: 0.22760299782653726
    valeur_ponderee: 0.22760299782653726
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.026538298108665703
    valeur_normalisee: -0.5247172782111439
    valeur_ponderee: -0.5247172782111439
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.016948589089727184
    valeur_normalisee: -0.049860742023781525
    valeur_ponderee: -0.049860742023781525
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.0119379016590353
    valeur_normalisee: 0.03258811020433071
    valeur_ponderee: 0.03258811020433071
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-18T05:26:32.672472+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.05113325465510125
    valeur_normalisee: 0.025566627327550624
    valeur_ponderee: 0.025566627327550624
    ts: '2026-08-18T05:26:32.672472+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.810768396627114
    valeur_normalisee: 0.405384198313557
    valeur_ponderee: 0.405384198313557
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_cotton:
    valeur: 110304.0
    valeur_normalisee: 0.8731439466661239
    valeur_ponderee: 0.8731439466661239
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_coton:
    valeur: 0.08278822567457067
    valeur_normalisee: 0.7022748553200774
    valeur_ponderee: 0.7022748553200774
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_coton:
    valeur: 0.02535811072396421
    valeur_normalisee: 0.332560207273955
    valeur_ponderee: 0.332560207273955
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_coton:
    valeur: 0.00474203338391499
    valeur_normalisee: 0.07643197095718474
    valeur_ponderee: 0.07643197095718474
    ts: '2026-08-18T05:26:32.672472+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '11.23'
    p2_shadow_contrib_exclu:
      24h: 70.0000000000001
      7j: 70.0000000000001
      1m: 70.0000000000001
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-18T05:26:32.672472+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: 'Signaux mitigés : offre chilienne en rebond et demande chinoise
      faible (SHORT) contre demande électrique record et importations chinoises élevées
      (LONG). Le prix a déjà monté de 3.99% sur 20j, suggérant que les nouvelles positives
      sont largement intégrées.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 86.60000000000016
      7j: 86.60000000000016
      1m: 86.60000000000016
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_copper_nets:
    valeur: 80503.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-18T05:26:32.672472+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 33d84a40551b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '12.23'
    p2_shadow_contrib_exclu:
      24h: 57.00000000000004
      7j: 57.00000000000004
      1m: 57.00000000000004
  ratio_cuivre_or:
    valeur: 0.0014923548732436866
    valeur_normalisee: -0.5375815739890383
    valeur_ponderee: -0.5375815739890383
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.03988440955666017
    valeur_normalisee: 0.3840347913049177
    valeur_ponderee: 0.3840347913049177
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.00790039214618754
    valeur_normalisee: -0.2400648556070655
    valeur_ponderee: -0.2400648556070655
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.006244215163353939
    valeur_normalisee: -0.22207867639246323
    valeur_ponderee: -0.22207867639246323
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4423511795000001
    valeur_normalisee: -0.6860941649246732
    valeur_ponderee: -0.6860941649246732
    ts: '2026-08-18T05:26:32.672472+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7099999999999995
    valeur_normalisee: 0.6494522104635299
    valeur_ponderee: 0.6494522104635299
    ts: '2026-08-18T05:26:32.672472+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.67603
    valeur_normalisee: -0.3535937804464313
    valeur_ponderee: -0.3535937804464313
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_eur_nets:
    valeur: -79915.0
    valeur_normalisee: -0.9298361009982374
    valeur_ponderee: -0.9298361009982374
    ts: '2026-08-18T05:26:32.672472+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.009104386500392359
    valeur_normalisee: 0.4437473349290615
    valeur_ponderee: 0.4437473349290615
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.002442996742671122
    valeur_normalisee: 0.1677532799671407
    valeur_ponderee: 0.1677532799671407
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.00019880543862527134
    valeur_normalisee: -0.029020219093522488
    valeur_ponderee: -0.029020219093522488
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5600369033629314
    valeur_ponderee: 0.5600369033629314
    ts: '2026-08-18T05:26:32.672472+00:00'
  sox_trend_5j:
    valeur: 559.12
    valeur_normalisee: -0.052547953983701656
    valeur_ponderee: -0.052547953983701656
    ts: '2026-08-18T05:26:32.672472+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16982476331401483
    valeur_normalisee: 0.5434980947075074
    valeur_ponderee: 0.5434980947075074
    ts: '2026-08-18T05:26:32.672472+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: 'Signaux mitigés : news LONG sur l''IA (Nvidia, OpenAI, TSMC)
      contrebalancées par des news SHORT (rendements 30 ans à 5.31%, ventes au détail
      en baisse, craintes inflation). Le prix a déjà monté de 4.86% sur 20j, suggérant
      que le positif est pricé.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 166.66666666666688
      7j: 166.66666666666688
      1m: 166.66666666666688
  flux_etf_qqq_5j:
    valeur: 0.012484914062174779
    valeur_normalisee: 0.15693249358410244
    valeur_ponderee: 0.15693249358410244
    ts: '2026-08-18T05:26:32.672472+00:00'
  spread_nasdaq_russell2000:
    valeur: 425.810002
    valeur_normalisee: 0.1095937297734328
    valeur_ponderee: 0.1095937297734328
    ts: '2026-08-18T05:26:32.672472+00:00'
  rsi_14j_ixic:
    valeur: 59.113599172968215
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.04857340185780945
    valeur_normalisee: 0.3953032423618713
    valeur_ponderee: 0.3953032423618713
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.021297109877643328
    valeur_normalisee: 0.2665046651966395
    valeur_ponderee: 0.2665046651966395
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.008525618232338994
    valeur_normalisee: 0.12909819505052117
    valeur_ponderee: 0.12909819505052117
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5600369033629314
    valeur_ponderee: 0.5600369033629314
    ts: '2026-08-18T05:26:32.672472+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_nets:
    valeur: 214856.0
    valeur_normalisee: 0.14816439944873105
    valeur_ponderee: 0.14816439944873105
    ts: '2026-08-18T05:26:32.672472+00:00'
  flux_etf_or_5j:
    valeur: 0.0073284143854419614
    valeur_normalisee: 0.187393368762397
    valeur_ponderee: 0.187393368762397
    ts: '2026-08-18T05:26:32.672472+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: Majorité de news LONG à matérialité high et fraîcheur immédiate
      (attaque Ormuz, menace offensive Iran, expiration cessez-le-feu) dominent, malgré
      quelques signaux SHORT faibles. Le prix +8.09%/20j confirme la tendance haussière,
      et les news récentes renforcent le biais.
    nature: structurel
    event_id: 47bf489092e9
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.23'
    p2_shadow_contrib_exclu:
      24h: 395.53333333333154
      7j: 395.53333333333154
      1m: 395.53333333333154
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-18T05:26:32.672472+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_or:
    valeur: 0.08086274767935464
    valeur_normalisee: 0.8293007664355929
    valeur_ponderee: 0.8293007664355929
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_or:
    valeur: 0.006429334987158697
    valeur_normalisee: 0.0334729805761083
    valeur_ponderee: 0.0334729805761083
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_or:
    valeur: 0.0046189230029547446
    valeur_normalisee: 0.05567691036804938
    valeur_ponderee: 0.05567691036804938
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-18T05:26:32.672472+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-14'
    valeur: 424410.0
    valeur_normalisee: -0.13812033584105132
    valeur_ponderee: -0.13812033584105132
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité high et fraîcheur immédiate
      (18/08) : attaque en Ormuz, expiration du cessez-le-feu, stratégie offensive
      iranienne, perturbation de l''offre. Les rares signaux SHORT sont faibles et
      anciens, ne contrebalancent pas le signal haussier net.'
    nature: structurel
    event_id: 47bf489092e9
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.23'
    p2_shadow_contrib_exclu:
      24h: 372.09999999999866
      7j: 372.09999999999866
      1m: 372.09999999999866
  cftc_cot_crude_nets:
    valeur: 23853.0
    valeur_normalisee: -0.045557257567997375
    valeur_ponderee: -0.045557257567997375
    ts: '2026-08-18T05:26:32.672472+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 47bf489092e9
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.23'
    p2_shadow_contrib_exclu:
      24h: 343.43333333333123
      7j: 343.43333333333123
      1m: 343.43333333333123
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
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  cushing_stocks:
    valeur: 22566.0
    valeur_normalisee: -0.15882864718542616
    valeur_ponderee: -0.15882864718542616
    ts: '2026-08-18T05:26:32.672472+00:00'
  spread_brent_wti:
    valeur: 4.752639000000002
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.015230179551228074
    valeur_normalisee: 0.10425359882668224
    valeur_ponderee: 0.10425359882668224
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.1051212113884834
    valeur_normalisee: 0.5926505405074548
    valeur_ponderee: 0.5926505405074548
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.04889962706962847
    valeur_normalisee: 0.4044481200235429
    valeur_ponderee: 0.4044481200235429
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-18T05:26:32.672472+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.02999999999999936
    valeur_normalisee: 0.12426641483934978
    valeur_ponderee: 0.12426641483934978
    ts: '2026-08-18T05:26:32.672472+00:00'
  hy_credit_spread:
    valeur: 2.67
    valeur_normalisee: -0.6141117489632224
    valeur_ponderee: -0.6141117489632224
    ts: '2026-08-18T05:26:32.672472+00:00'
  breadth_sp_ma50:
    valeur: 0.2857494088226386
    valeur_normalisee: 0.16878936828047256
    valeur_ponderee: 0.16878936828047256
    ts: '2026-08-18T05:26:32.672472+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.0004657632776126075
    valeur_normalisee: -0.11827296079860367
    valeur_ponderee: -0.11827296079860367
    ts: '2026-08-18T05:26:32.672472+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.35
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-18T05:26:32.672472+00:00'
  rsi_14j_gspc:
    valeur: 61.752907833574156
    ts: '2026-08-18T05:26:32.672472+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5600369033629314
    valeur_ponderee: 0.5600369033629314
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.041207874903835595
    valeur_normalisee: 0.5860325762753074
    valeur_ponderee: 0.5860325762753074
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.005347637139585748
    valeur_normalisee: -0.0010735610864200092
    valeur_ponderee: -0.0010735610864200092
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.00023299978294866186
    valeur_normalisee: -0.08345467827398144
    valeur_ponderee: -0.08345467827398144
    ts: '2026-08-18T05:26:32.672472+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
sucre:
  brent_ethanol_proxy_sucre:
    valeur: 90.036579
    valeur_normalisee: 0.3893418726572922
    valeur_ponderee: 0.3893418726572922
    ts: '2026-08-18T05:26:32.672472+00:00'
  usd_brl_sucre:
    valeur: 5.20408
    valeur_normalisee: 0.7509413258761375
    valeur_ponderee: 0.7509413258761375
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_sugar:
    valeur: 80425.0
    valeur_normalisee: 0.08231776585326993
    valeur_ponderee: 0.08231776585326993
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.11873080859774832
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.07156862745098036
    valeur_normalisee: 0.7031300045367309
    valeur_ponderee: 0.7031300045367309
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.022450888681010417
    valeur_normalisee: 0.3454101255394598
    valeur_ponderee: 0.3454101255394598
    ts: '2026-08-18T05:26:32.672472+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '11.23'
    p2_shadow_contrib_exclu:
      24h: 54.966666666666676
      7j: 54.966666666666676
      1m: 54.966666666666676
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
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '11.23'
    p2_shadow_contrib_exclu:
      24h: 54.966666666666676
      7j: 54.966666666666676
      1m: 54.966666666666676
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-18T05:26:32.672472+00:00'
  meteo_bresil_canne_sucre:
    valeur: -0.2777963714867588
    valeur_normalisee: 0.1388981857433794
    valeur_ponderee: 0.1388981857433794
    ts: '2026-08-18T05:26:32.672472+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5
    valeur_normalisee: 0.04959887909386986
    valeur_ponderee: 0.04959887909386986
    ts: '2026-08-18T05:26:32.672472+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.002317539800838153
    valeur_normalisee: 0.1147294794059344
    valeur_ponderee: 0.1147294794059344
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.002191528658398667
    valeur_normalisee: 0.15108620451188753
    valeur_ponderee: 0.15108620451188753
    ts: '2026-08-18T05:26:32.672472+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.023038707485790177
    valeur_normalisee: -0.5868783461488055
    valeur_ponderee: -0.5868783461488055
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_jpy_nets:
    valeur: -40040.0
    valeur_normalisee: 0.031499248803131374
    valeur_ponderee: 0.031499248803131374
    ts: '2026-08-18T05:26:32.672472+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.01
    valeur_normalisee: 0.6445705668255312
    valeur_ponderee: 0.6445705668255312
    ts: '2026-08-18T05:26:32.672472+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia
    ts: '2026-08-18T05:26:32.672472+00:00'
    nature: structurel
    event_id: 99255537fb71
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.23'
    p2_shadow_contrib_exclu:
      24h: 3.50000000000001
      7j: 3.50000000000001
      1m: 3.50000000000001
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-18T05:26:32.672472+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-18T05:26:32.672472+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-18T05:26:32.672472+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-18T05:26:32.672472+00:00'
  gap_rv_iv:
    valeur: -1.7692859488246615
    ts: '2026-08-18T05:26:32.672472+00:00'
  cftc_cot_vix_nets:
    valeur: -74934.0
    valeur_normalisee: -0.44221335910303994
    valeur_ponderee: -0.44221335910303994
    ts: '2026-08-18T05:26:32.672472+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-18T05:26:32.672472+00:00'
    synthese_rationale: Toutes les news récentes (≤48h) sont LONG, avec une matérialité
      majoritairement high et des confirmations (attaque Ormuz, expiration cessez-le-feu,
      fermeture détroit). Le contexte marché montre une baisse du VIX (-11.35%/20j),
      mais la fraîcheur et la gravité des événements géopolitiques (Ormuz, Iran
    nature: structurel
    event_id: 47bf489092e9
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.23'
    p2_shadow_contrib_exclu:
      24h: 408.3999999999983
      7j: 408.3999999999983
      1m: 408.3999999999983
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-18T05:26:32.672472+00:00'
```
