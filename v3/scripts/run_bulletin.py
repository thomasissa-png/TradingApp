"""TradingApp v3 — Bulletin runner.

Orchestre :
1. criteres_calculator.run()  (SCAFFOLD — fetchs externes stubbés)
2. scoring_analyste.run()     (moteur déterministe, zéro LLM)

Échec à n'importe quelle étape => exit code non-nul, pas de bulletin
inventé. La fraîcheur (last_update > 1h) bloque le bulletin (red line).
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
logger = logging.getLogger("run_bulletin")

# Permet l'import quand lancé depuis racine repo ou depuis v3/scripts
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import briefing  # noqa: E402
import criteres_calculator  # noqa: E402
import journaliste  # noqa: E402
import scoring_analyste  # noqa: E402


def main() -> int:
    now = datetime.now(ZoneInfo("Europe/Paris"))
    logger.info("=== Bulletin runner (%s Europe/Paris) ===", now.isoformat())

    # Étape 1 — critères courants
    try:
        cc_path = criteres_calculator.run()
        logger.info("criteres-courants OK : %s", cc_path)
    except Exception as e:
        logger.error("criteres_calculator KO : %s", e)
        return 2

    # Étape 2 — scoring
    try:
        out_path, results = scoring_analyste.run(now=now)
    except Exception as e:
        logger.error("scoring_analyste KO : %s", e)
        return 3

    logger.info("Bulletin écrit : %s (%d actifs)", out_path, len(results))

    # Étape 2bis — Briefing du jour (synthèse news à impact, déterministe, zéro
    # LLM). Best-effort : si échec, le bulletin reste valide.
    try:
        briefing_md = briefing.build_briefing(today=now.date())
        briefing.prepend_to_bulletin(out_path, briefing_md)
        logger.info("Briefing du jour inséré dans le bulletin")
    except Exception as e:  # noqa: BLE001
        logger.warning("briefing KO (non bloquant) : %s", e)

    # Étape 3 — stamp des prix d'émission du jour (pour mesure ultérieure
    # par le Journaliste). Best-effort : si Twelve Data dead, on ne bloque
    # pas le bulletin (la cellule passera en "suivi-interrompu" à la mesure).
    try:
        journaliste.stamp_prix_emission(now.date())
    except Exception as e:  # noqa: BLE001
        logger.warning("stamp_prix_emission KO (non bloquant) : %s", e)

    print(f"OK : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
