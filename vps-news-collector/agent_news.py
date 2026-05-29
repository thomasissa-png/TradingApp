"""TradingApp v3 — Agent News (Phase 2.1 : avec extracteur DeepSeek)

Loop infini :
- Toutes les 15 min, collecte RSS (BBC + CNBC + Investing).
- Dédup Jaccard 0,65.
- Pré-filtre finance (mots-clés).
- Pour chaque item retenu : extraction structurée via DeepSeek V4 Flash.
- Append des lignes enrichies (L1/L2/trigger/cours/...) dans events-log.md via Drive API.
- Ping Healthchecks.io.
- Log coût estimé par cycle.
"""

import os
import logging
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from news_collector import collect_rss_phase21
from drive_publisher import DrivePublisher
from extractor import Extractor

# ============================================================
# Setup
# ============================================================

load_dotenv()

LOG_DIR = Path(os.environ.get("LOG_DIR", "/opt/tradingapp/data/logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / f"news-collector-{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
logger = logging.getLogger("agent_news")


HEALTHCHECKS_URL = os.environ.get("HEALTHCHECKS_URL", "")
POLL_INTERVAL_SEC = 15 * 60
MAX_EXTRACTIONS_PER_CYCLE = int(os.environ.get("MAX_EXTRACTIONS_PER_CYCLE", "50"))


def _ping_healthchecks(suffix: str = ""):
    if not HEALTHCHECKS_URL:
        return
    try:
        requests.get(HEALTHCHECKS_URL + suffix, timeout=10)
    except Exception as e:
        logger.warning("Healthchecks ping failed: %s", e)


def run_one_cycle(publisher: DrivePublisher, extractor: Extractor):
    """Un cycle complet : collecte → dédup → filtre → extraction → écriture Drive."""
    started = time.monotonic()
    logger.info("=== Cycle start ===")

    try:
        result = collect_rss_phase21()
    except Exception as e:
        logger.error("collect_rss failed: %s", e, exc_info=True)
        _ping_healthchecks("/fail")
        return

    raw = result["raw"]
    deduped = result["deduped"]
    filtered = result["filtered"]
    skipped_non_fin = result["skipped_non_finance"]

    if not filtered:
        logger.info("No finance-relevant items this cycle. raw=%d deduped=%d", len(raw), len(deduped))
        _ping_healthchecks("")
        return

    # Garde-fou coût : si plus de MAX par cycle, on tronque (les autres reviendront au prochain cycle si pas dédupliqués)
    if len(filtered) > MAX_EXTRACTIONS_PER_CYCLE:
        logger.warning("Tronquage : %d filtered > MAX %d, on en garde %d",
                       len(filtered), MAX_EXTRACTIONS_PER_CYCLE, MAX_EXTRACTIONS_PER_CYCLE)
        filtered = filtered[:MAX_EXTRACTIONS_PER_CYCLE]

    # Extraction
    lines = []
    cycle_tokens_in = 0
    cycle_tokens_out = 0
    cycle_errors = 0
    if extractor.is_enabled():
        for item in filtered:
            extracted = extractor.extract(item.title, item.summary)
            lines.append(item.as_event_log_line_extracted(extracted))
            cycle_tokens_in += extracted.tokens_in
            cycle_tokens_out += extracted.tokens_out
            if extracted.error:
                cycle_errors += 1
        cycle_cost = (cycle_tokens_in * 0.14 + cycle_tokens_out * 0.28) / 1_000_000
        logger.info(
            "Extraction terminée : %d items, %d errors, %d tokens in / %d tokens out, cost ~$%.4f",
            len(filtered), cycle_errors, cycle_tokens_in, cycle_tokens_out, cycle_cost,
        )
    else:
        # Mode passif : lignes brutes sans extraction
        logger.info("Extractor désactivé → écriture en mode brut sans L1/L2/cours")
        for item in filtered:
            lines.append(item.as_event_log_line_raw())

    # Écriture Drive
    try:
        publisher.append_to_events_log(lines)
        logger.info("Appended %d events to Drive events-log.md", len(lines))
    except Exception as e:
        logger.error("Drive append failed: %s", e, exc_info=True)
        _ping_healthchecks("/fail")
        return

    duration = time.monotonic() - started
    stats = extractor.get_stats()
    logger.info(
        "=== Cycle done in %.1fs | raw=%d deduped=%d filtered=%d skipped_non_fin=%d | "
        "extractor stats: %s",
        duration, len(raw), len(deduped), len(filtered), skipped_non_fin, stats,
    )
    _ping_healthchecks("")


def main():
    logger.info("TradingApp v3 News Collector — Phase 2.1 starting")
    _ping_healthchecks("/start")

    try:
        publisher = DrivePublisher()
        logger.info("Drive publisher initialized")
    except Exception as e:
        logger.critical("Failed to init Drive publisher: %s", e, exc_info=True)
        _ping_healthchecks("/fail")
        raise

    extractor = Extractor()
    if extractor.is_enabled():
        logger.info("Extractor enabled (DeepSeek)")
    else:
        logger.warning("Extractor DISABLED — service en mode brut (colonnes L1/L2/etc vides)")

    while True:
        try:
            run_one_cycle(publisher, extractor)
        except KeyboardInterrupt:
            logger.info("Shutdown requested.")
            break
        except Exception as e:
            logger.error("Unexpected error in cycle: %s", e, exc_info=True)
            _ping_healthchecks("/fail")

        logger.info("Sleeping %d seconds...", POLL_INTERVAL_SEC)
        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    main()
