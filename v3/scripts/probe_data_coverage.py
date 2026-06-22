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
    print("\nLecture : 'âge 0-1j' = frais ; 'intraday' présent = Grow OK pour l'overnight.")


if __name__ == "__main__":
    main()
