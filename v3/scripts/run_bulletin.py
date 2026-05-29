"""TradingApp v3 — Bulletin runner (STUB Incrément 1)

À ce stade : NE SCORE PAS. Imprime un placeholder et écrit un bulletin stub
dans v3/data/bulletins/ pour valider que le workflow tourne, commit et push.

Les vrais modules viennent dans les incréments suivants :
- v3/scripts/criteres_calculator.py     (agrège events + prix → criteres-courants.md)
- v3/scripts/scoring_analyste.py        (12 fiches × 3 horizons → 36 cellules LONG/SHORT)
- v3/scripts/journaliste.py             (mesure conclusions échues, taux + Brier)

Dépendances bloquantes :
- 12 fiches actifs (YAML/MD) dans v3/config/fiches/ — pas encore lues
- triggers-and-windows.yml — classement des critères événementiels
- Les "criteres-courants" requièrent prix Twelve Data + events-log enrichi
"""

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


BULLETINS_DIR = Path(os.environ.get("BULLETINS_DIR", "v3/data/bulletins"))


def main() -> int:
    now_paris = datetime.now(ZoneInfo("Europe/Paris"))
    date_str = now_paris.strftime("%Y-%m-%d")
    logger.info("=== Bulletin runner STUB (%s Europe/Paris) ===", now_paris.isoformat())

    print("scoring engine TODO — criteres_calculator + scoring_analyste à implémenter")
    print(f"  date cible : {date_str}")
    print("  étapes prévues :")
    print("   1. lire v3/data/events-log.md (Phase 2.1 ✅)")
    print("   2. lire prix Twelve Data (TWELVE_DATA_API_KEY)")
    print("   3. agréger → criteres-courants.md")
    print("   4. scorer 12 fiches × 3 horizons → 36 cellules LONG/SHORT")
    print("   5. écrire v3/data/bulletins/bulletin-YYYY-MM-DD.md")
    print("   6. (mode shadow) ne PAS envoyer Telegram")

    # Écrit un stub-bulletin pour valider l'aller-retour git/commit du workflow
    BULLETINS_DIR.mkdir(parents=True, exist_ok=True)
    stub_path = BULLETINS_DIR / f"bulletin-{date_str}.md"
    stub_path.write_text(
        f"# Bulletin {date_str} — STUB\n\n"
        f"Généré à {now_paris.isoformat()}.\n\n"
        f"Scoring engine non implémenté (incrément 1 : squelette uniquement).\n"
        f"Voir v3/scripts/run_bulletin.py pour la roadmap.\n",
        encoding="utf-8",
    )
    logger.info("Stub bulletin écrit : %s", stub_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
