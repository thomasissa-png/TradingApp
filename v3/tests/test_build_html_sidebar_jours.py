"""Tests build_html — sidebar « historique » : un jour = une entrée, sans heure.

Refonte navigation (session 06-20). La liste latérale des bulletins
(`#bulletin-list`) regroupe désormais par JOUR :
- déduplication par date (plusieurs bulletins le même jour → une seule entrée),
- libellé SANS heure/créneau (« ven. 19 juin », pas « ven. 19 juin · 08h »),
- badge « dernier » conservé sur le jour le plus récent,
- clic → selectDay(date) (journée dépliable, cf. test_build_html_day_fil).

Le rendu de la liste est fait côté client (JS embarqué). Les tests vérifient le
contrat statique du JS généré. Présentation pure — WIN RATE ONLY, UTF-8/français.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_html as bh  # noqa: E402


def _html() -> str:
    return bh.render_html([], 0, reports=[], weekly=None)


def test_listDays_deduplique_par_date():
    html = _html()
    assert "function listDays()" in html
    # 1er bulletin rencontré par date = ancre (BULLETINS trié récent d'abord) ;
    # les doublons du même jour ne créent pas de seconde entrée.
    assert "if (!byDay[d]) byDay[d] = { date: d, briefingId: b.id };" in html
    # Un jour avec seulement suivi/bilan (sans briefing) apparaît aussi.
    assert "if (r.date && !byDay[r.date]) byDay[r.date] = { date: r.date, briefingId: null };" in html


def test_renderList_libelle_sans_heure():
    html = _html()
    assert "function renderList(activeDate)" in html
    # Libellé = la date seule (dt.short), JAMAIS le créneau/heure.
    assert "dateSpan.textContent = dt.short;" in html
    # On ne réintroduit pas l'ancien format « date · slot » dans la sidebar.
    assert "`${dt.short} · ${slotTxt}`" not in html


def test_renderList_une_entree_par_jour_et_clic_selectDay():
    html = _html()
    # La liste itère sur les JOURS dédupliqués (puis intercale les bilans semaine).
    assert "const days = listDays();" in html
    assert "days.forEach(d => entries.push({ kind: 'day', date: d.date }));" in html
    # Clic sur un jour → selectDay(date) (journée en onglets), plus selectBulletin(id).
    assert "selectDay(en.date);" in html


def test_renderList_jour_recent_gras_sans_badge():
    # Refonte S9 : la pastille verte « DERNIER » est retirée (redondante avec le
    # tri récent-d'abord + l'entrée « Aujourd'hui »). Le jour le plus récent garde
    # un repère DOUX : la classe .latest (léger gras), sans badge.
    html = _html()
    assert "const latestDate = days.length > 0 ? days[0].date : null;" in html
    assert "if (en.date === latestDate) a.classList.add('latest');" in html
    assert "badge.textContent = 'dernier';" not in html
    assert "badge-latest" not in html


def test_renderList_bilans_semaine_dans_le_menu():
    # (B) Les bilans de semaine apparaissent dans le menu, datés à leur dimanche,
    # marqués « (bilan) », et le clic ouvre la vue Bilan semaine sur CE bilan.
    html = _html()
    assert "(WEEKLIES || []).forEach(w =>" in html
    assert "dateSpan.textContent = dt.short + ' (bilan)';" in html
    assert "showWeek(en.weekly);" in html


def test_hash_route_par_jour_et_retrocompat_id():
    # Le hash devient « #jour=YYYY-MM-DD » ; un ancien hash d'id de bulletin
    # (ex. lien partagé « 2026-06-16T05... ») retombe sur sa date.
    html = _html()
    assert "a.href = '#jour=' + encodeURIComponent(en.date);" in html
    assert "const jm = hash.match(" in html
    assert "selectDay(known ? target : days[0].date);" in html
