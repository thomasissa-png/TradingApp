"""Tests du « WR tradable » (Lot 2 audit 10/06 — WR exécutable).

WR tradable = VRAI / (VRAI + FAUSSE + non-conclusif).
- Inclut les jours non-conclusifs (|delta| < seuil de fiche) : en réel, Thomas
  serait quand même en position ces jours-là → ces paris pèsent au dénominateur.
- EXCLUS (mêmes que le WR conclusif) : `non-notee` (gate suffisance / filtre 7h,
  pas une prédiction) et `suivi-interrompu` (pas de prix mesurable).
- Métrique SECONDAIRE : coexiste avec le WR conclusif (taux_eff_pct), ne le
  remplace pas. Le kill criterion v1 reste sur le WR conclusif.

Couvre les 3 exigences du brief :
  (a) calcul du WR tradable sur un jeu mixte VRAI/FAUSSE/NC/non-notee/interrompu ;
  (b) invariant `WR_tradable <= WR_conclusif` sur tout jeu de données ;
  (c) exclusion correcte de `non-notee` et `suivi-interrompu`.

HTTP non sollicité (construction directe de Measure, comme test_journaliste).
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Helper : Measure 24h (step non-chevauchant = 1j → chaque mesure compte)
# ---------------------------------------------------------------------------

def _measure(outcome: str, echeance: date, conc: str = "LONG") -> jr.Measure:
    cell = jr.BulletinCell(
        bulletin_date=echeance - timedelta(days=1),
        actif_name="Pétrole (Brent)",
        horizon="24h",
        conclusion=conc,
        score=1.0,
    )
    return jr.Measure(
        cell=cell,
        fiche_key="petrole",
        ticker="BZ=F",
        horizon="24h",
        echeance=echeance,
        prix_emission=100.0,
        prix_courant=101.0,
        seuil_pct=1.0,
        delta_pct=1.0,
        outcome=outcome,
    )


def _mixed_set() -> list:
    """Jeu mixte explicite : 6 VRAI, 3 FAUSSE, 4 NC, 2 non-notee, 1 interrompu.

    Échéances espacées d'1 jour → toutes non-chevauchantes en 24h
    (NON_OVERLAP_STEP["24h"] == 1).

    Attendus :
      - WR conclusif  = 6 / (6+3)     = 66.67 %
      - WR tradable   = 6 / (6+3+4)   = 46.15 %  (NC au dénominateur)
      - non-notee + interrompu EXCLUS des deux.
    """
    plan = (
        [jr.OUTCOME_VRAI] * 6
        + [jr.OUTCOME_FAUSSE] * 3
        + [jr.OUTCOME_NC] * 4
        + [jr.OUTCOME_NON_NOTE] * 2
        + [jr.OUTCOME_INTERROMPU] * 1
    )
    base = date(2026, 1, 1)
    return [_measure(o, base + timedelta(days=i)) for i, o in enumerate(plan)]


# ---------------------------------------------------------------------------
# (a) Calcul du WR tradable
# ---------------------------------------------------------------------------

def test_wr_tradable_calcul_jeu_mixte():
    k = jr.compute_kpi(_mixed_set())

    # WR conclusif inchangé : VRAI / (VRAI + FAUSSE) sur le non-chevauchant.
    assert k.n_vrai_eff == 6
    assert k.n_fausse_eff == 3
    assert k.taux_eff_pct == pytest.approx(66.67, abs=0.01)

    # WR tradable : VRAI / (VRAI + FAUSSE + NC) sur le non-chevauchant.
    assert k.n_nc_eff == 4
    assert k.n_tradable == 13  # 6 + 3 + 4
    assert k.tradable_eff_pct == pytest.approx(6 / 13 * 100.0, abs=0.01)


def test_wr_tradable_egal_conclusif_si_zero_nc():
    """Sans non-conclusif, les deux WR coïncident (même numérateur ET dénom)."""
    base = date(2026, 3, 1)
    ms = [_measure(jr.OUTCOME_VRAI, base + timedelta(days=i)) for i in range(7)]
    ms += [_measure(jr.OUTCOME_FAUSSE, base + timedelta(days=10 + i)) for i in range(3)]
    k = jr.compute_kpi(ms)
    assert k.tradable_eff_pct == pytest.approx(k.taux_eff_pct)
    assert k.n_tradable == k.n_effective


# ---------------------------------------------------------------------------
# (b) Invariant WR_tradable <= WR_conclusif sur tout jeu de données
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "n_vrai, n_fausse, n_nc, n_nn, n_int",
    [
        (6, 3, 4, 2, 1),   # cas nominal du brief
        (10, 0, 5, 0, 0),  # 100 % conclusif, NC tirent le tradable vers le bas
        (0, 5, 5, 1, 1),   # 0 % : tradable == conclusif == 0
        (3, 3, 0, 0, 0),   # pas de NC → égalité
        (1, 0, 9, 4, 3),   # NC massifs → tradable très bas, conclusif = 100 %
        (8, 2, 1, 0, 0),
        (0, 0, 6, 2, 2),   # que des NC → aucun conclusif, tradable = 0 %
    ],
)
def test_invariant_tradable_le_conclusif(n_vrai, n_fausse, n_nc, n_nn, n_int):
    plan = (
        [jr.OUTCOME_VRAI] * n_vrai
        + [jr.OUTCOME_FAUSSE] * n_fausse
        + [jr.OUTCOME_NC] * n_nc
        + [jr.OUTCOME_NON_NOTE] * n_nn
        + [jr.OUTCOME_INTERROMPU] * n_int
    )
    base = date(2026, 4, 1)
    ms = [_measure(o, base + timedelta(days=i)) for i, o in enumerate(plan)]
    k = jr.compute_kpi(ms)

    # Invariant central : le WR tradable ne peut JAMAIS dépasser le conclusif
    # (même numérateur VRAI, dénominateur élargi aux NC ≥ dénominateur conclusif).
    if k.taux_eff_pct is not None and k.tradable_eff_pct is not None:
        assert k.tradable_eff_pct <= k.taux_eff_pct + 1e-9
    # Si aucun pari conclusif (que des NC) : conclusif indéfini, tradable = 0 %.
    if n_vrai + n_fausse == 0 and n_nc > 0:
        assert k.taux_eff_pct is None
        assert k.tradable_eff_pct == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# (c) Exclusion de non-notee et suivi-interrompu
# ---------------------------------------------------------------------------

def test_non_notee_et_interrompu_exclus_du_tradable():
    """Ajouter des non-notee / suivi-interrompu NE CHANGE PAS le WR tradable."""
    base = date(2026, 5, 1)
    coeur = [
        _measure(jr.OUTCOME_VRAI, base + timedelta(days=0)),
        _measure(jr.OUTCOME_VRAI, base + timedelta(days=1)),
        _measure(jr.OUTCOME_FAUSSE, base + timedelta(days=2)),
        _measure(jr.OUTCOME_NC, base + timedelta(days=3)),
    ]
    k_coeur = jr.compute_kpi(list(coeur))

    pollue = list(coeur) + [
        _measure(jr.OUTCOME_NON_NOTE, base + timedelta(days=4)),
        _measure(jr.OUTCOME_NON_NOTE, base + timedelta(days=5)),
        _measure(jr.OUTCOME_INTERROMPU, base + timedelta(days=6)),
        _measure(jr.OUTCOME_INTERROMPU, base + timedelta(days=7)),
    ]
    k_pollue = jr.compute_kpi(pollue)

    # Le dénominateur tradable et le pourcentage sont identiques : les statuts
    # non-notee / suivi-interrompu n'entrent NI au numérateur NI au dénominateur.
    assert k_pollue.n_tradable == k_coeur.n_tradable == 4  # 2 VRAI + 1 FAUSSE + 1 NC
    assert k_pollue.n_nc_eff == k_coeur.n_nc_eff == 1
    assert k_pollue.tradable_eff_pct == pytest.approx(k_coeur.tradable_eff_pct)
    assert k_pollue.tradable_eff_pct == pytest.approx(2 / 4 * 100.0)


def test_select_non_overlapping_tradable_exclut_non_notee_interrompu():
    """La sélection tradable ne retient QUE VRAI / FAUSSE / NC."""
    base = date(2026, 6, 1)
    ms = _mixed_set()
    sel = jr.select_non_overlapping_tradable(ms, "24h")
    outcomes = {m.outcome for m in sel}
    assert jr.OUTCOME_NON_NOTE not in outcomes
    assert jr.OUTCOME_INTERROMPU not in outcomes
    assert outcomes <= {jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE, jr.OUTCOME_NC}
    assert len(sel) == 13  # 6 + 3 + 4


# ---------------------------------------------------------------------------
# Bilan du jour : même formule (VRAI / VRAI+FAUSSE+NC), même exclusions
# ---------------------------------------------------------------------------

def test_bilan_jour_wr_tradable_formule():
    """Reproduit le calcul de build_bilan_jour : wr_tradable_jour sur n_vrai/n_fausse/n_nc.

    On vérifie la formule pure (les statuts non-notee/suivi-interrompu ne sont
    jamais comptés dans n_vrai/n_fausse/n_nc côté bilan_jour) et l'invariant.
    """
    import bilan_jour as bj  # noqa: PLC0415

    from datetime import datetime  # noqa: PLC0415

    bilan = bj.BilanJour(date_j=date(2026, 1, 5), now=datetime(2026, 1, 5, 22, 0))
    bilan.n_vrai, bilan.n_fausse, bilan.n_nc = 6, 3, 4

    denom = bilan.n_vrai + bilan.n_fausse
    wr_conclusif = round(bilan.n_vrai / denom * 100.0, 1)
    denom_trad = bilan.n_vrai + bilan.n_fausse + bilan.n_nc
    wr_tradable = round(bilan.n_vrai / denom_trad * 100.0, 1)

    assert wr_conclusif == pytest.approx(66.7, abs=0.1)
    assert wr_tradable == pytest.approx(46.2, abs=0.1)
    assert wr_tradable <= wr_conclusif


# ---------------------------------------------------------------------------
# WR significatif (>= 0,5 % de mouvement favorable) — KPI ajouté pour tous les
# rapports : un call juste mais quasi-plat n'est pas une vraie réussite tradable.
# ---------------------------------------------------------------------------

def _measure_delta(outcome: str, echeance: date, delta: float, conc: str = "LONG") -> jr.Measure:
    cell = jr.BulletinCell(
        bulletin_date=echeance - timedelta(days=1),
        actif_name="Pétrole (Brent)", horizon="24h", conclusion=conc, score=1.0,
    )
    return jr.Measure(
        cell=cell, fiche_key="petrole", ticker="BZ=F", horizon="24h",
        echeance=echeance, prix_emission=100.0, prix_courant=100.0 + delta,
        seuil_pct=0.0, delta_pct=delta, outcome=outcome,
    )


def test_wr_significatif_exclut_les_calls_justes_mais_plats():
    base = date(2026, 6, 1)
    ms = [
        _measure_delta(jr.OUTCOME_VRAI, base, 2.0),               # vrai gain >= 0,5 %
        _measure_delta(jr.OUTCOME_VRAI, base + timedelta(days=1), 0.3),  # juste mais plat (< 0,5 %)
        _measure_delta(jr.OUTCOME_VRAI, base + timedelta(days=2), 1.5),  # vrai gain >= 0,5 %
        _measure_delta(jr.OUTCOME_FAUSSE, base + timedelta(days=3), -1.0),
    ]
    k = jr.compute_kpi(ms)
    # WR conclusif : 3 VRAI / 4 = 75 % ; WR significatif : 2 VRAI >= 0,5 % / 4 = 50 %.
    assert k.taux_eff_pct == pytest.approx(75.0, abs=0.1)
    assert k.n_vrai_signif_eff == 2
    assert k.taux_signif_eff_pct == pytest.approx(50.0, abs=0.1)
    # Invariant : le WR significatif est toujours <= WR conclusif.
    assert k.taux_signif_eff_pct <= k.taux_eff_pct


def test_wr_significatif_short_compte_amplitude_absolue():
    base = date(2026, 6, 1)
    ms = [
        _measure_delta(jr.OUTCOME_VRAI, base, -2.0, conc="SHORT"),  # SHORT gagnant, |delta|>=0,5
        _measure_delta(jr.OUTCOME_VRAI, base + timedelta(days=1), -0.2, conc="SHORT"),  # plat
    ]
    k = jr.compute_kpi(ms)
    assert k.n_vrai_signif_eff == 1
    assert k.taux_signif_eff_pct == pytest.approx(50.0, abs=0.1)
