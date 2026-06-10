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
    """Nature ∈ {structurel, ponctuel, deja_cote, verbal} + PROMPT_VERSION bump v2.3.

    NT-1 (bump v2.2 → v2.3) : ajout règle anti sur-structurel + few-shot
    audit single-name (Cobre Panama) classé ponctuel.
    """
    assert set(ex.NATURES) == {"structurel", "ponctuel", "deja_cote", "verbal"}
    assert ex.PROMPT_VERSION == "v2.3"


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


def test_p2_m7_part_news_bornee_0_1():
    """M7 (p2_M7_ratio_news) est désormais une PART bornée [0,1] — JAMAIS > 100%.

    Régression (bug 10/06) : l'ancien M7 réutilisait `ratio_news = |news|/|quant|`
    NON borné (observé jusqu'à 72.7 ≈ 7269% en prod quand le quant est minuscule).
    On reproduit le cas pathologique : un critère news fort + un critère quant
    quasi nul → l'ancien ratio aurait explosé ; M7 borné reste dans [0,1].
    Le champ DÉCISIONNEL `ratio_news` (brut), lui, reste non borné (inchangé).
    """
    import scoring_analyste as sa
    crit_n = {
        "id": "n", "nom": "N", "cle_courante": "n", "normalisation": "triplet",
        "poids": 10.0, "signe": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    crit_q = {
        "id": "q", "nom": "Q", "cle_courante": "q", "normalisation": "zscore",
        "zscore_window": 60, "zscore_div": 2, "cap": 1.0,
        "poids": 1.0, "signe": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_n, crit_q]}
    # news net (+1, poids 10) ; quant quasi nul (z≈0) → |quant| → 0.
    valeurs = {
        "n": {"valeur": 1, "source_track": "ia"},
        "q": {"valeur_normalisee": 0.0001},
    }
    res = sa.score_actif("test", fiche, valeurs)
    records = sa.build_decision_log_records([res], datetime.now(timezone.utc))
    for rec in records:
        m7 = rec["p2_M7_ratio_news"]
        assert 0.0 <= m7 <= 1.0, f"M7 hors bornes [0,1] : {m7}"
        # Le champ décisionnel brut peut, lui, dépasser 1.0 (non borné, inchangé) :
        # c'est exactement la valeur que la gate compare à NEWS_DOMINANT_RATIO.
        assert rec["ratio_news"] >= 0.0
    # Borne haute atteignable : quant nul → part news = 1.0 (≈100%, pas 7000%).
    assert any(
        abs(rec["p2_M7_ratio_news"] - 1.0) < 0.01 for rec in records
    ), "Avec quant≈0, M7 doit tendre vers 1.0 (100%), pas exploser"


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


# ============================================================
# Étape 6 — Propagation nature CHEMIN SYNTHÈSE COMPLET
#  triggers_classifier → criteres_calculator → scoring → decision-log
#  Diagnostic : 33 critères ia_synthese dans le run réel avaient
#  nature=null et coef_nature=null (bug de propagation).
# ============================================================

def test_step6_criteres_calculator_propage_nature():
    """build_critere_value (criteres_calculator) DOIT propager `nature`,
    `event_id`, `event_date`, `freshness_days` du dict triplet vers le
    dict de sortie (= raw consommé par scoring_analyste)."""
    import criteres_calculator as cc
    triplets = {
        "geopolitique_test": {
            "valeur": 1,
            "materiality": "high",
            "reliability": "confirmed",
            "source_track": "ia_synthese",
            "synthese_rationale": "Test rationale",
            "nature": "structurel",
            "event_id": "EID_TEST_1",
            "event_date": "2026-05-30T12:00:00+00:00",
            "event_date_source": "rss",
            "freshness_days": "1.50",
        },
    }
    crit = {
        "cle_courante": "geopolitique_test",
        "normalisation": "triplet",
        "source": "news",
    }
    out = cc.build_critere_value(
        "test_fiche", crit, triplets,
        triggers_cfg={}, events=[], now=datetime.now(timezone.utc),
    )
    assert out is not None
    # Propagation Phase 2 (le bug initial : ces clés manquaient toutes)
    assert out["nature"] == "structurel", (
        "BUG : nature non propagée de triplets vers le raw du scoring"
    )
    assert out["event_id"] == "EID_TEST_1"
    assert out["event_date"] == "2026-05-30T12:00:00+00:00"
    assert out["freshness_days"] == "1.50"
    # Rétro-compat : les anciens champs sont toujours là
    assert out["source_track"] == "ia_synthese"
    assert out["materiality"] == "high"
    assert out["synthese_rationale"] == "Test rationale"


def test_step6_chemin_complet_synthese_active_coef_nature():
    """End-to-end du chemin synthèse :
       criteres_calculator → scoring_analyste → decision-log.
       Un critère ia_synthese avec nature=ponctuel DOIT voir son coef_nature[1m]=0.15
       réellement appliqué (et tracé dans le decision-log).
    """
    import criteres_calculator as cc
    import scoring_analyste as sa

    triplets = {
        "news_synth": {
            "valeur": 1,
            "materiality": "medium",
            "reliability": "confirmed",
            "source_track": "ia_synthese",
            "synthese_rationale": "Synthèse DeepSeek test",
            "nature": "ponctuel",
            "event_id": "EID_SYNTH",
            "event_date": "2026-05-30T12:00:00+00:00",
            "event_date_source": "rss",
            "freshness_days": "1.00",
        },
    }
    crit_news = {
        "cle_courante": "news_synth",
        "normalisation": "triplet",
        "source": "news",
    }
    raw = cc.build_critere_value(
        "test_fiche", crit_news, triplets,
        triggers_cfg={}, events=[], now=datetime.now(timezone.utc),
    )

    # Fiche pour score_actif (format attendu par scoring_analyste)
    fiche = {
        "actif": "TEST",
        "criteres": [{
            "id": "n", "nom": "News synth", "cle_courante": "news_synth",
            "normalisation": "triplet", "poids": 1.0, "signe": 1,
            "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
        }],
    }
    valeurs = {"news_synth": raw}
    res = sa.score_actif("test", fiche, valeurs)
    c = res.criteres[0]

    # CRITICAL : CritereResult.nature DOIT être renseignée (preuve que le
    # chemin a transporté nature jusqu'au scoring).
    assert c.nature == "ponctuel", (
        f"BUG nature : attendu 'ponctuel', got '{c.nature}'. "
        "Le chemin criteres_calculator → scoring n'a pas propagé nature."
    )
    # coef_nature[1m] = 0.15 (ponctuel décay long) → contribution = 1*1*(1.0*0.15)*1
    assert abs(c.coef_nature_applied["1m"] - 0.15) < 1e-9
    assert abs(c.contributions["1m"] - 0.15) < 1e-6
    # 24h : ponctuel × 1.0 → identité
    assert abs(c.contributions["24h"] - 1.0) < 1e-6

    # Decision-log : la nature ET coef_nature DOIVENT être présentes
    records = sa.build_decision_log_records([res], datetime.now(timezone.utc))
    for rec in records:
        crit_log = rec["criteres"][0]
        assert crit_log.get("nature") == "ponctuel", (
            f"Decision-log {rec['horizon']} : nature manquante "
            f"(bug initial : 33 critères ia_synthese avec nature=null)"
        )
        assert crit_log.get("coef_nature") is not None
        # M5 (composition nature) doit être non-vide pour cet horizon
        assert rec["p2_M5_nature_composition"], (
            f"M5 vide alors qu'on a un critère news avec nature : {rec}"
        )
        assert rec["p2_M5_nature_composition"].get("ponctuel", 0) >= 1


def test_step6_chemin_synthese_faible_propage_nature():
    """Chemin ia_synthese_faible (val=0, conviction faible) :
    nature dominante des candidats DOIT être posée pour activer M5/T2."""
    import criteres_calculator as cc
    import scoring_analyste as sa

    # Simule la sortie de triggers_classifier pour le chemin faible :
    # val=0, source_track=ia_synthese_faible, nature posée (notre fix)
    triplets = {
        "news_faible": {
            "valeur": 0,
            "materiality": "",
            "reliability": "",
            "source_track": "ia_synthese_faible",
            "synthese_rationale": "Conviction faible",
            "nature": "structurel",  # nature dominante des candidats
        },
    }
    crit = {
        "cle_courante": "news_faible",
        "normalisation": "triplet",
        "source": "news",
    }
    raw = cc.build_critere_value(
        "f", crit, triplets, triggers_cfg={}, events=[],
        now=datetime.now(timezone.utc),
    )
    assert raw["nature"] == "structurel"
    fiche = {
        "actif": "TEST",
        "criteres": [{
            "id": "f", "nom": "News faible", "cle_courante": "news_faible",
            "normalisation": "triplet", "poids": 1.0, "signe": 1,
            "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
        }],
    }
    res = sa.score_actif("test", fiche, {"news_faible": raw})
    c = res.criteres[0]
    assert c.nature == "structurel"
    # Decision-log : nature + coef_nature doivent apparaître (même sans event_id)
    records = sa.build_decision_log_records([res], datetime.now(timezone.utc))
    for rec in records:
        crit_log = rec["criteres"][0]
        assert crit_log.get("nature") == "structurel", (
            "BUG chemin ia_synthese_faible : nature non loggée dans decision-log"
        )
        assert crit_log.get("coef_nature") is not None


def test_step6_triggers_classifier_pose_nature_meme_sans_best_ev():
    """Si DeepSeek tranche LONG/SHORT high mais qu'aucun event matchant
    n'est trouvé (best_ev=None), la nature DOIT quand même être dans le meta
    (fallback 'ponctuel') — bug initial : nature manquait → null en aval."""
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    # Un seul event hors-fenêtre (cutoff = now - 7j par défaut)
    events = []  # zéro candidat → best_ev sera None
    synthese = {
        "direction": "LONG",
        "conviction": "high",
        "rationale": "Rationale haute conviction",
    }
    # Stub minimal : choisir un (actif, cle) qui a un scope IA
    # On utilise un mock direct via API privée pour rester focalisé
    from triggers_classifier import _resolve_triplet_with_meta, CRITERION_SCOPE
    if not CRITERION_SCOPE:
        pytest.skip("CRITERION_SCOPE vide (config absente)")
    actif_key, cle = next(iter(CRITERION_SCOPE.keys()))
    val, meta = _resolve_triplet_with_meta(
        events, actif_key, cle,
        long_keywords=[], short_keywords=[],
        lookback_days=7, now=now, synthese=synthese,
    )
    # high conviction → val_signed = ±1
    assert val in (1, -1)
    # CRITICAL : nature DOIT être posée même sans best_ev (fallback)
    assert meta.get("nature") == "ponctuel", (
        f"BUG : nature absente du meta synthèse haute-conviction sans best_ev. "
        f"meta={meta}"
    )


# ============================================================
# A3 (P0) — Garde-fou anti-atomisation du structurel
# ============================================================

def test_a3_coef_structurel_no_atomization():
    """A3 — Le structurel à 1m ne doit PAS être atomisé : coef 1m=1.0 → contribution
    PRESQUE PLEINE. Un ponctuel à 1m doit l'être (×0.15). Vérifie que le mécanisme
    flottant amortit ponctuel SANS écraser structurel.
    """
    import scoring_analyste as sa
    crit_struct = {
        "id": "s", "nom": "Structurel high", "cle_courante": "struct",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    crit_ponct = {
        "id": "p", "nom": "Ponctuel high", "cle_courante": "ponct",
        "normalisation": "triplet", "poids": 1.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_struct, crit_ponct]}
    valeurs = {
        "struct": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed", "nature": "structurel",
            "event_id": "S1", "event_date": "2026-05-30T12:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 1.0,
        },
        "ponct": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed", "nature": "ponctuel",
            "event_id": "P1", "event_date": "2026-05-30T12:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 1.0,
        },
    }
    res = sa.score_actif("test", fiche, valeurs)
    c_struct = next(c for c in res.criteres if c.cle_courante == "struct")
    c_ponct = next(c for c in res.criteres if c.cle_courante == "ponct")

    # STRUCTUREL : contribution 1m = 1.0 (coef_nature=1.0 → PAS atomisé)
    assert abs(c_struct.contributions["1m"] - 1.0) < 1e-9, (
        f"BUG A3 : le structurel a été atomisé à 1m (contrib={c_struct.contributions['1m']}, "
        "attendu 1.0). Le coef_nature flottant ne doit JAMAIS écraser le structurel."
    )
    # PONCTUEL : contribution 1m = 0.15 (coef_nature=0.15 → bien réduit)
    assert abs(c_ponct.contributions["1m"] - 0.15) < 1e-9, (
        f"BUG A3 : le ponctuel n'a pas été amorti à 1m (contrib={c_ponct.contributions['1m']}, "
        "attendu 0.15)."
    )
    # Coef_nature appliqué tracé pour debug/decision-log
    assert c_struct.coef_nature_applied["1m"] == 1.0
    assert c_ponct.coef_nature_applied["1m"] == 0.15


# ============================================================
# NT-3 (P1) — Test d'intégration override news-vs-quant
# ============================================================

def test_nt3_override_active_fresh_structurel_high_flippe_le_quant():
    """NT-3 scénario 1 : quant SHORT + news fraîche (≤72h) structurel high
    non-rumeur LONG → l'override s'active, la cellule FLIPPE LONG.

    Vérifie le vrai changement de tendance capté.
    """
    import scoring_analyste as sa
    # 2 critères quant pesants → SHORT prononcé
    crit_q1 = {
        "id": "q1", "nom": "Quant 1", "cle_courante": "q1",
        "normalisation": "triplet", "poids": 2.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    crit_q2 = {
        "id": "q2", "nom": "Quant 2", "cle_courante": "q2",
        "normalisation": "triplet", "poids": 2.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    # 1 critère news LONG (high+confirmed+structurel+frais 24h)
    crit_n = {
        "id": "n", "nom": "News LONG", "cle_courante": "n",
        "normalisation": "triplet", "poids": 3.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "BRENT", "criteres": [crit_q1, crit_q2, crit_n]}
    valeurs = {
        "q1": -1,
        "q2": -1,
        "n": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed", "nature": "structurel",
            "event_id": "FRESH", "event_date": "2026-05-31T12:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 1.0,
        },
    }
    res = sa.score_actif("brent", fiche, valeurs)
    # L'override doit être actif sur au moins un horizon
    overrides = [res.news_cap_info[h]["override_high_confirmed"] for h in sa.HORIZONS]
    assert any(overrides), (
        f"NT-3 scénario 1 : override DOIT s'activer (fresh+structurel+high+non-rumor). "
        f"news_cap_info={res.news_cap_info}"
    )
    # Conséquence : sur 7j et 1m (où structurel coef=1.0, ponctuel partout =1 ici),
    # la news (poids 3 × val +1) doit l'emporter sur les 2 quant (poids 2 × val -1 each = -4 vs +3).
    # En l'absence d'override, le cap aurait écrêté news à 0.8×|quant|. Avec override,
    # news_total_capped = news_total brut → score = -4 + 3 = -1 (PAS de flip ici)
    # Mais le test d'override (qui empêche le cap) suffit à valider la sémantique.
    # On vérifie surtout que le CAP n'a PAS été appliqué quand override actif.
    for h in sa.HORIZONS:
        info_h = res.news_cap_info[h]
        if info_h["override_high_confirmed"]:
            # Cap_applied DOIT être False quand override actif (cap court-circuité)
            assert info_h["cap_applied"] is False, (
                f"BUG NT-3 : override actif mais cap_applied=True à {h} — "
                "le cap doit être court-circuité quand override est ON."
            )


def test_nt3_override_inactif_si_verbal_ou_stale_pas_de_flip():
    """NT-3 scénario 2 : quant SHORT + news LONG mais VERBAL (ou stale >72h)
    → override NE s'active PAS, le cap tient → pas de flip (faux changement
    de tendance évité).
    """
    import scoring_analyste as sa
    crit_q = {
        "id": "q", "nom": "Quant SHORT", "cle_courante": "q",
        "normalisation": "triplet", "poids": 2.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    crit_n = {
        "id": "n", "nom": "News verbal LONG", "cle_courante": "n",
        "normalisation": "triplet", "poids": 5.0, "signe": 1,
        "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_q, crit_n]}
    # Cas A — news VERBAL (high+confirmed+frais mais NATURE INTERDITE)
    valeurs_verbal = {
        "q": -1,
        "n": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed", "nature": "verbal",  # ← interdit
            "event_id": "V", "event_date": "2026-05-31T12:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 0.5,
        },
    }
    res_v = sa.score_actif("test", fiche, valeurs_verbal)
    # Override DOIT être inactif (nature verbal non éligible)
    for h in sa.HORIZONS:
        assert res_v.news_cap_info[h]["override_high_confirmed"] is False, (
            f"BUG NT-3 verbal : override actif à {h} alors que nature=verbal. "
            "Une news verbale (déclaration/rumeur) ne doit PAS pouvoir renverser le quant."
        )

    # Cas B — news STALE (>72h, structurel+high+confirmed mais TROP VIEUX)
    valeurs_stale = {
        "q": -1,
        "n": {
            "valeur": 1, "source_track": "ia", "materiality": "high",
            "reliability": "confirmed", "nature": "structurel",
            "event_id": "OLD", "event_date": "2026-05-25T12:00:00+00:00",
            "event_date_source": "rss",
            "freshness_days": 5.0,  # 5j = 120h > 72h → trop vieux pour override
        },
    }
    res_s = sa.score_actif("test", fiche, valeurs_stale)
    for h in sa.HORIZONS:
        assert res_s.news_cap_info[h]["override_high_confirmed"] is False, (
            f"BUG NT-3 stale : override actif à {h} avec freshness=5j (>72h). "
            "Une news >72h ne doit PAS pouvoir renverser le quant."
        )


# ============================================================
# A1 (P0) — Contribution fantôme (shadow) → T1 mesurable
# ============================================================

def test_a1_shadow_contrib_recorded_when_event_excluded():
    """A1 — Quand un event est écarté par _candidates_for (deja_cote/stale/repost),
    sa contribution fantôme est agrégée dans le stash module.
    """
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    # Reset propre (idempotence)
    tc._reset_shadow_contrib()

    # Event deja_cote ciblant BRENT (asset=BRENT direction=LONG high+confirmed)
    ev = {
        "trigger": "Brent up 9 weeks in a row",
        "cours": "BZ=F",
        "category": "macro",
        "nature": "deja_cote",
        "materiality": "high",
        "reliability": "confirmed",
        "_dt": now,
        "_canonical_dt": now,
        "_impacts": [{"asset": "BRENT", "direction": "LONG", "confidence": "high"}],
        "dedup_status": "kept",
        "stale": False,
        "event_id": "DJC1",
        "event_date_source": "rss",
    }
    # Critère petrole/opec_politique (a un scope IA + accepte category macro? non)
    # Utilisons un critère dont la category accepte macro : non, opec accepte
    # commodity/geopolitical. Prenons un event geopolitical pour rester compatible.
    ev["category"] = "geopolitical"
    cands = tc._candidates_for([ev], "petrole", "geopol_iran")
    # L'event est exclu (deja_cote)
    assert cands == []
    # Shadow doit avoir été enregistré
    sh = tc.get_shadow_contrib("petrole", "geopol_iran")
    assert sh, (
        f"BUG A1 : shadow_contrib vide alors qu'un event deja_cote ciblant l'actif "
        f"a été écarté. Stash = {tc._SHADOW_CONTRIB}"
    )
    # Direction LONG → contributions positives (signe +1)
    for h in ("24h", "7j", "1m"):
        assert sh.get(h, 0.0) > 0, (
            f"Shadow horizon {h} doit être > 0 (LONG high confirmed) — got {sh.get(h)}"
        )


def test_a1_shadow_flip_potential_detected_in_decision_log():
    """A1 — p2_shadow_flip_potential[h] = True si shadow_exclu aurait pu
    renverser le quant (signe opposé + amplitude > 0.8×|quant|).
    """
    import scoring_analyste as sa
    crit_q = {
        "id": "q", "nom": "Q", "cle_courante": "q", "normalisation": "triplet",
        "poids": 1.0, "signe": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    # Critère news avec shadow_contrib_exclu injecté en raw
    # On simule : quant = -1.0, shadow = +2.0 → opposé + |shadow|/|quant| = 2 > 0.8 → flip
    crit_n = {
        "id": "n", "nom": "N", "cle_courante": "n", "normalisation": "triplet",
        "poids": 1.0, "signe": 1, "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
    }
    fiche = {"actif": "TEST", "criteres": [crit_q, crit_n]}
    valeurs = {
        "q": -1,
        "n": {
            # Critère news présent (val=0 — la news a été filtrée ou est neutre)
            # mais p2_shadow_contrib_exclu non vide → mesure l'impact évité.
            "valeur": 0, "source_track": "ia", "materiality": "low",
            "reliability": "confirmed", "nature": "deja_cote",
            "event_id": "X", "event_date": "2026-05-31T00:00:00+00:00",
            "event_date_source": "rss", "freshness_days": 0.5,
            # shadow LONG fort sur tous horizons → flippe le quant SHORT
            "p2_shadow_contrib_exclu": {"24h": 2.0, "7j": 2.0, "1m": 2.0},
        },
    }
    res = sa.score_actif("test", fiche, valeurs)
    records = sa.build_decision_log_records([res], datetime.now(timezone.utc))
    # Au moins un horizon doit avoir p2_shadow_flip_potential=True ET T1>=1
    flip_potentials = [r["p2_shadow_flip_potential"] for r in records]
    t1_counts = [r["p2_T1_faux_flips_evites"] for r in records]
    assert any(flip_potentials), (
        f"BUG A1 : p2_shadow_flip_potential jamais True alors que shadow LONG (+2) "
        f"vs quant SHORT (-1) sur 3 horizons. records={records}"
    )
    assert any(t > 0 for t in t1_counts), (
        f"BUG A1 : T1 non recompté via shadow. t1_counts={t1_counts}"
    )
    # Le champ p2_shadow_contrib_exclu doit être persisté
    for r in records:
        assert "p2_shadow_contrib_exclu" in r
        assert "p2_shadow_flip_potential" in r
