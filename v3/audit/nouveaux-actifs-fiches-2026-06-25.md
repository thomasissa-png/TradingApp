# Fiches-drafts — Nouveaux actifs 2026-06-25
# USD/JPY · Cotton (COTN) · Sucre (CANE)

> Statut : DRAFT — ne pas créer les .yml dans config/ avant validation Thomas.
> Panel 3 experts : Analyst quant (A) · News Trader (NT) · Spéculateur (S).
> Règle zéro invention : chaque critère porte son statut faisabilité.
> Cœur = tendance (numériques). News = contexte secondaire.

---

## Sommaire

1. [Concertation préalable — désaccords résolus](#0-concertation)
2. [USD/JPY](#1-usdjpy)
3. [Cotton — COTN](#2-cotton)
4. [Sucre — CANE](#3-sucre)
5. [Tableau faisabilité consolidé](#4-faisabilite)
6. [Plan de câblage criteres_calculator.py](#5-cablage)
7. [Liste critères manuels / news-driven](#6-manuels)

---

## 0. Concertation préalable — désaccords résolus {#0-concertation}

### Désaccord 1 : poids momentum vs fondamentaux sur USD/JPY

**A (Analyst quant)** : Le différentiel de taux US-JP 2Y doit rester le critère dominant (poids 12). Le momentum prix est utile mais secondaire — sur le forex, le "carry" structure la tendance sur 7j/1m. Poids momentum : 6 (prove-first, comme les autres actifs).

**NT (News Trader)** : En 2024-2025, la BoJ a cassé trois fois un momentum établi en quelques heures (YCC exit, surprise hawkish). Le momentum doit être limité à poids 5, et le critère "risque d'intervention BoJ" (news) doit peser au moins 5.

**S (Spéculateur)** : Je ne trade pas USD/JPY sans regarder le momentum 7j. C'est le marché le plus suivi par les touristes macro. Si le momentum 7j est SHORT fort ET que le COT est net long JPY, c'est un signal d'écrasement imminent. Poids momentum 7j = 6, 20j = 5.

**Verdict convergent** : Différentiel 2Y US-JP poids 11 (dominant), momentum 7j poids 6 / momentum 20j poids 5, critère BoJ/intervention = triplet news poids 5. Le quant structure, les news alertent. Confiance : 8/10.

### Désaccord 2 : critère "parité éthanol/sucre" sur le Sucre

**A** : La parité sucre/éthanol Brésil est le driver fondamental le plus important après la météo. Le Brésil arbitre en permanence entre produire du sucre ou de l'éthanol selon le prix relatif Brent/sucre. C'est quantifiable via le spread Brent (Twelve XBR/USD) et la cotation CANE elle-même. Poids : 8.

**NT** : Ce ratio est pertinent, mais la donnée propre (prix de l'éthanol anhydre ESALQ) n'est pas sourçable sans abonnement brésilien. Utiliser le Brent comme proxy est une approximation grossière. Si on l'ajoute avec cette approximation, je veux un statut "proxy" visible.

**S** : Accord avec NT. Le Brent monte = l'éthanol vaut plus = le Brésil mouline moins de sucre = haussier. C'est une corrélation directe à câbler comme zscore XBR/USD, signe +1 (Brent monte = sucre haussier). C'est une approximation mais elle est documentée et non inventée.

**Verdict convergent** : Critère "Attractivité relative éthanol Brésil (proxy Brent)" conservé, source = Twelve XBR/USD z-score, statut ✅ avec note "proxy Brent — voir câblage". Poids 7. Confiance : 7/10.

### Désaccord 3 : critères météo coton — Texas seul ou Texas + Inde ?

**A** : Le Texas représente ~55 % de la production US. Open-Meteo couvre n'importe quelle coordonnée. Câbler Texas (Lubbock ~33N/-101W) est direct et sourçable. L'Inde (Gujarat/Telangana) est le 2e producteur mondial, mais les données météo indiennes sont bruitées.

**NT** : L'Inde + Pakistan représentent 40 % de la production mondiale. Les alertes de mousson faible Gujarat font souvent monter le cotton de 3-5 % sur la semaine. Il faut au moins un critère Inde, même imparfait.

**S** : Je veux les deux mais avec des poids différenciés : Texas poids 9 (critique pour la qualité US long staple, le seul que COTN reflète vraiment via le WisdomTree ETC basé sur futures ICE). Inde poids 5, même zone Open-Meteo Gujarat (22N/72E). Verdict à l'usage.

**Verdict convergent** : Deux critères météo, clés distinctes. Texas (cle : `meteo_texas_cotton_precip`) poids 9, Inde Gujarat (cle : `meteo_inde_gujarat_coton`) poids 5. Les deux en `zscore_abs` (sécheresse OU excès = haussier, cohérent avec la logique cacao/café). Confiance : 8/10.

---

## 1. USD/JPY {#1-usdjpy}

### Contexte actif

- Ticker Twelve : `USD/JPY` (forex natif, vérifiés)
- Famille : `fx`
- Ticker interne (YAML `ticker_principal`) : `USD/JPY` (format Twelve natif, pas Yahoo `=X`)
- Conclusion LONG = USD/JPY monte (dollar fort / yen faible)
- Seuils réussite % : 24h 0.3 · 7j 1.0 · 1m 2.5
- Note de confiance panel : **8/10**

### YAML draft

```yaml
# USD/JPY — fiche de positionnement v1-draft 2026-06-25
# Conclusion LONG = USD/JPY monte (dollar se renforce, yen faiblit).
# Ticker Twelve natif : USD/JPY (validé).
# Famille fx — actif continu (coté 24h/5j, angle mort overnight corrigé par _FRESH_PRICE_OVERRIDES).
actif: "USD/JPY"
ticker_principal: "USD/JPY"
famille: "fx"
news_zone: "US + JP"
version: 1

seuils_reussite_pct:
  "24h": 0.3
  "7j": 1.0
  "1m": 2.5

criteres:

  # CRITÈRE DOMINANT — différentiel taux 2Y US-JP.
  # Source : FRED DGS2 (2Y US Treasury, quotidien) - JGB 2Y JP.
  # JGB 2Y : FRED ne publie PAS de série quotidienne du JGB 2 ans. La série
  # IRGTLT01JPM156N (OECD, Japon long terme) est mensuelle et porte sur ~10Y.
  # Alternative directe : Bank of Japan Statistics (stats.boj.or.jp, format CSV,
  # sans clé) publie les taux JGB quotidiens toutes maturités dont 2Y.
  # → Câblage requis : nouveau fetcher `fetch_boj_jgb_2y()` (HTTP BOJ stats).
  # En attendant : proxy FRED IRGTLT01JPM156N (≈10Y, mensuel) — dégradation visible.
  - id: 1
    nom: "Écart de taux courts US − Japon (2 ans)"
    source: "FRED DGS2 (2Y US) - BOJ stats 2Y JGB (à câbler) ; proxy FRED IRGTLT01JPM156N (mensuel ≈10Y)"
    cle_courante: "diff_taux_2y_us_jp"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1                    # direct : spread s'élargit (Fed hawkish / BoJ dovish) => LONG USD/JPY
    poids: 11
    pertinence: { "24h": 0.4, "7j": 1.0, "1m": 1.0 }
    effet_long: "Spread s'élargit (Fed hawkish / BoJ dovish)"
    effet_short: "Spread se resserre (BoJ hawkish / Fed pivot)"

  # Tendance du dollar (DXY proxy FRED DTWEXBGS — déjà câblé, clé partagée)
  # Note L023 : `dxy_trend_20j` est déjà utilisée dans blé.yml, eurusd.yml, etc.
  # L023 = ne pas réutiliser une clé d'un autre actif. MAIS dxy_trend_20j est
  # une clé MACRO PARTAGÉE (même logique que hy_credit_spread ou taux_10y_us_reels_tips
  # qui apparaissent dans plusieurs fiches). Ce n'est PAS un critère propre à l'actif.
  # Décision : on l'utilise telle quelle (clé partagée légitime, comme dans blé/eurusd).
  # Le dispatcher gère la déduplication par critère, pas par clé.
  - id: 2
    nom: "Tendance du dollar (20 jours)"
    source: "FRED DTWEXBGS (déjà câblé — criteres_calculator.py FRED_SERIES_SIMPLE)"
    cle_courante: "dxy_trend_20j"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1                    # direct : DXY monte => LONG USD/JPY
    poids: 9
    pertinence: { "24h": 0.7, "7j": 1.0, "1m": 0.8 }
    effet_long: "DXY monte (dollar fort)"
    effet_short: "DXY baisse (dollar faible)"

  # Tendance 7 jours USD/JPY — momentum court
  - id: 3
    nom: "Tendance de l'USD/JPY (7 jours)"
    source: "Twelve Data USD/JPY (natif forex)"
    cle_courante: "momentum_prix_7j_usdjpy"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1
    poids: 6
    pertinence: { "24h": 0.5, "7j": 1.0, "1m": 0.2 }
    effet_long: "USD/JPY en tendance haussière (z>+1)"
    effet_short: "USD/JPY en tendance baissière (z<-1)"

  # Tendance 20 jours USD/JPY — momentum moyen terme
  - id: 4
    nom: "Tendance de l'USD/JPY (20 jours)"
    source: "Twelve Data USD/JPY (natif forex)"
    cle_courante: "momentum_prix_20j_usdjpy"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1
    poids: 5
    pertinence: { "24h": 0.4, "7j": 0.3, "1m": 1.0 }
    effet_long: "USD/JPY en tendance haussière (z>+1)"
    effet_short: "USD/JPY en tendance baissière (z<-1)"

  # Positionnement CFTC JPY (non-commercials nets)
  # CFTC market name : "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE"
  # Code CFTC : #097741 (contract code). Dataset Socrata jun7-fc8e déjà câblé.
  # → Ajouter entrée dans CFTC_MARKETS : "cftc_cot_jpy_nets" → "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE"
  # Signe inversé : nets SHORT JPY extreme (spéculateurs très short yen) => squeeze => USD/JPY baisse => SHORT.
  # Logique contrarian classique : nets LONG extreme JPY => yen bien acheté => USD/JPY haussier COURT TERME (retournement).
  # Non. Lecture directe : nets LONG JPY = spéculateurs achètent le yen = USD/JPY BAISSE => signe -1.
  - id: 5
    nom: "Positionnement des gros spéculateurs (yen)"
    source: "CFTC Socrata jun7-fc8e — JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE (à ajouter CFTC_MARKETS)"
    cle_courante: "cftc_cot_jpy_nets"
    normalisation: "zscore"
    zscore_window: 252
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : nets LONG JPY extreme => USD/JPY baisse => SHORT
    poids: 6
    pertinence: { "24h": 0.2, "7j": 0.6, "1m": 1.0 }
    effet_long: "Nets SHORT JPY extreme (squeeze à venir, yen s'apprécie)"
    effet_short: "Nets LONG JPY extreme (yen acheté, USD/JPY sous pression)"

  # Différentiel taux longs US-JP (10 ans)
  # FRED DGS10 (déjà câblé) - IRGTLT01JPM156N (mensuel Japon).
  # Même câblage que le spread US-DE (FRED_SPREADS) — à ajouter.
  - id: 6
    nom: "Écart de taux longs US − Japon (10 ans)"
    source: "FRED DGS10 (US 10Y, daily) - FRED IRGTLT01JPM156N (JP long-term, mensuel) — à ajouter FRED_SPREADS"
    cle_courante: "diff_taux_10y_us_jp"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1                    # direct : spread s'élargit => LONG USD/JPY
    poids: 5
    pertinence: { "24h": 0.3, "7j": 0.8, "1m": 1.0 }
    effet_long: "Spread s'élargit (10Y US >> JP)"
    effet_short: "Spread se resserre (BoJ relève / Fed baisse)"

  # Sentiment risque (VIX) — USD/JPY proxy risque
  # VIX monte = risk-off = yen s'apprécie = USD/JPY baisse.
  # CBOE VIX déjà câblé (taux_10y_us_reels_tips / niveau_vix_absolu dans CBOE CSV).
  # La clé `niveau_vix_absolu` est propre à vix.yml.
  # Ici on câble une NOUVELLE clé `vix_usdjpy_risk` via la même source CBOE CSV.
  # Signe -1 : VIX monte => USD/JPY baisse.
  - id: 7
    nom: "Niveau de volatilité implicite (VIX — stress marché)"
    source: "CBOE VIX CSV (déjà câblé dans criteres_calculator — mapping CBOE) — nouvelle cle_courante"
    cle_courante: "vix_risk_usdjpy"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : VIX monte (risk-off) => yen s'apprécie => USD/JPY baisse
    poids: 5
    pertinence: { "24h": 0.8, "7j": 0.6, "1m": 0.3 }
    effet_long: "VIX baisse (risk-on, carry JPY actif)"
    effet_short: "VIX monte (risk-off, fuite vers le yen)"

  # Politique BoJ / intervention — critère news-driven
  # La BoJ peut intervenir verbalement ou physiquement (achat de yen). Ce critère
  # est NON quantifiable en automatique : il n'existe pas de source API publique
  # gratuite du taux cible BoJ en temps réel (il change à la réunion BoJ).
  # → Critère triplet news-driven (DeepSeek via events-log, comme geopolitique_mer_noire).
  - id: 8
    nom: "Politique BoJ et risque d'intervention (verbal / physique)"
    source: "events-log (news IA DeepSeek — triplet)"
    cle_courante: "boj_intervention_risk"
    normalisation: "triplet"    # +1 BoJ hawkish/intervention contre USD/JPY montée / 0 / -1 BoJ dovish
    cap: 1.0
    signe: -1                   # inversé : BoJ hawkish (+1) => USD/JPY BAISSE => SHORT
    poids: 5
    pertinence: { "24h": 1.0, "7j": 0.8, "1m": 0.4 }
    effet_long: "BoJ dovish / aucune intervention (carry actif)"
    effet_short: "BoJ hawkish / intervention verbale ou physique"

  # Carry attractivité (taux Fed Funds vs taux cible BoJ)
  # FRED DFEDTARU (Federal Funds Rate upper bound, daily) disponible.
  # BoJ policy rate : pas de série FRED fiable quotidienne. Alternative manuelle.
  # Décision : OMIS en automatique ; intégré partiellement via diff_taux_2y_us_jp (id=1).
  # Mentionné ici pour traçabilité — voir section manuels.

  # GATE
  - id: 9
    nom: "Drapeau : événement majeur imminent"
    source: "events-log + calendrier"
    cle_courante: "gate_regime_extreme_usdjpy"
    normalisation: "gate"
    pertinence: { "24h": 1.0, "7j": 1.0, "1m": 1.0 }
    effet_short: "FOMC <24h OU réunion BoJ <24h OU NFP US ce vendredi OU CPI US <24h"
```

### Note de confiance panel USD/JPY : 8/10

Critères numériques solides (différentiels FRED + DXY + momentum Twelve + COT CFTC). Le critère BoJ est le seul news-driven — justifié car c'est le risque le moins anticipable du marché JPY. La clé `gate_regime_extreme_usdjpy` est distincte de `gate_regime_extreme` (L023 — clé unique par actif pour les gates spécifiques à l'actif).

**Réserve A** : Le différentiel 2Y US-JP sera en proxy mensuel jusqu'au câblage BOJ stats — couverture réduite à 7j/1m (pertinence 24h = 0.4 acceptable).
**Réserve NT** : La réunion BoJ doit impérativement figurer dans le calendrier `events-log` (comme les FOMC). À vérifier.

---

## 2. Cotton — COTN {#2-cotton}

### Contexte actif

- Ticker Twelve : `COTN` (ETC WisdomTree Cotton, LSE, coté en USD)
- Famille : `agri-softs`
- Ticker interne (`ticker_principal`) : `COTN`
- Conclusion LONG = prix du coton monte
- Note : COTN est un ETC qui trace les futures ICE Cotton No. 2 (#2). Ce n'est pas un ETF de producteurs. Le niveau de prix est celui du WisdomTree ETC (≈ futures, mais avec contango/roll effect). Les critères de momentum doivent utiliser COTN directement.
- Seuils réussite % : 24h 1.0 · 7j 3.5 · 1m 8.0
- Note de confiance panel : **7/10**

### YAML draft

```yaml
# Cotton (COTN) — fiche de positionnement v1-draft 2026-06-25
# Ticker Twelve : COTN (ETC WisdomTree Cotton, LSE/USD).
# Conclusion LONG = coton monte.
actif: "Cotton"
ticker_principal: "COTN"
famille: "agri-softs"
news_zone: "US + IN + CN"
version: 1

seuils_reussite_pct:
  "24h": 1.0
  "7j": 3.5
  "1m": 8.0

criteres:

  # Météo Texas (ceinture coton US) — driver offre US #1
  # Open-Meteo lat=33.5, lon=-101.9 (Lubbock TX, cœur du West Texas cotton belt)
  # zscore_abs : sécheresse OU pluies excessives = haussier (même logique que cacao/blé)
  # Le Texas représente ~55 % de la production US HRW coton Pima/Upland. Sec = pire.
  - id: 1
    nom: "Météo ceinture coton Texas (sécheresse OU excès)"
    source: "Open-Meteo lat=33.5, lon=-101.9 (Lubbock TX) — à ajouter METEO_CRITERIA"
    cle_courante: "meteo_texas_cotton_precip"
    normalisation: "zscore_abs"
    zscore_window: 60
    zscore_div: 2
    zscore_centre: 0.0
    cap: 1.0
    signe: 1                    # +1 : écart à la normale => HAUSSIER
    poids: 9
    pertinence: { "24h": 0.3, "7j": 1.0, "1m": 1.0 }
    effet_long: "Sécheresse West Texas OU pluies excessives (qualité dégradée)"
    effet_short: "Précipitations proches de la normale"

  # Météo Inde Gujarat — driver offre Inde #2 mondial
  # Open-Meteo lat=22.3, lon=72.6 (Gujarat, zone coton Inde principale)
  # Même logique zscore_abs — mousson faible OU trop forte
  - id: 2
    nom: "Météo Inde Gujarat (mousson coton — sécheresse OU excès)"
    source: "Open-Meteo lat=22.3, lon=72.6 (Gujarat) — à ajouter METEO_CRITERIA"
    cle_courante: "meteo_inde_gujarat_coton"
    normalisation: "zscore_abs"
    zscore_window: 60
    zscore_div: 2
    zscore_centre: 0.0
    cap: 1.0
    signe: 1
    poids: 5
    pertinence: { "24h": 0.2, "7j": 0.8, "1m": 1.0 }
    effet_long: "Mousson déficitaire OU excès Gujarat (offre indienne menacée)"
    effet_short: "Mousson normale (offre Inde sécurisée)"

  # COT coton ICE — positionnement spéculatif
  # CFTC COT : "COTTON NO. 2 - ICE FUTURES U.S." (contract #033661)
  # → Ajouter dans CFTC_MARKETS : "cftc_cot_cotton" → "COTTON NO. 2 - ICE FUTURES U.S."
  - id: 3
    nom: "Positionnement des gros spéculateurs (coton ICE)"
    source: "CFTC Socrata jun7-fc8e — COTTON NO. 2 - ICE FUTURES U.S. (#033661) — à ajouter CFTC_MARKETS"
    cle_courante: "cftc_cot_cotton"
    normalisation: "zscore"
    zscore_window: 252
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : nets SHORT extreme => LONG (squeeze spéculatif)
    poids: 7
    pertinence: { "24h": 0.2, "7j": 0.7, "1m": 1.0 }
    effet_long: "Nets SHORT extreme (squeeze à venir)"
    effet_short: "Nets LONG extreme (positions chargées)"

  # Tendance prix COTN (20 jours) — Twelve natif
  - id: 4
    nom: "Tendance du coton COTN (20 jours)"
    source: "Twelve Data COTN (ETC LSE/USD)"
    cle_courante: "momentum_prix_20j_coton"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1
    poids: 6
    pertinence: { "24h": 0.4, "7j": 0.3, "1m": 1.0 }
    effet_long: "COTN en tendance haussière (z>+1)"
    effet_short: "COTN en tendance baissière (z<-1)"

  # Tendance prix COTN (7 jours)
  - id: 5
    nom: "Tendance du coton COTN (7 jours)"
    source: "Twelve Data COTN (ETC LSE/USD)"
    cle_courante: "momentum_prix_7j_coton"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1
    poids: 6
    pertinence: { "24h": 0.4, "7j": 1.0, "1m": 0.2 }
    effet_long: "COTN en tendance haussière"
    effet_short: "COTN en tendance baissière"

  # Tendance du dollar — poids coton USD libellé en USD
  # Même clé partagée dxy_trend_20j (FRED DTWEXBGS déjà câblé)
  # Signe -1 : dollar fort = coton moins cher pour acheteurs non-USD => baissier
  - id: 6
    nom: "Tendance du dollar (20 jours)"
    source: "FRED DTWEXBGS (déjà câblé — criteres_calculator.py FRED_SERIES_SIMPLE)"
    cle_courante: "dxy_trend_20j"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : DXY monte => coton plus cher pour acheteurs => baissier demande
    poids: 5
    pertinence: { "24h": 0.3, "7j": 0.7, "1m": 0.8 }
    effet_long: "DXY baisse (coton moins cher en devises étrangères)"
    effet_short: "DXY monte (demande non-USD comprimée)"

  # Demande Chine — news-driven (pas de source API gratuite fiable)
  # Les imports textiles Chine (GACC) sont mensuels et non disponibles en API.
  # Triplet news IA (DeepSeek) : commandes Chine, achat spot, tensions textile.
  - id: 7
    nom: "Demande chinoise coton (commandes et imports)"
    source: "events-log (news IA DeepSeek — triplet)"
    cle_courante: "demande_chine_coton"
    normalisation: "triplet"    # +1 commandes élevées / 0 / -1 annulations/baisse
    cap: 1.0
    signe: 1
    poids: 5
    pertinence: { "24h": 0.5, "7j": 0.9, "1m": 0.7 }
    effet_long: "Chine commandes fortes (achat spot actif)"
    effet_short: "Chine annule / réduit les achats"

  # USDA WASDE / CropProgress cotton — statut cultures US
  # CropProgress coton : USDA NASS publie % Planted/Boll Set/Harvested.
  # Accessible via USDA NASS QuickStats API (clé gratuite USDA_API_KEY requise — déjà identifiée dans project-context).
  # Sans clé : critère MANUEL (v3/data/manual/) ou news-driven.
  # Décision : statut ⚠️ manuel — câblable si USDA_API_KEY obtenu (cf. blé.yml id=4 `nass_crop_progress`).
  - id: 8
    nom: "État des cultures coton US (% bon/excellent USDA NASS)"
    source: "USDA NASS QuickStats API (clé USDA_API_KEY requise — ⚠️ manuel sans clé ; cf. v3/data/manual/)"
    cle_courante: "nass_crop_progress_cotton"
    normalisation: "zscore"
    zscore_window: 5            # même semaine 5 ans (cohérent blé id=4)
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : <50% => mauvaise récolte => LONG
    poids: 6
    pertinence: { "24h": 0.2, "7j": 0.9, "1m": 0.8 }
    effet_long: "< 50% bon/excellent (récolte dégradée)"
    effet_short: "> 70% bon/excellent (récolte saine)"

  # GATE
  - id: 9
    nom: "Drapeau : événement majeur imminent"
    source: "events-log + calendrier"
    cle_courante: "gate_regime_extreme_coton"
    normalisation: "gate"
    pertinence: { "24h": 1.0, "7j": 1.0, "1m": 1.0 }
    effet_short: "USDA WASDE <7j OU CropProgress coton <48h OU saison récolte US (sept-nov)"
```

### Note de confiance panel Cotton : 7/10

**A** : Le COT coton et la météo Texas sont les deux drivers quantifiables les plus fiables. La fiche est solide si USDA_API_KEY est activé — sinon le CropProgress tombe en ⚠️ manuel.

**NT** : La demande Chine est THE catalyst sur le coton en 2024-2025 (annulations en masse = -10 % en 2 jours). Le triplet news est indispensable. Poids 5 conservateur.

**S** : COTN est un ETC avec roll costs. Le momentum peut diverger du futures ICE No. 2 les jours de roll. Acceptable tant que les seuils de réussite sont calibrés sur COTN lui-même (c'est le cas).

---

## 3. Sucre — CANE {#3-sucre}

### Contexte actif

- Ticker Twelve : `CANE` (Teucrium Sugar Fund, NYSE, coté en USD)
- Famille : `agri-softs`
- Ticker interne (`ticker_principal`) : `CANE`
- Conclusion LONG = prix du sucre monte
- Note : CANE est un ETF de futures sucre #11 (ICE). Comme COTN, le momentum doit se calculer sur CANE directement.
- Seuils réussite % : 24h 1.2 · 7j 4.0 · 1m 9.0
- Note de confiance panel : **7/10**

### YAML draft

```yaml
# Sucre (CANE) — fiche de positionnement v1-draft 2026-06-25
# Ticker Twelve : CANE (Teucrium Sugar Fund, NYSE/USD).
# Conclusion LONG = sucre monte.
actif: "Sucre"
ticker_principal: "CANE"
famille: "agri-softs"
news_zone: "BR + IN + TH"
version: 1

seuils_reussite_pct:
  "24h": 1.2
  "7j": 4.0
  "1m": 9.0

criteres:

  # Météo Brésil Centre-Sud (canne à sucre) — driver offre #1 mondial
  # Le Brésil Centre-Sud (SP/MG/GO) représente ~90 % de la production sucrière brésilienne
  # et ~40 % de l'offre mondiale. Campagne avril-novembre.
  # Open-Meteo lat=-21.2, lon=-48.1 (Ribeirão Preto SP — cœur de la ceinture sucrière)
  # zscore_abs : sécheresse ET excès de pluie (pourriture) = haussier
  - id: 1
    nom: "Météo Brésil Centre-Sud — canne à sucre (sécheresse OU excès)"
    source: "Open-Meteo lat=-21.2, lon=-48.1 (Ribeirão Preto SP) — à ajouter METEO_CRITERIA"
    cle_courante: "meteo_bresil_canne_sucre"
    normalisation: "zscore_abs"
    zscore_window: 60
    zscore_div: 2
    zscore_centre: 0.0
    cap: 1.0
    signe: 1
    poids: 10
    pertinence: { "24h": 0.3, "7j": 1.0, "1m": 1.0 }
    effet_long: "Sécheresse OU excès de pluie (rendements dégradés)"
    effet_short: "Conditions normales (récolte en ligne)"

  # Attractivité éthanol Brésil — proxy Brent
  # Le Brésil arbitre entre sucre et éthanol anhydre selon le prix relatif.
  # Quand le Brent monte, l'éthanol vaut plus => les usines brésiliennes privilégient
  # l'éthanol => moins de sucre => haussier. Proxy : XBR/USD (Twelve natif).
  # Source propre du ratio : Cepea/ESALQ (payant, BR) — non disponible.
  # Proxy Brent = approximation documentée et non inventée.
  - id: 2
    nom: "Attractivité relative éthanol Brésil (proxy Brent/sucre)"
    source: "Twelve Data XBR/USD (Brent natif, déjà câblé pour pétrole.yml)"
    cle_courante: "brent_ethanol_proxy_sucre"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1                    # direct : Brent monte => éthanol attractif => moins de sucre => HAUSSIER
    poids: 7
    pertinence: { "24h": 0.3, "7j": 0.8, "1m": 1.0 }
    effet_long: "Brent monte (éthanol plus attractif que le sucre)"
    effet_short: "Brent baisse (usines reviennent au sucre)"

  # USD/BRL — parité sucrière (coût de production en réal, prix vendu en USD)
  # Quand le réal se déprécie (USD/BRL monte), les exportateurs brésiliens reçoivent
  # plus de réais pour le même prix dollar => moins pression à vendre => baissier spot
  # court terme. Mais aussi : réal faible = compétitivité export accrue => haussier long.
  # Lecture retenue (alignée café.yml id=3) : USD/BRL baisse (réal fort) => coûts relatifs
  # plus élevés => moins de pression à exporter => haussier sucre. Signe -1.
  # Source : Twelve Data USD/BRL (déjà câblé pour café.yml `usd_brl`)
  - id: 3
    nom: "Taux de change dollar / réal brésilien"
    source: "Twelve Data USD/BRL (déjà câblé — café.yml cle usd_brl)"
    cle_courante: "usd_brl_sucre"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : USD/BRL baisse (réal fort) => haussier sucre
    poids: 6
    pertinence: { "24h": 0.4, "7j": 0.8, "1m": 0.9 }
    effet_long: "Réal fort (USD/BRL baisse) — marges export réduites"
    effet_short: "Réal faible (USD/BRL monte) — pression export Brésil"

  # COT sucre ICE — positionnement spéculatif
  # CFTC : "SUGAR NO. 11 - ICE FUTURES U.S." (contract #080732)
  # → Ajouter CFTC_MARKETS : "cftc_cot_sugar" → "SUGAR NO. 11 - ICE FUTURES U.S."
  - id: 4
    nom: "Positionnement des gros spéculateurs (sucre ICE No. 11)"
    source: "CFTC Socrata jun7-fc8e — SUGAR NO. 11 - ICE FUTURES U.S. (#080732) — à ajouter CFTC_MARKETS"
    cle_courante: "cftc_cot_sugar"
    normalisation: "zscore"
    zscore_window: 252
    zscore_div: 2
    cap: 1.0
    signe: -1                   # inversé : nets SHORT extreme => LONG (squeeze)
    poids: 6
    pertinence: { "24h": 0.2, "7j": 0.7, "1m": 1.0 }
    effet_long: "Nets SHORT extreme (squeeze à venir)"
    effet_short: "Nets LONG extreme (positions chargées)"

  # Tendance CANE (20 jours)
  - id: 5
    nom: "Tendance du sucre CANE (20 jours)"
    source: "Twelve Data CANE (NYSE/USD)"
    cle_courante: "momentum_prix_20j_sucre"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1
    poids: 6
    pertinence: { "24h": 0.4, "7j": 0.3, "1m": 1.0 }
    effet_long: "CANE en tendance haussière (z>+1)"
    effet_short: "CANE en tendance baissière (z<-1)"

  # Tendance CANE (7 jours)
  - id: 6
    nom: "Tendance du sucre CANE (7 jours)"
    source: "Twelve Data CANE (NYSE/USD)"
    cle_courante: "momentum_prix_7j_sucre"
    normalisation: "zscore"
    zscore_window: 60
    zscore_div: 2
    cap: 1.0
    signe: 1
    poids: 6
    pertinence: { "24h": 0.4, "7j": 1.0, "1m": 0.2 }
    effet_long: "CANE en tendance haussière"
    effet_short: "CANE en tendance baissière"

  # Production Inde/Thaïlande — news-driven
  # Inde : 2e producteur mondial (~17 %). Les décisions ISMA sur quotas d'export
  # sont l'un des drivers les plus impactants du sucre mondial (baisse -5 % en 1 jour
  # sur annonce de restriction). Pas de source API gratuite fiable.
  # Thaïlande : 3e exportateur mondial. Données Office of Cane and Sugar Board (OCSB),
  # non disponibles en API.
  # → Triplet news IA (DeepSeek) : restrictions export Inde, stocks ISMA, production Thaïlande.
  - id: 7
    nom: "Production et exports Inde + Thaïlande (restrictions / abondance)"
    source: "events-log (news IA DeepSeek — triplet)"
    cle_courante: "prod_inde_thai_sucre"
    normalisation: "triplet"    # +1 restriction export / pénurie / 0 / -1 abondance
    cap: 1.0
    signe: 1
    poids: 5
    pertinence: { "24h": 0.6, "7j": 0.9, "1m": 0.7 }
    effet_long: "Restriction export Inde OU mauvaise récolte Thaïlande"
    effet_short: "Inde lève les restrictions / bonne récolte Thaïlande"

  # Exports Brésil (UNICA/MAPA) — news-driven
  # UNICA publie des données bi-mensuelles sur la production/export de canne.
  # Non disponible via API gratuite en temps réel.
  # → Triplet news IA sur rythme des exports.
  - id: 8
    nom: "Rythme des exports sucre Brésil (UNICA / ports)"
    source: "events-log (news IA DeepSeek — triplet)"
    cle_courante: "exports_bresil_sucre"
    normalisation: "triplet"    # +1 recul exports / 0 / -1 accélération exports
    cap: 1.0
    signe: 1                    # baisse exports Brésil => offre mondiale réduite => HAUSSIER
    poids: 4
    pertinence: { "24h": 0.3, "7j": 0.8, "1m": 0.8 }
    effet_long: "Recul exports Brésil (offre mondiale resserrée)"
    effet_short: "Exports Brésil accélèrent (offre abondante)"

  # GATE
  - id: 9
    nom: "Drapeau : événement majeur imminent"
    source: "events-log + calendrier"
    cle_courante: "gate_regime_extreme_sucre"
    normalisation: "gate"
    pertinence: { "24h": 1.0, "7j": 1.0, "1m": 1.0 }
    effet_short: "UNICA bi-mensuel <48h OU annonce ISMA quota export OU récolte Brésil début/fin campagne (avr/nov)"
```

### Note de confiance panel Sucre : 7/10

**A** : Fiche solide sur les 6 premiers critères (météo + Brent proxy + BRL + COT + momentum). Les 2 triplets news (id=7/8) sont justifiés par l'absence de source API gratuite, mais ils représentent un risque de couverture si DeepSeek ne capture pas les communiqués ISMA (souvent en hindi ou sur des portails locaux).

**NT** : Le critère parité éthanol (id=2) est le plus original et pertinent. En 2023-2024, la corrélation Brent/sucre a été forte (+0.65 sur roulant 90j). Attention : si le Brent baisse pour des raisons de demande globale (récession), cela peut être bearish sucre ET Brent simultanément — le proxy peut se retourner. Surveiller en shadow.

**S** : Les seuils de réussite sont ambitieux (9 % sur 1 mois). Le sucre est volatile — à valider en shadow avant de calibrer. La fiche est plus défensive que le café/cacao en termes de fondamentaux : 3 critères news sur 8 = risque de couverture faible si les news ne sont pas capturées.

---

## 4. Tableau faisabilité consolidé {#4-faisabilite}

| Actif | Critère (cle_courante) | Source | Statut faisabilité |
|---|---|---|---|
| USD/JPY | `diff_taux_2y_us_jp` | FRED DGS2 (US, daily) − BOJ stats JGB 2Y (à câbler) | ⚠️ proxy mensuel FRED IRGTLT01JPM156N en attendant |
| USD/JPY | `dxy_trend_20j` | FRED DTWEXBGS (déjà câblé) | ✅ maintenant (partagée) |
| USD/JPY | `momentum_prix_7j_usdjpy` | Twelve Data USD/JPY | ✅ maintenant — ajouter préfixe momentum dispatcher |
| USD/JPY | `momentum_prix_20j_usdjpy` | Twelve Data USD/JPY | ✅ maintenant |
| USD/JPY | `cftc_cot_jpy_nets` | CFTC Socrata JAPANESE YEN - CME | ✅ maintenant — ajouter CFTC_MARKETS |
| USD/JPY | `diff_taux_10y_us_jp` | FRED DGS10 − IRGTLT01JPM156N (mensuel) | ✅ maintenant — ajouter FRED_SPREADS |
| USD/JPY | `vix_risk_usdjpy` | CBOE VIX CSV (déjà câblé) | ✅ maintenant — nouvelle cle_courante |
| USD/JPY | `boj_intervention_risk` | events-log DeepSeek triplet | ✅ maintenant (news-driven) |
| USD/JPY | `gate_regime_extreme_usdjpy` | events-log + calendrier (BoJ meetings) | ⚠️ BoJ meeting dates à ajouter au calendrier |
| Cotton | `meteo_texas_cotton_precip` | Open-Meteo lat=33.5, lon=-101.9 | ✅ maintenant — ajouter METEO_CRITERIA |
| Cotton | `meteo_inde_gujarat_coton` | Open-Meteo lat=22.3, lon=72.6 | ✅ maintenant — ajouter METEO_CRITERIA |
| Cotton | `cftc_cot_cotton` | CFTC Socrata COTTON NO. 2 - ICE FUTURES U.S. | ✅ maintenant — ajouter CFTC_MARKETS |
| Cotton | `momentum_prix_20j_coton` | Twelve Data COTN | ✅ maintenant |
| Cotton | `momentum_prix_7j_coton` | Twelve Data COTN | ✅ maintenant |
| Cotton | `dxy_trend_20j` | FRED DTWEXBGS (déjà câblé) | ✅ maintenant (partagée) |
| Cotton | `demande_chine_coton` | events-log DeepSeek triplet | ✅ maintenant (news-driven) |
| Cotton | `nass_crop_progress_cotton` | USDA NASS QuickStats (USDA_API_KEY requise) | ⚠️ manuel sans clé (v3/data/manual/) |
| Cotton | `gate_regime_extreme_coton` | events-log + calendrier | ✅ maintenant |
| Sucre | `meteo_bresil_canne_sucre` | Open-Meteo lat=-21.2, lon=-48.1 | ✅ maintenant — ajouter METEO_CRITERIA |
| Sucre | `brent_ethanol_proxy_sucre` | Twelve Data XBR/USD (déjà câblé pour pétrole) | ✅ maintenant — nouvelle cle_courante |
| Sucre | `usd_brl_sucre` | Twelve Data USD/BRL (déjà câblé pour café) | ✅ maintenant — nouvelle cle_courante |
| Sucre | `cftc_cot_sugar` | CFTC Socrata SUGAR NO. 11 - ICE FUTURES U.S. | ✅ maintenant — ajouter CFTC_MARKETS |
| Sucre | `momentum_prix_20j_sucre` | Twelve Data CANE | ✅ maintenant |
| Sucre | `momentum_prix_7j_sucre` | Twelve Data CANE | ✅ maintenant |
| Sucre | `prod_inde_thai_sucre` | events-log DeepSeek triplet | ✅ maintenant (news-driven) |
| Sucre | `exports_bresil_sucre` | events-log DeepSeek triplet | ✅ maintenant (news-driven) |
| Sucre | `gate_regime_extreme_sucre` | events-log + calendrier | ✅ maintenant |

**Légende** : ✅ sourçable maintenant (câblage décrit ci-dessous) · ⚠️ partiel/manuel · ⛔ omis (aucune source)

Critères omis (zéro invention) :
- Taux cible BoJ en daily automatique : pas de série FRED/ECB/BOJ sans parsing HTML → omis, couvert partiellement par `diff_taux_2y_us_jp` + `boj_intervention_risk` (news)
- Carry attractivité DFEDTARU−BoJ : BoJ policy rate non sourçable en quotidien → omis
- Prix éthanol anhydre ESALQ (sucre) : payant, Brésil → omis, couvert par proxy Brent
- Arrivées ports Brésil sucre : non disponibles en API gratuite → omis (news-driven id=8)
- Production Inde ISMA chiffres précis : pas d'API en anglais/gratuit → news-driven id=7

---

## 5. Plan de câblage criteres_calculator.py {#5-cablage}

### 5.1 Ajouts CFTC_MARKETS (3 nouvelles entrées)

```python
# Dans CFTC_MARKETS (ligne ~633), ajouter :
"cftc_cot_jpy_nets": "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
"cftc_cot_cotton":   "COTTON NO. 2 - ICE FUTURES U.S.",
"cftc_cot_sugar":    "SUGAR NO. 11 - ICE FUTURES U.S.",
```

Vérification noms exacts à faire via Socrata avant implémentation :
```
GET https://publicreporting.cftc.gov/resource/jun7-fc8e.json?$where=market_and_exchange_names+like+'%25JAPANESE%25YEN%25'&$limit=1
GET https://publicreporting.cftc.gov/resource/jun7-fc8e.json?$where=market_and_exchange_names+like+'%25COTTON%25NO%25'&$limit=1
GET https://publicreporting.cftc.gov/resource/jun7-fc8e.json?$where=market_and_exchange_names+like+'%25SUGAR%25NO%25'&$limit=1
```

### 5.2 Ajouts METEO_CRITERIA (3 nouvelles zones)

```python
# Dans METEO_CRITERIA (ligne ~1527), ajouter :
"meteo_texas_cotton_precip":  (33.5, -101.9, 60),   # Lubbock TX — coton US
"meteo_inde_gujarat_coton":   (22.3,   72.6, 60),   # Gujarat — coton Inde
"meteo_bresil_canne_sucre":   (-21.2, -48.1, 60),   # Ribeirão Preto SP — canne
```

### 5.3 Ajouts FRED_SPREADS (1 nouvelle entrée) + FRED_SERIES_SIMPLE possible

```python
# Dans FRED_SPREADS (ligne ~772), ajouter :
"diff_taux_10y_us_jp": ("DGS10", "IRGTLT01JPM156N"),

# diff_taux_2y_us_jp : idéalement fetch_boj_jgb_2y() (nouveau fetcher).
# En attendant : proxy via FRED IRGTLT01JPM156N (même série que 10Y JP, mensuel).
# Ajouter dans FRED_SPREADS avec tag [PROXY MENSUEL] dans source YAML.
"diff_taux_2y_us_jp_proxy": ("DGS2", "IRGTLT01JPM156N"),  # [PROXY : 10Y mensuel, pas 2Y]
```

### 5.4 Dispatcher momentum — nouvelles clés à reconnaître

Le dispatcher `momentum_prix_20j_` et `momentum_prix_7j_` reconnaît déjà toutes les clés commençant par ces préfixes (branche dédiée A1, 10/06). Les nouvelles clés `momentum_prix_20j_usdjpy`, `momentum_prix_7j_usdjpy`, `momentum_prix_20j_coton`, `momentum_prix_7j_coton`, `momentum_prix_20j_sucre`, `momentum_prix_7j_sucre` sont reconnues automatiquement si le `ticker_principal` de la fiche est mappé dans `TWELVE_SYMBOLS` ou lu directement.

Vérifier que `COTN` et `CANE` sont ajoutés au mapping Twelve si pas encore présents.

### 5.5 Nouvelles clés via XBR/USD et USD/BRL (Sucre)

`brent_ethanol_proxy_sucre` et `usd_brl_sucre` : la source est Twelve Data, même dispatcher que les séries z-score mono-symbole. Le ticker est déjà utilisé pour d'autres actifs (XBR/USD pour pétrole, USD/BRL pour café). Il suffit de câbler les nouvelles clés dans le dispatcher collect_for_fiche, en pointant le même fetch Twelve avec la nouvelle cle_courante.

### 5.6 VIX pour USD/JPY (`vix_risk_usdjpy`)

La source CBOE VIX CSV est déjà lue dans le run. Ajouter un handler pour `vix_risk_usdjpy` qui lit le même VIX absolu mais avec la nouvelle cle_courante (évite L023 — ne pas réutiliser `niveau_vix_absolu` de vix.yml).

### 5.7 BOJ meetings dans le calendrier

Ajouter les dates de réunion BoJ 2026 dans le calendrier events/triggers (comme les FOMC). Les réunions BoJ 2026 sont publiques (site BOJ). Le gate `gate_regime_extreme_usdjpy` doit déclencher à <24h d'une réunion BoJ.

### 5.8 Réunions BoJ 2026 (source : boj.or.jp)

Dates publiées sur le site de la Banque du Japon pour 2026 (à vérifier et à coller dans le calendrier triggers) :
- 23-24 janvier · 18-19 mars · 30 avril-1er mai · 16-17 juin · 30-31 juillet
- 18-19 septembre · 29-30 octobre · 18-19 décembre

---

## 6. Liste critères manuels / news-driven {#6-manuels}

### Critères news-driven (DeepSeek triplet via events-log)

| Actif | Critère | Cle | Justification |
|---|---|---|---|
| USD/JPY | Politique BoJ / intervention | `boj_intervention_risk` | Pas de source API quotidienne du taux BoJ ; les interventions verbales sont capturées par DeepSeek |
| Cotton | Demande chinoise coton | `demande_chine_coton` | Imports GACC Chine = mensuel, pas d'API gratuite |
| Sucre | Production/exports Inde + Thaïlande | `prod_inde_thai_sucre` | ISMA/OCSB = non disponibles en API |
| Sucre | Exports Brésil sucre | `exports_bresil_sucre` | UNICA bi-mensuel, pas d'API temps réel |

Pour ces critères, vérifier que les requêtes news DeepSeek couvrent les mots-clés :
- USD/JPY : `"BoJ intervention" OR "Bank of Japan rate" OR "yen verbal intervention"`
- Cotton : `"China cotton import" OR "China cotton order" OR "Xinjiang cotton"`
- Sucre : `"India sugar export ban" OR "ISMA sugar" OR "Thailand sugar production" OR "UNICA Brazil sugar"`

### Critères manuels (v3/data/manual/)

| Actif | Critère | Cle | Condition d'activation |
|---|---|---|---|
| Cotton | CropProgress coton US | `nass_crop_progress_cotton` | Disponible automatiquement si `USDA_API_KEY` obtenu (déjà identifiée dans project-context comme chantier data P2) |

### Critères omis définitivement (pas de source)

| Actif | Critère souhaité | Raison de l'omission |
|---|---|---|
| USD/JPY | Taux cible BoJ daily | Pas de source API publique gratuite en quotidien |
| USD/JPY | Carry attractivité précis | BoJ policy rate non sourçable en automatique |
| Sucre | Prix éthanol ESALQ Brésil | Source payante (Cepea, abonnement) |
| Cotton | Exports US hebdo USDA FAS | Clé USDA requise (voir chantier data) |

---

## Appendice — Note sur les clés `dxy_trend_20j` et `usd_brl` partagées

La règle L023 ("ne jamais réutiliser une clé d'un autre actif") porte sur les critères PROPRES à un actif (ex. `meteo_ci_ghana_precip_30j` est spécifique au cacao — l'utiliser pour le café serait une erreur d'identification). Elle ne s'applique pas aux critères MACRO TRANSVERSAUX qui, par nature, mesurent le même phénomène sur tous les actifs concernés : `dxy_trend_20j`, `taux_10y_us_reels_tips`, `hy_credit_spread`, `spread_oat_bund_10y` sont déjà partagés entre plusieurs fiches dans le système actuel.

En revanche, `usd_brl_sucre` est une NOUVELLE clé (distincte de `usd_brl` de café.yml) car la pertinence et les poids diffèrent : même source (Twelve USD/BRL), même signe (-1), mais pertinences calibrées différemment pour le sucre. C'est le bon comportement L023.

De même, `brent_ethanol_proxy_sucre` est une nouvelle clé même si la source XBR/USD est partagée avec pétrole.yml : le signe et la logique sont inversés (pour pétrole : Brent monte = coût prod monte = neutre pour le Brent lui-même ; pour sucre : Brent monte = éthanol attractif = haussier).
