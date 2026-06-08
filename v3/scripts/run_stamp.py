"""TradingApp v3 — Runner léger de stamp d'ouverture (prix-only).

Source de vérité : `v3/docs/reco/spec-refonte-5-rapports.md` §2.5 + §7 (CA-M1/M2/M3).
Décision Thomas (Q1 tranchée) : capturer les références d'ouverture à la VRAIE
ouverture de chaque marché, pas 3h plus tard dans le run 12h.

Ce runner appelle UNIQUEMENT `mesure_ouverture.stamp_prix_ouverture(now=...)` :
- prix-only : AUCUN scoring, AUCUN appel DeepSeek, AUCUNE mesure (pas measures-log).
- idempotent + entry-lock : un actif déjà stampé ce jour n'est ni refetché ni
  écrasé (le stamp est immuable). Re-déclencher est sans effet (zéro régression).
- léger : un fetch prix Twelve Data par actif dont le marché est ouvert à `now`.

Déclenché aux 3 vraies ouvertures de marché (heure de Paris, jours de bourse) :
- ~08h05 → stampe les actifs Continus (FX/métaux/agri/énergie, convention 08h).
- ~09h05 → stampe les actifs EU (CAC 40).
- ~15h35 → stampe les actifs US (S&P 500, Nasdaq, VIX).
`stamp_prix_ouverture` ne stampe QUE les marchés déjà ouverts (+ délai) à l'heure
courante : à 08h05 les actifs EU/US sont skippés proprement (retry au run suivant),
à 15h35 les Continus/EU sont déjà verrouillés (idempotence). Aucune liste d'actifs
n'est codée ici : le filtre est fait par groupe de marché dans mesure_ouverture.

La garde « jour de bourse » (is_trading_day) est appliquée par le workflow / le VPS
AVANT d'appeler ce runner — comme pour les autres créneaux.

Garde-fous :
- WIN RATE ONLY — aucune valeur monétaire (le module ne calcule aucun gain).
- Zéro invention : Twelve KO → ticker absent du JSON → suivi-interrompu, retry.
- DST : heures via ZoneInfo(Europe/Paris), JAMAIS d'offset codé en dur.

Exit code :
- 0 : succès (un stamp partiel — marchés pas tous ouverts — reste un succès).
- 1 : erreur fatale (stamp_prix_ouverture a levé une exception).
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
logger = logging.getLogger("run_stamp")

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PARIS_TZ = ZoneInfo("Europe/Paris")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Stamp d'ouverture (prix-only, léger, idempotent).",
    )
    parser.add_argument(
        "--date", default=None,
        help="Jour de stamp (YYYY-MM-DD). Défaut : aujourd'hui Europe/Paris.",
    )
    args = parser.parse_args(argv)

    import mesure_ouverture as MO  # noqa: PLC0415

    now = datetime.now(PARIS_TZ)
    date_j = None
    if args.date:
        from datetime import date as _date  # noqa: PLC0415
        date_j = _date.fromisoformat(args.date)

    logger.info(
        "=== Stamp ouverture runner (%s Europe/Paris) ===", now.isoformat()
    )
    try:
        out_path = MO.stamp_prix_ouverture(date_j=date_j, now=now)
    except Exception as e:  # noqa: BLE001
        logger.error("run_stamp KO : %s", e)
        return 1

    try:
        n = len(MO.load_prix_ouverture(date_j or now.date(), out_path.parent))
    except Exception:  # noqa: BLE001
        n = -1
    logger.info("OK : %s (%d tickers stampés au total ce jour)", out_path, n)
    print(f"OK : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
