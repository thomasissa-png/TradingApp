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


def _sample_news(source: str, n: int) -> list:
    """Retourne [(titre, snippet, source_name)]."""
    if source == "rss":
        try:
            import news_collector as nc
            res = nc.collect_all(commit_seen=False)
            items = res.get("filtered") or res.get("deduped") or res.get("raw") or []
            return [(it.title, getattr(it, "summary", ""), it.source) for it in items[:n]]
        except Exception as e:  # noqa: BLE001
            print(f"[warn] fetch RSS échoué ({e}) → fallback events-log")
    # source == events : relire les derniers titres de events-log
    log = ROOT / "data" / "events-log.md"
    out = []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| 20"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) >= 8:
                out.append((cols[3], "", cols[7]))  # trigger, -, source
    return out[-n:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--source", choices=["events", "rss"], default="rss")
    args = ap.parse_args()

    ext = ex.Extractor()
    lines = ["# Test extraction DeepSeek — rapport traçable", ""]
    lines.append(f"- Modèle : `{getattr(ext, 'model', 'n/a')}` · prompt `{ex.PROMPT_VERSION}` · temperature=0")
    lines.append(f"- Source des news : `{args.source}` · n={args.n}")
    lines.append("")

    if not ext.is_enabled():
        msg = ("⚠️ DEEPSEEK_API_KEY absente → impossible d'appeler DeepSeek. "
               "Lance ce script via le workflow GitHub `test-extraction` (clés présentes).")
        print(msg)
        lines.append(msg)
        REPORT.write_text("\n".join(lines), encoding="utf-8")
        return 0

    news = _sample_news(args.source, args.n)
    if not news:
        print("Aucune news à tester.")
        return 1

    # System prompt + few-shots : constants → résumé une fois.
    lines.append("## Contexte envoyé à CHAQUE appel (constant)")
    lines.append(f"- System prompt : {len(ex.SYSTEM_PROMPT)} caractères (rôle desk news-trading + schéma + 8 règles)")
    lines.append(f"- Few-shots : {len(ex.FEW_SHOTS)} exemples calibrés")
    lines.append("- Seul le message ci-dessous (la news) change d'un appel à l'autre.")
    lines.append("")

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
            lines.append(f"## News {i} — ERREUR : {e}")
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

        lines += [
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
        print(f"News {i}: {title[:60]}… → {len(ev.impacts)} impacts {[imp.asset for imp in ev.impacts]}")

    stats = ext.get_stats()
    lines.append(f"## Coût total run : {json.dumps(stats, ensure_ascii=False)}")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRapport écrit : {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
