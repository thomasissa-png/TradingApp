#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Déclencheur fiable du cycle TradingApp depuis le VPS Anya.
#
# Pourquoi : le scheduler `schedule` de GitHub Actions abandonne silencieusement
# des créneaux (incidents 01/06 + 02/06 : aucun run cron le matin). Le cron LOCAL
# du VPS (systemd/cronie), lui, est fiable à la minute. Ce script appelle l'API
# GitHub `workflow_dispatch` sur cycle.yml — le cycle s'exécute TOUJOURS sur
# GitHub Actions et commite ses données sur `main`. Le VPS n'est qu'une horloge.
#
# Le compute, le stockage (git-as-storage) et les secrets du pipeline restent
# sur GitHub : on ne réintroduit PAS de VPS dans l'architecture v3.
#
# Installé sur le VPS, appelé 3×/jour par cron (voir crontab.tradingapp).
# ---------------------------------------------------------------------------
set -euo pipefail

REPO="thomasissa-png/tradingapp"     # insensible à la casse côté API GitHub
WORKFLOW="cycle.yml"                  # nom de fichier du workflow (= cycle-decision)
REF="main"                           # branche où le cycle tourne ET commite
LOG="${TRADINGAPP_TRIGGER_LOG:-$HOME/tradingapp-trigger.log}"
TOKEN_FILE="${TRADINGAPP_TOKEN_FILE:-$HOME/.config/tradingapp/dispatch-token}"

ts()  { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

# Token : variable d'env prioritaire, sinon fichier (chmod 600 attendu).
TOKEN="${TRADINGAPP_DISPATCH_TOKEN:-}"
if [[ -z "$TOKEN" && -f "$TOKEN_FILE" ]]; then
  TOKEN="$(< "$TOKEN_FILE")"
fi
TOKEN="${TOKEN//[$'\t\r\n ']/}"      # strip espaces/retours parasites

if [[ -z "$TOKEN" ]]; then
  log "ERREUR: aucun token (ni \$TRADINGAPP_DISPATCH_TOKEN ni $TOKEN_FILE)"
  exit 1
fi

# 3 tentatives, backoff 2s/4s (réseau seulement — un 401/403/404 sort direct).
for attempt in 1 2 3; do
  code="$(curl -sS -o /tmp/tradingapp-dispatch.out -w '%{http_code}' \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches" \
    -d "{\"ref\":\"${REF}\"}" || echo "000")"

  case "$code" in
    204)
      log "OK dispatch ${WORKFLOW}@${REF} (HTTP 204, tentative ${attempt})"
      exit 0 ;;
    401|403|404|422)
      # Erreur non transitoire (token/permissions/ref) — inutile de réessayer.
      log "ECHEC HTTP ${code} (non transitoire) — $(tr -d '\n' < /tmp/tradingapp-dispatch.out 2>/dev/null | cut -c1-300)"
      exit 1 ;;
    *)
      log "ECHEC HTTP ${code} (tentative ${attempt}, retry) — $(tr -d '\n' < /tmp/tradingapp-dispatch.out 2>/dev/null | cut -c1-200)"
      sleep $((attempt * 2)) ;;
  esac
done

log "ABANDON après 3 tentatives"
exit 1
