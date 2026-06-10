"""TradingApp v3 — Moteur de backtest QUANT-only (itération 1).

Objectif : mesurer l'edge directionnel du moteur quant sur historique, en
réutilisant les VRAIES formules de normalisation/scoring du pipeline live
(`v3/scripts/scoring_analyste.normalise` + `score_actif` via construction
manuelle des `valeurs_actif`). Aucune réimplémentation divergente.

Principes :
- Zéro look-ahead : à chaque date de test, on n'utilise QUE les barres OHLCV
  strictement antérieures à cette date (via `series_asof`).
- Critères non-câblables en backtest historique (COT, FRED, météo, news,
  triplets manuels) → marqués n/a (poids effectif 0). Documenté.
- Critères QUANT price-derived REPRODUITS via les formules live :
  - z-score sur fenêtre de prix : `zscore_from_series` (live)
  - RSI 14j : `_compute_rsi` (live)
  - perf 5j : closes[-1] / closes[-6] - 1
  - ratios A/B et spreads A-B : alignés par date, z-score sur fenêtre
  - alpha 5j A vs B : perf(A,5j) - perf(B,5j), z-score
- Pour les critères qui dépendraient de symboles ABSENTS du backtest (CFTC,
  FRED, breadth, news, météo...) → on les laisse à None et `normalise()` les
  renvoie n/a proprement.

Verdict GO/NO-GO (audit scope-backtest §2.4, P0) :
- directional accuracy OOS ≥ 60% (vs < 55% NO-GO)
- Wilson lower bound 95% OOS ≥ 55% (vs < 50% NO-GO)
- p-value bootstrap (1000 permutations) < 0.05
"""

from __future__ import annotations

import logging
import math
import random
import statistics
import sys
import warnings
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import des formules LIVE — c'est le cœur de la promesse "même moteur"
from scoring_analyste import normalise, score_actif, load_fiches, HORIZONS  # noqa: E402
from criteres_calculator import (  # noqa: E402
    _compute_rsi,
    zscore_from_series,
    compute_zscore_normalisee,
)
from historical_data import (  # noqa: E402
    series_asof,
    future_return,
    non_overlapping_trading_dates,
    fred_series_asof,
    fred_spread_asof,
    fred_delta_asof,
    cot_nets_asof,
    TICKERS_V1,
    TICKERS_V2_EXTENSION,
    TICKER_TO_FICHE,
    _get_full_df,
    _to_date,
)
# Mappings FRED/CFTC LIVE — réutilisés tels quels (zéro divergence)
from criteres_calculator import (  # noqa: E402
    FRED_SERIES_SIMPLE,
    FRED_SPREADS,
    FRED_DELTA,
    CFTC_MARKETS,
)

logger = logging.getLogger("backtest.backtest_quant")


# ---------------------------------------------------------------------------
# Quant feature builders (réutilisent les formules live)
# ---------------------------------------------------------------------------

def _df_to_closes_dates(df) -> Tuple[List, List[float]]:
    """DataFrame OHLCV → (dates, closes) triés croissants."""
    dates = [d.date() for d in df.index]
    closes = [float(c) for c in df["Close"].tolist()]
    return dates, closes


def quant_zscore_single(ticker: str, as_of, *, window: int, zscore_div: float = 2.0,
                        cap: float = 1.0, lookback_days: Optional[int] = None) -> Optional[Dict[str, float]]:
    """z-score sur les closes d'un ticker, fenêtre `window` jours de trading,
    AS OF `as_of` (no look-ahead). Renvoie {valeur, valeur_normalisee} compatible
    avec le format attendu par `normalise(type='zscore')`."""
    lb = lookback_days or max(window * 2 + 20, 60)
    df = series_asof(ticker, as_of, lookback_days=lb)
    if df is None or len(df) < max(10, window // 4):
        return None
    closes = [float(c) for c in df["Close"].tolist()]
    hist = closes[-window:] if len(closes) >= window else closes
    res = zscore_from_series(hist, zscore_div=zscore_div, cap=cap)
    if res is None:
        return None
    return {"valeur": res[0], "valeur_normalisee": res[1]}


def quant_rsi(ticker: str, as_of, *, period: int = 14, lookback_days: int = 90) -> Optional[float]:
    """RSI Wilder calculé localement via la formule live `_compute_rsi`."""
    df = series_asof(ticker, as_of, lookback_days=lookback_days)
    if df is None or len(df) < period + 1:
        return None
    closes = [float(c) for c in df["Close"].tolist()]
    return _compute_rsi(closes, period=period)


def quant_perf_5j_zscore(ticker: str, as_of, *, window: int = 60,
                         zscore_div: float = 2.0, cap: float = 1.0) -> Optional[Dict[str, float]]:
    """Perf 5j glissante → z-score sur fenêtre. Mime la logique live de
    `_handle_twelve_zscore_dispatch` pour `flux_etf_*` et `mouvement_or_5j`."""
    df = series_asof(ticker, as_of, lookback_days=window + 30)
    if df is None or len(df) < 10:
        return None
    closes = [float(c) for c in df["Close"].tolist()]
    perfs = [closes[i] / closes[i - 5] - 1.0 for i in range(5, len(closes)) if closes[i - 5] != 0]
    if len(perfs) < 5:
        return None
    hist = perfs[-window:] if len(perfs) >= window else perfs
    res = zscore_from_series(hist, zscore_div=zscore_div, cap=cap)
    if res is None:
        return None
    return {"valeur": res[0], "valeur_normalisee": res[1]}


def quant_ratio_zscore(ticker_a: str, ticker_b: str, as_of, *, window: int = 60,
                       zscore_div: float = 2.0, cap: float = 1.0) -> Optional[Dict[str, float]]:
    """Ratio A/B → z-score. Mime `_twelve_ratio_zscore` (live)."""
    df_a = series_asof(ticker_a, as_of, lookback_days=window + 30)
    df_b = series_asof(ticker_b, as_of, lookback_days=window + 30)
    if df_a is None or df_b is None:
        return None
    dates_b = {d.date(): float(c) for d, c in zip(df_b.index, df_b["Close"])}
    pairs = []
    for d, c in zip(df_a.index, df_a["Close"]):
        b = dates_b.get(d.date())
        if b is None or b == 0:
            continue
        pairs.append(float(c) / b)
    if len(pairs) < max(10, window // 4):
        return None
    hist = pairs[-window:] if len(pairs) >= window else pairs
    res = zscore_from_series(hist, zscore_div=zscore_div, cap=cap)
    if res is None:
        return None
    return {"valeur": res[0], "valeur_normalisee": res[1]}


def quant_spread_zscore(ticker_a: str, ticker_b: str, as_of, *, window: int = 60,
                        zscore_div: float = 2.0, cap: float = 1.0) -> Optional[Dict[str, float]]:
    """Spread A - B → z-score. Mime `_twelve_spread_zscore` (live)."""
    df_a = series_asof(ticker_a, as_of, lookback_days=window + 30)
    df_b = series_asof(ticker_b, as_of, lookback_days=window + 30)
    if df_a is None or df_b is None:
        return None
    dates_b = {d.date(): float(c) for d, c in zip(df_b.index, df_b["Close"])}
    pairs = []
    for d, c in zip(df_a.index, df_a["Close"]):
        b = dates_b.get(d.date())
        if b is None:
            continue
        pairs.append(float(c) - b)
    if len(pairs) < max(10, window // 4):
        return None
    hist = pairs[-window:] if len(pairs) >= window else pairs
    res = zscore_from_series(hist, zscore_div=zscore_div, cap=cap)
    if res is None:
        return None
    return {"valeur": res[0], "valeur_normalisee": res[1]}


def quant_alpha_5j_zscore(ticker_a: str, ticker_b: str, as_of, *, window: int = 60,
                          zscore_div: float = 2.0, cap: float = 1.0) -> Optional[Dict[str, float]]:
    """Alpha 5j = perf(A,5j) - perf(B,5j), z-score sur fenêtre."""
    df_a = series_asof(ticker_a, as_of, lookback_days=window + 30)
    df_b = series_asof(ticker_b, as_of, lookback_days=window + 30)
    if df_a is None or df_b is None:
        return None
    dates_b = {d.date(): float(c) for d, c in zip(df_b.index, df_b["Close"])}
    aligned = []
    for d, c in zip(df_a.index, df_a["Close"]):
        if d.date() in dates_b:
            aligned.append((d.date(), float(c), dates_b[d.date()]))
    if len(aligned) < 10:
        return None
    alphas: List[float] = []
    for i in range(5, len(aligned)):
        ca0 = aligned[i - 5][1]; ca1 = aligned[i][1]
        cb0 = aligned[i - 5][2]; cb1 = aligned[i][2]
        if ca0 == 0 or cb0 == 0:
            continue
        alphas.append((ca1 / ca0 - 1.0) - (cb1 / cb0 - 1.0))
    if len(alphas) < 5:
        return None
    hist = alphas[-window:] if len(alphas) >= window else alphas
    res = zscore_from_series(hist, zscore_div=zscore_div, cap=cap)
    if res is None:
        return None
    return {"valeur": res[0], "valeur_normalisee": res[1]}


# ---------------------------------------------------------------------------
# Mapping cle_courante → builder (basé sur TWELVE_SYMBOLS du live)
# ---------------------------------------------------------------------------

# Pour chaque clé courante listée dans les fiches, on mappe vers un builder
# QUANT historique (ou None si non-câblable en v1).
#
# Conventions :
# - Symbole simple : on appelle quant_zscore_single (z-score sur closes)
# - Tuple (RSI, ticker) : on calcule RSI 14j
# - Tuple (A, B) avec cle commençant par "spread_" : spread_zscore
# - Tuple (A, B) avec "ratio_" : ratio_zscore
# - Tuple (A, B) avec "alpha_" : alpha_5j_zscore
# - "mouvement_or_5j" et "flux_etf_*" : perf 5j → z-score
# - GATE : toujours désactivé (False) en backtest historique (zéro news)
# - Triplets / lineaires non-quant / composites : None → n/a

QUANT_SYMBOLS: Dict[str, Any] = {
    # --- Trend / risk-off ---
    # dxy_trend_20j, taux_10y_us_reels_tips, taux_10y_us_delta_5j, hy_credit_spread
    # sont désormais câblés sur FRED (cf. build_quant_value) — PLUS de proxies ETF
    # (le proxy TIP était INVERSÉ en v1, bug corrigé via DFII10 direct).
    "vix_risk_off_proxy":    "^VIX",
    "niveau_vix_absolu":     "^VIX",
    "vix_regime":            "^VIX",          # mapping_non_monotone → traité spécifiquement
    "vxn_regime":            "^VXN",
    "vvix":                  "^VVIX",
    "skew_index_cboe":       "^SKEW",
    "sox_trend_5j":          "SOXX",
    # --- Term structure VIX ---
    "term_structure_vix_vix3m": ("^VIX3M", "^VIX"),
    # --- FX ---
    "usd_brl":               "USDBRL=X",
    "usd_jpy_proxy_risk":    "USDJPY=X",
    # --- Spreads commodities ---
    "spread_brent_wti":      ("BZ=F", "CL=F"),
    "spread_nasdaq_russell2000": ("^IXIC", "^RUT"),
    # --- Ratios ---
    "ratio_gold_silver":     ("GC=F", "SI=F"),
    "ratio_cuivre_or":       ("HG=F", "GC=F"),
    # --- Alpha ---
    "alpha_argent_vs_or_5j": ("SI=F", "GC=F"),
    "alpha_cac_vs_sp_5j":    ("^FCHI", "^GSPC"),
    # --- RSI ---
    "rsi_14j_gspc":          ("RSI", "^GSPC"),
    "rsi_14j_ixic":          ("RSI", "^IXIC"),
    "rsi_14j_fchi":          ("RSI", "^FCHI"),
    # --- Trend perf 5j ---
    "mouvement_or_5j":       "GC=F",
    "flux_etf_or_5j":        "GLD",
    "flux_etf_qqq_5j":       "QQQ",
    "flux_etf_spy_ivv_5j":   "SPY",
    "flux_etf_slv_pslv_5j":  "SLV",
    "flux_etf_msci_france_5j": "EWQ",
}


def build_macro_value(cle: str, crit: dict, as_of) -> Optional[Dict[str, float]]:
    """Câble les critères FRED + CFTC COT, AS OF `as_of` (no look-ahead).

    Réutilise les mappings ET formules LIVE (FRED_SERIES_SIMPLE/SPREADS/DELTA,
    CFTC_MARKETS, zscore_from_series, compute_zscore_normalisee). Renvoie
    {valeur, valeur_normalisee} ou None (n/a propre)."""
    zscore_div = float(crit.get("zscore_div", 2.0))
    cap = float(crit.get("cap", 1.0))

    # --- FRED série simple (DFII10, BAMLH0A0HYM2, DTWEXBGS) ---
    if cle in FRED_SERIES_SIMPLE:
        window = int(crit.get("zscore_window", 252))
        sid = FRED_SERIES_SIMPLE[cle]
        series = fred_series_asof(sid, as_of, lookback_days=max(window + 30, 400))
        if not series or len(series) < 10:
            return None
        value = series[-1]
        hist = series[-window:] if len(series) >= window else series
        norm = compute_zscore_normalisee(value, hist, zscore_div=zscore_div, cap=cap, label=cle)
        if norm is None:
            return None
        return {"valeur": float(value), "valeur_normalisee": norm}

    # --- FRED spread US-DE (DGS10-Bund, OAT-Bund) ---
    if cle in FRED_SPREADS:
        window = int(crit.get("zscore_window", 252))
        sus, sde = FRED_SPREADS[cle]
        # lookback large : la série DE mensuelle a besoin de profondeur pour le LOCF
        series = fred_spread_asof(sus, sde, as_of, lookback_days=max(window * 2 + 60, 600))
        if not series or len(series) < 10:
            return None
        value = series[-1]
        hist = series[-window:] if len(series) >= window else series
        norm = compute_zscore_normalisee(value, hist, zscore_div=zscore_div, cap=cap, label=cle)
        if norm is None:
            return None
        return {"valeur": float(value), "valeur_normalisee": norm}

    # --- FRED delta N jours (DGS10 delta 5j) ---
    if cle in FRED_DELTA:
        window = int(crit.get("zscore_window", 60))
        series_id, n_days = FRED_DELTA[cle]
        deltas = fred_delta_asof(series_id, as_of, n_days=n_days,
                                 lookback_days=max(window + n_days + 30, 400))
        if not deltas:
            return None
        hist = deltas[-window:] if len(deltas) >= window else deltas
        res = zscore_from_series(hist, zscore_div=zscore_div, cap=cap, label=cle)
        if res is None:
            return None
        return {"valeur": res[0], "valeur_normalisee": res[1]}

    # --- CFTC COT noncomm nets z-score ---
    if cle in CFTC_MARKETS:
        window = int(crit.get("zscore_window", 252))
        market = CFTC_MARKETS[cle]
        nets = cot_nets_asof(market, as_of, lookback_days=max((window + 20) * 7, 1900))
        if not nets or len(nets) < 20:
            return None
        value = nets[-1]
        hist = nets[-window:] if len(nets) >= window else nets
        norm = compute_zscore_normalisee(value, hist, zscore_div=zscore_div, cap=cap, label=cle)
        if norm is None:
            return None
        return {"valeur": float(value), "valeur_normalisee": norm}

    return None


# Filtre d'ablation : restreint les critères câblés à un sous-groupe.
# None = tous (comportement normal). Sinon un set de groupes parmi
# {"price", "fred", "cot"}. Utilisé par run_ablation.
_ABLATION_GROUPS: Optional[set] = None


def criterion_group(cle: str) -> str:
    """Classe un critère dans un grand groupe pour l'ablation."""
    if cle in CFTC_MARKETS:
        return "cot"
    if cle in FRED_SERIES_SIMPLE or cle in FRED_SPREADS or cle in FRED_DELTA:
        return "fred"
    return "price"


def build_quant_value(cle: str, crit: dict, as_of) -> Optional[Any]:
    """Construit la valeur historique pour un critère, AS OF `as_of`.

    Retourne :
    - un dict {valeur, valeur_normalisee} pour les z-scores
    - un dict {valeur} pour les linéaires (le scoring fera centre/echelle)
    - None si non-câblable (le scoring marquera n/a, poids 0)
    """
    type_norm = crit.get("normalisation", "")

    # GATE : on désactive systématiquement en backtest historique
    if type_norm == "gate":
        return {"valeur": False}

    # Triplet : non câblable en historique (vient de classification d'events news)
    # → on retourne None (n/a, poids 0)
    if type_norm == "triplet":
        return None

    # Ablation : si un sous-groupe est imposé, on masque les critères hors groupe.
    if _ABLATION_GROUPS is not None and criterion_group(cle) not in _ABLATION_GROUPS:
        return None

    # Macro FRED/COT (câblé v2) — prioritaire sur QUANT_SYMBOLS
    macro = build_macro_value(cle, crit, as_of)
    if macro is not None:
        return macro

    spec = QUANT_SYMBOLS.get(cle)
    if spec is None:
        # Critère non quant-mappable (COT, FRED, météo, breadth, news, composites...) → n/a
        return None

    window = int(crit.get("zscore_window", 60))
    zscore_div = float(crit.get("zscore_div", 2.0))
    cap = float(crit.get("cap", 1.0))

    # RSI : retourne valeur brute (le scoring fait centre/echelle si lineaire,
    # ou retournera n/a si type=zscore — ce qu'on évite ici en sortant lineaire)
    if isinstance(spec, tuple) and spec[0] == "RSI":
        rsi = quant_rsi(spec[1], as_of)
        if rsi is None:
            return None
        return {"valeur": rsi}

    # Mapping non-monotone (vix_regime) : on récupère la close brute du VIX
    if type_norm == "mapping_non_monotone":
        df = series_asof(spec if isinstance(spec, str) else spec[0], as_of, lookback_days=10)
        if df is None or len(df) == 0:
            return None
        price = float(df["Close"].iloc[-1])
        cap_loc = cap
        low = float(crit.get("low", 14.0))
        high = float(crit.get("high", 25.0))
        # Réutilise la formule live
        from criteres_calculator import _mapping_non_monotone_vix
        norm = _mapping_non_monotone_vix(price, low=low, high=high, cap=cap_loc)
        return {"valeur": price, "valeur_normalisee": norm}

    # Symbole simple
    if isinstance(spec, str):
        # perf 5j (flux ETF, mouvement_or)
        if cle == "mouvement_or_5j" or cle.startswith("flux_etf_"):
            return quant_perf_5j_zscore(spec, as_of, window=window,
                                        zscore_div=zscore_div, cap=cap)
        # Linéaire : on retourne juste la close brute, le scoring fait centre/echelle
        if type_norm == "lineaire":
            df = series_asof(spec, as_of, lookback_days=10)
            if df is None or len(df) == 0:
                return None
            return {"valeur": float(df["Close"].iloc[-1])}
        # Sinon : z-score sur closes
        return quant_zscore_single(spec, as_of, window=window,
                                   zscore_div=zscore_div, cap=cap)

    # Tuple (A, B) : spread / ratio / alpha
    sym_a, sym_b = spec
    if cle.startswith("spread_") or cle.startswith("differentiel_"):
        return quant_spread_zscore(sym_a, sym_b, as_of, window=window,
                                   zscore_div=zscore_div, cap=cap)
    if cle.startswith("ratio_"):
        return quant_ratio_zscore(sym_a, sym_b, as_of, window=window,
                                  zscore_div=zscore_div, cap=cap)
    if cle.startswith("alpha_"):
        return quant_alpha_5j_zscore(sym_a, sym_b, as_of, window=window,
                                     zscore_div=zscore_div, cap=cap)
    if cle == "term_structure_vix_vix3m":
        # Ratio VIX/VIX3M, sortie linéaire (le scoring applique centre/echelle)
        df_a = series_asof(sym_a, as_of, lookback_days=10)
        df_b = series_asof(sym_b, as_of, lookback_days=10)
        if df_a is None or df_b is None or len(df_a) == 0 or len(df_b) == 0:
            return None
        a = float(df_a["Close"].iloc[-1])
        b = float(df_b["Close"].iloc[-1])
        if b == 0:
            return None
        return {"valeur": a / b}
    return None


def build_valeurs_actif_asof(fiche: dict, as_of) -> dict:
    """Construit le dict `valeurs_actif` (format attendu par `score_actif`) à
    une date historique, en utilisant UNIQUEMENT des données antérieures."""
    out: Dict[str, Any] = {}
    for crit in fiche.get("criteres", []):
        cle = crit.get("cle_courante")
        if not cle:
            continue
        val = build_quant_value(cle, crit, as_of)
        if val is not None:
            out[cle] = val
    return out


# ---------------------------------------------------------------------------
# Métriques statistiques
# ---------------------------------------------------------------------------

def wilson_interval(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """IC Wilson 95% pour une proportion k/n."""
    if n == 0:
        return (0.0, 1.0)
    # z = 1.96 pour alpha=0.05
    z = 1.959963984540054
    p_hat = k / n
    denom = 1 + z**2 / n
    centre = p_hat + z**2 / (2 * n)
    half = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n)
    low = (centre - half) / denom
    high = (centre + half) / denom
    return max(0.0, low), min(1.0, high)


def permutation_pvalue(predictions: List[str], outcomes_signed: List[float],
                       seuil: float, n_iter: int = 1000, seed: int = 42) -> float:
    """p-value bootstrap par permutation. H0 = pas de lien pred→outcome.

    `predictions` : liste de "LONG"/"SHORT".
    `outcomes_signed` : rendement forward (>0 hausse, <0 baisse).
    `seuil` : seuil d'amplitude en pourcent (ex: 0.5 pour 0.5%).

    Retourne la probabilité d'obtenir, sous permutation aléatoire, une
    accuracy ≥ celle observée. Si p < 0.05 → on rejette H0.
    """
    rnd = random.Random(seed)
    n = len(predictions)
    if n == 0:
        return 1.0
    seuil_frac = seuil / 100.0

    def _accuracy(preds: List[str]) -> Optional[float]:
        k_true = k_false = 0
        for p, r in zip(preds, outcomes_signed):
            if abs(r) < seuil_frac:
                continue  # non-conclusive
            correct = (p == "LONG" and r > 0) or (p == "SHORT" and r < 0)
            if correct:
                k_true += 1
            else:
                k_false += 1
        denom = k_true + k_false
        if denom == 0:
            return None
        return k_true / denom

    observed = _accuracy(predictions)
    if observed is None:
        return 1.0
    ge_count = 0
    total = 0
    for _ in range(n_iter):
        shuffled = predictions[:]
        rnd.shuffle(shuffled)
        acc = _accuracy(shuffled)
        if acc is None:
            continue
        total += 1
        if acc >= observed:
            ge_count += 1
    if total == 0:
        return 1.0
    return ge_count / total


# ---------------------------------------------------------------------------
# Moteur de backtest principal
# ---------------------------------------------------------------------------

class BacktestNoDataError(RuntimeError):
    """Levée quand 0 date n'a été testée sur AUCUNE cellule.

    Garde-fou « échec visible » : un run qui ne teste aucune date (cache
    introuvable, fenêtre vide) ne doit jamais finir en success."""


@dataclass
class TradeResult:
    ticker: str
    fiche_key: str
    date: "date"
    horizon_days: int
    horizon_label: str
    score: float
    prediction: str           # LONG / SHORT
    return_pct: float         # rendement forward signé (ex: 0.005 = +0.5%)
    seuil_pct: float          # seuil amplitude de la fiche (ex: 0.5)
    outcome: str              # "VRAI" | "FAUSSE" | "non-conclusive"


@dataclass
class CellResults:
    ticker: str
    horizon_label: str
    trades_is: List[TradeResult] = field(default_factory=list)
    trades_oos: List[TradeResult] = field(default_factory=list)
    # Nb de dates effectivement itérées (IS+OOS), indépendant du fait qu'un trade
    # ait été retenu. Sert au garde-fou « 0 date testée = échec visible ».
    n_dates_tested: int = 0


def classify_outcome(prediction: str, return_pct: float, seuil_pct: float) -> str:
    """Classification VRAI/FAUSSE/non-conclusive selon seuils_reussite_pct."""
    if abs(return_pct) < seuil_pct / 100.0:
        return "non-conclusive"
    if prediction == "LONG":
        return "VRAI" if return_pct > 0 else "FAUSSE"
    if prediction == "SHORT":
        return "VRAI" if return_pct < 0 else "FAUSSE"
    return "non-conclusive"


def run_backtest_cell(
    ticker: str,
    horizon_label: str = "24h",
    horizon_days: int = 1,
    is_start: str = "2021-01-01",
    is_end: str = "2024-12-31",
    oos_start: str = "2025-01-01",
    oos_end: Optional[str] = None,
    warmup_skip_days: int = 252,
) -> CellResults:
    """Backtest pour une cellule (ticker × horizon).

    Walk-forward :
    - IS : dates dans [is_start, is_end]
    - OOS : dates dans [oos_start, oos_end] (par défaut, jusqu'à aujourd'hui)
    """
    fiche_key = TICKER_TO_FICHE.get(ticker)
    if not fiche_key:
        raise ValueError(f"ticker {ticker} non mappé dans TICKER_TO_FICHE")
    fiches = load_fiches()
    fiche = fiches.get(fiche_key)
    if not fiche:
        raise ValueError(f"fiche {fiche_key} introuvable")
    seuil_pct = float(fiche.get("seuils_reussite_pct", {}).get(horizon_label, 0.5))

    oos_end = oos_end or date.today().isoformat()
    results = CellResults(ticker=ticker, horizon_label=horizon_label)

    # Skip les `warmup_skip_days` premiers jours (le z-score 252j a besoin de warmup)
    effective_is_start = (_to_date(is_start) + timedelta(days=warmup_skip_days)).isoformat()

    for label, d_start, d_end, bucket in [
        ("IS",  effective_is_start, is_end, results.trades_is),
        ("OOS", oos_start, oos_end, results.trades_oos),
    ]:
        dates = non_overlapping_trading_dates(ticker, d_start, d_end, horizon_days=horizon_days)
        logger.info("Cell %s/%s [%s] : %d dates à tester", ticker, horizon_label, label, len(dates))
        results.n_dates_tested += len(dates)
        for i, d in enumerate(dates):
            # 1. Construit les features AS OF d (no look-ahead)
            valeurs = build_valeurs_actif_asof(fiche, d)
            # 2. Calcule scores avec le moteur LIVE (réutilisé tel quel)
            actif_res = score_actif(fiche_key, fiche, valeurs)
            score = actif_res.scores.get(horizon_label, 0.0)
            concl = actif_res.conclusions.get(horizon_label)
            if concl not in ("LONG", "SHORT"):
                # Tie-break a forcé LONG par défaut quand aucun critère actif
                concl = "LONG" if score >= 0 else "SHORT"
            # 3. Mesure outcome forward (utilise close future — légitime, c'est la mesure)
            ret = future_return(ticker, d, horizon_days=horizon_days)
            if ret is None:
                continue
            outcome = classify_outcome(concl, ret, seuil_pct)
            bucket.append(TradeResult(
                ticker=ticker, fiche_key=fiche_key, date=d,
                horizon_days=horizon_days, horizon_label=horizon_label,
                score=score, prediction=concl,
                return_pct=ret, seuil_pct=seuil_pct, outcome=outcome,
            ))
            if (i + 1) % 100 == 0:
                logger.info("  %s/%s [%s] : %d/%d", ticker, horizon_label, label, i + 1, len(dates))

    return results


def summarize_trades(trades: List[TradeResult]) -> Dict[str, Any]:
    """Calcule métriques sur une liste de trades : N_total, N_conclusive,
    accuracy, Wilson_low, p-value permutation, ratio LONG, distribution."""
    n_total = len(trades)
    concl = [t for t in trades if t.outcome != "non-conclusive"]
    n_concl = len(concl)
    k_true = sum(1 for t in concl if t.outcome == "VRAI")
    k_false = n_concl - k_true
    accuracy = (k_true / n_concl) if n_concl > 0 else None
    wilson_low, wilson_high = wilson_interval(k_true, n_concl) if n_concl > 0 else (None, None)
    longs = sum(1 for t in trades if t.prediction == "LONG")
    long_ratio = (longs / n_total) if n_total > 0 else None
    non_concl_rate = ((n_total - n_concl) / n_total) if n_total > 0 else None
    p_value = None
    if n_total >= 10:
        preds = [t.prediction for t in trades]
        rets = [t.return_pct for t in trades]
        seuil = trades[0].seuil_pct
        p_value = permutation_pvalue(preds, rets, seuil, n_iter=1000)
    return {
        "n_total": n_total,
        "n_conclusive": n_concl,
        "non_conclusive_rate": non_concl_rate,
        "k_true": k_true,
        "k_false": k_false,
        "accuracy": accuracy,
        "wilson_low": wilson_low,
        "wilson_high": wilson_high,
        "long_ratio": long_ratio,
        "p_value": p_value,
    }


def verdict(metrics_oos: Dict[str, Any]) -> str:
    """Verdict GO/NO-GO selon les seuils audit-reel-et-backtest-scope §2.4."""
    acc = metrics_oos.get("accuracy")
    wl = metrics_oos.get("wilson_low")
    p = metrics_oos.get("p_value")
    if acc is None or wl is None or p is None:
        return "INSUFFISANT (N_eff trop faible)"
    if acc >= 0.60 and wl >= 0.55 and p < 0.05:
        return "GO"
    if acc < 0.55 or wl < 0.50 or p > 0.10:
        return "NO-GO"
    return "BORDERLINE"


# ---------------------------------------------------------------------------
# Main — exécution backtest sur les 4 actifs v1
# ---------------------------------------------------------------------------

def fmt_pct(x: Optional[float], digits: int = 1) -> str:
    if x is None:
        return "  n/a "
    return f"{x*100:>5.{digits}f}%"


def fmt_n(x: Optional[Any]) -> str:
    if x is None:
        return " n/a "
    return f"{x:>5}"


def fmt_p(x: Optional[float]) -> str:
    if x is None:
        return "  n/a "
    return f"{x:.3f}"


def print_cell_summary(ticker: str, fiche_key: str, horizon: str, label: str,
                       m: Dict[str, Any]) -> None:
    print(f"  {label:<3} | N_total={fmt_n(m['n_total'])} | "
          f"N_concl={fmt_n(m['n_conclusive'])} | "
          f"NC_rate={fmt_pct(m['non_conclusive_rate'])} | "
          f"acc={fmt_pct(m['accuracy'])} | "
          f"WL={fmt_pct(m['wilson_low'])} | "
          f"p={fmt_p(m['p_value'])} | "
          f"long%={fmt_pct(m['long_ratio'])}")


def run_ablation(tickers: List[str], horizons: List[Tuple[str, int]]) -> None:
    """Étude d'ablation : recalcule l'accuracy pooled OOS en activant
    progressivement les groupes de critères (price-only / +FRED / +COT / tous).

    Montre quel groupe porte (ou non) l'edge. Léger : pooled global uniquement.
    Modifie le filtre module-level `_ABLATION_GROUPS` puis le restaure."""
    global _ABLATION_GROUPS
    scenarios = [
        ("price-only", {"price"}),
        ("+FRED",      {"price", "fred"}),
        ("+COT",       {"price", "cot"}),
        ("tous",       {"price", "fred", "cot"}),
    ]
    print("\n" + "=" * 100)
    print("ÉTUDE D'ABLATION — pooled OOS par groupe de critères")
    print("=" * 100)
    print(f"{'Scénario':<14} {'N_concl':>8} {'acc':>8} {'WL':>8} {'p-val':>8}")
    print("-" * 100)
    saved = _ABLATION_GROUPS
    try:
        for name, groups in scenarios:
            _ABLATION_GROUPS = groups
            kt = kf = 0
            all_preds: List[str] = []
            all_rets: List[float] = []
            seuil_ref = 0.5
            for ticker in tickers:
                for h_lbl, h_days in horizons:
                    try:
                        cell = run_backtest_cell(
                            ticker, horizon_label=h_lbl, horizon_days=h_days,
                            is_start="2021-01-01", is_end="2024-12-31",
                            oos_start="2025-01-01", oos_end=None,
                            warmup_skip_days=300,
                        )
                    except Exception:  # noqa: BLE001
                        continue
                    for t in cell.trades_oos:
                        all_preds.append(t.prediction)
                        all_rets.append(t.return_pct)
                        seuil_ref = t.seuil_pct
                        if t.outcome == "VRAI":
                            kt += 1
                        elif t.outcome == "FAUSSE":
                            kf += 1
            n = kt + kf
            acc = (kt / n) if n else None
            wl, _ = wilson_interval(kt, n) if n else (None, None)
            p = permutation_pvalue(all_preds, all_rets, seuil_ref, n_iter=500) if all_preds else None
            print(f"{name:<14} {fmt_n(n):>8} {fmt_pct(acc):>8} {fmt_pct(wl):>8} {fmt_p(p):>8}")
    finally:
        _ABLATION_GROUPS = saved


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    warnings.filterwarnings("ignore")

    # 12 actifs distincts (1 ticker par fiche). BZ=F et CL=F mappent tous deux
    # sur la fiche "petrole" → on garde CL=F (WTI, historique yfinance propre,
    # cohérent avec v1) et on écarte BZ=F pour ne pas double-compter le pétrole.
    tickers_raw = TICKERS_V1 + TICKERS_V2_EXTENSION
    tickers = []
    seen_fiches = set()
    for tk in tickers_raw:
        fk = TICKER_TO_FICHE.get(tk)
        if not fk or fk in seen_fiches:
            continue
        seen_fiches.add(fk)
        tickers.append(tk)
    # Mapping jours = celui du LIVE (journaliste.HORIZON_DAYS = 24h:1, 7j:7, 1m:30
    # jours CALENDAIRES, vérifié — le live mesure l'échéance en jours calendaires,
    # pas en jours de trading). On reste strictement aligné.
    horizons = [("24h", 1), ("7j", 7), ("1m", 30)]

    all_oos_metrics: Dict[str, Dict[str, Any]] = {}
    all_is_metrics: Dict[str, Dict[str, Any]] = {}
    all_cells: Dict[str, CellResults] = {}

    print("\n" + "=" * 100)
    print(f"BACKTEST QUANT v2 — {len(tickers)} actifs × {len(horizons)} horizons "
          f"({', '.join(h for h, _ in horizons)}), walk-forward IS 2021-2024 / OOS 2025+")
    print("=" * 100)

    for ticker in tickers:
        for horizon_label, horizon_days in horizons:
            fiche_key = TICKER_TO_FICHE[ticker]
            print(f"\n>>> {ticker} ({fiche_key}) — horizon {horizon_label}")
            try:
                cell = run_backtest_cell(
                    ticker, horizon_label=horizon_label, horizon_days=horizon_days,
                    is_start="2021-01-01", is_end="2024-12-31",
                    oos_start="2025-01-01", oos_end=None,
                    warmup_skip_days=300,
                )
            except Exception as e:
                logger.exception("ERROR sur %s : %s", ticker, e)
                continue
            all_cells[f"{ticker}|{horizon_label}"] = cell
            m_is = summarize_trades(cell.trades_is)
            m_oos = summarize_trades(cell.trades_oos)
            all_is_metrics[f"{ticker}|{horizon_label}"] = m_is
            all_oos_metrics[f"{ticker}|{horizon_label}"] = m_oos
            print_cell_summary(ticker, fiche_key, horizon_label, "IS ", m_is)
            print_cell_summary(ticker, fiche_key, horizon_label, "OOS", m_oos)
            v = verdict(m_oos)
            print(f"  VERDICT cellule : {v}")

    # ------------------------------------------------------------------
    # Garde-fou « échec visible » contre le faux vert (règle projet).
    # Si AUCUNE cellule n'a testé la moindre date (IS+OOS confondus), le run
    # ne doit PAS finir en success : cache introuvable ou fenêtre vide, et
    # surtout FRED/COT jamais exercés. Cf. run #1 backtest-v2-fred (0 dates
    # partout, aucun fred__ généré → faux vert).
    # ------------------------------------------------------------------
    total_dates_tested = sum(c.n_dates_tested for c in all_cells.values())
    if total_dates_tested == 0:
        raise BacktestNoDataError(
            "0 date testée sur toutes les cellules — cache introuvable ou "
            "fenêtre vide, FRED non exercé. Vérifier v3/backtest/.cache/ "
            "(fichiers prix présents ? plage couvrant la fenêtre demandée ?)."
        )

    # Agrégat OOS détaillé
    print("\n" + "=" * 100)
    print("AGRÉGAT OOS — par cellule")
    print("=" * 100)
    print(f"{'Cellule':<22} {'N_concl':>8} {'acc':>8} {'WL':>8} {'p-val':>8} {'verdict':>12}")
    print("-" * 100)
    total_true = total_false = 0
    pooled_by_h: Dict[str, List[int]] = {h: [0, 0] for h, _ in horizons}
    for key, m in all_oos_metrics.items():
        v = verdict(m)
        h_lbl = key.split("|")[1]
        if m["k_true"] is not None:
            total_true += m["k_true"]
            total_false += m["k_false"]
            pooled_by_h[h_lbl][0] += m["k_true"]
            pooled_by_h[h_lbl][1] += m["k_false"]
        print(f"{key:<22} {fmt_n(m['n_conclusive']):>8} "
              f"{fmt_pct(m['accuracy']):>8} {fmt_pct(m['wilson_low']):>8} "
              f"{fmt_p(m['p_value']):>8} {v:>12}")

    # Pooled par horizon + global
    print("\n" + "=" * 100)
    print("POOLED OOS — par horizon (tous actifs)")
    print("=" * 100)
    print(f"{'Horizon':<22} {'N_concl':>8} {'acc':>8} {'WL':>8}")
    print("-" * 100)
    for h_lbl, _ in horizons:
        kt, kf = pooled_by_h[h_lbl]
        n = kt + kf
        if n == 0:
            continue
        acc = kt / n
        wl, _ = wilson_interval(kt, n)
        print(f"{('POOLED ' + h_lbl):<22} {fmt_n(n):>8} {fmt_pct(acc):>8} {fmt_pct(wl):>8}")
    n_pool = total_true + total_false
    if n_pool > 0:
        pool_acc = total_true / n_pool
        pool_wl, _ = wilson_interval(total_true, n_pool)
        print("-" * 100)
        print(f"{'POOLED GLOBAL':<22} {fmt_n(n_pool):>8} "
              f"{fmt_pct(pool_acc):>8} {fmt_pct(pool_wl):>8}")

    # Étude d'ablation par groupe de critères
    run_ablation(tickers, horizons)

    return all_cells, all_is_metrics, all_oos_metrics


if __name__ == "__main__":
    try:
        main()
    except BacktestNoDataError as e:
        logger.error("ÉCHEC BACKTEST : %s", e)
        sys.exit(1)
