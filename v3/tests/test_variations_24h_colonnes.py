"""Onglet « Mouvements de marché » enrichi (demande fondateur 25/06).

Couvre :
- nouvelles colonnes du tableau (prix d'entrée, % 12h / 18h / clôture favorable,
  Max du jour, Call, Joué) et disparition des anciennes (Sens, Prix sortie) ;
- convention de signe FAVORABLE (LONG = realized brut ; SHORT = -realized) ;
- réutilisation des relevés suivi (suivi-tracking + delta-snapshot 12h) SANS
  re-dérivation, avec concordance de call ;
- zéro invention : jour sans relevé 12h/18h → « — » ;
- cohérence avec le Bilan du jour : un même actif a les mêmes % 12h / 18h /
  clôture dans la page Mouvements et dans le tracking lu par le bilan.

Tous les chemins sont injectés en tmp_path → zéro réseau, zéro pollution data/.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bilan_jour as bj  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
ECH = date(2026, 6, 24)
BDATE = date(2026, 6, 23)


def _write_measures(path: Path, records):
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def _rec(actif, call, realized, *, emis=100.0, ech_prix=None, max_gain=None):
    return {
        "actif": actif, "horizon": "24h", "conclusion": call,
        "realized_pct": realized, "prix_emission": emis,
        "prix_echeance": ech_prix if ech_prix is not None else emis * (1 + realized / 100),
        "max_gain_pct": max_gain,
        "echeance": ECH.isoformat(), "bulletin_date": BDATE.isoformat(),
    }


def test_favorable_loader_tracking_prioritaire(tmp_path):
    """suivi-tracking (fav% signé, call vérifié) = source 12h ET 18h."""
    tdir = tmp_path / "suivi-tracking"
    tdir.mkdir()
    (tdir / f"{ECH.isoformat()}.json").write_text(json.dumps({
        "12h": {"Argent": {"call": "SHORT", "fav_pct": 1.99}},
        "18h": {"Argent": {"call": "SHORT", "fav_pct": 4.17}},
    }), encoding="utf-8")
    p12, p18 = bj.load_perf_intraday_favorable(
        ECH, "Argent", "SHORT", tracking_dir=tdir, snapshot_dir=tmp_path / "vide"
    )
    assert p12 == 1.99
    assert p18 == 4.17


def test_favorable_loader_call_discordant_ignore(tmp_path):
    """Un relevé d'un call opposé est ignoré (zéro invention, comme le bilan)."""
    tdir = tmp_path / "suivi-tracking"
    tdir.mkdir()
    (tdir / f"{ECH.isoformat()}.json").write_text(json.dumps({
        "12h": {"Argent": {"call": "LONG", "fav_pct": 1.99}},
    }), encoding="utf-8")
    p12, p18 = bj.load_perf_intraday_favorable(
        ECH, "Argent", "SHORT", tracking_dir=tdir, snapshot_dir=tmp_path / "vide"
    )
    assert p12 is None and p18 is None


def test_favorable_loader_fallback_snapshot_brut(tmp_path):
    """Hors Sélection : delta BRUT du snapshot 12h × signe du call = favorable."""
    sdir = tmp_path / "suivi"
    sdir.mkdir()
    # Delta brut -1.99 (le prix a baissé). Call SHORT → favorable +1.99.
    (sdir / f"{ECH.isoformat()}-12h.json").write_text(
        json.dumps({"Argent": -1.99}), encoding="utf-8"
    )
    p12, p18 = bj.load_perf_intraday_favorable(
        ECH, "Argent", "SHORT", tracking_dir=tmp_path / "vide", snapshot_dir=sdir
    )
    assert p12 == 1.99   # -1.99 brut × -1 (SHORT) = +1.99 favorable
    assert p18 is None    # aucun snapshot 18h « tous actifs » → pas inventé


def test_favorable_loader_aucun_snapshot(tmp_path):
    """Jour historique sans relevé → (None, None), jamais inventé depuis la clôture."""
    p12, p18 = bj.load_perf_intraday_favorable(
        ECH, "Or", "SHORT", tracking_dir=tmp_path / "x", snapshot_dir=tmp_path / "y"
    )
    assert p12 is None and p18 is None


def test_cloture_favorable_signe(tmp_path, monkeypatch):
    """% clôture = realized brut converti en favorable (LONG +, SHORT inversé)."""
    mlog = tmp_path / "measures-log.jsonl"
    _write_measures(mlog, [
        _rec("Cacao", "LONG", 7.67),     # LONG hausse → favorable +7.67
        _rec("Argent", "SHORT", -7.82),  # SHORT baisse → favorable +7.82
        _rec("CAC 40", "SHORT", 1.5),    # SHORT hausse → favorable -1.50 (perdu)
    ])
    monkeypatch.setattr(bj, "MEASURES_LOG_FILE", mlog)
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "nope")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "nope2")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", tmp_path / "nost.jsonl")
    vs = {v.actif: v for v in bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl"
    )}
    assert vs["Cacao"].perf_cloture_fav == 7.67
    assert vs["Argent"].perf_cloture_fav == 7.82
    assert vs["CAC 40"].perf_cloture_fav == -1.5


def test_render_nouvelles_colonnes(tmp_path, monkeypatch):
    """Le markdown rendu porte les nouvelles colonnes, pas les anciennes."""
    mlog = tmp_path / "measures-log.jsonl"
    _write_measures(mlog, [_rec("Cacao", "LONG", 7.67, emis=4620.96, max_gain=8.03)])
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "nope")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "nope2")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", tmp_path / "nost.jsonl")
    vs = bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl"
    )
    md = bj.render_variations_24h(vs, now=datetime(2026, 6, 24, 22, 15, tzinfo=PARIS))
    # En-tête enrichi.
    assert "Prix d'entrée" in md
    assert "% 12h" in md and "% 18h" in md and "% clôture" in md
    assert "Max du jour" in md
    assert "Call" in md
    # Anciennes colonnes retirées.
    assert "Prix sortie" not in md
    assert "Prix départ" not in md
    # Valeurs : prix d'entrée, clôture favorable (+7.67), max (+8.03).
    assert "4621" in md  # 4620.96 formaté .4g
    assert "+7.67%" in md
    assert "+8.03%" in md


def test_max_du_jour_absent_reste_tiret(tmp_path, monkeypatch):
    """max_gain_pct None (anciens records) → « — », jamais inventé."""
    mlog = tmp_path / "measures-log.jsonl"
    _write_measures(mlog, [_rec("Or", "SHORT", -1.86, max_gain=None)])
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "nope")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "nope2")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", tmp_path / "nost.jsonl")
    vs = bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl"
    )
    assert vs[0].max_jour is None


def test_coherence_avec_bilan_meme_chiffres(tmp_path, monkeypatch):
    """Cohérence : % 12h / 18h / clôture / max de la page Mouvements == ce que le
    bilan affiche (mêmes sources persistées). Reproduit Argent 24/06 (validé Thomas :
    12h +1.99 · 18h +4.17 · clôture +6.54 · max +9.24)."""
    mlog = tmp_path / "measures-log.jsonl"
    _write_measures(mlog, [_rec("Argent", "SHORT", -7.815992, emis=62.30, max_gain=9.24)])
    tdir = tmp_path / "suivi-tracking"
    tdir.mkdir()
    # Relevés EXACTS du tracking 24/06 (fav% signé) — la source 12h/18h du bilan.
    (tdir / f"{ECH.isoformat()}.json").write_text(json.dumps({
        "12h": {"Argent": {"call": "SHORT", "fav_pct": 1.99}},
        "18h": {"Argent": {"call": "SHORT", "fav_pct": 4.17}},
    }), encoding="utf-8")
    # Clôture EXACTE du bilan (sortie-timing-log, réf. ouverture→clôture = +6.54).
    stl = tmp_path / "sortie-timing-log.jsonl"
    stl.write_text(json.dumps({
        "date": ECH.isoformat(), "actif": "Argent", "call": "SHORT",
        "cloture_pct": 6.54, "pic_pct": 6.54, "pic_heure": "clôture",
    }) + "\n", encoding="utf-8")
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tdir)
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "nope")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", stl)
    v = bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl"
    )[0]
    # TOUS les chiffres matchent le bilan (12h/18h/clôture/max), pas seulement 12h/18h.
    assert v.perf_12h == 1.99
    assert v.perf_18h == 4.17
    assert v.perf_cloture_fav == 6.54   # clôture EXACTE du bilan (pas re-dérivée)
    assert v.max_jour == 9.24


def test_cloture_fallback_realized_si_pas_de_bilan(tmp_path, monkeypatch):
    """Hors Sélection / historique : pas de sortie-timing → clôture = realized fav."""
    mlog = tmp_path / "measures-log.jsonl"
    _write_measures(mlog, [_rec("Pétrole (Brent)", "SHORT", -4.30)])
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "x")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "y")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", tmp_path / "z.jsonl")
    v = bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl"
    )[0]
    assert v.perf_cloture_fav == 4.30   # -4.30 brut × -1 (SHORT) = +4.30 favorable


def test_cloture_bilan_call_discordant_ignore(tmp_path, monkeypatch):
    """Un sortie-timing au call opposé est ignoré → fallback realized (zéro invention)."""
    mlog = tmp_path / "measures-log.jsonl"
    _write_measures(mlog, [_rec("Argent", "SHORT", -7.82)])
    stl = tmp_path / "sortie-timing-log.jsonl"
    stl.write_text(json.dumps({
        "date": ECH.isoformat(), "actif": "Argent", "call": "LONG", "cloture_pct": 6.54,
    }) + "\n", encoding="utf-8")
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "x")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "y")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", stl)
    v = bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl"
    )[0]
    assert v.perf_cloture_fav == 7.82   # call discordant → réutilise realized, pas 6.54
