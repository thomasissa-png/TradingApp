# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-17T05:22:57.159843+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.49614001036431454
    valeur_ponderee: 0.49614001036431454
    ts: '2026-08-17T05:22:57.159843+00:00'
  mouvement_or_5j:
    valeur: -0.002829828878777918
    valeur_normalisee: -0.12285344005763361
    valeur_ponderee: -0.12285344005763361
    ts: '2026-08-17T05:22:57.159843+00:00'
  ratio_gold_silver:
    valeur: 66.93633414609194
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_silver:
    valeur: 21465.0
    valeur_normalisee: -0.2803992279605361
    valeur_ponderee: -0.2803992279605361
    ts: '2026-08-17T05:22:57.159843+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.017043478260869493
    valeur_normalisee: 0.23435944037080855
    valeur_ponderee: 0.23435944037080855
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_argent:
    valeur: 0.1507952572071114
    valeur_normalisee: 0.9943063661848168
    valeur_ponderee: 0.9943063661848168
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_argent:
    valeur: -0.0001916722659816017
    valeur_normalisee: 0.029404961911026085
    valeur_ponderee: 0.029404961911026085
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_argent:
    valeur: 0.01639526033017824
    valeur_normalisee: 0.2260279280629774
    valeur_ponderee: 0.2260279280629774
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur: 920112000.0
    valeur_normalisee: -0.5367988110081852
    valeur_ponderee: -0.5367988110081852
    ts: '2026-08-17T05:22:57.159843+00:00'
  noaa_drought_midwest_plains:
    valeur: 0.19619140172993893
    valeur_normalisee: 0.09809570086496947
    valeur_ponderee: 0.09809570086496947
    ts: '2026-08-17T05:22:57.159843+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: 'Signal dominant clairement haussier : frappes ukrainiennes
      sur Novorossiysk (12/08, high) et tensions mer Noire (14/08, high) réduisent
      l''offre, soutenues par vagues de chaleur en Europe (15/08) et baisse de production
      USDA (06/08). Le prix a déjà monté (+3.28% sur 5j), mais la fraîcheur et la
      matér'
    nature: structurel
    event_id: cd16f8309faf
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 123.43333333333332
      7j: 123.43333333333332
      1m: 123.43333333333332
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -31179.0
    valeur_normalisee: 0.1801460824733161
    valeur_ponderee: 0.1801460824733161
    ts: '2026-08-17T05:22:57.159843+00:00'
  meteo_australie_dryland:
    valeur: -0.03401511159573321
    valeur_normalisee: -0.017007555797866607
    valeur_ponderee: -0.017007555797866607
    ts: '2026-08-17T05:22:57.159843+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_ble:
    valeur: 0.014561200789203754
    valeur_normalisee: -0.12252001864123543
    valeur_ponderee: -0.12252001864123543
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_ble:
    valeur: 0.05466991248982511
    valeur_normalisee: 0.4443903480048978
    valeur_ponderee: 0.4443903480048978
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_ble:
    valeur: 0.0011884621783444516
    valeur_normalisee: -0.08419151619922775
    valeur_ponderee: -0.08419151619922775
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-17T05:22:57.159843+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-17T05:22:57.159843+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.012948224719034562
    valeur_normalisee: -0.5316497916658766
    valeur_ponderee: -0.5316497916658766
    ts: '2026-08-17T05:22:57.159843+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.008977035490605467
    valeur_normalisee: -0.32793095964707913
    valeur_ponderee: -0.32793095964707913
    ts: '2026-08-17T05:22:57.159843+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: 'Signaux mitigés : PIB zone euro positif et emploi US faible
      (LONG) contre sécheresse, géopolitique et PMI chinois (SHORT). Prix +3.57% sur
      20j suggère que le positif est déjà intégré, et la baisse récente de -0.90%
      sur 5j reflète les risques SHORT. Pas de signal dominant clair.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: -344.20000000000005
      7j: -344.20000000000005
      1m: -344.20000000000005
  rsi_14j_fchi:
    valeur: 60.54151575868872
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.03573534417575153
    valeur_normalisee: 0.4600546419423196
    valeur_ponderee: 0.4600546419423196
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.0037488610095131047
    valeur_normalisee: -0.4353817992372094
    valeur_ponderee: -0.4353817992372094
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.008966283892315685
    valeur_normalisee: -0.5495392369326129
    valeur_ponderee: -0.5495392369326129
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: -0.0644654512707562
    valeur_normalisee: 0.0322327256353781
    valeur_ponderee: 0.0322327256353781
    ts: '2026-08-17T05:22:57.159843+00:00'
  hf_positioning_flux_options:
    valeur: -15606.0
    valeur_normalisee: -0.5862223435839012
    valeur_ponderee: -0.5862223435839012
    ts: '2026-08-17T05:22:57.159843+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: structurel
    event_id: 7f3f7e335e72
    event_date: '2026-08-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 121.2999999999999
      7j: 121.2999999999999
      1m: 121.2999999999999
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
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: Super El Niño s'intensifie et menace la récolte brésilienne
      (news high du 15/08), renforcée par de multiples alertes El Niño et baisses
      de production ouest-africaine. Les signaux SHORT (météo favorable, offre améliorée)
      sont plus anciens et de matérialité moindre, et le prix a déjà monté de +11%
      sur
    nature: structurel
    event_id: 7f3f7e335e72
    event_date: '2026-08-15T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 123.63333333333324
      7j: 123.63333333333324
      1m: 123.63333333333324
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.11020652810403786
    valeur_normalisee: -0.09681320416051989
    valeur_ponderee: -0.09681320416051989
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.022241843462500577
    valeur_normalisee: -0.3412315116908571
    valeur_ponderee: -0.3412315116908571
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.002327738214287778
    valeur_normalisee: -0.16044669330623204
    valeur_ponderee: -0.16044669330623204
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-17T05:22:57.159843+00:00'
cafe:
  meteo_bresil_minas_gerais:
    ts: '2026-08-17T05:22:57.159843+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-14'
    valeur: -0.40754739096499126
    valeur_normalisee: 0.20377369548249563
    valeur_ponderee: 0.20377369548249563
    reporte_cause: source réseau indisponible
  usd_brl:
    valeur: 5.21917
    valeur_normalisee: 0.927619470463312
    valeur_ponderee: 0.927619470463312
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_coffee:
    valeur: 27282.0
    valeur_normalisee: -0.16470293830600344
    valeur_ponderee: -0.16470293830600344
    ts: '2026-08-17T05:22:57.159843+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: 'Signaux mitigés : El Niño (high) et hausses arabica (medium)
      plaident LONG, mais récolte brésilienne en accélération (medium) et chute des
      prix arabica (medium) plaident SHORT. Le prix a baissé de 7.69% sur 20j, suggérant
      que le marché a déjà pricé les fondamentaux baissiers, et aucune news fraîche '
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 224.7333333333336
      7j: 224.7333333333336
      1m: 224.7333333333336
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-17T05:22:57.159843+00:00'
  meteo_vietnam_robusta:
    ts: '2026-08-17T05:22:57.159843+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-14'
    valeur: 0.37634245498084634
    valeur_normalisee: 0.18817122749042317
    valeur_ponderee: 0.18817122749042317
    reporte_cause: source réseau indisponible
  momentum_prix_20j_cafe:
    valeur: -0.07690757694840233
    valeur_normalisee: -0.7739701814936438
    valeur_ponderee: -0.7739701814936438
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.0028396717114442804
    valeur_normalisee: -0.2178910773492219
    valeur_ponderee: -0.2178910773492219
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.007241689691499964
    valeur_normalisee: -0.013258222870286968
    valeur_ponderee: -0.013258222870286968
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-17T05:22:57.159843+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.048573444207122195
    valeur_normalisee: 0.024286722103561097
    valeur_ponderee: 0.024286722103561097
    ts: '2026-08-17T05:22:57.159843+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.8094874444945113
    valeur_normalisee: 0.40474372224725563
    valeur_ponderee: 0.40474372224725563
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_cotton:
    valeur: 110304.0
    valeur_normalisee: 0.8731439466661239
    valeur_ponderee: 0.8731439466661239
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_coton:
    valeur: 0.0767028022090408
    valeur_normalisee: 0.682191441658359
    valeur_ponderee: 0.682191441658359
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_coton:
    valeur: 0.01897018970189701
    valeur_normalisee: 0.2604164181709367
    valeur_ponderee: 0.2604164181709367
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_coton:
    valeur: 0.012307692307692353
    valeur_normalisee: 0.24580630297706102
    valeur_ponderee: 0.24580630297706102
    ts: '2026-08-17T05:22:57.159843+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '10.22'
    p2_shadow_contrib_exclu:
      24h: 69.53333333333345
      7j: 69.53333333333345
      1m: 69.53333333333345
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-17T05:22:57.159843+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: 'Le prix du cuivre a fortement progressé (+6.52% sur 20j),
      soutenu par des nouvelles récentes à matérialité élevée : plus haut historique
      (2026-08-06) et importations chinoises record (2026-08-05). Les signaux baissiers
      (rebond de l''offre chilienne) sont récurrents mais de matérialité moyenne et
      semb'
    nature: structurel
    event_id: 33d84a40551b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '11.22'
    p2_shadow_contrib_exclu:
      24h: 41.2
      7j: 41.2
      1m: 41.2
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_copper_nets:
    valeur: 80503.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-17T05:22:57.159843+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: structurel
    event_id: 33d84a40551b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '11.22'
    p2_shadow_contrib_exclu:
      24h: 55.90000000000003
      7j: 55.90000000000003
      1m: 55.90000000000003
  ratio_cuivre_or:
    valeur: 0.001526730832692381
    valeur_normalisee: -0.08677691076604142
    valeur_ponderee: -0.08677691076604142
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.06515450372037157
    valeur_normalisee: 0.7141319134494881
    valeur_ponderee: 0.7141319134494881
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.014556980201237302
    valeur_normalisee: 0.22693604948820242
    valeur_ponderee: 0.22693604948820242
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.018026789939213028
    valeur_normalisee: 0.42072908120270414
    valeur_ponderee: 0.42072908120270414
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4590492046000003
    valeur_normalisee: -0.5717051089398907
    valeur_ponderee: -0.5717051089398907
    ts: '2026-08-17T05:22:57.159843+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6599999999999997
    valeur_normalisee: 0.41743042279015885
    valeur_ponderee: 0.41743042279015885
    ts: '2026-08-17T05:22:57.159843+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.06211
    valeur_normalisee: -0.5150851760778001
    valeur_ponderee: -0.5150851760778001
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_eur_nets:
    valeur: -79915.0
    valeur_normalisee: -0.9298361009982374
    valeur_ponderee: -0.9298361009982374
    ts: '2026-08-17T05:22:57.159843+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.017503029877224074
    valeur_normalisee: 0.8462013414146654
    valeur_ponderee: 0.8462013414146654
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.0036991475500727233
    valeur_normalisee: 0.27300480622155526
    valeur_ponderee: 0.27300480622155526
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.0013309710038460487
    valeur_normalisee: 0.13194399459950304
    valeur_ponderee: 0.13194399459950304
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.49614001036431454
    valeur_ponderee: 0.49614001036431454
    ts: '2026-08-17T05:22:57.159843+00:00'
  sox_trend_5j:
    valeur: 550.41998
    valeur_normalisee: -0.15553987717395998
    valeur_ponderee: -0.15553987717395998
    ts: '2026-08-17T05:22:57.159843+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17047614976222106
    valeur_normalisee: 0.667922583620326
    valeur_ponderee: 0.667922583620326
    ts: '2026-08-17T05:22:57.159843+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: Les nouvelles positives sur l'IA et les bénéfices dominent,
      avec des investissements massifs de Nvidia et des dépenses d'entreprise, malgré
      des données de ventes au détail faibles. Le prix a déjà monté de 5% sur 20 jours,
      ce qui suggère que le marché a intégré une partie de ces nouvelles, mais la
      fr
    nature: ponctuel
    event_id: c8f1e8b0443c
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 82.1666666666667
      7j: 82.1666666666667
      1m: 82.1666666666667
  flux_etf_qqq_5j:
    valeur: 0.01111983967127883
    valeur_normalisee: 0.13136295565458514
    valeur_ponderee: 0.13136295565458514
    ts: '2026-08-17T05:22:57.159843+00:00'
  spread_nasdaq_russell2000:
    valeur: 425.98001100000005
    valeur_normalisee: 0.1105544546040728
    valeur_ponderee: 0.1105544546040728
    ts: '2026-08-17T05:22:57.159843+00:00'
  rsi_14j_ixic:
    valeur: 58.4522235035339
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.05140003447571573
    valeur_normalisee: 0.41054073358634763
    valeur_ponderee: 0.41054073358634763
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.01919701267526852
    valeur_normalisee: 0.24158113253087987
    valeur_ponderee: 0.24158113253087987
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.017565588175021407
    valeur_normalisee: 0.3089048240523615
    valeur_ponderee: 0.3089048240523615
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.49614001036431454
    valeur_ponderee: 0.49614001036431454
    ts: '2026-08-17T05:22:57.159843+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_nets:
    valeur: 214856.0
    valeur_normalisee: 0.14816439944873105
    valeur_ponderee: 0.14816439944873105
    ts: '2026-08-17T05:22:57.159843+00:00'
  flux_etf_or_5j:
    valeur: 0.007553918739177323
    valeur_normalisee: 0.19295869351641462
    valeur_ponderee: 0.19295869351641462
    ts: '2026-08-17T05:22:57.159843+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (attaques sur
      Ormuz, escalade Ukraine-Russie, réserves pétrolières US au plus bas) malgré
      quelques signaux SHORT faibles. Le prix a déjà monté de 9% sur 20j, mais la
      fraîcheur et la gravité des risques géopolitiques soutiennent la tendance.
    nature: structurel
    event_id: a2ad4da65bfb
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 385.2333333333318
      7j: 385.2333333333318
      1m: 385.2333333333318
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
    ts: '2026-08-17T05:22:57.159843+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_or:
    valeur: 0.09134478528346857
    valeur_normalisee: 0.967209962345411
    valeur_ponderee: 0.967209962345411
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_or:
    valeur: 0.0014983326852684442
    valeur_normalisee: -0.03953806561378804
    valeur_ponderee: -0.03953806561378804
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_or:
    valeur: 0.00457180786981537
    valeur_normalisee: 0.07254197312076861
    valeur_ponderee: 0.07254197312076861
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-17T05:22:57.159843+00:00'
    reporte: true
    reporte_age_j: 1
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
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: Fermeture quasi totale d'Ormuz, attaques sur pétroliers et
      sanctions russes dominent, signal LONG massif et frais malgré un repli récent
      du prix. Le marché n'a pas encore intégré ces disruptions majeures.
    nature: structurel
    event_id: a2ad4da65bfb
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 362.7333333333321
      7j: 362.7333333333321
      1m: 362.7333333333321
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 23853.0
    valeur_normalisee: -0.045557257567997375
    valeur_ponderee: -0.045557257567997375
    ts: '2026-08-17T05:22:57.159843+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: structurel
    event_id: a2ad4da65bfb
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 335.73333333333113
      7j: 335.73333333333113
      1m: 335.73333333333113
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  cushing_stocks:
    valeur: 22566.0
    valeur_normalisee: -0.15882864718542616
    valeur_ponderee: -0.15882864718542616
    ts: '2026-08-17T05:22:57.159843+00:00'
  spread_brent_wti:
    valeur: 5.011690999999999
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.02048998080976916
    valeur_normalisee: 0.09732593632766802
    valeur_ponderee: 0.09732593632766802
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.052118394994170814
    valeur_normalisee: 0.34915939281114267
    valeur_ponderee: 0.34915939281114267
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.0017456926866897815
    valeur_normalisee: 0.023708815028565536
    valeur_ponderee: 0.023708815028565536
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-17T05:22:57.159843+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.0600000000000005
    valeur_normalisee: -0.4366838575788309
    valeur_ponderee: -0.4366838575788309
    ts: '2026-08-17T05:22:57.159843+00:00'
  hy_credit_spread:
    valeur: 2.71
    valeur_normalisee: -0.23962907560491067
    valeur_ponderee: -0.23962907560491067
    ts: '2026-08-17T05:22:57.159843+00:00'
  breadth_sp_ma50:
    valeur: 0.28694900609466195
    valeur_normalisee: 0.31603652179076464
    valeur_ponderee: 0.31603652179076464
    ts: '2026-08-17T05:22:57.159843+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.003983162144903796
    valeur_normalisee: -0.0016088335612736687
    valeur_ponderee: -0.0016088335612736687
    ts: '2026-08-17T05:22:57.159843+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.56
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-17T05:22:57.159843+00:00'
  rsi_14j_gspc:
    valeur: 64.25333657707091
    ts: '2026-08-17T05:22:57.159843+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.39
    valeur_normalisee: 0.49614001036431454
    valeur_ponderee: 0.49614001036431454
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.04446454397246136
    valeur_normalisee: 0.6540917249934112
    valeur_ponderee: 0.6540917249934112
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.00850887926600441
    valeur_normalisee: 0.07745987342447688
    valeur_ponderee: 0.07745987342447688
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.007501077138704293
    valeur_normalisee: 0.17153852680053985
    valeur_ponderee: 0.17153852680053985
    ts: '2026-08-17T05:22:57.159843+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-17T05:22:57.159843+00:00'
    reporte: true
    reporte_age_j: 5
    reporte_date: '2026-08-10'
    valeur: -0.1786140319430498
    valeur_normalisee: 0.0893070159715249
    valeur_ponderee: 0.0893070159715249
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 87.077853
    valeur_normalisee: 0.19028276896416324
    valeur_ponderee: 0.19028276896416324
    ts: '2026-08-17T05:22:57.159843+00:00'
  usd_brl_sucre:
    valeur: 5.21917
    valeur_normalisee: 0.927619470463312
    valeur_ponderee: 0.927619470463312
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_sugar:
    valeur: 80425.0
    valeur_normalisee: 0.08231776585326993
    valeur_ponderee: 0.08231776585326993
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.10472279260780293
    valeur_normalisee: 0.9363385483963403
    valeur_ponderee: 0.9363385483963403
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.07923771313941819
    valeur_normalisee: 0.8169612722979039
    valeur_ponderee: 0.8169612722979039
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.006463527239150557
    valeur_normalisee: -0.20078296799024775
    valeur_ponderee: -0.20078296799024775
    ts: '2026-08-17T05:22:57.159843+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '10.22'
    p2_shadow_contrib_exclu:
      24h: 54.03333333333334
      7j: 54.03333333333334
      1m: 54.03333333333334
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
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '10.22'
    p2_shadow_contrib_exclu:
      24h: 54.03333333333334
      7j: 54.03333333333334
      1m: 54.03333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-17T05:22:57.159843+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.4800000000000004
    valeur_normalisee: -0.06744969696599419
    valeur_ponderee: -0.06744969696599419
    ts: '2026-08-17T05:22:57.159843+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.0015496785620560116
    valeur_normalisee: -0.02842526093276739
    valeur_ponderee: -0.02842526093276739
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.001572803516933896
    valeur_normalisee: -0.0628168229351301
    valeur_ponderee: -0.0628168229351301
    ts: '2026-08-17T05:22:57.159843+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.029288664629192218
    valeur_normalisee: -0.7918032290922521
    valeur_ponderee: -0.7918032290922521
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_jpy_nets:
    valeur: -40040.0
    valeur_normalisee: 0.031499248803131374
    valeur_ponderee: 0.031499248803131374
    ts: '2026-08-17T05:22:57.159843+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.96
    valeur_normalisee: 0.3779015575742492
    valeur_ponderee: 0.3779015575742492
    ts: '2026-08-17T05:22:57.159843+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-17T05:22:57.159843+00:00'
    nature: ponctuel
    event_id: 267712266c81
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 4.699999999999998
      7j: 4.699999999999998
      1m: 4.699999999999998
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-17T05:22:57.159843+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-17T05:22:57.159843+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-17T05:22:57.159843+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-17T05:22:57.159843+00:00'
  gap_rv_iv:
    valeur: -1.928087376031412
    ts: '2026-08-17T05:22:57.159843+00:00'
  cftc_cot_vix_nets:
    valeur: -74934.0
    valeur_normalisee: -0.44221335910303994
    valeur_ponderee: -0.44221335910303994
    ts: '2026-08-17T05:22:57.159843+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-17T05:22:57.159843+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et fraîches (≤48h)
      : blocus d''Ormuz, attaques de pétroliers, escalade Ukraine-Russie, réserves
      US au plus bas. Malgré la baisse récente du VIX (-13.95%/20j), la persistance
      et l''intensité des tensions géopolitiques justifient un biais haussier.'
    nature: structurel
    event_id: a2ad4da65bfb
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 400.43333333333163
      7j: 400.43333333333163
      1m: 400.43333333333163
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-17T05:22:57.159843+00:00'
```
