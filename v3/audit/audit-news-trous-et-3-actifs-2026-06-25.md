# Audit news : trous récents + câblage des 3 nouveaux actifs (USD/JPY, Coton, Sucre)

> Audit sur pièces. Période inspectée : 20→25/06/2026. Sources : `source-health.md` (+ historique git 5 cycles), `criteres-health.md`, `events-log.md`, bulletins 23/24/25-06.
> Garde-fous : zéro invention, échec visible, WIN RATE ONLY. **Aucune modif code ici** (audit seul).

---

## VOLET A — Les TROUS des news récentes

### Vue d'ensemble (santé globale = BONNE)

| Cycle | Flux | OK | Échec | Muets | Reçus → gardés |
|---|---:|---:|---:|---:|---|
| 25/06 05:16 | 34 | 34 | **0** | 3 | 1770 → 704 |
| 24/06 05:17 | 34 | 34 | **0** | 2 | 1803 → 685 |
| 23/06 06:34 | 34 | 34 | **0** | 4 | 1785 → 629 |
| 23/06 05:16 | 34 | 34 | **0** | 2 | 1784 → 707 |
| 22/06 14:12 | 34 | 34 | **0** | 3 | 1815 → 670 |

**Constat : aucun flux en échec, aucun 403/429, aucun skip clé API sur les 5 derniers cycles.** Pas de panne de flux. Les trous sont **structurels** (mapping/keep-rate par actif), pas des pannes réseau. Bonne nouvelle : pas d'urgence P0 « flux mort ».

### Trous datés, par criticité

| # | Trou (FAIT daté) | Criticité | Cause probable | Reco |
|---|---|---|---|---|
| T1 | **CAC 40 = « aucune actualité »** au bulletin **25/06** (et VIX **23/06**), alors que `gnews_cac40` ingère **73→84 items/cycle** et n'en garde que **1→3**. Sur TOUT `events-log` : **42 events CAC40** vs 1441 Brent / 505 S&P. | **P0** | Incohérence de clé : fiche = `cac40.yml` → clé `cac40` (via `f.stem`), mais tout le pipeline news/triggers utilise **`cac_40`** (`IA_ASSET_TO_ACTIF["CAC40"]="cac_40"`, `ACTIF_KEYWORDS["cac_40"]`, `triggers-and-windows.yml: cac_40`). Les events routés IA→`cac_40` ne retombent pas sur la fiche `cac40` pour la section « News par actif ». `[HYPOTHÈSE À VÉRIFIER en code : réconciliation absente]` | **Vérifier le mapping `cac_40` ↔ fiche `cac40`** (aligner sur une seule clé). Si confirmé : 1 ligne. C'est le trou le plus impactant (un actif jugé sans son contexte news). |
| T2 | **VIX = 7 events taggés VIX** sur tout le log, et « aucune actualité » au bulletin **23/06**, alors que `gnews_vix` garde **82→97 items/cycle** (le 2e meilleur keep). | **P1** | Le flux `gnews_vix` est volumineux mais ses items sont routés vers d'AUTRES actifs (Brent/S&P/géopol) par l'IA, rarement taggés `VIX` lui-même (le VIX est un effet, pas un sujet). Keep-rate flux OK, mais **tag actif VIX rare**. | Normal en partie (le VIX se lit dans le risk-off des autres actifs). Surveiller : si « aucune actualité VIX » devient récurrent au bulletin, ajouter un routage IA `→VIX` sur les news de stress systémique. Pas un fix urgent. |
| T3 | **Coton/Sucre/USD-JPY ABSENTS** de tout le pipeline news (0 flux, 0 keyword, 0 mapping). | **P1** (devient P0 à l'ajout) | Actifs non encore câblés (objet du Volet B). | Voir Volet B. |
| T4 | **Cuivre : keep 1→2 / 75-81 reçus** sur `gnews_copper` (5 cycles) ; 96 events COPPER au total (faible). **Blé : keep 3→5 / 56-59**, 70 events WHEAT. | **P2** | Keep-rate bas mais STABLE et NON nul : flux vivant, dédup + filtre finance agressifs sur des sujets peu couverts. Pas une panne. | Surveiller, pas corriger. Élargir les requêtes `gnews_copper`/`gnews_wheat` seulement si le bulletin affiche « aucune actualité » répété (pas le cas 23-25/06). |
| T5 | **Volume ingestion 22/06 = 831 events/jour** vs 97-360 les autres jours (pic anormal). | **P2** (informatif) | Pic géopolitique Iran/Hormuz (le 22/06 concentre les news Brent). **Normal**, pas un trou : c'est l'inverse (sur-ingestion sur un actif). Le week-end 20/06 (148) est un creux **normal**. | RAS. Sert de repère : un jour ouvré < ~100 events hors week-end serait, lui, suspect. |
| T6 | **3 flux muets récurrents** : `eia_press_releases`, `fed_monetary`, `investing_stocks` (0 gardé après filtre). | **P2** (normal) | Dédup + blacklist + filtre finance (doublons de `fed_press_all` / `eia_today_in_energy` / `investing_news`). **Comportement attendu**, pas une panne. | Aucune action. Ne PAS « réparer » (ce serait réintroduire des doublons). |

### Distinction normal vs vrai trou (synthèse)

- **VRAI trou (à corriger)** : **T1 CAC 40** (mismatch de clé `cac_40`/`cac40` → actif jugé sans news). Seul P0.
- **À surveiller** : T2 VIX, T4 cuivre/blé (keep bas mais stable, non nul).
- **NORMAL (ne rien faire)** : T5 (pic Iran / creux week-end), T6 (muets par dédup), keep-rate bas sur sujets niche.

---

## VOLET B — News à AJOUTER pour USD/JPY, Coton, Sucre

> Méthode : lecture des configs EXISTANTES (`config.py` RSS_FEEDS/EARLY_SIGNAL_FEEDS/STRUCTURED_QUERIES, `triggers_classifier.py` ACTIF_KEYWORDS/IA_ASSET_TO_ACTIF, `calendrier-eco.yml`). On distingue « déjà couvrant » de « à ajouter ».

### Pré-requis commun aux 3 (sinon news perdues)

1. Ajouter chaque actif à **`ACTIF_KEYWORDS`** (`triggers_classifier.py` ~L80) : id IA + tickers + keywords.
2. Ajouter à **`IA_ASSET_TO_ACTIF`** (~L130) : `"USDJPY":"usdjpy"`, `"SUGAR":"sucre"`, `"COTTON":"coton"`.
3. Créer la **fiche** `v3/config/fiches/{usdjpy,sucre,coton}.yml` **avec un nom de fichier = clé interne identique** (éviter le piège T1 `cac_40`/`cac40` : prendre `usdjpy`/`sucre`/`coton` partout, sans variante).
4. Ajouter les triggers/critères dans **`triggers-and-windows.yml`** sous la même clé.
5. Étendre le **prompt extracteur** (`extractor.py`) pour que l'IA produise les ids `USDJPY/SUGAR/COTTON`.

### B.1 — USD/JPY

**Déjà couvrant (existant) :**
- `investing_forex` (RSS, news_1.rss) — forex générique, **garde 5/10 items/cycle**, vivant.
- `boj_news` (RSS officiel BoJ) — **garde 4/48**, source primaire de politique monétaire japonaise. **Déjà ingéré, pas encore routé vers un actif JPY.**
- `gnews` / `newsapi` (structurés) — captent « dollar index », « Fed ECB divergence » mais **pas le yen spécifiquement**.

**À AJOUTER :**
- **Keywords** (ACTIF_KEYWORDS `usdjpy`) : tickers `{"USDJPY=X","JPY=X","USDJPY"}` ; mots `{"usd/jpy","usdjpy","usd jpy","yen","japanese yen","boj","bank of japan"}`. _(`USDJPY=X` est déjà servi par Twelve — vu dans criteres-health provenance : `USDJPY=X` listé twelve_native.)_
- **Triggers** : `boj_policy` (BoJ, taux, YCC, normalisation), `intervention_mof` (MOF/Ministry of Finance, « intervention », « yen check rate »), `yen_carry` (« carry trade », « unwind »), `differentiel_taux_us_jp` (Fed vs BoJ).
- **Flux dédié recommandé** : `gnews_usdjpy` (Google News RSS), requête : `yen OR "USD/JPY" OR "Bank of Japan" OR "BoJ" OR "yen intervention" OR "Ministry of Finance Japan" OR "carry trade"`. Aligné sur les flux niche existants (gnews_copper/cocoa).
- **Catalyseurs calendrier** (`calendrier-eco.yml`) : **réunions BoJ** (8/an, type `BOJ`, `precision: regle` — dates 2026 non certaines → règle), actifs `[usdjpy]`. Optionnel : CPI Japon. (La Fed FOMC est déjà câblée et impacte USD/JPY → ajouter `usdjpy` à la liste `actifs` du FOMC existant.)

### B.2 — Sucre

**Déjà couvrant (existant) :**
- `investing_commod` (news_11.rss) — **garde 6/10**, commodités générales (déjà cité sur cacao/blé dans les bulletins). Couvre partiellement le sucre.
- `investing_commodities` / `investing_metals` — commodités, peu de sucre.
- `gnews` / `newsapi` — aucune requête sucre actuellement.

**À AJOUTER :**
- **Keywords** (`sucre`) : tickers `{"SB=F","SUGAR"}` ; mots `{"sugar","sucre","ethanol","unica","centre-south brazil"}`.
- **Triggers** : `meteo_bresil_canne` (sécheresse/pluies Centre-Sud Brésil), `mix_ethanol_sucre` (arbitrage canne→éthanol vs sucre, prix essence Brésil), `production_inde` (mousson, export ban/quota Inde), `broyages_unica` (rapports bimensuels UNICA Centre-Sud).
- **Flux dédié recommandé** : `gnews_sugar`, requête : `sugar prices OR "raw sugar" OR Brazil ethanol OR UNICA OR India sugar export OR "Centre-South Brazil" OR ICE sugar`.
- **Requête structurée** : ajouter à `STRUCTURED_QUERIES` : `sugar prices OR Brazil ethanol OR UNICA crush OR India sugar OR Thailand sugar`.
- **Catalyseurs calendrier** : **rapports UNICA** (broyages Centre-Sud, ~bimensuels — `precision: regle`), **WASDE sucre** (le WASDE USDA existant couvre déjà l'agri → ajouter `sucre` aux `actifs` du bloc WASDE).

### B.3 — Coton

**Déjà couvrant (existant) :**
- `investing_commod` / `investing_commodities` — commodités générales, sporadique sur coton.
- `gnews_wheat` capte « soft commodities » + WASDE/USDA — **partiellement** couvrant (USDA est commun coton/blé), mais pas ciblé coton.
- `gnews` / `newsapi` — aucune requête coton.

**À AJOUTER :**
- **Keywords** (`coton`) : tickers `{"CT=F","COTTON"}` ; mots `{"cotton","coton","usda cotton","cotlook"}`.
- **Triggers** : `meteo_texas` (sécheresse/excès High Plains Texas — symétrique `zscore_abs` comme cacao), `production_inde_chine` (Inde + Chine = 1ers consommateurs/producteurs), `wasde_coton` (estimations USDA surface/rendement/stocks), `demande_textile_chine` (filature/imports Chine).
- **Flux dédié recommandé** : `gnews_cotton`, requête : `cotton prices OR USDA cotton OR Texas cotton drought OR India cotton OR China cotton imports OR ICE cotton OR Cotlook`.
- **Requête structurée** : ajouter `cotton prices OR USDA cotton OR Texas drought OR India cotton OR China textile demand`.
- **Catalyseurs calendrier** : **WASDE** (déjà mensuel → ajouter `coton` aux `actifs`), **USDA Crop Progress / Cotton Ginnings** (`precision: regle`), **COT/CFTC** (le bloc COT existant → ajouter `coton`/`sucre` aux `actifs`).

---

## Reco priorisée (P0/P1/P2)

**P0 (vrai trou, corriger en premier) :**
- **T1** — Réconcilier la clé `cac_40` (pipeline news/triggers) ↔ fiche `cac40` (`f.stem`). Vérifier en code d'abord ; si mismatch confirmé, aligner sur une seule clé. Sans ça, le CAC 40 est jugé sans son contexte news (« aucune actualité » alors que 73-84 items/cycle entrent).
- **Pré-requis B** (1-5 ci-dessus) — au moment d'ajouter USD/JPY / Coton / Sucre, câbler les 5 points dans le bon ordre ET nommer fiche = clé interne (ne PAS reproduire le piège T1).

**P1 :**
- **B.1/B.2/B.3** — flux dédiés `gnews_usdjpy` / `gnews_sugar` / `gnews_cotton` + keywords + triggers + entrées calendrier (BoJ, UNICA, WASDE sucre/coton). Réutiliser `boj_news` (déjà ingéré) pour USD/JPY.
- **T2 VIX** — surveiller la récurrence de « aucune actualité VIX » ; routage IA→VIX sur stress systémique seulement si ça se répète.

**P2 (surveiller, ne rien forcer) :**
- **T4** cuivre/blé (keep bas mais stable) — élargir requêtes seulement si « aucune actualité » répété.
- **T6** muets eia_press/fed_monetary/investing_stocks — NE PAS toucher (dédup volontaire).

---

## Garde-fous respectés

- Zéro invention : tous les chiffres viennent de `source-health.md` (+ git), `criteres-health.md`, `events-log.md`, bulletins 23-25/06. Aucune date `precision: date` non certaine proposée (BoJ/UNICA/WASDE → `regle`).
- Échec visible : T1 présenté comme observé + cause `[HYPOTHÈSE À VÉRIFIER en code]`, pas affirmé comme bug certain.
- WIN RATE ONLY : aucune métrique de gain.
- **Aucune modif code, aucun commit.**
