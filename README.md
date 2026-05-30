# TradingApp v3

Bulletin de **positionnement directionnel** : 3×/jour (7h/12h/18h CET), **12 actifs × 3 horizons** (24h/7j/1m), chaque cellule **LONG ou SHORT**. Trend-following multi-actifs. Thomas exécute manuellement (turbos Bourse Direct) — le système ne place jamais d'ordre.

> **Objectif** : être certain de la **tendance** par actif (suivre les vagues dans le bon sens), pas l'edge à la minute.

## Où est quoi

| Chemin | Contenu |
|---|---|
| `v3/scripts/` | le système (ingest, critères, scoring, briefing, journaliste) |
| `v3/config/` | fiches actifs (`fiches/*.yml`), `triggers-and-windows.yml`, `weighting.yml` |
| `v3/data/` | sorties commitées : bulletins, events-log, **decision-log**, performance |
| `v3/audit/` | audits croisés (elon / ia / data) |
| `v3/docs/reco/` | décisions d'architecture |
| `v3/ACTIVATION.md` · `v3/README.md` · `v3/KILL-CRITERION.md` | activation, archi, règle d'arrêt |
| `project-context.md` | contexte technique (résumé) — réf produit complète = vault `Bourse/Bourse.md` |
| `legacy/` | ancienne app (bot turbo) — **archivée** |
| `.claude/`, `CLAUDE.md`, `update.sh` | framework Gradient Agents |

## Architecture

GitHub Actions (workflow `cycle-decision`, cron 3×/jour) + **git-as-storage** (tout commité). Sans VPS, sans Cowork. DeepSeek (extraction news), Twelve Data / CFTC / EIA / Open-Meteo (données), Telegram/Argos (émission, post-shadow).

## Tests

```bash
python -m pytest v3/tests/   # 217 tests
```
