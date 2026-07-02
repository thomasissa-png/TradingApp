"""C7 — LOT 6 : transparence à la publication + mesure flip vs continuation.

Tests pour les 2 livrables additifs (FLAG/MESURE, zéro changement des
conclusions/scores/seuils) :

LIVRABLE 1 — scoring_analyste.render_bulletin
  (a) Bloc « ⚠️ Cellules à surveiller » en tête (après briefing)
      - liste les cellules portant ≥ 1 drapeau de risque
      - « Aucune cellule à risque ce cycle » sinon
  (b) Cohérence biais agrégé ↔ détail (assertion testable, log ERROR si bug)

LIVRABLE 2 — journaliste.compute_kpi + compute_kpi_ab + render_performance
  - is_flip : True (sens changé), False (continuation), None (pas de précédent)
  - ventilation taux_flip / taux_continuation par cellule (avec N)
  - taux global existant INCHANGÉ
"""

from __future__ import annotations

import logging
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402
import journaliste as jr  # noqa: E402


# ===========================================================================
# Helpers scoring (alignés sur test_fix_news_flag_and_coinflip)
# ===========================================================================

def _fiche(quant_signe: int = 1, news_signe: int = 1,
           quant_poids: int = 10, news_poids: int = 10) -> dict:
    return {
        "actif": "TestActif",
        "criteres": [
            {
                "id": 1, "nom": "Quant",
                "cle_courante": "quant", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 1.0,
                "signe": quant_signe, "poids": quant_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
            {
                "id": 2, "nom": "News",
                "cle_courante": "news", "normalisation": "triplet",
                "cap": 1.0, "signe": news_signe, "poids": news_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _vals(quant_val: float, news_val: float,
          mat: str = "medium", rel: str = "confirmed") -> dict:
    return {
        "quant": {"valeur": quant_val, "source_track": "twelvedata"},
        "news": {
            "valeur": news_val, "source_track": "ia_synthese",
            "materiality": mat, "reliability": rel,
        },
    }


NOW = datetime(2026, 6, 2, 9, 0, tzinfo=timezone.utc)


# ===========================================================================
# LIVRABLE 1 (a) — Bloc « ⚠️ Cellules à surveiller »
# ===========================================================================

def test_surveillance_block_present_avec_titre():
    """Le bloc est présent dans le bulletin, même quand vide."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "## ⚠️ Cellules à surveiller" in bulletin


def test_surveillance_block_placeholder_si_aucune_cellule_a_risque():
    """Aucune cellule flaggée → ligne placeholder explicite."""
    # A1 (audit 05/06) : pour éviter le ◧ mono-critère (qui se déclenche si 1
    # critère porte >50% du score), on utilise une fiche à 2 critères quant de
    # contributions ÉGALES (50/50) → ni mono-critère, ni autre alerte.
    fiche = {
        "actif": "TestActif",
        "criteres": [
            {"id": 1, "nom": "QuantA", "cle_courante": "qa", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 1.0, "signe": 1, "poids": 10,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 2, "nom": "QuantB", "cle_courante": "qb", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 1.0, "signe": 1, "poids": 10,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
        ],
    }
    vals = {"qa": {"valeur": 0.5, "source_track": "twelvedata"},
            "qb": {"valeur": 0.5, "source_track": "twelvedata"}}
    res = sa.score_actif("test", fiche, vals)
    # Force confidence normale (coverage = 1.0 sur 2 critères valides).
    # Force pas d'incohérence inter-horizons, pas de denial, etc.
    res.divergence_quant_news = {h: False for h in sa.HORIZONS}
    res.contre_momentum = {h: False for h in sa.HORIZONS}
    res.incoherence_inter_horizons = False
    res.confidence = {h: "normale" for h in sa.HORIZONS}
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "_Aucune cellule à risque directionnel ce cycle._" in bulletin


def test_surveillance_block_divergence_hors_selection_non_listee():
    """[Règle 01/07, GO fondateur] La surveillance est RÉDUITE aux paris de la
    Sélection du jour et aux flips. Une cellule avec ↯ qui n'est NI dans la
    Sélection NI en flip n'est plus listée (le détail complet reste au
    decision-log, et l'intro le dit)."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    # Force divergence 24h
    res.divergence_quant_news = {"24h": True, "7j": False, "1m": False}
    res.contre_momentum = {h: False for h in sa.HORIZONS}
    res.incoherence_inter_horizons = False
    res.confidence = {h: "normale" for h in sa.HORIZONS}
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    # On extrait la section surveillance
    section = bulletin.split("## ⚠️ Cellules à surveiller", 1)[1].split("##", 1)[0]
    # Hors Sélection et hors flip → non listée malgré le ↯.
    assert "TestActif 24h" not in section
    # L'intro explique la réduction et renvoie au decision-log.
    assert "Sélection du jour" in section
    assert "decision-log" in section


def test_surveillance_block_exclut_insuffisant():
    """#5.2 — Cellule INSUFFISANT → EXCLUE de la surveillance (déjà listée dans
    sa propre sous-table 🚫). Même avec un flag directionnel co-présent, une
    cellule non-directionnelle (INSUFFISANT) n'est jamais 'à surveiller'."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    # Force conclusion insuffisant + une divergence (qui ne doit PAS la faire remonter)
    res.conclusions = {h: sa.CONCLUSION_INSUFFISANT for h in sa.HORIZONS}
    res.confidence = {h: "insuffisant" for h in sa.HORIZONS}
    res.divergence_quant_news = {h: True for h in sa.HORIZONS}
    res.contre_momentum = {h: False for h in sa.HORIZONS}
    res.incoherence_inter_horizons = False
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    section = bulletin.split("## ⚠️ Cellules à surveiller", 1)[1].split("##", 1)[0]
    # Aucune ligne INSUFFISANT dans la surveillance → placeholder
    assert "_Aucune cellule à risque directionnel ce cycle._" in section
    assert "TestActif 24h" not in section


def test_surveillance_block_contre_momentum_hors_selection_non_liste():
    """[Règle 01/07, GO fondateur] Même contrat que la divergence : le ⇄ d'une
    cellule hors Sélection/flips n'est plus listé dans la surveillance (il reste
    visible dans la Synthèse et au decision-log)."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    res.contre_momentum = {"7j": True, "24h": False, "1m": False}
    res.divergence_quant_news = {h: False for h in sa.HORIZONS}
    res.incoherence_inter_horizons = False
    res.confidence = {h: "normale" for h in sa.HORIZONS}
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    section = bulletin.split("## ⚠️ Cellules à surveiller", 1)[1].split("##", 1)[0]
    assert "TestActif 7j" not in section
    assert "decision-log" in section


def test_surveillance_block_apparait_avant_flips():
    """Ordre (I14) : « Cellules à surveiller » remonte JUSTE après la tête « 🎯
    Aujourd'hui », donc AVANT la Synthèse. Elle reste avant « Flips vs veille » puis
    « Détail par actif ». La table '## Matrice' a été fusionnée dans '## Synthèse des
    décisions' (#4.2)."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    idx_decision = bulletin.index("## 🎯 Aujourd'hui")
    idx_synthese = bulletin.index("## Synthèse des décisions")
    idx_surveillance = bulletin.index("## ⚠️ Cellules à surveiller")
    idx_flips = bulletin.index("## Flips vs veille")
    idx_detail = bulletin.index("## Détail par actif")
    # Décision → Surveillance → Synthèse, puis Surveillance toujours avant Flips/Détail.
    assert idx_decision < idx_surveillance < idx_synthese
    assert idx_surveillance < idx_flips < idx_detail
    # Plus de table '## Matrice' séparée (fusionnée dans la synthèse)
    assert "## Matrice" not in bulletin


# ===========================================================================
# LIVRABLE 1 (b) — Cohérence biais agrégé
# ===========================================================================

def test_bias_aggregate_compte_correctement():
    """compute_bias_aggregate compte les conclusions par sens."""
    fiche = _fiche()
    res_long = sa.score_actif("long_act", fiche, _vals(1.0, 1.0))     # → LONG/LONG/LONG
    res_short = sa.score_actif("short_act", fiche, _vals(-1.0, -1.0)) # → SHORT/SHORT/SHORT
    agg = sa.compute_bias_aggregate([res_long, res_short])
    assert agg["total"] == 6
    # 3 conclusions LONG + 3 SHORT (3 horizons × 2 actifs)
    assert agg["LONG"] + agg["SHORT"] + agg[sa.CONCLUSION_INSUFFISANT] == 6


def test_bias_coherence_ok_quand_cohérent():
    """assert_bias_coherence retourne (True, '') quand l'agrégat = recount."""
    fiche = _fiche()
    res = sa.score_actif("a", fiche, _vals(1.0, 1.0))
    agg = sa.compute_bias_aggregate([res])
    ok, msg = sa.assert_bias_coherence(agg, [res])
    assert ok is True
    assert msg == ""


def test_bias_coherence_detecte_incoherence(caplog):
    """Agrégat falsifié → detection KO + log ERROR + marqueur de message."""
    fiche = _fiche()
    res = sa.score_actif("a", fiche, _vals(1.0, 1.0))
    # On injecte un agrégat manifestement faux
    fake_agg = {"LONG": 999, "SHORT": 0, sa.CONCLUSION_INSUFFISANT: 0, "total": 999}
    with caplog.at_level(logging.ERROR, logger="scoring_analyste"):
        ok, msg = sa.assert_bias_coherence(fake_agg, [res])
    assert ok is False
    assert "INCOHÉRENCE BIAIS" in msg
    assert any("INCOHÉRENCE BIAIS" in r.message for r in caplog.records)


def test_bulletin_ne_contient_plus_ligne_biais_agrege():
    """[Couper le gras — fondateur 25/06] La ligne « Biais agrégé » est SUPPRIMÉE du
    bulletin (gras non actionnable, redondant avec la synthèse 12×3). La cohérence de
    biais reste vérifiée en interne (cf. test_assert_bias_coherence ci-dessus)."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "Biais agrégé" not in bulletin


def test_bulletin_pas_de_marqueur_incoherence_par_defaut():
    """Cas nominal : pas de marqueur INCOHÉRENCE dans le bulletin."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    bulletin = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "INCOHÉRENCE" not in bulletin


# ===========================================================================
# LIVRABLE 2 — is_flip + ventilation flip/continuation (journaliste)
# ===========================================================================

def _make_measure(
    outcome: str,
    conc: str = "LONG",
    score: float = 1.0,
    echeance: date = date(2026, 5, 2),
    is_flip=None,
    outcome_pond=None,
    conclusion_pond=None,
    score_pond=None,
) -> jr.Measure:
    cell = jr.BulletinCell(
        bulletin_date=echeance - timedelta(days=1),
        actif_name="Pétrole (Brent)",
        horizon="24h",
        conclusion=conc,
        score=score,
        conclusion_pond=conclusion_pond,
        score_pond=score_pond,
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
        is_flip=is_flip,
        outcome_pond=outcome_pond,
    )


def test_measure_dataclass_has_is_flip_field():
    """Le champ is_flip existe et default = None."""
    m = _make_measure(jr.OUTCOME_VRAI)
    assert hasattr(m, "is_flip")
    assert m.is_flip is None


def test_compute_kpi_ventilation_flip_vs_continuation_simple():
    """3 flips (2 vrai, 1 fausse) + 5 continuations (3 vrai, 2 fausse).

    taux_flip = 2/3 = 66.67 ; taux_continuation = 3/5 = 60.0.
    Taux global = 5/8 = 62.5 (inchangé).
    """
    ms = []
    base = date(2026, 1, 1)
    for i in range(2):
        ms.append(_make_measure(jr.OUTCOME_VRAI, is_flip=True,
                                echeance=base + timedelta(days=i)))
    ms.append(_make_measure(jr.OUTCOME_FAUSSE, is_flip=True,
                            echeance=base + timedelta(days=2)))
    for i in range(3):
        ms.append(_make_measure(jr.OUTCOME_VRAI, is_flip=False,
                                echeance=base + timedelta(days=10 + i)))
    for i in range(2):
        ms.append(_make_measure(jr.OUTCOME_FAUSSE, is_flip=False,
                                echeance=base + timedelta(days=20 + i)))
    k = jr.compute_kpi(ms)
    # Global inchangé
    assert k.n_vrai == 5
    assert k.n_fausse == 3
    assert k.taux_pct == pytest.approx(62.5)
    # Ventilation
    assert k.n_flip == 3
    assert k.n_vrai_flip == 2
    assert k.taux_flip == pytest.approx(66.67)
    assert k.n_continuation == 5
    assert k.n_vrai_continuation == 3
    assert k.taux_continuation == pytest.approx(60.0)


def test_compute_kpi_is_flip_none_exclu_des_deux_taux():
    """Mesures is_flip=None : NE comptent ni dans flip ni dans continuation."""
    ms = []
    base = date(2026, 1, 1)
    # 2 vrai is_flip=None (devraient être exclus des deux taux)
    for i in range(2):
        ms.append(_make_measure(jr.OUTCOME_VRAI, is_flip=None,
                                echeance=base + timedelta(days=i)))
    # 1 vrai is_flip=True
    ms.append(_make_measure(jr.OUTCOME_VRAI, is_flip=True,
                            echeance=base + timedelta(days=5)))
    # 1 fausse is_flip=False
    ms.append(_make_measure(jr.OUTCOME_FAUSSE, is_flip=False,
                            echeance=base + timedelta(days=10)))
    k = jr.compute_kpi(ms)
    assert k.n_flip == 1
    assert k.n_vrai_flip == 1
    assert k.taux_flip == pytest.approx(100.0)
    assert k.n_continuation == 1
    assert k.n_vrai_continuation == 0
    assert k.taux_continuation == pytest.approx(0.0)
    # Global inclut les 4 mesures
    assert k.n_vrai == 3
    assert k.n_fausse == 1


def test_compute_kpi_taux_flip_none_si_aucun_flip():
    """Aucun flip → taux_flip reste None (zéro division évitée)."""
    ms = [_make_measure(jr.OUTCOME_VRAI, is_flip=False,
                        echeance=date(2026, 1, 1))]
    k = jr.compute_kpi(ms)
    assert k.n_flip == 0
    assert k.taux_flip is None
    assert k.n_continuation == 1
    assert k.taux_continuation == pytest.approx(100.0)


def test_compute_kpi_global_inchange_par_ventilation():
    """Vérifie que la ventilation n'altère PAS le taux/Brier global."""
    ms = []
    base = date(2026, 1, 1)
    for i in range(21):
        ms.append(_make_measure(jr.OUTCOME_VRAI, is_flip=None,
                                echeance=base + timedelta(days=i)))
    for i in range(9):
        ms.append(_make_measure(jr.OUTCOME_FAUSSE, is_flip=None,
                                echeance=base + timedelta(days=21 + i)))
    k = jr.compute_kpi(ms)
    # 21/30 = 70% (test_compute_kpi_eligible_actif_70_pct existant)
    assert k.taux_pct == pytest.approx(70.0)
    assert k.statut == "éligible_actif"
    # Aucune ventilation possible
    assert k.n_flip == 0
    assert k.n_continuation == 0


def test_compute_kpi_ab_ventilation_pond():
    """compute_kpi_ab ventile aussi côté pondéré."""
    ms = []
    base = date(2026, 1, 1)
    # 2 flips ±1 VRAI, pondéré aussi VRAI
    for i in range(2):
        ms.append(_make_measure(
            jr.OUTCOME_VRAI, conc="LONG",
            is_flip=True,
            outcome_pond=jr.OUTCOME_VRAI,
            conclusion_pond="LONG", score_pond=1.0,
            echeance=base + timedelta(days=i),
        ))
    # 1 continuation FAUSSE ±1 ; pondéré FAUSSE
    ms.append(_make_measure(
        jr.OUTCOME_FAUSSE, conc="LONG",
        is_flip=False,
        outcome_pond=jr.OUTCOME_FAUSSE,
        conclusion_pond="LONG", score_pond=1.0,
        echeance=base + timedelta(days=10),
    ))
    k = jr.compute_kpi_ab(ms)
    # Global inchangé
    assert k.taux_pm1 == pytest.approx(2 / 3 * 100, abs=0.01)
    assert k.taux_pond == pytest.approx(2 / 3 * 100, abs=0.01)
    # Ventilation pm1
    assert k.n_flip_pm1 == 2
    assert k.n_vrai_flip_pm1 == 2
    assert k.taux_flip_pm1 == pytest.approx(100.0)
    assert k.n_continuation_pm1 == 1
    assert k.taux_continuation_pm1 == pytest.approx(0.0)
    # Ventilation pond
    assert k.n_flip_pond == 2
    assert k.taux_flip_pond == pytest.approx(100.0)
    assert k.n_continuation_pond == 1
    assert k.taux_continuation_pond == pytest.approx(0.0)


# ===========================================================================
# is_flip — détection via comparaison bulletins (intégration measure())
# ===========================================================================

def _write_min_bulletin(path: Path, bdate: date,
                       conclusions_by_actif: dict) -> None:
    """Écrit un bulletin minimaliste parsable par parse_bulletin.

    `conclusions_by_actif` = {actif_name: {"24h": "LONG", "7j": "SHORT", ...}}
    """
    lines = [f"# Bulletin Analyste — {bdate.isoformat()}", ""]
    lines.append("| Actif | 24h | 7j | 1m |")
    lines.append("|---|---|---|---|")
    for actif, hh in conclusions_by_actif.items():
        c24 = hh.get("24h", "LONG")
        c7 = hh.get("7j", "LONG")
        c1 = hh.get("1m", "LONG")
        lines.append(
            f"| {actif} | {c24} (+1.00) | {c7} (+1.00) | {c1} (+1.00) |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def test_is_flip_detecte_changement_de_sens(tmp_path, monkeypatch):
    """Bulletin J-1 LONG → J SHORT : is_flip=True sur la mesure J-1 (la cellule
    de J n'est pas mesurée si l'échéance n'est pas atteinte ; on regarde la
    cellule de J-1 qui n'a PAS de bulletin précédent → is_flip=None ; et celle
    de J-2 → précédent = J-3 etc.). On vérifie plutôt sur 3 bulletins :
    J-2 LONG, J-1 SHORT (flip), J=today (continuation) → mesures à today
    pour 24h émis à J-2 et J-1.
    """
    # Construction : 3 bulletins consécutifs
    bdir = tmp_path / "bulletins"
    bdir.mkdir()
    today = date(2026, 6, 5)
    d1 = today - timedelta(days=3)  # J-3 LONG (référence pour J-2)
    d2 = today - timedelta(days=2)  # J-2 LONG (continuation : pas de flip vs J-3)
    d3 = today - timedelta(days=1)  # J-1 SHORT (flip vs J-2)
    _write_min_bulletin(bdir / f"bulletin-{d1.isoformat()}.md", d1,
                        {"Pétrole (Brent)": {"24h": "LONG", "7j": "LONG", "1m": "LONG"}})
    _write_min_bulletin(bdir / f"bulletin-{d2.isoformat()}.md", d2,
                        {"Pétrole (Brent)": {"24h": "LONG", "7j": "LONG", "1m": "LONG"}})
    _write_min_bulletin(bdir / f"bulletin-{d3.isoformat()}.md", d3,
                        {"Pétrole (Brent)": {"24h": "SHORT", "7j": "LONG", "1m": "LONG"}})

    # prix-emission : on stamp un prix 100 pour chacun
    pedir = tmp_path / "prix-emission"
    pedir.mkdir()
    import json as _json
    for d in (d1, d2, d3):
        (pedir / f"{d.isoformat()}.json").write_text(
            _json.dumps({"BZ=F": 100.0}), encoding="utf-8"
        )

    # fiche pétrole minimale
    fiches = {
        "petrole": {
            "actif": "Pétrole (Brent)",
            "ticker_principal": "BZ=F",
            "seuils_reussite_pct": {"24h": 1.0, "7j": 2.0, "1m": 4.0},
        }
    }

    # fetch_price stub
    def stub_price(ticker):
        return 102.0  # LONG +2% → VRAI si conclusion=LONG, FAUSSE si SHORT

    measures, _ = jr.measure(
        today=today, bulletins_dir=bdir, prix_emission_dir=pedir,
        fiches=fiches, fetch_price=stub_price,
    )
    # On cherche les mesures 24h pour chaque bulletin
    by_date = {m.cell.bulletin_date: m for m in measures if m.horizon == "24h"}
    assert d1 in by_date
    assert d2 in by_date
    assert d3 in by_date
    # d1 : pas de précédent → None
    assert by_date[d1].is_flip is None
    # d2 : précédent (d1) = LONG, courant = LONG → continuation (False)
    assert by_date[d2].is_flip is False
    # d3 : précédent (d2) = LONG, courant = SHORT → flip (True)
    assert by_date[d3].is_flip is True


def test_is_flip_none_quand_conclusion_insuffisant(tmp_path):
    """Conclusion INSUFFISANT côté courant OU précédent → is_flip=None."""
    bdir = tmp_path / "bulletins"
    bdir.mkdir()
    today = date(2026, 6, 5)
    d1 = today - timedelta(days=2)
    d2 = today - timedelta(days=1)
    # d1 INSUFFISANT (cellule encodée comme dans le bulletin réel)
    (bdir / f"bulletin-{d1.isoformat()}.md").write_text(
        f"# Bulletin Analyste — {d1.isoformat()}\n\n"
        "| Actif | 24h | 7j | 1m |\n"
        "|---|---|---|---|\n"
        "| Pétrole (Brent) | 🚫 données insuff. (10%) | LONG (+1.00) | LONG (+1.00) |\n",
        encoding="utf-8",
    )
    # d2 LONG
    _write_min_bulletin(
        bdir / f"bulletin-{d2.isoformat()}.md", d2,
        {"Pétrole (Brent)": {"24h": "LONG", "7j": "LONG", "1m": "LONG"}},
    )
    pedir = tmp_path / "prix-emission"
    pedir.mkdir()
    import json as _json
    for d in (d1, d2):
        (pedir / f"{d.isoformat()}.json").write_text(
            _json.dumps({"BZ=F": 100.0}), encoding="utf-8"
        )
    fiches = {
        "petrole": {
            "actif": "Pétrole (Brent)", "ticker_principal": "BZ=F",
            "seuils_reussite_pct": {"24h": 1.0, "7j": 2.0, "1m": 4.0},
        }
    }
    measures, _ = jr.measure(
        today=today, bulletins_dir=bdir, prix_emission_dir=pedir,
        fiches=fiches, fetch_price=lambda _t: 102.0,
    )
    # Mesure 24h de d2 (précédent d1 = INSUFFISANT)
    m_d2_24h = next(m for m in measures
                    if m.cell.bulletin_date == d2 and m.horizon == "24h")
    assert m_d2_24h.is_flip is None


# ===========================================================================
# render_performance : nouvelle section flip/continuation
# ===========================================================================

def test_render_performance_contient_section_flip_continuation():
    """La section flip/continuation (win-rate-only) apparaît quand il y a des
    données — agrégats globaux uniquement, pas de pavé par cellule."""
    ms = []
    base = date(2026, 1, 1)
    for i in range(3):
        ms.append(_make_measure(jr.OUTCOME_VRAI, is_flip=True,
                                echeance=base + timedelta(days=i)))
    for i in range(2):
        ms.append(_make_measure(jr.OUTCOME_FAUSSE, is_flip=False,
                                echeance=base + timedelta(days=10 + i)))
    k = jr.compute_kpi(ms)
    kpis = {("petrole", "24h"): k}
    out = jr.render_performance(kpis, ms, datetime(2026, 6, 2, tzinfo=timezone.utc))
    assert "### Flip vs continuation" in out
    assert "Win rate sur retournements" in out
    assert "Win rate sur continuations" in out


def test_render_performance_section_flip_absente_si_pas_de_donnees():
    """Aucune mesure avec is_flip → la section flip/continuation est omise
    (pas de bruit dans la vue propre)."""
    ms = [_make_measure(jr.OUTCOME_VRAI, is_flip=None,
                        echeance=date(2026, 1, 1))]
    k = jr.compute_kpi(ms)
    kpis = {("petrole", "24h"): k}
    out = jr.render_performance(kpis, ms, datetime(2026, 6, 2, tzinfo=timezone.utc))
    assert "Flip vs continuation" not in out


# ===========================================================================
# decision-log (scoring_analyste) : is_flip propagé
# ===========================================================================

def test_decision_log_inclut_is_flip_si_veille_fournie():
    """build_decision_log_records expose is_flip quand veille_conclusions est fourni."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))  # LONG
    # Veille : SHORT sur 24h, LONG sur 7j, absent sur 1m
    veille = {"testactif": {"24h": "SHORT", "7j": "LONG"}}
    # Note : la cellule veille[actif] est lookup par r.nom.lower() = "testactif"
    res.nom = "TestActif"
    records = sa.build_decision_log_records(
        [res], NOW, veille_conclusions=veille,
    )
    by_h = {r["horizon"]: r for r in records}
    # 24h : SHORT→LONG = flip
    assert by_h["24h"]["is_flip"] is True
    # 7j : LONG→LONG = continuation
    assert by_h["7j"]["is_flip"] is False
    # 1m : pas de veille → None
    assert by_h["1m"]["is_flip"] is None


def test_decision_log_is_flip_none_si_veille_non_fournie():
    """Backward-compat : sans veille_conclusions, is_flip=None partout."""
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    records = sa.build_decision_log_records([res], NOW)
    for r in records:
        assert r["is_flip"] is None
