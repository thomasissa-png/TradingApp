"""Tests des correctifs de FORME sur les news du bulletin (audit trio).

#6a — dédup des news identiques AU SEIN d'un même actif (briefing.py)
#6b — troncature propre du rationale sur frontière de phrase/mot (journaliste.py)
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import briefing  # noqa: E402
import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# #6a — Dédup des news intra-actif (briefing._dedup_news_in_actif)
# ---------------------------------------------------------------------------

def _ev(trigger: str, source: str = "cnbc_top") -> dict:
    return {"trigger": trigger, "source": source}


def test_dedup_two_identical_news_collapse_to_one():
    """Deux news identiques (même titre + source) → une seule après dédup."""
    title = "SoftBank annonce 75 milliards d'euros d'investissements IA en France"
    evs = [_ev(title), _ev(title)]
    out = briefing._dedup_news_in_actif(evs)
    assert len(out) == 1
    assert out[0]["trigger"] == title


def test_dedup_identical_ignores_case_and_whitespace():
    """Casse et espaces multiples ne doivent pas empêcher la dédup."""
    evs = [
        _ev("SoftBank annonce 75 milliards"),
        _ev("  softbank   ANNONCE 75   milliards  "),
    ]
    out = briefing._dedup_news_in_actif(evs)
    assert len(out) == 1


def test_dedup_keeps_two_different_news():
    """Deux news différentes → toutes deux gardées, ordre préservé."""
    evs = [
        _ev("SoftBank investit en France"),
        _ev("Nvidia dépasse les attentes au T1"),
    ]
    out = briefing._dedup_news_in_actif(evs)
    assert len(out) == 2
    assert out[0]["trigger"] == "SoftBank investit en France"
    assert out[1]["trigger"] == "Nvidia dépasse les attentes au T1"


def test_dedup_same_title_different_source_kept():
    """Même titre mais source différente → considérées distinctes (gardées)."""
    title = "SoftBank investit en France"
    evs = [_ev(title, source="cnbc_top"), _ev(title, source="bbc_business")]
    out = briefing._dedup_news_in_actif(evs)
    assert len(out) == 2


def test_dedup_keeps_first_occurrence_order():
    """La 1re occurrence est gardée, l'ordre global est préservé."""
    a = _ev("News A")
    b = _ev("News B")
    a_dup = _ev("News A")
    out = briefing._dedup_news_in_actif([a, b, a_dup])
    assert [e["trigger"] for e in out] == ["News A", "News B"]


def test_build_briefing_no_duplicate_news_in_section(tmp_path: Path):
    """E2E : une news dupliquée dans events-log ne sort qu'une fois (CAC 40)."""
    log = tmp_path / "events-log.md"
    title = "SoftBank annonce 75 milliards d'euros d'investissements IA en France"
    log.write_text(
        "# TradingApp v3 — Events log\n\n"
        "| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
        f"| 2026-05-29 | Indices | CAC 40 | {title} | CAC 40 (^FCHI) | intraday | 1 | cnbc_top | EU | macro |  |\n"
        f"| 2026-05-29 | Indices | CAC 40 | {title} | CAC 40 (^FCHI) | intraday | 1 | cnbc_top | EU | macro |  |\n",
        encoding="utf-8",
    )
    # P6/P7 — le détail per-actif est désormais rendu par build_news_par_actif
    # (section « ## News par actif » en fin de bulletin), plus par build_briefing
    # (qui ne porte que le « Décor du jour »). La dédup intra-actif y est testée.
    md = briefing.build_news_par_actif(events_path=log, today=date(2026, 5, 29))
    assert md.count(title) == 1


# ---------------------------------------------------------------------------
# #6b — Troncature propre du rationale (journaliste._truncate_clean)
# ---------------------------------------------------------------------------

def test_top_news_au_plus_un_par_actif():
    """RÉGRESSION (fondateur 30/06) : 3 dépêches d'agences différentes sur le MÊME
    événement (yen au plus bas) ont des titres distincts → la dédup titre+source ne
    les attrape pas. Le TOP doit quand même n'en garder qu'UNE (1 ligne par actif),
    pour la variété (le détail par actif garde tout)."""
    def _evt(trigger):
        return {"trigger": trigger, "source": "gnews_usdjpy", "materiality": "high",
                "impacts": "USDJPY:LONG:high", "cours": "", "cat": "macro",
                "date": "2026-06-30"}
    evs = [
        _evt("Yen au plus bas depuis 1986, risque d'intervention japonaise"),
        _evt("Le yen japonais atteint son plus bas niveau depuis 1986"),
        _evt("Yen chute à son plus bas niveau en 40 ans"),
    ]
    lignes = briefing._top_news_lignes(evs, max_news=3)
    usdjpy = [l for l in lignes if "USD/JPY" in l]
    assert len(usdjpy) == 1, f"attendu 1 ligne USD/JPY, eu {len(usdjpy)} : {lignes}"


def test_short_text_not_truncated():
    """Texte sous la limite → retourné intact, sans ellipse."""
    txt = "Le prix a déjà baissé de 15% sur 20 jours."
    assert jr._truncate_clean(txt, maxlen=240) == txt
    assert "…" not in jr._truncate_clean(txt, maxlen=240)


def test_long_text_truncated_on_word_boundary():
    """Texte long → coupé sur une frontière de mot, jamais en plein mot."""
    txt = (
        "Le prix a déjà fortement baissé de quinze pour cent sur les vingt "
        "derniers jours mais la configuration technique reste fragile et la "
        "confiance des investisseurs demeure incertaine pour les prochaines semaines"
    )
    out = jr._truncate_clean(txt, maxlen=120)
    assert len(out) <= 122  # maxlen + ellipse
    assert out.endswith("…")
    # le mot juste avant l'ellipse doit être un mot complet présent dans le texte
    last_word = out.rstrip(" …").rsplit(" ", 1)[-1]
    assert last_word in txt.split()


def test_truncate_prefers_sentence_boundary():
    """Si une fin de phrase existe dans la fenêtre → coupe à cette phrase."""
    txt = (
        "Le prix a baissé de 15% sur 20 jours. La configuration technique "
        "reste néanmoins fragile et incertaine pour la suite des opérations "
        "sur ce sous-jacent particulièrement volatil ces derniers temps."
    )
    out = jr._truncate_clean(txt, maxlen=80)
    assert out.startswith("Le prix a baissé de 15% sur 20 jours.")
    assert out.endswith("…")


def test_truncate_never_cuts_mid_word():
    """Aucune coupe en plein mot pour une série de longueurs limites."""
    txt = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo"
    for maxlen in range(15, 60):
        out = jr._truncate_clean(txt, maxlen=maxlen)
        if out.endswith("…"):
            stub = out.rstrip(" …")
            # le dernier token doit être un mot complet du texte source
            assert stub.rsplit(" ", 1)[-1] in txt.split()


def test_extract_news_rationale_uses_clean_truncation():
    """_extract_news_rationale tronque proprement (pas de coupe en plein mot)."""
    long_rat = (
        "Le prix a déjà baissé de quinze pour cent sur vingt jours mais la "
        "configuration reste fragile et la confiance des opérateurs demeure "
        "faible pour les prochaines semaines selon plusieurs indicateurs avancés."
    )
    record = {"criteres": [{"nature": "geopolitique", "synthese_rationale": long_rat}]}
    out = jr._extract_news_rationale(record)
    assert out is not None
    if out.endswith("…"):
        assert out.rstrip(" …").rsplit(" ", 1)[-1] in long_rat.split()
