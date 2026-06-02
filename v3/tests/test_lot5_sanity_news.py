"""Tests Lot 5 — sanity sémantique des news (FLAG-ONLY, mode shadow).

Gates :
- C8a : already_priced relatif à l'horizon (fenêtre tunable par horizon).
- C8b : démenti / correction détecté par mots-clés (word-bounded, FR + EN).

Garde-fous obligatoires (cf. brief Lot 5) :
- Les conclusions / scores / pondérations restent INCHANGÉES quand un flag est posé.
- Flag tracé dans le decision-log seulement si True (zéro bruit).
- Zéro invention : event_date absente → pas de flag.
- Word-boundary strict : pas de faux match sur substring.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Permet d'importer les modules v3/scripts
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import triggers_classifier as tc  # noqa: E402
import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# C8a — already_priced relatif à l'horizon
# ---------------------------------------------------------------------------

def test_c8a_window_constants_documented():
    """Les fenêtres ALREADY_PRICED_WINDOW doivent couvrir les 3 horizons standard."""
    assert set(tc.ALREADY_PRICED_WINDOW.keys()) == {"24h", "7j", "1m"}
    # Ordre strictement croissant (cohérent avec horizons)
    assert tc.ALREADY_PRICED_WINDOW["24h"] < tc.ALREADY_PRICED_WINDOW["7j"]
    assert tc.ALREADY_PRICED_WINDOW["7j"] < tc.ALREADY_PRICED_WINDOW["1m"]


def test_c8a_event_3j_on_24h_is_already_priced():
    """Event 3j sur horizon 24h → already_priced=True (fenêtre 24h = 1j)."""
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(days=3)
    ap, age = tc.compute_already_priced_for_horizon(cdt, "24h", now=now)
    assert ap is True
    assert age is not None
    assert 2.9 < age < 3.1


def test_c8a_event_6h_on_24h_is_not_already_priced():
    """Event 6h sur horizon 24h → already_priced=False (fenêtre 24h = 1j > 6h)."""
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(hours=6)
    ap, age = tc.compute_already_priced_for_horizon(cdt, "24h", now=now)
    assert ap is False
    assert age is not None
    assert 0.2 < age < 0.3


def test_c8a_event_date_missing_no_flag():
    """Zéro invention : event_date manquante (None) → pas de flag, age=None."""
    ap, age = tc.compute_already_priced_for_horizon(None, "24h")
    assert ap is False
    assert age is None


def test_c8a_event_2j_on_7j_is_not_already_priced():
    """Event 2j sur horizon 7j → already_priced=False (fenêtre 7j = 3j)."""
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(days=2)
    ap, _ = tc.compute_already_priced_for_horizon(cdt, "7j", now=now)
    assert ap is False


def test_c8a_event_5j_on_7j_is_already_priced():
    """Event 5j sur horizon 7j → already_priced=True (fenêtre 7j = 3j < 5j)."""
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(days=5)
    ap, _ = tc.compute_already_priced_for_horizon(cdt, "7j", now=now)
    assert ap is True


def test_c8a_event_15j_on_1m_is_already_priced():
    """Event 15j sur horizon 1m → already_priced=True (fenêtre 1m = 10j)."""
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(days=15)
    ap, _ = tc.compute_already_priced_for_horizon(cdt, "1m", now=now)
    assert ap is True


def test_c8a_unknown_horizon_no_flag():
    """Horizon inconnu → pas de flag (zéro invention de fenêtre)."""
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(days=100)
    ap, age = tc.compute_already_priced_for_horizon(cdt, "_unknown_", now=now)
    assert ap is False
    assert age is not None  # l'âge reste calculable


# ---------------------------------------------------------------------------
# C8b — détection démenti / correction
# ---------------------------------------------------------------------------

def test_c8b_french_dement_matches():
    """Titre « La BCE dément… » → is_denial=True (FR, indicatif 3e pers)."""
    is_d, kw = tc.detect_denial("La BCE dement les rumeurs de hausse de taux")
    assert is_d is True
    assert kw  # mot-clé matché renseigné


def test_c8b_french_dementi_with_accent():
    """Accent strippé via _norm : « démenti » matche le keyword 'dementi'."""
    is_d, kw = tc.detect_denial("Démenti officiel du ministère")
    assert is_d is True
    assert kw == "dementi"


def test_c8b_english_denies_matches():
    """Titre EN « Fed denies imminent rate cut » → is_denial=True."""
    is_d, kw = tc.detect_denial("Fed denies imminent rate cut")
    assert is_d is True
    assert kw == "denies"


def test_c8b_english_no_longer_multitoken():
    """Multi-token AND : « no longer » matche dans n'importe quel ordre."""
    is_d, _ = tc.detect_denial("Company says rate hike no longer expected")
    assert is_d is True


def test_c8b_normal_title_no_match():
    """Titre normal → False (pas de faux positif)."""
    is_d, kw = tc.detect_denial("La BCE relève ses taux de 25bp")
    assert is_d is False
    assert kw == ""


def test_c8b_empty_text_no_match():
    is_d, _ = tc.detect_denial("")
    assert is_d is False


def test_c8b_word_boundary_no_false_match_dementir():
    """Word-boundary : « démentir » ne matche PAS 'dement' (frontière non-mot
    requise : 'dement' doit être suivi d'un non-token, pas de 'i').

    Note : « démentir » strippé → « dementir ». Token = 'dementir'.
    Keyword 'dement' tenté en phrase exacte sur 'dementir' → ne matche pas
    (lookaround `(?![a-z0-9_])` échoue, 'i' = alphanum). Et 'dement' est
    mono-token → pas de fallback tokens AND.
    """
    is_d, _ = tc.detect_denial("Le gouvernement va démentir cette information demain")
    # 'dementir' contient 'dement' en substring mais pas en token bound.
    # ⇒ pas de match → False.
    assert is_d is False


def test_c8b_word_boundary_no_false_match_correctement():
    """« correctement » ne doit PAS matcher 'correction' (substring distinct)."""
    is_d, _ = tc.detect_denial("La banque fonctionne correctement")
    assert is_d is False


def test_c8b_retract_variants():
    """Variantes anglaises : retract, retracts, retracted."""
    for variant in ("Reuters retracts story", "Source retracted statement",
                    "Editor will retract article"):
        is_d, _ = tc.detect_denial(variant)
        assert is_d, f"variant non détectée : {variant!r}"


# ---------------------------------------------------------------------------
# Propagation : parse_events_log marque is_denial à l'ingestion
# ---------------------------------------------------------------------------

def test_c8b_parse_events_log_marks_is_denial(tmp_path):
    """parse_events_log applique detect_denial → ev['is_denial']=True si match."""
    log = tmp_path / "events-log.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log.write_text(
        "| date | l1 | l2 | trigger | cours | latence | r | source | news_zone | category | pattern_id |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
        f"| {today} | A | B | La Fed dement la rumeur de QE | ^GSPC | 1 | T | reuters | US | macro | p1 |\n"
        f"| {today} | A | B | Fed relève ses taux | ^GSPC | 1 | T | reuters | US | macro | p2 |\n",
        encoding="utf-8",
    )
    events = tc.parse_events_log(log)
    assert len(events) == 2
    denials = [e for e in events if e.get("is_denial")]
    normals = [e for e in events if not e.get("is_denial")]
    assert len(denials) == 1
    assert "dement" in denials[0]["denial_keyword"].lower()
    assert len(normals) == 1


# ---------------------------------------------------------------------------
# C8a + C8b — emission dans decision-log SEULEMENT si True (zéro bruit)
# ---------------------------------------------------------------------------

def _make_actif_with_news_critere(
    *, event_age_days: float, is_denial: bool = False,
    nature: str = "structurel", conclusion_24h: str = "LONG",
) -> sa.ActifResult:
    """Forge un ActifResult minimal avec un critère news.

    On simule : un critère news IA, event_date = now - event_age_days.
    """
    now = datetime.now(timezone.utc)
    cdt = now - timedelta(days=event_age_days)
    crit = sa.CritereResult(
        id="news_test",
        nom="news_test",
        type_norm="signal_directionnel",
        valeur_brute={"valeur": 1},
        valeur_norm=1.0,
        poids=5.0,
        signe=1,
        pertinence={"24h": 1.0, "7j": 1.0, "1m": 1.0},
        note="",
        contributions={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        contributions_pond={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        materiality="high",
        reliability="confirmed",
        source_track="ia",
        cle_courante="news_test",
        nature=nature,
        event_id="ABC123",
        event_date=cdt.isoformat(),
        event_date_source="rss",
        freshness_days=event_age_days,
        is_denial=is_denial,
        denial_keyword="dement" if is_denial else "",
    )
    return sa.ActifResult(
        nom="TestActif",
        fiche_key="test",
        criteres=[crit],
        scores={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        conclusions={"24h": conclusion_24h, "7j": conclusion_24h, "1m": conclusion_24h},
        tie_break_notes={},
        scores_pond={"24h": 5.0, "7j": 5.0, "1m": 5.0},
        conclusions_pond={"24h": conclusion_24h, "7j": conclusion_24h, "1m": conclusion_24h},
        tie_break_notes_pond={},
        diverge={},
        news_cap_info={
            "24h": {"news_total_pm1": 5.0, "quant_total_pm1": 0.0},
            "7j":  {"news_total_pm1": 5.0, "quant_total_pm1": 0.0},
            "1m":  {"news_total_pm1": 5.0, "quant_total_pm1": 0.0},
        },
        coverage=1.0,
        confidence={"24h": "normale", "7j": "normale", "1m": "normale"},
    )


def test_decision_log_emits_already_priced_only_when_true():
    """Event 2j → already_priced=True sur 24h (1j), False sur 7j (3j) et 1m (10j)."""
    actif = _make_actif_with_news_critere(event_age_days=2.0)
    now = datetime.now(timezone.utc)
    records = sa.build_decision_log_records([actif], now)
    by_h = {r["horizon"]: r for r in records}

    # 24h : déjà coté (2j > 1j)
    crit_24h = by_h["24h"]["criteres"][0]
    assert crit_24h.get("already_priced") is True
    assert crit_24h.get("already_priced_horizon") == "24h"
    assert "already_priced_age_days" in crit_24h

    # 7j : non déjà coté (2j < 3j)
    crit_7j = by_h["7j"]["criteres"][0]
    assert "already_priced" not in crit_7j  # zéro bruit

    # 1m : non déjà coté (2j < 10j)
    crit_1m = by_h["1m"]["criteres"][0]
    assert "already_priced" not in crit_1m


def test_decision_log_emits_is_denial_only_when_true():
    """is_denial=True sur le critère → champ tracé dans toutes les cellules.
    is_denial=False → champ ABSENT (zéro bruit)."""
    now = datetime.now(timezone.utc)

    # Cas True
    actif_d = _make_actif_with_news_critere(event_age_days=0.5, is_denial=True)
    records_d = sa.build_decision_log_records([actif_d], now)
    for r in records_d:
        crit = r["criteres"][0]
        assert crit.get("is_denial") is True
        assert crit.get("denial_keyword")

    # Cas False
    actif_n = _make_actif_with_news_critere(event_age_days=0.5, is_denial=False)
    records_n = sa.build_decision_log_records([actif_n], now)
    for r in records_n:
        crit = r["criteres"][0]
        assert "is_denial" not in crit  # zéro bruit
        assert "denial_keyword" not in crit


# ---------------------------------------------------------------------------
# Garde-fou CRITIQUE : conclusions INCHANGÉES quand un flag est posé
# ---------------------------------------------------------------------------

def test_conclusions_unchanged_when_already_priced():
    """Mode shadow : un event déjà coté NE doit pas inverser la conclusion."""
    actif = _make_actif_with_news_critere(
        event_age_days=20.0,  # déjà coté sur les 3 horizons (>1j, >3j, >10j)
        conclusion_24h="LONG",
    )
    # Le constructeur a forgé LONG sur les 3 horizons.
    # On vérifie que les conclusions persistent telles quelles dans le decision-log.
    records = sa.build_decision_log_records([actif], datetime.now(timezone.utc))
    for r in records:
        assert r["conclusion_pm1"] == "LONG"
        assert r["score_pm1"] == 5.0
        # Le flag DOIT être présent
        assert r["criteres"][0].get("already_priced") is True


def test_conclusions_unchanged_when_is_denial():
    """Mode shadow : un démenti NE doit pas inverser la conclusion."""
    actif = _make_actif_with_news_critere(
        event_age_days=0.5,
        is_denial=True,
        conclusion_24h="LONG",
    )
    records = sa.build_decision_log_records([actif], datetime.now(timezone.utc))
    for r in records:
        assert r["conclusion_pm1"] == "LONG"
        assert r["score_pm1"] == 5.0
        assert r["criteres"][0].get("is_denial") is True


# ---------------------------------------------------------------------------
# Bulletin : marqueurs visuels présents quand flag True
# ---------------------------------------------------------------------------

def test_bulletin_shows_already_priced_marker():
    """⌛ apparait dans la cellule 24h pour un event de 2j (>1j, <3j, <10j)."""
    actif = _make_actif_with_news_critere(event_age_days=2.0)
    now = datetime.now(timezone.utc)
    md = sa.render_bulletin([actif], {}, now, "hash", "ok")
    # La ligne TestActif doit contenir ⌛ pour 24h. On lit la MATRICE détaillée
    # (pas la Synthèse compacte du haut, qui omet les flags ⌛/⊘).
    matrix_section = md.split("## Synthèse des décisions")[1].split("## Détail")[0]
    matrice_line = [l for l in matrix_section.splitlines() if "TestActif" in l and "|" in l]
    assert matrice_line, "Ligne actif introuvable dans la matrice"
    line = matrice_line[0]
    # 24h est la 2e cellule (après nom)
    cells = [c.strip() for c in line.split("|") if c.strip()]
    # ["TestActif", "<24h>", "<7j>", "<1m>"]
    assert "⌛" in cells[1], f"marqueur déjà-coté absent en 24h : {cells[1]!r}"
    # 7j et 1m ne portent PAS le marqueur (2j < 3j et 2j < 10j)
    assert "⌛" not in cells[2]
    assert "⌛" not in cells[3]
    # Légende doit mentionner ⌛
    assert "⌛" in md
    assert "déjà coté" in md or "deja cote" in md.lower()


def test_bulletin_shows_denial_marker():
    """⊘ apparait dans toutes les cellules (le démenti est sur l'event source)."""
    actif = _make_actif_with_news_critere(event_age_days=0.5, is_denial=True)
    md = sa.render_bulletin([actif], {}, datetime.now(timezone.utc), "h", "ok")
    matrix_section = md.split("## Synthèse des décisions")[1].split("## Détail")[0]
    matrice_line = [l for l in matrix_section.splitlines() if "TestActif" in l and "|" in l][0]
    cells = [c.strip() for c in matrice_line.split("|") if c.strip()]
    for h_cell in cells[1:4]:
        assert "⊘" in h_cell, f"marqueur démenti absent : {h_cell!r}"
    assert "⊘" in md
    assert "démenti" in md or "dementi" in md.lower()


def test_bulletin_no_marker_when_no_flag():
    """Cellule sans flag → ni ⌛ ni ⊘."""
    actif = _make_actif_with_news_critere(event_age_days=0.1, is_denial=False)
    md = sa.render_bulletin([actif], {}, datetime.now(timezone.utc), "h", "ok")
    matrix_section = md.split("## Synthèse des décisions")[1].split("## Détail")[0]
    matrice_line = [l for l in matrix_section.splitlines() if "TestActif" in l and "|" in l][0]
    cells = [c.strip() for c in matrice_line.split("|") if c.strip()]
    for h_cell in cells[1:4]:
        assert "⌛" not in h_cell
        assert "⊘" not in h_cell
