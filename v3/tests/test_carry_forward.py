"""Tests de l'HYSTÉRÉSIS DE MAINTIEN (carry-forward) — horizon-aware.

Sécurité demandée par Thomas : un simple TROU de data (coverage qui tombe sous
COVERAGE_MIN le temps d'un cycle, ex. panne FRED 429) ne doit PAS effacer une
direction LONG/SHORT valide la veille (cas réel : Cuivre LONG confirmé hier →
🚫 aujourd'hui à 35% de couverture). On MAINTIENT la dernière direction valide
tant que :
  - COVERAGE_FLOOR (0.25) ≤ coverage < COVERAGE_MIN (0.40)
  - il existe une dernière direction valide récente (decision-log)
  - les critères présents ne CONTREDISENT pas (signe opposé + |score| ≥ EPSILON_CARRY)
  - le maintien n'est pas PÉRIMÉ (âge < CARRY_MAX_AGE_H[horizon])

Couvre : (a) maintien nominal + is_carry, (b) 🚫 si cov<FLOOR, (c) 🚫 si
contradiction, (d) 🚫 si périmé, (e) 🚫 si aucune direction antérieure,
(f) horizon-aware (même cov, périmé en 1m mais OK en 7j), + robustesse
derniere_direction_valide (fichier manquant/vide/mal formé → None).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

NOW = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def petrole():
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    return fiches["petrole"]


def _write_snapshot(log_dir: Path, ts: datetime, records):
    """Écrit un snapshot decision-log jouet (1 ligne JSON par record)."""
    fname = f"{ts.astimezone(timezone.utc):%Y-%m-%d}-{ts.astimezone(timezone.utc):%H%M}.jsonl"
    path = log_dir / fname
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


def _rec(fiche_key, horizon, conclusion_pond, generated_at: datetime):
    return {
        "fiche_key": fiche_key,
        "horizon": horizon,
        "conclusion_pond": conclusion_pond,
        "generated_at": generated_at.isoformat(),
    }


# Valeurs partielles contrôlées sur petrole (total poids = 60).
# On choisit quels critères ont une valeur → contrôle direct de la coverage.
def _valeurs(couverts: dict):
    """couverts : {cle: valeur_lineaire_brute}. Les critères absents → n/a.

    Pour les critères 'lineaire' (brent/spread/caixin) : centre=0 echelle=1 →
    valeur_norm = valeur (clipée au cap). Pour 'zscore' on passe
    valeur_normalisee directement. Permet de piloter signe et magnitude du score.
    """
    return {cle: ({"valeur": v} if not isinstance(v, dict) else v) for cle, v in couverts.items()}


# ---------------------------------------------------------------------------
# 1. derniere_direction_valide — robustesse & sémantique
# ---------------------------------------------------------------------------

def test_ddv_dossier_absent(tmp_path):
    assert sa.derniere_direction_valide(
        "petrole", "24h", NOW, 24, log_dir=tmp_path / "nope"
    ) is None


def test_ddv_dossier_vide(tmp_path):
    assert sa.derniere_direction_valide("petrole", "24h", NOW, 24, log_dir=tmp_path) is None


def test_ddv_json_malforme_ignore(tmp_path):
    (tmp_path / "2026-06-02-1000.jsonl").write_text(
        "{pas du json\nligne pourrie}\n", encoding="utf-8"
    )
    assert sa.derniere_direction_valide("petrole", "24h", NOW, 24, log_dir=tmp_path) is None


def test_ddv_prend_le_plus_recent(tmp_path):
    # Ancien LONG, récent SHORT → on prend SHORT (plus récent).
    _write_snapshot(tmp_path, NOW - timedelta(hours=10),
                    [_rec("petrole", "24h", "LONG", NOW - timedelta(hours=10))])
    _write_snapshot(tmp_path, NOW - timedelta(hours=2),
                    [_rec("petrole", "24h", "SHORT", NOW - timedelta(hours=2))])
    assert sa.derniere_direction_valide("petrole", "24h", NOW, 24, log_dir=tmp_path) == "SHORT"


def test_ddv_ignore_insuffisant(tmp_path):
    # Le plus récent est INSUFFISANT → on remonte au LONG valide précédent.
    _write_snapshot(tmp_path, NOW - timedelta(hours=8),
                    [_rec("petrole", "24h", "LONG", NOW - timedelta(hours=8))])
    _write_snapshot(tmp_path, NOW - timedelta(hours=1),
                    [_rec("petrole", "24h", "INSUFFISANT", NOW - timedelta(hours=1))])
    assert sa.derniere_direction_valide("petrole", "24h", NOW, 24, log_dir=tmp_path) == "LONG"


def test_ddv_exclut_run_courant(tmp_path):
    cur = NOW
    _write_snapshot(tmp_path, cur, [_rec("petrole", "24h", "LONG", cur)])
    # Le seul record porte le generated_at courant → exclu → None.
    assert sa.derniere_direction_valide(
        "petrole", "24h", NOW, 24, log_dir=tmp_path,
        exclude_generated_at=cur.isoformat(),
    ) is None


def test_ddv_perime_hors_fenetre(tmp_path):
    # LONG à 30h, fenêtre 24h → hors fenêtre → None.
    _write_snapshot(tmp_path, NOW - timedelta(hours=30),
                    [_rec("petrole", "24h", "LONG", NOW - timedelta(hours=30))])
    assert sa.derniere_direction_valide("petrole", "24h", NOW, 24, log_dir=tmp_path) is None


def test_ddv_horizon_aware(tmp_path):
    # Même snapshot à 30h : périmé pour 24h (fenêtre 24h) mais OK pour 7j (48h).
    _write_snapshot(tmp_path, NOW - timedelta(hours=30),
                    [_rec("petrole", "7j", "LONG", NOW - timedelta(hours=30))])
    assert sa.derniere_direction_valide("petrole", "7j", NOW, 24, log_dir=tmp_path) is None
    assert sa.derniere_direction_valide("petrole", "7j", NOW, 48, log_dir=tmp_path) == "LONG"


# ---------------------------------------------------------------------------
# 2. score_actif — comportement de gate avec carry-forward
# ---------------------------------------------------------------------------

def _carry_log(tmp_path, conclusion="LONG", age_h=2):
    """Snapshot decision-log avec une direction valide récente pour petrole/24h+7j+1m."""
    ts = NOW - timedelta(hours=age_h)
    _write_snapshot(tmp_path, ts, [
        _rec("petrole", "24h", conclusion, ts),
        _rec("petrole", "7j", conclusion, ts),
        _rec("petrole", "1m", conclusion, ts),
    ])
    return tmp_path


def test_maintien_nominal(petrole, tmp_path):
    """(a) 0.25 ≤ cov < 0.40 + direction antérieure cohérente récente → MAINTIEN.

    Couverture : eia(10)+api(8) = 18/60 = 0.30. Valeurs ~neutres (score proche 0)
    → pas de contradiction. Direction antérieure LONG, âge 2h → maintenu LONG.
    """
    _carry_log(tmp_path, "LONG", age_h=2)
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": 0.0},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage == pytest.approx(0.30)
    for h in sa.HORIZONS:
        assert r.is_carry[h] is True
        assert r.conclusions[h] == "LONG"
        assert r.conclusions_pond[h] == "LONG"
        assert r.confidence[h] == "faible"


def test_insuffisant_si_sous_floor(petrole, tmp_path):
    """(b) cov < COVERAGE_FLOOR (0.25) → 🚫 même avec direction antérieure.

    Couverture : brent(5)+dxy(5) = 10/60 ≈ 0.167 < 0.25.
    """
    _carry_log(tmp_path, "LONG", age_h=2)
    valeurs = _valeurs({
        "brent_term_structure_m1m2": 0.0,
        "dxy_trend_20j": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage < sa.COVERAGE_FLOOR
    for h in sa.HORIZONS:
        assert r.is_carry[h] is False
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT


def test_insuffisant_si_contradiction(petrole, tmp_path):
    """(c) Critères présents contredisent franchement la direction maintenue → 🚫.

    Direction antérieure LONG. On force un score courant nettement SHORT
    (|score| ≥ EPSILON_CARRY, signe opposé) via une valeur linéaire négative
    forte sur un critère couvert → contradiction → INSUFFISANT.
    Couverture eia(10)+brent(5) = 15/60 = 0.25 (≥ FLOOR).
    brent : signe par défaut, lineaire centre=0 echelle=1, valeur -1 → contrib < 0.
    """
    _carry_log(tmp_path, "LONG", age_h=2)
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": -0.9},
        "brent_term_structure_m1m2": -1.0,
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage == pytest.approx(0.25)
    # Score courant doit être franchement négatif (SHORT) → contredit le LONG maintenu.
    for h in sa.HORIZONS:
        assert abs(r.scores[h]) >= sa.EPSILON_CARRY
        assert r.scores[h] < 0
        assert r.is_carry[h] is False
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT


def test_maintien_si_score_neutre_meme_signe_oppose_faible(petrole, tmp_path):
    """(c-bis) Signe opposé MAIS |score| < EPSILON_CARRY (neutre) → PAS contradiction → maintien."""
    _carry_log(tmp_path, "LONG", age_h=2)
    # Couverture eia(10)+api(8) = 0.30. Petit score négatif < epsilon.
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": -0.001},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    for h in sa.HORIZONS:
        assert abs(r.scores[h]) < sa.EPSILON_CARRY
        assert r.is_carry[h] is True
        assert r.conclusions[h] == "LONG"


def test_insuffisant_si_perime(petrole, tmp_path):
    """(d) Maintien périmé (> âge max horizon) → 🚫.

    Direction LONG à 30h. Pour 24h (fenêtre 24h) et 1m (fenêtre 24h) → périmé → 🚫.
    """
    ts = NOW - timedelta(hours=30)
    _write_snapshot(tmp_path, ts, [
        _rec("petrole", "24h", "LONG", ts),
        _rec("petrole", "1m", "LONG", ts),
    ])
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": 0.0},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage == pytest.approx(0.30)
    assert r.is_carry["24h"] is False
    assert r.conclusions["24h"] == sa.CONCLUSION_INSUFFISANT
    assert r.is_carry["1m"] is False
    assert r.conclusions["1m"] == sa.CONCLUSION_INSUFFISANT


def test_insuffisant_si_aucune_direction_anterieure(petrole, tmp_path):
    """(e) Aucune direction antérieure (decision-log vide) → 🚫."""
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": 0.0},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage == pytest.approx(0.30)
    for h in sa.HORIZONS:
        assert r.is_carry[h] is False
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT


def test_horizon_aware_perime_1m_ok_7j(petrole, tmp_path):
    """(f) Même cov, même âge : périmé en 1m (24h) mais maintenu en 7j (48h).

    Direction LONG à 30h sur 7j ET 1m. Fenêtres : 7j=48h (OK), 1m=24h (périmé).
    """
    ts = NOW - timedelta(hours=30)
    _write_snapshot(tmp_path, ts, [
        _rec("petrole", "7j", "LONG", ts),
        _rec("petrole", "1m", "LONG", ts),
    ])
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": 0.0},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    # 7j : maintenu (30h < 48h).
    assert r.is_carry["7j"] is True
    assert r.conclusions["7j"] == "LONG"
    # 1m : périmé (30h > 24h) → 🚫.
    assert r.is_carry["1m"] is False
    assert r.conclusions["1m"] == sa.CONCLUSION_INSUFFISANT


def test_coverage_normale_inchangee(petrole, tmp_path):
    """Garde-fou non-régression : coverage ≥ COVERAGE_MIN → aucun carry, comportement inchangé."""
    _carry_log(tmp_path, "LONG", age_h=2)
    valeurs = _valeurs({
        "eia_crude_surprise": {"valeur_normalisee": 0.2},
        "api_weekly_surprise": {"valeur_normalisee": 0.2},
        "cftc_cot_crude_nets": {"valeur_normalisee": 0.2},
        "opec_production_policy": {"valeur": 1},
        "brent_term_structure_m1m2": 0.2,
        "dxy_trend_20j": {"valeur_normalisee": 0.0},
    })
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage >= sa.COVERAGE_MIN
    for h in sa.HORIZONS:
        assert r.is_carry[h] is False
        assert r.conclusions[h] in ("LONG", "SHORT")
