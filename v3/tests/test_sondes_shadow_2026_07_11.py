"""Tests ciblés — SONDES SHADOW (GO fondateur 11/07, risque « tendance 3j mûre »).

TRAÇAGE PUR au decision-log. ZÉRO changement de call / conclusion / note /
Sélection. WIN RATE ONLY. On MESURE, rien d'autre.

Sonde 1 « confirmation post-flip » :
  - shadow_flip_j0   : ce record est un flip du jour (sens ≠ veille, francs).
  - shadow_flip_conf : ce record CONFIRME un flip d'hier (sens jour == veille ≠
    avant-veille, les trois francs).

Sonde 2 « catalyseur épuisé » :
  - shadow_cat_epuise : critère dominant = momentum_prix_3j_* saturé (|vn|≥0.999)
    ET à CONTRE-SENS du trio de fond (7j + 20j + synthèse news).
  - shadow_sens_fond  : sens du trio de fond ("LONG"/"SHORT") si config vraie,
    None sinon. Cas fondateur rejoué : café 09/07.

Invariance : aucune conclusion / sélection ne bouge quand les sondes tournent.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import scoring_analyste as sa  # noqa: E402

_NOW = datetime(2026, 7, 11, 7, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _isole_news_flux(monkeypatch):
    """Isole du feed news LIVE (même parade que test_selection_du_jour) : aucune
    news adverse par défaut, les sondes ne dépendent pas des données du jour."""
    import bilan_jour as bj  # noqa: PLC0415
    monkeypatch.setattr(bj, "cause_news_high_dir", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", lambda now: {}, raising=False)


# ---------------------------------------------------------------------------
# Fabriques minimales
# ---------------------------------------------------------------------------

def _crit(
    nom: str,
    cle: str,
    contrib_24h: float,
    *,
    valeur_norm: float = 1.0,
    source_track: str = "",
    is_na: bool = False,
    is_gate: bool = False,
) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle, nom=nom, type_norm="lineaire", valeur_brute=1.0,
        valeur_norm=valeur_norm, poids=1.0 / 3.0, signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS}, note="",
        contributions={h: (contrib_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        cle_courante=cle, source_track=source_track,
        is_gate=is_gate, is_na=is_na,
    )


def _actif(
    nom: str, fiche_key: str, criteres: List[sa.CritereResult],
    *, direction: str = "LONG", score_24h: float = 2.0,
) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom, fiche_key=fiche_key, criteres=criteres,
        scores={h: (score_24h if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (direction if h == "24h" else sa.CONCLUSION_INSUFFISANT)
                     for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS}, tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS}, coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


def _cafe_09_07() -> sa.ActifResult:
    """Cas fondateur café 09/07 : 3j saturé -1.0 DOMINANT, news +, 7j +, 20j +.
    Fond (0.5 + 0.4 + 0.3 = +1.2) OPPOSÉ au 3j (-1.0) → épuisé=True, fond=LONG."""
    return _actif("Café (Arabica)", "cafe", [
        _crit("Tendance 3 jours", "momentum_prix_3j_cafe", -1.0, valeur_norm=-1.0),
        _crit("Tendance 7 jours", "momentum_prix_7j_cafe", +0.5),
        _crit("Tendance 20 jours", "momentum_prix_20j_cafe", +0.4),
        _crit("Synthèse news (net)", "synthese_cafe", +0.3, source_track="ia_synthese"),
    ], direction="SHORT")


# ---------------------------------------------------------------------------
# SONDE 1 — compute_shadow_flip_fields (unitaire)
# ---------------------------------------------------------------------------

def test_flip_j0():
    j0, conf = sa.compute_shadow_flip_fields("LONG", "SHORT", "SHORT")
    assert j0 is True and conf is False


def test_confirmation_j1():
    # sens jour == veille (LONG) ≠ avant-veille (SHORT) → confirmation d'un flip.
    j0, conf = sa.compute_shadow_flip_fields("LONG", "LONG", "SHORT")
    assert j0 is False and conf is True


def test_pas_de_flip_continuation_stable():
    # 3 jours dans le même sens : ni flip ni confirmation de flip.
    j0, conf = sa.compute_shadow_flip_fields("LONG", "LONG", "LONG")
    assert j0 is False and conf is False


def test_exclusivite_j0_vs_conf():
    # Un flip J0 ne peut pas être aussi une confirmation.
    j0, conf = sa.compute_shadow_flip_fields("SHORT", "LONG", "LONG")
    assert j0 is True and conf is False


def test_sens_non_franc_tout_false():
    assert sa.compute_shadow_flip_fields("INSUFFISANT", "SHORT", "SHORT") == (False, False)
    assert sa.compute_shadow_flip_fields("LONG", None, "SHORT") == (False, False)
    # avant-veille introuvable → confirmation non calculable (best-effort False),
    # mais le flip J0 reste détectable.
    assert sa.compute_shadow_flip_fields("LONG", "SHORT", None) == (True, False)
    assert sa.compute_shadow_flip_fields("LONG", "LONG", None) == (False, False)


# ---------------------------------------------------------------------------
# SONDE 2 — compute_shadow_cat_epuise (unitaire)
# ---------------------------------------------------------------------------

def test_cat_epuise_cafe_09_07():
    epuise, sens = sa.compute_shadow_cat_epuise(_cafe_09_07(), "24h")
    assert epuise is True and sens == "LONG"


def test_cat_epuise_symetrique_short():
    # 3j saturé +1.0 dominant, fond négatif (7j/20j/news < 0) → fond SHORT.
    a = _actif("Cacao", "cacao_x", [
        _crit("3j", "momentum_prix_3j_cacao", +1.0, valeur_norm=+1.0),
        _crit("7j", "momentum_prix_7j_cacao", -0.4),
        _crit("20j", "momentum_prix_20j_cacao", -0.3),
        _crit("news", "synthese_cacao", -0.2, source_track="keyword"),
    ])
    epuise, sens = sa.compute_shadow_cat_epuise(a, "24h")
    assert epuise is True and sens == "SHORT"


def test_cat_non_epuise_3j_non_sature():
    a = _actif("Café", "cafe", [
        _crit("3j", "momentum_prix_3j_cafe", -0.6, valeur_norm=-0.6),  # |vn| < 0.999
        _crit("7j", "momentum_prix_7j_cafe", +0.3),
        _crit("news", "synthese_cafe", +0.2, source_track="ia_synthese"),
    ])
    assert sa.compute_shadow_cat_epuise(a, "24h") == (False, None)


def test_cat_non_epuise_fond_meme_sens():
    # 3j saturé -1.0 mais fond AUSSI négatif → pas de contre-sens.
    a = _actif("Café", "cafe", [
        _crit("3j", "momentum_prix_3j_cafe", -1.0, valeur_norm=-1.0),
        _crit("7j", "momentum_prix_7j_cafe", -0.3),
        _crit("news", "synthese_cafe", -0.2, source_track="ia_synthese"),
    ])
    assert sa.compute_shadow_cat_epuise(a, "24h") == (False, None)


def test_cat_non_epuise_dominant_pas_3j():
    # Le dominant est un critère de fond, pas le 3j → config non déclenchée.
    a = _actif("Café", "cafe", [
        _crit("3j", "momentum_prix_3j_cafe", -0.2, valeur_norm=-1.0),
        _crit("7j", "momentum_prix_7j_cafe", +0.9),  # dominant
        _crit("news", "synthese_cafe", +0.2, source_track="ia_synthese"),
    ])
    assert sa.compute_shadow_cat_epuise(a, "24h") == (False, None)


def test_cat_3j_na_ignore():
    # 3j n/a → exclu du dominant → pas de config.
    a = _actif("Café", "cafe", [
        _crit("3j", "momentum_prix_3j_cafe", -1.0, valeur_norm=-1.0, is_na=True),
        _crit("7j", "momentum_prix_7j_cafe", +0.5),
        _crit("news", "synthese_cafe", +0.2, source_track="ia_synthese"),
    ])
    assert sa.compute_shadow_cat_epuise(a, "24h") == (False, None)


# ---------------------------------------------------------------------------
# INTÉGRATION — build_decision_log_records (champs persistés + invariance)
# ---------------------------------------------------------------------------

def _rec_24h(records: List[dict], fiche_key: str) -> dict:
    for rec in records:
        if rec["fiche_key"] == fiche_key and rec["horizon"] == "24h":
            return rec
    raise AssertionError(f"record 24h introuvable pour {fiche_key}")


def test_champs_persistes_sur_24h_uniquement():
    a = _cafe_09_07()
    records = sa.build_decision_log_records(
        [a], _NOW, veille_conclusions={}, avant_veille_conclusions={},
    )
    rec24 = _rec_24h(records, "cafe")
    for champ in ("shadow_flip_j0", "shadow_flip_conf",
                  "shadow_cat_epuise", "shadow_sens_fond"):
        assert champ in rec24, champ
    # Pas sur 7j / 1m (les sondes sont définies sur le pari 24h).
    for rec in records:
        if rec["horizon"] != "24h":
            assert "shadow_flip_j0" not in rec
            assert "shadow_cat_epuise" not in rec


def test_integration_cafe_cat_epuise():
    records = sa.build_decision_log_records(
        [_cafe_09_07()], _NOW, veille_conclusions={}, avant_veille_conclusions={},
    )
    rec = _rec_24h(records, "cafe")
    assert rec["shadow_cat_epuise"] is True
    assert rec["shadow_sens_fond"] == "LONG"


def test_integration_flip_j0_et_confirmation():
    a = _actif("Or", "or", [_crit("3j", "momentum_prix_3j_or", +0.5, valeur_norm=0.5)],
               direction="LONG")
    # Flip J0 : aujourd'hui LONG, veille SHORT.
    r_j0 = sa.build_decision_log_records(
        [a], _NOW, veille_conclusions={"or": {"24h": "SHORT"}},
        avant_veille_conclusions={"or": {"24h": "SHORT"}},
    )
    rec = _rec_24h(r_j0, "or")
    assert rec["shadow_flip_j0"] is True and rec["shadow_flip_conf"] is False
    # Confirmation J+1 : aujourd'hui LONG, veille LONG, avant-veille SHORT.
    r_conf = sa.build_decision_log_records(
        [a], _NOW, veille_conclusions={"or": {"24h": "LONG"}},
        avant_veille_conclusions={"or": {"24h": "SHORT"}},
    )
    rec = _rec_24h(r_conf, "or")
    assert rec["shadow_flip_j0"] is False and rec["shadow_flip_conf"] is True


def test_invariance_conclusion_et_selection_inchangees():
    """Les sondes n'altèrent NI la conclusion NI la sélection : on fait varier
    veille/avant-veille (seuls inputs des sondes) et on vérifie que conclusion_pm1
    et selection_du_jour sont IDENTIQUES ; seul shadow_flip_conf diffère."""
    a = _actif("Or", "or", [_crit("3j", "momentum_prix_3j_or", +0.5, valeur_norm=0.5)],
               direction="LONG")
    base = sa.build_decision_log_records(
        [a], _NOW, veille_conclusions={"or": {"24h": "LONG"}},
        avant_veille_conclusions={"or": {"24h": "LONG"}},   # pas de confirmation
    )
    variante = sa.build_decision_log_records(
        [a], _NOW, veille_conclusions={"or": {"24h": "LONG"}},
        avant_veille_conclusions={"or": {"24h": "SHORT"}},  # confirmation
    )
    rb, rv = _rec_24h(base, "or"), _rec_24h(variante, "or")
    assert rb["conclusion_pm1"] == rv["conclusion_pm1"] == "LONG"
    assert rb["conclusion_pond"] == rv["conclusion_pond"]
    assert rb["selection_du_jour"] == rv["selection_du_jour"]
    assert rb["is_flip"] == rv["is_flip"]  # is_flip vivant intact
    # Seule la sonde bouge : confirmation détectée dans la variante uniquement.
    assert rb["shadow_flip_conf"] is False and rv["shadow_flip_conf"] is True


# ---------------------------------------------------------------------------
# [Fix 14/07] Le badge de flip ⇌ (span trend-flip, rendu S9) préfixait la
# conclusion dans la Synthèse → VEILLE_LINE_RE ratait toute ligne d'actif ayant
# flippé la veille (prouvé en prod : 6/15 actifs parsés sur le bulletin du
# 13/07, sonde « confirmation post-flip » jamais vraie, is_flip aveugle le
# lendemain d'un flip). Test-verrou sur le cas réel Argent 14/07.
# ---------------------------------------------------------------------------

def test_veille_parse_ligne_avec_badge_flip(tmp_path):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    bulls = tmp_path / "bulls"
    bulls.mkdir()
    ligne_flippee = (
        '| Argent | <span class="trend-flip" title="Tendance inversée vs la '
        'veille">⇌</span> SHORT (-0.87) ⚑<br><span class="cell-reason">· taux '
        "réels US élevés : l'or coûte à porter</span> | SHORT (-1.30) ⚑ | "
        'SHORT (-2.10) |'
    )
    (bulls / "bulletin-2026-07-13-07h.md").write_text(
        "## Synthèse des décisions\n\n| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
        + ligne_flippee + "\n", encoding="utf-8")
    now = datetime(2026, 7, 14, 7, 23, tzinfo=ZoneInfo("Europe/Paris"))
    _, veille = sa.load_veille(bulls, now)
    assert veille.get("argent") == {"24h": "SHORT", "7j": "SHORT", "1m": "SHORT"}


def test_flip_confirme_traverse_badge_flip():
    # Argent : LONG vendredi -> SHORT lundi (badge ⇌ au bulletin de lundi) ->
    # SHORT mardi = flip CONFIRMÉ, même si la ligne de la veille porte le badge.
    j0, conf = sa.compute_shadow_flip_fields("SHORT", "SHORT", "LONG")
    assert (j0, conf) == (False, True)
