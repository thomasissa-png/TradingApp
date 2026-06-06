#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Test de la logique de garde de `cycle.yml` (step "Guard").
#
# La garde est du bash-dans-YAML difficile à unit-tester en place. Ce script
# RÉIMPLÉMENTE à l'identique la fonction de décision et rejoue les cas clés
# de la table de vérité (week-end ET fériés de marché). Toute modif du YAML doit
# garder ce test vert. Le verdict « jour de bourse ouvert » est, côté YAML,
# délégué à is_trading_day() de journaliste.py (calendrier unique) — ce miroir
# bash modélise juste son résultat booléen via le paramètre `holiday`.
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
#   $5 = férié de marché ("yes"|"no") — miroir de is_trading_day (_is_market_holiday)
#
# NOTE : le YAML ne recopie PAS de liste de fériés ; il appelle is_trading_day()
# de journaliste.py (calendrier NYSE ∪ Euronext unique). Ce miroir bash modélise
# juste le verdict booléen « jour de bourse fermé ? » (week-end OU férié) pour
# rejouer la table de vérité sans dépendre de l'env Python.
# Écrit "true" / "false" sur stdout.
guard_decision() {
  local event="$1" force="$2" dow="$3" recent="$4" holiday="${5:-no}"

  # 1. Forçage explicite → bypass tout (week-end + fériés inclus).
  if [ "$force" = "true" ] || [ "$event" = "push" ]; then
    echo "true"; return
  fi

  # 2. Déclencheurs automatiques : garde JOUR DE BOURSE (week-end OU férié).
  #    = miroir de `! is_trading_day(today_paris)` dans cycle.yml.
  if [ "$dow" -ge 6 ] || [ "$holiday" = "yes" ]; then
    echo "false"; return
  fi

  # 3. Jour de bourse ouvert : anti-doublon ×3 pour le schedule uniquement.
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

# --- cas clés de la table de vérité ---------------------------------------
#        label                            attendu  event              force   dow recent holiday
check "schedule / lundi"                   true   schedule          ""      1   no     no
check "schedule / samedi"                  false  schedule          ""      6   no     no
check "schedule / lundi FÉRIÉ (FIX)"       false  schedule          ""      1   no     yes
check "dispatch-VPS / lundi"               true   workflow_dispatch false   1   no     no
check "dispatch-VPS / samedi"              false  workflow_dispatch false   6   no     no
check "dispatch-VPS / lundi FÉRIÉ (FIX)"   false  workflow_dispatch false   1   no     yes
check "dispatch-force / samedi"            true   workflow_dispatch true    6   no     no
check "dispatch-force / lundi FÉRIÉ"       true   workflow_dispatch true    1   no     yes
check "push RUN-CYCLE / lundi FÉRIÉ"       true   push              ""      1   no     yes

# --- cas complémentaires (non-régression) ---------------------------------
check "schedule / lundi doublon ×3"        false  schedule          ""      1   yes    no
check "schedule / dimanche"                false  schedule          ""      7   no     no
check "dispatch-VPS / vendredi"            true   workflow_dispatch false   5   no     no
check "dispatch-force / dimanche"          true   workflow_dispatch true    7   no     no

if [ "$fails" -eq 0 ]; then
  echo "ALL PASS"; exit 0
fi
echo "$fails FAIL(s)"; exit 1
