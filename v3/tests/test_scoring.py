"""Tests scoring_analyste — normalisation, tie-break, n/a, seuils, GATE."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fiches_dir():
    return ROOT / "config" / "fiches"


@pytest.fixture
def petrole(fiches_dir):
    fiches = sa.load_fiches(fiches_dir)
    assert "petrole" in fiches
    return fiches["petrole"]


def _now_utc():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

def test_normalise_lineaire_clip_haut():
    crit = {"normalisation": "lineaire", "centre": 0.0, "echelle": 1.0, "cap": 1.0}
    v, _ = sa.normalise(crit, 5.0)
    assert v == 1.0  # clip haut


def test_normalise_lineaire_clip_bas():
    crit = {"normalisation": "lineaire", "centre": 0.0, "echelle": 1.0, "cap": 1.0}
    v, _ = sa.normalise(crit, -5.0)
    assert v == -1.0  # clip bas


def test_normalise_lineaire_dans_intervalle():
    crit = {"normalisation": "lineaire", "centre": 3.0, "echelle": 2.0, "cap": 1.0}
    v, _ = sa.normalise(crit, 5.0)  # (5-3)/2 = 1.0 exactement
    assert v == pytest.approx(1.0)
    v2, _ = sa.normalise(crit, 4.0)  # (4-3)/2 = 0.5
    assert v2 == pytest.approx(0.5)


def test_normalise_triplet_valide():
    crit = {"normalisation": "triplet", "cap": 1.0}
    for inp, exp in [(-1, -1.0), (0, 0.0), (1, 1.0)]:
        v, _ = sa.normalise(crit, inp)
        assert v == exp


def test_normalise_triplet_clip_anormal():
    crit = {"normalisation": "triplet", "cap": 1.0}
    v, _ = sa.normalise(crit, 7)  # tolérance : valeur >0 -> +1
    assert v == 1.0
    v2, _ = sa.normalise(crit, -3)
    assert v2 == -1.0


def test_normalise_zscore_precalc():
    crit = {"normalisation": "zscore", "cap": 1.0}
    v, _ = sa.normalise(crit, {"valeur_normalisee": 0.4})
    assert v == pytest.approx(0.4)


def test_normalise_zscore_with_history():
    crit = {"normalisation": "zscore", "zscore_div": 2.0, "cap": 1.0}
    history = [10.0, 10.0, 10.0, 10.0, 12.0, 8.0]  # mean=10, stdev=~1.29
    v, note = sa.normalise(crit, {"valeur": 13.0, "history": history})
    assert v is not None
    assert -1.0 <= v <= 1.0
    assert "zscore" in note


def test_normalise_zscore_no_history_no_precalc_na():
    crit = {"normalisation": "zscore", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": 13.0})
    assert v is None
    assert "n/a" in note


def test_normalise_composite_precalc():
    """BUG#1 (a) : composite avec valeur_normalisee pré-calculée → valeur retournée.

    Avant correctif : tombait en « type de normalisation inconnu » → jeté en silence
    (ex: café météo Brésil composite poids 11, le critère le plus lourd, perdu).
    """
    crit = {"normalisation": "composite", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": -0.282, "valeur_normalisee": -0.141})
    assert v == pytest.approx(-0.141)
    assert "composite" in note and "pré-calculé" in note


def test_normalise_composite_precalc_clip():
    """composite : la valeur pré-calculée est bien capée à [-cap, +cap]."""
    crit = {"normalisation": "composite", "cap": 1.0}
    v, _ = sa.normalise(crit, {"valeur": 99.0, "valeur_normalisee": 2.5})
    assert v == 1.0


def test_normalise_mapping_non_monotone_precalc():
    """BUG#1 (b) : mapping_non_monotone avec valeur_normalisee pré-calculée.

    Ex: vix_regime / vxn_regime / v2x_regime (poids 7-8). Avant correctif : jeté.
    """
    crit = {"normalisation": "mapping_non_monotone", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": 14.95, "valeur_normalisee": 0.99})
    assert v == pytest.approx(0.99)
    assert "mapping_non_monotone" in note and "pré-calculé" in note


def test_normalise_composite_sans_normalisee_na():
    """BUG#1 (c) : composite SANS valeur_normalisee → n/a propre (pas de crash, pas d'invention)."""
    crit = {"normalisation": "composite", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": -0.282})
    assert v is None
    assert "n/a" in note and "composite" in note


def test_normalise_mapping_non_monotone_sans_normalisee_na():
    """mapping_non_monotone SANS valeur_normalisee → n/a propre."""
    crit = {"normalisation": "mapping_non_monotone", "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": 23.6})
    assert v is None
    assert "n/a" in note and "mapping_non_monotone" in note


def test_normalise_valeur_absente_na():
    crit = {"normalisation": "lineaire", "centre": 0.0, "echelle": 1.0, "cap": 1.0}
    v, note = sa.normalise(crit, None)
    assert v is None
    assert "n/a" in note


def test_normalise_source_dead_na():
    crit = {"normalisation": "lineaire", "centre": 0.0, "echelle": 1.0, "cap": 1.0}
    v, note = sa.normalise(crit, {"valeur": 1.0, "source_status": "DEAD"})
    assert v is None
    assert "DEAD" in note


def test_normalise_gate_drapeau_pas_de_valeur():
    crit = {"normalisation": "gate"}
    v, note = sa.normalise(crit, {"valeur": True})
    assert v is None
    assert "GATE" in note and "ACTIF" in note


# ---------------------------------------------------------------------------
# Seuil LONG / SHORT
# ---------------------------------------------------------------------------

def test_seuil_long_short(petrole):
    # Note : depuis l'ajout du gate de SUFFISANCE DE DONNÉES (sécurité Thomas),
    # un actif noté avec un seul critère sur ~10 → coverage < 40% → conclusion
    # = "INSUFFISANT" (override de la règle jamais-neutre). Pour valider la
    # logique LONG/SHORT pure, on fournit assez de critères pour atteindre
    # COVERAGE_OK (>= 65%) ; seul brent_term_structure_m1m2 porte le signe
    # voulu, les autres sont à 0 (neutres) pour ne pas perturber le score.
    base_valeurs = {
        # neutres (zscore pré-calculé à 0 → contribution nulle, mais critère couvert)
        "eia_crude_surprise": {"valeur_normalisee": 0.0},
        "api_weekly_surprise": {"valeur_normalisee": 0.0},
        "tension_geopol_moyen_orient": {"valeur": 0},
        "cftc_cot_crude_nets": {"valeur_normalisee": 0.0},
        "opec_production_policy": {"valeur": 0},
    }
    # Critère portant le signe LONG
    valeurs = {**base_valeurs, "brent_term_structure_m1m2": {"valeur": 5.0}}
    r = sa.score_actif("petrole", petrole, valeurs)
    assert r.confidence["7j"] in ("normale", "faible")  # pas INSUFFISANT
    assert r.scores["7j"] > 0
    assert r.conclusions["7j"] == "LONG"

    # Critère portant le signe SHORT
    valeurs_s = {**base_valeurs, "brent_term_structure_m1m2": {"valeur": -10.0}}
    r2 = sa.score_actif("petrole", petrole, valeurs_s)
    assert r2.confidence["7j"] in ("normale", "faible")
    assert r2.scores["7j"] < 0
    assert r2.conclusions["7j"] == "SHORT"


# ---------------------------------------------------------------------------
# n/a => poids 0 ce run
# ---------------------------------------------------------------------------

def test_na_implique_contribution_nulle(petrole):
    # Aucune valeur fournie => tous les critères en n/a => score = 0
    r = sa.score_actif("petrole", petrole, {})
    for h in sa.HORIZONS:
        assert r.scores[h] == 0.0
    # Tous les critères non-gate sont en n/a
    nas = [c for c in r.criteres if c.is_na]
    assert len(nas) >= 1
    for c in nas:
        for h in sa.HORIZONS:
            assert c.contributions[h] == 0.0


# ---------------------------------------------------------------------------
# GATE n'altère pas le score
# ---------------------------------------------------------------------------

def test_gate_n_altere_pas_le_score(petrole):
    valeurs_sans_gate = {"brent_term_structure_m1m2": {"valeur": 5.0}}
    valeurs_avec_gate = {
        "brent_term_structure_m1m2": {"valeur": 5.0},
        "gate_evenement_extreme": {"valeur": True},
    }
    r1 = sa.score_actif("petrole", petrole, valeurs_sans_gate)
    r2 = sa.score_actif("petrole", petrole, valeurs_avec_gate)
    for h in sa.HORIZONS:
        assert r1.scores[h] == r2.scores[h]
    # Le drapeau est bien actif dans r2
    gates_actifs = [c for c in r2.criteres if c.is_gate and c.gate_active]
    assert len(gates_actifs) == 1


# ---------------------------------------------------------------------------
# Tie-break §5.2
# ---------------------------------------------------------------------------

def _fiche_synth_tie():
    """Fiche minimale 4 critères linéaires pour tester le tie-break."""
    return {
        "actif": "Synthétique",
        "criteres": [
            {"id": 1, "nom": "A", "cle_courante": "a", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 1.0, "signe": 1, "poids": 10,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 2, "nom": "B", "cle_courante": "b", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 1.0, "signe": 1, "poids": 9,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 3, "nom": "C", "cle_courante": "c", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 1.0, "signe": 1, "poids": 8,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
            {"id": 4, "nom": "D", "cle_courante": "d", "normalisation": "lineaire",
             "centre": 0.0, "echelle": 1.0, "cap": 1.0, "signe": 1, "poids": 1,
             "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0}},
        ],
    }


def test_tie_break_majorite_top3_long():
    fiche = _fiche_synth_tie()
    # A=+1*10, B=+1*9, C=-1*8, D=-11/1=clip(-1)*1 -> score = 10+9-8-1 = 10  (>0, pas tie)
    # Pour forcer score=0 avec majorité top3 LONG :
    # A=+0.5*10=+5, B=+0.5*9=+4.5, C=-1*8=-8 ; D=-1.5/1->clip(-1)*1=-1.5 -> -1
    # somme = 5+4.5-8-1 = +0.5 (pas zéro). On vise score=0 et majorité top3 LONG.
    # A=+0.3*10=+3, B=+0.5*9=+4.5, C=-1*8=-8 ; D=+0.5*1=+0.5 -> 3+4.5-8+0.5=0.0 ✓
    valeurs = {"a": {"valeur": 0.3}, "b": {"valeur": 0.5}, "c": {"valeur": -1.0}, "d": {"valeur": 0.5}}
    r = sa.score_actif("synth", fiche, valeurs)
    assert r.scores["24h"] == pytest.approx(0.0)
    # top3 par |poids| = A(10), B(9), C(8). A>0 LONG, B>0 LONG, C<0 SHORT.
    # 2 LONG vs 1 SHORT -> LONG.
    assert r.conclusions["24h"] == "LONG"
    assert "24h" in r.tie_break_notes
    assert "majorité top3 LONG" in r.tie_break_notes["24h"]


def test_tie_break_majorite_top3_short():
    fiche = _fiche_synth_tie()
    # A=-0.3*10=-3, B=-0.5*9=-4.5, C=+1*8=+8 ; D=-0.5*1=-0.5 -> -3-4.5+8-0.5=0 ✓
    # top3 |poids|: A(-), B(-), C(+) -> 2 SHORT, 1 LONG -> SHORT
    valeurs = {"a": {"valeur": -0.3}, "b": {"valeur": -0.5}, "c": {"valeur": 1.0}, "d": {"valeur": -0.5}}
    r = sa.score_actif("synth", fiche, valeurs)
    assert r.scores["24h"] == pytest.approx(0.0)
    assert r.conclusions["24h"] == "SHORT"
    assert "majorité top3 SHORT" in r.tie_break_notes["24h"]


def test_tie_break_egalite_reconduction_veille():
    """Score=0 + égalité top3 => reconduit la veille."""
    fiche = _fiche_synth_tie()
    # 4 critères, mais on force top3 à 0 contributions par valeurs nulles
    # Solution : passer par tie_break directement avec construction manuelle.
    # On utilise score_actif avec valeurs qui mènent à top3 = 0,0,0 contributions
    # Difficile via valeurs brutes -> on teste tie_break directement.
    criteres = [
        sa.CritereResult(id=i, nom=f"X{i}", type_norm="lineaire", valeur_brute=None,
                         valeur_norm=0.0, poids=p, signe=1,
                         pertinence={"24h": 1, "7j": 1, "1m": 1},
                         note="", contributions={"24h": 0.0, "7j": 0.0, "1m": 0.0})
        for i, p in enumerate([10, 9, 8])
    ]
    conc, note = sa.tie_break(criteres, "24h", veille_conclusion="SHORT")
    assert conc == "SHORT"
    assert "reconduction veille" in note


def test_tie_break_aucune_veille_long_defaut():
    criteres = [
        sa.CritereResult(id=i, nom=f"X{i}", type_norm="lineaire", valeur_brute=None,
                         valeur_norm=0.0, poids=p, signe=1,
                         pertinence={"24h": 1, "7j": 1, "1m": 1},
                         note="", contributions={"24h": 0.0, "7j": 0.0, "1m": 0.0})
        for i, p in enumerate([10, 9, 8])
    ]
    conc, note = sa.tie_break(criteres, "24h", veille_conclusion=None)
    assert conc == "LONG"
    assert "LONG par défaut" in note


# ---------------------------------------------------------------------------
# Fraîcheur
# ---------------------------------------------------------------------------

def test_freshness_ok():
    now = _now_utc()
    data = {"last_update": now.isoformat()}
    ok, msg = sa.check_freshness(data, now=now)
    assert ok, msg


def test_freshness_stale():
    now = _now_utc()
    stale = now - timedelta(hours=2)
    data = {"last_update": stale.isoformat()}
    ok, msg = sa.check_freshness(data, now=now)
    assert not ok
    assert "PÉRIMÉ" in msg
    assert "âge ≈ 2h" in msg  # affichage lisible (#1)


def test_freshness_missing():
    ok, msg = sa.check_freshness({}, now=_now_utc())
    assert not ok
    assert "last_update" in msg


# ---------------------------------------------------------------------------
# Intégration : run() complet avec fixture criteres-courants
# ---------------------------------------------------------------------------

def test_run_full_petrole(tmp_path, petrole, fiches_dir):
    """Bout-en-bout : criteres-courants fixture -> bulletin écrit."""
    cc = tmp_path / "criteres-courants.md"
    now = _now_utc()
    # Suffisamment de critères pour passer le gate suffisance (sécurité Thomas) :
    # eia (10) + api (8) + tension (7) + cftc (7) + opec (6) + brent (5) +
    # spread (4) + caixin (4) = 51/60 = 85% → confidence "normale".
    cc.write_text(
        "```yaml\n"
        f"last_update: {now.isoformat()}\n"
        "petrole:\n"
        "  eia_crude_surprise: { valeur_normalisee: 0.0 }\n"
        "  api_weekly_surprise: { valeur_normalisee: 0.0 }\n"
        "  tension_geopol_moyen_orient: { valeur: 0 }\n"
        "  cftc_cot_crude_nets: { valeur_normalisee: 0.0 }\n"
        "  opec_production_policy: { valeur: 0 }\n"
        "  brent_term_structure_m1m2: { valeur: 0.5 }\n"
        "  spread_brent_wti: { valeur: 5.0 }\n"
        "  caixin_pmi_manuf: { valeur: 51.5 }\n"
        "  gate_evenement_extreme: { valeur: true }\n"
        "```\n",
        encoding="utf-8",
    )
    bulletins = tmp_path / "bulletins"
    out, results = sa.run(
        fiches_dir=fiches_dir,
        criteres_path=cc,
        bulletins_dir=bulletins,
        now=datetime.now(),
        write=True,
    )
    assert out.exists()
    txt = out.read_text(encoding="utf-8")
    assert "Bulletin Analyste" in txt
    assert "Pétrole (Brent)" in txt
    # GATE actif visible
    assert "GATE ACTIF" in txt or "⚑" in txt
    # le moteur charge toutes les fiches dispo ; on cible le résultat Pétrole
    assert any(r.fiche_key == "petrole" for r in results)
    r = next(r for r in results if r.fiche_key == "petrole")
    # Score > 0 (3 critères LONG, signe +1, valeurs positives)
    assert r.scores["7j"] > 0
    assert r.conclusions["7j"] == "LONG"


def _petrole_cc(tmp_path, now):
    """Écrit un criteres-courants Pétrole suffisant pour passer le gate."""
    cc = tmp_path / "criteres-courants.md"
    cc.write_text(
        "```yaml\n"
        f"last_update: {now.astimezone(timezone.utc).isoformat()}\n"
        "petrole:\n"
        "  eia_crude_surprise: { valeur_normalisee: 0.0 }\n"
        "  api_weekly_surprise: { valeur_normalisee: 0.0 }\n"
        "  tension_geopol_moyen_orient: { valeur: 0 }\n"
        "  cftc_cot_crude_nets: { valeur_normalisee: 0.0 }\n"
        "  opec_production_policy: { valeur: 0 }\n"
        "  brent_term_structure_m1m2: { valeur: 0.5 }\n"
        "  spread_brent_wti: { valeur: 5.0 }\n"
        "  caixin_pmi_manuf: { valeur: 51.5 }\n"
        "  gate_evenement_extreme: { valeur: true }\n"
        "```\n",
        encoding="utf-8",
    )
    return cc


def test_run_nom_fichier_heure_paris_pas_utc(tmp_path, fiches_dir):
    """Bug 05/06 : le nom de fichier du bulletin doit utiliser l'heure de PARIS
    (cohérente avec le titre « HHhMM (Paris) » et le decision-log), PAS l'heure
    UTC. Un run à 18h04 Paris (= 16h UTC) doit produire bulletin-...-18h.md, pas
    bulletin-...-16h.md."""
    from zoneinfo import ZoneInfo

    # 18h04 Paris = 16h04 UTC (été, UTC+2).
    now = datetime(2026, 6, 5, 18, 4, tzinfo=ZoneInfo("Europe/Paris"))
    cc = _petrole_cc(tmp_path, now)
    bulletins = tmp_path / "bulletins"

    out, _ = sa.run(
        fiches_dir=fiches_dir,
        criteres_path=cc,
        bulletins_dir=bulletins,
        now=now,
        write=True,
    )

    # Nom de fichier = heure Paris (18h), PAS heure UTC (16h).
    assert out.name == "bulletin-2026-06-05-18h.md", out.name
    assert "-16h.md" not in out.name
    # Cohérence nom de fichier ⇄ titre interne (« 18h04 (Paris) »).
    txt = out.read_text(encoding="utf-8")
    assert "18h04 (Paris)" in txt


# ---------------------------------------------------------------------------
# #6 — _fmt_raw : arrondi 4 chiffres significatifs pour les floats
# ---------------------------------------------------------------------------

def test_fmt_raw_float_long_arrondi_4_sig():
    """Un float long est arrondi à ~4 chiffres significatifs."""
    assert sa._fmt_raw(-0.01558281747644441) == "-0.01558"
    assert sa._fmt_raw(2.0712345) == "2.071"
    # Pas de notation scientifique moche : repli décimal lisible.
    out = sa._fmt_raw(1.234e-05)
    assert "e" not in out.lower()
    assert out == "0.00001234"


def test_fmt_raw_garde_entiers_none_str():
    """Les entiers, floats entiers, None/dict et chaînes restent propres."""
    # Entiers (triplets -1/0/+1, COT en milliers)
    assert sa._fmt_raw(-1) == "-1"
    assert sa._fmt_raw(0) == "0"
    assert sa._fmt_raw(1) == "1"
    # Float entier (ex. 441686.0) → sans décimales
    assert sa._fmt_raw(441686.0) == "441686"
    # None / chaînes
    assert sa._fmt_raw(None) == "—"
    assert sa._fmt_raw("texte") == "texte"
    # bool n'est pas confondu avec un float scientifique
    assert sa._fmt_raw(True) == "1"
    # dict → résout la valeur puis applique le même arrondi
    assert sa._fmt_raw({"valeur": -0.0099999}) == "-0.01"


# ---------------------------------------------------------------------------
# #7 — Audit de la veille (24h — convictions fortes)
# ---------------------------------------------------------------------------

def _ecrire_bulletin_veille(bulletins_dir: Path, bdate, conclusion: str = "LONG"):
    """Écrit un bulletin minimal de la veille avec une cellule 24h Pétrole."""
    bulletins_dir.mkdir(parents=True, exist_ok=True)
    bid = f"{bdate.isoformat()}-16h"
    p = bulletins_dir / f"bulletin-{bid}.md"
    p.write_text(
        f"# Bulletin Analyste — {bdate.isoformat()}\n\n"
        "## Matrice\n\n"
        "| Actif | 24h | 7j | 1m |\n"
        "|---|---|---|---|\n"
        f"| Pétrole (Brent) | {conclusion} (+1.50) | {conclusion} (+2.00) | {conclusion} (+3.00) |\n",
        encoding="utf-8",
    )
    return bid, p


def _ecrire_decision_log(log_dir: Path, bdate, confidence: str = "normale",
                         is_carry=False, is_news_regime=False, coin_flip=False,
                         news_dominant=False, ratio_news=0.0, score_pm1=1.5):
    """Écrit un decision-log pour la cellule Pétrole 24h de la veille."""
    import json
    log_dir.mkdir(parents=True, exist_ok=True)
    rec = {
        "bulletin_date": bdate.isoformat(),
        "actif": "Pétrole (Brent)",
        "horizon": "24h",
        "confidence": confidence,
        "is_carry": is_carry,
        "is_news_regime": is_news_regime,
        "coin_flip": coin_flip,
        "news_dominant": news_dominant,
        "ratio_news": ratio_news,
        "score_pm1": score_pm1,
    }
    (log_dir / f"{bdate.isoformat()}-1600.jsonl").write_text(
        json.dumps(rec, ensure_ascii=False) + "\n", encoding="utf-8",
    )


def test_audit_veille_warmup_message(tmp_path):
    """Aucune mesure 24h dispo → message « pas encore »."""
    import journaliste as j
    bulletins = tmp_path / "bulletins"
    bulletins.mkdir()
    lines = sa.build_audit_veille_24h(
        now=datetime.now(),
        bulletins_dir=bulletins,
        decision_log_dir=tmp_path / "decision-log",
    )
    txt = "\n".join(lines)
    assert "## Audit de la veille (24h — convictions fortes)" in txt
    assert "Pas encore de cellule 24h à forte conviction" in txt


def test_audit_veille_liste_conviction_normale_vrai(tmp_path, monkeypatch):
    """Une cellule 24h conviction normale, mesurée VRAI, est listée avec son %."""
    import journaliste as j
    now = datetime.now()
    bdate = (now - timedelta(days=1)).date()
    bulletins = tmp_path / "bulletins"
    log_dir = tmp_path / "decision-log"
    prix_dir = tmp_path / "prix-emission"

    bid, _ = _ecrire_bulletin_veille(bulletins, bdate, conclusion="LONG")
    _ecrire_decision_log(log_dir, bdate, confidence="normale", score_pm1=1.5)

    # Prix d'émission Pétrole (ticker BZ=F) + prix courant en hausse > seuil 24h.
    prix_dir.mkdir()
    (prix_dir / f"{bid}.json").write_text('{"BZ=F": 100.0}', encoding="utf-8")
    monkeypatch.setattr(j, "PRIX_EMISSION_DIR", prix_dir)
    monkeypatch.setattr(j, "DECISION_LOG_DIR", log_dir)
    # +5% > seuil 24h → mouvement net dans le sens LONG → VRAI.
    monkeypatch.setattr(
        "criteres_calculator.fetch_twelve_price", lambda ticker: 105.0,
    )

    lines = sa.build_audit_veille_24h(
        now=now, bulletins_dir=bulletins, decision_log_dir=log_dir,
        prix_emission_dir=prix_dir,
    )
    txt = "\n".join(lines)
    assert "✅" in txt
    assert "Pétrole (Brent) 24h LONG" in txt
    assert "VRAI" in txt
    assert "+5.00%" in txt
    assert "Pas encore" not in txt


def test_audit_veille_exclut_faible_carry_news(tmp_path, monkeypatch):
    """Les convictions dégradées (faible/carry/news) sont exclues de l'audit."""
    import journaliste as j
    now = datetime.now()
    bdate = (now - timedelta(days=1)).date()
    prix_dir = tmp_path / "prix-emission"
    prix_dir.mkdir()
    monkeypatch.setattr(j, "PRIX_EMISSION_DIR", prix_dir)
    monkeypatch.setattr(
        "criteres_calculator.fetch_twelve_price", lambda ticker: 105.0,
    )

    for label, kwargs in [
        ("faible", {"confidence": "faible"}),
        ("carry", {"confidence": "normale", "is_carry": True}),
        ("news_regime", {"confidence": "normale", "is_news_regime": True}),
        ("coin_flip", {"confidence": "normale", "coin_flip": True}),
        ("news_dominant", {"confidence": "normale", "news_dominant": True}),
    ]:
        bulletins = tmp_path / f"bulletins_{label}"
        log_dir = tmp_path / f"log_{label}"
        bid, _ = _ecrire_bulletin_veille(bulletins, bdate, conclusion="LONG")
        _ecrire_decision_log(log_dir, bdate, **kwargs)
        (prix_dir / f"{bid}.json").write_text('{"BZ=F": 100.0}', encoding="utf-8")
        monkeypatch.setattr(j, "DECISION_LOG_DIR", log_dir)
        lines = sa.build_audit_veille_24h(
            now=now, bulletins_dir=bulletins, decision_log_dir=log_dir,
            prix_emission_dir=prix_dir,
        )
        txt = "\n".join(lines)
        assert "Pas encore de cellule 24h à forte conviction" in txt, (
            f"profil {label} aurait dû être exclu → message warm-up attendu"
        )
