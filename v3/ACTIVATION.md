# TradingApp v3 — État & activation

> MAJ 2026-05-29 (autopilote). Archi : GitHub Actions + git-as-storage, zéro VPS/Cowork.
> Pipeline complet, testé (53 tests verts), tourne bout-en-bout. Reste : clés API + go-live shadow.

## Ce qui est FAIT ✅

| Brique | Fichiers | État |
|---|---|---|
| Ingestion news (DeepSeek) | `scripts/{extractor,news_collector,agent_news}.py` | ✅ optimisé (schéma 7 champs, blacklist, cost-cap) |
| Moteur scoring déterministe | `scripts/scoring_analyste.py` | ✅ 22 tests (formule, tie-break, n/a→0, flips, GATE drapeau) |
| Calcul critères | `scripts/criteres_calculator.py` + `triggers_classifier.py` | ✅ 31 tests, dégradation gracieuse |
| 12 fiches actifs | `config/fiches/*.yml` | ✅ 114 critères |
| Triggers/fenêtres | `config/triggers-and-windows.yml` | ✅ 11 triplets + 7 fenêtres |
| Orchestrateur + cron | `scripts/run_bulletin.py` + `.github/workflows/` | ✅ ingest /30min + bulletin 7h CET |
| Stockage | git (`data/*.md`) | ✅ |

**Comportement actuel sans clés** : bulletin produit, 30/114 critères alimentés (triplets neutres, calendriers, gates, hors-fenêtre=0). Le reste `n/a` (poids 0). **Zéro invention.**

## Ce qui BLOQUE la montée en couverture (→ toi)

### 1. Secrets GitHub (repo → Settings → Secrets → Actions)
| Secret | Débloque | Obligatoire |
|---|---|---|
| `TWELVE_DATA_API_KEY` | prix, RSI, DXY, spreads, z-scores (~40 critères) | oui (tu as plan Grow) |
| `DEEPSEEK_API_KEY` | extraction news → events-log → triplets | oui |
| `EIA_API_KEY` | stocks pétrole/gaz | recommandé |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | émission Argos (post-shadow) | plus tard |
| `HEALTHCHECKS_URL` | monitoring | recommandé |

### 2. Repo public (minutes Actions illimitées) — décision déjà prise.
### 3. Argos via BotFather (plus tard, pour le go-live actif).

## Couverture des critères (114 total)

- **Câblé, s'alimente avec clés** (~70 %) : prix/indices/FX/taux/spreads/ratios (Twelve Data), CFTC COT (Socrata, *market names à raffiner*), EIA, Open-Meteo (zones agri *à router sur cle_courante*), triplets (events-log via DeepSeek).
- **Sans API programmatique → reste n/a** (~30 %, design) : AAII, flux ETF, breadth, WGC achats CB, ICCO grindings, GASC, mappings non-monotones V2X/VIX/VXN, composites. → scraping/saisie manuelle ultérieure si jugé utile (le système tranche quand même : poids 0).

## TODO routing (autopilote, faisable mais à valider avec clés)
- mapper chaque `cle_courante` à son ticker Twelve Data / endpoint (skips `no_ticker:*`, `zscore_unmapped:*`, `lineaire_unmapped:*`)
- corriger les `market_and_exchange_names` CFTC (les 3 actuels → 400 ; cf. `curl https://publicreporting.cftc.gov/resource/jun7-fc8e.json?$limit=1`)
- router Open-Meteo sur les clés agri (`meteo_ci_ghana_precip_30j`, etc.)

## Séquence go-live (mode shadow)
1. Ajouter les secrets + rendre le repo public.
2. Lancer manuellement le workflow `bulletin` (Actions → Run workflow) → vérifier le bulletin commité dans `data/bulletins/`.
3. Laisser tourner le cron quotidien 7h CET. **Aucune émission Argos** pendant ~30 j (shadow).
4. Le Journaliste (à brancher) mesure T+24h/7j/1m → `data/performance.md`.
5. Cellules > **70 %** réussite (target Thomas, `Bourse.md`) → bascule active (Argos).

## Décisions autopilote prises (révisables)
- GATE = **drapeau** (hors score, annoté). FedWatch proba = centre 0.5/échelle 0.2.
- zscore : `valeur_normalisee` pré-calculée par le calculator ; lineaire : `valeur` brute + fiche.
- Hors fenêtre d'activation → contribution 0 (pas n/a).

## Pas encore branché (incréments suivants)
- `journaliste.py` (mesure perf T+H via Twelve Data → performance.md + Brier) + workflow mesure.
- Émission Argos (Telegram) post-shadow.
- `source_monitor.py` (santé sources → source-health.md).
