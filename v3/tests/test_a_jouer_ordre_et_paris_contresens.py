"""Refonte 23/06 (Option C, fondateur + 3 experts) — UN SEUL principe d'ordre.

A. Tableau « À jouer aujourd'hui (24h) » : les convictions FORTES forment UN SEUL
   groupe trié par |note| décroissante. Le drapeau ↯ reste AFFICHÉ (colonne
   Drapeaux) mais ne réordonne plus → une forte ↯ à |note| plus grande passe
   AU-DESSUS d'une forte propre plus faible (l'inverse de l'ancien comportement
   « sans drapeau d'abord, avec drapeau ensuite »).

B. Paris du jour : exclusion des cellules ↯ (news à contre-sens). Même plus forte
   note, une cellule ↯ n'entre PAS dans les paris ; on prend la suivante non-↯.
   Si < 3 non-↯ éligibles → moins de 3 paris (zéro invention).

Le ↯ « news high du flux » (`_feed_news_contredit_call`) NE dégrade PAS la
conviction (`_conviction_cell` ne teste que `divergence_quant_news`) : une cellule
peut donc être à la fois « forte » ET porter ↯ — c'est précisément le cas testé.
On mocke `_fresh_high_feed_dirs` (source du ↯ feed) pour piloter le drapeau sans
toucher au scoring.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 6, 23, 9, 0, tzinfo=timezone.utc)
SEUIL = 0.6  # seuil « forte » fixe (isole du chargement bilan_jour)


def _fiche(poids: int = 10) -> dict:
    # 3 critères équilibrés : évite le drapeau ◧ « mono-critère dominant » (qui
    # dégraderait la conviction en « fragile (1 seul critère) » au lieu de
    # « forte »). On veut isoler le ↯ (news à contre-sens) du ◧.
    return {
        "actif": "X",
        "criteres": [
            {"id": i, "nom": f"Quant{i}", "cle_courante": f"quant{i}",
             "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0,
             "cap": 5.0, "signe": 1, "poids": poids,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}}
            for i in (1, 2, 3)
        ],
    }


def _vals(v: float) -> dict:
    return {f"quant{i}": {"valeur": v, "source_track": "twelvedata"}
            for i in (1, 2, 3)}


def _make(nom: str, score24: float, *, conc: str = None,
          conf: str = "normale", coverage: float = 1.0) -> "sa.ActifResult":
    r = sa.score_actif(nom.lower(), _fiche(), _vals(1.0))
    r.nom = nom
    r.fiche_key = nom.lower()
    r.confidence = {h: conf for h in sa.HORIZONS}
    r.coverage = coverage
    if conc is None:
        conc = "LONG" if score24 >= 0 else "SHORT"
    r.conclusions = dict(r.conclusions)
    r.conclusions["24h"] = conc
    r.scores = dict(r.scores)
    r.scores["24h"] = score24
    return r


def _feed_dirs_for(noms_sens: dict):
    """Renvoie une fonction de remplacement de `_fresh_high_feed_dirs` : pour
    chaque actif, l'ensemble des sens OPPOSÉS au call que porte une news high
    fraîche (donc déclenche ↯ via `_feed_news_contredit_call`)."""
    def _patched(_now):
        return {nom: set(sens) for nom, sens in noms_sens.items()}
    return _patched


# ===========================================================================
# A — Tableau : ordre purement par |note| dans le groupe « Conviction forte »
# ===========================================================================

def test_a_forte_contresens_au_dessus_de_forte_propre(monkeypatch):
    """Une forte ↯ (|note| plus grande) s'affiche AU-DESSUS d'une forte propre
    (|note| plus petite). Inverse de l'ancien « sans drapeau d'abord »."""
    res = [
        _make("Or", -16.69),      # SHORT fort, recevra ↯ via news high du flux
        _make("Argent", -6.09),   # SHORT fort, propre
    ]
    # Or SHORT → une news high LONG du flux contredit le call → ↯ feed actif.
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        _feed_dirs_for({"Or": {"LONG"}}))

    # Pré-conditions : les deux sont « forte » (le ↯ feed ne dégrade PAS la conv).
    assert sa._conviction_cell(res[0], "24h", SEUIL) == "forte"
    assert sa._conviction_cell(res[1], "24h", SEUIL) == "forte"
    assert sa._cell_news_a_contresens(res[0], "24h", NOW) is True
    assert sa._cell_news_a_contresens(res[1], "24h", NOW) is False

    lines = sa.build_a_jouer_block(res, NOW, seuil_conviction=SEUIL)
    block = "\n".join(lines)
    # Un seul groupe « Conviction forte » (plus de découpage sans/avec drapeau).
    assert "_Conviction forte_" in block
    assert "sans drapeau" not in block
    assert "avec drapeau" not in block
    # Or (|note| 16.69, ↯) apparaît AVANT Argent (|note| 6.09, propre).
    rang_or = next(i for i, ln in enumerate(lines) if ln.startswith("| Or "))
    rang_argent = next(i for i, ln in enumerate(lines) if ln.startswith("| Argent "))
    assert rang_or < rang_argent
    # Le drapeau ↯ reste affiché dans la ligne de l'Or (avertissement inline).
    ligne_or = lines[rang_or]
    assert "↯" in ligne_or


def test_a_groupe_autres_jouables_reste_sous_forte(monkeypatch):
    """Le groupe « autres lignes jouables » (conviction non-forte) reste en
    dessous du groupe « Conviction forte » (axe différent : force, pas drapeau)."""
    res = [
        _make("Or", -16.69),     # forte
        _make("Cuivre", -0.40),  # jouable mais non-forte (|note| < seuil)
    ]
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", _feed_dirs_for({}))
    block = "\n".join(sa.build_a_jouer_block(res, NOW, seuil_conviction=SEUIL))
    assert "_Conviction forte_" in block
    assert "_Autres lignes jouables_" in block
    assert block.index("_Conviction forte_") < block.index("_Autres lignes jouables_")


# ===========================================================================
# B — Paris du jour : exclusion des ↯ (news à contre-sens)
# ===========================================================================

def test_b_paris_excluent_contresens_meme_plus_forte_note(monkeypatch):
    """Une cellule ↯, même plus forte note, n'est PAS dans les paris ; la suivante
    non-↯ est prise."""
    res = [
        _make("Or", -16.69),       # plus forte note, MAIS ↯ → exclue
        _make("EurUsd", -15.97),   # 2ᵉ note, MAIS ↯ → exclue
        _make("Argent", -6.09),    # propre → pari
        _make("Petrole", -1.86),   # propre mais < NEUTRAL_BAND ? non, > seuil ? non
    ]
    # Or & EUR/USD : news high à contre-sens (call SHORT → news high LONG).
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        _feed_dirs_for({"Or": {"LONG"}, "EurUsd": {"LONG"}}))
    ecartes: list = []
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL,
                                    ecartes_contresens=ecartes)
    noms = [p["actif"] for p in picks]
    # Or & EUR/USD écartés malgré la note la plus forte.
    assert "Or" not in noms
    assert "EurUsd" not in noms
    # Les non-↯ sont pris, par |note| décroissante.
    assert noms == ["Argent", "Petrole"]
    # Transparence : Or & EUR/USD (top par note sans le filtre) sont tracés.
    assert {e["actif"] for e in ecartes} == {"Or", "EurUsd"}


def test_b_moins_de_trois_non_contresens(monkeypatch):
    """Si < 3 cellules non-↯ éligibles → moins de 3 paris (s'abstenir est valide)."""
    res = [
        _make("Or", -16.69),       # ↯ → exclu
        _make("EurUsd", -15.97),   # ↯ → exclu
        _make("Argent", -6.09),    # propre → seul pari
    ]
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        _feed_dirs_for({"Or": {"LONG"}, "EurUsd": {"LONG"}}))
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL)
    assert [p["actif"] for p in picks] == ["Argent"]
    assert len(picks) == 1


def test_b_cellule_non_contresens_forte_reste_selectionnee(monkeypatch):
    """Une cellule NON-↯ forte est sélectionnée normalement (pas de sur-filtrage)."""
    res = [_make("Argent", -6.09), _make("Petrole", -1.86)]
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs", _feed_dirs_for({}))
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL)
    assert [p["actif"] for p in picks] == ["Argent", "Petrole"]


def test_b_transparence_mention_dans_le_bloc(monkeypatch):
    """Le bloc « 🎯 Aujourd'hui » mentionne l'écart pour news à contre-sens (↯)."""
    res = [
        _make("Or", -16.69),       # ↯ → écarté (top par note)
        _make("Argent", -6.09),    # propre → pari
    ]
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        _feed_dirs_for({"Or": {"LONG"}}))
    block = "\n".join(sa.build_paris_du_jour_block(res, NOW))
    assert "**Argent** SHORT" in block
    assert "Or" in block and "news à contre-sens" in block and "↯" in block


# ===========================================================================
# Reproduction du cas 23/06 (Or -16,69 ↯, EUR/USD -15,97 ↯, Argent -6,09 propre,
# Pétrole -1,86 propre) : ordre tableau par note + paris = Argent, Pétrole.
# ===========================================================================

def test_cas_2306_ordre_tableau_et_paris(monkeypatch):
    res = [
        _make("Or", -16.69),
        _make("EurUsd", -15.97),
        _make("Argent", -6.09),
        _make("Petrole", -1.86),
    ]
    monkeypatch.setattr(sa, "_fresh_high_feed_dirs",
                        _feed_dirs_for({"Or": {"LONG"}, "EurUsd": {"LONG"}}))

    # Tableau : ordre purement par |note| dans « Conviction forte ».
    lines = sa.build_a_jouer_block(res, NOW, seuil_conviction=SEUIL)
    ordre = [ln.split("|")[1].strip() for ln in lines
             if ln.startswith("| ") and ln.split("|")[1].strip()
             in {"Or", "EurUsd", "Argent", "Petrole"}]
    # Or et EUR/USD (les plus fortes notes) en tête, drapeau ↯ affiché mais non
    # réordonnant ; Argent puis Pétrole ensuite.
    assert ordre[0] in {"Or", "EurUsd"}
    assert ordre[1] in {"Or", "EurUsd"}
    assert ordre.index("Argent") > ordre.index("Or")
    assert ordre.index("Argent") > ordre.index("EurUsd")

    # Paris : Or & EUR/USD exclus (↯) → paris = Argent, Pétrole.
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL)
    assert [p["actif"] for p in picks] == ["Argent", "Petrole"]
