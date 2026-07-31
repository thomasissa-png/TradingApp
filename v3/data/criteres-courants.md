# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-31T05:23:03.847853+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.787268714566446
    valeur_ponderee: 0.787268714566446
    ts: '2026-07-31T05:23:03.847853+00:00'
  mouvement_or_5j:
    valeur: 0.006111352546944726
    valeur_normalisee: 0.3017943586456864
    valeur_ponderee: 0.3017943586456864
    ts: '2026-07-31T05:23:03.847853+00:00'
  ratio_gold_silver:
    valeur: 69.62289184866346
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_silver:
    valeur: 20569.0
    valeur_normalisee: -0.303970612481078
    valeur_ponderee: -0.303970612481078
    ts: '2026-07-31T05:23:03.847853+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.027660372115628773
    valeur_normalisee: 0.3104458240196233
    valeur_ponderee: 0.3104458240196233
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_argent:
    valeur: -0.019199920999688702
    valeur_normalisee: 0.7405824303293304
    valeur_ponderee: 0.7405824303293304
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_argent:
    valeur: 0.006638895092161423
    valeur_normalisee: 0.29620866486364666
    valeur_ponderee: 0.29620866486364666
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_argent:
    valeur: 0.02603868095756523
    valeur_normalisee: 0.45005810802726276
    valeur_ponderee: 0.45005810802726276
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.27986358735619027
    valeur_normalisee: 0.13993179367809513
    valeur_ponderee: 0.13993179367809513
    ts: '2026-07-31T05:23:03.847853+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: 'Signal dominant clairement haussier : l''USDA confirme une
      baisse de production et de stocks mondiaux (matérialité high, confirmé) et les
      risques d''exportation en mer Noire restent élevés, soutenant les prix. Malgré
      le repli récent de -3.22% sur 5j, la fraîcheur et la matérialité des news justifient '
    nature: structurel
    event_id: fd630a45bbcc
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 74.23333333333338
      7j: 74.23333333333338
      1m: 74.23333333333338
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -14250.0
    valeur_normalisee: 0.40842367936126867
    valeur_ponderee: 0.40842367936126867
    ts: '2026-07-31T05:23:03.847853+00:00'
  meteo_australie_dryland:
    valeur: -0.01775075627121474
    valeur_normalisee: -0.00887537813560737
    valeur_ponderee: -0.00887537813560737
    ts: '2026-07-31T05:23:03.847853+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_ble:
    valeur: 0.03977531064987483
    valeur_normalisee: 0.11087555029973341
    valeur_ponderee: 0.11087555029973341
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_ble:
    valeur: -0.03219284443525505
    valeur_normalisee: -0.43596829597753184
    valeur_ponderee: -0.43596829597753184
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_ble:
    valeur: -0.012018014157318846
    valeur_normalisee: -0.3046574456201112
    valeur_ponderee: -0.3046574456201112
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-07-31T05:23:03.847853+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.017723393725422643
    valeur_normalisee: 0.4747260046263874
    valeur_ponderee: 0.4747260046263874
    ts: '2026-07-31T05:23:03.847853+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.039829939583799545
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité high (frappes US-Iran,
      tarifs Trump, crise énergétique) malgré des PIB zone euro légèrement positifs.
      Le prix a légèrement monté sur 5j, mais la fraîcheur et la gravité des risques
      géopolitiques et commerciaux justifient un biais baissier modéré.
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -133.86666666666682
      7j: -133.86666666666682
      1m: -133.86666666666682
    sign_conflict: true
    sign_conflict_details:
    - event_id: ad154c825d37
      asset: CAC40
      rule_name: fed_actions
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: bce
      matched_surprise: hausse de taux
      surprise_polarity: up
      title: Publication de l'estimation flash du PIB de la zone euro jeudi, pouvant
        influencer la décision de hausse de taux de la BCE en septembre.
  rsi_14j_fchi:
    valeur: 58.246321118701104
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.0012719147637634265
    valeur_normalisee: -0.13431485684395383
    valeur_ponderee: -0.13431485684395383
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.014647609047159671
    valeur_normalisee: 0.35282848565752895
    valeur_ponderee: 0.35282848565752895
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.009466989775329449
    valeur_normalisee: 0.3174451220340991
    valeur_ponderee: 0.3174451220340991
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -13050.0
    valeur_normalisee: -0.5555916820879753
    valeur_ponderee: -0.5555916820879753
    ts: '2026-07-31T05:23:03.847853+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: structurel
    event_id: 30bb22bc65bf
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 91.20000000000022
      7j: 91.20000000000022
      1m: 91.20000000000022
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
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Les news récentes (30/07) montrent une crise au Ghana et une
      baisse de production de 16%, soutenues par des réductions de surplus (StoneX,
      El Niño), dominant les signaux baissiers plus anciens sur l'abondance de l'offre.
      Malgré la baisse de prix de -15.66% sur 20j, la fraîcheur et la matérialité
      éle
    nature: structurel
    event_id: 30bb22bc65bf
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 92.13333333333357
      7j: 92.13333333333357
      1m: 92.13333333333357
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: -0.1565762694851569
    valeur_normalisee: -0.7950220799371019
    valeur_ponderee: -0.7950220799371019
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.039793655411928586
    valeur_normalisee: -0.3706799877168119
    valeur_ponderee: -0.3706799877168119
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.016024780765415803
    valeur_normalisee: -0.25610029634084275
    valeur_ponderee: -0.25610029634084275
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
  meteo_ci_ghana_precip_30j:
    valeur: 0.12311321174260538
    valeur_normalisee: 0.06155660587130269
    valeur_ponderee: 0.06155660587130269
    ts: '2026-07-31T05:23:03.847853+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.38882880204236286
    valeur_normalisee: 0.19441440102118143
    valeur_ponderee: 0.19441440102118143
    ts: '2026-07-31T05:23:03.847853+00:00'
  usd_brl:
    valeur: 5.07315
    valeur_normalisee: -0.5826248928102342
    valeur_ponderee: -0.5826248928102342
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_coffee:
    valeur: 26034.0
    valeur_normalisee: -0.19563028321574708
    valeur_ponderee: -0.19563028321574708
    ts: '2026-07-31T05:23:03.847853+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Deux news SHORT récentes (29/07) sur la chute des prix du
      café arabica, renforcées par le tarif américain de 25% sur les exportations
      brésiliennes (22/07, matérialité high), dominent les signaux LONG faibles et
      dispersés sur les importations d'huile comestible en Inde. Le mouvement de prix
      récent (-
    nature: ponctuel
    event_id: 0e0e0ba114c1
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 101.93333333333354
      7j: 101.93333333333354
      1m: 101.93333333333354
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-31T05:23:03.847853+00:00'
  meteo_vietnam_robusta:
    valeur: 0.3538635108669549
    valeur_normalisee: 0.17693175543347744
    valeur_ponderee: 0.17693175543347744
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.0339918763273559
    valeur_normalisee: -0.4281370716660876
    valeur_ponderee: -0.4281370716660876
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.028271314020318128
    valeur_normalisee: 0.033808296671848
    valeur_ponderee: 0.033808296671848
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.05155008385445636
    valeur_normalisee: -0.692608270790051
    valeur_ponderee: -0.692608270790051
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.36471424515122663
    valeur_normalisee: 0.18235712257561332
    valeur_ponderee: 0.18235712257561332
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_cotton:
    valeur: 100360.0
    valeur_normalisee: 0.7692072556094062
    valeur_ponderee: 0.7692072556094062
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_coton:
    valeur: 0.048978741142142734
    valeur_normalisee: 0.35824631209470076
    valeur_ponderee: 0.35824631209470076
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_coton:
    valeur: 0.014104372355430161
    valeur_normalisee: 0.217003851950522
    valeur_ponderee: 0.217003851950522
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_coton:
    valeur: 0.003189156866653331
    valeur_normalisee: 0.11754057535877277
    valeur_ponderee: 0.11754057535877277
    ts: '2026-07-31T05:23:03.847853+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  demande_chine_coton:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: structurel
    event_id: f37165710bf1
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '9.22'
    p2_shadow_contrib_exclu:
      24h: 40.59999999999996
      7j: 40.59999999999996
      1m: 40.59999999999996
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.6028819546829338
    valeur_normalisee: 0.3014409773414669
    valeur_ponderee: 0.3014409773414669
    ts: '2026-07-31T05:23:03.847853+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: 'Les news récentes sont mitigées : le PMI chinois en contraction
      (31/07) et la décélération de l''activité manufacturière pèsent, mais les tensions
      sur l''offre et la demande IA soutiennent le prix. Le prix a déjà monté de +4.15%
      sur 20j, suggérant que le marché a intégré les facteurs haussiers, tandis'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 41.2
      7j: 41.2
      1m: 41.2
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_copper_nets:
    valeur: 74822.0
    valeur_normalisee: 0.9967771915326051
    valeur_ponderee: 0.9967771915326051
    ts: '2026-07-31T05:23:03.847853+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: ponctuel
    event_id: f75852b49d05
    event_date: '2026-07-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 38.566666666666656
      7j: 38.566666666666656
      1m: 38.566666666666656
  ratio_cuivre_or:
    valeur: 0.0015906955142401692
    valeur_normalisee: 0.97824556302149
    valeur_ponderee: 0.97824556302149
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.04146070282004022
    valeur_normalisee: 0.6792165877478881
    valeur_ponderee: 0.6792165877478881
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.029742283250473678
    valeur_normalisee: 0.5969733490378519
    valeur_ponderee: 0.5969733490378519
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.030073994849082686
    valeur_normalisee: 0.6707878596156068
    valeur_ponderee: 0.6707878596156068
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4880190158
    valeur_normalisee: -0.12114733153881607
    valeur_ponderee: -0.12114733153881607
    ts: '2026-07-31T05:23:03.847853+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6999999999999997
    valeur_normalisee: 0.90651729483311
    valeur_ponderee: 0.90651729483311
    ts: '2026-07-31T05:23:03.847853+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  usd_jpy_proxy_risk:
    valeur: 160.68904
    valeur_normalisee: -0.42119269447850566
    valeur_ponderee: -0.42119269447850566
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_eur_nets:
    valeur: -65177.0
    valeur_normalisee: -0.8513400297335095
    valeur_ponderee: -0.8513400297335095
    ts: '2026-07-31T05:23:03.847853+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.00772491591928226
    valeur_normalisee: 0.9813656699651556
    valeur_ponderee: 0.9813656699651556
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.011739050148167118
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.010468445365605206
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.787268714566446
    valeur_ponderee: 0.787268714566446
    ts: '2026-07-31T05:23:03.847853+00:00'
  sox_trend_5j:
    valeur: 504.53
    valeur_normalisee: -0.6224588987129324
    valeur_ponderee: -0.6224588987129324
    ts: '2026-07-31T05:23:03.847853+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17077024607958813
    valeur_normalisee: 0.859897701397343
    valeur_ponderee: 0.859897701397343
    ts: '2026-07-31T05:23:03.847853+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Escalade militaire US-Iran (frappes multiples, menaces de
      représailles) et resserrement des conditions financières dominent, malgré des
      nouvelles positives sur les dépenses IA. Le prix a déjà baissé de 5.74% sur
      20j, mais la fraîcheur et la matérialité élevée des news SHORT confirment la
      tendance.
    nature: ponctuel
    event_id: 322f6c6c8df1
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 77.6333333333334
      7j: 77.6333333333334
      1m: 77.6333333333334
  flux_etf_qqq_5j:
    valeur: -0.012153924731084897
    valeur_normalisee: -0.24506554035578587
    valeur_ponderee: -0.24506554035578587
    ts: '2026-07-31T05:23:03.847853+00:00'
  spread_nasdaq_russell2000:
    valeur: 390.95999
    valeur_normalisee: -0.9113065644773305
    valeur_ponderee: -0.9113065644773305
    ts: '2026-07-31T05:23:03.847853+00:00'
  rsi_14j_ixic:
    valeur: 43.36333852838083
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.05739342657289814
    valeur_normalisee: -0.662263171070855
    valeur_ponderee: -0.662263171070855
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.03585480496444726
    valeur_normalisee: -0.5742684521534956
    valeur_ponderee: -0.5742684521534956
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.0020963906643991503
    valeur_normalisee: 0.03452443874569601
    valeur_ponderee: 0.03452443874569601
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.787268714566446
    valeur_ponderee: 0.787268714566446
    ts: '2026-07-31T05:23:03.847853+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_nets:
    valeur: 176195.0
    valeur_normalisee: -0.19033380690269922
    valeur_ponderee: -0.19033380690269922
    ts: '2026-07-31T05:23:03.847853+00:00'
  flux_etf_or_5j:
    valeur: 0.015180905878038997
    valeur_normalisee: 0.4636883814573612
    valeur_ponderee: 0.4636883814573612
    ts: '2026-07-31T05:23:03.847853+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Escalade US-Iran (frappes multiples, conflit élargi) et achats
      records des banques centrales dominent, malgré quelques signaux SHORT (désarmement
      Hamas, rendements). Le prix a légèrement baissé sur 20j mais rebondit sur 5j,
      cohérent avec un biais haussier persistant.
    nature: structurel
    event_id: 8551f1ea61b4
    event_date: '2026-07-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 199.6333333333332
      7j: 199.6333333333332
      1m: 199.6333333333332
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
    ts: '2026-07-31T05:23:03.847853+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_or:
    valeur: -0.007474728832431943
    valeur_normalisee: 0.5121750053471416
    valeur_ponderee: 0.5121750053471416
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_or:
    valeur: 0.006741807827561397
    valeur_normalisee: 0.3502775222943181
    valeur_ponderee: 0.3502775222943181
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_or:
    valeur: 0.012962137867696955
    valeur_normalisee: 0.4354954302756532
    valeur_ponderee: 0.4354954302756532
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
petrole:
  eia_crude_surprise:
    valeur: 404508.0
    valeur_normalisee: -0.7758900959893141
    valeur_ponderee: -0.7758900959893141
    ts: '2026-07-31T05:23:03.847853+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Escalade US-Iran et frappes sur Suez dominent, malgré des
      signaux de désescalade récents. Le repli de 8.93% sur 5j est probablement un
      retracement après +17.28% sur 20j, mais les news fraîches à haute matérialité
      (frappe sur port égyptien, effondrement des exportations diesel) soutiennent
      un biais h
    nature: structurel
    event_id: 8551f1ea61b4
    event_date: '2026-07-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 181.86666666666676
      7j: 181.86666666666676
      1m: 181.86666666666676
    sign_conflict: true
    sign_conflict_details:
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
  cftc_cot_crude_nets:
    valeur: 42761.0
    valeur_normalisee: 0.3587204635040612
    valeur_ponderee: 0.3587204635040612
    ts: '2026-07-31T05:23:03.847853+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 174.86666666666716
      7j: 174.86666666666716
      1m: 174.86666666666716
    sign_conflict: true
    sign_conflict_details:
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
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  cushing_stocks:
    valeur: 18599.0
    valeur_normalisee: -0.8001382957591842
    valeur_ponderee: -0.8001382957591842
    ts: '2026-07-31T05:23:03.847853+00:00'
  spread_brent_wti:
    valeur: 3.2050700000000063
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.17275879675082106
    valeur_normalisee: 0.6490457100236185
    valeur_ponderee: 0.6490457100236185
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.0959580519723161
    valeur_normalisee: -0.4074922184961548
    valeur_ponderee: -0.4074922184961548
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.03621122576079716
    valeur_normalisee: 0.36006086778180274
    valeur_ponderee: 0.36006086778180274
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-31T05:23:03.847853+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.0
    valeur_normalisee: -0.1310737276837411
    valeur_ponderee: -0.1310737276837411
    ts: '2026-07-31T05:23:03.847853+00:00'
  hy_credit_spread:
    valeur: 2.87
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  breadth_sp_ma50:
    valeur: 0.29039086410764603
    valeur_normalisee: 0.7450998915914876
    valeur_ponderee: 0.7450998915914876
    ts: '2026-07-31T05:23:03.847853+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.0047549514312899
    valeur_normalisee: 0.05199574138032489
    valeur_ponderee: 0.05199574138032489
    ts: '2026-07-31T05:23:03.847853+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.62
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  rsi_14j_gspc:
    valeur: 49.42959359227667
    ts: '2026-07-31T05:23:03.847853+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.787268714566446
    valeur_ponderee: 0.787268714566446
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_sp500:
    valeur: -0.005457533181485452
    valeur_normalisee: -0.4126543496998598
    valeur_ponderee: -0.4126543496998598
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.00880690347970392
    valeur_normalisee: -0.3501675319442099
    valeur_ponderee: -0.3501675319442099
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.0035178028454172505
    valeur_normalisee: 0.08568990580474939
    valeur_ponderee: 0.08568990580474939
    ts: '2026-07-31T05:23:03.847853+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-07-31T05:23:03.847853+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-30'
    valeur: -0.1817535949708365
    valeur_normalisee: 0.09087679748541826
    valeur_ponderee: 0.09087679748541826
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 84.87144
    valeur_normalisee: -0.14130819827850535
    valeur_ponderee: -0.14130819827850535
    ts: '2026-07-31T05:23:03.847853+00:00'
  usd_brl_sucre:
    valeur: 5.07315
    valeur_normalisee: -0.5826248928102342
    valeur_ponderee: -0.5826248928102342
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_sugar:
    valeur: -47496.0
    valeur_normalisee: -0.431259358767976
    valeur_ponderee: -0.431259358767976
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_sucre:
    valeur: -0.03248730964467006
    valeur_normalisee: -0.4095690355306676
    valeur_ponderee: -0.4095690355306676
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.027551020408163374
    valeur_normalisee: -0.4182299735571662
    valeur_ponderee: -0.4182299735571662
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.008324661810613976
    valeur_normalisee: -0.134155249061371
    valeur_ponderee: -0.134155249061371
    ts: '2026-07-31T05:23:03.847853+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 36.933333333333294
      7j: 36.933333333333294
      1m: 36.933333333333294
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
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 36.933333333333294
      7j: 36.933333333333294
      1m: 36.933333333333294
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-31T05:23:03.847853+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5499999999999998
    valeur_normalisee: 0.48736055784848725
    valeur_ponderee: 0.48736055784848725
    ts: '2026-07-31T05:23:03.847853+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.019263437868106026
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.01935686156194738
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.006096181056299055
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_jpy_nets:
    valeur: -157406.0
    valeur_normalisee: -0.6920714340123324
    valeur_ponderee: -0.6920714340123324
    ts: '2026-07-31T05:23:03.847853+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0
    valeur_normalisee: 0.8908924839112319
    valeur_ponderee: 0.8908924839112319
    ts: '2026-07-31T05:23:03.847853+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.4
    materiality: high
    reliability: rumor
    source_track: ia
    ts: '2026-07-31T05:23:03.847853+00:00'
    nature: verbal
    event_id: 71dfa4f146f5
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 20.59999999999998
      7j: 20.59999999999998
      1m: 20.59999999999998
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-31T05:23:03.847853+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-31T05:23:03.847853+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-31T05:23:03.847853+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-31T05:23:03.847853+00:00'
  gap_rv_iv:
    valeur: -2.839336139520638
    ts: '2026-07-31T05:23:03.847853+00:00'
  cftc_cot_vix_nets:
    valeur: -76861.0
    valeur_normalisee: -0.47810632841843353
    valeur_ponderee: -0.47810632841843353
    ts: '2026-07-31T05:23:03.847853+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-31T05:23:03.847853+00:00'
    synthese_rationale: Escalade majeure US-Iran avec frappes massives et attaques
      de missiles, soutenue par de nombreuses news à matérialité élevée et fraîches
      (30-31/07). Malgré la baisse récente du VIX, la fraîcheur et la matérialité
      des news suggèrent un regain de volatilité imminent.
    nature: structurel
    event_id: 8551f1ea61b4
    event_date: '2026-07-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 224.73333333333315
      7j: 224.73333333333315
      1m: 224.73333333333315
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-31T05:23:03.847853+00:00'
```
