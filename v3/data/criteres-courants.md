# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-23T05:23:51.909406+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 0.8546168826218449
    valeur_ponderee: 0.8546168826218449
    ts: '2026-06-23T05:23:51.909406+00:00'
  mouvement_or_5j:
    valeur: -0.01932144338355757
    valeur_normalisee: -0.18910498534582593
    valeur_ponderee: -0.18910498534582593
    ts: '2026-06-23T05:23:51.909406+00:00'
  ratio_gold_silver:
    valeur: 65.76546751723393
    ts: '2026-06-23T05:23:51.909406+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-23T05:23:51.909406+00:00'
    note: hors fenêtre
  cftc_cot_silver:
    valeur: 23563.0
    valeur_normalisee: -0.21505943525506258
    valeur_ponderee: -0.21505943525506258
    ts: '2026-06-23T05:23:51.909406+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.03883178332517545
    valeur_normalisee: -0.18631805493282835
    valeur_ponderee: -0.18631805493282835
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_argent:
    valeur: -0.1370262478850367
    valeur_normalisee: -0.6233177081423015
    valeur_ponderee: -0.6233177081423015
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_argent:
    valeur: -0.10376377892496269
    valeur_normalisee: -0.6043962075740498
    valeur_ponderee: -0.6043962075740498
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-23T05:23:51.909406+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-23T05:23:51.909406+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.39228733892257533
    valeur_normalisee: 0.19614366946128767
    valeur_ponderee: 0.19614366946128767
    ts: '2026-06-23T05:23:51.909406+00:00'
  geopolitique_mer_noire:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: Multiples confirmations USDA d'exportations ukrainiennes élevées
      et dollar fort pèsent sur le blé, tandis que les news LONG (El Niño, conflits)
      sont anciennes ou peu spécifiques au blé. Le prix baisse déjà, confirmant le
      biais SHORT.
    nature: structurel
    event_id: 49df59e55c60
    event_date: '2026-06-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -5.233333333333336
      7j: -5.233333333333336
      1m: -5.233333333333336
  cftc_cot_wheat:
    valeur: -60900.0
    valeur_normalisee: -0.23900680005286748
    valeur_ponderee: -0.23900680005286748
    ts: '2026-06-23T05:23:51.909406+00:00'
  meteo_australie_dryland:
    valeur: 0.08903363659139567
    valeur_normalisee: 0.044516818295697834
    valeur_ponderee: 0.044516818295697834
    ts: '2026-06-23T05:23:51.909406+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_ble:
    valeur: -0.013352469082343554
    valeur_normalisee: -0.12466312676575673
    valeur_ponderee: -0.12466312676575673
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_ble:
    valeur: -0.0021206055387607003
    valeur_normalisee: -0.047873933286829186
    valeur_ponderee: -0.047873933286829186
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-23T05:23:51.909406+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-06-23T05:23:51.909406+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.002337254951896295
    valeur_normalisee: 0.1627853366466225
    valeur_ponderee: 0.1627853366466225
    ts: '2026-06-23T05:23:51.909406+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.03024453024453022
    valeur_normalisee: -0.7172944295396161
    valeur_ponderee: -0.7172944295396161
    ts: '2026-06-23T05:23:51.909406+00:00'
  tension_politique_fr:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: none
    ts: '2026-06-23T05:23:51.909406+00:00'
  rsi_14j_fchi:
    valeur: 59.79015311255406
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.017176812542916586
    valeur_normalisee: 0.07978888624617013
    valeur_ponderee: 0.07978888624617013
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.0243037941250559
    valeur_normalisee: 0.30822614709696367
    valeur_ponderee: 0.30822614709696367
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
cacao:
  hf_positioning_flux_options:
    valeur: -28076.0
    valeur_normalisee: -0.8426598550925855
    valeur_ponderee: -0.8426598550925855
    ts: '2026-06-23T05:23:51.909406+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-23T05:23:51.909406+00:00'
    note: hors fenêtre
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-23T05:23:51.909406+00:00'
    nature: structurel
    event_id: 45bb3b93b62d
    event_date: '2026-06-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: -8.733333333333308
      7j: -8.733333333333308
      1m: -8.733333333333308
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
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée (cartel cacao,
      El Niño) et fraîcheur récente, malgré une news SHORT isolée. Le prix a déjà
      monté de +13.43% sur 20j, mais les news les plus récentes (Super El Niño) confirment
      le biais haussier.
    nature: structurel
    event_id: 45bb3b93b62d
    event_date: '2026-06-18T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: -8.733333333333308
      7j: -8.733333333333308
      1m: -8.733333333333308
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.1342532161506893
    valeur_normalisee: 0.24836193687337565
    valeur_ponderee: 0.24836193687337565
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.09252234603263099
    valeur_normalisee: 0.3002631758085077
    valeur_ponderee: 0.3002631758085077
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-23T05:23:51.909406+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.33607985614802943
    valeur_normalisee: 0.16803992807401472
    valeur_ponderee: 0.16803992807401472
    ts: '2026-06-23T05:23:51.909406+00:00'
  usd_brl:
    valeur: 5.15891
    valeur_normalisee: 0.7193085892998572
    valeur_ponderee: 0.7193085892998572
    ts: '2026-06-23T05:23:51.909406+00:00'
  cftc_cot_coffee:
    valeur: 4710.0
    valeur_normalisee: -0.6178580667322232
    valeur_ponderee: -0.6178580667322232
    ts: '2026-06-23T05:23:51.909406+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: Les news LONG dominent en nombre et matérialité (El Niño,
      hausse des prix, +5.2% Arabica), mais les news SHORT récentes (ver à vis, indice
      mondial en baisse) et le prix déjà en hausse (+3.08%/20j) limitent la conviction.
    nature: structurel
    event_id: 44cda448037a
    event_date: '2026-06-16T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 50.2
      7j: 50.2
      1m: 50.2
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-23T05:23:51.909406+00:00'
  meteo_vietnam_robusta:
    valeur: 0.0030725591083069453
    valeur_normalisee: 0.0015362795541534727
    valeur_ponderee: 0.0015362795541534727
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.030756532426085004
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.02371056959842488
    valeur_normalisee: -0.18209723591056903
    valeur_ponderee: -0.18209723591056903
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-23T05:23:51.909406+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-23T05:23:51.909406+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée (restrictions
      commerciales Chine/US, faiblesse consommation chinoise) et récentes (22-23 juin),
      renforcées par la baisse des ventes au détail chinoises. Le prix a déjà baissé
      de 5.99% sur 20j, mais la fraîcheur et la matérialité des news SHORT justifient '
    nature: structurel
    event_id: 189e61c692f2
    event_date: '2026-06-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 3.5666666666666664
      7j: 3.5666666666666664
      1m: 3.5666666666666664
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-23T05:23:51.909406+00:00'
  cftc_cot_copper_nets:
    valeur: 75887.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-23T05:23:51.909406+00:00'
  news_construction_infra:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-06-23T05:23:51.909406+00:00'
    nature: ponctuel
    event_id: 8bc646c10317
    event_date: '2026-06-16T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 17.56666666666667
      7j: 17.56666666666667
      1m: 17.56666666666667
  ratio_cuivre_or:
    valeur: 0.001515130379801807
    valeur_normalisee: 0.6887872182058232
    valeur_ponderee: 0.6887872182058232
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.059859959473029134
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.03301941490883176
    valeur_normalisee: -0.5436201178956029
    valeur_ponderee: -0.5436201178956029
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6356243189000006
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-23T05:23:51.909406+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.4135
    valeur_normalisee: 0.09732238040611642
    valeur_ponderee: 0.09732238040611642
    ts: '2026-06-23T05:23:51.909406+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-23T05:23:51.909406+00:00'
  usd_jpy_proxy_risk:
    valeur: 161.60795
    valeur_normalisee: 0.8504122265573927
    valeur_ponderee: 0.8504122265573927
    ts: '2026-06-23T05:23:51.909406+00:00'
  cftc_cot_eur_nets:
    valeur: 2176.0
    valeur_normalisee: -0.40666106272625974
    valeur_ponderee: -0.40666106272625974
    ts: '2026-06-23T05:23:51.909406+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.015114153676369146
    valeur_normalisee: -0.7060737288775906
    valeur_ponderee: -0.7060737288775906
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.015988008993255143
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 0.8546168826218449
    valeur_ponderee: 0.8546168826218449
    ts: '2026-06-23T05:23:51.909406+00:00'
  sox_trend_5j:
    valeur: 655.01001
    valeur_normalisee: 0.9224939923169023
    valeur_ponderee: 0.9224939923169023
    ts: '2026-06-23T05:23:51.909406+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16471305420810278
    valeur_normalisee: 0.07054968588604213
    valeur_ponderee: 0.07054968588604213
    ts: '2026-06-23T05:23:51.909406+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (Fed hawkish,
      tensions Iran/Chine, restrictions commerciales) sur les 2 derniers jours, malgré
      un plan IA Japonais et une annonce NVIDIA. Le contexte de prix haussier (+3.28%
      sur 20j) est contredit par la fraîcheur et la force des signaux baissiers, justi
    nature: ponctuel
    event_id: 2ff74090d637
    event_date: '2026-06-19T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 17.166666666666664
      7j: 17.166666666666664
      1m: 17.166666666666664
  flux_etf_qqq_5j:
    valeur: 0.02302656071922149
    valeur_normalisee: 0.10318887124276827
    valeur_ponderee: 0.10318887124276827
    ts: '2026-06-23T05:23:51.909406+00:00'
  spread_nasdaq_russell2000:
    valeur: 439.77002000000005
    valeur_normalisee: 0.4841050654978627
    valeur_ponderee: 0.4841050654978627
    ts: '2026-06-23T05:23:51.909406+00:00'
  rsi_14j_ixic:
    valeur: 58.43793129531857
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.03280569855137516
    valeur_normalisee: -0.2646557376103037
    valeur_ponderee: -0.2646557376103037
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.06380373077311186
    valeur_normalisee: 0.4893646475562676
    valeur_ponderee: 0.4893646475562676
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 0.8546168826218449
    valeur_ponderee: 0.8546168826218449
    ts: '2026-06-23T05:23:51.909406+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-23T05:23:51.909406+00:00'
  cftc_cot_nets:
    valeur: 174385.0
    valeur_normalisee: -0.21280652149528007
    valeur_ponderee: -0.21280652149528007
    ts: '2026-06-23T05:23:51.909406+00:00'
  flux_etf_or_5j:
    valeur: -0.005044781780804586
    valeur_normalisee: 0.07877445037477034
    valeur_ponderee: 0.07877445037477034
    ts: '2026-06-23T05:23:51.909406+00:00'
  tension_geopolitique:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (Fed hawkish,
      levée de sanctions Iran, accord de paix) malgré quelques signaux LONG (Pentagon
      demande fonds guerre, Ormuz fermé). Le prix a déjà baissé de 6.88% sur 20j,
      confirmant le biais baissier.
    nature: structurel
    event_id: 92c9fa6f2bed
    event_date: '2026-06-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 61.06666666666665
      7j: 61.06666666666665
      1m: 61.06666666666665
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-23T05:23:51.909406+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_or:
    valeur: -0.06915642430632896
    valeur_normalisee: -0.6416843973414201
    valeur_ponderee: -0.6416843973414201
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_or:
    valeur: -0.04699965724004518
    valeur_normalisee: -0.6268430979901555
    valeur_ponderee: -0.6268430979901555
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-23T05:23:51.909406+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: Les news du jour sont dominées par des signaux SHORT (levée
      de sanctions, progrès diplomatiques) mais aussi des signaux LONG (Pentagon demande
      80B$, tensions Ormuz). Le prix a déjà baissé de 19.69% sur 20j, suggérant que
      le marché a pricé l'apaisement. Les signaux contradictoires et la fraîcheur
      des
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 49.19999999999999
      7j: 49.19999999999999
      1m: 49.19999999999999
  cftc_cot_crude_nets:
    valeur: 49344.0
    valeur_normalisee: 0.509749552836747
    valeur_ponderee: 0.509749552836747
    ts: '2026-06-23T05:23:51.909406+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-06-23T05:23:51.909406+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 45.333333333333314
      7j: 45.333333333333314
      1m: 45.333333333333314
    sign_conflict: true
    sign_conflict_details:
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
    ts: '2026-06-23T05:23:51.909406+00:00'
  cushing_stocks:
    valeur: 20034.0
    valeur_normalisee: -0.7252271143164453
    valeur_ponderee: -0.7252271143164453
    ts: '2026-06-23T05:23:51.909406+00:00'
  spread_brent_wti:
    valeur: 3.9795699999999954
    ts: '2026-06-23T05:23:51.909406+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-23T05:23:51.909406+00:00'
    note: hors fenêtre
  momentum_prix_20j_petrole:
    valeur: -0.19694476260918536
    valeur_normalisee: -0.6476600076674837
    valeur_ponderee: -0.6476600076674837
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.10584466628939782
    valeur_normalisee: -0.44163805041307297
    valeur_ponderee: -0.44163805041307297
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-23T05:23:51.909406+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.009999999999999787
    valeur_normalisee: -0.0029453068729317702
    valeur_ponderee: -0.0029453068729317702
    ts: '2026-06-23T05:23:51.909406+00:00'
  hy_credit_spread:
    valeur: 2.66
    valeur_normalisee: -0.6327428824008168
    valeur_ponderee: -0.6327428824008168
    ts: '2026-06-23T05:23:51.909406+00:00'
  breadth_sp_ma50:
    valeur: 0.2815862614813974
    valeur_normalisee: -0.1003939939250464
    valeur_ponderee: -0.1003939939250464
    ts: '2026-06-23T05:23:51.909406+00:00'
  dxy_trend_20j:
    valeur: 120.3958
    valeur_normalisee: 0.7298447595400192
    valeur_ponderee: 0.7298447595400192
    ts: '2026-06-23T05:23:51.909406+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.0035591641388608153
    valeur_normalisee: -0.13146788940542953
    valeur_ponderee: -0.13146788940542953
    ts: '2026-06-23T05:23:51.909406+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.58
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-23T05:23:51.909406+00:00'
  rsi_14j_gspc:
    valeur: 53.098806814717776
    ts: '2026-06-23T05:23:51.909406+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.21
    valeur_normalisee: 0.8546168826218449
    valeur_ponderee: 0.8546168826218449
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.0022485459762175974
    valeur_normalisee: -0.36658325654598345
    valeur_ponderee: -0.36658325654598345
    ts: '2026-06-23T05:23:51.909406+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.026136250584291476
    valeur_normalisee: 0.21018444384750545
    valeur_ponderee: 0.21018444384750545
    ts: '2026-06-23T05:23:51.909406+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-23T05:23:51.909406+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-23T05:23:51.909406+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-23T05:23:51.909406+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-23T05:23:51.909406+00:00'
  gap_rv_iv:
    valeur: 0.8776548024614481
    ts: '2026-06-23T05:23:51.909406+00:00'
  cftc_cot_vix_nets:
    valeur: -66739.0
    valeur_normalisee: -0.27614381922396297
    valeur_ponderee: -0.27614381922396297
    ts: '2026-06-23T05:23:51.909406+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-23T05:23:51.909406+00:00'
    synthese_rationale: 'Signaux contradictoires : news LONG (Pentagon demande 80B$,
      Ormuz fermé) vs SHORT (accords de paix US-Iran, pourparlers en Suisse) s''équilibrent.
      Le prix VIX en baisse de 13.6% sur 20j suggère que le marché a déjà intégré
      un apaisement, rendant le signal net trop faible.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 54.33333333333333
      7j: 54.33333333333333
      1m: 54.33333333333333
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-23T05:23:51.909406+00:00'
```
