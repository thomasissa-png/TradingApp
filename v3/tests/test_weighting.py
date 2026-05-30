"""Tests v3.1 — pondération (weighting + double score + decision-log + A/B).

Couvre :
- Loader weighting.yml (présent, absent, corrompu, défauts)
- weight_direction : news triplet → ±[0, cap] selon matérialité × fiabilité
- valeur_ponderee : identité pour numérique (= valeur_normalisee), cap
- score_actif : double score + double conclusion
- Détection de divergence
- build_decision_log_records / write_decision_log (champs présents)
- Journaliste A/B : measure_cell calcule outcome_pond ; compute_kpi_ab côte à côte
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import weighting as wg  # noqa: E402
import scoring_analyste as sa  # noqa: E402
import journaliste as jn  # noqa: E402


# ---------------------------------------------------------------------------
# 1) Loader weighting
# ---------------------------------------------------------------------------

def test_weighting_load_yml_existant(tmp_path):
    p = tmp_path / "weighting.yml"
    p.write_text(yaml.safe_dump({
        "version": 7,
        "materiality_factor": {"high": 0.9, "medium": 0.5, "low": 0.2},
        "reliability_factor": {"confirmed": 1.0, "reported": 0.6, "rumor": 0.3},
        "cap": 1.0,
    }), encoding="utf-8")
    wg.reset_cache()
    cfg = wg.load_weighting(p, force=True)
    assert cfg.version == 7
    assert cfg.materiality("high") == 0.9
    assert cfg.reliability("rumor") == 0.3
    assert cfg.cap == 1.0


def test_weighting_defauts_si_absent(tmp_path):
    wg.reset_cache()
    cfg = wg.load_weighting(tmp_path / "ne_existe_pas.yml", force=True)
    # Défauts documentés
    assert cfg.materiality("high") == 1.0
    assert cfg.materiality("medium") == 0.6
    assert cfg.reliability("confirmed") == 1.0
    assert cfg.reliability("rumor") == 0.4
    # Clé inconnue → fallback médian
    assert cfg.materiality("unknown") == 0.6
    assert cfg.reliability("unknown") == 0.7


def test_weighting_defauts_si_corrompu(tmp_path):
    p = tmp_path / "broken.yml"
    p.write_text(":::not yaml:::\n", encoding="utf-8")
    wg.reset_cache()
    cfg = wg.load_weighting(p, force=True)
    assert cfg.materiality("high") == 1.0


def test_weighting_weight_direction_capee():
    cfg = wg.WeightingConfig(
        materiality={"high": 2.0},   # delibérément > cap pour tester clipping
        reliability={"confirmed": 2.0},
        cap=1.0,
    )
    # 1 × 2 × 2 = 4 → capé à 1.0
    assert cfg.weight_direction(1, "high", "confirmed") == 1.0
    # -1 × 2 × 2 = -4 → capé à -1.0
    assert cfg.weight_direction(-1, "high", "confirmed") == -1.0


def test_weighting_news_vs_zero():
    cfg = wg.WeightingConfig()
    # direction 0 → 0
    assert cfg.weight_direction(0, "high", "confirmed") == 0.0


# ---------------------------------------------------------------------------
# 2) valeur_ponderee : extraction depuis raw
# ---------------------------------------------------------------------------

def test_extract_valeur_ponderee_numerique_identite():
    """Critère z-score : valeur_ponderee = valeur_normalisee (identité)."""
    crit = {"normalisation": "zscore", "cap": 1.0}
    raw = {"valeur": 100.0, "valeur_normalisee": 0.42, "valeur_ponderee": 0.42}
    vp = sa.extract_valeur_ponderee(crit, raw, 0.42)
    assert vp == pytest.approx(0.42)


def test_extract_valeur_ponderee_triplet_news():
    """Triplet news +1 × high × confirmed = 1.0 (capé)."""
    crit = {"normalisation": "triplet", "cap": 1.0}
    raw = {
        "valeur": 1,
        "valeur_normalisee": 1.0,
        "valeur_ponderee": 0.6 * 0.7,  # medium × reported = 0.42
        "materiality": "medium",
        "reliability": "reported",
    }
    vp = sa.extract_valeur_ponderee(crit, raw, 1.0)
    assert vp == pytest.approx(0.42)


def test_extract_valeur_ponderee_fallback_si_absent():
    """raw sans valeur_ponderee → fallback = valeur_norm."""
    crit = {"normalisation": "triplet", "cap": 1.0}
    raw = {"valeur": 1, "valeur_normalisee": 1.0}  # pas de valeur_ponderee
    vp = sa.extract_valeur_ponderee(crit, raw, 1.0)
    assert vp == 1.0


def test_extract_valeur_ponderee_cap():
    crit = {"normalisation": "triplet", "cap": 0.5}
    raw = {"valeur": 1, "valeur_ponderee": 0.9}  # > cap 0.5
    vp = sa.extract_valeur_ponderee(crit, raw, 1.0)
    assert vp == 0.5


# ---------------------------------------------------------------------------
# 3) score_actif : double score + double conclusion + divergence
# ---------------------------------------------------------------------------

FICHE_MINI = {
    "actif": "TestActif",
    "criteres": [
        {
            "id": 1, "nom": "news A", "cle_courante": "news_a",
            "normalisation": "triplet", "poids": 1.0, "signe": 1, "cap": 1.0,
            "pertinence": {"24h": 1.0, "7j": 0.5, "1m": 0.2},
        },
        {
            "id": 2, "nom": "news B", "cle_courante": "news_b",
            "normalisation": "triplet", "poids": 1.0, "signe": 1, "cap": 1.0,
            "pertinence": {"24h": 1.0, "7j": 0.5, "1m": 0.2},
        },
        {
            "id": 3, "nom": "z C", "cle_courante": "z_c",
            "normalisation": "zscore", "poids": 1.0, "signe": 1, "cap": 1.0,
            "pertinence": {"24h": 1.0, "7j": 0.5, "1m": 0.2},
        },
    ],
}


def test_score_actif_double_calcul_et_divergence():
    """Cas conçu pour faire diverger ±1 vs pondéré.

    - news A : +1, mais low/rumor (facteur ≈ 0.3 × 0.4 = 0.12 → quasi-nul)
    - news B : -1, high/confirmed (facteur 1.0 → -1.0 pondéré)
    - z C  : +0.05 (faible)

    ±1 baseline : +1 + (-1) + 0.05 = +0.05 → LONG
    Pondéré :   0.12 + (-1.0) + 0.05 = -0.83 → SHORT
    """
    valeurs = {
        "news_a": {
            "valeur": 1, "valeur_normalisee": 1.0, "valeur_ponderee": 0.12,
            "materiality": "low", "reliability": "rumor",
        },
        "news_b": {
            "valeur": -1, "valeur_normalisee": -1.0, "valeur_ponderee": -1.0,
            "materiality": "high", "reliability": "confirmed",
        },
        "z_c": {"valeur": 0.05, "valeur_normalisee": 0.05, "valeur_ponderee": 0.05},
    }
    res = sa.score_actif("test", FICHE_MINI, valeurs)
    # Sanity baseline
    assert res.scores["24h"] == pytest.approx(0.05, abs=1e-6)
    assert res.conclusions["24h"] == "LONG"
    # Pondéré
    assert res.scores_pond["24h"] == pytest.approx(-0.83, abs=1e-6)
    assert res.conclusions_pond["24h"] == "SHORT"
    # Divergence détectée
    assert res.diverge["24h"] is True
    # Hors 24h, mêmes signes (les contributions sont pondérées par pertinence
    # mais conservent leur signe global → on attend toujours divergence)
    for h in ("7j", "1m"):
        assert res.diverge[h] is True


def test_score_actif_pas_de_divergence_quand_meme_signe():
    """Critères tous cohérents → conclusions identiques → diverge=False."""
    valeurs = {
        "news_a": {"valeur": 1, "valeur_normalisee": 1.0, "valeur_ponderee": 1.0,
                   "materiality": "high", "reliability": "confirmed"},
        "news_b": {"valeur": 1, "valeur_normalisee": 1.0, "valeur_ponderee": 0.6,
                   "materiality": "medium", "reliability": "reported"},
        "z_c": {"valeur": 0.5, "valeur_normalisee": 0.5, "valeur_ponderee": 0.5},
    }
    res = sa.score_actif("test", FICHE_MINI, valeurs)
    for h in ("24h", "7j", "1m"):
        assert res.conclusions[h] == "LONG"
        assert res.conclusions_pond[h] == "LONG"
        assert res.diverge[h] is False


# ---------------------------------------------------------------------------
# 4) Decision log : structure complète, append-only
# ---------------------------------------------------------------------------

def test_decision_log_contient_tous_les_champs(tmp_path):
    valeurs = {
        "news_a": {"valeur": 1, "valeur_normalisee": 1.0, "valeur_ponderee": 0.6,
                   "materiality": "medium", "reliability": "reported",
                   "source_track": "ia"},
        "news_b": {"valeur": -1, "valeur_normalisee": -1.0, "valeur_ponderee": -0.3,
                   "materiality": "low", "reliability": "reported",
                   "source_track": "keyword"},
        "z_c": {"valeur": 0.5, "valeur_normalisee": 0.5, "valeur_ponderee": 0.5},
    }
    res = sa.score_actif("test", FICHE_MINI, valeurs)
    now = datetime(2026, 5, 30, 14, 30, tzinfo=timezone.utc)
    records = sa.build_decision_log_records([res], now)
    # 1 res × 3 horizons = 3 records
    assert len(records) == 3
    for rec in records:
        # Champs top-level
        for key in ("bulletin_date", "generated_at", "fiche_key", "actif",
                    "horizon", "score_pm1", "score_pond", "conclusion_pm1",
                    "conclusion_pond", "diverge", "criteres"):
            assert key in rec, f"clé manquante : {key}"
        assert rec["bulletin_date"] == "2026-05-30"
        assert isinstance(rec["criteres"], list)
        assert len(rec["criteres"]) == 3
        for c in rec["criteres"]:
            for ck in ("cle", "valeur", "valeur_normalisee", "valeur_ponderee",
                       "poids", "pertinence", "materiality", "reliability",
                       "facteur", "contrib_pm1", "contrib_pond", "source_track"):
                assert ck in c, f"critère sans clé : {ck} ({c})"
        # On vérifie l'ordre triplet en premier
        cles = [c["cle"] for c in rec["criteres"]]
        assert "news_a" in cles and "news_b" in cles and "z_c" in cles

    # Écriture JSONL
    path = sa.write_decision_log(records, now, base_dir=tmp_path)
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    # Chaque ligne est du JSON valide
    parsed = [json.loads(l) for l in lines]
    assert all(p["actif"] == "TestActif" for p in parsed)


# ---------------------------------------------------------------------------
# 5) Journaliste A/B : measure_cell calcule outcome_pond + KPI
# ---------------------------------------------------------------------------

FICHE_TEST_JN = {
    "actif": "Or",
    "ticker_principal": "XAU/USD",
    "seuils_reussite_pct": {"24h": 0.5, "7j": 1.0, "1m": 2.0},
}


def test_measure_cell_outcome_pond_diverge():
    """Conclusion pm1=LONG, conclusion pond=SHORT, prix monte > seuil :
    pm1 → VRAI ; pond → FAUSSE.
    """
    cell = jn.BulletinCell(
        bulletin_date=date(2026, 5, 29),
        actif_name="Or",
        horizon="24h",
        conclusion="LONG",
        score=0.3,
        conclusion_pond="SHORT",
        score_pond=-0.6,
    )
    m = jn.measure_cell(
        cell, fiche_key="or", fiche=FICHE_TEST_JN,
        prix_emission=2000.0, prix_courant=2030.0,  # +1.5% > 0.5%
    )
    assert m.outcome == jn.OUTCOME_VRAI    # LONG + montée > seuil
    assert m.outcome_pond == jn.OUTCOME_FAUSSE  # SHORT + montée > seuil


def test_measure_cell_outcome_pond_none_si_pas_annotation():
    """Bulletin antérieur sans annotation pondérée → outcome_pond = None."""
    cell = jn.BulletinCell(
        bulletin_date=date(2026, 5, 29), actif_name="Or", horizon="24h",
        conclusion="LONG", score=0.3,
        # pas de conclusion_pond / score_pond
    )
    m = jn.measure_cell(cell, "or", FICHE_TEST_JN, 2000.0, 2030.0)
    assert m.outcome == jn.OUTCOME_VRAI
    assert m.outcome_pond is None


def test_compute_kpi_ab_skip_propre():
    """Mesures pondérées partielles → n_pond < n_pm1, calculs propres."""
    base_cell = lambda i, conc_p: jn.BulletinCell(
        bulletin_date=date(2026, 5, 1),
        actif_name="Or", horizon="24h",
        conclusion="LONG", score=0.4,
        conclusion_pond=conc_p,
        score_pond=0.5 if conc_p == "LONG" else (-0.5 if conc_p == "SHORT" else None),
    )
    # 4 mesures pm1, dont 2 avec annotation pond
    measures = [
        jn.Measure(
            cell=base_cell(i, ("LONG" if i < 2 else None)),
            fiche_key="or", ticker="XAU/USD", horizon="24h",
            echeance=date(2026, 5, 2 + i),
            prix_emission=2000.0, prix_courant=2020.0,
            seuil_pct=0.5, delta_pct=1.0,
            outcome=jn.OUTCOME_VRAI,
            outcome_pond=(jn.OUTCOME_VRAI if i < 2 else None),
        )
        for i in range(4)
    ]
    kpi = jn.compute_kpi_ab(measures)
    assert kpi.n_pm1 == 4
    assert kpi.n_vrai_pm1 == 4
    assert kpi.taux_pm1 == 100.0
    assert kpi.n_pond == 2  # skip propre des mesures sans annotation pond
    assert kpi.n_vrai_pond == 2
    assert kpi.taux_pond == 100.0


# ---------------------------------------------------------------------------
# 6) Parsing bulletin : annotation pondérée détectée
# ---------------------------------------------------------------------------

def test_parse_bulletin_avec_annotation_pondree(tmp_path):
    bulletin = """# Bulletin Analyste — 2026-05-30

## Matrice (12 actifs × 3 horizons)

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| Or | LONG (+0.42) [pond:SHORT -0.60] ⚠ | LONG (+0.20) [pond:LONG +0.15] | SHORT (-0.10) [pond:SHORT -0.05] |
"""
    p = tmp_path / "bulletin-2026-05-30.md"
    p.write_text(bulletin, encoding="utf-8")
    cells = jn.parse_bulletin(p)
    assert len(cells) == 3
    c24 = next(c for c in cells if c.horizon == "24h")
    assert c24.conclusion == "LONG"
    assert c24.conclusion_pond == "SHORT"
    assert c24.score_pond == pytest.approx(-0.60)
    c7 = next(c for c in cells if c.horizon == "7j")
    assert c7.conclusion_pond == "LONG"
    c1 = next(c for c in cells if c.horizon == "1m")
    assert c1.conclusion_pond == "SHORT"


def test_parse_bulletin_sans_annotation_retrocompat(tmp_path):
    """Ancien format sans [pond:...] → conclusion_pond=None (skip propre)."""
    bulletin = """| Or | LONG (+0.42) | LONG (+0.20) | SHORT (-0.10) |\n"""
    p = tmp_path / "bulletin-2026-05-29.md"
    p.write_text(bulletin, encoding="utf-8")
    cells = jn.parse_bulletin(p)
    assert len(cells) == 3
    for c in cells:
        assert c.conclusion_pond is None
        assert c.score_pond is None
