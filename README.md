# TradingApp

Bot Telegram qui envoie a Thomas un signal turbo justifie par jour ouvre a 8h45-8h55 CET.

**Statut** : Phase 2a — squelette + mini-jalon J+7 (hello-world cron Telegram). R&D edge a venir (30-90j).

## Disclaimer juridique

Outil personnel a usage strictement individuel. **Pas un conseil en investissement** au sens de l'Art. L. 321-1 du Code monetaire et financier. Aucune redistribution autorisee. Cf. `docs/legal/legal-audit.md`.

## Quick start (Replit)

1. Forker / cloner le repo (prive obligatoire — donnees financieres personnelles).
2. Renseigner les Replit Secrets selon `.env.example` (cf. `REPLIT_ACTIONS.md`).
3. Cron Deployment configure a 8h40 CET, lundi-vendredi : `python -m src.main --mode=hello`.
4. Verifier la reception Telegram + le ping healthchecks.io le 1er jour ouvre.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # remplir les valeurs
python -m pytest tests/
python -m src.main --mode=hello
```

## Modes d'execution

- `--mode=hello` : push hello-world Telegram (mini-jalon J+7).
- `--mode=live` / `--mode=paper` : Phase 2c (fallback hello-world tant que pipeline scoring pas implemente).

## Arborescence

```
src/
├── main.py             entry point CLI
├── config.py           validation env vars (Pydantic)
├── telegram/           wrapper Bot API + templates
├── journal/            init SQLite + DDL 7 tables
├── scheduler/          calendrier ouvre FR + fenetre 8h40-8h55
├── ai/ scoring/ backtester/  stubs Phase 2b/2c
└── lib/                logger JSON + healthchecks.io
tests/                  pytest (config / schema / calendrier)
data/                   journal.sqlite (cree au runtime, gitignore)
```

## Documentation amont

- `docs/product/functional-specs.md` — 12 user stories
- `docs/analytics/kpi-framework.md` — schema SQLite + KPI
- `docs/ia/edge-scoring-model.md` v1.1 — sanity checks SC1-SC6
- `docs/ia/prompt-library.md` — `signal-scoring-v1.0`
- `docs/infra/infra-audit.md` — cron Replit + healthchecks
- `docs/legal/legal-audit.md` — AMF, RGPD, PFU 31,4 %

## Tests

```bash
python -m pytest tests/ -v
python -m mypy src/
python -m ruff check src/
```
