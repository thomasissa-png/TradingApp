"""Tests C5 — Intégrité de la mesure (gates-FINAL.md).

Trois garde-fous incorruptibles dans `journaliste.py` :

1. Entry-lock prix d'émission : immuable une fois stampé.
2. Échéance figée : echeance = bulletin_date + HORIZON_DAYS[h], assertion
   echeance > bulletin_date.
3. Zéro look-ahead : refus de mesurer si prix « courant » antérieur à
   l'émission OU si l'on est avant l'échéance.

Aucun de ces gardes ne doit modifier le scoring : ils REFUSENT de mesurer
les cas corrompus (outcome OUTCOME_INTERROMPU + log ERROR), jamais
VRAI/FAUSSE inventé.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures (mirrorent test_journaliste.py pour rester cohérent)
# ---------------------------------------------------------------------------

@pytest.fixture
def fiche_petrole():
    return {
        "actif": "Pétrole (Brent)",
        "ticker_principal": "BZ=F",
        "seuils_reussite_pct": {"24h": 1.0, "7j": 2.5, "1m": 6.0},
    }


def _cell(
    conc: str,
    horizon: str,
    score: float = 0.5,
    bdate: date = date(2026, 5, 1),
    actif: str = "Pétrole (Brent)",
) -> jr.BulletinCell:
    return jr.BulletinCell(
        bulletin_date=bdate,
        actif_name=actif,
        horizon=horizon,
        conclusion=conc,
        score=score,
    )


# ===========================================================================
# C5 invariant #1 — Entry-lock prix d'émission (immuabilité)
# ===========================================================================

class TestC5EntryLockImmuable:
    """Une fois écrit pour (actif, date), le prix d'émission est immuable.

    Garde-fou : un tick ultérieur (même plus favorable) ne doit JAMAIS
    écraser la valeur existante. Vérifié via deux niveaux :
      - helper pur `_enforce_entry_lock` (logique)
      - intégration `stamp_prix_emission` (idempotence sur disque)
    """

    def test_helper_preserve_ancien_meme_si_proposed_different(self, caplog):
        existing = {"BZ=F": 100.0}
        with caplog.at_level(logging.WARNING, logger="journaliste"):
            kept = jr._enforce_entry_lock(
                existing, "BZ=F", proposed_price=120.0,
                bulletin_date=date(2026, 5, 1),
            )
        assert kept == 100.0, "le prix d'origine doit être conservé"
        # Log de tentative d'écrasement
        assert any(
            "entry-lock violé" in rec.message
            for rec in caplog.records
        ), "tentative d'écrasement doit être loggée"

    def test_helper_premier_stamp_retourne_proposed(self):
        existing = {}
        kept = jr._enforce_entry_lock(
            existing, "BZ=F", proposed_price=100.0,
            bulletin_date=date(2026, 5, 1),
        )
        assert kept == 100.0

    def test_helper_meme_valeur_pas_de_warning(self, caplog):
        existing = {"BZ=F": 100.0}
        with caplog.at_level(logging.WARNING, logger="journaliste"):
            kept = jr._enforce_entry_lock(
                existing, "BZ=F", proposed_price=100.0,
                bulletin_date=date(2026, 5, 1),
            )
        assert kept == 100.0
        assert not any(
            "entry-lock violé" in rec.message
            for rec in caplog.records
        )

    def test_stamp_prix_emission_idempotent_ne_reecrase_pas(
        self, tmp_path, fiche_petrole, caplog,
    ):
        """Deuxième stamp avec un fetch « plus favorable » → ancien préservé + log."""
        bdate = date(2026, 5, 1)
        fiches = {"petrole": fiche_petrole}

        # 1er stamp
        jr.stamp_prix_emission(
            bdate, fiches=fiches,
            fetch_price=lambda t: 100.0,
            base_dir=tmp_path,
        )
        p1 = json.loads((tmp_path / f"{bdate.isoformat()}.json").read_text())
        assert p1["BZ=F"] == 100.0

        # 2e stamp avec fetch retournant 200 (tentative d'écrasement)
        with caplog.at_level(logging.WARNING, logger="journaliste"):
            jr.stamp_prix_emission(
                bdate, fiches=fiches,
                fetch_price=lambda t: 200.0,
                base_dir=tmp_path,
            )
        p2 = json.loads((tmp_path / f"{bdate.isoformat()}.json").read_text())
        assert p2["BZ=F"] == 100.0, "entry-lock : ancien prix immuable"

    def test_stamp_prix_emission_ne_refetch_pas_ticker_deja_stampe(
        self, tmp_path, fiche_petrole,
    ):
        """Un ticker déjà stampé ne doit même pas déclencher de fetch (idempotence stricte)."""
        bdate = date(2026, 5, 1)
        fiches = {"petrole": fiche_petrole}
        jr.stamp_prix_emission(
            bdate, fiches=fiches,
            fetch_price=lambda t: 100.0,
            base_dir=tmp_path,
        )

        calls = []

        def _fetch(t):
            calls.append(t)
            return 200.0

        jr.stamp_prix_emission(
            bdate, fiches=fiches,
            fetch_price=_fetch,
            base_dir=tmp_path,
        )
        assert calls == [], (
            "ticker déjà stampé : aucun refetch attendu (entry-lock économise un appel)"
        )


# ===========================================================================
# C5 invariant #2 — Échéance figée déterministe
# ===========================================================================

class TestC5EcheanceFigee:
    """echeance = bulletin_date + HORIZON_DAYS[h], invariant strict."""

    @pytest.mark.parametrize(
        "horizon,delta_days",
        [("24h", 1), ("7j", 7), ("1m", 30)],
    )
    def test_compute_echeance_pour_chaque_horizon(self, horizon, delta_days):
        bdate = date(2026, 5, 1)
        ech = jr.compute_echeance(bdate, horizon)
        # Doit utiliser EXACTEMENT la constante existante (pas de redéfinition)
        assert (ech - bdate).days == delta_days
        assert (ech - bdate).days == jr.HORIZON_DAYS[horizon]

    def test_compute_echeance_invariant_strict_superieur(self):
        """L'assertion echeance > bulletin_date doit être vraie pour tout horizon connu."""
        bdate = date(2026, 5, 1)
        for h in jr.HORIZONS:
            ech = jr.compute_echeance(bdate, h)
            assert ech > bdate, (
                f"invariant violé pour horizon={h} : echeance={ech} "
                f"<= bulletin_date={bdate}"
            )

    def test_compute_echeance_horizon_inconnu_refuse(self):
        """Refuser de fabriquer une échéance pour un horizon non listé."""
        with pytest.raises(KeyError):
            jr.compute_echeance(date(2026, 5, 1), "42j")

    def test_measure_cell_utilise_compute_echeance(self, fiche_petrole):
        """measure_cell DOIT calculer l'échéance via compute_echeance (cohérence)."""
        c = _cell("LONG", "7j", bdate=date(2026, 5, 1))
        m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 102.0)
        assert m.echeance == jr.compute_echeance(date(2026, 5, 1), "7j")
        assert m.echeance == date(2026, 5, 8)

    def test_measure_cell_echeance_24h(self, fiche_petrole):
        c = _cell("LONG", "24h", bdate=date(2026, 5, 1))
        m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 102.0)
        assert m.echeance == date(2026, 5, 2)

    def test_measure_cell_echeance_1m(self, fiche_petrole):
        c = _cell("LONG", "1m", bdate=date(2026, 5, 1))
        m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 110.0)
        assert m.echeance == date(2026, 5, 31)


# ===========================================================================
# C5 invariant #3 — Zéro look-ahead
# ===========================================================================

class TestC5ZeroLookAhead:
    """Refuser toute mesure dont le prix « courant » serait connu d'avance,
    ou prononcée avant l'échéance. Outcome → OUTCOME_INTERROMPU, jamais
    VRAI/FAUSSE.
    """

    def test_prix_courant_anterieur_emission_refuse(
        self, fiche_petrole, caplog,
    ):
        """Si prix_courant_date < bulletin_date → REFUS (bug TZ/cache/DST)."""
        c = _cell("LONG", "24h", bdate=date(2026, 5, 10))
        with caplog.at_level(logging.ERROR, logger="journaliste"):
            m = jr.measure_cell(
                c, "petrole", fiche_petrole,
                prix_emission=100.0, prix_courant=120.0,
                prix_courant_date=date(2026, 5, 9),  # AVANT émission → look-ahead
            )
        assert m.outcome == jr.OUTCOME_INTERROMPU, (
            "look-ahead : surtout PAS VRAI/FAUSSE"
        )
        assert m.outcome not in (jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE)
        assert "look-ahead" in m.note.lower()
        assert any(
            "look-ahead REFUS" in rec.message
            for rec in caplog.records
        ), "violation look-ahead doit être loggée en ERROR"

    def test_prix_courant_date_egale_emission_accepte(self, fiche_petrole):
        """Date égale à l'émission (cas limite, pas look-ahead) → mesure normale."""
        c = _cell("LONG", "24h", bdate=date(2026, 5, 10))
        m = jr.measure_cell(
            c, "petrole", fiche_petrole,
            prix_emission=100.0, prix_courant=102.0,
            prix_courant_date=date(2026, 5, 10),  # = émission → OK
            today=date(2026, 5, 11),  # après échéance
        )
        # +2 % > seuil 1 % et LONG → VRAI (mesure normale, garde n'a pas bloqué)
        assert m.outcome == jr.OUTCOME_VRAI

    def test_mesure_prematuree_refusee(self, fiche_petrole, caplog):
        """today < echeance → REFUS (horizon pas écoulé)."""
        c = _cell("LONG", "7j", bdate=date(2026, 5, 10))
        with caplog.at_level(logging.ERROR, logger="journaliste"):
            m = jr.measure_cell(
                c, "petrole", fiche_petrole,
                prix_emission=100.0, prix_courant=120.0,
                today=date(2026, 5, 12),  # echeance = 2026-05-17, today AVANT
            )
        assert m.outcome == jr.OUTCOME_INTERROMPU
        assert m.outcome not in (jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE)
        assert "prématur" in m.note.lower()
        assert any(
            "prématurée REFUS" in rec.message
            for rec in caplog.records
        )

    def test_mesure_jour_echeance_acceptee(self, fiche_petrole):
        """today == echeance → mesure autorisée (horizon écoulé pile)."""
        c = _cell("LONG", "24h", bdate=date(2026, 5, 10))
        m = jr.measure_cell(
            c, "petrole", fiche_petrole,
            prix_emission=100.0, prix_courant=102.0,
            today=date(2026, 5, 11),  # = echeance
        )
        assert m.outcome == jr.OUTCOME_VRAI  # +2 % > 1 % LONG

    def test_cas_nominal_inchange_sans_kwargs(self, fiche_petrole):
        """Backward-compat : sans prix_courant_date ni today, comportement inchangé."""
        c = _cell("LONG", "24h", bdate=date(2026, 5, 1))
        m = jr.measure_cell(c, "petrole", fiche_petrole, 100.0, 102.0)
        assert m.outcome == jr.OUTCOME_VRAI

    def test_cas_nominal_avec_kwargs_coherents(self, fiche_petrole):
        """Prix courant postérieur + today après échéance → mesure normale."""
        c = _cell("SHORT", "7j", bdate=date(2026, 5, 1))
        m = jr.measure_cell(
            c, "petrole", fiche_petrole,
            prix_emission=100.0, prix_courant=96.0,  # -4 % > seuil 2.5 % SHORT
            prix_courant_date=date(2026, 5, 8),  # après émission
            today=date(2026, 5, 9),  # après échéance (= 2026-05-08)
        )
        assert m.outcome == jr.OUTCOME_VRAI

    def test_lookahead_prioritaire_sur_autres_etats(self, fiche_petrole):
        """Le look-ahead doit court-circuiter AVANT toute logique de calcul.

        Même avec un prix_emission None (qui marquerait normalement
        suivi-interrompu pour autre raison), le look-ahead doit être détecté
        car la note doit l'expliciter (traçabilité du refus).
        """
        c = _cell("LONG", "24h", bdate=date(2026, 5, 10))
        m = jr.measure_cell(
            c, "petrole", fiche_petrole,
            prix_emission=None, prix_courant=120.0,
            prix_courant_date=date(2026, 5, 9),
        )
        assert m.outcome == jr.OUTCOME_INTERROMPU
        assert "look-ahead" in m.note.lower(), (
            "le motif de refus doit être tracé pour audit"
        )


# ===========================================================================
# Cas réel/fixture : look-ahead refusé sur fichier prix-emission existant
# ===========================================================================

def test_lookahead_refuse_sur_fixture_reelle(tmp_path, fiche_petrole):
    """Reproduit un cas réaliste : bulletin émis le 2026-06-01, mais le fetch
    « prix courant » renverrait une date antérieure (2026-05-30) — bug TZ
    typique. Le journaliste doit REFUSER (suivi-interrompu) et non scorer.
    """
    bdate = date(2026, 6, 1)
    c = jr.BulletinCell(
        bulletin_date=bdate,
        actif_name="Pétrole (Brent)",
        horizon="24h",
        conclusion="LONG",
        score=0.5,
    )
    # Cas pathologique : on a un prix qui ressemble à un "courant" mais
    # daté de 2j AVANT l'émission. Sans le garde, on scorerait VRAI/FAUSSE
    # selon un prix connu d'avance — corruption du KPI.
    m = jr.measure_cell(
        c, "petrole", fiche_petrole,
        prix_emission=93.08,         # cf. v3/data/prix-emission/2026-06-01.json
        prix_courant=95.50,          # "prix courant" usurpé
        prix_courant_date=date(2026, 5, 30),  # AVANT émission
        today=date(2026, 6, 2),
    )
    assert m.outcome == jr.OUTCOME_INTERROMPU
    assert m.outcome not in (jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE), (
        "régression critique : un look-ahead a produit un verdict"
    )
    assert "look-ahead" in m.note.lower()


# ===========================================================================
# Intégration : measure() propage today (défense en profondeur)
# ===========================================================================

def test_measure_propagation_today_active_garde_prematurite(
    tmp_path, fiche_petrole, monkeypatch,
):
    """`measure()` doit passer today à measure_cell — défense en profondeur.

    On vérifie que les cellules dont l'échéance est dans le futur sont
    EXCLUES (filtre boucle), et qu'aucune Measure n'a `today < echeance`.
    """
    bdate = date(2026, 5, 1)
    bulletins_dir = tmp_path / "bulletins"
    prix_dir = tmp_path / "prix-emission"
    bulletins_dir.mkdir()
    prix_dir.mkdir()

    # Bulletin minimal compatible parseur
    (bulletins_dir / f"bulletin-{bdate.isoformat()}.md").write_text(
        "# Bulletin\n\n"
        "| Actif | 24h | 7j | 1m |\n"
        "|---|---|---|---|\n"
        "| Pétrole (Brent) | LONG (+0.50) | LONG (+0.50) | LONG (+0.50) |\n",
        encoding="utf-8",
    )
    (prix_dir / f"{bdate.isoformat()}.json").write_text(
        json.dumps({"BZ=F": 100.0}), encoding="utf-8"
    )

    measures, _ = jr.measure(
        today=date(2026, 5, 3),  # 24h échue (2026-05-02), 7j et 1m PAS encore
        bulletins_dir=bulletins_dir,
        prix_emission_dir=prix_dir,
        fiches={"petrole": fiche_petrole},
        fetch_price=lambda t: 102.0,
    )

    # Seul l'horizon 24h doit être mesuré
    horizons_mesures = {m.horizon for m in measures}
    assert horizons_mesures == {"24h"}
    # Aucune Measure prématurée
    for m in measures:
        assert m.echeance <= date(2026, 5, 3), (
            f"mesure prématurée passée à travers : echeance={m.echeance}"
        )
        # Le verdict normal doit fonctionner (cas nominal)
        assert m.outcome == jr.OUTCOME_VRAI
