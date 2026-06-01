"""Tests Phase 2 news — spec v3/audit/spec-phase2-news-UNIFIEE.md.

Couvre chaque étape :
- Étape 1 : nature parsée par DeepSeek + fallback "ponctuel"
- Étape 2 : 5 nouvelles colonnes lues par nom (rétro-compat)
- Étape 3 : event_id stable + PREMIER-VU FAIT FOI (un repost daté aujourd'hui
            mais event_id vu hier → canonical_event_date=hier → stale/non-fresh)
- Étape 4 : coef_nature module la pertinence ; deja_cote exclu ; gate override
            bloqué si vieux/verbal
- Étape 5 : champs p2_*, T1, T2 présents dans le decision-log
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Permet d'importer les modules v3/scripts
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import triggers_classifier as tc  # noqa: E402
from triggers_classifier import (  # noqa: E402
    COEF_NATURE,
    NATURES_FILTERED_OUT,
    STALE_DAYS,
    compute_event_id,
    is_fresh_for_override,
    parse_events_log,
)
import extractor as ex  # noqa: E402


# ============================================================
# Étape 1 — nature DeepSeek (parsing + fallback)
# ============================================================

def test_step1_nature_in_extractor_dataclass():
    """L'ExtractedEvent expose un champ `nature` par défaut conservateur."""
    e = ex.ExtractedEvent()
    assert e.nature == "ponctuel"


def test_step1_nature_enum_and_prompt_version():
    """Nature ∈ {structurel, ponctuel, deja_cote, verbal} + PROMPT_VERSION bump v2.2."""
    assert set(ex.NATURES) == {"structurel", "ponctuel", "deja_cote", "verbal"}
    assert ex.PROMPT_VERSION == "v2.2"


def test_step1_nature_fallback_invalid_value():
    """Valeur hors-énum → fallback "ponctuel" (parsing défensif, zéro invention)."""
    out = ex._norm_enum("INVENTED_VALUE", ex._NAT_SET, default="ponctuel")
    assert out == "ponctuel"
    out2 = ex._norm_enum("STRUCTUREL", ex._NAT_SET, default="ponctuel")
    assert out2 == "structurel"  # uppercase normalisé
    out3 = ex._norm_enum(None, ex._NAT_SET, default="ponctuel")
    assert out3 == "ponctuel"


def test_step1_prompt_contains_nature_rule_and_fewshot():
    """Le SYSTEM_PROMPT mentionne nature dans le SCHEMA + dans les RÈGLES.
    Un few-shot deja_cote est présent."""
    assert '"nature"' in ex.SYSTEM_PROMPT
    assert "structurel" in ex.SYSTEM_PROMPT
    assert "deja_cote" in ex.SYSTEM_PROMPT
    # Few-shot deja_cote (compte-rendu S&P 500)
    fs_natures = []
    for _user, assistant_json in ex.FEW_SHOTS:
        try:
            fs_natures.append(json.loads(assistant_json).get("nature"))
        except json.JSONDecodeError:
            pass
    assert "deja_cote" in fs_natures


# ============================================================
# Étape 2 — Schéma events-log 5 nouvelles colonnes par NOM
# ============================================================

def test_step2_parse_events_log_v22_header_19_cols():
    """Une ligne v2.2 19 cols est parsée — les 5 nouveaux champs sont lus par NOM."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as f:
        f.write("| date | l1 | l2 | trigger | cours | latence | r | source | news_zone | category | pattern_id | impacts | materiality | reliability | event_id | event_date | nature | dedup_status | stale |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        f.write("| 2026-05-30 |  |  | Iran strikes Brent up | BRENT |  | 1 | reuters | Moyen-Orient | geopolitical |  | BRENT:LONG:high | high | confirmed | abc123def456 | 2026-05-30 | structurel |  |  |\n")
        path = Path(f.name)
    try:
        events = parse_events_log(path=path)
    finally:
        path.unlink()
    assert len(events) == 1
    ev = events[0]
    assert ev["event_id"] == "abc123def456"
    assert ev["nature"] == "structurel"
    assert ev["event_date_source"] == "rss"  # event_date parsable


def test_step2_parse_events_log_legacy_14col_retrocompat():
    """Une ligne legacy 14 cols (pré-Phase 2) reste lisible.
    Les nouvelles colonnes sont calculées à la volée (event_id) ou défaut (nature=ponctuel)."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as f:
        f.write("| date | l1 | l2 | trigger | cours | latence | r | source | news_zone | category | pattern_id | impacts | materiality | reliability |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        f.write("| 2026-05-30 |  |  | Some old news | BRENT |  | 1 | reuters |  | geopolitical |  | BRENT:LONG:high | high | confirmed |\n")
        path = Path(f.name)
    try:
        events = parse_events_log(path=path)
    finally:
        path.unlink()
    assert len(events) == 1
    ev = events[0]
    # event_id calculé à la volée
    assert len(ev["event_id"]) == 12
    # Nature : fallback "ponctuel" (zéro invention)
    assert ev["nature"] == "ponctuel"


# ============================================================
# Étape 3 — event_id stable + PREMIER-VU FAIT FOI
# ============================================================

def test_step3_event_id_stable_and_normalisation():
    """compute_event_id est stable contre les variations de casse/accents/ponctuation."""
    a = compute_event_id("Iran strikes US bases!", "BRENT")
    b = compute_event_id("IRAN strikes US bases", "brent")  # casse + ponctuation
    c = compute_event_id("Irán strikes  US   bases", "BRENT")  # accent + espaces
    assert a == b == c
    assert len(a) == 12


def test_step3_event_id_actif_matters():
    """Un même trigger mais actif différent → event_id différent."""
    a = compute_event_id("Iran strikes US bases", "BRENT")
    b = compute_event_id("Iran strikes US bases", "GOLD")
    assert a != b


def test_step3_premier_vu_fait_foi_critical():
    """SCÉNARIO CRITIQUE (règle Thomas) :
    Un event est vu HIER avec une certaine date. Le MÊME event est re-publié AUJOURD'HUI
    (même trigger, même actif → même event_id). canonical_event_date doit être HIER,
    pas AUJOURD'HUI — donc l'occurrence d'aujourd'hui n'est PAS fraîche pour le scoring
    et est marquée dedup_status="repost" → exclue."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    today = datetime.now(timezone.utc)
    # Construit 2 events à la main (sans passer par events-log.md)
    events = [
        {
            "date": yesterday.date().isoformat(),
            "trigger": "Iran strikes Brent jumps 5pct",
            "cours": "BRENT",
            "impacts": "BRENT:LONG:high",
            "materiality": "high",
            "reliability": "confirmed",
            "nature": "structurel",
            "event_id": "",
            "event_date": yesterday.date().isoformat(),
            "_dt": yesterday,
            "_impacts": [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
            "_event_dt": yesterday,
            "event_date_source": "rss",
        },
        {
            "date": today.date().isoformat(),
            "trigger": "Iran strikes Brent jumps 5pct",  # même contenu → même normalisation
            "cours": "BRENT",
            "impacts": "BRENT:LONG:high",
            "materiality": "high",
            "reliability": "confirmed",
            "nature": "structurel",
            "event_id": "",
            "event_date": today.date().isoformat(),
            "_dt": today,
            "_impacts": [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
            "_event_dt": today,
            "event_date_source": "rss",
        },
    ]
    tc._canonicalize_events(events)
    # Les 2 events partagent le même event_id (calculé à la volée)
    assert events[0]["event_id"] == events[1]["event_id"]
    # canonical_event_date = MIN = hier
    canonical = events[0]["_canonical_dt"]
    assert canonical is not None
    assert canonical.date() == yesterday.date()
    # L'occurrence d'aujourd'hui est marquée repost
    today_ev = [e for e in events if e["_dt"] == today][0]
    yest_ev = [e for e in events if e["_dt"] == yesterday][0]
    assert yest_ev["dedup_status"] == "kept"
    assert today_ev["dedup_status"] == "repost"
    # Aucun n'est stale (canonical = hier < 30j)
    assert today_ev["stale"] is False


def test_step3_repost_excluded_from_scoring():
    """Le repost (dedup_status=repost) est filtré AVANT le cutoff dans _candidates_for."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    today = datetime.now(timezone.utc)
    events = [
        {
            "trigger": "Hormuz blockade announced",
            "cours": "BRENT",
            "category": "geopolitical",
            "materiality": "high",
            "reliability": "confirmed",
            "nature": "structurel",
            "_dt": yesterday,
            "_impacts": [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
            "_event_dt": yesterday,
            "_canonical_dt": yesterday,
            "dedup_status": "kept",
            "stale": False,
            "event_id": "AAA",
            "event_date_source": "rss",
        },
        {
            "trigger": "Hormuz blockade announced",  # repost
            "cours": "BRENT",
            "category": "geopolitical",
            "materiality": "high",
            "reliability": "confirmed",
            "nature": "structurel",
            "_dt": today,
            "_impacts": [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
            "_event_dt": today,
            "_canonical_dt": yesterday,
            "dedup_status": "repost",
            "stale": False,
            "event_id": "AAA",
            "event_date_source": "rss",
        },
    ]
    candidates = tc._candidates_for(events, "petrole", "geopol_iran")
    # Seul le "kept" doit rester (repost exclu en amont)
    statuses = [c["dedup_status"] for c in candidates]
    assert "kept" in statuses
    assert "repost" not in statuses


def test_step3_stale_30days_excluded():
    """canonical_event_date > 30j → stale=True → exclu du pool."""
    old = datetime.now(timezone.utc) - timedelta(days=60)
    events = [{
        "trigger": "Archive 2025 republished",
        "cours": "BRENT",
        "_dt": old, "_impacts": [],
        "_canonical_dt": old, "dedup_status": "kept", "stale": True,
        "nature": "structurel", "event_id": "Z", "event_date_source": "rss",
        "category": "geopolitical", "materiality": "high", "reliability": "confirmed",
    }]
    # _candidates_for doit l'écarter (stale=True)
    candidates = tc._candidates_for(events, "petrole", "geopol_iran")
    assert candidates == []


def test_step3_event_date_safe_rejects_future_and_before_2020():
    """Garde-fou : dates futures ou <2020 → None (fallback)."""
    assert tc._parse_event_date_safe("2030-01-01") is None  # future
    assert tc._parse_event_date_safe("2019-12-31") is None  # avant 2020
    assert tc._parse_event_date_safe("not-a-date") is None
    # Valide :
    assert tc._parse_event_date_safe("2026-01-15") is not None


def test_step3_fuzzy_match_within_48h():
    """Match flou (Levenshtein ≤0.15) sur fenêtre 48h/actif → fusion event_id."""
    if not tc._RAPIDFUZZ_OK:
        pytest.skip("rapidfuzz indisponible")
    dt1 = datetime.now(timezone.utc) - timedelta(hours=2)
    dt2 = datetime.now(timezone.utc) - timedelta(hours=1)
    events = [
        {
            "trigger": "OPEC announces production cut of 2 mbd",
            "cours": "BRENT", "_dt": dt1, "_impacts": [],
            "event_id": "", "event_date_source": "rss",
            "nature": "structurel", "materiality": "high", "reliability": "confirmed",
            "category": "commodity",
        },
        {
            "trigger": "OPEC announces production cut of 2 mb/d",  # quasi identique (b/d vs bd)
            "cours": "BRENT", "_dt": dt2, "_impacts": [],
            "event_id": "", "event_date_source": "rss",
            "nature": "structurel", "materiality": "high", "reliability": "confirmed",
            "category": "commodity",
        },
    ]
    tc._canonicalize_events(events)
    # Les 2 events doivent finir avec le même event_id (le plus ancien gagne)
    assert events[0]["event_id"] == events[1]["event_id"]


# ============================================================
# Étape 4 — coef_nature + gate override
# ============================================================

def test_step4_coef_nature_table_complete():
    """COEF_NATURE est défini pour les 4 natures × 3 horizons."""
    assert set(COEF_NATURE.keys()) == {"structurel", "ponctuel", "deja_cote", "verbal"}
    for nat, coef_by_h in COEF_NATURE.items():
        assert set(coef_by_h.keys()) == {"24h", "7j", "1m"}


def test_step4_coef_structurel_1m_high():
    """Structurel : porte la tendance long terme (coef 1m = 1.0)."""
    assert COEF_NATURE["structurel"]["1m"] == 1.0


def test_step4_coef_ponctuel_decay():
    """Ponctuel : forte à 24h, s'amortit à 1m."""
    assert COEF_NATURE["ponctuel"]["24h"] == 1.0
    assert COEF_NATURE["ponctuel"]["1m"] < 0.2


def test_step4_deja_cote_filtered_out():
    """deja_cote est dans NATURES_FILTERED_OUT → écarté en amont par _candidates_for."""
    assert "deja_cote" in NATURES_FILTERED_OUT
    now = datetime.now(timezone.utc)
    events = [{
        "trigger": "S&P logs 9 weekly gains",
        "cours": "SP500",
        "nature": "deja_cote",
        "_dt": now, "_impacts": [{"asset": "SP500", "direction": "LONG", "confidence": "high"}],
        "_canonical_dt": now, "dedup_status": "kept", "stale": False,
        "event_id": "X", "event_date_source": "rss",
        "category": "macro", "materiality": "low", "reliability": "confirmed",
    }]
    candidates = tc._candidates_for(events, "sp500", "tension_geopolitique_active")
    assert candidates == []


def test_step4_is_fresh_for_override_72h():
    """Frais si canonical_event_date ≤72h."""
    now = datetime.now(timezone.utc)
    ev_fresh = {"_canonical_dt": now - timedelta(hours=24)}
    ev_old = {"_canonical_dt": now - timedelta(hours=100)}
    assert is_fresh_for_override(ev_fresh, now) is True
    assert is_fresh_for_override(ev_old, now) is False


def test_step4_scoring_applies_coef_nature_to_pertinence():
    """Sur un critère news, la contribution est modulée par coef_nature[horizon]."""
    import scoring_analyste as sa
    # Critère news factice
    crit = {
        "id": "test", "nom": "Test news", "cle_courante": "test_news",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    # raw : triplet news (source_track="ia") avec nature=ponctuel
    raw_ponctuel = {
        "valeur": 1, "source_track": "ia", "materiality": "high",
        "reliability": "confirmed", "nature": "ponctuel",
        "event_id": "EID1", "event_date": "2026-05-30T12:00:00+00:00",
        "event_date_source": "rss", "freshness_days": 1.0,
    }
    fiche = {"actif": "TEST", "criteres": [crit]}
    valeurs = {"test_news": raw_ponctuel}
    res = sa.score_actif("test", fiche, valeurs)
    c = res.criteres[0]
    # 1m : ponctuel × 0.15 → contribution = 1 * 1 * (1.0 * 0.15) * 1 = 0.15
    assert abs(c.contributions["1m"] - 0.15) < 1e-6
    # 24h : ponctuel × 1.0 → contribution = 1.0
    assert abs(c.contributions["24h"] - 1.0) < 1e-6


def test_step4_gate_override_blocked_if_old_or_verbal():
    """Le cap anti-inversion doit s'appliquer si la news est verbale OU vieille
    (>72h) OU rumor, même si materiality=high."""
    import scoring_analyste as sa
    # Critère quant (poids 1, val -1 → SHORT)
    crit_quant = {
        "id": "q", "nom": "Quant", "cle_courante": "quant",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    # Critère news (val +1, high+confirmed mais NATURE VERBAL → override doit être BLOQUÉ)
    crit_news = {
        "id": "n", "nom": "News", "cle_courante": "news",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_quant, crit_news]}
    valeurs = {
        "quant": -1,
        "news": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed",
            "nature": "verbal",  # ← nature interdite pour override
            "event_id": "E", "event_date": "2026-05-30T12:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 0.5,
        },
    }
    res = sa.score_actif("test", fiche, valeurs)
    # Override doit être FALSE pour tous les horizons
    for h in sa.HORIZONS:
        assert res.news_cap_info[h]["override_high_confirmed"] is False, h


def test_step4_gate_override_allowed_if_fresh_structurel_high():
    """Override autorisé si frais (≤72h) + structurel + high + non-rumor."""
    import scoring_analyste as sa
    crit_quant = {
        "id": "q", "nom": "Quant", "cle_courante": "quant",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    crit_news = {
        "id": "n", "nom": "News", "cle_courante": "news",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_quant, crit_news]}
    valeurs = {
        "quant": -1,
        "news": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed", "nature": "structurel",
            "event_id": "E", "event_date": "2026-05-30T12:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 1.0,  # 24h
        },
    }
    res = sa.score_actif("test", fiche, valeurs)
    # Override doit être TRUE pour au moins un horizon
    overrides = [res.news_cap_info[h]["override_high_confirmed"] for h in sa.HORIZONS]
    assert any(overrides)


# ============================================================
# Étape 5 — Persistance + métriques shadow
# ============================================================

def test_step5_p2_fields_in_decision_log():
    """Les champs p2_* et T1/T2 sont présents dans les records du decision-log."""
    import scoring_analyste as sa
    crit = {
        "id": "n", "nom": "News", "cle_courante": "news",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit]}
    valeurs = {"news": {
        "valeur": 1, "source_track": "ia", "materiality": "high",
        "reliability": "confirmed", "nature": "structurel",
        "event_id": "EID1", "event_date": "2026-05-30T12:00:00+00:00",
        "event_date_source": "rss", "freshness_days": 1.0,
    }}
    res = sa.score_actif("test", fiche, valeurs)
    records = sa.build_decision_log_records([res], datetime.now(timezone.utc))
    assert len(records) == 3  # 1 actif × 3 horizons
    for rec in records:
        # Champs racine Phase 2
        for f in (
            "p2_M1_nature_filtered_rate", "p2_M2_stale_rate", "p2_M3_dedup_rate",
            "p2_M4_gate_override_blocked", "p2_M5_nature_composition",
            "p2_M6_bias", "p2_M7_ratio_news",
            "p2_T1_faux_flips_evites", "p2_T2_vrais_flips_qualifies",
        ):
            assert f in rec, f"Champ manquant : {f}"
        # Critères : event_id, nature, freshness_days, coef_nature
        for c in rec["criteres"]:
            if c.get("event_id"):
                assert "nature" in c
                assert "event_date" in c
                assert "freshness_days" in c
                assert "coef_nature" in c


def test_step5_t1_t2_metrics_computed():
    """T1 (faux flips évités) et T2 (vrais flips qualifiés) sont calculables.

    Construction : un quant -1 et un news +1 dont nature=deja_cote → contribution
    nulle → T1 doit potentiellement compter (raw_contrib opposé à quant)."""
    import scoring_analyste as sa
    crit_q = {
        "id": "q", "nom": "Q", "cle_courante": "q", "normalisation": "triplet",
        "poids": 1.0, "signe": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    crit_n = {
        "id": "n", "nom": "N", "cle_courante": "n", "normalisation": "triplet",
        "poids": 1.0, "signe": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_q, crit_n]}
    valeurs = {
        "q": -1,
        "n": {
            "valeur": 1, "source_track": "ia", "materiality": "low",
            "reliability": "confirmed", "nature": "deja_cote",
            "event_id": "DC", "event_date": "2026-05-30T00:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 0.5,
        },
    }
    res = sa.score_actif("test", fiche, valeurs)
    records = sa.build_decision_log_records([res], datetime.now(timezone.utc))
    # Au moins un horizon doit montrer un faux flip évité (deja_cote vs quant opposé)
    t1_totals = [r["p2_T1_faux_flips_evites"] for r in records]
    assert sum(t1_totals) >= 1, f"T1 doit avoir détecté un faux flip évité, got {t1_totals}"
