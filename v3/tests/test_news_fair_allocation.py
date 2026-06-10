"""Tests Lot E — répartition équitable des extractions + fraîcheur à l'ingestion.

Couvre les deux fixes du diagnostic v3/audit/news-coverage-diagnostic.md :
1. `_round_robin_by_source` : les flux de QUEUE (silver/vix/nasdaq) ne sont plus
   affamés par la troncature FIFO MAX_EXTRACTIONS_PER_CYCLE.
2. `_is_too_old` : les articles à pubDate ancien (archive Google News RSS) sont
   écartés à l'ingestion.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

# Stub feedparser si absent en sandbox CI (cf. test_ingestion.py). En prod
# (GitHub Actions) feedparser est installé via requirements.
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    fp_stub = types.ModuleType("feedparser")
    fp_stub.parse = lambda content: types.SimpleNamespace(entries=[])
    sys.modules["feedparser"] = fp_stub

import agent_news as an  # noqa: E402
import news_collector as nc  # noqa: E402
from news_collector import NewsItem  # noqa: E402


def _item(source, title="t", age_days=0):
    pub = datetime.now(timezone.utc) - timedelta(days=age_days)
    return NewsItem(title=title, url="http://x", source=source, published=pub)


# ---------------------------------------------------------------------------
# 1. Round-robin par source
# ---------------------------------------------------------------------------

def test_round_robin_is_a_permutation():
    items = [_item("head", f"h{i}") for i in range(100)] + [_item("tail_silver", "s1")]
    out = an._round_robin_by_source(items)
    assert len(out) == len(items)
    assert {id(x) for x in out} == {id(x) for x in items}  # mêmes objets


def test_round_robin_serves_tail_feed_within_budget():
    # Simule la prod : 90 items de tête + 1 flux dédié en queue. FIFO[:5] le rate.
    items = [_item("head", f"h{i}") for i in range(90)] + [_item("gnews_silver_industrial", "silver")]
    rr = an._round_robin_by_source(items)
    # Le flux de queue passe dans les 2 premiers (round-robin : 1 par source/tour).
    top = rr[:2]
    assert any(it.source == "gnews_silver_industrial" for it in top), \
        "le flux de queue doit être servi dès le 1er tour de table"


def test_round_robin_preserves_intra_source_order():
    items = [_item("a", "a1"), _item("a", "a2"), _item("b", "b1")]
    rr = an._round_robin_by_source(items)
    a_titles = [it.title for it in rr if it.source == "a"]
    assert a_titles == ["a1", "a2"]  # ordre intra-source conservé


def test_max_default_raised_and_cost_safe():
    # Garde-fou : le débit relevé reste sous le soft cap coût.
    # 240/cycle × 3 cycles × ~$0.0003/extraction ≈ $0.22/j < soft cap $0.50.
    assert an.MAX_EXTRACTIONS_PER_CYCLE == 240
    est_cost_per_day = an.MAX_EXTRACTIONS_PER_CYCLE * 3 * 0.0003
    assert est_cost_per_day < 0.50, "le débit doit rester sous le soft cap coût"


# ---------------------------------------------------------------------------
# 2. Fraîcheur à l'ingestion
# ---------------------------------------------------------------------------

def test_is_too_old_filters_archive(monkeypatch):
    monkeypatch.setattr(nc, "INGEST_MAX_AGE_DAYS", 30)
    assert nc._is_too_old(_item("gnews_coffee", age_days=400)) is True   # archive 2022
    assert nc._is_too_old(_item("gnews_coffee", age_days=5)) is False    # frais


def test_freshness_filter_disabled_when_zero(monkeypatch):
    monkeypatch.setattr(nc, "INGEST_MAX_AGE_DAYS", 0)
    assert nc._is_too_old(_item("x", age_days=9999)) is False  # filtre off


def test_is_too_old_no_invention_on_missing_date(monkeypatch):
    monkeypatch.setattr(nc, "INGEST_MAX_AGE_DAYS", 30)
    bad = NewsItem(title="t", url="u", source="s", published=None)  # type: ignore
    assert nc._is_too_old(bad) is False  # pas de date → on n'écarte pas (zéro invention)
