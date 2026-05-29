"""TradingApp v3 — Critères courants (SCAFFOLD).

Lit `v3/data/events-log.md` (existant Phase 2.1) et les prix Twelve Data,
agrège par actif × clé critère, écrit `v3/data/criteres-courants.md` (bloc
YAML conforme à `SCHEMA-fiche.md`).

ÉTAT : SCAFFOLD. Structure complète, fetchs externes STUBBÉS (TODO).
Aucune valeur inventée : un critère non-câblé est OMIS (le scoring le
marquera `n/a`, poids 0).
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

logger = logging.getLogger("criteres_calculator")

ROOT = Path(__file__).resolve().parents[1]
FICHES_DIR = ROOT / "config" / "fiches"
EVENTS_LOG = ROOT / "data" / "events-log.md"
CRITERES_OUT = ROOT / "data" / "criteres-courants.md"


# ---------------------------------------------------------------------------
# Fetchs externes — STUBS explicites (zéro invention)
# ---------------------------------------------------------------------------

def fetch_twelve_data_price(symbol: str, *, interval: str = "1day", lookback: int = 60) -> Optional[List[float]]:
    """TODO: appeler https://api.twelvedata.com/time_series.
    Auth : TWELVE_DATA_API_KEY. Retourne la série close [oldest..newest].
    Tant que non câblé : retourne None (le scoring marquera le critère n/a)."""
    logger.debug("STUB fetch_twelve_data_price(%s, %s, %s)", symbol, interval, lookback)
    return None


def fetch_eia_surprise(series_id: str) -> Optional[Dict[str, Any]]:
    """TODO: EIA API (https://api.eia.gov/v2/...) + consensus (source à câbler).
    Retourne {valeur: σ surprise, history: [...]} ou None."""
    logger.debug("STUB fetch_eia_surprise(%s)", series_id)
    return None


def fetch_cftc_cot(market: str) -> Optional[Dict[str, Any]]:
    """TODO: CFTC COT (vendredi). Retourne managed money nets + history 252w."""
    logger.debug("STUB fetch_cftc_cot(%s)", market)
    return None


def read_events_log(path: Path = EVENTS_LOG) -> List[dict]:
    """Lit v3/data/events-log.md (format à confirmer côté agent_news).
    Retourne la liste brute des events. Stub si fichier absent."""
    if not path.exists():
        logger.warning("events-log absent (%s) — aucune entrée triplet/gate", path)
        return []
    # TODO: parser le format réel (markdown + frontmatter ou YAML inline)
    # Pour l'instant : on retourne [] pour ne RIEN inventer.
    logger.debug("STUB read_events_log: parser à câbler quand format figé")
    return []


# ---------------------------------------------------------------------------
# Résolution triplet à partir d'events-log
# ---------------------------------------------------------------------------

def resolve_triplet_from_events(
    events: List[dict],
    *,
    l2_tag: str,
    window_hours: int = 168,
    now: Optional[datetime] = None,
) -> Optional[int]:
    """TODO: appliquer `triggers-and-windows.yml` :
    - +1 escalade (mots-clés frappes, blocus, sanctions...)
    - -1 détente (accord, cessez-le-feu)
    -  0 statu quo
    Tant que `triggers-and-windows.yml` n'existe pas : retourne None (n/a)."""
    return None


def resolve_gate(events: List[dict], fiche_key: str, now: Optional[datetime] = None) -> bool:
    """TODO: détecter conditions GATE (OPEC <7j, FOMC <24h, EIA <4h…).
    Stub : False par défaut."""
    return False


# ---------------------------------------------------------------------------
# Agrégation par fiche
# ---------------------------------------------------------------------------

def collect_for_fiche(fiche_key: str, fiche: dict, events: List[dict]) -> Dict[str, dict]:
    """Pour chaque critère de la fiche, tente de produire {valeur, ts, ...}.
    Critère non disponible => OMIS (zéro invention)."""
    out: Dict[str, dict] = {}
    now = datetime.now(timezone.utc)
    for crit in fiche.get("criteres", []):
        cle = crit.get("cle_courante")
        if not cle:
            continue
        type_norm = crit.get("normalisation")
        source = (crit.get("source") or "").lower()

        if type_norm == "gate":
            actif = resolve_gate(events, fiche_key, now)
            out[cle] = {"valeur": actif, "ts": now.isoformat()}
            continue

        if type_norm == "triplet":
            # TODO: déterminer l2_tag depuis crit (ex: "L2=Iran-Moyen-Orient")
            val = resolve_triplet_from_events(events, l2_tag=cle, now=now)
            if val is None:
                continue  # n/a -> omis
            out[cle] = {"valeur": val, "ts": now.isoformat()}
            continue

        if type_norm in ("zscore", "lineaire"):
            # TODO: brancher fetch selon `source` (eia/twelve data/cftc/caixin)
            # Pour l'instant : OMIS (scoring marquera n/a).
            continue

    return out


# ---------------------------------------------------------------------------
# Écriture criteres-courants.md
# ---------------------------------------------------------------------------

def write_criteres(payload: dict, path: Path = CRITERES_OUT) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    yml = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    content = (
        "# Critères courants — généré par criteres_calculator.py\n"
        "# Source de vérité du moteur de scoring (Analyste).\n\n"
        "```yaml\n" + yml + "```\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def run() -> Path:
    fiches: Dict[str, dict] = {}
    for f in sorted(FICHES_DIR.glob("*.yml")):
        with f.open("r", encoding="utf-8") as fh:
            fiches[f.stem] = yaml.safe_load(fh)
    events = read_events_log()
    payload: Dict[str, Any] = {"last_update": datetime.now(timezone.utc).isoformat()}
    for key, fiche in fiches.items():
        payload[key] = collect_for_fiche(key, fiche, events)
    return write_criteres(payload)


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    path = run()
    print(f"OK (SCAFFOLD) : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
