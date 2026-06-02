# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T08:59:16.596655+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T08:59:16.596655+00:00'
  mouvement_or_5j:
    valeur: 0.006696288517972215
    valeur_normalisee: 0.12692046894254178
    valeur_ponderee: 0.12692046894254178
    ts: '2026-06-02T08:59:16.596655+00:00'
  ratio_gold_silver:
    valeur: 59.24316338522159
    ts: '2026-06-02T08:59:16.596655+00:00'
  alpha_argent_vs_or_5j:
    valeur: 0.003161732246898863
    valeur_normalisee: -0.03852791972921627
    valeur_ponderee: -0.03852791972921627
    ts: '2026-06-02T08:59:16.596655+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T08:59:16.596655+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.010093622001170255
    valeur_normalisee: -0.010882415223491364
    valeur_ponderee: -0.010882415223491364
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T08:59:16.596655+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T08:59:16.596655+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T08:59:16.596655+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Trois news SHORT récentes, dont deux à matérialité medium
      et confiance haute, confirment la baisse des prix du blé sur fond d'apaisement
      des craintes sur les récoltes et de pression du pétrole. Le mouvement de prix
      (-9.46% sur 20j) est cohérent avec le signal, renforçant la conviction.
    nature: ponctuel
    event_id: 60b424d3caa9
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.37'
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T08:59:16.596655+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T08:59:16.596655+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.013500534769797179
    valeur_normalisee: -0.07679225980550873
    valeur_ponderee: -0.07679225980550873
    ts: '2026-06-02T08:59:16.596655+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.014390081912774022
    valeur_normalisee: 0.2762766481355668
    valeur_ponderee: 0.2762766481355668
    ts: '2026-06-02T08:59:16.596655+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T08:59:16.596655+00:00'
  rsi_14j_fchi:
    valeur: 56.76541253839778
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.1718737046270795
    valeur_normalisee: 0.08593685231353974
    valeur_ponderee: 0.08593685231353974
    ts: '2026-06-02T08:59:16.596655+00:00'
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T08:59:16.596655+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T08:59:16.596655+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T08:59:16.596655+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Dollar strength et hausse des stocks ICE dominent avec 5 news
      SHORT de matérialité moyenne, dont 3 récentes (27 mai). Le prix a déjà baissé
      de 11.84% sur 20j, ce qui réduit la conviction à medium malgré la cohérence
      des signaux.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '12.37'
    p2_shadow_contrib_exclu:
      24h: -8.066666666666668
      7j: -8.066666666666668
      1m: -8.066666666666668
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Dollar strength et hausse des stocks ICE dominent avec 5 news
      SHORT de matérialité moyenne, dont 3 récentes (27 mai). Le prix a déjà baissé
      de 11.84% sur 20j, ce qui réduit la conviction à medium malgré la cohérence
      des signaux.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '12.37'
    p2_shadow_contrib_exclu:
      24h: -8.066666666666668
      7j: -8.066666666666668
      1m: -8.066666666666668
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T08:59:16.596655+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T08:59:16.596655+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Une news SHORT high matérialité (tarif 25% sur Brésil) contredit
      le biais LONG des autres news, et le prix a déjà baissé de 7% sur 20j, suggérant
      que le marché a intégré l'info. Signal trop dispersé pour un biais net.
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 26.96666666666665
      7j: 26.96666666666665
      1m: 26.96666666666665
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: 'Signaux contradictoires : tarif US sur Brésil (SHORT) vs
      PMI chinois solides (LONG) et tensions géopolitiques (LONG offre). Prix en hausse
      récente (+3.3% sur 5j) suggère que le marché a déjà intégré les facteurs haussiers,
      neutralisant le biais net.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: -2.033333333333333
      7j: -2.033333333333333
      1m: -2.033333333333333
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T08:59:16.596655+00:00'
  news_construction_infra:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: 'Signaux contradictoires : tarif US sur Brésil (SHORT) vs
      PMI chinois solides (LONG) et tensions géopolitiques (LONG offre). Prix en hausse
      récente (+3.3% sur 5j) suggère que le marché a déjà intégré les facteurs haussiers,
      neutralisant le biais net.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 2.7666666666666666
      7j: 2.7666666666666666
      1m: 2.7666666666666666
  ratio_cuivre_or:
    valeur: 0.0014599778877349941
    valeur_normalisee: 0.9654765625698423
    valeur_ponderee: 0.9654765625698423
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.74681
    valeur_normalisee: 0.5128350638136321
    valeur_ponderee: 0.5128350638136321
    ts: '2026-06-02T08:59:16.596655+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T08:59:16.596655+00:00'
  sox_trend_5j:
    valeur: 571.92999
    valeur_normalisee: 0.8877929217199515
    valeur_ponderee: 0.8877929217199515
    ts: '2026-06-02T08:59:16.596655+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Nvidia PC chip,
      Anthropic IPO, HPE AI demand) et cohérentes avec le rallye de +10% sur 20j.
      Les quelques news SHORT (Iran, régulation) sont minoritaires et ne renversent
      pas le momentum AI.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.37'
    p2_shadow_contrib_exclu:
      24h: 1.9333333333333331
      7j: 1.9333333333333331
      1m: 1.9333333333333331
  flux_etf_qqq_5j:
    valeur: 0.035120008225883126
    valeur_normalisee: 0.35922460073081663
    valeur_ponderee: 0.35922460073081663
    ts: '2026-06-02T08:59:16.596655+00:00'
  spread_nasdaq_russell2000:
    valeur: 453.75998000000004
    valeur_normalisee: 0.9414930191721986
    valeur_ponderee: 0.9414930191721986
    ts: '2026-06-02T08:59:16.596655+00:00'
  rsi_14j_ixic:
    valeur: 78.6749097386528
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T08:59:16.596655+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T08:59:16.596655+00:00'
  flux_etf_or_5j:
    valeur: -0.0061862644099786035
    valeur_normalisee: 0.04867063187236333
    valeur_ponderee: 0.04867063187236333
    ts: '2026-06-02T08:59:16.596655+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Dominance de news géopolitiques LONG (frappes US-Iran, escalade
      Israël-Liban) à matérialité high et fraîcheur récente, malgré des signaux SHORT
      plus anciens liés aux taux et espoirs de paix. Le prix -3.42%/20j est contredit
      par l'escalade des 48h, justifiant une conviction haute.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.37'
    p2_shadow_contrib_exclu:
      24h: 18.4
      7j: 18.4
      1m: 18.4
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T08:59:16.596655+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T08:59:16.596655+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T08:59:16.596655+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Escalade majeure US-Iran autour d'Ormuz et offensive israélienne
      au Liban dominent, avec matérialité high et fraîcheur récente. Malgré la baisse
      de prix de -11.86% sur 20j, les news des dernières 48h (frappes mutuelles, expansion
      au Liban) changent le régime de risque, justifiant un biais long.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.37'
    p2_shadow_contrib_exclu:
      24h: 19.2
      7j: 19.2
      1m: 19.2
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T08:59:16.596655+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Escalade majeure US-Iran autour d'Ormuz et offensive israélienne
      au Liban dominent, avec matérialité high et fraîcheur récente. Malgré la baisse
      de prix de -11.86% sur 20j, les news des dernières 48h (frappes mutuelles, expansion
      au Liban) changent le régime de risque, justifiant un biais long.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.37'
    p2_shadow_contrib_exclu:
      24h: 15.933333333333335
      7j: 15.933333333333335
      1m: 15.933333333333335
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
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-02T08:59:16.596655+00:00'
  spread_brent_wti:
    valeur: 2.4732999999999947
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
sp500:
  vix_regime:
    valeur: 23.865
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T08:59:16.596655+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-02T08:59:16.596655+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.017300533537625062
    valeur_normalisee: 0.2411352806454264
    valeur_ponderee: 0.2411352806454264
    ts: '2026-06-02T08:59:16.596655+00:00'
  rsi_14j_gspc:
    valeur: 75.89804938696159
    ts: '2026-06-02T08:59:16.596655+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T08:59:16.596655+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T08:59:16.596655+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T08:59:16.596655+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T08:59:16.596655+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T08:59:16.596655+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T08:59:16.596655+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (escalade Iran-USA,
      Israël-Liban, menaces sur Ormuz) malgré le recul du VIX de 13% sur 20j. La fraîcheur
      et la densité des événements des 48 dernières heures (frappes US-Iran, arrêt
      des négociations) créent un choc géopolitique non encore intégré par le ma
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.37'
    p2_shadow_contrib_exclu:
      24h: 16.400000000000002
      7j: 16.400000000000002
      1m: 16.400000000000002
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T08:59:16.596655+00:00'
```
