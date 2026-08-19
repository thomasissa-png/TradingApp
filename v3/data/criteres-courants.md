# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-19T05:23:09.602584+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.44
    valeur_normalisee: 0.6608315037266892
    valeur_ponderee: 0.6608315037266892
    ts: '2026-08-19T05:23:09.602584+00:00'
  mouvement_or_5j:
    valeur: -0.008290546570063673
    valeur_normalisee: -0.21908674343435414
    valeur_ponderee: -0.21908674343435414
    ts: '2026-08-19T05:23:09.602584+00:00'
  ratio_gold_silver:
    valeur: 69.19003077376263
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_silver:
    valeur: 21465.0
    valeur_normalisee: -0.2803992279605361
    valeur_ponderee: -0.2803992279605361
    ts: '2026-08-19T05:23:09.602584+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.018958155422715617
    valeur_normalisee: -0.00383274741811009
    valeur_ponderee: -0.00383274741811009
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_argent:
    valeur: 0.06286316062058517
    valeur_normalisee: 0.47882341929237027
    valeur_ponderee: 0.47882341929237027
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_argent:
    valeur: -0.04003439710998147
    valeur_normalisee: -0.2955256164004807
    valeur_ponderee: -0.2955256164004807
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_argent:
    valeur: -0.030354876165178957
    valeur_normalisee: -0.3957846318994916
    valeur_ponderee: -0.3957846318994916
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.19622893180525725
    valeur_normalisee: 0.09811446590262862
    valeur_ponderee: 0.09811446590262862
    ts: '2026-08-19T05:23:09.602584+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (fermeture
      d'Ormuz, tensions mer Noire, frappes sur Novorossiysk) malgré une prise de bénéfices
      isolée. Le prix est quasi stable sur 20j, mais la fraîcheur et la matérialité
      des drivers justifient de maintenir LONG.
    nature: structurel
    event_id: 2b47e84d9080
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 129.96666666666658
      7j: 129.96666666666658
      1m: 129.96666666666658
  cftc_cot_wheat:
    valeur: -31179.0
    valeur_normalisee: 0.1801460824733161
    valeur_ponderee: 0.1801460824733161
    ts: '2026-08-19T05:23:09.602584+00:00'
  meteo_australie_dryland:
    valeur: -0.0830358230734678
    valeur_normalisee: -0.0415179115367339
    valeur_ponderee: -0.0415179115367339
    ts: '2026-08-19T05:23:09.602584+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_ble:
    valeur: 0.005198495242323631
    valeur_normalisee: -0.18521006790132577
    valeur_ponderee: -0.18521006790132577
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_ble:
    valeur: 0.02076374177079865
    valeur_normalisee: 0.07636879705138531
    valeur_ponderee: 0.07636879705138531
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_ble:
    valeur: -0.011963393706971526
    valeur_normalisee: -0.30666764305689254
    valeur_ponderee: -0.30666764305689254
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-19T05:23:09.602584+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.019553371649989604
    valeur_normalisee: -0.7024167163165639
    valeur_ponderee: -0.7024167163165639
    ts: '2026-08-19T05:23:09.602584+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.019710631159572167
    valeur_normalisee: -0.6334295819092802
    valeur_ponderee: -0.6334295819092802
    ts: '2026-08-19T05:23:09.602584+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: 'Signaux contradictoires : news récentes LONG (accord US-Canada)
      contre SHORT (pétrole, Moyen-Orient) ; prix en baisse sur 5j malgré +1.75% sur
      20j, indiquant un arbitrage déjà effectué.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: -367.5333333333331
      7j: -367.5333333333331
      1m: -367.5333333333331
  rsi_14j_fchi:
    valeur: 48.184218362604724
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.017483948148588224
    valeur_normalisee: -0.05070483505543543
    valeur_ponderee: -0.05070483505543543
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.023588181122778495
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.016322553339748747
    valeur_normalisee: -0.8212226257690071
    valeur_ponderee: -0.8212226257690071
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-19T05:23:09.602584+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-18'
    valeur: -0.03261425247044984
    valeur_normalisee: 0.01630712623522492
    valeur_ponderee: 0.01630712623522492
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -15606.0
    valeur_normalisee: -0.5862223435839012
    valeur_ponderee: -0.5862223435839012
    ts: '2026-08-19T05:23:09.602584+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: structurel
    event_id: 7f3f7e335e72
    event_date: '2026-08-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 125.49999999999991
      7j: 125.49999999999991
      1m: 125.49999999999991
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
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée (El Niño, Super
      El Niño, menaces sur l''offre) et fraîcheur récente (jusqu''au 19/08), malgré
      quelques news SHORT plus anciennes sur conditions favorables en Afrique de l''Ouest.
      Le prix a déjà monté de +15.65% sur 20j, mais la persistance et l''intensité
      des '
    nature: structurel
    event_id: 7f3f7e335e72
    event_date: '2026-08-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 128.0666666666666
      7j: 128.0666666666666
      1m: 128.0666666666666
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.15647460826325288
    valeur_normalisee: 0.034896742624531324
    valeur_ponderee: 0.034896742624531324
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.034359423111795184
    valeur_normalisee: -0.05619136050265296
    valeur_ponderee: -0.05619136050265296
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.024904893821399376
    valeur_normalisee: 0.04846648553880351
    valeur_ponderee: 0.04846648553880351
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.41323086128874437
    valeur_normalisee: 0.20661543064437218
    valeur_ponderee: 0.20661543064437218
    ts: '2026-08-19T05:23:09.602584+00:00'
  usd_brl:
    valeur: 5.21538
    valeur_normalisee: 0.8328959404256008
    valeur_ponderee: 0.8328959404256008
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_coffee:
    valeur: 27282.0
    valeur_normalisee: -0.16470293830600344
    valeur_ponderee: -0.16470293830600344
    ts: '2026-08-19T05:23:09.602584+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: Dominance de news LONG récentes (El Niño, risques d'offre)
      et prix en hausse de 6.55% sur 5j confirment le biais haussier. Les news SHORT
      sur la récolte brésilienne sont plus anciennes et moins fraîches.
    nature: structurel
    event_id: f2fd02e28b8a
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 114.63333333333357
      7j: 114.63333333333357
      1m: 114.63333333333357
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported+keyword:pourrait
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-19T05:23:09.602584+00:00'
  meteo_vietnam_robusta:
    valeur: 0.46521276370885567
    valeur_normalisee: 0.23260638185442783
    valeur_ponderee: 0.23260638185442783
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.02501962406244429
    valeur_normalisee: -0.2800019923515223
    valeur_ponderee: -0.2800019923515223
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.048556969752972634
    valeur_normalisee: 0.20628488204766351
    valeur_ponderee: 0.20628488204766351
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.05838998046229338
    valeur_normalisee: 0.5536198280536859
    valeur_ponderee: 0.5536198280536859
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.050544977338137995
    valeur_normalisee: 0.025272488669068997
    valeur_ponderee: 0.025272488669068997
    ts: '2026-08-19T05:23:09.602584+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.8102339088575772
    valeur_normalisee: 0.4051169544287886
    valeur_ponderee: 0.4051169544287886
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_cotton:
    valeur: 110304.0
    valeur_normalisee: 0.8731439466661239
    valeur_ponderee: 0.8731439466661239
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_coton:
    valeur: 0.06890993350795882
    valeur_normalisee: 0.5826106602349407
    valeur_ponderee: 0.5826106602349407
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_coton:
    valeur: 0.017453011123897078
    valeur_normalisee: 0.21488835913534943
    valeur_ponderee: 0.21488835913534943
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_coton:
    valeur: 0.02690669763840492
    valeur_normalisee: 0.5314026772272242
    valeur_ponderee: 0.5314026772272242
    ts: '2026-08-19T05:23:09.602584+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '12.22'
    p2_shadow_contrib_exclu:
      24h: 71.63333333333341
      7j: 71.63333333333341
      1m: 71.63333333333341
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: Les news récentes (18-17 août) signalent un rebond de l'offre
      au Chili et un ralentissement de la demande chinoise, dominant les signaux LONG
      plus anciens. Le prix a déjà baissé de 2.33% sur 5j, confirmant la pression
      baissière.
    nature: structurel
    event_id: 5e294718ef14
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 45.40000000000001
      7j: 45.40000000000001
      1m: 45.40000000000001
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_copper_nets:
    valeur: 80503.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-19T05:23:09.602584+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: structurel
    event_id: 33d84a40551b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '13.22'
    p2_shadow_contrib_exclu:
      24h: 57.433333333333366
      7j: 57.433333333333366
      1m: 57.433333333333366
  ratio_cuivre_or:
    valeur: 0.0014837759992403067
    valeur_normalisee: -0.6339214218034964
    valeur_ponderee: -0.6339214218034964
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.0052717507989489265
    valeur_normalisee: -0.19919047799332598
    valeur_ponderee: -0.19919047799332598
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.021981126058128297
    valeur_normalisee: -0.5239772214131819
    valeur_ponderee: -0.5239772214131819
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.024628139478175992
    valeur_normalisee: -0.6781688822660523
    valeur_ponderee: -0.6781688822660523
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4539581149000003
    valeur_normalisee: -0.640225682509169
    valeur_ponderee: -0.640225682509169
    ts: '2026-08-19T05:23:09.602584+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7499999999999996
    valeur_normalisee: 0.8097472575549374
    valeur_ponderee: 0.8097472575549374
    ts: '2026-08-19T05:23:09.602584+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.26554
    valeur_normalisee: -0.4458231144649231
    valeur_ponderee: -0.4458231144649231
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_eur_nets:
    valeur: -79915.0
    valeur_normalisee: -0.9298361009982374
    valeur_ponderee: -0.9298361009982374
    ts: '2026-08-19T05:23:09.602584+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.005144175717408661
    valeur_normalisee: 0.24525466763832168
    valeur_ponderee: 0.24525466763832168
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.0053971036122415494
    valeur_normalisee: 0.37869556854185016
    valeur_ponderee: 0.37869556854185016
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.0017550533432468818
    valeur_normalisee: 0.16337335498358568
    valeur_ponderee: 0.16337335498358568
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.44
    valeur_normalisee: 0.6608315037266892
    valeur_ponderee: 0.6608315037266892
    ts: '2026-08-19T05:23:09.602584+00:00'
  sox_trend_5j:
    valeur: 531.39001
    valeur_normalisee: -0.4151038838356881
    valeur_ponderee: -0.4151038838356881
    ts: '2026-08-19T05:23:09.602584+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1708826334004734
    valeur_normalisee: 0.7090742042137382
    valeur_ponderee: 0.7090742042137382
    ts: '2026-08-19T05:23:09.602584+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: Vente massive sur les semi-conducteurs (KOSPI -5%) et hausse
      des rendements obligataires (30 ans >5.33%) dominent, malgré des nouvelles positives
      sur Nvidia et l'IA. Le prix a légèrement monté sur 20j, mais la fraîcheur des
      news SHORT (19/08) et leur matérialité élevée suggèrent un biais baissier.
    nature: verbal
    event_id: 76665f95fd4c
    event_date: '2026-08-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 84.50000000000004
      7j: 84.50000000000004
      1m: 84.50000000000004
  flux_etf_qqq_5j:
    valeur: -0.001308372171920591
    valeur_normalisee: -0.05169706279016393
    valeur_ponderee: -0.05169706279016393
    ts: '2026-08-19T05:23:09.602584+00:00'
  spread_nasdaq_russell2000:
    valeur: 417.28
    valeur_normalisee: -0.12662368101718813
    valeur_ponderee: -0.12662368101718813
    ts: '2026-08-19T05:23:09.602584+00:00'
  rsi_14j_ixic:
    valeur: 52.13200399965984
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.01204570060985799
    valeur_normalisee: 0.043250295391686455
    valeur_ponderee: 0.043250295391686455
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.007634563958062168
    valeur_normalisee: -0.15245324692154807
    valeur_ponderee: -0.15245324692154807
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.01988880415913563
    valeur_normalisee: -0.42051445984508395
    valeur_ponderee: -0.42051445984508395
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-19T05:23:09.602584+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.44
    valeur_normalisee: 0.6608315037266892
    valeur_ponderee: 0.6608315037266892
    ts: '2026-08-19T05:23:09.602584+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_nets:
    valeur: 214856.0
    valeur_normalisee: 0.14816439944873105
    valeur_ponderee: 0.14816439944873105
    ts: '2026-08-19T05:23:09.602584+00:00'
  flux_etf_or_5j:
    valeur: -0.006010574770814459
    valeur_normalisee: -0.015838926461344417
    valeur_ponderee: -0.015838926461344417
    ts: '2026-08-19T05:23:09.602584+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: 'Les news récentes (18-19 août) sont dominées par des tensions
      géopolitiques élevées (attaque de navire à Ormuz, menace d''offensive iranienne,
      expiration du cessez-le-feu) et des achats de banques centrales, soutenant l''or.
      Malgré quelques signaux baissiers (rendements, pétrole, cassure de support), '
    nature: structurel
    event_id: 75c125c4d8d5
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 415.83333333333235
      7j: 415.83333333333235
      1m: 415.83333333333235
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
    ts: '2026-08-19T05:23:09.602584+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_or:
    valeur: 0.05770205481833912
    valeur_normalisee: 0.5880858112436119
    valeur_ponderee: 0.5880858112436119
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_or:
    valeur: -0.015597414109975283
    valeur_normalisee: -0.3193742440453082
    valeur_ponderee: -0.3193742440453082
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_or:
    valeur: -0.008060496465577827
    valeur_normalisee: -0.2642251072837318
    valeur_ponderee: -0.2642251072837318
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-19T05:23:09.602584+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-19T05:23:09.602584+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-08-14'
    valeur: 424410.0
    valeur_normalisee: -0.13812033584105132
    valeur_ponderee: -0.13812033584105132
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: 'Signal dominant clairement LONG : attaque de navire à Ormuz,
      expiration du cessez-le-feu, posture offensive iranienne, crack diesel record
      et baisse des stocks. Malgré -3.8% sur 20j, la fraîcheur et la matérialité élevée
      des news (≤48h) justifient de suivre le signal.'
    nature: structurel
    event_id: 75c125c4d8d5
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 394.1333333333317
      7j: 394.1333333333317
      1m: 394.1333333333317
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 23853.0
    valeur_normalisee: -0.045557257567997375
    valeur_ponderee: -0.045557257567997375
    ts: '2026-08-19T05:23:09.602584+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: structurel
    event_id: 75c125c4d8d5
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 367.8999999999981
      7j: 367.8999999999981
      1m: 367.8999999999981
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  cushing_stocks:
    valeur: 22566.0
    valeur_normalisee: -0.15882864718542616
    valeur_ponderee: -0.15882864718542616
    ts: '2026-08-19T05:23:09.602584+00:00'
  spread_brent_wti:
    valeur: 4.813639999999992
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.038031644233413875
    valeur_normalisee: 0.027852940475880744
    valeur_ponderee: 0.027852940475880744
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.038659335252559934
    valeur_normalisee: 0.24355899309288406
    valeur_ponderee: 0.24355899309288406
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.034368669028854715
    valeur_normalisee: 0.27709803159894136
    valeur_ponderee: 0.27709803159894136
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-19T05:23:09.602584+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-19T05:23:09.602584+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.0
    valeur_normalisee: -0.05291434892196025
    valeur_ponderee: -0.05291434892196025
    ts: '2026-08-19T05:23:09.602584+00:00'
  hy_credit_spread:
    valeur: 2.7
    valeur_normalisee: -0.31828723349765287
    valeur_ponderee: -0.31828723349765287
    ts: '2026-08-19T05:23:09.602584+00:00'
  breadth_sp_ma50:
    valeur: 0.2863899760715359
    valeur_normalisee: 0.2292253620747496
    valeur_ponderee: 0.2292253620747496
    ts: '2026-08-19T05:23:09.602584+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.004036012769933484
    valeur_normalisee: -0.20615424877100647
    valeur_ponderee: -0.20615424877100647
    ts: '2026-08-19T05:23:09.602584+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.06
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-19T05:23:09.602584+00:00'
  rsi_14j_gspc:
    valeur: 56.466820732622
    ts: '2026-08-19T05:23:09.602584+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.44
    valeur_normalisee: 0.6608315037266892
    valeur_ponderee: 0.6608315037266892
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.02561872458362946
    valeur_normalisee: 0.2681722099227243
    valeur_ponderee: 0.2681722099227243
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.007513643437994322
    valeur_normalisee: -0.3095414726126285
    valeur_ponderee: -0.3095414726126285
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.013408224919010614
    valeur_normalisee: -0.5482168214262729
    valeur_ponderee: -0.5482168214262729
    ts: '2026-08-19T05:23:09.602584+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-19T05:23:09.602584+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-19T05:23:09.602584+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-18'
    valeur: -0.2777963714867588
    valeur_normalisee: 0.1388981857433794
    valeur_ponderee: 0.1388981857433794
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 90.30957
    valeur_normalisee: 0.41190566944056195
    valeur_ponderee: 0.41190566944056195
    ts: '2026-08-19T05:23:09.602584+00:00'
  usd_brl_sucre:
    valeur: 5.21538
    valeur_normalisee: 0.8328959404256008
    valeur_ponderee: 0.8328959404256008
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_sugar:
    valeur: 80425.0
    valeur_normalisee: 0.08231776585326993
    valeur_ponderee: 0.08231776585326993
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.14081632653061216
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.04976525821596245
    valeur_normalisee: 0.44589802442007553
    valeur_ponderee: 0.44589802442007553
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.03136531365313644
    valeur_normalisee: 0.5055656820099689
    valeur_ponderee: 0.5055656820099689
    ts: '2026-08-19T05:23:09.602584+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: structurel
    event_id: bcc962468c40
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 56.83333333333334
      7j: 56.83333333333334
      1m: 56.83333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported+keyword:envisage
  exports_bresil_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: structurel
    event_id: bcc962468c40
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 56.83333333333334
      7j: 56.83333333333334
      1m: 56.83333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported+keyword:envisage
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-19T05:23:09.602584+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5200000000000005
    valeur_normalisee: 0.15757747655274348
    valeur_ponderee: 0.15757747655274348
    ts: '2026-08-19T05:23:09.602584+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.0010715571084617403
    valeur_normalisee: -0.004757811874919391
    valeur_ponderee: -0.004757811874919391
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.00037164218834906393
    valeur_normalisee: 0.010104421230537043
    valeur_ponderee: 0.010104421230537043
    ts: '2026-08-19T05:23:09.602584+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.0017754354348480383
    valeur_normalisee: 0.05978067395481973
    valeur_ponderee: 0.05978067395481973
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_jpy_nets:
    valeur: -40040.0
    valeur_normalisee: 0.031499248803131374
    valeur_ponderee: 0.031499248803131374
    ts: '2026-08-19T05:23:09.602584+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.05
    valeur_normalisee: 0.8260184180488009
    valeur_ponderee: 0.8260184180488009
    ts: '2026-08-19T05:23:09.602584+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-08-19T05:23:09.602584+00:00'
    nature: verbal
    p2_shadow_contrib_exclu:
      24h: 5.833333333333345
      7j: 5.833333333333345
      1m: 5.833333333333345
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-19T05:23:09.602584+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-19T05:23:09.602584+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-19T05:23:09.602584+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-19T05:23:09.602584+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-19T05:23:09.602584+00:00'
  gap_rv_iv:
    valeur: -1.6421333450495226
    ts: '2026-08-19T05:23:09.602584+00:00'
  cftc_cot_vix_nets:
    valeur: -74934.0
    valeur_normalisee: -0.44221335910303994
    valeur_ponderee: -0.44221335910303994
    ts: '2026-08-19T05:23:09.602584+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-19T05:23:09.602584+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (attaque
      de navire, expiration du cessez-le-feu, menaces iraniennes) malgré le repli
      récent du VIX, qui semble déjà avoir intégré une partie du risque. La vente
      massive sur les semi-conducteurs et les tensions géopolitiques soutiennent une
      hauss
    nature: structurel
    event_id: 75c125c4d8d5
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 428.56666666666456
      7j: 428.56666666666456
      1m: 428.56666666666456
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-19T05:23:09.602584+00:00'
```
