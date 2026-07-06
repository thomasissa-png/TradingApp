"""Tests — Bloc « 📌 Positions ouvertes (Swing 7j / 1 mois) » (FEATURE 03/07).

Le « chaînon manquant » multi-horizons : une position s'OUVRE quand un actif entre
au bloc Swing 7j / Positions 1m, se MAINTIENT tant que la cellule garde le même
sens (avec % courant favorable), se CLÔTURE (ligne ✂️ une seule fois) au
retournement, puis DISPARAÎT. RENDU/LECTURE seul — zéro impact signal/mesure.

Couvre : ouverture → maintien → retournement/clôture → disparition ; zéro
réimpression (position ouverte = bloc 📌, jamais le tableau d'entrée) ;
reconstruction depuis decision-logs mockés + résolution du prix de prise ;
priorité record persisté vs bootstrap.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scoring_analyste as sa  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")


def _now(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d").replace(hour=18, tzinfo=PARIS)


def _res(fiche_key: str, nom: str, conc: dict, sel: set) -> sa.ActifResult:
    """ActifResult minimal (criteres vides) ; `_sel` = horizons où la cellule est
    DANS le bloc swing (piloté via le monkeypatch de select_swing_retenus). Le
    rendu du tableau (`_top_driver`) exige un vrai ActifResult, d'où le dataclass."""
    scores = {h: (-20.0 if v == "SHORT" else 20.0) for h, v in conc.items()}
    r = sa.ActifResult(
        nom=nom, fiche_key=fiche_key, criteres=[], scores=scores,
        conclusions=dict(conc), tie_break_notes={}, coverage=0.8,
    )
    r._sel = set(sel)  # type: ignore[attr-defined]
    return r


def _fake_select(results, H):
    """Remplace select_swing_retenus : retourne les cellules marquées `_sel` pour H
    et directionnelles (mêmes tuples (|note|, r, sens, famille))."""
    out = []
    for r in results:
        if H in getattr(r, "_sel", set()) and r.conclusions.get(H) in ("LONG", "SHORT"):
            out.append((1.0, r, r.conclusions.get(H), r.fiche_key))
    return out


# ---------------------------------------------------------------------------
# 1) Cycle de vie complet : ouverture → maintien → clôture → disparition
# ---------------------------------------------------------------------------

def test_cycle_de_vie_position(monkeypatch):
    monkeypatch.setattr(sa, "select_swing_retenus", _fake_select)

    # Jour 1 (30/06) : EUR/USD 1m SHORT entre au bloc Positions 1m.
    r1 = _res("eurusd", "EUR/USD", {"1m": "SHORT"}, {"1m"})
    state, evt1 = sa.compute_positions_ouvertes(
        [], [r1], {"eurusd": 1.13861}, _now("2026-06-30")
    )
    assert [p["fiche_key"] for p in evt1["opened"]] == ["eurusd"]
    assert evt1["maintained"] == [] and evt1["closed_today"] == []
    pos = state[0]
    assert pos["horizon"] == "1m" and pos["sens"] == "SHORT"
    assert pos["date_prise"] == "2026-06-30" and pos["prix_prise"] == 1.13861

    # Jour 1 — rendu : l'entrée est dans le TABLEAU 1m, PAS dans 📌 (bloc vide).
    assert sa.build_positions_ouvertes_block(evt1, {}, _now("2026-06-30")) == []

    # Jour 2 (01/07) : même sens → MAINTIEN, prix a baissé → % favorable positif.
    r2 = _res("eurusd", "EUR/USD", {"1m": "SHORT"}, {"1m"})
    state, evt2 = sa.compute_positions_ouvertes(
        state, [r2], {"eurusd": 1.130}, _now("2026-07-01")
    )
    assert [p["fiche_key"] for p in evt2["maintained"]] == ["eurusd"]
    assert evt2["opened"] == [] and evt2["closed_today"] == []
    bloc = "\n".join(sa.build_positions_ouvertes_block(evt2, {"eurusd": 1.130}, _now("2026-07-01")))
    assert "📌 Positions ouvertes" in bloc
    assert "EUR/USD" in bloc and "pris le 2026-06-30 à 1.13861" in bloc
    assert "tendance de fond intacte" in bloc
    assert "+0.76 %" in bloc  # SHORT + baisse = favorable positif

    # Jour 3 (02/07) : le sens se RETOURNE (LONG), l'actif sort du bloc → clôture
    # (✂️) une seule fois, sans ré-ouverture.
    r3 = _res("eurusd", "EUR/USD", {"1m": "LONG"}, set())
    state, evt3 = sa.compute_positions_ouvertes(
        state, [r3], {"eurusd": 1.120}, _now("2026-07-02")
    )
    assert [p["fiche_key"] for p in evt3["closed_today"]] == ["eurusd"]
    assert evt3["maintained"] == []
    bloc3 = "\n".join(sa.build_positions_ouvertes_block(evt3, {"eurusd": 1.120}, _now("2026-07-02")))
    assert "✂️" in bloc3 and "clôturée aujourd'hui" in bloc3 and "résultat +" in bloc3
    # La position clôturée ne reste PAS dans l'état (disparaît le lendemain).
    assert all(p["fiche_key"] != "eurusd" for p in state)

    # Jour 4 (03/07) : plus aucune position → aucun bloc, ✂️ a disparu.
    r4 = _res("eurusd", "EUR/USD", {"1m": "LONG"}, set())
    state, evt4 = sa.compute_positions_ouvertes(
        state, [r4], {"eurusd": 1.121}, _now("2026-07-03")
    )
    assert evt4["closed_today"] == [] and evt4["maintained"] == []
    assert sa.build_positions_ouvertes_block(evt4, {}, _now("2026-07-03")) == []


def test_retournement_dans_le_bloc_cloture_puis_reouvre(monkeypatch):
    """Retournement alors que l'actif RESTE dans le bloc au nouveau sens : l'ancienne
    position clôture (✂️) ET une nouvelle position s'ouvre au sens inverse (entrée
    du jour)."""
    monkeypatch.setattr(sa, "select_swing_retenus", _fake_select)
    r1 = _res("or", "Or", {"7j": "SHORT"}, {"7j"})
    state, _ = sa.compute_positions_ouvertes([], [r1], {"or": 4000.0}, _now("2026-06-30"))
    r2 = _res("or", "Or", {"7j": "LONG"}, {"7j"})
    state, evt = sa.compute_positions_ouvertes(state, [r2], {"or": 3950.0}, _now("2026-07-01"))
    assert [p["sens"] for p in evt["closed_today"]] == ["SHORT"]
    assert [p["sens"] for p in evt["opened"]] == ["LONG"]
    assert [(p["fiche_key"], p["sens"], p["date_prise"]) for p in state] == [
        ("or", "LONG", "2026-07-01")
    ]


# ---------------------------------------------------------------------------
# 2) Zéro réimpression : une position ouverte n'est PLUS dans le tableau d'entrée
# ---------------------------------------------------------------------------

def test_zero_reimpression_tableau_entree(monkeypatch):
    monkeypatch.setattr(sa, "select_swing_retenus", _fake_select)
    r = _res("eurusd", "EUR/USD", {"1m": "SHORT"}, {"1m"})

    # Sans exclusion : EUR/USD apparaît comme entrée (jour d'ouverture).
    t_ouverture = "\n".join(sa.build_positions_1m_block([r], fiches={}, now=_now("2026-06-30")))
    assert "EUR/USD" in t_ouverture

    # Avec exclusion (position déjà ouverte) : plus de ligne EUR/USD + message dédié.
    t_maintien = "\n".join(sa.build_positions_1m_block(
        [r], fiches={}, now=_now("2026-07-01"), exclude_fiche_keys={"eurusd"},
    ))
    assert "EUR/USD" not in t_maintien
    assert "Aucune nouvelle entrée aujourd'hui" in t_maintien
    assert "positions en cours ci-dessus" in t_maintien


def test_tableau_vide_sans_position_garde_message_neutre(monkeypatch):
    """Tableau vide SANS position ouverte → message « rien de jouable » d'origine
    (pas le message « positions en cours »)."""
    monkeypatch.setattr(sa, "select_swing_retenus", lambda results, H: [])
    txt = "\n".join(sa.build_positions_1m_block([], fiches={}, now=_now("2026-07-03")))
    assert "Aucune tendance 1m à conviction forte" in txt
    assert "positions en cours" not in txt


# ---------------------------------------------------------------------------
# 3) Sortie d'univers → clôture (pas de maintien fantôme)
# ---------------------------------------------------------------------------

def test_sortie_univers_cloture(monkeypatch):
    monkeypatch.setattr(sa, "select_swing_retenus", _fake_select)
    r1 = _res("or", "Or", {"7j": "SHORT"}, {"7j"})
    state, _ = sa.compute_positions_ouvertes([], [r1], {"or": 3988.0}, _now("2026-06-30"))
    # Jour suivant : l'actif n'est plus directionnel (INSUFFISANT) → clôture.
    r2 = _res("or", "Or", {"7j": "INSUFFISANT"}, set())
    _, evt = sa.compute_positions_ouvertes(state, [r2], {"or": 3950.0}, _now("2026-07-01"))
    assert [p["fiche_key"] for p in evt["closed_today"]] == ["or"]
    assert evt["closed_today"][0]["motif_cloture"] == "sortie"


# ---------------------------------------------------------------------------
# 4) Reconstruction initiale depuis decision-logs mockés + prix de prise
# ---------------------------------------------------------------------------

def _write_cell_log(path: Path, date: str, cells: list):
    lines = []
    for fk, actif, h, conc, cov, score in cells:
        lines.append(json.dumps({
            "record_type": "cellule", "bulletin_date": date, "fiche_key": fk,
            "actif": actif, "horizon": h, "conclusion_pm1": conc,
            "conclusion_pond": conc, "coverage": cov, "score_pm1": score,
            "quasi_neutre": False, "diverge": False, "mono_critere_dominant": False,
        }, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_reconstruction_depuis_logs(monkeypatch, tmp_path):
    dl = tmp_path / "decision-log"
    dl.mkdir()
    pe = tmp_path / "prix-emission"
    pe.mkdir()
    monkeypatch.setattr(sa, "PRIX_EMISSION_DIR", pe)

    # EUR/USD 1m SHORT présent le 30/06 et le 01/07 (conviction forte, cov OK).
    _write_cell_log(dl / "2026-06-30-0800.jsonl", "2026-06-30",
                    [("eurusd", "EUR/USD", "1m", "SHORT", 0.80, -25.0)])
    _write_cell_log(dl / "2026-07-01-0723.jsonl", "2026-07-01",
                    [("eurusd", "EUR/USD", "1m", "SHORT", 0.80, -22.0)])
    (pe / "2026-06-30-08h.json").write_text(json.dumps({"EUR=X": 1.13861}), encoding="utf-8")

    fiches = {"eurusd": {"ticker_principal": "EUR=X", "actif": "EUR/USD"}}
    pos = sa.reconstruct_positions_from_cell_logs(dl, _now("2026-07-03"), fiches=fiches)
    assert len(pos) == 1
    p = pos[0]
    assert p["fiche_key"] == "eurusd" and p["sens"] == "SHORT"
    assert p["date_prise"] == "2026-06-30"  # ancrée au 1er jour de présence
    assert p["prix_prise"] == 1.13861  # résolu depuis prix-emission du jour


def test_reconstruction_prix_introuvable_position_sans_montant(monkeypatch, tmp_path):
    """Prix-emission introuvable → position listée avec prix_prise=None (zéro
    invention), jamais de montant fabriqué."""
    dl = tmp_path / "decision-log"
    dl.mkdir()
    monkeypatch.setattr(sa, "PRIX_EMISSION_DIR", tmp_path / "vide")
    _write_cell_log(dl / "2026-06-30-0800.jsonl", "2026-06-30",
                    [("or", "Or", "7j", "SHORT", 0.80, -20.0)])
    pos = sa.reconstruct_positions_from_cell_logs(
        dl, _now("2026-07-01"), fiches={"or": {"ticker_principal": "GC=F"}}
    )
    assert len(pos) == 1 and pos[0]["prix_prise"] is None


# ---------------------------------------------------------------------------
# 5) Priorité état persisté vs bootstrap
# ---------------------------------------------------------------------------

def test_record_persiste_prioritaire_sur_bootstrap(tmp_path):
    dl = tmp_path / "decision-log"
    dl.mkdir()
    # Log par-cellule (bootstrap potentiel) + record d'état persisté de la veille.
    _write_cell_log(dl / "2026-07-01-0723.jsonl", "2026-07-01",
                    [("or", "Or", "7j", "SHORT", 0.80, -20.0)])
    persisted = {
        "record_type": "positions_ouvertes", "bulletin_date": "2026-07-02",
        "generated_at": "2026-07-02T18:00:00",
        "positions": [{"horizon": "1m", "fiche_key": "usdjpy", "actif": "USD/JPY",
                       "sens": "LONG", "date_prise": "2026-07-01", "prix_prise": 162.7}],
        "clotures_du_jour": [],
    }
    (dl / "2026-07-02-0723.jsonl").write_text(
        json.dumps(persisted, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    prev = sa.get_prev_positions_ouvertes(dl, _now("2026-07-03"))
    # On lit l'état persisté (usdjpy), PAS le bootstrap par-cellule (or).
    assert [p["fiche_key"] for p in prev] == ["usdjpy"]


def test_record_persiste_vide_bloque_bootstrap(tmp_path):
    """Un record d'état vide (veille sans position) est légitime → pas de bootstrap."""
    dl = tmp_path / "decision-log"
    dl.mkdir()
    _write_cell_log(dl / "2026-07-01-0723.jsonl", "2026-07-01",
                    [("or", "Or", "7j", "SHORT", 0.80, -20.0)])
    empty = {"record_type": "positions_ouvertes", "bulletin_date": "2026-07-02",
             "generated_at": "2026-07-02T18:00:00", "positions": [], "clotures_du_jour": []}
    (dl / "2026-07-02-0723.jsonl").write_text(
        json.dumps(empty, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    assert sa.get_prev_positions_ouvertes(dl, _now("2026-07-03")) == []


def test_read_last_state_ignore_jour_courant(tmp_path):
    """Le record du JOUR courant n'est pas relu comme « veille » (before_date strict)."""
    dl = tmp_path / "decision-log"
    dl.mkdir()
    rec = {"record_type": "positions_ouvertes", "bulletin_date": "2026-07-03",
           "generated_at": "2026-07-03T07:00:00",
           "positions": [{"horizon": "7j", "fiche_key": "x", "actif": "X",
                          "sens": "LONG", "date_prise": "2026-07-03", "prix_prise": 1.0}],
           "clotures_du_jour": []}
    (dl / "2026-07-03-0700.jsonl").write_text(
        json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    assert sa._read_last_positions_state(dl, before_date="2026-07-03") is None
