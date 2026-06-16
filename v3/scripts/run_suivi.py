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
EVENTS_LOG_DIR = ROOT / "data" / "events-log"

PARIS_TZ = ZoneInfo("Europe/Paris")

# Report types reconnus (heure Paris du créneau).
REPORT_12H = "12h"
REPORT_18H = "18h"
VALID_REPORTS = (REPORT_12H, REPORT_18H)

# Longueur max du rapport (CA-S5 : un suivi reste court, pas un bulletin).
MAX_MARKDOWN_LINES = 50

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
    statut: str                    # "✅ gagne" / "⚠️ perd" / "— neutre" / "🕐 pas encore ouvert"
    tendance: str                  # "—" / "↑ s'accélère" / "↓ s'essouffle" / "⇄ se retourne" / "↗ confirmé US" / "↘ infirmé US"
    delta_vs_prec: Optional[float] # points de % vs le suivi précédent (18h), None au 12h
    suggestion: str                # "Hold" / "Surveiller" / "Sortie à envisager" / "—"
    seuil_pct: Optional[float]
    us_pas_ouvert: bool = False


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


def _dominant_news_critere(criteres: List[dict]) -> Optional[tuple]:
    """Critère news à plus forte |contribution| dans une cellule. (nom, sens) ou None.

    On considère « news » un critère de type triplet ou dont la source vient des
    events-log. Zéro invention : si rien ne matche → None.
    """
    best = None
    best_abs = 0.0
    for c in criteres:
        type_norm = (c.get("type_norm") or "").lower()
        source = (c.get("source_track") or c.get("cle") or "").lower()
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
            best = (nom, sens)
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

    if prix_ouverture_dir is None:
        prix_ouverture_dir = MO.PRIX_OUVERTURE_DIR
    band = MO.neutral_band_pct(config)
    ouvertures = MO.load_prix_ouverture(date_j, prix_ouverture_dir)
    cells = load_briefing_cells(date_j, bulletins_dir)

    # Snapshot du suivi précédent (12h) pour la dynamique au 18h.
    prev = load_delta_snapshot(date_j, REPORT_12H, suivi_dir) if report_type == REPORT_18H else {}

    rapport = SuiviRapport(date_j=date_j, now=now, report_type=report_type)
    deltas_now: Dict[str, Optional[float]] = {}

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
        us_pas_ouvert = (
            group == "us" and not MO.is_open_for_stamp("us", now, config)
        )
        if us_pas_ouvert:
            rapport.lignes.append(SuiviLigne(
                actif=actif, call=call, ouverture=None, prix_courant=None,
                delta_pct=None, statut="🕐 pas encore ouvert", tendance="—",
                delta_vs_prec=None, suggestion="—", seuil_pct=seuil,
                us_pas_ouvert=True,
            ))
            continue

        ouverture = ouvertures.get(ticker)
        prix_courant = None
        if ticker:
            try:
                prix_courant = fetch_price(ticker)
            except Exception as e:  # noqa: BLE001
                logger.warning("suivi %s : fetch prix KO : %s", ticker, e)
                prix_courant = None
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

        rapport.lignes.append(SuiviLigne(
            actif=actif, call=call, ouverture=ouverture, prix_courant=prix_courant,
            delta_pct=delta, statut=statut, tendance=tendance,
            delta_vs_prec=(round(delta - delta_prec, 2)
                           if (delta is not None and isinstance(delta_prec, (int, float)))
                           else None),
            suggestion=suggestion, seuil_pct=seuil, us_pas_ouvert=False,
        ))

    rapport.news = news_a_impact(
        date_j, [li.actif for li in rapport.lignes], decision_log_dir
    )

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

    rapport.markdown = _render_markdown(rapport)

    # Persiste les deltas du 12h pour le suivi 18h (cache de présentation only).
    if report_type == REPORT_12H:
        save_delta_snapshot(date_j, REPORT_12H, deltas_now, suivi_dir)
        # Persiste aussi les titres frais affichés au 12h → dédup au 18h.
        save_titres_frais_snapshot(date_j, REPORT_12H, titres_frais, suivi_dir)
    return rapport


def _render_markdown(r: SuiviRapport) -> str:
    """Markdown court du suivi (CA-S1/S5). WIN RATE ONLY — pas de matrice LONG/SHORT."""
    heure = r.now.strftime("%Hh%M")
    h = r.report_type
    L: List[str] = []
    # [I-7 audit visuel 12/06] : H1 pour tous les rapports (cohérence avec le
    # Briefing — le suivi était en H2).
    L.append(f"# Suivi {h} — {r.date_j.isoformat()} {heure}")
    L.append("")

    # PARTIE B — 1 ligne de contexte réactualisée (factuelle, décor), en tête.
    if r.contexte_frais:
        L.append(f"_{r.contexte_frais}_")
        L.append("")

    if h == REPORT_12H:
        L.append("### Note sur les marchés US")
        L.append(
            "⚠️ Marchés US (S&P 500, Nasdaq, VIX) pas encore ouverts "
            "(ouverture 15h30 Paris). Ce suivi couvre EU + continus uniquement. "
            "Premier statut US au suivi 18h."
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
    if h == REPORT_12H:
        L.append(
            f"| Actif | Call 7h | Ouverture | Prix {h} | Delta% | Statut | Suggestion |"
        )
        L.append("|---|---|---|---|---|---|---|")
        if not r.lignes:
            L.append("| _aucune position actionnable du Briefing 7h_ | | | | | | |")
        for li in r.lignes:
            L.append(
                f"| {li.actif} | {li.call} | {_fmt_price(li.ouverture)} | "
                f"{_fmt_price(li.prix_courant)} | {_fmt_pct(li.delta_pct)} | "
                f"{li.statut} | {li.suggestion} |"
            )
    else:
        L.append(
            f"| Actif | Call 7h | Ouverture | Prix {h} | Delta% | Δ précédent | "
            f"Tendance | Statut | Suggestion |"
        )
        L.append("|---|---|---|---|---|---|---|---|---|")
        if not r.lignes:
            L.append("| _aucune position actionnable du Briefing 7h_ | | | | | | | | |")
        for li in r.lignes:
            L.append(
                f"| {li.actif} | {li.call} | {_fmt_price(li.ouverture)} | "
                f"{_fmt_price(li.prix_courant)} | {_fmt_pct(li.delta_pct)} | "
                f"{_fmt_points(li.delta_vs_prec)} | {li.tendance} | {li.statut} | "
                f"{li.suggestion} |"
            )
    L.append("")

    # Contexte news du Briefing 7h (NON réactualisé — fix libellé 16/06, Thomas).
    # Le suivi NE ré-ingère PAS les news : ces lignes proviennent du decision-log
    # 7h du jour (cf. news_a_impact). L'ancien titre « News à impact depuis 7h/12h »
    # impliquait à tort une réactualisation continue → libellé honnête.
    L.append("### Contexte news (bulletin 7h, non réactualisé)")
    if r.news:
        L.extend(r.news[:MAX_NEWS])
        # [C-S1 audit visuel 12/06] : les news du suivi proviennent du même
        # decision-log 7h → au 18h, elles sont identiques à celles du matin. On
        # le signale pour éviter au lecteur de les relire comme du neuf.
        if h == REPORT_18H:
            L.append("")
            L.append("_(mêmes news que les suivis précédents — source : Briefing 7h.)_")
    else:
        L.append("Aucune news impactante dans le Briefing 7h.")
    L.append("")

    # PARTIE B — bloc « Actus du jour » : titres FRAIS récoltés depuis le créneau
    # précédent (RSS léger, zéro DeepSeek). CLAIREMENT distinct du Contexte 7h
    # ci-dessus (matin figé) — libellé honnête sur la fenêtre de fraîcheur.
    heure_prec = SEUIL_HEURE_PRECEDENTE.get(h, 7)
    L.append(f"### Actus du jour (depuis {heure_prec}h)")
    if r.news_fraiches_indispo:
        L.append("Actus du jour indisponibles (flux injoignable).")
    elif r.news_fraiches:
        L.extend(r.news_fraiches[:MAX_NEWS_FRAICHES])
    else:
        L.append(f"Pas de news fraîche notable depuis {heure_prec}h.")
    L.append("")

    # Suggestions de sortie (drapeaux — Thomas décide).
    L.append("### Suggestions de sortie")
    sorties = [li for li in r.lignes if li.suggestion == "Sortie à envisager"]
    if sorties:
        for li in sorties:
            L.append(
                f"- ⚠️ **{li.actif}** ({li.call}) : {_fmt_pct(li.delta_pct)} contre "
                f"le call (seuil {_fmt_pct(li.seuil_pct, signed=False)}). "
                f"Sortie à envisager — drapeau, Thomas décide."
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
    "us_trend_flag",
    "load_briefing_cells",
    "save_delta_snapshot",
    "load_delta_snapshot",
    "news_a_impact",
    "recolte_news_fraiches",
    "save_titres_frais_snapshot",
    "load_titres_frais_snapshot",
    "build_suivi",
    "write_suivi",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
