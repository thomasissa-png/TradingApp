"""Tests Phase 2.2 — ingestion étendue (mainstream + early-signal + structured).

Mock 100% des appels HTTP / feedparser. Vérifie :
- early-signal feeds pollés au même titre que mainstream
- GNews + NewsAPI parsés correctement et items injectés au pipeline
- dédup cross-source (mainstream + early-signal + structured)
- feed mort (404 / timeout / exception) → log + skip sans casser la run
- clé API absente → skip propre (zéro invention, zéro item)
- pré-filtre finance (blacklist + whitelist) appliqué uniformément
- SOURCE_WEIGHTS : poids configuré pour chaque source pollée + DEFAULT fallback
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Stub feedparser si absent en environnement de test (sandbox CI sans sgmllib3k).
# En prod (GitHub Actions / Replit), feedparser est installé via requirements.
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    fp_stub = types.ModuleType("feedparser")
    fp_stub.parse = lambda content: types.SimpleNamespace(entries=[])
    sys.modules["feedparser"] = fp_stub

import config  # noqa: E402
import news_collector as nc  # noqa: E402


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    """Isole le cache dédup SQLite par test (pas de pollution cross-test)."""
    db = tmp_path / "titles_cache.db"
    monkeypatch.setattr(nc, "DB_PATH", db)
    yield


@pytest.fixture(autouse=True)
def _clear_api_keys(monkeypatch):
    """Par défaut, pas de clés API (le test qui en veut les set explicitement)."""
    monkeypatch.delenv("GNEWS_API_KEY", raising=False)
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)


def _mk_rss_response(entries):
    """Réponse HTTP mockée pour feedparser : entries est une liste de dicts."""
    resp = MagicMock()
    resp.status_code = 200
    resp.content = b"<rss/>"
    resp.raise_for_status = MagicMock()
    return resp, entries


# ============================================================
# Config sanity
# ============================================================

def test_early_signal_feeds_declared():
    """early-signal feeds configurés (purge flux morts 30/05 : 14 flux testés OK)."""
    assert len(config.EARLY_SIGNAL_FEEDS) >= 12
    # Échantillon : energie, banques centrales, métaux, actifs sous-couverts (gnews)
    names = {n for n, _, _ in config.EARLY_SIGNAL_FEEDS}
    assert "eia_today_in_energy" in names
    assert "mining_com" in names
    assert "fed_press_all" in names
    assert "ecb_press" in names
    assert "gnews_coffee" in names
    assert "gnews_cac40" in names
    assert "oilprice" in names


def test_structured_sources_declared():
    """GNews + NewsAPI déclarés avec env_key + base_url."""
    kinds = {kind for _, kind, _, _ in config.STRUCTURED_SOURCES}
    assert "gnews" in kinds
    assert "newsapi" in kinds
    for name, kind, env_key, base_url in config.STRUCTURED_SOURCES:
        assert env_key, f"Env key manquant pour {name}"
        assert base_url.startswith("http"), f"Base URL invalide pour {name}"


def test_source_weights_coverage():
    """Toutes les sources pollées ont un poids explicite (sauf DEFAULT)."""
    for name, _, _ in config.RSS_FEEDS:
        if name.startswith("reuters_"):
            continue
        assert name in config.SOURCE_WEIGHTS, f"Poids manquant : {name}"
    for name, _, _ in config.EARLY_SIGNAL_FEEDS:
        assert name in config.SOURCE_WEIGHTS, f"Poids manquant : {name}"
    for name, _, _, _ in config.STRUCTURED_SOURCES:
        assert name in config.SOURCE_WEIGHTS, f"Poids manquant : {name}"


def test_source_weight_default_fallback():
    """Source inconnue → DEFAULT_SOURCE_WEIGHT, pas d'exception."""
    assert config.source_weight("source_qui_nexiste_pas") == config.DEFAULT_SOURCE_WEIGHT
    assert config.source_weight("fed_press_all") > config.DEFAULT_SOURCE_WEIGHT  # signal primaire


# ============================================================
# GNews
# ============================================================

def test_gnews_parses_articles():
    payload = {
        "articles": [
            {
                "title": "Oil prices jump on OPEC cut",
                "description": "Brent crude rallies after OPEC+ announces production cut.",
                "url": "https://x/1",
                "publishedAt": "2026-05-29T10:00:00Z",
                "source": {"name": "Reuters"},
            },
            {
                "title": "Fed signals rate hold",
                "description": "FOMC minutes show dovish tilt.",
                "url": "https://x/2",
                "publishedAt": "2026-05-29T11:00:00Z",
                "source": {"name": "WSJ"},
            },
        ]
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=payload)
    with patch.object(nc.requests, "get", return_value=mock_resp):
        items = nc._fetch_gnews("oil", "fake_key", "https://gnews.io/api/v4/search")
    assert len(items) == 2
    assert items[0].source == "gnews"
    assert "OPEC" in items[0].title
    assert items[0].summary  # description bien injectée


def test_gnews_http_error_returns_empty():
    import requests as _rq
    with patch.object(nc.requests, "get", side_effect=_rq.Timeout("boom")):
        items = nc._fetch_gnews("x", "k", "https://x")
    assert items == []


def test_gnews_bad_json_returns_empty():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(side_effect=ValueError("bad json"))
    with patch.object(nc.requests, "get", return_value=mock_resp):
        items = nc._fetch_gnews("x", "k", "https://x")
    assert items == []


# ============================================================
# NewsAPI
# ============================================================

def test_newsapi_parses_articles():
    payload = {
        "status": "ok",
        "articles": [
            {
                "title": "Gold hits record on Fed dovish pivot",
                "description": "Bullion rallies above $2,500/oz.",
                "url": "https://x/1",
                "publishedAt": "2026-05-29T09:00:00Z",
                "source": {"name": "Bloomberg"},
            }
        ],
    }
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=payload)
    with patch.object(nc.requests, "get", return_value=mock_resp):
        items = nc._fetch_newsapi("gold", "fake_key", "https://newsapi.org/v2/everything")
    assert len(items) == 1
    assert items[0].source == "newsapi"
    assert "Gold" in items[0].title


def test_newsapi_status_error_returns_empty():
    payload = {"status": "error", "message": "rate limited"}
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=payload)
    with patch.object(nc.requests, "get", return_value=mock_resp):
        items = nc._fetch_newsapi("x", "k", "https://x")
    assert items == []


# ============================================================
# Structured collect — clés absentes
# ============================================================

def test_structured_collect_skips_when_no_keys(monkeypatch, caplog):
    """Pas de clé API → 0 item, log info, zéro exception."""
    monkeypatch.delenv("GNEWS_API_KEY", raising=False)
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
    with patch.object(nc.requests, "get") as mock_get:
        items = nc._collect_structured()
    assert items == []
    mock_get.assert_not_called()  # JAMAIS d'appel HTTP sans clé


def test_structured_collect_uses_gnews_when_key_present(monkeypatch):
    monkeypatch.setenv("GNEWS_API_KEY", "fake_gnews")
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
    payload = {"articles": [{
        "title": "Brent jumps", "description": "...", "url": "u",
        "publishedAt": "2026-05-29T00:00:00Z", "source": {"name": "x"},
    }]}
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=payload)
    with patch.object(nc.requests, "get", return_value=mock_resp) as mock_get:
        items = nc._collect_structured()
    # 1 article × N queries × 1 source active (GNews)
    assert len(items) == len(config.STRUCTURED_QUERIES)
    assert all(it.source == "gnews" for it in items)
    assert mock_get.call_count == len(config.STRUCTURED_QUERIES)


# ============================================================
# collect_all — pipeline complet
# ============================================================

def _make_mock_rss(items_by_url):
    """Retourne une fonction qui simule requests.get pour RSS feeds.
    items_by_url : dict url → list[dict entries] OU "FAIL" pour simuler une erreur.
    """
    import requests as _rq

    def fake_get(url, **kwargs):
        # Si URL inconnue → empty feed
        for known_url, entries in items_by_url.items():
            if url == known_url:
                if entries == "FAIL":
                    raise _rq.Timeout(f"timeout on {url}")
                resp = MagicMock()
                resp.raise_for_status = MagicMock()
                resp.content = b"<rss/>"
                return resp
        # Default : feed vide
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.content = b"<rss/>"
        return resp

    return fake_get


def _make_mock_feedparser(items_by_url, urls_seen):
    """Retourne fake feedparser.parse qui regarde quelle URL a été appelée."""
    # Comme feedparser.parse(content), on ne sait pas l'URL → on track via ordre d'appel.
    call_order = []

    def fake_parse(content):
        result = MagicMock()
        # On retourne les entries pour la prochaine URL dans urls_seen
        if urls_seen:
            url = urls_seen.pop(0)
            call_order.append(url)
            entries_data = items_by_url.get(url, [])
            if entries_data == "FAIL":
                result.entries = []
            else:
                result.entries = entries_data
        else:
            result.entries = []
        return result

    return fake_parse


def test_collect_all_polls_early_signal_feeds(monkeypatch):
    """Vérifie que collect_all() poll mainstream ET early-signal."""
    polled_urls = []

    def fake_fetch_rss(name, url, **kwargs):
        polled_urls.append((name, url))
        # Retourne 1 item finance-relevant par feed (pour passer le filtre)
        return [nc.NewsItem(
            title=f"Fed rate decision from {name}",
            url=f"https://x/{name}",
            source=name,
            published=nc.datetime.now(nc.timezone.utc),
            summary="FOMC inflation outlook",
        )]

    monkeypatch.setattr(nc, "_fetch_rss", fake_fetch_rss)
    monkeypatch.setattr(nc, "_collect_structured", lambda **kwargs: [])

    result = nc.collect_all()

    polled_names = {n for n, _ in polled_urls}
    # Mainstream pollés (hors Reuters)
    assert "bbc_business" in polled_names
    assert "cnbc_economy" in polled_names
    # Early-signal pollés
    assert "eia_today_in_energy" in polled_names
    assert "fed_press_all" in polled_names
    assert "mining_com" in polled_names

    # Total : mainstream actifs (10) + early-signal (16) = 26 feeds RSS pollés
    n_mainstream = len([f for f in config.RSS_FEEDS if not f[0].startswith("reuters_")])
    n_early = len(config.EARLY_SIGNAL_FEEDS)
    assert len(polled_urls) == n_mainstream + n_early

    # Le dédup Jaccard vire les doublons (mêmes titres "Fed rate decision from X")
    # mais comme les titres sont uniques (suffixe nom), tous passent.
    # Filtre finance : "Fed rate decision" + "FOMC" matchent whitelist
    assert len(result["filtered"]) > 0


def test_collect_all_dead_feed_does_not_break_run(monkeypatch):
    """Un feed qui lève une exception → log + skip, les autres continuent."""
    import requests as _rq

    def fake_fetch_rss(name, url, **kwargs):
        if name == "eia_today_in_energy":
            raise _rq.HTTPError("404 dead feed")
        return [nc.NewsItem(
            title=f"Brent oil OPEC {name}",
            url="https://x", source=name,
            published=nc.datetime.now(nc.timezone.utc),
            summary="",
        )]

    monkeypatch.setattr(nc, "_fetch_rss", fake_fetch_rss)
    monkeypatch.setattr(nc, "_collect_structured", lambda **kwargs: [])

    # Ne doit PAS lever
    result = nc.collect_all()

    # Run réussit, autres feeds OK
    assert len(result["filtered"]) > 0
    # Le feed mort n'a contribué aucun item
    sources_collected = {it.source for it in result["raw"]}
    assert "eia_today_in_energy" not in sources_collected


def test_collect_all_cross_source_dedup(monkeypatch):
    """Même titre venant de 2 sources différentes → dédupliqué."""
    def fake_fetch_rss(name, url, **kwargs):
        # Tous les feeds renvoient le MÊME titre
        return [nc.NewsItem(
            title="Fed hikes rates by 25 basis points",
            url=f"https://x/{name}", source=name,
            published=nc.datetime.now(nc.timezone.utc),
            summary="FOMC inflation",
        )]

    monkeypatch.setattr(nc, "_fetch_rss", fake_fetch_rss)
    monkeypatch.setattr(nc, "_collect_structured", lambda **kwargs: [])

    result = nc.collect_all()

    # Beaucoup de raw (1 par feed), mais dédup → 1 seul deduped
    assert len(result["raw"]) > 5
    assert len(result["deduped"]) == 1


def test_collect_all_structured_integrated_in_pipeline(monkeypatch):
    """Les items GNews/NewsAPI passent le filtre finance + dédup au même titre."""
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url, **kwargs: [])

    def fake_structured(**kwargs):
        return [
            nc.NewsItem(
                title="OPEC announces production cut to support oil prices",
                url="https://gnews/x", source="gnews",
                published=nc.datetime.now(nc.timezone.utc),
                summary="Brent crude rallies",
            ),
            # Sport blacklisté → doit être filtré
            nc.NewsItem(
                title="Premier League football star buys Tesla shares",
                url="https://gnews/y", source="gnews",
                published=nc.datetime.now(nc.timezone.utc),
                summary="",
            ),
        ]

    monkeypatch.setattr(nc, "_collect_structured", fake_structured)

    result = nc.collect_all()

    titles_filtered = [it.title for it in result["filtered"]]
    assert any("OPEC" in t for t in titles_filtered)
    assert not any("football" in t.lower() for t in titles_filtered)


def test_collect_all_blacklist_applied_uniformly(monkeypatch):
    """Blacklist appliquée sur mainstream + early-signal + structured."""
    def fake_fetch_rss(name, url, **kwargs):
        return [nc.NewsItem(
            title="Royal wedding shocker — King attends NBA game",
            url="https://x", source=name,
            published=nc.datetime.now(nc.timezone.utc),
            summary="",
        )]

    monkeypatch.setattr(nc, "_fetch_rss", fake_fetch_rss)
    monkeypatch.setattr(nc, "_collect_structured", lambda **kwargs: [])

    result = nc.collect_all()
    # Tout est blacklisté
    assert len(result["filtered"]) == 0
    assert result["skipped_non_finance"] > 0
