# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-03T20:01:09.026107+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T20:01:09.026107+00:00'
  mouvement_or_5j:
    valeur: -0.02096301155419311
    valeur_normalisee: -0.475720581664657
    valeur_ponderee: -0.475720581664657
    ts: '2026-06-03T20:01:09.026107+00:00'
  ratio_gold_silver:
    valeur: 60.707620180842845
    ts: '2026-06-03T20:01:09.026107+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.006556040996608115
    valeur_normalisee: -0.16000125814155972
    valeur_ponderee: -0.16000125814155972
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-03T20:01:09.026107+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.01896296296296296
    valeur_normalisee: -0.05246246995140854
    valeur_ponderee: -0.05246246995140854
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T20:01:09.026107+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-03T20:01:09.026107+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21681542249907854
    valeur_normalisee: 0.10840771124953927
    valeur_ponderee: 0.10840771124953927
    ts: '2026-06-03T20:01:09.026107+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: 'Signaux contradictoires : baisse production australienne
      (LONG high) vs fonds réduisent positions longues et pression vendeuse (SHORT).
      Prix en baisse de 10.91% sur 20j suggère que le marché a déjà intégré les éléments
      baissiers, sans nouvelle fraîche dominante pour inverser la tendance.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-03T20:01:09.026107+00:00'
  meteo_australie_dryland:
    valeur: -0.03979471650292972
    valeur_normalisee: -0.01989735825146486
    valeur_ponderee: -0.01989735825146486
    ts: '2026-06-03T20:01:09.026107+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T20:01:09.026107+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6785842105
    valeur_normalisee: 0.28629604490204547
    valeur_ponderee: 0.28629604490204547
    ts: '2026-06-03T20:01:09.026107+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.011932049519957966
    valeur_normalisee: -0.07065903339721107
    valeur_ponderee: -0.07065903339721107
    ts: '2026-06-03T20:01:09.026107+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.010108695652173982
    valeur_normalisee: -0.12409176963065256
    valeur_ponderee: -0.12409176963065256
    ts: '2026-06-03T20:01:09.026107+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-03T20:01:09.026107+00:00'
  rsi_14j_fchi:
    valeur: 52.46575810668952
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T20:01:09.026107+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-03T20:01:09.026107+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Majorité de news SHORT récentes (abondance offre, force dollar,
      stocks ICE) dominent, malgré une news LONG Chine/Brésil de matérialité high
      mais isolée. Le prix -4.41% sur 20j confirme le biais baissier, mais le rebond
      récent (+3.43% sur 5j) et la news LONG réduisent la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.83'
    p2_shadow_contrib_exclu:
      24h: -9.933333333333332
      7j: -9.933333333333332
      1m: -9.933333333333332
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Majorité de news SHORT récentes (abondance offre, force dollar,
      stocks ICE) dominent, malgré une news LONG Chine/Brésil de matérialité high
      mais isolée. Le prix -4.41% sur 20j confirme le biais baissier, mais le rebond
      récent (+3.43% sur 5j) et la news LONG réduisent la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.83'
    p2_shadow_contrib_exclu:
      24h: -9.933333333333332
      7j: -9.933333333333332
      1m: -9.933333333333332
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T20:01:09.026107+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.29223724434408876
    valeur_normalisee: -0.14611862217204438
    valeur_ponderee: -0.14611862217204438
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-03T20:01:09.026107+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Tarif Trump sur Brésil (SHORT) et levée interdiction Chine
      (LONG) le même jour s'annulent ; baisse prix -8% sur 20j suggère marché déjà
      pricé. Pas de signal dominant.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 38.43333333333333
      7j: 38.43333333333333
      1m: 38.43333333333333
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-03T20:01:09.026107+00:00'
  meteo_vietnam_robusta:
    valeur: -0.19898874237162403
    valeur_normalisee: -0.09949437118581202
    valeur_ponderee: -0.09949437118581202
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T20:01:09.026107+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Goldman Sachs relève son objectif cuivre de +10% à 13 735
      $/t, citant des perturbations d'approvisionnement majeures, et Trump signe une
      proclamation modifiant les droits de douane sur le cuivre, renforçant les perspectives
      haussières malgré des données chinoises mitigées et des risques tarifaires b
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 0.06666666666666654
      7j: 0.06666666666666654
      1m: 0.06666666666666654
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T20:01:09.026107+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Goldman Sachs relève son objectif cuivre de +10% à 13 735
      $/t, citant des perturbations d'approvisionnement majeures, et Trump signe une
      proclamation modifiant les droits de douane sur le cuivre, renforçant les perspectives
      haussières malgré des données chinoises mitigées et des risques tarifaires b
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 7.533333333333334
      7j: 7.533333333333334
      1m: 7.533333333333334
  ratio_cuivre_or:
    valeur: 0.0014548958779584916
    valeur_normalisee: 0.8879562707597872
    valeur_ponderee: 0.8879562707597872
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4722809443
    valeur_normalisee: 0.8801140282055967
    valeur_ponderee: 0.8801140282055967
    ts: '2026-06-03T20:01:09.026107+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4736842104999996
    valeur_normalisee: 0.38479878420450014
    valeur_ponderee: 0.38479878420450014
    ts: '2026-06-03T20:01:09.026107+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T20:01:09.026107+00:00'
  usd_jpy_proxy_risk:
    valeur: 160.07856
    valeur_normalisee: 0.665084882334267
    valeur_ponderee: 0.665084882334267
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T20:01:09.026107+00:00'
  sox_trend_5j:
    valeur: 615.68
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T20:01:09.026107+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16343518219929057
    valeur_normalisee: -0.21539908870515345
    valeur_ponderee: -0.21539908870515345
    ts: '2026-06-03T20:01:09.026107+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Les ISM services solides et les investissements IA massifs
      (Alphabet, HPE, Anthropic) dominent, mais les risques de droits de douane et
      de resserrement réglementaire limitent la conviction.
    nature: ponctuel
    event_id: 2535780fbc6f
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 6.333333333333333
      7j: 6.333333333333333
      1m: 6.333333333333333
  flux_etf_qqq_5j:
    valeur: 0.020275536085056833
    valeur_normalisee: 0.08506268961744692
    valeur_ponderee: 0.08506268961744692
    ts: '2026-06-03T20:01:09.026107+00:00'
  spread_nasdaq_russell2000:
    valeur: 456.57
    valeur_normalisee: 0.8899442943979667
    valeur_ponderee: 0.8899442943979667
    ts: '2026-06-03T20:01:09.026107+00:00'
  rsi_14j_ixic:
    valeur: 77.5988986358669
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T20:01:09.026107+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-03T20:01:09.026107+00:00'
  flux_etf_or_5j:
    valeur: -0.0014443193577399205
    valeur_normalisee: 0.12227792018453655
    valeur_ponderee: 0.12227792018453655
    ts: '2026-06-03T20:01:09.026107+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (3 juin) dominent, malgré quelques news SHORT et une baisse récente du prix.
      L''escalade militaire Iran-États-Unis, fermeture d''Ormuz et frappes sur Koweït
      créent un choc géopolitique majeur non encore pleinement pricé, justifiant une '
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 31.833333333333332
      7j: 31.833333333333332
      1m: 31.833333333333332
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-03T20:01:09.026107+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
petrole:
  eia_crude_surprise:
    valeur: 433712.0
    valeur_normalisee: 0.10010806760573361
    valeur_ponderee: 0.10010806760573361
    ts: '2026-06-03T20:01:09.026107+00:00'
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-03T20:01:09.026107+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Multiples news high matérialité confirmant escalade Iran-US,
      fermeture Ormuz, frappes sur Koweït dominent largement les rares signaux SHORT
      (demande Inde, rumeur Trump). Le rebond récent de +6.97% sur 5j confirme le
      momentum haussier malgré la baisse antérieure de -8.09% sur 20j.
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 37.533333333333324
      7j: 37.533333333333324
      1m: 37.533333333333324
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-03T20:01:09.026107+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: Multiples news high matérialité confirmant escalade Iran-US,
      fermeture Ormuz, frappes sur Koweït dominent largement les rares signaux SHORT
      (demande Inde, rumeur Trump). Le rebond récent de +6.97% sur 5j confirme le
      momentum haussier malgré la baisse antérieure de -8.09% sur 20j.
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 40.699999999999974
      7j: 40.699999999999974
      1m: 40.699999999999974
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
    - event_id: 208923e259fa
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: hausse
      surprise_polarity: up
      title: EIA publie son STEO de mai avec révision à la hausse des prix du pétrole
        en raison des perturbations persistantes au Moyen-Orient
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-03T20:01:09.026107+00:00'
  cushing_stocks:
    valeur: 22441.0
    valeur_normalisee: -0.3291943555278948
    valeur_ponderee: -0.3291943555278948
    ts: '2026-06-03T20:01:09.026107+00:00'
  spread_brent_wti:
    valeur: 1.5713499999999954
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-03T20:01:09.026107+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.08999999999999986
    valeur_normalisee: -0.683479598983062
    valeur_ponderee: -0.683479598983062
    ts: '2026-06-03T20:01:09.026107+00:00'
  breadth_sp_ma50:
    valeur: 0.2773947173013684
    valeur_normalisee: -0.49176345217401923
    valeur_ponderee: -0.49176345217401923
    ts: '2026-06-03T20:01:09.026107+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.0049302826285135826
    valeur_normalisee: -0.0621242807548921
    valeur_ponderee: -0.0621242807548921
    ts: '2026-06-03T20:01:09.026107+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.84
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T20:01:09.026107+00:00'
  rsi_14j_gspc:
    valeur: 68.4906089325198
    ts: '2026-06-03T20:01:09.026107+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-03T20:01:09.026107+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-03T20:01:09.026107+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-03T20:01:09.026107+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-03T20:01:09.026107+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-03T20:01:09.026107+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T20:01:09.026107+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée (frappes Iran,
      fermeture Ormuz, escalade militaire) malgré une baisse récente du VIX de -15%
      sur 20j. La fraîcheur et la densité des événements géopolitiques majeurs du
      3 juin justifient un biais haussier, le marché n''ayant pas encore intégré l''ampleur
      de '
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 31.799999999999997
      7j: 31.799999999999997
      1m: 31.799999999999997
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-03T20:01:09.026107+00:00'
```
