# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-03T05:03:52.059184+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T05:03:52.059184+00:00'
  mouvement_or_5j:
    valeur: -0.01558281747644441
    valeur_normalisee: -0.3599026636564093
    valeur_ponderee: -0.3599026636564093
    ts: '2026-06-03T05:03:52.059184+00:00'
  ratio_gold_silver:
    valeur: 59.86324789644915
    ts: '2026-06-03T05:03:52.059184+00:00'
  alpha_argent_vs_or_5j:
    valeur: 0.007249526200256096
    valeur_normalisee: 0.015582697551093629
    valeur_ponderee: 0.015582697551093629
    ts: '2026-06-03T05:03:52.059184+00:00'
  cftc_cot_silver:
    valeur: 23187.0
    valeur_normalisee: -0.22660953658335586
    valeur_ponderee: -0.22660953658335586
    ts: '2026-06-03T05:03:52.059184+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.024813539873780877
    valeur_normalisee: -0.09384042061287093
    valeur_ponderee: -0.09384042061287093
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T05:03:52.059184+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-03T05:03:52.059184+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.21681542249907854
    valeur_normalisee: 0.10840771124953927
    valeur_ponderee: 0.10840771124953927
    ts: '2026-06-03T05:03:52.059184+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (Chine lève interdictions
      Brésil, baisse production Australie) vs SHORT (Euronext à 3 semaines, pression
      pétrole). Prix -9% sur 20j suggère que le marché a déjà intégré les éléments
      baissiers, sans signal frais dominant.'
    nature: structurel
  cftc_cot_wheat:
    valeur: -11805.0
    valeur_normalisee: 0.39116175756839955
    valeur_ponderee: 0.39116175756839955
    ts: '2026-06-03T05:03:52.059184+00:00'
  meteo_australie_dryland:
    valeur: -0.03979471650292972
    valeur_normalisee: -0.01989735825146486
    valeur_ponderee: -0.01989735825146486
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T05:03:52.059184+00:00'
cac40:
  alpha_cac_vs_sp_5j:
    valeur: -0.007561655465863293
    valeur_normalisee: 0.060330506885334166
    valeur_ponderee: 0.060330506885334166
    ts: '2026-06-03T05:03:52.059184+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.003484364111498328
    valeur_normalisee: 0.0992604960124805
    valeur_ponderee: 0.0992604960124805
    ts: '2026-06-03T05:03:52.059184+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-03T05:03:52.059184+00:00'
  rsi_14j_fchi:
    valeur: 56.274953399816965
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T05:03:52.059184+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.16485467595528494
    valeur_normalisee: 0.08242733797764247
    valeur_ponderee: 0.08242733797764247
    ts: '2026-06-03T05:03:52.059184+00:00'
  hf_positioning_flux_options:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T05:03:52.059184+00:00'
  cftc_cot_cocoa:
    valeur: -22106.0
    valeur_normalisee: -0.7587526502316438
    valeur_ponderee: -0.7587526502316438
    ts: '2026-06-03T05:03:52.059184+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-03T05:03:52.059184+00:00'
    note: hors fenêtre
  eudr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Majorité de news SHORT (dollar fort, stocks ICE, offre abondante)
      dominent malgré une news LONG récente (Chine lève interdiction Brésil). Le prix
      a baissé de 2.66% sur 20j mais rebondi de 5.31% sur 5j, suggérant que le marché
      a partiellement intégré le biais SHORT.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.21'
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
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Majorité de news SHORT (dollar fort, stocks ICE, offre abondante)
      dominent malgré une news LONG récente (Chine lève interdiction Brésil). Le prix
      a baissé de 2.66% sur 20j mais rebondi de 5.31% sur 5j, suggérant que le marché
      a partiellement intégré le biais SHORT.
    nature: structurel
    event_id: 64803a61de8a
    event_date: '2026-06-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.21'
    p2_shadow_contrib_exclu:
      24h: -9.966666666666669
      7j: -9.966666666666669
      1m: -9.966666666666669
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T05:03:52.059184+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.29223724434408876
    valeur_normalisee: -0.14611862217204438
    valeur_ponderee: -0.14611862217204438
    ts: '2026-06-03T05:03:52.059184+00:00'
  cftc_cot_coffee:
    valeur: 14841.0
    valeur_normalisee: -0.43646054495256226
    valeur_ponderee: -0.43646054495256226
    ts: '2026-06-03T05:03:52.059184+00:00'
  maladies_cabosses_rouille:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Les news SHORT (tarifs US sur Brésil) et LONG (Chine lève
      interdiction, mauvaises récoltes) se neutralisent, et le prix en baisse de 5.7%
      sur 20j suggère que le marché a déjà intégré les risques tarifaires.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 37.10000000000001
      7j: 37.10000000000001
      1m: 37.10000000000001
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-03T05:03:52.059184+00:00'
  meteo_vietnam_robusta:
    valeur: -0.19898874237162403
    valeur_normalisee: -0.09949437118581202
    valeur_ponderee: -0.09949437118581202
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-03T05:03:52.059184+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Dominance de news LONG récentes (PMI chinois, Citi haussier,
      Trump modifiant droits de douane sur cuivre) malgré quelques SHORT (tarifs Brésil,
      PMI officiel chinois faible). Le prix a déjà monté de +4% sur 5j, ce qui limite
      la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.21'
    p2_shadow_contrib_exclu:
      24h: -0.7000000000000001
      7j: -0.7000000000000001
      1m: -0.7000000000000001
  cftc_cot_copper_nets:
    valeur: 73313.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T05:03:52.059184+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Dominance de news LONG récentes (PMI chinois, Citi haussier,
      Trump modifiant droits de douane sur cuivre) malgré quelques SHORT (tarifs Brésil,
      PMI officiel chinois faible). Le prix a déjà monté de +4% sur 5j, ce qui limite
      la conviction.
    nature: structurel
    event_id: 1c3cc2f34353
    event_date: '2026-05-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.21'
    p2_shadow_contrib_exclu:
      24h: 5.7666666666666675
      7j: 5.7666666666666675
      1m: 5.7666666666666675
  ratio_cuivre_or:
    valeur: 0.0014820683251225055
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
eurusd:
  differentiel_taux_10y_us_bund:
    valeur: 1.4736842104999996
    valeur_normalisee: 0.38479878420450014
    valeur_ponderee: 0.38479878420450014
    ts: '2026-06-03T05:03:52.059184+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.8917
    valeur_normalisee: 0.576838398131796
    valeur_ponderee: 0.576838398131796
    ts: '2026-06-03T05:03:52.059184+00:00'
  cftc_cot_eur_nets:
    valeur: -3756.0
    valeur_normalisee: -0.45320534828572134
    valeur_ponderee: -0.45320534828572134
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T05:03:52.059184+00:00'
  sox_trend_5j:
    valeur: 605.02002
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-03T05:03:52.059184+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16322237173886453
    valeur_normalisee: -0.25483139212601846
    valeur_ponderee: -0.25483139212601846
    ts: '2026-06-03T05:03:52.059184+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîche (Alphabet
      80B$, HPE, Nvidia, Anthropic) malgré quelques news SHORT (droits de douane,
      Fed). Le marché confirme avec +10.89% sur 20j.
    nature: ponctuel
    event_id: d4c06b4ad629
    event_date: '2026-06-02T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.21'
    p2_shadow_contrib_exclu:
      24h: 4.333333333333333
      7j: 4.333333333333333
      1m: 4.333333333333333
  flux_etf_qqq_5j:
    valeur: 0.021745001023785404
    valeur_normalisee: 0.11391538892261004
    valeur_ponderee: 0.11391538892261004
    ts: '2026-06-03T05:03:52.059184+00:00'
  spread_nasdaq_russell2000:
    valeur: 454.49997
    valeur_normalisee: 0.9069064768482825
    valeur_ponderee: 0.9069064768482825
    ts: '2026-06-03T05:03:52.059184+00:00'
  rsi_14j_ixic:
    valeur: 79.38409559275895
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T05:03:52.059184+00:00'
  cftc_cot_nets:
    valeur: 149660.0
    valeur_normalisee: -0.4324147600823245
    valeur_ponderee: -0.4324147600823245
    ts: '2026-06-03T05:03:52.059184+00:00'
  flux_etf_or_5j:
    valeur: -0.0049516666666665765
    valeur_normalisee: 0.07251219580773875
    valeur_ponderee: 0.07251219580773875
    ts: '2026-06-03T05:03:52.059184+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Multiples news high matérialité du 3 juin confirment une escalade
      US-Iran avec fermeture d'Ormuz et blocage du cessez-le-feu, dominant les quelques
      signaux baissiers plus anciens ou de moindre matérialité. Le recul récent du
      prix (-3.94% sur 20j) est contredit par cette vague de nouvelles très fraîc
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
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
    ts: '2026-06-03T05:03:52.059184+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-03T05:03:52.059184+00:00'
    note: hors fenêtre
  api_weekly_surprise:
    valeur: 441686.0
    valeur_normalisee: 0.37013572651064536
    valeur_ponderee: 0.37013572651064536
    ts: '2026-06-03T05:03:52.059184+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée et fraîche (03/06)
      sur l''escalade Iran-US et la fermeture d''Ormuz, dominant les rares signaux
      SHORT plus anciens ou de moindre matérialité. Le rebond de +6.14% sur 5j confirme
      que le marché intègre déjà la prime de risque, mais la fraîcheur et la force
      des '
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
    p2_shadow_contrib_exclu:
      24h: 30.76666666666667
      7j: 30.76666666666667
      1m: 30.76666666666667
  cftc_cot_crude_nets:
    valeur: 10418.0
    valeur_normalisee: -0.3018487738051978
    valeur_ponderee: -0.3018487738051978
    ts: '2026-06-03T05:03:52.059184+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: 'Majorité de news LONG à matérialité élevée et fraîche (03/06)
      sur l''escalade Iran-US et la fermeture d''Ormuz, dominant les rares signaux
      SHORT plus anciens ou de moindre matérialité. Le rebond de +6.14% sur 5j confirme
      que le marché intègre déjà la prime de risque, mais la fraîcheur et la force
      des '
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
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
    ts: '2026-06-03T05:03:52.059184+00:00'
  spread_brent_wti:
    valeur: 2.224221
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-03T05:03:52.059184+00:00'
  hy_credit_spread:
    valeur: 2.72
    valeur_normalisee: -0.5532705134158924
    valeur_ponderee: -0.5532705134158924
    ts: '2026-06-03T05:03:52.059184+00:00'
  breadth_sp_ma50:
    valeur: 0.27652486306035173
    valeur_normalisee: -0.5652837190101652
    valeur_ponderee: -0.5652837190101652
    ts: '2026-06-03T05:03:52.059184+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.011963894591032753
    valeur_normalisee: 0.10691033734835528
    valeur_ponderee: 0.10691033734835528
    ts: '2026-06-03T05:03:52.059184+00:00'
  rsi_14j_gspc:
    valeur: 76.07291159261612
    ts: '2026-06-03T05:03:52.059184+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.07
    valeur_normalisee: 0.5210421719417608
    valeur_ponderee: 0.5210421719417608
    ts: '2026-06-03T05:03:52.059184+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-03T05:03:52.059184+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-03T05:03:52.059184+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-03T05:03:52.059184+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-03T05:03:52.059184+00:00'
  cftc_cot_vix_nets:
    valeur: -54484.0
    valeur_normalisee: -0.04167689259523477
    valeur_ponderee: -0.04167689259523477
    ts: '2026-06-03T05:03:52.059184+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-03T05:03:52.059184+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée sur les tensions
      US-Iran et la fermeture d'Ormuz, malgré le recul du VIX de -15% sur 20j. La
      fraîcheur et la matérialité des news du 3 juin (frappes, représailles, cessez-le-feu
      bloqué) indiquent une escalade non encore intégrée par le marché, justifiant
      u
    nature: structurel
    event_id: f9ec3fe339c2
    event_date: '2026-06-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.21'
    p2_shadow_contrib_exclu:
      24h: 25.266666666666666
      7j: 25.266666666666666
      1m: 25.266666666666666
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-03T05:03:52.059184+00:00'
```
