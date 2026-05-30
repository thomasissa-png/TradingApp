"""TradingApp v3 — Test traçable de l'extraction DeepSeek.

But : montrer EXACTEMENT, pour de vraies news, ce que DeepSeek reçoit et interprète.
Pour chaque news :
  1. INPUT brut    : titre + snippet + source
  2. PROMPT envoyé : le message user (le system+few-shots sont constants, résumés)
  3. RÉPONSE BRUTE : le JSON exact renvoyé par DeepSeek
  4. INTERPRÉTÉ    : l'ExtractedEvent parsé (impacts directionnels, materiality, reliability…)
  5. ROUTING       : vers quels actifs/critères ça partirait

Sortie : rapport markdown `v3/data/test-extraction-report.md` (commité) + stdout.
Usage : python v3/scripts/test_extraction.py [--n 6] [--source events|rss]
  --source events : rejoue les N derniers titres de events-log.md (rapide, pas de fetch)
  --source rss    : fetch en direct quelques RSS (vrai bout-en-bout)
Nécessite DEEPSEEK_API_KEY. Sans clé → explique et sort proprement (zéro invention).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import extractor as ex  # noqa: E402

REPORT = ROOT / "data" / "test-extraction-report.md"
IA_TO_ACTIF = {
    "CAC40": "cac_40", "SP500": "sp500", "NASDAQ": "nasdaq", "EURUSD": "eurusd",
    "BRENT": "petrole", "VIX": "vix", "GOLD": "or", "SILVER": "argent",
    "COPPER": "cuivre", "COFFEE": "cafe", "COCOA": "cacao", "WHEAT": "ble",
}


def _sample_news(source: str, n: int) -> tuple:
    """Retourne (news, funnel) où news=[(titre, snippet, source_name)] et
    funnel = dict {raw, deduped, filtered, skipped} pour l'entonnoir.
    n <= 0 → TOUTES les news filtrées (pas de limite)."""
    funnel = {}
    if source == "rss":
        try:
            import news_collector as nc
            res = nc.collect_all(commit_seen=False)
            funnel = {
                "raw": len(res.get("raw") or []),
                "deduped": len(res.get("deduped") or []),
                "filtered": len(res.get("filtered") or []),
                "skipped_non_finance": res.get("skipped_non_finance", 0),
            }
            items = res.get("filtered") or res.get("deduped") or res.get("raw") or []
            if n and n > 0:
                items = items[:n]
            return [(it.title, getattr(it, "summary", ""), it.source) for it in items], funnel
        except Exception as e:  # noqa: BLE001
            print(f"[warn] fetch RSS échoué ({e}) → fallback events-log")
    # source == events : relire les titres de events-log
    log = ROOT / "data" / "events-log.md"
    out = []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| 20"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 8:
                out.append((cols[3], "", cols[7]))  # trigger, -, source
    if n and n > 0:
        out = out[-n:]
    funnel = {"raw": len(out), "deduped": len(out), "filtered": len(out), "skipped_non_finance": 0}
    return out, funnel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=0, help="0 = TOUTES les news du cycle (défaut)")
    ap.add_argument("--source", choices=["events", "rss"], default="rss")
    args = ap.parse_args()

    ext = ex.Extractor()
    lines = ["# Test extraction DeepSeek — rapport traçable", ""]
    lines.append(f"- Modèle : `{getattr(ext, 'model', 'n/a')}` · prompt `{ex.PROMPT_VERSION}` · temperature=0")
    lines.append(f"- Source des news : `{args.source}` · n={args.n if args.n else 'TOUTES'}")
    lines.append("")

    if not ext.is_enabled():
        msg = ("⚠️ DEEPSEEK_API_KEY absente → impossible d'appeler DeepSeek. "
               "Lance ce script via le workflow GitHub `test-extraction` (clés présentes).")
        print(msg)
        lines.append(msg)
        REPORT.write_text("\n".join(lines), encoding="utf-8")
        return 0

    news, funnel = _sample_news(args.source, args.n)
    lines.append("## Entonnoir de collecte")
    lines.append(f"- brut récupéré : **{funnel.get('raw', 0)}** → après dédup : **{funnel.get('deduped', 0)}** "
                 f"→ après pré-filtre finance : **{funnel.get('filtered', 0)}** "
                 f"(écartées non-finance : {funnel.get('skipped_non_finance', 0)})")
    lines.append(f"- **{len(news)} news envoyées à DeepSeek** dans ce run")
    lines.append("")
    if not news:
        print("Aucune news à tester.")
        lines.append("_Aucune news après filtrage._")
        REPORT.write_text("\n".join(lines), encoding="utf-8")
        return 0

    # System prompt + few-shots : constants → résumé une fois.
    lines.append("## Contexte envoyé à CHAQUE appel (constant)")
    lines.append(f"- System prompt : {len(ex.SYSTEM_PROMPT)} caractères (rôle desk news-trading + schéma + 8 règles)")
    lines.append(f"- Few-shots : {len(ex.FEW_SHOTS)} exemples calibrés")
    lines.append("- Seul le message ci-dessous (la news) change d'un appel à l'autre.")
    lines.append("")

    # Accumulateurs : table récap + détail séparés (table insérée avant le détail).
    recap_rows = []          # lignes de la table de synthèse
    detail_lines = []        # blocs détaillés par news
    n_avec_impact = 0
    n_sans_impact = 0
    n_erreurs = 0
    asset_counter = {}

    for i, (title, snippet, src) in enumerate(news, 1):
        msgs = ext._build_messages(title, snippet)
        user_msg = msgs[-1]["content"]
        start = time.monotonic()
        try:
            resp = ext.client.chat.completions.create(
                model=ext.model, messages=msgs, temperature=0,
                response_format={"type": "json_object"}, max_tokens=800, timeout=30,
            )
            raw = resp.choices[0].message.content
            dur = int((time.monotonic() - start) * 1000)
            tin = resp.usage.prompt_tokens if resp.usage else 0
            tout = resp.usage.completion_tokens if resp.usage else 0
        except Exception as e:  # noqa: BLE001
            n_erreurs += 1
            recap_rows.append(f"| {i} | {title[:55]} | `{src}` | — | — | ERREUR |")
            detail_lines.append(f"## News {i} — ERREUR : {e}\n")
            continue

        data = json.loads(raw)
        ev = ex.ExtractedEvent(
            impacts=ex._parse_impacts(data.get("impacts")),
            category=ex._norm_enum(data.get("category"), ex._CAT_SET, default="other"),
            subcat=str(data.get("subcat") or "")[:80],
            trigger=str(data.get("trigger") or title)[:250],
            news_zone=str(data.get("news_zone") or "")[:30],
            reliability=ex._norm_enum(data.get("reliability"), ex._REL_SET, default=""),
            materiality=ex._norm_enum(data.get("materiality"), ex._MAT_SET, default="low"),
        )
        routed = [f"{imp.asset}→{IA_TO_ACTIF.get(imp.asset,'?')} {imp.direction} ({imp.confidence})"
                  for imp in ev.impacts]

        # Stats récap
        if ev.impacts:
            n_avec_impact += 1
            for imp in ev.impacts:
                asset_counter[imp.asset] = asset_counter.get(imp.asset, 0) + 1
        else:
            n_sans_impact += 1
        impacts_short = ", ".join(f"{imp.asset} {imp.direction[:1]}" for imp in ev.impacts) or "—"
        recap_rows.append(
            f"| {i} | {title[:55].replace('|','/')} | `{src}` | {ev.category} | {ev.materiality}/{ev.reliability} | {impacts_short} |"
        )

        detail_lines += [
            f"## News {i}",
            f"**1. INPUT** — source `{src}`",
            f"> {title}",
            (f"> _snippet : {snippet[:300]}_" if snippet else "> _(pas de snippet)_"),
            "",
            "**2. PROMPT envoyé (message news)**",
            "```", user_msg, "```",
            "**3. RÉPONSE BRUTE DeepSeek (JSON exact)**",
            "```json", raw.strip(), "```",
            "**4. INTERPRÉTÉ**",
            f"- catégorie : `{ev.category}` / `{ev.subcat}` · zone `{ev.news_zone}`",
            f"- matérialité : **{ev.materiality}** · fiabilité : **{ev.reliability}**",
            f"- impacts : {len(ev.impacts)} → " + (", ".join(f'{imp.asset} **{imp.direction}** ({imp.confidence})' for imp in ev.impacts) or "_aucun (filtré)_"),
            "",
            "**5. ROUTING (vers quels critères/actifs)**",
            ("- " + " · ".join(routed)) if routed else "- _aucun actif tradable impacté → n'alimente aucun critère_",
            f"\n_coût : {tin} tok in / {tout} tok out · {dur} ms_",
            "\n---\n",
        ]
        print(f"News {i}/{len(news)}: {title[:55]}… → {len(ev.impacts)} impacts {[imp.asset for imp in ev.impacts]}")

    # --- Assemblage : synthèse + table récap + détail ---
    stats = ext.get_stats()
    assets_sorted = sorted(asset_counter.items(), key=lambda kv: -kv[1])
    lines.append("## Synthèse")
    lines.append(f"- News analysées : **{len(news)}** · avec impact tradable : **{n_avec_impact}** "
                 f"· sans impact (écartées) : **{n_sans_impact}** · erreurs : **{n_erreurs}**")
    if assets_sorted:
        lines.append("- Actifs les plus touchés : " + ", ".join(f"{a} ({c})" for a, c in assets_sorted))
    lines.append(f"- Coût total : `{json.dumps(stats, ensure_ascii=False)}`")
    lines.append("")
    lines.append("## Table récap (toutes les news)")
    lines.append("| # | Titre | Source | Catégorie | Matér./Fiab. | Impacts |")
    lines.append("|---|---|---|---|---|---|")
    lines += recap_rows
    lines.append("")
    lines.append("## Détail par news")
    lines.append("")
    lines += detail_lines

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRapport écrit : {REPORT}  ({len(news)} news, {n_avec_impact} avec impact, {n_erreurs} erreurs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
