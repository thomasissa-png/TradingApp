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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("validate_symbols")

ROOT = Path(__file__).resolve().parents[1]
REPORT_OUT = ROOT / "data" / "symbol-validation.md"

# Sonde 8h Paris — rapport audit dédié (NE TOUCHE PAS aux fiches/suivi.yaml).
# IMPORTANT : la sonde écrit dans `-run.md` (output machine, réécrit à chaque
# run CI). Le VERDICT d'analyse humain vit dans `symbol-validation-8h.md` et
# n'est JAMAIS écrasé par la sonde (sinon on perd l'analyse PROVE-FIRST).
FRESHNESS_REPORT_OUT = ROOT / "audit" / "symbol-validation-8h-run.md"

# Candidats futures pour la référence "8h Paris" (Globex cote, ETF SPY/QQQ/VIXY non).
# But : permettre de noter S&P 500 / Nasdaq / VIX depuis une réf 8h Paris au lieu
# de l'ouverture cash US 15h30. PROVE-FIRST : on mesure la dispo, on ne mappe rien.
#   ES=F : E-mini S&P 500 future (CME Globex)
#   NQ=F : E-mini Nasdaq 100 future (CME Globex)
#   VX=F : VIX future (CFE)
# Variantes testées : format Yahoo (=F) + symboles "purs" éventuels côté Twelve.
FUTURES_8H_CANDIDATES: List[Tuple[str, str, List[str]]] = [
    ("S&P 500 future",  "ES=F", ["ES=F", "ES", "ES1!", "ES1", "/ES"]),
    ("Nasdaq 100 future", "NQ=F", ["NQ=F", "NQ", "NQ1!", "NQ1", "/NQ"]),
    ("VIX future",      "VX=F", ["VX=F", "VX", "VX1!", "VX1", "/VX"]),
]

# Fenêtre de fraîcheur : à 8h00-8h30 Paris, un prix "frais" doit dater du jour
# courant (Globex cote la nuit). Un close de la veille (datetime J-1) = PÉRIMÉ.
# Seuil de tolérance : on accepte un timestamp < FRESHNESS_MAX_AGE_H heures.
FRESHNESS_MAX_AGE_H = 18  # > nuit Globex, < close veille 22h (J-1) à 8h (J) ≈ 10h

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
# Sonde de fraîcheur 8h Paris (futures Globex) — PROVE-FIRST
# ---------------------------------------------------------------------------

def _parse_quote_timestamp(data: dict) -> Optional[datetime]:
    """Extrait l'horodatage du dernier prix d'une réponse Twelve /quote.

    Twelve renvoie soit `timestamp` (epoch UNIX, UTC), soit `datetime`
    (chaîne "YYYY-MM-DD HH:MM:SS" en heure d'exchange). On privilégie
    `timestamp` (sans ambiguïté de fuseau). Retourne un datetime aware UTC
    ou None si rien d'exploitable (zéro invention : pas d'heure fabriquée).
    """
    ts = data.get("timestamp")
    if ts is not None:
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except (TypeError, ValueError, OSError):
            pass
    dt = data.get("datetime")
    if isinstance(dt, str) and dt.strip():
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                # Heure d'exchange, fuseau inconnu ici → on la traite comme UTC
                # pour un calcul d'âge GROSSIER (suffit à distinguer J vs J-1).
                return datetime.strptime(dt.strip(), fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def probe_freshness(symbol: str, *, now: Optional[datetime] = None,
                    sleep: float = SLEEP_BETWEEN) -> Dict[str, Any]:
    """Teste (a) le symbole RÉPOND et (b) son dernier prix est FRAIS.

    Retourne {ok, value, ts (iso|None), age_h (float|None), fresh (bool|None), error}.
      - ok       : Twelve renvoie un close numérique > 0 (le symbole existe).
      - fresh    : le dernier prix date de moins de FRESHNESS_MAX_AGE_H heures.
      - fresh=None : symbole OK mais Twelve ne fournit AUCUN horodatage
                     exploitable → fraîcheur indéterminable (on NE conclut pas).
    """
    now = now or datetime.now(timezone.utc)
    key = _twelve_key()
    if not key:
        return {"ok": False, "value": None, "ts": None, "age_h": None,
                "fresh": None, "error": "TWELVE_DATA_API_KEY manquante"}
    params = {"symbol": symbol, "apikey": key, "format": "JSON"}
    data = http_get_json(f"{TWELVE_BASE}/quote", params=params)
    if sleep > 0:
        time.sleep(sleep)
    if not isinstance(data, dict):
        return {"ok": False, "value": None, "ts": None, "age_h": None,
                "fresh": None, "error": "HTTP KO / réponse non-dict"}
    if data.get("status") == "error":
        return {"ok": False, "value": None, "ts": None, "age_h": None,
                "fresh": None, "error": data.get("message") or "status=error"}
    close = data.get("close")
    try:
        v = float(close) if close is not None else None
    except (TypeError, ValueError):
        v = None
    if v is None or v <= 0:
        return {"ok": False, "value": v, "ts": None, "age_h": None,
                "fresh": None, "error": f"close absent/invalide ({close!r})"}

    ts = _parse_quote_timestamp(data)
    if ts is None:
        # Symbole vivant mais sans horodatage → fraîcheur indéterminable.
        return {"ok": True, "value": v, "ts": None, "age_h": None,
                "fresh": None, "error": "horodatage absent (fraîcheur indéterminable)"}
    age_h = (now - ts).total_seconds() / 3600.0
    fresh = age_h < FRESHNESS_MAX_AGE_H
    return {"ok": True, "value": v, "ts": ts.isoformat(),
            "age_h": round(age_h, 2), "fresh": fresh, "error": None}


def probe_futures_8h(candidates=FUTURES_8H_CANDIDATES, *,
                     now: Optional[datetime] = None) -> List[dict]:
    """Teste les candidats futures (ES/NQ/VX) : réponse + fraîcheur 8h.

    Pour chaque actif, garde le 1er symbole qui répond ET (si possible) frais.
    """
    now = now or datetime.now(timezone.utc)
    results: List[dict] = []
    for label, yahoo, symbols in candidates:
        per_symbol: List[dict] = []
        winner: Optional[str] = None
        winner_fresh: Optional[bool] = None
        for sym in symbols:
            r = probe_freshness(sym, now=now)
            per_symbol.append({"symbol": sym, **r})
            if r["ok"] and winner is None:
                winner = sym
                winner_fresh = r["fresh"]
        results.append({
            "label": label,
            "yahoo": yahoo,
            "winner": winner,
            "winner_fresh": winner_fresh,
            "tests": per_symbol,
        })
    return results


def render_freshness_report(results: List[dict], *,
                            now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    paris_hint = (now + timedelta(hours=2)).strftime("%H:%M")  # CEST grossier
    lines: List[str] = []
    lines.append("# Sonde 8h Paris — futures indices/VIX (ES=F / NQ=F / VX=F)")
    lines.append("")
    lines.append(f"_Généré le {now.isoformat()} (~{paris_hint} Paris) par `validate_symbols.probe_futures_8h`._")
    lines.append("")
    lines.append("**But** : noter S&P 500 / Nasdaq / VIX depuis une référence **8h Paris** "
                 "(turbos sur futures Globex) au lieu de l'ouverture cash US 15h30.")
    lines.append("")
    lines.append("**PROVE-FIRST** : cette sonde MESURE la disponibilité. Elle ne touche "
                 "NI aux fiches NI à `suivi.yaml`. Le mapping ne se fera qu'APRÈS validation Thomas.")
    lines.append("")
    lines.append("Critères : (a) le symbole RÉPOND (close > 0) ; (b) le prix est **FRAIS** "
                 f"(< {FRESHNESS_MAX_AGE_H}h → daté du jour, pas un close veille).")
    lines.append("")
    lines.append("| Actif | Yahoo | Winner Twelve | Frais 8h ? | Détail |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        winner = f"`{r['winner']}`" if r["winner"] else "_(aucun)_"
        if r["winner"] is None:
            fresh_cell = "n/a (KO)"
        elif r["winner_fresh"] is True:
            fresh_cell = "✅ frais"
        elif r["winner_fresh"] is False:
            fresh_cell = "❌ périmé (close veille)"
        else:
            fresh_cell = "❓ indéterminable (pas d'horodatage)"
        details = []
        for t in r["tests"]:
            if t["ok"]:
                age = f"{t['age_h']}h" if t.get("age_h") is not None else "âge?"
                details.append(f"`{t['symbol']}` OK ({t['value']}, {age})")
            else:
                err = (t["error"] or "")[:50]
                details.append(f"`{t['symbol']}` KO ({err})")
        lines.append(f"| {r['label']} | `{r['yahoo']}` | {winner} | {fresh_cell} | {' ; '.join(details)} |")
    lines.append("")
    lines.append("## Lecture")
    lines.append("")
    lines.append("- **Winner + frais ✅** → mapping 8h envisageable (à valider Thomas).")
    lines.append("- **Aucun winner** → Twelve free/Grow n'expose pas ce future → fallback yfinance "
                 "→ **n/a sur GitHub Actions** (Yahoo bloque les IP datacenter) → **pas de réf 8h gratuite**.")
    lines.append("- **Winner mais périmé ❌** → cote mais pas à 8h Paris → inutile pour la réf 8h.")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_freshness_report(results: List[dict], path: Path = FRESHNESS_REPORT_OUT,
                           now: Optional[datetime] = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_freshness_report(results, now=now), encoding="utf-8")
    return path


def run_freshness_8h() -> Path:
    """CLI dédié sonde 8h : à lancer sur GitHub Actions à 8h00-8h30 Paris."""
    if not _twelve_key():
        logger.warning("TWELVE_DATA_API_KEY manquante — sonde 8h 'skip'.")
        now = datetime.now(timezone.utc)
        FRESHNESS_REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        FRESHNESS_REPORT_OUT.write_text(
            "# Sonde 8h Paris — futures indices/VIX\n\n"
            f"_Généré le {now.isoformat()} — **SKIP**._\n\n"
            "`TWELVE_DATA_API_KEY` non disponible. Aucun symbole testé.\n",
            encoding="utf-8",
        )
        return FRESHNESS_REPORT_OUT
    results = probe_futures_8h()
    return write_freshness_report(results)


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
    argv = sys.argv[1:] if argv is None else argv
    if "--freshness-8h" in argv:
        path = run_freshness_8h()
        print(f"OK (sonde 8h) : {path}")
        return 0
    path = run()
    print(f"OK : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
