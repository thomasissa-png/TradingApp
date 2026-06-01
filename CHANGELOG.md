# CHANGELOG — TradingApp v3

> Historique des sessions de travail (le plus récent en haut). Détail technique : `git log` + `v3/audit/`.

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
