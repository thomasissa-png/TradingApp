"""Tests rate-limiter Twelve Data : ATTEND au lieu de rejeter.

Cf. CI 2026-05 : l'ancien `_try_rate_limit()` retournait False dès le 8e appel
dans la minute → fallback yfinance → yfinance bloqué sur runners GitHub Actions
(IP datacenter) → indices/Twelve KO. Le nouveau `_acquire_rate_limit()` dort
jusqu'à libération d'un slot, sans perdre la requête.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest

# Path setup identique aux autres tests v3
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import market_data as md  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_rate_state():
    """Avant chaque test : vide la deque (état global module-level)."""
    md._request_times.clear()
    yield
    md._request_times.clear()


class _FakeClock:
    """Horloge contrôlée : remplace time.monotonic / time.sleep dans le module.

    sleep(dt) avance la fausse horloge de dt secondes sans réellement dormir.
    Garde la trace des sleeps appelés pour les assertions.
    """

    def __init__(self, start: float = 1000.0):
        self.now = start
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, dt: float) -> None:
        self.sleeps.append(dt)
        self.now += dt


@pytest.fixture
def fake_clock(monkeypatch):
    clock = _FakeClock()
    # Le module fait `import time` puis `time.monotonic()` / `time.sleep()`.
    # On patche les attributs sur l'objet time tel qu'importé dans md.
    monkeypatch.setattr(md.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(md.time, "sleep", clock.sleep)
    return clock


# ---------------------------------------------------------------------------
# _TD_RPM configurable via env
# ---------------------------------------------------------------------------

def test_td_rpm_default_is_grow_plan_safe_margin():
    """Sans env override, _TD_RPM = 55 (plan Grow ≈ 55-60 req/min, marge sûre)."""
    # On vérifie la valeur effective. Au moment du test, si TWELVE_RPM n'est pas
    # défini dans l'env CI, on doit avoir 55. Si défini, on accepte la valeur env.
    expected = int(os.environ.get("TWELVE_RPM", "55"))
    assert md._TD_RPM == expected
    # Garde-fou : la valeur ne doit jamais retomber à l'ancien 7 par défaut.
    if "TWELVE_RPM" not in os.environ:
        assert md._TD_RPM == 55


def test_td_rpm_reads_from_env(monkeypatch):
    """Au reload du module, _TD_RPM doit refléter TWELVE_RPM."""
    monkeypatch.setenv("TWELVE_RPM", "12")
    reloaded = importlib.reload(md)
    try:
        assert reloaded._TD_RPM == 12
    finally:
        # Restaure le module dans son état attendu par les autres tests
        monkeypatch.delenv("TWELVE_RPM", raising=False)
        importlib.reload(md)


# ---------------------------------------------------------------------------
# _acquire_rate_limit : attend puis acquiert
# ---------------------------------------------------------------------------

def test_acquire_rate_limit_fonction_existe():
    """API publique du module : _acquire_rate_limit doit exister."""
    assert hasattr(md, "_acquire_rate_limit")
    assert callable(md._acquire_rate_limit)


def test_acquire_passes_through_when_window_not_full(fake_clock, monkeypatch):
    """Fenêtre vide → acquisition immédiate, aucun sleep."""
    monkeypatch.setattr(md, "_TD_RPM", 5)
    ok = md._acquire_rate_limit()
    assert ok is True
    assert fake_clock.sleeps == []  # aucun sleep
    assert len(md._request_times) == 1


def test_acquire_sleeps_then_acquires_when_window_full(fake_clock, monkeypatch):
    """Fenêtre pleine → dort jusqu'à libération du plus ancien slot, puis acquiert."""
    monkeypatch.setattr(md, "_TD_RPM", 3)
    # Remplit la fenêtre : 3 slots à t=1000 (now actuel)
    for _ in range(3):
        md._request_times.append(fake_clock.now)
    # Avance le temps de 10s : le plus ancien a 10s, il reste 50s avant qu'il sorte.
    fake_clock.now += 10.0

    ok = md._acquire_rate_limit()
    assert ok is True
    # Doit avoir dormi ~50s (50 - epsilon + 0.05 marge) avant d'acquérir
    assert len(fake_clock.sleeps) == 1
    assert 49.5 < fake_clock.sleeps[0] < 51.0
    # Le nouveau slot vient d'être ajouté ; les anciens (>60s après sleep)
    # ont été expirés par la boucle de purge → seul le slot frais reste.
    assert len(md._request_times) == 1
    assert md._request_times[0] == fake_clock.now


def test_acquire_returns_false_when_wait_exceeds_max(fake_clock, monkeypatch):
    """Si l'attente nécessaire dépasse max_wait → False (dégradation gracieuse)."""
    monkeypatch.setattr(md, "_TD_RPM", 2)
    # Remplit avec des timestamps très récents → il faudrait attendre ~60s
    for _ in range(2):
        md._request_times.append(fake_clock.now)

    # max_wait = 5s seulement → impossible d'attendre 60s
    ok = md._acquire_rate_limit(max_wait=5.0)
    assert ok is False
    # Et on n'a pas dormi (refus en amont)
    assert fake_clock.sleeps == []


def test_try_rate_limit_still_works_for_backcompat(fake_clock, monkeypatch):
    """L'ancienne API non-bloquante reste fonctionnelle."""
    monkeypatch.setattr(md, "_TD_RPM", 2)
    assert md._try_rate_limit() is True
    assert md._try_rate_limit() is True
    # 3e tentative dans la même fenêtre → False (non-bloquant)
    assert md._try_rate_limit() is False


# ---------------------------------------------------------------------------
# Intégration avec _td_request : fallback préservé sans clé
# ---------------------------------------------------------------------------

def test_td_request_returns_none_when_no_api_key(monkeypatch):
    """Pas de clé Twelve → None (fallback yfinance dans le caller), pas de crash."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "")
    result = md._td_request("quote", {"symbol": "AAPL"}, yf_ticker="AAPL")
    assert result is None


def test_td_request_uses_acquire_not_try(fake_clock, monkeypatch):
    """_td_request doit appeler _acquire_rate_limit (bloquant), pas _try_rate_limit."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake-key-for-test")
    calls = {"acquire": 0, "try": 0}

    def fake_acquire(max_wait=md._RATE_WAIT_TIMEOUT):
        calls["acquire"] += 1
        return True

    def fake_try():
        calls["try"] += 1
        return True

    monkeypatch.setattr(md, "_acquire_rate_limit", fake_acquire)
    monkeypatch.setattr(md, "_try_rate_limit", fake_try)

    # Mock requests pour ne pas faire d'appel réseau
    class _Resp:
        status_code = 200
        text = "{}"
        def json(self): return {"price": "1.0"}

    class _FakeHttp:
        @staticmethod
        def get(url, params=None, timeout=None):
            return _Resp()

    monkeypatch.setattr(md, "http_req", _FakeHttp)

    md._td_request("price", {"symbol": "AAPL"}, yf_ticker="AAPL")
    assert calls["acquire"] == 1
    assert calls["try"] == 0


def test_td_request_falls_back_when_acquire_returns_false(monkeypatch):
    """Si _acquire_rate_limit refuse (timeout d'attente) → _td_request retourne None."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake-key-for-test")
    monkeypatch.setattr(md, "_acquire_rate_limit", lambda max_wait=90.0: False)
    # http_req ne doit JAMAIS être appelé si le rate-limit refuse
    sentinel = {"called": False}

    class _Boom:
        @staticmethod
        def get(*a, **kw):
            sentinel["called"] = True
            raise AssertionError("ne doit pas être appelé")

    monkeypatch.setattr(md, "http_req", _Boom)
    result = md._td_request("price", {"symbol": "AAPL"}, yf_ticker="AAPL")
    assert result is None
    assert sentinel["called"] is False
