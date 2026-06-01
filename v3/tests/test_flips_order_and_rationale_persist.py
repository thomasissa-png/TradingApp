"""Tests des deux changements demandés par Thomas (2026-06-01) :

Change 1 — Bulletin : "## Flips vs veille" affiché AVANT "## Matrice".
           Section toujours présente (placeholder si aucun flip) pour ne
           pas casser la sous-nav HTML.

Change 2 — Decision-log JSONL : pour chaque critère news (source_track="ia_*")
           qui a un synthese_rationale, persiste `synthese_rationale` et
           `conviction` (=materiality bucket high/medium/low). Critères
           non-news → champs absents (zéro invention).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers (alignés sur test_fix_news_flag_and_coinflip.py)
# ---------------------------------------------------------------------------

def _fiche(quant_poids: int = 10, news_poids: int = 10) -> dict:
    return {
        "actif": "TestActif",
        "criteres": [
            {
                "id": 1, "nom": "Quant",
                "cle_courante": "quant", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 1.0,
                "signe": 1, "poids": quant_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
            {
                "id": 2, "nom": "News",
                "cle_courante": "news", "normalisation": "triplet",
                "cap": 1.0, "signe": 1, "poids": news_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _vals_with_rationale(rationale: str, conviction: str = "high") -> dict:
    return {
        "quant": {"valeur": 1.0, "source_track": "twelvedata"},
        "news": {
            "valeur": 1.0,
            "source_track": "ia_synthese",
            "materiality": conviction,
            "reliability": "confirmed",
            "synthese_rationale": rationale,
        },
    }


# ---------------------------------------------------------------------------
# Change 1 — ordre des sections du bulletin
# ---------------------------------------------------------------------------

def test_flips_section_appears_before_matrice():
    """## Flips vs veille DOIT précéder ## Matrice dans le bulletin."""
    res = sa.score_actif("test", _fiche(), _vals_with_rationale("x"))
    bulletin = sa.render_bulletin(
        [res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok",
    )
    idx_flips = bulletin.find("## Flips vs veille")
    idx_matrice = bulletin.find("## Matrice")
    assert idx_flips != -1, "Section '## Flips vs veille' absente du bulletin"
    assert idx_matrice != -1, "Section '## Matrice' absente du bulletin"
    assert idx_flips < idx_matrice, (
        f"Flips ({idx_flips}) doit précéder Matrice ({idx_matrice})"
    )


def test_flips_section_placeholder_when_empty():
    """Si aucun flip → placeholder court (la section h2 doit exister pour la sous-nav)."""
    res = sa.score_actif("test", _fiche(), _vals_with_rationale("x"))
    bulletin = sa.render_bulletin(
        [res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok",
    )
    assert "## Flips vs veille" in bulletin
    # Le placeholder court (en italique markdown) doit apparaître si pas de flips
    assert "Aucun changement de position vs veille" in bulletin


def test_flips_section_lists_flips_when_present():
    """Si la veille divergeait → ligne de flip listée."""
    res = sa.score_actif("test", _fiche(), _vals_with_rationale("x"))
    # Veille : "test" était SHORT sur 24h, le run actuel est LONG → flip attendu.
    veille = {"testactif": {"24h": "SHORT", "7j": "LONG", "1m": "LONG"}}
    bulletin = sa.render_bulletin(
        [res], veille, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok",
    )
    assert "## Flips vs veille" in bulletin
    # Le flip doit apparaître
    assert "[24h]" in bulletin
    assert "SHORT → LONG" in bulletin
    # La section flips reste avant matrice
    assert bulletin.find("## Flips vs veille") < bulletin.find("## Matrice")


def test_matrice_table_intact_after_reorder():
    """Régression : la matrice (table + légende) doit rester fonctionnelle."""
    res = sa.score_actif("test", _fiche(), _vals_with_rationale("x"))
    bulletin = sa.render_bulletin(
        [res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok",
    )
    assert "| Actif | 24h | 7j | 1m |" in bulletin
    assert "**Légende**" in bulletin
    matrice_line = next(l for l in bulletin.splitlines() if l.startswith("| TestActif"))
    assert "LONG" in matrice_line or "SHORT" in matrice_line


# ---------------------------------------------------------------------------
# Change 2 — persistance synthese_rationale + conviction dans le decision-log
# ---------------------------------------------------------------------------

def test_decision_log_persists_synthese_rationale_for_news():
    """Pour un critère news (source_track='ia_synthese') avec rationale →
    le decision-log JSONL contient synthese_rationale + conviction."""
    rationale = "OPEC cut + Ormuz tension → bullish pétrole"
    res = sa.score_actif(
        "test", _fiche(),
        _vals_with_rationale(rationale, conviction="high"),
    )
    records = sa.build_decision_log_records(
        [res], datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    news_crit = next(c for c in rec_24h["criteres"] if c["cle"] == "news")
    assert news_crit.get("synthese_rationale") == rationale
    assert news_crit.get("conviction") == "high"


def test_decision_log_omits_rationale_for_non_news_criteres():
    """Critère quant (source_track='twelvedata') → PAS de synthese_rationale
    ni de conviction (zéro invention)."""
    res = sa.score_actif(
        "test", _fiche(),
        _vals_with_rationale("rationale ici", conviction="medium"),
    )
    records = sa.build_decision_log_records(
        [res], datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    quant_crit = next(c for c in rec_24h["criteres"] if c["cle"] == "quant")
    assert "synthese_rationale" not in quant_crit
    assert "conviction" not in quant_crit


def test_decision_log_omits_rationale_when_meta_absent():
    """Critère news mais SANS synthese_rationale dans le meta (ex chemin
    legacy keyword-only) → champs absents, pas vides à zéro invention."""
    vals = {
        "quant": {"valeur": 1.0, "source_track": "twelvedata"},
        "news": {
            "valeur": 1.0,
            "source_track": "ia",  # chemin IA-first keyword, pas synthese
            "materiality": "high",
            "reliability": "confirmed",
            # PAS de synthese_rationale
        },
    }
    res = sa.score_actif("test", _fiche(), vals)
    records = sa.build_decision_log_records(
        [res], datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    news_crit = next(c for c in rec_24h["criteres"] if c["cle"] == "news")
    assert "synthese_rationale" not in news_crit
    assert "conviction" not in news_crit


def test_decision_log_conviction_propagates_all_buckets():
    """high / medium / low (et faible synthese) doivent tous être persistés tels quels."""
    for conv in ("high", "medium", "low"):
        res = sa.score_actif(
            "test", _fiche(),
            _vals_with_rationale(f"r-{conv}", conviction=conv),
        )
        records = sa.build_decision_log_records(
            [res], datetime(2026, 6, 1, tzinfo=timezone.utc),
        )
        rec_24h = next(r for r in records if r["horizon"] == "24h")
        news_crit = next(c for c in rec_24h["criteres"] if c["cle"] == "news")
        assert news_crit.get("conviction") == conv
        assert news_crit.get("synthese_rationale") == f"r-{conv}"
