"""Onglet « Mouvements de marché » — historique FIGÉ + colonnes honnêtes.

Correctif fondateur 02/07 (audit variations-24h, 7 corrections) :
- points 1-2 : le mouvement de clôture d'un jour PASSÉ est figé (source datée), le
  filtre >1 % s'applique à cette valeur figée → deux générations successives (J et
  J+1, « prix courant » différent simulé par une cellule du jour courant qui dérive)
  donnent la MÊME table pour les jours passés ;
- point 1 : le jour COURANT (échéance 24h pas encore atteinte) est marqué « en cours » ;
- point 3 : « Max du jour » câblé sur la source datée du bilan (sortie-timing-log) ;
- point 4 : une même news ne peut expliquer qu'UN seul jour (dédup) ;
- point 5 : conviction = libellé + note (« forte (+8.77) ») ;
- point 6 : colonne « Résultat » (✅ / ❌ / ⚪) depuis l'outcome du measures-log.

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
NOW = datetime(2026, 7, 2, 7, 30, tzinfo=PARIS)


def _write_measures(path: Path, records):
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )


def _rec(actif, call, realized, *, bdate, ech, emis=100.0, max_gain=None, outcome=None):
    return {
        "actif": actif, "horizon": "24h", "conclusion": call,
        "realized_pct": realized, "prix_emission": emis,
        "prix_echeance": emis * (1 + realized / 100),
        "max_gain_pct": max_gain, "outcome": outcome,
        "echeance": ech.isoformat(), "bulletin_date": bdate.isoformat(),
    }


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "nope")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "nope2")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", tmp_path / "nost.jsonl")


def _row(md: str, needle: str) -> str:
    for line in md.splitlines():
        if line.startswith("|") and needle in line:
            return line
    raise AssertionError(f"ligne absente : {needle}\n{md}")


def test_jours_passes_figes_meme_table_a_j_et_jplus1(tmp_path, monkeypatch):
    """Points 1-2 : rejeu de la dérive prouvée. Le prix courant qui bouge (cellule
    du jour COURANT re-mesurée) ne change PAS les lignes des jours passés."""
    cafe = _rec("Café (Arabica)", "LONG", 8.52, bdate=date(2026, 6, 29), ech=date(2026, 6, 30))
    argent = _rec("Argent", "SHORT", -3.0, bdate=date(2026, 6, 27), ech=date(2026, 6, 28))
    # Génération à J = 01/07 : la cellule du jour courant (cacao, échéance 01/07) est
    # « en cours » et vaut +4.0 (mesure intermédiaire).
    log_a = tmp_path / "a.jsonl"
    _write_measures(log_a, [cafe, argent,
                            _rec("Cacao", "LONG", 4.0, bdate=date(2026, 7, 1), ech=date(2026, 7, 1))])
    # Génération à J+1 = 02/07 : la cellule 01/07 s'est FIGÉE à +6.0 (prix courant a
    # bougé), une NOUVELLE cellule courante 02/07 apparaît à +9.0.
    log_b = tmp_path / "b.jsonl"
    _write_measures(log_b, [cafe, argent,
                            _rec("Cacao", "LONG", 6.0, bdate=date(2026, 7, 1), ech=date(2026, 7, 1)),
                            _rec("Cacao", "LONG", 9.0, bdate=date(2026, 7, 2), ech=date(2026, 7, 2))])
    _isolate(monkeypatch, tmp_path)

    va = bj.variations_24h_significatives(measures_log_path=log_a,
                                          decision_log_dir=tmp_path / "dl", today=date(2026, 7, 1))
    vb = bj.variations_24h_significatives(measures_log_path=log_b,
                                          decision_log_dir=tmp_path / "dl", today=date(2026, 7, 2))
    md_a = bj.render_variations_24h(va, now=datetime(2026, 7, 1, 7, 30, tzinfo=PARIS))
    md_b = bj.render_variations_24h(vb, now=NOW)

    # Les jours PASSÉS sont IDENTIQUES entre les deux générations (aucune dérive).
    assert _row(md_a, "Café (Arabica)") == _row(md_b, "Café (Arabica)")
    assert _row(md_a, "Argent") == _row(md_b, "Argent")
    assert "+8.52%" in _row(md_b, "Café (Arabica)")


def test_jour_courant_marque_en_cours_passe_fige(tmp_path, monkeypatch):
    """Point 1 : la cellule dont l'échéance 24h n'est pas atteinte est « en cours » ;
    une cellule passée ne l'est jamais."""
    _isolate(monkeypatch, tmp_path)
    mlog = tmp_path / "m.jsonl"
    _write_measures(mlog, [
        _rec("Cacao", "LONG", 5.0, bdate=date(2026, 7, 2), ech=date(2026, 7, 2)),   # courant
        _rec("Café (Arabica)", "LONG", 8.52, bdate=date(2026, 6, 30), ech=date(2026, 7, 1)),  # passé
    ])
    vs = bj.variations_24h_significatives(measures_log_path=mlog,
                                          decision_log_dir=tmp_path / "dl", today=date(2026, 7, 2))
    md = bj.render_variations_24h(vs, now=NOW)
    assert "(en cours)" in _row(md, "Cacao")
    assert "(en cours)" not in _row(md, "Café (Arabica)")


def test_filtre_sur_valeur_figee_deterministe(tmp_path, monkeypatch):
    """Point 2 : le filtre >1 % s'applique au mouvement figé ; inclusion identique
    quel que soit `today` (aucune ligne qui apparaît/disparaît)."""
    _isolate(monkeypatch, tmp_path)
    mlog = tmp_path / "m.jsonl"
    _write_measures(mlog, [
        _rec("Or", "SHORT", -1.90, bdate=date(2026, 6, 29), ech=date(2026, 6, 30)),  # >1 %
        _rec("Blé", "SHORT", -0.5, bdate=date(2026, 6, 29), ech=date(2026, 6, 30)),  # <1 % exclu
    ])
    for t in (date(2026, 7, 1), date(2026, 7, 2)):
        vs = bj.variations_24h_significatives(measures_log_path=mlog,
                                              decision_log_dir=tmp_path / "dl", today=t)
        actifs = {v.actif for v in vs}
        assert "Or" in actifs
        assert "Blé" not in actifs


def test_max_du_jour_cable_sur_source_bilan(tmp_path, monkeypatch):
    """Point 3 : max_gain absent du measures-log → câblé depuis sortie-timing-log
    (même source datée que le bilan) au lieu de rester « — »."""
    monkeypatch.setattr(bj, "SUIVI_TRACKING_DIR", tmp_path / "nope")
    monkeypatch.setattr(bj, "SUIVI_SNAPSHOT_DIR", tmp_path / "nope2")
    stl = tmp_path / "sortie-timing-log.jsonl"
    stl.write_text(json.dumps({
        "date": date(2026, 6, 29).isoformat(), "actif": "Cacao", "call": "LONG",
        "cloture_pct": 1.86, "max_gain_pct": 4.12,
    }) + "\n", encoding="utf-8")
    monkeypatch.setattr(bj, "SORTIE_TIMING_LOG", stl)
    mlog = tmp_path / "m.jsonl"
    _write_measures(mlog, [_rec("Cacao", "LONG", 1.86,
                                bdate=date(2026, 6, 29), ech=date(2026, 6, 30), max_gain=None)])
    v = bj.variations_24h_significatives(measures_log_path=mlog,
                                         decision_log_dir=tmp_path / "dl", today=date(2026, 7, 2))[0]
    assert v.max_jour == 4.12   # câblé depuis le bilan, plus « — »


def test_dedup_raison_une_seule_fois(tmp_path, monkeypatch):
    """Point 4 : une même news (titre quasi identique) ne sert de raison que sur le
    jour le plus récent où elle apparaît ; les jours plus anciens → « non identifiée »."""
    _isolate(monkeypatch, tmp_path)
    TITRE = "World Gold Council survey reports central bank gold purchases"

    def _fake_cause(actif, d, sens, *a, **k):
        return TITRE + (" averaging 1,000 tonnes annually" if d == date(2026, 6, 26)
                        else " per year")
    monkeypatch.setattr(bj, "cause_news_high_dir", _fake_cause)
    mlog = tmp_path / "m.jsonl"
    _write_measures(mlog, [
        _rec("Or", "SHORT", -2.0, bdate=date(2026, 6, 25), ech=date(2026, 6, 26)),
        _rec("Or", "SHORT", -2.0, bdate=date(2026, 6, 26), ech=date(2026, 6, 29)),
    ])
    vs = {v.jour: v for v in bj.variations_24h_significatives(
        measures_log_path=mlog, decision_log_dir=tmp_path / "dl", today=date(2026, 7, 2))}
    assert vs[date(2026, 6, 26)].raison is not None      # jour le plus récent : gardé
    assert vs[date(2026, 6, 25)].raison is None          # jour plus ancien : dédupliqué


def test_conviction_libelle_et_note(tmp_path, monkeypatch):
    """Point 5 : « forte (+8.77) » via le libellé du decision-log ; note brute seule
    si le libellé est absent des vieux logs."""
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(bj, "_load_score_fort_seuil", lambda *a, **k: 0.6)
    dldir = tmp_path / "dl"
    dldir.mkdir()
    (dldir / "2026-06-29-07h.jsonl").write_text(json.dumps({
        "bulletin_date": "2026-06-29", "actif": "Café (Arabica)", "horizon": "24h",
        "score_pm1": 8.77,
    }) + "\n", encoding="utf-8")
    mlog = tmp_path / "m.jsonl"
    _write_measures(mlog, [_rec("Café (Arabica)", "LONG", 5.91,
                                bdate=date(2026, 6, 29), ech=date(2026, 6, 30))])
    vs = bj.variations_24h_significatives(measures_log_path=mlog,
                                          decision_log_dir=dldir, today=date(2026, 7, 2))
    md = bj.render_variations_24h(vs, now=NOW)
    assert "forte (+8.77)" in _row(md, "Café (Arabica)")


def test_verdict_colonne_outcome(tmp_path, monkeypatch):
    """Point 6 : « Résultat » = ✅ (VRAI) / ❌ (FAUSSE) / ⚪ (non-conclusif) / — (non mesuré)."""
    _isolate(monkeypatch, tmp_path)
    mlog = tmp_path / "m.jsonl"
    _write_measures(mlog, [
        _rec("Café (Arabica)", "LONG", 5.91, bdate=date(2026, 6, 29), ech=date(2026, 6, 30), outcome="VRAI"),
        _rec("Or", "SHORT", 2.16, bdate=date(2026, 6, 29), ech=date(2026, 6, 30), outcome="FAUSSE"),
        _rec("Coton", "SHORT", 1.79, bdate=date(2026, 6, 29), ech=date(2026, 6, 30), outcome="non-conclusif"),
        _rec("Blé", "SHORT", -3.01, bdate=date(2026, 6, 29), ech=date(2026, 6, 30), outcome=None),
    ])
    md = bj.render_variations_24h(
        bj.variations_24h_significatives(measures_log_path=mlog,
                                         decision_log_dir=tmp_path / "dl", today=date(2026, 7, 2)),
        now=NOW)
    assert "✅" in _row(md, "Café (Arabica)")
    assert "❌" in _row(md, "Or")
    assert "⚪" in _row(md, "Coton")
    # Blé : outcome None → « — » dans la colonne Résultat (avant-dernière).
    assert _row(md, "Blé").split("|")[-2].strip() != "✅"
    assert "Résultat" in md
