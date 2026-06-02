"""Tests criteres_calculator + triggers_classifier.

Mock 100% des appels HTTP — aucun appel réseau réel.
Vérifie :
- parsing events-log (avec/sans header, ligne invalide ignorée)
- triggers_classifier : match long/short/aucun/fenêtre lookback/calendrier
- fenêtre d'activation (dans/hors → comportement attendu)
- dégradation gracieuse : clé absente → critère omis, pas d'exception
- format de sortie compatible avec scoring_analyste.normalise
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402
import criteres_calculator as cc  # noqa: E402
import market_data as md  # noqa: E402
import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _no_real_http(monkeypatch):
    """Bloque tout appel HTTP réel : si un test oublie de mocker, il échoue clean.

    Couvre :
      - cc.http_get_json (CFTC, EIA, Open-Meteo, CBOE)
      - cc._fred_get_json (FRED, avec retry/backoff) — les tests FRED qui veulent
        un fetch doivent mocker soit cc._fred_get_json soit requests.get
      - md.fetch_history / md.fetch_price (Twelve Data + yfinance)
    """
    def _fail(*a, **kw):
        raise RuntimeError("HTTP réseau interdit dans les tests — mocker http_get_json")

    def _fail_md(*a, **kw):
        raise RuntimeError("HTTP réseau interdit dans les tests — mocker market_data.fetch_*")

    def _fail_fred(*a, **kw):
        raise RuntimeError("HTTP FRED interdit dans les tests — mocker _fred_get_json ou requests.get")

    monkeypatch.setattr(cc, "http_get_json", _fail)
    monkeypatch.setattr(cc, "_fred_get_json", _fail_fred)
    # Désactive aussi market_data : tests qui veulent un fetch doivent monkeypatcher md.fetch_*
    monkeypatch.setattr(md, "fetch_history", _fail_md)
    monkeypatch.setattr(md, "fetch_price", _fail_md)


@pytest.fixture
def triggers_cfg():
    return tc.load_triggers_config()


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Parsing events-log
# ---------------------------------------------------------------------------

EVENTS_SAMPLE = """# events-log

| date | l1 | l2 | trigger | cours | source | news_zone |
|---|---|---|---|---|---|---|
| 2026-05-28 | Géopolitique | Iran-Moyen-Orient | frappes Iran sur Ormuz | 85 | Reuters | Global |
| 2026-05-25 | Banques centrales | FOMC | FOMC hawkish | 100 | Reuters | US |
| 2026-05-20 | Politique-FR | France | motion de censure | 7400 | AFP | EU-FR |
| 2026-05-15 | Commodities | OPEC | OPEC cut annoncé | 90 | Bloomberg | Global |
| bad-date | x | x | x | x | x | x |
"""


def test_parse_events_log(tmp_path):
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_SAMPLE, encoding="utf-8")
    events = tc.parse_events_log(p)
    # 4 valides, la ligne bad-date ignorée
    assert len(events) == 4
    # Triés desc
    assert events[0]["_dt"] > events[-1]["_dt"]
    # Champs présents
    assert events[0]["trigger"]


def test_parse_events_log_absent(tmp_path):
    events = tc.parse_events_log(tmp_path / "nope.md")
    assert events == []


# ---------------------------------------------------------------------------
# Classifier triplets
# ---------------------------------------------------------------------------

def _make_event(date_str: str, trigger: str, l2: str = "") -> dict:
    return {
        "date": date_str,
        "l1": "",
        "l2": l2,
        "trigger": trigger,
        "source": "test",
        "news_zone": "Global",
        "_dt": datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc),
    }


def test_classify_long_match(triggers_cfg, now_fixed):
    events = [_make_event("2026-05-28", "frappes Iran sur Ormuz", "Iran")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    # cle_courante émis = "tension_geopol_moyen_orient" (alias YAML→fiche)
    assert res.get("petrole", {}).get("tension_geopol_moyen_orient") == 1


def test_classify_short_match(triggers_cfg, now_fixed):
    events = [_make_event("2026-05-28", "cessez-le-feu Iran annoncé", "Iran")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res.get("petrole", {}).get("tension_geopol_moyen_orient") == -1


def test_classify_no_match(triggers_cfg, now_fixed):
    events = [_make_event("2026-05-28", "marché calme, rien de neuf", "")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    # Tous les triplets doivent valoir 0
    assert res.get("petrole", {}).get("tension_geopol_moyen_orient") == 0
    assert res.get("vix", {}).get("tension_geopolitique_active") == 0


def test_classify_lookback_window(triggers_cfg, now_fixed):
    # Event vieux de 60 jours → hors fenêtre 7j de geopol_iran
    old_dt = (now_fixed - timedelta(days=60)).date().isoformat()
    events = [_make_event(old_dt, "frappes Iran", "Iran")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_classify_long_and_short_keeps_most_recent(triggers_cfg, now_fixed):
    events = [
        _make_event("2026-05-28", "cessez-le-feu Iran", "Iran"),   # plus récent: SHORT
        _make_event("2026-05-20", "frappes Iran", "Iran"),         # plus ancien: LONG
    ]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_classify_calendrier_or_diwali():
    # Octobre → LONG (Diwali)
    now = datetime(2026, 10, 15, tzinfo=timezone.utc)
    res = tc.classify_all(events=[], today=now)
    assert res["or"]["demande_indienne_saisonniere"] == 1


def test_classify_calendrier_or_off_season():
    # Mars → SHORT (off-season)
    now = datetime(2026, 3, 15, tzinfo=timezone.utc)
    res = tc.classify_all(events=[], today=now)
    assert res["or"]["demande_indienne_saisonniere"] == -1


def test_classify_calendrier_cafe_cycle():
    # 2025 (impaire) → off cycle → LONG
    now = datetime(2025, 6, 1, tzinfo=timezone.utc)
    res = tc.classify_all(events=[], today=now)
    assert res["cafe"]["cycle_bresil_biannuel"] == 1
    # 2026 (paire) → on cycle → SHORT
    now2 = datetime(2026, 6, 1, tzinfo=timezone.utc)
    res2 = tc.classify_all(events=[], today=now2)
    assert res2["cafe"]["cycle_bresil_biannuel"] == -1


def test_classify_word_boundary(triggers_cfg, now_fixed):
    # "war" en sub-string (warm) ne doit PAS matcher tension_geopolitique de l'or
    events = [_make_event("2026-05-28", "warm weather in Iowa", "")]
    res = tc.classify_all(events=events, today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["or"]["tension_geopolitique"] == 0


# ---------------------------------------------------------------------------
# Routing event→critère HYBRIDE (audit chantier 2)
# ---------------------------------------------------------------------------

def _make_event_full(date_str: str, trigger: str, cours: str = "",
                     l2: str = "", category: str = "") -> dict:
    return {
        "date": date_str,
        "l1": "",
        "l2": l2,
        "trigger": trigger,
        "cours": cours,
        "source": "test",
        "news_zone": "Moyen-Orient",
        "category": category,
        "_dt": datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc),
    }


def test_audit_iran_extended_ceasefire_routes_to_petrole(triggers_cfg, now_fixed):
    """Cas réel de l'audit chantier 2.

    Event : trigger="Report of breakthrough in US-Iran talks with extended ceasefire",
            cours="Brent (BZ=F), WTI (CL=F)", category="geopolitical".
    Avant : aucun routage (mot-clé attendu "Iran ceasefire" ne matche pas "extended ceasefire").
    Après : route sur petrole.tension_geopol_moyen_orient = -1 (détente) via :
      1. cours="Brent (BZ=F)" → mappe à actif "petrole"
      2. category="geopolitical" → scope OK
      3. tokens-AND : "iran ceasefire" → tous tokens ("iran", "ceasefire") présents
         dans le trigger → match SHORT → -1.
    """
    ev = _make_event_full(
        "2026-05-28",
        "Report of breakthrough in US-Iran talks with extended ceasefire subject to Trump's approval, causing oil prices to fall.",
        cours="Brent (BZ=F), WTI (CL=F)",
        l2="Pétrole-EIA",
        category="geopolitical",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_audit_iran_escalation_via_cours_routes_long(triggers_cfg, now_fixed):
    """Event escalade Iran avec cours Brent → +1 (LONG pétrole)."""
    ev = _make_event_full(
        "2026-05-29",
        "Iran retaliation: missile strikes target Israel, Brent up sharply",
        cours="Brent (BZ=F)",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_routing_hors_actif_via_cours_inutilisé(triggers_cfg, now_fixed):
    """Event ciblant un autre actif (Tesla) ne doit pas alimenter Pétrole geopol."""
    ev = _make_event_full(
        "2026-05-28",
        "Tesla beats earnings, guidance raised",
        cours="Tesla (TSLA)",
        l2="Automotive",
        category="earnings",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_routing_bon_actif_sans_cue_directionnel(triggers_cfg, now_fixed):
    """Event qui cible Brent + geopolitical mais sans cue LONG/SHORT clair → 0."""
    ev = _make_event_full(
        "2026-05-28",
        "Oil markets monitor Middle East developments closely",
        cours="Brent (BZ=F)",
        l2="Pétrole-EIA",
        category="geopolitical",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_routing_or_geopol_ne_pollue_pas_petrole(triggers_cfg, now_fixed):
    """Event Or (cours XAU) avec cue 'war' ne doit PAS alimenter petrole.geopol_iran."""
    ev = _make_event_full(
        "2026-05-28",
        "Gold rallies on global war fears",
        cours="Gold (GC=F)",
        l2="Or-Geopolitique",
        category="geopolitical",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Or geopol : LONG (war keyword)
    assert res["or"]["tension_geopolitique"] == 1
    # Petrole geopol Iran : pas d'Iran/Ormuz/etc → 0
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_routing_category_filter_blocks_off_topic(triggers_cfg, now_fixed):
    """Event Brent mais category=earnings (off-topic) ne route pas sur geopol."""
    ev = _make_event_full(
        "2026-05-28",
        "Some Iran-related corporate news with ceasefire mention",
        cours="Brent (BZ=F)",
        l2="Earnings-Corporate",
        category="earnings",  # pas geopolitical → bloqué
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_routing_opec_via_cours_petrole(triggers_cfg, now_fixed):
    """Event OPEC cut + cours Brent → petrole.opec_production_policy = +1."""
    ev = _make_event_full(
        "2026-05-15",
        "OPEC+ cut production by 1mbpd to support prices",
        cours="Brent (BZ=F)",
        l2="OPEC",
        category="commodity",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["opec_production_policy"] == 1


def test_routing_nasdaq_megacap_via_ticker(triggers_cfg, now_fixed):
    """Event NVDA beat + ticker dans cours → nasdaq.sentiment_ia_megacaps = +1."""
    ev = _make_event_full(
        "2026-05-28",
        "Nvidia beat consensus, guidance raised on AI demand",
        cours="Nvidia (NVDA)",
        l2="Semi-conducteurs",
        category="earnings",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["nasdaq"]["sentiment_ia_megacaps"] == 1


def test_routing_lookback_respecte(triggers_cfg, now_fixed):
    """Event Iran escalation hors fenêtre (lookback 7j) → 0."""
    old_dt = (now_fixed - timedelta(days=30)).date().isoformat()
    ev = _make_event_full(
        old_dt,
        "Iran retaliation strikes Hormuz",
        cours="Brent (BZ=F)",
        l2="Iran",
        category="geopolitical",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_calendrier_intacts_meme_avec_events(triggers_cfg):
    """Les critères calendrier ne sont pas affectés par les events."""
    # Mars → off-season Or
    now = datetime(2026, 3, 15, tzinfo=timezone.utc)
    ev = _make_event_full("2026-03-14", "random", cours="Brent (BZ=F)",
                          category="geopolitical")
    res = tc.classify_all(events=[ev], today=now, triggers_cfg=triggers_cfg)
    assert res["or"]["demande_indienne_saisonniere"] == -1


def test_emit_keys_alignes_avec_fiches(triggers_cfg, now_fixed):
    """Les clés émises doivent correspondre aux `cle_courante` des fiches."""
    res = tc.classify_all(events=[], today=now_fixed, triggers_cfg=triggers_cfg)
    # Alias YAML→fiche : vérifier que les bonnes clés sont émises
    assert "tension_geopol_moyen_orient" in res.get("petrole", {})
    assert "opec_production_policy" in res.get("petrole", {})
    assert "geopolitique_mer_noire" in res.get("ble", {})
    assert "eudr" in res.get("cacao", {})
    assert "maladies_cabosses" in res.get("cacao", {})
    assert "maladies_cabosses_rouille" in res.get("cafe", {})
    assert "demande_pv_mining_strikes" in res.get("argent", {})
    assert "news_construction_infra" in res.get("cuivre", {})


def test_phrase_matching_robuste_tokens_and(triggers_cfg, now_fixed):
    """Test direct du matching robuste : tokens AND non-adjacents."""
    # "Iran ceasefire" doit matcher "ceasefire ... Iran" même séparé
    ev = _make_event_full(
        "2026-05-29",
        "Vance says US and Iran very close to deal; framework of ceasefire extension agreed",
        cours="Pétrole brut (CL=F)",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_word_boundary_war_ne_matche_pas_warm():
    """Sanity : 'war' ne doit pas matcher 'warm'."""
    assert not tc._phrase_matches("warm weather in iowa", "war")
    assert tc._phrase_matches("global war fears", "war")


def test_phrase_match_accents():
    """Sanity : accents normalisés des deux côtés."""
    assert tc._phrase_matches("cessez-le-feu iran", "cessez-le-feu")
    assert tc._phrase_matches("desescalade au moyen-orient", "désescalade")


def test_classify_empty_events(triggers_cfg, now_fixed):
    res = tc.classify_all(events=[], today=now_fixed, triggers_cfg=triggers_cfg)
    # Tous les triplets = 0 ; calendrier résolu
    for actif, crits in res.items():
        for cle, val in crits.items():
            assert val in (-1, 0, 1)


# ---------------------------------------------------------------------------
# Fenêtres d'activation
# ---------------------------------------------------------------------------

def test_window_eia_in(triggers_cfg):
    # Jeudi 2026-05-28 14h CET → dans fenêtre EIA (mer 16h30 → ven 16h30)
    now = datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc)  # 14h CET (UTC+2 en mai)
    assert cc.is_in_activation_window("eia_crude_surprise", now, triggers_cfg, "petrole") is True


def test_window_eia_out(triggers_cfg):
    # Lundi → hors fenêtre
    now = datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("eia_crude_surprise", now, triggers_cfg, "petrole") is False


def test_window_wasde_in(triggers_cfg):
    # 10 du mois
    now = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("wasde", now, triggers_cfg, "ble") is True


def test_window_wasde_out(triggers_cfg):
    now = datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("wasde", now, triggers_cfg, "ble") is False


def test_window_unknown_returns_none(triggers_cfg):
    now = datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)
    assert cc.is_in_activation_window("inexistant_cle", now, triggers_cfg, "x") is None


def test_window_out_emits_zero_normalisee(triggers_cfg, now_fixed):
    """Critère numerique hors fenêtre → valeur_normalisee=0 (contribution 0)."""
    # On simule un critère EIA un lundi (hors fenêtre)
    monday = datetime(2026, 5, 25, 12, 0, tzinfo=timezone.utc)
    crit = {"cle_courante": "eia_crude_surprise", "normalisation": "zscore",
            "source": "EIA API", "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, triggers_cfg, [], monday)
    assert val is not None
    assert val["valeur_normalisee"] == 0.0


# ---------------------------------------------------------------------------
# Dégradation gracieuse
# ---------------------------------------------------------------------------

def test_twelve_no_key_skips_gracefully(monkeypatch, triggers_cfg, now_fixed):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    crit = {"cle_courante": "dxy_trend_20j", "normalisation": "zscore",
            "source": "Twelve Data", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, triggers_cfg, [], now_fixed)
    assert val is None  # omis


def test_eia_no_key_skips_gracefully(monkeypatch, triggers_cfg, now_fixed):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    # Mercredi 17h CET → dans fenêtre EIA → on tente le fetch → no key → omis
    wed = datetime(2026, 5, 27, 15, 30, tzinfo=timezone.utc)  # 17h30 CET
    crit = {"cle_courante": "eia_crude_surprise", "normalisation": "zscore",
            "source": "EIA API", "zscore_window": 52, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, triggers_cfg, [], wed)
    assert val is None


def test_unmapped_source_skips(triggers_cfg, now_fixed):
    crit = {"cle_courante": "wgc_demand_index", "normalisation": "zscore",
            "source": "WGC monthly", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("or", crit, {}, triggers_cfg, [], now_fixed)
    assert val is None  # OMIS, pas d'exception


def test_collect_for_fiche_handles_all_missing(triggers_cfg, now_fixed, monkeypatch):
    """Aucune clé API + events-log vide → fiche petrole ne crash pas, retourne au moins triplets+gate."""
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    fiches = cc.load_fiches()
    fiche = fiches["petrole"]
    triplets = tc.classify_all(events=[], today=now_fixed, triggers_cfg=triggers_cfg).get("petrole", {})
    out = cc.collect_for_fiche("petrole", fiche, triplets, triggers_cfg, [], now_fixed)
    # Triplets (geopol + opec) + gate → présents avec valeur=0/false
    assert "tension_geopol_moyen_orient" in out
    assert out["tension_geopol_moyen_orient"]["valeur"] == 0
    assert "opec_production_policy" in out
    assert "gate_evenement_extreme" in out
    # Les critères Twelve/EIA/CFTC sont OMIS (pas dans le dict)
    assert "dxy_trend_20j" not in out


# ---------------------------------------------------------------------------
# Compatibilité avec scoring_analyste.normalise
# ---------------------------------------------------------------------------

def test_output_compatible_scoring_triplet():
    """Une valeur triplet {valeur: -1/0/+1} doit être normalisée correctement par sa."""
    crit = {"normalisation": "triplet", "cap": 1.0}
    v, _ = sa.normalise(crit, {"valeur": 1, "ts": "x"})
    assert v == 1.0
    v, _ = sa.normalise(crit, {"valeur": -1, "ts": "x"})
    assert v == -1.0
    v, _ = sa.normalise(crit, {"valeur": 0, "ts": "x"})
    assert v == 0.0


def test_output_compatible_scoring_zscore_precalc():
    """valeur_normalisee pré-calculée doit passer telle quelle (capée)."""
    crit = {"normalisation": "zscore", "cap": 1.0, "zscore_div": 2}
    v, note = sa.normalise(crit, {"valeur": 100, "valeur_normalisee": 0.5, "ts": "x"})
    assert v == 0.5
    # Cap doit s'appliquer
    v2, _ = sa.normalise(crit, {"valeur": 999, "valeur_normalisee": 5.0, "ts": "x"})
    assert v2 == 1.0


def test_output_compatible_scoring_lineaire():
    """valeur brute lineaire → scoring applique centre/echelle."""
    crit = {"normalisation": "lineaire", "centre": 50.0, "echelle": 1.0, "cap": 1.0}
    v, _ = sa.normalise(crit, {"valeur": 51.0, "ts": "x"})
    assert v == 1.0  # (51-50)/1 = 1, capé


def test_output_compatible_scoring_gate():
    """gate avec valeur:bool → ne contribue pas (None) mais ne lève pas."""
    crit = {"normalisation": "gate", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": True, "ts": "x"})
    assert v is None
    assert "GATE" in note


# ---------------------------------------------------------------------------
# Fetch helpers mockés (sanity)
# ---------------------------------------------------------------------------

def _fake_df(values_list):
    """Helper : construit un DataFrame OHLCV yfinance-compatible à partir d'une liste
    [(date_str, close), ...] (oldest→newest)."""
    import pandas as pd
    rows = [{"Open": c, "High": c, "Low": c, "Close": c, "Volume": 0} for _, c in values_list]
    idx = pd.to_datetime([d for d, _ in values_list])
    df = pd.DataFrame(rows, index=idx)
    df.index.name = "Date"
    return df


def test_fetch_twelve_series_no_key(monkeypatch):
    """Sans clé Twelve ET sans yfinance dispo → None propre."""
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    # Force la branche "pas de yfinance" : on patche _yfinance_available
    monkeypatch.setattr(cc, "_yfinance_available", lambda: False)
    assert cc.fetch_twelve_series("DX-Y.NYB") is None


def test_fetch_twelve_series_with_mock(monkeypatch):
    """fetch_twelve_series délègue à market_data.fetch_history (ticker Yahoo)."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    fake_df = _fake_df([
        ("2026-05-25", 100.0), ("2026-05-26", 101.0), ("2026-05-27", 102.0),
    ])
    monkeypatch.setattr(md, "fetch_history", lambda ticker, **k: fake_df)
    series = cc.fetch_twelve_series("DX-Y.NYB", outputsize=3)
    assert series is not None
    assert len(series) == 3
    assert series[-1][1] == 102.0


def test_fetch_cftc_with_mock(monkeypatch):
    """Dataset CFTC Socrata jun7-fc8e (Legacy COT) → noncomm_positions_* (pas m_money_*)."""
    fake = [
        {"report_date_as_yyyy_mm_dd": "2026-05-21T00:00:00", "noncomm_positions_long_all": "100", "noncomm_positions_short_all": "50"},
        {"report_date_as_yyyy_mm_dd": "2026-05-14T00:00:00", "noncomm_positions_long_all": "120", "noncomm_positions_short_all": "60"},
    ]
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, timeout=15: fake)
    nets = cc.fetch_cftc_managed_money_nets("CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE")
    assert nets == [60.0, 50.0]  # oldest→newest


# ---------------------------------------------------------------------------
# Nouveaux fetchers (incrément 5) — Twelve RSI, spread, ratio, alpha ; Open-Meteo zone
# ---------------------------------------------------------------------------

def test_cftc_markets_table_complete():
    """Table CFTC_MARKETS doit couvrir les 9 critères CFTC des fiches."""
    expected = {
        "cftc_cot_crude_nets", "cftc_cot_nets", "cftc_cot_copper_nets",
        "cftc_cot_silver", "cftc_cot_wheat", "cftc_cot_cocoa",
        "cftc_cot_coffee", "cftc_cot_eur_nets", "cftc_cot_vix_nets",
    }
    assert expected.issubset(set(cc.CFTC_MARKETS.keys()))


def test_twelve_zscore_dispatch_simple_symbol(monkeypatch, now_fixed):
    """dxy_trend_20j → DX-Y.NYB via market_data (yfinance fallback) → zscore."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    # 30 closes croissants : la dernière est l'extrême → z>0 capé
    fake_df = _fake_df([(f"2026-04-{i:02d}", 100.0 + i) for i in range(1, 31)])
    monkeypatch.setattr(md, "fetch_history", lambda ticker, **k: fake_df)
    crit = {"cle_courante": "dxy_trend_20j", "normalisation": "zscore",
            "source": "Twelve Data", "zscore_window": 20, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert "valeur_normalisee" in val
    assert val["valeur_normalisee"] > 0  # tendance haussière


def test_twelve_rsi_dispatch(monkeypatch, now_fixed):
    """rsi_14j_gspc → RSI calculé localement à partir d'une série market_data."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    # Série croissante (50 points) → gains uniquement → RSI = 100
    fake_df = _fake_df([(f"2026-03-{i:02d}", 100.0 + i) for i in range(1, 32)] +
                       [(f"2026-04-{i:02d}", 131.0 + i) for i in range(1, 20)])
    monkeypatch.setattr(md, "fetch_history", lambda ticker, **k: fake_df)
    crit = {"cle_courante": "rsi_14j_gspc", "normalisation": "lineaire",
            "source": "Twelve Data", "centre": 50, "echelle": 20, "cap": 1.0}
    val = cc.build_critere_value("sp500", crit, {}, {}, [], now_fixed)
    assert val is not None
    # RSI sur série monotone croissante → 100 (pas de perte)
    assert val["valeur"] == 100.0


def test_twelve_spread_zscore(monkeypatch, now_fixed):
    """spread_brent_wti → BZ=F vs CL=F via market_data → diff → zscore."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")

    df_bz = _fake_df([(f"2026-04-{i:02d}", 80.0 + i * 0.5) for i in range(1, 31)])
    df_cl = _fake_df([(f"2026-04-{i:02d}", 77.0 + i * 0.4) for i in range(1, 31)])

    def fake_hist(ticker, **k):
        if ticker == "BZ=F":
            return df_bz
        if ticker == "CL=F":
            return df_cl
        return None

    monkeypatch.setattr(md, "fetch_history", fake_hist)
    crit = {"cle_courante": "spread_brent_wti", "normalisation": "zscore",
            "source": "Twelve Data (calculé)", "zscore_window": 20, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert "valeur_normalisee" in val
    # Spread BZ-CL = (80+0.5i)-(77+0.4i) = 3+0.1i → croissant → z>0
    assert val["valeur_normalisee"] > 0


def test_twelve_ratio_lineaire(monkeypatch, now_fixed):
    """_twelve_ratio_lineaire utilise market_data.fetch_price (Yahoo tickers)."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    monkeypatch.setattr(md, "fetch_price", lambda ticker, **k: 2000.0)
    ratio = cc._twelve_ratio_lineaire("GC=F", "SI=F")
    assert ratio == 1.0  # 2000 / 2000 (mock identique)


def test_cftc_parsing_socrata_payload(monkeypatch):
    """Parsing payload Socrata réaliste : ISO date + champs string, ordre desc."""
    monkeypatch.setenv("TWELVE_DATA_API_KEY", "fake")
    fake = [
        {"report_date_as_yyyy_mm_dd": "2026-05-19T00:00:00.000",
         "noncomm_positions_long_all": "198358", "noncomm_positions_short_all": "49698"},
        {"report_date_as_yyyy_mm_dd": "2026-05-12T00:00:00.000",
         "noncomm_positions_long_all": "212267", "noncomm_positions_short_all": "47093"},
        {"report_date_as_yyyy_mm_dd": "2026-05-05T00:00:00.000",
         "noncomm_positions_long_all": "203487", "noncomm_positions_short_all": "46986"},
    ]
    monkeypatch.setattr(cc, "http_get_json", lambda url, params=None, timeout=15: fake)
    nets = cc.fetch_cftc_managed_money_nets("GOLD - COMMODITY EXCHANGE INC.")
    assert nets is not None
    assert len(nets) == 3
    # oldest→newest : 2026-05-05 → 2026-05-19
    assert nets[0] == 203487 - 46986  # = 156501
    assert nets[-1] == 198358 - 49698  # = 148660


def test_open_meteo_zone_routing(monkeypatch, now_fixed):
    """meteo_ci_ghana_precip_30j → lat 6.5 lon -3.0 → anomalie calculée."""
    captured_params = []

    def fake_get(url, params=None, timeout=15):
        captured_params.append(dict(params or {}))
        # Premier appel = fenêtre récente, deuxième = climato
        return {"daily": {"precipitation_sum": [1.0, 2.0, 3.0, 4.0, 5.0] * 20}}
    monkeypatch.setattr(cc, "http_get_json", fake_get)
    crit = {"cle_courante": "meteo_ci_ghana_precip_30j", "normalisation": "zscore",
            "source": "Open-Meteo", "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("cacao", crit, {}, {}, [], now_fixed)
    # Avec série constante répétée, mean récent == mean climato → z=0 → omis (std=0)
    # Mais on vérifie que les bons lat/lon ont été passés
    assert len(captured_params) >= 1
    assert captured_params[0]["latitude"] == 6.8
    assert captured_params[0]["longitude"] == -5.3


def test_mapping_non_monotone_vix_centre():
    """VIX entre 14 et 25 → +cap. VIX < 14 → tend vers -cap (complacence)."""
    assert cc._mapping_non_monotone_vix(18.0, low=14, high=25, cap=1.0) == 1.0
    # VIX = 7 (très bas) → -cap
    val = cc._mapping_non_monotone_vix(7.0, low=14, high=25, cap=1.0)
    assert val == -1.0
    # VIX = 40 (très haut) → -cap
    val2 = cc._mapping_non_monotone_vix(40.0, low=14, high=25, cap=1.0)
    assert val2 == -1.0


def test_eia_series_routing(monkeypatch, now_fixed):
    """cushing_stocks utilise série W_EPC0_SAX_YCUOK_MBBL."""
    monkeypatch.setenv("EIA_API_KEY", "fake")
    captured = []

    def fake_get(url, params=None, timeout=15):
        captured.append((url, dict(params or {})))
        # Génère 60 points pour permettre le zscore
        return {"response": {"data": [
            {"period": f"2026-W{i:02d}", "value": 400.0 + i} for i in range(1, 60)
        ]}}
    monkeypatch.setattr(cc, "http_get_json", fake_get)
    # Pas de fenêtre pour cushing_stocks → on est dans le flux normal
    crit = {"cle_courante": "cushing_stocks", "normalisation": "zscore",
            "source": "EIA API", "zscore_window": 52, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("petrole", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert "valeur_normalisee" in val
    # Series ID Cushing doit être dans les facets
    assert any("W_EPC0_SAX_YCUOK_MBBL" in str(p) for _, p in captured)


def test_compute_zscore_cap():
    # Historique constant → std=0 → None
    assert cc.compute_zscore_normalisee(10, [5, 5, 5, 5], zscore_div=2, cap=1) is None
    # Valeur extrême → cap appliqué
    hist = [0.0, 1.0, 2.0, 3.0, 4.0]
    z = cc.compute_zscore_normalisee(100, hist, zscore_div=2, cap=1.0)
    assert z == 1.0


# ---------------------------------------------------------------------------
# Intégration : run complet sans clés
# ---------------------------------------------------------------------------

def test_run_complete_no_keys_no_crash(monkeypatch, tmp_path):
    monkeypatch.delenv("TWELVE_DATA_API_KEY", raising=False)
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    # Rediriger l'output vers tmp_path
    monkeypatch.setattr(cc, "CRITERES_OUT", tmp_path / "criteres-courants.md")
    out = cc.run(now=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc))
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "last_update" in text
    # Au moins les gates + triplets sont présents pour chaque fiche
    assert "petrole" in text or "petrole:" in text


# ---------------------------------------------------------------------------
# FRED — fetchers + dispatch
# ---------------------------------------------------------------------------

def test_fred_no_key_skips_gracefully(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    out = cc.fetch_fred_series("DFII10", n=30)
    assert out is None
    # Le compteur skip doit avoir été incrémenté
    assert any(k.startswith("fred_no_key") for k in cc.SKIP_COUNTER)


def test_fred_series_parsing_filters_missing_values(monkeypatch):
    """FRED renvoie '.' pour les jours sans observation — doit être filtré."""
    monkeypatch.setenv("FRED_API_KEY", "fake")
    fake = {
        "observations": [
            {"date": "2026-05-29", "value": "2.05"},
            {"date": "2026-05-28", "value": "."},     # manquant
            {"date": "2026-05-27", "value": "2.01"},
            {"date": "2026-05-26", "value": "1.98"},
            {"date": "2026-05-23", "value": ""},      # vide
            {"date": "2026-05-22", "value": "1.95"},
        ]
    }
    monkeypatch.setattr(cc, "_fred_get_json", lambda sid, params, timeout=15: fake)
    series = cc.fetch_fred_series("DFII10", n=10)
    assert series is not None
    # 4 valeurs valides, triées oldest→newest
    assert series == [1.95, 1.98, 2.01, 2.05]


def test_fred_spread_aligns_by_date(monkeypatch):
    """Spread FRED US-DE : seul les dates présentes dans LES DEUX séries sont gardées."""
    monkeypatch.setenv("FRED_API_KEY", "fake")
    payload_us = {"observations": [
        {"date": "2026-05-29", "value": "4.50"},
        {"date": "2026-05-28", "value": "4.45"},
        {"date": "2026-05-27", "value": "4.40"},
        {"date": "2026-05-26", "value": "4.42"},
        {"date": "2026-05-23", "value": "4.41"},
        {"date": "2026-05-22", "value": "4.43"},
        {"date": "2026-05-21", "value": "4.44"},
        {"date": "2026-05-20", "value": "4.46"},
        {"date": "2026-05-19", "value": "4.48"},
        {"date": "2026-05-16", "value": "4.49"},
    ]}
    payload_de = {"observations": [
        {"date": "2026-05-29", "value": "2.50"},
        {"date": "2026-05-28", "value": "2.45"},
        {"date": "2026-05-27", "value": "2.40"},
        {"date": "2026-05-26", "value": "2.42"},
        {"date": "2026-05-23", "value": "2.41"},
        {"date": "2026-05-22", "value": "2.43"},
        {"date": "2026-05-21", "value": "2.44"},
        {"date": "2026-05-20", "value": "2.46"},
        {"date": "2026-05-19", "value": "2.48"},
        {"date": "2026-05-16", "value": "2.49"},
    ]}
    calls = {"n": 0}
    def fake_get(sid, params, timeout=15):
        calls["n"] += 1
        if sid == "DGS10":
            return payload_us
        if sid == "IRLTLT01DEM156N":
            return payload_de
        return None
    monkeypatch.setattr(cc, "_fred_get_json", fake_get)
    spread = cc.fetch_fred_spread("DGS10", "IRLTLT01DEM156N", n=20)
    assert spread is not None
    # 10 dates communes, spread constant = 2.00 (oldest→newest)
    assert len(spread) == 10
    assert all(abs(s - 2.00) < 1e-9 for s in spread)


def test_fred_dispatch_taux_tips(monkeypatch, now_fixed):
    """cle_courante='taux_10y_us_reels_tips' (zscore) → calcule un z-score capé."""
    monkeypatch.setenv("FRED_API_KEY", "fake")
    obs = [{"date": f"2026-01-{i:02d}", "value": f"{1.5 + 0.01*i:.4f}"}
           for i in range(1, 32)] + [
           {"date": "2026-02-28", "value": "3.50"}]  # spike final
    fake = {"observations": list(reversed(obs))}  # FRED renvoie DESC
    monkeypatch.setattr(cc, "_fred_get_json", lambda sid, params, timeout=15: fake)
    crit = {"cle_courante": "taux_10y_us_reels_tips", "normalisation": "zscore",
            "source": "FRED (DFII10)", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("or", crit, {}, {}, [], now_fixed)
    assert val is not None
    # La valeur brute est le dernier point (le spike = 3.50)
    assert val["valeur"] == 3.50
    # z-score capé à +1.0 (cap)
    assert val["valeur_normalisee"] == 1.0
    assert val["valeur_ponderee"] == val["valeur_normalisee"]


def test_fred_dispatch_taux_tips_sp500(monkeypatch, now_fixed):
    """Le S&P 500 reçoit bien le critère TIPS (cle_courante='taux_10y_us_reels_tips').

    Régression : sp500.yml a longtemps été privé du signal taux réel TIPS (présent
    sur Nasdaq/Or/Argent), le faisant tomber en couverture insuffisante. Ce test
    verrouille le câblage : même cle_courante → série FRED DFII10 → z-score capé,
    avec le signe géré par la fiche (signe=-1 : taux réel monte ⇒ pression baissière).
    """
    monkeypatch.setenv("FRED_API_KEY", "fake")
    captured = {}
    def fake_get(sid, params, timeout=15):
        captured["sid"] = sid
        obs = [{"date": f"2026-01-{i:02d}", "value": f"{1.5 + 0.01*i:.4f}"}
               for i in range(1, 32)] + [{"date": "2026-02-28", "value": "3.50"}]
        return {"observations": list(reversed(obs))}
    monkeypatch.setattr(cc, "_fred_get_json", fake_get)
    crit = {"cle_courante": "taux_10y_us_reels_tips", "normalisation": "zscore",
            "source": "FRED (DFII10)", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("sp500", crit, {}, {}, [], now_fixed)
    assert val is not None
    # Même série FRED que Nasdaq/Or : DFII10 (taux 10a réel TIPS)
    assert captured["sid"] == "DFII10"
    assert val["valeur"] == 3.50
    # z-score capé à +1.0 (le signe -1 est appliqué en aval par le scoring, pas ici)
    assert val["valeur_normalisee"] == 1.0
    assert val["valeur_ponderee"] == val["valeur_normalisee"]


def test_sp500_fiche_includes_tips_critere():
    """La fiche sp500.yml DOIT déclarer le critère TIPS avec le bon signe/normalisation.

    Verrou structurel (pas seulement le dispatch) : garantit que la fiche elle-même
    porte le critère, aligné sur Nasdaq (signe=-1, zscore). Empêche une régression
    silencieuse si quelqu'un retire le critère de la fiche.
    """
    import yaml as _yaml
    from pathlib import Path as _Path
    fiche = _yaml.safe_load(
        (_Path(cc.__file__).resolve().parents[1] / "config" / "fiches" / "sp500.yml").read_text()
    )
    tips = [c for c in fiche["criteres"] if c.get("cle_courante") == "taux_10y_us_reels_tips"]
    assert len(tips) == 1, "sp500.yml doit déclarer exactement un critère TIPS"
    c = tips[0]
    assert c["normalisation"] == "zscore"
    assert c["signe"] == -1          # taux réel monte ⇒ SHORT (comme Nasdaq)
    assert c["poids"] > 0
    # Pertinence horizon présente pour les 3 horizons
    assert set(c["pertinence"]) == {"24h", "7j", "1m"}


def test_fred_dispatch_hy_credit_spread(monkeypatch, now_fixed):
    """cle_courante='hy_credit_spread' (zscore) — série BAMLH0A0HYM2."""
    monkeypatch.setenv("FRED_API_KEY", "fake")
    captured = {}
    def fake_get(sid, params, timeout=15):
        captured["sid"] = sid
        obs = [{"date": f"2026-04-{i:02d}", "value": f"{3.0 + 0.02*i:.4f}"} for i in range(1, 31)]
        return {"observations": list(reversed(obs))}
    monkeypatch.setattr(cc, "_fred_get_json", fake_get)
    crit = {"cle_courante": "hy_credit_spread", "normalisation": "zscore",
            "source": "FRED (ICE BofA HY OAS)", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("sp500", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert captured["sid"] == "BAMLH0A0HYM2"


def test_fred_dispatch_differentiel_10y(monkeypatch, now_fixed):
    """differentiel_taux_10y_us_bund → spread DGS10 - IRLTLT01DEM156N."""
    monkeypatch.setenv("FRED_API_KEY", "fake")
    def fake_get(sid, params, timeout=15):
        if sid == "DGS10":
            obs = [{"date": f"2026-04-{i:02d}", "value": f"{4.50 + 0.01*i:.4f}"} for i in range(1, 31)]
        elif sid == "IRLTLT01DEM156N":
            obs = [{"date": f"2026-04-{i:02d}", "value": f"{2.40 + 0.005*i:.4f}"} for i in range(1, 31)]
        else:
            return None
        return {"observations": list(reversed(obs))}
    monkeypatch.setattr(cc, "_fred_get_json", fake_get)
    crit = {"cle_courante": "differentiel_taux_10y_us_bund", "normalisation": "zscore",
            "source": "FRED", "zscore_window": 60, "zscore_div": 2, "cap": 1.0}
    val = cc.build_critere_value("eurusd", crit, {}, {}, [], now_fixed)
    assert val is not None
    # Spread positif (US > DE)
    assert val["valeur"] > 0


# ---------------------------------------------------------------------------
# FRED — résilience 429 / 5xx (retry backoff + throttle)
# ---------------------------------------------------------------------------

class _FakeResp:
    """Réponse HTTP factice pour mocker requests.get dans les tests FRED."""
    def __init__(self, status_code, json_data=None, headers=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else {}
        self.headers = headers or {}

    def json(self):
        return self._json


# Référence vers l'implémentation RÉELLE de _fred_get_json : la fixture autouse
# _no_real_http la remplace par un stub qui lève. Les tests de résilience FRED
# ci-dessous testent justement cette fonction → ils la restaurent.
_REAL_FRED_GET_JSON = cc._fred_get_json


def _patch_fred_timing(monkeypatch):
    """Restaure le vrai _fred_get_json et neutralise les sleeps (tests rapides)."""
    import time as _t
    monkeypatch.setattr(cc, "_fred_get_json", _REAL_FRED_GET_JSON)
    monkeypatch.setattr(cc, "_fred_throttle", lambda: None)
    monkeypatch.setattr(_t, "sleep", lambda *_a, **_k: None)


def test_fred_retry_on_429_then_success(monkeypatch):
    """429 puis 200 : la série doit revenir (pas de fred_dead)."""
    import requests as _rq
    _patch_fred_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    seq = [
        _FakeResp(429, headers={"Retry-After": "1"}),
        _FakeResp(200, {"observations": [
            {"date": "2026-05-29", "value": "2.05"},
            {"date": "2026-05-28", "value": "2.01"},
        ]}),
    ]
    calls = {"n": 0}
    def fake_get(url, params=None, timeout=None):
        i = calls["n"]
        calls["n"] += 1
        return seq[i]
    monkeypatch.setattr(_rq, "get", fake_get)
    monkeypatch.setenv("FRED_API_KEY", "fake")
    out = cc.fetch_fred_series("DFII10", n=10)
    assert out == [2.01, 2.05]
    assert calls["n"] == 2  # 1 retry consommé
    assert not any(k.startswith("fred_dead") for k in cc.SKIP_COUNTER)


def test_fred_retry_exhausted_returns_none_and_marks_dead(monkeypatch):
    """429 sur toutes les tentatives → None + fred_dead incrémenté UNE fois."""
    import requests as _rq
    _patch_fred_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    calls = {"n": 0}
    def fake_get(url, params=None, timeout=None):
        calls["n"] += 1
        return _FakeResp(429)
    monkeypatch.setattr(_rq, "get", fake_get)
    monkeypatch.setenv("FRED_API_KEY", "fake")
    out = cc.fetch_fred_series("DFII10", n=10)
    assert out is None
    assert calls["n"] == cc.FRED_MAX_RETRIES  # toutes les tentatives consommées
    assert cc.SKIP_COUNTER["fred_dead:DFII10"] == 1


def test_fred_retry_on_5xx(monkeypatch):
    """503 puis 200 : retry sur 5xx aussi."""
    import requests as _rq
    _patch_fred_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    seq = [_FakeResp(503), _FakeResp(200, {"observations": [
        {"date": "2026-05-28", "value": "1.50"}]})]
    calls = {"n": 0}
    def fake_get(url, params=None, timeout=None):
        r = seq[calls["n"]]
        calls["n"] += 1
        return r
    monkeypatch.setattr(_rq, "get", fake_get)
    monkeypatch.setenv("FRED_API_KEY", "fake")
    out = cc.fetch_fred_series("DFII10", n=10)
    assert out == [1.50]
    assert calls["n"] == 2


def test_fred_no_retry_on_404(monkeypatch):
    """404 (non-retriable) : échec immédiat, une seule requête."""
    import requests as _rq
    _patch_fred_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    calls = {"n": 0}
    def fake_get(url, params=None, timeout=None):
        calls["n"] += 1
        return _FakeResp(404)
    monkeypatch.setattr(_rq, "get", fake_get)
    monkeypatch.setenv("FRED_API_KEY", "fake")
    out = cc.fetch_fred_series("BADID", n=10)
    assert out is None
    assert calls["n"] == 1  # aucun retry sur 404
    assert cc.SKIP_COUNTER["fred_dead:BADID"] == 1


def test_fred_retry_after_header_respected(monkeypatch):
    """L'en-tête Retry-After (secondes) pilote le délai du backoff."""
    delays = []
    import time as _t
    monkeypatch.setattr(cc, "_fred_get_json", _REAL_FRED_GET_JSON)
    monkeypatch.setattr(cc, "_fred_throttle", lambda: None)
    monkeypatch.setattr(_t, "sleep", lambda d=0, *a, **k: delays.append(d))
    import requests as _rq
    seq = [_FakeResp(429, headers={"Retry-After": "5"}),
           _FakeResp(200, {"observations": [{"date": "2026-05-28", "value": "1.0"}]})]
    calls = {"n": 0}
    def fake_get(url, params=None, timeout=None):
        r = seq[calls["n"]]
        calls["n"] += 1
        return r
    monkeypatch.setattr(_rq, "get", fake_get)
    monkeypatch.setenv("FRED_API_KEY", "fake")
    cc.fetch_fred_series("DFII10", n=10)
    # Le délai du backoff doit être >= 5s (Retry-After) malgré le jitter
    assert delays and delays[0] >= 5.0


def test_parse_retry_after():
    assert cc._parse_retry_after("3") == 3.0
    assert cc._parse_retry_after(None) is None
    assert cc._parse_retry_after("Wed, 21 Oct 2026 07:28:00 GMT") is None


# ---------------------------------------------------------------------------
# CBOE — parsing CSV + dispatch
# ---------------------------------------------------------------------------

def test_cboe_csv_parsing():
    """Parse CSV CBOE basique : 'date,open,high,low,close'."""
    csv = (
        "Cboe Volatility Index (VIX) Historical Data\n"
        "DATE,OPEN,HIGH,LOW,CLOSE\n"
        "2026-05-29,18.50,19.20,18.10,18.95\n"
        "2026-05-28,18.20,18.80,18.00,18.50\n"
        "2026-05-27,17.90,18.40,17.70,18.20\n"
    )
    out = cc._parse_cboe_csv(csv)
    assert len(out) == 3
    # Tri oldest→newest
    assert out[0][0] == "2026-05-27"
    assert out[-1][0] == "2026-05-29"
    assert out[-1][1] == 18.95


def test_cboe_csv_parsing_skips_invalid_lines():
    csv = (
        "DATE,OPEN,HIGH,LOW,CLOSE\n"
        "2026-05-29,18.5,19.2,18.1,18.95\n"
        "bad,line,with,no,close-numeric\n"
        "2026-05-28,18.2,18.8,18.0,18.50\n"
    )
    out = cc._parse_cboe_csv(csv)
    assert len(out) == 2


def test_cboe_term_structure_vix_vix3m(monkeypatch, now_fixed):
    """term_structure_vix_vix3m → ratio VIX/VIX3M sur dernière date commune."""
    csv_vix = "DATE,OPEN,HIGH,LOW,CLOSE\n2026-05-29,18,19,17,19.0\n2026-05-28,18,19,17,18.5\n"
    csv_vix3m = "DATE,OPEN,HIGH,LOW,CLOSE\n2026-05-29,20,21,19,20.0\n2026-05-28,20,21,19,19.5\n"
    def fake_text(url, timeout=15):
        if "VIX3M" in url:
            return csv_vix3m
        if "VIX" in url:
            return csv_vix
        return None
    monkeypatch.setattr(cc, "http_get_text", fake_text)
    # http_get_json reste mocké à l'erreur — on n'en a pas besoin ici
    crit = {"cle_courante": "term_structure_vix_vix3m", "normalisation": "lineaire",
            "source": "Twelve Data (calculé)"}
    val = cc.build_critere_value("vix", crit, {}, {}, [], now_fixed)
    assert val is not None
    # 19.0 / 20.0 = 0.95
    assert abs(val["valeur"] - 0.95) < 1e-9


def test_cboe_skew_lineaire(monkeypatch, now_fixed):
    csv = "DATE,OPEN,HIGH,LOW,CLOSE\n2026-05-29,130,140,128,135.5\n"
    monkeypatch.setattr(cc, "http_get_text", lambda url, timeout=15: csv)
    crit = {"cle_courante": "skew_index_cboe", "normalisation": "lineaire", "source": "CBOE"}
    val = cc.build_critere_value("vix", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert val["valeur"] == 135.5


def test_cboe_vvix_lineaire(monkeypatch, now_fixed):
    csv = "DATE,OPEN,HIGH,LOW,CLOSE\n2026-05-29,92,98,90,95.2\n"
    monkeypatch.setattr(cc, "http_get_text", lambda url, timeout=15: csv)
    crit = {"cle_courante": "vvix", "normalisation": "lineaire", "source": "CBOE"}
    val = cc.build_critere_value("vix", crit, {}, {}, [], now_fixed)
    assert val is not None
    assert val["valeur"] == 95.2


def test_cboe_dead_returns_none(monkeypatch, now_fixed):
    """Si CBOE renvoie None (HTTP KO), critère omis proprement."""
    monkeypatch.setattr(cc, "http_get_text", lambda url, timeout=15: None)
    crit = {"cle_courante": "skew_index_cboe", "normalisation": "lineaire", "source": "CBOE"}
    val = cc.build_critere_value("vix", crit, {}, {}, [], now_fixed)
    assert val is None
    assert any(k.startswith("cboe_dead:") for k in cc.SKIP_COUNTER)


# ---------------------------------------------------------------------------
# Open-Meteo — routing par zone agri
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cle, lat, lon", [
    ("meteo_ci_ghana_precip_30j", 6.8, -5.3),
    ("meteo_vietnam_robusta", 12.7, 108.1),
    ("meteo_australie_dryland", -33.0, 147.0),
    ("noaa_drought_midwest_plains", 39.0, -98.0),
])
def test_meteo_routing_all_zones(monkeypatch, now_fixed, cle, lat, lon):
    captured = []
    def fake_get(url, params=None, timeout=15):
        captured.append(dict(params or {}))
        return {"daily": {"precipitation_sum": [1.0] * 100}}
    monkeypatch.setattr(cc, "http_get_json", fake_get)
    crit = {"cle_courante": cle, "normalisation": "zscore",
            "source": "Open-Meteo", "zscore_div": 2, "cap": 1.0}
    # Mappe cle → bonne fiche pour le routing
    fiche = {"meteo_ci_ghana_precip_30j": "cacao", "meteo_vietnam_robusta": "cafe",
             "meteo_australie_dryland": "ble", "noaa_drought_midwest_plains": "ble"}[cle]
    cc.build_critere_value(fiche, crit, {}, {}, [], now_fixed)
    assert len(captured) >= 1
    assert captured[0]["latitude"] == lat
    assert captured[0]["longitude"] == lon


def test_meteo_bresil_minas_composite_coords(monkeypatch, now_fixed):
    """meteo_bresil_minas_gerais (composite) → coords -19.9/-43.9."""
    captured = []
    def fake_get(url, params=None, timeout=15):
        captured.append(dict(params or {}))
        return {"daily": {"precipitation_sum": [1.0] * 100}}
    monkeypatch.setattr(cc, "http_get_json", fake_get)
    crit = {"cle_courante": "meteo_bresil_minas_gerais", "normalisation": "composite",
            "source": "NOAA / météo + check T min", "zscore_div": 2, "cap": 1.0}
    cc.build_critere_value("cafe", crit, {}, {}, [], now_fixed)
    assert len(captured) >= 1
    assert captured[0]["latitude"] == -19.9
    assert captured[0]["longitude"] == -43.9


# ---------------------------------------------------------------------------
# Résilience http_get_json (CFTC / EIA / Open-Meteo) — chemin via http_get_retry
# ---------------------------------------------------------------------------
# http_get_json est désormais un wrapper autour du helper partagé
# http_retry.http_get_retry : ces tests vérifient que CFTC/EIA/Open-Meteo
# encaissent un 429/5xx avec retry/backoff au lieu de tomber n/a au 1er coup.
# On restaure le vrai http_get_json (la fixture autouse le stub) et on mocke
# requests.get + neutralise les sleeps du module http_retry.

_REAL_HTTP_GET_JSON = cc.http_get_json


def _patch_http_retry_timing(monkeypatch):
    """Restaure le vrai http_get_json et neutralise throttle/backoff (tests rapides)."""
    import http_retry as _hr
    import time as _t
    monkeypatch.setattr(cc, "http_get_json", _REAL_HTTP_GET_JSON)
    # Le throttle et le backoff du helper partagé dorment via http_retry.time.sleep
    monkeypatch.setattr(_hr.time, "sleep", lambda *_a, **_k: None)
    monkeypatch.setattr(_t, "sleep", lambda *_a, **_k: None)


def test_http_get_json_retry_on_429_then_success(monkeypatch):
    """CFTC : 429 puis 200 → la série revient (pas de cftc_dead)."""
    import requests as _rq
    _patch_http_retry_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    payload = [
        {"report_date_as_yyyy_mm_dd": "2026-05-20",
         "noncomm_positions_long_all": "100", "noncomm_positions_short_all": "40"},
        {"report_date_as_yyyy_mm_dd": "2026-05-13",
         "noncomm_positions_long_all": "90", "noncomm_positions_short_all": "50"},
    ]
    seq = [_FakeResp(429, headers={"Retry-After": "1"}), _FakeResp(200, payload)]
    calls = {"n": 0}
    def fake_get(url, params=None, headers=None, timeout=None):
        r = seq[calls["n"]]
        calls["n"] += 1
        return r
    monkeypatch.setattr(_rq, "get", fake_get)
    nets = cc.fetch_cftc_managed_money_nets("CRUDE OIL")
    assert nets == [40.0, 60.0]  # oldest→newest : (90-50), (100-40)
    assert calls["n"] == 2  # 1 retry consommé
    assert not any(k.startswith("cftc_dead") for k in cc.SKIP_COUNTER)


def test_http_get_json_retry_exhausted_returns_none(monkeypatch):
    """CFTC : 429 sur toutes les tentatives → None + cftc_dead marqué."""
    import requests as _rq
    import http_retry as _hr
    _patch_http_retry_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    calls = {"n": 0}
    def fake_get(url, params=None, headers=None, timeout=None):
        calls["n"] += 1
        return _FakeResp(503)
    monkeypatch.setattr(_rq, "get", fake_get)
    nets = cc.fetch_cftc_managed_money_nets("DEAD MARKET")
    assert nets is None
    assert calls["n"] == _hr.DEFAULT_MAX_RETRIES  # toutes les tentatives consommées
    assert cc.SKIP_COUNTER["cftc_dead:DEAD MARKET"] == 1


def test_http_get_json_no_retry_on_404(monkeypatch):
    """EIA : 404 (non-retriable) → échec immédiat, une seule requête."""
    import requests as _rq
    _patch_http_retry_timing(monkeypatch)
    cc.SKIP_COUNTER.clear()
    monkeypatch.setenv("EIA_API_KEY", "fake")
    calls = {"n": 0}
    def fake_get(url, params=None, headers=None, timeout=None):
        calls["n"] += 1
        return _FakeResp(404)
    monkeypatch.setattr(_rq, "get", fake_get)
    out = cc.fetch_eia_series("petroleum/stoc/wstk/data/", series_id="WCESTUS1")
    assert out is None
    assert calls["n"] == 1  # aucun retry sur 404
    assert any(k.startswith("eia_dead") for k in cc.SKIP_COUNTER)


# ---------------------------------------------------------------------------
# fetch_fred_spread : forward-fill série DE mensuelle sur grille US quotidienne
# ---------------------------------------------------------------------------

def test_fred_spread_forward_fill_monthly_de(monkeypatch):
    """Série DE MENSUELLE + US QUOTIDIENNE → forward-fill → spread calculé (pas thin)."""
    monkeypatch.setenv("FRED_API_KEY", "fake")
    cc.SKIP_COUNTER.clear()
    # US : 12 jours ouvrés quotidiens, valeur constante 4.50
    us_obs = [{"date": f"2026-05-{d:02d}", "value": "4.50"}
              for d in range(11, 23)]  # 12 jours
    # DE : 2 points MENSUELS seulement (début mai et début avril)
    de_obs = [
        {"date": "2026-05-01", "value": "2.50"},
        {"date": "2026-04-01", "value": "2.40"},
    ]
    def fake_get(sid, params, timeout=15):
        if sid == "DGS10":
            return {"observations": us_obs}
        if sid == "IRLTLT01DEM156N":
            return {"observations": de_obs}
        return None
    monkeypatch.setattr(cc, "_fred_get_json", fake_get)
    spread = cc.fetch_fred_spread("DGS10", "IRLTLT01DEM156N", n=260)
    # Sans forward-fill : 0 date commune → thin. Avec : les 12 jours US reportent
    # la dernière valeur DE connue (2.50 du 2026-05-01) → 12 points = 4.50-2.50.
    assert spread is not None
    assert len(spread) == 12
    assert all(abs(s - 2.00) < 1e-9 for s in spread)
    assert not any(k.startswith("fred_spread_thin") for k in cc.SKIP_COUNTER)
