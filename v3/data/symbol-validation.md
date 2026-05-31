# Symbol validation — Twelve Data

_Généré le 2026-05-31T21:19:42.958364+00:00 par `validate_symbols.py`._

Pour chaque actif, plusieurs candidats sont testés via `/quote`.
Le **winner** est le 1er candidat qui répond avec une valeur numérique > 0.
→ Ce winner doit être utilisé dans `TWELVE_SYMBOLS` (criteres_calculator) et
  dans `YAHOO_TO_TWELVE` (journaliste — pour stamp_prix_emission).

## Résumé

- Actifs testés : **39**
- Avec winner : **14**
- Sans winner (TOUS les candidats KO) : **25**

### Actifs sans winner
- **VIX 3M** (Volatilité) — testés : `VIX3M`, `^VIX3M`, `VXV`
- **VXN (Nasdaq)** (Volatilité) — testés : `VXN`, `^VXN`
- **V2X (Euro)** (Volatilité) — testés : `V2X`, `^V2TX`, `VSTOXX`
- **SKEW** (Volatilité) — testés : `SKEW`, `^SKEW`
- **VVIX** (Volatilité) — testés : `VVIX`, `^VVIX`
- **Germany 10Y yield** (Taux) — testés : `DE10Y`, `DEU10Y`, `BUND`
- **France 10Y yield** (Taux) — testés : `FR10Y`, `FRA10Y`, `OAT`
- **Brent** (Énergie) — testés : `BZ=F`, `UKOIL`, `BNO`
- **WTI** (Énergie) — testés : `CL=F`, `WTI`, `USO`
- **Cacao (NY ICE)** (Softs) — testés : `CC=F`, `COCOA`, `NIB`
- **Café Arabica** (Softs) — testés : `KC=F`, `COFFEE`, `JO`
- **Café Robusta** (Softs) — testés : `RC=F`, `ROBUSTA`
- **Blé CBOT** (Softs) — testés : `ZW=F`, `WHEAT`, `WEAT`
- **Cacao Londres** (Softs) — testés : `C=F`, `LCC`
- **EUR/USD** (Forex) — testés : `EUR/USD`, `EURUSD`, `EUR=X`
- **USD/JPY** (Forex) — testés : `USD/JPY`, `USDJPY`, `JPY=X`
- **USD/BRL** (Forex) — testés : `USD/BRL`, `USDBRL`
- **USD/XOF (CFA)** (Forex) — testés : `USD/XOF`, `USDXOF`
- **USD/GHS (Ghana)** (Forex) — testés : `USD/GHS`, `USDGHS`
- **SPY** (ETF) — testés : `SPY`
- **QQQ** (ETF) — testés : `QQQ`
- **GLD** (ETF) — testés : `GLD`
- **SLV** (ETF) — testés : `SLV`
- **HYG (HY proxy)** (ETF) — testés : `HYG`
- **TIP (real yield proxy)** (ETF) — testés : `TIP`

## Indices

| Actif | Winner | Détail des tests |
|---|---|---|
| S&P 500 | `SPX` | `SPX` OK (0.090000004) ; `GSPC` KO (HTTP KO (timeout/connexion)) ; `^GSPC` KO (HTTP KO (timeout/connexion)) ; `SPY` OK (756.47998) |
| Nasdaq Composite | `QQQ` | `IXIC` KO (HTTP KO (timeout/connexion)) ; `^IXIC` KO (HTTP KO (timeout/connexion)) ; `QQQ` OK (738.31) |
| Nasdaq 100 | `NDX` | `NDX` OK (20.6) ; `^NDX` KO (HTTP KO (timeout/connexion)) ; `QQQ` OK (738.31) |
| CAC 40 | `CAC` | `CAC` OK (50.029999) ; `FCHI` OK (8183.33984) ; `^FCHI` KO (HTTP KO (timeout/connexion)) ; `EWQ` OK (45.97) |
| Russell 2000 | `IWM` | `RUT` KO (HTTP KO (timeout/connexion)) ; `^RUT` KO (HTTP KO (timeout/connexion)) ; `IWM` OK (290.42999) |
| Euro Stoxx 50 | `FEZ` | `SX5E` KO (HTTP KO (timeout/connexion)) ; `STOXX50E` KO (HTTP KO (timeout/connexion)) ; `^STOXX50E` KO (HTTP KO (timeout/connexion)) ; `FEZ` OK (67.91) |
| Philly Semicond (SOX) | `SOXX` | `SOX` KO (HTTP KO (timeout/connexion)) ; `^SOX` KO (HTTP KO (timeout/connexion)) ; `SOXX` OK (569.080017) |

## Volatilité

| Actif | Winner | Détail des tests |
|---|---|---|
| VIX | `VIXY` | `VIX` KO (HTTP KO (timeout/connexion)) ; `^VIX` KO (HTTP KO (timeout/connexion)) ; `VIXY` OK (23.29) |
| VIX 3M | _(aucun)_ | `VIX3M` KO (HTTP KO (timeout/connexion)) ; `^VIX3M` KO (HTTP KO (timeout/connexion)) ; `VXV` KO (HTTP KO (timeout/connexion)) |
| VXN (Nasdaq) | _(aucun)_ | `VXN` KO (HTTP KO (timeout/connexion)) ; `^VXN` KO (HTTP KO (timeout/connexion)) |
| V2X (Euro) | _(aucun)_ | `V2X` KO (HTTP KO (timeout/connexion)) ; `^V2TX` KO (HTTP KO (timeout/connexion)) ; `VSTOXX` KO (HTTP KO (timeout/connexion)) |
| SKEW | _(aucun)_ | `SKEW` KO (HTTP KO (timeout/connexion)) ; `^SKEW` KO (HTTP KO (timeout/connexion)) |
| VVIX | _(aucun)_ | `VVIX` KO (HTTP KO (timeout/connexion)) ; `^VVIX` KO (HTTP KO (timeout/connexion)) |

## Dollar

| Actif | Winner | Détail des tests |
|---|---|---|
| DXY | `USDX` | `DXY` KO (HTTP KO (timeout/connexion)) ; `^DXY` KO (HTTP KO (timeout/connexion)) ; `DX-Y.NYB` KO (HTTP KO (timeout/connexion)) ; `USDX` OK (25.806) ; `UUP` OK (27.66) |

## Taux

| Actif | Winner | Détail des tests |
|---|---|---|
| US 10Y yield | `TNX` | `TNX` OK (0.185) ; `^TNX` KO (HTTP KO (timeout/connexion)) ; `US10Y` KO (HTTP KO (timeout/connexion)) ; `TIP` OK (111.21) |
| US 2Y yield | `US2Y` | `UST2Y` KO (HTTP KO (timeout/connexion)) ; `^IRX` KO (HTTP KO (timeout/connexion)) ; `US2Y` OK (4.014) |
| Germany 10Y yield | _(aucun)_ | `DE10Y` KO (HTTP KO (timeout/connexion)) ; `DEU10Y` KO (HTTP KO (timeout/connexion)) ; `BUND` KO (HTTP KO (timeout/connexion)) |
| France 10Y yield | _(aucun)_ | `FR10Y` KO (HTTP KO (timeout/connexion)) ; `FRA10Y` KO (HTTP KO (timeout/connexion)) ; `OAT` KO (HTTP KO (timeout/connexion)) |

## Métaux

| Actif | Winner | Détail des tests |
|---|---|---|
| Or spot | `XAU/USD` | `XAU/USD` OK (4542.56067) ; `GC=F` KO (HTTP KO (timeout/connexion)) ; `GLD` OK (417.12) |
| Argent spot | `XAG/USD` | `XAG/USD` OK (75.37169) ; `SI=F` KO (HTTP KO (timeout/connexion)) ; `SLV` OK (68.33) |
| Cuivre (HG) | `CPER` | `HG=F` KO (HTTP KO (timeout/connexion)) ; `COPPER` KO (HTTP KO (timeout/connexion)) ; `CPER` OK (38.86) |

## Énergie

| Actif | Winner | Détail des tests |
|---|---|---|
| Brent | _(aucun)_ | `BZ=F` KO (HTTP KO (timeout/connexion)) ; `UKOIL` KO (HTTP KO (timeout/connexion)) ; `BNO` KO (HTTP KO (timeout/connexion)) |
| WTI | _(aucun)_ | `CL=F` KO (HTTP KO (timeout/connexion)) ; `WTI` KO (HTTP KO (timeout/connexion)) ; `USO` KO (HTTP KO (timeout/connexion)) |

## Softs

| Actif | Winner | Détail des tests |
|---|---|---|
| Cacao (NY ICE) | _(aucun)_ | `CC=F` KO (HTTP KO (timeout/connexion)) ; `COCOA` KO (HTTP KO (timeout/connexion)) ; `NIB` KO (HTTP KO (timeout/connexion)) |
| Café Arabica | _(aucun)_ | `KC=F` KO (HTTP KO (timeout/connexion)) ; `COFFEE` KO (HTTP KO (timeout/connexion)) ; `JO` KO (HTTP KO (timeout/connexion)) |
| Café Robusta | _(aucun)_ | `RC=F` KO (HTTP KO (timeout/connexion)) ; `ROBUSTA` KO (HTTP KO (timeout/connexion)) |
| Blé CBOT | _(aucun)_ | `ZW=F` KO (HTTP KO (timeout/connexion)) ; `WHEAT` KO (HTTP KO (timeout/connexion)) ; `WEAT` KO (HTTP KO (timeout/connexion)) |
| Cacao Londres | _(aucun)_ | `C=F` KO (HTTP KO (timeout/connexion)) ; `LCC` KO (HTTP KO (timeout/connexion)) |

## Forex

| Actif | Winner | Détail des tests |
|---|---|---|
| EUR/USD | _(aucun)_ | `EUR/USD` KO (HTTP KO (timeout/connexion)) ; `EURUSD` KO (HTTP KO (timeout/connexion)) ; `EUR=X` KO (HTTP KO (timeout/connexion)) |
| USD/JPY | _(aucun)_ | `USD/JPY` KO (HTTP KO (timeout/connexion)) ; `USDJPY` KO (HTTP KO (timeout/connexion)) ; `JPY=X` KO (HTTP KO (timeout/connexion)) |
| USD/BRL | _(aucun)_ | `USD/BRL` KO (HTTP KO (timeout/connexion)) ; `USDBRL` KO (HTTP KO (timeout/connexion)) |
| USD/XOF (CFA) | _(aucun)_ | `USD/XOF` KO (HTTP KO (timeout/connexion)) ; `USDXOF` KO (HTTP KO (timeout/connexion)) |
| USD/GHS (Ghana) | _(aucun)_ | `USD/GHS` KO (HTTP KO (timeout/connexion)) ; `USDGHS` KO (HTTP KO (timeout/connexion)) |

## ETF

| Actif | Winner | Détail des tests |
|---|---|---|
| SPY | _(aucun)_ | `SPY` KO (HTTP KO (timeout/connexion)) |
| QQQ | _(aucun)_ | `QQQ` KO (HTTP KO (timeout/connexion)) |
| GLD | _(aucun)_ | `GLD` KO (HTTP KO (timeout/connexion)) |
| SLV | _(aucun)_ | `SLV` KO (HTTP KO (timeout/connexion)) |
| HYG (HY proxy) | _(aucun)_ | `HYG` KO (HTTP KO (timeout/connexion)) |
| TIP (real yield proxy) | _(aucun)_ | `TIP` KO (HTTP KO (timeout/connexion)) |

