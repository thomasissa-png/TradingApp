# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-08T14:25:55.675401+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T14:25:55.675401+00:00'
  mouvement_or_5j:
    valeur: -0.0261208977291274
    valeur_normalisee: -0.5308560797738172
    valeur_ponderee: -0.5308560797738172
    ts: '2026-06-08T14:25:55.675401+00:00'
  ratio_gold_silver:
    valeur: 63.58179303761108
    ts: '2026-06-08T14:25:55.675401+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.04006007837307646
    valeur_normalisee: -0.5159046731785752
    valeur_ponderee: -0.5159046731785752
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_silver:
    valeur: 24492.0
    valeur_normalisee: -0.18736391301050243
    valeur_ponderee: -0.18736391301050243
    ts: '2026-06-08T14:25:55.675401+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.0926555342101375
    valeur_normalisee: -0.5284333609200144
    valeur_ponderee: -0.5284333609200144
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.367419817109613
    valeur_normalisee: 0.1837099085548065
    valeur_ponderee: 0.1837099085548065
    ts: '2026-06-08T14:25:55.675401+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG sur production australienne
      et Chine/Brésil, mais SHORT sur screwworm, positions fonds et baisse des prix.
      Prix en baisse de 12.8% sur 20j suggère que le marché a déjà intégré les éléments
      baissiers, sans signal frais dominant.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-08T14:25:55.675401+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -47361.0
    valeur_normalisee: -0.06793769229046236
    valeur_ponderee: -0.06793769229046236
    ts: '2026-06-08T14:25:55.675401+00:00'
  meteo_australie_dryland:
    valeur: -0.01740474500849054
    valeur_normalisee: -0.00870237250424527
    valeur_ponderee: -0.00870237250424527
    ts: '2026-06-08T14:25:55.675401+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T14:25:55.675401+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6785842105
    valeur_normalisee: 0.28629604490204547
    valeur_ponderee: 0.28629604490204547
    ts: '2026-06-08T14:25:55.675401+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.029611933798312284
    valeur_normalisee: 0.9561119658333148
    valeur_ponderee: 0.9561119658333148
    ts: '2026-06-08T14:25:55.675401+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.0037101702313400153
    valeur_normalisee: -0.07444510615172116
    valeur_ponderee: -0.07444510615172116
    ts: '2026-06-08T14:25:55.675401+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-08T14:25:55.675401+00:00'
  rsi_14j_fchi:
    valeur: 55.70827411624975
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_cocoa:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-08T14:25:55.675401+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-08T14:25:55.675401+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Dominance de news SHORT (demande faible, offre abondante,
      dollar fort) avec matérialité moyenne à élevée et fraîcheur récente. La seule
      news LONG (Brésil) est ancienne et non liée au cacao. Le prix baisse sur 20j
      et 5j, confirmant le biais baissier.
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.60'
    p2_shadow_contrib_exclu:
      24h: -15.20000000000002
      7j: -15.20000000000002
      1m: -15.20000000000002
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Dominance de news SHORT (demande faible, offre abondante,
      dollar fort) avec matérialité moyenne à élevée et fraîcheur récente. La seule
      news LONG (Brésil) est ancienne et non liée au cacao. Le prix baisse sur 20j
      et 5j, confirmant le biais baissier.
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.60'
    p2_shadow_contrib_exclu:
      24h: -15.20000000000002
      7j: -15.20000000000002
      1m: -15.20000000000002
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T14:25:55.675401+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.30514737140933784
    valeur_normalisee: -0.15257368570466892
    valeur_ponderee: -0.15257368570466892
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_coffee:
    valeur: 10188.0
    valeur_normalisee: -0.5226180177014742
    valeur_ponderee: -0.5226180177014742
    ts: '2026-06-08T14:25:55.675401+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Dominance de news SHORT récentes (tarifs US sur Brésil, pression
      récolte) malgré quelques signaux LONG plus anciens. Le prix a déjà baissé de
      8.41% sur 20j, confirmant le biais baissier.
    nature: structurel
    event_id: cb5427ddc947
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.60'
    p2_shadow_contrib_exclu:
      24h: 49.73333333333334
      7j: 49.73333333333334
      1m: 49.73333333333334
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-08T14:25:55.675401+00:00'
  meteo_vietnam_robusta:
    valeur: -0.14878450110829308
    valeur_normalisee: -0.07439225055414654
    valeur_ponderee: -0.07439225055414654
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T14:25:55.675401+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Goldman Sachs objectif
      +10%, Trump tarifs cuivre) et fraîches (≤5j) malgré une baisse récente de -1.87%
      sur 5j. Le +3.07% sur 20j confirme le biais haussier structurel.
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.60'
    p2_shadow_contrib_exclu:
      24h: 1.5333333333333334
      7j: 1.5333333333333334
      1m: 1.5333333333333334
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_copper_nets:
    valeur: 79599.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-08T14:25:55.675401+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Goldman Sachs objectif
      +10%, Trump tarifs cuivre) et fraîches (≤5j) malgré une baisse récente de -1.87%
      sur 5j. Le +3.07% sur 20j confirme le biais haussier structurel.
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.60'
    p2_shadow_contrib_exclu:
      24h: 13.466666666666665
      7j: 13.466666666666665
      1m: 13.466666666666665
  ratio_cuivre_or:
    valeur: 0.0014699069943152467
    valeur_normalisee: 0.8702517821719457
    valeur_ponderee: 0.8702517821719457
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4683630226999997
    valeur_normalisee: 0.7551441274948792
    valeur_ponderee: 0.7551441274948792
    ts: '2026-06-08T14:25:55.675401+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4736842104999996
    valeur_normalisee: 0.3447091196443128
    valeur_ponderee: 0.3447091196443128
    ts: '2026-06-08T14:25:55.675401+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T14:25:55.675401+00:00'
  usd_jpy_proxy_risk:
    valeur: 160.17649
    valeur_normalisee: 0.6355705420991694
    valeur_ponderee: 0.6355705420991694
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_eur_nets:
    valeur: 15729.0
    valeur_normalisee: -0.31647179596046804
    valeur_ponderee: -0.31647179596046804
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T14:25:55.675401+00:00'
  sox_trend_5j:
    valeur: 568.775
    valeur_normalisee: 0.6882110791422793
    valeur_ponderee: 0.6882110791422793
    ts: '2026-06-08T14:25:55.675401+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16438967267049573
    valeur_normalisee: -0.06513630306259632
    valeur_ponderee: -0.06513630306259632
    ts: '2026-06-08T14:25:55.675401+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (attaques Iran-Israël,
      vente tech, dollar fort, rotation sectorielle) sur les 3 derniers jours, malgré
      quelques news LONG isolées. Le prix a baissé de 3.56% sur 5j, confirmant le
      biais baissier.
    nature: ponctuel
    event_id: 4c495c7d569d
    event_date: '2026-06-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.60'
    p2_shadow_contrib_exclu:
      24h: 10.200000000000001
      7j: 10.200000000000001
      1m: 10.200000000000001
  flux_etf_qqq_5j:
    valeur: -0.03422461472688443
    valeur_normalisee: -0.8394024794941097
    valeur_ponderee: -0.8394024794941097
    ts: '2026-06-08T14:25:55.675401+00:00'
  spread_nasdaq_russell2000:
    valeur: 432.03000000000003
    valeur_normalisee: 0.5324980843347601
    valeur_ponderee: 0.5324980843347601
    ts: '2026-06-08T14:25:55.675401+00:00'
  rsi_14j_ixic:
    valeur: 55.571917135005364
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T14:25:55.675401+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_nets:
    valeur: 171417.0
    valeur_normalisee: -0.2399836149756058
    valeur_ponderee: -0.2399836149756058
    ts: '2026-06-08T14:25:55.675401+00:00'
  flux_etf_or_5j:
    valeur: -0.035670888594298455
    valeur_normalisee: -0.30964692988310755
    valeur_ponderee: -0.30964692988310755
    ts: '2026-06-08T14:25:55.675401+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et confirmées (escalade
      Iran-Israël, attaques missiles, frappes pétrochimiques) dominent le signal,
      malgré quelques news SHORT liées au dollar fort et aux attentes Fed. Le prix
      a baissé de 3.62% sur 20j, mais la fraîcheur et la matérialité des news LONG
      (to
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 52.36666666666665
      7j: 52.36666666666665
      1m: 52.36666666666665
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-08T14:25:55.675401+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-08T14:25:55.675401+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-08T14:25:55.675401+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Escalade militaire directe Iran-Israël avec frappes sur infrastructures
      pétrolières et menaces sur le détroit d'Ormuz dominent, malgré une hausse OPEC+
      et une baisse de prix de -14.9% sur 20 jours. La fraîcheur et la matérialité
      élevée des news LONG (toutes du 8 juin) surclassent le mouvement de pri
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 55.59999999999996
      7j: 55.59999999999996
      1m: 55.59999999999996
  cftc_cot_crude_nets:
    valeur: 28239.0
    valeur_normalisee: 0.07039238470355488
    valeur_ponderee: 0.07039238470355488
    ts: '2026-06-08T14:25:55.675401+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: Escalade militaire directe Iran-Israël avec frappes sur infrastructures
      pétrolières et menaces sur le détroit d'Ormuz dominent, malgré une hausse OPEC+
      et une baisse de prix de -14.9% sur 20 jours. La fraîcheur et la matérialité
      élevée des news LONG (toutes du 8 juin) surclassent le mouvement de pri
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 62.500000000000014
      7j: 62.500000000000014
      1m: 62.500000000000014
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
    ts: '2026-06-08T14:25:55.675401+00:00'
  cushing_stocks:
    valeur: 22441.0
    valeur_normalisee: -0.3291943555278948
    valeur_ponderee: -0.3291943555278948
    ts: '2026-06-08T14:25:55.675401+00:00'
  spread_brent_wti:
    valeur: 3.1399899999999974
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-08T14:25:55.675401+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.019999999999999574
    valeur_normalisee: -0.036056571495000286
    valeur_ponderee: -0.036056571495000286
    ts: '2026-06-08T14:25:55.675401+00:00'
  hy_credit_spread:
    valeur: 2.76
    valeur_normalisee: -0.3937430110206332
    valeur_ponderee: -0.3937430110206332
    ts: '2026-06-08T14:25:55.675401+00:00'
  breadth_sp_ma50:
    valeur: 0.281028679143665
    valeur_normalisee: -0.22192588632868845
    valeur_ponderee: -0.22192588632868845
    ts: '2026-06-08T14:25:55.675401+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T14:25:55.675401+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.020882195293120853
    valeur_normalisee: -0.6703571877987297
    valeur_ponderee: -0.6703571877987297
    ts: '2026-06-08T14:25:55.675401+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.57
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-08T14:25:55.675401+00:00'
  rsi_14j_gspc:
    valeur: 55.439468118141654
    ts: '2026-06-08T14:25:55.675401+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T14:25:55.675401+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-08T14:25:55.675401+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-08T14:25:55.675401+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-08T14:25:55.675401+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-08T14:25:55.675401+00:00'
  cftc_cot_vix_nets:
    valeur: -69952.0
    valeur_normalisee: -0.3350126494595268
    valeur_ponderee: -0.3350126494595268
    ts: '2026-06-08T14:25:55.675401+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T14:25:55.675401+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (08/06) dominent, malgré 2 news SHORT isolées. Le prix VIX en baisse de 12%
      sur 20j est contredit par l''escalade Iran-Israël très récente, ce qui justifie
      une conviction haute car le marché n''a pas encore intégré ce choc géopolitique '
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.60'
    p2_shadow_contrib_exclu:
      24h: 47.93333333333332
      7j: 47.93333333333332
      1m: 47.93333333333332
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-08T14:25:55.675401+00:00'
```
