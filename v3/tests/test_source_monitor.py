"""Tests source_monitor — santé des flux news par cycle.

Couvre :
- record_call : appelé / OK / échec / items_fetched cumulés multi-requêtes
- record_skip : flux non appelé (pas de clé API) → distinct d'un échec
- set_items_kept : distinction items_fetched (bruts) vs items_kept (post-filtre)
- write_source_health : tableau markdown généré, lignes triées (ko/muet d'abord)
- render_briefing_block : extrait synthèse + flux à problème pour bulletin
- Intégration : collect_all populate le monitor (RSS OK + RSS KO + skip API)
- Diagnostic muet : flux qui reçoit 30 items mais 0 gardé → raison renseignée
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Stub feedparser si absent (sandbox CI sans sgmllib3k).
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    fp_stub = types.ModuleType("feedparser")
    fp_stub.parse = lambda content: types.SimpleNamespace(entries=[])
    sys.modules["feedparser"] = fp_stub

import news_collector as nc  # noqa: E402
from source_monitor import (  # noqa: E402
    SourceMonitor,
    render_briefing_block,
    read_summary,
    write_source_health,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "titles_cache.db"
    monkeypatch.setattr(nc, "DB_PATH", db)
    yield


# ============================================================
# Unit — SourceMonitor (modèle pur)
# ============================================================

def test_record_call_ok_basic():
    m = SourceMonitor()
    m.record_call("bbc_business", ok=True, http_status="200", items_fetched=12)
    h = m.by_name["bbc_business"]
    assert h.called is True
    assert h.ok is True
    assert h.http_status == "200"
    assert h.items_fetched == 12
    assert h.items_kept == 0
    assert h.status_icon() == "⚪"  # tant que items_kept=0 → muet


def test_record_call_ko_captures_reason():
    m = SourceMonitor()
    m.record_call("dead_feed", ok=False, http_status="403",
                  items_fetched=0, reason="HTTP 403")
    h = m.by_name["dead_feed"]
    assert h.ok is False
    assert h.status_icon() == "❌"
    assert h.reason == "HTTP 403"


def test_record_call_aggregation_multi_requests():
    """gnews fait N requêtes — items_fetched doit s'additionner."""
    m = SourceMonitor()
    m.record_call("gnews", ok=True, http_status="200", items_fetched=10)
    m.record_call("gnews", ok=True, http_status="200", items_fetched=15)
    m.record_call("gnews", ok=True, http_status="200", items_fetched=5)
    h = m.by_name["gnews"]
    assert h.items_fetched == 30
    assert h.ok is True


def test_record_call_aggregation_one_failure_marks_partial():
    """Ticket A : si une requête échoue mais d'autres réussissent, le flux est
    PARTIEL (pas une panne) — les items des requêtes OK arrivent quand même.
    """
    m = SourceMonitor()
    m.record_call("gnews", ok=True, http_status="200", items_fetched=10)
    m.record_call("gnews", ok=False, http_status="429",
                  items_fetched=0, reason="rate limit", query="gold price")
    h = m.by_name["gnews"]
    # ok global = au moins une requête a abouti → non-panne.
    assert h.ok is True
    assert h.is_partial() is True
    assert h.status_icon() == "⚠️"
    assert h.status_label() == "partiel (1/2)"
    # La trace de la requête fautive est conservée pour diagnostic.
    assert "gold price" in h.failed_requests


def test_record_skip_distinct_from_failure():
    """Pas de clé API ≠ échec : on track séparément."""
    m = SourceMonitor()
    m.record_skip("newsapi", reason="pas de clé API (NEWSAPI_KEY absent)")
    h = m.by_name["newsapi"]
    assert h.called is False
    assert h.http_status == "skip"
    assert h.status_icon() == "⏭"
    s = m.summary()
    assert s["skip"] == 1
    assert s["called"] == 0
    assert s["ko"] == 0


def test_set_items_kept_distingue_fetched_vs_kept():
    """RÈGLE CRUCIALE : items_fetched (bruts API) vs items_kept (post-filtre).
    Un flux qui reçoit 30 items mais dont 0 passe le filtre finance est MUET
    par le filtre, pas par l'API.
    """
    m = SourceMonitor()
    m.record_call("gnews_cac40", ok=True, http_status="200", items_fetched=30)
    m.set_items_kept({"gnews_cac40": 0})
    h = m.by_name["gnews_cac40"]
    assert h.items_fetched == 30  # API a renvoyé
    assert h.items_kept == 0      # filtre a tout jeté
    assert h.status_icon() == "⚪"  # muet (appelé OK mais 0 utile)
    assert "30 reçus" in h.reason
    assert "0 gardés" in h.reason


def test_set_items_kept_zero_recus():
    """Distinction : 0 reçus (API vide) vs 0 gardés (filtre rejette)."""
    m = SourceMonitor()
    m.record_call("dead_query", ok=True, http_status="200", items_fetched=0)
    m.set_items_kept({"dead_query": 0})
    h = m.by_name["dead_query"]
    assert h.items_fetched == 0
    assert h.reason == "0 reçus"


def test_summary_counts():
    m = SourceMonitor()
    m.record_call("ok_feed", ok=True, http_status="200", items_fetched=5)
    m.record_call("muet_feed", ok=True, http_status="200", items_fetched=10)
    m.record_call("ko_feed", ok=False, http_status="403", items_fetched=0)
    m.record_skip("no_key_feed", reason="pas de clé")
    m.set_items_kept({"ok_feed": 5, "muet_feed": 0, "ko_feed": 0})
    s = m.summary()
    assert s["total"] == 4
    assert s["called"] == 3
    assert s["ok"] == 2
    assert s["partiel"] == 0  # aucune source multi-requêtes ici
    assert s["ko"] == 1
    assert s["muet"] == 1
    assert s["skip"] == 1
    assert s["items_fetched"] == 15  # 5+10+0
    assert s["items_kept"] == 5


# ============================================================
# Unit — Statut 3 états (Ticket A : OK / partiel R/N / ❌)
# ============================================================

def test_three_states_all_ok():
    """Toutes les requêtes réussissent → OK, pas partiel."""
    m = SourceMonitor()
    for _ in range(14):
        m.record_call("gnews", ok=True, http_status="200", items_fetched=20)
    h = m.by_name["gnews"]
    assert h.req_total == 14
    assert h.req_ok == 14
    assert h.req_ko == 0
    assert h.is_partial() is False
    assert h.ok is True
    m.set_items_kept({"gnews": 250})
    assert h.status_icon() == "✅"
    assert h.status_label() == "OK"


def test_three_states_partial_13_of_14():
    """Exemple du ticket : GNews 1 requête sur 14 échoue → partiel (13/14),
    PAS une panne (les 13 autres ont livré des items).
    """
    m = SourceMonitor()
    for i in range(13):
        m.record_call("gnews", ok=True, http_status="200",
                      items_fetched=20, query=f"q{i}")
    m.record_call("gnews", ok=False, http_status="400",
                  items_fetched=0, reason="HTTP 400", query="silver_industrial")
    h = m.by_name["gnews"]
    assert h.req_total == 14
    assert h.req_ok == 13
    assert h.req_ko == 1
    assert h.is_partial() is True
    assert h.ok is True  # non-panne : des données utiles arrivent
    assert h.status_icon() == "⚠️"
    assert h.status_label() == "partiel (13/14)"
    assert h.items_fetched == 13 * 20
    # Diagnostic : ratio + requête fautive dans la raison.
    assert "1/14 requêtes en échec" in h.reason
    assert "silver_industrial" in h.reason
    # set_items_kept ne doit pas écraser la raison de diagnostic du partiel.
    m.set_items_kept({"gnews": 240})
    assert h.items_kept == 240
    assert "silver_industrial" in h.reason
    s = m.summary()
    assert s["partiel"] == 1
    assert s["ok"] == 0
    assert s["ko"] == 0


def test_three_states_total_failure_is_ko():
    """Toutes les requêtes échouent (0 item) → ❌ panne réelle, pas partiel."""
    m = SourceMonitor()
    for i in range(14):
        m.record_call("gnews", ok=False, http_status="401",
                      items_fetched=0, reason="auth invalide", query=f"q{i}")
    h = m.by_name["gnews"]
    assert h.req_total == 14
    assert h.req_ok == 0
    assert h.req_ko == 14
    assert h.is_partial() is False  # 0 succès → pas un mix → panne
    assert h.ok is False
    assert h.status_icon() == "❌"
    assert h.status_label() == "échec"
    s = m.summary()
    assert s["ko"] == 1
    assert s["partiel"] == 0


def test_partial_capped_failed_requests_in_reason():
    """Plus de 3 requêtes fautives → raison plafonnée à 3 + '…'."""
    m = SourceMonitor()
    for i in range(10):
        m.record_call("gnews", ok=True, http_status="200",
                      items_fetched=5, query=f"ok{i}")
    for i in range(5):
        m.record_call("gnews", ok=False, http_status="429",
                      items_fetched=0, reason="rate limit", query=f"ko{i}")
    h = m.by_name["gnews"]
    assert h.is_partial() is True
    assert h.status_label() == "partiel (10/15)"
    assert "5/15 requêtes en échec" in h.reason
    assert "…" in h.reason  # plus de 3 → tronqué


def test_partial_not_in_briefing_problems(tmp_path):
    """Le partiel n'apparaît PAS dans 'Flux à problème' (pas une panne) mais
    dans une section dédiée 'Flux partiels'.
    """
    m = SourceMonitor()
    for i in range(13):
        m.record_call("gnews", ok=True, http_status="200",
                      items_fetched=10, query=f"q{i}")
    m.record_call("gnews", ok=False, http_status="400",
                  items_fetched=0, reason="HTTP 400", query="badq")
    m.record_call("dead_feed", ok=False, http_status="500",
                  items_fetched=0, reason="HTTP 500")
    m.set_items_kept({"gnews": 120, "dead_feed": 0})

    out = tmp_path / "source-health.md"
    write_source_health(m, out)
    block = render_briefing_block(out)

    problem_block = block.split("**Flux à problème :**")[1].split("**Flux partiels**")[0]
    assert "dead_feed" in problem_block
    assert "gnews" not in problem_block  # partiel ≠ panne
    assert "**Flux partiels**" in block
    partial_block = block.split("**Flux partiels**")[1]
    assert "gnews" in partial_block


def test_write_source_health_has_status_column_and_legend(tmp_path):
    """Le tableau a une colonne Statut + une légende mentionnant le partiel."""
    m = SourceMonitor()
    for i in range(14):
        ok = i != 0
        m.record_call("gnews", ok=ok, http_status="200" if ok else "400",
                      items_fetched=10 if ok else 0,
                      reason="" if ok else "HTTP 400",
                      query=f"q{i}")
    m.set_items_kept({"gnews": 130})
    out = tmp_path / "source-health.md"
    write_source_health(m, out)
    txt = out.read_text(encoding="utf-8")
    assert "| Statut |" in txt
    assert "partiel" in txt.lower()
    assert "⚠️" in txt
    assert "1 partiels" in txt  # la synthèse compte le flux partiel


# ============================================================
# Unit — Persistance source-health.md
# ============================================================

def test_write_source_health_writes_table(tmp_path):
    m = SourceMonitor()
    m.record_call("bbc_business", ok=True, http_status="200", items_fetched=12)
    m.record_call("dead_feed", ok=False, http_status="403",
                  items_fetched=0, reason="HTTP 403")
    m.record_skip("newsapi", reason="pas de clé API")
    m.set_items_kept({"bbc_business": 8, "dead_feed": 0})

    out = tmp_path / "source-health.md"
    write_source_health(m, out)

    txt = out.read_text(encoding="utf-8")
    assert "# Santé des sources news" in txt
    assert "**Synthèse**" in txt
    assert "bbc_business" in txt
    assert "dead_feed" in txt
    assert "newsapi" in txt
    assert "HTTP 403" in txt
    # Tri : ko en premier
    pos_ko = txt.find("| ❌ ")
    pos_ok = txt.find("| ✅ ")
    assert pos_ko < pos_ok, "Flux KO doit apparaître avant les OK (priorité debug)"


def test_render_briefing_block_extracts_synthese_and_problems(tmp_path):
    m = SourceMonitor()
    m.record_call("ok_feed", ok=True, http_status="200", items_fetched=5)
    m.record_call("muet_feed", ok=True, http_status="200", items_fetched=30)
    m.record_call("ko_feed", ok=False, http_status="500",
                  items_fetched=0, reason="HTTP 500")
    m.set_items_kept({"ok_feed": 5, "muet_feed": 0, "ko_feed": 0})

    out = tmp_path / "source-health.md"
    write_source_health(m, out)
    block = render_briefing_block(out)

    assert "## Santé des sources" in block
    assert "ko_feed" in block
    assert "muet_feed" in block
    assert "HTTP 500" in block
    # ok_feed ne doit PAS apparaître dans la liste des problèmes
    # (mais peut apparaître dans la synthèse, donc on vérifie le bloc "Flux à problème")
    problem_block = block.split("**Flux à problème :**")[1] if "**Flux à problème :**" in block else ""
    assert "ok_feed" not in problem_block


def test_render_briefing_block_no_file(tmp_path):
    """Pas de source-health.md → bloc minimal, pas de crash."""
    block = render_briefing_block(tmp_path / "absent.md")
    assert "## Santé des sources" in block
    assert "indisponible" in block.lower()


def test_read_summary_counts_icons(tmp_path):
    m = SourceMonitor()
    m.record_call("ok1", ok=True, http_status="200", items_fetched=5)
    m.record_call("ok2", ok=True, http_status="200", items_fetched=5)
    m.record_call("ko1", ok=False, http_status="403", items_fetched=0)
    m.record_skip("skip1", reason="x")
    m.set_items_kept({"ok1": 5, "ok2": 0, "ko1": 0})  # ok2 muet

    out = tmp_path / "source-health.md"
    write_source_health(m, out)

    s = read_summary(out)
    assert s["ok"] == 1   # ok1 (kept>0)
    assert s["muet"] == 1  # ok2 (kept=0)
    assert s["ko"] == 1
    assert s["skip"] == 1
    assert "synthese" in s


# ============================================================
# Intégration — collect_all avec monitor
# ============================================================

def _mock_response(status_code=200, content=b""):
    m = MagicMock()
    m.status_code = status_code
    m.content = content
    m.raise_for_status = MagicMock() if status_code < 400 else MagicMock(
        side_effect=__import__("requests").HTTPError(f"{status_code}")
    )
    return m


def test_collect_all_populates_monitor(monkeypatch):
    """End-to-end : collect_all branche le monitor sur tous les fetchs.
    On mock requests.get pour simuler 1 RSS OK + 1 RSS KO + skip API keys.
    """
    # Force pas de clés API → skip propre
    monkeypatch.delenv("GNEWS_API_KEY", raising=False)
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)

    # Stub RSS_FEEDS et EARLY_SIGNAL_FEEDS pour un test rapide
    monkeypatch.setattr(nc, "RSS_FEEDS", [
        ("test_ok", "https://x/ok.rss", 900),
        ("test_ko", "https://x/dead.rss", 900),
    ])
    monkeypatch.setattr(nc, "EARLY_SIGNAL_FEEDS", [])

    # feedparser stub : retourne 0 entries (peu importe, on teste le monitor)
    import types
    fp_stub = types.SimpleNamespace(entries=[])
    monkeypatch.setattr("feedparser.parse", lambda c: fp_stub)

    def fake_get(url, **kw):
        if "ok.rss" in url:
            return _mock_response(200, b"<rss></rss>")
        return _mock_response(403, b"forbidden")

    monkeypatch.setattr("requests.get", fake_get)

    result = nc.collect_all(commit_seen=False)
    assert "monitor" in result
    m = result["monitor"]
    assert "test_ok" in m.by_name
    assert "test_ko" in m.by_name
    # Skip API : gnews ET newsapi tous deux skip car pas de clé
    assert "gnews" in m.by_name
    assert "newsapi" in m.by_name
    assert m.by_name["gnews"].http_status == "skip"
    assert m.by_name["newsapi"].http_status == "skip"
    # test_ok appelé OK (mais 0 entries → muet)
    assert m.by_name["test_ok"].called is True
    assert m.by_name["test_ok"].ok is True
    # test_ko en échec HTTP 403
    assert m.by_name["test_ko"].called is True
    assert m.by_name["test_ko"].ok is False
    assert "403" in m.by_name["test_ko"].http_status


def test_collect_all_distingue_fetched_vs_kept_via_filtre(monkeypatch):
    """Simule un flux qui reçoit 3 items dont 0 passe le filtre finance.
    Vérifie que items_fetched=3 mais items_kept=0 (muet PAR le filtre).
    """
    monkeypatch.delenv("GNEWS_API_KEY", raising=False)
    monkeypatch.delenv("NEWSAPI_KEY", raising=False)
    monkeypatch.setattr(nc, "RSS_FEEDS", [("noise_feed", "https://x/noise.rss", 900)])
    monkeypatch.setattr(nc, "EARLY_SIGNAL_FEEDS", [])

    # 3 entries non-finance (ne matchent ni blacklist ni whitelist)
    import types
    entries = [
        types.SimpleNamespace(get=lambda k, d="": {
            "title": "Local bakery opens new shop downtown",
            "link": "http://x/1", "summary": "", "published_parsed": None,
            "updated_parsed": None,
        }.get(k, d)),
        types.SimpleNamespace(get=lambda k, d="": {
            "title": "Weather forecast for tomorrow looks pleasant",
            "link": "http://x/2", "summary": "", "published_parsed": None,
            "updated_parsed": None,
        }.get(k, d)),
        types.SimpleNamespace(get=lambda k, d="": {
            "title": "School fair planned for next weekend in the village",
            "link": "http://x/3", "summary": "", "published_parsed": None,
            "updated_parsed": None,
        }.get(k, d)),
    ]
    monkeypatch.setattr("feedparser.parse",
                        lambda c: types.SimpleNamespace(entries=entries))
    monkeypatch.setattr("requests.get",
                        lambda url, **kw: _mock_response(200, b"<rss/>"))

    result = nc.collect_all(commit_seen=False)
    m = result["monitor"]
    h = m.by_name["noise_feed"]
    assert h.called is True
    assert h.ok is True
    assert h.items_fetched == 3, "API a bien renvoyé 3 items"
    assert h.items_kept == 0, "Filtre finance a tout jeté"
    # La raison doit expliquer le delta
    assert "3 reçus" in h.reason
    assert "0 gardés" in h.reason


# ============================================================
# Régression — whitelist finance FR (fix gnews_cac40 muet)
# ============================================================

def test_whitelist_accepts_french_finance_terms():
    """Fix 31/05 : un titre FR mentionnant 'bourse' ou 'Euronext' doit passer
    la whitelist finance, sinon gnews_cac40 reste muet.
    """
    assert nc.is_finance_relevant("Cotation Bourse Euronext Paris du jour", "")
    assert nc.is_finance_relevant("LVMH publie ses résultats annuels", "")
    assert nc.is_finance_relevant("TotalEnergies en hausse de 3%", "")
    assert nc.is_finance_relevant(
        "La BCE relève son taux directeur de 25 points de base", "")
    assert nc.is_finance_relevant("Crédit Agricole rachète une filiale", "")
    # Anti-faux-positif : un titre lifestyle ne doit pas passer même en FR
    assert not nc.is_finance_relevant("Recette de la semaine : tarte aux pommes", "")


def test_investing_stocks_url_not_duplicate_of_econ():
    """Régression : avant fix, investing_stocks pointait vers news_25.rss
    (= dup de investing_econ) → 100% dédupliqué → muet. Doit être distinct.
    """
    import config
    by_name = {n: u for n, u, _ in config.RSS_FEEDS}
    assert by_name["investing_stocks"] != by_name["investing_econ"], (
        "investing_stocks ne doit plus dupliquer investing_econ"
    )
