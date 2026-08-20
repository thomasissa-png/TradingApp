# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-20T05:23:21.622666+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5195710868141741
    valeur_ponderee: 0.5195710868141741
    ts: '2026-08-20T05:23:21.622666+00:00'
  mouvement_or_5j:
    valeur: 0.025122269762966054
    valeur_normalisee: 0.43022837551278426
    valeur_ponderee: 0.43022837551278426
    ts: '2026-08-20T05:23:21.622666+00:00'
  ratio_gold_silver:
    valeur: 66.95222927274166
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_silver:
    valeur: 21465.0
    valeur_normalisee: -0.2803992279605361
    valeur_ponderee: -0.2803992279605361
    ts: '2026-08-20T05:23:21.622666+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.016085290956903364
    valeur_normalisee: 0.2533459849995179
    valeur_ponderee: 0.2533459849995179
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_argent:
    valeur: 0.16299026350038792
    valeur_normalisee: 0.9489151875942313
    valeur_ponderee: 0.9489151875942313
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_argent:
    valeur: 0.03962207831174824
    valeur_normalisee: 0.32715906539033435
    valeur_ponderee: 0.32715906539033435
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_argent:
    valeur: 0.018576335635355434
    valeur_normalisee: 0.22604064754480985
    valeur_ponderee: 0.22604064754480985
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.20304143625264642
    valeur_normalisee: 0.10152071812632321
    valeur_ponderee: 0.10152071812632321
    ts: '2026-08-20T05:23:21.622666+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (frappes
      sur Novorossiysk, tensions mer Noire, sécheresse Europe) malgré une prise de
      bénéfices isolée. Le prix +6.87%/20j confirme le biais haussier, et les news
      récentes (≤48h) renforcent la tendance.
    nature: structurel
    event_id: 2b47e84d9080
    event_date: '2026-08-17T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 137.89999999999992
      7j: 137.89999999999992
      1m: 137.89999999999992
  cftc_cot_wheat:
    valeur: -31179.0
    valeur_normalisee: 0.1801460824733161
    valeur_ponderee: 0.1801460824733161
    ts: '2026-08-20T05:23:21.622666+00:00'
  meteo_australie_dryland:
    valeur: -0.08483197118971558
    valeur_normalisee: -0.04241598559485779
    valeur_ponderee: -0.04241598559485779
    ts: '2026-08-20T05:23:21.622666+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_ble:
    valeur: 0.06897272261966947
    valeur_normalisee: 0.2153507789014733
    valeur_ponderee: 0.2153507789014733
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_ble:
    valeur: 0.04431239615169558
    valeur_normalisee: 0.3252072948032758
    valeur_ponderee: 0.3252072948032758
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_ble:
    valeur: 0.011162089485166726
    valeur_normalisee: 0.09701352518649181
    valeur_ponderee: 0.09701352518649181
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-20T05:23:21.622666+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.015505812786516637
    valeur_normalisee: -0.5519334270389862
    valeur_ponderee: -0.5519334270389862
    ts: '2026-08-20T05:23:21.622666+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.007366870132603731
    valeur_normalisee: -0.31691273079917265
    valeur_ponderee: -0.31691273079917265
    ts: '2026-08-20T05:23:21.622666+00:00'
  tension_politique_fr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: Les news les plus récentes (19-20 août) sont toutes LONG,
      portées par l'accord commercial US-Canada, et dominent les news SHORT plus anciennes
      (18 août) liées aux tensions Moyen-Orient. Le PIB zone euro solide et les données
      US faibles (emploi) soutiennent aussi le biais LONG, malgré le repli récent
    nature: verbal
    event_id: 835d109b8de0
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -192.49999999999977
      7j: -192.49999999999977
      1m: -192.49999999999977
  rsi_14j_fchi:
    valeur: 47.392800502847656
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.007587265614453775
    valeur_normalisee: -0.3182369624702285
    valeur_ponderee: -0.3182369624702285
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.025684086117999327
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.015618011662143827
    valeur_normalisee: -0.7593859573219452
    valeur_ponderee: -0.7593859573219452
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-20T05:23:21.622666+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-18'
    valeur: -0.03261425247044984
    valeur_normalisee: 0.01630712623522492
    valeur_ponderee: 0.01630712623522492
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -15606.0
    valeur_normalisee: -0.5862223435839012
    valeur_ponderee: -0.5862223435839012
    ts: '2026-08-20T05:23:21.622666+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: structurel
    event_id: af57c806570b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 128.76666666666665
      7j: 128.76666666666665
      1m: 128.76666666666665
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
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: Dominance de news LONG à matérialité high (Super El Niño menaçant
      la production du Ghana, Brésil, et deux récoltes) et fraîches (19-20 août),
      cohérentes avec le prix en hausse de +11.79% sur 20j. Une seule news SHORT (conditions
      favorables en Afrique de l'Ouest) est plus ancienne et de matérialité m
    nature: structurel
    event_id: af57c806570b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 131.33333333333331
      7j: 131.33333333333331
      1m: 131.33333333333331
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.11794533472936841
    valeur_normalisee: -0.08480792619948159
    valeur_ponderee: -0.08480792619948159
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.05690742696604678
    valeur_normalisee: 0.059832041335113655
    valeur_ponderee: 0.059832041335113655
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.007702737269324578
    valeur_normalisee: -0.21450477496449874
    valeur_ponderee: -0.21450477496449874
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.41323086128874437
    valeur_normalisee: 0.20661543064437218
    valeur_ponderee: 0.20661543064437218
    ts: '2026-08-20T05:23:21.622666+00:00'
  usd_brl:
    valeur: 5.17842
    valeur_normalisee: 0.45257802860931545
    valeur_ponderee: 0.45257802860931545
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_coffee:
    valeur: 27282.0
    valeur_normalisee: -0.16470293830600344
    valeur_ponderee: -0.16470293830600344
    ts: '2026-08-20T05:23:21.622666+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: Les news récentes (18-19 août) dominent avec un signal LONG
      répété sur les risques d'offre liés à El Niño/Super El Niño, malgré quelques
      news SHORT plus anciennes sur la récolte brésilienne. Le prix a rebondi de +4.40%
      sur 5j, cohérent avec le biais LONG, mais la matérialité moyenne et la dispersion
    nature: structurel
    event_id: f2fd02e28b8a
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 115.60000000000022
      7j: 115.60000000000022
      1m: 115.60000000000022
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
    ts: '2026-08-20T05:23:21.622666+00:00'
  meteo_vietnam_robusta:
    valeur: 0.49311581609125843
    valeur_normalisee: 0.24655790804562921
    valeur_ponderee: 0.24655790804562921
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.009932656981518462
    valeur_normalisee: -0.44927083403245904
    valeur_ponderee: -0.44927083403245904
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.04665160362166332
    valeur_normalisee: 0.19298354196186335
    valeur_ponderee: 0.19298354196186335
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.033100859578430564
    valeur_normalisee: 0.253420125601733
    valeur_ponderee: 0.253420125601733
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.03373235261639925
    valeur_normalisee: 0.016866176308199626
    valeur_ponderee: 0.016866176308199626
    ts: '2026-08-20T05:23:21.622666+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.8093129370246495
    valeur_normalisee: 0.40465646851232473
    valeur_ponderee: 0.40465646851232473
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_cotton:
    valeur: 110304.0
    valeur_normalisee: 0.8731439466661239
    valeur_ponderee: 0.8731439466661239
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_coton:
    valeur: 0.08107036669970258
    valeur_normalisee: 0.6476966017590229
    valeur_ponderee: 0.6476966017590229
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_coton:
    valeur: 0.04482758620689653
    valeur_normalisee: 0.5676537283470249
    valeur_ponderee: 0.5676537283470249
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_coton:
    valeur: 0.03609422492401215
    valeur_normalisee: 0.7050269871316445
    valeur_ponderee: 0.7050269871316445
    ts: '2026-08-20T05:23:21.622666+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: structurel
    event_id: 2f90239ca8a8
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 74.7000000000001
      7j: 74.7000000000001
      1m: 74.7000000000001
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: Livraisons LME de 20 000 t et effondrement du backwardation
      (high, 19/08) dominent, renforcées par le rebond de l'offre chilienne et le
      ralentissement chinois. Les signaux LONG (stocks LME en baisse, demande VE)
      sont plus anciens et contredits par le prix (-2% sur 5j).
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 48.433333333333344
      7j: 48.433333333333344
      1m: 48.433333333333344
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_copper_nets:
    valeur: 80503.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-20T05:23:21.622666+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: ponctuel
    event_id: acb5ff5c2d5b
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 60.466666666666654
      7j: 60.466666666666654
      1m: 60.466666666666654
  ratio_cuivre_or:
    valeur: 0.0014420294246021155
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.0018117339868333193
    valeur_normalisee: -0.15735736807716988
    valeur_ponderee: -0.15735736807716988
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.01700272943350578
    valeur_normalisee: -0.42562831058111944
    valeur_ponderee: -0.42562831058111944
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.020048268558624516
    valeur_normalisee: -0.5575306168859108
    valeur_ponderee: -0.5575306168859108
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4095391187000006
    valeur_normalisee: -0.935070864861787
    valeur_ponderee: -0.935070864861787
    ts: '2026-08-20T05:23:21.622666+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7399999999999998
    valeur_normalisee: 0.7327970614843283
    valeur_ponderee: 0.7327970614843283
    ts: '2026-08-20T05:23:21.622666+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  usd_jpy_proxy_risk:
    valeur: 158.62032
    valeur_normalisee: -0.5796930562424062
    valeur_ponderee: -0.5796930562424062
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_eur_nets:
    valeur: -79915.0
    valeur_normalisee: -0.9298361009982374
    valeur_ponderee: -0.9298361009982374
    ts: '2026-08-20T05:23:21.622666+00:00'
  balance_commerciale_ez:
    valeur: 8574.2
    valeur_normalisee: 0.23448230141445794
    valeur_ponderee: 0.23448230141445794
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.012401998196073016
    valeur_normalisee: 0.5597573441799529
    valeur_ponderee: 0.5597573441799529
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.012516154773572818
    valeur_normalisee: 0.8566521283627216
    valeur_ponderee: 0.8566521283627216
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.008056925242441837
    valeur_normalisee: 0.8847066363347077
    valeur_ponderee: 0.8847066363347077
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5195710868141741
    valeur_ponderee: 0.5195710868141741
    ts: '2026-08-20T05:23:21.622666+00:00'
  sox_trend_5j:
    valeur: 519.66998
    valeur_normalisee: -0.55997910832987
    valeur_ponderee: -0.55997910832987
    ts: '2026-08-20T05:23:21.622666+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1716986888072873
    valeur_normalisee: 0.8239114638958128
    valeur_ponderee: 0.8239114638958128
    ts: '2026-08-20T05:23:21.622666+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese_news_high
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: 'Signaux contradictoires : vente massive sur les semi-conducteurs
      et hausse des rendements obligataires (SHORT) contre rachats du Trésor et nouvelles
      sur Nvidia (LONG). Le prix a légèrement progressé sur 20j mais reculé sur 5j,
      indiquant une absence de biais net.'
    nature: ponctuel
    event_id: 4ab3bb72aaeb
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 169.9333333333335
      7j: 169.9333333333335
      1m: 169.9333333333335
  flux_etf_qqq_5j:
    valeur: -0.010529214998905467
    valeur_normalisee: -0.19614388465703814
    valeur_ponderee: -0.19614388465703814
    ts: '2026-08-20T05:23:21.622666+00:00'
  spread_nasdaq_russell2000:
    valeur: 414.36001699999997
    valeur_normalisee: -0.20173994250399524
    valeur_ponderee: -0.20173994250399524
    ts: '2026-08-20T05:23:21.622666+00:00'
  rsi_14j_ixic:
    valeur: 51.72697607007561
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.015212358834971518
    valeur_normalisee: 0.08898203335333564
    valeur_ponderee: 0.08898203335333564
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.006644725123808759
    valeur_normalisee: -0.13530573628701717
    valeur_ponderee: -0.13530573628701717
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.02050417861007947
    valeur_normalisee: -0.41843846585402705
    valeur_ponderee: -0.41843846585402705
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-20T05:23:21.622666+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5195710868141741
    valeur_ponderee: 0.5195710868141741
    ts: '2026-08-20T05:23:21.622666+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_nets:
    valeur: 214856.0
    valeur_normalisee: 0.14816439944873105
    valeur_ponderee: 0.14816439944873105
    ts: '2026-08-20T05:23:21.622666+00:00'
  flux_etf_or_5j:
    valeur: 0.022029017533611084
    valeur_normalisee: 0.3964891578547404
    valeur_ponderee: 0.3964891578547404
    ts: '2026-08-20T05:23:21.622666+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (frappes
      russes sur Kyiv, guerre économique contre l'Iran, blocus d'Ormuz) malgré quelques
      news SHORT faibles. Le prix (+10.88% sur 20j) confirme la tendance haussière.
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 435.7333333333316
      7j: 435.7333333333316
      1m: 435.7333333333316
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-20T05:23:21.622666+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_or:
    valeur: 0.10883387591477289
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_or:
    valeur: 0.03087363142319055
    valeur_normalisee: 0.40912532560663656
    valeur_ponderee: 0.40912532560663656
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_or:
    valeur: 0.01559664107945724
    valeur_normalisee: 0.2980178561491355
    valeur_ponderee: 0.2980178561491355
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
petrole:
  eia_crude_surprise:
    valeur: 428815.0
    valeur_normalisee: -0.007281118678166014
    valeur_ponderee: -0.007281118678166014
    ts: '2026-08-20T05:23:21.622666+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et fraîcheur
      immédiate (20/08) : guerre économique US-Iran, ralentissement à Ormuz, déficit
      d''offre. Malgré -5.14% sur 20j, le rebond récent (+4.92% sur 5j) et la fraîcheur
      des drivers géopolitiques justifient de suivre le signal.'
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 409.3666666666657
      7j: 409.3666666666657
      1m: 409.3666666666657
  cftc_cot_crude_nets:
    valeur: 23853.0
    valeur_normalisee: -0.045557257567997375
    valeur_ponderee: -0.045557257567997375
    ts: '2026-08-20T05:23:21.622666+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 383.06666666666484
      7j: 383.06666666666484
      1m: 383.06666666666484
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
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  cushing_stocks:
    valeur: 21252.0
    valeur_normalisee: -0.36351247895781225
    valeur_ponderee: -0.36351247895781225
    ts: '2026-08-20T05:23:21.622666+00:00'
  spread_brent_wti:
    valeur: 5.585821999999993
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.05138946893219032
    valeur_normalisee: -0.0186075812634181
    valeur_ponderee: -0.0186075812634181
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.02539742684300461
    valeur_normalisee: 0.1641016381851217
    valeur_ponderee: 0.1641016381851217
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.0030696651103310213
    valeur_normalisee: 0.019106000591937514
    valeur_ponderee: 0.019106000591937514
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-20T05:23:21.622666+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.009999999999999787
    valeur_normalisee: 0.020342146052462002
    valeur_ponderee: 0.020342146052462002
    ts: '2026-08-20T05:23:21.622666+00:00'
  hy_credit_spread:
    valeur: 2.75
    valeur_normalisee: 0.16007853467443775
    valeur_ponderee: 0.16007853467443775
    ts: '2026-08-20T05:23:21.622666+00:00'
  breadth_sp_ma50:
    valeur: 0.2887551134859572
    valeur_normalisee: 0.49614799951280353
    valeur_ponderee: 0.49614799951280353
    ts: '2026-08-20T05:23:21.622666+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.004440176629343928
    valeur_normalisee: -0.21421860595990388
    valeur_ponderee: -0.21421860595990388
    ts: '2026-08-20T05:23:21.622666+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.15
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-20T05:23:21.622666+00:00'
  rsi_14j_gspc:
    valeur: 57.72530851520939
    ts: '2026-08-20T05:23:21.622666+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.5195710868141741
    valeur_ponderee: 0.5195710868141741
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.028966736956960615
    valeur_normalisee: 0.34977602318830026
    valeur_ponderee: 0.34977602318830026
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.0051356750075229884
    valeur_normalisee: -0.24705302682212293
    valeur_ponderee: -0.24705302682212293
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.009377375529637466
    valeur_normalisee: -0.393588122273501
    valeur_ponderee: -0.393588122273501
    ts: '2026-08-20T05:23:21.622666+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-20T05:23:21.622666+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-08-18'
    valeur: -0.2777963714867588
    valeur_normalisee: 0.1388981857433794
    valeur_ponderee: 0.1388981857433794
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 90.061302
    valeur_normalisee: 0.3987644522945645
    valeur_ponderee: 0.3987644522945645
    ts: '2026-08-20T05:23:21.622666+00:00'
  usd_brl_sucre:
    valeur: 5.17842
    valeur_normalisee: 0.45257802860931545
    valeur_ponderee: 0.45257802860931545
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_sugar:
    valeur: 80425.0
    valeur_normalisee: 0.08231776585326993
    valeur_ponderee: 0.08231776585326993
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.15637860082304522
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.05046728971962633
    valeur_normalisee: 0.4386750076847564
    valeur_ponderee: 0.4386750076847564
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.04460966542750944
    valeur_normalisee: 0.7282883604177925
    valeur_ponderee: 0.7282883604177925
    ts: '2026-08-20T05:23:21.622666+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: structurel
    event_id: 264d7b6b38d9
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 60.80000000000004
      7j: 60.80000000000004
      1m: 60.80000000000004
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
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: structurel
    event_id: 264d7b6b38d9
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 60.80000000000004
      7j: 60.80000000000004
      1m: 60.80000000000004
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5200000000000005
    valeur_normalisee: 0.1491814210980041
    valeur_ponderee: 0.1491814210980041
    ts: '2026-08-20T05:23:21.622666+00:00'
  dxy_trend_20j:
    valeur: 118.9028
    valeur_normalisee: -0.7607886169235872
    valeur_ponderee: -0.7607886169235872
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.005550096236689117
    valeur_normalisee: -0.15815825566335703
    valeur_ponderee: -0.15815825566335703
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.00521235448600732
    valeur_normalisee: -0.2527348646319172
    valeur_ponderee: -0.2527348646319172
    ts: '2026-08-20T05:23:21.622666+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.007473267707024167
    valeur_normalisee: 0.3449420464453181
    valeur_ponderee: 0.3449420464453181
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_jpy_nets:
    valeur: -40040.0
    valeur_normalisee: 0.031499248803131374
    valeur_ponderee: 0.031499248803131374
    ts: '2026-08-20T05:23:21.622666+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.04
    valeur_normalisee: 0.7497684927567418
    valeur_ponderee: 0.7497684927567418
    ts: '2026-08-20T05:23:21.622666+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-20T05:23:21.622666+00:00'
    nature: structurel
    event_id: b93cae4ee23f
    event_date: '2026-08-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 8.333333333333352
      7j: 8.333333333333352
      1m: 8.333333333333352
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-20T05:23:21.622666+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-20T05:23:21.622666+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-20T05:23:21.622666+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-20T05:23:21.622666+00:00'
  gap_rv_iv:
    valeur: -1.670399023937902
    ts: '2026-08-20T05:23:21.622666+00:00'
  cftc_cot_vix_nets:
    valeur: -74934.0
    valeur_normalisee: -0.44221335910303994
    valeur_ponderee: -0.44221335910303994
    ts: '2026-08-20T05:23:21.622666+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-20T05:23:21.622666+00:00'
    synthese_rationale: 'Signal dominant clair : escalade géopolitique majeure (menaces
      Trump/Iran, frappes russes sur Kyiv, attaques en mer Rouge, perturbations d''Ormuz)
      avec matérialité élevée et fraîcheur immédiate (toutes news du 20/08). Malgré
      la baisse récente du VIX, ces événements récents et de forte intensité justi'
    nature: verbal
    event_id: 22c09f3ded75
    event_date: '2026-08-20T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 445.0666666666644
      7j: 445.0666666666644
      1m: 445.0666666666644
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-20T05:23:21.622666+00:00'
```
