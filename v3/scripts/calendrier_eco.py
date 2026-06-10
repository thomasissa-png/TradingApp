"""TradingApp v3 — Calendrier économique statique (catalyseurs récurrents).

Source de vérité : `v3/config/calendrier-eco.yml` — événements PUBLICS et DATÉS
À L'AVANCE (Fed/BLS/BCE/USDA/EIA/CFTC). ZÉRO API, ZÉRO scraping, ZÉRO invention.

Expose :
- `evenements_a_venir(now, horizon_jours=3)` → liste triée des catalyseurs dans
  la fenêtre [now ; now+horizon], résolvant les règles de récurrence calculables
  (1er vendredi du mois, mercredis hebdo, n-ième jour ouvré…) en Europe/Paris.
- `evenement_majeur_imminent(now, types=...)` → bool DÉTERMINISTE (FOMC J-1/J0 par
  défaut) utilisable comme source d'un gate « événement de marché majeur imminent »
  (flag hors score). N'est PAS branché dans le scoring par ce module.

Garde-fous :
- WIN RATE ONLY — aucune valeur monétaire. Purement informatif (affichage).
- Zéro invention : une entrée `precision: date` DOIT porter une date ISO valide ;
  sinon l'entrée est ignorée (jamais de date fabriquée). Les règles produisent des
  dates CALCULÉES (récurrence officielle), affichées préfixées « ~ ».
- DST : toutes les dates calculées en Europe/Paris via ZoneInfo, jamais d'offset
  codé en dur. Jours fériés ignorés best-effort en stdlib (pas de lib `holidays`).
- YAML absent/illisible → liste vide (fallback propre), jamais d'exception.
"""

from __future__ import annotations

import calendar
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger("calendrier_eco")

ROOT = Path(__file__).resolve().parents[1]
CALENDRIER_FILE = ROOT / "config" / "calendrier-eco.yml"

PARIS_TZ = ZoneInfo("Europe/Paris")

# Types considérés « majeurs » pour le gate déterministe (flag hors score).
TYPES_MAJEURS = ("FOMC",)
# Fenêtre par défaut du gate : l'événement est imminent à J-1 et J0.
GATE_HORIZON_JOURS = 1


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------

def charger_evenements(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Charge les entrées du YAML. Fallback propre (liste vide) si absent/illisible.

    `path=None` résout dynamiquement vers `CALENDRIER_FILE` (permet le monkeypatch
    du module dans les tests — un défaut figé serait lié à l'import).
    """
    path = path or CALENDRIER_FILE
    if not path.exists():
        logger.info("calendrier-eco.yml absent (%s) — catalyseurs indisponibles", path)
        return []
    try:
        import yaml  # noqa: PLC0415
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as e:  # noqa: BLE001
        logger.warning("calendrier-eco.yml illisible : %s — fallback vide", e)
        return []
    evts = data.get("evenements")
    if not isinstance(evts, list):
        return []
    return [e for e in evts if isinstance(e, dict)]


# ---------------------------------------------------------------------------
# Résolution des règles de récurrence (toutes en dates Europe/Paris)
# ---------------------------------------------------------------------------

def _premier_jour_semaine_mois(annee: int, mois: int, weekday: int) -> date:
    """Premier `weekday` (0=lundi…6=dimanche) du mois donné. Ex. NFP = 1er vendredi."""
    d = date(annee, mois, 1)
    decalage = (weekday - d.weekday()) % 7
    return d + timedelta(days=decalage)


def _nieme_jour_ouvre_mois(annee: int, mois: int, occurrence: int) -> date:
    """n-ième jour ouvré (lun-ven) du mois. Best-effort : ignore les fériés
    (stdlib only — pas de lib holidays). Approximation honnête, marquée `regle`."""
    occurrence = max(1, int(occurrence))
    d = date(annee, mois, 1)
    nb_jours = calendar.monthrange(annee, mois)[1]
    compte = 0
    while d.day <= nb_jours and d.month == mois:
        if d.weekday() < 5:  # lun-ven
            compte += 1
            if compte >= occurrence:
                return d
        d += timedelta(days=1)
    # Mois trop court pour l'occurrence demandée → dernier jour ouvré rencontré.
    dernier = date(annee, mois, nb_jours)
    while dernier.weekday() >= 5:
        dernier -= timedelta(days=1)
    return dernier


def _jour_du_mois(annee: int, mois: int, day: int) -> date:
    """Jour fixe du mois (borné au dernier jour). Si week-end → recale au lundi
    suivant (best-effort, beaucoup de publications glissent au jour ouvré)."""
    nb_jours = calendar.monthrange(annee, mois)[1]
    jour = min(max(1, int(day)), nb_jours)
    d = date(annee, mois, jour)
    while d.weekday() >= 5:  # samedi/dimanche → lundi suivant
        d += timedelta(days=1)
    return d


def _occurrences_hebdo(weekday: int, debut: date, fin: date) -> List[date]:
    """Toutes les dates `weekday` (0=lundi…) dans [debut ; fin] inclus."""
    if fin < debut:
        return []
    decalage = (weekday - debut.weekday()) % 7
    d = debut + timedelta(days=decalage)
    out: List[date] = []
    while d <= fin:
        out.append(d)
        d += timedelta(days=7)
    return out


def _dates_pour_regle(ev: Dict[str, Any], debut: date, fin: date) -> List[date]:
    """Calcule les dates d'une entrée `precision: regle` tombant dans [debut;fin].

    Couvre le mois courant ET le suivant pour les règles mensuelles (la fenêtre
    peut chevaucher deux mois). Hebdo : énumération directe sur la fenêtre.
    """
    regle = ev.get("regle")
    params = ev.get("regle_params") or {}
    out: List[date] = []

    if regle == "jour_semaine_hebdo":
        wd = int(params.get("weekday", 2))
        out = _occurrences_hebdo(wd, debut, fin)

    elif regle in ("premier_jour_semaine_mois", "nieme_jour_ouvre_mois", "jour_du_mois"):
        # Génère pour chaque (annee, mois) couvert par la fenêtre.
        for annee, mois in _mois_couverts(debut, fin):
            if regle == "premier_jour_semaine_mois":
                cand = _premier_jour_semaine_mois(annee, mois, int(params.get("weekday", 4)))
            elif regle == "nieme_jour_ouvre_mois":
                cand = _nieme_jour_ouvre_mois(annee, mois, int(params.get("occurrence", 1)))
            else:
                cand = _jour_du_mois(annee, mois, int(params.get("day", 1)))
            if debut <= cand <= fin:
                out.append(cand)
    else:
        logger.warning("Règle inconnue '%s' (event '%s') — ignorée", regle, ev.get("nom"))

    return out


def _mois_couverts(debut: date, fin: date) -> List[tuple]:
    """Liste des (annee, mois) traversés par [debut ; fin]."""
    out: List[tuple] = []
    a, m = debut.year, debut.month
    while (a, m) <= (fin.year, fin.month):
        out.append((a, m))
        m += 1
        if m > 12:
            m = 1
            a += 1
    return out


def _dates_pour_event(ev: Dict[str, Any], debut: date, fin: date) -> List[date]:
    """Dates d'un event dans la fenêtre. `precision: date` → dates ISO listées
    (jamais inventées : une date invalide est ignorée). `precision: regle` →
    dates calculées par récurrence."""
    precision = (ev.get("precision") or "").strip().lower()
    if precision == "date":
        out: List[date] = []
        for s in ev.get("dates") or []:
            try:
                d = date.fromisoformat(str(s))
            except (ValueError, TypeError):
                logger.warning("Date invalide '%s' (event '%s') — ignorée", s, ev.get("nom"))
                continue
            if debut <= d <= fin:
                out.append(d)
        return out
    if precision == "regle":
        return _dates_pour_regle(ev, debut, fin)
    logger.warning("precision inconnue '%s' (event '%s') — ignorée", precision, ev.get("nom"))
    return []


# ---------------------------------------------------------------------------
# API publique
# ---------------------------------------------------------------------------

def evenements_a_venir(
    now: Optional[datetime] = None,
    horizon_jours: int = 3,
    path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Catalyseurs dans la fenêtre ]aujourd'hui ; aujourd'hui+horizon] (Europe/Paris).

    Retourne une liste TRIÉE (date, puis impact high avant medium, puis nom) de :
        {date: 'AAAA-MM-JJ', nom, type, actifs, impact, precision}

    La fenêtre démarre à J+1 (demain) : on annonce ce qui ARRIVE, pas le jour même.
    `precision: regle` est conservé tel quel → l'appelant préfixe « ~ » à l'affichage.
    """
    now = now or datetime.now(PARIS_TZ)
    if now.tzinfo is None:
        now = now.replace(tzinfo=PARIS_TZ)
    aujourd_hui = now.astimezone(PARIS_TZ).date()
    debut = aujourd_hui + timedelta(days=1)
    fin = aujourd_hui + timedelta(days=max(1, int(horizon_jours)))

    sortie: List[Dict[str, Any]] = []
    for ev in charger_evenements(path):
        precision = (ev.get("precision") or "").strip().lower()
        for d in _dates_pour_event(ev, debut, fin):
            sortie.append({
                "date": d.isoformat(),
                "nom": str(ev.get("nom") or ev.get("type") or "Événement"),
                "type": str(ev.get("type") or ""),
                "actifs": list(ev.get("actifs") or []),
                "impact": str(ev.get("impact") or "medium"),
                "precision": precision,
            })

    _impact_rang = {"high": 0, "medium": 1}
    sortie.sort(key=lambda e: (e["date"], _impact_rang.get(e["impact"], 2), e["nom"]))
    return sortie


def evenement_majeur_imminent(
    now: Optional[datetime] = None,
    types: tuple = TYPES_MAJEURS,
    horizon_jours: int = GATE_HORIZON_JOURS,
    path: Optional[Path] = None,
) -> bool:
    """True si un événement majeur DÉTERMINISTE (FOMC par défaut) tombe à J0 ou
    dans `horizon_jours` (défaut 1 → J-1/J0).

    Source déterministe utilisable par un gate « événement de marché majeur
    imminent » EN PLUS du best-effort news. Ce module ne branche RIEN dans le
    scoring lui-même (flag hors score) — c'est à l'appelant de l'adopter.

    Inclut le jour même (J0), contrairement à `evenements_a_venir` (J+1+).
    """
    now = now or datetime.now(PARIS_TZ)
    if now.tzinfo is None:
        now = now.replace(tzinfo=PARIS_TZ)
    aujourd_hui = now.astimezone(PARIS_TZ).date()
    debut = aujourd_hui  # J0 inclus
    fin = aujourd_hui + timedelta(days=max(0, int(horizon_jours)))
    cibles = {t.upper() for t in types}

    for ev in charger_evenements(path):
        if str(ev.get("type") or "").upper() not in cibles:
            continue
        if _dates_pour_event(ev, debut, fin):
            return True
    return False
