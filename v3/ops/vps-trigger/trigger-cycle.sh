#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Déclencheur fiable du cycle TradingApp depuis le VPS Anya.
#
# Le cycle s'exécute TOUJOURS sur GitHub Actions (workflow_dispatch, ref=main)
# et commite ses données sur `main`. Le VPS n'est qu'une horloge.
#
# ⚠️ GARDE HORAIRE ROBUSTE (incident 02/06) : le cron Debian/Ubuntu (Vixie)
# n'honore PAS `CRON_TZ`. Plutôt que de parier sur le fuseau système, le cron
# appelle ce script TOUTES LES HEURES À LA MINUTE 15 (`15 * * * *`) et on ne
# déclenche qu'aux CRÉNEAUX EN HEURE DE PARIS — robuste été/hiver, indépendant
# du fuseau de la machine. Bypass test : TRADINGAPP_FORCE=1.
#
# CRÉNEAUX (refonte « 5 rapports », spec §5.4). Le VPS n'est qu'une horloge : il
# tire à l'heure pile, le ROUTAGE (quel runner) est fait par cycle.yml selon
# l'heure de Paris. Le VPS déclenche aux heures Paris :
#   07h → R1 Briefing complet        12h → R2 Suivi      18h → R3 Suivi
#   08h → stamp ouverture continus   09h → stamp EU/CAC  15h → stamp US
#   22h → R4 Bilan du jour (le routage cycle.yml exige ≥22h15 ; le cron à la
#         minute 15 garantit un tir à 22h15 Paris — JAMAIS un UTC fixe 20h, qui
#         serait 21h Paris en hiver, NYSE encore ouvert).
#   DIMANCHE → R5 Bilan semaine (workflow SÉPARÉ weekly-summary.yml, bypass
#         jour-de-bourse). Déclenché à 18h Paris le dimanche.
#
# ⚠️ GARDE WEEK-END (session 4) : marchés actions fermés sam/dim → prix figés.
# On ne dispatche PAS cycle.yml le week-end (heure de Paris). EXCEPTION : le
# DIMANCHE à 18h, on dispatche weekly-summary.yml (bilan de perf, pas de prix
# live — intentionnel). Le samedi reste totalement muet. Les workflows ont leur
# propre garde en défense en profondeur. TRADINGAPP_FORCE=1 bypass tout (test).
#
# ⚠️ Le curl est sur UNE SEULE LIGNE (les continuations `\` se perdent au
# copier-coller dans un terminal SSH — incident 02/06).
#
# Déploiement de référence (VPS) :
#   token : /root/.config/tradingapp/dispatch-token (chmod 600)
#   script: /opt/tradingapp/trigger-cycle.sh
#   cron  : /etc/cron.d/tradingapp  ->  15 * * * * root /opt/tradingapp/trigger-cycle.sh
#
# --check : affiche les créneaux configurés (format parseable) et sort (CA-I3).
# ---------------------------------------------------------------------------
set -euo pipefail

REPO="thomasissa-png/tradingapp"
WORKFLOW="cycle.yml"            # workflow par défaut (jours de bourse) ; le dimanche
WEEKLY_WORKFLOW="weekly-summary.yml"  # bilan semaine (workflow séparé, §5.2)
REF="main"

# --- --check : sortie parseable des créneaux (CA-I3) ----------------------
if [ "${1:-}" = "--check" ]; then
  echo "workflow-jours-bourse: ${WORKFLOW}"
  echo "workflow-weekly: ${WEEKLY_WORKFLOW}"
  echo "creneau: 07h-briefing-jours-bourse"
  echo "creneau: 08h-stamp-ouverture-continus-jours-bourse"
  echo "creneau: 09h-stamp-ouverture-eu-jours-bourse"
  echo "creneau: 12h-suivi-jours-bourse"
  echo "creneau: 15h-stamp-ouverture-us-jours-bourse"
  echo "creneau: 18h-suivi-jours-bourse"
  echo "creneau: 22h15-paris-jours-bourse"
  echo "creneau: 18h-dimanche"
  exit 0
fi
LOG="${TRADINGAPP_TRIGGER_LOG:-/var/log/tradingapp-trigger.log}"
TOKEN_FILE="${TRADINGAPP_TOKEN_FILE:-/root/.config/tradingapp/dispatch-token}"

ts()  { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

# --- Garde week-end + horaire (heure de Paris, robuste DST, sans CRON_TZ) ----
# Choisit AUSSI le workflow cible : cycle.yml (jours de bourse) ou
# weekly-summary.yml (dimanche 18h). Le VPS n'est qu'une horloge ; le routage du
# RUNNER (bulletin/stamp/suivi/bilan) est fait côté cycle.yml par l'heure Paris.
PARIS_H="force"
TARGET_WORKFLOW="$WORKFLOW"
if [ "${TRADINGAPP_FORCE:-}" != "1" ]; then
  PARIS_DOW="$(TZ=Europe/Paris date +%u)"  # 1=lundi … 6=samedi, 7=dimanche
  PARIS_H="$(TZ=Europe/Paris date +%H)"

  if [ "$PARIS_DOW" -eq 7 ]; then
    # DIMANCHE : seul créneau actif = 18h → bilan semaine (workflow séparé).
    # Marchés fermés mais R5 est un bilan de perf (intentionnel, §5.2).
    if [ "$PARIS_H" = "18" ]; then
      TARGET_WORKFLOW="$WEEKLY_WORKFLOW"
    else
      exit 0                  # dimanche hors 18h → no-op silencieux
    fi
  elif [ "$PARIS_DOW" -eq 6 ]; then
    exit 0                    # samedi → totalement muet (marchés fermés)
  else
    # JOURS OUVRÉS (lun-ven) : créneaux de cycle.yml. Le routage exact (et la
    # garde fériés) sont autoritaires côté workflow ; ici on filtre juste les
    # heures Paris où un créneau existe (économise des dispatches no-op).
    case "$PARIS_H" in
      07|08|09|12|15|18|22) : ;;   # créneau (briefing/stamp/suivi/bilan) → continue
      *) exit 0 ;;                 # hors créneau → no-op silencieux
    esac
  fi
fi

# --- Token (env prioritaire, sinon fichier chmod 600) ----------------------
TOKEN="${TRADINGAPP_DISPATCH_TOKEN:-}"
if [ -z "$TOKEN" ] && [ -f "$TOKEN_FILE" ]; then
  TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"
fi
[ -z "$TOKEN" ] && { log "ERREUR: aucun token"; echo "RESULTAT: PAS DE TOKEN"; exit 1; }

URL="https://api.github.com/repos/${REPO}/actions/workflows/${TARGET_WORKFLOW}/dispatches"

# 3 tentatives, backoff 2s/4s. Erreur non transitoire (auth/ref) => sortie directe.
for a in 1 2 3; do
  code="$(curl -sS -o /tmp/ta.out -w '%{http_code}' -X POST -H "Accept: application/vnd.github+json" -H "Authorization: Bearer ${TOKEN}" -H "X-GitHub-Api-Version: 2022-11-28" "$URL" -d "{\"ref\":\"${REF}\"}" || echo 000)"
  case "$code" in
    204) log "OK dispatch ${TARGET_WORKFLOW}@${REF} (HTTP 204, Paris ${PARIS_H}h, essai ${a})"; echo "RESULTAT: OK 204"; exit 0 ;;
    401|403|404|422) log "ECHEC HTTP ${code} (non transitoire): $(tr -d '\n' </tmp/ta.out | cut -c1-200)"; echo "RESULTAT: ECHEC $code"; exit 1 ;;
    *) log "ECHEC HTTP ${code} (essai ${a}, retry)"; sleep $((a * 2)) ;;
  esac
done
log "ABANDON après 3 tentatives"; echo "RESULTAT: ABANDON"; exit 1
