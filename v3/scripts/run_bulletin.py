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
from typing import Optional
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

import re  # noqa: E402

import briefing  # noqa: E402
import criteres_calculator  # noqa: E402
import journaliste  # noqa: E402
import scoring_analyste  # noqa: E402


# Ancrage d'insertion du Briefing (#5 — audit design 2026-06-02).
# CIBLE de lecture : la grille directionnelle (Top 3 + Synthèse des décisions)
# doit précéder le contexte news. On n'insère donc PLUS le Briefing après le H1
# (comportement de briefing.prepend_to_bulletin) mais JUSTE AVANT la section
# "## Flips vs veille", c.-à-d. après la Synthèse / Surveillance / Biais agrégé.
# Ordre final : H1 → méta → Top 3 → Synthèse → [Surveillance → Biais] →
#               Briefing → Bilan news → Santé sources → Flips → Détail → Limites.
# Le Bilan des news (journaliste) s'ancre sur "## Briefing du jour" (regex de
# section, pas de position) → il reste correctement inséré après le Briefing.
# Le parser du Journaliste (MATRIX_ROW_RE) lit la table Synthèse par regex de
# ligne markdown où qu'elle soit dans le fichier → réordonnancement sans impact.
_FLIPS_ANCHOR_RE = re.compile(r"^## Flips vs veille\s*$", re.MULTILINE)


def insert_briefing_after_synthese(bulletin_path: Path, briefing_md: str) -> bool:
    """Insère le Briefing juste avant '## Flips vs veille' (après la Synthèse).

    Idempotent : si un bloc Briefing existe déjà (re-run), il est d'abord retiré
    via le nettoyage de briefing.prepend_to_bulletin n'est PAS utilisé ici — on
    fait le retrait localement pour ancrer au bon endroit.

    Fallback : si l'ancre '## Flips vs veille' est introuvable (format inattendu),
    on retombe sur briefing.prepend_to_bulletin (insertion après H1) pour ne
    jamais perdre le Briefing.

    Retourne True si écrit, False si bulletin absent.
    """
    if not bulletin_path.exists():
        logger.warning("bulletin introuvable : %s", bulletin_path)
        return False

    content = bulletin_path.read_text(encoding="utf-8")

    # Retrait d'un Briefing (+ Santé des sources accolée) déjà présent (re-run),
    # quel que soit son emplacement actuel. Mêmes regex que briefing.py.
    existing_briefing = re.compile(r"## Briefing du jour\n.*?(?=\n## |\Z)", re.DOTALL)
    if existing_briefing.search(content):
        content = existing_briefing.sub("", content, count=1)
        sante = re.compile(r"## Santé des sources\n.*?(?=\n## |\Z)", re.DOTALL)
        content = sante.sub("", content, count=1)
        content = re.sub(r"\n{3,}", "\n\n", content)

    block = briefing_md.rstrip() + "\n\n"
    m = _FLIPS_ANCHOR_RE.search(content)
    if not m:
        # Ancre absente → on ne casse pas le pipeline : insertion après H1.
        logger.warning(
            "Ancre '## Flips vs veille' introuvable — fallback prepend après H1"
        )
        bulletin_path.write_text(content, encoding="utf-8")
        return briefing.prepend_to_bulletin(bulletin_path, briefing_md)

    insert_at = m.start()
    new_content = (
        content[:insert_at].rstrip() + "\n\n" + block + content[insert_at:].lstrip("\n")
    )
    bulletin_path.write_text(new_content, encoding="utf-8")
    return True


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

    # Étape 2ter — Decision-log (observabilité ±1 vs pondéré, append-only).
    # C7 LOT 6 : on re-lit la veille pour exposer is_flip dans chaque record.
    # Best-effort : si load_veille échoue, on passe None (is_flip absent).
    try:
        veille_conclusions_for_log: Optional[dict] = None
        try:
            _, veille_conclusions_for_log = scoring_analyste.load_veille(
                scoring_analyste.BULLETINS_DIR, now,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("load_veille KO (is_flip absent du decision-log) : %s", e)
        # Étage 2 (SHADOW) — capteurs courts 24h (retour veille / gap overnight)
        # tracés au decision-log, poids 0. Best-effort : indispo → champs None.
        shadow_capteurs: Optional[dict] = None
        try:
            _fiches = scoring_analyste.load_fiches()
            bulletin_id = f"{now:%Y-%m-%d}-{now:%H}h"
            _prix_emission = journaliste.load_prix_emission(bulletin_id)
            shadow_capteurs = scoring_analyste.compute_shadow_capteurs(
                _fiches, prix_emission=_prix_emission,
            )
        except Exception as e:  # noqa: BLE001 — capteurs shadow non bloquants
            logger.warning("capteurs shadow indisponibles : %s", e)
        recs = scoring_analyste.build_decision_log_records(
            results, now, veille_conclusions=veille_conclusions_for_log,
            shadow_capteurs=shadow_capteurs,
        )
        dl_path = scoring_analyste.write_decision_log(recs, now)
        n_diverge = sum(1 for r in recs if r.get("diverge"))
        n_flip = sum(1 for r in recs if r.get("is_flip") is True)
        n_cont = sum(1 for r in recs if r.get("is_flip") is False)
        logger.info(
            "Decision-log écrit : %s (%d lignes, %d divergences, "
            "%d flips, %d continuations)",
            dl_path, len(recs), n_diverge, n_flip, n_cont,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("decision-log KO (non bloquant) : %s", e)

    # Étape 2bis — Briefing du jour (synthèse news à impact, déterministe, zéro
    # LLM). Best-effort : si échec, le bulletin reste valide.
    # #5 (audit design) : on insère le Briefing APRÈS la Synthèse des décisions
    # (avant "## Flips vs veille"), pas après le H1 — la grille directionnelle
    # passe devant le contexte news.
    try:
        briefing_md = briefing.build_briefing(today=now.date())
        insert_briefing_after_synthese(out_path, briefing_md)
        logger.info("Briefing du jour inséré dans le bulletin (après la Synthèse)")
    except Exception as e:  # noqa: BLE001
        logger.warning("briefing KO (non bloquant) : %s", e)

    # Étape 3 — stamp des prix d'émission de CE bulletin (pour mesure ultérieure
    # par le Journaliste). Clé par IDENTITÉ de bulletin (créneau) et non par
    # date : 3 runs/jour → 3 jeux de prix distincts. On dérive l'identité du
    # fichier réellement écrit par scoring_analyste (out_path).
    # Best-effort : si Twelve Data dead, on ne bloque pas le bulletin (la cellule
    # passera en "suivi-interrompu" à la mesure).
    try:
        bid = journaliste.bulletin_id_from_path(out_path) or now.strftime("%Y-%m-%d")
        journaliste.stamp_prix_emission(bid)
    except Exception as e:  # noqa: BLE001
        logger.warning("stamp_prix_emission KO (non bloquant) : %s", e)

    print(f"OK : {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
