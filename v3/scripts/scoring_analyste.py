"""TradingApp v3 — Moteur de scoring déterministe (l'Analyste).

Zéro LLM, zéro data inventée. Lit les fiches `v3/config/fiches/*.yml` et le
fichier `v3/data/criteres-courants.md` (bloc YAML), normalise chaque critère
selon sa fiche, calcule Score(H) pour H ∈ {24h, 7j, 1m} et écrit le bulletin
`v3/data/bulletins/bulletin-YYYY-MM-DD.md`.

Spécifications : `v3/config/SCHEMA-fiche.md` (formule §1, tie-break §5.2,
types de normalisation, GATE traité en DRAPEAU par défaut).

Red lines :
- valeur manquante / source DEAD       -> critère `n/a`, poids 0 ce run
- last_update > 1h                     -> erreur visible, pas de bulletin
- GATE                                 -> drapeau (n'entre pas dans le score)
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import yaml

logger = logging.getLogger("scoring_analyste")

ANALYSTE_VERSION = "v3.0.0"
HORIZONS: Tuple[str, ...] = ("24h", "7j", "1m")
SEUIL_LONG = 0.0  # Score > 0 => LONG (cf. SCHEMA §1)
FRESHNESS_MAX = timedelta(hours=1)

# ---------------------------------------------------------------------------
# Gate de SUFFISANCE DE DONNÉES (demande Thomas — sécurité anti-fausse confiance)
# ---------------------------------------------------------------------------
# Coverage = Σ poids(critères non-gate AVEC valeur_norm non-None)
#            / Σ poids(critères non-gate de la fiche)
# Pondérée par les POIDS (pas en nombre brut) : rater un critère poids 9 ≠ poids 2.
# Les gates (drapeaux) sont exclus du numérateur ET du dénominateur.
#
# Paliers de confiance (tunables, alignés avec la spec validée) :
#   coverage ≥ COVERAGE_OK et données fraîches → "normale"
#   COVERAGE_MIN ≤ coverage < COVERAGE_OK OU données périmées → "faible"
#       (on garde LONG/SHORT mais marqué dans le bulletin)
#   coverage < COVERAGE_MIN → "insuffisant"
#       conclusion = "INSUFFISANT" (override de la règle jamais-neutre)
COVERAGE_OK: float = 0.65
COVERAGE_MIN: float = 0.40
CONCLUSION_INSUFFISANT: str = "INSUFFISANT"

# ---------------------------------------------------------------------------
# GATE Réconciliation Σ contributions = score (garde-fou P0 déterministe)
# ---------------------------------------------------------------------------
# But : garantir que le score d'un horizon est EXACTEMENT égal à la somme des
# contributions individuelles. Si l'égalité est rompue (bug arithmétique, code
# qui ajoute/retire silencieusement un terme, double-comptage), on logge une
# ERREUR claire SANS crasher la prod — l'écart doit être visible (alerte) mais
# le bulletin doit continuer à sortir (zéro régression utilisateur).
# Tolérance : 1e-9 (en-deçà du round(6) du score final). Au-dessus → ERROR.
RECONCILIATION_TOL: float = 1e-9

# ---------------------------------------------------------------------------
# Lot 4a — Détecteurs directionnels (FLAG-ONLY, zéro changement de comportement)
# ---------------------------------------------------------------------------
# C3 — Divergence quant↔news : signes opposés ET amplitudes non négligeables.
#      Epsilon aligné avec le seuil coin_flip (|score|<0.05 = non-actionnable) :
#      si l'un des deux totaux est inférieur en absolu à EPSILON_DIVERG, on ne
#      flag pas (signal trop faible pour parler de "divergence").
EPSILON_DIVERG: float = 0.05
#
# Score-vs-momentum : la conclusion (LONG/SHORT) est-elle alignée avec le
#      momentum prix récent de l'actif ? Le momentum est lu directement depuis
#      la `valeur_norm` du critère mappé (RSI 14j pour les indices) — AVANT
#      application du signe du critère (qui peut être contrarien). Si la valeur
#      normalisée |.| < EPSILON_MOMENTUM, momentum jugé neutre → pas de flag.
#      Mapping STRICT (zéro invention) : seuls les actifs avec un critère de
#      momentum prix pur sur leur propre ticker sont éligibles. Les autres
#      (commodities, FX) restent sans flag faute de signal direct disponible.
EPSILON_MOMENTUM: float = 0.15
MOMENTUM_CLE_PAR_ACTIF: Dict[str, str] = {
    # actif.lower() → cle_courante du critère "momentum prix récent"
    "s&p 500": "rsi_14j_gspc",
    "nasdaq": "rsi_14j_ixic",
    "cac 40": "rsi_14j_fchi",
}
#
# C6 — Cohérence inter-horizons : zig-zag (≥2 changements de sens) sur la
#      séquence 24h→7j→1m. Une transition simple (1 changement) reste normale
#      (continuation puis retournement). Conclusions INSUFFISANT exclues de la
#      détection (pas de direction → pas de comparaison possible).


def compute_directional_flags(
    criteres_res: List["CritereResult"],
    conclusions: Dict[str, str],
    news_cap_info: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, bool], Dict[str, bool], Dict[str, float], str, bool]:
    """Lot 4a — Calcule les 3 détecteurs directionnels en mode FLAG-ONLY.

    Cette fonction ne modifie JAMAIS les conclusions LONG/SHORT/INSUFFISANT.
    Elle se contente de DRAPEAUTER (signaler) 3 angles morts :

      1. C3 — divergence quant ↔ news (par horizon) :
         signes opposés ET |quant_total| > EPSILON_DIVERG ET |news_total| > EPSILON_DIVERG.
         Source : `news_cap_info[h]` (déjà calculé par score_actif), valeurs PRÉ-cap
         (pour mesurer la divergence *brute* avant arbitrage α).

      2. Score-vs-momentum (par horizon) :
         signe de la conclusion finale opposé au signe du momentum prix récent.
         Source momentum : `valeur_norm` du critère mappé via MOMENTUM_CLE_PAR_ACTIF
         (RSI 14j sur le ticker propre, AVANT signe contrarien — c'est la lecture
         "direction du marché"). |momentum| < EPSILON_MOMENTUM → neutre → pas de flag.
         Conclusions INSUFFISANT → pas de flag (pas de direction comparable).
         Si l'actif n'a PAS de critère de momentum mappé → pas de flag (zéro invention).

      3. C6 — incohérence inter-horizons (par actif) :
         zig-zag ≥ 2 changements de sens sur la séquence 24h→7j→1m.
         Les conclusions INSUFFISANT sont exclues de la séquence (pas de direction).
         Une simple transition (1 changement, ex. LONG→LONG→SHORT) reste normale.

    Retourne :
      (divergence_par_h, contre_momentum_par_h, momentum_valeur_par_h,
       momentum_source_cle, incoherence_inter_horizons)
    """
    # --- C3 — divergence quant ↔ news ---------------------------------------
    divergence: Dict[str, bool] = {}
    for h in HORIZONS:
        info = news_cap_info.get(h, {}) or {}
        q = float(info.get("quant_total_pm1", 0.0))
        n = float(info.get("news_total_pm1", 0.0))
        # Signes strictement opposés + amplitudes significatives.
        opposite = (q > 0 and n < 0) or (q < 0 and n > 0)
        significant = abs(q) > EPSILON_DIVERG and abs(n) > EPSILON_DIVERG
        divergence[h] = bool(opposite and significant)

    # --- Score-vs-momentum --------------------------------------------------
    contre_momentum: Dict[str, bool] = {}
    momentum_valeur: Dict[str, float] = {}
    momentum_source_cle = ""

    # Identifie le critère de momentum pour cet actif (via cle_courante mappée).
    # Premier critère qui matche, non n.a., non gate, valeur_norm définie.
    momentum_crit: Optional["CritereResult"] = None
    eligible_cles = set(MOMENTUM_CLE_PAR_ACTIF.values())
    for c in criteres_res:
        if (c.cle_courante in eligible_cles
                and not c.is_na
                and not c.is_gate
                and c.valeur_norm is not None):
            momentum_crit = c
            momentum_source_cle = c.cle_courante
            break

    for h in HORIZONS:
        # Default : pas de flag (zéro invention : pas de momentum → pas de comparaison).
        contre_momentum[h] = False
        if momentum_crit is None:
            continue
        conc = conclusions.get(h, "")
        if conc not in ("LONG", "SHORT"):
            # INSUFFISANT ou autre → pas de direction → pas de flag.
            continue
        mom = float(momentum_crit.valeur_norm or 0.0)
        momentum_valeur[h] = mom
        if abs(mom) < EPSILON_MOMENTUM:
            # Momentum jugé neutre → pas de divergence directionnelle mesurable.
            continue
        # Conclusion LONG + momentum < 0 → contre-momentum (et inverse).
        if (conc == "LONG" and mom < 0) or (conc == "SHORT" and mom > 0):
            contre_momentum[h] = True

    # --- C6 — incohérence inter-horizons (zig-zag) --------------------------
    seq = [conclusions.get(h, "") for h in HORIZONS]
    seq_dir = [s for s in seq if s in ("LONG", "SHORT")]
    changes = 0
    for i in range(1, len(seq_dir)):
        if seq_dir[i] != seq_dir[i - 1]:
            changes += 1
    incoherence = bool(changes >= 2)

    return divergence, contre_momentum, momentum_valeur, momentum_source_cle, incoherence


def reconcile_score(
    score_final: float,
    contributions: Dict[str, float],
    *,
    actif: str,
    horizon: str,
    cap_extra: float = 0.0,
    tol: float = RECONCILIATION_TOL,
) -> bool:
    """Vérifie |Σ(contributions) + cap_extra − score_final| < tol.

    `cap_extra` permet d'absorber l'effet du cap news/quant : le score final
    est `quant_total + news_total_capped`, alors que la somme brute des
    contributions individuelles vaut `quant_total + news_total` (avant cap).
    On passe donc cap_extra = news_total_capped - news_total pour réconcilier.

    Retourne True si OK, False si écart détecté (et logge ERREUR détaillée).
    Ne lève PAS d'exception (la prod doit continuer — l'alerte est dans les logs).
    """
    sigma = sum(contributions.values()) + cap_extra
    diff = abs(sigma - score_final)
    if diff < tol:
        return True
    logger.error(
        "RECONCILE ERROR actif=%s horizon=%s Σ=%.12f score=%.12f diff=%.3e "
        "(cap_extra=%.6f, n_contrib=%d) — bug de comptage probable",
        actif, horizon, sigma, score_final, diff, cap_extra, len(contributions),
    )
    return False

ROOT = Path(__file__).resolve().parents[1]
FICHES_DIR = ROOT / "config" / "fiches"
CRITERES_FILE = ROOT / "data" / "criteres-courants.md"
BULLETINS_DIR = ROOT / "data" / "bulletins"


# ---------------------------------------------------------------------------
# Chargement des fiches
# ---------------------------------------------------------------------------

def load_fiches(fiches_dir: Path = FICHES_DIR) -> Dict[str, dict]:
    """Charge toutes les fiches *.yml. Clé = nom du fichier sans extension
    (ex: 'petrole'), correspond à la clé attendue dans criteres-courants.md."""
    fiches: Dict[str, dict] = {}
    if not fiches_dir.exists():
        raise FileNotFoundError(f"Dossier fiches introuvable : {fiches_dir}")
    for f in sorted(fiches_dir.glob("*.yml")):
        with f.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict) or "criteres" not in data:
            logger.warning("Fiche ignorée (format invalide) : %s", f.name)
            continue
        fiches[f.stem] = data
    if not fiches:
        raise RuntimeError(f"Aucune fiche valide trouvée dans {fiches_dir}")
    return fiches


def fiches_hash(fiches: Dict[str, dict]) -> str:
    """Hash court des fiches utilisées (traçabilité bulletin)."""
    h = hashlib.sha256()
    for name in sorted(fiches.keys()):
        h.update(name.encode())
        h.update(yaml.safe_dump(fiches[name], sort_keys=True).encode())
    return h.hexdigest()[:12]


# ---------------------------------------------------------------------------
# Chargement criteres-courants.md
# ---------------------------------------------------------------------------

YAML_BLOCK_RE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL)


def load_criteres_courants(path: Path = CRITERES_FILE) -> dict:
    """Lit le bloc YAML du fichier criteres-courants.md.

    Accepte soit un fichier 100% YAML, soit un .md contenant un bloc ```yaml.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"criteres-courants introuvable : {path}. "
            "Lance d'abord criteres_calculator.py."
        )
    text = path.read_text(encoding="utf-8")
    m = YAML_BLOCK_RE.search(text)
    payload = m.group(1) if m else text
    data = yaml.safe_load(payload)
    if not isinstance(data, dict):
        raise ValueError(f"criteres-courants : YAML racine doit être un mapping ({type(data)})")
    return data


def check_freshness(data: dict, now: Optional[datetime] = None) -> Tuple[bool, str]:
    """Vérifie que last_update < 1h. Retourne (ok, message)."""
    last = data.get("last_update")
    if last is None:
        return False, "criteres-courants : `last_update` manquant"
    if isinstance(last, str):
        try:
            last_dt = datetime.fromisoformat(last)
        except ValueError as e:
            return False, f"criteres-courants : last_update illisible ({e})"
    elif isinstance(last, datetime):
        last_dt = last
    else:
        return False, f"criteres-courants : type last_update inattendu ({type(last)})"
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    age = now - last_dt
    if age > FRESHNESS_MAX:
        return False, (
            f"criteres-courants STALE : âge={age}, dernier update={last_dt.isoformat()} "
            f"(seuil {FRESHNESS_MAX})"
        )
    return True, f"fraîcheur OK (âge={age})"


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

def _clip(x: float, cap: float) -> float:
    return max(-cap, min(cap, x))


def extract_valeur_ponderee(critere: dict, raw: Any, valeur_norm: Optional[float]) -> Optional[float]:
    """Extrait valeur_ponderee depuis raw.

    Règles :
    - Si raw est un dict et contient `valeur_ponderee` → on l'utilise (clipé au cap).
    - Sinon (rétro-compat / raw scalaire / clé absente) → fallback = valeur_norm
      (identité avec le chemin baseline ±1).
    Retourne None si valeur_norm est None.
    """
    cap = float(critere.get("cap", 1.0))
    if valeur_norm is None:
        return None
    if isinstance(raw, dict) and "valeur_ponderee" in raw and raw["valeur_ponderee"] is not None:
        try:
            return _clip(float(raw["valeur_ponderee"]), cap)
        except (TypeError, ValueError):
            return _clip(valeur_norm, cap)
    return _clip(valeur_norm, cap)


def normalise(critere: dict, raw: Any) -> Tuple[Optional[float], str]:
    """Applique la normalisation de la fiche à la valeur brute.

    `raw` peut être :
    - un nombre/str directement (valeur brute)
    - un dict {valeur, ts, ...} ; on lit raw['valeur']
    - un dict {valeur_normalisee: ..., ...} pour bypasser le calcul zscore
      (utile tant que l'historique n'est pas dispo dans criteres_calculator)
    - un dict avec history pour calculer le zscore : {valeur, history: [...]}

    Retourne (valeur_normalisée ∈ [-cap,+cap] ou None si n/a, note).
    """
    if raw is None:
        return None, "n/a (valeur absente)"

    type_norm = critere.get("normalisation")
    cap = float(critere.get("cap", 1.0))

    # Extraction valeur brute
    valeur: Any = raw
    history: Optional[List[float]] = None
    valeur_norm_precalc: Optional[float] = None
    if isinstance(raw, dict):
        if raw.get("source_status", "").upper() == "DEAD":
            return None, "n/a (source DEAD)"
        valeur = raw.get("valeur")
        history = raw.get("history")
        valeur_norm_precalc = raw.get("valeur_normalisee")
        if valeur is None and valeur_norm_precalc is None:
            return None, "n/a (valeur absente)"

    # GATE : drapeau, n'entre pas dans le score
    if type_norm == "gate":
        active = bool(valeur) if valeur is not None else False
        return None, f"GATE {'ACTIF' if active else 'inactif'} (drapeau, hors score)"

    # Triplet : valeur ∈ {-1, 0, +1}
    if type_norm == "triplet":
        try:
            v = float(valeur)
        except (TypeError, ValueError):
            return None, "n/a (triplet : valeur non numérique)"
        if v not in (-1.0, 0.0, 1.0):
            # Tolérance : clipper à -1/0/+1 selon signe
            v = 1.0 if v > 0 else (-1.0 if v < 0 else 0.0)
        return _clip(v, cap), "triplet"

    # Linéaire : (val - centre) / echelle, capé
    if type_norm == "lineaire":
        try:
            v = float(valeur)
        except (TypeError, ValueError):
            return None, "n/a (lineaire : valeur non numérique)"
        centre = float(critere.get("centre", 0.0))
        echelle = float(critere.get("echelle", 1.0))
        if echelle == 0:
            return None, "n/a (lineaire : echelle=0 dans la fiche)"
        return _clip((v - centre) / echelle, cap), f"lineaire centre={centre} echelle={echelle}"

    # Zscore : nécessite historique. Sinon accepte valeur déjà normalisée.
    if type_norm == "zscore":
        if valeur_norm_precalc is not None:
            try:
                vn = float(valeur_norm_precalc)
            except (TypeError, ValueError):
                return None, "n/a (zscore : valeur_normalisee non numérique)"
            return _clip(vn, cap), "zscore (pré-calculé)"
        if history and len(history) >= 2 and valeur is not None:
            try:
                vals = [float(x) for x in history]
                v = float(valeur)
            except (TypeError, ValueError):
                return None, "n/a (zscore : history non numérique)"
            mean = statistics.fmean(vals)
            stdev = statistics.pstdev(vals)
            if stdev == 0:
                return None, "n/a (zscore : stdev=0)"
            z = (v - mean) / stdev
            div = float(critere.get("zscore_div", 2.0))
            return _clip(z / div, cap), f"zscore window={len(vals)} z={z:.3f}"
        return None, "n/a (zscore : historique indisponible)"

    return None, f"n/a (type de normalisation inconnu : {type_norm!r})"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@dataclass
class CritereResult:
    id: Any
    nom: str
    type_norm: str
    valeur_brute: Any
    valeur_norm: Optional[float]
    poids: float
    signe: int
    pertinence: Dict[str, float]
    note: str
    contributions: Dict[str, float] = field(default_factory=dict)
    is_gate: bool = False
    gate_active: bool = False
    is_na: bool = False
    # --- Pondération (v3.1) : chemin secondaire en parallèle du ±1 ---------
    valeur_ponderee: Optional[float] = None
    contributions_pond: Dict[str, float] = field(default_factory=dict)
    materiality: str = ""
    reliability: str = ""
    source_track: str = ""
    cle_courante: str = ""
    # Phase 2 — méta news (axe persistance + fraîcheur premier-vu)
    nature: str = ""
    event_id: str = ""
    event_date: str = ""           # canonical_event_date (ISO)
    event_date_source: str = ""    # rss | fallback
    freshness_days: float = 0.0    # delta (now - canonical_event_date) en jours
    # coef_nature appliqué par horizon (×pertinence) — utile pour debug/decision-log
    coef_nature_applied: Dict[str, float] = field(default_factory=dict)
    # A1 — shadow_contrib des events EXCLUS sur la cellule (actif×critère).
    # Dict {horizon: float signé}. Vide si aucune exclusion deja_cote/stale/repost.
    p2_shadow_contrib_exclu: Dict[str, float] = field(default_factory=dict)
    # Gate C1 — cohérence de signe DeepSeek : True si au moins UN impact news
    # a été NEUTRALISÉ pour conflit avec une règle macro NON AMBIGUË.
    sign_conflict: bool = False
    # Détails du conflit (rule_name, asset, ia_direction, expected_direction, ...).
    # Vide si sign_conflict=False. Tracé tel quel dans le decision-log.
    sign_conflict_details: List[Dict[str, Any]] = field(default_factory=list)
    # Persistance "pourquoi" DeepSeek (demande Thomas 2026-06-01) : rationale et
    # bucket de conviction de la synthèse directionnelle. Vide si critère non-news
    # ou si l'extractor n'a pas produit de synthèse (rétro-compat zéro invention).
    synthese_rationale: str = ""
    # Lot 5 C8b — démenti / correction détecté sur l'event source de la cellule.
    # FLAG ONLY : NE change PAS la conclusion ni le score (mode shadow — on mesure).
    is_denial: bool = False
    denial_keyword: str = ""


@dataclass
class ActifResult:
    nom: str
    fiche_key: str
    criteres: List[CritereResult]
    scores: Dict[str, float]
    conclusions: Dict[str, str]
    tie_break_notes: Dict[str, str]
    # --- Pondération (v3.1) ------------------------------------------------
    scores_pond: Dict[str, float] = field(default_factory=dict)
    conclusions_pond: Dict[str, str] = field(default_factory=dict)
    tie_break_notes_pond: Dict[str, str] = field(default_factory=dict)
    diverge: Dict[str, bool] = field(default_factory=dict)
    # --- Diagnostic cap news/quant (Point 3 plan horizon) -----------------
    news_cap_info: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # --- Gate suffisance de données (sécurité anti-fausse confiance) ------
    # coverage : 1 valeur au niveau actif (la disponibilité brute des critères
    #            ne varie pas par horizon, c'est la pertinence qui varie).
    # confidence : 1 valeur PAR horizon (la fraîcheur peut être dégradée
    #              globalement, et un même actif peut être "faible" sur tous
    #              les horizons en cas de stale).
    coverage: float = 1.0
    confidence: Dict[str, str] = field(default_factory=dict)
    # --- Lot 4a — Détecteurs directionnels (flag-only, n'altèrent PAS conclusions)
    # C3 : divergence quant↔news par horizon (signes opposés + amplitudes > eps).
    # quant_total_par_horizon / news_total_par_horizon : valeurs réelles pour le
    # decision-log (utilisées uniquement pour rendre la divergence mesurable).
    divergence_quant_news: Dict[str, bool] = field(default_factory=dict)
    # Score-vs-momentum : LONG sur quant↑ avec momentum prix baissier (ou inverse).
    # contre_momentum[h] = True si flag posé ; Dict[h, float] pour valeur momentum.
    contre_momentum: Dict[str, bool] = field(default_factory=dict)
    momentum_valeur: Dict[str, float] = field(default_factory=dict)  # momentum normalisé utilisé
    momentum_source_cle: str = ""                                    # cle_courante effective ou ""
    # C6 : incohérence inter-horizons (zig-zag ≥2 changements de sens). 1 bool/actif.
    incoherence_inter_horizons: bool = False


def compute_coverage(criteres: List[CritereResult]) -> float:
    """Calcule la couverture pondérée par les poids des critères non-gate.

    Formule : Σ |poids| sur critères non-gate AVEC valeur_norm non-None
              / Σ |poids| sur tous les critères non-gate de la fiche.

    Pondérée par |poids| (et pas en nombre brut) : rater un critère poids 9
    pénalise davantage que rater un critère poids 2. Les gates (drapeaux)
    sont exclus du numérateur ET du dénominateur (ils n'entrent pas dans le
    score). Retourne ∈ [0, 1].

    Cas limites :
    - Aucun critère non-gate (fiche dégénérée) → coverage = 1.0 (par
      convention : "100% de rien est couvert", on ne pénalise pas une fiche
      vide ; le rôle du gate est de détecter les TROUS).
    - Tous les poids à 0 → coverage = 1.0 (idem).
    """
    non_gate = [c for c in criteres if not c.is_gate]
    if not non_gate:
        return 1.0
    total_poids = sum(abs(c.poids) for c in non_gate)
    if total_poids <= 0:
        return 1.0
    covered_poids = sum(abs(c.poids) for c in non_gate if c.valeur_norm is not None)
    return covered_poids / total_poids


def derive_confidence(coverage: float, is_stale: bool = False) -> str:
    """Dérive le palier de confiance pour un actif/horizon.

    Règles (cf. CONSTANTES) :
      coverage < COVERAGE_MIN              → "insuffisant"
      coverage < COVERAGE_OK OU is_stale   → "faible"
      sinon                                → "normale"

    `is_stale` plafonne la confiance à "faible" même si coverage élevé :
    une donnée présente mais vieille n'est pas fiable. Néanmoins, si la
    coverage est sous le minimum, l'état "insuffisant" reste prioritaire
    (l'absence de donnée est PIRE qu'une donnée vieille).
    """
    if coverage < COVERAGE_MIN:
        return "insuffisant"
    if coverage < COVERAGE_OK or is_stale:
        return "faible"
    return "normale"


def coverage_pct(coverage: float) -> int:
    """Arrondi entier en pourcentage pour affichage ('🚫 données insuff. (32%)').

    Plancher à 0, plafond à 100. Utilisé par render_bulletin uniquement.
    """
    pct = int(round(max(0.0, min(1.0, coverage)) * 100))
    return pct


def _conclusion_from_score(score: float) -> Optional[str]:
    if score > SEUIL_LONG:
        return "LONG"
    if score < SEUIL_LONG:
        return "SHORT"
    return None  # tie


def tie_break(
    criteres: List[CritereResult],
    horizon: str,
    veille_conclusion: Optional[str] = None,
    use_pond: bool = False,
) -> Tuple[str, str]:
    """Tie-break Analyste §5.2.

    1. Majorité des 3 critères les plus pesants (|poids|) → 2/3 LONG ⇒ LONG.
    2. Égalité 3-3 ⇒ reconduire la conclusion de la veille.
    3. Aucune veille ⇒ LONG par défaut.
    use_pond=True : utilise contributions_pond au lieu de contributions.
    """
    actifs = [c for c in criteres if not c.is_na and not c.is_gate and c.valeur_norm is not None]
    top3 = sorted(actifs, key=lambda c: abs(c.poids), reverse=True)[:3]
    if len(top3) == 0:
        return "LONG", "tie-break: aucun critère actif → LONG par défaut"
    contribs_attr = "contributions_pond" if use_pond else "contributions"
    votes_long = sum(1 for c in top3 if getattr(c, contribs_attr).get(horizon, 0.0) > 0)
    votes_short = sum(1 for c in top3 if getattr(c, contribs_attr).get(horizon, 0.0) < 0)
    if votes_long > votes_short:
        return "LONG", f"tie-break: majorité top3 LONG ({votes_long}/{len(top3)})"
    if votes_short > votes_long:
        return "SHORT", f"tie-break: majorité top3 SHORT ({votes_short}/{len(top3)})"
    if veille_conclusion in ("LONG", "SHORT"):
        return veille_conclusion, f"tie-break: égalité top3, reconduction veille ({veille_conclusion})"
    return "LONG", "tie-break: égalité top3 + aucune veille → LONG par défaut"


def score_actif(
    fiche_key: str,
    fiche: dict,
    valeurs_actif: dict,
    veille_conclusions: Optional[Dict[str, str]] = None,
    is_stale: bool = False,
) -> ActifResult:
    """Calcule le score d'un actif sur les 3 horizons.

    `is_stale` (sécurité Thomas — voir CONSTANTES COVERAGE_*) :
      - si True → confidence plafonnée à "faible" même si coverage élevé
        (donnée présente mais vieille n'est pas fiable).
      - n'override JAMAIS l'état "insuffisant" (absence > vieillesse).
      - En pratique, `run()` lève déjà si la donnée globale est stale
        (FRESHNESS_MAX) ; ce flag sert au cas où on voudrait dégrader sans
        bloquer le bulletin, et aux tests.
    """
    veille_conclusions = veille_conclusions or {}
    criteres_res: List[CritereResult] = []
    for crit in fiche.get("criteres", []):
        cle = crit.get("cle_courante")
        raw = valeurs_actif.get(cle) if cle else None
        type_norm = crit.get("normalisation", "")
        is_gate = type_norm == "gate"
        valeur_norm, note = normalise(crit, raw)
        poids_raw = crit.get("poids", 0)
        try:
            poids = float(poids_raw) if not is_gate else 0.0
        except (TypeError, ValueError):
            poids = 0.0
        signe = int(crit.get("signe", 1))
        pertinence = {h: float(crit.get("pertinence", {}).get(h, 0.0)) for h in HORIZONS}
        is_na = (valeur_norm is None) and not is_gate
        # Pondéré : extrait depuis raw (triplet) ou fallback = valeur_norm (numérique).
        valeur_ponderee = extract_valeur_ponderee(crit, raw, valeur_norm)

        # --- Phase 2 — coef_nature × pertinence (news uniquement) -----------
        # Pour les critères news (source_track="ia*" ou "keyword"), on module
        # la pertinence par horizon via COEF_NATURE selon la nature DeepSeek.
        # Critères non-news (quant pur) : coef = 1.0 (neutre).
        # NB : la nature est dans `raw` (extrait par triggers_classifier).
        #
        # A3 — FLOTTANT VOULU : coef_nature COMPOSE avec pertinence (×, pas ÷),
        # pour AMORTIR les ponctuel/verbal aux longs horizons (ponctuel 1m=0.15,
        # verbal 1m=0.10) SANS sur-amortir les structurel (structurel 7j=1.0,
        # 1m=1.0 → contribution PRESQUE PLEINE). Décision Thomas, audit run 2053 :
        # le structurel qu'on VEUT garder ne doit JAMAIS être atomisé par cette
        # multiplication (cf. test_step4_coef_structurel_no_atomization).
        coef_nature_h: Dict[str, float] = {h: 1.0 for h in HORIZONS}
        if isinstance(raw, dict):
            raw_nature = str(raw.get("nature", "") or "").lower()
            raw_src = str(raw.get("source_track", "") or "")
            # Coef appliqué uniquement aux critères news (sinon news invisible
            # pour le quant pur — c'est l'objectif Phase 2).
            is_news = raw_src.startswith("ia") or raw_src == "keyword"
            if is_news and raw_nature:
                try:
                    from triggers_classifier import COEF_NATURE as _COEF
                except ImportError:
                    _COEF = {}
                coef_map = _COEF.get(raw_nature)
                if coef_map:
                    coef_nature_h = {h: float(coef_map.get(h, 1.0)) for h in HORIZONS}

        contributions: Dict[str, float] = {}
        contributions_pond: Dict[str, float] = {}
        if not is_na and not is_gate and valeur_norm is not None:
            for h in HORIZONS:
                # pertinence_effective = pertinence × coef_nature (modulation, PAS additive)
                pert_eff = pertinence[h] * coef_nature_h[h]
                contributions[h] = valeur_norm * poids * pert_eff * signe
                vp = valeur_ponderee if valeur_ponderee is not None else valeur_norm
                contributions_pond[h] = vp * poids * pert_eff * signe
        else:
            for h in HORIZONS:
                contributions[h] = 0.0
                contributions_pond[h] = 0.0
        gate_active = False
        if is_gate:
            if isinstance(raw, dict):
                gate_active = bool(raw.get("valeur"))
            else:
                gate_active = bool(raw)
        # Métadonnées de pondération (pour decision-log)
        mat = ""
        rel = ""
        src_track = ""
        synth_rationale = ""
        # --- Phase 2 méta ---
        p2_nature = ""
        p2_event_id = ""
        p2_event_date = ""
        p2_event_date_source = ""
        p2_freshness_days = 0.0
        p2_shadow_excl: Dict[str, float] = {}
        # Gate C1 — defaults (présents même si raw non-dict)
        _sign_conflict: bool = False
        _sign_conflict_details: List[Dict[str, Any]] = []
        # Lot 5 C8b — defaults
        _is_denial: bool = False
        _denial_keyword: str = ""
        if isinstance(raw, dict):
            mat = str(raw.get("materiality", "") or "")
            rel = str(raw.get("reliability", "") or "")
            src_track = str(raw.get("source_track", "") or "")
            # Synthèse DeepSeek (uniquement présente pour les triplets news
            # qui sont passés par le chemin ia_synthese / ia_synthese_faible).
            synth_rationale = str(raw.get("synthese_rationale", "") or "")
            p2_nature = str(raw.get("nature", "") or "")
            p2_event_id = str(raw.get("event_id", "") or "")
            p2_event_date = str(raw.get("event_date", "") or "")
            p2_event_date_source = str(raw.get("event_date_source", "") or "")
            try:
                p2_freshness_days = float(raw.get("freshness_days", 0.0) or 0.0)
            except (TypeError, ValueError):
                p2_freshness_days = 0.0
            # A1 — shadow_contrib_exclu : dict {horizon: float} si présent
            raw_shadow = raw.get("p2_shadow_contrib_exclu")
            if isinstance(raw_shadow, dict):
                for h_key, v_h in raw_shadow.items():
                    try:
                        p2_shadow_excl[str(h_key)] = float(v_h)
                    except (TypeError, ValueError):
                        continue
            # Gate C1 — sign_conflict (cohérence de signe DeepSeek).
            _sign_conflict = bool(raw.get("sign_conflict"))
            _sign_conflict_details = raw.get("sign_conflict_details") or []
            if not isinstance(_sign_conflict_details, list):
                _sign_conflict_details = []
            # Lot 5 C8b — démenti / correction (FLAG-ONLY).
            _is_denial = bool(raw.get("is_denial"))
            _denial_keyword = str(raw.get("denial_keyword", "") or "")
        criteres_res.append(
            CritereResult(
                id=crit.get("id"),
                nom=crit.get("nom", ""),
                type_norm=type_norm,
                valeur_brute=raw,
                valeur_norm=valeur_norm,
                poids=poids,
                signe=signe,
                pertinence=pertinence,
                note=note,
                contributions=contributions,
                is_gate=is_gate,
                gate_active=gate_active,
                is_na=is_na,
                valeur_ponderee=valeur_ponderee,
                contributions_pond=contributions_pond,
                materiality=mat,
                reliability=rel,
                source_track=src_track,
                cle_courante=str(cle or ""),
                synthese_rationale=synth_rationale,
                nature=p2_nature,
                event_id=p2_event_id,
                event_date=p2_event_date,
                event_date_source=p2_event_date_source,
                freshness_days=p2_freshness_days,
                coef_nature_applied=dict(coef_nature_h),
                p2_shadow_contrib_exclu=dict(p2_shadow_excl),
                sign_conflict=_sign_conflict,
                sign_conflict_details=list(_sign_conflict_details),
                is_denial=_is_denial,
                denial_keyword=_denial_keyword,
            )
        )

    scores: Dict[str, float] = {}
    conclusions: Dict[str, str] = {}
    tie_notes: Dict[str, str] = {}
    scores_pond: Dict[str, float] = {}
    conclusions_pond: Dict[str, str] = {}
    tie_notes_pond: Dict[str, str] = {}
    diverge: Dict[str, bool] = {}
    # --- Cap anti-inversion news/quant (Point 3 plan horizon) --------------
    # Diagnostic par horizon, pour traçabilité dans build_decision_log_records.
    news_cap_info: Dict[str, Dict[str, Any]] = {}
    for h in HORIZONS:
        # Sépare news (source_track démarre par "ia") vs quant (tout le reste).
        # Les critères is_na/is_gate ont contributions=0, donc neutres dans la somme.
        news_contribs = [c.contributions[h] for c in criteres_res
                         if c.source_track.startswith("ia") and not c.is_na and not c.is_gate]
        quant_contribs = [c.contributions[h] for c in criteres_res
                          if not c.source_track.startswith("ia") and not c.is_na and not c.is_gate]
        news_total = sum(news_contribs)
        quant_total = sum(quant_contribs)
        news_contribs_p = [c.contributions_pond[h] for c in criteres_res
                           if c.source_track.startswith("ia") and not c.is_na and not c.is_gate]
        quant_contribs_p = [c.contributions_pond[h] for c in criteres_res
                            if not c.source_track.startswith("ia") and not c.is_na and not c.is_gate]
        news_total_p = sum(news_contribs_p)
        quant_total_p = sum(quant_contribs_p)
        # Phase 2 — Gate override RAFFINÉ : remplace la règle high+confirmed seule.
        # La news ne peut renverser le quant (changement de tendance) que si :
        #   canonical_event_date ≤ 72h
        #   ET nature ∈ {structurel, ponctuel}
        #   ET materiality = high
        #   ET reliability ≠ rumor
        # Le `reliability` figé n'est plus le seul gardien : la fraîcheur + la
        # persistance (nature) deviennent les vrais juges. Empêche un repost
        # (canonical_event_date ancien) de déclencher un faux flip.
        GATE_MAX_HOURS = 72.0
        ALLOWED_NATURES = {"structurel", "ponctuel"}
        override = any(
            c.source_track.startswith("ia")
            and c.materiality == "high"
            and c.reliability not in ("rumor", "")
            and c.nature in ALLOWED_NATURES
            and c.freshness_days * 24.0 <= GATE_MAX_HOURS
            and not c.is_na and not c.is_gate
            and c.contributions[h] != 0.0
            for c in criteres_res
        )
        ALPHA = 0.8
        applied = False
        news_total_capped = news_total
        news_total_capped_p = news_total_p
        if not override:
            # PM1 : cap si signes opposés ET news > quant en valeur absolue (sinon
            # news_total est déjà ≤ quant_total*α, pas besoin de capper).
            if (news_total > 0 > quant_total) or (news_total < 0 < quant_total):
                cap_abs = abs(quant_total) * ALPHA
                if abs(news_total) > cap_abs:
                    sign_n = 1.0 if news_total > 0 else -1.0
                    news_total_capped = cap_abs * sign_n
                    applied = True
            # Pondéré : même logique en parallèle.
            if (news_total_p > 0 > quant_total_p) or (news_total_p < 0 < quant_total_p):
                cap_abs_p = abs(quant_total_p) * ALPHA
                if abs(news_total_p) > cap_abs_p:
                    sign_p = 1.0 if news_total_p > 0 else -1.0
                    news_total_capped_p = cap_abs_p * sign_p
        # Stocke le diagnostic (lu par build_decision_log_records).
        news_cap_info[h] = {
            "news_total_pm1": news_total,
            "quant_total_pm1": quant_total,
            "news_total_pm1_capped": news_total_capped,
            "news_total_pond": news_total_p,
            "quant_total_pond": quant_total_p,
            "news_total_pond_capped": news_total_capped_p,
            "cap_applied": applied,
            "override_high_confirmed": override,
            "alpha": ALPHA,
        }
        # --- Baseline ±1 (primaire, sortie de référence) ------------------
        scores[h] = round(quant_total + news_total_capped, 6)
        # GATE Réconciliation Σ=score : on additionne TOUTES les contributions
        # individuelles (gates/n.a. ont contributions[h]=0 donc neutres) + le
        # delta dû au cap (news_total_capped - news_total). Doit valoir scores[h]
        # à la tolérance round(.,6) près. Logge ERROR si écart (sans crasher).
        all_contribs = {str(idx): c.contributions[h] for idx, c in enumerate(criteres_res)}
        reconcile_score(
            scores[h], all_contribs,
            actif=fiche_key, horizon=h,
            cap_extra=(news_total_capped - news_total),
            tol=1e-6,  # round(.,6) borne déjà le score : tol cohérente
        )
        conc = _conclusion_from_score(scores[h])
        if conc is None:
            conc, note = tie_break(criteres_res, h, veille_conclusions.get(h))
            tie_notes[h] = note
        conclusions[h] = conc
        # --- Pondéré (secondaire, loggé) ----------------------------------
        scores_pond[h] = round(quant_total_p + news_total_capped_p, 6)
        all_contribs_p = {str(idx): c.contributions_pond[h] for idx, c in enumerate(criteres_res)}
        reconcile_score(
            scores_pond[h], all_contribs_p,
            actif=f"{fiche_key}[pond]", horizon=h,
            cap_extra=(news_total_capped_p - news_total_p),
            tol=1e-6,
        )
        conc_p = _conclusion_from_score(scores_pond[h])
        if conc_p is None:
            conc_p, note_p = tie_break(criteres_res, h, veille_conclusions.get(h), use_pond=True)
            tie_notes_pond[h] = note_p
        conclusions_pond[h] = conc_p
        diverge[h] = (conclusions[h] != conclusions_pond[h])

    # --- Gate suffisance de données (sécurité anti-fausse confiance) ---------
    # coverage est calculée UNE FOIS au niveau actif (la disponibilité brute
    # des critères ne dépend pas de l'horizon). confidence est dérivée PAR
    # horizon (même coverage, mais override stale potentiellement global).
    # Quand confidence == "insuffisant" → conclusion devient "INSUFFISANT"
    # sur cet horizon (override la règle jamais-neutre, voir tie_break).
    coverage = compute_coverage(criteres_res)
    confidence: Dict[str, str] = {}
    for h in HORIZONS:
        confidence[h] = derive_confidence(coverage, is_stale=is_stale)
        if confidence[h] == "insuffisant":
            # Override jamais-neutre : on REMPLACE LONG/SHORT par INSUFFISANT.
            # On conserve les scores numériques (utiles pour audit/decision-log)
            # mais la conclusion textuelle devient explicite.
            conclusions[h] = CONCLUSION_INSUFFISANT
            conclusions_pond[h] = CONCLUSION_INSUFFISANT
            # On retire le tie-break note s'il existait (plus pertinent).
            tie_notes.pop(h, None)
            tie_notes_pond.pop(h, None)
            # diverge n'a plus de sens si les deux sont INSUFFISANT.
            diverge[h] = False

    # --- Lot 4a — Détecteurs directionnels (FLAG-ONLY, post-conclusions) ---
    # Appelé APRÈS application de l'override INSUFFISANT pour que la séquence
    # inter-horizons et la comparaison score-vs-momentum tiennent compte des
    # cellules réellement non-actionnables. NE MODIFIE PAS conclusions/scores.
    divergence_qn, contre_mom, mom_val, mom_cle, incoh = compute_directional_flags(
        criteres_res, conclusions, news_cap_info
    )

    return ActifResult(
        nom=fiche.get("actif", fiche_key),
        fiche_key=fiche_key,
        criteres=criteres_res,
        scores=scores,
        conclusions=conclusions,
        tie_break_notes=tie_notes,
        scores_pond=scores_pond,
        conclusions_pond=conclusions_pond,
        tie_break_notes_pond=tie_notes_pond,
        diverge=diverge,
        news_cap_info=news_cap_info,
        coverage=coverage,
        confidence=confidence,
        divergence_quant_news=divergence_qn,
        contre_momentum=contre_mom,
        momentum_valeur=mom_val,
        momentum_source_cle=mom_cle,
        incoherence_inter_horizons=incoh,
    )


# ---------------------------------------------------------------------------
# Veille (flips)
# ---------------------------------------------------------------------------

VEILLE_LINE_RE = re.compile(
    r"^\|\s*(?P<actif>[^|]+?)\s*\|\s*(?P<c24>LONG|SHORT)[^|]*\|\s*(?P<c7>LONG|SHORT)[^|]*\|\s*(?P<c1>LONG|SHORT)[^|]*\|",
    re.MULTILINE,
)


def load_veille(bulletins_dir: Path, today: datetime) -> Tuple[Optional[Path], Dict[str, Dict[str, str]]]:
    """Cherche le bulletin le plus récent avant `today`.
    Retourne (chemin, conclusions par actif par horizon)."""
    if not bulletins_dir.exists():
        return None, {}
    files = sorted(
        [p for p in bulletins_dir.glob("bulletin-*.md") if p.stem != f"bulletin-{today:%Y-%m-%d}"],
        reverse=True,
    )
    if not files:
        return None, {}
    veille_path = files[0]
    text = veille_path.read_text(encoding="utf-8")
    conclusions: Dict[str, Dict[str, str]] = {}
    for m in VEILLE_LINE_RE.finditer(text):
        actif = m.group("actif").strip().lower()
        conclusions[actif] = {"24h": m.group("c24"), "7j": m.group("c7"), "1m": m.group("c1")}
    return veille_path, conclusions


# ---------------------------------------------------------------------------
# Bulletin
# ---------------------------------------------------------------------------

def render_bulletin(
    results: List[ActifResult],
    veille_conclusions: Dict[str, Dict[str, str]],
    now: datetime,
    fiches_h: str,
    freshness_msg: str,
) -> str:
    # Lot 5 C8a — import paresseux (cohérent avec build_decision_log_records).
    import triggers_classifier as _tc_classifier  # noqa: F401
    lines: List[str] = []
    lines.append(f"# Bulletin Analyste — {now:%Y-%m-%d} · {now:%Hh%M} (Paris)")
    lines.append("")
    lines.append(f"- Généré : {now.isoformat()}")
    lines.append(f"- Analyste version : {ANALYSTE_VERSION}")
    lines.append(f"- Fiches hash : {fiches_h}")
    lines.append(f"- Fraîcheur : {freshness_msg}")
    lines.append("")
    # Pré-calcul des flips AVANT le rendu matrice (l'ordre d'affichage est :
    # Briefing → Flips vs veille → Matrice → Détail → Limites — demande Thomas
    # 2026-06-01 : remonter les changements de position en tête de bulletin).
    flips: List[str] = []
    for r in results:
        veille = veille_conclusions.get(r.nom.lower(), {})
        for h in HORIZONS:
            v = veille.get(h)
            if v and v != r.conclusions[h]:
                flips.append(f"- {r.nom} [{h}] : {v} → {r.conclusions[h]} (score {r.scores[h]:+.2f})")
    lines.append("## Flips vs veille")
    if flips:
        lines.extend(flips)
    else:
        # Placeholder court pour que la section existe toujours (la sous-nav
        # HTML s'appuie sur les ## h2 — supprimer la section casserait la nav).
        lines.append("_Aucun changement de position vs veille._")
    lines.append("")
    lines.append("## Matrice (12 actifs × 3 horizons) — primaire ±1, pondéré en annotation")
    lines.append("")
    lines.append("| Actif | 24h | 7j | 1m |")
    lines.append("|---|---|---|---|")
    for r in results:
        cells = []
        cov_pct = coverage_pct(r.coverage)
        for h in HORIZONS:
            conc = r.conclusions[h]
            score = r.scores[h]
            confidence = r.confidence.get(h, "normale")
            # ─── Cellule INSUFFISANT ────────────────────────────────────────
            # Override l'affichage LONG/SHORT : pas de prédiction → 🚫.
            # On ne montre PAS de score ni d'annotation pondérée — la cellule
            # est explicitement non-actionnable. Parsée comme non-prédiction
            # par journaliste (exclue VRAI/FAUX + biais).
            if conc == CONCLUSION_INSUFFISANT:
                cells.append(f"🚫 données insuff. ({cov_pct}%)")
                continue
            gate_flag = " ⚑" if any(c.is_gate and c.gate_active for c in r.criteres) else ""
            tie = " (tb)" if h in r.tie_break_notes else ""
            # Annotation pondérée (secondaire) + ⚠ si divergence
            conc_p = r.conclusions_pond.get(h, "")
            score_p = r.scores_pond.get(h, 0.0)
            div_flag = " ⚠" if r.diverge.get(h) else ""
            pond_str = f" [pond:{conc_p} {score_p:+.2f}]{div_flag}" if conc_p else ""
            # Drapeau news_dominant (Point 4) : 📰 si abs(news)/abs(quant) > 0.5
            # Définition UNIFIÉE avec decision-log (ratio_news abs/abs) — voir l.679-680
            cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            n_tot = abs(float(cap_info.get("news_total_pm1", 0.0)))
            q_tot = abs(float(cap_info.get("quant_total_pm1", 0.0)))
            ratio_news_cell = n_tot / (q_tot + 1e-9)
            news_flag = " 📰" if ratio_news_cell > 0.5 else ""
            # Marqueur coin-flip : |score_pm1| < 0.05 → signal non-actionnable
            coin_flip_flag = " ⚪" if abs(score) < 0.05 else ""
            # Suffixe confiance faible : on garde la direction mais on marque
            # explicitement la fiabilité dégradée (coverage entre MIN et OK,
            # ou données périmées). Ajout APRÈS pond/news/coin_flip pour
            # rester en dernier (le plus visible).
            conf_flag = f" ⚠️ conf. faible ({cov_pct}%)" if confidence == "faible" else ""
            # --- Lot 4a — marqueurs détecteurs directionnels (flag-only) ---
            # Trois angles morts rendus VISIBLES sans modifier la conclusion :
            #   ↯ diverg.    : quant et news en désaccord directionnel (>eps)
            #   ⇄ contre-mom.: conclusion vs momentum prix (RSI) opposés
            #   ⇆ horizons   : zig-zag inter-horizons sur l'actif (1 marqueur/cellule)
            div_qn_flag = " ↯" if r.divergence_quant_news.get(h, False) else ""
            cmom_flag = " ⇄" if r.contre_momentum.get(h, False) else ""
            incoh_flag = " ⇆" if r.incoherence_inter_horizons else ""
            # --- Lot 5 — marqueurs sanity sémantique (FLAG-ONLY) -------------
            # ⌛ already-priced : au moins UN critère news de la cellule a son
            #    event_date plus vieux que la fenêtre déjà-cotée de cet horizon.
            # ⊘ démenti        : au moins UN critère news de la cellule porte
            #    un signal de démenti / correction sur son event source.
            # N'ALTÈRENT PAS la conclusion (mode shadow — on mesure).
            ap_flag = ""
            denial_flag = ""
            for c in r.criteres:
                if c.is_gate or c.is_na:
                    continue
                if c.is_denial:
                    denial_flag = " ⊘"
                if c.event_date and not ap_flag:
                    try:
                        _cdt = datetime.fromisoformat(c.event_date)
                    except ValueError:
                        _cdt = None
                    if _cdt is not None:
                        _ap, _ = _tc_classifier.compute_already_priced_for_horizon(
                            _cdt, h, now=now,
                        )
                        if _ap:
                            ap_flag = " ⌛"
                if ap_flag and denial_flag:
                    break
            cells.append(
                f"{conc} ({score:+.2f}){tie}{gate_flag}{pond_str}{news_flag}"
                f"{coin_flip_flag}{conf_flag}{div_qn_flag}{cmom_flag}{incoh_flag}"
                f"{ap_flag}{denial_flag}"
            )
        lines.append(f"| {r.nom} | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")
    lines.append(
        "**Légende** : ⚑ gate actif · 📰 news>50% du quant (abs/abs) · "
        "⚪ quasi coin-flip (|score|<0.05) — signal non-actionnable, la règle jamais-neutre tranche par défaut · "
        "⚠ divergence pm1/pondéré · "
        "🚫 données insuffisantes (coverage < "
        f"{int(COVERAGE_MIN * 100)}%) — pas de prédiction (override jamais-neutre) · "
        "⚠️ conf. faible (coverage < "
        f"{int(COVERAGE_OK * 100)}% ou données périmées) — direction conservée, fiabilité dégradée · "
        "↯ divergence quant↔news (signes opposés, amplitudes significatives) · "
        "⇄ contre-momentum (conclusion vs RSI 14j opposés) · "
        "⇆ incohérence inter-horizons (zig-zag ≥2 changements de sens) · "
        "⌛ déjà coté (event > fenêtre already-priced de l'horizon : 24h>1j · 7j>3j · 1m>10j) · "
        "⊘ démenti / correction détecté sur l'event source — "
        "Lots 4a/5 : flags visuels, n'altèrent PAS la conclusion (mode shadow)"
    )
    lines.append("")
    lines.append("## Détail par actif")
    for r in results:
        lines.append(f"### {r.nom}")
        lines.append("")
        lines.append("| Critère | Type | Valeur brute | Norm. | Poids | Signe | 24h | 7j | 1m | Note |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for c in r.criteres:
            valeur_brute_str = _fmt_raw(c.valeur_brute)
            vn = "—" if c.valeur_norm is None else f"{c.valeur_norm:+.3f}"
            poids = "—" if c.is_gate else f"{c.poids:g}"
            signe = "—" if c.is_gate else f"{c.signe:+d}"
            ctr = {h: ("—" if c.is_na or c.is_gate else f"{c.contributions[h]:+.3f}") for h in HORIZONS}
            note = c.note
            if c.is_gate and c.gate_active:
                note = "⚑ GATE ACTIF — " + note
            lines.append(
                f"| {c.nom} | {c.type_norm} | {valeur_brute_str} | {vn} | {poids} | {signe} | "
                f"{ctr['24h']} | {ctr['7j']} | {ctr['1m']} | {note} |"
            )
        if r.tie_break_notes:
            lines.append("")
            for h, note in r.tie_break_notes.items():
                lines.append(f"- [{h}] {note}")
        lines.append("")
        lines.append(f"- Scores : 24h={r.scores['24h']:+.3f} · 7j={r.scores['7j']:+.3f} · 1m={r.scores['1m']:+.3f}")
        lines.append("")
    lines.append("## Limites du jour")
    has_limit = False
    for r in results:
        nas = [c for c in r.criteres if c.is_na]
        gates_actifs = [c for c in r.criteres if c.is_gate and c.gate_active]
        if nas or gates_actifs:
            has_limit = True
            lines.append(f"### {r.nom}")
            for c in nas:
                lines.append(f"- n/a : {c.nom} — {c.note}")
            for c in gates_actifs:
                lines.append(f"- ⚑ GATE actif : {c.nom} — {c.note}")
    if not has_limit:
        lines.append("- (aucune)")
    lines.append("")
    return "\n".join(lines)


DECISION_LOG_DIR = ROOT / "data" / "decision-log"


def build_decision_log_records(results: List[ActifResult], now: datetime) -> List[Dict[str, Any]]:
    """Construit la liste de lignes JSONL (une par cellule actif × horizon).

    Chaque ligne contient :
    - bulletin_date, generated_at, fiche_key, actif, horizon
    - critères contributeurs (cle_courante, valeur, valeur_normalisee, valeur_ponderee,
      poids, pertinence, materiality, reliability, source_track, facteur, contrib_pm1, contrib_pond)
    - score_pm1, score_pond, conclusion_pm1, conclusion_pond, diverge
    """
    import math as _math
    # Lot 5 C8a — import paresseux de triggers_classifier (évite couplage dur,
    # cohérent avec le pattern d'import lazy déjà en place ailleurs).
    import triggers_classifier as tc  # noqa: F401  (utilisé plus bas)
    records: List[Dict[str, Any]] = []
    bulletin_date = now.strftime("%Y-%m-%d")
    generated_at = now.isoformat()
    for r in results:
        for h in HORIZONS:
            contribs: List[Dict[str, Any]] = []
            for c in r.criteres:
                if c.is_gate or c.is_na:
                    continue
                # Facteur de pondération réellement appliqué
                # Si valeur_norm ≠ 0 et != None : facteur = valeur_ponderee / valeur_norm
                facteur: Optional[float] = None
                if c.valeur_ponderee is not None and c.valeur_norm not in (None, 0, 0.0):
                    try:
                        facteur = c.valeur_ponderee / c.valeur_norm
                        if _math.isnan(facteur) or _math.isinf(facteur):
                            facteur = None
                    except ZeroDivisionError:
                        facteur = None
                contrib_entry: Dict[str, Any] = {
                    "cle": c.cle_courante,
                    "nom": c.nom,
                    "type_norm": c.type_norm,
                    "valeur": c.valeur_brute if not isinstance(c.valeur_brute, dict)
                              else c.valeur_brute.get("valeur"),
                    "valeur_normalisee": c.valeur_norm,
                    "valeur_ponderee": c.valeur_ponderee,
                    "poids": c.poids,
                    "pertinence": c.pertinence.get(h, 0.0),
                    "signe": c.signe,
                    "materiality": c.materiality,
                    "reliability": c.reliability,
                    "source_track": c.source_track,
                    "facteur": facteur,
                    "contrib_pm1": c.contributions.get(h, 0.0),
                    "contrib_pond": c.contributions_pond.get(h, 0.0),
                }
                # Persistance "pourquoi" DeepSeek (demande Thomas 2026-06-01) :
                # pour les critères news (source_track="ia_*"), on persiste
                # synthese_rationale + conviction (=materiality bucket high/medium/low).
                # Zéro invention : on n'ajoute les champs QUE si le rationale existe
                # réellement dans le meta du triplet (critères non-news → rien).
                if c.source_track.startswith("ia") and c.synthese_rationale:
                    contrib_entry["synthese_rationale"] = c.synthese_rationale
                    contrib_entry["conviction"] = c.materiality
                # --- Phase 2 — méta news (event_id, event_date, nature, ...)
                # Sur les critères news uniquement (ia* / keyword), on persiste
                # la chaîne événement : permet de tracer pourquoi un flip a été
                # bloqué ou autorisé. Zéro invention : on n'ajoute que si l'event_id
                # existe réellement (sinon critère quant pur → rien).
                if c.event_id:
                    contrib_entry["event_id"] = c.event_id
                    contrib_entry["event_date"] = c.event_date
                    contrib_entry["event_date_source"] = c.event_date_source
                    contrib_entry["freshness_days"] = round(c.freshness_days, 3)
                # Nature + coef_nature : on persiste dès qu'on a une nature
                # même sans event_id (cas ia_synthese_faible : DeepSeek a tranché
                # "faible/neutral" → val=0 et pas d'event source explicite, mais
                # la nature dominante des candidats reste pertinente pour M5/T1/T2).
                if c.nature and (c.source_track.startswith("ia")
                                 or c.source_track == "keyword"):
                    contrib_entry["nature"] = c.nature
                    contrib_entry["coef_nature"] = c.coef_nature_applied.get(h, 1.0)
                # Gate C1 — sign_conflict (cohérence de signe DeepSeek) :
                # tracé dès qu'au moins un impact a été neutralisé sur la
                # cellule. Vide sinon (zéro bruit dans le log).
                if c.sign_conflict:
                    contrib_entry["sign_conflict"] = True
                    contrib_entry["sign_conflict_details"] = c.sign_conflict_details
                # Lot 5 C8a — already_priced RELATIF À L'HORIZON.
                # On calcule par cellule (event_date connu, horizon connu). FLAG-ONLY.
                # Émis SEULEMENT si True (zéro bruit dans le log).
                if c.event_date:
                    try:
                        cdt = datetime.fromisoformat(c.event_date)
                    except ValueError:
                        cdt = None
                    if cdt is not None:
                        ap, age_d = tc.compute_already_priced_for_horizon(cdt, h, now=now)
                        if ap:
                            contrib_entry["already_priced"] = True
                            contrib_entry["already_priced_age_days"] = round(age_d or 0.0, 3)
                            contrib_entry["already_priced_horizon"] = h
                # Lot 5 C8b — démenti / correction (FLAG-ONLY).
                if c.is_denial:
                    contrib_entry["is_denial"] = True
                    contrib_entry["denial_keyword"] = c.denial_keyword
                contribs.append(contrib_entry)
            # --- Observabilité ratio_news (Point 4 plan horizon) ----------
            cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            news_total = float(cap_info.get("news_total_pm1", 0.0))
            quant_total = float(cap_info.get("quant_total_pm1", 0.0))
            ratio_news = abs(news_total) / (abs(quant_total) + 1e-9)
            news_dominant = ratio_news > 0.5
            score_pm1_val = r.scores.get(h, 0.0)

            # ---------- Phase 2 — métriques shadow (par cellule) -----------
            # M1 — taux filtrage nature : part des critères news où coef_nature=0
            #      (= deja_cote écarté, ou critère filtré amont par _candidates_for).
            # M2 — taux stale : critères news avec freshness_days*24 > 30j*24.
            # M3 — taux dédup : non-zero dans cap_info (estimation via _resolve_triplet).
            #      Approximé ici par : critère news avec source_track="" (event repost
            #      écarté → pas de contribution news).
            # M4 — gate override BLOQUÉ : il y a un critère news potentiel high+rumor
            #      OU vieux OU nature interdite ET le cap a été appliqué.
            # M5 — composition nature : compteurs par nature sur les critères news.
            # M6 — biais LONG/SHORT (signe du score).
            # M7 — ratio_news (déjà calculé ci-dessus).
            news_crits = [c for c in r.criteres
                          if (c.source_track.startswith("ia") or c.source_track == "keyword")
                          and not c.is_na and not c.is_gate]
            n_news = max(len(news_crits), 1)
            nb_nature_filtered = sum(
                1 for c in news_crits
                if c.coef_nature_applied.get(h, 1.0) == 0.0
            )
            nb_stale = sum(
                1 for c in news_crits if c.freshness_days > 30.0
            )
            nature_composition: Dict[str, int] = {}
            for c in news_crits:
                key = c.nature or "unknown"
                nature_composition[key] = nature_composition.get(key, 0) + 1
            bias_long_short = (
                "LONG" if score_pm1_val > 0 else ("SHORT" if score_pm1_val < 0 else "FLAT")
            )
            # M4 — gate override bloqué : potentiel news high non-rumor mais
            # pas frais OU nature non éligible (deja_cote/verbal).
            override_potential_blocked = any(
                c.materiality == "high"
                and c.reliability not in ("rumor", "")
                and (c.nature not in ("structurel", "ponctuel")
                     or c.freshness_days * 24.0 > 72.0)
                for c in news_crits
            )

            # T1 — faux flips évités : un flip aurait eu lieu sans Phase 2
            # (sans filtrage nature) mais est écarté car porté par deja_cote/verbal.
            # A1 — NOUVEAU : on utilise la CONTRIBUTION FANTÔME agrégée
            # (p2_shadow_contrib_exclu) calculée par triggers_classifier sur les
            # events réellement écartés (deja_cote/stale/repost). Plus besoin
            # d'estimer via valeur_norm × poids — on a la vraie contribution
            # qu'aurait eue chaque event exclu.
            #
            # shadow_contrib_total[h] = somme des shadow contribs sur tous les
            #                           critères news de la cellule pour cet horizon.
            # p2_shadow_flip_potential[h] = True si :
            #   signe(shadow_total) != signe(quant_total)
            #   ET |shadow_total| > |quant_total| × 0.8
            # → la news exclue aurait pu INVERSER le quant (faux changement
            # de tendance évité par Phase 2).
            cap_info_h = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            quant_total = float(cap_info_h.get("quant_total_pm1", 0.0))

            shadow_total_h = 0.0
            for c in news_crits:
                # Le shadow est "pré-poids/signe" → on multiplie ici par poids × signe
                # pour rendre la contribution comparable à quant_total (qui est
                # post-poids).
                sh_raw = c.p2_shadow_contrib_exclu.get(h, 0.0)
                if sh_raw:
                    shadow_total_h += sh_raw * c.poids * c.signe

            # Flip potential : aurait inversé le quant (signes opposés + amplitude)
            SHADOW_FLIP_RATIO = 0.8
            shadow_flip_potential = False
            if quant_total != 0.0 and shadow_total_h != 0.0:
                opposite_signs = (
                    (shadow_total_h > 0 and quant_total < 0)
                    or (shadow_total_h < 0 and quant_total > 0)
                )
                if opposite_signs and abs(shadow_total_h) > abs(quant_total) * SHADOW_FLIP_RATIO:
                    shadow_flip_potential = True

            # T1 — recomputé : 1 si la cellule présente un flip potentiel
            # évité (somme des shadow exclus aurait pu renverser le quant).
            # Fallback historique : si shadow vide (rétro-compat tests sans
            # propagation d'events réels), on conserve l'ancienne heuristique
            # estimative pour ne casser aucun test existant.
            t1_faux_flips_evites = 1 if shadow_flip_potential else 0
            if shadow_total_h == 0.0:
                # Pas de shadow disponible → fallback heuristique legacy
                # (compte les critères deja_cote/verbal dont le raw_contrib
                # aurait inversé le quant). Permet aux tests qui injectent
                # raw=deja_cote sans events réels de continuer à passer.
                for c in news_crits:
                    if c.nature in ("deja_cote", "verbal") and c.contributions.get(h, 0.0) == 0.0:
                        raw_contrib = (
                            (c.valeur_norm or 0.0) * c.poids * c.pertinence.get(h, 0.0) * c.signe
                        )
                        if (raw_contrib > 0 and quant_total < 0) or (raw_contrib < 0 and quant_total > 0):
                            t1_faux_flips_evites += 1

            t2_vrais_flips_qualifies = 0
            for c in news_crits:
                # T2 — vrai flip qualifié : structurel + frais (≤72h) + high
                if (c.nature == "structurel"
                        and c.materiality == "high"
                        and c.freshness_days * 24.0 <= 72.0
                        and c.contributions.get(h, 0.0) != 0.0):
                    # Et signe news vs quant opposé (= ça INVERSE le quant)
                    if ((c.contributions[h] > 0 and quant_total < 0)
                            or (c.contributions[h] < 0 and quant_total > 0)):
                        t2_vrais_flips_qualifies += 1

            # --- Lot 4a — flags directionnels (émis UNIQUEMENT si True) ---
            # Zéro bruit : on n'ajoute les champs au record que lorsque le
            # détecteur a effectivement levé un drapeau. Permet de filtrer
            # facilement le decision-log (`grep divergence_quant_news` etc.).
            directional_flags: Dict[str, Any] = {}
            if r.divergence_quant_news.get(h, False):
                cap_info_dir = r.news_cap_info.get(h, {}) or {}
                directional_flags["divergence_quant_news"] = True
                directional_flags["quant_total_for_divergence"] = round(
                    float(cap_info_dir.get("quant_total_pm1", 0.0)), 6
                )
                directional_flags["news_total_for_divergence"] = round(
                    float(cap_info_dir.get("news_total_pm1", 0.0)), 6
                )
            if r.contre_momentum.get(h, False):
                directional_flags["contre_momentum"] = True
                directional_flags["momentum_valeur"] = round(
                    float(r.momentum_valeur.get(h, 0.0)), 6
                )
                directional_flags["momentum_source_cle"] = r.momentum_source_cle
            # C6 — incoherence_inter_horizons : 1 valeur par actif, mais on la
            # tracé sur CHAQUE horizon pour faciliter le filtrage du log.
            if r.incoherence_inter_horizons:
                directional_flags["incoherence_inter_horizons"] = True

            records.append({
                "bulletin_date": bulletin_date,
                "generated_at": generated_at,
                "fiche_key": r.fiche_key,
                "actif": r.nom,
                "horizon": h,
                "score_pm1": score_pm1_val,
                "score_pond": r.scores_pond.get(h, 0.0),
                # ----- Phase 2 — métriques shadow (racine) ------------------
                "p2_M1_nature_filtered_rate": round(nb_nature_filtered / n_news, 3),
                "p2_M2_stale_rate": round(nb_stale / n_news, 3),
                "p2_M3_dedup_rate": 0.0,  # calculé hors-scoring (au niveau ingest)
                "p2_M4_gate_override_blocked": bool(override_potential_blocked),
                "p2_M5_nature_composition": nature_composition,
                "p2_M6_bias": bias_long_short,
                "p2_M7_ratio_news": round(ratio_news, 4),
                "p2_T1_faux_flips_evites": t1_faux_flips_evites,
                "p2_T2_vrais_flips_qualifies": t2_vrais_flips_qualifies,
                # A1 — shadow contribution agrégée (sur events deja_cote/stale/repost)
                "p2_shadow_contrib_exclu": round(shadow_total_h, 6),
                "p2_shadow_flip_potential": bool(shadow_flip_potential),
                "conclusion_pm1": r.conclusions.get(h, ""),
                "conclusion_pond": r.conclusions_pond.get(h, ""),
                "diverge": bool(r.diverge.get(h, False)),
                "coin_flip": bool(abs(score_pm1_val) < 0.05),
                # Gate suffisance de données (sécurité Thomas) :
                # coverage = même valeur pour toutes les cellules d'un actif
                # (la disponibilité brute des critères ne dépend pas de l'horizon).
                # confidence = peut varier par horizon (futurs : différents seuils
                # de coverage par horizon, ou is_stale par horizon).
                "coverage": round(r.coverage, 4),
                "confidence": r.confidence.get(h, "normale"),
                "criteres": contribs,
                "news_total": news_total,
                "quant_total": quant_total,
                "ratio_news": ratio_news,
                "news_dominant": news_dominant,
                "news_cap_applied": bool(cap_info.get("cap_applied", False)),
                "news_cap_override": bool(cap_info.get("override_high_confirmed", False)),
                **directional_flags,
            })
    return records


def write_decision_log(
    records: List[Dict[str, Any]],
    now: datetime,
    base_dir: Path = DECISION_LOG_DIR,
) -> Path:
    """Append-only : 1 fichier par run (date-hhmm) pour éviter les races."""
    import json as _json
    base_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{now:%Y-%m-%d}-{now:%H%M}.jsonl"
    path = base_dir / fname
    # Append (idempotence : si même run rejoué dans la même minute, on append).
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(_json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    return path


def _fmt_raw(raw: Any) -> str:
    if raw is None:
        return "—"
    if isinstance(raw, dict):
        v = raw.get("valeur", raw.get("valeur_normalisee"))
        return str(v) if v is not None else "—"
    return str(raw)


# ---------------------------------------------------------------------------
# Entrée principale
# ---------------------------------------------------------------------------

def run(
    fiches_dir: Path = FICHES_DIR,
    criteres_path: Path = CRITERES_FILE,
    bulletins_dir: Path = BULLETINS_DIR,
    now: Optional[datetime] = None,
    write: bool = True,
) -> Tuple[Path, List[ActifResult]]:
    now = now or datetime.now(ZoneInfo("Europe/Paris"))
    fiches = load_fiches(fiches_dir)
    data = load_criteres_courants(criteres_path)
    fresh_ok, fresh_msg = check_freshness(data, now=now.astimezone(timezone.utc))
    if not fresh_ok:
        raise RuntimeError(f"FRAÎCHEUR KO : {fresh_msg}")
    bulletins_dir.mkdir(parents=True, exist_ok=True)
    veille_path, veille_conclusions = load_veille(bulletins_dir, now)

    results: List[ActifResult] = []
    for key, fiche in fiches.items():
        valeurs = data.get(key, {}) or {}
        nom_lower = fiche.get("actif", key).lower()
        veille_for_actif = veille_conclusions.get(nom_lower, {})
        results.append(score_actif(key, fiche, valeurs, veille_for_actif))

    fhash = fiches_hash(fiches)
    content = render_bulletin(results, veille_conclusions, now, fhash, fresh_msg)
    out_path = bulletins_dir / f"bulletin-{now:%Y-%m-%d}.md"
    if write:
        out_path.write_text(content, encoding="utf-8")
        logger.info("Bulletin écrit : %s", out_path)
    return out_path, results


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    try:
        path, _ = run()
    except Exception as e:
        logger.error("Scoring KO : %s", e)
        return 1
    print(f"OK : {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
