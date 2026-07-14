# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-14T05:23:05.340538+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.8517453582824405
    valeur_ponderee: 0.8517453582824405
    ts: '2026-07-14T05:23:05.340538+00:00'
  mouvement_or_5j:
    valeur: -0.02456036137953277
    valeur_normalisee: -0.3057881062990816
    valeur_ponderee: -0.3057881062990816
    ts: '2026-07-14T05:23:05.340538+00:00'
  ratio_gold_silver:
    valeur: 69.37092535326167
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_silver:
    valeur: 25633.0
    valeur_normalisee: -0.15549669953103637
    valeur_ponderee: -0.15549669953103637
    ts: '2026-07-14T05:23:05.340538+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.0703974336125468
    valeur_normalisee: -0.3702786357503092
    valeur_ponderee: -0.3702786357503092
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_argent:
    valeur: 0.008735508026210148
    valeur_normalisee: 0.7378652449557883
    valeur_ponderee: 0.7378652449557883
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_argent:
    valeur: -0.033525802261348714
    valeur_normalisee: 0.0284827721035311
    valeur_ponderee: 0.0284827721035311
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_argent:
    valeur: -0.029662273669129324
    valeur_normalisee: -0.15785956790251704
    valeur_ponderee: -0.15785956790251704
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur: 920112000.0
    valeur_normalisee: -0.5367988110081852
    valeur_ponderee: -0.5367988110081852
    ts: '2026-07-14T05:23:05.340538+00:00'
  noaa_drought_midwest_plains:
    valeur: 0.3501135367975491
    valeur_normalisee: 0.17505676839877454
    valeur_ponderee: 0.17505676839877454
    ts: '2026-07-14T05:23:05.340538+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (USDA baisse production/stocks,
      tensions mer Noire) et fraîcheur récente, malgré une news SHORT isolée sur les
      exportations ukrainiennes. Le prix a déjà monté de +8.62% sur 20j, mais les
      news les plus récentes (13-14 juillet) restent cohérentes avec le mou
    nature: structurel
    event_id: a6306033e140
    event_date: '2026-07-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: 0.8666666666666805
      7j: 0.8666666666666805
      1m: 0.8666666666666805
  cftc_cot_wheat:
    valeur: -56842.0
    valeur_normalisee: -0.17467983163929127
    valeur_ponderee: -0.17467983163929127
    ts: '2026-07-14T05:23:05.340538+00:00'
  meteo_australie_dryland:
    valeur: 0.12955831599223924
    valeur_normalisee: 0.06477915799611962
    valeur_ponderee: 0.06477915799611962
    ts: '2026-07-14T05:23:05.340538+00:00'
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_ble:
    valeur: 0.08617561279969244
    valeur_normalisee: 0.891493757314359
    valeur_ponderee: 0.891493757314359
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_ble:
    valeur: 0.05213233050115518
    valeur_normalisee: 0.6089057100740308
    valeur_ponderee: 0.6089057100740308
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_ble:
    valeur: 0.006689021376836024
    valeur_normalisee: 0.15208148330050122
    valeur_ponderee: 0.15208148330050122
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-14T05:23:05.340538+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-07-14T05:23:05.340538+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.01077883388456391
    valeur_normalisee: -0.09409182521073665
    valeur_ponderee: -0.09409182521073665
    ts: '2026-07-14T05:23:05.340538+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.02691556327327982
    valeur_normalisee: -0.6656284154179036
    valeur_ponderee: -0.6656284154179036
    ts: '2026-07-14T05:23:05.340538+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Escalade géopolitique majeure avec fermeture du détroit d'Ormuz,
      frappes multiples et choc pétrolier dominent largement le flux d'actualités,
      malgré une légère baisse récente du CAC40.
    nature: structurel
    event_id: 52bd5e83e01d
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: -107.70000000000012
      7j: -107.70000000000012
      1m: -107.70000000000012
  rsi_14j_fchi:
    valeur: 51.51120241938983
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_cac40:
    valeur: -0.0023090831405554457
    valeur_normalisee: -0.3400411967706
    valeur_ponderee: -0.3400411967706
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.013004339357639116
    valeur_normalisee: -0.4251650012252823
    valeur_ponderee: -0.4251650012252823
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.013570197709437792
    valeur_normalisee: 0.4770639143550073
    valeur_ponderee: 0.4770639143550073
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    valeur: 0.8489372668535196
    valeur_normalisee: 0.4244686334267598
    valeur_ponderee: 0.4244686334267598
    ts: '2026-07-14T05:23:05.340538+00:00'
  hf_positioning_flux_options:
    valeur: -20051.0
    valeur_normalisee: -0.6840921342388772
    valeur_ponderee: -0.6840921342388772
    ts: '2026-07-14T05:23:05.340538+00:00'
  eudr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 45.30000000000012
      7j: 45.30000000000012
      1m: 45.30000000000012
  maladies_cabosses:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Plusieurs news high matérialité récentes (12-13 juillet) confirment
      une baisse de la récolte ivoirienne >10% due aux pluies et maladies, dominant
      les news SHORT plus anciennes. Le marché a déjà monté de 17% sur 20j, mais la
      fraîcheur et la matérialité des news LONG justifient un biais haussier maint
    nature: structurel
    event_id: 7cd99e1c470d
    event_date: '2026-07-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 45.30000000000012
      7j: 45.30000000000012
      1m: 45.30000000000012
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.17275004417396822
    valeur_normalisee: 0.12162888287633168
    valeur_ponderee: 0.12162888287633168
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.01044348202428047
    valeur_normalisee: -0.15935206666498727
    valeur_ponderee: -0.15935206666498727
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.03729077994048546
    valeur_normalisee: -0.40594993443427907
    valeur_ponderee: -0.40594993443427907
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-14T05:23:05.340538+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.35857641380619254
    valeur_normalisee: 0.17928820690309627
    valeur_ponderee: 0.17928820690309627
    ts: '2026-07-14T05:23:05.340538+00:00'
  usd_brl:
    valeur: 5.14659
    valeur_normalisee: 0.2708538903557773
    valeur_ponderee: 0.2708538903557773
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_coffee:
    valeur: 24398.0
    valeur_normalisee: -0.23079557073604987
    valeur_ponderee: -0.23079557073604987
    ts: '2026-07-14T05:23:05.340538+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: 'Signal dominant clair : 14 news LONG consécutives du 1er
      au 9 juillet, dont 6 à matérialité high et 8 à matérialité medium, toutes centrées
      sur la réévaluation du risque El Niño. La fraîcheur est bonne (dernière news
      le 9 juillet, soit 5 jours avant la date du jour). Le prix a déjà monté de +18.75% '
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 65.06666666666672
      7j: 65.06666666666672
      1m: 65.06666666666672
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
    ts: '2026-07-14T05:23:05.340538+00:00'
  meteo_vietnam_robusta:
    ts: '2026-07-14T05:23:05.340538+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-13'
    valeur: 0.2678676577849341
    valeur_normalisee: 0.13393382889246705
    valeur_ponderee: 0.13393382889246705
    reporte_cause: source réseau indisponible
  momentum_prix_20j_cafe:
    valeur: 0.18747666475420366
    valeur_normalisee: 0.6193410123204243
    valeur_ponderee: 0.6193410123204243
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.03922713902322705
    valeur_normalisee: 0.12233371318130254
    valeur_ponderee: 0.12233371318130254
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.013249068346384396
    valeur_normalisee: -0.26201922261239413
    valeur_ponderee: -0.26201922261239413
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-14T05:23:05.340538+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.4041272911590164
    valeur_normalisee: 0.2020636455795082
    valeur_ponderee: 0.2020636455795082
    ts: '2026-07-14T05:23:05.340538+00:00'
  meteo_inde_gujarat_coton:
    valeur: -0.053089691663112906
    valeur_normalisee: 0.026544845831556453
    valeur_ponderee: 0.026544845831556453
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_cotton:
    valeur: 93159.0
    valeur_normalisee: 0.6995048641586412
    valeur_ponderee: 0.6995048641586412
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_coton:
    valeur: 0.060682680151706636
    valeur_normalisee: 0.2352348919530473
    valeur_ponderee: 0.2352348919530473
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_coton:
    valeur: 0.049187161317215455
    valeur_normalisee: 0.48379213807394045
    valeur_ponderee: 0.48379213807394045
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_coton:
    valeur: 0.012673506336753126
    valeur_normalisee: 0.1967294352620185
    valeur_ponderee: 0.1967294352620185
    ts: '2026-07-14T05:23:05.340538+00:00'
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 8.866666666666667
      7j: 8.866666666666667
      1m: 8.866666666666667
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-14T05:23:05.340538+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Les exportations chinoises en juin accélèrent au rythme le
      plus rapide depuis 2021, tirées par l'IA, et l'inflation à la production atteint
      un plus haut de 4 ans, signalant une demande industrielle robuste. Malgré quelques
      signaux baissiers (IPC faible, substitution vers l'aluminium), le flux domina
    nature: structurel
    event_id: 80bd37f67f01
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '18.22'
    p2_shadow_contrib_exclu:
      24h: 6.966666666666665
      7j: 6.966666666666665
      1m: 6.966666666666665
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_copper_nets:
    valeur: 65891.0
    valeur_normalisee: 0.8617908275562549
    valeur_ponderee: 0.8617908275562549
    ts: '2026-07-14T05:23:05.340538+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: ponctuel
    event_id: a8593fd73b1a
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 26.9
      7j: 26.9
      1m: 26.9
  ratio_cuivre_or:
    valeur: 0.0015705986455453744
    valeur_normalisee: 0.9591386700986596
    valeur_ponderee: 0.9591386700986596
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.056695926778354666
    valeur_normalisee: 0.6944362476116642
    valeur_ponderee: 0.6944362476116642
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.03166764648246145
    valeur_normalisee: 0.6705775849051175
    valeur_ponderee: 0.6705775849051175
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.013577971053556182
    valeur_normalisee: 0.3474967047790178
    valeur_ponderee: 0.3474967047790178
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6107008208
    valeur_normalisee: 0.5398997157253684
    valeur_ponderee: 0.5398997157253684
    ts: '2026-07-14T05:23:05.340538+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.5134999999999996
    valeur_normalisee: 0.6349121824021942
    valeur_ponderee: 0.6349121824021942
    ts: '2026-07-14T05:23:05.340538+00:00'
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  usd_jpy_proxy_risk:
    valeur: 162.2953
    valeur_normalisee: 0.69627079742619
    valeur_ponderee: 0.69627079742619
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_eur_nets:
    valeur: -36629.0
    valeur_normalisee: -0.665237075617872
    valeur_ponderee: -0.665237075617872
    ts: '2026-07-14T05:23:05.340538+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.003160600778264966
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.0015422227285074586
    valeur_normalisee: 0.13361143766171155
    valeur_ponderee: 0.13361143766171155
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0020231922645740363
    valeur_normalisee: -0.10707777682665721
    valeur_ponderee: -0.10707777682665721
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.8517453582824405
    valeur_ponderee: 0.8517453582824405
    ts: '2026-07-14T05:23:05.340538+00:00'
  sox_trend_5j:
    valeur: 553.60999
    valeur_normalisee: 0.11090024946867856
    valeur_ponderee: 0.11090024946867856
    ts: '2026-07-14T05:23:05.340538+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16740663960725322
    valeur_normalisee: 0.6780525498003971
    valeur_ponderee: 0.6780525498003971
    ts: '2026-07-14T05:23:05.340538+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée et fraîcheur
      récente : escalade militaire US-Iran (frappes, ripostes, guerre), Fed hawkish,
      restrictions Nvidia sur la Chine. Les news LONG (TSMC, SK Hynix) sont plus anciennes
      ou de matérialité moindre, et le contexte de prix baissier (-1.53% sur 5j) con'
    nature: structurel
    event_id: eba4ec9b5ec4
    event_date: '2026-07-08T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 60.0666666666667
      7j: 60.0666666666667
      1m: 60.0666666666667
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  flux_etf_qqq_5j:
    valeur: -0.015328878346906882
    valeur_normalisee: -0.5008504153321115
    valeur_ponderee: -0.5008504153321115
    ts: '2026-07-14T05:23:05.340538+00:00'
  spread_nasdaq_russell2000:
    valeur: 418.25998000000004
    valeur_normalisee: -0.016138661433873436
    valeur_ponderee: -0.016138661433873436
    ts: '2026-07-14T05:23:05.340538+00:00'
  rsi_14j_ixic:
    valeur: 47.94880596136238
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.007502245091477011
    valeur_normalisee: -0.6003411458612314
    valeur_ponderee: -0.6003411458612314
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.01851978207923055
    valeur_normalisee: -0.5466698201998045
    valeur_ponderee: -0.5466698201998045
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.00042166591701331413
    valeur_normalisee: -0.14967232933222022
    valeur_ponderee: -0.14967232933222022
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.8517453582824405
    valeur_ponderee: 0.8517453582824405
    ts: '2026-07-14T05:23:05.340538+00:00'
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_nets:
    valeur: 183165.0
    valeur_normalisee: -0.13133631198635373
    valeur_ponderee: -0.13133631198635373
    ts: '2026-07-14T05:23:05.340538+00:00'
  flux_etf_or_5j:
    valeur: -0.039253657132389486
    valeur_normalisee: -0.5018723091530126
    valeur_ponderee: -0.5018723091530126
    ts: '2026-07-14T05:23:05.340538+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Escalade massive US-Iran avec fermeture du détroit d'Ormuz
      et frappes multiples (matérialité high, fraîcheur immédiate) domine largement
      les rares signaux SHORT anciens ou faibles. Le contexte de prix (-2.47% sur
      5j) est contredit par l'ampleur des news du jour, justifiant une conviction
      haute.
    nature: structurel
    event_id: 54b14234b281
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 215.46666666666636
      7j: 215.46666666666636
      1m: 215.46666666666636
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-14T05:23:05.340538+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_or:
    valeur: 0.005310796796744954
    valeur_normalisee: 0.9129817869876484
    valeur_ponderee: 0.9129817869876484
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_or:
    valeur: -0.02040337109307855
    valeur_normalisee: -0.09512886840770676
    valeur_ponderee: -0.09512886840770676
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_or:
    valeur: -0.02168731039292826
    valeur_normalisee: -0.37072199020317326
    valeur_ponderee: -0.37072199020317326
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-07-14T05:23:05.340538+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-10'
    valeur: 411357.0
    valeur_normalisee: -0.6144876248362549
    valeur_ponderee: -0.6144876248362549
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Escalade massive et confirmée du conflit US-Iran avec fermeture
      du détroit d'Ormuz, frappes sur pétroliers et annonce de péage de transit, créant
      un choc d'offre immédiat. Les 20+ news LONG à matérialité haute des 2 derniers
      jours dominent largement les rares signaux SHORT, et le contexte de prix ha
    nature: structurel
    event_id: 54b14234b281
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 200.9999999999999
      7j: 200.9999999999999
      1m: 200.9999999999999
  cftc_cot_crude_nets:
    valeur: 35623.0
    valeur_normalisee: 0.2108732580781409
    valeur_ponderee: 0.2108732580781409
    ts: '2026-07-14T05:23:05.340538+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: structurel
    event_id: 54b14234b281
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 210.13333333333344
      7j: 210.13333333333344
      1m: 210.13333333333344
    sign_conflict: true
    sign_conflict_details:
    - event_id: 56c74dc537b8
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: crude oil inventories
      matched_surprise: rising
      surprise_polarity: up
      title: Crude oil jumps 6% with US wholesale inventories rising 0.1% in May,
        energy shares surging, and stocks falling
    - event_id: 9eebdfb99c50
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: crude oil inventories
      matched_surprise: rise
      surprise_polarity: up
      title: Crude oil jumps 6% on supply concerns, US wholesale inventories rise
        0.1% in May
    - event_id: db8ce3bef4fa
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: crude oil inventories
      matched_surprise: rise
      surprise_polarity: up
      title: Crude oil jumps 6% amid broad market selloff; US wholesale inventories
        rise 0.1% in May
    - event_id: 19e031d6354c
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins que prévu, signalant
        une demande plus faible
    - event_id: acd93c29c552
      asset: BRENT
      rule_name: opec_production
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: opec
      matched_surprise: baisse de production
      surprise_polarity: down
      title: Arabie saoudite baisse ses prix pétroliers et OPEC+ relève ses objectifs
        de production
    - event_id: 93f789bff896
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: higher
      surprise_polarity: up
      title: US crude stocks fell 6.1M barrels in week ending June 19 despite higher
        imports and refinery runs
    - event_id: 20a6d1bce9f5
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: eia
      matched_surprise: higher
      surprise_polarity: up
      title: US crude stocks -6.1M barrels (week ending June 19) despite higher imports
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
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  cushing_stocks:
    valeur: 19614.0
    valeur_normalisee: -0.7089363198780467
    valeur_ponderee: -0.7089363198780467
    ts: '2026-07-14T05:23:05.340538+00:00'
  spread_brent_wti:
    valeur: 5.025760000000005
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.0796410526204736
    valeur_normalisee: 0.6243073456862216
    valeur_ponderee: 0.6243073456862216
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.17369234500107433
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.11707903356191274
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-14T05:23:05.340538+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.0699999999999994
    valeur_normalisee: 0.28345209590746273
    valeur_ponderee: 0.28345209590746273
    ts: '2026-07-14T05:23:05.340538+00:00'
  hy_credit_spread:
    valeur: 2.69
    valeur_normalisee: -0.6033410870717456
    valeur_ponderee: -0.6033410870717456
    ts: '2026-07-14T05:23:05.340538+00:00'
  breadth_sp_ma50:
    valeur: 0.2859564661146726
    valeur_normalisee: 0.4956070907146594
    valeur_ponderee: 0.4956070907146594
    ts: '2026-07-14T05:23:05.340538+00:00'
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.0028086065325069187
    valeur_normalisee: -0.3361808806608945
    valeur_ponderee: -0.3361808806608945
    ts: '2026-07-14T05:23:05.340538+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.85
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-14T05:23:05.340538+00:00'
  rsi_14j_gspc:
    valeur: 54.29757177713101
    ts: '2026-07-14T05:23:05.340538+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.32
    valeur_normalisee: 0.8517453582824405
    valeur_ponderee: 0.8517453582824405
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.015465693240814149
    valeur_normalisee: -0.30214748685031245
    valeur_ponderee: -0.30214748685031245
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.00457247633860125
    valeur_normalisee: -0.16410459918011666
    valeur_ponderee: -0.16410459918011666
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.005057633349674351
    valeur_normalisee: 0.036468977696684564
    valeur_ponderee: 0.036468977696684564
    ts: '2026-07-14T05:23:05.340538+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-07-14T05:23:05.340538+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-07-13'
    valeur: -0.17625317323450157
    valeur_normalisee: 0.08812658661725079
    valeur_ponderee: 0.08812658661725079
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 84.939
    valeur_normalisee: -0.2579802409826506
    valeur_ponderee: -0.2579802409826506
    ts: '2026-07-14T05:23:05.340538+00:00'
  usd_brl_sucre:
    valeur: 5.14659
    valeur_normalisee: 0.2708538903557773
    valeur_ponderee: 0.2708538903557773
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_sugar:
    valeur: -40489.0
    valeur_normalisee: -0.4108052621145078
    valeur_ponderee: -0.4108052621145078
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.03283898305084754
    valeur_normalisee: 0.35102752338778337
    valeur_ponderee: 0.35102752338778337
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_sucre:
    valeur: -0.01015228426395931
    valeur_normalisee: -0.20152647584817163
    valeur_ponderee: -0.20152647584817163
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.019114688128772594
    valeur_normalisee: -0.42852181623665614
    valeur_ponderee: -0.42852181623665614
    ts: '2026-07-14T05:23:05.340538+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 13.466666666666672
      7j: 13.466666666666672
      1m: 13.466666666666672
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  exports_bresil_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 13.466666666666672
      7j: 13.466666666666672
      1m: 13.466666666666672
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-14T05:23:05.340538+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.56
    valeur_normalisee: 0.8033065692494054
    valeur_ponderee: 0.8033065692494054
    ts: '2026-07-14T05:23:05.340538+00:00'
  dxy_trend_20j:
    valeur: 120.5046
    valeur_normalisee: 0.5495568568578492
    valeur_ponderee: 0.5495568568578492
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.001092962104951578
    valeur_normalisee: -0.3053458058783651
    valeur_ponderee: -0.3053458058783651
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.0037917980217980762
    valeur_normalisee: 0.4195398707752733
    valeur_ponderee: 0.4195398707752733
    ts: '2026-07-14T05:23:05.340538+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.0029741991146803315
    valeur_normalisee: -0.5303158683747364
    valeur_ponderee: -0.5303158683747364
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_jpy_nets:
    valeur: -125772.0
    valeur_normalisee: -0.5041385070028843
    valeur_ponderee: -0.5041385070028843
    ts: '2026-07-14T05:23:05.340538+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.9099999999999997
    valeur_normalisee: 0.6306150977589682
    valeur_ponderee: 0.6306150977589682
    ts: '2026-07-14T05:23:05.340538+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-14T05:23:05.340538+00:00'
    nature: structurel
    event_id: 2ad273c646f1
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 4.066666666666666
      7j: 4.066666666666666
      1m: 4.066666666666666
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-14T05:23:05.340538+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-14T05:23:05.340538+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-14T05:23:05.340538+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-14T05:23:05.340538+00:00'
  gap_rv_iv:
    valeur: -1.443741449801287
    ts: '2026-07-14T05:23:05.340538+00:00'
  cftc_cot_vix_nets:
    valeur: -64124.0
    valeur_normalisee: -0.23251815583135177
    valeur_ponderee: -0.23251815583135177
    ts: '2026-07-14T05:23:05.340538+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-14T05:23:05.340538+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et très récentes
      (14 juillet) sur l'escalade US-Iran et la fermeture du détroit d'Ormuz, malgré
      une baisse du VIX de -13.89% sur 20 jours. La fraîcheur et l'intensité des événements
      (frappes, blocage, péage) justifient un signal LONG fort, le marché n'ayan
    nature: structurel
    event_id: 54b14234b281
    event_date: '2026-07-14T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 221.59999999999968
      7j: 221.59999999999968
      1m: 221.59999999999968
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-14T05:23:05.340538+00:00'
```
