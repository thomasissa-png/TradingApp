# CHANGELOG — TradingApp v3

> Historique des sessions de travail (le plus récent en haut). Détail technique : `git log` + `v3/audit/`.

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
