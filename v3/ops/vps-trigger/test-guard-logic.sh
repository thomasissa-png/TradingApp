#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Test de la logique de garde de `cycle.yml` (step "Guard").
#
# La garde est du bash-dans-YAML difficile à unit-tester en place. Ce script
# RÉIMPLÉMENTE à l'identique la fonction de décision et rejoue les 6 cas clés
# de la table de vérité. Toute modif du YAML doit garder ce test vert.
#
#   Usage : bash v3/ops/vps-trigger/test-guard-logic.sh
#   Sortie : "ALL PASS" (exit 0) ou liste des échecs (exit 1).
# ---------------------------------------------------------------------------
set -euo pipefail

# Décision = miroir exact de la garde cycle.yml.
#   $1 = event (schedule|workflow_dispatch|push)
#   $2 = force input ("true"|"false"|"")
#   $3 = jour de la semaine (1..7, 6=sam 7=dim)
#   $4 = snapshot_recent ("yes"|"no") — uniquement pertinent pour schedule jour ouvré
# Écrit "true" / "false" sur stdout.
guard_decision() {
  local event="$1" force="$2" dow="$3" recent="$4"

  # 1. Forçage explicite → bypass tout (week-end inclus).
  if [ "$force" = "true" ] || [ "$event" = "push" ]; then
    echo "true"; return
  fi

  # 2. Déclencheurs automatiques : garde week-end.
  if [ "$dow" -ge 6 ]; then
    echo "false"; return
  fi

  # 3. Jour ouvré : anti-doublon ×3 pour le schedule uniquement.
  if [ "$event" != "schedule" ]; then
    echo "true"; return   # VPS = 1 tir/créneau → toujours passer.
  fi
  if [ "$recent" = "yes" ]; then
    echo "false"; return  # tentative schedule redondante.
  fi
  echo "true"
}

fails=0
check() {
  local label="$1" expected="$2"; shift 2
  local got; got="$(guard_decision "$@")"
  if [ "$got" = "$expected" ]; then
    echo "PASS  $label  → run=$got"
  else
    echo "FAIL  $label  → attendu run=$expected, obtenu run=$got"
    fails=$((fails + 1))
  fi
}

# --- 6 cas clés de la table de vérité -------------------------------------
#        label                          attendu  event              force   dow recent
check "schedule / lundi"                 true   schedule          ""      1   no
check "schedule / samedi"                false  schedule          ""      6   no
check "dispatch-VPS / lundi"             true   workflow_dispatch false   1   no
check "dispatch-VPS / samedi (FIX)"      false  workflow_dispatch false   6   no
check "dispatch-force / samedi"          true   workflow_dispatch true    6   no
check "push RUN-CYCLE / samedi"          true   push              ""      6   no

# --- cas complémentaires (non-régression) ---------------------------------
check "schedule / lundi doublon ×3"      false  schedule          ""      1   yes
check "schedule / dimanche"              false  schedule          ""      7   no
check "dispatch-VPS / vendredi"          true   workflow_dispatch false   5   no
check "dispatch-force / dimanche"        true   workflow_dispatch true    7   no

if [ "$fails" -eq 0 ]; then
  echo "ALL PASS"; exit 0
fi
echo "$fails FAIL(s)"; exit 1
