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
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

# [Point #5] Horodatage FR lisible de la ligne « Généré : … ».
try:
    from datetime_fr import horodatage_fr
except ImportError:  # pragma: no cover - chemin d'import alternatif
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from datetime_fr import horodatage_fr

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


def load_conviction_records(
    bulletin_date: date,
    decision_log_dir: Path = DECISION_LOG_DIR,
) -> Dict[Tuple[str, str], dict]:
    """Mappe (actif, horizon) -> DERNIER record brut du decision-log du jour.

    Comme `load_conviction_map` mais garde le record COMPLET (pas juste le niveau)
    pour que le Bilan déduise la raison de non-sélection (selection_motif_exclusion,
    coverage, drapeaux). Dernier record par cellule. {} si rien (zéro invention).
    """
    result: Dict[Tuple[str, str], dict] = {}
    if not decision_log_dir.exists():
        return result
    prefix = bulletin_date.isoformat()
    for fp in sorted(decision_log_dir.glob(f"{prefix}-*.jsonl")):
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
                    result[(str(actif), str(horizon))] = rec
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
# Refonte bilan soir S9 — 3 blocs « suivi 24h » (demande fondateur, design validé)
# ---------------------------------------------------------------------------
# WIN RATE ONLY : aucune valeur monétaire. Le % de mouvement (ampleur) est OK
# (Thomas l'a demandé). Tout est DÉTERMINISTE et ZÉRO INVENTION : un point de
# relevé absent (12h/18h non persisté) → « — » et le pic est calculé sur les
# seuls points disponibles, le trou est signalé.
#
# Le mouvement directionnel signé FAVORABLE (`+` = va dans le sens du call) est
# calculé par la fonction de vérité unique `run_suivi.fav_delta` (réutilisée :
# zéro divergence entre suivi et bilan).

# Libellés des points de relevé (heure Paris), ordonnés chronologiquement.
PIC_POINTS = ("12h", "18h", "clôture")

# Heure Paris (entier) associée à chaque label de point de relevé, pour borner la
# recherche d'un catalyseur news APRÈS le pic. « clôture » ≈ 22h (fin du 24h).
_PIC_HEURE_PARIS = {"12h": 12, "18h": 18, "clôture": 22}


# ---------------------------------------------------------------------------
# Brief B — le « POURQUOI » : cause TRAÇABLE d'un mouvement (zéro invention)
# ---------------------------------------------------------------------------
# La cause d'un repli (ou d'un gros move) n'est citée QUE si elle est tracée dans
# l'events-log : une news à FORTE matérialité (high) sur CET actif, horodatée
# (ingestion) APRÈS l'heure de référence (le pic). Réutilise le parser ROBUSTE de
# `briefing` (index de colonne nommée + horodatage de batch). Aucune news high
# tracée → AUCUNE cause inventée (l'appelant écrit « cause non identifiée »).


def _events_high_actif_apres(
    actif_label: str,
    date_j: date,
    apres_heure_paris: Optional[int],
    events_path: Optional[Path] = None,
) -> List[dict]:
    """Events high sur `actif_label`, ingérés le jour J (et après `apres_heure_paris`).

    Lecture seule de l'events-log (parser briefing, horodatage de batch). Filtre :
    - matérialité == high ;
    - actif principal de l'event == actif_label (mapping IA, cf. briefing) ;
    - ingéré le jour `date_j` ; si `apres_heure_paris` fourni, ingéré APRÈS cette
      heure (Paris). Un event sans horodatage d'ingestion lisible est EXCLU (zéro
      invention). Tri par fraîcheur (ingest_ts desc). Best-effort : erreur → [].
    """
    try:
        import briefing as B  # noqa: PLC0415
        path = events_path or B.EVENTS_LOG
        events = B.parse_events_with_ingest_ts(path)
    except Exception as e:  # noqa: BLE001
        logger.warning("cause news high : parsing events-log KO (%s)", e)
        return []

    cutoff = None
    if apres_heure_paris is not None:
        cutoff = datetime.combine(
            date_j, datetime.min.time().replace(hour=apres_heure_paris),
            tzinfo=PARIS_TZ,
        ).astimezone(ZoneInfo("UTC"))

    out: List[dict] = []
    for ev in events:
        if (ev.get("materiality", "") or "").lower() != "high":
            continue
        ts = ev.get("ingest_ts")
        if not isinstance(ts, datetime):
            continue  # horodatage absent → exclu (zéro invention)
        ts_utc = ts.astimezone(ZoneInfo("UTC"))
        if ts_utc.date() != date_j:
            continue
        if cutoff is not None and ts_utc < cutoff:
            continue
        try:
            if B._primary_actif_from_event(ev) != actif_label:
                continue
        except Exception:  # noqa: BLE001
            continue
        out.append(ev)
    out.sort(key=lambda e: e["ingest_ts"], reverse=True)
    return out


def _resume_news(ev: dict, max_len: int = 140) -> str:
    """Résumé court d'une news (trigger tronqué). Vide si pas de trigger.

    WIN RATE ONLY : nettoyage monétaire (symboles $€£, termes gain/perte/rendement/
    p&l) via `briefing.strip_monetaire` — on ne cite jamais une valeur monétaire,
    même issue d'un titre de news externe.
    """
    import briefing as B  # noqa: PLC0415
    trigger = B.strip_monetaire((ev.get("trigger", "") or "").strip())
    if not trigger:
        return ""
    if len(trigger) > max_len:
        trigger = trigger[: max_len - 3].rstrip() + "..."
    return trigger


def cause_news_high_apres(
    actif_label: str,
    date_j: date,
    apres_heure_paris: Optional[int],
    events_path: Optional[Path] = None,
) -> Optional[str]:
    """Résumé de la news high la plus fraîche sur `actif_label` APRÈS l'heure donnée.

    None si aucune news high tracée (zéro invention : l'appelant écrit alors
    « cause non identifiée »). Réutilisable pour le verdict de sortie (Bloc 1) et
    les gros moves hors Top 3 (Bloc 2).
    """
    evs = _events_high_actif_apres(actif_label, date_j, apres_heure_paris, events_path)
    for ev in evs:
        resume = _resume_news(ev)
        if resume:
            return resume
    return None


def _event_dir_pour_actif(ev: dict, actif_label: str) -> Optional[str]:
    """Direction IA (LONG/SHORT/NEUTRAL) que la news implique POUR `actif_label`,
    lue dans le champ `impacts` (ex. « GOLD:SHORT:high »). None si l'actif n'y figure
    pas. Sert à n'afficher qu'une news COHÉRENTE avec une direction donnée."""
    try:
        import briefing as B  # noqa: PLC0415
        for imp in B._parse_impacts_compact(ev.get("impacts", "") or ""):
            if B._IA_ASSET_TO_LABEL.get(imp["asset"]) == actif_label:
                return imp["direction"]
    except Exception:  # noqa: BLE001 — lecture best-effort
        return None
    return None


def cause_news_high_dir(
    actif_label: str,
    date_j: date,
    sens: str,
    apres_heure_paris: Optional[int] = None,
    events_path: Optional[Path] = None,
) -> Optional[str]:
    """News high la plus fraîche sur `actif_label` dont l'impact IA va dans le sens
    `sens` (LONG/SHORT). Garantit la COHÉRENCE direction news ↔ contexte d'affichage :
    - pro-call (sens = notre call) → « pourquoi on a pris/gagné ce pari » (sections 1 & 3) ;
    - contre-call (sens = inverse du call) → « ce qui nous a battus » (post-mortem section 4).
    None si aucune news cohérente (zéro invention : pas de titre à contre-sens affiché)."""
    sens = (sens or "").upper()
    if sens not in ("LONG", "SHORT"):
        return None
    for ev in _events_high_actif_apres(actif_label, date_j, apres_heure_paris, events_path):
        if _event_dir_pour_actif(ev, actif_label) == sens:
            resume = _resume_news(ev)
            if resume:
                return resume
    return None


def _fav(delta_pct: Optional[float], call: str) -> Optional[float]:
    """% directionnel signé favorable (réutilise run_suivi.fav_delta)."""
    try:
        from run_suivi import fav_delta  # noqa: PLC0415
    except ImportError:  # pragma: no cover - import alternatif
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run_suivi import fav_delta  # noqa: PLC0415
    return fav_delta(delta_pct, call)


@dataclass
class PerfTop3Ligne:
    """Performance 24h d'UNE cellule de la Sélection du jour (Bloc 1). WIN RATE ONLY."""
    actif: str
    call: str
    fav_12h: Optional[float]      # % favorable signé à 12h (None = pas de relevé)
    fav_18h: Optional[float]      # % favorable signé à 18h (None = pas de relevé)
    fav_cloture: Optional[float]  # % favorable signé à la clôture (None = pas mesurable)
    pic_valeur: Optional[float]   # meilleur % favorable parmi les points disponibles
    pic_heure: Optional[str]      # heure du pic ("12h"/"18h"/"clôture") ou None
    points_manquants: List[str]   # points de relevé absents (trou de données)
    verdict: str                  # verdict de sortie optimale, relié aux heures
    vendre_reco: Optional[str]    # reco réelle du suivi 18h ("Vendre"/"Pas vendre"/None)
    # Brief B — cause TRAÇABLE du repli après le pic (news high sur l'actif après
    # l'heure du pic) ou None si non identifiée (zéro invention). Renseigné SEULEMENT
    # quand le pic a reflué avant la clôture (sinon pas de repli à expliquer).
    cause_repli: Optional[str] = None


def _verdict_sortie(
    fav_12h: Optional[float],
    fav_18h: Optional[float],
    fav_cloture: Optional[float],
    pic_valeur: Optional[float],
    pic_heure: Optional[str],
) -> str:
    """Verdict de sortie optimale RELIÉ AUX HEURES (déterministe, zéro invention).

    Compare le pic (meilleur % favorable atteint) à la clôture :
    - pic à la clôture (monté jusqu'au bout) → « tenir était le bon choix » ;
    - pic AVANT la clôture et clôture plus basse → « sortir à {heure du pic}
      aurait été mieux » (avec les deux valeurs) ;
    - aucun point favorable (jamais dans notre sens) → constat honnête.
    Si données insuffisantes pour trancher → message explicite (pas d'invention).
    """
    if pic_valeur is None or pic_heure is None:
        return "Pas de point de relevé exploitable pour juger la sortie."
    # Le pari n'est jamais passé du bon côté : aucun verrouillage n'aurait aidé.
    if pic_valeur <= 0:
        return (
            f"jamais dans notre sens (meilleur point {_fmt_pct(pic_valeur)} "
            f"à {pic_heure}) : il n'y avait rien à verrouiller."
        )
    if pic_heure == "clôture":
        return (
            f"pic {_fmt_pct(pic_valeur)} à la clôture : monté jusqu'au bout, "
            f"tenir était le bon choix."
        )
    # Pic atteint AVANT la clôture : la clôture est-elle plus basse ?
    if isinstance(fav_cloture, (int, float)):
        if fav_cloture < pic_valeur:
            return (
                f"pic {_fmt_pct(pic_valeur)} à {pic_heure}, clôture "
                f"{_fmt_pct(fav_cloture)} : sortir à {pic_heure} aurait été mieux."
            )
        return (
            f"pic {_fmt_pct(pic_valeur)} à {pic_heure}, clôture stable : "
            f"tenir n'a rien coûté."
        )
    # Clôture non mesurable : on dit où était le pic, sans inventer la suite.
    return (
        f"pic {_fmt_pct(pic_valeur)} à {pic_heure} ; clôture non mesurable "
        f"(point manquant)."
    )


def compute_perf_top3(
    measures_24h: List[Any],
    selection_map: Dict[Tuple[str, str], bool],
    tracking: Dict[str, Dict[str, dict]],
    vendre_map: Optional[Dict[str, str]] = None,
    date_j: Optional[date] = None,
    events_path: Optional[Path] = None,
) -> List[PerfTop3Ligne]:
    """Bloc 1 — Performance 24h des cellules de la Sélection du jour (top ≤3).

    Pour chaque cellule `selection_du_jour: true` (horizon 24h) :
    - fav 12h / 18h : lus dans `tracking` (relevés persistés par run_suivi). Le
      call du tracking et celui du bulletin doivent concorder ; sinon le relevé
      est ignoré (zéro invention sur un call douteux).
    - fav clôture : calculé depuis la mesure (delta clôture vs ouverture × sens).
    - pic = max des points DISPONIBLES, avec son heure ; points manquants tracés.
    - verdict de sortie optimale relié aux heures (_verdict_sortie).
    - reco réelle du suivi 18h (vendre_map) pour confronter capté / raté.
    Tri : par actif (déterministe). Zéro point → ligne avec « — » partout.
    """
    vendre_map = vendre_map or {}
    out: List[PerfTop3Ligne] = []
    for m in measures_24h:
        actif = m.cell.actif_name
        if not selection_map.get((actif, m.horizon), False):
            continue
        call = m.cell.conclusion

        def _slot_fav(slot: str) -> Optional[float]:
            rec = (tracking.get(slot) or {}).get(actif)
            if not isinstance(rec, dict):
                return None
            # Concordance de call : un relevé d'un call opposé est ignoré.
            if str(rec.get("call", "")).upper() != str(call).upper():
                return None
            v = rec.get("fav_pct")
            return float(v) if isinstance(v, (int, float)) else None

        fav_12h = _slot_fav("12h")
        fav_18h = _slot_fav("18h")
        fav_cloture = _fav(m.delta_pct, call)

        points = [("12h", fav_12h), ("18h", fav_18h), ("clôture", fav_cloture)]
        dispo = [(h, v) for h, v in points if isinstance(v, (int, float))]
        manquants = [h for h, v in points if not isinstance(v, (int, float))]
        if dispo:
            pic_heure, pic_valeur = max(dispo, key=lambda kv: kv[1])
        else:
            pic_heure, pic_valeur = None, None

        verdict = _verdict_sortie(fav_12h, fav_18h, fav_cloture, pic_valeur, pic_heure)
        # Brief B — cause TRAÇABLE du repli : si le pic a reflué AVANT la clôture
        # (pic positif à 12h/18h, clôture plus basse), cherche une news high sur
        # CET actif ingérée APRÈS l'heure du pic. None si rien de tracé (l'appelant
        # écrira « cause non identifiée » — zéro invention).
        cause_repli = None
        a_reflue = (
            pic_heure in ("12h", "18h")
            and isinstance(pic_valeur, (int, float)) and pic_valeur > 0
            and isinstance(fav_cloture, (int, float)) and fav_cloture < pic_valeur
        )
        if a_reflue and date_j is not None:
            cause_repli = cause_news_high_apres(
                actif, date_j, _PIC_HEURE_PARIS.get(pic_heure), events_path
            )
        out.append(PerfTop3Ligne(
            actif=actif, call=call,
            fav_12h=(round(fav_12h, 2) if fav_12h is not None else None),
            fav_18h=(round(fav_18h, 2) if fav_18h is not None else None),
            fav_cloture=(round(fav_cloture, 2) if fav_cloture is not None else None),
            pic_valeur=(round(pic_valeur, 2) if pic_valeur is not None else None),
            pic_heure=pic_heure, points_manquants=manquants, verdict=verdict,
            vendre_reco=vendre_map.get(actif), cause_repli=cause_repli,
        ))
    out.sort(key=lambda x: x.actif)
    return out


@dataclass
class GrosMoveAutre:
    """Gros mouvement 24h sur un actif HORS top 3 (Bloc 2). WIN RATE ONLY."""
    actif: str
    call: str
    mouvement_pct: Optional[float]   # mouvement 24h vs ouverture (signé, brut)
    direction_juste: Optional[bool]  # le call 24h pointait-il le bon sens ?
    raison_non_select: str           # pourquoi pas dans le top 3 (déduit des logs)
    apprentissage: str               # 1 ligne actionnable
    # Brief B — POURQUOI le mouvement a eu lieu : news high sur l'actif ce jour
    # (résumé) ou None si non tracé (l'appelant écrit « cause non tracée »).
    cause_move: Optional[str] = None


def reason_non_selection(
    actif: str,
    record: Optional[dict],
    score_fort_seuil: float,
    selection_coverage_min: float,
) -> str:
    """Pourquoi `actif` n'est PAS dans la Sélection — DÉDUIT du decision-log.

    Priorité (zéro invention) :
    1. `selection_motif_exclusion` présent → raison EXACTE tracée par le sélecteur
       (« hors top 3 » / « même pari (X) que Y ») : on la rend telle quelle.
    2. Sinon, on déduit du même record : conviction non « forte » (drapeau actif
       ou |score| sous le seuil) → critère conviction ; couverture < plancher →
       critère couverture. Ce sont EXACTEMENT les étapes 1-2 de
       `compute_selection_du_jour` (source unique), donc pas une invention.
    3. Record absent / aucun critère déterminable → « raison non tracée ».
    """
    if not isinstance(record, dict):
        return "raison non tracée"
    motif = record.get("selection_motif_exclusion")
    if isinstance(motif, str) and motif.strip():
        return motif.strip()
    # Déduction des étapes 1-2 du sélecteur (mêmes règles que compute_selection).
    niveau = conviction_level(record, score_fort_seuil)
    cov = record.get("coverage")
    if niveau != "forte":
        # Quel drapeau / quel critère a dégradé la conviction ?
        if record.get("mono_critere_dominant"):
            return "conviction non forte (mono-critère dominant)"
        if record.get("diverge"):
            return "conviction non forte (signaux qui divergent)"
        if record.get("coin_flip"):
            return "conviction non forte (quasi pile ou face)"
        if record.get("quasi_neutre"):
            return "conviction non forte (signal quasi neutre)"
        return "conviction sous le seuil (pas assez tranchée)"
    if isinstance(cov, (int, float)) and cov < selection_coverage_min:
        return (
            f"couverture insuffisante ({cov * 100:.0f}% < "
            f"{selection_coverage_min * 100:.0f}% requis)"
        )
    # Conviction forte ET couverture OK mais non sélectionné, sans motif tracé :
    # on ne devine pas (le cas normal est couvert par selection_motif_exclusion).
    return "raison non tracée"


def _apprentissage_gros_move(direction_juste: Optional[bool], raison: str) -> str:
    """1 ligne d'apprentissage pour un gros move hors top 3 (déterministe)."""
    if direction_juste is True:
        if raison == "raison non tracée":
            return "bonne direction mais pas joué : critère de sélection à revoir."
        return f"bonne direction, écarté car {raison} : sélection peut-être trop prudente."
    if direction_juste is False:
        return "mauvaise direction : le call lui-même était à côté, à analyser."
    return "direction du call indéterminée (donnée manquante)."


def compute_gros_moves_autres(
    measures_24h: List[Any],
    selection_map: Dict[Tuple[str, str], bool],
    conviction_records: Dict[Tuple[str, str], dict],
    score_fort_seuil: float,
    selection_coverage_min: float = 0.70,
    gros_move_factor: float = GROS_MOVE_FACTOR,
    date_j: Optional[date] = None,
    events_path: Optional[Path] = None,
) -> List[GrosMoveAutre]:
    """Bloc 2 — Gros mouvements sur les AUTRES actifs (hors top 3).

    Parmi les cellules 24h NON sélectionnées dont |mouvement vs ouverture| ≥
    `gros_move_factor` × seuil_actif (réutilise le « gros move » existant) :
    direction du call juste ou non, raison de non-sélection (reason_non_selection),
    apprentissage. Triés du PLUS GROS mouvement au plus petit (le plus gros = le
    plus intéressant à jouer). Zéro invention.
    """
    out: List[GrosMoveAutre] = []
    for m in measures_24h:
        actif = m.cell.actif_name
        if selection_map.get((actif, m.horizon), False):
            continue  # dans le top 3 → traité au Bloc 1
        delta = m.delta_pct
        seuil = m.seuil_pct
        if not isinstance(delta, (int, float)) or not isinstance(seuil, (int, float)):
            continue
        if abs(delta) < gros_move_factor * seuil:
            continue  # pas un gros move
        call = m.cell.conclusion
        fav = _fav(delta, call)
        direction_juste = (fav > 0) if isinstance(fav, (int, float)) else None
        rec = conviction_records.get((actif, m.horizon))
        raison = reason_non_selection(actif, rec, score_fort_seuil, selection_coverage_min)
        # Brief B — POURQUOI le move : news high sur l'actif ce jour (toute heure),
        # ou None si rien de tracé (zéro invention → « cause non tracée » au rendu).
        cause_move = None
        if date_j is not None:
            cause_move = cause_news_high_apres(actif, date_j, None, events_path)
        out.append(GrosMoveAutre(
            actif=actif, call=call, mouvement_pct=round(delta, 2),
            direction_juste=direction_juste, raison_non_select=raison,
            apprentissage=_apprentissage_gros_move(direction_juste, raison),
            cause_move=cause_move,
        ))
    out.sort(key=lambda x: abs(x.mouvement_pct), reverse=True)
    return out


def compute_apprentissage_jour(
    perf_top3: List[PerfTop3Ligne],
    gros_moves: List[GrosMoveAutre],
) -> List[str]:
    """Bloc 3 — Apprentissage du jour : synthèse courte, actionnable, déterministe.

    Basée UNIQUEMENT sur les blocs 1-2 (zéro nouveau calcul, zéro blabla) :
    - sorties optimales ratées (pic avant la clôture) sur la Sélection ;
    - gros moves bonne direction mais pas joués (sélection trop prudente) ;
    - gros moves mauvaise direction (le call était à côté) ;
    - trous de données intraday (12h/18h non relevés) signalés honnêtement.
    Liste vide → 1 ligne neutre (rien de notable).
    """
    lignes: List[str] = []
    # Sorties ratées (pic strictement avant la clôture, avec gain positif).
    rates = [
        p for p in perf_top3
        if p.pic_heure in ("12h", "18h")
        and isinstance(p.pic_valeur, (int, float)) and p.pic_valeur > 0
        and isinstance(p.fav_cloture, (int, float)) and p.fav_cloture < p.pic_valeur
    ]
    for p in rates:
        # Brief B — inclure le POURQUOI causal du repli quand il est TRACÉ (news
        # high après le pic), sinon le dire honnêtement (cause non identifiée).
        if p.cause_repli:
            pourquoi = f" Repli après {p.pic_heure} car : {p.cause_repli}"
        else:
            pourquoi = (
                f" Repli après {p.pic_heure}, cause non identifiée "
                f"(pas de catalyseur tracé)"
            )
        lignes.append(
            f"- Sortie tardive sur **{p.actif}** : pic à {p.pic_heure}, clôture en "
            f"repli.{pourquoi}. Verrouiller au pic aurait mieux payé."
        )
    # Sélection trop prudente : gros move bonne direction, pas joué.
    prudents = [g for g in gros_moves if g.direction_juste is True]
    for g in prudents:
        # Brief B — POURQUOI le move (cause tracée uniquement).
        pourquoi = f", porté par : {g.cause_move}" if g.cause_move else " (cause non tracée)"
        lignes.append(
            f"- Sélection trop prudente sur **{g.actif}** : "
            f"{_fmt_pct(g.mouvement_pct)} dans le bon sens{pourquoi}, "
            f"écarté ({g.raison_non_select})."
        )
    # Mauvaise direction sur un gros move (le call était à côté).
    rates_dir = [g for g in gros_moves if g.direction_juste is False]
    for g in rates_dir:
        pourquoi = f", porté par : {g.cause_move}" if g.cause_move else " (cause non tracée)"
        lignes.append(
            f"- Mauvaise direction sur **{g.actif}** : "
            f"{_fmt_pct(g.mouvement_pct)} à contre-sens du call{pourquoi}, driver à revoir."
        )
    # Trous de données intraday (honnêteté : zéro invention).
    trous = [p for p in perf_top3 if p.points_manquants]
    if trous:
        noms = ", ".join(f"{p.actif} ({'/'.join(p.points_manquants)})" for p in trous)
        lignes.append(
            f"- Données intraday incomplètes : {noms}. Le pic est calculé sur les "
            f"seuls points relevés (à compléter par les suivis 12h/18h)."
        )
    if not lignes:
        lignes.append("- Rien de notable : la Sélection a suivi sa thèse, pas de gros move raté.")
    return lignes


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
    # WR significatif du jour = VRAI dont |mouvement| >= 0,5 % (gain exploitable),
    # même dénominateur que le win rate conclusif (≤ celui-ci). Un call juste mais
    # quasi-plat ne compte pas comme une vraie réussite tradable.
    n_vrai_signif: int = 0
    win_rate_signif_jour: Optional[float] = None
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
    # Refonte bilan soir S9 — 3 blocs « suivi 24h » (demande fondateur).
    perf_top3: List[PerfTop3Ligne] = field(default_factory=list)        # Bloc 1
    gros_moves_autres: List[GrosMoveAutre] = field(default_factory=list)  # Bloc 2
    apprentissage: List[str] = field(default_factory=list)             # Bloc 3
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
            if isinstance(m.delta_pct, (int, float)) and abs(m.delta_pct) >= J.SEUIL_MVT_SIGNIFICATIF:
                bilan.n_vrai_signif += 1
        elif m.outcome == J.OUTCOME_FAUSSE:
            bilan.n_fausse += 1
        elif m.outcome == J.OUTCOME_NC:
            bilan.n_nc += 1
    denom = bilan.n_vrai + bilan.n_fausse
    if denom > 0:
        bilan.win_rate_jour = round(bilan.n_vrai / denom * 100.0, 1)
        bilan.win_rate_signif_jour = round(bilan.n_vrai_signif / denom * 100.0, 1)
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

    # Refonte bilan soir S9 — 3 blocs « suivi 24h » (demande fondateur).
    # Relevés intraday persistés par run_suivi (call + fav% + heure à 12h/18h).
    try:
        from run_suivi import load_suivi_tracking  # noqa: PLC0415
        tracking = load_suivi_tracking(date_j)
    except Exception as e:  # noqa: BLE001 — relevés indispo → trous explicites
        logger.warning("bilan soir : load_suivi_tracking KO (%s) — trous", e)
        tracking = {}
    # Reco réelle du suivi 18h (compute_vendre sur fav 12h→18h, source unique).
    vendre_map = _vendre_reco_18h(tracking)
    conv_records = load_conviction_records(date_j, decision_log_dir)
    score_fort_seuil = _load_score_fort_seuil()

    bilan.perf_top3 = compute_perf_top3(
        measures_24h, selection_map, tracking, vendre_map, date_j=date_j
    )
    bilan.gros_moves_autres = compute_gros_moves_autres(
        measures_24h, selection_map, conv_records, score_fort_seuil, date_j=date_j,
    )
    bilan.apprentissage = compute_apprentissage_jour(bilan.perf_top3, bilan.gros_moves_autres)

    bilan.close_approx_tickers = approx_tickers
    bilan.markdown = _render_markdown(bilan, fiches)
    return bilan


def _vendre_reco_18h(tracking: Dict[str, Dict[str, dict]]) -> Dict[str, str]:
    """Reco réelle « Vendre à 18h ? » par actif, recalculée depuis les relevés.

    Réutilise `run_suivi.compute_vendre` (source de vérité unique, Vague A) sur le
    couple (fav 18h, fav 12h) persisté. Le compute_vendre raisonne en delta signé
    (et non en favorable) → on remonte le delta = fav / sens(call). band=0 ici (le
    suivi a déjà filtré la bande neutre ; on ne ré-applique pas un seuil arbitraire,
    on reproduit juste la décision verrou/coupe). {} si pas de relevé 18h.
    """
    try:
        from run_suivi import compute_vendre, call_sign  # noqa: PLC0415
    except ImportError:  # pragma: no cover
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run_suivi import compute_vendre, call_sign  # noqa: PLC0415

    out: Dict[str, str] = {}
    bloc_18h = tracking.get("18h") or {}
    bloc_12h = tracking.get("12h") or {}
    for actif, rec18 in bloc_18h.items():
        if not isinstance(rec18, dict):
            continue
        call = str(rec18.get("call", ""))
        sign = call_sign(call)
        fav18 = rec18.get("fav_pct")
        if sign is None or not isinstance(fav18, (int, float)):
            continue
        delta18 = fav18 / sign
        rec12 = bloc_12h.get(actif)
        delta12 = None
        if isinstance(rec12, dict) and isinstance(rec12.get("fav_pct"), (int, float)):
            s12 = call_sign(str(rec12.get("call", "")))
            if s12 is not None:
                delta12 = rec12["fav_pct"] / s12
        out[actif] = compute_vendre(delta18, delta12, call, 0.0)
    return out


def _fmt_fav_cell(v: Optional[float]) -> str:
    """% favorable signé en cellule de tableau (« — » placeholder vide si absent)."""
    return f"{v:+.2f}%" if isinstance(v, (int, float)) else "—"


def _render_bloc1_perf_top3(bilan: "BilanJour") -> List[str]:
    """Bloc 1 — Performance 24h du TOP 3 (la Sélection du jour).

    Tableau favorable 12h/18h/clôture + pic horodaté, puis verdict de sortie par
    actif (relié aux heures) confronté à la reco réelle du suivi 18h.
    """
    L: List[str] = []
    L.append("### 1. Performance 24h du Top 3 (la Sélection du jour)")
    L.append("")
    if not bilan.perf_top3:
        L.append("Pas de sélection conclusive aujourd'hui (aucun top 3 à noter).")
        L.append("")
        return L
    # Concept du 24h (fondateur) : une position du jour est un pari d'UNE journée.
    # À 22h, toute position encore active est clôturée (fin du 24h) au cours de
    # clôture. La colonne « % clôture » ci-dessous est ce résultat 24h final.
    L.append(
        "_Concept 24h : toute position encore ouverte à 22h est clôturée (fin du "
        "24h) au cours de clôture. La colonne « % clôture » est ce résultat final._"
    )
    L.append("")
    # En-têtes % à double libellé (desktop complet / mobile court) pour garder la
    # colonne Pic lisible sur petit écran (CSS .c-full / .c-short, comme le suivi).
    L.append(
        "| Actif "
        "| <span class=\"c-full\">Call 7h</span><span class=\"c-short\">Call</span> "
        "| <span class=\"c-full\">% fav. 12h</span><span class=\"c-short\">12h</span> "
        "| <span class=\"c-full\">% fav. 18h</span><span class=\"c-short\">18h</span> "
        "| <span class=\"c-full\">% fav. clôture</span><span class=\"c-short\">Clôt.</span> "
        "| Pic |"
    )
    L.append("|---|---|---|---|---|---|")
    for p in bilan.perf_top3:
        pic = (
            f"**{_fmt_pct(p.pic_valeur)} à {p.pic_heure}**"
            if p.pic_valeur is not None and p.pic_heure else "—"
        )
        L.append(
            f"| {p.actif} | {p.call} | {_fmt_fav_cell(p.fav_12h)} | "
            f"{_fmt_fav_cell(p.fav_18h)} | {_fmt_fav_cell(p.fav_cloture)} | {pic} |"
        )
    L.append("")
    L.append(
        "_% favorable signé : `+` = le marché va dans le sens du call (gagne), "
        "`-` = contre nous. Pic = meilleur % favorable atteint parmi 12h / 18h / "
        "clôture. « — » = point non relevé (zéro invention)._"
    )
    L.append("")
    # Verdict de sortie optimale par actif, confronté à la reco réelle du suivi.
    L.append("**Sortie optimale vs reco du suivi :**")
    for p in bilan.perf_top3:
        if p.vendre_reco == "Vendre":
            capte = (
                "capté" if (p.pic_heure in ("12h", "18h")) else "sorti trop tôt ?"
            )
            reco_txt = f" Le suivi 18h recommandait « Vendre » ({capte})."
        elif p.vendre_reco == "Pas vendre":
            rate = (
                " (le pic était avant la clôture : on a raté la sortie)"
                if p.pic_heure in ("12h", "18h")
                and isinstance(p.pic_valeur, (int, float)) and p.pic_valeur > 0
                and isinstance(p.fav_cloture, (int, float)) and p.fav_cloture < p.pic_valeur
                else ""
            )
            reco_txt = f" Le suivi 18h recommandait « Pas vendre »{rate}."
        else:
            reco_txt = " (pas de reco de suivi 18h relevée.)"
        # Brief B — POURQUOI le repli (cause tracée uniquement) : si le pic a reflué
        # avant la clôture, on cite la news high tracée sur l'actif après le pic, ou
        # on déclare honnêtement la cause non identifiée (jamais d'invention).
        cause_txt = ""
        a_reflue = (
            p.pic_heure in ("12h", "18h")
            and isinstance(p.pic_valeur, (int, float)) and p.pic_valeur > 0
            and isinstance(p.fav_cloture, (int, float)) and p.fav_cloture < p.pic_valeur
        )
        if a_reflue:
            if p.cause_repli:
                cause_txt = (
                    f" Le repli après {p.pic_heure} coïncide avec : {p.cause_repli}."
                )
            else:
                cause_txt = (
                    f" Cause du repli après {p.pic_heure} non identifiée "
                    f"(pas de catalyseur tracé)."
                )
        L.append(f"- **{p.actif}** ({p.call}) : {p.verdict}{reco_txt}{cause_txt}")
    L.append("")
    return L


def _render_bloc2_gros_moves(bilan: "BilanJour") -> List[str]:
    """Bloc 2 — Gros mouvements sur les AUTRES assets (hors top 3) + pourquoi pas joués."""
    L: List[str] = []
    L.append("### 2. Gros mouvements ailleurs (hors Top 3)")
    L.append("")
    if not bilan.gros_moves_autres:
        L.append(
            "Aucun gros mouvement hors Top 3 aujourd'hui (rien d'évident qu'on aurait dû jouer)."
        )
        L.append("")
        return L
    L.append(
        "_Du plus gros au plus petit (le plus gros = le plus intéressant à jouer)._"
    )
    L.append("")
    for g in bilan.gros_moves_autres:
        if g.direction_juste is True:
            dir_txt = "vu, **bonne direction** mais pas joué"
        elif g.direction_juste is False:
            dir_txt = "**raté** : mauvaise direction du call"
        else:
            dir_txt = "direction indéterminée (donnée manquante)"
        L.append(
            f"- **{g.actif}** ({g.call}) : {_fmt_pct(g.mouvement_pct)} vs ouverture "
            f"→ {dir_txt}. Pourquoi pas sélectionné : {g.raison_non_select}."
        )
        # Brief B — POURQUOI le mouvement (cause tracée uniquement, sinon honnête).
        if g.cause_move:
            L.append(f"  - _Pourquoi ce move : {g.cause_move}._")
        else:
            L.append("  - _Pourquoi ce move : cause non tracée (pas de news high sur l'actif ce jour)._")
        L.append(f"  - _Apprentissage : {g.apprentissage}_")
    L.append("")
    return L


def _render_bloc3_apprentissage(bilan: "BilanJour") -> List[str]:
    """Bloc 3 — Apprentissage du jour (synthèse courte, actionnable, déterministe)."""
    L: List[str] = []
    L.append("### 3. Apprentissage du jour")
    L.append("")
    L.extend(bilan.apprentissage or ["- Rien de notable aujourd'hui."])
    L.append("")
    return L


def _render_markdown(bilan: BilanJour, fiches: Dict[str, dict]) -> str:
    """Markdown R4 (spec §3.4). WIN RATE ONLY — aucun montant."""
    from journaliste import (  # noqa: PLC0415
        OUTCOME_VRAI, OUTCOME_FAUSSE, OUTCOME_NC,
    )

    L: List[str] = []
    # [I-7 audit visuel 12/06] : tous les rapports commencent par un H1 (le
    # Briefing est en H1, le suivi et le bilan étaient en H2 — incohérent).
    L.append(f"# Bilan du jour · {bilan.date_j.isoformat()}")
    L.append("")
    L.append(f"_Généré : {horodatage_fr(bilan.now)} (Europe/Paris)._")
    L.append("")
    # [H-BD1 audit visuel 12/06] : ligne résumé du score EN TÊTE, avant le
    # tableau détaillé — Thomas voit « j'ai eu raison combien de fois » d'un coup.
    wr_txt = (
        f" · Win rate : {bilan.win_rate_jour:.0f}%"
        if bilan.win_rate_jour is not None else ""
    )
    L.append(
        f"**Résultat du {bilan.date_j.strftime('%d/%m')} : "
        f"{bilan.n_vrai} ✅ / {bilan.n_fausse} ❌ / {bilan.n_nc} ⚪{wr_txt}**"
    )
    L.append("")

    # Refonte bilan soir S9 (Thomas) — 3 blocs « suivi 24h » EN TÊTE, avant la
    # mesure détaillée. WIN RATE ONLY (le % d'ampleur est OK). Zéro invention.
    L.extend(_render_bloc1_perf_top3(bilan))
    L.extend(_render_bloc2_gros_moves(bilan))
    L.extend(_render_bloc3_apprentissage(bilan))

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

    # Win rate du jour — [H-BD2 audit visuel 12/06] : 2 niveaux. Le chiffre
    # PRIMAIRE (le WR du jour) en gras, seul, en premier. Le détail (WR tradable,
    # conviction forte/faible, sélection) descend en bloc « Détail » secondaire.
    L.append("### Win rate du jour")
    denom = bilan.n_vrai + bilan.n_fausse
    if bilan.win_rate_jour is not None:
        L.append(
            f"**{bilan.win_rate_jour:.0f}% ({bilan.n_vrai}/{denom})** "
            f"— {denom} paris conclusifs, {bilan.n_nc} non-conclusifs sous seuil."
        )
    else:
        L.append("**— (aucun call conclusif aujourd'hui)**")
    L.append("")
    L.append("_Détail :_")
    # WR significatif : ne compte que les calls justes ayant bougé >= 0,5 % en
    # notre faveur (gain exploitable ; quasi-plats écartés). Même dénominateur.
    if bilan.win_rate_signif_jour is not None:
        L.append(
            f"- WR ≥ 0,5 % du jour : {bilan.n_vrai_signif}/{denom} = "
            f"{bilan.win_rate_signif_jour:.0f}% (calls justes ayant bougé d'au moins 0,5 %)"
        )
    # WR tradable (secondaire) : inclut les non-conclusifs au dénominateur.
    denom_trad = bilan.n_vrai + bilan.n_fausse + bilan.n_nc
    if bilan.wr_tradable_jour is not None:
        L.append(
            f"- WR tradable du jour : {bilan.n_vrai}/{denom_trad} = "
            f"{bilan.wr_tradable_jour:.0f}% (VRAI / VRAI+FAUSSE+non-conclusif)"
        )
    else:
        L.append("- WR tradable du jour : — (aucun pari tradable aujourd'hui)")
    # WR Sélection du jour (Étage 1c) : les paris de l'encart « Sélection (max 3) »
    # en tête de « 🎯 Décision du jour » (refonte S9 vague 3), mesurés comme objet
    # dédié (VRAI/FAUX, NC exclus comme le WR global). « — » si aucune cellule
    # sélectionnée n'est conclusive aujourd'hui.
    s = bilan.selection
    if s.taux is not None:
        L.append(
            f"- WR Sélection du jour : {s.n_vrai_select}/{s.n_select} = "
            f"{s.taux:.0f}% (encart « 🎯 Sélection (max 3) » de Décision du jour)"
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
    # [P-BD1 audit visuel 12/06] : explication réduite à 1 ligne (le détail
    # complet était du bruit après la première lecture).
    L.append("_Métrique shadow momentum (ne change pas le win rate) :_")
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
                f"dans le sens opposé."
            )
        # [C-BD1 audit visuel 12/06] : renvoi au bilan semaine UNE seule fois,
        # en bas de liste (au lieu de répété sur chaque erreur).
        L.append("")
        L.append("_Ces erreurs seront analysées dans le bilan de semaine._")
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
            f"({type_label}) · actifs : {actifs}"
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
    "load_conviction_records",
    "win_rate_par_conviction",
    "build_bilan_jour",
    "write_bilan_jour",
    "GROS_MOVE_FACTOR",
    "CLOSE_APPROX_MARKER",
    # Refonte bilan soir S9 — 3 blocs « suivi 24h ».
    "PerfTop3Ligne",
    "GrosMoveAutre",
    "compute_perf_top3",
    "compute_gros_moves_autres",
    "compute_apprentissage_jour",
    "reason_non_selection",
]
