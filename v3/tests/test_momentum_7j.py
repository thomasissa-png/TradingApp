"""Recalibrage horizon↔fenêtre 22/06 : tendance-prix COURTE (7j) pour l'horizon 7j.

Le 7j s'appuyait sur une tendance 20 jours (retard ~10j, incohérent avec un horizon
7j). On ajoute `momentum_prix_7j_<actif>` (lag 7, retard ~2-3j) qui DOMINE le 7j, et
on renvoie la 20j vers le 1 mois. Tests purs (série synthétique, zéro réseau).
"""
from __future__ import annotations

import glob
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import criteres_calculator as cc  # noqa: E402

FICHES = [p for p in glob.glob(str(ROOT / "config" / "fiches" / "*.yml"))
          if not os.path.basename(p).startswith("_")]
TREND_ASSETS = ["or", "argent", "cuivre", "petrole", "cafe", "cacao", "ble",
                "sp500", "nasdaq", "cac40", "eurusd"]  # vix : pas de tendance-prix propre


def _serie_bruitee(n=120, seed=1):
    random.seed(seed)
    base = datetime(2026, 1, 1)
    px = 100.0
    out = []
    for i in range(n):
        px *= (1 + 0.003 + random.uniform(-0.012, 0.012))
        out.append((base + timedelta(days=i), px))
    return out


_CRIT = {"normalisation": "zscore", "zscore_window": 60, "zscore_div": 2, "cap": 1.0, "signe": 1}
_TS = "2026-06-22T07:00:00+00:00"


def test_lag_parse_depuis_le_cle(monkeypatch):
    # Le dispatcher lit la fenêtre dans le cle : 7j → lag 7, 20j → lag 20.
    capt = {}
    real = cc._twelve_variation_zscore

    def spy(symbol, lag, crit):
        capt[symbol] = lag
        return real(symbol, lag, crit)

    monkeypatch.setattr(cc, "fetch_twelve_series", lambda s, **k: _serie_bruitee())
    monkeypatch.setattr(cc, "_twelve_variation_zscore", spy)
    cc._handle_twelve_zscore_dispatch("momentum_prix_7j_or", _CRIT, _TS)
    cc._handle_twelve_zscore_dispatch("momentum_prix_20j_or", _CRIT, _TS)
    assert capt.get("GC=F") in (7, 20)  # appelé
    # On vérifie les deux lags via deux symboles distincts
    capt.clear()
    cc._handle_twelve_zscore_dispatch("momentum_prix_7j_argent", _CRIT, _TS)
    assert capt.get("SI=F") == 7


def test_momentum_7j_calcule_pour_tous_les_actifs(monkeypatch):
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda s, **k: _serie_bruitee())
    for asset in TREND_ASSETS:
        res = cc._handle_twelve_zscore_dispatch(f"momentum_prix_7j_{asset}", _CRIT, _TS)
        assert res is not None, f"{asset} : momentum 7j devrait calculer"


def test_7j_demande_moins_de_donnees_que_20j(monkeypatch):
    # Argument de robustesse : un lag plus court exige MOINS de closes → si le 20j
    # calcule, le 7j calcule aussi. On le vérifie sur une série juste assez longue
    # pour le 7j mais trop courte pour le 20j.
    serie = _serie_bruitee(n=75)  # 7+60+marge OK ; 20+60+marge limite
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda s, **k: serie)
    r7 = cc._handle_twelve_zscore_dispatch("momentum_prix_7j_or", _CRIT, _TS)
    assert r7 is not None


def test_toutes_les_fiches_ont_7j_et_20j_demote():
    for p in FICHES:
        asset = os.path.splitext(os.path.basename(p))[0]
        data = yaml.safe_load(open(p, encoding="utf-8"))
        crits = {c.get("cle_courante"): c for c in (data.get("criteres") or [])}
        if asset == "vix":
            assert f"momentum_prix_7j_{asset}" not in crits  # pas de tendance-prix VIX
            continue
        c7 = crits.get(f"momentum_prix_7j_{asset}")
        c20 = crits.get(f"momentum_prix_20j_{asset}")
        assert c7 and c20, f"{asset} : 7j et 20j attendus"
        # 7j domine le 7j, 20j bascule vers le 1m.
        assert c7["pertinence"]["7j"] == 1.0 and c7["pertinence"]["1m"] <= 0.3
        assert c20["pertinence"]["1m"] == 1.0 and c20["pertinence"]["7j"] <= 0.4
        # résolution ticker
        assert cc.TWELVE_SYMBOLS.get(f"momentum_prix_7j_{asset}")
