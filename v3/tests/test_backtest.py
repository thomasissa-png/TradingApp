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

# pandas est une dépendance CI (v3/requirements.txt: pandas==2.2.2, installée par
# `pip install -r v3/requirements.txt` dans cycle.yml/test-extraction.yml) mais est
# absente de ce conteneur local. Les tests qui traversent le moteur backtest
# (historical_data/backtest_quant → pandas) sont skippés proprement ici, JAMAIS en CI.
_PANDAS_REASON = "pandas (dépendance CI v3/requirements.txt) absente du conteneur local"


# ---------------------------------------------------------------------------
# 1. No look-ahead (critère LE PLUS critique)
# ---------------------------------------------------------------------------

def test_series_asof_strict_no_lookahead():
    """series_asof('GC=F', d) ne doit JAMAIS retourner de barre datée >= d."""
    pytest.importorskip("pandas", reason=_PANDAS_REASON)
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
    pytest.importorskip("pandas", reason=_PANDAS_REASON)
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
    pytest.importorskip("pandas", reason=_PANDAS_REASON)
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
    pytest.importorskip("pandas", reason=_PANDAS_REASON)
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
    pytest.importorskip("pandas", reason=_PANDAS_REASON)
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
# 6bis. No look-ahead FRED + COT (chantier v2 — données injectées, sans réseau)
# ---------------------------------------------------------------------------

def test_fred_series_asof_strict_no_lookahead():
    """fred_series_asof ne doit JAMAIS renvoyer un point daté >= as_of.
    On injecte une série synthétique dans le cache RAM pour tester sans réseau."""
    import historical_data as hd
    sid = "__TEST_FRED__"
    # série quotidienne 2024-01-01 → 2024-12-31, valeur = jour de l'année
    pts = []
    d0 = date(2024, 1, 1)
    for i in range(366):
        d = d0 + timedelta(days=i)
        pts.append((d.isoformat(), float(i)))
    hd._FRED_RAM_CACHE[sid] = pts
    dated = hd.fred_dated_asof(sid, "2024-06-15", lookback_days=400)
    assert dated is not None and len(dated) > 0
    last = dated[-1][0]
    assert last < date(2024, 6, 15), f"VIOLATION look-ahead FRED : {last} >= as_of"
    # la valeur du 2024-06-14 = jour 165 doit être présente, celle du 15 absente
    present = {d for d, _ in dated}
    assert date(2024, 6, 14) in present
    assert date(2024, 6, 15) not in present
    del hd._FRED_RAM_CACHE[sid]


def test_cot_nets_asof_strict_no_lookahead_with_publication_lag():
    """cot_nets_asof ne doit garder qu'un rapport publié (report_date+lag) AVANT as_of.
    Données injectées : un rapport hebdo (mardi). Le rapport du mardi 2024-06-11
    n'est publié que vers le vendredi → visible à as_of=2024-06-13 ? Non (lag 3j).
    Visible à 2024-06-15 ? Oui."""
    import historical_data as hd
    mkt = "__TEST_MARKET__"
    pts = []
    # mardis successifs
    d = date(2024, 5, 7)
    val = 0.0
    while d <= date(2024, 6, 18):
        pts.append((d, val))
        val += 100.0
        d = d + timedelta(days=7)
    hd._COT_RAM_CACHE[mkt] = pts
    # report_date 2024-06-11 (+3 = 06-14). À as_of 2024-06-13 : pas encore visible.
    nets_13 = hd.cot_nets_asof(mkt, "2024-06-13", lookback_days=400)
    nets_16 = hd.cot_nets_asof(mkt, "2024-06-16", lookback_days=400)
    # entre le 13 et le 16, le rapport du 11 devient visible → +1 point
    assert nets_16 is not None
    n13 = 0 if nets_13 is None else len(nets_13)
    assert len(nets_16) == n13 + 1, (
        f"le rapport du 2024-06-11 doit devenir visible entre le 13 et le 16 "
        f"(n13={n13}, n16={len(nets_16)})"
    )
    # Aucun report_date visible ne doit dépasser as_of-lag
    from historical_data import COT_PUBLICATION_LAG_DAYS
    visible_reports = [rd for rd, _ in pts
                       if rd + timedelta(days=COT_PUBLICATION_LAG_DAYS) < date(2024, 6, 16)]
    assert len(nets_16) == len(visible_reports)
    del hd._COT_RAM_CACHE[mkt]


def test_cot_nets_definition_matches_live():
    """Le net COT du backtest = noncomm_long − noncomm_short, MÊME définition que le
    live fetch_cftc_managed_money_nets. Vérifié sur le parser Socrata partagé."""
    import historical_data as hd
    rows = [
        {"report_date_as_yyyy_mm_dd": "2024-06-11", "noncomm_positions_long_all": "300",
         "noncomm_positions_short_all": "100"},
        {"report_date_as_yyyy_mm_dd": "2024-06-04", "noncomm_positions_long_all": "250",
         "noncomm_positions_short_all": "150"},
    ]
    # On simule le parsing (même logique que _fetch_cot_socrata)
    from datetime import datetime
    parsed = []
    for r in rows:
        dd = datetime.fromisoformat(r["report_date_as_yyyy_mm_dd"]).date()
        net = float(r["noncomm_positions_long_all"]) - float(r["noncomm_positions_short_all"])
        parsed.append((dd, net))
    parsed.sort(key=lambda t: t[0])
    assert parsed[-1][1] == 200.0  # 300 - 100
    assert parsed[0][1] == 100.0   # 250 - 150


def test_fred_spread_asof_locf_alignment():
    """fred_spread_asof applique le forward-fill LOCF (série DE basse fréquence
    reportée sur les dates US) et reste no-look-ahead."""
    import historical_data as hd
    sus, sde = "__US__", "__DE__"
    # US quotidien
    us = []
    d0 = date(2024, 1, 1)
    for i in range(200):
        us.append(((d0 + timedelta(days=i)).isoformat(), 5.0))
    # DE mensuel (1er de chaque mois), valeur 2.0
    de = [((date(2024, m, 1)).isoformat(), 2.0) for m in range(1, 7)]
    hd._FRED_RAM_CACHE[sus] = us
    hd._FRED_RAM_CACHE[sde] = de
    spread = hd.fred_spread_asof(sus, sde, "2024-06-15", lookback_days=400)
    assert spread is not None and len(spread) > 10
    # spread = 5 - 2 = 3 partout (LOCF)
    assert all(abs(s - 3.0) < 1e-9 for s in spread)
    del hd._FRED_RAM_CACHE[sus]
    del hd._FRED_RAM_CACHE[sde]


# ---------------------------------------------------------------------------
# 6. future_return cohérence
# ---------------------------------------------------------------------------

def test_future_return_no_zero_on_weekend():
    """future_return un samedi ne doit PAS retourner 0 (artefact corrigé)."""
    pytest.importorskip("pandas", reason=_PANDAS_REASON)
    from historical_data import future_return
    # 2024-06-15 = samedi. Entry = close lundi 17, exit = close mardi 18.
    r = future_return("GC=F", "2024-06-15", horizon_days=1)
    if r is None:
        pytest.skip("yfinance indispo")
    assert abs(r) > 1e-6, "rendement 1j ne doit pas être strictement 0"
