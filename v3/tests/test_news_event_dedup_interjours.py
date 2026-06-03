"""Dédup INTER-JOURS news — cœur Phase 2 (#4, validé fondateur).

Problème adressé : une même actu (Nvidia, SoftBank…) génère des articles sur
plusieurs jours et était RECOMPTÉE jour après jour → gonflait le signal news.
La mémoire d'événement inter-jours (event_id + canonicalisation premier-vu)
garantit qu'un événement RÉELLEMENT nouveau passe, mais qu'un repost est skippé.

Couvre nommément les 5 cas du brief :
  (a) même titre 2 jours de suite → compté 1 fois (event_id exact).
  (b) titre quasi-identique (≤15% diff) même actif dans 48h → dédupliqué (flou).
  (c) titre différent / hors fenêtre 48h / autre actif → gardé (pas de faux drop).
  (d) fallback sans rapidfuzz → SHA exact seul fonctionne (mode dégradé).
  (e) event_date dérivé de pubDate RSS (distinct de la date d'ingestion).

Garde-fou central (CONTRAINTE FORTE du brief) : un événement nouveau passe
TOUJOURS ; re-run idempotent (re-jouer le même cycle ne re-skippe pas à tort).
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# Stub feedparser si absent (sandbox CI sans sgmllib3k) — pattern projet standard
# (cf. test_ingestion.py). En prod (GitHub Actions / Replit), feedparser est
# installé via requirements. Garantit que news_collector reste importable et que
# le test (e) est déterministe quel que soit l'ordre d'exécution.
try:
    import feedparser  # noqa: F401
except ImportError:
    import types
    _fp_stub = types.ModuleType("feedparser")
    _fp_stub.parse = lambda content: types.SimpleNamespace(entries=[])
    sys.modules["feedparser"] = _fp_stub

import triggers_classifier as tc  # noqa: E402
from triggers_classifier import compute_event_id  # noqa: E402


def _ev(trigger: str, actif: str, dt: datetime, nature: str = "structurel") -> dict:
    """Fabrique un event minimal au format consommé par _canonicalize_events."""
    return {
        "trigger": trigger,
        "cours": actif,
        "category": "geopolitical",
        "materiality": "high",
        "reliability": "confirmed",
        "nature": nature,
        "event_id": "",
        "event_date": dt.date().isoformat(),
        "_dt": dt,
        "_event_dt": dt,
        "_impacts": [{"asset": actif, "direction": "LONG", "confidence": "high"}],
        "event_date_source": "rss",
    }


# ============================================================
# (a) Même titre 2 jours de suite → compté 1 fois (event_id exact)
# ============================================================

def test_a_same_title_two_days_counted_once():
    """Le MÊME titre+actif ré-ingéré le lendemain partage l'event_id exact :
    l'occurrence J est `kept`, l'occurrence J+1 est `repost` (exclue du scoring),
    et canonical_event_date = J (premier-vu fait foi)."""
    d0 = datetime.now(timezone.utc) - timedelta(days=1)
    d1 = datetime.now(timezone.utc)
    title = "Nvidia signs multi-year chip supply deal with SoftBank"
    events = [_ev(title, "NASDAQ", d0), _ev(title, "NASDAQ", d1)]

    tc._canonicalize_events(events)

    # event_id exact identique (même normalise(trigger)+actif)
    assert events[0]["event_id"] == events[1]["event_id"]
    # canonical = MIN(date) = J0 pour les DEUX occurrences
    assert events[0]["_canonical_dt"].date() == d0.date()
    assert events[1]["_canonical_dt"].date() == d0.date()
    # 1 seule occurrence comptée : J0 kept, J1 repost
    j0 = next(e for e in events if e["_dt"] == d0)
    j1 = next(e for e in events if e["_dt"] == d1)
    assert j0["dedup_status"] == "kept"
    assert j1["dedup_status"] == "repost"
    # Exactement 1 "kept" sur le couple → compté une fois
    assert sum(1 for e in events if e["dedup_status"] == "kept") == 1


# ============================================================
# (b) Titre quasi-identique (≤15%) même actif dans 48h → dédupliqué (flou)
# ============================================================

def test_b_fuzzy_quasi_identical_same_actif_48h_deduped():
    """Deux titres quasi-identiques (≤15% Levenshtein), même actif, dans 48h →
    fusionnés sur le MÊME event_id (le plus ancien gagne) → 1 seul kept."""
    if not tc._RAPIDFUZZ_OK:
        pytest.skip("rapidfuzz indisponible — cas (b) couvert par (d) en mode dégradé")
    dt1 = datetime.now(timezone.utc) - timedelta(hours=4)
    dt2 = datetime.now(timezone.utc) - timedelta(hours=1)
    events = [
        _ev("OPEC+ announces production cut of 2 million bpd", "BRENT", dt1),
        _ev("OPEC+ announces production cut of 2 million b/d", "BRENT", dt2),  # b/d vs bpd
    ]
    tc._canonicalize_events(events)
    assert events[0]["event_id"] == events[1]["event_id"], (
        "Titres quasi-identiques même actif <48h doivent fusionner (dédup floue)"
    )
    assert sum(1 for e in events if e["dedup_status"] == "kept") == 1


# ============================================================
# (c) Titre différent / hors 48h / autre actif → gardé (pas de faux drop)
# ============================================================

def test_c1_different_title_kept():
    """Deux événements sémantiquement différents → 2 event_id distincts, 2 kept.
    CONTRAINTE FORTE : un événement réellement nouveau passe TOUJOURS."""
    now = datetime.now(timezone.utc)
    events = [
        _ev("Iran strikes US base in Iraq", "BRENT", now - timedelta(hours=2)),
        _ev("Fed holds rates steady, signals one cut in 2026", "SP500", now),
    ]
    tc._canonicalize_events(events)
    assert events[0]["event_id"] != events[1]["event_id"]
    assert all(e["dedup_status"] == "kept" for e in events)


def test_c2_same_title_other_actif_kept():
    """Même trigger mais ACTIF différent → event_id différent → les deux gardés
    (un choc géopol peut toucher BRENT ET GOLD : ce ne sont PAS des doublons)."""
    now = datetime.now(timezone.utc)
    title = "Hormuz strait blockade announced by Iran"
    events = [_ev(title, "BRENT", now), _ev(title, "GOLD", now)]
    tc._canonicalize_events(events)
    assert events[0]["event_id"] != events[1]["event_id"]
    assert all(e["dedup_status"] == "kept" for e in events)


def test_c3_fuzzy_outside_48h_window_kept():
    """Titres quasi-identiques même actif mais SÉPARÉS de >48h → PAS fusionnés
    par le flou (la fenêtre 48h borne le coût ET évite de re-merger une vieille
    archive avec une actu fraîche). Chacun garde son propre event_id."""
    if not tc._RAPIDFUZZ_OK:
        pytest.skip("rapidfuzz indisponible — fenêtre 48h non sollicitée en dégradé")
    dt_old = datetime.now(timezone.utc) - timedelta(hours=80)  # hors 48h
    dt_new = datetime.now(timezone.utc)
    events = [
        _ev("OPEC+ announces production cut of 2 million bpd", "BRENT", dt_old),
        _ev("OPEC+ announces production cut of 2 million b/d", "BRENT", dt_new),
    ]
    tc._canonicalize_events(events)
    # Hors fenêtre → le flou ne les fusionne pas, mais comme triggers normalisés
    # diffèrent (bpd vs b d), l'exact ne les fusionne pas non plus → 2 ids distincts.
    assert events[0]["event_id"] != events[1]["event_id"]
    assert all(e["dedup_status"] == "kept" for e in events)


# ============================================================
# (d) Fallback sans rapidfuzz → SHA exact seul (mode dégradé)
# ============================================================

def test_d_fallback_without_rapidfuzz_sha_exact_only(monkeypatch):
    """Si rapidfuzz est indisponible, la dédup EXACTE (event_id SHA-256) doit
    continuer de fonctionner : même titre+actif → repost détecté.
    Le flou est désactivé (degraded_mode=True), sans faire échouer le run."""
    monkeypatch.setattr(tc, "_RAPIDFUZZ_OK", False)
    d0 = datetime.now(timezone.utc) - timedelta(days=1)
    d1 = datetime.now(timezone.utc)
    title = "SoftBank raises stake in Arm to 92 percent"
    events = [_ev(title, "NASDAQ", d0), _ev(title, "NASDAQ", d1)]

    stats = tc._canonicalize_events(events)

    assert stats["degraded_mode"] is True
    # Dédup EXACTE toujours opérante
    assert events[0]["event_id"] == events[1]["event_id"]
    j1 = next(e for e in events if e["_dt"] == d1)
    assert j1["dedup_status"] == "repost"


def test_d_fallback_does_not_fuzzy_merge(monkeypatch):
    """En mode dégradé, deux titres SEULEMENT quasi-identiques (différence
    réelle de caractères) ne sont PAS fusionnés (pas de flou) → 2 kept.
    Prouve que le fallback est purement SHA exact (zéro merge approximatif)."""
    monkeypatch.setattr(tc, "_RAPIDFUZZ_OK", False)
    dt1 = datetime.now(timezone.utc) - timedelta(hours=2)
    dt2 = datetime.now(timezone.utc) - timedelta(hours=1)
    events = [
        _ev("OPEC+ announces production cut of 2 million bpd", "BRENT", dt1),
        _ev("OPEC+ announces production cut of 2 million b/d", "BRENT", dt2),
    ]
    tc._canonicalize_events(events)
    # SHA exact : triggers normalisés diffèrent → ids distincts → pas de drop
    assert events[0]["event_id"] != events[1]["event_id"]
    assert all(e["dedup_status"] == "kept" for e in events)


# ============================================================
# (e) event_date dérivé de pubDate RSS (≠ date d'ingestion)
# ============================================================

def test_e_event_date_from_pubdate_via_news_item():
    """NewsItem.as_event_log_line_extracted écrit event_date = pubDate RSS,
    distincte de la date d'ingestion (premier-vu calculé en aval)."""
    from news_collector import NewsItem
    from extractor import ExtractedEvent, Impact

    pub = datetime(2026, 5, 30, 8, 30, tzinfo=timezone.utc)
    item = NewsItem(
        title="Iran strikes US base, Brent jumps 5%",
        url="https://example.com/x",
        source="reuters",
        published=pub,
    )
    extracted = ExtractedEvent(
        impacts=[Impact(asset="BRENT", direction="LONG", confidence="high")],
        category="geopolitical",
        trigger="Frappes iraniennes sur base US",
        materiality="high",
        reliability="confirmed",
        nature="structurel",
    )
    line = item.as_event_log_line_extracted(extracted)
    # Ligne markdown "| c1 | c2 | ... | c19 |" → split sur | puis drop bords vides.
    parts = line.split("|")
    cols = [c.strip() for c in parts[1:-1]]
    # 19 colonnes schéma v2.2 : event_date en position 16 (index 15)
    assert len(cols) == 19
    assert cols[0] == "2026-05-30"           # date d'ingestion = pubDate ici
    assert cols[15] == "2026-05-30"          # event_date = pubDate RSS
    # event_id présent et de longueur 12 (SHA-256 tronqué)
    assert len(cols[14]) == 12


def test_e_event_date_parsed_source_rss_vs_fallback():
    """parse_events_log distingue event_date_source 'rss' (pubDate parsable)
    de 'fallback' (date d'ingestion) — la fraîcheur ne peut pas être faussée."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as f:
        f.write("| date | l1 | l2 | trigger | cours | latence | r | source | news_zone | category | pattern_id | impacts | materiality | reliability | event_id | event_date | nature | dedup_status | stale |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        # Ligne 1 : event_date valide → source=rss
        f.write("| 2026-06-01 |  |  | Fresh news | BRENT |  | 1 | reuters |  | geopolitical |  | BRENT:LONG:high | high | confirmed | aaaaaaaaaaaa | 2026-05-30 | structurel |  |  |\n")
        # Ligne 2 : event_date vide → fallback sur date d'ingestion
        f.write("| 2026-06-01 |  |  | No pubdate news | GOLD |  | 1 | ap |  | geopolitical |  | GOLD:LONG:high | high | confirmed | bbbbbbbbbbbb |  | ponctuel |  |  |\n")
        path = Path(f.name)
    try:
        events = tc.parse_events_log(path=path)
    finally:
        path.unlink()
    assert len(events) == 2
    rss_ev = next(e for e in events if e["cours"] == "BRENT")
    fb_ev = next(e for e in events if e["cours"] == "GOLD")
    assert rss_ev["event_date_source"] == "rss"
    assert rss_ev["_event_dt"].date() == datetime(2026, 5, 30).date()
    assert fb_ev["event_date_source"] == "fallback"
    assert fb_ev["_event_dt"].date() == datetime(2026, 6, 1).date()  # = date ingestion


# ============================================================
# Idempotence (CONTRAINTE FORTE) : re-jouer le même cycle ne re-skippe pas à tort
# ============================================================

def test_idempotence_single_occurrence_always_kept():
    """Un événement UNIQUE (jamais vu ailleurs) reste TOUJOURS kept, quel que
    soit le nombre de re-runs. La dédup ne doit jamais skipper un nouvel event."""
    now = datetime.now(timezone.utc)
    ev = _ev("Brand new structural event never seen before", "COPPER", now)
    events = [ev]
    tc._canonicalize_events(events)
    assert ev["dedup_status"] == "kept"
    # Re-run sur le même set in-memory : toujours kept (pas de dérive)
    tc._canonicalize_events(events)
    assert ev["dedup_status"] == "kept"


def test_compute_event_id_deterministic_for_dedup():
    """event_id est déterministe : c'est la PIERRE ANGULAIRE de la dédup
    inter-jours (un repost J+1 recalcule exactement le même id)."""
    a = compute_event_id("Nvidia deal with SoftBank!", "NASDAQ")
    b = compute_event_id("nvidia   deal with softbank", "nasdaq")  # casse/espaces/ponct
    assert a == b
    assert len(a) == 12
