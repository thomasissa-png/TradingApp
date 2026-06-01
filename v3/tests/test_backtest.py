"""Tests du moteur de backtest QUANT (v3/backtest/).

Vérifie :
1. No look-ahead garanti par `series_asof` (point critique du protocole)
2. Calcul correct accuracy / Wilson_low / outcome
3. Permutation pvalue cohérente sur cas jouet
4. Intégration avec les formules live (`scoring_analyste.normalise` retourne
   pareil sur valeurs construites par le backtest)
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backtest"))
sys.path.insert(0, str(ROOT / "scripts"))


# ---------------------------------------------------------------------------
# 1. No look-ahead (critère LE PLUS critique)
# ---------------------------------------------------------------------------

def test_series_asof_strict_no_lookahead():
    """series_asof('GC=F', d) ne doit JAMAIS retourner de barre datée >= d."""
    from historical_data import series_asof, _to_date

    for test_d_str in ("2024-01-15", "2024-06-15", "2024-11-04", "2025-03-10"):
        test_d = _to_date(test_d_str)
        df = series_asof("GC=F", test_d, lookback_days=400)
        if df is None:
            pytest.skip(f"yfinance indispo pour {test_d_str}")
        assert len(df) > 0
        last_idx_date = df.index[-1].date()
        assert last_idx_date < test_d, (
            f"VIOLATION look-ahead : last={last_idx_date}, asof={test_d}"
        )


def test_series_asof_no_lookahead_on_trading_day():
    """Même test sur un JOUR DE TRADING (pas un weekend) — cas piège."""
    from historical_data import series_asof, _to_date, _get_full_df

    df_full = _get_full_df("GC=F")
    if df_full is None or len(df_full) == 0:
        pytest.skip("yfinance indispo")
    # Prendre une date qui est explicitement un jour de trading
    trading_day = df_full.index[-100].date()
    df = series_asof("GC=F", trading_day, lookback_days=200)
    assert df is not None
    # La close de trading_day NE doit PAS apparaître dans le résultat
    assert all(d.date() < trading_day for d in df.index), (
        f"Bar du jour {trading_day} fuite dans series_asof !"
    )


# ---------------------------------------------------------------------------
# 2. Classification outcome
# ---------------------------------------------------------------------------

def test_classify_outcome_vrai_long():
    from backtest_quant import classify_outcome
    # LONG, rendement +1.5%, seuil 0.5% → VRAI
    assert classify_outcome("LONG", 0.015, 0.5) == "VRAI"


def test_classify_outcome_fausse_short():
    from backtest_quant import classify_outcome
    # SHORT, rendement +1.5%, seuil 0.5% → FAUSSE
    assert classify_outcome("SHORT", 0.015, 0.5) == "FAUSSE"


def test_classify_outcome_non_conclusive():
    from backtest_quant import classify_outcome
    # Mouvement de 0.2% sur seuil 0.5% → non-conclusive
    assert classify_outcome("LONG", 0.002, 0.5) == "non-conclusive"
    assert classify_outcome("SHORT", -0.001, 0.5) == "non-conclusive"


def test_classify_outcome_vrai_short():
    from backtest_quant import classify_outcome
    # SHORT, rendement -2%, seuil 0.5% → VRAI
    assert classify_outcome("SHORT", -0.02, 0.5) == "VRAI"


# ---------------------------------------------------------------------------
# 3. Wilson interval
# ---------------------------------------------------------------------------

def test_wilson_interval_n1_k1():
    """N=1, k=1 → IC [0.206, 1.0] (référence audit)."""
    from backtest_quant import wilson_interval
    low, high = wilson_interval(1, 1)
    assert 0.19 < low < 0.22
    assert high == pytest.approx(1.0, abs=0.001)


def test_wilson_interval_n10_k10():
    """N=10, k=10 → low ≈ 0.722 (Wilson standard sans correction de continuité).
    NB : la table de l'audit (0.697) utilise une variante (Wilson CC). On reste
    sur la formule Wilson classique, plus largement répandue et reproductible.
    """
    from backtest_quant import wilson_interval
    low, high = wilson_interval(10, 10)
    assert 0.70 < low < 0.74
    assert high == pytest.approx(1.0, abs=0.01)


def test_wilson_interval_n30_k21():
    """N=30, k=21 (70%) → low > 0.50 (zone éligibilité)."""
    from backtest_quant import wilson_interval
    low, _ = wilson_interval(21, 30)
    assert low > 0.50


def test_wilson_interval_n0():
    from backtest_quant import wilson_interval
    low, high = wilson_interval(0, 0)
    assert low == 0.0 and high == 1.0


# ---------------------------------------------------------------------------
# 4. Permutation p-value sur cas jouet
# ---------------------------------------------------------------------------

def test_permutation_pvalue_no_signal():
    """Predictions aléatoires + outcomes aléatoires → p-value haute (pas de signal)."""
    from backtest_quant import permutation_pvalue
    import random
    rnd = random.Random(0)
    preds = ["LONG" if rnd.random() < 0.5 else "SHORT" for _ in range(200)]
    rets = [rnd.gauss(0, 0.01) for _ in range(200)]
    p = permutation_pvalue(preds, rets, seuil=0.3, n_iter=500)
    # Pas de signal réel → p doit être loin de 0
    assert p > 0.10, f"p={p} (attendu >0.10 sans signal)"


def test_permutation_pvalue_strong_signal():
    """Predictions parfaitement corrélées aux outcomes → p-value très basse."""
    from backtest_quant import permutation_pvalue
    # 100 prédictions LONG avec rendement positif, 100 SHORT avec rendement négatif
    preds = ["LONG"] * 100 + ["SHORT"] * 100
    rets = [0.02] * 100 + [-0.02] * 100   # toutes au-dessus du seuil 0.5%
    p = permutation_pvalue(preds, rets, seuil=0.5, n_iter=500)
    assert p < 0.01, f"p={p} (attendu <0.01 sur signal parfait)"


# ---------------------------------------------------------------------------
# 5. Intégration avec les formules live
# ---------------------------------------------------------------------------

def test_quant_zscore_uses_live_formula():
    """quant_zscore_single doit produire le même résultat que la formule live
    zscore_from_series appelée directement sur les closes."""
    from backtest_quant import quant_zscore_single
    from historical_data import series_asof
    from criteres_calculator import zscore_from_series

    df = series_asof("GC=F", "2024-06-15", lookback_days=200)
    if df is None:
        pytest.skip("yfinance indispo")
    closes = [float(c) for c in df["Close"].tolist()]
    window = 60
    hist = closes[-window:]
    expected = zscore_from_series(hist, zscore_div=2.0, cap=1.0)

    result = quant_zscore_single("GC=F", "2024-06-15", window=60, zscore_div=2.0, cap=1.0)
    assert result is not None
    assert result["valeur"] == pytest.approx(expected[0])
    assert result["valeur_normalisee"] == pytest.approx(expected[1])


def test_quant_rsi_uses_live_compute_rsi():
    """quant_rsi doit utiliser la fonction live `_compute_rsi`."""
    from backtest_quant import quant_rsi
    from historical_data import series_asof
    from criteres_calculator import _compute_rsi

    df = series_asof("GC=F", "2024-06-15", lookback_days=90)
    if df is None:
        pytest.skip("yfinance indispo")
    closes = [float(c) for c in df["Close"].tolist()]
    expected = _compute_rsi(closes, period=14)
    actual = quant_rsi("GC=F", "2024-06-15", period=14, lookback_days=90)
    assert actual == pytest.approx(expected, abs=1e-6)


def test_build_valeurs_actif_returns_dict():
    """Smoke test : la construction des valeurs renvoie un dict avec au moins
    une clé câblée pour 'or' à une date avec historique."""
    from backtest_quant import build_valeurs_actif_asof
    from scoring_analyste import load_fiches

    fiches = load_fiches()
    fiche = fiches.get("or")
    if not fiche:
        pytest.skip("fiche or absente")
    v = build_valeurs_actif_asof(fiche, "2024-06-15")
    # Au moins 3 critères doivent être câblés (taux TIP, DXY, flux ETF, VIX, gate)
    assert len(v) >= 3, f"trop peu de critères câblés : {list(v.keys())}"


def test_summarize_trades_accuracy_calculation():
    """Test sur trades fabriqués manuellement : 3 VRAI + 2 FAUSSE → 60% accuracy."""
    from backtest_quant import TradeResult, summarize_trades
    from datetime import date as _d
    trades = [
        TradeResult("X", "x", _d(2024, 1, 1), 1, "24h", 1.0, "LONG", 0.01, 0.5, "VRAI"),
        TradeResult("X", "x", _d(2024, 1, 2), 1, "24h", 1.0, "LONG", 0.02, 0.5, "VRAI"),
        TradeResult("X", "x", _d(2024, 1, 3), 1, "24h", 1.0, "LONG", -0.01, 0.5, "FAUSSE"),
        TradeResult("X", "x", _d(2024, 1, 4), 1, "24h", 1.0, "SHORT", -0.015, 0.5, "VRAI"),
        TradeResult("X", "x", _d(2024, 1, 5), 1, "24h", 1.0, "SHORT", 0.01, 0.5, "FAUSSE"),
        TradeResult("X", "x", _d(2024, 1, 6), 1, "24h", 1.0, "LONG", 0.001, 0.5, "non-conclusive"),
    ]
    m = summarize_trades(trades)
    assert m["n_total"] == 6
    assert m["n_conclusive"] == 5
    assert m["k_true"] == 3
    assert m["k_false"] == 2
    assert m["accuracy"] == pytest.approx(0.6)
    assert m["long_ratio"] == pytest.approx(4 / 6)


# ---------------------------------------------------------------------------
# 6. future_return cohérence
# ---------------------------------------------------------------------------

def test_future_return_no_zero_on_weekend():
    """future_return un samedi ne doit PAS retourner 0 (artefact corrigé)."""
    from historical_data import future_return
    # 2024-06-15 = samedi. Entry = close lundi 17, exit = close mardi 18.
    r = future_return("GC=F", "2024-06-15", horizon_days=1)
    if r is None:
        pytest.skip("yfinance indispo")
    assert abs(r) > 1e-6, "rendement 1j ne doit pas être strictement 0"
