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

import functools
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

# Version systeme (cutover v2). Import robuste : ajoute le repertoire du script
# au path si besoin (cohérent avec les imports paresseux deja en place ici).
try:
    from system_version import SYSTEM_VERSION
except ImportError:  # pragma: no cover - chemin d'import alternatif
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from system_version import SYSTEM_VERSION

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
# HYSTÉRÉSIS DE MAINTIEN ("carry-forward") — horizon-aware (choix Thomas)
# ---------------------------------------------------------------------------
# Problème résolu : un simple TROU de data (coverage qui tombe sous COVERAGE_MIN
# le temps d'un cycle, ex. FRED 429) faisait basculer une cellule de LONG/SHORT
# valide à `INSUFFISANT` (🚫), EFFAÇANT une direction qui était bonne la veille
# (cas réel : Cuivre LONG confirmé hier → 🚫 aujourd'hui à 35% de couverture).
#
# Nouvelle logique de gate (insérée là où INSUFFISANT était décidé) :
#   coverage ≥ COVERAGE_MIN (0.40)            → comportement inchangé.
#   COVERAGE_FLOOR ≤ coverage < COVERAGE_MIN  → MAINTIEN possible si :
#       (1) il existe une dernière direction valide (LONG/SHORT) au(x) cycle(s)
#           précédent(s) pour ce (fiche_key, horizon),
#       (2) les critères ENCORE présents ne CONTREDISENT pas cette direction
#           (pas de retournement franc : |score| < EPSILON_CARRY = neutre OK ;
#            |score| ≥ EPSILON_CARRY et signe opposé = contradiction → 🚫),
#       (3) le maintien n'est pas PÉRIMÉ (âge < CARRY_MAX_AGE_H[horizon]).
#       → conclusion = direction maintenue, confidence = "faible", is_carry=True,
#         marqueur visuel ⏸. La cellule garde une VRAIE direction → elle EST
#         mesurée comme une prédiction (voulu : si on agirait dessus, on est scoré).
#   coverage < COVERAGE_FLOOR (0.25) OU contradiction OU périmé OU aucune
#       direction antérieure                  → INSUFFISANT (🚫) comme aujourd'hui.
COVERAGE_FLOOR: float = 0.25
# Âge max de maintien par horizon (péremption). Au-delà → 🚫 (on ne maintient
# pas une direction trop vieille sur data partielle). Horizon-aware : un même
# trou de data peut être maintenable en 7j (fenêtre 48h) mais périmé en 1m (24h).
CARRY_MAX_AGE_H: Dict[str, int] = {"24h": 24, "7j": 48, "1m": 24}
# Epsilon de contradiction : réutilise le seuil coin_flip (|score| < 0.05 =
# non-actionnable / neutre). Si |score courant| ≥ EPSILON_CARRY ET signe opposé
# à la direction maintenue → retournement franc → contradiction → 🚫.
EPSILON_CARRY: float = 0.05

# Bande quasi-neutre (K2 — audit trio bulletin 03/06). SHADOW : ne change PAS la
# conclusion (LONG/SHORT reste). Une cellule actionnée dont 0.05 ≤ |note| < 0.30
# porte un drapeau discret « ≈ » (faible conviction, quasi-neutre). Le ⚪ existant
# (|note| < 0.05 = coin-flip) reste intact et prime. But : rendre lisibles les
# quasi-zéros « habillés en SHORT ferme » (ex. S&P 7j −0.09, Cuivre 7j −0.28) sans
# toucher la direction. Mesure inchangée : la cellule reste LONG/SHORT.
NEUTRAL_BAND: float = 0.30

# ---------------------------------------------------------------------------
# GARDE-FOU CONVICTION vs COUVERTURE (« confiant ET aveugle » — Thomas 16/06)
# ---------------------------------------------------------------------------
# Cas réel cacao 16/06 : SHORT « forte » affiché alors que coverage=41% ET le
# critère de POIDS MAX de la fiche (« Arrivées ports » poids 9) était n/a. Le
# système était confiant tout en étant aveugle à son driver structurel principal.
# Règle : une conviction ne peut PAS être « forte » si (a) coverage < ce seuil
# ET (b) le critère non-gate de poids maximal de la fiche est absent (n/a). Dans
# ce cas la conviction est dégradée en « fragile (couverture insuffisante) ».
# La DIRECTION (LONG/SHORT) reste INCHANGÉE (jamais neutre) — seul le LIBELLÉ de
# conviction change, comme les autres dégradations de `_conviction_cell`.
# Distinct du palier confidence "faible" (coverage<COVERAGE_OK) : ce garde-fou
# cible le cas spécifique « confiance haute MALGRÉ le driver max manquant ».
CONVICTION_COVERAGE_MIN: float = 0.50

# Mono-critère dominant (K1 — audit trio bulletin 03/06). SHADOW decision-log only :
# détecte si UN SEUL critère fournit > 50% du |score| (somme des |contributions|).
# Sert à MESURER le sur-poids (ex. VIX régime qui flippe le S&P à lui seul). Pas
# d'affichage matrice (on évite la soupe de symboles).
MONO_CRITERE_RATIO: float = 0.50

# Seuil de poids pour la section "Limites du jour" (#8 audit design 2026-06-02).
# Seuls les critères absents (n/a) de poids >= ce seuil sont listés nominativement
# (ceux qui pèsent vraiment sur la direction) ; les plus légers sont résumés en
# une ligne de comptage. Évite ~45 lignes de n/a redondants avec les tableaux Détail.
LIMITES_POIDS_MIN: float = 8.0

# Nombre max de calls affichés dans « 🔎 Calls 24h jugés » du bulletin markdown
# (C-B3 audit visuel 12/06). ≈ 1 semaine ouvrée. L'historique complet reste
# consultable dans la vue Historique de la page HTML (zéro perte de donnée).
MAX_CALLS_DISPLAYED: int = 7

# ---------------------------------------------------------------------------
# RÉGIME NEWS (ticket D) — actifs structurellement news-driven
# ---------------------------------------------------------------------------
# Problème résolu : certaines matières premières sont pilotées EN PERMANENCE par
# les news (offre/demande géopolitique, météo, récoltes) et n'ont quasi jamais
# assez de critères quant disponibles → elles tombent perpétuellement en 🚫
# INSUFFISANT, alors que le signal LÉGITIME pour ces actifs vient des news.
#
# Comportement : quand la couverture quant est insuffisante (coverage < FLOOR ou
# carry impossible) MAIS que le biais news est NET & DÉCISIF, on affiche le BIAIS
# NEWS (drapeau 📰, confidence "faible") AU LIEU de 🚫. La cellule porte alors une
# VRAIE direction → elle est mesurée comme une prédiction par le Journaliste.
#
# Allowlist configurable : fiche_keys EXACTS des fiches news-driven
# (v3/config/fiches/{cuivre,cacao,cafe}.yml). Étendre cette liste = activer le
# régime news sur un nouvel actif. Aucun autre actif n'est concerné (un actif
# non listé en couverture insuffisante → 🚫 comme avant, même news net).
NEWS_DRIVEN_ASSETS: set = {"cuivre", "cacao", "cafe"}
# Seuil de dominance news : abs(news) / abs(quant) > NEWS_DOMINANT_RATIO = la news
# pilote la cellule (réutilise le seuil 0.5 déjà appliqué à news_dominant).
NEWS_DOMINANT_RATIO: float = 0.5


def compute_news_bias(
    criteres: List["CritereResult"], h: str
) -> Tuple[Optional[str], float, float, float]:
    """Calcule le biais directionnel news vs quant pour un horizon.

    Source de vérité UNIQUE (factorisée) pour :
      - le diagnostic news_dominant / ratio_news du decision-log,
      - la décision de RÉGIME NEWS (ticket D) dans le gate de score_actif.

    Sépare les contributions news (source_track démarrant par "ia") des quant
    (tout le reste), exclut les critères is_na/is_gate (contributions 0, neutres).

    Retourne (bias, ratio_news, news_total, quant_total) où :
      - bias = "LONG" si news_total > 0, "SHORT" si < 0, None si quasi nul
               (|news_total| < EPSILON_CARRY → neutre, pas de direction).
      - ratio_news = abs(news_total) / (abs(quant_total) + eps).
    """
    news_total = sum(
        c.contributions[h] for c in criteres
        if c.source_track.startswith("ia") and not c.is_na and not c.is_gate
    )
    quant_total = sum(
        c.contributions[h] for c in criteres
        if not c.source_track.startswith("ia") and not c.is_na and not c.is_gate
    )
    ratio_news = abs(news_total) / (abs(quant_total) + 1e-9)
    if abs(news_total) < EPSILON_CARRY:
        bias: Optional[str] = None
    else:
        bias = "LONG" if news_total > 0 else "SHORT"
    return bias, ratio_news, news_total, quant_total

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
RAISONS_DRIVERS_FILE = ROOT / "config" / "raisons-drivers.yml"


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
    # Affichage lisible de l'âge (le timedelta brut donne "-1 day, 23:59:59.99"
    # quand la donnée est quasi à l'heure → incompréhensible). On le traduit.
    age_h = age.total_seconds() / 3600.0
    if age_h < 1:
        age_label = "données du jour (< 1h)"
    elif age_h < 24:
        age_label = f"âge ≈ {age_h:.0f}h"
    else:
        age_label = f"âge ≈ {age_h / 24:.1f} j"
    if age > FRESHNESS_MAX:
        return False, (
            f"criteres-courants PÉRIMÉ : {age_label}, dernier update={last_dt.isoformat()} "
            f"(seuil {FRESHNESS_MAX})"
        )
    return True, f"fraîcheur OK — {age_label}"


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

    # Composite / mapping_non_monotone : la normalisation est faite EN AMONT par
    # criteres_calculator (_handle_composite / _handle_mapping_non_monotone, qui
    # émettent `valeur_normalisee`). On consomme la valeur pré-calculée, comme le
    # fait zscore ci-dessus. Sans cette branche, ces critères (souvent à fort
    # poids : météo Brésil composite poids 11, VIX regime poids 8, etc.) tombaient
    # en « type inconnu » et étaient jetés en silence (poids effectif perdu).
    if type_norm in ("composite", "mapping_non_monotone"):
        if valeur_norm_precalc is not None:
            try:
                vn = float(valeur_norm_precalc)
            except (TypeError, ValueError):
                return None, f"n/a ({type_norm} : valeur_normalisee non numérique)"
            return _clip(vn, cap), f"{type_norm} (pré-calculé)"
        return None, f"n/a ({type_norm} : valeur_normalisee absente)"

    # Zscore_abs : normalisation SYMÉTRIQUE « écart à la normale dans les 2 sens »
    # (cacao météo : sécheresse OU excès = haussier). La valeur_normalisee est
    # pré-calculée en amont par criteres_calculator (_handle_meteo via
    # zscore_abs_normalisee) ; le scoring la consomme telle quelle, exactement
    # comme zscore/composite. Le signe +1 de la fiche reste appliqué en aval
    # (norm>0 = haussier).
    if type_norm == "zscore_abs":
        if valeur_norm_precalc is not None:
            try:
                vn = float(valeur_norm_precalc)
            except (TypeError, ValueError):
                return None, "n/a (zscore_abs : valeur_normalisee non numérique)"
            return _clip(vn, cap), "zscore_abs (écart normale, pré-calculé)"
        return None, "n/a (zscore_abs : valeur_normalisee absente)"

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
    # --- Hystérésis de maintien (carry-forward) ----------------------------
    # is_carry[h] = True si la conclusion de l'horizon h est une DIRECTION
    # MAINTENUE (LONG/SHORT carry-forward) au lieu d'un INSUFFISANT, parce que
    # COVERAGE_FLOOR ≤ coverage < COVERAGE_MIN + direction antérieure cohérente
    # et récente. Rendu visuel : ⏸. La cellule reste une vraie prédiction
    # (mesurée VRAI/FAUX). Vide/False ailleurs.
    is_carry: Dict[str, bool] = field(default_factory=dict)
    # --- Régime news (ticket D) --------------------------------------------
    # is_news_regime[h] = True si la conclusion de l'horizon h est une DIRECTION
    # issue du BIAIS NEWS (actif news-driven + couverture quant insuffisante +
    # biais news net & décisif), affichée AU LIEU d'un INSUFFISANT. La cellule
    # porte alors une VRAIE direction (LONG/SHORT, confidence "faible") → mesurée
    # comme prédiction. Rendu visuel : 📰. Vide/False ailleurs. Mutuellement
    # exclusif avec is_carry (le carry prime ; voir gate dans score_actif).
    is_news_regime: Dict[str, bool] = field(default_factory=dict)
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

    A6 (audit momentum-family 10/06) — le momentum-prix (cle préfixe
    "momentum_prix_") est EXCLU du calcul de couverture (numérateur ET
    dénominateur). Raison : le momentum est toujours disponible via Twelve
    (donnée prix), donc l'inclure gonfle mécaniquement la couverture pondérée →
    fait repasser des cellules au-dessus du plancher COVERAGE_MIN → éteint le
    filet `is_news_regime` (drapeau 📰) qui rendait la voix aux news quand le
    quant manquait (exactement ce qui a sauvé le diagnostic cacao). Exclusion
    GLOBALE (pas seulement les NEWS_DRIVEN_ASSETS) : conservateur, ne gonfle la
    couverture d'AUCUN actif via un critère structurellement toujours présent.
    Le filet 📰 ne s'active de toute façon que pour les NEWS_DRIVEN_ASSETS.

    Cas limites :
    - Aucun critère non-gate (fiche dégénérée) → coverage = 1.0 (par
      convention : "100% de rien est couvert", on ne pénalise pas une fiche
      vide ; le rôle du gate est de détecter les TROUS).
    - Tous les poids à 0 → coverage = 1.0 (idem).
    """
    non_gate = [
        c for c in criteres
        if not c.is_gate and not c.cle_courante.startswith("momentum_prix_")
    ]
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


def compute_note_normalisee(
    criteres: "List[CritereResult]", note_brute: float, horizon: str,
) -> Optional[float]:
    """Intensité COMPARABLE entre actifs = note brute ÷ Σ|poids effectif couvert|.

    PROBLÈME (audit Analyst) : la note (score) est une SOMME BRUTE de contributions
    `valeur_norm × poids × pertinence`. Sa magnitude dépend du NOMBRE et du POIDS des
    critères réellement disponibles → « Cacao +6,45 » et « CAC +0,61 » ne sont PAS
    comparables entre actifs (un actif à 6 critères forts couverts pèse mécaniquement
    plus qu'un actif à 2 critères faibles). À l'intérieur d'un actif c'est bon ;
    ENTRE actifs c'est trompeur.

    FIX (PUR AFFICHAGE, INFORMATIF) : on ramène la note à une échelle ~[-1, +1] en
    divisant par le poids effectif MAXIMAL atteignable sur les critères COUVERTS de
    cette cellule (actif × horizon) :

        note_norm = note_brute / Σ ( |poids| × pertinence[horizon] )   sur critères
                    non-gate, non-momentum, valeur_norm disponible (= « couverts »).

    Comme |valeur_norm| ≤ cap = 1, chaque contribution est bornée par
    |poids| × pertinence, donc note_norm ∈ [-1, +1] : intensité comparable entre
    actifs indépendamment du nombre de critères actifs.

    DÉGRADATION PROPRE : aucun critère couvert (dénominateur ≤ 0) → None (le rendu
    affiche « — »). Le momentum-prix est EXCLU comme dans `compute_coverage`
    (toujours présent → gonflerait artificiellement le dénominateur).

    RED LINE : n'altère NI la note brute, NI la direction, NI la sélection. Purement
    une seconde lecture (intensité), jamais décisionnelle.
    """
    denom = 0.0
    for c in criteres:
        if c.is_gate or c.is_na or c.valeur_norm is None:
            continue
        if c.cle_courante.startswith("momentum_prix_"):
            continue
        pert = float(c.pertinence.get(horizon, 0.0)) if c.pertinence else 0.0
        denom += abs(float(c.poids)) * pert
    if denom <= 0:
        return None
    return float(note_brute) / denom


def derniere_direction_valide(
    fiche_key: str,
    horizon: str,
    now: datetime,
    max_age_h: float,
    *,
    log_dir: Optional[Path] = None,
    exclude_generated_at: Optional[str] = None,
) -> Optional[str]:
    """Cherche la dernière direction valide (LONG/SHORT) d'une cellule.

    Scanne les snapshots `v3/data/decision-log/*.jsonl` du plus RÉCENT au plus
    ANCIEN (le nom de fichier `YYYY-MM-DD-HHMM.jsonl` donne l'ordre chronologique),
    en EXCLUANT le run courant, dans la fenêtre d'âge `max_age_h`. Retourne la
    première `conclusion_pond` ∈ {LONG, SHORT} trouvée pour (fiche_key, horizon).

    Robustesse (zéro exception, jamais de crash de la prod) :
      - dossier absent / vide                → None
      - fichier illisible / JSON mal formé   → ligne ignorée, on continue
      - `generated_at` absent / illisible    → ligne ignorée (impossible de
                                                dater → ne peut pas valider l'âge)
      - run courant (exclude_generated_at)   → fichier entier ignoré
      - conclusion INSUFFISANT/FLAT/vide     → ignorée (on cherche une direction)

    `exclude_generated_at` : le `generated_at` ISO du run courant. Un snapshot
    portant exactement cette valeur est ignoré (on ne maintient pas sur soi-même
    si le decision-log courant a déjà été écrit dans la même minute).
    """
    import json as _json

    base = log_dir if log_dir is not None else DECISION_LOG_DIR
    try:
        if not base.exists():
            return None
        files = sorted(base.glob("*.jsonl"), reverse=True)  # plus récent d'abord
    except OSError:
        return None

    now_utc = now.astimezone(timezone.utc) if now.tzinfo else now.replace(tzinfo=timezone.utc)
    cutoff = now_utc - timedelta(hours=float(max_age_h))

    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = _json.loads(line)
            except (ValueError, TypeError):
                continue
            if not isinstance(rec, dict):
                continue
            if rec.get("fiche_key") != fiche_key or rec.get("horizon") != horizon:
                continue
            gen = rec.get("generated_at")
            if exclude_generated_at and gen == exclude_generated_at:
                continue
            # Datation : indispensable pour valider la fenêtre de péremption.
            if not isinstance(gen, str):
                continue
            try:
                gen_dt = datetime.fromisoformat(gen)
            except ValueError:
                continue
            if gen_dt.tzinfo is None:
                gen_dt = gen_dt.replace(tzinfo=timezone.utc)
            gen_utc = gen_dt.astimezone(timezone.utc)
            if gen_utc < cutoff:
                # Trop ancien pour CE snapshot — mais un fichier plus récent
                # listé après ? Non : on parcourt du plus récent au plus ancien,
                # donc une fois sous le cutoff on continue de scanner les autres
                # lignes du fichier (ordre intra-fichier non garanti), puis on
                # laisse la boucle externe passer aux fichiers suivants (plus
                # vieux → tous sous le cutoff → None par épuisement). On ne `break`
                # pas : robustesse face à un ordre intra-fichier non chronologique.
                continue
            conc = rec.get("conclusion_pond")
            if conc in ("LONG", "SHORT"):
                return conc
    return None


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
    now: Optional[datetime] = None,
    log_dir: Optional[Path] = None,
    current_generated_at: Optional[str] = None,
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
        # A2 (audit momentum-family 10/06) — contribution du momentum-prix.
        # Le momentum (cle_courante préfixe "momentum_prix_") est un critère QUANT :
        # il GARDE sa voix dans quant_total (donc dans le score), mais il ne doit
        # JAMAIS participer au PLAFONNEMENT des news (cap). Sinon, en tendance
        # finissante, un momentum encore haussier par inertie gonfle quant_total →
        # le cap laissé aux news SHORT explose mécaniquement (~7×) pile au
        # retournement où la news a raison (l'autre face du bug cacao).
        # On identifie la contribution momentum de façon robuste par le préfixe de
        # clé (documenté ; aligné sur TWELVE_SYMBOLS momentum_prix_20j_*).
        contrib_momentum = sum(
            c.contributions[h] for c in criteres_res
            if c.cle_courante.startswith("momentum_prix_")
            and not c.source_track.startswith("ia")
            and not c.is_na and not c.is_gate
        )
        contrib_momentum_p = sum(
            c.contributions_pond[h] for c in criteres_res
            if c.cle_courante.startswith("momentum_prix_")
            and not c.source_track.startswith("ia")
            and not c.is_na and not c.is_gate
        )
        # Base du cap = quant SANS le momentum (cap aveugle au momentum).
        quant_cap_base = quant_total - contrib_momentum
        quant_cap_base_p = quant_total_p - contrib_momentum_p
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
            # PM1 : cap AVEUGLE AU MOMENTUM (A2). Le plafond et son déclenchement
            # sont calculés sur quant_cap_base = quant_total − contrib_momentum.
            # Le momentum garde sa voix dans quant_total (et donc le score), mais
            # ne sert jamais à étouffer une news qui le contredit.
            if (news_total > 0 > quant_cap_base) or (news_total < 0 < quant_cap_base):
                cap_abs = abs(quant_cap_base) * ALPHA
                if abs(news_total) > cap_abs:
                    sign_n = 1.0 if news_total > 0 else -1.0
                    news_total_capped = cap_abs * sign_n
                    applied = True
            # Pondéré : même logique en parallèle, aveugle au momentum.
            if (news_total_p > 0 > quant_cap_base_p) or (news_total_p < 0 < quant_cap_base_p):
                cap_abs_p = abs(quant_cap_base_p) * ALPHA
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
            # A2 — observabilité du cap aveugle au momentum : contribution momentum
            # exclue de la base de plafonnement, et base effective du cap.
            "contrib_momentum": round(contrib_momentum, 6),
            "contrib_momentum_pond": round(contrib_momentum_p, 6),
            "cap_quant_ex_momentum": round(quant_cap_base, 6),
            "cap_quant_ex_momentum_pond": round(quant_cap_base_p, 6),
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
    is_carry: Dict[str, bool] = {h: False for h in HORIZONS}
    is_news_regime: Dict[str, bool] = {h: False for h in HORIZONS}
    now_carry = now or datetime.now(timezone.utc)
    for h in HORIZONS:
        confidence[h] = derive_confidence(coverage, is_stale=is_stale)
        if confidence[h] != "insuffisant":
            continue
        # confidence == "insuffisant" → coverage < COVERAGE_MIN.
        # HYSTÉRÉSIS DE MAINTIEN : avant d'effacer la direction par 🚫, on tente
        # un carry-forward si la couverture reste au-dessus du PLANCHER et qu'il
        # existe une direction antérieure cohérente et récente (cf. CONSTANTES).
        maintenu: Optional[str] = None
        if coverage >= COVERAGE_FLOOR:
            max_age_h = CARRY_MAX_AGE_H.get(h, 0)
            if max_age_h > 0:
                derniere = derniere_direction_valide(
                    fiche_key, h, now_carry, max_age_h,
                    log_dir=log_dir,
                    exclude_generated_at=current_generated_at,
                )
                if derniere in ("LONG", "SHORT"):
                    # Contradiction ? Le score courant (sur critères présents)
                    # a-t-il un signe OPPOSÉ avec une magnitude non négligeable ?
                    # |score| < EPSILON_CARRY = neutre → PAS de contradiction.
                    score_courant = scores.get(h, 0.0)
                    sens_courant = (
                        "LONG" if score_courant > 0
                        else ("SHORT" if score_courant < 0 else None)
                    )
                    contradit = (
                        abs(score_courant) >= EPSILON_CARRY
                        and sens_courant is not None
                        and sens_courant != derniere
                    )
                    if not contradit:
                        maintenu = derniere

        if maintenu is not None:
            # MAINTIEN : on conserve une VRAIE direction (mesurée comme prédiction).
            # confidence reste dégradée à "faible" (data partielle) + drapeau ⏸.
            conclusions[h] = maintenu
            conclusions_pond[h] = maintenu
            confidence[h] = "faible"
            is_carry[h] = True
            tie_notes.pop(h, None)
            tie_notes_pond.pop(h, None)
            diverge[h] = False
            continue

        # --- RÉGIME NEWS (ticket D) — priorité 3, APRÈS le carry échoué -----
        # Le carry n'a PAS pu maintenir une direction (maintenu is None). Pour un
        # actif structurellement news-driven, on regarde si le biais NEWS est net
        # & décisif : si oui, on affiche cette direction (📰, confidence "faible")
        # AU LIEU de 🚫. La cellule porte alors une vraie direction → mesurée.
        # Le carry primant déjà (on est dans la branche maintenu is None), il n'y
        # a pas de conflit d'ordre : 1) quant, 2) carry, 3) news, 4) 🚫.
        if fiche_key in NEWS_DRIVEN_ASSETS:
            bias_news, ratio_news_h, _, _ = compute_news_bias(criteres_res, h)
            news_decisif = (
                bias_news in ("LONG", "SHORT")
                and ratio_news_h > NEWS_DOMINANT_RATIO
            )
            if news_decisif:
                conclusions[h] = bias_news
                conclusions_pond[h] = bias_news
                confidence[h] = "faible"
                is_news_regime[h] = True
                tie_notes.pop(h, None)
                tie_notes_pond.pop(h, None)
                diverge[h] = False
                continue

        # --- INSUFFISANT (priorité 4, défaut) ------------------------------
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
        is_carry=is_carry,
        is_news_regime=is_news_regime,
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
    # Exclut TOUS les créneaux du jour courant (3 runs/jour : matin/midi/soir
    # partagent le même préfixe date). On compare la date UTC du run (cohérent
    # avec le nommage du writer). Match par préfixe : exclut bulletin-{date}.md
    # (ancien nommage) ET bulletin-{date}-HHh.md (nouveau nommage).
    today_utc = today.astimezone(timezone.utc) if today.tzinfo else today
    today_prefix = f"bulletin-{today_utc:%Y-%m-%d}"
    files = sorted(
        [
            p
            for p in bulletins_dir.glob("bulletin-*.md")
            if p.stem != today_prefix and not p.stem.startswith(today_prefix + "-")
        ],
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
# C7 — Surveillance & cohérence biais (publication & observabilité)
# ---------------------------------------------------------------------------
#
# Lot 6 / C7 : Thomas doit VOIR sans scanner la matrice :
#   (a) Les cellules portant au moins un drapeau de risque (bloc surveillance)
#   (b) La cohérence entre la ligne agrégée LONG/SHORT et le compte réel des
#       conclusions par actif (assertion testable, log ERROR si bug).
#
# Additif : ne change AUCUNE conclusion / score / seuil / pondération.
# ---------------------------------------------------------------------------

# Drapeaux de risque (sémantique alignée avec render_bulletin / build_decision_log_records)
SURVEILLANCE_FLAGS = {
    "insuffisant": "🚫",     # conclusion INSUFFISANT (gate suffisance)
    "news_regime": "📰",     # régime news (ticket D — direction issue du biais news)
    "carry": "⏸",            # direction maintenue (carry-forward, data partielle)
    "conf_low": "⚠️",        # confidence == "faible"
    "divergence_qn": "↯",   # divergence quant↔news
    "contre_momentum": "⇄", # conclusion vs RSI opposés
    "incoherence_ih": "⇆",  # incohérence inter-horizons (1 marqueur/actif)
    "deja_cote": "⌛",       # already-priced
    "dementi": "⊘",         # démenti / correction
    "mono_critere": "◧",    # A1 — un seul critère porte >50% du |score| (fragilité)
}


def _compute_cell_risk_flags(
    r: "ActifResult",
    h: str,
    now: datetime,
) -> List[str]:
    """Retourne la liste des libellés de drapeaux de risque pour (actif, horizon).

    Mêmes critères que render_bulletin (mode shadow — n'altère PAS la conclusion).
    Importé paresseusement pour éviter circular imports.
    """
    import triggers_classifier as _tc_classifier  # noqa: F401

    flags: List[str] = []
    conc = r.conclusions.get(h, "")
    confidence = r.confidence.get(h, "normale")

    # 🚫 insuffisant — prioritaire (override de la direction)
    if conc == CONCLUSION_INSUFFISANT:
        flags.append(SURVEILLANCE_FLAGS["insuffisant"])
    elif r.is_news_regime.get(h, False):
        # 📰 régime news (ticket D) — direction issue du biais news faute de quant.
        # Prioritaire sur carry/conf_low (le carry n'a pas pu maintenir : exclusif).
        flags.append(SURVEILLANCE_FLAGS["news_regime"])
    elif r.is_carry.get(h, False):
        # ⏸ direction maintenue (carry-forward) — plus précis que ⚠️ générique.
        flags.append(SURVEILLANCE_FLAGS["carry"])
    elif confidence == "faible":
        flags.append(SURVEILLANCE_FLAGS["conf_low"])

    # ↯ divergence quant↔news
    if r.divergence_quant_news.get(h, False):
        flags.append(SURVEILLANCE_FLAGS["divergence_qn"])
    # ⇄ contre-momentum
    if r.contre_momentum.get(h, False):
        flags.append(SURVEILLANCE_FLAGS["contre_momentum"])
    # ⇆ incohérence inter-horizons (1 par actif — répété sur chaque cellule
    #    de l'actif concerné pour que la cellule apparaisse dans surveillance)
    if r.incoherence_inter_horizons:
        flags.append(SURVEILLANCE_FLAGS["incoherence_ih"])

    # ⌛ déjà coté / ⊘ démenti : balayer les critères news de l'actif
    ap_present = False
    denial_present = False
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        if c.is_denial:
            denial_present = True
        if c.event_date and not ap_present:
            try:
                _cdt = datetime.fromisoformat(c.event_date)
            except ValueError:
                _cdt = None
            if _cdt is not None:
                _ap, _ = _tc_classifier.compute_already_priced_for_horizon(
                    _cdt, h, now=now,
                )
                if _ap:
                    ap_present = True
        if ap_present and denial_present:
            break
    if ap_present:
        flags.append(SURVEILLANCE_FLAGS["deja_cote"])
    if denial_present:
        flags.append(SURVEILLANCE_FLAGS["dementi"])

    # ◧ mono-critère dominant (A1) — alerte de FRAGILITÉ sur une direction actée :
    # un seul critère porte >50% du |score|. Réservé aux directions LONG/SHORT
    # (un INSUFFISANT n'a pas de direction à fragiliser).
    if conc in ("LONG", "SHORT"):
        mono_dom, _ = detect_mono_critere_dominant(r, h)
        if mono_dom:
            flags.append(SURVEILLANCE_FLAGS["mono_critere"])

    return flags


# Flags de surveillance considérés comme des ALERTES réelles et actionnables :
# une divergence quant↔news, un contre-momentum, un démenti, un déjà-coté ou
# une incohérence inter-horizons portent un risque DIRECTIONNEL sur une décision
# ACTÉE (LONG/SHORT). À l'inverse, ⚠️ conf. faible / ⏸ carry / 📰 régime news
# sont des QUALIFICATEURS de couverture déjà visibles dans la table de synthèse :
# isolés (sans alerte directionnelle), ils ne justifient PAS une ligne de
# surveillance dédiée (anti-bruit #5.2).
SURVEILLANCE_ALERTES_FORTES = {
    SURVEILLANCE_FLAGS["divergence_qn"],     # ↯
    SURVEILLANCE_FLAGS["contre_momentum"],   # ⇄
    SURVEILLANCE_FLAGS["incoherence_ih"],    # ⇆
    SURVEILLANCE_FLAGS["deja_cote"],         # ⌛
    SURVEILLANCE_FLAGS["dementi"],           # ⊘
    SURVEILLANCE_FLAGS["mono_critere"],      # ◧ — fragilité mono-critère (A1)
}


def _cellule_a_surveiller(r: "ActifResult", h: str, flags: List[str]) -> bool:
    """Décide si une cellule mérite une ligne dans 'Cellules à surveiller'.

    Resserrement #5.2 — ne garde que les cellules réellement actionnables ET
    problématiques :
      - EXCLUT les INSUFFISANT (🚫) : déjà listés dans leur propre section.
      - EXCLUT les cellules dont les seuls flags sont des qualificatifs de
        couverture (⚠️ / ⏸ / 📰) sans alerte directionnelle forte.
      - GARDE les directions ACTÉES (LONG/SHORT) portant ≥ 1 alerte forte
        (divergence ↯, contre-momentum ⇄, incohérence ⇆, déjà-coté ⌛, démenti ⊘).
    """
    if not flags:
        return False
    conc = r.conclusions.get(h, "")
    if conc not in ("LONG", "SHORT"):
        return False  # exclut INSUFFISANT (et tout non-directionnel)
    return any(f in SURVEILLANCE_ALERTES_FORTES for f in flags)


def build_surveillance_block(
    results: List["ActifResult"],
    now: datetime,
) -> List[str]:
    """Construit le bloc '## ⚠️ Cellules à surveiller'.

    Liste UNIQUEMENT les cellules ACTÉES (LONG/SHORT) portant une alerte
    directionnelle forte (cf. `_cellule_a_surveiller`). Les INSUFFISANT et les
    cellules dont le seul flag est un qualificatif de couverture sont exclus
    (anti-bruit #5.2). Format ligne : `- Actif Horizon — DIRECTION — [drapeaux]`.
    Si aucune → ligne placeholder.
    """
    lines: List[str] = []
    lines.append("## ⚠️ Cellules à surveiller")
    lines.append("")
    rows: List[str] = []
    for r in results:
        for h in HORIZONS:
            flags = _compute_cell_risk_flags(r, h, now)
            if not _cellule_a_surveiller(r, h, flags):
                continue
            direction = r.conclusions.get(h, "")
            flags_str = " ".join(flags)
            rows.append(f"- {r.nom} {h} — {direction} — [{flags_str}]")
    if rows:
        lines.extend(rows)
    else:
        lines.append("_Aucune cellule à risque directionnel ce cycle._")
    lines.append("")
    return lines


def compute_bias_aggregate(results: List["ActifResult"]) -> Dict[str, int]:
    """Compte les conclusions agrégées sur toutes les cellules (actif × horizon).

    Source de vérité : r.conclusions[h] directement. Retourne :
      { "LONG": n, "SHORT": n, "INSUFFISANT": n, "total": n }
    """
    counts = {"LONG": 0, "SHORT": 0, CONCLUSION_INSUFFISANT: 0, "total": 0}
    for r in results:
        for h in HORIZONS:
            conc = r.conclusions.get(h, "")
            counts["total"] += 1
            if conc in counts:
                counts[conc] += 1
    return counts


def assert_bias_coherence(
    aggregate: Dict[str, int],
    results: List["ActifResult"],
) -> Tuple[bool, str]:
    """Vérifie que l'agrégat global = le compte réel par actif×horizon.

    Re-calcule indépendamment depuis results (cellule par cellule, sans passer
    par compute_bias_aggregate) et compare. Si incohérence → log ERROR + message
    de marqueur retourné. Sinon (True, "").

    Détecte un bug d'agrégation (ex : double comptage, oubli d'une cellule).
    """
    recount = {"LONG": 0, "SHORT": 0, CONCLUSION_INSUFFISANT: 0, "total": 0}
    for r in results:
        for h in HORIZONS:
            recount["total"] += 1
            conc = r.conclusions.get(h, "")
            if conc == "LONG":
                recount["LONG"] += 1
            elif conc == "SHORT":
                recount["SHORT"] += 1
            elif conc == CONCLUSION_INSUFFISANT:
                recount[CONCLUSION_INSUFFISANT] += 1
    if (
        aggregate.get("LONG", -1) != recount["LONG"]
        or aggregate.get("SHORT", -1) != recount["SHORT"]
        or aggregate.get(CONCLUSION_INSUFFISANT, -1) != recount[CONCLUSION_INSUFFISANT]
        or aggregate.get("total", -1) != recount["total"]
    ):
        msg = (
            f"INCOHÉRENCE BIAIS : agrégat={aggregate} vs recount={recount}"
        )
        logger.error(msg)
        return False, msg
    return True, ""


# ---------------------------------------------------------------------------
# Bulletin
# ---------------------------------------------------------------------------

# Définitions courtes de chaque symbole (1 symbole = 1 ligne). Affichées
# UNIQUEMENT si le symbole est présent dans CE bulletin (légende compacte).
_LEGENDE_DEFS: List[Tuple[str, str]] = [
    ("🚫", "données insuffisantes — pas de prédiction"),
    ("⏸", "direction maintenue (carry-forward) — data partielle, dernière direction valide conservée"),
    ("⚑", "gate régime extrême actif"),
    ("📰", "news >50% du quant — pondéré en tête, brut entre parenthèses ; ou régime news (direction issue du biais news faute de couverture quant)"),
    ("⚪", "quasi coin-flip (|score|<0.05) — non-actionnable"),
    ("≈", "faible conviction (|note|<0.30) — quasi-neutre (direction conservée)"),
    ("⚠", "divergence primaire / pondéré"),
    ("⚠️", "confiance faible (coverage bas ou données périmées) — direction conservée"),
    ("↯", "divergence quant ↔ news (signes opposés)"),
    ("⇄", "contre-momentum (conclusion vs RSI 14j opposés)"),
    ("⇆", "incohérence inter-horizons (zig-zag)"),
    ("⌛", "déjà coté (event hors fenêtre already-priced)"),
    ("⊘", "démenti / correction détecté sur l'event source"),
    ("◧", "mono-critère dominant (>50% du score sur 1 seul critère) — fragilité, à lire avec prudence"),
    ("⚭", "driver macro partagé — plusieurs cellules de même direction portées par le MÊME signal macro (faux consensus, voir bloc dédié)"),
]


def _build_legende(flags_present: set) -> str:
    """Construit une légende COMPACTE : une ligne courte par symbole, et
    seulement pour les symboles réellement présents dans CE bulletin.

    Les flags 4a/5 (↯ ⇄ ⇆ ⌛ ⊘) et ⚠/⚠️ sont visuels : ils n'altèrent PAS la
    conclusion (mode shadow).
    """
    lines: List[str] = ["**Légende** (symboles présents) :", ""]
    any_shadow = False
    for sym, desc in _LEGENDE_DEFS:
        if sym not in flags_present:
            continue
        if sym in ("↯", "⇄", "⇆", "⌛", "⊘", "⚠", "⚠️", "◧"):
            any_shadow = True
        lines.append(f"- {sym} {desc}")
    # Échelle de la Note (toujours affichée) : la Note est une somme pondérée
    # signée, sans borne fixe — son amplitude dépend de la couverture de l'actif.
    # On la lit donc conjointement avec la confiance (%).
    lines.append("")
    lines.append(
        "_**Note** = somme pondérée signée des critères (signe × poids × "
        "pertinence par horizon). Plus |Note| est élevée, plus le signal est "
        "marqué ; il n'y a pas de borne fixe (l'amplitude dépend de la "
        "couverture) — à lire avec la confiance %._"
    )
    if any_shadow:
        lines.append("")
        lines.append("_Les flags visuels (↯ ⇄ ⇆ ⌛ ⊘ ⚠ ⚠️) n'altèrent PAS la conclusion (mode shadow)._")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Régime extrême — annonce UNE fois (anti-bruit visuel #5.1)
# ---------------------------------------------------------------------------
#
# Le gate "régime extrême" est souvent actif sur (quasi) tous les actifs : un
# ⚑ répété sur 12 lignes de la matrice = 0 information utile. On l'annonce
# UNE fois en tête si le gate est actif sur la quasi-totalité des actifs, et on
# retire le ⚑ répété des cellules de la table fusionnée (il reste dans le
# "Détail par actif" où il a un sens, ligne par critère).
#
# Seuil : ≥ 90% des actifs avec gate actif → annonce globale + masquage du ⚑
# répété. Sous ce seuil, le ⚑ reste sur les cellules concernées (info utile car
# discriminante). NE CHANGE PAS la logique du gate — uniquement son affichage.
# ---------------------------------------------------------------------------

REGIME_EXTREME_RATIO = 0.9  # part d'actifs avec gate actif déclenchant l'annonce globale


def _actif_gate_actif(r: "ActifResult") -> bool:
    """True si au moins un gate régime extrême est actif sur cet actif."""
    return any(c.is_gate and c.gate_active for c in r.criteres)


def regime_extreme_global(results: List["ActifResult"]) -> bool:
    """True si le gate régime extrême est actif sur (quasi) tous les actifs.

    Dans ce cas, le ⚑ répété par cellule n'apporte rien → on l'annonce 1× en
    tête et on le masque dans la table de synthèse fusionnée.
    """
    if not results:
        return False
    n_actifs = len(results)
    n_gate = sum(1 for r in results if _actif_gate_actif(r))
    return n_gate >= REGIME_EXTREME_RATIO * n_actifs


# ---------------------------------------------------------------------------
# Top 3 convictions du jour (#4.1) — vue d'oiseau en tête de bulletin
# ---------------------------------------------------------------------------
#
# Sélection : les 3 cellules (actif × horizon) ACTIONNABLES avec la plus forte
# |note| ET une couverture saine (confidence "normale" : ni faible, ni carry,
# ni régime news, ni insuffisant, ni quasi coin-flip). Si moins de 3 cellules
# "normale" existent, on en montre moins (jamais de remplissage avec du faible).
#
# Raison courte = nom du critère contributeur DOMINANT (|contribution| max sur
# l'horizon), pour donner le "pourquoi" en un coup d'œil. Zéro invention : si
# aucun critère ne contribue, pas de raison affichée.
# ---------------------------------------------------------------------------


def _top_driver(r: "ActifResult", h: str) -> Tuple[str, str]:
    """Critère à plus forte |contribution| pour (actif, horizon).

    Retourne `(cle_courante, nom)` — `cle_courante` pour identifier le driver
    (regroupement par clé, jamais par nom — L023) et `nom` pour l'affichage.
    Source UNIQUE : `contributions[h]` (mêmes données que `_top_explication` et
    le tableau « Détail par actif »). Exclut gates et critères n/a. Départage
    déterministe des ex æquo par nom. Retourne `("", "")` si aucun contributeur.
    """
    best: Tuple[float, str] = (0.0, "")  # (|c|, nom) pour le tri ex æquo stable
    best_cle = ""
    best_nom = ""
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        ctr = c.contributions.get(h)
        if ctr is None or abs(ctr) <= 0.0:
            continue
        key = (abs(ctr), c.nom)
        if key > best:
            best = key
            best_cle = getattr(c, "cle_courante", "") or ""
            best_nom = _nom_critere(c)  # libellé dynamique (net IA vs thème)
    return best_cle, best_nom


def _critere_dominant(r: "ActifResult", h: str) -> str:
    """Nom du critère à plus forte |contribution| pour (actif, horizon).

    Exclut gates et critères n/a. Retourne "" si aucun contributeur réel.
    """
    return _top_driver(r, h)[1]


def detect_mono_critere_dominant(
    r: "ActifResult", h: str
) -> Tuple[bool, Optional[str]]:
    """K1 (SHADOW, decision-log only) — détecte si UN SEUL critère fournit plus de
    `MONO_CRITERE_RATIO` (50%) du |score| de la cellule.

    Base : somme des |contributions| des critères non-gate / non-na sur l'horizon.
    Si la plus forte |contribution| dépasse MONO_CRITERE_RATIO × Σ|contributions|,
    la cellule est dominée par un seul critère.

    Retourne (is_mono, nom_critere|None). NE MODIFIE PAS la conclusion (mesure only).
    Si la somme est nulle (aucun contributeur), retourne (False, None).
    """
    best_nom: Optional[str] = None
    best_abs = 0.0
    somme_abs = 0.0
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        ctr = c.contributions.get(h)
        if ctr is None:
            continue
        a = abs(ctr)
        somme_abs += a
        if a > best_abs:
            best_abs = a
            best_nom = _nom_critere(c)  # libellé dynamique (net IA vs thème)
    if somme_abs <= 0.0 or best_nom is None:
        return False, None
    if best_abs > MONO_CRITERE_RATIO * somme_abs:
        return True, best_nom
    return False, None


def build_top3_block(results: List["ActifResult"]) -> List[str]:
    """Construit le bloc '## 🎯 Top 3 convictions du jour'.

    Ne retient que les cellules à confidence "normale" (couverture saine) et
    non quasi coin-flip. Q1 (audit trio 03/06) — Top 3 = 3 actifs DISTINCTS :
    on garde au plus UNE cellule par actif (le meilleur horizon par |note|), puis
    on prend les 3 actifs distincts au plus fort |note|. Évite le « Pétrole,
    Pétrole, Pétrole » (3 horizons du même actif).
    """
    candidates: List[Tuple[float, str, float, str, str]] = []
    # (abs_note, label "actif h", note_signed, direction, raison)
    for r in results:
        for h in HORIZONS:
            conc = r.conclusions.get(h, "")
            if conc not in ("LONG", "SHORT"):
                continue  # exclut INSUFFISANT
            confidence = r.confidence.get(h, "normale")
            if confidence != "normale":
                continue  # exclut conf faible
            if r.is_carry.get(h, False) or r.is_news_regime.get(h, False):
                continue  # exclut carry / régime news
            score = r.scores.get(h, 0.0)
            if abs(score) < 0.05:
                continue  # exclut quasi coin-flip
            raison = _critere_dominant(r, h)
            candidates.append((abs(score), f"{r.nom} {h}", score, conc, raison))
    # Q1 — dédup par ACTIF : on ne garde que le meilleur horizon (|note| max) de
    # chaque actif. Le nom de l'actif est le label avant le dernier espace.
    candidates.sort(key=lambda x: x[0], reverse=True)
    best_par_actif: Dict[str, Tuple[float, str, float, str, str]] = {}
    for cand in candidates:
        actif_nom = cand[1].rsplit(" ", 1)[0]
        if actif_nom not in best_par_actif:
            # candidates déjà trié desc → le premier vu = meilleur horizon de l'actif.
            best_par_actif[actif_nom] = cand
    distincts = sorted(best_par_actif.values(), key=lambda x: x[0], reverse=True)

    lines: List[str] = ["## 🎯 Top 3 convictions du jour", ""]
    if not distincts:
        lines.append("_Aucune conviction à couverture suffisante ce cycle._")
        lines.append("")
        return lines
    for _abs, label, score, direction, raison in distincts[:3]:
        suffix = f" — {raison}" if raison else ""
        lines.append(f"- **{label} — {direction} ({score:+.2f})**{suffix}")
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# « 🎯 À jouer aujourd'hui (24h) » — vue d'oiseau actionnable en tête (audit
# UX 2026-06-10, casquette DÉCIDER). PRÉSENTATION PURE : aucun score, aucune
# conclusion, aucune mesure ne change. Le tableau ne fait que RÉ-ORGANISER ce
# que la matrice contient déjà, en se restreignant à l'horizon 24h (l'horizon
# de trade préféré de Thomas) et en séparant ce qui est jouable de ce qui ne
# l'est pas — selon des critères EXISTANTS (⚪ / ≈ / 🚫 / conviction bilan_jour).
# ---------------------------------------------------------------------------


def _max_weight_critere_is_na(r: "ActifResult") -> bool:
    """True si le critère NON-GATE de poids maximal de la fiche est absent (n/a).

    Sert au garde-fou conviction (16/06) : un actif dont le driver de poids le
    plus fort manque ne peut pas porter une conviction « forte » à couverture
    insuffisante. Les gates (sans poids numérique) et les critères présents sont
    ignorés du test. Aucun critère non-gate → False (rien à invalider).
    """
    non_gate = [c for c in r.criteres if not c.is_gate]
    if not non_gate:
        return False
    poids_max = max(abs(c.poids) for c in non_gate)
    # Le(s) critère(s) à poids max : n/a si TOUS les porteurs du poids max sont absents.
    porteurs_max = [c for c in non_gate if abs(c.poids) == poids_max]
    return all(c.is_na for c in porteurs_max)


def _conviction_cell(r: "ActifResult", h: str, seuil: float) -> str:
    """Libellé EXPLICITE de conviction d'une cellule (audit UX 2026-06-11 :
    « forte »/« faible » binaire illisible — « faible » sur un score de 13 semble
    absurde). La LOGIQUE est INCHANGÉE (mêmes conditions, mêmes seuils que
    `bilan_jour.conviction_level` §4.7) : seul le LIBELLÉ d'affichage change.

    Mapping des conditions (toutes calculées comme avant) :
      - aucune condition dégradante + |score| >= seuil → « forte »
      - |score| < NEUTRAL_BAND (≈/⚪)                  → « molle (score faible) »
      - divergence quant↔news (↯)                      → « contestée (news à contre-sens) »
      - mono-critère dominant (◧)                      → « fragile (1 seul critère) »
      - incohérence inter-horizons (⇆)                 → « zigzag horizons »
      - INSUFFISANT                                    → « — »

    Priorité si plusieurs conditions actives (la plus disqualifiante d'abord) :
      molle > contestée > fragile > zigzag. On n'affiche QUE la première — les
      drapeaux restants demeurent visibles dans la colonne « Drapeaux ».
    """
    conc = r.conclusions.get(h, "")
    if conc not in ("LONG", "SHORT"):
        return "—"
    score = abs(r.scores.get(h, 0.0))
    mono_dom, _ = detect_mono_critere_dominant(r, h)
    # Conditions EXISTANTES, ordre de priorité d'affichage (n'altère ni seuils ni logique).
    if score < NEUTRAL_BAND:  # quasi_neutre (englobe coin-flip |score|<0.05)
        return "molle (score faible)"
    if r.divergence_quant_news.get(h, False):
        return "contestée (news à contre-sens)"
    if mono_dom:
        return "fragile (1 seul critère)"
    if r.incoherence_inter_horizons:
        return "zigzag horizons"
    # GARDE-FOU « confiant ET aveugle » (Thomas 16/06) : pas de « forte » si la
    # couverture est insuffisante (< CONVICTION_COVERAGE_MIN) ET que le critère
    # de poids MAX de la fiche est n/a. La direction reste notée (LONG/SHORT) ;
    # seule la conviction est dégradée. Inséré AVANT le palier « forte » pour le
    # court-circuiter ; n'affecte ni le score ni la conclusion (libellé only).
    if (
        score >= seuil
        and r.coverage < CONVICTION_COVERAGE_MIN
        and _max_weight_critere_is_na(r)
    ):
        return "fragile (couverture insuffisante)"
    if score >= seuil:
        return "forte"
    # |score| entre NEUTRAL_BAND et seuil, sans drapeau : ancien « faible »
    # (ni assez fort, ni dégradé) → on le qualifie de « molle (score faible) »
    # (même famille que le quasi-neutre : la note ne porte pas la conviction).
    return "molle (score faible)"


def _cell_a_eviter(r: "ActifResult", h: str) -> bool:
    """Une cellule 24h est « à éviter » si elle porte un drapeau de NON-jouabilité
    EXISTANT : 🚫 insuffisant OU ⚪ quasi coin-flip (|score|<0.05) OU ≈ quasi-neutre
    (|note|<NEUTRAL_BAND). Les drapeaux de prudence (◧/⚠️/↯/⇄/⇆/⌛/⊘) ne SORTENT PAS
    une cellule des « jouables » (prudence ≠ exclusion).
    """
    conc = r.conclusions.get(h, "")
    if conc == CONCLUSION_INSUFFISANT:
        return True
    score = abs(r.scores.get(h, 0.0))
    return score < NEUTRAL_BAND  # ⚪ (<0.05) et ≈ (<0.30) sont tous deux <NEUTRAL_BAND


def build_a_jouer_block(
    results: List["ActifResult"],
    now: datetime,
    prix_reference: Optional[Dict[str, float]] = None,
    seuil_conviction: Optional[float] = None,
) -> List[str]:
    """Construit le bloc « ## 🎯 À jouer aujourd'hui (24h) ».

    Tableau des 12 cellules 24h, trié par |note| décroissante, scindé en deux
    groupes : « Jouables » et « À éviter » (cf. `_cell_a_eviter`). Colonnes :
    Actif · Direction · Note · Conviction · Drapeaux · Prix de réf.

    `prix_reference` : dict {fiche_key: prix} (prix d'émission stampé). Absent
    → « — » (zéro invention, jamais de prix fabriqué).
    `seuil_conviction` : seuil EXISTANT (bilan_jour) ; chargé si None.
    """
    if seuil_conviction is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import bilan_jour as _bj  # import paresseux (isole d'un éventuel KO)
            seuil_conviction = _bj._load_score_fort_seuil()
        except Exception:  # noqa: BLE001 — défaut documenté si bilan_jour KO
            seuil_conviction = 0.6
    prix_reference = prix_reference or {}

    H = "24h"
    # Tampon par ligne : on calcule les champs AVANT de poser la colonne « Porté
    # par » car le marqueur ⚭ dépend des autres lignes (driver partagé) DU MÊME
    # tableau (Jouables / À éviter sont traités séparément). cle/nom du driver
    # viennent de _top_driver (même source que _top_explication — factorisé).
    Row = Tuple[float, bool, str, str, str, str, str, str, str]
    # (|note|, a_eviter, actif, direction, note_str, conv, flags_str, px_str,
    #  driver_nom) + driver_cle stocké à part pour le regroupement.
    buf: List[Tuple[float, bool, Dict[str, str]]] = []
    for r in results:
        conc = r.conclusions.get(H, "")
        score = r.scores.get(H, 0.0)
        flags = _compute_cell_risk_flags(r, H, now)
        # ⚪ / ≈ ne sont PAS dans _compute_cell_risk_flags → on les ajoute pour
        # rendre la non-jouabilité visible dans la colonne Drapeaux (cohérent
        # avec la matrice : ⚪ |score|<0.05, ≈ |score|<NEUTRAL_BAND).
        extra: List[str] = []
        if conc in ("LONG", "SHORT"):
            if abs(score) < 0.05:
                extra.append("⚪")
            elif abs(score) < NEUTRAL_BAND:
                extra.append("≈")
        flags_all = extra + flags
        flags_str = " ".join(flags_all) if flags_all else "—"

        direction = conc if conc in ("LONG", "SHORT") else conc
        note_str = "—" if conc == CONCLUSION_INSUFFISANT else f"{score:+.2f}"
        conv = _conviction_cell(r, H, seuil_conviction)
        px = prix_reference.get(r.fiche_key)
        px_str = f"{px:g}" if isinstance(px, (int, float)) else "—"
        driver_cle, driver_nom = _top_driver(r, H)

        buf.append((abs(score), _cell_a_eviter(r, H), {
            "actif": r.nom,
            "direction": direction,
            "note_str": note_str,
            "conv": conv,
            "flags_str": flags_str,
            "px_str": px_str,
            "driver_cle": driver_cle,
            "driver_nom": driver_nom,
            # P3 — « Porté par » enrichi : nom complet + valeur + sens + contrib.
            "driver_detail": _driver_detail(r, H),
        }))

    # Tri |note| décroissant, déterministe (l'actif départage les ex æquo).
    buf.sort(key=lambda t: (-t[0], t[2]["actif"]))
    jouables_cells = [d for _a, evit, d in buf if not evit]
    a_eviter_cells = [d for _a, evit, d in buf if evit]

    def _shared_groups(cells: List[Dict[str, str]]) -> Dict[Tuple[str, str], int]:
        # Compte par (driver_cle, direction) — regroupement par cle_courante
        # (L023, jamais par nom), MÊME direction uniquement (pas LONG vs SHORT).
        from collections import Counter
        counts: Counter = Counter()
        for d in cells:
            cle = d["driver_cle"]
            if cle and d["direction"] in ("LONG", "SHORT"):
                counts[(cle, d["direction"])] += 1
        return {k: n for k, n in counts.items() if n >= 2}

    def _render_table(cells: List[Dict[str, str]], shared: Dict[Tuple[str, str], int]) -> List[str]:
        lines: List[str] = []
        if not cells:
            lines.append("| _aucune_ | — | — | — | — | — | — |")
            return lines
        for d in cells:
            cle, nom = d["driver_cle"], d["driver_nom"]
            detail = d.get("driver_detail") or "—"
            if not nom:
                porte = "—"
            else:
                marker = ""
                if cle and (cle, d["direction"]) in shared:
                    marker = SHARED_DRIVERS_SYMBOL_LOCAL + " "
                # P3 — nom COMPLET non tronqué + valeur + sens + contribution.
                porte = marker + detail
            lines.append(
                f"| {d['actif']} | {d['direction']} | {d['note_str']} | "
                f"{d['conv']} | {d['flags_str']} | {porte} | {d['px_str']} |"
            )
        return lines

    jouables_shared = _shared_groups(jouables_cells)

    out: List[str] = ["## 🎯 À jouer aujourd'hui (24h)", ""]
    # P4 — la pédagogie (Conviction, À éviter, « Porté par », ⚭) est désormais
    # expliquée UNE SEULE fois dans « ## Comment lire les scores » (fin de
    # bulletin). Ici, la section ne garde que son titre + tableaux.
    header = "| Actif | Direction | Note | Conviction | Drapeaux | Porté par | Prix de réf. |"
    sep = "|---|---|---|---|---|---|---|"
    # [H-B1 audit visuel 12/06] : guider l'œil dans « Jouables » — séparer les
    # convictions FORTES (le pari net) des autres lignes jouables (prudence). Au
    # sein des fortes, celles SANS drapeau (les plus propres) d'abord, puis celles
    # AVEC drapeau(s). Le tri |note| desc EST préservé à l'intérieur de chaque
    # sous-groupe (buf est déjà trié). Zéro changement de scoring/sélection.
    def _is_forte(d: Dict[str, str]) -> bool:
        return d.get("conv", "") == "forte"

    def _has_flag(d: Dict[str, str]) -> bool:
        return d.get("flags_str", "—") not in ("", "—")

    forte_clean = [d for d in jouables_cells if _is_forte(d) and not _has_flag(d)]
    forte_flagged = [d for d in jouables_cells if _is_forte(d) and _has_flag(d)]
    autres_jouables = [d for d in jouables_cells if not _is_forte(d)]

    out.append("**Jouables**")
    out.append("")
    if forte_clean:
        out.append("_Conviction forte — sans drapeau_")
        out.append("")
        out.append(header)
        out.append(sep)
        out.extend(_render_table(forte_clean, jouables_shared))
        out.append("")
    if forte_flagged:
        out.append("_Conviction forte — avec drapeau(s) (prudence)_")
        out.append("")
        out.append(header)
        out.append(sep)
        out.extend(_render_table(forte_flagged, jouables_shared))
        out.append("")
    # Les autres lignes jouables (conviction non-forte mais ni ⚪ ni ≈ ni 🚫).
    if autres_jouables:
        out.append("_Autres lignes jouables_")
        out.append("")
        out.append(header)
        out.append(sep)
        out.extend(_render_table(autres_jouables, jouables_shared))
        out.append("")
    # Si rien dans aucun sous-groupe (cas dégénéré) : tableau vide explicite.
    if not (forte_clean or forte_flagged or autres_jouables):
        out.append(header)
        out.append(sep)
        out.extend(_render_table([], jouables_shared))
        out.append("")
    # Synthèse des paris partagés (une ligne par groupe ⚭ de même cle+direction).
    synth = _synthese_paris_partages(jouables_cells, jouables_shared)
    if synth:
        out.extend(synth)
        out.append("")
    out.append("**À éviter** (⚪ coin-flip · ≈ quasi-neutre · 🚫 insuffisant)")
    out.append("")
    out.append(header)
    out.append(sep)
    out.extend(_render_table(a_eviter_cells, _shared_groups(a_eviter_cells)))
    out.append("")
    return out


# ---------------------------------------------------------------------------
# « 🎯 Sélection du jour — max 3 » (décision fondateur 12/06 : « 2-3 bons paris
# par jour, pas 12 »). ZÉRO CUTOVER : aucun score, aucune conclusion, aucune
# mesure de signal ne change. Bloc d'AFFICHAGE + champ de MESURE (decision-log)
# qui RESTREINT la vue 24h aux paris les plus convaincants selon des conditions
# EXISTANTES (conviction « forte », coverage, top-driver). S'abstenir (aucune
# sélection) est une réponse valide — on ne force jamais 3 lignes.
# ---------------------------------------------------------------------------

# Seuil de couverture MINIMAL pour entrer dans la « Sélection du jour ». C'est un
# seuil d'AFFICHAGE/SÉLECTION (pas un seuil de scoring/conclusion) : il ne touche
# AUCUN score ni conclusion (les cellules sous 0.70 restent jouables ailleurs).
# Valeur fixée par la décision fondateur du 12/06 (≥ 0.70 = couverture franche).
SELECTION_COVERAGE_MIN: float = 0.70
# Nombre maximal de paris retenus par la sélection du jour (décision fondateur).
SELECTION_MAX: int = 3

# Note discrète (fin de section « À jouer ») signalant que les capteurs courts
# shadow tournent (Étage 2) — pour que Thomas sache qu'ils sont tracés au
# decision-log SANS effet sur les notes. Promotion éventuelle : ticket C (~23/06).
_SHADOW_CAPTEURS_NOTE: List[str] = [
    "_Capteurs courts (shadow, sans effet sur les notes) : retour veille / gap "
    "overnight tracés au decision-log._",
    "",
]


def compute_selection_du_jour(
    results: List["ActifResult"],
    seuil_conviction: Optional[float] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Calcule la « Sélection du jour — max 3 » sur l'horizon 24h.

    Source de vérité UNIQUE partagée par le bloc bulletin (1a) ET le decision-log
    (1b) : zéro divergence possible entre ce qui est AFFICHÉ et ce qui est MESURÉ.

    Les 4 règles (toutes réutilisent l'existant, zéro nouveau seuil métier hors le
    plancher d'affichage SELECTION_COVERAGE_MIN) :
      1. conviction « forte » (`_conviction_cell` == "forte") ;
      2. coverage ≥ SELECTION_COVERAGE_MIN (champ `coverage` existant de l'actif) ;
      3. un seul pari par FAMILLE macro : si plusieurs candidates partagent la
         même (`famille_macro` du top-driver, direction), on garde LA plus forte
         |note| et on écarte les autres (motif tracé). La dédup raisonne par
         famille macro (TIPS et écart 2Y US-DE = même complexe taux/dollar = un
         seul pari) et NON par critère littéral (réf. brief 12/06, défaut 11/06) ;
      4. max SELECTION_MAX lignes, tri |note| décroissant.

    Retourne (selection, ecartees) :
      - selection : liste de dicts {fiche_key, actif, direction, note, driver_cle,
        driver_nom, coverage} — au plus SELECTION_MAX, triée |note| desc.
      - ecartees  : liste de dicts {fiche_key, actif, motif} pour les candidates
        passant (1) et (2) mais écartées par (3) la dédup famille ou (4) le cap.
        `motif` = « même pari (<famille>) que <Actif> » (dédup) ou « hors top 3 »
        (cap), où <famille> est le label trader de la famille macro partagée.
    NE MODIFIE NI score NI conclusion (lecture seule sur `results`).
    """
    if seuil_conviction is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import bilan_jour as _bj  # import paresseux (isole d'un éventuel KO)
            seuil_conviction = _bj._load_score_fort_seuil()
        except Exception:  # noqa: BLE001 — défaut documenté si bilan_jour KO
            seuil_conviction = 0.6

    H = "24h"
    # Étape 1+2 : candidates = cellules 24h conviction « forte » ET coverage OK.
    candidates: List[Dict[str, Any]] = []
    for r in results:
        conc = r.conclusions.get(H, "")
        if conc not in ("LONG", "SHORT"):
            continue
        if _conviction_cell(r, H, seuil_conviction) != "forte":
            continue
        if r.coverage < SELECTION_COVERAGE_MIN:
            continue
        driver_cle, driver_nom = _top_driver(r, H)
        candidates.append({
            "fiche_key": r.fiche_key,
            "actif": r.nom,
            "direction": conc,
            "note": r.scores.get(H, 0.0),
            "driver_cle": driver_cle,
            "driver_nom": driver_nom,
            # P3 — « Porté par » enrichi (nom complet + valeur + sens + contrib).
            "driver_detail": _driver_detail(r, H),
            "coverage": r.coverage,
        })

    # Tri |note| décroissant, déterministe (actif départage les ex æquo).
    candidates.sort(key=lambda d: (-abs(d["note"]), d["actif"]))

    # Étape 3 : dédup par (FAMILLE macro, direction) — un seul pari par famille.
    # La première candidate vue (|note| max) gagne ; les suivantes de même famille
    # ET même direction sont écartées. La famille macro regroupe les critères qui
    # sont LE MÊME pari (TIPS + écart 2Y US-DE = complexe taux/dollar) ; une clé
    # inconnue retombe en famille SINGLETON (= la clé), donc pas de regroupement
    # abusif. Dédup UNIQUEMENT si le driver est connu (cle non vide) : sans driver
    # identifiable, on ne peut pas affirmer « même pari » (zéro invention).
    import shared_drivers as _shared_drivers  # lazy, cf. pattern existant
    selection: List[Dict[str, Any]] = []
    ecartees: List[Dict[str, Any]] = []
    gagnant_par_famille: Dict[Tuple[str, str], Tuple[str, str]] = {}
    for c in candidates:
        cle = c["driver_cle"]
        if cle:
            famille, label = _shared_drivers.famille_macro(cle, c["fiche_key"])
            groupe = (famille, c["direction"])
        else:
            famille, label, groupe = "", "", None
        if groupe is not None and groupe in gagnant_par_famille:
            gagnant_actif, gagnant_label = gagnant_par_famille[groupe]
            motif = f"même pari ({gagnant_label}) que {gagnant_actif}"
            ecartees.append({
                "fiche_key": c["fiche_key"],
                "actif": c["actif"],
                "motif": motif,
            })
            continue
        if groupe is not None:
            gagnant_par_famille[groupe] = (c["actif"], label)
        selection.append(c)

    # Étape 4 : cap max SELECTION_MAX (les surnuméraires sont « hors top 3 »).
    retenues = selection[:SELECTION_MAX]
    for c in selection[SELECTION_MAX:]:
        ecartees.append({
            "fiche_key": c["fiche_key"],
            "actif": c["actif"],
            "motif": "hors top 3",
        })
    return retenues, ecartees


def _catalyseurs_j0_high(now: datetime) -> List[Dict[str, Any]]:
    """Événements à impact `high` du calendrier tombant AUJOURD'HUI (J0).

    Import TOLÉRANT (calendrier_eco peut être absent/KO → liste vide, zéro
    invention). `evenements_a_venir` démarre à J+1, donc on relit J0 via le même
    module (charger_evenements + _dates_pour_event) — réutilisation, pas de
    nouvelle source. Retourne [{nom, actifs:[...], impact}] pour les seuls events
    d'impact « high » qui tombent le jour `now` (Europe/Paris).
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import calendrier_eco as _cal  # import paresseux/tolérant
    except Exception:  # noqa: BLE001 — calendrier indispo → pas d'avertissement
        return []
    try:
        jour = now.date()
        out: List[Dict[str, Any]] = []
        for ev in _cal.charger_evenements():
            if str(ev.get("impact") or "medium").strip().lower() != "high":
                continue
            if _cal._dates_pour_event(ev, jour, jour):
                out.append({
                    "nom": str(ev.get("nom") or ev.get("type") or "Événement"),
                    "actifs": [str(a) for a in (ev.get("actifs") or [])],
                    "impact": "high",
                })
        return out
    except Exception:  # noqa: BLE001 — toute anomalie calendrier → silencieux
        return []


# ---------------------------------------------------------------------------
# Étage 2 — Capteurs courts 24h en SHADOW (decision-log only, poids 0).
# ---------------------------------------------------------------------------
# Ces deux capteurs n'entrent PAS dans le score (observabilité pure). Ils sont
# tracés au decision-log pour le ticket C (~23/06) qui décidera de leur promotion
# en VRAIS critères. Zéro invention : toute donnée manquante → None.
#   - shadow_retour_j1   : close J-1 / close J-2 − 1 (rendement de la veille).
#   - shadow_gap_overnight : prix d'émission 7h / close J-1 − 1 (gap overnight).
# Source closes : fetch_twelve_series (déjà utilisé par les critères). Prix
# d'émission : stamp 7h existant (même source que « Prix de réf. »).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Chantier ③ (16/06, Thomas) — DÉTECTEUR « CHOC D'OFFRE » CACAO en SHADOW.
# ---------------------------------------------------------------------------
# PROBLÈME résolu : le 16/06 le marché price un CHOC D'OFFRE cacao (El Niño /
# récolte 2026-27 sous la normale / cherelles / maladies) = HAUSSIER, mais la
# SYNTHÈSE NET DeepSeek a renvoyé baissier (bruit de demande dominant) → le vrai
# signal d'offre a été NOYÉ. Ce détecteur capte SÉPARÉMENT le récit d'OFFRE
# PROSPECTIVE haussier, pour qu'il ne soit plus dilué dans le net.
#
# POURQUOI SHADOW (poids 0, L015) — IMPÉRATIF :
#   (a) ÉVITER LE DOUBLE-AMORTISSEMENT (L013) : la synthèse net IA (slot
#       maladies_cabosses + eudr) PORTE DÉJÀ une partie du signal offre. Activer
#       ce détecteur EN PLUS, sans décider comment il REMPLACE ou COMPLÈTE le
#       net, double-compterait le même récit. Il faut d'abord trancher la
#       méthodo (cf. point ouvert handoff) AVANT de câbler une contribution.
#   (b) CALIBRER SUR DU RÉEL (mesurer avant d'agir) : on observe d'abord la
#       FRÉQUENCE et la JUSTESSE du détecteur au decision-log avant de lui
#       donner un poids. Le bulletin reste INCHANGÉ (test-verrou conclusions).
#
# CRITÈRE D'ACTIVATION FUTUR (sur preuve, à valider Thomas) : promouvoir en
# critère pondéré seulement si, sur ≥ N cycles où shadow_choc_offre.detected,
# la direction HAUSSIER offre a un meilleur win-rate cacao que la synthèse net
# seule — ET après décision méthodo de remplacement/complément (anti-L013).
#
# ZÉRO INVENTION : events-log absent / aucune news offre → detected=False,
# would_be_contrib=0.0, conclusion inchangée.

# Mots-clés OFFRE HAUSSIÈRE cacao (offre↓ = prix↑). Réutilise/étend les
# long_keywords du triplet maladies_cabosses_cacao + le récit prospectif raté
# le 16/06 (météo/El Niño/récolte/cherelles/ICCO). En minuscules, match substr.
SHADOW_CHOC_OFFRE_CACAO_KEYWORDS: Tuple[str, ...] = (
    "el nino", "el niño", "el-nino",
    "drought west africa", "sécheresse", "harmattan",
    "poor harvest", "récolte sous", "crop shortfall", "below average crop",
    "cherelle", "cherelles", "flower failure",
    "black pod", "swollen shoot", "pod borer", "cocoa disease", "maladie cacao",
    "cocoa deficit", "supply deficit", "icco deficit", "production deficit",
    "supply shock", "choc d'offre", "tight supply cocoa",
)
# Mots-clés de DÉMENTI / détente (annulent un signal offre haussier).
SHADOW_CHOC_OFFRE_CACAO_NEGATORS: Tuple[str, ...] = (
    "good harvest", "bumper crop", "récolte saine", "healthy cocoa harvest",
    "surplus", "outbreak contained", "favorable weather", "rain returns",
)


def compute_shadow_choc_offre_cacao(
    events: Optional[List[dict]] = None,
    now: Optional[datetime] = None,
    lookback_jours: int = 30,
) -> Dict[str, Any]:
    """Détecteur SHADOW (poids 0) du récit de CHOC D'OFFRE cacao haussier.

    Scanne les events récents (≤ lookback_jours) pour des mots-clés d'OFFRE
    PROSPECTIVE haussière (météo/El Niño/récolte/maladie/déficit), DÉCOUPLÉ de
    la synthèse net DeepSeek. Retourne un dict tracé tel quel au decision-log :

      {"detected": bool,            # ≥1 event offre haussier net (après démentis)
       "direction": +1|0,          # +1 = offre↓ haussier ; 0 si rien/neutralisé
       "n_events": int,            # nb d'events offre haussiers retenus
       "negators": int,            # nb d'events de démenti/détente vus
       "keywords": List[str],      # mots-clés déclencheurs (dédupliqués, ≤8)
       "would_be_contrib": float}  # contribution SI activé (poids 0 → 0.0 ici)

    `would_be_contrib` est laissé à 0.0 (poids 0, shadow) : la contribution
    réelle ne sera fixée qu'à l'activation, après décision méthodo anti-L013.
    Zéro invention : events None/vides → detected=False, direction=0.
    """
    now = now or datetime.now(timezone.utc)
    if events is None:
        try:
            import triggers_classifier as _tc  # lazy, cohérent avec le module
            events = _tc.parse_events_log()
        except Exception:  # noqa: BLE001 — events indispo → shadow vide (zéro invention)
            events = []
    hits: List[str] = []
    negators = 0
    for ev in events or []:
        try:
            dt = ev.get("_canonical_dt") or ev.get("_dt")
            if isinstance(dt, datetime):
                age = (now - dt).total_seconds() / 86400.0
                if age > lookback_jours or age < -2:  # tolère léger futur (cf. C9)
                    continue
            blob = " ".join(
                str(ev.get(k, "") or "") for k in ("L1", "L2", "trigger", "cours", "news_zone")
            ).lower()
            if not blob.strip():
                continue
            # Ne scanne que les events à pertinence cacao (cours/zone) pour éviter
            # qu'un « el nino » café/sucre pollue le détecteur cacao.
            is_cacao = ("cocoa" in blob or "cacao" in blob
                        or "ci" in str(ev.get("news_zone", "")).lower()
                        or "gh" in str(ev.get("news_zone", "")).lower())
            if not is_cacao:
                continue
            if any(neg in blob for neg in SHADOW_CHOC_OFFRE_CACAO_NEGATORS):
                negators += 1
                continue
            for kw in SHADOW_CHOC_OFFRE_CACAO_KEYWORDS:
                if kw in blob and kw not in hits:
                    hits.append(kw)
        except Exception:  # noqa: BLE001 — un event malformé ne casse pas le scan
            continue
    detected = len(hits) > 0
    return {
        "detected": detected,
        "direction": 1 if detected else 0,
        "n_events": len(hits),
        "negators": negators,
        "keywords": hits[:8],
        "would_be_contrib": 0.0,  # SHADOW poids 0 — aucune contribution au score
    }


def compute_shadow_capteurs(
    fiches: Dict[str, dict],
    prix_emission: Optional[Dict[str, float]] = None,
    fetch_series: Optional[Any] = None,
) -> Dict[str, Dict[str, Optional[float]]]:
    """Calcule les capteurs courts shadow par fiche_key.

    Retourne {fiche_key: {"shadow_retour_j1": float|None,
                          "shadow_gap_overnight": float|None}}.

    `prix_emission` : {ticker: prix} du stamp 7h (load_prix_emission). Absent →
    gap overnight None (zéro invention).
    `fetch_series` : callable(symbol) -> [(dt, close)] oldest→newest (par défaut
    criteres_calculator.fetch_twelve_series). Absent/KO → retour_j1 None.

    Best-effort intégral : aucune exception ne remonte (run bulletin protégé).
    """
    prix_emission = prix_emission or {}
    if fetch_series is None:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import criteres_calculator as _cc  # import paresseux/tolérant
            fetch_series = _cc.fetch_twelve_series
        except Exception:  # noqa: BLE001 — pas de fetcher → tout None
            fetch_series = None

    out: Dict[str, Dict[str, Optional[float]]] = {}
    for key, fiche in (fiches or {}).items():
        ticker = fiche.get("ticker_principal")
        retour_j1: Optional[float] = None
        gap_overnight: Optional[float] = None
        close_j1: Optional[float] = None
        close_j2: Optional[float] = None
        if ticker and fetch_series is not None:
            try:
                serie = fetch_series(ticker, outputsize=10)
            except Exception:  # noqa: BLE001 — fetch KO → capteurs None
                serie = None
            if serie and len(serie) >= 1:
                # Série triée oldest→newest : [-1] = close J-1, [-2] = close J-2.
                close_j1 = serie[-1][1]
                if len(serie) >= 2:
                    close_j2 = serie[-2][1]
        # shadow_retour_j1 = close J-1 / close J-2 − 1 (None si l'un manque/≤0).
        if (isinstance(close_j1, (int, float)) and isinstance(close_j2, (int, float))
                and close_j2 not in (0, 0.0)):
            retour_j1 = round(close_j1 / close_j2 - 1.0, 6)
        # shadow_gap_overnight = prix émission 7h / close J-1 − 1 (None si manque).
        px_emission = prix_emission.get(ticker) if ticker else None
        if (isinstance(px_emission, (int, float))
                and isinstance(close_j1, (int, float)) and close_j1 not in (0, 0.0)):
            gap_overnight = round(px_emission / close_j1 - 1.0, 6)
        out[key] = {
            "shadow_retour_j1": retour_j1,
            "shadow_gap_overnight": gap_overnight,
        }
    return out


# VOLET B (2026-06-15) — seuil de matérialité du mouvement « depuis la dernière
# clôture vue par le système » au-delà duquel on lève un drapeau ⚠️ sur un actif
# continu sélectionné. 0.8 % (0.008) = mouvement intraday/overnight non
# négligeable pour un actif macro. En-dessous (ou ~0), on n'affiche RIEN (anti-
# bruit). Le drapeau n'est levé que si le mouvement est de SENS OPPOSÉ à la
# conclusion (le système décide peut-être sur une donnée dépassée).
_GAP_CONTRESENS_SEUIL: float = 0.008


def _is_continu_fiche(fiche_key: str, fiches: Optional[Dict[str, dict]]) -> bool:
    """True si l'actif `fiche_key` est du groupe CONTINU (or, argent, pétrole,
    cuivre, cacao, café, blé, FX). Réutilise mesure_ouverture.actif_group (source
    de vérité). Best-effort : indispo / fiche absente → False (pas de drapeau)."""
    if not fiches or fiche_key not in fiches:
        return False
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import mesure_ouverture as _mo  # noqa: E402
        return _mo.actif_group(fiches[fiche_key]) == "continu"
    except Exception:  # noqa: BLE001
        return False


def _build_gap_contresens_flags(
    selection: List[Dict[str, Any]],
    shadow_capteurs: Optional[Dict[str, Dict[str, Optional[float]]]],
    fiches: Optional[Dict[str, dict]],
) -> List[str]:
    """VOLET B — drapeaux ⚠️ « bouge à contre-sens depuis la dernière clôture vue ».

    Pour chaque actif CONTINU de la sélection : si son `shadow_gap_overnight`
    (mouvement prix-courant / close J-1 utilisé par le système) est ≥ seuil de
    matérialité ET de SENS OPPOSÉ à la conclusion (LONG alors que ça baisse, ou
    SHORT alors que ça monte), on lève un drapeau. But : le bulletin DIT quand il
    décide sur une donnée potentiellement dépassée.

    Dégradation sûre (zéro bruit, zéro invention) :
      - pas de shadow_capteurs / gap None / |gap| < seuil → RIEN ;
      - actif non continu → jamais de drapeau (close J-1 = dernier prix réel) ;
      - gap ALIGNÉ avec la conclusion → RIEN (le système voit déjà dans le bon sens).
    """
    if not shadow_capteurs:
        return []
    out: List[str] = []
    for s in selection:
        key = s["fiche_key"]
        if not _is_continu_fiche(key, fiches):
            continue
        cap = shadow_capteurs.get(key) or {}
        gap = cap.get("shadow_gap_overnight")
        if not isinstance(gap, (int, float)):
            continue
        if abs(gap) < _GAP_CONTRESENS_SEUIL:
            continue
        direction = s["direction"]
        # Contre-sens : LONG mais gap < 0 (ça baisse) ; SHORT mais gap > 0 (ça monte).
        contresens = (direction == "LONG" and gap < 0) or (direction == "SHORT" and gap > 0)
        if not contresens:
            continue
        out.append(
            f"⚠️ **{s['actif']}** bouge à contre-sens depuis la dernière clôture "
            f"vue par le système ({gap:+.1%}) — le pari {direction} repose "
            f"peut-être sur un prix déjà dépassé."
        )
    if out:
        out.append("")
    return out


def build_selection_du_jour_block(
    results: List["ActifResult"],
    now: datetime,
    prix_reference: Optional[Dict[str, float]] = None,
    seuil_conviction: Optional[float] = None,
    shadow_capteurs: Optional[Dict[str, Dict[str, Optional[float]]]] = None,
    fiches: Optional[Dict[str, dict]] = None,
) -> List[str]:
    """Construit le bloc « ## 🎯 Sélection du jour — max 3 » (placé EN PREMIER,
    avant « À jouer aujourd'hui »).

    Affiche au plus SELECTION_MAX paris 24h (cf. `compute_selection_du_jour`).
    Sous le tableau : avertissement ⚠️ si un catalyseur `high` du calendrier (J0)
    concerne un actif sélectionné. Si aucune cellule ne passe → message
    d'abstention (s'abstenir est une réponse valide).
    """
    prix_reference = prix_reference or {}
    selection, ecartees = compute_selection_du_jour(results, seuil_conviction)

    out: List[str] = ["## 🎯 Sélection du jour — max 3", ""]
    # P2 — la méthodologie de sélection (4 règles) est désormais expliquée UNE
    # SEULE fois dans la section « ## Comment lire les scores » (fin de bulletin).
    # Ici, la section ne garde que son titre + tableau.

    if not selection:
        out.append(
            "_Aucune sélection aujourd'hui (aucune cellule ne passe les 4 règles) "
            "— ne pas forcer._"
        )
        out.append("")
        return out

    header = "| Actif | Direction | Note | Porté par | Prix de réf. |"
    sep = "|---|---|---|---|---|"
    out.append(header)
    out.append(sep)
    for s in selection:
        note_str = f"{s['note']:+.2f}"
        # P3 — « Porté par » enrichi (nom complet + valeur + sens + contribution).
        porte = s.get("driver_detail") or (
            _truncate_driver(s["driver_nom"]) if s["driver_nom"] else "—"
        )
        px = prix_reference.get(s["fiche_key"])
        px_str = f"{px:g}" if isinstance(px, (int, float)) else "—"
        out.append(
            f"| {s['actif']} | {s['direction']} | {note_str} | {porte} | {px_str} |"
        )
    out.append("")

    # Candidates écartées par la dédup driver (motif explicite sous le tableau).
    ecartees_dedup = [e for e in ecartees if e["motif"].startswith("même pari")]
    for e in ecartees_dedup:
        out.append(f"_écartée : {e['actif']} — {e['motif']}._")
    if ecartees_dedup:
        out.append("")

    # VOLET B — drapeau ⚠️ « bouge à contre-sens depuis la dernière clôture vue »
    # pour les actifs CONTINUS de la sélection (fin de l'angle mort overnight /
    # week-end côté visibilité). No-op si pas de shadow_capteurs, gap < seuil, ou
    # gap aligné avec la conclusion.
    out += _build_gap_contresens_flags(selection, shadow_capteurs, fiches)

    # Avertissement catalyseur J0 (impact high) sur un actif sélectionné. Le
    # calendrier liste les actifs par `fiche_key` (cf. calendrier-eco.yml) → on
    # croise sur fiche_key, puis on affiche le NOM lisible de l'actif sélectionné.
    cat_high = _catalyseurs_j0_high(now)
    if cat_high:
        nom_par_key = {s["fiche_key"]: s["actif"] for s in selection}
        emis = False
        for ev in cat_high:
            touches = [nom_par_key[k] for k in ev["actifs"] if k in nom_par_key]
            if touches:
                liste = ", ".join(touches)
                out.append(
                    f"⚠️ **{ev['nom']} aujourd'hui** — peut retourner ce pari "
                    f"({liste})."
                )
                emis = True
        if emis:
            out.append("")

    return out


# Longueur max d'un nom de critère dans la colonne « Porté par » (troncature
# propre avec « … » — pas de coupe au milieu d'un mot si évitable).
DRIVER_NAME_MAX_LEN = 40


def _truncate_driver(nom: str) -> str:
    """Tronque un nom de critère à DRIVER_NAME_MAX_LEN pour la colonne « Porté par ».

    Coupe à la frontière de mot la plus proche sous la limite si possible, sinon
    coupe dur ; ajoute « … ». Déterministe, pas d'invention de contenu.
    """
    if len(nom) <= DRIVER_NAME_MAX_LEN:
        return nom
    coupe = nom[: DRIVER_NAME_MAX_LEN - 1].rstrip()
    espace = coupe.rfind(" ")
    if espace >= DRIVER_NAME_MAX_LEN // 2:
        coupe = coupe[:espace].rstrip()
    return coupe + "…"


def _driver_detail(r: "ActifResult", h: str) -> str:
    """« Porté par » ENRICHI (P3) — détail scannable du driver dominant.

    Format cible (concis) : `nom COMPLET (val X, sens Y) → contribue ±Z.ZZ`.
    - nom COMPLET : libellé trader NON tronqué (lisibilité — P3).
    - val X : valeur brute du critère (même source que la colonne « Valeur
      actuelle » du détail), « — » si absente.
    - sens Y : `normal` / `inversé` (même sémantique que la colonne « Sens »).
    - contribue ±Z.ZZ : contribution signée du critère sur l'horizon h (même
      source que la colonne « Effet {h} »).

    Le driver = critère au plus fort |effet| sur l'horizon (logique `_top_driver`
    inchangée — PUR AFFICHAGE, zéro modif du calcul). Retourne "—" si aucun
    contributeur réel. Best-effort : toute valeur manquante → dégradation propre.
    """
    cle, _nom = _top_driver(r, h)
    if not cle and not _nom:
        return "—"
    # Retrouver le CritereResult correspondant au driver (par cle puis nom).
    cible: Optional["CritereResult"] = None
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        ctr = c.contributions.get(h)
        if ctr is None or abs(ctr) <= 0.0:
            continue
        if (getattr(c, "cle_courante", "") or "") == cle and _nom_critere(c) == _nom:
            cible = c
            break
    if cible is None:
        # Fallback : on n'a que le nom (zéro invention au-delà du nom).
        return _nom or "—"
    nom = _nom_critere(cible)
    val = _fmt_raw(cible.valeur_brute)
    sens = "normal" if cible.signe == 1 else "inversé"
    contrib = cible.contributions.get(h, 0.0)
    parts = []
    if val != "—":
        parts.append(f"val {val}")
    parts.append(f"sens {sens}")
    ctx = ", ".join(parts)
    return f"{nom} ({ctx}) → contribue {contrib:+.2f}"


# ---------------------------------------------------------------------------
# SOURCE DE VÉRITÉ UNIQUE des drapeaux de prudence d'une cellule de Synthèse
# ---------------------------------------------------------------------------
# Cette fonction calcule la chaîne EXACTE de drapeaux de prudence rendue dans la
# colonne d'une cellule de la table « ## Synthèse des décisions », dans le MÊME
# ORDRE. La grille (render_bulletin) ET la couche « raison » (`_raison_flags_suffix`)
# l'appellent — c'est l'unique calcul, avec le MÊME `now`. Plus de divergence
# possible (cf. audit round 2 : VIX 24h portait ⌛ en trop, Pétrole 24h un ⌛ faux,
# parce que la raison passait par `_compute_cell_risk_flags` avec un `now` différent
# et un jeu de prédicats parallèle).
#
# PÉRIMÈTRE : drapeaux de PRUDENCE uniquement, dans l'ordre de rendu de la grille
#   📰 (news-dominant OU régime news) · ⏸ (carry) · ⚠️ (conf. faible) ·
#   ◧ (mono-critère) · ↯ (divergence q↔n) · ⇄ (contre-momentum) ·
#   ⇆ (incohérence inter-horizons) · ⌛ (déjà-coté) · ⊘ (démenti).
# EXCLUS volontairement (qualificatifs structurels, jamais portés par la raison) :
#   ⚑ (gate régime — bruit global), ≈ / ⚪ (bandes de neutralité), (tb) / [quant…].
# INSUFFISANT (🚫) : cellule sans direction → aucun drapeau de prudence (liste vide).
def _synthese_cell_risk_flags(
    r: "ActifResult", h: str, now: datetime
) -> List[str]:
    """Liste ordonnée des symboles de prudence de la cellule de Synthèse (h).

    Réplique EXACTE des prédicats de la grille (render_bulletin), au même `now`.
    C'est l'unique source : la grille et la raison consomment cette liste.
    Déterministe ; best-effort sur l'already-priced (jamais de crash de rendu).
    """
    import triggers_classifier as _tc_classifier  # noqa: F401 (import paresseux)

    conc = r.conclusions.get(h, "")
    if conc == CONCLUSION_INSUFFISANT:
        return []  # 🚫 : pas de drapeau de prudence (cellule non directionnelle)

    confidence = r.confidence.get(h, "normale")
    flags: List[str] = []

    # 📰 news-dominant (ratio > 0.5) OU 📰 régime news — même test que la grille.
    cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
    n_tot = abs(float(cap_info.get("news_total_pm1", 0.0)))
    q_tot = abs(float(cap_info.get("quant_total_pm1", 0.0)))
    is_news = (n_tot / (q_tot + 1e-9)) > NEWS_DOMINANT_RATIO
    is_news_regime = r.is_news_regime.get(h, False)
    if is_news or is_news_regime:
        flags.append("📰")

    # ⏸ carry / ⚠️ conf. faible — exclusifs entre eux et avec le régime news
    # (la grille pose conf_flag UNIQUEMENT hors carry ET hors régime news).
    if r.is_carry.get(h, False):
        flags.append("⏸")
    elif (not is_news_regime) and confidence == "faible":
        flags.append("⚠️")

    # ◧ mono-critère dominant (fragilité d'une direction actée)
    if detect_mono_critere_dominant(r, h)[0]:
        flags.append("◧")
    # ↯ divergence quant↔news
    if r.divergence_quant_news.get(h, False):
        flags.append("↯")
    # ⇄ contre-momentum
    if r.contre_momentum.get(h, False):
        flags.append("⇄")
    # ⇆ incohérence inter-horizons (1 par actif, répété sur chaque cellule)
    if r.incoherence_inter_horizons:
        flags.append("⇆")

    # ⌛ déjà-coté / ⊘ démenti — même balayage que la grille, au MÊME `now`.
    ap_present = False
    denial_present = False
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        if c.is_denial:
            denial_present = True
        if c.event_date and not ap_present:
            try:
                _cdt = datetime.fromisoformat(c.event_date)
            except ValueError:
                _cdt = None
            if _cdt is not None:
                try:
                    _ap, _ = _tc_classifier.compute_already_priced_for_horizon(
                        _cdt, h, now=now,
                    )
                except Exception:  # noqa: BLE001 — best-effort rendu
                    _ap = False
                if _ap:
                    ap_present = True
        if ap_present and denial_present:
            break
    if ap_present:
        flags.append("⌛")
    if denial_present:
        flags.append("⊘")
    return flags


# ---------------------------------------------------------------------------
# « Raison principale » par cellule (Synthèse des décisions) — PUR RENDU
# ---------------------------------------------------------------------------
# Driver dominant = critère au plus fort CONTRIBUTION DANS LE SENS de la
# conclusion nette (PAS le plus fort |effet| brut). Règle d'or de l'audit
# `/tmp/audit-marche-raisons.md` : si le critère de plus fort |effet| CONTREDIT
# la direction nette (cas S&P 7j LONG porté par crédit+taux 10a malgré taux réels
# baissiers dominants en |effet|), on prend le plus fort contributeur QUI VA dans
# le sens de la conclusion — jamais une raison à contre-sens.
#
# Déterministe, zéro LLM, zéro réseau. La raison est RECALCULÉE à chaque run
# depuis les drivers courants (aucun état stocké) → se met à jour « au fur et à
# mesure » et persiste tant que le driver dominant ne change pas.

# Convention de signe DOUTEUSE (audit point 5) : phrase neutre forcée.
_RAISON_DRIVERS_DOUTEUX: set = {"meteo_cacao_cote_ivoire_ghana"}

# Quasi-neutre → on n'invente PAS de direction (audit : VIX 7j/1m, CAC).
_RAISON_QUASI_NEUTRE = "quasi-neutre — pas de driver franc"

# B1 — co-driver news co-dominant : un 2ᵉ driver dont le |effet| atteint au moins
# (1 − RAISON_CODRIVER_TOL) fois celui du driver principal ET qui porte la news
# (source_track "ia*"/"keyword") est MENTIONNÉ dans la raison (sinon on masque un
# driver news décisif — cas Pétrole 7j : momentum −5.6 vs OPEC+ −5.4). 15 % de
# tolérance (≈ quasi-égalité) — aligné avec le brief d'audit.
RAISON_CODRIVER_TOL: float = 0.15

# N1 — repère d'actionnabilité (lentille Spéculateur). On RÉUTILISE la force de
# conviction déjà calculée pour la colonne « Conviction » de « À jouer »
# (`_conviction_cell`) : on n'ajoute le repère QUE sur une cellule franche
# (|note| ≥ NEUTRAL_BAND) et seulement si la force est exploitable (≠ "—").
# Quasi-neutre → pas de force (reste « pas de driver franc »).
_RAISON_FORCE_SEUIL_DEFAUT: float = 0.6  # fallback si bilan_jour KO (cf. À jouer)


def _raison_flags_suffix(r: "ActifResult", h: str, now: Optional[datetime] = None) -> str:
    """B2-EXACT — suffixe de drapeaux de prudence HÉRITÉS de la cellule de Synthèse.

    SOURCE DE VÉRITÉ UNIQUE : `_synthese_cell_risk_flags` — EXACTEMENT la même
    fonction (et le même `now`) que celle dont la grille « ## Synthèse des
    décisions » tire ses drapeaux de prudence par cellule. La raison ne peut donc
    JAMAIS diverger de la colonne (audit round 2 : VIX 24h portait ⌛ en trop,
    Pétrole 24h un ⌛ faux — causé par un calcul parallèle `_compute_cell_risk_flags`
    avec un `now` distinct ; supprimé). Pour TOUTE cellule :
    drapeaux(raison) == drapeaux(table Synthèse), au symbole et à l'ordre près.

    Retourne une chaîne « 📰 ⌛ » préfixée d'un espace (ou "" si aucun drapeau).
    `now` DOIT être le `now` du bulletin (l'already-priced ⌛ est sensible au temps) ;
    en l'absence, on retombe sur l'horloge (best-effort). Ne lève jamais.
    """
    now = now or datetime.now(timezone.utc)
    try:
        flags = _synthese_cell_risk_flags(r, h, now)
    except Exception:  # noqa: BLE001 — best-effort rendu, jamais de crash
        flags = []
    if not flags:
        return ""
    return " " + " ".join(flags)


def _cell_is_news_weighted(r: "ActifResult", h: str) -> bool:
    """True si la cellule est NEWS-PONDÉRÉE (📰) : abs(news)/abs(quant) > 0.5 ET
    le pondéré DIFFÈRE du brut (la décision est réellement tempérée par les news).

    Réutilise EXACTEMENT le test de la table de Synthèse (news_cap_info +
    pond_differe). Sert à B3 (chiffre pondéré) et au 📰 hérité (B2).
    """
    cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
    n_tot = abs(float(cap_info.get("news_total_pm1", 0.0)))
    q_tot = abs(float(cap_info.get("quant_total_pm1", 0.0)))
    is_news = (n_tot / (q_tot + 1e-9)) > NEWS_DOMINANT_RATIO
    if not is_news:
        return False
    conc_p = r.conclusions_pond.get(h, "")
    score_p = r.scores_pond.get(h, 0.0)
    score = r.scores.get(h, 0.0)
    conc = r.conclusions.get(h, "")
    pond_differe = bool(conc_p) and (conc_p != conc or abs(score_p - score) >= 0.005)
    return pond_differe


@functools.lru_cache(maxsize=1)
def _load_raisons_drivers() -> Dict[str, Dict[str, Dict[str, str]]]:
    """Charge `config/raisons-drivers.yml` (mémoïsé). Best-effort : si le fichier
    est absent/illisible, retourne une biblio vide → fallback nom canonique."""
    try:
        with RAISONS_DRIVERS_FILE.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001 (best-effort, jamais de crash de rendu)
        return {"drivers": {}, "prefixes": {}}
    return {
        "drivers": data.get("drivers", {}) or {},
        "prefixes": data.get("prefixes", {}) or {},
        "aliases": data.get("aliases", {}) or {},
    }


def _resolve_cle_canonique(cle: str) -> str:
    """Résout une clé RÉELLE du pipeline vers sa clé canonique de biblio via les
    `aliases`. Retourne la clé inchangée si pas d'alias. Sert aussi à détecter le
    driver « douteux » (meteo_cacao) après résolution."""
    if not cle:
        return cle
    return _load_raisons_drivers()["aliases"].get(cle, cle)


def _raison_phrases_for_cle(cle: str) -> Optional[Dict[str, str]]:
    """Retourne le dict de phrases (`phrase_long`/`phrase_short`/`phrase_neutre`)
    pour une `cle_courante`, ou None si la clé n'est pas dans la biblio.

    Ordre : alias (clé réelle → canonique) → exact → PRÉFIXE (clés à suffixe
    d'actif type `momentum_prix_20j_petrole`). L'exact prime sur le préfixe.
    """
    if not cle:
        return None
    biblio = _load_raisons_drivers()
    canon = _resolve_cle_canonique(cle)
    drivers = biblio["drivers"]
    if canon in drivers:
        return drivers[canon]
    # Préfixes : le plus long préfixe correspondant gagne (déterminisme).
    prefixes = biblio["prefixes"]
    best_pref = ""
    for pref in prefixes:
        if canon.startswith(pref) and len(pref) > len(best_pref):
            best_pref = pref
    if best_pref:
        return prefixes[best_pref]
    return None


def _driver_dominant_net(
    r: "ActifResult", h: str, direction: str
) -> Tuple[str, str, float]:
    """Critère au plus fort contributeur DANS LE SENS de `direction` (LONG/SHORT).

    LONG → max contribution positive. SHORT → contribution la plus négative
    (max |c| parmi les c<0). Exclut gates et n/a. Départage ex æquo par nom
    (déterministe). Retourne `(cle_courante, nom, contribution_signée)`, ou
    `("", "", 0.0)` si aucun contributeur ne va dans le sens de la conclusion.
    """
    veut_positif = direction == "LONG"
    best_key: Tuple[float, str] = (-1.0, "")  # (|contrib dans le sens|, nom)
    best_cle = ""
    best_nom = ""
    best_ctr = 0.0
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        ctr = c.contributions.get(h)
        if ctr is None:
            continue
        # Garde uniquement les contributeurs qui POUSSENT dans le sens net.
        if veut_positif and ctr <= 0.0:
            continue
        if (not veut_positif) and ctr >= 0.0:
            continue
        key = (abs(ctr), c.nom)
        if key > best_key:
            best_key = key
            best_cle = getattr(c, "cle_courante", "") or ""
            best_nom = _nom_critere(c)
            best_ctr = ctr
    return best_cle, best_nom, best_ctr


def _codriver_news_codominant(
    r: "ActifResult", h: str, direction: str, best_cle: str, best_ctr: float
) -> Tuple[str, float]:
    """B1 — repère un 2ᵉ driver NEWS co-dominant à mentionner dans la raison.

    Cherche, parmi les contributeurs qui poussent DANS LE SENS de `direction`
    (hors le driver principal `best_cle`), un critère news (source_track "ia*" /
    "keyword") dont le |effet| atteint au moins (1 − RAISON_CODRIVER_TOL) × |best_ctr|.
    Cas type : Pétrole 7j SHORT — momentum −5.6 (principal) vs OPEC+ −5.4 (news,
    quasi-égal) → on ne masque pas OPEC+.

    Retourne `(cle_courante, contribution_signée)` du co-driver, ou `("", 0.0)`.
    Déterministe : à |effet| égal, départage par nom (via le tri implicite).
    """
    if not best_cle or abs(best_ctr) <= 0.0:
        return "", 0.0
    veut_positif = direction == "LONG"
    seuil = abs(best_ctr) * (1.0 - RAISON_CODRIVER_TOL)
    best_co: Tuple[float, str] = (-1.0, "")
    best_co_cle = ""
    best_co_ctr = 0.0
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        cle = getattr(c, "cle_courante", "") or ""
        if cle == best_cle:
            continue
        src = getattr(c, "source_track", "") or ""
        is_news = src.startswith("ia") or src == "keyword"
        if not is_news:
            continue
        ctr = c.contributions.get(h)
        if ctr is None:
            continue
        if veut_positif and ctr <= 0.0:
            continue
        if (not veut_positif) and ctr >= 0.0:
            continue
        if abs(ctr) < seuil:
            continue
        key = (abs(ctr), c.nom)
        if key > best_co:
            best_co = key
            best_co_cle = cle
            best_co_ctr = ctr
    return best_co_cle, best_co_ctr


def _raison_force_suffix(r: "ActifResult", h: str) -> str:
    """N1 — repère d'actionnabilité (lentille Spéculateur) sur cellule FRANCHE.

    Réutilise la force déjà calculée pour la colonne « Conviction » de « À jouer »
    (`_conviction_cell`) — ne réinvente RIEN. On ne pose le repère que sur une
    direction franche (|note| ≥ NEUTRAL_BAND) ; quasi-neutre → pas de force.

    Retourne « [conviction forte] » / « [conviction molle (score faible)] » etc.,
    préfixé d'un espace, ou "" si la force n'est pas exploitable ("—").
    """
    direction = r.conclusions.get(h, "")
    if direction not in ("LONG", "SHORT"):
        return ""
    if abs(r.scores.get(h, 0.0)) < NEUTRAL_BAND:
        return ""
    try:
        seuil = _raison_force_seuil()
    except Exception:  # noqa: BLE001
        seuil = _RAISON_FORCE_SEUIL_DEFAUT
    force = _conviction_cell(r, h, seuil)
    if not force or force == "—":
        return ""
    return f" [conviction {force}]"


@functools.lru_cache(maxsize=1)
def _raison_force_seuil() -> float:
    """Seuil de conviction « forte » (même source que « À jouer »). Mémoïsé."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import bilan_jour as _bj
        return float(_bj._load_score_fort_seuil())
    except Exception:  # noqa: BLE001 — défaut documenté si bilan_jour KO
        return _RAISON_FORCE_SEUIL_DEFAUT


def _raison_parts(
    r: "ActifResult", h: str, now: Optional[datetime] = None
) -> Tuple[str, str, str]:
    """Décompose la raison d'une cellule en (corps_sans_chiffre, chiffre, suffixes).

    Sert au regroupement N2 (`build_raisons_block`) : deux horizons fusionnent
    SSI leur `corps_sans_chiffre` est identique. Le `chiffre` (par horizon) et les
    `suffixes` (force N1 + drapeaux B2, par horizon) restent distincts.

    Retourne :
      - corps  : phrase driver + éventuel « + co-driver (news) » (SANS chiffre),
                 ou _RAISON_QUASI_NEUTRE / "—".
      - chiffre: « (+5.1) » ou « (+1.0 pondéré, brut +2.9) », ou "".
      - suffixe: « [conviction forte] ↯ ⌛ », ou "".
    """
    direction = r.conclusions.get(h, "")
    score = r.scores.get(h, 0.0)
    if direction not in ("LONG", "SHORT") or abs(score) < NEUTRAL_BAND:
        return _RAISON_QUASI_NEUTRE, "", ""
    cle, nom, ctr = _driver_dominant_net(r, h, direction)
    if not cle and not nom:
        return "—", "", ""

    news_weighted = _cell_is_news_weighted(r, h)
    if news_weighted:
        score_p = r.scores_pond.get(h, score)
        chiffre = f"({score_p:+.1f} pondéré, brut {score:+.1f})"
    else:
        chiffre = f"({ctr:+.1f})"

    phrases = _raison_phrases_for_cle(cle)
    if phrases is None:
        corps = nom if nom else "—"
    else:
        if _resolve_cle_canonique(cle) in _RAISON_DRIVERS_DOUTEUX:
            phrase = phrases.get("phrase_neutre") or phrases.get(
                "phrase_long" if ctr > 0 else "phrase_short", ""
            )
        else:
            phrase = phrases.get("phrase_long" if ctr > 0 else "phrase_short", "")
        corps = phrase if phrase else (nom if nom else "—")

    if corps == "—":
        return "—", "", ""

    co_cle, co_ctr = _codriver_news_codominant(r, h, direction, cle, ctr)
    if co_cle:
        co_phrases = _raison_phrases_for_cle(co_cle)
        co_label = ""
        if co_phrases is not None and _resolve_cle_canonique(co_cle) not in _RAISON_DRIVERS_DOUTEUX:
            co_label = co_phrases.get("phrase_long" if co_ctr > 0 else "phrase_short", "")
        if not co_label:
            for c in r.criteres:
                if (getattr(c, "cle_courante", "") or "") == co_cle:
                    co_label = _nom_critere(c)
                    break
        if co_label:
            corps = f"{corps} + {co_label} (news)"

    suffixe = f"{_raison_force_suffix(r, h)}{_raison_flags_suffix(r, h, now)}"
    return corps, chiffre, suffixe


def _raison_cellule(r: "ActifResult", h: str, now: Optional[datetime] = None) -> str:
    """Raison principale DÉTERMINISTE d'une cellule (actif × horizon).

    Règles (audit `/tmp/audit-marche-raisons.md`) :
      1. Direction absente / INSUFFISANT / carry / news-régime sans note franche,
         ou |note| < NEUTRAL_BAND → « quasi-neutre — pas de driver franc »
         (ne JAMAIS inventer de direction — cf. VIX 7j/1m, CAC, S&P 1m).
      2. Sinon driver dominant = plus fort contributeur DANS LE SENS de la
         conclusion nette (jamais le |effet| brut à contre-sens — cas S&P 7j).
      3. Phrase de la biblio selon le SIGNE de la contribution + contribution
         chiffrée (ex. « taux réels US élevés … (−7.8) »).
      4. `meteo_cacao` (signe douteux) → phrase NEUTRE, pas de direction assénée.
      5. Gates (⚑ FOMC) jamais cités (exclus par `is_gate`).
      6. Fallback : pas d'entrée biblio → nom canonique (legacy). Aucun
         contributeur dans le sens → « — ». Jamais de crash.
      B1. Co-driver NEWS co-dominant (≥85 % du driver principal) mentionné.
      B2. Drapeaux de prudence HÉRITÉS de la cellule de Synthèse (↯ ⌛ ◧ ⚠️ 📰…).
      B3. Quand la cellule est NEWS-PONDÉRÉE (📰), le chiffre cité est la NOTE
          PONDÉRÉE de la colonne (brut→pondéré), jamais la contribution brute du
          critère seule (qui contredirait visuellement la note de la colonne).
      N1. Repère d'actionnabilité (force de conviction) sur cellule franche.

    Source UNIQUE : `_raison_parts` (mêmes données que le regroupement N2).
    """
    corps, chiffre, suffixe = _raison_parts(r, h, now)
    if corps in (_RAISON_QUASI_NEUTRE, "—"):
        return corps
    sep = " " if chiffre else ""
    return f"{corps}{sep}{chiffre}{suffixe}"


def build_raisons_block(
    results: List["ActifResult"], now: Optional[datetime] = None
) -> List[str]:
    """Bloc compact « raison principale » PAR ACTIF, sous la grille de Synthèse.

    Un bloc par actif (12), 3 horizons sur une ligne scannable :
      **Or** — 24h : taux réels élevés (SHORT) · 7j : … · 1m : …

    PUR RENDU : recalculé à chaque run depuis les drivers courants. La direction
    (LONG/SHORT) est rappelée entre parenthèses ; quasi-neutre → pas de direction.

    `now` : DOIT être le `now` du bulletin pour que les drapeaux ⌛ (already-priced,
    sensibles au temps) hérités soient IDENTIQUES à ceux de la grille de Synthèse.
    En l'absence (appel hors render_bulletin), on retombe sur l'horloge.
    """
    now = now or datetime.now(timezone.utc)
    lines: List[str] = []
    lines.append("**Raison principale par cellule** _(driver dominant courant, dans le sens de la décision — recalculé à chaque run)_")
    lines.append("")
    for r in results:
        # Décompose chaque horizon en (corps, chiffre, suffixe, direction, sémantique chiffre).
        # 5ᵉ champ `nw` (news-weighted) — N3 : la sémantique du chiffre DIFFÈRE selon
        # qu'il est news-pondéré (« note pondérée ») ou non (« effet du driver »). On
        # ne regroupe PAS deux horizons de sémantique différente (sinon une parenthèse
        # mélangerait note pondérée et effet brut — cas Nasdaq 7j pondéré vs 1m effet).
        parts: List[Tuple[str, str, str, str, bool]] = []  # (corps, chiffre, suffixe, dir, nw)
        for h in HORIZONS:
            corps, chiffre, suffixe = _raison_parts(r, h, now)
            direction = r.conclusions.get(h, "")
            score = r.scores.get(h, 0.0)
            dir_label = direction if (direction in ("LONG", "SHORT") and abs(score) >= NEUTRAL_BAND) else ""
            nw = _cell_is_news_weighted(r, h)
            parts.append((corps, chiffre, suffixe, dir_label, nw))

        # N2 — regroupe les horizons CONSÉCUTIFS au MÊME corps (même driver/phrase)
        # ET même direction franche. Garde le détail quand les drivers DIFFÈRENT.
        morceaux: List[str] = []
        i = 0
        while i < len(HORIZONS):
            corps, _chiffre, _suffixe, dir_label, nw = parts[i]
            # Cellule non-franche (quasi-neutre / —) : jamais regroupée, rendu simple.
            if corps in (_RAISON_QUASI_NEUTRE, "—"):
                morceaux.append(f"{HORIZONS[i]} : {corps}")
                i += 1
                continue
            # Étend le groupe tant que le corps, la direction ET la SÉMANTIQUE du
            # chiffre (news-pondéré vs effet brut, N3) sont identiques — sinon une
            # parenthèse de groupe mélangerait note pondérée et effet de driver.
            j = i + 1
            while (
                j < len(HORIZONS)
                and parts[j][0] == corps
                and parts[j][3] == dir_label
                and parts[j][4] == nw
                and corps not in (_RAISON_QUASI_NEUTRE, "—")
            ):
                j += 1
            if j - i >= 2:
                # Groupe : « 24h/7j/1m : même driver — <corps> (c1 / c2 / c3) (DIR) ».
                hz = "/".join(HORIZONS[i:j])
                chiffres = " / ".join(parts[k][1].strip("() ") for k in range(i, j))
                # Drapeaux/force : on prend ceux du PREMIER horizon du groupe (les
                # cellules d'un même driver partagent leurs drapeaux structurels) ;
                # si un horizon du groupe porte un suffixe DIFFÉRENT, on le détaille.
                suffixes = {parts[k][2] for k in range(i, j)}
                suff = parts[i][2] if len(suffixes) == 1 else ""
                dir_str = f" _({dir_label})_" if dir_label else ""
                morceaux.append(f"{hz} : même driver — {corps} ({chiffres}){suff}{dir_str}")
                i = j
            else:
                # Pas de regroupement : rendu détaillé de l'horizon.
                sep = " " if _chiffre else ""
                dir_str = f" _({dir_label})_" if dir_label else ""
                morceaux.append(f"{HORIZONS[i]} : {corps}{sep}{_chiffre}{_suffixe}{dir_str}")
                i += 1
        lines.append(f"- **{r.nom}** — " + " · ".join(morceaux))
    lines.append("")
    return lines


def _synthese_paris_partages(
    cells: List[Dict[str, str]],
    shared: Dict[Tuple[str, str], int],
) -> List[str]:
    """Lignes de synthèse « ⚭ Même pari » sous le tableau Jouables.

    Une ligne par groupe (cle_courante, direction) ayant ≥ 2 lignes. Le libellé
    du driver vient de shared_drivers.driver_label (fallback : nom du critère).
    Liste les actifs concernés et la direction. Rien si aucun groupe.
    """
    if not shared:
        return []
    try:
        import shared_drivers as _sd  # noqa: F401 (lazy, cf. pattern existant)
    except Exception:  # noqa: BLE001
        _sd = None  # type: ignore
    lines: List[str] = []
    # Ordre déterministe : par nombre de lignes desc, puis par cle.
    for (cle, direction), _n in sorted(
        shared.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])
    ):
        membres = [d for d in cells if d["driver_cle"] == cle and d["direction"] == direction]
        actifs = [d["actif"] for d in membres]
        nom_fallback = membres[0]["driver_nom"] if membres else ""
        label = _sd.driver_label(cle, nom_fallback) if _sd is not None else nom_fallback
        label = label or cle
        if len(actifs) > 1:
            liste = ", ".join(actifs[:-1]) + " et " + actifs[-1]
        else:
            liste = actifs[0]
        lines.append(
            f"_{SHARED_DRIVERS_SYMBOL_LOCAL} Même pari : **{label}** porte "
            f"{liste} ({direction}) — jouer plusieurs de ces lignes = "
            f"multiplier le levier sur UN driver._"
        )
    return lines


def _top_explication(r: "ActifResult", h: str) -> str:
    """Phrase d'explication DÉTERMINISTE (zéro LLM) d'une cellule du top conviction.

    Source UNIQUE : les `contributions[h]` des critères de l'ActifResult (mêmes
    données que le tableau « Détail par actif »). Cite les 2 critères qui portent
    le PLUS la direction (|contribution| max, nom trader + valeur signée), puis,
    si pertinent : « news en sens inverse (↯) » (divergence quant↔news sur cet
    horizon) OU « porté par les news 📰 » (les contributions news dominent et vont
    dans le sens de la conclusion). Retourne "" si aucun contributeur réel.
    """
    contribs: List[Tuple[float, str, float, bool]] = []  # (|c|, nom, c_signed, is_news)
    for c in r.criteres:
        if c.is_gate or c.is_na:
            continue
        ctr = c.contributions.get(h)
        if ctr is None or abs(ctr) <= 0.0:
            continue
        is_news = c.source_track.startswith("ia") or c.source_track == "keyword"
        contribs.append((abs(ctr), _nom_critere(c), float(ctr), is_news))
    if not contribs:
        return ""
    # Tri |contribution| desc, départage déterministe par nom pour stabilité.
    contribs.sort(key=lambda t: (-t[0], t[1]))
    top2 = contribs[:2]
    parts = [f"{nom} ({c_signed:+.1f})" for _a, nom, c_signed, _n in top2]
    if len(parts) == 1:
        coeur = f"Porté par {parts[0]}"
    else:
        coeur = f"Porté par {parts[0]} et {parts[1]}"

    mention = ""
    if r.divergence_quant_news.get(h, False):
        mention = " ; news en sens inverse (↯)"
    else:
        # 📰 — les news dominent ET vont dans le sens de la conclusion.
        news_total = sum(c for _a, _nm, c, is_n in contribs if is_n)
        quant_total = sum(c for _a, _nm, c, is_n in contribs if not is_n)
        conc = r.conclusions.get(h, "")
        news_aligne = (
            (conc == "LONG" and news_total > 0)
            or (conc == "SHORT" and news_total < 0)
        )
        if abs(news_total) > abs(quant_total) and news_aligne:
            mention = " ; porté par les news 📰"
    return f"_{coeur}{mention}._"


def build_top_multi_horizons_block(
    results: List["ActifResult"],
    shared_summary: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    """Mini « Top convictions multi-horizons » (≤ 3 lignes), AVEC les drapeaux
    de chaque cellule (audit UX 10/06 : la n°1 EUR/USD 7j ◧ affichée sans
    avertissement — plus jamais). Réutilise la sélection de `build_top3_block`
    (3 actifs distincts, meilleur horizon, confidence normale) mais expose les
    drapeaux de risque de la cellule.

    Si ≥ 2 cellules du top partagent le même driver dominant, ajoute une ligne
    « ⚭ N de ces convictions reposent sur le même driver : <label> »
    (réutilise shared_drivers — zéro nouveau calcul).
    """
    # Réutilise la sélection canonique du Top 3 (3 actifs distincts, normale).
    raw = build_top3_block(results)
    # raw contient le titre + lignes « - **Actif h — DIR (note)** — raison ».
    # On retrouve les (actif, horizon) sélectionnés pour rattacher les drapeaux.
    selected: List[Tuple["ActifResult", str]] = []
    res_by_nom = {r.nom: r for r in results}
    import re as _re
    for ln in raw:
        m = _re.match(r"- \*\*(.+) (24h|7j|1m) — ", ln)
        if not m:
            continue
        nom, h = m.group(1), m.group(2)
        r = res_by_nom.get(nom)
        if r is not None:
            selected.append((r, h))

    out: List[str] = ["## 🎯 Top convictions multi-horizons", ""]
    if not selected:
        out.append("_Aucune conviction à couverture suffisante ce cycle._")
        out.append("")
        return out
    # P5 — la pédagogie (◧ / ↯, recoupement avec « À jouer ») est expliquée UNE
    # SEULE fois dans « ## Comment lire les scores » (fin de bulletin).
    now_for_flags = datetime.now(timezone.utc)
    for r, h in selected:
        conc = r.conclusions.get(h, "")
        score = r.scores.get(h, 0.0)
        # P3 — driver enrichi (nom complet + valeur + sens + contribution).
        raison = _driver_detail(r, h)
        if raison == "—":
            raison = ""
        flags = _compute_cell_risk_flags(r, h, now_for_flags)
        if conc in ("LONG", "SHORT"):
            if abs(score) < 0.05:
                flags = ["⚪"] + flags
            elif abs(score) < NEUTRAL_BAND:
                flags = ["≈"] + flags
        flags_str = (" — drapeaux : " + " ".join(flags)) if flags else ""
        suffix = f" — {raison}" if raison else ""
        out.append(f"- **{r.nom} {h} — {conc} ({score:+.2f})**{suffix}{flags_str}")
        # Phrase d'explication déterministe (2 critères porteurs + ↯/📰).
        explication = _top_explication(r, h)
        if explication:
            out.append(f"  {explication}")

    # ⚭ — si ≥ 2 cellules du top partagent le même driver dominant.
    if shared_summary:
        try:
            import shared_drivers as _sd  # noqa: F401
        except Exception:  # noqa: BLE001
            _sd = None  # type: ignore
        # Driver dominant de chaque cellule sélectionnée (par cle_courante).
        from collections import Counter
        dom_cles: List[Tuple[str, str]] = []  # (cle, label)
        for r, h in selected:
            best_cle, best_label = _top_driver(r, h)
            if best_cle:
                lbl = best_label
                if _sd is not None:
                    lbl = _sd.driver_label(best_cle, best_label)
                dom_cles.append((best_cle, lbl))
        counts = Counter(cle for cle, _ in dom_cles)
        for cle, n in counts.most_common(1):
            if n >= 2:
                label = next(lbl for c, lbl in dom_cles if c == cle)
                out.append("")
                out.append(
                    f"- {SHARED_DRIVERS_SYMBOL_LOCAL} {n} de ces convictions "
                    f"reposent sur le même driver : {label} — un retournement "
                    f"de ce signal les fausserait ensemble."
                )
    out.append("")
    return out


# Symbole ⚭ (réf. shared_drivers) — copié localement pour éviter un import dur
# au niveau module (cohérent avec le pattern d'imports paresseux du fichier).
SHARED_DRIVERS_SYMBOL_LOCAL = "⚭"


# Traduction des types de normalisation en libellé humain pour le tableau
# « Détail par actif » (reco-wording-detail-bulletin.md §2). N'affecte QUE
# l'affichage — la valeur brute `type_norm` reste dans le decision-log.
TYPE_NORM_LABELS: Dict[str, str] = {
    "zscore": "Écart à la normale",
    "lineaire": "Échelle graduée",
    "mapping_non_monotone": "Régime par seuils",
    "composite": "Signal combiné",
    "triplet": "Direction news",
    "gate": "Drapeau régime",
}


def _label_type_norm(type_norm: str) -> str:
    """Libellé humain d'un type de normalisation ; retombe sur le brut si inconnu."""
    return TYPE_NORM_LABELS.get(type_norm, type_norm)


# Libellé affiché quand un créneau news PORTE la direction NETTE (synthèse
# DeepSeek du corpus de l'actif), par opposition à sa détection mots-clés
# thématique. Voir _nom_affiche.
SYNTHESE_NET_LABEL = "Synthèse news (net, IA)"

# source_track qui signifient « ce créneau porte le net IA » (synthèse
# directionnelle DeepSeek du corpus). Toute autre valeur (keyword, calendrier,
# ia_conflict, none, "", absent) = le créneau est en mode thématique → on
# affiche son nom de fiche tel quel (cf. triggers_classifier).
SYNTHESE_NET_TRACKS = frozenset({"ia_synthese", "ia_synthese_faible"})


def _nom_affiche(nom: str, source_track: str) -> str:
    """Libellé DYNAMIQUE d'un critère news, honnête dans ses 2 modes.

    Un créneau news « porteur du net » (cf. SYNTHESE_NET_CARRIER dans
    triggers_classifier) est à double casquette : tantôt il porte la DIRECTION
    NETTE du corpus (synthèse DeepSeek, source_track ∈ SYNTHESE_NET_TRACKS),
    tantôt il retombe sur sa DÉTECTION MOTS-CLÉS thématique (source_track
    "keyword" ou autre). Aucun NOM FIXE n'est honnête dans les 2 modes — d'où
    le libellé calculé AU RENDU :

    - source_track porte le net → « Synthèse news (net, IA) ».
    - sinon (keyword, calendrier, conflit, absent, critère non-news) → `nom`
      de fiche tel quel (comportement legacy, jamais de crash).

    PUR AFFICHAGE : n'altère ni cle_courante, ni signe, ni poids, ni score
    (L023). Se dégrade proprement si source_track manquant/inconnu.
    """
    track = (source_track or "").strip().lower()
    if track in SYNTHESE_NET_TRACKS:
        return SYNTHESE_NET_LABEL
    return nom


def _nom_critere(c: "CritereResult") -> str:
    """Raccourci : libellé dynamique d'un CritereResult (lit son source_track)."""
    return _nom_affiche(c.nom, getattr(c, "source_track", "") or "")


# Encart statique « Comment lire ce tableau » (reco-wording §5). Inséré une
# seule fois, juste avant la première section « Détail par actif ».
DETAIL_TABLE_HELP_LINES: List[str] = [
    "**Comment lire ce tableau**",
    "",
    "Chaque ligne est un critère qui influence la direction de l'actif.",
    "",
    "- **Penchant** (de −1 à +1) : à quel point ce critère pousse dans un sens. "
    "−1 = fortement baissier, +1 = fortement haussier, 0 = neutre.",
    "- **Importance** : le poids de ce critère dans la note finale. "
    "Un critère à 8 compte 4× plus qu'un critère à 2.",
    "- **Sens** : `normal` = quand la valeur monte, c'est haussier. "
    "`inversé` = quand la valeur monte, c'est baissier (ex. des taux réels élevés pèsent sur l'or).",
    "- **Effet 24h / 7j / 1m** : la contribution chiffrée de ce critère à chaque horizon. "
    "Positif = pousse LONG, négatif = pousse SHORT. La somme de tous les effets donne la note finale.",
    "",
]


# Mini-glossaire des acronymes conservés dans les noms de critères
# (reco-wording-noms-criteres.md §8). Affiché une seule fois, en pied de la
# section « Détail par actif ». N'affecte QUE l'affichage.
DETAIL_TABLE_GLOSSARY_LINES: List[str] = [
    "_**Glossaire** — "
    "PMI : indice d'activité industrielle (>50 = expansion) · "
    "RSI : indicateur de sur-achat / sur-vente (30 = très vendu, 70+ = très acheté) · "
    "VIX / VXN / V2X : indices de la « peur » du marché — volatilité attendue à 30 jours "
    "(US / Nasdaq / Europe) · "
    "SKEW / VVIX : risque de choc extrême et nervosité sur le VIX lui-même "
    "(montent avant les crises)._",
    "",
]


def build_comment_lire_block(flags_present: set) -> List[str]:
    """Section « ## Comment lire les scores » (P2/P4/P5) — TOUTE la pédagogie, UNE fois.

    Regroupe les explications jusque-là dispersées et répétées dans les sections
    du jour (Sélection / À jouer / Top convictions) + la légende des symboles + la
    définition de « Note ». Les sections du jour ne gardent désormais que leur
    titre + tableau ; cette section porte la pédagogie une seule fois, en fin de
    bulletin. PUR RENDU — aucun changement de score/mesure.

    `flags_present` : set des symboles réellement présents dans CE bulletin
    (légende contextuelle, comme avant). Best-effort, dégradation propre.
    """
    out: List[str] = ["## Comment lire les scores", ""]

    out.append("### Sélection du jour")
    out.append(
        "_Les meilleurs paris 24h du jour : (1) **signal fort**, (2) **données "
        "suffisantes** sur l'actif, (3) **chaque type de marché représenté une "
        "seule fois** (deux lignes portées par le même moteur — ex. taux/dollar — "
        "comptent pour un seul pari, on garde la plus forte), (4) **3 maximum**. "
        "Moins de 3 — voire zéro — est normal : on ne force jamais un pari._"
    )
    out.append("")

    out.append("### À jouer aujourd'hui (24h)")
    out.append(
        "_Les 12 cellules à 24h (horizon de trade), triées par force de note. "
        "« Conviction » = force du score ET absence de contestation (forte = note "
        "≥ seuil sans drapeau ; sinon le libellé dit POURQUOI : molle, contestée, "
        "fragile ou zigzag). « À éviter » = quasi coin-flip (⚪), quasi-neutre (≈) "
        "ou données insuffisantes (🚫). Les drapeaux de prudence (◧ ⚠️ ↯ …) restent "
        "dans « Jouables » — prudence, pas exclusion. Prix de réf. = prix "
        "d'émission stampé (— si pas encore disponible)._"
    )
    out.append(
        "_« Porté par » = le critère qui pèse le plus dans la note, avec sa valeur, "
        "son sens (normal / inversé) et sa contribution chiffrée signée ; "
        f"{SHARED_DRIVERS_SYMBOL_LOCAL} = plusieurs lignes reposent sur le même "
        "driver (jouer ces lignes = multiplier le levier sur UN signal)._"
    )
    out.append("")

    out.append("### Top convictions multi-horizons")
    out.append(
        "_Les meilleures convictions tous horizons confondus, avec leurs "
        "drapeaux : une note forte portée par 1 seul critère (◧) ou divergente "
        "(↯) reste à lire avec prudence. Ces convictions peuvent recouper les "
        "lignes 24h de « À jouer » (mêmes actifs, autres horizons)._"
    )
    out.append("")

    # Légende des symboles + définition de « Note » (déplacées depuis la synthèse).
    out.append("### Symboles et Note")
    out.append("")
    out.append(_build_legende(flags_present))
    out.append("")
    return out


def render_bulletin(
    results: List[ActifResult],
    veille_conclusions: Dict[str, Dict[str, str]],
    now: datetime,
    fiches_h: str,
    freshness_msg: str,
    prix_reference: Optional[Dict[str, float]] = None,
    shadow_capteurs: Optional[Dict[str, Dict[str, Optional[float]]]] = None,
    fiches: Optional[Dict[str, dict]] = None,
) -> str:
    # Lot 5 C8a — import paresseux (cohérent avec build_decision_log_records).
    import triggers_classifier as _tc_classifier  # noqa: F401
    lines: List[str] = []
    lines.append(f"# Bulletin Analyste — {now:%Y-%m-%d} · {now:%Hh%M} (Paris)")
    lines.append("")
    # En-tête allégé (audit UX 10/06, P1-D / bloc 4) : la ligne titre garde
    # date/heure ; « Fraîcheur » reste en tête (info utile au scan). La version
    # de l'Analyste + le hash des fiches (debug/suivi interne) sont déplacés EN
    # PIED de bulletin (section --- finale discrète) pour ne plus polluer la vue
    # de décision. La ligne « Généré » reste (utile pour dater le run).
    lines.append(f"- Généré : {now.isoformat()}")
    # P1 — la ligne « Fraîcheur » ne s'affiche QUE s'il y a un PROBLÈME (données
    # périmées / red line). Quand tout va bien (« fraîcheur OK … »), elle pollue la
    # méta chaque jour sans rien apporter → on la masque. La détection repose sur
    # la convention de check_freshness : message OK = commence par « fraîcheur OK ».
    _fresh_ok = (freshness_msg or "").strip().lower().startswith("fraîcheur ok")
    if not _fresh_ok:
        lines.append(f"- ⚠️ Fraîcheur : {freshness_msg}")
    # --- Régime extrême : annonce UNE fois (anti-bruit #5.1) ---------------
    # Si le gate est actif sur (quasi) tous les actifs, on l'annonce ici une
    # seule fois plutôt que de répéter ⚑ sur 12 lignes de la table. Le ⚑ par
    # cellule est alors masqué (cf. `regime_global` plus bas), il reste dans le
    # "Détail par actif" où il discrimine critère par critère.
    regime_global = regime_extreme_global(results)
    if regime_global:
        lines.append(
            "- ⚠️ Régime extrême actif sur l'ensemble du tableau "
            "(contexte géopolitique) — drapeau ⚑ non répété par cellule"
        )
    lines.append("")
    # --- C7 — Cellules à surveiller + cohérence biais agrégé ---------------
    # Bloc placé APRÈS la métadonnée et AVANT "Flips vs veille" pour que
    # Thomas voie immédiatement les cellules à risque sans scanner la matrice.
    # Le briefing étant préfixé en tête après le H1 (briefing.prepend_to_bulletin),
    # l'ordre final est : H1 → Briefing → Métadonnée → ⚠️ Surveillance → Biais
    # agrégé → Flips → Matrice → Détail → Limites.
    lines.extend(build_surveillance_block(results, now))

    # --- Reco A (audit corrélation cachée 05/06) — Drivers macro partagés ---
    # FLAG-ONLY (affichage pur). Signale quand un MÊME driver macro (par
    # cle_courante, jamais par nom — L023) porte ≥ 2 cellules de même direction
    # au-delà du seuil de part : le « large consensus » est alors UN pari répété.
    # Si aucun driver ne dépasse le seuil → pas de bloc (anti-bruit). Le symbole
    # ⚭ n'est ajouté à la légende QUE si le bloc est émis (pattern « présents only »).
    import shared_drivers as _shared_drivers  # noqa: F401 (lazy, cf. pattern existant)
    _shared_summary = _shared_drivers.compute_shared_drivers_summary(results, HORIZONS)
    _shared_block = _shared_drivers.build_shared_drivers_block(_shared_summary)
    if _shared_block:
        lines.extend(_shared_block)

    # Biais agrégé : ligne UNIQUE qui résume le compte de conclusions (LONG /
    # SHORT / INSUFFISANT). Le marqueur ⚠ INCOHÉRENCE n'apparaît que si le
    # compte re-calculé indépendamment diverge (bug d'agrégation).
    bias_counts = compute_bias_aggregate(results)
    bias_ok, bias_msg = assert_bias_coherence(bias_counts, results)
    bias_marker = "" if bias_ok else f" ⚠ INCOHÉRENCE : {bias_msg}"
    lines.append(
        f"- Biais agrégé : LONG {bias_counts['LONG']} · SHORT {bias_counts['SHORT']} · "
        f"INSUFFISANT {bias_counts[CONCLUSION_INSUFFISANT]} "
        f"(sur {bias_counts['total']} cellules){bias_marker}"
    )
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
                # Bloc 3 (audit UX 10/06) — drapeau ⚪/≈ sur les flips de BRUIT :
                # un flip à +0.01 (CAC/Blé le 10/06) est un quasi-coin-flip, il
                # doit le dire. Seuils EXISTANTS (⚪ |score|<0.05, ≈ <NEUTRAL_BAND).
                sc = r.scores[h]
                noise_flag = ""
                if r.conclusions[h] in ("LONG", "SHORT"):
                    if abs(sc) < 0.05:
                        noise_flag = " ⚪"
                    elif abs(sc) < NEUTRAL_BAND:
                        noise_flag = " ≈"
                flips.append(
                    f"- {r.nom} [{h}] : {v} → {r.conclusions[h]} "
                    f"(score {sc:+.2f}){noise_flag}"
                )
    lines.append("## Flips vs veille")
    if flips:
        lines.extend(flips)
    else:
        # Placeholder court pour que la section existe toujours (la sous-nav
        # HTML s'appuie sur les ## h2 — supprimer la section casserait la nav).
        lines.append("_Aucun changement de position vs veille._")
    lines.append("")
    # ── Construction des cellules (UNE PASSE) ───────────────────────────────
    # On calcule pour chaque (actif, horizon) la cellule détaillée + un repère
    # compact (direction + force) pour la "Synthèse des décisions" du haut.
    # `flags_present` accumule les symboles réellement utilisés → légende compacte.
    flags_present: set = set()
    # ⚭ dans la légende SEULEMENT si le bloc « Drivers macro partagés » est émis.
    if _shared_block:
        flags_present.add(_shared_drivers.SHARED_DRIVERS_SYMBOL)
    detail_cells: Dict[str, List[str]] = {}      # nom → [cell24, cell7j, cell1m]
    actionnables: List[ActifResult] = []
    insuffisants: List[ActifResult] = []
    for r in results:
        cells: List[str] = []
        cov_pct = coverage_pct(r.coverage)
        is_insuff_all = all(r.conclusions[h] == CONCLUSION_INSUFFISANT for h in HORIZONS)
        (insuffisants if is_insuff_all else actionnables).append(r)
        for h in HORIZONS:
            conc = r.conclusions[h]
            score = r.scores[h]
            confidence = r.confidence.get(h, "normale")
            if conc == CONCLUSION_INSUFFISANT:
                flags_present.add("🚫")
                cells.append(f"🚫 données insuff. ({cov_pct}%)")
                continue
            # ⚑ par cellule : masqué si le régime est annoncé globalement en tête
            # (anti-bruit #5.1 — 0 information répétée 12×). Sinon, conservé car
            # discriminant. La logique du gate n'est PAS modifiée, juste l'affichage.
            gate_flag = (
                " ⚑"
                if (not regime_global and any(c.is_gate and c.gate_active for c in r.criteres))
                else ""
            )
            if gate_flag:
                flags_present.add("⚑")
            tie = " (tb)" if h in r.tie_break_notes else ""
            # Pondéré : annoté UNIQUEMENT s'il DIFFÈRE du primaire (sinon = bruit).
            conc_p = r.conclusions_pond.get(h, "")
            score_p = r.scores_pond.get(h, 0.0)
            div_flag = " ⚠" if r.diverge.get(h) else ""
            if div_flag:
                flags_present.add("⚠")
            pond_differe = bool(conc_p) and (
                conc_p != conc or abs(score_p - score) >= 0.005
            )
            # Drapeau news_dominant : 📰 si abs(news)/abs(quant) > 0.5
            cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            n_tot = abs(float(cap_info.get("news_total_pm1", 0.0)))
            q_tot = abs(float(cap_info.get("quant_total_pm1", 0.0)))
            ratio_news_cell = n_tot / (q_tot + 1e-9)
            is_news = ratio_news_cell > 0.5
            news_flag = " 📰" if is_news else ""
            if is_news:
                flags_present.add("📰")
            coin_flip_flag = " ⚪" if abs(score) < 0.05 else ""
            if coin_flip_flag:
                flags_present.add("⚪")
            # ⏸ carry-forward : direction MAINTENUE sur data partielle. Prend le
            # K2 — bande quasi-neutre (SHADOW). Drapeau « ≈ » discret quand la note
            # est faible (0.05 ≤ |note| < NEUTRAL_BAND) sur une cellule actionnée :
            # rend lisible le quasi-zéro « habillé en SHORT ferme ». La conclusion
            # RESTE LONG/SHORT. Exclusif avec ⚪ (coin-flip, |note|<0.05, qui prime).
            # Calculé ici, appliqué seulement sur cellules quant actionnées (pas
            # carry/news-regime, traités plus bas avec leur propre habillage).
            # pas sur le ⚠️ générique (les deux sont en confidence "faible", mais
            # ⏸ porte l'info plus précise "direction conservée d'un cycle antérieur").
            # 📰 régime news (ticket D) : direction issue du biais news faute de
            # quant — porte une info plus précise que le ⚠️ générique, et prime
            # dessus (exclusif avec carry : le carry n'a pas pu maintenir).
            carry_flag = ""
            regime_flag = ""
            neutral_band_flag = ""  # K2 — « ≈ », posé seulement sur cellules quant normales
            if r.is_carry.get(h, False):
                carry_flag = f" ⏸ maintenu ({cov_pct}%)"
                flags_present.add("⏸")
                conf_flag = ""
            elif r.is_news_regime.get(h, False):
                regime_flag = f" 📰 régime news ({cov_pct}%)"
                flags_present.add("📰")
                conf_flag = ""
            else:
                conf_flag = f" ⚠️ conf. faible ({cov_pct}%)" if confidence == "faible" else ""
                if conf_flag:
                    flags_present.add("⚠️")
                # K2 — bande quasi-neutre (SHADOW) : direction inchangée, drapeau ≈.
                if EPSILON_CARRY <= abs(score) < NEUTRAL_BAND:
                    neutral_band_flag = " ≈"
                    flags_present.add("≈")
            # A1 (audit trio 05/06) — mono-critère dominant rendu VISIBLE.
            # La détection existait déjà (decision-log), mais le flag n'était jamais
            # affiché dans la matrice. Les 3 experts soulignent que le mono-critère
            # est un piège (« haute conviction » illusoire portée par 1 paramètre,
            # ex. EUR/USD 7j 96% sur le diff 2Y, CAC 7j sur l'OAT-Bund). On le rend
            # lisible. FLAG-ONLY : la conclusion LONG/SHORT reste inchangée.
            mono_dom_cell, _ = detect_mono_critere_dominant(r, h)
            mono_flag = " ◧" if mono_dom_cell else ""
            if mono_flag:
                flags_present.add("◧")
            div_qn_flag = " ↯" if r.divergence_quant_news.get(h, False) else ""
            if div_qn_flag:
                flags_present.add("↯")
            cmom_flag = " ⇄" if r.contre_momentum.get(h, False) else ""
            if cmom_flag:
                flags_present.add("⇄")
            incoh_flag = " ⇆" if r.incoherence_inter_horizons else ""
            if incoh_flag:
                flags_present.add("⇆")
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
            if ap_flag:
                flags_present.add("⌛")
            if denial_flag:
                flags_present.add("⊘")
            # ── Cœur de cellule ────────────────────────────────────────────
            if r.is_news_regime.get(h, False):
                # Q2 (audit trio 03/06) — RÉGIME NEWS : la direction (LONG/SHORT)
                # vient du BIAIS NEWS, pas du chiffre quant. Or le score quant peut
                # CONTREDIRE cette direction (ex. Cuivre 1m « LONG (-0.64) » =
                # illisible). On met donc la direction en tête SANS chiffre qui la
                # contredit, et on étiquette le quant explicitement : « LONG 📰
                # régime news (35%) [quant −0.64] ». La conclusion (LONG) ne change
                # pas — c'est purement l'affichage. Le `regime_flag` (📰 régime
                # news + cov%) est ajouté plus bas ; le score étiqueté est posé ici.
                core = f"{conc}{tie}{gate_flag} [quant {score:+.2f}]"
            elif is_news and pond_differe:
                # News dominante : pondéré (tempéré, plus fiable) EN TÊTE, brut
                # entre parenthèses. La direction de tête = direction pondérée.
                # Le brut (=score primaire pm1) reste affiché → parsé comme
                # score mesuré par journaliste (mesure inchangée).
                # [P-B1/I-3 audit visuel 12/06] : on ne RÉPÈTE le mot direction
                # `brut SHORT -8.24` que si la direction du brut DIFFÈRE du
                # pondéré (info utile : les deux méthodes divergent) ; sinon
                # `(brut -8.24)` (le signe du chiffre porte déjà la direction).
                brut_dir = f"{conc} " if conc != conc_p else ""
                core = f"{conc_p} {score_p:+.2f} (brut {brut_dir}{score:+.2f}){tie}{gate_flag}{news_flag}"
            elif pond_differe:
                # Hors news : on garde primaire en tête, pondéré en annotation.
                core = (
                    f"{conc} ({score:+.2f}){tie}{gate_flag} "
                    f"[pond:{conc_p} {score_p:+.2f}]{div_flag}{news_flag}"
                )
            else:
                # Pondéré identique au primaire → on n'affiche pas [pond:...].
                core = f"{conc} ({score:+.2f}){tie}{gate_flag}{news_flag}"
            # Si régime news actif, le 📰 explicite "régime news" remplace le 📰
            # générique news_dominant déjà inclus dans `core` (éviter doublon 📰).
            core_out = core.replace(news_flag, "") if (regime_flag and news_flag) else core
            cells.append(
                f"{core_out}{coin_flip_flag}{neutral_band_flag}{carry_flag}{regime_flag}{conf_flag}"
                f"{mono_flag}{div_qn_flag}{cmom_flag}{incoh_flag}{ap_flag}{denial_flag}"
            )
        detail_cells[r.nom] = cells

    # ── Synthèse des décisions (table UNIQUE, EN HAUT) ───────────────────────
    # #4.2 — Fusion : on ne garde QU'UNE table de synthèse au format riche
    # (direction + note + flags + conf%). L'ancienne table ●/○ redondante a été
    # supprimée. Le trader voit les décisions AVANT les diagnostics ; le détail
    # par critère reste plus bas (non redondant). La légende et le bloc "données
    # insuffisantes" sont rattachés à cette table.
    synth_lines: List[str] = []
    synth_lines.append("## Synthèse des décisions")
    synth_lines.append("")
    synth_lines.append("_Direction (note signée) + drapeaux + confiance%. |note| élevée = conviction forte · 📰 = news>50% du quant · 🚫 données insuffisantes. Détail par critère plus bas._")
    synth_lines.append("")
    synth_lines.append("| Actif | 24h | 7j | 1m |")
    synth_lines.append("|---|---|---|---|")
    for r in actionnables:
        c = detail_cells[r.nom]
        synth_lines.append(f"| {r.nom} | {c[0]} | {c[1]} | {c[2]} |")
    # Actifs 🚫 « données insuffisantes » regroupés (sous-table séparée, conservée).
    if insuffisants:
        synth_lines.append("")
        synth_lines.append("**Données insuffisantes (🚫, non actionnables) :**")
        synth_lines.append("")
        synth_lines.append("| Actif | 24h | 7j | 1m |")
        synth_lines.append("|---|---|---|---|")
        for r in insuffisants:
            c = detail_cells[r.nom]
            synth_lines.append(f"| {r.nom} | {c[0]} | {c[1]} | {c[2]} |")
    synth_lines.append("")
    # Raison principale par cellule — bloc compact PAR ACTIF sous la grille
    # (la grille est déjà large → lisibilité). PUR RENDU, recalculé à chaque run.
    synth_lines.extend(build_raisons_block(results, now))
    # ── Intensité comparable entre actifs (INFORMATIF, pur affichage) ─────────
    # (B) Audit Analyst : la Note brute n'est PAS comparable d'un actif à l'autre
    # (sa magnitude dépend du nombre/poids de critères couverts). On affiche EN PLUS
    # une « intensité comparable » = note ÷ Σ|poids effectif couvert| ∈ ~[-1, +1].
    # RED LINE : INFORMATIF uniquement. La Sélection du jour et toute la décision
    # restent sur la NOTE BRUTE (inchangées). Dégradation propre : « — » si 0 critère
    # couvert. Le tri/décision sur cette colonne serait une décision SÉPARÉE.
    # NB : section H2 DISTINCTE (pas H3 sous la Synthèse) → la grille de décision
    # « ## Synthèse des décisions » reste la seule table de DIRECTIONS. Cette table
    # d'intensité ne porte aucun drapeau directionnel : elle ne doit pas être lue
    # comme une cellule de grille (les parsers de flags s'arrêtent au prochain « ## »).
    synth_lines.append("")
    synth_lines.append("## Intensité comparable entre actifs (informatif)")
    synth_lines.append("")
    synth_lines.append(
        "_Note brute ÷ Σ|poids couvert| → échelle commune ~−1..+1, comparable D'UN "
        "ACTIF À L'AUTRE (la note brute ne l'est pas, sa magnitude dépend du nombre de "
        "critères actifs). **Informatif** : la Sélection et les décisions restent sur "
        "la note brute. « — » = aucun critère couvert._"
    )
    synth_lines.append("")
    synth_lines.append("| Actif | 24h | 7j | 1m |")
    synth_lines.append("|---|---|---|---|")
    for r in results:
        intens_cells: List[str] = []
        for h in HORIZONS:
            nn = compute_note_normalisee(r.criteres, r.scores[h], h)
            intens_cells.append("—" if nn is None else f"{nn:+.2f}")
        synth_lines.append(f"| {r.nom} | {intens_cells[0]} | {intens_cells[1]} | {intens_cells[2]} |")
    synth_lines.append("")
    # P2/P4/P5 — la légende des symboles + la définition de « Note » sont
    # désormais dans « ## Comment lire les scores » (fin de bulletin), une seule
    # fois. La synthèse ne garde que titre + table(s).
    # On insère la synthèse juste après le H1 + métadonnée (avant Surveillance).
    # `lines` contient déjà : H1, métadonnée, "", surveillance..., biais, flips.
    # → on la place après la dernière ligne de méta (Fraîcheur / régime extrême).
    # Anchor de fin de méta : dernière ligne de méta présente. « Généré » est
    # toujours là ; « Fraîcheur » peut être masquée (P1) → on retombe sur Généré.
    _meta_end = 0
    for i, ln in enumerate(lines):
        if (
            ln.startswith("- Généré")
            or ln.startswith("- ⚠️ Fraîcheur")
            or ln.startswith("- Fraîcheur")
            or ln.startswith("- ⚠️ Régime extrême")
        ):
            _meta_end = i + 1
    # Bloc 1 (audit UX 10/06) — « 🎯 À jouer aujourd'hui (24h) » remplace/absorbe
    # l'ancien « Top 3 convictions du jour » (qui mélangeait les horizons et
    # masquait les drapeaux). On garde un mini « Top convictions multi-horizons »
    # APRÈS, avec les drapeaux de chaque cellule + la ligne ⚭ si convergence.
    # « Sélection du jour — max 3 » EN PREMIER (décision fondateur 12/06).
    head_block = (
        build_selection_du_jour_block(
            results, now, prix_reference=prix_reference,
            shadow_capteurs=shadow_capteurs, fiches=fiches,
        )
        + build_a_jouer_block(results, now, prix_reference=prix_reference)
        + _SHADOW_CAPTEURS_NOTE
        + build_top_multi_horizons_block(results, _shared_summary)
    )
    lines = lines[:_meta_end] + [""] + head_block + synth_lines + lines[_meta_end:]

    # P2/P4/P5 — « ## Comment lire les scores » : TOUTE la pédagogie, une seule
    # fois, juste avant le détail. Les sections du jour (ci-dessus) ne gardent
    # que titre + tableau.
    lines.extend(build_comment_lire_block(flags_present))

    lines.append("## Détail par actif")
    lines.append("")
    # Encart « Comment lire ce tableau » : une seule fois, avant le 1er actif.
    lines.extend(DETAIL_TABLE_HELP_LINES)
    for r in results:
        lines.append(f"### {r.nom}")
        lines.append("")
        # Synthèse directionnelle EN TÊTE : la décision des 3 horizons (direction
        # + note signée) AVANT le tableau de critères qui la justifie. Remplace
        # l'ancienne ligne « - Scores » placée après le tableau (redondante).
        synth_h = " · ".join(
            f"{h} : {r.conclusions.get(h, '—')} ({r.scores[h]:+.2f})" for h in HORIZONS
        )
        lines.append(f"**{synth_h}**")
        lines.append("")
        lines.append("| Critère | Comment c'est lu | Valeur actuelle | Penchant | Importance | Sens | Effet 24h | Effet 7j | Effet 1m |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        # [P-B3 audit visuel 12/06] : on masque les lignes « Drapeau régime ⚑ »
        # (gate) INACTIVES — elles répétaient le même libellé sur chaque actif
        # (~10 lignes de bruit). Le gate ACTIF reste affiché EN TÊTE du tableau
        # (info de risque, fond mis en valeur via préfixe ⚑). Les autres critères
        # gardent leur ordre.
        gates_actifs_detail = [c for c in r.criteres if c.is_gate and c.gate_active]
        criteres_detail = (
            gates_actifs_detail
            + [c for c in r.criteres if not (c.is_gate and not c.gate_active)
               and c not in gates_actifs_detail]
        )
        for c in criteres_detail:
            valeur_brute_str = _fmt_raw(c.valeur_brute)
            vn = "—" if c.valeur_norm is None else f"{c.valeur_norm:+.3f}"
            poids = "—" if c.is_gate else f"{c.poids:g}"
            # Sens : texte humain (normal / inversé), — pour les gates.
            if c.is_gate:
                sens = "—"
            else:
                sens = "normal" if c.signe == 1 else "inversé"
            # [P-B2 audit visuel 12/06] : un effet quasi nul (|contrib| < 0.001,
            # ex. critère news à direction 0) s'affiche « — » plutôt que
            # « +0.000 » (zéros parasites qui polluent la lecture).
            ctr = {h: _fmt_effet(c, h) for h in HORIZONS}
            # « Comment c'est lu » : type traduit. Le gate ACTIF garde sa
            # visibilité de risque (info auparavant portée par la colonne Note).
            lu = _label_type_norm(c.type_norm)
            if c.is_gate and c.gate_active:
                lu = "⚑ **" + lu + " ACTIF**"
            lines.append(
                f"| {_nom_critere(c)} | {lu} | {valeur_brute_str} | {vn} | {poids} | {sens} | "
                f"{ctr['24h']} | {ctr['7j']} | {ctr['1m']} |"
            )
        if r.tie_break_notes:
            lines.append("")
            for h, note in r.tie_break_notes.items():
                lines.append(f"- [{h}] {note}")
        lines.append("")
    # Glossaire en pied de section « Détail par actif » (une seule fois).
    lines.extend(DETAIL_TABLE_GLOSSARY_LINES)
    # ── Limites du jour (filtrées) ──────────────────────────────────────────
    # #8 (audit design 2026-06-02) : on ne liste QUE les critères absents qui
    # comptent vraiment (poids ≥ LIMITES_POIDS_MIN). Les critères mineurs (poids
    # < seuil) sont absents des tableaux Détail aussi → on les résume en une
    # ligne « (+N critères mineurs de poids <8 omis) » par actif. Les GATES
    # actifs restent toujours affichés (info de risque, pas un n/a mineur).
    # But : passer de ~45 lignes de n/a redondants à ~10-12 lignes utiles.
    lines.append("## Limites du jour")
    has_limit = False
    for r in results:
        nas = [c for c in r.criteres if c.is_na]
        nas_majeurs = [c for c in nas if abs(c.poids) >= LIMITES_POIDS_MIN]
        n_mineurs = len(nas) - len(nas_majeurs)
        gates_actifs = [c for c in r.criteres if c.is_gate and c.gate_active]
        if nas_majeurs or gates_actifs or n_mineurs:
            has_limit = True
            lines.append(f"### {r.nom}")
            for c in nas_majeurs:
                # [P-B4 audit visuel 12/06] : « n/a : » dit déjà que la valeur
                # est absente → on n'ajoute « — {note} » que si la note porte une
                # info SUPPLÉMENTAIRE (cause précise : source DEAD, stdev=0, etc.),
                # pas la redondance générique « (valeur absente) ».
                note = c.note or ""
                detail = "" if note.strip() in ("n/a (valeur absente)", "") else f" — {note}"
                lines.append(f"- n/a : {_nom_critere(c)} (poids {c.poids:g}){detail}")
            for c in gates_actifs:
                lines.append(f"- ⚑ GATE actif : {_nom_critere(c)} — {c.note}")
            if n_mineurs:
                lines.append(
                    f"- _(+{n_mineurs} critère{'s' if n_mineurs > 1 else ''} "
                    f"mineur{'s' if n_mineurs > 1 else ''} de poids "
                    f"<{LIMITES_POIDS_MIN:g} omis)_"
                )
    if not has_limit:
        lines.append("- (aucune)")
    lines.append("")

    # ── Audit de la veille (24h — convictions fortes) ───────────────────────
    # Demande Thomas 2026-06-03 (#7) : EN FIN de bulletin, le résultat réalisé
    # des prédictions 24h de la veille pour les cellules à FORTE conviction
    # (confidence "normale" : ni faible, ni carry, ni news_regime, ni coin-flip).
    # Réutilise le mécanisme de mesure du « Bilan des news » (journaliste.measure),
    # filtré sur les cellules quant à forte conviction. Zéro invention : si le
    # réalisé n'est pas mesurable (warm-up / suivi-interrompu), la ligne est omise.
    lines.extend(build_audit_veille_24h(now))

    # ── Pied de bulletin (bloc 4) — métadonnées techniques déplacées ─────────
    # Version Analyste + hash des fiches : debug/suivi interne, sortis de la
    # tête de bulletin (audit UX 10/06, P1-D) vers une section --- discrète.
    lines.append("---")
    lines.append("")
    lines.append(
        f"_Analyste version : {ANALYSTE_VERSION} · Fiches hash : {fiches_h}_"
    )

    return "\n".join(lines)


DECISION_LOG_DIR = ROOT / "data" / "decision-log"


def build_decision_log_records(
    results: List[ActifResult],
    now: datetime,
    veille_conclusions: Optional[Dict[str, Dict[str, str]]] = None,
    shadow_capteurs: Optional[Dict[str, Dict[str, Optional[float]]]] = None,
) -> List[Dict[str, Any]]:
    """Construit la liste de lignes JSONL (une par cellule actif × horizon).

    Chaque ligne contient :
    - bulletin_date, generated_at, fiche_key, actif, horizon
    - critères contributeurs (cle_courante, valeur, valeur_normalisee, valeur_ponderee,
      poids, pertinence, materiality, reliability, source_track, facteur, contrib_pm1, contrib_pond)
    - score_pm1, score_pond, conclusion_pm1, conclusion_pond, diverge

    Étage 1b (SHADOW, decision-log only) : les records 24h portent
    `selection_du_jour` (bool) + `selection_motif_exclusion` (str, si écartée par
    la dédup driver / cap). AUCUN impact scoring/conclusion.
    Étage 2 (SHADOW) : les records 24h portent `shadow_retour_j1` et
    `shadow_gap_overnight` (None si non fournis/indisponibles). `shadow_capteurs`
    = {fiche_key: {shadow_retour_j1, shadow_gap_overnight}} (cf.
    compute_shadow_capteurs) ; None → champs à None (zéro invention).
    """
    import math as _math
    # Lot 5 C8a — import paresseux de triggers_classifier (évite couplage dur,
    # cohérent avec le pattern d'import lazy déjà en place ailleurs).
    import triggers_classifier as tc  # noqa: F401  (utilisé plus bas)
    # Reco A — drivers macro partagés (SHADOW, decision-log only). On calcule
    # l'ensemble des cle_courante partagées (≥ 2 fiches) UNE fois par run, puis
    # par cellule la liste des drivers partagés qui la portent (part ≥ seuil).
    import shared_drivers as _shared_drivers  # noqa: F401 (lazy, cf. pattern existant)
    _cles_partagees = _shared_drivers.compute_shared_cles(results, HORIZONS)
    # Étage 1b — sélection du jour (24h) : MÊME source que le bloc bulletin (1a),
    # zéro divergence affichage⇄mesure. fiche_keys retenus + motifs d'exclusion.
    _selection, _ecartees = compute_selection_du_jour(results)
    _selection_keys = {s["fiche_key"] for s in _selection}
    _motif_exclusion = {e["fiche_key"]: e["motif"] for e in _ecartees}
    shadow_capteurs = shadow_capteurs or {}
    records: List[Dict[str, Any]] = []
    bulletin_date = now.strftime("%Y-%m-%d")
    generated_at = now.isoformat()
    for r in results:
        for h in HORIZONS:
            contribs: List[Dict[str, Any]] = []
            # --- SHADOW persistance (mesure « news vit tant que le quant ne la
            #     dément pas ») : on pré-calcule le quant_total de la cellule AVANT
            #     la boucle critères pour pouvoir poser, par critère news, les flags
            #     observationnels persist_shadow_*. SOURCE DE VÉRITÉ = news_cap_info
            #     (même valeur que celle réinjectée plus bas par compute_news_bias).
            #     PUR AJOUT DE CHAMPS — aucun impact direction/score/conclusion.
            _cap_h_shadow = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            _quant_total_shadow = float(_cap_h_shadow.get("quant_total_pm1", 0.0))
            _sq_shadow = (
                1 if _quant_total_shadow > 1e-6
                else (-1 if _quant_total_shadow < -1e-6 else 0)
            )
            _PERSIST_SHADOW_HARD_DROP_DAYS = 30.0  # filet d'âge actuel (régime témoin)
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
                # --- SHADOW persistance (FLAG-ONLY, additif) -------------------
                # Mesure « news vit tant que le quant ne la dément pas » vs le
                # régime témoin « hard-drop 30j ». Posé UNIQUEMENT sur les critères
                # news (ia*/keyword). PUR AJOUT OBSERVATIONNEL : aucun de ces champs
                # n'est lu par le scoring/conclusion/mesure — ils s'accumuleront aux
                # prochains runs réels pour trancher empiriquement (cf.
                # v3/audit/persistance-shadow-mesure.md).
                _is_news_crit = (
                    c.source_track.startswith("ia") or c.source_track == "keyword"
                )
                if _is_news_crit:
                    # direction effective de la news = signe de sa contribution
                    # (fallback : signe brut du critère si contribution nulle).
                    _contrib_h = c.contributions.get(h, 0.0)
                    _sn_shadow = (
                        1 if _contrib_h > 0
                        else (-1 if _contrib_h < 0 else int(c.signe or 0))
                    )
                    _age_days = float(c.freshness_days or 0.0)
                    # quant_disconfirms : le quant de la cellule est de signe opposé
                    # à la direction de cette news (le quant dément déjà la news).
                    _quant_disconfirms = (
                        _sq_shadow != 0 and _sn_shadow != 0 and _sn_shadow == -_sq_shadow
                    )
                    # persist_shadow_alive : sous « persist-until-quant-confirms »,
                    # ce critère survivrait au-delà de 30j SSI le quant le confirme
                    # encore (ne le dément pas). En-deçà de 30j → vivant de toute
                    # façon (les deux régimes coïncident).
                    if _age_days < _PERSIST_SHADOW_HARD_DROP_DAYS:
                        _persist_alive = True
                    else:
                        _persist_alive = not _quant_disconfirms
                    # persist_shadow_blocks_flip : la news, sous persistance, resterait
                    # une voix vivante au-delà de 30j ALORS QUE le régime témoin 30j
                    # l'aurait DROP (≥30j) — et elle est DÉCISIVE pour la cellule
                    # (|contrib news| ≥ |quant_total|), donc son maintien peut figer la
                    # conclusion là où le drop l'aurait laissée suivre le quant.
                    # Conditions : âge ≥ 30j (le régime 30j la tue) ; vivante sous
                    # persistance (quant ne la dément pas) ; magnitude news ≥ quant
                    # (elle pèse assez pour tenir la conclusion). FLAG-ONLY.
                    _persist_blocks_flip = (
                        _age_days >= _PERSIST_SHADOW_HARD_DROP_DAYS
                        and _persist_alive
                        and abs(_contrib_h) >= abs(_quant_total_shadow)
                    )
                    contrib_entry["persist_shadow_age_days"] = round(_age_days, 3)
                    contrib_entry["quant_disconfirms"] = bool(_quant_disconfirms)
                    contrib_entry["persist_shadow_alive"] = bool(_persist_alive)
                    contrib_entry["persist_shadow_blocks_flip"] = bool(_persist_blocks_flip)
                contribs.append(contrib_entry)
            # --- Observabilité ratio_news (Point 4 plan horizon) ----------
            # FACTORISÉ (ticket D) : on dérive bias/ratio via compute_news_bias —
            # source de vérité UNIQUE partagée avec le gate régime news de
            # score_actif (zéro divergence possible). Les news_total/quant_total
            # retournés par le helper sont identiques aux *_pm1 de news_cap_info
            # (mêmes contributions non-na/non-gate) ; on les utilise directement.
            cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            _bias_news_h, ratio_news, news_total, quant_total = compute_news_bias(
                r.criteres, h
            )
            news_dominant = ratio_news > NEWS_DOMINANT_RATIO
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
            # M7 — PART news bornée [0,1] (fraction de la magnitude directionnelle
            #      portée par les news) = |news| / (|news| + |quant|). UNITÉ : part
            #      ∈ [0,1] (×100 = %), JAMAIS > 100%. Corrige le bug d'affichage :
            #      l'ancien M7 réutilisait `ratio_news` = |news|/|quant| (NON borné,
            #      observé jusqu'à 72.7 ≈ 7269%) — illisible en % quand la couverture
            #      quant est faible (quant_total → 0 fait exploser le ratio). Le champ
            #      DÉCISIONNEL `ratio_news` (brut, comparé à NEWS_DOMINANT_RATIO=0.5
            #      par la gate régime news) reste INCHANGÉ ci-dessous — M7 est une
            #      métrique d'OBSERVABILITÉ shadow distincte, sans impact sur le score.
            _abs_n = abs(news_total)
            _abs_q = abs(quant_total)
            p2_m7_part_news = round(_abs_n / (_abs_n + _abs_q + 1e-9), 4)
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

            # --- C7 LOT 6 — is_flip : la conclusion a-t-elle CHANGÉ vs veille ?
            # None si :
            #   - pas de veille_conclusions fournie
            #   - cellule absente de la veille
            #   - conclusion courante OU précédente == INSUFFISANT
            # True si sens différent (LONG↔SHORT). False = continuation.
            current_conc = r.conclusions.get(h, "")
            is_flip: Optional[bool] = None
            if veille_conclusions and current_conc in ("LONG", "SHORT"):
                prev = (veille_conclusions.get(r.nom.lower()) or {}).get(h)
                if prev in ("LONG", "SHORT"):
                    is_flip = (prev != current_conc)
            # K1 (SHADOW, decision-log only) — mono-critère dominant : un seul
            # critère fournit > 50% du |score| de la cellule. NE MODIFIE PAS la
            # conclusion. Sert à MESURER le sur-poids (ex. VIX régime qui flippe
            # le S&P à lui seul). Non affiché dans la matrice (anti soupe de symboles).
            mono_dominant, mono_nom = detect_mono_critere_dominant(r, h)
            # Étage 1b + 2 (SHADOW) — champs « sélection du jour » et capteurs
            # courts, posés UNIQUEMENT sur l'horizon 24h (la sélection et les
            # capteurs sont définis sur le pari 24h). AUCUN impact scoring.
            selection_extra: Dict[str, Any] = {}
            if h == "24h":
                selection_extra["selection_du_jour"] = bool(
                    r.fiche_key in _selection_keys
                )
                motif = _motif_exclusion.get(r.fiche_key)
                if motif:
                    selection_extra["selection_motif_exclusion"] = motif
                cap = shadow_capteurs.get(r.fiche_key, {})
                selection_extra["shadow_retour_j1"] = cap.get("shadow_retour_j1")
                selection_extra["shadow_gap_overnight"] = cap.get(
                    "shadow_gap_overnight"
                )
                # Chantier ③ — détecteur « choc d'offre » cacao en SHADOW (poids 0,
                # L015). Tracé au decision-log, AUCUN impact score/conclusion (cf.
                # compute_shadow_choc_offre_cacao + test-verrou conclusions). Calculé
                # UNIQUEMENT pour cacao (récit d'offre prospective spécifique) ; les
                # autres actifs n'ont pas ce champ (zéro bruit). Best-effort : toute
                # anomalie events-log → detected=False (zéro invention).
                if r.fiche_key == "cacao":
                    try:
                        selection_extra["shadow_choc_offre"] = (
                            compute_shadow_choc_offre_cacao(now=now)
                        )
                    except Exception:  # noqa: BLE001
                        selection_extra["shadow_choc_offre"] = {
                            "detected": False, "direction": 0, "n_events": 0,
                            "negators": 0, "keywords": [], "would_be_contrib": 0.0,
                        }
            records.append({
                "bulletin_date": bulletin_date,
                "generated_at": generated_at,
                # Cutover v2 : estampille la version sur les NOUVELLES entrees.
                # Les entrees passees sans ce champ = implicitement v1 (jamais
                # reecrites). Cf. system_version.py + v3/data/ref-changed.json.
                "system_version": SYSTEM_VERSION,
                "fiche_key": r.fiche_key,
                "actif": r.nom,
                "horizon": h,
                "is_flip": is_flip,
                "score_pm1": score_pm1_val,
                "score_pond": r.scores_pond.get(h, 0.0),
                # ----- Phase 2 — métriques shadow (racine) ------------------
                "p2_M1_nature_filtered_rate": round(nb_nature_filtered / n_news, 3),
                "p2_M2_stale_rate": round(nb_stale / n_news, 3),
                "p2_M3_dedup_rate": 0.0,  # calculé hors-scoring (au niveau ingest)
                "p2_M4_gate_override_blocked": bool(override_potential_blocked),
                "p2_M5_nature_composition": nature_composition,
                "p2_M6_bias": bias_long_short,
                # Part news bornée [0,1] (×100 = %), JAMAIS > 100% — voir M7 ci-dessus.
                # NB : renommé en sémantique « part », mais clé conservée pour la
                # continuité du decision-log. La valeur est désormais bornée.
                "p2_M7_ratio_news": p2_m7_part_news,
                "p2_T1_faux_flips_evites": t1_faux_flips_evites,
                "p2_T2_vrais_flips_qualifies": t2_vrais_flips_qualifies,
                # A1 — shadow contribution agrégée (sur events deja_cote/stale/repost)
                "p2_shadow_contrib_exclu": round(shadow_total_h, 6),
                "p2_shadow_flip_potential": bool(shadow_flip_potential),
                "conclusion_pm1": r.conclusions.get(h, ""),
                "conclusion_pond": r.conclusions_pond.get(h, ""),
                "diverge": bool(r.diverge.get(h, False)),
                "coin_flip": bool(abs(score_pm1_val) < 0.05),
                # A2 (audit trio 05/06) — quasi-neutre : note non-actionnable au
                # sens du trader (|note| < NEUTRAL_BAND=0.30), englobe coin_flip
                # strict ET la bande ≈. Champ shadow requêtable pour la mesure :
                # le seuil coin_flip historique (0.05) NE bouge PAS (il est couplé
                # à EPSILON_CARRY = contradiction du carry-forward, seuil décisionnel).
                # Ex. Cuivre 7j (-0.22) : coin_flip=False mais quasi_neutre=True.
                "quasi_neutre": bool(abs(score_pm1_val) < NEUTRAL_BAND),
                # K1 — mono-critère dominant (SHADOW, mesure du sur-poids).
                "mono_critere_dominant": bool(mono_dominant),
                "mono_critere_nom": mono_nom,
                # Reco A — drivers macro partagés portant cette cellule (SHADOW,
                # flag-only). Liste [{cle, part, signe}] des drivers présents dans
                # ≥ 2 fiches ET portant ≥ 50% du |score| de la cellule. Vide sinon.
                # Rend le faux consensus requêtable sans toucher score/conclusion.
                "drivers_partages": _shared_drivers.compute_cell_shared_drivers(
                    r, h, _cles_partagees
                ),
                # K2 — bande quasi-neutre (SHADOW) : True si 0.05 ≤ |note| < 0.30.
                # Direction inchangée ; tracé pour mesurer les quasi-zéros actionnés.
                "neutral_band": bool(EPSILON_CARRY <= abs(score_pm1_val) < NEUTRAL_BAND),
                # Gate suffisance de données (sécurité Thomas) :
                # coverage = même valeur pour toutes les cellules d'un actif
                # (la disponibilité brute des critères ne dépend pas de l'horizon).
                # confidence = peut varier par horizon (futurs : différents seuils
                # de coverage par horizon, ou is_stale par horizon).
                "coverage": round(r.coverage, 4),
                "confidence": r.confidence.get(h, "normale"),
                # Hystérésis de maintien : True si la direction est un carry-forward
                # (data partielle, dernière direction valide conservée — marqueur ⏸).
                "is_carry": bool(r.is_carry.get(h, False)),
                # Régime news (ticket D) : True si la direction est issue du biais
                # news (actif news-driven, couverture quant insuffisante, news
                # net & décisif) — marqueur 📰. Mutuellement exclusif avec is_carry.
                "is_news_regime": bool(r.is_news_regime.get(h, False)),
                "criteres": contribs,
                "news_total": news_total,
                "quant_total": quant_total,
                "ratio_news": ratio_news,
                "news_dominant": news_dominant,
                "news_cap_applied": bool(cap_info.get("cap_applied", False)),
                "news_cap_override": bool(cap_info.get("override_high_confirmed", False)),
                # A2 (audit momentum-family 10/06) — observabilité du cap aveugle
                # au momentum : contribution momentum (exclue de la base du cap) et
                # base de plafonnement effective (quant_total − contrib_momentum).
                "contrib_momentum": round(float(cap_info.get("contrib_momentum", 0.0)), 6),
                "cap_quant_ex_momentum": round(float(cap_info.get("cap_quant_ex_momentum", 0.0)), 6),
                **directional_flags,
                **selection_extra,
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


# ---------------------------------------------------------------------------
# Audit de la veille (24h — convictions fortes) — section bulletin (#7)
# ---------------------------------------------------------------------------

def load_conviction_map(
    bulletin_date: str,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Retrouve par cellule (actif, horizon) son profil de conviction.

    Scanne les decision-log/YYYY-MM-DD-HHMM.jsonl dont bulletin_date == date
    (le dernier run du jour écrase les précédents → reflète le bulletin final).
    Pour chaque cellule, retourne {confidence, is_carry, is_news_regime,
    coin_flip, news_dominant, ratio_news, score_pm1}. Zéro invention : si le
    dossier ou les fichiers n'existent pas → dict vide (la cellule sera ignorée).
    """
    import json as _json
    result: Dict[Tuple[str, str], Dict[str, Any]] = {}
    if not decision_log_dir.exists():
        return result
    files = sorted(decision_log_dir.glob(f"{bulletin_date}-*.jsonl"))
    if not files:
        return result
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = _json.loads(line)
                    except _json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    if rec.get("bulletin_date") != bulletin_date:
                        continue
                    actif = rec.get("actif")
                    horizon = rec.get("horizon")
                    if not actif or horizon not in HORIZONS:
                        continue
                    result[(str(actif), str(horizon))] = {
                        "confidence": rec.get("confidence"),
                        "is_carry": bool(rec.get("is_carry", False)),
                        "is_news_regime": bool(rec.get("is_news_regime", False)),
                        "coin_flip": bool(rec.get("coin_flip", False)),
                        "news_dominant": rec.get("news_dominant"),
                        "ratio_news": rec.get("ratio_news"),
                        "score_pm1": rec.get("score_pm1"),
                    }
        except OSError as e:
            logger.warning("decision-log illisible (audit veille) %s : %s", fp, e)
            continue
    return result


def _source_canonique_attendue(m, fiches: Dict[str, dict]) -> Optional[str]:
    """Source de référence CANONIQUE attendue pour la mesure `m` (fix L027).

    - actif CONTINU (or, argent, métaux, commodities, FX) → "emission" (7h, point
      d'exécution réel) ;
    - actif NON continu (indices cash, VIX) → "ouverture" (ouverture de marché).

    Réutilise `mesure_ouverture.actif_group` (source de vérité unique, zéro liste
    en dur). None si la fiche/groupe est introuvable (on n'étiquette alors rien).
    """
    fiche = fiches.get(getattr(m, "fiche_key", "")) if fiches else None
    if not fiche:
        return None
    try:
        import mesure_ouverture as _mo  # noqa: PLC0415
        groupe = _mo.actif_group(fiche)
    except Exception:  # noqa: BLE001
        return None
    if groupe is None:
        return None
    return "emission" if groupe == "continu" else "ouverture"


def build_audit_veille_24h(
    now: datetime,
    bulletins_dir: Path = BULLETINS_DIR,
    decision_log_dir: Path = DECISION_LOG_DIR,
    prix_emission_dir: Optional[Path] = None,
) -> List[str]:
    """Section « ## Audit de la veille (24h — convictions fortes) » (FIN bulletin).

    Pour chaque cellule 24h de la VEILLE qui était en confidence "normale"
    (forte conviction : ni faible, ni carry, ni news_regime, ni coin-flip,
    ni news-driven) et dont l'échéance 24h est arrivée → résultat réalisé
    (+x.xx %) + VRAI/FAUX (direction correcte ?).

    Réutilise journaliste.measure (même infra que le Bilan des news) puis
    filtre sur les cellules quant à forte conviction via le decision-log
    d'émission. Trie par |note| décroissante. Warm-up → message dédié.

    Zéro invention : si une mesure n'est pas conclusive (suivi-interrompu /
    delta indisponible) → ligne omise. Aucun chiffre fabriqué.
    """
    # Titre EXACT (bloc 2, audit UX 10/06) : l'agent build_html replie la section
    # par ce titre — NE PAS le modifier sans synchroniser build_html.py.
    lines: List[str] = ["## 🔎 Calls 24h jugés (fenêtre récente)", ""]
    placeholder = (
        "_Pas encore de cellule 24h à forte conviction arrivée à échéance._"
    )

    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import journaliste  # import paresseux : isole l'audit d'un éventuel KO
    except Exception as e:  # noqa: BLE001
        logger.warning("Audit veille 24h indisponible (import journaliste) : %s", e)
        lines.append(placeholder)
        lines.append("")
        return lines

    try:
        measure_kwargs: Dict[str, Any] = {
            "today": now.date(),
            "bulletins_dir": bulletins_dir,
        }
        if prix_emission_dir is not None:
            measure_kwargs["prix_emission_dir"] = prix_emission_dir
        measures, _ = journaliste.measure(**measure_kwargs)
    except Exception as e:  # noqa: BLE001
        # Best-effort : un fetch prix KO ne doit pas casser le bulletin.
        logger.warning("Audit veille 24h indisponible (measure_all) : %s", e)
        lines.append(placeholder)
        lines.append("")
        return lines

    OUTCOME_VRAI = getattr(journaliste, "OUTCOME_VRAI", "VRAI")
    OUTCOME_FAUSSE = getattr(journaliste, "OUTCOME_FAUSSE", "FAUSSE")

    # On ne garde que les cellules 24h conclusives (VRAI/FAUSSE) émises la VEILLE
    # (échéance 24h == aujourd'hui → bulletin_date == hier). On joint le profil
    # de conviction via le decision-log d'émission et on exclut tout ce qui
    # n'est PAS une forte conviction quant.
    conviction_cache: Dict[str, Dict[Tuple[str, str], Dict[str, Any]]] = {}
    retained: List[Tuple[float, Any]] = []  # (|note|, measure)
    for m in measures:
        if m.horizon != "24h":
            continue
        if m.outcome not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        if m.delta_pct is None:
            continue
        # « Veille » : prédiction émise hier, échue aujourd'hui.
        bdate_iso = m.cell.bulletin_date.isoformat()
        if bdate_iso not in conviction_cache:
            conviction_cache[bdate_iso] = load_conviction_map(
                bdate_iso, decision_log_dir=decision_log_dir,
            )
        prof = conviction_cache[bdate_iso].get((m.cell.actif_name, m.horizon))
        if prof is None:
            continue  # decision-log d'émission introuvable → zéro supposition
        # Forte conviction = confidence "normale" stricte ET aucun marqueur de
        # conviction dégradée (carry / news_regime / coin-flip / news-driven).
        if prof.get("confidence") != "normale":
            continue
        if prof.get("is_carry") or prof.get("is_news_regime") or prof.get("coin_flip"):
            continue
        news_dom = prof.get("news_dominant")
        ratio_news = prof.get("ratio_news")
        is_news = False
        if isinstance(news_dom, bool):
            is_news = news_dom
        elif isinstance(ratio_news, (int, float)):
            is_news = ratio_news > 50
        if is_news or m.news_driven is True:
            continue  # exclut les calls news (déjà couverts par « Bilan des news »)
        score = prof.get("score_pm1")
        note_abs = abs(float(score)) if isinstance(score, (int, float)) else abs(m.cell.score)
        retained.append((note_abs, m))

    if not retained:
        lines.append(placeholder)
        lines.append("")
        return lines

    # Tri par DATE de prédiction décroissante (bloc 2, audit UX 10/06 : les calls
    # les plus récents en tête). Départage déterministe : |note| desc, puis nom.
    retained.sort(
        key=lambda t: (t[1].cell.bulletin_date, t[0], t[1].cell.actif_name),
        reverse=True,
    )
    # [C-B3 audit visuel 12/06] : à 7h, Thomas veut les calls RÉCENTS (≈ 1
    # semaine), pas l'historique complet (l'intégral est dans la vue Historique
    # de la page). On tronque à MAX_CALLS_DISPLAYED, en gardant les plus récents
    # (la liste est triée date desc). La synthèse X✅/Y❌ porte alors sur la
    # fenêtre affichée (cohérent avec ce qui est listé).
    tronque = len(retained) > MAX_CALLS_DISPLAYED
    retained = retained[:MAX_CALLS_DISPLAYED]

    # Ligne de synthèse EN TÊTE : « X ✅ / Y ❌ (du A au B) ».
    n_vrai = sum(1 for _, m in retained if m.outcome == OUTCOME_VRAI)
    n_faux = sum(1 for _, m in retained if m.outcome == OUTCOME_FAUSSE)
    dates = [m.cell.bulletin_date for _, m in retained]
    d_min, d_max = min(dates), max(dates)
    periode = (
        f"du {d_min.isoformat()} au {d_max.isoformat()}"
        if d_min != d_max
        else f"le {d_min.isoformat()}"
    )
    suffixe_tronque = (
        f" — {MAX_CALLS_DISPLAYED} plus récents ; historique complet dans la vue Historique"
        if tronque else ""
    )
    lines.append(f"**{n_vrai} ✅ / {n_faux} ❌** ({periode}{suffixe_tronque})")
    lines.append("")

    fiches_for_tag = load_fiches()
    for _, m in retained:
        ok = m.outcome == OUTCOME_VRAI
        icon = "✅" if ok else "❌"
        verdict = "VRAI" if ok else "FAUX"
        # Étiquette « référence dégradée » : la référence de mesure n'est PAS la
        # source canonique du groupe de l'actif (fix L027). Canonique :
        #   - continu      → émission 7h (point d'exécution réel)
        #   - non continu  → ouverture de marché (CAC 9h / US 15h30)
        # Si la source réelle diffère (fallback faute de données), on le signale.
        # Champ EXISTANT du measures-log (zéro invention) ; absent → pas
        # d'étiquette (on n'affirme rien sur une provenance inconnue).
        src = getattr(m, "prix_reference_source", None)
        canonique = _source_canonique_attendue(m, fiches_for_tag)
        v1_tag = (
            " `[référence dégradée — source non canonique]`"
            if (src is not None and canonique is not None and src != canonique)
            else ""
        )
        lines.append(
            f"- {icon} **{m.cell.actif_name} 24h {m.cell.conclusion}** → "
            f"{verdict} (réel {m.delta_pct:+.2f}%) "
            f"[prédit le {m.cell.bulletin_date.isoformat()}]{v1_tag}"
        )
    lines.append("")
    return lines


# Seuil sous lequel un « Effet » (contribution par horizon) est affiché « — »
# au lieu de « +0.000 » (P-B2 audit visuel 12/06 — anti-zéros parasites).
EFFET_EPSILON: float = 0.001


def _fmt_effet(c: "CritereResult", h: str) -> str:
    """Formate la contribution d'un critère pour la colonne « Effet {h} ».

    « — » pour les gates / n.a. (pas de contribution) ET pour les effets quasi
    nuls (|contrib| < EFFET_EPSILON, ex. critère news à direction 0 → +0.000).
    Sinon le chiffre signé à 3 décimales (inchangé). Zéro impact sur le score.
    """
    if c.is_na or c.is_gate:
        return "—"
    val = c.contributions.get(h, 0.0)
    if abs(val) < EFFET_EPSILON:
        return "—"
    return f"{val:+.3f}"


def _fmt_raw(raw: Any) -> str:
    if raw is None:
        return "—"
    if isinstance(raw, dict):
        v = raw.get("valeur", raw.get("valeur_normalisee"))
        return _fmt_raw(v) if v is not None else "—"
    # bool est un sous-type d'int en Python → traité comme entier ci-dessous.
    if isinstance(raw, bool):
        return str(int(raw))
    if isinstance(raw, int):
        return str(raw)
    if isinstance(raw, float):
        # Entiers exacts (ex. 441686.0, COT en milliers) → sans décimales.
        if raw == int(raw) and abs(raw) < 1e15:
            return str(int(raw))
        # ~4 chiffres significatifs, sans notation scientifique moche.
        s = f"{raw:.4g}"
        if "e" in s or "E" in s:
            # repli : format décimal lisible (ex. 1.234e-05 → 0.00001234).
            s = f"{raw:.10f}".rstrip("0").rstrip(".")
        return s
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

    # generated_at du run courant : sert à EXCLURE le snapshot courant lors du
    # scan carry-forward (cohérent avec build_decision_log_records qui utilise
    # now.isoformat()). Le decision-log courant n'est pas encore écrit ici (run()
    # le fait après le bulletin via build_bulletin pipeline), mais on l'exclut par
    # sécurité au cas où un run serait rejoué dans la même minute.
    current_generated_at = now.isoformat()
    results: List[ActifResult] = []
    for key, fiche in fiches.items():
        valeurs = data.get(key, {}) or {}
        nom_lower = fiche.get("actif", key).lower()
        veille_for_actif = veille_conclusions.get(nom_lower, {})
        results.append(score_actif(
            key, fiche, valeurs, veille_for_actif,
            now=now,
            log_dir=DECISION_LOG_DIR,
            current_generated_at=current_generated_at,
        ))

    fhash = fiches_hash(fiches)
    # Prix de référence pour « 🎯 À jouer aujourd'hui (24h) » (bloc 1) : prix
    # d'émission STAMPÉ du créneau courant, mappé par fiche_key. Best-effort —
    # au run 7h, le stamp n'existe pas encore (il est posé APRÈS le bulletin par
    # run_bulletin.stamp_prix_emission) → map vide → colonne « — » (zéro
    # invention). Sur un re-render ultérieur (stamp présent), les prix s'affichent.
    prix_reference: Dict[str, float] = {}
    stamped: Dict[str, float] = {}
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import journaliste as _journ  # noqa: F401
        bulletin_id = f"{now:%Y-%m-%d}-{now:%H}h"
        stamped = _journ.load_prix_emission(bulletin_id) or {}  # {ticker: prix}
        for key, fiche in fiches.items():
            ticker = fiche.get("ticker_principal")
            if ticker and ticker in stamped:
                prix_reference[key] = stamped[ticker]
    except Exception as e:  # noqa: BLE001 — l'absence de prix ne casse pas le bulletin
        logger.warning("prix de référence À jouer indisponible : %s", e)

    # VOLET B — capteurs courts shadow (gap overnight) pour le drapeau ⚠️
    # contre-sens des actifs continus. Au run 7h le stamp n'existe pas encore
    # (prix_reference vide) → on alimente le prix d'émission par un fetch LIVE des
    # tickers (même source que le stamp) pour que le gap soit calculable. Best-
    # effort intégral : indispo → shadow_capteurs vide → aucun drapeau (no-op).
    shadow_capteurs_for_render: Dict[str, Dict[str, Optional[float]]] = {}
    try:
        prix_emission_live: Dict[str, float] = dict(stamped)
        if not prix_emission_live:
            import criteres_calculator as _cc_live  # noqa: F811
            for _k, _f in fiches.items():
                _tk = _f.get("ticker_principal")
                if not _tk or _tk in prix_emission_live:
                    continue
                try:
                    _px = _cc_live.fetch_twelve_price(_tk)
                except Exception:  # noqa: BLE001
                    _px = None
                if isinstance(_px, (int, float)):
                    prix_emission_live[_tk] = float(_px)
        shadow_capteurs_for_render = compute_shadow_capteurs(
            fiches, prix_emission=prix_emission_live,
        )
        # P9 — BUG WIRING : au run 7h le stamp n'existe pas encore (posé APRÈS par
        # run_bulletin) → `prix_reference` vide → colonne « Prix de réf. » = « — ».
        # Or `prix_emission_live` (fetch live, déjà construit ci-dessus pour les
        # capteurs shadow) PORTE les prix. Si `prix_reference` est vide, on
        # l'alimente depuis le live via le MÊME mapping ticker→fiche_key que le
        # stamp. Best-effort, jamais de crash, zéro invention (vrais prix).
        if not prix_reference and prix_emission_live:
            for key, fiche in fiches.items():
                ticker = fiche.get("ticker_principal")
                if ticker and ticker in prix_emission_live:
                    prix_reference[key] = prix_emission_live[ticker]
    except Exception as e:  # noqa: BLE001
        logger.warning("capteurs shadow (drapeau contre-sens) indispo : %s", e)

    content = render_bulletin(
        results, veille_conclusions, now, fhash, fresh_msg,
        prix_reference=prix_reference,
        shadow_capteurs=shadow_capteurs_for_render,
        fiches=fiches,
    )
    # Un fichier distinct par créneau (3 runs/jour). Le créneau est l'HEURE DE
    # PARIS du run, zéro-paddée (ex. bulletin-2026-06-05-18h.md pour un run 18h04
    # Paris). On utilise `now` (Europe/Paris) — la MÊME source d'heure que le
    # titre du bulletin (« HHhMM (Paris) ») et que le decision-log (HHMM Paris),
    # pour garantir la cohérence nom de fichier ⇄ titre ⇄ decision-log.
    # Historique : avant le 05/06 le nom utilisait l'heure UTC (bug d'affichage)
    # → le fichier disait 16h alors que le titre disait 18h04. Les bulletins
    # déjà produits ne sont PAS renommés (rétro-compat lecture/tri par stem).
    # Sans le créneau, chaque run écraserait le bulletin du jour → seul le run du
    # soir survivrait (biais de survie + perte de mesure pour matin/midi).
    out_path = bulletins_dir / f"bulletin-{now:%Y-%m-%d}-{now:%H}h.md"
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
