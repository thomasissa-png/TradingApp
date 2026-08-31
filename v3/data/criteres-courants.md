# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-31T05:23:11.289674+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.34
    valeur_normalisee: 0.12772531460076264
    valeur_ponderee: 0.12772531460076264
    ts: '2026-08-31T05:23:11.289674+00:00'
  mouvement_or_5j:
    valeur: -0.03552778298747039
    valeur_normalisee: -0.8033287399895607
    valeur_ponderee: -0.8033287399895607
    ts: '2026-08-31T05:23:11.289674+00:00'
  ratio_gold_silver:
    valeur: 66.55291284734318
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_silver:
    valeur: 23255.0
    valeur_normalisee: -0.2251627248122002
    valeur_ponderee: -0.2251627248122002
    ts: '2026-08-31T05:23:11.289674+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.043048469387755084
    valeur_normalisee: -0.2898076636106049
    valeur_ponderee: -0.2898076636106049
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_argent:
    valeur: 0.029651934723228024
    valeur_normalisee: 0.028592289663494412
    valeur_ponderee: 0.028592289663494412
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_argent:
    valeur: -0.03438121226786928
    valeur_normalisee: -0.5206339333795806
    valeur_ponderee: -0.5206339333795806
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_argent:
    valeur: 0.0031274649835832946
    valeur_normalisee: -0.04421979155264693
    valeur_ponderee: -0.04421979155264693
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-31T05:23:11.289674+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.03562873054698129
    valeur_normalisee: 0.017814365273490645
    valeur_ponderee: 0.017814365273490645
    ts: '2026-08-31T05:23:11.289674+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (frappes
      russes, problèmes d'exportation mer Noire, rallye des grains) malgré une seule
      news SHORT faible. Le prix a déjà monté de +20% sur 20j, mais les news récentes
      (≤48h) confirment et renforcent le biais haussier.
    nature: structurel
    event_id: 813be5de8bfe
    event_date: '2026-08-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 169.6333333333332
      7j: 169.6333333333332
      1m: 169.6333333333332
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -11740.0
    valeur_normalisee: 0.4475969488007501
    valeur_ponderee: 0.4475969488007501
    ts: '2026-08-31T05:23:11.289674+00:00'
  meteo_australie_dryland:
    valeur: -0.04313581958901265
    valeur_normalisee: -0.021567909794506325
    valeur_ponderee: -0.021567909794506325
    ts: '2026-08-31T05:23:11.289674+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_ble:
    valeur: 0.20320288856452118
    valeur_normalisee: 0.8288820576470787
    valeur_ponderee: 0.8288820576470787
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_ble:
    valeur: 0.1110832444604768
    valeur_normalisee: 0.8170274998653472
    valeur_ponderee: 0.8170274998653472
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_ble:
    valeur: -0.010044798774703323
    valeur_normalisee: -0.36850301072240266
    valeur_ponderee: -0.36850301072240266
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-31T05:23:11.289674+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-31T05:23:11.289674+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.014552740956961796
    valeur_normalisee: -0.5008257393488076
    valeur_ponderee: -0.5008257393488076
    ts: '2026-08-31T05:23:11.289674+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.017021276595744594
    valeur_normalisee: -0.5527056897152125
    valeur_ponderee: -0.5527056897152125
    ts: '2026-08-31T05:23:11.289674+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (coûts d'emprunt
      français, guerre commerciale US-Canada, blocage du gaz qatari) et fraîcheur
      récente (26-31 août). Le contexte marché (-1.27% sur 20j) est cohérent avec
      le biais baissier, renforçant la conviction.
    nature: structurel
    event_id: 9e729fce990b
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -219.99999999999963
      7j: -219.99999999999963
      1m: -219.99999999999963
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  rsi_14j_fchi:
    valeur: 42.23341361373883
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_cac40:
    valeur: -0.01274554087610491
    valeur_normalisee: -0.8176135334213982
    valeur_ponderee: -0.8176135334213982
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.011847980995367102
    valeur_normalisee: -0.43395966038854683
    valeur_ponderee: -0.43395966038854683
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.0045052266919795025
    valeur_normalisee: -0.24140255424287563
    valeur_ponderee: -0.24140255424287563
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.04730790428821082
    valeur_normalisee: 0.02365395214410541
    valeur_ponderee: 0.02365395214410541
    ts: '2026-08-31T05:23:11.289674+00:00'
  hf_positioning_flux_options:
    valeur: -18386.0
    valeur_normalisee: -0.6253210381718236
    valeur_ponderee: -0.6253210381718236
    ts: '2026-08-31T05:23:11.289674+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: structurel
    event_id: aa90a870f402
    event_date: '2026-08-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 157.56666666666652
      7j: 157.56666666666652
      1m: 157.56666666666652
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
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Les news récentes (28 août) confirment des risques de récolte
      en Afrique de l'Ouest, et les annonces de baisse de production au Ghana (COCOBOD
      -16%) et l'événement El Niño extrême dominent. Le mouvement de prix (+20% sur
      20j) est cohérent avec ce biais haussier, renforçant la conviction.
    nature: structurel
    event_id: aa90a870f402
    event_date: '2026-08-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 162.13333333333316
      7j: 162.13333333333316
      1m: 162.13333333333316
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.20277325753075393
    valeur_normalisee: 0.330273412925577
    valeur_ponderee: 0.330273412925577
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.12138997210078983
    valeur_normalisee: 0.5185921358286956
    valeur_ponderee: 0.5185921358286956
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.0023053644535464546
    valeur_normalisee: -0.11104945792969126
    valeur_ponderee: -0.11104945792969126
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-31T05:23:11.289674+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.3774764309805664
    valeur_normalisee: 0.1887382154902832
    valeur_ponderee: 0.1887382154902832
    ts: '2026-08-31T05:23:11.289674+00:00'
  usd_brl:
    valeur: 5.19497
    valeur_normalisee: 0.6769625257020098
    valeur_ponderee: 0.6769625257020098
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_coffee:
    valeur: 30746.0
    valeur_normalisee: -0.09318554391505972
    valeur_ponderee: -0.09318554391505972
    ts: '2026-08-31T05:23:11.289674+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: 'Signaux contradictoires : baisse récente des prix (Arabica
      -4%, Robusta attendu en baisse) et pressions baissières (récolte brésilienne,
      exportations indiennes) contre soutiens haussiers (stocks ICE bas, El Niño,
      hausse Robusta). Prix quasi stable sur 20j, -2.58% sur 5j, pas de signal dominant
      clair'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 237.80000000000007
      7j: 237.80000000000007
      1m: 237.80000000000007
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-31T05:23:11.289674+00:00'
  meteo_vietnam_robusta:
    valeur: 0.5221572242852129
    valeur_normalisee: 0.26107861214260647
    valeur_ponderee: 0.26107861214260647
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.00017835278699251944
    valeur_normalisee: -0.2928424628402702
    valeur_ponderee: -0.2928424628402702
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.08506865537899211
    valeur_normalisee: -0.8076659722186298
    valeur_ponderee: -0.8076659722186298
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.0003666866490530385
    valeur_normalisee: -0.01834112132768021
    valeur_ponderee: -0.01834112132768021
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-31T05:23:11.289674+00:00'
coton:
  meteo_texas_cotton_precip:
    ts: '2026-08-31T05:23:11.289674+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-28'
    valeur: 0.019694853294887994
    valeur_normalisee: 0.009847426647443997
    valeur_ponderee: 0.009847426647443997
    reporte_cause: source réseau indisponible
  meteo_inde_gujarat_coton:
    valeur: 0.8039928279095101
    valeur_normalisee: 0.40199641395475505
    valeur_ponderee: 0.40199641395475505
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_cotton:
    valeur: 127183.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_coton:
    valeur: 0.13076311605723379
    valeur_normalisee: 0.8074429907178463
    valeur_ponderee: 0.8074429907178463
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_coton:
    valeur: 0.043270993766043375
    valeur_normalisee: 0.4288992427189524
    valeur_ponderee: 0.4288992427189524
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_coton:
    valeur: 0.040219378427788
    valeur_normalisee: 0.7219050744395582
    valeur_ponderee: 0.7219050744395582
    ts: '2026-08-31T05:23:11.289674+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: structurel
    event_id: 2374791f65df
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 99.80000000000018
      7j: 99.80000000000018
      1m: 99.80000000000018
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-31T05:23:11.289674+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Les nouvelles récentes (31 août) montrent une contraction
      manufacturière chinoise et un rebond de l'offre chilienne, signalant un biais
      baissier. Malgré quelques nouvelles haussières (droits de douane US, demande
      électrique), le poids des nouvelles SHORT récentes et la stabilité du prix suggèrent
      un
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '12.22'
    p2_shadow_contrib_exclu:
      24h: 56.20000000000004
      7j: 56.20000000000004
      1m: 56.20000000000004
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_copper_nets:
    valeur: 84321.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: ponctuel
    event_id: 61d32360b04b
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 59.499999999999986
      7j: 59.499999999999986
      1m: 59.499999999999986
  ratio_cuivre_or:
    valeur: 0.0014846851864121196
    valeur_normalisee: -0.31357659322133863
    valeur_ponderee: -0.31357659322133863
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.005039070947759683
    valeur_normalisee: -0.36861237501526817
    valeur_ponderee: -0.36861237501526817
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.002413975584274475
    valeur_normalisee: -0.3042945895385341
    valeur_ponderee: -0.3042945895385341
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.005078088597674446
    valeur_normalisee: 0.050200627087418015
    valeur_ponderee: 0.050200627087418015
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.414941888
    valeur_normalisee: -0.7685415248884641
    valeur_ponderee: -0.7685415248884641
    ts: '2026-08-31T05:23:11.289674+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6999999999999997
    valeur_normalisee: 0.42644284357209983
    valeur_ponderee: 0.42644284357209983
    ts: '2026-08-31T05:23:11.289674+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.81393
    valeur_normalisee: -0.17806108392312361
    valeur_ponderee: -0.17806108392312361
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_eur_nets:
    valeur: -53872.0
    valeur_normalisee: -0.7461352509219135
    valeur_ponderee: -0.7461352509219135
    ts: '2026-08-31T05:23:11.289674+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.004011019474668975
    valeur_normalisee: -0.041556097093680654
    valeur_ponderee: -0.041556097093680654
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.006412729439400744
    valeur_normalisee: -0.7150327854917689
    valeur_ponderee: -0.7150327854917689
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.0005525291156944778
    valeur_normalisee: -0.025787680454653322
    valeur_ponderee: -0.025787680454653322
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.34
    valeur_normalisee: 0.12772531460076264
    valeur_ponderee: 0.12772531460076264
    ts: '2026-08-31T05:23:11.289674+00:00'
  sox_trend_5j:
    valeur: 508.62
    valeur_normalisee: -0.5811844371061993
    valeur_ponderee: -0.5811844371061993
    ts: '2026-08-31T05:23:11.289674+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17066566406579378
    valeur_normalisee: 0.4898216643373725
    valeur_ponderee: 0.4898216643373725
    ts: '2026-08-31T05:23:11.289674+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Les news récentes sont dominées par des signaux SHORT (escalade
      Iran, ton hawkish de Warsh) mais contrebalancées par des résultats Nvidia très
      positifs (croissance 70%, bénéfice doublé). Le prix a déjà monté de 4.13% sur
      20j, suggérant que le positif est pricé, et les signaux contradictoires ne perm
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 181.9999999999999
      7j: 181.9999999999999
      1m: 181.9999999999999
  flux_etf_qqq_5j:
    valeur: 0.004190948082529511
    valeur_normalisee: 0.07194091028009873
    valeur_ponderee: 0.07194091028009873
    ts: '2026-08-31T05:23:11.289674+00:00'
  spread_nasdaq_russell2000:
    valeur: 420.67999
    valeur_normalisee: 0.10883698928358955
    valeur_ponderee: 0.10883698928358955
    ts: '2026-08-31T05:23:11.289674+00:00'
  rsi_14j_ixic:
    valeur: 50.91802703256087
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.04133781074343812
    valeur_normalisee: 0.5696220847390193
    valeur_ponderee: 0.5696220847390193
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.0004887344873358845
    valeur_normalisee: 0.06242459017488128
    valeur_ponderee: 0.06242459017488128
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.008034134738045928
    valeur_normalisee: 0.19264997367097006
    valeur_ponderee: 0.19264997367097006
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.34
    valeur_normalisee: 0.12772531460076264
    valeur_ponderee: 0.12772531460076264
    ts: '2026-08-31T05:23:11.289674+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_nets:
    valeur: 242212.0
    valeur_normalisee: 0.38662879828456004
    valeur_ponderee: 0.38662879828456004
    ts: '2026-08-31T05:23:11.289674+00:00'
  flux_etf_or_5j:
    valeur: -0.03417890292372683
    valeur_normalisee: -0.5146408562935129
    valeur_ponderee: -0.5146408562935129
    ts: '2026-08-31T05:23:11.289674+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Escalade géopolitique majeure (frappes US sur l'Iran, menaces
      sur Kharg, riposte iranienne) domine, avec matérialité élevée et fraîcheur immédiate.
      Les signaux hawkish de la Fed sont présents mais secondaires face au risque
      de conflit.
    nature: verbal
    event_id: 2046b4758b7c
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 567.9999999999983
      7j: 567.9999999999983
      1m: 567.9999999999983
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-31T05:23:11.289674+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_or:
    valeur: 0.01454605986285129
    valeur_normalisee: -0.13605299050792535
    valeur_ponderee: -0.13605299050792535
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_or:
    valeur: -0.04748739196575791
    valeur_normalisee: -0.9632559568265767
    valeur_ponderee: -0.9632559568265767
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_or:
    valeur: -0.005652816273029937
    valeur_normalisee: -0.2464222261717245
    valeur_ponderee: -0.2464222261717245
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-31T05:23:11.289674+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-28'
    valeur: 428910.0
    valeur_normalisee: -0.010699044988311703
    valeur_ponderee: -0.010699044988311703
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Escalade militaire US-Iran avec frappes sur Larak et menace
      sur Kharg Island, confirmée et fraîche, domine nettement. Les signaux baissiers
      (Venezuela, Chine) sont secondaires et plus anciens.
    nature: verbal
    event_id: 2046b4758b7c
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 529.2333333333308
      7j: 529.2333333333308
      1m: 529.2333333333308
  cftc_cot_crude_nets:
    valeur: 17068.0
    valeur_normalisee: -0.1877382283014539
    valeur_ponderee: -0.1877382283014539
    ts: '2026-08-31T05:23:11.289674+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: verbal
    event_id: 2046b4758b7c
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 496.5999999999971
      7j: 496.5999999999971
      1m: 496.5999999999971
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
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  cushing_stocks:
    valeur: 22428.0
    valeur_normalisee: -0.18311536903012807
    valeur_ponderee: -0.18311536903012807
    ts: '2026-08-31T05:23:11.289674+00:00'
  spread_brent_wti:
    valeur: 3.611080000000001
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.07619549637745138
    valeur_normalisee: 0.3292153080158318
    valeur_ponderee: 0.3292153080158318
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.02543233829825564
    valeur_normalisee: -0.11678317304280388
    valeur_ponderee: -0.11678317304280388
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.03325767193405382
    valeur_normalisee: 0.2714894783085181
    valeur_ponderee: 0.2714894783085181
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-31T05:23:11.289674+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.020000000000000462
    valeur_normalisee: -0.28444093205310317
    valeur_ponderee: -0.28444093205310317
    ts: '2026-08-31T05:23:11.289674+00:00'
  hy_credit_spread:
    valeur: 2.63
    valeur_normalisee: -0.9196039481997228
    valeur_ponderee: -0.9196039481997228
    ts: '2026-08-31T05:23:11.289674+00:00'
  breadth_sp_ma50:
    valeur: 0.28685254531364257
    valeur_normalisee: 0.12056784851914465
    valeur_ponderee: 0.12056784851914465
    ts: '2026-08-31T05:23:11.289674+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.004740649509245465
    valeur_normalisee: 0.06640644189704538
    valeur_ponderee: 0.06640644189704538
    ts: '2026-08-31T05:23:11.289674+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.17
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  rsi_14j_gspc:
    valeur: 56.366181174679575
    ts: '2026-08-31T05:23:11.289674+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.34
    valeur_normalisee: 0.12772531460076264
    valeur_ponderee: 0.12772531460076264
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.029878251386866284
    valeur_normalisee: 0.46939132369575903
    valeur_ponderee: 0.46939132369575903
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.0003770603083688151
    valeur_normalisee: -0.03897905467653
    valeur_ponderee: -0.03897905467653
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.004491402560016233
    valeur_normalisee: 0.12827782441790658
    valeur_ponderee: 0.12827782441790658
    ts: '2026-08-31T05:23:11.289674+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.3965019427682916
    valeur_normalisee: 0.1982509713841458
    valeur_ponderee: 0.1982509713841458
    ts: '2026-08-31T05:23:11.289674+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 89.34887
    valeur_normalisee: 0.4412755298197978
    valeur_ponderee: 0.4412755298197978
    ts: '2026-08-31T05:23:11.289674+00:00'
  usd_brl_sucre:
    valeur: 5.19497
    valeur_normalisee: 0.6769625257020098
    valeur_ponderee: 0.6769625257020098
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_sugar:
    valeur: 180943.0
    valeur_normalisee: 0.4810257086697616
    valeur_ponderee: 0.4810257086697616
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.16528066528066554
    valeur_normalisee: 0.8803285928411226
    valeur_ponderee: 0.8803285928411226
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.002669039145907437
    valeur_normalisee: -0.25459379136630006
    valeur_ponderee: -0.25459379136630006
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.00900090009000909
    valeur_normalisee: 0.025456048193883942
    valeur_ponderee: 0.025456048193883942
    ts: '2026-08-31T05:23:11.289674+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: structurel
    event_id: 7ae3213754cf
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 72.1333333333335
      7j: 72.1333333333335
      1m: 72.1333333333335
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
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: structurel
    event_id: 7ae3213754cf
    event_date: '2026-08-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 72.1333333333335
      7j: 72.1333333333335
      1m: 72.1333333333335
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-31T05:23:11.289674+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5300000000000002
    valeur_normalisee: 0.11707635088741696
    valeur_ponderee: 0.11707635088741696
    ts: '2026-08-31T05:23:11.289674+00:00'
  dxy_trend_20j:
    valeur: 118.0628
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.004430862851048545
    valeur_normalisee: 0.21947657918453295
    valeur_ponderee: 0.21947657918453295
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.0019535283955491867
    valeur_normalisee: -0.07539967215414323
    valeur_ponderee: -0.07539967215414323
    ts: '2026-08-31T05:23:11.289674+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.003139121125179667
    valeur_normalisee: 0.21873223969149394
    valeur_ponderee: 0.21873223969149394
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_jpy_nets:
    valeur: -62792.0
    valeur_normalisee: -0.11127193802612544
    valeur_ponderee: -0.11127193802612544
    ts: '2026-08-31T05:23:11.289674+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0
    valeur_normalisee: 0.4264428435720987
    valeur_ponderee: 0.4264428435720987
    ts: '2026-08-31T05:23:11.289674+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-31T05:23:11.289674+00:00'
    nature: verbal
    event_id: d8f9a9fb0fed
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -1.8999999999999542
      7j: -1.8999999999999542
      1m: -1.8999999999999542
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-31T05:23:11.289674+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-31T05:23:11.289674+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-31T05:23:11.289674+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-31T05:23:11.289674+00:00'
  gap_rv_iv:
    valeur: -4.7662966500576385
    ts: '2026-08-31T05:23:11.289674+00:00'
  cftc_cot_vix_nets:
    valeur: -78164.0
    valeur_normalisee: -0.5083978702949855
    valeur_ponderee: -0.5083978702949855
    ts: '2026-08-31T05:23:11.289674+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-31T05:23:11.289674+00:00'
    synthese_rationale: Escalade majeure Iran/US avec frappes sur Larak et menace
      sur Kharg Island, risque sur le détroit d'Ormuz, domine malgré le repli récent
      du VIX. La fraîcheur et la matérialité élevée des news justifient de contrebalancer
      le mouvement de prix.
    nature: verbal
    event_id: 2046b4758b7c
    event_date: '2026-08-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 550.9333333333304
      7j: 550.9333333333304
      1m: 550.9333333333304
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-31T05:23:11.289674+00:00'
```
