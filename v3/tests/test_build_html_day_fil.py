"""Tests build_html — clic sur un JOUR de l'historique = journée dépliable.

Refonte navigation (session 06-20) : la sidebar liste désormais UN JOUR par
entrée (déduplication par date, sans heure dans le libellé). Cliquer un jour
présente la journée COMME la vue « Aujourd'hui » : un groupe repliable
(buildDayGroup) avec briefing 7h + suivis 12h/18h + bilan du soir, chacun dans
un <details class="today-report"> à rendu paresseux — au lieu de n'ouvrir que le
bulletin 7h.

Intention conservée vs l'ancien `appendDayFil`/`selectBulletin` (supprimés) :
- ordre canonique de la journée via `sameDayReports` (12h → 18h → bilan),
- TOUS les rapports du jour visibles et dépliables,
- dégradation propre si un rapport manque (jour sans bilan, etc.),
- rendu paresseux via le pipeline unifié `renderMarkdownInto`.
Le système de regroupement de today-view est RÉUTILISÉ (pas de second système).

Ces blocs sont construits côté client (JS embarqué dans index.html). Les tests
vérifient le contrat statique du JS/CSS généré. Présentation/JS/CSS pur —
WIN RATE ONLY, UTF-8/français.
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
# Helpers d'ordre canonique partagés (un seul système de regroupement)
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


def test_helper_sameDayBriefings_present():
    # Un jour peut avoir plusieurs briefings (run matin + soir) : helper dédié.
    html = _html()
    assert "function sameDayBriefings(dateIso)" in html


def test_buildTodayView_et_selectDay_reutilisent_le_meme_groupe():
    # Pas de duplication : today-view ET le clic d'historique passent par buildDayGroup.
    html = _html()
    assert "function buildDayGroup(dateIso, opts)" in html
    # today-view consomme buildDayGroup…
    assert "buildDayGroup(d, { openDay:" in html
    # …et le clic sur un jour aussi.
    assert "const grp = buildDayGroup(dateIso," in html


# ---------------------------------------------------------------------------
# buildDayGroup : ordre, rendu paresseux, dégradation propre
# ---------------------------------------------------------------------------

def test_buildDayGroup_collecte_briefings_et_rapports():
    html = _html()
    assert "const briefings = sameDayBriefings(dateIso);" in html
    assert "const dayReports = sameDayReports(dateIso);" in html


def test_buildDayGroup_ordre_briefing_suivis_bilan():
    # Ordre de lecture : briefing 7h → suivi 12h → suivi 18h → bilan 22h.
    html = _html()
    assert "briefings.forEach(b => ordered.push({ tag: 'Briefing'" in html
    # tags FR conservés
    assert "tag: isBilan ? 'Bilan' : 'Suivi'" in html


def test_buildDayGroup_onglets_briefing_par_defaut():
    # Vue jour en ONGLETS : le Briefing est visible par défaut, un menu (day-tabs)
    # donne accès aux autres rapports (Suivi/Bilan), un seul affiché à la fois.
    # Rendu via le pipeline unifié renderMarkdownInto (badges, fold…).
    html = _html()
    start = html.index("function buildDayGroup(dateIso, opts)")
    end = html.index("function buildTodayView()", start)
    body = html[start:end]
    assert "day-tabs" in body and "day-tab" in body   # menu d'onglets
    assert "day-panel" in body
    assert "renderMarkdownInto(panel, item.md)" in body   # pipeline unifié
    assert "showItem(ordered[0]" in body                  # Briefing (1er) par défaut


def test_buildDayGroup_degradation_propre_un_rapport_par_existence():
    # On n'ajoute que les rapports qui existent : aucune section vide forcée.
    # ordered est rempli à partir des seuls briefings/dayReports présents.
    html = _html()
    start = html.index("function buildDayGroup(dateIso, opts)")
    end = html.index("function buildTodayView()", start)
    body = html[start:end]
    assert "const ordered = [];" in body
    # Pas de placeholder « slot fixe » : on itère sur ce qui est réellement là.
    assert "dayReports.forEach(r =>" in body


# ---------------------------------------------------------------------------
# selectDay : présente la journée comme « Aujourd'hui » (briefing ouvert)
# ---------------------------------------------------------------------------

def test_selectDay_defini_et_rend_le_groupe_dans_le_contenu():
    html = _html()
    assert "function selectDay(dateIso)" in html
    # Le groupe est inséré dans la zone de lecture principale.
    assert "content.appendChild(grp);" in html
    # Le jour est ouvert, briefing (1er rapport) ouvert par défaut = lecture primaire.
    assert "buildDayGroup(dateIso, { openDay: true, openFirstReport: true })" in html


def test_selectDay_degradation_propre_si_jour_vide():
    # Jour sans aucun briefing ni rapport → message neutre, pas de crash.
    html = _html()
    assert "if (briefings.length === 0 && dayReports.length === 0) {" in html
    assert "Aucun rapport pour ce jour." in html


def test_selectDay_met_a_jour_hash_et_titre():
    html = _html()
    assert "history.replaceState(null, '', '#jour=' + encodeURIComponent(dateIso));" in html
    # Pas d'ancien selectBulletin/appendDayFil résiduel.
    assert "function selectBulletin(" not in html
    assert "function appendDayFil(" not in html


# ---------------------------------------------------------------------------
# CSS : l'accordéon today-day/today-report (réutilisé) est présent
# ---------------------------------------------------------------------------

def test_css_today_accordion_present_et_reutilise_les_variables():
    html = _html()
    assert ".today-day {" in html
    assert ".today-report {" in html
    assert ".today-report .report-body {" in html
    # Réutilise les tokens existants, pas un nouveau thème.
    assert "var(--border)" in html
    assert "var(--bg-panel)" in html
    # L'ancien thème day-fil-* a été retiré (un seul système).
    assert ".day-fil-report {" not in html
    assert ".day-fil-sep {" not in html
