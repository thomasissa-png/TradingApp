# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T09:41:23.262014+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T09:41:23.262014+00:00'
  mouvement_or_5j:
    valeur: 0.006145043832559205
    valeur_normalisee: 0.11487542093044714
    valeur_ponderee: 0.11487542093044714
    ts: '2026-06-02T09:41:23.262014+00:00'
  ratio_gold_silver:
    valeur: 59.33583698684447
    ts: '2026-06-02T09:41:23.262014+00:00'
  alpha_argent_vs_or_5j:
    valeur: 0.0016376528306003557
    valeur_normalisee: -0.0579361407659037
    valeur_ponderee: -0.0579361407659037
    ts: '2026-06-02T09:41:23.262014+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T09:41:23.262014+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.010093622001170255
    valeur_normalisee: -0.010882415223491364
    valeur_ponderee: -0.010882415223491364
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T09:41:23.262014+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T09:41:23.262014+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T09:41:23.262014+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Baisse de production australienne (LONG, high) contredit le
      mouvement baissier du prix (-9.69% sur 20j), mais les news SHORT récentes (Euronext
      à 3 semaines, pression pétrole) dominent et le marché a déjà intégré l'info.
      Signal trop dispersé.
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T09:41:23.262014+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T09:41:23.262014+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.013500534769797179
    valeur_normalisee: -0.07679225980550873
    valeur_ponderee: -0.07679225980550873
    ts: '2026-06-02T09:41:23.262014+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.014390081912774022
    valeur_normalisee: 0.2762766481355668
    valeur_ponderee: 0.2762766481355668
    ts: '2026-06-02T09:41:23.262014+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T09:41:23.262014+00:00'
  rsi_14j_fchi:
    valeur: 56.09732644308353
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T09:41:23.262014+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T09:41:23.262014+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T09:41:23.262014+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Dollar strength and rising ICE inventories dominate with multiple
      SHORT signals, despite a low-impact stable price outlook. The -10.61% price
      drop over 20 days aligns with the bearish news, but the signals are not fresh
      enough for high conviction.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '12.40'
    p2_shadow_contrib_exclu:
      24h: -7.600000000000003
      7j: -7.600000000000003
      1m: -7.600000000000003
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Dollar strength and rising ICE inventories dominate with multiple
      SHORT signals, despite a low-impact stable price outlook. The -10.61% price
      drop over 20 days aligns with the bearish news, but the signals are not fresh
      enough for high conviction.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '12.40'
    p2_shadow_contrib_exclu:
      24h: -7.600000000000003
      7j: -7.600000000000003
      1m: -7.600000000000003
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T09:41:23.262014+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T09:41:23.262014+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Une news SHORT high du 2 juin (tarif 25% Brésil) contredit
      les news LONG plus anciennes sur les récoltes et prix. Le prix a baissé de 7.42%
      sur 20j, suggérant que le marché a déjà intégré le choc tarifaire. Pas de signal
      dominant clair.
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 27.43333333333332
      7j: 27.43333333333332
      1m: 27.43333333333332
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Les news LONG dominent avec des PMI chinois solides, des profits
      industriels records et des risques d'offre (Cobre Panama, Iran), malgré une
      proposition de tarif US et des données officielles chinoises faibles. Le prix
      a déjà monté de 3% sur 5j, ce qui limite la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.40'
    p2_shadow_contrib_exclu:
      24h: -1.3666666666666667
      7j: -1.3666666666666667
      1m: -1.3666666666666667
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T09:41:23.262014+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Les news LONG dominent avec des PMI chinois solides, des profits
      industriels records et des risques d'offre (Cobre Panama, Iran), malgré une
      proposition de tarif US et des données officielles chinoises faibles. Le prix
      a déjà monté de 3% sur 5j, ce qui limite la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.40'
    p2_shadow_contrib_exclu:
      24h: 3.433333333333333
      7j: 3.433333333333333
      1m: 3.433333333333333
  ratio_cuivre_or:
    valeur: 0.0014572184834336368
    valeur_normalisee: 0.94820351938409
    valeur_ponderee: 0.94820351938409
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.72073
    valeur_normalisee: 0.5002842530288704
    valeur_ponderee: 0.5002842530288704
    ts: '2026-06-02T09:41:23.262014+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
nasdaq:
  sox_trend_5j:
    valeur: 571.92999
    valeur_normalisee: 0.8877929217199515
    valeur_ponderee: 0.8877929217199515
    ts: '2026-06-02T09:41:23.262014+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Nvidia, Alphabet,
      Anthropic) et fraîcheur récente, malgré quelques signaux SHORT isolés. Le prix
      (+10% sur 20j) confirme le momentum haussier, renforcé par des annonces majeures
      du 1er et 2 juin.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.40'
    p2_shadow_contrib_exclu:
      24h: 1.9333333333333331
      7j: 1.9333333333333331
      1m: 1.9333333333333331
  flux_etf_qqq_5j:
    valeur: 0.035120008225883126
    valeur_normalisee: 0.35922460073081663
    valeur_ponderee: 0.35922460073081663
    ts: '2026-06-02T09:41:23.262014+00:00'
  spread_nasdaq_russell2000:
    valeur: 453.75998000000004
    valeur_normalisee: 0.9414930191721986
    valeur_ponderee: 0.9414930191721986
    ts: '2026-06-02T09:41:23.262014+00:00'
  rsi_14j_ixic:
    valeur: 78.6749097386528
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T09:41:23.262014+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T09:41:23.262014+00:00'
  flux_etf_or_5j:
    valeur: -0.0061862644099786035
    valeur_normalisee: 0.04867063187236333
    valeur_ponderee: 0.04867063187236333
    ts: '2026-06-02T09:41:23.262014+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Dominance de news géopolitiques LONG (escalade US-Iran, Israël-Liban)
      à matérialité high et fraîcheur récente, malgré des signaux SHORT plus anciens
      et le recul du prix sur 20j. La fraîcheur et la matérialité des news LONG l'emportent.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.40'
    p2_shadow_contrib_exclu:
      24h: 23.1
      7j: 23.1
      1m: 23.1
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T09:41:23.262014+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T09:41:23.262014+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T09:41:23.262014+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Escalade Iran-USA et Israël-Liban domine avec matérialité
      high et fraîcheur, malgré des signaux de cessez-le-feu et baisse de prix saoudienne.
      Le marché a déjà intégré une partie du risque mais les news récentes (frappes,
      inflation énergie) renforcent le biais haussier.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.40'
    p2_shadow_contrib_exclu:
      24h: 24.566666666666666
      7j: 24.566666666666666
      1m: 24.566666666666666
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T09:41:23.262014+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Escalade Iran-USA et Israël-Liban domine avec matérialité
      high et fraîcheur, malgré des signaux de cessez-le-feu et baisse de prix saoudienne.
      Le marché a déjà intégré une partie du risque mais les news récentes (frappes,
      inflation énergie) renforcent le biais haussier.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.40'
    p2_shadow_contrib_exclu:
      24h: 21.966666666666672
      7j: 21.966666666666672
      1m: 21.966666666666672
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
    ts: '2026-06-02T09:41:23.262014+00:00'
  spread_brent_wti:
    valeur: 2.634829999999994
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
sp500:
  vix_regime:
    valeur: 23.865
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T09:41:23.262014+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-02T09:41:23.262014+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.017300533537625062
    valeur_normalisee: 0.2411352806454264
    valeur_ponderee: 0.2411352806454264
    ts: '2026-06-02T09:41:23.262014+00:00'
  rsi_14j_gspc:
    valeur: 75.89804938696159
    ts: '2026-06-02T09:41:23.262014+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T09:41:23.262014+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T09:41:23.262014+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T09:41:23.262014+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T09:41:23.262014+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T09:41:23.262014+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T09:41:23.262014+00:00'
    synthese_rationale: Majorité de news LONG (escalade Iran/US, Israël/Liban) avec
      matérialité high, mais le prix VIX a baissé de 13% sur 20j, suggérant que le
      marché a déjà intégré ces tensions. Une news SHORT (cessez-le-feu Liban) et
      la baisse récente du VIX limitent la conviction.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.40'
    p2_shadow_contrib_exclu:
      24h: 21.1
      7j: 21.1
      1m: 21.1
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T09:41:23.262014+00:00'
```
