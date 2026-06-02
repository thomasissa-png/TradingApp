"""Tests du GATE DE SUFFISANCE DE DONNÉES (sécurité demandée par Thomas).

Le gate empêche de noter LONG/SHORT avec fausse confiance quand trop de
données manquent. Spec :
  - coverage pondéré = Σ |poids| couverts / Σ |poids| totaux (critères non-gate)
  - coverage < COVERAGE_MIN (0.40) → conclusion = INSUFFISANT (override jamais-neutre)
  - COVERAGE_MIN ≤ coverage < COVERAGE_OK (0.65) OU données périmées → confidence "faible"
  - sinon → confidence "normale"
  - cellules INSUFFISANT exclues du calcul VRAI/FAUX ET du biais LONG/SHORT côté journaliste

Couvre : coverage pondéré jouet, 3 paliers, override jamais-neutre, périmé→faible,
journaliste exclusion VRAI/FAUX et biais, affichage bulletin 🚫/⚠️.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402
import journaliste as jo  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fiches_dir():
    return ROOT / "config" / "fiches"


@pytest.fixture
def petrole(fiches_dir):
    fiches = sa.load_fiches(fiches_dir)
    return fiches["petrole"]


def _all_neutral_petrole_valeurs():
    """Toutes les valeurs neutres pour atteindre coverage = 100% sur petrole."""
    return {
        "eia_crude_surprise": {"valeur_normalisee": 0.0},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
        "tension_geopol_moyen_orient": {"valeur": 0},
        "cftc_cot_crude_nets": {"valeur_normalisee": 0.0},
        "opec_production_policy": {"valeur": 0},
        "brent_term_structure_m1m2": {"valeur": 0.0},
        "dxy_trend_20j": {"valeur_normalisee": 0.0},
        "cushing_stocks": {"valeur_normalisee": 0.0},
        "spread_brent_wti": {"valeur": 0.0},
        "caixin_pmi_manuf": {"valeur": 50.0},
    }


# ---------------------------------------------------------------------------
# 1. Calcul coverage pondéré — cas jouet
# ---------------------------------------------------------------------------

def _crit(poids: float, valeur_norm, is_gate: bool = False):
    """Helper : crée un CritereResult minimal pour tester compute_coverage."""
    return sa.CritereResult(
        id=None,
        nom="x",
        type_norm="lineaire",
        valeur_brute=None,
        valeur_norm=valeur_norm,
        poids=poids,
        signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        is_gate=is_gate,
        is_na=(valeur_norm is None and not is_gate),
    )


def test_coverage_ponderee_complete():
    """Tous critères couverts → coverage = 1.0."""
    criteres = [_crit(10, 0.1), _crit(5, -0.2), _crit(3, 0.3)]
    assert sa.compute_coverage(criteres) == pytest.approx(1.0)


def test_coverage_ponderee_partielle():
    """Poids 10 manquant sur 18 total → couverture = 8/18 ≈ 0.444."""
    criteres = [_crit(10, None), _crit(5, 0.2), _crit(3, -0.1)]
    cov = sa.compute_coverage(criteres)
    assert cov == pytest.approx(8 / 18)


def test_coverage_pondere_pas_brute():
    """Manquer 1 critère poids 9 doit pénaliser PLUS que manquer 1 poids 2.

    Démontre que le calcul est pondéré (pas en nombre brut)."""
    # Cas A : on rate le poids 2 (sur 11) → coverage = 9/11 ≈ 0.818
    cas_a = [_crit(9, 0.1), _crit(2, None)]
    # Cas B : on rate le poids 9 (sur 11) → coverage = 2/11 ≈ 0.182
    cas_b = [_crit(9, None), _crit(2, 0.1)]
    assert sa.compute_coverage(cas_a) > sa.compute_coverage(cas_b)
    assert sa.compute_coverage(cas_a) == pytest.approx(9 / 11)
    assert sa.compute_coverage(cas_b) == pytest.approx(2 / 11)


def test_coverage_exclut_les_gates():
    """Les critères is_gate (drapeaux) sont exclus du num ET du dénom."""
    # 1 critère normal couvert (poids 5), 1 gate (peu importe valeur_norm)
    criteres = [_crit(5, 0.1), _crit(0, True, is_gate=True)]
    assert sa.compute_coverage(criteres) == pytest.approx(1.0)
    # Ajoute un critère normal non couvert poids 5 → 5/10 = 0.5
    criteres.append(_crit(5, None))
    assert sa.compute_coverage(criteres) == pytest.approx(0.5)


def test_coverage_fiche_vide_retourne_1():
    """Fiche sans critère non-gate → 1.0 (on ne pénalise pas le vide)."""
    assert sa.compute_coverage([]) == pytest.approx(1.0)
    assert sa.compute_coverage([_crit(0, True, is_gate=True)]) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 2. Trois paliers : normale / faible / insuffisant
# ---------------------------------------------------------------------------

def test_palier_normale():
    """coverage ≥ COVERAGE_OK et frais → normale."""
    assert sa.derive_confidence(0.65, is_stale=False) == "normale"
    assert sa.derive_confidence(0.80, is_stale=False) == "normale"
    assert sa.derive_confidence(1.0, is_stale=False) == "normale"


def test_palier_faible():
    """COVERAGE_MIN ≤ coverage < COVERAGE_OK → faible (frais)."""
    assert sa.derive_confidence(0.40, is_stale=False) == "faible"
    assert sa.derive_confidence(0.50, is_stale=False) == "faible"
    assert sa.derive_confidence(0.6499, is_stale=False) == "faible"


def test_palier_insuffisant():
    """coverage < COVERAGE_MIN → insuffisant."""
    assert sa.derive_confidence(0.0, is_stale=False) == "insuffisant"
    assert sa.derive_confidence(0.20, is_stale=False) == "insuffisant"
    assert sa.derive_confidence(0.3999, is_stale=False) == "insuffisant"


def test_palier_perime_plafonne_a_faible():
    """is_stale=True plafonne à faible MÊME si coverage élevé."""
    # Données fraîches → normale ; périmé → faible
    assert sa.derive_confidence(0.90, is_stale=False) == "normale"
    assert sa.derive_confidence(0.90, is_stale=True) == "faible"
    # Mais insuffisant reste prioritaire (absence > vieillesse)
    assert sa.derive_confidence(0.20, is_stale=True) == "insuffisant"


# ---------------------------------------------------------------------------
# 3. Override jamais-neutre : INSUFFISANT prend le pas
# ---------------------------------------------------------------------------

def test_override_jamais_neutre_sous_coverage_min(petrole):
    """Quand coverage < COVERAGE_MIN, conclusion DOIT devenir INSUFFISANT,
    même si la règle jamais-neutre aurait forcé LONG par défaut."""
    # Un seul critère valué : coverage = 5/60 ≈ 0.083 < COVERAGE_MIN
    valeurs = {"brent_term_structure_m1m2": {"valeur": 0.5}}
    r = sa.score_actif("petrole", petrole, valeurs)
    assert r.coverage < sa.COVERAGE_MIN
    for h in sa.HORIZONS:
        assert r.confidence[h] == "insuffisant"
        assert r.conclusions[h] == sa.CONCLUSION_INSUFFISANT
        assert r.conclusions_pond[h] == sa.CONCLUSION_INSUFFISANT
        # tie-break note doit avoir été retirée (plus pertinente)
        assert h not in r.tie_break_notes
        # divergence neutralisée
        assert r.diverge[h] is False


def test_override_ne_sapplique_qu_en_dessous_du_min(petrole):
    """L'override jamais-neutre ne doit s'appliquer QUE sous COVERAGE_MIN.

    Au-dessus (même en confiance faible), la direction LONG/SHORT est conservée
    — c'est explicitement la spec validée par Thomas."""
    # Couverture entre COVERAGE_MIN et COVERAGE_OK → "faible" mais LONG conservé.
    # On vise ~50% : tension(7)+brent(5)+spread(4)+caixin(4)+opec(6)+dxy(5) = 31/60 = 51.6%
    valeurs = {
        "tension_geopol_moyen_orient": {"valeur": 1},
        "brent_term_structure_m1m2": {"valeur": 5.0},
        "spread_brent_wti": {"valeur": 5.0},
        "caixin_pmi_manuf": {"valeur": 52.0},
        "opec_production_policy": {"valeur": 1},
        "dxy_trend_20j": {"valeur_normalisee": 0.5},
    }
    r = sa.score_actif("petrole", petrole, valeurs)
    assert sa.COVERAGE_MIN <= r.coverage < sa.COVERAGE_OK
    for h in sa.HORIZONS:
        assert r.confidence[h] == "faible"
        # Direction conservée — pas d'INSUFFISANT
        assert r.conclusions[h] in ("LONG", "SHORT")


def test_perime_marque_faible_meme_coverage_haut(petrole):
    """Données présentes mais périmées → faible même si coverage = 100%."""
    valeurs = _all_neutral_petrole_valeurs()
    # Force valeur positive pour avoir LONG attendu
    valeurs["brent_term_structure_m1m2"] = {"valeur": 5.0}
    r = sa.score_actif("petrole", petrole, valeurs, is_stale=True)
    assert r.coverage >= sa.COVERAGE_OK  # couverture haute
    for h in sa.HORIZONS:
        # Plafonné à "faible" à cause du flag stale
        assert r.confidence[h] == "faible"
        # Direction conservée
        assert r.conclusions[h] in ("LONG", "SHORT")


# ---------------------------------------------------------------------------
# 4. Affichage bulletin 🚫 et ⚠️
# ---------------------------------------------------------------------------

def _render(results):
    return sa.render_bulletin(
        results,
        veille_conclusions={},
        now=datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc),
        fiches_h="testhash",
        freshness_msg="ok",
    )


def test_bulletin_affiche_emoji_insuffisant(petrole):
    """Cellule INSUFFISANT → '🚫 données insuff. (X%)' dans la matrice."""
    valeurs = {"brent_term_structure_m1m2": {"valeur": 0.5}}  # coverage < MIN
    r = sa.score_actif("petrole", petrole, valeurs)
    txt = _render([r])
    assert "🚫 données insuff." in txt
    # Légende compacte : 🚫 listé (uniquement les symboles présents)
    assert "🚫" in txt and "données insuffisantes" in txt
    # Plus de LONG/SHORT sur cette cellule (table de synthèse fusionnée)
    matrix_section = txt.split("## Synthèse des décisions")[1].split("## Détail")[0]
    petrole_line = [
        line for line in matrix_section.splitlines()
        if "Pétrole" in line and "|" in line
    ]
    assert petrole_line, "ligne pétrole introuvable"
    assert "LONG" not in petrole_line[0] and "SHORT" not in petrole_line[0]


def test_bulletin_affiche_emoji_confiance_faible(petrole):
    """Cellule confiance faible → suffixe '⚠️ conf. faible (X%)'."""
    # Couverture ~50% → faible
    valeurs = {
        "tension_geopol_moyen_orient": {"valeur": 1},
        "brent_term_structure_m1m2": {"valeur": 5.0},
        "spread_brent_wti": {"valeur": 5.0},
        "caixin_pmi_manuf": {"valeur": 52.0},
        "opec_production_policy": {"valeur": 1},
        "dxy_trend_20j": {"valeur_normalisee": 0.5},
    }
    r = sa.score_actif("petrole", petrole, valeurs)
    assert all(r.confidence[h] == "faible" for h in sa.HORIZONS)
    txt = _render([r])
    assert "⚠️ conf. faible" in txt
    # Direction toujours visible
    assert "LONG" in txt or "SHORT" in txt
    assert "🚫 données insuff." not in txt


def test_bulletin_aucun_marqueur_si_confiance_normale(petrole):
    """Cellule normale → ni 🚫 ni '⚠️ conf. faible'."""
    valeurs = _all_neutral_petrole_valeurs()
    valeurs["brent_term_structure_m1m2"] = {"valeur": 5.0}
    r = sa.score_actif("petrole", petrole, valeurs)
    assert all(r.confidence[h] == "normale" for h in sa.HORIZONS)
    txt = _render([r])
    # La cellule petrole spécifiquement ne porte pas les marqueurs
    matrix_section = txt.split("## Synthèse des décisions")[1].split("## Détail")[0]
    petrole_line = [
        line for line in matrix_section.splitlines()
        if "Pétrole" in line and "|" in line
    ][0]
    assert "🚫" not in petrole_line
    assert "⚠️ conf. faible" not in petrole_line


# ---------------------------------------------------------------------------
# 5. Decision-log : champs coverage & confidence par cellule
# ---------------------------------------------------------------------------

def test_decision_log_contient_coverage_et_confidence(petrole):
    valeurs = _all_neutral_petrole_valeurs()
    valeurs["brent_term_structure_m1m2"] = {"valeur": 5.0}
    r = sa.score_actif("petrole", petrole, valeurs)
    records = sa.build_decision_log_records(
        [r], now=datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc)
    )
    assert len(records) == 3  # 1 actif × 3 horizons
    for rec in records:
        assert "coverage" in rec
        assert "confidence" in rec
        assert 0.0 <= rec["coverage"] <= 1.0
        assert rec["confidence"] in ("normale", "faible", "insuffisant")
        # coverage doit être identique pour tous les horizons d'un actif
        assert rec["coverage"] == pytest.approx(r.coverage, abs=1e-3)


# ---------------------------------------------------------------------------
# 6. Journaliste : exclusion VRAI/FAUX et biais
# ---------------------------------------------------------------------------

def test_journaliste_cellule_insuffisant_outcome_non_note(petrole):
    """measure_cell sur une cellule INSUFFISANT → outcome = OUTCOME_NON_NOTE,
    pas de calcul de delta, pas comptée comme VRAI/FAUSSE."""
    cell = jo.BulletinCell(
        bulletin_date=date(2026, 6, 1),
        actif_name="Pétrole (Brent)",
        horizon="7j",
        conclusion=jo.CONCLUSION_INSUFFISANT,
        score=0.0,
    )
    m = jo.measure_cell(
        cell=cell,
        fiche_key="petrole",
        fiche=petrole,
        prix_emission=100.0,
        prix_courant=110.0,  # +10% : aurait été VRAI si LONG
    )
    assert m.outcome == jo.OUTCOME_NON_NOTE
    # Aucun delta calculé → la cellule n'est pas comptée comme prédiction
    assert m.delta_pct is None


def test_journaliste_kpi_exclut_insuffisant_du_vrai_faux(petrole):
    """Un mix de mesures (1 VRAI + 1 INSUFFISANT) doit donner n_vrai=1,
    n_total=1 (INSUFFISANT exclue), pas n_total=2."""
    cell_long = jo.BulletinCell(
        bulletin_date=date(2026, 5, 28),
        actif_name="Pétrole (Brent)",
        horizon="7j",
        conclusion="LONG",
        score=0.5,
    )
    cell_insuf = jo.BulletinCell(
        bulletin_date=date(2026, 5, 29),
        actif_name="Pétrole (Brent)",
        horizon="7j",
        conclusion=jo.CONCLUSION_INSUFFISANT,
        score=0.0,
    )
    m_vrai = jo.measure_cell(cell_long, "petrole", petrole, 100.0, 110.0)
    assert m_vrai.outcome == jo.OUTCOME_VRAI
    m_ins = jo.measure_cell(cell_insuf, "petrole", petrole, 100.0, 110.0)
    assert m_ins.outcome == jo.OUTCOME_NON_NOTE

    kpi = jo.compute_kpi([m_vrai, m_ins])
    # INSUFFISANT exclue : n_total=1, n_vrai=1, n_long=1 (LONG seul)
    assert kpi.n_total == 1
    assert kpi.n_vrai == 1
    assert kpi.n_long == 1
    assert kpi.n_short == 0


def test_journaliste_kpi_exclut_insuffisant_du_biais_long_short(petrole):
    """Une cellule INSUFFISANT ne doit PAS gonfler la distribution LONG/SHORT
    (sinon on biaise le calcul de biais)."""
    # 1 LONG + 1 INSUFFISANT → distrib LONG = 100%, pas 50%
    cell_long = jo.BulletinCell(
        bulletin_date=date(2026, 5, 28),
        actif_name="Pétrole (Brent)",
        horizon="7j",
        conclusion="LONG",
        score=0.5,
    )
    cell_insuf = jo.BulletinCell(
        bulletin_date=date(2026, 5, 29),
        actif_name="Pétrole (Brent)",
        horizon="7j",
        conclusion=jo.CONCLUSION_INSUFFISANT,
        score=0.0,
    )
    m_long = jo.measure_cell(cell_long, "petrole", petrole, 100.0, 110.0)
    m_ins = jo.measure_cell(cell_insuf, "petrole", petrole, 100.0, 110.0)
    kpi = jo.compute_kpi([m_long, m_ins])
    # Le seul vote pris en compte est LONG → distrib LONG = 100%
    assert kpi.distrib_long_pct == 100.0
    assert kpi.distrib_short_pct == 0.0


def test_journaliste_parse_bulletin_capte_cellules_insuffisant(tmp_path):
    """Le parser doit reconnaître les cellules INSUFFISANT (pour pouvoir
    les tracer comme non-notées), sans perdre les autres cellules de la ligne."""
    bulletin = tmp_path / "bulletin-2026-06-01.md"
    bulletin.write_text(
        "# Bulletin\n\n"
        "## Matrice\n\n"
        "| Actif | 24h | 7j | 1m |\n"
        "|---|---|---|---|\n"
        "| Pétrole (Brent) | LONG (+0.42) | 🚫 données insuff. (35%) | SHORT (-0.20) |\n",
        encoding="utf-8",
    )
    cells = jo.parse_bulletin(bulletin)
    # 3 cellules malgré l'INSUFFISANT au milieu
    assert len(cells) == 3
    by_h = {c.horizon: c for c in cells}
    assert by_h["24h"].conclusion == "LONG"
    assert by_h["24h"].score == pytest.approx(0.42)
    assert by_h["7j"].conclusion == jo.CONCLUSION_INSUFFISANT
    assert by_h["7j"].score == 0.0
    assert by_h["1m"].conclusion == "SHORT"
    assert by_h["1m"].score == pytest.approx(-0.20)
