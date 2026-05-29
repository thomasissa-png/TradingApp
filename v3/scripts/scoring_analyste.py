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


@dataclass
class ActifResult:
    nom: str
    fiche_key: str
    criteres: List[CritereResult]
    scores: Dict[str, float]
    conclusions: Dict[str, str]
    tie_break_notes: Dict[str, str]


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
) -> Tuple[str, str]:
    """Tie-break Analyste §5.2.

    1. Majorité des 3 critères les plus pesants (|poids|) → 2/3 LONG ⇒ LONG.
    2. Égalité 3-3 ⇒ reconduire la conclusion de la veille.
    3. Aucune veille ⇒ LONG par défaut.
    """
    actifs = [c for c in criteres if not c.is_na and not c.is_gate and c.valeur_norm is not None]
    top3 = sorted(actifs, key=lambda c: abs(c.poids), reverse=True)[:3]
    if len(top3) == 0:
        return "LONG", "tie-break: aucun critère actif → LONG par défaut"
    votes_long = sum(1 for c in top3 if c.contributions.get(horizon, 0.0) > 0)
    votes_short = sum(1 for c in top3 if c.contributions.get(horizon, 0.0) < 0)
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
        contributions: Dict[str, float] = {}
        if not is_na and not is_gate and valeur_norm is not None:
            for h in HORIZONS:
                contributions[h] = valeur_norm * poids * pertinence[h] * signe
        else:
            for h in HORIZONS:
                contributions[h] = 0.0
        gate_active = False
        if is_gate:
            if isinstance(raw, dict):
                gate_active = bool(raw.get("valeur"))
            else:
                gate_active = bool(raw)
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
            )
        )

    scores: Dict[str, float] = {}
    conclusions: Dict[str, str] = {}
    tie_notes: Dict[str, str] = {}
    for h in HORIZONS:
        scores[h] = round(sum(c.contributions[h] for c in criteres_res), 6)
        conc = _conclusion_from_score(scores[h])
        if conc is None:
            conc, note = tie_break(criteres_res, h, veille_conclusions.get(h))
            tie_notes[h] = note
        conclusions[h] = conc

    return ActifResult(
        nom=fiche.get("actif", fiche_key),
        fiche_key=fiche_key,
        criteres=criteres_res,
        scores=scores,
        conclusions=conclusions,
        tie_break_notes=tie_notes,
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
    lines.append("## Matrice (12 actifs × 3 horizons)")
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
            cells.append(f"{conc} ({score:+.2f}){tie}{gate_flag}")
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
