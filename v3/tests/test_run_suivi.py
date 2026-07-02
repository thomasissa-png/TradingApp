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
    # Chantier B (L027) — prix d'émission 7h (« Prix d'entrée » du bulletin), keyé par
    # IDENTITÉ de bulletin (2026-06-08-07h.json). ÉGAL à l'ouverture par défaut : les
    # tests structurels (cohérence action/suggestion) restent valides ; les tests
    # dédiés Chantier B (base ≠ ouverture) écrivent leur propre fichier d'émission.
    edir = tmp_path / "prix-emission"
    edir.mkdir()
    (edir / "2026-06-08-07h.json").write_text(
        json.dumps({"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5300.0}),
        encoding="utf-8",
    )
    dlog = tmp_path / "decision-log"
    dlog.mkdir()
    sdir = tmp_path / "suivi"
    # Dir indices-US (OANDA) DÉDIÉ et VIDE par défaut : garantit le repli « cash
    # fermé » dans les tests qui n'injectent pas de cotation continue.
    fdir = tmp_path / "futures-us"
    return {
        "bdir": bdir, "odir": odir, "edir": edir, "dlog": dlog, "sdir": sdir,
        "fdir": fdir, "fiches": FICHES, "tmp": tmp_path,
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
        prix_emission_dir=env.get("edir"),
        fiches=fiches or env["fiches"],
        fetch_price=lambda t: cur.get(t),
        futures_us_dir=env["fdir"],
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
    # Correction fondateur 01/07 : tendance + Δ dérivés du FAVORABLE. Or SHORT, le
    # prix MONTE (+0.5% → +1.0%) → le pari se DÉGRADE (fav -0.5 → -1.0) : ↓ s'essouffle,
    # Δ favorable = -0.5 (le pari recule), plus jamais +0.5 (variation du prix brut).
    assert lig.tendance == "↓ s'essouffle"
    assert lig.delta_vs_prec == pytest.approx(-0.5, abs=0.02)


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
    # Or contre le call au-delà du seuil → reco d'action 🔴 Coupe (fondateur 24/06).
    assert or_li.action == "🔴 Coupe"
    assert "🔴" in r.markdown and "couper" in r.markdown  # bloc « Suggestions de sortie »


# ---------------------------------------------------------------------------
# US pas encore ouvert à 12h (🕐) — correction M-H
# ---------------------------------------------------------------------------

def test_us_pas_encore_ouvert_a_12h(env):
    # Cash US à 12h SANS cotation OANDA (dir vide) → « future : cotation en attente »
    # (on trade le future, pas « cash fermé » — cadrage fondateur 24/06).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5301.0})
    sp = _ligne(r, "S&P 500")
    assert sp.us_pas_ouvert is True
    assert sp.statut == "⏳ future : cotation en attente"
    assert sp.delta_pct is None  # pas de delta trompeur
    # Plus de « Note sur les marchés US » répétée à chaque suivi (fondateur 24/06).
    assert "Note sur les marchés US" not in r.markdown
    assert "Cash US" not in r.markdown


def _ecrire_oanda(env, day, snapshots, last_ts):
    """Écrit un fichier futures-us minimal {date}.json façon fetch_us_index."""
    env["fdir"].mkdir(parents=True, exist_ok=True)
    data = {"date": day, "snapshots": snapshots}
    for inst in ("SPX500_USD", "NAS100_USD"):
        vals = [s[inst] for s in snapshots if inst in s]
        if vals:
            data[inst] = {"price": vals[-1], "ts": last_ts}
    (env["fdir"] / f"{day}.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def test_us_via_future_oanda_frais_affiche_le_mouvement_signe(env):
    # SPX500_USD : ref (1ère cotation) 5500 → courant 5533 = +0.60%.
    # S&P 500 est LONG dans le bulletin → fav_now positif (sens du call).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    ts = now.astimezone(ZoneInfo("UTC")).isoformat()  # frais (= now)
    _ecrire_oanda(env, "2026-06-08", [
        {"ts": ts, "SPX500_USD": 5500.0, "NAS100_USD": 19800.0},
        {"ts": ts, "SPX500_USD": 5533.0, "NAS100_USD": 19850.0},
    ], last_ts=ts)
    r = _build(env, "12h", now, {"GC=F": 3400.0, "^FCHI": 8120.0})
    sp = _ligne(r, "S&P 500")
    assert sp.us_pas_ouvert is True
    assert sp.statut == "🔵 via future S&P 500"
    assert sp.delta_pct == 0.6  # mouvement indice vs indice
    assert sp.fav_now == 0.6    # LONG → favorable positif
    assert sp.prix_courant == 5533.0
    assert sp.ouverture == 5500.0  # référence = entrée du matin


def test_us_via_future_oanda_perime_repli_cash_ferme(env):
    # Cotation vieille de > 30 min → périmée → repli « future : cotation en attente ».
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    vieux = datetime(2026, 6, 8, 9, 0, tzinfo=ZoneInfo("UTC")).isoformat()
    _ecrire_oanda(env, "2026-06-08", [
        {"ts": vieux, "SPX500_USD": 5500.0},
        {"ts": vieux, "SPX500_USD": 5533.0},
    ], last_ts=vieux)
    r = _build(env, "12h", now, {"GC=F": 3400.0, "^FCHI": 8120.0})
    sp = _ligne(r, "S&P 500")
    assert sp.statut == "⏳ future : cotation en attente"
    assert sp.delta_pct is None


def test_us_via_future_oanda_echelle_jamais_melangee(env):
    # Le % de l'indice (5500→5533) ne doit JAMAIS se calculer contre un cash.
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    ts = now.astimezone(ZoneInfo("UTC")).isoformat()
    _ecrire_oanda(env, "2026-06-08", [
        {"ts": ts, "SPX500_USD": 5500.0},
        {"ts": ts, "SPX500_USD": 5533.0},
    ], last_ts=ts)
    r = _build(env, "12h", now, {"GC=F": 3400.0, "^FCHI": 8120.0})
    sp = _ligne(r, "S&P 500")
    assert sp.delta_pct == 0.6
    assert abs(sp.delta_pct) < 5  # garde-fou : pas un % aberrant


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
    # « gain » / « perte » = AMPLITUDE directionnelle, autorisée depuis la décision
    # fondateur 24/06 (« max gain » = % vers la cible turbo > 1 %, jamais un montant —
    # cohérent avec test_selection_table_pas_de_mention_monetaire). Seuls les vrais
    # marqueurs MONÉTAIRES restent interdits (WIN RATE ONLY).
    for token in ("€", "$", "rendement", "p&l", "expectancy", "equity"):
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
    # Chantier B (L027) : la table Sélection mesure vs le PRIX D'ENTRÉE 7h.
    assert "% vs entrée 12h" in md and "% vs entrée 18h" in md
    # Colonne « Action » (remplace « Vendre ? », fondateur 24/06).
    assert "| Action |" in md
    # Le tableau Sélection est AVANT le suivi détaillé.
    assert md.index("Sélection du jour — progression") < md.index("Suivi détaillé")
    # Au 12h : colonne 18h vide (placeholder —), 12h remplie. Or SHORT baisse → favorable +.
    or_li = _ligne(r, "Or")
    assert or_li.fav_now is not None and or_li.fav_now > 0
    assert or_li.fav_prec is None
    assert or_li.action.startswith("🟢")  # gagne et proche du pic → laisse courir


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
    # Contre le call au-delà du seuil → reco d'action 🔴 Coupe (fondateur 24/06).
    assert or_li.action == "🔴 Coupe"
    assert "**🔴 Coupe**" in r18.markdown


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
    # « gain » autorisé : le suivi affiche le « max gain » (% d'amplitude vers la
    # cible turbo > 1 %, jamais un montant — décision fondateur 24/06).
    for token in ("€", "$", "rendement", "p&l"):
        assert token not in md, f"mention monétaire interdite : {token!r}"


# ---------------------------------------------------------------------------
# Chantier A (02/07) — JUSTIFICATION UNIQUE bulletin↔suivi : le suivi affiche
# VERBATIM le texte persisté par le bulletin (selection_raison) ; fallback
# reconstitué (drivers_du_call) sur les vieux logs qui n'ont pas le champ.
# ---------------------------------------------------------------------------

def _decision_log_records(env, records):
    """Écrit un decision-log 7h brut (records arbitraires) pour le jour du test."""
    fp = env["dlog"] / "2026-06-08-07h.jsonl"
    fp.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


def test_chantierA_raison_verbatim_du_bulletin(env):
    # Le bulletin a PERSISTÉ le texte exact de sa justification → le suivi l'affiche
    # tel quel (une seule logique de formulation, côté bulletin).
    texte = "Porté par le récit d'offre (déficit ICCO) et un momentum haussier"
    _decision_log_records(env, [
        {"bulletin_date": "2026-06-08", "actif": "Or", "horizon": "24h",
         "selection_du_jour": True, "selection_raison": texte,
         "score_pm1": -3.2, "criteres": [{"nom": "Autre driver", "contrib_pond": -0.9}]},
    ])
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.raison_call == texte            # VERBATIM, aucune re-formulation
    assert texte in r.markdown
    assert "(reconstitué)" not in (or_li.raison_call or "")


def test_chantierA_fallback_reconstitue_vieux_log(env):
    # Vieux decision-log SANS selection_raison mais AVEC criteres → le suivi
    # reconstitue depuis drivers_du_call, avec la mention discrète « (reconstitué) ».
    _decision_log_records(env, [
        {"bulletin_date": "2026-06-08", "actif": "Or", "horizon": "24h",
         "selection_du_jour": True, "score_pm1": -3.2,
         "criteres": [
             {"nom": "Dollar fort", "contrib_pond": -0.8},
             {"nom": "Bruit mineur", "contrib_pond": -0.02},
         ]},
    ])
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.raison_call is not None
    assert or_li.raison_call.endswith("(reconstitué)")


# ---------------------------------------------------------------------------
# Chantier B (02/07, L027) — la table Sélection mesure vs le PRIX D'ÉMISSION 7h
# (« Prix d'entrée » du bulletin) ; le PANORAMA reste vs ouverture.
# ---------------------------------------------------------------------------

def _set_emission(env, prix):
    (env["edir"] / "2026-06-08-07h.json").write_text(json.dumps(prix), encoding="utf-8")


def _set_ouverture(env, prix):
    (env["odir"] / "2026-06-08.json").write_text(json.dumps(prix), encoding="utf-8")


def test_chantierB_pct_vs_emission_cas_cacao(env):
    # Cas réel cacao 01/07 : ouverture 5077, prix d'entrée (émission) 5079.97. Le %
    # annoncé au trader dans la table Sélection doit se mesurer vs 5079.97, PAS 5077
    # (arithmétique testée sur le ticker de la fixture ; le signe dépend du call).
    _decision_log_selection(env, {"Or"})
    _set_ouverture(env, {"GC=F": 5077.0, "^FCHI": 8120.0, "^GSPC": 5300.0})
    _set_emission(env, {"GC=F": 5079.97, "^FCHI": 8120.0, "^GSPC": 5300.0})
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 5130.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.emission == pytest.approx(5079.97)
    # delta brut vs ouverture = +1.04 % ; vs entrée = +0.98 % → BASES DIFFÉRENTES.
    assert or_li.delta_pct == pytest.approx(1.04, abs=0.02)
    assert or_li.delta_emission == pytest.approx(0.98, abs=0.02)
    assert or_li.delta_pct != or_li.delta_emission
    md = r.markdown
    panorama = md.split("### Positions du matin vs ouverture")[1]
    assert "5077" in panorama                     # panorama = base ouverture
    top3 = md.split("### Sélection du jour — progression")[1].split("### Positions")[0]
    assert "5080" in top3                          # table Sélection = base entrée (5079.97)
    assert "% vs entrée" in top3


def test_chantierB_transition_pas_de_faux_delta(env):
    # TRANSITION : le snapshot 12h précédent est sur l'ANCIENNE base (ouverture only).
    # Au 18h, faute de snapshot base-entrée, la colonne « % 12h » de la table Sélection
    # affiche « — » (zéro faux Δ inter-bases) — le panorama garde son Δ base-ouverture.
    _decision_log_selection(env, {"Or"})
    _set_emission(env, {"GC=F": 3410.0, "^FCHI": 8120.0, "^GSPC": 5300.0})
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    # Simule un ANCIEN 12h (pré-L027) : le snapshot base ENTRÉE n'existe pas.
    (env["sdir"] / "2026-06-08-12h-emission.json").unlink()
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3400.0, "^FCHI": 8120.0, "^GSPC": 5300.0})
    or_li = _ligne(r18, "Or")
    assert or_li.fav_prec is not None              # base ouverture : snapshot legacy présent
    assert or_li.fav_prec_emission is None          # base entrée absente → AUCUN faux Δ
    top3 = r18.markdown.split("### Sélection du jour — progression")[1].split("### Positions")[0]
    ligne_or = next(l for l in top3.splitlines() if l.startswith("| Or |"))
    assert "—" in ligne_or                          # colonne « % 12h » = « — »


def test_chantierB_action_et_suggestion_sur_base_entree(env):
    # Or SHORT, seuil 0.5 %. Émission == prix courant (3438) → 0 % vs entrée → ⚪ Tiens,
    # AUCUNE suggestion ; alors que vs ouverture (3400) c'est +1.12 % CONTRE le call
    # (🔴 Coupe). La table Sélection ET les suggestions suivent la base ENTRÉE.
    _decision_log_selection(env, {"Or"})
    _set_emission(env, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": 5300.0})
    r = _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
               {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.action == "🔴 Coupe"               # base ouverture (interne / panorama)
    assert or_li.action_emission == "⚪ Tiens"        # base entrée (table Sélection)
    md = r.markdown
    assert "**⚪ Tiens**" in md
    assert "**🔴 Coupe**" not in md                  # plus jamais le verdict base-ouverture
    bloc = md.split("### Suggestions de sortie")[1]
    assert "Aucune alerte" in bloc                   # aucune sortie sur la base entrée


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
        prix_ouverture_dir=env["odir"], prix_emission_dir=env.get("edir"),
        fiches=fiches or env["fiches"],
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


def test_suivi_statut_max_gain_gagne_et_pas_encore(env):
    """Le suivi affiche le max gain du jour + le statut vs cible turbo > 1 %
    (décision fondateur 24/06 : « gagné » / « pas encore »), sans réseau (high/low
    sauté faute de clé → max gain = excursion 1h injectée)."""
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT, ouverture 3400 → baisse à 3340 = +1.76% favorable (> 1% → gagné).
    series = {"GC=F": _series_1h_jour([3400, 3340])}
    r = _build_series(env, "12h", now, series)
    orr = _ligne(r, "Or")
    assert orr.max_gain_pct is not None and orr.max_gain_pct > 1.0
    md = r.markdown
    assert "Max gain jour" in md          # colonne max gain
    assert "Gagné" in md                  # colonne statut
    assert "✅ gagné" in md               # Or a dépassé 1 %


def test_suivi_statut_pas_encore_sous_seuil(env):
    """Pari sous 1 % → statut « pas encore » avec le max atteint (zéro invention)."""
    assert rs.statut_max_gain(0.6) == "⏳ pas encore (+0.60%)"
    assert rs.statut_max_gain(1.4) == "✅ gagné"
    assert rs.statut_max_gain(None) == "—"


# ---------------------------------------------------------------------------
# Conviction (note signée du signal 7h) — fondateur 25/06
# ---------------------------------------------------------------------------

def _decision_log_conviction(env, scores, selection=None):
    """Écrit un decision-log 7h avec `score_pm1` par actif (24h) + sélection.

    `scores` : dict actif -> score_pm1 (signé). `selection` : set d'actifs
    `selection_du_jour: true` (défaut = aucun)."""
    selection = selection or set()
    fp = env["dlog"] / "2026-06-08-07h.jsonl"
    lines = []
    for actif in ("Or", "CAC 40", "S&P 500"):
        rec = {
            "bulletin_date": "2026-06-08", "actif": actif, "horizon": "24h",
            "selection_du_jour": actif in selection,
        }
        if actif in scores:
            rec["score_pm1"] = scores[actif]
        lines.append(json.dumps(rec))
    fp.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_conviction_signee_priorite_pm1_puis_pond():
    # score_pm1 prioritaire (même priorité que le Bilan du jour, source unique).
    assert rs.conviction_signee({"score_pm1": -10.74, "score_pond": 2.0}) == -10.74
    # Fallback score_pond si pm1 absent.
    assert rs.conviction_signee({"score_pond": 3.24}) == 3.24
    # Aucun score → None (zéro invention).
    assert rs.conviction_signee({}) is None
    assert rs.conviction_signee({"score_pm1": None}) is None


def test_fmt_conviction_format_call_signe():
    # [Fusion 30/06] Call + conviction dans une seule colonne : « DIR · note ».
    assert rs._fmt_conviction("SHORT", -10.74) == "SHORT · -10.74"
    assert rs._fmt_conviction("LONG", 3.24) == "LONG · +3.24"
    # Score absent mais direction connue → on garde au moins la direction.
    assert rs._fmt_conviction("SHORT", None) == "SHORT"
    # Ni direction ni score → placeholder (zéro invention).
    assert rs._fmt_conviction("", None) == "—"


def test_positions_vs_ouverture_colonnes_riches(env):
    # Le panorama « Positions du matin vs ouverture » porte désormais les MÊMES
    # colonnes riches que le Top 3 + Conviction (fondateur 25/06).
    _decision_log_conviction(env, {"Or": -10.74, "CAC 40": 4.0, "S&P 500": 1.5})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8100.0, "^GSPC": None})
    panorama = r.markdown.split("### Positions du matin vs ouverture")[1]
    # En-tête : colonnes ajoutées (l'en-tête doit contenir « Max gain » pour
    # l'exemption HTML qui empêche de masquer ces colonnes).
    assert "Max gain du jour" in panorama
    assert "Gagné" in panorama
    # Point 5 (fondateur 01/07) : le panorama (non détenu) porte « Call » (intact/cassé),
    # PLUS l'action (Coupe/Sécurise/Tiens), qui reste dans la table Sélection.
    assert "| Call |" in panorama
    # [Fusion 30/06] la conviction est fusionnée dans la colonne « Call 7h ».
    assert "conviction" in panorama
    # Ligne Or : direction · LIBELLÉ conviction + note (point 9a : SHORT · forte (-10.74)),
    # et état du call (✅ intact / ✖ cassé), plus d'action en gras dans le panorama.
    ligne_or = next(l for l in panorama.splitlines() if l.startswith("| Or |"))
    assert "SHORT · forte (-10.74)" in ligne_or
    assert "✅ intact" in ligne_or or "✖ cassé" in ligne_or


def test_positions_vs_ouverture_conviction_absente_placeholder(env):
    # Pas de score dans le decision-log → Conviction « — » (zéro invention).
    _decision_log_conviction(env, {})  # aucun score_pm1
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8100.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.conviction is None


def test_coherence_top3_positions_memes_chiffres(env):
    # CONTRÔLE DE COHÉRENCE (fondateur 25/06) : un actif présent dans le Top 3 ET
    # dans « Positions vs ouverture » doit afficher EXACTEMENT les mêmes Max gain,
    # Action et Conviction (mêmes objets SuiviLigne, zéro re-dérivation).
    _decision_log_conviction(env, {"Or": -10.74, "CAC 40": 4.0},
                             selection={"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8100.0, "^GSPC": None})
    md = r.markdown
    top3 = md.split("### Sélection du jour — progression")[1].split("###")[0]
    panorama = md.split("### Positions du matin vs ouverture")[1]
    or_top3 = next(l for l in top3.splitlines() if l.startswith("| Or |"))
    or_pano = next(l for l in panorama.splitlines() if l.startswith("| Or |"))
    or_li = _ligne(r, "Or")
    # Max gain et Conviction (mêmes valeurs dérivées de la même ligne). L'action en
    # gras reste dans la table Sélection (Top 3) ; le panorama porte « Call » intact/cassé
    # (point 5) — plus d'action dupliquée dans le panorama.
    max_str = rs._fmt_pct(or_li.max_gain_pct)
    conv_str = rs._fmt_call_conviction(or_li.call, or_li.conviction, or_li.conviction_niveau)
    assert max_str in or_top3 and max_str in or_pano
    assert f"**{or_li.action}**" in or_top3
    assert conv_str in or_top3 and conv_str in or_pano


def test_cascade_prix_spot_temps_reel_prioritaire(env):
    # FONDATEUR 24/06 (bug prix périmé) : le SPOT TEMPS RÉEL prime sur la barre 1h
    # (qui peut avoir des heures de retard). En séance, « courant » = dernier prix réel.
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    series = {"GC=F": _series_1h_jour([3400, 3410, 3366])}  # barres 1h (potentiellement en retard)
    r = _build_series(env, "12h", now, series, spot={"GC=F": 3372.0})
    orr = _ligne(r, "Or")
    assert orr.prix_courant == pytest.approx(3372.0)  # spot, pas la barre 1h 3366


def test_cascade_prix_fallback_barre_1h_si_pas_de_spot(env):
    # Pas de spot exploitable → on retombe sur la dernière barre 1h (filet).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    series = {"GC=F": _series_1h_jour([3400, 3410, 3366])}
    r = _build_series(env, "12h", now, series, spot={"GC=F": None})
    orr = _ligne(r, "Or")
    assert orr.prix_courant == pytest.approx(3366.0)


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


def test_coherence_action_table_et_suggestions(env):
    # L'action 🔴 Coupe apparaît DANS LES DEUX endroits (colonne Action de la table
    # Sélection ET bloc Suggestions de sortie) — source unique, jamais de contradiction.
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.action == "🔴 Coupe"
    md = r.markdown
    assert "**🔴 Coupe**" in md            # colonne Action de la table Sélection
    bloc = md.split("### Suggestions de sortie")[1]
    assert "**Or**" in bloc and "couper" in bloc   # même verdict dans le bloc


def test_pari_qui_tient_jamais_de_contradiction(env):
    # Un pari favorable (gagne, proche du pic) → 🟢 Laisse courir ET absent du bloc
    # Suggestions (jamais l'un qui dit couper et l'autre tenir).
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    # Or SHORT baisse à 3366 (favorable +1.0%) → gagne → 🟢 Laisse courir.
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    or_li = _ligne(r, "Or")
    assert or_li.action.startswith("🟢")
    bloc = r.markdown.split("### Suggestions de sortie")[1]
    assert "Aucune alerte" in bloc


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
    assert "Max gain = meilleur % atteint depuis" in md  # légende reformulée (Action)
    assert "🟡 sécurise" in md
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


# ---------------------------------------------------------------------------
# ETF US commodity (CANE/COTN) fermé à 12h (fondateur 30/06) : pas de faux 0.00 %
# ---------------------------------------------------------------------------

_BULLETIN_SUCRE = """# Bulletin 2026-06-08 07h

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| Sucre | LONG (+0.90) | LONG (+0.40) | LONG (+0.20) |
"""


def _env_sucre(tmp_path):
    bdir = tmp_path / "bulletins"
    bdir.mkdir()
    (bdir / "bulletin-2026-06-08-07h.md").write_text(_BULLETIN_SUCRE, encoding="utf-8")
    odir = tmp_path / "prix-ouverture"
    odir.mkdir()
    (odir / "2026-06-08.json").write_text(json.dumps({"CANE": 9.78}), encoding="utf-8")
    return {"bdir": bdir, "odir": odir, "dlog": tmp_path / "dlog",
            "sdir": tmp_path / "suivi", "fdir": tmp_path / "futures-us"}


def _build_sucre(e, report_type, now, cur):
    return rs.build_suivi(
        report_type, now=now, date_j=date(2026, 6, 8),
        bulletins_dir=e["bdir"], decision_log_dir=e["dlog"], suivi_dir=e["sdir"],
        prix_ouverture_dir=e["odir"],
        fiches={"sucre": _fiche("Sucre", "CANE", "softs", 0.8)},
        fetch_price=lambda t: cur.get(t), futures_us_dir=e["fdir"],
    )


def test_etf_us_ferme_a_12h_pas_de_faux_zero(tmp_path):
    """Sucre (CANE, ETF NYSE) à 12h : marché US fermé → statut d'attente, pas de
    prix ni de faux 0.00 % (fondateur 30/06 : CANE affichait 9.785 → 9.785 = 0.00 %)."""
    e = _env_sucre(tmp_path)
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build_sucre(e, "12h", now, {"CANE": 9.78})
    li = _ligne(r, "Sucre")
    assert li.us_pas_ouvert is True
    assert li.prix_courant is None and li.ouverture is None
    assert li.delta_pct is None
    # Point 4 (fondateur 01/07) : libellé UNIFIÉ « 🕐 pas encore ouvert », pas de faux neutre.
    assert li.statut == rs.STATUT_PAS_ENCORE_OUVERT
    assert "pas encore ouvert" in li.statut
    ligne_md = next(l for l in r.markdown.splitlines() if l.startswith("| Sucre |"))
    assert "0.00%" not in ligne_md


def test_etf_us_ouvert_a_18h_prix_normal(tmp_path):
    """À 18h (US ouvert depuis 15h30) le même ETF reprend un relevé normal."""
    e = _env_sucre(tmp_path)
    now = datetime(2026, 6, 8, 18, 3, tzinfo=PARIS)
    r = _build_sucre(e, "18h", now, {"CANE": 9.98})
    li = _ligne(r, "Sucre")
    assert li.us_pas_ouvert is False
    assert li.prix_courant == pytest.approx(9.98)
    assert li.delta_pct == pytest.approx((9.98 - 9.78) / 9.78 * 100, abs=0.01)


# ---------------------------------------------------------------------------
# Vague de corrections fondateur 01/07 (points 1..9)
# ---------------------------------------------------------------------------

def test_point1_delta_precedent_en_favorable(env):
    # Point 1 : Δ précédent = variation du % FAVORABLE signé par le call (pas du prix
    # brut). Cas réel fondateur : CAC 40 SHORT, le pari S'AMÉLIORE (fav +0.46 → +0.79)
    # → Δ = +0.33 %pts (positif), plus jamais -0.33 (le prix brut baissait).
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3400.0, "^FCHI": 8082.65, "^GSPC": None})  # delta -0.46% → fav +0.46
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3400.0, "^FCHI": 8055.85, "^GSPC": 5300.0})  # delta -0.79% → fav +0.79
    cac = _ligne(r18, "CAC 40")
    assert cac.fav_prec == pytest.approx(0.46, abs=0.03)
    assert cac.fav_now == pytest.approx(0.79, abs=0.03)
    assert cac.delta_vs_prec == pytest.approx(0.33, abs=0.03)
    assert cac.tendance == "↑ s'accélère"


def test_point2_tendance_retournement_favorable(env):
    # Point 2 : ⇄ se retourne = le favorable change de camp. Or SHORT gagnant à 12h
    # (fav +1.0), puis le prix repasse au-dessus de l'ouverture à 18h (fav < 0).
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": 5300.0})
    orr = _ligne(r18, "Or")
    assert orr.fav_prec > 0 and orr.fav_now < 0
    assert orr.tendance == "⇄ se retourne"


def test_point3_max_gain_suspect_pure():
    # Point 3 : garde-fou de plausibilité (bug Blé +7.93%). Plafond = seuil × 5.
    assert rs.max_gain_suspect(7.93, 1.0) is True      # blé aberrant
    assert rs.max_gain_suspect(2.64, 1.0) is False     # café plausible
    assert rs.max_gain_suspect(7.93, None) is True     # fallback cible globale ×5
    assert rs.max_gain_suspect(None, 1.0) is False     # zéro invention
    assert "⚠️ à vérifier" in rs._fmt_max_gain(7.93, 1.0)
    assert "⚠️" not in rs._fmt_max_gain(2.64, 1.0)


def test_point3_max_gain_garde_fou_dans_rapport(env):
    # Point 3 (intégration) : un tick aberrant dans la série 1h gonfle le max gain
    # (Or SHORT, plus-bas à -8% = +8% favorable) → suffixé « ⚠️ à vérifier » (seuil
    # Or 0.5% → plafond plausible 2.5%). Le max reste AFFICHÉ (zéro invention).
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    series = {"GC=F": _series_1h_jour([3400, 3128])}  # -8% ⇒ +8% favorable (SHORT)
    r = _build_series(env, "12h", now, series)
    orr = _ligne(r, "Or")
    assert orr.max_gain_pct is not None and orr.max_gain_pct > 5.0
    assert rs.max_gain_suspect(orr.max_gain_pct, orr.seuil_pct) is True
    assert "⚠️ à vérifier" in r.markdown


def test_point5_call_etat_intact_casse():
    # Point 5 : le panorama porte « Call » intact/cassé (cassé = même seuil que 🔴).
    assert rs.call_etat(1.0, 0.5) == "✅ intact"     # favorable
    assert rs.call_etat(-0.3, 0.5) == "✅ intact"    # perd mais sous le seuil
    assert rs.call_etat(-0.6, 0.5) == "✖ cassé"      # contre le call au-delà du seuil
    assert rs.call_etat(None, 0.5) == "—"            # non mesurable


def test_point5_panorama_action_absente_call_present(env):
    # Point 5 : la reco d'action (🟢🟡🔴⚪) N'est PLUS dans le panorama (non détenu),
    # remplacée par « Call » (intact/cassé). Elle reste dans la table Sélection.
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3438.0, "^FCHI": 8120.0, "^GSPC": None})
    panorama = r.markdown.split("### Positions du matin vs ouverture")[1]
    ligne_or = next(l for l in panorama.splitlines() if l.startswith("| Or |"))
    assert "✖ cassé" in ligne_or       # Or SHORT monte au-delà du seuil → call cassé
    assert "🔴 Coupe" not in ligne_or   # plus d'action dans le panorama
    # ...mais l'action reste dans la table Sélection.
    top3 = r.markdown.split("### Sélection du jour — progression")[1].split("###")[0]
    assert "**🔴 Coupe**" in top3


def test_point6_suggestions_message_coherent(env):
    # Point 6 : aucun pari en alerte → message explicite (le panorama n'est pas détenu).
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    bloc = r.markdown.split("### Suggestions de sortie")[1]
    assert "Aucune alerte sur les paris du jour." in bloc
    assert "n'est pas détenu" in bloc


def test_point7_news_contre_sens_pure():
    # Point 7 : contre-sens = sens IA de la news OPPOSÉ au call (NEUTRAL/absent → non).
    assert rs.news_contre_sens("LONG", "SHORT") is True
    assert rs.news_contre_sens("SHORT", "LONG") is True
    assert rs.news_contre_sens("LONG", "LONG") is False
    assert rs.news_contre_sens("LONG", "NEUTRAL") is False
    assert rs.news_contre_sens("LONG", None) is False


def test_point7_grosse_actu_pour_fallback():
    # Point 7 (b) : si la news du pari est « — », on reprend la grosse actu de l'actif.
    lignes = ["- **Blé** : USDA relève les stocks mondiaux", "- Marché calme"]
    assert rs._grosse_actu_pour("Blé", lignes) == "USDA relève les stocks mondiaux"
    assert rs._grosse_actu_pour("Cacao", lignes) is None


def test_point7_news_contre_sens_marquee_dans_rapport(env, tmp_path, monkeypatch):
    # Point 7 (a) : Or SHORT est un pari ; la news dominante GOLD est LONG (haussière)
    # → suffixe « (à contre-sens du pari) » dans « News des paris du jour ».
    import briefing as B
    ev_path = _events_log(tmp_path, [
        {"trigger": "Gold rallies on safe-haven bid", "impacts": "GOLD:LONG:80",
         "cat": "geopolitical", "materiality": "high"},
    ])
    monkeypatch.setattr(B, "EVENTS_LOG", ev_path)
    _decision_log_selection(env, {"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    bloc = r.markdown.split("### News des paris du jour")[1]
    assert "Gold rallies" in bloc
    assert "(à contre-sens du pari)" in bloc


def test_point9a_fmt_call_conviction_libelle():
    # Point 9a : conviction = LIBELLÉ (forte/faible) + note entre parenthèses.
    assert rs._fmt_call_conviction("LONG", 8.77, "forte") == "LONG · forte (+8.77)"
    assert rs._fmt_call_conviction("SHORT", -2.88, "faible") == "SHORT · faible (-2.88)"
    # Dégradations : sans niveau → note seule ; sans score → direction ; rien → —.
    assert rs._fmt_call_conviction("LONG", 3.24, None) == "LONG · +3.24"
    assert rs._fmt_call_conviction("SHORT", None, "forte") == "SHORT"
    assert rs._fmt_call_conviction("", None, None) == "—"


def test_point9a_conviction_niveau_depuis_decision_log(env):
    # Point 9a : le niveau (forte/faible) vient du decision-log (même source que le
    # Bilan). Or a un score fort (|-10.74| ≥ seuil, sans drapeau) → « forte ».
    _decision_log_conviction(env, {"Or": -10.74}, selection={"Or"})
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, {"GC=F": 3366.0, "^FCHI": 8120.0, "^GSPC": None})
    orr = _ligne(r, "Or")
    assert orr.conviction_niveau == "forte"
    top3 = r.markdown.split("### Sélection du jour — progression")[1].split("###")[0]
    assert "forte (-10.74)" in top3
