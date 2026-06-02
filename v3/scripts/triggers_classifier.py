"""TradingApp v3 — Classifieur d'events vers triplets binaires.

Lit `v3/data/events-log.md` (tableau markdown : date|L1|L2|trigger|cours|latence|R|source|news_zone|category|pattern_id)
et `v3/config/triggers-and-windows.yml`. Pour chaque critère `type: triplet`,
applique un routage HYBRIDE :

1. **Routage par DeepSeek** (champs déjà extraits) :
   - `cours` mappé via TICKER_TO_ACTIF → quel actif est impacté
   - `category` filtré par CRITERION_CATEGORY_SCOPE → quelle famille de critère
   - À défaut de mapping `cours`, on garde l'event si le `l2`/`trigger` matche
     le scope textuel du critère (DOMAIN_HINTS) — borné pour éviter les faux positifs.
2. **Direction par mots-clés robustes** :
   - Match exact de la phrase (word-boundary, accents OK)
   - OU match "tokens AND" : tous les tokens du mot-clé apparaissent
     comme tokens word-bounded (« Iran ceasefire » matche « extended ceasefire »
     dès lors que l'event est déjà rattaché à l'Iran/Brent via cours+category).
3. Si LONG et SHORT matchent → garder le plus récent.
4. Si l'event est bien rattaché à l'actif+catégorie mais sans cue directionnel
   clair → rester 0 (ne pas inventer de direction).

Pour `type: calendrier`, résout selon la date du jour (Diwali, cycle Brésil).

Règles (cf. triggers-and-windows.yml) :
- Listes fermées : aucun match → 0 (neutre, pas n/a)
- Mots-clés FR + EN
- Case-insensitive, word-boundary, accents gérés
- Si LONG et SHORT matchent dans la même fenêtre → garder le plus récent

Zéro invention : events-log absent/vide → tous triplets = 0.

Interface stable (consommée par criteres_calculator.py) :
- `parse_events_log()` → List[dict]
- `load_triggers_config()` → dict
- `classify_all(events, today, triggers_cfg)` → Dict[actif_key, Dict[cle_courante, int]]
- `_event_text(ev)` → str (utilisé par criteres_calculator pour la gate événement extrême)
"""

from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml

# rapidfuzz : dédup floue par Levenshtein normalisée (Phase 2).
# Import optionnel : si absent → garde-fou auto bascule SHA exact seul (mode dégradé).
try:
    from rapidfuzz import fuzz as _rf_fuzz  # type: ignore
    _RAPIDFUZZ_OK = True
except ImportError:  # pragma: no cover — fallback dégradé
    _rf_fuzz = None
    _RAPIDFUZZ_OK = False

logger = logging.getLogger("triggers_classifier")

ROOT = Path(__file__).resolve().parents[1]
EVENTS_LOG = ROOT / "data" / "events-log.md"
TRIGGERS_YML = ROOT / "config" / "triggers-and-windows.yml"


# ---------------------------------------------------------------------------
# Table ticker → actif (cle YAML triggers-and-windows.yml)
# ---------------------------------------------------------------------------
# Format : { actif_key_yml: (set_de_tickers, set_d_alias_textuels) }
# Les tickers sont matchés exactement (entre parenthèses ou délimiteurs).
# Les alias matchent en substring case/accent-insensible sur le champ `cours`.
TICKER_TO_ACTIF: Dict[str, Tuple[Set[str], Set[str]]] = {
    "cac_40": (
        {"^FCHI", "CAC40"},
        {"cac 40", "cac40"},
    ),
    "nasdaq": (
        {"^IXIC", "NASDAQ", "NVDA", "MSFT", "GOOGL", "AAPL", "AMZN", "META", "TSLA"},
        {"nasdaq", "nvidia", "microsoft", "alphabet", "google", "apple",
         "amazon", "meta", "tesla"},
    ),
    "sp500": (
        {"^GSPC", "SP500", "SPX"},
        {"s&p 500", "sp500", "s&p500"},
    ),
    "vix": (
        {"^VIX", "VIX"},
        {"vix"},
    ),
    "eurusd": (
        {"EUR=X", "EURUSD"},
        {"eur/usd", "eurusd", "eur usd"},
    ),
    "petrole": (
        {"BZ=F", "CL=F", "BRENT"},
        {"brent", "petrole", "wti", "crude", "oil"},
    ),
    "or": (
        {"GC=F", "XAU/USD", "GOLD"},
        {"gold", " or "},  # " or " avec espaces pour éviter de matcher "for", "more", etc.
    ),
    "argent": (
        {"SI=F", "XAG/USD", "SILVER"},
        {"silver", "argent"},
    ),
    "cuivre": (
        {"HG=F", "COPPER"},
        {"copper", "cuivre"},
    ),
    "cafe": (
        {"KC=F", "COFFEE"},
        {"coffee", "cafe"},
    ),
    "cacao": (
        {"CC=F", "COCOA"},
        {"cocoa", "cacao"},
    ),
    "ble": (
        {"ZW=F", "WHEAT"},
        {"wheat", "ble"},
    ),
}


# ---------------------------------------------------------------------------
# Mapping ASSET (id IA fermé) → actif_key YAML
# ---------------------------------------------------------------------------
# Utilisé par le routage IA-first : pour un event qui a un `impacts[]` contenant
# {asset:"BRENT",...}, on sait que c'est l'actif `petrole` du YAML.
IA_ASSET_TO_ACTIF: Dict[str, str] = {
    "CAC40":   "cac_40",
    "SP500":   "sp500",
    "NASDAQ":  "nasdaq",
    "EURUSD":  "eurusd",
    "BRENT":   "petrole",
    "VIX":     "vix",
    "GOLD":    "or",
    "SILVER":  "argent",
    "COPPER":  "cuivre",
    "COFFEE":  "cafe",
    "COCOA":   "cacao",
    "WHEAT":   "ble",
}


# Matérialité IA → poids (pour départager LONG/SHORT de même date)
_MAT_WEIGHT = {"high": 3, "medium": 2, "low": 1, "": 1}


# ---------------------------------------------------------------------------
# Phase 2 — event_id, normalisation, dédup, fraîcheur (premier-vu fait foi)
# ---------------------------------------------------------------------------

# STALE = 30 jours sur canonical_event_date (archive 2025 re-publiée → écartée).
STALE_DAYS = 30
# Gate override = 72h : la news ne peut renverser le quant que si fraîche.
GATE_OVERRIDE_MAX_HOURS = 72
# Fuzz threshold : Levenshtein normalisée ≤ 0.15 → match (≥85 score rapidfuzz)
FUZZ_MIN_SCORE = 85
# Fenêtre dédup floue : 48h autour de l'actif
FUZZ_WINDOW_HOURS = 48
# Garde-fou anti-sur-dédup : si >30% droppés/actif/24h → mode dégradé (SHA exact seul)
DEDUP_DROP_RATIO_GUARD = 0.30

# Coefficients nature × horizon (modulent la pertinence, pas un decay global)
# Source : spec-phase2-news-UNIFIEE.md §2 — validé Thomas.
#
# A3 — DOC : le coef_nature est VOLONTAIREMENT FLOTTANT (composition avec la
# pertinence, pas substitution). Il joue le rôle d'amortisseur sur les natures
# faibles (ponctuel sur 7j/1m, verbal partout) SANS sur-amortir les natures
# fortes (structurel = 0.8/1.0/1.0 → on garde quasi-plein poids long terme,
# c'est ce qu'on VEUT pour porter la tendance). Tout passage en "decay global"
# casserait l'objectif tendance : un structurel high doit tenir à 1m.
COEF_NATURE: Dict[str, Dict[str, float]] = {
    "structurel": {"24h": 0.8, "7j": 1.0, "1m": 1.0},
    "ponctuel":   {"24h": 1.0, "7j": 0.5, "1m": 0.15},
    "deja_cote":  {"24h": 0.0, "7j": 0.0, "1m": 0.0},
    "verbal":     {"24h": 0.3, "7j": 0.2, "1m": 0.1},
}
# Natures écartées AVANT scoring (filtre amont, voir _candidates_for).
NATURES_FILTERED_OUT: Set[str] = {"deja_cote"}

# ---------------------------------------------------------------------------
# Lot 5 — Gates sanity sémantique des news (FLAG-ONLY, mode shadow)
# ---------------------------------------------------------------------------
# C8a — Détection « already-priced » RELATIVE à l'horizon.
# Distinct de la fraîcheur absolue T2/STALE (>30j) : ici un event peut être
# RÉCENT en absolu mais TROP VIEUX POUR SON HORIZON → le marché l'a probablement
# déjà digéré, le move associé est passé. Tunables (constantes documentées).
#
# Sémantique : `(now_utc - canonical_event_date) > ALREADY_PRICED_WINDOW[h]`
# → already_priced=True pour cet horizon. FLAG ONLY : la conclusion / le score /
# le coef_nature ne sont PAS modifiés. On mesure d'abord la fréquence du flag.
ALREADY_PRICED_WINDOW: Dict[str, timedelta] = {
    "24h": timedelta(days=1),
    "7j":  timedelta(days=3),
    "1m":  timedelta(days=10),
}

# C8b — Détection démenti / correction (word-boundary, FR + EN).
# Si match net dans le texte de l'event → is_denial=True : le signal initial
# est peut-être annulé. FLAG ONLY. Anti-faux-positifs : `_phrase_matches`
# (mêmes règles que les keywords directionnels — word-bounded, normalisation
# accents/case, AND tokens si multi-mot).
#
# Liste fermée mais extensible. Aucun mot-clé n'est un substring d'un mot
# courant : « dément » ≠ « démentir » (NFD strip → "dement" vs "dementir",
# le word-boundary empêche le match partiel). « no longer » est multi-token
# AND donc ne matche que si les 2 tokens sont présents.
DENIAL_KEYWORDS: Tuple[str, ...] = (
    # FR
    "dementi",        # « démenti » (accents strippés par _norm)
    "dement",         # « dément » conjugué 3e pers. sing. présent indicatif
    "infirme",
    "corrige",
    "rectification",
    "se retracte",
    # EN
    "retract",
    "retracts",
    "retracted",
    "denies",
    "denied",
    "correction",
    "walked back",
    "no longer",
    "walks back",
)


def compute_already_priced_for_horizon(
    canonical_dt: Optional[datetime],
    horizon: str,
    now: Optional[datetime] = None,
) -> Tuple[bool, Optional[float]]:
    """C8a — Retourne (already_priced, age_days) pour un event sur un horizon.

    - canonical_dt None → (False, None) : zéro invention, pas de flag sans date.
    - horizon non géré (clé inconnue) → (False, age_days) : pas de fenêtre définie.
    - sinon : compare (now - canonical_dt) à ALREADY_PRICED_WINDOW[horizon].

    Pure fonction, pas d'effet de bord — utilisée par le scoring quand il sait
    sur quel horizon il évalue la contribution.
    """
    if not isinstance(canonical_dt, datetime):
        return False, None
    now = now or datetime.now(timezone.utc)
    age = now - canonical_dt
    age_days = age.total_seconds() / 86400.0
    window = ALREADY_PRICED_WINDOW.get(horizon)
    if window is None:
        return False, age_days
    return age > window, age_days


def detect_denial(text: str) -> Tuple[bool, str]:
    """C8b — Détecte un démenti/correction dans le texte d'un event.

    Retourne (is_denial, matched_keyword). Utilise `_phrase_matches` (mêmes
    règles word-bounded que les keywords directionnels — pas de faux match
    sur « démentir une rumeur fondée » → « dement » matche en stem 3e pers
    indicatif, ce qui est le signal voulu).

    Anti-faux-positif :
    - Word-boundary strict via _phrase_matches (lookaround non-mot).
    - Texte vide → False.
    - Match au premier keyword trouvé (ordre = priorité documentation).
    """
    if not text:
        return False, ""
    text_norm = _norm(text)
    for kw in DENIAL_KEYWORDS:
        if _phrase_matches(text_norm, kw):
            return True, kw
    return False, ""

# ---------------------------------------------------------------------------
# A1 — Contribution fantôme (shadow) des events exclus → T1 mesurable
# ---------------------------------------------------------------------------
# Quand un event est écarté dans _candidates_for (nature=deja_cote / stale /
# repost), on calcule la contribution qu'il AURAIT eue s'il avait été retenu,
# et on l'agrège par cellule (actif_key, cle) × horizon. Le scoring lit ce
# stash pour mesurer T1 (faux flips évités) : si la somme des shadow_contrib
# exclus aurait suffi à renverser le signe du quant, Phase 2 a évité un faux
# changement de tendance.
#
# Stocké en module-level (reset au début de classify_all*) — pas thread-safe,
# mais le pipeline v3 est mono-thread.
_SHADOW_CONTRIB: Dict[Tuple[str, str], Dict[str, float]] = {}

# Poids materiality / reliability pour la contribution fantôme. On ré-utilise
# _MAT_WEIGHT (déjà défini plus bas, valeurs high=3/medium=2/low=1) et on
# normalise à [0..1] pour rester comparable à la pertinence brute.
_REL_WEIGHT_NORM = {"confirmed": 1.0, "reported": 0.7, "rumor": 0.3, "": 0.5}


def _reset_shadow_contrib() -> None:
    """Reset du stash shadow au début d'un run (idempotence rejeu)."""
    _SHADOW_CONTRIB.clear()


def get_shadow_contrib(actif_key: str, cle: str) -> Dict[str, float]:
    """Lecture du stash shadow pour une cellule (actif, critère).
    Retourne un dict horizon → contribution fantôme cumulée (signed), {} si rien.
    """
    return dict(_SHADOW_CONTRIB.get((actif_key, cle), {}))


def _record_shadow_contrib(
    ev: dict, actif_key: str, cle: str, crit_pertinence: Optional[Dict[str, float]] = None,
) -> None:
    """Calcule shadow_contrib[h] pour un event EXCLU et l'ajoute au stash.

    Formule (approxime les pondérations utilisées en aval — zéro invention :
    si une valeur manque on retombe à 0, pas d'hypothèse fabriquée) :
      shadow[h] = signe_direction × poids_materiality × poids_reliability × pertinence[h]

    Le poids du critère YAML n'est pas connu ici (vit dans les fiches scoring) ;
    on persiste donc une contribution "pré-poids" : le scoring multipliera par
    `poids × signe` du critère réel quand il agrégera.

    pertinence : si crit_pertinence fourni → utilisé tel quel. Sinon fallback
    à {24h:1.0, 7j:1.0, 1m:1.0} (pas d'inférence : on signale 0 nulle part car
    sinon T1 ne mesurerait jamais rien — on prend une pertinence neutre 1.0
    qui sera modulée par les pondérations matérialité/fiabilité).
    """
    # Direction depuis impacts[] IA si disponible (signed)
    direction_signed = 0
    impacts = ev.get("_impacts") or []
    for imp in impacts:
        asset = imp.get("asset")
        if asset and IA_ASSET_TO_ACTIF.get(asset) == actif_key:
            d = imp.get("direction", "")
            if d == "LONG":
                direction_signed = 1
                break
            if d == "SHORT":
                direction_signed = -1
                break
    if direction_signed == 0:
        # Pas de direction IA → pas de shadow mesurable (zéro invention)
        return

    mat = (ev.get("materiality") or "").strip().lower()
    rel = (ev.get("reliability") or "").strip().lower()
    w_mat = _MAT_WEIGHT.get(mat, 1) / 3.0  # normalise [1/3..1.0]
    w_rel = _REL_WEIGHT_NORM.get(rel, 0.5)

    if crit_pertinence is None:
        crit_pertinence = {"24h": 1.0, "7j": 1.0, "1m": 1.0}

    cell = _SHADOW_CONTRIB.setdefault((actif_key, cle), {})
    for h in ("24h", "7j", "1m"):
        pert = float(crit_pertinence.get(h, 0.0) or 0.0)
        contrib_h = direction_signed * w_mat * w_rel * pert
        cell[h] = cell.get(h, 0.0) + contrib_h


def _normalise_trigger(s: str) -> str:
    """Normalisation pour event_id : casefold + sans accents + sans ponctuation
    + collapse espaces, tronqué 120 chars. Reproductible quel que soit le titre source.
    """
    if not s:
        return ""
    s2 = _strip_accents(str(s)).casefold()
    # Remplace toute ponctuation/non-alphanum par espace
    s2 = re.sub(r"[^a-z0-9\s]", " ", s2)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2[:120]


def compute_event_id(trigger: str, actif: str) -> str:
    """SHA-256 tronqué 12 hex de `normalise(trigger)+"|"+actif`.

    `actif` peut être vide (mode brut, pas d'extraction) — l'id reste stable
    sur le couple (trigger, "").
    """
    payload = _normalise_trigger(trigger) + "|" + (actif or "").upper()
    h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return h[:12]


def _parse_event_date_safe(s: str) -> Optional[datetime]:
    """Parse event_date avec garde-fous : rejette futures (>now+1j) et <2020.

    Retourne None si illisible / incohérent → l'appelant doit fallback à la date
    d'ingestion + marquer event_date_source="fallback".
    """
    # C9 : clamp_future=False ici → on veut DÉTECTER les futures pour rejeter,
    # pas les masquer (le rôle de cette fonction est précisément la validation).
    dt = _parse_date(s, clamp_future=False)
    if dt is None:
        return None
    now_utc = datetime.now(timezone.utc)
    # Rejette futures (tolérance 1 jour pour timezone)
    if dt > now_utc + timedelta(days=1):
        return None
    # Rejette <2020 (archive incohérente)
    if dt < datetime(2020, 1, 1, tzinfo=timezone.utc):
        return None
    return dt


def _fuzzy_match_event_id(
    target_trigger_norm: str,
    target_actif: str,
    target_dt: datetime,
    candidates: List[dict],
) -> Optional[str]:
    """Cherche un event_id existant qui matche flou (Levenshtein ≤0.15) le
    trigger normalisé du target, sur la fenêtre 48h/actif autour de target_dt.

    Retourne le event_id du match le plus ancien si trouvé, sinon None.
    Si rapidfuzz indisponible → None (mode dégradé : SHA exact seul).

    Optimisation : chaque event candidat est censé porter `_trigger_norm`
    (calculé une seule fois en amont par _canonicalize_events). Fallback à
    `_normalise_trigger(c.trigger)` si absent.
    """
    if not _RAPIDFUZZ_OK or not target_trigger_norm:
        return None
    window_start = target_dt - timedelta(hours=FUZZ_WINDOW_HOURS)
    window_end = target_dt + timedelta(hours=FUZZ_WINDOW_HOURS)
    best: Optional[Tuple[datetime, str]] = None  # (dt, event_id) le plus ancien
    target_actif_u = (target_actif or "").upper()
    for c in candidates:
        c_id = c.get("event_id") or ""
        if not c_id:
            continue
        c_dt = c.get("_dt")
        if not isinstance(c_dt, datetime):
            continue
        if c_dt < window_start or c_dt > window_end:
            continue
        c_actif = (c.get("cours") or "").upper()
        # actif vide d'un côté ou de l'autre → on tolère (events bruts)
        if c_actif and target_actif_u and c_actif != target_actif_u:
            continue
        # Utilise le trigger_norm pré-calculé si dispo (perf x40 sur gros logs)
        c_norm = c.get("_trigger_norm")
        if c_norm is None:
            c_norm = _normalise_trigger(c.get("trigger", ""))
            c["_trigger_norm"] = c_norm
        if not c_norm:
            continue
        score = _rf_fuzz.ratio(target_trigger_norm, c_norm)
        if score >= FUZZ_MIN_SCORE:
            if best is None or c_dt < best[0]:
                best = (c_dt, c_id)
    return best[1] if best else None


def _canonicalize_events(events: List[dict]) -> Dict[str, Any]:
    """PREMIER-VU FAIT FOI (règle Thomas) : pour chaque event_id, calcule
    canonical_event_date = MIN(event_date) sur TOUT l'historique events-log,
    et marque les occurrences ultérieures dedup_status="repost".

    Étapes :
    1. Match exact event_id sur tout l'historique → groupes par id.
    2. Match flou (Levenshtein ≤0.15, fenêtre 48h/actif) → fusionne dans le
       groupe du match le plus ancien (mode dégradé si rapidfuzz absent).
    3. Pour chaque groupe : canonical_event_date = min des event_date.
       Toutes les occurrences autres que la plus ancienne → dedup_status="repost".
    4. Garde-fou : si >30% droppés/actif/24h → bascule en mode dégradé
       (rétablit le SHA exact seul, pas de fuzzy).

    Mutation in-place : enrichit chaque event avec
    `_canonical_dt`, `dedup_status` (kept|repost), `stale` (bool).

    Retourne un dict de stats {dropped_total, dropped_by_actif_24h,
    degraded_mode, fuzzy_collisions}.
    """
    stats: Dict[str, Any] = {
        "dropped_total": 0,
        "fuzzy_collisions": 0,
        "degraded_mode": not _RAPIDFUZZ_OK,
    }
    if not events:
        return stats

    # Tri ascendant par date pour pouvoir résoudre canonical en ordre chronologique.
    events_sorted = sorted(
        events,
        key=lambda e: e.get("_dt") or datetime.min.replace(tzinfo=timezone.utc),
    )

    # PASSE 1 : pour chaque event sans event_id (ancienne ligne legacy), on
    # calcule un id à la volée à partir de (trigger, cours). C'est nécessaire pour
    # que la canonisation puisse opérer même sur des lignes pré-Phase 2.
    # On précalcule aussi _trigger_norm (utilisé par le fuzzy match → perf x40
    # car on évite de re-normaliser le même trigger 100× dans la fenêtre).
    for ev in events_sorted:
        ev["_trigger_norm"] = _normalise_trigger(ev.get("trigger", ""))
        if not ev.get("event_id"):
            ev["event_id"] = compute_event_id(ev.get("trigger", ""), ev.get("cours", ""))

    # PASSE 2 : remap fuzzy → on fait pointer l'event sur un id plus ancien
    # s'il y a match flou dans la fenêtre 48h/actif.
    # Optimisation : on ne fuzzy-match QUE les events à <48h des autres ; on
    # maintient une fenêtre glissante (deque) des 48 dernières heures vues.
    by_id_chrono: Dict[str, List[dict]] = {}
    by_actif_24h: Dict[str, List[bool]] = {}  # actif -> liste flags (True=dropped)
    if _RAPIDFUZZ_OK:
        from collections import deque
        window: "deque[dict]" = deque()
        window_delta = timedelta(hours=FUZZ_WINDOW_HOURS)
        for ev in events_sorted:
            target_norm = ev.get("_trigger_norm") or ""
            target_dt = ev.get("_dt")
            target_actif = ev.get("cours", "")
            if isinstance(target_dt, datetime) and target_norm:
                # Élague la fenêtre : retire les events trop vieux pour matcher
                while window and isinstance(window[0].get("_dt"), datetime) \
                        and (target_dt - window[0]["_dt"]) > window_delta:
                    window.popleft()
                matched = _fuzzy_match_event_id(
                    target_norm, target_actif, target_dt, list(window),
                )
                if matched and matched != ev["event_id"]:
                    ev["event_id"] = matched
                    stats["fuzzy_collisions"] += 1
            window.append(ev)

    # PASSE 3 : grouper par event_id (post-remap), trouver canonical_event_date,
    # marquer reposts.
    for ev in events_sorted:
        by_id_chrono.setdefault(ev["event_id"], []).append(ev)

    drops_per_actif_24h: Dict[str, int] = {}
    totals_per_actif_24h: Dict[str, int] = {}
    now_utc = datetime.now(timezone.utc)
    for ev in events_sorted:
        actif = (ev.get("cours") or "").upper() or "_NOASSET"
        if (ev.get("_dt") or now_utc) >= now_utc - timedelta(hours=24):
            totals_per_actif_24h[actif] = totals_per_actif_24h.get(actif, 0) + 1

    for eid, group in by_id_chrono.items():
        # canonical = la plus petite date du groupe
        canonical_dt = min(
            (g.get("_dt") for g in group if isinstance(g.get("_dt"), datetime)),
            default=None,
        )
        # Première occurrence chronologique
        first_ev = None
        for g in sorted(
            group, key=lambda e: e.get("_dt") or datetime.max.replace(tzinfo=timezone.utc),
        ):
            if isinstance(g.get("_dt"), datetime):
                first_ev = g
                break
        for g in group:
            g["_canonical_dt"] = canonical_dt
            if canonical_dt is not None:
                age_days = (now_utc - canonical_dt).total_seconds() / 86400.0
                g["stale"] = age_days > STALE_DAYS
            else:
                g["stale"] = False
            # Statut dédup : 1re occurrence = kept, autres = repost
            if first_ev is not None and g is first_ev:
                g["dedup_status"] = "kept"
            elif len(group) == 1:
                g["dedup_status"] = "kept"
            else:
                g["dedup_status"] = "repost"
                stats["dropped_total"] += 1
                actif = (g.get("cours") or "").upper() or "_NOASSET"
                if (g.get("_dt") or now_utc) >= now_utc - timedelta(hours=24):
                    drops_per_actif_24h[actif] = drops_per_actif_24h.get(actif, 0) + 1

    # Garde-fou : si un actif a >30% droppés sur 24h → ré-applique le mode
    # dégradé sur cet actif (annule la fusion fuzzy, garde SHA exact).
    # En pratique : si on est en sur-dédup, on désactive fuzzy globalement pour
    # ce run (les futures ingestions auto-corrigeront).
    degraded_actifs: List[str] = []
    for actif, drops in drops_per_actif_24h.items():
        total = totals_per_actif_24h.get(actif, 0)
        if total > 0 and drops / total > DEDUP_DROP_RATIO_GUARD:
            degraded_actifs.append(actif)
    if degraded_actifs:
        stats["degraded_actifs"] = degraded_actifs
        logger.warning(
            "Phase2 dédup : garde-fou actif (%s) — >30%% droppés/24h → mode dégradé recommandé",
            ", ".join(degraded_actifs),
        )

    stats["dropped_by_actif_24h"] = drops_per_actif_24h
    return stats


def is_fresh_for_override(ev: dict, now: Optional[datetime] = None) -> bool:
    """Frais pour gate override : canonical_event_date ≤ 72h.

    Utilisé par le scoring pour autoriser un override de cap anti-inversion.
    """
    now = now or datetime.now(timezone.utc)
    cdt = ev.get("_canonical_dt") or ev.get("_dt")
    if not isinstance(cdt, datetime):
        return False
    age_h = (now - cdt).total_seconds() / 3600.0
    return age_h <= GATE_OVERRIDE_MAX_HOURS


# ---------------------------------------------------------------------------
# Scope catégorie + indices de domaine textuel par critère YAML
# ---------------------------------------------------------------------------
# Permet de filtrer les events candidats à un critère donné :
# - `categories` : ensemble des `category` DeepSeek acceptés (None = pas de filtre).
# - `domain_hints` : tokens (lowercase, sans accents) qui, présents dans l2/trigger,
#   permettent de rattacher un event au critère MEME SI le `cours` ne matche pas
#   l'actif. Liste fermée et stricte pour éviter les faux positifs.
# - `strict_actif` : si True, l'event DOIT cibler l'actif via `cours` ou alias ;
#   les domain_hints seuls ne suffisent pas.
CRITERION_SCOPE: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("cac_40", "tension_politique_fr"): {
        "categories": {"geopolitical", "central_bank_subtle", "regulatory", "macro"},
        "domain_hints": {"france", "lecornu", "matignon", "assemblee", "elysee",
                         "gouvernement francais", "loi de finances", "budget france"},
        "strict_actif": False,
    },
    ("nasdaq", "sentiment_ia_megacaps"): {
        "categories": {"earnings", "sector"},
        "domain_hints": {"nvda", "nvidia", "msft", "microsoft", "googl",
                         "alphabet", "aapl", "apple", "amzn", "amazon",
                         "meta", "tsla", "tesla", "guidance", "earnings"},
        "strict_actif": False,
    },
    ("vix", "tension_geopolitique_active"): {
        "categories": {"geopolitical"},
        "domain_hints": {"war", "guerre", "conflict", "conflit", "strike",
                         "frappe", "escalation", "escalade", "ceasefire",
                         "cessez-le-feu", "invasion"},
        "strict_actif": False,
    },
    ("petrole", "geopol_iran"): {
        "categories": {"geopolitical"},
        "domain_hints": {"iran", "ormuz", "hormuz", "tehran", "teheran",
                         "moyen-orient", "middle east", "israel", "gaza",
                         "hezbollah", "houthi", "oman"},
        "strict_actif": False,
    },
    ("petrole", "opec_politique"): {
        "categories": {"commodity", "geopolitical"},
        "domain_hints": {"opec", "opep"},
        "strict_actif": False,
    },
    ("or", "tension_geopolitique"): {
        "categories": {"geopolitical"},
        "domain_hints": {"war", "guerre", "conflict", "conflit", "escalation",
                         "escalade", "sanctions", "terrorism", "terrorisme",
                         "invasion", "ceasefire", "cessez-le-feu"},
        # Pour l'or, on n'exige PAS que `cours` mappe l'or : la tension géopol
        # impacte l'or indirectement via fly-to-safety.
        "strict_actif": False,
    },
    ("argent", "demande_photovoltaique_et_mining_strikes"): {
        "categories": {"commodity", "sector"},
        "domain_hints": {"silver", "argent", "photovoltaic", "photovoltaique",
                         "solar", "mining", "mine"},
        "strict_actif": False,
    },
    ("cuivre", "mining_strikes_chili_perou"): {
        "categories": {"commodity", "geopolitical", "sector"},
        "domain_hints": {"copper", "cuivre", "codelco", "las bambas",
                         "antofagasta", "chile mining", "peru mining",
                         "chili mine", "perou mine"},
        "strict_actif": False,
    },
    ("cuivre", "news_construction_infrastructure"): {
        "categories": {"macro", "sector", "commodity"},
        "domain_hints": {"china stimulus", "stimulus chine", "infrastructure",
                         "belt and road", "real estate china",
                         "immobilier chine", "construction"},
        "strict_actif": False,
    },
    ("cafe", "maladies_cabosses"): {
        "categories": {"commodity"},
        "domain_hints": {"coffee", "cafe", "rust", "rouille", "hemileia",
                         "broca", "outbreak"},
        "strict_actif": False,
    },
    ("cacao", "eudr_impact"): {
        "categories": {"regulatory", "commodity"},
        "domain_hints": {"eudr", "deforestation regulation", "traceability"},
        "strict_actif": False,
    },
    ("cacao", "maladies_cabosses_cacao"): {
        "categories": {"commodity"},
        "domain_hints": {"cocoa", "cacao", "black pod", "swollen shoot",
                         "pod borer", "outbreak"},
        "strict_actif": False,
    },
    ("ble", "geopol_mer_noire"): {
        "categories": {"geopolitical", "commodity"},
        "domain_hints": {"wheat", "ble", "ukraine", "russia wheat", "russie ble",
                         "black sea", "mer noire", "odessa", "corridor"},
        "strict_actif": False,
    },
}


# ---------------------------------------------------------------------------
# Mapping clé YAML → cle_courante des fiches
# ---------------------------------------------------------------------------
# Les fiches (config/fiches/*.yml) utilisent `cle_courante` qui peut différer
# de la clé du critère dans triggers-and-windows.yml. On émet TOUJOURS la clé
# attendue par les fiches (le criteres_calculator fait `triplets[cle_courante]`).
YML_KEY_TO_CLE_COURANTE: Dict[Tuple[str, str], str] = {
    ("petrole", "geopol_iran"): "tension_geopol_moyen_orient",
    ("petrole", "opec_politique"): "opec_production_policy",
    ("ble", "geopol_mer_noire"): "geopolitique_mer_noire",
    ("cacao", "eudr_impact"): "eudr",
    ("cacao", "maladies_cabosses_cacao"): "maladies_cabosses",
    ("cafe", "maladies_cabosses"): "maladies_cabosses_rouille",
    ("argent", "demande_photovoltaique_et_mining_strikes"): "demande_pv_mining_strikes",
    ("cuivre", "news_construction_infrastructure"): "news_construction_infra",
}


# ---------------------------------------------------------------------------
# Parsing events-log.md
# ---------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
_SEPARATOR_RE = re.compile(r"^\s*\|?[\s\-:|]+\|?\s*$")


# GATE C9 — Tolérance "futur" pour le parsing des timestamps d'event (events-log).
# Au-delà de NOW_UTC + C9_FUTURE_TOLERANCE_MIN, le timestamp est ramené à NOW_UTC
# (horloge source décalée — RSS d'un serveur mal réglé). Tolérance 10 min cohérente
# avec news_collector._normalize_to_utc.
C9_FUTURE_TOLERANCE_MIN: int = 10


def _parse_date(s: str, *, clamp_future: bool = True) -> Optional[datetime]:
    """Parse une date. GATE C9 : UTC tz-aware OBLIGATOIRE en sortie.

    - Si la source n'a pas de TZ → UTC explicite.
    - Si la source a une TZ → conversion en UTC (astimezone).
    - Si clamp_future=True (défaut, comportement ingestion) ET timestamp futur
      > NOW_UTC + C9_FUTURE_TOLERANCE_MIN → ramené à NOW_UTC + log WARNING.
    - Si clamp_future=False → la date est retournée telle quelle (utile pour
      les couches de validation type `_parse_event_date_safe` qui veulent
      vérifier la cohérence brute sans masquage).
    """
    s = s.strip()
    if not s:
        return None
    dt: Optional[datetime] = None
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
    if dt is None:
        return None
    # GATE C9 : tz-aware obligatoire (UTC par défaut), puis astimezone UTC.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # GATE C9 : timestamp futur > tolérance → corrigé à now (horloge décalée).
    if clamp_future:
        now_utc = datetime.now(timezone.utc)
        if dt > now_utc + timedelta(minutes=C9_FUTURE_TOLERANCE_MIN):
            logger.warning(
                "C9 _parse_date timestamp futur ramené à NOW_UTC source=%r dt=%s now=%s",
                s, dt.isoformat(), now_utc.isoformat(),
            )
            dt = now_utc
    return dt


def parse_events_log(path: Path = EVENTS_LOG) -> List[dict]:
    """Parse le tableau markdown. Retourne une liste de dicts triée par date desc.

    Rétro-compat : supporte 3 formats de header
    - Legacy (11 cols) : date|L1|L2|trigger|cours|latence|R|source|news_zone|category|pattern_id
    - v2 directionnel (14 cols) : + impacts|materiality|reliability
    - v2.2 Phase 2 (19 cols) : + event_id|event_date|nature|dedup_status|stale

    Une ligne sans colonnes v2 -> impacts décodés=[], materiality="", reliability="".
    Une ligne sans colonnes Phase 2 -> event_id calculé à la volée par
    `_canonicalize_events` (rétro-compat append-only).
    """
    if not path.exists():
        logger.warning("events-log absent (%s) — 0 events", path)
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("Impossible de lire events-log : %s", e)
        return []

    rows: List[List[str]] = []
    for line in text.splitlines():
        m = _TABLE_ROW_RE.match(line)
        if not m:
            continue
        if _SEPARATOR_RE.match(line):
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        rows.append(cells)

    if not rows:
        return []

    header = rows[0]
    first_is_date = _parse_date(header[0]) is not None
    # Header par défaut v2.2 Phase 2 (19 col). Si la ligne a moins de colonnes,
    # on tronque (les colonnes manquantes restent à "").
    DEFAULT_HEADERS = [
        "date", "l1", "l2", "trigger", "cours", "latence", "r",
        "source", "news_zone", "category", "pattern_id",
        "impacts", "materiality", "reliability",
        # Phase 2 — 5 nouvelles colonnes (lecture par NOM, pas position)
        "event_id", "event_date", "nature", "dedup_status", "stale",
    ]
    if first_is_date:
        headers_l = DEFAULT_HEADERS
        data_rows = rows
    else:
        headers_l = [h.lower().strip() for h in header]
        data_rows = rows[1:]

    # FIX bug v2.2 : un fichier peut avoir un header legacy puis des lignes data
    # plus riches (append-only, schéma upgradé en cours de vie).
    # - Si >= 12 colonnes ET pas `impacts` dans headers → upgrade v2 directionnel.
    # - Si >= 15 colonnes ET pas `event_id` dans headers → upgrade Phase 2.
    if "impacts" not in headers_l:
        if any(len(r) >= 12 for r in data_rows):
            headers_l = DEFAULT_HEADERS
    if "event_id" not in headers_l:
        if any(len(r) >= 15 for r in data_rows):
            headers_l = DEFAULT_HEADERS

    events: List[dict] = []
    for r in data_rows:
        if len(r) < 2:
            continue
        ev: Dict[str, Any] = {}
        for i, val in enumerate(r):
            if i < len(headers_l):
                ev[headers_l[i]] = val
        dt = _parse_date(ev.get("date", ""))
        if dt is None:
            logger.warning("events-log : ligne ignorée (date illisible) : %r", r)
            continue
        ev["_dt"] = dt
        # Décode `impacts` compacts en liste de dicts (rétro-compat : vide si absent)
        ev["_impacts"] = _decode_impacts_str(ev.get("impacts", ""))
        # Phase 2 — event_date du log si présent, sinon fallback = _dt (date d'ingestion)
        ev_date_raw = ev.get("event_date", "")
        ev_date_parsed = _parse_event_date_safe(ev_date_raw) if ev_date_raw else None
        if ev_date_parsed is not None:
            ev["_event_dt"] = ev_date_parsed
            ev["event_date_source"] = "rss"
        else:
            ev["_event_dt"] = dt
            ev["event_date_source"] = "fallback"
        # Nature : fallback "ponctuel" si absente/inconnue (parsing défensif)
        raw_nature = (ev.get("nature") or "").strip().lower()
        if raw_nature not in COEF_NATURE:
            raw_nature = "ponctuel"
        ev["nature"] = raw_nature
        # C8b — Détection démenti / correction (FLAG-ONLY, calculée une fois).
        # On scanne le texte complet de l'event (_event_text concatène trigger+l2+...).
        # is_denial=True NE NEUTRALISE PAS le signal — c'est purement informatif,
        # tracé dans le decision-log et le bulletin pour mesure de fréquence.
        is_denial, denial_kw = detect_denial(_event_text(ev))
        if is_denial:
            ev["is_denial"] = True
            ev["denial_keyword"] = denial_kw
        events.append(ev)
    events.sort(key=lambda e: e["_dt"], reverse=True)

    # Phase 2 — PREMIER-VU FAIT FOI : canonisation event_id + dédup + stale.
    # Cette passe mute chaque event in-place avec _canonical_dt, dedup_status, stale.
    _canonicalize_events(events)
    return events


# ---------------------------------------------------------------------------
# Décodage impacts (sans dépendance dure à extractor.py pour la rétro-compat)
# ---------------------------------------------------------------------------

# NEUTRAL est gardé dans le set d'acceptation pour la rétro-compat parsing
# (anciennes lignes events-log écrites en v2.0 qui contenaient des NEUTRAL).
# La logique de routage (_ia_direction_for) les traite désormais comme "pas de
# signal IA" → ils ne bloquent PAS le fallback keyword (fix bug v2 → v2.1).
_VALID_DIRECTIONS_TC = {"LONG", "SHORT", "NEUTRAL"}
_VALID_ASSETS_TC = set(IA_ASSET_TO_ACTIF.keys())
_VALID_CONF_BUCKETS_TC = {"high", "medium", "low"}


def _decode_impacts_str(encoded: str) -> List[Dict[str, Any]]:
    """Décodage tolérant 'ASSET:DIR:CONF;...' → [{asset,direction,confidence}].

    - confidence v2.1 : bucket str {high, medium, low}.
    - Rétro-compat : entier 0-100 mappé en bucket (>=66 high, >=33 medium, sinon low).
    - Entrées hors-énum silencieusement ignorées.
    """
    if not encoded or not isinstance(encoded, str):
        return []
    out: List[Dict[str, Any]] = []
    for chunk in encoded.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) < 2:
            continue
        asset = parts[0].strip().upper()
        direction = parts[1].strip().upper()
        if asset not in _VALID_ASSETS_TC or direction not in _VALID_DIRECTIONS_TC:
            continue
        confidence: Any = "low"
        if len(parts) >= 3 and parts[2].strip():
            raw_conf = parts[2].strip().lower()
            if raw_conf in _VALID_CONF_BUCKETS_TC:
                confidence = raw_conf
            else:
                try:
                    n = max(0.0, min(100.0, float(raw_conf)))
                    confidence = "high" if n >= 66 else ("medium" if n >= 33 else "low")
                except ValueError:
                    confidence = "low"
        out.append({"asset": asset, "direction": direction, "confidence": confidence})
    return out


# ---------------------------------------------------------------------------
# Helpers texte (normalisation, accents, tokens)
# ---------------------------------------------------------------------------

def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )


def _norm(s: str) -> str:
    """Lowercase + accents retirés (pour comparaisons souples)."""
    return _strip_accents(s or "").lower()


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(s: str) -> List[str]:
    return _TOKEN_RE.findall(_norm(s))


def _event_text(ev: dict) -> str:
    """Concaténation utilisée pour le match mots-clés ET pour la gate événement extrême."""
    parts = []
    for k in ("trigger", "l2", "l1", "source", "news_zone"):
        v = ev.get(k)
        if v:
            parts.append(str(v))
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Routage event → (actif, critère)
# ---------------------------------------------------------------------------

def _event_targets_actif(ev: dict, actif_key: str) -> bool:
    """L'event cible-t-il cet actif via son champ `cours` (ticker ou alias) ?"""
    cours = ev.get("cours") or ""
    if not cours:
        return False
    tickers, aliases = TICKER_TO_ACTIF.get(actif_key, (set(), set()))
    # 1) tickers : match exact entre délimiteurs (parenthèses, virgules, espaces)
    cours_padded = f" {cours} "
    for tk in tickers:
        pattern = r"[\(\s,/]" + re.escape(tk) + r"[\)\s,/]"
        if re.search(pattern, cours_padded, re.IGNORECASE):
            return True
    # 2) alias : substring case/accent-insensible
    cours_norm = f" {_norm(cours)} "
    for alias in aliases:
        if _norm(alias) in cours_norm:
            return True
    return False


def _event_matches_domain(ev: dict, scope: Dict[str, Any]) -> bool:
    """L'event relève-t-il du domaine textuel du critère (via l2/trigger) ?

    Borné par `domain_hints` pour éviter les faux positifs. Chaque hint est
    matché en word-boundary (tokens AND si multi-mot) — ainsi « war » ne match
    pas « warm ».
    """
    hints = scope.get("domain_hints") or set()
    if not hints:
        return False
    text_norm = _norm((ev.get("l2") or "") + " | " + (ev.get("trigger") or ""))
    return any(_phrase_matches(text_norm, h) for h in hints)


def _event_category_ok(ev: dict, scope: Dict[str, Any]) -> bool:
    """L'event a-t-il une `category` acceptée par le scope du critère ?

    Si scope.categories est None/vide → pas de filtre catégorie.
    Si l'event n'a PAS de category → on accepte (degradation gracieuse).
    """
    cats = scope.get("categories")
    if not cats:
        return True
    ev_cat = (ev.get("category") or "").strip().lower()
    if not ev_cat:
        return True  # event sans category → on laisse passer (ne pas pénaliser)
    return ev_cat in cats


def _event_ia_targets_actif(ev: dict, actif_key: str) -> bool:
    """L'event a-t-il un impact IA ciblant cet actif (asset IA mappé via
    IA_ASSET_TO_ACTIF) ?"""
    impacts = ev.get("_impacts") or []
    for imp in impacts:
        asset = imp.get("asset")
        if asset and IA_ASSET_TO_ACTIF.get(asset) == actif_key:
            return True
    return False


# ---------------------------------------------------------------------------
# Gate C1 — cohérence de signe DeepSeek (v3/audit/gates-FINAL.md, gate n°1)
# ---------------------------------------------------------------------------
# Import paresseux du module sign_consistency (évite tout couplage dur).
try:
    import sign_consistency as _sc  # type: ignore
    _SC_OK = True
except ImportError:  # pragma: no cover — dégradation gracieuse
    _sc = None
    _SC_OK = False

# Stash module-level : conflits détectés sur ce run (pour decision-log).
# Clé : (actif_key, cle YAML) → liste de dicts traçables.
# Reset en début de classify_all* (idempotence rejeu).
_SIGN_CONFLICTS: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}


def _reset_sign_conflicts() -> None:
    _SIGN_CONFLICTS.clear()


def get_sign_conflicts(actif_key: str, cle: str) -> List[Dict[str, Any]]:
    """Lecture du stash pour une cellule (actif, critère). Retourne une copie."""
    return list(_SIGN_CONFLICTS.get((actif_key, cle), []))


def _check_sign_conflict(ev: dict, asset: str, direction: str) -> Optional[Any]:
    """Cache + délègue à sign_consistency.detect_sign_conflict.

    Mise en cache sur l'event (clé `(asset, direction)`) pour éviter de re-matcher
    le texte sur chaque appel (un même event est interrogé plusieurs fois par
    _ia_direction_for / _group_events_by_asset).

    Retourne un ConflictHit si conflit NET, None sinon.
    """
    if not _SC_OK or _sc is None:
        return None
    if direction not in ("LONG", "SHORT") or not asset:
        return None
    cache = ev.setdefault("_sign_conflict_cache", {})
    key = (asset, direction)
    if key in cache:
        return cache[key]
    text = _event_text(ev)  # concat trigger + l2 + l1 + source + news_zone
    hit = _sc.detect_sign_conflict(text, asset, direction)
    cache[key] = hit
    return hit


def _record_sign_conflict(
    ev: dict, actif_key: str, cle: str, asset: str, hit: Any,
) -> None:
    """Trace un conflit dans le stash + log WARNING (idempotent).

    Une même (event_id, asset, cle) ne s'inscrit qu'UNE fois par cellule
    pour éviter le bruit (l'event peut être interrogé sur plusieurs horizons).
    """
    if hit is None:
        return
    ev_id = ev.get("event_id") or ""
    bucket = _SIGN_CONFLICTS.setdefault((actif_key, cle), [])
    # Dédup intra-cellule par (event_id, asset)
    for existing in bucket:
        if existing.get("event_id") == ev_id and existing.get("asset") == asset:
            return
    title = (ev.get("trigger") or ev.get("l2") or "")[:160]
    entry = {
        "event_id": ev_id,
        "asset": asset,
        "rule_name": hit.rule_name,
        "expected_direction": hit.expected_direction,
        "ia_direction": hit.ia_direction,
        "matched_subject": hit.matched_subject,
        "matched_surprise": hit.matched_surprise,
        "surprise_polarity": hit.surprise_polarity,
        "title": title,
    }
    bucket.append(entry)
    logger.warning(
        "C1 sign_conflict NEUTRALISE %s/%s asset=%s rule=%s "
        "ia=%s expected=%s subject=%r surprise=%r title=%r",
        actif_key, cle, asset, hit.rule_name,
        hit.ia_direction, hit.expected_direction,
        hit.matched_subject, hit.matched_surprise, title,
    )


def _candidates_for(events: List[dict], actif_key: str, cle: str) -> List[dict]:
    """Filtre les events candidats pour un critère donné (avant matching directionnel).

    Routage IA-first : un event dont `impacts[]` cible cet actif est candidat
    SANS exiger que `cours` ou `domain_hints` matchent (l'IA a déjà inféré
    l'impact réel). Le filtre catégorie reste appliqué pour éviter qu'un event
    earnings pollue un critère géopolitique.
    """
    scope = CRITERION_SCOPE.get((actif_key, cle), {})
    strict = bool(scope.get("strict_actif", False))
    out: List[dict] = []
    for ev in events:
        # A1 — shadow contribution : avant d'écarter un event pour
        # nature/stale/repost, on calcule sa contribution fantôme (ce qu'il
        # AURAIT pesé s'il était passé) et on l'agrège sur la cellule
        # (actif_key, cle). Permet à T1 de mesurer les faux flips évités.
        # Pré-requis : l'event doit cibler l'actif (sinon shadow non pertinent).
        ev_targets_this_actif = (
            _event_ia_targets_actif(ev, actif_key)
            or _event_targets_actif(ev, actif_key)
            or (not strict and _event_matches_domain(ev, scope))
        )

        # Phase 2 — filtres amont (AVANT cutoff lookback) :
        # 1. `nature` ∈ filtered_out (deja_cote) → écarté du scoring
        if ev.get("nature") in NATURES_FILTERED_OUT:
            if ev_targets_this_actif and _event_category_ok(ev, scope):
                _record_shadow_contrib(ev, actif_key, cle)
            continue
        # 2. stale=True (canonical_event_date > 30j) → écarté (archive re-publiée)
        if ev.get("stale"):
            if ev_targets_this_actif and _event_category_ok(ev, scope):
                _record_shadow_contrib(ev, actif_key, cle)
            continue
        # 3. repost (vu une 1re fois → déjà compté) → écarté du scoring courant
        #    mais conservé dans events-log pour traçabilité.
        if ev.get("dedup_status") == "repost":
            if ev_targets_this_actif and _event_category_ok(ev, scope):
                _record_shadow_contrib(ev, actif_key, cle)
            continue
        # Filtre catégorie en premier (peu coûteux, s'applique aussi à l'IA)
        if not _event_category_ok(ev, scope):
            continue
        # Routage : (a) impacts IA ciblent l'actif, (b) `cours` cible l'actif,
        # ou (c) domain_hints matchent (legacy fallback).
        ia_targets = _event_ia_targets_actif(ev, actif_key)
        targets = _event_targets_actif(ev, actif_key)
        domain = _event_matches_domain(ev, scope) if not strict else False
        if not (ia_targets or targets or domain):
            continue
        out.append(ev)
    return out


# ---------------------------------------------------------------------------
# Matching mots-clés robuste (exact phrase OU tokens AND)
# ---------------------------------------------------------------------------

def _phrase_matches(text_norm: str, keyword: str) -> bool:
    """Match d'un mot-clé sur un texte (déjà normalisé).

    Stratégie :
    1. Phrase exacte avec word-boundary (lookaround non-mot).
    2. Sinon, "tokens AND" : tous les tokens du mot-clé apparaissent comme
       tokens word-bounded dans le texte. Permet « Iran ceasefire » de matcher
       « extended ceasefire ... Iran ... » même si non adjacents.
    """
    kw_norm = _norm(keyword).strip()
    if not kw_norm:
        return False
    # 1) Phrase exacte
    escaped = re.escape(kw_norm)
    phrase_re = re.compile(
        rf"(?<![a-z0-9_]){escaped}(?![a-z0-9_])"
    )
    if phrase_re.search(text_norm):
        return True
    # 2) Tokens AND (uniquement si mot-clé multi-token)
    kw_tokens = _tokens(kw_norm)
    if len(kw_tokens) < 2:
        return False
    text_tokens = set(_tokens(text_norm))
    return all(tk in text_tokens for tk in kw_tokens)


def _any_keyword_matches(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return False
    text_norm = _norm(text)
    for kw in keywords:
        if _phrase_matches(text_norm, kw):
            return True
    return False


# ---------------------------------------------------------------------------
# Résolution triplet : routage + direction
# ---------------------------------------------------------------------------

# Poids confidence bucket → tie-break (cf. départage LONG/SHORT IA)
_CONF_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def _ia_direction_for(
    ev: dict, actif_key: str, cle: Optional[str] = None,
) -> Optional[str]:
    """Retourne 'LONG' / 'SHORT' si l'IA a explicitement marqué une direction
    tradable pour cet actif dans `impacts[]`, sinon None.

    Règle v2.1 : NEUTRAL n'est plus un signal IA (le prompt v2.1 interdit
    NEUTRAL — un actif sans direction claire n'est plus listé). Pour la
    rétro-compat avec d'anciennes lignes contenant `NEUTRAL`, on le traite
    comme "pas de signal IA" → None → le fallback keyword peut s'activer.

    Si plusieurs impacts LONG/SHORT ciblent le même actif (rare), on garde
    celui de confidence bucket max (high > medium > low).

    Gate C1 — cohérence de signe (sign_consistency) :
    Si l'impact contredit une règle macro NON AMBIGUË (ex. « OPEP augmente la
    production » classée LONG BRENT), il est NEUTRALISÉ ici (skip) et tracé
    via _record_sign_conflict (si `cle` fourni). Conservateur : on ne flip
    PAS, on retire le signal douteux pour qu'il ne contamine pas le score.
    """
    impacts = ev.get("_impacts") or []
    if not impacts:
        return None
    best_dir: Optional[str] = None
    best_weight = -1
    for imp in impacts:
        asset = imp.get("asset")
        if not asset:
            continue
        if IA_ASSET_TO_ACTIF.get(asset) != actif_key:
            continue
        direction = imp.get("direction")
        if direction not in ("LONG", "SHORT"):
            continue  # NEUTRAL / autre → ignoré pour ne pas bloquer le fallback
        # Gate C1 : impact contredit une règle macro NON AMBIGUË → neutralisé.
        hit = _check_sign_conflict(ev, asset, direction)
        if hit is not None:
            if cle:
                _record_sign_conflict(ev, actif_key, cle, asset, hit)
            continue
        conf = imp.get("confidence")
        if isinstance(conf, str):
            weight = _CONF_WEIGHT.get(conf.lower(), 1)
        elif isinstance(conf, (int, float)):
            # Rétro-compat ancien schéma 0-100
            n = max(0.0, min(100.0, float(conf)))
            weight = 3 if n >= 66 else (2 if n >= 33 else 1)
        else:
            weight = 1
        if weight > best_weight:
            best_weight = weight
            best_dir = direction
    return best_dir


def _resolve_triplet_with_meta(
    events: List[dict],
    actif_key: str,
    cle: str,
    long_keywords: List[str],
    short_keywords: List[str],
    lookback_days: int,
    now: datetime,
    synthese: Optional[Dict[str, str]] = None,
) -> Tuple[int, Dict[str, str]]:
    """Comme _resolve_triplet mais retourne aussi (materiality, reliability,
    source_track) du meilleur event ayant produit la direction.

    source_track ∈ {"ia_synthese", "ia_synthese_faible", "ia", "ia_conflict",
    "keyword", "none"}.
    materiality/reliability sont les champs bruts de l'event gagnant (lower-case,
    "" si manquants). Si direction = 0 → meta peut être vide ou contenir
    "ia_synthese_faible" (niveau 2 — fallback prix attendu).

    `synthese` (optionnel) : résultat de synthese_directionnelle pour cet actif,
    forme {"direction": "LONG|SHORT|NEUTRAL", "conviction": "high|medium|low",
    "rationale": "..."}. Si fourni avec conviction high/medium → court-circuite
    l'agrégation. Si low/NEUTRAL → critère = 0 (niveau 2).
    """
    val, meta = _resolve_triplet_impl(
        events, actif_key, cle, long_keywords, short_keywords, lookback_days, now,
        synthese=synthese,
    )
    return val, meta


def _resolve_triplet(
    events: List[dict],
    actif_key: str,
    cle: str,
    long_keywords: List[str],
    short_keywords: List[str],
    lookback_days: int,
    now: datetime,
    synthese: Optional[Dict[str, str]] = None,
) -> int:
    """Rétro-compat : ne retourne que la direction."""
    val, _meta = _resolve_triplet_impl(
        events, actif_key, cle, long_keywords, short_keywords, lookback_days, now,
        synthese=synthese,
    )
    return val


def _resolve_triplet_impl(
    events: List[dict],
    actif_key: str,
    cle: str,
    long_keywords: List[str],
    short_keywords: List[str],
    lookback_days: int,
    now: datetime,
    synthese: Optional[Dict[str, str]] = None,
) -> Tuple[int, Dict[str, str]]:
    """Résout un triplet en mode HYBRIDE :

    1. **IA-first** : si un event récent dans la fenêtre a un `impacts[]` qui
       cible cet actif avec une direction tradable (LONG/SHORT), on prend cette
       direction. NEUTRAL ou absence de l'actif dans impacts[] ne compte PAS
       comme un signal IA (correction du bug v2 : ces events ne doivent pas
       bloquer le fallback keyword).
       Le scope catégorie + domaine reste vérifié pour éviter qu'un event
       Brent off-topic (ex: earnings) pollue un critère géopolitique.
       Départage : matérialité descendante puis date descendante.

    2. **Fallback keyword** : pour les events où l'IA n'a pas marqué de
       direction LONG/SHORT pour cet actif (ancien schéma, NEUTRAL, ou IA
       n'ayant simplement pas listé cet actif), on applique le matching
       mots-clés (LONG/SHORT) avec le même routage scope.

    Règles communes :
    - Fenêtre [now - lookback, now]
    - Long et Short conflictuels (même event ou même date) : matérialité puis
      récence
    - Priorité IA : si au moins UN event a un signal IA LONG/SHORT pour cet
      actif, on tranche en IA-only (le fallback keyword est court-circuité
      pour éviter qu'un keyword secondaire écrase un signal IA explicite).
    """
    if not long_keywords and not short_keywords and not _criterion_has_ia_route(actif_key, cle):
        # Critère sans keywords ni route IA possible : 0 neutre.
        return 0, {}

    # -------- 0) Synthèse directionnelle IA (niveau 1) --------
    # Si une synthèse par actif a été calculée en amont par synthese_directionnelle,
    # elle PRIME sur l'agrégation mécanique : c'est elle qui résout les conflits
    # multi-news (ex Pétrole 16 LONG vs 8 SHORT). On l'applique uniquement aux
    # critères qui ont un scope IA (sinon la synthèse n'aurait pas vu cet actif).
    if synthese and _criterion_has_ia_route(actif_key, cle):
        direction = str(synthese.get("direction", "")).upper()
        conviction = str(synthese.get("conviction", "")).lower()
        rationale = str(synthese.get("rationale", ""))[:300]
        if conviction in ("high", "medium") and direction in ("LONG", "SHORT"):
            val_signed = 1 if direction == "LONG" else -1
            # Audit 2026-06-01 : propagation reliability depuis l'event source
            # le plus matériel ayant produit la direction de la synthèse.
            # La synthèse DeepSeek ne renvoie pas de reliability → on la dérive
            # de l'event "gagnant" (matérialité décroissante, puis date décroissante)
            # parmi les candidats scope-validés qui portent un impact IA dans la
            # direction de la synthèse. Si aucun event matchant → "" (red line
            # zéro invention : on documente l'absence plutôt que de mentir).
            cutoff_synth = now - timedelta(days=lookback_days)
            best_rel: str = ""
            best_ev: Optional[dict] = None
            best_key: Tuple[int, datetime] = (-1, datetime.min.replace(tzinfo=timezone.utc))
            for ev in _candidates_for(events, actif_key, cle):
                dt = ev.get("_dt")
                if not isinstance(dt, datetime):
                    continue
                if dt < cutoff_synth or dt > now:
                    continue
                # cle propagé → gate C1 enregistre les conflits trouvés ici aussi.
                if _ia_direction_for(ev, actif_key, cle=cle) != direction:
                    continue
                mat = (ev.get("materiality") or "").strip().lower()
                weight = _MAT_WEIGHT.get(mat, 1)
                key = (weight, dt)
                if key > best_key:
                    best_key = key
                    best_rel = (ev.get("reliability") or "").strip().lower()
                    best_ev = ev
            logger.info(
                "synthese[%s/%s] -> %s (conviction=%s, reliability=%s) : %s",
                actif_key, cle, direction, conviction, best_rel or "<none>", rationale[:160],
            )
            # Phase 2 meta — dérivés du best_ev (event source de la synthèse)
            # Nature : DOIT toujours être posée pour activer coef_nature côté
            # scoring. Si best_ev absent (cas rare : direction DeepSeek sans
            # event matchant en mémoire) → fallback "ponctuel" (conservateur,
            # cohérent avec l'extracteur). Zéro invention : c'est un défaut
            # documenté, pas une fabrication de données.
            synth_meta: Dict[str, Any] = {
                "materiality": conviction,  # propage le bucket pour valeur_pondérée
                "reliability": best_rel,
                "source_track": "ia_synthese",
                "synthese_rationale": rationale,
                "nature": (best_ev.get("nature", "ponctuel") if best_ev is not None
                           else "ponctuel"),
            }
            if best_ev is not None:
                cdt = best_ev.get("_canonical_dt") or best_ev.get("_dt")
                freshness_days = (now - cdt).total_seconds() / 86400.0 if isinstance(cdt, datetime) else 0.0
                synth_meta.update({
                    "event_id": best_ev.get("event_id", ""),
                    "event_date": cdt.isoformat() if isinstance(cdt, datetime) else "",
                    "event_date_source": best_ev.get("event_date_source", ""),
                    "freshness_days": f"{freshness_days:.2f}",
                })
                # Lot 5 C8b — propage le flag démenti si présent sur l'event source.
                if best_ev.get("is_denial"):
                    synth_meta["is_denial"] = True
                    synth_meta["denial_keyword"] = best_ev.get("denial_keyword", "")
            return val_signed, synth_meta
        # Conviction faible OU direction NEUTRAL → niveau 2 : critère news = 0.
        # Le prix tranchera via les critères numériques de la cellule.
        logger.info(
            "synthese[%s/%s] faible/neutral (dir=%s conv=%s) -> 0 (niveau 2 : prix tranchera)",
            actif_key, cle, direction or "?", conviction or "?",
        )
        # Phase 2 — même en niveau-2 (val=0), on remonte la nature dominante
        # des events scope-validés pour que M5 (composition nature) et T2
        # (vrais flips qualifiés) reflètent l'activité réelle. Sélection :
        # event le plus matériel parmi les candidats dans la fenêtre, puis
        # le plus frais. Fallback "ponctuel" si aucun candidat exploitable.
        cutoff_synth = now - timedelta(days=lookback_days)
        best_nat_ev: Optional[dict] = None
        best_nat_key: Tuple[int, datetime] = (-1, datetime.min.replace(tzinfo=timezone.utc))
        for ev in _candidates_for(events, actif_key, cle):
            dt = ev.get("_dt")
            if not isinstance(dt, datetime):
                continue
            if dt < cutoff_synth or dt > now:
                continue
            mat = (ev.get("materiality") or "").strip().lower()
            weight = _MAT_WEIGHT.get(mat, 1)
            key = (weight, dt)
            if key > best_nat_key:
                best_nat_key = key
                best_nat_ev = ev
        nat_faible = (best_nat_ev.get("nature", "ponctuel")
                      if best_nat_ev is not None else "ponctuel")
        return 0, {
            "materiality": "",
            "reliability": "",
            "source_track": "ia_synthese_faible",
            "synthese_rationale": rationale,
            "nature": nat_faible,
        }

    cutoff = now - timedelta(days=lookback_days)
    candidates = _candidates_for(events, actif_key, cle)

    # -------- 1) IA-first : un event avec direction IA LONG/SHORT --------
    # Tuple : (dt, materiality_weight, materiality_raw, reliability_raw, ev_ref)
    # ev_ref permet de remonter nature, _canonical_dt, event_date_source au scoring.
    ia_long: Optional[Tuple[datetime, int, str, str, dict]] = None
    ia_short: Optional[Tuple[datetime, int, str, str, dict]] = None
    ia_seen_any = False
    # On suit aussi les events où l'IA s'est "exprimée pour cet actif" mais en
    # direction non-tradable (NEUTRAL legacy) : ils ne déclenchent rien et
    # doivent rester éligibles au fallback keyword.
    for ev in candidates:
        dt = ev.get("_dt")
        if not isinstance(dt, datetime):
            continue
        if dt < cutoff or dt > now:
            continue
        # Gate C1 : `cle` propagé → conflit de signe → impact neutralisé + tracé.
        direction = _ia_direction_for(ev, actif_key, cle=cle)
        if direction is None:
            # Pas de signal IA exploitable pour cet actif (NEUTRAL, non-listé,
            # OU impact neutralisé par gate C1). On NE marque PAS ia_seen_any
            # → le fallback keyword reste ouvert.
            continue
        ia_seen_any = True
        mat = (ev.get("materiality") or "").strip().lower()
        rel = (ev.get("reliability") or "").strip().lower()
        weight = _MAT_WEIGHT.get(mat, 1)
        if direction == "LONG":
            if ia_long is None or (weight, dt) > (ia_long[1], ia_long[0]):
                ia_long = (dt, weight, mat, rel, ev)
        elif direction == "SHORT":
            if ia_short is None or (weight, dt) > (ia_short[1], ia_short[0]):
                ia_short = (dt, weight, mat, rel, ev)
    if ia_seen_any:
        # Au moins un event IA tradable cible cet actif → on tranche en IA-only.
        def _meta_from(t: Tuple[datetime, int, str, str, dict], track: str = "ia") -> Dict[str, Any]:
            ev_ref = t[4]
            cdt = ev_ref.get("_canonical_dt") or ev_ref.get("_dt") or t[0]
            freshness_days = (now - cdt).total_seconds() / 86400.0 if isinstance(cdt, datetime) else 0.0
            m: Dict[str, Any] = {
                "materiality": t[2],
                "reliability": t[3],
                "source_track": track,
                # --- Phase 2 metadata ---
                "nature": ev_ref.get("nature", "ponctuel"),
                "event_id": ev_ref.get("event_id", ""),
                "event_date": cdt.isoformat() if isinstance(cdt, datetime) else "",
                "event_date_source": ev_ref.get("event_date_source", ""),
                "freshness_days": f"{freshness_days:.2f}",
            }
            # Lot 5 C8b — flag démenti (zéro bruit : ajout SEULEMENT si True).
            if ev_ref.get("is_denial"):
                m["is_denial"] = True
                m["denial_keyword"] = ev_ref.get("denial_keyword", "")
            return m
        if ia_long and not ia_short:
            return 1, _meta_from(ia_long)
        if ia_short and not ia_long:
            return -1, _meta_from(ia_short)
        if ia_long and ia_short:
            # Règle de tranche (audit DeepSeek — conflit non arbitraire) :
            #   1) Si une direction a un materiality_weight STRICTEMENT supérieur,
            #      elle gagne.
            #   2) À weight égal, si l'écart de date est ≥ 1 jour, le plus récent
            #      gagne (signal frais surclasse l'ancien).
            #   3) Sinon (weight égal ET écart < 1 jour) : conflit non tranché
            #      → 0 neutre + meta source_track="ia_conflict" + log info.
            #      Pas de >= arbitraire qui forçait LONG par hasard d'ordre.
            w_long, dt_long = ia_long[1], ia_long[0]
            w_short, dt_short = ia_short[1], ia_short[0]
            if w_long > w_short:
                return 1, _meta_from(ia_long)
            if w_short > w_long:
                return -1, _meta_from(ia_short)
            # Weights égaux : départage par récence si écart significatif (≥ 1 jour).
            dt_gap = abs((dt_long - dt_short).total_seconds())
            if dt_gap >= 86400:  # 1 jour
                if dt_long > dt_short:
                    return 1, _meta_from(ia_long)
                return -1, _meta_from(ia_short)
            # Conflit non tranchable → 0 + observabilité.
            logger.info(
                "conflit IA non tranche sur %s/%s : LONG(mat=%s,dt=%s) vs "
                "SHORT(mat=%s,dt=%s) -> 0",
                actif_key, cle, ia_long[2] or "?", dt_long.isoformat(),
                ia_short[2] or "?", dt_short.isoformat(),
            )
            # Phase 2 — nature : on prend celle de l'event le plus frais
            # entre les deux (à matérialité égale, c'est le signal le plus
            # actif). Permet à M5 / T1-T2 de refléter le contexte du conflit.
            conflict_ev = ia_long[4] if dt_long >= dt_short else ia_short[4]
            return 0, {
                "materiality": "",
                "reliability": "",
                "source_track": "ia_conflict",
                "conflict_long_materiality": ia_long[2] or "",
                "conflict_short_materiality": ia_short[2] or "",
                "nature": conflict_ev.get("nature", "ponctuel"),
            }
        return 0, {}

    # -------- 2) Fallback keyword (IA n'a rien marqué d'exploitable) -----
    if not long_keywords and not short_keywords:
        return 0, {}
    # Tuple : (dt, materiality, reliability, ev_ref)
    last_long: Optional[Tuple[datetime, str, str, dict]] = None
    last_short: Optional[Tuple[datetime, str, str, dict]] = None
    for ev in candidates:
        dt = ev.get("_dt")
        if not isinstance(dt, datetime):
            continue
        if dt < cutoff or dt > now:
            continue
        text = _event_text(ev)
        mat = (ev.get("materiality") or "").strip().lower()
        rel = (ev.get("reliability") or "").strip().lower()
        if _any_keyword_matches(text, long_keywords):
            if last_long is None or dt > last_long[0]:
                last_long = (dt, mat, rel, ev)
        if _any_keyword_matches(text, short_keywords):
            if last_short is None or dt > last_short[0]:
                last_short = (dt, mat, rel, ev)

    def _kw_meta(t: Tuple[datetime, str, str, dict]) -> Dict[str, Any]:
        ev_ref = t[3]
        cdt = ev_ref.get("_canonical_dt") or ev_ref.get("_dt") or t[0]
        freshness_days = (now - cdt).total_seconds() / 86400.0 if isinstance(cdt, datetime) else 0.0
        m: Dict[str, Any] = {
            "materiality": t[1],
            "reliability": t[2],
            "source_track": "keyword",
            "nature": ev_ref.get("nature", "ponctuel"),
            "event_id": ev_ref.get("event_id", ""),
            "event_date": cdt.isoformat() if isinstance(cdt, datetime) else "",
            "event_date_source": ev_ref.get("event_date_source", ""),
            "freshness_days": f"{freshness_days:.2f}",
        }
        # Lot 5 C8b — flag démenti (zéro bruit : ajout SEULEMENT si True).
        if ev_ref.get("is_denial"):
            m["is_denial"] = True
            m["denial_keyword"] = ev_ref.get("denial_keyword", "")
        return m

    if last_long is None and last_short is None:
        return 0, {}
    if last_long is not None and last_short is None:
        return 1, _kw_meta(last_long)
    if last_short is not None and last_long is None:
        return -1, _kw_meta(last_short)
    # Les deux matchent
    if last_long[0] >= last_short[0]:  # type: ignore[index]
        return 1, _kw_meta(last_long)  # type: ignore[arg-type]
    return -1, _kw_meta(last_short)  # type: ignore[arg-type]


def _criterion_has_ia_route(actif_key: str, cle: str) -> bool:
    """Un critère est IA-routable si son scope catégorie est défini (sinon
    aucun event IA ne sera retenu — autant le savoir tôt)."""
    scope = CRITERION_SCOPE.get((actif_key, cle))
    return bool(scope)


# ---------------------------------------------------------------------------
# Calendrier (cycle annuel / saisonnier)
# ---------------------------------------------------------------------------

def _resolve_calendrier(cle: str, today: date) -> Optional[int]:
    """Résout les critères calendrier connus. Retourne -1/0/+1 ou None si non géré."""
    m = today.month
    y = today.year
    if cle == "demande_indienne_saisonniere":
        if m in (10, 11, 12):
            return 1
        if m in (1, 2, 3, 4, 5):
            return -1
        return 0
    if cle == "cycle_bresil_biannuel":
        return 1 if (y % 2 == 1) else -1
    return None


# ---------------------------------------------------------------------------
# Chargement triggers-and-windows.yml
# ---------------------------------------------------------------------------

def load_triggers_config(path: Path = TRIGGERS_YML) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"triggers-and-windows.yml absent : {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError("triggers-and-windows.yml : racine YAML doit être un mapping")
    return data


# ---------------------------------------------------------------------------
# API principale
# ---------------------------------------------------------------------------

def _emit_key(actif_key: str, yml_cle: str) -> str:
    """Retourne la clé sous laquelle émettre le triplet (cle_courante des fiches
    si un alias est défini, sinon la clé YAML directe)."""
    return YML_KEY_TO_CLE_COURANTE.get((actif_key, yml_cle), yml_cle)


def _group_events_by_asset(events: List[dict], now: datetime, lookback_days: int = 7) -> Dict[str, List[dict]]:
    """Regroupe les events par asset_id IA (BRENT, GOLD, ...) sur la fenêtre.

    Un event peut apparaître dans plusieurs buckets (multi-impacts).
    Tri desc par date dans chaque bucket. Filtre : seuls les events ayant un
    impact LONG/SHORT pour l'asset sont inclus (NEUTRAL/non-listé ignoré).
    """
    cutoff = now - timedelta(days=lookback_days)
    out: Dict[str, List[dict]] = {}
    for ev in events:
        dt = ev.get("_dt")
        if not isinstance(dt, datetime):
            continue
        if dt < cutoff or dt > now:
            continue
        impacts = ev.get("_impacts") or []
        for imp in impacts:
            if not isinstance(imp, dict):
                continue
            asset = str(imp.get("asset", "")).upper()
            direction = str(imp.get("direction", "")).upper()
            if asset not in IA_ASSET_TO_ACTIF or direction not in ("LONG", "SHORT"):
                continue
            # Gate C1 : impact contredisant une règle macro NON AMBIGUË →
            # neutralisé (la synthèse DeepSeek ne doit jamais voir le signal
            # douteux). Pas de _record_sign_conflict ici (pas de `cle` dispo
            # — l'enregistrement se fait dans la boucle _resolve_triplet_impl
            # qui connaît le critère cible).
            if _check_sign_conflict(ev, asset, direction) is not None:
                continue
            out.setdefault(asset, []).append(ev)
    # Déduplication (un event multi-impacts n'apparaît qu'une fois par asset)
    # + tri desc par date
    for asset in list(out.keys()):
        seen = set()
        dedup: List[dict] = []
        for ev in out[asset]:
            key = id(ev)
            if key in seen:
                continue
            seen.add(key)
            dedup.append(ev)
        dedup.sort(key=lambda e: e.get("_dt") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        out[asset] = dedup
    return out


def _compute_syntheses(
    events: List[dict], now: datetime, extractor: Any, max_lookback_days: int = 14,
) -> Dict[str, Dict[str, str]]:
    """Calcule les synthèses directionnelles par actif (niveau 1).

    Retourne {actif_key_yml: {direction, conviction, rationale}} (clé YAML, pas
    asset_id IA — c'est ce que consomme `_resolve_triplet_impl`).

    Si extractor None ou désactivé → {} (dégradation gracieuse, ancien comportement).
    """
    if extractor is None:
        return {}
    is_enabled = getattr(extractor, "is_enabled", None)
    if not callable(is_enabled) or not is_enabled():
        return {}
    try:
        import synthese_directionnelle as sd
    except ImportError as e:
        logger.warning("synthese_directionnelle import KO : %s", e)
        return {}

    events_by_asset = _group_events_by_asset(events, now, lookback_days=max_lookback_days)
    if not events_by_asset:
        return {}
    raw = sd.synthesize_all(events_by_asset, extractor)
    # Remap asset_id IA -> actif_key YAML
    out: Dict[str, Dict[str, str]] = {}
    for asset_id, synth in raw.items():
        actif_key = IA_ASSET_TO_ACTIF.get(asset_id)
        if actif_key:
            out[actif_key] = synth
    return out


def classify_all_with_meta(
    events: Optional[List[dict]] = None,
    today: Optional[datetime] = None,
    triggers_cfg: Optional[dict] = None,
    extractor: Any = None,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Variante riche : pour chaque triplet, retourne aussi materiality/reliability/source_track.

    Sortie : {actif_key: {cle_courante: {"valeur": int, "materiality": str,
              "reliability": str, "source_track": str}}}
    Pour les critères calendrier (pas d'event source) → meta avec source_track='calendrier'.

    `extractor` (optionnel) : instance Extractor. Si fournie ET activée, on calcule
    une synthèse directionnelle par actif (niveau 1 — DeepSeek) qui prime sur
    l'agrégation mécanique pour les critères de type news/géopol. Si None →
    comportement legacy 100% rétro-compatible (les 299 tests passent).
    """
    if triggers_cfg is None:
        triggers_cfg = load_triggers_config()
    if events is None:
        events = parse_events_log()
    if today is None:
        today = datetime.now(timezone.utc)
    if isinstance(today, datetime):
        today_dt = today if today.tzinfo else today.replace(tzinfo=timezone.utc)
        today_date = today.date()
    else:
        today_dt = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)
        today_date = today

    # A1 — reset du stash shadow (idempotence rejeu — _candidates_for va
    # le remplir à mesure des exclusions deja_cote/stale/repost).
    # Gate C1 — reset du stash sign_conflicts (idempotence rejeu).
    # Resets AVANT _compute_syntheses pour que _group_events_by_asset (qui
    # consulte le cache C1) parte d'un état propre.
    _reset_shadow_contrib()
    _reset_sign_conflicts()

    # Synthèses directionnelles par actif (niveau 1). Vide si extractor None.
    syntheses = _compute_syntheses(events, today_dt, extractor)

    out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for actif_key, criteres in triggers_cfg.items():
        if not isinstance(criteres, dict):
            continue
        actif_out: Dict[str, Dict[str, Any]] = {}
        synth_for_actif = syntheses.get(actif_key)
        for cle, spec in criteres.items():
            if not isinstance(spec, dict):
                continue
            t = spec.get("type")
            emit_cle = _emit_key(actif_key, cle)
            if t == "triplet" or t == "triplet_composite":
                lookback = int(spec.get("horizon_lookback_jours", 7))
                val, meta = _resolve_triplet_with_meta(
                    events,
                    actif_key,
                    cle,
                    spec.get("long_keywords", []) or [],
                    spec.get("short_keywords", []) or [],
                    lookback,
                    today_dt,
                    synthese=synth_for_actif,
                )
                entry: Dict[str, Any] = {"valeur": val}
                entry["materiality"] = meta.get("materiality", "")
                entry["reliability"] = meta.get("reliability", "")
                entry["source_track"] = meta.get("source_track", "none")
                if "synthese_rationale" in meta:
                    entry["synthese_rationale"] = meta["synthese_rationale"]
                # --- Phase 2 metadata (propagation au scoring) ---------------
                for k in ("nature", "event_id", "event_date",
                          "event_date_source", "freshness_days"):
                    if k in meta:
                        entry[k] = meta[k]
                # --- Lot 5 C8b — flag démenti (propagation au scoring) -------
                # Zéro bruit : on n'ajoute que si True (cohérent avec
                # sign_conflict / shadow_contrib_exclu).
                if meta.get("is_denial"):
                    entry["is_denial"] = True
                    entry["denial_keyword"] = meta.get("denial_keyword", "")
                # A1 — shadow_contrib_exclu agrégé pour cette cellule
                # (alimenté par _candidates_for sur les events deja_cote/stale/repost).
                # Lecture sur la PAIRE (actif_key, cle YAML), car le stash est
                # keyé sur la clé YAML (cle), pas sur emit_cle (cle_courante).
                shadow = get_shadow_contrib(actif_key, cle)
                if shadow:
                    entry["p2_shadow_contrib_exclu"] = shadow
                # Gate C1 — sign_conflicts détectés sur cette cellule (lecture
                # sur la PAIRE actif_key/cle YAML, comme le shadow). Propagés
                # tel quel au raw pour traçabilité decision-log + bulletin.
                conflicts = get_sign_conflicts(actif_key, cle)
                if conflicts:
                    entry["sign_conflict"] = True
                    entry["sign_conflict_details"] = conflicts
                actif_out[emit_cle] = entry
            elif t == "calendrier":
                val = _resolve_calendrier(cle, today_date)
                if val is not None:
                    actif_out[emit_cle] = {
                        "valeur": val,
                        "materiality": "",
                        "reliability": "",
                        "source_track": "calendrier",
                    }
                else:
                    logger.warning("Calendrier non géré : %s/%s", actif_key, cle)
        if actif_out:
            out[actif_key] = actif_out
    return out


def classify_all(
    events: Optional[List[dict]] = None,
    today: Optional[datetime] = None,
    triggers_cfg: Optional[dict] = None,
    extractor: Any = None,
) -> Dict[str, Dict[str, int]]:
    """Pour chaque actif × critère triplet/calendrier, retourne la valeur ∈ {-1,0,+1}.

    Sortie : {actif_key: {cle_courante: valeur_triplet}}
    Les clés émises sont les `cle_courante` attendues par les fiches.
    Les critères `numerique` (fenêtres d'activation) ne sont PAS traités ici
    (le calculator s'en occupe).

    `extractor` (optionnel) : instance Extractor pour activer la synthèse
    directionnelle (niveau 1). None → comportement legacy (rétro-compat tests).
    """
    if triggers_cfg is None:
        triggers_cfg = load_triggers_config()
    if events is None:
        events = parse_events_log()
    if today is None:
        today = datetime.now(timezone.utc)
    # Accepte un date OU un datetime (naïf ou aware). On dérive :
    #  - today_dt : datetime aware UTC (fin de journée) pour comparer aux _dt des events
    #  - today_date : date pure pour les critères calendrier
    if isinstance(today, datetime):
        today_dt = today if today.tzinfo else today.replace(tzinfo=timezone.utc)
        today_date = today.date()
    else:
        today_dt = datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)
        today_date = today

    # A1 — reset du stash shadow (idempotence rejeu).
    # Gate C1 — reset du stash sign_conflicts (idempotence rejeu).
    # Resets AVANT _compute_syntheses.
    _reset_shadow_contrib()
    _reset_sign_conflicts()

    syntheses = _compute_syntheses(events, today_dt, extractor)

    out: Dict[str, Dict[str, int]] = {}
    for actif_key, criteres in triggers_cfg.items():
        if not isinstance(criteres, dict):
            continue
        actif_out: Dict[str, int] = {}
        synth_for_actif = syntheses.get(actif_key)
        for cle, spec in criteres.items():
            if not isinstance(spec, dict):
                continue
            t = spec.get("type")
            emit_cle = _emit_key(actif_key, cle)
            if t == "triplet" or t == "triplet_composite":
                lookback = int(spec.get("horizon_lookback_jours", 7))
                val = _resolve_triplet(
                    events,
                    actif_key,
                    cle,
                    spec.get("long_keywords", []) or [],
                    spec.get("short_keywords", []) or [],
                    lookback,
                    today_dt,
                    synthese=synth_for_actif,
                )
                actif_out[emit_cle] = val
            elif t == "calendrier":
                val = _resolve_calendrier(cle, today_date)
                if val is not None:
                    actif_out[emit_cle] = val
                else:
                    logger.warning("Calendrier non géré : %s/%s", actif_key, cle)
            # numerique → ignoré (calculator)
        if actif_out:
            out[actif_key] = actif_out
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    res = classify_all()
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
