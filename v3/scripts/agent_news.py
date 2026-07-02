"""TradingApp v3 — Agent News (one-shot, GitHub Actions cron)

Refactor du `agent_news.py` original :
- Suppression de la boucle `while True` / `time.sleep`.
- Exposition de `main()` retournant un exit code (0 OK, 1 fatal).
- Cycle unique : collecte RSS → dédup → blacklist+whitelist → extraction DeepSeek
  (avec garde-fou coût) → écriture locale dans v3/data/events-log.md.
- Le commit git est délégué au workflow .github/workflows/ingest.yml.

Variables d'env attendues (Secrets GitHub) :
- DEEPSEEK_API_KEY (extraction LLM ; absent → mode brut sans LLM, le job ne crash pas)
- HEALTHCHECKS_URL (optionnel, ping en début / fin / fail)

Fuseau : tout est traité en UTC dans le script. Le cron UTC du workflow vise
~7h CET (cf. workflow). Conversion Europe/Paris uniquement pour logs lisibles.
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# Permet l'exécution `python v3/scripts/agent_news.py` depuis la racine du repo
sys.path.insert(0, str(Path(__file__).parent))

from extractor import Extractor  # noqa: E402
from news_collector import collect_all, mark_title_seen  # noqa: E402
from repo_publisher import RepoPublisher  # noqa: E402
from source_monitor import SourceMonitor, write_source_health  # noqa: E402

# Chemin de sortie de source-health.md : constante de MODULE (surchargeable par
# les tests via monkeypatch, cf. conftest _isole_ecritures_data) au lieu d'un
# import inline de config.DATA_DIR au site d'écriture.
from config import DATA_DIR as _DATA_DIR  # noqa: E402
SOURCE_HEALTH_FILE = _DATA_DIR / "source-health.md"


# ============================================================
# Logging
# ============================================================

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("agent_news")


HEALTHCHECKS_URL = os.environ.get("HEALTHCHECKS_URL", "").strip()
# MAX_EXTRACTIONS_PER_CYCLE : plafond de débit (≠ cap COÛT, qui reste dans
# extractor.py soft=$0.50 / hard=$0.80 et n'est PAS touché ici).
# 240/cycle × 3 cycles/j × ~$0.0003/extraction ≈ $0.22/j → sous le soft cap.
# 80 affamait la QUEUE des flux (gnews_silver/vix/nasdaq jamais atteints, cf.
# v3/audit/news-coverage-diagnostic.md). On relève le débit ET on le répartit
# équitablement (round-robin par source) pour que CHAQUE flux dédié soit servi.
MAX_EXTRACTIONS_PER_CYCLE = int(os.environ.get("MAX_EXTRACTIONS_PER_CYCLE", "240"))


def _round_robin_by_source(items: list) -> list:
    """Réordonne `items` en round-robin par source (préserve l'ordre intra-source).

    Le tronquage en aval (`filtered[:MAX]`) prenait les items dans l'ordre de
    COLLECTE (FIFO : RSS de tête d'abord, flux gnews dédiés en queue) → les flux
    des actifs « sourds » (silver/vix/nasdaq, positions 500-900 de la file) étaient
    systématiquement jetés. Le round-robin garantit une QUOTE-PART à chaque source
    avant la troncature : on prend le 1er item de chaque source, puis le 2e, etc.

    Zéro perte d'information : c'est une PERMUTATION de `items` (même contenu, ordre
    différent). Stable intra-source (l'item le plus récent d'un flux reste prioritaire
    si le flux les a déjà triés ainsi).
    """
    from collections import OrderedDict
    buckets: "OrderedDict[str, list]" = OrderedDict()
    for it in items:
        buckets.setdefault(getattr(it, "source", "") or "_unknown", []).append(it)
    interleaved: list = []
    # Tour de table jusqu'à épuisement de tous les buckets.
    while any(buckets.values()):
        for src in list(buckets.keys()):
            bucket = buckets[src]
            if bucket:
                interleaved.append(bucket.pop(0))
    return interleaved


def _ping_healthchecks(suffix: str = "") -> None:
    if not HEALTHCHECKS_URL:
        return
    try:
        requests.get(HEALTHCHECKS_URL + suffix, timeout=10)
    except Exception as e:
        logger.warning("Healthchecks ping failed: %s", e)


def _now_paris() -> str:
    return datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d %H:%M %Z")


def run_one_cycle(publisher: RepoPublisher, extractor: Extractor) -> dict:
    """Cycle complet one-shot. Retourne un dict de stats."""
    started = time.monotonic()
    logger.info("=== Cycle start (Europe/Paris : %s) ===", _now_paris())

    # commit_seen=False : on diffère la dédup jusqu'à extraction réussie (idempotence,
    # cf. audit-ia §1). Les titres NON extraits avec succès reviendront au prochain cycle.
    # monitor : santé des flux ce cycle (appelé/OK/échec/items reçus/items gardés).
    monitor = SourceMonitor()
    result = collect_all(commit_seen=False, monitor=monitor)
    raw = result["raw"]
    deduped = result["deduped"]
    filtered = result["filtered"]
    skipped = result["skipped_non_finance"]

    # Persiste source-health.md immédiatement (même si 0 filtered en aval).
    # Best-effort : ne casse pas le cycle si l'écriture échoue.
    try:
        health_path = SOURCE_HEALTH_FILE
        write_source_health(monitor, health_path)
        s = monitor.summary()
        logger.info(
            "source-health.md écrit : %d appelés, %d OK, %d échec, %d muets, %d skip",
            s["called"], s["ok"], s["ko"], s["muet"], s["skip"],
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("source-health write KO (non bloquant) : %s", e)

    if not filtered:
        logger.info("No finance-relevant items. raw=%d deduped=%d", len(raw), len(deduped))
        return {"raw": len(raw), "deduped": len(deduped), "filtered": 0, "written": 0}

    if len(filtered) > MAX_EXTRACTIONS_PER_CYCLE:
        # Round-robin par source AVANT la troncature : sans ça, le FIFO servait
        # les sources de tête et affamait les flux dédiés en queue (silver/vix/
        # nasdaq jamais atteints → 0 ligne écrite, cf. news-coverage-diagnostic.md).
        filtered = _round_robin_by_source(filtered)
        logger.warning(
            "Tronquage : %d filtered > MAX %d, on garde %d en round-robin par source "
            "(le reste reviendra au prochain cron)",
            len(filtered), MAX_EXTRACTIONS_PER_CYCLE, MAX_EXTRACTIONS_PER_CYCLE,
        )
        filtered = filtered[:MAX_EXTRACTIONS_PER_CYCLE]

    # Extraction.
    # NB: extractor.is_enabled() retourne False si pas d'API key OU si hard cap.
    # En cours de batch, un hard cap franchi → ExtractedEvent.error contient
    # "disabled" → on bascule en raw pour les suivants.
    #
    # Idempotence (audit-ia §1) :
    # - extraction OK            → écrire ligne enrichie + marquer vu (mark_title_seen)
    # - extracteur DELIBERATELY off (pas d'API key OU hard cap) → écrire ligne brute
    #   + marquer vu (mode dégradé volontaire ; pas de retry car aucun appel n'a
    #   eu lieu et ne pourra avoir lieu)
    # - extraction ECHEC réel (timeout, JSON tronqué, erreur réseau) → écrire ligne
    #   brute mais NE PAS marquer vu → l'item reviendra au prochain cycle pour
    #   ré-extraction. Pas de perte silencieuse.
    lines = []
    errors = 0
    retry_pending = 0
    if extractor.is_enabled():
        for item in filtered:
            extracted = extractor.extract(item.title, item.summary)
            if extracted.error and "disabled" in extracted.error:
                # Hard cap franchi en cours de batch → raw, on marque vu (mode off délibéré)
                lines.append(item.as_event_log_line_raw())
                mark_title_seen(item)
            elif extracted.error:
                # Erreur LLM réelle → ligne brute écrite MAIS pas de mark_title_seen
                # → ré-extraction au prochain cycle (idempotence).
                errors += 1
                retry_pending += 1
                lines.append(item.as_event_log_line_raw())
            else:
                # Succès → on commit définitivement
                lines.append(item.as_event_log_line_extracted(extracted))
                mark_title_seen(item)
    else:
        logger.warning("Extractor désactivé (no key ou hard cap) → écriture en mode brut")
        for item in filtered:
            lines.append(item.as_event_log_line_raw())
            mark_title_seen(item)  # mode off délibéré : pas de retry attendu

    publisher.append_to_events_log(lines)
    duration = time.monotonic() - started
    stats = extractor.get_stats()
    logger.info(
        "=== Cycle done in %.1fs | raw=%d dedup=%d filt=%d skip=%d err=%d retry=%d | extractor=%s",
        duration, len(raw), len(deduped), len(filtered), skipped, errors, retry_pending, stats,
    )
    return {
        "raw": len(raw),
        "deduped": len(deduped),
        "filtered": len(filtered),
        "written": len(lines),
        "errors": errors,
        "retry_pending": retry_pending,
        "extractor_stats": stats,
    }


def main() -> int:
    logger.info("TradingApp v3 — Agent News (one-shot) starting at %s", _now_paris())
    _ping_healthchecks("/start")

    try:
        publisher = RepoPublisher()
        extractor = Extractor()
        if extractor.is_enabled():
            logger.info("Extractor enabled (DeepSeek)")
        else:
            logger.warning("Extractor DISABLED — mode brut")

        run_one_cycle(publisher, extractor)
        _ping_healthchecks("")
        return 0
    except Exception as e:
        logger.exception("Fatal in cycle: %s", e)
        _ping_healthchecks("/fail")
        return 1


if __name__ == "__main__":
    sys.exit(main())
