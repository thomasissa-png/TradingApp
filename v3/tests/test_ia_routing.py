"""Tests routage IA-first dans triggers_classifier (prompt v2.1).

Couvre :
- IA-first : un event avec impacts[BRENT:LONG] prime sur le keyword matching.
- IA NEUTRAL (rétro-compat ancien schéma) ne bloque PAS le fallback keyword :
  un actif marqué NEUTRAL = "pas de signal IA" → les keywords du même event
  peuvent matcher (fix bug v2 → v2.1).
- IA sans impact pour cet actif → fallback keyword non bloqué.
- Fallback keyword : événement SANS impacts (ancien schéma) → matching texte.
- Cohabitation : un event IA récent + un event keyword plus ancien → IA gagne.
- Conflit LONG/SHORT IA : matérialité d'abord, date ensuite.
- Rétro-compat events-log : parser supporte 11 ET 14 colonnes.
- Asset hors-énum dans encoded impacts → ignoré.
- Confidence bucket (v2.1) ET legacy entier (v2.0) supportés au décodage.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402


@pytest.fixture
def triggers_cfg():
    return tc.load_triggers_config()


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


def _ev(date_str: str, *, trigger: str = "", cours: str = "", l2: str = "",
        category: str = "", impacts: str = "", materiality: str = "",
        reliability: str = "") -> dict:
    return {
        "date": date_str,
        "l1": "",
        "l2": l2,
        "trigger": trigger,
        "cours": cours,
        "source": "test",
        "news_zone": "Global",
        "category": category,
        "impacts": impacts,
        "materiality": materiality,
        "reliability": reliability,
        "_dt": datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc),
        "_impacts": tc._decode_impacts_str(impacts),
    }


# ---------------------------------------------------------------------------
# IA-first : direction prise depuis impacts[]
# ---------------------------------------------------------------------------

def test_ia_first_long_on_brent(triggers_cfg, now_fixed):
    """Event sans cue keyword mais avec impacts IA → IA décide."""
    ev = _ev(
        "2026-05-28",
        trigger="Oil markets monitor Middle East developments closely",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # IA-first : LONG malgré l'absence du keyword "frappes/airstrikes"
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_ia_first_short_on_brent(triggers_cfg, now_fixed):
    ev = _ev(
        "2026-05-28",
        trigger="Tehran signals talks continuing, prices ease",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:SHORT:medium",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_neutral_legacy_does_not_block_fallback_keyword(triggers_cfg, now_fixed):
    """FIX v2.1 — bug NEUTRAL : un event IA NEUTRAL (rétro-compat ancien schéma)
    ne doit PAS empêcher le fallback keyword de s'activer sur le même event.

    Ici : trigger contient "Iran ceasefire" (keyword SHORT du pétrole), IA legacy
    a marqué NEUTRAL. En v2.0 (bug) : 0 (NEUTRAL bloquait). En v2.1 (fix) : -1.
    """
    ev = _ev(
        "2026-05-28",
        trigger="Iran ceasefire holding, brent stable",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:NEUTRAL:medium",
        materiality="low",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # FIX : le keyword "Iran ceasefire" doit pouvoir trancher → SHORT (-1)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_impact_absent_does_not_block_fallback(triggers_cfg, now_fixed):
    """FIX v2.1 — un event IA dont impacts[] ne mentionne PAS l'actif visé
    (ici BRENT absent) ne doit pas bloquer le fallback keyword pour le pétrole.

    Le scope catégorie reste vérifié, donc l'event doit rester candidat via le
    `cours` ou via les domain_hints. Ici on s'appuie sur le cours=BRENT pour
    rester candidat tout en n'ayant aucun impact IA sur BRENT.
    """
    ev = _ev(
        "2026-05-28",
        trigger="frappes Iran sur infrastructure pétrolière",  # keyword LONG
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        # Impact uniquement sur l'OR, pas sur BRENT — le pétrole doit pouvoir
        # tomber sur le fallback keyword.
        impacts="GOLD:LONG:high",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Fallback keyword "frappes Iran" → LONG pétrole
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
    # En passant, l'or reste piloté par l'IA
    assert res["or"]["tension_geopolitique"] == 1


def test_ia_multi_assets_independants(triggers_cfg, now_fixed):
    """Un event escalade Iran touche BRENT + GOLD + VIX + SP500. Chaque actif
    reçoit la bonne direction depuis ses propres impacts."""
    ev = _ev(
        "2026-05-29",
        trigger="Iran airstrikes escalate, brent and gold surge",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:LONG:high;GOLD:LONG:high;VIX:LONG:medium;SP500:SHORT:medium",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
    assert res["or"]["tension_geopolitique"] == 1
    assert res["vix"]["tension_geopolitique_active"] == 1


# ---------------------------------------------------------------------------
# Fallback keyword : ancien schéma sans impacts
# ---------------------------------------------------------------------------

def test_fallback_keyword_on_legacy_event(triggers_cfg, now_fixed):
    """Event sans `impacts` (ancien schéma) → fallback keyword."""
    ev = _ev(
        "2026-05-28",
        trigger="frappes Iran sur Ormuz",
        cours="Brent (BZ=F)",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="",  # legacy
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Le keyword "frappes Iran" matche le LONG
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_fallback_short_keyword_legacy(triggers_cfg, now_fixed):
    ev = _ev(
        "2026-05-28",
        trigger="cessez-le-feu Iran annoncé",
        cours="Brent (BZ=F)",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_prevails_over_legacy_keyword(triggers_cfg, now_fixed):
    """Si même fenêtre : event IA LONG + event legacy SHORT keyword → IA gagne."""
    ia_ev = _ev(
        "2026-05-29",
        trigger="Iran escalation noted by traders",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    legacy_ev = _ev(
        "2026-05-29",
        trigger="cessez-le-feu Iran annoncé",
        cours="Brent (BZ=F)",
        l2="Iran",
        category="geopolitical",
        impacts="",
    )
    res = tc.classify_all(events=[ia_ev, legacy_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    # ia_seen_any=True (via ia_ev) → on tranche IA-only → LONG
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


# ---------------------------------------------------------------------------
# Conflit IA LONG vs IA SHORT : matérialité puis date
# ---------------------------------------------------------------------------

def test_ia_materiality_breaks_tie(triggers_cfg, now_fixed):
    """Deux events même date : LONG materiality=high vs SHORT materiality=low
    → LONG gagne (poids matérialité)."""
    long_ev = _ev(
        "2026-05-29",
        trigger="Iran tensions",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    short_ev = _ev(
        "2026-05-29",
        trigger="Iran talks",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:medium",
        materiality="low",
    )
    res = tc.classify_all(events=[long_ev, short_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_ia_date_breaks_tie_when_same_materiality(triggers_cfg, now_fixed):
    """Même matérialité : date plus récente gagne."""
    old_ev = _ev(
        "2026-05-25",
        trigger="Iran escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:medium",
        materiality="medium",
    )
    recent_ev = _ev(
        "2026-05-29",
        trigger="Iran ceasefire framework",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:medium",
        materiality="medium",
    )
    res = tc.classify_all(events=[old_ev, recent_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    # Plus récent et même weight → SHORT gagne
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


# ---------------------------------------------------------------------------
# Rétro-compat parsing events-log
# ---------------------------------------------------------------------------

EVENTS_LOG_LEGACY_11 = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-28 |  | Iran | frappes Iran sur Ormuz | Brent (BZ=F) | intraday | 1 | bbc | Moyen-Orient | geopolitical |  |
"""

EVENTS_LOG_V2_14 = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-28 |  | Iran | Iran escalation, brent surges | BRENT |  | 1 | bbc | Moyen-Orient | geopolitical |  | BRENT:LONG:high;GOLD:LONG:high | high | confirmed |
"""


def test_parse_events_log_legacy_11_cols(tmp_path):
    """Format legacy : impacts/materiality/reliability vides."""
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_LOG_LEGACY_11, encoding="utf-8")
    events = tc.parse_events_log(p)
    assert len(events) == 1
    ev = events[0]
    assert ev.get("category") == "geopolitical"
    assert ev.get("impacts", "") == ""
    assert ev.get("materiality", "") == ""
    assert ev.get("_impacts") == []


EVENTS_LOG_MIXED_HEADER_LEGACY_DATA_V2 = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-28 |  | Iran-Moyen-Orient | Report of breakthrough in US-Iran talks, extended ceasefire subject to Trump approval | BRENT |  | 1 | bbc_business | Moyen-Orient | geopolitical |  | BRENT:SHORT:high;GOLD:SHORT:medium;VIX:SHORT:medium;SP500:LONG:medium | high | reported |
| 2026-02-15 |  | Iran | Iran threatens Strait of Hormuz closure (vieux archive) | Brent (BZ=F) | intraday | 1 | bbc | Moyen-Orient | geopolitical |  |
"""


def test_parse_auto_upgrade_v2_when_header_legacy_but_data_v2(tmp_path):
    """FIX bug v2.2 (REGRESSION CRITIQUE) : un header legacy 11 cols suivi de
    lignes data v2 14 cols (append-only sur fichier vivant) DOIT auto-upgrade
    sur DEFAULT_HEADERS — sinon impacts/materiality/reliability sont silencieusement
    ignorés et tout le routage IA-first est désactivé (fallback keyword aveugle
    qui matche des archives).
    """
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_LOG_MIXED_HEADER_LEGACY_DATA_V2, encoding="utf-8")
    events = tc.parse_events_log(p)
    assert len(events) == 2
    # Event v2 (14 cols) DOIT avoir ses impacts décodés.
    ev_v2 = next(e for e in events if e["_dt"].year == 2026 and e["_dt"].month == 5)
    assert ev_v2.get("materiality") == "high"
    assert ev_v2.get("reliability") == "reported"
    decoded = ev_v2.get("_impacts")
    assert any(i["asset"] == "BRENT" and i["direction"] == "SHORT" for i in decoded)


def test_fresh_ia_short_beats_old_keyword_match(triggers_cfg):
    """SCENARIO RÉEL 31/05 (preuve du bug) : un event frais BRENT:SHORT:high
    (détente US-Iran) DOIT primer sur un vieux event archive contenant le mot
    "Iran/Ormuz" sans impacts IA (qui le keyword-matcherait en LONG).

    Avant fix v2.2 : le parser ignorait les impacts → fallback keyword aveugle
    sur les 2 events → "Iran" + "Ormuz" → LONG = +1 (bulletin à contresens).
    Après fix v2.2 : impacts décodés → IA-first ia_seen_any=True → SHORT = -1.
    """
    now = datetime(2026, 5, 31, 23, 59, tzinfo=timezone.utc)
    fresh_short = _ev(
        "2026-05-28",
        trigger="Report of breakthrough in US-Iran talks, extended ceasefire",
        cours="BRENT",
        l2="Iran-Moyen-Orient",
        category="geopolitical",
        impacts="BRENT:SHORT:high",
        materiality="high",
    )
    # Archive vieux mais dans la fenêtre (lookback geopol_iran=7j) :
    old_archive_keyword = _ev(
        "2026-05-26",
        trigger="frappes Iran sur Ormuz (archive)",
        cours="Brent (BZ=F)",
        l2="Iran",
        category="geopolitical",
        impacts="",  # legacy : pas d'impacts IA
    )
    res = tc.classify_all(events=[fresh_short, old_archive_keyword],
                          today=now, triggers_cfg=triggers_cfg)
    # SHORT IA prime — le keyword "frappes Iran" sur le vieux event est ignoré
    # car ia_seen_any=True (présence d'un signal IA exploitable pour BRENT).
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_cafe_penurie_haussiere_long(triggers_cfg):
    """Café : mauvaises récoltes Brésil/Vietnam → COFFEE:LONG → critère LONG.
    Régression : avant fix v2.2, le keyword fallback ne matchait aucun mot-clé
    coffee_rust spécifique → critère restait 0. Avec IA-first, la pénurie
    haussière donne bien +1.
    """
    now = datetime(2026, 5, 31, 23, 59, tzinfo=timezone.utc)
    ev = _ev(
        "2026-05-27",
        trigger="Mauvaises recoltes de cafe au Bresil et au Vietnam font grimper les prix",
        cours="COFFEE",
        l2="Cafe",
        category="commodity",
        impacts="COFFEE:LONG:medium",
        materiality="medium",
    )
    res = tc.classify_all(events=[ev], today=now, triggers_cfg=triggers_cfg)
    # Critère café maladies_cabosses → cle_courante "maladies_cabosses_rouille"
    assert res["cafe"]["maladies_cabosses_rouille"] == 1


def test_parse_events_log_v2_14_cols(tmp_path):
    """Format v2 : impacts décodés, materiality/reliability remplis."""
    p = tmp_path / "events-log.md"
    p.write_text(EVENTS_LOG_V2_14, encoding="utf-8")
    events = tc.parse_events_log(p)
    assert len(events) == 1
    ev = events[0]
    assert ev.get("materiality") == "high"
    assert ev.get("reliability") == "confirmed"
    assert ev.get("impacts") == "BRENT:LONG:high;GOLD:LONG:high"
    decoded = ev.get("_impacts")
    assert len(decoded) == 2
    assert decoded[0]["asset"] == "BRENT"
    assert decoded[0]["direction"] == "LONG"
    assert decoded[0]["confidence"] == "high"


def test_parse_events_log_v2_routes_correctly(tmp_path, triggers_cfg):
    """Bout en bout : ligne v2 parsée → classify_all → triplet correct via IA.

    NOTE (v2.2 Phase 2, format 19 col — CHANGELOG) : `parse_events_log` calcule
    désormais le flag `stale` (canonical_event_date > STALE_DAYS vs HORLOGE RÉELLE
    → event écarté du routing, cf. triggers_classifier L1341-1342). La date figée
    2026-05-28 devient donc stale dès qu'on exécute la suite > 30j plus tard, et le
    routing retourne 0 (faux négatif de test, PAS une régression code). On date
    l'event à J-1 réel et on route avec today=maintenant : l'event reste NON stale
    ET dans le lookback geopol_iran (7j).
    """
    now = datetime.now(timezone.utc)
    d_recent = (now - timedelta(days=1)).date().isoformat()
    log_v2 = (
        "| date | L1 | L2 | trigger | cours | latence | R | source | news_zone "
        "| category | pattern_id | impacts | materiality | reliability |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        f"| {d_recent} |  | Iran | Iran escalation, brent surges | BRENT |  | 1 "
        "| bbc | Moyen-Orient | geopolitical |  | BRENT:LONG:high;GOLD:LONG:high "
        "| high | confirmed |\n"
    )
    p = tmp_path / "events-log.md"
    p.write_text(log_v2, encoding="utf-8")
    events = tc.parse_events_log(p)
    res = tc.classify_all(events=events, today=now, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
    assert res["or"]["tension_geopolitique"] == 1


# ---------------------------------------------------------------------------
# Décodage robuste
# ---------------------------------------------------------------------------

def test_decode_ignores_unknown_asset():
    out = tc._decode_impacts_str("DOGECOIN:LONG:high;BRENT:LONG:high")
    assert len(out) == 1
    assert out[0]["asset"] == "BRENT"


def test_decode_ignores_unknown_direction():
    out = tc._decode_impacts_str("BRENT:WHATEVER:high")
    assert out == []


def test_decode_empty_string():
    assert tc._decode_impacts_str("") == []
    assert tc._decode_impacts_str(None) == []  # type: ignore[arg-type]


def test_decode_legacy_integer_confidence():
    """Rétro-compat : ancien schéma 'BRENT:LONG:85' → bucket 'high'."""
    out = tc._decode_impacts_str("BRENT:LONG:85;GOLD:LONG:50;VIX:LONG:10")
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"
    assert out[2]["confidence"] == "low"


def test_decode_bucket_confidence():
    """v2.1 : confidence directement en bucket."""
    out = tc._decode_impacts_str("BRENT:LONG:high;GOLD:LONG:medium;VIX:LONG:low")
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"
    assert out[2]["confidence"] == "low"


# ---------------------------------------------------------------------------
# Lookback respecté en mode IA
# ---------------------------------------------------------------------------

def test_ia_lookback_respecte(triggers_cfg, now_fixed):
    old_dt = (now_fixed - timedelta(days=30)).date().isoformat()
    ev = _ev(
        old_dt,
        trigger="Iran escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    # Hors fenêtre 7j de geopol_iran → 0
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


# ---------------------------------------------------------------------------
# Scope catégorie s'applique aussi à l'IA
# ---------------------------------------------------------------------------

def test_ia_blocked_by_category_scope(triggers_cfg, now_fixed):
    """Event impacts[BRENT:LONG] mais category=earnings → bloqué par scope geopol."""
    ev = _ev(
        "2026-05-28",
        trigger="Some random earnings note mentioning oil",
        cours="BRENT",
        l2="Earnings",
        category="earnings",  # pas geopolitical
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    res = tc.classify_all(events=[ev], today=now_fixed, triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


# ---------------------------------------------------------------------------
# Conflit IA non tranchable (audit DeepSeek)
# ---------------------------------------------------------------------------

def test_ia_conflict_same_materiality_same_day_returns_zero(triggers_cfg, now_fixed):
    """Conflit LONG vs SHORT, même materiality_weight, même jour → 0 (neutre)
    au lieu d'un arbitrage `>=` qui forçait LONG par hasard d'ordre."""
    long_ev = _ev(
        "2026-05-29",
        trigger="Iran tensions on the rise",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="medium",
    )
    short_ev = _ev(
        "2026-05-29",
        trigger="Iran de-escalation rumours",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:high",
        materiality="medium",
    )
    res = tc.classify_all(events=[long_ev, short_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 0


def test_ia_conflict_meta_exposes_source_track(triggers_cfg, now_fixed):
    """Le conflit IA non tranché expose source_track='ia_conflict' dans le meta."""
    long_ev = _ev(
        "2026-05-29",
        trigger="Iran tensions",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="medium",
    )
    short_ev = _ev(
        "2026-05-29",
        trigger="Iran de-escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:high",
        materiality="medium",
    )
    val, meta = tc._resolve_triplet_with_meta(
        events=[long_ev, short_ev],
        actif_key="petrole",
        # Clé interne triggers-and-windows.yml (la cle fiche
        # "tension_geopol_moyen_orient" est dérivée via YML_KEY_TO_CLE_COURANTE).
        cle="geopol_iran",
        long_keywords=[],
        short_keywords=[],
        lookback_days=7,
        now=now_fixed,
    )
    assert val == 0
    assert meta.get("source_track") == "ia_conflict"
    # Les matérialités des deux côtés sont exposées pour audit/decision-log.
    assert meta.get("conflict_long_materiality") == "medium"
    assert meta.get("conflict_short_materiality") == "medium"


def test_ia_strict_materiality_domination_long_wins(triggers_cfg, now_fixed):
    """Domination STRICTE de matérialité : LONG high vs SHORT low → LONG."""
    long_ev = _ev(
        "2026-05-29",
        trigger="Iran escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="high",
    )
    short_ev = _ev(
        "2026-05-29",
        trigger="Iran chatter",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:low",
        materiality="low",
    )
    res = tc.classify_all(events=[long_ev, short_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1


def test_ia_conflict_same_materiality_one_day_apart_recent_wins(triggers_cfg, now_fixed):
    """Weights égaux MAIS écart ≥ 1 jour → le plus récent gagne (signal frais)."""
    old_ev = _ev(
        "2026-05-27",
        trigger="Iran escalation",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:high",
        materiality="medium",
    )
    recent_ev = _ev(
        "2026-05-29",
        trigger="Iran ceasefire framework",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:SHORT:high",
        materiality="medium",
    )
    res = tc.classify_all(events=[old_ev, recent_ev], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    # Écart de 2 jours → SHORT (plus récent) gagne malgré weights égaux.
    assert res["petrole"]["tension_geopol_moyen_orient"] == -1


def test_ia_basket_of_lows_does_not_dominate_medium_event(triggers_cfg, now_fixed):
    """Garde anti-sur-extraction : un panier de 4 impacts low d'un même event ne
    domine pas un signal medium provenant d'un autre event.

    Mécanisme actuel : la matérialité de chaque event est figée au niveau de
    l'event (champ `materiality`), pas calculée par sommation des confidences
    des impacts. Donc un event "panier low" avec materiality='low' a un
    _MAT_WEIGHT=1, alors qu'un event medium dédié a _MAT_WEIGHT=2 → le medium
    l'emporte. On documente et on vérifie le comportement.
    """
    basket_low = _ev(
        "2026-05-29",
        trigger="Markets roundup of macro flows",
        cours="BRENT",
        l2="Macro",
        category="geopolitical",
        impacts="BRENT:SHORT:low;GOLD:LONG:low;VIX:LONG:low;SP500:SHORT:low",
        materiality="low",
    )
    focused_medium = _ev(
        "2026-05-29",
        trigger="Iran tension report",
        cours="BRENT",
        l2="Iran",
        category="geopolitical",
        impacts="BRENT:LONG:medium",
        materiality="medium",
    )
    res = tc.classify_all(events=[basket_low, focused_medium], today=now_fixed,
                          triggers_cfg=triggers_cfg)
    # _MAT_WEIGHT(medium)=2 > _MAT_WEIGHT(low)=1 → domination stricte → LONG.
    assert res["petrole"]["tension_geopol_moyen_orient"] == 1
