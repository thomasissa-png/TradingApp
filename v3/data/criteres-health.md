# Santé des critères

_Cycle : 2026-07-23 05:22 UTC_

**Synthèse** : 42 motifs de skip distincts, 71 occurrence(s). Chaque ligne = un critère n/a et sa cause exacte (code HTTP / vide / unmapped / exception).

| Occurrences | Motif | Détail (cause exacte) |
|---:|---|---|
| 6 | fresh_price_refreshed | `GC=F` |
| 5 | fresh_price_refreshed | `CC=F` |
| 5 | fresh_price_refreshed | `KC=F` |
| 4 | fresh_price_refreshed | `BZ=F` |
| 4 | fresh_price_refreshed | `HG=F` |
| 3 | c2_std_zero | `unknown` |
| 3 | caixin_pmi_no_value | `` |
| 3 | fresh_price_refreshed | `EUR=X` |
| 3 | fresh_price_refreshed | `SI=F` |
| 3 | fresh_price_refreshed | `ZW=F` |
| 1 | CBOE non câblé (Put/Call sans CSV public) | `put_call_ratio_cboe_5j` |
| 1 | CBOE non câblé (Put/Call sans CSV public) | `vix_risk_usdjpy` |
| 1 | composite_no_subsource | `demande_pv_mining_strikes` |
| 1 | composite_partial | `hf_positioning_flux_options` |
| 1 | hors_fenetre | `usda_wasde_stocks_to_use` |
| 1 | Source linéaire non programmatique | `breadth_cac_ma50` |
| 1 | Source linéaire non programmatique | `brent_term_structure_m1m2` |
| 1 | Source linéaire non programmatique | `fedwatch_proba` |
| 1 | Source linéaire non programmatique | `term_structure_m1_m3` |
| 1 | Open-Meteo injoignable (récents) | `-21.2,-48.1:net_error` |
| 1 | Open-Meteo injoignable (récents) | `6.8,-5.3:net_error` |
| 1 | no_breadth_data | `breadth_cac_ma50` |
| 1 | Twelve : série vide | `USDGHS=X` |
| 1 | Twelve : série vide | `USDXOF=X` |
| 1 | Twelve : série vide | `^STOXX50EVOL` |
| 1 | Twelve : série vide | `^VXN` |
| 1 | Pas de M2 distinct (term structure) | `brent_term_structure_m1m2` |
| 1 | Source z-score non programmatique | `aaii_bull_bear` |
| 1 | Source z-score non programmatique | `achats_pboc_cb_emergentes` |
| 1 | Source z-score non programmatique | `arrivees_port_abidjan_sanpedro_20j` |
| 1 | Source z-score non programmatique | `demande_chinoise_imports` |
| 1 | Source z-score non programmatique | `egypte_gasc_tenders` |
| 1 | Source z-score non programmatique | `grindings_q` |
| 1 | Source z-score non programmatique | `inventaires_comex_silver` |
| 1 | Source z-score non programmatique | `inventaires_lme_shfe_5j` |
| 1 | Source z-score non programmatique | `nass_crop_progress` |
| 1 | Source z-score non programmatique | `nass_crop_progress_cotton` |
| 1 | Source z-score non programmatique | `spread_arabica_robusta` |
| 1 | Source z-score non programmatique | `spread_ny_london` |
| 1 | Source z-score non programmatique | `spread_oat_bund_stress_ez` |
| 1 | Source z-score non programmatique | `stocks_ice_arabica_certifies_20j` |
| 1 | Source z-score non programmatique | `usd_cfa_usd_cedi` |

## Valeurs reportées (fallback dernière valeur valide)

_La source réseau a échoué ce cycle ; pour éviter un n/a qui ferait chuter la couverture, on a rejoué la dernière bonne valeur (fraîche). Échec VISIBLE : drapeau ⚠️ reportée._

| Critère | Âge (j ouvrés) | Cause de l'échec source |
|---|---:|---|
| ⚠️ `meteo_bresil_canne_sucre` | 1 | source réseau indisponible |
| ⚠️ `meteo_ci_ghana_precip_30j` | 1 | source réseau indisponible |

## Provenance des prix (source réellement utilisée ce cycle)

| N | source | symboles |
|---:|---|---|
| 29 | twelve_native | BZ=F, CANE, CC=F, CL=F, COTN, EUR=X, EURUSD=X, EWQ, GC=F, GLD, HG=F, HYG, KC=F, QQQ, QQQE, RSP, SI=F, SLV, SOXX, SPY, USD/JPY, USDBRL=X, USDJPY=X, ZW=F, ^FCHI, ^GSPC, ^IXIC, ^RUT, ^VIX |
