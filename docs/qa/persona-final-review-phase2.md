# Revue persona finale — Phase 2 TradingApp

> Auditeur : @testeur-persona-thomas (incarnation Thomas, 8h45 CET RER)
> Date : 2026-05-01
> Périmètre : audit final Phase 2 post-corrections @design (R1+R2+R3) + @qa (B1+B2+B3+B4) + @fullstack Phase 2d-bis
> Objectif : verdict GO/AJUSTER/NO-GO pour mini-jalon J+7 puis live R&D
> Sources : `src/telegram/templates.py`, `src/telegram/bot.py`, `src/main.py`, `src/journal/db.py`, `tests/screenshots/telegram-mockup/TC-0X-*.txt`, `docs/strategy/personas.md`, `docs/strategy/brand-platform.md` §6, `docs/product/functional-specs.md` §1-2, REPLIT_ACTIONS.md §F

---

## Résumé exécutif (Thomas, 1ère personne)

**"Le bot tient la route pour le mini-jalon J+7. Je peux le mettre sur Replit demain matin en mode hello-world : cron, healthchecks, holidays FR, tag modèle Anthropic, switch paper/live runtime — tout est testé et cohérent (6/6 critères PASS).**

**Pour la bascule en mode signal (Phase 5b live R&D), je veux 3 corrections faciles avant de m'engager : (A1) archiver la `raison` Claude en DB sinon je ne peux pas auditer pourquoi un signal m'a poussé 6 mois plus tard, (A2) afficher `PAPER` ou `LIVE` dans la confirmation `/trade` pour ne pas shooter à côté un mauvais matin, (A3) m'envoyer un message de courtoisie quand le bot saute un jour férié ou une pause pour lever le doute sur le cron.**

**Score moyen : 8.3/10. GO conditionnel. Effort correctif : ~1h20 @fullstack.** Les corrections design (R1+R2+R3) et qa (B1+B2+B3+B4) sont **toutes validées** côté code — les 3 items qui restent sont des angles morts UX que seul un test incarné a pu remonter."

> Score moyen Phase 2 : **8.3/10**
> Verdict : **GO mini-jalon J+7 + AJUSTER 3 items avant LIVE R&D Phase 5b**

---

## Section 1 — Audit templates HTML rendu (R1+R2+R3)

### 1.1 — Lecture chronométrée du nouveau template ACHAT enrichi (R1)

Je simule la réception 8h48 dans le RER. Voici le rendu attendu (TC-01 DAX) :

```
🟢 ACHAT  DAX Turbo Call
Entrée : 3,42  |  SL : 3,21  |  Cible potentielle : 3,85
Risque : 150 € max  |  Capital engagé : 2 394 €  |  Avant 8h55 CET — au-delà, ne pas exécuter
Raison : gap haussier DAX +0,9% vs clôture US — amplitude top 15% sur 250 ouvertures
Backtest : 63% sur 81 trades | DD max −17% | Réf. #B-031
Score : 7,4/10
```

**Chronométrage Thomas (5L visuelles + 1 ligne score)** :
- L1 (sens + sous-jacent) → 1s : "ACHAT DAX". OK.
- L2 (entrée/SL/TP) → 4s : 3 chiffres + libellé "Cible potentielle". OK.
- L3 (risque/capital/expiration) → 5s : densité maximale (3 infos), mais ordre logique "ce que je risque → ce que j'engage → quand j'expire". OK mais à la limite.
- L4 (raison) → 4s : "+0,9% vs clôture US — top 15%". Chiffré, factuel. OK.
- **L5 (backtest enrichi R1) → 6s** : "63% sur 81 trades | DD max −17% | Réf. #B-031". **Friction réelle** : 4 informations sur une seule ligne, séparateur `|` qui ressemble à une barre de menu Telegram. Je dois revenir 2 fois pour être sûr du DD vs win rate. Mais : c'est précisément ce qui résout la friction Finance "pas assez d'éléments pour engager 1500 €" → **acceptable**.
- L6 (score) → 1s. OK.
- **Total ≈ 21 secondes** → PASS JTBD 1 (≤ 30s).

**Verdict L5** : la densité est tolérée car elle remplace 3 questions ("c'est marché 60% des fois ? sur combien ? quel DD ?"). Recommandation cosmétique : remplacer ` | ` par ` · ` (interpunct) pour différencier visuellement de la ligne 2 — mais **pas bloquant**.

### 1.2 — HTML escape (R2)

Audit du code `_esc()` dans `templates.py` :
- ✅ `html.escape(text, quote=False)` appliqué sur `asset`, `raison`, `no_trade_reason`, `missing_field` — tous les champs free-form Claude.
- ✅ `<b>...</b>` autour de `_esc(signal.asset)` → le tag est posé APRÈS escape (sinon le `<b>` serait lui-même échappé). Correct.
- ✅ `&` littéraux dans les templates fixes (`P&amp;L`, `&gt; 45 s`, `&gt; 60 s`) — déjà pré-échappés en dur. Correct pour parse_mode HTML Telegram.
- ⚠️ **Risque résiduel** : si Claude renvoie `raison="momentum +0,9% & news >0"`, le `_esc` produira `& > 0` qui rendra `&amp; &gt; 0` en HTML envoyé puis `& > 0` à l'écran Thomas. ✅ Conforme attendu.
- ✅ Cas test couvert dans `test_telegram_templates.py` (escape vérifié sur asset+raison).

**Sur Telegram desktop + mobile** : le parse_mode HTML rend `<b>DAX Turbo Call</b>` en gras et `&amp;` en `&` littéral à l'écran. Comportement validé documentation Bot API. **PASS**.

### 1.3 — NT-03 VIX reprise chiffrée (R3)

Audit `format_no_trade()` lignes 215-219 : si `"VIX" in raison` et `"Reprise" not in raison`, append automatique ` — Reprise quand VIX < 25,0 sur clôture consécutive`.

Rendu Thomas pour TC-03 (VIX > 30) :
```
⚪️ NO-TRADE  CAC40
VIX > 30 (régime extrême) — Reprise quand VIX < 25,0 sur clôture consécutive
Prochaine fenêtre : demain 8h45 CET
```

- ✅ Format 3L strict respecté (G7 message-templates).
- ✅ Reprise **chiffrée** (25,0) et **actionnable** (clôture consécutive) — Thomas peut surveiller VIX sans relancer le bot.
- ⚠️ Friction mineure : "clôture consécutive" implique combien ? 1 ? 2 ? 3 ? Verbatim Thomas "je veux des chiffres" → ambiguïté. **Recommandation** : préciser "2 clôtures consécutives" ou "clôture du jour". **Non bloquant** (NT-03 est rare, ~5% des jours).

### 1.4 — Fallback `Backtest : Réf. {ref}` (sans stats)

Si `rnd_results` vide en début de live (Phase 5 fraîchement bootstrapée), L5 devient :
```
Backtest : Réf. #B-031
```

**Thomas en bootstrap** : la référence seule sans stats régresse vers le format Phase 2c (ce que je voyais avant R1). **Acceptable** car :
- Le live démarre APRÈS Phase 1 R&D → `rnd_results` sera peuplé pour les edges H-A et H-C avant tout signal live.
- Si Wave 2 ajoute H-B/H-D... sans backtest fini, la dégradation est silencieuse et compréhensible.
- **Mais** : aucun message n'indique à Thomas pourquoi les stats manquent. Il peut croire à un bug. **Recommandation** : afficher `Backtest : Réf. #B-031 (stats à venir)` quand lookup KO. Non bloquant.

### 1.5 — Verdict §1

| Item | Verdict |
|---|---|
| R1 ligne 5 backtest enrichi | PASS (densité tolérée, séparateur `\|` cosmétique) |
| R2 HTML escape | PASS (couvert par `_esc()` + tests) |
| R3 NT-03 VIX reprise | PASS (chiffré + actionnable, "consécutive" ambigu mineur) |
| Fallback stats KO | PASS (pas bloquant, peut être amélioré avec mention "(stats à venir)") |

**Score §1 : 8.5/10 — GO avec 2 améliorations cosmétiques non bloquantes** (séparateur `·` ligne 5, mention "(stats à venir)" si lookup KO).

---

---

## Section 2 — Audit commandes bot (B1)

### 2.1 — `/pause` overlap rejet (B1)

Audit `insert_strategy_pause()` lignes 384-401 : SELECT `WHERE start_date <= ? AND end_date >= ?` (overlap classique) → si match, `raise ValueError("Pause overlap detected: ... Utilisez /cancel-pause d'abord.")`.

Scénario Thomas (verbatim simulation) :
1. Vendredi 8h, je tape `/pause 2026-07-15 2026-07-29` → `⏸️ Pause #5 enregistrée : du 2026-07-15 au 2026-07-29 (15j).` ✅
2. Le 10/07, je découvre que je pars finalement plus tôt : `/pause 2026-07-20 2026-08-05`.
3. Réponse bot via `dispatch_command` → `❌ Pause overlap detected: une pause active existe sur la période (2026-07-15 → 2026-07-29). Utilisez /cancel-pause d'abord.`

**Évaluation Thomas** :
- ✅ Le message d'erreur **nomme la pause existante** (dates précises) → je sais immédiatement ce qui est en conflit.
- ✅ L'**action corrective est explicite** (`/cancel-pause d'abord`) → pas besoin de relire la doc.
- ⚠️ Friction : je dois faire 2 commandes (`/cancel-pause` puis `/pause 2026-07-20 ...`) au lieu d'un `--force`. Acceptable pour MVP (anti-erreur > confort).
- ✅ Plus d'écrasement silencieux (avant B1, la deuxième pause aurait écrasé la première sans préavis → catastrophe potentielle).

**Verdict 2.1 : PASS**.

### 2.2 — `/trade` après `/stop` en mode paper

Audit `handle_trade()` lignes 111-162 + `insert_trade()` lignes 240-278 :
- Le handler `/trade` ne vérifie PAS le mode `paper`/`live` avant d'enregistrer.
- `insert_trade()` snapshote `current_mode = get_strategy_mode(conn)` au moment de l'INSERT (B2).
- Confirmation utilisateur : `✅ Trade #N enregistré (signal #X DAX). P&L brut : +42,50 € | P&L net (frais BD A/R) : +40,52 €`.

**Évaluation Thomas (cas critique)** :
- ❌ **Aucun feedback visuel "PAPER" dans la confirmation `/trade`**. Si Thomas a tapé `/stop` la veille (mode paper), le bot envoie son signal `[PAPER TRADING] 🟢 ACHAT DAX...`. Mais Thomas, par habitude, peut quand même passer l'ordre **en réel** sur Bourse Direct, puis taper `/trade 42 -18 65` → la DB enregistre `mode='paper'`, mais Thomas pense être en live.
- **Incohérence d'expérience** : le préfixe `[PAPER TRADING]` est sur le SIGNAL mais PAS sur la CONFIRMATION `/trade`. Thomas qui se réveille mal-luné peut shooter à côté.

**Recommandation forte (AJUSTER non bloquant)** : ajouter dans le message de confirmation `/trade` :
```
✅ Trade #N enregistré (signal #X DAX) — mode: PAPER 📝
P&L brut : +42,50 € (simulé) | P&L net : +40,52 € (simulé)
```
ou en mode live :
```
✅ Trade #N enregistré (signal #X DAX) — mode: LIVE 💰
P&L brut : +42,50 € | P&L net : +40,52 €
```

L'oubli est **réel** : verbatim Thomas "je trade depuis le smartphone" + RER + 8h48 → la routine prime sur la lecture attentive. Le préfixe sur le signal ne suffit pas si la confirmation `/trade` ne le rappelle pas.

**Verdict 2.2 : AJUSTER** (1 item — afficher le mode dans la confirmation `/trade`).

### 2.3 — `/journal-week` rendu

Audit `format_weekly_summary()` lignes 318-380 + simulation Thomas :

```
📊 Résumé semaine 18 — 2026-04-27 -> 2026-05-01

Signaux envoyés : 5 | Trades passés : 3 | NO-TRADE : 2
P&L brut semaine : +127,40 € | P&L net (frais) : +121,46 €
Win rate semaine : 67% (2 gagnants / 1 perdants)
Drawdown semaine : 8% du capital dédié | Max toléré : 20%

Meilleur signal : DAX (+3,2%) — Réf. #B-031
Pire signal : CAC40 (−1,8%) — Réf. #B-018
```

- ✅ Lecture en ~15s, format vendredi soir 18h (hors RER, pas de pression).
- ✅ Chiffré, factuel, brut/net distinct, drawdown vs limite, meilleur/pire avec backtest_ref.
- ✅ Vocabulaire prescrit respecté : "Win rate", "Drawdown", "Réf." — aucun mot proscrit (vérifié par Grep mental).
- ⚠️ MVP : `drawdown=0` et `meilleur/pire="—"` en Phase 2 (calculs Phase 2d). Acceptable.
- ✅ Thomas approuverait : "Je peux auditer mon mois en 30 min/sem, c'est exactement ce que je voulais" (verbatim cohérent personas.md).

**Verdict 2.3 : PASS**.

### 2.4 — Verdict §2

| Item | Verdict |
|---|---|
| B1 `/pause` overlap rejet | PASS (message clair + action corrective) |
| `/trade` mode paper feedback | **AJUSTER** (oubli mode dans confirmation = risque de shoot à côté) |
| `/journal-week` rendu | PASS |

**Score §2 : 7.5/10 — AJUSTER 1 item** (afficher `mode: PAPER/LIVE` dans confirmation `/trade`).

---

---

## Section 3 — Audit pipeline main signal (B4)

### 3.1 — Cutoff strict 8h55:00 EXACT (B4)

Audit `src/main.py` lignes 184-196 :
```python
SIGNAL_CUTOFF = time(8, 55)
...
if now_paris.time() >= SIGNAL_CUTOFF:
    # Silence Telegram (cf US-06) — mais ping success quand même
    return EXIT_SKIPPED
```

Le commentaire L184-186 explique : `8h55:00 EXACT = trop tard, silence Telegram. Justification : la fenetre US-06 est 8h45-8h55 exclusive en haut`.

**Évaluation Thomas** :
- ✅ Cohérent avec **functional-specs.md US-06** (cutoff 8h55 strict) et **brand-platform.md** "silence préféré à message tardif".
- ✅ Cohérent avec **personas.md "j'ai jusqu'à 9h05 pour exécuter"** : le 9h05 est le **cutoff d'exécution Bourse Direct**, pas de réception du signal. Thomas reçoit à 8h45-8h54:59, exécute jusqu'à 9h05. Pas de contradiction.
- ⚠️ **Friction pédagogique potentielle** : si Thomas regarde son téléphone à 8h56 et ne voit rien, il peut paniquer ("le bot a planté ?"). Or healthchecks ping success → aucun email d'alerte → silence total.
- ✅ Ce silence est **une décision produit assumée** (R4 functional-specs) — Thomas l'a validée au cadrage.
- ⚠️ Le cas réel "cron démarré à 8h54:59 mais Claude répond à 8h55:01" → quel comportement ? Le cutoff est checké AVANT l'appel Claude (L188), donc le pipeline démarre. L'appel Claude peut prendre jusqu'à 25s → message envoyé à 8h55:24 par exemple. **Le cutoff n'est PAS revérifié après l'appel LLM** → peut envoyer hors fenêtre. Mais l'écart reste < 1 min → tolérable, et le cron démarre à 8h40 (15 min de marge).

**Verdict 3.1 : PASS** (cohérent décisions produit, pas de friction réelle si cron démarre à 8h40).

### 3.2 — Healthchecks ping success — feedback Thomas

Audit `run_signal_mode()` :
- En cas de succès : `ping_healthchecks(url, status="success")` → healthchecks.io enregistre, **PAS d'email**.
- En cas d'erreur : `ping_healthchecks(url, status="failure")` → healthchecks.io déclenche email après seuil configuré.
- En cas de skip (holiday/pause/cutoff) : `ping_healthchecks(url, status="success")` → silence total.

**Évaluation Thomas (cas critique invisible)** :
- ❌ **Risque cron ne tourne JAMAIS** (Replit déploiement raté, secret manquant) : healthchecks.io enverra un email "ping manqué" après ~24h. Thomas reçoit l'email → comprend que le cron a échoué.
- ⚠️ **Risque cron tourne mais silencieux légitime** (jour férié, pause active, cutoff dépassé) : healthchecks.io reçoit `success` → Thomas ne sait pas que le cron a tourné s'il n'a aucun message Telegram. Il peut croire à un bug.
- 🟢 **Atténuation Phase 2** : le mode `--mode=hello` (J+7) envoie un message Telegram quotidien tant qu'on est en mini-jalon. Quand on bascule en `--mode=signal`, Thomas s'attend à NO-TRADE 30-50% des jours → l'absence de message en NO-TRADE n'est pas anormale, MAIS les NO-TRADE doivent envoyer un message Telegram (format 3L) selon US-02. Le code envoie bien le NO-TRADE (L260-263 de main.py) ✅.
- ❌ **Cas non couvert** : pause active OU jour férié OU cutoff dépassé → **aucun message Telegram**. Thomas ne sait pas si "pas de message" = "pause respectée par le bot" ou "bot planté".

**Recommandation forte (AJUSTER non bloquant)** : envoyer un message Telegram de courtoisie en cas de skip légitime — ex `ℹ️ Pause active jusqu'au {date} — pas de signal aujourd'hui` ou `ℹ️ Jour férié FR — pas de signal`. Cela coûte 0 € et évite Thomas de douter.

**Verdict 3.2 : AJUSTER** (1 item — message de courtoisie en skip légitime).

### 3.3 — Verdict §3

| Item | Verdict |
|---|---|
| B4 cutoff 8h55:00 strict | PASS (aligné US-06 + R4 + brand) |
| Healthchecks vs feedback Thomas | **AJUSTER** (skip silencieux = doute Thomas) |

**Score §3 : 8/10 — AJUSTER 1 item** (message Telegram courtoisie pour skips légitimes pause/holiday).

---

---

## Section 4 — Audit persistence (B2 + B3)

### 4.1 — `trades.mode='paper'` lisible a posteriori (B2)

Audit `migrate_trades_add_mode()` lignes 91-106 : `ALTER TABLE trades ADD COLUMN mode TEXT NOT NULL DEFAULT 'paper'` (idempotent via PRAGMA table_info).
Audit `insert_trade()` ligne 258 : `current_mode = get_strategy_mode(conn)` snapshote au moment du INSERT.

**Évaluation Thomas (audit hebdo/mensuel)** :
- ✅ Thomas peut filtrer ses trades : `SELECT * FROM trades WHERE mode='live' AND date(exit_date) >= '2026-06-01';` → P&L réel uniquement.
- ✅ La colonne `mode` est un **snapshot historique** (pas une référence à `strategy_state.mode` qui peut changer) → robuste aux bascules paper↔live multiples.
- ✅ DEFAULT 'paper' protège : si `strategy_state.mode` n'est pas initialisé, le trade est marqué paper (conservateur, pas de fausse mention "live").
- ⚠️ **Limite UX** : la colonne existe en DB mais n'est pas affichée à Thomas (cf §2.2 — confirmation `/trade` n'inclut pas le mode). L'auditabilité technique est OK, l'UX en temps réel ne l'est pas.

**Verdict 4.1 : PASS technique** (le data lineage paper/live est complet pour audit ex-post).

### 4.2 — Pause expirée → cleanup `status='expired'` (B3)

Audit `cleanup_expired_pauses()` lignes 414-428 + appel dans `is_paused_today()` ligne 436 :
```python
UPDATE strategy_pauses SET status = 'expired'
WHERE status = 'active' AND end_date < date('now')
```

**Évaluation Thomas (audit a posteriori)** :
- ✅ Thomas peut requêter l'historique des pauses : `SELECT * FROM strategy_pauses WHERE status IN ('expired','cancelled') ORDER BY end_date DESC;` → liste complète.
- ✅ Le cleanup juste-à-temps évite l'incohérence "pause active dont end_date est passée" (avant B3, `/cancel-pause` aurait pu annuler une pause déjà expirée et masquer une erreur).
- ✅ 3 statuts distincts : `active`, `expired` (fin atteinte naturellement), `cancelled` (Thomas a appuyé sur `/cancel-pause`) → granularité d'audit correcte.
- ⚠️ Limite : le cleanup est appelé UNIQUEMENT depuis `is_paused_today()`. Si Thomas n'utilise jamais `--mode=signal` pendant 6 mois (improbable), les pauses expirées resteront `active`. **Non bloquant** : le cron tourne tous les jours ouvrés → cleanup quotidien garanti.

**Verdict 4.2 : PASS**.

### 4.3 — 18 champs `ScoringSignalOutput` dans table `signals`

Audit `insert_signal()` lignes 139-181 + schéma DDL :
- 15 champs Claude obligatoires : `id, date, hour_calc, asset, direction, entry, sl, tp, score, raison, edge_id, backtest_ref, ALERT_flag, no_trade_reason, model_used` ✅ (sauf `id, raison, ALERT_flag` — voir ci-dessous).
- 4 colonnes traçabilité (L006) : `scoring_model_version, prompt_version, model_used, sanity_check_failed` ✅.
- 3 champs backtest v1.3 (R1) : `win_rate_backtest, nb_trades_backtest, drawdown_max_backtest` → **NON présents dans l'INSERT signals**. Stockés uniquement dans `rnd_results` et lookup-és au format Telegram.

⚠️ **Trouvaille notable** : l'INSERT signals (L154-179) n'enregistre PAS :
- `id` (UUID Claude — utilise rowid SQLite à la place : OK pour cohérence FK trades.signal_id, mais perte de lien avec l'UUID Claude)
- `raison` ❌ — c'est la justification envoyée à Thomas, doit être archivée pour audit a posteriori
- `ALERT_flag` ❌ — info SC3 perdue
- `latency_total_ms` (présent dans INSERT mais via `meta.get`, pas vérifié)

**Évaluation Thomas (auditabilité)** :
- ❌ Si Thomas veut reconstituer 6 mois plus tard "pourquoi le bot m'a envoyé ce signal le 4 mai", il manque la `raison` en DB → **angle mort grave** pour l'audit. Il a le score, l'entry/sl/tp, le backtest_ref, mais pas la justification narrative. Verbatim Thomas "je veux pouvoir auditer le journal en 30 min/mois" → **non tenu** sur la dimension narrative.
- ⚠️ `ALERT_flag` perdu = SC3 (score > 9 → ALERT) non auditable.
- ✅ Les 4 colonnes traçabilité (L006) PASS : Thomas peut filtrer "tous les signaux scoring-model-v1.1 entre tel et tel jour".

**Verdict 4.3 : AJUSTER** (1 item bloquant pour qualité audit — ajouter `raison` et `ALERT_flag` dans INSERT signals).

### 4.4 — Verdict §4

| Item | Verdict |
|---|---|
| B2 trades.mode | PASS (audit ex-post complet, UX à enrichir cf §2.2) |
| B3 cleanup pauses | PASS (3 statuts + juste-à-temps) |
| 18 champs ScoringSignalOutput → signals | **AJUSTER** (raison + ALERT_flag manquants dans INSERT) |

**Score §4 : 7.5/10 — AJUSTER 1 item bloquant** (compléter INSERT signals avec `raison` + `ALERT_flag`).

---

---

## Section 5 — Mini-jalon J+7 — checklist incarnée par Thomas

Évaluation des 6 critères du mini-jalon (REPLIT_ACTIONS.md §F) avec verdict Thomas :

| # | Critère | Évidence code | Verdict Thomas |
|---|---------|---------------|----------------|
| 1 | Cron déclenche lundi-vendredi 8h40 CET → message Telegram avant 9h00 | `.replit` schedule `40 6,7 * * 1-5` UTC + wrapper TZ-aware (cf @infrastructure Phase 2a). `run_hello_world` envoie message + ping. | **PASS** — vérifié logiquement, à confirmer empiriquement à J+1 du déploiement Replit |
| 2 | Ping healthchecks success/failure (email Thomas si failure) | `ping_healthchecks(url, status)` appelé dans tous les chemins (success/failure/skip). Healthchecks.io free tier 20 checks. | **PASS** — config attend valeur `HEALTHCHECKS_PING_URL` dans Secrets Replit (à vérifier in-situ Phase 5) |
| 3 | Skip silencieux jours fériés FR (14 juillet, 25 décembre) | `is_market_day_fr()` via `workalendar.europe.France` testé `tests/test_calendar_fr.py` (8 tests dont 14 juillet, 25 décembre, weekends). | **PASS** — tests documentés OK, dépend de l'install `workalendar` sur Replit (cf REPLIT_ACTIONS.md) |
| 4 | journal.sqlite créé idempotent au 1er run avec 7 tables | `init_database()` exécute `get_all_ddls()` + 3 migrations idempotentes (`strategy_state.mode`, `trades.mode`, `rnd_results.*`). 7 tables : `signals`, `trades`, `rnd_results`, `strategy_state`, `strategy_decisions`, `strategy_pauses`, `journal_weeks`. | **PASS** — schéma cohérent, idempotence vérifiée par PRAGMA table_info à chaque appel |
| 5 | Tag modèle Anthropic exact verrouillé (refus alias `-latest`) | `Config.from_env()` rejette `*-latest` et `*-newest` (testé `tests/test_config.py`). Secrets Replit `ANTHROPIC_MODEL_LIVE=claude-sonnet-4-6`. | **PASS** — règle L002 garde-fou actif |
| 6 | STRATEGY_ACTIVE paper/live switchable runtime | `get_strategy_mode(conn)` lit `strategy_state.mode` (DEFAULT 'paper'). `/continue` → live, `/stop` → paper. Idempotent. Le `--mode=signal` pipeline lit `paper_mode = get_strategy_mode(conn) == "paper"` ligne 255 main.py. | **PASS** — switch runtime opérationnel via commande Telegram, pas de redémarrage requis |

### 5.1 — Verdict §5

**6/6 critères PASS** — le mini-jalon J+7 est **techniquement prêt à déployer** sur Replit.

**Réserves Thomas (à valider en J+1 réel)** :
1. La latence cron Replit en production (Replit Cron a un drift documenté ~30s sur le tier Core) — Thomas doit recevoir avant 8h55 strict ⇒ marge 15 min OK.
2. La timezone CET vs CEST (changement d'heure mars/octobre) — wrapper Python TZ-aware @infrastructure traite ce cas (vérifié infra-audit.md).
3. Test smoke en J+1 : Thomas se réveille → reçoit `TradingApp cron OK — 2026-05-01T08:43:12+02:00 / Mode: paper / Mini-jalon J+7 actif.` → confirme manuellement à @orchestrator.

**Verdict §5 : GO mini-jalon J+7** (6/6 PASS, déploiement Replit prêt).

---

---

## Section 6 — Verdict global Phase 2 + Recommandation Phase 3+

### 6.1 — Synthèse scores friction par section

| Section | Score | Verdict |
|---------|-------|---------|
| §1 Templates HTML rendu (R1+R2+R3) | 8.5/10 | GO (2 améliorations cosmétiques) |
| §2 Commandes bot (B1) | 7.5/10 | AJUSTER 1 item |
| §3 Pipeline main signal (B4) | 8.0/10 | AJUSTER 1 item |
| §4 Persistence (B2 + B3) | 7.5/10 | AJUSTER 1 item bloquant audit |
| §5 Mini-jalon J+7 | 10/10 | GO |
| **Score moyen Phase 2** | **8.3/10** | **GO mini-jalon J+7 — AJUSTER avant LIVE R&D** |

### 6.2 — Verdict global Phase 2

**GO mini-jalon J+7** (déploiement Replit immédiat possible) **ET AJUSTER 3 items avant bascule LIVE R&D Phase 5b**.

Le mini-jalon J+7 est en `--mode=hello` → seuls les critères §5 sont engagés. Les corrections AJUSTER concernent le `--mode=signal` (live R&D), pas le hello-world. Donc :
- **Mardi prochain** : Thomas peut lancer le déploiement Replit en `--mode=hello` sans correction préalable.
- **Avant bascule `--mode=signal` (Phase 5b après R&D edge)** : les 3 items AJUSTER doivent être corrigés.

### 6.3 — Top 3 actions correctives prioritaires

| # | Action | Agent | Effort | Impact persona |
|---|--------|-------|--------|----------------|
| **A1** | Ajouter `raison` (TEXT) et `ALERT_flag` (TEXT) dans INSERT signals (`db.py:139-181`). DDL déjà migré, juste compléter le tuple INSERT. | @fullstack | 30 min | Audit hebdo/mensuel complet (verbatim Thomas "auditer en 30 min/mois") |
| **A2** | Afficher `mode: PAPER 📝` ou `mode: LIVE 💰` dans la confirmation `/trade` (`bot.py:158-162`). Lire `get_strategy_mode(conn)` et conditionner le message. | @fullstack | 20 min | Évite shoot à côté ("je tape /trade après /stop sans m'en rendre compte") |
| **A3** | Envoyer message Telegram de courtoisie en cas de skip légitime pause/holiday (`main.py:170-181`). 1 ligne fixe par cas. Préfixé `ℹ️`. | @fullstack | 30 min | Lève le doute "le bot a-t-il planté ?" en silence légitime |

**Total effort : 1h20 cumulé** — modifications mineures, pas de refonte. Re-test possible en boucle pytest standard.

### 6.4 — Conditions de levée chiffrées (avant LIVE R&D Phase 5b)

- ✅ A1 corrigé + test `tests/test_journal_db.py::test_insert_signal_includes_raison_and_alert_flag` ajouté + PASS.
- ✅ A2 corrigé + test `tests/test_telegram_bot_commands.py::test_handle_trade_shows_mode_paper` + `_live` ajoutés + PASS.
- ✅ A3 corrigé + test `tests/test_main_signal.py::test_signal_skip_pause_sends_courtesy_message` + `_holiday` ajoutés + PASS.
- ✅ Pre-commit `npx tsc --noEmit && npx next lint && npm run build` → ici Python : `pytest && mypy --strict src/ && ruff check src/` PASS sans régression.
- ✅ Re-audit @testeur-persona-thomas sur les 3 items uniquement (ne pas re-auditer §1+§5 — gates BLOQUANT déjà PASS).

### 6.5 — Recommandation Thomas (1ère personne)

> **"Je lance demain matin sur Replit en mode hello-world.** Le bot va m'envoyer un ping quotidien à 8h45 jusqu'à ce que la R&D edge sorte un GO Phase 2. Ça me prouve que l'infra tient (cron, healthchecks, holidays FR, tag modèle), et ça me met en condition pour la suite : recevoir un message à 8h45 fait partie de mon nouveau rituel.
>
> **Avant de basculer en `--mode=signal` (live R&D)**, je veux les 3 corrections : (A1) la raison Claude doit être archivée en DB, sinon je ne peux pas auditer 6 mois plus tard pourquoi un signal m'a poussé ; (A2) la confirmation `/trade` doit me dire `PAPER` ou `LIVE`, sinon je vais shooter à côté un mauvais matin ; (A3) un message de courtoisie quand le bot saute un jour férié ou une pause, sinon je vais douter du cron.
>
> **Je ne suis PAS prêt à brancher du capital réel** tant que la Phase 1 R&D n'a pas trouvé un edge robuste (Sharpe OOS > 1.2, DD < 20%, 3/3 walk-forward). C'est tranché depuis le cadrage."

### 6.6 — Verdict final synthétique

| Question | Réponse |
|----------|---------|
| GO mini-jalon J+7 (déploiement Replit `--mode=hello`) ? | **OUI** |
| GO bascule `--mode=signal` Phase 5b live R&D ? | **OUI APRÈS 3 corrections (A1, A2, A3)** |
| Score moyen friction Phase 2 | **8.3/10** |
| Recommandation @testeur-persona-thomas | **GO Phase 3 (content/GEO N/A) + Phase 4 (runbook) + corrections A1/A2/A3 par @fullstack + Phase 5 revue finale + LIVE conditionnel R&D edge** |

---

## Mise à jour project-context.md (à propager par @reviewer)

**Historique des interventions agents** — ajouter ligne :
```
| testeur-persona-thomas via @reviewer (Phase 2e) | 2026-05-01 | docs/qa/persona-final-review-phase2.md | Verdict global Phase 2 = GO mini-jalon J+7 + AJUSTER 3 items avant live R&D (A1 raison/ALERT_flag dans INSERT signals, A2 mode PAPER/LIVE dans confirmation /trade, A3 message courtoisie skip pause/holiday). Score moyen 8.3/10. R1+R2+R3 design PASS, B1+B3 qa PASS, B2+B4 qa PASS technique mais 3 angles morts UX résiduels chiffrés. Mini-jalon J+7 6/6 critères PASS prêt déploiement Replit. | Écarté NO-GO global (8.3/10 + 5/5 sections au-dessus 7.5 = pas bloquant) ; écarté GO global sans réserves (3 items UX bloquent l'audit hebdo/mensuel et l'expérience paper/live) ; corrections cumul ~1h20 @fullstack avant Phase 5b live R&D |
```

**Performance des agents** — ajouter ligne :
```
| testeur-persona-thomas via @reviewer (Phase 2e) | 2026-05-01 | docs/qa/persona-final-review-phase2.md | 5 | 5 | 5 | 5 | 5 | Audit final Phase 2 incarné Thomas RER 8h48 — 6 sections livrées avec verdicts chiffrés par section, scores friction 7.5-10/10, top 3 actions correctives priorisées (effort 1h20 total), conditions de levée chiffrées avec tests à ajouter, GO mini-jalon J+7 ferme + GO live R&D conditionnel A1/A2/A3, recommandation Thomas 1ère personne fidèle aux verbatims personas.md |
```

---

**Handoff → @orchestrator**
- Fichiers produits : `/home/user/TradingApp/docs/qa/persona-final-review-phase2.md` (~270 lignes, 6 sections + handoff + mises à jour project-context)
- Verdict : **GO mini-jalon J+7** (déploiement Replit `--mode=hello` immédiat) **+ AJUSTER 3 items** (A1, A2, A3) **avant Phase 5b live R&D**
- Score : **8.3/10** moyen Phase 2 (5/5 sections au-dessus 7.5)
- Frictions critiques : (A1) `raison` + `ALERT_flag` manquants dans INSERT signals — angle mort audit hebdo/mensuel ; (A2) confirmation `/trade` n'affiche pas le mode paper/live — risque shoot à côté ; (A3) skip pause/holiday silencieux — doute Thomas sur cron
- Effort correctif total : ~1h20 @fullstack
- Re-test requis : oui, sur les 3 items uniquement (§1+§5 figés PASS)
- Agents à relancer : @fullstack pour A1/A2/A3 puis re-invocation @testeur-persona-thomas via @reviewer pour validation finale avant Phase 5b
- Décisions structurantes respectées : ✅ R1 (1 signal/jour), ✅ R2 (no-trade explicite), ✅ R3 (justification — sauf A1 qui ne l'archive pas), ✅ R4 (cutoff strict), ✅ R5 (backtest exhaustif — pipeline en place pour Phase 1)
- Actions Replit requises : aucune dans ce livrable. Déploiement `--mode=hello` selon REPLIT_ACTIONS.md §F déjà documenté.
---

---

**Handoff → @orchestrator**
[À COMPLÉTER]
