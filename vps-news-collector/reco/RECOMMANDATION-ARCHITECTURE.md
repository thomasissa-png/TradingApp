# Recommandation architecture — TradingApp v3 (sans VPS / Cowork / Claude Code)

> Synthèse @elon + @infrastructure + @ia (29/05/2026). Détails : `reco-elon.md`, `reco-infra.md`, `reco-ia.md`.

## Consensus des 3 agents (à adopter)

**Stack = GitHub Actions (cron) + git-as-storage + GitHub Secrets. 0 € d'infra.**

| Brique | Décision | Remplace |
|---|---|---|
| Compute + scheduler | **GitHub Actions cron** (Python natif, le code Phase 2.1 tourne tel quel) | VPS systemd 24/7 |
| Stockage | **Git-as-storage** : `.md` commités dans le repo (events-log, criteres-courants, bulletins, performance) | Google Drive |
| Fiches actifs (poids/critères) | **Fichiers versionnés** (YAML ou MD) dans le repo — `git diff` = la trace anti-modif-silencieuse | skills Cowork |
| Les "4 agents" | **4 scripts Python** one-shot (fetch / score / measure / notify), pas des entités | skills Cowork |
| Émission | `requests.post` Telegram (10 lignes) | Argos skill |
| Secrets | GitHub Actions Secrets | `.env` VPS |
| Monitoring | Healthchecks.io + mail GH Actions + alerte Telegram sur exception | — |

**Planification (cron UTC, fuseau géré en Python `zoneinfo Europe/Paris`)** : bulletin `30 4 * * *` (≈7h CET), intraday `*/30 7-20 * * 1-5`, mesure `0 17 * * *`, audit hebdo `0 18 * * 0`. Dérive 5-15 min non bloquante (lecture humaine).

**Migration du code déjà écrit** : `extractor.py` / `news_collector.py` / `config.py` conservés ; `agent_news.py` → retirer la boucle `while True`/`sleep`, exposer un `main()` one-shot ; `drive_publisher.py` → `repo_publisher.py` (commit git). Effort faible.

**Coût total ≈ 0-6 €/mois** (infra 0 € ; DeepSeek 0-6 € selon décision ci-dessous). Bien sous la red line 30 €.

## Le seul désaccord : la couche news/LLM

| | @elon (couper) | @ia (garder optimisé) |
|---|---|---|
| Position | **Supprimer** ingestion 31 sources + DeepSeek + events-log en v1 | **Garder** DeepSeek `deepseek-chat`, schéma 11→7 champs, pré-filtre durci |
| Argument | L'Analyste = 100 % règles sur `criteres-courants`. Il ne lit pas `events-log` → l'extraction nourrit un musée. La valeur vient des prix + 5-8 séries macro structurées. | Le JSON structuré (cours/ticker, news_zone, L1/L2) **route** les news vers le bon critère/actif. Sans lui, impossible de désambiguïser "oil"→Brent/WTI. Couper casse les critères événementiels. ROI ~125x. |
| Coût | 0 € | 2-3 €/mois (cap dur 25 €) |

**Qui a raison dépend d'un fait** : combien des ~110 critères des 12 fiches actifs sont réellement *événementiels* (news) vs *numériques* (prix/macro structurée) ? `triggers-and-windows.yml` existe pour classer les critères événementiels — donc il y en a. Mais apportent-ils un *lift de Brier* ou du bruit ? Seul le shadow le dira.

## Recommandation tranchée (synthèse)

**Démarrer en v1 SANS la couche LLM, mais garder le code prêt.**

1. **v1 (2 semaines)** : bulletin scoré sur prix (Twelve Data) + 5-8 APIs macro structurées (EIA, CFTC, USDA/WASDE, NOAA, FRED) + critères événementiels classés par **mots-clés** (`triggers-and-windows.yml`, déjà en place, zéro LLM). → premier bulletin shadow committé vite. C'est la v1 d'@elon.
2. **Garder `extractor.py` archivé mais prêt** (testé, optimisable à 2-3 €/mo — @ia).
3. **Pendant le shadow, mesurer la contribution par critère au Brier.** Si les critères événementiels n'apportent pas de lift → on reste sans LLM (@elon avait raison). S'ils apportent un lift mais que le matching mots-clés route mal → on rallume DeepSeek ciblé (code prêt — @ia avait raison).
4. **Écrire le kill criterion MAINTENANT** (@elon) : Brier > X à J+60 → on arrête ou on pivote. À définir avant la S1, pas après.

Avantage : simplicité maximale au départ (le moins de pièces mobiles), option LLM préservée, et c'est **la data du shadow qui tranche**, pas une opinion a priori.

## Décisions validées (Thomas, 29/05/2026)

1. ✅ **GitHub Actions + git-as-storage** comme stack.
2. ✅ **LLM gardé en v1, optimisé** (option @ia) : DeepSeek `deepseek-chat`, schéma 11→7 champs, pré-filtre durci (~85-90 %), garde-fous coût (soft 15 €/hard 25 €) → ~2-3 €/mois.
3. ✅ **Target taux de réussite = > 70 %/cellule** (Thomas, 29/05), Brier < 0,25. Gating shadow→actif par cellule : une cellule passe en actif quand elle tient le target ; en dessous → reste shadow, le Manager retravaille les poids, Thomas valide.
   ⚠️ `Bourse.md` (vault) écrit encore « > 55 % » — à aligner sur 70 % (voir action ci-dessous).
4. ✅ **Repo public** (minutes Actions illimitées, intraday /30min conservé).

> ⚠️ Note : le repo `thomasissa-png/TradingApp` est marqué « à supprimer » dans `Bourse.md`. Le code v3 est construit dans un dossier `v3/` séparable (migrable vers un repo neuf à tout moment).
