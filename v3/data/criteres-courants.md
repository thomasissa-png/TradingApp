# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-01T19:33:19.944145+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T19:33:19.944145+00:00'
  mouvement_or_5j:
    valeur: 0.006349405909789052
    valeur_normalisee: 0.11221811335885842
    valeur_ponderee: 0.11221811335885842
    ts: '2026-06-01T19:33:19.944145+00:00'
  ratio_gold_silver:
    valeur: 59.780266867946985
    ts: '2026-06-01T19:33:19.944145+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.0014927513607592147
    valeur_normalisee: -0.10022622326056614
    valeur_ponderee: -0.10022622326056614
    ts: '2026-06-01T19:33:19.944145+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-01T19:33:19.944145+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.007753071971913439
    valeur_normalisee: 0.003918700792165313
    valeur_ponderee: 0.003918700792165313
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:33:19.944145+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21729063160967518
    valeur_normalisee: 0.10864531580483759
    valeur_ponderee: 0.10864531580483759
    ts: '2026-06-01T19:33:19.944145+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Trois news SHORT récentes, dont deux à matérialité medium
      et confiance haute, dominent le signal. La baisse de prix de -3.36% sur 20j
      confirme la pression vendeuse, sans contradiction.
    nature: ponctuel
    event_id: 60b424d3caa9
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.81'
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:33:19.944145+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-01T19:33:19.944145+00:00'
  meteo_australie_dryland:
    valeur: -0.08312920306313831
    valeur_normalisee: -0.041564601531569156
    valeur_ponderee: -0.041564601531569156
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.01462711058216537
    valeur_normalisee: -0.10427265254074511
    valeur_ponderee: -0.10427265254074511
    ts: '2026-06-01T19:33:19.944145+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.016050475979632495
    valeur_normalisee: 0.3026867968370474
    valeur_ponderee: 0.3026867968370474
    ts: '2026-06-01T19:33:19.944145+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-01T19:33:19.944145+00:00'
  rsi_14j_fchi:
    valeur: 52.18370018731938
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T19:33:19.944145+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T19:33:19.944145+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:33:19.944145+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: 5 news SHORT récentes (dont 3 du 27 mai) dominent, avec dollar
      fort et stocks ICE en hausse. Le prix a déjà baissé de 15% sur 20j, mais la
      fraîcheur et la cohérence des signaux SHORT confirment la tendance.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '11.81'
    p2_shadow_contrib_exclu:
      24h: -8.066666666666668
      7j: -8.066666666666668
      1m: -8.066666666666668
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: 5 news SHORT récentes (dont 3 du 27 mai) dominent, avec dollar
      fort et stocks ICE en hausse. Le prix a déjà baissé de 15% sur 20j, mais la
      fraîcheur et la cohérence des signaux SHORT confirment la tendance.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '11.81'
    p2_shadow_contrib_exclu:
      24h: -8.066666666666668
      7j: -8.066666666666668
      1m: -8.066666666666668
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T19:33:19.944145+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-01T19:33:19.944145+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Les news LONG (mauvaises récoltes, hausse des prix) sont contredites
      par une baisse de prix de -7.53% sur 20j, indiquant que le marché a déjà intégré
      ces informations ou que d'autres facteurs baissiers dominent. Aucune news fraîche
      à matérialité high ne justifie d'aller contre le prix.
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
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T19:33:19.944145+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: 'Les PMI chinois et sud-coréens solides, les profits industriels
      chinois élevés et l''audit Cobre Panama soutiennent la demande, tandis que les
      perturbations géopolitiques (Ormuz, Iran) sont mitigées. Le prix a baissé de
      0.61% sur 20j mais rebondi de 3.84% sur 5j, suggérant que le marché intègre
      déjà '
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
    ts: '2026-06-01T19:33:19.944145+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: 'Les PMI chinois et sud-coréens solides, les profits industriels
      chinois élevés et l''audit Cobre Panama soutiennent la demande, tandis que les
      perturbations géopolitiques (Ormuz, Iran) sont mitigées. Le prix a baissé de
      0.61% sur 20j mais rebondi de 3.84% sur 5j, suggérant que le marché intègre
      déjà '
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
    valeur: 0.0014606347708327396
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.65647
    valeur_normalisee: 0.46985816119114165
    valeur_ponderee: 0.46985816119114165
    ts: '2026-06-01T19:33:19.944145+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T19:33:19.944145+00:00'
  sox_trend_5j:
    valeur: 571.49
    valeur_normalisee: 0.8853256086492375
    valeur_ponderee: 0.8853256086492375
    ts: '2026-06-01T19:33:19.944145+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Nvidia AI chip,
      Arm PC, Anthropic IPO) alignées avec le rallye récent (+10.3% sur 20j). Les
      rares news SHORT (restrictions US, bulle dotcom) sont minoritaires et sans matérialité
      suffisante pour inverser le signal.
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
    valeur: 0.036304625144371716
    valeur_normalisee: 0.37987976235668613
    valeur_ponderee: 0.37987976235668613
    ts: '2026-06-01T19:33:19.944145+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.19000000000005
    valeur_normalisee: 0.9465195944594701
    valeur_ponderee: 0.9465195944594701
    ts: '2026-06-01T19:33:19.944145+00:00'
  rsi_14j_ixic:
    valeur: 78.89362334592738
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T19:33:19.944145+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-01T19:33:19.944145+00:00'
  flux_etf_or_5j:
    valeur: -0.005400922976151024
    valeur_normalisee: 0.05858710146471818
    valeur_ponderee: 0.05858710146471818
    ts: '2026-06-01T19:33:19.944145+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (escalade US-Iran, Israël-Liban) dominent les quelques news SHORT plus anciennes
      ou de moindre matérialité. Le recul de -4.88% sur 20j est contredit par la concentration
      de news géopolitiques très récentes, justifiant un biais LONG ma
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 17.700000000000003
      7j: 17.700000000000003
      1m: 17.700000000000003
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T19:33:19.944145+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:33:19.944145+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T19:33:19.944145+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (frappes US-Iran,
      escalade Israël-Liban) malgré quelques signaux SHORT (baisse prix saoudien,
      espoirs cessez-le-feu). Le prix a baissé de 11% sur 20j, mais la concentration
      de news LONG très récentes (1er juin) suggère un changement de régime non encore
      in
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 18.5
      7j: 18.5
      1m: 18.5
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-01T19:33:19.944145+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (frappes US-Iran,
      escalade Israël-Liban) malgré quelques signaux SHORT (baisse prix saoudien,
      espoirs cessez-le-feu). Le prix a baissé de 11% sur 20j, mais la concentration
      de news LONG très récentes (1er juin) suggère un changement de régime non encore
      in
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 15.233333333333334
      7j: 15.233333333333334
      1m: 15.233333333333334
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-01T19:33:19.944145+00:00'
  spread_brent_wti:
    valeur: 2.7615869999999916
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
sp500:
  vix_regime:
    valeur: 23.69
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T19:33:19.944145+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-01T19:33:19.944145+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.01835334721375803
    valeur_normalisee: 0.2659346232189451
    valeur_ponderee: 0.2659346232189451
    ts: '2026-06-01T19:33:19.944145+00:00'
  rsi_14j_gspc:
    valeur: 76.2437977490757
    ts: '2026-06-01T19:33:19.944145+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-01T19:33:19.944145+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-01T19:33:19.944145+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-01T19:33:19.944145+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-01T19:33:19.944145+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-01T19:33:19.944145+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T19:33:19.944145+00:00'
    synthese_rationale: Plus de 25 news de matérialité haute et fraîcheur immédiate
      (1er juin) signalent une escalade majeure au Moyen-Orient (frappes US-Iran,
      offensive Israël-Liban, menace sur Ormuz), dominant largement une seule news
      SHORT de faible matérialité. Malgré la baisse récente du VIX, la concentration
      et la fo
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.81'
    p2_shadow_contrib_exclu:
      24h: 15.700000000000001
      7j: 15.700000000000001
      1m: 15.700000000000001
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-01T19:33:19.944145+00:00'
```
