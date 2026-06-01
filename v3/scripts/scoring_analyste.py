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
) -> ActifResult:
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
        contributions: Dict[str, float] = {}
        contributions_pond: Dict[str, float] = {}
        if not is_na and not is_gate and valeur_norm is not None:
            for h in HORIZONS:
                contributions[h] = valeur_norm * poids * pertinence[h] * signe
                vp = valeur_ponderee if valeur_ponderee is not None else valeur_norm
                contributions_pond[h] = vp * poids * pertinence[h] * signe
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
        if isinstance(raw, dict):
            mat = str(raw.get("materiality", "") or "")
            rel = str(raw.get("reliability", "") or "")
            src_track = str(raw.get("source_track", "") or "")
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
        # Override : un critère news high+confirmed sur CET horizon ⇒ pas de cap.
        # TODO Phase 2 : raffiner avec fraîcheur ≤48h + type=structurel (cf. plan horizon).
        override = any(
            c.source_track.startswith("ia")
            and c.materiality == "high"
            and c.reliability == "confirmed"
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
        conc = _conclusion_from_score(scores[h])
        if conc is None:
            conc, note = tie_break(criteres_res, h, veille_conclusions.get(h))
            tie_notes[h] = note
        conclusions[h] = conc
        # --- Pondéré (secondaire, loggé) ----------------------------------
        scores_pond[h] = round(quant_total_p + news_total_capped_p, 6)
        conc_p = _conclusion_from_score(scores_pond[h])
        if conc_p is None:
            conc_p, note_p = tie_break(criteres_res, h, veille_conclusions.get(h), use_pond=True)
            tie_notes_pond[h] = note_p
        conclusions_pond[h] = conc_p
        diverge[h] = (conclusions[h] != conclusions_pond[h])

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
    lines: List[str] = []
    lines.append(f"# Bulletin Analyste — {now:%Y-%m-%d}")
    lines.append("")
    lines.append(f"- Généré : {now.isoformat()}")
    lines.append(f"- Analyste version : {ANALYSTE_VERSION}")
    lines.append(f"- Fiches hash : {fiches_h}")
    lines.append(f"- Fraîcheur : {freshness_msg}")
    lines.append("")
    lines.append("## Matrice (12 actifs × 3 horizons) — primaire ±1, pondéré en annotation")
    lines.append("")
    lines.append("| Actif | 24h | 7j | 1m |")
    lines.append("|---|---|---|---|")
    flips: List[str] = []
    for r in results:
        cells = []
        for h in HORIZONS:
            conc = r.conclusions[h]
            score = r.scores[h]
            gate_flag = " ⚑" if any(c.is_gate and c.gate_active for c in r.criteres) else ""
            tie = " (tb)" if h in r.tie_break_notes else ""
            # Annotation pondérée (secondaire) + ⚠ si divergence
            conc_p = r.conclusions_pond.get(h, "")
            score_p = r.scores_pond.get(h, 0.0)
            div_flag = " ⚠" if r.diverge.get(h) else ""
            pond_str = f" [pond:{conc_p} {score_p:+.2f}]{div_flag}" if conc_p else ""
            # Drapeau news_dominant (Point 4) : 📰 si abs(news)>50% abs(quant)
            cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            n_tot = abs(float(cap_info.get("news_total_pm1", 0.0)))
            q_tot = abs(float(cap_info.get("quant_total_pm1", 0.0)))
            news_flag = " 📰" if (n_tot / (q_tot + 1e-9)) > 0.5 else ""
            cells.append(f"{conc} ({score:+.2f}){tie}{gate_flag}{pond_str}{news_flag}")
        lines.append(f"| {r.nom} | {cells[0]} | {cells[1]} | {cells[2]} |")
        veille = veille_conclusions.get(r.nom.lower(), {})
        for h in HORIZONS:
            v = veille.get(h)
            if v and v != r.conclusions[h]:
                flips.append(f"- {r.nom} [{h}] : {v} → {r.conclusions[h]} (score {r.scores[h]:+.2f})")
    lines.append("")
    lines.append("## Flips vs veille")
    if flips:
        lines.extend(flips)
    else:
        lines.append("- (aucun)")
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
                contribs.append({
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
                })
            # --- Observabilité ratio_news (Point 4 plan horizon) ----------
            cap_info = r.news_cap_info.get(h, {}) if r.news_cap_info else {}
            news_total = float(cap_info.get("news_total_pm1", 0.0))
            quant_total = float(cap_info.get("quant_total_pm1", 0.0))
            ratio_news = abs(news_total) / (abs(quant_total) + 1e-9)
            news_dominant = ratio_news > 0.5
            records.append({
                "bulletin_date": bulletin_date,
                "generated_at": generated_at,
                "fiche_key": r.fiche_key,
                "actif": r.nom,
                "horizon": h,
                "score_pm1": r.scores.get(h, 0.0),
                "score_pond": r.scores_pond.get(h, 0.0),
                "conclusion_pm1": r.conclusions.get(h, ""),
                "conclusion_pond": r.conclusions_pond.get(h, ""),
                "diverge": bool(r.diverge.get(h, False)),
                "criteres": contribs,
                "news_total": news_total,
                "quant_total": quant_total,
                "ratio_news": ratio_news,
                "news_dominant": news_dominant,
                "news_cap_applied": bool(cap_info.get("cap_applied", False)),
                "news_cap_override": bool(cap_info.get("override_high_confirmed", False)),
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
