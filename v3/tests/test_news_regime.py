"""Tests du RÉGIME NEWS (ticket D) — actifs structurellement news-driven.

Contexte : certaines matières premières (cuivre, cacao, café) sont pilotées EN
PERMANENCE par les news et n'ont quasi jamais assez de critères quant → elles
tombent perpétuellement en 🚫 INSUFFISANT, alors que leur signal LÉGITIME vient
des news. Quand la couverture quant est insuffisante (et que le carry ne peut
pas maintenir) MAIS que le biais news est NET & DÉCISIF, on affiche le biais
news (📰, confidence "faible") AU LIEU de 🚫 → la cellule porte une vraie
direction, mesurée comme prédiction.

Ordre de priorité du gate (vérifié ici) :
  1. coverage ≥ 0.40                     → direction quant (inchangé)
  2. FLOOR ≤ cov < 0.40 + carry possible → ⏸ carry (test (d))
  3. actif news-driven + biais news net  → 📰 régime news (test (a))
  4. sinon                               → 🚫 INSUFFISANT (tests (b), (c))

Couvre : (a) régime news nominal, (b) biais news neutre/faible → 🚫,
(c) actif NON news-driven → 🚫 (l'allowlist filtre), (d) carry > news (priorité),
(e) parité du helper compute_news_bias factorisé vs calcul inline historique.
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


NOW = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cuivre():
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    return fiches["cuivre"]


@pytest.fixture
def petrole():
    fiches = sa.load_fiches(ROOT / "config" / "fiches")
    return fiches["petrole"]


def _write_snapshot(log_dir: Path, ts: datetime, records):
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


def _news_triplet(valeur: float):
    """Critère news triplet avec source_track='ia*' → compté comme news.

    valeur ∈ {-1, 0, +1} (triplet) → valeur_norm. source_track 'ia_synthese'
    fait basculer le critère côté news dans compute_news_bias.
    """
    return {"valeur": valeur, "source_track": "ia_synthese"}


# ---------------------------------------------------------------------------
# (a) Régime news nominal — actif news-driven + cov<FLOOR + biais news net
# ---------------------------------------------------------------------------

def test_regime_news_nominal_long(cuivre, tmp_path):
    """(a) cuivre + couverture quant insuffisante + biais news NET → 📰 régime news.

    On ne couvre QUE les 2 critères news (mining_strikes poids 5 +
    news_construction poids 4 = 9/48 ≈ 0.19 < FLOOR 0.25). Les deux à +1 (signe 1)
    → news_total > 0, quant_total = 0 → ratio_news ≫ 0.5 → biais LONG décisif.
    Aucune direction antérieure (carry impossible) → régime news.
    """
    valeurs = {
        "mining_strikes_chili_perou": _news_triplet(1),
        "news_construction_infra": _news_triplet(1),
    }
    r = sa.score_actif(
        "cuivre", cuivre, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage < sa.COVERAGE_FLOOR
    for h in sa.HORIZONS:
        assert r.is_news_regime[h] is True
        assert r.is_carry[h] is False
        assert r.conclusions[h] == "LONG"
        assert r.conclusions_pond[h] == "LONG"
        assert r.confidence[h] == "faible"
        assert r.conclusions[h] != sa.CONCLUSION_INSUFFISANT
    # Le drapeau 📰 est posé sur les cellules de risque.
    for h in sa.HORIZONS:
        flags = sa._compute_cell_risk_flags(r, h, NOW)
        assert sa.SURVEILLANCE_FLAGS["news_regime"] in flags


def test_regime_news_nominal_short(cuivre, tmp_path):
    """(a-bis) Même setup mais news négatif (-1) → biais SHORT décisif → 📰 SHORT."""
    valeurs = {
        "mining_strikes_chili_perou": _news_triplet(-1),
        "news_construction_infra": _news_triplet(-1),
    }
    r = sa.score_actif(
        "cuivre", cuivre, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage < sa.COVERAGE_FLOOR
    for h in sa.HORIZONS:
        assert r.is_news_regime[h] is True
        assert r.conclusions[h] == "SHORT"


# ---------------------------------------------------------------------------
# (b) Biais news neutre / non-décisif → 🚫 (pas de régime news)
# ---------------------------------------------------------------------------

def test_news_neutre_reste_insuffisant(cuivre, tmp_path):
    """(b) cuivre news-driven mais biais news NEUTRE (valeur 0) → 🚫.

    news_total = 0 → |news_total| < EPSILON_CARRY → bias None → pas décisif.
    """
    valeurs = {
        "mining_strikes_chili_perou": _news_triplet(0),
        "news_construction_infra": _news_triplet(0),
    }
    r = sa.score_actif(
        "cuivre", cuivre, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage < sa.COVERAGE_FLOOR
    for h in sa.HORIZONS:
        assert r.is_news_regime[h] is False
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT


def test_news_non_dominant_reste_insuffisant(cuivre, tmp_path):
    """(b-bis) ratio_news ≤ 0.5 (quant domine la news) → pas décisif → 🚫.

    On couvre 1 critère news faible (news_construction poids 4, valeur +1) et
    un critère QUANT fort (inventaires zscore poids 8, valeur_normalisee très
    négative) avec une magnitude quant ≫ news sur tous les horizons → ratio_news
    < 0.5. Couverture = (4+8)/48 = 0.25 (= FLOOR) : le carry échoue (pas de
    direction antérieure), et la news n'est pas dominante → 🚫.
    """
    valeurs = {
        "news_construction_infra": _news_triplet(1),
        # quant zscore, gros poids, magnitude forte sur tous les horizons.
        "inventaires_lme_shfe_5j": {"valeur_normalisee": -3.0},
    }
    r = sa.score_actif(
        "cuivre", cuivre, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    for h in sa.HORIZONS:
        _bias, ratio, _, _ = sa.compute_news_bias(r.criteres, h)
        assert ratio <= sa.NEWS_DOMINANT_RATIO
        assert r.is_news_regime[h] is False
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT


# ---------------------------------------------------------------------------
# (c) Actif NON news-driven → l'allowlist filtre → 🚫
# ---------------------------------------------------------------------------

def test_actif_non_news_driven_reste_insuffisant(petrole, tmp_path):
    """(c) petrole (hors allowlist) + cov<FLOOR + news net → 🚫 (l'allowlist filtre).

    Même biais news net qu'en (a) mais sur un actif non listé dans
    NEWS_DRIVEN_ASSETS → le régime news ne s'active pas → 🚫.
    """
    assert "petrole" not in sa.NEWS_DRIVEN_ASSETS
    # Critère news de petrole : on cible un critère présent avec source_track ia.
    # tension_geopol_moyen_orient (triplet events-log, poids 7) → news net.
    valeurs = {
        "tension_geopol_moyen_orient": _news_triplet(1),
    }
    r = sa.score_actif(
        "petrole", petrole, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert r.coverage < sa.COVERAGE_FLOOR
    for h in sa.HORIZONS:
        assert r.is_news_regime[h] is False
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT


# ---------------------------------------------------------------------------
# (d) Priorité : carry (priorité 2) l'emporte sur régime news (priorité 3)
# ---------------------------------------------------------------------------

def test_carry_prime_sur_regime_news(cuivre, tmp_path):
    """(d) cuivre avec direction antérieure valide + cov dans la fenêtre carry
    + news net → ⏸ carry l'emporte sur 📰 (priorité 2 > 3).

    Couverture FLOOR ≤ cov < 0.40 : on couvre mining_strikes(5)+inventaires(8) =
    13/48 ≈ 0.27 (≥ FLOOR). mining_strikes est news (+1), inventaires est quant.
    Direction antérieure LONG récente cohérente → carry LONG, is_carry True,
    is_news_regime reste False (le carry a court-circuité le bloc news).
    """
    ts = NOW - timedelta(hours=2)
    _write_snapshot(tmp_path, ts, [
        _rec("cuivre", "24h", "LONG", ts),
        _rec("cuivre", "7j", "LONG", ts),
        _rec("cuivre", "1m", "LONG", ts),
    ])
    valeurs = {
        "mining_strikes_chili_perou": _news_triplet(1),       # news +1
        "inventaires_lme_shfe_5j": {"valeur_normalisee": 0.0},  # quant neutre
    }
    r = sa.score_actif(
        "cuivre", cuivre, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    assert sa.COVERAGE_FLOOR <= r.coverage < sa.COVERAGE_MIN
    for h in sa.HORIZONS:
        assert r.is_carry[h] is True
        assert r.is_news_regime[h] is False
        assert r.conclusions[h] == "LONG"
    # Le drapeau prioritaire est ⏸ (carry), pas 📰.
    for h in sa.HORIZONS:
        flags = sa._compute_cell_risk_flags(r, h, NOW)
        assert sa.SURVEILLANCE_FLAGS["carry"] in flags
        assert sa.SURVEILLANCE_FLAGS["news_regime"] not in flags


# ---------------------------------------------------------------------------
# (e) Parité du helper factorisé compute_news_bias vs calcul inline historique
# ---------------------------------------------------------------------------

def test_helper_parite_calcul_inline(cuivre, tmp_path):
    """(e) compute_news_bias reproduit EXACTEMENT le calcul news_total/quant_total/
    ratio_news historiquement inline (sommes des contributions non-na/non-gate),
    et les valeurs *_pm1 de news_cap_info concordent → zéro divergence.
    """
    valeurs = {
        "mining_strikes_chili_perou": _news_triplet(1),
        "news_construction_infra": _news_triplet(-1),
        "caixin_pmi_manuf": {"valeur": 1},
    }
    r = sa.score_actif(
        "cuivre", cuivre, valeurs, now=NOW, log_dir=tmp_path,
        current_generated_at=NOW.isoformat(),
    )
    for h in sa.HORIZONS:
        bias, ratio, news_total, quant_total = sa.compute_news_bias(r.criteres, h)
        # Recalcul inline indépendant (la formule historique).
        nt = sum(
            c.contributions[h] for c in r.criteres
            if c.source_track.startswith("ia") and not c.is_na and not c.is_gate
        )
        qt = sum(
            c.contributions[h] for c in r.criteres
            if not c.source_track.startswith("ia") and not c.is_na and not c.is_gate
        )
        assert news_total == pytest.approx(nt)
        assert quant_total == pytest.approx(qt)
        assert ratio == pytest.approx(abs(nt) / (abs(qt) + 1e-9))
        # Concordance avec les *_pm1 stockés dans news_cap_info.
        cap = r.news_cap_info[h]
        assert news_total == pytest.approx(cap["news_total_pm1"])
        assert quant_total == pytest.approx(cap["quant_total_pm1"])
        # Sémantique du biais.
        if abs(nt) < sa.EPSILON_CARRY:
            assert bias is None
        else:
            assert bias == ("LONG" if nt > 0 else "SHORT")
