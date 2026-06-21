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

# ---------------------------------------------------------------------------
# Routage par heure de Paris (miroir du step "Route" de cycle.yml).
#   $1 = heure Paris (0..23)   $2 = minute Paris (0..59)
# Écrit le slot sur stdout : bulletin|stamp|suivi12|suivi18|bilan|none.
# Doit rester identique au bash du step Route (DST absorbé par les plages).
route_slot() {
  local ph="$1" pm="$2"
  if   [ "$ph" -ge 6 ]  && [ "$ph" -le 7 ];  then echo "bulletin"; return; fi
  if   [ "$ph" -eq 8 ];                       then echo "stamp";    return; fi
  if   [ "$ph" -eq 9 ];                       then echo "stamp";    return; fi
  if   [ "$ph" -ge 11 ] && [ "$ph" -le 12 ]; then echo "suivi12";  return; fi
  if   [ "$ph" -eq 15 ];                      then echo "stamp";    return; fi
  if   [ "$ph" -ge 17 ] && [ "$ph" -le 18 ]; then echo "suivi18";  return; fi
  if   [ "$ph" -eq 22 ] && [ "$pm" -ge 15 ]; then echo "bilan";    return; fi
  echo "none"
}

# ---------------------------------------------------------------------------
# Garde du workflow SÉPARÉ weekly-summary.yml (bilan samedi, bypass bourse).
#   $1 = event   $2 = force   $3 = dow (1..7, 6=samedi)   $4 = recent (yes|no)
# Garde INVERSÉE vs cycle.yml : ne tourne QUE le samedi (weekday==6 en %u).
# Écrit "true" / "false".
weekly_decision() {
  local event="$1" force="$2" dow="$3" recent="$4"
  # 1. Forçage explicite → bypass garde samedi (CA-W1.c).
  if [ "$force" = "true" ] || [ "$event" = "push" ]; then echo "true"; return; fi
  # 2. Automatique : samedi STRICT (sinon NO-OP).
  if [ "$dow" -ne 6 ]; then echo "false"; return; fi
  # 3. Samedi : anti-doublon ×3 pour le schedule uniquement.
  if [ "$event" != "schedule" ]; then echo "true"; return; fi
  if [ "$recent" = "yes" ]; then echo "false"; return; fi
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

check_slot() {
  local label="$1" expected="$2" ph="$3" pm="$4"
  local got; got="$(route_slot "$ph" "$pm")"
  if [ "$got" = "$expected" ]; then
    echo "PASS  $label  → slot=$got"
  else
    echo "FAIL  $label  → attendu slot=$expected, obtenu slot=$got"
    fails=$((fails + 1))
  fi
}

check_weekly() {
  local label="$1" expected="$2"; shift 2
  local got; got="$(weekly_decision "$@")"
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

# --- ROUTAGE par heure de Paris (step Route de cycle.yml) -----------------
# La garde ci-dessus dit « run autorisé ce jour » ; le routage choisit le runner.
#            label                          slot       ph pm
check_slot "07h00 → bulletin (R1)"          bulletin   7  0
check_slot "06h00 hiver → bulletin (R1)"    bulletin   6  0
check_slot "08h05 → stamp continus"         stamp      8  5
check_slot "09h05 → stamp EU/CAC"           stamp      9  5
check_slot "12h00 → suivi 12h (R2)"         suivi12    12 0
check_slot "11h00 hiver → suivi 12h (R2)"   suivi12    11 0
check_slot "15h35 → stamp US"               stamp      15 35
check_slot "18h00 → suivi 18h (R3)"         suivi18    18 0
check_slot "17h00 hiver → suivi 18h (R3)"   suivi18    17 0
check_slot "22h15 → bilan du jour (R4)"     bilan      22 15
check_slot "22h00 → PAS encore (<22h15)"    none       22 0
check_slot "21h00 hiver (cron) → none"      none       21 0
check_slot "20h00 été (cron) → none"        none       20 0
check_slot "10h00 (cron) → none"            none       10 0
check_slot "13h00 (cron) → none"            none       13 0

# --- GARDE WEEKLY (workflow séparé weekly-summary.yml, bilan samedi) --------
#               label                            attendu  event              force dow recent
check_weekly "weekly / schedule samedi"          true   schedule          ""     6   no
check_weekly "weekly / schedule sam doublon ×3"  false  schedule          ""     6   yes
check_weekly "weekly / schedule lundi → NON"     false  schedule          ""     1   no
check_weekly "weekly / schedule dimanche → NON"  false  schedule          ""     7   no
check_weekly "weekly / dispatch-VPS samedi"      true   workflow_dispatch false  6   no
check_weekly "weekly / dispatch-VPS lundi → NON" false  workflow_dispatch false  1   no
check_weekly "weekly / force=true lundi (CA-W1c)" true  workflow_dispatch true   1   no
check_weekly "weekly / push RUN-WEEKLY lundi"    true   push              ""     1   no

if [ "$fails" -eq 0 ]; then
  echo "ALL PASS"; exit 0
fi
echo "$fails FAIL(s)"; exit 1
