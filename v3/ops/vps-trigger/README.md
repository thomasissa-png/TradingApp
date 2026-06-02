# Pinger VPS → TradingApp (déclenchement fiable du cycle)

> **But** : remplacer le `schedule` GitHub (qui abandonne silencieusement des créneaux — incidents 01/06 et 02/06) par un **cron local sur le VPS Anya**, fiable à la minute.
> **Principe** : le VPS n'est qu'une **horloge**. Le cycle (ingest → critères → bulletin → mesure) continue de tourner **sur GitHub Actions** et commite ses données sur `main`. Aucun compute / secret / stockage du pipeline ne revient sur le VPS → l'archi v3 « sans VPS » est préservée.

## Pourquoi ce choix (vs cron-job.org)

Le VPS `82.165.168.92` (IONOS, Ubuntu 24.04) est **déjà** la machine 24/7 la plus surveillée de Thomas : elle fait tourner Anya, n8n, opencode, Beeper, et **un système de cron déjà éprouvé** (`deploy/crontab.anya` + `sync-crons.sh` dans le repo ISSA-Capital). Ajouter le déclenchement TradingApp = quelques lignes, sur une infra de cron déjà fiable et monitorée. Meilleure hygiène de secret (PAT sur serveur durci ufw/fail2ban vs formulaire web tiers), zéro nouveau service à surveiller.

## Architecture du déclenchement

```
cron VPS (7h/12h/18h Paris)
   └─ trigger-cycle.sh
        └─ POST api.github.com .../workflows/cycle.yml/dispatches  {"ref":"main"}
             └─ GitHub Actions exécute cycle-decision sur main
                  └─ commit "[skip ci]" des données sur main
```

Le `schedule` natif de GitHub (`cron: "12,27,42 5,10,16 * * *"` dans `cycle.yml`) est **conservé en filet de secours** : s'il se déclenche, le garde-fou anti-doublon du workflow évite le double-run. Le pinger VPS devient la voie principale, fiable à l'heure pile.

> ⚠️ `workflow_dispatch` **contourne** le garde-fou anti-doublon (cycle.yml ligne 44, « les déclenchements manuels passent toujours »). D'où **un seul tir par créneau** côté cron VPS (pas de redondance ×3).

## Fichiers de ce dossier

| Fichier | Rôle |
|---|---|
| `trigger-cycle.sh` | Le script appelé par cron — fait le `workflow_dispatch`, log + retries. |
| `crontab.tradingapp` | Les 3 lignes de cron (7h/12h/18h Paris via `CRON_TZ`). |
| `README.md` | Cette procédure. |

## Installation (à faire sur le VPS)

### 1. Créer le token GitHub (fine-grained PAT)

GitHub → *Settings → Developer settings → Fine-grained tokens → Generate new token* :
- **Resource owner** : `thomasissa-png`
- **Repository access** : *Only select repositories* → `tradingapp`
- **Permissions** → *Repository permissions* → **Actions : Read and write** (rien d'autre).
- **Expiration** : 90 j (noter le renouvellement ; ou custom long).

→ Copier le token (`github_pat_...`).

### 2. Déposer le token sur le VPS (chmod 600)

```bash
ssh thomas@82.165.168.92          # ou compte de service approprié
mkdir -p ~/.config/tradingapp
printf '%s' 'github_pat_xxxxxxxx' > ~/.config/tradingapp/dispatch-token
chmod 600 ~/.config/tradingapp/dispatch-token
```

> Alternative : exporter `TRADINGAPP_DISPATCH_TOKEN` dans l'environnement du cron. Le fichier chmod 600 est préféré (même hygiène que `.env.local` d'Anya). À ajouter aussi dans **Bitwarden** (entrée « TradingApp — PAT dispatch »).

### 3. Installer le script

```bash
mkdir -p ~/tradingapp
# copier trigger-cycle.sh depuis le repo TradingApp (v3/ops/vps-trigger/)
install -m 0755 trigger-cycle.sh ~/tradingapp/trigger-cycle.sh
```

### 4. Tester immédiatement (le plus important)

```bash
~/tradingapp/trigger-cycle.sh
cat ~/tradingapp-trigger.log          # attendu : "OK dispatch cycle.yml@main (HTTP 204 ...)"
```

Vérifier côté GitHub qu'un run `cycle-decision` (event = *workflow_dispatch*) a démarré. Si HTTP 401/403 → token/permissions ; 404 → nom de repo/workflow ou accès ; 422 → `ref` introuvable.

### 5. Brancher le cron

**Option A — autonome (le plus simple, indépendant d'Anya)** :
```bash
crontab -e
# coller le contenu de crontab.tradingapp
crontab -l                            # vérifier
```

**Option B — intégré au système repo-driven d'Anya** (repo ISSA-Capital) :
Ajouter les lignes équivalentes dans `deploy/crontab.anya`, puis push sur `main` d'ISSA-Capital → `sync-crons.sh` les applique en ~5 min, sans SSH. ⚠️ Vérifier que `sync-crons.sh` préserve la directive `CRON_TZ=` ; sinon utiliser le bloc UTC de fallback (à réajuster aux changements d'heure).

## Vérification continue

- Log local : `~/tradingapp-trigger.log` (1 ligne OK/ECHEC par tir).
- Côté produit : un nouveau `v3/data/decision-log/AAAA-MM-JJ-HHMM.jsonl` + bulletin du jour doivent apparaître sur `main` après chaque créneau.
- (Option) faire surveiller le log par le `health-check` d'Anya pour alerter si un tir échoue.

## Rollback

Retirer la/les lignes du `crontab` (Option A) ou de `deploy/crontab.anya` (Option B) + `rm ~/.config/tradingapp/dispatch-token`. Le `schedule` GitHub natif reste en place — on retombe simplement sur le comportement actuel (cron GitHub, parfois droppé).

## Déclencher un créneau à la main (sans attendre le cron)

```bash
~/tradingapp/trigger-cycle.sh
```
(ou, depuis une session Claude Code branchée au repo : `workflow_dispatch` via le MCP GitHub.)
