"""TradingApp v3 — Gate C1 : cohérence de signe DeepSeek.

But (un seul, étroit) : empêcher qu'un impact news au sens INVERSÉ par DeepSeek
(ex. « OPEP augmente la production » classée HAUSSIER pétrole, ou « CPI hot »
classée HAUSSIER actions) ne contamine le score.

Stratégie (conservatrice, déterministe, EXTENSIBLE) :
- Table de règles macro NON AMBIGUËS uniquement (relations bien établies).
- Chaque règle = (asset cible, pattern de mots-clés détectable dans le
  titre/texte, direction de surprise) → direction de marché attendue.
- Détection sur titre + texte de la news + champ `cours`/asset cible.
- Si le sens DeepSeek CONTREDIT la direction attendue → `sign_conflict = True`.
- Action : NEUTRALISÉ (l'appelant ignore l'impact comme un n/a) + log WARNING
  + tracé. JAMAIS d'inversion (on n'a pas plus confiance dans notre règle que
  dans DeepSeek au point de flipper — on retire le signal douteux, pas plus).

Anti-faux-positif (essentiel) :
- N'agir QUE sur un match de pattern NET + direction de surprise NETTE.
- Aucun match clair → on ne touche à rien (zéro correction hasardeuse).
- C'est un garde-fou, pas un re-classifieur.
- Aucune règle ambiguë (ex. or sur CPI = AMBIGU → exclu volontairement).

Interface publique :
- `detect_sign_conflict(text, asset, ia_direction) -> Optional[ConflictHit]`
- `MACRO_SIGN_RULES` : table de règles (EXTENSIBLE — ajouter au bout)
- `RuleHit` / `ConflictHit` : dataclass pour la traçabilité

Utilisation côté triggers_classifier :
    hit = detect_sign_conflict(text, asset_id, direction)
    if hit is not None:
        # impact à neutraliser + tracer
        ...
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Sequence

logger = logging.getLogger("sign_consistency")


# =============================================================================
# Helpers texte (locaux — évite dépendance circulaire sur triggers_classifier)
# =============================================================================

def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s or "")
        if unicodedata.category(c) != "Mn"
    )


def _norm(s: str) -> str:
    """Lowercase + sans accents — pour comparaisons souples."""
    return _strip_accents(s or "").lower()


def _phrase_in(text_norm: str, phrase: str) -> bool:
    """Match phrase word-bounded (évite « war » dans « warm »).

    Pour une phrase multi-tokens, on accepte aussi un match « tokens AND »
    word-bounded : tous les tokens présents séparément dans le texte.
    """
    p = _norm(phrase).strip()
    if not p:
        return False
    # Match phrase exacte word-bounded
    pat = re.compile(rf"(?<![a-z0-9_]){re.escape(p)}(?![a-z0-9_])")
    if pat.search(text_norm):
        return True
    # Sinon tokens AND (uniquement si phrase multi-tokens)
    toks = [t for t in re.findall(r"[a-z0-9]+", p) if t]
    if len(toks) < 2:
        return False
    text_tokens = set(re.findall(r"[a-z0-9]+", text_norm))
    return all(t in text_tokens for t in toks)


def _any_phrase(text_norm: str, phrases: Sequence[str]) -> bool:
    return any(_phrase_in(text_norm, p) for p in phrases)


# =============================================================================
# Table de règles macro NON AMBIGUËS
# =============================================================================
# Chaque règle décrit :
#   - `name` : id court (pour log / trace decision-log)
#   - `assets` : ensemble d'assets cibles (id IA fermé : SP500, NASDAQ, ...).
#     L'asset DOIT figurer dans IA_ASSET_TO_ACTIF côté triggers_classifier.
#   - `subject_phrases` : mots-clés sujet (CPI, NFP, OPEP, EIA, Fed, ...)
#     identifiant le THÈME de la news. Tous case/accent-insensible.
#   - `surprise_up` : phrases qui signalent une surprise haussière du SUJET
#     (CPI plus chaud, taux qui montent, production qui augmente, stocks qui
#     gonflent, etc.) — DOIT être un cue net.
#   - `surprise_down` : phrases inverses (CPI plus froid, baisse de taux, OPEP
#     réduit, stocks qui chutent, dovish, ...).
#   - `expected_when_up` : direction de marché attendue si surprise_up matche
#     (LONG = haussier sur asset, SHORT = baissier).
#   - `expected_when_down` : direction attendue si surprise_down matche
#     (généralement l'inverse de expected_when_up).
#
# Règle d'or : on ne met QUE des relations économiques NON AMBIGUËS et bien
# établies. En cas de doute (ex. or sur CPI : peut être haussier via valeur
# refuge OU baissier via hausse réelle des taux) → on N'AJOUTE PAS.

@dataclass(frozen=True)
class MacroSignRule:
    name: str
    assets: frozenset
    subject_phrases: tuple
    surprise_up: tuple
    surprise_down: tuple
    expected_when_up: str    # "LONG" ou "SHORT"
    expected_when_down: str  # "LONG" ou "SHORT"


# Phrases « hausse / plus / au-dessus » et « baisse / moins / en-dessous » —
# vocabulaire FR+EN partagé par plusieurs règles.
_HOTTER = (
    "hot", "hotter", "higher", "above", "above expectations", "above forecast",
    "stronger", "exceeds", "exceeded", "beats", "beat", "tops", "topped",
    "surges", "surge", "jumps", "jump", "soars", "rises", "rise", "rising",
    "accelerates", "grimpe", "monte", "augmente", "depasse", "plus eleve",
    "plus chaud", "au-dessus", "au dessus", "superieur",
)
_COOLER = (
    "cool", "cooler", "lower", "below", "below expectations", "below forecast",
    "weaker", "misses", "miss", "missed", "falls", "fall", "falling",
    "drops", "drop", "declines", "decline", "slows", "ralentit", "baisse",
    "diminue", "recule", "plus bas", "plus froid", "en-dessous", "en dessous",
    "inferieur",
)


MACRO_SIGN_RULES: List[MacroSignRule] = [
    # -------------------------------------------------------------------------
    # CPI / inflation : hot → baissier actions, haussier USD (donc EUR/USD short)
    # -------------------------------------------------------------------------
    MacroSignRule(
        name="cpi_actions",
        assets=frozenset({"SP500", "NASDAQ", "CAC40"}),
        subject_phrases=(
            "cpi", "inflation", "consumer price", "prix a la consommation",
            "prix a la conso", "indice des prix",
        ),
        surprise_up=_HOTTER,
        surprise_down=_COOLER,
        expected_when_up="SHORT",
        expected_when_down="LONG",
    ),
    MacroSignRule(
        name="cpi_eurusd",
        assets=frozenset({"EURUSD"}),
        subject_phrases=(
            "us cpi", "u.s. cpi", "cpi americain", "inflation americaine",
            "inflation us", "consumer price",
        ),
        surprise_up=_HOTTER,
        surprise_down=_COOLER,
        expected_when_up="SHORT",   # USD se renforce → EUR/USD baisse
        expected_when_down="LONG",  # USD s'affaiblit → EUR/USD monte
    ),

    # -------------------------------------------------------------------------
    # Fed / taux directeurs : hike/hawkish → baissier actions, haussier USD ;
    # cut/dovish → inverse. On exige le SUJET « Fed / taux directeur » présent.
    # -------------------------------------------------------------------------
    MacroSignRule(
        name="fed_actions",
        assets=frozenset({"SP500", "NASDAQ", "CAC40"}),
        subject_phrases=(
            "fed", "federal reserve", "fomc", "powell",
            "bce", "ecb", "lagarde",
            "taux directeur", "policy rate", "interest rate",
        ),
        # Hausse de taux / hawkish
        surprise_up=(
            "hike", "hikes", "raises rates", "raise rates", "rate hike",
            "hausse de taux", "remonte les taux", "monte les taux",
            "hawkish", "restrictive",
        ),
        # Baisse de taux / dovish
        surprise_down=(
            "cut", "cuts", "rate cut", "lowers rates", "lower rates",
            "baisse de taux", "baisse les taux", "abaisse les taux",
            "dovish", "accomodante", "accommodative",
        ),
        expected_when_up="SHORT",   # hawkish/hike → actions down
        expected_when_down="LONG",  # dovish/cut → actions up
    ),
    MacroSignRule(
        name="fed_eurusd",
        assets=frozenset({"EURUSD"}),
        # On limite au sujet Fed (US) pour ne pas confondre avec BCE.
        subject_phrases=(
            "fed", "federal reserve", "fomc", "powell",
        ),
        surprise_up=(
            "hike", "hikes", "raises rates", "raise rates", "rate hike",
            "hausse de taux", "remonte les taux", "hawkish",
        ),
        surprise_down=(
            "cut", "cuts", "rate cut", "lowers rates", "lower rates",
            "baisse de taux", "abaisse les taux", "dovish",
        ),
        expected_when_up="SHORT",   # USD up → EUR/USD down
        expected_when_down="LONG",  # USD down → EUR/USD up
    ),

    # -------------------------------------------------------------------------
    # NFP / emploi US : stronger/higher → haussier USD (EUR/USD short)
    # -------------------------------------------------------------------------
    MacroSignRule(
        name="nfp_eurusd",
        assets=frozenset({"EURUSD"}),
        subject_phrases=(
            "nfp", "non-farm payrolls", "non farm payrolls", "nonfarm payrolls",
            "payrolls", "emploi americain", "us jobs", "us employment",
        ),
        surprise_up=_HOTTER,
        surprise_down=_COOLER,
        expected_when_up="SHORT",   # emploi fort → USD up → EUR/USD down
        expected_when_down="LONG",  # emploi faible → USD down → EUR/USD up
    ),
    # Chômage US (taux) — la convention de signe est inverse de NFP : un taux
    # de chômage qui MONTE est BAISSIER USD.
    MacroSignRule(
        name="unemployment_eurusd",
        assets=frozenset({"EURUSD"}),
        subject_phrases=(
            "unemployment rate", "taux de chomage", "jobless rate",
        ),
        surprise_up=_HOTTER,   # chômage en hausse
        surprise_down=_COOLER, # chômage en baisse
        expected_when_up="LONG",   # chômage up → USD down → EUR/USD up
        expected_when_down="SHORT",# chômage down → USD up → EUR/USD down
    ),

    # -------------------------------------------------------------------------
    # OPEP / OPEC production policy : augmente production → baissier pétrole ;
    # réduit → haussier. Relation 100% non ambiguë (offre).
    # -------------------------------------------------------------------------
    MacroSignRule(
        name="opec_production",
        assets=frozenset({"BRENT"}),
        subject_phrases=(
            "opec", "opep", "opec+", "opep+",
        ),
        # Augmentation de production / quotas
        surprise_up=(
            "raise production", "raises production", "raising production",
            "boost production", "boosts production", "boosting production",
            "increase production", "increases production", "increasing production",
            "increase output", "increases output", "raise output",
            "hike output", "hikes output", "boost output", "boosts output",
            "augmente la production", "augmenter la production",
            "augmente production", "hausse de production",
            "releve les quotas", "releve la production", "releve sa production",
            "augmente l'offre", "augmente loffre",
        ),
        # Baisse / coupe de production
        surprise_down=(
            "cut production", "cuts production", "cutting production",
            "reduce production", "reduces production", "reducing production",
            "lower production", "lowers production", "lowering production",
            "production cut", "production cuts", "output cut", "output cuts",
            "reduce output", "reduces output", "lower output", "lowers output",
            "baisse de production", "baisse la production",
            "reduit la production", "reduit production",
            "coupe de production", "coupe la production",
            "abaisse les quotas", "diminue la production",
        ),
        expected_when_up="SHORT",   # plus d'offre → prix baisse
        expected_when_down="LONG",  # moins d'offre → prix monte
    ),

    # -------------------------------------------------------------------------
    # EIA / stocks pétrole hebdo : build/rise → baissier ; draw/fall → haussier
    # -------------------------------------------------------------------------
    MacroSignRule(
        name="eia_stocks",
        assets=frozenset({"BRENT"}),
        subject_phrases=(
            "eia", "crude oil inventories", "crude inventories",
            "oil stockpiles", "oil stocks", "stocks de petrole",
            "stocks petroliers", "stocks de brut",
        ),
        # Stocks en hausse (build)
        surprise_up=(
            "build", "builds", "rise", "rises", "rising", "jump", "jumps",
            "surge", "surges", "increase", "increases", "increased",
            "higher", "hausse", "grimpent", "augmentent", "augmente",
            "en hausse",
        ),
        # Stocks en baisse (draw)
        surprise_down=(
            "draw", "draws", "fall", "falls", "drop", "drops", "decline",
            "declines", "decrease", "decreases", "decreased", "lower",
            "baisse", "baissent", "reculent", "diminuent", "en baisse",
            "chute",
        ),
        expected_when_up="SHORT",   # plus de stocks → baissier pétrole
        expected_when_down="LONG",  # moins de stocks → haussier pétrole
    ),
]


# =============================================================================
# Détection
# =============================================================================

@dataclass(frozen=True)
class ConflictHit:
    """Résultat d'une détection : impact à neutraliser.

    Champs traçables (decision-log + log WARNING) :
    - rule_name : id de la règle déclenchée
    - asset : asset IA cible (BRENT, SP500, ...)
    - expected_direction : direction de marché attendue (LONG/SHORT)
    - ia_direction : direction DeepSeek (LONG/SHORT) — celle qui contredit
    - matched_subject : phrase sujet qui a matché (debug)
    - matched_surprise : phrase de surprise qui a matché (debug)
    - surprise_polarity : "up" ou "down"
    """
    rule_name: str
    asset: str
    expected_direction: str
    ia_direction: str
    matched_subject: str
    matched_surprise: str
    surprise_polarity: str


def detect_sign_conflict(
    text: str, asset: str, ia_direction: str,
) -> Optional[ConflictHit]:
    """Détecte un conflit de signe DeepSeek vs règles macro NON AMBIGUËS.

    Args:
        text : titre + texte concaténés de la news (sans normalisation préalable).
        asset : asset IA cible (BRENT, SP500, NASDAQ, CAC40, EURUSD, ...).
        ia_direction : direction DeepSeek pour cet asset ("LONG" ou "SHORT").

    Returns:
        ConflictHit si conflit NET détecté, None sinon (incluant : pas de
        règle pour cet asset, sujet non matché, surprise non claire, sens
        DeepSeek non tradable).

    Anti-faux-positif :
    - Pas de match sujet NET → None (zéro action).
    - Pas de surprise NETTE (ni up ni down) → None.
    - Surprise up ET down matchent en même temps → None (ambigu).
    - ia_direction n'est pas LONG/SHORT → None.

    Idempotent et déterministe. Aucun side-effect : c'est l'appelant qui
    décide de neutraliser + logger.
    """
    if not text or not asset or ia_direction not in ("LONG", "SHORT"):
        return None
    text_norm = _norm(text)
    if not text_norm:
        return None

    for rule in MACRO_SIGN_RULES:
        if asset not in rule.assets:
            continue
        # 1) Sujet matché ?
        subj = None
        for s in rule.subject_phrases:
            if _phrase_in(text_norm, s):
                subj = s
                break
        if subj is None:
            continue
        # 2) Surprise NETTE (exactement un côté) ?
        up_hit = None
        for p in rule.surprise_up:
            if _phrase_in(text_norm, p):
                up_hit = p
                break
        down_hit = None
        for p in rule.surprise_down:
            if _phrase_in(text_norm, p):
                down_hit = p
                break
        if (up_hit is None) == (down_hit is None):
            # 0 surprise OU 2 surprises (ambigu) → skip
            continue
        if up_hit is not None:
            expected = rule.expected_when_up
            matched_surprise = up_hit
            polarity = "up"
        else:
            expected = rule.expected_when_down
            matched_surprise = down_hit or ""
            polarity = "down"
        # 3) Conflit ?
        if expected != ia_direction:
            return ConflictHit(
                rule_name=rule.name,
                asset=asset,
                expected_direction=expected,
                ia_direction=ia_direction,
                matched_subject=subj,
                matched_surprise=matched_surprise,
                surprise_polarity=polarity,
            )
        # Cohérent → rien à signaler, on continue (une autre règle pourrait
        # matcher mais c'est rare ; si elle matche aussi cohérente, OK).
    return None


__all__ = [
    "MACRO_SIGN_RULES",
    "MacroSignRule",
    "ConflictHit",
    "detect_sign_conflict",
]
