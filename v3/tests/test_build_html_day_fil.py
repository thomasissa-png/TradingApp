"""Tests build_html — fil complet de la journée sous le briefing 7h (vue Historique).

Cliquer un bulletin de l'Historique affiche le briefing 7h PUIS, sous lui, le fil
de la journée : suivi 12h → suivi 18h → bilan du jour 22h, chacun dans un
<details class="day-fil-report"> REPLIÉ (le briefing reste la lecture primaire).

Ces blocs sont construits côté client (JS embarqué dans index.html). Les tests
vérifient donc le contrat statique du JS/CSS généré :
- helper d'ordre canonique `sameDayReports(dateIso)` partagé avec la vue Aujourd'hui,
- `appendDayFil(content, id)` appelé après le rendu du briefing dans `selectBulletin`,
- ordre 12h → 18h → bilan, labels FR, rendu paresseux, dégradation propre,
- styles `.day-fil-*` cohérents avec l'existant.

Présentation/JS/CSS pur — WIN RATE ONLY, UTF-8/français.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_html as bh  # noqa: E402


def _html() -> str:
    """HTML minimal mais valide (sans I/O disque) pour inspecter le JS/CSS embarqué."""
    return bh.render_html([], 0, reports=[], weekly=None)


# ---------------------------------------------------------------------------
# Helper d'ordre canonique partagé
# ---------------------------------------------------------------------------

def test_helper_sameDayReports_present():
    html = _html()
    assert "function sameDayReports(dateIso)" in html
    # Filtre sur la date ISO et distingue le bilan du jour des suivis.
    assert "r.date !== dateIso" in html
    assert "r.kind === 'bilan-jour'" in html


def test_helper_sameDayReports_ordonne_suivis_puis_bilan():
    html = _html()
    # Suivis triés par créneau (12h avant 18h via localeCompare), bilan en dernier.
    assert "suivis.sort((a, b) => (a.slot || '').localeCompare(b.slot || ''))" in html
    assert "return bilan ? suivis.concat([bilan]) : suivis;" in html


def test_buildTodayView_reutilise_le_helper():
    # Pas de duplication de la logique d'ordre : la vue Aujourd'hui consomme le helper.
    html = _html()
    assert "const dayReports = sameDayReports(d);" in html


# ---------------------------------------------------------------------------
# appendDayFil : insertion dans selectBulletin
# ---------------------------------------------------------------------------

def test_appendDayFil_defini_et_appele_apres_briefing():
    html = _html()
    assert "function appendDayFil(container, id)" in html
    # Appelé dans selectBulletin, AVANT le replaceState (donc après le rendu 7h).
    assert "appendDayFil(content, b.id);" in html
    idx_call = html.index("appendDayFil(content, b.id);")
    idx_replace = html.index("history.replaceState(null, '', '#' + encodeURIComponent(id));")
    assert idx_call < idx_replace


def test_appendDayFil_calcule_la_date_depuis_id():
    html = _html()
    assert "const dateIso = (id || '').slice(0, 10);" in html
    assert "const reports = sameDayReports(dateIso);" in html


def test_appendDayFil_degradation_propre_si_aucun_rapport():
    # Aucun rapport du jour → return immédiat, rien n'est ajouté (zéro séparateur,
    # zéro message d'erreur).
    html = _html()
    assert "if (reports.length === 0) return;" in html


def test_appendDayFil_separateur_uniquement_si_rapports():
    # Le séparateur « La journée » est créé APRÈS le garde-fou length === 0,
    # donc absent quand il n'y a aucun rapport.
    html = _html()
    idx_guard = html.index("if (reports.length === 0) return;")
    idx_sep = html.index("sep.className = 'day-fil-sep';")
    assert idx_guard < idx_sep
    assert "sep.textContent = 'La journée';" in html


def test_appendDayFil_labels_francais():
    html = _html()
    assert "🕛 Suivi 12h" in html
    assert "🕕 Suivi 18h" in html
    assert "🌙 Bilan du jour — 22h15" in html


def test_appendDayFil_details_replie_par_defaut():
    # <details class="day-fil-report"> sans attribut open → replié (briefing primaire).
    html = _html()
    assert "rd.className = 'day-fil-report';" in html
    # Aucune ouverture forcée sur ces blocs (pas de rd.open = true dans appendDayFil).
    start = html.index("function appendDayFil(container, id)")
    end = html.index("function selectBulletin(id)", start)
    body = html[start:end]
    assert "rd.open = true" not in body


def test_appendDayFil_rendu_paresseux_via_pipeline_unifie():
    # Rendu seulement à la première ouverture, via renderMarkdownInto (badges, fold…).
    html = _html()
    start = html.index("function appendDayFil(container, id)")
    end = html.index("function selectBulletin(id)", start)
    body = html[start:end]
    assert "addEventListener('toggle'" in body
    assert "renderMarkdownInto(body, r.markdown)" in body


# ---------------------------------------------------------------------------
# CSS discret et cohérent
# ---------------------------------------------------------------------------

def test_css_day_fil_present_et_reutilise_les_variables():
    html = _html()
    assert ".day-fil-report {" in html
    assert ".day-fil-sep {" in html
    assert ".day-fil-body {" in html
    # Réutilise les tokens existants, pas un nouveau thème.
    assert "var(--border)" in html
    assert "var(--bg-panel)" in html
