"""TradingApp v3 — Repo Publisher (remplace drive_publisher.py)

Append des lignes events à un fichier local `v3/data/events-log.md`.
Le commit + push git est fait par le workflow GitHub Actions, PAS par ce script.
Ceci respecte la décision "git-as-storage" et garde le script idempotent /
re-runnable en local.

Format du fichier :
- Header markdown créé au premier append (table avec colonnes 11 champs schéma v3)
- Append append-only, jamais de réécriture
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


EVENTS_LOG_PATH = Path(os.environ.get("EVENTS_LOG_PATH", "v3/data/events-log.md"))


HEADER = (
    "# TradingApp v3 — Events log\n"
    "\n"
    "Source : pipeline RSS + DeepSeek (schéma 7 champs).\n"
    "Append-only. Édité par v3/scripts/agent_news.py (GitHub Actions cron).\n"
    "\n"
    "| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|\n"
)


class RepoPublisher:
    """API minimale, mêmes méthodes que l'ancien DrivePublisher pour drop-in."""

    def __init__(self, events_log_path: Path = EVENTS_LOG_PATH):
        self.path = Path(events_log_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(HEADER, encoding="utf-8")
            logger.info("Initialized events-log at %s", self.path)

    def append_to_events_log(self, lines: list) -> None:
        """Append une liste de lignes markdown (déjà formatées) au fichier."""
        if not lines:
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(f"<!-- batch {ts} : {len(lines)} events -->\n")
            for line in lines:
                fh.write(line.rstrip() + "\n")
        logger.info("Appended %d events to %s", len(lines), self.path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    pub = RepoPublisher()
    pub.append_to_events_log([
        "| 2026-05-29 | Test | smoke | publisher smoke test |  | intraday | 1 | self |  | other |  |",
    ])
    print(f"OK → {pub.path}")
