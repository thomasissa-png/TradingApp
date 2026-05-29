# Reco Elon — TradingApp v3, architecture minimale

> Avis consultatif, first principles. Thomas tranche.

## TL;DR

Tu construis une fusée Falcon Heavy pour livrer une pizza. Le pivot du 27/05 a déjà tranché : **pas d'edge informationnel sur sources publiques pour un retail en exécution manuelle**. Donc 31 sources + ingestion 24/7 + extraction LLM = théâtre. La valeur du bulletin vient des **règles de scoring + prix + 3-5 séries macro structurées**, pas du fait d'avoir lu Reuters à 3h12 du matin.

**Coupe 80 % du pipeline. Garde le scoring. Mode shadow en 2 semaines, pas 2 mois.**

## Le vrai problème (first principles)

Question : qu'est-ce qui fait bouger une cellule LONG/SHORT à 24h/7j/1m ?
- Prix & dérivés techniques (momentum, vol, RSI, MA) → **Twelve Data suffit**.
- Données macro structurées (EIA stocks pétrole, CFTC COT, USDA WASDE, VIX, DXY, courbe taux) → **APIs directes, pas de LLM**.
- Sentiment/news → marginal à 24h+, **zéro edge** vs algos HFT. C'est ça la conclusion du pivot.

Si la décision est 100 % règles déterministes (et elle l'est), alors les news servent à quoi exactement ? À nourrir un `events-log` que **personne ne lit dans le scoring**. C'est un musée.

## Ce qu'on SUPPRIME (sans dégrader le KPI)

| Composant | Verdict | Raison |
|---|---|---|
| Ingestion 24/7 | **SUPPRIMER** | Tu décides à 7h. Un poll à 6h30 suffit. 24/7 = ego, pas valeur. |
| 31 sources RSS | **COUPER à ≤8** | EIA, CFTC, USDA/WASDE, NOAA (cacao/café/blé), FRED (macro US), ECB (EUR), BLS (CPI/NFP), calendrier éco. Tout le reste = bruit corrélé. |
| Extraction LLM DeepSeek | **SUPPRIMER en v1** | Si scoring ne consomme pas les events, l'extraction ne crée pas de valeur. Économie : 6 €/mois + 1 brique mobile + 1 mode d'échec. Réintroduire SI un critère prouve un lift mesurable sur Brier. |
| `events-log` | **SUPPRIMER en v1** | Conséquence directe du point au-dessus. |
| `news_collector.py`, `extractor.py`, `agent_news.py` | **ARCHIVER** | Code mort dans la v1 cible. |
| Google Drive comme DB | **SUPPRIMER** | Markdown sur Drive = base de données déguisée. Lent, fragile, pas requêtable. |
| Manager (audit hebdo LLM) | **REPORTER** | Tant que t'as <30 conclusions, rien à auditer. Toi + un notebook = audit. |
| Journaliste comme "agent" | **DÉCONSTRUIRE** | C'est un script de 50 lignes : prix T+H vs prix T, MAJ table perf. Pas un agent. |
| Argos comme "agent" | **DÉCONSTRUIRE** | C'est `requests.post(telegram_url, ...)`. 10 lignes. |

## Architecture minimale (la v1 qui tient sur une serviette)

**1 repo. 1 langage (Python). 1 scheduler. 1 DB. 1 cron.**

- **Compute** : GitHub Actions (cron). Gratuit, scheduler intégré, secrets gérés, logs gardés, déploiement = `git push`. Pas de VPS à patcher, pas d'uptime à surveiller. Si une run échoue, GitHub te mail.
- **DB** : SQLite versionné dans le repo (ou Turso/LiteFS si tu veux du cloud SQLite). 36 cellules/jour × 365 = 13k lignes/an. Une table `criteres_courants`, une `bulletins`, une `performance`. Fin.
- **Code** : 4 scripts purs, pas d'agents.
  - `fetch_prices.py` (Twelve Data → SQLite)
  - `fetch_macro.py` (5-8 APIs structurées → SQLite)
  - `score.py` (lit fiches actifs YAML + SQLite → 36 cellules → SQLite + markdown bulletin)
  - `measure.py` (compare conclusions échues, MAJ KPI)
- **Fiches actifs** : YAML (pas markdown), 12 fichiers, dans le repo. Critères + poids + signes versionnés via git. Change = PR = trace. Le "pas de modif silencieuse des poids" est résolu **par git**, pas par un process.
- **Secrets** : GitHub Actions secrets. Point.
- **Bulletin** : généré en markdown dans le repo + posté sur Telegram (à activer post-shadow). Shadow = bulletin commité + pas envoyé.

## Plan d'exécution (timeline agressive)

| Semaine | Livraison |
|---|---|
| S1 | Repo propre, SQLite schema, `fetch_prices.py` + `fetch_macro.py` (3 sources prioritaires : EIA, CFTC, FRED), 3 fiches YAML (Brent, Or, S&P). |
| S2 | `score.py` + `measure.py`, GitHub Actions cron 6h30 UTC, premier bulletin shadow committé. |
| S3-S6 | Étendre aux 12 actifs, calibrer poids sur données historiques (backfill Twelve Data), monitorer Brier. |
| S6+ | SI Brier < 0,25 sur 30 conclusions → activer Telegram. SINON → ajuster poids ou tuer un actif. |

## Coût mensuel cible

- GitHub Actions : 0 €
- Twelve Data : déjà payé
- DeepSeek : 0 € (supprimé v1)
- Telegram : 0 €
- Domaine/hébergement : 0 €
- **Total : 0 € incrémental.** Vs ~10-15 €/mois VPS + 6 € LLM aujourd'hui.

## Ce qu'on REPORTE (pas mort, juste pas v1)

- Re-introduction LLM pour 1-2 critères qualitatifs (ex : "stress géopolitique" pondéré faible) → seulement si un backtest montre un lift sur Brier ≥ 2 points.
- Audit hebdo automatisé → quand >100 conclusions mesurées.
- UI/dashboard → jamais nécessaire. Markdown + git diff = ton dashboard.

## La question qui dérange

Si après 60 jours de shadow le Brier reste > 0,30, **le projet ne marche pas** — et c'est OK. Ton kill criterion doit être écrit AVANT de commencer, pas après. Sinon tu vas pondérer des indicateurs jusqu'à overfit le passé. Définis-le maintenant : Brier > X à J+60 → on arrête ou on pivote vers du pur copy-trading.

## Analogie SpaceX

Quand on a conçu le Raptor, on a viré 80 % des pièces du Merlin. Pas parce qu'elles étaient mauvaises — parce qu'elles n'étaient pas nécessaires. **The best part is no part.** Ton ingestion 24/7 sur 31 sources, c'est ton turbopompe inutile.

---

**Handoff** → Thomas (décideur). Ces recos sont des AVIS forts. Points à valider :
- Acceptes-tu de supprimer entièrement la couche news/LLM en v1 ?
- GitHub Actions + SQLite OK comme stack (vs alternative type Modal/Render) ?
- Kill criterion à J+60 défini avant S1 ?
