# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T19:55:47.857817+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T19:55:47.857817+00:00'
  mouvement_or_5j:
    valeur: -0.0021114410632073755
    valeur_normalisee: -0.06572546387522077
    valeur_ponderee: -0.06572546387522077
    ts: '2026-06-02T19:55:47.857817+00:00'
  ratio_gold_silver:
    valeur: 59.70477236913298
    ts: '2026-06-02T19:55:47.857817+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.004453392032654713
    valeur_normalisee: -0.1354427694549463
    valeur_ponderee: -0.1354427694549463
    ts: '2026-06-02T19:55:47.857817+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T19:55:47.857817+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.024885255306942078
    valeur_normalisee: -0.0943018629706126
    valeur_ponderee: -0.0943018629706126
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T19:55:47.857817+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T19:55:47.857817+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T19:55:47.857817+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (Chine lève interdictions
      Brésil, baisse production Australie) vs SHORT (Euronext à 3 semaines bas, pression
      pétrole). Prix en baisse de 9.89% sur 20j suggère que le marché a déjà intégré
      les éléments baissiers, sans signal frais dominant.'
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T19:55:47.857817+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.007455059325757185
    valeur_normalisee: 0.06296252977059161
    valeur_ponderee: 0.06296252977059161
    ts: '2026-06-02T19:55:47.857817+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.002613240418118501
    valeur_normalisee: 0.08533428312930098
    valeur_ponderee: 0.08533428312930098
    ts: '2026-06-02T19:55:47.857817+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T19:55:47.857817+00:00'
  rsi_14j_fchi:
    valeur: 56.274953399816965
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T19:55:47.857817+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T19:55:47.857817+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T19:55:47.857817+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Majorité de news SHORT (abondance offre, force dollar, stocks
      ICE) dominent, malgré une news LONG récente (Chine lève interdiction Brésil)
      de matérialité high mais conviction medium. Le prix a baissé de 7.73% sur 20j,
      confirmant le biais baissier, mais la news LONG récente limite la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.83'
    p2_shadow_contrib_exclu:
      24h: -9.966666666666669
      7j: -9.966666666666669
      1m: -9.966666666666669
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Majorité de news SHORT (abondance offre, force dollar, stocks
      ICE) dominent, malgré une news LONG récente (Chine lève interdiction Brésil)
      de matérialité high mais conviction medium. Le prix a baissé de 7.73% sur 20j,
      confirmant le biais baissier, mais la news LONG récente limite la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.83'
    p2_shadow_contrib_exclu:
      24h: -9.966666666666669
      7j: -9.966666666666669
      1m: -9.966666666666669
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.2821054799104276
    valeur_normalisee: -0.1410527399552138
    valeur_ponderee: -0.1410527399552138
    ts: '2026-06-02T19:55:47.857817+00:00'
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T19:55:47.857817+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Les news SHORT (tarifs US sur Brésil) et LONG (reconnaissance
      Chine, mauvaises récoltes) se contredisent fortement le même jour, sans signal
      dominant. Le prix a baissé de 7.62% sur 20j, suggérant que le marché a déjà
      intégré les risques tarifaires, neutralisant les drivers haussiers.
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
    ts: '2026-06-02T19:55:47.857817+00:00'
  meteo_vietnam_robusta:
    valeur: -0.21638148650563183
    valeur_normalisee: -0.10819074325281591
    valeur_ponderee: -0.10819074325281591
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, les profits industriels
      chinois élevés et le positionnement haussier de Citi dominent malgré les risques
      tarifaires et géopolitiques. Le prix a déjà intégré une partie de ce biais haussier
      (+3.91% sur 5j), limitant la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.83'
    p2_shadow_contrib_exclu:
      24h: -0.7000000000000001
      7j: -0.7000000000000001
      1m: -0.7000000000000001
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T19:55:47.857817+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, les profits industriels
      chinois élevés et le positionnement haussier de Citi dominent malgré les risques
      tarifaires et géopolitiques. Le prix a déjà intégré une partie de ce biais haussier
      (+3.91% sur 5j), limitant la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.83'
    p2_shadow_contrib_exclu:
      24h: 5.7666666666666675
      7j: 5.7666666666666675
      1m: 5.7666666666666675
  ratio_cuivre_or:
    valeur: 0.0014811335379655295
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
eurusd:
  differentiel_taux_10y_us_bund:
    valeur: 1.4536842105
    valeur_normalisee: 0.3001881730442448
    valeur_ponderee: 0.3001881730442448
    ts: '2026-06-02T19:55:47.857817+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.95124
    valeur_normalisee: 0.6106072927976115
    valeur_ponderee: 0.6106072927976115
    ts: '2026-06-02T19:55:47.857817+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T19:55:47.857817+00:00'
  sox_trend_5j:
    valeur: 605.075
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T19:55:47.857817+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16323549122101597
    valeur_normalisee: -0.25312343966196893
    valeur_ponderee: -0.25312343966196893
    ts: '2026-06-02T19:55:47.857817+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Alphabet/Berkshire
      80Mds IA, Nvidia PC chip, HPE résultats) sur une seule journée, confirmant la
      dynamique haussière du marché (+10.86% sur 20j). Les rares signaux SHORT (Barclays,
      executive order) sont marginaux et ne pèsent pas face au flux pro-IA massi
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 4.333333333333333
      7j: 4.333333333333333
      1m: 4.333333333333333
  flux_etf_qqq_5j:
    valeur: 0.02166288183999776
    valeur_normalisee: 0.11246817452377716
    valeur_ponderee: 0.11246817452377716
    ts: '2026-06-02T19:55:47.857817+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.58000000000004
    valeur_normalisee: 0.9078247304178639
    valeur_ponderee: 0.9078247304178639
    ts: '2026-06-02T19:55:47.857817+00:00'
  rsi_14j_ixic:
    valeur: 79.36856335939353
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T19:55:47.857817+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T19:55:47.857817+00:00'
  flux_etf_or_5j:
    valeur: -0.005108695652173978
    valeur_normalisee: 0.07051149754009155
    valeur_ponderee: 0.07051149754009155
    ts: '2026-06-02T19:55:47.857817+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Plusieurs news high matérialité soutiennent l'or (achats banques
      centrales, tensions géopolitiques persistantes au Liban et Ukraine, risque Ormuz),
      mais le prix a baissé de 4.3% sur 20j, suggérant que le marché a déjà intégré
      une partie de ces risques. La conviction est abaissée à medium car le sign
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
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
    ts: '2026-06-02T19:55:47.857817+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T19:55:47.857817+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T19:55:47.857817+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Malgré un recul de -9% sur 20j, les news du jour montrent
      un net biais LONG avec des tensions géopolitiques persistantes (Liban, Iran,
      Ukraine) et des risques d'offre (Ormuz, grève Ichthys). Les signaux SHORT (cessez-le-feu,
      discussions Iran) sont contredits par la poursuite des combats et l'incerti
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 30.76666666666667
      7j: 30.76666666666667
      1m: 30.76666666666667
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T19:55:47.857817+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: Malgré un recul de -9% sur 20j, les news du jour montrent
      un net biais LONG avec des tensions géopolitiques persistantes (Liban, Iran,
      Ukraine) et des risques d'offre (Ormuz, grève Ichthys). Les signaux SHORT (cessez-le-feu,
      discussions Iran) sont contredits par la poursuite des combats et l'incerti
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
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
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-02T19:55:47.857817+00:00'
  spread_brent_wti:
    valeur: 2.4114179999999976
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-02T19:55:47.857817+00:00'
  hy_credit_spread:
    valeur: 2.72
    valeur_normalisee: -0.5532705134158924
    valeur_ponderee: -0.5532705134158924
    ts: '2026-06-02T19:55:47.857817+00:00'
  breadth_sp_ma50:
    valeur: 0.2764677226106305
    valeur_normalisee: -0.5688759860264717
    valeur_ponderee: -0.5688759860264717
    ts: '2026-06-02T19:55:47.857817+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.011883944155240078
    valeur_normalisee: 0.105015964594727
    valeur_ponderee: 0.105015964594727
    ts: '2026-06-02T19:55:47.857817+00:00'
  rsi_14j_gspc:
    valeur: 76.0447602433787
    ts: '2026-06-02T19:55:47.857817+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T19:55:47.857817+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T19:55:47.857817+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T19:55:47.857817+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T19:55:47.857817+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T19:55:47.857817+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T19:55:47.857817+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T19:55:47.857817+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée et fraîcheur récente
      (escalade US-Iran, conflit Israël-Liban, tensions Ormuz) dominent largement
      les rares signaux SHORT (cessez-le-feu partiel, allègement sanctions). Malgré
      la baisse du VIX sur 20j, la concentration de news LONG très récentes (2 juin)
      et '
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.83'
    p2_shadow_contrib_exclu:
      24h: 25.266666666666666
      7j: 25.266666666666666
      1m: 25.266666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T19:55:47.857817+00:00'
```
