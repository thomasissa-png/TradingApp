# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T16:04:30.111439+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T16:04:30.111439+00:00'
  mouvement_or_5j:
    valeur: 0.0013629061139428522
    valeur_normalisee: 0.010286562442728556
    valeur_ponderee: 0.010286562442728556
    ts: '2026-06-02T16:04:30.111439+00:00'
  ratio_gold_silver:
    valeur: 59.45179428409599
    ts: '2026-06-02T16:04:30.111439+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.0008094158676223984
    valeur_normalisee: -0.08908815535664653
    valeur_ponderee: -0.08908815535664653
    ts: '2026-06-02T16:04:30.111439+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T16:04:30.111439+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.01821572002294891
    valeur_normalisee: -0.05137407595347953
    valeur_ponderee: -0.05137407595347953
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T16:04:30.111439+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T16:04:30.111439+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T16:04:30.111439+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: 'News mitigées : baisse production australienne (LONG) vs
      chute prix Euronext et pression pétrole (SHORT). Prix -9.89% sur 20j suggère
      que le marché a déjà intégré les facteurs baissiers, sans signal frais dominant.'
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T16:04:30.111439+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.0074683821779140125
    valeur_normalisee: 0.06263357280632174
    valeur_ponderee: 0.06263357280632174
    ts: '2026-06-02T16:04:30.111439+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.0034843205574912606
    valeur_normalisee: 0.09925979982269782
    valeur_ponderee: 0.09925979982269782
    ts: '2026-06-02T16:04:30.111439+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T16:04:30.111439+00:00'
  rsi_14j_fchi:
    valeur: 56.274953399816965
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T16:04:30.111439+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T16:04:30.111439+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T16:04:30.111439+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Majorité de news SHORT récentes (abondance, dollar fort, stocks
      ICE) dominent, malgré une news LONG Chine/Brésil de matérialité high mais isolée.
      Le prix a baissé de 7% sur 20j, confirmant le biais baissier.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.67'
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
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Majorité de news SHORT récentes (abondance, dollar fort, stocks
      ICE) dominent, malgré une news LONG Chine/Brésil de matérialité high mais isolée.
      Le prix a baissé de 7% sur 20j, confirmant le biais baissier.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.67'
    p2_shadow_contrib_exclu:
      24h: -9.966666666666669
      7j: -9.966666666666669
      1m: -9.966666666666669
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.2821054799104276
    valeur_normalisee: -0.1410527399552138
    valeur_ponderee: -0.1410527399552138
    ts: '2026-06-02T16:04:30.111439+00:00'
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T16:04:30.111439+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Tarif US sur Brésil (SHORT) et levée interdiction Chine (LONG)
      s'opposent le même jour, matérialité haute mais signaux contradictoires. Prix
      en baisse de 7.71% sur 20j suggère que le marché a déjà intégré les risques
      tarifaires, neutralisant les news LONG plus anciennes.
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
    ts: '2026-06-02T16:04:30.111439+00:00'
  meteo_vietnam_robusta:
    valeur: -0.21638148650563183
    valeur_normalisee: -0.10819074325281591
    valeur_ponderee: -0.10819074325281591
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, la hausse des profits
      industriels chinois, et les risques d'offre (Cobre Panama, tensions géopolitiques)
      dominent malgré les tarifs brésiliens et les données officielles chinoises faibles.
      Le prix a déjà monté de 4% sur 5j, ce qui limite la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.67'
    p2_shadow_contrib_exclu:
      24h: -0.7000000000000001
      7j: -0.7000000000000001
      1m: -0.7000000000000001
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T16:04:30.111439+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, la hausse des profits
      industriels chinois, et les risques d'offre (Cobre Panama, tensions géopolitiques)
      dominent malgré les tarifs brésiliens et les données officielles chinoises faibles.
      Le prix a déjà monté de 4% sur 5j, ce qui limite la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.67'
    p2_shadow_contrib_exclu:
      24h: 5.1000000000000005
      7j: 5.1000000000000005
      1m: 5.1000000000000005
  ratio_cuivre_or:
    valeur: 0.001480624285444805
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
eurusd:
  differentiel_taux_10y_us_bund:
    valeur: 1.4536842105
    valeur_normalisee: 0.3001881730442448
    valeur_ponderee: 0.3001881730442448
    ts: '2026-06-02T16:04:30.111439+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.89366
    valeur_normalisee: 0.5831828748191882
    valeur_ponderee: 0.5831828748191882
    ts: '2026-06-02T16:04:30.111439+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T16:04:30.111439+00:00'
  sox_trend_5j:
    valeur: 600.18
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T16:04:30.111439+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.162766371182963
    valeur_normalisee: -0.3140942462109095
    valeur_ponderee: -0.3140942462109095
    ts: '2026-06-02T16:04:30.111439+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Nvidia PC chip,
      HPE, Alphabet IA funding, Berkshire) sur une seule journée, confirmant le momentum
      haussier. Le prix (+10.77% sur 20j) est cohérent avec le signal, et la fraîcheur
      des news (2 juin) renforce la conviction.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.67'
    p2_shadow_contrib_exclu:
      24h: 3.8666666666666663
      7j: 3.8666666666666663
      1m: 3.8666666666666663
  flux_etf_qqq_5j:
    valeur: 0.021074066615240694
    valeur_normalisee: 0.10209002228292133
    valeur_ponderee: 0.10209002228292133
    ts: '2026-06-02T16:04:30.111439+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.56999999999994
    valeur_normalisee: 0.9077100007596335
    valeur_ponderee: 0.9077100007596335
    ts: '2026-06-02T16:04:30.111439+00:00'
  rsi_14j_ixic:
    valeur: 79.25650406784426
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T16:04:30.111439+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T16:04:30.111439+00:00'
  flux_etf_or_5j:
    valeur: -0.0022222222222222365
    valeur_normalisee: 0.10727790329326818
    valeur_ponderee: 0.10727790329326818
    ts: '2026-06-02T16:04:30.111439+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: 'Multiples news high matérialité soutiennent l''or : achats
      records des banques centrales, tensions persistantes au Liban et en Ukraine,
      risque de pénurie pétrolière via Ormuz. Le recul de -3.97% sur 20j est contredit
      par ces catalyseurs frais et forts, justifiant un biais haussier malgré le contexte '
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.67'
    p2_shadow_contrib_exclu:
      24h: 25.700000000000003
      7j: 25.700000000000003
      1m: 25.700000000000003
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T16:04:30.111439+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T16:04:30.111439+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T16:04:30.111439+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: 'Signaux contradictoires : cessez-le-feu au Liban et discussions
      US-Iran (SHORT) s''opposent aux tensions persistantes et aux risques sur le
      détroit d''Ormuz (LONG). Le prix a baissé de 9.5% sur 20j, suggérant que le
      marché a déjà intégré les risques géopolitiques, et la récente hausse de 2.3%
      sur 5j n'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 29.166666666666668
      7j: 29.166666666666668
      1m: 29.166666666666668
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T16:04:30.111439+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: 'Signaux contradictoires : cessez-le-feu au Liban et discussions
      US-Iran (SHORT) s''opposent aux tensions persistantes et aux risques sur le
      détroit d''Ormuz (LONG). Le prix a baissé de 9.5% sur 20j, suggérant que le
      marché a déjà intégré les risques géopolitiques, et la récente hausse de 2.3%
      sur 5j n'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 30.199999999999996
      7j: 30.199999999999996
      1m: 30.199999999999996
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-02T16:04:30.111439+00:00'
  spread_brent_wti:
    valeur: 2.7531199999999956
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
sp500:
  vix_regime:
    valeur: 23.6
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T16:04:30.111439+00:00'
  hy_credit_spread:
    valeur: 2.72
    valeur_normalisee: -0.5532705134158924
    valeur_ponderee: -0.5532705134158924
    ts: '2026-06-02T16:04:30.111439+00:00'
  breadth_sp_ma50:
    valeur: 0.2760386498867885
    valeur_normalisee: -0.5958012836168995
    valeur_ponderee: -0.5958012836168995
    ts: '2026-06-02T16:04:30.111439+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.012057141233277502
    valeur_normalisee: 0.10911966390162905
    valeur_ponderee: 0.10911966390162905
    ts: '2026-06-02T16:04:30.111439+00:00'
  rsi_14j_gspc:
    valeur: 76.10566119840932
    ts: '2026-06-02T16:04:30.111439+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T16:04:30.111439+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T16:04:30.111439+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T16:04:30.111439+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T16:04:30.111439+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T16:04:30.111439+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T16:04:30.111439+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T16:04:30.111439+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et fraîcheur récente
      (escalade Iran-USA, conflit Israël-Liban, tensions Ormuz) dominent, malgré une
      news SHORT (cessez-le-feu Liban) et une baisse de prix de 15% sur 20j. La fraîcheur
      et la matérialité des news LONG (notamment les frappes du 1er-2 juin) ind
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.67'
    p2_shadow_contrib_exclu:
      24h: 25.266666666666666
      7j: 25.266666666666666
      1m: 25.266666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T16:04:30.111439+00:00'
```
