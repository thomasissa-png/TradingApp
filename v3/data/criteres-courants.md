# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-02T10:29:23.282210+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T10:29:23.282210+00:00'
  mouvement_or_5j:
    valeur: 0.00685414252441352
    valeur_normalisee: 0.1303690576186378
    valeur_ponderee: 0.1303690576186378
    ts: '2026-06-02T10:29:23.282210+00:00'
  ratio_gold_silver:
    valeur: 59.42678324116085
    ts: '2026-06-02T10:29:23.282210+00:00'
  alpha_argent_vs_or_5j:
    valeur: -0.00013600267455626813
    valeur_normalisee: -0.08051687050774241
    valeur_ponderee: -0.08051687050774241
    ts: '2026-06-02T10:29:23.282210+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-02T10:29:23.282210+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.010093622001170255
    valeur_normalisee: -0.010882415223491364
    valeur_ponderee: -0.010882415223491364
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T10:29:23.282210+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-02T10:29:23.282210+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21352821955197626
    valeur_normalisee: 0.10676410977598813
    valeur_ponderee: 0.10676410977598813
    ts: '2026-06-02T10:29:23.282210+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Baisse de production australienne (LONG high) contredit le
      mouvement baissier du prix (-9.59%/20j), mais les news SHORT récentes (Euronext
      à 3 semaines, pression pétrole) dominent et le marché a déjà intégré l'info
      LONG. Signal trop dispersé.
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-02T10:29:23.282210+00:00'
  meteo_australie_dryland:
    valeur: -0.06596843397984538
    valeur_normalisee: -0.03298421698992269
    valeur_ponderee: -0.03298421698992269
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T10:29:23.282210+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.013500534769797179
    valeur_normalisee: -0.07679225980550873
    valeur_ponderee: -0.07679225980550873
    ts: '2026-06-02T10:29:23.282210+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.014390081912774022
    valeur_normalisee: 0.2762766481355668
    valeur_ponderee: 0.2762766481355668
    ts: '2026-06-02T10:29:23.282210+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-02T10:29:23.282210+00:00'
  rsi_14j_fchi:
    valeur: 55.88329258119969
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T10:29:23.282210+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-02T10:29:23.282210+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-02T10:29:23.282210+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Dollar strength et hausse des stocks ICE dominent avec 5 news
      SHORT de matérialité moyenne, dont 3 récentes (27 mai). La baisse de prix de
      -10.41% sur 20j confirme le biais baissier, mais la conviction est abaissée
      à medium car le mouvement est déjà en partie pricé.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '12.44'
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
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Dollar strength et hausse des stocks ICE dominent avec 5 news
      SHORT de matérialité moyenne, dont 3 récentes (27 mai). La baisse de prix de
      -10.41% sur 20j confirme le biais baissier, mais la conviction est abaissée
      à medium car le mouvement est déjà en partie pricé.
    nature: ponctuel
    event_id: ac61cc5a9f44
    event_date: '2026-05-21T00:00:00+00:00'
    event_date_source: fallback
    freshness_days: '12.44'
    p2_shadow_contrib_exclu:
      24h: -7.600000000000003
      7j: -7.600000000000003
      1m: -7.600000000000003
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-02T10:29:23.282210+00:00'
cafe:
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-02T10:29:23.282210+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Une news SHORT high matérialité (tarif 25% Brésil) contredit
      les news LONG plus anciennes sur les récoltes, et le prix a baissé de 7.4% sur
      20j, suggérant que le marché a déjà intégré le choc tarifaire. Signal trop dispersé
      pour un biais net.
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
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Signal LONG dominant grâce aux PMI chinois solides (Caixin),
      aux bénéfices industriels chinois en forte hausse, et à la proclamation Trump
      modifiant les droits de douane sur le cuivre. Les news SHORT (tarif Brésil,
      ralentissement demande Chine) sont plus anciennes ou de moindre matérialité,
      et le pr
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.44'
    p2_shadow_contrib_exclu:
      24h: -1.3666666666666667
      7j: -1.3666666666666667
      1m: -1.3666666666666667
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T10:29:23.282210+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Signal LONG dominant grâce aux PMI chinois solides (Caixin),
      aux bénéfices industriels chinois en forte hausse, et à la proclamation Trump
      modifiant les droits de douane sur le cuivre. Les news SHORT (tarif Brésil,
      ralentissement demande Chine) sont plus anciennes ou de moindre matérialité,
      et le pr
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.44'
    p2_shadow_contrib_exclu:
      24h: 3.433333333333333
      7j: 3.433333333333333
      1m: 3.433333333333333
  ratio_cuivre_or:
    valeur: 0.0014551244791669484
    valeur_normalisee: 0.9350545979913099
    valeur_ponderee: 0.9350545979913099
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
eurusd:
  usd_jpy_proxy_risk:
    valeur: 159.72854
    valeur_normalisee: 0.5040444886903337
    valeur_ponderee: 0.5040444886903337
    ts: '2026-06-02T10:29:23.282210+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T10:29:23.282210+00:00'
  sox_trend_5j:
    valeur: 571.92999
    valeur_normalisee: 0.8877929217199515
    valeur_ponderee: 0.8877929217199515
    ts: '2026-06-02T10:29:23.282210+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (Nvidia, Anthropic,
      Alphabet) sur les deux derniers jours, confirmant le momentum IA. Les quelques
      news SHORT (géopolitiques, régulation) sont minoritaires et ne pèsent pas face
      au signal haussier massif et cohérent avec la hausse de prix récente.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.44'
    p2_shadow_contrib_exclu:
      24h: 3.4
      7j: 3.4
      1m: 3.4
  flux_etf_qqq_5j:
    valeur: 0.035120008225883126
    valeur_normalisee: 0.35922460073081663
    valeur_ponderee: 0.35922460073081663
    ts: '2026-06-02T10:29:23.282210+00:00'
  spread_nasdaq_russell2000:
    valeur: 453.75998000000004
    valeur_normalisee: 0.9414930191721986
    valeur_ponderee: 0.9414930191721986
    ts: '2026-06-02T10:29:23.282210+00:00'
  rsi_14j_ixic:
    valeur: 78.6749097386528
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.534858151064053
    valeur_ponderee: 0.534858151064053
    ts: '2026-06-02T10:29:23.282210+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-02T10:29:23.282210+00:00'
  flux_etf_or_5j:
    valeur: -0.0061862644099786035
    valeur_normalisee: 0.04867063187236333
    valeur_ponderee: 0.04867063187236333
    ts: '2026-06-02T10:29:23.282210+00:00'
  tension_geopolitique:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Les news LONG (escalade Iran/US, Liban, Ukraine) et SHORT
      (cessez-le-feu partiel, hausse des taux, pression vendeuse) se neutralisent.
      Le prix a baissé de 3.43% sur 20j, suggérant que les risques géopolitiques sont
      déjà intégrés, et les signaux récents sont contradictoires sans dominance claire.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 23.3
      7j: 23.3
      1m: 23.3
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-02T10:29:23.282210+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T10:29:23.282210+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-02T10:29:23.282210+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Escalade militaire Iran-USA et Israël-Liban domine, avec trafic
      Ormuz menacé et inflation énergie élevée, malgré signaux de paix et baisse prix
      saoudien. Le marché a déjà intégré une partie de la baisse (-11%/20j) mais les
      news fraîches de conflit actif maintiennent un biais haussier fort.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.44'
    p2_shadow_contrib_exclu:
      24h: 25.7
      7j: 25.7
      1m: 25.7
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-02T10:29:23.282210+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Escalade militaire Iran-USA et Israël-Liban domine, avec trafic
      Ormuz menacé et inflation énergie élevée, malgré signaux de paix et baisse prix
      saoudien. Le marché a déjà intégré une partie de la baisse (-11%/20j) mais les
      news fraîches de conflit actif maintiennent un biais haussier fort.
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.44'
    p2_shadow_contrib_exclu:
      24h: 23.100000000000005
      7j: 23.100000000000005
      1m: 23.100000000000005
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
    ts: '2026-06-02T10:29:23.282210+00:00'
  spread_brent_wti:
    valeur: 2.718829999999997
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
sp500:
  vix_regime:
    valeur: 23.865
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-02T10:29:23.282210+00:00'
  hy_credit_spread:
    valeur: 2.74
    valeur_normalisee: -0.5223728403290695
    valeur_ponderee: -0.5223728403290695
    ts: '2026-06-02T10:29:23.282210+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.017300533537625062
    valeur_normalisee: 0.2411352806454264
    valeur_ponderee: 0.2411352806454264
    ts: '2026-06-02T10:29:23.282210+00:00'
  rsi_14j_gspc:
    valeur: 75.89804938696159
    ts: '2026-06-02T10:29:23.282210+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-02T10:29:23.282210+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-02T10:29:23.282210+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-02T10:29:23.282210+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-02T10:29:23.282210+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-02T10:29:23.282210+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-02T10:29:23.282210+00:00'
    synthese_rationale: Majorité de news LONG (escalade Iran-US, Israël-Liban, tensions
      Ormuz) avec matérialité high, mais une news SHORT (cessez-le-feu Liban) et baisse
      du VIX de 13% sur 20j suggèrent que le marché a déjà pricé une partie du risque.
      La fraîcheur des news LONG du 2 juin (clashes Liban, attaque Ukraine) mai
    nature: structurel
    event_id: 3e132052692c
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.44'
    p2_shadow_contrib_exclu:
      24h: 21.56666666666667
      7j: 21.56666666666667
      1m: 21.56666666666667
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-02T10:29:23.282210+00:00'
```
