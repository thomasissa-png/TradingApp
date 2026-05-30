"""TradingApp v3 — Le Journaliste (mesure de qualité prédictive).

Mesure, à chaque run, la qualité des conclusions passées du bulletin de
l'Analyste. Pour chaque cellule actif × horizon (24h / 7j / 1m), compare le
prix d'émission (stocké au moment du bulletin) au prix courant (Twelve Data)
et marque la conclusion :

- VRAI            : |delta cours| > seuils_reussite_pct[horizon] DANS le sens prédit
- FAUSSE          : |delta cours| > seuil DANS LE SENS OPPOSÉ
- non-conclusive  : |delta| ≤ seuil (mouvement insuffisant)
- suivi-interrompu: prix d'émission ou prix courant indisponible (red line :
                    JAMAIS de mesure inventée, retry au prochain run)

KPI par cellule sur les 30 dernières conclusions terminées :
- taux de réussite (%) = VRAI / (VRAI + FAUSSE)  [non-conclusive et
  suivi-interrompu EXCLUS du dénominateur, cf. Bourse.md]
- Brier score = mean((proba - outcome)²) avec
  proba = 0.5 + clip(score / PROBA_SCALE, -0.5, 0.5)
  outcome = 1 si VRAI, 0 si FAUSSE (cellules non-conclusives exclues)
- distribution LONG / SHORT (alerte si hors [30 %, 70 %])

Statuts :
- éligible_actif  : taux ≥ 70 % (Bourse.md target)
- shadow          : taux < 70 % OU pas encore 30 conclusions terminées

Sortie : `v3/data/performance.md` (regénéré à chaque run).

Red lines :
- Twelve Data injoignable          → conclusion `suivi-interrompu`, retry
- prix d'émission absent            → conclusion `suivi-interrompu`, retry
- JAMAIS d'invention de prix ou outcome

Stockage du prix d'émission :
- À chaque écriture d'un bulletin (`run_bulletin`), appeler
  `stamp_prix_emission(bulletin_date)` : récupère le prix courant de chaque
  actif (ticker_principal de la fiche) via Twelve Data et l'écrit dans
  `v3/data/prix-emission/YYYY-MM-DD.json` ({ticker: prix}). Idempotent : si
  un ticker est déjà stampé pour cette date et que le nouveau fetch échoue,
  l'ancien est préservé.
"""

from __future__ import annotations

import json
import logging
import math as _math
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import yaml

logger = logging.getLogger("journaliste")

JOURNALISTE_VERSION = "v3.1.0"
HORIZONS: Tuple[str, ...] = ("24h", "7j", "1m")
HORIZON_DAYS: Dict[str, int] = {"24h": 1, "7j": 7, "1m": 30}
WINDOW = 30                  # KPI sur 30 dernières conclusions terminées
PROBA_SCALE = 10.0           # score / PROBA_SCALE pour dériver la proba (param documenté)
TARGET_TAUX = 70.0           # seuil éligibilité (Bourse.md)
DISTRIB_MIN = 30.0           # alerte distribution LONG/SHORT hors [30, 70] %
DISTRIB_MAX = 70.0

# ---------------------------------------------------------------------------
# Paramètres statistiques rigoureux (audit-data §1 §2 §3)
# ---------------------------------------------------------------------------
# Pas non-chevauchant (en jours ouvrés) pour l'échantillonnage indépendant.
# On utilise des jours calendaires car les bulletins peuvent couvrir des horizons
# calendaires, mais on approxime : 7j → step 5 jours ouvrés ≈ 7j calendaires.
NON_OVERLAP_STEP: Dict[str, int] = {"24h": 1, "7j": 7, "1m": 30}

# Seuil Wilson : borne basse IC à 95 % doit dépasser ce niveau pour éligibilité.
WILSON_LOW_THRESHOLD = 0.50   # borne basse > 50 % exigée pour éligibilité non-chevauchante

# Nombre minimum d'observations non-chevauchantes pour avoir un statut défini
# (en dessous → warm-up, pas d'éligibilité). Aligné avec KILL-CRITERION.md.
N_EFFECTIVE_MIN = 15          # warm-up si n_effective < 15 (aligné kill-criterion N>=15)
N_EFFECTIVE_KILL = 15         # seuil kill criterion (KILL-CRITERION.md §2 condition 2)

# Critère global multiple-testing : fraction de cellules < 55 % autorisée
GLOBAL_MIN_TAUX = 55.0        # taux global minimum (kill criterion condition 1)
MAX_CELLS_BELOW_55 = 0.40     # alerte si > 40 % des cellules ont taux < 55 %

# Calibration ECE
CALIB_N_BINS = 5              # bins pour reliability diagram (ECE)

ROOT = Path(__file__).resolve().parents[1]
FICHES_DIR = ROOT / "config" / "fiches"
BULLETINS_DIR = ROOT / "data" / "bulletins"
PRIX_EMISSION_DIR = ROOT / "data" / "prix-emission"
PERFORMANCE_FILE = ROOT / "data" / "performance.md"
PERFORMANCE_AB_FILE = ROOT / "data" / "performance-ab.md"
CALIBRATION_FILE = ROOT / "data" / "calibration.md"


# ---------------------------------------------------------------------------
# Helpers fichiers / fiches
# ---------------------------------------------------------------------------

def load_fiches(fiches_dir: Path = FICHES_DIR) -> Dict[str, dict]:
    fiches: Dict[str, dict] = {}
    if not fiches_dir.exists():
        return fiches
    for f in sorted(fiches_dir.glob("*.yml")):
        try:
            with f.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except Exception as e:  # noqa: BLE001
            logger.warning("Fiche illisible %s : %s", f.name, e)
            continue
        if isinstance(data, dict) and "ticker_principal" in data:
            fiches[f.stem] = data
    return fiches


def fiche_for_actif_name(fiches: Dict[str, dict], actif_name: str) -> Optional[Tuple[str, dict]]:
    """Retrouve la fiche pour un nom d'actif lu dans un bulletin."""
    name_lower = actif_name.strip().lower()
    for key, fiche in fiches.items():
        if fiche.get("actif", "").strip().lower() == name_lower:
            return key, fiche
        if key.lower() == name_lower:
            return key, fiche
    return None


# ---------------------------------------------------------------------------
# Parsing bulletin
# ---------------------------------------------------------------------------

# Matrice "| Actif | LONG (+0.42) ... | SHORT (-1.20) (tb) | LONG (+0.00) ⚑ |"
MATRIX_LINE_RE = re.compile(
    r"^\|\s*(?P<actif>[^|]+?)\s*\|"
    r"\s*(?P<c24>LONG|SHORT)\s*\((?P<s24>[+-]?\d+(?:\.\d+)?)\)[^|]*\|"
    r"\s*(?P<c7>LONG|SHORT)\s*\((?P<s7>[+-]?\d+(?:\.\d+)?)\)[^|]*\|"
    r"\s*(?P<c1>LONG|SHORT)\s*\((?P<s1>[+-]?\d+(?:\.\d+)?)\)[^|]*\|",
    re.MULTILINE,
)
# Annotation pondérée optionnelle : "[pond:LONG +0.42]"
POND_ANNOT_RE = re.compile(r"\[pond:(LONG|SHORT)\s+([+-]?\d+(?:\.\d+)?)\]")
BULLETIN_FILE_RE = re.compile(r"^bulletin-(\d{4}-\d{2}-\d{2})\.md$")


@dataclass
class BulletinCell:
    bulletin_date: date
    actif_name: str          # tel que lu dans le bulletin
    horizon: str             # "24h" / "7j" / "1m"
    conclusion: str          # "LONG" / "SHORT" (baseline ±1)
    score: float
    # Pondéré (v3.1) — None si bulletin antérieur ne contient pas l'annotation
    conclusion_pond: Optional[str] = None
    score_pond: Optional[float] = None


def parse_bulletin(path: Path) -> List[BulletinCell]:
    """Extrait toutes les cellules (actif × horizon) d'un bulletin."""
    m = BULLETIN_FILE_RE.match(path.name)
    if not m:
        return []
    try:
        bdate = date.fromisoformat(m.group(1))
    except ValueError:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    cells: List[BulletinCell] = []
    for mm in MATRIX_LINE_RE.finditer(text):
        actif = mm.group("actif").strip()
        # Découpe la ligne complète en cellules markdown pour extraire l'annotation pondérée
        # par cellule (re-split sur '|', on garde les 3 dernières cellules après l'actif).
        line = mm.group(0)
        raw_cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Format attendu : [actif, cell24, cell7, cell1] → 4 entrées
        cell_texts = raw_cells[1:4] if len(raw_cells) >= 4 else ["", "", ""]
        for h, conc_key, score_key, idx in (
            ("24h", "c24", "s24", 0),
            ("7j", "c7", "s7", 1),
            ("1m", "c1", "s1", 2),
        ):
            try:
                score = float(mm.group(score_key))
            except (TypeError, ValueError):
                continue
            conc_pond: Optional[str] = None
            score_pond: Optional[float] = None
            if idx < len(cell_texts):
                mp = POND_ANNOT_RE.search(cell_texts[idx])
                if mp:
                    conc_pond = mp.group(1)
                    try:
                        score_pond = float(mp.group(2))
                    except (TypeError, ValueError):
                        score_pond = None
            cells.append(
                BulletinCell(
                    bulletin_date=bdate,
                    actif_name=actif,
                    horizon=h,
                    conclusion=mm.group(conc_key),
                    score=score,
                    conclusion_pond=conc_pond,
                    score_pond=score_pond,
                )
            )
    return cells


def list_bulletins(bulletins_dir: Path = BULLETINS_DIR) -> List[Path]:
    if not bulletins_dir.exists():
        return []
    return sorted(bulletins_dir.glob("bulletin-*.md"))


# ---------------------------------------------------------------------------
# Prix d'émission (stamp + lecture)
# ---------------------------------------------------------------------------

def prix_emission_path(d: date, base_dir: Path = PRIX_EMISSION_DIR) -> Path:
    return base_dir / f"{d.isoformat()}.json"


def load_prix_emission(d: date, base_dir: Path = PRIX_EMISSION_DIR) -> Dict[str, float]:
    p = prix_emission_path(d, base_dir)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("prix-emission illisible %s : %s", p, e)
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, float] = {}
    for k, v in data.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def stamp_prix_emission(
    bulletin_date: date,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    base_dir: Path = PRIX_EMISSION_DIR,
) -> Path:
    """Stamp le prix courant de chaque actif pour le bulletin de `bulletin_date`.

    - fiches : si None, chargées depuis FICHES_DIR
    - fetch_price : callable(ticker) -> Optional[float] (injecté en tests).
      Par défaut, importe criteres_calculator.fetch_twelve_price.
    - Idempotent : si le fichier existe déjà, fusionne (préserve les anciens
      prix si le nouveau fetch échoue).
    """
    fiches = fiches if fiches is not None else load_fiches()
    if fetch_price is None:
        # Lazy import pour ne pas dépendre de requests en test
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import criteres_calculator  # noqa: E402
        fetch_price = criteres_calculator.fetch_twelve_price

    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = prix_emission_path(bulletin_date, base_dir)
    existing = load_prix_emission(bulletin_date, base_dir)
    stamped: Dict[str, float] = dict(existing)

    for fiche_key, fiche in fiches.items():
        ticker = fiche.get("ticker_principal")
        if not ticker:
            continue
        if ticker in stamped:
            # déjà stampé pour cette date (idempotence)
            continue
        try:
            price = fetch_price(ticker)
        except Exception as e:  # noqa: BLE001
            logger.warning("stamp prix %s : exception %s", ticker, e)
            price = None
        if price is None:
            logger.warning("stamp prix %s : indisponible (suivi-interrompu)", ticker)
            continue
        try:
            stamped[ticker] = float(price)
        except (TypeError, ValueError):
            continue

    out_path.write_text(
        json.dumps(stamped, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    logger.info("Prix d'émission stampés %s : %d tickers", out_path, len(stamped))
    return out_path


# ---------------------------------------------------------------------------
# Mesure d'une cellule (VRAI / FAUSSE / non-conclusive / suivi-interrompu)
# ---------------------------------------------------------------------------

OUTCOME_VRAI = "VRAI"
OUTCOME_FAUSSE = "FAUSSE"
OUTCOME_NC = "non-conclusive"
OUTCOME_INTERROMPU = "suivi-interrompu"


@dataclass
class Measure:
    cell: BulletinCell
    fiche_key: str
    ticker: str
    horizon: str
    echeance: date
    prix_emission: Optional[float]
    prix_courant: Optional[float]
    seuil_pct: Optional[float]
    delta_pct: Optional[float]
    outcome: str
    note: str = ""
    # A/B : outcome pondéré (None si bulletin sans annotation pondérée)
    outcome_pond: Optional[str] = None


def measure_cell(
    cell: BulletinCell,
    fiche_key: str,
    fiche: dict,
    prix_emission: Optional[float],
    prix_courant: Optional[float],
) -> Measure:
    ticker = fiche.get("ticker_principal", "")
    seuils = fiche.get("seuils_reussite_pct") or {}
    seuil_raw = seuils.get(cell.horizon)
    try:
        seuil = float(seuil_raw) if seuil_raw is not None else None
    except (TypeError, ValueError):
        seuil = None
    echeance = cell.bulletin_date + timedelta(days=HORIZON_DAYS[cell.horizon])

    base = Measure(
        cell=cell,
        fiche_key=fiche_key,
        ticker=ticker,
        horizon=cell.horizon,
        echeance=echeance,
        prix_emission=prix_emission,
        prix_courant=prix_courant,
        seuil_pct=seuil,
        delta_pct=None,
        outcome=OUTCOME_INTERROMPU,
    )

    if prix_emission is None or prix_emission == 0:
        base.note = "prix d'émission indisponible"
        return base
    if prix_courant is None:
        base.note = "prix courant indisponible (Twelve Data)"
        return base
    if seuil is None:
        base.outcome = OUTCOME_INTERROMPU
        base.note = f"seuil manquant dans la fiche pour {cell.horizon}"
        return base

    delta_pct = (prix_courant - prix_emission) / prix_emission * 100.0
    base.delta_pct = delta_pct
    abs_delta = abs(delta_pct)

    if abs_delta <= seuil:
        base.outcome = OUTCOME_NC
        base.note = f"|delta|={abs_delta:.3f}% ≤ seuil={seuil}%"
        return base

    # mouvement > seuil : VRAI si dans le sens prédit, sinon FAUSSE
    if cell.conclusion == "LONG":
        base.outcome = OUTCOME_VRAI if delta_pct > 0 else OUTCOME_FAUSSE
    elif cell.conclusion == "SHORT":
        base.outcome = OUTCOME_VRAI if delta_pct < 0 else OUTCOME_FAUSSE
    else:
        base.outcome = OUTCOME_INTERROMPU
        base.note = f"conclusion inconnue : {cell.conclusion}"
        return base

    base.note = f"delta={delta_pct:+.3f}% vs seuil={seuil}%"

    # --- A/B : outcome pondéré (même delta, conclusion différente possible) ---
    if cell.conclusion_pond in ("LONG", "SHORT"):
        if abs_delta <= seuil:
            base.outcome_pond = OUTCOME_NC
        elif cell.conclusion_pond == "LONG":
            base.outcome_pond = OUTCOME_VRAI if delta_pct > 0 else OUTCOME_FAUSSE
        else:  # SHORT
            base.outcome_pond = OUTCOME_VRAI if delta_pct < 0 else OUTCOME_FAUSSE
    # Sinon : bulletin antérieur sans annotation pondérée → outcome_pond reste None.

    return base


# ---------------------------------------------------------------------------
# Agrégation KPI par cellule (actif × horizon)
# ---------------------------------------------------------------------------

@dataclass
class CellKPI:
    fiche_key: str
    actif_name: str
    horizon: str
    n_total: int = 0          # mesures terminées (VRAI + FAUSSE + non-conclusive) — brutes chevauchantes
    n_vrai: int = 0
    n_fausse: int = 0
    n_nc: int = 0
    n_long: int = 0
    n_short: int = 0
    brier_sum: float = 0.0
    brier_n: int = 0
    interrompus_recents: int = 0
    taux_pct: Optional[float] = None           # taux brut (chevauchant) — indicatif
    brier: Optional[float] = None
    distrib_long_pct: Optional[float] = None
    distrib_short_pct: Optional[float] = None
    statut: str = "shadow"
    alertes: List[str] = field(default_factory=list)
    # --- Correction #1 : non-chevauchant ---
    n_effective: int = 0                       # nb obs non-chevauchantes
    n_vrai_eff: int = 0
    n_fausse_eff: int = 0
    taux_eff_pct: Optional[float] = None       # taux non-chevauchant (décisionnel)
    # --- Correction #2 : Wilson IC + critère global ---
    wilson_low: Optional[float] = None         # borne basse IC Wilson 95 % (sur n_effective)
    wilson_high: Optional[float] = None        # borne haute IC Wilson 95 %


def wilson_ci(n_success: int, n_total: int, z: float = 1.96) -> Tuple[float, float]:
    """Intervalle de confiance de Wilson (proportion) à z-sigma (défaut z=1.96 → 95 %).

    Formule : (p̂ + z²/2n ± z*sqrt(p̂(1-p̂)/n + z²/4n²)) / (1 + z²/n)

    Retourne (borne_basse, borne_haute) ∈ [0, 1].
    Retourne (0.0, 1.0) si n_total <= 0 (indéfini).
    """
    if n_total <= 0:
        return (0.0, 1.0)
    p_hat = n_success / n_total
    z2 = z * z
    centre = p_hat + z2 / (2 * n_total)
    margin = z * _math.sqrt(p_hat * (1 - p_hat) / n_total + z2 / (4 * n_total * n_total))
    denom = 1 + z2 / n_total
    low = max(0.0, (centre - margin) / denom)
    high = min(1.0, (centre + margin) / denom)
    return (round(low, 4), round(high, 4))


def select_non_overlapping(
    measures: List["Measure"],
    horizon: str,
    step_days: Optional[int] = None,
) -> List["Measure"]:
    """Retourne un sous-ensemble NON-CHEVAUCHANT de mesures terminées (VRAI ou FAUSSE).

    Stratégie : fenêtre glissante — on prend la 1ère mesure terminée disponible,
    puis la suivante dont l'échéance est ≥ echeance_précédente + step_days.
    Les non-conclusives sont exclues (elles n'entrent pas dans le taux de réussite).

    step_days : si None, utilise NON_OVERLAP_STEP[horizon] (défaut sécurisé).
    """
    step = step_days if step_days is not None else NON_OVERLAP_STEP.get(horizon, 1)
    # Tri par échéance croissante (ordre temporel)
    terminées = sorted(
        [m for m in measures if m.outcome in (OUTCOME_VRAI, OUTCOME_FAUSSE)],
        key=lambda m: m.echeance,
    )
    selected: List["Measure"] = []
    last_echeance: Optional[date] = None
    for m in terminées:
        if last_echeance is None or (m.echeance - last_echeance).days >= step:
            selected.append(m)
            last_echeance = m.echeance
    return selected


def proba_from_score(score: float, conclusion: str, scale: float = PROBA_SCALE) -> float:
    """Dérive une proba ∈ [0, 1] que la conclusion soit VRAIE.

    proba = 0.5 + clip(|score| / scale, 0, 0.5)
    (le score signe est déjà cohérent avec la conclusion : score>0 ⇒ LONG, score<0 ⇒ SHORT)
    """
    if scale <= 0:
        return 0.5
    raw = abs(score) / scale
    if raw > 0.5:
        raw = 0.5
    return 0.5 + raw


def compute_kpi(measures_for_cell: List[Measure]) -> CellKPI:
    """measures_for_cell triée par échéance asc, on garde les WINDOW dernières
    terminées (hors suivi-interrompu) pour les KPI."""
    if not measures_for_cell:
        return CellKPI(fiche_key="", actif_name="", horizon="")

    fiche_key = measures_for_cell[0].fiche_key
    actif_name = measures_for_cell[0].cell.actif_name
    horizon = measures_for_cell[0].horizon
    kpi = CellKPI(fiche_key=fiche_key, actif_name=actif_name, horizon=horizon)

    interrompus = [m for m in measures_for_cell if m.outcome == OUTCOME_INTERROMPU]
    kpi.interrompus_recents = len(interrompus)

    terminees = [m for m in measures_for_cell if m.outcome != OUTCOME_INTERROMPU]
    window = terminees[-WINDOW:]
    kpi.n_total = len(window)
    if not window:
        kpi.alertes.append("aucune mesure terminée dans la fenêtre")
        return kpi

    for m in window:
        if m.outcome == OUTCOME_VRAI:
            kpi.n_vrai += 1
        elif m.outcome == OUTCOME_FAUSSE:
            kpi.n_fausse += 1
        elif m.outcome == OUTCOME_NC:
            kpi.n_nc += 1

        if m.cell.conclusion == "LONG":
            kpi.n_long += 1
        elif m.cell.conclusion == "SHORT":
            kpi.n_short += 1

        # Brier : exclut les non-conclusives (outcome 0/1 indéfini)
        if m.outcome in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            outcome_bin = 1.0 if m.outcome == OUTCOME_VRAI else 0.0
            proba = proba_from_score(m.cell.score, m.cell.conclusion)
            kpi.brier_sum += (proba - outcome_bin) ** 2
            kpi.brier_n += 1

    denom = kpi.n_vrai + kpi.n_fausse
    if denom > 0:
        kpi.taux_pct = round(kpi.n_vrai / denom * 100.0, 2)
    if kpi.brier_n > 0:
        kpi.brier = round(kpi.brier_sum / kpi.brier_n, 4)
    if kpi.n_total > 0:
        kpi.distrib_long_pct = round(kpi.n_long / kpi.n_total * 100.0, 1)
        kpi.distrib_short_pct = round(kpi.n_short / kpi.n_total * 100.0, 1)

    # --- Correction #1 : observations non-chevauchantes ---
    non_overlap = select_non_overlapping(window, horizon)
    kpi.n_effective = len(non_overlap)
    kpi.n_vrai_eff = sum(1 for m in non_overlap if m.outcome == OUTCOME_VRAI)
    kpi.n_fausse_eff = sum(1 for m in non_overlap if m.outcome == OUTCOME_FAUSSE)
    denom_eff = kpi.n_vrai_eff + kpi.n_fausse_eff  # == n_effective (VRAI+FAUSSE uniquement)
    if denom_eff > 0:
        kpi.taux_eff_pct = round(kpi.n_vrai_eff / denom_eff * 100.0, 2)

    # --- Correction #2 : intervalle de Wilson sur n_effective ---
    if kpi.n_effective > 0:
        low, high = wilson_ci(kpi.n_vrai_eff, kpi.n_effective)
        kpi.wilson_low = low
        kpi.wilson_high = high

    # Statut éligibilité — basé sur NON-CHEVAUCHANT + Wilson (décisionnel)
    # Règle :
    #   warm-up   : n_effective < N_EFFECTIVE_MIN
    #   éligible  : n_effective >= N_EFFECTIVE_MIN ET wilson_low > WILSON_LOW_THRESHOLD
    #               ET taux_eff_pct >= TARGET_TAUX
    #   shadow    : sinon
    if kpi.n_effective < N_EFFECTIVE_MIN:
        kpi.statut = "shadow"
        kpi.alertes.append(
            f"warm-up non-chevauchant : {kpi.n_effective}/{N_EFFECTIVE_MIN} obs effectives"
        )
    elif (
        kpi.taux_eff_pct is not None
        and kpi.taux_eff_pct >= TARGET_TAUX
        and kpi.wilson_low is not None
        and kpi.wilson_low > WILSON_LOW_THRESHOLD
    ):
        kpi.statut = "éligible_actif"
    else:
        kpi.statut = "shadow"
        if kpi.taux_eff_pct is not None and kpi.taux_eff_pct < TARGET_TAUX:
            kpi.alertes.append(f"taux_eff {kpi.taux_eff_pct}% < cible {TARGET_TAUX}% (non-chevauchant)")
        if kpi.wilson_low is not None and kpi.wilson_low <= WILSON_LOW_THRESHOLD:
            kpi.alertes.append(
                f"Wilson low {kpi.wilson_low:.3f} ≤ {WILSON_LOW_THRESHOLD:.2f} "
                f"(IC trop large, N_eff={kpi.n_effective})"
            )
    # Alerte rétro-compat sur n_total (warm-up fenêtre brute)
    if kpi.n_total < WINDOW:
        kpi.alertes.append(f"{kpi.n_total}/{WINDOW} mesures terminées (fenêtre brute warm-up)")

    # Distribution L/S
    if kpi.distrib_long_pct is not None:
        if kpi.distrib_long_pct < DISTRIB_MIN or kpi.distrib_long_pct > DISTRIB_MAX:
            kpi.alertes.append(
                f"biais distribution : LONG {kpi.distrib_long_pct}% (hors [{DISTRIB_MIN},{DISTRIB_MAX}]%)"
            )

    if kpi.interrompus_recents > 0:
        kpi.alertes.append(f"{kpi.interrompus_recents} suivi(s) interrompu(s) sur la fenêtre observable")

    return kpi


# ---------------------------------------------------------------------------
# Orchestration measure()
# ---------------------------------------------------------------------------

def _today_paris(now: Optional[datetime] = None) -> date:
    now = now or datetime.now(ZoneInfo("Europe/Paris"))
    return now.date()


def measure(
    today: Optional[date] = None,
    bulletins_dir: Path = BULLETINS_DIR,
    prix_emission_dir: Path = PRIX_EMISSION_DIR,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
) -> Tuple[List[Measure], Dict[Tuple[str, str], CellKPI]]:
    """Mesure toutes les conclusions échues à la date `today`.

    Une conclusion d'horizon H émise au bulletin du jour J est échue dès que
    today >= J + HORIZON_DAYS[H]. Pour chaque cellule, lit le prix d'émission
    (fichier `prix-emission/J.json` → ticker → prix) et le prix courant via
    fetch_price(ticker). Si l'un manque → suivi-interrompu (retry au prochain run).

    Retourne (liste de mesures, dict KPI par (fiche_key, horizon)).
    """
    today = today or _today_paris()
    fiches = fiches if fiches is not None else load_fiches()
    if fetch_price is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import criteres_calculator  # noqa: E402
        fetch_price = criteres_calculator.fetch_twelve_price

    bulletins = list_bulletins(bulletins_dir)
    # cache prix courants : 1 fetch par ticker pour tout le run
    prix_courants: Dict[str, Optional[float]] = {}

    def _get_current(ticker: str) -> Optional[float]:
        if ticker in prix_courants:
            return prix_courants[ticker]
        try:
            p = fetch_price(ticker)
        except Exception as e:  # noqa: BLE001
            logger.warning("fetch prix courant %s : %s", ticker, e)
            p = None
        prix_courants[ticker] = (float(p) if p is not None else None)
        return prix_courants[ticker]

    measures: List[Measure] = []
    for bpath in bulletins:
        cells = parse_bulletin(bpath)
        if not cells:
            continue
        bdate = cells[0].bulletin_date
        prix_emis = load_prix_emission(bdate, prix_emission_dir)
        for cell in cells:
            # n'inclure que les horizons échus à `today`
            echeance = cell.bulletin_date + timedelta(days=HORIZON_DAYS[cell.horizon])
            if echeance > today:
                continue
            match = fiche_for_actif_name(fiches, cell.actif_name)
            if not match:
                logger.warning("Fiche introuvable pour actif %r (bulletin %s)", cell.actif_name, bdate)
                continue
            fiche_key, fiche = match
            ticker = fiche.get("ticker_principal", "")
            p_emis = prix_emis.get(ticker)
            p_courant = _get_current(ticker) if ticker else None
            m = measure_cell(cell, fiche_key, fiche, p_emis, p_courant)
            measures.append(m)

    # Agrégation par cellule
    by_cell: Dict[Tuple[str, str], List[Measure]] = {}
    for m in measures:
        by_cell.setdefault((m.fiche_key, m.horizon), []).append(m)
    for key in by_cell:
        by_cell[key].sort(key=lambda m: m.echeance)

    kpis: Dict[Tuple[str, str], CellKPI] = {}
    for key, ms in by_cell.items():
        kpis[key] = compute_kpi(ms)

    return measures, kpis


# ---------------------------------------------------------------------------
# Correction #3 : Calibration — reliability diagram + ECE
# ---------------------------------------------------------------------------

@dataclass
class CalibBin:
    bin_idx: int
    proba_low: float           # borne basse du bin
    proba_high: float          # borne haute du bin
    n: int                     # nb obs dans ce bin
    mean_proba_pred: float     # proba prédite moyenne
    mean_outcome: float        # taux observé moyen (0/1)
    ece_contribution: float    # |mean_proba_pred - mean_outcome| * n / N_total


@dataclass
class CalibResult:
    bins: List[CalibBin]
    ece: float                 # Expected Calibration Error (pondéré par taille bin)
    n_total: int               # nb total d'obs dans le diagramme
    mean_proba: float          # proba prédite moyenne globale
    mean_outcome: float        # taux observé global


def compute_calibration(
    measures: List[Measure],
    n_bins: int = CALIB_N_BINS,
) -> Optional[CalibResult]:
    """Produit un reliability diagram bucketisé sur toutes les mesures VRAI/FAUSSE.

    Buckets sur la proba prédite ∈ [0.5, 1.0] (par construction : proba ≥ 0.5).
    Retourne None si < 10 observations conclusives.
    """
    conclusives = [
        m for m in measures if m.outcome in (OUTCOME_VRAI, OUTCOME_FAUSSE)
    ]
    if len(conclusives) < 10:
        return None

    # Bornes des bins : proba ∈ [0.5, 1.0] découpé en n_bins parties égales
    bin_edges = [0.5 + i * 0.5 / n_bins for i in range(n_bins + 1)]
    bins_data: List[List[Tuple[float, float]]] = [[] for _ in range(n_bins)]

    for m in conclusives:
        p = proba_from_score(m.cell.score, m.cell.conclusion)
        outcome = 1.0 if m.outcome == OUTCOME_VRAI else 0.0
        # Trouver le bin (index du dernier edge ≤ p)
        idx = min(
            int((p - 0.5) / (0.5 / n_bins)),
            n_bins - 1,
        )
        bins_data[idx].append((p, outcome))

    n_total = len(conclusives)
    calib_bins: List[CalibBin] = []
    for i, bucket in enumerate(bins_data):
        if not bucket:
            calib_bins.append(CalibBin(
                bin_idx=i,
                proba_low=bin_edges[i],
                proba_high=bin_edges[i + 1],
                n=0,
                mean_proba_pred=0.0,
                mean_outcome=0.0,
                ece_contribution=0.0,
            ))
            continue
        n = len(bucket)
        mean_p = sum(x[0] for x in bucket) / n
        mean_o = sum(x[1] for x in bucket) / n
        ece_contrib = abs(mean_p - mean_o) * n / n_total
        calib_bins.append(CalibBin(
            bin_idx=i,
            proba_low=bin_edges[i],
            proba_high=bin_edges[i + 1],
            n=n,
            mean_proba_pred=round(mean_p, 4),
            mean_outcome=round(mean_o, 4),
            ece_contribution=round(ece_contrib, 4),
        ))

    ece = round(sum(b.ece_contribution for b in calib_bins), 4)
    all_probas = [x[0] for bkt in bins_data for x in bkt]
    all_outcomes = [x[1] for bkt in bins_data for x in bkt]
    mean_proba = round(sum(all_probas) / n_total, 4) if n_total else 0.0
    mean_outcome = round(sum(all_outcomes) / n_total, 4) if n_total else 0.0

    return CalibResult(
        bins=calib_bins,
        ece=ece,
        n_total=n_total,
        mean_proba=mean_proba,
        mean_outcome=mean_outcome,
    )


def render_calibration(
    calib: Optional[CalibResult],
    now: datetime,
) -> str:
    """Génère le contenu de calibration.md (reliability diagram textuel + ECE)."""
    lines: List[str] = []
    lines.append("# Calibration probabiliste — Reliability Diagram")
    lines.append("")
    lines.append(f"- Généré : {now.isoformat()}")
    lines.append(f"- Méthode : ECE (Expected Calibration Error) simple, {CALIB_N_BINS} bins sur proba ∈ [0.5, 1.0]")
    lines.append(f"- proba = 0.5 + clip(|score| / {PROBA_SCALE}, 0, 0.5)  [mapping déterministe — non calibré empiriquement]")
    lines.append("")
    lines.append("## Interprétation")
    lines.append("")
    lines.append("- **Bien calibré** : proba_prédite ≈ taux_observé dans chaque bin → ECE proche de 0")
    lines.append("- **Sur-confiant** : proba_prédite > taux_observé (systématique si ECE élevé et proba >> taux)")
    lines.append("- **Sous-confiant** : proba_prédite < taux_observé")
    lines.append("- Seuil d'alerte ECE > 0.10 : recalibration du mapping score→proba recommandée")
    lines.append("")

    if calib is None:
        lines.append("_Pas encore assez d'observations conclusives (< 10) pour produire le diagramme._")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"- Observations conclusives totales : {calib.n_total}")
    lines.append(f"- Proba prédite moyenne : {calib.mean_proba:.4f}")
    lines.append(f"- Taux observé global : {calib.mean_outcome:.4f}")
    lines.append(f"- **ECE = {calib.ece:.4f}** {'⚠️ RECALIBRER (> 0.10)' if calib.ece > 0.10 else '✓ acceptable (≤ 0.10)'}")
    lines.append("")
    lines.append("## Reliability Diagram (textuel)")
    lines.append("")
    lines.append("| Bin | Proba prédite (range) | N | Proba préd. moy. | Taux observé | Ecart | ECE contrib. |")
    lines.append("|---|---|---|---|---|---|---|")

    for b in calib.bins:
        if b.n == 0:
            lines.append(
                f"| {b.bin_idx + 1} | [{b.proba_low:.2f}, {b.proba_high:.2f}] | 0 | — | — | — | — |"
            )
        else:
            ecart = b.mean_proba_pred - b.mean_outcome
            lines.append(
                f"| {b.bin_idx + 1} | [{b.proba_low:.2f}, {b.proba_high:.2f}] | {b.n} | "
                f"{b.mean_proba_pred:.4f} | {b.mean_outcome:.4f} | {ecart:+.4f} | {b.ece_contribution:.4f} |"
            )

    lines.append("")
    lines.append(f"**ECE total = {calib.ece:.4f}**")
    lines.append("")
    lines.append("## Note méthodologique")
    lines.append("")
    lines.append("L'ECE mesure l'écart moyen pondéré entre la probabilité prédite et la fréquence observée.")
    lines.append("Une ECE de 0.10 signifie que le système se trompe en moyenne de 10 points de proba.")
    lines.append("Sans calibration empirique (Platt scaling, isotonic regression), le mapping score→proba")
    lines.append("est structurellement non-calibré. Ce diagramme permet de détecter le biais systématique.")
    lines.append("")

    return "\n".join(lines)


def write_calibration(content: str, path: Path = CALIBRATION_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Rendu performance.md
# ---------------------------------------------------------------------------

def render_performance(
    kpis: Dict[Tuple[str, str], CellKPI],
    measures: List[Measure],
    now: datetime,
) -> str:
    lines: List[str] = []
    lines.append(f"# Performance du bulletin — Journaliste")
    lines.append("")
    lines.append(f"- Généré : {now.isoformat()}")
    lines.append(f"- Journaliste version : {JOURNALISTE_VERSION}")
    lines.append(f"- Fenêtre KPI : {WINDOW} dernières conclusions terminées par cellule")
    lines.append(f"- PROBA_SCALE : {PROBA_SCALE} (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))")
    lines.append(f"- Cible éligibilité : {TARGET_TAUX:.0f}% (Bourse.md)")
    lines.append("")
    lines.append("## Matrice cellules (actif × horizon)")
    lines.append("")
    lines.append(
        "| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")

    # tri par actif puis horizon
    horizon_order = {h: i for i, h in enumerate(HORIZONS)}
    sorted_keys = sorted(
        kpis.keys(),
        key=lambda k: (kpis[k].actif_name.lower(), horizon_order.get(k[1], 99)),
    )
    for key in sorted_keys:
        k = kpis[key]
        taux = "—" if k.taux_pct is None else f"{k.taux_pct:.1f}%"
        taux_eff = "—" if k.taux_eff_pct is None else f"{k.taux_eff_pct:.1f}%"
        w_low = "—" if k.wilson_low is None else f"{k.wilson_low:.3f}"
        brier = "—" if k.brier is None else f"{k.brier:.4f}"
        if k.distrib_long_pct is None:
            distrib = "—"
        else:
            distrib = f"{k.distrib_long_pct:.0f}/{k.distrib_short_pct:.0f}%"
        alertes = "; ".join(k.alertes) if k.alertes else "—"
        lines.append(
            f"| {k.actif_name} | {k.horizon} | {k.n_total} | {taux} | {k.n_effective} | "
            f"{taux_eff} | {w_low} | {brier} | {distrib} | {k.statut} | {alertes} |"
        )

    # Synthèse
    nb_eligibles = sum(1 for k in kpis.values() if k.statut == "éligible_actif")
    nb_shadow = sum(1 for k in kpis.values() if k.statut == "shadow")
    lines.append("")
    lines.append("## Synthèse")
    lines.append(f"- Cellules éligibles actif (Wilson low > {WILSON_LOW_THRESHOLD:.0%}, taux_eff ≥ {TARGET_TAUX:.0f}%) : **{nb_eligibles}** / {len(kpis)}")
    lines.append(f"- Cellules shadow : {nb_shadow} / {len(kpis)}")
    lines.append("")
    lines.append("### Critère global (multiple testing — audit-data §2)")
    lines.append("")
    lines.append("Avec 36 cellules testées, ~1-2 faux positifs attendus par hasard à α=0,05.")
    lines.append("Critère d'éligibilité renforcé : Wilson low > 50 % (borne basse IC 95 % sur N_eff).")
    lines.append("")
    # Calculer les métriques globales
    cells_with_eff = [k for k in kpis.values() if k.n_effective >= N_EFFECTIVE_MIN and k.taux_eff_pct is not None]
    if cells_with_eff:
        taux_global = sum(k.taux_eff_pct for k in cells_with_eff) / len(cells_with_eff)  # type: ignore[arg-type]
        cells_below_55 = [k for k in cells_with_eff if k.taux_eff_pct is not None and k.taux_eff_pct < GLOBAL_MIN_TAUX]
        pct_below = len(cells_below_55) / len(cells_with_eff) * 100
        lines.append(f"- Taux moyen global (N_eff ≥ {N_EFFECTIVE_MIN}) : **{taux_global:.1f}%** ({len(cells_with_eff)} cellules)")
        lines.append(f"- Cellules < {GLOBAL_MIN_TAUX:.0f}% : {len(cells_below_55)}/{len(cells_with_eff)} ({pct_below:.0f}%)")
        kill_trigger = taux_global < GLOBAL_MIN_TAUX
        lines.append(f"- Taux global {'< ⚠️ KILL CRITERION DÉCLENCHÉ' if kill_trigger else '≥'} {GLOBAL_MIN_TAUX:.0f}% : {'KILL' if kill_trigger else 'OK'}")
    else:
        lines.append(f"- Critère global : warm-up (aucune cellule avec N_eff ≥ {N_EFFECTIVE_MIN})")

    # Détail : 10 dernières mesures
    lines.append("")
    lines.append("## Dernières mesures (max 20)")
    lines.append("")
    lines.append("| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    recent = sorted(measures, key=lambda m: m.echeance, reverse=True)[:20]
    for m in recent:
        pe = "—" if m.prix_emission is None else f"{m.prix_emission:.4f}"
        pc = "—" if m.prix_courant is None else f"{m.prix_courant:.4f}"
        delta = "—" if m.delta_pct is None else f"{m.delta_pct:+.3f}%"
        seuil = "—" if m.seuil_pct is None else f"{m.seuil_pct}%"
        lines.append(
            f"| {m.cell.bulletin_date.isoformat()} | {m.echeance.isoformat()} | {m.cell.actif_name} | "
            f"{m.horizon} | {m.cell.conclusion} | {pe} | {pc} | {delta} | {seuil} | {m.outcome} | {m.note} |"
        )
    lines.append("")

    return "\n".join(lines)


def write_performance(content: str, path: Path = PERFORMANCE_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# A/B Performance (±1 vs pondéré, côte à côte)
# ---------------------------------------------------------------------------

@dataclass
class CellKPIAB:
    fiche_key: str
    actif_name: str
    horizon: str
    # Baseline ±1
    n_pm1: int = 0
    n_vrai_pm1: int = 0
    n_fausse_pm1: int = 0
    taux_pm1: Optional[float] = None
    brier_pm1: Optional[float] = None
    # Pondéré
    n_pond: int = 0
    n_vrai_pond: int = 0
    n_fausse_pond: int = 0
    taux_pond: Optional[float] = None
    brier_pond: Optional[float] = None


def compute_kpi_ab(measures_for_cell: List[Measure]) -> CellKPIAB:
    """Calcule taux + Brier en parallèle pour ±1 et pondéré.

    Skip propre : les mesures dont outcome_pond=None (anciennes) ne comptent
    PAS dans le dénominateur pondéré (mais bien dans le ±1).
    """
    if not measures_for_cell:
        return CellKPIAB(fiche_key="", actif_name="", horizon="")
    kpi = CellKPIAB(
        fiche_key=measures_for_cell[0].fiche_key,
        actif_name=measures_for_cell[0].cell.actif_name,
        horizon=measures_for_cell[0].horizon,
    )
    terminees = [m for m in measures_for_cell if m.outcome != OUTCOME_INTERROMPU]
    window = terminees[-WINDOW:]
    brier_sum_pm1 = 0.0
    brier_n_pm1 = 0
    brier_sum_pond = 0.0
    brier_n_pond = 0
    for m in window:
        # ±1
        if m.outcome in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            kpi.n_pm1 += 1
            if m.outcome == OUTCOME_VRAI:
                kpi.n_vrai_pm1 += 1
            else:
                kpi.n_fausse_pm1 += 1
            outcome_bin = 1.0 if m.outcome == OUTCOME_VRAI else 0.0
            proba = proba_from_score(m.cell.score, m.cell.conclusion)
            brier_sum_pm1 += (proba - outcome_bin) ** 2
            brier_n_pm1 += 1
        # Pondéré (skip si outcome_pond None ou non-conclusive)
        if m.outcome_pond in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            kpi.n_pond += 1
            if m.outcome_pond == OUTCOME_VRAI:
                kpi.n_vrai_pond += 1
            else:
                kpi.n_fausse_pond += 1
            outcome_bin = 1.0 if m.outcome_pond == OUTCOME_VRAI else 0.0
            score_p = m.cell.score_pond if m.cell.score_pond is not None else m.cell.score
            conc_p = m.cell.conclusion_pond if m.cell.conclusion_pond else m.cell.conclusion
            proba = proba_from_score(score_p, conc_p)
            brier_sum_pond += (proba - outcome_bin) ** 2
            brier_n_pond += 1
    if kpi.n_pm1 > 0:
        kpi.taux_pm1 = round(kpi.n_vrai_pm1 / kpi.n_pm1 * 100.0, 2)
    if brier_n_pm1 > 0:
        kpi.brier_pm1 = round(brier_sum_pm1 / brier_n_pm1, 4)
    if kpi.n_pond > 0:
        kpi.taux_pond = round(kpi.n_vrai_pond / kpi.n_pond * 100.0, 2)
    if brier_n_pond > 0:
        kpi.brier_pond = round(brier_sum_pond / brier_n_pond, 4)
    return kpi


def render_performance_ab(
    kpis_ab: Dict[Tuple[str, str], CellKPIAB],
    now: datetime,
) -> str:
    lines: List[str] = []
    lines.append("# Performance A/B — ±1 (baseline) vs pondéré (secondaire)")
    lines.append("")
    lines.append(f"- Généré : {now.isoformat()}")
    lines.append(f"- Fenêtre KPI : {WINDOW} dernières conclusions terminées par cellule")
    lines.append(f"- Cible : {TARGET_TAUX:.0f}% (Bourse.md)")
    lines.append("")
    lines.append("Skip propre : les bulletins antérieurs sans annotation pondérée ne comptent")
    lines.append("pas dans le dénominateur pondéré (colonne N_pond < N_pm1 normal au démarrage).")
    lines.append("")
    lines.append("## Matrice A/B")
    lines.append("")
    lines.append("| Actif | Horizon | N_pm1 | Taux_pm1 | Brier_pm1 | N_pond | Taux_pond | Brier_pond |")
    lines.append("|---|---|---|---|---|---|---|---|")
    horizon_order = {h: i for i, h in enumerate(HORIZONS)}
    sorted_keys = sorted(
        kpis_ab.keys(),
        key=lambda k: (kpis_ab[k].actif_name.lower(), horizon_order.get(k[1], 99)),
    )
    for key in sorted_keys:
        k = kpis_ab[key]
        t_pm1 = "—" if k.taux_pm1 is None else f"{k.taux_pm1:.1f}%"
        b_pm1 = "—" if k.brier_pm1 is None else f"{k.brier_pm1:.4f}"
        t_p = "—" if k.taux_pond is None else f"{k.taux_pond:.1f}%"
        b_p = "—" if k.brier_pond is None else f"{k.brier_pond:.4f}"
        lines.append(
            f"| {k.actif_name} | {k.horizon} | {k.n_pm1} | {t_pm1} | {b_pm1} | "
            f"{k.n_pond} | {t_p} | {b_p} |"
        )
    # Synthèse globale
    lines.append("")
    lines.append("## Synthèse globale (cellules avec ≥1 mesure pondérée)")
    deltas = []
    for k in kpis_ab.values():
        if k.taux_pm1 is not None and k.taux_pond is not None and k.n_pond > 0:
            deltas.append(k.taux_pond - k.taux_pm1)
    if deltas:
        avg = sum(deltas) / len(deltas)
        lines.append(f"- Delta taux moyen (pondéré − ±1) : **{avg:+.2f} pts** sur {len(deltas)} cellules")
    else:
        lines.append("- Aucune cellule avec mesure pondérée disponible (warm-up A/B).")
    lines.append("")
    return "\n".join(lines)


def write_performance_ab(content: str, path: Path = PERFORMANCE_AB_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Entrée principale
# ---------------------------------------------------------------------------

def run(
    today: Optional[date] = None,
    now: Optional[datetime] = None,
    bulletins_dir: Path = BULLETINS_DIR,
    prix_emission_dir: Path = PRIX_EMISSION_DIR,
    performance_path: Path = PERFORMANCE_FILE,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    stamp_today: bool = True,
) -> Tuple[Path, List[Measure], Dict[Tuple[str, str], CellKPI]]:
    """Run journaliste : stamp prix du jour (optionnel) + mesure échéances + écrit performance.md."""
    now = now or datetime.now(ZoneInfo("Europe/Paris"))
    today = today or now.date()
    fiches = fiches if fiches is not None else load_fiches()

    if stamp_today:
        try:
            stamp_prix_emission(
                today,
                fiches=fiches,
                fetch_price=fetch_price,
                base_dir=prix_emission_dir,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("stamp_prix_emission KO : %s (on continue la mesure)", e)

    measures, kpis = measure(
        today=today,
        bulletins_dir=bulletins_dir,
        prix_emission_dir=prix_emission_dir,
        fiches=fiches,
        fetch_price=fetch_price,
    )
    content = render_performance(kpis, measures, now)
    out_path = write_performance(content, performance_path)
    logger.info("performance.md écrit : %s (%d mesures, %d cellules)", out_path, len(measures), len(kpis))

    # Calibration (best-effort, non bloquant)
    try:
        calib = compute_calibration(measures)
        calib_content = render_calibration(calib, now)
        calib_path = performance_path.parent / "calibration.md"
        write_calibration(calib_content, calib_path)
        logger.info("calibration.md écrit : %s (ECE=%s)", calib_path, calib.ece if calib else "n/a")
    except Exception as e:  # noqa: BLE001
        logger.warning("calibration KO (non bloquant) : %s", e)

    # A/B : ±1 vs pondéré (best-effort, non bloquant)
    try:
        by_cell_ab: Dict[Tuple[str, str], List[Measure]] = {}
        for m in measures:
            by_cell_ab.setdefault((m.fiche_key, m.horizon), []).append(m)
        for key in by_cell_ab:
            by_cell_ab[key].sort(key=lambda m: m.echeance)
        kpis_ab: Dict[Tuple[str, str], CellKPIAB] = {
            k: compute_kpi_ab(ms) for k, ms in by_cell_ab.items()
        }
        ab_content = render_performance_ab(kpis_ab, now)
        write_performance_ab(ab_content)
        logger.info("performance-ab.md écrit (%d cellules A/B)", len(kpis_ab))
    except Exception as e:  # noqa: BLE001
        logger.warning("performance-ab KO (non bloquant) : %s", e)

    return out_path, measures, kpis


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    try:
        path, measures, kpis = run()
    except Exception as e:  # noqa: BLE001
        logger.error("Journaliste KO : %s", e)
        return 1
    print(f"OK : {path} ({len(measures)} mesures, {len(kpis)} cellules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
