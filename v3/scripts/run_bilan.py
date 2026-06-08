"""TradingApp v3 — Runner CLI du Bilan du jour 22h (R4, refonte 5 rapports).

Source de vérité : `v3/docs/reco/spec-refonte-5-rapports.md` §3.4 + §7 (CA-B*).

Ce runner appelle `bilan_jour.build_bilan_jour(now=...)` (Phase 1, déjà construit)
et écrit le rapport R4 dans `v3/data/bilan-jour/{date}.md`. Le bilan note les
calls 24h du Briefing 7h (sens clôture−ouverture vs call) et produit le win rate
du jour. Le DÉCLENCHEMENT à 22h15 Paris (cron + garde heure-Paris) est géré par
l'infra, séparément de ce runner.

Garde-fous :
- WIN RATE ONLY — aucune valeur monétaire (la logique est dans bilan_jour.py).
- `now` ancré sur Europe/Paris réelle (DST via ZoneInfo, jamais d'offset en dur).

Exit code :
- 0 : succès (un bilan vide — aucune cellule échue — reste un succès).
- 1 : erreur fatale (build_bilan_jour a levé une exception).
"""

from __future__ import annotations

import argparse
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
logger = logging.getLogger("run_bilan")

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PARIS_TZ = ZoneInfo("Europe/Paris")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Bilan du jour 22h (R4).")
    parser.add_argument(
        "--date", default=None,
        help="Jour à bilanter (YYYY-MM-DD). Défaut : aujourd'hui Europe/Paris.",
    )
    args = parser.parse_args(argv)

    import bilan_jour  # noqa: PLC0415

    now = datetime.now(PARIS_TZ)
    date_j = None
    if args.date:
        from datetime import date as _date  # noqa: PLC0415
        date_j = _date.fromisoformat(args.date)

    logger.info("=== Bilan du jour runner (%s Europe/Paris) ===", now.isoformat())
    try:
        bilan = bilan_jour.build_bilan_jour(now=now, date_j=date_j)
        out_path = bilan_jour.write_bilan_jour(bilan)
    except Exception as e:  # noqa: BLE001
        logger.error("run_bilan KO : %s", e)
        return 1

    wr = f"{bilan.win_rate_jour:.0f}%" if bilan.win_rate_jour is not None else "—"
    logger.info(
        "OK : %s (%d cellules 24h, VRAI=%d FAUSSE=%d NC=%d, win rate jour=%s)",
        out_path, len(bilan.measures_24h), bilan.n_vrai, bilan.n_fausse,
        bilan.n_nc, wr,
    )
    print(f"OK : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
