"""Sonde de couverture données (verify-first, forfait Twelve Grow actif).

But : MESURER (pas supposer) ce que la clé Twelve réelle sert, par actif :
- série JOURNALIÈRE (points + dernière date → fraîcheur réelle, ex. close de
  vendredi servi le lundi ?),
- série INTRADAY 1h (dispo avec Grow ? combien de barres, dernière barre),
- tickers FUTURES (ES=F/NQ=F) et indices cash directs (^GSPC/^IXIC) : résolvent-ils
  enfin, ou faut-il garder les proxies ETF / FRED ?

À lancer en CI (workflow probe-data) avec le secret TWELVE_DATA_API_KEY. Lecture
seule, aucun fichier modifié. Sortie = tableau lisible dans les logs du run.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import criteres_calculator as cc  # noqa: E402
import market_data as md  # noqa: E402

# Candidats US NATIFS Twelve à tester EN DIRECT (sans passer par _TICKER_MAP) :
# le but est de savoir si Twelve GROW sert une donnée US EN DEHORS des heures
# cash (futures overnight / CFD ~24h / pré-marché), puisque nos paris sont pris
# à 8h Paris = 2h-3h du matin à New York (cash ET pré-marché US fermés).
#   - indices natifs Twelve : SPX, IXIC, NDX, DJI, RUT (heures cash uniquement)
#   - CFD éventuels ~24h     : US500, US100, USTEC, US30, SPX500, NAS100
#   - futures alt (sans =F)  : ES, NQ, MES, MNQ
#   - ETF + prepost          : SPY/QQQ avec extended hours
US_SYMBOLS_DIRECT = [
    ("SPX",     {}),
    ("IXIC",    {}),
    ("NDX",     {}),
    ("DJI",     {}),
    ("RUT",     {}),
    ("US500",   {}),
    ("US100",   {}),
    ("USTEC",   {}),
    ("US30",    {}),
    ("SPX500",  {}),
    ("NAS100",  {}),
    ("ES",      {}),
    ("NQ",      {}),
    ("MES",     {}),
    ("MNQ",     {}),
    ("SPY",     {"prepost": "true"}),
    ("QQQ",     {"prepost": "true"}),
]

# Tickers fiche (ticker_principal) + candidats à re-tester avec Grow.
FICHE_TICKERS = {
    "or": "GC=F", "argent": "SI=F", "cuivre": "HG=F", "petrole": "BZ=F",
    "cafe": "KC=F", "cacao": "CC=F", "ble": "ZW=F", "eurusd": "EUR=X",
    "sp500": "^GSPC", "nasdaq": "^IXIC", "cac40": "^FCHI", "vix": "^VIX",
}
# Proxies / candidats spéciaux (la question overnight + indices directs).
CANDIDATS = {
    "future S&P (ES=F)": "ES=F",
    "future Nasdaq (NQ=F)": "NQ=F",
    "ETF S&P (SPY)": "SPY",
    "ETF Nasdaq (QQQ)": "QQQ",
    "DXY (DX-Y.NYB)": "DX-Y.NYB",
}


def _probe(label: str, ticker: str) -> str:
    now = datetime.now(timezone.utc)
    # Journalier
    try:
        d = cc.fetch_twelve_series(ticker, interval="1day", outputsize=15) or []
    except Exception as e:  # noqa: BLE001
        d = []
        d_err = type(e).__name__
    else:
        d_err = ""
    if d:
        last_dt, _ = d[-1]
        age = (now.date() - last_dt.date()).days
        daily = f"{len(d)} pts, dernier {last_dt.date()} (âge {age}j)"
    else:
        daily = f"VIDE{(' ('+d_err+')') if d_err else ''}"
    # Intraday 1h
    try:
        h = cc.fetch_twelve_series(ticker, interval="1h", outputsize=24) or []
    except Exception as e:  # noqa: BLE001
        h = []
    if h:
        last_h, _ = h[-1]
        hourly = f"{len(h)} barres 1h, dernière {last_h:%Y-%m-%d %H:%M}"
    else:
        hourly = "pas d'intraday"
    return f"{label:24s} {ticker:12s} | jour: {daily:38s} | {hourly}"


def _probe_us_direct(symbol: str, extra: dict) -> str:
    """Teste un symbole US EN DIRECT sur Twelve (bypass _TICKER_MAP).

    On veut la DERNIÈRE barre 1h ET sa fraîcheur : si Twelve sert une donnée
    overnight (futures/CFD), la dernière barre sera récente même la nuit US.
    Si la dernière barre date de la clôture cash précédente (22h Paris), le
    symbole ne couvre QUE les heures cash → inutile pour un pari à 8h.
    """
    now = datetime.now(timezone.utc)
    params = {"symbol": symbol, "interval": "1h", "outputsize": 6, **extra}
    data = md._td_request("time_series", params)
    tag = f"+prepost" if extra.get("prepost") else ""
    if not data or "values" not in data:
        # message d'erreur Twelve éventuel (symbol not found / not available)
        status = (data or {}).get("status") if isinstance(data, dict) else None
        note = "symbole inconnu/non servi" if status == "error" else "VIDE"
        return f"{symbol:8s}{tag:9s} | {note}"
    values = data.get("values") or []
    if not values:
        return f"{symbol:8s}{tag:9s} | aucune barre"
    last_dt_str = values[0].get("datetime", "?")  # Twelve = newest-first
    try:
        last_dt = datetime.fromisoformat(last_dt_str.replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        age_h = (now - last_dt).total_seconds() / 3600.0
        fresh = f"âge {age_h:.1f}h"
    except Exception:  # noqa: BLE001
        fresh = "âge ?"
    return f"{symbol:8s}{tag:9s} | {len(values)} barres 1h, dernière {last_dt_str} ({fresh})"


def main() -> None:
    print("=" * 100)
    print("SONDE COUVERTURE DONNÉES — Twelve Grow (réel)  ·", datetime.now(timezone.utc).isoformat())
    print("=" * 100)
    has_key = bool(cc._twelve_key()) if hasattr(cc, "_twelve_key") else "?"
    print(f"Clé Twelve présente : {has_key}\n")
    print("--- Tickers fiche (ticker_principal) ---")
    for asset, t in FICHE_TICKERS.items():
        print(_probe(asset, t))
    print("\n--- Candidats à re-tester avec Grow (futures / indices directs / DXY) ---")
    for label, t in CANDIDATS.items():
        print(_probe(label, t))
    print("\n--- US EN DIRECT (overnight ?) : indices natifs / CFD / futures alt / prepost ---")
    print("    Question : Y a-t-il une donnée US FRAÎCHE à 8h Paris (= nuit US) ?")
    print("    'âge < 2h' = servi en continu (overnight OK) | 'âge > 10h' = heures cash only.")
    for sym, extra in US_SYMBOLS_DIRECT:
        print("  " + _probe_us_direct(sym, extra))
    print("\nLecture : 'âge 0-1j' = frais ; 'intraday' présent = Grow OK pour l'overnight.")


if __name__ == "__main__":
    main()
