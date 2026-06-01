#!/usr/bin/env python3
"""TradingApp v3 — Analyse complète (kit du matin).

Lecture seule. Agrège tout ce qu'il faut pour juger un run en un coup d'œil :
matrice, biais, mesure forward (VRAI/FAUX), bilan des calls news, Phase 2 (nature/
reposts/T1/T2), flips, et rappel du backtest. Aucune dépendance réseau.

Usage :  python3 v3/scripts/analyse_complete.py
"""
from __future__ import annotations
import glob
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def _section(title: str) -> None:
    print("\n" + "=" * 70 + f"\n {title}\n" + "=" * 70)


def _latest(pattern: str):
    fs = sorted(glob.glob(os.path.join(DATA, pattern)))
    return fs[-1] if fs else None


def run_info_and_matrix() -> None:
    _section("1. RUN — bulletin du jour")
    b = _latest("bulletins/bulletin-*.md")
    if not b:
        print("  (aucun bulletin)"); return
    txt = open(b).read()
    print(f"  Fichier : {os.path.basename(b)}")
    m = re.search(r"(\d+) events analysés", txt)
    print(f"  Events analysés : {m.group(1) if m else '?'}")
    mat = re.search(r"## Matrice.*?\n(.*?)\n## ", txt, re.S)
    if mat:
        rows = [l for l in mat.group(1).splitlines() if l.startswith("| ") and "Actif" not in l and "---" not in l]
        print(f"  Cellules : {len(rows)} lignes | tie-breaks : {txt.count('(tb)')} | 📰 : {txt.count('📰')} | ⚪ : {txt.count('⚪')}")
        for r in rows:
            print("   " + r[:110])


def bilan_news() -> None:
    _section("2. BILAN DES NEWS — le jugement DeepSeek a-t-il marché ?")
    b = _latest("bulletins/bulletin-*.md")
    if not b:
        print("  (aucun bulletin)"); return
    txt = open(b).read()
    m = re.search(r"## Bilan des news.*?\n(.*?)(\n## |\Z)", txt, re.S)
    print(m.group(1).strip() if m else "  (bloc Bilan des news absent)")


def mesure_forward() -> None:
    _section("3. MESURE FORWARD — taux de réussite réel (VRAI/FAUX)")
    p = os.path.join(DATA, "performance.md")
    if not os.path.exists(p):
        print("  (performance.md absent)"); return
    txt = open(p).read()
    c = Counter(re.findall(r"\| (VRAI|FAUX|non-conclusive|suivi-interrompu) \|", txt))
    concl = c["VRAI"] + c["FAUX"]
    taux = f"{100*c['VRAI']//concl}%" if concl else "n/a"
    print(f"  VRAI={c['VRAI']}  FAUX={c['FAUX']}  non-conclusive={c['non-conclusive']}  suivi-interrompu={c['suivi-interrompu']}")
    print(f"  Taux de réussite (sur concluantes) : {taux}  [N concluantes={concl}]")
    elig = re.search(r"éligibles[^:]*: \*\*(\d+)\*\* / (\d+)", txt)
    if elig:
        print(f"  Cellules éligibles : {elig.group(1)}/{elig.group(2)}  (warm-up si 0)")


def phase2_metrics() -> None:
    _section("4. PHASE 2 — nature, reposts, T1/T2")
    dl = _latest("decision-log/*.jsonl")
    if not dl:
        print("  (aucun decision-log)"); return
    lines = [json.loads(l) for l in open(dl)]
    nat = Counter(c["nature"] for d in lines for c in d.get("criteres", [])
                  if str(c.get("source_track", "")).startswith("ia") and c.get("nature"))
    t1 = sum(d.get("p2_T1_faux_flips_evites", 0) for d in lines)
    t2 = sum(d.get("p2_T2_vrais_flips_qualifies", 0) for d in lines)
    print(f"  decision-log : {os.path.basename(dl)}")
    print(f"  nature critères news : {dict(nat) if nat else '(aucune)'}")
    print(f"  T1 (faux changements de tendance évités) = {t1}")
    print(f"  T2 (vrais changements de tendance qualifiés) = {t2}")
    # events-log : reposts / stale
    el = os.path.join(DATA, "events-log.md")
    if os.path.exists(el):
        e = open(el).read()
        nat_el = dict(Counter(re.findall(r"\| (structurel|ponctuel|deja_cote|verbal) \|", e)))
        reposts = e.count("| repost |")
        print(f"  events-log : reposts={reposts}  natures={nat_el}")


def biais() -> None:
    _section("5. BIAIS DIRECTIONNEL — sur tous les runs")
    files = sorted(glob.glob(os.path.join(DATA, "decision-log/*.jsonl")))
    print(f"  {len(files)} runs")
    longs = shorts = 0
    for fp in files[-6:]:
        cells = [json.loads(l) for l in open(fp)]
        c = Counter(d.get("conclusion_pm1") for d in cells)
        tot = c["LONG"] + c["SHORT"]
        pct = 100 * c["LONG"] // max(tot, 1)
        longs += c["LONG"]; shorts += c["SHORT"]
        flag = "  ⚠️ >70%" if pct > 70 else ""
        print(f"   {os.path.basename(fp)[:16]} : {pct}% long{flag}")
    tot = longs + shorts
    print(f"  Médiane récente ~ {100*longs//max(tot,1)}% long (seuil alerte 70%)")


def flips() -> None:
    _section("6. FLIPS — changements de tendance vs veille")
    b = _latest("bulletins/bulletin-*.md")
    if not b:
        return
    txt = open(b).read()
    m = re.search(r"## Flips.*?\n(.*?)(\n## |\Z)", txt, re.S)
    if m:
        fl = [l for l in m.group(1).splitlines() if l.strip().startswith("- ")]
        print(f"  {len(fl)} changement(s) de position :")
        for l in fl[:15]:
            print("   " + l[:100])
    else:
        print("  (section Flips absente)")


def backtest_status() -> None:
    _section("7. BACKTEST QUANT — rappel du verdict")
    r = os.path.join(DATA, "..", "backtest", "REPORT.md")
    r = os.path.normpath(r)
    if os.path.exists(r):
        txt = open(r).read()
        m = re.search(r"## Verdict.*?\n(.*?)\n##", txt, re.S)
        print("  " + (m.group(1).strip()[:300] if m else "voir v3/backtest/REPORT.md"))
    else:
        print("  (pas de backtest)")


def caveat() -> None:
    _section("8. RAPPEL STATISTIQUE")
    print("  ⚠️ Mode shadow / warm-up : tant que N_eff < 15/cellule, aucun chiffre")
    print("     n'est statistiquement significatif. Signal précoce ≠ edge prouvé.")
    print("     Backtest quant v1 = NO-GO sur sous-ensemble price-only (partiel).")


if __name__ == "__main__":
    print("ANALYSE COMPLÈTE — TradingApp v3")
    for fn in (run_info_and_matrix, bilan_news, mesure_forward, phase2_metrics, biais, flips, backtest_status, caveat):
        try:
            fn()
        except Exception as e:  # robustesse : une section qui casse ne tue pas le reste
            print(f"  [section {fn.__name__} erreur : {type(e).__name__}: {e}]")
    print("\n" + "=" * 70)
