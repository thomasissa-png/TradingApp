"""TradingApp v3 — Source Monitor (santé des flux news par cycle).

Trace, pour CHAQUE flux appelé pendant un run de news_collector :
- appelé (bool)              : la requête a-t-elle été tentée ?
- ok (bool)                  : la requête a-t-elle abouti (HTTP 2xx + parse OK) ?
- http_status (int|str)      : code HTTP ou type d'erreur ("timeout", "skip:no_api_key"…)
- items_fetched (int)        : items bruts reçus avant tout filtre
- items_kept (int)           : items survivants après dédup + blacklist + whitelist
- reason (str)               : raison du 0-kept si applicable
                               ("HTTP 403", "0 reçus", "30 reçus / 0 gardés après filtre finance",
                                "skip: pas de clé API")

Persisté dans `v3/data/source-health.md` (réécrit à chaque run) + rendu dans
le briefing via `render_briefing_block()` + lu par `analyse_complete.py`.

Pas de réseau, pas de LLM. Module pur (idempotent, testable).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================
# Modèle
# ============================================================

@dataclass
class SourceHealth:
    name: str
    called: bool = False
    ok: bool = False
    http_status: str = ""           # "200", "403", "timeout", "skip:no_api_key", "parse_error"
    items_fetched: int = 0          # bruts reçus
    items_kept: int = 0             # après filtres downstream
    reason: str = ""                # raison du 0-kept si applicable

    def status_icon(self) -> str:
        if not self.called:
            return "⏭"
        if not self.ok:
            return "❌"
        if self.items_kept == 0:
            return "⚪"  # appelé, OK, mais 0 kept (muet)
        return "✅"


@dataclass
class SourceMonitor:
    """Accumulateur thread-unsafe (appelé séquentiellement par news_collector)."""
    by_name: dict = field(default_factory=dict)

    def record_call(
        self,
        name: str,
        ok: bool,
        http_status: str,
        items_fetched: int,
        reason: str = "",
    ) -> None:
        """Enregistre un appel à un flux. Si déjà présent (ex: gnews appelé sur N
        requêtes), on additionne items_fetched et on garde le pire ok/http_status.
        """
        existing = self.by_name.get(name)
        if existing is None:
            self.by_name[name] = SourceHealth(
                name=name,
                called=True,
                ok=ok,
                http_status=http_status,
                items_fetched=items_fetched,
                reason=reason,
            )
            return
        # Aggrégation multi-requêtes (cas gnews/newsapi)
        existing.called = True
        existing.items_fetched += items_fetched
        if not ok:
            existing.ok = False
            existing.http_status = http_status or existing.http_status
            if reason:
                existing.reason = reason
        # Si déjà ok, on garde ok=True. Si déjà ko, on reste ko.

    def record_skip(self, name: str, reason: str) -> None:
        """Flux non appelé délibérément (ex: pas de clé API)."""
        self.by_name[name] = SourceHealth(
            name=name,
            called=False,
            ok=False,
            http_status="skip",
            items_fetched=0,
            items_kept=0,
            reason=reason,
        )

    def set_items_kept(self, kept_by_source: dict) -> None:
        """Renseigne items_kept (post-filtre) par flux. Appelé en fin de cycle.
        kept_by_source : {source_name: count_kept_after_dedup_blacklist_whitelist}
        """
        for name, kept in kept_by_source.items():
            health = self.by_name.get(name)
            if health is None:
                # Source apparue dans les items mais pas enregistrée — edge case
                # (ex: collecte structurée multi-requêtes agrégée sous "gnews").
                continue
            health.items_kept = kept
            # Renseigne reason si muet
            if health.called and health.ok and kept == 0:
                if health.items_fetched == 0:
                    health.reason = "0 reçus"
                else:
                    health.reason = (
                        f"{health.items_fetched} reçus / 0 gardés "
                        f"(dédup + blacklist + filtre finance)"
                    )

    def summary(self) -> dict:
        called = [h for h in self.by_name.values() if h.called]
        ok = [h for h in called if h.ok]
        ko = [h for h in called if not h.ok]
        muet = [h for h in ok if h.items_kept == 0]
        skip = [h for h in self.by_name.values() if not h.called]
        return {
            "total": len(self.by_name),
            "called": len(called),
            "ok": len(ok),
            "ko": len(ko),
            "muet": len(muet),
            "skip": len(skip),
            "items_fetched": sum(h.items_fetched for h in called),
            "items_kept": sum(h.items_kept for h in called),
        }


# ============================================================
# Persistance source-health.md
# ============================================================

def write_source_health(
    monitor: SourceMonitor,
    out_path: Path,
    now: Optional[datetime] = None,
) -> Path:
    """Réécrit v3/data/source-health.md avec l'état courant."""
    now = now or datetime.now(timezone.utc)
    s = monitor.summary()
    lines = []
    lines.append("# Santé des sources news")
    lines.append("")
    lines.append(f"_Cycle : {now.strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append("")
    lines.append(
        f"**Synthèse** : {s['total']} flux configurés, {s['called']} appelés, "
        f"{s['ok']} OK, {s['ko']} en échec, {s['muet']} muets (0 gardé), "
        f"{s['skip']} skip (pas de clé API). "
        f"Items : {s['items_fetched']} reçus → {s['items_kept']} gardés."
    )
    lines.append("")
    lines.append("| | Flux | HTTP | Reçus | Gardés | Raison |")
    lines.append("|---|---|---|---:|---:|---|")
    # Tri : muets et échecs d'abord (priorité de debug), puis OK
    def sort_key(h: SourceHealth):
        # Ordre : ko, muet, skip, ok-actif
        if h.called and not h.ok:
            return (0, h.name)
        if h.called and h.ok and h.items_kept == 0:
            return (1, h.name)
        if not h.called:
            return (2, h.name)
        return (3, h.name)
    for h in sorted(monitor.by_name.values(), key=sort_key):
        reason = (h.reason or "").replace("|", "/")
        lines.append(
            f"| {h.status_icon()} | {h.name} | {h.http_status or '-'} | "
            f"{h.items_fetched} | {h.items_kept} | {reason} |"
        )
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


# ============================================================
# Lecture source-health.md (pour briefing + analyse_complete)
# ============================================================

def render_briefing_block(health_path: Path) -> str:
    """Génère le bloc markdown `## Santé des sources` pour le bulletin.

    Lit source-health.md (déjà écrit par agent_news), extrait synthèse + flux
    en échec / muets. Si le fichier n'existe pas → bloc minimal indicatif.
    """
    lines = ["## Santé des sources", ""]
    if not health_path.exists():
        lines.append("_source-health.md indisponible (cycle news pas encore exécuté)._")
        lines.append("")
        return "\n".join(lines)

    txt = health_path.read_text(encoding="utf-8")
    # Extraire synthèse (ligne **Synthèse** : ...)
    import re
    m = re.search(r"\*\*Synthèse\*\* : ([^\n]+)", txt)
    if m:
        lines.append(m.group(1).strip())
        lines.append("")

    # Extraire les lignes du tableau avec ❌ ou ⚪
    problems = []
    for ln in txt.splitlines():
        if ln.startswith("| ❌ ") or ln.startswith("| ⚪ "):
            # Format : | icon | name | http | recus | kept | reason |
            parts = [c.strip() for c in ln.split("|")[1:-1]]
            if len(parts) >= 6:
                icon, name, http, recus, kept, reason = parts[:6]
                problems.append(f"- {icon} `{name}` ({http}, reçus={recus}, gardés={kept}) — {reason or 'n/a'}")
    if problems:
        lines.append("**Flux à problème :**")
        lines.extend(problems[:15])  # cap à 15 pour pas saturer le briefing
        if len(problems) > 15:
            lines.append(f"- _(+{len(problems) - 15} autres, voir source-health.md)_")
        lines.append("")
    else:
        lines.append("Tous les flux appelés ont livré des items utiles.")
        lines.append("")
    return "\n".join(lines)


def read_summary(health_path: Path) -> dict:
    """Pour analyse_complete : extrait la synthèse en dict simple."""
    if not health_path.exists():
        return {}
    txt = health_path.read_text(encoding="utf-8")
    import re
    out = {}
    m = re.search(r"\*\*Synthèse\*\* : ([^\n]+)", txt)
    if m:
        out["synthese"] = m.group(1).strip()
    # Compte les ❌ et ⚪ dans le tableau
    out["ko"] = sum(1 for l in txt.splitlines() if l.startswith("| ❌ "))
    out["muet"] = sum(1 for l in txt.splitlines() if l.startswith("| ⚪ "))
    out["ok"] = sum(1 for l in txt.splitlines() if l.startswith("| ✅ "))
    out["skip"] = sum(1 for l in txt.splitlines() if l.startswith("| ⏭ "))
    return out
