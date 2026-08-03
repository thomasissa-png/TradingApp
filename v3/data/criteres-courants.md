# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-03T05:23:02.656856+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.7644380868457178
    valeur_ponderee: 0.7644380868457178
    ts: '2026-08-03T05:23:02.656856+00:00'
  mouvement_or_5j:
    valeur: -0.002331144210928504
    valeur_normalisee: 0.1212523452685901
    valeur_ponderee: 0.1212523452685901
    ts: '2026-08-03T05:23:02.656856+00:00'
  ratio_gold_silver:
    valeur: 69.79347830948392
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_silver:
    valeur: 20236.0
    valeur_normalisee: -0.31454313983426346
    valeur_ponderee: -0.31454313983426346
    ts: '2026-08-03T05:23:02.656856+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.004373455029473394
    valeur_normalisee: 0.08934295400413285
    valeur_ponderee: 0.08934295400413285
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_argent:
    valeur: -0.009631893177017292
    valeur_normalisee: 0.783667065639802
    valeur_ponderee: 0.783667065639802
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_argent:
    valeur: -0.004601572036850854
    valeur_normalisee: 0.19568580931826265
    valeur_ponderee: 0.19568580931826265
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_argent:
    valeur: 0.009029270936615541
    valeur_normalisee: 0.24418357397647017
    valeur_ponderee: 0.24418357397647017
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.25412379720503014
    valeur_normalisee: 0.12706189860251507
    valeur_ponderee: 0.12706189860251507
    ts: '2026-08-03T05:23:02.656856+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: Les news récentes sont majoritairement LONG, dominées par
      les risques d'exportation en mer Noire et la baisse prévue des stocks mondiaux
      par l'USDA. Cependant, le prix a baissé de 3.62% sur 5 jours, suggérant que
      le marché a déjà intégré ces facteurs, ce qui réduit la conviction.
    nature: structurel
    event_id: fd630a45bbcc
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '11.22'
    p2_shadow_contrib_exclu:
      24h: 75.83333333333337
      7j: 75.83333333333337
      1m: 75.83333333333337
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -5384.0
    valeur_normalisee: 0.5293592418323769
    valeur_ponderee: 0.5293592418323769
    ts: '2026-08-03T05:23:02.656856+00:00'
  meteo_australie_dryland:
    valeur: -0.06238797257227118
    valeur_normalisee: -0.03119398628613559
    valeur_ponderee: -0.03119398628613559
    ts: '2026-08-03T05:23:02.656856+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_ble:
    valeur: -0.012722764770635275
    valeur_normalisee: -0.20199434999583224
    valeur_ponderee: -0.20199434999583224
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_ble:
    valeur: -0.034004906994913875
    valeur_normalisee: -0.4506462284010571
    valeur_ponderee: -0.4506462284010571
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_ble:
    valeur: -0.003419622825620028
    valeur_normalisee: -0.12661511449518897
    valeur_ponderee: -0.12661511449518897
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-03T05:23:02.656856+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.005444598855597338
    valeur_normalisee: 0.11933961895052231
    valeur_ponderee: 0.11933961895052231
    ts: '2026-08-03T05:23:02.656856+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.03559510567296975
    valeur_normalisee: 0.970562515679734
    valeur_ponderee: 0.970562515679734
    ts: '2026-08-03T05:23:02.656856+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: 'Frappes américaines sur l''Iran et escalade au Moyen-Orient
      (matérialité high, 30/07) dominent, malgré des PIB zone euro solides (LONG,
      matérialité medium). Le prix est quasi stable sur 20j, signalant que le risque
      géopolitique n''est pas pleinement pricé, mais la fraîcheur et la matérialité
      des news '
    nature: structurel
    event_id: 4849db7c8bba
    event_date: '2026-07-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: -132.40000000000015
      7j: -132.40000000000015
      1m: -132.40000000000015
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
    valeur: 59.036904355120946
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.00018445287150314904
    valeur_normalisee: -0.164361916313617
    valeur_ponderee: -0.164361916313617
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.008503311014502302
    valeur_normalisee: 0.14045467922088034
    valeur_ponderee: 0.14045467922088034
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.0060126139202809625
    valeur_normalisee: 0.17714254833039872
    valeur_ponderee: 0.17714254833039872
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-03T05:23:02.656856+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-31'
    valeur: 0.12311321174260538
    valeur_normalisee: 0.06155660587130269
    valeur_ponderee: 0.06155660587130269
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -15428.0
    valeur_normalisee: -0.5922330245608465
    valeur_ponderee: -0.5922330245608465
    ts: '2026-08-03T05:23:02.656856+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: structurel
    event_id: 46b9dc77b8a8
    event_date: '2026-08-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 92.46666666666691
      7j: 92.46666666666691
      1m: 92.46666666666691
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
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: Les news récentes (1er août) à matérialité élevée signalent
      une baisse de production au Ghana et des risques El Niño, dominantes malgré
      des nouvelles plus anciennes sur l'abondance de l'offre. Le prix a baissé de
      9% sur 20j, mais le rebond de 4,4% sur 5j suggère que le marché commence à intégrer
      ces
    nature: structurel
    event_id: 46b9dc77b8a8
    event_date: '2026-08-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 93.40000000000023
      7j: 93.40000000000023
      1m: 93.40000000000023
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: -0.09020990391317107
    valeur_normalisee: -0.6144324937361529
    valeur_ponderee: -0.6144324937361529
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.04796187577040589
    valeur_normalisee: 0.044476768918528635
    valeur_ponderee: 0.044476768918528635
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.0004555087171782546
    valeur_normalisee: -0.13323109717820714
    valeur_ponderee: -0.13323109717820714
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.39286916087297913
    valeur_normalisee: 0.19643458043648956
    valeur_ponderee: 0.19643458043648956
    ts: '2026-08-03T05:23:02.656856+00:00'
  usd_brl:
    valeur: 5.07593
    valeur_normalisee: -0.600731343128577
    valeur_ponderee: -0.600731343128577
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_coffee:
    valeur: 27914.0
    valeur_normalisee: -0.15738525585500848
    valeur_ponderee: -0.15738525585500848
    ts: '2026-08-03T05:23:02.656856+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: 'Signaux contradictoires : news récentes LONG (prix Vietnam
      élevé) contre SHORT (baisse arabica, tarif US 25% sur Brésil). Le prix a monté
      +1.57% sur 20j, mais les news SHORT dominent en matérialité et fraîcheur, sans
      signal net.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 205.73333333333372
      7j: 205.73333333333372
      1m: 205.73333333333372
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-03T05:23:02.656856+00:00'
  meteo_vietnam_robusta:
    valeur: 0.2881454700756573
    valeur_normalisee: 0.14407273503782864
    valeur_ponderee: 0.14407273503782864
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.015662854216529132
    valeur_normalisee: -0.24389869256494912
    valeur_ponderee: -0.24389869256494912
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.027052003457735285
    valeur_normalisee: -0.016812739388302342
    valeur_ponderee: -0.016812739388302342
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.0018350059086824633
    valeur_normalisee: -0.13679347398353342
    valeur_ponderee: -0.13679347398353342
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.3716941117783762
    valeur_normalisee: 0.1858470558891881
    valeur_ponderee: 0.1858470558891881
    ts: '2026-08-03T05:23:02.656856+00:00'
  meteo_inde_gujarat_coton:
    ts: '2026-08-03T05:23:02.656856+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-31'
    valeur: 0.6028819546829338
    valeur_normalisee: 0.3014409773414669
    valeur_ponderee: 0.3014409773414669
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 98453.0
    valeur_normalisee: 0.7538273781947771
    valeur_ponderee: 0.7538273781947771
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_coton:
    valeur: 0.05892255892255904
    valeur_normalisee: 0.4355313024558446
    valeur_ponderee: 0.4355313024558446
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_coton:
    valeur: -0.0025768087215064517
    valeur_normalisee: 0.040695856100165614
    valeur_ponderee: 0.040695856100165614
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_coton:
    valeur: 0.000596540067607787
    valeur_normalisee: 0.07224515215655188
    valeur_ponderee: 0.07224515215655188
    ts: '2026-08-03T05:23:02.656856+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  demande_chine_coton:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: structurel
    event_id: f37165710bf1
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '12.22'
    p2_shadow_contrib_exclu:
      24h: 39.733333333333285
      7j: 39.733333333333285
      1m: 39.733333333333285
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: 'Signaux contradictoires : PMI chinois en contraction (SHORT)
      contre prix proches des records et demande chinoise forte (LONG). Le prix a
      déjà monté de 3.17% sur 20j, suggérant que les nouvelles haussières sont largement
      intégrées.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 42.13333333333334
      7j: 42.13333333333334
      1m: 42.13333333333334
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_copper_nets:
    valeur: 68497.0
    valeur_normalisee: 0.881260518302941
    valeur_ponderee: 0.881260518302941
    ts: '2026-08-03T05:23:02.656856+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: ponctuel
    event_id: f75852b49d05
    event_date: '2026-07-31T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 39.69999999999998
      7j: 39.69999999999998
      1m: 39.69999999999998
  ratio_cuivre_or:
    valeur: 0.001606312909253916
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.031716683710136584
    valeur_normalisee: 0.487116189483903
    valeur_ponderee: 0.487116189483903
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.026154781135557137
    valeur_normalisee: 0.5385472084893951
    valeur_ponderee: 0.5385472084893951
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.005796314186155005
    valeur_normalisee: 0.1504654489484379
    valeur_ponderee: 0.1504654489484379
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5169262087000006
    valeur_normalisee: 0.0013877712377426319
    valeur_ponderee: 0.0013877712377426319
    ts: '2026-08-03T05:23:02.656856+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7099999999999995
    valeur_normalisee: 0.9156177786065571
    valeur_ponderee: 0.9156177786065571
    ts: '2026-08-03T05:23:02.656856+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  usd_jpy_proxy_risk:
    valeur: 156.50249
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_eur_nets:
    valeur: -100540.0
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.009885212457644288
    valeur_normalisee: 0.9403019671367074
    valeur_ponderee: 0.9403019671367074
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.01459346768589298
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.00031221813640458507
    valeur_normalisee: 0.06799050332784033
    valeur_ponderee: 0.06799050332784033
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.7644380868457178
    valeur_ponderee: 0.7644380868457178
    ts: '2026-08-03T05:23:02.656856+00:00'
  sox_trend_5j:
    valeur: 504.89001
    valeur_normalisee: -0.6307219697390104
    valeur_ponderee: -0.6307219697390104
    ts: '2026-08-03T05:23:02.656856+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17016235948432912
    valeur_normalisee: 0.7414770279795562
    valeur_ponderee: 0.7414770279795562
    ts: '2026-08-03T05:23:02.656856+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: Les frappes américaines sur l'Iran et le ralentissement économique
      dominent, malgré quelques signaux positifs sur l'IA et la consommation. Le prix
      a déjà baissé de 3.45% sur 20j, mais la fraîcheur des news géopolitiques et
      macro justifie une conviction medium.
    nature: ponctuel
    event_id: 322f6c6c8df1
    event_date: '2026-07-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 78.76666666666671
      7j: 78.76666666666671
      1m: 78.76666666666671
  flux_etf_qqq_5j:
    valeur: 0.005495242988329929
    valeur_normalisee: 0.04464190840818811
    valeur_ponderee: 0.04464190840818811
    ts: '2026-08-03T05:23:02.656856+00:00'
  spread_nasdaq_russell2000:
    valeur: 396.78998
    valeur_normalisee: -0.7430762607563121
    valeur_ponderee: -0.7430762607563121
    ts: '2026-08-03T05:23:02.656856+00:00'
  rsi_14j_ixic:
    valeur: 44.945705363278
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.03453549072510487
    valeur_normalisee: -0.48062753638035044
    valeur_ponderee: -0.48062753638035044
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.024611881324502094
    valeur_normalisee: -0.3975589262571061
    valeur_ponderee: -0.3975589262571061
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.01850508547136287
    valeur_normalisee: 0.37662427624145367
    valeur_ponderee: 0.37662427624145367
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.7644380868457178
    valeur_ponderee: 0.7644380868457178
    ts: '2026-08-03T05:23:02.656856+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_nets:
    valeur: 174131.0
    valeur_normalisee: -0.20851213210640585
    valeur_ponderee: -0.20851213210640585
    ts: '2026-08-03T05:23:02.656856+00:00'
  flux_etf_or_5j:
    valeur: -0.0009679483992457438
    valeur_normalisee: 0.17114843396871243
    valeur_ponderee: 0.17114843396871243
    ts: '2026-08-03T05:23:02.656856+00:00'
  tension_geopolitique:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: Les news du jour (2026-08-03) montrent une annulation des
      frappes sur l'Iran et une reprise des négociations, signalant une désescalade
      géopolitique qui pèse sur l'or (matérialité high, fraîcheur immédiate). Le prix
      de l'or est quasi stable sur 20j, cohérent avec un marché ayant déjà intégré
      ce biai
    nature: ponctuel
    event_id: f99e0a815349
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 207.09999999999974
      7j: 207.09999999999974
      1m: 207.09999999999974
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-03T05:23:02.656856+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_or:
    valeur: 0.001140291492902401
    valeur_normalisee: 0.6194767037227659
    valeur_ponderee: 0.6194767037227659
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_or:
    valeur: -0.004785163008871107
    valeur_normalisee: 0.13301935123107061
    valeur_ponderee: 0.13301935123107061
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_or:
    valeur: 0.003016408317622954
    valeur_normalisee: 0.1902030818832884
    valeur_ponderee: 0.1902030818832884
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-03T05:23:02.656856+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-31'
    valeur: 404508.0
    valeur_normalisee: -0.7758900959893141
    valeur_ponderee: -0.7758900959893141
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: Multiples news confirmées du 2-3 août indiquent l'annulation
      des frappes US sur l'Iran et l'espoir de négociations, réduisant la prime de
      risque sur le détroit d'Ormuz, malgré le rally passé de +14.93% sur 20j. Le
      repli récent de -2.89% sur 5j confirme que le marché intègre déjà ce choc baissier.
    nature: ponctuel
    event_id: f99e0a815349
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 185.9333333333334
      7j: 185.9333333333334
      1m: 185.9333333333334
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
    valeur: 32189.0
    valeur_normalisee: 0.13392206358519956
    valeur_ponderee: 0.13392206358519956
    ts: '2026-08-03T05:23:02.656856+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 173.23333333333383
      7j: 173.23333333333383
      1m: 173.23333333333383
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
    ts: '2026-08-03T05:23:02.656856+00:00'
  cushing_stocks:
    valeur: 18599.0
    valeur_normalisee: -0.8001382957591842
    valeur_ponderee: -0.8001382957591842
    ts: '2026-08-03T05:23:02.656856+00:00'
  spread_brent_wti:
    valeur: 3.3738400000000013
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.1492627076126558
    valeur_normalisee: 0.5697180898055282
    valeur_ponderee: 0.5697180898055282
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.12705319968152595
    valeur_normalisee: -0.5590564400353942
    valeur_ponderee: -0.5590564400353942
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.057957303675770344
    valeur_normalisee: -0.4162561498665405
    valeur_ponderee: -0.4162561498665405
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-03T05:23:02.656856+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.03000000000000025
    valeur_normalisee: -0.28729343371056515
    valeur_ponderee: -0.28729343371056515
    ts: '2026-08-03T05:23:02.656856+00:00'
  hy_credit_spread:
    valeur: 2.84
    valeur_normalisee: 0.8626862683392456
    valeur_ponderee: 0.8626862683392456
    ts: '2026-08-03T05:23:02.656856+00:00'
  breadth_sp_ma50:
    valeur: 0.2878197477386816
    valeur_normalisee: 0.49497319345175955
    valeur_ponderee: 0.49497319345175955
    ts: '2026-08-03T05:23:02.656856+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.010961849037958382
    valeur_normalisee: 0.24149262933810203
    valeur_ponderee: 0.24149262933810203
    ts: '2026-08-03T05:23:02.656856+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.91
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  rsi_14j_gspc:
    valeur: 52.857122433414034
    ts: '2026-08-03T05:23:02.656856+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.7644380868457178
    valeur_ponderee: 0.7644380868457178
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.0030210248789834804
    valeur_normalisee: -0.2691827901714216
    valeur_ponderee: -0.2691827901714216
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.0005083434998867098
    valeur_normalisee: -0.11651262647049124
    valeur_ponderee: -0.11651262647049124
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.008328211920311634
    valeur_normalisee: 0.2732901315310981
    valeur_ponderee: 0.2732901315310981
    ts: '2026-08-03T05:23:02.656856+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-03T05:23:02.656856+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-30'
    valeur: -0.1817535949708365
    valeur_normalisee: 0.09087679748541826
    valeur_ponderee: 0.09087679748541826
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 82.87777
    valeur_normalisee: -0.22127907303648525
    valeur_ponderee: -0.22127907303648525
    ts: '2026-08-03T05:23:02.656856+00:00'
  usd_brl_sucre:
    valeur: 5.07593
    valeur_normalisee: -0.600731343128577
    valeur_ponderee: -0.600731343128577
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_sugar:
    valeur: -81679.0
    valeur_normalisee: -0.5608615387476262
    valeur_ponderee: -0.5608615387476262
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_sucre:
    valeur: -0.015353121801433
    valeur_normalisee: -0.23605376626851002
    valeur_ponderee: -0.23605376626851002
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.010288065843621519
    valeur_normalisee: -0.1258487913000699
    valeur_ponderee: -0.1258487913000699
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.005224660397074032
    valeur_normalisee: 0.18666070992025743
    valeur_ponderee: 0.18666070992025743
    ts: '2026-08-03T05:23:02.656856+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 35.299999999999955
      7j: 35.299999999999955
      1m: 35.299999999999955
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
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 35.299999999999955
      7j: 35.299999999999955
      1m: 35.299999999999955
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-03T05:23:02.656856+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5600000000000005
    valeur_normalisee: 0.5193511451983042
    valeur_ponderee: 0.5193511451983042
    ts: '2026-08-03T05:23:02.656856+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.044254961410353566
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.00610042191970539
    valeur_normalisee: -0.30616725096934966
    valeur_ponderee: -0.30616725096934966
    ts: '2026-08-03T05:23:02.656856+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.03556726646529318
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_jpy_nets:
    valeur: -171320.0
    valeur_normalisee: -0.7719946476652498
    valeur_ponderee: -0.7719946476652498
    ts: '2026-08-03T05:23:02.656856+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.01
    valeur_normalisee: 0.9066789810057067
    valeur_ponderee: 0.9066789810057067
    ts: '2026-08-03T05:23:02.656856+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-03T05:23:02.656856+00:00'
    nature: ponctuel
    event_id: 66805837e1b3
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 10.333333333333345
      7j: 10.333333333333345
      1m: 10.333333333333345
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-03T05:23:02.656856+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-03T05:23:02.656856+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-03T05:23:02.656856+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-03T05:23:02.656856+00:00'
  gap_rv_iv:
    valeur: -2.5786629726794263
    ts: '2026-08-03T05:23:02.656856+00:00'
  cftc_cot_vix_nets:
    valeur: -63413.0
    valeur_normalisee: -0.21963090052659925
    valeur_ponderee: -0.21963090052659925
    ts: '2026-08-03T05:23:02.656856+00:00'
  tension_geopolitique_active:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-03T05:23:02.656856+00:00'
    synthese_rationale: Les news du jour (2026-08-03) montrent une annulation des
      frappes sur l'Iran et une reprise des négociations, signalant une désescalade
      géopolitique qui pèse sur la volatilité (SHORT VIX). Ce signal frais et de matérialité
      élevée domine les news LONG plus anciennes (30-31 juillet) et est cohérent av
    nature: ponctuel
    event_id: f99e0a815349
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 232.1999999999996
      7j: 232.1999999999996
      1m: 232.1999999999996
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-03T05:23:02.656856+00:00'
```
