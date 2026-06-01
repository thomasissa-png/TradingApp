# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-01T18:39:35.399681+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T18:39:35.399681+00:00'
  mouvement_or_5j:
    valeur: 0.006856681138938114
    valeur_normalisee: 0.12321545216540201
    valeur_ponderee: 0.12321545216540201
    ts: '2026-06-01T18:39:35.399681+00:00'
  ratio_gold_silver:
    valeur: 59.72003787245507
    ts: '2026-06-01T18:39:35.399681+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.000589524551645626
    valeur_normalisee: -0.08872509000952711
    valeur_ponderee: -0.08872509000952711
    ts: '2026-06-01T18:39:35.399681+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-01T18:39:35.399681+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.00599765944997066
    valeur_normalisee: 0.015019465419554122
    valeur_ponderee: 0.015019465419554122
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:39:35.399681+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21729063160967518
    valeur_normalisee: 0.10864531580483759
    valeur_ponderee: 0.10864531580483759
    ts: '2026-06-01T18:39:35.399681+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Trois news SHORT récentes (dont deux à matérialité medium)
      confirment la baisse des prix, avec des inquiétudes sur les récoltes et des
      pressions externes. Le prix a déjà baissé de 3.33% sur 20j, ce qui réduit la
      conviction à medium.
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:39:35.399681+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-01T18:39:35.399681+00:00'
  meteo_australie_dryland:
    valeur: -0.08312920306313831
    valeur_normalisee: -0.041564601531569156
    valeur_ponderee: -0.041564601531569156
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T18:39:35.399681+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.015136739887062767
    valeur_normalisee: -0.11669895307589298
    valeur_ponderee: -0.11669895307589298
    ts: '2026-06-01T18:39:35.399681+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.01616116891742303
    valeur_normalisee: 0.30444609742504375
    valeur_ponderee: 0.30444609742504375
    ts: '2026-06-01T18:39:35.399681+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-01T18:39:35.399681+00:00'
  rsi_14j_fchi:
    valeur: 52.18370018731938
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T18:39:35.399681+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T18:39:35.399681+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:39:35.399681+00:00'
    note: hors fenêtre
  eudr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Trois news SHORT récentes (dollar fort, stocks ICE) confirment
      la baisse de -15% sur 20j, mais le prix a déjà intégré ce biais, abaissant la
      conviction.
  maladies_cabosses:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Trois news SHORT récentes (dollar fort, stocks ICE) confirment
      la baisse de -15% sur 20j, mais le prix a déjà intégré ce biais, abaissant la
      conviction.
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T18:39:35.399681+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-01T18:39:35.399681+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Les news LONG (mauvaises récoltes, hausse des prix) sont contredites
      par une baisse de prix de -7.57% sur 20j, indiquant que le marché a déjà intégré
      ces facteurs ou les juge insuffisants. Aucune news fraîche à matérialité high
      ne justifie un renversement.
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T18:39:35.399681+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: 'Signaux contradictoires : PMI chinois et profits industriels
      haussiers (LONG) mais conflit Moyen-Orient et ralentissement demande chinoise
      (SHORT). Prix récent -0.63% sur 20j suggère que le marché a déjà intégré les
      tensions, malgré le rebond 5j. Pas de signal dominant clair.'
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T18:39:35.399681+00:00'
  news_construction_infra:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: 'Signaux contradictoires : PMI chinois et profits industriels
      haussiers (LONG) mais conflit Moyen-Orient et ralentissement demande chinoise
      (SHORT). Prix récent -0.63% sur 20j suggère que le marché a déjà intégré les
      tensions, malgré le rebond 5j. Pas de signal dominant clair.'
  ratio_cuivre_or:
    valeur: 0.001459294531311046
    valeur_normalisee: 0.9995312656137653
    valeur_ponderee: 0.9995312656137653
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.6483
    valeur_normalisee: 0.46590874457124304
    valeur_ponderee: 0.46590874457124304
    ts: '2026-06-01T18:39:35.399681+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
nasdaq:
  sox_trend_5j:
    valeur: 574.5
    valeur_normalisee: 0.9021813854500393
    valeur_ponderee: 0.9021813854500393
    ts: '2026-06-01T18:39:35.399681+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Nvidia AI chip,
      Arm PC, Anthropic IPO) cohérentes avec le rallye récent (+10.46% sur 20j). Les
      rares news SHORT (restrictions US, Powell) sont minoritaires et ne contredisent
      pas le momentum.
  flux_etf_qqq_5j:
    valeur: 0.037252307529958006
    valeur_normalisee: 0.3963817287235949
    valeur_ponderee: 0.3963817287235949
    ts: '2026-06-01T18:39:35.399681+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.29999999999995
    valeur_normalisee: 0.9478045726313782
    valeur_ponderee: 0.9478045726313782
    ts: '2026-06-01T18:39:35.399681+00:00'
  rsi_14j_ixic:
    valeur: 79.06538836098176
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T18:39:35.399681+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-01T18:39:35.399681+00:00'
  flux_etf_or_5j:
    valeur: -0.00497803380750006
    valeur_normalisee: 0.06392646738120741
    valeur_ponderee: 0.06392646738120741
    ts: '2026-06-01T18:39:35.399681+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (frappes US-Iran,
      escalade Israël-Liban) malgré des signaux SHORT sur les taux et la diplomatie.
      La fraîcheur et la cohérence des news géopolitiques l'emportent, et la baisse
      récente de -4.84% sur 20j est contredite par l'escalade du jour, justifiant
      une c
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T18:39:35.399681+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:39:35.399681+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:39:35.399681+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: 'Escalade militaire majeure autour du détroit d''Ormuz et
      expansion israélienne au Liban dominent, avec de multiples news high matérialité
      LONG. Les signaux SHORT (cessez-le-feu, baisse prix saoudien) sont minoritaires
      et contestés. Malgré la baisse de -11% sur 20j, la fraîcheur et la matérialité
      des '
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-01T18:39:35.399681+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: 'Escalade militaire majeure autour du détroit d''Ormuz et
      expansion israélienne au Liban dominent, avec de multiples news high matérialité
      LONG. Les signaux SHORT (cessez-le-feu, baisse prix saoudien) sont minoritaires
      et contestés. Malgré la baisse de -11% sur 20j, la fraîcheur et la matérialité
      des '
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-01T18:39:35.399681+00:00'
  spread_brent_wti:
    valeur: 2.8938500000000005
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
sp500:
  vix_regime:
    valeur: 23.465
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T18:39:35.399681+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-01T18:39:35.399681+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.018829448274912064
    valeur_normalisee: 0.2771393940268435
    valeur_ponderee: 0.2771393940268435
    ts: '2026-06-01T18:39:35.399681+00:00'
  rsi_14j_gspc:
    valeur: 76.39691507639117
    ts: '2026-06-01T18:39:35.399681+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-01T18:39:35.399681+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-01T18:39:35.399681+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-01T18:39:35.399681+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-01T18:39:35.399681+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-01T18:39:35.399681+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:39:35.399681+00:00'
    synthese_rationale: Plus de 25 news de matérialité haute et fraîcheur immédiate
      (1er juin) signalent une escalade majeure au Moyen-Orient (frappes US-Iran,
      offensive Israël-Liban, menace de blocus d'Ormuz), toutes orientées LONG. Malgré
      la baisse récente du VIX (-14% sur 20j), la concentration et la force de ces
      signau
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-01T18:39:35.399681+00:00'
```
