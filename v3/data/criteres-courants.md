# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-08T05:04:05.330834+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T05:04:05.330834+00:00'
  mouvement_or_5j:
    valeur: -0.027235304094172408
    valeur_normalisee: -0.5586573744825856
    valeur_ponderee: -0.5586573744825856
    ts: '2026-06-08T05:04:05.330834+00:00'
  ratio_gold_silver:
    valeur: 63.62969682407424
    ts: '2026-06-08T05:04:05.330834+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.04059997300502527
    valeur_normalisee: -0.5222246154405821
    valeur_ponderee: -0.5222246154405821
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_silver:
    valeur: 24492.0
    valeur_normalisee: -0.18736391301050243
    valeur_ponderee: -0.18736391301050243
    ts: '2026-06-08T05:04:05.330834+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.09893165520269276
    valeur_normalisee: -0.5724961493084685
    valeur_ponderee: -0.5724961493084685
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.367419817109613
    valeur_normalisee: 0.1837099085548065
    valeur_ponderee: 0.1837099085548065
    ts: '2026-06-08T05:04:05.330834+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: 'Signaux contradictoires : baisse de production australienne
      (LONG) contre fonds shortant et pression baissière des prix (SHORT). Prix en
      forte baisse (-13.73% sur 20j) suggère que les news LONG sont déjà intégrées,
      et les news récentes sont mitigées sans signal dominant.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-08T05:04:05.330834+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -47361.0
    valeur_normalisee: -0.06793769229046236
    valeur_ponderee: -0.06793769229046236
    ts: '2026-06-08T05:04:05.330834+00:00'
  meteo_australie_dryland:
    valeur: -0.01740474500849054
    valeur_normalisee: -0.00870237250424527
    valeur_ponderee: -0.00870237250424527
    ts: '2026-06-08T05:04:05.330834+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T05:04:05.330834+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6785842105
    valeur_normalisee: 0.28629604490204547
    valeur_ponderee: 0.28629604490204547
    ts: '2026-06-08T05:04:05.330834+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.02928859190966171
    valeur_normalisee: 0.9914243684045311
    valeur_ponderee: 0.9914243684045311
    ts: '2026-06-08T05:04:05.330834+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.013269523602349342
    valeur_normalisee: -0.2117423019010508
    valeur_ponderee: -0.2117423019010508
    ts: '2026-06-08T05:04:05.330834+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-08T05:04:05.330834+00:00'
  rsi_14j_fchi:
    valeur: 55.43114523430505
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_cocoa:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-08T05:04:05.330834+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-08T05:04:05.330834+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: Majorité de news SHORT (demande faible, offre abondante, dollar
      fort) dominent, avec une seule news LONG (Brésil) de matérialité high mais non
      liée au cacao. Le prix a baissé de 7.71% sur 5j, confirmant le biais baissier,
      mais la conviction est medium car les news sont majoritairement de matérialité
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.21'
    p2_shadow_contrib_exclu:
      24h: -14.53333333333335
      7j: -14.53333333333335
      1m: -14.53333333333335
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: Majorité de news SHORT (demande faible, offre abondante, dollar
      fort) dominent, avec une seule news LONG (Brésil) de matérialité high mais non
      liée au cacao. Le prix a baissé de 7.71% sur 5j, confirmant le biais baissier,
      mais la conviction est medium car les news sont majoritairement de matérialité
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.21'
    p2_shadow_contrib_exclu:
      24h: -14.53333333333335
      7j: -14.53333333333335
      1m: -14.53333333333335
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T05:04:05.330834+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.30514737140933784
    valeur_normalisee: -0.15257368570466892
    valeur_ponderee: -0.15257368570466892
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_coffee:
    valeur: 10188.0
    valeur_normalisee: -0.5226180177014742
    valeur_ponderee: -0.5226180177014742
    ts: '2026-06-08T05:04:05.330834+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: Tarif US de 25% sur le Brésil (high, 2 juin) et pression récoltière
      pèsent, malgré des signaux longs plus anciens. Le prix a déjà baissé de 7.5%
      sur 20j, ce qui limite la conviction.
    nature: structurel
    event_id: cb5427ddc947
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.21'
    p2_shadow_contrib_exclu:
      24h: 50.43333333333334
      7j: 50.43333333333334
      1m: 50.43333333333334
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-08T05:04:05.330834+00:00'
  meteo_vietnam_robusta:
    valeur: -0.14878450110829308
    valeur_normalisee: -0.07439225055414654
    valeur_ponderee: -0.07439225055414654
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T05:04:05.330834+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Goldman Sachs objectif
      +10%, Trump tarifs cuivre, PMI Chine solides) malgré une baisse récente de -3.27%
      sur 5j. Le signal haussier est frais et cohérent, surclassant les rares news
      SHORT.
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.21'
    p2_shadow_contrib_exclu:
      24h: 1.5333333333333334
      7j: 1.5333333333333334
      1m: 1.5333333333333334
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_copper_nets:
    valeur: 79599.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-08T05:04:05.330834+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Goldman Sachs objectif
      +10%, Trump tarifs cuivre, PMI Chine solides) malgré une baisse récente de -3.27%
      sur 5j. Le signal haussier est frais et cohérent, surclassant les rares news
      SHORT.
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.21'
    p2_shadow_contrib_exclu:
      24h: 13.466666666666665
      7j: 13.466666666666665
      1m: 13.466666666666665
  ratio_cuivre_or:
    valeur: 0.0014483944053787006
    valeur_normalisee: 0.730304722811644
    valeur_ponderee: 0.730304722811644
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-08T05:04:05.330834+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.4683630226999997
    valeur_normalisee: 0.7551441274948792
    valeur_ponderee: 0.7551441274948792
    ts: '2026-06-08T05:04:05.330834+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4736842104999996
    valeur_normalisee: 0.3447091196443128
    valeur_ponderee: 0.3447091196443128
    ts: '2026-06-08T05:04:05.330834+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T05:04:05.330834+00:00'
  usd_jpy_proxy_risk:
    valeur: 160.35109
    valeur_normalisee: 0.7124196146565978
    valeur_ponderee: 0.7124196146565978
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_eur_nets:
    valeur: 15729.0
    valeur_normalisee: -0.31647179596046804
    valeur_ponderee: -0.31647179596046804
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T05:04:05.330834+00:00'
  sox_trend_5j:
    valeur: 539.77002
    valeur_normalisee: 0.5500428115745252
    valeur_ponderee: 0.5500428115745252
    ts: '2026-06-08T05:04:05.330834+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16483703561352803
    valeur_normalisee: -0.010690247862750557
    valeur_ponderee: -0.010690247862750557
    ts: '2026-06-08T05:04:05.330834+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée et fraîcheur
      récente (8 juin) : escalade géopolitique, dollar fort, rotation sectorielle,
      et déception Broadcom. Les quelques news LONG (Nvidia, emploi US) sont minoritaires
      et ne compensent pas le biais baissier net.'
    nature: ponctuel
    event_id: 4c495c7d569d
    event_date: '2026-06-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.21'
    p2_shadow_contrib_exclu:
      24h: 10.200000000000001
      7j: 10.200000000000001
      1m: 10.200000000000001
  flux_etf_qqq_5j:
    valeur: -0.04503528599097939
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-08T05:04:05.330834+00:00'
  spread_nasdaq_russell2000:
    valeur: 423.41000799999995
    valeur_normalisee: 0.44855683148372927
    valeur_ponderee: 0.44855683148372927
    ts: '2026-06-08T05:04:05.330834+00:00'
  rsi_14j_ixic:
    valeur: 49.314415752504445
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T05:04:05.330834+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_nets:
    valeur: 171417.0
    valeur_normalisee: -0.2399836149756058
    valeur_ponderee: -0.2399836149756058
    ts: '2026-06-08T05:04:05.330834+00:00'
  flux_etf_or_5j:
    valeur: -0.050057561373226034
    valeur_normalisee: -0.49819148642406386
    valeur_ponderee: -0.49819148642406386
    ts: '2026-06-08T05:04:05.330834+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: Escalade militaire Iran-Israël et frappes au Liban dominent
      avec matérialité high, malgré le recul récent du prix de -3.74% sur 20j. La
      fraîcheur et la gravité des news géopolitiques (missiles balistiques, attaque
      terminal pétrolier) justifient un biais haussier malgré la pression baissière
      du dolla
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
    p2_shadow_contrib_exclu:
      24h: 50.99999999999999
      7j: 50.99999999999999
      1m: 50.99999999999999
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-08T05:04:05.330834+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-08T05:04:05.330834+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-08T05:04:05.330834+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et très récentes
      (8 juin) : escalade Iran-Israël, attaque terminal pétrolier Oman, effondrement
      trafic Ormuz. Malgré baisse prix -12.5%/20j, ces événements changent le régime
      offre, justifiant un biais haussier.'
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
    p2_shadow_contrib_exclu:
      24h: 54.69999999999997
      7j: 54.69999999999997
      1m: 54.69999999999997
  cftc_cot_crude_nets:
    valeur: 28239.0
    valeur_normalisee: 0.07039238470355488
    valeur_ponderee: 0.07039238470355488
    ts: '2026-06-08T05:04:05.330834+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et très récentes
      (8 juin) : escalade Iran-Israël, attaque terminal pétrolier Oman, effondrement
      trafic Ormuz. Malgré baisse prix -12.5%/20j, ces événements changent le régime
      offre, justifiant un biais haussier.'
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
    p2_shadow_contrib_exclu:
      24h: 61.133333333333354
      7j: 61.133333333333354
      1m: 61.133333333333354
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
    ts: '2026-06-08T05:04:05.330834+00:00'
  cushing_stocks:
    valeur: 22441.0
    valeur_normalisee: -0.3291943555278948
    valeur_ponderee: -0.3291943555278948
    ts: '2026-06-08T05:04:05.330834+00:00'
  spread_brent_wti:
    valeur: 2.7999050000000096
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-08T05:04:05.330834+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.019999999999999574
    valeur_normalisee: -0.036056571495000286
    valeur_ponderee: -0.036056571495000286
    ts: '2026-06-08T05:04:05.330834+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.456606071454028
    valeur_ponderee: -0.456606071454028
    ts: '2026-06-08T05:04:05.330834+00:00'
  breadth_sp_ma50:
    valeur: 0.2817842896316764
    valeur_normalisee: -0.18192491000672747
    valeur_ponderee: -0.18192491000672747
    ts: '2026-06-08T05:04:05.330834+00:00'
  dxy_trend_20j:
    valeur: 118.8783
    valeur_normalisee: -0.22895973114507306
    valeur_ponderee: -0.22895973114507306
    ts: '2026-06-08T05:04:05.330834+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.02502378185870824
    valeur_normalisee: -0.7779714819929686
    valeur_ponderee: -0.7779714819929686
    ts: '2026-06-08T05:04:05.330834+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.57
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-08T05:04:05.330834+00:00'
  rsi_14j_gspc:
    valeur: 50.86560450551567
    ts: '2026-06-08T05:04:05.330834+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.11
    valeur_normalisee: 0.6955800631800233
    valeur_ponderee: 0.6955800631800233
    ts: '2026-06-08T05:04:05.330834+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-08T05:04:05.330834+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-08T05:04:05.330834+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-08T05:04:05.330834+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-08T05:04:05.330834+00:00'
  cftc_cot_vix_nets:
    valeur: -69952.0
    valeur_normalisee: -0.3350126494595268
    valeur_ponderee: -0.3350126494595268
    ts: '2026-06-08T05:04:05.330834+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-08T05:04:05.330834+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et fraîcheur
      récente (8 juin) : escalade Iran-Israël, attaques sur infrastructures pétrolières,
      effondrement du trafic d''Ormuz. Le rebond de +4.38% sur 5j confirme le signal
      haussier malgré la baisse sur 20j.'
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
    p2_shadow_contrib_exclu:
      24h: 46.56666666666666
      7j: 46.56666666666666
      1m: 46.56666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-08T05:04:05.330834+00:00'
```
