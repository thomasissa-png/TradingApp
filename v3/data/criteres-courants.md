# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-29T05:23:48.187098+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 0.6234832894461405
    valeur_ponderee: 0.6234832894461405
    ts: '2026-06-29T05:23:48.187098+00:00'
  mouvement_or_5j:
    valeur: 0.013463836147843633
    valeur_normalisee: 0.5481721193604399
    valeur_ponderee: 0.5481721193604399
    ts: '2026-06-29T05:23:48.187098+00:00'
  ratio_gold_silver:
    valeur: 69.59428913180511
    ts: '2026-06-29T05:23:48.187098+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  cftc_cot_silver:
    valeur: 23389.0
    valeur_normalisee: -0.22071937560278862
    valeur_ponderee: -0.22071937560278862
    ts: '2026-06-29T05:23:48.187098+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.1046882876827423
    valeur_normalisee: -0.6149333815614358
    valeur_ponderee: -0.6149333815614358
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_argent:
    valeur: -0.10857108232309809
    valeur_normalisee: -0.3207731409338019
    valeur_ponderee: -0.3207731409338019
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_argent:
    valeur: -0.10511195148090735
    valeur_normalisee: -0.5355035765908519
    valeur_ponderee: -0.5355035765908519
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-29T05:23:48.187098+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.3167060139394853
    valeur_normalisee: 0.15835300696974264
    valeur_ponderee: 0.15835300696974264
    ts: '2026-06-29T05:23:48.187098+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: Majoritarily LONG news (USDA crop issues, El Niño, Ukraine/Russia
      tensions) but market price -1.75% over 5 days suggests these are already priced
      in. A few SHORT signals (strong dollar, fertilizer ships) add uncertainty. No
      dominant fresh high-materiality signal to override price action.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: -21.333333333333304
      7j: -21.333333333333304
      1m: -21.333333333333304
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -61072.0
    valeur_normalisee: -0.23819600021494963
    valeur_ponderee: -0.23819600021494963
    ts: '2026-06-29T05:23:48.187098+00:00'
  meteo_australie_dryland:
    valeur: 0.09673736570538352
    valeur_normalisee: 0.04836868285269176
    valeur_ponderee: 0.04836868285269176
    ts: '2026-06-29T05:23:48.187098+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_ble:
    valeur: -0.012468095517055522
    valeur_normalisee: -0.07695496386276472
    valeur_ponderee: -0.07695496386276472
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_ble:
    valeur: -0.03653625027150864
    valeur_normalisee: -0.34411910894232456
    valeur_ponderee: -0.34411910894232456
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-29T05:23:48.187098+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-06-29T05:23:48.187098+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.013955327100095505
    valeur_normalisee: 0.4302568717965671
    valeur_ponderee: 0.4302568717965671
    ts: '2026-06-29T05:23:48.187098+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.02161100196463661
    valeur_normalisee: -0.5384343384839736
    valeur_ponderee: -0.5384343384839736
    ts: '2026-06-29T05:23:48.187098+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée et fraîcheur
      récente (tensions Iran/US, guerre, contraction PIB zone euro, menaces tarifaires
      Trump) malgré quelques signaux LONG plus anciens. Le prix a légèrement baissé
      sur 5j, cohérent avec le biais baissier.
    nature: structurel
    event_id: 68cc3ee14491
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -61.43333333333332
      7j: -61.43333333333332
      1m: -61.43333333333332
    sign_conflict: true
    sign_conflict_details:
    - event_id: eb6dec57006e
      asset: CAC40
      rule_name: fed_actions
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: bce
      matched_surprise: hawkish
      surprise_polarity: up
      title: Les rendements de la zone euro proches de plus bas de 3 mois, les craintes
        de croissance limitent le ton hawkish de la BCE
  rsi_14j_fchi:
    valeur: 55.35295618736706
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.024626898545129894
    valeur_normalisee: 0.11409518042503793
    valeur_ponderee: 0.11409518042503793
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.0054466923956275615
    valeur_normalisee: -0.3116839053910585
    valeur_ponderee: -0.3116839053910585
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -27525.0
    valeur_normalisee: -0.8248926081081333
    valeur_ponderee: -0.8248926081081333
    ts: '2026-06-29T05:23:48.187098+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: structurel
    event_id: c38af322cc46
    event_date: '2026-06-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 8.3
      7j: 8.3
      1m: 8.3
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
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: 'Signal LONG dominant avec matérialité élevée et fraîcheur
      : El Niño et craintes sur les récoltes ouest-africaines (news high du 25 juin,
      23 juin) confirment la tendance haussière. Le prix a déjà monté de +33% sur
      20j, mais les news récentes (≤48h) à matérialité high renforcent le biais, justifiant
      u'
    nature: structurel
    event_id: c38af322cc46
    event_date: '2026-06-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 8.3
      7j: 8.3
      1m: 8.3
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.33476701493051886
    valeur_normalisee: 0.8146132365533485
    valeur_ponderee: 0.8146132365533485
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.11042605732436028
    valeur_normalisee: 0.2762795740204275
    valeur_ponderee: 0.2762795740204275
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-29T05:23:48.187098+00:00'
  meteo_ci_ghana_precip_30j:
    valeur: 0.9950209185486898
    valeur_normalisee: 0.4975104592743449
    valeur_ponderee: 0.4975104592743449
    ts: '2026-06-29T05:23:48.187098+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.33647484859011906
    valeur_normalisee: 0.16823742429505953
    valeur_ponderee: 0.16823742429505953
    ts: '2026-06-29T05:23:48.187098+00:00'
  usd_brl:
    valeur: 5.17199
    valeur_normalisee: 0.6194380094096356
    valeur_ponderee: 0.6194380094096356
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_coffee:
    valeur: 10724.0
    valeur_normalisee: -0.49837226534013546
    valeur_ponderee: -0.49837226534013546
    ts: '2026-06-29T05:23:48.187098+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: Dominance de news LONG récentes (hausse robusta/arabica, pluies
      Brésil, Super El Niño) avec matérialité medium à high, malgré quelques SHORT
      anciens. Le prix a déjà monté de +11% sur 20j, mais les news fraîches (25-24
      juin) confirment le momentum.
    nature: structurel
    event_id: e0949e4a1a58
    event_date: '2026-06-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 55.56666666666667
      7j: 55.56666666666667
      1m: 55.56666666666667
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
    ts: '2026-06-29T05:23:48.187098+00:00'
  meteo_vietnam_robusta:
    valeur: 0.06353764901042196
    valeur_normalisee: 0.03176882450521098
    valeur_ponderee: 0.03176882450521098
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.1123622574997114
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.025864940898340905
    valeur_normalisee: 0.375808618270211
    valeur_ponderee: 0.375808618270211
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-29T05:23:48.187098+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.3184602880055196
    valeur_normalisee: 0.1592301440027598
    valeur_ponderee: 0.1592301440027598
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_cotton:
    valeur: 84973.0
    valeur_normalisee: 0.6158899306252916
    valeur_ponderee: 0.6158899306252916
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_coton:
    valeur: -0.054909819639278545
    valeur_normalisee: -0.41127691597855753
    valeur_ponderee: -0.41127691597855753
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_coton:
    valeur: -0.039315542880423604
    valeur_normalisee: -0.4463768563962919
    valeur_ponderee: -0.4463768563962919
    ts: '2026-06-29T05:23:48.187098+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.21
    materiality: low
    reliability: reported
    source_track: ia
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: ponctuel
    event_id: 2dadecfc401c
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-29T05:23:48.187098+00:00'
  meteo_inde_gujarat_coton:
    valeur: -0.24952385683679618
    valeur_normalisee: 0.12476192841839809
    valeur_ponderee: 0.12476192841839809
    ts: '2026-06-29T05:23:48.187098+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: Plusieurs news récentes à matérialité élevée (IA infrastructure,
      record du cuivre) soutiennent une demande structurelle forte, dominant les signaux
      baissiers plus anciens ou de moindre matérialité. Le prix a baissé de 2.94%
      sur 20j mais rebondi de 2.50% sur 5j, suggérant que le marché intègre déjà l
    nature: structurel
    event_id: 80bd37f67f01
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 4.3999999999999995
      7j: 4.3999999999999995
      1m: 4.3999999999999995
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_copper_nets:
    valeur: 73012.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-29T05:23:48.187098+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: structurel
    event_id: 80bd37f67f01
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 18.733333333333334
      7j: 18.733333333333334
      1m: 18.733333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.0015111644292892187
    valeur_normalisee: 0.5732156448500557
    valeur_ponderee: 0.5732156448500557
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.029421081808822414
    valeur_normalisee: -0.5833383170015124
    valeur_ponderee: -0.5833383170015124
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.03559383120000126
    valeur_normalisee: -0.5096985320046589
    valeur_ponderee: -0.5096985320046589
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6143008750999996
    valeur_normalisee: 0.8125042928871419
    valeur_ponderee: 0.8125042928871419
    ts: '2026-06-29T05:23:48.187098+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.3535000000000004
    valeur_normalisee: -0.24226010501512807
    valeur_ponderee: -0.24226010501512807
    ts: '2026-06-29T05:23:48.187098+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  usd_jpy_proxy_risk:
    valeur: 161.79763
    valeur_normalisee: 0.7458258542950488
    valeur_ponderee: 0.7458258542950488
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_eur_nets:
    valeur: -24754.0
    valeur_normalisee: -0.591011209184829
    valeur_ponderee: -0.591011209184829
    ts: '2026-06-29T05:23:48.187098+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.013721176001801783
    valeur_normalisee: -0.5459399171001359
    valeur_ponderee: -0.5459399171001359
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.0037885747784166535
    valeur_normalisee: -0.03689289624445031
    valeur_ponderee: -0.03689289624445031
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 0.6234832894461405
    valeur_ponderee: 0.6234832894461405
    ts: '2026-06-29T05:23:48.187098+00:00'
  sox_trend_5j:
    valeur: 589.94
    valeur_normalisee: 0.5024679801779851
    valeur_ponderee: 0.5024679801779851
    ts: '2026-06-29T05:23:48.187098+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1679782548837045
    valeur_normalisee: 0.7293639097030042
    valeur_ponderee: 0.7293639097030042
    ts: '2026-06-29T05:23:48.187098+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée et fraîcheur
      récente : restrictions chinoises, baisse des ventes de Nvidia en Chine, rout
      technologique asiatique, hausse de taux anticipée par Kashkari, et demande de
      guerre contre l''Iran. Le contexte de prix (-4.6% sur 5j) confirme le biais
      baissier, sa'
    nature: structurel
    event_id: 0f10918805f7
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 28.83333333333333
      7j: 28.83333333333333
      1m: 28.83333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  flux_etf_qqq_5j:
    valeur: -0.04604247792390159
    valeur_normalisee: -0.9496676060619116
    valeur_ponderee: -0.9496676060619116
    ts: '2026-06-29T05:23:48.187098+00:00'
  spread_nasdaq_russell2000:
    valeur: 406.69003000000004
    valeur_normalisee: 0.006577755395701367
    valeur_ponderee: 0.006577755395701367
    ts: '2026-06-29T05:23:48.187098+00:00'
  rsi_14j_ixic:
    valeur: 46.4634300753535
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.039532301237963474
    valeur_normalisee: -0.8744149963747578
    valeur_ponderee: -0.8744149963747578
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.03197869498230743
    valeur_normalisee: -0.813194035741357
    valeur_ponderee: -0.813194035741357
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 0.6234832894461405
    valeur_ponderee: 0.6234832894461405
    ts: '2026-06-29T05:23:48.187098+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_nets:
    valeur: 172884.0
    valeur_normalisee: -0.2243003459079453
    valeur_ponderee: -0.2243003459079453
    ts: '2026-06-29T05:23:48.187098+00:00'
  flux_etf_or_5j:
    valeur: -0.034847075842116215
    valeur_normalisee: -0.40009113556449644
    valeur_ponderee: -0.40009113556449644
    ts: '2026-06-29T05:23:48.187098+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: Multiples news high matérialité récentes (28-29 juin) confirment
      une escalade US-Iran et des frappes au Moyen-Orient, dominant les signaux SHORT
      plus anciens ou de moindre matérialité. Le prix a baissé de -4.79% sur 20j mais
      rebondit de +1.37% sur 5j, suggérant que le marché intègre déjà le risque g
    nature: structurel
    event_id: 7ac502230404
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 83.70000000000003
      7j: 83.70000000000003
      1m: 83.70000000000003
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-29T05:23:48.187098+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_or:
    valeur: -0.0481443982141182
    valeur_normalisee: -0.11888994035770274
    valeur_ponderee: -0.11888994035770274
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_or:
    valeur: -0.03263481382703404
    valeur_normalisee: -0.328351071925935
    valeur_ponderee: -0.328351071925935
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: 'Signaux contradictoires : accord de pause des hostilités
      (SHORT) vs reprise des frappes (LONG) le même jour, avec baisse massive des
      prix (-23.81% sur 20j) suggérant que le marché a déjà intégré les tensions.
      Aucun signal dominant clair.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 141.13333333333352
      7j: 141.13333333333352
      1m: 141.13333333333352
  cftc_cot_crude_nets:
    valeur: 43084.0
    valeur_normalisee: 0.373459397087807
    valeur_ponderee: 0.373459397087807
    ts: '2026-06-29T05:23:48.187098+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 65.90000000000003
      7j: 65.90000000000003
      1m: 65.90000000000003
    sign_conflict: true
    sign_conflict_details:
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
    - event_id: e4081bee17c1
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de brut
      matched_surprise: baisse
      surprise_polarity: down
      title: Optimisme sur la réouverture du détroit d'Ormuz, baisse des prix du brut
        et de l'essence, mais stocks bas et contraintes logistiques
    - event_id: d680e22bc9c3
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: chute
      surprise_polarity: down
      title: Les prix des biens de grande consommation ne devraient pas baisser malgré
        la chute du brut sous 80 $, en raison de stocks achetés lors du conflit au-dessus
        de 1
    - event_id: bae1728ca145
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: baisse
      surprise_polarity: down
      title: Les stocks de pétrole restent élevés malgré la baisse des prix, suggérant
        un décalage entre prix et fondamentaux
    - event_id: 5aa3a2e9d5a3
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse des stocks de brut inférieure aux prévisions, signaux de demande
        mitigés
    - event_id: 34a7e1cc4307
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: oil stocks
      matched_surprise: hausse
      surprise_polarity: up
      title: Avertissement des dirigeants pétroliers sur des stocks bas et une hausse
        des prix de l'essence cet été
    - event_id: 3d89aa578c9d
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut US en baisse, mais moins que prévu
    - event_id: 0c1807e7a1bb
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: increased
      surprise_polarity: up
      title: U.S. crude oil inventories fell for the seventh consecutive week, refineries
        increased capacity use
    - event_id: a2dbe0286308
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stockpiles
      matched_surprise: draws
      surprise_polarity: down
      title: China draws crude oil stockpiles to offset Middle East supply disruption
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  cushing_stocks:
    valeur: 18957.0
    valeur_normalisee: -0.8758656777574757
    valeur_ponderee: -0.8758656777574757
    ts: '2026-06-29T05:23:48.187098+00:00'
  spread_brent_wti:
    valeur: 3.0832400000000035
    ts: '2026-06-29T05:23:48.187098+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-29T05:23:48.187098+00:00'
    note: hors fenêtre
  momentum_prix_20j_petrole:
    valeur: -0.2381009259362702
    valeur_normalisee: -0.7297874066005101
    valeur_ponderee: -0.7297874066005101
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.1041650656186216
    valeur_normalisee: -0.3780708660597054
    valeur_ponderee: -0.3780708660597054
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-29T05:23:48.187098+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.08999999999999986
    valeur_normalisee: -0.5913500332861878
    valeur_ponderee: -0.5913500332861878
    ts: '2026-06-29T05:23:48.187098+00:00'
  hy_credit_spread:
    valeur: 2.78
    valeur_normalisee: -0.07850481003559777
    valeur_ponderee: -0.07850481003559777
    ts: '2026-06-29T05:23:48.187098+00:00'
  breadth_sp_ma50:
    valeur: 0.28849504504170215
    valeur_normalisee: 0.5308444907131216
    valeur_ponderee: 0.5308444907131216
    ts: '2026-06-29T05:23:48.187098+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.02376998719460577
    valeur_normalisee: -0.7658052433217503
    valeur_ponderee: -0.7658052433217503
    ts: '2026-06-29T05:23:48.187098+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.7
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-29T05:23:48.187098+00:00'
  rsi_14j_gspc:
    valeur: 43.03038731907584
    ts: '2026-06-29T05:23:48.187098+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 0.6234832894461405
    valeur_ponderee: 0.6234832894461405
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_sp500:
    valeur: -0.03393849811657812
    valeur_normalisee: -0.8623053607864337
    valeur_ponderee: -0.8623053607864337
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.02844085859712764
    valeur_normalisee: -0.8833225188143218
    valeur_ponderee: -0.8833225188143218
    ts: '2026-06-29T05:23:48.187098+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
sucre:
  brent_ethanol_proxy_sucre:
    valeur: 72.97208
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-29T05:23:48.187098+00:00'
  usd_brl_sucre:
    valeur: 5.17199
    valeur_normalisee: 0.6194380094096356
    valeur_ponderee: 0.6194380094096356
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_sugar:
    valeur: -137708.0
    valeur_normalisee: -0.7941371369128345
    valeur_ponderee: -0.7941371369128345
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.0067991631799162455
    valeur_normalisee: 0.17869888492497996
    valeur_ponderee: 0.17869888492497996
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.013157894736842035
    valeur_normalisee: 0.2769689831200679
    valeur_ponderee: 0.2769689831200679
    ts: '2026-06-29T05:23:48.187098+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: structurel
    event_id: 8e20b1202b46
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
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
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: structurel
    event_id: 8e20b1202b46
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-29T05:23:48.187098+00:00'
  meteo_bresil_canne_sucre:
    valeur: -0.17744248658840586
    valeur_normalisee: 0.08872124329420293
    valeur_ponderee: 0.08872124329420293
    ts: '2026-06-29T05:23:48.187098+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.44
    valeur_normalisee: 0.4262344770613197
    valeur_ponderee: 0.4262344770613197
    ts: '2026-06-29T05:23:48.187098+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.0012084610091263048
    valeur_normalisee: -0.04699731712460963
    valeur_ponderee: -0.04699731712460963
    ts: '2026-06-29T05:23:48.187098+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.00896883720205155
    valeur_normalisee: 0.23018033984325442
    valeur_ponderee: 0.23018033984325442
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_jpy_nets:
    valeur: -154291.0
    valeur_normalisee: -0.6891872690995869
    valeur_ponderee: -0.6891872690995869
    ts: '2026-06-29T05:23:48.187098+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.7500000000000004
    valeur_normalisee: -0.6008722909380724
    valeur_ponderee: -0.6008722909380724
    ts: '2026-06-29T05:23:48.187098+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-06-29T05:23:48.187098+00:00'
    nature: verbal
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-29T05:23:48.187098+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-29T05:23:48.187098+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-29T05:23:48.187098+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-29T05:23:48.187098+00:00'
  gap_rv_iv:
    valeur: 1.3487188800498302
    ts: '2026-06-29T05:23:48.187098+00:00'
  cftc_cot_vix_nets:
    valeur: -66774.0
    valeur_normalisee: -0.2774757397104772
    valeur_ponderee: -0.2774757397104772
    ts: '2026-06-29T05:23:48.187098+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-29T05:23:48.187098+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et fraîches (28-29
      juin) dominent, malgré quelques news SHORT plus anciennes. Le prix VIX a baissé
      sur 20j mais rebondit sur 5j, cohérent avec l'escalade récente.
    nature: structurel
    event_id: 7ac502230404
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 75.06666666666669
      7j: 75.06666666666669
      1m: 75.06666666666669
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-29T05:23:48.187098+00:00'
```
