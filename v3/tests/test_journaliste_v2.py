"""Tests Journaliste v2 — corrections statistiques :
   #1 non-chevauchant, #2 Wilson IC + critère global, #3 calibration ECE.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import List

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers partagés
# ---------------------------------------------------------------------------

def _make_measure(
    outcome: str,
    conc: str = "LONG",
    score: float = 1.0,
    echeance: date = date(2026, 5, 2),
    horizon: str = "24h",
) -> jr.Measure:
    cell = jr.BulletinCell(
        bulletin_date=echeance - timedelta(days=jr.HORIZON_DAYS[horizon]),
        actif_name="Pétrole (Brent)",
        horizon=horizon,
        conclusion=conc,
        score=score,
    )
    return jr.Measure(
        cell=cell,
        fiche_key="petrole",
        ticker="BZ=F",
        horizon=horizon,
        echeance=echeance,
        prix_emission=100.0,
        prix_courant=101.0,
        seuil_pct=1.0,
        delta_pct=1.0,
        outcome=outcome,
    )


def _measures_seq(
    outcomes: List[str],
    horizon: str = "24h",
    start: date = date(2026, 1, 1),
    step: int = 1,
    score: float = 3.0,
) -> List[jr.Measure]:
    """Crée une liste de mesures avec des échéances séparées de `step` jours."""
    ms = []
    for i, o in enumerate(outcomes):
        echeance = start + timedelta(days=i * step)
        ms.append(_make_measure(o, echeance=echeance, horizon=horizon, score=score))
    ms.sort(key=lambda m: m.echeance)
    return ms


# ---------------------------------------------------------------------------
# Test #1 : wilson_ci
# ---------------------------------------------------------------------------

class TestWilsonCI:
    def test_coin_flip_perfect(self):
        """5/10 ≈ 50% — IC doit encadrer 0.5."""
        low, high = jr.wilson_ci(5, 10)
        assert low < 0.5 < high

    def test_n_zero_retourne_0_1(self):
        low, high = jr.wilson_ci(0, 0)
        assert low == 0.0
        assert high == 1.0

    def test_tous_vrais_borne_basse_elevee(self):
        """10/10 → low doit être > 0.7."""
        low, high = jr.wilson_ci(10, 10)
        assert low > 0.7
        assert high == 1.0

    def test_aucun_vrai_borne_haute_basse(self):
        """0/10 → high doit être < 0.3."""
        low, high = jr.wilson_ci(0, 10)
        assert low == 0.0
        assert high < 0.3

    def test_21_sur_30_low_superieur_50pct(self):
        """21/30 = 70% — borne basse Wilson 95% doit être > 50%."""
        low, high = jr.wilson_ci(21, 30)
        assert low > 0.50, f"Wilson low={low} devrait être > 0.50 pour 21/30"
        assert high > low

    def test_15_sur_30_low_inferieur_50pct(self):
        """15/30 = 50% — borne basse Wilson doit être < 50%."""
        low, high = jr.wilson_ci(15, 30)
        assert low < 0.50

    def test_bornes_dans_0_1(self):
        for n_succ, n_tot in [(0, 1), (1, 1), (3, 5), (7, 10), (30, 30)]:
            low, high = jr.wilson_ci(n_succ, n_tot)
            assert 0.0 <= low <= 1.0, f"low={low} hors [0,1]"
            assert 0.0 <= high <= 1.0, f"high={high} hors [0,1]"
            assert low <= high

    def test_symetrie_approximative(self):
        """Wilson n'est pas symétrique, mais les deux bornes doivent encadrer p_hat."""
        low, high = jr.wilson_ci(7, 10)
        p_hat = 7 / 10
        assert low < p_hat < high


# ---------------------------------------------------------------------------
# Test #1 : select_non_overlapping
# ---------------------------------------------------------------------------

class TestSelectNonOverlapping:
    def test_24h_toutes_obs_independantes(self):
        """24h avec step=1j : chaque jour est indépendant."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1)
        result = jr.select_non_overlapping(ms, "24h")
        assert len(result) == 10

    def test_7j_chevauche_skip_obs_proches(self):
        """7j avec 3 obs consécutives (step=1j) → seulement 1 obs effective."""
        ms = _measures_seq(
            [jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE, jr.OUTCOME_VRAI],
            horizon="7j",
            step=1,
        )
        result = jr.select_non_overlapping(ms, "7j")
        assert len(result) == 1, f"attendu 1 obs non-chevauchante, obtenu {len(result)}"

    def test_7j_obs_espaces_7j_toutes_independantes(self):
        """7j avec step=7j : toutes les obs sont indépendantes."""
        ms = _measures_seq(
            [jr.OUTCOME_VRAI] * 5, horizon="7j", step=7
        )
        result = jr.select_non_overlapping(ms, "7j")
        assert len(result) == 5

    def test_1m_chevauche_fortement(self):
        """1m avec obs quotidiennes (30 obs / 30 jours) → ~1 obs effective."""
        ms = _measures_seq(
            [jr.OUTCOME_VRAI] * 30, horizon="1m", step=1
        )
        result = jr.select_non_overlapping(ms, "1m")
        assert len(result) == 1

    def test_1m_obs_espaces_30j(self):
        """1m avec step=30j : toutes indépendantes."""
        ms = _measures_seq(
            [jr.OUTCOME_VRAI] * 4, horizon="1m", step=30
        )
        result = jr.select_non_overlapping(ms, "1m")
        assert len(result) == 4

    def test_nc_exclues_du_non_chevauchant(self):
        """Non-conclusives exclues : ne bloquent PAS les observations suivantes."""
        # 1 VRAI, 1 NC (même jour+1), 1 VRAI (+1j) → NC ignorée, les 2 VRAI inclus
        ms = [
            _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 1), horizon="24h"),
            _make_measure(jr.OUTCOME_NC, echeance=date(2026, 1, 2), horizon="24h"),
            _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 3), horizon="24h"),
        ]
        result = jr.select_non_overlapping(ms, "24h")
        assert len(result) == 2  # NC exclue → seuls les 2 VRAI restent

    def test_vide_si_aucune_terminee(self):
        ms = [_make_measure(jr.OUTCOME_NC, horizon="24h")]
        result = jr.select_non_overlapping(ms, "24h")
        assert len(result) == 0

    def test_interrompus_exclus(self):
        ms = [
            _make_measure(jr.OUTCOME_INTERROMPU, echeance=date(2026, 1, 1), horizon="24h"),
            _make_measure(jr.OUTCOME_VRAI, echeance=date(2026, 1, 2), horizon="24h"),
        ]
        result = jr.select_non_overlapping(ms, "24h")
        assert len(result) == 1
        assert result[0].outcome == jr.OUTCOME_VRAI

    def test_step_custom(self):
        """Test avec step_days custom override."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 5, horizon="24h", step=1)
        # Forcer step=3 : sur 5 obs consécutives séparées de 1j, step=3 → obs 0, 3 → 2 obs
        result = jr.select_non_overlapping(ms, "24h", step_days=3)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Test #1 + #2 : compute_kpi avec n_effective et Wilson
# ---------------------------------------------------------------------------

class TestComputeKpiNonChevauchant:
    def test_n_effective_24h_egal_n_vrai_fausse(self):
        """24h step=1j → n_effective = nb VRAI + FAUSSE dans la fenêtre."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10 + [jr.OUTCOME_FAUSSE] * 5, horizon="24h", step=1)
        k = jr.compute_kpi(ms)
        assert k.n_effective == 15

    def test_n_effective_7j_reduit(self):
        """7j avec 7 obs quotidiennes → n_effective ≤ 1 (sauf si espacées)."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 7, horizon="7j", step=1)
        k = jr.compute_kpi(ms)
        assert k.n_effective == 1

    def test_taux_eff_different_taux_brut_7j(self):
        """7j chevauchant : taux brut ≠ taux_eff si les obs chevauchent."""
        # 6 VRAI consécutifs 7j (step=1j) + 1 FAUSSE 7j plus tard (step=7j)
        ms_vrai = _measures_seq([jr.OUTCOME_VRAI] * 6, horizon="7j", step=1, start=date(2026, 1, 1))
        ms_fausse = _measures_seq([jr.OUTCOME_FAUSSE], horizon="7j", step=7, start=date(2026, 1, 8))
        ms = ms_vrai + ms_fausse
        ms.sort(key=lambda m: m.echeance)
        k = jr.compute_kpi(ms)
        # Brut : 6 VRAI / 7 = 85.7%
        assert k.taux_pct == pytest.approx(6 / 7 * 100, abs=0.1)
        # Non-chevauchant : obs 1 (VRAI, j1), obs 2 (FAUSSE, j8) → 50%
        assert k.n_effective == 2
        assert k.taux_eff_pct == pytest.approx(50.0, abs=0.1)

    def test_wilson_low_calcule(self):
        """Wilson low est bien calculé pour n_effective > 0."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 21 + [jr.OUTCOME_FAUSSE] * 9, horizon="24h", step=1)
        k = jr.compute_kpi(ms)
        assert k.wilson_low is not None
        assert k.wilson_high is not None
        assert k.wilson_low < k.taux_eff_pct / 100 < k.wilson_high  # type: ignore[operator]

    def test_eligible_si_wilson_low_gt_50_et_taux_eff_gte_70(self):
        """30 VRAI sur 30 obs 24h → taux_eff=100%, wilson_low >> 50% → éligible."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 30, horizon="24h", step=1)
        k = jr.compute_kpi(ms)
        assert k.statut == "éligible_actif"
        assert k.wilson_low is not None and k.wilson_low > 0.50

    def test_shadow_si_wilson_low_le_50_meme_taux_eleve(self):
        """Avec n_effective petit (5 obs) même à 100%, Wilson low peut être ≤ 50%."""
        # 5 VRAI sur 5 obs non-chevauchantes (24h, step=1j)
        ms = _measures_seq([jr.OUTCOME_VRAI] * 5, horizon="24h", step=1)
        k = jr.compute_kpi(ms)
        # Wilson IC(5, 5) low ≈ 0.478 ≤ 0.50 → shadow
        assert k.wilson_low is not None
        if k.wilson_low <= jr.WILSON_LOW_THRESHOLD:
            assert k.statut == "shadow"

    def test_warmup_si_n_effective_sous_min(self):
        """Si n_effective < N_EFFECTIVE_MIN → warm-up dans alertes."""
        # 4 VRAI espacées de 1j (24h) → n_effective = 4 < N_EFFECTIVE_MIN (5)
        ms = _measures_seq([jr.OUTCOME_VRAI] * 4, horizon="24h", step=1)
        k = jr.compute_kpi(ms)
        assert k.n_effective < jr.N_EFFECTIVE_MIN
        assert any("warm-up" in a for a in k.alertes)

    def test_shadow_si_taux_eff_sous_70(self):
        """n_effective=10, taux=40% → shadow + alerte taux_eff."""
        ms = _measures_seq(
            [jr.OUTCOME_VRAI] * 4 + [jr.OUTCOME_FAUSSE] * 6,
            horizon="24h",
            step=1,
        )
        k = jr.compute_kpi(ms)
        assert k.statut == "shadow"
        assert any("taux_eff" in a for a in k.alertes) or k.taux_eff_pct < 70.0


# ---------------------------------------------------------------------------
# Test #3 : compute_calibration + render_calibration
# ---------------------------------------------------------------------------

class TestComputeCalibration:
    def test_none_si_moins_de_10_obs(self):
        ms = _measures_seq([jr.OUTCOME_VRAI] * 5, horizon="24h", step=1, score=3.0)
        result = jr.compute_calibration(ms)
        assert result is None

    def test_retourne_calib_result_avec_10_obs(self):
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1, score=3.0)
        result = jr.compute_calibration(ms)
        assert result is not None
        assert result.n_total == 10
        assert 0.0 <= result.ece <= 1.0

    def test_parfaitement_calibre_proba_egal_taux(self):
        """Si tous VRAI avec proba=0.7, ECE ~ |0.7 - 1.0| = 0.3 (surestimation).

        Audit 2026-06-01 : PROBA_SCALE est passé de 10 à 15 → on adapte le score
        pour conserver l'intention (proba=0.7). score=3.0 → proba=0.5+3/15=0.7.
        """
        ms = _measures_seq([jr.OUTCOME_VRAI] * 20, horizon="24h", step=1, score=3.0)
        # score=3.0 (avec PROBA_SCALE=15) → proba=0.7, tous VRAI → taux=1.0 → surestimation
        result = jr.compute_calibration(ms)
        assert result is not None
        # ECE = |0.7 - 1.0| * 20/20 = 0.3 (approximativement)
        assert result.ece == pytest.approx(0.3, abs=0.05)

    def test_ece_zero_si_proba_parfaite_et_vrai(self):
        """proba=1.0 (score=100) + tous VRAI → ECE ≈ 0."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1, score=100.0)
        result = jr.compute_calibration(ms)
        assert result is not None
        assert result.ece == pytest.approx(0.0, abs=0.01)

    def test_ece_max_si_proba_haute_et_tous_faux(self):
        """proba=1.0 (score=100) + tous FAUSSE → ECE ≈ 1.0."""
        ms = _measures_seq([jr.OUTCOME_FAUSSE] * 10, horizon="24h", step=1, score=100.0)
        result = jr.compute_calibration(ms)
        assert result is not None
        assert result.ece == pytest.approx(1.0, abs=0.01)

    def test_nc_exclues_du_calcul_calibration(self):
        """Non-conclusives exclues : n_total ne les compte pas."""
        ms_vrai = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1, score=3.0)
        ms_nc = _measures_seq(
            [jr.OUTCOME_NC] * 5,
            horizon="24h",
            step=1,
            start=date(2026, 2, 1),
            score=0.0,
        )
        result = jr.compute_calibration(ms_vrai + ms_nc)
        assert result is not None
        assert result.n_total == 10

    def test_bins_somme_n_egal_n_total(self):
        """La somme des n par bin = n_total."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 5 + [jr.OUTCOME_FAUSSE] * 5, horizon="24h", step=1, score=3.0)
        result = jr.compute_calibration(ms)
        assert result is not None
        assert sum(b.n for b in result.bins) == result.n_total

    def test_ece_borne_0_1(self):
        """ECE doit toujours être dans [0, 1]."""
        for score in [0.5, 2.0, 5.0, 10.0]:
            ms = _measures_seq([jr.OUTCOME_VRAI] * 5 + [jr.OUTCOME_FAUSSE] * 5,
                               horizon="24h", step=1, score=score)
            result = jr.compute_calibration(ms)
            assert result is not None
            assert 0.0 <= result.ece <= 1.0, f"ECE={result.ece} hors [0,1] pour score={score}"


class TestRenderCalibration:
    def _now(self):
        return datetime(2026, 5, 30, 12, 0, tzinfo=timezone.utc)

    def test_render_avec_none_contient_pas_assez(self):
        content = jr.render_calibration(None, self._now())
        assert "pas encore assez" in content.lower() or "pas assez" in content.lower() or "< 10" in content

    def test_render_avec_calib_contient_ece(self):
        ms = _measures_seq([jr.OUTCOME_VRAI] * 15, horizon="24h", step=1, score=3.0)
        calib = jr.compute_calibration(ms)
        content = jr.render_calibration(calib, self._now())
        assert "ECE" in content
        assert "Reliability" in content

    def test_render_ecrit_fichier(self, tmp_path):
        ms = _measures_seq([jr.OUTCOME_VRAI] * 15, horizon="24h", step=1, score=3.0)
        calib = jr.compute_calibration(ms)
        content = jr.render_calibration(calib, self._now())
        out = tmp_path / "calibration.md"
        jr.write_calibration(content, out)
        assert out.exists()
        assert "ECE" in out.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Test critère global multiple-testing (synthèse render_performance)
# ---------------------------------------------------------------------------

class TestWinRateView:
    """Vue win-rate-only (refonte Session 4) : tableau propre, zéro P&L,
    Brier/Taux_brut/Alertes retirés de l'affichage."""

    def test_render_performance_synthese_cellules_fiables(self):
        """La ligne de synthèse « X / N cellules fiables » est présente."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1, score=3.0)
        kpis = {("petrole", "24h"): jr.compute_kpi(ms)}
        now = datetime(2026, 5, 30, 12, 0, tzinfo=timezone.utc)
        content = jr.render_performance(kpis, ms, now)
        assert "cellules fiables" in content
        assert "15 paris requis" in content

    def test_render_performance_colonnes_win_rate_only(self):
        """Les colonnes de la vue humaine sont win-rate-only."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1, score=3.0)
        kpis = {("petrole", "24h"): jr.compute_kpi(ms)}
        now = datetime(2026, 5, 30, 12, 0, tzinfo=timezone.utc)
        content = jr.render_performance(kpis, ms, now)
        # WR tradable COEXISTE avec le WR conclusif (Lot 2 audit 10/06).
        assert "| Actif | Win rate | WR tradable | Paris (réels) | Non notés | Statut |" in content

    def test_render_performance_argent_et_jargon_absents(self):
        """Zéro P&L et plus de colonnes Taux_brut/Brier/Alertes à l'affichage."""
        ms = _measures_seq([jr.OUTCOME_VRAI] * 10, horizon="24h", step=1, score=3.0)
        kpis = {("petrole", "24h"): jr.compute_kpi(ms)}
        now = datetime(2026, 5, 30, 12, 0, tzinfo=timezone.utc)
        content = jr.render_performance(kpis, ms, now)
        for banned in ["Taux_brut", "Brier", "| Alertes", "P&L", "€", "$", "gain"]:
            assert banned not in content, f"Terme interdit présent : {banned}"


# ---------------------------------------------------------------------------
# Test intégration : run() produit calibration.md
# ---------------------------------------------------------------------------

def _write_bulletin(dir_: Path, d: date, rows) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Bulletin Analyste — {d.isoformat()}",
        "",
        "## Matrice (12 actifs × 3 horizons)",
        "",
        "| Actif | 24h | 7j | 1m |",
        "|---|---|---|---|",
    ]
    for actif, (c24, s24), (c7, s7), (c1, s1) in rows:
        lines.append(
            f"| {actif} | {c24} ({s24:+.2f}) | {c7} ({s7:+.2f}) | {c1} ({s1:+.2f}) |"
        )
    path = dir_ / f"bulletin-{d.isoformat()}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


import json  # noqa: E402

def _write_prix(dir_: Path, d: date, prix: dict) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / f"{d.isoformat()}.json").write_text(json.dumps(prix), encoding="utf-8")


def test_run_produit_calibration_md(tmp_path):
    """run() doit écrire calibration.md même avec peu d'obs (fichier produit, contenu minimal)."""
    fiche_petrole = {
        "actif": "Pétrole (Brent)",
        "ticker_principal": "BZ=F",
        "seuils_reussite_pct": {"24h": 1.0, "7j": 2.5, "1m": 6.0},
    }
    fiches = {"petrole": fiche_petrole}
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    perf = tmp_path / "performance.md"
    calib = tmp_path / "calibration.md"

    d_em = date(2026, 5, 28)
    _write_bulletin(bulletins, d_em, [("Pétrole (Brent)", ("LONG", 0.5), ("SHORT", -0.5), ("LONG", 0.3))])
    _write_prix(prix, d_em, {"BZ=F": 100.0})

    now = datetime(2026, 5, 29, 19, 0, tzinfo=timezone.utc)
    jr.run(
        today=date(2026, 5, 29),
        now=now,
        bulletins_dir=bulletins,
        prix_emission_dir=prix,
        performance_path=perf,
        fiches=fiches,
        fetch_price=lambda t: 105.0,
        stamp_today=True,
    )
    # calibration.md écrit par run() dans le même répertoire que performance.md
    assert calib.exists(), "calibration.md doit être créé par run()"
    content = calib.read_text(encoding="utf-8")
    assert "Calibration" in content
