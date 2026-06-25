# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-25T05:23:55.966920+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.29
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  mouvement_or_5j:
    valeur: -0.03946019772810161
    valeur_normalisee: -0.6096122354562695
    valeur_ponderee: -0.6096122354562695
    ts: '2026-06-25T05:23:55.966920+00:00'
  ratio_gold_silver:
    valeur: 69.6690225330106
    ts: '2026-06-25T05:23:55.966920+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-25T05:23:55.966920+00:00'
    note: hors fenêtre
  cftc_cot_silver:
    valeur: 23563.0
    valeur_normalisee: -0.21505943525506258
    valeur_ponderee: -0.21505943525506258
    ts: '2026-06-25T05:23:55.966920+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.1831519167061051
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_argent:
    valeur: -0.15475474802416633
    valeur_normalisee: -0.6579837885217154
    valeur_ponderee: -0.6579837885217154
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_argent:
    valeur: -0.1276486271005448
    valeur_normalisee: -0.7190861930617041
    valeur_ponderee: -0.7190861930617041
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-25T05:23:55.966920+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-25T05:23:55.966920+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.4100751202679635
    valeur_normalisee: 0.20503756013398175
    valeur_ponderee: 0.20503756013398175
    ts: '2026-06-25T05:23:55.966920+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Demande de fonds de guerre iranienne et aide agricole (24
      juin, high) et rapport USDA montrant blé d'hiver en difficulté (23 juin, medium)
      dominent, malgré le dollar fort et les prévisions d'exportation ukrainienne
      haussières. Le prix a baissé de 3.23% sur 5j, ce qui tempère la conviction.
    nature: structurel
    event_id: 9aaaeca1b22b
    event_date: '2026-06-24T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -8.933333333333346
      7j: -8.933333333333346
      1m: -8.933333333333346
  cftc_cot_wheat:
    valeur: -60900.0
    valeur_normalisee: -0.23900680005286748
    valeur_ponderee: -0.23900680005286748
    ts: '2026-06-25T05:23:55.966920+00:00'
  meteo_australie_dryland:
    valeur: 0.092235955172061
    valeur_normalisee: 0.0461179775860305
    valeur_ponderee: 0.0461179775860305
    ts: '2026-06-25T05:23:55.966920+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_ble:
    valeur: 0.007766907338202289
    valeur_normalisee: 0.043512070935293454
    valeur_ponderee: 0.043512070935293454
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_ble:
    valeur: -0.030615189611447602
    valeur_normalisee: -0.33720069426200316
    valeur_ponderee: -0.33720069426200316
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-25T05:23:55.966920+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-06-25T05:23:55.966920+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.015463161317579188
    valeur_normalisee: 0.4500548744966473
    valeur_ponderee: 0.4500548744966473
    ts: '2026-06-25T05:23:55.966920+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.028175119202427323
    valeur_normalisee: -0.6639250627794109
    valeur_ponderee: -0.6639250627794109
    ts: '2026-06-25T05:23:55.966920+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-25T05:23:55.966920+00:00'
  rsi_14j_fchi:
    valeur: 57.361651550022245
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.021637788466125407
    valeur_normalisee: 0.10040380494805176
    valeur_ponderee: 0.10040380494805176
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.0001765819030976612
    valeur_normalisee: -0.20251376491407605
    valeur_ponderee: -0.20251376491407605
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-25T05:23:55.966920+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -28076.0
    valeur_normalisee: -0.8426598550925855
    valeur_ponderee: -0.8426598550925855
    ts: '2026-06-25T05:23:55.966920+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-25T05:23:55.966920+00:00'
    note: hors fenêtre
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-25T05:23:55.966920+00:00'
    nature: structurel
    event_id: e0949e4a1a58
    event_date: '2026-06-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 4.366666666666668
      7j: 4.366666666666668
      1m: 4.366666666666668
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  maladies_cabosses:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (El Niño menaçant
      récoltes, cartel cacao) et fraîcheur récente (24-25 juin). Le prix a déjà monté
      de +26.65% sur 20j, mais les news les plus récentes (craintes El Niño, pluies
      excessives) confirment et renforcent le biais haussier, justifiant une convictio
    nature: structurel
    event_id: e0949e4a1a58
    event_date: '2026-06-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 4.366666666666668
      7j: 4.366666666666668
      1m: 4.366666666666668
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.2664675182418912
    valeur_normalisee: 0.7413642279623346
    valeur_ponderee: 0.7413642279623346
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.16969264290329433
    valeur_normalisee: 0.6581483474893437
    valeur_ponderee: 0.6581483474893437
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-25T05:23:55.966920+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.33647484859011906
    valeur_normalisee: 0.16823742429505953
    valeur_ponderee: 0.16823742429505953
    ts: '2026-06-25T05:23:55.966920+00:00'
  usd_brl:
    valeur: 5.20903
    valeur_normalisee: 0.921754898172392
    valeur_ponderee: 0.921754898172392
    ts: '2026-06-25T05:23:55.966920+00:00'
  cftc_cot_coffee:
    valeur: 4710.0
    valeur_normalisee: -0.6178580667322232
    valeur_ponderee: -0.6178580667322232
    ts: '2026-06-25T05:23:55.966920+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Signal LONG dominant avec news récentes (24-23 juin) sur hausse
      des prix arabica et pluies au Brésil, renforcé par matérialité high sur El Niño
      et craintes récolte. Les news SHORT sont plus anciennes et moins fraîches, ne
      contredisent pas le momentum haussier (+12% sur 20j).
    nature: structurel
    event_id: e0949e4a1a58
    event_date: '2026-06-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 52.53333333333333
      7j: 52.53333333333333
      1m: 52.53333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-25T05:23:55.966920+00:00'
  meteo_vietnam_robusta:
    valeur: 0.014344770357353525
    valeur_normalisee: 0.0071723851786767625
    valeur_ponderee: 0.0071723851786767625
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.12063572773778164
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.04240252531441002
    valeur_normalisee: 0.5823102882959027
    valeur_ponderee: 0.5823102882959027
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-25T05:23:55.966920+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-25T05:23:55.966920+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Les news SHORT dominent en nombre et matérialité (restrictions
      chinoises, ralentissement demande), mais les news LONG récentes (IA, G7) sont
      trop faibles pour inverser la tendance. Le prix a déjà baissé de 7.87% sur 20j,
      suggérant que le marché a intégré les risques SHORT.
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 5.266666666666667
      7j: 5.266666666666667
      1m: 5.266666666666667
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-25T05:23:55.966920+00:00'
  cftc_cot_copper_nets:
    valeur: 75887.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-06-25T05:23:55.966920+00:00'
    nature: ponctuel
    event_id: 8bc646c10317
    event_date: '2026-06-16T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '9.22'
    p2_shadow_contrib_exclu:
      24h: 15.966666666666665
      7j: 15.966666666666665
      1m: 15.966666666666665
  ratio_cuivre_or:
    valeur: 0.0015020410387029974
    valeur_normalisee: 0.5816130147463041
    valeur_ponderee: 0.5816130147463041
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.0787253392817091
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.058439967970357
    valeur_normalisee: -0.8241318283371613
    valeur_ponderee: -0.8241318283371613
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-25T05:23:55.966920+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6561290583000003
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4535
    valeur_normalisee: 0.35693274039089284
    valeur_ponderee: 0.35693274039089284
    ts: '2026-06-25T05:23:55.966920+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-25T05:23:55.966920+00:00'
  usd_jpy_proxy_risk:
    valeur: 161.76027
    valeur_normalisee: 0.8340531171425922
    valeur_ponderee: 0.8340531171425922
    ts: '2026-06-25T05:23:55.966920+00:00'
  cftc_cot_eur_nets:
    valeur: 2176.0
    valeur_normalisee: -0.40666106272625974
    valeur_ponderee: -0.40666106272625974
    ts: '2026-06-25T05:23:55.966920+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.013686147223716971
    valeur_normalisee: -0.575007062867951
    valeur_ponderee: -0.575007062867951
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.008108013754822063
    valeur_normalisee: -0.39354944607174447
    valeur_ponderee: -0.39354944607174447
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-25T05:23:55.966920+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.29
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  sox_trend_5j:
    valeur: 601.5
    valeur_normalisee: 0.5989752559620649
    valeur_ponderee: 0.5989752559620649
    ts: '2026-06-25T05:23:55.966920+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16700909065323238
    valeur_normalisee: 0.48464793762089176
    valeur_ponderee: 0.48464793762089176
    ts: '2026-06-25T05:23:55.966920+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Demande massive de financement pour une guerre contre l'Iran
      (matérialité élevée, fraîche) et position hawkish de la Fed dominent, malgré
      des nouvelles positives sur l'IA (Micron, Nvidia). Le marché a déjà baissé de
      2.69% sur 20j, mais la persistance des news SHORT récentes confirme le biais
      baissie
    nature: ponctuel
    event_id: 5112d279f820
    event_date: '2026-06-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 17.366666666666667
      7j: 17.366666666666667
      1m: 17.366666666666667
  flux_etf_qqq_5j:
    valeur: -0.026361206619916255
    valeur_normalisee: -0.651909349641932
    valeur_ponderee: -0.651909349641932
    ts: '2026-06-25T05:23:55.966920+00:00'
  spread_nasdaq_russell2000:
    valeur: 413.93
    valeur_normalisee: 0.13873476600870002
    valeur_ponderee: 0.13873476600870002
    ts: '2026-06-25T05:23:55.966920+00:00'
  rsi_14j_ixic:
    valeur: 47.98179612473428
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.026921220891114928
    valeur_normalisee: -0.7431181318803118
    valeur_ponderee: -0.7431181318803118
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.014861271458898484
    valeur_normalisee: -0.5750745770526399
    valeur_ponderee: -0.5750745770526399
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-25T05:23:55.966920+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.29
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-25T05:23:55.966920+00:00'
  cftc_cot_nets:
    valeur: 174385.0
    valeur_normalisee: -0.21280652149528007
    valeur_ponderee: -0.21280652149528007
    ts: '2026-06-25T05:23:55.966920+00:00'
  flux_etf_or_5j:
    valeur: -0.07974747881196087
    valeur_normalisee: -0.9012559199271891
    valeur_ponderee: -0.9012559199271891
    ts: '2026-06-25T05:23:55.966920+00:00'
  tension_geopolitique:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: 'Signaux contradictoires : demande de guerre US vs Iran (LONG)
      mais reprise du trafic à Ormuz et hawkish Fed (SHORT). Le prix a déjà baissé
      de 7.79% sur 20j, suggérant que le marché a pricé les risques baissiers dominants.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 131.80000000000018
      7j: 131.80000000000018
      1m: 131.80000000000018
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-25T05:23:55.966920+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_or:
    valeur: -0.07772430570313404
    valeur_normalisee: -0.7279683610724135
    valeur_ponderee: -0.7279683610724135
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_or:
    valeur: -0.05146649423929506
    valeur_normalisee: -0.6654497252821383
    valeur_ponderee: -0.6654497252821383
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-25T05:23:55.966920+00:00'
petrole:
  eia_crude_surprise:
    valeur: 412134.0
    valeur_normalisee: -0.6231169994857738
    valeur_ponderee: -0.6231169994857738
    ts: '2026-06-25T05:23:55.966920+00:00'
  tension_geopol_moyen_orient:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Majorité de news SHORT à matérialité élevée (reprise trafic
      Ormuz, accord paix US-Iran, apaisement tensions) dominent les quelques signaux
      LONG, et le prix a déjà baissé de 21.5% sur 20j, confirmant le biais baissier.
    nature: structurel
    event_id: 7161db8934dd
    event_date: '2026-06-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 51.999999999999986
      7j: 51.999999999999986
      1m: 51.999999999999986
  cftc_cot_crude_nets:
    valeur: 49344.0
    valeur_normalisee: 0.509749552836747
    valeur_ponderee: 0.509749552836747
    ts: '2026-06-25T05:23:55.966920+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-06-25T05:23:55.966920+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 43.59999999999999
      7j: 43.59999999999999
      1m: 43.59999999999999
    sign_conflict: true
    sign_conflict_details:
    - event_id: 8d8d4a34f31c
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: crude inventories
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins forte que prévu
    - event_id: ddfe1eafaac5
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins forte que prévu, signal
        de demande plus faible
    - event_id: e4081bee17c1
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de brut
      matched_surprise: baisse
      surprise_polarity: down
      title: Optimisme sur la réouverture du détroit d'Ormuz, baisse des prix du brut
        et de l'essence, mais stocks bas et contraintes logistiques
    - event_id: d680e22bc9c3
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: chute
      surprise_polarity: down
      title: Les prix des biens de grande consommation ne devraient pas baisser malgré
        la chute du brut sous 80 $, en raison de stocks achetés lors du conflit au-dessus
        de 1
    - event_id: bae1728ca145
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: baisse
      surprise_polarity: down
      title: Les stocks de pétrole restent élevés malgré la baisse des prix, suggérant
        un décalage entre prix et fondamentaux
    - event_id: 5aa3a2e9d5a3
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse des stocks de brut inférieure aux prévisions, signaux de demande
        mitigés
    - event_id: 34a7e1cc4307
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: oil stocks
      matched_surprise: hausse
      surprise_polarity: up
      title: Avertissement des dirigeants pétroliers sur des stocks bas et une hausse
        des prix de l'essence cet été
    - event_id: 3d89aa578c9d
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut US en baisse, mais moins que prévu
    - event_id: 0c1807e7a1bb
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: increased
      surprise_polarity: up
      title: U.S. crude oil inventories fell for the seventh consecutive week, refineries
        increased capacity use
    - event_id: a2dbe0286308
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stockpiles
      matched_surprise: draws
      surprise_polarity: down
      title: China draws crude oil stockpiles to offset Middle East supply disruption
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
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-25T05:23:55.966920+00:00'
  cushing_stocks:
    valeur: 18957.0
    valeur_normalisee: -0.8758656777574757
    valeur_ponderee: -0.8758656777574757
    ts: '2026-06-25T05:23:55.966920+00:00'
  spread_brent_wti:
    valeur: 3.1647700000000043
    ts: '2026-06-25T05:23:55.966920+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-25T05:23:55.966920+00:00'
    note: hors fenêtre
  momentum_prix_20j_petrole:
    valeur: -0.2151533451809312
    valeur_normalisee: -0.6876613446447525
    valeur_ponderee: -0.6876613446447525
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.08621607706731027
    valeur_normalisee: -0.301343858154454
    valeur_ponderee: -0.301343858154454
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-25T05:23:55.966920+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-25T05:23:55.966920+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.03000000000000025
    valeur_normalisee: 0.13479917430763524
    valeur_ponderee: 0.13479917430763524
    ts: '2026-06-25T05:23:55.966920+00:00'
  hy_credit_spread:
    valeur: 2.71
    valeur_normalisee: -0.44111885007210977
    valeur_ponderee: -0.44111885007210977
    ts: '2026-06-25T05:23:55.966920+00:00'
  breadth_sp_ma50:
    valeur: 0.2869183389738467
    valeur_normalisee: 0.3466964137139572
    valeur_ponderee: 0.3466964137139572
    ts: '2026-06-25T05:23:55.966920+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-25T05:23:55.966920+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.022776684318188356
    valeur_normalisee: -0.7290321295318648
    valeur_ponderee: -0.7290321295318648
    ts: '2026-06-25T05:23:55.966920+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.94
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  rsi_14j_gspc:
    valeur: 45.735917980966214
    ts: '2026-06-25T05:23:55.966920+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.29
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_20j_sp500:
    valeur: -0.02311520178332227
    valeur_normalisee: -0.6879314012195709
    valeur_ponderee: -0.6879314012195709
    ts: '2026-06-25T05:23:55.966920+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.011472881698685544
    valeur_normalisee: -0.551628831516173
    valeur_ponderee: -0.551628831516173
    ts: '2026-06-25T05:23:55.966920+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-25T05:23:55.966920+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-25T05:23:55.966920+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-25T05:23:55.966920+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-25T05:23:55.966920+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-25T05:23:55.966920+00:00'
  gap_rv_iv:
    valeur: 1.3761504706332346
    ts: '2026-06-25T05:23:55.966920+00:00'
  cftc_cot_vix_nets:
    valeur: -66739.0
    valeur_normalisee: -0.27614381922396297
    valeur_ponderee: -0.27614381922396297
    ts: '2026-06-25T05:23:55.966920+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-25T05:23:55.966920+00:00'
    synthese_rationale: Multiples demandes de financement de guerre (Pentagon, White
      House) et menaces iraniennes sur Hormuz dominent, malgré quelques signaux de
      détente. Le prix VIX a baissé de 7% sur 20j mais rebondi de 5% sur 5j, suggérant
      que le marché intègre déjà le risque haussier ; la fraîcheur et la matérialité
      él
    nature: structurel
    event_id: d3773807d09c
    event_date: '2026-06-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 58.93333333333331
      7j: 58.93333333333331
      1m: 58.93333333333331
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-25T05:23:55.966920+00:00'
```
