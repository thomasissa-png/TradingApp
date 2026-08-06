# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-06T05:23:37.356353+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.4
    valeur_normalisee: 0.6556416159119935
    valeur_ponderee: 0.6556416159119935
    ts: '2026-08-06T05:23:37.356353+00:00'
  mouvement_or_5j:
    valeur: 0.05253789472309944
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  ratio_gold_silver:
    valeur: 68.6933591416543
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_silver:
    valeur: 20236.0
    valeur_normalisee: -0.31454313983426346
    valeur_ponderee: -0.31454313983426346
    ts: '2026-08-06T05:23:37.356353+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.08305968707745803
    valeur_normalisee: 0.6525699464384846
    valeur_ponderee: 0.6525699464384846
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_argent:
    valeur: 0.10712616152051191
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_argent:
    valeur: 0.04956677477948945
    valeur_normalisee: 0.5873122056672612
    valeur_ponderee: 0.5873122056672612
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_argent:
    valeur: 0.06430529820512887
    valeur_normalisee: 0.8358402381459396
    valeur_ponderee: 0.8358402381459396
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.18073137073279208
    valeur_normalisee: 0.09036568536639604
    valeur_ponderee: 0.09036568536639604
    ts: '2026-08-06T05:23:37.356353+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: Signal dominant LONG via sécheresse extrême, tensions mer
      Noire et baisse prévue des stocks USDA, malgré quelques news SHORT anciennes.
      Le prix a baissé de 6.23% sur 20j, mais les news LONG récentes (≤48h) à matérialité
      high suggèrent un changement de régime, d'où conviction medium.
    nature: structurel
    event_id: 55b523467a1b
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 86.40000000000008
      7j: 86.40000000000008
      1m: 86.40000000000008
  cftc_cot_wheat:
    valeur: -5384.0
    valeur_normalisee: 0.5293592418323769
    valeur_ponderee: 0.5293592418323769
    ts: '2026-08-06T05:23:37.356353+00:00'
  meteo_australie_dryland:
    valeur: -0.08470876690229434
    valeur_normalisee: -0.04235438345114717
    valeur_ponderee: -0.04235438345114717
    ts: '2026-08-06T05:23:37.356353+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_ble:
    valeur: -0.06227319126769959
    valeur_normalisee: -0.5021367565592436
    valeur_ponderee: -0.5021367565592436
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_ble:
    valeur: -0.031816373607197024
    valeur_normalisee: -0.4596445972936872
    valeur_ponderee: -0.4596445972936872
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_ble:
    valeur: -0.01458961997327246
    valeur_normalisee: -0.3778114224304043
    valeur_ponderee: -0.3778114224304043
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-06T05:23:37.356353+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.02424294671411098
    valeur_normalisee: -0.7272469137655015
    valeur_ponderee: -0.7272469137655015
    ts: '2026-08-06T05:23:37.356353+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.04460558119094715
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  tension_politique_fr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: Les news récentes (48h) montrent un apaisement des tensions
      au Moyen-Orient et des PMI services/manufacturiers solides, soutenant le CAC40
      malgré la sécheresse et les PMI chinois faibles. Le prix a déjà monté de +5.05%
      sur 20j, mais la fraîcheur des news LONG et la matérialité moyenne dominent
      les s
    nature: structurel
    event_id: d77b25239556
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -124.60000000000011
      7j: -124.60000000000011
      1m: -124.60000000000011
  rsi_14j_fchi:
    valeur: 67.83757323668955
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.0504854958185994
    valeur_normalisee: 0.8836689133575792
    valeur_ponderee: 0.8836689133575792
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.031315532302372384
    valeur_normalisee: 0.78548270265409
    valeur_ponderee: 0.78548270265409
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.01876226921077695
    valeur_normalisee: 0.6451569738688137
    valeur_ponderee: 0.6451569738688137
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.08231768080661178
    valeur_normalisee: 0.04115884040330589
    valeur_ponderee: 0.04115884040330589
    ts: '2026-08-06T05:23:37.356353+00:00'
  hf_positioning_flux_options:
    valeur: -15428.0
    valeur_normalisee: -0.5922330245608465
    valeur_ponderee: -0.5922330245608465
    ts: '2026-08-06T05:23:37.356353+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: structurel
    event_id: 63b5ff8bb33d
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 104.83333333333334
      7j: 104.83333333333334
      1m: 104.83333333333334
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
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (baisse de production
      du Ghana, El Niño) et fraîches (jusqu'au 5 août), cohérentes avec le prix en
      hausse. Les quelques news SHORT sont faibles ou anciennes et ne contrebalancent
      pas le signal haussier.
    nature: structurel
    event_id: 63b5ff8bb33d
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 106.0
      7j: 106.0
      1m: 106.0
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.04847839448295144
    valeur_normalisee: -0.24415693179466433
    valeur_ponderee: -0.24415693179466433
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.14933573824684143
    valeur_normalisee: 0.47844644070251
    valeur_ponderee: 0.47844644070251
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.003980646561653867
    valeur_normalisee: -0.22798611540946895
    valeur_ponderee: -0.22798611540946895
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.3962270150369114
    valeur_normalisee: 0.1981135075184557
    valeur_ponderee: 0.1981135075184557
    ts: '2026-08-06T05:23:37.356353+00:00'
  usd_brl:
    valeur: 5.13458
    valeur_normalisee: 0.08209417671252574
    valeur_ponderee: 0.08209417671252574
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_coffee:
    valeur: 27914.0
    valeur_normalisee: -0.15738525585500848
    valeur_ponderee: -0.15738525585500848
    ts: '2026-08-06T05:23:37.356353+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: 'Signaux mixtes : baisses récentes des prix Arabica (04/08)
      et chute du 29/07 s''opposent aux hausses de prix minimum Fairtrade et aux prix
      élevés au Vietnam. Le prix a baissé de 6.21% sur 5j, confirmant le biais baissier
      déjà pricé, sans news fraîche à matérialité high pour inverser.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 211.73333333333363
      7j: 211.73333333333363
      1m: 211.73333333333363
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-06T05:23:37.356353+00:00'
  meteo_vietnam_robusta:
    valeur: 0.3095330219106034
    valeur_normalisee: 0.1547665109553017
    valeur_ponderee: 0.1547665109553017
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.029482533147234813
    valeur_normalisee: -0.47107332942427554
    valeur_ponderee: -0.47107332942427554
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.03966211787011675
    valeur_normalisee: -0.5742136156019998
    valeur_ponderee: -0.5742136156019998
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.030190763785288177
    valeur_normalisee: -0.512726218899657
    valeur_ponderee: -0.512726218899657
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
coton:
  meteo_texas_cotton_precip:
    ts: '2026-08-06T05:23:37.356353+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-05'
    valeur: 0.20868274854246602
    valeur_normalisee: 0.10434137427123301
    valeur_ponderee: 0.10434137427123301
    reporte_cause: source réseau indisponible
  meteo_inde_gujarat_coton:
    valeur: 0.7299812424277818
    valeur_normalisee: 0.3649906212138909
    valeur_ponderee: 0.3649906212138909
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_cotton:
    valeur: 98453.0
    valeur_normalisee: 0.7538273781947771
    valeur_ponderee: 0.7538273781947771
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_coton:
    valeur: 0.03922751961375992
    valeur_normalisee: 0.3837802948943602
    valeur_ponderee: 0.3837802948943602
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_coton:
    valeur: 0.029699023320709506
    valeur_normalisee: 0.46478097050443434
    valeur_ponderee: 0.46478097050443434
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_coton:
    valeur: 0.026629570747217945
    valeur_normalisee: 0.5301974309185606
    valeur_ponderee: 0.5301974309185606
    ts: '2026-08-06T05:23:37.356353+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: structurel
    event_id: e454b16a420f
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 50.46666666666672
      7j: 50.46666666666672
      1m: 50.46666666666672
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: Les importations chinoises de cuivre en forte hausse et la
      demande IA US-Chine avec stocks en chute dominent, malgré des PMI chinois faibles
      et un rebond de l'offre chilienne. Le prix a déjà monté de 7.37% sur 20j, ce
      qui limite la conviction.
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 25.033333333333292
      7j: 25.033333333333292
      1m: 25.033333333333292
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_copper_nets:
    valeur: 68497.0
    valeur_normalisee: 0.881260518302941
    valeur_ponderee: 0.881260518302941
    ts: '2026-08-06T05:23:37.356353+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 42.86666666666664
      7j: 42.86666666666664
      1m: 42.86666666666664
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.0015712651092159155
    valeur_normalisee: 0.5188296567460347
    valeur_ponderee: 0.5188296567460347
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.07372736820805348
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.032717909587852034
    valeur_normalisee: 0.5664962077951771
    valeur_ponderee: 0.5664962077951771
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.025734058890400924
    valeur_normalisee: 0.567439539579812
    valeur_ponderee: 0.567439539579812
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5376749090000001
    valeur_normalisee: 0.062383679056416445
    valeur_ponderee: 0.062383679056416445
    ts: '2026-08-06T05:23:37.356353+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6599999999999997
    valeur_normalisee: 0.5689839731914696
    valeur_ponderee: 0.5689839731914696
    ts: '2026-08-06T05:23:37.356353+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  usd_jpy_proxy_risk:
    valeur: 157.77084
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_eur_nets:
    valeur: -100540.0
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.009424971803771776
    valeur_normalisee: 0.8172387785529871
    valeur_ponderee: 0.8172387785529871
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.0015527950310558758
    valeur_normalisee: 0.13942143734130547
    valeur_ponderee: 0.13942143734130547
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.003215014988921183
    valeur_normalisee: 0.34738093815124843
    valeur_ponderee: 0.34738093815124843
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.4
    valeur_normalisee: 0.6556416159119935
    valeur_ponderee: 0.6556416159119935
    ts: '2026-08-06T05:23:37.356353+00:00'
  sox_trend_5j:
    valeur: 530.70001
    valeur_normalisee: -0.3471552640388049
    valeur_ponderee: -0.3471552640388049
    ts: '2026-08-06T05:23:37.356353+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1687996705534598
    valeur_normalisee: 0.4928457283950338
    valeur_ponderee: 0.4928457283950338
    ts: '2026-08-06T05:23:37.356353+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: 'Signaux mitigés : news LONG (rebond IA, PMI solides, remboursement
      douanes) contre SHORT (tarifs, inflation, tensions Fed, épuisement missiles).
      Prix +8.4% sur 5j suggère que le positif est déjà pricé, et la fraîcheur des
      news SHORT du jour (tarifs, futures) équilibre.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 147.6000000000003
      7j: 147.6000000000003
      1m: 147.6000000000003
  flux_etf_qqq_5j:
    valeur: 0.08397686621361777
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  spread_nasdaq_russell2000:
    valeur: 417.53
    valeur_normalisee: -0.15543680658754327
    valeur_ponderee: -0.15543680658754327
    ts: '2026-08-06T05:23:37.356353+00:00'
  rsi_14j_ixic:
    valeur: 54.840533484958826
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.008236801416844575
    valeur_normalisee: -0.11098734773042206
    valeur_ponderee: -0.11098734773042206
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.05157448835981926
    valeur_normalisee: 0.7490460207012632
    valeur_ponderee: 0.7490460207012632
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.04260236402567408
    valeur_normalisee: 0.8084183345661906
    valeur_ponderee: 0.8084183345661906
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-06T05:23:37.356353+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.4
    valeur_normalisee: 0.6556416159119935
    valeur_ponderee: 0.6556416159119935
    ts: '2026-08-06T05:23:37.356353+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_nets:
    valeur: 174131.0
    valeur_normalisee: -0.20851213210640585
    valeur_ponderee: -0.20851213210640585
    ts: '2026-08-06T05:23:37.356353+00:00'
  flux_etf_or_5j:
    valeur: 0.050016232753613776
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  tension_geopolitique:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: 'Signaux contradictoires : plusieurs news SHORT sur un accord
      Iran-Oman pour Ormuz (matérialité high mais non confirmé) contre des news LONG
      sur tensions géopolitiques (frappe russe sur Kyiv, stocks Patriot épuisés).
      Le prix a déjà monté de +5.93% sur 20j, suggérant que le marché a pricé une
      partie d'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 450.59999999999815
      7j: 450.59999999999815
      1m: 450.59999999999815
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-06T05:23:37.356353+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_or:
    valeur: 0.05928894010973185
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_or:
    valeur: 0.036953973658285566
    valeur_normalisee: 0.8409683723215123
    valeur_ponderee: 0.8409683723215123
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_or:
    valeur: 0.04927485870326498
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-06T05:23:37.356353+00:00'
petrole:
  eia_crude_surprise:
    valeur: 406987.0
    valeur_normalisee: -0.6764819159441962
    valeur_ponderee: -0.6764819159441962
    ts: '2026-08-06T05:23:37.356353+00:00'
  tension_geopol_moyen_orient:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: La majorité des news récentes (5-6 août) signalent une désescalade
      des tensions sur le détroit d'Ormuz avec des pourparlers Iran-Oman et un accord
      proche, ce qui réduit la prime de risque et pèse sur les prix. Le mouvement
      de prix récent (-9.55% sur 5j) confirme cette tendance baissière, malgré quel
    nature: structurel
    event_id: 1095f46f0761
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 204.3999999999999
      7j: 204.3999999999999
      1m: 204.3999999999999
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 32189.0
    valeur_normalisee: 0.13392206358519956
    valeur_ponderee: 0.13392206358519956
    ts: '2026-08-06T05:23:37.356353+00:00'
  opec_production_policy:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: structurel
    event_id: 1095f46f0761
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 185.70000000000053
      7j: 185.70000000000053
      1m: 185.70000000000053
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  cushing_stocks:
    valeur: 20955.0
    valeur_normalisee: -0.41464832709950017
    valeur_ponderee: -0.41464832709950017
    ts: '2026-08-06T05:23:37.356353+00:00'
  spread_brent_wti:
    valeur: 3.8510500000000008
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.03348374009460198
    valeur_normalisee: 0.25334010168232657
    valeur_ponderee: 0.25334010168232657
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.04056929482425731
    valeur_normalisee: -0.09291211846585161
    valeur_ponderee: -0.09291211846585161
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.05348173881521523
    valeur_normalisee: -0.3204233666469908
    valeur_ponderee: -0.3204233666469908
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-06T05:23:37.356353+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-06T05:23:37.356353+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.019999999999999574
    valeur_normalisee: -0.017853516051952296
    valeur_ponderee: -0.017853516051952296
    ts: '2026-08-06T05:23:37.356353+00:00'
  hy_credit_spread:
    valeur: 2.73
    valeur_normalisee: -0.12592477703028673
    valeur_ponderee: -0.12592477703028673
    ts: '2026-08-06T05:23:37.356353+00:00'
  breadth_sp_ma50:
    valeur: 0.2854414914571894
    valeur_normalisee: 0.2454550176583031
    valeur_ponderee: 0.2454550176583031
    ts: '2026-08-06T05:23:37.356353+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.05528741657424896
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.19
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  rsi_14j_gspc:
    valeur: 64.15148768602526
    ts: '2026-08-06T05:23:37.356353+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.4
    valeur_normalisee: 0.6556416159119935
    valeur_ponderee: 0.6556416159119935
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.03272063233912981
    valeur_normalisee: 0.2948212752544915
    valeur_ponderee: 0.2948212752544915
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.04153750135773393
    valeur_normalisee: 0.9942308850084899
    valeur_ponderee: 0.9942308850084899
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.03046725046711618
    valeur_normalisee: 0.9762867547814695
    valeur_ponderee: 0.9762867547814695
    ts: '2026-08-06T05:23:37.356353+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.18102908042596266
    valeur_normalisee: 0.09051454021298133
    valeur_ponderee: 0.09051454021298133
    ts: '2026-08-06T05:23:37.356353+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 78.58269
    valeur_normalisee: -0.38254552483328197
    valeur_ponderee: -0.38254552483328197
    ts: '2026-08-06T05:23:37.356353+00:00'
  usd_brl_sucre:
    valeur: 5.13458
    valeur_normalisee: 0.08209417671252574
    valeur_ponderee: 0.08209417671252574
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_sugar:
    valeur: -81679.0
    valeur_normalisee: -0.5608615387476262
    valeur_ponderee: -0.5608615387476262
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.003018108651911655
    valeur_normalisee: -0.03867808504682157
    valeur_ponderee: -0.03867808504682157
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.037460978147762836
    valeur_normalisee: 0.7093620862524657
    valeur_ponderee: 0.7093620862524657
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.03638253638253652
    valeur_normalisee: 0.8143772028393657
    valeur_ponderee: 0.8143772028393657
    ts: '2026-08-06T05:23:37.356353+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '10.22'
    p2_shadow_contrib_exclu:
      24h: 36.69999999999996
      7j: 36.69999999999996
      1m: 36.69999999999996
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
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '10.22'
    p2_shadow_contrib_exclu:
      24h: 36.69999999999996
      7j: 36.69999999999996
      1m: 36.69999999999996
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5300000000000002
    valeur_normalisee: 0.3184254629870951
    valeur_ponderee: 0.3184254629870951
    ts: '2026-08-06T05:23:37.356353+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.011113676757177227
    valeur_normalisee: -0.3531737374652895
    valeur_ponderee: -0.3531737374652895
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.003626764790057191
    valeur_normalisee: 0.2575555323473356
    valeur_ponderee: 0.2575555323473356
    ts: '2026-08-06T05:23:37.356353+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.028568564579620093
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_jpy_nets:
    valeur: -171320.0
    valeur_normalisee: -0.7719946476652498
    valeur_ponderee: -0.7719946476652498
    ts: '2026-08-06T05:23:37.356353+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.96
    valeur_normalisee: 0.5079968800912141
    valeur_ponderee: 0.5079968800912141
    ts: '2026-08-06T05:23:37.356353+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-06T05:23:37.356353+00:00'
    nature: ponctuel
    event_id: 9c10b6559c09
    event_date: '2026-08-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 11.26666666666667
      7j: 11.26666666666667
      1m: 11.26666666666667
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-06T05:23:37.356353+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-06T05:23:37.356353+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-06T05:23:37.356353+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-06T05:23:37.356353+00:00'
  gap_rv_iv:
    valeur: -0.8205897692046467
    ts: '2026-08-06T05:23:37.356353+00:00'
  cftc_cot_vix_nets:
    valeur: -63413.0
    valeur_normalisee: -0.21963090052659925
    valeur_ponderee: -0.21963090052659925
    ts: '2026-08-06T05:23:37.356353+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-06T05:23:37.356353+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée (épuisement des
      stocks de missiles, fermeture d''Ormuz, pertes pétrolières) dominent, malgré
      quelques signaux SHORT sur un accord potentiel. Le prix a baissé de 6.88% sur
      20j, ce qui suggère que le marché a déjà pricé une partie du risque, mais la
      fraîcheur '
    nature: structurel
    event_id: 16f3a6f1e3f6
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 249.1999999999995
      7j: 249.1999999999995
      1m: 249.1999999999995
  gate_evenement_macro_imminent:
    valeur: false
    ts: '2026-08-06T05:23:37.356353+00:00'
```
