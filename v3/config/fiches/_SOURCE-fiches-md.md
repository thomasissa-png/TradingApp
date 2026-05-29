# Source — 11 fiches actifs (markdown vault) à convertir en YAML

> Extrait fidèle du vault `Bourse/Actifs/` (v2, 27/05). À convertir en `v3/config/fiches/<slug>.yml`
> selon `v3/config/SCHEMA-fiche.md` + le template `petrole.yml`. Pétrole déjà fait.
> Conventions : `cle_courante` = slug du nom de critère (snake_case). `signe` = -1 si « signe inversé ».
> normalisation : zscore (window/div/cap) | lineaire (centre/echelle/cap) | triplet | gate (drapeau, hors score).
> Échelles linéaires non chiffrées dans la source → dériver des seuils énoncés + commentaire « à calibrer ».

---

## CAC 40  (slug: cac40)
frontmatter: nom="CAC 40", ticker_principal="^FCHI", famille="indices", news_zone="EU-FR", version=2
seuils_reussite_pct: 24h=0.5, 7j=1.2, 1m=3.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | V2X régime | V2X=16 (calme sain) | V2X>30 OU <11 | Mapping NON-MONOTONE : pic à V2X=16, chute aux extrêmes | 8 | 0,8 | 0,5 | 0,2 |
| 2 | Spread OAT-Bund 10Y (bp) | resserre vs 60j (z<−1) | élargit (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 10 | 0,4 | 0,9 | 1,0 |
| 3 | Alpha CAC vs S&P 5j | CAC out-perf >+1% | under-perf >−1% | zscore 60j /2 cap1 | 6 | 0,3 | 0,8 | 0,6 |
| 4 | Breadth CAC (%>MA50) | >65% | <30% | lineaire (breadth−50)/35 cap1 | 6 | 0,9 | 0,7 | 0,4 |
| 5 | Flux ETF MSCI France 5j net | entrées >+1σ | sorties <−1σ | zscore 60j /2 cap1 | 5 | 0,3 | 1,0 | 0,7 |
| 6 | Tension politique FR | « accord budget/stabilité » → +1 | « motion/dissolution/dégradation rating/shutdown » → −1 | triplet | 3 | 0,5 | 0,8 | 0,5 |
| 7 | RSI 14j ^FCHI | RSI=30 oversold | RSI>75 | lineaire INVERSÉ centré 50 cap1 | 2 | 0,8 | 0,4 | 0,2 |
| 8 | GATE régime extrême | n/a | V2X>40 OU FOMC/BCE/CPI US/NFP <24h OU géopol Iran-Europe actif | gate (drapeau) | gate | 1,0 | 1,0 | 1,0 |

---

## S&P 500  (slug: sp500)
frontmatter: nom="S&P 500", ticker_principal="^GSPC", famille="indices", news_zone="US", version=2
seuils_reussite_pct: 24h=0.4, 7j=1.0, 1m=2.5

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | VIX régime | VIX=14-16 sain | VIX>28 OU <11 | mapping NON-MONOTONE | 8 | 0,9 | 0,6 | 0,3 |
| 2 | Taux 10Y US delta 5j | taux baisse (z<−1) | monte (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 9 | 0,4 | 0,9 | 1,0 |
| 3 | HY credit spread (ICE BofA HY OAS) | resserre (z<−1) | élargit (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 7 | 0,5 | 1,0 | 0,9 |
| 4 | Breadth S&P (%>MA50) | >65% | <30% | lineaire (breadth−50)/35 cap1 | 7 | 0,9 | 0,8 | 0,5 |
| 5 | DXY trend 20j | DXY baisse | monte | zscore 60j /2 cap1, signe INVERSÉ | 5 | 0,3 | 0,7 | 0,9 |
| 6 | Flux ETF SPY+IVV 5j net | entrées >+1σ | sorties <−1σ | zscore 60j /2 cap1 | 5 | 0,4 | 1,0 | 0,7 |
| 7 | AAII bull-bear | Bears>Bulls+1σ (contrarian) | Bulls>Bears+1σ | zscore 252 semaines /2 cap1, signe INVERSÉ | 4 | 0,2 | 0,7 | 0,5 |
| 8 | Shiller CAPE / Forward P/E | CAPE<25 OU FwdPE<16 | CAPE>35 OU FwdPE>22 | percentile 252j, signe INVERSÉ, max des deux | 4 | 0,1 | 0,3 | 1,0 |
| 9 | RSI 14j ^GSPC | RSI=30 | RSI>75 | lineaire INVERSÉ cap1 | 2 | 0,8 | 0,4 | 0,2 |
| 10 | GATE régime extrême | n/a | VIX>35 OU FOMC/CPI US/NFP <24h OU earnings méga-cap (NVDA/MSFT/AAPL/GOOGL/AMZN/META/TSLA) cette semaine | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Nasdaq  (slug: nasdaq)
frontmatter: nom="Nasdaq", ticker_principal="^IXIC", famille="indices", news_zone="US", version=2
seuils_reussite_pct: 24h=0.7, 7j=1.5, 1m=4.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Taux 10Y US réels (TIPS) | TIPS baisse (z<−1) | monte (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 11 | 0,5 | 1,0 | 1,0 |
| 2 | VXN régime | VXN=18-22 | VXN>35 OU <14 | mapping NON-MONOTONE | 7 | 0,9 | 0,6 | 0,3 |
| 3 | SOX trend 5j | SOX hausse (z>+1) | baisse (z<−1) | zscore 60j /2 cap1 | 7 | 0,9 | 0,9 | 0,5 |
| 4 | Breadth Nasdaq 100 (%>MA50) | >60% | <25% | lineaire cap1 | 6 | 0,9 | 0,7 | 0,4 |
| 5 | Concentration top 7 | baisse (rotation) | >52% top 7 (overheated) | zscore 60j /2 cap1, signe INVERSÉ | 5 | 0,1 | 0,4 | 0,9 |
| 6 | Sentiment IA / méga-caps | beat earnings + guidance haussière | miss OU correction guidance | triplet (events L1=Tech-IA 7j) | 5 | 0,8 | 0,9 | 0,5 |
| 7 | Flux ETF QQQ 5j net | entrées >+1σ | sorties <−1σ | zscore 60j cap1 | 5 | 0,4 | 1,0 | 0,7 |
| 8 | Spread Nasdaq-Russell 2000 | Russell out-perf (breadth saine) | Nasdaq out-perf très large | zscore 60j /2 cap1, signe INVERSÉ | 4 | 0,5 | 0,8 | 0,7 |
| 9 | RSI 14j ^IXIC | RSI=30 | RSI>75 | lineaire INVERSÉ cap1 | 2 | 0,8 | 0,4 | 0,2 |
| 10 | GATE régime extrême | n/a | VXN>40 OU FOMC/CPI <24h OU earnings méga-cap cette semaine | gate | gate | 1,0 | 1,0 | 1,0 |

---

## VIX  (slug: vix)  — conclusion LONG = VIX va MONTER
frontmatter: nom="VIX", ticker_principal="^VIX", famille="volatilité", news_zone="US", version=2
seuils_reussite_pct: 24h=5.0, 7j=10.0, 1m=15.0  (en % de variation du VIX). NOTE: cible réussite 52% (instrument bruyant)

| # | Critère | LONG VIX (+1) | SHORT VIX (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Niveau VIX absolu | VIX<13 (rebond attendu) | VIX>32 (baisse attendue) | lineaire INVERSÉ centré 20 cap1 | 10 | 0,9 | 0,8 | 0,5 |
| 2 | Term structure VIX/VIX3M | ratio>1,05 (backwardation) | ratio<0,85 (contango fort) | lineaire centré 0,95 cap1 | 8 | 0,8 | 1,0 | 0,6 |
| 3 | Put/Call ratio CBOE 5j moy | P/C>1,2 (panique=peak fear) | P/C<0,7 (complacency) | zscore 60j /2 cap1, signe INVERSÉ | 6 | 0,6 | 0,9 | 0,4 |
| 4 | SKEW Index CBOE | SKEW>150 | SKEW<120 | lineaire centré 135 cap1 | 5 | 0,4 | 0,8 | 0,3 |
| 5 | VVIX | VVIX>110 | VVIX<80 | lineaire centré 95 cap1 | 5 | 0,7 | 0,6 | 0,3 |
| 6 | Gap RV-IV (réalisée 20j vs implicite) | IV>>RV +5pts | RV>>IV +5pts | lineaire centré 0 cap1, signe INVERSÉ | 5 | 0,5 | 0,7 | 0,3 |
| 7 | CFTC COT VIX nets | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 5 | 0,2 | 0,7 | 0,9 |
| 8 | Tension géopolitique active | event L1=Géopolitique actif 3j | détente | triplet | 4 | 0,9 | 0,6 | 0,3 |
| 9 | GATE événement macro imminent | n/a | FOMC/CPI US/NFP/ECB rate decision <24-48h | gate | gate | 1,0 | 1,0 | 1,0 |

---

## EUR/USD  (slug: eurusd)  — LONG = EUR/USD monte (USD faiblit)
frontmatter: nom="EUR/USD", ticker_principal="EUR=X", famille="fx", news_zone="Global", version=2
seuils_reussite_pct: 24h=0.25, 7j=0.7, 1m=1.8

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Différentiel taux 2Y US-DE | se resserre (BCE+hawkish) | s'élargit (Fed+hawkish) | zscore 60j /2 cap1, signe INVERSÉ | 12 | 0,5 | 1,0 | 1,0 |
| 2 | Différentiel taux 10Y US-Bund | se resserre | s'élargit | zscore 60j /2 cap1, signe INVERSÉ | 6 | 0,3 | 0,7 | 1,0 |
| 3 | DXY trend 20j | DXY baisse (z<−1) | monte (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 9 | 0,7 | 1,0 | 0,8 |
| 4 | USD/JPY (proxy risk) | USD/JPY baisse | monte | zscore 60j /2 cap1, signe INVERSÉ | 4 | 0,7 | 0,8 | 0,5 |
| 5 | FedWatch proba | proba cut Fed >70% | proba hike >70% OU aucun cut | lineaire cap1 sur proba | 6 | 0,3 | 0,8 | 0,9 |
| 6 | CFTC COT EUR nets | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 5 | 0,2 | 0,6 | 0,9 |
| 7 | Spread OAT-Bund (stress EZ) | se resserre | s'élargit | zscore 60j /2 cap1, signe INVERSÉ | 4 | 0,4 | 0,7 | 0,6 |
| 8 | Balance commerciale EZ | surplus hausse (z>+1) | baisse/déficit (z<−1) | zscore 12 mois /2 cap1 | 3 | 0,1 | 0,3 | 0,9 |
| 9 | GATE régime extrême | n/a | FOMC/ECB rate decision <24h OU NFP US ce vendredi OU CPI US <24h | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Or  (slug: or)
frontmatter: nom="Or", ticker_principal="GC=F", famille="métaux-précieux", news_zone="Global", version=2
seuils_reussite_pct: 24h=0.5, 7j=1.3, 1m=3.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Taux 10Y US réels (TIPS) | TIPS baisse (z<−1) | monte (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 12 | 0,5 | 1,0 | 1,0 |
| 2 | Achats PBoC + CB émergentes (12m cumulés vs 24m précédents) | accumulation >+1σ | sortie/ralentissement | zscore 60 MOIS /2 cap1 | 9 | 0,1 | 0,3 | 1,0 |
| 3 | DXY trend 20j | DXY baisse (z<−1) | monte (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 8 | 0,6 | 0,9 | 0,8 |
| 4 | CFTC COT nets | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 6 | 0,2 | 0,7 | 1,0 |
| 5 | Flux ETF or agrégés 5j net | entrées >+1σ | sorties <−1σ | zscore 60j /2 cap1 | 5 | 0,4 | 1,0 | 0,7 |
| 6 | Tension géopolitique | escalade 7j (guerre/sanctions/terrorisme) | détente | triplet | 5 | 0,8 | 0,5 | 0,3 |
| 7 | Demande indienne saisonnière | Diwali (oct-nov) OU mariages (oct-déc) | off-season (jan-mai) | triplet (calendrier) | 3 | 0,1 | 0,3 | 0,9 |
| 8 | VIX (risk-off proxy) | VIX>22 | VIX<14 | lineaire centré 18 cap1 | 3 | 0,7 | 0,5 | 0,2 |
| 9 | GATE régime extrême | n/a | FOMC/CPI US <24h OU NFP vendredi OU WGC report <7j | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Argent  (slug: argent)
frontmatter: nom="Argent", ticker_principal="SI=F", famille="métaux-précieux", news_zone="Global", version=2
seuils_reussite_pct: 24h=0.8, 7j=2.0, 1m=5.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Taux 10Y US réels (TIPS) | TIPS baisse (z<−1) | monte (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 8 | 0,5 | 1,0 | 1,0 |
| 2 | Mouvement de l'or 5j | or >+2% 5j | or <−2% 5j | zscore 60j /2 cap1 | 7 | 0,8 | 0,9 | 0,7 |
| 3 | Ratio Gold/Silver | ratio>85 (argent sous-éval) | ratio<60 (cher) | lineaire INVERSÉ centré 75 cap1 | 7 | 0,3 | 0,7 | 1,0 |
| 4 | Alpha Argent-vs-Or 5j | argent out-perf >+2% | under-perf >−2% | zscore 60j /2 cap1 | 5 | 0,4 | 0,8 | 0,6 |
| 5 | Caixin PMI Chine manuf | PMI>51 | PMI<49 | lineaire centré 50 cap1 | 5 | 0,1 | 0,4 | 1,0 |
| 6 | CFTC COT Silver | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 5 | 0,2 | 0,7 | 1,0 |
| 7 | Inventaires COMEX Silver | baisse (z<−1) | hausse (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 4 | 0,4 | 0,9 | 0,8 |
| 8 | Flux ETF SLV+PSLV 5j net | entrées >+1σ | sorties <−1σ | zscore 60j /2 cap1 | 4 | 0,4 | 1,0 | 0,7 |
| 9 | Demande photovoltaïque + mining strikes | demande PV haussière OU strike Mexique/Pérou | demande PV baisse OU stocks normalisés | triplet composite | 3 | 0,2 | 0,5 | 1,0 |
| 10 | GATE régime extrême | n/a | FOMC/CPI US <24h OU NFP vendredi OU Silver Institute report <14j | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Cuivre  (slug: cuivre)
frontmatter: nom="Cuivre", ticker_principal="HG=F", famille="métaux-industriels", news_zone="Global", version=2
seuils_reussite_pct: 24h=0.8, 7j=2.0, 1m=5.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Caixin PMI Chine manuf | PMI>52 | PMI<48 | lineaire centré 50 cap1 (facteur ×1,5 → echelle réduite) | 12 | 0,1 | 0,4 | 1,0 |
| 2 | Inventaires LME+SHFE (trend 5j) | baissent (z<−1) | montent (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 8 | 0,3 | 1,0 | 0,9 |
| 3 | Mining strikes Chili/Pérou | grève active/annonce 30j | production normale | triplet | 5 | 0,7 | 0,9 | 0,5 |
| 4 | DXY trend 20j | DXY baisse | monte | zscore 60j /2 cap1, signe INVERSÉ | 6 | 0,3 | 0,7 | 0,8 |
| 5 | CFTC COT Copper nets | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 5 | 0,2 | 0,7 | 1,0 |
| 6 | Term structure M1-M3 | backwardation >50 USD/T | contango >100 USD/T | lineaire centré 0 cap1 | 5 | 0,2 | 0,9 | 0,7 |
| 7 | News construction/infra US-Chine | stimulus/plan infra 30j | annulation/réduction | triplet | 4 | 0,2 | 0,5 | 0,9 |
| 8 | Ratio Cuivre/Or | hausse (z>+1, growth) | baisse (z<−1, safe haven) | zscore 60j /2 cap1 | 3 | 0,4 | 0,7 | 0,6 |
| 9 | GATE régime extrême | n/a | Caixin PMI <24h OU FOMC <24h OU stimulus Chine annoncé 48h | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Café (Arabica)  (slug: cafe)
frontmatter: nom="Café (Arabica)", ticker_principal="KC=F", famille="agri-softs", news_zone="BR + VN", version=2
seuils_reussite_pct: 24h=1.0, 7j=3.0, 1m=7.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Météo Brésil Minas Gerais (gel/sécheresse) | gel imminent OU sécheresse persistante | pluies normales/abondantes | zscore 60j précipitations + check T min<4°C | 11 | 0,5 | 1,0 | 1,0 |
| 2 | Stocks ICE Arabica certifiés (trend 20j) | baissent (z<−1) | montent (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 9 | 0,3 | 0,9 | 1,0 |
| 3 | USD/BRL | baisse (real fort) | monte (real faible) | zscore 60j /2 cap1, signe INVERSÉ | 6 | 0,4 | 0,8 | 0,9 |
| 4 | CFTC COT Coffee | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 5 | 0,2 | 0,7 | 1,0 |
| 5 | Maladies cabosses/rouille | outbreak 30j | aucun | triplet | 5 | 0,3 | 0,7 | 1,0 |
| 6 | Cycle Brésil bi-annuel | année « off » (prod faible) | année « on » (prod forte) | triplet (calendrier CONAB) | 4 | 0,1 | 0,3 | 0,9 |
| 7 | Spread Arabica-Robusta | se resserre (z<−1) | s'élargit (z>+1) | zscore 60j /2 cap1 | 4 | 0,3 | 0,8 | 0,7 |
| 8 | Météo Vietnam (Robusta) | sécheresse | pluies normales | zscore précip 60j, signe INVERSÉ | 4 | 0,2 | 0,6 | 0,9 |
| 9 | GATE régime extrême | n/a | gel actif Brésil (T<0°C) OU CONAB <48h OU saison récolte avril-sept | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Cacao  (slug: cacao)
frontmatter: nom="Cacao", ticker_principal="CC=F", famille="agri-softs", news_zone="CI + GH", version=2
seuils_reussite_pct: 24h=1.5, 7j=4.0, 1m=10.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | Météo CI + Ghana (anomalie précip 30j) | sécheresse harmattan OU pluies excessives | pluies normales | zscore 60j /2 cap1 | 11 | 0,3 | 0,9 | 0,7 |
| 2 | Arrivées port Abidjan+San Pedro (trend 20j) | baissent (z<−1) | montent (z>+1) | zscore 60j /2 cap1, signe INVERSÉ | 9 | 0,4 | 1,0 | 0,9 |
| 3 | Hedge fund positioning + flux options ICE | OI puts>>calls + COT nets SHORT | OI calls>>puts + COT nets LONG | composite zscore put/call OI + zscore COT, signe INVERSÉ | 7 | 0,3 | 0,8 | 1,0 |
| 4 | CFTC COT Cocoa | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 6 | 0,2 | 0,7 | 1,0 |
| 5 | Grindings Q (broyages) | > consensus | < consensus | zscore trimestres publiés, signe direct | 5 | 0,1 | 0,3 | 1,0 |
| 6 | EU Deforestation Regulation (EUDR) | échéance proche, tension supply | implémentation sans rupture | triplet (phase EUDR) | 5 | 0,1 | 0,4 | 0,9 |
| 7 | Spread NY-London (CC=F vs C-=F) | s'élargit (squeeze NY) | se resserre | zscore 60j /2 cap1 | 4 | 0,5 | 0,9 | 0,6 |
| 8 | Maladies cabosses (Black Pod, Swollen Shoot) | outbreak 30j | aucun | triplet | 4 | 0,2 | 0,5 | 0,9 |
| 9 | USD/CFA + USD/Cedi | monnaies fortes (z<−1) | faibles | zscore moy pondérée 60j /2 cap1, signe INVERSÉ | 3 | 0,3 | 0,6 | 0,7 |
| 10 | GATE régime extrême | n/a | harmattan actif (déc-mars) OU ICCO <48h OU grindings <7j OU EUDR échéance <30j | gate | gate | 1,0 | 1,0 | 1,0 |

---

## Blé  (slug: ble)
frontmatter: nom="Blé", ticker_principal="ZW=F", famille="agri", news_zone="US + EU + Mer Noire + AU", version=2
seuils_reussite_pct: 24h=0.8, 7j=2.5, 1m=6.0

| # | Critère | LONG (+1) | SHORT (−1) | Normalisation | Poids | 24h | 7j | 1m |
|---|---|---|---|---|---|---|---|---|
| 1 | USDA WASDE stocks-to-use mondial (delta) | ratio baisse (offre serrée) | ratio monte (oversupply) | zscore 12 publi /2 cap1, signe INVERSÉ | 11 | 0,1 | 0,5 | 1,0 |
| 2 | NOAA drought % Midwest+Plains D2+ | >40% drought (z>+1) | <10% (z<−1) | zscore 60j /2 cap1, signe DIRECT | 9 | 0,3 | 1,0 | 1,0 |
| 3 | Géopolitique mer Noire | escalade (blocus/rupture corridor/sanctions) 14j | détente (accord/reconduction) | triplet | 8 | 0,7 | 0,9 | 0,7 |
| 4 | NASS Crop Progress % good/excellent | <50% (z<−1) | >70% (z>+1) | zscore même semaine 5 ans, signe INVERSÉ | 6 | 0,2 | 0,9 | 0,8 |
| 5 | Demande chinoise (imports USDA FAS) | > consensus | < consensus | zscore 12 mois, signe direct | 5 | 0,1 | 0,3 | 1,0 |
| 6 | CFTC COT Wheat | nets SHORT extreme | nets LONG extreme | zscore 252j /2 cap1, signe INVERSÉ | 5 | 0,2 | 0,7 | 1,0 |
| 7 | Météo Australie (dryland) | sécheresse persistante | normales/favorables | zscore précip 60j (NSW/VIC/WA), signe INVERSÉ | 5 | 0,1 | 0,4 | 1,0 |
| 8 | Égypte GASC tenders | tender massif + prix élevé | annulation OU prix très bas | zscore 12 tenders, signe direct | 4 | 0,5 | 0,9 | 0,6 |
| 9 | DXY trend 20j | DXY baisse | monte | zscore 60j /2 cap1, signe INVERSÉ | 4 | 0,3 | 0,7 | 0,8 |
| 10 | GATE régime extrême | n/a | USDA WASDE <7j OU saison récolte US (mai-août)/AU (nov-jan) OU mouvement corridor mer Noire 48h | gate | gate | 1,0 | 1,0 | 1,0 |
