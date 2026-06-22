# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-22T07:44:58.604894+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.23
    valeur_normalisee: 0.9901009175952068
    valeur_ponderee: 0.9901009175952068
    ts: '2026-06-22T07:44:58.604894+00:00'
  mouvement_or_5j:
    valeur: -0.015023201880396186
    valeur_normalisee: -0.09785968941807696
    valeur_ponderee: -0.09785968941807696
    ts: '2026-06-22T07:44:58.604894+00:00'
  ratio_gold_silver:
    valeur: 63.19674377514566
    ts: '2026-06-22T07:44:58.604894+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  cftc_cot_silver:
    valeur: 21439.0
    valeur_normalisee: -0.2761544121303307
    valeur_ponderee: -0.2761544121303307
    ts: '2026-06-22T07:44:58.604894+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.021538967444919455
    valeur_normalisee: -0.06576654189326524
    valeur_ponderee: -0.06576654189326524
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_argent:
    valeur: -0.1166415448675332
    valeur_normalisee: -0.516277685567832
    valeur_ponderee: -0.516277685567832
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.3920169968999874
    valeur_normalisee: 0.1960084984499937
    valeur_ponderee: 0.1960084984499937
    ts: '2026-06-22T07:44:58.604894+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: Multiples confirmations USDA d'exportations ukrainiennes élevées
      et récolte record Mer Noire dominent le flux SHORT, malgré une news LONG récente
      sur le conflit russo-ukrainien. Le prix en baisse confirme le biais baissier.
    nature: structurel
    event_id: 49df59e55c60
    event_date: '2026-06-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.32'
    p2_shadow_contrib_exclu:
      24h: -4.3
      7j: -4.3
      1m: -4.3
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -67881.0
    valeur_normalisee: -0.3345346843914137
    valeur_ponderee: -0.3345346843914137
    ts: '2026-06-22T07:44:58.604894+00:00'
  meteo_australie_dryland:
    valeur: 0.08835903226995234
    valeur_normalisee: 0.04417951613497617
    valeur_ponderee: 0.04417951613497617
    ts: '2026-06-22T07:44:58.604894+00:00'
  dxy_trend_20j:
    valeur: 119.5073
    valeur_normalisee: 0.15537082863485205
    valeur_ponderee: 0.15537082863485205
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_ble:
    valeur: -0.011532817979660104
    valeur_normalisee: -0.11633734624172874
    valeur_ponderee: -0.11633734624172874
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-22T07:44:58.604894+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-06-22T07:44:58.604894+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.02040787803749633
    valeur_normalisee: 0.6025114046476586
    valeur_ponderee: 0.6025114046476586
    ts: '2026-06-22T07:44:58.604894+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.01568543188654914
    valeur_normalisee: -0.41892859291858897
    valeur_ponderee: -0.41892859291858897
    ts: '2026-06-22T07:44:58.604894+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-22T07:44:58.604894+00:00'
  rsi_14j_fchi:
    valeur: 61.41848363303224
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.019489601257723477
    valeur_normalisee: 0.10901960626140009
    valeur_ponderee: 0.10901960626140009
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -29350.0
    valeur_normalisee: -0.8736520422725818
    valeur_ponderee: -0.8736520422725818
    ts: '2026-06-22T07:44:58.604894+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-22T07:44:58.604894+00:00'
    nature: structurel
    event_id: 45bb3b93b62d
    event_date: '2026-06-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.32'
    p2_shadow_contrib_exclu:
      24h: -15.900000000000025
      7j: -15.900000000000025
      1m: -15.900000000000025
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
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (cartel cacao,
      El Niño) et fraîcheur récente, malgré une news SHORT isolée. Le prix (+9.12%
      sur 20j) confirme le biais haussier.
    nature: structurel
    event_id: 45bb3b93b62d
    event_date: '2026-06-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.32'
    p2_shadow_contrib_exclu:
      24h: -15.900000000000025
      7j: -15.900000000000025
      1m: -15.900000000000025
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.09121039930996955
    valeur_normalisee: 0.08234208311405056
    valeur_ponderee: 0.08234208311405056
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-22T07:44:58.604894+00:00'
  meteo_ci_ghana_precip_30j:
    valeur: 1.0255825525612192
    valeur_normalisee: 0.5127912762806096
    valeur_ponderee: 0.5127912762806096
    ts: '2026-06-22T07:44:58.604894+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.33511553616340856
    valeur_normalisee: 0.16755776808170428
    valeur_ponderee: 0.16755776808170428
    ts: '2026-06-22T07:44:58.604894+00:00'
  usd_brl:
    valeur: 5.15367
    valeur_normalisee: 0.7117253617293052
    valeur_ponderee: 0.7117253617293052
    ts: '2026-06-22T07:44:58.604894+00:00'
  cftc_cot_coffee:
    valeur: 1316.0
    valeur_normalisee: -0.6884038422015029
    valeur_ponderee: -0.6884038422015029
    ts: '2026-06-22T07:44:58.604894+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: 'Signaux contradictoires : news récentes SHORT (ver à vis,
      indice en baisse) s''opposent aux news LONG plus anciennes (El Niño, hausse
      arabica). Le prix a baissé de 2.44% sur 5j, suggérant que le marché intègre
      déjà les risques SHORT. Pas de signal dominant clair.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 49.96666666666667
      7j: 49.96666666666667
      1m: 49.96666666666667
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-22T07:44:58.604894+00:00'
  meteo_vietnam_robusta:
    valeur: -0.010035332975601857
    valeur_normalisee: 0.005017666487800929
    valeur_ponderee: 0.005017666487800929
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.021953936113348727
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-22T07:44:58.604894+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité high le 22 juin (restrictions
      chinoises) et le 16 juin (ventes au détail chinoises en baisse), malgré quelques
      signaux LONG plus anciens. Le prix a déjà baissé de 2.69% sur 20j, confirmant
      le biais baissier.
    nature: structurel
    event_id: 189e61c692f2
    event_date: '2026-06-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.32'
    p2_shadow_contrib_exclu:
      24h: 4.966666666666667
      7j: 4.966666666666667
      1m: 4.966666666666667
  dxy_trend_20j:
    valeur: 119.5073
    valeur_normalisee: 0.15537082863485205
    valeur_ponderee: 0.15537082863485205
    ts: '2026-06-22T07:44:58.604894+00:00'
  cftc_cot_copper_nets:
    valeur: 75588.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-22T07:44:58.604894+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-06-22T07:44:58.604894+00:00'
    nature: ponctuel
    event_id: 8bc646c10317
    event_date: '2026-06-16T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.32'
    p2_shadow_contrib_exclu:
      24h: 18.5
      7j: 18.5
      1m: 18.5
  ratio_cuivre_or:
    valeur: 0.001518722802781655
    valeur_normalisee: 0.7328202196624232
    valeur_ponderee: 0.7328202196624232
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.026908775371152882
    valeur_normalisee: -0.8039873737624303
    valeur_ponderee: -0.8039873737624303
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6732508345000001
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-22T07:44:58.604894+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4435000000000002
    valeur_normalisee: 0.27480643507605923
    valeur_ponderee: 0.27480643507605923
    ts: '2026-06-22T07:44:58.604894+00:00'
  dxy_trend_20j:
    valeur: 119.5073
    valeur_normalisee: 0.15537082863485205
    valeur_ponderee: 0.15537082863485205
    ts: '2026-06-22T07:44:58.604894+00:00'
  usd_jpy_proxy_risk:
    valeur: 161.77036
    valeur_normalisee: 0.9401421096736055
    valeur_ponderee: 0.9401421096736055
    ts: '2026-06-22T07:44:58.604894+00:00'
  cftc_cot_eur_nets:
    valeur: -18345.0
    valeur_normalisee: -0.5514666177749327
    valeur_ponderee: -0.5514666177749327
    ts: '2026-06-22T07:44:58.604894+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.016007840574975618
    valeur_normalisee: -0.7646336330345761
    valeur_ponderee: -0.7646336330345761
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.23
    valeur_normalisee: 0.9901009175952068
    valeur_ponderee: 0.9901009175952068
    ts: '2026-06-22T07:44:58.604894+00:00'
  sox_trend_5j:
    valeur: 639.45001
    valeur_normalisee: 0.8756434133289228
    valeur_ponderee: 0.8756434133289228
    ts: '2026-06-22T07:44:58.604894+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16429478004914802
    valeur_normalisee: -0.005909929769678052
    valeur_ponderee: -0.005909929769678052
    ts: '2026-06-22T07:44:58.604894+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: 'Multiples news SHORT high matérialité dominent : restrictions
      chinoises sur entreprises US, position hawkish Fed, demande militaire massive,
      et doutes sur la paix Iran. Le rally récent (+3.85% sur 20j) est contredit par
      ces signaux frais et forts, justifiant une conviction haute malgré le contexte
      h'
    nature: ponctuel
    event_id: 2ff74090d637
    event_date: '2026-06-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.32'
    p2_shadow_contrib_exclu:
      24h: 16.633333333333333
      7j: 16.633333333333333
      1m: 16.633333333333333
  flux_etf_qqq_5j:
    valeur: 0.03276996876394467
    valeur_normalisee: 0.26526227901616767
    valeur_ponderee: 0.26526227901616767
    ts: '2026-06-22T07:44:58.604894+00:00'
  spread_nasdaq_russell2000:
    valeur: 445.03000000000003
    valeur_normalisee: 0.5629526914374172
    valeur_ponderee: 0.5629526914374172
    ts: '2026-06-22T07:44:58.604894+00:00'
  rsi_14j_ixic:
    valeur: 59.52255216716162
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.03851921647565826
    valeur_normalisee: -0.20876572925212283
    valeur_ponderee: -0.20876572925212283
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.23
    valeur_normalisee: 0.9901009175952068
    valeur_ponderee: 0.9901009175952068
    ts: '2026-06-22T07:44:58.604894+00:00'
  dxy_trend_20j:
    valeur: 119.5073
    valeur_normalisee: 0.15537082863485205
    valeur_ponderee: 0.15537082863485205
    ts: '2026-06-22T07:44:58.604894+00:00'
  cftc_cot_nets:
    valeur: 165904.0
    valeur_normalisee: -0.28823309737285147
    valeur_ponderee: -0.28823309737285147
    ts: '2026-06-22T07:44:58.604894+00:00'
  flux_etf_or_5j:
    valeur: 0.002070796177500611
    valeur_normalisee: 0.1768983062584739
    valeur_ponderee: 0.1768983062584739
    ts: '2026-06-22T07:44:58.604894+00:00'
  tension_geopolitique:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: Multiples news high matérialité confirment un accord de paix
      US-Iran et une position hawkish de la Fed, dominant les signaux longs liés aux
      tensions sur Ormuz. Le prix a déjà baissé de 6.6% sur 20j, mais la concentration
      de news SHORT fraîches et de haute matérialité renforce le bais baissier.
    nature: structurel
    event_id: 5c6e59502f2d
    event_date: '2026-06-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.32'
    p2_shadow_contrib_exclu:
      24h: 58.19999999999999
      7j: 58.19999999999999
      1m: 58.19999999999999
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-22T07:44:58.604894+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_or:
    valeur: -0.06562485983464239
    valeur_normalisee: -0.5908049466432149
    valeur_ponderee: -0.5908049466432149
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: Multiples news confirmées de matérialité high (accord de roadmap
      US-Iran, accord de paix signé) et nombreuses news SHORT dominent, malgré quelques
      tensions LONG sur Ormuz. Le prix a déjà baissé de 18.91% sur 20j, mais la fraîcheur
      et la matérialité des news SHORT du jour justifient un biais baissier
    nature: structurel
    event_id: 5c6e59502f2d
    event_date: '2026-06-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.32'
    p2_shadow_contrib_exclu:
      24h: 49.999999999999986
      7j: 49.999999999999986
      1m: 49.999999999999986
  cftc_cot_crude_nets:
    valeur: 42102.0
    valeur_normalisee: 0.35966847625640336
    valeur_ponderee: 0.35966847625640336
    ts: '2026-06-22T07:44:58.604894+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-06-22T07:44:58.604894+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 51.19999999999996
      7j: 51.19999999999996
      1m: 51.19999999999996
    sign_conflict: true
    sign_conflict_details:
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
    - event_id: a064c322c763
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: oil stocks
      matched_surprise: hausse
      surprise_polarity: up
      title: Avertissement des dirigeants pétroliers sur des stocks très bas et hausse
        imminente des prix
  dxy_trend_20j:
    valeur: 119.5073
    valeur_normalisee: 0.15537082863485205
    valeur_ponderee: 0.15537082863485205
    ts: '2026-06-22T07:44:58.604894+00:00'
  cushing_stocks:
    valeur: 20034.0
    valeur_normalisee: -0.7252271143164453
    valeur_ponderee: -0.7252271143164453
    ts: '2026-06-22T07:44:58.604894+00:00'
  spread_brent_wti:
    valeur: 3.6702999999999975
    ts: '2026-06-22T07:44:58.604894+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-22T07:44:58.604894+00:00'
    note: hors fenêtre
  momentum_prix_20j_petrole:
    valeur: -0.18912661608219616
    valeur_normalisee: -0.6338352442445119
    valeur_ponderee: -0.6338352442445119
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-22T07:44:58.604894+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.05999999999999961
    valeur_normalisee: -0.4194937537867631
    valeur_ponderee: -0.4194937537867631
    ts: '2026-06-22T07:44:58.604894+00:00'
  hy_credit_spread:
    valeur: 2.63
    valeur_normalisee: -0.6595300681164844
    valeur_ponderee: -0.6595300681164844
    ts: '2026-06-22T07:44:58.604894+00:00'
  breadth_sp_ma50:
    valeur: 0.2811688309340444
    valeur_normalisee: -0.14340240771639978
    valeur_ponderee: -0.14340240771639978
    ts: '2026-06-22T07:44:58.604894+00:00'
  dxy_trend_20j:
    valeur: 119.5073
    valeur_normalisee: 0.15537082863485205
    valeur_ponderee: 0.15537082863485205
    ts: '2026-06-22T07:44:58.604894+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.012171952773639916
    valeur_normalisee: 0.07913098737306169
    valeur_ponderee: 0.07913098737306169
    ts: '2026-06-22T07:44:58.604894+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.71
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-22T07:44:58.604894+00:00'
  rsi_14j_gspc:
    valeur: 54.57926975672146
    ts: '2026-06-22T07:44:58.604894+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.23
    valeur_normalisee: 0.9901009175952068
    valeur_ponderee: 0.9901009175952068
    ts: '2026-06-22T07:44:58.604894+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.007406394603709954
    valeur_normalisee: -0.2968549714076329
    valeur_ponderee: -0.2968549714076329
    ts: '2026-06-22T07:44:58.604894+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-22T07:44:58.604894+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-22T07:44:58.604894+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-22T07:44:58.604894+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-22T07:44:58.604894+00:00'
  gap_rv_iv:
    valeur: 0.8419853538287505
    ts: '2026-06-22T07:44:58.604894+00:00'
  cftc_cot_vix_nets:
    valeur: -74420.0
    valeur_normalisee: -0.4200243704620096
    valeur_ponderee: -0.4200243704620096
    ts: '2026-06-22T07:44:58.604894+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-22T07:44:58.604894+00:00'
    synthese_rationale: 'Signaux contradictoires : news SHORT (accord US-Iran, apaisement)
      et LONG (fermeture Ormuz, tensions) se neutralisent. Le prix a baissé de 15.83%
      sur 20j, suggérant que le marché a déjà pricé l''apaisement, mais la fraîcheur
      des news ne permet pas de trancher.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 52.39999999999999
      7j: 52.39999999999999
      1m: 52.39999999999999
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-22T07:44:58.604894+00:00'
```
