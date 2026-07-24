# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-24T05:23:43.151687+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.8726918175816001
    valeur_ponderee: 0.8726918175816001
    ts: '2026-07-24T05:23:43.151687+00:00'
  mouvement_or_5j:
    valeur: 0.00434580730920997
    valeur_normalisee: 0.28084055044524403
    valeur_ponderee: 0.28084055044524403
    ts: '2026-07-24T05:23:43.151687+00:00'
  ratio_gold_silver:
    valeur: 70.04956060439304
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_silver:
    valeur: 22604.0
    valeur_normalisee: -0.24337735975094785
    valeur_ponderee: -0.24337735975094785
    ts: '2026-07-24T05:23:43.151687+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.03314151617384398
    valeur_normalisee: 0.377995802437052
    valeur_ponderee: 0.377995802437052
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_argent:
    valeur: -0.07842491622304093
    valeur_normalisee: 0.16606365985659635
    valeur_ponderee: 0.16606365985659635
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_argent:
    valeur: 0.02769557941547629
    valeur_normalisee: 0.5081176610970248
    valeur_ponderee: 0.5081176610970248
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_argent:
    valeur: -0.022127245396684758
    valeur_normalisee: -0.11528516151848466
    valeur_ponderee: -0.11528516151848466
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-24T05:23:43.151687+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.3421316960053057
    valeur_normalisee: 0.17106584800265284
    valeur_ponderee: 0.17106584800265284
    ts: '2026-07-24T05:23:43.151687+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Signal LONG dominant avec news high matérialité récentes (Black
      Sea disruptions, USDA baisse production) et prix en forte hausse (+19% sur 20j)
      confirmant le momentum. Pas de contradiction significative.
    nature: structurel
    event_id: fd630a45bbcc
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 50.46666666666664
      7j: 50.46666666666664
      1m: 50.46666666666664
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -25958.0
    valeur_normalisee: 0.24746974397717958
    valeur_ponderee: 0.24746974397717958
    ts: '2026-07-24T05:23:43.151687+00:00'
  meteo_australie_dryland:
    valeur: 0.044569537127407584
    valeur_normalisee: 0.022284768563703792
    valeur_ponderee: 0.022284768563703792
    ts: '2026-07-24T05:23:43.151687+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_ble:
    valeur: 0.19132591010161693
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_ble:
    valeur: 0.02751128386400148
    valeur_normalisee: 0.20667157873118747
    valeur_ponderee: 0.20667157873118747
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_ble:
    valeur: 0.036825099974235664
    valeur_normalisee: 0.5896526526823678
    valeur_ponderee: 0.5896526526823678
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-24T05:23:43.151687+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-07-24T05:23:43.151687+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.0073017158502625135
    valeur_normalisee: 0.268217999617705
    valeur_ponderee: 0.268217999617705
    ts: '2026-07-24T05:23:43.151687+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.010845506861443144
    valeur_normalisee: -0.2504724493954814
    valeur_ponderee: -0.2504724493954814
    ts: '2026-07-24T05:23:43.151687+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée et très récentes
      : droits de douane Trump, escalade militaire US-Iran, pétrole à 100$, STMicroelectronics
      en baisse. Le contexte de prix (-1.57% sur 20j) est cohérent avec le signal
      SHORT, renforçant la conviction.'
    nature: structurel
    event_id: a7f7006a15e3
    event_date: '2026-07-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -123.73333333333345
      7j: -123.73333333333345
      1m: -123.73333333333345
    sign_conflict: true
    sign_conflict_details:
    - event_id: 351a6b7e7bc6
      asset: CAC40
      rule_name: cpi_actions
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: inflation
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse temporaire de l'inflation en juin, hausse attendue par la suite
  rsi_14j_fchi:
    valeur: 46.84272671154058
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_cac40:
    valeur: -0.015717105096062833
    valeur_normalisee: -0.4991862862617615
    valeur_ponderee: -0.4991862862617615
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.00809859973089666
    valeur_normalisee: -0.35760307588991586
    valeur_ponderee: -0.35760307588991586
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.004918460821085047
    valeur_normalisee: -0.25308748309368634
    valeur_ponderee: -0.25308748309368634
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-07-24T05:23:43.151687+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-22'
    valeur: 0.3822598866442453
    valeur_normalisee: 0.19112994332212266
    valeur_ponderee: 0.19112994332212266
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -18516.0
    valeur_normalisee: -0.6527264467064956
    valeur_ponderee: -0.6527264467064956
    ts: '2026-07-24T05:23:43.151687+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 84.76666666666685
      7j: 84.76666666666685
      1m: 84.76666666666685
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
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Les news récentes (24-21 juillet) montrent un resserrement
      de l'offre lié à El Niño et une demande nord-américaine forte, dominant les
      signaux baissiers plus anciens (demande européenne atone, dollar fort). Le prix
      a monté de +5.64% sur 20j, mais la fraîcheur des news LONG (24 juillet) et la
      matéria
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 84.76666666666685
      7j: 84.76666666666685
      1m: 84.76666666666685
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.056434616981858365
    valeur_normalisee: -0.2127487741638003
    valeur_ponderee: -0.2127487741638003
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.05474034020944196
    valeur_normalisee: -0.5166463316192775
    valeur_ponderee: -0.5166463316192775
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.054015180668609
    valeur_normalisee: -0.5715438298599484
    valeur_ponderee: -0.5715438298599484
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-24T05:23:43.151687+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.40165849517112373
    valeur_normalisee: 0.20082924758556187
    valeur_ponderee: 0.20082924758556187
    ts: '2026-07-24T05:23:43.151687+00:00'
  usd_brl:
    valeur: 5.09384
    valeur_normalisee: -0.26493180021375196
    valeur_ponderee: -0.26493180021375196
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_coffee:
    valeur: 26499.0
    valeur_normalisee: -0.18862009873184962
    valeur_ponderee: -0.18862009873184962
    ts: '2026-07-24T05:23:43.151687+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Tarif US sur Brésil (22/07, high) et El Niño (17/07, medium)
      dominent, soutenus par USDA haussier (15/07). Malgré le recul récent du prix
      (-3.41% sur 5j), la fraîcheur et matérialité des news LONG l'emportent.
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '18.22'
    p2_shadow_contrib_exclu:
      24h: 87.4666666666668
      7j: 87.4666666666668
      1m: 87.4666666666668
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
    ts: '2026-07-24T05:23:43.151687+00:00'
  meteo_vietnam_robusta:
    valeur: 0.2401677520941673
    valeur_normalisee: 0.12008387604708365
    valeur_ponderee: 0.12008387604708365
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.02402378874030986
    valeur_normalisee: -0.1668210445215034
    valeur_ponderee: -0.1668210445215034
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.036496906169424914
    valeur_normalisee: -0.4299715577828161
    valeur_ponderee: -0.4299715577828161
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.04198729054626571
    valeur_normalisee: -0.5668813371601695
    valeur_ponderee: -0.5668813371601695
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-24T05:23:43.151687+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.44707840241174296
    valeur_normalisee: 0.22353920120587148
    valeur_ponderee: 0.22353920120587148
    ts: '2026-07-24T05:23:43.151687+00:00'
  meteo_inde_gujarat_coton:
    ts: '2026-07-24T05:23:43.151687+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-23'
    valeur: 0.05646156344348821
    valeur_normalisee: 0.028230781721744105
    valeur_ponderee: 0.028230781721744105
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 101259.0
    valeur_normalisee: 0.7785042547190695
    valeur_ponderee: 0.7785042547190695
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_coton:
    valeur: 0.06746784735399514
    valeur_normalisee: 0.38678462830022
    valeur_ponderee: 0.38678462830022
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_coton:
    valeur: 0.001384493670886
    valeur_normalisee: 0.0508647114253343
    valeur_ponderee: 0.0508647114253343
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_coton:
    valeur: 0.03495502861815192
    valeur_normalisee: 0.5550347943962732
    valeur_ponderee: 0.5550347943962732
    ts: '2026-07-24T05:23:43.151687+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  demande_chine_coton:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    event_id: f37165710bf1
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 30.666666666666618
      7j: 30.666666666666618
      1m: 30.666666666666618
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-24T05:23:43.151687+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Deux news high matérialité du 23 juillet (record NY, tensions
      Chine/tarifs) dominent le flux, renforcées par des signaux longs récurrents
      (demande Chine, électrification UE). Les news short (PIB Chine, ventes auto)
      sont plus anciennes et moins fraîches, le marché a déjà intégré le biais haussier
      (+1
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 8.866666666666665
      7j: 8.866666666666665
      1m: 8.866666666666665
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_copper_nets:
    valeur: 65629.0
    valeur_normalisee: 0.8500644003681505
    valeur_ponderee: 0.8500644003681505
    ts: '2026-07-24T05:23:43.151687+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 26.599999999999998
      7j: 26.599999999999998
      1m: 26.599999999999998
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.001562133847532094
    valeur_normalisee: 0.6785628685848232
    valeur_ponderee: 0.6785628685848232
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.019643143615978298
    valeur_normalisee: 0.323449811760811
    valeur_ponderee: 0.323449811760811
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.01051412750567704
    valeur_normalisee: 0.19828903664687217
    valeur_ponderee: 0.19828903664687217
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.029915037224210184
    valeur_normalisee: -0.7050883829659416
    valeur_ponderee: -0.7050883829659416
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5482889447999995
    valeur_normalisee: 0.23896088175190278
    valeur_ponderee: 0.23896088175190278
    ts: '2026-07-24T05:23:43.151687+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6999999999999997
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  usd_jpy_proxy_risk:
    valeur: 163.81411
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_eur_nets:
    valeur: -34257.0
    valeur_normalisee: -0.6453198959279014
    valeur_ponderee: -0.6453198959279014
    ts: '2026-07-24T05:23:43.151687+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.004948287770035753
    valeur_normalisee: 0.19283080915483675
    valeur_ponderee: 0.19283080915483675
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.004896089248712654
    valeur_normalisee: -0.23980780957308317
    valeur_ponderee: -0.23980780957308317
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.00142131445266247
    valeur_normalisee: -0.054747043561330595
    valeur_ponderee: -0.054747043561330595
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.8726918175816001
    valeur_ponderee: 0.8726918175816001
    ts: '2026-07-24T05:23:43.151687+00:00'
  sox_trend_5j:
    valeur: 551.23999
    valeur_normalisee: -0.03195493960014616
    valeur_ponderee: -0.03195493960014616
    ts: '2026-07-24T05:23:43.151687+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1678854220508289
    valeur_normalisee: 0.6626729261930354
    valeur_ponderee: 0.6626729261930354
    ts: '2026-07-24T05:23:43.151687+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Multiples news SHORT à matérialité élevée ce jour (tarifs
      Trump, frappes Iran, pétrole >100$) dominent, malgré quelques signaux LONG isolés.
      Le prix a déjà baissé de 2.63% sur 20j, mais la concentration et la fraîcheur
      des news SHORT justifient une conviction haute.
    nature: ponctuel
    event_id: 091bed95f9ba
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 73.36666666666672
      7j: 73.36666666666672
      1m: 73.36666666666672
  flux_etf_qqq_5j:
    valeur: -0.019803354392724737
    valeur_normalisee: -0.4639997995898779
    valeur_ponderee: -0.4639997995898779
    ts: '2026-07-24T05:23:43.151687+00:00'
  spread_nasdaq_russell2000:
    valeur: 399.870024
    valeur_normalisee: -0.7072446463634041
    valeur_ponderee: -0.7072446463634041
    ts: '2026-07-24T05:23:43.151687+00:00'
  rsi_14j_ixic:
    valeur: 41.59346303148037
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.0262587318116575
    valeur_normalisee: -0.5564648999269745
    valeur_ponderee: -0.5564648999269745
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.03853045061067972
    valeur_normalisee: -0.7361650103387785
    valeur_ponderee: -0.7361650103387785
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.005890265223946978
    valeur_normalisee: -0.20298875560558588
    valeur_ponderee: -0.20298875560558588
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.8726918175816001
    valeur_ponderee: 0.8726918175816001
    ts: '2026-07-24T05:23:43.151687+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_nets:
    valeur: 175931.0
    valeur_normalisee: -0.19336088557858558
    valeur_ponderee: -0.19336088557858558
    ts: '2026-07-24T05:23:43.151687+00:00'
  flux_etf_or_5j:
    valeur: 0.017974573048404663
    valeur_normalisee: 0.5555470600463758
    valeur_ponderee: 0.5555470600463758
    ts: '2026-07-24T05:23:43.151687+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Escalade majeure US-Iran avec frappes continues, menaces Houthies
      sur les détroits d'Ormuz et Bab Al-Mandab, et Brent >100$/bbl dominent largement
      les rares signaux short (rendements US, dollar fort). La fraîcheur et la matérialité
      élevée des news LONG surclassent le contexte de prix baissier (-3.55
    nature: structurel
    event_id: cf4cdf457f5c
    event_date: '2026-07-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 171.7666666666668
      7j: 171.7666666666668
      1m: 171.7666666666668
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-24T05:23:43.151687+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_or:
    valeur: -0.03518755980728072
    valeur_normalisee: 0.09007028401852672
    valeur_ponderee: 0.09007028401852672
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_or:
    valeur: 0.0027531358017827134
    valeur_normalisee: 0.29856327313953046
    valeur_ponderee: 0.29856327313953046
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_or:
    valeur: -0.012210572220519023
    valeur_normalisee: -0.17183996394879952
    valeur_ponderee: -0.17183996394879952
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
petrole:
  eia_crude_surprise:
    valeur: 411675.0
    valeur_normalisee: -0.5782047119748305
    valeur_ponderee: -0.5782047119748305
    ts: '2026-07-24T05:23:43.151687+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Escalade US-Iran avec frappes continues, menaces Houthies
      sur les détroits d'Ormuz et Bab Al-Mandab, et Brent >100$ dominent largement
      malgré quelques signaux SHORT faibles. Le prix a déjà fortement monté, mais
      la fraîcheur et la matérialité élevée des news LONG justifient le maintien de
      la directio
    nature: structurel
    event_id: 18f2de181768
    event_date: '2026-07-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 148.7666666666668
      7j: 148.7666666666668
      1m: 148.7666666666668
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 51028.0
    valeur_normalisee: 0.5358446521183773
    valeur_ponderee: 0.5358446521183773
    ts: '2026-07-24T05:23:43.151687+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    event_id: 18f2de181768
    event_date: '2026-07-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 161.33333333333343
      7j: 161.33333333333343
      1m: 161.33333333333343
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  cushing_stocks:
    valeur: 19370.0
    valeur_normalisee: -0.7071724108334729
    valeur_ponderee: -0.7071724108334729
    ts: '2026-07-24T05:23:43.151687+00:00'
  spread_brent_wti:
    valeur: 2.657110000000003
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.28345377899042057
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.11415234850971823
    valeur_normalisee: 0.6553622084151148
    valeur_ponderee: 0.6553622084151148
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.03269299717179619
    valeur_normalisee: 0.3361266088862246
    valeur_ponderee: 0.3361266088862246
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-24T05:23:43.151687+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.1200000000000001
    valeur_normalisee: 0.5350060504785339
    valeur_ponderee: 0.5350060504785339
    ts: '2026-07-24T05:23:43.151687+00:00'
  hy_credit_spread:
    valeur: 2.68
    valeur_normalisee: -0.6102518618865367
    valeur_ponderee: -0.6102518618865367
    ts: '2026-07-24T05:23:43.151687+00:00'
  breadth_sp_ma50:
    valeur: 0.2870844548360082
    valeur_normalisee: 0.624203317936282
    valeur_ponderee: 0.624203317936282
    ts: '2026-07-24T05:23:43.151687+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.016703938220798964
    valeur_normalisee: -0.6625215551909194
    valeur_ponderee: -0.6625215551909194
    ts: '2026-07-24T05:23:43.151687+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.42
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  rsi_14j_gspc:
    valeur: 44.3113225146838
    ts: '2026-07-24T05:23:43.151687+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.8726918175816001
    valeur_ponderee: 0.8726918175816001
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.006737221192750109
    valeur_normalisee: -0.30105196566149595
    valeur_ponderee: -0.30105196566149595
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.018155739511439006
    valeur_normalisee: -0.6859372003008499
    valeur_ponderee: -0.6859372003008499
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.005268952361220713
    valeur_normalisee: -0.3020742558054642
    valeur_ponderee: -0.3020742558054642
    ts: '2026-07-24T05:23:43.151687+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-07-24T05:23:43.151687+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-22'
    valeur: -0.2138384775982998
    valeur_normalisee: 0.1069192387991499
    valeur_ponderee: 0.1069192387991499
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 94.41815
    valeur_normalisee: 0.20164926069544453
    valeur_ponderee: 0.20164926069544453
    ts: '2026-07-24T05:23:43.151687+00:00'
  usd_brl_sucre:
    valeur: 5.09384
    valeur_normalisee: -0.26493180021375196
    valeur_ponderee: -0.26493180021375196
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_sugar:
    valeur: -45822.0
    valeur_normalisee: -0.4281576108153665
    valeur_ponderee: -0.4281576108153665
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.038709677419354716
    valeur_normalisee: 0.28766039125076465
    valeur_ponderee: 0.28766039125076465
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.018292682926829285
    valeur_normalisee: -0.32442146373965297
    valeur_ponderee: -0.32442146373965297
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.011258955987717423
    valeur_normalisee: -0.26061894671404356
    valeur_ponderee: -0.26061894671404356
    ts: '2026-07-24T05:23:43.151687+00:00'
  prod_inde_thai_sucre:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    event_id: 9b9416f709bd
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 24.29999999999998
      7j: 24.29999999999998
      1m: 24.29999999999998
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  exports_bresil_sucre:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    event_id: 9b9416f709bd
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 24.29999999999998
      7j: 24.29999999999998
      1m: 24.29999999999998
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-24T05:23:43.151687+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.6399999999999997
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  dxy_trend_20j:
    valeur: 120.5315
    valeur_normalisee: 0.48268877937019605
    valeur_ponderee: 0.48268877937019605
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.00858884403414839
    valeur_normalisee: 0.878153480830837
    valeur_ponderee: 0.878153480830837
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.0036574035155483298
    valeur_normalisee: 0.34398071427441473
    valeur_ponderee: 0.34398071427441473
    ts: '2026-07-24T05:23:43.151687+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.01502432505048934
    valeur_normalisee: 0.6866523809303688
    valeur_ponderee: 0.6866523809303688
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_jpy_nets:
    valeur: -127263.0
    valeur_normalisee: -0.5107367349427174
    valeur_ponderee: -0.5107367349427174
    ts: '2026-07-24T05:23:43.151687+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-24T05:23:43.151687+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-24T05:23:43.151687+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 3.633333333333334
      7j: 3.633333333333334
      1m: 3.633333333333334
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-24T05:23:43.151687+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-24T05:23:43.151687+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-24T05:23:43.151687+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-24T05:23:43.151687+00:00'
  gap_rv_iv:
    valeur: -3.578915531402057
    ts: '2026-07-24T05:23:43.151687+00:00'
  cftc_cot_vix_nets:
    valeur: -65783.0
    valeur_normalisee: -0.26642687690687433
    valeur_ponderee: -0.26642687690687433
    ts: '2026-07-24T05:23:43.151687+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-24T05:23:43.151687+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîcheur immédiate
      (13e nuit de frappes, Brent >100$, menaces sur Ormuz/Bab Al-Mandab). Les rares
      signaux SHORT (résolution du Congrès) sont noyés par l'escalade continue.
    nature: structurel
    event_id: 18f2de181768
    event_date: '2026-07-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 196.7999999999999
      7j: 196.7999999999999
      1m: 196.7999999999999
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-24T05:23:43.151687+00:00'
```
