"""TradingApp v3 — Validation des symboles Twelve Data.

Pour chaque actif, teste plusieurs variantes de symboles (Yahoo, Twelve forex,
ETF proxy, etc.) contre `https://api.twelvedata.com/quote` avec la clé
`TWELVE_DATA_API_KEY`. Écrit un rapport markdown `v3/data/symbol-validation.md`
listant pour chaque actif : quels symboles répondent OK (avec valeur) vs erreur.

Red line : zéro invention. Si la clé est absente → message clair, exit 0
(rapport "skip — pas de clé"). Si tous les symboles échouent pour un actif →
on l'écrit explicitement.

Le rapport sert ensuite à corriger `TWELVE_SYMBOLS` dans criteres_calculator.py
ET la table `YAHOO_TO_TWELVE` pour stamp_prix_emission (journaliste).

Usage :
    TWELVE_DATA_API_KEY=xxx python3 v3/scripts/validate_symbols.py
"""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("validate_symbols")

ROOT = Path(__file__).resolve().parents[1]
REPORT_OUT = ROOT / "data" / "symbol-validation.md"

TWELVE_BASE = "https://api.twelvedata.com"
DEFAULT_TIMEOUT = 15  # seconds
SLEEP_BETWEEN = 0.4  # respect du rate-limit plan Grow (≤ 55 req/min)


# ---------------------------------------------------------------------------
# Candidats à tester — un actif = N symboles possibles, on garde le 1er qui marche
# ---------------------------------------------------------------------------

# Format : (groupe, label_humain, [symboles candidats par ordre de préférence])
# Les "groupes" structurent le rapport (Indices, Métaux, Forex, Commodities, Vol).
CANDIDATES: List[Tuple[str, str, List[str]]] = [
    # --- INDICES (testés avec et sans préfixe) ---
    ("Indices", "S&P 500",        ["SPX", "GSPC", "^GSPC", "SPY"]),
    ("Indices", "Nasdaq Composite", ["IXIC", "^IXIC", "QQQ"]),
    ("Indices", "Nasdaq 100",     ["NDX", "^NDX", "QQQ"]),
    ("Indices", "CAC 40",         ["CAC", "FCHI", "^FCHI", "EWQ"]),
    ("Indices", "Russell 2000",   ["RUT", "^RUT", "IWM"]),
    ("Indices", "Euro Stoxx 50",  ["SX5E", "STOXX50E", "^STOXX50E", "FEZ"]),
    ("Indices", "Philly Semicond (SOX)", ["SOX", "^SOX", "SOXX"]),

    # --- VOLATILITÉ ---
    ("Volatilité", "VIX",         ["VIX", "^VIX", "VIXY"]),
    ("Volatilité", "VIX 3M",      ["VIX3M", "^VIX3M", "VXV"]),
    ("Volatilité", "VXN (Nasdaq)", ["VXN", "^VXN"]),
    ("Volatilité", "V2X (Euro)",  ["V2X", "^V2TX", "VSTOXX"]),
    ("Volatilité", "SKEW",        ["SKEW", "^SKEW"]),
    ("Volatilité", "VVIX",        ["VVIX", "^VVIX"]),

    # --- DOLLAR INDEX (le bug central — DXY n'est PAS sur Twelve plan Grow) ---
    # On teste plusieurs formats. UUP = ETF Invesco DB USD Bullish (proxy fiable).
    ("Dollar", "DXY",             ["DXY", "^DXY", "DX-Y.NYB", "USDX", "UUP"]),

    # --- TAUX / OBLIG ---
    ("Taux", "US 10Y yield",      ["TNX", "^TNX", "US10Y", "TIP"]),
    ("Taux", "US 2Y yield",       ["UST2Y", "^IRX", "US2Y"]),
    ("Taux", "Germany 10Y yield", ["DE10Y", "DEU10Y", "BUND"]),
    ("Taux", "France 10Y yield",  ["FR10Y", "FRA10Y", "OAT"]),

    # --- MÉTAUX (forex spot fonctionne, futures =F non) ---
    ("Métaux", "Or spot",         ["XAU/USD", "GC=F", "GLD"]),
    ("Métaux", "Argent spot",     ["XAG/USD", "SI=F", "SLV"]),
    ("Métaux", "Cuivre (HG)",     ["HG=F", "COPPER", "CPER"]),

    # --- ÉNERGIE (futures Yahoo =F ne marchent pas → ETF proxies) ---
    ("Énergie", "Brent",          ["BZ=F", "UKOIL", "BNO"]),
    ("Énergie", "WTI",            ["CL=F", "WTI", "USO"]),

    # --- SOFT COMMODITIES (futures ICE → ETF proxies/CFD) ---
    ("Softs", "Cacao (NY ICE)",   ["CC=F", "COCOA", "NIB"]),
    ("Softs", "Café Arabica",     ["KC=F", "COFFEE", "JO"]),
    ("Softs", "Café Robusta",     ["RC=F", "ROBUSTA"]),
    ("Softs", "Blé CBOT",         ["ZW=F", "WHEAT", "WEAT"]),
    ("Softs", "Cacao Londres",    ["C=F", "LCC"]),

    # --- FOREX (spot, généralement OK) ---
    ("Forex", "EUR/USD",          ["EUR/USD", "EURUSD", "EUR=X"]),
    ("Forex", "USD/JPY",          ["USD/JPY", "USDJPY", "JPY=X"]),
    ("Forex", "USD/BRL",          ["USD/BRL", "USDBRL"]),
    ("Forex", "USD/XOF (CFA)",    ["USD/XOF", "USDXOF"]),
    ("Forex", "USD/GHS (Ghana)",  ["USD/GHS", "USDGHS"]),

    # --- ETF (validation directe — proxies pour flux) ---
    ("ETF", "SPY", ["SPY"]),
    ("ETF", "QQQ", ["QQQ"]),
    ("ETF", "GLD", ["GLD"]),
    ("ETF", "SLV", ["SLV"]),
    ("ETF", "HYG (HY proxy)", ["HYG"]),
    ("ETF", "TIP (real yield proxy)", ["TIP"]),
]


# ---------------------------------------------------------------------------
# HTTP helper (mockable en tests)
# ---------------------------------------------------------------------------

def http_get_json(url: str, params: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> Optional[Any]:
    """GET JSON. Retourne None si erreur. (Mocké en tests.)"""
    try:
        import requests  # lazy
    except ImportError:
        logger.warning("requests non installé — HTTP désactivé")
        return None
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:  # noqa: BLE001
        logger.warning("HTTP GET %s : %s", url, e)
        return None


def _twelve_key() -> Optional[str]:
    k = os.environ.get("TWELVE_DATA_API_KEY")
    return k or None


# ---------------------------------------------------------------------------
# Test d'un symbole
# ---------------------------------------------------------------------------

def probe_symbol(symbol: str, *, sleep: float = SLEEP_BETWEEN) -> Dict[str, Any]:
    """Teste un symbole via /quote. Retourne {ok, value, error}.

    - ok=True si Twelve renvoie un champ 'close' numérique > 0.
    - ok=False sinon (status=error, vide, 404, parse KO).
    """
    key = _twelve_key()
    if not key:
        return {"ok": False, "value": None, "error": "TWELVE_DATA_API_KEY manquante"}
    params = {"symbol": symbol, "apikey": key, "format": "JSON"}
    data = http_get_json(f"{TWELVE_BASE}/quote", params=params)
    # respect rate-limit
    if sleep > 0:
        time.sleep(sleep)
    if data is None:
        return {"ok": False, "value": None, "error": "HTTP KO (timeout/connexion)"}
    if not isinstance(data, dict):
        return {"ok": False, "value": None, "error": f"réponse non-dict ({type(data).__name__})"}
    if data.get("status") == "error":
        return {"ok": False, "value": None, "error": data.get("message") or "status=error"}
    close = data.get("close")
    if close is None:
        return {"ok": False, "value": None, "error": "champ 'close' absent"}
    try:
        v = float(close)
    except (TypeError, ValueError):
        return {"ok": False, "value": None, "error": f"close non numérique : {close!r}"}
    if v <= 0:
        return {"ok": False, "value": v, "error": f"close <= 0 ({v})"}
    return {"ok": True, "value": v, "error": None}


def validate_all(candidates: List[Tuple[str, str, List[str]]] = CANDIDATES) -> List[dict]:
    """Pour chaque actif, teste tous les candidats. Retourne la liste structurée."""
    results: List[dict] = []
    for group, label, symbols in candidates:
        per_symbol: List[dict] = []
        winner: Optional[str] = None
        for sym in symbols:
            r = probe_symbol(sym)
            per_symbol.append({"symbol": sym, **r})
            if r["ok"] and winner is None:
                winner = sym
        results.append({
            "group": group,
            "label": label,
            "winner": winner,
            "tests": per_symbol,
        })
    return results


# ---------------------------------------------------------------------------
# Rapport markdown
# ---------------------------------------------------------------------------

def render_report(results: List[dict], *, now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    lines: List[str] = []
    lines.append("# Symbol validation — Twelve Data")
    lines.append("")
    lines.append(f"_Généré le {now.isoformat()} par `validate_symbols.py`._")
    lines.append("")
    lines.append("Pour chaque actif, plusieurs candidats sont testés via `/quote`.")
    lines.append("Le **winner** est le 1er candidat qui répond avec une valeur numérique > 0.")
    lines.append("→ Ce winner doit être utilisé dans `TWELVE_SYMBOLS` (criteres_calculator) et")
    lines.append("  dans `YAHOO_TO_TWELVE` (journaliste — pour stamp_prix_emission).")
    lines.append("")

    # Résumé : nombre d'actifs sans winner
    no_winner = [r for r in results if not r["winner"]]
    lines.append(f"## Résumé")
    lines.append("")
    lines.append(f"- Actifs testés : **{len(results)}**")
    lines.append(f"- Avec winner : **{len(results) - len(no_winner)}**")
    lines.append(f"- Sans winner (TOUS les candidats KO) : **{len(no_winner)}**")
    if no_winner:
        lines.append("")
        lines.append("### Actifs sans winner")
        for r in no_winner:
            lines.append(f"- **{r['label']}** ({r['group']}) — testés : "
                         + ", ".join(f"`{t['symbol']}`" for t in r["tests"]))
    lines.append("")

    # Détail par groupe
    by_group: Dict[str, List[dict]] = {}
    for r in results:
        by_group.setdefault(r["group"], []).append(r)
    for group, items in by_group.items():
        lines.append(f"## {group}")
        lines.append("")
        lines.append("| Actif | Winner | Détail des tests |")
        lines.append("|---|---|---|")
        for r in items:
            winner = f"`{r['winner']}`" if r["winner"] else "_(aucun)_"
            details = []
            for t in r["tests"]:
                if t["ok"]:
                    details.append(f"`{t['symbol']}` OK ({t['value']})")
                else:
                    err = (t["error"] or "")[:80]
                    details.append(f"`{t['symbol']}` KO ({err})")
            lines.append(f"| {r['label']} | {winner} | {' ; '.join(details)} |")
        lines.append("")

    return "\n".join(lines) + "\n"


def write_report(results: List[dict], path: Path = REPORT_OUT,
                 now: Optional[datetime] = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(results, now=now), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run() -> Path:
    if not _twelve_key():
        logger.warning("TWELVE_DATA_API_KEY manquante — rapport 'skip'.")
        # On écrit quand même un rapport explicite (red line : pas d'invention).
        now = datetime.now(timezone.utc)
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        REPORT_OUT.write_text(
            "# Symbol validation — Twelve Data\n\n"
            f"_Généré le {now.isoformat()} — **SKIP**._\n\n"
            "`TWELVE_DATA_API_KEY` non disponible dans l'environnement. "
            "Aucun symbole testé.\n",
            encoding="utf-8",
        )
        return REPORT_OUT
    results = validate_all()
    return write_report(results)


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    path = run()
    print(f"OK : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
