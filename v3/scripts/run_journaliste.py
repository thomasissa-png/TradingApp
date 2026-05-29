"""TradingApp v3 — Runner journaliste (cron quotidien).

Exécute le journaliste : stamp les prix d'émission du jour + mesure les
conclusions échues + écrit `v3/data/performance.md`.

Exit code :
- 0  : succès (même si des mesures sont en suivi-interrompu, c'est normal)
- 1  : erreur fatale (journaliste a levé une exception)
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("run_journaliste")

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import journaliste  # noqa: E402


def main() -> int:
    now = datetime.now(ZoneInfo("Europe/Paris"))
    logger.info("=== Journaliste runner (%s Europe/Paris) ===", now.isoformat())
    try:
        out_path, measures, kpis = journaliste.run(now=now)
    except Exception as e:  # noqa: BLE001
        logger.error("journaliste KO : %s", e)
        return 1
    nb_eligibles = sum(1 for k in kpis.values() if k.statut == "éligible_actif")
    logger.info(
        "OK : %s (%d mesures, %d cellules, %d éligibles)",
        out_path, len(measures), len(kpis), nb_eligibles,
    )
    print(f"OK : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
