# CHANGELOG — TradingApp v3

> Historique des sessions de travail (le plus récent en haut). Détail technique : `git log` + `v3/audit/`.

## 2026-06-06 (Session 4) — Fériés de marché AUTO via lib `holidays` (NYSE XNYS + Euronext XECB) — fin de la maintenance annuelle manuelle

**Demande fondateur** : que la mise à jour des jours fériés de marché soit **automatique chaque année, zéro maintenance manuelle**. Avant : `MARKET_HOLIDAYS` était une liste statique « à étendre chaque année » → dette de maintenance + risque d'oubli (un férié non recopié = run sur prix figés).

### Correctif (@infrastructure)
- **`v3/scripts/journaliste.py`** — `_is_market_holiday` refondu : **source PRIMAIRE = lib `holidays`**, calendrier **XNYS** (NYSE) **∪ XECB** (TARGET/ECB = exactement les fermetures Euronext : 1 Jan, Vendredi saint, Lundi de Pâques, 1 Mai, 25 Déc, 26 Déc), **calculé pour l'année de la date testée** → valable 2026/2027/2028… **automatiquement**, plus de liste à étendre. `_is_market_holiday(d) = d ∈ (XNYS(d.year) ∪ XECB(d.year)) ∪ MARKET_HOLIDAYS`.
- **`MARKET_HOLIDAYS` (statique)** → devient (1) **fallback déterministe** anti-crash si la lib est absente/échoue, (2) **filet d'override manuel** pour fermetures ad-hoc hors lib (deuil national, etc.). Commentaire « à étendre chaque année » remplacé par « la lib couvre l'auto ; ce set = overrides exceptionnels + fallback ». Couverture 2026 conservée pour le fallback.
- **ROBUSTESSE (garde-fou critique)** : tout échec (ImportError, code financier absent de la version, API différente) → `_is_market_holiday` retombe **proprement** sur le socle statique, **JAMAIS de crash** (un crash dans la garde = NO-OP permanent du pipeline). Pattern try/except import préservé et durci.
- **`.github/workflows/cycle.yml`** — étape Guard : `pip install -q holidays || echo …` ajouté **juste avant** l'appel `python3 -c is_trading_day` (la garde tourne AVANT le setup des deps). Si ce pip échoue (réseau), `|| true` n'interrompt rien → fallback statique. Table de vérité + commentaires mis à jour (source des fériés devient auto ; logique conceptuelle inchangée). YAML revalidé (`yaml.safe_load`).
- **`v3/requirements.txt`** : `holidays==0.98` ajouté (pure-python) pour le pipeline de mesure.
- **Tests `v3/tests/test_is_trading_day.py`** (7 → **12 cas verts**) : **PREUVE de l'automatisme** — fériés **2027** (Noël 24/12, Thanksgiving 25/11, Lundi de Pâques 29/03) et **2028** (Vendredi saint 14/04, Thanksgiving 23/11, 1 Mai) calculés par la lib, **absents du statique** → `is_trading_day=False` ; **cohérence croisée** lib (XNYS ∪ XECB) vs statique **2026** (identiques, zéro divergence) ; **fallback ImportError** via monkeypatch → pas de crash, jour ouvré non bloqué. Simulation du chemin CI exact (`python3 -c`) : Noël 2026/2027, Thanksgiving 2027, Vendredi saint 2028 → NO-OP ; mardis ordinaires 2026/2028 → run. **Aucune régression** (174 tests journaliste/mesure verts). `v3/data/` non pollué.
- **Garde-fous** : zéro invention, mode shadow, logique de compute non touchée (calendrier de garde uniquement), aucun jour ouvré normal bloqué, fallback anti-crash testé. **Aucun run déclenché.** `test_scoring.py` non touché (autre agent en parallèle).

## 2026-06-06 (Session 4) — Test audit-veille rendu déterministe (date figée jour ouvré) — fin du faux rouge week-end

**Bug du test (pas du code)** : `test_audit_veille_liste_conviction_normale_vrai` et `test_audit_veille_exclut_faible_carry_news` (`v3/tests/test_scoring.py`) ancraient `now = datetime.now()` puis `bdate = now - 1 jour`. Le **samedi**, `bdate` = vendredi et la logique d'échéance 24h jour-ouvré/fériés (ajoutée en S3) reporte au lundi → la cellule n'est « pas encore » mesurable → l'assertion `assert "Pas encore" not in txt` casse. Le test échouait donc **uniquement selon le jour réel d'exécution** (rouge le samedi 06/06, vert en semaine).

### Correctif (@fullstack)
- **`v3/tests/test_scoring.py`** : `now` figé sur **`datetime(2026, 6, 9, 12, 0)`** (mardi) → `bdate` = **lundi 2026-06-08** (jour ouvré, NI week-end NI férié de marché) → échéance 24h mûre quel que soit le jour réel. **2 tests corrigés**. Assertions métier intactes (✅, VRAI, +5.00%, exclusion faible/carry/news). `test_audit_veille_warmup_message` laissé tel quel (indépendant du jour : vérifie le message warm-up sans cellule à mesurer).
- **Gate** : `python3 -m pytest v3/tests/test_scoring.py -q` → **33 passed, 100% vert** (dont les 3 `test_audit_veille_*`). `v3/data/` non pollué (`git checkout` post-run).

## 2026-06-06 (Session 4) — Garde de run étendue aux jours fériés de marché (réutilise `MARKET_HOLIDAYS`)

**Demande fondateur (« point final »)** : des rapports **uniquement les jours où la bourse est OUVERTE**. Le week-end était déjà coupé ; il manquait les **jours fériés de marché** — un lundi férié (NYSE/Euronext fermés) produisait encore un bulletin sur **prix figés à la clôture précédente** + mesures 24h dégénérées (« +0.0% ») qui polluent le shadow.

### Correctif (@infrastructure)
- **`v3/scripts/journaliste.py`** : nouvelle fonction importable **`is_trading_day(d: date) -> bool`** = `jour ouvré (lun-ven) and not _is_market_holiday(d)`. **SOURCE DE VÉRITÉ UNIQUE** : réutilise EXACTEMENT le calendrier existant `_is_market_holiday` / `MARKET_HOLIDAYS` (NYSE ∪ Euronext) — **zéro liste de dates dupliquée**, une seule à maintenir. La fonction ne juge QUE le jour (le bypass `force` reste dans la garde YAML).
- **`.github/workflows/cycle.yml`** — étape Guard : le test week-end bash pur est remplacé par un appel **Python** à `is_trading_day(today Europe/Paris)` (stdlib + `MARKET_HOLIDAYS` statique, aucune dépendance réseau/pip — `python3` est dispo sur les runners avant le setup deps). Conservé : échappatoire `force`/`RUN-CYCLE.txt` (bypass tout), anti-doublon ×3 schedule-only. Si bourse fermée (week-end **OU** férié) et pas de force → `run=false` (NO-OP) avec log clair (« week-end » / « férié de marché AAAA-MM-JJ »). Table de vérité mise à jour (ligne « dispatch (VPS) / jour férié / false → NON ← FIX »).
- **VPS (`trigger-cycle.sh`)** : la garde week-end bash y reste (fast-path) ; les **fériés** sont gérés de façon **autoritaire au niveau du workflow** (le VPS n'a pas l'env Python du repo et NE recopie AUCUNE liste de fériés). Le VPS peut tirer un lundi férié → le workflow NO-OP. Documenté dans `v3/ops/vps-trigger/README.md`.
- **Tests** : `v3/tests/test_is_trading_day.py` (7 cas : mardi True, samedi/dimanche False, **férié réel de `MARKET_HOLIDAYS`** False, cohérence calendrier, signature `is_trading_day(d)` sans `force`). `test-guard-logic.sh` étendu (param `holiday`) → **13 cas verts** dont férié schedule/dispatch/force/push. `v3/data/` non pollué (vérifié).
- **Garde-fous** : zéro duplication du calendrier, zéro invention, mode shadow, aucun jour ouvré normal bloqué, logique de compute non touchée (garde de déclenchement uniquement). Aucun run déclenché.

## 2026-06-06 (Session 4) — Garde week-end étendue à `workflow_dispatch` (VPS) + input `force` + garde jour-ouvré VPS

**Bug** : un briefing a été produit **samedi 06/06 07h** alors que le week-end doit être coupé. **Cause racine** (diagnostiquée, non ré-enquêtée) : la garde week-end de `cycle.yml` ne s'appliquait qu'aux événements `schedule`. Or le **driver réel** est le **pinger VPS**, qui déclenche en **`workflow_dispatch`**. L'early-exit en tête de garde (`if event != schedule → run=true; exit`) traitait `workflow_dispatch` comme un forçage manuel → le NO-OP week-end (plus bas) n'était jamais atteint pour le VPS. Résultat : run samedi sur prix figés (clôture vendredi) → mesures 24h dégénérées polluant le shadow.

### Correctif (@infrastructure)
- **`.github/workflows/cycle.yml`** : input booléen **`force`** (défaut `false`) ajouté à `workflow_dispatch`. Garde **restructurée** (table de vérité en commentaire) : (1) **forçage explicite** = `inputs.force=='true'` **OU** push `RUN-CYCLE.txt` → `run=true`, bypass tout (week-end inclus) = échappatoire humaine ; (2) **sinon** (schedule OU dispatch-VPS sans force) → **garde week-end** (sam/dim Europe/Paris → `run=false`) ; (3) jour ouvré → **anti-doublon ×3 pour le schedule uniquement** (VPS = 1 tir/créneau, toujours passé, comportement préservé). **Aucun run de semaine affecté.**
- **`v3/ops/vps-trigger/trigger-cycle.sh`** : **garde jour-ouvré** ajoutée (`TZ=Europe/Paris date +%u ≥ 6 → exit 0`) → le pinger ne dispatche même pas le week-end (économise un no-op, cohérence). `TRADINGAPP_FORCE=1` bypass aussi. Garde week-end côté `cycle.yml` conservée en **défense en profondeur**.
- **`v3/ops/vps-trigger/test-guard-logic.sh`** : nouveau script de test (miroir exact de la décision YAML) — **10 cas verts** dont les 6 clés de la table de vérité. README VPS documenté.
- **Garde-fous respectés** : aucun run déclenché (logique seule), compute du pipeline non touché (garde de déclenchement uniquement), mode shadow préservé.

## 2026-06-06 (Session 4) — `mining_com` retiré (403 Cloudflare persistant CI, retry inefficace)

**Contexte** : le retry 403 borné posé le 05/06 (`RETRY_STATUS_WITH_403`, cf. Bug 2 plus bas) **n'a PAS résolu** le problème. Le run live frais du 06/06 07h montre `mining_com` **toujours ❌ HTTP 403**. **Diagnostic confirmé** (pas ré-enquêté) : blocage **Cloudflare PERSISTANT sur la plage d'IP des runners GitHub Actions** — le feed répond 200 ailleurs, jamais depuis CI. Le retry ne peut rien faire si TOUTE la plage d'IP est bloquée (≠ 403 intermittent par requête, hypothèse du 05/06 invalidée). **Décision (avec Thomas) : retirer la source** (poids faible ~1.1, redondante avec `investing_commodities`/`investing_metals` poids 0.9 + `oilprice`).

### Retrait (@fullstack)
- **`v3/scripts/config.py`** : ligne `("mining_com", …)` retirée de `EARLY_SIGNAL_FEEDS` + poids `"mining_com": 1.1` retiré de `SOURCE_WEIGHTS`. Commentaire de retrait documenté in-place (pourquoi). Le **total de flux n'est PAS figé** (`source_monitor.summary()` = `len(self.by_name)` dynamique) → il se décrémente seul, plus de faux « partiel ». Plus aucun appel `mining_com` → plus de ❌ 403 dans `source-health.md`.
- **Aucun critère cassé** : les news sont poolées + matchées par mots-clés. Les critères `mining_strikes_*`/`demande_pv_mining_strikes` (cuivre/argent) matchent sur le **pool global** de news, sans dépendance au flux `mining_com` (vérifié : zéro mapping nommé vers le flux). Le retrait enlève quelques items, ne touche ni scoring ni mesure.
- **Mécanisme retry 403 conservé** pour les autres RSS scrapables (`RETRY_STATUS_WITH_403` reste utile si un flux a un 403 *réellement* intermittent) — commentaires généralisés (plus de dépendance à mining.com comme exemple).
- **Pas de remplacement câblé** : aucun flux métaux/mining RSS gratuit n'a de certitude de marcher depuis les runners CI (c'est le piège exact qui a tué mining_com). Candidats à TESTER avant câblage : `kitco.com` RSS, `investing.com/rss/commodities_Industrial_Metals.rss`. Retrait net = objectif minimal atteint.
- **Tests** : références flux→config remplacées (`investing_metals` / nom générique) ; assertions `mining_com not in feeds/polled` ajoutées. Suites ingestion+http_retry+source_monitor **61 verts**. Suite `v3/` complète : **878 passed** (1 échec **pré-existant** `test_audit_veille_liste_conviction_normale_vrai`, date-dépendant samedi, sans lien). `v3/data/` restauré après pytest (pas de pollution des runs réels).

## 2026-06-05 (Session 4) — Corrections audit trio bulletins live (A1/A2 flag-only) + recos Lot 4b/ticket C

**Contexte** : audit trio des bulletins live 04-05/06 (Analyst/News Trader/Spéculateur). Verdict unanime **AJUSTER**. Corrections appliquées = **flag-only, zéro impact conclusion/mesure**. Tout ce qui touchait une DÉCISION (Lot 4b contre-momentum, ticket C calibration) → **reco À VALIDER THOMAS**, pas appliqué (garde-fous fondateur). 870 → 873 → **879 tests** (+6 : 2 micro-bugs run live 18h04, voir bas de section), 0 régression. Doc clé : `v3/audit/reco-corrections-2026-06-05.md`.

### Outil — relancer le backtest quant v2 AVEC FRED (@infrastructure)
- **Nouveau workflow `.github/workflows/backtest-v2.yml`** (job `backtest-v2-fred`, `workflow_dispatch` **MANUEL uniquement**, jamais de cron → ne concurrence pas `cycle-decision`, mode shadow préservé). Expose `FRED_API_KEY` (secret), lance `backtest_quant.py`, publie le log/REPORT en **artifact** (`upload-artifact`). But : clore le verdict sur l'arm d'ablation **`+FRED`** (le run de réf a tourné sans clé → `+FRED` == `price-only`).
- **Stratégie cache** : yfinance étant **bloqué sur les runners CI**, le **cache prix/COT** (`v3/backtest/.cache/*.csv`, 35 fichiers, 3,6 Mo, OHLCV/COT publics, **0 secret**) est **committé** (`git add -f`, dossier gitignored). Le CI lit ce cache (0 appel yfinance) + appelle **FRED réellement** (les `fred__*.csv` sont **volontairement NON committés**) + CFTC Socrata. Step sanity qui abort si cache absent. Fallback documenté : VPS Anya.
- **Garde-fous** : `permissions: contents: read`, **AUCUN commit auto** (l'exécution salit `v3/data/` via import `scripts/` → un commit écraserait les runs réels de `cycle-decision`). Doc « Comment relancer avec FRED » ajoutée à `v3/backtest/REPORT.md`. Tests `test_backtest.py` **21 verts**. **Non déclenché** (Thomas décide du lancement).

### Vrais bugs corrigés (affichage uniquement)
- **A1 — mono-critère rendu VISIBLE** (`◧`) : la détection `mono_critere_dominant` fonctionnait déjà (CAC 7j ET EUR/USD 7j = True au decision-log — l'« incohérence d'affichage » de l'audit n'existait pas), mais le flag était SHADOW decision-log only, jamais affiché. Les 3 experts jugent le mono-critère trop fragile pour rester invisible (EUR/USD 7j = 96% sur 1 critère). Ajouté : drapeau `◧` dans la matrice + section « Cellules à surveiller » + légende. **Conclusion/mesure inchangées.**
- **A2 — champ shadow `quasi_neutre`** au decision-log (`|score| < NEUTRAL_BAND=0.30`) : englobe coin-flip strict ET bande `≈`. Cuivre 7j (-0.22) était raté par `coin_flip` (seuil 0.05) → désormais `quasi_neutre=True`. **Le seuil `coin_flip`/`EPSILON_CARRY` (0.05) N'A PAS bougé** (il est couplé à la contradiction du carry-forward = seuil décisionnel, garde-fou).

### Enquêtes → reportées (pas de bug → reco)
- **B1 CAC « à l'envers »** : signe spread OAT-Bund **vérifié CORRECT** (élargissement → SHORT = risque France baissier, conforme). SHORT = contre-momentum pur (déjà flaggé `⇄`). Faire agir le `⇄` = **Lot 4b → reco À VALIDER THOMAS** (cap contre-momentum), non appliqué.
- **B2 Cuivre SHORT 7j/1m** : mono-critère COT + couverture 48%. Marquage déjà correct (`≈`+`⚠️`+`↯`). Abaisser couverture = **ticket C → reco**.
- **C1 S&P 7j / C2 Argent 1m / C3 échelles saturées** : pertinence par horizon + échelles. Aucun bug technique trouvé (fenêtres/séries correctes, saturation modérée ~1.1-1.3σ non absurde) → **ticket C → recos**, non appliqué.
- **DXY 118.9** (bonus News Trader) : **faux positif d'audit** — `dxy_trend_20j` câblé sur FRED DTWEXBGS (base 2006=100, ~120-130 normal), PAS le DXY classique. z-score = tendance 20j (pas niveau). Donnée + signe **sains** → aucune correction.
- **#8 Or SHORT « à contre-sens »** (backtest 1m 18.2 %) : enquête signe complète (`v3/audit/enquete-or-2026-06-05.md`). SHORT piloté à ~60 % par le critère **TIPS** (taux réels), signe `-1` **macro-canonique vérifié CORRECT** (taux réels hauts → coût d'opportunité or → baissier). **PAS un bug de signe.** Les 7 signes Or sont corrects. Le backtest « sent l'inversion » à tort : (a) il **ne teste pas le TIPS** (run sans `FRED_API_KEY` → poids 0, le 18 % = COT+price-only), (b) il est **news-blind** sur un or **+70 % en 2025 MALGRÉ des TIPS au plus haut** = **rupture de régime** (or-refuge/dédollarisation a découplé la relation or/taux-réels). Inverser le signe = overfit au régime 2025 (l'Or basculerait +12.6/+13.4 LONG). → **RÉGIME/CALIBRATION → reco À VALIDER THOMAS** (ticket C : rééquilibrer poids/pertinence TIPS vs géopol-refuge ; re-run backtest avec FRED). **Aucune correction de code.** Impact décision : NON (Or reste SHORT, `↯` signale déjà le piège).

### 2 micro-bugs du run live 18h04 (audit infra/affichage — zéro impact décision, mode shadow)
- **Bug 1 — nom de fichier du bulletin en UTC au lieu de Paris** (`scoring_analyste.py`). Le run 18h04 Paris produisait `bulletin-2026-06-05-16h.md` (heure UTC) alors que le **titre interne** (« 18h04 (Paris) ») et le **decision-log** (`...-1804.jsonl`) sont en heure Paris → fichier incohérent avec son contenu. **Cause racine** : `out_path` utilisait `now.astimezone(timezone.utc)` au lieu de `now` (Europe/Paris), la même source d'heure que le titre. **Fix** : construire le créneau du nom depuis `now` (Paris) → `bulletin-...-18h.md`. Le `bulletin_id` (stem) est une clé d'identité opaque (prix d'émission, tri, parsing) jamais réinterprétée comme une heure UTC → changement sûr. **Les bulletins déjà produits ne sont PAS renommés** (rétro-compat, historique préservé). +1 test (run 18h04 Paris → `-18h.md` + cohérence titre). Commit `e5f849b`.
- **Bug 2 — `mining_com` 403 revenu malgré l'UA Chrome**. **Diagnostic** : l'UA Chrome ÉTAIT bien propagé sur ce flux (`_fetch_rss` → `http_get_retry(headers=…)`), et `mining.com/feed/` répond **200** depuis cet environnement (les 3 jeux de headers testés passent). Le 403 n'est donc **PAS** « header non propagé » ni un **blocage durable** : c'est un **403 WAF (Cloudflare) intermittent** (challenge transitoire selon l'IP/géo des runners GitHub Actions). Le problème : le 403 était traité comme **non-retriable** → un 403 ponctuel devenait un échec définitif sur le cycle. **Fix mesuré, sans forçage** : (a) en-têtes navigateur enrichis sur les RSS (`config.BROWSER_HEADERS` = UA + `Accept` + `Accept-Language`, certains WAF inspectent `Accept*`) ; (b) nouveau paramètre `retry_status` sur `http_get_retry` + set `RETRY_STATUS_WITH_403` appliqué **au seul flux RSS** → un 403 transitoire est retenté (borné par `max_retries`), pas FRED/GNews/NewsAPI (défaut inchangé, zéro régression). Si le 403 **persiste** après retries → `source_monitor` signale le flux **muet** = dégradation propre déjà en place (zéro acharnement, zéro invention de news). +6 tests (3 http_retry, 2 ingestion RSS, +helpers). Commit séparé.

## 2026-06-03 (Session 3) — Audits trio, refonte page de rendu & comblement des données

**Contexte** : revue fondateur du bulletin frais + audits par le trio + le designer. Beaucoup de polissage, de fiabilisation et de **branchement de données** (le gros levier de qualité). 684 → **859 tests**, 0 régression.

### Bulletin — polissage post-audit trio (affichage/shadow, 0 impact conclusions)
- **Top 3 convictions = actifs distincts** ; **régime news** affiché sans contradiction de signe (`LONG [quant -0.08] 📰`) ; **bande quasi-neutre `≈`** (shadow, |note|<0.30) ; **mono-critère dominant** loggé (shadow). (`f19face`)
- **Fix mesure** : les cellules news (`📰 régime news` + `(brut LONG +X)`) n'étaient PAS mesurées → parsers corrigés. (`e2b3e18`)

### Page de rendu (`build_html`) — audit designer 6.5/10 → ~8.5
- **Favicon** (base64 — les entités HTML ne s'affichaient pas), **dark mode auto**, **onglet « 📊 Historique / Performance »** + persistance `measures-log.jsonl`, tooltips symboles, fusion en 1 table, ⚑ dégonflé. (`120df61`,`6c33b2f`,`9d8726b`,`1ec3158`)
- Bulletin : **décimales 4 sig figs**, section **« Audit de la veille 24h »** (réel %+VRAI/FAUX), **flux muets** reclassés (≠ pannes), ligne **Fraîcheur lisible**, légende d'échelle. (`0eb4bab`,`120df61`,`4f49f14`,`0c307b3`)

### Fiabilité mesure
- **Le système ne tourne plus le week-end** (garde jours-ouvrés cron) ; **échéance 24h sur jour ouvré** (vendredi→lundi) **+ jours fériés** NYSE/Euronext ; **verrou look-ahead C5 armé** (date du tick) ; **filet anti-mesure dégénérée** (prix figé = non-conclusive). (`875722c`,`f629fff`)
- **Dédup news inter-jours** verrouillée (event_id SHA-256 + event_date + Levenshtein 48h, rapidfuzz). (`e64a7b5`)

### Données comblées (gros gain de couverture)
- Récupérés via fix composite/mapping + source VIX unifiée : café météo (p11), VIX régime S&P (p8), HF cacao… (`7bbe128`)
- **Caixin PMI** via extraction news (`f0a9790`) ; **DXY**/**taux 10Y delta 5j**/**spread OAT-Bund** via FRED (`45dd253`) ; **Shiller CAPE** via scraper multpl défensif (`38fdded`) ; **différentiel taux 2Y US-DE** (EUR/USD, **poids 12**) via FRED+ECB Data Portal (`2197e1f`).
- ⚠️ Signe/échelle de ces nouveaux critères = **hypothèses à valider en shadow** (comme le proxy breadth).

## 2026-06-02 (Session 2) — Gate intelligent (anti-biais de survie) + audits reproductibles

**Contexte** : revue des 6 points fondateur + audits par le trio (Analyst/Spéculateur/NewsTrader). La P1 « calibration coverage » (12 actifs muets en INSUFFISANT) est attaquée non par un seuil arbitraire mais par un **gate à priorités**.

### Gate de suffisance — nouvelle logique à priorités (`scoring_analyste.py`)
- **Hystérésis de maintien** (carry-forward, horizon-aware) : `0.25 ≤ cov < 0.40` + dernière direction valide non contredite + non périmée → **⏸ maintenu** au lieu de 🚫 (`COVERAGE_FLOOR=0.25`, `CARRY_MAX_AGE_H={24h:24,7j:48,1m:24}`). Source = decision-log scanné. Smoke réel : **9 cellules récupérées**. (`b868b6d`)
- **Régime news-driven** (cuivre/cacao/café) : couverture quant insuffisante + biais news net (`ratio_news>0.5`) → **📰 direction news** au lieu de 🚫. Helper `compute_news_bias` factorisé. (`2b209d8`)
- Ordre final : quant ≥40% → ⏸ carry → 📰 news → 🚫. Cellules ⏸/📰 portent une vraie direction → **mesurées** (tags `is_carry`/`is_news_regime` pour audit hit-rate futur).

### Bulletins & monitoring
- **3 briefings/jour distincts** `bulletin-{date}-{HH}h.md` (fin du biais de survie : matin/midi/soir s'écrasaient) ; prix d'émission re-clés par créneau ; chacun mesuré. (`7df13ce`)
- **Monitoring sources 3 états** : OK / ⚠️ partiel (R/N) / ❌ — fin des faux ❌ GNews quand 13/14 requêtes passent. (`8b172c2`)
- Note + **confiance%** au lieu de force ●/○, + légende d'échelle. (`040f687`, `0c307b3`)

### Bug & audits
- **🐛 Bug VIX** : `vix_regime` renvoyait +1.0 (plateau 14-25) au lieu du triangle des fiches → faux signal **haussier** systémique sur S&P/Nasdaq/CAC dès que VIX∈[14,25]. Corrigé en triangle (VIX 23.9 : +1.0→-0.36). (`5719cde`)
- **Audit S&P reproductible** (`v3/audit/sp500-explication-reproductible.md`) : la formule `signe×poids×pertinence×norm` reconstitue les scores au centième. Drivers réels = taux réels TIPS + breadth (pas le VIX, absent du run). A corrigé une narration initiale erronée (crédit HY mal signé) ET un angle mort de l'audit lui-même.
- Vérifié : `compute_coverage` pondère déjà par poids (ticket E, rien à faire) ; horodatage = faux problème.
- **684 tests**, 0 régression (8 échecs pré-existants env-only).
- **Différé → C** : calibrer `COVERAGE_MIN` (0.40) sur hit-rate réel — rouvrir ~2026-06-23 quand les tags `is_carry`/`is_news_regime` auront accumulé assez de mesures.

### Polissage post-audit du bulletin (trio → consensus en 3 rounds)
Audit forme+fond du bulletin par le trio : Fond **6/10** (méthode 8, mais données qui la nourrissent 4), Forme **6/10** (transparence forte, mais dense/bruitée). Plan de 6 actions re-priorisé par « impact/effort », exécuté en autopilote :
- **🔴 #1 Bug normalisation** : `normalise()` jetait en silence les critères `composite`/`mapping_non_monotone` (« type inconnu ») → critères à fort poids récupérés : café météo (+11), S&P VIX régime (+8), CAC V2X (+8), Nasdaq VXN (+7), cacao HF (+7). Bug côté consommateur seul (émission déjà correcte). (`7bbe128`)
- **🔴 #2 Incohérence VIX** : `vix_regime` lisait 23.6 (Twelve) vs 14.95 (CBOE) pour le même VIX → unifié sur la source CBOE fraîche (14.95 → +0.975 régime sain). (`7bbe128`)
- **🟡 #6 News** : dédup des news identiques au sein d'un actif (doublon SoftBank CAC) + troncature propre sur frontière de phrase (140→240). (`4e737e0`)
- **🟢 #4/#5 Forme** : bloc **🎯 Top 3 convictions** en tête ; **fusion des 2 tables** de synthèse en une ; **⚑ régime extrême** annoncé 1× au lieu de 12× ; « à surveiller » resserrée (27→6-7 lignes, alertes directionnelles seules). (`1ec3158`)
- **⏸ Différé → #3** : combler les vraies données absentes (Caixin PMI cuivre p.12, diff. taux EUR/USD p.12, etc.) = chantier sources (nouvelles intégrations), non autopilotable.
- **716 tests** verts, 0 régression (8 échecs pré-existants env-only).

## 2026-06-01 (soir) — Observabilité news + optimisation requêtes (10/10)

- **Bilan des news** : bloc dans le bulletin marquant les calls portés par les news qui ont marché/raté (juger le jugement DeepSeek).
- **source_monitor** : santé des flux par cycle (appelé/OK/échec/muet + reçus vs gardés + raison) → `v3/data/source-health.md` + bloc « Santé des sources » dans le briefing + kit d'analyse. Fix 4 flux muets (gnews_cac40 FR, gnews_wheat query, investing_stocks doublon ; mining_com 403 visible).
- **Optimisation requêtes news (audit 3 experts, 3 rounds → 10/10 côté news)** : comble Nasdaq (Nvidia/IA/semi) + VIX (volatilité + causes amont war/escalation), retire DAX, supprime Q3 redondante, dégroupe Or/Argent/Cuivre, sépare Fed/BCE, S&P earnings-driver, enrichit CB-gold/solaire/EUDR/WASDE/café-gel/blé-GASC/CAC-SBF120. 14 requêtes, 22 flux. Plafond news 9,5-10 (reste = pipeline data : CFTC COT, ETF, CBOE, GASC).
- **Kit d'analyse du matin** : `python3 v3/scripts/analyse_complete.py` (matrice, bilan news, mesure, Phase 2 T1/T2, biais, flips, santé sources, backtest).
- **Backtest quant v1** : `v3/backtest/` — moteur historique no-look-ahead ; v1 (price-only, 4 actifs × 24h) = NO-GO (50.8% OOS, partiel). v2 (COT+FRED+horizons) = prochain chantier.

## 2026-06-01 — Fiabilisation run quotidien + plan horizon

**Contexte** : répétition des cycles quotidiens pour débusquer les défauts cachés, audit par les 3 experts, correction en autopilote.

### Correctifs pipeline
- **Routing IA-first réparé** : le parser ignorait les impacts DeepSeek → la synthèse directionnelle (LONG/SHORT par actif) pilote désormais les critères news.
- **Prix d'émission réparés** : la boucle prédiction→mesure (Journaliste) est fermée — conclusions VRAI/FAUX réelles.
- **Indices via ETF Twelve Data** : `^GSPC→SPY`, `^IXIC→QQQ`, `^FCHI→FCHI`, `^VIX→VIXY`, etc. (yfinance bloqué sur les runners GitHub). Débloque CAC/S&P/Nasdaq (0 tie-break).
- **Rate-limiter Twelve** : `_acquire_rate_limit` attend un slot au lieu de rejeter (→ fallback yfinance bloqué) ; `TWELVE_RPM=55` (plan Grow). Cause racine des indices n/a en CI.
- **PROBA_SCALE 10→15** (anti-saturation Brier), propagation `reliability`, garde chevauchement 7j/1m.

### Audits (3 experts : Analyst / News Trader / Spéculateur)
- Audit des runs dans l'ordre d'édition (`v3/audit/chaine-*.md`).
- **Audit de cohérence** (`coherence-3-experts.md`) : 2 faux positifs écartés sur preuve (signe géopol déjà câblé `ia_synthese` ; events 2025 filtrés par cutoff lookback).
- Trio formalisé comme panel d'audit officiel (`v3/audit/README.md`).

### Plan horizon (validé Thomas + 3 experts)
- **Constat** : DeepSeek produit 1 direction/actif **horizon-agnostique** ; sur cellules faibles/longues la news domine voire inverse le quant (Or 24h 43%, VIX 1m 480%).
- **Décision** : PAS de decay global (casserait l'OPEC). Recalibrage `pertinence` (or/petrole/vix) + cap anti-inversion α=0.8 (override si high+confirmed) + `ratio_news`/drapeau 📰.
- **Preuve** : Or 24h +0.17→−1.33 SHORT, VIX 1m +0.25→−0.55 SHORT, Pétrole/S&P inchangés. 360 tests.

### Infra
- `schedule` GitHub diagnostiqué **retardé de 1-3h** (6 runs prouvés les 30-31/05), pas une panne. Redondance cron ×3 (`:12/:27/:42`) + garde-fou anti-doublon. Permissions read/write activées.
- **À faire (Phase 2)** : tracer `event_id`/date + flag nature news (structurel/ponctuel/déjà-price) — cause racine du biais news.
