"""Tests du helper HTTP partagé `http_retry.http_get_retry`.

Couvre la résilience attendue par les fetchers news (RSS/GNews/NewsAPI) et FRED :
- retry backoff sur 429 puis succès 200
- épuisement des retries (429 persistant) → None
- AUCUN retry sur statut non-retriable (403, 404) → échec immédiat
- respect de l'en-tête Retry-After
- zéro régression sur 200 (succès au 1er essai, aucun sleep)
- erreur réseau persistante → None ; status_out renseigné pour le monitoring
- buckets de throttle indépendants

Tous les sleeps sont capturés (pas d'attente réelle) ; on vérifie aussi les
DÉLAIS calculés pour garantir le backoff et le respect de Retry-After.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import http_retry as hr  # noqa: E402


def _resp(status_code: int, *, headers: dict | None = None, content: bytes = b"ok"):
    m = MagicMock()
    m.status_code = status_code
    m.headers = headers or {}
    m.content = content
    m.json = MagicMock(return_value={"ok": True})
    return m


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Capture les sleeps (backoff + throttle) sans attendre. Expose la liste des
    délais pour les tests qui veulent vérifier le backoff."""
    delays: list[float] = []
    monkeypatch.setattr(hr.time, "sleep", lambda s=0.0: delays.append(s))
    # Reset throttle global entre tests (état module-level partagé).
    hr._last_request_ts.clear()
    return delays


@pytest.fixture(autouse=True)
def _no_jitter(monkeypatch):
    """Jitter déterministe (0) pour assertions exactes sur les délais."""
    monkeypatch.setattr(hr.random, "uniform", lambda a, b: 0.0)


# ---------------------------------------------------------------------------
# Succès direct — zéro régression
# ---------------------------------------------------------------------------

def test_200_succeeds_first_try_no_retry(_no_sleep):
    with patch("requests.get", return_value=_resp(200)) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, label="t")
    assert out is not None
    assert out.status_code == 200
    assert g.call_count == 1
    # Aucun backoff (que des sleeps de throttle, ici min_interval=0 → aucun)
    assert _no_sleep == []


def test_200_returns_response_for_caller_parsing(_no_sleep):
    r = _resp(200)
    with patch("requests.get", return_value=r):
        out = hr.http_get_retry("https://x", min_interval=0.0)
    assert out is r  # la Response est rendue telle quelle (caller fait .json()/.content)


# ---------------------------------------------------------------------------
# Retry sur 429 / 5xx
# ---------------------------------------------------------------------------

def test_429_then_200_retries_and_succeeds(_no_sleep):
    seq = [_resp(429), _resp(200)]
    with patch("requests.get", side_effect=seq) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, backoff_base=2.0, label="t")
    assert out is not None and out.status_code == 200
    assert g.call_count == 2
    # 1 backoff avant le 2e essai : 2.0 * 2**0 = 2.0 (jitter=0)
    assert _no_sleep == [pytest.approx(2.0)]


def test_503_then_200_retries(_no_sleep):
    seq = [_resp(503), _resp(200)]
    with patch("requests.get", side_effect=seq) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0)
    assert out is not None and out.status_code == 200
    assert g.call_count == 2


def test_429_exhausts_retries_returns_none(_no_sleep):
    with patch("requests.get", return_value=_resp(429)) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=3,
                                backoff_base=2.0, label="t")
    assert out is None
    assert g.call_count == 3  # 3 tentatives totales
    # 2 backoffs (avant essais 2 et 3) : 2.0 puis 4.0
    assert _no_sleep == [pytest.approx(2.0), pytest.approx(4.0)]


def test_exhaustion_records_last_status(_no_sleep):
    status_out: dict = {}
    with patch("requests.get", return_value=_resp(429)):
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=2,
                                status_out=status_out)
    assert out is None
    assert status_out["status"] == "429"


# ---------------------------------------------------------------------------
# Statuts non-retriables — pas d'acharnement (403 mining_com, 404)
# ---------------------------------------------------------------------------

def test_403_no_retry_returns_none(_no_sleep):
    status_out: dict = {}
    with patch("requests.get", return_value=_resp(403)) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=3,
                                status_out=status_out, label="mining_com")
    assert out is None
    assert g.call_count == 1  # AUCUN retry sur 403
    assert _no_sleep == []     # aucun backoff
    assert status_out["status"] == "403"


def test_404_no_retry_returns_none(_no_sleep):
    with patch("requests.get", return_value=_resp(404)) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=3)
    assert out is None
    assert g.call_count == 1


def test_401_no_retry(_no_sleep):
    with patch("requests.get", return_value=_resp(401)) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=3)
    assert out is None
    assert g.call_count == 1


# ---------------------------------------------------------------------------
# Retry-After
# ---------------------------------------------------------------------------

def test_retry_after_honored_over_backoff(_no_sleep):
    seq = [_resp(429, headers={"Retry-After": "7"}), _resp(200)]
    with patch("requests.get", side_effect=seq):
        out = hr.http_get_retry("https://x", min_interval=0.0, backoff_base=2.0)
    assert out is not None and out.status_code == 200
    # On respecte Retry-After=7 (au lieu du backoff 2.0)
    assert _no_sleep == [pytest.approx(7.0)]


def test_retry_after_invalid_falls_back_to_backoff(_no_sleep):
    # Retry-After au format date HTTP (non géré) → backoff exponentiel
    seq = [_resp(429, headers={"Retry-After": "Wed, 21 Oct 2025 07:28:00 GMT"}), _resp(200)]
    with patch("requests.get", side_effect=seq):
        out = hr.http_get_retry("https://x", min_interval=0.0, backoff_base=2.0)
    assert out is not None
    assert _no_sleep == [pytest.approx(2.0)]


def test_parse_retry_after_units():
    assert hr.parse_retry_after("5") == 5.0
    assert hr.parse_retry_after("0") == 0.0
    assert hr.parse_retry_after(None) is None
    assert hr.parse_retry_after("") is None
    assert hr.parse_retry_after("not-a-number") is None
    assert hr.parse_retry_after("-3") is None  # négatif ignoré


# ---------------------------------------------------------------------------
# Erreur réseau
# ---------------------------------------------------------------------------

def test_network_error_persistent_returns_none(_no_sleep):
    import requests as _rq
    with patch("requests.get", side_effect=_rq.Timeout("boom")) as g:
        status_out: dict = {}
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=3,
                                status_out=status_out)
    assert out is None
    assert g.call_count == 3  # retry sur erreur réseau aussi
    assert status_out["status"] == "net_error"


def test_network_error_then_recovers(_no_sleep):
    import requests as _rq
    seq = [_rq.ConnectionError("flaky"), _resp(200)]
    with patch("requests.get", side_effect=seq) as g:
        out = hr.http_get_retry("https://x", min_interval=0.0, max_retries=3)
    assert out is not None and out.status_code == 200
    assert g.call_count == 2


# ---------------------------------------------------------------------------
# Throttle
# ---------------------------------------------------------------------------

def test_throttle_sleeps_between_requests(_no_sleep, monkeypatch):
    # 2 requêtes 200 successives sur le même bucket avec min_interval > 0.
    # monotonic figé → l'écart perçu est 0 → throttle dort min_interval au 2e appel.
    monkeypatch.setattr(hr.time, "monotonic", lambda: 100.0)
    with patch("requests.get", return_value=_resp(200)):
        hr.http_get_retry("https://x", bucket="b1", min_interval=0.5)
        hr.http_get_retry("https://x", bucket="b1", min_interval=0.5)
    # Le 2e appel a dû dormir ~0.5s (le 1er fixe le timestamp).
    assert any(d == pytest.approx(0.5) for d in _no_sleep)


def test_throttle_buckets_are_independent(_no_sleep, monkeypatch):
    monkeypatch.setattr(hr.time, "monotonic", lambda: 100.0)
    with patch("requests.get", return_value=_resp(200)):
        hr.http_get_retry("https://x", bucket="alpha", min_interval=0.5)
        hr.http_get_retry("https://x", bucket="beta", min_interval=0.5)
    # Buckets distincts → aucun des deux ne devrait attendre pour l'autre.
    assert _no_sleep == []
