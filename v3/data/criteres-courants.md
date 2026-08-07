# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-07T05:23:14.663592+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.6806703918419534
    valeur_ponderee: 0.6806703918419534
    ts: '2026-08-07T05:23:14.663592+00:00'
  mouvement_or_5j:
    valeur: 0.055681269640274866
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  ratio_gold_silver:
    valeur: 68.48531090276832
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_silver:
    valeur: 20236.0
    valeur_normalisee: -0.31454313983426346
    valeur_ponderee: -0.31454313983426346
    ts: '2026-08-07T05:23:14.663592+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.043925233644859896
    valeur_normalisee: 0.37983498440347363
    valeur_ponderee: 0.37983498440347363
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_argent:
    valeur: 0.11373716326302219
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_argent:
    valeur: 0.08125996736855567
    valeur_normalisee: 0.8246215653421971
    valeur_ponderee: 0.8246215653421971
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_argent:
    valeur: 0.04663589772364363
    valeur_normalisee: 0.6088260767623378
    valeur_ponderee: 0.6088260767623378
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.17799138439972464
    valeur_normalisee: 0.08899569219986232
    valeur_ponderee: 0.08899569219986232
    ts: '2026-08-07T05:23:14.663592+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: 'Signal dominant clairement haussier : USDA prévoit baisse
      production et stocks mondiaux, frappes russes sur Odessa menacent exportations,
      sécheresse en Europe et chaleur aux US. Malgré -7.25% sur 20j, les news fraîches
      (≤48h) à matérialité high confirment un choc d''offre, justifiant de suivre
      le sig'
    nature: structurel
    event_id: aa42529c633b
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 90.43333333333341
      7j: 90.43333333333341
      1m: 90.43333333333341
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -5384.0
    valeur_normalisee: 0.5293592418323769
    valeur_ponderee: 0.5293592418323769
    ts: '2026-08-07T05:23:14.663592+00:00'
  meteo_australie_dryland:
    valeur: -0.08468508499255537
    valeur_normalisee: -0.04234254249627768
    valeur_ponderee: -0.04234254249627768
    ts: '2026-08-07T05:23:14.663592+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_ble:
    valeur: -0.07247393876833197
    valeur_normalisee: -0.5710955173291823
    valeur_ponderee: -0.5710955173291823
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_ble:
    valeur: -0.007699185261319186
    valeur_normalisee: -0.20265337055903074
    valeur_ponderee: -0.20265337055903074
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_ble:
    valeur: -0.007746327877096837
    valeur_normalisee: -0.23785404911840927
    valeur_ponderee: -0.23785404911840927
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-07T05:23:14.663592+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.011000710928309454
    valeur_normalisee: -0.3573355113911135
    valeur_ponderee: -0.3573355113911135
    ts: '2026-08-07T05:23:14.663592+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.024316763503335448
    valeur_normalisee: 0.5233400807705549
    valeur_ponderee: 0.5233400807705549
    ts: '2026-08-07T05:23:14.663592+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: 'Les news récentes sont mitigées : des signaux SHORT liés
      à la sécheresse et aux tensions géopolitiques (frappes sur l''Iran) s''opposent
      à des signaux LONG (PMI solides, apaisement Moyen-Orient). Le prix a déjà progressé
      de +4.48% sur 20j, suggérant que les bonnes nouvelles sont intégrées, et les
      risq'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: -269.9333333333328
      7j: -269.9333333333328
      1m: -269.9333333333328
  rsi_14j_fchi:
    valeur: 69.3144118169325
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.044806876574549515
    valeur_normalisee: 0.7324678048015366
    valeur_ponderee: 0.7324678048015366
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.028482793299937637
    valeur_normalisee: 0.672552293907776
    valeur_ponderee: 0.672552293907776
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.009971144847343627
    valeur_normalisee: 0.2584132879273834
    valeur_ponderee: 0.2584132879273834
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-07T05:23:14.663592+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-06'
    valeur: 0.08231768080661178
    valeur_normalisee: 0.04115884040330589
    valeur_ponderee: 0.04115884040330589
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -15428.0
    valeur_normalisee: -0.5922330245608465
    valeur_ponderee: -0.5922330245608465
    ts: '2026-08-07T05:23:14.663592+00:00'
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: structurel
    event_id: df1bf2a2c3f4
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 109.93333333333334
      7j: 109.93333333333334
      1m: 109.93333333333334
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
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Les news LONG dominent nettement, notamment la baisse de production
      de 16% au Ghana et les impacts El Niño, avec matérialité élevée et fraîcheur
      récente. Les news SHORT récentes (offre abondante, baisse des prix) sont moins
      nombreuses et de matérialité inférieure, et le prix a déjà monté de 7% sur 5
    nature: structurel
    event_id: 63b5ff8bb33d
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 111.33333333333334
      7j: 111.33333333333334
      1m: 111.33333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.044309952970126965
    valeur_normalisee: -0.2576215957976863
    valeur_ponderee: -0.2576215957976863
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.0705770418181304
    valeur_normalisee: 0.09357584734666029
    valeur_ponderee: 0.09357584734666029
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.051460155085125026
    valeur_normalisee: -0.6020191056319694
    valeur_ponderee: -0.6020191056319694
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.3962270150369114
    valeur_normalisee: 0.1981135075184557
    valeur_ponderee: 0.1981135075184557
    ts: '2026-08-07T05:23:14.663592+00:00'
  usd_brl:
    valeur: 5.11897
    valeur_normalisee: -0.0812371711874568
    valeur_ponderee: -0.0812371711874568
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_coffee:
    valeur: 27914.0
    valeur_normalisee: -0.15738525585500848
    valeur_ponderee: -0.15738525585500848
    ts: '2026-08-07T05:23:14.663592+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Les news récentes (4 août) montrent une chute des prix de
      l'Arabica, renforcée par des baisses antérieures (29-30 juillet), malgré quelques
      signaux haussiers (Fairtrade, prix Vietnam). Le mouvement de prix (-7.82% sur
      5j) confirme la tendance baissière, mais la matérialité moyenne et la dispersion
      d
    nature: ponctuel
    event_id: 5fc518d40698
    event_date: '2026-08-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 106.53333333333353
      7j: 106.53333333333353
      1m: 106.53333333333353
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-07T05:23:14.663592+00:00'
  meteo_vietnam_robusta:
    valeur: 0.3319366854552472
    valeur_normalisee: 0.1659683427276236
    valeur_ponderee: 0.1659683427276236
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_cafe:
    valeur: -0.04371826367325027
    valeur_normalisee: -0.5397926866103255
    valeur_ponderee: -0.5397926866103255
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.07606636201457795
    valeur_normalisee: -0.8629436533165894
    valeur_ponderee: -0.8629436533165894
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.05189863866855271
    valeur_normalisee: -0.7371356724578355
    valeur_ponderee: -0.7371356724578355
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.13372570943115306
    valeur_normalisee: 0.06686285471557653
    valeur_ponderee: 0.06686285471557653
    ts: '2026-08-07T05:23:14.663592+00:00'
  meteo_inde_gujarat_coton:
    ts: '2026-08-07T05:23:14.663592+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-06'
    valeur: 0.7299812424277818
    valeur_normalisee: 0.3649906212138909
    valeur_ponderee: 0.3649906212138909
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 98453.0
    valeur_normalisee: 0.7538273781947771
    valeur_ponderee: 0.7538273781947771
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_coton:
    valeur: 0.03839195979899501
    valeur_normalisee: 0.40759786643240303
    valeur_ponderee: 0.40759786643240303
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_coton:
    valeur: 0.02724199642075975
    valeur_normalisee: 0.45068342776820064
    valeur_ponderee: 0.45068342776820064
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_coton:
    valeur: 0.02297029702970299
    valeur_normalisee: 0.48270142042019476
    valeur_ponderee: 0.48270142042019476
    ts: '2026-08-07T05:23:14.663592+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: structurel
    event_id: 1ca8cba3cf66
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 52.80000000000006
      7j: 52.80000000000006
      1m: 52.80000000000006
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Les news récentes (48h) sont majoritairement LONG, dominées
      par la demande IA et les importations chinoises records, malgré quelques signaux
      SHORT (PMI, offre chilienne). Le prix a déjà monté de +7.9% sur 20j, ce qui
      suggère que le marché a partiellement intégré ces nouvelles, mais la fraîcheur
      et l
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 27.33333333333329
      7j: 27.33333333333329
      1m: 27.33333333333329
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_copper_nets:
    valeur: 68497.0
    valeur_normalisee: 0.881260518302941
    valeur_ponderee: 0.881260518302941
    ts: '2026-08-07T05:23:14.663592+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 44.166666666666636
      7j: 44.166666666666636
      1m: 44.166666666666636
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.0015723419426044158
    valeur_normalisee: 0.5185407456340426
    valeur_ponderee: 0.5185407456340426
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.07896408180197145
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.035577270300216846
    valeur_normalisee: 0.5981635494287418
    valeur_ponderee: 0.5981635494287418
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.014983074842773059
    valeur_normalisee: 0.2884781621364794
    valeur_ponderee: 0.2884781621364794
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5096857384999995
    valeur_normalisee: -0.10692526681084696
    valeur_ponderee: -0.10692526681084696
    ts: '2026-08-07T05:23:14.663592+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.6599999999999997
    valeur_normalisee: 0.5573666873514449
    valeur_ponderee: 0.5573666873514449
    ts: '2026-08-07T05:23:14.663592+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  usd_jpy_proxy_risk:
    valeur: 158.37958
    valeur_normalisee: -0.8456584986201754
    valeur_ponderee: -0.8456584986201754
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_eur_nets:
    valeur: -100540.0
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.007360976334723324
    valeur_normalisee: 0.6777692613649028
    valeur_ponderee: 0.6777692613649028
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.0006504544508429966
    valeur_normalisee: -0.024595184837077712
    valeur_ponderee: -0.024595184837077712
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0008930739083687911
    valeur_normalisee: -0.10549434134070079
    valeur_ponderee: -0.10549434134070079
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.6806703918419534
    valeur_ponderee: 0.6806703918419534
    ts: '2026-08-07T05:23:14.663592+00:00'
  sox_trend_5j:
    valeur: 532.52002
    valeur_normalisee: -0.325177461330422
    valeur_ponderee: -0.325177461330422
    ts: '2026-08-07T05:23:14.663592+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16795633616577804
    valeur_normalisee: 0.35807630110200855
    valeur_ponderee: 0.35807630110200855
    ts: '2026-08-07T05:23:14.663592+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Les tarifs de Trump sur les semi-conducteurs et le solaire
      (high, 2026-08-07) dominent, renforcés par les menaces tarifaires et les propos
      hawkish de Cook. Malgré des données solides (ventes de semi-conducteurs, PMI
      services), le biais est négatif, mais le prix récent (+4.55% sur 5j) suggère
      un cert
    nature: ponctuel
    event_id: f4347dbbe9be
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 72.4333333333334
      7j: 72.4333333333334
      1m: 72.4333333333334
  flux_etf_qqq_5j:
    valeur: 0.04549781355420701
    valeur_normalisee: 0.5956115737106968
    valeur_ponderee: 0.5956115737106968
    ts: '2026-08-07T05:23:14.663592+00:00'
  spread_nasdaq_russell2000:
    valeur: 416.40002000000004
    valeur_normalisee: -0.18172839179953273
    valeur_ponderee: -0.18172839179953273
    ts: '2026-08-07T05:23:14.663592+00:00'
  rsi_14j_ixic:
    valeur: 53.8103272827635
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.011931768667800768
    valeur_normalisee: -0.26473470059716325
    valeur_ponderee: -0.26473470059716325
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.05797277617689045
    valeur_normalisee: 0.8560060861569115
    valeur_ponderee: 0.8560060861569115
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.020826507141020745
    valeur_normalisee: 0.38506491138548454
    valeur_ponderee: 0.38506491138548454
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-07T05:23:14.663592+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.6806703918419534
    valeur_ponderee: 0.6806703918419534
    ts: '2026-08-07T05:23:14.663592+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_nets:
    valeur: 174131.0
    valeur_normalisee: -0.20851213210640585
    valeur_ponderee: -0.20851213210640585
    ts: '2026-08-07T05:23:14.663592+00:00'
  flux_etf_or_5j:
    valeur: 0.0331689733799978
    valeur_normalisee: 0.6979839118412585
    valeur_ponderee: 0.6979839118412585
    ts: '2026-08-07T05:23:14.663592+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Les news du jour (07/08) sont majoritairement LONG avec plusieurs
      matérialités high (menaces iraniennes sur Ormuz, trafic quasi arrêté), et le
      prix est en hausse de +6.42% sur 20j, cohérent avec un biais haussier. Cependant,
      des news SHORT du 06/08 (accord Iran-Oman potentiel) et une matérialité moy
    nature: structurel
    event_id: 7e992cc7480a
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 250.53333333333273
      7j: 250.53333333333273
      1m: 250.53333333333273
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
    ts: '2026-08-07T05:23:14.663592+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_or:
    valeur: 0.06414023598332008
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_or:
    valeur: 0.05502720287043905
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_or:
    valeur: 0.04670984146334156
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-07T05:23:14.663592+00:00'
petrole:
  eia_crude_surprise:
    valeur: 406987.0
    valeur_normalisee: -0.6764819159441962
    valeur_ponderee: -0.6764819159441962
    ts: '2026-08-07T05:23:14.663592+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Les news du jour (07/08) montrent une escalade des tensions
      sur le détroit d'Ormuz avec menaces iraniennes d'interdiction des navires américains
      et israéliens, et un trafic proche de l'arrêt, signal LONG dominant malgré des
      signaux SHORT plus anciens (accord Iran-Oman). Le prix a déjà monté de +8.53
    nature: structurel
    event_id: 7e992cc7480a
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 229.63333333333307
      7j: 229.63333333333307
      1m: 229.63333333333307
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 32189.0
    valeur_normalisee: 0.13392206358519956
    valeur_ponderee: 0.13392206358519956
    ts: '2026-08-07T05:23:14.663592+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: structurel
    event_id: 7e992cc7480a
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 212.80000000000015
      7j: 212.80000000000015
      1m: 212.80000000000015
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  cushing_stocks:
    valeur: 20955.0
    valeur_normalisee: -0.41464832709950017
    valeur_ponderee: -0.41464832709950017
    ts: '2026-08-07T05:23:14.663592+00:00'
  spread_brent_wti:
    valeur: 4.216719999999995
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.08527289804050997
    valeur_normalisee: 0.41105495090132754
    valeur_ponderee: 0.41105495090132754
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.062009628462821764
    valeur_normalisee: -0.19696307486045156
    valeur_ponderee: -0.19696307486045156
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.052341992663049064
    valeur_normalisee: 0.515230858091682
    valeur_ponderee: 0.515230858091682
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-07T05:23:14.663592+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-07T05:23:14.663592+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.040000000000000036
    valeur_normalisee: -0.352240318487389
    valeur_ponderee: -0.352240318487389
    ts: '2026-08-07T05:23:14.663592+00:00'
  hy_credit_spread:
    valeur: 2.75
    valeur_normalisee: 0.0576881709797007
    valeur_ponderee: 0.0576881709797007
    ts: '2026-08-07T05:23:14.663592+00:00'
  breadth_sp_ma50:
    valeur: 0.2844019985427293
    valeur_normalisee: 0.13892238786884992
    valeur_ponderee: 0.13892238786884992
    ts: '2026-08-07T05:23:14.663592+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.03622807372352321
    valeur_normalisee: 0.8333184441637229
    valeur_ponderee: 0.8333184441637229
    ts: '2026-08-07T05:23:14.663592+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.12
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  rsi_14j_gspc:
    valeur: 63.060331525459105
    ts: '2026-08-07T05:23:14.663592+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.41
    valeur_normalisee: 0.6806703918419534
    valeur_ponderee: 0.6806703918419534
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.022415531989316895
    valeur_normalisee: 0.12814215199590723
    valeur_ponderee: 0.12814215199590723
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.03738899437665655
    valeur_normalisee: 0.8700761838033128
    valeur_ponderee: 0.8700761838033128
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.014373038773424662
    valeur_normalisee: 0.4138426288189522
    valeur_ponderee: 0.4138426288189522
    ts: '2026-08-07T05:23:14.663592+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-07T05:23:14.663592+00:00'
sucre:
  meteo_bresil_canne_sucre:
    valeur: -0.1788555367913411
    valeur_normalisee: 0.08942776839567056
    valeur_ponderee: 0.08942776839567056
    ts: '2026-08-07T05:23:14.663592+00:00'
  brent_ethanol_proxy_sucre:
    valeur: 82.52126
    valeur_normalisee: -0.17586151576780526
    valeur_ponderee: -0.17586151576780526
    ts: '2026-08-07T05:23:14.663592+00:00'
  usd_brl_sucre:
    valeur: 5.11897
    valeur_normalisee: -0.0812371711874568
    valeur_ponderee: -0.0812371711874568
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_sugar:
    valeur: -81679.0
    valeur_normalisee: -0.5608615387476262
    valeur_ponderee: -0.5608615387476262
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.02306920762286846
    valeur_normalisee: 0.16940108944242502
    valeur_ponderee: 0.16940108944242502
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.06583072100313458
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.03658536585365857
    valeur_normalisee: 0.7916398016641182
    valeur_ponderee: 0.7916398016641182
    ts: '2026-08-07T05:23:14.663592+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: structurel
    event_id: f7793f92754c
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 39.69999999999999
      7j: 39.69999999999999
      1m: 39.69999999999999
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
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: structurel
    event_id: f7793f92754c
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 39.69999999999999
      7j: 39.69999999999999
      1m: 39.69999999999999
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5099999999999998
    valeur_normalisee: 0.19932900932996084
    valeur_ponderee: 0.19932900932996084
    ts: '2026-08-07T05:23:14.663592+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.005860426350001946
    valeur_normalisee: 0.2852462985900036
    valeur_ponderee: 0.2852462985900036
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.004113094568271691
    valeur_normalisee: 0.27424569912113095
    valeur_ponderee: 0.27424569912113095
    ts: '2026-08-07T05:23:14.663592+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.024883072676685103
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_jpy_nets:
    valeur: -171320.0
    valeur_normalisee: -0.7719946476652498
    valeur_ponderee: -0.7719946476652498
    ts: '2026-08-07T05:23:14.663592+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.96
    valeur_normalisee: 0.49273798642990607
    valeur_ponderee: 0.49273798642990607
    ts: '2026-08-07T05:23:14.663592+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-07T05:23:14.663592+00:00'
    nature: ponctuel
    event_id: 0e9321aabc2d
    event_date: '2026-08-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 7.700000000000011
      7j: 7.700000000000011
      1m: 7.700000000000011
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-07T05:23:14.663592+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-07T05:23:14.663592+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-07T05:23:14.663592+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-07T05:23:14.663592+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-07T05:23:14.663592+00:00'
  gap_rv_iv:
    valeur: -1.004367773020146
    ts: '2026-08-07T05:23:14.663592+00:00'
  cftc_cot_vix_nets:
    valeur: -63413.0
    valeur_normalisee: -0.21963090052659925
    valeur_ponderee: -0.21963090052659925
    ts: '2026-08-07T05:23:14.663592+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-07T05:23:14.663592+00:00'
    synthese_rationale: Dominance de news LONG fraîches (48h) sur tensions Ormuz et
      guerre Iran, malgré quelques signaux SHORT d'accord. Le prix VIX en baisse contredit
      ce biais, donc conviction réduite à medium.
    nature: structurel
    event_id: 7e992cc7480a
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 273.2666666666661
      7j: 273.2666666666661
      1m: 273.2666666666661
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-07T05:23:14.663592+00:00'
```
