#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Déclencheur fiable du cycle TradingApp depuis le VPS Anya.
#
# Pourquoi : le scheduler `schedule` de GitHub Actions abandonne silencieusement
# des créneaux (incidents 01/06 + 02/06). Le cron LOCAL du VPS, lui, est fiable.
# Ce script appelle l'API GitHub `workflow_dispatch` sur cycle.yml — le cycle
# s'exécute TOUJOURS sur GitHub Actions et commite ses données sur `main`.
# Le VPS n'est qu'une horloge. Aucun compute/stockage du pipeline sur le VPS.
#
# Déploiement de référence (validé en prod le 2026-06-02) :
#   - token : /root/.config/tradingapp/dispatch-token  (chmod 600)
#   - script: /opt/tradingapp/trigger-cycle.sh
#   - cron  : /etc/cron.d/tradingapp  (CRON_TZ=Europe/Paris, run as root)
#
# ⚠️ La commande curl est volontairement sur UNE SEULE LIGNE : les retours à la
# ligne `\` se perdent au copier-coller dans un terminal SSH (incident 02/06).
# ---------------------------------------------------------------------------
set -euo pipefail

REPO="thomasissa-png/tradingapp"     # insensible à la casse côté API GitHub
WORKFLOW="cycle.yml"                  # fichier du workflow (= cycle-decision)
REF="main"                           # branche où le cycle tourne ET commite
LOG="${TRADINGAPP_TRIGGER_LOG:-/var/log/tradingapp-trigger.log}"
TOKEN_FILE="${TRADINGAPP_TOKEN_FILE:-/root/.config/tradingapp/dispatch-token}"

ts()  { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

# Token : variable d'env prioritaire, sinon fichier (chmod 600 attendu).
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
    204) log "OK dispatch ${WORKFLOW}@${REF} (HTTP 204, essai ${a})"; echo "RESULTAT: OK 204"; exit 0 ;;
    401|403|404|422) log "ECHEC HTTP ${code} (non transitoire): $(tr -d '\n' </tmp/ta.out | cut -c1-200)"; echo "RESULTAT: ECHEC $code"; exit 1 ;;
    *) log "ECHEC HTTP ${code} (essai ${a}, retry)"; sleep $((a * 2)) ;;
  esac
done

log "ABANDON après 3 tentatives"; echo "RESULTAT: ABANDON"; exit 1
