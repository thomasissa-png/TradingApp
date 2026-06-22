"""Drapeau ↯ étendu au FLUX (audit fond 22/06, News Trader).

Jusqu'ici ↯ ne voyait que la divergence quant↔news du SCORING. On le fait aussi
mordre quand une news HIGH du FLUX events-log contredit le call (ex. Cuivre SHORT
vs alliance G7 minerais critiques haussière high). FLAG-ONLY : aucun score ni
`r.divergence_quant_news` n'est modifié. Tests purs (zéro réseau) via monkeypatch
de `_fresh_high_feed_dirs`.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

_NOW = datetime(2026, 6, 22, 7, 0, tzinfo=timezone.utc)


def _actif(nom: str, conc_24h: str) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=nom.lower(),
        criteres=[],
        scores={h: (-4.5 if h == "24h" else 0.0) for h in sa.HORIZONS},
        conclusions={h: (conc_24h if h == "24h" else sa.CONCLUSION_INSUFFISANT)
                     for h in sa.HORIZONS},
        tie_break_notes={},
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
        divergence_quant_news={h: False for h in sa.HORIZONS},
    )


def test_feed_news_contredit_short_par_news_haussiere(monkeypatch):
    # Cuivre SHORT, mais une news high LONG (G7) dans le flux → contradiction.
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        lambda now: {"Cuivre": {"LONG"}})
    r = _actif("Cuivre", "SHORT")
    assert sa._feed_news_contredit_call(r, "24h", _NOW) is True


def test_feed_news_confirme_ne_contredit_pas(monkeypatch):
    # News high SHORT alignée avec un call SHORT → PAS une contradiction.
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        lambda now: {"Cuivre": {"SHORT"}})
    r = _actif("Cuivre", "SHORT")
    assert sa._feed_news_contredit_call(r, "24h", _NOW) is False


def test_feed_news_absente_pas_de_contradiction(monkeypatch):
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", lambda now: {})
    r = _actif("Cuivre", "SHORT")
    assert sa._feed_news_contredit_call(r, "24h", _NOW) is False


def test_feed_news_sans_now_pas_de_contradiction(monkeypatch):
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        lambda now: {"Cuivre": {"LONG"}})
    r = _actif("Cuivre", "SHORT")
    assert sa._feed_news_contredit_call(r, "24h", None) is False


def test_drapeau_flag_pose_dans_les_deux_fonctions(monkeypatch):
    # Le ↯ doit apparaître dans la grille de synthèse ET dans la table Jouables
    # (les deux fonctions de flags doivent rester synchrones).
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        lambda now: {"Cuivre": {"LONG"}})
    r = _actif("Cuivre", "SHORT")
    assert "↯" in sa._synthese_cell_risk_flags(r, "24h", _NOW)
    assert sa.SURVEILLANCE_FLAGS["divergence_qn"] in sa._compute_cell_risk_flags(r, "24h", _NOW)


def test_pas_de_flag_si_news_aligne(monkeypatch):
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        lambda now: {"Cuivre": {"SHORT"}})
    r = _actif("Cuivre", "SHORT")
    assert "↯" not in sa._synthese_cell_risk_flags(r, "24h", _NOW)
