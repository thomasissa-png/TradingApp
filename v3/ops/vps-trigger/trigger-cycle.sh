#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Déclencheur fiable du cycle TradingApp depuis le VPS Anya.
#
# Le cycle s'exécute TOUJOURS sur GitHub Actions (workflow_dispatch, ref=main)
# et commite ses données sur `main`. Le VPS n'est qu'une horloge.
#
# ⚠️ GARDE HORAIRE ROBUSTE (incident 02/06) : le cron Debian/Ubuntu (Vixie)
# n'honore PAS `CRON_TZ`. Plutôt que de parier sur le fuseau système, le cron
# appelle ce script TOUTES LES HEURES (`0 * * * *`) et on ne déclenche qu'aux
# heures de bulletin EN HEURE DE PARIS (7h/12h/18h) — robuste été/hiver,
# indépendant du fuseau de la machine.  Bypass test : TRADINGAPP_FORCE=1.
#
# ⚠️ Le curl est sur UNE SEULE LIGNE (les continuations `\` se perdent au
# copier-coller dans un terminal SSH — incident 02/06).
#
# Déploiement de référence (VPS) :
#   token : /root/.config/tradingapp/dispatch-token (chmod 600)
#   script: /opt/tradingapp/trigger-cycle.sh
#   cron  : /etc/cron.d/tradingapp  ->  0 * * * * root /opt/tradingapp/trigger-cycle.sh
# ---------------------------------------------------------------------------
set -euo pipefail

REPO="thomasissa-png/tradingapp"
WORKFLOW="cycle.yml"
REF="main"
LOG="${TRADINGAPP_TRIGGER_LOG:-/var/log/tradingapp-trigger.log}"
TOKEN_FILE="${TRADINGAPP_TOKEN_FILE:-/root/.config/tradingapp/dispatch-token}"

ts()  { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

# --- Garde horaire (heure de Paris, robuste DST, sans CRON_TZ) --------------
PARIS_H="force"
if [ "${TRADINGAPP_FORCE:-}" != "1" ]; then
  PARIS_H="$(TZ=Europe/Paris date +%H)"
  case "$PARIS_H" in
    07|12|18) : ;;            # créneau de bulletin → on continue
    *) exit 0 ;;             # hors créneau → no-op silencieux
  esac
fi

# --- Token (env prioritaire, sinon fichier chmod 600) ----------------------
TOKEN="${TRADINGAPP_DISPATCH_TOKEN:-}"
if [ -z "$TOKEN" ] && [ -f "$TOKEN_FILE" ]; then
  TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"
fi
[ -z "$TOKEN" ] && { log "ERREUR: aucun token"; echo "RESULTAT: PAS DE TOKEN"; exit 1; }

URL="https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches"

# 3 tentatives, backoff 2s/4s. Erreur non transitoire (auth/ref) => sortie directe.
for a in 1 2 3; do
  code="$(curl -sS -o /tmp/ta.out -w '%{http_code}' -X POST -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$URL" -d "{\"ref\":\"${REF}\"}" || echo 000)"
  case "$code" in
    204) log "OK dispatch ${WORKFLOW}@${REF} (HTTP 204, Paris ${PARIS_H}h, essai ${a})"; echo "RESULTAT: OK 204"; exit 0 ;;
    401|403|404|422) log "ECHEC HTTP ${code} (non transitoire): $(tr -d '\n' </tmp/ta.out | cut -c1-200)"; echo "RESULTAT: ECHEC $code"; exit 1 ;;
    *) log "ECHEC HTTP ${code} (essai ${a}, retry)"; sleep $((a * 2)) ;;
  esac
done
log "ABANDON après 3 tentatives"; echo "RESULTAT: ABANDON"; exit 1
