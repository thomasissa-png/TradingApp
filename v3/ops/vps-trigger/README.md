# Pinger VPS → TradingApp (déclenchement fiable du cycle)

> **But** : remplacer le `schedule` GitHub (qui abandonne silencieusement des créneaux — incidents 01/06 et 02/06) par un **cron local sur le VPS Anya**, fiable à la minute.
> **Principe** : le VPS n'est qu'une **horloge**. Le cycle (ingest → critères → bulletin → mesure) continue de tourner **sur GitHub Actions** et commite ses données sur `main`. Aucun compute / secret / stockage du pipeline ne revient sur le VPS → l'archi v3 « sans VPS » est préservée.
> **Statut** : ✅ déployé et validé en prod le 2026-06-02 (run #25 déclenché depuis le VPS, HTTP 204).

## Architecture du déclenchement

```
cron VPS (/etc/cron.d/tradingapp, 7h/12h/18h Paris)
   └─ /opt/tradingapp/trigger-cycle.sh
        └─ POST api.github.com .../workflows/cycle.yml/dispatches  {"ref":"main"}
             └─ GitHub Actions exécute cycle-decision sur main
                  └─ commit "[skip ci]" des données sur main
```

Le `schedule` natif de GitHub (`cron: "12,27,42 5,10,16 * * *"` dans `cycle.yml`) est **conservé en filet de secours**.

> ⚠️ `workflow_dispatch` **contourne** le garde-fou anti-doublon du workflow → **un seul tir par créneau** côté cron VPS (pas de redondance ×3).

> ⚠️ **Garde week-end (session 4)** : le script `trigger-cycle.sh` **ne dispatche pas** samedi/dimanche (heure de Paris, `TZ=Europe/Paris date +%u` ≥ 6 → `exit 0`). Marchés actions fermés le week-end → prix figés à la clôture de vendredi. En **défense en profondeur**, `cycle.yml` applique sa propre garde à TOUS les déclencheurs automatiques (`schedule` **ET** `workflow_dispatch` sans `force`) : même si le dispatch VPS partait un week-end, le workflow ferait NO-OP. **Échappatoire** : `workflow_dispatch` avec input `force=true` (ou push `v3/RUN-CYCLE.txt`) bypass la garde côté GitHub ; `TRADINGAPP_FORCE=1` bypass côté script VPS.

> ⚠️ **Garde fériés de marché (session 4) — AUTORITATIVE CÔTÉ WORKFLOW, PAS SUR LE VPS.** En plus du week-end, un run automatique ne s'exécute que les **jours de bourse ouverts** (ni week-end **ni férié** NYSE/Euronext : Vendredi saint, Memorial Day, Thanksgiving, Pâques Euronext, etc.). Le verdict « jour de bourse ouvert » est rendu par `is_trading_day()` de `v3/scripts/journaliste.py` (calendrier unique `MARKET_HOLIDAYS` réutilisé — **zéro liste de dates dupliquée**), appelé dans la garde du workflow. **Le VPS NE connaît PAS les fériés** (il n'a pas l'env Python du repo) : il **peut** dispatcher un lundi férié, mais le workflow fera alors **NO-OP** (log « férié de marché AAAA-MM-JJ »). C'est volontaire : on n'introduit aucune liste de fériés sur le VPS (sinon double source = risque de divergence). Le VPS ne gère que le fast-path week-end ; la couche férié est centralisée côté workflow, source de vérité unique.

## Pourquoi le VPS plutôt que cron-job.org

Le VPS `82.165.168.92` (IONOS) est déjà la machine 24/7 la plus surveillée de Thomas (Anya, n8n, opencode, Beeper) et a déjà un système de cron éprouvé. Coût marginal = quelques lignes. Meilleure hygiène de secret (PAT sur serveur durci ufw/fail2ban vs formulaire web tiers), zéro nouveau service à surveiller.

## Déploiement de référence (tel que posé en prod)

| Élément | Emplacement |
|---|---|
| Token (PAT) | `/root/.config/tradingapp/dispatch-token` (chmod 600) |
| Script | `/opt/tradingapp/trigger-cycle.sh` |
| Cron | `/etc/cron.d/tradingapp` (run as `root`, **horaire `0 * * * *`** + garde Paris dans le script) |
| Journal | `/var/log/tradingapp-trigger.log` |

`/etc/cron.d/` (et pas la crontab de `thomas`) car le déploiement auto d'Anya réécrit la crontab de `thomas` — un fichier dédié **survit aux redéploiements**.

## Procédure (re)installation

### 1. Créer le token GitHub (fine-grained PAT)
https://github.com/settings/personal-access-tokens/new
- **Resource owner** : `thomasissa-png` · **Repository access** : *Only* → `TradingApp`
- **Permissions** → *Repository* → **Actions : Read and write** (rien d'autre)

> 🔒 **Ne jamais coller la valeur du token dans un chat / un ticket / un commit.** Uniquement dans le terminal SSH. (Leçon 02/06 : un token collé dans le chat = compromis → révoquer immédiatement.)

### 2. Poser le token sur le VPS (`ssh root@82.165.168.92`)
```bash
install -d -m 700 /root/.config/tradingapp
printf '%s' 'TON_TOKEN' > /root/.config/tradingapp/dispatch-token
chmod 600 /root/.config/tradingapp/dispatch-token
```
À ajouter aussi dans **Bitwarden** (entrée « TradingApp — PAT dispatch »).

### 3. Installer le script
Copier `trigger-cycle.sh` (ce dossier) vers `/opt/tradingapp/trigger-cycle.sh` puis `chmod +x`.

> ⚠️ La commande `curl` du script est sur **une seule ligne** : les continuations `\` se perdent au copier-coller dans un terminal SSH (incident 02/06 : `-H: command not found`). Ne pas la re-découper.

### 4. Tester
```bash
/opt/tradingapp/trigger-cycle.sh
tail -n1 /var/log/tradingapp-trigger.log    # attendu : RESULTAT: OK 204
```
401/403 → token/permissions · 404 → repo/workflow · 422 → ref introuvable.

### 5. Brancher le cron
```bash
cat > /etc/cron.d/tradingapp <<'EOF'
0 * * * * root /opt/tradingapp/trigger-cycle.sh
EOF
chmod 644 /etc/cron.d/tradingapp
```
⚠️ **Ne PAS utiliser `CRON_TZ`** : le cron Debian/Ubuntu (Vixie) ne l'honore pas
(incident 02/06 — le créneau de midi n'est jamais parti). On fire toutes les
heures et le script self-gate sur l'heure de Paris (7/12/18) → robuste DST,
indépendant du fuseau système. Cron lit `/etc/cron.d/` automatiquement.

## Vérification continue
- Log : `/var/log/tradingapp-trigger.log` (1 ligne OK/ECHEC par tir).
- Côté produit : un nouveau `v3/data/decision-log/AAAA-MM-JJ-HHMM.jsonl` + bulletin du jour sur `main` après chaque créneau.
- Côté GitHub : un run `cycle-decision` (event *workflow_dispatch*) à ~05/10/16 UTC.

## Rollback
`rm /etc/cron.d/tradingapp` + `rm /root/.config/tradingapp/dispatch-token`. Le `schedule` GitHub natif reste en place (on retombe sur le comportement antérieur).

## Déclencher un créneau à la main
```bash
/opt/tradingapp/trigger-cycle.sh
```
(ou, depuis une session Claude Code branchée au repo : `workflow_dispatch` via le MCP GitHub.)
