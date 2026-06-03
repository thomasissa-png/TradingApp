# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-03T15:06:00.417996+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T15:06:00.417996+00:00'
  mouvement_or_5j:
    valeur: -0.019056892776091905
    valeur_normalisee: -0.434811218812146
    valeur_ponderee: -0.434811218812146
    ts: '2026-06-03T15:06:00.417996+00:00'
  ratio_gold_silver:
    valeur: 60.28940298950071
    ts: '2026-06-03T15:06:00.417996+00:00'
  alpha_argent_vs_or_5j:
    valeur: -8.543896234591841e-05
    valeur_normalisee: -0.07776377661524383
    valeur_ponderee: -0.07776377661524383
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-03T15:06:00.417996+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.01140740740740731
    valeur_normalisee: -0.0037908708914586764
    valeur_ponderee: -0.0037908708914586764
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T15:06:00.417996+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-03T15:06:00.417996+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21681542249907854
    valeur_normalisee: 0.10840771124953927
    valeur_ponderee: 0.10840771124953927
    ts: '2026-06-03T15:06:00.417996+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (Chine lève interdiction
      Brésil, baisse production Australie) vs SHORT (Euronext à 3 semaines bas, pression
      vente). Prix -10% sur 20j suggère que le marché a déjà intégré les éléments
      baissiers, sans signal frais dominant.'
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-03T15:06:00.417996+00:00'
  meteo_australie_dryland:
    valeur: -0.03979471650292972
    valeur_normalisee: -0.01989735825146486
    valeur_ponderee: -0.01989735825146486
    ts: '2026-06-03T15:06:00.417996+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T15:06:00.417996+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6785842105
    valeur_normalisee: 0.28629604490204547
    valeur_ponderee: 0.28629604490204547
    ts: '2026-06-03T15:06:00.417996+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.01194814989963544
    valeur_normalisee: -0.07107503312528235
    valeur_ponderee: -0.07107503312528235
    ts: '2026-06-03T15:06:00.417996+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.004999999999999893
    valeur_normalisee: -0.04224920207228074
    valeur_ponderee: -0.04224920207228074
    ts: '2026-06-03T15:06:00.417996+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-03T15:06:00.417996+00:00'
  rsi_14j_fchi:
    valeur: 53.69399394807396
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T15:06:00.417996+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-03T15:06:00.417996+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Majorité de news SHORT récentes (dollar fort, abondance offre)
      dominent, malgré une news LONG Chine/Brésil de matérialité high mais isolée.
      Le prix -4.17% sur 20j confirme le biais baissier, mais le rebond récent (+3.68%
      sur 5j) et la news LONG récente limitent la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.63'
    p2_shadow_contrib_exclu:
      24h: -10.4
      7j: -10.4
      1m: -10.4
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Majorité de news SHORT récentes (dollar fort, abondance offre)
      dominent, malgré une news LONG Chine/Brésil de matérialité high mais isolée.
      Le prix -4.17% sur 20j confirme le biais baissier, mais le rebond récent (+3.68%
      sur 5j) et la news LONG récente limitent la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.63'
    p2_shadow_contrib_exclu:
      24h: -10.4
      7j: -10.4
      1m: -10.4
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T15:06:00.417996+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.29223724434408876
    valeur_normalisee: -0.14611862217204438
    valeur_ponderee: -0.14611862217204438
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-03T15:06:00.417996+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Deux news SHORT high du 2 juin (tarifs US sur Brésil) contredisent
      les news LONG plus anciennes sur les récoltes et prix, et le prix a déjà baissé
      de 7% en 20j. Signal trop équilibré et déjà pricé.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 37.96666666666667
      7j: 37.96666666666667
      1m: 37.96666666666667
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-03T15:06:00.417996+00:00'
  meteo_vietnam_robusta:
    valeur: -0.19898874237162403
    valeur_normalisee: -0.09949437118581202
    valeur_ponderee: -0.09949437118581202
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T15:06:00.417996+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Dominance des PMI chinois et sud-coréens solides (1er juin)
      et de la proclamation Trump sur les droits de douane cuivre (2 juin, high matérialité)
      face à des signaux short dispersés (PIB Australie, tarifs Brésil, données officielles
      Chine faibles). Le prix récent (+2.48% sur 5j) confirme le biais ha
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.63'
    p2_shadow_contrib_exclu:
      24h: -1.3666666666666667
      7j: -1.3666666666666667
      1m: -1.3666666666666667
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T15:06:00.417996+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Dominance des PMI chinois et sud-coréens solides (1er juin)
      et de la proclamation Trump sur les droits de douane cuivre (2 juin, high matérialité)
      face à des signaux short dispersés (PIB Australie, tarifs Brésil, données officielles
      Chine faibles). Le prix récent (+2.48% sur 5j) confirme le biais ha
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.63'
    p2_shadow_contrib_exclu:
      24h: 5.1000000000000005
      7j: 5.1000000000000005
      1m: 5.1000000000000005
  ratio_cuivre_or:
    valeur: 0.0014617782486604104
    valeur_normalisee: 0.9307195966282786
    valeur_ponderee: 0.9307195966282786
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4722809443
    valeur_normalisee: 0.8801140282055967
    valeur_ponderee: 0.8801140282055967
    ts: '2026-06-03T15:06:00.417996+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4736842104999996
    valeur_normalisee: 0.38479878420450014
    valeur_ponderee: 0.38479878420450014
    ts: '2026-06-03T15:06:00.417996+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T15:06:00.417996+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.99005
    valeur_normalisee: 0.6234112123958566
    valeur_ponderee: 0.6234112123958566
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T15:06:00.417996+00:00'
  sox_trend_5j:
    valeur: 614.99
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T15:06:00.417996+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16313968458319925
    valeur_normalisee: -0.2542333650046265
    valeur_ponderee: -0.2542333650046265
    ts: '2026-06-03T15:06:00.417996+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Les news LONG (ISM services solide, investissements IA massifs)
      sont contrebalancées par des news SHORT (droits de douane, resserrement réglementaire,
      vente d'actions Alphabet). Le marché a déjà intégré une hausse de 9.45% sur
      20j, ce qui affaiblit le signal directionnel net.
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 5.333333333333333
      7j: 5.333333333333333
      1m: 5.333333333333333
  flux_etf_qqq_5j:
    valeur: 0.02224962612585335
    valeur_normalisee: 0.11985225049267596
    valeur_ponderee: 0.11985225049267596
    ts: '2026-06-03T15:06:00.417996+00:00'
  spread_nasdaq_russell2000:
    valeur: 456.92499999999995
    valeur_normalisee: 0.8939292070526892
    valeur_ponderee: 0.8939292070526892
    ts: '2026-06-03T15:06:00.417996+00:00'
  rsi_14j_ixic:
    valeur: 79.09552411891094
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T15:06:00.417996+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-03T15:06:00.417996+00:00'
  flux_etf_or_5j:
    valeur: -0.00012237753977761834
    valeur_normalisee: 0.13917187505687453
    valeur_ponderee: 0.13917187505687453
    ts: '2026-06-03T15:06:00.417996+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (3 juin) sur escalade Iran-États-Unis, fermeture d''Ormuz, et frappes au Koweït.
      Malgré la baisse récente de -4.23% sur 20j, la concentration et la force des
      news LONG récentes dominent, indiquant un changement de régime haussier pour '
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.63'
    p2_shadow_contrib_exclu:
      24h: 26.833333333333336
      7j: 26.833333333333336
      1m: 26.833333333333336
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-03T15:06:00.417996+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
petrole:
  eia_crude_surprise:
    valeur: 441686.0
    valeur_normalisee: 0.37013572651064536
    valeur_ponderee: 0.37013572651064536
    ts: '2026-06-03T15:06:00.417996+00:00'
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-03T15:06:00.417996+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Multiples news high matérialité confirmant escalade Iran-US
      et fermeture Ormuz dominent, malgré quelques signaux short (demande Inde, subventions
      Japon) et une baisse de -8.48% sur 20j. La fraîcheur et la force des news géopolitiques
      justifient un biais long malgré le contexte de prix.
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.63'
    p2_shadow_contrib_exclu:
      24h: 30.300000000000004
      7j: 30.300000000000004
      1m: 30.300000000000004
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-03T15:06:00.417996+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Multiples news high matérialité confirmant escalade Iran-US
      et fermeture Ormuz dominent, malgré quelques signaux short (demande Inde, subventions
      Japon) et une baisse de -8.48% sur 20j. La fraîcheur et la force des news géopolitiques
      justifient un biais long malgré le contexte de prix.
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.63'
    p2_shadow_contrib_exclu:
      24h: 31.8
      7j: 31.8
      1m: 31.8
    sign_conflict: true
    sign_conflict_details:
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
    - event_id: ef3e2bf5d814
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: hausse
      surprise_polarity: up
      title: EIA publie son STEO de mai avec révision à la hausse des prix pétrole
        due aux perturbations Moyen-Orient
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T15:06:00.417996+00:00'
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-03T15:06:00.417996+00:00'
  spread_brent_wti:
    valeur: 2.059430000000006
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-03T15:06:00.417996+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.08999999999999986
    valeur_normalisee: -0.683479598983062
    valeur_ponderee: -0.683479598983062
    ts: '2026-06-03T15:06:00.417996+00:00'
  hy_credit_spread:
    valeur: 2.71
    valeur_normalisee: -0.5586257164931435
    valeur_ponderee: -0.5586257164931435
    ts: '2026-06-03T15:06:00.417996+00:00'
  breadth_sp_ma50:
    valeur: 0.2772979193396913
    valeur_normalisee: -0.4978847495255331
    valeur_ponderee: -0.4978847495255331
    ts: '2026-06-03T15:06:00.417996+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T15:06:00.417996+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.007395437267930571
    valeur_normalisee: -0.00367793065870295
    valeur_ponderee: -0.00367793065870295
    ts: '2026-06-03T15:06:00.417996+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.84
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T15:06:00.417996+00:00'
  rsi_14j_gspc:
    valeur: 70.96194665943648
    ts: '2026-06-03T15:06:00.417996+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T15:06:00.417996+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-03T15:06:00.417996+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-03T15:06:00.417996+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-03T15:06:00.417996+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-03T15:06:00.417996+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-03T15:06:00.417996+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T15:06:00.417996+00:00'
    synthese_rationale: Majorité de news LONG matérialité élevée (escalade Iran-US,
      fermeture Ormuz) mais prix VIX en baisse de 15% sur 20j suggère que le marché
      a déjà intégré ces tensions. Une seule news SHORT faible (cessez-le-feu Liban)
      ne contrebalance pas, mais le contexte de prix impose une conviction basse.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 25.266666666666666
      7j: 25.266666666666666
      1m: 25.266666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-03T15:06:00.417996+00:00'
```
