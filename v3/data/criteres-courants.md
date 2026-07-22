# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-22T05:23:36.983972+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.7843198481317555
    valeur_ponderee: 0.7843198481317555
    ts: '2026-07-22T05:23:36.983972+00:00'
  mouvement_or_5j:
    valeur: 0.02665578142984315
    valeur_normalisee: 0.793821620625845
    valeur_ponderee: 0.793821620625845
    ts: '2026-07-22T05:23:36.983972+00:00'
  ratio_gold_silver:
    valeur: 69.19777533616497
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_silver:
    valeur: 22604.0
    valeur_normalisee: -0.24337735975094785
    valeur_ponderee: -0.24337735975094785
    ts: '2026-07-22T05:23:36.983972+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.0016926462290766109
    valeur_normalisee: 0.13179045969517608
    valeur_ponderee: 0.13179045969517608
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_argent:
    valeur: -0.022471010769033795
    valeur_normalisee: 0.6342257542338242
    valeur_ponderee: 0.6342257542338242
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_argent:
    valeur: 0.03156737606820448
    valeur_normalisee: 0.5615820285171045
    valeur_ponderee: 0.5615820285171045
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_argent:
    valeur: 0.06407977253757191
    valeur_normalisee: 0.9127516435009608
    valeur_ponderee: 0.9127516435009608
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-22T05:23:36.983972+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.32080029370940105
    valeur_normalisee: 0.16040014685470053
    valeur_ponderee: 0.16040014685470053
    ts: '2026-07-22T05:23:36.983972+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: Multiples news à matérialité élevée (USDA baisse production/stocks,
      escalade Russie-Ukraine, vague de chaleur Europe) dominent le flux, toutes LONG.
      Le prix a déjà intégré une partie du biais (+15% sur 20j), mais la fraîcheur
      et la cohérence des signaux récents (21 juillet) maintiennent une convicti
    nature: structurel
    event_id: 633d06cceafb
    event_date: '2026-07-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 37.76666666666657
      7j: 37.76666666666657
      1m: 37.76666666666657
  cftc_cot_wheat:
    valeur: -25958.0
    valeur_normalisee: 0.24746974397717958
    valeur_ponderee: 0.24746974397717958
    ts: '2026-07-22T05:23:36.983972+00:00'
  meteo_australie_dryland:
    valeur: 0.04356817544295561
    valeur_normalisee: 0.021784087721477805
    valeur_ponderee: 0.021784087721477805
    ts: '2026-07-22T05:23:36.983972+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_ble:
    valeur: 0.15364665915130304
    valeur_normalisee: 0.8993876331002573
    valeur_ponderee: 0.8993876331002573
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_ble:
    valeur: 0.006493173470555114
    valeur_normalisee: 0.0031510000475395055
    valeur_ponderee: 0.0031510000475395055
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_ble:
    valeur: -0.00048327155788030485
    valeur_normalisee: -0.05222370804263254
    valeur_ponderee: -0.05222370804263254
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-22T05:23:36.983972+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-07-22T05:23:36.983972+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.004278386866875206
    valeur_normalisee: 0.21643750483522914
    valeur_ponderee: 0.21643750483522914
    ts: '2026-07-22T05:23:36.983972+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.0033303507253474862
    valeur_normalisee: 0.13610546739611984
    valeur_ponderee: 0.13610546739611984
    ts: '2026-07-22T05:23:36.983972+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée et fraîches (escalade
      Iran-USA, droits de douane US sur Canada, pétrole >90$). Le prix quasi stable
      (+0.27% sur 20j) ne reflète pas encore pleinement ces risques, d'où une conviction
      haute malgré l'absence de baisse récente.
    nature: structurel
    event_id: bbd13d723aee
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -113.33333333333344
      7j: -113.33333333333344
      1m: -113.33333333333344
  rsi_14j_fchi:
    valeur: 51.99312307455519
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.0026891823486929756
    valeur_normalisee: -0.15461982704624957
    valeur_ponderee: -0.15461982704624957
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.0028984299958596527
    valeur_normalisee: 0.030204795395411425
    valeur_ponderee: 0.030204795395411425
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.001757095413986165
    valeur_normalisee: -0.10942999677677086
    valeur_ponderee: -0.10942999677677086
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.3822598866442453
    valeur_normalisee: 0.19112994332212266
    valeur_ponderee: 0.19112994332212266
    ts: '2026-07-22T05:23:36.983972+00:00'
  hf_positioning_flux_options:
    valeur: -18516.0
    valeur_normalisee: -0.6527264467064956
    valeur_ponderee: -0.6527264467064956
    ts: '2026-07-22T05:23:36.983972+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 75.80000000000015
      7j: 75.80000000000015
      1m: 75.80000000000015
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
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: Super El Niño menace les récoltes (high, 21/07) domine les
      signaux SHORT plus anciens sur offre abondante et dollar fort. Le prix a déjà
      monté de 11.82% sur 20j, ce qui limite la conviction malgré la fraîcheur de
      la news LONG.
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 75.80000000000015
      7j: 75.80000000000015
      1m: 75.80000000000015
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.11817118438484253
    valeur_normalisee: -0.028937036423771167
    valeur_ponderee: -0.028937036423771167
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.051953578676740775
    valeur_normalisee: -0.5072965983082213
    valeur_ponderee: -0.5072965983082213
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.013814028003893197
    valeur_normalisee: -0.05893804564672073
    valeur_ponderee: -0.05893804564672073
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-22T05:23:36.983972+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.40165849517112373
    valeur_normalisee: 0.20082924758556187
    valeur_ponderee: 0.20082924758556187
    ts: '2026-07-22T05:23:36.983972+00:00'
  usd_brl:
    valeur: 5.08598
    valeur_normalisee: -0.3117958188501177
    valeur_ponderee: -0.3117958188501177
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_coffee:
    valeur: 26499.0
    valeur_normalisee: -0.18862009873184962
    valeur_ponderee: -0.18862009873184962
    ts: '2026-07-22T05:23:36.983972+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: 'Dominance de signaux haussiers récents et à forte matérialité
      : tarifs US sur le Brésil (16/07, high) et rapports USDA haussiers (15/07, medium)
      renforcés par les prévisions El Niño (17/07, medium). La seule news SHORT (baisse
      surfaces brûlées Amazonie, 21/07, medium) est isolée et ne contrebalance '
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '16.22'
    p2_shadow_contrib_exclu:
      24h: 80.96666666666673
      7j: 80.96666666666673
      1m: 80.96666666666673
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
    ts: '2026-07-22T05:23:36.983972+00:00'
  meteo_vietnam_robusta:
    valeur: 0.22066182733931083
    valeur_normalisee: 0.11033091366965542
    valeur_ponderee: 0.11033091366965542
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.06603334666248406
    valeur_normalisee: 0.021385482262313262
    valeur_ponderee: 0.021385482262313262
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.007258739302562156
    valeur_normalisee: -0.22619063778546053
    valeur_ponderee: -0.22619063778546053
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.00572850417154025
    valeur_normalisee: -0.0463451923181158
    valeur_ponderee: -0.0463451923181158
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-22T05:23:36.983972+00:00'
coton:
  meteo_texas_cotton_precip:
    ts: '2026-07-22T05:23:36.983972+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-21'
    valeur: 0.537600574891199
    valeur_normalisee: 0.2688002874455995
    valeur_ponderee: 0.2688002874455995
    reporte_cause: source réseau indisponible
  meteo_inde_gujarat_coton:
    ts: '2026-07-22T05:23:36.983972+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-21'
    valeur: -0.0010689968498498183
    valeur_normalisee: 0.0005344984249249092
    valeur_ponderee: 0.0005344984249249092
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 101259.0
    valeur_normalisee: 0.7785042547190695
    valeur_ponderee: 0.7785042547190695
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_coton:
    valeur: 0.021193415637859925
    valeur_normalisee: 0.10930397410857023
    valeur_ponderee: 0.10930397410857023
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_coton:
    valeur: -0.009578926362003637
    valeur_normalisee: -0.0706565590799878
    valeur_ponderee: -0.0706565590799878
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_coton:
    valeur: 0.010794297352342053
    valeur_normalisee: 0.19826890803658503
    valeur_ponderee: 0.19826890803658503
    ts: '2026-07-22T05:23:36.983972+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    event_id: 70467c30767d
    event_date: '2026-07-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 24.199999999999985
      7j: 24.199999999999985
      1m: 24.199999999999985
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-22T05:23:36.983972+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: 'Signaux contradictoires : forte demande chinoise et électrification
      (EU plan, US power demand) vs chute des ventes auto chinoises et PIB décevant.
      Le prix a déjà monté de +5.75% sur 20j, suggérant que les news LONG sont intégrées,
      tandis que les news SHORT récentes (ventes auto -20%, PIB faible) lim'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 10.733333333333325
      7j: 10.733333333333325
      1m: 10.733333333333325
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_copper_nets:
    valeur: 65629.0
    valeur_normalisee: 0.8500644003681505
    valeur_ponderee: 0.8500644003681505
    ts: '2026-07-22T05:23:36.983972+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    event_id: 97a37c8d1dd9
    event_date: '2026-07-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 26.233333333333327
      7j: 26.233333333333327
      1m: 26.233333333333327
  ratio_cuivre_or:
    valeur: 0.001570450816900207
    valeur_normalisee: 0.7940798671506216
    valeur_ponderee: 0.7940798671506216
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.05749021964170242
    valeur_normalisee: 0.792651353347601
    valeur_ponderee: 0.792651353347601
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.022366466559220033
    valeur_normalisee: 0.43440212033241143
    valeur_ponderee: 0.43440212033241143
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.04088071035397167
    valeur_normalisee: 0.9390897088136281
    valeur_ponderee: 0.9390897088136281
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5000617769
    valeur_normalisee: 0.07739434332238053
    valeur_ponderee: 0.07739434332238053
    ts: '2026-07-22T05:23:36.983972+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6299999999999994
    valeur_normalisee: 0.8287518318497274
    valeur_ponderee: 0.8287518318497274
    ts: '2026-07-22T05:23:36.983972+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  usd_jpy_proxy_risk:
    valeur: 163.16916
    valeur_normalisee: 0.8889420507942896
    valeur_ponderee: 0.8889420507942896
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_eur_nets:
    valeur: -34257.0
    valeur_normalisee: -0.6453198959279014
    valeur_ponderee: -0.6453198959279014
    ts: '2026-07-22T05:23:36.983972+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.0021689318010880143
    valeur_normalisee: 0.4103303136911062
    valeur_ponderee: 0.4103303136911062
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.00470196191323613
    valeur_normalisee: -0.23627143139082887
    valeur_ponderee: -0.23627143139082887
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0019419853738757986
    valeur_normalisee: -0.1360008430465531
    valeur_ponderee: -0.1360008430465531
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.7843198481317555
    valeur_ponderee: 0.7843198481317555
    ts: '2026-07-22T05:23:36.983972+00:00'
  sox_trend_5j:
    valeur: 552.69
    valeur_normalisee: 0.014143989437578178
    valeur_ponderee: 0.014143989437578178
    ts: '2026-07-22T05:23:36.983972+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16653737816285785
    valeur_normalisee: 0.44875099980787386
    valeur_ponderee: 0.44875099980787386
    ts: '2026-07-22T05:23:36.983972+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: Escalade militaire US-Iran dominante avec frappes répétées
      et menace nucléaire, pétrole >90$, craintes inflationnistes et droits de douane
      Trump pèsent sur le Nasdaq. Les news LONG (TSMC, Wistron) sont minoritaires
      et ne compensent pas le signal SHORT massif et frais.
    nature: ponctuel
    event_id: b8beafe19dad
    event_date: '2026-07-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 70.06666666666673
      7j: 70.06666666666673
      1m: 70.06666666666673
  flux_etf_qqq_5j:
    valeur: -0.014895343828592922
    valeur_normalisee: -0.4077247423250234
    valeur_ponderee: -0.4077247423250234
    ts: '2026-07-22T05:23:36.983972+00:00'
  spread_nasdaq_russell2000:
    valeur: 412.42996
    valeur_normalisee: -0.29765662949641664
    valeur_ponderee: -0.29765662949641664
    ts: '2026-07-22T05:23:36.983972+00:00'
  rsi_14j_ixic:
    valeur: 47.51918645561519
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.03927100698867125
    valeur_normalisee: -0.6773376067214298
    valeur_ponderee: -0.6773376067214298
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.022797810880652025
    valeur_normalisee: -0.5297183996542542
    valeur_ponderee: -0.5297183996542542
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.0042921069779300325
    valeur_normalisee: 0.007147636102297405
    valeur_ponderee: 0.007147636102297405
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.7843198481317555
    valeur_ponderee: 0.7843198481317555
    ts: '2026-07-22T05:23:36.983972+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_nets:
    valeur: 175931.0
    valeur_normalisee: -0.19336088557858558
    valeur_ponderee: -0.19336088557858558
    ts: '2026-07-22T05:23:36.983972+00:00'
  flux_etf_or_5j:
    valeur: 0.007147682578199088
    valeur_normalisee: 0.36068166761194204
    valeur_ponderee: 0.36068166761194204
    ts: '2026-07-22T05:23:36.983972+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée sur l'escalade
      US-Iran et la perturbation du détroit d'Ormuz, malgré une hausse des rendements
      US et une médiation. Le prix a légèrement progressé sur 5j, confirmant le biais
      haussier.
    nature: structurel
    event_id: 4b4d00ea49b9
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 175.66666666666677
      7j: 175.66666666666677
      1m: 175.66666666666677
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-22T05:23:36.983972+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_or:
    valeur: 4.18125745997866e-05
    valeur_normalisee: 0.6974595193699936
    valeur_ponderee: 0.6974595193699936
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_or:
    valeur: 0.015669626358500777
    valeur_normalisee: 0.5665236309506633
    valeur_ponderee: 0.5665236309506633
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_or:
    valeur: 0.028286417478377013
    valeur_normalisee: 0.8059934237085606
    valeur_ponderee: 0.8059934237085606
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-07-22T05:23:36.983972+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-07-17'
    valeur: 409665.0
    valeur_normalisee: -0.6527350227315017
    valeur_ponderee: -0.6527350227315017
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: 'Escalade continue des hostilités US-Iran avec frappes nocturnes
      et menace sur le détroit d''Ormuz domine, malgré quelques signaux short sur
      demande chinoise et médiation. Le prix a déjà intégré une partie du risque mais
      la fraîcheur et la matérialité élevée des news LONG justifient un biais haussier '
    nature: structurel
    event_id: 4b4d00ea49b9
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 151.06666666666675
      7j: 151.06666666666675
      1m: 151.06666666666675
    sign_conflict: true
    sign_conflict_details:
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
  cftc_cot_crude_nets:
    valeur: 51028.0
    valeur_normalisee: 0.5358446521183773
    valeur_ponderee: 0.5358446521183773
    ts: '2026-07-22T05:23:36.983972+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    event_id: 4b4d00ea49b9
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 165.03333333333353
      7j: 165.03333333333353
      1m: 165.03333333333353
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
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  cushing_stocks:
    valeur: 20044.0
    valeur_normalisee: -0.6190626099156435
    valeur_ponderee: -0.6190626099156435
    ts: '2026-07-22T05:23:36.983972+00:00'
  spread_brent_wti:
    valeur: 6.8453500000000105
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.22964163151056138
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.1086514532769225
    valeur_normalisee: 0.650581127388881
    valeur_ponderee: 0.650581127388881
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.047031458982002006
    valeur_normalisee: 0.4754414495301499
    valeur_ponderee: 0.4754414495301499
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-22T05:23:36.983972+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.020000000000000462
    valeur_normalisee: -0.24782000417804706
    valeur_ponderee: -0.24782000417804706
    ts: '2026-07-22T05:23:36.983972+00:00'
  hy_credit_spread:
    valeur: 2.69
    valeur_normalisee: -0.5447725637002251
    valeur_ponderee: -0.5447725637002251
    ts: '2026-07-22T05:23:36.983972+00:00'
  breadth_sp_ma50:
    valeur: 0.2843320434463552
    valeur_normalisee: 0.33905791618258907
    valeur_ponderee: 0.33905791618258907
    ts: '2026-07-22T05:23:36.983972+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.00472179868529321
    valeur_normalisee: -0.322644797248666
    valeur_ponderee: -0.322644797248666
    ts: '2026-07-22T05:23:36.983972+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.98
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-22T05:23:36.983972+00:00'
  rsi_14j_gspc:
    valeur: 52.028143151126876
    ts: '2026-07-22T05:23:36.983972+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.7843198481317555
    valeur_ponderee: 0.7843198481317555
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.005225782113867927
    valeur_normalisee: -0.3399281770977947
    valeur_ponderee: -0.3399281770977947
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.008834995578051563
    valeur_normalisee: -0.4533074081451909
    valeur_ponderee: -0.4533074081451909
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.0032501333353367468
    valeur_normalisee: -0.23326992518791817
    valeur_ponderee: -0.23326992518791817
    ts: '2026-07-22T05:23:36.983972+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.2138384775982998
    valeur_normalisee: 0.1069192387991499
    valeur_ponderee: 0.1069192387991499
    ts: '2026-07-22T05:23:36.983972+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 92.25724
    valeur_normalisee: 0.0850884509204169
    valeur_ponderee: 0.0850884509204169
    ts: '2026-07-22T05:23:36.983972+00:00'
  usd_brl_sucre:
    valeur: 5.08598
    valeur_normalisee: -0.3117958188501177
    valeur_ponderee: -0.3117958188501177
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_sugar:
    valeur: -45822.0
    valeur_normalisee: -0.4281576108153665
    valeur_ponderee: -0.4281576108153665
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.06637649619151276
    valeur_normalisee: 0.5557611039727485
    valeur_ponderee: 0.5557611039727485
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.0010193679918449883
    valeur_normalisee: -0.11027568795626756
    valeur_ponderee: -0.11027568795626756
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.02833158447009465
    valeur_normalisee: 0.4951445774219804
    valeur_ponderee: 0.4951445774219804
    ts: '2026-07-22T05:23:36.983972+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    event_id: b3cfd6c3a64c
    event_date: '2026-07-16T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 20.466666666666658
      7j: 20.466666666666658
      1m: 20.466666666666658
  exports_bresil_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    event_id: b3cfd6c3a64c
    event_date: '2026-07-16T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 20.466666666666658
      7j: 20.466666666666658
      1m: 20.466666666666658
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-22T05:23:36.983972+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.54
    valeur_normalisee: 0.7057225577752227
    valeur_ponderee: 0.7057225577752227
    ts: '2026-07-22T05:23:36.983972+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.005999653259105342
    valeur_normalisee: 0.5479073807859328
    valeur_ponderee: 0.5479073807859328
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.004472038172719461
    valeur_normalisee: 0.5239957668315417
    valeur_ponderee: 0.5239957668315417
    ts: '2026-07-22T05:23:36.983972+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.012700811933657796
    valeur_normalisee: 0.46130105375849034
    valeur_ponderee: 0.46130105375849034
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_jpy_nets:
    valeur: -127263.0
    valeur_normalisee: -0.5107367349427174
    valeur_ponderee: -0.5107367349427174
    ts: '2026-07-22T05:23:36.983972+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.9299999999999997
    valeur_normalisee: 0.7184074303359826
    valeur_ponderee: 0.7184074303359826
    ts: '2026-07-22T05:23:36.983972+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-22T05:23:36.983972+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 2.666666666666667
      7j: 2.666666666666667
      1m: 2.666666666666667
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-22T05:23:36.983972+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-22T05:23:36.983972+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-22T05:23:36.983972+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-22T05:23:36.983972+00:00'
  gap_rv_iv:
    valeur: -3.2609056717050606
    ts: '2026-07-22T05:23:36.983972+00:00'
  cftc_cot_vix_nets:
    valeur: -65783.0
    valeur_normalisee: -0.26642687690687433
    valeur_ponderee: -0.26642687690687433
    ts: '2026-07-22T05:23:36.983972+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-22T05:23:36.983972+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et très fraîches
      (22 juillet) sur l'escalade US-Iran et les perturbations du détroit d'Ormuz,
      malgré un prix VIX en baisse de 5.45% sur 20j. La fraîcheur et l'intensité des
      événements justifient un signal LONG fort.
    nature: structurel
    event_id: 4b4d00ea49b9
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 191.93333333333325
      7j: 191.93333333333325
      1m: 191.93333333333325
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-22T05:23:36.983972+00:00'
```
