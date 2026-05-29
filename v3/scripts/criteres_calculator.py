"""TradingApp v3 — Critères courants (v1 câblé).

Produit `v3/data/criteres-courants.md` à partir de :
- Twelve Data (prix, séries → z-scores, lineaires bruts)
- CFTC COT (Socrata public, pas de clé) → managed money nets z-score
- EIA API (clé requise) → crude stocks niveau (z-score à défaut de consensus)
- Open-Meteo (public, pas de clé) → anomalies météo zones agri
- triggers_classifier (events-log + triggers-and-windows.yml) → triplets + calendrier

Red line : zéro invention. Source injoignable / clé absente / valeur non
disponible → critère OMIS (le scoring le marquera n/a, poids 0). Log WARNING
par source ratée + compteur de skip global.

Format de sortie pour le scoring (cf. scoring_analyste.normalise) :
- zscore  → `valeur_normalisee` pré-calculée (z/zscore_div, capé)
- lineaire → `valeur` brute (le scoring applique centre/echelle/cap)
- triplet  → `valeur` ∈ {-1, 0, +1}
- gate     → `valeur: bool`
"""

from __future__ import annotations

import json
import logging
import math
import os
import statistics
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import yaml

logger = logging.getLogger("criteres_calculator")

ROOT = Path(__file__).resolve().parents[1]
FICHES_DIR = ROOT / "config" / "fiches"
TRIGGERS_YML = ROOT / "config" / "triggers-and-windows.yml"
EVENTS_LOG = ROOT / "data" / "events-log.md"
CRITERES_OUT = ROOT / "data" / "criteres-courants.md"

# Import local
sys.path.insert(0, str(Path(__file__).resolve().parent))
import triggers_classifier as tc  # noqa: E402

# Compteurs globaux de skip (instrumentation)
SKIP_COUNTER: Counter = Counter()

DEFAULT_TIMEOUT = 15  # seconds


# ---------------------------------------------------------------------------
# HTTP helper (mockable en tests)
# ---------------------------------------------------------------------------

def http_get_json(url: str, params: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT) -> Optional[Any]:
    """GET JSON avec timeout. Retourne None si erreur (et log WARNING)."""
    try:
        import requests  # lazy import (testable)
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


# ---------------------------------------------------------------------------
# Twelve Data
# ---------------------------------------------------------------------------

TWELVE_BASE = "https://api.twelvedata.com"


def _twelve_key() -> Optional[str]:
    k = os.environ.get("TWELVE_DATA_API_KEY")
    return k or None


def fetch_twelve_series(symbol: str, *, interval: str = "1day", outputsize: int = 60) -> Optional[List[Tuple[datetime, float]]]:
    """Retourne [(datetime_utc, close)] triée oldest→newest. None si indisponible."""
    key = _twelve_key()
    if not key:
        SKIP_COUNTER["twelve_no_key"] += 1
        logger.warning("TWELVE_DATA_API_KEY manquante — symbol=%s skip", symbol)
        return None
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": key,
        "format": "JSON",
        "order": "ASC",
    }
    data = http_get_json(f"{TWELVE_BASE}/time_series", params=params)
    if not isinstance(data, dict):
        SKIP_COUNTER[f"twelve_dead:{symbol}"] += 1
        return None
    if data.get("status") == "error":
        logger.warning("TwelveData error symbol=%s : %s", symbol, data.get("message"))
        SKIP_COUNTER[f"twelve_err:{symbol}"] += 1
        return None
    values = data.get("values")
    if not isinstance(values, list) or not values:
        SKIP_COUNTER[f"twelve_empty:{symbol}"] += 1
        return None
    out: List[Tuple[datetime, float]] = []
    for v in values:
        try:
            dt = datetime.fromisoformat(v["datetime"]).replace(tzinfo=timezone.utc)
            close = float(v["close"])
        except (KeyError, ValueError, TypeError):
            continue
        out.append((dt, close))
    if not out:
        SKIP_COUNTER[f"twelve_parse:{symbol}"] += 1
        return None
    out.sort(key=lambda t: t[0])
    return out


def fetch_twelve_price(symbol: str) -> Optional[float]:
    """Dernier close. None si indisponible."""
    series = fetch_twelve_series(symbol, outputsize=5)
    if not series:
        return None
    return series[-1][1]


# ---------------------------------------------------------------------------
# CFTC COT (Socrata)
# ---------------------------------------------------------------------------

CFTC_BASE = "https://publicreporting.cftc.gov/resource/jun7-fc8e.json"
# Mapping cle_courante → market_and_exchange_names (approximatif, à valider)
CFTC_MARKETS = {
    "cftc_cot_crude_nets": "CRUDE OIL, LIGHT SWEET-WTI - NEW YORK MERCANTILE EXCHANGE",
    "cftc_cot_nets": "GOLD - COMMODITY EXCHANGE INC.",  # or
    "cftc_cot_copper_nets": "COPPER- #1 - COMMODITY EXCHANGE INC.",
    "cftc_cot_silver_nets": "SILVER - COMMODITY EXCHANGE INC.",
    "cftc_cot_wheat_nets": "WHEAT-SRW - CHICAGO BOARD OF TRADE",
    "cftc_cot_cocoa_nets": "COCOA - ICE FUTURES U.S.",
    "cftc_cot_coffee_nets": "COFFEE C - ICE FUTURES U.S.",
}


def fetch_cftc_managed_money_nets(market: str, *, weeks: int = 260) -> Optional[List[float]]:
    """Retourne la série des nets managed money (long - short) sur N semaines (oldest→newest)."""
    params = {
        "$select": "report_date_as_yyyy_mm_dd,m_money_positions_long_all,m_money_positions_short_all",
        "$where": f"market_and_exchange_names='{market}'",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": weeks,
    }
    data = http_get_json(CFTC_BASE, params=params)
    if not isinstance(data, list) or not data:
        SKIP_COUNTER[f"cftc_dead:{market}"] += 1
        return None
    nets: List[Tuple[datetime, float]] = []
    for row in data:
        try:
            dt = datetime.fromisoformat(row["report_date_as_yyyy_mm_dd"].replace("Z", "")).replace(tzinfo=timezone.utc)
            longp = float(row["m_money_positions_long_all"])
            shortp = float(row["m_money_positions_short_all"])
        except (KeyError, ValueError, TypeError):
            continue
        nets.append((dt, longp - shortp))
    if not nets:
        SKIP_COUNTER[f"cftc_parse:{market}"] += 1
        return None
    nets.sort(key=lambda t: t[0])
    return [n for _, n in nets]


# ---------------------------------------------------------------------------
# EIA
# ---------------------------------------------------------------------------

EIA_BASE = "https://api.eia.gov/v2"


def _eia_key() -> Optional[str]:
    k = os.environ.get("EIA_API_KEY")
    return k or None


def fetch_eia_series(series_path: str, *, length: int = 60) -> Optional[List[float]]:
    """Récupère N derniers points d'une série EIA. Path = endpoint v2 (ex: 'petroleum/stoc/wstk').
    Retourne valeurs oldest→newest. None si KO ou clé manquante."""
    key = _eia_key()
    if not key:
        SKIP_COUNTER["eia_no_key"] += 1
        logger.warning("EIA_API_KEY manquante — series=%s skip", series_path)
        return None
    params = {
        "api_key": key,
        "frequency": "weekly",
        "data[0]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": length,
    }
    data = http_get_json(f"{EIA_BASE}/{series_path}/data/", params=params)
    if not isinstance(data, dict):
        SKIP_COUNTER[f"eia_dead:{series_path}"] += 1
        return None
    resp = data.get("response", {})
    rows = resp.get("data") if isinstance(resp, dict) else None
    if not isinstance(rows, list) or not rows:
        SKIP_COUNTER[f"eia_empty:{series_path}"] += 1
        return None
    vals: List[Tuple[str, float]] = []
    for row in rows:
        try:
            period = row.get("period")
            val = float(row.get("value"))
        except (TypeError, ValueError):
            continue
        if period is None:
            continue
        vals.append((period, val))
    if not vals:
        return None
    vals.sort(key=lambda t: t[0])
    return [v for _, v in vals]


# ---------------------------------------------------------------------------
# Open-Meteo (anomalies météo)
# ---------------------------------------------------------------------------

OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"

# Zones agri (lat, lon) — centroides indicatifs
METEO_ZONES = {
    "minas_gerais": (-19.5, -44.0),       # café Brésil
    "cote_ivoire_ghana": (6.5, -3.0),     # cacao
    "vietnam_central_highlands": (12.7, 108.0),  # café robusta
    "australia_wheatbelt": (-31.5, 117.0),  # blé
    "us_midwest": (41.5, -93.5),          # blé US
}


def fetch_open_meteo_anomaly(lat: float, lon: float, *, days: int = 90) -> Optional[float]:
    """Anomalie z-score de précipitations sur les `days` derniers jours vs même fenêtre 30 ans avant.
    Retourne le z ou None si KO. Implémentation simplifiée : on compare la moyenne récente à la
    moyenne longue (climatologie sur 365×5 jours)."""
    today = date.today()
    end = today - timedelta(days=1)
    start = end - timedelta(days=days)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "precipitation_sum",
        "timezone": "UTC",
    }
    data = http_get_json(OPEN_METEO_ARCHIVE, params=params)
    if not isinstance(data, dict):
        SKIP_COUNTER[f"meteo_dead:{lat},{lon}"] += 1
        return None
    daily = data.get("daily", {})
    series = daily.get("precipitation_sum") if isinstance(daily, dict) else None
    if not isinstance(series, list) or len(series) < 10:
        SKIP_COUNTER[f"meteo_empty:{lat},{lon}"] += 1
        return None
    try:
        clean = [float(x) for x in series if x is not None]
    except (TypeError, ValueError):
        return None
    if len(clean) < 10:
        return None
    # Climatologie 5 ans
    clim_start = end - timedelta(days=365 * 5)
    clim_end = end - timedelta(days=days)
    params2 = dict(params)
    params2["start_date"] = clim_start.isoformat()
    params2["end_date"] = clim_end.isoformat()
    data2 = http_get_json(OPEN_METEO_ARCHIVE, params=params2)
    if not isinstance(data2, dict):
        SKIP_COUNTER[f"meteo_clim_dead:{lat},{lon}"] += 1
        return None
    clim_series = data2.get("daily", {}).get("precipitation_sum") if isinstance(data2.get("daily"), dict) else None
    if not isinstance(clim_series, list) or len(clim_series) < 30:
        return None
    try:
        clim_clean = [float(x) for x in clim_series if x is not None]
    except (TypeError, ValueError):
        return None
    if len(clim_clean) < 30:
        return None
    recent_mean = statistics.fmean(clean)
    clim_mean = statistics.fmean(clim_clean)
    clim_std = statistics.pstdev(clim_clean)
    if clim_std == 0:
        return None
    return (recent_mean - clim_mean) / clim_std


# ---------------------------------------------------------------------------
# Z-score utility (cap selon fiche)
# ---------------------------------------------------------------------------

def compute_zscore_normalisee(value: float, history: List[float], *, zscore_div: float, cap: float) -> Optional[float]:
    """Calcule (z / zscore_div) capé. history doit inclure ou exclure value indifféremment
    (statistiquement on prend l'ensemble fourni comme référence)."""
    if not history or len(history) < 2:
        return None
    mean = statistics.fmean(history)
    std = statistics.pstdev(history)
    if std == 0:
        return None
    z = (value - mean) / std
    norm = z / zscore_div
    return max(-cap, min(cap, norm))


# ---------------------------------------------------------------------------
# Mapping cle_courante → fetcher
# ---------------------------------------------------------------------------

# Tickers Twelve Data pour critères standardisés
TWELVE_TICKERS = {
    "dxy_trend_20j": "DXY",
    "vix_risk_off_proxy": "VIX",
    "vix_niveau": "VIX",
}

# Symboles Twelve Data composites
COMPOSITE_PRICES = {
    # ratio_cuivre_or = HG=F / GC=F (proxy via Twelve : "XCU/USD" or use futures symbols)
    # On reste prudent : ratios omis si Twelve ne fournit pas les 2 symboles
}


def _make_zscore_critere(value: float, history: List[float], crit: dict, ts: str) -> Optional[dict]:
    div = float(crit.get("zscore_div", 2.0))
    cap = float(crit.get("cap", 1.0))
    norm = compute_zscore_normalisee(value, history, zscore_div=div, cap=cap)
    if norm is None:
        return None
    return {"valeur": value, "valeur_normalisee": norm, "ts": ts}


def _handle_twelve_zscore(symbol: str, crit: dict, ts: str) -> Optional[dict]:
    window = int(crit.get("zscore_window", 60))
    series = fetch_twelve_series(symbol, outputsize=window + 5)
    if not series or len(series) < max(10, window // 4):
        return None
    closes = [c for _, c in series]
    value = closes[-1]
    history = closes[-window:] if len(closes) >= window else closes
    return _make_zscore_critere(value, history, crit, ts)


def _handle_twelve_lineaire(symbol: str, crit: dict, ts: str) -> Optional[dict]:
    price = fetch_twelve_price(symbol)
    if price is None:
        return None
    return {"valeur": price, "ts": ts}


def _handle_cftc(cle: str, crit: dict, ts: str) -> Optional[dict]:
    market = CFTC_MARKETS.get(cle)
    if not market:
        return None
    window = int(crit.get("zscore_window", 252))
    nets = fetch_cftc_managed_money_nets(market, weeks=max(window + 10, 260))
    if not nets or len(nets) < 20:
        return None
    value = nets[-1]
    history = nets[-window:] if len(nets) >= window else nets
    return _make_zscore_critere(value, history, crit, ts)


def _handle_eia_crude(crit: dict, ts: str) -> Optional[dict]:
    """EIA WCRSTUS1 — Crude oil stocks (weekly), niveau brut z-scoré (faute de consensus)."""
    window = int(crit.get("zscore_window", 52))
    series = fetch_eia_series("petroleum/stoc/wstk", length=window + 10)
    if not series or len(series) < 10:
        return None
    value = series[-1]
    history = series[-window:] if len(series) >= window else series
    return _make_zscore_critere(value, history, crit, ts)


# ---------------------------------------------------------------------------
# Fenêtres d'activation
# ---------------------------------------------------------------------------

def is_in_activation_window(cle: str, now: datetime, triggers_cfg: dict, fiche_key: str) -> Optional[bool]:
    """Retourne True/False si la fenêtre est définie pour ce critère, None sinon.

    Implémentation simplifiée par règles connues (cf. triggers-and-windows.yml) :
    - eia_crude_surprise : mercredi 16h30 CET → vendredi 16h30 CET
    - api_weekly_surprise / api_bulletin_surprise : mardi 22h30 → mercredi 16h30 CET
    - caixin_pmi_manuf : 1er jour ouvré du mois → +7j
    - wasde : ~10 du mois → +7j
    - nass_crop_progress : lundi 22h → vendredi 22h CET (saison avril-novembre)
    - grindings : ouvert 14j après mi-jan/avril/juil/oct
    Hors fenêtre → False. Inconnu → None (= pas de fenêtre à appliquer).
    """
    try:
        cet = now.astimezone(ZoneInfo("Europe/Paris"))
    except Exception:  # noqa: BLE001
        cet = now
    wd = cet.weekday()  # 0=Lundi
    h = cet.hour + cet.minute / 60.0
    m = cet.month
    d = cet.day

    if cle == "eia_crude_surprise":
        # Mercredi 16h30 → Vendredi 16h30
        if wd == 2 and h >= 16.5:
            return True
        if wd == 3:
            return True
        if wd == 4 and h < 16.5:
            return True
        return False
    if cle in ("api_weekly_surprise", "api_bulletin_surprise"):
        # Mardi 22h30 → Mercredi 16h30
        if wd == 1 and h >= 22.5:
            return True
        if wd == 2 and h < 16.5:
            return True
        return False
    if cle == "caixin_pmi_manuf":
        # 1er jour ouvré → +7j ouvrés ≈ 9j calendaires (approx)
        return d <= 9
    if cle == "wasde":
        return 8 <= d <= 17
    if cle == "nass_crop_progress":
        if m < 4 or m > 11:
            return False
        # Lundi 22h → Vendredi 22h
        if wd == 0 and h >= 22:
            return True
        if 1 <= wd <= 3:
            return True
        if wd == 4 and h < 22:
            return True
        return False
    if cle == "grindings":
        # mi-jan / mi-avril / mi-juil / mi-oct → +14j
        if m in (1, 4, 7, 10) and 15 <= d <= 29:
            return True
        return False
    return None  # pas de fenêtre


# ---------------------------------------------------------------------------
# Construction des critères par fiche
# ---------------------------------------------------------------------------

def _resolve_gate(cle: str, now: datetime, events: List[dict]) -> bool:
    """Heuristique GATE : vrai si EIA fenêtre active OU triggers géopol récents (<48h).
    Inconnu → False."""
    # EIA fenêtre = gate "EIA publication < 4h" → on prend la fenêtre étendue
    try:
        cet = now.astimezone(ZoneInfo("Europe/Paris"))
    except Exception:  # noqa: BLE001
        cet = now
    if cet.weekday() == 2 and 16 <= cet.hour <= 17:
        return True
    # Heuristique : un event triggerable < 48h ? on regarde les events récents.
    cutoff = now - timedelta(hours=48)
    for ev in events:
        dt = ev.get("_dt")
        if isinstance(dt, datetime) and dt >= cutoff:
            text = tc._event_text(ev).lower()
            if any(k in text for k in ("fomc", "cpi", "nfp", "frappes", "opec", "escalation", "escalade")):
                return True
    return False


def build_critere_value(
    fiche_key: str,
    crit: dict,
    triplets: Dict[str, int],
    triggers_cfg: dict,
    events: List[dict],
    now: datetime,
) -> Optional[dict]:
    """Retourne le dict {valeur, [valeur_normalisee], ts} ou None si critère à omettre."""
    cle = crit.get("cle_courante")
    if not cle:
        return None
    type_norm = crit.get("normalisation")
    source = (crit.get("source") or "").lower()
    ts = now.isoformat()

    # GATE
    if type_norm == "gate":
        return {"valeur": _resolve_gate(cle, now, events), "ts": ts}

    # Triplet (résolu par triggers_classifier)
    if type_norm == "triplet":
        if cle in triplets:
            return {"valeur": int(triplets[cle]), "ts": ts}
        # Pas dans le triggers config → on essaye 0 (neutre, conforme règle « ne match rien → 0 »)
        SKIP_COUNTER[f"triplet_no_cfg:{cle}"] += 1
        return {"valeur": 0, "ts": ts}

    # Fenêtre d'activation (pour numerique)
    in_window = is_in_activation_window(cle, now, triggers_cfg, fiche_key)
    if in_window is False:
        # Hors fenêtre → contribution 0 (poids effectif 0). On émet valeur_normalisee=0 directement.
        return {"valeur_normalisee": 0.0, "ts": ts, "note": "hors fenêtre"}

    # Numerique (zscore / lineaire)
    if type_norm == "zscore":
        # Critères Twelve Data standardisés
        if "twelve" in source or cle in TWELVE_TICKERS:
            symbol = TWELVE_TICKERS.get(cle)
            if symbol:
                return _handle_twelve_zscore(symbol, crit, ts)
            SKIP_COUNTER[f"no_ticker:{cle}"] += 1
            return None
        if "cftc" in source or cle.startswith("cftc_"):
            return _handle_cftc(cle, crit, ts)
        if "eia" in source:
            if cle in ("eia_crude_surprise", "cushing_stocks"):
                return _handle_eia_crude(crit, ts)
            SKIP_COUNTER[f"eia_no_route:{cle}"] += 1
            return None
        # Autre source non câblée
        SKIP_COUNTER[f"zscore_unmapped:{cle}"] += 1
        return None

    if type_norm == "lineaire":
        if "twelve" in source or cle in TWELVE_TICKERS:
            symbol = TWELVE_TICKERS.get(cle)
            if symbol:
                return _handle_twelve_lineaire(symbol, crit, ts)
        SKIP_COUNTER[f"lineaire_unmapped:{cle}"] += 1
        return None

    SKIP_COUNTER[f"unknown_norm:{type_norm}"] += 1
    return None


def collect_for_fiche(
    fiche_key: str,
    fiche: dict,
    triplets: Dict[str, int],
    triggers_cfg: dict,
    events: List[dict],
    now: datetime,
) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for crit in fiche.get("criteres", []):
        cle = crit.get("cle_courante")
        if not cle:
            continue
        try:
            val = build_critere_value(fiche_key, crit, triplets, triggers_cfg, events, now)
        except Exception as e:  # noqa: BLE001
            logger.warning("Critère %s/%s : exception %s — omis", fiche_key, cle, e)
            SKIP_COUNTER[f"exception:{cle}"] += 1
            continue
        if val is None:
            continue
        out[cle] = val
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


def load_fiches(fiches_dir: Path = FICHES_DIR) -> Dict[str, dict]:
    fiches: Dict[str, dict] = {}
    for f in sorted(fiches_dir.glob("*.yml")):
        with f.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and "criteres" in data:
            fiches[f.stem] = data
    return fiches


def run(now: Optional[datetime] = None) -> Path:
    SKIP_COUNTER.clear()
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    fiches = load_fiches()
    triggers_cfg = tc.load_triggers_config()
    events = tc.parse_events_log()
    triplets_by_actif = tc.classify_all(events=events, today=now, triggers_cfg=triggers_cfg)

    payload: Dict[str, Any] = {"last_update": now.isoformat()}
    total_crit = 0
    total_filled = 0
    for key, fiche in fiches.items():
        actif_triplets = triplets_by_actif.get(key, {})
        crits = collect_for_fiche(key, fiche, actif_triplets, triggers_cfg, events, now)
        payload[key] = crits
        total_crit += len(fiche.get("criteres", []))
        total_filled += len(crits)

    out = write_criteres(payload)
    logger.info("Critères : %d/%d alimentés (%.0f%%)", total_filled, total_crit,
                100.0 * total_filled / max(total_crit, 1))
    if SKIP_COUNTER:
        logger.info("Skips : %s", dict(SKIP_COUNTER))
    return out


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
