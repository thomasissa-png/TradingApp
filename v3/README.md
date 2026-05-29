# TradingApp v3

> Architecture **GitHub Actions + git-as-storage + GitHub Secrets**. 0 € d'infra.
> Source de vérité : `vps-news-collector/reco/RECOMMANDATION-ARCHITECTURE.md`.
> Briefing technique : `vps-news-collector/reco/_BRIEFING-v3.md`.

## Objectif

Produire chaque matin **7h CET** un bulletin de positionnement directionnel :
**12 actifs × 3 horizons (24h/7j/1m) = 36 cellules**, chacune LONG ou SHORT.
- Le système ne trade jamais. Thomas exécute manuellement chez Bourse Direct.
- Mode shadow 30-90 j avant émission Telegram.
- KPI : taux de réussite > 55 %/cellule, Brier < 0,25 sur 30 dernières conclusions.

## Architecture

```
v3/
├── scripts/                # Python one-shot (appelés par GitHub Actions)
│   ├── config.py           # constantes RSS + chemins
│   ├── extractor.py        # DeepSeek (schéma 7 champs, garde-fous coût)
│   ├── news_collector.py   # RSS → dédup → blacklist → whitelist finance
│   ├── repo_publisher.py   # append v3/data/events-log.md
│   ├── agent_news.py       # cycle complet one-shot (ingest)
│   └── run_bulletin.py     # STUB → scoring engine TODO
├── config/
│   └── fiches/             # 12 fiches actifs (YAML/MD) — à venir
├── data/                   # storage commité (events-log, bulletins, perf)
└── requirements.txt
```

Workflows GitHub Actions (à la racine `.github/workflows/`) :
- **ingest.yml** : cron `*/30 5-19 * * 1-5` UTC (≈ 7h-20h CET lun-ven)
- **bulletin.yml** : cron `30 4 * * *` UTC (≈ 6h30-7h CET, dérive DST ±1h tolérée)

## Ce qui marche (Incrément 1)

✅ **Ingestion news (one-shot)** :
- 5 RSS feeds (BBC, CNBC, Investing) — Reuters exclu (mort).
- Dédup Jaccard 0,65 (cache SQLite committé sous `v3/data/`).
- Pré-filtre 2 étages : **blacklist** (royals/sport/lifestyle) puis **whitelist finance**.
- Extraction DeepSeek `deepseek-chat` schéma 7 champs (L1, L2, trigger, cours, latence, news_zone, news_category).
- Garde-fous coût quotidiens persistés dans `v3/data/cost-ledger.json` :
  - soft cap 0,50 $/j → log WARN
  - hard cap 0,80 $/j → bascule fallback brut (pas d'appel LLM)
- Mode brut transparent si `DEEPSEEK_API_KEY` absent (le job ne crash pas).

✅ **Publication git-as-storage** :
- Append à `v3/data/events-log.md` (append-only).
- Commit + push par le workflow (PAT non requis, `GITHUB_TOKEN` suffit + `permissions: contents: write`).

✅ **Workflows GitHub Actions** :
- `ingest.yml` 30 min, lun-ven, jour
- `bulletin.yml` 1×/jour matin (STUB)

## Ce qui est STUBBÉ

🚧 `run_bulletin.py` — **imprime "scoring engine TODO"** et écrit un bulletin stub.
🚧 `criteres_calculator.py` — agrégation events + prix Twelve Data → criteres-courants.md
🚧 `scoring_analyste.py` — 12 fiches × 3 horizons × critères pondérés → 36 cellules
🚧 `journaliste.py` — mesure conclusions échues → taux + Brier → performance.md
🚧 `triggers_classifier.py` — classement critères événementiels (`triggers-and-windows.yml`)
🚧 `v3/config/fiches/*.yml` — 12 fiches actifs (poids/critères/seuils) à porter depuis le vault

**Dépendance bloquante** : les fiches actifs du vault Drive doivent être migrées
dans `v3/config/fiches/` avant d'écrire le moteur de scoring (les poids définissent
le calcul).

## Secrets GitHub à configurer

Settings → Secrets and variables → Actions :

| Secret | Usage | Optionnel ? |
|---|---|---|
| `DEEPSEEK_API_KEY` | extraction LLM (ingest) | non bloquant (fallback brut) |
| `TWELVE_DATA_API_KEY` | prix marché (criteres + bulletin + perf) | requis dès Incrément 2 |
| `TELEGRAM_BOT_TOKEN` | émission bulletin (post-shadow) | requis quand shadow → actif |
| `TELEGRAM_CHAT_ID` | destinataire bulletin | requis quand shadow → actif |
| `HEALTHCHECKS_URL` | ping monitoring (start/success/fail) | optionnel mais recommandé |

⚠️ **Aucune valeur en clair dans le repo**. Le `.env` est .gitignored.

## Exécution locale (debug)

```bash
cd v3
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-...
python scripts/agent_news.py      # un cycle complet
python scripts/run_bulletin.py    # stub bulletin
```

## Fuseau

Tout le code Python travaille en UTC. Les logs affichent l'heure Europe/Paris
via `zoneinfo` pour lisibilité humaine. Les crons UTC ciblent 7h-20h CET avec
une dérive DST de ±1h jugée non bloquante (lecture humaine du bulletin).

## Coût attendu

- GitHub Actions : 0 € (repo public, minutes illimitées).
- DeepSeek : ~2-3 €/mois cible (hard cap 0,80 $/jour = 24 $/mois plafond).
- Twelve Data : déjà payé (plan Grow).
- Telegram : gratuit.

**Total ≈ 2-3 €/mois.**

## Prochaine étape (Incrément 2)

1. Migrer les 12 fiches actifs du vault Drive vers `v3/config/fiches/*.yml`.
2. Écrire `criteres_calculator.py` (events-log + Twelve Data → criteres-courants).
3. Écrire `scoring_analyste.py` (somme pondérée par critère → LONG/SHORT par cellule).
4. Remplacer le STUB `run_bulletin.py` par le vrai pipeline.
5. Définir le kill criterion AVANT de lancer le shadow (Brier > X à J+60).
