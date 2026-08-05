# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-05T05:23:05.845643+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.7818724533228507
    valeur_ponderee: 0.7818724533228507
    ts: '2026-08-05T05:23:05.845643+00:00'
  mouvement_or_5j:
    valeur: 0.0233200487284424
    valeur_normalisee: 0.683342226914355
    valeur_ponderee: 0.683342226914355
    ts: '2026-08-05T05:23:05.845643+00:00'
  ratio_gold_silver:
    valeur: 68.0273287185701
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_silver:
    valeur: 20236.0
    valeur_normalisee: -0.31454313983426346
    valeur_ponderee: -0.31454313983426346
    ts: '2026-08-05T05:23:05.845643+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.04139264990328817
    valeur_normalisee: 0.38694677027936053
    valeur_ponderee: 0.38694677027936053
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_argent:
    valeur: 0.09583522687052204
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_argent:
    valeur: 0.05555778216506613
    valeur_normalisee: 0.6661150412967175
    valeur_ponderee: 0.6661150412967175
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_argent:
    valeur: 0.05513050309965983
    valeur_normalisee: 0.7662035270706454
    valeur_ponderee: 0.7662035270706454
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.15282372538234223
    valeur_normalisee: 0.07641186269117112
    valeur_ponderee: 0.07641186269117112
    ts: '2026-08-05T05:23:05.845643+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: Les news récentes (USDA baisse production/stocks, tensions
      mer Noire) sont majoritairement LONG et à matérialité élevée, mais le prix a
      baissé de 5.74% sur 20j, suggérant que le marché a déjà intégré ces facteurs.
      La fraîcheur des news (3 août) et leur cohérence soutiennent un biais LONG,
      mais la di
    nature: structurel
    event_id: 55b523467a1b
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 82.8333333333334
      7j: 82.8333333333334
      1m: 82.8333333333334
  cftc_cot_wheat:
    valeur: -5384.0
    valeur_normalisee: 0.5293592418323769
    valeur_ponderee: 0.5293592418323769
    ts: '2026-08-05T05:23:05.845643+00:00'
  meteo_australie_dryland:
    valeur: -0.08479130726281946
    valeur_normalisee: -0.04239565363140973
    valeur_ponderee: -0.04239565363140973
    ts: '2026-08-05T05:23:05.845643+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_ble:
    valeur: -0.05738918667874393
    valeur_normalisee: -0.46683028929857606
    valeur_ponderee: -0.46683028929857606
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_ble:
    valeur: -0.036538632844785424
    valeur_normalisee: -0.49995311225792366
    valeur_ponderee: -0.49995311225792366
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_ble:
    valeur: -0.005864691945581035
    valeur_normalisee: -0.20893475282802734
    valeur_ponderee: -0.20893475282802734
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-05T05:23:05.845643+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.016555864936308895
    valeur_normalisee: -0.5056301064441682
    valeur_ponderee: -0.5056301064441682
    ts: '2026-08-05T05:23:05.845643+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.04049912434325753
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  tension_politique_fr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: Les news récentes (3-5 août) montrent un apaisement des tensions
      au Moyen-Orient et des PMI manufacturiers solides, soutenant le CAC40, malgré
      des PMI chinois faibles. Les frappes sur l'Iran du 30 juillet sont plus anciennes
      et le prix a déjà progressé de +2.73% sur 20j, ce qui limite la conviction.
    nature: verbal
    event_id: ed7d74cfbf5b
    event_date: '2026-08-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -124.40000000000012
      7j: -124.40000000000012
      1m: -124.40000000000012
  rsi_14j_fchi:
    valeur: 67.57267832320561
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.027309517476839407
    valeur_normalisee: 0.39300435482882556
    valeur_ponderee: 0.39300435482882556
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.035157639317777045
    valeur_normalisee: 0.9403947256623265
    valeur_ponderee: 0.9403947256623265
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_cac40:
    valeur: 0.021329002581437884
    valeur_normalisee: 0.7772387750686388
    valeur_ponderee: 0.7772387750686388
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-05T05:23:05.845643+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-07-31'
    valeur: 0.12311321174260538
    valeur_normalisee: 0.06155660587130269
    valeur_ponderee: 0.06155660587130269
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -15428.0
    valeur_normalisee: -0.5922330245608465
    valeur_ponderee: -0.5922330245608465
    ts: '2026-08-05T05:23:05.845643+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: structurel
    event_id: 46b9dc77b8a8
    event_date: '2026-08-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 101.33333333333333
      7j: 101.33333333333333
      1m: 101.33333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  maladies_cabosses:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: Dominance de nouvelles à matérialité élevée et fraîches (Ghana
      -16% production, El Niño) signalant une offre réduite, cohérentes avec le prix
      en hausse de +8.81% sur 20j. Les quelques nouvelles baissières sont faibles
      ou anciennes et ne contrebalancent pas le signal haussier.
    nature: structurel
    event_id: 46b9dc77b8a8
    event_date: '2026-08-01T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.22'
    p2_shadow_contrib_exclu:
      24h: 102.26666666666664
      7j: 102.26666666666664
      1m: 102.26666666666664
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.08809404709170554
    valeur_normalisee: -0.12202074284710528
    valeur_ponderee: -0.12202074284710528
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.14524807549249075
    valeur_normalisee: 0.47270442944707064
    valeur_ponderee: 0.47270442944707064
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_cacao:
    valeur: 0.09689642959244926
    valeur_normalisee: 0.5815506119976019
    valeur_ponderee: 0.5815506119976019
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.3962270150369114
    valeur_normalisee: 0.1981135075184557
    valeur_ponderee: 0.1981135075184557
    ts: '2026-08-05T05:23:05.845643+00:00'
  usd_brl:
    valeur: 5.14309
    valeur_normalisee: 0.16731304737011649
    valeur_ponderee: 0.16731304737011649
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_coffee:
    valeur: 27914.0
    valeur_normalisee: -0.15738525585500848
    valeur_ponderee: -0.15738525585500848
    ts: '2026-08-05T05:23:05.845643+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: 'Les news récentes (3-4 août) montrent des signaux LONG (prix
      élevés au Vietnam, hausse des prix minimum Fairtrade) malgré une baisse des
      prix le 4 août. Le contexte marché (+3.23% sur 20j) est cohérent avec un biais
      LONG, mais la baisse récente sur 5j et les news SHORT du 29-30 juillet tempèrent
      la '
    nature: ponctuel
    event_id: 5416d5232089
    event_date: '2026-08-03T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 105.86666666666689
      7j: 105.86666666666689
      1m: 105.86666666666689
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-05T05:23:05.845643+00:00'
  meteo_vietnam_robusta:
    valeur: 0.303199456788643
    valeur_normalisee: 0.1515997283943215
    valeur_ponderee: 0.1515997283943215
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.032313926351170474
    valeur_normalisee: -0.18417547693399441
    valeur_ponderee: -0.18417547693399441
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_cafe:
    valeur: -0.008077034357039659
    valeur_normalisee: -0.30880154263407705
    valeur_ponderee: -0.30880154263407705
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_cafe:
    valeur: -0.02440455813457265
    valeur_normalisee: -0.445589902345887
    valeur_ponderee: -0.445589902345887
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.20868274854246602
    valeur_normalisee: 0.10434137427123301
    valeur_ponderee: 0.10434137427123301
    ts: '2026-08-05T05:23:05.845643+00:00'
  meteo_inde_gujarat_coton:
    ts: '2026-08-05T05:23:05.845643+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-07-31'
    valeur: 0.6028819546829338
    valeur_normalisee: 0.3014409773414669
    valeur_ponderee: 0.3014409773414669
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 98453.0
    valeur_normalisee: 0.7538273781947771
    valeur_ponderee: 0.7538273781947771
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_coton:
    valeur: 0.012615138165799067
    valeur_normalisee: 0.17059598176716972
    valeur_ponderee: 0.17059598176716972
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_coton:
    valeur: 0.013020833333333481
    valeur_normalisee: 0.25473837799374266
    valeur_ponderee: 0.25473837799374266
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_coton:
    valeur: 0.004768527717067261
    valeur_normalisee: 0.1421048444585515
    valeur_ponderee: 0.1421048444585515
    ts: '2026-08-05T05:23:05.845643+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: structurel
    event_id: 37e0a148f8cf
    event_date: '2026-08-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 46.50000000000002
      7j: 46.50000000000002
      1m: 46.50000000000002
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: Les importations chinoises de cuivre en forte hausse et la
      demande IA US/Chine avec stocks en chute dominent, malgré des PMI chinois faibles.
      Le prix a déjà monté de 6.34% sur 20j, ce qui tempère la conviction.
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 23.399999999999963
      7j: 23.399999999999963
      1m: 23.399999999999963
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_copper_nets:
    valeur: 68497.0
    valeur_normalisee: 0.881260518302941
    valeur_ponderee: 0.881260518302941
    ts: '2026-08-05T05:23:05.845643+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 40.56666666666664
      7j: 40.56666666666664
      1m: 40.56666666666664
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.0016016115154022605
    valeur_normalisee: 0.8940220741480343
    valeur_ponderee: 0.8940220741480343
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.06337411465818099
    valeur_normalisee: 0.9311143887205378
    valeur_ponderee: 0.9311143887205378
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_cuivre:
    valeur: 0.050967903520340974
    valeur_normalisee: 0.9564238184159981
    valeur_ponderee: 0.9564238184159981
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_cuivre:
    valeur: 0.030328601288297286
    valeur_normalisee: 0.719253738080752
    valeur_ponderee: 0.719253738080752
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-05T05:23:05.845643+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5479469258999998
    valeur_normalisee: 0.1285546572140481
    valeur_ponderee: 0.1285546572140481
    ts: '2026-08-05T05:23:05.845643+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.73
    valeur_normalisee: 0.9257671479215225
    valeur_ponderee: 0.9257671479215225
    ts: '2026-08-05T05:23:05.845643+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  usd_jpy_proxy_risk:
    valeur: 157.64666
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_eur_nets:
    valeur: -100540.0
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.007943651632861704
    valeur_normalisee: 0.7704429207696746
    valeur_ponderee: 0.7704429207696746
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.005842853405424231
    valeur_normalisee: 0.4546809669936871
    valeur_ponderee: 0.4546809669936871
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_eurusd:
    valeur: 0.00019077680847723322
    valeur_normalisee: 0.032357102717328716
    valeur_ponderee: 0.032357102717328716
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.7818724533228507
    valeur_ponderee: 0.7818724533228507
    ts: '2026-08-05T05:23:05.845643+00:00'
  sox_trend_5j:
    valeur: 542.21002
    valeur_normalisee: -0.2058096884441106
    valeur_ponderee: -0.2058096884441106
    ts: '2026-08-05T05:23:05.845643+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16852939610497744
    valeur_normalisee: 0.4701934627720655
    valeur_ponderee: 0.4701934627720655
    ts: '2026-08-05T05:23:05.845643+00:00'
  sentiment_ia_megacaps:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: 'Signaux mitigés : news LONG (IA, PMI, exportations coréennes)
      contre SHORT (guerre Iran, épuisement missiles, pression Fed, interdiction composants).
      Prix +7% sur 5j suggère que le positif est déjà pricé, et les news SHORT récentes
      (matérialité high) contrebalancent.'
    nature: ponctuel
    p2_shadow_contrib_exclu:
      24h: 153.866666666667
      7j: 153.866666666667
      1m: 153.866666666667
  flux_etf_qqq_5j:
    valeur: 0.07159245986753993
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  spread_nasdaq_russell2000:
    valeur: 422.13998999999995
    valeur_normalisee: -0.030185733733903326
    valeur_ponderee: -0.030185733733903326
    ts: '2026-08-05T05:23:05.845643+00:00'
  rsi_14j_ixic:
    valeur: 57.76262384077865
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.020326163544340803
    valeur_normalisee: -0.03137526648791301
    valeur_ponderee: -0.03137526648791301
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.0579045074873803
    valeur_normalisee: 0.8207178353364999
    valeur_ponderee: 0.8207178353364999
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.05895690233277606
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.7818724533228507
    valeur_ponderee: 0.7818724533228507
    ts: '2026-08-05T05:23:05.845643+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_nets:
    valeur: 174131.0
    valeur_normalisee: -0.20851213210640585
    valeur_ponderee: -0.20851213210640585
    ts: '2026-08-05T05:23:05.845643+00:00'
  flux_etf_or_5j:
    valeur: 0.012968026639954555
    valeur_normalisee: 0.4039429236462791
    valeur_ponderee: 0.4039429236462791
    ts: '2026-08-05T05:23:05.845643+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: Les news récentes sont dominées par des tensions géopolitiques
      (frappe russe sur Kyiv, navire frappé à Ormuz, épuisement des missiles US) et
      des achats d'or par les banques centrales, soutenant l'or. Cependant, des signaux
      contradictoires (progrès de médiation, hausse des taux) et le prix déjà en ha
    nature: structurel
    event_id: 16f3a6f1e3f6
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 214.99999999999972
      7j: 214.99999999999972
      1m: 214.99999999999972
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-05T05:23:05.845643+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_or:
    valeur: 0.04093864810457992
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_or:
    valeur: 0.01786424793723307
    valeur_normalisee: 0.5348080853400481
    valeur_ponderee: 0.5348080853400481
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_or:
    valeur: 0.023954458568263393
    valeur_normalisee: 0.675000754916391
    valeur_ponderee: 0.675000754916391
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-05T05:23:05.845643+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-08-05T05:23:05.845643+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-07-31'
    valeur: 404508.0
    valeur_normalisee: -0.7758900959893141
    valeur_ponderee: -0.7758900959893141
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: 'Les news du jour sont contradictoires : des signaux SHORT
      (accord imminent sur Ormuz, chute de 10%, réouverture d''oléoduc) s''opposent
      à des signaux LONG (frappe sur navire, perte de 2,6 Mds de barils, stocks bas).
      Le prix a chuté de 11% sur 5j, suggérant que le marché a déjà pricé une partie
      de l''ap'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 386.1999999999983
      7j: 386.1999999999983
      1m: 386.1999999999983
  cftc_cot_crude_nets:
    valeur: 32189.0
    valeur_normalisee: 0.13392206358519956
    valeur_ponderee: 0.13392206358519956
    ts: '2026-08-05T05:23:05.845643+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: structurel
    event_id: 16f3a6f1e3f6
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 175.7666666666673
      7j: 175.7666666666673
      1m: 175.7666666666673
    sign_conflict: true
    sign_conflict_details:
    - event_id: c4566eff9e81
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de petrole
      matched_surprise: baisse
      surprise_polarity: down
      title: Pétrole en baisse après avoir bondi de 8% suite à des hostilités iraniennes
        et une baisse des stocks
    - event_id: 8aa5c20f7194
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: draw
      surprise_polarity: down
      title: La Chine a puisé 41 millions de barils dans ses stocks de brut en juin,
        réduisant la pression sur l'offre mondiale pendant le conflit iranien.
    - event_id: 46c8cbf2b438
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: oil stocks
      matched_surprise: draw
      surprise_polarity: down
      title: La Chine a puisé 41 millions de barils dans ses stocks de brut en juin,
        l'un des plus gros prélèvements mensuels jamais enregistrés, selon l'AIE.
    - event_id: a802379cbc43
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: stocks petroliers
      matched_surprise: hausse
      surprise_polarity: up
      title: Disparition des buffers pétroliers mondiaux (faibles stocks, détroit
        d'Ormuz perturbé, excédents réduits) augmentant le risque de hausse des prix
    - event_id: 417f7c27cfee
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Stocks de pétrole brut américains en baisse moins que prévu
    - event_id: 1d1529ae2727
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse des stocks de brut inférieure aux attentes, signal de demande
        plus faible
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
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  cushing_stocks:
    valeur: 18599.0
    valeur_normalisee: -0.8001382957591842
    valeur_ponderee: -0.8001382957591842
    ts: '2026-08-05T05:23:05.845643+00:00'
  spread_brent_wti:
    valeur: 2.8707509999999985
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_petrole:
    valeur: -0.014921751662327565
    valeur_normalisee: 0.09958693796528309
    valeur_ponderee: 0.09958693796528309
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.08531830465313195
    valeur_normalisee: -0.32699687403374456
    valeur_ponderee: -0.32699687403374456
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.12413837869473654
    valeur_normalisee: -0.8905625926096535
    valeur_ponderee: -0.8905625926096535
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-05T05:23:05.845643+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-05T05:23:05.845643+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.04999999999999982
    valeur_normalisee: 0.15219864733513835
    valeur_ponderee: 0.15219864733513835
    ts: '2026-08-05T05:23:05.845643+00:00'
  hy_credit_spread:
    valeur: 2.78
    valeur_normalisee: 0.3109038201541257
    valeur_ponderee: 0.3109038201541257
    ts: '2026-08-05T05:23:05.845643+00:00'
  breadth_sp_ma50:
    valeur: 0.2855198090176757
    valeur_normalisee: 0.26391142427080017
    valeur_ponderee: 0.26391142427080017
    ts: '2026-08-05T05:23:05.845643+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.041127919460193674
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.28
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  rsi_14j_gspc:
    valeur: 65.65553133805568
    ts: '2026-08-05T05:23:05.845643+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.7818724533228507
    valeur_ponderee: 0.7818724533228507
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.03158978663947831
    valeur_normalisee: 0.245940829615213
    valeur_ponderee: 0.245940829615213
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.04384722563500243
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_sp500:
    valeur: 0.03996281465302198
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-05T05:23:05.845643+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-05T05:23:05.845643+00:00'
    reporte: true
    reporte_age_j: 4
    reporte_date: '2026-07-30'
    valeur: -0.1817535949708365
    valeur_normalisee: 0.09087679748541826
    valeur_ponderee: 0.09087679748541826
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 78.058881
    valeur_normalisee: -0.417550978541472
    valeur_ponderee: -0.417550978541472
    ts: '2026-08-05T05:23:05.845643+00:00'
  usd_brl_sucre:
    valeur: 5.14309
    valeur_normalisee: 0.16731304737011649
    valeur_ponderee: 0.16731304737011649
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_sugar:
    valeur: -81679.0
    valeur_normalisee: -0.5608615387476262
    valeur_ponderee: -0.5608615387476262
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_sucre:
    valeur: -0.003018108651911433
    valeur_normalisee: -0.1052347974194834
    valeur_ponderee: -0.1052347974194834
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.020597322348094638
    valeur_normalisee: 0.4337402627502225
    valeur_ponderee: 0.4337402627502225
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.03987408184679975
    valeur_normalisee: 0.9177213867538129
    valeur_ponderee: 0.9177213867538129
    ts: '2026-08-05T05:23:05.845643+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '9.22'
    p2_shadow_contrib_exclu:
      24h: 35.53333333333329
      7j: 35.53333333333329
      1m: 35.53333333333329
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
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '9.22'
    p2_shadow_contrib_exclu:
      24h: 35.53333333333329
      7j: 35.53333333333329
      1m: 35.53333333333329
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-05T05:23:05.845643+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.58
    valeur_normalisee: 0.5857530693918652
    valeur_ponderee: 0.5857530693918652
    ts: '2026-08-05T05:23:05.845643+00:00'
  dxy_trend_20j:
    valeur: 119.7034
    valeur_normalisee: -0.11371340011022336
    valeur_ponderee: -0.11371340011022336
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_7j_usdjpy:
    valeur: -0.035503134171723016
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.002608563578466061
    valeur_normalisee: 0.20137711677960163
    valeur_ponderee: 0.20137711677960163
    ts: '2026-08-05T05:23:05.845643+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.02921704936641356
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_jpy_nets:
    valeur: -171320.0
    valeur_normalisee: -0.7719946476652498
    valeur_ponderee: -0.7719946476652498
    ts: '2026-08-05T05:23:05.845643+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0300000000000002
    valeur_normalisee: 0.9145890901591022
    valeur_ponderee: 0.9145890901591022
    ts: '2026-08-05T05:23:05.845643+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-05T05:23:05.845643+00:00'
    nature: ponctuel
    event_id: 0245b306e21d
    event_date: '2026-08-04T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 11.166666666666675
      7j: 11.166666666666675
      1m: 11.166666666666675
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-05T05:23:05.845643+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-05T05:23:05.845643+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-05T05:23:05.845643+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-05T05:23:05.845643+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-05T05:23:05.845643+00:00'
  gap_rv_iv:
    valeur: -0.7800450063441371
    ts: '2026-08-05T05:23:05.845643+00:00'
  cftc_cot_vix_nets:
    valeur: -63413.0
    valeur_normalisee: -0.21963090052659925
    valeur_ponderee: -0.21963090052659925
    ts: '2026-08-05T05:23:05.845643+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-05T05:23:05.845643+00:00'
    synthese_rationale: Malgré les rumeurs d'accord et l'annulation de frappes, les
      news fraîches (05/08) confirment une escalade (Ormuz, frappe russe sur Kyiv)
      et la matérialité élevée domine. Le prix a baissé récemment, mais la fraîcheur
      et la gravité des événements justifient un biais long modéré.
    nature: structurel
    event_id: 16f3a6f1e3f6
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 240.7666666666662
      7j: 240.7666666666662
      1m: 240.7666666666662
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-05T05:23:05.845643+00:00'
```
