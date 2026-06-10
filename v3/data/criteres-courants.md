# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-10T05:19:06.037447+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  mouvement_or_5j:
    valeur: -0.03481711498948936
    valeur_normalisee: -0.7036541665923679
    valeur_ponderee: -0.7036541665923679
    ts: '2026-06-10T05:19:06.037447+00:00'
  ratio_gold_silver:
    valeur: 65.5640505111426
    ts: '2026-06-10T05:19:06.037447+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.02516308796779887
    valeur_normalisee: -0.3008725561644248
    valeur_ponderee: -0.3008725561644248
    ts: '2026-06-10T05:19:06.037447+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-10T05:19:06.037447+00:00'
    note: hors fenêtre
  cftc_cot_silver:
    valeur: 24492.0
    valeur_normalisee: -0.18736391301050243
    valeur_ponderee: -0.18736391301050243
    ts: '2026-06-10T05:19:06.037447+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.13207827180467713
    valeur_normalisee: -0.7769743397041239
    valeur_ponderee: -0.7769743397041239
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-10T05:19:06.037447+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.38433206691784166
    valeur_normalisee: 0.19216603345892083
    valeur_ponderee: 0.19216603345892083
    ts: '2026-06-10T05:19:06.037447+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (baisse production Australie,
      Chine lève interdiction Brésil) vs SHORT (screwworm US, fonds réduisent longs,
      baisse prix Euronext). Prix -9.23% sur 20j suggère que le biais SHORT est déjà
      intégré, sans news fraîche high pour inverser.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  cftc_cot_wheat:
    valeur: -47361.0
    valeur_normalisee: -0.06793769229046236
    valeur_ponderee: -0.06793769229046236
    ts: '2026-06-10T05:19:06.037447+00:00'
  meteo_australie_dryland:
    valeur: -0.009155520263872403
    valeur_normalisee: -0.004577760131936202
    valeur_ponderee: -0.004577760131936202
    ts: '2026-06-10T05:19:06.037447+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-10T05:19:06.037447+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6785842105
    valeur_normalisee: 0.28629604490204547
    valeur_ponderee: 0.28629604490204547
    ts: '2026-06-10T05:19:06.037447+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.028958883885329523
    valeur_normalisee: 0.8952673302858846
    valeur_ponderee: 0.8952673302858846
    ts: '2026-06-10T05:19:06.037447+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.004340320992173519
    valeur_normalisee: -0.11346484560021698
    valeur_ponderee: -0.11346484560021698
    ts: '2026-06-10T05:19:06.037447+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-10T05:19:06.037447+00:00'
  rsi_14j_fchi:
    valeur: 55.4330713795003
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-10T05:19:06.037447+00:00'
  cftc_cot_cocoa:
    valeur: -23189.0
    valeur_normalisee: -0.7730303034118962
    valeur_ponderee: -0.7730303034118962
    ts: '2026-06-10T05:19:06.037447+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-10T05:19:06.037447+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Majorité des news récentes (8 sur 9) signalent une pression
      baissière via demande faible et offre abondante, malgré une news LONG sur le
      Brésil. Le prix a légèrement augmenté (+1.69% sur 20j), ce qui contredit le
      signal SHORT dominant, abaissant la conviction à medium.
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: -17.466666666666697
      7j: -17.466666666666697
      1m: -17.466666666666697
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Majorité des news récentes (8 sur 9) signalent une pression
      baissière via demande faible et offre abondante, malgré une news LONG sur le
      Brésil. Le prix a légèrement augmenté (+1.69% sur 20j), ce qui contredit le
      signal SHORT dominant, abaissant la conviction à medium.
    nature: structurel
    event_id: d1aea367dde8
    event_date: '2026-06-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: -17.466666666666697
      7j: -17.466666666666697
      1m: -17.466666666666697
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-10T05:19:06.037447+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.32046178494102
    valeur_normalisee: -0.16023089247051
    valeur_ponderee: -0.16023089247051
    ts: '2026-06-10T05:19:06.037447+00:00'
  cftc_cot_coffee:
    valeur: 10188.0
    valeur_normalisee: -0.5226180177014742
    valeur_ponderee: -0.5226180177014742
    ts: '2026-06-10T05:19:06.037447+00:00'
  maladies_cabosses_rouille:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Dominance de news SHORT récentes (harvest pressure, tarif
      US sur Brésil) malgré quelques signaux LONG plus anciens. Le prix a déjà baissé
      de 10% sur 20j, mais la fraîcheur des news SHORT (2-3 juin) et la matérialité
      high du tarif US justifient un biais SHORT avec conviction medium.
    nature: structurel
    event_id: cb5427ddc947
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 51.36666666666666
      7j: 51.36666666666666
      1m: 51.36666666666666
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-10T05:19:06.037447+00:00'
  meteo_vietnam_robusta:
    valeur: -0.12444798088850217
    valeur_normalisee: -0.06222399044425109
    valeur_ponderee: -0.06222399044425109
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-10T05:19:06.037447+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-10T05:19:06.037447+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée et fraîches (inflation
      Chine, exportations, relèvement objectif cuivre Goldman Sachs) malgré quelques
      news SHORT anciennes ou de faible matérialité. Le prix quasi stable sur 5j ne
      contredit pas le signal haussier fort.
    nature: structurel
    event_id: fb9705ac3bbb
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 2.4
      7j: 2.4
      1m: 2.4
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-10T05:19:06.037447+00:00'
  cftc_cot_copper_nets:
    valeur: 79599.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée et fraîches (inflation
      Chine, exportations, relèvement objectif cuivre Goldman Sachs) malgré quelques
      news SHORT anciennes ou de faible matérialité. Le prix quasi stable sur 5j ne
      contredit pas le signal haussier fort.
    nature: structurel
    event_id: 077856a285a5
    event_date: '2026-06-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 14.799999999999997
      7j: 14.799999999999997
      1m: 14.799999999999997
  ratio_cuivre_or:
    valeur: 0.0014990054867602197
    valeur_normalisee: 0.9926251096994506
    valeur_ponderee: 0.9926251096994506
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5264185420000005
    valeur_normalisee: 0.9663254531308894
    valeur_ponderee: 0.9663254531308894
    ts: '2026-06-10T05:19:06.037447+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.5636842104999995
    valeur_normalisee: 0.7553088678801506
    valeur_ponderee: 0.7553088678801506
    ts: '2026-06-10T05:19:06.037447+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-10T05:19:06.037447+00:00'
  usd_jpy_proxy_risk:
    valeur: 160.3646
    valeur_normalisee: 0.684803580298282
    valeur_ponderee: 0.684803580298282
    ts: '2026-06-10T05:19:06.037447+00:00'
  cftc_cot_eur_nets:
    valeur: 15729.0
    valeur_normalisee: -0.31647179596046804
    valeur_ponderee: -0.31647179596046804
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  sox_trend_5j:
    valeur: 562.14001
    valeur_normalisee: 0.629222101317357
    valeur_ponderee: 0.629222101317357
    ts: '2026-06-10T05:19:06.037447+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.1648418358972681
    valeur_normalisee: 0.004543638491264228
    valeur_ponderee: 0.004543638491264228
    ts: '2026-06-10T05:19:06.037447+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Escalade Iran-Israël confirmée (high mat) et vente massive
      tech (high mat) dominent, avec dollar fort et craintes Fed. Les news LONG (exportations
      Chine, IA) sont plus anciennes ou moins matérielles, et le prix a déjà baissé
      de 5% en 5j, confirmant le biais short.
    nature: ponctuel
    event_id: 4c495c7d569d
    event_date: '2026-06-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 10.200000000000001
      7j: 10.200000000000001
      1m: 10.200000000000001
  flux_etf_qqq_5j:
    valeur: -0.05136961448092703
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  spread_nasdaq_russell2000:
    valeur: 422.810031
    valeur_normalisee: 0.4095757350906469
    valeur_ponderee: 0.4095757350906469
    ts: '2026-06-10T05:19:06.037447+00:00'
  rsi_14j_ixic:
    valeur: 51.21912483538989
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-10T05:19:06.037447+00:00'
  cftc_cot_nets:
    valeur: 171417.0
    valeur_normalisee: -0.2399836149756058
    valeur_ponderee: -0.2399836149756058
    ts: '2026-06-10T05:19:06.037447+00:00'
  flux_etf_or_5j:
    valeur: -0.051389754790878706
    valeur_normalisee: -0.5026433465785143
    valeur_ponderee: -0.5026433465785143
    ts: '2026-06-10T05:19:06.037447+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Escalade US-Iran du 10 juin avec hélicoptère abattu et frappes
      directes domine, malgré baisse récente de l'or. Tensions géopolitiques élevées
      et risque d'inflation soutiennent l'or comme valeur refuge.
    nature: structurel
    event_id: f84937356b73
    event_date: '2026-06-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 57.76666666666665
      7j: 57.76666666666665
      1m: 57.76666666666665
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-10T05:19:06.037447+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-10T05:19:06.037447+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur: 433712.0
    valeur_normalisee: 0.10010806760573361
    valeur_ponderee: 0.10010806760573361
    ts: '2026-06-10T05:19:06.037447+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Escalade majeure US-Iran le 10 juin avec hélicoptère abattu
      et frappes américaines, menaçant le détroit d'Ormuz, domine les signaux baissiers
      plus anciens et moins matériels. Le prix a baissé de 12.6% sur 20j, mais la
      fraîcheur et la matérialité élevée des news LONG du jour justifient un biais
      hauss
    nature: structurel
    event_id: f84937356b73
    event_date: '2026-06-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 60.533333333333296
      7j: 60.533333333333296
      1m: 60.533333333333296
  cftc_cot_crude_nets:
    valeur: 28239.0
    valeur_normalisee: 0.07039238470355488
    valeur_ponderee: 0.07039238470355488
    ts: '2026-06-10T05:19:06.037447+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: Escalade majeure US-Iran le 10 juin avec hélicoptère abattu
      et frappes américaines, menaçant le détroit d'Ormuz, domine les signaux baissiers
      plus anciens et moins matériels. Le prix a baissé de 12.6% sur 20j, mais la
      fraîcheur et la matérialité élevée des news LONG du jour justifient un biais
      hauss
    nature: structurel
    event_id: f84937356b73
    event_date: '2026-06-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 67.43333333333337
      7j: 67.43333333333337
      1m: 67.43333333333337
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
    ts: '2026-06-10T05:19:06.037447+00:00'
  cushing_stocks:
    valeur: 22441.0
    valeur_normalisee: -0.3291943555278948
    valeur_ponderee: -0.3291943555278948
    ts: '2026-06-10T05:19:06.037447+00:00'
  spread_brent_wti:
    valeur: 3.2022599999999954
    ts: '2026-06-10T05:19:06.037447+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-10T05:19:06.037447+00:00'
    note: hors fenêtre
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-10T05:19:06.037447+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.08999999999999986
    valeur_normalisee: 0.37590470577805546
    valeur_ponderee: 0.37590470577805546
    ts: '2026-06-10T05:19:06.037447+00:00'
  hy_credit_spread:
    valeur: 2.75
    valeur_normalisee: -0.4053176352217691
    valeur_ponderee: -0.4053176352217691
    ts: '2026-06-10T05:19:06.037447+00:00'
  breadth_sp_ma50:
    valeur: 0.2838206409413848
    valeur_normalisee: -0.028729069573097482
    valeur_ponderee: -0.028729069573097482
    ts: '2026-06-10T05:19:06.037447+00:00'
  dxy_trend_20j:
    valeur: 120.0831
    valeur_normalisee: 0.48294014677064406
    valeur_ponderee: 0.48294014677064406
    ts: '2026-06-10T05:19:06.037447+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.02964838224721389
    valeur_normalisee: -0.8596994676930342
    valeur_ponderee: -0.8596994676930342
    ts: '2026-06-10T05:19:06.037447+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.54
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  rsi_14j_gspc:
    valeur: 51.61147890925813
    ts: '2026-06-10T05:19:06.037447+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-10T05:19:06.037447+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-10T05:19:06.037447+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-10T05:19:06.037447+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-10T05:19:06.037447+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-10T05:19:06.037447+00:00'
  cftc_cot_vix_nets:
    valeur: -69952.0
    valeur_normalisee: -0.3350126494595268
    valeur_ponderee: -0.3350126494595268
    ts: '2026-06-10T05:19:06.037447+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-10T05:19:06.037447+00:00'
    synthese_rationale: 'Escalade US-Iran avec hélicoptère abattu et frappes américaines
      le 10 juin, matérialité high et fraîcheur dominante, surclassant les news SHORT
      anciennes. Le prix VIX en baisse sur 20j (-11.46%) est contredit par cette nouvelle
      escalade, mais la fraîcheur et la matérialité high justifient un signal '
    nature: structurel
    event_id: f84937356b73
    event_date: '2026-06-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 53.099999999999994
      7j: 53.099999999999994
      1m: 53.099999999999994
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-10T05:19:06.037447+00:00'
```
