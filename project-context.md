# Contexte Projet — TradingApp v3

> Lu par tous les agents avant toute action.
> **Repo privé** (données financières personnelles). Dernière mise à jour : 2026-06-02.
> **Stade : V1 EN COURS** (mode shadow — rien émis publiquement). Reste avant V1 : (1) valider/calibrer le gate coverage sur données fraîches, (2) ~30 j shadow avec KPI > 70%, (3) backtest v2 concluant sur l'edge directionnel.
> **Source de vérité produit complète : vault Drive `Bourse/Bourse.md`** (ce fichier en est le résumé technique).

## En une phrase

Système qui produit **3 fois par jour (7h/12h/18h CET)** un **bulletin de positionnement directionnel** sur **12 actifs × 3 horizons (24h/7j/1m)** : chaque cellule tranche **LONG ou SHORT**. Thomas (trader humain) lit le bulletin et exécute manuellement des turbos chez Bourse Direct. Le système ne place jamais d'ordre.

## Objectif (NON NÉGOCIABLE)

⚠️ **On ne cherche PAS l'edge à la minute.** Un retard de 4h sur une news n'est pas grave.
But = **être certain de la TENDANCE par actif**, pour **suivre les vagues de hausse/baisse dans le bon sens, sans erreur de direction**. C'est du **trend-following directionnel**, pas du front-running de news. Tout raisonnement qui critique la *vitesse de capture* est hors-sujet.

## Architecture (30/05/2026)

- **GitHub Actions + git-as-storage** — scripts Python, **sans VPS, sans Cowork, sans Drive**. Coût infra 0 €.
- Workflow unique `cycle-decision` (cron 3×/jour) enchaîne : **ingest** (26 sources + extraction DeepSeek) → **critères** (Twelve Data/CFTC/EIA/Open-Meteo + triplets news) → **bulletin** (scoring + Briefing) → **mesure** (Journaliste). Commit git atomique.
- Tout le système est dans **`v3/`**. Données et historiques commités dans `v3/data/`.

## Méthode

- Score pondéré de critères par actif × horizon → LONG si >0, SHORT sinon (jamais neutre).
- 2 types de critères : **numériques** (prix, z-scores, COT, météo — cœur de la tendance) + **événementiels** (news, direction donnée par DeepSeek = contexte).
- **A/B** : score **±1** (référence) + score **pondéré** (matérialité×fiabilité) calculés en parallèle, mesurés ; activation du pondéré sur preuve.
- **Observabilité** : `decision-log` JSONL par cycle (tout tracé, historique git requêtable).

## KPI

Taux de réussite > **70 %** + Brier < 0,25 par cellule (30 dernières conclusions). Mesure A/B dans `v3/data/performance-ab.md`. Kill criterion : `v3/KILL-CRITERION.md`.

## État (01/06/2026)

- ✅ Système v3 en **mode shadow** (cron 3×/jour, rien émis). **619 tests** verts.
- ✅ Pipeline complet sur vraies données : **indices via ETF Twelve** (SPY/QQQ/FCHI/VIXY… — yfinance bloqué sur les runners CI), métaux/commodities Twelve, taux FRED, vol CBOE, news DeepSeek. 0 tie-break, ~117 critères/run.
- ✅ **Boucle prédiction→mesure fermée** : prix d'émission stampés, conclusions VRAI/FAUX (Journaliste), KPI Wilson/Brier en warm-up.
- ✅ Session 01/06 (cf. Historique) : synthèse directionnelle 2 niveaux + contexte-prix, rate-limiter Twelve (attend, RPM=55), PROBA_SCALE=15, **plan horizon** (pertinence recalibrée + cap anti-inversion news α=0.8 + drapeau 📰 si news>50%).
- ⚠️ **GitHub `schedule` retardé de 1-3h** (comportement GitHub normal, PAS un bug — 6 runs schedule prouvés les 30-31/05). Parade : redondance ×3 par créneau (cron `:12/:27/:42`) + garde-fou anti-doublon (skip si snapshot <2h). Fallback fiables : push `v3/RUN-CYCLE.txt` ou `workflow_dispatch`. **Ne plus churner le cron** (re-registration fait sauter l'occurrence suivante). **→ RÉSOLU 02/06 : pinger sur le VPS Anya (`v3/ops/vps-trigger/`) déclenche `workflow_dispatch` 3×/jour à l'heure pile ; schedule GitHub gardé en fallback.**
- ✅ Session 02/06 (cf. Historique) : **gate S5 suffisance de données** (couverture pondérée + paliers `⚠️ conf. faible`/`🚫 insuffisant`, abstention override jamais-neutre), **6 lots de gates anti-erreur de jugement** (intégrité quant z-score/std0/spike + réconciliation Σ + UTC, signe DeepSeek C1, intégrité mesure C5, détecteurs directionnels flag-only, sanity news déjà-coté/démenti, publication « cellules à surveiller » + flip/continuation), **source_monitor** (santé flux/cycle + 4 flux muets réparés), **requêtes news 10/10** (concertation 3 experts ×3 rounds), backtest quant v1 (NO-GO partiel sur price-only), bilan news, heure dans titre bulletin.
- ✅ **RÉSOLU (priorité 1) — 02/06** : la couverture basse (5 actifs `INSUFFISANT` sur run frais 12h29, 42% du bulletin) n'était **pas** un seuil mal calibré ni un trou d'archi, mais une **panne FRED 429** (rate-limit → `DFII10`/TIPS + spreads morts, prouvé dans les logs du run). `COVERAGE_MIN=0.40` reste juste. Corrigé : retry/backoff + throttle FRED (commit `a03cd98`, +6 tests). Diagnostic via audit trio du bulletin (AJUSTER 6/10 → `v3/audit/coherence-bulletin-2026-06-02.md`).
- ⬜ **À venir** : **Lot 4b gates** (actions : plafond mono-news + hystérésis, à calibrer sur fréquence mesurée des détecteurs 4a) → activer garde look-ahead (propager date du tick) → backtest quant **v2** (COT+FRED+7j/1m) → durcir mesure (multiple-testing) → ~30 j shadow → **Phase 2 news** → émission post-shadow.

## Garde-fous

- **Zéro invention** (source absente → critère n/a, poids 0). **Pas de modif silencieuse** des poids/prompts (changelog + validation Thomas). **Mode shadow obligatoire** avant toute émission. **Échec visible**.

## Repères repo

- `v3/scripts/` : le système. `v3/config/` : fiches actifs (YAML) + triggers + weighting. `v3/data/` : sorties (bulletins, events-log, decision-log, performance). `v3/audit/` : audits. `v3/docs/reco/` : décisions d'architecture.
- `legacy/` : ancienne app (bot « 1 signal turbo/jour ») — **archivée, ne pas utiliser**.
- `.claude/`, `CLAUDE.md`, `update.sh` : framework Gradient Agents (séparé du projet trading).

## Historique des interventions agents

| Date | Agent | Livrable | Décisions clés |
|---|---|---|---|
| 2026-06-01 | orchestration + @fullstack | Correctifs pipeline run quotidien | Routing IA-first réparé, prix d'émission, symboles Twelve validés. Synthèse directionnelle 2 niveaux + contexte-prix. **Indices via ETF Twelve** (yfinance bloqué CI). **Rate-limiter Twelve** : attend au lieu de rejeter, `TWELVE_RPM=55` (plan Grow). PROBA_SCALE 10→15, propagation reliability, garde chevauchement 7j/1m. |
| 2026-06-01 | 3 experts (Analyst / News Trader / Spéculateur) | `v3/audit/chaine-*.md` + `coherence-3-experts.md` | Audit des runs dans l'ordre d'édition. Cohérence : 2 faux positifs écartés sur preuve (signe géopol déjà câblé `ia_synthese` ; contamination 2025 filtrée par cutoff lookback). **Trio = panel d'audit officiel** (`v3/audit/README.md`). |
| 2026-06-01 | @fullstack + 3 experts (validé Thomas) | **Plan horizon** (`revue-plan-horizon-*.md`) | Constat : DeepSeek = 1 direction/actif **horizon-agnostique** ; l'horizon est géré par `pertinence` par critère. **PAS de decay_factor global** (rejeté 3/3 : doublon + casserait l'OPEC structurel). Retenu : recalibrer pertinence (or/petrole/vix, OPEC 7j-1m préservé) + cap anti-inversion α=0.8 (override si high+confirmed) + `ratio_news`/drapeau 📰. Preuve : Or 24h & VIX 1m → SHORT, Pétrole/S&P inchangés. |
| 2026-06-01 | infrastructure (orch) | Workflow `cycle-decision` | Diagnostic : `schedule` GitHub retardé 1-3h (pas une panne). Redondance ×3 + garde-fou anti-doublon. Read/write permissions activées. |
| 2026-06-01 | @data-analyst | `v3/audit/spec-phase2-news-analyst.md` | Spec Phase 2 News lot cœur : `event_id` (SHA-256/12 + dédup floue Levenshtein ≤15 %), `event_date` (fraîcheur RSS pubDate vs ingestion), `nature` (DeepSeek — 5 valeurs fermées, verbal/deja_cote/non_tradable exclus du scoring), gate fraîcheur FRESHNESS_OVERRIDE_DAYS=3j sur override high+confirmed, STALE_THRESHOLD=30j. Zéro double-amortissement avec pertinence. Shadow direct : 7 métriques M1-M7 dans decision-log (champs `p2_*`). PROMPT_VERSION bumper v2.1→v2.2. |
| 2026-06-01 | @data-analyst | `v3/audit/chaine-analyst.md` (écrasé — run 2053) | **Validation méthodo Phase 2.** T1/T2=0 = angle mort instrumentation (pas anomalie) — proposé `p2_shadow_contrib_exclu` + `p2_shadow_flip_potential` pour rendre T1 mesurable (A1-P0). Dédup CAC40/GOLD >30% = vrais quasi-doublons, garde-fou légitime. 399 reposts / 397 stale plausibles — EIA source de fond à exclure du compteur taux_stale (A4-P1). Zéro double-amortissement si coef_nature binaire (spec) — à vérifier si flottant en implémentation (A3-P0). T1/T2 significatifs à 30 runs (J+10). **Verdict : GO 7,5/10.** |
| 2026-06-01 | @data-analyst | `v3/audit/audit-reel-et-backtest-scope.md` | **Audit honnête données réelles + protocole backtest.** N_eff=0/12 cellules → aucune affirmation statistique possible. Wilson N=1 : borne basse 20.6% (seuil opérationnel 50%). Puissance stat à N=1 : ~5% = pile ou face. Biais LONG 61% : borderline (p~0.05 à N_eff_ind≈60) — régime ou structurel indiscernable sans 30 runs. Seuils à revoir : VIX 5%→3%, Cacao 1.5%→1.0%. Backtest quant-only protocol défini : 4 ans historique, non-chevauchant (24h quotidien/7j hebdo/1m mensuel), walk-forward IS:2021-24 / OOS:2025-26, critères GO : directional accuracy OOS≥60%, Wilson_low≥55%, p-value bootstrap<0.05. Effort : 5-7j dev. |
| 2026-06-02 | @data-analyst | `v3/audit/gates-analyst.md` | **Concertation round 1 — grille complète des gates méthodologiques.** 46 gates définis sur S1-S9 (S5 exclu). 12 P0 identifiés, dont Top 5 critiques : borne z-score (S4-G4), division par zéro écart-type (S4-G5), exclusion nature Phase 2 du scoring (S2-G5), zéro look-ahead Journaliste (S8-G2/G3), réconciliation somme contributions (S6-G1). 12 gates automatisables en CI avant sortie shadow. Gates revue humaine : révision seuils S8-G4, chevauchement S8-G7, enum nature Phase 2 — requis avant émission réelle. |
| 2026-06-02 | orchestration (édition directe) | Seuils mesure + heure bulletin | Resserre seuils 24h **VIX 5→3%**, **Cacao 1.5→1.0%** (audit réel : réduit les non-conclusives, AVANT accumulation pour éviter biais rétrospectif). Heure du run dans le titre du bulletin (visible HTML). *Pourquoi édition directe : config 1 ligne + cosmétique, hors périmètre agent (commandement 4 exceptions).* |
| 2026-06-02 | @fullstack | `v3/backtest/` (backtest quant v1) | **Backtest historique no-look-ahead** (yfinance, walk-forward IS 2022-24/OOS 2025-26, non-chevauchant). Verdict v1 **NO-GO** : POOLED OOS **50.8%** = pile ou face sur 4 actifs × 24h **price-only**. PARTIEL : COT/FRED absents (~50% du poids) → v2 obligatoire pour conclure. Bug trouvé : proxy ETF TIP inversé. *Alternative écartée : POC limité — Thomas a choisi le vrai backtest.* |
| 2026-06-02 | @fullstack | Bilan news + `source_monitor` | **Bilan des news** (calls portés news VRAI/FAUX dans le bulletin — juger le jugement DeepSeek). **source_monitor** : santé par flux/cycle (appelé/OK/échec/muet + reçus vs gardés + raison) → `source-health.md` + bloc bulletin. Audit 4 flux muets : gnews_cac40 (whitelist FR ajoutée), gnews_wheat (query élargie), investing_stocks (doublon→news_287), mining_com 403 (visible). |
| 2026-06-02 | 3 experts (NT/Analyst/Spé) ×3 rounds | `v3/audit/audit-requetes-news-*.md` | **Optimisation requêtes news jusqu'à 10/10** (itération demandée Thomas). Comble Nasdaq (Nvidia/IA/semi) + VIX (volatilité + causes amont). Sépare Fed/BCE, S&P earnings, retire DAX, dégroupe Or/Argent, +CB-gold/solaire/EUDR/WASDE/café-gel/blé-GASC/CAC-SBF120. 14 requêtes, 22 flux. **Plafond news ~9,5-10** (reste = pipeline data : CFTC/CBOE/GASC). |
| 2026-06-02 | @fullstack | **Gate S5 suffisance de données** | Couverture pondérée Σpoids(critères avec donnée)/Σpoids total. Paliers : ≥65% normale · 40-65%/périmé `⚠️ conf. faible` · <40% `🚫 insuffisant` (override jamais-neutre, exclu mesure VRAI/FAUX + biais). Sécurité demandée Thomas (plus de note confiante sur 2 critères/9). *Pourquoi code et pas DeepSeek : couverture = calcul déterministe ; DeepSeek réservé au jugement news.* |
| 2026-06-02 | 3 experts ×2 rounds + orchestration | `v3/audit/gates-FINAL.md` (concertation) | **Liste finale convergée des gates** (débat contradictoire R1+R2). 9 gates consensus + roadmap 6 lots. 3 frictions tranchées : C3 = détecte/drapeaute (cap α arbitre, pas trend-first dur) ; C8 scindé C8a P0/C8b P1 ; C4 = plafond mono-news + materiality×reliability (pas de quorum bloquant). |
| 2026-06-02 | @fullstack (×6 lots) | **6 lots de gates** (cf. État) | Lot 1 fondation déterministe (z-score borné/std0/spike→n/a + réconciliation Σ + UTC) · Lot 2 C1 signe DeepSeek (neutralise news au sens inversé) · Lot 3 C5 intégrité mesure (verrou prix/échéance/look-ahead) · Lot 4a détecteurs flag-only (↯⇄⇆) · Lot 5 sanity news (⌛⊘) · Lot 6 publication (« cellules à surveiller » + flip/continuation). 478→619 tests. **Lot 4b (actions) différé** : calibrer sur fréquence mesurée des détecteurs (choix Thomas « mesurer avant d'agir »). |
| 2026-06-02 | orchestration (édition directe) | **Pinger VPS — fiabilisation du cron** (`v3/ops/vps-trigger/`) | Le `schedule` GitHub abandonne des créneaux (matins 01-02/06 sautés, prouvé par l'absence de runs `schedule`). Cron local sur le VPS Anya → `workflow_dispatch` (ref=main) 3×/jour via `/etc/cron.d/tradingapp` (run root, survit aux redéploiements Anya). Compute/stockage restent sur GitHub Actions (archi v3 « sans VPS » préservée — le VPS n'est qu'une horloge). Validé prod : runs #23 (MCP) + #25 (VPS) HTTP 204 → success. Schedule natif gardé en fallback. **Leçons** : curl mono-ligne (continuations `\` perdues au paste SSH) ; un PAT collé en chat = compromis → révoqué + régénéré. |
| 2026-06-02 | orchestration + 3 experts + @fullstack | **Audit trio du bulletin + correctif FRED-429 + fix cron TZ** | **Trio** (Analyst/News Trader/Spéculateur) sur bulletin 12h29 : **AJUSTER 6/10** unanime (`v3/audit/bulletin-*.md` + `coherence-bulletin-2026-06-02.md`). Noyau sain : Or SHORT, Pétrole/Argent LONG. **Audit des recos avant d'appliquer** : le « 42% INSUFFISANT » = **FRED 429** (rate-limit → `DFII10`/TIPS morts), PAS un seuil ni un trou d'archi → **corrigé** (retry/backoff + throttle FRED, commit `a03cd98`, +6 tests). Coin-flips Nasdaq/VIX 24h : **gardés flag-only** (décision Thomas — Lot 4b différé maintenu). Cron : `CRON_TZ` inopérant sur Vixie/Ubuntu (midi 02/06 raté) → bascule **cron horaire `0 * * * *` + garde heure-Paris dans le script** (robuste DST). **FRED vérifié en prod** (run #28) : `fred_dead:DFII10` disparu, TIPS revient. **Généralisé** : helper partagé `http_retry.py` (429/5xx + `Retry-After` + throttle par bucket) → GNews/NewsAPI + UA Chrome pour le 403 mining_com (commit `e28f40f`, +16 tests, 632 verts). **Durcissement HTTP complet** (commit `6c1fe8e`) : `http_get_json` CFTC/EIA/Open-Meteo passé sous retry (wrapper préservant le contrat) + `fred_spread_thin` DGS10-DE résolu (forward-fill LOCF de la série DE mensuelle sur la grille US quotidienne). **Toute la chaîne HTTP du pipeline est désormais résiliente au 429/5xx** — prêt pour tests complets. |
| 2026-06-02 | orchestration + @fullstack (×4) | **Améliorations bulletin : lisibilité + capteurs** | **Lisibilité** (`c00d702`) : synthèse des décisions EN HAUT, cellules allégées (`[pond]` affiché seulement si ≠ primaire, pondéré en tête sur cellules 📰), légende compacte (symboles présents only), actifs 🚫 regroupés — présentation only, mesure/conclusions inchangées. **Capteurs** : TIPS partagé S&P (`b5bba34`, +16% couverture pondérée) ; breadth S&P/Nasdaq câblé via **proxy EW/CW** RSP/SPY + QQQE/QQQ (`1637241`, zscore `signe:+1`, CAC laissé n/a faute d'ETF EW gratuit) ; Caixin laissé **n/a + news** (choix Thomas) ; **FedWatch : aucune source ZQ gratuite fiable** (Twelve/FRED/yfinance KO, CME 25$/mo) → **n/a, décision Thomas en attente**. Tests 642 verts. ⚠️ Calibration proxy breadth (`signe:+1`, hypothèse EW/CW↑=haussier) à valider dans la boucle prédiction→mesure en shadow. |

---

## Mémo de reprise — dernière session

- **Date/heure de clôture** : 2026-06-02
- **Numéro de session** : **Session 1** (1er mémo formel ; projet actif depuis 2026-05-01, ~6 journées de travail antérieures non numérotées — ce numéro devient la source de vérité pour le nommage des branches).
- **Résumé** : Session « fiabilisation & garde-fous ». Livré : gate de **suffisance de données** (S5), **6 lots de gates anti-erreur de jugement** (478→619 tests), **source_monitor** (santé des flux + 4 flux muets réparés), **requêtes news optimisées 10/10** (concertation 3 experts ×3 rounds), **backtest quant v1** (verdict honnête NO-GO partiel : 50.8% OOS price-only), bilan des news, heure dans le titre du bulletin. Décisions clés : « **mesurer avant d'agir** » (Lot 4b différé pour calibrer les seuils sur données réelles) ; gates **flag-only en shadow** (détecter+mesurer sans changer les conclusions, prouvé par tests verrous) ; arbitrage gates par **concertation contradictoire** des 3 experts.
- **Travaux en cours / différés** :
  - **Lot 4b gates** (actions : plafond mono-news + materiality×reliability + hystérésis anti-flip) — spec figée dans `gates-FINAL.md`, attend quelques cycles de données des détecteurs 4a pour calibrer les seuils.
  - **Garde look-ahead (Lot 3)** armé mais latent — le pipeline ne propage pas encore la date du tick prix jusqu'à `measure_cell`. Petit câblage à faire.
  - **Backtest quant v2** : câbler COT + FRED + horizons 7j/1m (le v1 price-only est NO-GO partiel ; v2 = seul moyen de conclure sur l'edge).
  - **P2** : distribution dégénérée des scores + correction multiple-testing (avant émission réelle).
- **Prochaines actions (priorisées)** :
  1. **[P1] Vérifier la calibration coverage sur le run frais de 7h** (orchestration + @data-analyst) — sur données vieilles, les 12 actifs sont en `INSUFFISANT` (couverture 0-35%). Si le run frais confirme une couverture basse, le gate S5 rendrait le système muet → recalibrer `COVERAGE_MIN` ou vérifier que le pipeline remplit assez de critères. **Bloquant pour l'utilité du système.** Lancer `python3 v3/scripts/analyse_complete.py`.
  2. **[P1] Lot 4b gates** (@fullstack) — une fois 3-5 cycles de détecteurs 4a accumulés, calibrer plafond mono-news + hystérésis sur la fréquence réelle des divergences/flips.
  3. **[P2] Backtest quant v2** (@fullstack) — COT+FRED+7j/1m, pour trancher sur l'edge directionnel (~7 j).
- **Blockers** : aucune question utilisateur en attente. La calibration coverage (#1) est une **vérification**, pas un blocage ; le Lot 4b s'auto-débloque avec l'accumulation des cycles.
- **Branche prochaine session** : `claude/tradingapp-s2-coverage-calib-[suffix]`
- **Commande de reprise** :
  > « Reprise TradingApp session 2. Lis project-context.md (Mémo de reprise) + docs/lessons-learned.md. Priorité 1 : lance `python3 v3/scripts/analyse_complete.py` sur le run frais et vérifie la distribution de couverture (gate S5) — si la majorité des actifs sont en INSUFFISANT sur données FRAÎCHES, diagnostique (seuil COVERAGE_MIN trop agressif vs pipeline qui ne remplit pas assez de critères) et propose une correction. Puis enchaîne sur le Lot 4b des gates (gates-FINAL.md) une fois assez de cycles de détecteurs 4a accumulés. »
