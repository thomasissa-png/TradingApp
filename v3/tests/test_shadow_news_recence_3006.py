"""Instrument SHADOW « récence des news » (fondateur 30/06) : repère quand une news
FRAÎCHE à fort impact contredit notre call du jour (cas cacao : call LONG, news
fraîche baissière « offre abondante »). Zéro impact décisionnel — pure mesure.
"""
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import bilan_jour as bj  # noqa: E402

TODAY = date(2026, 6, 30)


def _ev(impacts, materiality="high", d="2026-06-29", trigger="titre", cat="commodity"):
    return {"date": d, "materiality": materiality, "impacts": impacts,
            "trigger": trigger, "cours": "", "cat": cat}


def test_news_fraiche_contra_call_flaggee():
    """Cacao LONG + news fraîche high COCOA:SHORT → signalé (pris à contre-pied)."""
    evs = [_ev("COCOA:SHORT:high", trigger="Offre mondiale plus abondante")]
    out = bj.shadow_news_fraiche_contra_call({"Cacao": "LONG"}, evs, TODAY)
    assert len(out) == 1
    assert out[0]["actif"] == "Cacao" and out[0]["call"] == "LONG"
    assert out[0]["news_dir"] == "SHORT"
    assert "abondante" in out[0]["titre"]


def test_news_alignee_non_flaggee():
    """News fraîche dans LE SENS du call → rien à signaler."""
    evs = [_ev("COCOA:LONG:high")]
    assert bj.shadow_news_fraiche_contra_call({"Cacao": "LONG"}, evs, TODAY) == []


def test_news_perimee_non_flaggee():
    """News contra mais VIEILLE (au-delà de fresh_jours) → pas fraîche → ignorée."""
    evs = [_ev("COCOA:SHORT:high", d="2026-06-25")]  # > 2 jours avant le 30
    assert bj.shadow_news_fraiche_contra_call({"Cacao": "LONG"}, evs, TODAY, fresh_jours=2) == []


def test_news_faible_impact_non_flaggee():
    """Contra mais materiality medium → pas 'fort impact' → ignorée.

    (La matérialité vit dans la COLONNE `materiality` de l'events-log, pas dans
    le 3e champ des impacts — celui-ci est une confidence numérique.)"""
    evs = [_ev("COCOA:SHORT:high", materiality="medium")]
    assert bj.shadow_news_fraiche_contra_call({"Cacao": "LONG"}, evs, TODAY) == []


def test_actif_non_parie_ignore():
    """News contra sur un actif qu'on n'a PAS parié → hors périmètre."""
    evs = [_ev("COCOA:SHORT:high")]
    assert bj.shadow_news_fraiche_contra_call({"Or": "SHORT"}, evs, TODAY) == []


def test_un_par_actif_le_plus_frais():
    """Deux news contra sur le même actif → une seule (la plus fraîche)."""
    evs = [
        _ev("COCOA:SHORT:high", d="2026-06-29", trigger="ancienne"),
        _ev("COCOA:SHORT:high", d="2026-06-30", trigger="fraiche"),
    ]
    out = bj.shadow_news_fraiche_contra_call({"Cacao": "LONG"}, evs, TODAY)
    assert len(out) == 1 and out[0]["date"] == "2026-06-30" and out[0]["titre"] == "fraiche"


def test_libelle_tolerant_petrole_brent():
    """Le call « Pétrole (Brent) » matche l'event BRENT → « Pétrole » (norme tolérante)."""
    evs = [_ev("BRENT:LONG:high")]  # news haussière vs call SHORT
    out = bj.shadow_news_fraiche_contra_call({"Pétrole (Brent)": "SHORT"}, evs, TODAY)
    assert len(out) == 1 and out[0]["actif"] == "Pétrole (Brent)" and out[0]["news_dir"] == "LONG"


def test_aucun_call_aucune_news_liste_vide():
    assert bj.shadow_news_fraiche_contra_call({}, [], TODAY) == []
