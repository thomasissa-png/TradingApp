# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-27T05:23:00.757650+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.06658736153418282
    valeur_ponderee: 0.06658736153418282
    ts: '2026-08-27T05:23:00.757650+00:00'
  mouvement_or_5j:
    valeur: 0.0026652672039988445
    valeur_normalisee: -0.11441968644794236
    valeur_ponderee: -0.11441968644794236
    ts: '2026-08-27T05:23:00.757650+00:00'
  ratio_gold_silver:
    valeur: 66.88225041989821
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_silver:
    valeur: 21431.0
    valeur_normalisee: -0.28020633769108966
    valeur_ponderee: -0.28020633769108966
    ts: '2026-08-27T05:23:00.757650+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.026328974250279247
    valeur_normalisee: 0.25136009665903564
    valeur_ponderee: 0.25136009665903564
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_argent:
    valeur: 0.08648299780502167
    valeur_normalisee: 0.3634443165096998
    valeur_ponderee: 0.3634443165096998
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_argent:
    valeur: 0.014372687399996975
    valeur_normalisee: -0.03401938118788276
    valeur_ponderee: -0.03401938118788276
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_argent:
    valeur: 0.0014342178691775231
    valeur_normalisee: -0.10346525203532643
    valeur_ponderee: -0.10346525203532643
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.037508491572347896
    valeur_normalisee: 0.018754245786173948
    valeur_ponderee: 0.018754245786173948
    ts: '2026-08-27T05:23:00.757650+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (problèmes
      d'exportation en mer Noire, El Niño, sécheresses) cohérentes avec le rally de
      +15% sur 20j. La seule news SHORT (sables bitumineux) est hors sujet et faible.
    nature: structurel
    event_id: 9101641b7a19
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 157.96666666666655
      7j: 157.96666666666655
      1m: 157.96666666666655
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -23542.0
    valeur_normalisee: 0.2852130850549151
    valeur_ponderee: 0.2852130850549151
    ts: '2026-08-27T05:23:00.757650+00:00'
  meteo_australie_dryland:
    valeur: -0.0021193580206303694
    valeur_normalisee: -0.0010596790103151847
    valeur_ponderee: -0.0010596790103151847
    ts: '2026-08-27T05:23:00.757650+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_ble:
    valeur: 0.15093037044536395
    valeur_normalisee: 0.6608693906125832
    valeur_ponderee: 0.6608693906125832
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_ble:
    valeur: 0.07658321159636072
    valeur_normalisee: 0.6213361917242726
    valeur_ponderee: 0.6213361917242726
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_ble:
    valeur: 0.07631331506291361
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-27T05:23:00.757650+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.0007735916247214591
    valeur_normalisee: -0.07617405544066297
    valeur_ponderee: -0.07617405544066297
    ts: '2026-08-27T05:23:00.757650+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.0065733672603900395
    valeur_normalisee: -0.28171962404182477
    valeur_ponderee: -0.28171962404182477
    ts: '2026-08-27T05:23:00.757650+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée et fraîche (guerre
      commerciale US-Canada, tarifs de rétorsion, chute des actions européennes) malgré
      un PIB allemand meilleur qu'attendu. Le prix récent (+0.64% sur 20j) est contredit,
      mais la fraîcheur et la matérialité des news SHORT justifient de suivr
    nature: structurel
    event_id: 7ddb3cbe65b1
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -218.63333333333296
      7j: -218.63333333333296
      1m: -218.63333333333296
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  rsi_14j_fchi:
    valeur: 43.84525611746347
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.006436534866883559
    valeur_normalisee: -0.35434923360317866
    valeur_ponderee: -0.35434923360317866
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.013661472018272947
    valeur_normalisee: -0.5185259945110358
    valeur_ponderee: -0.5185259945110358
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.0025977043602564143
    valeur_normalisee: -0.18686537492647706
    valeur_ponderee: -0.18686537492647706
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.0312902311800997
    valeur_normalisee: 0.01564511559004985
    valeur_ponderee: 0.01564511559004985
    ts: '2026-08-27T05:23:00.757650+00:00'
  hf_positioning_flux_options:
    valeur: -17088.0
    valeur_normalisee: -0.6073814431844113
    valeur_ponderee: -0.6073814431844113
    ts: '2026-08-27T05:23:00.757650+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: structurel
    event_id: b99d2b50a2e6
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 141.46666666666664
      7j: 141.46666666666664
      1m: 141.46666666666664
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
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: Les news récentes (23-26 août) sont majoritairement SHORT
      sur l'offre abondante, mais les news plus anciennes (19-21 août) à matérialité
      high (El Niño, baisse de récolte au Ghana) sont fortement LONG. Le prix a légèrement
      baissé sur 5j (-3.36%), ce qui suggère que le marché a déjà intégré les news
      S
    nature: structurel
    event_id: b99d2b50a2e6
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 145.79999999999998
      7j: 145.79999999999998
      1m: 145.79999999999998
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.018705006670961977
    valeur_normalisee: -0.31399157623648893
    valeur_ponderee: -0.31399157623648893
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.030191700777632335
    valeur_normalisee: -0.31487723949822555
    valeur_ponderee: -0.31487723949822555
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.016875406854345076
    valeur_normalisee: -0.23135244777629688
    valeur_ponderee: -0.23135244777629688
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
cafe:
  meteo_bresil_minas_gerais:
    ts: '2026-08-27T05:23:00.757650+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-26'
    valeur: -0.40789732748586705
    valeur_normalisee: 0.20394866374293352
    valeur_ponderee: 0.20394866374293352
    reporte_cause: source réseau indisponible
  usd_brl:
    valeur: 5.14904
    valeur_normalisee: 0.17760932615694477
    valeur_ponderee: 0.17760932615694477
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_coffee:
    valeur: 30706.0
    valeur_normalisee: -0.09623866131180062
    valeur_ponderee: -0.09623866131180062
    ts: '2026-08-27T05:23:00.757650+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: 'Les news LONG dominent, notamment les alertes El Niño de
      matérialité high (23/08, 21/08) et le canal de Panama confirmé, malgré plusieurs
      news SHORT sur la récolte brésilienne et vietnamienne. Le prix a déjà monté
      de +2.77% sur 20j, ce qui suggère un pricing partiel, mais la fraîcheur des
      news LONG '
    nature: ponctuel
    event_id: 84bffd94ba09
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 117.66666666666686
      7j: 117.66666666666686
      1m: 117.66666666666686
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-27T05:23:00.757650+00:00'
  meteo_vietnam_robusta:
    valeur: 0.5123328775263933
    valeur_normalisee: 0.25616643876319667
    valeur_ponderee: 0.25616643876319667
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.027681710879511767
    valeur_normalisee: -0.21661590623702737
    valeur_ponderee: -0.21661590623702737
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.018605385773893035
    valeur_normalisee: -0.3380284573136333
    valeur_ponderee: -0.3380284573136333
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.05729368470194185
    valeur_normalisee: -0.7712735041171322
    valeur_ponderee: -0.7712735041171322
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.018268446594197345
    valeur_normalisee: 0.009134223297098672
    valeur_ponderee: 0.009134223297098672
    ts: '2026-08-27T05:23:00.757650+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.8054356950910792
    valeur_normalisee: 0.4027178475455396
    valeur_ponderee: 0.4027178475455396
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_cotton:
    valeur: 113853.0
    valeur_normalisee: 0.9066635816917005
    valeur_ponderee: 0.9066635816917005
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_coton:
    valeur: 0.11946363266964655
    valeur_normalisee: 0.7861212221100621
    valeur_ponderee: 0.7861212221100621
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_coton:
    valeur: 0.04021144043798386
    valeur_normalisee: 0.4228770595143195
    valeur_ponderee: 0.4228770595143195
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_coton:
    valeur: 0.0005447612130016211
    valeur_normalisee: -0.08641432967216434
    valeur_ponderee: -0.08641432967216434
    ts: '2026-08-27T05:23:00.757650+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: structurel
    event_id: 2374791f65df
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 90.46666666666678
      7j: 90.46666666666678
      1m: 90.46666666666678
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese_news_high
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: 'Signaux mitigés : news récentes SHORT (profits industriels
      chinois, inflation australienne, offre chilienne) contrebalancées par des drivers
      LONG (tarifs US, stocks LME, VE). Prix stable (+0.61% sur 20j) suggère que le
      marché a déjà arbitré.'
    nature: structurel
    event_id: 7ec48a6013b2
    event_date: '2026-08-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 104.46666666666685
      7j: 104.46666666666685
      1m: 104.46666666666685
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_copper_nets:
    valeur: 79513.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: ponctuel
    event_id: 61d32360b04b
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 60.59999999999998
      7j: 60.59999999999998
      1m: 60.59999999999998
  ratio_cuivre_or:
    valeur: 0.0014286674152763934
    valeur_normalisee: -0.889997652669628
    valeur_ponderee: -0.889997652669628
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.00610117618727557
    valeur_normalisee: -0.15537399382597722
    valeur_ponderee: -0.15537399382597722
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.018916386638285765
    valeur_normalisee: 0.27050621802506436
    valeur_ponderee: 0.27050621802506436
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.0009295019052515396
    valeur_normalisee: -0.09528731116992249
    valeur_ponderee: -0.09528731116992249
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4195573424
    valeur_normalisee: -0.7719838086621288
    valeur_ponderee: -0.7719838086621288
    ts: '2026-08-27T05:23:00.757650+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6699999999999995
    valeur_normalisee: 0.3078639571566468
    valeur_ponderee: 0.3078639571566468
    ts: '2026-08-27T05:23:00.757650+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.34126
    valeur_normalisee: -0.32110978852647604
    valeur_ponderee: -0.32110978852647604
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_eur_nets:
    valeur: -80601.0
    valeur_normalisee: -0.9278126647744607
    valeur_ponderee: -0.9278126647744607
    ts: '2026-08-27T05:23:00.757650+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.008322087269455603
    valeur_normalisee: 0.24930428432999296
    valeur_ponderee: 0.24930428432999296
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.001995016739303468
    valeur_normalisee: -0.44790999604560844
    valeur_ponderee: -0.44790999604560844
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0007287192544773724
    valeur_normalisee: -0.2541605519751893
    valeur_ponderee: -0.2541605519751893
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.06658736153418282
    valeur_ponderee: 0.06658736153418282
    ts: '2026-08-27T05:23:00.757650+00:00'
  sox_trend_5j:
    valeur: 515.40002
    valeur_normalisee: -0.52910061316538
    valeur_ponderee: -0.52910061316538
    ts: '2026-08-27T05:23:00.757650+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17190772734301418
    valeur_normalisee: 0.7555112822683089
    valeur_ponderee: 0.7555112822683089
    ts: '2026-08-27T05:23:00.757650+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: Les résultats de Nvidia (CA doublé, prévision de croissance
      70%) dominent la fenêtre avec une matérialité élevée et une fraîcheur immédiate,
      soutenus par des partenariats IA (AWS, Amazon) et des gains sectoriels. La seule
      news SHORT à matérialité élevée (guerre commerciale US-Canada) est contrebalan
    nature: ponctuel
    event_id: c3d3f34ddda3
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 89.70000000000003
      7j: 89.70000000000003
      1m: 89.70000000000003
  flux_etf_qqq_5j:
    valeur: -0.0065775009610413715
    valeur_normalisee: -0.11055048800944244
    valeur_ponderee: -0.11055048800944244
    ts: '2026-08-27T05:23:00.757650+00:00'
  spread_nasdaq_russell2000:
    valeur: 412.44001000000003
    valeur_normalisee: -0.1937348542878172
    valeur_ponderee: -0.1937348542878172
    ts: '2026-08-27T05:23:00.757650+00:00'
  rsi_14j_ixic:
    valeur: 48.81021059331747
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.07501552219229968
    valeur_normalisee: 0.9244816408900044
    valeur_ponderee: 0.9244816408900044
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.0253469795991067
    valeur_normalisee: -0.3480826930273347
    valeur_ponderee: -0.3480826930273347
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.0029014352993945725
    valeur_normalisee: -0.02368783943551181
    valeur_ponderee: -0.02368783943551181
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.06658736153418282
    valeur_ponderee: 0.06658736153418282
    ts: '2026-08-27T05:23:00.757650+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_nets:
    valeur: 219495.0
    valeur_normalisee: 0.188135627570805
    valeur_ponderee: 0.188135627570805
    ts: '2026-08-27T05:23:00.757650+00:00'
  flux_etf_or_5j:
    valeur: 0.01807464237386447
    valeur_normalisee: 0.23153061462266375
    valeur_ponderee: 0.23153061462266375
    ts: '2026-08-27T05:23:00.757650+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: Dominance de news géopolitiques LONG (Ormuz, guerre Iran,
      tensions commerciales) avec matérialité élevée et fraîcheur du jour, malgré
      quelques signaux SHORT sur l'inflation et les rendements. Le prix +6.39%/20j
      confirme la tendance haussière, et les news récentes à fort impact renforcent
      le biais LO
    nature: structurel
    event_id: f2616112b48e
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 500.9333333333311
      7j: 500.9333333333311
      1m: 500.9333333333311
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
    ts: '2026-08-27T05:23:00.757650+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_or:
    valeur: 0.06396995784219395
    valeur_normalisee: 0.349576864621173
    valeur_ponderee: 0.349576864621173
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_or:
    valeur: 0.022367800535784355
    valeur_normalisee: 0.12318334037891071
    valeur_ponderee: 0.12318334037891071
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_or:
    valeur: -0.0068219734224073125
    valeur_normalisee: -0.3314797666423495
    valeur_ponderee: -0.3314797666423495
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
petrole:
  eia_crude_surprise:
    valeur: 428910.0
    valeur_normalisee: -0.010699044988311703
    valeur_ponderee: -0.010699044988311703
    ts: '2026-08-27T05:23:00.757650+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: Attaque de pétrolier à Ormuz et trafic toujours déprimé, avec
      près de la moitié de l'offre mondiale en zones de conflit, dominent malgré des
      espoirs de désescalade. La fraîcheur et la matérialité élevée des news LONG
      du jour surclassent les signaux SHORT plus anciens.
    nature: structurel
    event_id: f2616112b48e
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 469.0333333333315
      7j: 469.0333333333315
      1m: 469.0333333333315
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 16985.0
    valeur_normalisee: -0.19062765856647587
    valeur_ponderee: -0.19062765856647587
    ts: '2026-08-27T05:23:00.757650+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: structurel
    event_id: f2616112b48e
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 430.29999999999865
      7j: 430.29999999999865
      1m: 430.29999999999865
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  cushing_stocks:
    valeur: 22428.0
    valeur_normalisee: -0.18311536903012807
    valeur_ponderee: -0.18311536903012807
    ts: '2026-08-27T05:23:00.757650+00:00'
  spread_brent_wti:
    valeur: 4.569639999999993
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.005970858068991669
    valeur_normalisee: 0.09182150970268281
    valeur_ponderee: 0.09182150970268281
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.04182030438853024
    valeur_normalisee: -0.2064737162695541
    valeur_ponderee: -0.2064737162695541
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.045282697233282376
    valeur_normalisee: -0.3388517599242151
    valeur_ponderee: -0.3388517599242151
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-27T05:23:00.757650+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.07000000000000028
    valeur_normalisee: -0.6254579138493526
    valeur_ponderee: -0.6254579138493526
    ts: '2026-08-27T05:23:00.757650+00:00'
  hy_credit_spread:
    valeur: 2.7
    valeur_normalisee: -0.31533766863696727
    valeur_ponderee: -0.31533766863696727
    ts: '2026-08-27T05:23:00.757650+00:00'
  breadth_sp_ma50:
    valeur: 0.28993054912173755
    valeur_normalisee: 0.599491603461637
    valeur_ponderee: 0.599491603461637
    ts: '2026-08-27T05:23:00.757650+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.0038748355235607157
    valeur_normalisee: -0.17655022186473224
    valeur_ponderee: -0.17655022186473224
    ts: '2026-08-27T05:23:00.757650+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.98
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  rsi_14j_gspc:
    valeur: 53.72279010832747
    ts: '2026-08-27T05:23:00.757650+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.06658736153418282
    valeur_ponderee: 0.06658736153418282
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.050201513442779344
    valeur_normalisee: 0.925484495221274
    valeur_ponderee: 0.925484495221274
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.008528819768564122
    valeur_normalisee: -0.2687301577888914
    valeur_ponderee: -0.2687301577888914
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.0004702071437421296
    valeur_normalisee: -0.0069036543513623806
    valeur_ponderee: -0.0069036543513623806
    ts: '2026-08-27T05:23:00.757650+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-27T05:23:00.757650+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-26'
    valeur: -0.4086510585974624
    valeur_normalisee: 0.2043255292987312
    valeur_ponderee: 0.2043255292987312
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 86.36156
    valeur_normalisee: 0.20356739904664042
    valeur_ponderee: 0.20356739904664042
    ts: '2026-08-27T05:23:00.757650+00:00'
  usd_brl_sucre:
    valeur: 5.14904
    valeur_normalisee: 0.17760932615694477
    valeur_ponderee: 0.17760932615694477
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_sugar:
    valeur: 139023.0
    valeur_normalisee: 0.3151137091263304
    valeur_ponderee: 0.3151137091263304
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.17591623036649207
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.027447392497712775
    valeur_normalisee: 0.11812163452460449
    valeur_ponderee: 0.11812163452460449
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.001784121320249632
    valeur_normalisee: -0.12732785985501255
    valeur_ponderee: -0.12732785985501255
    ts: '2026-08-27T05:23:00.757650+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: structurel
    event_id: 7ae3213754cf
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 66.96666666666678
      7j: 66.96666666666678
      1m: 66.96666666666678
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
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: structurel
    event_id: 7ae3213754cf
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 66.96666666666678
      7j: 66.96666666666678
      1m: 66.96666666666678
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-27T05:23:00.757650+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5
    valeur_normalisee: -0.06160531303073942
    valeur_ponderee: -0.06160531303073942
    ts: '2026-08-27T05:23:00.757650+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.0016052833536339683
    valeur_normalisee: 0.12634452377483654
    valeur_ponderee: 0.12634452377483654
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.0014607378309980934
    valeur_normalisee: 0.12346843659912285
    valeur_ponderee: 0.12346843659912285
    ts: '2026-08-27T05:23:00.757650+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.009732605727975185
    valeur_normalisee: 0.4144252558941033
    valeur_ponderee: 0.4144252558941033
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_jpy_nets:
    valeur: -52476.0
    valeur_normalisee: -0.04638456092591132
    valeur_ponderee: -0.04638456092591132
    ts: '2026-08-27T05:23:00.757650+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.9699999999999998
    valeur_normalisee: 0.3078639571566479
    valeur_ponderee: 0.3078639571566479
    ts: '2026-08-27T05:23:00.757650+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-27T05:23:00.757650+00:00'
    nature: verbal
    event_id: df909aa662e6
    event_date: '2026-08-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 11.0
      7j: 11.0
      1m: 11.0
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-27T05:23:00.757650+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-27T05:23:00.757650+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-27T05:23:00.757650+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-27T05:23:00.757650+00:00'
  gap_rv_iv:
    valeur: -3.55925911256705
    ts: '2026-08-27T05:23:00.757650+00:00'
  cftc_cot_vix_nets:
    valeur: -89446.0
    valeur_normalisee: -0.7211456087175471
    valeur_ponderee: -0.7211456087175471
    ts: '2026-08-27T05:23:00.757650+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-27T05:23:00.757650+00:00'
    synthese_rationale: 'Malgré un repli de 20% sur 20j, les news du jour (27/08)
      sont massivement LONG : attaque de pétrolier à Ormuz, guerre commerciale US-Canada,
      et escalade Iran. Les signaux SHORT (cessez-le-feu, déminage) sont plus anciens
      (25-26/08) et contredits par les développements récents.'
    nature: structurel
    event_id: f2616112b48e
    event_date: '2026-08-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 494.53333333333046
      7j: 494.53333333333046
      1m: 494.53333333333046
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-27T05:23:00.757650+00:00'
```
