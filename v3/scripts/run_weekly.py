"""TradingApp v3 — Bilan de la semaine samedi matin (R5) + le Manager.

Source de vérité : `v3/docs/reco/spec-refonte-5-rapports.md` §4 + §7 (CA-W*).

R5 est le 4e agent historique du système (Veilleur / Analyste / Journaliste /
**Manager**), enfin implémenté. Le Manager est la couche apprentissage/pilotage :
il LIT les résultats de la semaine et PROPOSE des ajustements de configuration.

PRINCIPE CARDINAL (le coeur du Manager) : le Manager PROPOSE, Thomas VALIDE.
JAMAIS de modification silencieuse de config. Après un run weekly,
`git diff v3/config/` DOIT être vide (CA-W4 — testé en garde-fou).

Garde-fous :
- WIN RATE ONLY — aucune valeur monétaire (€/$/gain/perte/rendement). Jamais.
- Zéro écriture dans `v3/config/` — le Manager n'applique RIEN (CA-W4).
- Zéro invention : un ajustement proposé est justifié par des chiffres réels du
  KPI (win rate, N_eff, Wilson). Jamais inventé (commandement 2).
- Détection cellule faible : N_eff >= 10 ET Wilson_low < 50%, observé sur >= 2
  semaines CONSÉCUTIVES (§4.3 cond. 1). N_eff 5-9 -> observation, PAS de
  proposition (« mesurer avant d'agir »).
- Remonte aussi ce qui MARCHE (cellules porteuses, §4.6).
- Win rate par conviction forte/faible (§4.7, réutilise bilan_jour).
- Fuseaux via ZoneInfo, jamais d'offset codé en dur. Réutilise l'existant
  (compute_kpi/measure, archive hebdo, win rate conviction).

Le déclenchement samedi matin (guard weekday()==5 + bypass is_trading_day) est
géré par l'infra (cron + cycle.yml), PAS ici. Ce module EXPOSE build_bilan_semaine
appelable avec un `now` (datetime Europe/Paris).
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger("run_weekly")

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# [Point #5] Horodatage FR lisible de la ligne « Généré : … ».
from datetime_fr import horodatage_fr  # noqa: E402 (après l'ajout au sys.path)

PARIS_TZ = ZoneInfo("Europe/Paris")

BILAN_SEMAINE_DIR = ROOT / "data" / "bilan-semaine"
# Snapshots internes du Manager (persistance de la détection inter-semaines).
# N'est PAS un fichier de config : c'est une donnée de mesure (v3/data/).
MANAGER_STATE_DIR = BILAN_SEMAINE_DIR / ".state"
PERFORMANCE_WEEKLY_DIR = ROOT / "data" / "performance" / "weekly"
DECISION_LOG_DIR = ROOT / "data" / "decision-log"
PRIX_EMISSION_DIR = ROOT / "data" / "prix-emission"
PRIX_OUVERTURE_DIR = ROOT / "data" / "prix-ouverture"
# Journal PERSISTÉ des mesures (verdicts jugés jour par jour). Source de vérité du
# bilan : on NE re-mesure PAS à chaud (les prix passés ne sont plus dispo en fin
# de semaine → tout repasserait « non-conclusif » = bug « Aucune sélection »).
MEASURES_LOG = ROOT / "data" / "measures-log.jsonl"

# --- Seuils de détection du Manager (§4.3) ---------------------------------
# Cellule faible : N_eff >= N_EFF_PROPOSE ET Wilson_low < WILSON_FAIBLE,
# observé sur >= SEMAINES_CONSECUTIVES semaines. Entre N_EFF_OBSERVE et
# N_EFF_PROPOSE-1 -> observation sans proposition (« mesurer avant d'agir »).
N_EFF_PROPOSE = 10          # seuil dur de proposition (correction D1 Analyst)
N_EFF_OBSERVE = 5           # plancher d'observation (5-9 -> observation)
WILSON_FAIBLE = 50.0        # Wilson_low en % (borne basse < 50% = faible)
SEMAINES_CONSECUTIVES = 2   # observé sur >= 2 semaines consécutives
# Cellule porteuse (§4.6) : ce qui MARCHE.
WINRATE_PORTEUSE = 65.0     # win rate >= 65%
N_EFF_PORTEUSE = 5          # avec au moins 5 paris indépendants


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------

@dataclass
class CelluleObs:
    """Observation d'une cellule pour le Manager (win-rate-only)."""
    actif: str
    horizon: str
    win_rate: Optional[float]
    n_eff: int
    wilson_low: Optional[float]
    # WR tradable = VRAI / (VRAI + FAUSSE + non-conclusif). Métrique SECONDAIRE
    # affichée À CÔTÉ du win rate conclusif (toujours ≤ win_rate). Le kill
    # criterion reste sur win_rate (conclusif) — coexistence, rien retiré.
    wr_tradable: Optional[float] = None
    n_tradable: int = 0
    # candidate faible cette semaine (N_eff>=10 ET Wilson_low<50%)
    candidate_faible: bool = False
    # faible CONFIRMÉE (candidate >= 2 semaines consécutives)
    faible_confirmee: bool = False
    porteuse: bool = False


@dataclass
class BilanSemaine:
    iso: str
    lundi: date
    dimanche: date
    now: datetime
    cellules: List[CelluleObs] = field(default_factory=list)
    n_forte: int = 0
    taux_forte: Optional[float] = None
    n_faible_conv: int = 0
    taux_faible_conv: Optional[float] = None
    propositions: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    selection: Optional["SelectionSemaine"] = None
    tendances: List["TendanceActif"] = field(default_factory=list)
    picks: List["PickSemaine"] = field(default_factory=list)  # post-mortem causal (S9)
    markdown: str = ""


def _fmt_pct(v: Optional[float]) -> str:
    return f"{v:.1f}%" if isinstance(v, (int, float)) else "—"


# ---------------------------------------------------------------------------
# Persistance inter-semaines (détection >= 2 semaines consécutives)
# ---------------------------------------------------------------------------
# Le Manager doit savoir si une cellule était DÉJÀ candidate faible la semaine
# ISO précédente. On persiste, par semaine ISO, la liste des cellules candidates
# (N_eff>=10 ET Wilson_low<50%) dans v3/data/bilan-semaine/.state/{ISO}.json.
# C'est une DONNÉE de mesure (pas de la config) — zéro écriture v3/config/.

def _prev_iso_label(now: datetime) -> str:
    from journaliste import iso_week_label  # noqa: PLC0415
    paris = now.astimezone(PARIS_TZ)
    from datetime import timedelta  # noqa: PLC0415
    return iso_week_label(paris - timedelta(days=7))


def load_candidates_state(
    iso: str, state_dir: Path = MANAGER_STATE_DIR
) -> set:
    """Charge l'ensemble des (actif, horizon) candidates faibles d'une semaine ISO.

    Set vide si le fichier n'existe pas (zéro invention — une semaine sans
    snapshot = aucune candidate connue, donc pas de 2e semaine consécutive).
    """
    fp = state_dir / f"{iso}.json"
    if not fp.exists():
        return set()
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
        return {(str(a), str(h)) for a, h in data.get("candidates_faibles", [])}
    except (OSError, json.JSONDecodeError, ValueError) as e:
        logger.warning("state Manager illisible %s : %s", fp, e)
        return set()


def save_candidates_state(
    iso: str, candidates: set, state_dir: Path = MANAGER_STATE_DIR
) -> Path:
    """Persiste les candidates faibles de la semaine (pour le run de S+1)."""
    state_dir.mkdir(parents=True, exist_ok=True)
    fp = state_dir / f"{iso}.json"
    payload = {
        "iso": iso,
        "candidates_faibles": sorted([list(c) for c in candidates]),
    }
    fp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return fp


# ---------------------------------------------------------------------------
# Chargement des KPIs (réutilise measure() — zéro recalcul custom)
# ---------------------------------------------------------------------------

def collect_cellules(
    now: datetime,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    prev_candidates: Optional[set] = None,
) -> Tuple[List[CelluleObs], set, List[Any]]:
    """Construit la liste des observations de cellules à partir des KPIs réels.

    Réutilise journaliste.measure() (seul R1/7h mesuré, only_seven_am=True) —
    AUCUN recalcul de win rate custom (CA-W2). wilson_low du KPI est en
    proportion [0,1] -> converti en %.

    Retourne (cellules, candidates_faibles_semaine, measures).
    """
    from journaliste import measure, load_fiches  # noqa: PLC0415

    fiches = fiches if fiches is not None else load_fiches()
    prev_candidates = prev_candidates or set()
    measures, kpis = measure(fiches=fiches, fetch_price=fetch_price)

    cellules: List[CelluleObs] = []
    candidates_now: set = set()
    for (_fk, horizon), kpi in kpis.items():
        actif = kpi.actif_name
        wr = kpi.taux_eff_pct
        n_eff = kpi.n_effective
        # wilson_low du KPI ∈ [0,1] -> en %.
        w_low = kpi.wilson_low * 100.0 if kpi.wilson_low is not None else None

        obs = CelluleObs(
            actif=actif, horizon=horizon, win_rate=wr, n_eff=n_eff, wilson_low=w_low,
            wr_tradable=kpi.tradable_eff_pct, n_tradable=kpi.n_tradable,
        )
        # Candidate faible cette semaine : N_eff>=10 ET Wilson_low<50%.
        if n_eff >= N_EFF_PROPOSE and w_low is not None and w_low < WILSON_FAIBLE:
            obs.candidate_faible = True
            candidates_now.add((actif, horizon))
            # Faible CONFIRMÉE seulement si déjà candidate la semaine ISO précédente.
            if (actif, horizon) in prev_candidates:
                obs.faible_confirmee = True
        # Porteuse : ce qui MARCHE (§4.6).
        if (
            wr is not None
            and wr >= WINRATE_PORTEUSE
            and n_eff >= N_EFF_PORTEUSE
        ):
            obs.porteuse = True
        cellules.append(obs)

    return cellules, candidates_now, measures


# ---------------------------------------------------------------------------
# Win rate par conviction (réutilise bilan_jour) — sur les paris de la semaine
# ---------------------------------------------------------------------------

def _conviction_semaine(
    measures: List[Any], now: datetime, decision_log_dir: Optional[Path] = None
):
    """Win rate forte/faible sur les paris dont l'échéance tombe dans la semaine ISO.

    Réutilise bilan_jour.win_rate_par_conviction + load_conviction_map (zéro
    nouveau champ, §4.7). La conviction d'une cellule est lue sur le decision-log
    du jour de DÉCISION du pari (bulletin_date = échéance - horizon).
    """
    from journaliste import iso_week_bounds, OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415
    from bilan_jour import load_conviction_map, win_rate_par_conviction  # noqa: PLC0415
    from datetime import timedelta  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    horizon_days = {"24h": 1, "7j": 7, "1m": 30}

    week_measures = [
        m for m in measures
        if m.outcome in (OUTCOME_VRAI, OUTCOME_FAUSSE)
        and monday <= m.echeance <= sunday
    ]
    # Conviction par cellule : on lit le decision-log du jour de décision.
    conv_map: Dict[Tuple[str, str], str] = {}
    seen_dates: set = set()
    for m in week_measures:
        dd = horizon_days.get(m.horizon, 1)
        decision_day = m.echeance - timedelta(days=dd)
        if decision_day in seen_dates:
            continue
        seen_dates.add(decision_day)
        day_map = load_conviction_map(decision_day, decision_log_dir) \
            if decision_log_dir else load_conviction_map(decision_day)
        for k, v in day_map.items():
            conv_map.setdefault(k, v)

    return win_rate_par_conviction(week_measures, conv_map)


# ---------------------------------------------------------------------------
# SECTION 1 — Performance des 24h sélectionnés (la semaine)
# ---------------------------------------------------------------------------
# Agrégat hebdo de nos « top du jour » (selection_du_jour: true, horizon 24h) :
#   - win rate de la sélection (réutilise bilan_jour.win_rate_selection cumulé) ;
#   - ampleur moyenne en % des sélections gagnantes / perdantes (mouvement
#     directionnel signé, WIN RATE ONLY = % de mouvement, jamais d'€).
# Zéro invention : une cellule dont le prix de réf ou le prix d'échéance manque
# est exclue de l'ampleur (mais reste comptée dans le win rate via son outcome).

@dataclass
class SelectionSemaine:
    """Agrégat hebdo de la Sélection du jour (24h). WIN RATE ONLY."""
    n_select: int = 0           # sélections conclusives (VRAI+FAUSSE)
    n_vrai: int = 0             # sélections VRAI
    ampleurs_gagnantes: List[float] = field(default_factory=list)  # % >= 0
    ampleurs_perdantes: List[float] = field(default_factory=list)  # % < 0

    @property
    def win_rate(self) -> Optional[float]:
        return round(self.n_vrai / self.n_select * 100.0, 1) if self.n_select else None

    @property
    def ampleur_moy_gagnantes(self) -> Optional[float]:
        v = self.ampleurs_gagnantes
        return round(sum(v) / len(v), 2) if v else None

    @property
    def ampleur_moy_perdantes(self) -> Optional[float]:
        v = self.ampleurs_perdantes
        return round(sum(v) / len(v), 2) if v else None


def _mouvement_directionnel_pct(m: Any) -> Optional[float]:
    """% de mouvement DANS LE SENS du call (signe LONG=+1 / SHORT=−1).

    `signe × (prix_courant − prix_emission) / prix_emission × 100`. None si un
    prix manque ou si la direction n'est pas LONG/SHORT (zéro invention).
    """
    direction = getattr(m.cell, "conclusion", None)
    if direction not in ("LONG", "SHORT"):
        return None
    pe = m.prix_emission
    pc = m.prix_courant
    if not isinstance(pe, (int, float)) or not isinstance(pc, (int, float)) or pe == 0:
        return None
    signe = 1.0 if direction == "LONG" else -1.0
    return signe * (pc - pe) / pe * 100.0


def selection_semaine(
    now: datetime,
    measures_log: Path = MEASURES_LOG,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> SelectionSemaine:
    """Agrège la Sélection du jour (24h) sur la semaine ISO de `now`.

    Source = le JOURNAL PERSISTÉ des mesures (measures-log.jsonl), c.-à-d. les
    verdicts déjà jugés jour par jour. On NE re-mesure PAS à chaud : en fin de
    semaine, les prix passés ne sont souvent plus re-téléchargeables → une
    re-mesure live repasse tout en « non-conclusif » et fait disparaître la
    sélection (bug historique « Aucune sélection 24h jugée » malgré des tops).

    Pour chaque mesure 24h CONCLUSIVE (VRAI/FAUSSE) dont l'échéance tombe dans la
    semaine : on vérifie qu'elle était dans la Sélection du jour de décision
    (`selection_du_jour: true`, lu via load_selection_map sur la bulletin_date du
    record). Win rate = VRAI / (VRAI+FAUSSE) ; ampleur directionnelle = signe du
    call × realized_pct (LONG +, SHORT −), gagnante si ≥ 0. Dédup par
    (actif, échéance), dernier record gagnant. Zéro invention : realized_pct
    absent → exclu de l'ampleur (mais compté au win rate via son outcome).
    """
    from journaliste import (  # noqa: PLC0415
        iso_week_bounds, OUTCOME_VRAI, OUTCOME_FAUSSE,
    )
    from bilan_jour import load_selection_map  # noqa: PLC0415
    from datetime import timedelta  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    res = SelectionSemaine()
    if not measures_log.exists():
        return res

    # Dédup : dernier record par (actif, horizon, échéance) gagne (re-mesures).
    records: Dict[Tuple[str, str, str], dict] = {}
    for line in measures_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(r, dict) or r.get("horizon") != "24h":
            continue
        key = (str(r.get("actif")), "24h", str(r.get("echeance")))
        records[key] = r

    sel_cache: Dict[date, Dict[Tuple[str, str], bool]] = {}
    for r in records.values():
        if r.get("outcome") not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        try:
            ech = date.fromisoformat(str(r.get("echeance")))
        except (TypeError, ValueError):
            continue
        if not (monday <= ech <= sunday):
            continue
        # Jour de décision = bulletin_date du record (fallback échéance − 1).
        try:
            decision_day = date.fromisoformat(str(r.get("bulletin_date")))
        except (TypeError, ValueError):
            decision_day = ech - timedelta(days=1)
        actif = str(r.get("actif"))
        if decision_day not in sel_cache:
            sel_cache[decision_day] = load_selection_map(decision_day, decision_log_dir)
        if not sel_cache[decision_day].get((actif, "24h"), False):
            continue
        res.n_select += 1
        if r.get("outcome") == OUTCOME_VRAI:
            res.n_vrai += 1
        rp = r.get("realized_pct")
        concl = r.get("conclusion")
        if isinstance(rp, (int, float)) and concl in ("LONG", "SHORT"):
            mv = (1.0 if concl == "LONG" else -1.0) * float(rp)
            if mv >= 0:
                res.ampleurs_gagnantes.append(round(mv, 2))
            else:
                res.ampleurs_perdantes.append(round(mv, 2))
    return res


# ---------------------------------------------------------------------------
# POST-MORTEM CAUSAL — un pick enrichi = la jointure mesure ↔ drivers d'émission
# (spec data-analyst v3/docs/reco/bilan-hebdo-analyse-s9.md). C'est ce qui permet
# de dire POURQUOI un top a marché ou raté : news-driven vs quant-pur, drapeau de
# signal faible suivi à tort, et la news réelle qui a bougé l'actif. Zéro invention.
# ---------------------------------------------------------------------------

@dataclass
class PickSemaine:
    """Un pick de la Sélection 24h jugé cette semaine, enrichi de sa cause."""
    actif: str
    call: str                            # LONG / SHORT
    outcome: str                         # VRAI / FAUSSE
    realized_pct: Optional[float]        # mouvement brut signé
    mouvement_dir: Optional[float]       # signe(call) × realized_pct (favorable si ≥ 0)
    bulletin_date: date
    ratio_news: Optional[float]          # 0-1, part de news à l'émission
    mono_critere: bool = False
    mono_critere_nom: Optional[str] = None
    coin_flip: bool = False
    quasi_neutre: bool = False
    cause_news: Optional[str] = None     # résumé de la news high du jour (ou None)

    @property
    def vrai(self) -> bool:
        return self.outcome == "VRAI"

    @property
    def news_driven(self) -> bool:
        return isinstance(self.ratio_news, (int, float)) and self.ratio_news > 0.50

    @property
    def drapeau_faible(self) -> Optional[str]:
        """Libellé du drapeau de signal faible (priorité coin-flip > mono > quasi)."""
        if self.coin_flip:
            return "coin-flip"
        if self.mono_critere:
            return (f"mono-critère : {self.mono_critere_nom}"
                    if self.mono_critere_nom else "mono-critère")
        if self.quasi_neutre:
            return "quasi-neutre"
        return None


def _enrich_picks_semaine(
    now: datetime,
    measures_log: Path = MEASURES_LOG,
    decision_log_dir: Path = DECISION_LOG_DIR,
    events_path: Optional[Path] = None,
) -> List[PickSemaine]:
    """Picks de la Sélection 24h jugés cette semaine, enrichis (cause news +
    drapeaux d'émission). Même socle que selection_semaine (journal persisté +
    selection_du_jour) ; ajoute la jointure decision-log et la news via
    cause_news_high_apres. Dégradation propre : champ absent → None/False."""
    from journaliste import iso_week_bounds, OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415
    from bilan_jour import (  # noqa: PLC0415
        load_selection_map, load_conviction_records, cause_news_high_apres,
    )
    from datetime import timedelta  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    picks: List[PickSemaine] = []
    if not measures_log.exists():
        return picks

    records: Dict[Tuple[str, str, str], dict] = {}
    for line in measures_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(r, dict) or r.get("horizon") != "24h":
            continue
        records[(str(r.get("actif")), "24h", str(r.get("echeance")))] = r

    sel_cache: Dict[date, Dict[Tuple[str, str], bool]] = {}
    conv_cache: Dict[date, Dict[Tuple[str, str], dict]] = {}
    for r in records.values():
        if r.get("outcome") not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        try:
            ech = date.fromisoformat(str(r.get("echeance")))
        except (TypeError, ValueError):
            continue
        if not (monday <= ech <= sunday):
            continue
        try:
            bdate = date.fromisoformat(str(r.get("bulletin_date")))
        except (TypeError, ValueError):
            bdate = ech - timedelta(days=1)
        actif = str(r.get("actif"))
        if bdate not in sel_cache:
            sel_cache[bdate] = load_selection_map(bdate, decision_log_dir)
        if not sel_cache[bdate].get((actif, "24h"), False):
            continue
        if bdate not in conv_cache:
            conv_cache[bdate] = load_conviction_records(bdate, decision_log_dir)
        rec = conv_cache[bdate].get((actif, "24h")) or {}
        # ratio_news : on prend le driver d'émission p2_M7_ratio_news (proportion
        # 0-1 bien définie). PAS le champ measures-log « ratio_news » : c'est une
        # autre métrique non normalisée (valeurs > 1, jusqu'à ~480) → inutilisable
        # comme proportion. Absent → None (pas de classification news/quant).
        ratio = rec.get("p2_M7_ratio_news") if rec else None
        call = r.get("conclusion")
        rp = r.get("realized_pct")
        mv = ((1.0 if call == "LONG" else -1.0) * float(rp)
              if isinstance(rp, (int, float)) and call in ("LONG", "SHORT") else None)
        cause = None
        try:
            cause = cause_news_high_apres(actif, bdate, None, events_path)
        except Exception:  # noqa: BLE001 — cause best-effort, jamais bloquante
            cause = None
        picks.append(PickSemaine(
            actif=actif, call=str(call), outcome=str(r.get("outcome")),
            realized_pct=round(float(rp), 2) if isinstance(rp, (int, float)) else None,
            mouvement_dir=round(mv, 2) if mv is not None else None,
            bulletin_date=bdate,
            ratio_news=float(ratio) if isinstance(ratio, (int, float)) else None,
            mono_critere=bool(rec.get("mono_critere_dominant", False)),
            mono_critere_nom=rec.get("mono_critere_nom"),
            coin_flip=bool(rec.get("coin_flip", False)),
            quasi_neutre=bool(rec.get("quasi_neutre", False)),
            cause_news=cause,
        ))
    picks.sort(key=lambda p: (p.bulletin_date, p.actif))
    return picks


# ---------------------------------------------------------------------------
# SECTION 2 — Performance par TENDANCE 7j, par actif (cœur de la demande)
# ---------------------------------------------------------------------------
# Pour chaque actif : segmenter la semaine en phases de direction 7j CONSTANTE,
# et donner la perf directionnelle de chaque phase, mesurée depuis le prix de
# DÉBUT de segment (émission du jour de prise/bascule) jusqu'à la fin (veille de
# la bascule) ou « maintenant » (dernier prix dispo). Agrégé par cle_courante =
# ticker_principal (L023). WIN RATE ONLY = % directionnel, jamais d'€. Zéro
# invention : prix de réf manquant -> segment perf « — ».

@dataclass
class SegmentTendance:
    direction: str              # "LONG" / "SHORT"
    jours: List[date]           # jours de bourse du segment, ordonnés
    prix_debut: Optional[float] = None
    prix_fin: Optional[float] = None
    en_cours: bool = False

    @property
    def perf_pct(self) -> Optional[float]:
        """% de mouvement DANS LE SENS de la tendance. None si prix manquant."""
        pd, pf = self.prix_debut, self.prix_fin
        if not isinstance(pd, (int, float)) or not isinstance(pf, (int, float)) or pd == 0:
            return None
        signe = 1.0 if self.direction == "LONG" else -1.0
        return round(signe * (pf - pd) / pd * 100.0, 2)


@dataclass
class TendanceActif:
    actif: str
    ticker: Optional[str]
    segments: List[SegmentTendance] = field(default_factory=list)


def _decision_7j_du_jour(
    day: date, decision_log_dir: Path = DECISION_LOG_DIR
) -> Dict[str, str]:
    """Direction 7j (LONG/SHORT) par NOM d'actif, dernier record du jour `day`.

    Lit tous les fichiers decision-log `{day}-*.jsonl`, dernier record gagne (comme
    load_selection_map / load_conviction_map). Jour sans log -> dict vide (sauté,
    zéro invention).
    """
    out: Dict[str, str] = {}
    if not decision_log_dir.exists():
        return out
    prefix = day.isoformat()
    for fp in sorted(decision_log_dir.glob(f"{prefix}-*.jsonl")):
        try:
            for line in fp.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(rec, dict) or rec.get("bulletin_date") != prefix:
                    continue
                if rec.get("horizon") != "7j":
                    continue
                actif = rec.get("actif")
                conc = rec.get("conclusion_pm1")
                if actif and conc in ("LONG", "SHORT"):
                    out[str(actif)] = conc
        except OSError as e:
            logger.warning("decision-log illisible %s : %s", fp, e)
    return out


def _prix_du_jour(
    ticker: str,
    day: date,
    prix_emission_dir: Path = PRIX_EMISSION_DIR,
    prix_ouverture_dir: Path = PRIX_OUVERTURE_DIR,
) -> Optional[float]:
    """Prix d'émission du jour pour `ticker` (point d'exécution 7h, « bon prix »).

    Priorité : prix-emission/{day}*.json (tout suffixe horaire, ex. -07h/-08h),
    fallback prix-ouverture/{day}.json. None si introuvable (zéro invention).
    """
    if not ticker:
        return None
    # prix-emission : la date peut porter un suffixe horaire variable (-07h…).
    candidates = sorted(prix_emission_dir.glob(f"{day.isoformat()}*.json"))
    # On préfère le fichier sans suffixe puis le plus matinal (tri lexical OK : 07h<08h).
    exact = prix_emission_dir / f"{day.isoformat()}.json"
    ordered = ([exact] if exact.exists() else []) + [c for c in candidates if c != exact]
    for fp in ordered:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and ticker in data:
            try:
                return float(data[ticker])
            except (TypeError, ValueError):
                pass
    fp = prix_ouverture_dir / f"{day.isoformat()}.json"
    if fp.exists():
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(data, dict) and ticker in data:
                return float(data[ticker])
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    return None


def tendances_par_actif(
    now: datetime,
    fiches: Optional[Dict[str, dict]] = None,
    decision_log_dir: Path = DECISION_LOG_DIR,
    prix_emission_dir: Path = PRIX_EMISSION_DIR,
    prix_ouverture_dir: Path = PRIX_OUVERTURE_DIR,
) -> List[TendanceActif]:
    """Segmente la semaine ISO en phases de direction 7j CONSTANTE, par actif.

    Pour chaque jour de bourse de la semaine, lit la direction 7j de chaque actif
    (decision-log). Des jours consécutifs de même direction = un segment ; un
    changement = bascule = nouveau segment. Le prix de DÉBUT de segment = prix
    d'émission du 1er jour du segment ; le prix de FIN = prix d'émission du dernier
    jour du segment (veille de la bascule, ou « maintenant » = dernier dispo pour
    le segment en cours). Perf = % directionnel signé. Prix manquant -> perf « — ».
    """
    from journaliste import iso_week_bounds, load_fiches  # noqa: PLC0415
    from datetime import timedelta  # noqa: PLC0415

    fiches = fiches if fiches is not None else load_fiches()
    monday, sunday = iso_week_bounds(now)
    # Map nom d'actif -> ticker_principal (cle_courante, L023).
    ticker_par_actif: Dict[str, str] = {}
    for fiche in fiches.values():
        nom = (fiche.get("actif") or "").strip()
        tk = fiche.get("ticker_principal")
        if nom and tk:
            ticker_par_actif[nom] = tk

    # Direction 7j par jour de bourse de la semaine (jours sans log = sautés).
    jours = []
    d = monday
    while d <= sunday:
        dirs = _decision_7j_du_jour(d, decision_log_dir)
        if dirs:
            jours.append((d, dirs))
        d += timedelta(days=1)

    # Liste ordonnée et stable des actifs vus cette semaine.
    actifs_vus: List[str] = []
    for _d, dirs in jours:
        for a in dirs:
            if a not in actifs_vus:
                actifs_vus.append(a)
    actifs_vus.sort()

    resultats: List[TendanceActif] = []
    last_day = jours[-1][0] if jours else None

    for actif in actifs_vus:
        ticker = ticker_par_actif.get(actif)
        ta = TendanceActif(actif=actif, ticker=ticker)
        seg: Optional[SegmentTendance] = None
        for d, dirs in jours:
            direction = dirs.get(actif)
            if direction is None:
                continue  # actif non jugé ce jour -> sauté (zéro invention)
            if seg is None or direction != seg.direction:
                seg = SegmentTendance(direction=direction, jours=[d])
                ta.segments.append(seg)
            else:
                seg.jours.append(d)
        # Prix de début/fin de chaque segment.
        # FIN d'une phase = prix au moment de la BASCULE (= 1er jour du segment
        # suivant), pas le dernier jour où la direction tenait : sinon une phase
        # d'un seul jour a prix_debut == prix_fin → 0 % mécanique (bug S9), et les
        # phases multi-jours rataient le mouvement de leur dernier jour. La phase
        # EN COURS (dernière) n'a pas de bascule → on prend son dernier jour dispo
        # (≈ maintenant).
        n = len(ta.segments)
        for i, s in enumerate(ta.segments):
            s.prix_debut = _prix_du_jour(
                ticker, s.jours[0], prix_emission_dir, prix_ouverture_dir
            ) if ticker else None
            fin_day = ta.segments[i + 1].jours[0] if i < n - 1 else s.jours[-1]
            s.prix_fin = _prix_du_jour(
                ticker, fin_day, prix_emission_dir, prix_ouverture_dir
            ) if ticker else None
            s.en_cours = bool(s is ta.segments[-1] and last_day in s.jours)
        resultats.append(ta)
    return resultats


# ---------------------------------------------------------------------------
# Propositions du Manager (§4.5) — PROPOSE, n'applique JAMAIS
# ---------------------------------------------------------------------------
# Champs obligatoires (CA-W3) : Type, Actif(s), Critère(s), Constat, Proposition,
# Risque, Validation requise. Un champ vide = proposition rejetée par le système.

PROPOSITION_CHAMPS = (
    "type", "actifs", "criteres", "constat", "proposition", "risque", "validation",
)


def build_propositions(cellules: List[CelluleObs]) -> List[Dict[str, Any]]:
    """Génère 0..N propositions, UNIQUEMENT sur cellules faibles CONFIRMÉES.

    Une proposition n'existe que si la cellule est faible >= 2 semaines
    consécutives (N_eff>=10 ET Wilson_low<50%). Chaque champ est rempli avec des
    chiffres RÉELS du KPI (zéro invention). Le Manager n'applique rien : il
    demande une validation Thomas explicite.
    """
    props: List[Dict[str, Any]] = []
    faibles = sorted(
        [c for c in cellules if c.faible_confirmee],
        key=lambda c: (c.win_rate if c.win_rate is not None else 100.0),
    )
    for i, c in enumerate(faibles, start=1):
        wr = _fmt_pct(c.win_rate)
        props.append({
            "n": i,
            "titre": f"{c.actif} {c.horizon} · faiblesse confirmée sur 2 semaines",
            "type": "Ajustement à instruire (Thomas tranche le levier, rien n'est appliqué seul)",
            "actifs": c.actif,
            "criteres": "critère dominant à identifier dans le decision-log de la cellule",
            "constat": (
                f"{c.actif} {c.horizon} : {wr} de réussite sur {c.n_eff} paris mesurés. "
                "Sur les deux dernières semaines, même en étant prudent sur la marge "
                "d'erreur, la cellule reste sous 50% : ce n'est pas un coup de malchance "
                "passager, c'est une faiblesse structurelle."
            ),
            "proposition": (
                f"Revoir les critères de {c.actif} {c.horizon} : le système n'a pas "
                "correctement discriminé sur 2 semaines. Analyser le decision-log pour "
                "repérer le critère qui tire dans le mauvais sens, puis ajuster son poids "
                "dans la config de l'actif. Thomas valide avant toute modification."
            ),
            "risque": (
                "Sur-réaction à un régime de marché passager : le nombre de paris reste "
                "modeste, un ajustement de poids peut dégrader une autre période."
            ),
            "validation": "Thomas OUI / NON avant toute modification de config",
        })
    return props


def proposition_valide(prop: Dict[str, Any]) -> bool:
    """CA-W3 : tous les champs obligatoires non vides, sinon rejet."""
    for champ in PROPOSITION_CHAMPS:
        v = prop.get(champ)
        if v is None or (isinstance(v, str) and not v.strip()):
            return False
    return True


# ---------------------------------------------------------------------------
# Dates de sortie de warm-up par horizon (§6.2)
# ---------------------------------------------------------------------------

WARMUP_DATES = {
    "24h": "~début juillet 2026 (1 pari/jour de bourse, ~5/semaine -> N_eff>=15 en ~3 semaines)",
    "7j": "~début octobre 2026 (1 pari indépendant/semaine -> N_eff>=15 en ~15 semaines)",
    "1m": "hors portée horizon 6 mois (1 pari indépendant/mois -> ~15 mois)",
}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_bilan_semaine(
    now: Optional[datetime] = None,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    state_dir: Path = MANAGER_STATE_DIR,
    persist_state: bool = True,
) -> BilanSemaine:
    """Construit le bilan de la semaine + propositions du Manager.

    NE MODIFIE AUCUN FICHIER DE CONFIG (CA-W4). Persiste uniquement l'état de
    détection (data/, pas config/). Le markdown produit est WIN-RATE-ONLY.
    """
    from journaliste import iso_week_label, iso_week_bounds  # noqa: PLC0415

    now = now or datetime.now(PARIS_TZ)
    now = now.astimezone(PARIS_TZ)
    iso = iso_week_label(now)
    monday, sunday = iso_week_bounds(now)

    prev_iso = _prev_iso_label(now)
    prev_candidates = load_candidates_state(prev_iso, state_dir)

    cellules, candidates_now, measures = collect_cellules(
        now, fiches=fiches, fetch_price=fetch_price, prev_candidates=prev_candidates
    )

    conv = _conviction_semaine(measures, now)
    sel = selection_semaine(now)
    tend = tendances_par_actif(now, fiches=fiches)
    picks = _enrich_picks_semaine(now)

    bilan = BilanSemaine(
        iso=iso, lundi=monday, dimanche=sunday, now=now, cellules=cellules,
        n_forte=conv.n_forte, taux_forte=conv.taux_forte,
        n_faible_conv=conv.n_faible, taux_faible_conv=conv.taux_faible,
        selection=sel, tendances=tend, picks=picks,
    )

    propositions = [p for p in build_propositions(cellules) if proposition_valide(p)]
    bilan.propositions = propositions

    # Observations sans proposition : candidates faibles non encore confirmées
    # (1ère semaine) + cellules en zone d'observation N_eff 5-9.
    for c in cellules:
        if c.candidate_faible and not c.faible_confirmee:
            bilan.observations.append(
                f"{c.actif} {c.horizon} : en observation cette semaine "
                f"({_fmt_pct(c.win_rate)} de réussite sur {c.n_eff} paris). Si la "
                "faiblesse se confirme la semaine prochaine, une proposition "
                "d'ajustement sera préparée."
            )
        elif (
            N_EFF_OBSERVE <= c.n_eff < N_EFF_PROPOSE
            and c.wilson_low is not None
            and c.wilson_low < WILSON_FAIBLE
        ):
            bilan.observations.append(
                f"{c.actif} {c.horizon} : seulement {c.n_eff} paris mesurés, pas assez "
                f"pour conclure. On attend {N_EFF_PROPOSE} paris avant d'agir."
            )

    bilan.markdown = render_bilan_semaine(bilan)

    # Persistance de l'état de détection pour le run S+1 (data/, jamais config/).
    if persist_state:
        try:
            save_candidates_state(iso, candidates_now, state_dir)
        except OSError as e:
            logger.warning("save_candidates_state KO (non bloquant) : %s", e)

    return bilan


def _read_weekly_archive(iso: str) -> Optional[str]:
    """Lit l'archive hebdo win-rate-{ISO}.md telle quelle (CA-W2). None si absente."""
    fp = PERFORMANCE_WEEKLY_DIR / f"win-rate-{iso}.md"
    if not fp.exists():
        return None
    try:
        return fp.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("archive hebdo illisible %s : %s", fp, e)
        return None


def _fmt_signed_pct(v: Optional[float]) -> str:
    """% signé à la française (« +1,5 % », « -0,8 % »). « — » si None (placeholder)."""
    if not isinstance(v, (int, float)):
        return "—"
    # Normalise le zéro négatif (-0.0) en zéro positif (cosmétique).
    if v == 0:
        v = 0.0
    s = f"{v:+.1f}".replace(".", ",")
    return f"{s} %"


def _fmt_jours_segment(jours: List[date]) -> str:
    """Étiquette lisible des jours d'un segment (« lun→mer », « jeu »)."""
    JJ = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")
    if not jours:
        return "—"
    debut = JJ[jours[0].weekday()]
    fin = JJ[jours[-1].weekday()]
    return debut if debut == fin else f"{debut}→{fin}"


def _render_section1_selection(bilan: BilanSemaine, L: List[str]) -> None:
    """SECTION 1 — Performance des 24h sélectionnés (la semaine)."""
    L.append("## 1. Performance des 24h sélectionnés (la semaine)")
    L.append("")
    L.append(
        "> Nos « top du jour » (la Sélection, horizon 24h) agrégés sur la semaine : "
        "taux de réussite et ampleur moyenne du mouvement, en pourcentage (jamais en euros)."
    )
    L.append("")
    s = bilan.selection
    if s is None or s.n_select == 0:
        L.append(
            "Aucune sélection 24h jugée cette semaine (pas de top du jour conclusif "
            "sur les jours de bourse écoulés)."
        )
        L.append("")
        return
    wr = _fmt_pct(s.win_rate)
    L.append("| Indicateur | Valeur |")
    L.append("|---|---|")
    L.append(f"| Win rate de la sélection | {wr} ({s.n_vrai}/{s.n_select} jugées) |")
    ng = len(s.ampleurs_gagnantes)
    npd = len(s.ampleurs_perdantes)
    amp_g = _fmt_signed_pct(s.ampleur_moy_gagnantes) if ng else "—"
    amp_p = _fmt_signed_pct(s.ampleur_moy_perdantes) if npd else "—"
    L.append(f"| Ampleur moyenne des sélections gagnantes | {amp_g} ({ng}) |")
    L.append(f"| Ampleur moyenne des sélections perdantes | {amp_p} ({npd}) |")
    L.append("")
    L.append(
        "> Ampleur = moyenne du mouvement dans le sens du call (signe selon LONG/SHORT), "
        "depuis le prix de référence d'émission. Sélection dont un prix manque = exclue "
        "de l'ampleur (zéro donnée fabriquée)."
    )
    L.append("")


def _verdict_segment(perf: Optional[float]) -> str:
    """Verdict visuel d'une phase de tendance : ✅ gagnant / ❌ perdant / ⚪ neutre
    / — sans donnée. Seuil de matérialité partagé (_PERF_MATERIELLE_PCT) : sous le
    seuil = mouvement négligeable (⚪), pas une vraie réussite/échec."""
    if perf is None:
        return "—"
    if abs(perf) < _PERF_MATERIELLE_PCT:
        return "⚪"
    return "✅" if perf > 0 else "❌"


def _render_section2_tendances(bilan: BilanSemaine, L: List[str]) -> None:
    """SECTION 2 — Performance par TENDANCE 7j, par actif (tableau visuel)."""
    L.append("## 2. Performance par tendance 7 jours, par actif")
    L.append("")
    L.append(
        "> Une ligne par phase de direction 7j constante. À chaque bascule (LONG "
        "vers SHORT ou l'inverse) commence une nouvelle phase. Perf = mouvement "
        "dans le sens de la tendance, du prix d'émission du jour de prise au dernier "
        "prix de la phase. ✅ gagnant · ❌ perdant · ⚪ négligeable · — prix manquant "
        "(jamais inventé)."
    )
    L.append("")
    tendances = [t for t in bilan.tendances if t.segments]
    if not tendances:
        L.append(
            "Aucune direction 7j lisible cette semaine (decision-log absent sur les "
            "jours écoulés) : rien à segmenter."
        )
        L.append("")
        return
    L.append("| Actif | Tendance | Période | Perf (sens tendance) | Résultat |")
    L.append("|---|---|---|---|---|")
    for t in tendances:
        for i, s in enumerate(t.segments):
            # Actif affiché une seule fois par groupe (lecture en colonnes).
            actif_cell = f"**{t.actif}**" if i == 0 else ""
            tendance_cell = s.direction + (" (en cours)" if s.en_cours else "")
            periode = _fmt_jours_segment(s.jours)
            perf = _fmt_signed_pct(s.perf_pct)
            verdict = _verdict_segment(s.perf_pct)
            L.append(f"| {actif_cell} | {tendance_cell} | {periode} | {perf} | {verdict} |")
    L.append("")


def render_bilan_semaine(bilan: BilanSemaine) -> str:
    L: List[str] = []
    # [I-7 audit visuel 12/06] : H1 pour tous les rapports (harmonisation des
    # niveaux de titre — le bilan semaine était en H2). Le range lundi→dimanche
    # reste présent (lu par build_html.weekHumanTitle pour le titre humain).
    L.append(f"# Bilan semaine · {bilan.iso} ({bilan.lundi.isoformat()} → {bilan.dimanche.isoformat()})")
    L.append("")
    L.append(f"- Généré : {horodatage_fr(bilan.now)} (samedi matin, Paris)")
    L.append("- WIN RATE ONLY · aucune mesure monétaire. Le Manager PROPOSE, Thomas VALIDE.")
    L.append(
        "- WR tradable = VRAI / (VRAI + FAUSSE + non-conclusif) · inclut les jours "
        "sous seuil où une position aurait quand même été prise (toujours ≤ Win rate)."
    )
    L.append("")

    # ===================================================================
    # SECTION 1 — Performance des 24h sélectionnés (la semaine)
    # ===================================================================
    _render_section1_selection(bilan, L)

    # ===================================================================
    # SECTION 2 — Performance par tendance 7j, par actif
    # ===================================================================
    _render_section2_tendances(bilan, L)

    # ===================================================================
    # SECTION 3 — Ce qu'on a bien fait cette semaine (analyse + POURQUOI)
    # Recentrée : uniquement l'analyse de ce qui a marché, avec la cause
    # traçable. Le détail win rate (tables) vit sur la page Performance et,
    # in extenso, dans l'annexe technique repliée en pied de bilan.
    # ===================================================================
    L.append("## 3. Ce qu'on a bien fait cette semaine")
    L.append("")
    points_forts = _points_forts(bilan)
    if points_forts:
        for p in points_forts:
            L.append(f"- {p}")
    else:
        L.append(
            "Rien de statistiquement notable cette semaine (warm-up, N encore "
            "modeste sur la plupart des cellules)."
        )
    L.append("")

    # ===================================================================
    # SECTION 4 — Ce qu'on doit améliorer (analyse + POURQUOI + propositions)
    # Recentrée : les faiblesses avec leur cause, puis les propositions
    # actionnables à valider. Le monitoring fin (cellules à surveiller,
    # warm-up, news vs quant) descend dans l'annexe technique.
    # ===================================================================
    L.append("## 4. Ce qu'on doit améliorer")
    L.append("")
    points_faibles = _points_faibles(bilan)
    if points_faibles:
        for p in points_faibles:
            L.append(f"- {p}")
    else:
        L.append(
            "Aucun point faible confirmé cette semaine (aucune cellule sous le seuil "
            "de détection ni tendance perdante marquée)."
        )
    L.append("")

    # --- Propositions d'ajustement (à valider Thomas) — actionnable, on garde ---
    L.append("### Propositions d'ajustement (à valider Thomas)")
    L.append("")
    if bilan.propositions:
        for p in bilan.propositions:
            L.append(f"#### Proposition P{p['n']} · {p['titre']}")
            L.append("")
            L.append(f"**Type** : {p['type']}")
            L.append(f"**Actif(s) concerné(s)** : {p['actifs']}")
            L.append(f"**Critère(s) concerné(s)** : {p['criteres']}")
            L.append(f"**Constat** : {p['constat']}")
            L.append(f"**Proposition** : {p['proposition']}")
            L.append(f"**Risque** : {p['risque']}")
            L.append(f"**Validation requise** : {p['validation']}")
            L.append("")
            L.append("- [ ] Thomas valide · appliquer au prochain run")
            L.append("- [ ] Thomas refuse · garder en observation")
            L.append("- [ ] Thomas demande plus de données · reporter à S+1")
            L.append("")
    else:
        L.append(
            "Aucun ajustement proposé cette semaine : toutes les cellules avec assez de "
            "paris mesurés restent au-dessus du seuil de confiance. On continue de mesurer "
            "avant d'agir."
        )
    L.append("")

    # ===================================================================
    # SECTION 5 — Les learnings de la semaine
    # ===================================================================
    L.append("## 5. Les learnings de la semaine")
    L.append("")
    L.append(
        "> Synthèse actionnable et déterministe, dérivée des sections 1 à 4. "
        "Chaque learning repose sur un seuil chiffré franchi (jamais d'interprétation libre)."
    )
    L.append("")
    learnings = _learnings_semaine(bilan)
    if learnings:
        for ln in learnings:
            L.append(f"- {ln}")
    else:
        L.append(
            "Pas de learning net cette semaine : échantillon insuffisant (warm-up). "
            "On continue de mesurer avant d'agir."
        )
    L.append("")

    # ===================================================================
    # ANNEXE TECHNIQUE — repliée par défaut (détail de mesure, pour qui veut
    # creuser). Sort les tableaux denses des sections 3/4 pour qu'elles restent
    # de l'ANALYSE. Rendu : <details> HTML (marked le laisse passer tel quel).
    # ===================================================================
    _render_annexe_technique(bilan, L)

    return "\n".join(L)


def _render_annexe_technique(bilan: BilanSemaine, L: List[str]) -> None:
    """Détail de mesure dense, replié — déplacé hors des sections 3/4 (analyse)."""
    L.append('<details class="weekly-annex">')
    L.append("<summary>Annexe technique · détail de mesure (replié)</summary>")
    L.append("")
    L.append(
        "> Le détail win rate par cellule est aussi consultable sur la page "
        "**Performance**. Ci-dessous : la photo figée de la semaine."
    )
    L.append("")

    # --- Win rate de la semaine (archive hebdo prise telle quelle) ---
    L.append("### Win rate de la semaine")
    L.append("")
    archive = _read_weekly_archive(bilan.iso)
    if archive:
        L.append(f"> Source : `win-rate-{bilan.iso}.md` (archive hebdo, prise telle quelle).")
        L.append("")
        body = "\n".join(ln for ln in archive.splitlines() if not ln.startswith("# ")).strip()
        L.append(body)
    else:
        L.append(f"> Archive `win-rate-{bilan.iso}.md` absente · produite au prochain run Journaliste.")
    L.append("")

    # --- Win rate par conviction ---
    L.append("### Win rate par conviction")
    L.append("")
    L.append("| Conviction | N paris | Win rate | Interprétation |")
    L.append("|---|---|---|---|")
    tf = _fmt_pct(bilan.taux_forte) if bilan.n_forte >= 3 else "— (N insuffisant)"
    tw = _fmt_pct(bilan.taux_faible_conv) if bilan.n_faible_conv >= 3 else "— (N insuffisant)"
    interp_f = _interp_conviction(bilan.taux_forte, bilan.n_forte, forte=True)
    interp_w = _interp_conviction(bilan.taux_faible_conv, bilan.n_faible_conv, forte=False)
    L.append(f"| Forte (|score| ≥ seuil, 0 drapeau ◧/⇆/↯/~) | {bilan.n_forte} | {tf} | {interp_f} |")
    L.append(f"| Faible (quasi-neutre, mono-critère, coin-flip) | {bilan.n_faible_conv} | {tw} | {interp_w} |")
    L.append("")

    # --- Cellules porteuses ---
    L.append("### Cellules porteuses (ce qui marche)")
    L.append("")
    porteuses = sorted(
        [c for c in bilan.cellules if c.porteuse],
        key=lambda c: (c.win_rate if c.win_rate is not None else 0.0), reverse=True,
    )
    if porteuses:
        L.append("| Actif | Horizon | Win rate | WR tradable | N_eff | Signal |")
        L.append("|---|---|---|---|---|---|")
        for c in porteuses:
            L.append(
                f"| {c.actif} | {c.horizon} | {_fmt_pct(c.win_rate)} | "
                f"{_fmt_pct(c.wr_tradable)} | {c.n_eff} | "
                f"solide (≥ {WINRATE_PORTEUSE:.0f}% sur N_eff ≥ {N_EFF_PORTEUSE}) |"
            )
    else:
        L.append(f"Aucune cellule avec N_eff ≥ {N_EFF_PORTEUSE} et win rate ≥ {WINRATE_PORTEUSE:.0f}% · observer.")
    L.append("")

    # --- Cellules à surveiller ---
    L.append("### Cellules à surveiller")
    L.append("")
    surveiller = sorted(
        [c for c in bilan.cellules if c.candidate_faible],
        key=lambda c: (c.win_rate if c.win_rate is not None else 100.0),
    )
    if surveiller:
        L.append("| Actif | Horizon | Raison | Win rate | N_eff | Wilson_low |")
        L.append("|---|---|---|---|---|---|")
        for c in surveiller:
            raison = "faible confirmée (≥2 sem.)" if c.faible_confirmee else "candidate (1ère sem.)"
            L.append(
                f"| {c.actif} | {c.horizon} | {raison} | {_fmt_pct(c.win_rate)} | "
                f"{c.n_eff} | {_fmt_pct(c.wilson_low)} |"
            )
    else:
        L.append("Aucune cellule sous le seuil de détection (N_eff ≥ 10 ET Wilson_low < 50%).")
    L.append("")

    # --- Observations sans proposition ---
    L.append("### Observations sans proposition")
    L.append("")
    if bilan.observations:
        for o in bilan.observations:
            L.append(f"- {o}")
    else:
        L.append("Rien en zone d'observation cette semaine.")
    L.append("")

    # --- Sortie de warm-up par horizon ---
    L.append("### Sortie de warm-up par horizon")
    L.append("")
    L.append("| Horizon | Date estimée de significativité |")
    L.append("|---|---|")
    for h in ("24h", "7j", "1m"):
        L.append(f"| {h} | {WARMUP_DATES[h]} |")
    L.append("")
    L.append(
        "> Le 7j est en warm-up jusqu'en octobre 2026 ; le 1m n'est pas mesurable "
        "statistiquement dans les 6 premiers mois. Le Manager se concentre sur le "
        "24h pendant cette période."
    )
    L.append("")

    # --- Justesse des news vs quant (informatif) ---
    L.append("### Justesse des news vs quant (informatif)")
    L.append("")
    L.append(
        "> Mesure SÉPARÉE de la justesse des calls *dominés par les news* "
        "(`ratio_news` > 50 % à l'émission) vs les calls *quant-purs*, par horizon. "
        "Informatif uniquement · n'alimente aucune proposition. Garde-fou : "
        f"N < {_NEWS_MIN_N} ⇒ « en chauffe », jamais présenté comme significatif."
    )
    L.append("")
    try:
        nq = _news_vs_quant_winrate()
        L.append("| Horizon | News-driven | Quant-pures |")
        L.append("|---|---|---|")
        for h in ("24h", "7j", "1m"):
            L.append(f"| {h} | {_fmt_news_cell(nq[h]['news'])} | {_fmt_news_cell(nq[h]['quant'])} |")
        L.append("")
        L.append(
            "> Rapport détaillé (semaine par semaine, verdict) : "
            "`v3/audit/news-winrate-mesure.md`."
        )
    except Exception as e:  # noqa: BLE001 — vue informative best-effort, jamais bloquante
        logger.warning("vue news vs quant KO (non bloquant) : %s", e)
        L.append("> Vue indisponible ce run (lecture measures-log/decision-log).")
    L.append("")
    L.append("</details>")
    L.append("")


# ---------------------------------------------------------------------------
# Synthèses des sections 3/4/5 (déterministes, dérivées des chiffres réels)
# ---------------------------------------------------------------------------

def _segments_signes(bilan: BilanSemaine) -> Tuple[List[str], List[str]]:
    """(gagnants, perdants) parmi les segments de tendance avec perf mesurable.

    Seuil de matérialité : |perf| >= _PERF_MATERIELLE_PCT (un segment à 0 % ou
    sous le seuil = mouvement négligeable, pas un learning). Zéro invention :
    segment sans perf (« — ») ignoré.
    """
    gagnants: List[str] = []
    perdants: List[str] = []
    for t in bilan.tendances:
        n_seg = len(t.segments)
        for i, s in enumerate(t.segments):
            p = s.perf_pct
            if p is None or abs(p) < _PERF_MATERIELLE_PCT:
                continue
            cause = _cause_segment(s, i, n_seg, gagnant=(p > 0))
            libelle = (
                f"{t.actif} {s.direction} ({_fmt_jours_segment(s.jours)}) "
                f"{_fmt_signed_pct(p)} · {cause}"
            )
            (gagnants if p > 0 else perdants).append(libelle)
    return gagnants, perdants


def _cause_segment(s: "SegmentTendance", idx: int, n_seg: int, gagnant: bool) -> str:
    """POURQUOI traçable d'une phase, dérivé de la STRUCTURE des segments (zéro
    invention) : direction stable (continuation) vs bascule (changement de
    tendance capté ou subi). C'est la seule cause déductible des prix + du
    decision-log, sans interprétation libre."""
    suivi_dun_flip = idx < n_seg - 1          # une autre phase suit → bascule après
    issu_dun_flip = idx > 0                    # cette phase succède à une bascule
    if gagnant:
        if n_seg == 1:
            return "tendance stable tenue (le directionnel s'est prolongé dans le bon sens)"
        if issu_dun_flip:
            return f"bascule {s.direction} captée (le retournement a été suivi à temps)"
        return "phase de tendance bien suivie avant bascule"
    # perdant
    if suivi_dun_flip:
        return "tendance retournée contre le call (une bascule a suivi cette phase)"
    if issu_dun_flip:
        return "bascule prise à contre-sens (le retournement n'a pas payé)"
    return "le mouvement est allé contre la direction tenue sur la phase"


def _ratio_pct(p: "PickSemaine") -> str:
    """Ratio news en % entier, ou '?' si non disponible (zéro invention)."""
    return f"{p.ratio_news * 100:.0f}%" if isinstance(p.ratio_news, (int, float)) else "?"


def _points_forts(bilan: BilanSemaine) -> List[str]:
    """SECTION 3 — ce qui a marché et POURQUOI (post-mortem causal, spec S9).

    Priorité : cause tracée par pick (3.1) > bascules captées / continuations
    (3.2) > conviction (3.3) > comptage sélection (3.4, seulement si rien d'autre).
    """
    pts: List[str] = []
    gagnants_pick = [p for p in bilan.picks if p.vrai]

    # Règle 3.1 — picks gagnants, cause par pick (news-driven / quant / paradoxe).
    for p in gagnants_pick:
        drap = p.drapeau_faible
        if p.vrai and drap:  # paradoxe : succès sur signal classé faible
            pts.append(
                f"{p.actif} {p.call} a gagné MALGRÉ un signal classé faible "
                f"(drapeau {drap}). Pas de conclusion : on garde le garde-fou, un "
                "coup réussi ne valide pas un signal faible."
            )
        elif p.news_driven and p.cause_news:
            pts.append(
                f"{p.actif} {p.call} : bon flair news (part news {_ratio_pct(p)}). "
                f"{p.cause_news} a poussé dans notre sens."
            )
        elif p.news_driven:
            pts.append(
                f"{p.actif} {p.call} : call orienté news (part news {_ratio_pct(p)}), "
                "le marché est allé dans notre sens (catalyseur précis non tracé)."
            )
        else:
            pts.append(
                f"{p.actif} {p.call} : call quant-pur confirmé (part news {_ratio_pct(p)}), "
                "le mouvement a suivi nos critères de tendance, sans news déterminante."
            )

    # Règle 3.2 — tendances 7j gagnantes (continuation / bascule captée).
    gagnants_seg, _ = _segments_signes(bilan)
    if gagnants_seg:
        pts.append("Tendances 7j bien suivies : " + " ; ".join(gagnants_seg[:3]) + ".")

    # Règle 3.3 — conviction forte qui paie.
    if bilan.n_forte >= 3 and bilan.taux_forte is not None and bilan.taux_forte >= 70.0:
        pts.append(
            f"Le tri par conviction a payé : {_fmt_pct(bilan.taux_forte)} de réussite "
            f"sur {bilan.n_forte} paris à conviction forte."
        )

    # Règle 3.4 — filet : comptage sélection, seulement si rien de causal au-dessus.
    s = bilan.selection
    if not pts and s is not None and s.n_select >= 3 and s.win_rate is not None and s.win_rate >= 60.0:
        pts.append(
            f"La Sélection 24h tient : {_fmt_pct(s.win_rate)} sur {s.n_select} tops jugés "
            f"({s.n_vrai} gagnants)."
        )
    return pts[:4]


def _points_faibles(bilan: BilanSemaine) -> List[str]:
    """SECTION 4 — ce qu'on doit améliorer et POURQUOI (post-mortem causal, spec S9).

    Pick perdant par pick : news ratée (CAS A), signal faible suivi à tort (CAS B),
    ou call quant solide raté (CAS C). Puis tendances perdantes, alarme sélection,
    cellules faibles (reformulées sans jargon Wilson).
    """
    pts: List[str] = []
    perdants_pick = [p for p in bilan.picks if not p.vrai]

    # Règle 4.1 — picks perdants, cause par pick.
    for p in perdants_pick:
        drap = p.drapeau_faible
        if p.news_driven and p.cause_news:  # CAS A : news ratée
            pts.append(
                f"{p.actif} {p.call} raté : call orienté news (part news {_ratio_pct(p)}). "
                f"{p.cause_news} a dominé le marché à CONTRE-SENS de notre position. Ce "
                "catalyseur n'était pas (ou mal) pris dans notre synthèse."
            )
        elif p.news_driven:  # CAS A bis : news-driven mais aucun catalyseur tracé
            pts.append(
                f"{p.actif} {p.call} raté : call orienté news (part news {_ratio_pct(p)}) "
                "mais aucun catalyseur tracé dans l'events-log. Mouvement adverse inexpliqué."
            )
        elif drap:  # CAS B : signal faible suivi à tort
            pts.append(
                f"{p.actif} {p.call} raté : pari pris sur un signal classé FAIBLE "
                f"(drapeau {drap}). Ce type de signal ne devrait pas entrer dans la Sélection."
            )
        elif p.cause_news:  # CAS C : quant solide raté, mais une news adverse existait
            pts.append(
                f"{p.actif} {p.call} raté : signal quant solide (aucun drapeau), mais "
                f"{p.cause_news} l'a contre-pied. News possiblement sous-pondérée au scoring."
            )
        else:  # CAS C bis : quant solide raté, cause non identifiée
            pts.append(
                f"{p.actif} {p.call} raté : signal quant solide (aucun drapeau), cause non "
                "identifiée (aucune news high tracée). À revoir si le pattern se répète."
            )

    # Règle 4.2 — tendances 7j à contre-sens (retournement subi / faux flip).
    _, perdants_seg = _segments_signes(bilan)
    if perdants_seg:
        pts.append("Tendances 7j à contre-sens : " + " ; ".join(perdants_seg[:3]) + ".")

    # Règle 4.3 — alarme globale sélection (complète, ne duplique pas les actifs cités).
    s = bilan.selection
    if s is not None and s.n_select >= 3 and s.win_rate is not None and s.win_rate < 50.0 \
            and not perdants_pick:
        pts.append(
            f"La Sélection 24h sous la barre : {_fmt_pct(s.win_rate)} sur {s.n_select} tops jugés."
        )

    # Règle 4.5 — cellules faibles confirmées (sans jargon Wilson).
    confirmees = [c for c in bilan.cellules if c.faible_confirmee]
    if confirmees:
        noms = ", ".join(f"{c.actif} {c.horizon} ({_fmt_pct(c.win_rate)})" for c in confirmees)
        pts.append(
            f"Cellules faibles sur 2 semaines : {noms}. Pas un coup de malchance passager, "
            "une faiblesse structurelle : une proposition d'ajustement est ci-dessous."
        )
    return pts[:4]


def _learnings_semaine(bilan: BilanSemaine) -> List[str]:
    """SECTION 5 — learnings actionnables ([observation chiffrée] + [action à J+7]).

    Max 3. Priorité : drapeaux (5.1) > news vs quant (5.2) > conviction (5.4) >
    prudence sélection (5.5) > fallback (5.6).
    """
    out: List[str] = []
    picks = bilan.picks

    # Règle 5.1 — drapeaux de signal faible qui ratent.
    picks_drap = [p for p in picks if p.drapeau_faible]
    rates_drap = [p for p in picks_drap if not p.vrai]
    if rates_drap:
        out.append(
            f"Les picks au signal faible (coin-flip / mono-critère) ont raté "
            f"{len(rates_drap)}/{len(picks_drap)} fois cette semaine. À surveiller : si le "
            "pattern se confirme la semaine prochaine, durcir le filtre (un signal faible "
            "ne passe pas dans le top 3)."
        )

    # Règle 5.2 — news-driven vs quant-pur sur les picks de la semaine.
    nd = [p for p in picks if p.news_driven]
    qp = [p for p in picks if p.ratio_news is not None and not p.news_driven]
    if len(nd) >= 2 or len(qp) >= 2:
        def _wr(lst):
            return (sum(1 for p in lst if p.vrai) / len(lst) * 100.0) if lst else None
        wn, wq = _wr(nd), _wr(qp)
        morceaux = []
        if wn is not None:
            morceaux.append(f"news-driven {wn:.0f}% ({len(nd)})")
        if wq is not None:
            morceaux.append(f"quant-pur {wq:.0f}% ({len(qp)})")
        verdict = ""
        if wn is not None and wq is not None and (len(nd) < 3 or len(qp) < 3):
            verdict = " N encore faible dans un segment, ne pas généraliser."
        elif wn is not None and wq is not None:
            verdict = (" Le flair news a mieux payé." if wn > wq
                       else " Le quant a mieux performé que les calls news." if wq > wn
                       else " Égalité news / quant cette semaine.")
        out.append("Calls cette semaine : " + ", ".join(morceaux) + "." + verdict)

    # Règle 5.4 — conviction forte vs faible (écart > 10 pts).
    if (bilan.n_forte >= 3 and bilan.n_faible_conv >= 3
            and bilan.taux_forte is not None and bilan.taux_faible_conv is not None):
        ecart = bilan.taux_forte - bilan.taux_faible_conv
        if ecart > 10:
            out.append(
                f"La conviction forte a bien discriminé ({_fmt_pct(bilan.taux_forte)} vs "
                f"{_fmt_pct(bilan.taux_faible_conv)} en faible) : ne pas assouplir le filtre."
            )
        elif ecart < -10:
            out.append(
                f"Anomalie : la conviction faible ({_fmt_pct(bilan.taux_faible_conv)}) dépasse "
                f"la forte ({_fmt_pct(bilan.taux_forte)}). N encore modeste, à surveiller sans "
                "conclure avant plus de paris."
            )

    # Règle 5.5 — sélection peut-être trop prudente.
    s = bilan.selection
    if (len(out) < 3 and s is not None and 1 <= s.n_select <= 2
            and s.win_rate is not None and s.win_rate >= 60.0):
        out.append(
            f"Seulement {s.n_select} pick(s) jugé(s) pour {_fmt_pct(s.win_rate)} de réussite : "
            "sélection peut-être trop prudente. À surveiller : si le taux tient au-dessus de "
            "60% sur plus de paris, envisager d'élargir un peu le top 3."
        )

    # Règle 5.6 — fallback unique.
    if not out:
        out.append(
            "Pas de learning net cette semaine : trop peu de paris par catégorie (warm-up) "
            "pour conclure de façon fiable. On continue de mesurer."
        )
    return out[:3]


# Seuil de matérialité d'un mouvement de tendance (% directionnel) pour qu'il
# compte comme learning. En-dessous = bruit, ignoré (zéro sur-interprétation).
_PERF_MATERIELLE_PCT = 0.5


# Garde-fou honnêteté partagé avec le rapport backfill (cohérence du seuil).
_NEWS_MIN_N = 15
_NEWS_RATIO_THRESHOLD_PCT = 50.0


def _fmt_news_cell(b: Tuple[int, int]) -> str:
    """Formate (vrai, faux) en win-rate avec garde-fou N<_NEWS_MIN_N."""
    vrai, faux = b
    n = vrai + faux
    if n == 0:
        return "— (0 jugé)"
    wr = 100.0 * vrai / n
    if n < _NEWS_MIN_N:
        return f"{wr:.0f}% [N={n} — en chauffe]"
    return f"{wr:.0f}% [N={n}]"


def _news_vs_quant_winrate() -> Dict[str, Dict[str, Tuple[int, int]]]:
    """Win-rate news-driven vs quant-pures par horizon, depuis measures-log.

    Pour chaque mesure jugée (VRAI/FAUX), classe la cellule news/quant via le
    champ persisté `ratio_news` (forward) ; à défaut via jointure decision-log
    d'émission (load_ratio_news_map). NC exclus. Best-effort, lecture seule.
    """
    import journaliste as jr  # noqa: PLC0415

    measures_log = ROOT / "data" / "measures-log.jsonl"
    out: Dict[str, Dict[str, Tuple[int, int]]] = {
        h: {"news": (0, 0), "quant": (0, 0)} for h in ("24h", "7j", "1m")
    }
    if not measures_log.exists():
        return out
    ratio_cache: Dict[str, Dict[Tuple[str, str], float]] = {}

    def _add(h: str, g: str, win: bool) -> None:
        v, f = out[h][g]
        out[h][g] = (v + (1 if win else 0), f + (0 if win else 1))

    for line in measures_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        outcome = r.get("outcome")
        h = r.get("horizon")
        if outcome not in ("VRAI", "FAUSSE") or h not in out:
            continue
        rn = r.get("ratio_news")
        if not isinstance(rn, (int, float)) or isinstance(rn, bool):
            bd = r.get("bulletin_date")
            if bd not in ratio_cache:
                try:
                    from datetime import date as _date  # noqa: PLC0415
                    ratio_cache[bd] = jr.load_ratio_news_map(_date.fromisoformat(bd))
                except Exception:  # noqa: BLE001
                    ratio_cache[bd] = {}
            rn = ratio_cache[bd].get((r.get("actif"), h))
        if not isinstance(rn, (int, float)) or isinstance(rn, bool):
            continue  # inconnu (pré-instrumentation) → exclu de la comparaison
        g = "news" if rn > _NEWS_RATIO_THRESHOLD_PCT else "quant"
        _add(h, g, outcome == "VRAI")
    return out


def _interp_conviction(taux: Optional[float], n: int, forte: bool) -> str:
    if n < 3:
        return "attendre N ≥ 3"
    if taux is None:
        return "—"
    if forte:
        return "signal fiable" if taux >= 70.0 else "edge non confirmé"
    return "bruit — à éviter" if taux < 55.0 else "à confirmer (N_eff > 10)"


def write_bilan_semaine(bilan: BilanSemaine, out_dir: Path = BILAN_SEMAINE_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    fp = out_dir / f"{bilan.iso}.md"
    fp.write_text(bilan.markdown, encoding="utf-8")
    return fp


def main(argv: Optional[List[str]] = None) -> int:
    """CLI : produit le bilan de la semaine + propositions Manager.

    Le déclenchement samedi matin (guard weekday()==5, bypass is_trading_day) est
    géré par l'infra. Ici on construit et on écrit le rapport.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    now = datetime.now(PARIS_TZ)
    bilan = build_bilan_semaine(now=now)
    out = write_bilan_semaine(bilan)
    logger.info(
        "bilan semaine écrit : %s (%d propositions, %d observations)",
        out, len(bilan.propositions), len(bilan.observations),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
