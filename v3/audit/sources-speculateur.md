# Audit sources — œil spéculateur trend-follower (24h/7j/1m)

Câblé réellement (data chiffrées) : **Twelve Data, CFTC COT, EIA, Open-Meteo**. Tout le reste = RSS/GNews/NewsAPI (news, pas data). Les fiches sont excellentes sur le papier (TIPS, COT, term structure, breadth, spreads de crédit, flux ETF) mais **la moitié des critères pointent vers des sources NON câblées** (FRED, WGC flux, LME/SHFE, ICE/COMEX, CBOE, AAII, Caixin, USDA). On lit des news là où la fiche réclame une donnée. C'est l'écart n°1.

## Par actif : driver de tendance moyen-terme | capté ? | manque | type

| Actif | Vrai driver moyen-terme | Capté ? | Manque clé | Type |
|---|---|---|---|---|
| **Or** | Taux réels (TIPS) + DXY + achats CB + flux ETF | Partiel | FRED DFII10, flux ETF or (GLD/WGC), achats WGC | DATA |
| **Argent** | Or + ratio G/S + PMI Chine + stocks COMEX + flux SLV | Partiel | Inventaires COMEX, flux SLV/PSLV, Caixin PMI | DATA |
| **Cuivre** | PMI Chine + stocks LME/SHFE + mines + term struct | Faible | **Stocks LME+SHFE**, Caixin PMI, term M1-M3 | DATA |
| **Pétrole** | Stocks EIA/API + OPEC + term struct + géopol | Bon | API stocks (mardi), Cushing via EIA, Caixin | DATA partiel |
| **Blé** | WASDE stocks/use + drought + mer Noire | Partiel | **USDA WASDE/NASS/FAS**, NOAA drought (Open-Meteo ≠ drought monitor) | DATA |
| **Café** | Météo Brésil (gel) + stocks ICE + USD/BRL | Partiel | **Stocks ICE certifiés**, check T min gel ciblé | DATA |
| **Cacao** | Météo CI/Ghana + arrivées ports + grindings | Faible | **Arrivées ports Abidjan**, grindings ECA/NCA, OI options ICE | DATA |
| **Nasdaq** | Taux réels + SOX + breadth + flux QQQ + VXN | Partiel | FRED TIPS, **breadth NDX %>MA50**, VXN, flux QQQ | DATA |
| **S&P 500** | Taux 10Y + **HY credit spread** + breadth + VIX | Partiel | FRED HY OAS, breadth SPX, AAII, flux SPY | DATA |
| **CAC 40** | **Spread OAT-Bund** + alpha vs SPX + politique FR | Partiel | OAT-Bund (calculable TD ?), breadth CAC, flux MSCI France | DATA |
| **EUR/USD** | Différentiel taux 2Y/10Y US-DE + DXY + FedWatch | Partiel | FRED 2Y DE/US, **CME FedWatch**, OAT-Bund | DATA |
| **VIX** | Niveau + **term structure VIX/VIX3M** + P/C + VVIX | Faible | CBOE (P/C, SKEW, VVIX), VIX3M, gap RV-IV | DATA |

## Données chiffrées qui battent les news (manquantes, par priorité de levier)

1. **Courbe des taux réels US (FRED)** — pilier de Or, Nasdaq, S&P, EUR/USD, Argent. Une seule série (DFII10, DGS2, DGS10, T10YIE, OAS HY, OAT-Bund) alimente 6 actifs. **Plus haut ROI du système.**
2. **Term structure / spreads commodités** — backwardation Brent M1-M2, cuivre M1-M3, VIX/VIX3M. C'est LE signal de tension d'offre qui précède le prix. Calculable depuis Twelve Data (contrats) — déjà à portée.
3. **Stocks physiques** — LME+SHFE (cuivre), COMEX (argent), ICE arabica (café), arrivées ports CI (cacao). Aujourd'hui couverts par des news Google ⇒ bruit + retard.
4. **Flux ETF nets 5j** — GLD/SLV/QQQ/SPY/MSCI France. Le flux passif = le moteur de tendance 7j/1m des indices et métaux. Non câblé du tout.
5. **CME FedWatch + breadth (%>MA50)** — FedWatch = anticipation taux (EUR/USD, indices) ; breadth = santé interne d'une tendance indicielle (anti-fausse-cassure).

## Régime de marché : LE chaînon manquant

Aucun **indicateur de régime global** transversal. Chaque actif a un GATE binaire (évite de trader avant FOMC) mais rien ne dit *« on est en risk-on tendanciel »* vs *« range/risk-off »*. Un trend-follower sans filtre de régime suit les fausses cassures.
**À ajouter (tout calculable Twelve Data + FRED, zéro nouvelle source) :** un score de régime composite =
- VIX niveau + pente VIX/VIX3M (vol calme/montante)
- DXY trend 20j (dollar = robinet du risque)
- HY credit spread direction (stress crédit = fin de tendance actions)
- breadth agrégée indices.
Sortie : `RISK_ON_TREND / NEUTRAL / RISK_OFF`. Sert de multiplicateur de conviction (pas de gate), pondère LONG actions/commodités en risk-on, favorise Or/VIX en risk-off.

## Recul : de « lecteur de news » à « lecteur de tendance »

- **Trop de news, pas assez de data.** RSS/GNews dominent le pipeline alors que les fiches sont conçues pour des séries chiffrées. La news sert à expliquer *a posteriori*, rarement à anticiper une tendance moyen-terme — sauf géopol/OPEC/banques centrales (à garder).
- **Brancher FRED en priorité absolue** (gratuit, API propre) : débloque taux réels, différentiels, HY OAS, OAT-Bund → 6 actifs d'un coup. Plus gros gain de justesse par unité d'effort.
- **Exploiter Twelve Data à fond** (déjà câblé) : term structures, spreads, ratios, breadth, flux proxy sont calculables sans nouvelle source. On sous-utilise l'API qu'on paie déjà.
- **Ajouter un filtre de régime** : transforme 12 signaux isolés en système qui sait *quand* suivre la tendance et *quand* se méfier d'une cassure — c'est ce qui sépare un agrégateur de news d'un trend-follower crédible.
