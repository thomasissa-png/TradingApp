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
import re
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
    edge_familles: List["EdgeFamille"] = field(default_factory=list)  # où concentrer (S9)
    detail_24h: List["Detail24hActif"] = field(default_factory=list)  # grille 24h/actif (S9)
    mouvements_rates: List["MouvementRate"] = field(default_factory=list)  # wins ratés (S9)
    sortie_timing: Optional["SortieTimingSemaine"] = None  # agrégat trop tôt/tard (vs 12h/18h)
    # {bulletin_date: {actif: realized_pct}} — mouvements 24h réels par JOUR D'ÉMISSION,
    # pour le post-mortem cross-asset déterministe (section 4, même levier que le quotidien).
    moves_by_jour: Dict[date, Dict[str, float]] = field(default_factory=dict)
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
        iso_week_bounds, OUTCOME_VRAI, OUTCOME_FAUSSE, OUTCOME_NC,
    )
    from bilan_jour import (  # noqa: PLC0415
        load_selection_map, SEUIL_MAX_GAIN_JOUR, gagnant_max_gain,
    )
    from datetime import timedelta  # noqa: PLC0415
    # Statuts non jugeables (marché fermé / non mesuré) : toujours exclus.
    _NON_JUGEABLE = {"marche-ferme", "non-notee", "suivi-interrompu"}

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
        outcome = r.get("outcome")
        mg = r.get("max_gain_pct")
        has_mg = isinstance(mg, (int, float))
        # Décision fondateur 24/06 : un pick GAGNE si son max gain du jour > 1 %.
        # Records récents (max_gain_pct présent) → jugés sur le max gain (le verdict
        # clôture NC inclus puisqu'on a désormais la donnée). Anciens records (pas de
        # max gain) → repli sur le verdict clôture VRAI/FAUSSE (NC exclu, zéro invention).
        if has_mg:
            if outcome in _NON_JUGEABLE:
                continue
        elif outcome not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
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
        if has_mg:
            if gagnant_max_gain(mg, SEUIL_MAX_GAIN_JOUR):
                res.n_vrai += 1
        elif outcome == OUTCOME_VRAI:
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
    fiche_key: Optional[str] = None      # clé fiche (pour calendrier + famille)
    score: Optional[float] = None        # score pondéré à l'émission (classement top 1)
    mono_critere: bool = False
    mono_critere_nom: Optional[str] = None
    coin_flip: bool = False
    quasi_neutre: bool = False
    raison_call: Optional[str] = None    # VRAIE raison : critère(s) dominant(s) du score (decision-log)
    cause_pro: Optional[str] = None      # news high COHÉRENTE avec notre call (contexte succès, section 3)
    cause_contra: Optional[str] = None   # news high À CONTRE-SENS de notre call (ce qui nous a battus)
    evenement_programme: Optional[str] = None  # nom de l'événement calendaire majeur (ou None)
    famille: Optional[str] = None        # famille granulaire de la fiche (ex. métaux-précieux)
    # Colonnes alignées sur le bilan QUOTIDIEN (mêmes sources, zéro nouveau calcul) :
    conviction_signee: Optional[float] = None  # note signée (score_pm1 sinon score_pond)
    perf_12h: Optional[float] = None     # % favorable 12h (load_perf_intraday_favorable)
    perf_18h: Optional[float] = None     # % favorable 18h (idem)
    max_gain_pct: Optional[float] = None  # max gain jour (champ measures-log de la cellule)

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


# Famille macro d'un actif (priorisation par classe). Dérivée du champ `famille`
# des fiches (granulaire) → 3 classes lisibles par Thomas. Source : v3/config/fiches.
_MACRO_FAMILLE = {
    "métaux-précieux": "Matières premières",
    "métaux-industriels": "Matières premières",
    "énergie": "Matières premières",
    "agri": "Matières premières",
    "agri-softs": "Matières premières",
    "fx": "Devises",
    "indices": "Indices actions",
    "volatilité": "Indices actions",
}


def _macro_famille_par_cle(fiches: Optional[Dict[str, dict]] = None) -> Dict[str, str]:
    """fiche_key -> famille macro (Matières premières / Devises / Indices actions).

    Lit le champ `famille` des fiches et le réduit aux 3 classes. fiche_key absente
    ou famille inconnue -> 'Autres' (zéro invention, dégradation propre)."""
    from journaliste import load_fiches  # noqa: PLC0415
    fiches = fiches if fiches is not None else load_fiches()
    out: Dict[str, str] = {}
    for cle, fiche in (fiches or {}).items():
        fam = str((fiche or {}).get("famille") or "").strip().lower()
        out[cle] = _MACRO_FAMILLE.get(fam, "Autres")
    return out


def _evenement_programme(
    fiche_key: Optional[str], d_debut: date, d_fin: date,
    calendrier_path: Optional[Path] = None,
) -> Optional[str]:
    """Nom d'un événement calendaire MAJEUR (impact high) touchant `fiche_key` dans
    [d_debut, d_fin], ou None. Source déterministe = calendrier-eco.yml (FOMC, BCE,
    OPEP, NFP…). Sert à dire « on a perdu un jour d'événement PRÉVISIBLE » (le pick
    aurait dû être moins certain ce jour-là). Best-effort, jamais bloquant."""
    if not fiche_key:
        return None
    try:
        from calendrier_eco import charger_evenements, _dates_pour_event  # noqa: PLC0415
        for ev in charger_evenements(calendrier_path):
            if str(ev.get("impact") or "medium").lower() != "high":
                continue
            if fiche_key not in (ev.get("actifs") or []):
                continue
            if _dates_pour_event(ev, d_debut, d_fin):
                return str(ev.get("nom") or ev.get("type") or "événement programmé")
    except Exception:  # noqa: BLE001 — calendrier best-effort
        return None
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
        load_selection_map, load_conviction_records, cause_news_high_dir,
        load_perf_intraday_favorable, SUIVI_TRACKING_DIR, SUIVI_SNAPSHOT_DIR,
        load_max_gain_bilan,
    )
    from datetime import timedelta  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    # Max gain du jour tel que CALCULÉ par le bilan QUOTIDIEN (sortie-timing-log) —
    # source partagée pour afficher LE MÊME Max dans le quotidien et l'hebdo (le
    # measures-log ne porte pas toujours le champ pour les échéances passées).
    st_max = load_max_gain_bilan()
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
        # On groupe par JOUR D'ÉMISSION (bulletin_date), pas par échéance : le call
        # du vendredi est tenu sur le week-end (échéance = lundi suivant, HORS semaine
        # ISO) alors que son résultat intraday vendredi est connu. Filtrer par échéance
        # faisait disparaître le vendredi des tableaux. Le verdict VRAI/FAUSSE et le
        # max gain restent lus depuis CE record measures (échéance lundi incluse).
        try:
            bdate = date.fromisoformat(str(r.get("bulletin_date")))
        except (TypeError, ValueError):
            bdate = ech - timedelta(days=1)
        if not (monday <= bdate <= sunday):
            continue
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
        # Deux causes DIRECTIONNELLES (cohérence garantie via le champ `impacts`) :
        #  - cause_pro    : news allant dans le sens de NOTRE call (pourquoi on l'a pris) ;
        #  - cause_contra : news à CONTRE-SENS (ce qui nous a battus, pour le post-mortem).
        # On n'affiche jamais un titre dont la direction contredit le contexte.
        cause_pro = cause_contra = None
        opp = "SHORT" if call == "LONG" else "LONG" if call == "SHORT" else None
        try:
            cause_pro = cause_news_high_dir(actif, bdate, str(call), None, events_path)
            if opp:
                cause_contra = cause_news_high_dir(actif, bdate, opp, None, events_path)
        except Exception:  # noqa: BLE001 — cause best-effort, jamais bloquante
            cause_pro = cause_contra = None
        fiche_key = r.get("fiche_key")
        # Événement programmé majeur entre la prise (bdate) et l'échéance (ech).
        evt = _evenement_programme(fiche_key, bdate, ech)
        # Colonnes alignées sur le bilan QUOTIDIEN — mêmes sources, zéro recalcul.
        # Conviction signée : score_pm1 prioritaire (déjà signé ±1), sinon score_pond.
        conv_signee = (rec.get("score_pm1") if isinstance(rec.get("score_pm1"), (int, float))
                       else rec.get("score_pond") if isinstance(rec.get("score_pond"), (int, float))
                       else None)
        # % 12h / % 18h favorables (jour d'émission = bdate, call du measures-log).
        try:
            perf_12h, perf_18h = load_perf_intraday_favorable(
                bdate, actif, str(call),
                tracking_dir=SUIVI_TRACKING_DIR, snapshot_dir=SUIVI_SNAPSHOT_DIR,
            )
        except Exception:  # noqa: BLE001 — best-effort, jamais bloquant
            perf_12h = perf_18h = None
        # Max gain jour : measures-log de la cellule, sinon le Max du bilan QUOTIDIEN
        # (sortie-timing-log, clé jour d'émission) → même valeur que le quotidien,
        # plus de « — » quand le quotidien l'a calculé. None seulement si vraiment rien.
        mg = r.get("max_gain_pct")
        if not isinstance(mg, (int, float)):
            mg = st_max.get((bdate.isoformat(), actif))
        max_gain = round(float(mg), 2) if isinstance(mg, (int, float)) else None
        picks.append(PickSemaine(
            actif=actif, call=str(call), outcome=str(r.get("outcome")),
            realized_pct=round(float(rp), 2) if isinstance(rp, (int, float)) else None,
            mouvement_dir=round(mv, 2) if mv is not None else None,
            bulletin_date=bdate,
            ratio_news=float(ratio) if isinstance(ratio, (int, float)) else None,
            fiche_key=str(fiche_key) if fiche_key else None,
            score=(rec.get("score_pond") if isinstance(rec.get("score_pond"), (int, float))
                   else rec.get("score_pm1") if isinstance(rec.get("score_pm1"), (int, float))
                   else None),
            mono_critere=bool(rec.get("mono_critere_dominant", False)),
            mono_critere_nom=rec.get("mono_critere_nom"),
            coin_flip=bool(rec.get("coin_flip", False)),
            quasi_neutre=bool(rec.get("quasi_neutre", False)),
            raison_call=_raison_reelle(rec, str(call)),
            cause_pro=cause_pro,
            cause_contra=cause_contra,
            evenement_programme=evt,
            conviction_signee=(float(conv_signee) if isinstance(conv_signee, (int, float)) else None),
            perf_12h=perf_12h,
            perf_18h=perf_18h,
            max_gain_pct=max_gain,
        ))
    picks.sort(key=lambda p: (p.bulletin_date, p.actif))
    return picks


def _moves_24h_par_jour(
    now: datetime,
    measures_log: Path = MEASURES_LOG,
) -> Dict[date, Dict[str, float]]:
    """{bulletin_date: {actif: realized_pct}} pour la semaine ISO, par JOUR D'ÉMISSION.

    Mouvements 24h BRUTS signés (delta réel de l'actif) de chaque jour. Sert au
    post-mortem cross-asset déterministe (`cause_cross_asset`) : pour un pari perdant,
    on regarde ce qu'ont fait les actifs corrélés CE jour-là. Zéro invention : un
    record sans realized_pct exploitable est ignoré."""
    from journaliste import iso_week_bounds  # noqa: PLC0415
    from datetime import timedelta  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    out: Dict[date, Dict[str, float]] = {}
    if not measures_log.exists():
        return out
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
        rp = r.get("realized_pct")
        if not isinstance(rp, (int, float)):
            continue
        try:
            ech = date.fromisoformat(str(r.get("echeance")))
        except (TypeError, ValueError):
            continue
        try:
            bdate = date.fromisoformat(str(r.get("bulletin_date")))
        except (TypeError, ValueError):
            bdate = ech - timedelta(days=1)
        if not (monday <= bdate <= sunday):
            continue
        out.setdefault(bdate, {})[str(r.get("actif"))] = round(float(rp), 2)
    return out


@dataclass
class MouvementRate:
    """Un gros mouvement 24h (> 1 %) DANS LE BON SENS qu'on a RATÉ (pas dans le
    top 3 du jour) — opportunité manquée à comprendre pour s'améliorer."""
    actif: str
    jour: date            # jour d'échéance (où le mouvement s'est joué)
    call: str             # direction qui aurait gagné (notre call non sélectionné)
    perf_dir: float       # % de gain dans le sens du call (> 1)
    variation_brute: float  # variation BRUTE signée de l'actif (monte +, baisse −)
    raison: str           # pourquoi pas dans le top 3 (déduit du decision-log)


def mouvements_rates_semaine(
    now: datetime,
    measures_log: Path = MEASURES_LOG,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> List[MouvementRate]:
    """Actifs ayant fait > 1 % sur 24h DANS LE SENS de notre call, JUGÉS VRAI, mais
    PAS retenus dans le top 3 du jour : des wins qu'on a ratés. La raison du
    non-choix est déduite du decision-log (signal classé faible = exclusion
    légitime ; sinon bon call sous-classé = vraie opportunité ratée). Zéro
    invention : prix/échéance manquants ignorés."""
    from journaliste import iso_week_bounds, OUTCOME_VRAI  # noqa: PLC0415
    from bilan_jour import load_selection_map, load_conviction_records  # noqa: PLC0415
    from datetime import timedelta  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    if not measures_log.exists():
        return []
    records: Dict[Tuple[str, str], dict] = {}
    for line in measures_log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(r, dict) and r.get("horizon") == "24h":
            records[(str(r.get("actif")), str(r.get("echeance")))] = r

    sel_cache: Dict[date, Dict[Tuple[str, str], bool]] = {}
    conv_cache: Dict[date, Dict[Tuple[str, str], dict]] = {}
    out: List[MouvementRate] = []
    for r in records.values():
        if r.get("outcome") != OUTCOME_VRAI:
            continue
        call = r.get("conclusion")
        rp = r.get("realized_pct")
        if call not in ("LONG", "SHORT") or not isinstance(rp, (int, float)):
            continue
        perf_dir = (1.0 if call == "LONG" else -1.0) * float(rp)
        if perf_dir <= _SEUIL_BIEN_FAIT_PCT:  # pas un gros mouvement
            continue
        try:
            ech = date.fromisoformat(str(r.get("echeance")))
        except (TypeError, ValueError):
            continue
        # Groupé par jour d'émission (bulletin_date), cohérent avec _enrich_picks_semaine :
        # un mouvement raté du vendredi (échéance lundi suivant) doit rester dans la semaine.
        try:
            bdate = date.fromisoformat(str(r.get("bulletin_date")))
        except (TypeError, ValueError):
            bdate = ech - timedelta(days=1)
        if not (monday <= bdate <= sunday):
            continue
        actif = str(r.get("actif"))
        if bdate not in sel_cache:
            sel_cache[bdate] = load_selection_map(bdate, decision_log_dir)
        if sel_cache[bdate].get((actif, "24h"), False):
            continue  # était dans le top 3 → pas raté
        if bdate not in conv_cache:
            conv_cache[bdate] = load_conviction_records(bdate, decision_log_dir)
        rec = conv_cache[bdate].get((actif, "24h")) or {}
        if rec.get("coin_flip"):
            raison = "écarté du top 3 car signal coin-flip (exclusion légitime) ; il a gagné quand même"
        elif rec.get("mono_critere_dominant"):
            nom = rec.get("mono_critere_nom")
            raison = (f"écarté car signal mono-critère ({nom})" if nom
                      else "écarté car signal mono-critère") + " ; il a gagné quand même"
        elif rec.get("quasi_neutre"):
            raison = "écarté car signal quasi-neutre ; il a gagné quand même"
        else:
            raison = "bon call NON classé dans le top 3 ce jour-là (conviction/score inférieurs) : opportunité ratée"
        out.append(MouvementRate(actif=actif, jour=ech, call=str(call),
                                 perf_dir=round(perf_dir, 2),
                                 variation_brute=round(float(rp), 2), raison=raison))
    out.sort(key=lambda m: (-m.perf_dir, m.jour, m.actif))
    return out


@dataclass
class SortieTimingSemaine:
    """Agrégat hebdo des verdicts de SORTIE de la Sélection 24h (trop tôt / trop tard /
    bien tenu), reconstitué depuis le journal écrit par les bilans du jour."""
    n_bien_tenu: int = 0
    n_trop_tard: int = 0
    n_trop_tot: int = 0
    cas: List[str] = field(default_factory=list)  # libellés des cas notables (trop tard/tôt)

    @property
    def n_juge(self) -> int:
        return self.n_bien_tenu + self.n_trop_tard + self.n_trop_tot


def sortie_timing_semaine(now: datetime, path: Optional[Path] = None) -> Optional[SortieTimingSemaine]:
    """Agrège les verdicts de sortie de la semaine ISO depuis sortie-timing-log.jsonl
    (écrit par les bilans du jour). None si rien de jugé. Zéro invention."""
    from journaliste import iso_week_bounds  # noqa: PLC0415
    from bilan_jour import SORTIE_TIMING_LOG  # noqa: PLC0415
    path = path or SORTIE_TIMING_LOG
    if not path.exists():
        return None
    monday, sunday = iso_week_bounds(now)
    agg = SortieTimingSemaine()
    JJ = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            d = date.fromisoformat(str(r.get("date")))
        except (TypeError, ValueError):
            continue
        if not (monday <= d <= sunday):
            continue
        cat = r.get("categorie")
        if cat == "bien_tenu":
            agg.n_bien_tenu += 1
        elif cat == "trop_tard":
            agg.n_trop_tard += 1
            agg.cas.append(
                f"{r.get('actif')} ({JJ[d.weekday()]}) clôturé trop tard : pic "
                f"{_fmt_signed_pct(r.get('pic_pct'))} à {r.get('pic_heure')}, "
                f"rendu à {_fmt_signed_pct(r.get('cloture_pct'))}"
            )
        elif cat == "trop_tot":
            agg.n_trop_tot += 1
            agg.cas.append(
                f"{r.get('actif')} ({JJ[d.weekday()]}) : le suivi disait « Vendre » "
                "mais l'actif a monté jusqu'à la clôture (sortie aurait été trop tôt)"
            )
    if agg.n_juge == 0:
        return None
    return agg


@dataclass
class EdgeFamille:
    """Win rate cumulé des top 3 d'une famille d'actifs (où concentrer les paris)."""
    famille: str
    n_vrai: int = 0
    n_total: int = 0       # paris conclusifs (VRAI + FAUSSE)

    @property
    def win_rate(self) -> Optional[float]:
        return round(self.n_vrai / self.n_total * 100.0, 1) if self.n_total else None


def edge_par_famille(
    measures_log: Path = MEASURES_LOG,
    decision_log_dir: Path = DECISION_LOG_DIR,
    fiches: Optional[Dict[str, dict]] = None,
) -> List[EdgeFamille]:
    """Win rate CUMULÉ de nos top 3 (Sélection 24h) par famille macro, sur TOUT
    l'historique persisté (pas seulement la semaine). C'est la carte « où est notre
    edge » : prioriser les familles qui gagnent, se méfier de celles qui perdent.
    Zéro invention : seules les sélections conclusives comptent. Dédup (actif, échéance)."""
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415
    from bilan_jour import load_selection_map  # noqa: PLC0415

    macro = _macro_famille_par_cle(fiches)
    if not measures_log.exists():
        return []
    records: Dict[Tuple[str, str], dict] = {}
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
        if r.get("outcome") not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        records[(str(r.get("actif")), str(r.get("echeance")))] = r  # dédup, dernier

    sel_cache: Dict[date, Dict[Tuple[str, str], bool]] = {}
    par_famille: Dict[str, EdgeFamille] = {}
    for r in records.values():
        try:
            bdate = date.fromisoformat(str(r.get("bulletin_date")))
        except (TypeError, ValueError):
            continue
        actif = str(r.get("actif"))
        if bdate not in sel_cache:
            sel_cache[bdate] = load_selection_map(bdate, decision_log_dir)
        if not sel_cache[bdate].get((actif, "24h"), False):
            continue  # seulement les top 3 (certitudes)
        fam = macro.get(str(r.get("fiche_key")), "Autres")
        ef = par_famille.setdefault(fam, EdgeFamille(famille=fam))
        ef.n_total += 1
        if r.get("outcome") == OUTCOME_VRAI:
            ef.n_vrai += 1
    # Tri : win rate décroissant (les familles à edge en tête), N en départage.
    return sorted(
        par_famille.values(),
        key=lambda e: (e.win_rate if e.win_rate is not None else -1.0, e.n_total),
        reverse=True,
    )


@dataclass
class Detail24hActif:
    """Détail des calls 24h de la semaine pour UN actif (grille jour par jour)."""
    actif: str
    # weekday -> (direction, outcome, variation) ; variation = % de mouvement BRUT
    # de l'actif (monte → +, baisse → −), None si prix manquant. Le verdict
    # (outcome) dit si le call était dans le bon sens.
    par_jour: Dict[int, Tuple[str, str, Optional[float]]] = field(default_factory=dict)
    n_vrai: int = 0
    n_concl: int = 0  # VRAI + FAUSSE

    @property
    def bilan(self) -> str:
        return f"{self.n_vrai}/{self.n_concl}" if self.n_concl else "—"


def detail_24h_par_actif(
    now: datetime,
    measures_log: Path = MEASURES_LOG,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> List[Detail24hActif]:
    """Détail des calls 24h de la semaine, par actif, jour par jour (équivalent
    pour le 24h du tableau des tendances 7j). Un call est rangé sur le jour de son
    ÉCHÉANCE (le jour où il s'est joué). Tous les actifs jugés, pas seulement le
    top 3. Dédup (actif, échéance). Zéro invention : jour sans call = absent."""
    from journaliste import iso_week_bounds, OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415

    monday, sunday = iso_week_bounds(now)
    if not measures_log.exists():
        return []
    records: Dict[Tuple[str, str], dict] = {}
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
        records[(str(r.get("actif")), str(r.get("echeance")))] = r  # dédup, dernier

    par_actif: Dict[str, Detail24hActif] = {}
    for r in records.values():
        try:
            ech = date.fromisoformat(str(r.get("echeance")))
        except (TypeError, ValueError):
            continue
        if not (monday <= ech <= sunday) or ech.weekday() > 4:  # Lun-Ven seulement
            continue
        outcome = str(r.get("outcome") or "")
        direction = str(r.get("conclusion") or "")
        if direction not in ("LONG", "SHORT"):
            continue
        # Variation BRUTE de l'actif (monte → +, baisse → −), pas le sens du call.
        rp = r.get("realized_pct")
        variation = round(float(rp), 2) if isinstance(rp, (int, float)) else None
        d = par_actif.setdefault(str(r.get("actif")), Detail24hActif(actif=str(r.get("actif"))))
        d.par_jour[ech.weekday()] = (direction, outcome, variation)
        if outcome == OUTCOME_VRAI:
            d.n_vrai += 1
            d.n_concl += 1
        elif outcome == OUTCOME_FAUSSE:
            d.n_concl += 1
    return sorted(par_actif.values(), key=lambda d: d.actif)


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
    # Famille granulaire par pick (sert au learning « biais LONG métaux », S-MÉTAUX).
    _fam_par_cle = {
        cle: str((f or {}).get("famille") or "").strip().lower()
        for cle, f in (fiches or {}).items()
    }
    for _p in picks:
        if _p.fiche_key and _p.fiche_key in _fam_par_cle:
            _p.famille = _fam_par_cle[_p.fiche_key] or None
    edge_fam = edge_par_famille(fiches=fiches)
    detail24 = detail_24h_par_actif(now)
    rates = mouvements_rates_semaine(now)
    timing = sortie_timing_semaine(now)  # agrégat trop tôt/tard (journal des bilans du jour)
    moves_by_jour = _moves_24h_par_jour(now)  # cross-asset post-mortem (section 4)

    bilan = BilanSemaine(
        iso=iso, lundi=monday, dimanche=sunday, now=now, cellules=cellules,
        n_forte=conv.n_forte, taux_forte=conv.taux_forte,
        n_faible_conv=conv.n_faible, taux_faible_conv=conv.taux_faible,
        selection=sel, tendances=tend, picks=picks, edge_familles=edge_fam,
        detail_24h=detail24, mouvements_rates=rates, sortie_timing=timing,
        moves_by_jour=moves_by_jour,
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


def _top1_picks(picks: List["PickSemaine"]) -> List["PickSemaine"]:
    """Le meilleur pari de CHAQUE jour (1 par bulletin_date) = score |max|.
    Départage : ampleur favorable puis actif (déterministe). 1 par jour de bourse."""
    par_jour: Dict[date, "PickSemaine"] = {}
    def _key(p):
        return (abs(p.score) if isinstance(p.score, (int, float)) else -1.0,
                p.mouvement_dir if p.mouvement_dir is not None else -999.0)
    for p in picks:
        cur = par_jour.get(p.bulletin_date)
        if cur is None or _key(p) > _key(cur):
            par_jour[p.bulletin_date] = p
    return list(par_jour.values())


def _agg_picks(picks: List["PickSemaine"]) -> Tuple[int, int, Optional[float]]:
    """(n_vrai, n_conclusifs, ampleur_moy_dir) sur un ensemble de picks."""
    concl = [p for p in picks if p.outcome in ("VRAI", "FAUSSE")]
    nv = sum(1 for p in concl if p.vrai)
    amps = [p.mouvement_dir for p in concl if p.mouvement_dir is not None]
    amp = round(sum(amps) / len(amps), 2) if amps else None
    return nv, len(concl), amp


def _fmt_conviction(v: Optional[float]) -> str:
    """Conviction signée façon bilan quotidien (« +1.25 »). « — » si absente."""
    return f"{v:+.2f}" if isinstance(v, (int, float)) else "—"


def _fmt_pct_quotidien(v: Optional[float]) -> str:
    """% signé façon bilan quotidien (« +1.25% »). « — » si absent (placeholder cellule)."""
    return f"{v:+.2f}%" if isinstance(v, (int, float)) else "—"


def _render_picks_par_jour(picks: List["PickSemaine"], L: List[str]) -> None:
    """Table des picks triée PAR JOUR (pas par actif). Colonnes alignées sur le bilan
    QUOTIDIEN : jour, actif, call, conviction signée, % 12h, % 18h, max gain jour,
    variation brute (sens marché), verdict, raison. Au sein d'un jour, du meilleur
    score au moins bon."""
    JJ = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")
    rows = sorted(
        picks,
        key=lambda p: (p.bulletin_date,
                       -(abs(p.score) if isinstance(p.score, (int, float)) else -1.0),
                       p.actif),
    )
    # [Relecture 27/06] Raison SORTIE du tableau (comme le bilan quotidien) : avec
    # Conviction/12h/18h/Max ajoutées, garder la longue liste de drivers en colonne
    # rendait chaque ligne géante. Tableau compact ici, « pourquoi » en sous-liste.
    L.append("| Jour | Actif | Call | Conviction | % 12h | % 18h | Max | Variation actif | Résultat |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in rows:
        jour = f"{JJ[p.bulletin_date.weekday()]} {p.bulletin_date.day}"
        glyph = "✅" if p.vrai else ("❌" if p.outcome in ("FAUSSE", "FAUX") else "⚪")
        # Variation BRUTE de l'actif (monte → +, baisse → −), pas le sens du call.
        # Le ✅/❌ dit si notre call (LONG/SHORT) était dans le bon sens.
        L.append(
            f"| {jour} | {p.actif} | {p.call} | {_fmt_conviction(p.conviction_signee)} | "
            f"{_fmt_pct_quotidien(p.perf_12h)} | {_fmt_pct_quotidien(p.perf_18h)} | "
            f"{_fmt_pct_quotidien(p.max_gain_pct)} | {_fmt_signed_pct(p.realized_pct)} | "
            f"{glyph} |"
        )
    L.append("")
    # « Pourquoi » en sous-liste (drivers du signal 7h), tableau gardé étroit.
    avec_raison = [p for p in rows if _raison_pick(p) and _raison_pick(p) != "—"]
    if avec_raison:
        L.append("**Pourquoi ces paris (signal 7h) :**")
        L.append("")
        for p in avec_raison:
            jour = f"{JJ[p.bulletin_date.weekday()]} {p.bulletin_date.day}"
            L.append(f"- **{p.actif}** ({jour}, {p.call}) : {_raison_pick(p)}")
        L.append("")


def _drivers_reels(rec: dict, call: str) -> List[str]:
    """Délègue à la SOURCE UNIQUE `journaliste.drivers_du_call` (alignement jour /
    semaine / suivi) : tous les critères qui ont matériellement poussé le score dans
    le sens du call, déterministe, jamais une news lambda."""
    from journaliste import drivers_du_call  # noqa: PLC0415
    return drivers_du_call(rec, call)


def _raison_reelle(rec: dict, call: str) -> Optional[str]:
    """VRAIE raison du call : tous les drivers matériels joints par « + ». None si
    aucun critère tracé (zéro invention)."""
    drivers = _drivers_reels(rec, call)
    return " + ".join(drivers) if drivers else None


def _drivers_segment(
    actif: str, direction: str, jour: date,
    conv_cache: Dict[date, Dict[Tuple[str, str], dict]],
) -> Optional[str]:
    """VRAIS drivers d'une orientation 7j (decision-log du jour `jour`, horizon 7j),
    joints par « + ». None si non tracé. Partagé par la section 2 (bascules) et la
    section 3 (réussites) pour un POURQUOI cohérent partout."""
    from bilan_jour import load_conviction_records  # noqa: PLC0415
    if jour not in conv_cache:
        try:
            conv_cache[jour] = load_conviction_records(jour)
        except Exception:  # noqa: BLE001 — best-effort
            conv_cache[jour] = {}
    rec = conv_cache[jour].get((actif, "7j")) or {}
    return _raison_reelle(rec, direction)


def _raison_pick(p: "PickSemaine") -> str:
    """Raison (le moteur RÉEL) d'un pick pour le tableau Top 1/Top 3 : le critère
    dominant du score à l'émission (ce qui a VRAIMENT déclenché le call), à défaut le
    type de signal (orienté news / quant-pur / signal faible). Zéro invention,
    jamais une news lambda."""
    if p.raison_call:
        return p.raison_call
    if p.news_driven:
        return f"orienté news ({_ratio_pct(p)})"
    if p.drapeau_faible:
        return f"signal faible ({p.drapeau_faible})"
    return "quant-pur"


def _render_agg_picks(picks: List["PickSemaine"], L: List[str]) -> None:
    nv, nt, amp = _agg_picks(picks)
    wr = _fmt_pct(round(nv / nt * 100.0, 1)) if nt else "—"
    # WR significatif : VRAI dont le mouvement FAVORABLE atteint >= 0,5 % (gain
    # exploitable ; un call juste mais quasi-plat ne compte pas). Même dénominateur.
    concl = [p for p in picks if p.outcome in ("VRAI", "FAUSSE")]
    nv_sig = sum(1 for p in concl
                 if p.vrai and isinstance(p.mouvement_dir, (int, float))
                 and p.mouvement_dir >= _PERF_MATERIELLE_PCT)
    wr_sig = _fmt_pct(round(nv_sig / nt * 100.0, 1)) if nt else "—"
    L.append(
        f"Win rate : **{wr}** ({nv}/{nt} jugés) · WR ≥ 0,5 % : **{wr_sig}** "
        f"({nv_sig}/{nt}) · ampleur moyenne : **{_fmt_signed_pct(amp)}**."
    )
    L.append("")


def _render_section1_selection(bilan: BilanSemaine, L: List[str]) -> None:
    """SECTION 1 — Performance des 24h sélectionnés (la semaine), par jour."""
    L.append("## 1. Performance des 24h sélectionnés (la semaine)")
    L.append("")
    L.append(
        "> Nos paris 24h de la semaine, triés PAR JOUR. **Top 1** = le meilleur pari de "
        "chaque jour (1 par jour de bourse, ~5/semaine) ; **Top 3** = les trois retenus. "
        "**Variation actif** = mouvement RÉEL de l'actif sur 24h (monte → +, baisse → −) ; "
        "le ✅/❌ dit si notre call (LONG/SHORT) était dans le bon sens. Win rate = % de "
        "calls justes · ampleur = % moyen favorable (jamais d'euros)."
    )
    L.append("")
    picks = bilan.picks
    if not picks:
        L.append(
            "Aucune sélection 24h jugée cette semaine (pas de top du jour conclusif "
            "sur les jours de bourse écoulés)."
        )
        L.append("")
    else:
        L.append("### Top 1 du jour (le meilleur pari, 1 par jour)")
        L.append("")
        top1 = _top1_picks(picks)
        _render_agg_picks(top1, L)
        _render_picks_par_jour(top1, L)
        L.append("### Top 3 du jour")
        L.append("")
        _render_agg_picks(picks, L)
        _render_picks_par_jour(picks, L)
    _render_sortie_timing_semaine(bilan, L)


def _render_sortie_timing_semaine(bilan: BilanSemaine, L: List[str]) -> None:
    """Sortie de la semaine : a-t-on clôturé trop tôt / trop tard ? (agrégat des
    bilans du jour, vs les points 12h/18h). Rien si aucun verdict tracé."""
    t = bilan.sortie_timing
    if t is None or t.n_juge == 0:
        return
    L.append("### Sortie : a-t-on clôturé au bon moment ? (vs 12h / 18h)")
    L.append("")
    L.append(
        f"Sur {t.n_juge} position(s) jugée(s) cette semaine : **{t.n_bien_tenu} bien "
        f"tenue(s)** · **{t.n_trop_tard} clôturée(s) trop tard** (gain rendu après le "
        f"pic) · **{t.n_trop_tot} trop tôt** (sortie aurait coupé un gain qui montait "
        "encore)."
    )
    if t.cas:
        L.append("")
        for c in t.cas[:6]:
            L.append(f"- {c}.")
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
        "prix de la phase. **Raison** = le(s) critère(s) qui ont VRAIMENT déclenché "
        "l'orientation (drivers dominants du score à l'émission, decision-log), pas "
        "une news lambda ; « — » si non tracé. ✅ gagnant · ❌ perdant · ⚪ négligeable."
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
    conv_cache: Dict[date, Dict[Tuple[str, str], dict]] = {}
    L.append("| Actif | Tendance | Période | Perf (sens tendance) | Résultat | Raison |")
    L.append("|---|---|---|---|---|---|")
    for t in tendances:
        for i, s in enumerate(t.segments):
            # Actif affiché une seule fois par groupe (lecture en colonnes).
            actif_cell = f"**{t.actif}**" if i == 0 else ""
            tendance_cell = s.direction + (" (en cours)" if s.en_cours else "")
            periode = _fmt_jours_segment(s.jours)
            perf = _fmt_signed_pct(s.perf_pct)
            verdict = _verdict_segment(s.perf_pct)
            raison = _raison_orientation(t.actif, s, flip=(i > 0), conv_cache=conv_cache)
            L.append(f"| {actif_cell} | {tendance_cell} | {periode} | {perf} | {verdict} | {raison} |")
    L.append("")


def _raison_orientation(
    actif: str, s: "SegmentTendance", flip: bool,
    conv_cache: Optional[Dict[date, Dict[Tuple[str, str], dict]]] = None,
) -> str:
    """VRAIE raison d'une orientation 7j (ou de son changement) : le(s) critère(s)
    dominant(s) du score à l'émission, dans le sens du segment (decision-log du 1er
    jour de la phase = jour de bascule pour un flip). On les liste TOUS. « — » si pas
    de critères tracés (zéro invention ; jamais une news lambda)."""
    if not s.jours:
        return "—"
    if conv_cache is None:
        conv_cache = {}
    raison = _drivers_segment(actif, s.direction, s.jours[0], conv_cache)
    if not raison:
        return "—"
    return (f"bascule {s.direction} : {raison}" if flip else raison)


# GARDE-FOU HONNÊTETÉ (brief S9) — libellé ALIGNÉ sur le Bilan du jour
# (bilan_jour._MSG_MESURE_INDISPO). Une semaine sans AUCUNE cellule notée ne doit
# JAMAIS afficher « Rien à améliorer / RAS » (qui se lit « semaine parfaite ») :
# elle affiche « mesure indisponible ». Même esprit, libellé adapté à la semaine.
_MSG_MESURE_INDISPO_SEMAINE = (
    "Mesure indisponible cette semaine (donnée absente) : à ne pas lire comme RAS."
)


def _mesure_indisponible_semaine(bilan: BilanSemaine) -> bool:
    """True si la semaine ne repose sur AUCUNE mesure exploitable.

    Garde-fou d'honnêteté symétrique de `bilan_jour._mesure_indisponible` : si
    aucune cellule 24h n'a été jugée VRAI/FAUSSE cette semaine (detail_24h vide,
    aucun pick), aucune phase de tendance 7j lisible, et aucune conviction mesurée,
    alors les sections « bien fait / à améliorer / learnings » ne doivent pas
    afficher un message rassurant trompeur. Zéro invention : on ne déduit l'absence
    QUE de l'absence réelle de données agrégées."""
    a_mesure_24h = bool(bilan.detail_24h) or bool(bilan.picks)
    a_tendance = any(t.segments for t in bilan.tendances)
    a_conviction = (bilan.n_forte + bilan.n_faible_conv) > 0
    a_selection = bilan.selection is not None and bilan.selection.n_select > 0
    # KPI cumulés : au moins une cellule avec des paris effectivement mesurés
    # (n_eff > 0) prouve qu'il y a de la donnée à lire (même hors semaine ISO).
    a_kpi = any((c.n_eff or 0) > 0 for c in bilan.cellules)
    return not (a_mesure_24h or a_tendance or a_conviction or a_selection or a_kpi)


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
    # Garde-fou honnêteté : 0 mesure sur la semaine → message explicite (pas RAS).
    indispo = _mesure_indisponible_semaine(bilan)

    L.append("## 3. Ce qu'on a bien fait cette semaine")
    L.append("")
    points_forts = _points_forts(bilan)
    if indispo:
        L.append(_MSG_MESURE_INDISPO_SEMAINE)
    elif points_forts:
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
    if indispo:
        L.append(_MSG_MESURE_INDISPO_SEMAINE)
    elif points_faibles:
        for p in points_faibles:
            L.append(f"- {p}")
    else:
        L.append(
            "Aucun point faible confirmé cette semaine (aucune cellule sous le seuil "
            "de détection ni tendance perdante marquée)."
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
    if indispo:
        L.append(_MSG_MESURE_INDISPO_SEMAINE)
    elif learnings:
        for ln in learnings:
            L.append(f"- {ln}")
    else:
        L.append(
            "Pas de learning net cette semaine : échantillon insuffisant (warm-up). "
            "On continue de mesurer avant d'agir."
        )
    L.append("")

    # ===================================================================
    # SECTION 6 — Ajustements proposés (APRÈS les learnings : ce sont les
    # changements de RÈGLE qui en découlent, à valider par Thomas). Distincts des
    # learnings : un learning ORIENTE la semaine ; une proposition ne se déclenche
    # que lorsqu'une cellule franchit le seuil STATISTIQUE (N indépendant suffisant
    # sous le seuil de confiance). D'où « aucune proposition » possible malgré des
    # learnings — c'est normal, on n'altère le moteur qu'avec une preuve chiffrée.
    # ===================================================================
    L.append("## 6. Ajustements proposés (à valider Thomas)")
    L.append("")
    if bilan.propositions:
        L.append(
            "> Changements de règle déclenchés par une preuve statistique (≠ learnings, "
            "qui orientent sans encore changer le moteur). À valider avant application."
        )
        L.append("")
        for p in bilan.propositions:
            L.append(f"### Proposition P{p['n']} · {p['titre']}")
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
            "Aucun changement de RÈGLE proposé cette semaine — et c'est cohérent avec les "
            "learnings ci-dessus : ceux-ci ORIENTENT (ils se confirment sur plusieurs "
            "semaines avant de devenir une règle), mais une proposition formelle n'est "
            "déclenchée que lorsqu'une cellule franchit le seuil statistique (assez de "
            "paris indépendants ET borne de confiance sous le seuil). Tant qu'aucune ne "
            "l'a franchi, on applique les learnings à la main et on continue de mesurer "
            "avant de toucher au moteur."
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
        "> Info de CONTRÔLE (traçabilité), pas des décisions. Le détail win rate par "
        "cellule (24h/7j/1m) vit sur la page **Performance**. Rappel warm-up : le 7j "
        f"n'est significatif que vers {WARMUP_DATES['7j']}, le 1m pas avant 6 mois — "
        "le Manager se concentre sur le 24h."
    )
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

    # --- Cellules : ce qui marche / ce qui décroche (fusion porteuses + surveiller
    #     + observations en un seul tableau) ---
    L.append("### Cellules : ce qui marche / ce qui décroche")
    L.append("")
    porteuses = sorted(
        [c for c in bilan.cellules if c.porteuse],
        key=lambda c: (c.win_rate if c.win_rate is not None else 0.0), reverse=True,
    )
    surveiller = sorted(
        [c for c in bilan.cellules if c.candidate_faible],
        key=lambda c: (c.win_rate if c.win_rate is not None else 100.0),
    )
    if porteuses or surveiller:
        L.append("| Actif | Horizon | État | Win rate | WR tradable | N_eff | Repère |")
        L.append("|---|---|---|---|---|---|---|")
        for c in porteuses:
            L.append(
                f"| {c.actif} | {c.horizon} | ✅ porteuse | {_fmt_pct(c.win_rate)} | "
                f"{_fmt_pct(c.wr_tradable)} | {c.n_eff} | "
                f"≥ {WINRATE_PORTEUSE:.0f}% sur N_eff ≥ {N_EFF_PORTEUSE} |"
            )
        for c in surveiller:
            etat = ("⚠️ faible confirmée (≥ 2 sem.)" if c.faible_confirmee
                    else "⚠️ candidate (1ʳᵉ sem.)")
            L.append(
                f"| {c.actif} | {c.horizon} | {etat} | {_fmt_pct(c.win_rate)} | "
                f"{_fmt_pct(c.wr_tradable)} | {c.n_eff} | borne basse {_fmt_pct(c.wilson_low)} |"
            )
    else:
        L.append(
            f"Aucune cellule notable : ni porteuse (≥ {WINRATE_PORTEUSE:.0f}% sur "
            f"N_eff ≥ {N_EFF_PORTEUSE}), ni sous le seuil de détection (N_eff ≥ 10 ET "
            "borne basse < 50 %). Tout est encore en chauffe."
        )
    L.append("")
    # Pré-watchlist : cellules en zone d'observation (pas encore de proposition).
    if bilan.observations:
        L.append("_En observation (pas encore de proposition, on attend confirmation) :_")
        L.append("")
        for o in bilan.observations:
            L.append(f"- {o}")
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
            # Échec de tendance : on ajoute le POURQUOI cross-asset/externe (même
            # cascade que les paris perdants) sur le dernier jour de la phase ratée.
            if p <= 0 and s.jours:
                pourquoi = _pourquoi_cascade(t.actif, s.jours[-1], bilan, call=s.direction)
                if pourquoi and "divergence quant" not in pourquoi:
                    libelle += f" — {pourquoi}"
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


# Seuil « bien fait » / « gros mouvement » : variation directionnelle de plus de
# 1 % (définition fondateur S9). En dessous = bruit, ni succès ni opportunité.
_SEUIL_BIEN_FAIT_PCT = 1.0


def _news_actif_jour(actif: str, jour: date, sens: Optional[str] = None) -> Optional[str]:
    """News high tracée sur `actif` à la date `jour` (ou None). Best-effort.

    Si `sens` (LONG/SHORT) est fourni, ne renvoie qu'une news COHÉRENTE avec ce sens
    (via le champ `impacts`) — sinon la news la plus fraîche, sans filtre de direction.
    """
    try:
        if sens in ("LONG", "SHORT"):
            from bilan_jour import cause_news_high_dir  # noqa: PLC0415
            return cause_news_high_dir(actif, jour, sens, None, None)
        from bilan_jour import cause_news_high_apres  # noqa: PLC0415
        return cause_news_high_apres(actif, jour, None, None)
    except Exception:  # noqa: BLE001
        return None


def _points_forts(bilan: BilanSemaine) -> List[str]:
    """SECTION 3 — ce qu'on a bien fait, et POURQUOI (symétrique de la section 4).

    Un succès = mouvement de PLUS DE 1 % capté DANS LE BON SENS. Pour CHAQUE réussite
    on dit le POURQUOI réel : « Pris sur : {drivers du score} » (ce qui a vraiment
    déclenché le bon call, decision-log) + « Catalyseur confirmant : {news cohérente} »
    si une news high allait dans notre sens. Vrai pour les top 3 (24h) ET les
    tendances (7j). Zéro invention (driver/news absent → on n'écrit rien de faux)."""
    pts: List[str] = []

    # Top 3 (24h) : gain directionnel > 1 % (donc dans le bon sens, et matériel).
    for p in bilan.picks:
        if p.mouvement_dir is None or p.mouvement_dir <= _SEUIL_BIEN_FAIT_PCT:
            continue
        ligne = (f"{p.actif} {p.call} (24h) : {_fmt_signed_pct(p.mouvement_dir)} dans le "
                 f"bon sens. Pris sur : {_raison_pick(p)}")
        if p.cause_pro:  # news high allant dans notre sens = catalyseur qui a confirmé
            ligne += f". Catalyseur confirmant : {p.cause_pro}"
        pts.append(ligne + ".")

    # Tendances (7j) : phase de plus de 1 % dans le sens de la tendance.
    conv_cache: Dict[date, Dict[Tuple[str, str], dict]] = {}
    for t in bilan.tendances:
        for s in t.segments:
            if s.perf_pct is None or s.perf_pct <= _SEUIL_BIEN_FAIT_PCT:
                continue
            ligne = (f"Tendance {t.actif} {s.direction} ({_fmt_jours_segment(s.jours)}) : "
                     f"{_fmt_signed_pct(s.perf_pct)} dans le bon sens")
            pourquoi = _drivers_segment(t.actif, s.direction, s.jours[0], conv_cache) if s.jours else None
            if pourquoi:
                ligne += f". Pris sur : {pourquoi}"
            news = _news_actif_jour(t.actif, s.jours[-1], s.direction) if s.jours else None
            if news:
                ligne += f". Catalyseur confirmant : {news}"
            pts.append(ligne + ".")

    if not pts:
        pts.append(
            "Rien de net cette semaine : aucun mouvement de plus de 1 % capté dans le "
            "bon sens (ni sur les top 3, ni sur les tendances)."
        )
    return pts[:8]


def _pourquoi_cascade(
    actif: str, bulletin_date: date, bilan: "BilanSemaine",
    cause_contra: Optional[str] = None, call: Optional[str] = None,
) -> str:
    """POURQUOI réel d'un échec, MÊME cascade que le bilan quotidien (zéro invention) :
    a. news propre à contre-sens (déjà passée en argument via cause_contra) ;
    b. cross-asset déterministe (`cause_cross_asset` sur les moves 24h du jour) ;
    c. piste externe best-effort (`cause_externe_news`, None hors réseau — OK) ;
    d. sinon divergence quant ↔ marché (le marché n'a pas suivi notre signal).
    Renvoie une phrase prête à concaténer (jamais « cause non identifiée » à tort)."""
    if cause_contra:
        return f"{cause_contra} a dominé à contre-sens"
    from bilan_jour import cause_cross_asset, cause_externe_news  # noqa: PLC0415
    moves = (getattr(bilan, "moves_by_jour", None) or {}).get(bulletin_date) or {}
    try:
        cross = cause_cross_asset(actif, moves)
    except Exception:  # noqa: BLE001 — best-effort
        cross = None
    if cross:
        return cross  # ex. « porté par le complexe métaux précieux (Or +2.10%)… »
    # c. DRIVER MINORITAIRE (déterministe, NOS données) : un facteur de notre propre
    #    analyse qui pointait À L'INVERSE de notre call (sous-pondéré) et que le marché
    #    a suivi. Ex. Pétrole SHORT raté → « Tension géopolitique au Moyen-Orient »
    #    (haussier) qu'on avait sous-pesé. C'est un vrai pourquoi, pas une divergence.
    try:
        from bilan_jour import load_conviction_records, cause_minority_driver  # noqa: PLC0415
        rec = (load_conviction_records(bulletin_date) or {}).get((actif, "24h")) or {}
        # Le call vient du pick/segment (le decision-log ne porte pas "conclusion") ;
        # fallback sur le champ rec si jamais fourni. Helper PARTAGÉ avec le quotidien.
        _call = (call or str(rec.get("conclusion") or "")).upper()
        mino = cause_minority_driver(rec, _call)
        if mino:
            return f"le marché a suivi un facteur qu'on avait sous-pondéré : {mino}"
    except Exception:  # noqa: BLE001 — best-effort, decision-log absent → on continue
        pass
    # d. piste externe best-effort (None hors réseau / sans feedparser — OK).
    try:
        ext = cause_externe_news(actif, bulletin_date)
    except Exception:  # noqa: BLE001 — best-effort, None hors réseau
        ext = None
    if ext:
        return f"piste externe à vérifier : {ext}"
    return "divergence quant ↔ marché (le marché n'a pas suivi notre signal)"


def _points_faibles(bilan: BilanSemaine) -> List[str]:
    """SECTION 4 — ce qu'on doit améliorer et POURQUOI (post-mortem causal, spec S9).

    Pick perdant par pick : news ratée (CAS A), signal faible suivi à tort (CAS B),
    ou call quant solide raté (CAS C). Puis tendances perdantes, alarme sélection,
    cellules faibles (reformulées sans jargon Wilson).
    """
    pts: List[str] = []

    # Règle 4.0 — PRIORISATION PAR FAMILLE (où concentrer / se méfier). C'est le
    # levier n°1 vers 70 % : faire plus confiance là où on a un edge prouvé.
    prio = _priorite_familles(bilan)
    if prio:
        pts.append(prio)

    perdants_pick = [p for p in bilan.picks if not p.vrai]

    # Règle 4.1 — picks perdants, cause par pick. La variation BRUTE de l'actif
    # (monte +, baisse −) est affichée pour chiffrer l'ampleur de l'échec.
    for p in perdants_pick:
        drap = p.drapeau_faible
        tete = f"{p.actif} {p.call} ({_fmt_signed_pct(p.realized_pct)})"
        if p.news_driven and p.cause_contra:  # CAS A : news ratée
            pts.append(
                f"{tete} raté : call orienté news (part news {_ratio_pct(p)}). "
                f"{p.cause_contra} a dominé le marché à CONTRE-SENS de notre position. Ce "
                "catalyseur n'était pas (ou mal) pris dans notre synthèse."
            )
        elif p.news_driven:  # CAS A bis : news-driven mais aucun catalyseur tracé
            pts.append(
                f"{tete} raté : call orienté news (part news {_ratio_pct(p)}) "
                "mais aucun catalyseur tracé dans l'events-log. Mouvement adverse inexpliqué."
            )
        elif drap:  # CAS B : signal faible suivi à tort
            pts.append(
                f"{tete} raté : pari pris sur un signal classé FAIBLE "
                f"(drapeau {drap}). Ce type de signal ne devrait pas entrer dans la Sélection."
            )
        elif p.cause_contra:  # CAS C : quant solide raté, mais une news adverse existait
            pts.append(
                f"{tete} raté : signal quant solide (aucun drapeau), mais "
                f"{p.cause_contra} l'a contre-pied. News possiblement sous-pondérée au scoring."
            )
        else:  # CAS C bis : quant solide raté → MÊME cascade de POURQUOI que le quotidien
            pourquoi = _pourquoi_cascade(p.actif, p.bulletin_date, bilan, call=p.call)
            pts.append(
                f"{tete} raté : signal quant solide (aucun drapeau). Pourquoi : "
                f"{pourquoi}. À revoir si le pattern se répète."
            )
        # Alerte événement PROGRAMMÉ (News Trader) : si une grosse échéance connue
        # au calendrier tombait ce jour-là, le pari n'aurait pas dû passer en top 3
        # avec une certitude pleine. C'est une faute évitable (≠ choc imprévisible).
        if p.evenement_programme and pts:
            pts[-1] = pts[-1].rstrip(".") + (
                f". Or un événement PRÉVISIBLE était au calendrier ce jour-là "
                f"({p.evenement_programme}) : on aurait dû baisser la certitude sur cet "
                "actif, voire l'écarter du top 3."
            )

    # Règle 4.2 — ÉCHECS DE TENDANCE 7j (volet b).
    _, perdants_seg = _segments_signes(bilan)
    if perdants_seg:
        pts.append("Échecs de tendance 7j : " + " ; ".join(perdants_seg[:3]) + ".")

    # Règle 4.4 — GROS MOUVEMENTS RATÉS (volet c) : actif > 1 % sur 24h dans le bon
    # sens, jugé VRAI, mais PAS dans le top 3 du jour. À comprendre pour s'améliorer.
    rates = bilan.mouvements_rates
    if rates:
        JJ = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")
        bouts = [
            f"{m.actif} {m.call} {_fmt_signed_pct(m.variation_brute)} ({JJ[m.jour.weekday()]}) · {m.raison}"
            for m in rates[:5]
        ]
        pts.append(
            "Opportunités ratées (mouvement 24h de plus de 1 % dans le bon sens, hors "
            "top 3) : " + " ; ".join(bouts) + "."
        )

    # Règle 4.5 — cellules faibles confirmées (sans jargon Wilson).
    confirmees = [c for c in bilan.cellules if c.faible_confirmee]
    if confirmees:
        noms = ", ".join(f"{c.actif} {c.horizon} ({_fmt_pct(c.win_rate)})" for c in confirmees)
        pts.append(
            f"Cellules faibles sur 2 semaines : {noms}. Pas un coup de malchance passager, "
            "une faiblesse structurelle : une proposition d'ajustement est ci-dessous."
        )
    return pts[:9]


def _priorite_familles(bilan: BilanSemaine) -> Optional[str]:
    """Reco de priorisation par famille (Règle 4.0). Ferme quand N >= 10 dans une
    famille ; sinon lecture douce « à confirmer » s'il y a un écart net sur N >= 3 ;
    rien si tout est trop maigre (zéro sur-interprétation)."""
    edges = [e for e in bilan.edge_familles if e.n_total > 0]
    if not edges:
        return None
    forts = [e for e in edges if e.n_total >= 10 and e.win_rate is not None and e.win_rate >= 60.0]
    fragiles = [e for e in edges if e.n_total >= 10 and e.win_rate is not None and e.win_rate < 45.0]
    if forts or fragiles:
        bouts = []
        if forts:
            bouts.append("concentrer les top 3 sur : " + ", ".join(
                f"{e.famille} ({_fmt_pct(e.win_rate)})" for e in forts))
        if fragiles:
            bouts.append("se méfier de : " + ", ".join(
                f"{e.famille} ({_fmt_pct(e.win_rate)})" for e in fragiles))
        return "Priorisation par famille (edge confirmé sur ≥ 10 paris) · " + " ; ".join(bouts) + "."
    # Lecture douce : un écart net entre la meilleure et la pire famille (N >= 3).
    notables = [e for e in edges if e.n_total >= 3 and e.win_rate is not None]
    if len(notables) >= 2:
        meilleure, pire = notables[0], notables[-1]
        if meilleure.win_rate - pire.win_rate >= 20.0:
            return (
                f"Tendance d'edge par famille (à CONFIRMER, N encore faible) : on gagne "
                f"surtout sur {meilleure.famille} ({_fmt_pct(meilleure.win_rate)}), on peine "
                f"sur {pire.famille} ({_fmt_pct(pire.win_rate)}). À surveiller avant de "
                "rééquilibrer la priorité des top 3."
            )
    return None


def _learnings_semaine(bilan: BilanSemaine) -> List[str]:
    """SECTION 5 — learnings actionnables ([observation chiffrée] + [action à J+7]).

    Max 3. Priorité : drapeaux (5.1) > news vs quant (5.2) > conviction (5.4) >
    prudence sélection (5.5) > fallback (5.6).
    """
    out: List[str] = []
    picks = bilan.picks

    # === SYNTHÈSE (en tête) : ce qu'on doit retenir des sections 1 à 4. ===
    # NB : on NE classe PLUS les actifs en « gagnants / perdants » sur une semaine
    # (1-2 paris par actif = bruit, pas un edge — verdict unanime des 3 experts).
    # Le win rate appartient au PROCESS, pas à l'actif. On raisonne donc par rang,
    # par type de signal et par contexte, jamais par actif sur N hebdo.

    # S-CADRE (Analyst) — le garde-fou OUVRE la section : il pose le cadre avant
    # toute observation. Aucun chiffre hebdo n'est significatif seul ; un learning
    # ORIENTE, il ne devient une règle de fond qu'après ~50 paris cumulés.
    out.append(
        "Cadre de lecture : avec ~8 paris/semaine, AUCUN chiffre ci-dessous n'est "
        "significatif seul (un win rate hebdo de 30 à 80 % reste compatible avec "
        "50 % réel). Ces learnings ORIENTENT la semaine ; on ne bascule une piste en "
        "règle de fond qu'après ~50 paris cumulés (≈ 10 semaines) — chaque piste "
        "ci-dessous précise son déclencheur chiffré."
    )

    # S-RANG — le meilleur pari du jour (Top 1) gagne-t-il nettement plus que le
    # Top 3 ? Si oui, c'est LE levier vers 70 % : concentrer sur le Top 1.
    top1 = _top1_picks(picks)
    nv1, nt1, _ = _agg_picks(top1)
    nv3, nt3, _ = _agg_picks(picks)
    if nt1 >= 2 and nt3 > nt1:
        wr1, wr3 = nv1 / nt1 * 100.0, nv3 / nt3 * 100.0
        if wr1 - wr3 >= 15.0:
            out.append(
                f"Le meilleur pari du jour (Top 1) gagne {wr1:.0f}% ({nv1}/{nt1}) contre "
                f"{wr3:.0f}% ({nv3}/{nt3}) pour le Top 3 : le 2e/3e choix tire le win rate "
                "vers le bas. Action testable dès maintenant : concentrer sur le Top 1 "
                "(privilégier 1 pari principal/jour plutôt que 3). Échantillon minuscule "
                f"(N={nt1}) — DÉCLENCHEUR pour passer en Top-1-only durable : l'écart tient "
                "sur ≥ 20 paris cumulés (≈ 3-4 semaines)."
            )

    # S-B — opportunités ratées (gros mouvements hors top 3). On normalise (Analyst) :
    # le ratio bons-calls-sous-classés / total est plus parlant que le comptage brut.
    rates = bilan.mouvements_rates
    sous_classes = [m for m in rates if "opportunité ratée" in m.raison]
    if rates:
        if sous_classes:
            part = len(sous_classes) / len(rates) * 100.0
            détail = f", dont {len(sous_classes)}/{len(rates)} ({part:.0f}%) bons calls sous-classés"
        else:
            détail = ""
        out.append(
            f"On a raté {len(rates)} mouvement(s) de plus de 1 % hors top 3{détail} : "
            "revoir le classement — mais ne remonter que les signaux SOLIDES "
            "(multi-critère ou portés par une news), jamais les mono-critère / "
            "coin-flip, qui restent exclus à raison même quand ils gagnent."
        )

    # S-MÉTAUX (News Trader) — biais directionnel HAUSSIER sur les métaux qui a coûté.
    # Un repricing Fed est un RÉGIME (dollar/taux en tendance sur plusieurs jours),
    # pas un événement ponctuel : la règle FOMC ne le couvre pas. Observation ancrée
    # (vrais LONG métaux perdus) + directive de vérification macro (zéro invention).
    METAUX = {"métaux-précieux", "métaux-industriels"}
    long_met_perdus = [
        p for p in picks
        if not p.vrai and p.call == "LONG" and (p.famille or "").lower() in METAUX
    ]
    if len(long_met_perdus) >= 2:
        noms = ", ".join(f"{p.actif} ({_fmt_signed_pct(p.realized_pct)})" for p in long_met_perdus)
        out.append(
            f"Biais LONG métaux qui a coûté : {len(long_met_perdus)} paris LONG sur les "
            f"métaux perdus cette semaine ({noms}). En régime de hausse du dollar et des "
            "taux (repricing Fed), ne PAS acheter le contre-pied haussier des métaux : "
            "vérifier la tendance dollar/taux 5-10 jours avant tout LONG métal — en régime "
            "hawkish, la macro domine le signal quant. DÉCLENCHEUR : si le pattern se "
            "répète, ajouter un filtre « vent macro contraire » au scoring."
        )

    # S-NOTRADE — règle de précaution « jour blanc » (Spéculateur + Analyst). Couvre
    # les jours de verdict programmé ET les Top 1 sans signal solide. Précaution
    # ASSUMÉE : pas de déclencheur chiffré ici (contrairement aux autres pistes) car
    # éviter un risque connu à l'avance ne coûte rien — confirmation non requise.
    evt_perdus = [p for p in picks if not p.vrai and p.evenement_programme]
    top1_faibles = [p for p in top1 if p.drapeau_faible and not p.news_driven]
    if evt_perdus or top1_faibles:
        if evt_perdus:
            preuve = (f" Cette semaine : {len(evt_perdus)} pari(s) perdu(s) un jour "
                      f"d'événement programmé (ex. {evt_perdus[0].evenement_programme}) — "
                      "le cas type à passer en flat.")
        else:
            preuve = (f" Cette semaine : le meilleur pari du jour reposait sur un signal "
                      f"faible ({top1_faibles[0].actif}) — à ne pas jouer.")
        out.append(
            "Règle de NO-TRADE (jour blanc), à appliquer SANS attendre de confirmation "
            "(éviter un risque connu ne coûte rien) : aucun pari directionnel un jour de "
            "verdict programmé (FOMC, BCE, OPEP, NFP, CPI…), NI quand le meilleur pari du "
            "jour (Top 1) n'est porté par aucun signal solide (mono-critère ou coin-flip "
            "seul). On sort l'actif, on ne le joue pas dégradé." + preuve
        )

    # (L'ancienne Règle 5.1 « drapeaux de signal faible » est supprimée : la règle
    # NO-TRADE ci-dessus + le filtre « signaux solides » de S-B la couvrent déjà.)

    # Règle 5.2 — news-driven vs quant-pur sur les picks de la semaine.
    nd = [p for p in picks if p.news_driven]
    qp = [p for p in picks if p.ratio_news is not None and not p.news_driven]
    if len(nd) >= 2 or len(qp) >= 2:
        def _wr(lst):
            return (sum(1 for p in lst if p.vrai) / len(lst) * 100.0) if lst else None
        wn, wq = _wr(nd), _wr(qp)
        # Flag N<3 inline (Analyst) : un 100 % sur 2 paris n'est pas interprétable.
        def _seg(label: str, wr: float, n: int) -> str:
            return f"{label} {wr:.0f}% ({n}{', non interprétable' if n < 3 else ''})"
        morceaux = []
        if wn is not None:
            morceaux.append(_seg("news-driven", wn, len(nd)))
        if wq is not None:
            morceaux.append(_seg("quant-pur", wq, len(qp)))
        verdict = ""
        # Signal poison repéré par le Spéculateur : un call quant-pur sans news ni
        # multi-critère qui plafonne ≈ pile-ou-face. On le pointe même à N faible.
        if wq is not None and wq <= 40.0 and len(qp) >= 2:
            verdict = (" Le quant-pur se comporte comme un pile-ou-face : candidat à "
                       "écarter du top 3 s'il n'est ni porté par une news ni multi-critère. "
                       "DÉCLENCHEUR : s'il reste ≤ 40 % sur ≥ 20 paris cumulés, l'exclure "
                       "du top 3 en dur.")
        elif wn is not None and wq is not None and (len(nd) < 3 or len(qp) < 3):
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

    # Règle 5.6 — fallback : aucune piste au-delà du cadre de lecture (out[0]).
    if len(out) == 1:
        out.append(
            "Pas de piste nette cette semaine : trop peu de paris par catégorie (warm-up) "
            "pour conclure de façon fiable. On continue de mesurer."
        )

    # Cadre de lecture (S-CADRE) en tête + au plus 4 pistes derrière.
    return out[:5]


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
