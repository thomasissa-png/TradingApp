# Critères courants — généré par criteres_calculator.py
# Source de vérité du moteur de scoring (Analyste).

```yaml
last_update: '2026-06-30T06:04:12.876566+00:00'
argent:
  taux_10y_us_reels_tips:
    valeur: 2.18
    valeur_normalisee: 0.5636005097590084
    valeur_ponderee: 0.5636005097590084
    ts: '2026-06-30T06:04:12.876566+00:00'
  mouvement_or_5j:
    valeur: -0.010052772738553317
    valeur_normalisee: 0.028519716370644457
    valeur_ponderee: 0.028519716370644457
    ts: '2026-06-30T06:04:12.876566+00:00'
  ratio_gold_silver:
    valeur: 69.30708706340408
    ts: '2026-06-30T06:04:12.876566+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-30T06:04:12.876566+00:00'
    note: hors fenêtre
  cftc_cot_silver:
    valeur: 23389.0
    valeur_normalisee: -0.22071937560278862
    valeur_ponderee: -0.22071937560278862
    ts: '2026-06-30T06:04:12.876566+00:00'
  flux_etf_slv_pslv_5j:
    valeur: -0.10575454082498725
    valeur_normalisee: -0.6104931820974692
    valeur_ponderee: -0.6104931820974692
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_argent:
    valeur: -0.09402387447883087
    valeur_normalisee: -0.2231639700074737
    valeur_ponderee: -0.2231639700074737
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_argent:
    valeur: -0.06678156730052065
    valeur_normalisee: -0.2747412857079082
    valeur_ponderee: -0.2747412857079082
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
ble:
  usda_wasde_stocks_to_use:
    valeur_normalisee: 0.0
    ts: '2026-06-30T06:04:12.876566+00:00'
    note: hors fenêtre
  noaa_drought_midwest_plains:
    valeur: 0.3168270000804747
    valeur_normalisee: 0.15841350004023735
    valeur_ponderee: 0.15841350004023735
    ts: '2026-06-30T06:04:12.876566+00:00'
  geopolitique_mer_noire:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Majorité de news LONG (El Niño, guerre, demande USDA) mais
      prix en baisse de 1.67% sur 20j et 2.64% sur 5j, suggérant que le marché a déjà
      intégré ces facteurs. Une seule news SHORT (dollar fort) de conviction high,
      mais ancienne (18 juin).
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: -23.19999999999997
      7j: -23.19999999999997
      1m: -23.19999999999997
  cftc_cot_wheat:
    valeur: -61072.0
    valeur_normalisee: -0.23819600021494963
    valeur_ponderee: -0.23819600021494963
    ts: '2026-06-30T06:04:12.876566+00:00'
  meteo_australie_dryland:
    valeur: 0.10035196401566776
    valeur_normalisee: 0.05017598200783388
    valeur_ponderee: 0.05017598200783388
    ts: '2026-06-30T06:04:12.876566+00:00'
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_ble:
    valeur: -0.017422690319784717
    valeur_normalisee: -0.10339368442449462
    valeur_ponderee: -0.10339368442449462
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_ble:
    valeur: -0.022392710159087614
    valeur_normalisee: -0.1712431293536443
    valeur_ponderee: -0.1712431293536443
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
cac40:
  spread_oat_bund_10y:
    valeur: 0.6951
    valeur_normalisee: 0.34043669656849884
    valeur_ponderee: 0.34043669656849884
    ts: '2026-06-30T06:04:12.876566+00:00'
  alpha_cac_vs_sp_5j:
    valeur: 0.0006517159440819764
    valeur_normalisee: 0.13231422433269197
    valeur_ponderee: 0.13231422433269197
    ts: '2026-06-30T06:04:12.876566+00:00'
  flux_etf_msci_france_5j:
    valeur: -0.0008847600088476293
    valeur_normalisee: -0.10915735364119367
    valeur_ponderee: -0.10915735364119367
    ts: '2026-06-30T06:04:12.876566+00:00'
  tension_politique_fr:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -1.0
    materiality: high
    reliability: confirmed
    source_track: ia_synthese
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (tensions Iran,
      contraction PIB zone euro, menaces tarifaires US) sur les 5 derniers jours,
      malgré une news LONG récente (China PMI) de matérialité moyenne. Le prix a légèrement
      baissé sur 5j (-0.39%), cohérent avec le biais négatif.
    nature: structurel
    event_id: 68cc3ee14491
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: -66.69999999999999
      7j: -66.69999999999999
      1m: -66.69999999999999
    sign_conflict: true
    sign_conflict_details:
    - event_id: eb6dec57006e
      asset: CAC40
      rule_name: fed_actions
      expected_direction: SHORT
      ia_direction: LONG
      matched_subject: bce
      matched_surprise: hawkish
      surprise_polarity: up
      title: Les rendements de la zone euro proches de plus bas de 3 mois, les craintes
        de croissance limitent le ton hawkish de la BCE
  rsi_14j_fchi:
    valeur: 54.320227876468856
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_cac40:
    valeur: 0.02709602966828628
    valeur_normalisee: 0.14341700029722443
    valeur_ponderee: 0.14341700029722443
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_cac40:
    valeur: -0.011885996945385058
    valeur_normalisee: -0.43105207929776046
    valeur_ponderee: -0.43105207929776046
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
cacao:
  meteo_ci_ghana_precip_30j:
    ts: '2026-06-30T06:04:12.876566+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-06-29'
    valeur: 0.9950209185486898
    valeur_normalisee: 0.4975104592743449
    valeur_ponderee: 0.4975104592743449
    reporte_cause: source réseau indisponible
  hf_positioning_flux_options:
    valeur: -27525.0
    valeur_normalisee: -0.8248926081081333
    valeur_ponderee: -0.8248926081081333
    ts: '2026-06-30T06:04:12.876566+00:00'
  grindings_q:
    valeur_normalisee: 0.0
    ts: '2026-06-30T06:04:12.876566+00:00'
    note: hors fenêtre
  eudr:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: structurel
    event_id: c38af322cc46
    event_date: '2026-06-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
    p2_shadow_contrib_exclu:
      24h: 12.466666666666647
      7j: 12.466666666666647
      1m: 12.466666666666647
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
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Dominance de news LONG sur El Niño et craintes sur l'offre
      ouest-africaine, dont une matérialité high le 25 juin. La news SHORT du 29 juin
      (offre abondante) est isolée et ne renverse pas le signal malgré le récent +30%
      de prix, car la fraîcheur et la matérialité des news LONG restent fortes.
    nature: structurel
    event_id: c38af322cc46
    event_date: '2026-06-25T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '5.25'
    p2_shadow_contrib_exclu:
      24h: 12.466666666666647
      7j: 12.466666666666647
      1m: 12.466666666666647
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  momentum_prix_20j_cacao:
    valeur: 0.3054510859198962
    valeur_normalisee: 0.6941858173839089
    valeur_ponderee: 0.6941858173839089
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_cacao:
    valeur: 0.06515790128543775
    valeur_normalisee: 0.06081961184914918
    valeur_ponderee: 0.06081961184914918
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
cafe:
  meteo_bresil_minas_gerais:
    valeur: -0.33647484859011906
    valeur_normalisee: 0.16823742429505953
    valeur_ponderee: 0.16823742429505953
    ts: '2026-06-30T06:04:12.876566+00:00'
  usd_brl:
    valeur: 5.17347
    valeur_normalisee: 0.6046775843945823
    valeur_ponderee: 0.6046775843945823
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_coffee:
    valeur: 10724.0
    valeur_normalisee: -0.49837226534013546
    valeur_ponderee: -0.49837226534013546
    ts: '2026-06-30T06:04:12.876566+00:00'
  maladies_cabosses_rouille:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Pluies abondantes au Brésil retardent la récolte d'arabica
      (29 juin, high) et le déficit de mousson en Inde (29 juin, medium) renforcent
      les risques d'offre, dominant les signaux SHORT plus anciens. Le prix a déjà
      monté de 13% sur 20j, mais les news fraîches à haute matérialité confirment
      la tendanc
    nature: structurel
    event_id: 46c5edfd284d
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: 55.1
      7j: 55.1
      1m: 55.1
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
    ts: '2026-06-30T06:04:12.876566+00:00'
  meteo_vietnam_robusta:
    valeur: 0.06420670081127436
    valeur_normalisee: 0.03210335040563718
    valeur_ponderee: 0.03210335040563718
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_cafe:
    valeur: 0.1335581547641509
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_cafe:
    valeur: 0.006919907111088364
    valeur_normalisee: 0.14360767609007455
    valeur_ponderee: 0.14360767609007455
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
coton:
  meteo_texas_cotton_precip:
    valeur: 0.3262536316567442
    valeur_normalisee: 0.1631268158283721
    valeur_ponderee: 0.1631268158283721
    ts: '2026-06-30T06:04:12.876566+00:00'
  meteo_inde_gujarat_coton:
    valeur: -0.24936775845238357
    valeur_normalisee: 0.12468387922619178
    valeur_ponderee: 0.12468387922619178
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_cotton:
    valeur: 84973.0
    valeur_normalisee: 0.6158899306252916
    valeur_ponderee: 0.6158899306252916
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_coton:
    valeur: -0.06834249803613512
    valeur_normalisee: -0.4621367751519508
    valeur_ponderee: -0.4621367751519508
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_coton:
    valeur: -0.033020790868324434
    valeur_normalisee: -0.37387649828962793
    valeur_ponderee: -0.37387649828962793
    ts: '2026-06-30T06:04:12.876566+00:00'
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  demande_chine_coton:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: structurel
    event_id: c81278f1f56b
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: 1.633333333333333
      7j: 1.633333333333333
      1m: 1.633333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
cuivre:
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-30T06:04:12.876566+00:00'
    note: hors fenêtre
  mining_strikes_chili_perou:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Dominance des news LONG récentes (PMI chinois, demande IA)
      malgré des signaux SHORT plus anciens sur les tensions commerciales. Le prix
      a baissé de 3.38% sur 20j, ce qui suggère que le marché n'a pas encore intégré
      le catalyseur haussier du jour (PMI chinois supérieur aux attentes).
    nature: structurel
    event_id: 80bd37f67f01
    event_date: '2026-06-26T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '4.25'
    p2_shadow_contrib_exclu:
      24h: 1.7333333333333332
      7j: 1.7333333333333332
      1m: 1.7333333333333332
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_copper_nets:
    valeur: 73012.0
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-30T06:04:12.876566+00:00'
  news_construction_infra:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: ponctuel
    event_id: e0b0ae927b9c
    event_date: '2026-06-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 15.066666666666663
      7j: 15.066666666666663
      1m: 15.066666666666663
  ratio_cuivre_or:
    valeur: 0.0015333334007364265
    valeur_normalisee: 0.6962207255786739
    valeur_ponderee: 0.6962207255786739
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_cuivre:
    valeur: -0.033843352181741504
    valeur_normalisee: -0.6187280888818272
    valeur_ponderee: -0.6187280888818272
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_cuivre:
    valeur: -0.0012288906973628722
    valeur_normalisee: -0.05550171711678568
    valeur_ponderee: -0.05550171711678568
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
eurusd:
  differentiel_taux_2y_us_de:
    valeur: 1.6171205073000001
    valeur_normalisee: 0.790277989859919
    valeur_ponderee: 0.790277989859919
    ts: '2026-06-30T06:04:12.876566+00:00'
  differentiel_taux_10y_us_bund:
    valeur: 1.3335
    valeur_normalisee: -0.3650676530980997
    valeur_ponderee: -0.3650676530980997
    ts: '2026-06-30T06:04:12.876566+00:00'
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  usd_jpy_proxy_risk:
    valeur: 162.36362
    valeur_normalisee: 0.8893550618488069
    valeur_ponderee: 0.8893550618488069
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_eur_nets:
    valeur: -24754.0
    valeur_normalisee: -0.591011209184829
    valeur_ponderee: -0.591011209184829
    ts: '2026-06-30T06:04:12.876566+00:00'
  balance_commerciale_ez:
    valeur: -1004.5
    valeur_normalisee: -0.6903957604646677
    valeur_ponderee: -0.6903957604646677
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_eurusd:
    valeur: -0.012976655888905175
    valeur_normalisee: -0.4735039071853067
    valeur_ponderee: -0.4735039071853067
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_eurusd:
    valeur: 0.0003689972061640123
    valeur_normalisee: 0.2799884241167483
    valeur_ponderee: 0.2799884241167483
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
nasdaq:
  taux_10y_us_reels_tips:
    valeur: 2.18
    valeur_normalisee: 0.5636005097590084
    valeur_ponderee: 0.5636005097590084
    ts: '2026-06-30T06:04:12.876566+00:00'
  sox_trend_5j:
    valeur: 614.34998
    valeur_normalisee: 0.6296468166712877
    valeur_ponderee: 0.6296468166712877
    ts: '2026-06-30T06:04:12.876566+00:00'
  breadth_nasdaq100_ma50:
    valeur: 0.16703954971871568
    valeur_normalisee: 0.5826229439022113
    valeur_ponderee: 0.5826229439022113
    ts: '2026-06-30T06:04:12.876566+00:00'
  sentiment_ia_megacaps:
    valeur: -1
    valeur_normalisee: -1.0
    valeur_ponderee: -0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Dominance de news SHORT à matérialité élevée (Kashkari hawkish,
      rout tech asiatique, restrictions Chine, tensions Iran) et fraîcheur récente,
      malgré quelques signaux LONG (SpaceX intégration, Nvidia). Le prix confirme
      la tendance baissière (-1.93% sur 20j).
    nature: structurel
    event_id: 0f10918805f7
    event_date: '2026-06-29T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '1.25'
    p2_shadow_contrib_exclu:
      24h: 28.83333333333333
      7j: 28.83333333333333
      1m: 28.83333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  flux_etf_qqq_5j:
    valeur: -0.01879530159502274
    valeur_normalisee: -0.5283248628790729
    valeur_ponderee: -0.5283248628790729
    ts: '2026-06-30T06:04:12.876566+00:00'
  spread_nasdaq_russell2000:
    valeur: 425.11001699999997
    valeur_normalisee: 0.2535873533262763
    valeur_ponderee: 0.2535873533262763
    ts: '2026-06-30T06:04:12.876566+00:00'
  rsi_14j_ixic:
    valeur: 52.68277984817595
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_nasdaq:
    valeur: -0.019273723774566154
    valeur_normalisee: -0.7258139382975202
    valeur_ponderee: -0.7258139382975202
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_nasdaq:
    valeur: 0.0021729899631426353
    valeur_normalisee: -0.3472348422065395
    valeur_ponderee: -0.3472348422065395
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: false
    ts: '2026-06-30T06:04:12.876566+00:00'
or:
  taux_10y_us_reels_tips:
    valeur: 2.18
    valeur_normalisee: 0.5636005097590084
    valeur_ponderee: 0.5636005097590084
    ts: '2026-06-30T06:04:12.876566+00:00'
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_nets:
    valeur: 172884.0
    valeur_normalisee: -0.2243003459079453
    valeur_ponderee: -0.2243003459079453
    ts: '2026-06-30T06:04:12.876566+00:00'
  flux_etf_or_5j:
    valeur: -0.04162877349905081
    valeur_normalisee: -0.5132539150864646
    valeur_ponderee: -0.5132539150864646
    ts: '2026-06-30T06:04:12.876566+00:00'
  tension_geopolitique:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_synthese_faible
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: 'Signaux contradictoires : tensions US-Iran (LONG) vs craintes
      de hausse de taux Fed (SHORT) s''équilibrent, sans dominance claire. Le prix
      a baissé de 2.14% sur 20j, suggérant que le marché a déjà intégré les pressions
      baissières, et les news récentes ne changent pas la donne de manière décisive.'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 177.20000000000005
      7j: 177.20000000000005
      1m: 177.20000000000005
  demande_indienne_saisonniere:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: calendrier
    ts: '2026-06-30T06:04:12.876566+00:00'
  vix_risk_off_proxy:
    valeur: 14.95
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_or:
    valeur: -0.02102661856188015
    valeur_normalisee: 0.41819820320764833
    valeur_ponderee: 0.41819820320764833
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_or:
    valeur: -0.030282866227350436
    valeur_normalisee: -0.2756813959728735
    valeur_ponderee: -0.2756813959728735
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
petrole:
  eia_crude_surprise:
    valeur_normalisee: 0.0
    ts: '2026-06-30T06:04:12.876566+00:00'
    note: hors fenêtre
  tension_geopol_moyen_orient:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Les news du 30 juin montrent un choc d'offre baissier (retour
      exportations Golfe) mais les tensions US-Iran soudaines et les frappes récentes
      (high matérialité) dominent, soutenues par des perturbations d'offre (raffineries
      ukrainiennes, réserves US au plus bas). Malgré la baisse de -25% sur 20j, la
    nature: structurel
    event_id: ff98f6fe0c25
    event_date: '2026-06-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 74.33333333333336
      7j: 74.33333333333336
      1m: 74.33333333333336
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  cftc_cot_crude_nets:
    valeur: 43084.0
    valeur_normalisee: 0.373459397087807
    valeur_ponderee: 0.373459397087807
    ts: '2026-06-30T06:04:12.876566+00:00'
  opec_production_policy:
    valeur: 0
    valeur_normalisee: 0.0
    valeur_ponderee: 0.0
    materiality: ''
    reliability: ''
    source_track: ia_conflict
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: structurel
    p2_shadow_contrib_exclu:
      24h: 68.50000000000001
      7j: 68.50000000000001
      1m: 68.50000000000001
    sign_conflict: true
    sign_conflict_details:
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
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  cushing_stocks:
    valeur: 18957.0
    valeur_normalisee: -0.8758656777574757
    valeur_ponderee: -0.8758656777574757
    ts: '2026-06-30T06:04:12.876566+00:00'
  spread_brent_wti:
    valeur: 3.4203899999999976
    ts: '2026-06-30T06:04:12.876566+00:00'
  caixin_pmi_manuf:
    valeur_normalisee: 0.0
    ts: '2026-06-30T06:04:12.876566+00:00'
    note: hors fenêtre
  momentum_prix_20j_petrole:
    valeur: -0.24965576732814931
    valeur_normalisee: -0.7532118446444415
    valeur_ponderee: -0.7532118446444415
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_petrole:
    valeur: -0.08942116932045452
    valeur_normalisee: -0.30274628525139924
    valeur_ponderee: -0.30274628525139924
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_evenement_extreme:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
sp500:
  vix_regime:
    valeur: 14.95
    valeur_normalisee: 0.9749999999999996
    valeur_ponderee: 0.9749999999999996
    ts: '2026-06-30T06:04:12.876566+00:00'
  taux_10y_us_delta_5j:
    valeur: -0.08000000000000007
    valeur_normalisee: -0.5177592280297248
    valeur_ponderee: -0.5177592280297248
    ts: '2026-06-30T06:04:12.876566+00:00'
  hy_credit_spread:
    valeur: 2.83
    valeur_normalisee: 0.23934603751041436
    valeur_ponderee: 0.23934603751041436
    ts: '2026-06-30T06:04:12.876566+00:00'
  breadth_sp_ma50:
    valeur: 0.28751687314439944
    valeur_normalisee: 0.4683538903578621
    valeur_ponderee: 0.4683538903578621
    ts: '2026-06-30T06:04:12.876566+00:00'
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  flux_etf_spy_ivv_5j:
    valeur: -0.004554077774364451
    valeur_normalisee: -0.31857261537826925
    valeur_ponderee: -0.31857261537826925
    ts: '2026-06-30T06:04:12.876566+00:00'
  shiller_cape_fwd_pe:
    valeur: 41.39
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    ts: '2026-06-30T06:04:12.876566+00:00'
  rsi_14j_gspc:
    valeur: 51.14530001965334
    ts: '2026-06-30T06:04:12.876566+00:00'
  taux_10y_us_reels_tips:
    valeur: 2.18
    valeur_normalisee: 0.5636005097590084
    valeur_ponderee: 0.5636005097590084
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_sp500:
    valeur: -0.020463172072313074
    valeur_normalisee: -0.7217910745930074
    valeur_ponderee: -0.7217910745930074
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_sp500:
    valeur: 5.395702726307405e-05
    valeur_normalisee: -0.3139508045760094
    valeur_ponderee: -0.3139508045760094
    ts: '2026-06-30T06:04:12.876566+00:00'
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
sucre:
  meteo_bresil_canne_sucre:
    ts: '2026-06-30T06:04:12.876566+00:00'
    reporte: true
    reporte_age_j: 1
    reporte_date: '2026-06-29'
    valeur: -0.17744248658840586
    valeur_normalisee: 0.08872124329420293
    valeur_ponderee: 0.08872124329420293
    reporte_cause: source réseau indisponible
  brent_ethanol_proxy_sucre:
    valeur: 73.41428
    valeur_normalisee: -0.9546887381205154
    valeur_ponderee: -0.9546887381205154
    ts: '2026-06-30T06:04:12.876566+00:00'
  usd_brl_sucre:
    valeur: 5.17347
    valeur_normalisee: 0.6046775843945823
    valeur_ponderee: 0.6046775843945823
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_sugar:
    valeur: -137708.0
    valeur_normalisee: -0.7941371369128345
    valeur_ponderee: -0.7941371369128345
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_sucre:
    valeur: 0.0025614754098362003
    valeur_normalisee: 0.1602920827649921
    valeur_ponderee: 0.1602920827649921
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_sucre:
    valeur: 0.04652406417112309
    valeur_normalisee: 0.614316500706815
    valeur_ponderee: 0.614316500706815
    ts: '2026-06-30T06:04:12.876566+00:00'
  prod_inde_thai_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: structurel
    event_id: 75ce573504f3
    event_date: '2026-06-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 1.8333333333333333
      7j: 1.8333333333333333
      1m: 1.8333333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported+keyword:could
  exports_bresil_sucre:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.7
    materiality: high
    reliability: reported
    source_track: ia
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: structurel
    event_id: 75ce573504f3
    event_date: '2026-06-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 1.8333333333333333
      7j: 1.8333333333333333
      1m: 1.8333333333333333
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported+keyword:could
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
usdjpy:
  diff_taux_2y_us_jp:
    valeur: 1.4200000000000004
    valeur_normalisee: 0.31088620154207885
    valeur_ponderee: 0.31088620154207885
    ts: '2026-06-30T06:04:12.876566+00:00'
  dxy_trend_20j:
    valeur: 120.8866
    valeur_normalisee: 0.9770730515100163
    valeur_ponderee: 0.9770730515100163
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_7j_usdjpy:
    valeur: 0.004862963726924852
    valeur_normalisee: 0.1932912025132977
    valeur_ponderee: 0.1932912025132977
    ts: '2026-06-30T06:04:12.876566+00:00'
  momentum_prix_20j_usdjpy:
    valeur: 0.011218477187039166
    valeur_normalisee: 0.3228688121715376
    valeur_ponderee: 0.3228688121715376
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_jpy_nets:
    valeur: -154291.0
    valeur_normalisee: -0.6891872690995869
    valeur_ponderee: -0.6891872690995869
    ts: '2026-06-30T06:04:12.876566+00:00'
  diff_taux_10y_us_jp:
    valeur: 1.73
    valeur_normalisee: -0.7408094409078075
    valeur_ponderee: -0.7408094409078075
    ts: '2026-06-30T06:04:12.876566+00:00'
  boj_intervention_risk:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 1.0
    materiality: high
    reliability: confirmed
    source_track: ia
    ts: '2026-06-30T06:04:12.876566+00:00'
    nature: structurel
    event_id: 42832b34c2ea
    event_date: '2026-06-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: -1.6666666666666665
      7j: -1.6666666666666665
      1m: -1.6666666666666665
  gate_regime_extreme:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
vix:
  niveau_vix_absolu:
    valeur: 14.95
    ts: '2026-06-30T06:04:12.876566+00:00'
  term_structure_vix_vix3m:
    valeur: 0.8223322332233223
    ts: '2026-06-30T06:04:12.876566+00:00'
  skew_index_cboe:
    valeur: 148.7
    ts: '2026-06-30T06:04:12.876566+00:00'
  vvix:
    valeur: 92.67
    ts: '2026-06-30T06:04:12.876566+00:00'
  gap_rv_iv:
    valeur: 2.47771372234466
    ts: '2026-06-30T06:04:12.876566+00:00'
  cftc_cot_vix_nets:
    valeur: -66774.0
    valeur_normalisee: -0.2774757397104772
    valeur_ponderee: -0.2774757397104772
    ts: '2026-06-30T06:04:12.876566+00:00'
  tension_geopolitique_active:
    valeur: 1
    valeur_normalisee: 1.0
    valeur_ponderee: 0.42
    materiality: medium
    reliability: reported
    source_track: ia_synthese
    ts: '2026-06-30T06:04:12.876566+00:00'
    synthese_rationale: Dominance de news LONG à matérialité élevée et fraîches (28-30
      juin) sur tensions US-Iran, escalade au Moyen-Orient et perturbations du détroit
      d'Ormuz, malgré une baisse du VIX de -6.83% sur 20j. La fraîcheur et la matérialité
      des news LONG récentes (notamment les frappes et attaques de cargos) sur
    nature: structurel
    event_id: ff98f6fe0c25
    event_date: '2026-06-30T00:00:00+00:00'
    event_date_source: rss
    freshness_days: '0.25'
    p2_shadow_contrib_exclu:
      24h: 79.30000000000003
      7j: 79.30000000000003
      1m: 79.30000000000003
    nature_shadow_downgrade: true
    nature_proposee: verbal
    rumor_reason: reliability:reported
  gate_evenement_macro_imminent:
    valeur: true
    ts: '2026-06-30T06:04:12.876566+00:00'
```
