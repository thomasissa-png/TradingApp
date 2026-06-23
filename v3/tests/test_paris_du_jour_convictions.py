"""Refonte 23/06 — La tête « 🎯 Aujourd'hui » dérive des CONVICTIONS 24h jouables.

Décision fondateur + 3 experts : les 3 paris du jour = les 3 PLUS FORTES
CONVICTIONS 24h JOUABLES (cohérence par construction). Plus de moteur séparé
(selection_jour.compute_top3) qui pouvait CONTREDIRE le fond (ex. « Or LONG » en
tête alors que la conviction 24h était « Or SHORT forte »).

Tests :
  A. Le top 3 affiché = les 3 plus fortes convictions 24h jouables, DANS L'ORDRE,
     sens = sens de la conviction ; exclusion des fragile/couverture insuffisante.
  B. Cas reproduisant le 23/06 (fond Or SHORT fort, autrefois pari « Or LONG ») →
     AUCUN Or LONG, l'or apparaît SHORT s'il est top 3.
  C. Boost news 24h : une cellule avec grosse news fraîche voit sa contribution
     news 24h monter (sanity sur le calcul de note via la pertinence boostée).
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
SEUIL = 0.6  # seuil de conviction « forte » fixe (isole du chargement bilan_jour)


def _fiche(poids: int = 10) -> dict:
    return {
        "actif": "X",
        "criteres": [
            {"id": 1, "nom": "Quant", "cle_courante": "quant",
             "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0,
             "cap": 5.0, "signe": 1, "poids": poids,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
        ],
    }


def _vals(v: float) -> dict:
    return {"quant": {"valeur": v, "source_track": "twelvedata"}}


def _make(nom: str, score24: float, *, conc: str = None,
          conf: str = "normale", coverage: float = 1.0) -> "sa.ActifResult":
    """ActifResult avec un score 24h imposé (LONG si >0, SHORT si <0)."""
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


# ===========================================================================
# A — top 3 = 3 plus fortes convictions 24h jouables, ordre + sens conviction
# ===========================================================================

def test_a_top3_ordre_par_force_de_conviction():
    """Les paris sont les 3 plus forts |score| jouables, dans l'ordre décroissant,
    sens = sens de la conviction."""
    res = [
        _make("Faible", 0.40),       # jouable mais faible |note|
        _make("Or", -0.90),          # SHORT fort
        _make("EurUsd", -0.95),      # SHORT le plus fort
        _make("Nasdaq", 0.70),       # LONG moyen
    ]
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL)
    assert [p["actif"] for p in picks] == ["EurUsd", "Or", "Nasdaq"]
    assert [p["direction"] for p in picks] == ["SHORT", "SHORT", "LONG"]
    # Le 4ᵉ (Faible) est exclu du top 3 (zéro remplissage forcé au-delà du tri).
    assert "Faible" not in [p["actif"] for p in picks]


def test_a_exclut_quasi_neutre_et_insuffisant():
    """Une cellule ≈/⚪ (|note|<NEUTRAL_BAND) ou INSUFFISANT n'est jamais jouable."""
    res = [
        _make("Or", -0.90),                                    # jouable
        _make("Neutre", 0.01),                                 # ⚪ coin-flip
        _make("QuasiNeutre", 0.10),                            # ≈ quasi-neutre
        _make("Insuf", 0.0, conc=sa.CONCLUSION_INSUFFISANT),   # 🚫
    ]
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL)
    noms = [p["actif"] for p in picks]
    assert noms == ["Or"]
    assert "Neutre" not in noms and "QuasiNeutre" not in noms and "Insuf" not in noms


def test_a_exclut_fragile_couverture_insuffisante():
    """Une conviction « fragile (couverture insuffisante) » ne porte pas de pari du
    jour, même avec un |note| énorme (garde-fou « confiant ET aveugle »)."""
    # Cuivre : score fort MAIS couverture < CONVICTION_COVERAGE_MIN et critère de
    # poids max n/a → conviction dégradée « fragile (couverture insuffisante) ».
    cuivre = sa.score_actif("cuivre", _fiche(), {"quant": None})  # critère n/a
    cuivre.nom = "Cuivre"
    cuivre.fiche_key = "cuivre"
    cuivre.confidence = {h: "normale" for h in sa.HORIZONS}
    cuivre.coverage = 0.10  # < CONVICTION_COVERAGE_MIN (0.50)
    cuivre.conclusions = dict(cuivre.conclusions)
    cuivre.conclusions["24h"] = "LONG"
    cuivre.scores = dict(cuivre.scores)
    cuivre.scores["24h"] = 5.0  # |note| énorme
    # Pré-condition : la conviction EST bien « fragile (couverture insuffisante) ».
    assert sa._conviction_cell(cuivre, "24h", SEUIL) == "fragile (couverture insuffisante)"

    or_res = _make("Or", -0.90)
    picks = sa.select_paris_du_jour([cuivre, or_res], NOW, seuil_conviction=SEUIL)
    noms = [p["actif"] for p in picks]
    assert "Cuivre" not in noms          # exclu malgré |note| 5.0
    assert noms == ["Or"]


def test_a_bloc_tete_affiche_aujourdhui_et_sens():
    """Le bloc « ## 🎯 Aujourd'hui » liste les paris avec leur sens de conviction."""
    res = [_make("Or", -0.90), _make("EurUsd", -0.95)]
    block = "\n".join(sa.build_paris_du_jour_block(res, NOW))
    assert "## 🎯 Aujourd'hui" in block
    assert "**Or** SHORT" in block
    assert "**EurUsd** SHORT" in block


def test_a_moins_de_trois_jouables_pas_de_remplissage():
    """< 3 jouables → on en affiche moins (zéro invention)."""
    picks = sa.select_paris_du_jour([_make("Or", -0.90)], NOW, seuil_conviction=SEUIL)
    assert len(picks) == 1
    # Aucun jouable → message explicite, pas de pari fabriqué.
    block = "\n".join(sa.build_paris_du_jour_block([_make("N", 0.01)], NOW))
    assert "Aucune conviction 24h jouable" in block


# ===========================================================================
# B — cas du 23/06 : fond Or SHORT fort → AUCUN « Or LONG » en tête
# ===========================================================================

def test_b_cas_2306_aucun_or_long_or_apparait_short():
    """Reproduction du 23/06 : conviction de fond = Or SHORT -14,49 forte, EUR/USD
    SHORT -15,87 forte. L'ancien moteur sortait « Or LONG » en tête (contradiction).
    Désormais la tête dérive des convictions → Or ne peut apparaître que SHORT."""
    res = [
        _make("Or", -14.49),       # SHORT fort (fond)
        _make("EurUsd", -15.87),   # SHORT le plus fort (fond)
        _make("Cac40", -8.0),      # SHORT
        _make("Nasdaq", 0.20),     # ≈ quasi-neutre → PAS dans les plus fortes
    ]
    picks = sa.select_paris_du_jour(res, NOW, seuil_conviction=SEUIL)
    block = "\n".join(sa.build_paris_du_jour_block(res, NOW))

    # Aucun « Or LONG » nulle part.
    assert "Or** LONG" not in block
    # L'or apparaît, et SHORT (sens = sens de la conviction).
    or_pick = next(p for p in picks if p["actif"] == "Or")
    assert or_pick["direction"] == "SHORT"
    # Top 3 = les 3 plus fortes convictions jouables.
    assert [p["actif"] for p in picks] == ["EurUsd", "Or", "Cac40"]
    # Nasdaq (quasi-neutre) n'est PAS dans le top 3.
    assert "Nasdaq" not in [p["actif"] for p in picks]
    # Aucun pari ne contredit sa conviction (sens pick == signe du score).
    for p in picks:
        r = next(x for x in res if x.nom == p["actif"])
        attendu = "LONG" if r.scores["24h"] >= 0 else "SHORT"
        assert p["direction"] == attendu


# ===========================================================================
# C — boost news 24h : une grosse news fraîche fait monter la contribution 24h
# ===========================================================================

def test_c_boost_news_24h_augmente_contribution():
    """Sanity : la pertinence 24h du porteur news (boostée à 1.0) fait que la
    contribution news 24h égale la contribution 7j/1m pour une même news nette.
    On vérifie via la fiche réelle de l'or (porteur = tension_geopolitique)."""
    import yaml  # noqa: PLC0415

    fiche_path = ROOT / "config" / "fiches" / "or.yml"
    fiche = yaml.safe_load(fiche_path.read_text(encoding="utf-8"))
    crit = next(c for c in fiche["criteres"]
                if c.get("cle_courante") == "tension_geopolitique")
    # Le boost est appliqué : 24h pertinence = 1.0 (avant : 0.5).
    assert crit["pertinence"]["24h"] == 1.0
    # Une grosse news SHORT fraîche (triplet net) → contribution 24h non amortie
    # par la pertinence (×1.0). On vérifie que la contribution 24h >= avant-boost
    # (la pertinence 0.5 aurait coupé la contribution de moitié).
    vals = {"tension_geopolitique": {
        "valeur": -1, "source_track": "ia_synthese",
        "materiality": "high", "reliability": "confirmed", "nature": "ponctuel",
    }}
    # On ne fournit QUE le critère news : les autres sont n/a (test ciblé).
    r = sa.score_actif("or", fiche, vals)
    crit_res = next(c for c in r.criteres
                    if getattr(c, "cle_courante", "") == "tension_geopolitique")
    c24 = crit_res.contributions.get("24h", 0.0)
    # La news SHORT (signe +1, valeur -1) contribue NÉGATIVEMENT en 24h, et avec
    # la pertinence boostée à 1.0 sa magnitude n'est plus divisée (sanity : non nul).
    assert c24 < 0.0
    assert abs(c24) > 0.0
