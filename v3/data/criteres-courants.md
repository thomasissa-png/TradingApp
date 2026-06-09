# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-09T05:19:08.061714+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  mouvement_or_5j:
    valeur: -0.03225972355615536
    valeur_normalisee: -0.6702574867698836
    valeur_ponderee: -0.6702574867698836
    ts: '2026-06-09T05:19:08.061714+00:00'
  ratio_gold_silver:
    valeur: 63.77696699419418
    ts: '2026-06-09T05:19:08.061714+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.048421197399424964
    valeur_normalisee: -0.597072599116012
    valeur_ponderee: -0.597072599116012
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_silver:
    valeur: 24492.0
    valeur_normalisee: -0.18736391301050243
    valeur_ponderee: -0.18736391301050243
    ts: '2026-06-09T05:19:08.061714+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.08999556672085118
    valeur_normalisee: -0.5117121996018871
    valeur_ponderee: -0.5117121996018871
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.371711058376757
    valeur_normalisee: 0.1858555291883785
    valeur_ponderee: 0.1858555291883785
    ts: '2026-06-09T05:19:08.061714+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: 'Signaux contradictoires : news SHORT sur screwworm et baisse
      des prix (Euronext, fonds) s''opposent aux news LONG (production australienne,
      Chine-Brésil). Prix en baisse de 11.56% sur 20j suggère que le marché a déjà
      intégré les facteurs baissiers, sans signal frais dominant.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  cftc_cot_wheat:
    valeur: -47361.0
    valeur_normalisee: -0.06793769229046236
    valeur_ponderee: -0.06793769229046236
    ts: '2026-06-09T05:19:08.061714+00:00'
  meteo_australie_dryland:
    valeur: -0.016438192334041927
    valeur_normalisee: -0.008219096167020963
    valeur_ponderee: -0.008219096167020963
    ts: '2026-06-09T05:19:08.061714+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6785842105
    valeur_normalisee: 0.28629604490204547
    valeur_ponderee: 0.28629604490204547
    ts: '2026-06-09T05:19:08.061714+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.03193898465426093
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.0058926233085989654
    valeur_normalisee: -0.11369165325241017
    valeur_ponderee: -0.11369165325241017
    ts: '2026-06-09T05:19:08.061714+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-09T05:19:08.061714+00:00'
  rsi_14j_fchi:
    valeur: 54.65508448476364
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_cocoa:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-09T05:19:08.061714+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-09T05:19:08.061714+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Majorité de nouvelles SHORT (demande faible, offre abondante,
      dollar fort) dominent, avec une seule news LONG (Brésil exempt de fièvre aphteuse)
      de matérialité élevée mais non fraîche. Le prix a déjà baissé de 2.80% sur 5j,
      confirmant le biais baissier, mais la conviction est medium car la news LONG
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: -17.933333333333362
      7j: -17.933333333333362
      1m: -17.933333333333362
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Majorité de nouvelles SHORT (demande faible, offre abondante,
      dollar fort) dominent, avec une seule news LONG (Brésil exempt de fièvre aphteuse)
      de matérialité élevée mais non fraîche. Le prix a déjà baissé de 2.80% sur 5j,
      confirmant le biais baissier, mais la conviction est medium car la news LONG
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: -17.933333333333362
      7j: -17.933333333333362
      1m: -17.933333333333362
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.3059834009569211
    valeur_normalisee: -0.15299170047846056
    valeur_ponderee: -0.15299170047846056
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_coffee:
    valeur: 10188.0
    valeur_normalisee: -0.5226180177014742
    valeur_ponderee: -0.5226180177014742
    ts: '2026-06-09T05:19:08.061714+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Plusieurs news SHORT récentes (harvest pressure, tarif US
      sur Brésil) dominent malgré des signaux LONG plus anciens. Le prix a déjà baissé
      de 8.57% sur 20j, ce qui réduit la conviction.
    nature: structurel
    event_id: cb5427ddc947
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 50.900000000000006
      7j: 50.900000000000006
      1m: 50.900000000000006
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-09T05:19:08.061714+00:00'
  meteo_vietnam_robusta:
    valeur: -0.14159759581600762
    valeur_normalisee: -0.07079879790800381
    valeur_ponderee: -0.07079879790800381
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Goldman relève
      objectif cuivre, tarifs Trump sur cuivre, exportations chinoises en hausse)
      malgré quelques signaux SHORT (tarifs Brésil, baisse ventes auto). Le prix a
      légèrement baissé sur 5j (-3%) mais la fraîcheur et la force des news LONG récentes
      (≤4
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 1.7333333333333336
      7j: 1.7333333333333336
      1m: 1.7333333333333336
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_copper_nets:
    valeur: 79599.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Goldman relève
      objectif cuivre, tarifs Trump sur cuivre, exportations chinoises en hausse)
      malgré quelques signaux SHORT (tarifs Brésil, baisse ventes auto). Le prix a
      légèrement baissé sur 5j (-3%) mais la fraîcheur et la force des news LONG récentes
      (≤4
    nature: structurel
    event_id: e4507225c94e
    event_date: '2026-06-09T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 14.133333333333331
      7j: 14.133333333333331
      1m: 14.133333333333331
  ratio_cuivre_or:
    valeur: 0.001456384867230558
    valeur_normalisee: 0.7567681792243136
    valeur_ponderee: 0.7567681792243136
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-09T05:19:08.061714+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5684764053999998
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.5536842104999997
    valeur_normalisee: 0.7343215340744282
    valeur_ponderee: 0.7343215340744282
    ts: '2026-06-09T05:19:08.061714+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-09T05:19:08.061714+00:00'
  usd_jpy_proxy_risk:
    valeur: 160.20118
    valeur_normalisee: 0.6324228432063472
    valeur_ponderee: 0.6324228432063472
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_eur_nets:
    valeur: 15729.0
    valeur_normalisee: -0.31647179596046804
    valeur_ponderee: -0.31647179596046804
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  sox_trend_5j:
    valeur: 571.45001
    valeur_normalisee: 0.7024157183083091
    valeur_ponderee: 0.7024157183083091
    ts: '2026-06-09T05:19:08.061714+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16432750827392215
    valeur_normalisee: -0.07345973444801805
    valeur_ponderee: -0.07345973444801805
    ts: '2026-06-09T05:19:08.061714+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (exportations chinoises,
      partenariats IA) et SHORT (liste noire Pentagon, tensions Iran-Israël, vente
      massive tech) s''équilibrent. Le prix a baissé de 3.59% sur 5j, suggérant que
      le marché a déjà intégré les risques géopolitiques et macro, sans signal dominant
      cla'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 10.200000000000001
      7j: 10.200000000000001
      1m: 10.200000000000001
  flux_etf_qqq_5j:
    valeur: -0.03590756302215525
    valeur_normalisee: -0.8665045067936481
    valeur_ponderee: -0.8665045067936481
    ts: '2026-06-09T05:19:08.061714+00:00'
  spread_nasdaq_russell2000:
    valeur: 431.96001700000005
    valeur_normalisee: 0.5317015746404825
    valeur_ponderee: 0.5317015746404825
    ts: '2026-06-09T05:19:08.061714+00:00'
  rsi_14j_ixic:
    valeur: 55.05560101540505
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-09T05:19:08.061714+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_nets:
    valeur: 171417.0
    valeur_normalisee: -0.2399836149756058
    valeur_ponderee: -0.2399836149756058
    ts: '2026-06-09T05:19:08.061714+00:00'
  flux_etf_or_5j:
    valeur: -0.03401745771488951
    valeur_normalisee: -0.28881549540702584
    valeur_ponderee: -0.28881549540702584
    ts: '2026-06-09T05:19:08.061714+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Les news récentes (8-9 juin) montrent une escalade militaire
      Iran-Israël dominante (matérialité high, fraîcheur), soutenant l'or comme valeur
      refuge, malgré le recul du prix de -4.64% sur 20j. Le marché a partiellement
      pricé l'info, mais la persistance des attaques et l'absence de désescalade claire
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 54.76666666666665
      7j: 54.76666666666665
      1m: 54.76666666666665
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-09T05:19:08.061714+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-09T05:19:08.061714+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-09T05:19:08.061714+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-09T05:19:08.061714+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Escalade militaire Iran-Israël avec frappes directes et menaces
      sur Hormuz dominent, malgré une baisse de prix de -11% sur 20j. Les news LONG
      high matérialité des 2 derniers jours (frappes, attaque terminal Oman) sont
      fraîches et changent le régime, justifiant un biais haussier malgré le recul
      récen
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 57.06666666666663
      7j: 57.06666666666663
      1m: 57.06666666666663
  cftc_cot_crude_nets:
    valeur: 28239.0
    valeur_normalisee: 0.07039238470355488
    valeur_ponderee: 0.07039238470355488
    ts: '2026-06-09T05:19:08.061714+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Escalade militaire Iran-Israël avec frappes directes et menaces
      sur Hormuz dominent, malgré une baisse de prix de -11% sur 20j. Les news LONG
      high matérialité des 2 derniers jours (frappes, attaque terminal Oman) sont
      fraîches et changent le régime, justifiant un biais haussier malgré le recul
      récen
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 63.966666666666676
      7j: 63.966666666666676
      1m: 63.966666666666676
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
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-09T05:19:08.061714+00:00'
  cushing_stocks:
    valeur: 22441.0
    valeur_normalisee: -0.3291943555278948
    valeur_ponderee: -0.3291943555278948
    ts: '2026-06-09T05:19:08.061714+00:00'
  spread_brent_wti:
    valeur: 3.3888199999999955
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-09T05:19:08.061714+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-09T05:19:08.061714+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.09999999999999964
    valeur_normalisee: 0.42667100546060216
    valeur_ponderee: 0.42667100546060216
    ts: '2026-06-09T05:19:08.061714+00:00'
  hy_credit_spread:
    valeur: 2.76
    valeur_normalisee: -0.3937430110206332
    valeur_ponderee: -0.3937430110206332
    ts: '2026-06-09T05:19:08.061714+00:00'
  breadth_sp_ma50:
    valeur: 0.28085009662279553
    valeur_normalisee: -0.23346032258556998
    valeur_ponderee: -0.23346032258556998
    ts: '2026-06-09T05:19:08.061714+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-09T05:19:08.061714+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.025469995661929423
    valeur_normalisee: -0.773796932733941
    valeur_ponderee: -0.773796932733941
    ts: '2026-06-09T05:19:08.061714+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.67
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  rsi_14j_gspc:
    valeur: 53.024124662133616
    ts: '2026-06-09T05:19:08.061714+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.19
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-09T05:19:08.061714+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-09T05:19:08.061714+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-09T05:19:08.061714+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-09T05:19:08.061714+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-09T05:19:08.061714+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-09T05:19:08.061714+00:00'
  cftc_cot_vix_nets:
    valeur: -69952.0
    valeur_normalisee: -0.3350126494595268
    valeur_ponderee: -0.3350126494595268
    ts: '2026-06-09T05:19:08.061714+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-09T05:19:08.061714+00:00'
    synthese_rationale: Majorité de news à matérialité haute et fraîcheur récente
      (8 juin) signalent une escalade Iran-Israël, avec attaques directes et menaces
      sur le détroit d'Ormuz, ce qui domine les quelques signaux d'apaisement. Le
      marché a baissé de 11.6% sur 20j, mais la concentration de news LONG très récentes
      (≤48
    nature: ponctuel
    event_id: dbf9364e740a
    event_date: '2026-06-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 49.633333333333326
      7j: 49.633333333333326
      1m: 49.633333333333326
  gate_evenement_macro_imminent:
    valeur: false
    ts: '2026-06-09T05:19:08.061714+00:00'
```
