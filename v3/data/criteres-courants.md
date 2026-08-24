# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-24T05:57:54.146434+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.24915747214905534
    valeur_ponderee: 0.24915747214905534
    ts: '2026-08-24T05:57:54.146434+00:00'
  mouvement_or_5j:
    valeur: 0.0255611215274405
    valeur_normalisee: 0.34591599045960525
    valeur_ponderee: 0.34591599045960525
    ts: '2026-08-24T05:57:54.146434+00:00'
  ratio_gold_silver:
    valeur: 67.36095067826139
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_silver:
    valeur: 21431.0
    valeur_normalisee: -0.28020633769108966
    valeur_ponderee: -0.28020633769108966
    ts: '2026-08-24T05:57:54.146434+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.0725034199726402
    valeur_normalisee: 0.6506012605164805
    valeur_ponderee: 0.6506012605164805
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_argent:
    valeur: 0.15667549595223162
    valeur_normalisee: 0.7586290802402795
    valeur_ponderee: 0.7586290802402795
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_argent:
    valeur: 0.0465585647591511
    valeur_normalisee: 0.320592735816019
    valeur_ponderee: 0.320592735816019
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_argent:
    valeur: -0.0019181292788981175
    valeur_normalisee: -0.15750426072453885
    valeur_ponderee: -0.15750426072453885
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.1245790864161239
    valeur_normalisee: 0.06228954320806195
    valeur_ponderee: 0.06228954320806195
    ts: '2026-08-24T05:57:54.146434+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: 'Signal dominant LONG massif et cohérent : El Niño extrême,
      sécheresses, tensions mer Noire et attaques sur terminaux céréaliers russes.
      Le prix a déjà monté +8.42%/20j, mais les news les plus récentes (23/08) confirment
      et renforcent le biais haussier.'
    nature: structurel
    event_id: 630bfd372f78
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
    p2_shadow_contrib_exclu:
      24h: 147.23333333333323
      7j: 147.23333333333323
      1m: 147.23333333333323
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -23542.0
    valeur_normalisee: 0.2852130850549151
    valeur_ponderee: 0.2852130850549151
    ts: '2026-08-24T05:57:54.146434+00:00'
  meteo_australie_dryland:
    valeur: -0.050940983819796753
    valeur_normalisee: -0.025470491909898377
    valeur_ponderee: -0.025470491909898377
    ts: '2026-08-24T05:57:54.146434+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_ble:
    valeur: 0.08417293029503581
    valeur_normalisee: 0.283773371663335
    valeur_ponderee: 0.283773371663335
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_ble:
    valeur: 0.02558898564745249
    valeur_normalisee: 0.10208060297150673
    valeur_ponderee: 0.10208060297150673
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_ble:
    valeur: 0.012636826115470123
    valeur_normalisee: 0.0849281940198063
    valeur_ponderee: 0.0849281940198063
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-24T05:57:54.146434+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.003962313727317812
    valeur_normalisee: -0.16801885455101223
    valeur_ponderee: -0.16801885455101223
    ts: '2026-08-24T05:57:54.146434+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.00990099009900991
    valeur_normalisee: -0.3960742475043301
    valeur_ponderee: -0.3960742475043301
    ts: '2026-08-24T05:57:54.146434+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: Échec des négociations US-Canada et tarifs de rétorsion (23/08)
      dominent, renforcés par PMI faible et tensions Moyen-Orient. Malgré un PIB T2
      positif et un accord temporaire le 19/08, le flux récent est clairement négatif,
      cohérent avec la baisse de -1.76% sur 5j.
    nature: structurel
    event_id: 4fdacc1657cc
    event_date: '2026-08-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: -211.49999999999966
      7j: -211.49999999999966
      1m: -211.49999999999966
  rsi_14j_fchi:
    valeur: 45.40205141141123
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.013395325572396422
    valeur_normalisee: -0.16431582447592338
    valeur_ponderee: -0.16431582447592338
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.021961043022401427
    valeur_normalisee: -0.8256531285075821
    valeur_ponderee: -0.8256531285075821
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.002929792484343441
    valeur_normalisee: -0.20136583860469973
    valeur_ponderee: -0.20136583860469973
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-24T05:57:54.146434+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-21'
    valeur: 0.0747558222393906
    valeur_normalisee: 0.0373779111196953
    valeur_ponderee: 0.0373779111196953
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -17088.0
    valeur_normalisee: -0.6073814431844113
    valeur_ponderee: -0.6073814431844113
    ts: '2026-08-24T05:57:54.146434+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: structurel
    event_id: b99d2b50a2e6
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.25'
    p2_shadow_contrib_exclu:
      24h: 131.43333333333334
      7j: 131.43333333333334
      1m: 131.43333333333334
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
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (El
      Niño extrême, baisse de récolte au Ghana) malgré quelques news SHORT plus faibles.
      Le prix a déjà monté de +2.21% sur 20j, mais la fraîcheur et la matérialité
      des news LONG récentes (≤48h) confirment le biais haussier.
    nature: structurel
    event_id: b99d2b50a2e6
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.25'
    p2_shadow_contrib_exclu:
      24h: 134.83333333333326
      7j: 134.83333333333326
      1m: 134.83333333333326
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: -0.009063381407955373
    valeur_normalisee: -0.4412316517191705
    valeur_ponderee: -0.4412316517191705
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.007273877929484529
    valeur_normalisee: -0.22921750895785906
    valeur_ponderee: -0.22921750895785906
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.008797942875928166
    valeur_normalisee: -0.023260484307679817
    valeur_ponderee: -0.023260484307679817
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.41105794010979435
    valeur_normalisee: 0.20552897005489718
    valeur_ponderee: 0.20552897005489718
    ts: '2026-08-24T05:57:54.146434+00:00'
  usd_brl:
    valeur: 5.13847
    valeur_normalisee: 0.04746512998751796
    valeur_ponderee: 0.04746512998751796
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_coffee:
    valeur: 30706.0
    valeur_normalisee: -0.09623866131180062
    valeur_ponderee: -0.09623866131180062
    ts: '2026-08-24T05:57:54.146434+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: Dominance de news LONG liées à El Niño (matérialité high,
      fraîches) malgré quelques news SHORT sur récoltes. Le prix a légèrement baissé
      sur 5j, mais la fraîcheur et la matérialité des news LONG justifient un biais
      haussier modéré.
    nature: structurel
    event_id: f2fd02e28b8a
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
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
    ts: '2026-08-24T05:57:54.146434+00:00'
  meteo_vietnam_robusta:
    valeur: 0.4855264995343699
    valeur_normalisee: 0.24276324976718494
    valeur_ponderee: 0.24276324976718494
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.0005809513291645807
    valeur_normalisee: -0.366047049031157
    valeur_ponderee: -0.366047049031157
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.0162758808893817
    valeur_normalisee: -0.061248140349717525
    valeur_ponderee: -0.061248140349717525
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.006231161713305289
    valeur_normalisee: -0.1746096809900668
    valeur_ponderee: -0.1746096809900668
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
coton:
  meteo_texas_cotton_precip:
    ts: '2026-08-24T05:57:54.146434+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-20'
    valeur: 0.03373235261639925
    valeur_normalisee: 0.016866176308199626
    valeur_ponderee: 0.016866176308199626
    reporte_cause: source réseau indisponible
  meteo_inde_gujarat_coton:
    valeur: 0.8062861674657493
    valeur_normalisee: 0.40314308373287466
    valeur_ponderee: 0.40314308373287466
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_cotton:
    valeur: 113853.0
    valeur_normalisee: 0.9066635816917005
    valeur_ponderee: 0.9066635816917005
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_coton:
    valeur: 0.1031650641025641
    valeur_normalisee: 0.7506458458951784
    valeur_ponderee: 0.7506458458951784
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_coton:
    valeur: 0.04457511380880108
    valeur_normalisee: 0.5329004890757716
    valeur_ponderee: 0.5329004890757716
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_coton:
    valeur: 0.03807728557964185
    valeur_normalisee: 0.6933816556490077
    valeur_ponderee: 0.6933816556490077
    ts: '2026-08-24T05:57:54.146434+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: structurel
    event_id: ee7d1f5f61a6
    event_date: '2026-08-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: 80.66666666666677
      7j: 80.66666666666677
      1m: 80.66666666666677
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: Livraisons LME de 20 000 t et rebond de l'offre chilienne
      dominent, malgré des signaux longs sur les VE et le canal de Panama. Le prix
      a baissé de 0.72% sur 20j, cohérent avec le biais short.
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
    p2_shadow_contrib_exclu:
      24h: 50.53333333333334
      7j: 50.53333333333334
      1m: 50.53333333333334
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_copper_nets:
    valeur: 79513.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-24T05:57:54.146434+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
    p2_shadow_contrib_exclu:
      24h: 61.566666666666634
      7j: 61.566666666666634
      1m: 61.566666666666634
  ratio_cuivre_or:
    valeur: 0.0014150402813778297
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.007151219246580909
    valeur_normalisee: -0.34314120712727036
    valeur_ponderee: -0.34314120712727036
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.005513160227071268
    valeur_normalisee: -0.2919897468512185
    valeur_ponderee: -0.2919897468512185
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.002038740632967273
    valeur_normalisee: -0.19525970740334392
    valeur_ponderee: -0.19525970740334392
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.3986045574000006
    valeur_normalisee: -0.9346806121809953
    valeur_ponderee: -0.9346806121809953
    ts: '2026-08-24T05:57:54.146434+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7200000000000002
    valeur_normalisee: 0.6035951851331854
    valeur_ponderee: 0.6035951851331854
    ts: '2026-08-24T05:57:54.146434+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  usd_jpy_proxy_risk:
    valeur: 158.90135
    valeur_normalisee: -0.4578975205662388
    valeur_ponderee: -0.4578975205662388
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_eur_nets:
    valeur: -80601.0
    valeur_normalisee: -0.9278126647744607
    valeur_ponderee: -0.9278126647744607
    ts: '2026-08-24T05:57:54.146434+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.012780494572191659
    valeur_normalisee: 0.5197098370949308
    valeur_ponderee: 0.5197098370949308
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.008678681531247623
    valeur_normalisee: 0.5397346903758881
    valeur_ponderee: 0.5397346903758881
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.00035969990750572833
    valeur_normalisee: -0.13210108824198902
    valeur_ponderee: -0.13210108824198902
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.24915747214905534
    valeur_ponderee: 0.24915747214905534
    ts: '2026-08-24T05:57:54.146434+00:00'
  sox_trend_5j:
    valeur: 520.049988
    valeur_normalisee: -0.525727136674503
    valeur_ponderee: -0.525727136674503
    ts: '2026-08-24T05:57:54.146434+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1720537115945279
    valeur_normalisee: 0.8432740187080553
    valeur_ponderee: 0.8432740187080553
    ts: '2026-08-24T05:57:54.146434+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: 'Signaux contradictoires : Alibaba placement massif et échec
      négociations US-Canada (SHORT) contre résultats Nvidia et PMI services solide
      (LONG). Le prix a déjà monté de 4.27% sur 20j, suggérant que les nouvelles positives
      sont largement pricées, et la récente baisse de 2.41% sur 5j reflète les crai'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 175.2
      7j: 175.2
      1m: 175.2
  flux_etf_qqq_5j:
    valeur: -0.024115347136652532
    valeur_normalisee: -0.3990929580751604
    valeur_ponderee: -0.3990929580751604
    ts: '2026-08-24T05:57:54.146434+00:00'
  spread_nasdaq_russell2000:
    valeur: 413.48001000000005
    valeur_normalisee: -0.20525288368276376
    valeur_ponderee: -0.20525288368276376
    ts: '2026-08-24T05:57:54.146434+00:00'
  rsi_14j_ixic:
    valeur: 50.19608177622593
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.04269035390703002
    valeur_normalisee: 0.432156174878516
    valeur_ponderee: 0.432156174878516
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.01417715884790438
    valeur_normalisee: -0.22957104304642578
    valeur_ponderee: -0.22957104304642578
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.005672408667859452
    valeur_normalisee: -0.10160202082251528
    valeur_ponderee: -0.10160202082251528
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.24915747214905534
    valeur_ponderee: 0.24915747214905534
    ts: '2026-08-24T05:57:54.146434+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_nets:
    valeur: 219495.0
    valeur_normalisee: 0.188135627570805
    valeur_ponderee: 0.188135627570805
    ts: '2026-08-24T05:57:54.146434+00:00'
  flux_etf_or_5j:
    valeur: 0.05449830490937768
    valeur_normalisee: 0.8372368950830806
    valeur_ponderee: 0.8372368950830806
    ts: '2026-08-24T05:57:54.146434+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et fraîche (24/08)
      : offensive US contre l''Iran, menace de saisie de navires, et risque de blocage
      d''Ormuz. Le dollar faible et la demande ETF renforcent le biais haussier, cohérent
      avec le prix (+13.78%/20j).'
    nature: structurel
    event_id: ec250db3685b
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 484.2666666666645
      7j: 484.2666666666645
      1m: 484.2666666666645
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
    ts: '2026-08-24T05:57:54.146434+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_or:
    valeur: 0.1377027572675389
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_or:
    valeur: 0.05031829661423215
    valeur_normalisee: 0.6425128842025014
    valeur_ponderee: 0.6425128842025014
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_or:
    valeur: 0.0075898604252637725
    valeur_normalisee: 0.01917791079621885
    valeur_ponderee: 0.01917791079621885
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-24T05:57:54.146434+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-21'
    valeur: 428815.0
    valeur_normalisee: -0.007281118678166014
    valeur_ponderee: -0.007281118678166014
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: Menaces iraniennes de stopper les exportations pétrolières
      et offensive financière US dominent, avec déclin des stocks mondiaux et blocage
      d'Ormuz. Les news SHORT sont surtout des réactions tactiques à l'annonce de
      sanctions, sans matérialité suffisante face au signal LONG massif et frais.
    nature: structurel
    event_id: ec250db3685b
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 452.83333333333167
      7j: 452.83333333333167
      1m: 452.83333333333167
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 16985.0
    valeur_normalisee: -0.19062765856647587
    valeur_ponderee: -0.19062765856647587
    ts: '2026-08-24T05:57:54.146434+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: structurel
    event_id: ec250db3685b
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 418.19999999999857
      7j: 418.19999999999857
      1m: 418.19999999999857
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  cushing_stocks:
    valeur: 21252.0
    valeur_normalisee: -0.36351247895781225
    valeur_ponderee: -0.36351247895781225
    ts: '2026-08-24T05:57:54.146434+00:00'
  spread_brent_wti:
    valeur: 5.8424499999999995
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.07146548263333674
    valeur_normalisee: 0.34232690902909635
    valeur_ponderee: 0.34232690902909635
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.06523508872648698
    valeur_normalisee: 0.34600900060903106
    valeur_ponderee: 0.34600900060903106
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.01515776779020439
    valeur_normalisee: 0.11736324360218856
    valeur_ponderee: 0.11736324360218856
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-24T05:57:54.146434+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.0600000000000005
    valeur_normalisee: 0.3284813800447446
    valeur_ponderee: 0.3284813800447446
    ts: '2026-08-24T05:57:54.146434+00:00'
  hy_credit_spread:
    valeur: 2.75
    valeur_normalisee: 0.15366214850783944
    valeur_ponderee: 0.15366214850783944
    ts: '2026-08-24T05:57:54.146434+00:00'
  breadth_sp_ma50:
    valeur: 0.2894922539371671
    valeur_normalisee: 0.562857242204311
    valeur_ponderee: 0.562857242204311
    ts: '2026-08-24T05:57:54.146434+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.01367965013990069
    valeur_normalisee: -0.44995975138811445
    valeur_ponderee: -0.44995975138811445
    ts: '2026-08-24T05:57:54.146434+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.96
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-24T05:57:54.146434+00:00'
  rsi_14j_gspc:
    valeur: 54.327644123702285
    ts: '2026-08-24T05:57:54.146434+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.35
    valeur_normalisee: 0.24915747214905534
    valeur_ponderee: 0.24915747214905534
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.036255099079142816
    valeur_normalisee: 0.5396620105433677
    valeur_ponderee: 0.5396620105433677
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.008763893497183095
    valeur_normalisee: -0.3183518329078704
    valeur_ponderee: -0.3183518329078704
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.0022542706071501106
    valeur_normalisee: -0.12151387445005311
    valeur_ponderee: -0.12151387445005311
    ts: '2026-08-24T05:57:54.146434+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.34400602012671605
    valeur_normalisee: 0.17200301006335803
    valeur_ponderee: 0.17200301006335803
    ts: '2026-08-24T05:57:54.146434+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 91.4388
    valeur_normalisee: 0.5074036154600199
    valeur_ponderee: 0.5074036154600199
    ts: '2026-08-24T05:57:54.146434+00:00'
  usd_brl_sucre:
    valeur: 5.13847
    valeur_normalisee: 0.04746512998751796
    valeur_ponderee: 0.04746512998751796
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_sugar:
    valeur: 139023.0
    valeur_normalisee: 0.3151137091263304
    valeur_ponderee: 0.3151137091263304
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.15447991761071056
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.04864359214218905
    valeur_normalisee: 0.3946682312580932
    valeur_ponderee: 0.3946682312580932
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.0026833631484795006
    valeur_normalisee: -0.08934821657454059
    valeur_ponderee: -0.08934821657454059
    ts: '2026-08-24T05:57:54.146434+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: structurel
    event_id: ee7d1f5f61a6
    event_date: '2026-08-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: 61.8333333333334
      7j: 61.8333333333334
      1m: 61.8333333333334
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
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: structurel
    event_id: ee7d1f5f61a6
    event_date: '2026-08-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: 61.8333333333334
      7j: 61.8333333333334
      1m: 61.8333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-24T05:57:54.146434+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5200000000000005
    valeur_normalisee: 0.13195006840820678
    valeur_ponderee: 0.13195006840820678
    ts: '2026-08-24T05:57:54.146434+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.0035889689043401285
    valeur_normalisee: -0.06742446438523128
    valeur_ponderee: -0.06742446438523128
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.0005186209124558028
    valeur_normalisee: 0.01738859276939019
    valeur_ponderee: 0.01738859276939019
    ts: '2026-08-24T05:57:54.146434+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.007364365289306063
    valeur_normalisee: 0.3406776778760848
    valeur_ponderee: 0.3406776778760848
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_jpy_nets:
    valeur: -52476.0
    valeur_normalisee: -0.04638456092591132
    valeur_ponderee: -0.04638456092591132
    ts: '2026-08-24T05:57:54.146434+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0200000000000005
    valeur_normalisee: 0.6167987899630603
    valeur_ponderee: 0.6167987899630603
    ts: '2026-08-24T05:57:54.146434+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-24T05:57:54.146434+00:00'
    nature: structurel
    event_id: b93cae4ee23f
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
    p2_shadow_contrib_exclu:
      24h: 11.033333333333331
      7j: 11.033333333333331
      1m: 11.033333333333331
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-24T05:57:54.146434+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-24T05:57:54.146434+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-24T05:57:54.146434+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-24T05:57:54.146434+00:00'
  gap_rv_iv:
    valeur: -2.100891930425238
    ts: '2026-08-24T05:57:54.146434+00:00'
  cftc_cot_vix_nets:
    valeur: -89446.0
    valeur_normalisee: -0.7211456087175471
    valeur_ponderee: -0.7211456087175471
    ts: '2026-08-24T05:57:54.146434+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-24T05:57:54.146434+00:00'
    synthese_rationale: 'Signal dominant clair : escalade géopolitique majeure (Iran,
      Russie) avec menaces sur le détroit d''Ormuz et sanctions économiques, toutes
      les news récentes étant LONG. Malgré la baisse du VIX sur 20j, la fraîcheur
      et la matérialité élevée des news du jour justifient de maintenir la direction
      LONG.'
    nature: structurel
    event_id: ec250db3685b
    event_date: '2026-08-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 484.03333333333063
      7j: 484.03333333333063
      1m: 484.03333333333063
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-24T05:57:54.146434+00:00'
```
