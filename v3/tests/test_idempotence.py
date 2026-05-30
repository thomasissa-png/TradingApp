"""Tests Idempotence — agent_news + news_collector (cf. audit-ia §1).

Vérifie que :
- collect_all(commit_seen=False) NE marque PAS les titres comme vus dans la DB.
- collect_all(commit_seen=True) (rétro-compat) marque bien comme vus.
- mark_title_seen() committe explicitement un titre.
- Sur erreur d'extraction LLM, le titre n'est PAS dédupé → ré-extrait au cycle suivant.
- Sur extracteur DELIBERATELY off (pas de key OU hard cap), le titre EST dédupé
  (mode dégradé volontaire, aucune ré-extraction attendue).
- Sur succès d'extraction, le titre EST dédupé.
- Bonus : si l'extracteur passe de KO à OK entre 2 cycles, le titre PERDU au
  cycle 1 (erreur) est bien RE-traité au cycle 2 (succès).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Stub feedparser si absent (sandbox CI)
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    fp_stub = types.ModuleType("feedparser")
    fp_stub.parse = lambda *_a, **_kw: type("R", (), {"entries": []})()  # type: ignore
    sys.modules["feedparser"] = fp_stub

import agent_news  # noqa: E402
import news_collector as nc  # noqa: E402
from extractor import ExtractedEvent, Impact  # noqa: E402


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    """Isole le cache dédup SQLite par test."""
    db = tmp_path / "titles_cache.db"
    monkeypatch.setattr(nc, "DB_PATH", db)
    yield


def _mk_item(title: str, source: str = "test_feed") -> nc.NewsItem:
    return nc.NewsItem(
        title=title,
        url=f"https://x/{title[:20]}",
        source=source,
        published=datetime.now(timezone.utc),
        summary="",
    )


# ============================================================
# news_collector — commit_seen toggle
# ============================================================

def test_collect_all_commit_seen_false_does_not_persist(monkeypatch):
    """commit_seen=False → titres filtrés mais NON marqués vus en DB."""
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("Fed hikes rates 25bps OPEC oil", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    r1 = nc.collect_all(commit_seen=False)
    assert len(r1["filtered"]) >= 1

    # 2e collecte : le même titre passe ENCORE le dédup (rien n'a été marqué)
    r2 = nc.collect_all(commit_seen=False)
    assert len(r2["filtered"]) >= 1
    assert r2["filtered"][0].title == r1["filtered"][0].title


def test_collect_all_commit_seen_true_persists(monkeypatch):
    """commit_seen=True (défaut historique) → 2e collecte dédupliqué."""
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("Fed hikes rates 25bps OPEC oil", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    r1 = nc.collect_all(commit_seen=True)
    assert len(r1["filtered"]) >= 1

    r2 = nc.collect_all(commit_seen=True)
    # Tous dédupliqués → 0 filtered au cycle 2
    assert len(r2["filtered"]) == 0


def test_mark_title_seen_commits(monkeypatch):
    """mark_title_seen() explicite → le titre est ensuite dédupliqué."""
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("Brent crude rallies OPEC cut", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    r1 = nc.collect_all(commit_seen=False)
    item = r1["filtered"][0]

    # On marque explicitement vu
    nc.mark_title_seen(item)

    # 2e collecte → dédupliqué
    r2 = nc.collect_all(commit_seen=False)
    assert len(r2["filtered"]) == 0


# ============================================================
# agent_news.run_one_cycle — idempotence sur erreur LLM
# ============================================================

class _FakeExtractor:
    """Extracteur factice : programme la séquence d'outputs par appel."""

    def __init__(self, outputs):
        self._outputs = list(outputs)
        self._calls = 0
        self._enabled = True

    def is_enabled(self):
        return self._enabled

    def extract(self, title, snippet=""):
        self._calls += 1
        if not self._outputs:
            return ExtractedEvent(trigger=title[:200], error="no more programmed outputs")
        return self._outputs.pop(0)

    def get_stats(self):
        return {"enabled": self._enabled, "calls": self._calls}


class _FakePublisher:
    def __init__(self):
        self.lines = []

    def append_to_events_log(self, lines):
        self.lines.extend(lines)


def test_extraction_error_does_not_dedupe(monkeypatch):
    """Cœur du fix idempotence : extraction KO → titre NON marqué vu →
    réapparaît au cycle suivant pour ré-extraction.
    """
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("Fed FOMC inflation outlook critical", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    # Cycle 1 : l'extracteur retourne une ERREUR (ex: JSON tronqué)
    extractor_ko = _FakeExtractor(outputs=[
        ExtractedEvent(trigger="Fed FOMC", error="invalid JSON: truncated"),
    ] * 50)  # autant qu'on en a besoin
    pub = _FakePublisher()

    stats1 = agent_news.run_one_cycle(pub, extractor_ko)
    assert stats1["errors"] >= 1
    assert stats1["retry_pending"] >= 1
    # Une ligne brute a été écrite (pas de perte de trace)
    assert len(pub.lines) >= 1

    # Cycle 2 : MÊME extraction relancée → l'item ré-apparaît dans filtered
    # car NON marqué vu au cycle 1
    extractor_ok = _FakeExtractor(outputs=[
        ExtractedEvent(
            impacts=[Impact(asset="SP500", direction="SHORT", confidence="medium")],
            category="central_bank",
            trigger="Fed FOMC",
            news_zone="US",
            reliability="reported",
            materiality="medium",
        ),
    ] * 50)
    pub2 = _FakePublisher()
    stats2 = agent_news.run_one_cycle(pub2, extractor_ok)
    # L'item a été RE-traité (preuve d'idempotence : pas de perte silencieuse)
    assert stats2["filtered"] >= 1
    assert stats2["errors"] == 0
    assert extractor_ok._calls >= 1


def test_extraction_success_dedupes(monkeypatch):
    """Extraction OK → titre marqué vu → cycle 2 ne le revoit pas."""
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("OPEC announces production cut Brent", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    extractor = _FakeExtractor(outputs=[
        ExtractedEvent(
            impacts=[Impact(asset="BRENT", direction="LONG", confidence="high")],
            category="commodity",
            trigger="OPEC cut",
            news_zone="Global",
            reliability="confirmed",
            materiality="high",
        ),
    ] * 50)
    pub = _FakePublisher()

    stats1 = agent_news.run_one_cycle(pub, extractor)
    assert stats1["filtered"] >= 1
    assert stats1["errors"] == 0

    # Cycle 2 : titre dédupé
    extractor2 = _FakeExtractor(outputs=[])
    pub2 = _FakePublisher()
    stats2 = agent_news.run_one_cycle(pub2, extractor2)
    assert stats2["filtered"] == 0
    assert extractor2._calls == 0  # rien à extraire


def test_extractor_deliberately_off_dedupes(monkeypatch):
    """Extracteur DELIBERATELY off (pas de key, hard cap) → ligne brute écrite
    ET titre marqué vu (mode dégradé volontaire, pas de retry attendu).
    """
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("Gold hits record on Fed dovish pivot", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    extractor_off = _FakeExtractor(outputs=[])
    extractor_off._enabled = False
    pub = _FakePublisher()

    stats1 = agent_news.run_one_cycle(pub, extractor_off)
    assert stats1["filtered"] >= 1
    # Une ligne brute a été écrite
    assert len(pub.lines) >= 1

    # Cycle 2 : titre dédupé (mode off = pas de retry)
    extractor_off2 = _FakeExtractor(outputs=[])
    extractor_off2._enabled = False
    pub2 = _FakePublisher()
    stats2 = agent_news.run_one_cycle(pub2, extractor_off2)
    assert stats2["filtered"] == 0


def test_hard_cap_midbatch_dedupes(monkeypatch):
    """Hard cap atteint en cours de batch → ExtractedEvent.error contient
    'disabled' → ligne brute + mark_title_seen (mode dégradé volontaire).
    """
    monkeypatch.setattr(nc, "_fetch_rss", lambda name, url: [
        _mk_item("Iran strikes Brent oil rallies geopolitical", name)
    ])
    monkeypatch.setattr(nc, "_collect_structured", lambda: [])

    extractor = _FakeExtractor(outputs=[
        ExtractedEvent(trigger="Iran", error="extractor disabled or hard-capped"),
    ] * 50)
    pub = _FakePublisher()

    stats1 = agent_news.run_one_cycle(pub, extractor)
    assert stats1["filtered"] >= 1
    # NB : "disabled" dans error → on traite comme mode off délibéré
    assert stats1["errors"] == 0  # pas compté en erreur retry
    assert stats1["retry_pending"] == 0

    # Cycle 2 : titre dédupé
    extractor2 = _FakeExtractor(outputs=[])
    pub2 = _FakePublisher()
    stats2 = agent_news.run_one_cycle(pub2, extractor2)
    assert stats2["filtered"] == 0
