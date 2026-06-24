"""TradingApp v3 — Prix indices US (S&P 500 / Nasdaq) via API courtier OANDA.

POURQUOI : on score des paris US dès 7h Paris et on les trade en TURBOS, qui
suivent le FUTURE (pas le cash). Le future bouge dès 8h ; on peut revendre à
midi. Il faut donc un prix US continu DÈS 8h, or :
- Twelve Data GROW ne sert AUCUN future/CFD/pré-marché US (sonde 23/06, prouvé).
- Yahoo (yfinance) a les futures mais bloque les IP GitHub Actions.

SOLUTION (choix fondateur 23/06) : l'API démo OANDA sert les indices US en CFD
(`SPX500_USD`, `NAS100_USD`, `US30_USD`) quasi 24h/24, en GRATUIT, et depuis nos
serveurs (pas de blocage). Ce script TOURNE DANS LE CYCLE (GitHub Actions), pas
sur un VPS. Aucune brique en plus à maintenir.

CE QUE FAIT CE SCRIPT :
- Lit la dernière cotation (mid = (bid+ask)/2) de chaque instrument OANDA.
- Append un snapshot horodaté dans `v3/data/futures-us/{YYYY-MM-DD}.json` (même
  contrat que l'ancien fetch futures — lu par run_suivi). Le 1er snapshot du jour
  (pris au bulletin 7h/8h) = RÉFÉRENCE « entrée turbo ». Le suivi 12h/18h compare
  le prix courant à cette référence → % de mouvement de l'indice, signé par le call.
- Best-effort TOTAL : pas de token / réseau KO / marché fermé → n'écrit RIEN
  (ni fichier vide, ni prix inventé), log + exit 0. Ne casse JAMAIS le cycle.

CONFIG (secrets GitHub) :
- `OANDA_API_TOKEN` (obligatoire) : token personnel du compte démo OANDA.
- `OANDA_ENV` (optionnel) : "practice" (défaut) ou "live".

CONTRAT DU FICHIER `futures-us/{YYYY-MM-DD}.json` (inchangé / rétro-compatible) :
    {
      "date": "2026-06-23",
      "SPX500_USD": {"price": 5512.2, "ts": "2026-06-23T06:01:00+00:00"},  # DERNIER
      "NAS100_USD": {"price": 19840.5, "ts": "..."},
      "snapshots": [ {"ts": "...", "SPX500_USD": 5500.0, "NAS100_USD": 19800.0}, ... ]
    }
Le 1er snapshot du jour sert de référence (mouvement indice vs indice, échelle
cohérente, jamais mélangé avec un proxy cash).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("fetch_us_index")

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
FUTURES_US_DIR = ROOT / "data" / "futures-us"

PARIS_TZ = ZoneInfo("Europe/Paris")

# Instruments OANDA suivis (CFD indices US, cotés ~24h/5). VIX non couvert
# (pas d'instrument overnight simple) → reste « cash fermé » au matin.
OANDA_INSTRUMENTS = ("SPX500_USD", "NAS100_USD", "US30_USD")

OANDA_BASES = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}
OANDA_TIMEOUT = 15  # secondes


def _oanda_token() -> str:
    """Token lu en runtime (tests : setenv/delenv après import)."""
    return os.environ.get("OANDA_API_TOKEN", "").strip()


def _oanda_base() -> str:
    env = os.environ.get("OANDA_ENV", "practice").strip().lower()
    return OANDA_BASES.get(env, OANDA_BASES["practice"])


def _http_json(url: str, token: str) -> Optional[dict]:
    """GET JSON authentifié OANDA (Bearer). None si KO (best-effort)."""
    try:
        import requests  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001 — dépendance absente
        logger.warning("fetch_us_index: requests indisponible (%s)", e)
        return None
    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept-Datetime-Format": "RFC3339"},
            timeout=OANDA_TIMEOUT,
        )
        if resp.status_code != 200:
            logger.warning("fetch_us_index: OANDA HTTP %d (%s)", resp.status_code, resp.text[:160])
            return None
        return resp.json()
    except Exception as e:  # noqa: BLE001 — réseau/parse KO
        logger.warning("fetch_us_index: requête OANDA KO (%s)", e)
        return None


def _first_account_id(base: str, token: str) -> Optional[str]:
    """Récupère le 1er accountID du compte (l'endpoint pricing en a besoin)."""
    data = _http_json(f"{base}/v3/accounts", token)
    if not isinstance(data, dict):
        return None
    accounts = data.get("accounts")
    if isinstance(accounts, list) and accounts:
        acc = accounts[0]
        if isinstance(acc, dict) and acc.get("id"):
            return str(acc["id"])
    return None


def _mid_from_price(price: dict) -> Optional[float]:
    """Mid = (meilleur bid + meilleur ask)/2 depuis un objet price OANDA."""
    try:
        bids = price.get("bids") or []
        asks = price.get("asks") or []
        bid = float(bids[0]["price"]) if bids else None
        ask = float(asks[0]["price"]) if asks else None
        if bid and ask and bid > 0 and ask > 0:
            return round((bid + ask) / 2.0, 2)
        # Repli : closeoutBid/closeoutAsk si carnet vide.
        cb = price.get("closeoutBid"); ca = price.get("closeoutAsk")
        if cb and ca:
            return round((float(cb) + float(ca)) / 2.0, 2)
    except (KeyError, ValueError, TypeError, IndexError):
        return None
    return None


def fetch_oanda_prices(
    instruments=OANDA_INSTRUMENTS,
    fetcher: Optional[Callable[[], Dict[str, float]]] = None,
) -> Dict[str, float]:
    """Dernier mid par instrument OANDA. {} si token absent / KO (zéro invention).

    `fetcher()` injectable en test (zéro réseau). Ne retourne QUE les instruments
    cotés (`tradeable`) avec un mid > 0 ; un marché fermé (week-end) renvoie {}.
    """
    if fetcher is not None:
        return fetcher()
    token = _oanda_token()
    if not token:
        logger.info("fetch_us_index: OANDA_API_TOKEN absent → rien (best-effort)")
        return {}
    base = _oanda_base()
    acc_id = _first_account_id(base, token)
    if not acc_id:
        logger.warning("fetch_us_index: aucun compte OANDA accessible → rien")
        return {}
    url = f"{base}/v3/accounts/{acc_id}/pricing?instruments={','.join(instruments)}"
    data = _http_json(url, token)
    if not isinstance(data, dict):
        return {}
    out: Dict[str, float] = {}
    for price in data.get("prices") or []:
        if not isinstance(price, dict):
            continue
        inst = price.get("instrument")
        # `tradeable=false` = marché fermé → on n'enregistre pas (pas de prix figé).
        if not inst or price.get("tradeable") is False:
            continue
        mid = _mid_from_price(price)
        if mid and mid > 0:
            out[inst] = mid
    if not out:
        logger.warning("fetch_us_index: OANDA n'a renvoyé aucun prix coté (marché fermé ?)")
    return out


def _load_existing(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001 — corrompu → on repart propre
        logger.warning("fetch_us_index: fichier existant illisible (%s) → reset", e)
        return {}


def write_snapshot(
    prices: Dict[str, float],
    now: Optional[datetime] = None,
    base_dir: Path = FUTURES_US_DIR,
) -> Optional[Path]:
    """Append un snapshot horodaté dans `futures-us/{YYYY-MM-DD}.json`.

    `prices` vide → n'écrit RIEN (best-effort, zéro fichier vide). Sinon met à
    jour le DERNIER prix par instrument + append un snapshot daté. Nom du fichier
    = jour de marché en heure Paris (cohérent avec le suivi).
    """
    if not prices:
        logger.info("fetch_us_index: aucun prix → rien écrit (best-effort)")
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
    for inst, price in prices.items():
        data[inst] = {"price": price, "ts": ts_iso}
        snapshot[inst] = price

    snapshots = data.get("snapshots")
    if not isinstance(snapshots, list):
        snapshots = []
    snapshots.append(snapshot)
    data["snapshots"] = snapshots

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logger.info("fetch_us_index: %s écrit (%s)", path, ", ".join(prices))
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Prix indices US (OANDA CFD) → futures-us/{date}.json"
    )
    parser.add_argument("--out-dir", type=Path, default=FUTURES_US_DIR)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # Best-effort TOTAL : toute exception → log + exit 0 (ne casse jamais le cycle).
    try:
        prices = fetch_oanda_prices()
        write_snapshot(prices, base_dir=args.out_dir)
    except Exception as e:  # noqa: BLE001
        logger.warning("fetch_us_index: erreur inattendue (%s) → exit 0", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
