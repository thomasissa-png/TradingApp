"""Régression bilan 22h15 (29-30/06) : usdjpy/USD/JPY + sucre/CANE → echeance None.

Cause racine prouvée :
  1. Twelve /price renvoie "not found / not available" pour ces symboles à 22h15
     (forex hors fenêtre temps réel / ETC softs). L'ancien code blacklistait alors
     le ticker → le repli daily-close INTERNE à fetch_price (fetch_quote →
     fetch_history) était lui aussi bloqué → prix_echeance None.
  2. Coton (COTN) n'était pas blacklisté → daily-close 2.371 servi (stale côté
     Twelve, cf. note diagnostic).

Fix :
  - /price ne blackliste plus jamais (seuls time_series/quote sondent la capacité).
  - fetch_price ajoute un repli daily-close qui CONTOURNE la blacklist (close réel).

Tous les tests sont mockés : zéro réseau.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import market_data as md  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch):
    """Clé Twelve présente + état global propre avant/après chaque test."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake-key")
    md._cache.clear()
    md._request_times.clear()
    with md._blacklist_lock:
        md._td_blacklist.discard("USDJPY=X")
        md._td_blacklist.discard("CANE")
        md._td_blacklist.discard("COTN")
    # Neutralise yfinance (bloqué en CI de toute façon) : on veut tester Twelve.
    monkeypatch.setattr(md, "_acquire_rate_limit", lambda max_wait=90.0: True)
    yield
    md._cache.clear()
    md._request_times.clear()


def _install_td(monkeypatch, responder):
    """Installe un faux http_req dont .get() délègue à responder(endpoint, params)."""
    class _Resp:
        def __init__(self, payload):
            self.status_code = 200
            self._payload = payload
            self.text = str(payload)

        def json(self):
            return self._payload

    class _FakeHttp:
        @staticmethod
        def get(url, params=None, timeout=None):
            endpoint = url.rsplit("/", 1)[-1]
            return _Resp(responder(endpoint, params or {}))

    monkeypatch.setattr(md, "http_req", _FakeHttp)


# ---------------------------------------------------------------------------
# Change 1 — /price "not found" ne blackliste PAS
# ---------------------------------------------------------------------------

def test_price_not_found_ne_blackliste_pas(monkeypatch):
    def responder(endpoint, params):
        if endpoint == "price":
            return {"status": "error", "message": "symbol not found"}
        return {"status": "error", "message": "boom"}

    _install_td(monkeypatch, responder)
    md._td_request("price", {"symbol": "USD/JPY"}, yf_ticker="USDJPY=X")
    with md._blacklist_lock:
        assert "USDJPY=X" not in md._td_blacklist


def test_timeseries_not_found_blackliste_toujours(monkeypatch):
    def responder(endpoint, params):
        return {"status": "error", "message": "symbol not found"}

    _install_td(monkeypatch, responder)
    md._td_request("time_series", {"symbol": "ZZZ"}, yf_ticker="ZZZ=F")
    with md._blacklist_lock:
        assert "ZZZ=F" in md._td_blacklist
        md._td_blacklist.discard("ZZZ=F")


# ---------------------------------------------------------------------------
# Change 2 — repli daily-close réel récupère l'échéance (USD/JPY, CANE)
# ---------------------------------------------------------------------------

def test_fetch_price_repli_daily_close_usdjpy(monkeypatch):
    """/price KO (not found) + yfinance KO → daily-close réel = échéance non-None."""
    monkeypatch.setattr(md, "_yf_history", lambda *a, **k: None)

    def responder(endpoint, params):
        if endpoint == "price":
            return {"status": "error", "message": "symbol not found"}
        if endpoint == "time_series":
            return {"values": [{"datetime": "2026-06-30", "open": "162.0",
                                "high": "162.5", "low": "161.5", "close": "162.34"}]}
        return {"status": "error", "message": "no quote"}

    _install_td(monkeypatch, responder)
    price = md.fetch_price("USDJPY=X")
    assert price == pytest.approx(162.34)
    with md._blacklist_lock:
        assert "USDJPY=X" not in md._td_blacklist


def test_fetch_price_repli_survit_a_une_blacklist_anterieure(monkeypatch):
    """Hypothèse (a) : ticker déjà blacklisté par un échec time_series antérieur.
    Le repli daily-close contourne la blacklist → close réel quand même."""
    monkeypatch.setattr(md, "_yf_history", lambda *a, **k: None)
    with md._blacklist_lock:
        md._td_blacklist.add("CANE")

    def responder(endpoint, params):
        # _map_ticker retournerait None (blacklisté) donc /price n'appelle pas TD ;
        # seul _td_daily_close (bypass) émet ce time_series.
        if endpoint == "time_series":
            return {"values": [{"datetime": "2026-06-30", "open": "9.7",
                                "high": "9.9", "low": "9.6", "close": "9.78"}]}
        return {"status": "error", "message": "blacklisted path"}

    _install_td(monkeypatch, responder)
    try:
        price = md.fetch_price("CANE")
        assert price == pytest.approx(9.78)
    finally:
        with md._blacklist_lock:
            md._td_blacklist.discard("CANE")


def test_fetch_price_none_propre_si_tout_echoue(monkeypatch):
    """Aucune source disponible → None propre (n/a), zéro valeur inventée."""
    monkeypatch.setattr(md, "_yf_history", lambda *a, **k: None)

    def responder(endpoint, params):
        return {"status": "error", "message": "not available"}

    _install_td(monkeypatch, responder)
    assert md.fetch_price("USDJPY=X") is None


def test_daily_close_repli_ignore_indices_sans_proxy(monkeypatch):
    """_td_daily_close ne cible que les symboles mappés Twelve (pas ^DJI etc.)."""
    calls = {"n": 0}

    def responder(endpoint, params):
        calls["n"] += 1
        return {"values": [{"datetime": "2026-06-30", "open": "1", "high": "1",
                            "low": "1", "close": "42"}]}

    _install_td(monkeypatch, responder)
    assert md._td_daily_close("^DJI") is None
    assert calls["n"] == 0  # aucun appel réseau pour un ticker non mappé
