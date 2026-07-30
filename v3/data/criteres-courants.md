# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-30T05:23:09.453093+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.8076491359199692
    valeur_ponderee: 0.8076491359199692
    ts: '2026-07-30T05:23:09.453093+00:00'
  mouvement_or_5j:
    valeur: -0.003404997926928943
    valeur_normalisee: 0.10386922943485342
    valeur_ponderee: 0.10386922943485342
    ts: '2026-07-30T05:23:09.453093+00:00'
  ratio_gold_silver:
    valeur: 70.69216311826085
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_silver:
    valeur: 20569.0
    valeur_normalisee: -0.303970612481078
    valeur_ponderee: -0.303970612481078
    ts: '2026-07-30T05:23:09.453093+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.03987388724035601
    valeur_normalisee: -0.14103909659005578
    valeur_ponderee: -0.14103909659005578
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_argent:
    valeur: -0.044591393201915075
    valeur_normalisee: 0.5103702995098206
    valeur_ponderee: 0.5103702995098206
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_argent:
    valeur: -0.00855629739117214
    valeur_normalisee: 0.17951534880088502
    valeur_ponderee: 0.17951534880088502
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_argent:
    valeur: -0.021329845244597023
    valeur_normalisee: -0.10402978338369907
    valeur_ponderee: -0.10402978338369907
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.29620091872242404
    valeur_normalisee: 0.14810045936121202
    valeur_ponderee: 0.14810045936121202
    ts: '2026-07-30T05:23:09.453093+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Multiples news high matérialité récentes (USDA baisse production/stocks,
      Black Sea disruptions) dominent le flux, cohérentes avec le rallye de +5.22%
      sur 20j. La légère baisse récente de -2.43% sur 5j ne remet pas en cause le
      signal haussier dominant.
    nature: structurel
    event_id: fd630a45bbcc
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 72.00000000000003
      7j: 72.00000000000003
      1m: 72.00000000000003
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -14250.0
    valeur_normalisee: 0.40842367936126867
    valeur_ponderee: 0.40842367936126867
    ts: '2026-07-30T05:23:09.453093+00:00'
  meteo_australie_dryland:
    valeur: -0.00731408260772745
    valeur_normalisee: -0.003657041303863725
    valeur_ponderee: -0.003657041303863725
    ts: '2026-07-30T05:23:09.453093+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_ble:
    valeur: 0.052706925861327525
    valeur_normalisee: 0.18532372089599825
    valeur_ponderee: 0.18532372089599825
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_ble:
    valeur: -0.045692470995017276
    valeur_normalisee: -0.5692452249362906
    valeur_ponderee: -0.5692452249362906
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_ble:
    valeur: 0.007102953588202565
    valeur_normalisee: 0.05572730653003941
    valeur_ponderee: 0.05572730653003941
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-30T05:23:09.453093+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-07-30T05:23:09.453093+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.02050583295446584
    valeur_normalisee: 0.566623363723985
    valeur_ponderee: 0.566623363723985
    ts: '2026-07-30T05:23:09.453093+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.00021968365553615143
    valeur_normalisee: 0.0056587784273867065
    valeur_ponderee: 0.0056587784273867065
    ts: '2026-07-30T05:23:09.453093+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Multiples news de matérialité élevée et très récentes (30
      juillet) confirment une escalade militaire majeure entre les États-Unis et l'Iran,
      avec frappes directes et menace sur les détroits pétroliers, ce qui domine largement
      le contexte de prix (+0.85% sur 20j). Les tarifs douaniers de Trump et les
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -133.06666666666683
      7j: -133.06666666666683
      1m: -133.06666666666683
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
    valeur: 53.45631405236008
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.008513496550972777
    valeur_normalisee: 0.021972719363991873
    valeur_ponderee: 0.021972719363991873
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.008172455416012525
    valeur_normalisee: 0.13811997478895438
    valeur_ponderee: 0.13811997478895438
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.004298621025499827
    valeur_normalisee: 0.09130258342103198
    valeur_ponderee: 0.09130258342103198
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -13050.0
    valeur_normalisee: -0.5555916820879753
    valeur_ponderee: -0.5555916820879753
    ts: '2026-07-30T05:23:09.453093+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: structurel
    event_id: aea535c26834
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 88.86666666666687
      7j: 88.86666666666687
      1m: 88.86666666666687
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
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Les news récentes (29-30 juillet) sont LONG (StoneX réduit
      surplus, El Niño) mais le prix a baissé de 13% sur 20j, indiquant que le marché
      a déjà intégré ces risques. Les news SHORT plus anciennes (abondance offre,
      demande faible) pèsent encore. Signal contradictoire et prix en baisse.
    nature: structurel
    event_id: aea535c26834
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 179.59999999999968
      7j: 179.59999999999968
      1m: 179.59999999999968
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: -0.13150153014269728
    valeur_normalisee: -0.7245242779558388
    valeur_ponderee: -0.7245242779558388
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.03391081929137896
    valeur_normalisee: -0.35078995027107224
    valeur_ponderee: -0.35078995027107224
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.006793057454387519
    valeur_normalisee: -0.06923998763524186
    valeur_ponderee: -0.06923998763524186
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-30T05:23:09.453093+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.38882880204236286
    valeur_normalisee: 0.19441440102118143
    valeur_ponderee: 0.19441440102118143
    ts: '2026-07-30T05:23:09.453093+00:00'
  usd_brl:
    valeur: 5.12629
    valeur_normalisee: -0.020523568192315007
    valeur_ponderee: -0.020523568192315007
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_coffee:
    valeur: 26034.0
    valeur_normalisee: -0.19563028321574708
    valeur_ponderee: -0.19563028321574708
    ts: '2026-07-30T05:23:09.453093+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: 'News SHORT récente (29/07) avec matérialité medium et confirmation
      forte, renforcée par le tarif US du 22/07 (high matérialité). Les news LONG
      El Niño sont plus anciennes et moins fraîches. Le prix a baissé de 3.54% sur
      20j, cohérent avec le biais SHORT, mais le rebond récent (+3.76% sur 5j) limite '
    nature: ponctuel
    event_id: 0e0e0ba114c1
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 100.23333333333353
      7j: 100.23333333333353
      1m: 100.23333333333353
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-30T05:23:09.453093+00:00'
  meteo_vietnam_robusta:
    valeur: 0.3712212651273927
    valeur_normalisee: 0.18561063256369634
    valeur_ponderee: 0.18561063256369634
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.035415054902062204
    valeur_normalisee: -0.43184951653681247
    valeur_ponderee: -0.43184951653681247
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.04822270352501401
    valeur_normalisee: 0.18800613340080818
    valeur_ponderee: 0.18800613340080818
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.008013960852439883
    valeur_normalisee: -0.038680857304363166
    valeur_ponderee: -0.038680857304363166
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-30T05:23:09.453093+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.3666310877943971
    valeur_normalisee: 0.18331554389719856
    valeur_ponderee: 0.18331554389719856
    ts: '2026-07-30T05:23:09.453093+00:00'
  meteo_inde_gujarat_coton:
    ts: '2026-07-30T05:23:09.453093+00:00'
    reporte: true
    reporte_age_j: 5
    reporte_date: '2026-07-23'
    valeur: 0.05646156344348821
    valeur_normalisee: 0.028230781721744105
    valeur_ponderee: 0.028230781721744105
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 100360.0
    valeur_normalisee: 0.7692072556094062
    valeur_ponderee: 0.7692072556094062
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_coton:
    valeur: 0.01968096125958141
    valeur_normalisee: 0.1581823945879504
    valeur_ponderee: 0.1581823945879504
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_coton:
    valeur: 0.006132461161079128
    valeur_normalisee: 0.12037455336677533
    valeur_ponderee: 0.12037455336677533
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_coton:
    valeur: -0.014022435897435903
    valeur_normalisee: -0.17191232856209324
    valeur_ponderee: -0.17191232856209324
    ts: '2026-07-30T05:23:09.453093+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  demande_chine_coton:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: structurel
    event_id: f37165710bf1
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 39.666666666666615
      7j: 39.666666666666615
      1m: 39.666666666666615
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-30T05:23:09.453093+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Plusieurs news high matérialité récentes (23 juillet) signalent
      des prix du cuivre proches des records sur tensions Chine/tarifs, renforcées
      par une demande chinoise forte et des inquiétudes sur l'offre. Les news SHORT
      plus anciennes (20-27 juillet) sont de matérialité plus faible et ne contredisent
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 20.13333333333333
      7j: 20.13333333333333
      1m: 20.13333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_copper_nets:
    valeur: 74822.0
    valeur_normalisee: 0.9967771915326051
    valeur_ponderee: 0.9967771915326051
    ts: '2026-07-30T05:23:09.453093+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: ponctuel
    event_id: 883dde228407
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 39.56666666666665
      7j: 39.56666666666665
      1m: 39.56666666666665
  ratio_cuivre_or:
    valeur: 0.0015613277695421235
    valeur_normalisee: 0.615867452166127
    valeur_ponderee: 0.615867452166127
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.011703715340507514
    valeur_normalisee: 0.23552103619386375
    valeur_ponderee: 0.23552103619386375
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.0010341524074179986
    valeur_normalisee: 0.03766344174371051
    valeur_ponderee: 0.03766344174371051
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.006332442194028953
    valeur_normalisee: -0.1407087818497046
    valeur_ponderee: -0.1407087818497046
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5524355810999997
    valeur_normalisee: 0.19769344992530832
    valeur_ponderee: 0.19769344992530832
    ts: '2026-07-30T05:23:09.453093+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6400000000000001
    valeur_normalisee: 0.6336626140466493
    valeur_ponderee: 0.6336626140466493
    ts: '2026-07-30T05:23:09.453093+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  usd_jpy_proxy_risk:
    valeur: 163.49053
    valeur_normalisee: 0.7508082988598123
    valeur_ponderee: 0.7508082988598123
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_eur_nets:
    valeur: -65177.0
    valeur_normalisee: -0.8513400297335095
    valeur_ponderee: -0.8513400297335095
    ts: '2026-07-30T05:23:09.453093+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.003460177301237044
    valeur_normalisee: 0.7544354386580034
    valeur_ponderee: 0.7544354386580034
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.006785083363362254
    valeur_normalisee: 0.7993834031350844
    valeur_ponderee: 0.7993834031350844
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.007652993903994432
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.8076491359199692
    valeur_ponderee: 0.8076491359199692
    ts: '2026-07-30T05:23:09.453093+00:00'
  sox_trend_5j:
    valeur: 465.0
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17455760429654404
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Multiples news de matérialité haute confirment une escalade
      militaire Iran-USA (frappes du 30 juillet) et un débouclage du trade IA (SK
      Hynix, Fed hawkish), dominant les rares signaux longs. Le prix a déjà baissé
      de 10% sur 20j, mais la fraîcheur et la force des news SHORT justifient de maintenir
      la
    nature: ponctuel
    event_id: 322f6c6c8df1
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 77.16666666666673
      7j: 77.16666666666673
      1m: 77.16666666666673
  flux_etf_qqq_5j:
    valeur: -0.0618416406561747
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  spread_nasdaq_russell2000:
    valeur: 373.15996999999993
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  rsi_14j_ixic:
    valeur: 32.427918742910364
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.10139874792507486
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.04932048688136215
    valeur_normalisee: -0.7912998552717248
    valeur_ponderee: -0.7912998552717248
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.03288368042569545
    valeur_normalisee: -0.6945746440235543
    valeur_ponderee: -0.6945746440235543
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.8076491359199692
    valeur_ponderee: 0.8076491359199692
    ts: '2026-07-30T05:23:09.453093+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_nets:
    valeur: 176195.0
    valeur_normalisee: -0.19033380690269922
    valeur_ponderee: -0.19033380690269922
    ts: '2026-07-30T05:23:09.453093+00:00'
  flux_etf_or_5j:
    valeur: -0.021207039987339082
    valeur_normalisee: -0.17389296841151625
    valeur_ponderee: -0.17389296841151625
    ts: '2026-07-30T05:23:09.453093+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: 'Multiples news de matérialité élevée et très récentes (30
      juillet) confirment une escalade militaire majeure entre les États-Unis et l''Iran,
      ce qui est fortement haussier pour l''or. Malgré une baisse de prix de -1.84%
      sur 20 jours, la fraîcheur et la force des news dominent, indiquant un changement '
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 198.29999999999993
      7j: 198.29999999999993
      1m: 198.29999999999993
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-30T05:23:09.453093+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_or:
    valeur: -0.01872254876292423
    valeur_normalisee: 0.3363947545125769
    valeur_ponderee: 0.3363947545125769
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_or:
    valeur: -0.001806435740356216
    valeur_normalisee: 0.20241778045095768
    valeur_ponderee: 0.20241778045095768
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_or:
    valeur: -0.00852642138744042
    valeur_normalisee: -0.07305734498320997
    valeur_ponderee: -0.07305734498320997
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
petrole:
  eia_crude_surprise:
    valeur: 404508.0
    valeur_normalisee: -0.7758900959893141
    valeur_ponderee: -0.7758900959893141
    ts: '2026-07-30T05:23:09.453093+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et très fraîches
      (30 juillet) sur l'escalade US-Iran, malgré une news SHORT isolée le 29 juillet
      et une baisse récente de -8% sur 5 jours. Le conflit ouvert et les menaces sur
      l'offre pétrolière constituent un choc géopolitique majeur non encore pleinement
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 176.73333333333355
      7j: 176.73333333333355
      1m: 176.73333333333355
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
  cftc_cot_crude_nets:
    valeur: 42761.0
    valeur_normalisee: 0.3587204635040612
    valeur_ponderee: 0.3587204635040612
    ts: '2026-07-30T05:23:09.453093+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 173.73333333333383
      7j: 173.73333333333383
      1m: 173.73333333333383
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
    ts: '2026-07-30T05:23:09.453093+00:00'
  cushing_stocks:
    valeur: 18599.0
    valeur_normalisee: -0.8001382957591842
    valeur_ponderee: -0.8001382957591842
    ts: '2026-07-30T05:23:09.453093+00:00'
  spread_brent_wti:
    valeur: 2.6594900000000052
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.22024949038252473
    valeur_normalisee: 0.8020116326402356
    valeur_ponderee: 0.8020116326402356
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.044884635147731
    valeur_normalisee: -0.14713973972088576
    valeur_ponderee: -0.14713973972088576
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.023264136346943687
    valeur_normalisee: 0.2527075874166838
    valeur_ponderee: 0.2527075874166838
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-30T05:23:09.453093+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.019999999999999574
    valeur_normalisee: -0.24940829643493354
    valeur_ponderee: -0.24940829643493354
    ts: '2026-07-30T05:23:09.453093+00:00'
  hy_credit_spread:
    valeur: 2.84
    valeur_normalisee: 0.9280676518097379
    valeur_ponderee: 0.9280676518097379
    ts: '2026-07-30T05:23:09.453093+00:00'
  breadth_sp_ma50:
    valeur: 0.2957393059046608
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.02401620358369061
    valeur_normalisee: -0.8280493297675364
    valeur_ponderee: -0.8280493297675364
    ts: '2026-07-30T05:23:09.453093+00:00'
  shiller_cape_fwd_pe:
    valeur: 39.93
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-30T05:23:09.453093+00:00'
  rsi_14j_gspc:
    valeur: 38.55767835454831
    ts: '2026-07-30T05:23:09.453093+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.8076491359199692
    valeur_ponderee: 0.8076491359199692
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_sp500:
    valeur: -0.02317982717088729
    valeur_normalisee: -0.6913095165441178
    valeur_ponderee: -0.6913095165441178
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.017019507796188105
    valeur_normalisee: -0.586552719898629
    valeur_ponderee: -0.586552719898629
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.012815787866452655
    valeur_normalisee: -0.5568064756904797
    valeur_ponderee: -0.5568064756904797
    ts: '2026-07-30T05:23:09.453093+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.1817535949708365
    valeur_normalisee: 0.09087679748541826
    valeur_ponderee: 0.09087679748541826
    ts: '2026-07-30T05:23:09.453093+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 87.3253
    valeur_normalisee: -0.045208837359253067
    valeur_ponderee: -0.045208837359253067
    ts: '2026-07-30T05:23:09.453093+00:00'
  usd_brl_sucre:
    valeur: 5.12629
    valeur_normalisee: -0.020523568192315007
    valeur_ponderee: -0.020523568192315007
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_sugar:
    valeur: -47496.0
    valeur_normalisee: -0.431259358767976
    valeur_ponderee: -0.431259358767976
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_sucre:
    valeur: -0.02451481103166475
    valeur_normalisee: -0.3416707235338406
    valeur_ponderee: -0.3416707235338406
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.022517911975434846
    valeur_normalisee: -0.34625843189628425
    valeur_ponderee: -0.34625843189628425
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.016477857878475777
    valeur_normalisee: -0.32232351090817285
    valeur_ponderee: -0.32232351090817285
    ts: '2026-07-30T05:23:09.453093+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 36.433333333333294
      7j: 36.433333333333294
      1m: 36.433333333333294
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
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 36.433333333333294
      7j: 36.433333333333294
      1m: 36.433333333333294
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-30T05:23:09.453093+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5899999999999999
    valeur_normalisee: 0.6876192990929171
    valeur_ponderee: 0.6876192990929171
    ts: '2026-07-30T05:23:09.453093+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.0023173191935407234
    valeur_normalisee: -0.8014569432921098
    valeur_ponderee: -0.8014569432921098
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.0015672931136754276
    valeur_normalisee: -0.44093094005354627
    valeur_ponderee: -0.44093094005354627
    ts: '2026-07-30T05:23:09.453093+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.011084031887023338
    valeur_normalisee: 0.3610359366457432
    valeur_ponderee: 0.3610359366457432
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_jpy_nets:
    valeur: -157406.0
    valeur_normalisee: -0.6920714340123324
    valeur_ponderee: -0.6920714340123324
    ts: '2026-07-30T05:23:09.453093+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.9400000000000004
    valeur_normalisee: 0.5634067744273235
    valeur_ponderee: 0.5634067744273235
    ts: '2026-07-30T05:23:09.453093+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-30T05:23:09.453093+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 19.933333333333316
      7j: 19.933333333333316
      1m: 19.933333333333316
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-30T05:23:09.453093+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-30T05:23:09.453093+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-30T05:23:09.453093+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-30T05:23:09.453093+00:00'
  gap_rv_iv:
    valeur: -4.543430390283158
    ts: '2026-07-30T05:23:09.453093+00:00'
  cftc_cot_vix_nets:
    valeur: -76861.0
    valeur_normalisee: -0.47810632841843353
    valeur_ponderee: -0.47810632841843353
    ts: '2026-07-30T05:23:09.453093+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-30T05:23:09.453093+00:00'
    synthese_rationale: Escalade militaire majeure US-Iran avec frappes confirmées
      le 30 juillet, conflit ouvert et menaces sur l'offre pétrolière, dominant largement
      le signal court isolé du 29 juillet. Le prix du VIX a déjà grimpé de +8.74%
      sur 5j, mais la fraîcheur et la matérialité élevée des news du jour justifient
      de
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 224.06666666666646
      7j: 224.06666666666646
      1m: 224.06666666666646
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-30T05:23:09.453093+00:00'
```
