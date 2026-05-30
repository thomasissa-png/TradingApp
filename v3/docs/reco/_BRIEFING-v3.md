# Briefing technique — TradingApp v3 (pour reco d'architecture)

> ⚠️ Source de vérité = CE fichier (extrait du vault Drive de Thomas, fiches v3 du 27/05/2026).
> **IGNORER `project-context.md` à la racine du repo** : c'est l'ancienne app legacy (bot turbo 1 signal/jour, Replit), PAS le projet v3.

## La demande de Thomas

Re-lire les fiches projet, prendre du recul, et recommander **l'architecture technique la plus SIMPLE et la plus EFFICACE possible**, sachant qu'**on quitte les 3 maisons d'exécution actuelles** :
- ❌ **Cowork hub** (les 4 skills/agents planifiés Veilleur/Analyste/Journaliste/Manager)
- ❌ **Claude Code web** (la session de déploiement)
- ❌ **le VPS 82.165.168.92** (le service `news_collector` 24/7)

Tout ce qui était porté par ces 3 maisons doit trouver un nouveau toit, plus simple.

## L'objectif produit (inchangé)

Produire **chaque matin 7h CET un bulletin de positionnement directionnel** : 12 actifs × 3 horizons (24h/7j/1m) = **36 cellules**, chacune **LONG ou SHORT** (jamais neutre).
- Actifs : CAC 40, S&P 500, Nasdaq, EUR/USD, Brent, VIX, Or, Argent, Cuivre, Café, Cacao, Blé.
- Le système **ne trade jamais**. Thomas lit le bulletin, exécute manuellement chez Bourse Direct (turbos).
- **Mode shadow 30-90 j** : bulletin produit + mesuré, aucun envoi, le temps de calibrer.
- KPI : taux de réussite par cellule (cible >55 %) + Brier score (<0,25) sur 30 dernières conclusions.

## La méthode (point CLÉ pour simplifier)

- **L'Analyste = score pondéré par critères, 100 % RÈGLES déterministes. AUCUN LLM dans la décision.**
  Pour chaque actif : 5-15 critères chiffrables, chacun (valeur courante × poids × pertinence_horizon × signe) → somme → LONG si >0 sinon SHORT.
- Le **seul** usage LLM du système = **extraction des news** (DeepSeek V4 Flash) côté ingestion, pour remplir events-log. Coût observé ~6 €/mois (~5 000 events).
- Les "fiches actifs" (critères + poids + seuils) sont des **données/config** (12 fichiers markdown aujourd'hui dans le vault).

## Le pipeline fonctionnel (ce qui doit tourner)

| Étage | Fonction | Cadence | LLM ? |
|---|---|---|---|
| **Ingestion** | poll ~31 sources (RSS + APIs structurées EIA/CFTC/USDA/NOAA/Twelve Data) → dédup Jaccard → extraction DeepSeek → `events-log` | était 24/7 (15-60 min) | oui (extraction) |
| **Critères** | agréger events + prix Twelve Data → `criteres-courants` (valeur courante par critère × actif) | avant 7h | non |
| **Bulletin (Analyste)** | scorer les 12 fiches × 3 horizons → 36 cellules LONG/SHORT → `bulletin-quotidien` | 7h CET quotidien | non |
| **Mesure (Journaliste)** | comparer conclusions échues T+24h/7j/1m via Twelve Data → taux + Brier → `performance` | quotidien + 19h flips | non |
| **Émission (Argos)** | bulletin + score veille → Telegram | 7h (après shadow) | non |
| **Audit (Manager)** | audit hebdo qualité, propose ajustements de poids (Thomas tranche) | dim 21h | optionnel |

## Briques externes qui SURVIVENT (indépendantes des 3 maisons)

- **DeepSeek API** (clé déjà en main) — extraction news.
- **Twelve Data API** (plan Grow déjà payé) — prix marché, mesure perf.
- **Telegram Bot API** (Argos, à créer via BotFather) — délivrance.
- **Google Drive** (vault) — stockage actuel des .md (events-log, criteres-courants, fiches actifs, bulletins). À garder ou remplacer.
- **GitHub** — repo accessible, le VPS et ce conteneur atteignent github.com.

## Code déjà écrit (réutilisable)

Phase 2.1 en Python (`vps-news-collector/`) : `extractor.py` (DeepSeek), `news_collector.py` (RSS + pré-filtre finance), `agent_news.py` (loop), `config.py` (31 sources + poids), `drive_publisher.py` (I/O Drive). Encore à écrire : `criteres_calculator.py`, `triggers_classifier.py`, `source_monitor.py`, et le scoring Analyste.

## Contraintes / red lines

- Zéro invention de données (source DEAD → critère `n/a`, poids 0).
- Échec visible (source down, LLM en erreur → log + alerte, jamais masqué).
- Pas de modification silencieuse des poids/prompts (changement = trace + validation Thomas).
- Budget LLM : si coût mensuel projeté > 30 € → revenir à Thomas.
- Mono-utilisateur (Thomas seul). Pas d'UI web. Pas de scale.

## La question à laquelle répondre

**Quelle est l'architecture la plus simple et la plus efficace pour faire tourner ce pipeline SANS VPS, SANS Cowork, SANS Claude Code web ?**
Couvrir : où ça tourne (compute/scheduler), où vivent les données, comment c'est planifié (7h CET, intraday, hebdo), secrets, déploiement/maintenance, coût mensuel, et ce qu'on peut SUPPRIMER (recul first-principles). Trancher, pas de menu A/B/C non priorisé.
