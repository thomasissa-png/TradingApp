# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-05-29T12:00:00+00:00'
argent:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-05-29T12:00:00+00:00'
    note: hors fenêtre
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-05-29T12:00:00+00:00'
    note: hors fenêtre
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    event_id: 6b208bfadc1f
    event_date: '2026-05-29T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.50'
    p2_shadow_contrib_exclu:
      24h: 0.4666666666666666
      7j: 0.4666666666666666
      1m: 0.4666666666666666
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
cac40:
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-05-29T12:00:00+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
cacao:
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-05-29T12:00:00+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: structurel
    event_id: 702f99fbaa85
    event_date: '2026-05-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.50'
    p2_shadow_contrib_exclu:
      24h: -23.30000000000003
      7j: -23.30000000000003
      1m: -23.30000000000003
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: structurel
    event_id: 702f99fbaa85
    event_date: '2026-05-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.50'
    p2_shadow_contrib_exclu:
      24h: -23.30000000000003
      7j: -23.30000000000003
      1m: -23.30000000000003
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
cafe:
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    event_id: 3903ee686cd1
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '1.50'
    p2_shadow_contrib_exclu:
      24h: 50.43333333333334
      7j: 50.43333333333334
      1m: 50.43333333333334
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-05-29T12:00:00+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-05-29T12:00:00+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.50'
    p2_shadow_contrib_exclu:
      24h: 3.0999999999999996
      7j: 3.0999999999999996
      1m: 3.0999999999999996
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.50'
    p2_shadow_contrib_exclu:
      24h: 14.499999999999996
      7j: 14.499999999999996
      1m: 14.499999999999996
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
eurusd:
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
nasdaq:
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    event_id: f03c36755e32
    event_date: '2026-05-29T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '0.50'
    p2_shadow_contrib_exclu:
      24h: 11.733333333333334
      7j: 11.733333333333334
      1m: 11.733333333333334
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
or:
  tension_geopolitique:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 49.7
      7j: 49.7
      1m: 49.7
  demande_indienne_saisonniere:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-05-29T12:00:00+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-05-29T12:00:00+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
petrole:
  tension_geopol_moyen_orient:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 50.23333333333332
      7j: 50.23333333333332
      1m: 50.23333333333332
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 61.266666666666644
      7j: 61.266666666666644
      1m: 61.266666666666644
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-05-29T12:00:00+00:00'
    note: hors fenêtre
  gate_evenement_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-05-29T12:00:00+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.18
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-05-29T12:00:00+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-05-29T12:00:00+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-05-29T12:00:00+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-05-29T12:00:00+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-05-29T12:00:00+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-05-29T12:00:00+00:00'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 45.03333333333333
      7j: 45.03333333333333
      1m: 45.03333333333333
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-05-29T12:00:00+00:00'
```
