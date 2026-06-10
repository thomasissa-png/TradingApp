"""Replay du scoring sur decision-log 2026-06-01-1337 avec/sans changements.

Objectif : prouver que les Points 2+3 du plan horizon font passer
Or 24h et VIX 1m de LONG à SHORT, sans casser Pétrole et S&P (sens conservé).

Méthode : pour chaque cellule actif×horizon visée, on relit la liste des
critères du decision-log (valeur_normalisee, poids, pertinence stockée AVANT
recalibration, signe, source_track, materiality, reliability). On recalcule
le score AVANT (pertinence du log) puis APRÈS (pertinence YAML actuelle + cap).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scoring_analyste as sa  # noqa: E402

LOG_PATH = ROOT / "data" / "decision-log" / "2026-06-01-1337.jsonl"

# Pertinence APRÈS recalibration (Point 2). Tout le reste est inchangé.
PERTINENCE_NEW: Dict[Tuple[str, str], Dict[str, float]] = {
    ("petrole", "tension_geopol_moyen_orient"): {"24h": 0.6, "7j": 0.6, "1m": 0.2},
    ("petrole", "opec_production_policy"):       {"24h": 0.3, "7j": 0.9, "1m": 1.0},
    ("or",      "tension_geopolitique"):         {"24h": 0.5, "7j": 0.4, "1m": 0.3},
    ("vix",     "tension_geopolitique_active"):  {"24h": 0.9, "7j": 0.6, "1m": 0.1},
}

ALPHA = 0.8


def _is_news(src_track: str) -> bool:
    return (src_track or "").startswith("ia")


def _override_active(criteres: List[Dict[str, Any]]) -> bool:
    for c in criteres:
        if (_is_news(c.get("source_track", ""))
                and c.get("materiality") == "high"
                and c.get("reliability") == "confirmed"
                and (c.get("contrib_pm1") or 0.0) != 0.0):
            return True
    return False


def _apply_cap(news_total: float, quant_total: float, override: bool) -> Tuple[float, bool]:
    # NOTE (A2, audit momentum-family 10/06) : ce rejeu reste VOLONTAIREMENT sur
    # l'ANCIENNE formule (cap basé sur quant_total entier, sans soustraction du
    # momentum). Raison : cet outil rejoue un decision-log FIGÉ du 2026-06-01
    # (LOG_PATH), antérieur à l'introduction du critère momentum_prix_* — ce log
    # ne contient AUCUNE contribution momentum, donc `contrib_momentum` y vaudrait
    # 0 et la formule aveugle au momentum donnerait un résultat strictement
    # identique. L'aligner n'aurait aucun effet et brouillerait l'intention de
    # preuve datée (Points 2+3 du plan horizon de juin). Le cap aveugle au
    # momentum vit dans scoring_analyste.score_actif (chemin de production).
    if override:
        return news_total, False
    if (news_total > 0 > quant_total) or (news_total < 0 < quant_total):
        cap_abs = abs(quant_total) * ALPHA
        if abs(news_total) > cap_abs:
            sign = 1.0 if news_total > 0 else -1.0
            return cap_abs * sign, True
    return news_total, False


def score_horizon(rec: Dict[str, Any], use_new_pertinence: bool, apply_cap: bool) -> Tuple[float, str, Dict[str, float]]:
    fiche_key = rec["fiche_key"]
    horizon = rec["horizon"]
    criteres = rec["criteres"]
    news_total = 0.0
    quant_total = 0.0
    for c in criteres:
        cle = c.get("cle", "")
        vn = c.get("valeur_normalisee")
        if vn is None:
            continue
        poids = float(c.get("poids", 0.0))
        signe = int(c.get("signe", 1))
        # Pertinence : par défaut celle loggée, ou la nouvelle si on est en "after".
        pert = float(c.get("pertinence", 0.0))
        if use_new_pertinence:
            key = (fiche_key, cle)
            if key in PERTINENCE_NEW:
                pert = PERTINENCE_NEW[key][horizon]
        contrib = float(vn) * poids * pert * signe
        if _is_news(c.get("source_track", "")):
            news_total += contrib
        else:
            quant_total += contrib
    override = _override_active(criteres) if apply_cap else False
    news_total_capped = news_total
    cap_applied = False
    if apply_cap:
        news_total_capped, cap_applied = _apply_cap(news_total, quant_total, override)
    score = round(quant_total + news_total_capped, 6)
    concl = "LONG" if score > 0 else ("SHORT" if score < 0 else "TIE")
    diag = {
        "news_total": news_total,
        "quant_total": quant_total,
        "news_total_capped": news_total_capped,
        "cap_applied": cap_applied,
        "override": override,
        "ratio_news": abs(news_total) / (abs(quant_total) + 1e-9),
    }
    return score, concl, diag


def main() -> int:
    # Cellules cibles : (fiche_key, horizon, "doit_passer_a")
    targets = [
        ("or",      "24h", "SHORT"),
        ("vix",     "1m",  "SHORT"),
        ("petrole", "24h", "LONG"),   # doit rester LONG
        ("petrole", "1m",  "LONG"),   # inchangé
        ("sp500",   "24h", "LONG"),   # inchangé (sanity)
        ("sp500",   "1m",  "LONG"),
        # bonus : on imprime aussi le 7j pour les actifs touchés
        ("or",      "7j",  None),
        ("vix",     "24h", None),
        ("vix",     "7j",  None),
        ("petrole", "7j",  None),
    ]
    records = [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_key = {(r["fiche_key"], r["horizon"]): r for r in records}

    print(f"Replay decision-log : {LOG_PATH.name}")
    print(f"Hypothèse : pertinence et cap appliqués sur valeurs_normalisées loggées (le reste inchangé).\n")
    print(f"{'Actif':<10} {'H':<5} {'AVANT':>10} {'AVANT_C':<8} {'APRÈS':>10} {'APRÈS_C':<8} {'cap?':<6} {'over?':<6} {'ratio_news':>10} {'attendu':<8} {'OK'}")
    print("-" * 110)
    failures = 0
    for fiche_key, horizon, expected in targets:
        rec = by_key.get((fiche_key, horizon))
        if rec is None:
            print(f"{fiche_key:<10} {horizon:<5} (cellule absente du log)")
            continue
        score_before, concl_before, _ = score_horizon(rec, use_new_pertinence=False, apply_cap=False)
        score_after, concl_after, diag = score_horizon(rec, use_new_pertinence=True, apply_cap=True)
        ok = "—"
        if expected is not None:
            ok = "✓" if concl_after == expected else "✗ ATTENDU=" + expected
            if concl_after != expected:
                failures += 1
        print(f"{fiche_key:<10} {horizon:<5} {score_before:>+10.3f} {concl_before:<8} {score_after:>+10.3f} {concl_after:<8} "
              f"{str(diag['cap_applied']):<6} {str(diag['override']):<6} {diag['ratio_news']:>10.3f} {str(expected or ''):<8} {ok}")
    print()
    if failures:
        print(f"FAILURES : {failures}")
        return 1
    print("OK : toutes les cellules cibles ont le verdict attendu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
