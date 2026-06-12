"""TradingApp v3 — Bilan du jour 22h (R4, Phase 1 refonte 5 rapports).

Source de vérité : `v3/docs/reco/spec-refonte-5-rapports.md` §3.4 + §7 (CA-B*).

Le Bilan du jour note les calls 24h du Briefing 7h (sens clôture−ouverture vs
call), produit le win rate du jour, liste les calls FAUX à forte amplitude (tri
par amplitude — WIN RATE ONLY, l'amplitude trie les erreurs, ne mesure aucun
gain), les news qui ont compté (Option C : croisement news × actifs notés) et
les catalyseurs J+1 best-effort.

Périmètre Phase 1 : ce module EXPOSE la fonction de bilan, appelable avec un
paramètre `now` (datetime Europe/Paris). Le déclenchement réel à 22h15 Paris est
géré par l'infra (cron + garde heure-Paris), PAS ici.

Garde-fous :
- WIN RATE ONLY — aucune valeur monétaire (€/$/gain/perte/rendement). Jamais.
- Référence 24h = prix d'OUVERTURE (prix-ouverture/{date}.json), pas prix 7h.
- Zéro invention : prix/news/catalyseur absent → marqué indisponible, pas inventé.
- DST : heures via ZoneInfo(Europe/Paris), jamais d'offset codé en dur.
"""

from __future__ import annotations

import glob
import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger("bilan_jour")

ROOT = Path(__file__).resolve().parents[1]
BULLETINS_DIR = ROOT / "data" / "bulletins"
DECISION_LOG_DIR = ROOT / "data" / "decision-log"
BILAN_JOUR_DIR = ROOT / "data" / "bilan-jour"
MANAGER_CONFIG_FILE = ROOT / "config" / "manager.yaml"

PARIS_TZ = ZoneInfo("Europe/Paris")

# Multiplicateur d'amplitude pour le flag « gros move » (spec §3.4) :
# FAUSSE ET |delta%| >= GROS_MOVE_FACTOR × seuil_actif → ⚡ gros move (erreur
# prioritaire). WIN-RATE-ONLY : sert UNIQUEMENT à TRIER les erreurs, jamais à
# chiffrer une perte.
GROS_MOVE_FACTOR = 2.0

# CA-B2 — Marqueur de clôture EU approximative (fallback Q5).
# Apposé sur la clôture d'un actif EU (CAC) quand on n'a PAS pu obtenir le close
# officiel 17h30 et qu'on retombe sur le dernier prix disponible (spot 22h).
# Zéro invention : on ne fabrique jamais un close, on signale l'approximation.
CLOSE_APPROX_MARKER = "[close approx]"

# Seuil de conviction forte par défaut (overridé par manager.yaml).
# NB : le score du decision-log (`score_pm1`) n'est PAS normalisé dans [0,1] —
# il vit sur l'échelle ±5..±14. La valeur nominale 0.6 de la spec §4.7 est
# « 60% du max » : tant qu'aucune normalisation validée n'existe, on compare
# |score_pm1| à ce seuil BRUT et on documente que la valeur doit être calibrée
# sur la distribution réelle (mesurer avant d'agir). Configurable.
DEFAULT_SCORE_FORT_SEUIL = 0.6


def _load_score_fort_seuil(path: Path = MANAGER_CONFIG_FILE) -> float:
    if not path.exists():
        return DEFAULT_SCORE_FORT_SEUIL
    try:
        import yaml  # noqa: PLC0415
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        val = data.get("score_fort_seuil")
        return float(val) if val is not None else DEFAULT_SCORE_FORT_SEUIL
    except Exception as e:  # noqa: BLE001
        logger.warning("manager.yaml illisible : %s — défaut", e)
        return DEFAULT_SCORE_FORT_SEUIL


# ---------------------------------------------------------------------------
# Conviction (CA-W6 / §4.7) — calculée depuis le decision-log
# ---------------------------------------------------------------------------

def conviction_level(record: dict, score_fort_seuil: float) -> str:
    """Niveau de conviction d'une cellule du decision-log (§4.7).

    Conviction FORTE : |score_pm1| >= seuil ET aucun drapeau actif parmi
    mono_critere_dominant (◧) / diverge (⇆ contradiction) / coin_flip (↯) /
    quasi_neutre (~). Sinon FAIBLE. Zéro invention : un drapeau absent du record
    est traité comme False (non actif).

    Retourne "forte" ou "faible".
    """
    try:
        score = abs(float(record.get("score_pm1")))
    except (TypeError, ValueError):
        score = 0.0
    drapeaux = (
        bool(record.get("mono_critere_dominant"))
        or bool(record.get("diverge"))
        or bool(record.get("coin_flip"))
        or bool(record.get("quasi_neutre"))
    )
    if score >= score_fort_seuil and not drapeaux:
        return "forte"
    return "faible"


def load_conviction_map(
    bulletin_date: date,
    decision_log_dir: Path = DECISION_LOG_DIR,
    score_fort_seuil: Optional[float] = None,
) -> Dict[Tuple[str, str], str]:
    """Mappe (actif, horizon) -> niveau de conviction pour le bulletin 7h du jour.

    Lit les decision-log du jour ; pour chaque cellule garde le DERNIER record
    (le bulletin du jour reflète le dernier run). Dict vide si rien (zéro
    invention — les cellules sans record n'ont pas de conviction).
    """
    if score_fort_seuil is None:
        score_fort_seuil = _load_score_fort_seuil()
    result: Dict[Tuple[str, str], str] = {}
    if not decision_log_dir.exists():
        return result
    prefix = bulletin_date.isoformat()
    files = sorted(decision_log_dir.glob(f"{prefix}-*.jsonl"))
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    if rec.get("bulletin_date") != prefix:
                        continue
                    actif = rec.get("actif")
                    horizon = rec.get("horizon")
                    if not actif or not horizon:
                        continue
                    result[(str(actif), str(horizon))] = conviction_level(
                        rec, score_fort_seuil
                    )
        except OSError as e:
            logger.warning("decision-log illisible %s : %s", fp, e)
            continue
    return result


def load_selection_map(
    bulletin_date: date,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> Dict[Tuple[str, str], bool]:
    """Mappe (actif, horizon) -> `selection_du_jour` pour le bulletin du jour.

    Étage 1c (décision fondateur 12/06) — la « Sélection du jour » devient un
    objet MESURÉ : on lit le champ shadow `selection_du_jour` des records du
    decision-log du jour (dernier record par cellule, comme conviction). Seules
    les cellules explicitement `selection_du_jour: true` sont retenues (toute
    autre — false OU champ absent, anciens logs — est NON sélectionnée : zéro
    invention, dégradation propre). N'altère NI score NI win rate global.
    """
    result: Dict[Tuple[str, str], bool] = {}
    if not decision_log_dir.exists():
        return result
    prefix = bulletin_date.isoformat()
    files = sorted(decision_log_dir.glob(f"{prefix}-*.jsonl"))
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    if rec.get("bulletin_date") != prefix:
                        continue
                    actif = rec.get("actif")
                    horizon = rec.get("horizon")
                    if not actif or not horizon:
                        continue
                    # Champ absent (anciens logs) → False (dégradation propre).
                    result[(str(actif), str(horizon))] = bool(
                        rec.get("selection_du_jour", False)
                    )
        except OSError as e:
            logger.warning("decision-log illisible %s : %s", fp, e)
            continue
    return result


@dataclass
class WinRateSelection:
    """Agrégat WR de la « Sélection du jour » (Étage 1c). WIN RATE ONLY.

    n_select = cellules sélectionnées conclusives (VRAI+FAUSSE) ; n_vrai_select =
    celles VRAI. Les non-conclusives (NC) sont exclues, comme le WR global.
    """
    n_select: int = 0
    n_vrai_select: int = 0

    @property
    def taux(self) -> Optional[float]:
        return round(self.n_vrai_select / self.n_select * 100.0, 1) if self.n_select else None


def win_rate_selection(
    measures: List[Any],
    selection_map: Dict[Tuple[str, str], bool],
) -> WinRateSelection:
    """WR des cellules de la « Sélection du jour » (Étage 1c).

    `measures` : objets avec .outcome, .cell.actif_name, .horizon. On ne compte
    que VRAI/FAUSSE des cellules `selection_du_jour: true` (mêmes règles VRAI/
    FAUSSE/NC que le WR global). Cellule sans entrée = non sélectionnée (exclue).
    """
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415

    wr = WinRateSelection()
    for m in measures:
        if m.outcome not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        if not selection_map.get((m.cell.actif_name, m.horizon), False):
            continue
        wr.n_select += 1
        if m.outcome == OUTCOME_VRAI:
            wr.n_vrai_select += 1
    return wr


# ---------------------------------------------------------------------------
# A5 (audit momentum-family 10/06) — métrique « FAUSSES aux retournements »
# ---------------------------------------------------------------------------
# OBSERVABILITÉ PURE, mode shadow : DISTINCTE du win rate, AUCUN impact sur le
# scoring, les conclusions ou un quelconque kill-criterion. WIN RATE ONLY (zéro
# argent/PnL — on compte des conclusions, pas des gains).
#
# But : comparer AVANT/APRÈS momentum v3 le taux de conclusions FAUSSES sur les
# seules cellules « en situation de retournement » — là où le bug cacao se joue
# (le système restait LONG pendant que les news SHORT avaient raison). Le
# momentum v3 (variation 20j) + le cap aveugle au momentum (A2) sont censés
# RÉDUIRE ce taux. Forward-test : premier signal v3 = bulletin 11/06 7h,
# fenêtre J+60 = 2026-08-08 (cf. SELECTION-RULE addendum cutover).
#
# Une cellule est « en situation de retournement » si, dans son record
# decision-log d'émission :
#   (R1) le cap anti-inversion s'est DÉCLENCHÉ (`news_cap_applied == True`) —
#        les news poussaient assez fort dans le sens OPPOSÉ au quant pour être
#        plafonnées ; OU
#   (R2) le signe des news est OPPOSÉ au signe du quant HORS momentum
#        (`cap_quant_ex_momentum`) — désaccord news/quant directionnel, que le
#        cap ait mordu ou non. On utilise le quant EX-momentum (base du cap A2)
#        pour rester cohérent : c'est le désaccord news vs reste-du-quant qui
#        signe le retournement, pas la voix du momentum lui-même.
# Zéro invention : champ absent/illisible → cellule NON taguée (ni retournement
# ni non-retournement) et exclue de la métrique.

def is_reversal_context(record: dict) -> Optional[bool]:
    """Retourne True/False si la cellule est « en situation de retournement », ou
    None si le record ne permet pas de trancher (champs absents → zéro invention).

    R1 OU R2 (cf. bloc ci-dessus). News vs quant-ex-momentum.
    """
    if not isinstance(record, dict):
        return None
    cap_applied = record.get("news_cap_applied")
    news_total = record.get("news_total")
    quant_ex_mom = record.get("cap_quant_ex_momentum")
    # R1 : le cap a mordu → retournement avéré (news opposées assez fortes).
    if cap_applied is True:
        return True
    # R2 : désaccord directionnel news vs quant-ex-momentum.
    if isinstance(news_total, (int, float)) and isinstance(quant_ex_mom, (int, float)):
        if news_total > 0 > quant_ex_mom or news_total < 0 < quant_ex_mom:
            return True
        # Signes connus et concordants (ou l'un nul) → pas de retournement.
        return False
    # Ni R1 ni données R2 exploitables → indéterminé (exclu de la métrique).
    if cap_applied is False:
        return False
    return None


def load_reversal_context_map(
    bulletin_date: date,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> Dict[Tuple[str, str], bool]:
    """Mappe (actif, horizon) -> est-en-situation-de-retournement (A5, shadow).

    Lit les decision-log du jour (dernier record par cellule, comme conviction /
    news-driven). Dict vide si rien. Les cellules indéterminées (is_reversal_context
    renvoie None) sont ABSENTES du dict (zéro invention).
    """
    result: Dict[Tuple[str, str], bool] = {}
    if not decision_log_dir.exists():
        return result
    prefix = bulletin_date.isoformat()
    files = sorted(decision_log_dir.glob(f"{prefix}-*.jsonl"))
    for fp in files:
        try:
            with fp.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(rec, dict):
                        continue
                    if rec.get("bulletin_date") != prefix:
                        continue
                    actif = rec.get("actif")
                    horizon = rec.get("horizon")
                    if not actif or not horizon:
                        continue
                    rev = is_reversal_context(rec)
                    if rev is None:
                        # Indéterminé : on n'écrase PAS un éventuel tag déjà posé
                        # par un run antérieur du jour, et on n'invente rien.
                        continue
                    result[(str(actif), str(horizon))] = rev
        except OSError as e:
            logger.warning("decision-log illisible %s : %s", fp, e)
            continue
    return result


@dataclass
class FaussesAuxRetournements:
    """Agrégat shadow A5 — comptage des conclusions sur cellules en retournement.

    WIN RATE ONLY. n_retournement = cellules conclusives (VRAI/FAUSSE) en
    situation de retournement ; n_fausse_retournement = celles FAUSSES.
    """
    n_retournement: int = 0
    n_fausse_retournement: int = 0

    @property
    def taux_fausses(self) -> Optional[float]:
        """% de FAUSSES parmi les cellules conclusives en retournement (None si N=0)."""
        if self.n_retournement <= 0:
            return None
        return round(self.n_fausse_retournement / self.n_retournement * 100.0, 1)


def fausses_aux_retournements(
    measures: List[Any],
    reversal_map: Dict[Tuple[str, str], bool],
) -> FaussesAuxRetournements:
    """Compte les conclusions FAUSSES sur les cellules en situation de retournement.

    Ne compte QUE les cellules conclusives (VRAI/FAUSSE) ET taguées retournement
    (présentes dans reversal_map avec valeur True). Zéro invention : une cellule
    absente du map (indéterminée) n'entre PAS dans la métrique.
    """
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415

    agg = FaussesAuxRetournements()
    for m in measures:
        if m.outcome not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        key = (m.cell.actif_name, m.horizon)
        if reversal_map.get(key) is not True:
            continue
        agg.n_retournement += 1
        if m.outcome == OUTCOME_FAUSSE:
            agg.n_fausse_retournement += 1
    return agg


# ---------------------------------------------------------------------------
# Win rate par conviction (CA-W6) — sur une liste de mesures
# ---------------------------------------------------------------------------

@dataclass
class WinRateConviction:
    n_forte: int = 0
    n_vrai_forte: int = 0
    n_faible: int = 0
    n_vrai_faible: int = 0

    @property
    def taux_forte(self) -> Optional[float]:
        return round(self.n_vrai_forte / self.n_forte * 100.0, 1) if self.n_forte else None

    @property
    def taux_faible(self) -> Optional[float]:
        return round(self.n_vrai_faible / self.n_faible * 100.0, 1) if self.n_faible else None


def win_rate_par_conviction(
    measures: List[Any],
    conviction_map: Dict[Tuple[str, str], str],
) -> WinRateConviction:
    """Win rate segmenté forte vs faible (CA-W6 / §4.7).

    `measures` : objets ayant .outcome, .cell.actif_name, .horizon (Measure du
    Journaliste). On ne compte que VRAI/FAUSSE (non-conclusives exclues, même
    formule que le win rate global). Une cellule sans conviction connue est
    classée « faible » (zéro invention de conviction forte).
    """
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415

    wr = WinRateConviction()
    for m in measures:
        if m.outcome not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        key = (m.cell.actif_name, m.horizon)
        niveau = conviction_map.get(key, "faible")
        vrai = 1 if m.outcome == OUTCOME_VRAI else 0
        if niveau == "forte":
            wr.n_forte += 1
            wr.n_vrai_forte += vrai
        else:
            wr.n_faible += 1
            wr.n_vrai_faible += vrai
    return wr


# ---------------------------------------------------------------------------
# Construction du bilan du jour
# ---------------------------------------------------------------------------

@dataclass
class BilanJour:
    date_j: date
    now: datetime
    measures_24h: List[Any] = field(default_factory=list)   # Measures du bulletin 7h, horizon 24h
    n_vrai: int = 0
    n_fausse: int = 0
    n_nc: int = 0
    win_rate_jour: Optional[float] = None
    # WR tradable du jour = VRAI / (VRAI + FAUSSE + non-conclusif). Inclut les
    # calls sous seuil (en réel, Thomas serait quand même en position ce jour-là).
    # Métrique SECONDAIRE — coexiste avec le win rate conclusif (≤ celui-ci).
    wr_tradable_jour: Optional[float] = None
    conviction: WinRateConviction = field(default_factory=WinRateConviction)
    # Étage 1c (décision fondateur 12/06) — WR de la « Sélection du jour ».
    # La sélection devient un objet mesuré, à côté du WR global.
    selection: WinRateSelection = field(default_factory=WinRateSelection)
    # A5 (audit momentum-family 10/06) — métrique shadow « FAUSSES aux
    # retournements ». OBSERVABILITÉ PURE : n'altère NI le win rate, NI les
    # conclusions, NI aucun kill-criterion. WIN RATE ONLY.
    fausses_retournement: FaussesAuxRetournements = field(
        default_factory=FaussesAuxRetournements
    )
    # CA-B2 : tickers EU dont la clôture est un fallback approx (spot 22h faute
    # de close officiel 17h30 — Q5 non validé). Sert au marqueur `[close approx]`.
    close_approx_tickers: set = field(default_factory=set)
    markdown: str = ""


def _fmt_pct(v: Optional[float]) -> str:
    return f"{v:+.2f}%" if isinstance(v, (int, float)) else "—"


def _fmt_price(v: Optional[float]) -> str:
    return f"{v:.4g}" if isinstance(v, (int, float)) else "—"


def _eu_official_close(
    ticker: str,
    date_j: date,
    fetch_series: Optional[Any],
) -> Optional[float]:
    """Close officiel 17h30 (Euronext) pour un ticker EU le jour `date_j` (CA-B2).

    Stratégie robuste, zéro invention :
    - On lit la série journalière (`interval="1day"`) du ticker : la bougie du
      jour `date_j` a pour `close` le close OFFICIEL de fin de séance Euronext
      (17h30). C'est la seule source fiable d'un close officiel intraday-libre.
    - Si la série est absente, ou ne contient pas de bougie datée `date_j` (Q5
      non validé : Twelve peut ne pas exposer le close 17h30 le soir même pour
      FCHI/ETF), on retourne None → l'appelant retombe sur le spot 22h marqué
      `[close approx]`.

    `fetch_series(ticker)` doit renvoyer une liste de tuples (datetime, close)
    triée oldest→newest, ou None. Injecté (Twelve Data en prod, mock en test).
    Ne lève jamais : toute erreur → None (fallback marqué, jamais d'invention).
    """
    if fetch_series is None:
        return None
    try:
        series = fetch_series(ticker)
    except Exception as e:  # noqa: BLE001
        logger.warning("CA-B2 close EU %s : série indisponible (%s) — fallback spot", ticker, e)
        return None
    if not series:
        return None
    # Cherche la bougie journalière datée du jour J (close officiel 17h30).
    for ts, close in reversed(series):
        try:
            d = ts.date() if hasattr(ts, "date") else None
        except Exception:  # noqa: BLE001
            continue
        if d == date_j:
            try:
                return float(close)
            except (TypeError, ValueError):
                return None
    # Pas de bougie datée J → on n'invente pas (Q5 : close 17h30 pas encore
    # publié par Twelve le soir même). Fallback spot marqué côté appelant.
    return None


def _wrap_fetch_eu_close(
    fetch_price: Optional[Any],
    fetch_series: Optional[Any],
    eu_tickers: set,
    date_j: date,
    approx_tickers: set,
) -> Any:
    """Enveloppe `fetch_price` pour substituer le close officiel 17h30 des EU (CA-B2).

    Pour un ticker EU (CAC) : tente le close officiel 17h30 via la série
    journalière ; si indisponible → spot habituel + ajoute le ticker à
    `approx_tickers` (pour le marqueur `[close approx]` dans le rendu).
    Pour tout autre ticker : comportement inchangé (spot 22h).

    `approx_tickers` est muté in-place (effet de bord assumé, set de sortie).
    Zéro modification silencieuse : la substitution est tracée par le marqueur.
    """
    def _fetch(ticker: str):
        if ticker in eu_tickers:
            close = _eu_official_close(ticker, date_j, fetch_series)
            if close is not None:
                return close
            # Fallback Q5 : close 17h30 indisponible → spot 22h, marqué approx.
            approx_tickers.add(ticker)
            logger.info(
                "CA-B2 %s : close officiel 17h30 indisponible (Q5) — spot 22h marqué %s",
                ticker, CLOSE_APPROX_MARKER,
            )
        if fetch_price is None:
            return None
        return fetch_price(ticker)

    return _fetch


def _eu_tickers_from_fiches(fiches: Dict[str, dict]) -> set:
    """Tickers des actifs du groupe de marché EU (clôture 17h30) — CA-B2.

    Réutilise `actif_group` de mesure_ouverture (source unique des heures de
    marché, CAC = eu via override nom). Zéro heure codée en dur ici.
    """
    from mesure_ouverture import actif_group, load_suivi_config  # noqa: PLC0415

    config = load_suivi_config()
    out: set = set()
    for fiche in fiches.values():
        ticker = fiche.get("ticker_principal")
        if not ticker:
            continue
        if actif_group(fiche, config) == "eu":
            out.add(ticker)
    return out


def build_bilan_jour(
    now: Optional[datetime] = None,
    date_j: Optional[date] = None,
    bulletins_dir: Path = BULLETINS_DIR,
    decision_log_dir: Path = DECISION_LOG_DIR,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    fetch_series: Optional[Any] = None,
    prix_ouverture_dir: Optional[Path] = None,
    prix_emission_dir: Optional[Path] = None,
) -> BilanJour:
    """Construit le bilan du jour (R4) : note les calls 24h du Briefing 7h.

    Référence = prix d'ouverture du jour (fallback émission), clôture = prix
    courant à `now` (≈ 22h15 Paris). Mesure via le Journaliste existant (filtre
    7h actif). Calcule win rate du jour + win rate par conviction. Génère le
    markdown R4. Best-effort : aucune invention de prix/news/catalyseur.

    `now` (Europe/Paris) est PARAMÉTRABLE : l'infra l'ancre à 22h15 Paris réel.
    """
    import journaliste as J  # noqa: PLC0415
    from mesure_ouverture import PRIX_OUVERTURE_DIR  # noqa: PLC0415

    now = now or datetime.now(PARIS_TZ)
    if now.tzinfo is None:
        now = now.replace(tzinfo=PARIS_TZ)
    else:
        now = now.astimezone(PARIS_TZ)
    date_j = date_j or now.date()
    if prix_ouverture_dir is None:
        prix_ouverture_dir = PRIX_OUVERTURE_DIR
    if prix_emission_dir is None:
        prix_emission_dir = J.PRIX_EMISSION_DIR
    fiches = fiches if fiches is not None else J.load_fiches()

    bilan = BilanJour(date_j=date_j, now=now)

    # CA-B2 — Clôture officielle 17h30 pour les actifs EU (CAC).
    # On résout les fetchers par défaut (Twelve Data) ici pour pouvoir
    # ENVELOPPER `fetch_price` : les tickers EU prennent le close officiel 17h30
    # (bougie 1day du jour), fallback spot 22h marqué `[close approx]` (Q5 non
    # validé en shadow — comportement Twelve à 18h pour FCHI/ETF à confirmer en live).
    if fetch_price is None or fetch_series is None:
        try:
            import criteres_calculator as CC  # noqa: PLC0415
            if fetch_price is None:
                fetch_price = CC.fetch_twelve_price
            if fetch_series is None:
                fetch_series = CC.fetch_twelve_series
        except Exception as e:  # noqa: BLE001 — pas de réseau/clé : fallback spot marqué
            logger.warning("CA-B2 : fetchers Twelve indisponibles (%s) — close EU approx", e)

    eu_tickers = _eu_tickers_from_fiches(fiches)
    approx_tickers: set = set()
    wrapped_fetch = _wrap_fetch_eu_close(
        fetch_price, fetch_series, eu_tickers, date_j, approx_tickers,
    )

    # Mesure : on appelle le Journaliste avec today = date_j de sorte que les
    # cellules 24h du jour soient échues (échéance 24h = prochain jour ouvré >
    # date_j ; pour clôturer le 24h LE SOIR MÊME on force l'échéance à aujourd'hui
    # via today = échéance). On utilise donc today = compute_echeance(date_j, "24h").
    today_for_24h = J.compute_echeance(date_j, "24h")
    measures, _ = J.measure(
        today=today_for_24h,
        bulletins_dir=bulletins_dir,
        prix_emission_dir=prix_emission_dir,
        fiches=fiches,
        fetch_price=wrapped_fetch,
        prix_ouverture_dir=prix_ouverture_dir,
        only_seven_am=True,
    )
    # Ne garder que les cellules 24h émises le jour J (bulletin 7h du jour).
    measures_24h = [
        m for m in measures
        if m.horizon == "24h" and m.cell.bulletin_date == date_j
    ]
    bilan.measures_24h = measures_24h

    for m in measures_24h:
        if m.outcome == J.OUTCOME_VRAI:
            bilan.n_vrai += 1
        elif m.outcome == J.OUTCOME_FAUSSE:
            bilan.n_fausse += 1
        elif m.outcome == J.OUTCOME_NC:
            bilan.n_nc += 1
    denom = bilan.n_vrai + bilan.n_fausse
    if denom > 0:
        bilan.win_rate_jour = round(bilan.n_vrai / denom * 100.0, 1)
    # WR tradable : dénominateur élargi aux non-conclusifs (statuts non-notee /
    # suivi-interrompu déjà exclus car non comptés dans n_vrai/n_fausse/n_nc).
    denom_trad = bilan.n_vrai + bilan.n_fausse + bilan.n_nc
    if denom_trad > 0:
        bilan.wr_tradable_jour = round(bilan.n_vrai / denom_trad * 100.0, 1)

    # Win rate par conviction (CA-W6).
    conv_map = load_conviction_map(date_j, decision_log_dir)
    bilan.conviction = win_rate_par_conviction(measures_24h, conv_map)

    # Étage 1c — WR de la « Sélection du jour » (objet mesuré dédié). Source : le
    # champ shadow `selection_du_jour` du decision-log du jour. Dégradation propre
    # si absent (anciens logs → sélection vide).
    selection_map = load_selection_map(date_j, decision_log_dir)
    bilan.selection = win_rate_selection(measures_24h, selection_map)

    # A5 — métrique shadow « FAUSSES aux retournements » (observabilité pure,
    # zéro impact scoring/conclusions). Même source que la conviction : le
    # decision-log d'émission du jour.
    reversal_map = load_reversal_context_map(date_j, decision_log_dir)
    bilan.fausses_retournement = fausses_aux_retournements(measures_24h, reversal_map)

    bilan.close_approx_tickers = approx_tickers
    bilan.markdown = _render_markdown(bilan, fiches)
    return bilan


def _render_markdown(bilan: BilanJour, fiches: Dict[str, dict]) -> str:
    """Markdown R4 (spec §3.4). WIN RATE ONLY — aucun montant."""
    from journaliste import (  # noqa: PLC0415
        OUTCOME_VRAI, OUTCOME_FAUSSE, OUTCOME_NC,
    )

    L: List[str] = []
    L.append(f"## Bilan du jour — {bilan.date_j.isoformat()}")
    L.append("")
    L.append(f"_Généré : {bilan.now.isoformat()} (Europe/Paris)._")
    L.append("")
    L.append("### Résultat des calls 7h")
    L.append("")
    L.append("| Actif | Call 7h | Ouverture | Clôture | Delta% | Résultat | Amplitude flag |")
    L.append("|---|---|---|---|---|---|---|")

    res_label = {
        OUTCOME_VRAI: "✅ VRAI",
        OUTCOME_FAUSSE: "❌ FAUSSE",
        OUTCOME_NC: "⚪ NC",
    }
    faux_gros: List[Tuple[str, float]] = []  # (ligne, |delta|) — tri par amplitude
    for m in sorted(bilan.measures_24h, key=lambda x: x.cell.actif_name):
        delta = m.delta_pct
        seuil = m.seuil_pct
        flag = "—"
        if (
            m.outcome == OUTCOME_FAUSSE
            and isinstance(delta, (int, float))
            and isinstance(seuil, (int, float))
            and abs(delta) >= GROS_MOVE_FACTOR * seuil
        ):
            flag = "⚡ gros move"
            faux_gros.append((m.cell.actif_name, abs(delta)))
        # CA-B2 : marqueur [close approx] si la clôture EU est un fallback spot
        # (close officiel 17h30 indisponible — Q5).
        cloture_cell = _fmt_price(m.prix_courant)
        if getattr(m, "ticker", None) in bilan.close_approx_tickers:
            cloture_cell = f"{cloture_cell} {CLOSE_APPROX_MARKER}"
        L.append(
            f"| {m.cell.actif_name} | {m.cell.conclusion} | "
            f"{_fmt_price(m.prix_emission)} | {cloture_cell} | "
            f"{_fmt_pct(delta)} | {res_label.get(m.outcome, m.outcome)} | {flag} |"
        )
    if not bilan.measures_24h:
        L.append("| _aucune cellule 24h mesurable du Briefing 7h_ | | | | | | |")
    L.append("")
    # CA-B2 — note Q5 : si une clôture EU est approximée (spot 22h faute de
    # close officiel 17h30), on le signale explicitement (zéro invention).
    if bilan.close_approx_tickers:
        L.append(
            f"> {CLOSE_APPROX_MARKER} : clôture EU = dernier prix disponible "
            f"(spot ~22h), faute de close officiel 17h30 récupérable. "
            f"À valider en live (Q5 : comportement Twelve Data pour FCHI/ETF)."
        )
        L.append("")

    # Win rate du jour
    L.append("### Win rate du jour")
    denom = bilan.n_vrai + bilan.n_fausse
    L.append(
        f"- Paris conclusifs : {denom} / {denom + bilan.n_nc} "
        f"({bilan.n_nc} non-conclusifs sous seuil)"
    )
    if bilan.win_rate_jour is not None:
        L.append(
            f"- Win rate du jour : **{bilan.n_vrai}/{denom} = {bilan.win_rate_jour:.0f}%**"
        )
    else:
        L.append("- Win rate du jour : — (aucun call conclusif aujourd'hui)")
    # WR tradable (secondaire) : inclut les non-conclusifs au dénominateur.
    denom_trad = bilan.n_vrai + bilan.n_fausse + bilan.n_nc
    if bilan.wr_tradable_jour is not None:
        L.append(
            f"- WR tradable du jour : **{bilan.n_vrai}/{denom_trad} = "
            f"{bilan.wr_tradable_jour:.0f}%** (VRAI / VRAI+FAUSSE+non-conclusif)"
        )
    else:
        L.append("- WR tradable du jour : — (aucun pari tradable aujourd'hui)")
    # WR Sélection du jour (Étage 1c) — les paris du bloc « 🎯 Sélection du jour
    # — max 3 », mesurés comme objet dédié (VRAI/FAUSSE, NC exclus comme le WR
    # global). « — » si aucune cellule sélectionnée n'est conclusive aujourd'hui.
    s = bilan.selection
    if s.taux is not None:
        L.append(
            f"- WR Sélection du jour : **{s.n_vrai_select}/{s.n_select} = "
            f"{s.taux:.0f}%** (paris du bloc « 🎯 Sélection du jour — max 3 »)"
        )
    else:
        L.append(
            "- WR Sélection du jour : — (aucun pari sélectionné conclusif aujourd'hui)"
        )
    # Win rate par conviction (CA-W6)
    c = bilan.conviction
    tf = f"{c.taux_forte:.0f}%" if c.taux_forte is not None else "— (N insuffisant)"
    tw = f"{c.taux_faible:.0f}%" if c.taux_faible is not None else "— (N insuffisant)"
    L.append(f"- Win rate conviction forte (jour) : {tf} (N={c.n_forte})")
    L.append(f"- Win rate conviction faible (jour) : {tw} (N={c.n_faible})")
    L.append("- Win rate cumulé : voir performance.md")
    L.append("")
    # A5 (audit momentum-family 10/06) — métrique shadow « FAUSSES aux
    # retournements ». DISTINCTE du win rate ; sert UNIQUEMENT à comparer
    # avant/après momentum v3 le taux d'erreurs aux points de retournement
    # (forward-test J+60 = 2026-08-08). N'entre dans AUCUNE décision.
    fr = bilan.fausses_retournement
    L.append("### FAUSSES aux retournements (shadow A5)")
    L.append(
        "_Cellules conclusives en situation de retournement (cap anti-inversion "
        "déclenché OU news opposées au quant hors-momentum). Métrique "
        "d'observabilité momentum v3 — DISTINCTE du win rate, sans impact "
        "décisionnel. WIN RATE ONLY._"
    )
    if fr.taux_fausses is not None:
        L.append(
            f"- FAUSSES aux retournements (jour) : "
            f"**{fr.n_fausse_retournement}/{fr.n_retournement} = "
            f"{fr.taux_fausses:.0f}%** (N={fr.n_retournement} cellules en retournement)"
        )
    else:
        L.append(
            "- FAUSSES aux retournements (jour) : — "
            "(aucune cellule conclusive en situation de retournement aujourd'hui)"
        )
    L.append("")

    # FAUX à forte amplitude (erreurs prioritaires) — tri par amplitude % desc.
    L.append("### FAUX à forte amplitude (erreurs prioritaires)")
    if faux_gros:
        for actif, amp in sorted(faux_gros, key=lambda x: x[1], reverse=True):
            L.append(
                f"- ⚡ {actif} : call faux, le marché a bougé {amp:.2f}% "
                f"dans le sens opposé. → À analyser dans le bilan semaine."
            )
    else:
        L.append("Pas de call faux à forte amplitude aujourd'hui.")
    L.append("")

    # News qui ont compté (Option C — croisement) : best-effort.
    L.append("### News qui ont compté aujourd'hui")
    news_lines = _news_qui_ont_compte(bilan)
    if news_lines:
        L.extend(news_lines)
    else:
        L.append("Pas de news déterminante croisée avec un call conclusif aujourd'hui.")
    L.append("")

    # Catalyseurs J+1 (calendrier économique statique — zéro API, zéro invention).
    L.append("### Catalyseurs J+1")
    L.extend(_catalyseurs_j1(bilan.now))
    L.append("")
    return "\n".join(L)


# Libellés courts par type de catalyseur (langage trader).
_CATALYSEUR_TYPE_LABEL = {
    "FOMC": "Fed", "CPI": "Inflation US", "NFP": "Emploi US", "BCE": "BCE",
    "OPEC": "OPEC+", "WASDE": "USDA", "EIA": "Stocks pétrole", "COT": "Positionnement",
}


def _catalyseurs_j1(now: Optional[datetime]) -> List[str]:
    """Section « Catalyseurs J+1 » alimentée par le calendrier éco statique.

    Horizon J+1, étendu à J+2 si J+1 tombe un week-end (agenda éco creux).
    Entrées `precision: regle` préfixées « ~ » (honnêteté : date approximative).
    Fallback propre si le YAML est absent (calendrier_eco renvoie une liste vide).
    """
    now = now or datetime.now(PARIS_TZ)
    if now.tzinfo is None:
        now = now.replace(tzinfo=PARIS_TZ)
    demain = now.astimezone(PARIS_TZ).date() + timedelta(days=1)
    # J+1 week-end (samedi/dimanche) → on regarde jusqu'à J+2 pour ne pas afficher
    # un vide trompeur le vendredi soir.
    horizon = 3 if demain.weekday() >= 5 else 1

    try:
        from calendrier_eco import evenements_a_venir  # noqa: PLC0415
        evts = evenements_a_venir(now, horizon_jours=horizon)
    except Exception as e:  # noqa: BLE001
        logger.warning("calendrier éco indisponible : %s — fallback", e)
        evts = []

    if not evts:
        return [
            "Aucun catalyseur majeur connu dans les prochains jours "
            "(calendrier éco statique — zéro invention)."
        ]

    lignes: List[str] = []
    for ev in evts:
        prefixe = "~ " if ev.get("precision") == "regle" else ""
        type_label = _CATALYSEUR_TYPE_LABEL.get(ev.get("type", ""), ev.get("type", ""))
        impact_mark = "🔴" if ev.get("impact") == "high" else "🟡"
        actifs = ", ".join(ev.get("actifs") or []) or "marché large"
        lignes.append(
            f"- {prefixe}**{ev['date']}** {impact_mark} {ev['nom']} "
            f"({type_label}) — actifs : {actifs}"
        )
    lignes.append(
        "> « ~ » = date approximative (règle de récurrence, pas une date "
        "officielle confirmée). 🔴 impact fort · 🟡 impact moyen."
    )
    return lignes


def _news_qui_ont_compte(bilan: BilanJour) -> List[str]:
    """Option C (Q6) : croise les news ingérées (tag news_driven sur la mesure)
    avec les actifs VRAI/FAUSSE du jour. Zéro appel DeepSeek, zéro invention.

    Le tag `news_driven` + `news_rationale` est posé par le Journaliste depuis
    le decision-log du jour. On n'affiche que les cellules conclusives ET
    news-driven (rationale non vide).
    """
    from journaliste import OUTCOME_VRAI, OUTCOME_FAUSSE  # noqa: PLC0415

    out: List[str] = []
    seen: set = set()
    for m in bilan.measures_24h:
        if m.outcome not in (OUTCOME_VRAI, OUTCOME_FAUSSE):
            continue
        if not getattr(m, "news_driven", None):
            continue
        rationale = getattr(m, "news_rationale", None)
        if not rationale:
            continue
        if m.cell.actif_name in seen:
            continue
        seen.add(m.cell.actif_name)
        verdict = "call confirmé" if m.outcome == OUTCOME_VRAI else "call infirmé"
        out.append(f"- **{m.cell.actif_name}** : {rationale} → {verdict}.")
    return out


def write_bilan_jour(bilan: BilanJour, base_dir: Path = BILAN_JOUR_DIR) -> Path:
    """Écrit le bilan du jour dans v3/data/bilan-jour/{date}.md."""
    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = base_dir / f"{bilan.date_j.isoformat()}.md"
    out_path.write_text(bilan.markdown + "\n", encoding="utf-8")
    logger.info("Bilan du jour écrit : %s", out_path)
    return out_path


__all__ = [
    "BilanJour",
    "WinRateConviction",
    "conviction_level",
    "load_conviction_map",
    "win_rate_par_conviction",
    "build_bilan_jour",
    "write_bilan_jour",
    "GROS_MOVE_FACTOR",
    "CLOSE_APPROX_MARKER",
]
