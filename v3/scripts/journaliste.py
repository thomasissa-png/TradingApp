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

JOURNALISTE_VERSION = "v3.0.0"
HORIZONS: Tuple[str, ...] = ("24h", "7j", "1m")
HORIZON_DAYS: Dict[str, int] = {"24h": 1, "7j": 7, "1m": 30}
WINDOW = 30                  # KPI sur 30 dernières conclusions terminées
PROBA_SCALE = 10.0           # score / PROBA_SCALE pour dériver la proba (param documenté)
TARGET_TAUX = 70.0           # seuil éligibilité (Bourse.md)
DISTRIB_MIN = 30.0           # alerte distribution LONG/SHORT hors [30, 70] %
DISTRIB_MAX = 70.0

ROOT = Path(__file__).resolve().parents[1]
FICHES_DIR = ROOT / "config" / "fiches"
BULLETINS_DIR = ROOT / "data" / "bulletins"
PRIX_EMISSION_DIR = ROOT / "data" / "prix-emission"
PERFORMANCE_FILE = ROOT / "data" / "performance.md"


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
BULLETIN_FILE_RE = re.compile(r"^bulletin-(\d{4}-\d{2}-\d{2})\.md$")


@dataclass
class BulletinCell:
    bulletin_date: date
    actif_name: str          # tel que lu dans le bulletin
    horizon: str             # "24h" / "7j" / "1m"
    conclusion: str          # "LONG" / "SHORT"
    score: float


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
        # Skip ligne d'en-tête "| Actif | 24h | 7j | 1m |" (déjà filtrée par regex car nécessite LONG/SHORT)
        for h, conc_key, score_key in (("24h", "c24", "s24"), ("7j", "c7", "s7"), ("1m", "c1", "s1")):
            try:
                score = float(mm.group(score_key))
            except (TypeError, ValueError):
                continue
            cells.append(
                BulletinCell(
                    bulletin_date=bdate,
                    actif_name=actif,
                    horizon=h,
                    conclusion=mm.group(conc_key),
                    score=score,
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
    return base


# ---------------------------------------------------------------------------
# Agrégation KPI par cellule (actif × horizon)
# ---------------------------------------------------------------------------

@dataclass
class CellKPI:
    fiche_key: str
    actif_name: str
    horizon: str
    n_total: int = 0          # mesures terminées (VRAI + FAUSSE + non-conclusive)
    n_vrai: int = 0
    n_fausse: int = 0
    n_nc: int = 0
    n_long: int = 0
    n_short: int = 0
    brier_sum: float = 0.0
    brier_n: int = 0
    interrompus_recents: int = 0
    taux_pct: Optional[float] = None
    brier: Optional[float] = None
    distrib_long_pct: Optional[float] = None
    distrib_short_pct: Optional[float] = None
    statut: str = "shadow"
    alertes: List[str] = field(default_factory=list)


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

    # Statut éligibilité (Bourse.md)
    if kpi.n_total >= WINDOW and kpi.taux_pct is not None and kpi.taux_pct >= TARGET_TAUX:
        kpi.statut = "éligible_actif"
    else:
        kpi.statut = "shadow"
        if kpi.n_total < WINDOW:
            kpi.alertes.append(f"{kpi.n_total}/{WINDOW} mesures terminées (warm-up)")
        elif kpi.taux_pct is not None and kpi.taux_pct < TARGET_TAUX:
            kpi.alertes.append(f"taux {kpi.taux_pct}% < cible {TARGET_TAUX}%")

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
    lines.append("| Actif | Horizon | N | Taux | Brier | LONG/SHORT | Statut | Alertes |")
    lines.append("|---|---|---|---|---|---|---|---|")

    # tri par actif puis horizon
    horizon_order = {h: i for i, h in enumerate(HORIZONS)}
    sorted_keys = sorted(
        kpis.keys(),
        key=lambda k: (kpis[k].actif_name.lower(), horizon_order.get(k[1], 99)),
    )
    for key in sorted_keys:
        k = kpis[key]
        taux = "—" if k.taux_pct is None else f"{k.taux_pct:.1f}%"
        brier = "—" if k.brier is None else f"{k.brier:.4f}"
        if k.distrib_long_pct is None:
            distrib = "—"
        else:
            distrib = f"{k.distrib_long_pct:.0f}/{k.distrib_short_pct:.0f}%"
        alertes = "; ".join(k.alertes) if k.alertes else "—"
        lines.append(
            f"| {k.actif_name} | {k.horizon} | {k.n_total} | {taux} | {brier} | {distrib} | {k.statut} | {alertes} |"
        )

    # Synthèse
    nb_eligibles = sum(1 for k in kpis.values() if k.statut == "éligible_actif")
    nb_shadow = sum(1 for k in kpis.values() if k.statut == "shadow")
    lines.append("")
    lines.append("## Synthèse")
    lines.append(f"- Cellules éligibles actif (taux ≥ {TARGET_TAUX:.0f}%) : **{nb_eligibles}** / {len(kpis)}")
    lines.append(f"- Cellules shadow : {nb_shadow} / {len(kpis)}")

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
