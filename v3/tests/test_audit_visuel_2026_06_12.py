"""Tests des fixes de l'audit visuel 2026-06-12 (présentation pure).

Couvre les fixes MAJEURS (cas ciblés) : P-B1 (anti-répétition direction dans
« brut »), P-B2 (effets quasi nuls → —), P-B3 (gate inactif masqué / actif mis
en valeur dans le Détail), H-B1 (Jouables scindé forte sans/avec drapeau),
H-BD1 (ligne résumé score en tête du bilan), H-BD2 (WR du jour à 2 niveaux),
C-B3 (troncature Calls jugés), I-2 (verdict FAUSSE standardisé côté HTML),
I-7 (H1 pour tous les rapports), P-S2 (%pts), C-R1/P-R1 (transform vue Résultats).

Zéro vérification de scoring/mesure : présentation uniquement.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import scoring_analyste as sa
import bilan_jour as bj
import journaliste as J
import build_html as bh
import run_suivi as rs

NOW = datetime(2026, 6, 12, 7, 24, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fabriques
# ---------------------------------------------------------------------------

def _crit(nom, cle, contrib, *, poids=5.0, type_norm="lineaire", valeur_norm=0.8,
          is_gate=False, gate_active=False, source_track=""):
    return sa.CritereResult(
        id=cle, nom=nom, type_norm=type_norm, valeur_brute=1.0,
        valeur_norm=(None if is_gate else valeur_norm), poids=poids, signe=1,
        pertinence={h: 1.0 for h in sa.HORIZONS}, note="",
        contributions={h: contrib for h in sa.HORIZONS},
        is_gate=is_gate, gate_active=gate_active, source_track=source_track,
        cle_courante=cle,
    )


def _actif(nom, fkey, score, direction, criteres, conf="normale", coverage=0.85):
    def conc(s):
        return "LONG" if s > 0 else ("SHORT" if s < 0 else sa.CONCLUSION_INSUFFISANT)
    r = sa.ActifResult(
        nom=nom, fiche_key=fkey, criteres=criteres,
        scores={h: score for h in sa.HORIZONS},
        conclusions={h: conc(score) for h in sa.HORIZONS},
        tie_break_notes={},
        scores_pond={h: score for h in sa.HORIZONS},
        conclusions_pond={h: conc(score) for h in sa.HORIZONS},
        tie_break_notes_pond={}, diverge={h: False for h in sa.HORIZONS},
        coverage=coverage, confidence={h: conf for h in sa.HORIZONS},
    )
    r.news_cap_info = {h: {"news_total_pm1": 0.0, "quant_total_pm1": 1.0} for h in sa.HORIZONS}
    return r


def _render(results):
    sa._catalyseurs_j0_high = lambda now: []
    return sa.render_bulletin(results, {}, NOW, "hash123", "frais", prix_reference={})


# ---------------------------------------------------------------------------
# P-B2 — effets quasi nuls → —
# ---------------------------------------------------------------------------

def test_pb2_effet_quasi_nul_devient_tiret():
    c = _crit("Sentiment news", "news_x", 0.0, source_track="ia", valeur_norm=0.0)
    assert sa._fmt_effet(c, "24h") == "—"
    c2 = _crit("Driver", "drv_x", 0.42)
    assert sa._fmt_effet(c2, "24h") == "+0.420"


def test_pb2_dans_le_detail():
    crits = [
        _crit("Driver", "drv_or", -0.42),
        _crit("Sentiment news (neutre)", "news_or", 0.0, source_track="ia", valeur_norm=0.0),
    ]
    md = _render([_actif("Or", "or", -2.0, "SHORT", crits)])
    detail = md.split("## Détail par actif")[1]
    # La ligne du critère news neutre a « — » dans les 3 colonnes Effet (pas
    # +0.000). NB : le « Penchant » (valeur_norm) peut rester +0.000 — c'est la
    # contribution (« Effet ») qui est nettoyée par P-B2.
    news_row = [l for l in detail.splitlines() if "Sentiment news (neutre)" in l][0]
    cells = [c.strip() for c in news_row.split("|")]
    # Colonnes : '' Critère Lu Valeur Penchant Importance Sens Effet24 Effet7 Effet1m ''
    effet_24h, effet_7j, effet_1m = cells[7], cells[8], cells[9]
    assert effet_24h == "—" and effet_7j == "—" and effet_1m == "—"


# ---------------------------------------------------------------------------
# P-B3 — gate inactif masqué, gate actif mis en valeur + remonté en tête
# ---------------------------------------------------------------------------

def test_pb3_gate_inactif_masque():
    crits = [
        _crit("Driver", "drv_or", -0.42),
        _crit("Drapeau : événement majeur", "gate_or", 0.0, type_norm="gate",
              is_gate=True, gate_active=False),
    ]
    md = _render([_actif("Or", "or", -2.0, "SHORT", crits)])
    detail = md.split("## Détail par actif")[1]
    assert "Drapeau : événement majeur" not in detail


def test_pb3_gate_actif_mis_en_valeur():
    crits = [
        _crit("Driver", "drv_vix", -0.42),
        _crit("Drapeau : événement majeur", "gate_vix", 0.0, type_norm="gate",
              is_gate=True, gate_active=True),
    ]
    md = _render([_actif("VIX", "vix", -2.0, "SHORT", crits)])
    detail = md.split("## Détail par actif")[1]
    assert "⚑ **Drapeau régime ACTIF**" in detail


# ---------------------------------------------------------------------------
# P-B1 / I-3 — pas de répétition de la direction dans (brut ...)
# ---------------------------------------------------------------------------

def test_pb1_pas_de_repetition_direction_si_pondere_identique():
    # pondéré == primaire (fallback) → pas de [pond:...] et pas de « brut DIR ».
    crits = [_crit("Driver news", "news_x", -1.0, source_track="ia")]
    r = _actif("Cacao", "cacao", -2.0, "SHORT", crits)
    # news domine (ratio>0.5) → branche pond_differe possible ; on vérifie surtout
    # qu'aucune cellule n'affiche « brut SHORT » / « brut LONG » (répétition).
    md = _render([r])
    synth = md.split("## Synthèse des décisions")[1].split("## ")[0]
    assert "brut SHORT" not in synth
    assert "brut LONG" not in synth


# ---------------------------------------------------------------------------
# H-B1 — Jouables scindé en sous-groupes
# ---------------------------------------------------------------------------

def test_hb1_jouables_scinde_forte_sans_drapeau():
    # Une cellule forte propre (sans drapeau) → sous-groupe dédié.
    crits = [
        _crit("Driver", "drv_or", -0.42),
        _crit("Sec", "sec_or", -0.30),
        _crit("Ter", "ter_or", -0.28),
    ]
    md = _render([_actif("Or", "or", -13.3, "SHORT", crits)])
    a_jouer = md.split("## 🎯 À jouer aujourd'hui (24h)")[1].split("## ")[0]
    assert "_Conviction forte : sans drapeau_" in a_jouer


# ---------------------------------------------------------------------------
# C-B3 — troncature des Calls jugés
# ---------------------------------------------------------------------------

def test_cb3_constante_max_calls():
    assert sa.MAX_CALLS_DISPLAYED == 7


# ---------------------------------------------------------------------------
# H-BD1 / H-BD2 — bilan : ligne résumé + WR 2 niveaux
# ---------------------------------------------------------------------------

def _bilan_1_8_3():
    DJ = date(2026, 6, 11)
    def m(actif, conc, delta, outcome, seuil=0.5):
        cell = J.BulletinCell(bulletin_date=DJ, actif_name=actif, horizon="24h",
                              conclusion=conc, score=-2.0)
        return J.Measure(cell=cell, fiche_key=actif.lower(), ticker="X", horizon="24h",
                         echeance=date(2026, 6, 12), prix_emission=100.0,
                         prix_courant=101.0, seuil_pct=seuil, delta_pct=delta,
                         outcome=outcome)
    V, F, NC = J.OUTCOME_VRAI, J.OUTCOME_FAUSSE, J.OUTCOME_NC
    ms = ([m("Argent", "LONG", 1.6, V)]
          + [m(f"F{i}", "LONG", -2.0, F) for i in range(8)]
          + [m(f"N{i}", "SHORT", 0.04, NC) for i in range(3)])
    b = bj.BilanJour(date_j=DJ, now=datetime(2026, 6, 11, 22, 15))
    b.measures_24h = ms
    b.n_vrai, b.n_fausse, b.n_nc = 1, 8, 3
    b.win_rate_jour = 11.1
    b.wr_tradable_jour = round(1 / 12 * 100, 1)
    return b


def test_hbd1_ligne_resume_en_tete():
    b = _bilan_1_8_3()
    md = bj._render_markdown(b, {})
    # Ligne résumé AVANT le titre « Résultat des calls 7h ».
    head = md.split("### Résultat des calls 7h")[0]
    assert "1 ✅ / 8 ❌ / 3 ⚪" in head
    assert "Win rate : 11%" in head


def test_hbd2_wr_du_jour_primaire_en_gras():
    b = _bilan_1_8_3()
    md = bj._render_markdown(b, {})
    wr_section = md.split("### Win rate du jour")[1].split("### ")[0]
    assert "**11% (1/9)**" in wr_section
    assert "_Détail :_" in wr_section


def test_i7_bilan_titre_h1():
    b = _bilan_1_8_3()
    md = bj._render_markdown(b, {})
    assert md.startswith("# Bilan du jour")


# ---------------------------------------------------------------------------
# I-7 / P-S2 / H-S2 — suivi
# ---------------------------------------------------------------------------

def test_i7_suivi_titre_h1():
    r = rs.SuiviRapport(date_j=date(2026, 6, 11), now=datetime(2026, 6, 11, 18, 5),
                        report_type=rs.REPORT_18H)
    md = rs._render_markdown(r)
    assert md.startswith("# Suivi 18h")


def test_ps2_unite_pourcent_points():
    assert rs._fmt_points(1.51) == "+1.51%pts"
    assert rs._fmt_points(None) == "—"


def test_suivi_12h_pas_de_colonne_tendance_vide():
    r = rs.SuiviRapport(date_j=date(2026, 6, 11), now=datetime(2026, 6, 11, 12, 5),
                        report_type=rs.REPORT_12H)
    r.lignes = [rs.SuiviLigne("Or", "SHORT", 100.0, 99.0, -1.0, "✅ gagne", "—",
                              None, "Hold", 0.5)]
    md = rs._render_markdown(r)
    table_header = [l for l in md.splitlines() if l.startswith("| Actif")][0]
    # Au 12h, ni « Tendance » ni « Δ » dans l'en-tête (colonnes vides retirées).
    assert "Tendance" not in table_header
    assert "Δ" not in table_header


def test_suivi_18h_uniforme_delta_precedent():
    r = rs.SuiviRapport(date_j=date(2026, 6, 11), now=datetime(2026, 6, 11, 18, 5),
                        report_type=rs.REPORT_18H)
    r.lignes = [rs.SuiviLigne("Or", "SHORT", 100.0, 99.0, -1.0, "✅ gagne",
                              "↑ s'accélère", -0.4, "Hold", 0.5)]
    md = rs._render_markdown(r)
    table_header = [l for l in md.splitlines() if l.startswith("| Actif")][0]
    assert "Δ précédent" in table_header
    assert "Δ vs 7h" not in md and "Δ vs 12h" not in md


# ---------------------------------------------------------------------------
# I-2 — verdict FAUSSE standardisé côté HTML
# ---------------------------------------------------------------------------

def test_i2_outcome_badge_fausse_dans_html():
    html = bh.render_html([], 0)
    # La fonction outcomeBadge renvoie « ❌ FAUSSE » (et plus « ❌ FAUX »).
    assert "return '❌ FAUSSE';" in html
    assert "return '❌ FAUX';" not in html


# ---------------------------------------------------------------------------
# C-R1 / P-R1 — transform vue Résultats présent dans le HTML
# ---------------------------------------------------------------------------

def test_cr1_pr1_enhance_winrate_present():
    html = bh.render_html([], 0)
    assert "function enhanceWinrateRows" in html
    assert "WINRATE_MIN_N" in html


# ---------------------------------------------------------------------------
# S-R1 / P-R2 — performance.md : synthèse en tête + warning N faible
# ---------------------------------------------------------------------------

def test_sr1_synthese_en_tete_performance():
    md = J.render_performance({}, [], NOW, fiches={})
    lignes = [l for l in md.splitlines() if l.strip()]
    # 1re ligne = H1 ; 2e ligne significative = la synthèse « cellules fiables ».
    assert lignes[0].startswith("# ")
    assert "cellules fiables" in lignes[1]
