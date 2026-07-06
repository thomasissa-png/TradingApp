"""[Point 1 — 03/07] Suffixe « pré-publication » sur les Top actus du Décor.

Le jour d'un catalyseur J0 (NFP/CPI/FOMC...), une news des Top actus dont le
TITRE cite l'événement mais générée AVANT l'heure de publication porte le suffixe
« (avant la publication : rapport précédent ou anticipation) ».

Cas couverts (mockés, zéro I/O réseau) :
- cas de référence : « Rapport NFP américain décevant, dollar baisse » à 07h23 le
  03/07 (jour NFP) → suffixé ;
- jour SANS catalyseur → aucun suffixe ;
- news datée/générée APRÈS l'heure de publication (15h00) → aucun suffixe ;
- titre qui ne matche pas les mots-clés du catalyseur → aucun suffixe.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import briefing  # noqa: E402

# Noms de catalyseurs tels que fournis par le calendrier statique (config).
NOM_NFP = "Emploi US (NFP / rapport mensuel)"
NOM_FOMC = "Décision de taux Fed (FOMC)"

# Bulletin généré le 03/07 à 07h23 (matin) — toujours AVANT la publication NFP.
NOW_MATIN = datetime(2026, 7, 3, 7, 23)
# Même jour mais après l'heure de publication NFP (14h30 Paris).
NOW_APRES = datetime(2026, 7, 3, 15, 0)


def _ev(trigger: str, materiality: str = "high", impacts: str = "GOLD:SHORT:80") -> dict:
    """Event minimal exploitable par _top_news_lignes (actif résolu via impacts)."""
    return {
        "date": "2026-07-03",
        "trigger": trigger,
        "materiality": materiality,
        "impacts": impacts,
        "cours": "",
        "source": "reuters",
    }


TRIGGER_NFP = "Rapport NFP américain décevant, dollar baisse"


def test_reference_nfp_avant_publication_est_suffixe():
    """Cas de référence : news NFP à 07h23 le jour du NFP → suffixée."""
    lignes = briefing._top_news_lignes(
        [_ev(TRIGGER_NFP)], now=NOW_MATIN, cats_noms=[NOM_NFP]
    )
    assert lignes, "la news high devrait apparaître dans le top"
    assert briefing.PRE_PUBLICATION_SUFFIX in lignes[0]
    assert TRIGGER_NFP in lignes[0]


def test_jour_sans_catalyseur_aucun_suffixe():
    """Aucun catalyseur J0 → aucune news suffixée, même si le titre cite « NFP »."""
    lignes = briefing._top_news_lignes(
        [_ev(TRIGGER_NFP)], now=NOW_MATIN, cats_noms=[]
    )
    assert lignes
    assert briefing.PRE_PUBLICATION_SUFFIX not in lignes[0]


def test_news_apres_heure_publication_aucun_suffixe():
    """News générée APRÈS l'heure de publication (15h00 > 14h30) → pas de suffixe
    (c'est le résultat, pas une anticipation)."""
    lignes = briefing._top_news_lignes(
        [_ev(TRIGGER_NFP)], now=NOW_APRES, cats_noms=[NOM_NFP]
    )
    assert lignes
    assert briefing.PRE_PUBLICATION_SUFFIX not in lignes[0]


def test_titre_hors_sujet_aucun_suffixe():
    """Jour NFP mais titre qui ne cite pas l'événement → pas de suffixe."""
    lignes = briefing._top_news_lignes(
        [_ev("Or en hausse sur fond de tensions géopolitiques")],
        now=NOW_MATIN,
        cats_noms=[NOM_NFP],
    )
    assert lignes
    assert briefing.PRE_PUBLICATION_SUFFIX not in lignes[0]


def test_fomc_heure_specifique_20h():
    """FOMC publié à 20h Paris : une news « FOMC » à 07h23 est bien pré-publication."""
    lignes = briefing._top_news_lignes(
        [_ev("Anticipations avant la décision FOMC de ce soir")],
        now=NOW_MATIN,
        cats_noms=[NOM_FOMC],
    )
    assert lignes
    assert briefing.PRE_PUBLICATION_SUFFIX in lignes[0]


def test_backward_compat_sans_now_ni_cats():
    """Appel legacy (sans now/cats) → jamais de suffixe (rétrocompat des tests)."""
    lignes = briefing._top_news_lignes([_ev(TRIGGER_NFP)])
    assert lignes
    assert briefing.PRE_PUBLICATION_SUFFIX not in lignes[0]


def test_build_intro_block_reference_bout_en_bout(monkeypatch):
    """Intégration : build_intro_block à 07h23 le jour du NFP suffixe la news NFP."""
    monkeypatch.setattr(briefing, "_catalyseurs_j0_noms", lambda now: [NOM_NFP])
    impactful = [_ev(TRIGGER_NFP)]
    groups = briefing.group_by_actif(impactful)
    lines = briefing.build_intro_block(
        impactful, groups, date(2026, 7, 3), NOW_MATIN
    )
    txt = "\n".join(lines)
    assert "## Décor du jour" in txt
    assert "Catalyseur(s) attendu(s) aujourd'hui" in txt
    assert briefing.PRE_PUBLICATION_SUFFIX in txt
