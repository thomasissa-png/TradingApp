# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-01T19:20:36.829305+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T19:20:36.829305+00:00'
  mouvement_or_5j:
    valeur: 0.006758617696913216
    valeur_normalisee: 0.12108972208142445
    valeur_ponderee: 0.12108972208142445
    ts: '2026-06-01T19:20:36.829305+00:00'
  ratio_gold_silver:
    valeur: 59.777492074955795
    ts: '2026-06-01T19:20:36.829305+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.0011129928719701976
    valeur_normalisee: -0.09539092368635115
    valeur_ponderee: -0.09539092368635115
    ts: '2026-06-01T19:20:36.829305+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-01T19:20:36.829305+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.007167934464599068
    valeur_normalisee: 0.007618978394243177
    valeur_ponderee: 0.007618978394243177
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:20:36.829305+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21729063160967518
    valeur_normalisee: 0.10864531580483759
    valeur_ponderee: 0.10864531580483759
    ts: '2026-06-01T19:20:36.829305+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Trois news SHORT récentes, dont deux de matérialité medium
      avec haute confiance, confirment la tendance baissière du prix (-3.33% sur 20j).
      La plus récente (1er juin) renforce le biais short malgré le contexte de baisse
      déjà intégrée.
    nature: ponctuel
    event_id: 60b424d3caa9
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.81'
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:20:36.829305+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-01T19:20:36.829305+00:00'
  meteo_australie_dryland:
    valeur: -0.08312920306313831
    valeur_normalisee: -0.041564601531569156
    valeur_ponderee: -0.041564601531569156
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T19:20:36.829305+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.01472769531339524
    valeur_normalisee: -0.10672548381675814
    valeur_ponderee: -0.10672548381675814
    ts: '2026-06-01T19:20:36.829305+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.01616116891742303
    valeur_normalisee: 0.30444609742504375
    valeur_ponderee: 0.30444609742504375
    ts: '2026-06-01T19:20:36.829305+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-01T19:20:36.829305+00:00'
  rsi_14j_fchi:
    valeur: 52.18370018731938
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T19:20:36.829305+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T19:20:36.829305+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:20:36.829305+00:00'
    note: hors fenêtre
  eudr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Multiple recent news point to dollar strength pressuring cocoa
      prices, aligning with the -15% decline over 20 days. However, the market has
      likely already priced this in, and no fresh high-materiality catalyst justifies
      a strong conviction.
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: -5.933333333333333
      7j: -5.933333333333333
      1m: -5.933333333333333
  maladies_cabosses:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Multiple recent news point to dollar strength pressuring cocoa
      prices, aligning with the -15% decline over 20 days. However, the market has
      likely already priced this in, and no fresh high-materiality catalyst justifies
      a strong conviction.
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: -5.933333333333333
      7j: -5.933333333333333
      1m: -5.933333333333333
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T19:20:36.829305+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-01T19:20:36.829305+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Les news LONG (mauvaises récoltes, hausse des prix) sont contredites
      par une baisse de prix de -7.53% sur 20j, indiquant que le marché a déjà intégré
      ces informations ou que d'autres facteurs baissiers dominent. Aucune news fraîche
      à matérialité high ne justifie d'aller contre le prix.
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 25.933333333333323
      7j: 25.933333333333323
      1m: 25.933333333333323
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T19:20:36.829305+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, les profits industriels
      chinois élevés et la position haussière de Citi dominent, malgré les tensions
      géopolitiques et le ralentissement de l'activité chinoise fin mai. Le prix a
      rebondi de +3.89% sur 5j, en ligne avec le biais long, mais la baisse sur 20j
      (-0
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.81'
    p2_shadow_contrib_exclu:
      24h: -1.5666666666666664
      7j: -1.5666666666666664
      1m: -1.5666666666666664
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T19:20:36.829305+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, les profits industriels
      chinois élevés et la position haussière de Citi dominent, malgré les tensions
      géopolitiques et le ralentissement de l'activité chinoise fin mai. Le prix a
      rebondi de +3.89% sur 5j, en ligne avec le biais long, mais la baisse sur 20j
      (-0
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.81'
    p2_shadow_contrib_exclu:
      24h: 1.7666666666666666
      7j: 1.7666666666666666
      1m: 1.7666666666666666
  ratio_cuivre_or:
    valeur: 0.0014602550806257603
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.69085
    valeur_normalisee: 0.48646090023178323
    valeur_ponderee: 0.48646090023178323
    ts: '2026-06-01T19:20:36.829305+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T19:20:36.829305+00:00'
  sox_trend_5j:
    valeur: 572.0
    valeur_normalisee: 0.8881854068209121
    valeur_ponderee: 0.8881854068209121
    ts: '2026-06-01T19:20:36.829305+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Nvidia AI chip,
      Arm PC, Anthropic IPO) et cohérentes avec le rallye récent (+10.36% sur 20j).
      Les rares news SHORT (Iran, Powell, régulation) sont minoritaires et de matérialité
      moindre, ne renversant pas le momentum haussier.
    nature: ponctuel
    event_id: 3a1ea0ee1c97
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 1.9333333333333331
      7j: 1.9333333333333331
      1m: 1.9333333333333331
  flux_etf_qqq_5j:
    valeur: 0.0367366568201537
    valeur_normalisee: 0.3874051974069907
    valeur_ponderee: 0.3874051974069907
    ts: '2026-06-01T19:20:36.829305+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.315
    valeur_normalisee: 0.947979770680809
    valeur_ponderee: 0.947979770680809
    ts: '2026-06-01T19:20:36.829305+00:00'
  rsi_14j_ixic:
    valeur: 78.97227626526373
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T19:20:36.829305+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-01T19:20:36.829305+00:00'
  flux_etf_or_5j:
    valeur: -0.00497803380750006
    valeur_normalisee: 0.06392646738120741
    valeur_ponderee: 0.06392646738120741
    ts: '2026-06-01T19:20:36.829305+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Dominance de news géopolitiques LONG (frappes US-Iran, escalade
      Israël-Liban) à matérialité élevée et fraîcheur immédiate, malgré des news SHORT
      sur les taux et la baisse récente du prix. Le marché n'a pas encore intégré
      cette escalade majeure du 1er juin.
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 17.0
      7j: 17.0
      1m: 17.0
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T19:20:36.829305+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:20:36.829305+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:20:36.829305+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée sur l'escalade
      Iran-USA et Israël-Liban, malgré quelques signaux SHORT et une baisse de prix
      de -11% sur 20j. La fraîcheur et la matérialité des news géopolitiques récentes
      (1er juin) justifient un biais haussier malgré le contexte de prix baissier.
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 17.8
      7j: 17.8
      1m: 17.8
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-01T19:20:36.829305+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée sur l'escalade
      Iran-USA et Israël-Liban, malgré quelques signaux SHORT et une baisse de prix
      de -11% sur 20j. La fraîcheur et la matérialité des news géopolitiques récentes
      (1er juin) justifient un biais haussier malgré le contexte de prix baissier.
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 14.533333333333333
      7j: 14.533333333333333
      1m: 14.533333333333333
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-01T19:20:36.829305+00:00'
  spread_brent_wti:
    valeur: 2.733164000000002
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
sp500:
  vix_regime:
    valeur: 23.605
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T19:20:36.829305+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-01T19:20:36.829305+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.018561222324966264
    valeur_normalisee: 0.2708276362191231
    valeur_ponderee: 0.2708276362191231
    ts: '2026-06-01T19:20:36.829305+00:00'
  rsi_14j_gspc:
    valeur: 76.31089543785005
    ts: '2026-06-01T19:20:36.829305+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-01T19:20:36.829305+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-01T19:20:36.829305+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-01T19:20:36.829305+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-01T19:20:36.829305+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-01T19:20:36.829305+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:20:36.829305+00:00'
    synthese_rationale: 'Dominance de news LONG à matérialité élevée et fraîcheur
      immédiate (toutes du 1er juin) : escalade Iran-USA, offensive Israël-Liban,
      menaces sur Ormuz. Malgré la baisse récente du VIX, la concentration et la force
      des signaux géopolitiques justifient une conviction haute.'
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 15.0
      7j: 15.0
      1m: 15.0
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-01T19:20:36.829305+00:00'
```
