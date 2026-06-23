"""TradingApp v3 — Fetch des futures US (ES=F / NQ=F) via yfinance.

⚠️ OÙ TOURNE CE SCRIPT (lire avant tout) :
Ce script DOIT tourner sur une IP NON bloquée par Yahoo Finance — typiquement
un VPS, PAS un runner GitHub Actions. Les runners GitHub partagent des plages
IP que Yahoo rejette (HTTP 429 / empty body), donc yfinance y renvoie du VIDE.
Sur le VPS, yfinance répond normalement.

POURQUOI : on score des paris US (S&P 500 / Nasdaq) dès 7h Paris, mais le cash
US n'ouvre qu'à 15h30. Twelve Data ne sert AUCUN future CME (ES=F / NQ=F vides,
re-vérifié sonde CI 23/06). Ce fetch comble le trou du matin : il écrit un
fichier que le cycle (GitHub Actions, run_suivi) LIT pour afficher un statut US
« via future » au lieu de « cash fermé (ouvre 15h30) ».

CE QUE FAIT CE SCRIPT :
- Récupère le dernier prix de ES=F (future S&P 500) et NQ=F (future Nasdaq).
  (VIX laissé de côté en Phase 1.)
- Append un snapshot horodaté dans `v3/data/futures-us/{YYYY-MM-DD}.json`
  (heure Paris pour le nom du fichier = jour de marché courant).
- Best-effort TOTAL : si yfinance KO/bloqué/vide → n'écrit RIEN (ni fichier
  vide, ni prix inventé), log + exit 0. Ne casse JAMAIS l'appelant.

CE QU'IL NE FAIT PAS :
- Il ne commit/push PAS. Le wrapper VPS (cron) s'en charge :
    python v3/scripts/fetch_us_futures.py \
      && git add v3/data/futures-us \
      && git commit -m "data: futures US snapshot" \
      && git push
  (le commit/push côté VPS sera câblé séparément — Phase 1 = côté repo only).

CONTRAT DU FICHIER `v3/data/futures-us/{YYYY-MM-DD}.json` :
    {
      "date": "2026-06-23",                      # jour de marché (heure Paris)
      "ES=F": {"price": 5512.25, "ts": "2026-06-23T05:31:00+00:00"},  # DERNIER
      "NQ=F": {"price": 19840.5, "ts": "2026-06-23T05:31:00+00:00"},
      "snapshots": [                             # petite série intraday (append)
        {"ts": "2026-06-23T05:01:00+00:00", "ES=F": 5500.0, "NQ=F": 19800.0},
        {"ts": "2026-06-23T05:31:00+00:00", "ES=F": 5512.25, "NQ=F": 19840.5}
      ]
    }
- `ES=F` / `NQ=F` au top niveau = le DERNIER prix vu (lecture rapide par le suivi).
- `snapshots` = série ordonnée (du + ancien au + récent). Le 1er snapshot du jour
  sert de RÉFÉRENCE au suivi pour calculer un % de mouvement FUTURE vs FUTURE.
- `ts` en ISO-8601 UTC. Un ticker absent d'un fetch n'écrase pas son dernier prix.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("fetch_us_futures")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
FUTURES_US_DIR = ROOT / "data" / "futures-us"

PARIS_TZ = ZoneInfo("Europe/Paris")

# Futures suivis en Phase 1 (VIX laissé de côté : pas de future simple en Phase 1).
FUTURES_TICKERS = ("ES=F", "NQ=F")


def _yfinance_last_price(ticker: str) -> Optional[float]:
    """Dernier prix d'un future via yfinance. None si KO/vide (best-effort).

    On lit la dernière clôture de la série 1m du jour (fallback : `fast_info` /
    `info`). yfinance peut renvoyer un DataFrame VIDE sur IP bloquée → None.
    """
    try:
        import yfinance as yf  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001 — dépendance absente → best-effort
        logger.warning("fetch_us_futures: yfinance indisponible (%s)", e)
        return None
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="1d", interval="1m")
        if hist is not None and not hist.empty and "Close" in hist.columns:
            val = hist["Close"].dropna()
            if len(val) > 0:
                price = float(val.iloc[-1])
                if price > 0:
                    return price
        # Fallback : fast_info (dernier prix temps réel) si l'historique est vide.
        fast = getattr(tk, "fast_info", None)
        if fast is not None:
            last = fast.get("last_price") if hasattr(fast, "get") else getattr(fast, "last_price", None)
            if isinstance(last, (int, float)) and last > 0:
                return float(last)
    except Exception as e:  # noqa: BLE001 — réseau/parse KO → best-effort
        logger.warning("fetch_us_futures: %s fetch KO (%s)", ticker, e)
    return None


def fetch_futures(
    tickers=FUTURES_TICKERS,
    fetcher: Optional[Callable[[str], Optional[float]]] = None,
) -> Dict[str, float]:
    """Récupère le dernier prix de chaque future. Best-effort par ticker.

    `fetcher(ticker) -> Optional[float]` injectable en test (zéro réseau).
    Retourne un dict {ticker: price} ne contenant QUE les tickers fetchés OK
    (prix > 0). Un ticker KO est absent du dict (zéro invention).
    """
    fetcher = fetcher or _yfinance_last_price
    out: Dict[str, float] = {}
    for tkr in tickers:
        price = fetcher(tkr)
        if isinstance(price, (int, float)) and price > 0:
            out[tkr] = float(price)
        else:
            logger.warning("fetch_us_futures: %s KO/vide → ignoré", tkr)
    return out


def _load_existing(path: Path) -> Dict[str, Any]:
    """Charge le fichier du jour s'il existe (pour append), sinon dict vide."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001 — fichier corrompu → on repart propre
        logger.warning("fetch_us_futures: fichier existant illisible (%s) → reset", e)
        return {}


def write_snapshot(
    prices: Dict[str, float],
    now: Optional[datetime] = None,
    base_dir: Path = FUTURES_US_DIR,
) -> Optional[Path]:
    """Append un snapshot horodaté dans `futures-us/{YYYY-MM-DD}.json`.

    - `prices` vide → n'écrit RIEN, retourne None (best-effort, zéro fichier vide).
    - Sinon : met à jour le DERNIER prix par ticker + append un snapshot daté.
    - Le nom du fichier = jour de marché en heure Paris (cohérent avec le suivi).
    Retourne le chemin écrit, ou None si rien écrit.
    """
    if not prices:
        logger.info("fetch_us_futures: aucun prix → rien écrit (best-effort)")
        return None

    now = now or datetime.now(timezone.utc)
    now_utc = now.astimezone(timezone.utc)
    day_paris = now.astimezone(PARIS_TZ).date().isoformat()
    ts_iso = now_utc.isoformat()

    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"{day_paris}.json"
    data = _load_existing(path)
    data["date"] = day_paris

    snapshot: Dict[str, Any] = {"ts": ts_iso}
    for tkr, price in prices.items():
        # DERNIER prix par ticker (un ticker absent du fetch garde son ancien prix).
        data[tkr] = {"price": price, "ts": ts_iso}
        snapshot[tkr] = price

    snapshots = data.get("snapshots")
    if not isinstance(snapshots, list):
        snapshots = []
    snapshots.append(snapshot)
    data["snapshots"] = snapshots

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logger.info("fetch_us_futures: %s écrit (%s)", path, ", ".join(prices))
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fetch futures US (ES=F/NQ=F) via yfinance → futures-us/{date}.json")
    parser.add_argument(
        "--out-dir", type=Path, default=FUTURES_US_DIR,
        help="Répertoire de sortie (défaut: v3/data/futures-us).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Logs DEBUG.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Best-effort TOTAL : toute exception → log + exit 0 (ne casse jamais le cron).
    try:
        prices = fetch_futures()
        write_snapshot(prices, base_dir=args.out_dir)
    except Exception as e:  # noqa: BLE001 — best-effort, ne casse jamais l'appelant
        logger.warning("fetch_us_futures: erreur inattendue (%s) → exit 0", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
