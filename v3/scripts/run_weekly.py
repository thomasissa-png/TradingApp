"""TradingApp v3 — Bilan de la semaine dimanche 18h (R5) + le Manager.

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

Le déclenchement dimanche 18h (guard weekday()==6 + bypass is_trading_day) est
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
        wl = _fmt_pct(c.wilson_low)
        props.append({
            "n": i,
            "titre": f"{c.actif} {c.horizon} — cellule faible 2 semaines",
            "type": "Note d'observation — ajustement à instruire (Thomas tranche le levier)",
            "actifs": c.actif,
            "criteres": "à déterminer depuis le decision-log (critère dominant de la cellule)",
            "constat": (
                f"Win rate {wr} sur {c.n_eff} paris indépendants, "
                f"Wilson_low {wl} < {WILSON_FAIBLE:.0f}%, observé sur "
                f">= {SEMAINES_CONSECUTIVES} semaines consécutives."
            ),
            "proposition": (
                f"Revoir la pondération des critères de {c.actif} {c.horizon} "
                f"(réduire le poids du critère qui tire dans le mauvais sens, "
                f"identifié au decision-log). Modification de config à valider "
                f"avant application."
            ),
            "risque": (
                "Sur-réaction à un régime de marché conjoncturel. N_eff reste "
                "modeste — un ajustement de poids peut dégrader une autre période."
            ),
            "validation": "Thomas OUI/NON avant toute modification de config YAML",
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

    bilan = BilanSemaine(
        iso=iso, lundi=monday, dimanche=sunday, now=now, cellules=cellules,
        n_forte=conv.n_forte, taux_forte=conv.taux_forte,
        n_faible_conv=conv.n_faible, taux_faible_conv=conv.taux_faible,
    )

    propositions = [p for p in build_propositions(cellules) if proposition_valide(p)]
    bilan.propositions = propositions

    # Observations sans proposition : candidates faibles non encore confirmées
    # (1ère semaine) + cellules en zone d'observation N_eff 5-9.
    for c in cellules:
        if c.candidate_faible and not c.faible_confirmee:
            bilan.observations.append(
                f"{c.actif} {c.horizon} : candidate faible cette semaine "
                f"(win rate {_fmt_pct(c.win_rate)}, N_eff {c.n_eff}, "
                f"Wilson_low {_fmt_pct(c.wilson_low)}) — 1ère semaine, "
                f"PAS de proposition (attendre confirmation S+1)."
            )
        elif (
            N_EFF_OBSERVE <= c.n_eff < N_EFF_PROPOSE
            and c.wilson_low is not None
            and c.wilson_low < WILSON_FAIBLE
        ):
            bilan.observations.append(
                f"{c.actif} {c.horizon} : sous surveillance (N_eff {c.n_eff} "
                f"entre {N_EFF_OBSERVE}-{N_EFF_PROPOSE - 1}) — observation, "
                f"PAS de proposition (mesurer avant d'agir)."
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


def render_bilan_semaine(bilan: BilanSemaine) -> str:
    L: List[str] = []
    # [I-7 audit visuel 12/06] : H1 pour tous les rapports (harmonisation des
    # niveaux de titre — le bilan semaine était en H2). Le range lundi→dimanche
    # reste présent (lu par build_html.weekHumanTitle pour le titre humain).
    L.append(f"# Bilan semaine — {bilan.iso} ({bilan.lundi.isoformat()} → {bilan.dimanche.isoformat()})")
    L.append("")
    L.append(f"- Généré : {horodatage_fr(bilan.now)} (dimanche 18h Paris)")
    L.append("- WIN RATE ONLY — aucune mesure monétaire. Le Manager PROPOSE, Thomas VALIDE.")
    L.append(
        "- WR tradable = VRAI / (VRAI + FAUSSE + non-conclusif) — inclut les jours "
        "sous seuil où une position aurait quand même été prise (toujours ≤ Win rate)."
    )
    L.append("")

    # --- Win rate de la semaine (archive hebdo prise telle quelle, CA-W2) ---
    L.append("### Win rate de la semaine")
    L.append("")
    archive = _read_weekly_archive(bilan.iso)
    if archive:
        L.append(f"> Source : `win-rate-{bilan.iso}.md` (archive hebdo, prise telle quelle).")
        L.append("")
        # On insère le corps de l'archive (sans son titre H1).
        body = "\n".join(
            ln for ln in archive.splitlines() if not ln.startswith("# ")
        ).strip()
        L.append(body)
    else:
        L.append(f"> Archive `win-rate-{bilan.iso}.md` absente — produite au prochain run Journaliste.")
    L.append("")

    # --- Win rate par conviction (§4.7 / CA-W6) ---
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

    # --- Cellules porteuses (ce qui marche, §4.6) ---
    L.append("### Cellules porteuses (ce qui marche)")
    L.append("")
    porteuses = sorted(
        [c for c in bilan.cellules if c.porteuse],
        key=lambda c: (c.win_rate if c.win_rate is not None else 0.0),
        reverse=True,
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
        L.append(f"Aucune cellule avec N_eff ≥ {N_EFF_PORTEUSE} et win rate ≥ {WINRATE_PORTEUSE:.0f}% — observer.")
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

    # --- Propositions d'ajustement (à valider Thomas) ---
    L.append("### Propositions d'ajustement (à valider Thomas)")
    L.append("")
    if bilan.propositions:
        for p in bilan.propositions:
            L.append(f"#### Proposition P{p['n']} — {p['titre']}")
            L.append("")
            L.append(f"**Type** : {p['type']}")
            L.append(f"**Actif(s) concerné(s)** : {p['actifs']}")
            L.append(f"**Critère(s) concerné(s)** : {p['criteres']}")
            L.append(f"**Constat** : {p['constat']}")
            L.append(f"**Proposition** : {p['proposition']}")
            L.append(f"**Risque** : {p['risque']}")
            L.append(f"**Validation requise** : {p['validation']}")
            L.append("")
            L.append("- [ ] Thomas valide — appliquer au prochain run")
            L.append("- [ ] Thomas refuse — garder en observation")
            L.append("- [ ] Thomas demande plus de données — reporter à S+1")
            L.append("")
    else:
        L.append(
            "Aucune proposition cette semaine : aucune cellule faible confirmée "
            f"sur ≥ {SEMAINES_CONSECUTIVES} semaines consécutives "
            f"(N_eff ≥ {N_EFF_PROPOSE} ET Wilson_low < {WILSON_FAIBLE:.0f}%). "
            "Le Manager n'invente pas d'ajustement sur petit N (mesurer avant d'agir)."
        )
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

    # --- Dates de sortie de warm-up (§6.2) ---
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

    # --- Justesse des news vs quant (informatif, mesure-only) ---
    # Vue LÉGÈRE : win-rate news-driven vs quant-pures PAR HORIZON, même garde-fou
    # N<15 → « en chauffe ». Lecture seule de measures-log (+ fallback decision-log
    # pour les mesures pré-instrumentation). N'influence AUCUNE proposition Manager.
    L.append("### Justesse des news vs quant (informatif)")
    L.append("")
    L.append(
        "> Mesure SÉPARÉE de la justesse des calls *dominés par les news* "
        "(`ratio_news` > 50 % à l'émission) vs les calls *quant-purs*, par horizon. "
        "Informatif uniquement — n'alimente aucune proposition. Garde-fou : "
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

    return "\n".join(L)


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

    Le déclenchement dimanche 18h (guard weekday()==6, bypass is_trading_day) est
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
