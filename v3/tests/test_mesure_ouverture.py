"""Tests Phase 1 — mesure ouverture→clôture + bilan 22h.

Dérivés des critères d'acceptation CA-M* / CA-B* / CA-W6 de la spec
`v3/docs/reco/spec-refonte-5-rapports.md`. WIN RATE ONLY (aucun montant).
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import journaliste as jr  # noqa: E402
import mesure_ouverture as mo  # noqa: E402
import bilan_jour as bj  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


def _fiche(actif, ticker, famille, seuil_24h=1.0):
    return {
        "actif": actif,
        "ticker_principal": ticker,
        "famille": famille,
        "seuils_reussite_pct": {"24h": seuil_24h, "7j": 1.3, "1m": 3.0},
    }


FICHE_OR = _fiche("Or", "GC=F", "métaux-précieux", 0.5)        # continu
FICHE_CAC = _fiche("CAC 40", "^FCHI", "indices")               # eu
FICHE_SP = _fiche("S&P 500", "^GSPC", "indices")               # us


# ---------------------------------------------------------------------------
# Mapping groupe (déterministe)
# ---------------------------------------------------------------------------

def test_actif_group_mapping():
    assert mo.actif_group(FICHE_OR) == "continu"
    assert mo.actif_group(FICHE_CAC) == "eu"      # override par nom
    assert mo.actif_group(FICHE_SP) == "us"       # override par nom
    assert mo.actif_group(_fiche("VIX", "^VIX", "volatilité")) == "us"
    # Famille inconnue → None (zéro invention)
    assert mo.actif_group(_fiche("X", "X", "famille-bidon")) is None


# ---------------------------------------------------------------------------
# CA-M2 — délai post-ouverture (heure Paris, DST via ZoneInfo)
# ---------------------------------------------------------------------------

def test_is_open_for_stamp_respecte_delai():
    # Continu ouvre 08h00 + délai 5 min → stampable à 08h05, pas à 08h00.
    avant = datetime(2026, 6, 8, 8, 4, tzinfo=PARIS)
    apres = datetime(2026, 6, 8, 8, 6, tzinfo=PARIS)
    assert mo.is_open_for_stamp("continu", avant) is False
    assert mo.is_open_for_stamp("continu", apres) is True
    # EU ouvre 09h00 : à 08h06 le continu est ouvert mais pas l'EU.
    assert mo.is_open_for_stamp("eu", datetime(2026, 6, 8, 8, 6, tzinfo=PARIS)) is False
    assert mo.is_open_for_stamp("eu", datetime(2026, 6, 8, 9, 6, tzinfo=PARIS)) is True
    # US ouvre 15h30.
    assert mo.is_open_for_stamp("us", datetime(2026, 6, 8, 15, 30, tzinfo=PARIS)) is False
    assert mo.is_open_for_stamp("us", datetime(2026, 6, 8, 15, 36, tzinfo=PARIS)) is True


def test_is_open_for_stamp_dst_jamais_offset_dur():
    """Garde-fou DST : un datetime UTC est correctement converti en Paris.
    En CEST (été), 06h05 UTC = 08h05 Paris → continu stampable."""
    utc = datetime(2026, 6, 8, 6, 6, tzinfo=ZoneInfo("UTC"))  # = 08h06 Paris CEST
    assert mo.is_open_for_stamp("continu", utc) is True
    # En CET (hiver), 07h06 UTC = 08h06 Paris → continu stampable aussi.
    utc_hiver = datetime(2026, 1, 8, 7, 6, tzinfo=ZoneInfo("UTC"))
    assert mo.is_open_for_stamp("continu", utc_hiver) is True


# ---------------------------------------------------------------------------
# CA-M1 — stamp idempotent + entry-lock
# ---------------------------------------------------------------------------

def test_stamp_prix_ouverture_cree_json_et_idempotent(tmp_path):
    fiches = {"or": FICHE_OR}
    base = tmp_path / "prix-ouverture"
    now = datetime(2026, 6, 8, 8, 30, tzinfo=PARIS)  # continu ouvert
    p = mo.stamp_prix_ouverture(
        date_j=date(2026, 6, 8), fiches=fiches,
        fetch_price=lambda t: 3420.0, base_dir=base, now=now,
    )
    assert p.exists()
    data = json.loads(p.read_text())
    assert data == {"GC=F": 3420.0}

    # Re-run avec un prix DIFFÉRENT → entry-lock : l'ancien est préservé (CA-M1).
    mo.stamp_prix_ouverture(
        date_j=date(2026, 6, 8), fiches=fiches,
        fetch_price=lambda t: 9999.0, base_dir=base, now=now,
    )
    data2 = json.loads(p.read_text())
    assert data2 == {"GC=F": 3420.0}  # inchangé


def test_stamp_marche_pas_ouvert_skip(tmp_path):
    """Un actif US à 08h30 Paris (US fermé) n'est PAS stampé (pas d'invention)."""
    fiches = {"sp500": FICHE_SP}
    base = tmp_path / "prix-ouverture"
    now = datetime(2026, 6, 8, 8, 30, tzinfo=PARIS)  # US ouvre 15h30
    mo.stamp_prix_ouverture(
        date_j=date(2026, 6, 8), fiches=fiches,
        fetch_price=lambda t: 5300.0, base_dir=base, now=now,
    )
    data = json.loads((base / "2026-06-08.json").read_text())
    assert data == {}  # S&P pas encore ouvert → absent


# ---------------------------------------------------------------------------
# CA-M3 — Twelve KO → ticker absent (zéro invention)
# ---------------------------------------------------------------------------

def test_stamp_twelve_ko_ticker_absent(tmp_path):
    fiches = {"or": FICHE_OR}
    base = tmp_path / "prix-ouverture"
    now = datetime(2026, 6, 8, 8, 30, tzinfo=PARIS)
    mo.stamp_prix_ouverture(
        date_j=date(2026, 6, 8), fiches=fiches,
        fetch_price=lambda t: None, base_dir=base, now=now,  # Twelve KO
    )
    data = json.loads((base / "2026-06-08.json").read_text())
    assert "GC=F" not in data  # absent, PAS de null


# ---------------------------------------------------------------------------
# CA-M4 / fix L027 — référence du 24h selon le groupe de marché
#   - NON continu (indices cash, VIX) → prix-OUVERTURE de marché (inchangé)
#   - CONTINU (or, FX, métaux, commodities) → prix d'ÉMISSION 7h (point
#     d'exécution réel ; l'ouverture 8h pouvait tomber au milieu d'un mouvement)
# ---------------------------------------------------------------------------

def _write_bulletin_7h(bulletins_dir: Path, bdate: date, actif: str, conc: str, score: float):
    bulletins_dir.mkdir(parents=True, exist_ok=True)
    p = bulletins_dir / f"bulletin-{bdate.isoformat()}-07h.md"
    p.write_text(
        f"# Bulletin — {bdate.isoformat()}\n\n## Matrice\n\n"
        "| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
        f"| {actif} | {conc} (+{score}) | {conc} (+{score}) | {conc} (+{score}) |\n",
        encoding="utf-8",
    )
    return p


def test_24h_non_continu_utilise_prix_ouverture(tmp_path):
    """Indice cash (CAC, NON continu) : la référence reste l'OUVERTURE de marché.

    Le fix L027 est SCOPÉ aux continus — un indice fermé à 7h garde sa logique
    d'ouverture (9h CAC), un prix d'émission serait un prix de nuit.
    """
    bdate = date(2026, 6, 8)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"
    _write_bulletin_7h(bulletins, bdate, "CAC 40", "LONG", 1.5)

    # Émission (7h, marché fermé) = 3500 ; ouverture réelle 9h = 3400.
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({"^FCHI": 3500.0}))
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"^FCHI": 3400.0}))

    measures, _ = jr.measure(
        today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={"cac40": FICHE_CAC},
        fetch_price=lambda t: 3460.0,  # clôture
    )
    m24 = [m for m in measures if m.horizon == "24h"][0]
    # Référence = OUVERTURE 3400 (pas l'émission 3500) — inchangé pour un indice.
    assert m24.prix_emission == 3400.0
    assert m24.prix_reference_source == "ouverture"
    assert m24.outcome == jr.OUTCOME_VRAI  # 3400 → 3460 = +1.76 % LONG


def test_24h_continu_utilise_prix_emission_pas_ouverture(tmp_path):
    """Continu (or) : la référence est l'ÉMISSION 7h, PAS l'ouverture 8h (fix L027).

    L'ouverture stampée à 8h peut tomber au milieu d'un mouvement déjà entamé
    depuis l'émission 7h → mesurer depuis 8h tronque le mouvement jugé.
    """
    bdate = date(2026, 6, 8)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"
    _write_bulletin_7h(bulletins, bdate, "Or", "LONG", 1.5)

    # Émission 7h (point d'exécution) = 3400 ; ouverture 8h (après un début de
    # mouvement) = 3450. La référence DOIT être l'émission 3400.
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({"GC=F": 3400.0}))
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 3450.0}))

    measures, _ = jr.measure(
        today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={"or": FICHE_OR},
        fetch_price=lambda t: 3460.0,  # clôture
    )
    m24 = [m for m in measures if m.horizon == "24h"][0]
    # Référence = ÉMISSION 3400 (pas l'ouverture 3450).
    assert m24.prix_emission == 3400.0
    assert m24.prix_reference_source == "emission"
    # 3400 → 3460 = +1.76 % (LONG, seuil 0.5 %) → VRAI.
    assert m24.outcome == jr.OUTCOME_VRAI


# ---------------------------------------------------------------------------
# CA-M5 / fix L027 — fallback de référence si la source primaire est absente
# ---------------------------------------------------------------------------

def test_fallback_ouverture_si_emission_absente_continu(tmp_path, caplog):
    """Continu, émission absente → fallback OUVERTURE (référence dégradée, WARNING)."""
    bdate = date(2026, 6, 8)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"  # vide → fallback
    prix_ouv = tmp_path / "prix-ouverture"
    _write_bulletin_7h(bulletins, bdate, "Or", "LONG", 1.5)
    prix_emis.mkdir()
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 3400.0}))

    import logging
    with caplog.at_level(logging.WARNING):
        measures, _ = jr.measure(
            today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
            prix_ouverture_dir=prix_ouv, fiches={"or": FICHE_OR},
            fetch_price=lambda t: 3460.0,
        )
    m24 = [m for m in measures if m.horizon == "24h"][0]
    assert m24.prix_emission == 3400.0
    assert m24.prix_reference_source == "ouverture"
    assert any("fallback ouverture" in r.message for r in caplog.records)


def test_fallback_emission_si_ouverture_absente_non_continu(tmp_path, caplog):
    """Non continu (CAC), ouverture absente → fallback ÉMISSION (inchangé, CA-M5)."""
    bdate = date(2026, 6, 8)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"  # vide → fallback
    _write_bulletin_7h(bulletins, bdate, "CAC 40", "LONG", 1.5)
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({"^FCHI": 3400.0}))

    import logging
    with caplog.at_level(logging.WARNING):
        measures, _ = jr.measure(
            today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
            prix_ouverture_dir=prix_ouv, fiches={"cac40": FICHE_CAC},
            fetch_price=lambda t: 3460.0,
        )
    m24 = [m for m in measures if m.horizon == "24h"][0]
    assert m24.prix_emission == 3400.0
    assert m24.prix_reference_source == "emission"
    assert any("fallback prix d'émission" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# CA-M6 / CA-M6b — filtre 7h (fin du gonflement ×3)
# ---------------------------------------------------------------------------

def test_filtre_7h_reconnaissance_creneaux():
    assert jr.is_seven_am_bulletin("2026-06-08-07h") is True
    assert jr.is_seven_am_bulletin("2026-06-08-05h") is True   # UTC historique
    assert jr.is_seven_am_bulletin("2026-06-08-06h") is True   # cron 7h en HIVER
    assert jr.is_seven_am_bulletin("2026-06-08-08h") is True   # relance matinale tôt
    assert jr.is_seven_am_bulletin("2026-06-08") is True       # ancien nommage
    assert jr.is_seven_am_bulletin("2026-06-08-09h") is False  # après la fenêtre briefing
    assert jr.is_seven_am_bulletin("2026-06-08-12h") is False
    assert jr.is_seven_am_bulletin("2026-06-08-18h") is False
    assert jr.is_seven_am_bulletin("2026-06-08-16h") is False


def test_seul_7h_compte_dans_kpi(tmp_path):
    """3 bulletins le même jour → seul le 7h donne une mesure NOTÉE (N_brut=1).

    Date POST-cutover (GC=F/Or est reset au 2026-06-17 depuis le cutover « fix
    L027 — référence continus = émission 7h ») : on date le bulletin au 2026-06-17
    pour que l'observation entre bien dans le KPI v2 et que le test isole son objet
    réel (filtre 7h vs 12h/18h, CA-M6b), sans interférence de l'enforcement cutover.
    Or étant un continu, la référence est l'ÉMISSION 7h (fix L027) → on la stampe.
    """
    bdate = date(2026, 6, 17)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_ouv = tmp_path / "prix-ouverture"
    prix_emis = tmp_path / "prix-emission"
    bulletins.mkdir()
    for creneau in ("07h", "12h", "18h"):
        p = bulletins / f"bulletin-{bdate.isoformat()}-{creneau}.md"
        p.write_text(
            f"# B {creneau}\n\n## M\n\n| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
            "| Or | LONG (+1.5) | LONG (+1.5) | LONG (+1.5) |\n",
            encoding="utf-8",
        )
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 3400.0}))
    prix_emis.mkdir()
    # Continu → référence = émission 7h (fix L027).
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({"GC=F": 3400.0}))

    measures, kpis = jr.measure(
        today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={"or": FICHE_OR},
        fetch_price=lambda t: 3460.0,
    )
    m24 = [m for m in measures if m.horizon == "24h"]
    notes = [m for m in m24 if m.outcome in (jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE, jr.OUTCOME_NC)]
    non_notes = [m for m in m24 if m.outcome == jr.OUTCOME_NON_NOTE]
    # 1 seul noté (le 7h), 2 non-notés (12h + 18h).
    assert len(notes) == 1
    assert len(non_notes) == 2
    assert notes[0].cell.bulletin_id.endswith("07h")
    # KPI : N_brut = 1 (pas 3).
    kpi = kpis[("or", "24h")]
    assert kpi.n_total == 1


# ---------------------------------------------------------------------------
# CA-W6 — win rate par conviction
# ---------------------------------------------------------------------------

def test_conviction_level_forte_vs_faible():
    seuil = 0.6
    # Score fort, aucun drapeau → forte.
    assert bj.conviction_level({"score_pm1": 1.5}, seuil) == "forte"
    # Score fort MAIS drapeau coin_flip → faible.
    assert bj.conviction_level({"score_pm1": 1.5, "coin_flip": True}, seuil) == "faible"
    # Score faible → faible.
    assert bj.conviction_level({"score_pm1": 0.3}, seuil) == "faible"
    # Drapeau quasi_neutre → faible même si score >= seuil.
    assert bj.conviction_level({"score_pm1": 5.0, "quasi_neutre": True}, seuil) == "faible"
    # Drapeau diverge (contradiction) → faible.
    assert bj.conviction_level({"score_pm1": 5.0, "diverge": True}, seuil) == "faible"


class _FakeCell:
    def __init__(self, actif):
        self.actif_name = actif


class _FakeMeasure:
    def __init__(self, actif, horizon, outcome):
        self.cell = _FakeCell(actif)
        self.horizon = horizon
        self.outcome = outcome


def test_win_rate_par_conviction_segmente():
    conv = {("Or", "24h"): "forte", ("S&P 500", "24h"): "faible"}
    measures = [
        _FakeMeasure("Or", "24h", jr.OUTCOME_VRAI),
        _FakeMeasure("S&P 500", "24h", jr.OUTCOME_FAUSSE),
        _FakeMeasure("Nasdaq", "24h", jr.OUTCOME_VRAI),  # inconnu → faible
    ]
    wr = bj.win_rate_par_conviction(measures, conv)
    assert wr.n_forte == 1 and wr.n_vrai_forte == 1
    assert wr.taux_forte == 100.0
    assert wr.n_faible == 2 and wr.n_vrai_faible == 1
    assert wr.taux_faible == 50.0


# ---------------------------------------------------------------------------
# CA-B1/B4/B5 — bilan du jour
# ---------------------------------------------------------------------------

def test_build_bilan_jour_note_24h_et_win_rate(tmp_path, monkeypatch):
    bdate = date(2026, 6, 8)
    bulletins = tmp_path / "bulletins"
    prix_ouv = tmp_path / "prix-ouverture"
    prix_emis = tmp_path / "prix-emission"
    log_dir = tmp_path / "decision-log"
    _write_bulletin_7h(bulletins, bdate, "Or", "LONG", 1.5)
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 3400.0}))
    prix_emis.mkdir()
    log_dir.mkdir()
    (log_dir / f"{bdate.isoformat()}-0704.jsonl").write_text(
        json.dumps({"bulletin_date": bdate.isoformat(), "actif": "Or",
                    "horizon": "24h", "score_pm1": 1.5}) + "\n", encoding="utf-8",
    )
    # now = 22h15 Paris (le bilan note le 24h le soir même).
    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    bilan = bj.build_bilan_jour(
        now=now, date_j=bdate, bulletins_dir=bulletins,
        decision_log_dir=log_dir, fiches={"or": FICHE_OR},
        prix_ouverture_dir=prix_ouv, prix_emission_dir=prix_emis,
        fetch_price=lambda t: 3460.0,  # clôture en hausse → LONG VRAI
    )
    assert bilan.n_vrai == 1
    assert bilan.win_rate_jour == 100.0
    # Référence du 24h = ouverture (CA-B1).
    assert bilan.measures_24h[0].prix_emission == 3400.0
    # Conviction forte (score 1.5, aucun drapeau).
    assert bilan.conviction.n_forte == 1


def test_bilan_jour_aucun_montant_monetaire(tmp_path):
    """CA-B5 : le rapport ne contient aucune mention monétaire."""
    bdate = date(2026, 6, 8)
    bulletins = tmp_path / "bulletins"
    prix_ouv = tmp_path / "prix-ouverture"
    prix_emis = tmp_path / "prix-emission"
    _write_bulletin_7h(bulletins, bdate, "Or", "LONG", 1.5)
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 3400.0}))
    prix_emis.mkdir()
    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    bilan = bj.build_bilan_jour(
        now=now, date_j=bdate, bulletins_dir=bulletins,
        decision_log_dir=tmp_path / "decision-log", fiches={"or": FICHE_OR},
        prix_ouverture_dir=prix_ouv, prix_emission_dir=prix_emis,
        fetch_price=lambda t: 3460.0,
    )
    md = bilan.markdown.lower()
    for interdit in ("€", "$", "gain", "perte", "rendement", "p&l", "profit"):
        assert interdit not in md, f"mention monétaire interdite trouvée : {interdit}"


def test_bilan_jour_flag_gros_move(tmp_path):
    """CA §3.4 : un FAUX d'amplitude >= 2×seuil porte le flag ⚡ gros move."""
    bdate = date(2026, 6, 8)
    bulletins = tmp_path / "bulletins"
    prix_ouv = tmp_path / "prix-ouverture"
    prix_emis = tmp_path / "prix-emission"
    # Call SHORT mais marché monte fort → FAUSSE à forte amplitude.
    _write_bulletin_7h(bulletins, bdate, "Or", "SHORT", 1.5)
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 3000.0}))
    prix_emis.mkdir()
    now = datetime(2026, 6, 8, 22, 15, tzinfo=PARIS)
    # 3000 → 3060 = +2 % (seuil 0.5 % → 2×0.5=1 % ; 2 % > 1 %), SHORT → FAUSSE.
    bilan = bj.build_bilan_jour(
        now=now, date_j=bdate, bulletins_dir=bulletins,
        decision_log_dir=tmp_path / "decision-log", fiches={"or": FICHE_OR},
        prix_ouverture_dir=prix_ouv, prix_emission_dir=prix_emis,
        fetch_price=lambda t: 3060.0,
    )
    assert bilan.n_fausse == 1
    assert "⚡ gros move" in bilan.markdown
    assert "FAUX à forte amplitude" in bilan.markdown
