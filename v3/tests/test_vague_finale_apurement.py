"""Vague finale d'apurement de dette (02/07) — preuves des 3 chantiers.

1. Anti-pollution v3/data : les writers résolvent leur chemin par défaut
   dynamiquement (path=None → constante module) → le monkeypatch du conftest est
   effectif (prouvé ici sur save_suivi_tracking / write_variations_24h / save_cache).
2. Garde-fou fraîcheur fournisseur : flag-only, jamais d'invalidation d'outcome.
3. Base émission unifiée sur suivi-tracking + marqueur `base` + guard aval.
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bilan_jour as bj  # noqa: E402
import journaliste as jr  # noqa: E402
import last_good_cache as lgc  # noqa: E402
import run_suivi as rs  # noqa: E402


# --- Chantier 1 : writers path=None résolvent la constante module (monkeypatchable) ---

def test_save_suivi_tracking_defaut_dynamique(monkeypatch, tmp_path):
    """base_dir=None → SUIVI_TRACKING_DIR courant (donc redirigeable en test)."""
    cible = tmp_path / "td"
    monkeypatch.setattr(rs, "SUIVI_TRACKING_DIR", cible)
    li = rs.SuiviLigne(
        actif="Or", call="SHORT", ouverture=100.0, prix_courant=99.0, delta_pct=-1.0,
        statut="✅", tendance="—", delta_vs_prec=None, suggestion="Hold",
        seuil_pct=0.3, vendre="Pas vendre", selection=True,
        fav_now=1.0, fav_prec=None, fav_now_emission=1.23,
    )
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now = datetime(2026, 6, 8, 12, 5, tzinfo=ZoneInfo("Europe/Paris"))
    p = rs.save_suivi_tracking(date(2026, 6, 8), "12h", [li], now)  # base_dir=None
    assert p is not None and p.parent == cible


def test_write_variations_et_save_cache_defaut_dynamique(monkeypatch, tmp_path):
    v = tmp_path / "var.md"
    monkeypatch.setattr(bj, "VARIATIONS_24H_FILE", v)
    monkeypatch.setattr(bj, "MEASURES_LOG_FILE", tmp_path / "empty.jsonl")
    out = bj.write_variations_24h()  # path=None
    assert out == v and v.exists()
    lg = tmp_path / "lg.json"
    monkeypatch.setattr(lgc, "LAST_GOOD_PATH", lg)
    lgc.save_cache({"x": 1})  # path=None
    assert lg.exists()


# --- Chantier 2 : garde-fou fraîcheur fournisseur (flag-only) ---

def test_flag_prix_suspect_stale_journaliste():
    """Deux échéances consécutives au MÊME prix d'échéance (même ticker) → la plus
    récente est flaggée ; l'outcome n'est jamais touché."""
    def _m(ech, px, outcome):
        cell = jr.BulletinCell(
            bulletin_date=ech, bulletin_id="b", actif_name="Coton",
            horizon="24h", conclusion="LONG", score=1.0,
        )
        return jr.Measure(
            cell=cell, fiche_key="coton", ticker="COTN", horizon="24h",
            echeance=ech, prix_emission=2.30, prix_courant=px,
            seuil_pct=0.3, delta_pct=1.0, outcome=outcome,
        )
    m29 = _m(date(2026, 6, 29), 2.371, jr.OUTCOME_VRAI)
    m30 = _m(date(2026, 6, 30), 2.371, jr.OUTCOME_FAUSSE)  # figé vs veille
    jr._flag_prix_suspect_stale([m29, m30])
    assert m30.prix_suspect_stale is True
    assert m29.prix_suspect_stale is None       # pas d'échéance antérieure comparable
    assert m30.outcome == jr.OUTCOME_FAUSSE       # FLAG-ONLY : outcome intact


def test_flag_prix_suspect_stale_prix_differents_pas_de_flag():
    def _m(ech, px):
        cell = jr.BulletinCell(
            bulletin_date=ech, bulletin_id="b", actif_name="Or",
            horizon="24h", conclusion="LONG", score=1.0,
        )
        return jr.Measure(
            cell=cell, fiche_key="or", ticker="GC=F", horizon="24h",
            echeance=ech, prix_emission=100.0, prix_courant=px,
            seuil_pct=0.3, delta_pct=1.0, outcome=jr.OUTCOME_VRAI,
        )
    ms = [_m(date(2026, 6, 29), 3400.0), _m(date(2026, 6, 30), 3410.0)]
    jr._flag_prix_suspect_stale(ms)
    assert all(m.prix_suspect_stale is None for m in ms)


def test_flag_prix_stale_bilan_depuis_measures_log(tmp_path):
    """Clôture du jour identique à la dernière clôture persistée (veille) → flag."""
    log = tmp_path / "measures-log.jsonl"
    log.write_text(json.dumps({
        "actif": "Coton", "horizon": "24h", "echeance": "2026-06-29",
        "prix_echeance": 2.371, "realized_pct": 1.0, "outcome": "VRAI",
    }) + "\n", encoding="utf-8")

    class _Cell:
        actif_name = "Coton"

    class _M:
        cell = _Cell()
        prix_courant = 2.371
        prix_suspect_stale = None
    m = _M()
    bj._flag_prix_stale_bilan([m], date(2026, 6, 30), log)
    assert m.prix_suspect_stale is True


# --- Chantier 3 : base émission + marqueur + guard aval ---

def test_tracking_marque_base_emission(tmp_path):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    li = rs.SuiviLigne(
        actif="Or", call="SHORT", ouverture=100.0, prix_courant=99.0, delta_pct=-1.0,
        statut="✅", tendance="—", delta_vs_prec=None, suggestion="Hold",
        seuil_pct=0.3, vendre="Pas vendre", selection=True,
        fav_now=0.9, fav_prec=None, fav_now_emission=1.5,
    )
    now = datetime(2026, 6, 8, 12, 5, tzinfo=ZoneInfo("Europe/Paris"))
    rs.save_suivi_tracking(date(2026, 6, 8), "12h", [li], now, base_dir=tmp_path)
    raw = json.loads((tmp_path / "2026-06-08.json").read_text(encoding="utf-8"))
    assert raw["base"] == "emission"
    assert raw["12h"]["Or"]["fav_pct"] == 1.5      # base entrée, pas fav_now (0.9)
    data = rs.load_suivi_tracking(date(2026, 6, 8), base_dir=tmp_path)
    assert data["_base"] == "emission"


def test_require_base_ecarte_snapshot_ouverture(tmp_path):
    """Un snapshot SANS marqueur (= base ouverture) est ignoré si l'appelant exige
    la base émission → « — » (None), zéro mélange de bases."""
    tdir = tmp_path / "suivi-tracking"
    tdir.mkdir()
    (tdir / "2026-06-08.json").write_text(json.dumps({
        "12h": {"Or": {"call": "SHORT", "fav_pct": 1.99}},   # pas de "base" → ouverture
    }), encoding="utf-8")
    # Base-agnostique (défaut) : lit la valeur.
    p12, _ = bj.load_perf_intraday_favorable(
        date(2026, 6, 8), "Or", "SHORT", tracking_dir=tdir, snapshot_dir=tmp_path / "x",
    )
    assert p12 == 1.99
    # require_base="emission" : base non concordante → None (colonne « — »).
    p12e, _ = bj.load_perf_intraday_favorable(
        date(2026, 6, 8), "Or", "SHORT", tracking_dir=tdir, snapshot_dir=tmp_path / "x",
        require_base="emission",
    )
    assert p12e is None
