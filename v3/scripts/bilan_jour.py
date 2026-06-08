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
from datetime import date, datetime
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
    conviction: WinRateConviction = field(default_factory=WinRateConviction)
    markdown: str = ""


def _fmt_pct(v: Optional[float]) -> str:
    return f"{v:+.2f}%" if isinstance(v, (int, float)) else "—"


def _fmt_price(v: Optional[float]) -> str:
    return f"{v:.4g}" if isinstance(v, (int, float)) else "—"


def build_bilan_jour(
    now: Optional[datetime] = None,
    date_j: Optional[date] = None,
    bulletins_dir: Path = BULLETINS_DIR,
    decision_log_dir: Path = DECISION_LOG_DIR,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
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
        fetch_price=fetch_price,
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

    # Win rate par conviction (CA-W6).
    conv_map = load_conviction_map(date_j, decision_log_dir)
    bilan.conviction = win_rate_par_conviction(measures_24h, conv_map)

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
        L.append(
            f"| {m.cell.actif_name} | {m.cell.conclusion} | "
            f"{_fmt_price(m.prix_emission)} | {_fmt_price(m.prix_courant)} | "
            f"{_fmt_pct(delta)} | {res_label.get(m.outcome, m.outcome)} | {flag} |"
        )
    if not bilan.measures_24h:
        L.append("| _aucune cellule 24h mesurable du Briefing 7h_ | | | | | | |")
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
    # Win rate par conviction (CA-W6)
    c = bilan.conviction
    tf = f"{c.taux_forte:.0f}%" if c.taux_forte is not None else "— (N insuffisant)"
    tw = f"{c.taux_faible:.0f}%" if c.taux_faible is not None else "— (N insuffisant)"
    L.append(f"- Win rate conviction forte (jour) : {tf} (N={c.n_forte})")
    L.append(f"- Win rate conviction faible (jour) : {tw} (N={c.n_faible})")
    L.append("- Win rate cumulé : voir performance.md")
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

    # Catalyseurs J+1 (best-effort).
    L.append("### Catalyseurs J+1")
    L.append(
        "Catalyseurs J+1 non disponibles — agenda éco non ingéré ce jour "
        "(best-effort, zéro invention)."
    )
    L.append("")
    return "\n".join(L)


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
]
