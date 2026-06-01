# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-01T18:53:28.928821+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T18:53:28.928821+00:00'
  mouvement_or_5j:
    valeur: 0.0070201172169601644
    valeur_normalisee: 0.12675803770129074
    valeur_ponderee: 0.12675803770129074
    ts: '2026-06-01T18:53:28.928821+00:00'
  ratio_gold_silver:
    valeur: 59.61944411305748
    ts: '2026-06-01T18:53:28.928821+00:00'
  alpha_argent_vs_or_5j:
    valeur: 0.000949152323817648
    valeur_normalisee: -0.06912719353207507
    valeur_ponderee: -0.06912719353207507
    ts: '2026-06-01T18:53:28.928821+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-01T18:53:28.928821+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.0040959625511995945
    valeur_normalisee: 0.027044894125803427
    valeur_ponderee: 0.027044894125803427
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:53:28.928821+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21729063160967518
    valeur_normalisee: 0.10864531580483759
    valeur_ponderee: 0.10864531580483759
    ts: '2026-06-01T18:53:28.928821+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Trois news SHORT récentes, dont deux à matérialité medium
      et confiance haute, dominent le signal. Le prix a déjà baissé de 3.33% sur 20j,
      ce qui réduit la conviction à medium car le marché a partiellement intégré l'info.
    nature: ponctuel
    event_id: 60b424d3caa9
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.79'
  nass_crop_progress:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:53:28.928821+00:00'
    note: hors fenêtre
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-01T18:53:28.928821+00:00'
  meteo_australie_dryland:
    valeur: -0.08312920306313831
    valeur_normalisee: -0.041564601531569156
    valeur_ponderee: -0.041564601531569156
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T18:53:28.928821+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.014808163098378957
    valeur_normalisee: -0.10868765488390061
    valeur_ponderee: -0.10868765488390061
    ts: '2026-06-01T18:53:28.928821+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.0163825547930041
    valeur_normalisee: 0.3079641645185347
    valeur_ponderee: 0.3079641645185347
    ts: '2026-06-01T18:53:28.928821+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-01T18:53:28.928821+00:00'
  rsi_14j_fchi:
    valeur: 52.18370018731938
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T18:53:28.928821+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-01T18:53:28.928821+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:53:28.928821+00:00'
    note: hors fenêtre
  eudr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Trois news SHORT récentes (dollar fort, stocks ICE) confirment
      la baisse de -15% sur 20j, mais le prix a déjà intégré ce biais, abaissant la
      conviction.
    nature: ponctuel
  maladies_cabosses:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Trois news SHORT récentes (dollar fort, stocks ICE) confirment
      la baisse de -15% sur 20j, mais le prix a déjà intégré ce biais, abaissant la
      conviction.
    nature: ponctuel
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T18:53:28.928821+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-01T18:53:28.928821+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Les news LONG (mauvaises récoltes, hausse des prix) sont contredites
      par une baisse de -7.57% sur 20j, indiquant que le marché a déjà intégré ces
      facteurs ou anticipe une demande plus faible. Aucune news fraîche à matérialité
      high ne justifie un renversement.
    nature: ponctuel
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-01T18:53:28.928821+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Les PMI chinois et sud-coréen solides, les profits industriels
      chinois en forte hausse, et l'audit clé sur Cobre Panama soutiennent une demande
      robuste et des risques d'offre, malgré les tensions géopolitiques et le ralentissement
      de l'activité chinoise fin mai. Le prix a rebondi de +3.96% sur 5j, e
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.79'
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T18:53:28.928821+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Les PMI chinois et sud-coréen solides, les profits industriels
      chinois en forte hausse, et l'audit clé sur Cobre Panama soutiennent une demande
      robuste et des risques d'offre, malgré les tensions géopolitiques et le ralentissement
      de l'activité chinoise fin mai. Le prix a rebondi de +3.96% sur 5j, e
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.79'
  ratio_cuivre_or:
    valeur: 0.0014606970857002624
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.7087
    valeur_normalisee: 0.4950701385053085
    valeur_ponderee: 0.4950701385053085
    ts: '2026-06-01T18:53:28.928821+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T18:53:28.928821+00:00'
  sox_trend_5j:
    valeur: 574.28
    valeur_normalisee: 0.900951255241468
    valeur_ponderee: 0.900951255241468
    ts: '2026-06-01T18:53:28.928821+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Dominance de news LONG matérialité élevée (Nvidia AI chip,
      Arm PC, Anthropic IPO) malgré quelques signaux SHORT (Iran, restrictions US).
      Le marché haussier (+10% sur 20j) est cohérent avec le flux LONG massif et frais.
    nature: ponctuel
    event_id: 3a1ea0ee1c97
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.79'
  flux_etf_qqq_5j:
    valeur: 0.036994482175056076
    valeur_normalisee: 0.39189421034972444
    valeur_ponderee: 0.39189421034972444
    ts: '2026-06-01T18:53:28.928821+00:00'
  spread_nasdaq_russell2000:
    valeur: 453.795
    valeur_normalisee: 0.9419025667855109
    valeur_ponderee: 0.9419025667855109
    ts: '2026-06-01T18:53:28.928821+00:00'
  rsi_14j_ixic:
    valeur: 79.01893561841179
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.06
    valeur_normalisee: 0.4978077857323267
    valeur_ponderee: 0.4978077857323267
    ts: '2026-06-01T18:53:28.928821+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-01T18:53:28.928821+00:00'
  flux_etf_or_5j:
    valeur: -0.004446401709767511
    valeur_normalisee: 0.0706383247308117
    valeur_ponderee: 0.0706383247308117
    ts: '2026-06-01T18:53:28.928821+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (escalade US-Iran, Israël-Liban) dominent les quelques news SHORT plus anciennes
      ou de moindre matérialité. Le recul de -4.83% sur 20j est contredit par la concentration
      de news géopolitiques très récentes, justifiant une conviction h
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.79'
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-01T18:53:28.928821+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:53:28.928821+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-01T18:53:28.928821+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Escalade militaire US-Iran et Israël-Liban domine avec matérialité
      high et fraîcheur, malgré des signaux short dispersés (prix saoudien, cessez-le-feu).
      Le prix -11% sur 20j est contredit par ces news très récentes (≤48h) qui changent
      le régime de risque.
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.79'
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-01T18:53:28.928821+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Escalade militaire US-Iran et Israël-Liban domine avec matérialité
      high et fraîcheur, malgré des signaux short dispersés (prix saoudien, cessez-le-feu).
      Le prix -11% sur 20j est contredit par ces news très récentes (≤48h) qui changent
      le régime de risque.
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.79'
  cushing_stocks:
    valeur: 23024.0
    valeur_normalisee: -0.2331981036984469
    valeur_ponderee: -0.2331981036984469
    ts: '2026-06-01T18:53:28.928821+00:00'
  spread_brent_wti:
    valeur: 2.75582
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
sp500:
  vix_regime:
    valeur: 23.54
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-01T18:53:28.928821+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-01T18:53:28.928821+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.018722157894933922
    valeur_normalisee: 0.2746149378357638
    valeur_ponderee: 0.2746149378357638
    ts: '2026-06-01T18:53:28.928821+00:00'
  rsi_14j_gspc:
    valeur: 76.36258229489319
    ts: '2026-06-01T18:53:28.928821+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-01T18:53:28.928821+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-01T18:53:28.928821+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-01T18:53:28.928821+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-01T18:53:28.928821+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-01T18:53:28.928821+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-01T18:53:28.928821+00:00'
    synthese_rationale: Toutes les news récentes (1er juin) sont LONG, avec matérialité
      élevée et fraîcheur maximale, indiquant une escalade majeure au Moyen-Orient
      (frappes US-Iran, offensive Israël-Liban, menace sur Ormuz). Malgré la baisse
      du VIX de 14% sur 20j, la concentration et la force des signaux suggèrent un
      reto
    nature: ponctuel
    event_id: 15b7dff53af3
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.79'
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-01T18:53:28.928821+00:00'
```
