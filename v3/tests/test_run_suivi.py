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
    # FIX 1 (23/06) : le bloc « Suggestions de sortie » ne porte QUE sur les paris
    # (selection=True). On marque Or sélectionné. Or SHORT seuil 0.5%, monte +1.12%
    # contre le call → Sortie à envisager rendue ET colonne « Vendre » cohérente.
    _decision_log_selection(env, {"Or"})
    r = _build(env, "12h", now, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.suggestion == "Sortie à envisager"
    assert or_li.vendre == "Vendre"  # source unique : cohérent avec la suggestion
    assert "Sortie à envisager" in r.markdown


# ---------------------------------------------------------------------------
# US pas encore ouvert à 12h (🕐) — correction M-H
# ---------------------------------------------------------------------------

def test_us_pas_encore_ouvert_a_12h(env):
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5301.0})
    sp = _ligne(r, "S&P 500")
    assert sp.us_pas_ouvert is True
    assert sp.statut == "🕐 cash fermé (ouvre 15h30)"
    assert sp.delta_pct is None  # pas de delta trompeur
    # Note honnête : cash fermé jusqu'à 15h30, futures non servis par notre source.
    assert "Cash US" in r.markdown and "futures" in r.markdown


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
# Refonte suivi S9 — fav_delta + compute_vendre (fonctions pures)
# ---------------------------------------------------------------------------

def test_fav_delta_signe_favorable():
    # LONG : favorable = +delta (monte = pour nous).
    assert rs.fav_delta(1.0, "LONG") == pytest.approx(1.0)
    assert rs.fav_delta(-1.0, "LONG") == pytest.approx(-1.0)
    # SHORT : favorable = -delta (baisse = pour nous).
    assert rs.fav_delta(-1.0, "SHORT") == pytest.approx(1.0)
    assert rs.fav_delta(1.0, "SHORT") == pytest.approx(-1.0)
    # Données / call absents → None (zéro invention).
    assert rs.fav_delta(None, "LONG") is None
    assert rs.fav_delta(1.0, "INSUFFISANT") is None


def test_compute_vendre_neutre_sous_bande():
    band = 0.001  # 0,1%
    # |delta| sous la bande → Pas vendre (rien à verrouiller), même au 18h.
    assert rs.compute_vendre(0.05, 0.04, "LONG", band) == "Pas vendre"
    assert rs.compute_vendre(0.05, None, "SHORT", band) == "Pas vendre"


def test_compute_vendre_donnees_absentes():
    band = 0.001
    # delta_now absent → Pas vendre (défaut sûr).
    assert rs.compute_vendre(None, 0.5, "LONG", band) == "Pas vendre"
    # call inconnu → Pas vendre.
    assert rs.compute_vendre(1.0, 0.5, "INSUFFISANT", band) == "Pas vendre"


def test_compute_vendre_12h_toujours_pas_vendre():
    band = 0.001
    # Au 12h (delta_prec None), on laisse courir, quel que soit le sens.
    # LONG favorable (fav_now>0) → Pas vendre.
    assert rs.compute_vendre(1.0, None, "LONG", band) == "Pas vendre"
    # LONG contre nous (fav_now<0) → Pas vendre (laisse la journée).
    assert rs.compute_vendre(-1.0, None, "LONG", band) == "Pas vendre"
    # SHORT favorable (delta<0 = pour nous) → Pas vendre.
    assert rs.compute_vendre(-1.0, None, "SHORT", band) == "Pas vendre"


def test_compute_vendre_18h_favorable():
    band = 0.001
    # LONG, gain qui GRANDIT (fav_now 1.5 > fav_prec 1.0) → Pas vendre (laisse courir).
    assert rs.compute_vendre(1.5, 1.0, "LONG", band) == "Pas vendre"
    # LONG, gain qui REFLUE (fav_now 0.6 < fav_prec 1.0) → Vendre (pic passé).
    assert rs.compute_vendre(0.6, 1.0, "LONG", band) == "Vendre"
    # LONG, gain stable (égal) → Pas vendre.
    assert rs.compute_vendre(1.0, 1.0, "LONG", band) == "Pas vendre"
    # LONG, signe INVERSÉ (était pour nous +0.8, maintenant contre -0.5) → Vendre.
    assert rs.compute_vendre(-0.5, 0.8, "LONG", band) == "Vendre"
    # SHORT favorable (delta -1.5 → fav +1.5) qui grandit vs 12h (-1.0 → fav +1.0)
    # → Pas vendre.
    assert rs.compute_vendre(-1.5, -1.0, "SHORT", band) == "Pas vendre"
    # SHORT favorable qui reflue (fav +0.6 < +1.0) → Vendre.
    assert rs.compute_vendre(-0.6, -1.0, "SHORT", band) == "Vendre"


def test_compute_vendre_18h_contre_nous():
    band = 0.001
    # LONG contre nous qui EMPIRE (fav -1.5 < fav -1.0) → Vendre (le pari ne paie pas).
    assert rs.compute_vendre(-1.5, -1.0, "LONG", band) == "Vendre"
    # LONG contre nous qui SE REDRESSE vers l'ouverture (fav -0.4 > fav -1.0) → Pas vendre.
    assert rs.compute_vendre(-0.4, -1.0, "LONG", band) == "Pas vendre"
    # SHORT contre nous (delta +1.5 → fav -1.5) qui empire vs 12h (delta +1.0 → fav -1.0)
    # → Vendre.
    assert rs.compute_vendre(1.5, 1.0, "SHORT", band) == "Vendre"


# ---------------------------------------------------------------------------
# Refonte suivi S9 — tableau de progression « Sélection du jour »
# ---------------------------------------------------------------------------

def _decision_log_selection(env, actifs_selectionnes):
    """Écrit un decision-log 7h marquant `selection_du_jour: true` pour `actifs`."""
    fp = env["dlog"] / "2026-06-08-07h.jsonl"
    lines = []
    for actif in ("Or", "CAC 40", "S&P 500"):
        lines.append(json.dumps({
            "bulletin_date": "2026-06-08", "actif": actif, "horizon": "24h",
            "selection_du_jour": actif in actifs_selectionnes,
        }))
    fp.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_selection_table_12h_seule_colonne_12h(env):
    # Or + CAC 40 sélectionnés ce jour.
    _decision_log_selection(env, {"Or", "CAC 40"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT, baisse -1% (favorable) ; CAC 40 SHORT, baisse (favorable).
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8100.0, "^GSPC": None})
    assert _ligne(r, "Or").selection is True
    assert _ligne(r, "S&P 500").selection is False
    md = r.markdown
    assert "Sélection du jour — progression" in md
    # En-tête du tableau Sélection présent (libellés complets desktop, dans des
    # spans à double libellé .c-full/.c-short — on vérifie les deux colonnes %).
    assert "% vs ouv. 12h" in md and "% vs ouv. 18h" in md
    # Décision ancrée à l'heure du rapport (ici 12h).
    assert "Vendre à 12h ?" in md
    # Le tableau Sélection est AVANT le suivi détaillé.
    assert md.index("Sélection du jour — progression") < md.index("Suivi détaillé")
    # Au 12h : colonne 18h vide (placeholder —), 12h remplie. Or SHORT baisse → favorable +.
    or_li = _ligne(r, "Or")
    assert or_li.fav_now is not None and or_li.fav_now > 0
    assert or_li.fav_prec is None
    assert or_li.vendre == "Pas vendre"  # 12h → on laisse courir


def test_selection_table_18h_deux_colonnes_et_vendre(env):
    # FIX 1 (23/06) : « Vendre » est désormais DÉRIVÉ de la suggestion de sortie
    # (seuil franchi CONTRE le call), source unique cohérente avec « Suggestions de
    # sortie ». Or SHORT seuil 0.5%, monte à 3438 (+1.12% contre le call) → perd
    # au-delà du seuil → Sortie à envisager → « Vendre ». Les deux colonnes 12h/18h
    # restent renseignées (favorable précédent + courant).
    _decision_log_selection(env, {"Or"})
    # 12h : Or SHORT, baisse -1.0% → favorable +1.0 (persisté pour la colonne 12h).
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    # 18h : Or monte à 3438 → delta +1.12% → contre le SHORT, au-delà du seuil 0.5%.
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": 5300.0})
    or_li = _ligne(r18, "Or")
    assert or_li.fav_prec == pytest.approx(1.0, abs=0.05)
    assert or_li.fav_now == pytest.approx(-1.12, abs=0.05)
    assert or_li.suggestion == "Sortie à envisager"
    assert or_li.vendre == "Vendre"  # cohérent avec la suggestion (source unique)
    assert "**Vendre**" in r18.markdown


def test_selection_table_aucune_selection(env):
    # Aucun decision-log → aucune sélection → message explicite (zéro invention).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8100.0, "^GSPC": None})
    assert "Pas de sélection aujourd'hui." in r.markdown
    # Le suivi détaillé reste présent (toutes les positions 24h).
    assert "Suivi détaillé" in r.markdown


def test_selection_table_pas_de_mention_monetaire(env):
    _decision_log_selection(env, {"Or", "CAC 40"})
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3366.0, "^FCHI": 8100.0, "^GSPC": None})
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3380.0, "^FCHI": 8110.0, "^GSPC": 5300.0})
    md = r18.markdown.lower()
    for token in ("€", "$", "gain", "perte", "rendement", "p&l"):
        assert token not in md, f"mention monétaire interdite : {token!r}"


# ---------------------------------------------------------------------------
# Brief S9 — cohérence avec le Bilan : excursions max favorable/adverse depuis
# l'ouverture (réutilise mesure_bilan), cascade de prix, garde-fou briefing 7h.
# ---------------------------------------------------------------------------

def _series_1h_jour(prices, h0=9):
    """Série 1h du 2026-06-08 : une barre/prix, heures Paris croissantes depuis h0."""
    return [
        (datetime(2026, 6, 8, h0 + i, 0, tzinfo=PARIS), float(p))
        for i, p in enumerate(prices)
    ]


def _build_series(env, report_type, now, series_by_ticker, fiches=None, spot=None):
    """build_suivi avec une série 1h injectée par ticker (fetch_series) + spot optionnel."""
    def _fetch_series(tkr, *, interval="1h", outputsize=24):
        return series_by_ticker.get(tkr)
    return rs.build_suivi(
        report_type, now=now, date_j=date(2026, 6, 8),
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"], suivi_dir=env["sdir"],
        prix_ouverture_dir=env["odir"], fiches=fiches or env["fiches"],
        fetch_price=(lambda t: (spot or {}).get(t)),
        fetch_series=_fetch_series,
    )


def test_excursions_max_long_depuis_ouverture(env):
    # CAC 40 est SHORT dans le bulletin fixture ; on teste un LONG via un fiche/cellule
    # dédiée : S&P 500 LONG, ouverture 5300. Série monte à 5400 (fav +1.89%) puis
    # redescend à 5250 (adverse -0.94%). Excursions calculées par mesure_bilan.
    now = datetime(2026, 6, 8, 18, 3, tzinfo=PARIS)
    series = {"^GSPC": _series_1h_jour([5300, 5400, 5250, 5320], h0=16)}
    r = _build_series(env, "18h", now, series)
    sp = _ligne(r, "S&P 500")
    assert sp.max_favorable_pct == pytest.approx(1.89, abs=0.02)
    assert sp.max_adverse_pct == pytest.approx(-0.94, abs=0.02)


def test_excursions_max_short_depuis_ouverture(env):
    # Or SHORT, ouverture 3400. Série baisse à 3340 (favorable +1.76%) puis remonte
    # à 3430 (adverse -0.88%). Favorable = sens du call (baisse pour un SHORT).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    series = {"GC=F": _series_1h_jour([3400, 3340, 3430, 3380])}
    r = _build_series(env, "12h", now, series)
    orr = _ligne(r, "Or")
    assert orr.max_favorable_pct == pytest.approx(1.76, abs=0.02)
    assert orr.max_adverse_pct == pytest.approx(-0.88, abs=0.02)
    # Affiché dans le tableau (sélection vide ici → on vérifie via la ligne).
    # Persistance : champs additifs écrits dans suivi-tracking si sélectionné (testé
    # ailleurs) ; ici on s'assure juste que le rendu n'a pas cassé.
    assert r.markdown


def test_cascade_prix_derniere_barre_1h_prioritaire_sur_spot(env):
    # La dernière barre 1h du jour PRIME sur le spot (cascade cohérente bilan).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    series = {"GC=F": _series_1h_jour([3400, 3410, 3366])}  # dernière barre = 3366
    r = _build_series(env, "12h", now, series, spot={"GC=F": 9999.0})
    orr = _ligne(r, "Or")
    assert orr.prix_courant == pytest.approx(3366.0)  # 1h, pas le spot 9999


def test_cascade_prix_fallback_spot_si_pas_de_barre(env):
    # Aucune barre 1h exploitable → on retombe sur le spot (zéro invention sinon).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build_series(env, "12h", now, {"GC=F": None}, spot={"GC=F": 3372.0})
    orr = _ligne(r, "Or")
    assert orr.prix_courant == pytest.approx(3372.0)


def test_cascade_prix_aucune_source_donne_tiret(env):
    # Ni barre 1h, ni spot → prix courant None (jamais comblé).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build_series(env, "12h", now, {"GC=F": None}, spot={"GC=F": None})
    orr = _ligne(r, "Or")
    assert orr.prix_courant is None
    assert orr.delta_pct is None


# --- GARDE-FOU HONNÊTETÉ : Briefing 7h introuvable vs aucune position ---------

def test_briefing_introuvable_affiche_message(env, tmp_path):
    # Dossier bulletins VIDE (briefing 7h archivé / jamais émis) → message explicite,
    # PAS un tableau vide silencieux (cause du suivi 18h vide d'aujourd'hui).
    bdir_vide = tmp_path / "bull-vide"
    bdir_vide.mkdir()
    r = rs.build_suivi(
        "18h", now=datetime(2026, 6, 8, 18, 3, tzinfo=PARIS), date_j=date(2026, 6, 8),
        bulletins_dir=bdir_vide, decision_log_dir=env["dlog"], suivi_dir=env["sdir"],
        prix_ouverture_dir=env["odir"], fiches=env["fiches"], fetch_price=lambda t: None,
    )
    assert r.briefing_introuvable is True
    assert "Briefing 7h du jour introuvable" in r.markdown
    assert "suivi des positions impossible" in r.markdown
    # On ne montre PAS le tableau de suivi détaillé dans ce cas.
    assert "Suivi détaillé" not in r.markdown


def test_briefing_trouve_mais_aucune_position_distinct(env, tmp_path):
    # Briefing 7h présent mais TOUTES les cellules 24h INSUFFISANT → 0 position
    # actionnable, MAIS le briefing existe → message DIFFÉRENT (pas « introuvable »).
    bdir = tmp_path / "bull-insuf"
    bdir.mkdir()
    (bdir / "bulletin-2026-06-08-07h.md").write_text(
        "# Bulletin 2026-06-08 07h\n\n"
        "| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
        "| Or | 🚫 données insuff. (32%) | 🚫 données insuff. (32%) | "
        "🚫 données insuff. (32%) |\n",
        encoding="utf-8",
    )
    r = rs.build_suivi(
        "12h", now=datetime(2026, 6, 8, 12, 3, tzinfo=PARIS), date_j=date(2026, 6, 8),
        bulletins_dir=bdir, decision_log_dir=env["dlog"], suivi_dir=env["sdir"],
        prix_ouverture_dir=env["odir"], fiches=env["fiches"], fetch_price=lambda t: None,
    )
    assert r.briefing_introuvable is False         # le briefing EXISTE
    assert "Briefing 7h du jour introuvable" not in r.markdown
    assert len(r.lignes) == 0                       # mais 0 position actionnable
    assert "aucune position actionnable du Briefing 7h" in r.markdown


def test_briefing_7h_existe_helper(env, tmp_path):
    # True quand un bulletin 7h du jour existe ; False sinon.
    assert rs.briefing_7h_existe(date(2026, 6, 8), env["bdir"]) is True
    vide = tmp_path / "vide"
    vide.mkdir()
    assert rs.briefing_7h_existe(date(2026, 6, 8), vide) is False


def test_excursions_persistees_dans_tracking(env, tmp_path):
    # Une sélection avec excursions calculables → champs additifs max_fav/max_adv
    # persistés dans suivi-tracking (clés existantes call/fav_pct/heure inchangées).
    _decision_log_selection(env, {"Or"})
    tracking_dir = tmp_path / "suivi-tracking"
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    series = {"GC=F": _series_1h_jour([3400, 3340, 3380])}
    r = _build_series(env, "12h", now, series)
    orr = _ligne(r, "Or")
    assert orr.selection is True
    # On persiste explicitement avec un base_dir de test (le default arg est figé).
    rs.save_suivi_tracking(date(2026, 6, 8), "12h", r.lignes, now, base_dir=tracking_dir)
    data = rs.load_suivi_tracking(date(2026, 6, 8), base_dir=tracking_dir)
    rec = data["12h"]["Or"]
    assert rec["call"] == "SHORT" and "fav_pct" in rec and "heure" in rec  # inchangés
    assert rec["max_fav_pct"] == pytest.approx(1.76, abs=0.02)
    assert rec["max_adv_pct"] == pytest.approx(0.0, abs=0.02)  # jamais au-dessus de l'ouverture


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


# ---------------------------------------------------------------------------
# FIX 1..4 (fondateur 23/06) — cohérence sorties/paris, news refondue, signe, légende
# ---------------------------------------------------------------------------

def _events_log(tmp_path, lignes):
    """Écrit un events-log.md minimal (1 batch du jour + lignes d'events).

    `lignes` = liste de dicts partiels (trigger/impacts/cat/materiality/date).
    Colonnes : date|l1|l2|trigger|cours|latence|r|source|zone|cat|pat|impacts|materiality|reliability
    """
    p = tmp_path / "events-log.md"
    out = ["<!-- batch 2026-06-08T07:30:00Z : 3 events -->"]
    for ev in lignes:
        row = [
            ev.get("date", "2026-06-08"), "", "", ev.get("trigger", ""),
            ev.get("cours", ""), "", "", ev.get("source", "rss"),
            "", ev.get("cat", "commodity"), "", ev.get("impacts", ""),
            ev.get("materiality", "high"), "",
        ]
        out.append("| " + " | ".join(row) + " |")
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return p


def test_news_reelle_paris_titre_reel_pas_synthese(env, tmp_path):
    # FIX 2a : pour un pari, on affiche le VRAI titre de news (events-log), JAMAIS
    # « Synthèse news (net, IA) ». Or (mappé via impacts GOLD) a une news dédiée.
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    ev_path = _events_log(tmp_path, [
        {"trigger": "Gold tumbles as US-Iran truce holds", "impacts": "GOLD:SHORT:80",
         "cat": "geopolitical", "materiality": "high"},
    ])
    out = rs.news_reelle_paris("12h", now, ["Or"], events_path=ev_path)
    assert out.get("Or") == "Gold tumbles as US-Iran truce holds"
    assert "Synthèse news" not in out.get("Or", "")


def test_news_reelle_paris_pas_de_news_absent(env, tmp_path):
    # FIX 2a (zéro invention) : un pari sans event exploitable est ABSENT du dict
    # (le rendu affichera « — »).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    ev_path = _events_log(tmp_path, [
        {"trigger": "Copper dips", "impacts": "COPPER:SHORT:60",
         "cat": "commodity", "materiality": "medium"},
    ])
    out = rs.news_reelle_paris("12h", now, ["Or"], events_path=ev_path)
    assert "Or" not in out


def test_vendre_from_suggestion_source_unique():
    # FIX 1 : « Vendre » ssi « Sortie à envisager », sinon « Pas vendre ». Verdict
    # UNIQUE partagé par la colonne « Vendre ? » et le bloc « Suggestions de sortie ».
    assert rs.vendre_from_suggestion("Sortie à envisager") == "Vendre"
    assert rs.vendre_from_suggestion("Surveiller") == "Pas vendre"
    assert rs.vendre_from_suggestion("Hold") == "Pas vendre"
    assert rs.vendre_from_suggestion("—") == "Pas vendre"


def test_fix1_aucune_suggestion_sur_actif_non_pari(env):
    # FIX 1 : Or perd au-delà du seuil MAIS n'est PAS sélectionné → aucune
    # suggestion de sortie rendue (on ne détient pas cet actif).
    _decision_log_selection(env, {"CAC 40"})  # seul CAC 40 est un pari
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT monte +1.12% (perd au-delà du seuil 0.5%) mais non-pari.
    r = _build(env, "12h", now, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    assert _ligne(r, "Or").suggestion == "Sortie à envisager"  # calculé...
    # ...mais NON rendu (Or non-pari) → bloc sans Or.
    bloc = r.markdown.split("### Suggestions de sortie")[1]
    assert "Or" not in bloc


def test_fix1_coherence_colonne_vendre_et_suggestions(env):
    # FIX 1 : un pari dont le % favorable dépasse le seuil → « sortie à envisager »
    # DANS LES DEUX endroits (colonne « Vendre ? » == Vendre ET bloc Suggestions).
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.suggestion == "Sortie à envisager"
    assert or_li.vendre == "Vendre"
    md = r.markdown
    # Colonne Vendre = **Vendre** dans la table Sélection ET dans le bloc Suggestions.
    assert "**Vendre**" in md
    bloc = md.split("### Suggestions de sortie")[1]
    assert "**Or**" in bloc and "Sortie à envisager" in bloc


def test_fix1_pari_qui_tient_jamais_de_contradiction(env):
    # FIX 1 : un pari favorable (gagne) → « Pas vendre » ET absent du bloc
    # Suggestions (jamais l'un qui dit vendre et l'autre tenir).
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT baisse à 3366 (favorable +1.0%) → gagne → Hold/Pas vendre.
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.vendre == "Pas vendre"
    assert or_li.suggestion == "Hold"
    bloc = r.markdown.split("### Suggestions de sortie")[1]
    assert "Aucune alerte de sortie." in bloc


def test_fix3_convention_signe_short_gagnant_positif_partout(env):
    # FIX 3 : SHORT gagnant → % FAVORABLE POSITIF dans la table Sélection ET dans
    # le panorama « Positions du matin » (plus jamais +x et −x sur le même actif).
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT, prix baisse 3400 → 3366 : delta brut -1.0%, favorable +1.0%.
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.fav_now == pytest.approx(1.0, abs=0.05)  # favorable POSITIF
    md = r.markdown
    # Le panorama « Positions du matin » affiche aussi le % FAVORABLE (signe + pour Or).
    panorama = md.split("### Positions du matin vs ouverture")[1]
    assert "| Or | SHORT |" in panorama
    ligne_or = next(l for l in panorama.splitlines() if l.startswith("| Or |"))
    assert "+1.00%" in ligne_or  # favorable positif, JAMAIS -1.00%
    # La colonne « Vendre / Pas vendre » a disparu du panorama (FIX 1).
    assert "Vendre / Pas vendre" not in panorama


def test_fix1_panorama_sans_colonne_vendre(env):
    # FIX 1 : le tableau panorama « Positions du matin » n'a plus de colonne de
    # reco de vente (on ne détient pas ces actifs).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    panorama = r.markdown.split("### Positions du matin vs ouverture")[1]
    assert "% favorable" in panorama
    assert "Vendre / Pas vendre" not in panorama


def test_fix4_legende_courte(env):
    # FIX 4 : légende courte (1 phrase), plus de pavé « Décision datée à 12h… ».
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    md = r.markdown
    assert "Vendre = sortir maintenant" in md
    assert "Décision datée à" not in md  # ancien pavé supprimé


def test_fix2b_grosse_actu_high_hors_paris_presente(env, tmp_path, monkeypatch):
    # FIX 2b : une grosse actu HIGH hors-paris (Pétrole/Ormuz) reste affichée dans
    # « Grosses actualités depuis 7h », même si Pétrole n'est pas un pari.
    import briefing as B
    ev_path = _events_log(tmp_path, [
        {"trigger": "Iran ferme le detroit d'Ormuz, tensions au plus haut",
         "impacts": "BRENT:LONG:90", "cat": "geopolitical", "materiality": "high"},
        {"trigger": "Bruit de faible matérialité sur le café",
         "impacts": "COFFEE:LONG:30", "cat": "commodity", "materiality": "low"},
    ])
    monkeypatch.setattr(B, "EVENTS_LOG", ev_path)
    _decision_log_selection(env, {"Or"})  # Pétrole n'est PAS un pari
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    md = r.markdown
    bloc = md.split("### 🚨 Grosses actualités depuis 7h")[1]
    assert "Ormuz" in bloc  # grosse actu high hors-pari présente
    # L'actu LOW non-pari n'apparaît PAS (filtre high materiality).
    assert "faible matérialité" not in md
