"""Régression : parsing du format COURANT (19 cols) de l'events-log.

Le schéma de l'events-log a évolué : materiality|reliability ne sont PLUS les 2
dernières colonnes — event_id|canonical_date|nature (+ colonnes vides) viennent
APRÈS. L'ancien parser briefing (regex « ancré en fin de ligne ») ne matchait plus
le format 19 cols → fallback → materiality="" → « 0 à impact » partout.

Ces tests verrouillent : (1) parse 19 cols → materiality/reliability/impacts/nature
correctes ; (2) filter_recent_impactful garde les high/medium récents ; (3) News par
actif non vide quand events à impact présents ; (4) rétro-compat 11 et 14 cols ;
(5) robustesse à une colonne future surnuméraire (21 cols).
"""
import sys
from datetime import date
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import briefing  # noqa: E402


# Format COURANT 19 cols :
# date|l1|l2|trigger|cours|latence|r|source|zone|cat|pat|impacts|materiality|
# reliability|event_id|canonical_date|nature|<vide>|<vide>
FIXTURE_V3 = """| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id | impacts | materiality | reliability | event_id | canonical_date | nature |  |  |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-19 |  | Iran-Moyen-Orient | Accord de paix iranien permet la reprise du transit pétrolier | BRENT |  | 1 | investing_commod | Moyen-Orient | geopolitical |  | BRENT:SHORT:high;GOLD:SHORT:medium;VIX:SHORT:medium;SP500:LONG:medium | high | confirmed | 9821f821f871 | 2026-06-19 | structurel |  |  |
| 2026-06-19 |  | Fed-Iran | Fed hawkish shift and Iran peace deal optimism | GOLD |  | 1 | investing_metals | Global | macro |  | GOLD:SHORT:medium | medium | reported | 46982ef2e1e4 | 2026-06-19 | verbal |  |  |
| 2026-06-19 |  | Silver | Analyse structurelle du déséquilibre offre-demande d'argent | SILVER |  | 1 | investing_commodities | Global | commodity |  | SILVER:LONG:low | low | reported | a65f7181c7fa | 2026-06-19 | structurel |  |  |
"""


@pytest.fixture
def today():
    return date(2026, 6, 19)


@pytest.fixture
def log_v3(tmp_path):
    p = tmp_path / "events-log.md"
    p.write_text(FIXTURE_V3, encoding="utf-8")
    return p


def test_parse_v3_extracts_materiality_reliability(log_v3):
    """Le format 19 cols → materiality/reliability/impacts/nature à leur position
    RÉELLE (pas supposées en fin de ligne)."""
    evs = briefing.parse_events(log_v3)
    assert len(evs) == 3
    accord = evs[0]
    assert accord["materiality"] == "high"
    assert accord["reliability"] == "confirmed"
    assert accord["impacts"].startswith("BRENT:SHORT:high")
    assert accord["nature"] == "structurel"
    assert accord["event_id"] == "9821f821f871"
    # Le bug historique : materiality récupérait event_id/nature/"". On vérifie
    # qu'elle ne contient JAMAIS un id ou une colonne de queue.
    assert accord["materiality"] in ("high", "medium", "low")


def test_filter_keeps_high_medium_recent_v3(log_v3, today):
    """filter_recent_impactful garde les events high/medium récents du format 19 cols."""
    evs = briefing.parse_events(log_v3)
    kept = briefing.filter_recent_impactful(evs, today)
    mats = sorted((e.get("materiality") or "") for e in kept)
    assert "high" in mats
    assert "medium" in mats
    assert len(kept) >= 2


def test_news_par_actif_non_vide_v3(log_v3, today):
    """News par actif n'est PAS « aucune actualité » partout quand des events à
    impact existent (régression directe du bug « 0 à impact »)."""
    md = briefing.build_news_par_actif(log_v3, today=today)
    assert "Accord de paix iranien" in md
    assert "Fed hawkish shift" in md
    # Pétrole et Or doivent avoir leur news (donc pas « aucune actualité » sur eux).
    petrole_section = md.split("### Pétrole", 1)[1].split("###", 1)[0]
    assert "aucune actualité" not in petrole_section
    or_section = md.split("### Or", 1)[1].split("###", 1)[0]
    assert "aucune actualité" not in or_section


def test_top_news_high_first_v3(log_v3, today):
    """Le Top news met le high (accord Iran) en tête (matérialité bien lue)."""
    evs = briefing.parse_events(log_v3)
    impactful = briefing.filter_recent_impactful(evs, today)
    lignes = briefing._top_news_lignes(impactful)
    assert lignes, "Top news ne doit pas être vide avec un event high présent"
    assert "(high)" in lignes[0]


def test_retrocompat_11_et_14_cols(tmp_path, today):
    """Rétro-compat : les anciens batches (11 et 14 cols) restent lisibles."""
    mixed = (
        "| 2026-06-19 |  | legacy11 | legacy event | Brent (BZ=F) | intraday | 1 "
        "| s | Global | geopolitical |  |\n"
        "| 2026-06-19 |  | v2_14 | v2 event | BRENT | intraday | 1 | s | Global "
        "| geopolitical |  | BRENT:LONG:high | high | confirmed |\n"
    )
    p = tmp_path / "events-log.md"
    p.write_text(mixed, encoding="utf-8")
    evs = briefing.parse_events(p)
    assert len(evs) == 2
    # legacy 11 : pas de materiality
    assert evs[0]["materiality"] == ""
    assert evs[0]["impacts"] == ""
    # v2 14 : materiality lue
    assert evs[1]["materiality"] == "high"
    assert evs[1]["impacts"] == "BRENT:LONG:high"


def test_robustesse_colonne_future_surnumeraire(tmp_path, today):
    """Robustesse anti-régression : une colonne FUTURE en queue (21 cols) ne doit
    PAS re-casser la lecture de materiality/reliability (lues par index, pas en
    fin de ligne)."""
    future = (
        "| 2026-06-19 |  | Future | event futur | BRENT |  | 1 | s | Global "
        "| geopolitical |  | BRENT:SHORT:high | high | confirmed | id123 "
        "| 2026-06-19 | structurel |  |  | colonne_v4 | encore_une |\n"
    )
    p = tmp_path / "events-log.md"
    p.write_text(future, encoding="utf-8")
    evs = briefing.parse_events(p)
    assert len(evs) == 1
    assert evs[0]["materiality"] == "high"
    assert evs[0]["reliability"] == "confirmed"
    assert evs[0]["nature"] == "structurel"
