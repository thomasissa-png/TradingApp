"""Tests (B) — NOTE NORMALISÉE COMPARABLE ENTRE ACTIFS (Zone 1.1).

La Note brute est une SOMME pondérée → sa magnitude dépend du nombre/poids des
critères couverts → « Cacao +6.45 » vs « CAC +0.61 » n'est PAS comparable entre
actifs. La note normalisée = note ÷ Σ|poids effectif couvert| ramène à une échelle
commune ~[-1, +1].

VERROUS (red line) :
- la note normalisée est INFORMATIVE (pur affichage), jamais décisionnelle ;
- elle n'altère NI la note brute, NI la direction, NI la sélection.

Vérifie :
- formule note_norm = note / Σ(|poids|×pertinence) sur critères couverts ;
- comparabilité (cacao note brute forte vs CAC note brute faible → intensités
  du même ordre) ;
- exclusion des gates / n/a / momentum-prix du dénominateur ;
- dégradation propre (aucun critère couvert → None) ;
- bornage ~[-1, 1] (|valeur_norm| ≤ 1) ;
- la note brute n'est PAS touchée par le calcul.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


def _crit(cle, poids, valeur_norm, pert, *, is_gate=False, is_na=False):
    return sa.CritereResult(
        id=cle, nom=cle, type_norm="zscore", valeur_brute=0.0,
        valeur_norm=valeur_norm, poids=poids, signe=1,
        pertinence={"24h": pert, "7j": pert, "1m": pert},
        note="", is_gate=is_gate, is_na=is_na, cle_courante=cle,
    )


# --- Formule de base --------------------------------------------------------

def test_formule_note_normalisee():
    """note_norm = note / Σ(|poids| × pertinence) sur critères couverts."""
    criteres = [
        _crit("a", poids=10, valeur_norm=0.5, pert=1.0),   # contrib 5.0
        _crit("b", poids=4, valeur_norm=0.25, pert=1.0),   # contrib 1.0
    ]
    note_brute = 6.0  # 5.0 + 1.0
    # dénominateur = 10*1.0 + 4*1.0 = 14
    nn = sa.compute_note_normalisee(criteres, note_brute, "7j")
    assert nn == pytest.approx(6.0 / 14.0)


def test_gate_et_na_exclus_du_denominateur():
    """Gates, n/a et momentum-prix ne comptent PAS dans Σ|poids couvert|."""
    criteres = [
        _crit("a", poids=10, valeur_norm=0.5, pert=1.0),
        _crit("gate", poids=0, valeur_norm=None, pert=1.0, is_gate=True),
        _crit("absent", poids=8, valeur_norm=None, pert=1.0, is_na=True),
        _crit("momentum_prix_x", poids=6, valeur_norm=1.0, pert=1.0),  # exclu
    ]
    nn = sa.compute_note_normalisee(criteres, 5.0, "7j")
    # dénominateur = seul "a" couvert non-momentum = 10*1.0 = 10
    assert nn == pytest.approx(5.0 / 10.0)


def test_degradation_propre_aucun_critere_couvert():
    """Aucun critère couvert → None (rendu « — »)."""
    criteres = [
        _crit("gate", poids=0, valeur_norm=None, pert=1.0, is_gate=True),
        _crit("absent", poids=8, valeur_norm=None, pert=1.0, is_na=True),
    ]
    assert sa.compute_note_normalisee(criteres, 0.0, "7j") is None


def test_borne_environ_moins_un_plus_un():
    """|valeur_norm| ≤ 1 → |note_norm| ≤ 1 (intensité comparable bornée)."""
    criteres = [
        _crit("a", poids=11, valeur_norm=1.0, pert=0.9),
        _crit("b", poids=5, valeur_norm=1.0, pert=0.9),
    ]
    note_max = 11 * 1.0 * 0.9 + 5 * 1.0 * 0.9  # contributions maximales
    nn = sa.compute_note_normalisee(criteres, note_max, "7j")
    assert nn == pytest.approx(1.0)
    assert -1.0 <= nn <= 1.0


# --- Comparabilité entre actifs (cœur de la demande B) ----------------------

def test_comparabilite_cacao_vs_cac():
    """Cacao (note brute FORTE car bcp de poids couvert) vs CAC (note brute FAIBLE
    car peu de poids couvert) : leurs notes BRUTES ne sont pas comparables, mais
    leurs INTENSITÉS normalisées le sont (même ordre de grandeur)."""
    # Cacao : bcp de critères couverts, tous fortement haussiers → note brute FORTE.
    cacao = [
        _crit("meteo", poids=11, valeur_norm=0.80, pert=0.9),
        _crit("arrivees", poids=9, valeur_norm=0.80, pert=1.0),
        _crit("hf", poids=5, valeur_norm=0.70, pert=0.8),
        _crit("spread", poids=4, valeur_norm=0.60, pert=0.9),
    ]
    note_cacao = sum(c.valeur_norm * c.poids * c.pertinence["7j"] * c.signe
                     for c in cacao if c.valeur_norm is not None)
    # CAC : 2 critères couverts, poids légers, faiblement haussiers → note brute FAIBLE.
    cac = [
        _crit("oat", poids=4, valeur_norm=0.30, pert=0.5),
        _crit("vol", poids=3, valeur_norm=0.10, pert=0.5),
    ]
    note_cac = sum(c.valeur_norm * c.poids * c.pertinence["7j"] * c.signe
                   for c in cac if c.valeur_norm is not None)

    nn_cacao = sa.compute_note_normalisee(cacao, note_cacao, "7j")
    nn_cac = sa.compute_note_normalisee(cac, note_cac, "7j")
    # Les notes BRUTES diffèrent fortement en magnitude (incomparables)…
    assert abs(note_cacao) > 5 * abs(note_cac), (note_cacao, note_cac)
    # …mais les INTENSITÉS normalisées sont du même ordre (comparables, ~[-1,1]) :
    assert -1.0 <= nn_cacao <= 1.0
    assert -1.0 <= nn_cac <= 1.0
    # Cacao = critères forts → intensité plus haute que CAC, mais pas d'un facteur 5+.
    assert abs(nn_cacao) > abs(nn_cac)
    assert abs(nn_cacao) / abs(nn_cac) < 5.0


# --- Verrou : la note brute n'est PAS modifiée ------------------------------

def test_note_brute_inchangee():
    """compute_note_normalisee NE modifie pas la note brute passée (pure fonction)."""
    criteres = [_crit("a", poids=10, valeur_norm=0.5, pert=1.0)]
    note = 5.0
    _ = sa.compute_note_normalisee(criteres, note, "7j")
    assert note == 5.0  # inchangée (immutable float, mais on verrouille l'intention)
    # idempotence : 2 appels → même résultat
    assert sa.compute_note_normalisee(criteres, note, "7j") == \
        sa.compute_note_normalisee(criteres, note, "7j")
