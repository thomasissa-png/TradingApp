# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-08-13T05:23:11.346069+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.699910477827727
    valeur_ponderee: 0.699910477827727
    ts: '2026-08-13T05:23:11.346069+00:00'
  mouvement_or_5j:
    valeur: 0.013984062701989819
    valeur_normalisee: 0.22252655408612756
    valeur_ponderee: 0.22252655408612756
    ts: '2026-08-13T05:23:11.346069+00:00'
  ratio_gold_silver:
    valeur: 67.24783639956358
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_silver:
    valeur: 20058.0
    valeur_normalisee: -0.3206731163551768
    valeur_ponderee: -0.3206731163551768
    ts: '2026-08-13T05:23:11.346069+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.05332621722846431
    valeur_normalisee: 0.41361129029343535
    valeur_ponderee: 0.41361129029343535
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_argent:
    valeur: 0.12474911102331099
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_argent:
    valeur: 0.06402270174416791
    valeur_normalisee: 0.5163463985593191
    valeur_ponderee: 0.5163463985593191
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_argent:
    valeur: -0.003988456461720857
    valeur_normalisee: -0.033535550379559124
    valeur_ponderee: -0.033535550379559124
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur: 920112000.0
    valeur_normalisee: -0.5367988110081852
    valeur_ponderee: -0.5367988110081852
    ts: '2026-08-13T05:23:11.346069+00:00'
  noaa_drought_midwest_plains:
    valeur: 0.18090503003884764
    valeur_normalisee: 0.09045251501942382
    valeur_ponderee: 0.09045251501942382
    ts: '2026-08-13T05:23:11.346069+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Attaques récentes sur les terminaux céréaliers russes en mer
      Noire et frappes sur Novorossiysk perturbent les exportations, signal dominant
      malgré la baisse de prix sur 20j. USDA prévoit une baisse de 11% de la production
      des principaux exportateurs, renforçant le biais haussier.
    nature: structurel
    event_id: cd16f8309faf
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 111.06666666666679
      7j: 111.06666666666679
      1m: 111.06666666666679
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -19165.0
    valeur_normalisee: 0.34324298726925345
    valeur_ponderee: 0.34324298726925345
    ts: '2026-08-13T05:23:11.346069+00:00'
  meteo_australie_dryland:
    valeur: -0.0035213740647018067
    valeur_normalisee: -0.0017606870323509034
    valeur_ponderee: -0.0017606870323509034
    ts: '2026-08-13T05:23:11.346069+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_ble:
    valeur: -0.03523058702021775
    valeur_normalisee: -0.40529695926891096
    valeur_ponderee: -0.40529695926891096
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_ble:
    valeur: 0.038507910852265015
    valeur_normalisee: 0.2929965504215468
    valeur_ponderee: 0.2929965504215468
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_ble:
    valeur: 0.02381627796424368
    valeur_normalisee: 0.343063864547384
    valeur_ponderee: 0.343063864547384
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-08-13T05:23:11.346069+00:00'
  alpha_cac_vs_sp_5j:
    valeur: -0.002856818923131499
    valeur_normalisee: -0.21610990776300598
    valeur_ponderee: -0.21610990776300598
    ts: '2026-08-13T05:23:11.346069+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.0006310475389146308
    valeur_normalisee: -0.11935770487943953
    valeur_ponderee: -0.11935770487943953
    ts: '2026-08-13T05:23:11.346069+00:00'
  tension_politique_fr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Malgré des risques géopolitiques et sécheresse, les news récentes
      (Sentix positif, emploi US faible, PMI solides) dominent et soutiennent le CAC40,
      cohérent avec la hausse de 3.49% sur 20j.
    nature: ponctuel
    event_id: b079c1b71b9d
    event_date: '2026-08-10T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '3.22'
    p2_shadow_contrib_exclu:
      24h: -153.7000000000001
      7j: -153.7000000000001
      1m: -153.7000000000001
  rsi_14j_fchi:
    valeur: 64.5385153751403
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.03489569860024666
    valeur_normalisee: 0.46473487958105736
    valeur_ponderee: 0.46473487958105736
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.0070955879970058255
    valeur_normalisee: -0.08731159785940189
    valeur_ponderee: -0.08731159785940189
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.004588592383698353
    valeur_normalisee: -0.390605969513323
    valeur_ponderee: -0.390605969513323
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-08-13T05:23:11.346069+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-08-12'
    valeur: 0.031046256409448445
    valeur_normalisee: 0.015523128204724223
    valeur_ponderee: 0.015523128204724223
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -13320.0
    valeur_normalisee: -0.5520070944399957
    valeur_ponderee: -0.5520070944399957
    ts: '2026-08-13T05:23:11.346069+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: structurel
    event_id: 5ae5acf78f87
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 117.16666666666663
      7j: 117.16666666666663
      1m: 117.16666666666663
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
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Les news récentes (11 août) à matérialité high sur El Niño
      et les menaces sur l'offre dominent, malgré quelques signaux baissiers plus
      anciens. Le prix a déjà monté de +7.39% sur 20j, ce qui suggère que l'information
      est en partie pricée, d'où une conviction medium.
    nature: structurel
    event_id: 5ae5acf78f87
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 119.03333333333329
      7j: 119.03333333333329
      1m: 119.03333333333329
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.07388360929554283
    valeur_normalisee: -0.19136973556964285
    valeur_ponderee: -0.19136973556964285
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.0002755907292408821
    valeur_normalisee: -0.26518330709403587
    valeur_ponderee: -0.26518330709403587
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.03081993061399846
    valeur_normalisee: -0.41394702216238344
    valeur_ponderee: -0.41394702216238344
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-13T05:23:11.346069+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.40626486655948374
    valeur_normalisee: 0.20313243327974187
    valeur_ponderee: 0.20313243327974187
    ts: '2026-08-13T05:23:11.346069+00:00'
  usd_brl:
    valeur: 5.19525
    valeur_normalisee: 0.8099726783371988
    valeur_ponderee: 0.8099726783371988
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_coffee:
    valeur: 26014.0
    valeur_normalisee: -0.19165598000827952
    valeur_ponderee: -0.19165598000827952
    ts: '2026-08-13T05:23:11.346069+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Les news récentes (12-13 août) montrent un rebond de l'arabica
      à un pic de 3 semaines, soutenu par les craintes El Niño (matérialité high le
      7 août) et des prix élevés au Vietnam. Les signaux baissiers (récolte brésilienne
      en accélération) sont plus anciens et moins frais, et le prix a déjà monté de
    nature: ponctuel
    event_id: 348647462e84
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 109.26666666666688
      7j: 109.26666666666688
      1m: 109.26666666666688
  cycle_bresil_biannuel:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-13T05:23:11.346069+00:00'
  meteo_vietnam_robusta:
    valeur: 0.3810072820309148
    valeur_normalisee: 0.1905036410154574
    valeur_ponderee: 0.1905036410154574
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.018335849009877947
    valeur_normalisee: -0.3155689956929577
    valeur_ponderee: -0.3155689956929577
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.03738465101405031
    valeur_normalisee: 0.06052658048932171
    valeur_ponderee: 0.06052658048932171
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.014652945804972894
    valeur_normalisee: 0.02771023603041688
    valeur_ponderee: 0.02771023603041688
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-13T05:23:11.346069+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.11540905873890839
    valeur_normalisee: 0.057704529369454194
    valeur_ponderee: 0.057704529369454194
    ts: '2026-08-13T05:23:11.346069+00:00'
  meteo_inde_gujarat_coton:
    valeur: 0.7939637630686788
    valeur_normalisee: 0.3969818815343394
    valeur_ponderee: 0.3969818815343394
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_cotton:
    valeur: 102492.0
    valeur_normalisee: 0.7964676176052232
    valeur_ponderee: 0.7964676176052232
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_coton:
    valeur: 0.0349430702787592
    valeur_normalisee: 0.39372661651717805
    valeur_ponderee: 0.39372661651717805
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_coton:
    valeur: 0.043960396039604
    valeur_normalisee: 0.5774498271354321
    valeur_ponderee: 0.5774498271354321
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_coton:
    valeur: 0.011123897199846633
    valeur_normalisee: 0.2247629685590138
    valeur_ponderee: 0.2247629685590138
    ts: '2026-08-13T05:23:11.346069+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 64.36666666666677
      7j: 64.36666666666677
      1m: 64.36666666666677
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-13T05:23:11.346069+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Les news LONG dominent nettement, notamment les importations
      chinoises record et la demande IA, malgré des signaux SHORT récurrents sur l'offre
      chilienne. Le prix a déjà monté de 3.83% sur 20j, ce qui suggère que l'essentiel
      est pricé, mais la fraîcheur des news LONG (12/08) et leur matérialité élev
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 35.46666666666664
      7j: 35.46666666666664
      1m: 35.46666666666664
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_copper_nets:
    valeur: 77422.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-13T05:23:11.346069+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: structurel
    event_id: 576489ea4147
    event_date: '2026-08-05T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '8.22'
    p2_shadow_contrib_exclu:
      24h: 55.300000000000026
      7j: 55.300000000000026
      1m: 55.300000000000026
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.001486502670627994
    valeur_normalisee: -0.6085374148249475
    valeur_ponderee: -0.6085374148249475
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.03826092750110255
    valeur_normalisee: 0.4237294063426987
    valeur_ponderee: 0.4237294063426987
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.022309824987003846
    valeur_normalisee: -0.5522971302208669
    valeur_ponderee: -0.5522971302208669
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_cuivre:
    valeur: -0.01074051513965224
    valeur_normalisee: -0.3159637102329248
    valeur_ponderee: -0.3159637102329248
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-13T05:23:11.346069+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5112979040999996
    valeur_normalisee: -0.19444724866675572
    valeur_ponderee: -0.19444724866675572
    ts: '2026-08-13T05:23:11.346069+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.73
    valeur_normalisee: 0.8020959491227253
    valeur_ponderee: 0.8020959491227253
    ts: '2026-08-13T05:23:11.346069+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  usd_jpy_proxy_risk:
    valeur: 159.33044
    valeur_normalisee: -0.48381056839497744
    valeur_ponderee: -0.48381056839497744
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_eur_nets:
    valeur: -78631.0
    valeur_normalisee: -0.9272135456966083
    valeur_ponderee: -0.9272135456966083
    ts: '2026-08-13T05:23:11.346069+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_eurusd:
    valeur: 0.013532882530358892
    valeur_normalisee: 0.8031332262883146
    valeur_ponderee: 0.8031332262883146
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.00015619034396596732
    valeur_normalisee: 0.017449362635462953
    valeur_ponderee: 0.017449362635462953
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0014727285328158812
    valeur_normalisee: -0.15050580066233396
    valeur_ponderee: -0.15050580066233396
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.699910477827727
    valeur_ponderee: 0.699910477827727
    ts: '2026-08-13T05:23:11.346069+00:00'
  sox_trend_5j:
    valeur: 546.60999
    valeur_normalisee: -0.17351128758013953
    valeur_ponderee: -0.17351128758013953
    ts: '2026-08-13T05:23:11.346069+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17015337612058343
    valeur_normalisee: 0.6437056523918346
    valeur_ponderee: 0.6437056523918346
    ts: '2026-08-13T05:23:11.346069+00:00'
  sentiment_ia_megacaps:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Le financement massif de 500 Mds$ pour l'infrastructure IA
      de Nvidia, confirmé et répété, domine le flux d'actualités, soutenu par un CPI
      modéré et des attentes dovish. Malgré des risques géopolitiques et des pressions
      inflationnistes, le signal long est net mais la matérialité moyenne et la fraîche
    nature: ponctuel
    event_id: c8f1e8b0443c
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 75.76666666666672
      7j: 75.76666666666672
      1m: 75.76666666666672
  flux_etf_qqq_5j:
    valeur: 0.008922375699461638
    valeur_normalisee: 0.07958249998392532
    valeur_ponderee: 0.07958249998392532
    ts: '2026-08-13T05:23:11.346069+00:00'
  spread_nasdaq_russell2000:
    valeur: 420.99002
    valeur_normalisee: -0.03292884185125931
    valeur_ponderee: -0.03292884185125931
    ts: '2026-08-13T05:23:11.346069+00:00'
  rsi_14j_ixic:
    valeur: 56.004946065907845
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_nasdaq:
    valeur: 0.008303870598042051
    valeur_normalisee: -0.030345189213917635
    valeur_ponderee: -0.030345189213917635
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.03375377142817659
    valeur_normalisee: 0.4618048052050711
    valeur_ponderee: 0.4618048052050711
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_nasdaq:
    valeur: 0.0009266295632652799
    valeur_normalisee: 0.0029442443557399257
    valeur_ponderee: 0.0029442443557399257
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.699910477827727
    valeur_ponderee: 0.699910477827727
    ts: '2026-08-13T05:23:11.346069+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_nets:
    valeur: 190648.0
    valeur_normalisee: -0.0635299654081457
    valeur_ponderee: -0.0635299654081457
    ts: '2026-08-13T05:23:11.346069+00:00'
  flux_etf_or_5j:
    valeur: 0.039215685268050304
    valeur_normalisee: 0.6459233024134913
    valeur_ponderee: 0.6459233024134913
    ts: '2026-08-13T05:23:11.346069+00:00'
  tension_geopolitique:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Blocus d'Ormuz et attaques en mer Rouge dominent, avec matérialité
      élevée et fraîcheur récente, soutenant l'or malgré quelques news SHORT dispersées.
      Le prix a déjà monté de 8.63% sur 20j, mais les tensions géopolitiques actuelles
      renforcent le biais haussier.
    nature: structurel
    event_id: 54d27362d3ad
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 335.6333333333319
      7j: 335.6333333333319
      1m: 335.6333333333319
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-08-13T05:23:11.346069+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_or:
    valeur: 0.08621909082285506
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_or:
    valeur: 0.03823298449196
    valeur_normalisee: 0.53085884655726
    valeur_ponderee: 0.53085884655726
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_or:
    valeur: 0.002953487625150908
    valeur_normalisee: 0.015692976996882928
    valeur_ponderee: 0.015692976996882928
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
petrole:
  eia_crude_surprise:
    valeur: 424410.0
    valeur_normalisee: -0.13812033584105132
    valeur_ponderee: -0.13812033584105132
    ts: '2026-08-13T05:23:11.346069+00:00'
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: Blocus persistant du détroit d'Ormuz et attaques en mer Rouge
      dominent, avec matérialité élevée et fraîcheur récente, malgré des stocks US
      en hausse. Le prix a déjà monté, mais les news de supply disruption sont massives
      et cohérentes.
    nature: structurel
    event_id: 54d27362d3ad
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 314.3666666666652
      7j: 314.3666666666652
      1m: 314.3666666666652
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 26587.0
    valeur_normalisee: 0.013076899911430795
    valeur_ponderee: 0.013076899911430795
    ts: '2026-08-13T05:23:11.346069+00:00'
  opec_production_policy:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: structurel
    event_id: 54d27362d3ad
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 285.99999999999847
      7j: 285.99999999999847
      1m: 285.99999999999847
    sign_conflict: true
    sign_conflict_details:
    - event_id: c891330a80ef
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: stocks de petrole
      matched_surprise: chute
      surprise_polarity: down
      title: Accord de navigation Iran-Oman sur Hormuz et rebond des stocks US, le
        pétrole chute
    - event_id: fef734e1aa7e
      asset: BRENT
      rule_name: eia_stocks
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: eia
      matched_surprise: baisse
      surprise_polarity: down
      title: 'Inventaires pétroliers US: brut +2,5M barils, produits en baisse'
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
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  cushing_stocks:
    valeur: 22566.0
    valeur_normalisee: -0.15882864718542616
    valeur_ponderee: -0.15882864718542616
    ts: '2026-08-13T05:23:11.346069+00:00'
  spread_brent_wti:
    valeur: 4.535556
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.03232095795342205
    valeur_normalisee: 0.2616984711667566
    valeur_ponderee: 0.2616984711667566
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_petrole:
    valeur: 0.11706717835993508
    valeur_normalisee: 0.7077476661027442
    valeur_ponderee: 0.7077476661027442
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_petrole:
    valeur: 0.007459498016117783
    valeur_normalisee: 0.11040412978031786
    valeur_ponderee: 0.11040412978031786
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-08-13T05:23:11.346069+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.07000000000000028
    valeur_normalisee: 0.27904381108525644
    valeur_ponderee: 0.27904381108525644
    ts: '2026-08-13T05:23:11.346069+00:00'
  hy_credit_spread:
    valeur: 2.72
    valeur_normalisee: -0.15717527120227187
    valeur_ponderee: -0.15717527120227187
    ts: '2026-08-13T05:23:11.346069+00:00'
  breadth_sp_ma50:
    valeur: 0.2861914133023264
    valeur_normalisee: 0.26014312452772576
    valeur_ponderee: 0.26014312452772576
    ts: '2026-08-13T05:23:11.346069+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  flux_etf_spy_ivv_5j:
    valeur: 0.0035074631654727906
    valeur_normalisee: -0.02815145105515393
    valeur_ponderee: -0.02815145105515393
    ts: '2026-08-13T05:23:11.346069+00:00'
  shiller_cape_fwd_pe:
    valeur: 42.34
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-08-13T05:23:11.346069+00:00'
  rsi_14j_gspc:
    valeur: 63.04381405081347
    ts: '2026-08-13T05:23:11.346069+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.699910477827727
    valeur_ponderee: 0.699910477827727
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.02342309985294322
    valeur_normalisee: 0.20689871512415517
    valeur_ponderee: 0.20689871512415517
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_sp500:
    valeur: 0.019559980454814996
    valeur_normalisee: 0.35251107069573845
    valeur_ponderee: 0.35251107069573845
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.000995809934616898
    valeur_normalisee: -0.10396378237569098
    valeur_ponderee: -0.10396378237569098
    ts: '2026-08-13T05:23:11.346069+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-08-13T05:23:11.346069+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-08-10'
    valeur: -0.1786140319430498
    valeur_normalisee: 0.0893070159715249
    valeur_ponderee: 0.0893070159715249
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 87.5968
    valeur_normalisee: 0.19183018974626884
    valeur_ponderee: 0.19183018974626884
    ts: '2026-08-13T05:23:11.346069+00:00'
  usd_brl_sucre:
    valeur: 5.19525
    valeur_normalisee: 0.8099726783371988
    valeur_ponderee: 0.8099726783371988
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_sugar:
    valeur: -54728.0
    valeur_normalisee: -0.4516842533419668
    valeur_ponderee: -0.4516842533419668
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.08970438328236474
    valeur_normalisee: 0.8339668000186402
    valeur_ponderee: 0.8339668000186402
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.08638211382113825
    valeur_normalisee: 0.9790859255561687
    valeur_ponderee: 0.9790859255561687
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_sucre:
    valeur: 0.00375586854460086
    valeur_normalisee: 0.008150255719454397
    valeur_ponderee: 0.008150255719454397
    ts: '2026-08-13T05:23:11.346069+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 49.73333333333333
      7j: 49.73333333333333
      1m: 49.73333333333333
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
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: structurel
    event_id: 15780fa2ca51
    event_date: '2026-08-07T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 49.73333333333333
      7j: 49.73333333333333
      1m: 49.73333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-08-13T05:23:11.346069+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.5499999999999998
    valeur_normalisee: 0.3615940798841089
    valeur_ponderee: 0.3615940798841089
    ts: '2026-08-13T05:23:11.346069+00:00'
  dxy_trend_20j:
    valeur: 119.0649
    valeur_normalisee: -0.6362460776563852
    valeur_ponderee: -0.6362460776563852
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.0054471058515261905
    valeur_normalisee: 0.2413264676634427
    valeur_ponderee: 0.2413264676634427
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_3j_usdjpy:
    valeur: 0.00011053440592090347
    valeur_normalisee: 0.01962506634841583
    valeur_ponderee: 0.01962506634841583
    ts: '2026-08-13T05:23:11.346069+00:00'
  momentum_prix_20j_usdjpy:
    valeur: -0.027581944479451836
    valeur_normalisee: -0.8708921452571329
    valeur_ponderee: -0.8708921452571329
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_jpy_nets:
    valeur: -46951.0
    valeur_normalisee: -0.009726152296552546
    valeur_ponderee: -0.009726152296552546
    ts: '2026-08-13T05:23:11.346069+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0300000000000002
    valeur_normalisee: 0.7627500851943896
    valeur_ponderee: 0.7627500851943896
    ts: '2026-08-13T05:23:11.346069+00:00'
  boj_intervention_risk:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-08-13T05:23:11.346069+00:00'
    nature: ponctuel
    event_id: 267712266c81
    event_date: '2026-08-11T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '2.22'
    p2_shadow_contrib_exclu:
      24h: 6.066666666666667
      7j: 6.066666666666667
      1m: 6.066666666666667
  gate_regime_extreme:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-08-13T05:23:11.346069+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-08-13T05:23:11.346069+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-08-13T05:23:11.346069+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-08-13T05:23:11.346069+00:00'
  gap_rv_iv:
    valeur: -1.24952223975251
    ts: '2026-08-13T05:23:11.346069+00:00'
  cftc_cot_vix_nets:
    valeur: -61109.0
    valeur_normalisee: -0.17603530735988018
    valeur_ponderee: -0.17603530735988018
    ts: '2026-08-13T05:23:11.346069+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-08-13T05:23:11.346069+00:00'
    synthese_rationale: 'Blocus persistant du détroit d''Ormuz, attaques en mer Rouge
      et golfe d''Oman, et prévision EIA de 600k barils/jour hors marché jusqu''à
      fin 2027 : signal LONG massif et cohérent. Malgré la baisse récente du VIX,
      la fraîcheur et la matérialité élevée des news (toutes ≤ 48h) indiquent une
      escalade géopo'
    nature: structurel
    event_id: 54d27362d3ad
    event_date: '2026-08-13T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 354.56666666666524
      7j: 354.56666666666524
      1m: 354.56666666666524
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-08-13T05:23:11.346069+00:00'
```
