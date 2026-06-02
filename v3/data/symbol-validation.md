# Symbol validation — Twelve Data

_Généré le 2026-06-02T07:52:29.485204+00:00 par `validate_symbols.py`._

Pour chaque actif, plusieurs candidats sont testés via `/quote`.
Le **winner** est le 1er candidat qui répond avec une valeur numérique > 0.
→ Ce winner doit être utilisé dans `TWELVE_SYMBOLS` (criteres_calculator) et
  dans `YAHOO_TO_TWELVE` (journaliste — pour stamp_prix_emission).

## Résumé

- Actifs testés : **39**
- Avec winner : **26**
- Sans winner (TOUS les candidats KO) : **13**

### Actifs sans winner
- **VIX 3M** (Volatilité) — testés : `VIX3M`, `^VIX3M`, `VXV`
- **VXN (Nasdaq)** (Volatilité) — testés : `VXN`, `^VXN`
- **V2X (Euro)** (Volatilité) — testés : `V2X`, `^V2TX`, `VSTOXX`
- **SKEW** (Volatilité) — testés : `SKEW`, `^SKEW`
- **VVIX** (Volatilité) — testés : `VVIX`, `^VVIX`
- **Germany 10Y yield** (Taux) — testés : `DE10Y`, `DEU10Y`, `BUND`
- **France 10Y yield** (Taux) — testés : `FR10Y`, `FRA10Y`, `OAT`
- **Café Arabica** (Softs) — testés : `KC=F`, `COFFEE`, `JO`
- **Café Robusta** (Softs) — testés : `RC=F`, `ROBUSTA`
- **Cacao Londres** (Softs) — testés : `C=F`, `LCC`
- **SLV** (ETF) — testés : `SLV`
- **HYG (HY proxy)** (ETF) — testés : `HYG`
- **TIP (real yield proxy)** (ETF) — testés : `TIP`

## Indices

| Actif | Winner | Détail des tests |
|---|---|---|
| S&P 500 | `SPX` | `SPX` OK (0.085000001) ; `GSPC` KO (HTTP KO (timeout/connexion)) ; `^GSPC` KO (HTTP KO (timeout/connexion)) ; `SPY` OK (758.53998) |
| Nasdaq Composite | `QQQ` | `IXIC` KO (HTTP KO (timeout/connexion)) ; `^IXIC` KO (HTTP KO (timeout/connexion)) ; `QQQ` OK (742.73999) |
| Nasdaq 100 | `NDX` | `NDX` OK (21.2) ; `^NDX` KO (HTTP KO (timeout/connexion)) ; `QQQ` OK (742.73999) |
| CAC 40 | `CAC` | `CAC` OK (48.98) ; `FCHI` OK (8223.66992) ; `^FCHI` KO (HTTP KO (timeout/connexion)) ; `EWQ` OK (45.82) |
| Russell 2000 | `IWM` | `RUT` KO (HTTP KO (timeout/connexion)) ; `^RUT` KO (HTTP KO (timeout/connexion)) ; `IWM` OK (288.98001) |
| Euro Stoxx 50 | `FEZ` | `SX5E` KO (HTTP KO (timeout/connexion)) ; `STOXX50E` KO (HTTP KO (timeout/connexion)) ; `^STOXX50E` KO (HTTP KO (timeout/connexion)) ; `FEZ` OK (67.93) |
| Philly Semicond (SOX) | `SOXX` | `SOX` KO (HTTP KO (timeout/connexion)) ; `^SOX` KO (HTTP KO (timeout/connexion)) ; `SOXX` OK (571.92999) |

## Volatilité

| Actif | Winner | Détail des tests |
|---|---|---|
| VIX | `VIXY` | `VIX` KO (HTTP KO (timeout/connexion)) ; `^VIX` KO (HTTP KO (timeout/connexion)) ; `VIXY` OK (23.85) |
| VIX 3M | _(aucun)_ | `VIX3M` KO (HTTP KO (timeout/connexion)) ; `^VIX3M` KO (HTTP KO (timeout/connexion)) ; `VXV` KO (HTTP KO (timeout/connexion)) |
| VXN (Nasdaq) | _(aucun)_ | `VXN` KO (HTTP KO (timeout/connexion)) ; `^VXN` KO (HTTP KO (timeout/connexion)) |
| V2X (Euro) | _(aucun)_ | `V2X` KO (HTTP KO (timeout/connexion)) ; `^V2TX` KO (HTTP KO (timeout/connexion)) ; `VSTOXX` KO (HTTP KO (timeout/connexion)) |
| SKEW | _(aucun)_ | `SKEW` KO (HTTP KO (timeout/connexion)) ; `^SKEW` KO (HTTP KO (timeout/connexion)) |
| VVIX | _(aucun)_ | `VVIX` KO (HTTP KO (timeout/connexion)) ; `^VVIX` KO (HTTP KO (timeout/connexion)) |

## Dollar

| Actif | Winner | Détail des tests |
|---|---|---|
| DXY | `USDX` | `DXY` KO (HTTP KO (timeout/connexion)) ; `^DXY` KO (HTTP KO (timeout/connexion)) ; `DX-Y.NYB` KO (HTTP KO (timeout/connexion)) ; `USDX` OK (25.7) ; `UUP` OK (27.76) |

## Taux

| Actif | Winner | Détail des tests |
|---|---|---|
| US 10Y yield | `TNX` | `TNX` OK (0.185) ; `^TNX` KO (HTTP KO (timeout/connexion)) ; `US10Y` KO (HTTP KO (timeout/connexion)) ; `TIP` OK (109.98) |
| US 2Y yield | `US2Y` | `UST2Y` KO (HTTP KO (timeout/connexion)) ; `^IRX` KO (HTTP KO (timeout/connexion)) ; `US2Y` OK (4.0637) |
| Germany 10Y yield | _(aucun)_ | `DE10Y` KO (HTTP KO (timeout/connexion)) ; `DEU10Y` KO (HTTP KO (timeout/connexion)) ; `BUND` KO (HTTP KO (timeout/connexion)) |
| France 10Y yield | _(aucun)_ | `FR10Y` KO (HTTP KO (timeout/connexion)) ; `FRA10Y` KO (HTTP KO (timeout/connexion)) ; `OAT` KO (HTTP KO (timeout/connexion)) |

## Métaux

| Actif | Winner | Détail des tests |
|---|---|---|
| Or spot | `XAU/USD` | `XAU/USD` OK (4531.64264) ; `GC=F` KO (HTTP KO (timeout/connexion)) ; `GLD` OK (411.26001) |
| Argent spot | `XAG/USD` | `XAG/USD` OK (76.73143) ; `SI=F` KO (HTTP KO (timeout/connexion)) ; `SLV` OK (67.67) |
| Cuivre (HG) | `CPER` | `HG=F` KO (HTTP KO (timeout/connexion)) ; `COPPER` KO (HTTP KO (timeout/connexion)) ; `CPER` OK (39.96) |

## Énergie

| Actif | Winner | Détail des tests |
|---|---|---|
| Brent | `BNO` | `BZ=F` KO (HTTP KO (timeout/connexion)) ; `UKOIL` KO (HTTP KO (timeout/connexion)) ; `BNO` OK (52.49) |
| WTI | `WTI` | `CL=F` KO (HTTP KO (timeout/connexion)) ; `WTI` OK (3.99) ; `USO` OK (135.5) |

## Softs

| Actif | Winner | Détail des tests |
|---|---|---|
| Cacao (NY ICE) | `NIB` | `CC=F` KO (HTTP KO (timeout/connexion)) ; `COCOA` KO (HTTP KO (timeout/connexion)) ; `NIB` OK (14.884) |
| Café Arabica | _(aucun)_ | `KC=F` KO (HTTP KO (timeout/connexion)) ; `COFFEE` KO (HTTP KO (timeout/connexion)) ; `JO` KO (HTTP KO (timeout/connexion)) |
| Café Robusta | _(aucun)_ | `RC=F` KO (HTTP KO (timeout/connexion)) ; `ROBUSTA` KO (HTTP KO (timeout/connexion)) |
| Blé CBOT | `WEAT` | `ZW=F` KO (HTTP KO (timeout/connexion)) ; `WHEAT` KO (HTTP KO (timeout/connexion)) ; `WEAT` OK (23.31) |
| Cacao Londres | _(aucun)_ | `C=F` KO (HTTP KO (timeout/connexion)) ; `LCC` KO (HTTP KO (timeout/connexion)) |

## Forex

| Actif | Winner | Détail des tests |
|---|---|---|
| EUR/USD | `EUR/USD` | `EUR/USD` OK (1.16495) ; `EURUSD` KO (HTTP KO (timeout/connexion)) ; `EUR=X` KO (HTTP KO (timeout/connexion)) |
| USD/JPY | `USD/JPY` | `USD/JPY` OK (159.72088) ; `USDJPY` KO (HTTP KO (timeout/connexion)) ; `JPY=X` KO (HTTP KO (timeout/connexion)) |
| USD/BRL | `USD/BRL` | `USD/BRL` OK (5.02645) ; `USDBRL` KO (HTTP KO (timeout/connexion)) |
| USD/XOF (CFA) | `USD/XOF` | `USD/XOF` OK (563.11574) ; `USDXOF` KO (HTTP KO (timeout/connexion)) |
| USD/GHS (Ghana) | `USD/GHS` | `USD/GHS` OK (11.76695) ; `USDGHS` KO (HTTP KO (timeout/connexion)) |

## ETF

| Actif | Winner | Détail des tests |
|---|---|---|
| SPY | `SPY` | `SPY` OK (758.53998) |
| QQQ | `QQQ` | `QQQ` OK (742.73999) |
| GLD | `GLD` | `GLD` OK (411.26001) |
| SLV | _(aucun)_ | `SLV` KO (HTTP KO (timeout/connexion)) |
| HYG (HY proxy) | _(aucun)_ | `HYG` KO (HTTP KO (timeout/connexion)) |
| TIP (real yield proxy) | _(aucun)_ | `TIP` KO (HTTP KO (timeout/connexion)) |

