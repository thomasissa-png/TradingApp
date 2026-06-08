"""Tests Phase 2 — Suivis intra-journée 12h/18h (R2/R3).

Dérivés des critères d'acceptation CA-S1..CA-S6b de la spec
`v3/docs/reco/spec-refonte-5-rapports.md` §3.2/§3.3. WIN RATE ONLY (aucun montant).

Couvre :
- statut vs ouverture (✅ gagne / ⚠️ perd / — neutre) — CA-S4
- dynamique de tendance (↑ s'accélère / ↓ s'essouffle / ⇄ se retourne) — §3.3
- drapeau de sortie au seuil de l'actif (CONTRE le call) — CA-S4
- US pas encore ouvert à 12h (🕐) — correction M-H
- run_suivi n'écrit PAS dans measures-log.jsonl — CA-S6/CA-S6b
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_suivi as rs  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


# ---------------------------------------------------------------------------
# Fixtures : un bulletin 7h minimal + ouvertures
# ---------------------------------------------------------------------------

BULLETIN_7H = """# Bulletin 2026-06-08 07h

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| Or | SHORT (-1.20) | SHORT (-0.80) | SHORT (-0.50) |
| CAC 40 | SHORT (-0.40) | LONG (+0.20) | LONG (+0.10) |
| S&P 500 | LONG (+0.60) | LONG (+0.30) | LONG (+0.10) |
"""


def _fiche(actif, ticker, famille, seuil_24h):
    return {
        "actif": actif,
        "ticker_principal": ticker,
        "famille": famille,
        "seuils_reussite_pct": {"24h": seuil_24h, "7j": 1.3, "1m": 3.0},
    }


FICHES = {
    "or": _fiche("Or", "GC=F", "métaux-précieux", 0.5),       # continu
    "cac40": _fiche("CAC 40", "^FCHI", "indices", 0.4),       # eu
    "sp500": _fiche("S&P 500", "^GSPC", "indices", 0.6),      # us
}


@pytest.fixture
def env(tmp_path):
    """Construit bulletins + ouvertures + dossiers data temporaires."""
    bdir = tmp_path / "bulletins"
    bdir.mkdir()
    (bdir / "bulletin-2026-06-08-07h.md").write_text(BULLETIN_7H, encoding="utf-8")
    odir = tmp_path / "prix-ouverture"
    odir.mkdir()
    (odir / "2026-06-08.json").write_text(
        json.dumps({"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5300.0}),
        encoding="utf-8",
    )
    dlog = tmp_path / "decision-log"
    dlog.mkdir()
    sdir = tmp_path / "suivi"
    return {
        "bdir": bdir, "odir": odir, "dlog": dlog, "sdir": sdir,
        "fiches": FICHES, "tmp": tmp_path,
    }


def _build(env, report_type, now, cur, fiches=None):
    return rs.build_suivi(
        report_type,
        now=now,
        date_j=date(2026, 6, 8),
        bulletins_dir=env["bdir"],
        decision_log_dir=env["dlog"],
        suivi_dir=env["sdir"],
        prix_ouverture_dir=env["odir"],
        fiches=fiches or env["fiches"],
        fetch_price=lambda t: cur.get(t),
    )


def _ligne(rapport, actif):
    return next(li for li in rapport.lignes if li.actif == actif)


# ---------------------------------------------------------------------------
# CA-S1 : tableau des actifs actionnables, colonnes attendues
# ---------------------------------------------------------------------------

def test_load_briefing_cells_24h_actionnables(env):
    cells = rs.load_briefing_cells(date(2026, 6, 8), env["bdir"])
    actifs = {c.actif_name for c in cells}
    assert actifs == {"Or", "CAC 40", "S&P 500"}
    assert all(c.horizon == "24h" for c in cells)


# ---------------------------------------------------------------------------
# CA-S4 : statut vs ouverture (✅ gagne / ⚠️ perd / — neutre)
# ---------------------------------------------------------------------------

def test_statut_gagne_perd_neutre():
    band = 0.001  # 0,1%
    # Or SHORT, monte +1% → perd
    assert rs.compute_statut(1.0, "SHORT", band) == "⚠️ perd"
    # Or SHORT, baisse -1% → gagne
    assert rs.compute_statut(-1.0, "SHORT", band) == "✅ gagne"
    # LONG, monte → gagne
    assert rs.compute_statut(0.5, "LONG", band) == "✅ gagne"
    # mouvement sous la bande (0.05% < 0.1%) → neutre
    assert rs.compute_statut(0.05, "LONG", band) == "— neutre"


def test_statut_suivi_vs_ouverture(env):
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT, ouverture 3400 → 3438 (+1.12%) → perd
    cur = {"GC=F": 3438.0, "^FCHI": 8100.0, "^GSPC": None}
    r = _build(env, "12h", now, cur)
    assert _ligne(r, "Or").statut == "⚠️ perd"
    assert _ligne(r, "Or").delta_pct == pytest.approx(1.12, abs=0.01)
    # CAC 40 SHORT, baisse (8120 → 8100) → gagne
    assert _ligne(r, "CAC 40").statut == "✅ gagne"


# ---------------------------------------------------------------------------
# Dynamique de tendance (§3.3) : ↑ / ↓ / ⇄
# ---------------------------------------------------------------------------

def test_compute_tendance_dynamique():
    band = 0.001
    # 12h : pas de précédent → —
    assert rs.compute_tendance(0.5, None, False, band) == "—"
    # accélère : même signe, amplitude plus grande
    assert rs.compute_tendance(1.0, 0.5, False, band) == "↑ s'accélère"
    # s'essouffle : même signe, amplitude plus petite
    assert rs.compute_tendance(0.3, 0.5, False, band) == "↓ s'essouffle"
    # se retourne : signe opposé
    assert rs.compute_tendance(-0.4, 0.5, False, band) == "⇄ se retourne"


def test_tendance_au_18h_depuis_snapshot_12h(env):
    # 12h : Or à +0.50% → snapshot persisté
    r12 = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
                 {"GC=F": 3417.0, "^FCHI": 8120.0, "^GSPC": None})
    assert _ligne(r12, "Or").delta_pct == pytest.approx(0.5, abs=0.01)
    # 18h : Or à +1.00% → s'accélère (même signe, plus fort)
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3434.0, "^FCHI": 8110.0, "^GSPC": 5310.0})
    lig = _ligne(r18, "Or")
    assert lig.delta_pct == pytest.approx(1.0, abs=0.01)
    assert lig.tendance == "↑ s'accélère"
    assert lig.delta_vs_prec == pytest.approx(0.5, abs=0.02)


def test_flag_us_confirme_infirme_au_18h(env):
    # 12h d'abord (US pas ouvert), puis 18h US ouvert
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": None})
    # S&P LONG, ouverture 5300 → 5320 (+0.38%) dans le sens du call
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5320.0})
    assert _ligne(r18, "S&P 500").tendance == "↗ confirmé US"


# ---------------------------------------------------------------------------
# CA-S4 : drapeau de sortie au seuil de l'actif, CONTRE le call
# ---------------------------------------------------------------------------

def test_suggestion_sortie_au_seuil():
    # perd au-delà du seuil → Sortie à envisager
    assert rs.compute_suggestion(1.2, "SHORT", 0.5, "⚠️ perd") == "Sortie à envisager"
    # perd sous le seuil → Surveiller
    assert rs.compute_suggestion(0.3, "SHORT", 0.5, "⚠️ perd") == "Surveiller"
    # gagne → Hold (jamais de sortie sur une position gagnante)
    assert rs.compute_suggestion(1.2, "LONG", 0.5, "✅ gagne") == "Hold"
    # neutre → Hold
    assert rs.compute_suggestion(0.05, "LONG", 0.5, "— neutre") == "Hold"


def test_suggestion_sortie_dans_rapport(env):
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT seuil 0.5%, monte +1.12% contre le call → Sortie à envisager
    r = _build(env, "12h", now, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    assert _ligne(r, "Or").suggestion == "Sortie à envisager"
    assert "Sortie à envisager" in r.markdown


# ---------------------------------------------------------------------------
# US pas encore ouvert à 12h (🕐) — correction M-H
# ---------------------------------------------------------------------------

def test_us_pas_encore_ouvert_a_12h(env):
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5301.0})
    sp = _ligne(r, "S&P 500")
    assert sp.us_pas_ouvert is True
    assert sp.statut == "🕐 pas encore ouvert"
    assert sp.delta_pct is None  # pas de delta trompeur
    assert "pas encore ouverts" in r.markdown


def test_us_ouvert_a_18h(env):
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": None})
    r = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
               {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5330.0})
    sp = _ligne(r, "S&P 500")
    assert sp.us_pas_ouvert is False
    assert sp.statut == "✅ gagne"  # LONG, +0.57%


# ---------------------------------------------------------------------------
# CA-S6 / CA-S6b : run_suivi n'écrit PAS dans measures-log.jsonl
# ---------------------------------------------------------------------------

def test_run_suivi_n_ecrit_pas_measures_log(env, tmp_path):
    measures_log = tmp_path / "measures-log.jsonl"
    measures_log.write_text("", encoding="utf-8")
    before = measures_log.read_text(encoding="utf-8")
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 3438.0, "^FCHI": 8100.0, "^GSPC": None})
    rs.write_suivi(r, base_dir=env["sdir"])
    # Le measures-log n'est jamais touché par run_suivi.
    assert measures_log.read_text(encoding="utf-8") == before
    # Le seul fichier produit dans suivi/ est le rapport markdown (+ snapshot json).
    produced = sorted(p.name for p in env["sdir"].glob("*"))
    assert "2026-06-08-12h.md" in produced


# ---------------------------------------------------------------------------
# CA-S5 : rapport court, pas de matrice LONG/SHORT
# ---------------------------------------------------------------------------

def test_rapport_court_sans_matrice(env):
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": None})
    n_lines = len(r.markdown.splitlines())
    assert n_lines <= rs.MAX_MARKDOWN_LINES
    # Pas de scoring/matrice : aucune occurrence de score brut "(-1.20)".
    assert "(-1.20)" not in r.markdown


# ---------------------------------------------------------------------------
# WIN RATE ONLY : aucune mention monétaire
# ---------------------------------------------------------------------------

def test_aucune_mention_monetaire(env):
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 3438.0, "^FCHI": 8100.0, "^GSPC": None})
    md = r.markdown.lower()
    for token in ("€", "$", "gain", "perte", "rendement", "p&l"):
        assert token not in md, f"mention monétaire interdite : {token!r}"


# ---------------------------------------------------------------------------
# Ouverture absente → — (zéro invention) — CA-S2
# ---------------------------------------------------------------------------

def test_ouverture_absente_affiche_tiret(env):
    # Pas d'ouverture pour GC=F ce jour → colonne Ouverture = — , delta = None
    odir = env["tmp"] / "ouv-vide"
    odir.mkdir()
    (odir / "2026-06-08.json").write_text(json.dumps({"^FCHI": 8120.0}), encoding="utf-8")
    r = rs.build_suivi(
        "12h", now=datetime(2026, 6, 8, 12, 3, tzinfo=PARIS), date_j=date(2026, 6, 8),
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"], suivi_dir=env["sdir"],
        prix_ouverture_dir=odir, fiches=env["fiches"], fetch_price=lambda t: 3438.0,
    )
    lig = _ligne(r, "Or")
    assert lig.ouverture is None
    assert lig.delta_pct is None
    assert lig.statut == "—"


# ---------------------------------------------------------------------------
# run_bilan : runner CLI OK (smoke)
# ---------------------------------------------------------------------------

def test_run_bilan_runner_smoke(monkeypatch):
    import run_bilan
    import bilan_jour

    called = {}

    class _FakeBilan:
        n_vrai = 0
        n_fausse = 0
        n_nc = 0
        win_rate_jour = None
        measures_24h = []

    def fake_build(now=None, date_j=None):
        called["build"] = (now, date_j)
        return _FakeBilan()

    def fake_write(bilan):
        called["write"] = True
        return Path("/tmp/bilan-jour/2026-06-08.md")

    monkeypatch.setattr(bilan_jour, "build_bilan_jour", fake_build)
    monkeypatch.setattr(bilan_jour, "write_bilan_jour", fake_write)
    rc = run_bilan.main(["--date", "2026-06-08"])
    assert rc == 0
    assert called["build"][1] == date(2026, 6, 8)
    assert called.get("write") is True
