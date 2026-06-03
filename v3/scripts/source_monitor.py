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
    # Compteurs multi-requêtes (sources type gnews/newsapi : N requêtes / source)
    req_total: int = 0              # nombre de requêtes tentées sous ce nom
    req_ok: int = 0                 # requêtes ayant abouti (HTTP 2xx + parse)
    req_ko: int = 0                 # requêtes en échec
    failed_requests: list = field(default_factory=list)  # libellés des requêtes fautives

    def is_partial(self) -> bool:
        """Vrai si la source est multi-requêtes ET a un mix succès/échec.
        0 < req_ko < req_total → certaines requêtes échouent, d'autres marchent.
        """
        return self.req_total > 1 and 0 < self.req_ko < self.req_total

    def status_icon(self) -> str:
        if not self.called:
            return "⏭"
        # Partiel : des données utiles arrivent malgré des requêtes fautives →
        # PAS une panne (pas de ❌ rouge), simple avertissement de diagnostic.
        if self.is_partial():
            return "⚠️"
        if not self.ok:
            return "❌"
        if self.items_kept == 0:
            return "⚪"  # appelé, OK, mais 0 kept (muet)
        return "✅"

    def status_label(self) -> str:
        """Libellé court du statut, avec ratio R/N pour le partiel."""
        if not self.called:
            return "skip"
        if self.is_partial():
            return f"partiel ({self.req_ok}/{self.req_total})"
        if not self.ok:
            return "échec"
        if self.items_kept == 0:
            return "muet"
        return "OK"


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
        query: str = "",
    ) -> None:
        """Enregistre un appel à un flux. Si déjà présent (ex: gnews appelé sur N
        requêtes), on additionne items_fetched et on compte succès/échecs par
        requête pour déterminer un statut à 3 états (OK / partiel / ❌).

        `ok` global = "au moins une requête a réussi" (la source n'est en panne
        que si TOUTES ses requêtes échouent). Un mix succès/échec donne le statut
        ``partiel`` (cf. SourceHealth.is_partial) qui n'est PAS traité comme une
        panne tant que des données utiles arrivent.

        `query` (optionnel) : libellé de la requête, conservé pour diagnostic si
        elle échoue.
        """
        existing = self.by_name.get(name)
        if existing is None:
            existing = SourceHealth(name=name, called=True)
            self.by_name[name] = existing

        existing.called = True
        existing.items_fetched += items_fetched
        existing.req_total += 1
        if ok:
            existing.req_ok += 1
        else:
            existing.req_ko += 1
            existing.failed_requests.append(query or http_status or "?")
            # On garde le dernier http_status/reason d'échec pour diagnostic.
            existing.http_status = http_status or existing.http_status
            if reason:
                existing.reason = reason
        # http_status affiché : un code de succès si on n'a encore aucun échec.
        if ok and existing.req_ko == 0:
            existing.http_status = http_status or existing.http_status
        # ok global = au moins une requête a abouti (non-panne totale).
        existing.ok = existing.req_ok > 0
        # Raison de diagnostic du partiel : ratio + requêtes fautives (cap 3).
        if existing.is_partial():
            failed = existing.failed_requests[:3]
            suffix = "…" if len(existing.failed_requests) > 3 else ""
            existing.reason = (
                f"{existing.req_ko}/{existing.req_total} requêtes en échec : "
                f"{', '.join(str(f) for f in failed)}{suffix}"
            )

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
            # Ne pas écraser la raison d'un partiel (elle sert au diagnostic
            # des requêtes fautives) — le partiel n'est pas un état "muet".
            if health.is_partial():
                continue
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
        partiel = [h for h in called if h.is_partial()]
        # OK = appelé, non-partiel, au moins une requête réussie.
        ok = [h for h in called if h.ok and not h.is_partial()]
        # KO = panne réelle : toutes les requêtes ont échoué (et pas partiel).
        ko = [h for h in called if not h.ok and not h.is_partial()]
        muet = [h for h in ok if h.items_kept == 0]
        skip = [h for h in self.by_name.values() if not h.called]
        return {
            "total": len(self.by_name),
            "called": len(called),
            "ok": len(ok),
            "partiel": len(partiel),
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
        f"{s['ok']} OK, {s['partiel']} partiels, {s['ko']} en échec, "
        f"{s['muet']} muets (0 gardé), {s['skip']} skip (pas de clé API). "
        f"Items : {s['items_fetched']} reçus → {s['items_kept']} gardés."
    )
    lines.append("")
    lines.append(
        "_Légende : ✅ OK · ⚠️ partiel (R/N requêtes — données utiles reçues, "
        "pas une panne) · ❌ échec total · ⚪ muet (0 gardé après filtre) · "
        "⏭ skip (pas de clé API)._"
    )
    lines.append("")
    lines.append("| | Statut | Flux | HTTP | Reçus | Gardés | Raison |")
    lines.append("|---|---|---|---|---:|---:|---|")
    # Tri : échecs réels d'abord, puis partiels, muets, skip, OK (priorité debug).
    def sort_key(h: SourceHealth):
        if h.called and not h.ok and not h.is_partial():
            return (0, h.name)  # panne réelle
        if h.is_partial():
            return (1, h.name)  # avertissement partiel
        if h.called and h.ok and h.items_kept == 0:
            return (2, h.name)  # muet
        if not h.called:
            return (3, h.name)  # skip
        return (4, h.name)      # OK actif
    for h in sorted(monitor.by_name.values(), key=sort_key):
        reason = (h.reason or "").replace("|", "/")
        lines.append(
            f"| {h.status_icon()} | {h.status_label()} | {h.name} | "
            f"{h.http_status or '-'} | "
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

    # Extraire les lignes du tableau, en trois groupes DISTINCTS :
    #  - problems (❌) = VRAIES pannes (0 reçu / auth / dead) → bloquant.
    #  - mutes    (⚪) = flux muets (reçus>0 mais 0 gardé = tout dédupliqué/
    #                    filtré) → NORMAL, non bloquant, ne doit PAS affoler.
    #  - partials (⚠️) = requêtes fautives mais données utiles reçues → non bloquant.
    # On ne change PAS le calcul du statut (déjà en place), seulement le
    # regroupement d'affichage pour ne plus présenter les muets comme problèmes.
    # Format colonnes : | icon | statut | name | http | recus | kept | reason |
    problems = []
    mutes = []
    partials = []
    for ln in txt.splitlines():
        is_problem = ln.startswith("| ❌ ")
        is_mute = ln.startswith("| ⚪ ")
        is_partial = ln.startswith("| ⚠️ ")
        if not (is_problem or is_mute or is_partial):
            continue
        parts = [c.strip() for c in ln.split("|")[1:-1]]
        if len(parts) >= 7:
            icon, _status, name, http, recus, kept, reason = parts[:7]
        elif len(parts) >= 6:
            # Compat ancien format sans colonne Statut.
            icon, name, http, recus, kept, reason = parts[:6]
        else:
            continue
        entry = f"- {icon} `{name}` ({http}, reçus={recus}, gardés={kept}) — {reason or 'n/a'}"
        if is_partial:
            partials.append(entry)
        elif is_mute:
            mutes.append(entry)
        else:
            problems.append(entry)
    if problems:
        lines.append("**Flux à problème :**")
        lines.extend(problems[:15])  # cap à 15 pour pas saturer le briefing
        if len(problems) > 15:
            lines.append(f"- _(+{len(problems) - 15} autres, voir source-health.md)_")
        lines.append("")
    else:
        lines.append("Aucune vraie panne : tous les flux appelés ont répondu.")
        lines.append("")
    if mutes:
        lines.append("**Flux muets** (normal — tout dédupliqué/filtré, non bloquant) :")
        lines.extend(mutes[:10])
        if len(mutes) > 10:
            lines.append(f"- _(+{len(mutes) - 10} autres, voir source-health.md)_")
        lines.append("")
    if partials:
        lines.append("**Flux partiels** (données reçues, requêtes fautives non bloquantes) :")
        lines.extend(partials[:10])
        if len(partials) > 10:
            lines.append(f"- _(+{len(partials) - 10} autres, voir source-health.md)_")
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
    # Compte les statuts dans le tableau (partiel ⚠️ distinct de la panne ❌).
    out["ko"] = sum(1 for l in txt.splitlines() if l.startswith("| ❌ "))
    out["partiel"] = sum(1 for l in txt.splitlines() if l.startswith("| ⚠️ "))
    out["muet"] = sum(1 for l in txt.splitlines() if l.startswith("| ⚪ "))
    out["ok"] = sum(1 for l in txt.splitlines() if l.startswith("| ✅ "))
    out["skip"] = sum(1 for l in txt.splitlines() if l.startswith("| ⏭ "))
    return out
