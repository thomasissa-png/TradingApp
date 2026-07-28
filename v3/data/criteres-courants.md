# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-07-28T05:23:16.539857+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.9446120352625141
    valeur_ponderee: 0.9446120352625141
    ts: '2026-07-28T05:23:16.539857+00:00'
  mouvement_or_5j:
    valeur: -0.0015642833305086201
    valeur_normalisee: 0.14399961248612486
    valeur_ponderee: 0.14399961248612486
    ts: '2026-07-28T05:23:16.539857+00:00'
  ratio_gold_silver:
    valeur: 70.78347913662414
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_silver:
    valeur: 20569.0
    valeur_normalisee: -0.303970612481078
    valeur_ponderee: -0.303970612481078
    ts: '2026-07-28T05:23:16.539857+00:00'
  flux_etf_slv_pslv_5j:
    valeur: 0.03825029423303272
    valeur_normalisee: 0.3945198749332356
    valeur_ponderee: 0.3945198749332356
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_argent:
    valeur: -0.01971711729576564
    valeur_normalisee: 0.8101375037236287
    valeur_ponderee: 0.8101375037236287
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_argent:
    valeur: -0.027938915378335927
    valeur_normalisee: 0.007000912364295198
    valeur_ponderee: 0.007000912364295198
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_argent:
    valeur: -0.017945915477466934
    valeur_normalisee: -0.07062182476443586
    valeur_ponderee: -0.07062182476443586
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
ble:
  noaa_drought_midwest_plains:
    valeur: 0.3783375536277475
    valeur_normalisee: 0.18916877681387376
    valeur_ponderee: 0.18916877681387376
    ts: '2026-07-28T05:23:16.539857+00:00'
  geopolitique_mer_noire:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Multiples news high matérialité récentes (23 juillet) confirment
      Black Sea export risks et baisse USDA des stocks mondiaux, dominant le signal.
      Le prix a déjà monté +9.73% sur 20j, mais la fraîcheur et la force des news
      justifient le maintien du biais long.
    nature: structurel
    event_id: fd630a45bbcc
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 60.73333333333336
      7j: 60.73333333333336
      1m: 60.73333333333336
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_wheat:
    valeur: -14250.0
    valeur_normalisee: 0.40842367936126867
    valeur_ponderee: 0.40842367936126867
    ts: '2026-07-28T05:23:16.539857+00:00'
  meteo_australie_dryland:
    valeur: -0.005468858215597745
    valeur_normalisee: -0.0027344291077988723
    valeur_ponderee: -0.0027344291077988723
    ts: '2026-07-28T05:23:16.539857+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_ble:
    valeur: 0.09686428436837757
    valeur_normalisee: 0.44013364240968217
    valeur_ponderee: 0.44013364240968217
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_ble:
    valeur: -0.02735920420666016
    valeur_normalisee: -0.37449280754892345
    valeur_ponderee: -0.37449280754892345
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_ble:
    valeur: -0.02802136818000578
    valeur_normalisee: -0.5738157937841702
    valeur_ponderee: -0.5738157937841702
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-28T05:23:16.539857+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.71
    valeur_normalisee: 0.3848685183169597
    valeur_ponderee: 0.3848685183169597
    ts: '2026-07-28T05:23:16.539857+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.011950111899463822
    valeur_normalisee: 0.3678407659709989
    valeur_ponderee: 0.3678407659709989
    ts: '2026-07-28T05:23:16.539857+00:00'
  flux_etf_msci_france_5j:
    valeur: 0.012516763522574692
    valeur_normalisee: 0.40072807627901935
    valeur_ponderee: 0.40072807627901935
    ts: '2026-07-28T05:23:16.539857+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: 'Dominance de news SHORT à matérialité élevée et très récentes
      (27 juillet) : tarifs douaniers Trump, guerre Iran-USA, choc énergétique. Le
      léger rebond du CAC40 (+0.46% sur 20j) est marginal face à ce flux négatif massif
      et frais.'
    nature: structurel
    event_id: 63503e3a50d4
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: -129.83333333333348
      7j: -129.83333333333348
      1m: -129.83333333333348
    sign_conflict: true
    sign_conflict_details:
    - event_id: 351a6b7e7bc6
      asset: CAC40
      rule_name: cpi_actions
      expected_direction: LONG
      ia_direction: SHORT
      matched_subject: inflation
      matched_surprise: baisse
      surprise_polarity: down
      title: Baisse temporaire de l'inflation en juin, hausse attendue par la suite
  rsi_14j_fchi:
    valeur: 54.57843373517047
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.004628655691804484
    valeur_normalisee: -0.07461309010976412
    valeur_ponderee: -0.07461309010976412
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_cac40:
    valeur: 0.003365921467048505
    valeur_normalisee: -0.010743498834274858
    valeur_ponderee: -0.010743498834274858
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_cac40:
    valeur: -0.0037722797192542012
    valeur_normalisee: -0.2229343125972897
    valeur_ponderee: -0.2229343125972897
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-07-28T05:23:16.539857+00:00'
    reporte: true
    reporte_age_j: 4
    reporte_date: '2026-07-22'
    valeur: 0.3822598866442453
    valeur_normalisee: 0.19112994332212266
    valeur_ponderee: 0.19112994332212266
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -13050.0
    valeur_normalisee: -0.5555916820879753
    valeur_ponderee: -0.5555916820879753
    ts: '2026-07-28T05:23:16.539857+00:00'
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    event_id: ed85122594ec
    event_date: '2026-07-21T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '7.22'
    p2_shadow_contrib_exclu:
      24h: 90.2666666666669
      7j: 90.2666666666669
      1m: 90.2666666666669
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  maladies_cabosses:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Les news récentes sont dominées par des signaux SHORT (abondance
      d'offre, demande faible) mais une news LONG à matérialité high du 21 juillet
      (Super El Niño) contredit ce biais. Le prix a baissé de 14.71% sur 20j, suggérant
      que le marché a déjà intégré les facteurs baissiers, et la fraîcheur de la n
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 181.46666666666636
      7j: 181.46666666666636
      1m: 181.46666666666636
  momentum_prix_20j_cacao:
    valeur: -0.14710028557832844
    valeur_normalisee: -0.7962427259752334
    valeur_ponderee: -0.7962427259752334
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_cacao:
    valeur: -0.08079859383441246
    valeur_normalisee: -0.5930358601726694
    valeur_ponderee: -0.5930358601726694
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_cacao:
    valeur: -0.03325186163960259
    valeur_normalisee: -0.37362407201746195
    valeur_ponderee: -0.37362407201746195
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-28T05:23:16.539857+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.38863129900019383
    valeur_normalisee: 0.19431564950009692
    valeur_ponderee: 0.19431564950009692
    ts: '2026-07-28T05:23:16.539857+00:00'
  usd_brl:
    valeur: 5.12609
    valeur_normalisee: 0.0039802809460789705
    valeur_ponderee: 0.0039802809460789705
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_coffee:
    valeur: 26034.0
    valeur_normalisee: -0.19563028321574708
    valeur_ponderee: -0.19563028321574708
    ts: '2026-07-28T05:23:16.539857+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Majorité de news LONG (USDA haussier, tarifs US sur Brésil,
      El Niño) dominent, mais une news SHORT high (tarif US 25% sur Brésil le 22/07)
      et le prix déjà en hausse (+3.94% sur 5j) limitent la conviction.
    nature: structurel
    event_id: 6f566bc3932f
    event_date: '2026-07-06T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '22.22'
    p2_shadow_contrib_exclu:
      24h: 93.83333333333343
      7j: 93.83333333333343
      1m: 93.83333333333343
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
    ts: '2026-07-28T05:23:16.539857+00:00'
  meteo_vietnam_robusta:
    valeur: 0.34374146970113334
    valeur_normalisee: 0.17187073485056667
    valeur_ponderee: 0.17187073485056667
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.029943090343780288
    valeur_normalisee: -0.15046154273206233
    valeur_ponderee: -0.15046154273206233
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.0007406998855195024
    valeur_normalisee: -0.14363652308536273
    valeur_ponderee: -0.14363652308536273
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_cafe:
    valeur: 0.028869676479203354
    valeur_normalisee: 0.22553682520795898
    valeur_ponderee: 0.22553682520795898
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-28T05:23:16.539857+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.379028426435131
    valeur_normalisee: 0.1895142132175655
    valeur_ponderee: 0.1895142132175655
    ts: '2026-07-28T05:23:16.539857+00:00'
  meteo_inde_gujarat_coton:
    ts: '2026-07-28T05:23:16.539857+00:00'
    reporte: true
    reporte_age_j: 3
    reporte_date: '2026-07-23'
    valeur: 0.05646156344348821
    valeur_normalisee: 0.028230781721744105
    valeur_ponderee: 0.028230781721744105
    reporte_cause: source réseau indisponible
  cftc_cot_cotton:
    valeur: 100360.0
    valeur_normalisee: 0.7692072556094062
    valeur_ponderee: 0.7692072556094062
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_coton:
    valeur: 0.05754637436762233
    valeur_normalisee: 0.34834682885368595
    valeur_ponderee: 0.34834682885368595
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_coton:
    valeur: 0.021792260692464316
    valeur_normalisee: 0.2675246612967771
    valeur_ponderee: 0.2675246612967771
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_coton:
    valeur: -0.005550049554013836
    valeur_normalisee: -0.06464971340923992
    valeur_ponderee: -0.06464971340923992
    ts: '2026-07-28T05:23:16.539857+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  demande_chine_coton:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    event_id: f37165710bf1
    event_date: '2026-07-22T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '6.22'
    p2_shadow_contrib_exclu:
      24h: 35.73333333333328
      7j: 35.73333333333328
      1m: 35.73333333333328
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-28T05:23:16.539857+00:00'
cuivre:
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Plusieurs news LONG à matérialité high du 23 juillet (prix
      proches du record sur tensions Chine/tarifs) et du 16 juillet (tarifs US, plan
      EU) dominent, mais des news SHORT récentes (ralentissement profits chinois,
      ventes auto) et le contexte de prix déjà en hausse (+3.9%/20j) limitent la conviction.
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 16.16666666666668
      7j: 16.16666666666668
      1m: 16.16666666666668
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_copper_nets:
    valeur: 74822.0
    valeur_normalisee: 0.9967771915326051
    valeur_ponderee: 0.9967771915326051
    ts: '2026-07-28T05:23:16.539857+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    event_id: 7b613f670a0f
    event_date: '2026-07-23T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.22'
    p2_shadow_contrib_exclu:
      24h: 32.333333333333336
      7j: 32.333333333333336
      1m: 32.333333333333336
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  ratio_cuivre_or:
    valeur: 0.0015591856350082875
    valeur_normalisee: 0.596216919236476
    valeur_ponderee: 0.596216919236476
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_cuivre:
    valeur: 0.039005110912234464
    valeur_normalisee: 0.6765348099951043
    valeur_ponderee: 0.6765348099951043
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.028105088053872906
    valeur_normalisee: -0.5752610786139185
    valeur_ponderee: -0.5752610786139185
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_cuivre:
    valeur: 5.552277068154865e-05
    valeur_normalisee: 0.004024346450227846
    valeur_ponderee: 0.004024346450227846
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.5580471795
    valeur_normalisee: 0.2515534807525991
    valeur_ponderee: 0.2515534807525991
    ts: '2026-07-28T05:23:16.539857+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.7200000000000002
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-28T05:23:16.539857+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  usd_jpy_proxy_risk:
    valeur: 163.75712
    valeur_normalisee: 0.9027794656087952
    valeur_ponderee: 0.9027794656087952
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_eur_nets:
    valeur: -65177.0
    valeur_normalisee: -0.8513400297335095
    valeur_ponderee: -0.8513400297335095
    ts: '2026-07-28T05:23:16.539857+00:00'
  balance_commerciale_ez:
    valeur: -7776.2
    valeur_normalisee: -0.9342360836841009
    valeur_ponderee: -0.9342360836841009
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.0047123124490887625
    valeur_normalisee: 0.1850434863798288
    valeur_ponderee: 0.1850434863798288
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_eurusd:
    valeur: -0.0030531940094229437
    valeur_normalisee: -0.04418466895880602
    valeur_ponderee: -0.04418466895880602
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_eurusd:
    valeur: -0.0009758928100439546
    valeur_normalisee: 0.025336251163519653
    valeur_ponderee: 0.025336251163519653
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.9446120352625141
    valeur_ponderee: 0.9446120352625141
    ts: '2026-07-28T05:23:16.539857+00:00'
  sox_trend_5j:
    valeur: 516.22998
    valeur_normalisee: -0.4509297495203109
    valeur_ponderee: -0.4509297495203109
    ts: '2026-07-28T05:23:16.539857+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.17049785961414413
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-28T05:23:16.539857+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée le 28 juillet
      (craintes IA chinoise, déroute technologique asiatique, dollar fort) malgré
      quelques news LONG sur Nvidia. Le contexte de baisse de prix (-3.45% sur 20j)
      confirme le biais baissier.
    nature: structurel
    event_id: b02f553d6371
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 75.5333333333334
      7j: 75.5333333333334
      1m: 75.5333333333334
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  flux_etf_qqq_5j:
    valeur: -0.020027006350104792
    valeur_normalisee: -0.44270769928404424
    valeur_ponderee: -0.44270769928404424
    ts: '2026-07-28T05:23:16.539857+00:00'
  spread_nasdaq_russell2000:
    valeur: 389.21
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    ts: '2026-07-28T05:23:16.539857+00:00'
  rsi_14j_ixic:
    valeur: 38.15191327976984
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.03453549695591085
    valeur_normalisee: -0.5800878036287735
    valeur_ponderee: -0.5800878036287735
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_nasdaq:
    valeur: -0.033742244383375475
    valeur_normalisee: -0.6104970812389238
    valeur_ponderee: -0.6104970812389238
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_nasdaq:
    valeur: -0.03293397697409728
    valeur_normalisee: -0.7387630705616286
    valeur_ponderee: -0.7387630705616286
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.9446120352625141
    valeur_ponderee: 0.9446120352625141
    ts: '2026-07-28T05:23:16.539857+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_nets:
    valeur: 176195.0
    valeur_normalisee: -0.19033380690269922
    valeur_ponderee: -0.19033380690269922
    ts: '2026-07-28T05:23:16.539857+00:00'
  flux_etf_or_5j:
    valeur: 0.019124020154406507
    valeur_normalisee: 0.5502043828286894
    valeur_ponderee: 0.5502043828286894
    ts: '2026-07-28T05:23:16.539857+00:00'
  tension_geopolitique:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Majorité de news SHORT récentes (désescalade US-Iran, dollar
      fort, attentes Fed) dominent malgré quelques signaux LONG. Le prix est en baisse
      modérée, cohérent avec le biais SHORT.
    nature: structurel
    event_id: d0c9fa728b22
    event_date: '2026-07-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 185.70000000000007
      7j: 185.70000000000007
      1m: 185.70000000000007
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-07-28T05:23:16.539857+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_or:
    valeur: -0.008362635644296401
    valeur_normalisee: 0.5377675535623477
    valeur_ponderee: 0.5377675535623477
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_or:
    valeur: -0.008496327528774716
    valeur_normalisee: 0.06118202548791936
    valeur_ponderee: 0.06118202548791936
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_or:
    valeur: -0.0031632333132960433
    valeur_normalisee: 0.04220892403412108
    valeur_ponderee: 0.04220892403412108
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
petrole:
  eia_crude_surprise:
    ts: '2026-07-28T05:23:16.539857+00:00'
    reporte: true
    reporte_age_j: 2
    reporte_date: '2026-07-24'
    valeur: 411675.0
    valeur_normalisee: -0.5782047119748305
    valeur_ponderee: -0.5782047119748305
    reporte_cause: hors_fenetre — eia_crude_surprise
  tension_geopol_moyen_orient:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.6
    materiality: medium
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: Majorité de news SHORT à matérialité élevée et fraîcheur récente
      (27-28 juillet) signalent une désescalade US-Iran, avec chute du pétrole de
      7-8%. Les quelques news LONG sont plus anciennes ou de moindre matérialité,
      et le contexte de prix (-7.31% sur 5j) confirme le biais baissier.
    nature: structurel
    event_id: d0c9fa728b22
    event_date: '2026-07-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 161.66666666666694
      7j: 161.66666666666694
      1m: 161.66666666666694
  cftc_cot_crude_nets:
    valeur: 42761.0
    valeur_normalisee: 0.3587204635040612
    valeur_ponderee: 0.3587204635040612
    ts: '2026-07-28T05:23:16.539857+00:00'
  opec_production_policy:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    event_id: d4b4caf8d043
    event_date: '2026-07-28T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.22'
    p2_shadow_contrib_exclu:
      24h: 164.4666666666669
      7j: 164.4666666666669
      1m: 164.4666666666669
    sign_conflict: true
    sign_conflict_details:
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
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  cushing_stocks:
    valeur: 19370.0
    valeur_normalisee: -0.7071724108334729
    valeur_ponderee: -0.7071724108334729
    ts: '2026-07-28T05:23:16.539857+00:00'
  spread_brent_wti:
    valeur: 3.2061399999999907
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_petrole:
    valeur: 0.15447212066685223
    valeur_normalisee: 0.6421373055519133
    valeur_ponderee: 0.6421373055519133
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.03826568452041501
    valeur_normalisee: -0.11002727482037152
    valeur_ponderee: -0.11002727482037152
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_petrole:
    valeur: -0.10742327040918276
    valeur_normalisee: -0.8205355260585977
    valeur_ponderee: -0.8205355260585977
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-07-28T05:23:16.539857+00:00'
  taux_10y_us_delta_5j:
    valeur: 0.14000000000000057
    valeur_normalisee: 0.6221144565871279
    valeur_ponderee: 0.6221144565871279
    ts: '2026-07-28T05:23:16.539857+00:00'
  hy_credit_spread:
    valeur: 2.79
    valeur_normalisee: 0.49009802940980324
    valeur_ponderee: 0.49009802940980324
    ts: '2026-07-28T05:23:16.539857+00:00'
  breadth_sp_ma50:
    valeur: 0.291141785356549
    valeur_normalisee: 0.9832706192113086
    valeur_ponderee: 0.9832706192113086
    ts: '2026-07-28T05:23:16.539857+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.004042636190824345
    valeur_normalisee: -0.24798280906786885
    valeur_ponderee: -0.24798280906786885
    ts: '2026-07-28T05:23:16.539857+00:00'
  shiller_cape_fwd_pe:
    valeur: 40.47
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-28T05:23:16.539857+00:00'
  rsi_14j_gspc:
    valeur: 44.63495449833472
    ts: '2026-07-28T05:23:16.539857+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.43
    valeur_normalisee: 0.9446120352625141
    valeur_ponderee: 0.9446120352625141
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_sp500:
    valeur: 0.01385483633321205
    valeur_normalisee: -0.17818556826446907
    valeur_ponderee: -0.17818556826446907
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_sp500:
    valeur: -0.015491719235869006
    valeur_normalisee: -0.5725578157552608
    valeur_ponderee: -0.5725578157552608
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_sp500:
    valeur: -0.011131699246666571
    valeur_normalisee: -0.5104880656071913
    valeur_ponderee: -0.5104880656071913
    ts: '2026-07-28T05:23:16.539857+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-07-28T05:23:16.539857+00:00'
    reporte: true
    reporte_age_j: 4
    reporte_date: '2026-07-22'
    valeur: -0.2138384775982998
    valeur_normalisee: 0.1069192387991499
    valeur_ponderee: 0.1069192387991499
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 84.74144
    valeur_normalisee: -0.17874260522654392
    valeur_ponderee: -0.17874260522654392
    ts: '2026-07-28T05:23:16.539857+00:00'
  usd_brl_sucre:
    valeur: 5.12609
    valeur_normalisee: 0.0039802809460789705
    valeur_ponderee: 0.0039802809460789705
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_sugar:
    valeur: -47496.0
    valeur_normalisee: -0.431259358767976
    valeur_ponderee: -0.431259358767976
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_sucre:
    valeur: -0.0010395010395010118
    valeur_normalisee: -0.11308566645295894
    valeur_ponderee: -0.11308566645295894
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.008394543546694555
    valeur_normalisee: 0.06299555155634047
    valeur_ponderee: 0.06299555155634047
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_sucre:
    valeur: -0.011316872427983626
    valeur_normalisee: -0.23920823422127407
    valeur_ponderee: -0.23920823422127407
    ts: '2026-07-28T05:23:16.539857+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 32.033333333333275
      7j: 32.033333333333275
      1m: 32.033333333333275
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
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    event_id: 8ffa1516a530
    event_date: '2026-07-27T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.22'
    p2_shadow_contrib_exclu:
      24h: 32.033333333333275
      7j: 32.033333333333275
      1m: 32.033333333333275
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-07-28T05:23:16.539857+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.6600000000000001
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-28T05:23:16.539857+00:00'
  dxy_trend_20j:
    valeur: 120.7105
    valeur_normalisee: 0.4918758400550825
    valeur_ponderee: 0.4918758400550825
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.0033147746798762867
    valeur_normalisee: 0.008532144014946763
    valeur_ponderee: 0.008532144014946763
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_3j_usdjpy:
    valeur: -0.0006317850368499078
    valeur_normalisee: -0.3029367921727489
    valeur_ponderee: -0.3029367921727489
    ts: '2026-07-28T05:23:16.539857+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.006814564684811231
    valeur_normalisee: -0.22236850427457455
    valeur_ponderee: -0.22236850427457455
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_jpy_nets:
    valeur: -157406.0
    valeur_normalisee: -0.6920714340123324
    valeur_ponderee: -0.6920714340123324
    ts: '2026-07-28T05:23:16.539857+00:00'
  diff_taux_10y_us_jp:
    valeur: 2.0200000000000005
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-07-28T05:23:16.539857+00:00'
  boj_intervention_risk:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-07-28T05:23:16.539857+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 1.4333333333333318
      7j: 1.4333333333333318
      1m: 1.4333333333333318
  gate_regime_extreme:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-07-28T05:23:16.539857+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-07-28T05:23:16.539857+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-07-28T05:23:16.539857+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-07-28T05:23:16.539857+00:00'
  gap_rv_iv:
    valeur: -3.9211370616782837
    ts: '2026-07-28T05:23:16.539857+00:00'
  cftc_cot_vix_nets:
    valeur: -76861.0
    valeur_normalisee: -0.47810632841843353
    valeur_ponderee: -0.47810632841843353
    ts: '2026-07-28T05:23:16.539857+00:00'
  tension_geopolitique_active:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-07-28T05:23:16.539857+00:00'
    synthese_rationale: 'Signaux contradictoires : news récentes de désescalade US-Iran
      (SHORT) s''opposent aux news de chute technologique et d''inquiétudes IA (LONG).
      Le prix VIX est quasi stable sur 5j (+0.71%), suggérant que le marché n''a pas
      tranché.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 419.9999999999984
      7j: 419.9999999999984
      1m: 419.9999999999984
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-07-28T05:23:16.539857+00:00'
```
