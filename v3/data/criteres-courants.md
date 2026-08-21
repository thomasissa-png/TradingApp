# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-21T05:22:43.131748+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.26181629928418243
    valeur_ponderee: 0.26181629928418243
    ts: '2026-08-21T05:22:43.131748+00:00'
  mouvement_or_5j:
    valeur: 0.036099652238668956
    valeur_normalisee: 0.6258862695443698
    valeur_ponderee: 0.6258862695443698
    ts: '2026-08-21T05:22:43.131748+00:00'
  ratio_gold_silver:
    valeur: 65.79161957847288
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_silver:
    valeur: 21465.0
    valeur_normalisee: -0.2803992279605361
    valeur_ponderee: -0.2803992279605361
    ts: '2026-08-21T05:22:43.131748+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.06017881705639616
    valeur_normalisee: 0.5700235090028147
    valeur_ponderee: 0.5700235090028147
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_argent:
    valeur: 0.19544762473417676
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_argent:
    valeur: 0.06570568482636974
    valeur_normalisee: 0.5161963570527431
    valeur_ponderee: 0.5161963570527431
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_argent:
    valeur: 0.08801588924263215
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-21T05:22:43.131748+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.18981413577405845
    valeur_normalisee: 0.09490706788702923
    valeur_ponderee: 0.09490706788702923
    ts: '2026-08-21T05:22:43.131748+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (El
      Niño record, tensions mer Noire, attaques sur terminaux russes) cohérentes avec
      le prix +7.28%/20j. Aucune news SHORT significative ne contrebalance.
    nature: structurel
    event_id: 2b47e84d9080
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 142.33333333333323
      7j: 142.33333333333323
      1m: 142.33333333333323
  cftc_cot_wheat:
    valeur: -31179.0
    valeur_normalisee: 0.1801460824733161
    valeur_ponderee: 0.1801460824733161
    ts: '2026-08-21T05:22:43.131748+00:00'
  meteo_australie_dryland:
    valeur: -0.05301540921239028
    valeur_normalisee: -0.02650770460619514
    valeur_ponderee: -0.02650770460619514
    ts: '2026-08-21T05:22:43.131748+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_ble:
    valeur: 0.07279968955124883
    valeur_normalisee: 0.2307227183130611
    valeur_ponderee: 0.2307227183130611
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_ble:
    valeur: 0.018066843470688765
    valeur_normalisee: 0.040854474403361325
    valeur_ponderee: 0.040854474403361325
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_ble:
    valeur: 0.038874428383719906
    valeur_normalisee: 0.5721896364284477
    valeur_ponderee: 0.5721896364284477
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-21T05:22:43.131748+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.0031842350220064874
    valeur_normalisee: -0.14802665704918663
    valeur_ponderee: -0.14802665704918663
    ts: '2026-08-21T05:22:43.131748+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.010132995566814351
    valeur_normalisee: -0.3985493335868941
    valeur_ponderee: -0.3985493335868941
    ts: '2026-08-21T05:22:43.131748+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: 'Signaux mitigés : accords commerciaux US-Canada (LONG) contre
      délaissement de la France, minutes BCE hawkish et tensions Moyen-Orient (SHORT).
      Prix récent en hausse sur 20j mais en baisse sur 5j, sans signal dominant clair.'
    nature: verbal
    p2_shadow_contrib_exclu:
      24h: -398.3999999999992
      7j: -398.3999999999992
      1m: -398.3999999999992
  rsi_14j_fchi:
    valeur: 42.2547571767334
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.018556251696845605
    valeur_normalisee: -0.020827195285074658
    valeur_ponderee: -0.020827195285074658
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.03004617049344538
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.014745416074258832
    valeur_normalisee: -0.709621022868782
    valeur_ponderee: -0.709621022868782
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-21T05:22:43.131748+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.0747558222393906
    valeur_normalisee: 0.0373779111196953
    valeur_ponderee: 0.0373779111196953
    ts: '2026-08-21T05:22:43.131748+00:00'
  hf_positioning_flux_options:
    valeur: -15606.0
    valeur_normalisee: -0.5862223435839012
    valeur_ponderee: -0.5862223435839012
    ts: '2026-08-21T05:22:43.131748+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: structurel
    event_id: b99d2b50a2e6
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 129.79999999999998
      7j: 129.79999999999998
      1m: 129.79999999999998
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
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (El Niño record,
      baisse de récolte au Ghana) et fraîches (21/08), cohérentes avec le prix en
      hausse de +12.36% sur 20j. Les rares news SHORT sont faibles ou anciennes et
      ne contrebalancent pas le signal.
    nature: structurel
    event_id: b99d2b50a2e6
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 132.0333333333333
      7j: 132.0333333333333
      1m: 132.0333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.12363333535772325
    valeur_normalisee: -0.0645066087888621
    valeur_ponderee: -0.0645066087888621
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.04752062987575556
    valeur_normalisee: 0.021760923026122977
    valeur_ponderee: 0.021760923026122977
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.023707045037696606
    valeur_normalisee: 0.047575874888522565
    valeur_ponderee: 0.047575874888522565
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.41323086128874437
    valeur_normalisee: 0.20661543064437218
    valeur_ponderee: 0.20661543064437218
    ts: '2026-08-21T05:22:43.131748+00:00'
  usd_brl:
    valeur: 5.19534
    valeur_normalisee: 0.6070558160030777
    valeur_ponderee: 0.6070558160030777
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_coffee:
    valeur: 27282.0
    valeur_normalisee: -0.16470293830600344
    valeur_ponderee: -0.16470293830600344
    ts: '2026-08-21T05:22:43.131748+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Signal dominant LONG via El Niño (matérialité high le 21/08,
      confirmé par multiples news medium) malgré quelques news SHORT dispersées et
      un prix -0.89%/20j. La fraîcheur et la matérialité du risque El Niño sur l'offre
      de café surclassent les signaux baissiers anciens.
    nature: structurel
    event_id: f2fd02e28b8a
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 117.90000000000018
      7j: 117.90000000000018
      1m: 117.90000000000018
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
    ts: '2026-08-21T05:22:43.131748+00:00'
  meteo_vietnam_robusta:
    ts: '2026-08-21T05:22:43.131748+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-20'
    valeur: 0.49311581609125843
    valeur_normalisee: 0.24655790804562921
    valeur_ponderee: 0.24655790804562921
    reporte_cause: source réseau indisponible
  momentum_prix_20j_cafe:
    valeur: -0.008888745215861138
    valeur_normalisee: -0.4398019925567813
    valeur_ponderee: -0.4398019925567813
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.05491574903719876
    valeur_normalisee: 0.25719836784320405
    valeur_ponderee: 0.25719836784320405
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.007317775591330289
    valeur_normalisee: -0.22143139826138336
    valeur_ponderee: -0.22143139826138336
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
coton:
  meteo_texas_cotton_precip:
    ts: '2026-08-21T05:22:43.131748+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-20'
    valeur: 0.03373235261639925
    valeur_normalisee: 0.016866176308199626
    valeur_ponderee: 0.016866176308199626
    reporte_cause: source réseau indisponible
  meteo_inde_gujarat_coton:
    valeur: 0.8087861873066279
    valeur_normalisee: 0.40439309365331394
    valeur_ponderee: 0.40439309365331394
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_cotton:
    valeur: 110304.0
    valeur_normalisee: 0.8731439466661239
    valeur_ponderee: 0.8731439466661239
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_coton:
    valeur: 0.08591744025281467
    valeur_normalisee: 0.6588299152056744
    valeur_ponderee: 0.6588299152056744
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_coton:
    valeur: 0.05730769230769228
    valeur_normalisee: 0.721526907717397
    valeur_ponderee: 0.721526907717397
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_coton:
    valeur: 0.0379460071738722
    valeur_normalisee: 0.7169524572571581
    valeur_ponderee: 0.7169524572571581
    ts: '2026-08-21T05:22:43.131748+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: structurel
    event_id: 2f90239ca8a8
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 78.56666666666676
      7j: 78.56666666666676
      1m: 78.56666666666676
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-21T05:22:43.131748+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Livraison LME de 20 000 t et rebond de l'offre chilienne dominent,
      malgré des signaux longs sur les VE et les stocks. Le prix a monté de 1.55%
      sur 20j, mais la fraîcheur des news short (20/08) et la matérialité élevée de
      la livraison LME justifient un biais short modéré.
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 48.66666666666668
      7j: 48.66666666666668
      1m: 48.66666666666668
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_copper_nets:
    valeur: 80503.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 59.69999999999999
      7j: 59.69999999999999
      1m: 59.69999999999999
  ratio_cuivre_or:
    valeur: 0.001441646913102672
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.015513054179155272
    valeur_normalisee: 0.05933284963142244
    valeur_ponderee: 0.05933284963142244
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.008767699195573853
    valeur_normalisee: -0.2592722101304559
    valeur_ponderee: -0.2592722101304559
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.013742591641836333
    valeur_normalisee: 0.31820650539083867
    valeur_ponderee: 0.31820650539083867
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4092476155000004
    valeur_normalisee: -0.8949151410769038
    valeur_ponderee: -0.8949151410769038
    ts: '2026-08-21T05:22:43.131748+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6800000000000002
    valeur_normalisee: 0.4358783586359286
    valeur_ponderee: 0.4358783586359286
    ts: '2026-08-21T05:22:43.131748+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.03206
    valeur_normalisee: -0.46819409869365225
    valeur_ponderee: -0.46819409869365225
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_eur_nets:
    valeur: -79915.0
    valeur_normalisee: -0.9298361009982374
    valeur_ponderee: -0.9298361009982374
    ts: '2026-08-21T05:22:43.131748+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.013760274685256535
    valeur_normalisee: 0.6059948716200194
    valeur_ponderee: 0.6059948716200194
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.01049219999135742
    valeur_normalisee: 0.6923663837062342
    valeur_ponderee: 0.6923663837062342
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.009933574618421037
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.26181629928418243
    valeur_ponderee: 0.26181629928418243
    ts: '2026-08-21T05:22:43.131748+00:00'
  sox_trend_5j:
    valeur: 522.34998
    valeur_normalisee: -0.5106186006436129
    valeur_ponderee: -0.5106186006436129
    ts: '2026-08-21T05:22:43.131748+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17191566218777746
    valeur_normalisee: 0.8351473783902997
    valeur_ponderee: 0.8351473783902997
    ts: '2026-08-21T05:22:43.131748+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: 'Signaux contradictoires : rachats du Trésor et assouplissement
      chinois sur Nvidia (LONG) contre vente massive semi-conducteurs et hausse des
      rendements (SHORT). Prix récent +2.74% sur 20j mais -2.89% sur 5j, pas de biais
      net.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 173.20000000000007
      7j: 173.20000000000007
      1m: 173.20000000000007
  flux_etf_qqq_5j:
    valeur: -0.0288770429028109
    valeur_normalisee: -0.4797790848251988
    valeur_ponderee: -0.4797790848251988
    ts: '2026-08-21T05:22:43.131748+00:00'
  spread_nasdaq_russell2000:
    valeur: 413.25998
    valeur_normalisee: -0.22227674034712971
    valeur_ponderee: -0.22227674034712971
    ts: '2026-08-21T05:22:43.131748+00:00'
  rsi_14j_ixic:
    valeur: 49.710423989250785
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.027414835325312525
    valeur_normalisee: 0.23755618678273357
    valeur_ponderee: 0.23755618678273357
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.010467005213069758
    valeur_normalisee: -0.18506001088330254
    valeur_ponderee: -0.18506001088330254
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.025949840382533895
    valeur_normalisee: -0.5084351882162379
    valeur_ponderee: -0.5084351882162379
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.26181629928418243
    valeur_ponderee: 0.26181629928418243
    ts: '2026-08-21T05:22:43.131748+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_nets:
    valeur: 214856.0
    valeur_normalisee: 0.14816439944873105
    valeur_ponderee: 0.14816439944873105
    ts: '2026-08-21T05:22:43.131748+00:00'
  flux_etf_or_5j:
    valeur: 0.040856277342497416
    valeur_normalisee: 0.6606995057159517
    valeur_ponderee: 0.6606995057159517
    ts: '2026-08-21T05:22:43.131748+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (or en forte hausse,
      dollar effondré, guerre économique US-Iran, blocage d'Ormuz) et cohérentes avec
      le prix (+12% sur 20j). Les quelques news SHORT (rendements, réserves russes)
      sont minoritaires et de matérialité moyenne.
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 451.7999999999982
      7j: 451.7999999999982
      1m: 451.7999999999982
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-21T05:22:43.131748+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_or:
    valeur: 0.12139328302947572
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_or:
    valeur: 0.035859360534985285
    valeur_normalisee: 0.4697154128211724
    valeur_ponderee: 0.4697154128211724
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_or:
    valeur: 0.04562680555036813
    valeur_normalisee: 0.9859823234850903
    valeur_ponderee: 0.9859823234850903
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
petrole:
  eia_crude_surprise:
    valeur: 428815.0
    valeur_normalisee: -0.007281118678166014
    valeur_ponderee: -0.007281118678166014
    ts: '2026-08-21T05:22:43.131748+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (guerre économique
      US-Iran, sanctions, blocage d'Ormuz, déficit d'offre) malgré quelques news SHORT
      faibles. Le prix a rebondi de +5% sur 5j, cohérent avec le signal LONG.
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 426.3666666666653
      7j: 426.3666666666653
      1m: 426.3666666666653
    sign_conflict: true
    sign_conflict_details:
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
  cftc_cot_crude_nets:
    valeur: 23853.0
    valeur_normalisee: -0.045557257567997375
    valeur_ponderee: -0.045557257567997375
    ts: '2026-08-21T05:22:43.131748+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 394.3999999999984
      7j: 394.3999999999984
      1m: 394.3999999999984
    sign_conflict: true
    sign_conflict_details:
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
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  cushing_stocks:
    valeur: 21252.0
    valeur_normalisee: -0.36351247895781225
    valeur_ponderee: -0.36351247895781225
    ts: '2026-08-21T05:22:43.131748+00:00'
  spread_brent_wti:
    valeur: 5.445160000000001
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.015695327349306676
    valeur_normalisee: 0.08352796448902282
    valeur_ponderee: 0.08352796448902282
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.05157197404153813
    valeur_normalisee: 0.2875067984325248
    valeur_ponderee: 0.2875067984325248
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.017728666962680606
    valeur_normalisee: 0.1362020643158136
    valeur_ponderee: 0.1362020643158136
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-21T05:22:43.131748+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.02999999999999936
    valeur_normalisee: -0.2366112777681204
    valeur_ponderee: -0.2366112777681204
    ts: '2026-08-21T05:22:43.131748+00:00'
  hy_credit_spread:
    valeur: 2.73
    valeur_normalisee: -0.0355921826737546
    valeur_ponderee: -0.0355921826737546
    ts: '2026-08-21T05:22:43.131748+00:00'
  breadth_sp_ma50:
    valeur: 0.28885392837277546
    valeur_normalisee: 0.495505376200482
    valeur_ponderee: 0.495505376200482
    ts: '2026-08-21T05:22:43.131748+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.019643158327762644
    valeur_normalisee: -0.6173564059535593
    valeur_ponderee: -0.6173564059535593
    ts: '2026-08-21T05:22:43.131748+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.79
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  rsi_14j_gspc:
    valeur: 52.53964626204836
    ts: '2026-08-21T05:22:43.131748+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.26181629928418243
    valeur_ponderee: 0.26181629928418243
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.033081349170681174
    valeur_normalisee: 0.45212632382725565
    valeur_ponderee: 0.45212632382725565
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.010330175456810586
    valeur_normalisee: -0.3664595088200125
    valeur_ponderee: -0.3664595088200125
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.013032730998556508
    valeur_normalisee: -0.5047308219253392
    valeur_ponderee: -0.5047308219253392
    ts: '2026-08-21T05:22:43.131748+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-21T05:22:43.131748+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.27956898399998503
    valeur_normalisee: 0.13978449199999252
    valeur_ponderee: 0.13978449199999252
    ts: '2026-08-21T05:22:43.131748+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 91.72876
    valeur_normalisee: 0.5172578556436304
    valeur_ponderee: 0.5172578556436304
    ts: '2026-08-21T05:22:43.131748+00:00'
  usd_brl_sucre:
    valeur: 5.19534
    valeur_normalisee: 0.6070558160030777
    valeur_ponderee: 0.6070558160030777
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_sugar:
    valeur: 80425.0
    valeur_normalisee: 0.08231776585326993
    valeur_ponderee: 0.08231776585326993
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.15838509316770177
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.0332409972299168
    valeur_normalisee: 0.23549840475245573
    valeur_ponderee: 0.23549840475245573
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.023787740164684434
    valeur_normalisee: 0.32580557806008265
    valeur_ponderee: 0.32580557806008265
    ts: '2026-08-21T05:22:43.131748+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: structurel
    event_id: 153e0c030819
    event_date: '2026-08-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 60.9666666666667
      7j: 60.9666666666667
      1m: 60.9666666666667
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
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: structurel
    event_id: 153e0c030819
    event_date: '2026-08-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 60.9666666666667
      7j: 60.9666666666667
      1m: 60.9666666666667
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5200000000000005
    valeur_normalisee: 0.14508817962022613
    valeur_ponderee: 0.14508817962022613
    ts: '2026-08-21T05:22:43.131748+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.0018968043052812744
    valeur_normalisee: -0.019572841374221925
    valeur_ponderee: -0.019572841374221925
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.0037957255753493513
    valeur_normalisee: -0.17026873661413885
    valeur_ponderee: -0.17026873661413885
    ts: '2026-08-21T05:22:43.131748+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.00887088245114831
    valeur_normalisee: 0.3863874943794946
    valeur_ponderee: 0.3863874943794946
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_jpy_nets:
    valeur: -40040.0
    valeur_normalisee: 0.031499248803131374
    valeur_ponderee: 0.031499248803131374
    ts: '2026-08-21T05:22:43.131748+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.9800000000000004
    valeur_normalisee: 0.43612583189593895
    valeur_ponderee: 0.43612583189593895
    ts: '2026-08-21T05:22:43.131748+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-21T05:22:43.131748+00:00'
    nature: structurel
    event_id: b93cae4ee23f
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 9.033333333333369
      7j: 9.033333333333369
      1m: 9.033333333333369
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-21T05:22:43.131748+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-21T05:22:43.131748+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-21T05:22:43.131748+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-21T05:22:43.131748+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-21T05:22:43.131748+00:00'
  gap_rv_iv:
    valeur: -2.125510971113542
    ts: '2026-08-21T05:22:43.131748+00:00'
  cftc_cot_vix_nets:
    valeur: -74934.0
    valeur_normalisee: -0.44221335910303994
    valeur_ponderee: -0.44221335910303994
    ts: '2026-08-21T05:22:43.131748+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-21T05:22:43.131748+00:00'
    synthese_rationale: Dominance de news LONG à matérialité high (sanctions US, frappes
      russes, tensions Ormuz) malgré le repli récent du VIX, mais le marché a déjà
      pricé une partie du risque, d'où une conviction medium.
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 460.6666666666642
      7j: 460.6666666666642
      1m: 460.6666666666642
  gate_evenement_macro_imminent:
    valeur: false
    ts: '2026-08-21T05:22:43.131748+00:00'
```
