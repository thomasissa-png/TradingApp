"""Volet 2 (décision 23/06) — une news HIGH fraîche unidirectionnelle DOIT
pouvoir porter le signe net du carrier sur le 24h, même quand la synthèse nette
DeepSeek du corpus retombe en « faible/neutral » (net dilué par d'anciennes news).

CONTEXTE DU BUG (Pétrole 24h, 23/06) :
- Le porteur du net news pétrole = `geopol_iran` (cle_courante
  `tension_geopol_moyen_orient`, poids 7, pertinence 24h boostée à 1.0).
- Le net DeepSeek du corpus est ressorti « faible » (dilué par d'anciennes news
  Brent LONG type Hormuz/escalade) → niveau-2 → critère news = 0.
- Résultat : malgré le poids 7 + pertinence 1.0, le critère news pesait 0 sur le
  24h ; le SHORT était porté par la SEULE tendance 20j résiduelle (−1.63).
- La grosse news fraîche « USA lèvent sanctions Iran → BRENT SHORT high » ne se
  matérialisait nulle part.

FIX (triggers_classifier, niveau-2 du carrier) : avant d'abandonner à val=0, on
tente un filet « news IA high FRAÎCHE et UNIDIRECTIONNELLE » (≤ 72h, zéro high à
contre-sens). Si trouvé → val signée (±1), source_track="ia_synthese_news_high".
Conservateur : conflit high (2 sens) ou rien de high frais → on reste à 0.

Ce que ce fichier prouve :
1. News high fraîche SHORT BRENT + synthèse faible → carrier passe à −1 (au lieu
   de 0). C'est ce signe ±1 qui, ×poids 7 ×pertinence 24h 1.0, fait peser la news
   dans le 24h (et lui permet de dépasser la tendance 20j résiduelle).
2. Conflit high (LONG + SHORT) → on reste à 0 (pas d'invention de direction).
3. News SHORT mais MEDIUM (pas high) → on reste à 0 (le filet n'abaisse pas le
   seuil de matérialité — seul un signal high est assez fort pour le filet).
4. News high mais ANCIENNE (> 72h) → on reste à 0 (filet réservé au frais).
5. Non-régression : synthèse HIGH directionnelle → niveau-1 inchangé (ia_synthese).
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import triggers_classifier as tc  # noqa: E402


NOW = datetime(2026, 6, 23, 8, 0, tzinfo=timezone.utc)

# Synthèse DeepSeek « faible » du corpus pétrole (le net est dilué).
SYNTH_FAIBLE = {"direction": "NEUTRAL", "conviction": "low",
                "rationale": "corpus dilué (anciennes news Hormuz LONG)"}
# Synthèse HIGH directionnelle (cas niveau-1 historique, non-régression).
SYNTH_HIGH_SHORT = {"direction": "SHORT", "conviction": "high",
                    "rationale": "récit baissier net"}


def _event_brent(direction: str, materiality: str, age_hours: float,
                 trigger: str) -> dict:
    """Event IA factice ciblant BRENT (→ petrole), prêt pour _candidates_for /
    _ia_direction_for. `_dt` et `_canonical_dt` posés directement (on court-circuite
    le parsing — c'est un test unitaire de la logique de routage, pas du parsing)."""
    dt = NOW - timedelta(hours=age_hours)
    return {
        "trigger": trigger,
        "category": "geopolitical",
        "materiality": materiality,
        "reliability": "high",
        "nature": "ponctuel",
        "event_id": "test_" + trigger[:8].replace(" ", "_"),
        "_dt": dt,
        "_canonical_dt": dt,
        "_impacts": [{"asset": "BRENT", "direction": direction,
                      "confidence": "high"}],
    }


def _resolve(events, synth):
    spec = tc.load_triggers_config()["petrole"]["geopol_iran"]
    return tc._resolve_triplet_with_meta(
        events,
        "petrole",
        "geopol_iran",
        spec.get("long_keywords", []) or [],
        spec.get("short_keywords", []) or [],
        int(spec.get("horizon_lookback_jours", 7)),
        NOW,
        synthese=synth,
    )


# ---------------------------------------------------------------------------
# 1. PREUVE — news high fraîche SHORT + synthèse faible → carrier = −1
# ---------------------------------------------------------------------------

def test_news_high_fraiche_short_domine_malgre_synthese_faible():
    ev = _event_brent("SHORT", "high", age_hours=6.0,
                      trigger="USA levent les sanctions sur le petrole iranien")
    val, meta = _resolve([ev], SYNTH_FAIBLE)
    # AVANT le fix : val == 0 (ia_synthese_faible). APRÈS : −1, news high portée.
    assert val == -1, "une news high fraîche SHORT doit matérialiser le signe net"
    assert meta["source_track"] == "ia_synthese_news_high"
    assert meta["materiality"] == "high"

    # PREUVE chiffrée de la domination 24h : le signe net (−1) × poids 7 ×
    # pertinence 24h 1.0 (= 7.0 en magnitude pré-normalisation) dépasse en valeur
    # absolue la contribution de la tendance 20j résiduelle observée (|−1.63|).
    # On reconstitue l'ordre de grandeur de la contribution news 24h vs 20j.
    contrib_news_24h = abs(val) * 7.0 * 1.0          # poids 7, pertinence 24h 1.0
    contrib_momentum_20j_24h = 6.0 * 0.4 * 0.6786    # poids 6, pert 0.4, |norm| observé
    assert contrib_news_24h > contrib_momentum_20j_24h, (
        f"news 24h ({contrib_news_24h:.2f}) doit dépasser la tendance 20j "
        f"résiduelle ({contrib_momentum_20j_24h:.2f})"
    )


# ---------------------------------------------------------------------------
# 2. CONSERVATEUR — conflit high (LONG + SHORT) → on reste à 0
# ---------------------------------------------------------------------------

def test_conflit_high_reste_neutre():
    ev_short = _event_brent("SHORT", "high", age_hours=6.0,
                            trigger="USA levent les sanctions Iran")
    ev_long = _event_brent("LONG", "high", age_hours=5.0,
                           trigger="frappes sur le detroit d Ormuz")
    val, meta = _resolve([ev_short, ev_long], SYNTH_FAIBLE)
    assert val == 0, "conflit high → pas d'invention de direction"
    assert meta["source_track"] == "ia_synthese_faible"


# ---------------------------------------------------------------------------
# 3. SEUIL — news SHORT MEDIUM (pas high) → on reste à 0
# ---------------------------------------------------------------------------

def test_news_medium_ne_declenche_pas_le_filet():
    ev = _event_brent("SHORT", "medium", age_hours=6.0,
                      trigger="rumeur de hausse de quota OPEC")
    val, meta = _resolve([ev], SYNTH_FAIBLE)
    assert val == 0, "le filet exige une matérialité HIGH"
    assert meta["source_track"] == "ia_synthese_faible"


# ---------------------------------------------------------------------------
# 4. FRAÎCHEUR — news high ANCIENNE (> 72h) → on reste à 0
# ---------------------------------------------------------------------------

def test_news_high_ancienne_ne_declenche_pas_le_filet():
    ev = _event_brent("SHORT", "high", age_hours=100.0,
                      trigger="vieille news sanctions Iran")
    val, meta = _resolve([ev], SYNTH_FAIBLE)
    assert val == 0, "le filet est réservé au frais (≤ 72h)"
    assert meta["source_track"] == "ia_synthese_faible"


# ---------------------------------------------------------------------------
# 5. NON-RÉGRESSION — synthèse HIGH directionnelle → niveau-1 inchangé
# ---------------------------------------------------------------------------

def test_synthese_high_directionnelle_inchangee():
    ev = _event_brent("SHORT", "high", age_hours=6.0,
                      trigger="USA levent les sanctions Iran")
    val, meta = _resolve([ev], SYNTH_HIGH_SHORT)
    assert val == -1
    # La synthèse high prime : on reste sur le track historique ia_synthese,
    # PAS sur le filet niveau-2.
    assert meta["source_track"] == "ia_synthese"
