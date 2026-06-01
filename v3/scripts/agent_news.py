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
MAX_EXTRACTIONS_PER_CYCLE = int(os.environ.get("MAX_EXTRACTIONS_PER_CYCLE", "80"))


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
        from config import DATA_DIR
        health_path = DATA_DIR / "source-health.md"
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
        logger.warning(
            "Tronquage : %d filtered > MAX %d, on garde %d (le reste reviendra au prochain cron)",
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
