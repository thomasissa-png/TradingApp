# Reco infra — TradingApp v3 sans VPS / Cowork / Claude Code web

> Source : `_BRIEFING-v3.md`. Mono-utilisateur, batch Python, zéro UI, zéro 24/7.
> Verdict global : **GitHub Actions (compute + cron) + git-as-storage (.md commités) + GitHub Secrets**. 0 €/mois infra (hors APIs métier).

## 1. Décision en une ligne

Tout le pipeline est un **paquet de scripts Python** dans CE repo, lancés par **GitHub Actions cron**, qui lisent/écrivent les `.md` **dans le repo lui-même** (commit auto). Aucun serveur, aucune DB, aucun runtime à maintenir.

## 2. Compute / scheduler

| Option | Verdict | Pourquoi |
|---|---|---|
| **GitHub Actions (cron)** | ✅ RETENU | Python natif (`actions/setup-python`), code Phase 2.1 réutilisé tel quel, 0 réécriture, free tier large, secrets intégrés, logs gratuits |
| Cloudflare Workers/Cron | ❌ | Pas de Python natif (JS/WASM), faille-il porter `feedparser`/`openai`/RSS ; CPU limité 30 s (10-15 min payant), I/O git impossible |
| Render/Fly cron | ❌ | Réintroduit un service à maintenir + facturation à l'usage |

**Quotas GH Actions** (repo privé) : 2 000 min/mois gratuit. **Repo public = minutes illimitées gratuites** → si le repo peut être public (aucun secret en clair, tout en Secrets), coût compute = 0 garanti. Voir §8 budget.

## 3. Données — où vivent les .md

| Option | Verdict | Pourquoi |
|---|---|---|
| **Git-as-storage (.md dans le repo)** | ✅ RETENU | Versionné (audit poids/prompts = diff git natif, exige red line "trace"), gratuit, lecture/écriture triviale en Python, diffable, backup = historique git |
| SQLite/D1 | ❌ | Sur-ingénierie pour 1 user ; perd la lisibilité .md ; D1 = runtime CF |
| Neon Postgres | ❌ | Idem, aucun besoin relationnel ni concurrence |
| Garder Google Drive | ❌ | Auth OAuth fragile en CI, pas de versioning de diff propre, dépendance externe inutile une fois sorti du VPS |

**Layout repo** : `data/events-log.md`, `data/criteres-courants.md`, `data/performance.md`, `data/bulletins/AAAA-MM-JJ.md`, `config/fiches/<actif>.md` (12 fiches = config versionnée). Cache dédup = `data/dedup-cache.sqlite` commité (petit) OU clé-hash dans events-log.

## 4. Secrets

GitHub repo → Settings → Secrets and variables → Actions. Jamais en clair, jamais dans `.env` commité.

| Secret | Usage |
|---|---|
| `DEEPSEEK_API_KEY` | extraction news |
| `TWELVE_DATA_API_KEY` | prix + mesure perf |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | émission Argos |
| `HEALTHCHECKS_URL` | ping monitoring |

(Plus de `GOOGLE_*` une fois Drive abandonné. `GITHUB_TOKEN` auto-injecté pour le commit.)

## 5. Planification (cron GH Actions, UTC)

| Job | Cadence voulue | Cron (UTC, été CEST=+2) | Précision |
|---|---|---|---|
| Bulletin matin | 7h CET quotidien | `30 4 * * *` (≈06h30 UTC marge) | dérive 5-15 min OK (lecture humaine) |
| Ingestion intraday | lun-ven 9h-22h, /30min | `*/30 7-20 * * 1-5` | dérive OK |
| Mesure + flips | quotidien 19h | `0 17 * * *` | OK |
| Audit hebdo | dim 20-21h | `0 18 * * 0` | OK |

⚠️ **Cron GH dérive 5-15 min en heures de pointe** : non bloquant ici (Thomas lit le bulletin, pas de latence marché à la seconde). **Heure d'hiver (CET=+1)** : ajuster les heures UTC 2×/an OU faire le décalage en Python (`zoneinfo Europe/Paris`) et planifier large. Reco : **calcul du fuseau en Python**, cron planifié 15 min avant l'heure cible.

## 6. Déploiement / maintenance

- **Déploiement = `git push`**. Pas de build, pas de serveur. Le workflow re-checkout le code à chaque run.
- Workflow type (un fichier `.github/workflows/`) : checkout → setup-python → pip install → run script → `git commit -am "data: <job>" && git push` (data write-back via `GITHUB_TOKEN`, `permissions: contents: write`).
- **Maintenance = zéro** : pas d'OS à patcher, pas de service à redémarrer (vs VPS systemd).

## 7. Monitoring / échec visible (red line)

- **Healthchecks.io** (gratuit, déjà câblé dans `agent_news.py`) : un check par job, ping `/start` /succès /`/fail`. Alerte mail/Telegram si pas de ping.
- **Alerte Telegram** sur exception (source DEAD, LLM erreur) : envoi direct au bot Argos depuis le `except`.
- **GitHub Actions** notifie par mail tout workflow en échec (natif, gratuit).
- Red line respectée : échec jamais masqué (log + Healthchecks `/fail` + Telegram).

## 8. Coût mensuel projeté

| Poste | Coût |
|---|---|
| Compute GH Actions | **0 €** (repo public = illimité ; privé = dans les 2 000 min) |
| Stockage git | **0 €** |
| Secrets / monitoring (Healthchecks free) | **0 €** |
| DeepSeek (métier, ~5 000 events) | ~6 € |
| Twelve Data (déjà payé, plan Grow) | 0 € marginal |
| Telegram | 0 € |
| **TOTAL infra** | **0 €** — **total avec API métier ≈ 6 €/mois** (< red line 30 €) |

**Estimation minutes** (si repo privé) : intraday ~26 runs/j × ~3 min × 22 j ≈ 1 700 min + jobs quotidiens ~150 min ≈ **1 850 min/mois** → sous le quota 2 000. Marge fine → **rendre le repo public** ou réduire l'intraday à /60min pour sécuriser.

## 9. Migration du code Phase 2.1

| Fichier | Sort |
|---|---|
| `extractor.py` (DeepSeek) | ✅ conservé tel quel |
| `news_collector.py` (RSS + filtre) | ✅ conservé tel quel |
| `agent_news.py` (loop `while True` + `sleep`) | ♻️ **refactor** : supprimer la boucle infinie + `time.sleep`, garder `run_one_cycle()`, exposer un `main()` one-shot appelé par le cron |
| `drive_publisher.py` | 🔁 **remplacer** par `repo_publisher.py` (écrit/append dans `data/*.md` local + commit) |
| `config.py` | ✅ conservé (31 sources + poids) |
| À écrire | `criteres_calculator.py`, `scoring_analyste.py` (règles pures, 0 LLM), `journaliste_mesure.py`, `source_monitor.py` |

**Effort migration : faible** — l'essentiel (RSS, dédup, extraction) est réutilisé ; on retire juste l'orchestration 24/7 (remplacée par le cron) et la couche Drive (remplacée par git).

## 10. Ce qu'on SUPPRIME (first-principles)

VPS systemd + `while True`/`sleep` + Cowork agents + Claude Code web + OAuth Google Drive. Le 24/7 était inutile : un batch /30min en heures de marché suffit à remplir events-log avant le bulletin de 7h.
