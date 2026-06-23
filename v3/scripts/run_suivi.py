"""TradingApp v3 — Suivi intra-journée 12h / 18h (R2/R3, Phase 2 refonte 5 rapports).

Source de vérité : `v3/docs/reco/spec-refonte-5-rapports.md` §3.2 (R2 12h),
§3.3 (R3 18h) + §7 (CA-S1..CA-S6b).

Rapport COURT (Thomas lit en 2 min). Pour chaque position du Briefing 7h du jour :
- Statut vs SON ouverture de marché : `(prix du moment − ouverture) / ouverture` %,
  ✅ gagne (sens du call) / ⚠️ perd (contre le call) / — neutre (sous bande).
- Dynamique de tendance (§3.2/§3.3) : Δ vs le suivi précédent + flag
  ↑ s'accélère / ↓ s'essouffle / ⇄ se retourne (le vrai signal de sortie).
- Suggestion de sortie : drapeau `Sortie à envisager` si |Delta%| ≥ SEUIL_PCT_actif
  CONTRE le call. DRAPEAU-SUGGESTION, JAMAIS UN ORDRE.
- Marchés US à 12h : pas encore ouverts (ouverture 15h30 Paris) → affichés
  explicitement « pas encore ouvert » (CA-S, correction M-H). 1er statut US au 18h.
- Contexte news du Briefing 7h (NON réactualisé : pas de ré-ingestion, court).

Garde-fous (non négociables) :
- WIN RATE ONLY — aucune valeur monétaire (€/$/gain/perte). Le % de mouvement est OK.
- Le suivi N'ÉCRIT JAMAIS dans `measures-log.jsonl` ni `performance.md` (CA-S6/CA-S6b).
  Pas de scoring complet, pas de re-scoring DeepSeek (léger : prix + news, Q9).
- Zéro invention : prix/ouverture absent → `—`, jamais une valeur fabriquée.
- DST : heures via ZoneInfo(Europe/Paris), JAMAIS d'offset codé en dur (réutilise
  le mapping de groupe de `mesure_ouverture`).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("run_suivi")

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

ROOT = SCRIPTS_DIR.parent
SUIVI_DIR = ROOT / "data" / "suivi"
# Refonte bilan soir S9 — persistance intraday DÉDIÉE des relevés 12h/18h de la
# Sélection du jour (call + % favorable signé + heure), pour que le Bilan du soir
# reconstruise le PIC sur {12h, 18h, clôture}. Cache de présentation, jamais une
# mesure (n'alimente NI measures-log NI performance). v3/data/ jamais commité ici.
SUIVI_TRACKING_DIR = ROOT / "data" / "suivi-tracking"
EVENTS_LOG_DIR = ROOT / "data" / "events-log"
# Note US (cash-hours only) : Twelve Data GROW ne sert AUCUNE donnée US fiable
# hors séance cash (sonde 23/06 : futures ES/NQ vides ou figés, CFD US500/USTEC
# vides, SPY/QQQ prepost vides). Les indices US (S&P/Nasdaq/VIX) ne sont donc
# suivis qu'à partir de leur ouverture cash (15h30 Paris) ; avant, statut honnête
# « cash fermé (ouvre 15h30) ». Pas de piste futures (abandon VPS/yfinance).

PARIS_TZ = ZoneInfo("Europe/Paris")

# Report types reconnus (heure Paris du créneau).
REPORT_12H = "12h"
REPORT_18H = "18h"
VALID_REPORTS = (REPORT_12H, REPORT_18H)

# Longueur max du rapport (CA-S5 : un suivi reste court, pas un bulletin).
# Refonte suivi S9 : + tableau « Sélection du jour » en tête (≤ 3 lignes) + sa
# note + titre du suivi détaillé → marge relevée (reste court : pas un bulletin).
MAX_MARKDOWN_LINES = 62

# Nombre max de news affichées dans le bloc « news à impact » (suivi = court).
MAX_NEWS = 3

# Nombre max de news FRAÎCHES (bloc « Actus du jour ») — suivi reste court.
MAX_NEWS_FRAICHES = 3

# Heure de référence (Paris) du rapport précédent par créneau : 12h récolte depuis
# 07h du jour (Briefing matin), 18h récolte depuis 12h du jour (suivi midi).
SEUIL_HEURE_PRECEDENTE = {REPORT_12H: 7, REPORT_18H: 12}


# ---------------------------------------------------------------------------
# Modèle d'une ligne de suivi
# ---------------------------------------------------------------------------

@dataclass
class SuiviLigne:
    actif: str
    call: str                      # "LONG" / "SHORT"
    ouverture: Optional[float]
    prix_courant: Optional[float]
    delta_pct: Optional[float]     # (courant - ouverture) / ouverture * 100
    statut: str                    # "✅ gagne" / "⚠️ perd" / "— neutre" / "🕐 cash fermé (ouvre 15h30)"
    tendance: str                  # "—" / "↑ s'accélère" / "↓ s'essouffle" / "⇄ se retourne" / "↗ confirmé US" / "↘ infirmé US"
    delta_vs_prec: Optional[float] # points de % vs le suivi précédent (18h), None au 12h
    suggestion: str                # "Hold" / "Surveiller" / "Sortie à envisager" / "—"
    seuil_pct: Optional[float]
    us_pas_ouvert: bool = False
    # Refonte suivi S9 — tableau de progression « Sélection du jour ».
    vendre: str = "Pas vendre"     # reco binaire (compute_vendre) : "Vendre" / "Pas vendre"
    selection: bool = False        # True si cellule `selection_du_jour: true` du jour
    fav_now: Optional[float] = None  # % directionnel signé favorable, créneau courant
    fav_prec: Optional[float] = None  # % directionnel signé favorable, créneau précédent (None au 12h)
    raison_call: Optional[str] = None  # VRAIE raison du call (drivers du score 7h) — aligné jour/semaine
    # Cohérence avec le Bilan du jour (brief S9) — excursions intraday MAX depuis
    # l'ouverture, calculées par mesure_bilan._excursions_intraday sur la série 1h
    # (MÊME primitive que le bilan, zéro duplication). « meilleur point » (favorable
    # max ≥ 0) et « pire point » (adverse max ≤ 0). None si non calculable (zéro invention).
    max_favorable_pct: Optional[float] = None
    max_adverse_pct: Optional[float] = None


@dataclass
class SuiviRapport:
    date_j: date
    now: datetime
    report_type: str               # "12h" / "18h"
    lignes: List[SuiviLigne] = field(default_factory=list)
    news: List[str] = field(default_factory=list)
    # PARTIE B — actus FRAÎCHES du jour (récolte RSS légère depuis le créneau
    # précédent). `news_fraiches` = lignes markdown prêtes ; `news_fraiches_indispo`
    # = True si le fetch RSS a échoué (dégradation propre, distinct du cas « vide »).
    news_fraiches: List[str] = field(default_factory=list)
    news_fraiches_indispo: bool = False
    contexte_frais: str = ""
    # Section « News majeures depuis {heure_préc} » : events de l'events-log à
    # FORTE matérialité (high) ingérés depuis le rapport précédent (lecture seule,
    # zéro DeepSeek). Lignes markdown prêtes ; [] → « Aucune news majeure ».
    news_majeures: List[str] = field(default_factory=list)
    # FIX 2a (fondateur 23/06) — titre RÉEL de la news dominante PAR PARI (clé =
    # actif sélectionné). Source : events-log (news_reelle_paris). Remplace le
    # libellé opaque « Synthèse news (net, IA) ». Actif absent → « — » au rendu.
    news_paris: Dict[str, str] = field(default_factory=dict)
    # GARDE-FOU HONNÊTETÉ (brief S9) — distingue deux cas que l'ancien code
    # confondait en un tableau vide silencieux :
    #  - briefing_introuvable=True : AUCUN Briefing 7h actif pour date_j (archivé /
    #    jamais émis) → le suivi des positions est IMPOSSIBLE (on l'affiche).
    #  - briefing_introuvable=False ET lignes=[] : briefing trouvé mais 0 position
    #    LONG/SHORT actionnable (message DIFFÉRENT).
    briefing_introuvable: bool = False
    markdown: str = ""


# ---------------------------------------------------------------------------
# Helpers de formatage
# ---------------------------------------------------------------------------

def _fmt_pct(v: Optional[float], signed: bool = True) -> str:
    if not isinstance(v, (int, float)):
        return "—"
    return f"{v:+.2f}%" if signed else f"{v:.2f}%"


def _fmt_points(v: Optional[float]) -> str:
    # [P-S2 audit visuel 12/06] : « pts » seul était ambigu (points d'index ?
    # de %?). Le delta vs suivi précédent est une variation de POINTS DE
    # POURCENTAGE → on suffixe « %pts » pour lever l'ambiguïté.
    if not isinstance(v, (int, float)):
        return "—"
    return f"{v:+.2f}%pts"


def _fmt_price(v: Optional[float]) -> str:
    return f"{v:.4g}" if isinstance(v, (int, float)) else "—"


# ---------------------------------------------------------------------------
# Logique de statut / tendance / suggestion (pures, testables)
# ---------------------------------------------------------------------------

def call_sign(call: str) -> Optional[int]:
    """Signe attendu du mouvement pour un call. LONG → +1, SHORT → -1, sinon None."""
    c = (call or "").strip().upper()
    if c == "LONG":
        return 1
    if c == "SHORT":
        return -1
    return None


def compute_statut(
    delta_pct: Optional[float], call: str, neutral_band_pct: float
) -> str:
    """Statut d'une position vs son ouverture (CA-S4).

    `✅ gagne` si signe(delta) == sens(call), `⚠️ perd` sinon,
    `— neutre` si |delta| (en proportion) < neutral_band_pct.
    `neutral_band_pct` est une PROPORTION (0.001 = 0,1%) ; delta_pct est en %
    → on compare |delta_pct| / 100 à la bande.
    """
    sign = call_sign(call)
    if delta_pct is None or sign is None:
        return "—"
    if abs(delta_pct) / 100.0 < neutral_band_pct:
        return "— neutre"
    return "✅ gagne" if (delta_pct > 0) == (sign > 0) else "⚠️ perd"


def compute_tendance(
    delta_now: Optional[float],
    delta_prec: Optional[float],
    is_us: bool,
    neutral_band_pct: float,
) -> str:
    """Flag de dynamique de tendance (§3.2/§3.3).

    - Au 12h (premier suivi), `delta_prec` est None → `—` (pas de précédent).
    - Au 18h, compare delta 18h vs delta 12h :
        ↑ s'accélère  : |delta_now| > |delta_prec| ET même signe (renforce la thèse)
        ↓ s'essouffle : |delta_now| < |delta_prec| ET même signe (ralentit)
        ⇄ se retourne : signe(delta_now) ≠ signe(delta_prec) (retournement)
    - `— neutre` si |delta_now| sous la bande.
    NB : les flags US spécifiques (↗ confirmé / ↘ infirmé) sont posés au niveau
    de la ligne (ils dépendent du sens du call, pas seulement du delta).
    """
    if delta_now is None:
        return "—"
    if abs(delta_now) / 100.0 < neutral_band_pct:
        return "— neutre"
    if delta_prec is None:
        return "—"
    s_now = 1 if delta_now > 0 else -1
    s_prec = 1 if delta_prec > 0 else (-1 if delta_prec < 0 else 0)
    if s_prec == 0:
        # Précédent neutre/nul → on ne qualifie pas l'accélération.
        return "—"
    if s_now != s_prec:
        return "⇄ se retourne"
    if abs(delta_now) > abs(delta_prec):
        return "↑ s'accélère"
    if abs(delta_now) < abs(delta_prec):
        return "↓ s'essouffle"
    return "—"


def compute_suggestion(
    delta_pct: Optional[float],
    call: str,
    seuil_pct: Optional[float],
    statut: str,
) -> str:
    """Suggestion de sortie (drapeau, JAMAIS un ordre — CA-S4).

    Règle UNIQUE : `Sortie à envisager` si |Delta%| ≥ SEUIL_PCT_actif ET la
    position perd (signe(delta) ≠ sens(call)). Sinon `Surveiller` si elle perd
    sous le seuil, `Hold` si elle gagne ou neutre. `—` si données absentes.
    Aucun calcul monétaire : seuil en %, pas en €.
    """
    if delta_pct is None or call_sign(call) is None:
        return "—"
    if statut.startswith("✅") or statut.startswith("— neutre"):
        return "Hold"
    # statut == ⚠️ perd
    if (
        isinstance(seuil_pct, (int, float))
        and abs(delta_pct) >= seuil_pct
    ):
        return "Sortie à envisager"
    return "Surveiller"


def vendre_from_suggestion(suggestion: str) -> str:
    """Reco binaire « Vendre » / « Pas vendre » DÉRIVÉE de la suggestion de sortie.

    Source de vérité UNIQUE (FIX 1, fondateur 23/06) : la colonne « Vendre ? » de
    la table « Sélection du jour » et le bloc « Suggestions de sortie » partagent
    EXACTEMENT le même verdict, pour ne jamais se contredire (l'un « vendre »,
    l'autre « tenir »). « Vendre » ssi le seuil de sortie est franchi CONTRE le
    call (suggestion == « Sortie à envisager »). Sinon « Pas vendre ».
    """
    return "Vendre" if suggestion == "Sortie à envisager" else "Pas vendre"


def fav_delta(delta_pct: Optional[float], call: str) -> Optional[float]:
    """Mouvement directionnel signé FAVORABLE : `+delta` si LONG, `−delta` si SHORT.

    fav>0 = la position va dans le sens du call (gagne) ; fav<0 = contre nous.
    None si delta absent ou call non LONG/SHORT (zéro invention).
    """
    sign = call_sign(call)
    if delta_pct is None or sign is None:
        return None
    return delta_pct * sign


def compute_vendre(
    delta_now: Optional[float],
    delta_prec: Optional[float],
    call: str,
    neutral_band_pct: float,
) -> str:
    """Reco binaire « Vendre » / « Pas vendre », orientée MAXIMISATION DU GAIN.

    Source de vérité : demande fondateur (refonte suivi S9). Logique pure et
    testable — aucune valeur monétaire, aucun ordre : un drapeau d'aide.

    Soit `fav = +delta si LONG, −delta si SHORT` (fav>0 = va dans notre sens).
    `fav_now`, `fav_prec` (None au 12h, faute de suivi précédent).
    - |delta_now| sous la bande neutre → « Pas vendre » (rien à verrouiller).
    - Favorable (fav_now>0) :
        * 12h (fav_prec None) → « Pas vendre » (laisse courir, pic indétectable).
        * 18h : si `fav_now < fav_prec` (le gain reflue = pic passé) OU signe
          inversé (était pour nous, maintenant contre) → « Vendre » (verrouille
          près du pic) ; sinon (gain stable ou grandit) → « Pas vendre ».
    - Contre nous (fav_now<0) :
        * 12h → « Pas vendre » (laisse la journée).
        * 18h : si `fav_now < fav_prec` (ça empire) → « Vendre » (le pari ne
          paie pas) ; si ça se redresse vers l'ouverture → « Pas vendre ».
    - Données absentes (delta_now None, ou call non LONG/SHORT) → « Pas vendre »
      (défaut sûr, zéro invention).
    """
    PAS_VENDRE = "Pas vendre"
    VENDRE = "Vendre"

    fav_now = fav_delta(delta_now, call)
    if fav_now is None:
        return PAS_VENDRE  # données absentes / call inconnu → défaut sûr
    # delta_now est non-None ici (fav_now non-None ⇒ delta_now non-None).
    if abs(delta_now) / 100.0 < neutral_band_pct:
        return PAS_VENDRE  # sous la bande neutre : rien à verrouiller

    fav_prec = fav_delta(delta_prec, call)
    if fav_prec is None:
        return PAS_VENDRE  # 12h (pas de précédent) : on laisse la journée

    # 18h : on compare le favorable courant au favorable précédent.
    if fav_now > 0:
        # On gagnait / on gagne : verrouiller si le gain reflue ou s'est inversé.
        if fav_now < fav_prec:
            return VENDRE
        return PAS_VENDRE
    # fav_now < 0 (ou == 0 mais hors bande, traité comme contre nous) :
    # le pari est contre nous → vendre seulement si ça empire vs 12h.
    if fav_now < fav_prec:
        return VENDRE
    return PAS_VENDRE


def prix_courant_cascade(
    ticker: str,
    series_1h: Optional[List[Any]],
    date_j: date,
    fetch_price: Optional[Callable[[str], Optional[float]]],
) -> Optional[float]:
    """Relevé de prix du créneau via une cascade COHÉRENTE avec le bilan.

    Ordre (zéro invention — source absente → None, jamais comblé) :
      1. dernière barre 1h du jour J (close le plus frais de la séance) ;
      2. spot via fetch_price(ticker).
    C'est l'ordre miroir de `mesure_bilan._resolve_cloture` (1h → spot) restreint
    aux sources disponibles à chaud pendant la séance (pas de bougie 1day du jour
    encore, pas de relevé de suivi puisqu'on EST le suivi). Best-effort.
    """
    if not ticker:
        return None
    import mesure_bilan as MB  # noqa: PLC0415
    bars = MB._bars_du_jour(series_1h, date_j)
    if bars:
        px = bars[-1][1]
        if isinstance(px, (int, float)) and px > 0:
            return float(px)
    if fetch_price is not None:
        try:
            spot = fetch_price(ticker)
        except Exception as e:  # noqa: BLE001 — best-effort, dégrade proprement
            logger.warning("suivi %s : spot fetch KO : %s", ticker, e)
            spot = None
        if isinstance(spot, (int, float)) and spot > 0:
            return float(spot)
    return None


def excursions_suivi(
    ticker: str,
    series_1h: Optional[List[Any]],
    date_j: date,
    ouverture: Optional[float],
    call: str,
) -> tuple:
    """Excursions MAX favorable / adverse depuis l'ouverture, sur la série 1h du jour.

    RÉUTILISE `mesure_bilan._excursions_intraday` (+ `_bars_du_jour`) — la MÊME
    primitive que le Bilan du jour, AUCUNE duplication de la logique d'excursion.
    Retourne (max_favorable_pct ≥ 0, max_adverse_pct ≤ 0), ou (None, None) si la
    référence (ouverture) ou la série manque, ou si le call n'est pas LONG/SHORT.
    """
    if not isinstance(ouverture, (int, float)) or ouverture <= 0:
        return (None, None)
    if call not in ("LONG", "SHORT"):
        return (None, None)
    import mesure_bilan as MB  # noqa: PLC0415
    bars = MB._bars_du_jour(series_1h, date_j)
    if not bars:
        return (None, None)
    return MB._excursions_intraday(bars, ouverture, call)


def us_trend_flag(delta_pct: Optional[float], call: str) -> str:
    """Flag US spécifique au 18h (open US 15h30 a confirmé ou retourné le call).

    `↗ confirmé US` si le mouvement va dans le sens du call, `↘ infirmé US`
    sinon. `—` si delta absent.
    """
    sign = call_sign(call)
    if delta_pct is None or sign is None:
        return "—"
    return "↗ confirmé US" if (delta_pct > 0) == (sign > 0) else "↘ infirmé US"


# ---------------------------------------------------------------------------
# Chargement du bulletin 7h du jour (les positions à suivre)
# ---------------------------------------------------------------------------

def load_briefing_cells(date_j: date, bulletins_dir: Path) -> List[Any]:
    """Cellules 24h actionnables du Briefing 7h du jour `date_j`.

    On suit la position 24h (le call du jour). Sont exclues les cellules
    INSUFFISANT (CA-S1 : tableau = actifs actionnables uniquement). Si aucun
    bulletin 7h n'existe pour le jour → liste vide (zéro invention).
    """
    import journaliste as J  # noqa: PLC0415

    cells: List[Any] = []
    for p in J.list_bulletins(bulletins_dir):
        bid = J.bulletin_id_from_path(p)
        if bid is None:
            continue
        try:
            # L'identité de bulletin commence par la date ISO (YYYY-MM-DD).
            if J.date.fromisoformat(bid[:10]) != date_j:
                continue
        except (ValueError, AttributeError):
            continue
        if not J.is_seven_am_bulletin(bid):
            continue
        for cell in J.parse_bulletin(p):
            if cell.horizon != "24h":
                continue
            if cell.conclusion == J.CONCLUSION_INSUFFISANT:
                continue
            if cell.conclusion not in ("LONG", "SHORT"):
                continue
            cells.append(cell)
    return cells


def briefing_7h_existe(date_j: date, bulletins_dir: Path) -> bool:
    """True si un Briefing 7h du jour `date_j` est trouvable (≥ 1 cellule 24h).

    GARDE-FOU HONNÊTETÉ (brief S9) : distinguer « aucun Briefing 7h actif »
    (archivé en cours de journée / jamais émis → suivi impossible) de « briefing
    trouvé mais aucune position LONG/SHORT » (`load_briefing_cells` exclut déjà les
    INSUFFISANT, donc sa liste vide ne suffit pas à trancher). On réutilise EXACTEMENT
    la même détection que `mesure_bilan.load_cells_et_prix_7h` / `load_briefing_cells`
    (`is_seven_am_bulletin` + date du bulletin) — une seule source de vérité.

    Best-effort : toute erreur de parsing dégrade vers False (on ne fabrique pas
    un briefing inexistant ; zéro invention).
    """
    import journaliste as J  # noqa: PLC0415

    for p in J.list_bulletins(bulletins_dir):
        bid = J.bulletin_id_from_path(p)
        if bid is None:
            continue
        try:
            if J.date.fromisoformat(bid[:10]) != date_j:
                continue
        except (ValueError, AttributeError):
            continue
        if not J.is_seven_am_bulletin(bid):
            continue
        try:
            cells = J.parse_bulletin(p)
        except Exception:  # noqa: BLE001 — best-effort, dégrade proprement
            continue
        if any(getattr(c, "horizon", None) == "24h" for c in cells):
            return True
    return False


# ---------------------------------------------------------------------------
# Persistance des deltas pour la dynamique de tendance (Δ vs suivi précédent)
# ---------------------------------------------------------------------------

def _snapshot_path(date_j: date, report_type: str, base_dir: Path) -> Path:
    return base_dir / f"{date_j.isoformat()}-{report_type}.json"


def save_delta_snapshot(
    date_j: date,
    report_type: str,
    deltas: Dict[str, Optional[float]],
    base_dir: Path = SUIVI_DIR,
) -> Path:
    """Persiste les deltas% du suivi (clé = actif) pour le suivi suivant.

    Le suivi 18h lit le snapshot 12h pour calculer `Δ vs 12h` et la tendance.
    Ce fichier est un cache de PRÉSENTATION (pas une mesure) — il N'ALIMENTE
    PAS measures-log/performance (CA-S6).
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    p = _snapshot_path(date_j, report_type, base_dir)
    payload = {a: d for a, d in deltas.items() if isinstance(d, (int, float))}
    p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


def load_delta_snapshot(
    date_j: date, report_type: str, base_dir: Path = SUIVI_DIR
) -> Dict[str, float]:
    """Lit le snapshot deltas d'un suivi précédent. {} si absent (zéro invention)."""
    p = _snapshot_path(date_j, report_type, base_dir)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: Dict[str, float] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            try:
                out[str(k)] = float(v)
            except (TypeError, ValueError):
                continue
    return out


# ---------------------------------------------------------------------------
# News à impact depuis le matin (court, best-effort, zéro invention)
# ---------------------------------------------------------------------------

def news_a_impact(
    date_j: date,
    actifs: List[str],
    decision_log_dir: Path,
    max_news: int = MAX_NEWS,
) -> List[str]:
    """Lignes « news à impact » courtes, depuis le decision-log 7h du jour.

    Best-effort, ZÉRO appel DeepSeek (Q9 — suivi léger), zéro invention :
    on ne liste QUE les cellules 24h du bulletin 7h dont `news_dominant` ou
    `is_news_regime` est vrai, en nommant le critère news à plus forte
    contribution (présent dans le decision-log). Aucune cellule news → liste
    vide → message « pas de news impactante » côté rendu.
    """
    if not decision_log_dir.exists():
        return []
    prefix = date_j.isoformat()
    files = sorted(decision_log_dir.glob(f"{prefix}-*.jsonl"))
    actif_set = {a for a in actifs}
    out: List[str] = []
    seen: set = set()
    for fp in files:
        try:
            lines = fp.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            if rec.get("horizon") != "24h":
                continue
            actif = rec.get("actif")
            if actif not in actif_set or actif in seen:
                continue
            if not (rec.get("news_dominant") or rec.get("is_news_regime")):
                continue
            crit = _dominant_news_critere(rec.get("criteres") or [])
            if crit is None:
                continue
            nom, sens = crit
            seen.add(actif)
            out.append(f"- **{actif}** : {nom} → biais {sens}.")
            if len(out) >= max_news:
                return out
    return out


# Nombre max de news MAJEURES (high) affichées dans le suivi (court).
MAX_NEWS_MAJEURES = 3


def _heure_precedente_label(report_type: str) -> str:
    """Libellé court de l'heure du rapport précédent (« 7h » / « 12h »)."""
    return f"{SEUIL_HEURE_PRECEDENTE.get(report_type, 7)}h"


def news_majeures_lignes(
    report_type: str,
    now: datetime,
    events_path: Optional[Path] = None,
    max_news: int = MAX_NEWS_MAJEURES,
) -> List[str]:
    """Lignes « News majeures depuis {heure_préc} » (high matérialité, zéro DeepSeek).

    LÉGER : lecture seule de l'events-log déjà classé (réutilise le parser ROBUSTE
    par index de colonne de `briefing`, + l'horodatage d'INGESTION du batch). Pas
    de re-scoring, pas de DeepSeek.

    Filtre (cf. briefing.news_majeures_depuis) : matérialité == high ET ingéré
    DEPUIS l'heure du rapport précédent (12h → depuis 7h du jour ; 18h → depuis 12h
    du jour). Un event sans horodatage d'ingestion lisible est EXCLU (zéro
    invention, pas de supposition d'heure). Max `max_news`, triées par fraîcheur.

    Best-effort : toute erreur de lecture/parsing → liste vide (le suivi ne casse
    jamais). Retourne des lignes markdown prêtes (1 ligne/news : actif si dispo +
    résumé court). Liste vide → message « Aucune news majeure » géré au rendu.
    """
    try:
        import briefing as B  # noqa: PLC0415
        path = events_path or B.EVENTS_LOG
        events = B.parse_events_with_ingest_ts(path)
        heure_prec = SEUIL_HEURE_PRECEDENTE.get(report_type, 7)
        # Heure du rapport précédent, en Paris ce jour-là, convertie en UTC.
        cutoff_paris = datetime.combine(
            now.date(), time(hour=heure_prec), tzinfo=PARIS_TZ
        )
        cutoff_utc = cutoff_paris.astimezone(timezone.utc)
        majeures = B.news_majeures_depuis(events, cutoff_utc, now.date(), max_news)
    except Exception as e:  # noqa: BLE001 — bloc léger best-effort, jamais de crash
        logger.warning("news_majeures_lignes KO: %s — section vide", e)
        return []

    lignes: List[str] = []
    for ev in majeures:
        try:
            actif = B._primary_actif_from_event(ev)
        except Exception:  # noqa: BLE001
            actif = None
        trigger = B.strip_monetaire((ev.get("trigger", "") or "").strip())
        if not trigger:
            continue
        if len(trigger) > 160:
            trigger = trigger[:157].rstrip() + "..."
        prefixe = f"**{actif}** : " if actif and actif != "Autres" else ""
        lignes.append(f"- {prefixe}{trigger}")
    return lignes


def news_reelle_paris(
    report_type: str,
    now: datetime,
    actifs: List[str],
    events_path: Optional[Path] = None,
) -> Dict[str, str]:
    """Titre RÉEL de la news/driver dominant pour chaque actif PARI (FIX 2a, 23/06).

    Remplace le libellé opaque « Synthèse news (net, IA) » par le VRAI titre de la
    news la plus matérielle de la journée pour chaque pari. UNE source de vérité :
    l'events-log déjà classé (même que `news_majeures_lignes`), réutilise
    `briefing.parse_events_with_ingest_ts` + `_primary_actif_from_event` +
    `strip_monetaire`. Tri materiality desc puis fraîcheur (réutilise le tri de
    briefing). ZÉRO DeepSeek, ZÉRO invention : un actif sans event exploitable est
    ABSENT du dict (le rendu affichera « — »).

    Best-effort total : toute erreur de lecture/parsing → {} (le suivi ne casse
    jamais). Retourne {actif: titre_court} pour les actifs de `actifs` seulement.
    """
    cibles = {a for a in actifs}
    if not cibles:
        return {}
    try:
        import briefing as B  # noqa: PLC0415
        path = events_path or B.EVENTS_LOG
        events = B.parse_events_with_ingest_ts(path)
        # Fenêtre du jour, à impact (même filtre que le briefing 7h).
        recents = B.filter_recent_impactful(events, now.date())
        ordonnes = B._sort_by_materiality_then_date(recents)
    except Exception as e:  # noqa: BLE001 — bloc léger best-effort, jamais de crash
        logger.warning("news_reelle_paris KO: %s — section vide", e)
        return {}

    out: Dict[str, str] = {}
    for ev in ordonnes:
        try:
            actif = B._primary_actif_from_event(ev)
        except Exception:  # noqa: BLE001
            actif = None
        if not actif or actif not in cibles or actif in out:
            continue
        trigger = B.strip_monetaire((ev.get("trigger", "") or "").strip())
        if not trigger:
            continue
        if len(trigger) > 160:
            trigger = trigger[:157].rstrip() + "..."
        out[actif] = trigger
    return out


# source_track signifiant « ce créneau news porte la direction NETTE IA »
# (synthèse DeepSeek du corpus). Doit rester aligné avec
# scoring_analyste.SYNTHESE_NET_TRACKS / SYNTHESE_NET_LABEL.
_SYNTHESE_NET_TRACKS = frozenset(
    {"ia_synthese", "ia_synthese_faible", "ia_synthese_news_high"}
)
_SYNTHESE_NET_LABEL = "Synthèse news (net, IA)"


def _nom_affiche_news(nom: str, source_track: str) -> str:
    """Libellé DYNAMIQUE d'un critère news lu depuis le decision-log.

    Miroir de scoring_analyste._nom_affiche : si le créneau porte le net IA
    (source_track ∈ _SYNTHESE_NET_TRACKS) → « Synthèse news (net, IA) », sinon
    le nom de fiche tel quel. PUR AFFICHAGE, se dégrade proprement si
    source_track absent (vieux decision-logs → nom legacy, jamais de crash).
    """
    if (source_track or "").strip().lower() in _SYNTHESE_NET_TRACKS:
        return _SYNTHESE_NET_LABEL
    return nom


def _dominant_news_critere(criteres: List[dict]) -> Optional[tuple]:
    """Critère news à plus forte |contribution| dans une cellule. (nom, sens) ou None.

    On considère « news » un critère de type triplet ou dont la source vient des
    events-log. Zéro invention : si rien ne matche → None. Le `nom` retourné est
    le libellé DYNAMIQUE (cf. _nom_affiche_news) : « Synthèse news (net, IA) »
    quand le créneau porte le net, son thème de fiche sinon.
    """
    best = None
    best_abs = 0.0
    for c in criteres:
        type_norm = (c.get("type_norm") or "").lower()
        track = (c.get("source_track") or "")
        source = (track or c.get("cle") or "").lower()
        nom = (c.get("nom") or "").strip()
        is_news = type_norm == "triplet" or "event" in source or "news" in source
        if not is_news or not nom:
            continue
        try:
            contrib = float(c.get("contrib_pm1"))
        except (TypeError, ValueError):
            continue
        if abs(contrib) > best_abs:
            best_abs = abs(contrib)
            sens = "haussier" if contrib > 0 else ("baissier" if contrib < 0 else "neutre")
            best = (_nom_affiche_news(nom, track), sens)
    return best


# ---------------------------------------------------------------------------
# PARTIE B — Actus FRAÎCHES du jour (récolte RSS légère, zéro DeepSeek)
# ---------------------------------------------------------------------------
# Le suivi 12h/18h refetch les MÊMES flux RSS que le pipeline 7h (chemin
# `news_collector.collect_rss_light`, déjà filtré finance via la whitelist des
# 12 actifs), garde les titres POSTÉRIEURS au rapport précédent (12h → depuis 07h ;
# 18h → depuis 12h), les dédoublonne contre ce qui a DÉJÀ été montré (Contexte 7h
# + titres frais déjà affichés au 12h), et n'en garde que le top 1-3 par fraîcheur.
# ZÉRO appel DeepSeek (titres seuls). ZÉRO écriture dans la DB de dédup. Best-effort :
# flux KO/timeout → dégradation propre (`news_fraiches_indispo`), JAMAIS de crash.


def _normalize_titre(titre: str) -> str:
    """Clé de dédup d'un titre : minuscule, espaces réduits, ponctuation marginale ôtée."""
    t = re.sub(r"\s+", " ", (titre or "").strip().lower())
    return t.strip(" .,;:!?\"'()[]")


def _seuil_news_utc(report_type: str, now: datetime) -> datetime:
    """Seuil de fraîcheur (UTC tz-aware) = heure du rapport précédent, le jour de `now`.

    12h → 07h00 Paris du jour ; 18h → 12h00 Paris du jour. Converti en UTC pour
    comparer aux `NewsItem.published` (toujours UTC, GATE C9). DST géré par ZoneInfo
    (jamais d'offset codé en dur).
    """
    heure = SEUIL_HEURE_PRECEDENTE.get(report_type, 7)
    seuil_paris = datetime.combine(now.date(), time(hour=heure), tzinfo=PARIS_TZ)
    return seuil_paris.astimezone(timezone.utc)


def _titres_deja_vus(news_7h: List[str], snapshot_titres: List[str]) -> set:
    """Set normalisé des titres DÉJÀ montrés (Contexte 7h + frais affichés au 12h).

    `news_7h` = lignes markdown du bloc Contexte 7h (on en extrait le texte) ;
    `snapshot_titres` = titres frais persistés par le suivi précédent (12h).
    """
    seen: set = set()
    for ligne in news_7h:
        # Lignes type "- **Actif** : Titre → biais ..." → on garde le texte normalisé entier.
        seen.add(_normalize_titre(ligne))
    for t in snapshot_titres:
        seen.add(_normalize_titre(t))
    return seen


def recolte_news_fraiches(
    report_type: str,
    now: datetime,
    deja_vus: set,
    max_news: int = MAX_NEWS_FRAICHES,
    collect_light: Optional[Callable[[], list]] = None,
) -> tuple:
    """Récolte les titres RSS FRAIS depuis le créneau précédent. (lignes, titres, indispo).

    Returns:
        (lignes_markdown, titres_bruts, indispo) :
        - lignes_markdown : List[str] prêtes à afficher (top 1-3 NOUVEAUX titres).
        - titres_bruts : List[str] des titres retenus (pour persistance dédup 18h).
        - indispo : bool — True si le fetch RSS a échoué (dégradation propre, à
          distinguer du cas « 0 news fraîche » où indispo=False).

    Best-effort intégral : toute exception du fetch → ([], [], True). Zéro DeepSeek,
    zéro écriture DB. Filtre : published >= seuil, dédup contre `deja_vus` + interne,
    tri fraîcheur desc.
    """
    if collect_light is None:
        try:
            from news_collector import collect_rss_light as _cl  # noqa: PLC0415
            collect_light = _cl
        except Exception as e:  # noqa: BLE001 — module indispo → dégradation propre
            logger.warning("recolte_news_fraiches: import collect_rss_light KO: %s", e)
            return [], [], True

    try:
        items = collect_light()
    except Exception as e:  # noqa: BLE001 — fetch RSS KO/timeout → dégradation propre
        logger.warning("recolte_news_fraiches: fetch RSS KO: %s — dégradation propre", e)
        return [], [], True
    if items is None:
        return [], [], True

    seuil = _seuil_news_utc(report_type, now)
    frais = []
    for it in items:
        pub = getattr(it, "published", None)
        titre = (getattr(it, "title", "") or "").strip()
        if not titre or not isinstance(pub, datetime):
            continue
        # Normalise en UTC tz-aware avant comparaison (robustesse si source naïve).
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        else:
            pub = pub.astimezone(timezone.utc)
        if pub < seuil:
            continue  # antérieur au rapport précédent → pas « frais »
        frais.append((pub, titre, getattr(it, "source", "")))

    # Tri fraîcheur desc (le plus récent d'abord), puis dédup contre déjà-vus + interne.
    frais.sort(key=lambda x: x[0], reverse=True)
    lignes: List[str] = []
    titres: List[str] = []
    vus_local = set(deja_vus)
    for _pub, titre, source in frais:
        key = _normalize_titre(titre)
        if key in vus_local:
            continue
        vus_local.add(key)
        affiche = titre if len(titre) <= 180 else titre[:177].rstrip() + "..."
        src = f" ({source})" if source else ""
        lignes.append(f"- {affiche}{src}")
        titres.append(titre)
        if len(lignes) >= max_news:
            break
    return lignes, titres, False


def _ligne_contexte_frais(
    report_type: str, news_fraiches: List[str], indispo: bool
) -> str:
    """1 ligne factuelle de contexte réactualisé en tête du suivi.

    Style FACTUEL (décor, pas d'avis). Trois cas honnêtes :
    - flux KO → « Actus du jour indisponibles (flux injoignable). »
    - rien de frais → « Rien de neuf depuis {Xh}. »
    - news fraîche(s) → « Du neuf depuis {Xh} : N actu(s) fraîche(s) ci-dessous. »
    """
    heure_prec = SEUIL_HEURE_PRECEDENTE.get(report_type, 7)
    label = f"{heure_prec}h"
    if indispo:
        return "Actus du jour indisponibles (flux injoignable)."
    if not news_fraiches:
        return f"Rien de neuf depuis {label}."
    n = len(news_fraiches)
    s = "s" if n > 1 else ""
    return f"Du neuf depuis {label} : {n} actu{s} fraîche{s} ci-dessous."


def _snapshot_titres_path(date_j: date, report_type: str, base_dir: Path) -> Path:
    return base_dir / f"{date_j.isoformat()}-{report_type}-titres.json"


def save_titres_frais_snapshot(
    date_j: date, report_type: str, titres: List[str], base_dir: Path = SUIVI_DIR
) -> Path:
    """Persiste les titres frais affichés (clé dédup pour le suivi suivant).

    Cache de PRÉSENTATION (n'alimente PAS measures-log/performance — CA-S6). Le 18h
    lit ce fichier pour ne pas réafficher un titre déjà montré au 12h.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    p = _snapshot_titres_path(date_j, report_type, base_dir)
    p.write_text(json.dumps(list(titres), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def load_titres_frais_snapshot(
    date_j: date, report_type: str, base_dir: Path = SUIVI_DIR
) -> List[str]:
    """Lit les titres frais d'un suivi précédent. [] si absent/illisible (zéro invention)."""
    p = _snapshot_titres_path(date_j, report_type, base_dir)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [str(t) for t in data] if isinstance(data, list) else []


# ---------------------------------------------------------------------------
# Refonte bilan soir S9 — persistance intraday des relevés 12h/18h
# ---------------------------------------------------------------------------
# Le Bilan du soir doit comparer le PIC favorable atteint parmi {12h, 18h,
# clôture}. Les % à 12h/18h ne sont connus QUE le moment du suivi → on les
# persiste ici par actif sélectionné (call + % favorable signé + heure du
# relevé). Idempotent : un même créneau écrase son propre bloc, sans toucher
# l'autre. Cache de PRÉSENTATION (CA-S6 : n'alimente NI measures-log NI
# performance). Zéro invention : un actif sans fav% calculable n'est PAS écrit.

def _tracking_path(date_j: date, base_dir: Path) -> Path:
    return base_dir / f"{date_j.isoformat()}.json"


def save_suivi_tracking(
    date_j: date,
    report_type: str,
    lignes: List["SuiviLigne"],
    now: datetime,
    base_dir: Path = SUIVI_TRACKING_DIR,
) -> Optional[Path]:
    """Persiste le relevé du créneau pour les cellules de la Sélection du jour.

    Écrit `{date}.json` avec un bloc par créneau (clé "12h"/"18h") :
        {"12h": {"<actif>": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}}}
    IDEMPOTENT : relit le fichier, remplace SEULEMENT le bloc du créneau courant,
    réécrit le tout (rejouer le 12h ne touche pas le 18h, et inversement). Seules
    les lignes `selection=True` AVEC un `fav_now` calculable sont écrites (zéro
    invention : un actif sans relevé exploitable est absent → trou explicite côté
    Bilan). Retourne le chemin écrit, ou None si rien à écrire (aucune sélection
    relevable ce créneau — on n'écrase alors PAS un bloc existant).
    """
    bloc: Dict[str, dict] = {}
    for li in lignes:
        if not li.selection or li.fav_now is None:
            continue
        rec = {
            "call": li.call,
            "fav_pct": li.fav_now,
            "heure": now.strftime("%Hh%M"),
        }
        # Champs ADDITIFS (brief S9) — excursions max depuis l'ouverture, pour que
        # le Bilan du soir lise « meilleur/pire point » du créneau s'il le souhaite.
        # On n'écrit que ce qui est calculable (zéro invention) ; les clés
        # existantes (call/fav_pct/heure) sont INCHANGÉES (compat bilan_jour).
        if li.max_favorable_pct is not None:
            rec["max_fav_pct"] = li.max_favorable_pct
        if li.max_adverse_pct is not None:
            rec["max_adv_pct"] = li.max_adverse_pct
        bloc[li.actif] = rec
    if not bloc:
        return None
    base_dir.mkdir(parents=True, exist_ok=True)
    p = _tracking_path(date_j, base_dir)
    data: Dict[str, Any] = {}
    if p.exists():
        try:
            loaded = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except (OSError, json.JSONDecodeError):
            data = {}
    data[report_type] = bloc
    p.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return p


def load_suivi_tracking(
    date_j: date, base_dir: Path = SUIVI_TRACKING_DIR
) -> Dict[str, Dict[str, dict]]:
    """Lit `{date}.json` (relevés 12h/18h). {} si absent/illisible (zéro invention).

    Forme : {"12h": {"<actif>": {"call","fav_pct","heure"}}, "18h": {...}}.
    Les blocs/valeurs malformés sont ignorés sans crash (dégradation propre).
    """
    p = _tracking_path(date_j, base_dir)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, Dict[str, dict]] = {}
    for slot, bloc in data.items():
        if slot not in VALID_REPORTS or not isinstance(bloc, dict):
            continue
        clean: Dict[str, dict] = {}
        for actif, rec in bloc.items():
            if isinstance(rec, dict):
                clean[str(actif)] = rec
        out[str(slot)] = clean
    return out


# ---------------------------------------------------------------------------
# Construction du rapport de suivi
# ---------------------------------------------------------------------------

def build_suivi(
    report_type: str,
    now: Optional[datetime] = None,
    date_j: Optional[date] = None,
    bulletins_dir: Optional[Path] = None,
    decision_log_dir: Optional[Path] = None,
    suivi_dir: Path = SUIVI_DIR,
    prix_ouverture_dir: Optional[Path] = None,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    fetch_series: Optional[Any] = None,
    config: Optional[dict] = None,
    collect_light: Optional[Callable[[], list]] = None,
) -> SuiviRapport:
    """Construit le rapport de suivi 12h/18h (R2/R3).

    Pour chaque position 24h du Briefing 7h : statut vs ouverture, dynamique de
    tendance (vs suivi précédent), suggestion de sortie (drapeau). Les actifs US
    sont marqués « pas encore ouvert » tant que leur marché n'est pas ouvert
    (typiquement à 12h). Léger : prix + news, PAS de scoring (Q9).

    `now` (Europe/Paris) paramétrable pour l'injection en test.
    """
    import journaliste as J  # noqa: PLC0415
    import mesure_ouverture as MO  # noqa: PLC0415

    if report_type not in VALID_REPORTS:
        raise ValueError(
            f"report_type invalide : {report_type!r} (attendu {VALID_REPORTS})"
        )

    now = now or datetime.now(PARIS_TZ)
    now = now.replace(tzinfo=PARIS_TZ) if now.tzinfo is None else now.astimezone(PARIS_TZ)
    date_j = date_j or now.date()
    if bulletins_dir is None:
        bulletins_dir = J.BULLETINS_DIR
    if decision_log_dir is None:
        from bilan_jour import DECISION_LOG_DIR as _DLD  # noqa: PLC0415
        decision_log_dir = _DLD
    config = config if config is not None else MO.load_suivi_config()
    fiches = fiches if fiches is not None else J.load_fiches()
    if fetch_price is None:
        import criteres_calculator  # noqa: PLC0415
        fetch_price = criteres_calculator.fetch_twelve_price
    if fetch_series is None:
        import criteres_calculator  # noqa: PLC0415
        fetch_series = criteres_calculator.fetch_twelve_series

    if prix_ouverture_dir is None:
        prix_ouverture_dir = MO.PRIX_OUVERTURE_DIR
    band = MO.neutral_band_pct(config)
    ouvertures = MO.load_prix_ouverture(date_j, prix_ouverture_dir)
    cells = load_briefing_cells(date_j, bulletins_dir)
    # GARDE-FOU HONNÊTETÉ (brief S9) : un Briefing 7h archivé en cours de journée
    # rendait `cells` vide → tableau VIDE silencieux (cause du suivi 18h vide
    # d'aujourd'hui). On détecte explicitement l'absence de Briefing 7h pour
    # distinguer ce cas de « briefing trouvé mais 0 position » (message différent).
    briefing_introuvable = not briefing_7h_existe(date_j, bulletins_dir)

    # Sélection du jour (top ≤3) : champ shadow `selection_du_jour` du
    # decision-log du jour. Réutilise le mapping mesuré du Bilan (zéro invention :
    # une cellule absente / false → non sélectionnée). Dégradation propre si KO.
    try:
        from bilan_jour import load_selection_map  # noqa: PLC0415
        selection_map = load_selection_map(date_j, decision_log_dir)
    except Exception as e:  # noqa: BLE001 — mapping indispo → aucune sélection (pas d'invention)
        logger.warning("build_suivi: load_selection_map KO: %s — aucune sélection", e)
        selection_map = {}

    # Snapshot du suivi précédent (12h) pour la dynamique au 18h.
    prev = load_delta_snapshot(date_j, REPORT_12H, suivi_dir) if report_type == REPORT_18H else {}

    rapport = SuiviRapport(date_j=date_j, now=now, report_type=report_type)
    rapport.briefing_introuvable = briefing_introuvable
    deltas_now: Dict[str, Optional[float]] = {}
    # Cache des séries 1h par ticker (1 fetch/ticker pour TOUT le suivi). Sert au
    # relevé de prix (cascade 1h → spot) ET aux excursions intraday max (réutilise
    # mesure_bilan). Best-effort : un fetch KO → None (le spot reste le fallback).
    cache_1h: Dict[str, Optional[List[Any]]] = {}

    def _series_1h(tkr: str) -> Optional[List[Any]]:
        if not tkr or fetch_series is None:
            return None
        if tkr not in cache_1h:
            try:
                cache_1h[tkr] = fetch_series(tkr, interval="1h", outputsize=24)
            except Exception as e:  # noqa: BLE001 — best-effort, dégrade proprement
                logger.warning("suivi %s : fetch_series 1h KO : %s", tkr, e)
                cache_1h[tkr] = None
        return cache_1h[tkr]

    for cell in cells:
        actif = cell.actif_name
        call = cell.conclusion
        found = J.fiche_for_actif_name(fiches, actif)
        fiche = found[1] if found else {}
        ticker = fiche.get("ticker_principal", "")
        group = MO.actif_group(fiche, config) if fiche else None
        seuil = None
        try:
            seuil_raw = (fiche.get("seuils_reussite_pct") or {}).get("24h")
            seuil = float(seuil_raw) if seuil_raw is not None else None
        except (TypeError, ValueError):
            seuil = None

        # Marché US pas encore ouvert (typiquement à 12h) → ligne explicite.
        # Twelve GROW ne sert aucune donnée US fiable hors séance cash (futures
        # CME vides/figés, CFD vides, prepost vide — sonde 23/06). On affiche donc
        # honnêtement « cash fermé (ouvre 15h30) » : le suivi US réel commence à
        # l'ouverture cash (15h30 Paris), capté par le stamp d'ouverture.
        us_pas_ouvert = (
            group == "us" and not MO.is_open_for_stamp("us", now, config)
        )
        is_select = bool(selection_map.get((actif, "24h"), False))
        if us_pas_ouvert:
            rapport.lignes.append(SuiviLigne(
                actif=actif, call=call, ouverture=None, prix_courant=None,
                delta_pct=None, statut="🕐 cash fermé (ouvre 15h30)", tendance="—",
                delta_vs_prec=None, suggestion="—", seuil_pct=seuil,
                us_pas_ouvert=True, vendre="Pas vendre", selection=is_select,
                fav_now=None, fav_prec=None,
            ))
            continue

        ouverture = ouvertures.get(ticker)
        # Relevé de prix via cascade COHÉRENTE avec le bilan (dernière barre 1h →
        # spot). La série 1h sert AUSSI aux excursions max ci-dessous (1 fetch).
        series_1h = _series_1h(ticker)
        prix_courant = prix_courant_cascade(ticker, series_1h, date_j, fetch_price)
        # Excursions MAX favorable / adverse depuis l'ouverture (mesure_bilan).
        max_fav, max_adv = excursions_suivi(
            ticker, series_1h, date_j, ouverture, call
        )
        delta = None
        if isinstance(ouverture, (int, float)) and isinstance(prix_courant, (int, float)) and ouverture:
            delta = (prix_courant - ouverture) / ouverture * 100.0
            delta = round(delta, 2)
        deltas_now[actif] = delta

        statut = compute_statut(delta, call, band)
        # [H-S2/I-4 audit visuel 12/06] : au 18h, les marchés US sont ouverts
        # depuis 15h30. Si on a un prix 18h mais PAS d'ouverture stampée (delta
        # None), un statut « — » est confusant (donne l'impression d'un actif
        # non ouvert). On marque explicitement « ⏳ données manquantes » (zéro
        # invention : on ne fabrique pas d'ouverture, on dit juste qu'elle manque).
        if (
            report_type == REPORT_18H
            and group == "us"
            and delta is None
            and isinstance(prix_courant, (int, float))
        ):
            statut = "⏳ données manquantes"
        # Tendance : générique (vs précédent) ; pour les actifs US au 18h on
        # surclasse par le flag US (open 15h30 a confirmé/infirmé le call).
        delta_prec = prev.get(actif)
        tendance = compute_tendance(delta, delta_prec, group == "us", band)
        if report_type == REPORT_18H and group == "us" and delta is not None:
            tendance = us_trend_flag(delta, call)
        suggestion = compute_suggestion(delta, call, seuil, statut)
        # Reco binaire « Vendre / Pas vendre » DÉRIVÉE de la suggestion (FIX 1,
        # 23/06) : source de vérité UNIQUE → la colonne « Vendre ? » de la table
        # Sélection et le bloc « Suggestions de sortie » ne se contredisent JAMAIS
        # (mêmes seuils, mêmes verdicts). + % directionnels favorables signés.
        vendre = vendre_from_suggestion(suggestion)
        fav_now_v = fav_delta(delta, call)
        fav_prec_v = fav_delta(delta_prec, call) if isinstance(delta_prec, (int, float)) else None

        rapport.lignes.append(SuiviLigne(
            actif=actif, call=call, ouverture=ouverture, prix_courant=prix_courant,
            delta_pct=delta, statut=statut, tendance=tendance,
            delta_vs_prec=(round(delta - delta_prec, 2)
                           if (delta is not None and isinstance(delta_prec, (int, float)))
                           else None),
            suggestion=suggestion, seuil_pct=seuil, us_pas_ouvert=False,
            vendre=vendre, selection=is_select,
            fav_now=(round(fav_now_v, 2) if fav_now_v is not None else None),
            fav_prec=(round(fav_prec_v, 2) if fav_prec_v is not None else None),
            max_favorable_pct=(round(max_fav, 2) if max_fav is not None else None),
            max_adverse_pct=(round(max_adv, 2) if max_adv is not None else None),
        ))

    # FIX 2a/2c (fondateur 23/06) — la section news est CENTRÉE sur les paris :
    # titre RÉEL de la news dominante par pari (events-log), PAS « Synthèse news
    # (net, IA) » ni des actifs non-paris. `rapport.news` (Contexte 7h opaque) est
    # SUPPRIMÉ du rendu ; on ne garde qu'une liste vide pour la dédup des frais.
    selection_actifs = [li.actif for li in rapport.lignes if li.selection]
    rapport.news_paris = news_reelle_paris(report_type, now, selection_actifs)
    rapport.news = []

    # VRAIE raison du call (drivers du score 7h) pour les positions de la Sélection —
    # même source unique que le bilan jour/semaine (journaliste.drivers_du_call). On
    # explique « pourquoi on tient » chaque position, jamais une news lambda.
    selected_lignes = [li for li in rapport.lignes if li.selection]
    if selected_lignes:
        try:
            from bilan_jour import load_conviction_records  # noqa: PLC0415
            conv = load_conviction_records(date_j, decision_log_dir)
            for li in selected_lignes:
                rec = conv.get((li.actif, "24h")) or {}
                drivers = J.drivers_du_call(rec, li.call)
                if drivers:
                    li.raison_call = " + ".join(drivers)
        except Exception as e:  # noqa: BLE001 — best-effort, jamais bloquant
            logger.warning("build_suivi: raison_call KO (non bloquant) : %s", e)

    # PARTIE B — actus FRAÎCHES du jour (récolte RSS légère, best-effort, zéro DeepSeek).
    # Dédup contre : (1) le Contexte 7h affiché ci-dessus, (2) les titres frais déjà
    # montrés au 12h (snapshot, lu seulement au 18h). Best-effort total : une erreur
    # ne doit jamais casser le suivi (le suivi reste fonctionnel hors-ligne).
    snapshot_titres = (
        load_titres_frais_snapshot(date_j, REPORT_12H, suivi_dir)
        if report_type == REPORT_18H else []
    )
    deja_vus = _titres_deja_vus(rapport.news, snapshot_titres)
    try:
        lignes_frais, titres_frais, indispo = recolte_news_fraiches(
            report_type, now, deja_vus, collect_light=collect_light
        )
    except Exception as e:  # noqa: BLE001 — garde-fou ultime : jamais de crash sur la récolte
        logger.warning("build_suivi: récolte news fraîches KO: %s — dégradation propre", e)
        lignes_frais, titres_frais, indispo = [], [], True
    rapport.news_fraiches = lignes_frais
    rapport.news_fraiches_indispo = indispo
    rapport.contexte_frais = _ligne_contexte_frais(report_type, lignes_frais, indispo)

    # Section « News majeures depuis {heure_préc} » : high matérialité de l'events-log
    # ingérées depuis le rapport précédent (lecture seule, zéro DeepSeek). Best-effort.
    rapport.news_majeures = news_majeures_lignes(report_type, now)

    rapport.markdown = _render_markdown(rapport)

    # Persiste les deltas du 12h pour le suivi 18h (cache de présentation only).
    if report_type == REPORT_12H:
        save_delta_snapshot(date_j, REPORT_12H, deltas_now, suivi_dir)
        # Persiste aussi les titres frais affichés au 12h → dédup au 18h.
        save_titres_frais_snapshot(date_j, REPORT_12H, titres_frais, suivi_dir)

    # Persiste le relevé intraday de la Sélection (call + fav% + heure) pour le
    # Bilan du soir — aux DEUX créneaux (12h ET 18h, le Bilan reconstruit le pic
    # sur ces points + la clôture). Best-effort : un échec ne casse jamais le
    # suivi (cache de présentation). v3/data/ jamais commité par l'agent.
    try:
        save_suivi_tracking(date_j, report_type, rapport.lignes, now)
    except Exception as e:  # noqa: BLE001 — persistance non-critique
        logger.warning("build_suivi: save_suivi_tracking KO: %s", e)
    return rapport


def _fmt_fav(v: Optional[float]) -> str:
    """% directionnel signé favorable : `+` = va dans le sens du call, `−` = contre.

    `—` (placeholder de cellule vide) si non calculable. Le signe `+/-` est rendu
    par `_fmt_pct` (les signes ASCII sont conservés tels quels par marked).
    """
    return _fmt_pct(v)


def _render_selection_table(r: SuiviRapport) -> List[str]:
    """Tableau de PROGRESSION focalisé « Sélection du jour » (top ≤3), en tête.

    Colonnes : Actif | Call 7h | % vs ouv. 12h | % vs ouv. 18h | Tendance |
    Vendre / Pas vendre. Le `%` est le mouvement directionnel signé FAVORABLE
    (`+` = va dans le sens du call, `−` = contre nous). Au 12h : seule la colonne
    « 12h » est remplie. Au 18h : les deux. Si aucune cellule `selection_du_jour`
    ce jour-là → « Pas de sélection aujourd'hui » (zéro invention).
    """
    L: List[str] = []
    L.append("### Sélection du jour — progression")
    L.append("")
    selection = [li for li in r.lignes if li.selection]
    if not selection:
        L.append("Pas de sélection aujourd'hui.")
        L.append("")
        return L

    is_12h = r.report_type == REPORT_12H
    # La décision de sortie est ANCRÉE à l'heure du rapport (au prix de ce
    # moment-là) : « Vendre à 12h » ou « Vendre à 18h ». Indispensable pour mesurer
    # ensuite si on aurait dû sortir plus tôt (le prix de sortie dépend de l'heure).
    hour_label = "12h" if is_12h else "18h"
    # En-têtes % à double libellé : complet sur desktop, court sur mobile (CSS
    # .c-full / .c-short) pour que la colonne décision reste visible sur petit écran.
    L.append(
        "| Actif "
        "| <span class=\"c-full\">Call 7h</span><span class=\"c-short\">Call</span> "
        "| <span class=\"c-full\">Prix d'entrée</span><span class=\"c-short\">Entrée</span> "
        "| <span class=\"c-full\">% vs ouv. 12h</span><span class=\"c-short\">% 12h</span> "
        "| <span class=\"c-full\">% vs ouv. 18h</span><span class=\"c-short\">% 18h</span> "
        "| <span class=\"c-full\">Meilleur point</span><span class=\"c-short\">Best</span> "
        "| <span class=\"c-full\">Pire point</span><span class=\"c-short\">Pire</span> "
        "| Tendance "
        f"| Vendre à {hour_label} ? |"
    )
    L.append("|---|---|---|---|---|---|---|---|---|")
    for li in selection:
        if is_12h:
            # Au 12h : colonne 12h = favorable courant, colonne 18h = vide.
            col_12 = _fmt_fav(li.fav_now)
            col_18 = "—"
        else:
            # Au 18h : colonne 12h = favorable précédent (snapshot 12h), 18h = courant.
            col_12 = _fmt_fav(li.fav_prec)
            col_18 = _fmt_fav(li.fav_now)
        # Meilleur / pire point depuis l'ouverture (excursions max, mesure_bilan).
        col_best = _fmt_pct(li.max_favorable_pct)
        col_pire = _fmt_pct(li.max_adverse_pct)
        # Prix d'entrée = prix d'ouverture (la référence du %).
        L.append(
            f"| {li.actif} | {li.call} | {_fmt_price(li.ouverture)} | {col_12} | {col_18} | "
            f"{col_best} | {col_pire} | {li.tendance} | **{li.vendre}** |"
        )
    L.append("")
    # FIX 4 (fondateur 23/06) — légende courte : 1 phrase, détail replié.
    L.append(
        "_Vendre = sortir maintenant ; % favorable `+`=gagne / `-`=perd ; "
        "Meilleur/Pire = excursion max depuis l'ouverture._"
    )
    L.append("")
    # Pourquoi on tient ces positions : la VRAIE raison du call (drivers du score à
    # l'émission 7h), comme le bilan jour/semaine — pas une news lambda.
    avec_raison = [li for li in selection if li.raison_call]
    if avec_raison:
        L.append("**Pourquoi ces positions (signal à 7h) :**")
        L.append("")
        for li in avec_raison:
            L.append(f"- **{li.actif}** ({li.call}) : {li.raison_call}")
        L.append("")
    return L


# GARDE-FOU HONNÊTETÉ (brief S9) — message affiché quand le Briefing 7h du jour
# est INTROUVABLE (archivé en cours de journée / jamais émis). Distinct du cas
# « briefing trouvé mais 0 position » : ici le suivi des positions est IMPOSSIBLE,
# on ne montre PAS un tableau vide silencieux (cause du suivi 18h vide d'aujourd'hui).
_MSG_BRIEFING_INTROUVABLE = (
    "Briefing 7h du jour introuvable : suivi des positions impossible "
    "(aucun bulletin 7h actif pour ce jour). À ne pas lire comme « aucune position »."
)


def _render_markdown(r: SuiviRapport) -> str:
    """Markdown court du suivi (CA-S1/S5). WIN RATE ONLY — pas de matrice LONG/SHORT."""
    heure = r.now.strftime("%Hh%M")
    h = r.report_type
    L: List[str] = []
    # [I-7 audit visuel 12/06] : H1 pour tous les rapports (cohérence avec le
    # Briefing — le suivi était en H2).
    L.append(f"# Suivi {h} · {r.date_j.isoformat()} {heure}")
    L.append("")

    # GARDE-FOU HONNÊTETÉ : Briefing 7h introuvable → on l'affiche EXPLICITEMENT en
    # tête et on s'arrête là (rien à suivre, pas de tableau vide silencieux).
    if r.briefing_introuvable:
        L.append(f"⚠️ **{_MSG_BRIEFING_INTROUVABLE}**")
        L.append("")
        return "\n".join(L)

    # FIX 2c (fondateur 23/06) — le bloc « Actus du jour » (titres RSS bruts de
    # faible matérialité) étant SUPPRIMÉ, on ne rend plus la ligne de contexte
    # « Du neuf depuis Xh… ci-dessous » qui y renvoyait (plus de bloc en dessous).

    # Refonte suivi S9 (Thomas) — vue rapide en TÊTE : progression de la
    # Sélection du jour (top ≤3) + reco Vendre/Pas vendre. Le suivi détaillé de
    # TOUTES les positions 24h reste plus bas.
    L.extend(_render_selection_table(r))

    L.append("### Suivi détaillé : toutes les positions 24h")
    L.append("")
    if h == REPORT_12H:
        L.append("### Note sur les marchés US")
        L.append(
            "⚠️ Cash US (S&P 500, Nasdaq, VIX) ouvre à 15h30 Paris. Notre "
            "fournisseur de données ne sert ni les futures CME, ni les CFD, ni le "
            "pré-marché US : avant 15h30, aucun prix US fiable n'existe pour nous "
            "(donnée absente, pas marché endormi). Premier statut US au suivi 18h."
        )
        L.append("")
        L.append("### Positions du matin vs ouverture")
    else:
        L.append("### Positions vs ouverture + dynamique intraday")

    L.append("")
    # [H-S1/P-S1/I-1 audit visuel 12/06] : au 12h, les colonnes « Δ précédent »
    # et « Tendance » sont structurellement vides (pas de suivi antérieur) → on
    # les RETIRE (tableau 7 colonnes). Au 18h, elles sont remplies → tableau 9
    # colonnes. Le libellé de la colonne delta est UNIFORME : « Δ précédent »
    # (au lieu de « Δ vs 7h » / « Δ vs 12h » — incohérence inter-rapports).
    # FIX 1 + FIX 3 (fondateur 23/06) : ce tableau est un PANORAMA de marché (on ne
    # détient PAS ces actifs) → la colonne « Vendre / Pas vendre » est RETIRÉE (aucune
    # reco de vente hors paris). La colonne % est le % FAVORABLE signé par le call
    # (`+` = va dans notre sens, `−` = contre) — MÊME convention que la table Sélection,
    # plus jamais de signes opposés pour le même actif.
    if h == REPORT_12H:
        L.append(
            f"| Actif | Call 7h | Ouverture | Prix {h} | % favorable | Statut |"
        )
        L.append("|---|---|---|---|---|---|")
        if not r.lignes:
            L.append("| _aucune position actionnable du Briefing 7h_ | | | | | |")
        for li in r.lignes:
            L.append(
                f"| {li.actif} | {li.call} | {_fmt_price(li.ouverture)} | "
                f"{_fmt_price(li.prix_courant)} | {_fmt_fav(li.fav_now)} | "
                f"{li.statut} |"
            )
    else:
        L.append(
            f"| Actif | Call 7h | Ouverture | Prix {h} | % favorable | Δ précédent | "
            f"Tendance | Statut |"
        )
        L.append("|---|---|---|---|---|---|---|---|")
        if not r.lignes:
            L.append("| _aucune position actionnable du Briefing 7h_ | | | | | | | |")
        for li in r.lignes:
            L.append(
                f"| {li.actif} | {li.call} | {_fmt_price(li.ouverture)} | "
                f"{_fmt_price(li.prix_courant)} | {_fmt_fav(li.fav_now)} | "
                f"{_fmt_points(li.delta_vs_prec)} | {li.tendance} | {li.statut} |"
            )
    L.append("")

    # FIX 2a/2c (fondateur 23/06) — section news CENTRÉE sur les paris : la VRAIE
    # news/driver dominant(e) de chaque pari (titre réel issu de l'events-log),
    # PAS le libellé opaque « Synthèse news (net, IA) » ni des actifs non-paris.
    # Le bloc « Contexte news (Synthèse net IA) » et « Actus du jour » (titres bruts
    # de faible matérialité) sont SUPPRIMÉS. Zéro invention : pas de titre → « — ».
    L.append("### News des paris du jour")
    paris = [li for li in r.lignes if li.selection]
    if paris:
        for li in paris:
            titre = r.news_paris.get(li.actif)
            L.append(f"- **{li.actif}** ({li.call}) : {titre if titre else '—'}")
    else:
        L.append("Pas de sélection aujourd'hui.")
    L.append("")

    # FIX 2b (fondateur 23/06) — GARDÉ : les grosses actus à FORTE matérialité
    # (high) depuis le rapport précédent, MÊME hors des 3 paris (ex. Pétrole /
    # Ormuz). Lecture seule de l'events-log déjà classé, zéro DeepSeek.
    heure_prec_label = _heure_precedente_label(h)
    L.append(f"### 🚨 Grosses actualités depuis {heure_prec_label}")
    if r.news_majeures:
        L.extend(r.news_majeures[:MAX_NEWS_MAJEURES])
    else:
        L.append(f"Aucune actualité majeure depuis {heure_prec_label}.")
    L.append("")

    # Suggestions de sortie (drapeaux — Thomas décide). FIX 1 (fondateur 23/06) :
    # PORTE UNIQUEMENT sur les 3 paris du jour (selection=True), JAMAIS sur un
    # actif non détenu. Même verdict que la colonne « Vendre ? » (source unique).
    L.append("### Suggestions de sortie")
    sorties = [
        li for li in r.lignes
        if li.selection and li.suggestion == "Sortie à envisager"
    ]
    if sorties:
        for li in sorties:
            L.append(
                f"- ⚠️ **{li.actif}** ({li.call}) : {_fmt_pct(li.delta_pct)} contre "
                f"le call (seuil {_fmt_pct(li.seuil_pct, signed=False)}). "
                f"Sortie à envisager : drapeau, Thomas décide."
            )
    else:
        L.append("Aucune alerte de sortie.")
    L.append("")

    # [I-6 audit visuel 12/06] : catalyseurs du lendemain au suivi 18h (Thomas
    # décide en fin de journée s'il garde ses positions overnight). Copie légère
    # depuis le calendrier éco (même source que le Bilan du jour, zéro invention).
    if h == REPORT_18H:
        L.append("### Catalyseurs J+1")
        L.extend(_catalyseurs_j1_court(r.now))
        L.append("")
    return "\n".join(L)


def _catalyseurs_j1_court(now: datetime) -> List[str]:
    """Catalyseurs J+1 en 1-2 lignes pour le suivi 18h (I-6).

    Réutilise `bilan_jour._catalyseurs_j1` (même calendrier éco statique, même
    format ~/🔴/🟡) — zéro nouvelle source, zéro invention. Best-effort : si le
    calendrier est indisponible, message propre via la fonction réutilisée.
    """
    try:
        from bilan_jour import _catalyseurs_j1  # noqa: PLC0415
        return _catalyseurs_j1(now)
    except Exception as e:  # noqa: BLE001
        logger.warning("catalyseurs J+1 (suivi 18h) indisponibles : %s", e)
        return ["Catalyseurs J+1 indisponibles (calendrier éco)."]


def write_suivi(rapport: SuiviRapport, base_dir: Path = SUIVI_DIR) -> Path:
    """Écrit le suivi dans v3/data/suivi/{date}-{heure}.md."""
    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = base_dir / f"{rapport.date_j.isoformat()}-{rapport.report_type}.md"
    out_path.write_text(rapport.markdown + "\n", encoding="utf-8")
    logger.info("Suivi %s écrit : %s", rapport.report_type, out_path)
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Suivi intra-journée 12h/18h (R2/R3).")
    parser.add_argument(
        "report_type", choices=list(VALID_REPORTS),
        help="Créneau du suivi (12h ou 18h).",
    )
    args = parser.parse_args(argv)

    now = datetime.now(PARIS_TZ)
    logger.info("=== Suivi %s runner (%s Europe/Paris) ===", args.report_type, now.isoformat())
    try:
        rapport = build_suivi(args.report_type, now=now)
        out_path = write_suivi(rapport)
    except Exception as e:  # noqa: BLE001
        logger.error("run_suivi KO : %s", e)
        return 1
    n_sorties = sum(1 for li in rapport.lignes if li.suggestion == "Sortie à envisager")
    logger.info(
        "OK : %s (%d positions, %d suggestions de sortie)",
        out_path, len(rapport.lignes), n_sorties,
    )
    print(f"OK : {out_path}")
    return 0


__all__ = [
    "REPORT_12H",
    "REPORT_18H",
    "VALID_REPORTS",
    "SuiviLigne",
    "SuiviRapport",
    "call_sign",
    "compute_statut",
    "compute_tendance",
    "compute_suggestion",
    "compute_vendre",
    "vendre_from_suggestion",
    "news_reelle_paris",
    "fav_delta",
    "us_trend_flag",
    "prix_courant_cascade",
    "excursions_suivi",
    "load_briefing_cells",
    "briefing_7h_existe",
    "save_delta_snapshot",
    "load_delta_snapshot",
    "news_a_impact",
    "news_majeures_lignes",
    "recolte_news_fraiches",
    "save_titres_frais_snapshot",
    "load_titres_frais_snapshot",
    "save_suivi_tracking",
    "load_suivi_tracking",
    "SUIVI_TRACKING_DIR",
    "build_suivi",
    "write_suivi",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
