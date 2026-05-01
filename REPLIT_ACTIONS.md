# REPLIT_ACTIONS — TradingApp Phase 2a

> Auteur : @infrastructure — Date : 2026-05-01
> **Lecteur cible : Thomas (persona)**. Ce document liste les actions manuelles à effectuer dans l'interface Replit pour rendre le mini-jalon J+7 opérationnel (cron quotidien jours ouvrés + push Telegram "hello world" + journal SQLite vide initialisé).
>
> **Pré-requis** : repo GitHub privé `TradingApp` accessible, compte Replit existant, smartphone avec Telegram installé.
>
> **Temps estimé total** : 45-60 min (setup initial + Secrets + Cron Deployment + healthchecks.io).
>
> **Ce que CE document NE fait PAS** : il ne configure pas l'edge R&D (Phase 1 séparée), il ne lance pas le live trading. Il prépare uniquement le rail technique J+7.

---

## A. Setup initial Replit Core (1 fois — ~10 min)

### A.1. Souscrire Replit Core
1. Aller sur [replit.com/pricing](https://replit.com/pricing) → choisir plan **Core (20 $/mois facturation annuelle, 25 $/mois mensuel)**.
2. Vérifier que le plan inclut **25 $/mois de crédits** + **Cron Deployments** + **Reserved VM Deployments**.
3. Renseigner mode de paiement (CB perso).

### A.2. Créer le Repl Python
1. Dashboard Replit → **Create Repl** → template **Python**.
2. Nom : `TradingApp` (ou laisser le nom GitHub si import direct).
3. Cocher **Private** (obligatoire — données financières personnelles, cf. `project-context.md`).

### A.3. Importer le repo GitHub privé
1. Dans le Repl → menu **Tools** (sidebar gauche) → **Git**.
2. Bouton **Connect to GitHub** → autoriser Replit à accéder au repo privé.
3. Sélectionner le repo `thomasissa-png/TradingApp` (ou le nom retenu).
4. Cliquer **Clone** → le repo est rapatrié dans `/home/runner/<repl-name>/`.
5. Vérifier que les fichiers `.replit`, `.gitignore`, `pyproject.toml` (à venir @fullstack) sont bien présents.

### A.4. Installer les dépendances Python (premier run)
1. Ouvrir le Shell Replit (onglet **Shell**).
2. Lancer : `uv sync` (si `pyproject.toml` + `uv.lock` présents) OU `pip install -r requirements.txt` selon ce que produit @fullstack.
3. Vérifier que Python 3.12+ est utilisé : `python --version` (doit retourner `Python 3.12.x` ou +).

> **Si erreur "uv not found"** : Replit Nix module `python312` doit être actif (cf. `.replit` packager `uv`). Sinon `pip install uv` puis relancer.

---

## B. Variables d'environnement (Replit Secrets — ~15 min)

> **RÈGLE ABSOLUE** : aucune de ces valeurs ne doit jamais être commitée dans `.env` ou dans le code. Toujours via **Replit Secrets** (icône cadenas dans la sidebar gauche, "Tools" → "Secrets").

### B.1. Secrets à créer (dans l'ordre)

| # | Clé | Valeur | Comment l'obtenir |
|---|-----|--------|-------------------|
| 1 | `TELEGRAM_BOT_TOKEN` | Token alphanumérique (~46 chars) | Ouvrir Telegram → contacter `@BotFather` → `/newbot` → choisir nom (ex. `TradingApp Bot Thomas`) → choisir handle unique (ex. `thomas_tradingapp_bot`) → BotFather renvoie le token. **Ne jamais le partager.** |
| 2 | `THOMAS_CHAT_ID` | Entier numérique (ex. `123456789`) | Ouvrir Telegram → ouvrir une conversation avec le bot créé (recherche son handle) → cliquer `/start` → ouvrir une convo avec `@userinfobot` → envoyer `/start` → copier le `Id` retourné. **Note** : si chat_id perdu après réinstall Telegram, refaire la procédure (cf. F22 user-flows.md). |
| 3 | `TWELVEDATA_API_KEY` | Clé alphanumérique (~32 chars) | [twelvedata.com/account/api-keys](https://twelvedata.com/account/api-keys) → vérifier plan **Pro Individual 79 $/mois actif** (H2 PASS) → copier la clé existante OU regenerate. |
| 4 | `ANTHROPIC_API_KEY` | Clé `sk-ant-api03-...` | [console.anthropic.com](https://console.anthropic.com) → API Keys → **Create Key** dédiée TradingApp (ne pas réutiliser une clé partagée avec d'autres projets). Définir un budget cap mensuel à 30 $ via "Workspace Limits" (sécurité). |
| 5 | `ANTHROPIC_MODEL_LIVE` | `claude-sonnet-4-5-20250929` | Tag exact validé (cf. `lessons-learned.md` L002 — JAMAIS `-latest`). |
| 6 | `ANTHROPIC_MODEL_RND` | `claude-haiku-4-5` | Modèle R&D batch + cache (cf. `ai-architecture.md`). |
| 7 | `CONFIDENCE_THRESHOLD_PAPER` | `7.0` | Seuil signal en mode paper-trading (cf. `edge-scoring-model.md` v1.1 §4.2). |
| 8 | `CONFIDENCE_THRESHOLD_LIVE` | `6.5` | Seuil signal en mode live, `[HYPOTHÈSE]` à recalibrer post-R&D. |
| 9 | `RND_DAILY_CALL_CAP` | `100` | Plafond Claude Haiku R&D / jour (cf. `ai-architecture.md` §3.3). |
| 10 | `MONTHLY_AI_BUDGET_EUR` | `10` | Budget IA mensuel (live ; alerte Telegram si dépassement, cf. monitoring §5.5 infra-audit). |
| 11 | `TZ` | `Europe/Paris` | Fuseau horaire — critique pour cron 8h40 CET. |
| 12 | `LOG_LEVEL` | `INFO` | DEBUG en R&D si besoin, INFO par défaut. |
| 13 | `BOURSE_DIRECT_FRAIS_ALLER_RETOUR` | `1.98` | Frais aller-retour Bourse Direct (cf. `kpi-framework.md` formule P&L net). |
| 14 | `STRATEGY_ACTIVE` | `paper` | Mode actif (`paper` ou `live`, cf. US-11). Bascule manuelle après validation. |
| 15 | `HEALTHCHECKS_PING_URL` | `https://hc-ping.com/<uuid>` | Généré à la section E ci-dessous. À renseigner après création du check. |

### B.2. Procédure d'ajout dans Replit
1. Sidebar gauche du Repl → cliquer l'icône **Secrets** (cadenas).
2. Bouton **+ New Secret**.
3. Pour chaque ligne du tableau B.1 : renseigner **Key** = nom exact (case-sensitive) + **Value** = valeur copiée. Sauvegarder.
4. Vérifier que les 15 secrets apparaissent dans la liste.

### B.3. Vérification post-setup
Dans le Shell Replit :
```bash
echo "TELEGRAM_BOT_TOKEN length: ${#TELEGRAM_BOT_TOKEN}"
echo "THOMAS_CHAT_ID: $THOMAS_CHAT_ID"
echo "TZ: $TZ"
```
Sortie attendue :
- `TELEGRAM_BOT_TOKEN length: 46` (approximatif, jamais 0)
- `THOMAS_CHAT_ID: <numérique>`
- `TZ: Europe/Paris`

**Si une variable affiche vide (`length: 0`) → le secret n'est pas chargé. Redémarrer le Repl ("Stop" puis "Run") pour forcer le rechargement.**

---

## C. Cron Deployment (~15 min)

> **Choix structurant** : Cron Deployment, **PAS Always-On** (cf. `infra-audit.md` §1.3 — l'app tourne 10 min/j ouvré, 220 min/mois, Always-On 24/7 = gaspillage).

### C.1. Créer le Cron Deployment
1. Dans le Repl → onglet **Deployments** (sidebar gauche, icône fusée).
2. Bouton **Create Deployment** → choisir type **Scheduled (Cron)**.
3. **Name** : `tradingapp-cron-daily`.
4. **Schedule** : voir section C.2 ci-dessous (TZ-dépendant).
5. **Run command** : `python -m src.main --mode=live`.
6. **Build command** : `uv sync` (ou laisser vide si dépendances déjà installées dans le Repl source).
7. **Resources** : 0.5 vCPU / 1 GB RAM (suffisant pour la fenêtre 10 min). Augmenter si besoin lors de la R&D phase 1.
8. Cliquer **Deploy**.

### C.2. Schedule cron — gestion fuseau horaire (CRITIQUE)

**Replit Cron Deployments interprètent le schedule en UTC par défaut**, indépendamment de la variable `TZ` du runtime. Donc le schedule cron doit être en UTC.

**Conversion 8h40 CET → UTC** :
- **Heure d'été (CEST = UTC+2, ~30 mars → 26 octobre)** : 8h40 CEST = **6h40 UTC** → cron `40 6 * * 1-5`
- **Heure d'hiver (CET = UTC+1, ~26 octobre → 30 mars)** : 8h40 CET = **7h40 UTC** → cron `40 7 * * 1-5`

**Trois options pour gérer le changement d'heure** :

#### Option 1 (recommandée, robuste) — wrapper Python
Schedule cron à `40 6,7 * * 1-5` (déclenche à 6h40 ET 7h40 UTC). Le wrapper Python vérifie `datetime.now(ZoneInfo("Europe/Paris")).hour == 8 and minute == 40` et n'exécute que si l'heure locale CET est bien 8h40 — sinon exit 0 silencieux.

```python
# src/main.py (extrait — sera implémenté @fullstack)
from datetime import datetime
from zoneinfo import ZoneInfo

now_paris = datetime.now(ZoneInfo("Europe/Paris"))
if not (now_paris.hour == 8 and now_paris.minute == 40):
    print(f"[cron-guard] Skipped — local time is {now_paris.isoformat()}")
    raise SystemExit(0)
```

→ **Avantage** : aucune intervention manuelle 2×/an aux changements d'heure. **À implémenter par @fullstack.**

#### Option 2 — ajustement manuel 2×/an
Mettre à jour le schedule manuellement chaque dernier dimanche de mars et octobre. **Risqué** (oubli = signal manqué pendant 1 semaine).

#### Option 3 — Cron natif Linux (si Replit supporte TZ par cron)
Vérifier dans le dashboard Deployments si une option "TZ-aware schedule" est disponible. **À ce jour (mai 2026), Replit Scheduled Deployments sont UTC uniquement** — donc Option 1 retenue.

**DÉCISION RETENUE PHASE 2a : Option 1** — schedule UTC `40 6,7 * * 1-5` + wrapper Python (à coder par @fullstack).

### C.3. Vérification post-déploiement
1. Dans Deployments → onglet du cron → vérifier **Status: Active**.
2. Onglet **Logs** : attendre la prochaine exécution programmée (ou déclencher manuellement via bouton **Run now**).
3. Confirmer dans les logs : message "✅ TradingApp cron OK [DATE/HEURE]" envoyé sur Telegram (cf. F.2 ci-dessous).

---

## D. Volume persistant (~5 min)

> **CRITIQUE** : sans volume persistant, le SQLite `data/journal.sqlite` est perdu à chaque redéploiement (storage éphémère sur Replit Deployments).

### D.1. Activer un volume persistant
1. Dans Deployments → cron `tradingapp-cron-daily` → onglet **Storage** (ou **Volumes** selon UI Replit).
2. Bouton **+ Add Volume**.
3. **Mount path** : `/home/runner/<repl-name>/data` (ou variable `${REPLIT_DB_DIR}/data` si exposée).
4. **Size** : 1 GB (largement suffisant — SQLite cache 5 ans Twelve Data ≈ 200-400 MB max, journal trades < 10 MB).
5. Cliquer **Create**.

### D.2. Fichiers persistés dans `data/`
- `data/market_cache.sqlite` — cache 5 ans bougies 1m Twelve Data (Phase 1 R&D).
- `data/journal.sqlite` — journal signaux + trades (cf. `kpi-framework.md` §3 schéma SQL).
- `data/score_distribution_observed.json` — distribution scores observée vs prior (cf. `score-distribution-simulation.md`).
- `data/last_run.timestamp` — healthcheck local.

### D.3. Backup hebdo (à automatiser Phase 2b)
- **Quotidien** : copie locale `data/journal.$(date +%F).bak` (rotation 14 jours).
- **Hebdomadaire** : upload `tar.gz` vers Cloudflare R2 (free tier 10 GB) — compte R2 à créer ultérieurement, hors Phase 2a.

---

## E. healthchecks.io (~5 min)

### E.1. Créer le compte
1. Aller sur [healthchecks.io](https://healthchecks.io) → **Sign up** (free tier = 20 checks).
2. Confirmer l'email.

### E.2. Créer le check "TradingApp daily cron"
1. Dashboard healthchecks.io → bouton **Add Check**.
2. **Name** : `TradingApp daily cron`.
3. **Schedule type** : **Cron**.
4. **Cron expression** : `40 8 * * 1-5` (heure locale CET, le wrapper Python ping après vérification TZ).
5. **Timezone** : `Europe/Paris`.
6. **Grace time** : `20 minutes` (signal calculé entre 8h40 et 9h00, ping doit arriver dans cette fenêtre).
7. Cliquer **Save**.
8. Copier l'URL ping affichée (format `https://hc-ping.com/<uuid>`) → coller dans Replit Secrets clé `HEALTHCHECKS_PING_URL` (cf. B.1 ligne 15).

### E.3. Configurer l'alerte Telegram (optionnel mais recommandé)
1. Dans healthchecks.io → onglet **Integrations** → **Add Integration** → **Telegram**.
2. Suivre la procédure d'intégration (création d'un bot dédié notifications OU réutilisation du bot TradingApp avec un canal séparé).
3. Tester l'alerte : healthchecks.io → check `TradingApp daily cron` → bouton **Pause** puis attendre 25 min → vérifier réception Telegram "Down".
4. Réactiver le check (**Resume**).

### E.4. Calendrier jours fériés FR
Le wrapper Python (cf. C.2 Option 1) doit aussi exclure les jours fériés français (cf. infra-audit §5.1) avec la lib **`workalendar`** (Python). Implémentation @fullstack :

```python
from workalendar.europe import France
cal = France()
if not cal.is_working_day(now_paris.date()):
    print(f"[cron-guard] Skipped — {now_paris.date()} is not a French working day")
    requests.get(os.environ["HEALTHCHECKS_PING_URL"])  # ping OK pour ne pas alerter healthchecks
    raise SystemExit(0)
```

**Important** : faire un ping healthchecks.io OK les jours fériés (sinon healthchecks alerte à tort). Alternative : configurer un schedule healthchecks "Mon-Fri excluding FR holidays" — non supporté nativement, donc ping côté code.

---

## F. Mini-jalon J+7 — checklist de validation

> Cette section liste **les 6 critères** que Thomas doit valider à J+7 (~ 8 mai 2026). Si un critère échoue → debug avant Phase 1 R&D.

### F.1. ✅ Cron déclenche à 8h40 CET Mon-Fri
- **Comment vérifier** : dans Replit Deployments → `tradingapp-cron-daily` → **Logs** → vérifier que le wrapper Python a logué "Cron triggered at 08:40 Europe/Paris" 5 jours ouvrés consécutifs.
- **Échec si** : pas de log ou log à mauvaise heure → vérifier schedule UTC C.2 et wrapper TZ.

### F.2. ✅ Push Telegram "hello world" reçu sur THOMAS_CHAT_ID
- **Comment vérifier** : ouvrir Telegram → conversation avec le bot TradingApp → message reçu chaque jour ouvré 8h40-8h41 CET, format :
  ```
  ✅ TradingApp cron OK
  2026-05-08 08:40:12 CEST
  Mode : paper
  Healthcheck : sent
  ```
- **Échec si** : pas de message ou message en double → vérifier `TELEGRAM_BOT_TOKEN` + `THOMAS_CHAT_ID` + idempotence wrapper.

### F.3. ✅ Pas de signal weekend ni jours fériés FR
- **Comment vérifier** : aucun message Telegram samedi/dimanche, ni le 8 mai 2026 (Victoire 1945 — férié FR).
- **Échec si** : message envoyé un jour férié → wrapper `workalendar` mal configuré (cf. E.4).

### F.4. ✅ healthchecks.io confirme ping reçu
- **Comment vérifier** : dashboard healthchecks.io → check `TradingApp daily cron` → status **Up** (vert), dernier ping affiché < 24h, log des 5 derniers pings visible.
- **Échec si** : status **Down** ou **Late** → URL ping mal renseignée ou wrapper ne pingue pas.

### F.5. ✅ SQLite `data/journal.sqlite` créé avec tables vides
- **Comment vérifier** : Shell Replit (depuis le Deployment ou le Repl source si volume monté) :
  ```bash
  sqlite3 data/journal.sqlite ".tables"
  ```
  Sortie attendue :
  ```
  signals  trades  journal_weeks  strategy_decisions  strategy_pauses  strategy_state
  ```
  Et `SELECT COUNT(*) FROM signals;` doit retourner `0`.
- **Échec si** : tables manquantes → script d'initialisation @fullstack à corriger.

### F.6. ✅ Logs visibles dans Replit
- **Comment vérifier** : Replit Deployments → onglet Logs → format JSON (cf. infra-audit §4.4) avec champs `ts`, `level`, `stage`, `latency_ms`. Au moins 5 jours de logs cumulés à J+7.
- **Échec si** : logs en clair non structurés ou absents → corriger logger Python @fullstack.

### F.7. Validation finale persona
- Si **6/6 PASS** → Phase 1 R&D edge peut démarrer (mini-jalon J+7 réussi).
- Si **< 6/6 PASS** → debug ciblé avant d'engager R&D (la fiabilité infra est la fondation).

---

## G. Sécurité — checklist permanente

| # | Action | Fréquence |
|---|--------|-----------|
| G.1 | Repo GitHub `private` (vérifier `gh repo view --json visibility`) | Permanent — JAMAIS rendre public |
| G.2 | Secrets dans Replit Secrets uniquement, JAMAIS dans `.env` commité | Permanent — vérifier `.gitignore` |
| G.3 | Rotation `TELEGRAM_BOT_TOKEN` | Tous les 6 mois OU si exposé |
| G.4 | Rotation `TWELVEDATA_API_KEY` | Tous les 12 mois OU si exposé |
| G.5 | Rotation `ANTHROPIC_API_KEY` | Tous les 6 mois OU si suspicion |
| G.6 | Audit `pip-audit` (Python) | Mensuel, le 1er du mois |
| G.7 | Vérifier qu'aucun fichier `data/*.sqlite` n'est commité | À chaque PR |
| G.8 | Vérifier que les logs Replit ne contiennent jamais les valeurs des secrets (input filtering) | À chaque déploiement |
| G.9 | Cap budget Anthropic (Workspace Limits 30 $/mois) | Permanent |
| G.10 | Disclaimer README ⚠️ "outil personnel non commercialisé" | Permanent |

---

## H. Limites Replit connues à anticiper

| Limite | Impact TradingApp | Mitigation |
|--------|-------------------|------------|
| Cold start ~5-15 s sur Cron Deployment | Worker démarre 5-15 s après le trigger 8h40 → signal calculé à 8h40:15 → fenêtre 8h45 OK | Aucune (acceptable). Si critique : Always-On 24/7 (~5 $/mois sup, hors budget actuel) |
| Storage éphémère hors volume persistant | SQLite perdu si pas de volume | Volume persistant `data/` activé section D.1 |
| Pas de cron natif < 1 min de granularité | N/A (besoin = quotidien) | OK |
| Mémoire 1 GB plan Core | R&D Phase 1 sur 5 ans bougies 1m peut frôler la limite | Streaming / chunking dans le backtester (à coder @fullstack), upgrade resources si besoin |
| DATABASE_URL Replit Postgres N/A | TradingApp utilise SQLite local, pas Postgres | OK (SQLite suffit pour MVP perso) |
| Replit Cron Deployments en UTC uniquement | Risque drift CET vs UTC aux changements d'heure | Wrapper Python TZ-aware (Option 1 section C.2) |

---

## Handoff

---
**Handoff → @orchestrator** (Phase 2a setup terminé)

- Fichiers produits :
  - `/home/user/TradingApp/REPLIT_ACTIONS.md` (ce document — guide actions Thomas)
  - `/home/user/TradingApp/.replit` (config Replit run/build/packager)
  - `/home/user/TradingApp/.gitignore` (exclusions secrets, SQLite, caches)
  - `/home/user/TradingApp/replit.nix` (dépendances système : python312, sqlite, git, openssl, uv)

- Décisions prises :
  - **Cron Deployment retenu** (pas Always-On) — économie ~5 $/mois.
  - **Schedule UTC `40 6,7 * * 1-5`** + wrapper Python TZ-aware (Option 1 C.2) — robuste aux changements d'heure.
  - **Volume persistant `data/` 1 GB** activé pour SQLite (sans ça, journal perdu à chaque déploiement).
  - **15 Secrets Replit listés** avec source de chaque valeur (BotFather, Twelve Data dashboard, Anthropic console).
  - **Stack Python pur** confirmé (cohérent project-context.md ligne 53).
  - **Package manager : uv** (rapide, lock file, recommandé Replit Nix Python 3.12).

- Points d'attention :
  - **TZ UTC ↔ CET** : critique. Si wrapper Python TZ-aware non implémenté par @fullstack → risque signal manqué 1 semaine 2×/an aux changements d'heure.
  - **Jours fériés FR** : `workalendar.europe.France` à intégrer dans le wrapper, sinon faux positifs sur jours fériés.
  - **Healthchecks.io ping OK les jours fériés** : sinon alerte à tort (le calendar exclut les fériés mais healthchecks ne le sait pas).
  - **Cap budget Anthropic 30 $/mois** : à configurer côté console.anthropic.com workspace limits (sécurité runaway).

- **Actions Replit requises (Thomas)** :
  1. Suivre A.1 → souscrire Replit Core 20 $/mois annuel.
  2. Suivre A.2-A.4 → créer Repl + importer GitHub + installer deps.
  3. Suivre B.1-B.2 → créer les 15 Secrets (sauf `HEALTHCHECKS_PING_URL` créé en E).
  4. Suivre C.1-C.2 → créer Cron Deployment avec schedule UTC `40 6,7 * * 1-5`.
  5. Suivre D.1 → activer volume persistant 1 GB sur `data/`.
  6. Suivre E.1-E.4 → créer compte healthchecks.io + check + intégration alertes.
  7. Suivre F.1-F.7 → valider mini-jalon J+7 (6 critères PASS).
  8. Suivre G.1-G.10 → checklist sécurité permanente.

**Handoff secondaire :**
- @fullstack : implémenter `src/main.py` (wrapper TZ-aware + workalendar + ping healthchecks + push Telegram hello + init SQLite tables vides) pour matcher F.1-F.6.
- @qa : préparer le test plan J+7 (5 jours ouvrés × 6 critères = 30 checks) à exécuter par Thomas.

---
