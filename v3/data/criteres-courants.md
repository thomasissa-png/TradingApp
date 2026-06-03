# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-03T10:04:07.864232+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T10:04:07.864232+00:00'
  mouvement_or_5j:
    valeur: -0.020751551942760793
    valeur_normalisee: -0.47118942522319074
    valeur_ponderee: -0.47118942522319074
    ts: '2026-06-03T10:04:07.864232+00:00'
  ratio_gold_silver:
    valeur: 60.048025172831636
    ts: '2026-06-03T10:04:07.864232+00:00'
  alpha_argent_vs_or_5j:
    valeur: 0.00442377289736573
    valeur_normalisee: -0.02038427379978828
    valeur_ponderee: -0.02038427379978828
    ts: '2026-06-03T10:04:07.864232+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-03T10:04:07.864232+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.024813539873780877
    valeur_normalisee: -0.09384042061287093
    valeur_ponderee: -0.09384042061287093
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T10:04:07.864232+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-03T10:04:07.864232+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21681542249907854
    valeur_normalisee: 0.10840771124953927
    valeur_ponderee: 0.10840771124953927
    ts: '2026-06-03T10:04:07.864232+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (Chine lève interdictions
      Brésil, baisse production Australie) vs SHORT (Euronext à 3 semaines bas, pression
      pétrole). Prix -8.5% sur 20j suggère que le biais baissier domine déjà, sans
      news fraîche high assez forte pour inverser.'
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-03T10:04:07.864232+00:00'
  meteo_australie_dryland:
    valeur: -0.03979471650292972
    valeur_normalisee: -0.01989735825146486
    valeur_ponderee: -0.01989735825146486
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T10:04:07.864232+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.007561655465863293
    valeur_normalisee: 0.060330506885334166
    valeur_ponderee: 0.060330506885334166
    ts: '2026-06-03T10:04:07.864232+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.003484364111498328
    valeur_normalisee: 0.0992604960124805
    valeur_ponderee: 0.0992604960124805
    ts: '2026-06-03T10:04:07.864232+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-03T10:04:07.864232+00:00'
  rsi_14j_fchi:
    valeur: 54.472774711111946
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T10:04:07.864232+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T10:04:07.864232+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-03T10:04:07.864232+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Majorité de news SHORT (dollar fort, inventaires ICE, offre
      abondante) dominent malgré une news LONG récente (Chine lève interdiction Brésil).
      Le prix a baissé de 3.91% sur 20j, confirmant le biais baissier, mais le rebond
      récent (+3.97% sur 5j) et la news LONG réduisent la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.42'
    p2_shadow_contrib_exclu:
      24h: -10.633333333333335
      7j: -10.633333333333335
      1m: -10.633333333333335
  maladies_cabosses:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Majorité de news SHORT (dollar fort, inventaires ICE, offre
      abondante) dominent malgré une news LONG récente (Chine lève interdiction Brésil).
      Le prix a baissé de 3.91% sur 20j, confirmant le biais baissier, mais le rebond
      récent (+3.97% sur 5j) et la news LONG réduisent la conviction.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.42'
    p2_shadow_contrib_exclu:
      24h: -10.633333333333335
      7j: -10.633333333333335
      1m: -10.633333333333335
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T10:04:07.864232+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.29223724434408876
    valeur_normalisee: -0.14611862217204438
    valeur_ponderee: -0.14611862217204438
    ts: '2026-06-03T10:04:07.864232+00:00'
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-03T10:04:07.864232+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Les news SHORT (tarifs US sur Brésil) et LONG (Chine lève
      interdiction, mauvaises récoltes) se neutralisent, avec une matérialité élevée
      mais des signaux contradictoires. Le prix en baisse de -5.82% sur 20j suggère
      que le marché a déjà intégré les risques tarifaires, réduisant la conviction.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 37.60000000000001
      7j: 37.60000000000001
      1m: 37.60000000000001
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-03T10:04:07.864232+00:00'
  meteo_vietnam_robusta:
    valeur: -0.19898874237162403
    valeur_normalisee: -0.09949437118581202
    valeur_ponderee: -0.09949437118581202
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T10:04:07.864232+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, la proclamation Trump
      sur les droits de douane cuivre, et le positionnement haussier de Citi dominent
      malgré les tarifs brésiliens et le ralentissement officiel chinois. Le prix
      a déjà intégré une partie du biais haussier (+3.27% sur 5j), ce qui limite la
      conv
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.42'
    p2_shadow_contrib_exclu:
      24h: -1.3666666666666667
      7j: -1.3666666666666667
      1m: -1.3666666666666667
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T10:04:07.864232+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Les PMI chinois et sud-coréens solides, la proclamation Trump
      sur les droits de douane cuivre, et le positionnement haussier de Citi dominent
      malgré les tarifs brésiliens et le ralentissement officiel chinois. Le prix
      a déjà intégré une partie du biais haussier (+3.27% sur 5j), ce qui limite la
      conv
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.42'
    p2_shadow_contrib_exclu:
      24h: 5.1000000000000005
      7j: 5.1000000000000005
      1m: 5.1000000000000005
  ratio_cuivre_or:
    valeur: 0.0014795647110955287
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
eurusd:
  differentiel_taux_10y_us_bund:
    valeur: 1.4736842104999996
    valeur_normalisee: 0.38479878420450014
    valeur_ponderee: 0.38479878420450014
    ts: '2026-06-03T10:04:07.864232+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.78572
    valeur_normalisee: 0.5263599654828154
    valeur_ponderee: 0.5263599654828154
    ts: '2026-06-03T10:04:07.864232+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T10:04:07.864232+00:00'
  sox_trend_5j:
    valeur: 605.02002
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T10:04:07.864232+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16322237173886453
    valeur_normalisee: -0.25483139212601846
    valeur_ponderee: -0.25483139212601846
    ts: '2026-06-03T10:04:07.864232+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Les news LONG dominent largement en nombre et matérialité
      (Alphabet 80B$ IA, HPE, Nvidia, Anthropic), malgré quelques signaux SHORT (droits
      de douane, vente d'actions Alphabet, mise en garde Barclays). Le marché a déjà
      intégré ce biais haussier (+10.89% sur 20j), ce qui limite la conviction.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.42'
    p2_shadow_contrib_exclu:
      24h: 4.333333333333333
      7j: 4.333333333333333
      1m: 4.333333333333333
  flux_etf_qqq_5j:
    valeur: 0.021745001023785404
    valeur_normalisee: 0.11391538892261004
    valeur_ponderee: 0.11391538892261004
    ts: '2026-06-03T10:04:07.864232+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.49997
    valeur_normalisee: 0.9069064768482825
    valeur_ponderee: 0.9069064768482825
    ts: '2026-06-03T10:04:07.864232+00:00'
  rsi_14j_ixic:
    valeur: 79.38409559275895
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T10:04:07.864232+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-03T10:04:07.864232+00:00'
  flux_etf_or_5j:
    valeur: -0.0049516666666665765
    valeur_normalisee: 0.07251219580773875
    valeur_ponderee: 0.07251219580773875
    ts: '2026-06-03T10:04:07.864232+00:00'
  tension_geopolitique:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Majorité de news LONG matérialité élevée sur tensions Iran/US,
      mais prix -4.47% sur 20j suggère que le marché a déjà intégré ces risques. Une
      seule news SHORT (ISM solide) ne suffit pas à inverser, mais la divergence prix/news
      abaisse la conviction.
    nature: structurel
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
    ts: '2026-06-03T10:04:07.864232+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-03T10:04:07.864232+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur: 441686.0
    valeur_normalisee: 0.37013572651064536
    valeur_ponderee: 0.37013572651064536
    ts: '2026-06-03T10:04:07.864232+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (fermeture d'Ormuz, frappes US/Iran, escalade militaire) dominent largement
      les rares signaux SHORT (demande indienne faible, subventions japonaises). Le
      rebond de +8.11% sur 5j confirme que le marché intègre ces tensions, et la baiss
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.42'
    p2_shadow_contrib_exclu:
      24h: 30.300000000000004
      7j: 30.300000000000004
      1m: 30.300000000000004
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-03T10:04:07.864232+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Majorité de news LONG à matérialité élevée et fraîcheur immédiate
      (fermeture d'Ormuz, frappes US/Iran, escalade militaire) dominent largement
      les rares signaux SHORT (demande indienne faible, subventions japonaises). Le
      rebond de +8.11% sur 5j confirme que le marché intègre ces tensions, et la baiss
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.42'
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
    ts: '2026-06-03T10:04:07.864232+00:00'
  spread_brent_wti:
    valeur: 2.1081999999999965
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-03T10:04:07.864232+00:00'
  hy_credit_spread:
    valeur: 2.72
    valeur_normalisee: -0.5532705134158924
    valeur_ponderee: -0.5532705134158924
    ts: '2026-06-03T10:04:07.864232+00:00'
  breadth_sp_ma50:
    valeur: 0.27652486306035173
    valeur_normalisee: -0.5652837190101652
    valeur_ponderee: -0.5652837190101652
    ts: '2026-06-03T10:04:07.864232+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.011963894591032753
    valeur_normalisee: 0.10691033734835528
    valeur_ponderee: 0.10691033734835528
    ts: '2026-06-03T10:04:07.864232+00:00'
  rsi_14j_gspc:
    valeur: 76.07291159261612
    ts: '2026-06-03T10:04:07.864232+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T10:04:07.864232+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-03T10:04:07.864232+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-03T10:04:07.864232+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-03T10:04:07.864232+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-03T10:04:07.864232+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-03T10:04:07.864232+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T10:04:07.864232+00:00'
    synthese_rationale: Multiples news high matérialité du 3 juin confirment une escalade
      US-Iran (frappes, fermeture d'Ormuz, blocage cessez-le-feu), signal dominant
      pour une hausse de la volatilité. Malgré la baisse récente du VIX, la fraîcheur
      et la force des news justifient un biais LONG.
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.42'
    p2_shadow_contrib_exclu:
      24h: 25.266666666666666
      7j: 25.266666666666666
      1m: 25.266666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-03T10:04:07.864232+00:00'
```
